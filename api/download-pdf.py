"""
Vercel Python Serverless Function · POST /api/download-pdf

Genera un PDF amb el pressupost orientatiu (resum + desglossament).
Rep el payload del configurador i el resultat ja calculat per evitar
recomputar (la lògica de càlcul viu a /api/calcular).

Body JSON: { "payload": {...}, "result": {...} }
Response : application/pdf
"""
from http.server import BaseHTTPRequestHandler
from datetime import date
from io import BytesIO
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Table, TableStyle, Spacer, HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Colors corporatius PAPIK ────────────────────────────────────────────────
GREEN = colors.HexColor('#002819')
SAGE = colors.HexColor('#95BBA5')
SAGE_LT = colors.HexColor('#c4d8cb')
CREAM = colors.HexColor('#F4F1ED')
GRAY = colors.HexColor('#56685E')
GRAY_LT = colors.HexColor('#9FA9A3')
HAIRLINE = colors.HexColor('#d8d2c7')
BG_SOFT = colors.HexColor('#F5F3EC')

W, H = A4
ML, MR = 2.25 * cm, 2.25 * cm
MT, MB = 2.50 * cm, 2.20 * cm

FONT_LIGHT = 'Helvetica'
FONT_REGULAR = 'Helvetica'
FONT_MEDIUM = 'Helvetica-Bold'
FONT_BOLD = 'Helvetica-Bold'


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
    base = dict(name=name, fontName=FONT_REGULAR, fontSize=10, leading=14, textColor=GREEN)
    base.update(kw)
    return ParagraphStyle(**base)


def _header_footer(canvas, doc):
    canvas.saveState()
    # Header: PAPIK brand
    canvas.setFont(FONT_BOLD, 11)
    canvas.setFillColor(GREEN)
    canvas.drawString(ML, H - 1.5 * cm, 'PAPIK')
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(ML + 1.4 * cm, H - 1.5 * cm, 'GROUP')
    canvas.drawRightString(W - MR, H - 1.5 * cm, 'PRESSUPOST ORIENTATIU')

    # Hairline
    canvas.setStrokeColor(HAIRLINE)
    canvas.setLineWidth(0.5)
    canvas.line(ML, H - 1.85 * cm, W - MR, H - 1.85 * cm)

    # Footer
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(GRAY_LT)
    canvas.drawString(ML, MB - 0.6 * cm, 'PAPIK Real Estate Group S.L.U. · papik.cat')
    canvas.drawRightString(W - MR, MB - 0.6 * cm, f'Pàgina {doc.page}')
    canvas.restoreState()


def _h1(text):
    return Paragraph(text, _sty('h1', fontName=FONT_LIGHT, fontSize=28, leading=34, spaceAfter=8))


def _h2(text):
    return Paragraph(text, _sty('h2', fontName=FONT_REGULAR, fontSize=14, leading=18,
                                spaceBefore=18, spaceAfter=10, textColor=GREEN))


def _label(text):
    return Paragraph(text, _sty('label', fontName=FONT_BOLD, fontSize=8, leading=10,
                                textColor=GRAY_LT, spaceAfter=2))


def _value(text):
    return Paragraph(text, _sty('value', fontName=FONT_REGULAR, fontSize=11, leading=14, textColor=GREEN))


def _section_break():
    return HRFlowable(width='100%', thickness=0.5, color=HAIRLINE, spaceBefore=12, spaceAfter=12)


def _line_table(rows, total_label=None, total_value=None):
    """Genera taula de partides; última fila és subtotal/total."""
    data = []
    for label, value in rows:
        data.append([
            Paragraph(label, _sty('cell', fontSize=10, textColor=GREEN)),
            Paragraph(_fmt_eur(value), _sty('val', fontSize=10, alignment=TA_RIGHT, textColor=GRAY)),
        ])
    if total_label is not None:
        data.append([
            Paragraph(f'<b>{total_label}</b>', _sty('cell-bold', fontSize=10.5, fontName=FONT_BOLD, textColor=GREEN)),
            Paragraph(f'<b>{_fmt_eur(total_value)}</b>',
                      _sty('val-bold', fontSize=10.5, fontName=FONT_BOLD, alignment=TA_RIGHT, textColor=GREEN)),
        ])
    t = Table(data, colWidths=[12 * cm, 4.5 * cm])
    style = [
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.25, HAIRLINE),
    ]
    if total_label is not None:
        style.append(('LINEABOVE', (0, -1), (-1, -1), 0.75, GREEN))
        style.append(('TOPPADDING', (0, -1), (-1, -1), 10))
        style.append(('BOTTOMPADDING', (0, -1), (-1, -1), 10))
    t.setStyle(TableStyle(style))
    return t


