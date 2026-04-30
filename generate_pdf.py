"""
generate_pdf.py  —  PAPIK Group · Generador de pressupostos en PDF
Combina la portada institucional (CONFIGURACIÓ PRESSUPOST - CAT.pdf)
amb les pàgines de partides pressupostàries generades amb ReportLab.
Les pàgines de pressupost s'insereixen entre la pàgina 5 i 6 de la portada.
"""

import os
from io import BytesIO
from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Table, TableStyle, Spacer,
    HRFlowable, KeepTogether,
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas as RLCanvas
from pypdf import PdfReader, PdfWriter

# ── Registre de fonts TT Firs Neue ───────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_TTF_BASE = os.path.join(_PROJECT_ROOT, 'fonts')

_FONT_LIGHT   = 'Helvetica'
_FONT_REGULAR = 'Helvetica'
_FONT_MEDIUM  = 'Helvetica'
_FONT_BOLD    = 'Helvetica-Bold'

_fonts_loaded = False
try:
    pdfmetrics.registerFont(TTFont('TTFirsNeue-Light',   os.path.join(_TTF_BASE, 'TT_Firs_Neue_Light.ttf')))
    pdfmetrics.registerFont(TTFont('TTFirsNeue-Regular', os.path.join(_TTF_BASE, 'TT_Firs_Neue_Regular.ttf')))
    pdfmetrics.registerFont(TTFont('TTFirsNeue-Medium',  os.path.join(_TTF_BASE, 'TT_Firs_Neue_Medium.ttf')))
    _FONT_LIGHT   = 'TTFirsNeue-Light'
    _FONT_REGULAR = 'TTFirsNeue-Regular'
    _FONT_MEDIUM  = 'TTFirsNeue-Medium'
    _FONT_BOLD    = 'TTFirsNeue-Medium'   # Medium com a equivalent de bold
    _fonts_loaded = True
except Exception:
    pass  # fallback a Helvetica si les fonts no es troben

# ── Colors corporatius PAPIK ──────────────────────────────────────────────────
GREEN    = colors.HexColor('#002819')
SAGE     = colors.HexColor('#95BBA5')
SAGE_LT  = colors.HexColor('#c4d8cb')
CREAM    = colors.HexColor('#F5F3EC')
WHITE    = colors.white
GRAY     = colors.HexColor('#6b7280')
GRAY_LT  = colors.HexColor('#e8e6df')
ALMOST_WHITE = colors.HexColor('#fafaf8')

W, H = A4   # 595.27 × 841.89 pts

# Marges idèntics als del DOCX corporatiu
ML = 2.25 * cm   # esquerra

# Ruta del logo oficial (PNG retallat sense marges)
_LOGO_PATH = os.path.join(_PROJECT_ROOT, 'static', 'logos', 'PAPIK-cropped.png')
MR = 2.25 * cm   # dreta
MT = 3.20 * cm   # superior (espai per capçalera + logo)
MB = 2.00 * cm   # inferior


# ── Helpers de format ─────────────────────────────────────────────────────────
def fmt_eur(n):
    """Formata com a moneda; retorna '—' si és 0 o None."""
    try:
        v = float(n)
    except (TypeError, ValueError):
        return '—'
    if v == 0:
        return '—'
    return f'{v:,.2f} €'.replace(',', 'X').replace('.', ',').replace('X', '.')


def fmt_eur_total(n):
    """Sempre mostra valor, fins i tot si és 0."""
    try:
        v = float(n)
    except (TypeError, ValueError):
        v = 0.0
    return f'{v:,.2f} €'.replace(',', 'X').replace('.', ',').replace('X', '.')


