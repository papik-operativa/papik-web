# Manual d'estil editorial · PAPIK Group

> Document canònic de veu i tono per a tot el contingut editorial del site (articles de blog, fitxes de projecte, copy de pàgines, communicacions). Aplicable a CA, ES i EN amb adaptacions culturals descrites a la secció corresponent.
>
> Última revisió · 28 abril 2026 · v1.3

---

## 1. Posicionament editorial

PAPIK Group és **un referent al sector** de la construcció Passivhaus i la rehabilitació energètica a Catalunya. Aquesta condició no s'afirma — es demostra cada vegada que es publica contingut.

El nostre tono ha de ser:

- **Corporatiu i seriós** — som una empresa amb 30 anys d'ofici, no una start-up
- **Formal sense ser distant** — vostè / usted / formal you sempre
- **Tècnic sense ser inaccessible** — explicar conceptes complexos amb claredat
- **Comercial sense ser comercial-pushy** — la conversió ve de la confiança que generem amb la qualitat editorial, no de pressió directa

El lector ideal: un professional o particular informat que valora la profunditat sobre el sensacionalisme. Si dubtem entre "expressar-se com una agència" o "expressar-se com un despatx d'arquitectes", **guanya el segon**.

---

## 2. Veu · les vuit regles d'or

### 2.1 · Vostè / usted / formal you sempre

Sense excepcions. Inclou:
- "vostè ja sap que..."
- "es preguntarà si..."
- "el seu projecte"

Mai:
- "tu ja saps que..."
- "et preguntaràs..."
- "el teu projecte"

⚠ Excepció única · cites textuals d'altres autors / personatges que parlin en primera persona — es respecta el seu registre original.

### 2.2 · Cero superlatius comercials sense dades

**Prohibits sense dada que els respalgui:**
- "els millors"
- "líders del sector"
- "innovador"
- "pioner" (excepte casos verificables · "2a casa Passivhaus certificada de Catalunya" sí, "pioners de la sostenibilitat" no)
- "premium" (excepte com a categoria objectiva · "calidades premium" sí, "servei premium" no)
- "expert" (mostrem expertesa, no la proclamem)

**Substituts vàlids · dades concretes:**
- "30 anys construint a Catalunya"
- "100+ obres construïdes"
- "36 cases documentades a la web"
- "1a casa Passivhaus certificada del municipi"
- "Sistema constructiu propi des del 2014"

### 2.3 · Frases curtes amb pes

Cada frase ha de guanyar-se el seu lloc. Si una frase es pot eliminar sense perdre informació, s'elimina. Regla pràctica · si una frase passa de 30 paraules, dividir-la.

### 2.4 · Tècnic quan aporta · accessible quan no

Si la dada tècnica aporta autoritat al text, usar-la sense apologies (U-value, n50, kWh/m²·a, EnerPHit, ponts tèrmics, SATE, CLT). Si només és jerga, simplificar. Primera aparició · explicació parentètica curta.

### 2.5 · Sense exclamacions · sense interrogacions retòriques excessives

Una sola exclamació per article com a màxim, idealment cap. Interrogacions retòriques només quan obren un punt real.

### 2.6 · Verbs en present indicatiu sempre que es pugui

El present indicatiu transmet autoritat. Reservem el condicional per a estimacions reals.

### 2.7 · Cap guió llarg (em-dash)

Esmena editorial v1.1. El caràcter "—" és una empremta lingüística que els detectors d'IA marquen com a sospitosa, i que en la tradició editorial catalana professional té poc ús real. S'evita sistemàticament a tot el copy públic.

Substitucions naturals: coma o parèntesi per a incisos curts; punt i coma o punt seguit per a clàusules amb pausa marcada; dos punts quan introdueix explicació. També limitem l'abús del punt volat (·) com a separador estilístic.

### 2.8 · Registre adult, no didàctic

Esmena editorial v1.1. Explicar conceptes amb claredat no requereix simplificar-los al nivell d'un manual escolar. Frases com "Imagineu que...", "Vegem com funciona", "És important destacar que", "Cal recordar que" condueixen el lector com si fos un alumne. La prosa professional planteja directament la idea. Adverbis emfàtics ("clarament", "evidentment", "obviament") també s'eviten perquè substitueixen l'argument per un to autoritari.

---

## 3. Estructura · cada article ha de tenir

### 3.1 · Title · 30-65 caràcters (vegeu §9)

Format · `[Tema concret + valor afegit] · PAPIK`

### 3.2 · Meta description · 100-165 caràcters (vegeu §9)

