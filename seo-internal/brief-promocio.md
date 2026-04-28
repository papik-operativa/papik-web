# Content brief — `/promocio` (CA) · `/es/promocion` · `/en/development`

> INTERNAL DOCUMENT. Not to be published. Do not include any internal pricing data, real client names not already public on papik.cat, or operational metrics.

## Strategic context

**Promoció** is a NEW service line for the public-facing PAPIK site. PAPIK has been doing it internally for years but it has never had a dedicated public page. The current papik.cat does not host this offer.

### Modelo financiero · clave del posicionamiento

> **PAPIK financia, construye y vende. El comprador NO arriesga capital durante obra ni asume riesgo de proyecto.**

- **PAPIK compra el solar** con capital propio
- **PAPIK desarrolla el proyecto y construye** asumiendo riesgo técnico, de plazos y de coste
- **PAPIK vende la vivienda terminada** (o sobre plano con entrega cerrada) llave en mano
- **El comprador entra a vivir inmediatamente** una vez firmada la compra — sin gestión, sin obra, sin sorpresas

Esta es la **diferencia radical con el otro servicio (`/construccio`)**: en Construcció es el cliente quien tiene solar + capital y PAPIK es contratista. En Promoció es PAPIK quien tiene solar + capital y el cliente es comprador final.

### Tabla rápida de diferenciación interna (NO publicar tal cual)

| | Construcció | Promoció |
|---|---|---|
| Quién pone el solar | Cliente | PAPIK |
| Quién financia la obra | Cliente | PAPIK |
| Quién asume riesgo de plazos | Cliente | PAPIK |
| Quién asume riesgo de coste | Cliente | PAPIK |
| Personalización | Total | Limitada (ya diseñada) |
| Tiempo hasta vivir en ella | 12-18 meses obra | Inmediato (terminada) o entrega fija (sobre plano) |
| Perfil comprador | Cliente con solar y tiempo | Comprador busca producto terminado |

**Implication for SEO:** zero migration. This is a **greenfield page** — Google has no prior version. We declare it as new in the sitemap and submit fresh to Search Console post-launch.

## Target audience (in priority order)

1. **Familias con capital y sin tiempo / sin solar propio** — quieren casa nueva pasiva pero no quieren gestionar arquitecto + constructor + permisos + financiación. Compran "el resultado".
2. **Inversores particulares** — patrimonio personal, buscan vehículo inmobiliario eficiente con alquiler o reventa con plusvalía verde.
3. **Recién retornados a Catalunya** (catalanes en BCN urbano que buscan casa unifamiliar fuera) — perfil objetivo claro para Sant Cugat, Sant Quirze, Bellaterra, Maresme.
4. **Compradores extranjeros** (segmento EN) — versión inglesa apunta aquí: expats trabajando en Barcelona, segundas residencias.

## Keyword cabeza por idioma

| Idioma | Keyword principal | Secundarias |
|---|---|---|
| CA | autopromotor cases passives Catalunya | promoció immobiliària sostenible, casa passiva clau en mà, comprar casa Passivhaus nova |
| ES | autopromotor casas pasivas Cataluña | promoción inmobiliaria sostenible, casa pasiva llave en mano, comprar casa Passivhaus nueva |
| EN | passive house developer Catalonia | turnkey Passivhaus Spain, sustainable property development Barcelona |

## Tono y voz

- Tratamiento: **vostè / usted / formal you**
- Registro: profesional pero cercano, sin jerga técnica innecesaria. El lector NO es arquitecto, es comprador final.
- Diferenciador discursivo: "Lo construimos mejor de lo que lo construiríamos para vosotros, porque al principio era nuestro" → posicionar la garantía implícita del autopromotor frente al constructor por encargo.

## Estructura de página (wireframe)

