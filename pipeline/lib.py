"""Shared utilities: project paths, slug-mapping loader, page resolution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SEO_INTERNAL = ROOT / "seo-internal"
COPY = SEO_INTERNAL / "copy"
SCHEMAS_DIR = SEO_INTERNAL / "schemas"
SLUG_MAPPING = SEO_INTERNAL / "slug-mapping.json"

DOMAIN = "https://papik.cat"
LOCALES = ("ca", "es", "en")


@dataclass(frozen=True)
class Page:
    """A single entry from slug-mapping.json."""
    id: str
    type: str
    priority: float
    changefreq: str
    urls: dict[str, str | None]   # {"ca": "/...", "es": "/es/...", "en": "/en/..." or None}
    exists_declared: dict[str, object]
    status: str | None = None
    tier: int | None = None
    note: str | None = None
    raw: dict | None = None  # full original entry for type-specific fields

    def url(self, locale: str) -> str | None:
        return self.urls.get(locale)

    def expected_filepath(self, locale: str) -> Path | None:
        url = self.url(locale)
        if not url:
            return None
        return url_to_filepath(url)

    def is_deferred(self) -> bool:
        return self.status == "deferred-post-launch"


def url_to_filepath(url: str) -> Path:
    u = url.strip()
    if not u or u == "/":
        return PUBLIC / "index.html"
    if u.endswith("/"):
        return PUBLIC / u.lstrip("/").rstrip("/") / "index.html"
    return PUBLIC / (u.lstrip("/") + ".html")


@lru_cache(maxsize=1)
def load_slug_mapping() -> dict:
    return json.loads(SLUG_MAPPING.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_pages() -> list[Page]:
    data = load_slug_mapping()
    pages = []
    for entry in data["pages"]:
        pages.append(Page(
            id=entry["id"],
            type=entry.get("type", "?"),
            priority=entry.get("priority", 0.5),
            changefreq=entry.get("changefreq", "monthly"),
            urls={loc: entry.get(loc) for loc in LOCALES},
            exists_declared=entry.get("exists", {}),
            status=entry.get("status"),
            tier=entry.get("tier"),
            note=entry.get("note"),
            raw=entry,
        ))
    return pages


@lru_cache(maxsize=1)
def page_index() -> dict[str, Page]:
    return {p.id: p for p in load_pages()}


def resolve_canonical_url(page: Page, locale: str) -> str | None:
    """Return absolute canonical URL for a (page, locale)."""
    rel = page.url(locale)
    if not rel:
        return None
    return DOMAIN + rel


def language_attr(locale: str) -> str:
    """ISO language tag for hreflang and inLanguage fields."""
    return {"ca": "ca-ES", "es": "es-ES", "en": "en"}[locale]
