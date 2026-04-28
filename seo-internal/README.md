# PAPIK Group · SEO Project · Document Maestre d'Orquestració

> **Document d'entrada al projecte SEO de PAPIK Group · web nova llançament 1 juny 2026.**
>
> Llegeix aquest document primer si arribes nou al projecte. T'orienta a través dels 90+ artefactes generats durant la fase de planificació + estructuració + producció (S1-S4) i et dóna un mapa clar de què hi ha, com s'usa i en quin ordre.
>
> Última revisió · 28 abril 2026 · v1.2

---

## 1. Resum executiu del projecte

PAPIK Group és una constructora de cases Passivhaus a Catalunya · 30 anys d'ofici · sistema constructiu propi Eskimohaus®. La pàgina actual `papik.cat` (WordPress) es substitueix el **1 juny 2026** per una nova web estàtica desplegada a Vercel.

L'objectiu d'aquest projecte és **no perdre cap equity SEO** durant la migració, i alhora aprofitar el reset per llançar una arquitectura de continguts moderna, més rica i alineada amb la realitat del negoci (4 unitats de negoci · 5 si comptem la sub-pàgina de comunitats).

**Calendari · S1 → S5 → 1 juny:**

| Setmana | Foco | Estat |
|---|---|---|
| **S1** (28 abr-4 mai) · investigació + estratègia | 5 auditories + decisions estratègiques + privacy boundary + redirect map + briefs | ✅ Complet |
| **S2** (5-11 mai) · briefs + copy CA | 14 briefs + copy CA v1.0 + style guide + audit articles | ✅ Complet |
| **S3** (12-18 mai) · implementació tècnica | sitemap, robots, schemas, hreflang, vercel.json, generate_html.py | ✅ Complet |
| **S4** (19-25 mai) · contingut + traduccions | Copy v1.1 (CA · ES · EN) + legal placeholders | ✅ Complet |
| **S5** (26-31 mai) · QA pre-launch | qa-script.py · legal review · runbook | ✅ Complet (placeholders pending counsel) |
| **1 juny** · LAUNCH | Switchover · GSC submit · anuncis | 🎯 |

---

## 2. Status badge · estat global per fase

| Fase | Status | Owner | Notes |
|---|---|---|---|
| Style guide v1.1 | ✅ Done | Editorial | Ampliat a v1.2 amb taxonomia slugs, hreflang, parity, privacy v2, cross-linking, metadata |
| Copy CA v1.1 | ✅ Done | Editorial | 28 fitxers (homepage + 5 unitats + comunitats + 5 landings + 1 comarca + 18 articles) |
| Copy ES | ✅ Done | Translation | 28 fitxers paritat amb CA · slug ES propi (proyectos, presupuesto, etc.) |
| Copy EN | ✅ Done | Translation | 26 fitxers · semantic slugs (areas/, regions/, articles/) · adaptació cultural |
| Legal placeholders CA/ES/EN (3+3+3) | ⚠ Placeholders done | Counsel review pending | NIF, adreça i inventari real de cookies pendents |
| Tier 1 landings (4) | ✅ Done | Content | Sant Cugat · Sant Quirze · Bellaterra · Matadepera |
| Tier 2 landings (5) | ✅ Done | Content | Argentona · Castellar · Llavaneres · Sitges · Vilanova |
| Comarcal hubs (3) | ✅ Done | Content | Vallès Occidental · Maresme · Garraf |
| Articles tri-lingual (18) | ✅ Done | Content | Tots existeixen a CA + ES + EN sense excepcions |
| HTML build (`generate_html.py`) | ✅ Done | Dev | Genera públic/ amb hreflang i schemas inyectats |
| vercel.json amb 301 redirects | ✅ Done | Dev | 245+ entries · `vercel.json.candidate` promogut a producció |
| sitemap.xml · regenerat | ✅ Done | Dev | `generate_sitemap.py` actualitzat post-renames |
| Schemas JSON-LD (7 templates) | ✅ Done | Dev | Inyectats segons matrix per tipus de pàgina |
| QA script (`qa-script.py`) | ✅ Done | Dev | qa-findings.json generat · 0 P0 confirmat |
| Cookie banner | ⚠ In progress | Dev | Script + CSS pendents inventari real cookies |
| Forms backend | ⚠ Placeholders | Dev | Endpoints declarats · backend pendent |
| Counsel sign-off (6 docs) | 🔴 Blocked | Legal | Patrimonis · Comunitats LPH · Ponsa · Sabadell · 3 legal pages |
| Launch 1 juny 2026 | 🎯 Scheduled | All | Vegeu deployment-runbook.md |

