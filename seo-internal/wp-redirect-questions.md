# WP Redirect Audit — Open Questions

Generated: 2026-04-27 · Reviewer: @founder · Source: `wp-redirects-proposed.json` (class G items)

These items need a decision before merging into `vercel.json`. Each block lists the WP URL, the candidate destinations considered, the recommendation, and the question.

---

## Q1 · `/projectes/k-colombia/` (CA only — no ES counterpart in WP sitemap)

**Live WP URL:** `https://www.papik.cat/projectes/k-colombia/`
**Candidates:**
- (a) `/projectes` — projects index (safe fallback)
- (b) Create a new `/projecte-k-colombia` page on the new site
- (c) 410 Gone (mark as obsolete)

**Recommendation:** (a) for launch. Project not in v1 catalogue (`slug-mapping.json` lists 33 `projecte-*` pages, K-Colombia not among them).

**Question:** Is K-Colombia an active project we should rebuild in v1.1, or was it deprecated when the WP site was last curated? If active → schedule v1.1 build (option b).

---

## Q2 · Legal pages (CA + ES) — `/avis-legal`, `/politica-de-privacitat`, `/politica-de-cookies` and ES equivalents

**Live WP URLs:**
- `/avis-legal/`, `/politica-de-privacitat/`, `/politica-de-cookies/`
- `/es/aviso-legal/`, `/es/politica-de-privacidad/`, `/es/politica-de-cookies/`

**Candidates:**
- (a) Build the same six pages on the new site → 1:1 redirect
- (b) Consolidate into one `/legal` hub per language
- (c) Redirect all to `/` (lossy, hurts compliance UX)

**Recommendation:** (a) — these pages are required by GDPR/LSSI-CE; they should exist as HTML and the redirects should be 1:1. Currently they do not exist in `public/` (verified — only `dashboard-cliente.html`, no `avis-legal.html` etc.).

**Question:** Do we have the legal copy approved by counsel? If yes, schedule build before launch. Until then, the proposed redirect is self-referential and will 404.

---

## Q3 · `/es/prioridades-a-la-hora-de-hacer-tu-casa-a-medida` (and CA `/prioritats-a-lhora-de-de-fer-te-la-teva-casa-a-mida`)

**Candidates:**
- (a) `/com-construim-la-teva-casa` (CA) / `/es/blog` (ES, no Spanish process page yet)
- (b) `/es/blog`

**Recommendation:** CA → `/com-construim-la-teva-casa` (already proposed as B). For ES, the Spanish localisation of "com construim la teva casa" doesn't yet exist on the new site.

**Question:** Should we build `/es/como-construimos-tu-casa` for v1.1, or temporarily redirect ES traffic to the CA process page? (Cross-language redirects hurt UX but preserve link equity.)

---

## Q4 · `/professional` and `/es/profesional`

**Live WP URLs:** `/professional/`, `/es/profesional/`

**Candidates:**
- (a) Redirect to `/` (current proposal — lossy)
- (b) Build a B2B/professional landing on the new site
- (c) Redirect to `/empresa` → `/nosaltres`

**Recommendation:** (a) for launch unless B2B is a 2026 priority. The page existed on WP for installer/architect partnerships.

**Question:** Is the B2B audience worth a dedicated landing in v1.1?

---

## Q5 · ES "/es/que-hacemos/*" sub-tree

Already covered by catch-all in proposal (`/es/que-hacemos/:path*` → `/es/construccio`). However, the Spanish "promocion / patrimonios / rehabilitacion" service split exists in `slug-mapping.json` but `/es/que-hacemos/promociones` was never on WP.

**Recommendation:** Keep the catch-all to `/es/construccio` for safety; verify with GA4 search-console-data which sub-paths actually had impressions.

**Question:** Should `/es/que-hacemos/rehabilitaciones` route to `/es/rehabilitacio` (per current proposal) or to a more granular `/es/rehabilitacion-comunidades` once that page is built?

---

## Q6 · Legacy ES post slugs that exist as duplicate Spanish content under root (no `/es/` prefix)

WP has a few orphan posts where the Spanish post got published at the root path instead of under `/es/` — e.g.:
- `/como-las-casas-passivhaus-reducen-las-facturas-de-energia` (Spanish, served from CA root)
- `/por-que-elegir-una-casa-passivhaus-ventajas-para-la-salud-y-el-confort` (Spanish, served from CA root)
- `/segunda-casa-pasiva-en-cataluna` (Spanish, served from CA root)

Currently proposed: redirect to `/es/blog` (or `/projecte-passivpalau` for the third).

**Question:** Confirm the destination language. If Google indexed these as Spanish content under the CA root, redirecting to `/es/blog` is correct (preserves language). If they ranked in CA search, we may want to redirect to `/blog` instead. Recommend verifying via Search Console.

---

## Q7 · `/feed` and category/tag/author RSS feeds

`vercel.json` already redirects `/feed` and `/es/feed`. WP also auto-generates per-category and per-author feeds (`/category/X/feed/`, `/author/X/feed/`).

**Recommendation:** Add catch-all `/(.*)/feed` → root-blog. Not included in proposal because Vercel pattern syntax requires a dedicated entry. Should we add it?

**Question:** Approve adding two more catch-alls? `/(.*)/feed` → `/blog` and `/es/(.*)/feed` → `/es/blog`.

---

## Q8 · WP image attachments and uploads (`/wp-content/uploads/...`)

Not covered in this audit (sitemaps don't list them). WP serves images from `/wp-content/uploads/YYYY/MM/file.jpg`. After launch, all hot-linked image URLs from social media, press, and external blogs will 404.

**Recommendation:** Either (a) keep `/wp-content/uploads/` proxied to the legacy CDN for 12 months, or (b) accept the loss for non-critical images and 410 the path.

**Question:** Do we have the historical S3/uploads bucket archived? If yes, set up `/wp-content/uploads/:path*` → `https://archive.papik.cat/...` rewrite. If no, accept 404s.

---

**End of questions. Once answered, update `wp-redirects-proposed.json` and request a fresh diff before merging into `vercel.json`.**
