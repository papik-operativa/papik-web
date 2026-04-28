# Schema Validation Report

Generated: 2026-04-29

## Summary
- Total HTML files scanned: 256
- Files with at least 1 JSON-LD: 254
- Files with NO JSON-LD: 2
- Total JSON-LD blocks: 262
- Validation errors: 3
- Placeholder leaks: 0

### Files with NO JSON-LD
- `cookie-banner.html`
- `es/projectes.html`

## Errors by severity

### CRITICAL · placeholders in production
None.

### HIGH · invalid JSON syntax
None.

### MEDIUM · missing required fields
None.

### LOW · inconsistent inLanguage
- `en/index.html` (line 108): page lang `en`, schema inLanguage `['ca-ES', 'es-ES', 'en-US']`
- `es/index.html` (line 108): page lang `es`, schema inLanguage `['ca-ES', 'es-ES', 'en-US']`
- `index.html` (line 108): page lang `ca`, schema inLanguage `['ca-ES', 'es-ES', 'en-US']`

## Schema type distribution

| @type | Count |
|---|---|
| Service | 15 |
| Article | 54 |
| LocalBusiness | 51 |
| HomeAndConstructionBusiness | 3 |
| RealEstateListing | 108 |
| FAQPage | 9 |
| BreadcrumbList | 251 |
| CollectionPage | 6 |
| WebSite | 3 |
| WebPage | 3 |
| AboutPage | 2 |
| ItemList | 3 |

## Fixes applied

No automatic fixes were applied.

## Recommended fixes

1. Align `inLanguage` with `<html lang>` on 3 block(s) to avoid hreflang/Schema mismatch signals.
2. Add baseline JSON-LD (Organization or WebPage) to 2 page(s) currently shipping with no schema.
