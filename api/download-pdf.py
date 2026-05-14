"""
Vercel Python Serverless Function · POST /api/download-pdf

Genera la proposta de pressupost final, que NO és un PDF aïllat sinó la
plantilla corporativa de PAPIK Group amb les pàgines del pressupost
inserides entre la pàgina 6 («Presentación del presupuesto») i la 7
(«Fases del proceso de proyecto y construcción»).

Flux:
  1. Genera 1-2 pàgines internes amb el detall del pressupost
     (configuració del client + desglossament per packs + total) amb la
     tipografia TT Firs Neue i el color corporatiu #002819, replicant
     l'estil de seccions de la plantilla (títol amb línia horitzontal,
     cos sangrat, header i footer iguals que la resta del document).
  2. Fa l'splice amb pypdf: pàgines 1-6 plantilla + pàgines generades +
     pàgines 7-10 plantilla.
  3. Sobreposa nous números de pàgina ("Página X de N", on N és el
     total final) sobre cada full per evitar que els footers de la
     plantilla original quedin descabalats.

Body JSON: { "payload": {...}, "result": {...} }
Response : application/pdf
"""
from http.server import BaseHTTPRequestHandler
from datetime import date
from io import BytesIO
import json
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Table, TableStyle, Spacer, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # legacy environments
    from PyPDF2 import PdfReader, PdfWriter  # type: ignore


# ── Brand palette (matches the website + template) ──────────────────────────
GREEN      = colors.HexColor('#002819')
GREEN_SOFT = colors.HexColor('#56685E')
ACCENT     = colors.HexColor('#95BBA5')
HAIRLINE   = colors.HexColor('#002819')   # thin lines under titles
MUTED      = colors.HexColor('#56685E')
BG_BAND    = colors.HexColor('#F4F1ED')

W, H = A4
# Match the template's margins so headers/footers align
ML, MR = 100, 100
MT, MB = 130, 90


# ── Asset paths (relative to this file, bundled with the function) ──────────
HERE     = os.path.dirname(os.path.abspath(__file__))
ASSETS   = os.path.join(HERE, '_assets')
TEMPLATE = os.path.join(ASSETS, 'plantilla.pdf')
FONTS    = os.path.join(ASSETS, 'fonts')


# ── Font registration (TT Firs Neue corporate family) ───────────────────────
_FONTS_REGISTERED = False

