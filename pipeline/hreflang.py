"""Build hreflang <link> tags for a given Page.

Strategy:
- Emit one <link rel="alternate" hreflang="<locale>"> for each locale where the
  page has a declared URL AND is not deferred.
- Emit hreflang="x-default" pointing to CA (DOMAIN policy: CA is the default).
"""

from __future__ import annotations

from .lib import DOMAIN, LOCALES, Page, language_attr


def build_hreflang_links(page: Page) -> list[str]:
    """Return a list of <link> tags as strings, indented and ready to inject."""
    if page.is_deferred():
        return []

    tags: list[str] = []
    for loc in LOCALES:
        url = page.url(loc)
        if not url:
            continue
        href = DOMAIN + url
        tags.append(
            f'<link rel="alternate" hreflang="{language_attr(loc)}" href="{href}">'
        )

    # x-default → CA (project policy)
    ca_url = page.url("ca")
    if ca_url:
        tags.append(
            f'<link rel="alternate" hreflang="x-default" href="{DOMAIN + ca_url}">'
        )
    return tags


def build_canonical_link(page: Page, locale: str) -> str | None:
    url = page.url(locale)
    if not url:
        return None
    return f'<link rel="canonical" href="{DOMAIN + url}">'
