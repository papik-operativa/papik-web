#!/usr/bin/env python3
"""
Internal Linking Analysis for PAPIK Group static site.

Walks all HTML pages in /public/, builds a link graph, computes per-page
metrics (in-degree, out-degree), identifies orphan pages and weak anchor
text, and emits a markdown report at /seo-internal/internal-linking-report.md.
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from urllib.parse import urlparse, urldefrag, unquote

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public"))
REPORT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "internal-linking-report.md")
)

# Files / directories we want to skip from analysis (still considered as link
# targets if referenced, but not analyzed as source pages).
EXCLUDE_FILE_PATTERNS = (
    "404.html",
    "dashboard-cliente.html",
    "cookie-banner.html",
)

# Generic / weak anchor text that should be improved with descriptive copy.
GENERIC_ANCHORS = {
    "click here", "clica aqui", "clica aquí", "haz clic", "haz clic aquí",
    "haz click", "haz click aquí", "click", "aquí", "aqui", "here",
    "read more", "llegir més", "llegeix més", "llegir mes", "leer más",
    "leer mas", "más", "mes", "more", "saber més", "saber mas", "saber más",
    "veure", "veure més", "veure mes", "ver", "ver más", "ver mas",
    "veure detalls", "ver detalles", "see more", "see details",
    "→", "›", ">>", "...", "▸", "↗",
    "info", "more info", "más info", "més info",
    "link", "enlace", "enllaç",
}


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []  # (href, anchor_text)
        self._current_href: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag, attrs):  # type: ignore[override]
        if tag.lower() != "a":
            return
        href = None
        for k, v in attrs:
            if k.lower() == "href":
                href = v
                break
        if not href:
            return
        self._current_href = href
        self._buf = []

    def handle_endtag(self, tag):  # type: ignore[override]
        if tag.lower() == "a" and self._current_href is not None:
            anchor = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self.links.append((self._current_href, anchor))
            self._current_href = None
            self._buf = []

    def handle_data(self, data):  # type: ignore[override]
        if self._current_href is not None:
            self._buf.append(data)

    def handle_startendtag(self, tag, attrs):  # type: ignore[override]
        # capture <img alt> inside <a> as anchor fallback
        if self._current_href is None:
            return
        if tag.lower() == "img":
            for k, v in attrs:
                if k.lower() == "alt" and v:
                    self._buf.append(v)


def is_excluded_source(rel_path: str) -> bool:
    base = os.path.basename(rel_path)
    if base in EXCLUDE_FILE_PATTERNS:
        return True
    if base.startswith("_"):
        return True
    return False


def list_html_files(root: str) -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        # prune
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            if f.lower().endswith(".html"):
                full = os.path.join(dirpath, f)
                out.append(full)
    return sorted(out)


def lang_of(rel_path: str) -> str:
    parts = rel_path.split(os.sep)
    if parts and parts[0] == "es":
        return "ES"
    if parts and parts[0] == "en":
        return "EN"
    return "CA"


def resolve_link(src_abs: str, href: str) -> tuple[str | None, bool]:
    """Resolve an href relative to a source HTML file.

    Returns (relative-path-within-public, is_internal).
    relative-path is normalized with forward slashes; None if cannot resolve to
    a file inside /public/.
    """
    if not href:
        return None, False
    href = href.strip()
    if not href:
        return None, False

    # Strip fragment & query
    href_no_frag, _ = urldefrag(href)
    parsed = urlparse(href_no_frag)

    # Skip non-page schemes
    if parsed.scheme in ("mailto", "tel", "javascript", "data", "sms", "whatsapp"):
        return None, False

    # External
    if parsed.scheme in ("http", "https"):
        if parsed.netloc and "papikgroup" not in parsed.netloc.lower() and "papik.com" not in parsed.netloc.lower():
            return None, False
        # treat papikgroup.com / papik.com URLs as internal -> path
        path = parsed.path or "/"
        target_rel = path.lstrip("/")
        if target_rel.endswith("/") or target_rel == "":
            target_rel += "index.html"
        target_rel = unquote(target_rel)
        target_abs = os.path.normpath(os.path.join(ROOT, target_rel))
    else:
        # Relative or root-relative
        path = parsed.path
        if not path:
            return None, False
        path = unquote(path)
        if path.startswith("/"):
            target_abs = os.path.normpath(os.path.join(ROOT, path.lstrip("/")))
        else:
            target_abs = os.path.normpath(os.path.join(os.path.dirname(src_abs), path))

    # If target is a directory, append index.html
    if os.path.isdir(target_abs):
        target_abs = os.path.join(target_abs, "index.html")
    elif not os.path.splitext(target_abs)[1]:
        # Extensionless paths: try .html suffix
        if os.path.exists(target_abs + ".html"):
            target_abs = target_abs + ".html"
        elif os.path.isdir(target_abs):
            target_abs = os.path.join(target_abs, "index.html")

    # Must be inside ROOT
    try:
        common = os.path.commonpath([ROOT, target_abs])
    except ValueError:
        return None, False
    if common != ROOT:
        return None, False

    rel = os.path.relpath(target_abs, ROOT).replace(os.sep, "/")
    return rel, True


CANONICAL_RE = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', re.IGNORECASE
)


def main() -> int:
    files = list_html_files(ROOT)
    pages = []
    for f in files:
        rel = os.path.relpath(f, ROOT).replace(os.sep, "/")
        if is_excluded_source(rel):
            continue
        pages.append(rel)
    page_set = set(pages)

    # Build canonical-URL -> rel-path index so we can match links that use
    # the rewritten/canonical URL form (cleanUrls=true).
    canonical_to_rel: dict[str, str] = {}
    for rel in pages:
        full = os.path.join(ROOT, rel)
        try:
            with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                head = fh.read(8192)
        except OSError:
            continue
        m = CANONICAL_RE.search(head)
        if not m:
            continue
        url = m.group(1).strip()
        parsed = urlparse(url)
        path = (parsed.path or "/").rstrip("/")
        if not path:
            path = "/"
        canonical_to_rel[path] = rel
        # Also index without leading slash for path-only match
        canonical_to_rel[path.lstrip("/")] = rel

    in_links: dict[str, list[tuple[str, str]]] = defaultdict(list)   # target -> [(source, anchor)]
    out_links: dict[str, list[tuple[str, str]]] = defaultdict(list)  # source -> [(target, anchor)]
    weak_anchors: list[tuple[str, str, str]] = []  # (source, target, anchor)
    broken_internal: list[tuple[str, str]] = []    # (source, raw href)

    for rel in pages:
        full = os.path.join(ROOT, rel)
        try:
            with open(full, "r", encoding="utf-8", errors="ignore") as fh:
                html = fh.read()
        except OSError:
            continue
        parser = LinkExtractor()
        try:
            parser.feed(html)
        except Exception:
            pass

        for href, anchor in parser.links:
            target_rel, is_internal = resolve_link(full, href)
            # Try canonical-URL match if file-resolution failed
            if (target_rel is None or target_rel not in page_set) and href:
                href_no_frag, _ = urldefrag(href.strip())
                parsed = urlparse(href_no_frag)
                if parsed.scheme in ("", "http", "https"):
                    path = parsed.path or ""
                    path = unquote(path).rstrip("/")
                    if not path:
                        path = "/"
                    cand = canonical_to_rel.get(path) or canonical_to_rel.get(path.lstrip("/"))
                    if cand:
                        target_rel = cand
                        is_internal = True
            if not is_internal or target_rel is None:
                continue
            # Self-link: skip
            if target_rel == rel:
                continue
            if target_rel not in page_set:
                # Internal-looking but not a known page (asset, missing file, etc.)
                if target_rel.endswith(".html"):
                    broken_internal.append((rel, href))
                continue

            out_links[rel].append((target_rel, anchor))
            in_links[target_rel].append((rel, anchor))

            anchor_norm = anchor.strip().lower()
            if anchor_norm in GENERIC_ANCHORS or (anchor_norm and len(anchor_norm) <= 3 and not anchor_norm.isalpha()):
                weak_anchors.append((rel, target_rel, anchor))

    # Metrics
    indeg = {p: len(in_links.get(p, [])) for p in pages}
    outdeg = {p: len(out_links.get(p, [])) for p in pages}
    total_links = sum(outdeg.values())
    orphans = [p for p in pages if indeg[p] == 0]
    weak = [p for p in pages if 1 <= indeg[p] <= 2]
    avg_links = (total_links / len(pages)) if pages else 0

    top_in = sorted(pages, key=lambda p: indeg[p], reverse=True)[:10]
    top_out = sorted(pages, key=lambda p: outdeg[p], reverse=True)[:10]

    # Group orphans by language
    orphans_by_lang: dict[str, list[str]] = defaultdict(list)
    for o in orphans:
        orphans_by_lang[lang_of(o)].append(o)

    # Cross-lang imbalance: same article with very different in-degree
    # Pair by stripping prefix
    imbalances: list[tuple[str, dict[str, int]]] = []
    base_groups: dict[str, dict[str, str]] = defaultdict(dict)
    for p in pages:
        lang = lang_of(p)
        # heuristic group key: filename without lang dir
        key = os.path.basename(p)
        base_groups[key][lang] = p
    for key, langmap in base_groups.items():
        if len(langmap) >= 2:
            counts = {l: indeg[langmap[l]] for l in langmap}
            mx, mn = max(counts.values()), min(counts.values())
            if mx >= 3 and mn == 0:
                imbalances.append((key, counts))

    # Compose report
    lines: list[str] = []
    lines.append("# Internal Linking Analysis Report\n")
    lines.append("Generated: 2026-04-29\n\n")
    lines.append("## Summary\n")
    lines.append(f"- Total pages analyzed: {len(pages)}\n")
    lines.append(f"- Total internal links: {total_links}\n")
    lines.append(f"- Orphans (0 in-links): {len(orphans)}\n")
    lines.append(f"- Weakly-linked (1-2 in-links): {len(weak)}\n")
    lines.append(f"- Average outbound internal links per page: {avg_links:.1f}\n\n")

    lines.append("## Top 10 most-linked-to pages\n")
    for i, p in enumerate(top_in, 1):
        lines.append(f"{i}. `{p}` — {indeg[p]} in-links\n")
    lines.append("\n")

    lines.append("## Top 10 pages with most outbound links\n")
    for i, p in enumerate(top_out, 1):
        lines.append(f"{i}. `{p}` — {outdeg[p]} out-links\n")
    lines.append("\n")

    lines.append("## Orphans by language\n")
    for l in ("CA", "ES", "EN"):
        lst = orphans_by_lang.get(l, [])
        lines.append(f"### {l} ({len(lst)})\n")
        if not lst:
            lines.append("- (none)\n")
        for p in sorted(lst):
            lines.append(f"- `{p}`\n")
        lines.append("\n")

    lines.append("## Cross-language balance check\n")
    lines.append(
        f"- CA orphans: {len(orphans_by_lang.get('CA', []))}, "
        f"ES orphans: {len(orphans_by_lang.get('ES', []))}, "
        f"EN orphans: {len(orphans_by_lang.get('EN', []))}\n\n"
    )
    lines.append("### Pages with imbalanced cross-language link profile\n")
    if not imbalances:
        lines.append("- (none detected with threshold max>=3 / min=0)\n")
    for key, counts in sorted(imbalances)[:30]:
        c_str = ", ".join(f"{l}={n}" for l, n in counts.items())
        lines.append(f"- `{key}` — {c_str}\n")
    lines.append("\n")

    lines.append("## Generic anchor texts (improvement candidates)\n")
    if not weak_anchors:
        lines.append("- (none detected)\n")
    seen = set()
    sample_n = 0
    for src, tgt, anchor in weak_anchors:
        sig = (src, tgt, anchor.lower())
        if sig in seen:
            continue
        seen.add(sig)
        lines.append(f"- `{src}` → `{tgt}` anchor: \"{anchor}\"\n")
        sample_n += 1
        if sample_n >= 50:
            lines.append(f"- ... and {len(weak_anchors) - 50} more\n")
            break
    lines.append("\n")

    if broken_internal:
        lines.append("## Broken internal HTML links (target file not found)\n")
        for src, href in broken_internal[:30]:
            lines.append(f"- `{src}` → `{href}`\n")
        if len(broken_internal) > 30:
            lines.append(f"- ... and {len(broken_internal) - 30} more\n")
        lines.append("\n")

    lines.append("## Recommendations\n")
    lines.append(
        "1. Add contextual links from the relevant hub pages (blog.html, "
        "projectes.html, construccio.html, rehabilitacio.html) to every "
        "orphan article and project, in all three languages.\n"
    )
    lines.append(
        "2. Replace generic anchor text (\"veure\", \"més\", \"read more\") with "
        "keyword-rich phrases that describe the destination.\n"
    )
    lines.append(
        "3. Wire cross-language hreflang siblings via visible language switchers "
        "so EN/ES counterparts inherit authority from the CA hub.\n"
    )
    lines.append(
        "4. Add 2-3 contextual related-article links inside each blog post body "
        "(not only the related-posts widget) using semantic anchors.\n"
    )
    lines.append(
        "5. Resolve any broken internal HTML targets listed above before they "
        "leak crawl budget.\n"
    )

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

    # Preserve any existing "## Fixes applied" section so re-runs do not
    # overwrite the human-curated changelog appended after the first run.
    appended = ""
    if os.path.exists(REPORT_PATH):
        try:
            with open(REPORT_PATH, "r", encoding="utf-8") as fh:
                prev = fh.read()
            marker = "## Fixes applied"
            idx = prev.find(marker)
            if idx >= 0:
                appended = "\n" + prev[idx:]
        except OSError:
            pass

    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write("".join(lines))
        if appended:
            fh.write(appended)

    # Console summary
    print(f"Pages analyzed: {len(pages)}")
    print(f"Total internal links: {total_links}")
    print(f"Orphans: {len(orphans)}")
    print(f"Weak (1-2): {len(weak)}")
    print(f"Weak anchors: {len(weak_anchors)}")
    print(f"Broken internal: {len(broken_internal)}")
    print(f"Report: {REPORT_PATH}")

    # Emit machine-readable orphan list to stderr for chaining
    print("ORPHANS_START", file=sys.stderr)
    for p in orphans:
        print(p, file=sys.stderr)
    print("ORPHANS_END", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
