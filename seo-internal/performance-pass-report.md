# Performance Pass Report

Generated: 2026-04-29

## Summary
- Files scanned: 266
- Files modified: 265
- Total optimizations applied: 632

> Note: counts below reflect the cumulative state of the site after running
> `seo-internal/perf-pass.py`. Re-running the script is a no-op (idempotent),
> so these numbers represent the optimizations now present in the HTML. The
> "Issues found" section is recomputed on every run from the live HTML.

## By pass

- Pass 1 (defer/async scripts): 104 changes
  - defer added: 104 (mostly to `splash.js`, `dashboard-guard.js`, `supabase-auth.js`, `header.js`, `motion.js`, `cursor.js`)
  - async added: 0 (no analytics scripts present in the static build)
  - already deferred at source: 530 (cookie-banner.js + forms.js across 265 files)
- Pass 2 (lazy loading images): 0 changes
  - No `<img>` tags were found in any HTML file. PAPIK uses CSS `background-image` for hero/decorative imagery; the lazy-loading pass therefore had nothing to mutate. See "Recommended next steps" for follow-up.
- Pass 3 (preload hints): 526 changes
  - main CSS preload: 261 (`tokens.css`, with the exact relative path each page uses)
  - font preload: 265 (`/fonts/TT_Firs_Neue_Regular.woff2`)
  - preconnect (Google Fonts): 0 (site uses self-hosted TT Firs Neue, no Google Fonts)
- Pass 4 (dns-prefetch): 2 changes
  - `//cdn.jsdelivr.net` (used by `usuaris.html` for Supabase)
  - `//unpkg.com` (used by `es/nosotros.html` for Leaflet)

## Issues found (require manual review)

- **Images missing alt text:** 0 (no `<img>` elements site-wide)
- **Images missing width/height:** 0 (no `<img>` elements site-wide)
- **Render-blocking scripts identified:**
  - `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2` (in `usuaris.html`)
  - `https://unpkg.com/leaflet@1.9.4/dist/leaflet.js` (in `es/nosotros.html`)

  Both are external CDN scripts loaded synchronously without `defer` or `async`.
  They were left untouched because adding `defer` could break inline init code
  that follows them in the body. Manual review recommended: either move to
  bundled local files or refactor inline init to wait for `DOMContentLoaded`.

## Recommended next steps

1. **Lighthouse audit on real Chrome (mobile + desktop)** against staging once Vercel deployment completes; validate LCP / CLS / INP improvements from the preload hints (CSS + font preloads typically reduce LCP by 200-600 ms on cold loads).
2. **Image format conversion.** All decorative imagery currently lives in `/public/img/` as PNG/JPG referenced from CSS. Convert to WebP/AVIF and update the CSS `url()` references; gate behind `image-set()` for fallback.
3. **Critical CSS inlining.** The site loads 5 stylesheets (`tokens`, `base`, `header`, `components`, `footer`). Inline the above-the-fold subset (~3-5 kB of `tokens.css` + hero-specific rules) as a `<style>` block in `<head>` and `media="print" onload="this.media='all'"` the rest. Eliminates the remaining render-blocking CSS round-trip.
4. **Service Worker** for `/css/`, `/js/`, `/fonts/`, `/img/` (cache-first, 30-day TTL) and HTML (network-first with offline fallback to `/_t.html`). Improves repeat-visit TTI dramatically and unlocks offline browsing of the project pages.
5. **Refactor the two render-blocking external scripts.** Replace the CDN Supabase reference with a bundled local copy (current version pinned in `package.json`); replace the Leaflet CDN with a self-hosted copy under `/public/js/vendor/`. Both can then be deferred safely.
6. **Add explicit width/height to background-image hero blocks via CSS `aspect-ratio`** so layout shifts on hero swap-in are zero. Currently CSS hero containers rely on padding-top hacks in some places; standardise on `aspect-ratio: 16 / 9` (or matching) for CLS = 0.
7. **Bundle CSS** into a single `main.css` at build time via `generate_html.py`. The five-file split is editor-friendly but costs five round-trips on first load. Concatenate + minify in the build step; one preload hint then covers the lot.
8. **Add `Cache-Control: public, max-age=31536000, immutable` headers** in `vercel.json` for `/fonts/*`, `/css/*`, `/js/*`, `/img/*` (versioned filenames or query-string busted on deploy).
