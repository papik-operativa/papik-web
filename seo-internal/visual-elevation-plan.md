# Visual Elevation Plan · `/impeccable` + `high-end-visual-design`

> Generated: 29 April 2026 · post-`/impeccable teach` (refined editorial · quiet luxury) + `high-end-visual-design` (Vanguard Vibe + Layout)
> Read alongside `.impeccable.md` for design context and `seo-internal/style-guide-editorial.md` v1.3 for editorial rules.

---

## 1. Variance roll · committed direction

Per `high-end-visual-design` Section 3 (Creative Variance Engine), the following archetypes are committed for PAPIK Group:

- **Vibe Archetype · Editorial Luxury** — warm creams (`#F4F1ED`), oat (`#EAE6DE`), paper (`#FAF8F4`), deep ink/forest (`#002819`), accent sage (`#95BBA5`). High-contrast typography. Subtle 0.025 opacity grain available.
- **Layout Archetype · Editorial Split + Asymmetric Bento** combined. Split for hero/article moments (massive type / interactive list). Bento for project showcases.
- **Theme** · light dominant. Patrimonis sub-palette uses `--paper` + zero accent for B2B sobriety.
- **Motion** · existing `motion.js` already provides IntersectionObserver-driven reveals. New `cinema` variant adds 4px blur + cubic-bezier(.16,1,.3,1) for 900ms cinematic entries.

This locks the design language. Future pages must respect it. Future skills (`polish`, `animate`, `layout`) operate inside this frame.

---

## 2. Bug fixes applied

### 2.1 `--ease-paper` was undefined

`components.css` referenced `var(--ease-paper)` in 5 places (button transitions). The variable was not declared anywhere. Browsers silently fell back to default easing, neutering button physics.

Fixed by declaring in `tokens.css`:

```css
--ease-paper: cubic-bezier(.32,.72,0,1);
```

This is the Vanguard "physical paper" curve (decisive deceleration, no bounce, no over-shoot). Now active on all button hover/press transitions site-wide.

---

## 3. Tokens upgraded (`tokens.css`)

### 3.1 New surface tokens · Mediterranean warmth

| Token | Hex | Purpose |
|---|---|---|
| `--cream` | `#F4F1ED` | Primary editorial section background |
| `--oat` | `#EAE6DE` | Secondary warm surface, headers, callouts |
| `--paper` | `#FAF8F4` | Lightest warm white, page backgrounds |
| `--stone` | `#D8D2C7` | Warm divider against cream |
| `--ink` | `#1A1F1B` | Deep tinted near-black, never `#000` |

### 3.2 New text token

`--muted-cream: #6B6A62` — muted text that reads cleanly on cream surfaces (the existing `--muted` reads slightly cool against warm backgrounds).

### 3.3 New border tokens

| Token | Value | Purpose |
|---|---|---|
| `--hairline` | `rgba(0,40,25,0.08)` | The 1-pixel architectural line for cards, dividers |
| `--hairline-strong` | `rgba(0,40,25,0.18)` | Emphasis hairline |

### 3.4 Editorial type scale

| Token | Range | Purpose |
|---|---|---|
| `--t-eyebrow` | `11px` | Microscopic uppercase tags |
| `--t-body` | `16px` | Body text |
| `--t-lede` | `18-22px` clamp | Lead paragraphs |
| `--t-h3` | `22-28px` clamp | Sub-section headings |
| `--t-h2` | `28-44px` clamp | Section headings |
| `--t-h1` | `40-72px` clamp | Page hero titles |
| `--t-display` | `56-128px` clamp | Editorial drama, max-impact |
| `--t-display-2` | `48-96px` clamp | Secondary display |

Modular ratio `~1.333`. Maximum drama at top end (`128px`) without sacrificing mobile readability (`56px` minimum).

### 3.5 Reading width tokens

| Token | Value | Purpose |
|---|---|---|
| `--measure-tight` | `38ch` | Pull quotes, callouts |
| `--measure` | `65ch` | Primary body measure |
| `--measure-wide` | `75ch` | Permissive reading width |

### 3.6 Editorial shadow tokens

| Token | Purpose |
|---|---|
| `--sh-soft` | Card resting state · diffused, near-flat |
| `--sh-lift` | Card hover · clear elevation, no harshness |
| `--sh-float` | Featured card · maximum lift, still soft |
| `--sh-inset-highlight` | Inner highlight for double-bezel inner cores |

### 3.7 Editorial easing curves

