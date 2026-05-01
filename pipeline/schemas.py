"""Build JSON-LD schema dicts for a Page+locale, filling placeholders from
either the existing HTML (Mode B inject-only) or supplied metadata (Mode A render).

Page type → schema dispatcher (per seo-internal/schemas/README.md matrix):

    homepage          → 01-organization (only; @id: papik.cat/#org)
    service           → 02-service + 06-breadcrumb
    subpage           → 02-service + 06-breadcrumb
    geo-landing       → 03-localbusiness + 06-breadcrumb
    geo-hub           → 03-localbusiness + 06-breadcrumb
    article           → 04-article + 06-breadcrumb
    press-release     → 04-article + 06-breadcrumb
    project           → 07-realestatelisting + 06-breadcrumb
    company           → 06-breadcrumb
    index             → 06-breadcrumb
    tool              → 06-breadcrumb
    authority-hub     → 06-breadcrumb
"""

from __future__ import annotations

import copy
import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from .lib import DOMAIN, Page, SCHEMAS_DIR, language_attr


# ---------- Template loading ----------

@lru_cache(maxsize=None)
def _load_template(filename: str) -> dict:
    raw = json.loads((SCHEMAS_DIR / filename).read_text(encoding="utf-8"))
    return _strip_doc_keys(raw)


