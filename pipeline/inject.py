"""Mode B: inject schema JSON-LD + hreflang into existing HTML files in-place.

Uses BeautifulSoup ONLY for read-only metadata extraction. Mutations are done
with regex-based string operations on the raw HTML so we don't reformat
unrelated parts of the file (preserves indentation, attribute case,
self-closing styles, etc.).

Idempotent: each injection sandwiches its output between marker comments
    <!-- papik-pipeline:begin -->
    ...
    <!-- papik-pipeline:end -->
On re-run, the previous block is removed before fresh content is inserted.
Existing <link rel="alternate" hreflang="..."> tags outside our markers are
also removed so we own the canonical hreflang set.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

from .hreflang import build_hreflang_links
from .lib import Page
from .schemas import PageMeta, build_schemas, serialize


BEGIN_MARK = "<!-- papik-pipeline:begin -->"
END_MARK = "<!-- papik-pipeline:end -->"

# Regex used to strip prior pipeline output (greedy across the marker pair)
_BLOCK_RE = re.compile(
    re.escape(BEGIN_MARK) + r".*?" + re.escape(END_MARK) + r"\n?",
    re.DOTALL,
)
# Match any pre-existing <link rel="alternate" ... hreflang="..." ...> tag,
# regardless of attribute order or quote style.
_HREFLANG_RE = re.compile(
    r'\s*<link\b[^>]*\brel\s*=\s*"alternate"[^>]*\bhreflang\s*=[^>]*>\n?',
    re.IGNORECASE,
)
_HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)
# Detect any pre-existing application/ld+json script (so we don't duplicate
# schemas that were placed there by another build pipeline).
_LDJSON_RE = re.compile(
    r'<script\b[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>',
    re.IGNORECASE,
)


@dataclass
class InjectResult:
    page_id: str
    locale: str
    file: Path
    success: bool
    schemas_added: int
    hreflang_added: int
    skipped_reason: Optional[str] = None
    error: Optional[str] = None
    # Diagnostic: was schema injection skipped because the file already had one?
    schemas_skipped_pre_existing: bool = False


# ---------- Metadata extraction (read-only via BS4) ----------

def _extract_meta(html: str) -> PageMeta:
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    elif soup.title and soup.title.string:
        t = soup.title.string.strip()
        title = re.sub(r"\s*[|·–-]\s*PAPIK.*$", "", t).strip() or t

    description = ""
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        description = md["content"].strip()

    hero = None
    og = soup.find("meta", attrs={"property": "og:image"})
    if og and og.get("content"):
        hero = og["content"].strip()
    if not hero:
        first_img = soup.find("img")
        if first_img and first_img.get("src"):
            src = first_img["src"]
            hero = src if src.startswith("http") else f"https://papik.cat/{src.lstrip('/')}"

    word_count = None
    body = soup.find("article") or soup.find("main") or soup.body
    if body:
        text = body.get_text(" ", strip=True)
        if text:
            word_count = len(text.split())

    return PageMeta(
        title=title,
        description=description,
        hero_image_url=hero,
        word_count=word_count,
    )


# ---------- String-level mutation ----------

def _strip_prior_block(html: str) -> str:
    return _BLOCK_RE.sub("", html)


def _strip_existing_hreflang(html: str) -> tuple[str, int]:
    new_html, n = _HREFLANG_RE.subn("\n", html)
    return new_html, n


def _build_block(hreflang_strings: list[str], schema_strings: list[str]) -> str:
    parts = [BEGIN_MARK]
    for s in hreflang_strings:
        parts.append("  " + s)
    for s in schema_strings:
        parts.append(s)
    parts.append(END_MARK)
    return "\n".join(parts) + "\n"


def _insert_before_head_close(html: str, block: str) -> str:
    """Insert block right before </head>, with the same indentation as </head>."""
    m = _HEAD_CLOSE_RE.search(html)
    if not m:
        raise ValueError("no </head> found")
    # Detect indentation of the line that contains </head>
    line_start = html.rfind("\n", 0, m.start()) + 1
    indent = html[line_start:m.start()]
    indented_lines = []
    for line in block.splitlines():
        indented_lines.append(indent + line if line else "")
    indented = "\n".join(indented_lines) + "\n"
    return html[:line_start] + indented + html[line_start:]


# ---------- Public API ----------

def inject_into_file(
    page: Page,
    locale: str,
    *,
    dry_run: bool = False,
    file_override: Optional[Path] = None,
) -> InjectResult:
    fp = file_override or page.expected_filepath(locale)
    if fp is None:
        return InjectResult(page.id, locale, Path("<none>"), False, 0, 0,
                            skipped_reason="no-url-for-locale")
    if not fp.is_file():
        return InjectResult(page.id, locale, fp, False, 0, 0,
                            skipped_reason="file-not-found")
    if page.is_deferred():
        return InjectResult(page.id, locale, fp, False, 0, 0,
                            skipped_reason="page-deferred")

    try:
        html = fp.read_text(encoding="utf-8")

        meta = _extract_meta(html)
        if not meta.title:
            return InjectResult(page.id, locale, fp, False, 0, 0,
                                error="could-not-extract-title")

        # Cleanup prior pipeline output and stray hreflang tags FIRST
        html = _strip_prior_block(html)
        html, _hreflang_removed = _strip_existing_hreflang(html)

        # Detect schemas that survived after stripping our own block.
        # If the page already has its own schemas (e.g. from another build
        # pipeline), do NOT add ours — that would create duplicates.
        has_pre_existing_schema = bool(_LDJSON_RE.search(html))

        # Build new payload
        hreflang_strings = build_hreflang_links(page)
        if has_pre_existing_schema:
            schema_strings: list[str] = []  # don't touch existing schemas
        else:
            schema_dicts = build_schemas(page, locale, meta)
            schema_strings = serialize(schema_dicts)

        block = _build_block(hreflang_strings, schema_strings)
        new_html = _insert_before_head_close(html, block)

        if not dry_run:
            fp.write_text(new_html, encoding="utf-8")

        return InjectResult(
            page.id, locale, fp, True,
            schemas_added=len(schema_strings),
            hreflang_added=len(hreflang_strings),
            schemas_skipped_pre_existing=has_pre_existing_schema,
        )

    except Exception as e:
        return InjectResult(page.id, locale, fp, False, 0, 0, error=repr(e))
