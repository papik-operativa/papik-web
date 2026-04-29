# PAPIK Original Design System · Block Components

> Authoritative reference for the block-based components extracted from the
> original PAPIK design HTML files (all CSS was inline). Pair this document
> with `public/css/blocks.css`, which contains the production-ready rules.
>
> Source files (read-only):
> - `papik/index.html` (homepage, 1958 lines)
> - `papik/projecte-k-iturbi.html` (project page, 1750 lines)
> - `papik/article-pressupost-casa-passiva.html` (article)
> - `papik/construccio.html` (service page)
>
> Tokens consumed (declared in `public/css/tokens.css`):
> `--green`, `--green-light`, `--green-dark`, `--accent`, `--bg-light`,
> `--bg-section`, `--text`, `--muted`, `--muted-light`, `--border`,
> `--warm-1`, `--warm-2`, `--ff-sans`.

---

## Component: block-hero

**Purpose:** Cinematic full-bleed opener for any page (homepage, service,
landing, project). Holds an image + dark overlay + centered title block.

**HTML structure:**
```html
<section class="block-hero">
  <div class="block-hero__media">
    <div class="ph ph-hero"></div>
    <!-- or: <img src="{image}" alt="{alt}"> -->
  </div>
  <div class="block-hero__overlay"></div>
  <div class="block-hero__content">
    <p class="block-hero__eyebrow">{optional eyebrow}</p>
    <h1 class="block-hero__title">{Title<br>two lines}</h1>
    <p class="block-hero__sub">{optional sub-paragraph}</p>
    <div class="block-hero__cta">
      <a class="btn btn-primary" href="{href}">{cta}</a>
    </div>
  </div>
</section>
```

**Key styles:**
- Width 100vw, height 54.6875vw, capped to `100vh - 100px`.
- `.block-hero__overlay` defaults to `rgba(26,24,22,.42)`. Service variant
  uses `rgba(10,18,12,.5)` (darker, greener tint).
- Title is `clamp(38px, 5.2vw, 76px)`, weight 300, max-width 860px, white.
- `__eyebrow` is 11px uppercase, `letter-spacing .2em`,
  `rgba(255,255,255,.45)`.
- Mobile (<=900px): height drops to `106vw / max 500px`; title to 30px;
  at 520px title 26px.

**Used on:** homepage hero, every project page hero (with image swap),
every service page (`construccio`, `rehabilitacio`, `promocio`,
`patrimonis`, `comunitats`), landings, and the static `nosaltres` opener.

**Variants:**
- Plain: title + cta (homepage).
- Service: eyebrow + title + sub + cta (construccio).
- Project: image-only hero, no overlay text (overridden inline by project
  page `.project-hero` rules in `editorial.css`).

---

## Component: block-info-repeatable

**Purpose:** Alternating image/text rows used to introduce a service line.
Each row is a 60/40 split that flips on even children.

**HTML structure:**
```html
<section class="block-info-repeatable">
  <div class="block-info-repeatable__item bg-warm-1">
    <div class="item__info">
      <div class="item__info__text">
        <p class="tag">{eyebrow}</p>
        <h2 class="big-text">{Big headline<br>two lines}</h2>
        <p class="text">{paragraph}</p>
      </div>
      <a class="link-wrapper item__info__link" href="{href}">
        <span class="link_images">
          <div><div class="ph ph-warm-1"></div></div>
          <div><div class="ph ph-warm-2"></div></div>
          <div><div class="ph ph-warm-3"></div></div>
        </span>
        <span class="link-arrow">{label}</span>
      </a>
    </div>
    <div class="item__media">
      <div class="ph ph-warm-2"></div>
    </div>
  </div>
  <div class="block-info-repeatable__item bg-warm-2">…</div>
</section>
```

**Key styles:**
- Each row min-height `37.5vw`.
- `.item__info` 40% padded `4.6875vw`; `.item__media` 60%.
- `.big-text` `clamp(26px, 2.8vw, 40px)`, weight 300.
- `.tag` 11px upper, `letter-spacing .2em`, opacity .65.
- Even children flip via `nth-child(even)` `order` swaps.
- `link_images` is the 64x64 stacked-circles avatar trio with 2px
  `var(--warm-1)` ring.
- Mobile stacks vertical, text first, media 62vw tall.

**Used on:** homepage `Construcció` + `Rehabilitació` rows.

**Variants:** `bg-warm-1` (lighter), `bg-warm-2` (cooler grey).

---

