import os, base64, json, io, re
import openai
import pdfplumber
import requests as http
try:
    from pdf2image import convert_from_bytes
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False
from flask import Flask, request, jsonify, Response, redirect
from datetime import date, timedelta
from generate_pdf import generar_pdf

app = Flask(__name__)

# Distàncies aproximades (km per carretera) des de Sant Cugat del Vallès
MUNICIPIS_KM = {
    "Abrera": 27, "Alcanar": 196, "Amposta": 180, "Arenys de Mar": 48,
    "Badalona": 32, "Badia del Vallès": 12, "Banyoles": 108, "Barcelona": 23,
    "Barberà del Vallès": 13, "Bellaterra": 4, "Berga": 92, "Blanes": 70,
    "Calafell": 60, "Calella": 60, "Cambrils": 123, "Capellades": 58,
    "Castellbisbal": 14, "Castelldefels": 29, "Castelló d'Empúries": 148,
    "Castellví de Rosanes": 22, "Cerdanyola del Vallès": 9, "Cervera": 95,
    "Collbató": 30, "Corbera de Llobregat": 19, "Cornellà de Llobregat": 21,
    "El Bruc": 38, "El Papiol": 12, "El Vendrell": 55,
    "Esparreguera": 29, "Esplugues de Llobregat": 17,
    "Figueres": 135, "Gavà": 26, "Gelida": 35, "Girona": 100,
    "Granollers": 32, "Igualada": 52,
    "La Garriga": 38, "La Pobla de Claramunt": 52, "La Seu d'Urgell": 152,
    "Lleida": 152, "Lloret de Mar": 82, "L'Hospitalet de Llobregat": 22,
    "Manresa": 62, "Martorell": 23, "Masquefa": 38, "Mataró": 44,
    "Molins de Rei": 11, "Mollet del Vallès": 22, "Mollerussa": 140,
    "Montblanc": 100, "Montcada i Reixac": 16, "Montserrat": 35,
    "Olesa de Montserrat": 30, "Olot": 112,
    "Palafrugell": 118, "Palamós": 120, "Parets del Vallès": 24,
    "Piera": 42, "Pineda de Mar": 55, "Premià de Mar": 40, "Puigcerdà": 133,
    "Reus": 117, "Ribes de Freser": 120, "Ripoll": 105, "Ripollet": 13,
    "Roses": 155, "Rubí": 8,
    "Sabadell": 20, "Salou": 122,
    "Sant Andreu de la Barca": 17, "Sant Boi de Llobregat": 25,
    "Sant Cugat del Vallès": 0, "Sant Feliu de Guíxols": 112,
    "Sant Joan Despí": 19, "Sant Quirze del Vallès": 6,
    "Sant Sadurní d'Anoia": 42, "Santa Coloma de Gramenet": 28,
    "Santa Coloma de Queralt": 80, "Sitges": 36, "Sort": 185,
    "Subirats": 40, "Tarragona": 112, "Terrassa": 17, "Tortosa": 162,
    "Tossa de Mar": 91, "Tremp": 162,
    "Ulldecona": 195, "Valls": 90, "Vic": 67,
    "Vilafranca del Penedès": 42, "Vilanova i la Geltrú": 43,
    # EMDs i municipis addicionals
    "Valldoreix": 3, "Les Planes": 5, "La Floresta": 4,
    "Lliçà d'Amunt": 30, "Lliçà de Vall": 28,
    "Palau-solità i Plegamans": 22, "Polinyà": 18,
    "Santa Perpètua de Mogoda": 19, "Sentmenat": 20,
    "Caldes de Montbui": 30, "Sant Feliu de Codines": 35,
    "Castellterçol": 44, "Moià": 52, "Sant Quirze Safaja": 38,
    "Sant Just Desvern": 18, "Sant Vicenç dels Horts": 23,
    "Cervelló": 23, "Vallirana": 26, "Begues": 31,
    "Avinyonet del Penedès": 38, "Sant Pere de Ribes": 45,
    "Cubelles": 50, "Cunit": 52,
    "Canovelles": 30, "Cardedeu": 37,
    "Les Franqueses del Vallès": 33, "Montmeló": 22,
    "Montornès del Vallès": 24, "Tagamanent": 48,
    "Sant Antoni de Vilamajor": 40, "Sant Pere de Vilamajor": 42,
    "Bigues i Riells": 35, "Caldes d'Estrac": 46,
    "Aiguafreda": 46, "Figaró-Montmany": 50,
    "Sant Esteve de Palautordera": 44, "Santa Maria de Palautordera": 46,
    "Fogars de la Selva": 65, "Hostalric": 68,
    "Llinars del Vallès": 38, "Vallgorguina": 44,
    "Sant Celoni": 50, "Gualba": 52,
    "Sarrià de Ter": 100, "Sant Gregori": 103,
}
KM_PER_DEFECTE = 25  # si no es troba el municipi


def calcular_km(municipi):
    if not municipi:
        return 0
    nom = municipi.strip()
    if nom in MUNICIPIS_KM:
        return MUNICIPIS_KM[nom]
    nom_l = nom.lower()
    for k, v in MUNICIPIS_KM.items():
        if nom_l in k.lower():
            return v
    return KM_PER_DEFECTE


def derivar_variables(data):
    """Deriva variables tècniques de les respostes del qüestionari de vida."""
    m2      = float(data.get('m2', 160))
    plantes = str(data.get('plantes', '2'))
    banys   = int(data.get('num_banys', 2))

    # ── Variables calculades internament ───────────────────────────────────
    m2_paviment     = round(m2 * 0.91)                         # 91% superfície útil
    num_portes      = max(4, round(m2 / 22)) + banys           # ~1/22m² + 1 per bany
    m2_fonamentacio = m2                                        # coherent amb referència doc
    escala          = plantes != '1'                            # auto: >1 planta → escala

    # ── Finestres ← prioritat energètica ──────────────────────────────────
    energia = data.get('energia_prioritat', 'equilibri')
    finestres = {
        'max_eficiencia': 'ventaclimVMM74',
        'equilibri':      'ecovenS82',
        'confort':        'ecovenS70',
    }.get(energia, 'ecovenS82')

    # ── Aerotèrmia ← sistema climatització ────────────────────────────────
    clima     = data.get('climatitzacio', 'acs')
    aerotermia = {'total': 'acs_calefaccio', 'acs': 'acs', 'no': 'cap'}.get(clima, 'acs')

    # ── Zehnder ← qualitat de l'aire ──────────────────────────────────────
    zehnder = data.get('qualitat_aire', 'bona') == 'excel_lent'

    # ── Krona ← nivell d'acabat ────────────────────────────────────────────
    krona = data.get('estil_acabats', 'alta_qualitat') == 'exclusiu'

    # ── Garatge ───────────────────────────────────────────────────────────
    garatge_resp = data.get('garatge', 'no')
    garatge      = garatge_resp not in ('no', '', None, False)
    m2_garatge   = float(data.get('m2_garatge', 0)) if garatge else 0.0

    # ── Pòrxos ────────────────────────────────────────────────────────────
    porxos_resp = data.get('porxos', 'no')
    porxos      = porxos_resp not in ('no', '', None, False)
    m2_porxos   = float(data.get('m2_porxos', 0)) if porxos else 0.0

    # ── Km ← municipi ─────────────────────────────────────────────────────
    municipi = data.get('municipi', '')
    km       = calcular_km(municipi)

    return dict(
        m2=m2, plantes=plantes, num_banys=banys,
        m2_paviment=m2_paviment, num_portes=num_portes,
        m2_fonamentacio=m2_fonamentacio, escala=escala,
        finestres=finestres, aerotermia=aerotermia,
        zehnder=zehnder, krona=krona,
        garatge=garatge, m2_garatge=m2_garatge,
        porxos=porxos, m2_porxos=m2_porxos,
        km=km, municipi=municipi,
        energia_prioritat=energia,
        climatitzacio=clima,
        qualitat_aire=data.get('qualitat_aire', 'important'),
        estil_acabats=data.get('estil_acabats', 'alta_qualitat'),
    )