def _register_fonts():
    """Register the corporate font once per cold start. Falls back to
    Helvetica if the TTF files aren't bundled (so the function still
    renders something rather than 500-ing)."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    mapping = [
        ('TTFirs',         'TT_Firs_Neue_Regular.ttf'),
        ('TTFirs-Light',   'TT_Firs_Neue_Light.ttf'),
        ('TTFirs-Medium',  'TT_Firs_Neue_Medium.ttf'),
    ]
    for name, fname in mapping:
        try:
            pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, fname)))
        except Exception:
            pass
    _FONTS_REGISTERED = True

FONT_LIGHT  = 'TTFirs-Light'
FONT_REG    = 'TTFirs'
FONT_MEDIUM = 'TTFirs-Medium'


# ── Helpers ─────────────────────────────────────────────────────────────────

def _fmt_eur(n):
    try:
        v = float(n)
        if v == 0:
            return '—'
        s = f'{int(round(v)):,}'.replace(',', '.')
        return f'{s} €'
    except Exception:
        return '—'


def _fmt_eur_total(n):
    try:
        v = float(n)
        s = f'{int(round(v)):,}'.replace(',', '.')
        return f'{s} €'
    except Exception:
        return '—'


def _sty(name, **kw):
    base = dict(name=name, fontName=FONT_REG, fontSize=10, leading=15, textColor=GREEN)
    base.update(kw)
    return ParagraphStyle(**base)


# ── Page chrome (header + footer) ───────────────────────────────────────────

def _draw_chrome(canvas, doc):
    """Header (PAPIK logo + tagline) and footer. Page number is added
    later in a post-process pass once we know the final total."""
    canvas.saveState()
    # Header: PAPIK wordmark (left)
    canvas.setFont(FONT_MEDIUM, 16)
    canvas.setFillColor(GREEN)
    canvas.drawString(ML, H - 60, 'PAPIK')
    canvas.setFont(FONT_REG, 6)
    canvas.drawString(ML + 56, H - 53, '®')

    # Header: tagline (right, two lines)
    canvas.setFont(FONT_MEDIUM, 10.5)
    canvas.setFillColor(GREEN)
    canvas.drawRightString(W - MR, H - 56, 'Casas sostenibles,')
    canvas.drawRightString(W - MR, H - 70, 'naturalmente')

    # Footer placeholder marker — actual "Página X de N" comes later in
    # the overlay pass. We still leave a small reservation so reportlab
    # doesn't drop content onto it.
    canvas.restoreState()


# ── Section title with hairline divider (template style) ────────────────────

def _section_title(text, line_w=None):
    """Title row matching the template style: small uppercase title
    followed by a thin horizontal line that fills the column."""
    if line_w is None:
        line_w = W - ML - MR
    para = Paragraph(
        text,
        _sty('section-title', fontName=FONT_MEDIUM, fontSize=10.5, leading=13,
             textColor=GREEN, spaceAfter=0),
    )
    # Build a 2-row 1-col table: title row, then a thin underline rule
    t = Table(
        [[para]],
        colWidths=[line_w],
    )
    t.setStyle(TableStyle([
        ('LINEBELOW',    (0, 0), (-1, 0), 0.6, HAIRLINE),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
    ]))
    return t


def _indented_body(flowables, indent=60):
    """Wrap content in a table so it appears indented from the section
    title, just like the template's body paragraphs."""
    t = Table([[flowables]], colWidths=[W - ML - MR - indent])
    t.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',  (0, 0), (-1, -1), indent),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 10),
    ]))
    return t


# ── Budget content: configuration summary ───────────────────────────────────

def _build_summary_lines(payload, result):
    """Return a list of (label, value) tuples summarising the user input."""
    v = result.get('variables_derivades', {}) or {}
    rows = []

    municipi = v.get('municipi') or payload.get('municipi') or '—'
    rows.append(('Ubicació', municipi))
    rows.append(('Superfície construïda', f"{int(payload.get('m2', 0))} m²"))

    plantes = str(payload.get('plantes', ''))
    plantes_lbl = {'1': '1 planta', '2': '2 plantes', '3': 'Més de 2 plantes'}.get(plantes, '—')
    rows.append(('Plantes', plantes_lbl))
    rows.append(('Banys', f"{payload.get('num_banys', '—')} banys"))

    if payload.get('garatge') == 'si':
        rows.append(('Garatge', f"Sí · {int(payload.get('m2_garatge', 0))} m²"))
    else:
        rows.append(('Garatge', 'No'))

    if payload.get('m2_porxos', 0):
        rows.append(('Pòrxos / terrasses', f"{int(payload['m2_porxos'])} m²"))

    rows.append(('Coberta', v.get('coberta_label', '—')))
    rows.append(('Façana', v.get('facana_label', '—')))
    rows.append(('Paviment', v.get('paviment_label', '—')))
    rows.append(('Banys (qualitat)', v.get('bany_label', '—')))
    rows.append(('Finestres', v.get('finestres_label', '—')))
    rows.append(('Aerotèrmia', v.get('aerotermia_label', '—')))

    equip = []
    if payload.get('plaques_solars') == 'si': equip.append('Plaques solars')
    if payload.get('persianes') == 'si':      equip.append('Persianes motoritzades')
    if payload.get('fan_coils') == 'si':      equip.append('Fan coils')
    if payload.get('llar_foc') == 'si':       equip.append('Llar de foc')
    if payload.get('membrana_rado') == 'si':  equip.append('Membrana radó')
    if payload.get('domotica') == 'si':       equip.append('Domòtica Loxone')
    if equip:
        rows.append(('Equipament addicional', ' · '.join(equip)))

    rows.append(('Transport (estimat)',
                 f"{v.get('km_transport', 0)} km des de Sant Cugat"))

    return rows