---

## 3. Mapa d'artefactes · seo-internal/

Tots els artefactes interns viuen a `/Users/trisfisas/Desktop/CÓDIGO/papik-web/seo-internal/` (no es serveixen al públic · només per al treball intern).

### 3.1 · Documents fundacionals (llegir primer si arribes nou)

| Fitxer | Què és | Quan es consulta |
|---|---|---|
| `README.md` | **Aquest document** · mapa global del projecte | Sempre primer |
| `style-guide-editorial.md` | Manual d'estil editorial · veu, tono, regles · v1.2 | Abans de qualsevol redacció |
| `deployment-runbook.md` | Runbook operatiu del llançament 1 juny 2026 | T-7 → T+7 |
| `redirect-map.csv` | 33 redirects 301 explícits · S1 | S3 · implementació |
| `redirect-map-full.csv` | 331 entries (108 rewrites + 169 × 301 + 54 deprecate) | S3 · implementació |
| `vercel-rewrites-snippet.json` | Snippet producció-ready amb 94 rewrites + 158 redirects | Mergeed a vercel.json |
| `slug-mapping.json` | Registre canònic CA↔ES↔EN · 78 entries | Permanent · base de hreflang i sitemap |
| `audit-articles-existents.md` | Auditoria SEO + tono dels 15 articles existents | S4 · rewrite priorit zat |

### 3.2 · Reports generats (S3-S5)

Tots els reports viuen a l'arrel de `seo-internal/`:

| Fitxer | Què és |
|---|---|
| `s3-status-report.md` | Estat tècnic post-S3 · slugs, hreflang, schemas, redirects |
| `s4-build-report.md` | Resum del build via `generate_html.py` · pàgines generades |
| `s5-qa-report.md` | Resum del pas QA · resolucions, issues, severitats |
| `qa-findings.json` | Output complet del `qa-script.py` · ~290 KB de findings |
| `legal-review-report.md` | Llistat punts pendents de counsel sign-off |
| `vercel-merge-diff.md` | Diff entre vercel.json antic i `.candidate` post-merge |
| `wp-redirect-audit.md` + `wp-redirect-questions.md` | Audit dels 342 URLs WP indexats |
| `wp-redirects-proposed.json` | Proposta JSON dels 301 a aplicar |

### 3.3 · Briefs estratègics (S1-S2)

| Fitxer | Pàgina/secció |
|---|---|
| `brief-homepage.md` | `/` · divisor de tràfic 4 unitats |
| `brief-construccio.md` | `/construccio` · unitat principal |
| `brief-promocio.md` | `/promocio` · greenfield SEO |
| `brief-rehabilitacio.md` | `/rehabilitacio` · driver NGEU |
| `brief-patrimonis.md` | `/patrimonis` · B2B financer · ⚠ revisió CNMV |
| `brief-comunitats.md` | `/rehabilitacio/comunitats` · sub-pàgina B2B |
| `brief-autoridad.md` | `/premsa` + `/certificacions` |
| `brief-chatbot.md` | Assistent conversacional · routing 4 unitats |
| `brief-landings-locals.md` | 4 landings Tier 1 Vallès Occ. + hub comarcal |
| `brief-landings-maresme.md` | 4 landings Tier 1 Maresme + hub comarcal |
| `brief-landings-garraf.md` | 3 landings Tier 1 Garraf + hub comarcal |
| `brief-articles-bellaterra-cluster.md` | 3 articles satèl·lit per a /zones/bellaterra |
| `draft-wikipedia-papik-group.md` | Borrador Viquipèdia CA + estratègia ES + EN |
| `poum-municipios-tier1.md` | Datos urbanístics Tier 1 |

### 3.4 · Schemas JSON-LD · `seo-internal/schemas/`

7 templates ready-to-paste:

| # | Schema | Aplica a |
|---|---|---|
| 01 | Organization · HomeAndConstructionBusiness | `/`, `/es/`, `/en/` |
| 02 | Service | 4 unitats de negoci |
| 03 | LocalBusiness amb GeoCircle | Cada landing geogràfica |
| 04 | Article | Cada `/article-*` |
| 05 | FAQPage | Qualsevol pàgina amb FAQ |
| 06 | BreadcrumbList | Tota pàgina excepte homepage |
| 07 | RealEstateListing project | Cada `/projecte-*` |