def _strip_doc_keys(obj: Any) -> Any:
    """Recursively remove keys that start with `_` (documentation-only)."""
    if isinstance(obj, dict):
        return {k: _strip_doc_keys(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_strip_doc_keys(x) for x in obj]
    return obj


def _fill(obj: Any, replacements: dict[str, str]) -> Any:
    """Substitute {{TOKEN}} placeholders in any string value."""
    if isinstance(obj, dict):
        return {k: _fill(v, replacements) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_fill(x, replacements) for x in obj]
    if isinstance(obj, str):
        out = obj
        for k, v in replacements.items():
            out = out.replace(f"{{{{{k}}}}}", v if v is not None else "")
        return out
    return obj


def _drop_unfilled(obj: Any) -> Any:
    """Recursively remove dict entries whose value is empty or still contains
    an unfilled {{TOKEN}}, and remove additionalProperty entries with empty value."""
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            v2 = _drop_unfilled(v)
            if isinstance(v2, str) and ("{{" in v2 and "}}" in v2):
                continue
            if v2 in (None, "", [], {}):
                continue
            cleaned[k] = v2
        return cleaned
    if isinstance(obj, list):
        out = []
        for x in obj:
            x2 = _drop_unfilled(x)
            if x2 in (None, "", [], {}):
                continue
            out.append(x2)
        return out
    return obj


# ---------- Page-type → schemas dispatcher ----------

PAGE_TYPE_SCHEMAS: dict[str, list[str]] = {
    "homepage":      ["01-organization-homepage.json"],
    "service":       ["02-service.json", "06-breadcrumb.json"],
    "subpage":       ["02-service.json", "06-breadcrumb.json"],
    "geo-landing":   ["03-localbusiness-landing.json", "06-breadcrumb.json"],
    "geo-hub":       ["03-localbusiness-landing.json", "06-breadcrumb.json"],
    "article":       ["04-article.json", "06-breadcrumb.json"],
    "press-release": ["04-article.json", "06-breadcrumb.json"],
    "project":       ["07-realestatelisting-project.json", "06-breadcrumb.json"],
    "company":       ["06-breadcrumb.json"],
    "index":         ["06-breadcrumb.json"],
    "tool":          ["06-breadcrumb.json"],
    "authority-hub": ["06-breadcrumb.json"],
    "legal":         ["06-breadcrumb.json"],
}


# ---------- Breadcrumb resolution ----------

PARENT_NAMES_BY_TYPE: dict[str, dict[str, tuple[str, str]]] = {
    # type → locale → (parent_name, parent_url_path)
    "article": {
        "ca": ("Blog", "/blog"),
        "es": ("Blog", "/es/blog"),
        "en": ("Blog", "/en/blog"),
    },
    "press-release": {
        "ca": ("Premsa", "/premsa"),
        "es": ("Prensa", "/es/prensa"),
        "en": ("Press", "/en/press"),
    },
    "project": {
        "ca": ("Projectes", "/projectes"),
        "es": ("Proyectos", "/es/proyectos"),
        "en": ("Projects", "/en/projects"),
    },
    "geo-landing": {
        "ca": ("Zones", "/zones"),
        "es": ("Zonas", "/es/zonas"),
        "en": ("Areas", "/en/areas"),
    },
    "geo-hub": {
        "ca": ("Comarques", "/comarques"),
        "es": ("Comarcas", "/es/comarcas"),
        "en": ("Regions", "/en/regions"),
    },
    "subpage": {
        "ca": ("Rehabilitació", "/rehabilitacio"),
        "es": ("Rehabilitación", "/es/rehabilitacion"),
        "en": ("Retrofit", "/en/retrofit"),
    },
}

HOME_NAMES = {"ca": "Inici", "es": "Inicio", "en": "Home"}


# ---------- Public API ----------

class PageMeta:
    """Bag of values extracted (Mode B) or supplied (Mode A) for filling schemas."""

    def __init__(
        self,
        title: str,
        description: str = "",
        hero_image_url: Optional[str] = None,
        date_published: Optional[str] = None,
        date_modified: Optional[str] = None,
        word_count: Optional[int] = None,
        location_locality: Optional[str] = None,
        # Project-specific extras (all optional)
        square_meters: Optional[str] = None,
        energy_class: Optional[str] = None,
        passivhaus_level: Optional[str] = None,
        heating_demand: Optional[str] = None,
        airtightness: Optional[str] = None,
    ):
        self.title = title
        self.description = description
        self.hero_image_url = hero_image_url
        self.date_published = date_published
        self.date_modified = date_modified
        self.word_count = word_count
        self.location_locality = location_locality
        self.square_meters = square_meters
        self.energy_class = energy_class
        self.passivhaus_level = passivhaus_level
        self.heating_demand = heating_demand
        self.airtightness = airtightness


def build_schemas(page: Page, locale: str, meta: PageMeta) -> list[dict]:
    """Return a list of cleaned, fully-substituted JSON-LD dicts for the page."""
    schemas: list[dict] = []
    for tpl_name in PAGE_TYPE_SCHEMAS.get(page.type, ["06-breadcrumb.json"]):
        builder = _BUILDERS.get(tpl_name)
        if builder is None:
            continue
        s = builder(page, locale, meta)
        if s:
            schemas.append(s)
    return schemas


# ---------- Per-template builders ----------

def _build_organization(page: Page, locale: str, meta: PageMeta) -> dict:
    tpl = copy.deepcopy(_load_template("01-organization-homepage.json"))
    # Organization template currently has no placeholders; use as-is
    # but ensure @id is canonical.
    tpl.setdefault("@id", f"{DOMAIN}/#org")
    return _drop_unfilled(tpl)


def _build_service(page: Page, locale: str, meta: PageMeta) -> dict:
    tpl = copy.deepcopy(_load_template("02-service.json"))
    url = DOMAIN + (page.url(locale) or "")
    rep = {
        "SERVICE_NAME": meta.title,
        "SERVICE_DESCRIPTION": meta.description or meta.title,
        "SERVICE_URL": url,
        "SERVICE_TYPE": page.id.replace("-", " ").title(),
        "LANGUAGE": language_attr(locale),
    }
    return _drop_unfilled(_fill(tpl, rep))


def _build_localbusiness(page: Page, locale: str, meta: PageMeta) -> dict:
    tpl = copy.deepcopy(_load_template("03-localbusiness-landing.json"))
    url = DOMAIN + (page.url(locale) or "")
    locality = meta.location_locality or _slug_to_locality(page.id)
    rep = {
        "LANDING_NAME": meta.title,
        "LANDING_DESCRIPTION": meta.description or meta.title,
        "LANDING_URL": url,
        "LOCATION_LOCALITY": locality,
        "LOCATION_REGION": "Catalunya",
        "LANGUAGE": language_attr(locale),
    }
    return _drop_unfilled(_fill(tpl, rep))


def _build_article(page: Page, locale: str, meta: PageMeta) -> dict:
    tpl = copy.deepcopy(_load_template("04-article.json"))
    url = DOMAIN + (page.url(locale) or "")
    today = date.today().isoformat()
    rep = {
        "ARTICLE_HEADLINE": meta.title,
        "ARTICLE_DESCRIPTION": meta.description or meta.title,
        "ARTICLE_URL": url,
        "HERO_IMAGE_URL": meta.hero_image_url or f"{DOMAIN}/img/og/default.jpg",
        "DATE_PUBLISHED": meta.date_published or today,
        "DATE_MODIFIED": meta.date_modified or today,
        "ARTICLE_SECTION": "Construcció Passivhaus" if locale == "ca"
                           else ("Construcción Passivhaus" if locale == "es"
                                 else "Passivhaus Construction"),
        "WORD_COUNT": str(meta.word_count) if meta.word_count else "",
        "LANGUAGE": language_attr(locale),
        "AUTHOR_NAME": "PAPIK Group",
        "AUTHOR_URL": DOMAIN,
    }
    return _drop_unfilled(_fill(tpl, rep))


def _build_realestate(page: Page, locale: str, meta: PageMeta) -> dict:
    tpl = copy.deepcopy(_load_template("07-realestatelisting-project.json"))
    url = DOMAIN + (page.url(locale) or "")
    rep = {
        "PROJECT_NAME": meta.title,
        "PROJECT_DESCRIPTION": meta.description or meta.title,
        "PROJECT_URL": url,
        "HERO_IMAGE_URL": meta.hero_image_url or f"{DOMAIN}/img/og/default.jpg",
        "LOCATION_LOCALITY": meta.location_locality or "",
        "YEAR": "",
        "SQUARE_METERS": meta.square_meters or "",
        "ENERGY_CLASS": meta.energy_class or "",
        "PASSIVHAUS_LEVEL": meta.passivhaus_level or "",
        "HEATING_DEMAND": meta.heating_demand or "",
        "AIRTIGHTNESS": meta.airtightness or "",
    }
    s = _drop_unfilled(_fill(tpl, rep))
    # Drop incomplete PropertyValue entries (no `value`)
    if "additionalProperty" in s:
        s["additionalProperty"] = [
            pv for pv in s["additionalProperty"]
            if pv.get("value")
        ]
        if not s["additionalProperty"]:
            del s["additionalProperty"]
    return s


def _build_breadcrumb(page: Page, locale: str, meta: PageMeta) -> dict:
    tpl = copy.deepcopy(_load_template("06-breadcrumb.json"))
    home_url = DOMAIN + ("/" if locale == "ca" else f"/{locale}/")
    items = [
        {"@type": "ListItem", "position": 1, "name": HOME_NAMES[locale], "item": home_url}
    ]
    parent = PARENT_NAMES_BY_TYPE.get(page.type, {}).get(locale)
    pos = 2
    if parent:
        parent_name, parent_path = parent
        items.append({
            "@type": "ListItem",
            "position": pos,
            "name": parent_name,
            "item": DOMAIN + parent_path,
        })
        pos += 1
    items.append({
        "@type": "ListItem",
        "position": pos,
        "name": meta.title,
    })
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


_BUILDERS = {
    "01-organization-homepage.json": _build_organization,
    "02-service.json": _build_service,
    "03-localbusiness-landing.json": _build_localbusiness,
    "04-article.json": _build_article,
    "06-breadcrumb.json": _build_breadcrumb,
    "07-realestatelisting-project.json": _build_realestate,
}


# ---------- Helpers ----------

_SLUG_TO_LOCALITY_OVERRIDES = {
    "zones-sant-cugat": "Sant Cugat del Vallès",
    "zones-sant-quirze": "Sant Quirze del Vallès",
    "zones-bellaterra": "Bellaterra (Cerdanyola del Vallès)",
    "zones-matadepera": "Matadepera",
    "zones-argentona": "Argentona",
    "zones-castellar-del-valles": "Castellar del Vallès",
    "zones-cabrils": "Cabrils",
    "zones-llavaneres": "Sant Andreu de Llavaneres",
    "zones-alella": "Alella",
    "zones-tiana": "Tiana",
    "zones-cerdanyola": "Cerdanyola del Vallès",
    "zones-vilassar-de-mar": "Vilassar de Mar",
    "zones-mataro": "Mataró",
    "zones-premia-de-dalt": "Premià de Dalt",
    "zones-sitges": "Sitges",
    "zones-vilanova-i-la-geltru": "Vilanova i la Geltrú",
    "zones-sant-pere-de-ribes": "Sant Pere de Ribes",
    "zones-valles-occidental": "Vallès Occidental",
    "zones-maresme": "Maresme",
    "zones-garraf": "Garraf",
    "zones-anoia": "Anoia",
    "zones-baix-llobregat": "Baix Llobregat",
    "zones-baix-emporda": "Baix Empordà",
    "zones-osona": "Osona",
}


def _slug_to_locality(page_id: str) -> str:
    if page_id in _SLUG_TO_LOCALITY_OVERRIDES:
        return _SLUG_TO_LOCALITY_OVERRIDES[page_id]
    last = page_id.split("-")[-1]
    return last.replace("_", " ").title()


def serialize(schemas: list[dict]) -> list[str]:
    """Serialize each schema dict as a <script type="application/ld+json"> block."""
    out = []
    for s in schemas:
        body = json.dumps(s, ensure_ascii=False, indent=2)
        out.append(f'<script type="application/ld+json">\n{body}\n</script>')
    return out