# ── Capçalera / peu de cada pàgina ───────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4

    # ── Capçalera ESQUERRA: logo oficial PAPIK ───────────────────────────
    logo_h = 0.85 * cm
    logo_w = logo_h * (536 / 143)
    logo_y = h - 0.65 * cm - logo_h
    if os.path.exists(_LOGO_PATH):
        canvas.drawImage(_LOGO_PATH, ML, logo_y, width=logo_w, height=logo_h,
                         mask='auto')

    # ── Capçalera DRETA: tagline corporatiu (bold, com al document) ──────
    canvas.setFont(_FONT_MEDIUM, 9.5)
    canvas.setFillColor(GREEN)
    canvas.drawRightString(w - MR, h - 0.80 * cm, 'Cases sostenibles,')
    canvas.drawRightString(w - MR, h - 1.30 * cm, 'naturalment')

    # (Peu de pàgina s'afegeix com a overlay amb numeració correcta)

    canvas.restoreState()


# ── Overlay de número de pàgina ──────────────────────────────────────────────
def _page_number_overlay(page_num, total_pages):
    """Crea una pàgina transparent amb 'Pàgina X de Y' al peu."""
    buf = BytesIO()
    c = RLCanvas(buf, pagesize=A4)
    w, h = A4
    c.setFont(_FONT_LIGHT, 7.5)
    c.setFillColor(GRAY)
    c.drawRightString(w - MR, 1.20 * cm, f'Pàgina {page_num} de {total_pages}')
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


# ── Estils de paràgraf ────────────────────────────────────────────────────────
def _sty(name, **kw):
    return ParagraphStyle(name, **kw)


TITLE_STY   = _sty('title',   fontName=_FONT_MEDIUM,  fontSize=14, textColor=GREEN,   spaceAfter=3,  leading=18)
SUB_STY     = _sty('sub',     fontName=_FONT_LIGHT,   fontSize=8.5,textColor=GRAY,    spaceAfter=2,  leading=12)
SECTION_STY = _sty('section', fontName=_FONT_MEDIUM,  fontSize=9,  textColor=WHITE,   spaceAfter=0,  leading=12)
BODY_STY    = _sty('body',    fontName=_FONT_LIGHT,   fontSize=9,  textColor=GREEN,   leading=13)
BOLD_STY    = _sty('bold',    fontName=_FONT_MEDIUM,  fontSize=9,  textColor=GREEN,   leading=13)


# ── Constructors de taula ─────────────────────────────────────────────────────
COL_W = W - ML - MR   # amplada útil


def _section_header(text):
    """Capçalera de secció: fons verd fosc, text blanc."""
    t = Table([[Paragraph(text, SECTION_STY)]], colWidths=[COL_W])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), GREEN),
        ('TOPPADDING',    (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
    ]))
    return t


def _line(desc, total, bold=False, subtotal=False):
    """Fila de partida pressupostària."""
    fn  = _FONT_MEDIUM if bold or subtotal else _FONT_LIGHT
    tc  = GREEN if subtotal else colors.HexColor('#2d3748')
    d_p = Paragraph(desc,  _sty('d', fontName=fn, fontSize=8.5, textColor=tc, leading=12))
    t_p = Paragraph(
        fmt_eur(total) if not subtotal else fmt_eur_total(total),
        _sty('t', fontName=fn, fontSize=8.5, textColor=tc, alignment=TA_RIGHT, leading=12)
    )
    return [d_p, t_p]


def _build_table(rows):
    """Taula de dues columnes: Descripció | Total."""
    t = Table(rows, colWidths=[COL_W - 4 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0),  (-1, -2), [WHITE, ALMOST_WHITE]),
        ('BACKGROUND',     (0, -1), (-1, -1), CREAM),
        ('LINEBELOW',      (0, 0),  (-1, -1), 0.3, GRAY_LT),
        ('TOPPADDING',     (0, 0),  (-1, -1), 5),
        ('BOTTOMPADDING',  (0, 0),  (-1, -1), 5),
        ('LEFTPADDING',    (0, 0),  (0, -1),  10),
        ('RIGHTPADDING',   (-1, 0), (-1, -1), 10),
        ('ALIGN',          (-1, 0), (-1, -1), 'RIGHT'),
    ]))
    return t


def _section(header_text, rows):
    """Capçalera + taula + espai, com a bloc indivisible."""
    return KeepTogether([
        _section_header(header_text),
        Spacer(1, 0.1 * cm),
        _build_table(rows),
        Spacer(1, 0.50 * cm),
    ])