def _summary_grid(items):
    """Grid 3-col amb label + value per cada item."""
    cells = []
    row = []
    for it in items:
        cell = [_label(it['label']), _value(it['value'])]
        row.append(cell)
        if len(row) == 3:
            cells.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append([Paragraph('', _sty('empty'))])
        cells.append(row)

    flat = []
    for r in cells:
        flat.append([Table([[c]], colWidths=[None]) for c in r])

    t = Table(flat, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm], rowHeights=[1.4 * cm] * len(flat))
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, HAIRLINE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HAIRLINE),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
    ]))
    return t


def _build_summary_items(payload, result):
    v = result.get('variables_derivades', {})
    items = []

    items.append({'label': 'SUPERFÍCIE', 'value': f"{int(payload.get('m2', 0))} m²"})
    plantes_label = {'1': '1 planta', '2': '2 plantes', '3': 'Més de 2 plantes'}.get(str(payload.get('plantes', '')), '—')
    items.append({'label': 'PLANTES', 'value': plantes_label})
    items.append({'label': 'BANYS', 'value': f"{payload.get('num_banys', '—')} banys"})

    if payload.get('garatge') == 'si':
        items.append({'label': 'GARATGE', 'value': f"Sí · {int(payload.get('m2_garatge', 0))} m²"})
    else:
        items.append({'label': 'GARATGE', 'value': 'No'})

    if payload.get('m2_porxos', 0) > 0:
        items.append({'label': 'PÒRXOS', 'value': f"{int(payload['m2_porxos'])} m²"})

    if str(payload.get('plantes')) != '1' and payload.get('tipus_escala') and payload.get('tipus_escala') != 'no':
        escala_label = {'fusta': 'Fusta', 'metallica': 'Metàl·lica'}.get(payload.get('tipus_escala'), payload.get('tipus_escala'))
        items.append({'label': 'ESCALA', 'value': escala_label})

    items.append({'label': 'COBERTA', 'value': v.get('coberta_label', '—')})
    items.append({'label': 'FAÇANA', 'value': v.get('facana_label', '—')})
    items.append({'label': 'PAVIMENT', 'value': v.get('paviment_label', '—')})
    items.append({'label': 'BANYS · QUALITAT', 'value': v.get('bany_label', '—')})

    equip = []
    if payload.get('plaques_solars') == 'si':
        equip.append('Plaques solars')
    if payload.get('persianes') == 'si':
        equip.append('Persianes motoritzades')
    if payload.get('fan_coils') == 'si':
        equip.append('Fan coils')
    if payload.get('llar_foc') == 'si':
        equip.append('Llar de foc')
    if payload.get('membrana_rado') == 'si':
        equip.append('Membrana radó')
    if payload.get('domotica') == 'si':
        equip.append('Domòtica Loxone')
    items.append({'label': 'EQUIPAMENT', 'value': ' · '.join(equip) if equip else 'Bàsic'})

    items.append({'label': 'UBICACIÓ', 'value': f"{v.get('municipi', '—')} ({v.get('km_transport', 0)} km)"})

    return items


