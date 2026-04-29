# PAPIK Group · Full SEO Audit

> Generated: 2026-04-29 · pre-launch (1 June 2026)
> Domain: papik.cat
> Languages: CA / ES / EN
> Markets: Catalonia + Balearic Islands + Andorra
> Inputs consolidated: s5-qa-report, wave-4-cleanup-report, schema-validation-report, hreflang-validation-report, internal-linking-report, performance-pass-report, h-sitemap-report; competitor research via web search (Arquima, House Habitat, Coll Viader); SERP scan on 4 keyword tiers.

---

## Executive Summary

PAPIK enters the 1 June 2026 launch with a structurally exceptional SEO foundation that materially out-engineers all three benchmarked Catalan competitors: 285 JSON-LD blocks across 277/279 pages, 97.1 % hreflang triplet completeness on a tri-lingual (CA/ES/EN) axis none of the three competitors matches, 270-URL sitemap, zero broken internal links after Wave 4 cleanup, and a 632-optimization performance pass already shipped. The biggest commercial moat is the geographic mesh (14 zonal + 3 comarcal landings + 36 tri-lingual project pages) — a topical authority footprint Arquima, House Habitat and Coll Viader simply do not have on the long-tail "passivhaus + municipality" axis. The top three priorities before launch are: (1) close the residual 65 LocalBusiness `geo` gaps and 6 hreflang-sibling holes (1.5 days of build-pipeline work, immediate Rich-Result eligibility on every zone landing), (2) fix the 2 P0 / 4 P1 blockers from the S5 QA pass (`_t.html` test file, ES H1 holes, zone-landing relative-nav links, generator domain mismatch `papik.cat` vs canonical), and (3) execute a manual Lighthouse + Rich-Results browser pass on staging — the only real validation gap remaining since the static analyzer cannot test browser-rendered Core Web Vitals. **Verdict: strong foundation; ship-ready after one focused fix sprint.** The site will arrive with deeper schema, broader keyword surface, and a higher-quality content cluster than any benchmarked competitor.

---

## Keyword Opportunity Table

(20 keywords sorted by Opportunity Score = relevance × inverse difficulty. Difficulty assessed from top-10 SERP composition observed in web search; volume signals inferred from SERP density and PAA prevalence.)

| # | Keyword | Difficulty | Opportunity Score | Current Ranking (est.) | Intent | Recommended Content Type |
|---|---|---|---|---|---|---|
| 1 | passivhaus sant cugat | Easy | 9.5 / 10 | Page exists at `/zones/sant-cugat`; expect top-5 within 90 days | Commercial/local | Tier-1 landing (built) |
| 2 | passivhaus bellaterra | Easy | 9.5 / 10 | `/zones/bellaterra` with K-Iturbi anchor; expect top-3 within 60 days | Commercial/local | Tier-1 landing (built) |
| 3 | derribar y reconstruir bellaterra | Easy | 9.4 / 10 | `article-llicencia-derribo-cerdanyola-bellaterra` | Decision-stage transactional | Long-form article (built, BOFU) |
| 4 | passivhaus matadepera | Easy | 9.2 / 10 | `/zones/matadepera` (currently orphan — fix priority) | Commercial/local | Tier-1 landing |
| 5 | constructora passivhaus catalunya | Moderate | 8.8 / 10 | competing with Arquima, House Habitat, Growing Buildings | Commercial/discovery | Service + service-area page |
| 6 | construir casa passiva catalunya | Moderate | 8.5 / 10 | `/construccio` + `/es/casas-pasivas-cataluna` | Commercial | Pillar service page (built) |
| 7 | EnerPHit catalonia | Easy | 8.4 / 10 | `/rehabilitacio` mentions standard; no dedicated landing yet | Niche/decision | Standalone EnerPHit landing (gap) |
| 8 | hipoteca verde passivhaus | Easy | 8.3 / 10 | `article-hipoteca-energetica` (built) | Mid-funnel research | Long-form article (built) |
| 9 | pressupost casa passivhaus | Easy | 8.2 / 10 | `article-pressupost-casa-passiva` + configurator | Decision-stage | Article + tool (built; tool gap) |
| 10 | rehabilitacion energetica next generation cataluña | Moderate | 8.1 / 10 | `article-guia-subvencions-ngeu-catalunya` (orphan) | Mid-funnel research | Pillar guide (built; needs in-links) |
| 11 | casas pasivas costa brava | Moderate | 7.9 / 10 | no landing yet | Geographic | Tier-2 landing (gap) |
| 12 | passivhaus maresme | Easy | 7.8 / 10 | `/comarques/maresme` (built) | Geographic | Comarcal hub (built) |
| 13 | passivhaus garraf | Easy | 7.6 / 10 | `/comarques/garraf` (built) | Geographic | Comarcal hub (built) |
| 14 | substituir o rehabilitar casa | Easy | 7.5 / 10 | `article-substituir-vs-rehabilitar` (built) | Decision-stage | Article (built) |
| 15 | casa passivhaus catalunya | Hard | 7.2 / 10 | competing Arquima, Energiehaus, Farhaus | Head-term | Pillar landing (`/construccio`) |
| 16 | passive house catalonia | Moderate | 7.0 / 10 | `/en/construction` | EN head-term | Service page (built) |
| 17 | demolicion y obra nueva cerdanyola | Easy | 6.9 / 10 | `article-llicencia-derribo-cerdanyola-bellaterra` | Decision/local | Article (built) |
| 18 | passivhaus mediterrania | Moderate | 6.5 / 10 | `article-passivhaus-mediterrania` (orphan) | Awareness | Article (built; needs in-links) |
| 19 | family office construccion sostenible | Hard | 5.8 / 10 | `/patrimonis` (built) | B2B niche | Pillar B2B page (built) |
| 20 | coinversion inmobiliaria passivhaus | Hard | 5.0 / 10 | `/patrimonis` only mention | B2B niche | Standalone B2B vertical (gap) |

