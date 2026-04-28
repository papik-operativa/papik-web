# Asset Handoff Specification

> What assets PAPIK needs to deliver before launch, in what format, and where they go.
> Last updated: 2026-04-29

This document is the single source of truth for everything that has to come from outside the codebase before the new `papik.cat` can go live on **1 June 2026**: curated images, OG images, real corporate identifiers, the cookie inventory, signed consents, and counsel sign-off. Each section names the deliverable, the format, the destination path, and the operational consequence of delivering late.

---

## 1. Project page images

For each of the **36 project pages**, deliver a curated image set. The project pages are tri-lingual (CA `/projecte-*`, ES `/es/proyecto-*`, EN `/en/projects/*`) but the image set is shared across all three URLs of the cluster, so each slug only needs **one** image folder.

### Naming convention

Per project, under a folder named with the canonical CA slug (without the `projecte-` prefix is acceptable, but consistency with the slug-mapping is preferred):

```
[slug]/
├── hero.jpg        (main shot, used in hero section + OG)
├── exterior-01.jpg (exterior photo 1)
├── exterior-02.jpg
├── interior-01.jpg
├── interior-02.jpg
├── detail-01.jpg   (construction detail)
└── plan.jpg        (floor plan, optional)
```

`hero.jpg` is mandatory. Two `exterior-*` and two `interior-*` are strongly recommended. `detail-*` and `plan.jpg` are optional but improve dwell time.

### Recommended sizes and formats

- Hero: 1920 x 1080 (16:9), targeted file size under 250 KB.
- Gallery (exterior, interior, detail): 1600 x 1200 (4:3) or 1920 x 1280 (3:2), under 200 KB each.
- Floor plan: 1600 x 1200 minimum, white or light background, under 150 KB.
- WebP as primary format, JPG as fallback. Always deliver both.
- Colour space: sRGB. Strip EXIF before delivery (privacy). Avoid borders, watermarks, overlays.
- Orientation: landscape only for hero and gallery (mobile crops anyway). Portrait only acceptable for detail or plan.

### Where they go

- `/public/img/projects/[slug]/hero.webp` (+ `.jpg` fallback)
- `/public/img/projects/[slug]/exterior-01.webp` etc.
- The Hero is also reused as the OG image for that project's three URLs. No separate OG asset needed per project.

### Slug list (36 projects)

```
projecte-ampliacio-valldoreix
projecte-arboc
projecte-fornells
projecte-k-alzina
projecte-k-aragai
projecte-k-argentona
projecte-k-begues
projecte-k-bellindret
projecte-k-botigues
projecte-k-calonge
projecte-k-cim
projecte-k-codines
projecte-k-del-carril
projecte-k-denbas
projecte-k-gorgs
projecte-k-hostalets
projecte-k-igualada
projecte-k-iturbi
projecte-k-lamassa
projecte-k-llavaneres
projecte-k-malats
projecte-k-marges
projecte-k-maristany
projecte-k-matadepera
projecte-k-merla
projecte-k-mogent
projecte-k-orio
projecte-k-premia
projecte-k-vallor
projecte-la-floresta
projecte-moianes
projecte-passivpalau
projecte-passivrooms
projecte-rehabilitacio-valldoreix
projecte-remunta-sant-cugat
projecte-remunta-valldoreix
```

If a project's image set is incomplete on launch day, a generic Eskimohaus placeholder will render in the hero and gallery. The page will still ship; quality just suffers. **Priority projects** (per `slug-mapping.json`, priority 0.8): K-Codines, K-Del-Carril, K-Iturbi, K-Llavaneres, K-Matadepera, K-Vallor, La Floresta, Passivpalau. Deliver these first if time-constrained.

---

## 2. OG images per page type

Default fallback already in place: `/img/og/og-default.jpg` (1200 x 630). Every page falls back to this if a more specific OG is missing, so the site is launch-safe without any further OG work. The list below is the **upgrade path**.

Per-page-type OG images:

- Homepage (3 langs share one): `og-home.jpg`
- `/construccio` and translations: `og-construccion.jpg`
- `/promocio` and translations: `og-promocion.jpg`
- `/rehabilitacio` and translations: `og-rehabilitacion.jpg`
- `/patrimonis` and translations: `og-patrimonis.jpg`
- `/comunitats` and translations: `og-comunitats.jpg`
- Each project page: derived from `/img/projects/[slug]/hero.jpg` (no separate OG asset)
- Each landing (Tier 1 + Tier 2): `og-zona-[slug].jpg` (e.g. `og-zona-bellaterra.jpg`)
- Each comarcal hub: `og-comarca-[slug].jpg` (e.g. `og-comarca-valles-occidental.jpg`)
- Each article: derived from the article hero image, or fallback to `og-blog.jpg`
- Legal pages: fallback to `og-default.jpg` (no upgrade needed)