Síntesi del valor de l'article + verb d'acció implícit.

### 3.3 · H1 únic · idèntic o similar al title

### 3.4 · Byline + data · obligatoris

Sense byline + data, l'article no es publica.

### 3.5 · Estructura del cos · prosa per defecte

Esmena editorial v1.1. La forma natural del contingut PAPIK és **prosa argumentada en seccions i subseccions**, no llistats esquemàtics. Reservem els bullets per a tres situacions: processos amb fases numerades, taxonomies heterogènies escannejables, checklists operatius.

Intro de 150-200 paraules · cos amb H2 jeràrquics · cierre de 50-100 paraules amb CTA i 2-3 cross-links.

### 3.6 · FAQ opcional · si el tema ho permet (4-7 preguntes amb schema FAQPage)

### 3.7 · Imatge hero · obligatòria

WebP/AVIF · 1200x630 ideal · alt descriptiu (no decoratiu).

---

## 4. Slug taxonomy · CA / ES / EN

Esmena v1.2. Cada URL del site té tres versions registrades a `slug-mapping.json`. Aquesta secció codifica les regles que han governat les decisions de slug durant S3-S4.

### 4.1 · Toponímia · mantenir Catalan

Quan el slug és un topònim, **manté la forma catalana** a les tres llengües. La identitat geogràfica és estable i no es tradueix:

- `bellaterra` → `bellaterra` → `bellaterra`
- `sant-cugat-del-valles` → `sant-cugat-del-valles` → `sant-cugat-del-valles`
- `argentona` → `argentona` → `argentona`
- `valles-occidental` → `valles-occidental` → `valles-occidental`

ES no usa "Sant Cugat del Vallés" amb accent al slug · només al copy. EN no transliteralitza ni adapta.

### 4.2 · Servei i conceptes · traducció pròpia per llengua

Quan el slug és una paraula de servei o concepte (no topònim), **es tradueix correctament** a cada llengua:

| CA | ES | EN |
|---|---|---|
| `construccio` | `construccion` | `construction` |
| `rehabilitacio` | `rehabilitacion` | `retrofit` |
| `promocio` | `promocion` | `development` |
| `patrimonis` | `patrimonios` | `wealth` |
| `comunitats` | `comunidades` | `communities` |
| `nosaltres` | `nosotros` | `about` |
| `projectes` | `proyectos` | `projects` |
| `pressupost` | `presupuesto` | `budget` |
| `usuaris` | `usuarios` | `users` |
| `premsa` | `prensa` | `press` |
| `certificacions` | `certificaciones` | `certifications` |

### 4.3 · EN · estratègia de traducció semàntica, no transliteració

Per a slugs d'articles, EN aplica **traducció semàntica** (no calc literal):

- CA `article-derribar-construir-passos` → EN `article-demolish-and-rebuild-steps` (no `article-derribar-construir-steps`)
- CA `article-revolucio-fusta` → EN `article-wood-revolution`
- CA `article-petjada-ecologica` → EN `article-ecological-footprint`
- CA `article-apagada-2025` → EN `article-blackout-2025`

EN també adopta una taxonomia de carpetes pròpia · `areas/` per landings (no `landings/`), `regions/` per comarques (no `comarques/` o `comarcas/`).

### 4.4 · El "double-n bug" · regla cautelar

Esmena v1.2. Durant S3 vam patir un bug a un script de bulk-rename ES: un regex que substituïa `construccio` → `construccion` es va aplicar dues vegades, generant `construccionn`. Lliçó codificada:

**Mai apliquis un regex de substitució global sense una guarda que comprovi si la substitució ja està aplicada.** Patró segur:

```python
# MALAMENT
slug = re.sub(r'construccio\b', 'construccion', slug)
# Si s'executa sobre un slug ja migrat, dóna 'construccionn'

# BÉ
if not re.search(r'construccion\b', slug):
    slug = re.sub(r'construccio\b', 'construccion', slug)
```

O bé · mantenir un set de slugs ja migrats i saltar-los, o mantenir el slug-mapping.json com a font de veritat única i fer mai re-runs no idempotents.

### 4.5 · Slug stability · una vegada publicat, no es canvia

Tot canvi de slug post-launch ha de generar entry al redirect-map. La continuïtat SEO importa més que la perfecció lingüística retroactiva.

---

## 5. Hreflang invariants

Esmena v1.2. Tota pàgina del site té els tres idiomes + x-default declarats al `<head>`. Cap excepció.

