# S5 QA Pre-launch Report

Generated: 2026-04-28 · Scope: 180 HTML files (CA + ES + EN) + sitemap + robots + vercel.json
Tooling: `seo-internal/qa-script.py` (static analyzer, no browser/JS execution)
Findings dump: `seo-internal/qa-findings.json`

> Note on scope: the brief stated "90 HTML files"; the actual in-scope tree contains
> 180 (71 CA root + 4 CA zones + 73 ES root + 4 ES zonas + 23 EN root + 4 EN areas
> + 1 EN retrofit). All 180 were scanned. Some of those are expected non-public
> pages (e.g. `_t.html`, `dashboard-cliente.html`).

## Executive Summary

- 180 HTML files scanned, 6,744 internal links and 7 external links extracted.
- 1,698 issues raised: **9 P0 / 679 P1 / 811 P2 / 199 P3**.
- After triage of false positives (intentional `noindex` on dashboards, scratch
  file `_t.html`), the real launch blockers reduce to **5 P0** plus a small
  cluster of high-impact P1s (broken navigation links on the 12 zone landings,
  missing EN hreflang on a swath of CA/ES articles, missing JSON-LD on 90 ES
  project + utility pages).
- **Verdict: NOT yet ready to launch on 1 June 2026.** The site is structurally
  sound but P0 H1-missing issues and zone-landing broken nav links are visible
  to crawlers and users on day one. Realistic time to a green build: 1.5-2
  engineering days plus a re-run of this script.

## Severity classification

- **P0 critical** — blocks launch (must fix before deploy)
- **P1 high** — should fix before deploy (visible UX/SEO impact)
- **P2 medium** — fix in week 1 post-launch
- **P3 low** — nice-to-have, schedule later

---

## Per-section findings

### 1. HTML structural — 7 P0, 5 P1, 90 P2

P0 (must fix):
- `public/_t.html` — scratch/test file, missing `<html lang>`, `<meta charset>`,
  `<title>`, `<h1>`. **Recommendation: delete or move out of `/public/` before
  deploy** (it will otherwise be crawled).
- `public/es/construccio.html` — missing `<h1>`. (This file is the legacy
  CA-named slug duplicated under `/es/`; either remove it in favour of
  `construccion.html` or add an H1.)
- `public/es/promocio.html` — missing `<h1>`. Same pattern.
- `public/es/rehabilitacio.html` — missing `<h1>`. Same pattern.

P1:
- 5 files report multiple `<h1>` tags. Should be condensed to one canonical H1
  per page (full list in `qa-findings.json`).

P2 (90 issues, defer to week 1):
- `<title>` lengths 66-78 chars on ~10 long-form articles (e.g.
  `article-sostenibilitat-passivhaus.html`, `article-derribar-construir-passos.html`).
- `<meta description>` lengths 166-192 chars on ~12 articles. Trim to ≤165.
- A handful of heading-hierarchy skips (H2 → H4) — cosmetic SEO impact.

### 2. SEO meta — 2 P0, 203 P1, 41 P2

P0:
- `public/dashboard-cliente.html` and `public/es/dashboard-cliente.html` carry
  `<meta name="robots" content="noindex, nofollow">`. **This is intentional
  for the logged-in user dashboard and should NOT be removed.** Reclassify as
  P3 / informational in the script's next pass.

P1 (the real backlog — 203 issues, ~113 unique files):
- ~90 CA + ES articles are missing the EN hreflang entry. Examples:
  `article-apagada-2025.html`, `article-derribar-construir-passos.html`,
  `article-innovacions-passivhaus.html`, `article-tecnologies-passivhaus.html`.
  These articles do not yet have an EN sibling, so either (a) ship the EN
  translations or (b) add `hreflang="x-default"` only and remove the broken EN
  alternates.
- Some files are missing the canonical link (`_t.html`, a few utilities).
- `blog.html` and `dashboard-cliente.html` lack any hreflang triplet.

P2 (41): Open Graph or Twitter card meta partially missing on legacy pages
(typically missing `og:locale`, `twitter:title`, or `og:type`).

### 3. JSON-LD — 90 P1, 6 P2, 3 P3

