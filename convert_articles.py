#!/usr/bin/env python3
"""
Convert all PAPIK articles from old single-column layout to new
sidebar+content layout (adapted from Integrated Biosciences design).
"""
import re
import os
import urllib.parse

PAPIK_DIR = os.path.join(os.path.dirname(__file__), 'papik')

# Articles to convert (exclude the template itself)
ARTICLES = [
    'article-apagada-2025.html',
    'article-casa-montseny.html',
    'article-hipoteca-energetica.html',
    'article-innovacions-passivhaus.html',
    'article-materials-sostenibles.html',
    'article-nota-premsa-papik-ksandal.html',
    'article-nota-premsa-papik-ponsa.html',
    'article-petjada-ecologica.html',
    'article-pressupost-casa-passiva.html',
    'article-principis-passivhaus.html',
    'article-revolucio-fusta.html',
    'article-sostenibilitat-passivhaus.html',
    'article-tecnologies-passivhaus.html',
    'article-ventilacio-passivhaus.html',
]

def extract_between(html, start_marker, end_marker):
    """Extract content between two markers."""
    idx_start = html.find(start_marker)
    if idx_start == -1:
        return None
    idx_start += len(start_marker)
    idx_end = html.find(end_marker, idx_start)
    if idx_end == -1:
        return None
    return html[idx_start:idx_end]

def extract_tag_content(html, pattern):
    """Extract content matching a regex pattern."""
    m = re.search(pattern, html, re.DOTALL)
    return m.group(1).strip() if m else None

