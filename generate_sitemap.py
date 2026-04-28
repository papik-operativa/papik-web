#!/usr/bin/env python3
"""
PAPIK sitemap generator (filesystem-driven).

Walks the /public tree, parses each .html file for canonical and hreflang
metadata, and emits public/sitemap.xml with proper xhtml:link annotations.

Replaces the legacy slug-mapping.json driven generator. Slug-mapping.json is
kept as the source of truth for redirects and rewrites; sitemap.xml is now
generated from what is actually published.

Usage:
  python3 generate_sitemap.py             # Write public/sitemap.xml
  python3 generate_sitemap.py --dry-run   # Print to stdout instead
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).parent
PUBLIC = ROOT / "public"
OUTPUT = PUBLIC / "sitemap.xml"
SLUG_MAP = ROOT / "seo-internal" / "slug-mapping.json"
DOMAIN = "https://papik.cat"

# Files to always exclude (non-indexable / private / partials)
EXCLUDE_FILENAMES = {
    "dashboard-cliente.html",
    "_t.html",
    "cookie-banner.html",
}

# Directories under /public to walk. Missing dirs are silently skipped.
WALK_DIRS = [
    "",                    # /public root (CA pages)
    "zones",
    "comarques",
    "es",
    "es/zonas",
    "es/comarcas",
    "en",
    "en/areas",
    "en/regions",
    "en/retrofit",
]

# Regex helpers
RE_CANONICAL = re.compile(
    r'<link\s+rel="canonical"\s+href="([^"]+)"', re.IGNORECASE
)
RE_HREFLANG = re.compile(
    r'<link\s+rel="alternate"\s+hreflang="([^"]+)"\s+href="([^"]+)"',
    re.IGNORECASE,
)
RE_MODIFIED = re.compile(
    r'<meta\s+property="article:modified_time"\s+content="([^"]+)"',
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Page classification (priority + changefreq)
# ---------------------------------------------------------------------------

# Tier 1: homepages, key services, and primary landing pages.
TIER1_SLUGS = {
    "construccio", "construccion", "construction",
    "rehabilitacio", "rehabilitacion", "retrofit",
    "promocio", "promocion", "development",
    "patrimonis", "patrimonios", "wealth",
    "pressupost", "presupuesto",
    "comunitats", "comunidades", "communities",
}

# Tier 2: secondary landings (zonals/comarcal/blog hub/about).
TIER2_SLUGS = {
    "blog", "nosaltres", "nosotros", "projectes", "proyectos", "usuaris",
    "usuarios", "qualitats", "qualities",
}

LEGAL_SLUGS = {
    "avis-legal", "aviso-legal", "legal-notice",
    "politica-cookies", "politica-cookies", "cookie-policy",
    "politica-privacitat", "politica-privacidad", "privacy-policy",
}


def classify(canonical_url: str, file_path: Path) -> Tuple[float, str]:
    """Return (priority, changefreq) given the canonical URL and source file."""
    # Strip domain
    path = canonical_url.replace(DOMAIN, "", 1).strip("/")

    # Homepages
    if path in {"", "es", "en"}:
        return 1.0, "weekly"

    # Article pages (article-* slug, in any language root)
    last = path.split("/")[-1]
    if last.startswith("article-"):
        return 0.7, "monthly"

    # Project pages (projecte-/proyecto-)
    if last.startswith("projecte-") or last.startswith("proyecto-"):
        return 0.6, "monthly"

    # Legal pages
    if last in LEGAL_SLUGS:
        return 0.3, "yearly"

    # Tier 1 (services + key landings + comunitats nested)
    if last in TIER1_SLUGS:
        return 0.9, "weekly"

    # Comarcal / comarcas / regions hubs (directory based)
    if "/comarques/" in canonical_url or "/comarcas/" in canonical_url \
            or "/regions/" in canonical_url:
        return 0.8, "monthly"

    # Tier 2 (blog hub, about, projectes hub, zonals)
    if last in TIER2_SLUGS:
        return 0.8, "weekly"

    # Zonal landings: zones/<slug>, zonas/<slug>, areas/<slug>
    if "/zones/" in canonical_url or "/zonas/" in canonical_url \
            or "/areas/" in canonical_url:
        return 0.8, "monthly"

    # Default mid-tier
    return 0.7, "monthly"


# ---------------------------------------------------------------------------
# Slug-mapping fallback
# ---------------------------------------------------------------------------

def file_to_url(file_path: Path) -> str:
    """Derive the public URL from a public/ file path under Vercel cleanUrls.

    Examples:
      public/index.html             -> /
      public/construccio.html       -> /construccio
      public/es/index.html          -> /es/
      public/es/zonas/bellaterra.html -> /es/zonas/bellaterra
      public/zones/bellaterra.html  -> /zones/bellaterra
    """
    rel = file_path.relative_to(PUBLIC).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-len("index.html")]
    if rel.endswith(".html"):
        rel = rel[:-len(".html")]
    return "/" + rel


def load_slug_map() -> List[dict]:
    """Load page list from slug-mapping.json (best-effort)."""
    if not SLUG_MAP.exists():
        return []
    try:
        with SLUG_MAP.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    return data.get("pages", [])


def build_url_to_page(pages: List[dict]) -> Dict[str, dict]:
    """Build a lookup: any-language URL -> page entry (raw slug-map record)."""
    table: Dict[str, dict] = {}
    for page in pages:
        for lang in ("ca", "es", "en"):
            url = page.get(lang)
            if url:
                table[url.rstrip("/") or "/"] = page
    return table


def fallback_hreflang(url: str, url_to_page: Dict[str, dict]) -> Dict[str, str]:
    """Look up a URL in the slug-mapping table and return absolute hreflang map.

    Only includes language siblings whose underlying file actually exists.
    """
    key = url.rstrip("/") or "/"
    page = url_to_page.get(key)
    if not page:
        return {}
    out: Dict[str, str] = {}
    for lang in ("ca", "es", "en"):
        lang_url = page.get(lang)
        if not lang_url:
            continue
        target_path = _url_to_filepath(lang_url)
        if target_path and target_path.exists():
            out[lang] = f"{DOMAIN}{lang_url}"
    if "ca" in out:
        out["x-default"] = out["ca"]
    elif out:
        out["x-default"] = next(iter(out.values()))
    return out


def _url_to_filepath(url: str) -> Optional[Path]:
    """Inverse of file_to_url: map a public URL back to its .html file."""
    path = url.lstrip("/")
    if path == "" or path in ("es/", "en/", "es", "en"):
        if path.startswith("es"):
            return PUBLIC / "es" / "index.html"
        if path.startswith("en"):
            return PUBLIC / "en" / "index.html"
        return PUBLIC / "index.html"
    if path.endswith("/"):
        return PUBLIC / path / "index.html"
    return PUBLIC / f"{path}.html"


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------

def parse_html(file_path: Path,
               url_to_page: Optional[Dict[str, dict]] = None
               ) -> Optional[dict]:
    """Extract canonical, hreflang map, and lastmod from an HTML file.

    If the file has no <link rel="canonical">, derive canonical from the
    filesystem path (Vercel cleanUrls) and look up hreflang siblings in
    slug-mapping.json if provided.
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    canonical_match = RE_CANONICAL.search(text)
    canonical: Optional[str] = (
        canonical_match.group(1).strip() if canonical_match else None
    )

    hreflang: Dict[str, str] = {}
    for lang, href in RE_HREFLANG.findall(text):
        hreflang[lang.strip().lower()] = href.strip()

    fallback_used = False
    if not canonical:
        derived_path = file_to_url(file_path)
        canonical = f"{DOMAIN}{derived_path}"
        fallback_used = True

    if not hreflang and url_to_page is not None:
        derived_path = canonical.replace(DOMAIN, "", 1) or "/"
        hreflang = fallback_hreflang(derived_path, url_to_page)

    mod_match = RE_MODIFIED.search(text)
    if mod_match:
        lastmod = _normalize_iso_date(mod_match.group(1).strip())
    else:
        mtime = _dt.datetime.fromtimestamp(file_path.stat().st_mtime)
        lastmod = mtime.date().isoformat()

    return {
        "file": file_path,
        "canonical": canonical,
        "hreflang": hreflang,
        "lastmod": lastmod,
        "fallback_used": fallback_used,
    }


