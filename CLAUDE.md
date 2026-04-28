# PAPIK Group · Project Memory (CLAUDE.md)

> Master orientation file for any agent or human entering the `papik-web` project. Skim this first, then jump to the relevant artefact.
>
> Last updated · 28 April 2026 · post-S5 (pre-launch QA complete)

---

## Current state summary

PAPIK Group is a Passivhaus constructor in Catalonia (30 years, proprietary system Eskimohaus®). The legacy WordPress at `papik.cat` is being replaced on **1 June 2026** by a static build deployed on Vercel.

**Project phase · post-Wave-3, pre-launch.**

- Phases S1-S5 + Wave 1-3 complete: strategy, briefs, copy v1.1 (CA + ES + EN), HTML build, QA pass, project pages tri-lingual, Tier-2 landings, performance pass.
- **268 HTML pages** in production across three languages.
- **36 project pages tri-lingual** (`/projecte-*` CA, `/es/proyecto-*`, `/en/projects/*`).
- **14 landings tri-lingual** · 4 Tier-1 (Bellaterra, Sant Cugat, Matadepera, Sant Quirze) + 5 Tier-2 (Cabrils, Alella, Premià de Dalt, Tiana, Cerdanyola) + 5 Tier-2 batch 3 (Argentona, Castellar, Llavaneres, Sitges, Vilanova).
- **3 comarcal hubs tri-lingual** · Vallès Occidental, Maresme, Garraf.
- **~18 v1.1 articles tri-lingual** (~54 article files total).
- **Hubs tri-lingual** · blog, projectes, 404.
- **Legal placeholders** · 6 CA + 3 EN (counsel sign-off pending).
- vercel.json with 301 redirects merged from `.candidate`. sitemap.xml has 255 URLs. robots.txt blocks AI scrapers (GPTBot, ClaudeBot, PerplexityBot, CCBot, Bytespider, Google-Extended).
- `generate_html.py` is the build pipeline; `generate_sitemap.py` regenerates the sitemap.
- Remaining blockers: counsel sign-off (6 docs), real assets (NIF, cookie inventory, OG images, project images), manual QA (Lighthouse, axe, Mobile-Friendly, Rich Results).

For the full status table see `seo-internal/README.md` §2 (status badge table).

---

## Key paths

### Documentation (read first)

- `seo-internal/README.md` · master orchestration document, status by phase
- `seo-internal/style-guide-editorial.md` · editorial v1.3 (voice, slug taxonomy, hreflang invariants, parity rule, privacy v2, cross-linking, technical metadata, project page conventions, Tier-2 landings, performance defaults, robots policy)
- `seo-internal/deployment-runbook.md` · 1 June 2026 launch runbook
- `seo-internal/schemas/README.md` · JSON-LD matrix per page type

### Copy artefacts

- `seo-internal/copy/rewrites/` · v2 of CA copy (homepage, services, articles, landings, legal)
- `seo-internal/copy/translations/es/` · ES copy (28 files)
- `seo-internal/copy/translations/en/` · EN copy (26 files)
- `seo-internal/copy/rewrites/legal/` · CA legal placeholders (3)
- `seo-internal/copy/translations/{es,en}/legal/` · ES + EN legal placeholders (3 + 3)

### Technical artefacts

- `seo-internal/slug-mapping.json` · canonical CA↔ES↔EN slug registry (single source of truth for hreflang)
- `seo-internal/redirect-map-full.csv` · 331 entries
- `seo-internal/vercel-rewrites-snippet.json` · already mergeed into `vercel.json`
- `vercel.json` · production config (root)
- `generate_html.py` · build pipeline (root)
- `generate_sitemap.py` · sitemap regenerator (root)
- `public/` · build output (sitemap, robots, HTML pages)

### Reports

- `seo-internal/s3-status-report.md`
- `seo-internal/s4-build-report.md`
- `seo-internal/s5-qa-report.md`
- `seo-internal/qa-findings.json` (full qa-script.py output)
- `seo-internal/legal-review-report.md`
- `seo-internal/vercel-merge-diff.md`

---

## Slug map quick reference

Full taxonomy at `style-guide-editorial.md` §4. Snapshot:

### Toponyms · keep Catalan across all three languages

`bellaterra`, `sant-cugat-del-valles`, `sant-quirze-del-valles`, `matadepera`, `argentona`, `castellar`, `llavaneres`, `sitges`, `vilanova`, `valles-occidental`, `maresme`, `garraf`.

### Service words · translate properly per language

| CA | ES | EN |
|---|---|---|
| construccio | construccion | construction |
| rehabilitacio | rehabilitacion | retrofit |
| promocio | promocion | development |
| patrimonis | patrimonios | wealth |
| comunitats | comunidades | communities |
| nosaltres | nosotros | about |
| projectes | proyectos | projects |
| pressupost | presupuesto | budget |
| usuaris | usuarios | users |
| premsa | prensa | press |
| certificacions | certificaciones | certifications |

### EN articles · semantic translation, not transliteration

`derribar-construir-passos` → `demolish-and-rebuild-steps` · `revolucio-fusta` → `wood-revolution` · `petjada-ecologica` → `ecological-footprint` · `apagada-2025` → `blackout-2025`.