### Format and budget

- Dimensions: 1200 x 630 px exactly (Facebook/LinkedIn/Twitter card spec).
- Format: JPG (WebP not yet universally accepted by social crawlers).
- Max file size: 100 KB each. Tighten with mozjpeg or squoosh.
- Safe area: keep critical content in centred 1080 x 540 inner box (some platforms crop edges).
- No microscopic text. Min legible text size 32 px.
- Brand: Eskimohaus mark in bottom-right or top-left corner, 64 px tall.

### Where they go

- All in `/public/img/og/`.
- Filenames must match the convention above (the build pipeline does not auto-discover; the metadata block in `generate_html.py` references explicit paths).

---

## 3. Real corporate data (for legal placeholders)

All three legal pages (avis legal, política de privacitat, política de cookies) and their ES + EN equivalents currently ship with `[PLACEHOLDER]` markers in the rendered HTML, plus a banner warning the visitor that these are draft texts pending counsel review.

### Required to fill

- **Denominació social**: full registered company name as it appears in Registre Mercantil.
- **NIF/CIF**: tax identifier.
- **Domicilio fiscal**: full registered address (street, number, postal code, municipality, province).
- **Phone number** (corporate, public-facing).
- **Email DPO** (or general contact if no DPO is designated).
- **Email contact** (general public inbox).
- **Registro Mercantil entry**: tom, foli, full, secció, hoja registral.
- **City of fiscal seat**: needed for the jurisdiction clause ("submission to the courts of [city]").
- **DPO designation decision**: yes/no. If yes, name + appointment date. If no, a written justification (Article 37 GDPR) is recommended.

### Where they go

The 9 placeholder legal source files (Markdown) are:

- `/seo-internal/copy/rewrites/legal/avis-legal-ca-v2.md`
- `/seo-internal/copy/rewrites/legal/politica-privacitat-ca-v2.md`
- `/seo-internal/copy/rewrites/legal/politica-cookies-ca-v2.md`
- `/seo-internal/copy/translations/es/legal/aviso-legal-es-v2.md`
- `/seo-internal/copy/translations/es/legal/politica-privacidad-es-v2.md`
- `/seo-internal/copy/translations/es/legal/politica-cookies-es-v2.md`
- `/seo-internal/copy/translations/en/legal/legal-notice-en-v2.md`
- `/seo-internal/copy/translations/en/legal/privacy-policy-en-v2.md`
- `/seo-internal/copy/translations/en/legal/cookie-policy-en-v2.md`

Process:

1. Apply real values across all 9 files (search/replace `[PLACEHOLDER:NIF]`, `[PLACEHOLDER:DOMICILIO]`, etc.).
2. Run `python generate_html.py` from project root to regenerate the rendered HTML in `/public/`.
3. Visually diff one page per language (browser) to confirm placeholders are gone.
4. Remove the warning banner once counsel signs off (separate flag in `generate_html.py`).

---

## 4. Cookie inventory

The cookie policy table in section 3 of each cookie policy is currently empty (placeholder text only). The real inventory can only be assembled after a first staging deploy, because cookies are emitted by the live runtime (analytics, embedded video, social pixels, Vercel functions, etc.).

### Required after first staging deploy

Run a cookie scanner against the staging URL:

- Cookiebot, OneTrust, Termly, or any equivalent.
- Scan must cover all 4 unitats de negoci pages, the configurador, the contact form, the blog, and one project page.
- Scan in 3 sessions: pre-consent, post-accept-all, post-reject-all. The deltas matter.

For each cookie detected:

- Cookie name (exact string).
- Owner (first-party `papik.cat` or third-party domain).
- Purpose (one sentence).
- Duration (session, days, months, years).
- Type (technical/functional, preferences, analytics, advertising). The first two are typically exempt from prior consent under the AEPD guidelines; the latter two are not.

### Where it goes

The 3 cookie policy source files (CA + ES + EN) carry an empty markdown table in section 3:

- `/seo-internal/copy/rewrites/legal/politica-cookies-ca-v2.md`
- `/seo-internal/copy/translations/es/legal/politica-cookies-es-v2.md`
- `/seo-internal/copy/translations/en/legal/cookie-policy-en-v2.md`

