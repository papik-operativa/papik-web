"""
Vercel Python Serverless Function · POST /api/calcular

Calcula el pressupost orientatiu d'un habitatge Passivhaus a partir de les
respostes del configurador. Tota la lògica de preus viu al servidor: el client
només envia les respostes i rep el desglossament.

Portat des de app.py (Flask) — calculate_budget() amb dades reals de 14
projectes Papik (2024-2025). Sense dependències externes (stdlib only).
"""
from http.server import BaseHTTPRequestHandler
from datetime import date, timedelta
import json


# ── Distàncies aproximades (km per carretera) des de Sant Cugat del Vallès ────
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
    "Vallvidrera": 15, "Vacarisses": 30, "Collsuspina": 52,
    "Premià de Dalt": 40,
}
KM_PER_DEFECTE = 25


def calcular_km(municipi):
    if not municipi:
        return 0
    nom = str(municipi).strip()
    if nom in MUNICIPIS_KM:
        return MUNICIPIS_KM[nom]
    nom_l = nom.lower()
    for k, v in MUNICIPIS_KM.items():
        if nom_l in k.lower():
            return v
    return KM_PER_DEFECTE


def derivar_variables(data):
    m2 = float(data.get('m2', 160))
    plantes = str(data.get('plantes', '2'))
    banys = int(data.get('num_banys', 2))

    m2_paviment = round(m2 * 0.91)
    num_portes = max(4, round(m2 / 22)) + banys
    m2_fonamentacio = m2

    tipus_escala = data.get('tipus_escala', 'no' if plantes == '1' else 'fusta')
    escala = plantes != '1' and tipus_escala != 'no'

    energia = data.get('energia_prioritat', 'equilibri')
    finestres = {
        'max_eficiencia': 'ventaclimVMM74',
        'equilibri': 'ecovenS82',
        'confort': 'ecovenS70',
    }.get(energia, 'ecovenS82')

    clima = data.get('climatitzacio', 'acs')
    aerotermia = {'total': 'acs_calefaccio', 'acs': 'acs', 'no': 'cap'}.get(clima, 'acs')

    zehnder = data.get('qualitat_aire', 'bona') == 'excel_lent'
    krona = data.get('estil_acabats', 'alta_qualitat') == 'exclusiu'

    garatge_resp = data.get('garatge', 'no')
    garatge = garatge_resp not in ('no', '', None, False)
    m2_garatge = float(data.get('m2_garatge', 0)) if garatge else 0.0

    m2_porxos = float(data.get('m2_porxos', 0) or 0)
    porxos = m2_porxos > 0

    nivell_bany = data.get('nivell_bany', 'alt')
    tipus_coberta = data.get('tipus_coberta', 'teula')
    tipus_facana = data.get('tipus_facana', 'sate')
    tipus_paviment = data.get('tipus_paviment', 'ceramic')
    vol_solar = data.get('plaques_solars', 'no') == 'si'
    vol_persianes = data.get('persianes', 'no') == 'si'
    vol_fan_coils = data.get('fan_coils', 'no') == 'si'
    vol_llar_foc = data.get('llar_foc', 'no') == 'si'
    vol_rado = data.get('membrana_rado', 'no') == 'si'
    vol_domotica = data.get('domotica', 'no') == 'si'

    num_finestres = max(4, round(m2 / 16))

    municipi = data.get('municipi', '')
    km = calcular_km(municipi)

    return dict(
        m2=m2, plantes=plantes, num_banys=banys,
        m2_paviment=m2_paviment, num_portes=num_portes,
        m2_fonamentacio=m2_fonamentacio, escala=escala,
        tipus_escala=tipus_escala,
        finestres=finestres, aerotermia=aerotermia,
        zehnder=zehnder, krona=krona,
        garatge=garatge, m2_garatge=m2_garatge,
        porxos=porxos, m2_porxos=m2_porxos,
        km=km, municipi=municipi,
        nivell_bany=nivell_bany,
        tipus_coberta=tipus_coberta,
        tipus_facana=tipus_facana,
        tipus_paviment=tipus_paviment,
        vol_solar=vol_solar, vol_persianes=vol_persianes,
        vol_fan_coils=vol_fan_coils, vol_llar_foc=vol_llar_foc,
        vol_rado=vol_rado, vol_domotica=vol_domotica,
        num_finestres=num_finestres,
    )


