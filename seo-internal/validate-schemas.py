#!/usr/bin/env python3
"""
Schema.org JSON-LD validation pass for PAPIK Group static site.
Walks /public/, finds .html files, extracts JSON-LD, validates structure,
detects placeholder leaks, and writes a report.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Optional, Tuple, List

PUBLIC_DIR = Path("/Users/trisfisas/Desktop/CÓDIGO/papik-web/public")
REPORT_PATH = Path("/Users/trisfisas/Desktop/CÓDIGO/papik-web/seo-internal/schema-validation-report.md")

EXCLUDE_PATTERNS = [
    re.compile(r"^dashboard-.*\.html$"),
    re.compile(r"^_t\.html$"),
    re.compile(r"^404\.html$"),
    re.compile(r".*test.*\.html$", re.IGNORECASE),
]

REQUIRED_FIELDS = {
    "Article": ["headline", "datePublished", "author", "publisher", "mainEntityOfPage"],
    "NewsArticle": ["headline", "datePublished", "author", "publisher", "mainEntityOfPage"],
    "BlogPosting": ["headline", "datePublished", "author", "publisher", "mainEntityOfPage"],
    "Service": ["name", "provider", "areaServed"],
    "LocalBusiness": ["name", "address", "geo"],  # telephone OR url checked separately
    "GeneralContractor": ["name", "address", "geo"],
    "HomeAndConstructionBusiness": ["name", "address", "geo"],
    "Organization": ["name", "url", "logo", "sameAs"],
    "RealEstateListing": ["name", "description", "url"],
    "FAQPage": ["mainEntity"],
    "BreadcrumbList": ["itemListElement"],
    "CollectionPage": ["name", "description"],
}

PLACEHOLDER_PATTERNS = [
    re.compile(r"\[XXX\]"),
    re.compile(r"\[FECHA REAL\]", re.IGNORECASE),
    re.compile(r"\[DATA REAL\]", re.IGNORECASE),
    re.compile(r"\[DATE REAL\]", re.IGNORECASE),
    re.compile(r"\[INSERT[^\]]*\]", re.IGNORECASE),
    re.compile(r"\[REPLACE[^\]]*\]", re.IGNORECASE),
    re.compile(r"\[TODO[^\]]*\]", re.IGNORECASE),
    re.compile(r"\[PLACEHOLDER[^\]]*\]", re.IGNORECASE),
    re.compile(r"\[YOUR[^\]]*\]", re.IGNORECASE),
    re.compile(r"\bLOREM IPSUM\b", re.IGNORECASE),
    re.compile(r"\bXXXX\b"),
]

PLACEHOLDER_REPLACEMENTS = {
    "[FECHA REAL]": "2026-06-01",
    "[DATA REAL]": "2026-06-01",
    "[DATE REAL]": "2026-06-01",
}

JSON_LD_BLOCK_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)

LANG_ATTR_RE = re.compile(r'<html[^>]*\blang=["\']([^"\']+)["\']', re.IGNORECASE)


def is_excluded(filename: str) -> bool:
    return any(p.match(filename) for p in EXCLUDE_PATTERNS)


def find_html_files(root: Path):
    files = []
    for p in root.rglob("*.html"):
        if is_excluded(p.name):
            continue
        files.append(p)
    return sorted(files)


def page_lang(html: str) -> Optional[str]:
    m = LANG_ATTR_RE.search(html)
    if not m:
        return None
    return m.group(1).split("-")[0].lower()


def extract_jsonld_blocks(html: str):
    """Yield (raw_text, start_offset_in_html)."""
    for m in JSON_LD_BLOCK_RE.finditer(html):
        yield m.group(1), m.start(1)


def line_of_offset(html: str, offset: int) -> int:
    return html.count("\n", 0, offset) + 1


def collect_types(node, types: list):
    """Walk node and collect every @type seen (handles arrays/nested @graph)."""
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            types.append(t)
        elif isinstance(t, list):
            types.extend([x for x in t if isinstance(x, str)])
        if "@graph" in node and isinstance(node["@graph"], list):
            for sub in node["@graph"]:
                collect_types(sub, types)
        # Also recurse into mainEntity which sometimes is a wrapped node
    elif isinstance(node, list):
        for sub in node:
            collect_types(sub, types)


def iter_typed_nodes(node):
    """Yield every dict node that has an @type, with its (type-string-or-list, dict)."""
    if isinstance(node, dict):
        if "@type" in node:
            yield node
        if "@graph" in node and isinstance(node["@graph"], list):
            for sub in node["@graph"]:
                yield from iter_typed_nodes(sub)
    elif isinstance(node, list):
        for sub in node:
            yield from iter_typed_nodes(sub)


def node_types(node: dict):
    t = node.get("@type")
    if isinstance(t, str):
        return [t]
    if isinstance(t, list):
        return [x for x in t if isinstance(x, str)]
    return []


def find_placeholders_in_text(text: str):
    hits = []
    for pat in PLACEHOLDER_PATTERNS:
        for m in pat.finditer(text):
            hits.append(m.group(0))
    return hits


def find_placeholders_in_obj(obj, path="$"):
    """Yield (path, placeholder_string) for each placeholder embedded in any string value."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from find_placeholders_in_obj(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from find_placeholders_in_obj(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        for hit in find_placeholders_in_text(obj):
            yield path, hit


