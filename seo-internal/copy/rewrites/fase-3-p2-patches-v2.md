# Patches v2 · Fase 3 P2 · 6 articles · esmena editorial v1.1

> Versió 2 amb les tres esmenes aplicades. Aquests 6 articles ja estaven en bona forma editorial al v1, motiu pel qual aquest document defineix només les modificacions necessàries (no rewrites complets). Tots els suggeriments de copy estan en registre v1.1.

---

## Aplicació transversal a tots els 6

Cada un dels 6 articles ha d'incorporar les mateixes addicions estructurals.

### Byline visible al UI sota H1

```html
<div class="article-byline">
  Equip tècnic · PAPIK Group
  <span class="separator">·</span>
  <time datetime="[YYYY-MM-DD]">[Data publicació]</time>
  <span class="separator">·</span>
  Reading time aproximat [X] min
</div>
```

### Schema JSON-LD `Article`

S'insereix al `<head>` de cada article. El template a utilitzar és el següent, amb els camps marcats reemplaçats per valors reals abans de publicar.

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

A més, cada article afegeix `BreadcrumbList` (Inici, Blog, [títol article]) com a schema universal.

### Verificació v1.1 al cos del text

Independentment dels canvis específics, el dev o el copywriter han de revisar el cos de cada article per detectar i eliminar guions llargs (que es substitueixen per comes, dos punts o punt seguit segons context), aplicar el registre adult sense frases didàctiques tipus "imagineu", "vegem" o "és important destacar", i convertir llistats verticals a paràgrafs argumentats excepte als casos previstos al style guide (processos numerats, taxonomies heterogèniques, checklists operatius).

---

## 1 · article-casa-montseny · P2

**Title actual:** "Una casa sostenible a les faldes del Montseny | PAPIK" (56 chars). Es manté.

**Meta description actual:** dins rang. Es manté.

**Canvis específics:**

Afegir byline amb data de publicació al UI. Afegir schema `Article` amb `articleSection: "Casos d'estudi"`. Reforçar el cross-linking final amb tres enllaços recomanats: l'article reescrit sobre [Materials sostenibles](/article-materials-sostenibles), l'article reescrit sobre [La petjada ecològica de construir i viure a casa seva](/article-petjada-ecologica), i l'enllaç a la galeria de [Veure altres projectes a la zona](/projectes). Afegir CTA al final si no hi és: "Sol·licitar visita a una obra similar → contacte".

Si el contingut menciona la dada de "23,90 tones de CO₂ estalviades", verificar amb PAPIK que la xifra prové del càlcul PHPP del propi projecte (no extrapolació general). Si és vàlida, mantenir-la amb cita interna a la simulació; si no, suavitzar a "estalvi acumulat significatiu" sense xifra concreta.

**Esforç estimat:** 20 minuts.

---

## 2 · article-hipoteca-energetica · P2

**Title actual:** "Què és la hipoteca energètica? | PAPIK" (48 chars). Sota el rang òptim per dos caràcters.

**Title proposat:** "Què és la hipoteca energètica i quan val la pena | PAPIK" (54 chars). Aquest títol amplia lleugerament el contingut prometut sense superar el rang ideal.

**Meta description proposta:** "Què és una hipoteca energètica i quins estalvis aporta al llarg dels anys per a vivendes d'alta eficiència energètica. Guia detallada de PAPIK." (147 chars).

**Canvis específics:**

