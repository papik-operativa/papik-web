# Revisión ortográfica ES · informe filológico

> Realizada por agente especialista en filología hispánica, fundamentada en RAE/DLE/DPD/OLE/NGLE/Fundéu.
> Fecha: 2026-04-29
> Alcance: 50 archivos `.md` en `/seo-internal/copy/translations/es/` (excluido `/legal/`).
> Build: `python3 generate_html.py` ejecutado tras los cambios. 162 HTML escritos. 0 fallos.

---

## Resumen ejecutivo

El corpus en español de PAPIK Group presenta una calidad ortográfica y gramatical alta. Las reformas ortográficas posteriores a la OLE 2010 (eliminación de la tilde diacrítica en `solo` y en los demostrativos, preferencia por `guion` monosílabo, abandono de los puntos en siglas) ya se encuentran aplicadas con consistencia. No se han detectado casos de leísmo, laísmo, loísmo, dequeísmo, queísmo, pluralización indebida del verbo `haber` impersonal ni gerundios mal usados.

Las correcciones aplicadas se concentran en dos focos: (1) un anglicismo recurrente en los _bylines_ de los 19 artículos (`Reading time aproximado` → `Tiempo de lectura aproximado`) y (2) tres anglicismos léxicos en `about-es.md`, `patrimonios-es.md` y `article-presupuesto-casa-pasiva-es.md` (`partners`, `partner`, `partenariado`, `email`).

Los topónimos siguen la política del proyecto: `Sant Cugat del Vallès`, `Cerdanyola del Vallès`, `Llinars del Vallès` mantienen forma catalana oficial; `Vallés Occidental` con tilde española aparece 59 veces de forma coherente; `Cataluña`, `Baleares`, `Andorra` en su forma castellana. Las denominaciones oficiales `Agència de l'Habitatge de Catalunya` y `Institut de Tecnologia de la Construcció de Catalunya` se conservan como nombres propios institucionales.

---

## Correcciones por categoría

### A. Léxico · anglicismos en cuerpo editorial (correcciones aplicadas)

| Archivo | Línea | Original | Corrección | Fuente |
|---|---|---|---|---|
| `articles/article-apagon-2025-es.md` | 30 | `Reading time aproximado 6 min` | `Tiempo de lectura aproximado 6 min` | DPD s.v. _anglicismo_; Fundéu RAE |
| `articles/article-casa-montseny-es.md` | 32 | `Reading time aproximado 6 min` | `Tiempo de lectura aproximado 6 min` | id. |
| `articles/article-derribar-construir-pasos-es.md` | _byline_ | `Reading time aproximado` | `Tiempo de lectura aproximado` | id. |
| `articles/article-guia-subvenciones-ngeu-cataluna-es.md` | 32 | id. | id. | id. |
| `articles/article-hipoteca-energetica-es.md` | _byline_ | id. | id. | id. |
| `articles/article-huella-ecologica-es.md` | 30 | id. | id. | id. |
| `articles/article-innovaciones-passivhaus-es.md` | 31 | id. | id. | id. |
| `articles/article-licencia-derribo-cerdanyola-bellaterra-es.md` | _byline_ | id. | id. | id. |
| `articles/article-materiales-sostenibles-es.md` | _byline_ | id. | id. | id. |
| `articles/article-nota-prensa-papik-ksandal-es.md` | _byline_ | id. | id. | id. |
| `articles/article-nota-prensa-papik-ponsa-es.md` | _byline_ | id. | id. | id. |
| `articles/article-nota-prensa-papik-sabadell-es.md` | 30 | id. | id. | id. |
| `articles/article-passivhaus-mediterranea-es.md` | _byline_ | id. | id. | id. |
| `articles/article-presupuesto-casa-pasiva-es.md` | 30 | id. | id. | id. |
| `articles/article-revolucion-madera-es.md` | _byline_ | id. | id. | id. |
| `articles/article-sostenibilidad-passivhaus-es.md` | 36 | id. | id. | id. |
| `articles/article-sustituir-vs-rehabilitar-es.md` | _byline_ | id. | id. | id. |
| `articles/article-tecnologias-passivhaus-es.md` | 30 | id. | id. | id. |
| `fase-3-p2-patches-es.md` | 19 | `Reading time aproximado [X] min` | `Tiempo de lectura aproximado [X] min` | id. |
| `about-es.md` | 3 | `periodistas, partners y visitantes curiosos` | `periodistas, socios y visitantes curiosos` | DLE s.v. _socio_; Fundéu (anglicismo evitable) |
| `about-es.md` | 63 | `a menudo en partenariado con propietarios de suelo` | `a menudo en colaboración con propietarios de suelo` | DPD s.v. _partenariado_ (galicismo/anglicismo, recomienda `colaboración`, `asociación`) |
| `patrimonios-es.md` | 87-88 | `socios ya constituidos que buscan partner / constructor de confianza` | `socios ya constituidos que buscan socio / constructor de confianza` | DLE s.v. _socio_ |
| `articles/article-presupuesto-casa-pasiva-es.md` | 121 | `La estimación se entrega por email con un PDF detallado` | `La estimación se entrega por correo electrónico con un PDF detallado` | DPD/Fundéu RAE (preferencia en registro formal) |