## Component: block-services

**Purpose:** Two-column section that pairs a tall illustrative gif with an
interactive list of service divisions (PAPIK Construcció, Rehabilitació,
Promoció, Patrimonis, Comunitats…).

**HTML structure:**
```html
<section class="block-services block-margin">
  <div class="container">
    <div class="block-services__content">
      <div class="services__gif">
        <div class="ph ph-warm-3"></div>
      </div>
      <div class="services__list">
        <p class="label">{section label}</p>
        <ul>
          <li class="active"><span>Construcció</span><svg>…</svg></li>
          <li><span>Rehabilitació</span><svg>…</svg></li>
          <li><span>Promoció</span><svg>…</svg></li>
          <li><span>Patrimonis</span><svg>…</svg></li>
          <li><span>Comunitats</span><svg>…</svg></li>
        </ul>
      </div>
    </div>
  </div>
</section>
```

**Key styles:**
- Content padded `12.96875vw` from the left (intentional asymmetric inset).
- Gif `44.6875vw` wide, image `29.8vw` tall, `border-radius 8px`.
- List items `clamp(26px, 2.8vw, 40px)`, default `--muted-light`,
  hover/active `--green`. SVG arrow appears on hover/active.
- Mobile collapses to a column; gif full width, padding zeroed.

**Used on:** homepage Divisions section.

**Variants:** none.

---

## Component: block-categories

**Purpose:** 3-tile category grid with a centered archive button below.
Used as the secondary services entry point on the homepage.

**HTML structure:**
```html
<section class="block-categories block-margin" id="serveis">
  <div class="container">
    <h4 class="t42 center block-categories__title">Serveis</h4>
    <div class="categories-container">
      <a href="construccio.html" class="categories__item">
        <div class="ph ph-cat ph-warm-1"></div>
        <p class="categories__item__title center t24">Construcció</p>
      </a>
      <a href="promocio.html" class="categories__item">…</a>
      <a href="rehabilitacio.html" class="categories__item">…</a>
    </div>
    <a href="#contacte" class="archive-btn t16">Contacta'ns</a>
  </div>
</section>
```

**Key styles:**
- Section padded `80px 0` on `--bg-light`.
- Items 27.96vw wide; image 17.97vw tall, border-radius 8px.
- Hover dims to opacity .6.
- `.archive-btn` is a pill: `#E7E9E8`, 24px radius, hovers to black.
- Mobile <=900px: items 48% width; <=520px stack to 100%.

**Used on:** homepage Serveis section.

**Variants:** none.

---

## Component: block-columns

**Purpose:** 3-column repeater for project / showroom thumbnails with
title + sub-text.

**HTML structure:**
```html
<section class="block-columns block-margin" id="projectes">
  <div class="container">
    <h4 class="t42 center block-columns__title">Projectes recents</h4>
    <div class="block-columns__repeater">
      <a href="{href}" class="block-columns__item">
        <div class="item__media-col"><div class="ph ph-project1"></div></div>
        <p class="title">{Project name}</p>
        <p class="text">{Location · year · m²}</p>
      </a>
      <!-- repeat ×3 -->
    </div>
  </div>
</section>
```

**Key styles:**
- Grid `repeat(3, 1fr)` with 24px gap.
- Image 18vw tall, 8px radius. Hover dims media to opacity .82.
- Mobile collapses to 1 column, media 56vw.

**Used on:** homepage `Projectes recents`, sometimes the bottom of project
pages as related content.

**Variants:** none — but the `.cons-projects-grid` sibling on
`construccio.html` re-uses the same visual rhythm with a different class.

---

## Component: block-info

**Purpose:** Dark green "Nosaltres" CTA panel — large image circle on the
right, copy + button on the left.

**HTML structure:**
```html
<section class="block-info block-margin" id="nosaltres">
  <div class="container">
    <div class="block-info__content">
      <div class="block-info__text">
        <h4>{Headline}</h4>
        <p class="text">{paragraph}</p>
        <a class="btn" href="nosaltres.html">Coneix-nos</a>
      </div>
      <div class="block-info__image">
        <div class="ph ph-circle ph-green"></div>
      </div>
    </div>
  </div>
</section>
```

**Key styles:**
- Content `--green` background, 8px radius, 56px padding (right side
  flushes the image).
- Text 60% wide, padding `0 40px 0 56px`.
- Image circle 20vw square, capped 340px.
- Mobile stacks, padding `40px 5vw`, image becomes 50vw circle.

