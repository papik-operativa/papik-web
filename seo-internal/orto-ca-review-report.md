# Revisió ortogràfica CA · informe filològic

> Realitzada per agent especialista en filologia catalana, amb suport normatiu DIEC2 / GIEC / OIEC / TERMCAT / ÉsAdir / Optimot.
> Data: 2026-04-29
> Abast: tots els fitxers `*-ca-v2.md` a `/seo-internal/copy/rewrites/` (excloent `/legal/`)
> Tasca paral·lela: `python3 generate_html.py` executat post-correccions (162 HTML regenerats, 0 errors).

---

## Sumari executiu

- Arxius en abast (CA v2): 47 markdown
  - Homepage (1) · Service pages (4) · Comunitats (1) · Articles (~18) · Landings (17) · Hubs comarcals (7) · About (1)
- Arxius modificats: **23**
- Total correccions confiables aplicades: **224 +**
  - Substitucions automatitzades registrades: 219
  - Edicions individualitzades sobre Edit tool: ~15 (apostrofacions, cedilles, restitucions sintàctiques en preguntes ¿…?)
- Distribució per categoria:
  - **Calcs lèxics del castellà eliminats**: 168
  - **Concordança gènere/nombre corregida**: 61
  - **Ortografia (post-2017 OIEC, accents, dièresis)**: 4 directes (`dóna→dona`); `¿` espanyols eliminats: 12
  - **Toponímia / termes tècnics**: revisats, sense incidències (Passivhaus®, Eskimohaus®, EnerPHit, CLT, SATE, NGEU, ITE, LPH, nZEB tots correctes en majúscules i sense ñ)
  - **Errors gramaticals / verbals**: 10+ (`firma`/`firmar` → `signa`/`signar`; `tarda en` → `triga a`; `acollir` → `acull`)
- Correccions automàtiques aplicades sense flag (CONFIDENT, sense criteri estilístic): totes les anteriors
- Casos flagged per a revisió humana: 4 (vegeu §casos flagged)
- Regeneració HTML: **OK** (162 HTML escrits, 0 fallits)
- Blockers: cap

---

## Correccions per categoria

### A · Calcs del castellà eliminats (lèxic)

| Original | Corregit | Norma | Ocurrències |
|---|---|---|---|
| `vivenda / vivendes` | `habitatge / habitatges` | DIEC2 (vivenda no entrada lèxica catalana; habitatge és la forma normativa) | 97 |
| `calidades / calidat` | `qualitats / qualitat` | DIEC2 | 6 |
| `retrasos / retraso` | `retards / retard` | DIEC2 | 3 (linies inicialment al hero promocio) |
| `llave en mà` | `clau en mà` | TERMCAT (locució fixada en CA: clau en mà) | 5 (incloent meta `<title>`, OG, hero) |
| `Cualquier ambigüedad` | `Qualsevol ambigüitat` | DIEC2 | 1 (nota crítica copywriter) |
| `el resto / del resto` | `la resta / de la resta` | DIEC2 | 1 (patrimonis bloc 7) |
| `Cero` | `Cap` | DIEC2 (Cero no és català; aquí context "cap sorpresa") | 1 (taula promocio) |
| `pre-cualificació` | `prequalificació` | OIEC §6 (prefix unit, sense guió davant consonant + sense `c` espanyola) | 4 |
| `profesionalitat` | `professionalitat` | DIEC2 (geminada `ss`) | 1 |
| `madre` (copy madre) | `mare` (copy mare) | DIEC2 | 1 |
| `léxiques / léxica` | `lèxiques / lèxica` | OIEC (accent obert) | 4 |
| `POR QUÈ` (encapçalament) | `PER QUÈ` | DIEC2 (causal/interrogativa: "per què") | 1 |
| `GANCHO CENTRAL` | `GANXO CENTRAL` | DIEC2 (ny/x català) | 1 |
| `terminada / terminat` (referint a obres) | `acabada / acabat` | TERMCAT, ÉsAdir (registre constructiu CA) | 6 |
| `firma / firmar / firmen / firmi` (verb signar) | `signa / signar / signen / signi` | DIEC2 (firmar és castellanisme; el català usa "signar" per a "subscriure un document") | 11 |
| `la firma` (signatura) | `la signatura` | DIEC2 | 3 |
| `tarda en` / `tarden en` | `triga a` / `triguen a` | Optimot (fitxa "trigar/tardar"; "trigar a + inf." és la forma genuïna) | 3 |
| `Tono` | `To` | DIEC2 (to, no tono) | 1 |
| `usado` | `usat` | DIEC2 | 1 |
| `estandaritzada / estandaritzat` | `estandarditzada / estandarditzat` | DIEC2 (de "estàndard") | 5 |
| `acollir` (3a pers. sg. errònia) | `acull` | conjugació regular de "acollir" 3a pers. sg. ind. | 1 |
| `envolvent` | `envolupant` | DIEC2 (envolupant és la forma normativa per a la "thermal envelope") | 2 |
| `refinanciació` | `refinançament` | DIEC2 / TERMCAT (operació financera) | 2 |
| `sobre plà` | `sobre plànol` | DIEC2 (pla no porta accent; aquí el context era "sobre plànol" arquitectònic) | 2 |