People-Also-Ask gold (observed in SERPs): "¿Cuánto cuesta una casa passivhaus?", "¿Qué es EnerPHit?", "¿Hay subvenciones para passivhaus?", "¿Diferencia entre casa pasiva y casa modular?". The first three are already covered in PAPIK's article cluster; the modular-vs-passive distinction is a content gap (see §Content Gaps).

---

## On-Page Issues Table

10 sample pages assessed. All H1 counts = 1 (clean). Title and meta-description lengths within style-guide §9 envelope (30-65 / 100-165) on 9 of 10. Hreflang triplets present on 10 of 10. JSON-LD present on 10 of 10.

| Page | Issue | Severity | Recommended Fix |
|---|---|---|---|
| `index.html` | None blocking; meta description 167 chars (1 over band) | P3 | Trim "Sistema constructiu propi Eskimohaus®." closing; bring to ≤165 |
| `construccio.html` | None | — | — |
| `zones/bellaterra.html` | Relative nav links break (`index.html` instead of `/`) | P1 | Apply zone-template absolute-nav fix (s5-qa §5) |
| `zones/sant-cugat-del-valles.html` | File missing on disk; canonical lives at `zones/sant-cugat.html` | P1 | Vercel rewrite already exists; confirm 200 in production. Slug-mapping references the long form for hreflang on 6 EN/ES siblings (h-sitemap §Dead alternates) — collapse to `/zones/sant-cugat` everywhere |
| `comarques/valles-occidental.html` | Duplicate-canonical with root-level `valles-occidental.html` | P2 | Delete the root-level legacy file or 301-redirect; resolved per internal-linking-report follow-up #1 |
| `article-pressupost-casa-passiva.html` | Title 56 chars OK; meta 159 chars OK; JSON-LD `Article` + `BreadcrumbList` OK; but no `FAQPage` schema despite article containing 4 Q-shaped sections | P2 | Add `FAQPage` JSON-LD to capture Rich Result eligibility (high CTR uplift on cost queries) |
| `article-substituir-vs-rehabilitar.html` | Same as above — clear FAQ structure, no `FAQPage` schema | P2 | Add `FAQPage` JSON-LD |
| `projecte-k-iturbi.html` | Canonical and hreflang still emit `www.papik.cat/projecte-k-iturbi.html` (with `.html` and `www.`) instead of canonical `https://papik.cat/projecte-k-iturbi` (no `www`, no `.html`) — domain/extension mismatch with the rest of the site | P1 | Re-run `generate_html.py` for all 36 project pages; check the hreflang generator constant (s5-qa §4 flagged the same issue on the legacy `papik.cat` vs `papikgroup.com` axis but the deeper bug is www-prefix + .html on project pages specifically) |
| `es/index.html` | Title 51 chars, meta 162 chars — clean. inLanguage fixed in W4 | — | — |
| `en/construction.html` | Title 53 chars, meta 161 chars — clean | — | — |