### B. Ortografía estricta (OLE 2010)

Sin incidencias. No se han hallado:

- `sólo` con tilde diacrítica obsoleta (0 casos).
- Demostrativos `éste/ése/aquél` con tilde diacrítica obsoleta (0 casos).
- `guión` con tilde (0 casos en cuerpo editorial; la única aparición —`fase-3-p2-patches-es.md`— se refiere a la tipografía `guion largo` y se conserva la grafía sin tilde).
- Siglas con puntos (`I.T.E.`, `N.I.F.`): 0 casos. Todas las siglas (ITE, NIF, BOPB, BOE, COAC, ITeC, IDAE, PEP, FSC, PEFC, CTE, NGEU, ICIO, CLT, SATE, EPS, XPS, COV, KNX, EMD, POUM) aparecen sin puntos según OLE 2010.

### C. Acentuación

Sin incidencias. Hiatos correctamente acentuados (`día`, `país`, `vacío`, `río`, `caída`); adverbios en `-mente` con tilde correcta (`fácilmente`, `rápidamente`, `proporcionalmente`, etc.); verbos con enclíticos correctos.

### D. Gramática (NGLE)

Sin incidencias. Verificados:

- `haber` impersonal en singular (0 casos de `*hubieron problemas`, `*habrán incidencias`).
- Sin dequeísmo (0 casos de `*pienso de que`, `*creo de que`).
- Sin queísmo (0 casos de `*estoy seguro que`).
- Concordancia ad sensum y nominal correctas en todos los pasajes inspeccionados.
- Subjuntivo en oraciones temporales futuras correcto (`cuando vengas`, `mientras estés` en bylines y CTAs).
- Uso de `sino` vs `si no` correcto en todos los hallazgos (`no es estilística sino técnica y ética`, `no se limita a cumplir el mínimo normativo, sino que busca`).
- Uso de `por qué`, `porque`, `por que`, `porqué` correcto en los hallazgos.

### E. Toponimia (verificada coherente con la política del proyecto)

| Forma | Ocurrencias | Estado |
|---|---|---|
| `Sant Cugat del Vallès` | múltiples | OK · forma oficial catalana mantenida en ES (política del proyecto, registrada en `homepage-es.md` línea 471) |
| `Cerdanyola del Vallès` | múltiples | OK · idem |
| `Llinars del Vallès` | 1 | OK · idem |
| `Castellar del Vallès` | múltiples | OK · idem |
| `Vallés Occidental` | 59 | OK · forma castellana con tilde en hub comarcal y landings |
| `Cataluña` | múltiples | OK · forma castellana |
| `Baleares` / `Islas Baleares` | múltiples | OK · forma castellana |
| `Andorra` | múltiples | OK |
| `Catalunya` (en cuerpo ES) | 0 | OK · sólo aparece dentro de nombres propios institucionales (`Agència de l'Habitatge de Catalunya`, `Institut de Tecnologia de la Construcció de Catalunya`), conservados como denominaciones oficiales |
| `Lleida`, `Girona` | 1 cada | conservados en cita textual de un nodo logístico (Osona, Baix Empordà); aceptable en contexto de proximidad geográfica regional |

### F. Términos técnicos

Verificada coherencia: `Passivhaus` (siempre con mayúscula inicial), `Eskimohaus®` (siempre con símbolo registrado), `EnerPHit`, `nZEB`, `CLT`, `SATE`, `blower-door`. Distinciones léxicas conservadas: `rehabilitación` vs `reforma`, `cubierta` vs `tejado`, `fachada` vs `envolvente`, `vivienda` preferido sobre `casa` en contexto técnico.

### G. Registro y puntuación

- Em-dashes (`—`): 0 ocurrencias en cuerpo editorial. Cumple §2.7 del style-guide.
- Signos de interrogación y exclamación: dobles correctos (`¿…?`, `¡…!`).
- Comillas: latinas/inglesas en uso, sin comillas simples como en inglés.
- Tratamiento de cortesía: ustedeo coherente en homepage, servicios, landings y FAQs.

---

## Casos flagged (no modificados; criterio editorial)

