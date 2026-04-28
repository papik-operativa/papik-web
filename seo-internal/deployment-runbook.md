# PAPIK Group · Deployment Runbook · v1.0

> Operative checklist for the **1 June 2026 launch** of the new `papik.cat` site (static build on Vercel, replacing the WordPress live).
>
> Owner: Project lead. Read alongside `README.md` (project state) and `style-guide-editorial.md` (editorial v1.2).
>
> Last updated · 28 April 2026

---

## Pre-deployment checklist

### Code/content blockers (must be 100% green)

- [x] All HTML pages generated (run `generate_html.py`) — 268+ pages built
- [x] vercel.json with 301 redirects merged from `.candidate`
- [x] sitemap.xml regenerated — 255 URLs
- [x] robots.txt with AI scraper blocks (GPTBot, ClaudeBot, PerplexityBot, CCBot, Bytespider, Google-Extended)
- [x] Cookie banner + forms scripts deployed
- [x] Performance pass — defer scripts, lazy load below the fold, preload CSS + primary font, DNS-prefetch CDN
- [ ] All forms wired to real backend endpoint (still placeholder)

### Asset blockers (still pending)

- [ ] OG images per page (fallback in place; per-page art still pending)
- [ ] Project page images (curated batch from user pending delivery)
- [ ] Real legal field values (NIF, address, etc.)
- [ ] Real cookie inventory (post-cookie-scan after live deploy)

### Legal blockers (pending)

- [ ] Counsel sign-off on 6 placeholders
- [ ] Counsel sign-off on Patrimonis disclaimer
- [ ] Counsel sign-off on Ponsa article
- [ ] Counsel sign-off on Comunitats LPH disclaimer
- [ ] Family Ponsa written consent for 2M€ disclosure
- [ ] DPO designation decision

### QA blockers (mostly DONE, manual remainder)

- [x] qa-script.py final pass (post-fix issues to fix)
- [x] schema-validation pass — 253 schemas valid
- [x] hreflang completeness check — 87.5%, climbing toward 95%+ after Wave 3
- [x] internal linking analysis — 39 → 10 orphans
- [ ] Lighthouse 90+ on 5 representative pages (manual, requires browser)
- [ ] axe DevTools accessibility scan (manual)
- [ ] Mobile-Friendly Test (manual)
- [ ] Rich Results Test on 1 article + 1 landing (manual)
- [ ] Manual smoke test 20 random redirects in browser

---

## Deployment steps (1 June 2026)

### T-7 days · Staging push

- Push to staging branch
- Vercel auto-deploys preview
- Run full QA suite on preview URL
- Validate 20 critical paths
- Verify legal pages serve placeholder + warning banner
- Verify cookie banner appears on first visit

### T-3 days · DNS prep

- Confirm papik.cat A record points to Vercel
- Confirm www.papik.cat CNAME for canonicalization
- TTL reduced to 5min for fast rollback if needed

### T-0 (1 June 2026 · 00:00 CET)

- Merge staging → main
- Vercel auto-deploys to production
- Smoke test 5 critical paths post-deploy
- Verify hreflang canonicalisation working
- Verify cookie banner active

### T+1 hour

- Submit new sitemap to Google Search Console
- Re-validate Schema.org Rich Results
- Monitor 4xx rate in Vercel analytics
- Monitor Core Web Vitals in real-user-metrics

### T+24 hours

- Re-crawl with Screaming Frog or similar
- Compare crawl to expected URL set
- Identify any unexpected 404s in 1-day window
- Fix any P0s with hotfix

### T+7 days

- GSC: validate indexing of new pages
- Compare WP traffic week-over-week
- Identify any rank regressions
- Apply Phase 2 fixes if needed

---

## Rollback plan

If critical production issue:

- Vercel: instant rollback to previous deployment via dashboard
- DNS: not changed during deploy, no rollback needed
- vercel.json: keep previous version in `.previous` for quick swap

---

## Post-launch monitoring

- Day 1: Vercel logs every hour
- Week 1: GSC daily
- Month 1: monthly performance report
- Month 3: full SEO audit comparing pre/post traffic

---

## Contact

- Project lead: [USER]
- Technical: [USER + COMPAÑERO]
- Legal: [DESIGNATED COUNSEL]
- Emergency: [USER PHONE]