def calculate_budget(data):
    """Calcula el pressupost complet · ratios validats amb 14 projectes reals."""
    v = derivar_variables(data)
    m2 = v['m2']
    plantes = v['plantes']
    num_banys = v['num_banys']
    m2_paviment = v['m2_paviment']
    num_portes = v['num_portes']
    m2_fonamentacio = v['m2_fonamentacio']
    escala = v['escala']
    tipus_escala = v['tipus_escala']
    finestres = v['finestres']
    aerotermia = v['aerotermia']
    zehnder = v['zehnder']
    krona = v['krona']
    garatge = v['garatge']
    m2_garatge = v['m2_garatge']
    m2_porxos = v['m2_porxos']
    km = v['km']
    nivell_bany = v['nivell_bany']
    tipus_coberta = v['tipus_coberta']
    tipus_facana = v['tipus_facana']
    tipus_paviment = v['tipus_paviment']
    vol_solar = v['vol_solar']
    vol_persianes = v['vol_persianes']
    vol_fan_coils = v['vol_fan_coils']
    vol_llar_foc = v['vol_llar_foc']
    vol_rado = v['vol_rado']
    vol_domotica = v['vol_domotica']
    num_finestres = v['num_finestres']

    # Preus finestres (€/m² de finestra)
    preu_finestres = {
        'ecovenS70': 18.53, 'ecovenS82': 22.00,
        'ventaclimVMM74': 28.00, 'ventaclimSupercomfort': 35.00,
    }.get(finestres, 18.53)
    preu_base_finestres = 18.53

    # ── PACK ENVOLVENT TÈRMIC ────────────────────────────────────────────────
    rate = {'1': 820.0, '2': 984.4}.get(plantes, 1050.0)
    m2_finestres = m2 * 0.109
    suplement_finestres = (preu_finestres - preu_base_finestres) * m2_finestres
    cost_porta_entrada = 2245.00
    cost_grua = min(900.0, max(450.0, 450.0 + (m2 - 120) * 2.5))
    base_variable = rate * m2
    cost_estructura = base_variable * 0.503
    cost_coberta = base_variable * 0.294
    cost_finestres = base_variable * 0.178 + suplement_finestres

    increment_coberta = {
        'teula': 0.0,
        'plana': base_variable * 0.015,
        'xapa': base_variable * -0.020,
    }.get(tipus_coberta, 0.0)
    cost_coberta += increment_coberta

    increment_facana = {
        'sate': 0.0,
        'ventilada': 28.0 * m2,
        'suro': 22.0 * m2,
        'accoya': 45.0 * m2,
    }.get(tipus_facana, 0.0)

    pack_envolvent = (cost_estructura + cost_coberta + cost_finestres
                      + cost_porta_entrada + cost_grua + increment_facana)

    # ── PACK INSTAL·LACIONS ──────────────────────────────────────────────────
    cost_teleco = 1989.00
    cost_sanejament = 1621.00
    cost_electricitat = 48.0 * m2
    cost_agua = 37.5 * m2
    cost_escomeses = 8578.00
    cost_ventilacio = 1985.00

    if zehnder:
        cost_zehnder = 8910.00 if m2 <= 180 else 9639.00
    else:
        cost_zehnder = 0.0

    cost_aerotermia = {'acs': 2870.00, 'acs_calefaccio': 10976.00}.get(aerotermia, 0.0)

    num_fan_coils = max(2, round(m2 / 40)) if vol_fan_coils else 0
    cost_fan_coils = 996.0 * num_fan_coils

    cost_llar_foc = 3200.0 if vol_llar_foc else 0.0
    cost_solar = 6500.0 if vol_solar else 0.0
    cost_persianes = 650.0 * num_finestres if vol_persianes else 0.0
    cost_rado = 12.0 * m2 if vol_rado else 0.0
    cost_domotica = (8500.0 + 25.0 * m2) if vol_domotica else 0.0

    pack_installacions = (cost_teleco + cost_sanejament + cost_electricitat + cost_agua
                          + cost_escomeses + cost_ventilacio + cost_zehnder + cost_aerotermia
                          + cost_fan_coils + cost_llar_foc + cost_solar + cost_persianes
                          + cost_rado + cost_domotica)

    # ── PACK PARKING I EXTERIORS ─────────────────────────────────────────────
    cost_porta_peatonal = 544.00 if garatge else 0.0
    cost_porta_motoritzada = 2450.00 if garatge else 0.0
    cost_garatge_estructura = 998.0 * m2_garatge
    cost_porxos_calc = 577.0 * m2_porxos
    pack_parking = (cost_porta_peatonal + cost_porta_motoritzada
                    + cost_garatge_estructura + cost_porxos_calc)

    # ── PACK ACABATS INTERIORS ───────────────────────────────────────────────
    cost_pintura = 19.5 * m2
    cost_pladur = 99.0 * m2

    acabats_cuina = data.get('estil_acabats', 'alta_qualitat')
    cost_cuina = {
        'funcional': 10500.00,
        'alta_qualitat': 13234.00,
        'exclusiu': 16500.00,
    }.get(acabats_cuina, 13234.00)

    preu_paviment = {'formigo': 42.0, 'ceramic': 49.0, 'parquet': 68.0}.get(tipus_paviment, 49.0)
    cost_paviments = preu_paviment * m2_paviment
    cost_portes_interiors = 495.0 * num_portes
    cost_krona = 245.0 * num_portes if krona else 0.0

    preu_bany = {'estandar': 2800.00, 'alt': 4500.00, 'premium': 7500.00}.get(nivell_bany, 4500.00)
    cost_banys = preu_bany * num_banys

    if escala:
        cost_escala = {'fusta': 3423.0, 'metallica': 4800.0}.get(tipus_escala, 3423.0)
    else:
        cost_escala = 0.0

    pack_acabats = (cost_pintura + cost_pladur + cost_cuina + cost_paviments
                    + cost_portes_interiors + cost_krona + cost_banys + cost_escala)

    # ── TRANSPORT ────────────────────────────────────────────────────────────
    cost_transport = 95.0 * km

    # ── TOTALS ───────────────────────────────────────────────────────────────
    total_construccio = pack_envolvent + pack_installacions + pack_parking + pack_acabats + cost_transport
    cost_projecte = 0.0 if data.get('te_projecte') else total_construccio * 0.105
    cost_seguretat = total_construccio * 0.0175
    cost_fonamentacio = 396.0 * m2_fonamentacio
    total_contractacio = cost_projecte + cost_seguretat + cost_fonamentacio
    total_sense_iva = total_construccio + total_contractacio
    iva = total_sense_iva * 0.10
    total_pressupost = total_sense_iva + iva

    today = date.today()
    validesa = today + timedelta(days=30)
    r = lambda x: round(x, 2)

    finestres_labels = {
        'ecovenS70': 'EcoVen S-70 PVC (estàndard)',
        'ecovenS82': 'EcoVen S-82 (alt rendiment)',
        'ventaclimVMM74': 'Ventaclim VMM-74 (Passivhaus)',
        'ventaclimSupercomfort': 'Ventaclim Supercomfort',
    }
    aerotermia_labels = {
        'cap': 'No inclosa', 'acs': 'Aerotèrmia ACS',
        'acs_calefaccio': 'Aerotèrmia ACS + Calefacció',
    }
    coberta_labels = {'teula': 'Teula àrab/mixta', 'plana': 'Plana (grava/transitable)', 'xapa': 'Xapa metàl·lica'}
    facana_labels = {'sate': 'SATE arrebossat', 'ventilada': 'Façana ventilada (fusta)', 'suro': 'Suro natural', 'accoya': 'Fusta Accoya'}
    paviment_labels = {'formigo': 'Formigó polit', 'ceramic': 'Ceràmic/Gres', 'parquet': 'Parquet fusta'}
    bany_labels = {'estandar': 'Estàndard', 'alt': 'Alt (Roca ONA)', 'premium': 'Premium exclusiu'}

    return {
        'variables_derivades': {
            'te_projecte': bool(data.get('te_projecte')),
            'municipi': v['municipi'],
            'km_transport': km,
            'm2': m2,
            'm2_paviment_calculat': m2_paviment,
            'num_portes_calculat': num_portes,
            'finestres_label': finestres_labels.get(finestres, finestres),
            'aerotermia_label': aerotermia_labels.get(aerotermia, aerotermia),
            'coberta_label': coberta_labels.get(tipus_coberta, tipus_coberta),
            'facana_label': facana_labels.get(tipus_facana, tipus_facana),
            'paviment_label': paviment_labels.get(tipus_paviment, tipus_paviment),
            'bany_label': bany_labels.get(nivell_bany, nivell_bany),
            'num_finestres': num_finestres,
            'num_fan_coils': num_fan_coils,
        },
        'pack_envolvent': {
            'estructura_vertical': r(cost_estructura),
            'coberta_forjats': r(cost_coberta),
            'finestres': r(cost_finestres),
            'increment_facana': r(increment_facana),
            'porta_entrada': r(cost_porta_entrada),
            'grua': r(cost_grua),
            'total': r(pack_envolvent),
        },
        'pack_installacions': {
            'telecomunicacions': r(cost_teleco),
            'sanejament_interior': r(cost_sanejament),
            'electricitat_interior': r(cost_electricitat),
            'agua_interior': r(cost_agua),
            'escomeses': r(cost_escomeses),
            'preinstallacio_ventilacio': r(cost_ventilacio),
            'zehnder': r(cost_zehnder),
            'aerotermia': r(cost_aerotermia),
            'fan_coils': r(cost_fan_coils),
            'llar_foc': r(cost_llar_foc),
            'solar': r(cost_solar),
            'persianes': r(cost_persianes),
            'membrana_rado': r(cost_rado),
            'domotica': r(cost_domotica),
            'total': r(pack_installacions),
        },
        'pack_parking': {
            'porta_peatonal': r(cost_porta_peatonal),
            'porta_motoritzada': r(cost_porta_motoritzada),
            'garatge_estructura': r(cost_garatge_estructura),
            'porxos_terrasses': r(cost_porxos_calc),
            'total': r(pack_parking),
        },
        'pack_acabats': {
            'pintura': r(cost_pintura),
            'pladur': r(cost_pladur),
            'cuina': r(cost_cuina),
            'paviments': r(cost_paviments),
            'portes_interiors': r(cost_portes_interiors),
            'estructura_krona': r(cost_krona),
            'banys': r(cost_banys),
            'escala': r(cost_escala),
            'total': r(pack_acabats),
        },
        'transport': r(cost_transport),
        'total_construccio': r(total_construccio),
        'contractacio_externa': {
            'projecte_arquitectonic': r(cost_projecte),
            'seguretat_salut': r(cost_seguretat),
            'fonamentacio': r(cost_fonamentacio),
            'total': r(total_contractacio),
        },
        'total_sense_iva': r(total_sense_iva),
        'iva': r(iva),
        'total_pressupost': r(total_pressupost),
        'data_emissio': today.strftime('%d/%m/%Y'),
        'data_validesa': validesa.strftime('%d/%m/%Y'),
    }


class handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0) or 0)
            body = self.rfile.read(length).decode('utf-8') if length else ''
            data = json.loads(body) if body else {}
            result = calculate_budget(data)
            self._send(200, result)
        except (ValueError, TypeError) as e:
            self._send(400, {'error': 'invalid_input', 'detail': str(e)})
        except Exception as e:
            self._send(500, {'error': 'server_error', 'detail': str(e)})

    def do_GET(self):
        self._send(405, {'error': 'method_not_allowed', 'detail': 'use POST'})