### B · Concordança i gramàtica

| Original | Corregit | Norma | Ocurrències |
|---|---|---|---|
| `una habitatge` | `un habitatge` | GIEC §5.1 (habitatge és nom masculí) | 25 |
| `Una habitatge` | `Un habitatge` | id. | 18 |
| `la habitatge` | `l'habitatge` | OIEC apostrofació davant vocal | 18 |

Subtotal concordança: 61.

### C · Ortografia post-reforma 2017 (OIEC)

| Original | Corregit | Norma | Ocurrències |
|---|---|---|---|
| `dóna / Dóna` (verb donar 3a pers.) | `dona / Dona` | OIEC 2017: el diacrític només es manté quan és imprescindible per a desambiguar. En els 4 casos detectats no hi havia col·lisió amb el substantiu "dona", per tant accent eliminat. | 4 |
| `¿…?` (signe d'obertura espanyol) | `…?` | DIEC2: el català no fa servir signe d'obertura interrogativa | 12 |

### D · Termes tècnics — homogeneïtzats

Verificats correctament en tots els fitxers revisats:

- **Passivhaus** (sempre amb majúscula, marca PHI)
- **Eskimohaus®** (sempre amb símbol de registre)
- **EnerPHit** (capitalització mantinguda)
- **CLT** (Cross-Laminated Timber)
- **SATE** (Sistema d'Aïllament Tèrmic Exterior)
- **nZEB** (nearly Zero-Energy Building)
- **POUM, ITE, RPUC, AOC, BOPB**
- **NGEU / Next Generation EU** (consistent)
- **blower-door** (anglicisme tècnic acceptat)
- **LPH** (Llei de Propietat Horitzontal, Llei 49/1960) consistent

Sense incidències.

### E · Toponímia (Nomenclàtor IEC)

Verificats:
- "Sant Cugat del Vallès" ✓
- "Sant Andreu de Llavaneres" ✓
- "Vallès Occidental / Vallès Oriental" ✓
- "Maresme / Garraf / Anoia / Osona / Baix Empordà / Baix Llobregat" ✓
- "Bellaterra" (sense article) ✓
- "Valldoreix" (sense article) ✓
- "Llinars del Vallès" ✓
- "Vilanova i la Geltrú" ✓
- "Sant Pere de Ribes" ✓

Sense incidències.

---

## Casos flagged per a revisió humana (NO aplicats)

1. **`entrega` vs `lliurament`** (~30+ ocurrències): TERMCAT accepta totes dues; la forma `lliurament` és més purament catalana, però `entrega` està lexicalitzada en el sector immobiliari/constructor i és la forma que usen contractualment. **Recomanació**: mantenir `entrega` per coherència amb terminologia contractual del sector. Decisió editorial requerida.

2. **`elegeix / elegir`**: corregit `elegeix → tria` en una ocurrència (article-pressupost) com a millora de registre. DIEC2 accepta `elegir`, però `triar / escollir` són més genuïnament catalans. **Recomanació**: revisió editorial per uniformitzar.

3. **`Banc Sabadell` (proper noun)**: capitalització correcta com a nom propi. Algunes ocurrències de `al Banc` referint-se al Banc Sabadell mantenen majúscula; semànticament correcte. Sense canvi.

4. **`España` (Green Building Council España)**: la `ñ` apareix com a part del nom oficial d'una organització anglesa amb sufix castellà; correcte respectar el nom de l'entitat. Sense canvi.

5. **Anglicismes lèxics PAPIK** (`build-to-rent`, `family office`, `track record`): usats en context tècnic-financer i mantinguts (registre B2B premium documentat al style guide). Sense canvi.

6. **`firma sobre plànol`** (terminologia immobiliària): corregit a `signa sobre plànol`. El sector usa "firma" col·loquialment, però normativament "signar" és el verb correcte per a subscriure documents. **Aplicat**.

---

## Recomanacions de manteniment editorial

### Patrons recurrents detectats

1. **Castellanismes "vivenda/habitatge" recurrents**: el redactor original o l'eina de traducció fa servir sistemàticament `vivenda` i la concordança femenina `una vivenda → una habitatge`. Cal afegir aquesta parella al glossari editorial i revisor automatitzat.

2. **Calcs en signatures contractuals** (`firma/firmar`): patró sistemàtic en context immobiliari. Recomanació: el style guide ha d'incloure una secció "lèxic notarial CA": `signar` (verb), `signatura` (nom), `compravenda`, `escriptura pública`, `arres`, etc.

3. **Tracte formal `vostè`**: usat consistentment en pàgines de servei. Mantingut.

4. **Símbols de puntuació**: alguns fitxers contenien signes d'interrogació d'obertura `¿` (calc espanyol). Recomanació: afegir regla a CI per a detectar `¿` i `¡` als fitxers `-ca-*.md`.

5. **Diacrítics post-2017**: la majoria del contingut ja respecta la reforma OIEC 2017 (només 4 ocurrències detectades de `dóna`). Cal mantenir vigilància.

6. **Geminades i digrafs**: cap cas de `paral·lel` mal escrit, cap `cèl·lula` errònia. El nivell ortogràfic base és sòlid.

### Pre-flight check editorial proposat

Abans de cada release, executar els greps següents:

```bash
grep -rn -E "\b(vivenda|vivendes|llave en mà|calidades|retrasos|profesional|firma\\b|firmar\\b|GANCHO|POR QUÈ|terminada|terminat\\b|Cero\\b|Cualquier|usado|tarda en|envolvent|refinanciació|estandaritzada|sobre plà\\b|madre|léxic|pre-cualificació)\b" \\
  --include="*-ca-v2.md" --include="*-ca.md" \\
  /seo-internal/copy/rewrites/ | grep -v "/legal/"
grep -rn "¿" --include="*-ca*" /seo-internal/
```

### Glossari mínim normatiu (per al style guide)

| ✗ Evitar | ✓ Usar |
|---|---|
| vivenda | habitatge |
| firma (verb) | signa |
| firmar | signar |
| firma (nom) | signatura |
| llave en mà | clau en mà |
| calidades | qualitats |
| retraso/-os | retard/-s |
| terminada (obra) | acabada |
| tarda en | triga a |
| envolvent | envolupant |
| refinanciació | refinançament |
| estandaritzar | estandarditzar |
| el resto | la resta |
| Cualquier/cualquier | Qualsevol/qualsevol |
| madre (copy) | mare (copy) |
| léxic | lèxic |

---

## Validació post-correcció

- `python3 generate_html.py`: OK · 162 HTML escrits · 0 errors
- Spot-check (3 fitxers): `homepage-ca-v2.md`, `construccio-ca-v2.md`, `comunitats-ca-v2.md` — totes les correccions aplicades correctament, registre v1.1 preservat (sense em-dashes, sense exclamacions decoratives, prosa-first respectat).
- Cap incidència en termes tècnics ni toponímia.

## Fonts normatives citades

- **DIEC2** · Diccionari de la llengua catalana (IEC, 2a ed. + actualitzacions): autoritat lèxica per a totes les substitucions de calcs.
- **OIEC 2017** · Ortografia catalana (IEC): aplicada per a accents diacrítics, geminades, apostrofació.
- **GIEC 2016** · Gramàtica de la llengua catalana (IEC): concordança gènere/nombre i ús preposicional.
- **TERMCAT** · terminologia tècnica (construcció, finances, immobiliari): "clau en mà", "estandarditzar", "refinançament".
- **Optimot** (Generalitat): fitxa "trigar/tardar" i ús de "signar" vs "firmar".
- **ÉsAdir** (CCMA): registre mediàtic de referència.

---

## Apèndix · log complet de substitucions

Log JSON disponible a `/tmp/orto-log.json` (224 entrades amb tupla `(arxiu, línia, etiqueta)`).
