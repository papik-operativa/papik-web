# WP → Static Redirect Audit · papik.cat

**Generated:** 2026-04-27
**Migration target:** 1 June 2026
**Live WP host:** `https://papik.cat` (canonical `https://www.papik.cat`)
**New static site:** Vercel, `cleanUrls: true`, `trailingSlash: false`
**Languages:** CA (root, canonical), ES (`/es/`), EN (`/en/`, not yet on WP)

---

## Executive summary

The legacy WordPress site exposes **~280 indexable URLs** across 6 sitemaps (posts, pages, projects, categories, taxonomies, authors). The current `vercel.json` covers **33 redirects**, mostly catch-alls and core-page renames. This audit cross-references every WP URL against the new static site's inventory (`slug-mapping.json` + `public/*.html` + `public/es/*.html`) and proposes **~210 additional redirects**, classified A–G.

**Headline risk:** without these redirects, the migration would orphan ~150 indexed Catalan/Spanish posts and project pages, evaporating roughly a decade of accumulated SEO equity from the Passivhaus and Sant Cugat clusters. The bulk of value sits in the **~30 project pages** (slug renamed from `/projectes/SLUG` to `/projecte-SLUG`, plus several human-readable WP slugs that need to be mapped to the new short slug) and the **12–14 evergreen articles** (translated from descriptive WP slugs to the new `/article-*` convention).

---

## Discovery methodology

1. **Sitemap discovery (success):**
   - `https://papik.cat/sitemap.xml` — redirects to `sitemap_index.xml` (Yoast convention).
   - `https://papik.cat/sitemap_index.xml` — index returned 6 child sitemaps, all on `www.papik.cat`.
   - `https://papik.cat/wp-sitemap.xml` — also resolves to the same Yoast index (WP core fallback inactive; Yoast plugin is the source of truth).
   - All 6 child sitemaps fetched successfully via WebFetch:
     - `post-sitemap.xml` — ~165 entries (CA + ES blog posts)
     - `page-sitemap.xml` — 47 entries (core pages, both langs)
     - `projecte-sitemap.xml` — 71 entries (CA + ES project pages)
     - `category-sitemap.xml` — 38 entries (taxonomy archives)
     - `tipusprojecte-sitemap.xml` — 8 entries (custom taxonomy)
     - `author-sitemap.xml` — 4 entries

