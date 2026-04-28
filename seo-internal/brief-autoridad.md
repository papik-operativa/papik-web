# Content briefs — `/premsa` + `/certificacions` (autoridad / E-E-A-T)

> INTERNAL DOCUMENT. Not to be published. Both pages use ONLY public, third-party-verifiable content. No internal data.

---

## Página 1 · `/premsa` · `/es/prensa` · `/en/press`

### Objetivo estratégico

Concentrar **toda** la cobertura editorial ganada por PAPIK en un único hub. Hoy esas piezas están dispersas como posts individuales o, peor, perdidas. Centralizándolas:

1. Subimos el **E-E-A-T** del dominio (Experience-Expertise-Authoritativeness-Trustworthiness — factor de ranking)
2. Damos al lead frío argumento de prueba social en 5 segundos
3. Generamos una página citable por terceros (medios, partners, clientes)
4. Recuperamos backlinks a URLs hoy rotas (mediante el redirect map)

### Inventario inicial · contenido a incluir

> Todas estas piezas son verificables públicamente. Las marcadas ⚠ requieren confirmación de que la URL está viva o se sustituye por captura de pantalla.

**TV / radio / vídeo:**
- TV3 "Lletra Petita: Energia a la llar" (Cap.10, T1, 17/04/2013) — URL viva en 3Cat
- Betevé "Verd Primera" (18/04/2017) ⚠ URL original perdida — usar reproducción interna
- Cugat Mèdia (versión audio de la entrevista de Papik Fisas)
- TV3 / 3Cat — cualquier otra aparición que se localice