**Used on:** homepage Nosaltres section.

**Variants:** none in source. Sibling `block-cta` (dark green centered
strip) lives in `components.css`.

---

## Component: block-journal

**Purpose:** Editorial section that combines one large featured article and
a row of three smaller news cards.

**HTML structure:**
```html
<section class="block-journal block-margin">
  <div class="container">
    <div class="journal-bar">
      <h4 class="t42">Actualitat</h4>
      <a href="blog.html" class="link-arrow">Veure totes</a>
    </div>
    <article class="featured__item">
      <div class="featured__item__content">
        <a class="featured__item__img" href="{href}">
          <div class="ph ph-news1"></div>
        </a>
        <a class="featured__item__text" href="{href}">
          <div class="categories t16">{Category · subcategory}</div>
          <h3 class="title">{Featured title}</h3>
          <p class="desc">{deck}</p>
          <span class="date">{date}</span>
        </a>
      </div>
    </article>
  </div>
  <div class="other-articles">
    <div class="container">
      <div class="news-grid">
        <a class="news-card" href="{href}">
          <div class="news-card__img"><div class="ph ph-news2"></div></div>
          <div class="news-text">
            <p class="category">{cat}</p>
            <h4>{title}</h4>
          </div>
        </a>
        <!-- ×3 -->
      </div>
    </div>
  </div>
</section>
```

**Key styles:**
- Featured image 43vw × 27.5vw, 8px radius. Title 40px.
- News cards: image 14vw tall, 8px radius. Hover image to opacity .82,
  text to opacity .7.
- `.category` is the small uppercase 11px label with `letter-spacing .08em`.
- Mobile stacks featured; news cards become 2-up at 900px and 1-up at
  520px.

**Used on:** homepage `Actualitat`, sometimes bottom of project pages as
"related articles".

**Variants:** none.

---

## Component: block-process

**Purpose:** Numbered process / phases grid (8 phases for construccio,
parametric for other services). Two-column step list above 900px.

**HTML structure:**
```html
<section class="block-process">
  <div class="container">
    <div class="block-process__header">
      <span class="block-process__tag">El procés</span>
      <h2 class="block-process__title">Vuit fases<br>del projecte a les claus</h2>
      <p class="block-process__intro">{intro}</p>
    </div>
    <div class="process-steps">
      <div class="process-step">
        <span class="process-step__num">01</span>
        <div class="process-step__body">
          <h3 class="process-step__title">{step title}</h3>
          <p class="process-step__desc">{step description}</p>
        </div>
      </div>
      <!-- repeat -->
    </div>
  </div>
</section>
```

**Key styles:**
- Section `80px 0` on `--bg-light`.
- `process-steps` is a 2-column grid with hairline borders top + bottom,
  even children get a left border + left padding `5vw`.
- Numbers `clamp(36px, 3vw, 52px)` in `--border` color (architectural
  ghosted feel).
- Mobile stacks to 1 column, removes left border.

**Used on:** `construccio.html`, `rehabilitacio.html`, `promocio.html`.

**Variants:** none — but `.cons-svcs__grid`, `.cons-5p__grid`,
`.cons-why__grid` are sibling specialized grids that share the design DNA.

---

## Component: block-login

**Purpose:** Two side-by-side cards leading to user-portal and supplier-
portal (Usuaris area on homepage).

**HTML structure:**
```html
<section class="block-login block-margin">
  <div class="container">
    <div class="block-login__content">
      <a class="block-login__item" href="usuaris.html">
        <div>
          <h6>{Heading}</h6>
          <span class="link_button">Accedir <svg/></span>
        </div>
      </a>
      <a class="block-login__item" href="usuaris.html">…</a>
    </div>
  </div>
</section>
```

**Key styles:**
- Card `--bg-light` background with `--border` hairline.
- Hover changes border color to black.
- Min-height 130px, width 43vw.
- Mobile stacks to single column, full width.

**Used on:** homepage Usuaris area.

**Variants:** none.

---

## Component: block-cta-inv

**Purpose:** Inverted contact CTA — split panel with copy on the left and
an embedded form on the right, all on dark green.

**HTML structure:**
```html
<section class="block-cta-inv" id="contacte">
  <div class="container">
    <div class="block-cta-inv__inner">
      <div class="cta-left">
        <span class="tag">{eyebrow}</span>
        <h2>{Headline}</h2>
        <p>{paragraph}</p>
        <div class="cta-confidencial">
          <svg/> <span>{discretion line}</span>
        </div>
      </div>
      <div class="cta-right">
        <form class="pat-form">
          <label>Nom</label><input type="text">
          <label>Correu</label><input type="email">
          <label>Missatge</label><textarea></textarea>
          <button class="pat-form__submit">Envia</button>
        </form>
      </div>
    </div>
  </div>
</section>
```