def _summary_table(rows):
    """Two-column table styled like the template's body lists."""
    data = []
    for label, value in rows:
        data.append([
            Paragraph(label,
                      _sty('s-l', fontName=FONT_REG, fontSize=10, textColor=GREEN_SOFT)),
            Paragraph(str(value),
                      _sty('s-v', fontName=FONT_MEDIUM, fontSize=10,
                           alignment=TA_RIGHT, textColor=GREEN)),
        ])
    t = Table(data, colWidths=[None, 6 * cm])
    t.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 6),
        ('LINEBELOW',    (0, 0), (-1, -2), 0.25,
                         colors.HexColor('#dcdcd5')),
    ]))
    return t


# ── Budget content: breakdown packs ────────────────────────────────────────

PACKS = [
    ('ENVOLVENT TÈRMIC', 'pack_envolvent', [
        ('Estructura vertical', 'estructura_vertical'),
        ('Coberta i forjats',   'coberta_forjats'),
        ('Finestres',           'finestres'),
        ('Suplement façana',    'increment_facana'),
        ("Porta d'entrada",     'porta_entrada'),
        ('Grua i mitjans',      'grua'),
    ]),
    ('INSTAL·LACIONS', 'pack_installacions', [
        ('Telecomunicacions',         'telecomunicacions'),
        ('Sanejament',                'sanejament_interior'),
        ('Electricitat',              'electricitat_interior'),
        ('Aigua',                     'agua_interior'),
        ('Escomeses',                 'escomeses'),
        ('Pre-instal·lació ventilació','preinstallacio_ventilacio'),
        ('Recuperador Zehnder',       'zehnder'),
        ('Aerotèrmia',                'aerotermia'),
        ('Fan coils',                 'fan_coils'),
        ('Llar de foc',               'llar_foc'),
        ('Plaques solars',            'solar'),
        ('Persianes motoritzades',    'persianes'),
        ('Membrana anti-radó',        'membrana_rado'),
        ('Domòtica Loxone',           'domotica'),
    ]),
    ('PARKING I EXTERIORS', 'pack_parking', [
        ('Porta peatonal',     'porta_peatonal'),
        ('Porta motoritzada',  'porta_motoritzada'),
        ('Estructura garatge', 'garatge_estructura'),
        ('Pòrxos i terrasses', 'porxos_terrasses'),
    ]),
    ('ACABATS INTERIORS', 'pack_acabats', [
        ('Pintura',           'pintura'),
        ('Pladur',            'pladur'),
        ('Cuina',             'cuina'),
        ('Paviments',         'paviments'),
        ('Portes interiors',  'portes_interiors'),
        ('Estructura Krona',  'estructura_krona'),
        ('Banys',             'banys'),
        ('Escala',            'escala'),
    ]),
]


