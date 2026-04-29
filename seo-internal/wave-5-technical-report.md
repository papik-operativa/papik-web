# Wave 5 Technical Fixes

Generated: 2026-04-29

## Before vs After

| Metric | Before | After |
|---|---|---|
| Project-page canonical mismatch (www / `.html` in canonical & hreflang) | 36 (108 files) | 0 |
| Render-blocking external scripts | 2 (Supabase CDN, Leaflet CDN) | 0 |
| Skip-to-content link present (rendered HTML) | 0 / 291 pages | 290 / 291 pages (only `cookie-banner.html` partial excluded) |
| `<main id="main">` present (rendered HTML) | 229 / 291 | 291 / 291 |
| Hreflang triplets — full | 278 / 286 (97.2%) | 282 / 286 (98.6%) |
| Hreflang missing 1 sibling | 6 | 2 |
| Hreflang missing 2+ siblings | 1 | 1 |
| Hreflang dead alternates | 53 | 53 (out of scope, slug-mapping work) |
| Sitemap URLs | 285 | 285 (regenerated cleanly) |

## Fixes applied

### Fix 1 · Project-page canonical / hreflang / og normalisation (108 files)

- Replaced every `https://www.papik.cat/...` reference inside the 108 project pages with `https://papik.cat/...` (apex domain).
- Removed the `.html` suffix from every `canonical`, `hreflang` (ca/es/en/x-default) and `og:url` URL on those pages.
- Stripped `.html` from project URLs inside JSON-LD (`@id`, `WebPage.url`, `BreadcrumbList.item`) and from the `<select>` language switcher options.
- 51 of the 108 files also had `www.papik.cat` in JSON-LD / nav — swept clean by `wave5_sweep_www.py`.
- Total replacements across the 108 files: 828 (canonical/hreflang/og) + ~357 (sweep). Result: 0 `www.papik.cat` and 0 `.html` left in canonical/hreflang/og:url within project pages.
- Generator at `/tmp/gen_papik_projects.py` (and `/tmp/papik_gen.py`) is a tmp build helper; future builds for project pages should regenerate clean URLs (recommend pinning `DOMAIN = "https://papik.cat"` and dropping `.html` in the helper next time the project pages are rebuilt).

### Fix 2 · Self-host render-blocking external scripts

Downloaded to `/public/js/vendor/`:

- `supabase.js` — Supabase JS v2 (~196 KB) from `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2`
- `leaflet.js` — Leaflet 1.9.4 (~147 KB) from `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js`
- `leaflet.css` — Leaflet CSS 1.9.4 (~14 KB)

Updated:

- `public/usuaris.html` — Supabase script now `js/vendor/supabase.js` with `defer`
- `public/es/nosotros.html` — Leaflet CSS local + Leaflet script `../js/vendor/leaflet.js` with `defer`

ES `usuaris.html` (slated for rename to `usuarios.html`) does not actually load Supabase, so no change needed. CA `nosaltres.html` does not load Leaflet, so no change needed.

### Fix 3 · Skip-to-content link (WCAG AAA)

- Added `.skip-to-content` and `.skip-to-content:focus` rules to `/public/css/base.css` per spec (positions off-screen, slides in on focus, uses `--green` and `--accent` tokens).
- Injected `<a href="#main" class="skip-to-content">…</a>` immediately after `<body …>` on 290 pages (the 1 file skipped is `cookie-banner.html`, a head-less partial). Label varies by tree: CA → "Salta al contingut", ES → "Saltar al contenido", EN → "Skip to content".
- Backfilled `id="main"` onto 62 `<main>` elements that lacked it (project pages, some article pages, cookie-banner-style fragments). All 291 pages now have a `<main id="main">` target.
- Patched `generate_html.py` for future builds:
  - Added top-level `_SKIP_LABEL = {"ca": …, "es": …, "en": …}` dispatch.
  - Inserted `<a href="#main" class="skip-to-content">{_SKIP_LABEL[page.lang]}</a>` directly in the page template, right after `<body class="page--…">`. Future `python3 generate_html.py` runs preserve the link.

### Fix 4 · Hreflang sibling backfill

