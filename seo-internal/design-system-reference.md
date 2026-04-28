# PAPIK Group · Design System Reference (extracted from /public)

Extracted from `/public/css/{tokens,base,components,header,footer,cookie-banner}.css` and the canonical reference HTML pages (`projecte-k-iturbi.html`, `blog.html`, `qualitats.html`, `nosaltres.html`, `dashboard-cliente.html`).

This is the **source of truth** for class names and HTML patterns the generator must produce. CSS files are read-only.

---

## 1. Tokens (from `tokens.css`)

- **Font:** `TT Firs Neue` (light 300, regular 400, medium 500). Body `font-family: var(--ff-sans)`.
- **Brand greens:** `--green #002819`, `--green-light #56685E`, `--green-dark #0A1B12`.
- **Accent:** `--accent #95BBA5` plus soft variants `--accent-soft`, `--accent-soft-hover`.
- **Text:** `--text #002819` (dark on light), `--muted #56685E`, `--muted-light #9FA9A3`.
- **Surfaces:** `--bg-light` (faded green tint), `--footer-bg #07140D`.
- **Borders:** `--border`, `--border-soft`.
- **Radii:** xs/sm/md/lg/xl + `--r-pill 21px`, `--r-full 9999px`.
- **Easings:** `--ease-anim`, `--ease-img`, `--ease-bounce`. Buttons reference `--ease-paper` (also defined globally; use as-is).

---

## 2. Page boilerplate

Every page must:

```html
<!DOCTYPE html>
<html lang="ca|es|en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>...</title>
  <meta name="description" content="...">

  <link rel="canonical" href="...">
  <link rel="alternate" hreflang="ca" href="...">
  <link rel="alternate" hreflang="es" href="...">
  <link rel="alternate" hreflang="en" href="...">
  <link rel="alternate" hreflang="x-default" href="...">

  <link rel="stylesheet" href="css/tokens.css">
  <link rel="stylesheet" href="css/base.css">
  <link rel="stylesheet" href="css/header.css">
  <link rel="stylesheet" href="css/components.css">
  <link rel="stylesheet" href="css/footer.css">
  <link rel="stylesheet" href="/css/cookie-banner.css">

  <!-- OG / Twitter -->
  <!-- JSON-LD -->
</head>
<body>
  <!-- cookie banner snippet -->
  <!-- mobile-nav (optional, present in reference pages) -->
  <header class="header-top">…</header>
  <main id="main">…</main>
  <footer>…</footer>
  <script src="js/cookie-banner.js" defer></script>
  <script src="js/forms.js" defer></script>
</body>
</html>
```

Path prefixes: CA pages live at `/`. ES at `/es/`. EN at `/en/`. Sub-folders for landings (`/zones/`, `/es/zonas/`, `/en/areas/`) and comarcal hubs (`/comarques/`, `/es/comarcas/`, `/en/regions/`). Asset prefix is `css/` for top-level pages, `../css/` for `/es/`, `/en/`, and `../../css/` for sub-folders. Fixed `/css/cookie-banner.css` works from anywhere.

---

## 3. Header pattern (canonical, from blog.html / qualitats.html)

```html
<header class="header-top" id="headerTop">
  <div class="header-logo-layer"></div>
  <div class="header-logo">
    <div class="container">
      <div class="header-logo__content">
        <div class="menu-btn-wrapper" id="burgerBtn">
          <div class="menu-btn__burger"><span></span><span></span><span></span></div>
        </div>
        <div class="logo"><a href="index.html"><svg>…PAPIK logo…</svg></a></div>
      </div>
      <div class="lang">
        <select onchange="if(this.value)location=this.value">
          <option value="…CA url…" selected>CA</option>
          <option value="…ES url…">ES</option>
          <option value="…EN url…">EN</option>
        </select>
      </div>
    </div>
  </div>
</header>
```

The full submenu / sticky-bar block is feature-rich on `index.html` and `blog.html`; for the regenerated SEO pages we keep the simple header (logo + lang) which all reference pages share. Sticky submenus are nice-to-have and add JS dependencies (`header.js`); the simple header is sufficient and matches `dashboard-cliente.html` style.

---

## 4. Hero patterns

Three canonical hero variants exist:

### 4.1 Light hero (default, `.hero`)

```html
<section class="hero">
  <div class="container">
    <nav class="breadcrumb">
      <a href="index.html">Inici</a>
      <span class="sep">·</span>
      <span>Page name</span>
    </nav>
    <span class="hero__eyebrow">EYEBROW</span>
    <h1 class="hero__title" data-reveal-words>Title</h1>
    <p class="hero__subtitle">Subtitle / lead.</p>
    <div class="hero__actions">
      <a class="btn-accent" href="#">Primary CTA →</a>
      <a class="btn-outline" href="#">Secondary CTA →</a>
    </div>
  </div>
</section>
```