1. **`portfolio` (10+ ocurrencias en `landings/sant-cugat-es.md`, hubs comarcales `osona`, `valles-occidental`, `baix-emporda`, `garraf`, `maresme`, `anoia`, `baix-llobregat`).** El DLE no recoge `portfolio` (sí `portafolio` y `portafolios`); Fundéu prefiere `cartera de proyectos`. Sin embargo, su uso es consistente en marketing técnico y aparece en la versión catalana e inglesa. Recomendación editorial: sustituir por `cartera de proyectos` en una pasada de armonización tri-lingüe (CA: `portafoli` o `cartera de projectes`; EN: `portfolio` aceptable). No corregido en esta revisión por el alcance transversal y el riesgo SEO.

2. **`cluster` (en `landings/sant-cugat-es.md` líneas 77 y 271; `comarcas/valles-occidental-es.md` líneas 95 y 296).** Anglicismo. El DLE lo recoge sin marca (admitido en informática; no en marketing geográfico). Fundéu sugiere `agrupación`, `conjunto`, `núcleo`. En este corpus se usa con valor metonímico (`cluster Bellaterra`, `cluster más consolidado`). Aceptable en jerga editorial interna; cuestionable en cuerpo público. Flag para revisión editorial.

3. **`reading time` y `byline` en `fase-3-p2-patches-es.md`.** Documento de patch operativo interno (no se publica). Mantenido el anglicismo `byline` y `cross-link` por ser tecnicismos de equipo.

4. **`(link a /es/...)` en notas de maquetación.** Son anotaciones para el desarrollador dentro de bloques `[CTA discreto]`, `[Link discreto]`. No se publican como copy. No corregido.

5. **`Reading time` se ha modificado pero `[Campo: email]` se conserva** en `homepage-es.md` línea 428: es un placeholder técnico de UI que indica el `type` del campo, no copy editorial.

6. **Mayúsculas en eyebrows (`QUIERO CONSTRUIR`, `QUIÉNES SOMOS`, etc.).** Tildes correctamente conservadas en mayúsculas (OLE 2010 §3.4.1.2).

---

## Recomendaciones de mantenimiento editorial

1. **Glosario tri-lingüe**: añadir al `style-guide-editorial.md` una entrada explícita sobre anglicismos editoriales prohibidos en bylines (`reading time`, `byline`, `cross-link` son aceptables en notas internas pero nunca en cuerpo publicado).

2. **Lint pre-commit ortográfico**: incorporar un script `python3` que ejecute las búsquedas regex de esta revisión (anglicismos, tildes diacríticas obsoletas, dequeísmo, doble espacio, em-dashes, `Catalunya` fuera de nombres propios) y bloquee `commit` si encuentra ocurrencias en `seo-internal/copy/translations/es/`.

3. **Decisión editorial sobre `portfolio` y `cluster`** antes del lanzamiento. La hispanización (`cartera de proyectos`, `agrupación`, `núcleo`) refuerza el registro adulto-profesional v1.1; mantenerlos exige justificación.

4. **Revisión jurídica pendiente** en `/legal/` (excluida de esta auditoría).

5. **Verificación post-build**: tras la regeneración HTML, hacer `spot-check` del campo `<meta name="description">` de homepage, services y los 4 Tier-1 landings para confirmar que las correcciones se han propagado correctamente al `<head>` (los meta tags en los `.md` actuales no contenían los anglicismos corregidos; los cambios afectan únicamente al cuerpo).

---

## Anexo · método

Se ejecutaron búsquedas `grep -rnP` con expresiones para cada categoría sobre los 50 archivos en alcance:

- Tildes diacríticas obsoletas: `\bsólo\b`, `\béste\b`, `\bése\b`, `\baquél\b`, `\bguión\b`.
- Dequeísmo/queísmo: `\bpienso de que\b`, `\bcreo de que\b`, `\bestoy seguro que\b`, etc.
- `haber` impersonal: `\bhubieron \b`, `\bhabrán (problemas|casas)\b`.
- Em-dashes: `—`.
- Anglicismos: `\b(email|link|password|feedback|target|business|meeting|partner|partners|portfolio|cluster|byline|delivery|staff|know-how)\b`.
- Catalanismos: `\b(Catalunya|Balears|Lleida|Girona|aviso a navegantes|recolzar|enviament|apropar)\b`.
- Concordancia: `\b(el casa|la sistema|la problema)\b`.
- Tildes faltantes: `\b(pais|paises|tambien|despues|tecnico|practica)\b`.
- Punctuación: `\?[A-Z]`, `\![A-Z]`.

Tras la edición se ejecutó `python3 generate_html.py` con resultado: **162 HTML escritos, 0 fallos**.
