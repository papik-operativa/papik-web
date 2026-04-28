#!/usr/bin/env python3
"""
PAPIK Group · Performance Pass
==============================
Walks all HTML files under /public/ and applies these idempotent passes:

  1. defer/async on script tags
  2. lazy loading on images (with above-the-fold heuristic)
  3. preload hints (fonts, main CSS) in <head>
  4. dns-prefetch / preconnect for external domains
  5. report missing alt / width / height

Re-runnable safely: every mutation checks for the optimization first.

Skips:
  - public/dashboard-cliente.html and public/es/dashboard-cliente.html
  - public/_t.html
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
REPORT = ROOT / "seo-internal" / "performance-pass-report.md"

SKIP_REL = {
    "dashboard-cliente.html",
    "es/dashboard-cliente.html",
    "en/dashboard-cliente.html",
    "_t.html",
}

# Scripts that should be deferred (first-party, non-critical)
DEFER_SCRIPTS = {
    "cookie-banner.js",
    "forms.js",
    "splash.js",
    "supabase-auth.js",
    "dashboard-guard.js",
    "header.js",
    "motion.js",
    "cursor.js",
}

# Hosts that mark a script as third-party analytics → should be async
ASYNC_HOSTS = (
    "googletagmanager.com",
    "google-analytics.com",
    "googleadservices.com",
    "googlesyndication.com",
    "connect.facebook.net",
    "static.hotjar.com",
    "cdn.segment.com",
    "plausible.io",
    "umami",
    "stats.g.doubleclick.net",
)

# Recognized external domains for dns-prefetch
DNS_PREFETCH_HOSTS = (
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "www.googletagmanager.com",
    "www.google-analytics.com",
    "connect.facebook.net",
    "cdn.jsdelivr.net",
    "unpkg.com",
)

CSS_DIR = PUBLIC / "css"
FONTS_DIR = PUBLIC / "fonts"

# ---------------------------------------------------------------------------
# Counters
# ---------------------------------------------------------------------------

stats = Counter()
issues = {
    "missing_alt": [],          # list of (file, snippet)
    "missing_dims": 0,          # count
    "render_blocking": set(),   # set of script srcs
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCRIPT_RE = re.compile(r"<script\b([^>]*)>", re.IGNORECASE)
IMG_RE = re.compile(r"<img\b([^>]*)/?>", re.IGNORECASE)
SECTION_OPEN_RE = re.compile(r"<section\b", re.IGNORECASE)
HEAD_END_RE = re.compile(r"</head>", re.IGNORECASE)
SRC_RE = re.compile(r'\bsrc\s*=\s*"([^"]*)"', re.IGNORECASE)
ATTR_RE = re.compile(r'\b([\w-]+)(?:\s*=\s*"([^"]*)")?')


def has_attr(attrs: str, name: str) -> bool:
    return re.search(rf'\b{name}\b(?:\s*=|\s|/?>|$)', attrs, re.IGNORECASE) is not None


def get_attr(attrs: str, name: str) -> str | None:
    m = re.search(rf'\b{name}\s*=\s*"([^"]*)"', attrs, re.IGNORECASE)
    return m.group(1) if m else None


def add_attr(attrs: str, name: str, value: str | None = None) -> str:
    """Append an attribute to a tag attribute string. Idempotent."""
    if has_attr(attrs, name):
        return attrs
    new = f' {name}="{value}"' if value is not None else f" {name}"
    # Place it before the trailing slash if present
    attrs = attrs.rstrip()
    if attrs.endswith("/"):
        return attrs[:-1].rstrip() + new + " /"
    return attrs + new


# ---------------------------------------------------------------------------
# Pass 1 · scripts
# ---------------------------------------------------------------------------

def pass_scripts(html: str, file_rel: str) -> str:
    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        src = get_attr(attrs, "src")
        if not src:
            return m.group(0)  # inline script — leave alone

        is_module = (get_attr(attrs, "type") or "").lower() == "module"
        has_defer = has_attr(attrs, "defer")
        has_async = has_attr(attrs, "async")

        # Decide which optimization
        basename = src.rsplit("/", 1)[-1].lower()
        host = ""
        m_host = re.match(r"https?://([^/]+)", src)
        if m_host:
            host = m_host.group(1).lower()

        new_attrs = attrs
        if any(h in host for h in ASYNC_HOSTS):
            if not has_async and not is_module:
                new_attrs = add_attr(new_attrs, "async")
                stats["pass1_async"] += 1
        elif basename in DEFER_SCRIPTS:
            if not has_defer and not has_async and not is_module:
                new_attrs = add_attr(new_attrs, "defer")
                stats["pass1_defer"] += 1
        else:
            # Other first-party scripts (non-cdn, non-analytics) → defer if static js/
            if (
                not host
                and not has_defer
                and not has_async
                and not is_module
            ):
                if src.startswith(("js/", "/js/", "./js/")):
                    new_attrs = add_attr(new_attrs, "defer")
                    stats["pass1_defer"] += 1
                else:
                    issues["render_blocking"].add(src)
            elif host and not has_defer and not has_async and not is_module:
                # external non-analytics CDN script with no async/defer → render-blocking
                issues["render_blocking"].add(src)

        if new_attrs != attrs:
            return f"<script{new_attrs}>"
        return m.group(0)

    return SCRIPT_RE.sub(repl, html)


# ---------------------------------------------------------------------------
# Pass 2 · images
# ---------------------------------------------------------------------------

def find_body_offset(html: str) -> int:
    m = re.search(r"<body\b[^>]*>", html, re.IGNORECASE)
    return m.end() if m else 0


def find_above_fold_threshold(html: str) -> int:
    """
    Return the byte offset that separates 'above the fold' from below.
    Heuristic: end of the second <section> opening, or 800 chars * 4 bytes
    after <body>, whichever is larger.
    """
    body = find_body_offset(html)
    if body == 0:
        return 0

    sections = list(SECTION_OPEN_RE.finditer(html, body))
    fallback = body + 3200  # ~800px equivalent of HTML
    if len(sections) >= 2:
        # End of the second section opening tag-ish: take its position + a buffer
        return max(sections[1].start(), fallback)
    if len(sections) == 1:
        return max(sections[0].start() + 4000, fallback)
    return fallback


def pass_images(html: str, file_rel: str) -> str:
    threshold = find_above_fold_threshold(html)
    body_start = find_body_offset(html)
    out = []
    last = 0

    for m in IMG_RE.finditer(html):
        out.append(html[last:m.start()])
        attrs = m.group(1)
        original = m.group(0)
        pos = m.start()

        # Only consider <img> in <body>
        in_body = pos >= body_start

        # Above-the-fold detection
        above_fold = in_body and pos < threshold
        # Hero detection (parent section has class "hero")
        hero_lookback = html[max(0, pos - 800):pos].lower()
        is_hero = (
            "hero" in hero_lookback
            and hero_lookback.rfind("<section") > hero_lookback.rfind("</section>")
        )

        new_attrs = attrs

        # --- Audit (always, regardless of mutation state) ---
        alt = get_attr(new_attrs, "alt")
        if alt is None or alt.strip() == "":
            src = get_attr(new_attrs, "src") or "(no src)"
            issues["missing_alt"].append(f"{file_rel} :: {src}")

        if not has_attr(new_attrs, "width") or not has_attr(new_attrs, "height"):
            issues["missing_dims"] += 1

        # --- Mutations ---
        if not has_attr(new_attrs, "loading"):
            if above_fold or is_hero:
                new_attrs = add_attr(new_attrs, "loading", "eager")
            else:
                new_attrs = add_attr(new_attrs, "loading", "lazy")
            stats["pass2_loading"] += 1

        if not has_attr(new_attrs, "decoding"):
            new_attrs = add_attr(new_attrs, "decoding", "async")
            stats["pass2_decoding"] += 1

        if is_hero and not has_attr(new_attrs, "fetchpriority"):
            new_attrs = add_attr(new_attrs, "fetchpriority", "high")
            stats["pass2_fetchpriority"] += 1

        if new_attrs != attrs:
            out.append(f"<img{new_attrs}>")
        else:
            out.append(original)
        last = m.end()

    out.append(html[last:])
    return "".join(out)


# ---------------------------------------------------------------------------
# Pass 3 + 4 · head hints
# ---------------------------------------------------------------------------

PRELOAD_BLOCK_MARKER = "<!-- perf-pass:preload -->"
DNS_BLOCK_MARKER = "<!-- perf-pass:dns -->"


def pass_head_hints(html: str, file_rel: str) -> str:
    head_end = HEAD_END_RE.search(html)
    if not head_end:
        return html

    head_html = html[:head_end.start()]

    # Build preload block (Pass 3)
    preload_lines: list[str] = []

    # Detect the exact href used for the page's primary stylesheet (tokens.css)
    main_css = None
    css_match = re.search(
        r'rel="stylesheet"\s+href="([^"]*tokens\.css)"', head_html
    )
    if css_match:
        main_css = css_match.group(1)
    else:
        css_match = re.search(
            r'rel="stylesheet"\s+href="([^"]*base\.css)"', head_html
        )
        if css_match:
            main_css = css_match.group(1)

    if main_css and f'rel="preload" href="{main_css}"' not in head_html:
        preload_lines.append(
            f'  <link rel="preload" href="{main_css}" as="style">'
        )
        stats["pass3_css_preload"] += 1

    # Font preload (TT Firs Neue Regular)
    font_path = FONTS_DIR / "TT_Firs_Neue_Regular.woff2"
    if font_path.exists():
        # Determine relative path: pages in /public root → fonts/...
        # pages in /public/es/, /public/en/ etc. → ../fonts/...
        depth = file_rel.count("/")
        if depth == 0:
            font_url = "/fonts/TT_Firs_Neue_Regular.woff2"
        else:
            font_url = "/fonts/TT_Firs_Neue_Regular.woff2"
        if (
            'TT_Firs_Neue_Regular.woff2' not in head_html
            or 'rel="preload"' not in head_html
        ):
            if f'href="{font_url}" as="font"' not in head_html:
                preload_lines.append(
                    f'  <link rel="preload" href="{font_url}" as="font" type="font/woff2" crossorigin>'
                )
                stats["pass3_font_preload"] += 1

    # Pass 4 · DNS prefetch / preconnect
    # Detect external domains referenced in the page
    referenced_hosts = set()
    for m in re.finditer(r'https?://([^/"\s]+)', html):
        referenced_hosts.add(m.group(1).lower())

    dns_lines: list[str] = []

    # If Google Fonts referenced anywhere → preconnect to gstatic + googleapis
    uses_google_fonts = any(
        "fonts.googleapis.com" in h or "fonts.gstatic.com" in h
        for h in referenced_hosts
    )
    if uses_google_fonts:
        if 'preconnect" href="https://fonts.gstatic.com"' not in head_html:
            dns_lines.append(
                '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            )
            stats["pass3_preconnect"] += 1
        if 'preconnect" href="https://fonts.googleapis.com"' not in head_html:
            dns_lines.append(
                '  <link rel="preconnect" href="https://fonts.googleapis.com">'
            )
            stats["pass3_preconnect"] += 1

    for host in DNS_PREFETCH_HOSTS:
        if any(host in rh for rh in referenced_hosts):
            tag_needle = f'dns-prefetch" href="//{host}"'
            if tag_needle not in head_html:
                dns_lines.append(f'  <link rel="dns-prefetch" href="//{host}">')
                stats["pass4_dns"] += 1

    if not preload_lines and not dns_lines:
        return html

    insertion = ""
    if preload_lines and PRELOAD_BLOCK_MARKER not in head_html:
        insertion += "\n  " + PRELOAD_BLOCK_MARKER + "\n" + "\n".join(preload_lines) + "\n"
    elif preload_lines:
        insertion += "\n" + "\n".join(preload_lines) + "\n"
    if dns_lines and DNS_BLOCK_MARKER not in head_html:
        insertion += "  " + DNS_BLOCK_MARKER + "\n" + "\n".join(dns_lines) + "\n"
    elif dns_lines:
        insertion += "\n".join(dns_lines) + "\n"

    return html[:head_end.start()] + insertion + html[head_end.start():]


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def should_skip(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if rel in SKIP_REL:
        return True
    base = rel.rsplit("/", 1)[-1]
    return base in {"dashboard-cliente.html", "_t.html"}


def process_file(path: Path) -> bool:
    rel = path.relative_to(PUBLIC).as_posix()
    if should_skip(rel):
        return False

    original = path.read_text(encoding="utf-8")
    html = original

    html = pass_scripts(html, rel)
    html = pass_images(html, rel)
    html = pass_head_hints(html, rel)

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> int:
    if not PUBLIC.exists():
        print(f"ERROR: {PUBLIC} does not exist", file=sys.stderr)
        return 1

    files = sorted(PUBLIC.rglob("*.html"))
    scanned = 0
    modified = 0
    for p in files:
        rel = p.relative_to(PUBLIC).as_posix()
        if should_skip(rel):
            continue
        scanned += 1
        if process_file(p):
            modified += 1

    write_report(scanned, modified)
    print(f"Scanned: {scanned} · Modified: {modified}")
    print(f"Report: {REPORT}")
    return 0


def write_report(scanned: int, modified: int) -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    total_opt = (
        stats["pass1_defer"]
        + stats["pass1_async"]
        + stats["pass2_loading"]
        + stats["pass2_decoding"]
        + stats["pass2_fetchpriority"]
        + stats["pass3_css_preload"]
        + stats["pass3_font_preload"]
        + stats["pass3_preconnect"]
        + stats["pass4_dns"]
    )

    missing_alt_block = (
        "\n".join(f"  - {entry}" for entry in issues["missing_alt"][:50])
        or "  - (none)"
    )
    if len(issues["missing_alt"]) > 50:
        missing_alt_block += f"\n  - ...and {len(issues['missing_alt']) - 50} more"

    render_blocking_block = (
        "\n".join(f"  - {s}" for s in sorted(issues["render_blocking"]))
        or "  - (none)"
    )

    body = f"""# Performance Pass Report

