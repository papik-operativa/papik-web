# Schemas JSON-LD · documentació d'ús

> Templates llests per copiar i pegar al `<head>` de cada pàgina. Vital per a que Google entengui la semàntica del nostre site i ens doni rich results.

## Llista de schemas i a quina pàgina aplica cadascun

| Schema | Quina pàgina | Inclou | Rich result que dóna |
|---|---|---|---|
| **01 · Organization homepage** | `/`, `/es/`, `/en/` (només homepage) | HomeAndConstructionBusiness + WebSite + ItemList serveis | Knowledge Panel + sitelinks + search box |
| **02 · Service** | `/construccio`, `/promocio`, `/rehabilitacio`, `/patrimonis` | Service amb provider, areaServed, hasOfferCatalog | Sitelinks + categories al SERP |
| **03 · LocalBusiness landing** | Cada `/zones/<municipi>` | LocalBusiness + GeoCircle | Map pack local + horaris al SERP |
| **04 · Article** | Cada `/article-*` | Article amb author, datePublished, image | Top stories + Discover feed |
| **05 · FAQPage** | Qualsevol pàgina amb FAQ | FAQPage amb mainEntity | FAQ expandible al SERP (gran impacte CTR) |
| **06 · BreadcrumbList** | Tota pàgina excepte homepage | BreadcrumbList | Breadcrumbs al SERP enlloc d'URL crua |
| **07 · RealEstateListing project** | Cada `/projecte-*` | CreativeWork + Place + additionalProperty | Rich snippet amb m², classe energètica, etc. |

## Combinacions per tipus de pàgina

Cada pàgina pot portar **múltiples schemas** combinats:

| Tipus pàgina | Schemas a posar |
|---|---|
| Homepage | 01 |
| Pàgina servei (Construcció, etc.) | 02 + 06 |
| Sub-pàgina (Comunitats) | 02 + 06 + 05 (si té FAQ) |
| Landing geogràfica | 03 + 06 + 05 (si té FAQ) |
| Article blog | 04 + 06 |
| Fitxa projecte | 07 + 06 |
| Pàgina amb FAQ (qualsevol) | + 05 |

## Format d'inserció al HTML

```html
<head>
  <!-- ... altres meta tags ... -->

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "...",
    ...
  }
  </script>

  <!-- Si hi ha múltiples schemas, un script per cadascun, o usar @graph al primer -->
</head>
```

## Reemplaçaments obligatoris abans de publicar

Cada template té camps `{{ ... }}` que cal omplir. Els camps a remplaçar globalment:

| Camp | Valor real |
|---|---|
| `{{LOGO_URL}}` | `https://papik.cat/img/logo-papik.svg` (verificar path) |
| `{{HERO_IMAGE_URL}}` | URL del hero image de cada pàgina (1200×630 ideal per OG) |
| `{{LATITUDE}} / {{LONGITUDE}}` | Coordenades de Carrer Sort 34, Sant Cugat (verificar amb cadastre) |
| `{{LINKEDIN_URL}}` | URL real del perfil LinkedIn de PAPIK |
| `{{INSTAGRAM_URL}}` | URL real del perfil Instagram |
| `{{YOUTUBE_URL}}` | URL real del canal YouTube |

## Validació · obligatòria abans de qualsevol deploy

Cada schema **ha de validar** a:

1. **Google Rich Results Test** → https://search.google.com/test/rich-results
2. **Schema.org validator** → https://validator.schema.org/

Si un schema no valida, NO es desplega — Google penalitza schema invalid.

## Connexió amb el graph (opcional · recomanat)

Per consolidar autoritat, totes les referències a "PAPIK Group" haurien d'apuntar al `@id` definit al schema d'Organization de la homepage:

```json
"provider": { "@id": "https://papik.cat/#org" }
```

Així Google entén que TOTES les pàgines del site són de la mateixa organització, no entitats disperses.

## Flux de treball recomanat per al dev en S3

1. Llegir aquest README
2. Per a cada pàgina, identificar quins schemas necessita (taula de combinacions)
3. Copiar el template JSON corresponent
4. Reemplaçar tots els `{{ ... }}` amb valors reals
5. Validar amb Rich Results Test
6. Inserir al `<head>` de la pàgina dins de `<script type="application/ld+json">`
7. Committejar i fer pull request
8. Pre-deploy: validar de nou (assegurar que cap canvi al copy ha trencat el JSON)