### 4.2 Dark hero (`.hero.hero--dark`)

Same skeleton with `class="hero hero--dark"`. Buttons swap to `.btn-white` (primary) and `.btn-outline` (which is auto-restyled white-on-dark via `.hero--dark .btn-outline`).

### 4.3 Article hero (`.article-hero`, from project pages)

```html
<section class="article-hero">
  <div class="container">
    <nav class="breadcrumb">…</nav>
    <span class="tag-pill">Category</span>
    <h1 class="article-hero__title">Title</h1>
    <p class="article-hero__meta"><time>2026</time></p>
  </div>
</section>
```

---

## 5. Body sections

### 5.1 Section wrappers

`section.section` (white bg) · `section.section--light` (faded bg) · `section.section--dark` (green bg, white text) · `section.section--tight` (tighter padding).

Each section has a `<div class="container">` wrapping content.

### 5.2 Section header

```html
<header class="section-header">
  <h2 class="section-header__title">Title</h2>
  <p class="section-header__lead">Lead</p>
</header>
```

### 5.3 Article body (long-form copy)

```html
<section class="article-body">
  <div class="container">
    <div class="article-body__content">
      <p>…</p><h2>…</h2><h3>…</h3><blockquote><p>…</p></blockquote>…
    </div>
  </div>
</section>
```

The article-body styles cap text at ~70ch and apply correct h2/h3/p/list/blockquote spacing.

---

## 6. Cards (used by homepage units, project lists, services, etc.)

```html
<div class="card-grid card-grid--2">  <!-- or default 3-col, --4 -->
  <article class="card card--icon">
    <span class="card__cat">EYEBROW</span>
    <h3 class="card__title">Title</h3>
    <p class="card__excerpt">Description text.</p>
    <a class="link-arrow" href="#">CTA →</a>
  </article>
  …
</div>
```

Variants: `.card--icon` (services / qualitats / homepage 4-up), `.card--stat` (KPIs).

For project-style cards: `.featured-card` for full-bleed featured items.

---

## 7. Buttons

Source: `components.css`. Site-wide unified system:

- `.btn-accent` / `.btn-dark` — primary green-filled (default CTA on light bg).
- `.btn-white` — primary white-on-dark (hero on dark).
- `.btn-outline` — secondary, auto-restyled in `.hero--dark` / `.section--dark`.
- `.link-arrow` — text-link CTA with underline-on-hover.
- `.nav-cta` — sticky-bar compact button.

All `<a class="btn-...">` and `<button class="btn-...">` work. Avoid inline styles; classes carry it all.

---

## 8. Lists / steps / phases

```html
<ol class="list">
  <li class="list-step">
    <span class="list-step__num">01</span>
    <div>
      <h3 class="list-step__title">Phase title</h3>
      <p class="list-step__text">Description.</p>
    </div>
  </li>
  …
</ol>
```

Two-column variants: add `.list--2col`, `.list-grid`, or `.faq-list--2col`.

---

## 9. Tables

`.article-body__content table` and a custom `.data-table` (defined inline previously) both work. Prefer `.data-table` (matches Eskimohaus tables in `qualitats.html`):

```html
<table class="data-table">
  <thead><tr><th>Header</th>…</tr></thead>
  <tbody><tr><td>Cell</td>…</tr></tbody>
</table>
```

---

## 10. Accordion (FAQ)

Native `<details>` element (no JS needed), styled minimally site-wide:

```html
<details class="faq-item">
  <summary>Question</summary>
  <div class="faq-item__body"><p>Answer.</p></div>
</details>
```

We add minimal CSS in the generator's `<style>` block since legacy doesn't define `.faq-item` explicitly.

---

## 11. Banner CTA / closing block

```html
<section class="block-cta section--dark">
  <div class="container">
    <p class="block-cta__label">EYEBROW</p>
    <h2 class="block-cta__title">Call to action title</h2>
    <p class="block-cta__sub">Optional subtitle</p>
    <a class="btn-white" href="#">CTA →</a>
  </div>
</section>
```

---

## 12. Forms (newsletter, contact)

Minimal styling; rely on `.btn-accent` for submit, `<input>` inherits `var(--ff-sans)` from base. For brand-consistent inputs:

