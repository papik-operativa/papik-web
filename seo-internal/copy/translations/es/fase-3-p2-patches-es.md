# Patches ES · fase 3 P2 · 6 artículos · traducción de v2 CA

> Versión 2 con las tres enmiendas aplicadas. Estos 6 artículos ya estaban en buena forma editorial en el v1, motivo por el cual este documento define solamente las modificaciones necesarias (no rewrites completos). Todas las sugerencias de copy están en registro v1.1.

---

## Aplicación transversal a los 6

Cada uno de los 6 artículos debe incorporar las mismas adiciones estructurales.

### Byline visible en la UI bajo H1

```html
<div class="article-byline">
  Equipo técnico · PAPIK Group
  <span class="separator">·</span>
  <time datetime="[YYYY-MM-DD]">[Fecha publicación]</time>
  <span class="separator">·</span>
  Tiempo de lectura aproximado [X] min
</div>
```

### Schema JSON-LD `Article`

Se inserta en el `<head>` de cada artículo. La plantilla a utilizar es la siguiente, con los campos marcados sustituidos por valores reales antes de publicar.

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[H1 EXACTO]",
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
    "@id": "[URL CANÓNICA]"
  },
  "articleSection": "[SECCIÓN]",
  "wordCount": [INT],
  "inLanguage": "es-ES",
  "isAccessibleForFree": true
}
</script>
```

Además, cada artículo añade `BreadcrumbList` (Inicio, Blog, [título artículo]) como schema universal.

### Verificación v1.1 en el cuerpo del texto

Independientemente de los cambios específicos, el dev o el copywriter deben revisar el cuerpo de cada artículo para detectar y eliminar guiones largos (que se sustituyen por comas, dos puntos o punto seguido según contexto), aplicar el registro adulto sin frases didácticas tipo "imaginen", "veamos" o "es importante destacar", y convertir listados verticales a párrafos argumentados excepto en los casos previstos en el style guide (procesos numerados, taxonomías heterogéneas, checklists operativos).

---

## 1 · article-casa-montseny · P2

**Title actual:** "Una casa sostenible en las faldas del Montseny | PAPIK" (54 chars). Se mantiene.

**Meta description actual:** dentro del rango. Se mantiene.

**Cambios específicos:**

Añadir byline con fecha de publicación en la UI. Añadir schema `Article` con `articleSection: "Casos de estudio"`. Reforzar el cross-linking final con tres enlaces recomendados: el artículo reescrito sobre [Materiales sostenibles](/es/article-materiales-sostenibles), el artículo reescrito sobre [La huella ecológica de construir y vivir en su casa](/es/article-huella-ecologica), y el enlace a la galería de [Ver otros proyectos en la zona](/es/proyectos). Añadir CTA al final si no está presente: "Solicitar visita a una obra similar → contacto".

Si el contenido menciona el dato de "23,90 toneladas de CO₂ ahorradas", verificar con PAPIK que la cifra proviene del cálculo PHPP del propio proyecto (no extrapolación general). Si es válida, mantenerla con cita interna a la simulación; si no, suavizar a "ahorro acumulado significativo" sin cifra concreta.

**Esfuerzo estimado:** 20 minutos.

---

## 2 · article-hipoteca-energetica · P2

**Title actual:** "¿Qué es la hipoteca energética? | PAPIK" (48 chars). Por debajo del rango óptimo por dos caracteres.

**Title propuesto:** "¿Qué es la hipoteca energética y cuándo vale la pena | PAPIK" (60 chars). Este título amplía ligeramente el contenido prometido sin superar el rango ideal.

**Meta description propuesta:** "Qué es una hipoteca energética y qué ahorros aporta a lo largo de los años para viviendas de alta eficiencia energética. Guía detallada de PAPIK." (147 chars).

**Cambios específicos:**

Renombrar title según propuesta. Añadir byline con fecha. Añadir schema `Article` con `articleSection: "Financiación e hipotecas"`. Añadir cross-link prominente al artículo reescrito [Hipoteca verde para Passivhaus: el acuerdo entre PAPIK y Banc Sabadell](/es/article-nota-prensa-papik-sabadell), ya que este artículo complementa el contenido general sobre hipoteca verde con el caso específico del acuerdo PAPIK y Sabadell. Considerar añadir bloque FAQ con 3 o 4 preguntas (qué es exactamente, cómo se solicita, qué la diferencia de una hipoteca convencional, requisitos habituales) acompañado de schema `FAQPage`.

**Esfuerzo estimado:** 35 minutos.

---

## 3 · article-principis-passivhaus · P2

**Title actual:** "Los cinco principios del Passivhaus | PAPIK" (51 chars). Se mantiene.

**Meta description actual:** dentro del rango. Se mantiene.

**Cambios específicos:**

Añadir byline con fecha. Añadir schema `Article` con `articleSection: "Técnico Passivhaus"`. Reforzar internal linking, ya que este artículo es pillar del cluster Passivhaus y debe conectar con el resto de artículos técnicos: [Tecnologías clave del Passivhaus 2026](/es/article-tecnologias-passivhaus), [Innovaciones Passivhaus 2026](/es/article-innovaciones-passivhaus), [¿Por qué se respira mejor en una casa Passivhaus?](/es/article-ventilacion-passivhaus) y [Sostenibilidad y Passivhaus](/es/article-sostenibilidad-passivhaus). Añadir CTA al final: "Configurar el presupuesto de mi casa Passivhaus → /es/presupuesto".

**Esfuerzo estimado:** 20 minutos.

---

## 4 · article-revolucio-fusta · P2

**Title actual:** "La revolución de la madera · casas de madera superresistentes | PAPIK" (66 chars). Dentro del rango, pero la palabra "revolución" puede ser un superlativo sin base si el artículo no cita un estudio científico concreto.

**Acción previa obligatoria:** verificar con el autor original cuál es la fuente del dato citado en el cuerpo del artículo (referencia a "madera autodensificada con resistencia nueve veces superior" o similar). Si la fuente es sólida (estudio académico concreto con DOI o URL), añadir cita inline en el texto y mantener el title con la palabra "revolución" justificada por el dato. Si la fuente es débil o inexistente, suavizar el cuerpo del texto a una construcción más moderada como "madera de resistencia significativamente superior" y ajustar el title a "Madera superresistente: futuro de los materiales de construcción | PAPIK" (66 chars).

**Cambios específicos:**

Resueltos los puntos anteriores, añadir byline con fecha. Añadir schema `Article` con `articleSection: "Materiales y tecnología"`. Añadir cross-links a [Materiales sostenibles](/es/article-materiales-sostenibles) e [Innovaciones Passivhaus 2026](/es/article-innovaciones-passivhaus). Añadir CTA al final.

**Esfuerzo estimado:** 30 minutos (depende de la verificación de la fuente).

⚠ Acción PAPIK: clarificar con el autor original cuál es la fuente del dato de "9× resistencia" antes de aplicar el patch.

---

## 5 · article-sostenibilitat-passivhaus · P2

**Title actual:** "Passivhaus y sostenibilidad · cómo minimizar la huella ecológica | PAPIK" (66 chars). Dentro del rango, se mantiene.

**Title propuesto alternativo (solo si se quiere simplificar):** "Passivhaus y sostenibilidad: minimizar la huella ecológica | PAPIK" (66 chars). Sustituye el punto volado por dos puntos, en línea con la regla v1.1 que limita el punto volado como recurso ornamental.

**Meta description actual:** dentro del rango. Se mantiene.

**Cambios específicos:**

Añadir byline con fecha. Añadir schema `Article` con `articleSection: "Técnico Passivhaus"`. Cross-link prominente a [La huella ecológica de construir y vivir en su casa](/es/article-huella-ecologica), que es el artículo complementario con el cálculo LCA detallado. Añadir cross-links a [Los cinco principios del Passivhaus](/es/article-principios-passivhaus) y [Materiales sostenibles](/es/article-materiales-sostenibles). Añadir CTA al final: "Configurar el presupuesto de mi proyecto → /es/presupuesto".

**Esfuerzo estimado:** 20 minutos.

---

## 6 · article-ventilacio-passivhaus · P2

**Title actual:** "¿Por qué se respira mejor en una casa Passivhaus? | PAPIK" (60 chars). Dentro del rango, se mantiene.

**Meta description actual:** dentro del rango. Se mantiene.

**Acción previa obligatoria:** localizar la fuente concreta de la cifra "5 veces más contaminado" si aparece en el cuerpo del texto. Las fuentes válidas para esta afirmación son los estudios sobre IAQ (Indoor Air Quality) de la EPA (Environmental Protection Agency de Estados Unidos), los informes sobre calidad del aire interior de la OMS (Organización Mundial de la Salud), o los estudios del BPIE (Building Performance Institute Europe) sobre viviendas europeas. Si se localiza, añadir cita inline en el texto con formato "(EPA · estudios sobre calidad del aire interior, 2023)" o equivalente. Si no se puede localizar, ajustar el texto a una construcción más general como "hasta varias veces más contaminado que el exterior" sin cifra concreta.

**Cambios específicos:**

Resueltos los puntos anteriores, añadir byline con fecha. Añadir schema `Article` y considerar `FAQPage` para las preguntas habituales sobre ventilación. Añadir cross-links a [Tecnologías clave del Passivhaus 2026](/es/article-tecnologias-passivhaus) y [Los cinco principios del Passivhaus](/es/article-principios-passivhaus). Añadir CTA al final: "Configurar el presupuesto de mi casa con VRC → /es/presupuesto".

**Esfuerzo estimado:** 30 minutos.

⚠ Acción PAPIK: validar la fuente del dato "5×" antes de publicar.

---

## Resumen de esfuerzo total Fase 3 P2

La aplicación completa de los patches a los 6 artículos requiere entre 2 horas y 35 minutos y 3 horas totales, según el siguiente desglose:

El artículo casa-montseny necesita 20 minutos (schema, byline y cross-links). El artículo hipoteca-energetica necesita 35 minutos (refinamiento de title y de meta description, schema, cross-link a Sabadell). El artículo principis-passivhaus necesita 20 minutos (schema, byline y cluster linking). El artículo revolucio-fusta necesita 30 minutos dependiendo de la verificación de fuente. El artículo sostenibilitat-passivhaus necesita 20 minutos (schema y linking a huella-ecologica). El artículo ventilacio-passivhaus necesita 30 minutos dependiendo de la verificación de fuente.

---

## Validaciones externas pendientes

Tres puntos requieren verificación externa antes de publicar, con respuesta directa de PAPIK:

La fuente del dato "9× resistencia" en article-revolucio-fusta. ¿Cuál es el estudio original o el artículo técnico del que proviene esta cifra?

La fuente del dato "5× contaminación interior" en article-ventilacio-passivhaus. ¿EPA, OMS, BPIE u otra fuente?

La validación de "23,90 toneladas CO₂" en article-casa-montseny con el cálculo PHPP del proyecto concreto. ¿La cifra proviene del cálculo de simulación real o es una extrapolación general?

Si en algún caso la fuente no se localiza, suavizar el copy a una versión más general sin cifra concreta. La regla es: ningún dato cuantitativo en el copy público sin fuente verificable.

---

## Aplicación práctica · cómo el dev hace esto

Para cada artículo de la Fase 3 P2, el proceso a seguir es el siguiente.

Primero, abrir el fichero `/public/article-[slug].html`. Segundo, aplicar los cambios específicos según este documento de patches. Tercero, verificar en el ES que el byline y la fecha son visibles en la UI, no solo en el schema. Cuarto, validar el schema con el Rich Results Test de Google. Quinto, verificar que los cross-links funcionan correctamente y no conducen a 404s. Sexto, replicar todos los cambios en la versión ES (`/es/article-[slug-traducido].html`) si existe. Séptimo, regenerar el sitemap.xml ejecutando `python3 generate_sitemap.py`. Octavo, commitear con un mensaje claro como "P2 patches v1.1: schema, byline, cross-links · 6 artículos existentes".

Cada patch es aplicable en menos de 30 minutos por artículo. El total para los 6 artículos se sitúa entre 2 y 3 horas, con un ratio de impacto SEO sobre tiempo invertido excepcional.

---

## Cambios respecto a los patches v1

Las sugerencias de copy en este documento v2 están todas en registro v1.1. Se han eliminado los puntos volados como separadores ornamentales dentro de las frases, se han sustituido por comas o puntos seguidos según contexto. Las frases didácticas presentes en el v1 (como "vamos a ver" en castellano o "vegem" en catalán en algunas propuestas de copy) se han eliminado. Los listados verticales de errores frecuentes y de tipos de cambios a aplicar se han convertido a texto continuo o a párrafos argumentados. Se mantiene la estructura de "patches por artículo" porque es un formato operativo inherente al documento (cada artículo tiene sus cambios específicos) y no un listado ornamental.

---

## Cierre del batch v1.1

Este documento cierra el batch v1.1 al 100%. Los 23 ficheros de copy CA (incluyendo este documento de patches) están ahora alineados con el manual de estilo editorial v1.1. El siguiente movimiento lógico es la traducción a ES de los 22 ficheros v1.1 con adaptaciones léxicas, y posteriormente la creación de versiones EN con adaptación cultural en línea con la planificación de la semana 4 (S4) del calendario de prelanzamiento.