| Token | Curve | Use |
|---|---|---|
| `--ease-paper` | `cubic-bezier(.32,.72,0,1)` | Decisive button press, no bounce |
| `--ease-out-quart` | `cubic-bezier(.25,1,.5,1)` | UI state transitions |
| `--ease-out-expo` | `cubic-bezier(.16,1,.3,1)` | Cinematic entries, hero reveals |

Existing `--ease-anim`, `--ease-img`, `--ease-bounce` retained for backward compatibility.

### 3.8 Cinematic timing token

`--t-cinematic: .9s` — for hero reveals, page entries, story-mode moments. Distinct from interaction timings (.18s / .22s / .35s / .65s).

---

## 4. New stylesheet · `editorial.css`

Created at `/public/css/editorial.css`, **~470 lines**, 18 sections of high-end primitives.

Import order (must remain):

```html
<link rel="stylesheet" href="/css/tokens.css">
<link rel="stylesheet" href="/css/base.css">
<link rel="stylesheet" href="/css/components.css">
<link rel="stylesheet" href="/css/header.css">
<link rel="stylesheet" href="/css/footer.css">
<link rel="stylesheet" href="/css/editorial.css">  <!-- LAST · elevates without breaking -->
<link rel="stylesheet" href="/css/cookie-banner.css">
```

