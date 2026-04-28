# Vercel Merge · Diff Report

Generated: 2026-04-28 · Source: wp-redirects-proposed.json (post Q&A) + current vercel.json

## Summary

- Total redirects in current vercel.json: 34
- Total redirects in candidate: **301** (after manual cleanup)
- Net new (proposal merged + host rule): **267**

## Manual fixes applied post-agent run (2026-04-28)

1. **Typo fix:** `/es/construccionn` (7 destinations) → `/es/construccion`. Bug introduced by Fix 1 regex.
2. **Self-loop removal:** stripped 9 self-loop entries (2 introduced by Fix 1 + 7 pre-existing intentional placeholders for legal pages and `/projectes`). All useless: a redirect to itself is noop. Legal pages and `/projectes` will serve their HTML directly when the request hits.
3. **Q3 patch:** `/com-construir-la-teva-casa` → `/com-construim-la-teva-casa` was pointing to a page that doesn't exist on new site. Patched to → `/construccio` (per Q3 decision).

## Fixes Applied

### Fix 1 · ES slug normalisation
Number of destinations rewritten: 25
- In proposal: 18
- In existing vercel.json: 7

Sample changes:
- `/es/proyectos` → `/es/proyectos` (was `/es/projectes`)
- `/es/proyectos/:slug*` → `/es/proyectos` (was `/es/projectes`)
- `/es/casa-pasiva` → `/es/construccion` (was `/es/construccio`)
- `/es/papik-cases-passives-reconocida-por-su-excelencia-empresarial` → `/es/nosotros` (was `/es/nosaltres`)
- `/es/prioridades-a-la-hora-de-hacer-tu-casa-a-medida` → `/es/construccionn` (was `/es/construccion`)
- existing `/es/presupuesto` → `/es/presupuesto` (was `/es/pressupost`)
- existing `/es/presupuesto-gratuito` → `/es/presupuesto` (was `/es/pressupost`)
- existing `/es/diario` → `/es/boletin` (was `/es/butlleti`)
- existing `/es/boletin-de-noticias` → `/es/boletin` (was `/es/butlleti`)
- existing `/es/lista-de-proyectos-activos` → `/es/proyectos` (was `/es/projectes`)

### Fix 2 · /author bug patch
- /author/:slug*: /empresa -> /nosaltres
- /es/author/:slug*: /es/empresa -> /es/nosotros

### Fix 3 · Host canonicalisation
Added top-level rule (FIRST in array): `www.papik.cat/* → https://papik.cat/$1` (301).

### Fix 4 · Field strip + merge
- `_classification` removed: 275 entries
- `_note` removed: 38 entries
- `_section` documentation markers skipped: 10
- Class E duplicates skipped: 1
- Class F obsolete (404 intended) skipped: 0
- Source already present in existing vercel.json (skipped to avoid Vercel duplicate-source error): 0
- Internal duplicates within proposal removed: 0

## Merged Sections

| Section | Count |
|---|---|
| 1. Host canonicalisation | 1 |
| 2. Existing patched | 34 |
| 3. Q-decision specific (Q1–Q7) | 24 |
| CA articles/pages | 93 |
| ES articles/pages | 97 |
| Projects (CA) | 39 |
| Projects (ES) | 38 |
| Categories/tags catch-alls | 0 |
| Feeds (Q7) | 2 |
| Legal pages (Q2) | 6 |
| wp-admin / feed leftovers | 0 |
| **TOTAL** | **310** |

## Unresolved (manual review needed)

- Note: current `vercel.json` actually contains **34** redirects (user briefed "33"). Treated all 34 as authoritative existing rules.
- **Self-loops introduced by Fix 1** (source == destination after ES normalisation). These are harmless 301-to-self but wasteful — consider removing in a follow-up:
  - `/es/presupuesto → /es/presupuesto` (was `/es/presupuesto → /es/pressupost`)
  - `/es/proyectos → /es/proyectos` (proposal Class A entry, now self-loop after normalisation)
- **Pre-existing self-loops** (intentional per Q2 — placeholders kept for stability): `/avis-legal`, `/politica-de-privacitat`, `/politica-de-cookies`, `/es/aviso-legal`, `/es/politica-de-privacidad`, `/es/politica-de-cookies`, `/projectes`. Leaving as-is.

## Validation Checklist (user must run before deploy)

- [ ] `vercel dev` locally — confirm no JSON syntax errors
- [ ] Spot-check 5 random redirects in browser
- [ ] Verify host canonicalisation: `curl -I https://www.papik.cat/test` returns 301 to `https://papik.cat/test`
- [ ] Confirm no duplicate `source` entries (Vercel rejects duplicates)
- [ ] Test legal page redirects don't 404 (placeholders must be built and deployed first)
- [ ] Verify `/es/proyectos` and `/es/proyecto-*` slugs resolve on the new site (Fix 1 assumes ES URLs are now Spanish-slugged)
- [ ] Verify `/es/construccion`, `/es/rehabilitacion`, `/es/nosotros`, `/es/presupuesto`, `/es/contacto`, `/es/boletin`, `/es/aviso-legal`, `/es/politica-de-privacidad` exist on the new site

## Next Steps

1. User reviews this diff
2. User runs validation checklist
3. If clean: replace `vercel.json` with `vercel.json.candidate` content
4. Push to staging, smoke test 10–15 critical paths
5. Deploy to production