def calculate_budget(data):
    v = derivar_variables(data)
    m2              = v['m2']
    plantes         = v['plantes']
    num_banys       = v['num_banys']
    m2_paviment     = v['m2_paviment']
    num_portes      = v['num_portes']
    m2_fonamentacio = v['m2_fonamentacio']
    escala          = v['escala']
    finestres       = v['finestres']
    aerotermia      = v['aerotermia']
    zehnder         = v['zehnder']
    krona           = v['krona']
    garatge         = v['garatge']
    m2_garatge      = v['m2_garatge']
    porxos          = v['porxos']
    m2_porxos       = v['m2_porxos']
    km              = v['km']

    # Preus finestres (€/m² de finestra)
    preu_finestres      = {'ecovenS70': 18.53, 'ecovenS82': 22.00,
                           'ventaclimVMM74': 28.00, 'ventaclimSupercomfort': 35.00
                           }.get(finestres, 18.53)
    preu_base_finestres = 18.53

    # ── Pack Envolvent Tèrmic ──────────────────────────────────────────────
    rate = {'1': 820.0, '2': 984.4}.get(plantes, 1050.0)
    m2_finestres       = m2 * 0.109
    suplement_finestres = (preu_finestres - preu_base_finestres) * m2_finestres
    cost_porta_entrada  = 2245.00
    cost_grua           = 450.00
    base_variable       = rate * m2
    cost_estructura     = base_variable * 0.546
    cost_coberta        = base_variable * 0.312
    cost_finestres      = base_variable * 0.142 + suplement_finestres
    pack_envolvent      = base_variable + suplement_finestres + cost_porta_entrada + cost_grua

    # ── Pack Instal·lacions ────────────────────────────────────────────────
    cost_teleco        = 1989.00
    cost_sanejament    = 1621.00
    cost_electricitat  = 48.0 * m2
    cost_agua          = 37.5 * m2
    cost_escomeses     = 8578.00
    cost_ventilacio    = 1985.00
    cost_zehnder       = 8910.00 if zehnder else 0.0
    cost_aerotermia    = {'acs': 2870.00, 'acs_calefaccio': 10976.00}.get(aerotermia, 0.0)
    pack_installacions = (cost_teleco + cost_sanejament + cost_electricitat + cost_agua
                          + cost_escomeses + cost_ventilacio + cost_zehnder + cost_aerotermia)

    # ── Pack Parking i Exteriors ───────────────────────────────────────────
    cost_porta_peatonal    = 544.00 if garatge else 0.0
    cost_porta_motoritzada = 2850.00 if garatge else 0.0
    cost_garatge_estructura = 998.0 * m2_garatge
    cost_porxos_calc        = 577.0 * m2_porxos
    pack_parking = (cost_porta_peatonal + cost_porta_motoritzada
                    + cost_garatge_estructura + cost_porxos_calc)

    # ── Pack Acabats Interiors ─────────────────────────────────────────────
    cost_pintura          = 19.5 * m2
    cost_pladur           = 99.0 * m2
    cost_cuina            = 61.2 * m2
    cost_paviments        = 49.0 * m2_paviment
    cost_portes_interiors = 495.0 * num_portes
    cost_krona            = 245.0 * num_portes if krona else 0.0
    cost_banys            = 3952.62 * num_banys
    cost_escala           = 3423.0 if escala else 0.0
    pack_acabats = (cost_pintura + cost_pladur + cost_cuina + cost_paviments
                    + cost_portes_interiors + cost_krona + cost_banys + cost_escala)

    # ── Transport ──────────────────────────────────────────────────────────
    cost_transport = 95.0 * km

    # ── Totals ────────────────────────────────────────────────────────────
    total_construccio  = pack_envolvent + pack_installacions + pack_parking + pack_acabats + cost_transport
    cost_projecte      = 0.0 if data.get('te_projecte') else total_construccio * 0.105
    cost_seguretat     = total_construccio * 0.02
    cost_fonamentacio  = 396.0 * m2_fonamentacio
    total_contractacio = cost_projecte + cost_seguretat + cost_fonamentacio
    total_sense_iva    = total_construccio + total_contractacio
    iva                = total_sense_iva * 0.10
    total_pressupost   = total_sense_iva + iva

    today    = date.today()
    validesa = today + timedelta(days=30)
    r = lambda x: round(x, 2)

    # Etiquetes amigables
    finestres_labels = {
        'ecovenS70':           'EcoVen S-70 PVC (estàndard)',
        'ecovenS82':           'EcoVen S-82 (alt rendiment)',
        'ventaclimVMM74':      'Ventaclim VMM-74 (Passivhaus)',
        'ventaclimSupercomfort': 'Ventaclim Supercomfort',
    }
    aerotermia_labels = {
        'cap':           'No inclosa',
        'acs':           'Aerotèrmia ACS',
        'acs_calefaccio': 'Aerotèrmia ACS + Calefacció',
    }

    return {
        'variables_derivades': {
            'te_projecte':            bool(data.get('te_projecte')),
            'municipi':               v['municipi'],
            'km_transport':           km,
            'm2_paviment_calculat':   m2_paviment,
            'num_portes_calculat':    num_portes,
            'm2_fonamentacio_calculat': m2_fonamentacio,
            'finestres_label':        finestres_labels.get(finestres, finestres),
            'aerotermia_label':       aerotermia_labels.get(aerotermia, aerotermia),
            'zehnder':                zehnder,
            'escala':                 escala,
            'krona':                  krona,
        },
        'pack_envolvent': {
            'finestres':         r(cost_finestres),
            'estructura_vertical': r(cost_estructura),
            'coberta_forjats':   r(cost_coberta),
            'porta_entrada':     r(cost_porta_entrada),
            'grua':              r(cost_grua),
            'total':             r(pack_envolvent),
        },
        'pack_installacions': {
            'telecomunicacions':       r(cost_teleco),
            'sanejament_interior':     r(cost_sanejament),
            'electricitat_interior':   r(cost_electricitat),
            'agua_interior':           r(cost_agua),
            'escomeses':               r(cost_escomeses),
            'preinstallacio_ventilacio': r(cost_ventilacio),
            'zehnder':                 r(cost_zehnder),
            'aerotermia':              r(cost_aerotermia),
            'total':                   r(pack_installacions),
        },
        'pack_parking': {
            'porta_peatonal':    r(cost_porta_peatonal),
            'porta_motoritzada': r(cost_porta_motoritzada),
            'garatge_estructura': r(cost_garatge_estructura),
            'porxos_terrasses':  r(cost_porxos_calc),
            'total':             r(pack_parking),
        },
        'pack_acabats': {
            'pintura':           r(cost_pintura),
            'pladur':            r(cost_pladur),
            'cuina':             r(cost_cuina),
            'paviments':         r(cost_paviments),
            'portes_interiors':  r(cost_portes_interiors),
            'estructura_krona':  r(cost_krona),
            'banys':             r(cost_banys),
            'escala':            r(cost_escala),
            'total':             r(pack_acabats),
        },
        'transport':           r(cost_transport),
        'total_construccio':   r(total_construccio),
        'contractacio_externa': {
            'projecte_arquitectonic': r(cost_projecte),
            'seguretat_salut':        r(cost_seguretat),
            'fonamentacio':           r(cost_fonamentacio),
            'total':                  r(total_contractacio),
        },
        'total_sense_iva':  r(total_sense_iva),
        'iva':              r(iva),
        'total_pressupost': r(total_pressupost),
        'data_emissio':     today.strftime('%d/%m/%Y'),
        'data_validesa':    validesa.strftime('%d/%m/%Y'),
    }