def _pack_table(pack_data, lines, subtotal_label):
    """Single pack table: indented line items + bold subtotal row."""
    rows = []
    for label, key in lines:
        v = pack_data.get(key)
        if v in (None, 0, 0.0):
            continue
        rows.append([
            Paragraph(label, _sty('p-l', fontSize=9.5, textColor=GREEN)),
            Paragraph(_fmt_eur(v),
                      _sty('p-v', fontSize=9.5, alignment=TA_RIGHT, textColor=GREEN_SOFT)),
        ])
    if not rows:
        return None
    # Subtotal row
    rows.append([
        Paragraph(subtotal_label,
                  _sty('p-st', fontName=FONT_MEDIUM, fontSize=10, textColor=GREEN)),
        Paragraph(_fmt_eur_total(pack_data.get('total', 0)),
                  _sty('p-st-v', fontName=FONT_MEDIUM, fontSize=10,
                       alignment=TA_RIGHT, textColor=GREEN)),
    ])
    t = Table(rows, colWidths=[None, 4 * cm])
    style = [
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        # subtle dotted-look hairline between items
        ('LINEBELOW',    (0, 0), (-1, -2), 0.25, colors.HexColor('#e2dfd6')),
        # solid line above subtotal
        ('LINEABOVE',    (0, -1), (-1, -1), 0.6, HAIRLINE),
        ('TOPPADDING',   (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING',(0, -1), (-1, -1), 8),
    ]
    t.setStyle(TableStyle(style))
    return t


# ── Story assembly (the inserted pages) ─────────────────────────────────────

def _build_story(payload, result):
    today = date.today().strftime('%d/%m/%Y')

    total      = result.get('total_pressupost', 0)
    no_iva     = result.get('total_sense_iva', 0)
    iva        = result.get('iva', 0)
    transport  = result.get('transport', 0)
    ce         = result.get('contractacio_externa', {}) or {}
    v          = result.get('variables_derivades', {}) or {}
    m2         = float(v.get('m2') or payload.get('m2') or 0) or 1.0
    per_m2     = total / m2 if m2 else 0

    story = []

    # ── Page 1: total + summary ──────────────────────────────────────
    story.append(_section_title('PROPUESTA ECONÓMICA'))
    story.append(Spacer(1, 18))

    # Hero: total amount
    hero_left = [
        Paragraph('Pressupost total orientatiu',
                  _sty('hero-eyebrow', fontName=FONT_REG, fontSize=9.5,
                       leading=12, textColor=GREEN_SOFT, spaceAfter=4)),
        Paragraph(_fmt_eur_total(total),
                  _sty('hero-total', fontName=FONT_LIGHT, fontSize=42,
                       leading=46, textColor=GREEN, spaceAfter=4)),
        Paragraph(
            f"≈ {_fmt_eur(per_m2)} / m²  ·  {int(m2)} m² construïts  ·  emès el {today}",
            _sty('hero-meta', fontSize=9, leading=12, textColor=GREEN_SOFT)),
    ]
    hero = Table([[hero_left]], colWidths=[W - ML - MR])
    hero.setStyle(TableStyle([
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 12),
    ]))
    story.append(hero)
    story.append(Spacer(1, 4))

    # Configuration summary
    story.append(_section_title('RESUM DE LA CONFIGURACIÓ'))
    story.append(_indented_body(_summary_table(_build_summary_lines(payload, result))))
    story.append(Spacer(1, 10))

    # Force a new page for the breakdown so each pack stays readable
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # ── Page 2: breakdown packs + totals ─────────────────────────────
    story.append(_section_title('DESGLOSSAMENT PER PARTIDES'))
    story.append(Spacer(1, 14))

    for title, key, lines in PACKS:
        data = result.get(key) or {}
        tbl = _pack_table(data, lines, f'Subtotal · {title.lower()}')
        if tbl is None:
            continue
        story.append(KeepTogether([
            Paragraph(title,
                      _sty('pack-title', fontName=FONT_MEDIUM, fontSize=10,
                           leading=12, textColor=GREEN_SOFT, spaceAfter=4)),
            _indented_body(tbl, indent=20),
        ]))
        story.append(Spacer(1, 6))

    # Altres conceptes
    rows_extra = []
    if transport:
        km = v.get('km_transport', 0)
        rows_extra.append((f'Transport ({km} km)', transport))
    if ce.get('projecte_arquitectonic'):
        rows_extra.append(('Projecte arquitectònic', ce['projecte_arquitectonic']))
    if ce.get('seguretat_salut'):
        rows_extra.append(('Seguretat i salut', ce['seguretat_salut']))
    if ce.get('fonamentacio'):
        rows_extra.append(('Fonamentació', ce['fonamentacio']))
    if rows_extra:
        story.append(Paragraph(
            'ALTRES CONCEPTES',
            _sty('pack-title', fontName=FONT_MEDIUM, fontSize=10, leading=12,
                 textColor=GREEN_SOFT, spaceAfter=4)))
        extra_rows = [[
            Paragraph(lbl, _sty('p-l', fontSize=9.5, textColor=GREEN)),
            Paragraph(_fmt_eur(vv),
                      _sty('p-v', fontSize=9.5, alignment=TA_RIGHT, textColor=GREEN_SOFT)),
        ] for lbl, vv in rows_extra]
        et = Table(extra_rows, colWidths=[None, 4 * cm])
        et.setStyle(TableStyle([
            ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING',   (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
            ('LINEBELOW',    (0, 0), (-1, -1), 0.25, colors.HexColor('#e2dfd6')),
        ]))
        story.append(_indented_body(et, indent=20))
        story.append(Spacer(1, 12))

    # Total final block — coloured strip, like a final emphasis
    total_table = Table(
        [
            [Paragraph('Subtotal sense IVA',
                       _sty('tot-lbl', fontSize=10, textColor=GREEN_SOFT)),
             Paragraph(_fmt_eur_total(no_iva),
                       _sty('tot-val', fontSize=10, alignment=TA_RIGHT, textColor=GREEN))],
            [Paragraph('IVA (10%)',
                       _sty('tot-lbl', fontSize=10, textColor=GREEN_SOFT)),
             Paragraph(_fmt_eur_total(iva),
                       _sty('tot-val', fontSize=10, alignment=TA_RIGHT, textColor=GREEN))],
            [Paragraph('TOTAL PRESSUPOST',
                       _sty('tot-final', fontName=FONT_MEDIUM, fontSize=12,
                            textColor=GREEN)),
             Paragraph(_fmt_eur_total(total),
                       _sty('tot-final-v', fontName=FONT_MEDIUM, fontSize=14,
                            alignment=TA_RIGHT, textColor=GREEN))],
        ],
        colWidths=[None, 5 * cm],
    )
    total_table.setStyle(TableStyle([
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING',  (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING',   (0, 0), (0, 1), 6),
        ('BOTTOMPADDING',(0, 0), (0, 1), 6),
        ('TOPPADDING',   (0, -1), (-1, -1), 14),
        ('BOTTOMPADDING',(0, -1), (-1, -1), 14),
        ('LINEBELOW',    (0, 0), (-1, -2), 0.4, colors.HexColor('#e2dfd6')),
        ('LINEABOVE',    (0, -1), (-1, -1), 1.0, GREEN),
        ('LINEBELOW',    (0, -1), (-1, -1), 1.0, GREEN),
        ('BACKGROUND',   (0, -1), (-1, -1), BG_BAND),
    ]))
    story.append(_indented_body(total_table, indent=20))
    story.append(Spacer(1, 8))

    # Disclaimer
    story.append(Paragraph(
        'Estimació orientativa basada en costos mitjans reals de projectes PAPIK Group. '
        'El pressupost definitiu pot variar segons les condicions del terreny, '
        'el projecte arquitectònic i els preus actualitzats dels materials. '
        f'Vàlid fins el {result.get("data_validesa") or "—"}.',
        _sty('disclaimer', fontSize=8, leading=11, alignment=TA_LEFT, textColor=GREEN_SOFT)))

    return story