```
1. HERO
   H1: "Casas pasivas para vivir desde el día 1" (CA: "Cases passives per viure des del primer dia")
   Subhead: una frase que sintetice "PAPIK como autopromotor: sin solar, sin gestión, llave en mano"
   CTA primario: "Ver promociones disponibles" (→ ancla interna o a /projectes filtrado)
   CTA secundario: "Hablar con un asesor"

2. POR QUÉ COMPRAR UNA PROMOCIÓ PAPIK · 3 razones
   Card 1: Sin riesgo de obra — el solar lo compramos nosotros, la obra la financiamos nosotros, los retrasos los absorbemos nosotros
   Card 2: Sin sorpresas — precio cerrado al firmar, calidades cerradas, plazo de entrega cerrado
   Card 3: Vivir desde el primer día — viviendas ya terminadas o con entrega fija; el día que firma, entra a vivir o tiene la fecha en el contrato

3. EL PROCESO · 5 pasos visuales (NO publicar plazos concretos en semanas/meses)
   1. Te enseñamos las promociones disponibles
   2. Eliges la que encaja con tu vida
   3. Visitas la obra (si está en construcción) o el solar (si aún no)
   4. Reserva + contrato
   5. Entrega de llaves con manual de uso de la casa

4. PROMOCIONES ACTIVAS · cards
   - Pull dinámico desde /projectes filtrando "tipo: promoció"
   - Cada card: foto, ubicación (municipio o comarca, NO dirección), m², dormitorios, año entrega previsto
   - NO publicar precio concreto. CTA: "Solicitar información"

5. DIFERENCIA VS COMPRAR USADO · tabla comparativa (educativa, no agresiva)
   | | Casa de obra usada | Promoció PAPIK |
   |---|---|---|
   | Eficiencia energética | C-D-E habitual | A / Passivhaus |
   | Costes mantenimiento años 1-10 | Altos (reformas) | Mínimos |
   | Garantía de obra | Vencida | 10 años decenal + sistema PAPIK |
   | Sorpresas técnicas | Probables | Cero |

6. UBICACIONES OBJETIVO (texto educativo, no operativo)
   "Donde construimos: Vallès Occidental, Maresme, Garraf y, puntualmente, Andorra y Baleares."
   Map estilizado o lista de comarcas. NO mencionar municipios concretos donde no haya promoción activa.

7. PREGUNTAS FRECUENTES (FAQPage schema)
   - ¿Puedo personalizar la casa que compro a PAPIK como promotor?
   - ¿Qué incluye exactamente "llave en mano"?
   - ¿Hay financiación verde / hipoteca pasiva disponible?
   - ¿Cuánto tarda en entregarse una promoció PAPIK? (respuesta: depende del estado de la obra; redirigir a asesor)
   - ¿Cómo me protege el contrato si hay retrasos?
   - ¿Qué diferencia hay entre vuestras promociones y comprar a otro autopromotor?

8. CIERRE · CTA fuerte
   "Reserve una visita a una de nuestras promociones activas"
   Link al formulario de contacto con campo "Estoy interesado en: [Promoció]"

9. CROSS-LINK al final · diferenciación clara con Construcció
   - "¿Ya tiene solar y quiere construir su casa a medida? Construcció es para usted → /construccio"
   - "¿Quiere comprar una casa ya terminada o con entrega cerrada? Sigue en Promoció"
   - "¿Quiere entender el sistema Eskimohaus? → [link blog pillar]"
```

**Nota crítica para el copywriter:** la página debe dejar claro **en los primeros 3 segundos de scroll** que aquí se compra producto terminado, NO se contrata obra. Cualquier ambigüedad provoca leads desalineados (clientes con solar que rellenan el formulario de Promoció pensando que es para construir).

## Reglas de copy (estrictas)

- **Cero precios concretos.** Si el lector pregunta "cuánto cuesta": "depende de la promoció — solicítenos información para la que le interese".
- **Cero plazos en semanas/meses.** Solo "calendario de entrega previsto" caso a caso.
- **Cero direcciones exactas.** Solo comarca o municipio.
- **Cero datos del configurador interno.** El configurador es para Construccio (cliente con solar), no para Promoció.
- **Cero comparativas con competidores nominales** (Arquima, Canexel, etc.).
- **Cero mención a márgenes, retornos esperados, ROI** en la versión pública. Eso es interno.
- **Cero números de obras totales / facturación.** Solo "30 años, +100 cases construïdes" — dato ya público.

## Schema.org markup

- `Service` schema con `provider: PAPIK Group, areaServed: Catalonia + Balearic Islands + Andorra`
- `FAQPage` para el bloque de preguntas frecuentes
- `BreadcrumbList`
- `Organization` (heredado de plantilla común)

## Internal linking (recibir + emitir)

Recibe enlaces desde:
- Homepage (sección "Què fem")
- Footer (servicios)
- /construccio (cross-link: "¿No tiene solar? Mire promoció")
- Pillar blog "construir casa Catalunya" (mención breve)

Emite enlaces a:
- /projectes filtrado por tipo "promoció"
- /pressupost (CTA si está pensando en construir con solar)
- /contacte
- 1-2 artículos blog relevantes ("Cómo elegir entre obra nueva y reforma" cuando exista)

## Validación pre-publicación

Antes de subir a producción el 1 de junio, esta página debe pasar el checklist de privacidad:

- [ ] No contiene cifras del análisis interno de presupuestos
- [ ] No nombra promociones por dirección exacta
- [ ] No revela operativa interna (proveedores, márgenes, plazos comprometidos)
- [ ] FAQ revisada por departamento comercial (las respuestas comprometen a la marca)
- [ ] Disclaimer legal al pie sobre el carácter orientativo de información de promociones

## Versiones idiomáticas · paridad de contenido

- CA es **canónico** — texto madre
- ES es **traducción literal con adaptaciones léxicas** (promoció → promoción, etc.)
- EN es **adaptación cultural**:
  - "autopromotor" no traduce 1:1 → usar "developer-builder" o "in-house developer"
  - Referencias a "Vallès / Maresme / Garraf" requieren paréntesis con (greater Barcelona area)
  - Mencionar EnerPHit junto a Passivhaus (el público anglo conoce ambos términos)

## Métrica de éxito (medir post-launch)

- Posición SERP "autopromotor casas pasivas Cataluña" > top 10 a los 90 días
- Conversión página → formulario contacto con campo "Promoció" > 1.5%
- Tiempo en página > 2:30 min (página densa, lectura genuina)
