# Going-Live Checklist · 1 June 2026

> The exact T-7 → T-0 → T+7 sequence for the new `papik.cat` launch.
> Built from `deployment-runbook.md` (foundation) plus all post-Wave-3 specifics.
> Last updated: 2026-04-29

This document is the operational playbook for the human running the launch on 1 June 2026. It assumes the codebase is in the state described in `README.md` v1.3 (post-Wave-4 cleanup) and that all asset and counsel deliverables in `asset-handoff-spec.md` are either resolved or explicitly accepted as fallback-only.

Every step has a checkbox, an owner, and a verification step. Tick as you go. Do not skip ahead. Do not run T-0 steps if any T-7 step is red.

---

## Roles

- **Lead**: project owner, final go/no-go authority.
- **Dev**: technical operator (Vercel, DNS, deploy commands).
- **Editorial**: content QA, browser-side smoke tests.
- **Legal**: external counsel, asynchronous (must have signed off by T-3).

---

## T-7 days (25 May 2026) · Staging push and full QA

### Pre-flight

- [ ] **Lead**: confirm all sections of `asset-handoff-spec.md` are either resolved or explicitly accepted as fallback. If counsel sign-off is pending, decide whether to launch with the warning banner active.
- [ ] **Dev**: confirm `/seo-internal/wave-4-cleanup-report.md` shows zero P0 issues open.
- [ ] **Dev**: pull latest main, run `python generate_html.py`, verify output: 268+ HTML files in `/public/`, sitemap regenerates with 255+ URLs, no errors in console.
- [ ] **Dev**: run `python seo-internal/qa-script.py` final pass. Target: 0 P0, 0 P1, P2/P3 documented in `qa-findings.json`.
- [ ] **Dev**: run `python seo-internal/validate-schemas.py`. Target: 100% schemas valid.
- [ ] **Dev**: run `python seo-internal/validate-hreflang.py`. Target: 95%+ completeness, no broken cluster.

### Staging deploy

- [ ] **Dev**: push to `staging` branch. Vercel auto-deploys preview to `papik-staging.vercel.app` (or assigned alias).
- [ ] **Dev**: confirm deployment is green in Vercel dashboard. No build errors. No runtime warnings.
- [ ] **Dev**: copy preview URL, share with Lead and Editorial.

### Staging QA suite (full)

- [ ] **Editorial**: run all 5 manual validations from `asset-handoff-spec.md` §7 against the staging URL.
  - Lighthouse on 5 pages (homepage, `/construccio`, `/article-principis-passivhaus`, `/zones/bellaterra`, `/projecte-k-iturbi`). Target ≥90 per category.
  - axe DevTools on same 5 pages. Target 0 critical.
  - Mobile-Friendly Test on same 5 pages. Target all pass.
  - Rich Results Test on 1 article + 1 landing. Target: schema valid.
  - Visual smoke test on 20 random URLs at 1920 px and 375 px viewports.
- [ ] **Editorial**: validate 20 critical paths manually (top branded queries, top transactional URLs, configurador, contact form, language switcher round-trip CA↔ES↔EN on 5 page types).
- [ ] **Editorial**: verify cookie banner appears on first visit (incognito), reject and accept paths both produce expected behaviour.
- [ ] **Editorial**: verify legal pages render with the warning banner active (or removed if counsel has approved).
- [ ] **Editorial**: log all findings in `/seo-internal/launch-validation-2026-05-25.md`.

### Cookie scan

- [ ] **Dev**: run cookie scanner (Cookiebot or equivalent) against staging URL. Three sessions: pre-consent, post-accept-all, post-reject-all.
- [ ] **Editorial**: update the cookie inventory table in 3 cookie policy markdown files per `asset-handoff-spec.md` §4.
- [ ] **Dev**: regenerate HTML, redeploy to staging, verify cookie banner script reads the new inventory.

### Counsel final sign-off

- [ ] **Legal**: deliver counsel-approved redlines for all 8 documents listed in `asset-handoff-spec.md` §6. If amendments arrived, Editorial applies them, Dev regenerates HTML.
- [ ] **Editorial**: flip the legal-warning-banner flag in `generate_html.py` to off, regenerate, redeploy to staging, verify banner is gone on legal pages.

### T-7 exit gate

- [ ] **Lead**: review all checkboxes above. If any are unchecked, decide: fix-and-proceed, accept-as-known-issue, or delay launch. Document decision in `launch-validation-2026-05-25.md`.

---

## T-3 days (29 May 2026) · DNS prep and rollback dry-run

### DNS