Generated: {today}

## Summary
- Files scanned: {scanned}
- Files modified: {modified}
- Total optimizations applied: {total_opt}

## By pass
- Pass 1 (defer/async scripts): {stats['pass1_defer'] + stats['pass1_async']} changes
  - defer added: {stats['pass1_defer']}
  - async added: {stats['pass1_async']}
- Pass 2 (lazy loading images): {stats['pass2_loading'] + stats['pass2_decoding'] + stats['pass2_fetchpriority']} changes
  - loading attr: {stats['pass2_loading']}
  - decoding=async: {stats['pass2_decoding']}
  - fetchpriority=high (hero): {stats['pass2_fetchpriority']}
- Pass 3 (preload hints): {stats['pass3_css_preload'] + stats['pass3_font_preload'] + stats['pass3_preconnect']} changes
  - main CSS preload: {stats['pass3_css_preload']}
  - font preload: {stats['pass3_font_preload']}
  - preconnect (Google Fonts): {stats['pass3_preconnect']}
- Pass 4 (dns-prefetch): {stats['pass4_dns']} changes

## Issues found (require manual review)
- Images missing alt text ({len(issues['missing_alt'])}):
{missing_alt_block}
- Images missing width/height: {issues['missing_dims']}
- Render-blocking scripts identified:
{render_blocking_block}

## Recommended next steps
- Run a Lighthouse audit on a real Chrome instance against staging to validate LCP / CLS / INP improvements.
- Convert `/public/img/` PNG and JPG assets to WebP / AVIF; keep PNG fallback via `<picture>`.
- Inline critical CSS for above-the-fold (header + first hero) as a `<style>` block in `<head>` to remove the remaining render-blocking CSS round-trip.
- Register a Service Worker (network-first for HTML, cache-first for /css, /js, /fonts, /img) for offline + faster repeat visits.
- Add explicit `width` and `height` to every `<img>` to lock CLS at 0 (currently {issues['missing_dims']} images lack them).
- Audit alt text manually for the {len(issues['missing_alt'])} flagged images and provide meaningful, non-redundant copy.
- Consider switching the main CSS files to a single bundled `main.css` so the preload hint maps to one file rather than five.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(body, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