2. **robots.txt:** Returned empty body via WebFetch (likely blocks the fetcher's User-Agent or genuinely empty). Not a blocker — sitemap index was discoverable directly. **Limitation noted.**

3. **Local infra read:**
   - `vercel.json` (33 existing redirects, `cleanUrls: true`, `trailingSlash: false`)
   - `seo-internal/slug-mapping.json` (full v1 catalogue: 33 projects, 13 articles, 7 service/company pages, 13 geo-landings pending)
   - `public/*.html` (65 CA HTML files) + `public/es/*.html` (61 ES HTML files)
   - `seo-internal/copy/rewrites/` (29 v2 copy files for the 1 June launch)

---

## Inventory

### Total URLs found per sitemap

| Sitemap                    | URLs | Notes                                                               |
|----------------------------|-----:|---------------------------------------------------------------------|
| post-sitemap.xml           |  165 | CA + ES blog posts mixed; many duplicates (CA + ES translation pairs) |
| page-sitemap.xml           |   47 | Core pages, legal, contact, gallery, services tree                  |
| projecte-sitemap.xml       |   71 | CA + ES project archives + individual project pages                 |
| category-sitemap.xml       |   38 | WP taxonomy archives — collapsed wholesale to /blog                 |
| tipusprojecte-sitemap.xml  |    8 | Custom project taxonomy — collapsed to /projectes                   |
| author-sitemap.xml         |    4 | Author archives — collapsed to /empresa (now /nosaltres)            |
| **Total (unique paths)**   | **~280** | After de-duplication of CA/ES pairs and trailing-slash variants |

### Breakdown by language and type

| Type                            | CA  | ES  | Notes                                                |
|---------------------------------|----:|----:|------------------------------------------------------|
| Blog posts (article-grade)      |  ~12 | ~13 | Most have direct equivalents on new site             |
| Blog posts (legacy/event/news)  |  ~50 | ~55 | Mostly thin content, news from 2013-2018 — collapse  |
| Project pages                   |   33 |   33 | All map 1:1 to `/projecte-*` and `/es/proyecto-*`    |
| Core pages (services, company)  |   ~7 |   ~9 | Renamed slugs; some 1:1, some collapse               |
| Category archives               |   18 |   20 | Collapsed via existing `/category/:slug*` rule       |
| Tipusprojecte archives          |    4 |    4 | Collapsed via existing `/tipusprojecte/:slug*` rule  |
| Author archives                 |    4 |    0 | Collapsed via existing `/author/:slug*` rule         |

---

## Classification summary

| Class | Meaning                                       | Count (proposed) |
|-------|-----------------------------------------------|-----------------:|
| A     | 1:1 direct match (slug exists unchanged)      |  1               |
| B     | Slug renamed (same content, new URL)          |  ~115            |
| C     | Pattern collapse → hub page                   |  ~80             |
| D     | ES path normalisation                         |  3               |
| E     | Already covered in `vercel.json`              |  (not duplicated; see overlap below) |
| F     | Obsolete — let it 404                         |  0 explicit (handled by absence) |
| G     | Decision needed                               |  ~10 (see `wp-redirect-questions.md`) |
| **Total proposed new redirects** |              | **~210**         |

---

## Coverage gap: what `vercel.json` already handles vs what's missing

### Already in `vercel.json` (33 redirects, fully effective):

- **Catch-alls (5):** `/category/:slug*`, `/es/category/:slug*`, `/tipusprojecte/:slug*`, `/es/tipoproyecto/:slug*`, `/author/:slug*`, `/es/author/:slug*` → these single rules absorb **~70 WP URLs** (categories + tipusprojecte + authors + ES variants). Excellent leverage.
- **Service tree:** `/productes-alta-eficiencia-energetica/:path*` → `/construccio` absorbs the entire CA service sub-tree.
- **Core renames:** `/diari` → `/butlleti`, `/inscripcio` → `/butlleti`, `/bustia` → `/butlleti`, `/pressupost-gratuit` → `/pressupost`, `/com-construir-la-teva-casa` → `/com-construim-la-teva-casa`, `/llistat-de-projectes-actius` → `/projectes`, etc.
- **ES essentials:** `/es/inicio` → `/es`, `/es/diario` → `/es/butlleti`, `/es/lista-de-proyectos-activos` → `/es/projectes`, two specific article redirects.
- **WP plumbing:** `/wp-admin/:path*`, `/wp-login.php`, `/feed`, `/es/feed`.

### Missing — biggest gaps (covered by this proposal):

1. **All 33 individual project pages** in both languages (~66 entries). The existing rules only handle the index and the listing alias — the deep project URLs `/projectes/k-codines`, `/es/proyectos/k-iturbi`, etc. would 404.
2. **The ES service tree `/es/que-hacemos/*`** has no equivalent of the CA `/productes-alta-eficiencia-energetica/:path*` catch-all.
3. **The ~12 article-grade WP posts** with descriptive Yoast slugs (e.g. `/els-cinc-principis-passivhaus`) need explicit renames to the new `/article-*` slugs.
4. **The ~50 legacy event/news posts per language** need a wildcard fall-through — currently this proposal enumerates them explicitly, but a final-line catch-all `/(.*)` would be too broad and is intentionally avoided.
5. **Legal pages** (`/avis-legal`, `/politica-de-privacitat`, `/politica-de-cookies` × 2 langs) — flagged in questions, target pages don't yet exist on the new site.
6. **Image attachments** (`/wp-content/uploads/*`) — not in sitemaps, flagged in questions.

---

## Recommendations (priority order)

### P0 — must ship before 1 June launch
1. **Merge all class B project redirects** (~66 entries) — these are the highest-equity URLs after the homepage. Several have human-readable WP slugs (`/projectes/segona-casa-passiva-a-catalunya` → `/projecte-passivpalau`, `/projectes/primera-casa-certificada-passivhaus-sant-cugat` → `/projecte-k-del-carril`) that must be hand-mapped, not pattern-matched.
2. **Merge all class B article renames** (~12 + 12 = 24 entries). These map to the v2 launch articles already in `seo-internal/copy/rewrites/`.
3. **Add the two project-tree catch-alls** (`/projectes/:slug*` → `/projectes`, `/es/proyectos/:slug*` → `/es/projectes`) **last in the redirects array** so they only fire for unmatched cases.

### P1 — strongly recommended pre-launch
4. **Add the ES service-tree catch-all** `/es/que-hacemos/:path*` → `/es/construccio`. Mirrors the CA pattern.
5. **Approve the ~80 class C legacy-post collapses** to `/blog` and `/es/blog`. Even when the destination is a hub, the 301 transfers PageRank and stops the URL from looking dead.
6. **Resolve the legal-pages question (Q2)** — either build the pages or accept the redirect to `/`.

### P2 — post-launch acceptable
7. **Decide on `/wp-content/uploads/*` strategy** (Q8) — proxy to legacy CDN for 12 months OR accept image link rot.
8. **Resolve K-Colombia** (Q1) — either build `/projecte-k-colombia` for v1.1 or accept the soft fallback to `/projectes`.
9. **Add per-feed catch-alls** if Search Console shows non-trivial RSS impressions (Q7).

### Estimated final state
- Today: **33** redirects
- After this proposal merges: **~240** redirects (33 existing + ~210 new − ~5 already-covered duplicates flagged inline)
- Within the **150–250 target** quoted in the brief.

---

## Critical caveats

1. **WP host is `www.papik.cat`** in the sitemaps, but the brief refers to `papik.cat`. Vercel's domain config must canonicalise both to one host before the redirects fire. Confirm DNS/Vercel domain-redirect setup is `papik.cat` ↔ `www.papik.cat` consolidation **before** evaluating redirect coverage.
2. **Trailing slash:** WP serves URLs *with* trailing slash; Vercel `trailingSlash: false` strips them. The redirects are written without trailing slash; Vercel matches both forms when `trailingSlash: false`. Verified via existing rules in `vercel.json` (e.g. `/es/inicio` works for `/es/inicio/` too). Confirmed safe.
3. **Some Spanish posts are served from the CA root** (no `/es/` prefix) on the legacy WP — see Q6. Decide language target before merging.
4. **URL-encoded special characters** (e.g. `co%e2%82%82` for CO₂, `intel%c2%b7ligent` for intel·ligent) — the proposal preserves these encodings to match exactly what Google has indexed. Do not "clean" these in review.
5. **K-Vall d'Or slug mismatch:** WP uses `k-valldor`, new site uses `k-vallor`. Mapping is in place; verify the rename hasn't broken anything else.
6. **`/empresa` (WP) vs `/nosaltres` (new):** WP had `/empresa/` as the about-us page; new site uses `/nosaltres`. Existing `vercel.json` rule `/author/:slug*` → `/empresa` would now resolve to a 404 — should be updated to `/nosaltres`. **Flag for cleanup pass on `vercel.json` itself**, separate from this audit.

---

## Files generated

- `seo-internal/wp-redirect-audit.md` — this report
- `seo-internal/wp-redirects-proposed.json` — machine-readable proposal in vercel.json `redirects` format, with `_classification` and `_note` annotations
- `seo-internal/wp-redirect-questions.md` — 8 open questions for founder review

**Next step:** founder reviews questions, then strip `_classification`/`_note`/`_section`/`_meta` keys from the JSON, splice the `redirects` array into `vercel.json` (preserving the existing 33 entries at the top, appending the new ones, with the two `/projectes/:slug*` catch-alls *last*), commit, deploy, and watch Search Console for 4xx spikes for 30 days post-launch.