**Key styles:**
- Inner `--green` panel, 8px radius, flex stretch.
- Left side flexes; right side fixed 42% with `rgba(255,255,255,.04)` tint.
- Form inputs use a transparent underline pattern with white .2 opacity.
- Mobile stacks; right panel becomes 100% width.

**Used on:** `construccio.html`, mirrored on every service page footer.

**Variants:** none.

---

## Component: bg-warm utilities

**Purpose:** Single-rule helpers to tint a section background with the
warm neutral palette tokens.

**HTML usage:**
```html
<div class="block-info-repeatable__item bg-warm-1">…</div>
<div class="block-info-repeatable__item bg-warm-2">…</div>
```

**CSS:**
```css
.bg-warm-1 { background: var(--warm-1); }
.bg-warm-2 { background: var(--warm-2); }
```

**Used on:** homepage info-repeatable rows.

---

## Component: archive-btn

**Purpose:** Tertiary pill button anchoring archive / contact links under
a grid section.

**HTML usage:**
```html
<a href="#contacte" class="archive-btn t16">Contacta'ns</a>
```

**Key styles:** `#E7E9E8` background, 24px radius, padding `10px 24px`,
hover swaps to black + white.

**Used on:** under `.block-categories` on homepage.

---

## Component: btn-up

**Purpose:** Floating "scroll to top" pill button at the very bottom of
each page. Note: declared in `components.css` already.

**HTML usage:**
```html
<button class="btn-up t14" onclick="window.scrollTo({top:0,behavior:'smooth'})">
  Tornar amunt
</button>
```

**Key styles:** muted bg, hovers to black. (See `components.css` line 103.)

**Used on:** every page above the footer.

---

## Component: btn-close-search

**Purpose:** Round dismiss button that appears in the header search drawer
when it's open.

**HTML usage:**
```html
<button class="btn-close-search" id="searchClose">
  <svg><!-- close icon --></svg>
</button>
```

**Key styles:** 40x40 round, `--bg-light` background, fades in only when
`.header-sticky.search-open` is set.

**Used on:** site-wide header.

---

## Component: block-margin (utility)

**Purpose:** Base vertical-rhythm helper that imposes a uniform 80px gap
(45px on tablet) below any block.

**HTML usage:**
```html
<section class="block-services block-margin">…</section>
```

**Used on:** any section that needs the standard inter-block gap.

---

## Inventory · components found by source page

Use this table to drive the static-site generator update — emit only the
blocks that match the page archetype.

| Component | homepage (`index.html`) | project page (`projecte-*`) | article (`article-*`) | service (`construccio.html`) |
|---|---|---|---|---|
| `block-hero` | ✓ | (replaced by project hero) | (replaced by `article-hero`) | ✓ |
| `block-info-repeatable` | ✓ | — | — | — |
| `big-text` | ✓ (inside info-repeat) | — | — | — |
| `block-services` | ✓ | — | — | — |
| `block-categories` | ✓ | — | — | — |
| `categories-container` / `categories__item` | ✓ | — | — | — |
| `archive-btn` | ✓ | — | — | — |
| `block-columns` | ✓ | (related projects) | — | (related projects) |
| `block-info` | ✓ | — | — | — |
| `block-journal` | ✓ | — | — | — |
| `featured__item` / `news-card` | ✓ | — | — | — |
| `block-login` | ✓ | — | — | — |
| `block-margin` (utility) | ✓ | ✓ | ✓ | ✓ |
| `bg-warm-1` / `bg-warm-2` | ✓ | — | — | — |
| `block-process` | — | — | — | ✓ |
| `block-cta-inv` | — | — | — | ✓ |
| `block-cta` (in components.css) | — | ✓ | ✓ | — |
| `btn-up` (in components.css) | ✓ | ✓ | ✓ | ✓ |
| `btn-close-search` | ✓ | ✓ | ✓ | ✓ |

**Total block components extracted: 18** (12 named blocks + 6 sub-components/utilities).

**File output:** `public/css/blocks.css` — production-ready, consumes
`tokens.css` variables only, contains responsive overrides at 900px and
520px breakpoints to mirror the original sources exactly.