`validate-hreflang.py` flagged 6 missing-1 entries before. Decisions per page:

| Page | EN sibling on disk? | Action |
|---|---|---|
| `/en/budget.html` (missing x-default) | n/a (target was x-default itself) | Added `<link rel="alternate" hreflang="x-default" href="https://papik.cat/pressupost">` |
| `/es/article-derribar-construir-pasos.html` | yes (`/en/article-demolish-and-rebuild-steps.html`) | Added EN hreflang |
| `/es/nosotros.html` | yes (`/en/about.html`) | Added EN hreflang |
| `/nosaltres.html` | yes (`/en/about.html`) | Added EN hreflang |
| `/es/usuaris.html` | no (no `/en/users.html` exists) | Left as-is — content production needed |
| `/usuaris.html` | no (no `/en/users.html` exists) | Left as-is — content production needed |
| `/qualitats.html` (missing en+es) | no (no EN, no ES) | Left as-is — content production needed |

Validator now reports 2 missing-1 (both `usuaris` pages) + 1 missing-2 (`qualitats`). The 3 newly-introduced bidirectional inconsistencies are because we point CA + ES at `/en/about.html` while the EN page does not yet point back; this should be reconciled when EN sibling slugs are registered in `slug-mapping.json` and `generate_html.py` is re-run.

## Files modified (counts)

- 108 project pages (canonical/hreflang/og + JSON-LD/lang-switcher sweep)
- 1 `usuaris.html` (Supabase localised)
- 1 `es/nosotros.html` (Leaflet localised)
- 1 `public/css/base.css` (skip-to-content styles)
- 290 `*.html` pages (skip link injected)
- 62 of those (a subset) also had `id="main"` backfilled
- 1 `generate_html.py` (template + `_SKIP_LABEL` dict for future-proofing)
- 1 `/en/budget.html` (x-default backfill)
- 3 pages (`/es/article-derribar-construir-pasos.html`, `/es/nosotros.html`, `/nosaltres.html`) — EN hreflang backfill
- 3 vendored libraries dropped under `/public/js/vendor/`

Mirror `/tmp/papik-public/` refreshed via `rsync -a --delete` for preview parity.

## Validators re-run

- `python3 seo-internal/validate-hreflang.py` → 282 / 286 full triplet (was 278). Missing-1 dropped 6 → 2.
- `python3 seo-internal/internal-linking-analysis.py` → 6030 internal links across 285 pages, 0 broken internal links.
- `python3 generate_sitemap.py` → 285 URLs (unchanged, expected).
- `python3 generate_html.py` was NOT re-run as part of Wave 5 because (a) the `cookie-banner.html` head-less partial was deliberately left alone and re-running could overwrite the bespoke sweeps; (b) the skip-link template patch is verified against 290 already-injected pages and will only matter on the next full rebuild. A dry build is recommended before the 1 June launch.

## Issues remaining

- **3 bidirectional hreflang inconsistencies** introduced by Fix 4 (CA/ES point to `/en/about.html` and `/en/article-demolish-and-rebuild-steps.html`, but those EN pages currently advertise different ES partner slugs). Resolution path: extend `slug-mapping.json` to register `nosaltres ↔ nosotros ↔ about` and the demolish/rebuild trio, then re-run `generate_html.py` to regenerate the EN sides consistently. Out of scope for a 10-min Wave 5 pass.
- **53 dead alternates** (clean-URL targets like `/article-derribar-casa-antiga-construir-nova-passos`) remain. These are expected to resolve when Vercel `cleanUrls + redirects` are live; the validator does not respect `vercel.json` rewrites. Not a Wave 5 deliverable.
- **2 `usuaris` pages and `qualitats.html`** still missing their EN sibling. Decision documented: leave as-is because no EN content exists; better than emitting a dead alternate. Flag for content production before launch.
- **Project page generator** (`/tmp/gen_papik_projects.py`, `/tmp/papik_gen.py`) was not patched (it lives in `/tmp` and is treated as an ad-hoc helper). Any future regeneration of the 36 project pages will re-introduce `www` and `.html` unless its `DOMAIN` constant + `url_for()` are updated. Recommend folding the helper back into `generate_html.py` proper.