def _render_budget_pages(payload, result):
    """Generate the inserted pages as a standalone PDF (bytes)."""
    _register_fonts()
    buf = BytesIO()
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
        title='Proposta econòmica PAPIK',
        author='PAPIK Group',
    )
    frame = Frame(ML, MB, W - ML - MR, H - MT - MB, id='main',
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='papik', frames=[frame], onPage=_draw_chrome)])
    doc.build(_build_story(payload, result))
    return buf.getvalue()


# ── Footer overlay: covers original numbers and stamps fresh ones ───────────

def _make_footer_overlay(page_num, total):
    """Generate a single-page overlay PDF (A4) with a white rectangle
    covering the original page number area + a fresh "Página X de N"
    stamp in corporate green. Returns the first PdfReader page."""
    _register_fonts()
    buf = BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    # Cover any pre-existing footer text (right side, near bottom).
    # The template's "Página X de 10" sits roughly between y=40 and y=60,
    # so we paint a generous safety margin (y=20..80) to also swallow
    # descenders and the underline below the page-number digit.
    c.setFillColorRGB(1, 1, 1)
    c.rect(W * 0.50, 20, W * 0.48, 60, fill=1, stroke=0)
    # Fresh footer text
    c.setFillColor(GREEN)
    label = 'Página '
    num_a = str(page_num)
    sep   = ' de '
    num_b = str(total)
    w_a = c.stringWidth(label, FONT_REG, 10)
    w_b = c.stringWidth(num_a, FONT_MEDIUM, 10)
    w_c = c.stringWidth(sep,   FONT_REG, 10)
    w_d = c.stringWidth(num_b, FONT_MEDIUM, 10)
    total_w = w_a + w_b + w_c + w_d
    x = W - MR - total_w + 30  # nudged right to align with template
    y = 50
    c.setFont(FONT_REG, 10);    c.drawString(x, y, label); x += w_a
    c.setFont(FONT_MEDIUM, 10); c.drawString(x, y, num_a); x += w_b
    c.setFont(FONT_REG, 10);    c.drawString(x, y, sep);   x += w_c
    c.setFont(FONT_MEDIUM, 10); c.drawString(x, y, num_b)
    c.save()
    return PdfReader(BytesIO(buf.getvalue())).pages[0]


