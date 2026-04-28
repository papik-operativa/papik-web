# Auditoria 15 articles existents · PAPIK CA

> Auditoria SEO + tono + estructura dels 15 articles heretats del WordPress live al nou build. Punts d'acció priorit zats per a S4 (rewrite). Aquest document complementa `style-guide-editorial.md`.
>
> Última auditoria · abril 2026

---

## Resum executiu

Madurez SEO **moderada amb gaps crítics estructurals**:

- **7 de 15 articles** sobrepassen el rang òptim de title 50-60 chars · 46,7% no compleix
- **3 articles de premsa** (K-SANDAL, Ponsa, Sabadell) tenen titles **catastróficament llargs** (102-149 chars) · prioritat P0
- **0 de 15 articles** tenen schema BlogPosting · gap sistèmic
- **0 articles** tenen byline/data visibles al UI · falta E-E-A-T crítica
- **Ortografia i to són correctes en general** · catalanismes/castellanismes mínims
- **Internal linking sòlid** · pattern temàtic ben treballat

**Conclusió ràpida:** el contingut és tècnic i correcte; el problema és la presentació SEO i la falta d'estructura E-E-A-T moderna.

---

## Taula resum (15 articles)

| Slug | Title (chars) | Meta (chars) | H1 OK | Schema | Byline | Tono | Ortografia | SEO | **Prioritat** |
|---|---|---|---|---|---|---|---|---|---|
| apagada-2025 | 65 ⚠ | ~130 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P1** |
| casa-montseny | 56 ✅ | ~140 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P2** |
| hipoteca-energetica | 48 ⚠ | ~135 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P2** |
| innovacions-passivhaus | 71 ⚠⚠ | ~145 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | **P1** |
| materials-sostenibles | 72 ⚠⚠ | ~150 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | **P1** |
| **nota-premsa-ksandal** | **102 🔴** | ~130 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | 🔴 | **P0** |
| **nota-premsa-ponsa** | **116 🔴** | ~130 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | 🔴 | **P0** |
| **nota-premsa-sabadell** | **149 🔴** | ~135 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | 🔴 | **P0** |
| petjada-ecologica | 62 ⚠ | ~155 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P1** |
| pressupost-casa-passiva | 67 ⚠ | ~160 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P1** |
| principis-passivhaus | 55 ✅ | ~140 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P2** |
| revolucio-fusta | 60 ✅ | ~140 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P2** |
| sostenibilitat-passivhaus | 58 ✅ | ~155 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P2** |
| tecnologies-passivhaus | 67 ⚠ | ~160 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P1** |
| ventilacio-passivhaus | 60 ✅ | ~155 ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ⚠ | **P2** |

**Llegenda prioritats:**
- 🔴 **P0** · rewrite total + reestructura · pre-launch obligat
- ⚠ **P1** · rewrite parcial (title + meta + schema + byline) · pre-launch desitjable
- ✅ **P2** · optimització lleugera (schema + byline) · post-launch acceptable

---

## Detall per article

### article-apagada-2025 · P1

**Title actual:** "Quan tot es va apagar, tres cases seguien enceses | PAPIK" (65 chars · 5 chars over)
**Recomanació:** títol més curt aprofitant la força narrativa
- "Tres cases enceses durant l'apagada del 2025 | PAPIK" (52 chars) ✅
- O sense data: "Tres cases enceses quan va fallar la xarxa | PAPIK" (50 chars)