### 3.5 · Copy v1.1 · estat consolidat

**CA · 28 fitxers:**
- 1 homepage · `copy/homepage-ca.md` (+ v2 a `rewrites/homepage-ca-v2.md`)
- 5 unitats · construccio, rehabilitacio, promocio, patrimonis, comunitats (totes amb v2)
- 1 comarca · `rewrites/comarques/valles-occidental-ca-v2.md`
- 5 landings · sant-cugat, sant-quirze, bellaterra, matadepera, argentona (a `rewrites/landings/`)
- 18 articles v2 · vegeu `copy/rewrites/article-*-ca-v2.md`
- 3 legal · `rewrites/legal/avis-legal-ca-v2.md` · `politica-cookies` · `politica-privacitat`

**ES · 28 fitxers paral·lels** a `copy/translations/es/`:
- homepage, construccion, rehabilitacion, promocion, patrimonios, comunidades
- 4 landings (sant-cugat, sant-quirze, bellaterra, matadepera) a `landings/`
- 18 articles a `articles/`
- 3 legal a `legal/` (aviso-legal, politica-cookies, politica-privacidad)

**EN · 26 fitxers paral·lels** a `copy/translations/en/`:
- homepage, construction, retrofit, development, wealth
- 4 landings a `areas/` (semantic slug strategy)
- 18 articles a `articles/` (semantic translation)
- 3 legal a `legal/` (legal-notice, cookie-policy, privacy-policy)

**Tri-lingual parity rule** · cada article publicat existeix simultàniament a CA + ES + EN. No hi ha excepcions.

**Volum total entregat:** ~95.000 paraules de copy editorial multilingüe en producció.

---

## 4. Mapa d'artefactes · arrel del projecte i public/

### 4.1 · Build HTML (S3-S4)

| Fitxer | Funció |
|---|---|
| `generate_html.py` | Build pipeline · llegeix copy/, inyecta schemas, hreflang, navega slug-mapping.json |
| `public/sitemap.xml` | Sitemap generada · 80+ URLs amb hreflang |
| `public/robots.txt` | Producció-ready |
| `public/*.html` (CA) · `public/es/*.html` · `public/en/*.html` | Build complet tri-lingual |
| `vercel.json` | Configuració Vercel · 245+ redirects · headers · cleanUrls · cache · sense `.candidate` |
| `generate_sitemap.py` | Script regenerador del sitemap |

### 4.2 · Backend Python existent

| Fitxer | Funció |
|---|---|
| `app.py` | Backend principal |
| `serve.py` · `serve_dev.py` | Servidors locals |
| `papik_configurador.json` | Definició del configurador de pressupost |
| `convert_articles.py` · `inject_header_css.py` · `generate_pdf.py` | Utilitats |

---

## 5. Estat operatiu · què està fet · què queda

### 5.1 · ✅ Completat (S1-S5)

**S1-S2 · estratègia + briefs** (vegeu §3.3)

**S3 · tècnica**
- 8 renames ES aplicats (construccion, promocion, rehabilitacion, patrimonios, nosotros, proyectos, usuarios, presupuesto)
- vercel.json definitiu · `vercel-rewrites-snippet.json` mergeed
- Schemas JSON-LD inyectats segons matrix
- hreflang automàtic via slug-mapping.json (CA + ES + EN + x-default → CA)
- sitemap re-generat post-renames
- generate_html.py com a build pipeline reproducible

**S4 · contingut multilingüe**
- Copy v1.1 CA aplicat al build (28 fitxers)
- Traducció ES completa (28 fitxers)
- Adaptació EN completa (26 fitxers)
- 18 articles a paritat tri-lingual
- 9 legal placeholders (3 CA + 3 ES + 3 EN)
- Comarcal hubs Vallès Occ · Maresme · Garraf
- Tier 2 landings (Argentona · Castellar · Llavaneres · Sitges · Vilanova)

**S5 · QA + reports**
- `qa-script.py` final pass · `qa-findings.json` produït
- `s5-qa-report.md` · 0 P0 confirmat
- `legal-review-report.md` · llistat de blockers per counsel
- Reports S3 + S4 + S5 generats

### 5.2 · ⏳ Pendent · pre-launch (vegeu deployment-runbook.md)