def generate_pdf(payload, result):
    buf = BytesIO()
    doc = BaseDocTemplate(
        buf, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
        title='Pressupost orientatiu PAPIK',
        author='PAPIK Group',
    )
    frame = Frame(ML, MB, W - ML - MR, H - MT - MB, id='main',
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='papik', frames=[frame], onPage=_header_footer)])

    story = []

    # ── HERO ────────────────────────────────────────────────────────
    today = date.today().strftime('%d/%m/%Y')
    story.append(Paragraph('ESTIMACIÓ ORIENTATIVA', _sty('eyebrow', fontName=FONT_BOLD,
                          fontSize=8.5, leading=11, textColor=GRAY_LT, spaceAfter=8)))
    total = result.get('total_pressupost', 0)
    m2 = result.get('variables_derivades', {}).get('m2', payload.get('m2', 1)) or 1
    per_m2 = total / m2 if m2 else 0
    story.append(Paragraph(_fmt_eur_total(total),
                           _sty('total', fontName=FONT_LIGHT, fontSize=44, leading=50,
                                spaceAfter=4, textColor=GREEN)))
    story.append(Paragraph('Pressupost total (IVA inclòs)',
                           _sty('label-total', fontSize=10.5, leading=14, textColor=GRAY, spaceAfter=4)))
    story.append(Paragraph(f'≈ {_fmt_eur(per_m2)} / m² · {int(m2)} m² construïts · Generat el {today}',
                           _sty('meta', fontSize=9, leading=12, textColor=GRAY_LT, spaceAfter=18)))
    story.append(_section_break())

    # ── CONFIGURACIÓ ────────────────────────────────────────────────
    story.append(_h2('La teva configuració'))
    story.append(_summary_grid(_build_summary_items(payload, result)))
    story.append(Spacer(1, 6))

    # ── DESGLOSSAMENT ──────────────────────────────────────────────
    story.append(_h2('Desglossament del pressupost'))

    pe = result.get('pack_envolvent', {}) or {}
    rows_envolvent = [
        ('Estructura vertical', pe.get('estructura_vertical')),
        ('Coberta i forjats', pe.get('coberta_forjats')),
        ('Finestres', pe.get('finestres')),
        ('Façana (suplement)', pe.get('increment_facana')),
        ('Porta d\'entrada', pe.get('porta_entrada')),
        ('Grua i mitjans', pe.get('grua')),
    ]
    rows_envolvent = [(l, v) for l, v in rows_envolvent if v not in (None, 0, 0.0)]
    if rows_envolvent:
        story.append(Paragraph('ENVOLVENT TÈRMIC',
                               _sty('group', fontName=FONT_BOLD, fontSize=8.5, leading=11,
                                    textColor=GRAY, spaceAfter=4)))
        story.append(_line_table(rows_envolvent, 'Subtotal envolvent', pe.get('total')))
        story.append(Spacer(1, 14))

    pi = result.get('pack_installacions', {}) or {}
    rows_installacions = [
        ('Telecomunicacions', pi.get('telecomunicacions')),
        ('Sanejament', pi.get('sanejament_interior')),
        ('Electricitat', pi.get('electricitat_interior')),
        ('Aigua', pi.get('agua_interior')),
        ('Escomeses', pi.get('escomeses')),
        ('Pre-instal·lació ventilació', pi.get('preinstallacio_ventilacio')),
        ('Recuperador Zehnder', pi.get('zehnder')),
        ('Aerotèrmia', pi.get('aerotermia')),
        ('Fan coils', pi.get('fan_coils')),
        ('Llar de foc', pi.get('llar_foc')),
        ('Plaques solars', pi.get('solar')),
        ('Persianes motoritzades', pi.get('persianes')),
        ('Membrana anti-radó', pi.get('membrana_rado')),
        ('Domòtica Loxone', pi.get('domotica')),
    ]
    rows_installacions = [(l, v) for l, v in rows_installacions if v not in (None, 0, 0.0)]
    if rows_installacions:
        story.append(Paragraph('INSTAL·LACIONS',
                               _sty('group', fontName=FONT_BOLD, fontSize=8.5, leading=11,
                                    textColor=GRAY, spaceAfter=4)))
        story.append(_line_table(rows_installacions, 'Subtotal instal·lacions', pi.get('total')))
        story.append(Spacer(1, 14))

    pp = result.get('pack_parking', {}) or {}
    rows_parking = [
        ('Porta peatonal', pp.get('porta_peatonal')),
        ('Porta motoritzada', pp.get('porta_motoritzada')),
        ('Estructura garatge', pp.get('garatge_estructura')),
        ('Pòrxos i terrasses', pp.get('porxos_terrasses')),
    ]
    rows_parking = [(l, v) for l, v in rows_parking if v not in (None, 0, 0.0)]
    if rows_parking:
        story.append(Paragraph('PARKING I EXTERIORS',
                               _sty('group', fontName=FONT_BOLD, fontSize=8.5, leading=11,
                                    textColor=GRAY, spaceAfter=4)))
        story.append(_line_table(rows_parking, 'Subtotal parking', pp.get('total')))
        story.append(Spacer(1, 14))

    pa = result.get('pack_acabats', {}) or {}
    rows_acabats = [
        ('Pintura', pa.get('pintura')),
        ('Pladur', pa.get('pladur')),
        ('Cuina', pa.get('cuina')),
        ('Paviments', pa.get('paviments')),
        ('Portes interiors', pa.get('portes_interiors')),
        ('Estructura Krona', pa.get('estructura_krona')),
        ('Banys', pa.get('banys')),
        ('Escala', pa.get('escala')),
    ]
    rows_acabats = [(l, v) for l, v in rows_acabats if v not in (None, 0, 0.0)]
    if rows_acabats:
        story.append(Paragraph('ACABATS INTERIORS',
                               _sty('group', fontName=FONT_BOLD, fontSize=8.5, leading=11,
                                    textColor=GRAY, spaceAfter=4)))
        story.append(_line_table(rows_acabats, 'Subtotal acabats', pa.get('total')))
        story.append(Spacer(1, 14))

    # Altres conceptes
    ce = result.get('contractacio_externa', {}) or {}
    rows_altres = []
    km = result.get('variables_derivades', {}).get('km_transport', 0)
    rows_altres.append((f'Transport ({km} km)', result.get('transport')))
    if ce.get('projecte_arquitectonic'):
        rows_altres.append(('Projecte arquitectònic', ce.get('projecte_arquitectonic')))
    rows_altres.append(('Seguretat i salut', ce.get('seguretat_salut')))
    rows_altres.append(('Fonamentació', ce.get('fonamentacio')))
    rows_altres.append(('IVA (10%)', result.get('iva')))
    story.append(Paragraph('ALTRES CONCEPTES',
                           _sty('group', fontName=FONT_BOLD, fontSize=8.5, leading=11,
                                textColor=GRAY, spaceAfter=4)))
    story.append(_line_table(rows_altres))
    story.append(Spacer(1, 18))

    # TOTAL FINAL
    total_table = Table(
        [[Paragraph('<b>TOTAL ESTIMAT (IVA inclòs)</b>',
                    _sty('total-l', fontName=FONT_BOLD, fontSize=12, textColor=GREEN)),
          Paragraph(f'<b>{_fmt_eur_total(total)}</b>',
                    _sty('total-r', fontName=FONT_BOLD, fontSize=18, alignment=TA_RIGHT, textColor=GREEN))]],
        colWidths=[10.5 * cm, 6 * cm],
    )
    total_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
        ('BACKGROUND', (0, 0), (-1, -1), CREAM),
        ('LINEABOVE', (0, 0), (-1, 0), 1.0, GREEN),
        ('LINEBELOW', (0, 0), (-1, 0), 1.0, GREEN),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 24))

    # Disclaimer
    story.append(_section_break())
    story.append(Paragraph(
        'Aquesta és una estimació orientativa basada en costos mitjans reals de projectes Papik. '
        'El pressupost definitiu pot variar en funció de les condicions del terreny, '
        'el projecte arquitectònic i els preus actualitzats dels materials.',
        _sty('disclaimer', fontSize=8, leading=12, alignment=TA_CENTER, textColor=GRAY_LT)))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        f"Generat el {today} · Per a {payload.get('nom', '—')} · {payload.get('email', '—')}",
        _sty('meta-bottom', fontSize=8, leading=11, alignment=TA_CENTER, textColor=GRAY_LT)))

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf


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
            self.send_header('Content-Disposition', f'attachment; filename="pressupost-papik-{today}.pdf"')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(pdf_bytes)))
            self.end_headers()
            self.wfile.write(pdf_bytes)
        except (ValueError, TypeError) as e:
            self._send_json(400, {'error': 'invalid_input', 'detail': str(e)})
        except Exception as e:
            self._send_json(500, {'error': 'server_error', 'detail': str(e)})

    def do_GET(self):
        self._send_json(405, {'error': 'method_not_allowed', 'detail': 'use POST'})
