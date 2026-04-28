# Patches Fase 3 P2 · 6 articles · canvis lleugers

> Aquests 6 articles estan en bona forma (titles dins rang, contingut sòlid). Els canvis necessaris són optimitzacions puntuals: schema, byline, fonts citades, cross-links. **NO es reescriu el cos** · només els canvis específics.

---

## Aplicació transversal a tots els 6

A tots els articles d'aquesta fase, afegir:

### Byline visible al UI (sota H1)

```html
<div class="article-byline">
  Equip tècnic · PAPIK Group
  <span class="separator">·</span>
  <time datetime="[YYYY-MM-DD]">[Data publicació]</time>
  <span class="separator">·</span>
  Reading time ~[X] min
</div>
```

### Schema JSON-LD `Article`

Inserir al `<head>`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[H1 EXACTE]",
  "description": "[META DESCRIPTION]",
  "image": "https://papik.cat/img/articles/[slug]/hero.jpg",
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "author": {
    "@type": "Organization",
    "name": "PAPIK Group",
    "url": "https://papik.cat"
  },
  "publisher": { "@id": "https://papik.cat/#org" },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "[URL CANÒNICA]"
  },
  "articleSection": "[SECCIÓ]",
  "wordCount": [INT],
  "inLanguage": "ca-ES",
  "isAccessibleForFree": true
}
</script>
```

+ `BreadcrumbList` (Inici > Blog > [Article]) inseritat universalment.

---

## 1 · article-casa-montseny · P2

**Title actual:** "Una casa sostenible a les faldes del Montseny | PAPIK" (56 chars) ✅ **mantenir**

**Meta description actual:** dins rang ✅ **mantenir**

**Canvis específics:**

1. Afegir byline + data publicació al UI
2. Afegir schema `Article` (articleSection: "Casos d'estudi")
3. Afegir cross-links al final:
   - [Materials sostenibles · fusta, suro, cel·lulosa](/article-materials-sostenibles)
   - [La petjada ecològica de construir i viure a casa seva](/article-petjada-ecologica)
   - [Veure altres projectes a la zona](/projectes)
4. Afegir CTA al final (si no n'hi ha): "Sol·licitar visita a una obra similar → contacte"

⚠ Si el contingut menciona "23,90 tones de CO₂ estalviades", verificar que la dada està basada en càlcul PHPP del propi projecte (no extrapolació general). Si és vàlida, mantenir amb cita interna a la simulació.

**Esforç estimat:** 20 min

---

## 2 · article-hipoteca-energetica · P2

**Title actual:** "Què és la hipoteca energètica? | PAPIK" (48 chars · 2 sota mínim)

**Title proposat:** "Hipoteca energètica · estalvi acumulat al llarg dels anys | PAPIK" (62 chars · una mica over però acceptable)

O alternativa més curta:
**"Què és la hipoteca energètica i quan val la pena | PAPIK"** (54 chars) ✅

**Meta description proposta:** "Què és una hipoteca energètica i quins estalvis aporta al llarg dels anys per a vivendes d'alta eficiència energètica. Guia detallada de PAPIK." (147 chars) ✅

**Canvis específics:**

1. Renomenar title segons proposta
2. Afegir byline + data
3. Afegir schema `Article` (articleSection: "Finançament i hipoteques")
4. **Afegir cross-link prominent** al article reescrit [Hipoteca verda per a Passivhaus · acord PAPIK + Banc Sabadell](/article-nota-premsa-papik-sabadell)
5. Considerar afegir bloc FAQ (3-4 preguntes) + schema FAQPage

**Esforç estimat:** 35 min

---

## 3 · article-principis-passivhaus · P2

**Title actual:** "Els cinc principis del Passivhaus | PAPIK" (55 chars) ✅

**Meta description:** dins rang ✅ **mantenir**

**Canvis específics:**

1. Afegir byline + data
2. Afegir schema `Article` (articleSection: "Tècnic Passivhaus")
3. **Reforçar internal linking** · l'article és pillar del cluster Passivhaus, ha d'enllaçar a:
   - [Tecnologies clau del Passivhaus 2026](/article-tecnologies-passivhaus)
   - [Innovacions Passivhaus 2026](/article-innovacions-passivhaus)
   - [Per què es respira millor en una casa Passivhaus?](/article-ventilacio-passivhaus)
   - [Sostenibilitat i Passivhaus](/article-sostenibilitat-passivhaus)
4. Afegir CTA: "Configurar el pressupost de la meva casa Passivhaus → /pressupost"

**Esforç estimat:** 20 min

---

## 4 · article-revolucio-fusta · P2

**Title actual:** "La revolució de la fusta · cases de fusta superresistents | PAPIK" (60 chars) ✅

**⚠ Problema detectat:** "revolució" és superlatiu sense dada concreta · l'article cita un avenç científic (fusta autodensificada amb resistència 9× superior). **Verificar font de l'estudi**.

**Canvis específics:**

1. **Verificar font científica:** la dada de "9× resistència" prové d'estudi específic? Si sí, afegir cita amb DOI o URL al text. Si no, suavitzar a "fins a vàries vegades superior" amb font general.
2. Si la font és sòlida, mantenir title amb "revolució" justificada per la dada
3. Si la font és feble, considerar reescriure title a: "Fusta superresistent · futur dels materials de construcció | PAPIK" (62 chars)
4. Afegir byline + data
5. Afegir schema `Article` (articleSection: "Materials i tecnologia")
6. Afegir cross-links a [Materials sostenibles](/article-materials-sostenibles) i [Innovacions Passivhaus 2026](/article-innovacions-passivhaus)
7. Afegir CTA al final

**Esforç estimat:** 30 min (depèn de la verificació de font)

⚠ Acció PAPIK · clarificar amb l'autor original quina és la font de la dada "9× resistència"

---

## 5 · article-sostenibilitat-passivhaus · P2

**Title actual:** "Passivhaus i sostenibilitat · com minimitzar la petjada ecològica | PAPIK" (58 chars) ✅

**Meta description:** dins rang ✅ **mantenir**

**Canvis específics:**

1. Afegir byline + data
2. Afegir schema `Article` (articleSection: "Tècnic Passivhaus")
3. **Cross-link prominent** a [La petjada ecològica de construir i viure a casa seva](/article-petjada-ecologica) — l'article reescrit cobreix el càlcul LCA detallat
4. Afegir cross-links a:
   - [Els cinc principis del Passivhaus](/article-principis-passivhaus)
   - [Materials sostenibles](/article-materials-sostenibles)
5. Afegir CTA al final: "Configurar el pressupost del meu projecte → /pressupost"

**Esforç estimat:** 20 min

---

## 6 · article-ventilacio-passivhaus · P2

**Title actual:** "Per què es respira millor en una casa Passivhaus? | PAPIK" (60 chars) ✅

**Meta description:** dins rang ✅ **mantenir**

**⚠ Problema detectat:** la dada "L'aire interior pot ser fins a 5 vegades més contaminat que l'exterior" necessita font.

**Fonts vàlides per a aquesta afirmació:**
- **EPA (Environmental Protection Agency · Estats Units)** · estudis sobre IAQ (Indoor Air Quality)
- **OMS (Organització Mundial de la Salut)** · informes sobre qualitat de l'aire interior
- **Estudi BPIE (Building Performance Institute Europe)** · informes sobre vivendes europees

**Canvis específics:**

1. Localitzar font concreta de la xifra "5×" i afegir-la inline · format: "(EPA · estudis sobre qualitat de l'aire interior, 2023)" o equivalent
2. Afegir byline + data
3. Afegir schema `Article` + considerar `FAQPage` per a les preguntes habituals sobre ventilació
4. Cross-links a:
   - [Tecnologies clau del Passivhaus 2026](/article-tecnologies-passivhaus)
   - [Els cinc principis del Passivhaus](/article-principis-passivhaus)
5. Afegir CTA: "Configurar el pressupost de la meva casa amb VRC → /pressupost"

**Esforç estimat:** 30 min

⚠ Acció PAPIK · validar font de la dada "5×" abans de publicar (alternativament, ajustar a "fins a diverses vegades més contaminat")

---

## Resum d'esforç total Fase 3 P2

| Article | Acció principal | Esforç |
|---|---|---|
| casa-montseny | Schema + byline + cross-links | 20 min |
| hipoteca-energetica | Title fine-tune + schema + cross-link a Sabadell | 35 min |
| principis-passivhaus | Schema + byline + cluster linking | 20 min |
| revolucio-fusta | Verificar font · schema · linking | 30 min |
| sostenibilitat-passivhaus | Schema + linking a petjada-ecologica | 20 min |
| ventilacio-passivhaus | Verificar font · schema · linking | 30 min |
| **TOTAL** | | **~2h 35 min** |

---

## Validacions externes pendents

Aquests punts requereixen verificació externa abans de publicar (PAPIK ha de respondre):

1. **revolucio-fusta** · font de la dada "9× resistència" — quin estudi/article original?
2. **ventilacio-passivhaus** · font de la dada "5× contaminació interior" — EPA, OMS, o altra?
3. **casa-montseny** · validar 23,90 tones CO₂ amb càlcul PHPP del projecte concret

Si en algun cas la font no es localitza, suavitzar el copy a versió més general sense xifra concreta.

---

## Aplicació pràctica · com el dev fa això

Per cada article del Fase 3 P2:

1. Obrir el fitxer `/public/article-[slug].html`
2. Aplicar els canvis específics segons aquest patches doc
3. Verificar al CA que el byline + data són visibles al UI
4. Validar el schema amb Rich Results Test (https://search.google.com/test/rich-results)
5. Verificar que els cross-links funcionen (no 404s)
6. Replicar tots els canvis a la versió ES (`/es/article-[slug-traduit].html`) si existeix
7. Re-generar `sitemap.xml` (amb `python3 generate_sitemap.py`)
8. Commitejar amb missatge clar · ex: "P2 patches: schema + byline + cross-links · 6 articles existents"

**Cada patch és aplicable en menys de 30 minuts. Total Fase 3 P2: 2-3 hores per a tots els 6 articles. Excel·lent ratio impacte SEO/temps invertit.**