def _normalize_iso_date(raw: str) -> str:
    """Normalize an ISO-ish datetime to YYYY-MM-DD."""
    raw = raw.strip()
    # Try parsing common ISO 8601 forms
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d", "%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return _dt.datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    # Fallback: take first 10 chars if they look like a date
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[:10]
    return _dt.date.today().isoformat()


# ---------------------------------------------------------------------------
# Walk
# ---------------------------------------------------------------------------

def collect_html_files() -> List[Path]:
    files: List[Path] = []
    for rel in WALK_DIRS:
        d = PUBLIC / rel if rel else PUBLIC
        if not d.exists() or not d.is_dir():
            continue
        for entry in sorted(d.iterdir()):
            if entry.is_file() and entry.suffix == ".html":
                if entry.name in EXCLUDE_FILENAMES:
                    continue
                files.append(entry)
    return files


# ---------------------------------------------------------------------------
# Sitemap rendering
# ---------------------------------------------------------------------------

def render_sitemap(entries: List[dict]) -> str:
    """Render the full sitemap XML.

    `entries` is a list of dicts with: canonical, hreflang, lastmod, priority,
    changefreq.
    """
    lines: List[str] = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    )

    for e in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{e['canonical']}</loc>")
        lines.append(f"    <lastmod>{e['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{e['changefreq']}</changefreq>")
        lines.append(f"    <priority>{e['priority']:.1f}</priority>")
        # Stable hreflang ordering: ca, es, en, x-default, then any others.
        order = ["ca", "es", "en", "x-default"]
        seen = set()
        for lang in order:
            if lang in e["hreflang"]:
                href = e["hreflang"][lang]
                lines.append(
                    f'    <xhtml:link rel="alternate" hreflang="{lang}" '
                    f'href="{href}"/>'
                )
                seen.add(lang)
        for lang, href in e["hreflang"].items():
            if lang not in seen:
                lines.append(
                    f'    <xhtml:link rel="alternate" hreflang="{lang}" '
                    f'href="{href}"/>'
                )
        lines.append("  </url>")

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_entries() -> Tuple[List[dict], List[Path], List[Path]]:
    files = collect_html_files()
    pages = load_slug_map()
    url_to_page = build_url_to_page(pages)

    entries: List[dict] = []
    skipped_no_canonical: List[Path] = []
    seen_canonicals: Dict[str, Path] = {}
    duplicates: List[Path] = []

    for f in files:
        parsed = parse_html(f, url_to_page=url_to_page)
        if parsed is None:
            skipped_no_canonical.append(f)
            continue
        canonical = parsed["canonical"]
        if canonical in seen_canonicals:
            duplicates.append(f)
            continue
        seen_canonicals[canonical] = f

        priority, changefreq = classify(canonical, f)
        entries.append({
            "canonical": canonical,
            "hreflang": parsed["hreflang"],
            "lastmod": parsed["lastmod"],
            "priority": priority,
            "changefreq": changefreq,
            "file": f,
            "fallback_used": parsed.get("fallback_used", False),
        })

    # Sort by priority desc, then by canonical asc for stable output.
    entries.sort(key=lambda e: (-e["priority"], e["canonical"]))
    return entries, skipped_no_canonical, duplicates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print sitemap to stdout instead of writing.")
    args = parser.parse_args()

    entries, skipped, duplicates = build_entries()
    sitemap = render_sitemap(entries)

    if args.dry_run:
        sys.stdout.write(sitemap)
        return 0

    OUTPUT.write_text(sitemap, encoding="utf-8")
    print(f"OK · sitemap.xml written: {OUTPUT}")
    print(f"   {len(entries)} URLs included")
    if skipped:
        print(f"   {len(skipped)} files skipped (no canonical):")
        for p in skipped:
            print(f"     - {p.relative_to(PUBLIC)}")
    if duplicates:
        print(f"   {len(duplicates)} files skipped (duplicate canonical):")
        for p in duplicates:
            print(f"     - {p.relative_to(PUBLIC)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