# ── Generació de les pàgines del pressupost ───────────────────────────────────
def _generar_pagines_pressupost(data, result):
    """Genera les pàgines de partides amb ReportLab i retorna BytesIO."""
    buf    = BytesIO()
    frame  = Frame(ML, MB, COL_W, H - MT - MB, id='normal')
    tmpl   = PageTemplate(id='main', frames=[frame], onPage=_header_footer)
    doc    = BaseDocTemplate(buf, pagesize=A4, pageTemplates=[tmpl])

    vd     = result.get('variables_derivades', {})
    pe     = result['pack_envolvent']
    pi     = result['pack_installacions']
    pp     = result['pack_parking']
    pa     = result['pack_acabats']
    ce     = result['contractacio_externa']
    avui   = date.today()
    valid  = avui + timedelta(days=30)

    muni   = vd.get('municipi') or data.get('municipi', '—')
    m2     = data.get('m2', '—')
    plantes= str(data.get('plantes', '—'))
    banys  = str(data.get('num_banys', '—'))

    # Mapes de descripció (sense marques comercials)
    energia_map = {
        'max_eficiencia': 'Màxima eficiència energètica (Passivhaus)',
        'equilibri':      'Alt rendiment energètic',
        'confort':        'Qualitat estàndard PAPIK',
    }
    clima_map = {
        'total': 'Aerotèrmia completa (calefacció + ACS)',
        'acs':   'Aerotèrmia bàsica (ACS)',
        'no':    'Sense aerotèrmia',
    }
    aire_map = {
        'excel_lent': 'Excel·lent (recuperació de calor)',
        'bona':       'Bona (ventilació controlada)',
        'estandar':   'Estàndard',
    }
    acabats_map = {
        'funcional':    'Alta qualitat funcional',
        'alta_qualitat':'Alta gamma',
        'exclusiu':     'Disseny exclusiu personalitzat',
    }
    plantes_map = {'1': '1 planta', '2': '2 plantes', '3': '3 o més plantes'}

    story = []

    # ── Títol del document ───────────────────────────────────────────────
    story.append(Paragraph('PRESSUPOST ORIENTATIU', TITLE_STY))
    story.append(Paragraph(
        f'{muni}  ·  {m2} m²  ·  Emès el {avui.strftime("%d/%m/%Y")}', SUB_STY
    ))
    story.append(Spacer(1, 0.20 * cm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=GRAY_LT, spaceAfter=8))

    # ── Resum de configuració ─────────────────────────────────────────────
    config_data = [
        ('Ubicació del terreny',     muni),
        ('Superfície construïda',    f'{m2} m²'),
        ('Nombre de plantes',        plantes_map.get(plantes, plantes)),
        ('Banys',                    f"{banys} ({vd.get('bany_label', '—')})"),
        ('Coberta',                  vd.get('coberta_label', '—')),
        ('Façana',                   vd.get('facana_label', '—')),
        ('Paviment',                 vd.get('paviment_label', '—')),
        ('Eficiència energètica',    energia_map.get(data.get('energia_prioritat', ''), '—')),
        ('Sistema de climatització', clima_map.get(data.get('climatitzacio', ''), '—')),
        ("Qualitat de l'aire",       aire_map.get(data.get('qualitat_aire', ''), '—')),
        ("Nivell d'acabat",          acabats_map.get(data.get('estil_acabats', ''), '—')),
        ('Garatge',                  'Sí' if data.get('garatge') == 'si' else 'No'),
        ('Vàlid fins a',             valid.strftime('%d/%m/%Y')),
    ]
    conf_rows = [
        [Paragraph(k, _sty('ck', fontName=_FONT_MEDIUM, fontSize=7.5, textColor=GRAY,  leading=11)),
         Paragraph(v, _sty('cv', fontName=_FONT_LIGHT,  fontSize=7.5, textColor=GREEN, leading=11))]
        for k, v in config_data
    ]
    conf_table = Table(conf_rows, colWidths=[5.5 * cm, COL_W - 5.5 * cm])
    conf_table.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, CREAM]),
        ('LINEBELOW',      (0, 0), (-1, -1), 0.3, GRAY_LT),
        ('TOPPADDING',     (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 5),
        ('LEFTPADDING',    (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 8),
    ]))
    story.append(conf_table)
    story.append(Spacer(1, 0.80 * cm))

    # ── PACK ENVOLVENT TÈRMIC ─────────────────────────────────────────────
    envolvent_rows = [
        _line("Estructura vertical",             pe['estructura_vertical']),
        _line(f"Coberta i forjats ({vd.get('coberta_label', '')})", pe['coberta_forjats']),
        _line("Finestres d'alta eficiència",     pe['finestres']),
    ]
    if pe.get('increment_facana', 0) > 0:
        envolvent_rows.append(_line(f"Increment façana ({vd.get('facana_label', '')})", pe['increment_facana']))
    envolvent_rows.extend([
        _line("Porta d'entrada",                 pe['porta_entrada']),
        _line("Grua de muntatge",                pe['grua']),
        _line("SUBTOTAL PACK ENVOLVENT",         pe['total'], subtotal=True),
    ])
    story.append(_section('PACK ENVOLVENT TÈRMIC', envolvent_rows))

    # ── PACK INSTAL·LACIONS ───────────────────────────────────────────────
    inst_rows = [
        _line("Telecomunicacions",               pi['telecomunicacions']),
        _line("Sanejament interior",             pi['sanejament_interior']),
        _line("Electricitat interior",           pi['electricitat_interior']),
        _line("Fontaneria interior",             pi['agua_interior']),
        _line("Escomeses",                       pi['escomeses']),
        _line("Pre-instal·lació de ventilació",  pi['preinstallacio_ventilacio']),
    ]
    if pi.get('zehnder', 0) > 0:
        inst_rows.append(_line("Sistema de recuperació de calor (Zehnder)", pi['zehnder']))
    if pi.get('aerotermia', 0) > 0:
        aero_label = vd.get('aerotermia_label', 'Aerotèrmia')
        inst_rows.append(_line(aero_label, pi['aerotermia']))
    if pi.get('fan_coils', 0) > 0:
        n_fc = vd.get('num_fan_coils', 0)
        inst_rows.append(_line(f"Fan coils climatització ({n_fc} ud)", pi['fan_coils']))
    if pi.get('llar_foc', 0) > 0:
        inst_rows.append(_line("Llar de foc / xemeneia", pi['llar_foc']))
    if pi.get('solar', 0) > 0:
        inst_rows.append(_line("Plaques solars fotovoltaiques (~4 kWp)", pi['solar']))
    if pi.get('persianes', 0) > 0:
        n_fin = vd.get('num_finestres', 0)
        inst_rows.append(_line(f"Persianes motoritzades ({n_fin} ud)", pi['persianes']))
    if pi.get('membrana_rado', 0) > 0:
        inst_rows.append(_line("Membrana anti-radó", pi['membrana_rado']))
    if pi.get('domotica', 0) > 0:
        inst_rows.append(_line("Domòtica Loxone", pi['domotica']))
    inst_rows.append(_line("SUBTOTAL PACK INSTAL·LACIONS", pi['total'], subtotal=True))
    story.append(_section("PACK INSTAL·LACIONS", inst_rows))

    # ── PACK PARKING I EXTERIORS ──────────────────────────────────────────
    park_rows = []
    if pp.get('porta_peatonal', 0) > 0:
        park_rows.append(_line("Porta peatonal",          pp['porta_peatonal']))
    if pp.get('porta_motoritzada', 0) > 0:
        park_rows.append(_line("Porta motoritzada",       pp['porta_motoritzada']))
    if pp.get('garatge_estructura', 0) > 0:
        m2_g = data.get('m2_garatge', '—')
        park_rows.append(_line(f"Estructura garatge ({m2_g} m²)", pp['garatge_estructura']))
    if pp.get('porxos_terrasses', 0) > 0:
        m2_p = data.get('m2_porxos', '—')
        park_rows.append(_line(f"Pòrxos / terrassa ({m2_p} m²)", pp['porxos_terrasses']))
    if park_rows:
        park_rows.append(_line("SUBTOTAL PACK PARKING I EXTERIORS", pp['total'], subtotal=True))
        story.append(_section("PACK PARKING I EXTERIORS", park_rows))

    # ── PACK ACABATS INTERIORS ────────────────────────────────────────────
    m2_pav   = vd.get('m2_paviment_calculat', '—')
    n_portes = vd.get('num_portes_calculat', '—')
    pav_label = vd.get('paviment_label', '')
    bany_label = vd.get('bany_label', '')
    acabat_rows = [
        _line("Pintura interior",                 pa['pintura']),
        _line("Pladur",                           pa['pladur']),
        _line("Cuina completa equipada",          pa['cuina']),
        _line(f"Paviments {pav_label} ({m2_pav} m²)", pa['paviments']),
        _line(f"Portes interiors ({n_portes} u)", pa['portes_interiors']),
    ]
    if pa.get('estructura_krona', 0) > 0:
        acabat_rows.append(_line("Disseny d'interiors personalitzat", pa['estructura_krona']))
    acabat_rows.append(_line(f"Banys {bany_label} ({banys} u)", pa['banys']))
    if pa.get('escala', 0) > 0:
        acabat_rows.append(_line("Escala interior", pa['escala']))
    acabat_rows.append(_line("SUBTOTAL PACK ACABATS INTERIORS", pa['total'], subtotal=True))
    story.append(_section("PACK ACABATS INTERIORS", acabat_rows))

    # ── TRANSPORT ─────────────────────────────────────────────────────────
    if result.get('transport', 0) > 0:
        story.append(_section("TRANSPORT", [
            _line("Transport i desplaçament", result['transport']),
            _line("SUBTOTAL TRANSPORT",       result['transport'], subtotal=True),
        ]))

    # ── HONORARIS I GESTIÓ TÈCNICA ────────────────────────────────────────
    m2_fon = vd.get('m2_fonamentacio_calculat', '—')
    story.append(_section("HONORARIS I GESTIÓ TÈCNICA", [
        _line("Projecte arquitectònic (10,5% s/cost construcció)", ce['projecte_arquitectonic']),
        _line("Coordinació de seguretat i salut (1,75%)",           ce['seguretat_salut']),
        _line(f"Fonamentació ({m2_fon} m² × 396 €/m²)",           ce['fonamentacio']),
        _line("SUBTOTAL HONORARIS I GESTIÓ",                       ce['total'], subtotal=True),
    ]))

    # ── RESUM DE TOTALS ───────────────────────────────────────────────────
    story.append(Spacer(1, 0.30 * cm))

    totals_rows = [
        [Paragraph("Total Construcció",
                   _sty('t1',  fontName=_FONT_LIGHT,   fontSize=9,   textColor=GRAY,  leading=13)),
         Paragraph(fmt_eur_total(result['total_construccio']),
                   _sty('t1r', fontName=_FONT_LIGHT,   fontSize=9,   textColor=GREEN, alignment=TA_RIGHT, leading=13))],
        [Paragraph("Honoraris i Gestió Tècnica",
                   _sty('t2',  fontName=_FONT_LIGHT,   fontSize=9,   textColor=GRAY,  leading=13)),
         Paragraph(fmt_eur_total(ce['total']),
                   _sty('t2r', fontName=_FONT_LIGHT,   fontSize=9,   textColor=GREEN, alignment=TA_RIGHT, leading=13))],
        [Paragraph("Base Imposable",
                   _sty('t3',  fontName=_FONT_MEDIUM,  fontSize=9.5, textColor=GREEN, leading=13)),
         Paragraph(fmt_eur_total(result['total_sense_iva']),
                   _sty('t3r', fontName=_FONT_MEDIUM,  fontSize=9.5, textColor=GREEN, alignment=TA_RIGHT, leading=13))],
        [Paragraph("IVA 10%",
                   _sty('t4',  fontName=_FONT_LIGHT,   fontSize=9,   textColor=GRAY,  leading=13)),
         Paragraph(fmt_eur_total(result['iva']),
                   _sty('t4r', fontName=_FONT_LIGHT,   fontSize=9,   textColor=GREEN, alignment=TA_RIGHT, leading=13))],
        [Paragraph("TOTAL PRESSUPOST",
                   _sty('t5',  fontName=_FONT_MEDIUM,  fontSize=12,  textColor=WHITE, leading=16)),
         Paragraph(fmt_eur_total(result['total_pressupost']),
                   _sty('t5r', fontName=_FONT_MEDIUM,  fontSize=12,  textColor=WHITE, alignment=TA_RIGHT, leading=16))],
    ]

    totals_table = Table(totals_rows, colWidths=[COL_W - 5 * cm, 5 * cm])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0),  (-1, 1),  ALMOST_WHITE),
        ('BACKGROUND',    (0, 2),  (-1, 3),  CREAM),
        ('BACKGROUND',    (0, 4),  (-1, 4),  GREEN),
        ('LINEBELOW',     (0, 0),  (-1, -1), 0.4, GRAY_LT),
        ('TOPPADDING',    (0, 0),  (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0),  (-1, -1), 8),
        ('LEFTPADDING',   (0, 0),  (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0),  (-1, -1), 12),
        ('ALIGN',         (-1, 0), (-1, -1), 'RIGHT'),
    ]))
    story.append(KeepTogether([totals_table]))

    # ── Peu legal ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.50 * cm))
    story.append(Paragraph(
        f"Pressupost orientatiu emès el {avui.strftime('%d/%m/%Y')}, "
        f"vàlid fins al {valid.strftime('%d/%m/%Y')}. "
        "Els preus inclouen materials i mà d'obra. "
        "El cost de fonamentació és una estimació mitjana; el valor definitiu "
        "pot variar en funció de les condicions geotècniques del terreny. "
        "Pressupost sotmès a les condicions generals de PAPIK Group.",
        _sty('disc', fontName=_FONT_LIGHT, fontSize=7.5, textColor=GRAY, leading=11)
    ))

    doc.build(story)
    buf.seek(0)
    return buf