# ── Anàlisi de plànols amb GPT-4o Vision — Pipeline optimitzat ───────────────
# Configura la clau API abans d'iniciar el servidor:
#   export OPENAI_API_KEY="sk-proj-..."
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Factor de conversió sq ft → m²
SQ_FT_TO_M2 = 0.09290304


# ── STEP 1: Neteja de text PDF ────────────────────────────────────────────────

def _clean_pdf_text(text):
    """Neteja text extret de PDF amb codificació defectuosa o caràcters repetits."""
    if not text:
        return ''
    # Eliminar patrons de caràcters repetits anòmals (AAAA, BBBB...)
    text = re.sub(r'(.)\1{4,}', r'\1', text)
    # Eliminar caràcters no imprimibles (excepte whitespace normal)
    text = re.sub(r'[^\x20-\x7E\xA0-\xFF\n\r\t]', ' ', text)
    # Col·lapsar espais múltiples (però preservar salts de línia)
    text = re.sub(r'[ \t]{3,}', ' ', text)
    return text.strip()


# ── STEP 2: Detecció de taules d'àrea ────────────────────────────────────────

def _extract_areas_from_text(text):
    """
    Extreu valors d'àrea del text d'una pàgina PDF.
    Retorna llista de dicts: {'value': float, 'unit': 'm2'|'sqft', 'context': str}
    """
    areas = []
    if not text:
        return areas

    # Patrons en m² (CA / ES / EN)
    m2_patterns = [
        r'(\d[\d\s.,]{0,8})\s*m[²2]',
        r'(?:superfici[ea]|àrea|area|total|construïda?|construida?|habitable)'
        r'[^\d]{0,40}(\d[\d.,]{1,6})\s*m',
        r'm[²2]\s*[:\-–]?\s*(\d[\d.,]{1,6})',
    ]
    for pat in m2_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            try:
                val_str = m.group(1).replace(' ', '').replace(',', '.')
                val = float(val_str)
                if 30 < val < 5000:
                    ctx = text[max(0, m.start() - 40):m.end() + 40].strip()
                    areas.append({'value': val, 'unit': 'm2', 'context': ctx})
            except Exception:
                pass

    # Patrons en sq ft / SF (EN)
    sqft_patterns = [
        r'(\d[\d,]{1,6})\s*(?:sq\.?\s*ft\.?|SF|square\s*fe?e?t)',
        r'(?:area|floor|total|living|gross)[^\d]{0,40}(\d[\d,]{1,6})\s*(?:sq\.?\s*ft\.?|SF)',
        r'(?:sq\.?\s*ft\.?|SF)\s*[:\-–]?\s*(\d[\d,]{1,6})',
    ]
    for pat in sqft_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            try:
                val_str = m.group(1).replace(',', '')
                val = float(val_str)
                if 300 < val < 54000:  # 28 m² – 5000 m² en sq ft
                    ctx = text[max(0, m.start() - 40):m.end() + 40].strip()
                    areas.append({'value': val, 'unit': 'sqft', 'context': ctx})
            except Exception:
                pass

    return areas


# ── STEP 3: Conversió imperial → mètric ──────────────────────────────────────

def _sqft_to_m2(sqft_value):
    """Converteix sq ft a m² (arrodonit a 1 decimal)."""
    return round(sqft_value * SQ_FT_TO_M2, 1)


def _best_area_from_texts(page_texts):
    """
    Busca el valor d'àrea total més fiable en tots els textos de les pàgines.
    Retorna {'value_m2': float, 'context': str} o None.
    """
    candidates = []
    for txt in page_texts:
        for a in _extract_areas_from_text(txt):
            v_m2 = a['value'] if a['unit'] == 'm2' else _sqft_to_m2(a['value'])
            if 50 < v_m2 < 1500:
                candidates.append({'value_m2': v_m2, 'context': a['context'],
                                    'unit': a['unit'], 'raw': a['value']})
    if not candidates:
        return None
    # Preferir el valor més gran raonable (sol ser el total construït)
    return max(candidates, key=lambda c: c['value_m2'])


# ── STEP 4: Puntuació i selecció de pàgines ──────────────────────────────────

