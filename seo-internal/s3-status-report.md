# S3 Status Report — Technical SEO Infrastructure

> Audit date: 2026-04-27 · Launch target: 2026-06-01 (T-35 days) · Auditor: Claude Code agent

## State of S3

S3 infrastructure is **structurally sound and ~80% launch-ready**. The four pillars — sitemap generator, robots.txt, vercel.json (redirects + headers), and JSON-LD schema templates — are all in place and follow current Google best practice. The sitemap is generated programmatically from `slug-mapping.json` (the single source of truth) with a defensive `file_exists()` gate that prevents 404 URLs from leaking. Hreflang annotations are correctly emitted with x-default → CA. **The remaining gaps are primarily downstream of S4 (HTML build/render) rather than S3 itself**: the new v1.1 article slugs and the four geo-landings have copy ready but lack the rendered HTML files, so the generator silently skips them. Once those HTMLs ship, the sitemap will automatically expand. The only true S3 work pending now is (a) deciding whether to publish the rename of ES slugs (`construccio` → `construccion`, etc.), (b) auditing the WP-legacy redirect coverage in `vercel.json` (only 33 redirects visible vs the 245+ historically claimed), and (c) writing the formal hreflang strategy document.

## Infrastructure inventory

| File | Status | Notes |
|---|---|---|
| `/public/sitemap.xml` | OK · regenerated (61 URLs) | Auto-built by `generate_sitemap.py` from slug-mapping. hreflang + x-default present on every entry. |
| `/public/robots.txt` | OK · production-ready | `Sitemap:` directive present, WP legacy paths blocked, dashboard noindex'd, CSS/JS/img allowed. No changes needed. |
| `/vercel.json` | OK · partial coverage | `cleanUrls=true`, security headers (HSTS/XFO/Referrer/Permissions), cache-control for static assets. **33 redirects only** — see Gaps for missing WP slugs. Do NOT auto-edit per task scope. |
| `/generate_sitemap.py` | OK · solid implementation | Reads slug-mapping.json, applies ES legacy fallback, skips nonexistent files. Idempotent, safe to run pre-deploy. Recommend wiring into Vercel `buildCommand`. |
| `/seo-internal/slug-mapping.json` | UPDATED · v1.0 → +v1.1 entries | Added 3 new v1.1 articles + reconfirmed 4 Tier-1 landings as `copy-ready-html-pending`. Sabadell ES note updated. |
| `/seo-internal/schemas/*.json` (7 files) | OK · templates production-ready | All 7 schemas (Organization, Service, LocalBusiness, Article, FAQPage, Breadcrumb, RealEstateListing) inspected. README documents combinations per page type and `{{...}}` tokens. |
| `/seo-internal/schemas/README.md` | OK · comprehensive | Validation flow (Rich Results Test + schema.org) documented. Workflow for dev included. |

## Gaps for launch

### High severity
- **HIGH · Vercel redirects undercount.** Only **33 redirects** in `vercel.json`. Previous summary mentioned 245+. The bulk of legacy WP slugs (individual project URLs, individual blog post URLs, taxonomy pages, paginated archives, attachment pages, language variants of the WP site, dated archives `/2018/03/...`, etc.) appear unreferenced. Without these, organic equity from the old site will 404 instead of 301-passing. **Action required: audit by user** with WP export or historical sitemap.
- **HIGH · No `/en/` HTML files exist in `/public/`.** Copy is ready for 7 EN pages (homepage, development, retrofit, wealth, construction, 4 landings, 5 articles) but `public/en/` directory does not exist. Sitemap correctly excludes them. **S4 must build EN HTML before EN entries auto-appear in sitemap.**
- **HIGH · 4 Tier-1 geo-landings have no HTML.** Sant Cugat, Sant Quirze, Bellaterra, Matadepera. Copy CA+ES+EN ready in `seo-internal/copy/`. These are the largest organic upside in the launch (geo + service intent). **S4 dependency.**
- **HIGH · 3 new v1.1 articles have no HTML.** `article-derribar-construir-passos`, `article-llicencia-derribo-cerdanyola-bellaterra`, `article-substituir-vs-rehabilitar`. Copy CA+ES ready. They form the Bellaterra cluster. **S4 dependency.**