- [ ] **Dev**: confirm `papik.cat` A record points to Vercel's IP (`76.76.21.21` or current Vercel IP).
- [ ] **Dev**: confirm `www.papik.cat` CNAME points to `cname.vercel-dns.com`.
- [ ] **Dev**: reduce DNS TTL on both records to 5 minutes (300 s). This enables fast rollback if DNS-level changes become necessary on launch day.
- [ ] **Dev**: confirm both records resolve correctly from at least 2 external locations (`dig` from a non-local network, or use whatsmydns.net).
- [ ] **Dev**: confirm Vercel project has `papik.cat` and `www.papik.cat` listed under "Domains" with valid SSL certificates.

### Backup of legacy WP

- [ ] **Dev**: take a final full backup of the WordPress site (database + uploads). Store in `/Users/trisfisas/Desktop/CÓDIGO/papik-web/BACKUPS/wp-final-2026-05-29/`.
- [ ] **Dev**: take a final crawl of the live `papik.cat` (Screaming Frog or wget mirror). Store in same folder. This becomes the authoritative reference for redirect validation post-launch.

### Rollback dry-run

- [ ] **Dev**: confirm previous Vercel deployment is still listed in the dashboard. Test the "Promote to Production" rollback path on a non-customer-facing branch to validate the muscle memory.
- [ ] **Dev**: confirm `/Users/trisfisas/Desktop/CÓDIGO/papik-web/vercel.json.previous` exists and contains the working pre-launch config (in case a config-only rollback is needed without re-deploying).

### Communication prep

- [ ] **Lead**: draft launch announcement (LinkedIn, internal Slack, customer email if applicable). Hold for T+1 hour.
- [ ] **Lead**: confirm phone availability of Dev for the T-0 to T+24h window.

### T-3 exit gate

- [ ] **Lead**: all DNS, backup, and rollback steps green. Schedule confirmed for 1 June 2026, 00:00 CET.

---

## T-1 day (31 May 2026) · Final freeze

- [ ] **Lead**: declare content freeze. No edits to copy or markdown source files until T+24h.
- [ ] **Dev**: confirm no open PRs touch production paths.
- [ ] **Dev**: re-run `qa-script.py` one final time. Confirm same green result as T-7.
- [ ] **Editorial**: do one last visual smoke test on 5 pages on staging.
- [ ] **Lead**: post a "go" decision in writing (email or Slack timestamp) to Dev, Editorial, Legal.

---

## T-0 (1 June 2026 · 00:00 CET) · Switchover

### 23:30 CET (31 May)

- [ ] **Dev**: open Vercel dashboard, GSC, papik.cat in browser, terminal with `dig` and `curl` ready, monitoring tab on Vercel analytics.
- [ ] **Dev**: confirm staging deployment is the candidate to promote. SHA matches the T-7 staging.

### 00:00 CET

- [ ] **Dev**: merge `staging` into `main`. Vercel auto-deploys to production.
- [ ] **Dev**: alternative path if not using auto-deploy: click "Promote to Production" on the staging deployment in Vercel.

### 00:05 CET (production live)

- [ ] **Dev**: confirm `https://papik.cat` resolves to the new build. Curl the homepage, check for the new build's signature (e.g. presence of cookie banner script, Eskimohaus mark, new footer).
- [ ] **Dev**: smoke test 5 critical paths in the browser:
  - `https://papik.cat/`
  - `https://papik.cat/construccio`
  - `https://papik.cat/zones/bellaterra`
  - `https://papik.cat/article-principis-passivhaus`
  - `https://papik.cat/projecte-k-iturbi`
- [ ] **Dev**: verify hreflang canonicalisation working: from CA homepage, click language switcher to ES, then EN, then back. URLs should rotate correctly with no 404s.
- [ ] **Dev**: verify cookie banner active on first visit (incognito).
- [ ] **Dev**: pick 5 random redirects from `redirect-map-full.csv` and confirm each old WP URL 301s to the correct new URL.

### 00:30 CET (post-deploy verification)

- [ ] **Dev**: confirm no spike in 4xx in Vercel analytics.
- [ ] **Dev**: confirm no errors in Vercel runtime logs.
- [ ] **Dev**: tag the production deployment as `launch-2026-06-01` in Vercel for future reference.

---

## T+1 hour (01:00 CET) · GSC and announcements