### 5.1 · Estructura mínima per pàgina

```html
<link rel="canonical" href="https://papik.cat/[slug-ca]">
<link rel="alternate" hreflang="ca" href="https://papik.cat/[slug-ca]">
<link rel="alternate" hreflang="es" href="https://papik.cat/es/[slug-es]">
<link rel="alternate" hreflang="en" href="https://papik.cat/en/[slug-en]">
<link rel="alternate" hreflang="x-default" href="https://papik.cat/[slug-ca]">
```

### 5.2 · Invariants

- **x-default sempre apunta a CA** (mercat principal · Catalunya)
- **Canonical apunta a la pàgina mateixa en la seva llengua** (no a la versió CA per a una pàgina ES)
- **Reciprocitat obligatòria** · si CA enllaça a ES, ES ha d'enllaçar a CA · sense excepcions
- **Self-reference inclosa** · una pàgina CA ha de declarar hreflang="ca" cap a si mateixa
- **No incloure pàgines no publicades** als hreflang (404 a hreflang penalitza el cluster sencer)
- **Build automatic** · el `generate_html.py` inyecta les 5 línies a partir de `slug-mapping.json`. No editar mai a mà.

### 5.3 · Validació

Pre-deploy · validar amb una eina externa (Sitebulb, Screaming Frog hreflang checker, o el Hreflang Tags Testing Tool) sobre el preview Vercel. Cap warning acceptat.

---

## 6. Tri-lingual parity rule

Esmena v1.2. Codificació explícita d'una instrucció operativa de l'usuari:

**Cada article publicat al site existeix simultàniament a CA + ES + EN. Cap article es desplega només en una llengua.**

### 6.1 · Implicacions de la regla

- Si un article està redactat però no traduït, no es publica fins que les tres versions estiguin enllestides.
- L'arquitectura de carpetes força la simetria · `copy/rewrites/article-X-ca-v2.md` → `copy/translations/es/articles/article-X-es.md` → `copy/translations/en/articles/article-X-en.md`.
- El sitemap genera entries només quan els tres fitxers existeixen i el slug-mapping registra el trio.
- El build pipeline `generate_html.py` salta amb error si troba un trio incomplet.

### 6.2 · Excepcions documentades · cap actual

No hi ha excepcions a aquesta regla a abril 2026. Si en el futur calgués una excepció (per exemple un article hyperlocal CA-only sobre normativa municipal), s'ha de documentar aquí amb justificació, i la pàgina ha de portar `<meta name="robots" content="noindex">` a la versió única perquè no entri al cluster hreflang.

### 6.3 · Lliurament editorial

L'editor envia els tres fitxers junts (CA + ES + EN) o cap. No es comencen revisions amb una sola llengua disponible.

---

## 7. Privacy boundary v2

Versió ampliada (v1.2). Substitueix la versió 4-prohibits del manual v1.1.

### 7.1 · Cero dades internes (sense excepcions)

- Preus reals, marges, % de cost de l'obra
- Lògica del configurador, taules €/m² internes
- Dades dels 14 presupuestos analitzats
- Conversió real · ratis comercials interns
- Volum de leads · pipeline · facturació

### 7.2 · Cero dades específiques de productes financers

Esmena v1.2. Aplicable a tot article relacionat amb hipoteca verda, finançament, NGEU:

- Cap tipus d'interès específic ("Sabadell ofereix al 2,3%")
- Cap LTV (loan-to-value) específic
- Cap termini compromès ("aprovació en 7 dies")
- Cap subvenció a casos concrets ("aquesta família ha rebut 38.000€")

Les dades de mercat es citen sempre **com a rang del sector amb font** ("els tipus verds del mercat es mouen entre el 2 i el 3,5%, segons les dades públiques de [Banc d'Espanya / AEB / etc.]"). Mai com a oferta concreta de PAPIK ni de tercers.

### 7.3 · Cero clients identificats sense permís escrit (Ponsa-rule)

Esmena v1.2. Originat al cas de la nota de premsa Ponsa amb la xifra 2M€:

