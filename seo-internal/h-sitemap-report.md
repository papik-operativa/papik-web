# Sitemap Regeneration Report — PAPIK Group

Generated: 2026-04-27
Source: `/public/**/*.html` (filesystem walk)
Output: `/public/sitemap.xml`
Generator: `generate_sitemap.py` (rewritten — was slug-mapping-driven, now filesystem-driven with slug-mapping fallback for hreflang)

---

## Summary

- **Total URLs in sitemap:** 178
- **Well-formed XML:** YES (parses cleanly with `xml.etree.ElementTree`)
- **All `<loc>` absolute under `https://papik.cat/`:** YES (0 violations)
- **Duplicate `<loc>` entries:** 0
- **Hreflang triplet completeness:**
  - Complete (CA + ES + EN + x-default): **74 / 178 (41.6%)**
  - Incomplete (missing one or more siblings): **104 / 178 (58.4%)**

---

## Breakdown by language (`<loc>` path prefix)

| Language | URLs |
| --- | ---: |
| CA (root) | 74 |
| ES (`/es/...`) | 72 |
| EN (`/en/...`) | 32 |

EN is under-built relative to CA/ES — this is the main driver of the 58 % incomplete-triplet figure.

## Breakdown by `<priority>`

| Priority | Page type | URLs |
| --- | --- | ---: |
| 1.0 | Homepages (CA / ES / EN) | 3 |
| 0.9 | Tier 1 services and key landings | 17 |
| 0.8 | Tier 2 landings, comarcal hubs, zonals | 22 |
| 0.7 | Articles + general mid-tier | 59 |
| 0.6 | Project pages | 72 |
| 0.3 | Legal placeholders | 5 |

## Breakdown by `<changefreq>`

- weekly  — homepages, services, key landings, blog/projectes hubs
- monthly — articles, projects, zonal/comarcal landings
- yearly  — legal pages

---

## Validation Results

| Check | Result |
| --- | --- |
| XML well-formed | PASS |
| `<urlset>` namespaces correct (`sitemaps.org/schemas/sitemap/0.9` + `xhtml`) | PASS |
| All `<loc>` absolute (`https://papik.cat/...`) | PASS (178 / 178) |
| No duplicate `<loc>` | PASS |
| Each URL has at least one hreflang alternate | PASS |
| Each URL has full triplet (CA + ES + EN + x-default) | PARTIAL (74 / 178) |

---

## URLs missing hreflang siblings

Grouped by which sibling languages are absent.

### Missing only EN — 99 URLs

EN HTML version not yet built. This is expected per `slug-mapping.json` (most EN pages are still `to-create-S4` or `en-pending`).

Highlights:
- All articles (CA + ES, but no EN equivalent built yet)
- All projects (CA + ES, but no EN equivalent built yet)
- `/blog`, `/es/blog`, `/nosaltres`, `/es/nosotros` (CA + ES exist, EN pending)

### Missing EN + ES — 2 URLs
- `/projectes` (CA only — ES exists at `/es/projectes` but slug-map flags it as rename-pending to `/es/proyectos`; the parser only sees the published file)
- `/qualitats` (CA only — ES `/es/calidades` and EN `/en/qualities` not yet built)

### Missing CA + ES + EN (orphans on the CA/ES side) — 3 URLs
- `/usuaris` (no slug-mapping entry, no canonical/hreflang in HTML; treated as standalone CA page)
- `/es/usuaris` (legacy ES file using CA slug; rename-pending to `/es/usuarios`)
- `/es/projectes` (legacy ES file using CA slug; rename-pending to `/es/proyectos`)

> Note: these "orphans" are still emitted to the sitemap with self-canonical so search engines can discover them. They will gain hreflang siblings once the rename batch lands or once they are added to `slug-mapping.json`.

---

## Notes for the next pass

1. **Rename pending in `/es/`** — `slug-mapping.json._pending_renames` lists 8 ES pages still using Catalan slugs (`construccio`, `promocio`, `rehabilitacio`, `patrimonis`, `nosaltres`, `projectes`, `usuaris`, `pressupost`). Once renamed on disk, the sitemap will pick them up automatically; some hreflang triplets will shift from "missing ES" to "complete" without code changes.
2. **EN backfill is the biggest lever** — adding EN HTML for blog, articles, projects, services would push triplet completeness from 41 % toward ~95 %.
3. **`/usuaris` orphan** — file exists in both CA and ES but is missing from `slug-mapping.json`. Consider either adding it (with `noindex`) or excluding it explicitly via `EXCLUDE_FILENAMES` in `generate_sitemap.py` if it is not meant to be public.
4. **`comarques/` and `es/comarcas/` and `en/regions/` directories exist but are empty** — the script walks them safely; no entries emitted yet. They will populate automatically once Agent D builds the comarcal hubs.

---

## Generator behavior

The new `generate_sitemap.py`:

- Walks `/public/`, `/public/zones/`, `/public/comarques/`, `/public/es/`, `/public/es/zonas/`, `/public/es/comarcas/`, `/public/en/`, `/public/en/areas/`, `/public/en/regions/`, `/public/en/retrofit/`.
- Excludes `dashboard-cliente.html`, `_t.html`, `cookie-banner.html`.
- For each file, extracts `<link rel="canonical">` and `<link rel="alternate" hreflang="...">` from the HTML head.
- Falls back to filesystem-derived canonical (Vercel cleanUrls) and `slug-mapping.json` hreflang siblings when the HTML lacks tags.
- Reads `<meta property="article:modified_time">` for `<lastmod>`; falls back to file mtime.
- Classifies pages into priority tiers (1.0 / 0.9 / 0.8 / 0.7 / 0.6 / 0.3) and changefreq buckets (weekly / monthly / yearly).
- Sorts output by priority desc, then canonical asc.
- Writes to `/public/sitemap.xml` (or stdout with `--dry-run`).
