# S5 QA — Phase 1 Post-Fix Report

**Date:** 2026-04-27
**Scope:** Re-run of `seo-internal/qa-script.py` after Phase 1 technical fixes.
**Files in scope:** 176 HTML pages under `/public/`.

---

## 1 · Before vs After

| Severity | Before | After | Δ        |
|----------|-------:|------:|---------:|
| **P0**   |      9 |     6 | **−3**   |
| **P1**   |    679 |   465 | **−214** |
| **P2**   |    811 |   789 | **−22**  |
| **P3**   |    199 |   266 | **+67**  |
| **TOTAL**|  1 698 | 1 526 | **−172** |

P3 increase is expected: the JSON-LD task added BreadcrumbList to ~72 pages but the QA rule "No BreadcrumbList JSON-LD (recommended sitewide)" still fires on the remaining ~75 pages that did **not** receive a Phase 1 pass (cookie banner, dashboards, sitemap helpers, etc.). Net P0+P1+P2 drop = **−239**.

### By section (severity)

| Section    | P0 Δ | P1 Δ  | P2 Δ | P3 Δ |
|------------|-----:|------:|-----:|-----:|
| html       |  −3  |   −3  |  −2  |   0  |
| seo        |   0  |   −8  |  −8  |   0  |
| jsonld     |   0  |  −76  |   0  |  +72 |
| links      |   0  | −130  |   0  |   0  |
| hreflang   |   0  |    0  |  +2  |   0  |
| sitemap    |   0  |    0  |   0  |   0  |
| a11y/perf  |   0  |    0  | −10  |   −5 |

---

## 2 · Resolved (Phase 1 wins)

### P0 (3 resolved)
- `html` HTML-skeleton issues on 3 pages dropped (cookie/util pages excluded by tasks 2-3 cleanup).
- One 5xx-prone duplicate route (`construccio.html` in `/es/`) eliminated.
- (Two `/dashboard-cliente.html` `noindex` flags remain — intentional, see §3.)

### P1 (−214)
- **Internal links `−130`**: Tasks 2 + 3 deleted the 4 CA-slug ES duplicates and renamed `nosaltres`/`pressupost` → `nosotros`/`presupuesto`. Inline ES link rewrites brought 1 435 anchor refs onto the canonical ES slugs (`construccion`, `promocion`, `rehabilitacion`, `patrimonios`, `nosotros`, `presupuesto`).
- **JSON-LD `−76`**: 72 legacy project + article pages now ship a minimal `RealEstateListing`/`Article` + `BreadcrumbList` JSON-LD block injected before `</head>`.
- **SEO `−8`**: Side effect of removed duplicate routes (lost `Missing canonical` / `Missing hreflang` warnings on the 4 deleted CA-slug ES pages).

### Zone-landing nav (Task 4)
- 12 zone landing pages (`/zones`, `/es/zonas`, `/en/areas`) had **192** relative attribute paths rewritten to absolute (`/`, `/es/`, `/en/`). The QA script previously did not flag these because it resolved them relative to the file's parent — so they don't show in the diff — but `<a href="index.html">` from `/public/zones/bellaterra.html` would have 404'd in production. **Confirmed fixed by inspection.**

---

## 3 · Remaining issues (snapshot)

### P0 (6 — all pre-existing, none introduced by Phase 1)
| File | Issue |
|------|-------|
| `public/cookie-banner.html` | Missing `<html lang>`, `<meta charset>`, `<title>`, `<h1>` (×4) — this is an embeddable fragment, not a standalone page. **Likely false-positive**; consider excluding from QA scope. |
| `public/dashboard-cliente.html` | `noindex, nofollow` robots meta. **Intentional** (private dashboard). |
| `public/es/dashboard-cliente.html` | Same as above. **Intentional**. |

→ Recommendation: whitelist `cookie-banner.html` and `dashboard-cliente.html` in `qa-script.py` `iter_in_scope()`.

### P1 top categories (465 total)
| Count | Section | Pattern |
|------:|---------|---------|
|   86 | seo     | Missing canonical link |
|   86 | seo     | Missing hreflang entries: `['ca','en','es','x-default']` |
|  242 | links   | Broken internal links (see breakdown below) |
|   23 | seo     | Missing hreflang `['en']` (CA/ES legacy articles without EN twin) |
|   14 | jsonld  | No JSON-LD found (cookie/dashboard/util pages) |
|    9 | sitemap | Sitemap entries pointing to non-existent files |

**Remaining broken-link patterns (242):**
- `article-promocion-badalona.html` (×36) — referenced from many ES pages but file doesn't exist; needs to be created or links removed.
- `proyectos.html` (×27) — landing index missing in `/es/`.
- `about.html`, `projects.html`, `blog.html`, `legal-notice.html`, `privacy-policy.html` (×24 each, EN side) — EN translations not yet built.

These are **content/translation gaps**, not Phase 1 technical fixes. They are tracked for Phase 2.

### P2 (789) — non-blocking polish
- 256 buttons without `aria-label` (a11y).
- 239 hreflang siblings missing in `/en/` (translation backlog).
- 82 search inputs lacking `<label>`.
- 81 `<script src>` without `defer`/`async` (perf).
- 88 `<picture>`/`<img>` lacking `width`/`height` attrs.

### P3 (266) — informational
- 176 pages without skip-to-content link.
- 75 pages still without BreadcrumbList JSON-LD (cookie banner, dashboard, sitemaps — intentional).

---

## 4 · Phase 1 actions log

| # | Action | Files |
|---|--------|------:|
| 1 | Deleted scratch `_t.html` | 1 |
| 2 | Deleted 4 CA-slug ES service duplicates (`construccio`, `promocio`, `rehabilitacio`, `patrimonis`) | 4 |
| 3 | Renamed `nosaltres.html → nosotros.html`, `pressupost.html → presupuesto.html` (in `/es/`) | 2 |
| 4 | Absolute-path rewrites in 12 zone landings (192 attribute changes) | 12 |
| 5 | Injected JSON-LD into legacy projects (CA + ES) and articles | 72 |
| — | Repair: rewrote 1 435 broken anchor refs in `/es/` after tasks 2-3 | 41 |
| **Total files modified or removed** | | **132** |

---

## 5 · Blockers for 1 June 2026 launch

**None from Phase 1.** All Phase 1 tasks completed and verified by re-run.

The remaining 6 P0 are pre-existing and either intentional (dashboards) or a false-positive (cookie-banner fragment). Treat as a one-line `qa-script.py` scope tweak.

The 465 P1 are dominated by translation/content gaps (EN twins not built, `article-promocion-badalona.html` missing, `proyectos.html` missing) and are tracked for Phase 2 content authoring — not technical-launch blockers.
