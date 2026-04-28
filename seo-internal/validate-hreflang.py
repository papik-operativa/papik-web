#!/usr/bin/env python3
"""
Hreflang completeness audit for PAPIK Group static site.

Walks /public/, parses <link rel="alternate" hreflang> tags inside <head>,
and validates:
  1. each page declares a full triplet (ca + es + en) plus x-default
  2. every alternate URL resolves to a real file on disk
  3. the cluster is bidirectional: if A points at B, B must point back at A
  4. x-default points to the CA URL (project convention)

Outputs Markdown report at /seo-internal/hreflang-validation-report.md.

Run: python3 seo-internal/validate-hreflang.py
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# --- config -----------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
REPORT = ROOT / "seo-internal" / "hreflang-validation-report.md"
DOMAIN = "https://www.papik.cat"
# Accept both apex and www. The cluster mixes both in practice.
DOMAIN_PREFIXES = ("https://www.papik.cat", "https://papik.cat")

# Files / directories to ignore during the walk.
EXCLUDE_FILES = {"404.html"}
EXCLUDE_FILENAME_SUBSTRINGS = ("dashboard", "test", "preview")
EXCLUDE_DIR_NAMES = {"img", "css", "js", "fonts", "exports"}

# --- regex (head + hreflang) ------------------------------------------------

HEAD_RE = re.compile(r"<head\b[^>]*>(.*?)</head>", re.IGNORECASE | re.DOTALL)
LINK_RE = re.compile(
    r"""<link\s+[^>]*rel=["']alternate["'][^>]*>""",
    re.IGNORECASE,
)
HREFLANG_ATTR_RE = re.compile(r"""hreflang=["']([^"']+)["']""", re.IGNORECASE)
HREF_ATTR_RE = re.compile(r"""href=["']([^"']+)["']""", re.IGNORECASE)


# --- helpers ----------------------------------------------------------------


def should_skip(path: Path) -> bool:
    name = path.name.lower()
    if name in EXCLUDE_FILES:
        return True
    if any(s in name for s in EXCLUDE_FILENAME_SUBSTRINGS):
        return True
    parts = {p.lower() for p in path.parts}
    if parts & EXCLUDE_DIR_NAMES:
        return True
    return False


def walk_html() -> List[Path]:
    out: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(PUBLIC):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            p = Path(dirpath) / fn
            if should_skip(p):
                continue
            out.append(p)
    return sorted(out)


def url_to_path(url: str) -> Optional[Path]:
    """Resolve a public URL to its local file path under /public/.

    The site uses Vercel cleanUrls=true: /<slug> serves /<slug>.html.
    Alternates are emitted with the .html suffix already, but be lenient.
    """
    matched_prefix = next((p for p in DOMAIN_PREFIXES if url.startswith(p)), None)
    if matched_prefix is None:
        return None
    rel = url[len(matched_prefix):].lstrip("/")
    rel = rel.split("?", 1)[0].split("#", 1)[0]
    if not rel or rel.endswith("/"):
        rel = (rel or "") + "index.html"
    candidate = PUBLIC / rel
    # Prefer .html sibling over a directory match (Vercel cleanUrls=true serves
    # /en/retrofit.html for /en/retrofit; the /en/retrofit/ directory only
    # holds nested children like /en/retrofit/communities.html).
    if not rel.endswith(".html"):
        alt = PUBLIC / (rel + ".html")
        if alt.is_file():
            return alt
    if candidate.is_file():
        return candidate
    if candidate.is_dir():
        idx = candidate / "index.html"
        if idx.is_file():
            return idx
    return None


def path_to_url(p: Path) -> str:
    rel = p.relative_to(PUBLIC).as_posix()
    return f"{DOMAIN}/{rel}"


def normalize_alt(url: str) -> Optional[str]:
    """Resolve an alternate URL to its canonical form: file path under PUBLIC,
    re-emitted under the www domain with .html suffix. Returns None if the
    target file does not exist (so the caller can flag a dead link)."""
    target = url_to_path(url)
    if target is None:
        return None
    return path_to_url(target)