```html
<form class="form" action="#" method="post">
  <label class="form-field">
    <span class="form-field__label">Email</span>
    <input class="form-field__input" type="email" required>
  </label>
  <label class="form-field form-field--check">
    <input type="checkbox" required>
    <span>Accepto la política de privacitat</span>
  </label>
  <button class="btn-accent" type="submit">Subscriure'm</button>
</form>
```

We add small inline CSS for `.form-field` since legacy `.css` doesn't include those classes universally (`forms.js` handles validation, no extra CSS dependencies).

---

## 13. Cross-links nav

```html
<nav class="cross-links">
  <p class="cross-links__label">Veure també</p>
  <ul>
    <li><a class="link-arrow" href="…">Title →</a></li>
    …
  </ul>
</nav>
```

---

## 14. Footer (canonical, from blog.html)

`.footer__content__info` flex row with `.footer-col` columns; `.footer__newsletter` panel; `.copyright` strip with legal links. Defined in `footer.css`. The generator must reproduce the structure with language-localised labels (already in the existing generator's `FOOTER_BY_LANG` dict — preserve).

---

## 15. Cookie banner snippet

`/public/cookie-banner.html` shows the canonical aside. Inject at start of `<body>`. JS at `/public/js/cookie-banner.js` handles localisation. Always include both:

```html
<aside id="papik-cc-banner" class="papik-cc" role="region" aria-label="Avís de galetes" hidden>…</aside>
…
<script src="js/cookie-banner.js" defer></script>
<script src="js/forms.js" defer></script>
```

---

## 16. Marker → component map (for the generator)

| v1.1 marker | Output HTML |
|---|---|
| `## BLOC HERO` + fenced block | `<section class="hero hero--dark">` with eyebrow / h1 / subhead / actions |
| `## BLOC N · TITLE` + fenced block | `<section class="section">` (or `--light` alternating) with eyebrow + h2 + subhead + body |
| `[Eyebrow]` line | `<span class="hero__eyebrow">` (in hero) or `.section-header__eyebrow` (in body) |
| `[H1]` line | `<h1 class="hero__title">` (only in hero) |
| `[H2]` / `[H2 centrat]` line | `<h2 class="section-header__title">` |
| `[H3]` line | `<h3>` |
| `[Subhead]`, `[Subhead · N línies]` | `<p class="hero__subtitle">` (hero) or `<p class="section-header__lead">` (body) |
| `[CTA primari]` text + `→` | `<a class="btn-accent">` or `.btn-white` on dark hero |
| `[CTA secundari]` | `<a class="btn-outline">` or `.link-arrow` |
| `[Botó]` / `[Botó alternatiu]` | `<button class="btn-accent">` |
| `[Form]` block (with `[Camp]`, `[Selector]`, `[Checkbox]`) | `<form class="form">` with `.form-field` rows |
| `[Card]` / `### Card N` blocks | `<article class="card card--icon">` inside `<div class="card-grid">` |
| `[Diagrama vertical]` numbered phases (01, 02…) | `<ol class="list list--2col">` with `<li class="list-step">` |
| `[Tabla]` + ASCII pipe-table | `<table class="data-table">` |
| `[Accordion]` + `P · question` / `R · answer` | `<details class="faq-item">` + `<summary>` |
| `[Banner destacat]` / `[Bloc destacat]` | `<section class="block-cta section--dark">` |
| `[Cross-links discrets]` | `<nav class="cross-links">` with `<ul>` |
| `[Frase de tancament]` | `<p class="closing-sentence">` (large light-weight quote) |
| `⚠ NOTA *`, leading `>` doc-comments, `## NOTES OPERATIVES`, `## Canvis respecte a v1`, `## Word count`, `## CHECKLIST PRE-PUBLICACIÓ`, `## NOTES PER AL DEV`, `## NOTAS PARA EL DEV`, `## NOTES FOR THE DEV`, etc. | strip |
| Code fences ` ``` ` (without `html` lang) | strip fences, parse inner content as wireframe markers |

---

## 17. Minimal extra CSS the generator emits inline (per page)

Only patterns not present in the design system get tiny inline rules:

- `.eyebrow` / `.hero__eyebrow--inline` — already covered by `.hero__eyebrow` and `.card__cat`.
- `.faq-item` — `<details>` styling (subtle border, brand greens).
- `.form-field` — input row spacing, brand-aligned border.
- `.cross-links`, `.closing-sentence` — small accents.
- `.phases-list` — number + content rhythm (uses `.list-step` if possible; else minimal accent).

These rules are intentionally tiny and additive; they reuse tokens (`--green`, `--bg-light`, `--border`, `--accent`).