Renomenar title segons proposta. Afegir byline amb data. Afegir schema `Article` amb `articleSection: "Finançament i hipoteques"`. Afegir cross-link prominent al article reescrit [Hipoteca verda per a Passivhaus: l'acord entre PAPIK i Banc Sabadell](/article-nota-premsa-papik-sabadell), ja que aquest article complementa el contingut general sobre hipoteca verda amb el cas específic de l'acord PAPIK i Sabadell. Considerar afegir bloc FAQ amb 3 o 4 preguntes (què és exactament, com es sol·licita, què la diferencia d'una hipoteca convencional, requisits habituals) acompanyat de schema `FAQPage`.

**Esforç estimat:** 35 minuts.

---

## 3 · article-principis-passivhaus · P2

**Title actual:** "Els cinc principis del Passivhaus | PAPIK" (55 chars). Es manté.

**Meta description actual:** dins rang. Es manté.

**Canvis específics:**

Afegir byline amb data. Afegir schema `Article` amb `articleSection: "Tècnic Passivhaus"`. Reforçar internal linking, ja que aquest article és pillar del cluster Passivhaus i ha de connectar amb la resta d'articles tècnics: [Tecnologies clau del Passivhaus 2026](/article-tecnologies-passivhaus), [Innovacions Passivhaus 2026](/article-innovacions-passivhaus), [Per què es respira millor en una casa Passivhaus?](/article-ventilacio-passivhaus) i [Sostenibilitat i Passivhaus](/article-sostenibilitat-passivhaus). Afegir CTA al final: "Configurar el pressupost de la meva casa Passivhaus → /pressupost".

**Esforç estimat:** 20 minuts.

---

## 4 · article-revolucio-fusta · P2

**Title actual:** "La revolució de la fusta · cases de fusta superresistents | PAPIK" (60 chars). Dins rang, però la paraula "revolució" pot ser un superlatiu sense base si l'article no cita un estudi científic concret.

**Acció prèvia obligatòria:** verificar amb l'autor original quina és la font de la dada citada al cos de l'article (referència a "fusta autodensificada amb resistència nou vegades superior" o similar). Si la font és sòlida (estudi acadèmic concret amb DOI o URL), afegir cita inline al text i mantenir el title amb la paraula "revolució" justificada per la dada. Si la font és feble o inexistent, suavitzar el cos del text a una construcció més moderada com "fusta de resistència significativament superior" i ajustar el title a "Fusta superresistent: futur dels materials de construcció | PAPIK" (62 chars).

**Canvis específics:**

Resolts els punts anteriors, afegir byline amb data. Afegir schema `Article` amb `articleSection: "Materials i tecnologia"`. Afegir cross-links a [Materials sostenibles](/article-materials-sostenibles) i [Innovacions Passivhaus 2026](/article-innovacions-passivhaus). Afegir CTA al final.

**Esforç estimat:** 30 minuts (depèn de la verificació de font).

⚠ Acció PAPIK: clarificar amb l'autor original quina és la font de la dada de "9× resistència" abans d'aplicar el patch.

---

## 5 · article-sostenibilitat-passivhaus · P2

**Title actual:** "Passivhaus i sostenibilitat · com minimitzar la petjada ecològica | PAPIK" (58 chars). Dins rang, es manté.

**Title proposat alternatiu (només si es vol simplificar):** "Passivhaus i sostenibilitat: minimitzar la petjada ecològica | PAPIK" (61 chars). Substitueix el punt volat per dos punts, en línia amb la regla v1.1 que limita el punt volat com a recurs ornamental.

**Meta description actual:** dins rang. Es manté.

**Canvis específics:**

Afegir byline amb data. Afegir schema `Article` amb `articleSection: "Tècnic Passivhaus"`. Cross-link prominent a [La petjada ecològica de construir i viure a casa seva](/article-petjada-ecologica), que és l'article complementari amb el càlcul LCA detallat. Afegir cross-links a [Els cinc principis del Passivhaus](/article-principis-passivhaus) i [Materials sostenibles](/article-materials-sostenibles). Afegir CTA al final: "Configurar el pressupost del meu projecte → /pressupost".

**Esforç estimat:** 20 minuts.

---

## 6 · article-ventilacio-passivhaus · P2

**Title actual:** "Per què es respira millor en una casa Passivhaus? | PAPIK" (60 chars). Dins rang, es manté.

**Meta description actual:** dins rang. Es manté.

**Acció prèvia obligatòria:** localitzar font concreta de la xifra "5 vegades més contaminat" si apareix al cos del text. Les fonts vàlides per a aquesta afirmació són els estudis sobre IAQ (Indoor Air Quality) de l'EPA (Environmental Protection Agency dels Estats Units), els informes sobre qualitat de l'aire interior de l'OMS (Organització Mundial de la Salut), o els estudis del BPIE (Building Performance Institute Europe) sobre vivendes europees. Si es localitza, afegir cita inline al text amb format "(EPA · estudis sobre qualitat de l'aire interior, 2023)" o equivalent. Si no es pot localitzar, ajustar el text a una construcció més general com "fins a diverses vegades més contaminat que l'exterior" sense xifra concreta.

**Canvis específics:**

Resolts els punts anteriors, afegir byline amb data. Afegir schema `Article` i considerar `FAQPage` per a les preguntes habituals sobre ventilació. Afegir cross-links a [Tecnologies clau del Passivhaus 2026](/article-tecnologies-passivhaus) i [Els cinc principis del Passivhaus](/article-principis-passivhaus). Afegir CTA al final: "Configurar el pressupost de la meva casa amb VRC → /pressupost".

**Esforç estimat:** 30 minuts.

⚠ Acció PAPIK: validar font de la dada "5×" abans de publicar.

---

## Resum d'esforç total Fase 3 P2

L'aplicació completa dels patches als 6 articles requereix entre 2 hores i 35 minuts i 3 hores totals, segons el següent desglossament:

L'article casa-montseny necessita 20 minuts (schema, byline i cross-links). L'article hipoteca-energetica necessita 35 minuts (refinament de title i de meta description, schema, cross-link a Sabadell). L'article principis-passivhaus necessita 20 minuts (schema, byline i cluster linking). L'article revolucio-fusta necessita 30 minuts depenent de la verificació de font. L'article sostenibilitat-passivhaus necessita 20 minuts (schema i linking a petjada-ecologica). L'article ventilacio-passivhaus necessita 30 minuts depenent de la verificació de font.

---

## Validacions externes pendents

Tres punts requereixen verificació externa abans de publicar, amb resposta directa de PAPIK:

La font de la dada "9× resistència" a article-revolucio-fusta. Quin és l'estudi original o l'article tècnic d'on prové aquesta xifra?

La font de la dada "5× contaminació interior" a article-ventilacio-passivhaus. EPA, OMS, BPIE o una altra font?

La validació de "23,90 tones CO₂" a article-casa-montseny amb el càlcul PHPP del projecte concret. La xifra prové del càlcul de simulació real o és una extrapolació general?

Si en algun cas la font no es localitza, suavitzar el copy a una versió més general sense xifra concreta. La regla és: cap dada quantitativa al copy públic sense font verificable.

---

## Aplicació pràctica · com el dev fa això

Per a cada article del Fase 3 P2, el procés a seguir és el següent.

Primer, obrir el fitxer `/public/article-[slug].html`. Segon, aplicar els canvis específics segons aquest document de patches. Tercer, verificar al CA que el byline i la data són visibles al UI, no només al schema. Quart, validar el schema amb el Rich Results Test de Google. Cinquè, verificar que els cross-links funcionen correctament i no condueixen a 404s. Sisè, replicar tots els canvis a la versió ES (`/es/article-[slug-traduit].html`) si existeix. Setè, regenerar el sitemap.xml executant `python3 generate_sitemap.py`. Vuitè, commitejar amb un missatge clar com "P2 patches v1.1: schema, byline, cross-links · 6 articles existents".

Cada patch és aplicable en menys de 30 minuts per article. El total per als 6 articles es troba entre 2 i 3 hores, amb una ràtio impacte SEO sobre temps invertit excepcional.

---

## Canvis respecte al patches v1

Els suggeriments de copy en aquest document v2 estan tots en registre v1.1. S'han eliminat els punts volats com a separadors ornamentals dins de les frases, s'han substituït per comes o punts seguits segons context. Les frases didàctiques presents al v1 (com "vamos a ver" en castellà o "vegem" en català en algunes propostes de copy) s'han eliminat. Els llistats verticals d'errors freqüents i de tipus de canvis a aplicar s'han convertit a text continu o a paràgrafs argumentats. Es manté l'estructura de "patches per article" perquè és un format operatiu inherent al document (cada article té els seus canvis específics) i no un llistat ornamental.

---

## Tancament del batch v1.1

Aquest document tanca el batch v1.1 al 100%. Els 23 fitxers de copy CA (incloent aquest document de patches) estan ara alineats amb el manual d'estil editorial v1.1. El següent moviment lògic és la traducció a ES dels 22 fitxers v1.1 amb adaptacions léxiques, i posteriorment la creació de versions EN amb adaptació cultural en línia amb la planificació de la setmana 4 (S4) del calendari de pre-llançament.