- [ ] **Dev**: submit new sitemap (`https://papik.cat/sitemap.xml`) to Google Search Console for both `papik.cat` and `www.papik.cat` properties.
- [ ] **Dev**: run Schema.org Rich Results Test on homepage, 1 article, 1 landing, 1 project. Confirm all valid in production.
- [ ] **Dev**: monitor 4xx rate in Vercel analytics. Threshold: < 2% of total requests.
- [ ] **Dev**: monitor Core Web Vitals via Vercel real-user-metrics. Threshold: LCP p75 < 2.5 s, CLS < 0.1, INP < 200 ms.
- [ ] **Lead**: publish launch announcement on selected channels.

---

## T+24 hours (2 June 2026) · First-day audit

- [ ] **Dev**: re-crawl production with Screaming Frog. Compare to expected URL set (255+ from sitemap).
- [ ] **Dev**: identify any unexpected 404s. Cross-reference against `redirect-map-full.csv` to confirm a redirect entry exists for each legacy URL that returns 404.
- [ ] **Dev**: check Vercel analytics: total requests, % 200 / 301 / 404 / 5xx, top 10 URLs, top 10 referrers.
- [ ] **Dev**: hotfix any P0 issue (5xx, broken redirect, broken hreflang cluster). Hotfixes go through `staging` first, even at speed; never push direct to main.
- [ ] **Editorial**: spot-check 10 random URLs in the browser. No regressions vs. T-0 smoke test.
- [ ] **Lead**: publish a 1-day status note to internal stakeholders.

---

## T+7 days (8 June 2026) · First-week audit

- [ ] **Dev**: GSC: validate indexing of new pages. Target: 80%+ of submitted URLs indexed within 7 days.
- [ ] **Dev**: GSC: review "Coverage" report. Document any "Excluded" URLs and confirm each is intentional (e.g. legal-warning-banner pages, deprecated articles).
- [ ] **Dev**: compare WP traffic week-over-week (if WP analytics is still accessible). Target: no caída significativa de tràfic orgànic global.
- [ ] **Dev**: identify any rank regressions on the 5 priority queries (`construir casa Passivhaus Catalunya`, `constructora Sant Cugat`, `llicència derribo Cerdanyola`, branded `papik group`, `eskimohaus`).
- [ ] **Editorial**: review Vercel analytics for top 50 URLs by traffic. Confirm internal linking is funnelling visitors as expected (configurador conversion, contact form submissions, blog → landing → project flow).
- [ ] **Lead**: publish a 7-day status note. Decide: apply Phase 2 fixes if any rank regressions or schema warnings persist.

---

## Rollback plan (use only if critical production issue)

### Trigger conditions

- 5xx rate > 5% sustained over 10 minutes.
- Homepage or any service page returns broken layout for > 5 minutes.
- Critical legal or factual error discovered in published copy that cannot be hotfixed within 30 minutes.
- DNS misconfiguration that cannot be resolved within 15 minutes.

### Rollback procedure

1. **Dev**: open Vercel dashboard. Find the previous production deployment (tagged or by timestamp).
2. **Dev**: click "Promote to Production" on the previous deployment. Takes effect within 30 seconds.
3. **Dev**: confirm `https://papik.cat` now serves the previous build.
4. **Dev**: notify Lead and Editorial. Pause the launch announcement if it has not yet been posted.
5. **Lead**: decide next steps: fix-and-redeploy in same window, or postpone and announce delay.

DNS does not change during deploy, so DNS rollback is never needed unless a misconfiguration was made at T-3.

---

## Post-launch monitoring cadence

- **Day 1**: Vercel logs reviewed every hour for the first 12 hours, then every 4 hours.
- **Week 1**: GSC reviewed daily. Vercel analytics reviewed daily.
- **Month 1**: monthly performance report drafted on day 30. Compare KPIs in `README.md` §7.2.
- **Month 3**: full SEO audit comparing pre/post traffic, ranking deltas on priority queries, configurador conversion. KPIs in `README.md` §7.3.

---

## Contacts

- Project lead: [USER]
- Technical: [USER + COMPAÑERO]
- Legal: [DESIGNATED COUNSEL]
- Emergency: [USER PHONE]

---

## Final go/no-go criteria

Launch proceeds at T-0 only if all of the following are true:

- T-7 exit gate: green or all reds explicitly accepted.
- T-3 DNS, backup, rollback dry-run: green.
- T-1 freeze declared and respected.
- 0 P0 in `qa-findings.json`.
- 0 critical issues in axe DevTools scan.
- All 5 Lighthouse scores ≥ 90 (or accepted gap documented).
- Counsel sign-off in writing or warning banner kept active and accepted.

Otherwise: postpone to next available window. There is no shame in slipping a date for a 30-year-old construction company. There is shame in launching a broken site.