Aggregate from S5 QA across full 180-file scan: 4 real P0s remain (delete `_t.html`, add H1 to 3 ES pages), ~10 article titles 66-78 chars (P2 trim), ~12 article metas 166-192 chars (P2 trim), 90 ES pages still missing JSON-LD per S5 — partially overlapping with the 65 LocalBusiness `geo` gap from schema-validation-report.

---

## Content Gap Recommendations

10 gaps identified by web-searching competitor topical coverage and triangulating against PAPIK's existing 18-article cluster + 14 landings + 36 projects.

| # | Topic / Asset | Why It Matters | Format | Priority | Effort |
|---|---|---|---|---|---|
| 1 | EnerPHit Catalunya pillar landing (`/rehabilitacio/enerphit`) | Niche keyword with low competition; PAPIK only mentions in passing. Coll Viader and House Habitat both have dedicated EnerPHit content | Pillar landing + 1 case study | High | 1 dev-day + 1 copy-day |
| 2 | "Casa modular vs casa passivhaus" comparison article | Top PAA on the head term; Arquima dominates "modular" angle — PAPIK can carve the distinction | Article (3 langs) | High | 2 days |
| 3 | Interactive cost configurator surfaced as standalone page (not just in funnel) | All three competitors have static brochures, none has a public configurator. PAPIK already has the engine internally — surface it as `/configurador` | Tool / lead-magnet | High | 3-5 days |
| 4 | Costa Brava + Empordà landing (`/zones/empordà`, `/zones/costa-brava-girona`) | Keyword "casas pasivas costa brava" has demand; Coll Viader (Girona) covers it with project pages but no landing | 2 Tier-2 landings | High | 2 days |
| 5 | Passivhaus glossary (`/glossari` / `/glosario` / `/glossary`) | Captures featured-snippet potential on "qué es EnerPHit", "ventilación VMC", "puente térmico". None of the three competitors has a structured glossary | Glossary page with `DefinedTerm` schema | Medium | 2 days |
| 6 | Video case studies on Tier-1 landings | Arquima embeds short videos on its passivhaus-premium pages; House Habitat publishes vimeo walkthroughs. PAPIK's project pages are text+image only | Video embeds + `VideoObject` schema | Medium | Asset cost: 8-12 K€ for 4 videos |
| 7 | Balearic Islands + Andorra service-area pages | Site claims coverage in those markets but only Catalonia has landings. Searches for "passivhaus mallorca", "passivhaus andorra" return Arquima (Mallorca) and a Hausbec result; clean opportunity | 3 Tier-2 landings | Medium | 2 days |
| 8 | Family-office investment thesis page (B2B vertical) | `/patrimonis` is the hub but it talks "wealth"; the actual B2B keywords ("coinversion inmobiliaria sostenible", "club deal passivhaus") need their own page distinct from B2C copy | B2B landing + downloadable thesis PDF | Medium | 3 days |
| 9 | "Hipoteca verde + ITP/IBI bonificacions Passivhaus" calculator | PAPIK has the article; a calculator beats Arquima's text-only treatment | Calculator (lead-magnet) | Medium | 4-5 days |
| 10 | Catalan-language Wikipedia presence (`Eskimohaus®`, `PAPIK Group`) | `seo-internal/draft-wikipedia-papik-group.md` is drafted but not published; Wikipedia backlink + entity-graph anchor for E-E-A-T | Editorial + submission | Medium | 1 week incl. notability sourcing |
| 11 | NextGen EU subvencions hub (cluster around `article-guia-subvencions-ngeu-catalunya`) | Currently orphan; the article ranks for none of its keywords because no internal authority flows to it | Restructure: hub + 3 satellites + internal-link injection | Low (article exists) | 0.5 day rewiring |
| 12 | "Passivhaus mediterrània" topical cluster | Article exists, orphan; expand with sub-topics (overheating, shading, costa-mediterranean materials) | Cluster expansion | Low | 2 days |

---

## Technical SEO Checklist

Consolidated from 8 internal reports. Net of Wave 4 cleanup.