- Cap nom de família a article públic sense **consentiment escrit** datat i arxivat.
- Cap xifra d'inversió privada (>50.000€) atribuïda a un client identificable.
- Si el client ja és públic per altres mitjans (premsa, TV3) · es referencia la font pública, no s'aporta info nova de PAPIK.
- Excepció única · projectes ja anonimitzats a `/projectes` sota nom-codi (K-Sandal, K-Vall d'Or, etc.) que no permeten re-identificació.

### 7.4 · Project pages · cero adreces exactes

Esmena v1.2. Per a fitxes de projecte (`/projecte-*`):

- Municipi sí (Bellaterra, Matadepera, etc.)
- Comarca sí (Vallès Occidental, Maresme, etc.)
- Carrer + número · **mai** (risc privacitat + seguretat clients)
- Geolocation schema (`@type: Place`) · sempre a nivell de municipi (point coordinates dins l'àrea municipal sense precisió de carrer)

### 7.5 · Investment-adjacent content · disclaimer regulatori obligatori

Esmena v1.2. Tot article que toqui `/patrimonis`, hipoteques, productes financers, plusvàlues immobiliàries, ha de portar al peu un disclaimer estàndard:

> "Aquest contingut té caràcter informatiu general i no constitueix recomanació d'inversió, assessorament financer ni oferta pública de valors. PAPIK Group no és entitat regulada per la CNMV ni intermediari financer. Per a decisions específiques, consulti un assessor independent."

Versions ES + EN equivalents · text canònic mantingut a `copy/translations/{es,en}/legal/disclaimer-investment.md` (a crear post-counsel review).

### 7.6 · Cero comparatives nominals amb competidors

Mantingut de v1.0. Es compara contra **sistemes constructius o pràctiques** ("construcció industrialitzada genèrica", "constructor generalista"), mai contra empreses (Arquima, Canexel, Coll Viader, Farhaus, House Habitat).

---

## 8. Cross-linking taxonomy

Esmena v1.2. Codificació de quan i com cross-linkar entre pàgines.

### 8.1 · Articles · sempre 3 cross-links a articles relacionats

Tot article publicat ha d'enllaçar a **3 articles relacionats al final del cos** (abans del CTA), sota un lead "Llegiu també:" / "Lea también:" / "Read also:".

Criteri de selecció:
1. Mateix cluster temàtic (Bellaterra cluster, NGEU cluster, Passivhaus tècnic cluster, etc.)
2. Si no hi ha tres al mateix cluster, complementar amb articles de cluster adjacent
3. No enllaçar a articles "thin" · prioritzar articles ≥1.500 paraules amb autoritat

### 8.2 · Landings geogràfiques · 3-5 projectes nearby

Cada landing (Tier 1 + Tier 2) enllaça a **3-5 fitxes de projecte de la mateixa àrea geogràfica**. La selecció es fa per radi · primer projectes al mateix municipi, després comarca, després metropolitana.

### 8.3 · Service pages · 3 projectes representatius

Cada pàgina de servei (`/construccio`, `/rehabilitacio`, etc.) enllaça a **3 fitxes de projecte representatives** de cada categoria. Rotació trimestral recomanada per refrescar el contingut intern (signal de freshness).

### 8.4 · Tota pàgina · enllaç al hub corresponent

- Landings → enllacen al hub comarcal corresponent (Vallès Occidental / Maresme / Garraf)
- Articles cluster Bellaterra → enllacen a `/zones/bellaterra`
- Service pages → enllacen entre elles (Construcció ↔ Rehabilitació, etc.)
- Sub-pàgines (Comunitats) → enllacen al pare (Rehabilitació)

### 8.5 · Anchor text · semàntic, no genèric

Mai "click here", "more info", "llegir més" sense context. L'anchor text ha de descriure la pàgina destí amb la keyword principal:

- ✅ "guia completa de la llicència de derribo a Cerdanyola"
- ❌ "llegir més"

### 8.6 · Audit obligatori pre-publicació

Cap pàgina passa QA si té enllaços interns trencats (404), enllaços externs obsolets (4xx/5xx), o anchor text genèric.

---

## 9. Technical metadata standards

Esmena v1.2. Estandardització dels valors tècnics que el `generate_html.py` ha de respectar.

### 9.1 · Title length · 30-65 caràcters

- Mínim 30 chars · evitar titles vagues
- Màxim 65 chars · Google trunca a ~580px (~60-65 chars en latín)
- Format canònic · `[Tema concret + valor afegit] · PAPIK`
- Versió ES · `[Tema] · PAPIK`
- Versió EN · `[Topic] · PAPIK`

### 9.2 · Meta description length · 100-165 caràcters

- Mínim 100 chars · descripcions massa curtes són rejected per Google i remplaçades amb snippets dolents
- Màxim 165 chars · Google trunca a ~155-165
- Sempre conté · keyword principal + valor + verb d'acció implícit

### 9.3 · OG image · fallback chain

Per cada pàgina, el build assigna OG image en aquest ordre:

1. **OG image específica** (si existeix a `public/og/[slug].jpg` · 1200×630)
2. **OG image de categoria** (si existeix a `public/og/category-[type].jpg` · ex. `category-article.jpg`, `category-landing.jpg`)
3. **OG image fallback corporatiu** (`public/og/default.jpg` · sempre present)

Tota pàgina ha de tenir alguna OG image servida. Cap missing image al validador.

### 9.4 · JSON-LD per page type · matrix

Aquesta matrix la respecta `generate_html.py` automàticament:

| Tipus de pàgina | Schemas obligatoris |
|---|---|
| Homepage | 01 Organization · 06 BreadcrumbList |
| Service page | 02 Service · 06 BreadcrumbList |
| Sub-service (Comunitats) | 02 Service · 06 BreadcrumbList · 05 FAQPage si té FAQ |
| Landing geogràfica | 03 LocalBusiness amb GeoCircle · 06 BreadcrumbList · 05 FAQPage si té FAQ |
| Comarcal hub | 03 LocalBusiness (àrea més àmplia) · 06 BreadcrumbList |
| Article | 04 Article · 06 BreadcrumbList · 05 FAQPage si té FAQ |
| Project page | 07 RealEstateListing · 06 BreadcrumbList |
| Press / certificacions | 06 BreadcrumbList |
| Legal pages | 06 BreadcrumbList (no Article ni Service) |

Cap pàgina sense almenys 1 schema. Cap schema amb camps `{{ }}` no resolts. Validació Rich Results Test obligatòria pre-deploy.

### 9.5 · Charset, viewport, language

Tota pàgina · `<meta charset="utf-8">` · `<meta name="viewport" content="width=device-width, initial-scale=1">` · `<html lang="[ca|es|en]">` segons la versió.

### 9.6 · Twitter Card

`twitter:card="summary_large_image"` · twitter:site · twitter:title · twitter:description · twitter:image (mateixa fallback chain que OG).

---

## 10. Project page conventions

Esmena v1.3. Codificació del format v1.1 de pàgina de projecte (`/projecte-*`). El trio CA + ES + EN és obligatori (regla §6).

### 10.1 · Slug pattern tri-lingüe

| CA | ES | EN |
|---|---|---|
| `/projecte-X` | `/es/proyecto-X` | `/en/projects/X` |

Nota · l'EN adopta camí pla sota `/en/projects/` (no `/en/project-X/`). Aquesta asimetria respecta la convenció editorial anglesa de carpeta-pare per a llistats.

### 10.2 · Privacy boundary específica de projectes

Reforça §7.4 amb prohibicions explícites:
- **No adreces exactes** · municipi + comarca only (no carrer, no número, no urbanització identificable)
- **No noms de client** sense consentiment escrit datat (Ponsa-rule, §7.3)
- **No €/m²** · ni cost total, ni preu de venda, ni rendibilitat
- **No superlatius** · "la casa més...", "el projecte més...", "el més gran de" prohibits sense dada verificable

### 10.3 · Seccions obligatòries

Tota fitxa de projecte ha de portar, en aquest ordre:

1. **Hero** · eyebrow (categoria · "Casa Passivhaus", "Rehabilitació EnerPHit", etc.) + H1 únic + subtítol de localització a nivell municipi + comarca
2. **Project specs** · taula compacta amb m², any, classe energètica, nivell Passivhaus (Classic / Plus / Premium / EnerPHit), sistema constructiu (Eskimohaus®, Passive Rooms, mixt)
3. **Descripció** · 2-3 paràgrafs de prosa argumentada (§3.5), no llista de bullets
4. **3 projectes relacionats** · cross-linkats (vegeu §10.5)
5. **JSON-LD RealEstateListing** + **BreadcrumbList**

### 10.4 · Schema requirements

`RealEstateListing` ha de contenir:
- `name` · nom-codi del projecte (K-Sandal, K-Vall d'Or, etc.)
- `description` · 1-2 frases sintetitzant la fitxa
- `url` · canonical de la versió en la llengua de la pàgina
- `location` · `@type: Place` amb `address.addressLocality` (municipi) i `address.addressRegion` (comarca). **Mai** `streetAddress` ni coordinates de precisió de carrer.

### 10.5 · Cross-link rule per fitxa

Cada fitxa de projecte enllaça a:
1. **Zone landing** corresponent (si existeix · `/zones/bellaterra`, `/comarca/maresme`, etc.)
2. **1-2 projectes germans** · mateixa categoria o àrea geogràfica propera
3. **Service hub rellevant** · `/construccio` per obres noves, `/rehabilitacio` per intervencions sobre existent, `/promocio` per promocions

---

## 11. Comarcal i Tier-2 landing conventions

Esmena v1.3. La taxonomia de landings s'ha ampliat post-S5 amb un tier addicional. Codificació del nou tier i del seu tractament editorial.

### 11.1 · Tres tiers de landing

| Tier | Definició | Exemples | Word count |
|---|---|---|---|
| Tier 1 | Municipis prime amb cluster propi | Bellaterra, Sant Cugat del Vallès, Matadepera, Sant Quirze del Vallès | 1.500-2.500 paraules |
| Tier 2 | Municipis amb projecte directe PAPIK | Cabrils, Alella, Premià de Dalt, Tiana, Cerdanyola del Vallès, Argentona, Castellar, Llavaneres, Sitges, Vilanova | 600-900 paraules |
| Comarcal hub | Hub agregador de comarca | Vallès Occidental, Maresme, Garraf | 800-1.000 paraules |

### 11.2 · Tier-2 · concisió focalitzada

A diferència de Tier 1 (extens, exhaustiu), Tier 2 és **concís i focalitzat**. 600-900 paraules és el rang. No bullet-fests; prosa breu en 3-4 H2.

### 11.3 · Anchor proximity rule

Esmena crítica v1.3. Cada landing Tier-2 referencia el **projecte PAPIK directe més proper geogràficament**, no el projecte famós o icònic si està lluny.

Exemple correcte:
- Cabrils landing → ancla a **K-Llavaneres** (Maresme, 4 km)
- Cabrils landing → NO ancla a K-Iturbi (Sant Cugat, 35 km, només pel renom)

Lògica · l'usuari aterra a la landing buscant proximitat. El projecte més proper és l'evidència més rellevant.

### 11.4 · Comarcal hubs · llistat exhaustiu

Cada hub comarcal llista **tots els municipis dins el seu àmbit** que tenen landing publicada, i els enllaça. Sense exclusions selectives. La completesa de la llista és la utilitat del hub.

---

## 12. Performance defaults

Esmena v1.3. Codificació de les regles de rendiment que el `generate_html.py` injecta i que tota plantilla manual ha de respectar.

### 12.1 · Scripts externs · sempre defer o async

Tot `<script src="...">` ha de portar `defer` (per defecte) o `async` (per analytics, scripts independents del DOM). Cap script bloquejant al `<head>`.

### 12.2 · Imatges · loading strategy per fold

- **Above the fold** (hero, primer viewport) · `loading="eager"` + `fetchpriority="high"`
- **Below the fold** (la resta) · `loading="lazy"` + `decoding="async"`

### 12.3 · Preload · CSS i font primaris

- `<link rel="preload" as="style" href="/styles/main.css">`
- `<link rel="preload" as="font" type="font/woff2" href="/fonts/tt-firs-neue.woff2" crossorigin>`

### 12.4 · DNS-prefetch · CDN externs

Tot CDN extern usat (analytics, fonts CDN, video provider) declarat amb `<link rel="dns-prefetch" href="//[domain]">` al `<head>`.

### 12.5 · No Google Fonts

Esmena v1.3. La família TT Firs Neue és **self-hosted** des de `/fonts/`. Cap dependència de `fonts.googleapis.com`. Raons · privacitat (AEPD), rendiment (un round-trip menys), control de versions.

---

## 13. Robots i crawl policy

Esmena v1.3. Codificació de `robots.txt` i de la postura PAPIK davant scrapers.

### 13.1 · Block AI scrapers (drets de contingut AEPD)

Els següents user-agents són bloquejats sistemàticament a `robots.txt`:

- `GPTBot` (OpenAI)
- `ClaudeBot` (Anthropic)
- `PerplexityBot` (Perplexity)
- `CCBot` (Common Crawl, alimenta entrenament massiu)
- `Bytespider` (ByteDance / TikTok)
- `Google-Extended` (entrenament Bard/Gemini, distint del crawler de Search)

Justificació · els 95.000 paraules editorials són IP de PAPIK; el seu ús per entrenar models comercials sense llicència no està autoritzat. Aquesta postura s'alinea amb el guidance AEPD/CNIL sobre data scraping.

### 13.2 · Per-bot crawl-delay 5s · scrapers SEO

Bloc específic per scrapers de monitoring SEO de tercers (Ahrefs, Semrush, Majestic / MJ12) amb `Crawl-delay: 5`. Es permet l'accés (per a anàlisi competitiva legítima de tercers que ens monitoritzen) però amb cadència restringida per limitar càrrega.

### 13.3 · Sitemap reference

Al final de `robots.txt`:

```
Sitemap: https://papik.cat/sitemap.xml
```

Únic sitemap canonical. Cap sitemap-index múltiple ni sitemaps secundaris.

---

## 14. Convencions de format

### 10.1 · Nombres
- Anys · "1994", "2024", "2026"
- Quantitats grans · "100+ obres", "+30 anys"
- Percentatges · "70%" (sense espai)
- Mesures · "200 m²", "3,5 m" (amb espai)
- Rangs · "30-50%", "8-16 setmanes" (guió simple)

### 10.2 · Dates
- Format complet · "21 de juny de 2014"
- Format curt · "21/06/2014" només en taules

### 10.3 · Termes tècnics
- Estàndards · "Passivhaus" (amb majúscula · marca registrada PHI)
- Sistemes propi · "Eskimohaus®" (primera vegada de l'article)
- Acrònims · explicar a primera aparició · "nZEB (edificis de consum gairebé nul)"

### 10.4 · Topònims
- Catalunya · sempre (no "Cataluña" en CA)
- El Vallès Occidental · amb article
- Sant Cugat del Vallès · nom complet a primera aparició

### 10.5 · Cometes
- Cometes baixes · « » per a cita textual llarga
- Cometes altes · " " per a frase curta o terme

---

## 11. Citacions · com referenciar fonts

PAPIK basa autoritat en dades verificables. Tota afirmació factual no obvia ha de tenir font.

### 11.1 · Fonts vàlides
BOE / DOGC / BOPB · IDAE / ICAEN / ITeC / COAC / COAATT · Passivhaus Institut Darmstadt · Sociedad de Tasación / Idealista Data / Tinsa · Universitat / centre recerca · Mitjans de prestigi (La Vanguardia, El País, ARA, El Confidencial).

### 11.2 · Fonts a evitar
Wikipedia com a font primària · blogs comercials de competidors · press releases pagats · fonts sense data.

---

## 12. CTAs · com tancar un article

Acabar amb un CTA específic relacionat amb el tema, ofert com a següent pas natural · seguit de 2-3 cross-links a contingut relacionat (vegeu §8).

---

## 13. Adaptació a ES i EN

### 13.1 · ES (versió canónica · traducció literal amb adaptacions léxiques)
- "Vostè" → "usted"
- Topònims · mantenir versió oficial castellana al copy ("Cataluña")
- Slug · vegeu §4

### 13.2 · EN (adaptació cultural important)
- "Casa pasiva" → "passive house" (NO "passive home")
- Referències geogràfiques amb context "(greater Barcelona area)"
- Subvencions NGEU · explicar al primer ús ("EU recovery funds")
- Slug · semantic translation, vegeu §4.3

---

## 14. Workflow editorial

1. Brief · qui escriu, paraula clau, audiència, longitud
2. Esborrany CA seguint aquest manual
3. Revisió tècnica · una persona del equip verifica dades
4. Revisió ortogràfica i d'estil
5. Traducció ES + EN paral·lela (§6 parity rule)
6. Revisió SEO · checklist §15
7. Schema + hreflang generat per `generate_html.py`
8. Imatge hero + OG + alt descriptiu
9. Internal linking validat (§8)
10. Publicar a producció amb les tres llengües simultàniament

---

## 15. SEO · checklist per article

- [ ] Title 30-65 chars · keyword principal al primer terç
- [ ] Meta description 100-165 chars · valor + CTA implícit
- [ ] H1 únic · keyword principal present
- [ ] H2/H3 jeràrquics · subkeywords distribuïdes
- [ ] Byline + data visible
- [ ] Schema Article amb autor, dates, image, wordCount, inLanguage (vegeu §9.4)
- [ ] hreflang CA + ES + EN + x-default (vegeu §5)
- [ ] Canonical apuntant a si mateix
- [ ] OG tags + fallback chain (§9.3)
- [ ] Twitter Card
- [ ] 3+ internal links · 3 cross-links a articles relacionats (§8)
- [ ] 2+ external links a fonts autoritzades
- [ ] Imatge hero optimitzada + alt descriptiu
- [ ] Word count > 1.000 paraules per content "thin" · > 2.000 per pillar
- [ ] FAQ + schema FAQPage si el tema ho permet
- [ ] Existeix versió ES i EN paral·lela (§6)

---

## 16. Glosari intern · termes correctes

| Forma correcta | Variants incorrectes a evitar |
|---|---|
| Passivhaus | Passive House (en CA/ES) |
| Eskimohaus® | Eskimohaus (sense ®) · "el sistema eskimohaus" (amb minúscula) |
| Passive Rooms | PassivRooms · Passivrooms |
| K-Vall d'Or | K-Valldor · K-Vallor |
| Sant Cugat del Vallès | Sant Cugat (només a partir de la segona menció) |
| Bellaterra (Cerdanyola del Vallès) | Bellaterra sense aclarir el primer ús |
| n50 hermeticitat | hermeticitat (sense unitat) |
| kWh/m²·a | kwh/m2 (formatat malament) |
| Pla d'Ordenació Urbanística Municipal (POUM) | POUM (només a partir de la segona menció) |
| Next Generation EU | Next Generation (sense EU) |
| ITE (Inspecció Tècnica de l'Edifici) | ITE (sense aclarir el primer ús) |

---

## 17. Indicadors de qualitat editorial

- ✅ El title comunica el valor en 30-65 chars?
- ✅ La meta description fa que un usuari hi vulgui clicar (100-165 chars)?
- ✅ La intro hooka el lector en les primeres 100 paraules?
- ✅ Cada H2 cobreix una secció amb valor independent?
- ✅ Hi ha dades concretes amb fonts (mínim 3)?
- ✅ El tono és consistent (vostè, formal, sense superlatius)?
- ✅ Cap em-dash al text (§2.7)?
- ✅ Registre adult (§2.8)?
- ✅ 3 cross-links a articles relacionats (§8.1)?
- ✅ Existeix paritat tri-lingual (§6)?
- ✅ Schema valida (§9.4)?
- ✅ hreflang configurat (§5)?
- ✅ Privacy boundary respectada (§7)?

Si ≥10 dels 13 punts es compleixen, l'article està en bona forma.

---

## 18. Mantenir aquest document

Aquest manual és **viu**. Cada vegada que detectem un patró editorial nou (positiu o negatiu) o una decisió tècnica nova, l'incorporem aquí.

### Història de versions

**v1.3 (28 abril 2026 · post-Wave-3)**

Cinc seccions noves codificades a partir de descobriments del cicle de project pages, Tier-2 landings i performance pass:

- §10 · Project page conventions (slug tri-lingüe `/projecte-X` / `/es/proyecto-X` / `/en/projects/X`, privacy boundary específica, seccions obligatòries, schema RealEstateListing a nivell municipi, cross-link rule)
- §11 · Comarcal i Tier-2 landing conventions (Tier-2 600-900 paraules, anchor proximity rule, comarcal hubs llistat exhaustiu)
- §12 · Performance defaults (defer/async, lazy/eager per fold, preload CSS+font, DNS-prefetch, no Google Fonts)
- §13 · Robots i crawl policy (block GPTBot/ClaudeBot/PerplexityBot/CCBot/Bytespider/Google-Extended, crawl-delay 5s SEO scrapers, sitemap canonical)

També renumeració de §10-§17 antics a §14-§21.

**v1.2 (28 abril 2026 · post-S5)**

Cinc seccions noves codificades a partir de descobriments del cicle S3-S5:

- §4 · Slug taxonomy completa (CA/ES/EN, regla toponímia, EN semantic, double-n bug)
- §5 · Hreflang invariants (CA + ES + EN + x-default, x-default→CA, canonical self)
- §6 · Tri-lingual parity rule (cap article només en una llengua)
- §7 · Privacy boundary v2 (afegits cero rates hipoteca, Ponsa-rule, project addresses, investment disclaimer)
- §8 · Cross-linking taxonomy (3 articles, 3-5 projectes, anchor semàntic)
- §9 · Technical metadata standards (title 30-65, meta 100-165, OG fallback chain, JSON-LD matrix)

També actualitzat el §15 SEO checklist per reflectir les noves regles.

**v1.1 (abril 2026, esmena editorial)**

Tres rectificacions transversals:
- Eliminació sistemàtica del guió llarg (em-dash) i reducció del punt volat (§2.7)
- Elevació del registre a un català tècnic-professional adult (§2.8)
- Prosa argumentada com a forma natural per defecte (§3.5)

**v1.0 (abril 2026)**

Document inicial. Definició de veu, tono, regles, glossari, workflow editorial.

### Pròximes revisions

Post-launch (juny), després trimestrals. Persona responsable: responsable editorial i SEO de PAPIK.