def extract_article_data(filepath):
    """Extract all relevant data from an old article file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    data = {}

    # Title
    data['title_tag'] = extract_tag_content(html, r'<title>(.*?)</title>')
    data['h1'] = extract_tag_content(html, r'<h1 class="article-hero__title">(.*?)</h1>')

    # Meta description
    data['meta_desc'] = extract_tag_content(html, r'<meta name="description" content="(.*?)"')

    # OG tags
    data['og_image'] = extract_tag_content(html, r'<meta property="og:image" content="(.*?)"')
    data['og_url'] = extract_tag_content(html, r'<meta property="og:url" content="(.*?)"')

    # Twitter tags
    data['twitter_desc'] = extract_tag_content(html, r'<meta name="twitter:description" content="(.*?)"')

    # Category
    data['category'] = extract_tag_content(html, r'<span class="article-hero__cat">(.*?)</span>')

    # Date
    data['date'] = extract_tag_content(html, r'<time>(.*?)</time>')

    # Reading time
    reading_match = re.search(r'<span>(\d+ min lectura)</span>', html)
    data['reading_time'] = reading_match.group(1) if reading_match else '5 min lectura'

    # Breadcrumb text
    breadcrumb_match = re.search(r'<span class="sep">&rsaquo;</span>\s*<span>(.*?)</span>\s*</nav>', html, re.DOTALL)
    data['breadcrumb_text'] = breadcrumb_match.group(1).strip() if breadcrumb_match else data['h1'][:50] if data['h1'] else ''

    # Cover image style
    cover_match = re.search(r'<div class="article-cover__img"[^>]*style="(.*?)"', html)
    data['cover_style'] = cover_match.group(1) if cover_match else "background:linear-gradient(160deg,#002819 0%,#95BBA5 100%);"

    # Article body content - extract between the content div tags
    body_match = re.search(
        r'<div class="article-body__content">\s*(.*?)\s*(?:<a href="blog\.html" class="article-back">|</div>\s*</div>\s*</section>\s*(?:<!-- RELATED|<section class="related))',
        html, re.DOTALL
    )
    if body_match:
        body_content = body_match.group(1).strip()
        # Remove trailing article-back link if present
        body_content = re.sub(r'\s*<a href="blog\.html" class="article-back">.*?</a>\s*$', '', body_content, flags=re.DOTALL)
        data['body_html'] = body_content
    else:
        data['body_html'] = '<p>Content not found</p>'

    # Related articles section
    related_match = re.search(
        r'(<div class="blog-grid">.*?</div>\s*</div>\s*</div>)\s*</section>\s*(?:<!-- CTA|<section class="block-cta")',
        html, re.DOTALL
    )
    data['related_html'] = related_match.group(1).strip() if related_match else ''

    # Check if it's a press release (nota de premsa)
    data['is_press_release'] = 'nota-premsa' in filepath or (data['category'] and 'premsa' in data['category'].lower())

    # Check for press contact block
    data['has_press_contact'] = 'Contacte de premsa' in html or 'contacte de premsa' in html.lower()

    # Filename
    data['filename'] = os.path.basename(filepath)

    return data

def generate_share_url(base_url, title):
    """Generate share URLs."""
    encoded_url = urllib.parse.quote(base_url, safe='')
    encoded_title = urllib.parse.quote(title, safe='')
    return {
        'linkedin': f"https://www.linkedin.com/shareArticle?url={encoded_url}&title={encoded_title}",
        'x': f"https://x.com/share?url={encoded_url}&text={encoded_title}",
    }

def build_new_article(data):
    """Build the new article HTML using the post-detail template structure."""

    filename = data['filename']
    title = data['h1'] or 'Article'
    title_tag = data['title_tag'] or f"{title} | PAPIK"
    meta_desc = data['meta_desc'] or ''
    og_image = data['og_image'] or f"https://www.papik.cat/img/og/og-{filename.replace('article-', '').replace('.html', '')}.jpg"
    category = data['category'] or 'Blog'
    date = data['date'] or ''
    reading_time = data['reading_time'] or '5 min lectura'
    cover_style = data['cover_style']
    body_html = data['body_html']
    related_html = data['related_html']
    breadcrumb = data['breadcrumb_text']
    base_url = f"https://www.papik.cat/{filename}"

    share_urls = generate_share_url(base_url, title)

    # For K-SANDAL, use the real image
    if 'ksandal' in filename:
        cover_style = "background:url('img/foto-ksandal.jpg') center/cover no-repeat;"

    # Determine author based on type
    author_name = "PAPIK Group"
    author_role = "Autor"

    # Build related section
    related_section = ''
    if related_html:
        related_section = f'''
<!-- ARTICLES RELACIONATS -->
<section class="related-section">
  <div class="container">
    <div class="related-section__header">
      <h2 class="related-section__title">Articles relacionats</h2>
      <a href="blog.html" class="related-section__link" aria-label="Veure tots els articles">
        Veure tots
        <svg width="12" height="10" viewBox="0 0 12.447 10.89"><path d="M9.335,3.11V4.666H0V6.222H9.335V7.778H7.78V9.334H6.224V10.89H7.78V9.334H9.335V7.778h1.556V6.222h1.556V4.666H10.891V3.11Zm-1.556,0H9.336V1.554H7.78ZM6.224,1.554H7.78V0H6.224Z" fill="currentColor"/></svg>
      </a>
    </div>
    {related_html}
  </div>
</section>'''

    # Check if body already has a press contact block - if so don't add share at end
    has_existing_press = 'Contacte de premsa' in body_html or 'contacte de premsa' in body_html.lower()

    # Bottom share section
    bottom_share = f'''
        <!-- BOTTOM SHARE -->
        <div class="article-share-bottom">
          <span class="article-share-bottom__label">Compartir:</span>
          <div class="article-share-bottom__links">
            <a href="{share_urls['linkedin']}" class="share-btn-inline" target="_blank" rel="noopener noreferrer" aria-label="Compartir a LinkedIn">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" fill="currentColor"/></svg>
              LinkedIn
            </a>
            <a href="{share_urls['x']}" class="share-btn-inline" target="_blank" rel="noopener noreferrer" aria-label="Compartir a X">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" fill="currentColor"/></svg>
              X
            </a>
            <button class="share-btn-inline js-copy-url" aria-label="Copiar enllaç" data-url="{base_url}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <span class="copy-label">Copiar</span>
            </button>
          </div>
        </div>'''

    # Read the template
    template_path = os.path.join(PAPIK_DIR, 'article-post-detail.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Extract just the <style> block from template (everything between first <style> after fonts and </style> before </head>)
    # We'll use the template's CSS
    style_start = template.find('  <style>\n    /* ═══════════════════════════════════\n       VARIABLES & RESET')
    style_end = template.find('</head>')
    template_styles = template[style_start:style_end].strip()

    # Build the full HTML
    new_html = f'''<!DOCTYPE html>
<html lang="ca">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_tag}</title>
  <meta name="description" content="{meta_desc}">
  <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title_tag}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:image" content="{og_image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:url" content="{base_url}">
  <meta property="og:site_name" content="PAPIK">
  <meta property="og:locale" content="ca_ES">
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title_tag}">
  <meta name="twitter:description" content="{meta_desc}">
  <meta name="twitter:image" content="{og_image}">
  <!-- Canonical -->
  <link rel="canonical" href="{base_url}">
  <!-- Structured Data -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "WebSite",
        "@id": "https://www.papik.cat/#website",
        "url": "https://www.papik.cat/",
        "name": "PAPIK",
        "description": "Construcció sostenible i eficiència energètica",
        "inLanguage": "ca"
      }},
      {{
        "@type": "Article",
        "@id": "{base_url}#article",
        "headline": "{title}",
        "description": "{meta_desc}",
        "author": {{ "@type": "Organization", "name": "PAPIK Group" }},
        "publisher": {{ "@type": "Organization", "name": "PAPIK Group", "url": "https://www.papik.cat/" }},
        "mainEntityOfPage": "{base_url}",
        "inLanguage": "ca"
      }},
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{ "@type": "ListItem", "position": 1, "item": "https://www.papik.cat/", "name": "Inici" }},
          {{ "@type": "ListItem", "position": 2, "item": "https://www.papik.cat/blog.html", "name": "Blog" }},
          {{ "@type": "ListItem", "position": 3, "name": "{title}" }}
        ]
      }}
    ]
  }}
  </script>
  <!-- Fonts -->
  <style>
    @font-face {{
      font-family: 'TT Firs Neue';
      src: url('fonts/TT_Firs_Neue_Light.woff2') format('woff2'),
           url('fonts/TT_Firs_Neue_Light.woff') format('woff');
      font-weight: 300;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'TT Firs Neue';
      src: url('fonts/TT_Firs_Neue_Regular.woff2') format('woff2'),
           url('fonts/TT_Firs_Neue_Regular.woff') format('woff');
      font-weight: 400;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: 'TT Firs Neue';
      src: url('fonts/TT_Firs_Neue_Medium.woff2') format('woff2'),
           url('fonts/TT_Firs_Neue_Medium.woff') format('woff');
      font-weight: 500;
      font-style: normal;
      font-display: swap;
    }}
  </style>

  {template_styles}
</head>
<body>

<!-- MOBILE NAV OVERLAY -->
<nav class="mobile-nav" id="mobileNav">
  <div class="mobile-nav__header">
    <div class="logo">
      <a href="index.html" aria-label="PAPIK — Inici">
        <svg width="80" height="20" viewBox="0 0 80 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0 0.5H4.5C8.09 0.5 10.5 2.91 10.5 6.5C10.5 10.09 8.09 12.5 4.5 12.5H2.8V19.5H0V0.5ZM4.3 10.1C6.5 10.1 7.7 8.7 7.7 6.5C7.7 4.3 6.5 2.9 4.3 2.9H2.8V10.1H4.3Z" fill="#002819"/>
          <path d="M16 0.5H20.28L25.48 19.5H22.58L21.38 14.8H14.88L13.68 19.5H10.78L16 0.5ZM15.58 12.4H20.68L18.18 2.9H18.08L15.58 12.4Z" fill="#002819"/>
          <path d="M27 0.5H31.5C35.09 0.5 37.5 2.91 37.5 6.5C37.5 10.09 35.09 12.5 31.5 12.5H29.8V19.5H27V0.5ZM31.3 10.1C33.5 10.1 34.7 8.7 34.7 6.5C34.7 4.3 33.5 2.9 31.3 2.9H29.8V10.1H31.3Z" fill="#002819"/>
          <path d="M39 0.5H41.8V19.5H39V0.5Z" fill="#002819"/>
          <path d="M44 0.5H46.8V9L53.1 0.5H56.4L50.2 8.6L57 19.5H53.6L48.2 10.5L46.8 12.2V19.5H44V0.5Z" fill="#002819"/>
        </svg>
      </a>
    </div>
    <button class="mobile-nav__close" id="mobileNavClose" aria-label="Tancar menú">&#10005;</button>
  </div>
  <ul>
    <li><a href="construccio.html">Construcció Residencial</a></li>
    <li><a href="promocio.html">Promoció Immobiliària</a></li>
    <li><a href="rehabilitacio.html">Rehabilitació Energètica</a></li>
    <li class="sub-title">Descobreix</li>
    <li><a href="nosaltres.html">Qui som</a></li>
    <li><a href="blog.html">Blog</a></li>
    <li><a href="index.html#contacte">Contacte</a></li>
    <li><a href="pressupost.html">Pressupost Online</a></li>
  </ul>
</nav>
<div class="fade-bg" id="fadeBg"></div>

<!-- HEADER -->
<div class="header-logo-layer"></div>
<header class="header-top" id="headerTop">
  <div class="header-logo">
    <div class="container">
      <div class="header-logo__content">
        <div class="menu-btn-wrapper" id="burgerBtn">
          <div class="menu-btn__burger"><span></span><span></span><span></span></div>
        </div>
        <div class="logo">
          <a href="index.html" aria-label="PAPIK — Inici">
            <svg width="80" height="20" viewBox="0 0 80 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M0 0.5H4.5C8.09 0.5 10.5 2.91 10.5 6.5C10.5 10.09 8.09 12.5 4.5 12.5H2.8V19.5H0V0.5ZM4.3 10.1C6.5 10.1 7.7 8.7 7.7 6.5C7.7 4.3 6.5 2.9 4.3 2.9H2.8V10.1H4.3Z" fill="#002819"/>
              <path d="M16 0.5H20.28L25.48 19.5H22.58L21.38 14.8H14.88L13.68 19.5H10.78L16 0.5ZM15.58 12.4H20.68L18.18 2.9H18.08L15.58 12.4Z" fill="#002819"/>
              <path d="M27 0.5H31.5C35.09 0.5 37.5 2.91 37.5 6.5C37.5 10.09 35.09 12.5 31.5 12.5H29.8V19.5H27V0.5ZM31.3 10.1C33.5 10.1 34.7 8.7 34.7 6.5C34.7 4.3 33.5 2.9 31.3 2.9H29.8V10.1H31.3Z" fill="#002819"/>
              <path d="M39 0.5H41.8V19.5H39V0.5Z" fill="#002819"/>
              <path d="M44 0.5H46.8V9L53.1 0.5H56.4L50.2 8.6L57 19.5H53.6L48.2 10.5L46.8 12.2V19.5H44V0.5Z" fill="#002819"/>
            </svg>
          </a>
        </div>
      </div>
      <div class="lang">
        <select onchange="location=this.value" aria-label="Idioma">
          <option value="{filename}" selected>CA</option>
          <option value="es/{filename}">ES</option>
        </select>
      </div>
    </div>
  </div>
</header>

<!-- STICKY NAV -->
<section class="header-sticky" id="headerSticky">
  <div class="header-sticky__bar">
    <div class="container">
      <div class="header-sticky__content">
        <nav class="menu" aria-label="Navegació principal">
          <ul>
            <li><a href="construccio.html" class="t14">Construcció</a></li>
            <li><a href="promocio.html" class="t14">Promoció</a></li>
            <li><a href="rehabilitacio.html" class="t14">Rehabilitació</a></li>
            <li><a href="nosaltres.html" class="t14">Qui som</a></li>
            <li><a href="blog.html" class="t14 active">Blog</a></li>
          </ul>
        </nav>
        <nav class="menu-right" aria-label="Accions">
          <ul>
            <li><a href="pressupost.html" class="nav-cta t12">
              <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M8 0v16M0 8h16" stroke="#fff" stroke-width="1.5"/></svg>
              Pressupost
            </a></li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</section>

<!-- ARTICLE HERO -->
<section class="article-hero">
  <div class="container">
    <nav class="breadcrumb" aria-label="Fil d'Ariadna">
      <a href="index.html">Inici</a>
      <span class="sep" aria-hidden="true">&rsaquo;</span>
      <a href="blog.html">Blog</a>
      <span class="sep" aria-hidden="true">&rsaquo;</span>
      <span>{breadcrumb}</span>
    </nav>
    <span class="article-hero__cat">{category}</span>
    <h1 class="article-hero__title">{title}</h1>
    <div class="article-hero__meta">
      <time>{date}</time>
      <span class="sep" aria-hidden="true">&middot;</span>
      <span>{reading_time}</span>
    </div>
  </div>
</section>

<!-- COVER -->
<div class="article-cover">
  <div class="article-cover__img" role="img" aria-label="Imatge de portada: {title}" style="{cover_style}"></div>
</div>

<!-- ARTICLE BODY -->
<section class="article-body">
  <div class="container">
    <div class="article-body__layout">

      <!-- SIDEBAR -->
      <aside class="article-sidebar">
        <div class="article-sidebar__inner">
          <a href="blog.html" class="sidebar__back" aria-label="Tornar al Blog">
            <svg width="12" height="10" viewBox="0 0 12.447 10.89"><path d="M9.335,3.11V4.666H0V6.222H9.335V7.778H7.78V9.334H6.224V10.89H7.78V9.334H9.335V7.778h1.556V6.222h1.556V4.666H10.891V3.11Zm-1.556,0H9.336V1.554H7.78ZM6.224,1.554H7.78V0H6.224Z" fill="currentColor"/></svg>
            Tornar al Blog
          </a>
          <div class="sidebar__author">
            <div class="sidebar__author-name">{author_name}</div>
            <div class="sidebar__author-role">{author_role}</div>
          </div>
          <div class="sidebar__share-label">COMPARTIR:</div>
          <div class="sidebar__share-links">
            <a href="{share_urls['linkedin']}" class="share-btn" target="_blank" rel="noopener noreferrer" aria-label="Compartir a LinkedIn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" fill="currentColor"/></svg>
              LinkedIn
            </a>
            <a href="{share_urls['x']}" class="share-btn" target="_blank" rel="noopener noreferrer" aria-label="Compartir a X">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" fill="currentColor"/></svg>
              X
            </a>
            <button class="share-btn js-copy-url" aria-label="Copiar enllaç" data-url="{base_url}">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <span class="copy-label">Copiar</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- CONTENT -->
      <article class="article-body__content">
        {body_html}

        {bottom_share}
      </article>
    </div>
  </div>
</section>
{related_section}

<!-- CTA -->
<section class="block-cta">
  <div class="container">
    <p class="block-cta__label">Tens alguna pregunta?</p>
    <h2 class="block-cta__title">Parla amb nosaltres sobre el teu projecte</h2>
    <a href="index.html#contacte">
      <button class="btn-white">
        Contactar
        <svg width="12" height="11" viewBox="0 0 12.447 10.89" fill="none">
          <path d="M9.335,3.11V4.666H0V6.222H9.335V7.778H7.78V9.334H6.224V10.89H7.78V9.334H9.335V7.778h1.556V6.222h1.556V4.666H10.891V3.11Zm-1.556,0H9.336V1.554H7.78ZM6.224,1.554H7.78V0H6.224Z" fill="currentColor"/>
        </svg>
      </button>
    </a>
  </div>
</section>

<!-- FOOTER -->
<footer>
  <div class="container">
    <div class="footer__content__info color-white">
      <div class="footer-col">
        <p class="footer__col-title">PAPIK</p>
        <ul>
          <li><a href="index.html#nosaltres">Qui som</a></li>
          <li><a href="blog.html">Blog</a></li>
          <li><a href="index.html#contacte">Contacte</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <p class="footer__col-title">Serveis</p>
        <ul>
          <li><a href="construccio.html">Construcció Residencial</a></li>
          <li><a href="promocio.html">Promoció Immobiliària</a></li>
          <li><a href="rehabilitacio.html">Rehabilitació Energètica</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <p class="footer__col-title">Oficines</p>
        <div class="info-showroom__item">
          <h3>SEU CENTRAL</h3>
          <p>Carrer de la Sort, 34<br>08172 Sant Cugat del Vallès<br><a href="tel:935906074">T 935 90 60 74</a></p>
        </div>
        <div class="info-showroom__item">
          <h3>CORREU</h3>
          <p><a href="mailto:info@papik.cat">info@papik.cat</a></p>
        </div>
      </div>
      <div class="footer__newsletter">
        <p class="footer__col-title" style="font-size:18px;font-weight:400;margin-bottom:20px;">Newsletter</p>
        <p>Segueix les novetats de PAPIK: projectes, rehabilitació energètica i ajudes disponibles.</p>
        <div class="newsletter-form">
          <input type="email" placeholder="El teu email" aria-label="Correu electrònic per a la newsletter">
          <button type="submit" aria-label="Subscriure's">
            <svg width="18" height="16" viewBox="0 0 12.447 10.89"><path d="M9.335,3.11V4.666H0V6.222H9.335V7.778H7.78V9.334H6.224V10.89H7.78V9.334H9.335V7.778h1.556V6.222h1.556V4.666H10.891V3.11Zm-1.556,0H9.336V1.554H7.78ZM6.224,1.554H7.78V0H6.224Z" fill="rgba(255,255,255,.8)"/></svg>
          </button>
        </div>
        <div class="footer__rrss">
          <p>Segueix-nos</p>
          <div class="rrss__links">
            <a href="#" aria-label="Instagram">Instagram</a>
            <a href="#" aria-label="LinkedIn">LinkedIn</a>
          </div>
        </div>
      </div>
    </div>
    <div class="copyright">
      <p>Copyright &copy; 2026 PAPIK SL &ndash; Tots els drets reservats<br>papik.cat</p>
      <div>
        <a href="#" style="font-size:12px;color:rgba(255,255,255,.35);margin-right:20px;">Avís Legal</a>
        <a href="#" style="font-size:12px;color:rgba(255,255,255,.35);">Política de Privacitat</a>
      </div>
      <button class="btn-up t14" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="Tornar a dalt">
        Amunt
        <svg width="11" height="12" viewBox="0 0 10.89 12.447"><path d="M9.335,3.11V4.666H0V6.222H9.335V7.778H7.78V9.334H6.224V10.89H7.78V9.334H9.335V7.778h1.556V6.222h1.556V4.666H10.891V3.11Zm-1.556,0H9.336V1.554H7.78ZM6.224,1.554H7.78V0H6.224Z" transform="translate(0 12.447) rotate(-90)" fill="#fff"/></svg>
      </button>
    </div>
  </div>
</footer>

<!-- JAVASCRIPT -->
<script>
  // Header scroll
  let lastScrollY = 0;
  const headerTop = document.getElementById('headerTop');
  window.addEventListener('scroll', () => {{
    const y = window.scrollY;
    if (y > 80 && y > lastScrollY) headerTop.classList.add('hidden');
    else headerTop.classList.remove('hidden');
    if (y > 10) headerTop.classList.add('hdr-scrolled');
    else headerTop.classList.remove('hdr-scrolled');
    lastScrollY = y;
  }}, {{ passive: true }});

  // Mobile nav
  const fadeBg = document.getElementById('fadeBg');
  const mobileNav = document.getElementById('mobileNav');
  const burgerBtn = document.getElementById('burgerBtn');
  const mobileNavClose = document.getElementById('mobileNavClose');
  burgerBtn.addEventListener('click', () => {{
    mobileNav.classList.add('open');
    document.body.style.overflow = 'hidden';
    fadeBg.style.zIndex = '190';
    document.body.classList.add('submenu-open');
  }});
  function closeMobileNav() {{
    mobileNav.classList.remove('open');
    document.body.style.overflow = '';
    fadeBg.style.zIndex = '70';
    document.body.classList.remove('submenu-open');
  }}
  mobileNavClose.addEventListener('click', closeMobileNav);
  fadeBg.addEventListener('click', closeMobileNav);
  mobileNav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMobileNav));

  // Copy URL
  document.querySelectorAll('.js-copy-url').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const url = btn.dataset.url || window.location.href;
      navigator.clipboard.writeText(url).then(() => {{
        const label = btn.querySelector('.copy-label');
        if (label) {{
          const original = label.textContent;
          label.textContent = 'Copiat!';
          btn.classList.add('share-btn--copied');
          setTimeout(() => {{ label.textContent = original; btn.classList.remove('share-btn--copied'); }}, 2000);
        }}
      }});
    }});
  }});
</script>
<script src="cursor.js"></script>
<!-- MOTION ENGINE -->
<script>
(function () {{
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;
  document.documentElement.classList.add('js-ready');
  if (reduced || !hasIO) {{
    document.querySelectorAll('[data-anim]').forEach(function (el) {{ el.classList.add('is-visible'); }});
    return;
  }}
  var io = new IntersectionObserver(function (entries) {{
    entries.forEach(function (e) {{
      if (!e.isIntersecting) return;
      e.target.classList.add('is-visible');
      io.unobserve(e.target);
    }});
  }}, {{ threshold: 0.1, rootMargin: '0px 0px -40px 0px' }});
  document.querySelectorAll('[data-anim]').forEach(function (el) {{
    var rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {{
      setTimeout(function(){{ el.classList.add('is-visible'); }}, 60);
    }} else {{ io.observe(el); }}
  }});
}})();
</script>
</body>
</html>'''

    return new_html


def main():
    converted = 0
    errors = []

    for article_file in ARTICLES:
        filepath = os.path.join(PAPIK_DIR, article_file)
        if not os.path.exists(filepath):
            errors.append(f"NOT FOUND: {article_file}")
            continue

        try:
            data = extract_article_data(filepath)
            new_html = build_new_article(data)

            # Write the new file (overwrite)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_html)

            converted += 1
            print(f"✓ Converted: {article_file} (cat: {data['category']}, date: {data['date']})")
        except Exception as e:
            errors.append(f"ERROR {article_file}: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*50}")
    print(f"Total converted: {converted}/{len(ARTICLES)}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("No errors!")


if __name__ == '__main__':
    main()