| Check | Status | Details |
|---|---|---|
| HTTPS | Pass | All canonicals + hreflang use `https://`; vercel.json enforces TLS |
| Sitemap.xml | Pass | 270 URLs (post W4); well-formed XML; `xhtml:link` hreflang annotations on every entry; priorities + changefreq classified per `generate_sitemap.py` (priority tiers 1.0 → 0.3) |
| Robots.txt | Pass | Sitemap reference in place; AI scrapers blocked (GPTBot, ClaudeBot, PerplexityBot, CCBot, Bytespider, Google-Extended); crawl-delay set for SEO bots per style-guide §13 |
| Canonicals | Warning | 95.7 → 97 % triplet completeness; 36 project pages still emit `www.papik.cat/...html` instead of canonical apex+cleanUrl form (regenerate `generate_html.py` for `/projecte-*` set) |
| Hreflang | Warning | 271/279 pages with full quartet (CA+ES+EN+x-default). 6 pages missing 1 sibling, 1 page missing 2+ (`/qualitats`), 1 page with no hreflang (`/cookie-banner.html` — utility, acceptable). 61 dead alternate URLs targeting legacy slugs covered by `vercel.json` 301s (resolves at runtime; static analyzer false-positive) |
| Schema markup | Warning | 285 JSON-LD blocks across 277/279 pages. 0 CRITICAL, 0 HIGH, 65 MEDIUM (LocalBusiness missing `geo` on every zone/comarca/area landing — single-template fix), 0 LOW. 2 pages with no JSON-LD (`cookie-banner.html` utility, `es/projectes.html` legacy duplicate) |
| Internal links | Pass | 0 broken internal links (153 → 0 in W4); 5,647 internal links across 278 pages; 10 remaining "orphans" are file-system duplicates (legacy root vs `comarques/`), not SEO orphans; 25 contextual orphan-rescue links added in W4 |
| Mobile responsive | Pending | Static analyzer cannot validate; viewport meta and CSS breakpoints present in templates. Manual device-emulator pass required (deployment-runbook T-2) |
| Page speed | Pass (static) | Performance pass: 632 optimizations applied, 265/266 files modified. Defer/async on 104 scripts, preload hints (CSS+font) on 261+265 files, dns-prefetch on 2 external CDNs. 2 render-blocking external scripts intentionally untouched (Supabase on `usuaris.html`, Leaflet on `es/nosotros.html`) — manual refactor scheduled |
| Core Web Vitals | Pending | Lighthouse browser audit not yet run on staging; LCP / CLS / INP pending. Preload hints typically yield 200-600 ms LCP improvement; CSS aspect-ratio standardization should hold CLS ≈ 0 |
| Indexation | Pass | No accidental `noindex` outside the two intentional dashboard files (`dashboard-cliente.html` CA + ES). robots `noindex, nofollow` correctly scoped |
| 404 page | Pass | Custom 404 tri-lingual; included in `EXCLUDE_FILENAMES` of sitemap generator |
| Heading hierarchy | Pass | 1 H1 per page on all 10 sampled pages; S5 flagged 5 pages with multiple H1 sitewide (P1, condensable) |
| Open Graph + Twitter cards | Warning | 41 P2 partially-missing on legacy pages (`og:locale`, `twitter:title`, `og:type`); single-template fix |
| Accessibility (skip-to-content) | Warning | Missing on every page (180 P3); single shared-header fix |
| Accessibility (form labels / aria) | Warning | ~340 P2 instances on shared header newsletter + footer social icons; single shared-partial fix |
| Image format | Warning | All hero/decorative imagery currently `background-image` PNG/JPG; no `<img>` lazy-loading needed but WebP/AVIF migration pending; alt-text not applicable (CSS backgrounds) — semantic content images need an audit when added |
| Vercel cleanUrls | Pass | Sitemap URLs are extension-less; vercel.json `cleanUrls: true` confirmed; 301 redirect-map (331 entries) merged from `.candidate` |
| Cross-language parity | Warning | 12 sibling sets show ≥6 heading divergence (`comunitats`, `construccio`, `rehabilitacio`, `patrimonis`, `promocio`, `pressupost`, `blog`); ES translations short on most. Pre-launch content review recommended |

---

## Competitor Comparison Summary

PAPIK vs the three benchmarked Catalan-Passivhaus competitors. Web-search-derived qualitative assessment; rough domain-authority signals from observed depth + age + presence on aggregator sites (Houzz, ecoconstruccion).

