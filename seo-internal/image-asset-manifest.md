# Image Asset Manifest

_Generated: 2026-04-29 — migration from `/codigopapik/papik/img/` and `/codigopapik/FOTOS/` into `/papik-web/public/img/`._

## OG images (`public/img/og/`)

Total: **52** files (1200×630, ready for `<meta property="og:image">`).

### Coverage breakdown

**Project pages (33)** — one OG per project page slug:
- `og-projecte-ampliacio-valldoreix.jpg`
- `og-projecte-arboc.jpg`
- `og-projecte-fornells.jpg`
- `og-projecte-k-alzina.jpg`
- `og-projecte-k-aragai.jpg`
- `og-projecte-k-argentona.jpg`
- `og-projecte-k-begues.jpg`
- `og-projecte-k-bellindret.jpg`
- `og-projecte-k-botigues.jpg`
- `og-projecte-k-calonge.jpg`
- `og-projecte-k-cim.jpg`
- `og-projecte-k-codines.jpg`
- `og-projecte-k-del-carril.jpg`
- `og-projecte-k-denbas.jpg`
- `og-projecte-k-gorgs.jpg`
- `og-projecte-k-hostalets.jpg`
- `og-projecte-k-igualada.jpg`
- `og-projecte-k-iturbi.jpg`
- `og-projecte-k-lamassa.jpg`
- `og-projecte-k-llavaneres.jpg`
- `og-projecte-k-malats.jpg`
- `og-projecte-k-marges.jpg`
- `og-projecte-k-maristany.jpg`
- `og-projecte-k-matadepera.jpg`
- `og-projecte-k-merla.jpg`
- `og-projecte-k-mogent.jpg`
- `og-projecte-k-orio.jpg`
- `og-projecte-k-premia.jpg`
- `og-projecte-k-vallor.jpg`
- `og-projecte-la-floresta.jpg`
- `og-projecte-moianes.jpg`
- `og-projecte-passivpalau.jpg`
- `og-projecte-passivrooms.jpg`
- `og-projecte-rehabilitacio-valldoreix.jpg`
- `og-projecte-remunta-sant-cugat.jpg`
- `og-projecte-remunta-valldoreix.jpg`

**Article / topic pages (11)**:
- `og-apagada-2025.jpg`
- `og-casa-montseny.jpg`
- `og-hipoteca-energetica.jpg`
- `og-innovacions-passivhaus.jpg`
- `og-materials-sostenibles.jpg`
- `og-petjada-ecologica.jpg`
- `og-pressupost-casa-passiva.jpg`
- `og-principis-passivhaus.jpg`
- `og-revolucio-fusta.jpg`
- `og-sostenibilitat-passivhaus.jpg`
- `og-tecnologies-passivhaus.jpg`
- `og-ventilacio-passivhaus.jpg`

**LinkedIn mockup variants (4)** — preview-only assets, prefix `_` excludes from OG defaults:
- `_linkedin-mockup-hipoteca.jpg`
- `_linkedin-mockup-montseny.jpg`
- `_linkedin-mockup-ventilacio.jpg`
- `_linkedin-preview-mockup.jpg`

> Note: brief estimated ~58 OG images; the actual source folder contained 52. All 52 copied; nothing dropped.

## Generic photos (`public/img/fotos/`)

Total: **8** placeholders (`photo-1.jpg` through `photo-8.jpg`). Used by the original design as hero/section background fallbacks. Other pre-existing files in this directory were left untouched.

## Project-specific photos (`public/img/projects/`)

Curated from 20 unsorted source files in `/codigopapik/FOTOS/`. Each project folder is keyed by the route slug used in `/projectes/[slug]`.

- **`projecte-k-mogent/`** — 2 photos (Llinars / Sant Sadurní shoot, 22-Oct-2024)
  - `hero.jpg` — `22 10 24_PAPIK_LLINARS_SANT SADURNÍ 24_044.jpg`
  - `exterior-01.jpg` — `22 10 24_PAPIK_LLINARS_SANT SADURNÍ 24_048 (1).jpg`
- **`projecte-k-argentona/`** — 2 photos (TIF → JPG converted)
  - `hero.jpg` — `ARGENTONA 003.tif`
  - `exterior-01.jpg` — `ARGENTONA 010 (2).tif`