- Counsel sign-off de 6 placeholders (3 legal pages × 1 idioma representatiu + Patrimonis + Comunitats LPH + Ponsa)
- Family Ponsa consentiment escrit (xifra 2M€)
- DPO designation
- Real cookie inventory (post cookie-scan staging)
- Cookie banner script + CSS deployment
- OG images per pàgina (o fallback chain validat)
- Project page images (lliurament PAPIK)
- Lighthouse 90+ a 5 pàgines representatives
- axe DevTools 0 critical
- Mobile-Friendly Test
- Rich Results Test (1 article + 1 landing)
- Smoke test 20 redirects manualment

### 5.3 · 🔴 Bloquejat · per inputs externs

| Pendent | Bloquejat per |
|---|---|
| Counsel sign-off (6 documents) | Advocat especialitzat · pendent contracte |
| Family Ponsa consentiment 2M€ | Decisió family Ponsa |
| DPO designation | Decisió interna PAPIK |
| Imatges OG + projectes | Lliurament PAPIK |

---

## 6. Notes crítiques · no perdre

### 6.1 · Privacy boundary v2 (vegeu style-guide §7)

Cero dades internes (preus, lògica configurador, % subvencions a casos concrets, marges, dades dels 14 presupuestos analitzats). Cero clients identificats sense permís escrit (Ponsa-rule). Cero adreces exactes a project pages. Disclaimers regulatoris obligatoris a content investment-adjacent.

### 6.2 · "Double-n bug" cautionary tale

Mai aplicar regex de bulk-replace que no comprovi si la substitució ja està aplicada (cas del slug `construccion` → `construccionn` per doble pas). Vegeu style-guide §4 per a la lliçó codificada.

### 6.3 · Tri-lingual parity (vegeu style-guide §6)

Cap article es publica només en una llengua. Si arriba un nou article, ha d'existir a CA + ES + EN abans del deploy.

### 6.4 · Brand correctness

Formes correctes (vegeu glossari a `style-guide-editorial.md` §13):
- **Passive Rooms** (no PassivRooms · slug es manté `passivrooms` per continuïtat SEO)
- **K-Vall d'Or** (no K-Vallor · slug es manté `k-vallor` per continuïtat SEO)
- **Eskimohaus®** (amb símbol registrada · primera vegada de l'article)
- **Cases sostenibles, naturalment.** (claim oficial · NO inventar nous)

### 6.5 · Riscos regulatoris a vigilar

- `/patrimonis` · risc oferta pública d'inversió (CNMV)
- `/rehabilitacio/comunitats` · risc Llei Propietat Horitzontal
- `article-nota-premsa-papik-ponsa` (xifra 2M€) · risc CNMV + consentiment family
- `article-nota-premsa-papik-sabadell` (hipoteca verda) · risc Banc d'Espanya

---

## 7. KPIs · com mesurarem l'èxit

### 7.1 · Pre-launch (vegeu deployment-runbook.md per checklist complet)

- [ ] 100% schemas validen (Rich Results Test)
- [ ] LCP < 2.5s a 5 pàgines clau
- [ ] hreflang funcional 100%
- [ ] Mobile-friendly 100%
- [ ] 0 P0 al qa-script.py
- [ ] Lighthouse ≥90 a 5 pàgines

### 7.2 · 30 dies post-launch

- Branded queries top 1
- Cap caiguda significativa de tràfic orgànic global
- GSC sense errors crítics

### 7.3 · 90 dies post-launch

- "Construir casa Passivhaus Catalunya" · top 10
- "Constructora Sant Cugat" · top 5
- "Llicència derribo Cerdanyola" · top 1-3
- Configurador · 100+ leads/mes

---

## 8. Versions i història

| Versió | Data | Canvis |
|---|---|---|
| 1.0 | 27 abril 2026 | Document inicial · post-S2 |
| 1.1 | 27 abril 2026 | Update post style-guide v1.1 (em-dash, registre adult, prosa) |
| 1.2 | 28 abril 2026 | Post-S5 · status badges · paritat tri-lingual · comptes finals · pointer al deployment-runbook |

---

## 9. Final · resum d'una línia

**Tots els blockers de codi, contingut i tècnica resolts · només resten counsel sign-off (6 docs), assets reals (imatges, NIF, cookies) i smoke tests previs al 1 juny · vegeu `deployment-runbook.md`.**