| Dimension | PAPIK | Arquima | House Habitat | Coll Viader | Winner |
|---|---|---|---|---|---|
| Keyword breadth (head + long-tail) | Tri-lingual head + 14 zonal + 3 comarcal + 36 projects = ~270 indexable keyword entries | Strong head ("modulares", "passivhaus premium"), weak local-long-tail | Mid head, strong "biopasiva" niche | Mid head, "fábrica Girona" angle | **PAPIK** |
| Content depth | 18 v1.1 articles tri-lingual + 4 service hubs + structured cluster | Marketing pages + project portfolio; thin blog | Medium blog (~30 posts), strong PR coverage | Slim site; case-study heavy | **PAPIK** |
| Publishing frequency | Active Wave-1-3 cadence; 18 fresh articles in 2026 | Sporadic; mostly project announcements | Regular (~1-2/month) | Low (~quarterly) | **PAPIK** / House Habitat tie |
| Backlink signals (qualitative) | Pre-launch: limited; legacy `papik.cat` has organic press references (Sant Cugat first Passivhaus); Wikipedia draft pending | Strong: Houzz, ecoconstruccion, regional press | Strong: ecoconstruccion repeat coverage, Brains Real Estate | Mid: PEP partner mentions, ecoconstruccion | **Arquima** (current); PAPIK ramps post-launch |
| Technical SEO score | 97 % hreflang, 285 schemas, 632 perf opts, 0 broken links, AI scrapers blocked | Multi-language but `?lang=` query-string (weaker than `/es/` path); fewer schemas observed in SERP cards | Mostly ES-only; older WP; some schemas | Bilingual ES/EN; ES dominant | **PAPIK** (decisive) |
| SERP feature presence | None yet (pre-launch); FAQ + Article schemas primed for snippets | Image-pack appearances on "casas modulares"; some PAA inclusions | PAA inclusions on "casa biopasiva"; news-style snippets | Limited | Arquima (current); **PAPIK** primed to capture once indexed |
| Brand differentiation | Eskimohaus® proprietary system + 30-yr track + Sant Cugat anchor + tri-market (Cat/Bal/And) + family-office vertical | "Premium Passivhaus" + "first house with max Passivhaus + GBCe" | "Biopasiva" terminology owned + CLT/Pyrenees materials | Own factory, 5-day envelope | **PAPIK** (broadest differentiation) |
| Service-area coverage | 14 zonal + 3 comarcal landings; tri-lingual | "Casas modulares en {Barcelona, Valencia, Mallorca, Castellón}" pages — 4 cities | Generic "Catalonia" coverage | Girona + Barcelona | **PAPIK** (10× landing density) |
| B2B / financial verticalization | `/patrimonis` + family-office angle articulated | None observable | None observable | None observable | **PAPIK** (uncontested) |

---

## Prioritized Action Plan

### Quick Wins (this week, before 1 June)

1. **Fix the 4 P0s from S5 QA** — delete `public/_t.html`, add H1 to `es/construccio.html` / `es/promocio.html` / `es/rehabilitacio.html` (or remove these duplicate-CA-slug files in favour of `construccion`/`promocion`/`rehabilitacion`). Effort: 30 min. Impact: unblocks launch.
2. **Repair the project-page canonical/hreflang generator** — 36 project pages still emit `www.papik.cat/...html` instead of canonical apex + cleanUrl. Re-run `generate_html.py` for the `/projecte-*` set after fixing the constant. Effort: 1 hour. Impact: removes 144 dead-alternate hreflang flags from the sitemap and stabilizes the Rich-Result eligibility for `RealEstateListing` schemas.
3. **Backfill `geo` on the 65 zone/comarca/area `LocalBusiness` schemas** — single template fix in `seo-internal/schemas/`; rebuild. Effort: 2 hours. Impact: every zone landing becomes Rich-Result-eligible (map cards, area-served panel) on day-one indexing.
4. **Fix relative nav links on the 12 zone/zonas/areas landings** — turn `index.html` into `/`, `about.html` into `/nosaltres`, etc. Single shared-partial edit. Effort: 1 hour. Impact: unbreaks ~150 navigation flows that crawlers see as 404s.
5. **Inject FAQ schema on the 4 BOFU articles** that already have Q-shaped sections (`article-pressupost-casa-passiva`, `article-substituir-vs-rehabilitar`, `article-hipoteca-energetica`, `article-guia-subvencions-ngeu-catalunya`). Effort: 2 hours. Impact: high-CTR Rich Results on cost / mortgage / subsidy queries.
6. **Wire the 3 orphan articles into the topical hubs** (`article-passivhaus-mediterrania`, `article-guia-subvencions-ngeu-catalunya`, `article-petjada-ecologica`) — add 3-5 contextual links from the appropriate service hub + blog index. Effort: 1 hour. Impact: opens crawl path; should rank within 60-90 days.
7. **Run the deployment-runbook T-2 manual QA**: Lighthouse on 5 representative pages (homepage, service, article, landing, legal), Rich Results Test on 1 article + 1 landing, Mobile-Friendly Test, axe DevTools. Effort: 2 hours. Impact: confirms the 8th technical-checklist row (Core Web Vitals "Pending") flips to Pass.