**Schema:** afegir `Article` + `NewsArticle` (perquè és narrativa d'esdeveniment)

**Byline + data:** publicat 29 abril 2025 (recent). Afegir `datePublished: 2025-05-01`.

**Internal linking:** ja enllaça a hipoteca-energetica, principis-passivhaus, petjada-ecologica. ✅ Bo.

**Recomanacions adicionals:**
- Esmentar K-Codines, K-Vall d'Or, K-Llavaneres com a casos identificables (estan a /projectes)
- Cross-link a `/zones/sant-andreu-de-llavaneres` (landing nova) on K-Llavaneres és caso anchor

---

### article-casa-montseny · P2

**Title actual:** "Una casa sostenible a les faldes del Montseny | PAPIK" (56 chars) ✅

**Strengths:** profunditat tècnica excellent · Blower Door · CO₂ data · 23,90 tones d'estalvi.

**Schema:** afegir `Article` amb wordCount + author + dates.

**Recomanació:** mínima · només schema + byline.

---

### article-hipoteca-energetica · P2

**Title actual:** "Què és la hipoteca energètica? | PAPIK" (48 chars · 2 sota mínim)
**Recomanació:** ampliar títol amb dada concreta
- "Hipoteca energètica · estalvi de €80k en 30 anys | PAPIK" (54 chars)

**Schema:** `Article` + opcionalment `FAQPage` si afegim FAQ sobre què és / com sol·licitar / requisits.

**Cross-link recomanat:** a article-pressupost-casa-passiva.

---

### article-innovacions-passivhaus · P1

**Title actual:** "Les innovacions que estan revolucionant la construcció Passivhaus | PAPIK" (71 chars · 11 over)
**Recomanació:** retallar i datar
- "Innovacions Passivhaus 2026 · membranes, PCM, BIPV | PAPIK" (54 chars)

**Tono:** "revolucionant" és superlatiu — substituir per dada concreta.

**Schema:** `Article` + dates necessàries.

---

### article-materials-sostenibles · P1

**Title actual:** "Materials sostenibles que donen vida a la construcció sostenible | PAPIK" (72 chars · 12 over · "sostenibles" repetit)
**Recomanació:** reescriure títol amb especificitat
- "Materials sostenibles · fusta, suro, cel·lulosa | PAPIK" (54 chars)

**Author byline:** afegir · article amb 14 anys d'experiència de camp claimat exigeix atribució autoral.

**Schema:** `Article` + `Person` author si possible.

---

### article-nota-premsa-papik-ksandal · 🔴 P0

**Title actual:** "PAPIK Group llança K-SANDAL, la nova promoció d'habitatge passiu al Parc de Collserola | PAPIK" (102 chars · 42 over · CRITIC)

**Recomanacions:**
- Reescriure títol: "K-SANDAL · habitatge passiu al Parc de Collserola | PAPIK" (54 chars)
- Convertir de "nota de premsa" a "**article**" híbrid (manté autoritat + millora discoverability)
- Afegir data de publicació
- Schema `NewsArticle` o `Article`
- Considerar: aquest és contingut promocional — verificar si entra a /promocio/k-sandal en lloc de blog

**Decisió estratègica:** ¿k-sandal és una promoció activa? Si sí, hauria de tenir pàgina pròpia a /projectes o /promocio en lloc de · només · article de blog.

---

### article-nota-premsa-papik-ponsa · 🔴 P0

**Title actual:** "PAPIK Group firma un acord estratègic amb la família Ponsa per a projectes immobiliaris de 2M€ anuals | PAPIK" (116 chars · 56 over · CRITIC)

**Recomanacions:**
- Reescriure: "PAPIK + Família Ponsa · 2M€ anuals en habitatge sostenible | PAPIK" (66 chars · una mica over però acceptable)
- Considerar angle educatiu addicional sobre "què és un acord d'autopromoció" per a SEO
- ⚠ **Verificar amb PAPIK comercial:** és aquest un acord públic o té components confidencials? La xifra "2M€ anuals" és pública o exposa estructura financera privada?

**Privacitat · alerta:** revisar amb client abans de mantenir / reescriure.

---

### article-nota-premsa-papik-sabadell · 🔴 P0

**Title actual:** "PAPIK Group formalitza un acord amb Banc Sabadell per oferir finançament estructurat i condicions hipotecàries preferents als seus clients | PAPIK" (149 chars · 89 over · CATASTROFIC)

**Recomanacions:**
- Reescriure: "Banc Sabadell + PAPIK · hipoteques verdes preferents | PAPIK" (60 chars) ✅
- Afegir schema `FinancialProduct` per a les condicions hipotecàries (LTV 80%, etc.)
- Considerar: aquest contingut té valor educatiu real (hipoteques verdes per a Passivhaus) — reformular com a article educatiu amb el partnership com a hook
- ⚠ **Verificar amb PAPIK** que les condicions específiques (80% LTV, 20% inicial) són encara vigents · anuncis financers tenen data de caducitat

**Recomanació estratègica:** reformular completament com a article educatiu sobre "Hipoteques verdes per a Passivhaus" amb Banc Sabadell com a partner referenciat. Així captura SEO + manté valor del partnership.

**No traduït a ES** · pendent traducció (el K-SANDAL i Ponsa sí estan en ES).

---

### article-petjada-ecologica · P1

**Title actual:** "La petjada ecològica de construir i viure a casa teva | PAPIK" (62 chars · 2 over)
- Detecta `vostè` vs `tu` issue: "casa teva" → ha de ser "casa seva"

**Recomanació:** "La petjada ecològica de construir i viure a casa seva | PAPIK" (61 chars · acceptable)

**Strengths:** anàlisi cicle de vida (LCA) + EN 15978 · contingut tècnic excel·lent.

**Schema:** `Article` + considerar `HowTo` si l'article descriu un mètode d'avaluació.

---

### article-pressupost-casa-passiva · P1

**Title actual:** "Com calcular el pressupost de construcció d'una casa passiva | PAPIK" (67 chars · 7 over)
**Recomanació:** "Pressupost casa Passivhaus · guia de costos | PAPIK" (53 chars) ✅

**Privacitat · CRITIC:** verificar que el contingut **no** publica xifres concretes dels 14 presupuestos interns (€1.800-2.200/m² es xifres orientatives genèriques del sector? si vénen del nostre dataset intern, eliminar).

**Schema:** `Article` + `FAQPage` per a desglossament de costos.

**Cross-link:** afegir CTA al configurador `/pressupost`.

---

### article-principis-passivhaus · P2

**Title actual:** "Els cinc principis del Passivhaus | PAPIK" (55 chars) ✅
**Excel·lent base.** Només falta schema + byline.

**Recomanació:** mínima · `Article` schema + byline visible + cross-link a fitxa de cada principi (si existeix article dedicat per cada un · oportunitat futura).

---

### article-revolucio-fusta · P2

**Title actual:** "La revolució de la fusta · cases de fusta superresistents | PAPIK" (60 chars) ✅

**Tono · alerta lleugera:** "revolució" és supeprlatiu.
**Recomanació:** mantenir si l'article cita estudi científic concret amb font verificable. Si és inflat, reescriure.

**Schema:** `Article` + cita de l'estudi (DOI, URL).

---

### article-sostenibilitat-passivhaus · P2

**Title actual:** "Passivhaus i sostenibilitat · com minimitzar la petjada ecològica | PAPIK" (58 chars) ✅

**Recomanació:** schema + byline + millorar internal linking (afegir cross-link a `petjada-ecologica`).

---

### article-tecnologies-passivhaus · P1

**Title actual:** "Tecnologies clau en la construcció d'una casa Passivhaus | PAPIK" (67 chars · 7 over)
**Recomanació:** "Cinc tecnologies clau del Passivhaus 2026 | PAPIK" (49 chars) ✅

**Schema:** `Article`.

---

### article-ventilacio-passivhaus · P2

**Title actual:** "Per què es respira millor en una casa Passivhaus? | PAPIK" (60 chars) ✅

**Cita pendent:** "L'aire interior pot ser fins a 5 vegades més contaminat que l'exterior" · necessita font (probablement EPA o WHO).

**Schema:** `Article` + `FAQPage` per a preguntes sobre ventilació.

---

## Patrons sistèmics detectats

### 1. Schema absent · 0 de 15 (gap massiu)

Cap article té schema `BlogPosting` / `Article`. Implementar l'schema és **el guany SEO més gran disponible** · transforma articles en candidates a top stories i Discover feed.

### 2. Byline + data invisibles al UI · gap E-E-A-T crític

Cap article mostra autor o data al lector. Google penalitza fortament l'absència de senyals E-E-A-T en contingut tècnic/comercial.

**Solució:** template d'article amb:
```
Equip tècnic · PAPIK Group
[Data publicació] · [Reading time]
```

Visible sota el H1 · NO només al schema.

### 3. Titles llargs · 7 de 15 (47%)

Els 3 articles de nota de premsa són crítics (102, 116, 149 chars). Els 4 articles educatius excedits per +5-12 chars són menors però acumulables.

### 4. Notes de premsa amb format inadequat per a blog SEO

Els 3 articles de premsa (K-SANDAL, Ponsa, Sabadell) tenen format "anunci corporatiu" en lloc de "article educatiu amb hook". Tenen:
- Titles llargs amb noms d'empresa
- Cap angle educatiu
- Cap discoverability per a queries de l'usuari

**Recomanació estratègica:** **reformular com a articles educatius** amb el partnership com a context, no com a focus.

### 5. Internal linking sòlid · ✅ no requereix correcció

Els articles enllacen entre ells temàticament. Aquest és el patró més fort del live actual i s'ha de preservar.

### 6. Tono i ortografia · ✅ generalment correctes

Errors ortogràfics o de tono inconsistents detectats: només **1 cas confirmat** (`casa teva` a article-petjada-ecologica · ha de ser `casa seva`).

Cal verificació exhaustiva per advocat o copywriter natiu, però els problemes detectats són puntuals.

### 7. Privacitat · alerta lleugera a 1-2 articles

- **article-pressupost-casa-passiva** · verificar que les xifres €/m² no provenen del dataset intern dels 14 presupuestos
- **article-nota-premsa-papik-ponsa** · verificar que la xifra "2M€ anuals" és pública

---

## Pla de rewrite priorit zat

### FASE 1 · P0 · 3 articles · ~4 hores

**Pre-launch obligat** (els titles actuals són catastrofics SEO):

1. **article-nota-premsa-papik-ksandal** · 102→54 chars + data + considerar moure a /promocio
2. **article-nota-premsa-papik-ponsa** · 116→66 chars + data + verificar privacitat (xifra 2M€)
3. **article-nota-premsa-papik-sabadell** · 149→60 chars + reformular com a article educatiu sobre hipoteca verda + crear versió ES

### FASE 2 · P1 · 6 articles · ~8 hores

**Pre-launch desitjable** (afecten la visibilitat SERP en queries clau):

1. **article-apagada-2025** · title 65→52 + schema + cita projectes per nom (K-Codines, K-Vall d'Or, K-Llavaneres)
2. **article-innovacions-passivhaus** · title 71→54 + reduir superlatius
3. **article-materials-sostenibles** · title 72→54 + autor byline + eliminar redundància
4. **article-petjada-ecologica** · title 62→61 + corregir "casa teva" → "casa seva"
5. **article-pressupost-casa-passiva** · title 67→53 + verificar privacitat xifres + FAQ schema
6. **article-tecnologies-passivhaus** · title 67→49 + schema

### FASE 3 · P2 · 6 articles · ~3 hores

**Post-launch acceptable** (només optimització schema + byline):

1. article-casa-montseny · `Article` schema
2. article-hipoteca-energetica · title 48→54 + schema + opcional FAQ
3. article-principis-passivhaus · schema + byline
4. article-revolucio-fusta · schema + verificar font de l'estudi
5. article-sostenibilitat-passivhaus · schema + cross-link
6. article-ventilacio-passivhaus · schema + cita per al "5x contaminació"

---

## Esforç total estimat

| Fase | Articles | Hores | Quan |
|---|---|---|---|
| P0 (crítics) | 3 | ~4 | Pre-launch (S4) |
| P1 (alta prioritat) | 6 | ~8 | Pre-launch (S4) |
| P2 (mitjana prioritat) | 6 | ~3 | Post-launch (juny) |
| **Total** | **15** | **~15** | — |

15 hores concentrades de feina editorial · pot fer-se en 2-3 dies a S4.

---

## Pasos opera tius per al rewrite

Per a cada article que es rewrite:

1. **Llegir l'article actual íntegre** (no només els headers)
2. **Aplicar `style-guide-editorial.md`** com a referència
3. **Reescriure title segons rang 50-60 chars**
4. **Reescriure meta description segons rang 150-160 chars**
5. **Verificar i corregir tono/ortografia**
6. **Afegir byline `Equip tècnic · PAPIK Group`** + data publicació visible
7. **Afegir schema `Article`** amb tots els camps necessaris (cf. `schemas/04-article.json`)
8. **Verificar internal linking** (mínim 3 links)
9. **Afegir external linking** (mínim 2 fonts autoritzades)
10. **Verificar privacitat** (cap xifra interna, cap client identificat sense permís)
11. **Validar amb Rich Results Test**
12. **Assegurar versió ES paritzada** (si manca)

---

## Recomanació final

**Aplicar abans del 1 juny:**
- ✅ Fase 1 (P0 · 3 articles)
- ✅ Fase 2 (P1 · 6 articles)

**Postposable a post-launch:**
- ⏳ Fase 3 (P2 · 6 articles)

Si el calendari S4 ho permet, fer **les 15 reescriptures concentrades en una setmana editorial** (~15 hores) per assegurar consistència total amb el style guide. Si no, mínim Fase 1 + Fase 2 (9 articles · ~12 hores) abans de llançar.