def _score_pdf_page(text):
    """
    Puntua una pàgina PDF per rellevància arquitectònica.
    Versió millorada: multilingüe (CA/ES/EN), detecta taules d'àrea, cotes.
    """
    score = 0
    t = text or ''
    t_low = t.lower()

    # ── Plantes habilitades ───────────────────────────────────────────────────
    floor_kws = [
        'planta baixa', 'planta primera', 'planta segunda', 'planta pis',
        'ground floor', 'first floor', 'second floor', 'floor plan',
        'floor layout', 'pb', 'p1', 'p2', 'plante', 'plano',
    ]
    for kw in floor_kws:
        if kw in t_low:
            score += 6
            break
    if 'acotada' in t_low or 'dimensioned' in t_low or 'cotat' in t_low:
        score += 10  # planta amb cotes → prioritat màxima

    # ── Àrea / superfície explícita ───────────────────────────────────────────
    area_kws = [
        'superfície', 'superficie', 'àrea', 'area', 'm²', 'm2',
        'sq ft', 'sqft', 'square feet', 'square foot',
        'total area', 'floor area', 'gross area', 'living area',
        'habitable', 'útil', 'construïda', 'construida',
    ]
    area_hit = any(kw in t_low for kw in area_kws)
    # Detectar "SF" com a unitat (amb word boundary per evitar falsos positius)
    if not area_hit and re.search(r'\bSF\b', t):
        area_hit = True
    # Sempre intentar extreure àrees numèriques (independentment de paraules clau)
    areas = _extract_areas_from_text(t)
    if area_hit:
        score += 6
    if areas:
        score += 12  # taula d'àrees amb valors numèrics → prioritat màxima

    # ── Estances i espais (indicadors de planta) ──────────────────────────────
    room_kws = [
        'bany', 'wc', 'lavabo', 'toilet', 'bathroom', 'bath', 'aseo',
        'garatge', 'garaje', 'garage', 'parking', 'aparcament',
        'porxo', 'porche', 'porch', 'terrassa', 'terraza',
        'dormitori', 'habitació', 'bedroom', 'living', 'sala', 'cuina',
        'kitchen', 'dining', 'study', 'office', 'despacho',
    ]
    rooms = sum(1 for kw in room_kws if kw in t_low)
    score += min(rooms * 2, 14)

    # ── Dimensions numèriques (cotes) ─────────────────────────────────────────
    dim_count = len(re.findall(r'\b\d+[.,]\d{2}\b', t))       # 3.50 / 4,20
    dim_count += len(re.findall(r"\b\d+'\s*\d+\"\s*", t))     # 12'6"
    score += min(dim_count // 2, 10)

    # ── Penalitzar pàgines no rellevants ──────────────────────────────────────
    penalty_kws = [
        'elevation', 'alçat', 'façana', 'fachada', 'section', 'secció',
        'detail', 'detall', 'detalle', 'notes', 'specifications',
        'cover', 'portada', 'title', 'index', 'índex', 'índice',
        'photograph', 'location', 'situació', 'urbanization',
        'schedule of finishes', 'acabados',
    ]
    for kw in penalty_kws:
        if kw in t_low:
            score -= 3

    return score


def _best_pdf_pages(raw_bytes, max_pages=4):
    """
    Selecciona les pàgines més rellevants d'un PDF arquitectònic.
    Retorna (page_numbers_1indexed, page_texts).
    """
    try:
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            total = len(pdf.pages)
            page_texts = {}
            scored = []
            for i, page in enumerate(pdf.pages):
                raw_text = page.extract_text() or ''
                clean = _clean_pdf_text(raw_text)
                page_texts[i + 1] = clean
                scored.append((_score_pdf_page(clean), i + 1))

            if total <= max_pages:
                nums = list(range(1, total + 1))
                return nums, [page_texts[n] for n in nums]

            scored.sort(reverse=True)
            best_nums = sorted([p for _, p in scored[:max_pages]])
            return best_nums, [page_texts[n] for n in best_nums]
    except Exception:
        return list(range(1, max_pages + 1)), [''] * max_pages


# ── STEP 5: Validació del resultat ───────────────────────────────────────────

def _validate_extraction(extracted, page_texts=None):
    """
    Valida i corregeix l'extracció de GPT-4o:
    - Comprova rangs raonables
    - Detecta possibles confusions d'unitats (sq ft → m²)
    - Fallback: intenta recuperar m² del text extret si GPT no el va trobar
    - Ajusta la confiança si hi ha inconsistències
    """
    if not isinstance(extracted, dict):
        return extracted

    m2         = extracted.get('m2')
    floors     = extracted.get('floors')
    bathrooms  = extracted.get('num_bathrooms')
    confidence = float(extracted.get('confidence', 0.5))
    issues     = []

    # ── Validació m² ─────────────────────────────────────────────────────────
    if m2 is not None:
        # Llindar: habitatge unifamiliar PAPIK → màxim ~700 m²
        # Valors > 700 probablement sq ft sense convertir (700 m² = ~7535 SF)
        if m2 > 700:
            converted = _sqft_to_m2(m2)
            if 50 < converted < 800:
                extracted['m2'] = converted
                extracted['_auto_converted'] = (
                    f'Convertit automàticament de {m2:.0f} sq ft → {converted} m²'
                )
                confidence = max(0.0, confidence - 0.10)
                issues.append('auto_sqft_conversion')
            else:
                confidence = max(0.0, confidence - 0.30)
                issues.append('m2_too_large')
        elif m2 < 25:
            confidence = max(0.0, confidence - 0.30)
            issues.append('m2_too_small')

    # ── Validació floors ─────────────────────────────────────────────────────
    if floors is not None and (floors < 1 or floors > 4):
        confidence = max(0.0, confidence - 0.20)
        issues.append('floors_out_of_range')

    # ── Validació banys ──────────────────────────────────────────────────────
    if bathrooms is not None and (bathrooms < 1 or bathrooms > 8):
        confidence = max(0.0, confidence - 0.20)
        issues.append('bathrooms_out_of_range')

    # ── Cross-check m² / plantes ─────────────────────────────────────────────
    if m2 is not None and floors is not None and floors > 0:
        m2_per_floor = extracted.get('m2', m2) / floors
        if m2_per_floor > 600:
            confidence = max(0.0, confidence - 0.15)
            issues.append('high_m2_per_floor')
        elif m2_per_floor < 20:
            confidence = max(0.0, confidence - 0.20)
            issues.append('low_m2_per_floor')

    # ── Fallback: recuperar m² del text si GPT no el va trobar ───────────────
    if extracted.get('m2') is None and page_texts:
        best = _best_area_from_texts(page_texts)
        if best:
            extracted['m2'] = best['value_m2']
            extracted['_text_fallback'] = (
                f"m² recuperat del text PDF: '{best['context']}'"
                + (f" ({best['raw']:.0f} sq ft)" if best['unit'] == 'sqft' else '')
            )
            confidence = max(0.3, confidence - 0.05)
            issues.append('m2_from_text_fallback')

    extracted['confidence'] = round(max(0.0, min(1.0, confidence)), 2)
    if issues:
        extracted['_validation_issues'] = issues
    return extracted


# ── Prompt multilingüe per a GPT-4o Vision ───────────────────────────────────

PROMPT_PLANS = """You are an expert residential architectural plan reader.
You receive 1–4 images from the SAME single-family house project (floor plans, sections, elevations, area schedules, cover sheets).
Your task: extract technical data and return ONLY a valid JSON object. No explanations, no markdown.

═══ EXTRACTION RULES ═══

1. TOTAL AREA (m²) — use this priority:
   a. Explicit total built / gross / living area in title blocks or area schedule tables.
   b. Sum of per-floor areas if listed.
   c. Visual estimate from exterior dimensions × number of habitable floors.
   → If area is given in sq ft or SF, convert: 1 sq ft = 0.092903 m². Return ONLY m².

2. HABITABLE FLOORS — count only livable floors:
   ✔ Ground / first floor (Planta Baixa / PB) / second floor / basement (if habitable)
   ✗ Roof plan, attic access, crawl space, foundation plan
   → If you only see ONE floor plan (e.g., only Planta Baixa / Ground Floor), return floors=1.
   → If you see TWO separate floor plans, return floors=2. Etc.

3. BATHROOMS — count every space with toilet/shower/tub/sink:
   bathroom · bath · WC · toilet · lavabo · bany · aseo · ensuite · half-bath · powder room
   Use room labels AND sanitary fixture symbols.

4. GARAGE — apply this logic:
   → If the plan clearly shows a garage / garatge / garaje / parking / vehicle bay: return true.
   → If you have examined the plan and there is NO garage visible: return false.
   → Return null ONLY if the plan quality makes it genuinely impossible to determine.
   Estimate area if not explicit but garage is present.

5. PORCHES / COVERED TERRACES — apply this logic:
   → If the plan clearly shows a covered outdoor area (porch · porxo · porche · covered terrace · covered deck): return true.
   → If you have examined the plan and there are NO covered outdoor areas: return false.
   → Return null ONLY if genuinely impossible to determine.
   Estimate area if present but not labelled.

6. CONFIDENCE — 0.0–1.0:
   · 0.9–1.0 → explicit values in title block / schedule
   · 0.6–0.8 → values readable in drawing but not in summary table
   · 0.3–0.5 → estimated from dimensions or symbols
   · 0.1–0.2 → very uncertain

7. NULL rule — use null ONLY when you truly cannot make a determination.
   For boolean fields (garage, porches), prefer false over null when the element is clearly absent.

═══ OUTPUT — return ONLY this JSON ═══
{
  "m2": <number or null>,
  "floors": <integer or null>,
  "num_bathrooms": <integer or null>,
  "garage": <true | false | null>,
  "m2_garage": <number or null>,
  "porches": <true | false | null>,
  "m2_porches": <number or null>,
  "source_area": {
    "value": <number or null>,
    "unit": <"m2" | "sqft" | null>,
    "source_text": <string describing where you found it, or null>
  },
  "confidence": <number 0.0–1.0>
}
"""


# ── Endpoint: /analitzar-plans ────────────────────────────────────────────────

@app.route('/analitzar-plans', methods=['POST'])
def analitzar_plans():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify({'error': 'OPENAI_API_KEY no configurada al servidor. '
                                 'Executa: export OPENAI_API_KEY="sk-proj-..."'}), 503

    files = request.files.getlist('plans')
    if not files:
        return jsonify({'error': 'No s\'han rebut fitxers.'}), 400

    # Acumular totes les imatges i els textos extrets
    content_images = []
    all_page_texts = []

    for f in files[:3]:
        mime = f.mimetype or 'image/png'
        raw_bytes = f.read()

        if mime == 'application/pdf' or f.filename.lower().endswith('.pdf'):
            try:
                # STEP 4: seleccionar les millors pàgines (amb scoring millorat)
                best_pages, page_texts = _best_pdf_pages(raw_bytes, max_pages=4)
                all_page_texts.extend(page_texts)

                if HAS_PDF2IMAGE:
                    # Convertir les pàgines seleccionades a PNG a 200 DPI
                    all_images = convert_from_bytes(raw_bytes, dpi=200)
                    for page_num in best_pages:
                        if page_num <= len(all_images):
                            buf = io.BytesIO()
                            all_images[page_num - 1].save(buf, format='PNG')
                            b64 = base64.standard_b64encode(buf.getvalue()).decode('utf-8')
                            content_images.append({
                                'type': 'image_url',
                                'image_url': {'url': f'data:image/png;base64,{b64}',
                                              'detail': 'high'},
                            })
                # Si pdf2image no està disponible, utilitzem només el text extret
                # Les imatges PNG/JPG pujades directament sí que passen per Vision
            except Exception as e:
                # No aturar tot el procés si un PDF falla
                all_page_texts.append(f'[Error processant PDF: {e}]')
                continue

        elif mime in ('image/jpeg', 'image/png', 'image/gif', 'image/webp') \
                or f.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            b64 = base64.standard_b64encode(raw_bytes).decode('utf-8')
            content_images.append({
                'type': 'image_url',
                'image_url': {'url': f'data:{mime};base64,{b64}', 'detail': 'high'},
            })

    if not content_images and not all_page_texts:
        return jsonify({'error': 'Formats acceptats: PDF, PNG, JPG, WEBP.'}), 400

    # STEP 5a: construir el missatge — afegir context de text extret si n'hi ha
    text_context = ''
    if all_page_texts:
        combined = '\n---\n'.join(t for t in all_page_texts if t.strip())
        if combined.strip():
            # Limitar a 3000 caràcters per no inflar el context
            combined = combined[:3000]
            text_context = (
                f'\n\nEXTRACTED TEXT FROM PDF (use this to help identify areas, '
                f'room names and dimensions):\n"""\n{combined}\n"""'
            )

    prompt_with_context = PROMPT_PLANS + text_context
    content = [{'type': 'text', 'text': prompt_with_context}] + content_images

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model='gpt-4o',
            max_tokens=900,
            temperature=0,          # determinista per extracció de dades
            messages=[{'role': 'user', 'content': content}],
        )
        raw = response.choices[0].message.content.strip()

        # Eliminar blocs markdown ```json ... ``` si els hi ha
        if '```' in raw:
            parts = raw.split('```')
            raw = parts[1] if len(parts) > 1 else raw
            if raw.lower().startswith('json'):
                raw = raw[4:]
        raw = raw.strip()

        extracted = json.loads(raw)

        # STEP 5b: validació i correcció post-extracció
        extracted = _validate_extraction(extracted, page_texts=all_page_texts)

        # STEP 5c: mapar noms de camps anglès → català per compatibilitat amb el frontend
        FIELD_MAP = {
            'floors':       'plantes',
            'num_bathrooms':'num_banys',
            'garage':       'garatge',
            'm2_garage':    'm2_garatge',
            'porches':      'porxos',
            'm2_porches':   'm2_porxos',
        }
        mapped = {}
        for k, v in extracted.items():
            mapped[FIELD_MAP.get(k, k)] = v

        return jsonify(mapped)

    except json.JSONDecodeError:
        return jsonify({'error': 'No s\'ha pogut interpretar la resposta de la IA.'}), 500
    except openai.AuthenticationError:
        return jsonify({'error': 'Clau API OpenAI incorrecta.'}), 401
    except openai.RateLimitError:
        return jsonify({'error': 'Límit de la API d\'OpenAI assolit. Torna-ho a intentar.'}), 429
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ── Assessor Virtual PAPIK — Xat amb context del pressupost ──────────────────