**Prensa nacional / regional:**
- La Vanguardia · Lorena Farràs · "Llega la ventilación inteligente" (~2017) ⚠ URL detrás de paywall
- L'Econòmic (21/06/2014) ⚠ URL perdida
- ARA (si existe) — pendiente de búsqueda
- El Punt Avui (vinculado a L'Econòmic)

**Prensa local Sant Cugat / comarca:**
- Cugat Mèdia · entrevista a Papik Fisas (2 piezas, viva)
- TOT Sant Cugat · "Papik, la teva casa a mida" (viva)
- TOT Sant Cugat · "Sant Cugat estrena casa passiva certificada" (viva)
- Diari de Sant Cugat (20/06/2014, "Habitatges del futur") ⚠ URL perdida

**Prensa sectorial / arquitectura:**
- Construnario · 3 piezas Eskimohaus / autosuficiencia / masterclass (vivas)
- Interempresas · Ambiente saludable Eskimohaus (viva)
- NAN Arquitectura · 2 piezas (vivas)
- Revista de la Construcción · entrevista Papik Fisas (viva)
- Plataforma PEP · artículo Eskimohaus + Zehnder (viva, 4 snapshots Wayback)

**Asociaciones / academia:**
- APTIE · "El agujero invisible…" (viva)
- Elisava · mesa redonda Passivhaus con Eva Jordán + Papik Fisas + Joan Vilanova (viva)

**Lo que NO incluimos:**
- ❌ Los 3 placements **patrocinados** de 2026 (Cantabria Económica, Estartit TV, Majadahonda Magazin) — Google los detecta como pagados y desvalorizan la página
- ❌ Repeticiones agregadoras (Hechos de Hoy, Majadahonda Magazin reposting de la pieza del apagón) — usamos solo la fuente original (El Confidencial Digital)

### Estructura de página

```
HERO
  H1: "Han parlat de nosaltres" / "Han hablado de nosotros" / "Featured in"
  Subhead: una línea sobria — "30 años construyendo en Catalunya, contado por terceros"

FILTROS (chips horizontales, opcional pero recomendado)
  [Tot] [TV] [Premsa nacional] [Premsa local] [Sector] [Acadèmia]

GRID DE TARJETAS (1 tarjeta por pieza)
  Cada tarjeta:
   - Logo del medio (cuando existe; si no, nombre estilizado)
   - Fecha
   - Titular
   - 1 frase de contexto
   - Enlace EXTERNO (target=_blank, rel=noopener) a la pieza original
   - Si la pieza está perdida → enlace a reproducción interna o a Wayback Machine

CIERRE
  Bloque "¿Eres periodista?" → email de prensa + dossier descargable (kit pdf con logos, fotos, datos públicos)
```

### Reglas de copy

- **Citas literales entre comillas.** Si extraemos quote del artículo, citarlo textual.
- **Cero embellecimiento.** Si el medio dijo "una de las primeras", no escribir "la pionera".
- **Logos solo con permiso.** Verificar uso editorial; si no, usar nombre del medio en tipografía.
- **Idioma original.** La tarjeta puede estar en CA/ES/EN, pero el enlace abre la pieza en su idioma original — no traducimos al lector.

### Schema.org markup

```json
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "Premsa - PAPIK Group",
  "about": {"@type": "Organization", "name": "PAPIK Group"},
  "hasPart": [
    {
      "@type": "Article",
      "name": "...titular...",
      "publisher": {"@type": "Organization", "name": "TV3"},
      "url": "https://...",
      "datePublished": "2013-04-17"
    }
    // ... una entrada por pieza
  ]
}
```

### Internal linking

- Enlace desde footer ("Premsa") en todas las páginas
- Mención en `/empresa` ("Más de 20 medios han hablado de nosotros → Ver premsa")
- Cada `/projecte-*` que tenga cobertura mediática enlaza al item específico de premsa
- Redirect map: `/es/llega-la-ventilacion-inteligente-la-vanguardia` → `/es/premsa` (ya en `vercel.json`)

### Mantenimiento

- Política: añadir nueva entrada en las 24h posteriores a la publicación
- Revisar trimestralmente que las URLs externas siguen vivas — si caen, cambiar a Wayback

---

## Página 2 · `/certificacions` · `/es/certificaciones` · `/en/certifications`

### Objetivo estratégico

Centralizar todas las **certificaciones, premios y validaciones técnicas** verificables por terceros. Es **el complemento técnico de /premsa** — premsa son palabras, certificacions son sellos.

### Inventario inicial · contenido a incluir

> Todo lo que aparezca aquí debe poder verificarse en la web del organismo emisor. Si no se verifica, NO se publica.

**Certificaciones técnicas:**
- **Passivhaus Institut Darmstadt** — listado de obras certificadas con número de certificado (verificable en la base oficial PHI). Solo las que están confirmadas como Passivhaus *certificadas* (no "passivhaus-able" ni en proceso).
- **FSC** (Forest Stewardship Council) — número de cadena de custodia
- **PEFC** — si aplica
- Cualquier sello técnico de producto (CE, ETA) que sea PAPIK como empresa, no de proveedores

**Asociaciones (membresía vigente):**
- **PEP — Plataforma de Edificación Passivhaus** — verificar que la ficha en plataforma-pep.org/directorio-socios está activa y enlazarla
- **Gremi de Constructors** (si aplica)
- **Col·legi d'Aparelladors** (si aplica)
- **Green Building Council España** (si aplica — verificable)

**Premios:**
- "Excel·lència empresarial" El Economista (referenciado en /empresa actual) — **verificar enlace original** del premio. Si no se localiza el PDF/comunicado del premiador, NO publicar el sello.
- Cualquier otro premio listado en la web actual — auditar uno a uno

**Hitos verificables (no certificación pero pública):**
- "2ª casa Passivhaus certificada de Catalunya" — verificable en archivo PHI

**Lo que NO incluimos:**
- ❌ "Reconocida por su excelencia" sin entidad otorgante verificable
- ❌ Sellos genéricos sin número de registro (RGI, etc.)
- ❌ Certificaciones de proveedores (Zehnder, Loxone, etc.) — son de ellos, no de PAPIK
- ❌ Premios internos de feria sin documento público

### Estructura de página

```
HERO
  H1: "Certificacions i avals" / "Certificaciones y avales" / "Certifications & accreditations"
  Subhead: "Cada afirmació tècnica de PAPIK té un sello que la respalda" o equivalente

GRID DE BLOQUES (3 columnas en desktop)

BLOQUE 1 · Certificacions tècniques
  Logos + nombre + número de registro (cuando público) + enlace a verificación oficial

BLOQUE 2 · Asociaciones profesionales
  Logos + nombre + enlace a ficha en sitio del organismo

BLOQUE 3 · Premios y reconocimientos
  Año + nombre + entidad + enlace al comunicado oficial

PROYECTOS CERTIFICADOS PASSIVHAUS · listado
  Tabla simple:
  | Proyecto | Año | Clase | Nº certificado PHI | Enlace verificación |
  Solo entradas verificables. Si la verificación no carga, fila no se publica.

CTA · ¿Quieres ver una de nuestras casas certificadas?
  Link a /projectes filtrado o a /contacte
```

### Reglas de copy

- **Cada sello = un enlace de verificación al organismo emisor.** Si no enlaza, no se publica.
- **Cero adjetivos como "líder", "pionero", "el mejor".** Solo hechos verificables.
- **Año visible en cada premio.** Sin fecha, parece sospechoso.
- **No usar logos sin permiso explícito.** En su lugar, nombre tipográfico.

### Schema.org markup

```json
{
  "@context": "https://schema.org",
  "@type": "AboutPage",
  "name": "Certificacions - PAPIK Group",
  "mainEntity": {
    "@type": "Organization",
    "name": "PAPIK Group",
    "hasCredential": [
      {
        "@type": "EducationalOccupationalCredential",
        "credentialCategory": "certification",
        "name": "Passivhaus Institut",
        "recognizedBy": {"@type": "Organization", "name": "Passivhaus Institut Darmstadt"},
        "url": "https://passivehouse-database.org/..."
      }
      // ... una entrada por certificación
    ]
  }
}
```

### Internal linking

- Footer → "Certificacions"
- /empresa → "Más de 20 obras certificadas Passivhaus → Ver certificacions"
- /construccio → "Cada obra es certificable; mira nuestras certificaciones activas"
- /promocio → "Las viviendas que vendemos cumplen [X estándar certificado]"
- Cada `/projecte-*` certificado → link específico al item

### Validación pre-publicación · checklist privacidad + veracidad

- [ ] Cada sello tiene URL de verificación pública que abre y carga
- [ ] Cada nº de certificado es público (no interno)
- [ ] No se exhibe documentación que solo PAPIK tiene custodia (PDFs internos)
- [ ] Logos: licencia de uso comprobada
- [ ] Tabla de proyectos certificados: solo proyectos cuya certificación está en base PHI pública

---

## Tareas pendientes para que estas 2 páginas se publiquen el 1 de junio

| # | Tarea | Responsable | Fecha límite |
|---|---|---|---|
| 1 | Auditoría de URLs vivas de cada pieza de prensa (verificar 200 OK) | Equipo SEO / Claude | S2 (5 mayo) |
| 2 | Captura de Wayback Machine para piezas con URL caída | Claude | S2 |
| 3 | Verificación nº certificados PHI en base oficial passivehouse-database.org | PAPIK · oficina técnica | S2 |
| 4 | Confirmación premio El Economista (URL del comunicado) | PAPIK · comunicación | S2 |
| 5 | Revisión legal de uso de logos de medios | PAPIK · legal | S3 |
| 6 | Diseño visual del grid (mood: editorial sobrio) | Diseñador | S3 |
| 7 | Implementación + schema | Dev | S4 |
| 8 | QA pre-launch (cada link externo abre, schema valida en Rich Results Test) | Claude | S5 |