# ── Funció pública: genera el PDF final ───────────────────────────────────────
def generar_pdf(data, result):
    """
    Combina la portada institucional amb les pàgines de partides:
      · Pàgines 1–5 de la portada  (bloc corporatiu)
      · Pàgines del pressupost      (inserides entre pàg. 5 i 6)
      · Pàgines 6–8 de la portada  (proposta de valor del grup)
    Retorna BytesIO del PDF final.
    """
    cover_path = os.path.join(_PROJECT_ROOT, 'cover.pdf')

    writer = PdfWriter()

    # Llegim la portada una sola vegada
    cover_pages = []
    if os.path.exists(cover_path):
        try:
            cover_pdf = PdfReader(cover_path)
            cover_pages = list(cover_pdf.pages)
        except Exception:
            pass  # Si la portada falla, continuem sense ella

    # Pàgines 1–5 de la portada (índexs 0–4)
    pages_before = 0
    for i, page in enumerate(cover_pages):
        if i < 5:
            writer.add_page(page)
            pages_before += 1

    # Pàgines del pressupost generades (s'insereixen aquí)
    budget_buf = _generar_pagines_pressupost(data, result)
    budget_pdf = PdfReader(budget_buf)

    # Calcular total de pàgines del document final
    pages_after = max(0, len(cover_pages) - 5)
    n_budget = len(budget_pdf.pages)
    total_pages = pages_before + n_budget + pages_after

    # Afegir pàgines del pressupost amb numeració correcta
    for i, page in enumerate(budget_pdf.pages):
        overlay = _page_number_overlay(pages_before + 1 + i, total_pages)
        page.merge_page(overlay)
        writer.add_page(page)

    # Pàgines 6–8 de la portada (índexs 5–7)
    for i, page in enumerate(cover_pages):
        if i >= 5:
            writer.add_page(page)

    out = BytesIO()
    writer.write(out)
    out.seek(0)
    return out
