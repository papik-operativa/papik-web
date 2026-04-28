#!/usr/bin/env python3
"""
PAPIK Group — S5 Pre-launch Static QA Script
=============================================

Scans the static-site output under /public/ and produces machine-checkable
findings against 9 dimensions (HTML structure, SEO meta, JSON-LD, hreflang,
internal links, sitemap/robots, accessibility, performance, cross-lang).

Usage:
    python3 qa-script.py              # full report (writes JSON next to itself)
    python3 qa-script.py --report-md  # also (re)write s5-qa-report.md skeleton

This is a STATIC analyzer — no browser, no JS execution, no HTTP fetching.
Items requiring runtime checks are flagged as "manual QA".
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent  # papik-web/
PUBLIC = ROOT / "public"
SEO_DIR = ROOT / "seo-internal"
SCHEMAS_DIR = SEO_DIR / "schemas"
VERCEL_JSON = ROOT / "vercel.json"
VERCEL_JSON_CAND = ROOT / "vercel.json.candidate"

# In-scope HTML directories
SCOPE_DIRS = [
    PUBLIC,                       # CA root
    PUBLIC / "zones",             # CA landings
    PUBLIC / "es",                # ES root
    PUBLIC / "es" / "zonas",      # ES landings
    PUBLIC / "en",                # EN root
    PUBLIC / "en" / "areas",      # EN landings
    PUBLIC / "en" / "retrofit",   # EN sub-pages
]

VALID_LANGS = {"ca", "es", "en"}

SEVERITY = ("P0", "P1", "P2", "P3")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def lang_from_path(p: Path) -> str:
    parts = p.relative_to(PUBLIC).parts
    if parts and parts[0] == "es":
        return "es"
    if parts and parts[0] == "en":
        return "en"
    return "ca"


def in_scope(p: Path) -> bool:
    """Only direct children of SCOPE_DIRS, not deeper."""
    if p.suffix.lower() != ".html":
        return False
    for d in SCOPE_DIRS:
        if p.parent == d:
            return True
    return False


def iter_in_scope() -> list[Path]:
    files = []
    for d in SCOPE_DIRS:
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.is_file() and f.suffix.lower() == ".html":
                files.append(f)
    return sorted(files)


# ---------------------------------------------------------------------------
# Lightweight HTML parser
# ---------------------------------------------------------------------------


class PageParser(HTMLParser):
    """Collects what we need without pulling a heavy dependency."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.has_doctype = False
        self.html_lang: str | None = None
        self.charset: str | None = None
        self.viewport: str | None = None
        self.title: str | None = None
        self._in_title = False
        self._title_buf: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.headings: list[tuple[int, str]] = []  # (level, text)
        self._heading_stack: list[tuple[int, list[str]]] = []
        self.imgs: list[dict[str, str]] = []
        self.anchors: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self._script_buf: list[str] = []
        self._in_script_with_type: str | None = None
        self.jsonld_blocks: list[str] = []
        self.inline_style_blocks = 0
        self.external_stylesheets = 0
        self.forms: list[dict[str, Any]] = []
        self._current_form: dict[str, Any] | None = None
        self.labels: list[dict[str, str]] = []
        self.inputs: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self._in_button = False
        self._button_buf: list[str] = []

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        d = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.html_lang = d.get("lang")
        elif tag == "meta":
            self.metas.append(d)
            if "charset" in d and not self.charset:
                self.charset = d["charset"]
            if d.get("name", "").lower() == "viewport":
                self.viewport = d.get("content", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "link":
            self.links.append(d)
            rel = d.get("rel", "").lower()
            if "stylesheet" in rel:
                self.external_stylesheets += 1
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._heading_stack.append((int(tag[1]), []))
        elif tag == "img":
            self.imgs.append(d)
        elif tag == "a":
            self.anchors.append(d)
        elif tag == "script":
            self.scripts.append(d)
            stype = d.get("type", "").lower()
            if stype == "application/ld+json":
                self._in_script_with_type = "ld+json"
                self._script_buf = []
        elif tag == "style":
            self.inline_style_blocks += 1
        elif tag == "form":
            self._current_form = {"inputs": [], "labels_for": set()}
            self.forms.append(self._current_form)
        elif tag == "label":
            self.labels.append(d)
            if self._current_form is not None and d.get("for"):
                self._current_form["labels_for"].add(d["for"])
        elif tag == "input":
            self.inputs.append(d)
            if self._current_form is not None:
                self._current_form["inputs"].append(d)
        elif tag == "button":
            self.buttons.append(d)
            self._in_button = True
            self._button_buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            self.title = "".join(self._title_buf).strip()
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._heading_stack:
            level, buf = self._heading_stack.pop()
            self.headings.append((level, "".join(buf).strip()))
        elif tag == "script":
            if self._in_script_with_type == "ld+json":
                self.jsonld_blocks.append("".join(self._script_buf))
            self._in_script_with_type = None
            self._script_buf = []
        elif tag == "form":
            self._current_form = None
        elif tag == "button":
            text = "".join(self._button_buf).strip()
            if self.buttons:
                self.buttons[-1]["__text__"] = text
            self._in_button = False
            self._button_buf = []

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_buf.append(data)
        if self._heading_stack:
            self._heading_stack[-1][1].append(data)
        if self._in_script_with_type == "ld+json":
            self._script_buf.append(data)
        if self._in_button:
            self._button_buf.append(data)


def parse_page(p: Path) -> PageParser:
    parser = PageParser()
    try:
        parser.feed(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        # Lenient — record but don't crash
        print(f"[WARN] parse error in {p}: {e}", file=sys.stderr)
    return parser


# ---------------------------------------------------------------------------
# Findings collector
# ---------------------------------------------------------------------------


class Findings:
    def __init__(self) -> None:
        self.issues: list[dict[str, Any]] = []

    def add(self, section: str, severity: str, file: Path | None, msg: str, **extra: Any) -> None:
        rec = {
            "section": section,
            "severity": severity,
            "file": str(file.relative_to(ROOT)) if file else None,
            "message": msg,
        }
        rec.update(extra)
        self.issues.append(rec)

    def by_section_severity(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        for i in self.issues:
            out[i["section"]][i["severity"]] += 1
        return out

    def total_by_severity(self) -> dict[str, int]:
        c: Counter[str] = Counter()
        for i in self.issues:
            c[i["severity"]] += 1
        return dict(c)


# ---------------------------------------------------------------------------
# 1. HTML structural validation
# ---------------------------------------------------------------------------


def check_html_structure(p: Path, doc: PageParser, f: Findings) -> None:
    expected_lang = lang_from_path(p)

    if not doc.has_doctype:
        f.add("html", "P1", p, "Missing <!DOCTYPE html>")

    if not doc.html_lang:
        f.add("html", "P0", p, "Missing <html lang> attribute")
    else:
        base = doc.html_lang.split("-")[0].lower()
        if base not in VALID_LANGS:
            f.add("html", "P0", p, f"<html lang='{doc.html_lang}'> not in {sorted(VALID_LANGS)}")
        elif base != expected_lang:
            f.add(
                "html", "P1", p,
                f"<html lang='{doc.html_lang}'> mismatches expected '{expected_lang}' for path",
            )

    if not doc.charset:
        f.add("html", "P0", p, "Missing <meta charset>")
    if not doc.viewport:
        f.add("html", "P1", p, "Missing <meta name='viewport'>")
    elif "width=device-width" not in doc.viewport:
        f.add("html", "P2", p, f"viewport content unexpected: '{doc.viewport}'")

    if not doc.title:
        f.add("html", "P0", p, "Missing <title>")
    else:
        L = len(doc.title)
        if L < 30 or L > 65:
            f.add("html", "P2", p, f"<title> length {L} (ideal 30-65)")

    desc_meta = next((m for m in doc.metas if m.get("name", "").lower() == "description"), None)
    if not desc_meta or not desc_meta.get("content", "").strip():
        f.add("html", "P1", p, "Missing meta description")
    else:
        L = len(desc_meta["content"].strip())
        if L < 100 or L > 165:
            f.add("html", "P2", p, f"meta description length {L} (ideal 100-165)")

    h1s = [h for h in doc.headings if h[0] == 1]
    if len(h1s) == 0:
        f.add("html", "P0", p, "Missing <h1>")
    elif len(h1s) > 1:
        f.add("html", "P1", p, f"Multiple <h1> ({len(h1s)})")

    # Hierarchy: no skipped levels going down (e.g., H2 → H4)
    prev = 0
    for level, _ in doc.headings:
        if prev and level > prev + 1:
            f.add("html", "P2", p, f"Heading hierarchy skip: H{prev} → H{level}")
            break
        prev = level

    # Img alt
    imgs_no_alt = [i for i in doc.imgs if "alt" not in i]
    imgs_empty_alt = [i for i in doc.imgs if "alt" in i and not i["alt"].strip()]
    if imgs_no_alt:
        f.add(
            "html", "P1", p,
            f"{len(imgs_no_alt)} <img> missing alt attribute",
            sample=[i.get("src", "") for i in imgs_no_alt[:3]],
        )
    if imgs_empty_alt:
        # Empty alt is permissible for decorative images — flag as low.
        f.add(
            "html", "P3", p,
            f"{len(imgs_empty_alt)} <img> with empty alt (verify decorative)",
        )


# ---------------------------------------------------------------------------
# 2. SEO meta validation
# ---------------------------------------------------------------------------


def expected_canonical(p: Path) -> str:
    """Best-effort guess of canonical URL for the file."""
    rel = p.relative_to(PUBLIC).as_posix()
    if rel.endswith("index.html"):
        rel = rel[:-len("index.html")]
    return f"https://papikgroup.com/{rel}"


def check_seo_meta(p: Path, doc: PageParser, f: Findings) -> None:
    # Canonical
    canon = next((l for l in doc.links if l.get("rel", "").lower() == "canonical"), None)
    if not canon or not canon.get("href"):
        f.add("seo", "P1", p, "Missing canonical link")
    else:
        href = canon["href"]
        # Just sanity-check that the canonical mentions the right slug
        slug = p.stem
        if slug not in href and not href.endswith(("/", ".html")):
            f.add("seo", "P2", p, f"Canonical href looks unrelated to path: {href}")

    # Hreflang
    alt_links = [l for l in doc.links if l.get("rel", "").lower() == "alternate"]
    hreflangs = {l.get("hreflang", "").lower(): l.get("href", "") for l in alt_links if l.get("hreflang")}
    needed = {"ca", "es", "en", "x-default"}
    missing = needed - set(hreflangs.keys())
    if missing:
        f.add("seo", "P1", p, f"Missing hreflang entries: {sorted(missing)}")

    # OG tags
    og_props = {m.get("property", "").lower() for m in doc.metas if m.get("property")}
    needed_og = {"og:title", "og:description", "og:url", "og:type", "og:locale"}
    missing_og = needed_og - og_props
    if missing_og:
        f.add("seo", "P2", p, f"Missing OG tags: {sorted(missing_og)}")

    # Twitter card
    tw_names = {m.get("name", "").lower() for m in doc.metas if m.get("name", "").lower().startswith("twitter:")}
    missing_tw = {"twitter:card", "twitter:title"} - tw_names
    if missing_tw:
        f.add("seo", "P2", p, f"Missing Twitter card meta: {sorted(missing_tw)}")

    # Robots noindex check
    robots = next((m for m in doc.metas if m.get("name", "").lower() == "robots"), None)
    if robots:
        content = robots.get("content", "").lower()
        if "noindex" in content:
            f.add("seo", "P0", p, f"Accidental noindex robots meta: '{content}'")


# ---------------------------------------------------------------------------
# 3. JSON-LD validation
# ---------------------------------------------------------------------------


PLACEHOLDER_RE = re.compile(r"\[(XXX|FECHA REAL|FECHA|TODO|PLACEHOLDER)[^\]]*\]", re.I)


def expected_jsonld_types(p: Path) -> set[str]:
    name = p.stem
    rel = p.relative_to(PUBLIC).as_posix()

    # Homepage
    if rel in ("index.html", "es/index.html", "en/index.html"):
        return {"Organization"}
    # Landings
    if "/zones/" in "/" + rel or "/zonas/" in "/" + rel or "/areas/" in "/" + rel:
        return {"LocalBusiness"}
    # Articles
    if name.startswith(("article-",)):
        return {"Article", "NewsArticle"}
    # Service pages
    service_slugs = {
        "construccio", "construccion", "construction",
        "rehabilitacio", "rehabilitacion", "retrofit",
        "patrimonis", "patrimonios", "wealth",
        "promocio", "promocion", "development",
        "comunitats", "comunidades", "communities",
    }
    if name in service_slugs:
        return {"Service"}
    return set()


def check_jsonld(p: Path, doc: PageParser, f: Findings) -> None:
    if not doc.jsonld_blocks:
        f.add("jsonld", "P1", p, "No JSON-LD <script type='application/ld+json'> found")
        return

    parsed_types: list[str] = []
    for idx, raw in enumerate(doc.jsonld_blocks):
        if PLACEHOLDER_RE.search(raw):
            f.add("jsonld", "P0", p, f"Placeholder token in JSON-LD block #{idx + 1}")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            f.add("jsonld", "P0", p, f"JSON-LD block #{idx + 1} parse error: {e.msg} (line {e.lineno})")
            continue

        # Could be list (graph) or single
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            ctx = item.get("@context")
            if ctx and "schema.org" not in (ctx if isinstance(ctx, str) else json.dumps(ctx)):
                f.add("jsonld", "P2", p, f"@context not schema.org: {ctx}")
            t = item.get("@type")
            if isinstance(t, list):
                parsed_types.extend(t)
            elif isinstance(t, str):
                parsed_types.append(t)

    expected = expected_jsonld_types(p)
    if expected and not (expected & set(parsed_types)):
        f.add(
            "jsonld", "P2", p,
            f"Expected one of {sorted(expected)} JSON-LD type, got {parsed_types}",
        )

    # BreadcrumbList recommended on all pages
    if "BreadcrumbList" not in parsed_types:
        f.add("jsonld", "P3", p, "No BreadcrumbList JSON-LD (recommended sitewide)")


# ---------------------------------------------------------------------------
# 4. Hreflang triplet integrity
# ---------------------------------------------------------------------------


def sibling_paths(p: Path) -> dict[str, Path | None]:
    """Best-effort sibling path mapping. Returns {lang: Path or None}."""
    rel = p.relative_to(PUBLIC).as_posix()
    name = p.name

    # Canonical CA → ES → EN slug map (covers our known cases)
    SLUG_MAP = {
        # service pages
        "construccio.html": ("construccion.html", "construction.html"),
        "rehabilitacio.html": ("rehabilitacion.html", "retrofit.html"),
        "patrimonis.html": ("patrimonios.html", "wealth.html"),
        "promocio.html": ("promocion.html", "development.html"),
        "comunitats.html": ("comunidades.html", "communities.html"),
        # legal
        "avis-legal.html": ("aviso-legal.html", None),
        "politica-cookies.html": ("politica-cookies.html", None),
        "politica-privacitat.html": ("politica-privacidad.html", None),
        # other
        "blog.html": ("blog.html", None),
        "index.html": ("index.html", "index.html"),
        "nosaltres.html": ("nosaltres.html", None),
        "pressupost.html": ("pressupost.html", None),
        "usuaris.html": ("usuaris.html", None),
        "dashboard-cliente.html": ("dashboard-cliente.html", None),
        # zones
        "bellaterra.html": ("bellaterra.html", "bellaterra.html"),
        "matadepera.html": ("matadepera.html", "matadepera.html"),
        "sant-cugat.html": ("sant-cugat.html", "sant-cugat-del-valles.html"),
        "sant-quirze.html": ("sant-quirze.html", "sant-quirze-del-valles.html"),
    }

    lang = lang_from_path(p)

    # Compute CA-baseline name
    ca_name = es_name = en_name = None

    if lang == "ca":
        ca_name = name
        if name in SLUG_MAP:
            es_name, en_name = SLUG_MAP[name]
    elif lang == "es":
        # reverse lookup
        for k, (es, en) in SLUG_MAP.items():
            if es == name:
                ca_name, en_name = k, en
                break
    elif lang == "en":
        for k, (es, en) in SLUG_MAP.items():
            if en == name:
                ca_name, es_name = k, es
                break

    result: dict[str, Path | None] = {"ca": None, "es": None, "en": None}
    # Determine whether the file lives in a zones subfolder
    if "zones/" in rel or "zonas/" in rel or "areas/" in rel:
        if ca_name:
            result["ca"] = PUBLIC / "zones" / ca_name
        if es_name:
            result["es"] = PUBLIC / "es" / "zonas" / es_name
        if en_name:
            result["en"] = PUBLIC / "en" / "areas" / en_name
    else:
        if ca_name:
            result["ca"] = PUBLIC / ca_name
        if es_name:
            result["es"] = PUBLIC / "es" / es_name
        if en_name:
            result["en"] = PUBLIC / "en" / en_name

    return result


def check_hreflang_integrity(p: Path, doc: PageParser, f: Findings) -> None:
    sibs = sibling_paths(p)
    for lang in ("ca", "es", "en"):
        sib = sibs.get(lang)
        if sib is None:
            # Not all pages have triplets; skip silently
            continue
        if not sib.exists():
            f.add(
                "hreflang", "P2", p,
                f"Expected {lang} sibling missing: {sib.relative_to(ROOT)}",
            )

    # Verify hreflang URLs in the head resolve to existing files
    alt_links = [l for l in doc.links if l.get("rel", "").lower() == "alternate"]
    for l in alt_links:
        href = l.get("href", "")
        hl = l.get("hreflang", "")
        if not href or hl == "x-default":
            continue
        # Try to map href → file
        m = re.match(r"https?://[^/]+(/.*)$", href)
        path_part = m.group(1) if m else href if href.startswith("/") else None
        if not path_part:
            continue
        candidate = (PUBLIC / path_part.lstrip("/")).resolve()
        if path_part.endswith("/"):
            candidate = candidate / "index.html"
        if not candidate.exists():
            f.add("hreflang", "P2", p, f"hreflang='{hl}' points to non-existent file: {href}")


# ---------------------------------------------------------------------------
# 5. Internal link integrity
# ---------------------------------------------------------------------------


def check_internal_links(p: Path, doc: PageParser, f: Findings, link_stats: dict[str, int]) -> None:
    for a in doc.anchors:
        href = a.get("href", "").strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue
        if href.startswith(("http://", "https://")):
            link_stats["external"] += 1
            continue
        link_stats["internal"] += 1
        # Strip query/fragment
        clean = href.split("#", 1)[0].split("?", 1)[0]
        if not clean:
            continue
        if clean.startswith("/"):
            target = PUBLIC / clean.lstrip("/")
        else:
            target = (p.parent / clean).resolve()
        if clean.endswith("/"):
            target = target / "index.html"
        # Some links may reference assets like img/foo.jpg – allow any existing path
        if not target.exists():
            # Try with .html appended
            alt = Path(str(target) + ".html") if target.suffix == "" else None
            if alt and alt.exists():
                continue
            f.add("links", "P1", p, f"Broken internal link: {href}")


# ---------------------------------------------------------------------------
# 6. Sitemap + robots
# ---------------------------------------------------------------------------


def check_sitemap_robots(f: Findings) -> None:
    sm = PUBLIC / "sitemap.xml"
    rb = PUBLIC / "robots.txt"

    if not sm.exists():
        f.add("sitemap", "P0", sm, "sitemap.xml missing")
    else:
        try:
            tree = ET.parse(sm)
            root = tree.getroot()
        except ET.ParseError as e:
            f.add("sitemap", "P0", sm, f"sitemap.xml is not well-formed XML: {e}")
            root = None

        if root is not None:
            ns = {
                "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
                "x": "http://www.w3.org/1999/xhtml",
            }
            urls = root.findall("sm:url", ns)
            if not urls:
                f.add("sitemap", "P1", sm, "sitemap has no <url> entries")
            # Sample-check 10 URLs
            sample_count = min(10, len(urls))
            missing = 0
            for url_el in urls[:sample_count]:
                loc_el = url_el.find("sm:loc", ns)
                if loc_el is None or not loc_el.text:
                    continue
                m = re.match(r"https?://[^/]+(/.*)$", loc_el.text.strip())
                if not m:
                    continue
                path_part = m.group(1)
                cand = PUBLIC / path_part.lstrip("/")
                if path_part.endswith("/"):
                    cand = cand / "index.html"
                if not cand.exists():
                    missing += 1
                    f.add("sitemap", "P1", sm, f"sitemap loc points to missing file: {loc_el.text.strip()}")
            # hreflang alternates
            has_alt = any(u.find("x:link", ns) is not None for u in urls[:50])
            if not has_alt:
                f.add("sitemap", "P2", sm, "sitemap has no <xhtml:link rel='alternate'> hreflang annotations")

    if not rb.exists():
        f.add("sitemap", "P1", rb, "robots.txt missing")
    else:
        body = rb.read_text(encoding="utf-8", errors="replace")
        if "Sitemap:" not in body and "sitemap:" not in body.lower():
            f.add("sitemap", "P2", rb, "robots.txt does not reference Sitemap")
        if "Disallow: /" in body and "Disallow: /\n" in body:
            # Crude check — full disallow
            f.add("sitemap", "P0", rb, "robots.txt blocks entire site (Disallow: /)")
        if "/wp-admin" not in body:
            f.add("sitemap", "P3", rb, "robots.txt does not explicitly block /wp-admin (recommended)")

    if not VERCEL_JSON.exists() and not VERCEL_JSON_CAND.exists():
        f.add("sitemap", "P0", None, "Neither vercel.json nor vercel.json.candidate present")
    else:
        target = VERCEL_JSON_CAND if VERCEL_JSON_CAND.exists() else VERCEL_JSON
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
            redirects = data.get("redirects", [])
            if not redirects:
                f.add("sitemap", "P2", target, f"{target.name} has no 'redirects' array (expected for legacy URLs)")
            else:
                # quick syntactic check
                for i, r in enumerate(redirects):
                    if "source" not in r or "destination" not in r:
                        f.add("sitemap", "P1", target, f"redirect entry #{i} missing source/destination")
        except json.JSONDecodeError as e:
            f.add("sitemap", "P0", target, f"{target.name} not valid JSON: {e}")


# ---------------------------------------------------------------------------
# 7. Accessibility quick-check
# ---------------------------------------------------------------------------


SKIP_PATTERNS = re.compile(r"(skip[-\s]?to|salta[-\s]?al|saltar[-\s]?al|salta[-\s]?a)", re.I)


def check_accessibility(p: Path, doc: PageParser, f: Findings, html_text: str) -> None:
    # Skip-to-content link in nav
    if not SKIP_PATTERNS.search(html_text[:8000]):
        # Lots of static sites omit this; flag P3
        f.add("a11y", "P3", p, "No skip-to-content link found in early markup")

    # Form labels
    for i, form in enumerate(doc.forms):
        for inp in form.get("inputs", []):
            t = (inp.get("type", "") or "text").lower()
            if t in ("hidden", "submit", "button", "reset"):
                continue
            inp_id = inp.get("id", "")
            has_aria = inp.get("aria-label") or inp.get("aria-labelledby")
            has_label = inp_id and inp_id in form.get("labels_for", set())
            if not has_label and not has_aria:
                f.add(
                    "a11y", "P2", p,
                    f"Form #{i + 1} input '{inp.get('name', '?')}' lacks <label> or aria-label",
                )

    # Buttons accessible name
    for b in doc.buttons:
        text = (b.get("__text__", "") or "").strip()
        aria = (b.get("aria-label", "") or "").strip()
        if not text and not aria:
            f.add("a11y", "P2", p, f"<button> with no accessible text (aria-label missing)")


# ---------------------------------------------------------------------------
# 8. Performance quick-check
# ---------------------------------------------------------------------------


def check_performance(p: Path, doc: PageParser, f: Findings, html_text: str) -> None:
    if doc.inline_style_blocks >= 3:
        f.add(
            "perf", "P3", p,
            f"{doc.inline_style_blocks} inline <style> blocks (consider consolidating to external CSS)",
        )

    # Inline style attributes count (rough)
    inline_attr = html_text.count(" style=\"") + html_text.count(" style='")
    if inline_attr > 50:
        f.add("perf", "P3", p, f"~{inline_attr} inline style='' attributes (consider class-based styling)")

    # Scripts with src and no defer/async
    blocking = []
    for s in doc.scripts:
        if not s.get("src"):
            continue
        if s.get("type", "").lower() == "application/ld+json":
            continue
        if "defer" not in s and "async" not in s:
            blocking.append(s.get("src"))
    if blocking:
        f.add(
            "perf", "P2", p,
            f"{len(blocking)} blocking <script src> without defer/async",
            sample=blocking[:3],
        )

    # PNG that could be webp
    png_imgs = [i.get("src", "") for i in doc.imgs if i.get("src", "").lower().endswith(".png")]
    if len(png_imgs) >= 3:
        f.add(
            "perf", "P3", p,
            f"{len(png_imgs)} <img> reference .png — consider .webp/.avif for hero/listing images",
        )


# ---------------------------------------------------------------------------
# 9. Cross-lang consistency
# ---------------------------------------------------------------------------


def check_cross_lang(parsed: dict[Path, PageParser], f: Findings) -> None:
    """Group by sibling-set and compare H1 / H2-count / paragraph-count."""
    seen_groups: set[tuple[str, ...]] = set()
    for p, doc in parsed.items():
        sibs = sibling_paths(p)
        existing = {lang: s for lang, s in sibs.items() if s and s.exists()}
        if len(existing) < 2:
            continue
        key = tuple(sorted(str(s) for s in existing.values()))
        if key in seen_groups:
            continue
        seen_groups.add(key)

        counts: dict[str, dict[str, int]] = {}
        for lang, s in existing.items():
            d = parsed.get(s)
            if d is None:
                continue
            counts[lang] = {
                "h1": sum(1 for h in d.headings if h[0] == 1),
                "h2": sum(1 for h in d.headings if h[0] == 2),
                "headings_total": len(d.headings),
            }

        if len(counts) < 2:
            continue
        h2s = [c["h2"] for c in counts.values()]
        if h2s and (max(h2s) - min(h2s)) >= 4:
            f.add(
                "crosslang", "P2", p,
                f"H2 count diverges across siblings: {counts}",
            )
        totals = [c["headings_total"] for c in counts.values()]
        if totals and (max(totals) - min(totals)) >= 6:
            f.add(
                "crosslang", "P3", p,
                f"Total heading count diverges across siblings: {counts}",
            )


# ---------------------------------------------------------------------------
# Schemas dir validation (pre-flight)
# ---------------------------------------------------------------------------


def check_schemas_dir(f: Findings) -> None:
    if not SCHEMAS_DIR.exists():
        f.add("jsonld", "P1", SCHEMAS_DIR, "schemas/ directory missing")
        return
    for tpl in SCHEMAS_DIR.glob("*.json"):
        try:
            data = json.loads(tpl.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            f.add("jsonld", "P1", tpl, f"Schema template not valid JSON: {e}")
            continue
        if isinstance(data, dict) and "@context" not in data:
            f.add("jsonld", "P2", tpl, "Schema template missing @context")


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def main() -> int:
    files = iter_in_scope()
    print(f"[QA] In-scope HTML files: {len(files)}")

    f = Findings()
    parsed: dict[Path, PageParser] = {}
    link_stats = {"internal": 0, "external": 0}

    for p in files:
        try:
            html_text = p.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            f.add("io", "P0", p, f"unable to read file: {e}")
            continue
        doc = parse_page(p)
        parsed[p] = doc
        check_html_structure(p, doc, f)
        check_seo_meta(p, doc, f)
        check_jsonld(p, doc, f)
        check_hreflang_integrity(p, doc, f)
        check_internal_links(p, doc, f, link_stats)
        check_accessibility(p, doc, f, html_text)
        check_performance(p, doc, f, html_text)

    check_cross_lang(parsed, f)
    check_sitemap_robots(f)
    check_schemas_dir(f)

    # Output JSON
    out = {
        "summary": {
            "files_scanned": len(files),
            "internal_links_total": link_stats["internal"],
            "external_links_total": link_stats["external"],
            "issues_total": len(f.issues),
            "by_severity": f.total_by_severity(),
            "by_section_severity": {k: dict(v) for k, v in f.by_section_severity().items()},
        },
        "issues": f.issues,
    }
    out_path = SEO_DIR / "qa-findings.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[QA] Findings written to {out_path}")
    print(f"[QA] Total issues: {len(f.issues)} — by severity: {f.total_by_severity()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