### Medium severity
- **MEDIUM · ES slug rename unresolved.** `slug-mapping.json` documents 8 pending renames (`construccio.html` → `construccion.html`, etc.) under `_pending_renames`. Generator has `ES_FALLBACK_MAP` so the site still works, but ES URLs currently use Catalan slugs which is a soft signal-loss for Spanish SEO. **Decision needed: rename or postpone.**
- **MEDIUM · ES `article-nota-prensa-papik-sabadell.html` not built.** Translation MD exists. Once built, sitemap auto-emits the ES alternate.
- **MEDIUM · No `RealEstateListing` schema for `/promocio` (RealEstateListing differs from project schema 07).** Schema 07 covers individual `/projecte-*` pages but `/promocio` (Promociones, where K-Vall d'Or etc. are sold) probably warrants `RealEstateListing` proper or `ItemList` of `RealEstateListing`. **Consider adding schema 08 in S4.**
- **MEDIUM · Hreflang strategy not formally documented.** Implementation is correct in sitemap, but no markdown explains the choice (CA = canonical/x-default, ES under `/es/`, EN under `/en/`, no `ca-ES`/`es-ES` regional codes). Add `seo-internal/hreflang-strategy.md` for posterity.

### Low severity
- **LOW · `Crawl-delay: 1` in robots.txt.** Google ignores it; Bing/Yandex respect it. Harmless. Could remove for cleanliness.
- **LOW · `lastmod` is the build date, not the actual page-modified date.** All entries currently say `2026-04-27`. Google de-emphasizes lastmod when noisy. Generator could be enhanced to read file mtime per page. Not blocking.
- **LOW · No `image:image` extension in sitemap.** Could add `xmlns:image` and `<image:image>` blocks for hero images to feed Google Images. Optional polish.
- **LOW · No `news:news` for press releases.** Articles `article-nota-premsa-*` could use Google News sitemap if PAPIK applies for News inclusion. Not relevant unless News submission is planned.
- **LOW · No JSON-LD `NewsArticle` variant for press releases.** Schema 04 (Article) is used; switching the press releases to `NewsArticle` would clarify intent for Google. Cosmetic.

## Fixes applied

1. **`slug-mapping.json` — added 3 new v1.1 article entries** (`article-derribar-construir-passos`, `article-llicencia-derribo-cerdanyola-bellaterra`, `article-substituir-vs-rehabilitar`) with `status: "v1.1-pending-build"` and explicit CA + ES URL declarations. They will auto-emit in sitemap once HTML ships.
2. **`slug-mapping.json` — promoted 4 Tier-1 landings** (Sant Cugat, Sant Quirze, Bellaterra, Matadepera) from `status: "to-create-S4"` to `status: "copy-ready-html-pending"` with explanatory notes pointing at the copy files.
3. **`slug-mapping.json` — updated `article-nota-premsa-papik-sabadell` entry** to declare the ES URL (`/es/article-nota-prensa-papik-sabadell`) and note that the translation copy is ready.
4. **`/public/sitemap.xml` — regenerated via `generate_sitemap.py`.** Now contains **61 valid URLs** (was 60). Sabadell ES alternate did not yet emit because the ES HTML is still missing — the generator's safety gate held correctly.

No changes were made to `vercel.json`, `robots.txt`, schemas, copy files, or any HTML in `/public/` (per task scope).

## Pending — needs user decision before applying

1. **Audit and expand WP-legacy redirects in `vercel.json`.** Need a master list of WP URLs (from old sitemap, GSC coverage report, or Screaming Frog crawl of the old site). Without it, post-launch 404s are guaranteed for any external link to the WP site.
2. **Decide on ES slug rename batch** (8 renames in `_pending_renames`). If yes, requires: rename HTML files, update internal links, regenerate sitemap, add corresponding 301 redirects in vercel.json (`/es/construccio` → `/es/construccion` etc.).
3. **Confirm whether to publish EN homepage at launch** even if only 7 EN pages are ready. Partial EN deployment is fine SEO-wise as long as hreflang only references existing pages — which the generator already enforces.
4. **Decide on schema 08 (`RealEstateListing` / `ItemList`) for `/promocio`.** S4 territory but worth flagging now.
5. **Add `dashboard-cliente` and `usuaris` `noindex` reinforcement.** `vercel.json` already X-Robots-Tag's `/dashboard-cliente` but not `/usuaris` or the ES variants. Recommend extending the noindex header rule.

## Recommended next steps (prioritized)

1. **(P0, blocks launch) Run a WP redirect audit** — pull a list of every URL the old WordPress site indexed (use Screaming Frog or `wp-cli` export), diff against current `vercel.json`, and add the missing `permanent: true` redirects. Expect 50–250 entries. Without this the SEO equity transfer fails.
2. **(P0, blocks Tier-1 SEO upside) S4: build the 4 geo-landings** — the slug-mapping is ready, the copy is ready, the sitemap auto-emits on build. This is the single biggest organic-traffic lever for the launch quarter.
3. **(P1) S4: build the 3 new v1.1 articles** — Bellaterra topical cluster. Same pattern as #2.
4. **(P1) Decide ES slug rename and execute or postpone** — postponement has a real (small) cost in `es.es` SEO. Recommend executing in S3 (now) before launch so URL identity is permanent from day 1.
5. **(P1) Build `/en/index.html` + the 6 other EN HTML pages** so EN slot of hreflang triplet is non-empty at launch. Even partial EN coverage is better than no EN.
6. **(P2) Wire `python3 generate_sitemap.py` into Vercel `buildCommand`** so the sitemap can never go stale relative to `slug-mapping.json`. Add to `vercel.json` or to a `scripts/build.sh`.
7. **(P2) Write `seo-internal/hreflang-strategy.md`** documenting the canonical-CA, ES-subpath, EN-subpath strategy and the x-default policy. Future-proofing for whoever maintains this site after S5.
8. **(P2) Extend X-Robots-Tag `noindex` header** in `vercel.json` to cover `/usuaris`, `/es/usuarios`, and (if added) `/dashboard-cliente`'s ES variant.
9. **(P3) Add `xmlns:image` to sitemap** with hero images per page. Cheap win for Google Images discovery, especially for project pages.
10. **(P3) Switch `article-nota-premsa-*` to `NewsArticle` schema** instead of generic `Article`.
11. **(P3) Improve `lastmod`** by reading file mtime in the generator instead of using build date for every entry.

---

*Generated by Claude Code S3 audit · 2026-04-27*