P1 — 90 pages have **no JSON-LD `<script>` at all**. Pattern:
- All ~50 ES `proyecto-*.html` project pages.
- All four ES `zonas/*.html` landings (the CA/EN siblings have JSON-LD; ES
  was apparently missed).
- ES utility pages: `blog.html`, `nosaltres.html`, `pressupost.html`,
  `projectes.html`, `promocio.html`, `patrimonis.html`, `construccio.html`,
  `dashboard-cliente.html`.

P2 (6): a handful of pages have JSON-LD but the `@type` does not match the
expected page archetype (e.g. an article page emitting only `BreadcrumbList`).

P3 (3): pages without `BreadcrumbList` graph entry (recommended sitewide).

No `[XXX]` / `[FECHA REAL]` placeholder leaks were detected in production
JSON-LD output.

### 4. Hreflang triplet integrity — 237 P2

The hreflang URLs in `<head>` reference `https://papik.cat/...` (the legacy
domain). The static analyzer correctly flags that those URLs do not resolve to
files in `/public/` because the domain prefix differs from the new
`papikgroup.com` canonical.

Two distinct issues hide here:

1. **Domain mismatch (cosmetic):** the hreflang generator is still emitting
   `papik.cat` instead of `papikgroup.com`. Fix the generator constant before
   deploy.
2. **Triplet completeness:** for ~30 articles only the CA + ES pair exists; the
   EN file has not been built yet. Decide whether to ship the EN translations
   pre-launch or drop the EN hreflang alternate and rely on `x-default` until
   the translation lands.

### 5. Internal link integrity — 372 P1

Repeating offenders:

- **All 12 zone/zonas/areas landings** carry a navigation block with relative
  links that don't resolve when served from a sub-folder. Examples in
  `public/zones/bellaterra.html`: `index.html`, `about.html`, `projects.html`,
  `blog.html`, `construction.html`. These were authored with EN slugs but
  placed inside a CA folder, so the relative paths break. Fix: make these
  links absolute (`/index.html`, `/projectes.html`, etc.) or fix the
  per-language link table.
- ~10 broken links per file in `public/en/article-ecological-footprint.html`
  and `public/en/retrofit/communities.html` — same root cause (relative paths
  authored against the wrong folder depth).
- A few orphaned legacy slug links sitewide:
  `/article-derribar-casa-antiga-construir-nova-passos` (4 occurrences),
  `/eskimohaus`, `/politica-de-privacitat`, `/politica-de-cookies` in
  `avis-legal.html`. Either add these to `vercel.json` redirects or rewrite
  the source link.

### 6. Sitemap + robots — 9 P1, 0 P0

- `sitemap.xml` is well-formed and contains hreflang `<xhtml:link>` annotations.
- All 9 sample sitemap URLs (`/construccio`, `/promocio`, `/rehabilitacio`,
  `/patrimonis`, `/nosaltres`, `/qualitats`, `/projectes`, `/blog`,
  `/pressupost`) point to extension-less paths (no `.html`). On Vercel that's
  fine **iff** the build maps clean URLs; confirm `vercel.json` `cleanUrls:
  true` or equivalent rewrite is present (the candidate file mentioned in the
  brief, `vercel.json.candidate`, was not found; only `vercel.json` exists).
- `robots.txt` exists and references the sitemap. Does not explicitly disallow
  `/wp-admin` (low concern — site no longer runs WordPress).

### 7. Accessibility — 348 P2, 180 P3

- 180 P3: every page lacks a "skip to content" link. Recommend adding once to
  the shared header partial.
- ~340 P2: form inputs without label and icon-only buttons without
  `aria-label`. Concentrated in the newsletter/search form repeated across
  blog headers, and in social-icon button rows in the footer. A single-pass
  fix in the shared partial will clear the bulk of these.

Static analyzer cannot evaluate color contrast — see manual QA list.

### 8. Performance — 89 P2, 4 P3

- 89 P2: blocking `<script src>` without `defer` or `async`. Mostly
  `splash.js`, `cursor.js`, `supabase-auth.js`, `dashboard-guard.js`. Add
  `defer` on all of them; the splash/cursor are visual-effect scripts that
  should not block first paint.
- 4 P3: pages with 3+ inline `<style>` blocks (consolidate to external CSS
  during the next CSS pass).