### Stable slugs (do not change for SEO continuity)

`passivrooms` (despite brand `Passive Rooms`) · `k-vallor` (despite brand `K-Vall d'Or`).

---

## Style guide pointer

Always read `seo-internal/style-guide-editorial.md` v1.3 before writing or editing any copy. Key sections:

- §2.7 · No em-dashes (`—`)
- §2.8 · Adult register, not didactic
- §3.5 · Prose by default, bullets only for processes / heterogeneous taxonomies / checklists
- §4 · Slug taxonomy (CA/ES/EN)
- §5 · Hreflang invariants (CA + ES + EN + x-default; x-default → CA; canonical self)
- §6 · Tri-lingual parity rule (no article ships in only one language)
- §7 · Privacy boundary v2
- §8 · Cross-linking taxonomy (3 article cross-links · 3-5 projects on landings)
- §9 · Technical metadata (title 30-65, meta 100-165, OG fallback chain, JSON-LD matrix)
- §10 · Project page conventions (`/projecte-X` / `/es/proyecto-X` / `/en/projects/X`, RealEstateListing schema, no addresses, no €/m²)
- §11 · Comarcal and Tier-2 landing tier (anchor proximity rule)
- §12 · Performance defaults (defer/async, lazy/eager, preload CSS+font, no Google Fonts)
- §13 · Robots and crawl policy (block AI scrapers, crawl-delay SEO bots)

---

## "Don't repeat" warnings

Hard-won lessons from this project. If you find yourself doing one of these, stop and re-read the relevant section.

### Editorial

- **Never use em-dashes** (`—`). Substitute with comma, parenthesis, semicolon, colon, or full stop. AI detectors flag them; Catalan editorial tradition rarely uses them. (style-guide §2.7)
- **Never write didactic transitions** ("Imagineu que...", "Vegem com funciona", "És important destacar que"). Adult professional register only. (style-guide §2.8)
- **Never default to bullet lists.** Prose is the default. Bullets only for numbered processes, heterogeneous taxonomies, operational checklists. (style-guide §3.5)
- **Never use commercial superlatives without data** ("els millors", "líders", "innovador" without proof). Substitute with concrete numbers. (style-guide §2.2)
- **Never use exclamation marks** beyond one per article (ideally zero). (style-guide §2.5)

### Privacy and legal

- **No internal pricing data** ever leaks to public copy (the 14 budgets, configurator logic, margins, conversion rates).
- **No specific mortgage rates / LTVs / terms** in any article. Cite ranges with public sources. (style-guide §7.2)
- **No identified clients without written consent** (Ponsa-rule). Family names, investment figures attributed to identifiable clients are forbidden without a dated written release. (style-guide §7.3)
- **No exact addresses on project pages.** Municipality + comarca only; never street + number. (style-guide §7.4)
- **Investment-adjacent content** must carry the regulatory disclaimer. (style-guide §7.5)
- **No nominal competitor comparisons** (Arquima, Canexel, Coll Viader, Farhaus, House Habitat). Compare to construction systems, not companies.

### Technical

- **Never re-run a non-idempotent regex bulk-rename** without a guard checking the substitution is not already applied. The `construccio → construccion → construccionn` "double-n bug" cost real time. (style-guide §4.4)
- **Never edit hreflang or canonical tags by hand.** They are generated by `generate_html.py` from `slug-mapping.json`. Editing manually breaks the cluster.
- **Never publish an article in only one language.** All three (CA + ES + EN) ship together or none. (style-guide §6)
- **Never break the slug-stability rule.** Once a slug is published, changes require a redirect-map entry. SEO continuity > retroactive linguistic perfection.
- **Never publish a page without at least one JSON-LD schema** appropriate to its type (matrix at style-guide §9.4).

### Process

- **Never assume.** If a fact is not in the briefs, the audit, or the existing copy, do not invent it. PAPIK has a strict factual-claim regime; unverified claims are a regulatory risk on `/patrimonis` and the financial articles.
- **Never overwrite without backup.** Vercel.json keeps a `.previous` for rollback; build outputs in `BACKUPS/`.
- **Never assume project location — read legacy HTML first.** K-Codines, K-Hostalets, K-Malats, K-Maristany, K-Orio, K-Premia and PassivPalau all had wrong assumed locations until verified against legacy WP HTML. The project name does not always encode the municipality. Always crack open the legacy page and confirm before drafting the fitxa.
- **Always run `generate_html.py` AFTER all language siblings exist.** The hreflang block reads `slug-mapping.json` and self-references the trio at build time. Building CA before ES/EN exist produces `404` hreflang targets and breaks the cluster. Order: write all three copy files, register slug-mapping, THEN build.
- **Tier-2 landings anchor to the CLOSEST direct project, not the famous one.** Cabrils landing references K-Llavaneres (4 km, Maresme), not K-Iturbi (35 km, Sant Cugat) just because K-Iturbi is iconic. Proximity beats fame for landing relevance and conversion. (style-guide §11.3)

---

## Launch context

Date: **1 June 2026 · 00:00 CET**.

Refer to `seo-internal/deployment-runbook.md` for T-7 → T+7 operational steps. Refer to `seo-internal/README.md` §2 for current blocker status.
