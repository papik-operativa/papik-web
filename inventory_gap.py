"""
Inventari Fase 0 · diff entre slug-mapping.json (font de veritat declarada)
i la realitat de papik-final/public/.

Output: inventory-gap.csv amb una fila per (page_id, locale) i columnes
per existència, schema, hreflang, copy markdown disponible i acció proposada.

També imprimeix un resum agregat.
"""

import csv
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAPPING = ROOT / "seo-internal" / "slug-mapping.json"
PUBLIC = ROOT / "public"
COPY = ROOT / "seo-internal" / "copy"
OUT_CSV = ROOT / "inventory-gap.csv"


def url_to_filepath(url: str) -> Path:
    """Resolve a sitemap-style URL to its expected .html path under public/."""
    u = url.strip()
    if not u or u == "/":
        return PUBLIC / "index.html"
    if u.endswith("/"):
        return PUBLIC / u.lstrip("/").rstrip("/") / "index.html"
    return PUBLIC / (u.lstrip("/") + ".html")


def detect_schema_and_hreflang(path: Path) -> tuple[int, int]:
    if not path.is_file():
        return (0, 0)
    text = path.read_text(encoding="utf-8", errors="ignore")
    schemas = len(re.findall(r'application/ld\+json', text))
    hreflangs = len(re.findall(r'hreflang', text))
    return schemas, hreflangs


def url_slug(url: str) -> str:
    """Extract the last path segment of a URL (without locale prefix)."""
    u = url.strip().strip("/")
    parts = [p for p in u.split("/") if p and p not in ("es", "en")]
    return parts[-1] if parts else ""


# Build a one-shot index of all markdown copy files, keyed by stem-without-locale-and-version.
def _build_copy_index() -> dict[str, list[Path]]:
    idx: dict[str, list[Path]] = {}
    if not COPY.is_dir():
        return idx
    for p in COPY.rglob("*.md"):
        stem = p.stem
        # strip trailing -ca / -es / -en / -v2 / -v3 (in any combo, repeatedly)
        for suffix in ("-v2", "-v3", "-ca", "-es", "-en"):
            while stem.endswith(suffix):
                stem = stem[: -len(suffix)]
        # also strip leading "article-" so id `petjada-ecologica` matches `article-petjada-ecologica-...md`
        normalized = stem
        idx.setdefault(stem, []).append(p)
        if stem.startswith("article-"):
            short = stem[len("article-"):]
            idx.setdefault(short, []).append(p)
    return idx


_COPY_INDEX = _build_copy_index()


def find_copy_markdown(page_id: str, url: str, locale: str, page_type: str) -> str | None:
    """Resolve the markdown copy file for a slug+locale by stem matching."""
    candidates_keys = []
    slug = url_slug(url)
    # Try by URL slug first (most reliable), then by id, then by id with prefix stripped
    for key in (slug, page_id, page_id.replace("zones-", ""), page_id.replace("article-", "")):
        if key and key not in candidates_keys:
            candidates_keys.append(key)

    for key in candidates_keys:
        matches = _COPY_INDEX.get(key, [])
        # Filter by locale
        loc_matches = []
        for m in matches:
            name = m.name
            if locale == "ca":
                # CA files don't live under translations/
                if "translations/" in str(m).replace("\\", "/"):
                    continue
                if "-ca" in name or name.endswith("-v2.md") or name.endswith(".md"):
                    loc_matches.append(m)
            elif locale == "es":
                if "/translations/es/" in str(m).replace("\\", "/"):
                    loc_matches.append(m)
            elif locale == "en":
                if "/translations/en/" in str(m).replace("\\", "/"):
                    loc_matches.append(m)
        if loc_matches:
            # Prefer v2 over v1
            loc_matches.sort(key=lambda p: ("-v2" not in p.name, p.name))
            return str(loc_matches[0].relative_to(ROOT))
    return None


def main():
    data = json.loads(MAPPING.read_text(encoding="utf-8"))
    rows = []
    summary = {
        "total_entries": 0,
        "exists_ca": 0, "exists_es": 0, "exists_en": 0,
        "schema_ca": 0, "schema_es": 0, "schema_en": 0,
        "hreflang_ca": 0, "hreflang_es": 0, "hreflang_en": 0,
        "copy_ca": 0, "copy_es": 0, "copy_en": 0,
    }
    locales = ("ca", "es", "en")

    for page in data["pages"]:
        pid = page["id"]
        ptype = page.get("type", "?")
        for loc in locales:
            url = page.get(loc)
            if not url:
                continue
            summary["total_entries"] += 1
            fp = url_to_filepath(url)
            exists = fp.is_file()
            schemas, hreflangs = detect_schema_and_hreflang(fp) if exists else (0, 0)
            copy_md = find_copy_markdown(pid, url, loc, ptype)

            if exists:
                summary[f"exists_{loc}"] += 1
                if schemas > 0:
                    summary[f"schema_{loc}"] += 1
                if hreflangs > 0:
                    summary[f"hreflang_{loc}"] += 1
            if copy_md:
                summary[f"copy_{loc}"] += 1

            # Action heuristic
            if not exists and copy_md:
                action = "GENERATE"
            elif not exists and not copy_md:
                action = "BLOCKED:no-copy"
            elif exists and (schemas == 0 or hreflangs == 0):
                action = "REBUILD:add-schema-hreflang"
            else:
                action = "OK"

            rows.append({
                "page_id": pid,
                "type": ptype,
                "locale": loc,
                "url": url,
                "expected_file": str(fp.relative_to(ROOT)),
                "exists": exists,
                "schemas": schemas,
                "hreflangs": hreflangs,
                "copy_md": copy_md or "",
                "action": action,
            })

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV.relative_to(ROOT)}")
    print()
    print("=== Summary per locale ===")
    print(f"{'locale':<8} {'declared':>10} {'exists':>8} {'has_schema':>12} {'has_hreflang':>14} {'copy_avail':>12}")
    for loc in locales:
        declared = sum(1 for r in rows if r["locale"] == loc)
        print(
            f"{loc:<8} {declared:>10} "
            f"{summary[f'exists_{loc}']:>8} "
            f"{summary[f'schema_{loc}']:>12} "
            f"{summary[f'hreflang_{loc}']:>14} "
            f"{summary[f'copy_{loc}']:>12}"
        )

    print()
    print("=== Action breakdown ===")
    actions = {}
    for r in rows:
        actions.setdefault(r["action"], 0)
        actions[r["action"]] += 1
    for a, n in sorted(actions.items(), key=lambda x: -x[1]):
        print(f"  {a}: {n}")

    print()
    print("=== BLOCKED:no-copy entries (need copy or scope cut) ===")
    blocked = [r for r in rows if r["action"] == "BLOCKED:no-copy"]
    for r in blocked[:30]:
        print(f"  {r['locale']}  {r['page_id']:<40} ({r['type']})  url={r['url']}")
    if len(blocked) > 30:
        print(f"  ... and {len(blocked) - 30} more")


if __name__ == "__main__":
    main()
