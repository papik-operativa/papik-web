# Duplicate Comarca Files Resolution Report

Date: 2026-04-27

## Context

Comarcal hub pages had duplicates at root level (`/maresme`, `/garraf`, `/valles-occidental`) competing with the canonical `/comarques/*`, `/es/comarcas/*`, `/en/regions/*` URLs. Canonical tags in the published HTML confirm `/comarques/...`, `/es/comarcas/...`, `/en/regions/...` as the truth.

## Step 1 · Existence audit

| Path | Existed? | Action |
|---|---|---|
| `/public/maresme.html` | yes | deleted |
| `/public/garraf.html` | yes | deleted |
| `/public/valles-occidental.html` | yes | deleted |
| `/public/es/maresme.html` | yes | deleted |
| `/public/es/garraf.html` | yes | deleted |
| `/public/es/valles-occidental.html` | yes | deleted |
| `/public/en/maresme.html` | no | skip |
| `/public/en/garraf.html` | no | skip |
| `/public/en/valles-occidental.html` | yes | deleted |

## Step 2 · Files deleted (7)

- `/Users/trisfisas/Desktop/CÓDIGO/papik-web/public/maresme.html`
- `/Users/trisfisas/Desktop/CÓDIGO/papik-web/public/garraf.html`
- `/Users/trisfisas/Desktop/CÓDIGO/papik-web/public/valles-occidental.html`
- `/Users/trisfisas/Desktop/CÓDIGO/papik-web/public/es/maresme.html`
- `/Users/trisfisas/Desktop/CÓDIGO/papik-web/public/es/garraf.html`
- `/Users/trisfisas/Desktop/CÓDIGO/papik-web/public/es/valles-occidental.html`
- `/Users/trisfisas/Desktop/CÓDIGO/papik-web/public/en/valles-occidental.html`

## Step 3 · Redirects added to vercel.json (7 · permanent 301)

Inserted after the host-canonicalisation rule, before the existing `/es/inicio` redirect.

| source | destination |
|---|---|
| `/maresme` | `/comarques/maresme` |
| `/garraf` | `/comarques/garraf` |
| `/valles-occidental` | `/comarques/valles-occidental` |
| `/es/maresme` | `/es/comarcas/maresme` |
| `/es/garraf` | `/es/comarcas/garraf` |
| `/es/valles-occidental` | `/es/comarcas/valles-occidental` |
| `/en/valles-occidental` | `/en/regions/valles-occidental` |

`/en/maresme` and `/en/garraf` redirects intentionally not added (no duplicate file existed → nothing to redirect).

`vercel.json` reparses as valid JSON (verified with `python3 -c "import json; json.load(...)"`).

## Step 4 · slug-mapping.json updates (3)

The three geo-hub entries used stale `/zones/`, `/es/zonas/`, `/en/areas/` paths that did NOT match the deployed canonical URLs in the actual HTML files. Updated to align with deployed canonicals (the source of truth):

| id | before (CA / ES / EN) | after (CA / ES / EN) |
|---|---|---|
| `zones-valles-occidental` | `/zones/valles-occidental` · `/es/zonas/valles-occidental` · `/en/areas/valles-occidental` | `/comarques/valles-occidental` · `/es/comarcas/valles-occidental` · `/en/regions/valles-occidental` |
| `zones-maresme` | `/zones/maresme` · `/es/zonas/maresme` · `/en/areas/maresme` | `/comarques/maresme` · `/es/comarcas/maresme` · `/en/regions/maresme` |
| `zones-garraf` | `/zones/garraf` · `/es/zonas/garraf` · `/en/areas/garraf` | `/comarques/garraf` · `/es/comarcas/garraf` · `/en/regions/garraf` |

Note: there are still many `/zones/...` entries (geo-landings: sant-cugat, sant-quirze, bellaterra, matadepera, argentona, llavaneres, mataro, premia, etc.) with `exists: false`. These are out of scope for this duplicate-resolution task; if those pages are also intended to live under `/comarques/...` or another path, that requires a separate alignment pass.

`slug-mapping.json` reparses as valid JSON.

## Step 5 · Verification

- Deletions confirmed: all 7 root-level files no longer exist (ls returns "No such file or directory" for each).
- Canonical files intact: all 9 files under `/comarques/`, `/es/comarcas/`, `/en/regions/` still present.
- `vercel.json` parses cleanly · 7 comarca redirects in place.
- `slug-mapping.json` parses cleanly · 3 geo-hub entries aligned to deployed canonicals.

## Summary

7 duplicate HTML files removed · 7 permanent 301 redirects added · 3 slug-mapping geo-hub canonicals corrected · 0 blockers.
