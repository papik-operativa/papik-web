#!/usr/bin/env python3
"""
Schema enrichment pass · Wave 2.

Two fixes, both idempotent:

  ISSUE 1 · 51 LocalBusiness JSON-LD blocks across landing/comarca pages
            are missing a top-level `geo` field.
            Walks /public/zones/, /public/comarques/, plus /es/zonas/,
            /es/comarcas/, /en/areas/, /en/regions/ and inserts a
            GeoCoordinates node into the LocalBusiness using the
            municipality/comarca slug -> lat,lon table below.

  ISSUE 2 · 10 utility pages have zero JSON-LD.
            Adds a BreadcrumbList plus a page-type-appropriate primary
            schema (Service / AboutPage+Organization / WebPage) right
            before </head>. cookie-banner.html is detected as a fragment
            (no <html>) and skipped.

Both fixes are idempotent: re-running the script after a successful run
makes no further changes.

Usage:
    python3 seo-internal/schema-enrichment.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

PUBLIC_DIR = Path("/Users/trisfisas/Desktop/CÓDIGO/papik-web/public")

# ---------------------------------------------------------------------------
# Coordinate registry
# ---------------------------------------------------------------------------
# Slugs as they appear in the file path (Catalan toponym slugs reused across
# every language). The four slug variants for Sant Cugat / Sant Quirze are
# normalised to the canonical Catalan slug.
COORDS: dict[str, tuple[str, str]] = {
    # Tier 1 + Tier 2 municipalities
    "sant-cugat-del-valles": ("41.473", "2.083"),
    "sant-cugat":             ("41.473", "2.083"),
    "sant-quirze-del-valles": ("41.532", "2.082"),
    "sant-quirze":            ("41.532", "2.082"),
    "bellaterra":             ("41.503", "2.099"),
    "matadepera":             ("41.598", "2.027"),
    "argentona":              ("41.555", "2.402"),
    "castellar-del-valles":   ("41.612", "2.087"),
    "sant-andreu-de-llavaneres": ("41.572", "2.486"),
    "sitges":                 ("41.236", "1.811"),
    "vilanova-i-la-geltru":   ("41.224", "1.726"),
    "cabrils":                ("41.527", "2.367"),
    "alella":                 ("41.494", "2.295"),
    "premia-de-dalt":         ("41.515", "2.357"),
    "tiana":                  ("41.480", "2.269"),
    "cerdanyola-del-valles":  ("41.491", "2.140"),
    # Comarcal hubs
    "valles-occidental":      ("41.560", "2.080"),
    "maresme":                ("41.540", "2.450"),
    "garraf":                 ("41.230", "1.800"),
}

LANDING_DIRS = [
    PUBLIC_DIR / "zones",
    PUBLIC_DIR / "es" / "zonas",
    PUBLIC_DIR / "en" / "areas",
    PUBLIC_DIR / "comarques",
    PUBLIC_DIR / "es" / "comarcas",
    PUBLIC_DIR / "en" / "regions",
]

JSON_LD_BLOCK_RE = re.compile(
    r'(<script[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)',
    re.DOTALL | re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def slug_for(path: Path) -> Optional[str]:
    return path.stem  # e.g. "sant-cugat", "valles-occidental"


def _add_geo_to_localbusiness_node(node: dict, lat: str, lon: str) -> bool:
    """Mutate a single dict node in place. Returns True if changed."""
    if not isinstance(node, dict):
        return False
    type_field = node.get("@type")
    types = type_field if isinstance(type_field, list) else [type_field]
    if not any(t in ("LocalBusiness", "GeneralContractor",
                     "HomeAndConstructionBusiness") for t in types if isinstance(t, str)):
        return False
    if "geo" in node and isinstance(node["geo"], dict) and node["geo"].get("@type") == "GeoCoordinates":
        # Already enriched.
        return False
    node["geo"] = {
        "@type": "GeoCoordinates",
        "latitude": lat,
        "longitude": lon,
    }
    return True


def _walk_and_enrich(node, lat: str, lon: str) -> int:
    """Walk arbitrarily nested data and enrich every LocalBusiness node."""
    changes = 0
    if isinstance(node, dict):
        if _add_geo_to_localbusiness_node(node, lat, lon):
            changes += 1
        for v in node.values():
            changes += _walk_and_enrich(v, lat, lon)
    elif isinstance(node, list):
        for item in node:
            changes += _walk_and_enrich(item, lat, lon)
    return changes


def fix_localbusiness_geo(path: Path) -> tuple[bool, int]:
    """Returns (file_modified, nodes_enriched)."""
    slug = slug_for(path)
    if slug not in COORDS:
        return False, 0
    lat, lon = COORDS[slug]
    html = path.read_text(encoding="utf-8")
    new_html = html
    total_enriched = 0

    def _replace(m: re.Match) -> str:
        nonlocal total_enriched
        opening, body, closing = m.group(1), m.group(2), m.group(3)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return m.group(0)
        enriched = _walk_and_enrich(data, lat, lon)
        if enriched == 0:
            return m.group(0)
        total_enriched += enriched
        # Preserve formatting: re-serialise with 2-space indent (matches existing).
        new_body = "\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n  "
        return f"{opening}{new_body}{closing}"

    new_html = JSON_LD_BLOCK_RE.sub(_replace, html)
    if total_enriched == 0:
        return False, 0
    path.write_text(new_html, encoding="utf-8")
    return True, total_enriched


# ---------------------------------------------------------------------------
# Issue 2 · utility pages without any JSON-LD
# ---------------------------------------------------------------------------
ORG_ID = "https://papik.cat/#org"
ORG_NAME = "PAPIK Group"
ORG_LOGO = "https://papik.cat/img/logo/papik-logo.svg"

# Each entry: list of schema dicts, plus lang + breadcrumb config.
def build_breadcrumb(lang: str, page_name: str, page_url: str) -> dict:
    home_label = {"ca": "Inici", "es": "Inicio", "en": "Home"}[lang]
    home_url = {
        "ca": "https://papik.cat/",
        "es": "https://papik.cat/es/",
        "en": "https://papik.cat/en/",
    }[lang]
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": home_label,
                "item": home_url,
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": page_name,
                "item": page_url,
            },
        ],
    }


def build_service_schema(lang: str, page_url: str) -> dict:
    name = {
        "ca": "Configurador de pressupost Passivhaus",
        "es": "Configurador de presupuesto Passivhaus",
        "en": "Passivhaus budget configurator",
    }[lang]
    description = {
        "ca": "Sol·licitud i estimació orientativa de pressupost per a "
              "construcció i rehabilitació Passivhaus.",
        "es": "Solicitud y estimación orientativa de presupuesto para "
              "construcción y rehabilitación Passivhaus.",
        "en": "Request and indicative estimate for Passivhaus construction "
              "and retrofit projects.",
    }[lang]
    return {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": name,
        "description": description,
        "url": page_url,
        "provider": {"@id": ORG_ID, "@type": "Organization", "name": ORG_NAME},
        "areaServed": [
            {"@type": "AdministrativeArea", "name": "Catalunya"},
            {"@type": "AdministrativeArea", "name": "Vallès Occidental"},
            {"@type": "AdministrativeArea", "name": "Maresme"},
            {"@type": "AdministrativeArea", "name": "Garraf"},
        ],
        "serviceType": "Construction budget request",
        "inLanguage": lang,
    }


def build_aboutpage_schema(lang: str, page_url: str) -> dict:
    name = {
        "ca": "Sobre PAPIK Group",
        "es": "Sobre PAPIK Group",
    }[lang]
    description = {
        "ca": "Constructora Passivhaus a Catalunya. 30 anys d'experiència, "
              "sistema propi Eskimohaus®.",
        "es": "Constructora Passivhaus en Cataluña. 30 años de experiencia, "
              "sistema propio Eskimohaus®.",
    }[lang]
    return {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": name,
        "description": description,
        "url": page_url,
        "inLanguage": lang,
        "mainEntity": {
            "@id": ORG_ID,
            "@type": "Organization",
            "name": ORG_NAME,
            "url": "https://papik.cat/",
            "logo": ORG_LOGO,
            "sameAs": [
                "https://www.linkedin.com/company/papik-group",
                "https://www.instagram.com/papikgroup",
            ],
        },
    }


def build_webpage_schema(lang: str, page_url: str, name: str,
                          description: str, noindex: bool = False) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": name,
        "description": description,
        "url": page_url,
        "inLanguage": lang,
        "isPartOf": {"@id": "https://papik.cat/#website"},
    }
    if noindex:
        schema["robots"] = "noindex,follow"
    return schema


# Page registry: file path -> (lang, page_name, page_url, [schemas])
def utility_pages() -> list[dict]:
    out = []

    # pressupost / presupuesto / budget
    out.append({
        "path": PUBLIC_DIR / "pressupost.html",
        "lang": "ca",
        "page_name": "Pressupost",
        "page_url": "https://papik.cat/pressupost",
        "primary": build_service_schema("ca", "https://papik.cat/pressupost"),
    })
    out.append({
        "path": PUBLIC_DIR / "es" / "presupuesto.html",
        "lang": "es",
        "page_name": "Presupuesto",
        "page_url": "https://papik.cat/es/presupuesto",
        "primary": build_service_schema("es", "https://papik.cat/es/presupuesto"),
    })
    out.append({
        "path": PUBLIC_DIR / "en" / "budget.html",
        "lang": "en",
        "page_name": "Budget",
        "page_url": "https://papik.cat/en/budget",
        "primary": build_service_schema("en", "https://papik.cat/en/budget"),
    })

    # nosaltres / nosotros (no EN)
    out.append({
        "path": PUBLIC_DIR / "nosaltres.html",
        "lang": "ca",
        "page_name": "Nosaltres",
        "page_url": "https://papik.cat/nosaltres",
        "primary": build_aboutpage_schema("ca", "https://papik.cat/nosaltres"),
    })
    out.append({
        "path": PUBLIC_DIR / "es" / "nosotros.html",
        "lang": "es",
        "page_name": "Nosotros",
        "page_url": "https://papik.cat/es/nosotros",
        "primary": build_aboutpage_schema("es", "https://papik.cat/es/nosotros"),
    })

    # qualitats (CA only)
    out.append({
        "path": PUBLIC_DIR / "qualitats.html",
        "lang": "ca",
        "page_name": "Qualitats",
        "page_url": "https://papik.cat/qualitats",
        "primary": build_webpage_schema(
            "ca",
            "https://papik.cat/qualitats",
            "Qualitats · PAPIK Group",
            "Estàndards constructius i de qualitat aplicats per PAPIK Group "
            "en projectes Passivhaus.",
        ),
    })

    # usuaris CA + ES (noindex declared in JSON-LD too)
    out.append({
        "path": PUBLIC_DIR / "usuaris.html",
        "lang": "ca",
        "page_name": "Usuaris",
        "page_url": "https://papik.cat/usuaris",
        "primary": build_webpage_schema(
            "ca",
            "https://papik.cat/usuaris",
            "Àrea d'usuaris · PAPIK Group",
            "Accés privat per a clients i col·laboradors de PAPIK Group.",
            noindex=True,
        ),
    })
    out.append({
        "path": PUBLIC_DIR / "es" / "usuaris.html",
        "lang": "es",
        "page_name": "Usuarios",
        "page_url": "https://papik.cat/es/usuaris",
        "primary": build_webpage_schema(
            "es",
            "https://papik.cat/es/usuaris",
            "Área de usuarios · PAPIK Group",
            "Acceso privado para clientes y colaboradores de PAPIK Group.",
            noindex=True,
        ),
    })

    return out


SCHEMA_BLOCK_MARKER = "<!-- schema-enrichment:wave2 -->"


def render_schema_block(breadcrumb: dict, primary: dict) -> str:
    """Render two <script> tags as a single contiguous block, marker-tagged."""
    lines = [SCHEMA_BLOCK_MARKER]
    lines.append('<script type="application/ld+json">')
    lines.append(json.dumps(breadcrumb, indent=2, ensure_ascii=False))
    lines.append("</script>")
    lines.append('<script type="application/ld+json">')
    lines.append(json.dumps(primary, indent=2, ensure_ascii=False))
    lines.append("</script>")
    return "\n".join(lines) + "\n"


def is_fragment(html: str) -> bool:
    """Return True for files that lack <html> / <head> (eg cookie-banner)."""
    head = html[:2048].lower()
    return "<html" not in head and "<head" not in head


def inject_schema_into_utility(entry: dict) -> tuple[bool, str]:
    path: Path = entry["path"]
    if not path.exists():
        return False, f"missing file: {path}"
    html = path.read_text(encoding="utf-8")
    if is_fragment(html):
        return False, f"fragment skipped: {path.name}"
    # Idempotency guard
    if SCHEMA_BLOCK_MARKER in html:
        return False, f"already enriched: {path.name}"

    # Also skip if the page already has any JSON-LD (defensive)
    if JSON_LD_BLOCK_RE.search(html):
        return False, f"already has JSON-LD: {path.name}"

    breadcrumb = build_breadcrumb(entry["lang"], entry["page_name"], entry["page_url"])
    block = render_schema_block(breadcrumb, entry["primary"])

    # Insert just before </head>
    if "</head>" not in html:
        return False, f"no </head> tag: {path.name}"
    new_html = html.replace("</head>", block + "</head>", 1)
    path.write_text(new_html, encoding="utf-8")
    return True, f"enriched: {path.name}"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main() -> int:
    print("=" * 70)
    print("PAPIK Group · schema enrichment · Wave 2")
    print("=" * 70)

    # ---- Issue 1 ----
    issue1_files = []
    for d in LANDING_DIRS:
        if d.exists():
            issue1_files.extend(sorted(d.glob("*.html")))

    issue1_changed = 0
    issue1_nodes = 0
    issue1_skipped = []
    for f in issue1_files:
        slug = slug_for(f)
        if slug not in COORDS:
            issue1_skipped.append(str(f))
            continue
        changed, n = fix_localbusiness_geo(f)
        if changed:
            issue1_changed += 1
            issue1_nodes += n
            print(f"  [geo+] {f.relative_to(PUBLIC_DIR)} -> +{n} node(s)")
        else:
            print(f"  [skip] {f.relative_to(PUBLIC_DIR)} (no LocalBusiness without geo)")

    print()
    print(f"Issue 1 summary: {issue1_changed}/{len(issue1_files)} files modified, "
          f"{issue1_nodes} LocalBusiness node(s) enriched, "
          f"{len(issue1_skipped)} files unmapped.")
    if issue1_skipped:
        for p in issue1_skipped:
            print(f"  [unmapped] {p}")

    # ---- Issue 2 ----
    print()
    issue2_changed = 0
    issue2_total = 0
    for entry in utility_pages():
        issue2_total += 1
        ok, msg = inject_schema_into_utility(entry)
        prefix = "  [schema+]" if ok else "  [skip]   "
        print(f"{prefix} {msg}")
        if ok:
            issue2_changed += 1

    # cookie-banner explicit fragment check
    cb = PUBLIC_DIR / "cookie-banner.html"
    if cb.exists():
        if is_fragment(cb.read_text(encoding="utf-8")):
            print("  [skip]    cookie-banner.html confirmed fragment, no JSON-LD added")

    print()
    print(f"Issue 2 summary: {issue2_changed}/{issue2_total} utility pages enriched.")
    print()
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