# ── Main splice: template[0:6] + budget pages + template[6:10] ──────────────

# In the original template these pages do NOT carry a "Página X de 10"
# footer (1-indexed): the cover (1) and the three dark-green "Propuesta
# de valor" pages (3, 4, 5). We must NOT stamp a new footer there or
# we'd plant a white box on top of a full-bleed photo / dark-green
# background.
TEMPLATE_PAGES_WITH_FOOTER = {2, 6, 7, 8, 9, 10}


def generate_pdf(payload, result):
    # 1. Generate the budget pages
    budget_bytes = _render_budget_pages(payload, result)
    budget_reader = PdfReader(BytesIO(budget_bytes))
    n_budget = len(budget_reader.pages)

    # 2. Open the template
    template_reader = PdfReader(TEMPLATE)
    n_template = len(template_reader.pages)
    split = min(6, n_template)

    total_pages = n_template + n_budget

    writer = PdfWriter()

    # Pages 1..6 of the template — only stamp pages that originally had a footer
    for i in range(split):
        page = template_reader.pages[i]
        if (i + 1) in TEMPLATE_PAGES_WITH_FOOTER:
            page.merge_page(_make_footer_overlay(i + 1, total_pages))
        writer.add_page(page)

    # Inserted budget pages — always stamped (they were generated white-bg)
    for i, page in enumerate(budget_reader.pages):
        page.merge_page(_make_footer_overlay(split + i + 1, total_pages))
        writer.add_page(page)

    # Pages 7..end of template — same filter applies
    for i in range(split, n_template):
        page = template_reader.pages[i]
        if (i + 1) in TEMPLATE_PAGES_WITH_FOOTER:
            new_idx = split + n_budget + (i - split) + 1
            page.merge_page(_make_footer_overlay(new_idx, total_pages))
        writer.add_page(page)

    out = BytesIO()
    writer.write(out)
    return out.getvalue()


# ── HTTP handler ────────────────────────────────────────────────────────────

class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0) or 0)
            body = self.rfile.read(length).decode('utf-8') if length else ''
            data = json.loads(body) if body else {}
            payload = data.get('payload', {})
            result = data.get('result', {})
            if not result:
                self._send_json(400, {'error': 'missing_result'})
                return
            pdf_bytes = generate_pdf(payload, result)
            today = date.today().strftime('%Y%m%d')
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition',
                             f'attachment; filename="pressupost-papik-{today}.pdf"')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self.end_headers()
            self.wfile.write(pdf_bytes)
        except FileNotFoundError as e:
            self._send_json(500, {
                'error': 'template_missing',
                'detail': f'Plantilla no trobada: {e}. '
                          'Comprova que api/_assets/plantilla.pdf està al bundle.',
            })
        except (ValueError, TypeError) as e:
            self._send_json(400, {'error': 'invalid_input', 'detail': str(e)})
        except Exception as e:
            self._send_json(500, {'error': 'server_error', 'detail': str(e)})

    def do_GET(self):
        self._send_json(405, {'error': 'method_not_allowed', 'detail': 'use POST'})