def replace_placeholders_in_text(text: str) -> Tuple[str, List[str]]:
    """Replace placeholders in raw JSON-LD text. Returns (new_text, list_of_replacements_made)."""
    new_text = text
    replacements = []
    for needle, repl in PLACEHOLDER_REPLACEMENTS.items():
        if needle in new_text:
            count = new_text.count(needle)
            new_text = new_text.replace(needle, repl)
            replacements.append(f'replaced "{needle}" -> "{repl}" ({count}x)')
    return new_text, replacements


def validate_required(node: dict, type_name: str):
    """Return list of missing required field names."""
    required = REQUIRED_FIELDS.get(type_name, [])
    missing = [f for f in required if f not in node or node[f] in (None, "", [])]
    # LocalBusiness special-case: telephone OR url
    if type_name in ("LocalBusiness", "GeneralContractor", "HomeAndConstructionBusiness"):
        if not node.get("telephone") and not node.get("url"):
            missing.append("telephone|url")
    return missing


def main():
    files = find_html_files(PUBLIC_DIR)
    total_files = len(files)
    files_with_jsonld = 0
    files_without_jsonld = []
    total_blocks = 0

    type_counter = Counter()

    critical_placeholders = []   # list of dicts
    high_json_errors = []        # list of dicts
    medium_missing = []          # list of dicts
    low_inlanguage = []          # list of dicts

    fixes_applied = []           # list of dicts

    for path in files:
        try:
            html = path.read_text(encoding="utf-8")
        except Exception as e:
            high_json_errors.append({
                "file": str(path),
                "msg": f"could not read file: {e}",
                "line": 0,
            })
            continue

        rel = path.relative_to(PUBLIC_DIR)
        page_lang_code = page_lang(html)

        blocks = list(extract_jsonld_blocks(html))
        if not blocks:
            files_without_jsonld.append(str(rel))
            continue

        files_with_jsonld += 1
        total_blocks += len(blocks)

        # We may rewrite the HTML if we apply fixes; track changes.
        new_html = html
        page_modified = False

        for raw, offset in blocks:
            line = line_of_offset(html, offset)

            # 1. Detect placeholder leaks in raw block text BEFORE parsing
            raw_placeholder_hits = find_placeholders_in_text(raw)
            if raw_placeholder_hits:
                critical_placeholders.append({
                    "file": str(rel),
                    "line": line,
                    "hits": list(set(raw_placeholder_hits)),
                })

                # Apply auto-fix for known replaceable placeholders
                fixed_text, repls = replace_placeholders_in_text(raw)
                if repls:
                    new_html = new_html.replace(raw, fixed_text, 1)
                    page_modified = True
                    fixes_applied.append({
                        "file": str(rel),
                        "line": line,
                        "type": "placeholder",
                        "details": repls,
                    })
                    raw = fixed_text  # use fixed for subsequent JSON parse

            # 2. JSON syntax
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                high_json_errors.append({
                    "file": str(rel),
                    "line": line,
                    "msg": f"JSONDecodeError: {e.msg} at line {e.lineno} col {e.colno}",
                })
                continue

            # 3. Collect types for distribution
            seen_types = []
            collect_types(data, seen_types)
            for t in seen_types:
                type_counter[t] += 1

            # 4. For every typed node, check required fields
            for node in iter_typed_nodes(data):
                for tname in node_types(node):
                    if tname in REQUIRED_FIELDS:
                        missing = validate_required(node, tname)
                        if missing:
                            medium_missing.append({
                                "file": str(rel),
                                "line": line,
                                "type": tname,
                                "missing": missing,
                            })

                # 5. Check inLanguage vs page lang
                il = node.get("inLanguage")
                if il and page_lang_code:
                    il_short = str(il).split("-")[0].lower()
                    if il_short != page_lang_code:
                        low_inlanguage.append({
                            "file": str(rel),
                            "line": line,
                            "page_lang": page_lang_code,
                            "schema_lang": il,
                        })

        # If we modified placeholders, write file back
        if page_modified:
            try:
                path.write_text(new_html, encoding="utf-8")
            except Exception as e:
                fixes_applied.append({
                    "file": str(rel),
                    "line": 0,
                    "type": "WRITE-FAILED",
                    "details": [str(e)],
                })

    # ---------- write report ----------
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write("# Schema Validation Report\n\n")
        f.write("Generated: 2026-04-29\n\n")

        f.write("## Summary\n")
        f.write(f"- Total HTML files scanned: {total_files}\n")
        f.write(f"- Files with at least 1 JSON-LD: {files_with_jsonld}\n")
        f.write(f"- Files with NO JSON-LD: {len(files_without_jsonld)}\n")
        f.write(f"- Total JSON-LD blocks: {total_blocks}\n")
        total_errors = len(high_json_errors) + len(medium_missing) + len(low_inlanguage)
        f.write(f"- Validation errors: {total_errors}\n")
        f.write(f"- Placeholder leaks: {len(critical_placeholders)}\n\n")

        if files_without_jsonld:
            f.write("### Files with NO JSON-LD\n")
            for p in files_without_jsonld:
                f.write(f"- `{p}`\n")
            f.write("\n")

        f.write("## Errors by severity\n\n")

        f.write("### CRITICAL · placeholders in production\n")
        if critical_placeholders:
            for item in critical_placeholders:
                f.write(f"- `{item['file']}` (line {item['line']}): {', '.join(item['hits'])}\n")
        else:
            f.write("None.\n")
        f.write("\n")

        f.write("### HIGH · invalid JSON syntax\n")
        if high_json_errors:
            for item in high_json_errors:
                f.write(f"- `{item['file']}` (line {item.get('line',0)}): {item['msg']}\n")
        else:
            f.write("None.\n")
        f.write("\n")

        f.write("### MEDIUM · missing required fields\n")
        if medium_missing:
            grouped = defaultdict(list)
            for item in medium_missing:
                grouped[item["type"]].append(item)
            for tname, items in sorted(grouped.items()):
                f.write(f"\n**{tname}** ({len(items)})\n")
                for it in items:
                    f.write(f"- `{it['file']}` (line {it['line']}): missing {', '.join(it['missing'])}\n")
        else:
            f.write("None.\n")
        f.write("\n")

        f.write("### LOW · inconsistent inLanguage\n")
        if low_inlanguage:
            for item in low_inlanguage:
                f.write(
                    f"- `{item['file']}` (line {item['line']}): "
                    f"page lang `{item['page_lang']}`, schema inLanguage `{item['schema_lang']}`\n"
                )
        else:
            f.write("None.\n")
        f.write("\n")

        f.write("## Schema type distribution\n\n")
        f.write("| @type | Count |\n|---|---|\n")
        priority = [
            "Organization", "Service", "Article", "NewsArticle", "BlogPosting",
            "LocalBusiness", "GeneralContractor", "HomeAndConstructionBusiness",
            "RealEstateListing", "FAQPage", "BreadcrumbList", "CollectionPage",
            "WebSite", "WebPage", "Person", "Place", "PostalAddress", "GeoCoordinates",
            "Question", "Answer",
        ]
        seen = set()
        for k in priority:
            if k in type_counter:
                f.write(f"| {k} | {type_counter[k]} |\n")
                seen.add(k)
        for k, v in sorted(type_counter.items()):
            if k in seen:
                continue
            f.write(f"| {k} | {v} |\n")
        f.write("\n")

        f.write("## Fixes applied\n\n")
        if fixes_applied:
            for fix in fixes_applied:
                f.write(f"- `{fix['file']}` (line {fix['line']}, {fix['type']}): "
                        f"{'; '.join(fix['details'])}\n")
        else:
            f.write("No automatic fixes were applied.\n")
        f.write("\n")

        f.write("## Recommended fixes\n\n")
        rec = []
        n = 1
        if critical_placeholders:
            unfixed = [c for c in critical_placeholders if not any(
                fa["file"] == c["file"] and fa["line"] == c["line"] and fa["type"] == "placeholder"
                for fa in fixes_applied
            )]
            if unfixed:
                rec.append(f"{n}. Manually replace remaining placeholders that the auto-fixer "
                          f"cannot infer (e.g. `[XXX]`, `[INSERT...]`) with real values. "
                          f"Affected files: {', '.join(sorted({c['file'] for c in unfixed}))}.")
                n += 1
        if high_json_errors:
            rec.append(f"{n}. Repair JSON syntax in {len(high_json_errors)} block(s); "
                      f"these are silently ignored by Google.")
            n += 1
        if medium_missing:
            by_type = Counter(item["type"] for item in medium_missing)
            top = ", ".join(f"{t} ({c})" for t, c in by_type.most_common())
            rec.append(f"{n}. Backfill missing required properties: {top}.")
            n += 1
        if low_inlanguage:
            rec.append(f"{n}. Align `inLanguage` with `<html lang>` on {len(low_inlanguage)} block(s) "
                      f"to avoid hreflang/Schema mismatch signals.")
            n += 1
        if files_without_jsonld:
            rec.append(f"{n}. Add baseline JSON-LD (Organization or WebPage) to "
                      f"{len(files_without_jsonld)} page(s) currently shipping with no schema.")
            n += 1
        if not rec:
            rec.append("1. No issues detected. Site schema layer is clean.")
        f.write("\n".join(rec) + "\n")

    # Stdout summary for the caller
    print(f"Scanned {total_files} files; {total_blocks} JSON-LD blocks.")
    print(f"CRITICAL placeholders: {len(critical_placeholders)} | "
          f"HIGH json errors: {len(high_json_errors)} | "
          f"MEDIUM missing fields: {len(medium_missing)} | "
          f"LOW inLanguage: {len(low_inlanguage)}")
    print(f"Fixes applied: {len(fixes_applied)}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