def _format_budget_for_context(budget_input, budget_result):
    """Formata el pressupost com a text estructurat per al context del chatbot."""
    lines = ['═══ PRESSUPOST PERSONALITZAT PAPIK ═══\n']

    m2        = budget_input.get('m2', '—')
    plantes   = budget_input.get('plantes', '—')
    num_banys = budget_input.get('num_banys', '—')
    municipi  = budget_input.get('municipi', '')

    lines.append(f'Superfície construïda: {m2} m²')
    if municipi:
        lines.append(f'Municipi: {municipi}')
    lines.append(f'Nombre de plantes: {plantes}')
    lines.append(f'Nombre de banys: {num_banys}')

    # Garatge i pòrxos
    garatge   = budget_input.get('garatge', False)
    m2_gar    = budget_input.get('m2_garatge', 0)
    porxos    = budget_input.get('porxos', False)
    m2_por    = budget_input.get('m2_porxos', 0)
    lines.append(f"Garatge: {'Sí (' + str(m2_gar) + ' m²)' if garatge else 'No'}")
    lines.append(f"Pòrxos/Terrassa coberta: {'Sí (' + str(m2_por) + ' m²)' if porxos else 'No'}")

    # Sistemes i acabats
    energia_labels = {
        'max_eficiencia': 'Màxima eficiència (Passivhaus)',
        'equilibri':      'Alt rendiment energètic',
        'confort':        'Qualitat estàndard',
    }
    clima_labels = {
        'total': 'ACS + Calefacció per aerotèrmia',
        'acs':   'ACS per aerotèrmia',
        'no':    'Sense aerotèrmia',
    }
    lines.append(f"Eficiència energètica: {energia_labels.get(budget_input.get('energia_prioritat','equilibri'), '—')}")
    lines.append(f"Climatització: {clima_labels.get(budget_input.get('climatitzacio','acs'), '—')}")
    if budget_input.get('qualitat_aire') == 'excel_lent':
        lines.append('Sistema Zehnder (recuperació de calor): Inclòs')
    if budget_input.get('estil_acabats') == 'exclusiu':
        lines.append("Acabats: Disseny d'interiors personalitzat (Krona)")
    if budget_input.get('te_projecte'):
        lines.append("Projecte arquitectònic: Propi (honoraris no inclosos al pressupost)")

    # Desglossament econòmic
    if budget_result:
        vd  = budget_result.get('variables_derivades', {})
        pe  = budget_result.get('pack_envolvent', {})
        pi  = budget_result.get('pack_installacions', {})
        pp  = budget_result.get('pack_parking', {})
        pa  = budget_result.get('pack_acabats', {})
        ce  = budget_result.get('contractacio_externa', {})
        fmt = lambda x: f"{float(x):,.0f} €" if x else '0 €'

        lines.append(f"\n─── DESGLOSSAMENT DE COSTOS ───")
        lines.append(f"Finestres seleccionades: {vd.get('finestres_label','—')}")
        lines.append(f"Aerotèrmia: {vd.get('aerotermia_label','—')}")
        lines.append(f"Km de transport des de fàbrica: {vd.get('km_transport','—')} km")
        lines.append(f"\nPack Envolvent Tèrmic:     {fmt(pe.get('total',0))}")
        lines.append(f"  Estructura vertical:      {fmt(pe.get('estructura_vertical',0))}")
        lines.append(f"  Coberta i forjats:        {fmt(pe.get('coberta_forjats',0))}")
        lines.append(f"  Finestres:                {fmt(pe.get('finestres',0))}")
        lines.append(f"  Porta d'entrada:          {fmt(pe.get('porta_entrada',0))}")
        lines.append(f"  Grua de muntatge:         {fmt(pe.get('grua',0))}")
        lines.append(f"\nPack Instal·lacions:       {fmt(pi.get('total',0))}")
        lines.append(f"  Electricitat:             {fmt(pi.get('electricitat_interior',0))}")
        lines.append(f"  Fontaneria:               {fmt(pi.get('agua_interior',0))}")
        lines.append(f"  Sanejament:               {fmt(pi.get('sanejament_interior',0))}")
        lines.append(f"  Escomeses:                {fmt(pi.get('escomeses',0))}")
        lines.append(f"  Aerotèrmia:               {fmt(pi.get('aerotermia',0))}")
        lines.append(f"  Sistema Zehnder:          {fmt(pi.get('zehnder',0))}")
        lines.append(f"\nPack Parking i Exteriors:  {fmt(pp.get('total',0))}")
        lines.append(f"\nPack Acabats Interiors:    {fmt(pa.get('total',0))}")
        lines.append(f"  Banys:                    {fmt(pa.get('banys',0))}")
        lines.append(f"  Cuina:                    {fmt(pa.get('cuina',0))}")
        lines.append(f"  Paviments:                {fmt(pa.get('paviments',0))}")
        lines.append(f"  Portes interiors:         {fmt(pa.get('portes_interiors',0))}")
        lines.append(f"\nTransport:                 {fmt(budget_result.get('transport',0))}")
        lines.append(f"\nHonoraris i Gestió Tècnica:{fmt(ce.get('total',0))}")
        lines.append(f"  Projecte arquitectònic:   {fmt(ce.get('projecte_arquitectonic',0))}")
        lines.append(f"  Seguretat i salut:        {fmt(ce.get('seguretat_salut',0))}")
        lines.append(f"  Fonamentació:             {fmt(ce.get('fonamentacio',0))}")
        lines.append(f"\nSubtotal sense IVA:        {fmt(budget_result.get('total_sense_iva',0))}")
        lines.append(f"IVA (10%):                 {fmt(budget_result.get('iva',0))}")
        lines.append(f"TOTAL PRESSUPOST AMB IVA:  {fmt(budget_result.get('total_pressupost',0))}")
        lines.append(f"Vàlid fins: {budget_result.get('data_validesa','—')}")

    return '\n'.join(lines)