- Plenty of `.png` references in articles — recommend WebP/AVIF conversion
  during a future image-pipeline pass.

### 9. Cross-lang consistency — 12 P3

12 sibling sets show ≥6 heading divergence, all on long-form pages:

- `comunitats.html`: CA 31 / ES 23 headings.
- `construccio.html`: CA 37 / ES 31 / EN 37.
- `rehabilitacio.html`: CA 31 / ES 23 / EN 31.
- `patrimonis.html`: CA 25 / ES 17 / EN 18.
- `promocio.html`: CA 23 / ES 16 / EN 23.
- `pressupost.html`: CA 4 / ES 26 (extreme — likely two different page
  templates).
- `blog.html`: CA 50 / ES 36.

The pattern (ES short, CA/EN long) suggests the ES versions are partially
truncated translations or built from an older template. Recommend a content
review for each before launch.

---

## Recommended fix order

### 1. P0 — block launch (4 real fixes, ~30 min)

1. Delete or move `public/_t.html` (test/scratch file).
2. Add `<h1>` to `public/es/construccio.html`, `public/es/promocio.html`,
   `public/es/rehabilitacio.html` — or remove these duplicate-slug files in
   favour of the proper ES slugs (`construccion.html`, `promocion.html`,
   `rehabilitacion.html`).
3. Confirm `noindex, nofollow` on `dashboard-cliente.html` is intentional (it
   is) and tag the QA script to ignore those two paths going forward.

### 2. P1 — recommended before launch (~1.5 days)

1. Fix relative navigation in all 12 zone/zonas/areas landings (turn
   `index.html` into `/index.html`, etc.). Single shared partial fix.
2. Add JSON-LD to the 90 ES pages missing it (use existing
   `seo-internal/schemas/` templates, fill from page metadata).
3. Repair the hreflang generator: emit `papikgroup.com` not `papik.cat`.
4. For ~30 articles missing EN translations, either ship the EN files or
   remove the EN hreflang alternate and emit `x-default` only.
5. Resolve the orphaned legacy slugs in
   `article-llicencia-derribo-cerdanyola-bellaterra.html`,
   `article-substituir-vs-rehabilitar.html`, `avis-legal.html` — either
   author redirects in `vercel.json` or fix the in-page `<a href>`.

### 3. P2 — week 1 post-launch

1. Add `defer` to all non-critical `<script src>` tags (splash, cursor, auth).
2. Fix label/aria-label on shared header newsletter form and footer social
   icons.
3. Trim `<title>` and `<meta description>` on the long-form articles to land
   inside the SEO ideal range.
4. Backfill missing OG / Twitter card meta on legacy pages.
5. Rewrite the few hreflang entries pointing to non-existent files.

### 4. P3 — scheduled

1. Add a "skip to content" link in the shared header partial.
2. Add `BreadcrumbList` JSON-LD to the small set of pages still missing it.
3. Cross-lang content review for the 12 pages with heading-count divergence;
   close translation gaps.
4. WebP/AVIF image pipeline migration.
5. Empty-alt images audit (decorative vs. content) for ~180 occurrences.

---

## Manual QA items (cannot validate statically)

- Color contrast (use Lighthouse / axe DevTools in browser).
- Mobile responsiveness (use device emulator or real iOS / Android).
- JS form interactions (newsletter signup, contact form, configurator).
- Real-world page load performance (Lighthouse on 3G + 4G profiles).
- Visual design coherence across pages.
- Real-world Vercel routing (clean URLs, redirects from
  `vercel.json` `redirects` array).
- Configurator interactive flow + conversion path.

## Validation tools to run before deploy

- [ ] `vercel dev` locally + crawl 20 random pages with `wget --spider -r`
- [ ] Lighthouse audit on 5 representative pages (homepage, service, article,
      landing, legal)
- [ ] Google Rich Results Test on 1 article + 1 landing
- [ ] Mobile-Friendly Test
- [ ] axe DevTools accessibility scan on homepage + service page + landing
- [ ] Re-run `python3 seo-internal/qa-script.py` and confirm P0 = 0 (after
      excluding `dashboard-cliente.html`) before pushing the deploy button