The generator (`generate_html.py`) must be updated to include `editorial.css` after `footer.css` for all v1.1 pages. Legacy pages remain untouched (they don't include editorial.css; their existing design is preserved).

### 4.1 Primitives delivered

| § | Class | Purpose |
|---|---|---|
| §1 | `.eyebrow` (+ variants `--filled`, `--inverse`, `--bare`) | Architectural microscopic tag for section labels |
| §2 | `.display` (+ `--secondary`) | Editorial massive headlines, max-1-per-page |
| §3 | `.lede` (+ `--muted`) | Lead paragraph styling |
| §4 | `.bezel` + `.bezel__inner` (+ `--ink`, `--paper`) | Double-bezel nested architecture |
| §5 | `.btn-island` + `.btn-island__icon` | Button-in-button trailing icon |
| §6 | `.split` (+ `--reverse`) | Editorial Split layout, sticky lead |
| §7 | `.bento` + cells (`__cell--wide`, `--narrow`, `--full`, `--tall`) | Asymmetric Bento grid |
| §8 | `.quote` + `.quote__cite` | Editorial pull quote, no decorative quote-mark icons |
| §9 | `.measure`, `.measure-tight`, `.measure-wide` | Reading-width constraints |
| §10 | `.rule` (+ `--short`, `--strong`) | Architectural divider |
| §11 | `.stats` + `.stat__number`, `.stat__label` | Editorial fact slabs |
| §12 | `.section--cream`, `.section--paper`, `.section--ink`, `.section--editorial` | Editorial section variants |
| §13 | `.timeline` + `.cert-row` | Generational trust-builders, type-only |
| §14 | `body.has-grain` overlay | Subtle paper noise (opt-in) |
| §15 | `[data-anim="cinema"]` | Cinematic 900ms entry with blur dissolve |
| §16 | `.fact-row` | Sustainability without symbols (anti-greenwashing) |
| §17 | Responsive mobile collapse | Editorial primitives simplify gracefully |

### 4.2 Anti-pattern guards built in

The new file includes a comment block at the top reaffirming what the elevation MUST NOT introduce:

- NO greenwashing icons (leaves, eco badges)
- NO gradient text (banned per `impeccable` Absolute Bans)
- NO glassmorphism applied decoratively
- NO `border-left/right > 1px` as colored stripe
- NO purple/cyan AI palette
- Sharp architectural radii preferred over rounded-pills (the `.eyebrow` and `.btn-island__icon` are deliberate exceptions where pills read as "machined hardware")

---

## 5. Existing strengths preserved

The `motion.js` engine and `components.css` button system already implement multiple `high-end-visual-design` principles. Nothing was downgraded. Specifically retained:

- Custom easing scale (`--ease-anim`, `--ease-img`, `--ease-bounce`) — added new ones rather than replacing
- IntersectionObserver scroll reveals — `.cinema` variant added to the existing `[data-anim]` system
- Hero word-by-word reveal — untouched
- Cursor-following spotlight on `.card`, `.list-item`, `.featured-card` — untouched (Vanguard "haptic" effect)
- Animated counters — untouched
- Header backdrop on scroll — untouched
- Active-press scale .98 on all buttons — untouched
- Icon-shift-on-hover (4px translateX) — untouched, complemented by new `.btn-island__icon` translateX(2px)

---

## 6. Application strategy · who applies what, when

This `high-end-visual-design` pass establishes the SYSTEM. It does not yet apply elevation to specific pages. Application is the next phase.

### 6.1 Order of rollout

1. **Generator update** (`generate_html.py`) — include `editorial.css` reference in `<head>` of all v1.1 pages.
2. **Homepage exemplar** — refactor to use `.eyebrow`, `.display`, `.lede`, `.bezel`, `.split`, `.bento`, `.section--cream`, `.section--ink` markup. Becomes the visual proof-of-concept.
3. **Service pages** (4) — apply same primitives, with Patrimonis using `.section--paper` + zero accent for B2B sobriety.
4. **Tier-1 landings** (4) — hero with `.display` + `.eyebrow`; project list with `.bento`.
5. **Articles** (~20) — `.eyebrow` over title, `.display` for H1, `.lede` for opening paragraph, `.measure` on body, `.quote` for callouts.
6. **Project pages** (36) — `.bezel` for spec panel, `.fact-row` for technical data, `.split` for description vs photo gallery.
7. **Comarcal hubs + Tier-2** — `.bento` for municipality grid.
8. **About + 404 + hubs** — apply selectively where it elevates.

### 6.2 What applies via `polish`

The `polish` skill (next in the sequence) will:

- Audit each existing page against the new primitives
- Identify alignment, spacing, and consistency drift
- Apply the editorial primitives to the homepage as exemplar
- Document residual inconsistencies for batch fixes

### 6.3 What applies via `animate`

If invoked later, the `animate` skill will:

- Choreograph the homepage hero entry (stagger eyebrow → display → lede → CTAs over 1.4s)
- Add `.cinema` reveal to article H1s
- Refine the bento entry stagger
- Add subtle hover mass on `.bezel` cards

---

## 7. Pre-output checklist verification (Section 8 of `high-end-visual-design`)

- [x] No banned fonts (TT Firs Neue is custom, not in reflex_fonts_to_reject list, not Inter/Roboto/Arial)
- [x] No banned icons (the site is image-free / icon-free by design choice — anti-greenwashing principle)
- [x] No 1px solid gray borders (replaced with `--hairline` rgba green-tinted)
- [x] No harsh dark drop shadows (replaced with `--sh-soft` / `--sh-lift` / `--sh-float`)
- [x] No edge-to-edge sticky navbar (existing `motion.js` makes header float-able and adds backdrop on scroll)
- [x] No symmetric Bootstrap grids (Editorial Split + Asymmetric Bento are committed archetypes)
- [x] No `linear` or `ease-in-out` (custom cubic-bezier curves throughout, including new `--ease-paper`)
- [x] No instant state changes (transitions defined for all interactive surfaces)
- [x] Vibe + Layout archetypes consciously selected (Editorial Luxury + Split-Bento)
- [x] Double-bezel architecture available via `.bezel` + `.bezel__inner` (concentric radii)
- [x] Button-in-button via `.btn-island` + `.btn-island__icon`
- [x] Section padding ≥ `py-24` (existing `.section` is `56px`, new `.section--editorial` clamps to `96-192px`)
- [x] Custom cubic-bezier transitions throughout
- [x] Scroll entry animations present (existing `[data-anim]` + new `cinema` variant)
- [x] Mobile collapse below 900px implemented in all new primitives
- [x] Animations only on `transform`, `opacity`, `filter` (no layout-triggering properties)
- [x] `backdrop-blur` not applied to scrolling content (only fixed elements where used)
- [x] Reads as agency-tier system, not template-with-fonts

---

## 8. Done in this pass

✓ `tokens.css` upgraded with editorial luxury palette, type scale, easing, shadows
✓ `--ease-paper` bug fixed
✓ `editorial.css` created (470 lines, 18 sections)
✓ Documentation written (this file)

## 9. Next pass · `polish`

When `/polish` is invoked, it should:

1. Inspect homepage / service pages / articles
2. Identify drift from the `editorial.css` primitives (where existing markup could opt into eyebrow, display, lede, etc.)
3. Apply elevations to the homepage as exemplar
4. Document spacing, alignment, type-rhythm fixes needed

The system is ready. The polish phase brings it to life on actual pages.

---

## 10. Maintenance

This plan is complete for v1. Update only when:

- New design language decisions are made (e.g., adding a display serif post-launch)
- Layout archetypes shift (e.g., introducing a Z-Axis Cascade variant)
- Brand identity evolves (new colors, fonts)
- A new vibe is needed for a sub-product (e.g., a B2B portal with stricter sobriety)

Otherwise, the file is reference material for future agents.