# ── DocsGPT — Assessor Virtual amb memòria de qualitats ─────────────────────
# L'agent DocsGPT ja coneix la memòria de qualitats de PAPIK.
# Injectem el context del pressupost en cada conversa via el camp "history".
# Arquitectura SENSE base de dades ni sessions:
#   - L'historial de conversa viu al navegador (advisorChatHistory al JS)
#   - Cada petició envia tot l'historial + el context del pressupost
#   - El servidor és completament stateless

DOCSGPT_API_KEY = 'c16cbd85-1244-4d97-a866-8e2ce99fc914'
DOCSGPT_URL     = 'https://gptcloud.arc53.com/api/answer'


@app.route('/chat-pressupost', methods=['POST'])
def chat_pressupost():
    """
    Endpoint de xat per a l'Assessor Virtual PAPIK via DocsGPT.

    Gestió de context:
    - Primer missatge (sense conversation_id): injectem el context del pressupost
      com a prefix de la pregunta. DocsGPT crea una nova conversa i retorna
      un conversation_id que el frontend guardarà.
    - Missatges posteriors: enviem només la pregunta + conversation_id.
      DocsGPT manté l'historial al seu costat (servidor DocsGPT és stateful,
      el nostre backend és stateless).
    """
    payload          = request.get_json() or {}
    user_message     = (payload.get('message') or '').strip()
    conversation_id  = payload.get('conversation_id')   # None en el primer missatge
    budget_input     = payload.get('budget_input', {})
    budget_result    = payload.get('budget_result', {})

    if not user_message:
        return jsonify({'error': 'Missatge buit.'}), 400

    # Primera pregunta: afegir el context del pressupost com a prefix
    if not conversation_id:
        budget_context = _format_budget_for_context(budget_input, budget_result)
        full_question = (
            f"[CONTEXT DEL PRESSUPOST PERSONALITZAT DEL CLIENT]\n"
            f"{budget_context}\n\n"
            f"[PREGUNTA DEL CLIENT]\n{user_message}"
        )
    else:
        full_question = user_message

    docsgpt_payload = {
        'question': full_question,
        'api_key':  DOCSGPT_API_KEY,
    }
    if conversation_id:
        docsgpt_payload['conversation_id'] = conversation_id

    try:
        resp = http.post(DOCSGPT_URL, json=docsgpt_payload, timeout=45)
        data = resp.json() if resp.ok else {}
        answer  = data.get('answer') or "No s'ha pogut obtenir resposta de l'agent."
        new_cid = data.get('conversation_id')
        return jsonify({'answer': answer, 'conversation_id': new_cid})

    except http.exceptions.Timeout:
        return jsonify({'error': "Temps d'espera exhaurit. Torna-ho a intentar."}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chat-configurador', methods=['POST'])
def chat_configurador():
    """
    Endpoint del Guia de Configuració PAPIK.

    Assistent contextual que acompanya l'usuari durant el procés de configuració
    (steps 1-4). Reutilitza el mateix DocsGPT (mateixa API key), però amb un
    context diferent: l'estat actual de la configuració en lloc del pressupost.

    Arquitectura idèntica a /chat-pressupost:
    - Primer missatge: injecta context de configuració com a prefix
    - Missatges posteriors: envia conversation_id; DocsGPT manté l'historial
    """
    payload         = request.get_json() or {}
    user_message    = (payload.get('message') or '').strip()
    conversation_id = payload.get('conversation_id')
    step            = payload.get('step', 1)
    config_state    = payload.get('config_state', {})

    if not user_message:
        return jsonify({'error': 'Missatge buit.'}), 400

    if not conversation_id:
        config_context = _format_config_context(step, config_state)
        full_question  = (
            f"[CONTEXT DE CONFIGURACIÓ — PAS {step}]\n"
            f"{config_context}\n\n"
            f"[PREGUNTA DE L'USUARI]\n{user_message}"
        )
    else:
        full_question = user_message

    docsgpt_payload = {'question': full_question, 'api_key': DOCSGPT_API_KEY}
    if conversation_id:
        docsgpt_payload['conversation_id'] = conversation_id

    # Regex extraction from user message (runs instantly)
    regex_updates = _extract_form_from_message(user_message, step)

    try:
        resp    = http.post(DOCSGPT_URL, json=docsgpt_payload, timeout=45)
        data    = resp.json() if resp.ok else {}
        answer  = data.get('answer') or "No s'ha pogut obtenir resposta de l'agent."
        new_cid = data.get('conversation_id')

        # Try to extract form data from the DocsGPT answer
        answer, ai_updates = _extract_form_from_answer(answer)

        # Merge: AI extraction takes priority, regex fills gaps
        form_updates = {**regex_updates, **ai_updates}

        # Validate municipi against known list
        if 'municipi' in form_updates and 'km' not in form_updates:
            nom = form_updates['municipi']
            matched, km = _match_municipi(nom)
            if matched:
                form_updates['municipi'] = matched
                form_updates['km'] = km
            else:
                del form_updates['municipi']

        return jsonify({
            'answer': answer,
            'conversation_id': new_cid,
            'form_updates': form_updates if form_updates else None,
        })

    except http.exceptions.Timeout:
        return jsonify({'error': "Temps d'espera exhaurit. Torna-ho a intentar."}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _format_config_context(step, config_state):
    """
    Formata l'estat actual de la configuració com a text per al Guia.
    Inclou una persona explícita perquè DocsGPT actuï com a guia de configuració.
    """
    step_names = {1: 'Parcel·la', 2: 'L\'Habitatge', 3: 'Confort', 4: 'Acabats'}
    step_name  = step_names.get(step, f'Pas {step}')

    d = config_state or {}

    lines = [
        "Ets el Guia Virtual de PAPIK, l'empresa que dissenya i construeix cases "
        "sostenibles de fusta. Acompanyes l'usuari mentre configura la seva futura llar.",
        "Personalitat: amable, calmat, intel·ligent, respostes curtes (2-4 frases). "
        "No siguis intrusiu. Si la pregunta és tècnica, explica de forma senzilla sense tecnicismes.",
        "",
        f"Pas actual de la configuració: {step} — {step_name}",
        "",
        "── Dades configurades fins ara ──",
    ]

    def val(key, label, transform=None):
        v = d.get(key)
        if v:
            lines.append(f"{label}: {transform(v) if transform else v}")
        else:
            lines.append(f"{label}: (pendent)")

    val('municipi',   'Municipi')
    val('topografia', 'Topografia', lambda x: {
        'pla':'Terreny pla','desnivell_lleu':'Desnivell lleu','desnivell_pronunciat':'Desnivell pronunciat'
    }.get(x, x))

    if d.get('garatge'):
        lines.append(f"Garatge: Sí ({d.get('m2_garatge', '?')} m²)" if d.get('m2_garatge') else "Garatge: Sí")
    else:
        lines.append("Garatge: No / Pendent")

    if d.get('porxos'):
        lines.append(f"Pòrxos/Terrassa: Sí ({d.get('m2_porxos', '?')} m²)" if d.get('m2_porxos') else "Pòrxos: Sí")
    else:
        lines.append("Pòrxos: No / Pendent")

    if d.get('m2'):
        lines.append(f"Superfície: {d.get('m2')} m²")
    if d.get('plantes'):
        lines.append(f"Plantes: {d.get('plantes')}")
    if d.get('num_banys'):
        lines.append(f"Banys: {d.get('num_banys')}")

    if d.get('energia_prioritat'):
        labels = {'max_eficiencia':'Màxima eficiència (Passivhaus)', 'equilibri':'Alt rendiment', 'confort':'Estàndard'}
        lines.append(f"Prioritat energètica: {labels.get(d['energia_prioritat'], d['energia_prioritat'])}")

    if d.get('climatitzacio'):
        clabels = {'total':'Aerotèrmia completa (ACS + calefacció)', 'acs':'Aerotèrmia bàsica (ACS)', 'no':'Sense aerotèrmia'}
        lines.append(f"Climatització: {clabels.get(d['climatitzacio'], d['climatitzacio'])}")

    if d.get('qualitat_aire'):
        alabels = {'excel_lent':'Excel·lent (Zehnder)', 'bona':'Bona', 'estandard':'Estàndard'}
        lines.append(f"Qualitat de l'aire: {alabels.get(d['qualitat_aire'], d['qualitat_aire'])}")

    if d.get('estil_acabats'):
        flabels = {'funcional':'Alta qualitat funcional', 'estandard':'Alta gamma', 'exclusiu':'Disseny exclusiu'}
        lines.append(f"Acabats: {flabels.get(d['estil_acabats'], d['estil_acabats'])}")

    lines.append("")
    lines.append(f"L'usuari es troba al Pas {step} ({step_name}). Respon estrictament en català.")
    lines.append("")
    lines.append(
        "INSTRUCCIÓ ESPECIAL: Si el missatge de l'usuari conté informació que correspon "
        "a un camp del formulari, afegeix AL FINAL de la teva resposta un bloc amb aquest "
        "format exacte (sense espais addicionals):\n"
        "<!--FORM:{\"camp\":\"valor\"}-->\n"
        "Camps possibles segons el pas:\n"
        "Pas 1: municipi (nom), topografia (pla|desnivell_lleu|desnivell_pronunciat), "
        "garatge (si|no), m2_garatge (número), porxos (si|no), m2_porxos (número)\n"
        "Pas 2: m2 (número), plantes (1|2|3), num_banys (número)\n"
        "Pas 3: energia_prioritat (max_eficiencia|equilibri|confort), "
        "climatitzacio (total|acs|no), qualitat_aire (excel_lent|bona|estandard)\n"
        "Pas 4: estil_acabats (funcional|estandard|exclusiu)\n"
        "Si no hi ha dades de formulari, NO incloguis el bloc."
    )

    return '\n'.join(lines)


# ── Form extraction helpers ─────────────────────────────────────────────

def _extract_form_from_answer(answer):
    """
    Busca un bloc <!--FORM:{...}--> a la resposta de DocsGPT.
    Retorna (clean_answer, form_updates_dict).
    """
    m = re.search(r'<!--FORM:(.*?)-->', answer, re.DOTALL)
    if not m:
        return answer, {}
    try:
        updates = json.loads(m.group(1))
    except (json.JSONDecodeError, ValueError):
        return answer, {}
    clean = answer.replace(m.group(0), '').strip()
    return clean, updates


def _normalize(text):
    """Normalitza text: minúscules i sense accents bàsics."""
    t = text.lower()
    for a, b in [('à','a'),('è','e'),('é','e'),('í','i'),('ï','i'),('ò','o'),('ó','o'),('ú','u'),('ü','u'),('ç','c'),('ñ','n'),('·','')]:
        t = t.replace(a, b)
    return t


def _match_municipi(message):
    """
    Cerca un nom de municipi dins el missatge.
    Retorna (nom_exacte, km) o (None, None).
    """
    msg_norm = _normalize(message)
    best_name, best_km, best_len = None, None, 0
    for nom, km in MUNICIPIS_KM.items():
        nom_norm = _normalize(nom)
        if nom_norm in msg_norm and len(nom_norm) > best_len:
            best_name, best_km, best_len = nom, km, len(nom_norm)
    return best_name, best_km


def _extract_form_from_message(message, step):
    """
    Extracció per regex del missatge de l'usuari.
    Retorna un dict amb els camps detectats.
    """
    updates = {}
    msg = message.strip()
    msg_low = msg.lower()
    msg_norm = _normalize(msg)

    # ── Municipi (qualsevol pas) ──
    muni, km = _match_municipi(msg)
    if muni:
        updates['municipi'] = muni
        updates['km'] = km

    # ── Topografia ──
    if step == 1 or not updates.get('municipi'):
        if re.search(r'\b(desnivell\s*pronunciat|molt[ae]?\s+pendent|pendent\s+elevad)', msg_norm):
            updates['topografia'] = 'desnivell_pronunciat'
        elif re.search(r'\b(desnivell\s*lleu|pendent\s+moderad|poc[a]?\s+pendent)', msg_norm):
            updates['topografia'] = 'desnivell_lleu'
        elif re.search(r'\b(pla\b|plana\b|plano\b|terreny\s+pla|flat)', msg_norm):
            updates['topografia'] = 'pla'

    # ── Garatge ──
    if re.search(r'\b(sense\s+garatg|no\s+garatg|no.*garatg|sin\s+garaj)', msg_norm):
        updates['garatge'] = 'no'
    elif re.search(r'\b(si.*garatg|amb\s+garatg|vull\s+garatg|garatge|garaj)', msg_norm):
        updates['garatge'] = 'si'
        m2g = re.search(r'garatg\w*\s+(?:de\s+)?(\d+)\s*m|(\d+)\s*m\w*\s*(?:de\s+)?garatg', msg_norm)
        if m2g:
            updates['m2_garatge'] = int(m2g.group(1) or m2g.group(2))

    # ── Pòrxos / terrassa ──
    if re.search(r'\b(sense\s+(?:porxo|terrass)|no\s+(?:porxo|terrass)|no.*(?:porxo|terrass)|sin\s+(?:porche|terraz))', msg_norm):
        updates['porxos'] = 'no'
    elif re.search(r'\b(si.*(?:porxo|terrass)|amb\s+(?:porxo|terrass)|vull\s+(?:porxo|terrass)|porxo|terrassa)', msg_norm):
        updates['porxos'] = 'si'
        m2p = re.search(r'(?:porxo|terrass)\w*\s+(?:de\s+)?(\d+)\s*m|(\d+)\s*m\w*\s*(?:de\s+)?(?:porxo|terrass)', msg_norm)
        if m2p:
            updates['m2_porxos'] = int(m2p.group(1) or m2p.group(2))

    # ── Superfície (m²) ──
    m2_match = re.search(r'(\d{2,4})\s*(?:m2|m²|metres?\s*quadrats?|metros?\s*cuadrados?)', msg_norm)
    if m2_match:
        val = int(m2_match.group(1))
        if 80 <= val <= 800:
            updates['m2'] = val

    # ── Plantes ──
    pl = re.search(r'\b(1|una?|2|dos|dues|3|tres)\s*plant', msg_norm)
    if pl:
        v = pl.group(1)
        mapping = {'1':'1','un':'1','una':'1','2':'2','dos':'2','dues':'2','3':'3','tres':'3'}
        updates['plantes'] = mapping.get(v, v)

    # ── Banys ──
    bn = re.search(r'(\d)\s*banys?', msg_norm)
    if bn:
        updates['num_banys'] = bn.group(1)

    # ── Energia ──
    if re.search(r'passivhaus|maxima\s+eficiencia', msg_norm):
        updates['energia_prioritat'] = 'max_eficiencia'
    elif re.search(r'alt\s+rendiment|equilibri', msg_norm):
        updates['energia_prioritat'] = 'equilibri'
    elif re.search(r'estandard|confort\s+basic|qualitat\s+estandard', msg_norm):
        updates['energia_prioritat'] = 'confort'

    # ── Climatització ──
    if re.search(r'sense\s+aerotermia|no\s+aerotermia|sin\s+aerotermia', msg_norm):
        updates['climatitzacio'] = 'no'
    elif re.search(r'aerotermia\s+complet|aerotermia\s+total|acs\s*\+\s*calefaccio', msg_norm):
        updates['climatitzacio'] = 'total'
    elif re.search(r'aerotermia\s+basic|nomes?\s+acs|solo\s+acs', msg_norm):
        updates['climatitzacio'] = 'acs'

    # ── Qualitat aire ──
    if re.search(r'zehnder|excel.?lent|aire\s+excel', msg_norm):
        updates['qualitat_aire'] = 'excel_lent'
    elif re.search(r'bona\s+(?:qualitat|aire)|aire\s+bo', msg_norm):
        updates['qualitat_aire'] = 'bona'
    elif re.search(r'aire\s+estandard|qualitat\s+estandard', msg_norm):
        updates['qualitat_aire'] = 'estandard'

    # ── Acabats ──
    if re.search(r'funcional', msg_norm):
        updates['estil_acabats'] = 'funcional'
    elif re.search(r'exclusiu|disseny\s+exclusiu|krona', msg_norm):
        updates['estil_acabats'] = 'exclusiu'
    elif re.search(r'alta\s+gamma|estandard.*acabat|acabat.*estandard', msg_norm):
        updates['estil_acabats'] = 'estandard'

    return updates


@app.route('/')
def index():
    return redirect('/usuaris.html')


@app.route('/municipis')
def municipis():
    q = request.args.get('q', '').lower().strip()
    if len(q) < 2:
        return jsonify([])
    resultats = [
        {'nom': k, 'km': v}
        for k, v in sorted(MUNICIPIS_KM.items())
        if q in k.lower()
    ][:10]
    return jsonify(resultats)


@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    return jsonify(calculate_budget(data))


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    result = calculate_budget(data)
    pdf_buf = generar_pdf(data, result)
    from datetime import date as _date
    filename = f"pressupost-papik-{_date.today().strftime('%Y%m%d')}.pdf"
    return Response(
        pdf_buf.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'application/pdf',
        }
    )


if __name__ == '__main__':
    print('\n' + '=' * 47)
    print('  PAPIK · Configurador de Pressupostos v2')
    print('  Servidor: http://localhost:5001')
    print('=' * 47 + '\n')
    app.run(debug=True, port=5001)