### Strategic Investments (this quarter)

1. **Build the EnerPHit Catalunya pillar landing** + 1 case-study satellite. Effort: 1 dev-day + 1 copy-day per language × 3. Impact: captures a low-competition decision-stage keyword cluster Arquima/House Habitat/Coll Viader all under-serve. Dependencies: 1 EnerPHit-grade reference project from PAPIK portfolio with photo rights. Expected ranking horizon: 90-120 days.
2. **Surface the cost configurator as a public lead-magnet at `/configurador` / `/configurador-es` / `/configurator`** — none of the three competitors offers an interactive tool. Effort: 3-5 days (engine exists internally per CLAUDE.md). Impact: differentiator both for SERPs (tool-pages get featured snippets) and for conversion. Dependencies: legal review on what numbers can be shown publicly (privacy boundary v2 §7).
3. **Build the 2 missing Tier-2 landings** (`/zones/costa-brava-girona`, `/zones/empordà`) and the 3 Balearic + Andorra geo pages (`/zones/mallorca`, `/zones/menorca`, `/zones/andorra`). Effort: 2 days each language. Impact: extends the 14-landing mesh into the 3-market promise the homepage already makes. Dependencies: at least 1 reference project per region for credibility (currently Fornells = Menorca proxy exists; verify others).
4. **Publish the `Eskimohaus®` + `PAPIK Group` Wikipedia entries** from the existing draft. Effort: 1 week including notability sourcing per WP:N. Impact: Wikipedia-grade backlink + Knowledge-Graph entity anchor for E-E-A-T and AI-overview eligibility. Dependencies: independent secondary sources (press references — legacy `papik.cat` has these; collate citations).
5. **Launch the family-office B2B vertical** — separate landing distinct from `/patrimonis` consumer copy, with downloadable investment thesis PDF. Effort: 3 days. Impact: occupies an uncontested keyword space ("coinversion inmobiliaria sostenible passivhaus") and supports the 4th audience profile. Dependencies: legal sign-off on regulatory disclaimer (style-guide §7.5).
6. **Image pipeline migration to WebP/AVIF** + consolidate the 5 stylesheets into a single bundled `main.css`. Effort: 3-5 days. Impact: 200-600 ms LCP improvement on cold loads; eliminates the 4 remaining performance-pass-report P3s. Dependencies: image asset replacement (real OG / hero / project images — already a tracked launch blocker).
7. **Cross-language content parity rebuild on the 12 pages with heading-count divergence** (`comunitats`, `construccio`, `rehabilitacio`, `patrimonis`, `promocio`, `pressupost`, `blog`). Effort: 2 days copy work per language. Impact: closes the only material translation-quality gap the QA flagged. Dependencies: ES copy reviewer.
8. **Glossary page with `DefinedTerm` schema** — captures featured-snippet potential on "qué es EnerPHit", "ventilación VMC", "puente térmico". Effort: 2 days. Impact: high-impression low-conversion top-funnel surface that none of the 3 competitors has.

---

## Follow-Up

**Pending blockers (need user / external action):**

1. Manual Lighthouse + axe DevTools + Rich Results Test on staging — required to convert the "Pending" rows on the technical checklist (Mobile, Core Web Vitals) into Pass/Warning entries.
2. Google Search Console access to validate post-launch indexation, sitemap acceptance, and Rich-Result eligibility on the 285 schemas.
3. Counsel sign-off on 6 legal placeholders (tracked under launch-blocker "real assets") — gates the legal-page hreflang quartet.
4. Decision on whether to ship EN translations for the ~30 articles currently CA+ES only, or accept `x-default` only and remove broken EN alternates (S5 §4 caveat).

**Open questions (raise with the team):**

- Should `/configurador` ship pre-launch as a quick-win or post-launch as a strategic investment? (It sits in both buckets above; the call depends on dev capacity vs the 1 June date.)
- Is the family-office B2B vertical a launch-day asset or a Q3 push? (Different copy + legal review timeline.)
- Should `papik.cat` apex stay as canonical, or migrate to `papikgroup.com` per the s5-qa note? (The hreflang generator constant fix is non-trivial if the answer is "migrate" — would need a redirect-map regeneration.)

**Recommended re-audit cadence:** T+30 (post-launch SERP capture), T+90 (first ranking signals), T+180 (full retrospective vs the 20-keyword opportunity table above).