Update the table in each file (same data, translated headers), regenerate HTML, and confirm the cookie banner script reads the same inventory (single source of truth principle).

---

## 5. Family Ponsa consent

The article `/article-nota-premsa-papik-ponsa` (and ES + EN siblings) currently sits with a "draft, do not publish" flag pending written consent. The article references the Ponsa surname and the 2 M EUR annual investment commitment figure, both of which fall under the Ponsa-rule (no identified clients without written consent) and the regulatory caution around investment-adjacent claims.

### For the article to remain published, deliver

- Written consent from the Ponsa family.
- Format: signed PDF, or an email from a verifiable family address with explicit text "I authorize the publication of [scope]".
- Scope must explicitly list:
  - The family surname.
  - The 2 M EUR annual investment commitment figure.
  - Reference to the strategic agreement (i.e. the press-release framing).
- Date and signatory clearly identified.

### Where it goes

- File the original at `/Users/trisfisas/Desktop/CÓDIGO/papik-web/BACKUPS/legal-consents/ponsa-consent-[YYYY-MM-DD].pdf`.
- Cross-reference in `/seo-internal/legal-review-report.md` updated to "consent received on [date], scope: [verbatim]".
- Without the consent, the article is pulled from the launch and replaced with a 410 Gone (or temporary noindex) until resolved.

---

## 6. Counsel sign-off package

The legal review pass identifies 8 documents that require external counsel sign-off before launch.

### Deliver to your lawyer

- All 9 legal placeholders (CA + ES + EN x avis-legal / política privacitat / política cookies).
- `/patrimonis` page disclaimer (CNMV exposure).
- `/comunitats` LPH disclaimer (Llei Propietat Horitzontal exposure).
- `/rehabilitacio` NGEU disclaimer (subvention claims).
- `/article-nota-premsa-papik-sabadell` disclaimer (Banc d'Espanya exposure on green-mortgage framing).
- `/article-nota-premsa-papik-ponsa` disclaimer (CNMV + family consent).
- `/article-hipoteca-energetica` disclaimer (financial product framing).
- `/seo-internal/legal-review-report.md` (the in-house shadow review, for context only).

### Counsel reviews and either

- **(a) Approves verbatim.** Lift the warning banner via the flag in `generate_html.py`, regenerate HTML, deploy.
- **(b) Suggests amendments.** Apply edits to the source markdown files, regenerate HTML, send second pass.
- **(c) Identifies blocking issues.** Escalate immediately. May trigger launch delay or content removal (e.g. pull Ponsa article, remove a paragraph from `/patrimonis`).

Estimated counsel time: **12.5 hours** (per the shadow review's bottom-up estimate). Book the slot at least 2 weeks before T-0.

---

## 7. Post-deploy validation (manual, browser-side)

The automated QA pipeline (`qa-script.py`) covers schemas, hreflang, internal links, broken anchors, and metadata. Five validations remain that **must be done by a human in a browser** after the first staging deploy.

### Validation list

- **Lighthouse audit** on 5 representative pages: homepage `/`, a service page (`/construccio`), an article (`/article-principis-passivhaus`), a landing (`/zones/bellaterra`), and a project (`/projecte-k-iturbi`). Target: each category (Performance, Accessibility, Best Practices, SEO) >= 90.
- **axe DevTools accessibility scan** on the same 5 pages. Target: 0 critical issues. Serious and moderate logged for post-launch backlog.
- **Mobile-Friendly Test** (Google Search Console tool, or PageSpeed Insights mobile section) on the same 5 pages. Target: all pass.
- **Rich Results Test** on 1 article and 1 landing. Target: schema valid, no warnings on the structured data block. Test both the canonical CA URL and one translated sibling.
- **Visual smoke test**: open 20 random URLs in a desktop browser (mix of services, landings, articles, projects, legal). Confirm: hero renders, language switcher works, footer renders, cookie banner appears on first visit, mobile responsive at 375 px width.

Any failure here is a launch-blocker until resolved. Log results in a new `/seo-internal/launch-validation-[YYYY-MM-DD].md` for the audit trail.

---

## Summary

Six external dependencies stand between today and launch:

1. Project images (36 sets).
2. Per-page OG images (fallback covers it; upgrade only).
3. Corporate data (NIF, address, registry entry).
4. Cookie inventory (post-staging scan).
5. Ponsa family consent (or pull the article).
6. Counsel sign-off (8 documents, 12.5 hours).

Plus one internal task: 5 manual browser validations after staging deploy.

Everything else is already in the codebase and reproducible via `generate_html.py`.