def parse_hreflang(html_path: Path) -> Dict[str, str]:
    """Return {hreflang: url} for the first <head> block of the file."""
    try:
        text = html_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    head_match = HEAD_RE.search(text)
    head = head_match.group(1) if head_match else text
    out: Dict[str, str] = {}
    for tag in LINK_RE.findall(head):
        lang_m = HREFLANG_ATTR_RE.search(tag)
        href_m = HREF_ATTR_RE.search(tag)
        if not lang_m or not href_m:
            continue
        lang = lang_m.group(1).strip().lower()
        href = href_m.group(1).strip()
        # First occurrence wins (some files have duplicate blocks).
        out.setdefault(lang, href)
    return out


# --- main -------------------------------------------------------------------


def main() -> int:
    pages = walk_html()
    parsed: Dict[Path, Dict[str, str]] = {p: parse_hreflang(p) for p in pages}

    # Index every page by its canonical URL so we can resolve alternates fast.
    by_url: Dict[str, Path] = {path_to_url(p): p for p in pages}

    expected_langs = {"ca", "es", "en"}

    full_triplet: List[Path] = []
    missing_one: List[Tuple[Path, List[str]]] = []
    missing_two_plus: List[Tuple[Path, List[str]]] = []
    no_hreflang_at_all: List[Path] = []

    dead_alternates: List[Tuple[Path, str, str]] = []
    xdefault_issues: List[Tuple[Path, str]] = []
    bidirectional_issues: List[Tuple[Path, str, Path, str]] = []

    for page, tags in parsed.items():
        present_langs = set(tags.keys())
        if not (present_langs & (expected_langs | {"x-default"})):
            no_hreflang_at_all.append(page)
            continue

        missing = sorted(expected_langs - present_langs)
        has_xdefault = "x-default" in tags
        if not missing and has_xdefault:
            full_triplet.append(page)
        else:
            slots_missing = list(missing)
            if not has_xdefault:
                slots_missing.append("x-default")
            if len(slots_missing) == 1:
                missing_one.append((page, slots_missing))
            else:
                missing_two_plus.append((page, slots_missing))

        # x-default convention: should equal the CA url.
        if has_xdefault and "ca" in tags and tags["x-default"] != tags["ca"]:
            xdefault_issues.append(
                (page, f"x-default={tags['x-default']} != ca={tags['ca']}")
            )

        # Resolve every alternate to disk; flag dead targets.
        for lang, url in tags.items():
            target = url_to_path(url)
            if target is None:
                dead_alternates.append((page, lang, url))

    # Bidirectional check: if A->B, then B->A on the same lang it claims to be.
    # Compare on canonical (domain-normalized + .html-suffixed) URLs so that
    # http(s)://papik.cat/foo and https://www.papik.cat/foo.html are treated
    # as the same target.
    for page, tags in parsed.items():
        page_url = path_to_url(page)
        norm = {lang: normalize_alt(u) for lang, u in tags.items()}
        # Determine "self lang" from the cluster.
        self_lang = next(
            (lg for lg, n in norm.items() if n == page_url and lg != "x-default"),
            None,
        )
        if self_lang is None:
            continue
        for lang, normalized in norm.items():
            if lang in ("x-default",):
                continue
            if lang == self_lang:
                continue
            if normalized is None:
                continue  # already flagged as dead
            partner = url_to_path(tags[lang])
            if partner is None:
                continue
            partner_tags = parsed.get(partner, {})
            back_norm = normalize_alt(partner_tags.get(self_lang, ""))
            if back_norm != page_url:
                bidirectional_issues.append(
                    (page, lang, partner, partner_tags.get(self_lang) or "<missing>")
                )

    # --- write report -------------------------------------------------------
    total = len(pages)
    triplet_pct = (len(full_triplet) / total * 100) if total else 0.0
    today = date.today().isoformat()

    lines: List[str] = []
    lines.append("# Hreflang Validation Report")
    lines.append("")
    lines.append(f"Generated: {today}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total HTML pages: {total}")
    lines.append(
        f"- Pages with full triplet (CA + ES + EN + x-default): "
        f"{len(full_triplet)} ({triplet_pct:.1f}%)"
    )
    lines.append(f"- Pages missing 1 sibling: {len(missing_one)}")
    lines.append(f"- Pages missing 2+ siblings: {len(missing_two_plus)}")
    lines.append(f"- Pages with no hreflang at all: {len(no_hreflang_at_all)}")
    lines.append(f"- Bidirectional inconsistencies: {len(bidirectional_issues)}")
    lines.append(f"- Dead alternate URLs (404 targets): {len(dead_alternates)}")
    lines.append(f"- x-default issues: {len(xdefault_issues)}")
    lines.append("")

    lines.append("## Errors by category")
    lines.append("")
    lines.append("### Missing siblings (asymmetric triplets)")
    if not missing_one and not missing_two_plus and not no_hreflang_at_all:
        lines.append("- (none)")
    else:
        for p, miss in missing_one + missing_two_plus:
            rel = p.relative_to(PUBLIC).as_posix()
            lines.append(f"- `/{rel}` missing: {', '.join(miss)}")
        for p in no_hreflang_at_all:
            rel = p.relative_to(PUBLIC).as_posix()
            lines.append(f"- `/{rel}` has NO hreflang tags at all")
    lines.append("")

    lines.append("### Bidirectional inconsistencies")
    if not bidirectional_issues:
        lines.append("- (none)")
    else:
        for a, lang, b, back in bidirectional_issues:
            rel_a = a.relative_to(PUBLIC).as_posix()
            rel_b = b.relative_to(PUBLIC).as_posix()
            lines.append(
                f"- `/{rel_a}` -> `{lang}` -> `/{rel_b}`, "
                f"but partner returns `{back}`"
            )
    lines.append("")

    lines.append("### Dead alternates (target file does not exist)")
    if not dead_alternates:
        lines.append("- (none)")
    else:
        for p, lang, url in dead_alternates:
            rel = p.relative_to(PUBLIC).as_posix()
            lines.append(f"- `/{rel}` `hreflang=\"{lang}\"` -> {url} (404)")
    lines.append("")

    lines.append("### x-default issues")
    if not xdefault_issues:
        lines.append("- (none)")
    else:
        for p, msg in xdefault_issues:
            rel = p.relative_to(PUBLIC).as_posix()
            lines.append(f"- `/{rel}`: {msg}")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    if total and triplet_pct >= 99:
        lines.append("- Cluster is healthy. Re-run after every build.")
    else:
        lines.append(
            "- Re-run `generate_html.py` for any page in the *Missing siblings* "
            "list; the build pipeline derives hreflang from `slug-mapping.json`, "
            "so missing tags usually mean the slug pair is absent there."
        )
        lines.append(
            "- For *Dead alternates*, either create the target page or remove "
            "the row from `slug-mapping.json` (do NOT hand-edit the HTML; "
            "see CLAUDE.md `Don't repeat` warnings)."
        )
        lines.append(
            "- *Bidirectional inconsistencies* almost always come from one side "
            "being regenerated and the other not. Rebuild both partners."
        )
        lines.append(
            "- *x-default issues*: project convention pins x-default to the CA "
            "URL (style-guide-editorial.md §5)."
        )
    lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {REPORT}")
    print(
        f"Pages: {total} | full triplet: {len(full_triplet)} "
        f"({triplet_pct:.1f}%) | missing-1: {len(missing_one)} | "
        f"missing-2+: {len(missing_two_plus)} | dead: {len(dead_alternates)} | "
        f"bidir: {len(bidirectional_issues)} | xdef: {len(xdefault_issues)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