- **`projecte-k-premia/`** — 4 photos (full coverage: hero / exterior / interior / detail)
  - `hero.jpg` — `CASA PREMIA 01 (4).jpg`
  - `exterior-01.jpg` — `CASA PREMIA 02 (5).jpg`
  - `interior-01.jpg` — `CASA PREMIA 13 (5).jpg`
  - `detail-01.jpg` — `CASA PREMIA 17 (6).jpg`
- **`projecte-k-llavaneres/`** — 1 photo (Sant Andreu de Llavaneres)
  - `hero.jpg` — `Sant_Andreu04.jpg`
- **`projecte-k-del-carril/`** — 2 photos (Sant Cugat — best guess between K-del-Carril, K-Aragai, remunta-sant-cugat, etc. Confirm before publish.)
  - `hero.jpg` — `Papik_Sant_cugat03.jpg`
  - `exterior-01.jpg` — `Papik_Sant_cugat08 (1).jpg`

**Subtotal:** 11 curated photos across 5 projects.

## Unmatched photos (`public/img/projects/_unmatched/`)

Total: **9** files awaiting manual project assignment.

- `hostalric-13.jpg` — Hostalric: no current project page matches the locality
- `hostalric-16.jpg` — same shoot as above
- `papik-group-004bv-mariana-castel.jpg` — professional shoot (© Mariana Castel); needs editorial-rights review before publishing
- `papik-group-005b-mariana-castel.jpg` — same shoot, same rights note
- `papik-group-006co.jpg` — © Papik Cases Passives, project unidentified from filename
- `unidentified-04.jpg` — original `04 (3).jpg`, no locality cue in filename
- `mg-3728.jpg` — generic camera filename `_MG_3728 Web (3).jpg`, no project match
- `mg-3787.jpg` — generic camera filename `_MG_3787 Web (7).jpg`, no project match
- `36291.jpg` — TIF → JPG converted; numeric-only filename, project unknown

## Format conversions

### TIF → JPG (sips, default quality)

- `ARGENTONA 003.tif` → `projecte-k-argentona/hero.jpg`
- `ARGENTONA 010 (2).tif` → `projecte-k-argentona/exterior-01.jpg`
- `36291.tif` → `_unmatched/36291.jpg`

### JPG → WebP

**Skipped — blocker.** The macOS-native `sips` on this system does not include the WebP encoder (`Error: Can't write format: org.webmproject.webp`). Neither `cwebp`, `magick/convert` (ImageMagick), nor `ffmpeg` are installed. To unblock, install one of:

```bash
brew install webp           # provides cwebp
# or
brew install imagemagick    # provides magick with webp support
```

Then re-run from `papik-web/public/img/projects/`:

```bash
find projecte-k-* -name '*.jpg' -exec sh -c 'cwebp -q 85 "$1" -o "${1%.jpg}.webp"' _ {} \;
```

## Recommendations for next pass

1. **Confirm the Sant Cugat assignment** — `Papik_Sant_cugat0{3,8}.jpg` was placed under `projecte-k-del-carril/` but could equally belong to `projecte-k-aragai`, `projecte-remunta-sant-cugat`, `projecte-rehabilitacio-valldoreix`, or `projecte-ampliacio-valldoreix`. Visual inspection by the design owner needed.
2. **Resolve unmatched photos** — review the 9 files in `_unmatched/` and either route to a project folder or cull. Hostalric specifically may motivate a new project page if there's an associated build.
3. **Image-rights gate** — the two `© Mariana Castel` files require editorial sign-off before going live. Tag the credit string into any future `<figure><figcaption>` rendering.
4. **Generate WebP** — once `cwebp`/ImageMagick is installed, run the snippet above for the 11 curated project JPGs (and re-run on any future additions). Targets a ~30-40 % byte-size reduction at q=85.
5. **Photo backfill** — current OG coverage spans 33 project slugs but only 5 projects have body photography. The remaining 28 project pages are still using OG-only imagery; commission/curate hero shots for them next.
6. **Optimize raw JPG sizes** — several originals are 3–7 MB (e.g. `photo-5.jpg` = 6.9 MB). Even pre-WebP, run a JPEG mozjpeg/`jpegoptim` pass to land them under ~500 KB before they hit the production bundle.
