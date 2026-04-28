#!/usr/bin/env python3
"""
PAPIK static-site generator (v2 · post-S5 redesign).

Converts the v1.1 wireframe-marker markdown copy in
`seo-internal/copy/{rewrites,translations}` into HTML pages that integrate
with the existing PAPIK design system (`/public/css/`).

The previous generator emitted authoring markers ("BLOC HERO", "[Eyebrow]",
"[CTA primari]") as visible text. This version parses those markers and
produces design-system components: `.hero`, `.btn-accent`, `.card`,
`.list-step`, `.data-table`, `.block-cta`, `<details>`, etc.

Design-system reference: `seo-internal/design-system-reference.md`.

Usage:
    python3 generate_html.py
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent
SRC_CA = ROOT / "seo-internal" / "copy" / "rewrites"
SRC_ES = ROOT / "seo-internal" / "copy" / "translations" / "es"
SRC_EN = ROOT / "seo-internal" / "copy" / "translations" / "en"
SCHEMAS = ROOT / "seo-internal" / "schemas"
OUT_ROOT = ROOT / "public"
OUT_ES = OUT_ROOT / "es"
OUT_EN = OUT_ROOT / "en"

IGNORE_BASENAMES = {
    "fase-3-p2-patches.md",
    "fase-3-p2-patches-v2.md",
    "fase-3-p2-patches-en.md",
    "fase-3-p2-patches-es.md",
    "_test_dir.txt",
}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class PageMeta:
    title: str = ""
    description: str = ""
    canonical: str = ""
    og_image: str = ""
    og_locale: str = ""
    article_section: str = ""
    hreflang: dict = field(default_factory=dict)
    h1: str = ""


@dataclass
class Page:
    src: Path
    out: Path
    lang: str            # "ca" | "es" | "en"
    page_type: str       # "homepage" | "service" | "article" | "landing" | "legal" | "community"
    slug: str
    raw: str
    meta: PageMeta
    body_md: str
    out_depth: int = 1   # 1 for /public/foo.html, 2 for /public/zones/foo.html
    has_faq: bool = False


# ---------------------------------------------------------------------------
# Meta parsing
# ---------------------------------------------------------------------------

META_BLOCK_RE = re.compile(r"```html\s*\n(.*?)\n```", re.DOTALL)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
DESC_RE = re.compile(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', re.IGNORECASE)
CANON_RE = re.compile(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', re.IGNORECASE)
OG_IMAGE_RE = re.compile(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', re.IGNORECASE)
OG_LOCALE_RE = re.compile(r'<meta[^>]+property="og:locale"[^>]+content="([^"]+)"', re.IGNORECASE)
ARTICLE_SECTION_RE = re.compile(r'<meta[^>]+property="article:section"[^>]+content="([^"]+)"', re.IGNORECASE)
HREFLANG_RE = re.compile(r'<link[^>]+rel="alternate"[^>]+hreflang="([^"]+)"[^>]+href="([^"]+)"', re.IGNORECASE)


def parse_meta(raw: str) -> PageMeta:
    meta = PageMeta()
    blocks = META_BLOCK_RE.findall(raw)
    if not blocks:
        return meta
    block = blocks[0]
    if (m := TITLE_RE.search(block)):
        meta.title = m.group(1).strip()
    if (m := DESC_RE.search(block)):
        meta.description = m.group(1).strip()
    if (m := CANON_RE.search(block)):
        meta.canonical = m.group(1).strip()
    if (m := OG_IMAGE_RE.search(block)):
        meta.og_image = m.group(1).strip()
    if (m := OG_LOCALE_RE.search(block)):
        meta.og_locale = m.group(1).strip()
    if (m := ARTICLE_SECTION_RE.search(block)):
        meta.article_section = m.group(1).strip()
    for lang, url in HREFLANG_RE.findall(block):
        meta.hreflang[lang.strip()] = url.strip()
    return meta


# ---------------------------------------------------------------------------
# Source cleaning: strip doc-comments, internal notes, trailing changelogs
# ---------------------------------------------------------------------------

TRAILING_TRIM_MARKERS = (
    "## NOTES OPERATIVES",
    "## NOTAS OPERATIVAS",
    "## OPERATIONAL NOTES",
    "## NOTES PER AL DEV",
    "## NOTAS PARA EL DEV",
    "## NOTES FOR THE DEV",
    "## NOTES PER AL DEV",
    "## NOTES PARA EL DEV",
    "## NOTAS PER AL DEV",
    "## CHECKLIST PRE-PUBLICACIÓ",
    "## CHECKLIST PRE-PUBLICACION",
    "## CHECKLIST PRE-PUBLICATION",
    "## Canvis respecte a v1",
    "## Canvis respecte a la v1",
    "## Cambios respecto a v1",
    "## Cambios respecto a la v1",
    "## Changes from v1",
    "## Word count",
    "## Word Count",
)

INTERNAL_NOTE_RE = re.compile(
    r"^\s*[⚠⚙][^\n]*NOTA[^\n]*\n",
    re.MULTILINE | re.IGNORECASE,
)


def strip_top_doc(raw: str) -> str:
    """Strip leading H1 file-title and `>` doc-comment lines until first content."""
    lines = raw.split("\n")
    out = []
    skip_doc = True
    for ln in lines:
        if skip_doc:
            stripped = ln.strip()
            if stripped.startswith("# ") and not stripped.startswith("## "):
                continue
            if stripped.startswith(">"):
                continue
            if stripped == "":
                continue
            if stripped == "---":
                skip_doc = False
                continue
            skip_doc = False
        out.append(ln)
    return "\n".join(out)


def strip_trailing_blocks(text: str) -> str:
    for marker in TRAILING_TRIM_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    return text


def strip_internal_notes(text: str) -> str:
    return INTERNAL_NOTE_RE.sub("", text)


def first_h1_marker(raw: str) -> str:
    """Find first '[H1]' marker text or '## H1' content."""
    m = re.search(r"\[H1[^\]]*\]\s*\n+([^\n\[]+?)(?:\n|$)", raw)
    if m:
        return m.group(1).strip()
    m = re.search(r"^##\s*H1\s*\n+(.+?)$", raw, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return ""


def detect_faq(raw: str) -> bool:
    return bool(re.search(
        r"\[Accordion\]|##\s*FAQ|## H2\s*·\s*FAQ|##\s*Preguntes|##\s*Preguntas|##\s*Frequently",
        raw, re.IGNORECASE,
    ))


# ---------------------------------------------------------------------------
# Inline markdown helpers
# ---------------------------------------------------------------------------

def md_inline(s: str) -> str:
    """Inline markdown: bold, italic, code, links, escape HTML."""
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


# ---------------------------------------------------------------------------
# Wireframe marker parser
# ---------------------------------------------------------------------------
#
# Each "section block" of source is a fenced code block whose content is a
# sequence of wireframe directives like:
#
#     [Eyebrow]
#     SOME TEXT
#
#     [H1]
#     Title
#
#     [Subhead]
#     One or more lines
#
#     [CTA primari]
#     Configurar el meu pressupost  →
#
# We parse each `[Marker]` followed by 1+ content lines until next `[Marker]`
# or blank line. Most markers map straight to a component template.

MARKER_RE = re.compile(r"^\s*\[([^\]\n]+)\]\s*(.*)$")
ARROW_RE = re.compile(r"\s*[→➔➜>]\s*$")


def normalize_marker(name: str) -> str:
    """Lower, strip, drop annotations after `·`."""
    n = name.strip().lower()
    # cut explanatory annotations after middle-dot
    if "·" in n:
        n = n.split("·", 1)[0].strip()
    if " " in n:
        # 'cta primari' / 'subhead 1 línia' etc.
        n = n.replace(",", " ").strip()
    return n


def parse_marker_block(block_text: str) -> list[dict]:
    """Return list of {marker, lines, annotation} dicts.

    Each entry is one marker with its trailing content lines (until next
    blank-marker boundary or another `[Marker]` line). Lines that aren't
    preceded by any marker become 'paragraph' entries with marker=None.
    """
    entries: list[dict] = []
    current = None
    pending_paragraph: list[str] = []

    def flush_para():
        nonlocal pending_paragraph
        if pending_paragraph:
            entries.append({"marker": None, "annotation": "", "lines": pending_paragraph[:]})
            pending_paragraph = []

    def flush_current():
        nonlocal current
        if current is not None:
            entries.append(current)
            current = None

    for raw_line in block_text.split("\n"):
        line = raw_line.rstrip()
        if line.strip() == "":
            # blank line: flush current marker entry; paragraphs accumulate as one block
            flush_current()
            flush_para()
            continue
        m = MARKER_RE.match(line)
        if m:
            flush_current()
            flush_para()
            raw_name = m.group(1)
            inline_after = m.group(2).strip()
            mname = normalize_marker(raw_name)
            current = {
                "marker": mname,
                "annotation": raw_name.strip(),
                "lines": [inline_after] if inline_after else [],
            }
            continue
        if current is not None:
            current["lines"].append(line)
        else:
            pending_paragraph.append(line)
    flush_current()
    flush_para()
    return entries


# ---------------------------------------------------------------------------
# Component renderers (marker entries -> HTML fragments)
# ---------------------------------------------------------------------------

def _join_lines(lines: list[str]) -> str:
    return " ".join(l.strip() for l in lines if l.strip())


def _strip_arrow(text: str) -> str:
    return ARROW_RE.sub("", text).strip()


def render_hero_from_entries(entries: list[dict], lang: str, page_type: str) -> str:
    """Build a `<section class="hero hero--dark">` block from a hero marker block."""
    eyebrow = ""
    h1 = ""
    subhead_parts: list[str] = []
    primary_cta = None
    secondary_cta = None
    microtrust = ""

    for e in entries:
        m = e["marker"]
        text = _join_lines(e["lines"])
        if not text:
            continue
        if m is None:
            # a free paragraph in the hero — treat as additional subhead
            subhead_parts.append(text)
        elif m.startswith("eyebrow"):
            eyebrow = text
        elif m == "h1" or m.startswith("h1"):
            h1 = text
        elif m == "h2" or m.startswith("h2"):
            # rare in hero; treat as subtitle
            subhead_parts.append(text)
        elif m.startswith("subhead") or m.startswith("subtitle") or m.startswith("subtítol"):
            # split multi-line subheads on internal newlines as separate parts
            subhead_parts.append(text)
        elif m.startswith("cta primari") or m.startswith("cta primary") or m.startswith("cta principal"):
            primary_cta = _strip_arrow(text)
        elif m.startswith("cta secund") or m.startswith("cta secondary"):
            secondary_cta = _strip_arrow(text)
        elif m.startswith("microtrust") or m.startswith("micro-trust") or m.startswith("microtext"):
            microtrust = text

    parts = ['<section class="hero hero--dark">', '  <div class="container">']
    if eyebrow:
        parts.append(f'    <span class="hero__eyebrow">{md_inline(eyebrow)}</span>')
    if h1:
        parts.append(f'    <h1 class="hero__title">{md_inline(h1)}</h1>')
    if subhead_parts:
        parts.append(f'    <p class="hero__subtitle">{md_inline(" ".join(subhead_parts))}</p>')
    if primary_cta or secondary_cta:
        parts.append('    <div class="hero__actions">')
        if primary_cta:
            parts.append(f'      <a class="btn-white" href="#contacte">{md_inline(primary_cta)} <span aria-hidden="true">→</span></a>')
        if secondary_cta:
            parts.append(f'      <a class="btn-outline" href="#main">{md_inline(secondary_cta)} <span aria-hidden="true">→</span></a>')
        parts.append('    </div>')
    if microtrust:
        parts.append(f'    <p class="hero__microtrust">{md_inline(microtrust)}</p>')
    parts.append('  </div>')
    parts.append('</section>')
    return "\n".join(parts)


def render_section_from_entries(entries: list[dict], section_title: str, alt: bool) -> str:
    """Render a generic body section from a marker block.

    Section header (eyebrow/h2/subhead) -> `.section-header`.
    Subsequent entries -> paragraphs, lists, or component blocks.
    The presence of [Card] / [Diagrama vertical] / [Tabla] / [Accordion] /
    [Banner destacat] / [Form] / [Cross-links] / [Frase de tancament] hints
    the appropriate component.
    """
    parts: list[str] = []
    sec_class = "section section--light" if alt else "section"
    parts.append(f'<section class="{sec_class}">')
    parts.append('  <div class="container">')

    # Section header from leading eyebrow + h2 + subhead
    eyebrow = ""
    h2 = ""
    subhead_parts: list[str] = []
    body_entries: list[dict] = []
    consumed_header = False

    for e in entries:
        m = e["marker"]
        text = _join_lines(e["lines"])
        if not consumed_header:
            if m and (m.startswith("eyebrow")):
                eyebrow = text
                continue
            if m and (m == "h2" or m.startswith("h2")):
                h2 = text
                continue
            if m and (m.startswith("subhead") or m.startswith("subtitle") or m.startswith("subtítol")):
                subhead_parts.append(text)
                continue
            consumed_header = True
        body_entries.append(e)

    # Use BLOC heading as h2 fallback
    if not h2 and section_title:
        h2 = section_title

    if eyebrow or h2 or subhead_parts:
        parts.append('    <header class="section-header">')
        if eyebrow:
            parts.append(f'      <span class="section-header__eyebrow">{md_inline(eyebrow)}</span>')
        if h2:
            parts.append(f'      <h2 class="section-header__title">{md_inline(h2)}</h2>')
        if subhead_parts:
            parts.append(f'      <p class="section-header__lead">{md_inline(" ".join(subhead_parts))}</p>')
        parts.append('    </header>')

    parts.append('    <div class="section-body">')

    # Render body entries with a small state machine for tables/forms/accordions
    i = 0
    while i < len(body_entries):
        e = body_entries[i]
        m = e["marker"]
        text = _join_lines(e["lines"])

        if m is None:
            if text:
                parts.append(f'      <p>{md_inline(text)}</p>')
            i += 1
            continue
        if m.startswith("h3"):
            parts.append(f'      <h3>{md_inline(text)}</h3>')
            i += 1
            continue
        if m.startswith("h4"):
            parts.append(f'      <h4>{md_inline(text)}</h4>')
            i += 1
            continue
        if m.startswith("subhead") or m.startswith("subtitle") or m.startswith("subtítol"):
            parts.append(f'      <p class="section-body__lead">{md_inline(text)}</p>')
            i += 1
            continue
        if m.startswith("cta primari") or m.startswith("cta primary") or m.startswith("cta principal"):
            parts.append(f'      <a class="btn-accent" href="#contacte">{md_inline(_strip_arrow(text))} <span aria-hidden="true">→</span></a>')
            i += 1
            continue
        if m.startswith("cta secund") or m.startswith("cta secondary") or m.startswith("cta") or m == "link" or m.startswith("link "):
            parts.append(f'      <a class="link-arrow" href="#">{md_inline(_strip_arrow(text))} <span aria-hidden="true">→</span></a>')
            i += 1
            continue
        if m.startswith("botó") or m.startswith("boton") or m.startswith("button"):
            parts.append(f'      <button class="btn-accent" type="button">{md_inline(_strip_arrow(text))}</button>')
            i += 1
            continue
        if m.startswith("frase de tancament") or m.startswith("frase final") or m.startswith("closing"):
            parts.append(f'      <p class="closing-sentence">{md_inline(text)}</p>')
            i += 1
            continue
        if m.startswith("microtext") or m.startswith("microcopy"):
            parts.append(f'      <p class="microtext">{md_inline(text)}</p>')
            i += 1
            continue
        if m.startswith("paràgraf") or m.startswith("parrafo") or m.startswith("paragraph") or m.startswith("texto") or m.startswith("text") or m.startswith("descripció") or m.startswith("descripcion") or m.startswith("description"):
            parts.append(f'      <p>{md_inline(text)}</p>')
            i += 1
            continue
        # Generic marker we don't know -> if it has text, emit as a paragraph (skip pure layout cues)
        layout_only = (
            m.startswith("grid") or m.startswith("línia") or m.startswith("linea")
            or m.startswith("separador") or m.startswith("strip") or m.startswith("layout")
            or m.startswith("nom unitat") or m.startswith("foto") or m.startswith("imagen")
            or m.startswith("image") or m.startswith("visual") or m.startswith("microtrust")
            or m.startswith("mapa") or m.startswith("camp") or m.startswith("selector")
            or m.startswith("checkbox") or m.startswith("input") or m.startswith("form")
            or m.startswith("card") or m.startswith("tabla") or m.startswith("table")
            or m.startswith("accordion") or m.startswith("acord") or m.startswith("diagrama")
            or m.startswith("phase") or m.startswith("fase") or m.startswith("banner")
            or m.startswith("bloc destacat") or m.startswith("block") or m.startswith("badge")
            or m.startswith("tag") or m.startswith("pill") or m.startswith("eyebrow")
            or m.startswith("h1") or m.startswith("h2") or m.startswith("microtext")
            or m.startswith("note") or m.startswith("nota") or m.startswith("kpi")
            or m.startswith("stat") or m.startswith("number") or m.startswith("number")
            or m.startswith("logo") or m.startswith("slot") or m.startswith("spec")
            or m.startswith("cross-link") or m.startswith("cross") or m.startswith("microtrust strip")
            or m.startswith("llistat") or m.startswith("listado") or m.startswith("list")
        )
        if not layout_only and text:
            parts.append(f'      <p>{md_inline(text)}</p>')
        i += 1

    parts.append('    </div>')
    parts.append('  </div>')
    parts.append('</section>')
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# ASCII pipe-table -> <table class="data-table">
# ---------------------------------------------------------------------------

def render_pipe_table(rows: list[str]) -> str:
    out = ['<table class="data-table">']
    body_started = False
    for i, r in enumerate(rows):
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if all(re.fullmatch(r"-+|:-+|-+:|:-+:", c) for c in cells if c):
            continue
        tag = "th" if i == 0 else "td"
        if tag == "td" and not body_started:
            out.append("<tbody>")
            body_started = True
        if tag == "th":
            out.append("<thead><tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in cells) + "</tr></thead>")
        else:
            out.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in cells) + "</tr>")
    if body_started:
        out.append("</tbody>")
    out.append("</table>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Top-level body parser
# ---------------------------------------------------------------------------
#
# Walks the cleaned body and emits HTML sections.
#
# Recognised structures:
#   * `## BLOC HERO` followed by ``` ... ``` -> hero
#   * `## BLOC N · TITLE` followed by ``` ... ``` -> section header + body section
#   * `### Card N · ...` followed by ``` ... ``` -> card item (collected into card-grid for the current BLOC)
#   * Standalone ``` ... ``` after a section -> append to that section's body
#   * ASCII pipe tables (``` followed by `|...|`) -> data-table
#   * Native markdown sections: paragraphs, headings, lists, blockquotes
#
# Anything wrapped in a code fence is parsed as wireframe markers via
# parse_marker_block(). Anything outside fences is treated as plain markdown.

BLOC_HERO_RE = re.compile(r"^##\s*(?:BLOC\s*)?HERO\s*$", re.IGNORECASE | re.MULTILINE)
BLOC_HEADING_RE = re.compile(r"^##\s*BLOC\s*(\d+)\s*[·\-:]?\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
BLOC_FOOTER_RE = re.compile(r"^##\s*FOOTER\s*$", re.IGNORECASE | re.MULTILINE)


def split_into_sections(body: str) -> list[dict]:
    """Split body into ordered list of sections: hero, blocs, free md.

    Returns list of {kind: 'hero'|'bloc'|'free', title: str, content_lines: list[str]}.
    """
    lines = body.split("\n")
    sections: list[dict] = []
    current = {"kind": "free", "title": "", "content_lines": []}

    for ln in lines:
        # Section dividers
        if re.match(r"^\s*---\s*$", ln):
            if current["content_lines"]:
                sections.append(current)
                current = {"kind": "free", "title": "", "content_lines": []}
            continue
        if BLOC_HERO_RE.match(ln):
            if current["content_lines"]:
                sections.append(current)
            current = {"kind": "hero", "title": "", "content_lines": []}
            continue
        m = BLOC_HEADING_RE.match(ln)
        if m:
            if current["content_lines"]:
                sections.append(current)
            current = {"kind": "bloc", "title": m.group(2).strip(), "number": m.group(1), "content_lines": []}
            continue
        if BLOC_FOOTER_RE.match(ln):
            # Stop: footer is generated by template
            if current["content_lines"]:
                sections.append(current)
            current = {"kind": "skip", "title": "", "content_lines": []}
            continue
        # Strip "## H1" / "## BYLINE" / "## META TAGS" headings entirely
        if re.match(r"^##\s*(H1|BYLINE|META TAGS|HEAD|HEADER)\b", ln, re.IGNORECASE):
            if current["content_lines"]:
                sections.append(current)
            current = {"kind": "skip", "title": "", "content_lines": []}
            continue
        current["content_lines"].append(ln)

    if current["content_lines"]:
        sections.append(current)

    # Drop skipped sections
    return [s for s in sections if s["kind"] != "skip"]


def collect_fenced_blocks(content_lines: list[str]) -> list[dict]:
    """Within a section's content lines, return ordered list of:
        {kind: 'fence', text: str}
        {kind: 'card', heading: str, text: str}
        {kind: 'md', text: str}     (free markdown, paragraphs/lists/etc.)
    """
    blocks: list[dict] = []
    i = 0
    n = len(content_lines)
    md_buffer: list[str] = []

    def flush_md():
        nonlocal md_buffer
        if any(l.strip() for l in md_buffer):
            blocks.append({"kind": "md", "text": "\n".join(md_buffer).strip()})
        md_buffer = []

    while i < n:
        ln = content_lines[i]
        # H3 card heading
        h3 = re.match(r"^###\s*(?:Card\s*[A-Z0-9]*\s*[·\-:]?\s*|Columna\s*\d+\s*[·\-:]?\s*|Card\s+\d+\s*[·\-:]?\s*)?(.+?)\s*$", ln)
        if ln.strip().startswith("### "):
            flush_md()
            heading_text = re.sub(r"^###\s*", "", ln).strip()
            heading_text = re.sub(r"^(?:Card\s*[A-Z0-9]*\s*[·\-:]?\s*|Columna\s*\d+\s*[·\-:]?\s*|Card\s+\d+\s*[·\-:]?\s*)", "", heading_text, flags=re.IGNORECASE).strip()
            # Look ahead for an immediate fenced block
            j = i + 1
            while j < n and content_lines[j].strip() == "":
                j += 1
            if j < n and content_lines[j].strip().startswith("```") and not content_lines[j].strip().startswith("```html"):
                fence = content_lines[j].strip()
                k = j + 1
                fence_lines: list[str] = []
                while k < n and not content_lines[k].strip().startswith("```"):
                    fence_lines.append(content_lines[k])
                    k += 1
                blocks.append({"kind": "card", "heading": heading_text, "text": "\n".join(fence_lines)})
                i = k + 1
                continue
            else:
                # H3 without fence -> treat as md heading
                md_buffer.append(ln)
                i += 1
                continue
        if ln.strip().startswith("```"):
            flush_md()
            lang_tag = ln.strip()[3:].strip()
            j = i + 1
            fence_lines: list[str] = []
            while j < n and not content_lines[j].strip().startswith("```"):
                fence_lines.append(content_lines[j])
                j += 1
            if lang_tag.lower() == "html":
                # Skip the meta-tags HTML block (already extracted)
                i = j + 1
                continue
            text = "\n".join(fence_lines)
            blocks.append({"kind": "fence", "text": text})
            i = j + 1
            continue
        md_buffer.append(ln)
        i += 1
    flush_md()
    return blocks


# ---------------------------------------------------------------------------
# Free markdown -> HTML (paragraphs, lists, headings, tables, blockquotes)
# ---------------------------------------------------------------------------

def md_to_html(md: str) -> str:
    if not md.strip():
        return ""
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    in_para: list[str] = []

    def flush_para():
        nonlocal in_para
        if in_para:
            text = " ".join(l.strip() for l in in_para).strip()
            if text:
                out.append(f"<p>{md_inline(text)}</p>")
            in_para = []

    while i < len(lines):
        ln = lines[i]
        stripped = ln.strip()
        if stripped == "":
            flush_para()
            i += 1
            continue
        if stripped.startswith("## "):
            flush_para()
            txt = stripped[3:].strip()
            txt = re.sub(r"^H2\s*[·\-:]?\s*\d*\.?\s*", "", txt, flags=re.IGNORECASE)
            if txt:
                out.append(f"<h2>{md_inline(txt)}</h2>")
            i += 1
            continue
        if stripped.startswith("### "):
            flush_para()
            txt = stripped[4:].strip()
            txt = re.sub(r"^H3\s*[·\-:]?\s*", "", txt, flags=re.IGNORECASE)
            if txt:
                out.append(f"<h3>{md_inline(txt)}</h3>")
            i += 1
            continue
        if stripped.startswith("#### "):
            flush_para()
            txt = stripped[5:].strip()
            if txt:
                out.append(f"<h4>{md_inline(txt)}</h4>")
            i += 1
            continue
        if stripped == "---":
            flush_para()
            out.append('<hr class="rule">')
            i += 1
            continue
        if "|" in ln and ln.strip().startswith("|"):
            flush_para()
            block = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(render_pipe_table(block))
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>")
            for it in items:
                out.append(f"<li>{md_inline(it)}</li>")
            out.append("</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            out.append("<ol>")
            for it in items:
                out.append(f"<li>{md_inline(it)}</li>")
            out.append("</ol>")
            continue
        if stripped.startswith("> "):
            flush_para()
            quotes = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quotes.append(lines[i].strip()[2:])
                i += 1
            out.append("<blockquote><p>" + md_inline(" ".join(quotes)) + "</p></blockquote>")
            continue
        # Drop bracketed wireframe phrases left in free md
        if re.match(r"^\s*\[[^\]]+\]\s*$", ln):
            i += 1
            continue
        if stripped.startswith("**Visual:**") or stripped.lower().startswith("visual:"):
            i += 1
            continue
        in_para.append(ln)
        i += 1
    flush_para()
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Special block detectors inside a fenced wireframe block
# ---------------------------------------------------------------------------

PHASE_LINE_RE = re.compile(r"^\s*(\d{1,2})\.\s+(.+?)\s*$")
PHASE_NUM_HEAD_RE = re.compile(r"^\s*(\d{2})\s+[·\-:—]\s+(.+)$")


def detect_phases(text: str) -> list[tuple[str, str, str]]:
    """Detect a vertical-diagram phase listing (01 · TITLE / description).
    Returns list of (num, title, body) or empty if not detected.
    """
    out = []
    paras = re.split(r"\n\s*\n", text.strip())
    for p in paras:
        first = p.strip().split("\n", 1)
        head = first[0]
        body = first[1].strip() if len(first) > 1 else ""
        m = PHASE_NUM_HEAD_RE.match(head) or re.match(r"^\s*(\d{2})\s+(.+)$", head)
        if m:
            num, title = m.group(1), m.group(2)
            out.append((num, title.strip(), body))
        elif PHASE_LINE_RE.match(head):
            mm = PHASE_LINE_RE.match(head)
            num, title = mm.group(1).zfill(2), mm.group(2)
            out.append((num, title.strip(), body))
        else:
            return []  # not a phase block
    return out if len(out) >= 2 else []


def detect_pipe_table(text: str) -> list[str]:
    """Return list of pipe-table rows if text looks like one, else []."""
    rows = [l for l in text.split("\n") if l.strip().startswith("|")]
    return rows if len(rows) >= 2 else []


def detect_accordion(text: str) -> list[tuple[str, str]]:
    """Detect P/R accordion pairs. Returns list of (q, a)."""
    pairs: list[tuple[str, str]] = []
    # Pattern: "P · question" / "R · answer"
    chunks = re.split(r"(?=^\s*P\s*[·\-:]\s+)", text, flags=re.MULTILINE)
    for ch in chunks:
        ch = ch.strip()
        if not ch:
            continue
        mq = re.match(r"^P\s*[·\-:]\s+(.+?)(?:\n\s*R\s*[·\-:]\s+(.+))?$", ch, re.DOTALL)
        if mq:
            q = mq.group(1).strip().split("\n", 1)[0].strip()
            rest = ch.split("\n", 1)[1] if "\n" in ch else ""
            ra = re.search(r"R\s*[·\-:]\s+(.+)", rest, re.DOTALL)
            a = ra.group(1).strip() if ra else ""
            pairs.append((q, a))
    return pairs


# ---------------------------------------------------------------------------
# Render a single fenced block based on its content shape
# ---------------------------------------------------------------------------

def render_fence(text: str, current_section_kind: str = "bloc") -> str:
    """Decide what HTML the fenced block should produce."""
    # Empty?
    if not text.strip():
        return ""

    # Pipe table?
    rows = detect_pipe_table(text)
    if rows:
        return render_pipe_table(rows)

    # Phase / vertical diagram?
    phases = detect_phases(text)
    if phases:
        out = ['<ol class="phase-list">']
        for num, title, body in phases:
            out.append(
                f'  <li class="phase-list__item">\n'
                f'    <span class="phase-list__num">{html.escape(num)}</span>\n'
                f'    <div class="phase-list__body">\n'
                f'      <h3 class="phase-list__title">{md_inline(title)}</h3>\n'
                + (f'      <p class="phase-list__text">{md_inline(body)}</p>\n' if body else "")
                + '    </div>\n'
                f'  </li>'
            )
        out.append('</ol>')
        return "\n".join(out)

    # Accordion?
    if "[Accordion]" in text or re.search(r"^\s*P\s*[·\-:]\s+", text, re.MULTILINE):
        # Strip [Accordion] marker
        body_text = re.sub(r"^\s*\[Accordion[^\]]*\]\s*\n", "", text, flags=re.MULTILINE)
        pairs = detect_accordion(body_text)
        if pairs:
            out = ['<div class="faq-list">']
            for q, a in pairs:
                out.append(f'  <details class="faq-item"><summary>{md_inline(q)}</summary><div class="faq-item__body"><p>{md_inline(a)}</p></div></details>')
            out.append('</div>')
            return "\n".join(out)

    # Banner / banner destacat?
    if re.search(r"^\s*\[(?:Banner destacat|Bloc destacat|Banner CTA)[^\]]*\]", text, re.MULTILINE | re.IGNORECASE):
        entries = parse_marker_block(text)
        h2 = ""
        sub = ""
        cta = ""
        eyebrow = ""
        for e in entries:
            mname = e["marker"] or ""
            t = _join_lines(e["lines"])
            if mname.startswith("eyebrow"):
                eyebrow = t
            elif mname.startswith("h2") or mname.startswith("h3"):
                h2 = t
            elif mname.startswith("subhead") or mname.startswith("frase"):
                sub = t
            elif mname.startswith("cta"):
                cta = _strip_arrow(t)
            elif mname is None and not h2:
                h2 = t
        out = ['<section class="block-cta">', '  <div class="container">']
        if eyebrow:
            out.append(f'    <p class="block-cta__label">{md_inline(eyebrow)}</p>')
        if h2:
            out.append(f'    <h2 class="block-cta__title">{md_inline(h2)}</h2>')
        if sub:
            out.append(f'    <p class="block-cta__sub">{md_inline(sub)}</p>')
        if cta:
            out.append(f'    <a class="btn-white" href="#contacte">{md_inline(cta)} <span aria-hidden="true">→</span></a>')
        out.append('  </div>')
        out.append('</section>')
        return "\n".join(out)

    # Cross-links?
    if re.search(r"^\s*\[Cross-?links?[^\]]*\]", text, re.MULTILINE | re.IGNORECASE):
        entries = parse_marker_block(text)
        link_lines: list[str] = []
        for e in entries:
            if e["marker"] is None and e["lines"]:
                for l in e["lines"]:
                    s = l.strip()
                    if not s:
                        continue
                    # Strip leading bullets
                    s = re.sub(r"^[-*•]\s*", "", s)
                    s = _strip_arrow(s)
                    if s:
                        link_lines.append(s)
        if link_lines:
            out = ['<nav class="cross-links">', '  <ul>']
            for s in link_lines:
                out.append(f'    <li><a class="link-arrow" href="#">{md_inline(s)} <span aria-hidden="true">→</span></a></li>')
            out.append('  </ul>')
            out.append('</nav>')
            return "\n".join(out)

    # Form?
    if re.search(r"^\s*\[Form[^\]]*\]", text, re.MULTILINE | re.IGNORECASE):
        entries = parse_marker_block(text)
        fields: list[str] = []
        button_label = "Enviar"
        for e in entries:
            mname = e["marker"] or ""
            t = _join_lines(e["lines"])
            if mname.startswith("camp") or mname.startswith("campo") or mname.startswith("input") or mname.startswith("field"):
                # parse "[Camp · X]" annotation
                ann = e["annotation"]
                fld = re.sub(r"^\[?[Cc]amp\s*[·\-:]?\s*", "", ann)
                fld = fld.strip(" ]")
                input_type = "email" if "email" in fld.lower() else ("tel" if "tel" in fld.lower() else "text")
                fields.append(f'<label class="form-field"><span class="form-field__label">{md_inline(fld or t)}</span><input class="form-field__input" type="{input_type}" required></label>')
            elif mname.startswith("selector") or mname.startswith("select"):
                ann = e["annotation"]
                lbl = re.sub(r"^\[?[Ss]elector\s*[·\-:]?\s*", "", ann).strip(" ]")
                fields.append(f'<label class="form-field"><span class="form-field__label">{md_inline(lbl or t)}</span><select class="form-field__input"><option>—</option></select></label>')
            elif mname.startswith("checkbox"):
                ann = e["annotation"]
                lbl = re.sub(r"^\[?[Cc]heckbox\s*[·\-:]?\s*", "", ann).strip(" ]")
                fields.append(f'<label class="form-field form-field--check"><input type="checkbox" required><span>{md_inline(lbl or t)}</span></label>')
            elif mname.startswith("botó") or mname.startswith("boton") or mname.startswith("button"):
                button_label = _strip_arrow(t) or e["annotation"].split("·", 1)[-1].strip(" []") or "Enviar"
        out = ['<form class="form" action="#" method="post" novalidate>']
        out.extend("  " + f for f in fields)
        out.append(f'  <button class="btn-accent" type="submit">{md_inline(button_label)}</button>')
        out.append('</form>')
        return "\n".join(out)

    # Generic marker block — flatten markers into reasonable HTML
    entries = parse_marker_block(text)
    out_html: list[str] = []
    for e in entries:
        m = e["marker"]
        t = _join_lines(e["lines"])
        if not t:
            continue
        if m is None:
            out_html.append(f'<p>{md_inline(t)}</p>')
        elif m.startswith("eyebrow"):
            out_html.append(f'<span class="eyebrow">{md_inline(t)}</span>')
        elif m.startswith("h1") or m == "h1":
            out_html.append(f'<h2 class="hero__title">{md_inline(t)}</h2>')
        elif m.startswith("h2") or m == "h2":
            out_html.append(f'<h2>{md_inline(t)}</h2>')
        elif m.startswith("h3") or m == "h3":
            out_html.append(f'<h3>{md_inline(t)}</h3>')
        elif m.startswith("h4") or m == "h4":
            out_html.append(f'<h4>{md_inline(t)}</h4>')
        elif m.startswith("subhead") or m.startswith("subtitle") or m.startswith("subtítol"):
            out_html.append(f'<p class="lead">{md_inline(t)}</p>')
        elif m.startswith("cta primari") or m.startswith("cta primary") or m.startswith("cta principal"):
            out_html.append(f'<a class="btn-accent" href="#contacte">{md_inline(_strip_arrow(t))} <span aria-hidden="true">→</span></a>')
        elif m.startswith("cta secund") or m.startswith("cta secondary"):
            out_html.append(f'<a class="btn-outline" href="#main">{md_inline(_strip_arrow(t))} <span aria-hidden="true">→</span></a>')
        elif m == "cta" or m.startswith("cta") or m == "link" or m.startswith("link "):
            out_html.append(f'<a class="link-arrow" href="#">{md_inline(_strip_arrow(t))} <span aria-hidden="true">→</span></a>')
        elif m.startswith("botó") or m.startswith("boton") or m.startswith("button"):
            out_html.append(f'<button class="btn-accent" type="button">{md_inline(_strip_arrow(t))}</button>')
        elif m.startswith("frase de tancament") or m.startswith("frase final") or m.startswith("closing"):
            out_html.append(f'<p class="closing-sentence">{md_inline(t)}</p>')
        elif m.startswith("microtext") or m.startswith("microcopy") or m.startswith("microtrust"):
            out_html.append(f'<p class="microtext">{md_inline(t)}</p>')
        elif m.startswith("paràgraf") or m.startswith("parrafo") or m.startswith("paragraph") or m.startswith("text") or m.startswith("texto") or m.startswith("descripció") or m.startswith("descripcion") or m.startswith("description"):
            out_html.append(f'<p>{md_inline(t)}</p>')
        elif m.startswith("nom unitat") or m.startswith("title destacat"):
            out_html.append(f'<h3 class="card__title">{md_inline(t)}</h3>')
        elif m.startswith("badge") or m.startswith("tag") or m.startswith("pill"):
            out_html.append(f'<span class="tag-pill">{md_inline(t)}</span>')
        # Skip pure layout cues
    return "\n".join(out_html)


# ---------------------------------------------------------------------------
# Render a section (BLOC) with its blocks
# ---------------------------------------------------------------------------

def render_bloc_section(section: dict, idx: int) -> str:
    """Turn a 'bloc' section (with title and blocks) into one or more HTML sections."""
    blocks = collect_fenced_blocks(section["content_lines"])

    # Separate cards from generic fences
    cards: list[dict] = []
    fences: list[dict] = []
    md_blocks: list[dict] = []
    for b in blocks:
        if b["kind"] == "card":
            cards.append(b)
        elif b["kind"] == "fence":
            fences.append(b)
        else:
            md_blocks.append(b)

    parts: list[str] = []
    sec_class = "section section--light" if (idx % 2 == 1) else "section"
    parts.append(f'<section class="{sec_class}">')
    parts.append('  <div class="container">')

    # Build section header from the FIRST fence (which usually carries eyebrow/h2/subhead)
    # before rendering the rest.
    used_first_fence_for_header = False
    if fences:
        first = fences[0]
        entries = parse_marker_block(first["text"])
        eyebrow = ""
        h2 = ""
        subhead_parts: list[str] = []
        rest_entries: list[dict] = []
        consumed_header = False
        for e in entries:
            m = e["marker"] or ""
            t = _join_lines(e["lines"])
            if not consumed_header:
                if m.startswith("eyebrow"):
                    eyebrow = t
                    continue
                if m.startswith("h2") or m == "h2":
                    h2 = t
                    continue
                if m.startswith("subhead") or m.startswith("subtitle") or m.startswith("subtítol"):
                    subhead_parts.append(t)
                    continue
                consumed_header = True
            rest_entries.append(e)

        if not h2 and section.get("title"):
            h2 = section["title"]

        if eyebrow or h2 or subhead_parts:
            parts.append('    <header class="section-header">')
            if eyebrow:
                parts.append(f'      <span class="section-header__eyebrow">{md_inline(eyebrow)}</span>')
            if h2:
                parts.append(f'      <h2 class="section-header__title">{md_inline(h2)}</h2>')
            if subhead_parts:
                parts.append(f'      <p class="section-header__lead">{md_inline(" ".join(subhead_parts))}</p>')
            parts.append('    </header>')
            used_first_fence_for_header = True

        # Render whatever's left from the first fence as body
        if rest_entries:
            # Reassemble as text and run render_fence on it
            # Simpler: render each entry through the same logic as render_fence's generic path
            # We'll synthesize a synthetic block from rest_entries by re-emitting
            rebuilt_lines = []
            for e in rest_entries:
                if e["marker"]:
                    rebuilt_lines.append(f"[{e['annotation']}]")
                rebuilt_lines.extend(e["lines"])
                rebuilt_lines.append("")
            rebuilt = "\n".join(rebuilt_lines)
            rendered = render_fence(rebuilt)
            if rendered:
                parts.append('    <div class="section-body">')
                parts.append("      " + rendered.replace("\n", "\n      "))
                parts.append('    </div>')

    # Then render any md blocks
    if md_blocks:
        parts.append('    <div class="section-body">')
        for b in md_blocks:
            html_md = md_to_html(b["text"])
            if html_md:
                parts.append("      " + html_md.replace("\n", "\n      "))
        parts.append('    </div>')

    # Then render remaining fences (after first)
    extra_fences = fences[1:] if used_first_fence_for_header else fences
    for f in extra_fences:
        rendered = render_fence(f["text"])
        if rendered:
            parts.append('    <div class="section-body">')
            parts.append("      " + rendered.replace("\n", "\n      "))
            parts.append('    </div>')

    # Cards
    if cards:
        parts.append('    <div class="card-grid">')
        for c in cards:
            entries = parse_marker_block(c["text"])
            eyebrow = ""
            title = c["heading"]
            desc_lines: list[str] = []
            cta = ""
            for e in entries:
                m = e["marker"] or ""
                t = _join_lines(e["lines"])
                if not t:
                    continue
                if m.startswith("eyebrow"):
                    eyebrow = t
                elif m.startswith("nom unitat") or m.startswith("title") or m.startswith("h3") or m.startswith("h2"):
                    if not title:
                        title = t
                elif m.startswith("descripció") or m.startswith("descripcion") or m.startswith("description") or m.startswith("text") or m.startswith("texto") or m.startswith("paràgraf") or m.startswith("parrafo") or m.startswith("paragraph") or m is None:
                    desc_lines.append(t)
                elif m.startswith("cta") or m == "link" or m.startswith("link "):
                    cta = _strip_arrow(t)
            parts.append('      <article class="card card--icon">')
            if eyebrow:
                parts.append(f'        <span class="card__cat">{md_inline(eyebrow)}</span>')
            if title:
                parts.append(f'        <h3 class="card__title">{md_inline(title)}</h3>')
            if desc_lines:
                parts.append(f'        <p class="card__excerpt">{md_inline(" ".join(desc_lines))}</p>')
            if cta:
                parts.append(f'        <a class="link-arrow" href="#">{md_inline(cta)} <span aria-hidden="true">→</span></a>')
            parts.append('      </article>')
        parts.append('    </div>')

    parts.append('  </div>')
    parts.append('</section>')
    return "\n".join(parts)


def render_free_section(section: dict) -> str:
    text = "\n".join(section["content_lines"])
    md_html = md_to_html(text)
    if not md_html.strip():
        return ""
    return f'''<section class="article-body">
  <div class="container">
    <div class="article-body__content">
{md_html}
    </div>
  </div>
</section>'''


def render_body(body: str, page: "Page") -> str:
    """Top-level: split body and render each section in order."""
    sections = split_into_sections(body)
    out_parts: list[str] = []
    bloc_index = 0
    for sec in sections:
        if sec["kind"] == "hero":
            # Hero is rendered separately by template; skip here
            continue
        if sec["kind"] == "bloc":
            out_parts.append(render_bloc_section(sec, bloc_index))
            bloc_index += 1
        else:
            free = render_free_section(sec)
            if free:
                out_parts.append(free)
    return "\n".join(out_parts)


def extract_hero(body: str) -> Optional[str]:
    """Return the rendered hero HTML if a `## BLOC HERO` exists, else None."""
    sections = split_into_sections(body)
    for sec in sections:
        if sec["kind"] == "hero":
            blocks = collect_fenced_blocks(sec["content_lines"])
            for b in blocks:
                if b["kind"] == "fence":
                    entries = parse_marker_block(b["text"])
                    return render_hero_from_entries(entries, "ca", "homepage")
    return None


# ---------------------------------------------------------------------------
# JSON-LD schema embedding (preserved from previous generator)
# ---------------------------------------------------------------------------

def load_schema(name: str) -> Optional[dict]:
    p = SCHEMAS / name
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def fill_placeholders(obj, mapping: dict):
    if isinstance(obj, dict):
        return {k: fill_placeholders(v, mapping) for k, v in obj.items()
                if k not in ("_doc", "_replace_before_publish")}
    if isinstance(obj, list):
        return [fill_placeholders(v, mapping) for v in obj]
    if isinstance(obj, str):
        out = obj
        for k, v in mapping.items():
            out = out.replace("{{" + k + "}}", str(v) if v is not None else "")
        return out
    return obj


def build_jsonld(page: Page) -> str:
    schemas = []
    base = page.meta.canonical.rsplit("/", 1)[0] if page.meta.canonical else "https://papik.cat"
    title = page.meta.title or page.meta.h1
    desc = page.meta.description or ""
    img = page.meta.og_image or "https://papik.cat/img/og/og-default.jpg"
    parent_section_name = {"ca": "Inici", "es": "Inicio", "en": "Home"}[page.lang]
    parent_section_url = {"ca": "https://papik.cat/", "es": "https://papik.cat/es/", "en": "https://papik.cat/en/"}[page.lang]
    common = {
        "URL": page.meta.canonical or "",
        "TITLE": title, "DESCRIPTION": desc, "IMAGE": img, "H1": page.meta.h1,
        "LANG": page.lang, "LANGUAGE": page.lang,
        "DATE_PUBLISHED": "2025-01-01", "DATE_MODIFIED": "2026-04-27",
        "BASE_URL": base,
        "SERVICE_NAME": title, "SERVICE_DESCRIPTION": desc,
        "SERVICE_URL": page.meta.canonical or "", "SERVICE_TYPE": "ConstructionService",
        "ARTICLE_HEADLINE": title, "ARTICLE_DESCRIPTION": desc,
        "ARTICLE_URL": page.meta.canonical or "",
        "ARTICLE_SECTION": page.meta.article_section or "Construcció sostenible",
        "AUTHOR_NAME": "PAPIK Group", "AUTHOR_URL": "https://papik.cat/nosaltres",
        "HERO_IMAGE_URL": img,
        "WORD_COUNT": str(max(150, len(page.body_md.split()))),
        "PARENT_SECTION_NAME": parent_section_name,
        "PARENT_SECTION_URL": parent_section_url,
        "CURRENT_PAGE_NAME": page.meta.h1 or title,
        "MUNICIPI_NAME": (page.meta.h1 or page.slug.replace("-", " ").title()),
        "MUNICIPI_SLUG": page.slug,
        "LOCATION_LOCALITY": page.meta.h1 or page.slug.replace("-", " ").title(),
        "LATITUDE": "41.4727", "LONGITUDE": "2.0844",
        "RADIUS_METERS": "15000", "MUNICIPI_HERO_IMAGE": img,
        "LOGO_URL": "https://papik.cat/img/papik-logo.svg",
        "INSTAGRAM_URL": "https://www.instagram.com/papikgroup",
        "LINKEDIN_URL": "https://www.linkedin.com/company/papik-group",
        "YOUTUBE_URL": "https://www.youtube.com/@papikgroup",
        "PASSIVHAUS_LEVEL": "Classic", "HEATING_DEMAND": "15",
        "AIRTIGHTNESS": "0.6", "ENERGY_CLASS": "A", "SQUARE_METERS": "180",
        "PROJECT_NAME": title, "PROJECT_DESCRIPTION": desc,
        "PROJECT_URL": page.meta.canonical or "", "YEAR": "2025",
    }
    if page.page_type == "homepage":
        s = load_schema("01-organization-homepage.json")
        if s:
            schemas.append(fill_placeholders(s, common))
    elif page.page_type == "service":
        s = load_schema("02-service.json")
        if s:
            schemas.append(fill_placeholders(s, common))
    elif page.page_type == "landing":
        s = load_schema("03-localbusiness-landing.json")
        if s:
            schemas.append(fill_placeholders(s, common))
    elif page.page_type == "article":
        s = load_schema("04-article.json")
        if s:
            schemas.append(fill_placeholders(s, common))
    if page.page_type != "homepage":
        bc = load_schema("06-breadcrumb.json")
        if bc:
            schemas.append(fill_placeholders(bc, common))
    if page.has_faq:
        faq = load_schema("05-faqpage.json")
        if faq:
            schemas.append(fill_placeholders(faq, common))
    if not schemas:
        return ""
    body = json.dumps(schemas[0] if len(schemas) == 1 else schemas, ensure_ascii=False, indent=2)
    return f'<script type="application/ld+json">{body}</script>'


# ---------------------------------------------------------------------------
# Header / footer fragments
# ---------------------------------------------------------------------------

LOGO_SVG = '''<svg height="30" viewBox="155 228 535 140" xmlns="http://www.w3.org/2000/svg" style="display:block;overflow:visible;">
<path fill="#002819" d="M659.7,243.4c0-7,5.2-12.1,12.2-12.1c7,0,12.2,5.1,12.2,12.1c0,7-5.2,12.1-12.2,12.1 C664.9,255.5,659.7,250.3,659.7,243.4z M681.3,243.4c0-5.7-3.9-9.7-9.4-9.7c-5.6,0-9.4,4-9.4,9.7s3.9,9.7,9.4,9.7 C677.5,253.1,681.3,249.1,681.3,243.4z M667.5,236.9h4.4c3.2,0,5,1.6,5,3.8c0,1.3-0.8,2.4-2.5,3.4l3.2,5.3h-2.9l-3.6-6l1.6-0.8 c1.1-0.6,1.5-1.1,1.5-1.9c0-1.1-0.9-1.6-2.4-1.6H670v10.2h-2.6V236.9z"/>
<path fill="#002819" d="M489.9,232.2h26.2V364h-26.2V232.2z"/>
<path fill="#002819" d="M533.6,232.2h26.2V364h-26.2V232.2z"/>
<polygon fill="#002819" points="318,232.2 290.1,232.2 236.4,364 264.5,364 272.2,344.4 315.7,336.7 306.8,314 282.4,318.2 303.9,262.8 319.8,303.5 319.8,303.5 341,357.6 341,357.6 343.5,364 371.7,364"/>
<polygon fill="#002819" points="403.8,302.8 403.8,256.8 403.8,232.2 377.6,232.2 377.6,364 403.8,364 403.8,343.4 403.8,327.7"/>
<path fill="#002819" d="M428.4,232.2H417v24.6h11.7c14.8,0,23.3,7.1,23.3,18.9c0,10.8-7.9,18.9-23.1,22l-11.9,2.4v25l11.7-2.3 c34.3-7,49.9-24.7,49.9-48.2C478.6,248.9,458.8,232.2,428.4,232.2z"/>
<polygon fill="#002819" points="184.4,302.8 184.4,302.8 184.4,256.8 184.4,256.8 184.4,232.2 158.2,232.2 158.2,364 184.4,364 184.4,327.7 184.4,327.7"/>
<path fill="#002819" d="M208.9,232.2h-11.3v24.6h11.7c14.8,0,23.3,7.1,23.3,18.9c0,10.8-7.9,18.9-23.1,22l-11.9,2.4v25l11.7-2.3 c34.3-7,49.9-24.7,49.9-48.2C259.2,248.9,239.4,232.2,208.9,232.2z"/>
<path fill="#002819" d="M614.3,297.6c31.3-22.9,33.7-65.3,33.7-65.3h-26.2c0,0-1,34.1-27.1,49.2c0,0-5.5,3.4-10.1,5.4 c-4.6,2.1-13.1,5.1-13.1,5.1v25.1l19.2-7.9l31.5,54.9h29.5L614.3,297.6z"/>
</svg>'''


def lang_options(page: Page) -> str:
    options = []
    for code, label in (("ca", "CA"), ("es", "ES"), ("en", "EN")):
        if code in page.meta.hreflang:
            url = page.meta.hreflang[code]
            sel = " selected" if code == page.lang else ""
            options.append(f'<option value="{html.escape(url)}"{sel}>{label}</option>')
    if not options:
        options = [f'<option value="" selected>{page.lang.upper()}</option>']
    return "\n          ".join(options)


def asset_prefix(page: Page) -> str:
    """Relative path back to /public/ for css/js/img references."""
    return "../" * (page.out_depth - 1)


def lang_root(lang: str) -> str:
    """Absolute URL prefix for a given language root (CA at /, ES at /es/, EN at /en/)."""
    if lang == "ca":
        return "/"
    return f"/{lang}/"


def header_html(page: Page) -> str:
    pref = asset_prefix(page)
    home_href = lang_root(page.lang)
    return f'''<header class="header-top" id="headerTop">
  <div class="header-logo-layer"></div>
  <div class="header-logo">
    <div class="container">
      <div class="header-logo__content">
        <div class="menu-btn-wrapper" id="burgerBtn">
          <div class="menu-btn__burger"><span></span><span></span><span></span></div>
        </div>
        <div class="logo">
          <a href="{home_href}">{LOGO_SVG}</a>
        </div>
      </div>
      <div class="lang">
        <select onchange="if(this.value)location=this.value">
          {lang_options(page)}
        </select>
      </div>
    </div>
  </div>
</header>'''


FOOTER_BY_LANG = {
    "ca": {
        "papik": "PAPIK", "qui_som": "Qui som", "projects": "Projectes",
        "blog": "Blog", "contact": "Contacte",
        "services": "Serveis", "construction": "Construcció Residencial",
        "promotion": "Promoció Immobiliària", "retrofit": "Rehabilitació Energètica",
        "wealth": "Patrimonis · Inversió Conjunta",
        "offices": "Oficines", "newsletter": "Newsletter",
        "newsletter_copy": "Segueix les novetats de PAPIK: projectes, rehabilitació energètica i ajudes disponibles.",
        "email": "El teu email", "follow": "Segueix-nos",
        "copyright": "Copyright © 2025 PAPIK Fusters S.L. – Tots els drets reservats · papik.cat",
        "legal": "Avís Legal", "privacy": "Política de Privacitat",
        "cookies_link": "Galetes",
        "construccio_url": "construccio.html", "promocio_url": "promocio.html",
        "rehabilitacio_url": "rehabilitacio.html", "patrimonis_url": "patrimonis.html",
        "blog_url": "blog.html", "nosaltres_url": "nosaltres.html",
        "projectes_url": "projectes.html",
        "legal_url": "avis-legal.html", "privacy_url": "politica-privacitat.html",
        "cookies_url": "politica-cookies.html",
    },
    "es": {
        "papik": "PAPIK", "qui_som": "Quiénes somos", "projects": "Proyectos",
        "blog": "Blog", "contact": "Contacto",
        "services": "Servicios", "construction": "Construcción Residencial",
        "promotion": "Promoción Inmobiliaria", "retrofit": "Rehabilitación Energética",
        "wealth": "Patrimonios · Inversión Conjunta",
        "offices": "Oficinas", "newsletter": "Newsletter",
        "newsletter_copy": "Sigue las novedades de PAPIK: proyectos, rehabilitación energética y ayudas disponibles.",
        "email": "Tu email", "follow": "Síguenos",
        "copyright": "Copyright © 2025 PAPIK Fusters S.L. – Todos los derechos reservados · papik.cat",
        "legal": "Aviso Legal", "privacy": "Política de Privacidad",
        "cookies_link": "Cookies",
        "construccio_url": "construccion.html", "promocio_url": "promocion.html",
        "rehabilitacio_url": "rehabilitacion.html", "patrimonis_url": "patrimonios.html",
        "blog_url": "blog.html", "nosaltres_url": "nosotros.html",
        "projectes_url": "proyectos.html",
        "legal_url": "aviso-legal.html", "privacy_url": "politica-privacidad.html",
        "cookies_url": "politica-cookies.html",
    },
    "en": {
        "papik": "PAPIK", "qui_som": "About us", "projects": "Projects",
        "blog": "Blog", "contact": "Contact",
        "services": "Services", "construction": "Residential Construction",
        "promotion": "Real Estate Development", "retrofit": "Energy Retrofit",
        "wealth": "Wealth · Joint Investment",
        "offices": "Offices", "newsletter": "Newsletter",
        "newsletter_copy": "Follow PAPIK: projects, energy retrofit and available subsidies.",
        "email": "Your email", "follow": "Follow us",
        "copyright": "Copyright © 2025 PAPIK Fusters S.L. – All rights reserved · papik.cat",
        "legal": "Legal Notice", "privacy": "Privacy Policy",
        "cookies_link": "Cookies",
        "construccio_url": "construction.html", "promocio_url": "development.html",
        "rehabilitacio_url": "retrofit.html", "patrimonis_url": "wealth.html",
        "blog_url": "blog.html", "nosaltres_url": "about.html",
        "projectes_url": "projects.html",
        "legal_url": "legal-notice.html", "privacy_url": "privacy-policy.html",
        "cookies_url": "cookie-policy.html",
    },
}


def footer_html(page: Page) -> str:
    f = FOOTER_BY_LANG[page.lang]
    root = lang_root(page.lang)
    return f'''<footer>
  <div class="container">
    <div class="footer__content__info color-white">
      <div class="footer-col">
        <p class="footer__col-title">{f["papik"]}</p>
        <ul>
          <li><a href="{root}{f["nosaltres_url"]}">{f["qui_som"]}</a></li>
          <li><a href="{root}{f["projectes_url"]}">{f["projects"]}</a></li>
          <li><a href="{root}{f["blog_url"]}">{f["blog"]}</a></li>
          <li><a href="#contacte">{f["contact"]}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <p class="footer__col-title">{f["services"]}</p>
        <ul>
          <li><a href="{root}{f["construccio_url"]}">{f["construction"]}</a></li>
          <li><a href="{root}{f["promocio_url"]}">{f["promotion"]}</a></li>
          <li><a href="{root}{f["rehabilitacio_url"]}">{f["retrofit"]}</a></li>
          <li><a href="{root}{f["patrimonis_url"]}">{f["wealth"]}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <p class="footer__col-title">{f["offices"]}</p>
        <div class="info-showroom__item">
          <h3>SEU CENTRAL</h3>
          <p>Carrer de la Sort, 34<br>08172 Sant Cugat del Vallès<br><a href="tel:935906074">T 93 590 60 74</a></p>
        </div>
        <div class="info-showroom__item">
          <h3>{"CORREU" if page.lang == "ca" else ("CORREO" if page.lang == "es" else "EMAIL")}</h3>
          <p><a href="mailto:info@papik.cat">info@papik.cat</a></p>
        </div>
      </div>
      <div class="footer__newsletter">
        <p class="footer__col-title">{f["newsletter"]}</p>
        <p>{f["newsletter_copy"]}</p>
        <form class="newsletter-form" action="#" method="post" novalidate>
          <input type="email" placeholder="{f["email"]}" required>
          <button type="submit" aria-label="Subscribe">→</button>
        </form>
        <div class="footer__rrss">
          <p>{f["follow"]}</p>
          <div class="rrss__links">
            <a href="https://www.instagram.com/papikgroup">Instagram</a>
            <a href="https://www.linkedin.com/company/papik-group">LinkedIn</a>
            <a href="https://www.youtube.com/@papikgroup">YouTube</a>
          </div>
        </div>
      </div>
    </div>
    <div class="copyright">
      <p>{f["copyright"]}</p>
      <div class="legal" style="display:flex;gap:20px;">
        <a href="{root}{f["legal_url"]}">{f["legal"]}</a>
        <a href="{root}{f["privacy_url"]}">{f["privacy"]}</a>
        <a href="{root}{f["cookies_url"]}">{f["cookies_link"]}</a>
      </div>
    </div>
  </div>
</footer>'''


COOKIE_BANNER = '''<aside id="papik-cc-banner" class="papik-cc" role="region" aria-label="Avís de galetes" hidden>
  <div class="papik-cc-inner">
    <div class="papik-cc-copy">
      <h2 data-cc-text="title">Aquesta web utilitza galetes</h2>
      <p data-cc-text="body">Utilitzem galetes pròpies i de tercers per analitzar el nostre servei i mostrar-te publicitat relacionada amb les teves preferències. Pots acceptar-les totes, rebutjar-les totes o configurar-les.</p>
    </div>
    <div class="papik-cc-actions">
      <button type="button" class="papik-cc-btn papik-cc-btn--ghost" data-cc-action="reject">Rebutjar tot</button>
      <button type="button" class="papik-cc-btn papik-cc-btn--ghost" data-cc-action="configure">Configurar</button>
      <button type="button" class="papik-cc-btn papik-cc-btn--primary" data-cc-action="accept">Acceptar tot</button>
    </div>
  </div>
</aside>'''


# ---------------------------------------------------------------------------
# Page template
# ---------------------------------------------------------------------------

EXTRA_INLINE_CSS = """
.section-header__eyebrow{display:inline-block;font-size:11px;text-transform:uppercase;letter-spacing:.18em;color:var(--accent);margin-bottom:14px;font-weight:var(--fw-regular);}
.section-header{display:block;margin-bottom:32px;max-width:760px;}
.section-header__title{font-size:clamp(22px,2.4vw,32px);font-weight:var(--fw-light);color:var(--text);line-height:1.2;}
.section-header__lead{margin-top:14px;color:var(--muted);font-size:16px;line-height:1.6;}
.section-body{font-size:16px;line-height:1.75;color:var(--muted);max-width:760px;}
.section-body h2{font-size:clamp(22px,2.4vw,28px);font-weight:var(--fw-light);color:var(--text);margin:36px 0 14px;line-height:1.2;}
.section-body h3{font-size:clamp(17px,1.7vw,22px);font-weight:var(--fw-regular);color:var(--text);margin:28px 0 10px;}
.section-body h4{font-size:15px;font-weight:var(--fw-medium);color:var(--text);margin:20px 0 8px;}
.section-body p{margin-bottom:16px;}
.section-body strong{color:var(--text);font-weight:var(--fw-medium);}
.section-body ul,.section-body ol{padding-left:22px;margin-bottom:18px;}
.section-body li{margin-bottom:6px;}
.section-body a{color:var(--green);border-bottom:1px solid var(--border);}
.section-body a:hover{color:var(--accent);border-color:var(--accent);}
.section-body .lead{font-size:18px;color:var(--text);font-weight:var(--fw-light);line-height:1.55;margin-bottom:20px;}
.section-body .closing-sentence{font-size:clamp(20px,2vw,26px);font-weight:var(--fw-light);color:var(--text);line-height:1.35;margin:32px 0;letter-spacing:-.005em;}
.section-body .microtext{font-size:13px;color:var(--muted-light);}
.section-body .eyebrow{display:inline-block;font-size:11px;text-transform:uppercase;letter-spacing:.18em;color:var(--accent);font-weight:var(--fw-regular);margin-bottom:8px;}
.hero--dark .hero__microtrust{margin-top:24px;font-size:13px;color:rgba(255,255,255,.55);letter-spacing:.02em;}
.hero{padding:96px 0 64px;}
.hero--dark{background:linear-gradient(160deg,#0A1B12 0%,#002819 60%,#56685E 110%);}
.hero__actions{margin-top:28px;display:inline-flex;gap:12px;flex-wrap:wrap;}
.data-table{width:100%;border-collapse:collapse;margin:24px 0;font-size:14px;}
.data-table th,.data-table td{border:1px solid var(--border);padding:10px 12px;text-align:left;vertical-align:top;}
.data-table th{background:var(--bg-light);font-weight:var(--fw-medium);color:var(--text);}
.faq-list{margin:24px 0;border-top:1px solid var(--border);}
.faq-item{border-bottom:1px solid var(--border);padding:16px 0;}
.faq-item summary{cursor:pointer;font-size:16px;font-weight:var(--fw-medium);color:var(--text);list-style:none;display:flex;justify-content:space-between;align-items:center;gap:16px;}
.faq-item summary::after{content:"+";color:var(--green);font-size:22px;line-height:1;transition:transform .25s ease;}
.faq-item[open] summary::after{transform:rotate(45deg);}
.faq-item__body{padding-top:12px;color:var(--muted);font-size:15px;line-height:1.6;}
.phase-list{list-style:none;padding:0;margin:32px 0;border-top:1px solid var(--border);}
.phase-list__item{display:grid;grid-template-columns:64px 1fr;gap:24px;padding:22px 0;border-bottom:1px solid var(--border);align-items:flex-start;}
.phase-list__num{font-size:clamp(20px,2vw,28px);font-weight:var(--fw-light);color:var(--accent);line-height:1;}
.phase-list__title{font-size:17px;font-weight:var(--fw-medium);color:var(--text);margin-bottom:6px;line-height:1.3;}
.phase-list__text{color:var(--muted);font-size:14px;line-height:1.6;margin:0;}
.cross-links{margin:32px 0;padding:24px;background:var(--bg-light);border-radius:var(--r-md);}
.cross-links__label{font-size:12px;text-transform:uppercase;letter-spacing:.15em;color:var(--muted);margin-bottom:14px;}
.cross-links ul{padding:0;margin:0;}
.cross-links li{padding:6px 0;border-bottom:1px solid var(--border-soft);}
.cross-links li:last-child{border-bottom:0;}
.form{display:grid;gap:16px;max-width:520px;margin:24px 0;}
.form-field{display:block;}
.form-field__label{display:block;font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);margin-bottom:6px;}
.form-field__input{width:100%;height:44px;padding:0 14px;border:1px solid var(--border);background:#fff;font-size:15px;color:var(--text);font-family:var(--ff-sans);border-radius:var(--r-sm);}
.form-field__input:focus{outline:2px solid var(--green);outline-offset:2px;}
.form-field--check{display:flex;align-items:flex-start;gap:10px;font-size:14px;color:var(--muted);}
.form-field--check input{margin-top:3px;}
.card-grid .card--icon{padding:24px 22px;}
.article-body{padding:56px 0 80px;background:#fff;}
.article-body__content{max-width:min(70ch,720px);margin:0 auto;}
.article-body__content h2{font-size:clamp(22px,2.4vw,32px);font-weight:var(--fw-light);margin:48px 0 20px;color:var(--text);line-height:1.2;}
.article-body__content h3{font-size:clamp(18px,1.8vw,22px);font-weight:var(--fw-regular);margin:32px 0 14px;color:var(--text);}
.article-body__content p{font-size:16px;line-height:1.75;color:var(--muted);margin-bottom:20px;}
.article-body__content ul,.article-body__content ol{padding-left:22px;margin-bottom:20px;}
.article-body__content li{font-size:16px;line-height:1.75;color:var(--muted);margin-bottom:8px;}
.article-body__content strong{color:var(--text);font-weight:var(--fw-medium);}
.article-body__content blockquote{padding:24px 28px;background:var(--bg-light);border-radius:var(--r-md);font-size:18px;font-weight:var(--fw-light);color:var(--text);margin:32px 0;}
.article-body__content a{color:var(--green);border-bottom:1px solid var(--border);}
.article-body__content a:hover{color:var(--accent);border-color:var(--accent);}
.breadcrumb{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted-light);margin-bottom:24px;}
.hero--dark .breadcrumb{color:rgba(255,255,255,.7);}
.hero--dark .breadcrumb a{color:rgba(255,255,255,.85);}
.breadcrumb a{color:var(--muted-light);border-bottom:0;}
.breadcrumb a:hover{opacity:.7;}
.breadcrumb .sep{opacity:.5;}
.block-cta{background:var(--green);color:#fff;padding:64px 0;text-align:center;}
.block-cta__label{font-size:11px;text-transform:uppercase;letter-spacing:.2em;color:rgba(255,255,255,.55);margin-bottom:14px;}
.block-cta__title{font-size:clamp(22px,2.4vw,32px);font-weight:var(--fw-light);color:#fff;line-height:1.2;margin:0 auto 20px;max-width:680px;}
.block-cta__sub{font-size:15px;color:rgba(255,255,255,.7);max-width:540px;margin:0 auto 28px;}
"""


def hreflang_tags(page: Page) -> str:
    return "\n  ".join(
        f'<link rel="alternate" hreflang="{html.escape(code)}" href="{html.escape(url)}">'
        for code, url in page.meta.hreflang.items()
    )


def html_lang_attr(lang: str) -> str:
    return {"ca": "ca", "es": "es", "en": "en"}.get(lang, "ca")


def render_breadcrumb(page: Page) -> str:
    if page.page_type == "homepage":
        return ""
    label_home = {"ca": "Inici", "es": "Inicio", "en": "Home"}[page.lang]
    home_href = lang_root(page.lang)
    here = html.escape(page.meta.h1 or page.meta.title or page.slug.replace("-", " ").title())
    return f'''<nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="{home_href}">{label_home}</a>
        <span class="sep">·</span>
        <span>{here}</span>
      </nav>'''


def hero_for_page(page: Page) -> str:
    """Render the page's hero. Prefers `## BLOC HERO` block; falls back to a default hero."""
    body_text = page.body_md
    sections = split_into_sections(body_text)
    breadcrumb = render_breadcrumb(page)

    for sec in sections:
        if sec["kind"] != "hero":
            continue
        blocks = collect_fenced_blocks(sec["content_lines"])
        for b in blocks:
            if b["kind"] == "fence":
                entries = parse_marker_block(b["text"])
                # Build hero
                eyebrow = ""
                h1 = ""
                subhead_parts: list[str] = []
                primary_cta = None
                secondary_cta = None
                microtrust = ""
                for e in entries:
                    m = e["marker"] or ""
                    t = _join_lines(e["lines"])
                    if not t:
                        continue
                    if m.startswith("eyebrow"):
                        eyebrow = t
                    elif m == "h1" or m.startswith("h1"):
                        h1 = t
                    elif m.startswith("subhead") or m.startswith("subtitle") or m.startswith("subtítol"):
                        subhead_parts.append(t)
                    elif m.startswith("cta primari") or m.startswith("cta primary") or m.startswith("cta principal"):
                        primary_cta = _strip_arrow(t)
                    elif m.startswith("cta secund") or m.startswith("cta secondary"):
                        secondary_cta = _strip_arrow(t)
                    elif m.startswith("microtrust") or m.startswith("micro-trust"):
                        microtrust = t
                    elif m is None:
                        subhead_parts.append(t)
                if not h1:
                    h1 = page.meta.h1 or page.meta.title

                parts = [
                    '<section class="hero hero--dark">',
                    '  <div class="container">',
                ]
                if breadcrumb:
                    parts.append("    " + breadcrumb)
                if eyebrow:
                    parts.append(f'    <span class="hero__eyebrow">{md_inline(eyebrow)}</span>')
                if h1:
                    parts.append(f'    <h1 class="hero__title">{md_inline(h1)}</h1>')
                if subhead_parts:
                    parts.append(f'    <p class="hero__subtitle">{md_inline(" ".join(subhead_parts))}</p>')
                if primary_cta or secondary_cta:
                    parts.append('    <div class="hero__actions">')
                    if primary_cta:
                        parts.append(f'      <a class="btn-white" href="#contacte">{md_inline(primary_cta)} <span aria-hidden="true">→</span></a>')
                    if secondary_cta:
                        parts.append(f'      <a class="btn-outline" href="#main">{md_inline(secondary_cta)} <span aria-hidden="true">→</span></a>')
                    parts.append('    </div>')
                if microtrust:
                    parts.append(f'    <p class="hero__microtrust">{md_inline(microtrust)}</p>')
                parts.append('  </div>')
                parts.append('</section>')
                return "\n".join(parts)

    # Fallback hero
    h1 = page.meta.h1 or page.meta.title or page.slug.replace("-", " ").title()
    desc = page.meta.description or ""
    parts = ['<section class="hero hero--dark">', '  <div class="container">']
    if breadcrumb:
        parts.append("    " + breadcrumb)
    parts.append(f'    <h1 class="hero__title">{md_inline(h1)}</h1>')
    if desc:
        parts.append(f'    <p class="hero__subtitle">{md_inline(desc)}</p>')
    parts.append('  </div>')
    parts.append('</section>')
    return "\n".join(parts)


def render_page(page: Page) -> str:
    pref = asset_prefix(page)
    title = html.escape(page.meta.title or page.meta.h1 or "PAPIK")
    desc = html.escape(page.meta.description or "")
    canonical = html.escape(page.meta.canonical or "")
    og_image = html.escape(page.meta.og_image or "https://papik.cat/img/og/og-default.jpg")
    og_locale = html.escape(page.meta.og_locale or {"ca": "ca_ES", "es": "es_ES", "en": "en_US"}[page.lang])
    jsonld = build_jsonld(page)
    hero = hero_for_page(page)
    body_html = render_body(page.body_md, page)
    if not body_html.strip():
        # Fallback: render the whole body as free markdown article
        sections = split_into_sections(page.body_md)
        # Keep only non-hero, non-skip
        text = "\n".join(
            "\n".join(s["content_lines"]) for s in sections if s["kind"] not in ("hero", "skip")
        )
        body_html = f'''<section class="article-body">
  <div class="container"><div class="article-body__content">
{md_to_html(text)}
  </div></div>
</section>'''

    return f'''<!DOCTYPE html>
<html lang="{html_lang_attr(page.lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{desc}">

  <link rel="canonical" href="{canonical}">
  {hreflang_tags(page)}

  <link rel="stylesheet" href="{pref}css/tokens.css">
  <link rel="stylesheet" href="{pref}css/base.css">
  <link rel="stylesheet" href="{pref}css/header.css">
  <link rel="stylesheet" href="{pref}css/components.css">
  <link rel="stylesheet" href="{pref}css/footer.css">
  <link rel="stylesheet" href="/css/cookie-banner.css">

  <style>{EXTRA_INLINE_CSS}</style>

  <meta property="og:type" content="{('article' if page.page_type == 'article' else 'website')}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="PAPIK Group">
  <meta property="og:locale" content="{og_locale}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{og_image}">
  <meta name="theme-color" content="#002819">

  {jsonld}
</head>
<body class="page--{page.page_type}">
{COOKIE_BANNER}

{header_html(page)}

<main id="main">
{hero}
{body_html}
</main>

{footer_html(page)}

<script src="{pref}js/cookie-banner.js" defer></script>
<script src="{pref}js/forms.js" defer></script>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

SLUG_TYPE = {
    "homepage": "homepage", "index": "homepage",
    "construccio": "service", "construccion": "service", "construction": "service",
    "promocio": "service", "promocion": "service", "development": "service",
    "rehabilitacio": "service", "rehabilitacion": "service", "retrofit": "service",
    "patrimonis": "service", "patrimonios": "service", "wealth": "service",
    "comunitats": "community", "comunidades": "community", "communities": "community",
}


def classify(src: Path, lang: str) -> tuple[str, str, Path, int]:
    """Return (page_type, slug, out_path, out_depth)."""
    name = src.stem
    parent = src.parent.name

    base = re.sub(r"-(?:ca-v2|ca|es|en)$", "", name)

    if base in ("homepage",):
        ptype = "homepage"
        slug = "index"
    elif parent == "legal":
        ptype = "legal"
        slug = base
    elif parent in ("landings", "areas", "zonas", "zones"):
        ptype = "landing"
        slug = base
    elif parent in ("comarques", "comarcas", "regions"):
        ptype = "landing"
        slug = base
    elif parent == "retrofit":
        ptype = "community"
        slug = base
    elif parent == "articles":
        ptype = "article"
        slug = base
    elif base.startswith("article-"):
        ptype = "article"
        slug = base
    else:
        ptype = SLUG_TYPE.get(base, "article")
        slug = base

    out_depth = 1
    if lang == "ca":
        if ptype == "homepage":
            out = OUT_ROOT / "index.html"
        elif ptype == "landing":
            if parent == "comarques":
                out = OUT_ROOT / "comarques" / f"{slug}.html"
                out_depth = 2
            else:
                out = OUT_ROOT / "zones" / f"{slug}.html"
                out_depth = 2
        elif ptype == "legal":
            out = OUT_ROOT / f"{slug}.html"
        else:
            out = OUT_ROOT / f"{slug}.html"
    elif lang == "es":
        out_depth = 2
        if ptype == "homepage":
            out = OUT_ES / "index.html"
        elif ptype == "landing":
            if parent == "comarcas":
                out = OUT_ES / "comarcas" / f"{slug}.html"
                out_depth = 3
            else:
                out = OUT_ES / "zonas" / f"{slug}.html"
                out_depth = 3
        elif ptype == "legal":
            out = OUT_ES / f"{slug}.html"
        else:
            out = OUT_ES / f"{slug}.html"
    else:  # en
        out_depth = 2
        if ptype == "homepage":
            out = OUT_EN / "index.html"
        elif ptype == "landing":
            if parent == "regions":
                out = OUT_EN / "regions" / f"{slug}.html"
                out_depth = 3
            else:
                out = OUT_EN / "areas" / f"{slug}.html"
                out_depth = 3
        elif ptype == "community":
            out = OUT_EN / "retrofit" / f"{slug}.html"
            out_depth = 3
        elif ptype == "legal":
            out = OUT_EN / f"{slug}.html"
        else:
            out = OUT_EN / f"{slug}.html"

    return ptype, slug, out, out_depth


def collect_sources() -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for p in sorted(SRC_CA.rglob("*.md")):
        if p.name in IGNORE_BASENAMES:
            continue
        if p.stem.endswith("-ca"):
            sibling = p.with_name(p.stem + "-v2.md")
            if sibling.exists():
                continue
        out.append((p, "ca"))
    for p in sorted(SRC_ES.rglob("*.md")):
        if p.name in IGNORE_BASENAMES:
            continue
        if "rewrites" in p.parts:
            continue
        out.append((p, "es"))
    for p in sorted(SRC_EN.rglob("*.md")):
        if p.name in IGNORE_BASENAMES:
            continue
        out.append((p, "en"))
    return out


def reconcile_hreflang(pages: list[Page]) -> None:
    """Fill in missing hreflang entries by inspecting siblings.

    The CA/ES articles were authored before EN existed, so their meta blocks
    only declare CA+ES (and an x-default). Now EN exists and *its* meta block
    correctly declares all three siblings. We use that to back-fill the older
    CA/ES pages: if EN page X declares CA sibling Y and ES sibling Z, then
    Y must declare EN sibling X and Z must declare EN sibling X.
    """
    # Index by canonical URL
    by_canonical: dict[str, Page] = {}
    for p in pages:
        if p.meta.canonical:
            by_canonical[p.meta.canonical.rstrip("/")] = p

    # Cross-reference: for every (page, hreflang_entry) pair, ensure the
    # target page declares the source page as its sibling for the source's lang.
    changed = True
    iterations = 0
    while changed and iterations < 4:
        changed = False
        iterations += 1
        for p in pages:
            for code, url in list(p.meta.hreflang.items()):
                if code in ("x-default",):
                    continue
                target = by_canonical.get(url.rstrip("/"))
                if target is None:
                    continue
                # target should declare p.lang -> p.canonical
                if p.lang not in target.meta.hreflang and p.meta.canonical:
                    target.meta.hreflang[p.lang] = p.meta.canonical
                    changed = True
                # target should also declare its self-canonical for its own lang
                if target.lang not in target.meta.hreflang and target.meta.canonical:
                    target.meta.hreflang[target.lang] = target.meta.canonical
                    changed = True

    # Final pass: ensure every page declares its own self-canonical hreflang
    for p in pages:
        if p.meta.canonical and p.lang not in p.meta.hreflang:
            p.meta.hreflang[p.lang] = p.meta.canonical


def build_pages() -> tuple[list[Page], list[tuple[Path, str]]]:
    pages: list[Page] = []
    errors: list[tuple[Path, str]] = []
    for src, lang in collect_sources():
        try:
            raw = src.read_text(encoding="utf-8")
            meta = parse_meta(raw)
            cleaned = strip_top_doc(raw)
            cleaned = strip_internal_notes(cleaned)
            cleaned = strip_trailing_blocks(cleaned)
            # Strip the meta tags ```html``` code block from body (already extracted)
            cleaned_body = META_BLOCK_RE.sub("", cleaned, count=1).strip()
            meta.h1 = first_h1_marker(raw) or meta.h1 or meta.title
            ptype, slug, out_path, out_depth = classify(src, lang)
            page = Page(
                src=src, out=out_path, lang=lang, page_type=ptype, slug=slug,
                raw=raw, meta=meta, body_md=cleaned_body,
                out_depth=out_depth,
                has_faq=detect_faq(raw),
            )
            pages.append(page)
        except Exception as e:
            errors.append((src, f"{type(e).__name__}: {e}"))
    reconcile_hreflang(pages)
    return pages, errors


def write_all(pages: list[Page]) -> tuple[int, int, dict]:
    written = 0
    failed = 0
    by_type: dict[str, int] = {}
    by_lang: dict[str, int] = {}
    for page in pages:
        try:
            page.out.parent.mkdir(parents=True, exist_ok=True)
            html_text = render_page(page)
            page.out.write_text(html_text, encoding="utf-8")
            written += 1
            by_type[page.page_type] = by_type.get(page.page_type, 0) + 1
            by_lang[page.lang] = by_lang.get(page.lang, 0) + 1
        except Exception as e:
            failed += 1
            print(f"FAIL {page.src} -> {page.out}: {e}", file=sys.stderr)
    return written, failed, {"by_type": by_type, "by_lang": by_lang}


def write_report(pages, errors, written, failed, summary):
    rep_path = ROOT / "seo-internal" / "s4-build-report.md"
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# S4 Build Report (post-redesign generator)\n")
    lines.append(f"- Total source files discovered: **{len(pages) + len(errors)}**")
    lines.append(f"- HTML files written: **{written}**")
    lines.append(f"- Failed: **{failed}**\n")
    lines.append("## Per-language\n")
    for lang in ("ca", "es", "en"):
        lines.append(f"- {lang.upper()}: {summary['by_lang'].get(lang, 0)}")
    lines.append("\n## Per-type\n")
    for k, v in sorted(summary["by_type"].items()):
        lines.append(f"- {k}: {v}")
    if errors:
        lines.append("\n## Parse errors\n")
        for src, msg in errors:
            lines.append(f"- `{src.name}` — {msg}")
    lines.append("\n## Validation spot-check\n")
    samples = []
    for ptype in ("homepage", "service", "article", "landing", "legal", "community"):
        match = next((p for p in pages if p.page_type == ptype and p.lang == "ca"), None) \
                or next((p for p in pages if p.page_type == ptype), None)
        if match:
            samples.append(match)
    for p in samples:
        if not p.out.exists():
            continue
        text = p.out.read_text(encoding="utf-8")
        ok_canonical = "rel=\"canonical\"" in text and bool(p.meta.canonical)
        ok_hreflang = "hreflang=" in text
        ok_h1 = "<h1" in text
        no_markers = (
            "[Eyebrow]" not in text and "[H1]" not in text and "[H2]" not in text
            and "[CTA primari]" not in text and "BLOC HERO" not in text
            and "{{" not in text
        )
        lines.append(
            f"- {p.page_type}/{p.lang} `{p.out.relative_to(ROOT)}` — canonical:{ok_canonical} hreflang:{ok_hreflang} h1:{ok_h1} clean:{no_markers}"
        )
    rep_path.write_text("\n".join(lines), encoding="utf-8")
    return rep_path


def main():
    pages, errors = build_pages()
    written, failed, summary = write_all(pages)
    rep = write_report(pages, errors, written, failed, summary)
    print(f"PAPIK: wrote {written} HTML files (failed={failed}). Report: {rep}")


if __name__ == "__main__":
    main()
