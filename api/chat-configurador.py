"""
Vercel Python Serverless Function · POST /api/chat-configurador

Guia Virtual de PAPIK que acompanya l'usuari durant els passos del
configurador. Reenvia la pregunta a DocsGPT (Arc53) injectant el
context de configuració com a prefix la primera vegada, i mantenint
la conversa via conversation_id en les peticions següents.

Portat des de app.py (Flask `/chat-configurador`). Sense dependències
externes — només stdlib. La API key s'agafa de la variable d'entorn
`DOCSGPT_API_KEY` configurada al dashboard de Vercel.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import urllib.request
import urllib.error


DOCSGPT_URL = 'https://gptcloud.arc53.com/api/answer'
DOCSGPT_API_KEY = os.environ.get('DOCSGPT_API_KEY', '')


# ── Municipis (subconjunt suficient per detectar ubicació via xat) ──────────
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
    "Valldoreix": 3, "La Floresta": 4, "Premià de Dalt": 40,
}


def _normalize(text):
    t = text.lower()
    for a, b in [('à', 'a'), ('è', 'e'), ('é', 'e'), ('í', 'i'), ('ï', 'i'),
                 ('ò', 'o'), ('ó', 'o'), ('ú', 'u'), ('ü', 'u'),
                 ('ç', 'c'), ('ñ', 'n'), ('·', '')]:
        t = t.replace(a, b)
    return t


def _match_municipi(message):
    msg_norm = _normalize(message)
    best_name, best_km, best_len = None, None, 0
    for nom, km in MUNICIPIS_KM.items():
        nom_norm = _normalize(nom)
        if nom_norm in msg_norm and len(nom_norm) > best_len:
            best_name, best_km, best_len = nom, km, len(nom_norm)
    return best_name, best_km


def _format_config_context(step, config_state):
    """Context prefix sent ONCE on the first message of a conversation.

    Keep this lean: do NOT try to redefine the agent persona here — that
    lives in the DocsGPT agent prompt. We only feed live form state and
    a short, focused instruction about the FORM-update marker.
    """
    step_names = {1: 'Parcel·la', 2: "L'Habitatge", 3: 'Confort', 4: 'Acabats'}
    step_name = step_names.get(step, f'Pas {step}')

    d = config_state or {}
    lines = [
        f"[ESTAT ACTUAL DEL CONFIGURADOR · Pas {step} — {step_name}]",
    ]

    def val(key, label):
        v = d.get(key)
        if v in (None, '', 0):
            lines.append(f"  · {label}: (pendent)")
        else:
            lines.append(f"  · {label}: {v}")

    val('municipi',       'Municipi')
    val('m2',             'Superfície (m²)')
    val('plantes',        'Plantes')
    val('num_banys',      'Banys')
    val('garatge',        'Garatge')
    val('m2_garatge',     'Garatge (m²)')
    val('m2_porxos',      'Pòrxos (m²)')
    val('tipus_coberta',  'Coberta')
    val('tipus_facana',   'Façana')
    val('tipus_paviment', 'Paviment')
    val('nivell_bany',    'Nivell de bany')

    lines.append("")
    lines.append(
        "[INSTRUCCIÓ TÈCNICA · només per al sistema, no per a l'usuari] "
        "Quan el missatge de l'usuari contingui dades que encaixin amb un camp "
        "del formulari (municipi, m2, plantes, num_banys, garatge, m2_garatge, "
        "m2_porxos), afegeix una ÚLTIMA línia separada de la resposta amb el "
        "format exacte: <!--FORM:{\"camp\":valor}-->  "
        "Valors acceptats: municipi=nom de municipi català · m2=enter 80-800 · "
        "plantes=\"1\"|\"2\"|\"3\" · num_banys=enter 1-4 · garatge=\"si\"|\"no\" · "
        "m2_garatge=enter · m2_porxos=enter. "
        "Si no hi ha cap dada nova, no incloguis aquest bloc."
    )

    return '\n'.join(lines)


def _extract_form_from_answer(answer):
    """Busca un bloc <!--FORM:{...}--> a la resposta i el retira del text."""
    m = re.search(r'<!--FORM:(.*?)-->', answer, re.DOTALL)
    if not m:
        return answer, {}
    try:
        updates = json.loads(m.group(1))
    except (json.JSONDecodeError, ValueError):
        return answer, {}
    clean = answer.replace(m.group(0), '').strip()
    return clean, updates


def _extract_form_from_message(message, step):
    """Extracció ràpida per regex del missatge de l'usuari."""
    updates = {}
    msg_norm = _normalize(message)

    muni, km = _match_municipi(message)
    if muni:
        updates['municipi'] = muni
        updates['km'] = km

    if re.search(r'\b(desnivell\s*pronunciat|molt[ae]?\s+pendent)', msg_norm):
        updates['topografia'] = 'desnivell_pronunciat'
    elif re.search(r'\b(desnivell\s*lleu|pendent\s+moderad|poc[a]?\s+pendent)', msg_norm):
        updates['topografia'] = 'desnivell_lleu'
    elif re.search(r'\b(pla\b|plana\b|terreny\s+pla|flat)', msg_norm):
        updates['topografia'] = 'pla'

    m2_match = re.search(r'(\d{2,4})\s*(?:m2|m²|metres?\s*quadrats?)', msg_norm)
    if m2_match:
        v = int(m2_match.group(1))
        if 80 <= v <= 800:
            updates['m2'] = v

    pl = re.search(r'\b(1|una?|2|dos|dues|3|tres)\s*plant', msg_norm)
    if pl:
        mapping = {'1': '1', 'un': '1', 'una': '1', '2': '2',
                   'dos': '2', 'dues': '2', '3': '3', 'tres': '3'}
        updates['plantes'] = mapping.get(pl.group(1), pl.group(1))

    bn = re.search(r'(\d)\s*banys?', msg_norm)
    if bn:
        updates['num_banys'] = bn.group(1)

    if re.search(r'passivhaus|maxima\s+eficiencia', msg_norm):
        updates['energia_prioritat'] = 'max_eficiencia'
    elif re.search(r'alt\s+rendiment|equilibri', msg_norm):
        updates['energia_prioritat'] = 'equilibri'

    return updates


def _docsgpt_call(question, conversation_id):
    """Invoca l'API de DocsGPT i retorna (answer, new_conversation_id)."""
    if not DOCSGPT_API_KEY:
        raise RuntimeError(
            "DOCSGPT_API_KEY no configurada al servidor. "
            "Defineix-la com a variable d'entorn al projecte de Vercel."
        )

    payload = {'question': question, 'api_key': DOCSGPT_API_KEY}
    if conversation_id:
        payload['conversation_id'] = conversation_id

    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        DOCSGPT_URL,
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )

    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode('utf-8'))

    answer = data.get('answer') or "No s'ha pogut obtenir resposta de l'agent."
    new_cid = data.get('conversation_id')
    return answer, new_cid


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
            raw = self.rfile.read(length).decode('utf-8') if length else ''
            payload = json.loads(raw) if raw else {}

            # Accept both `message` (CA backend) and `question` (existing ES JS)
            user_message = (payload.get('message') or payload.get('question') or '').strip()
            conversation_id = payload.get('conversation_id')
            step = payload.get('step', 1)
            config_state = payload.get('config_state') or {}

            # The ES frontend sends config_state as a JSON string — handle both.
            if isinstance(config_state, str):
                try:
                    config_state = json.loads(config_state)
                except (json.JSONDecodeError, ValueError):
                    config_state = {}

            if not user_message:
                self._send(400, {'error': 'Missatge buit.'})
                return

            if not conversation_id:
                ctx = _format_config_context(step, config_state)
                full_question = (
                    f"[CONTEXT DE CONFIGURACIÓ — PAS {step}]\n{ctx}\n\n"
                    f"[PREGUNTA DE L'USUARI]\n{user_message}"
                )
            else:
                full_question = user_message

            regex_updates = _extract_form_from_message(user_message, step)

            answer, new_cid = _docsgpt_call(full_question, conversation_id)
            answer, ai_updates = _extract_form_from_answer(answer)

            form_updates = {**regex_updates, **ai_updates}

            if 'municipi' in form_updates and 'km' not in form_updates:
                matched, km = _match_municipi(form_updates['municipi'])
                if matched:
                    form_updates['municipi'] = matched
                    form_updates['km'] = km
                else:
                    del form_updates['municipi']

            self._send(200, {
                'answer': answer,
                'conversation_id': new_cid,
                'form_updates': form_updates or None,
            })

        except urllib.error.HTTPError as e:
            self._send(e.code, {'error': f'DocsGPT HTTP {e.code}', 'detail': e.reason})
        except urllib.error.URLError as e:
            self._send(504, {'error': "No s'ha pogut connectar amb DocsGPT", 'detail': str(e.reason)})
        except (ValueError, TypeError) as e:
            self._send(400, {'error': 'invalid_input', 'detail': str(e)})
        except RuntimeError as e:
            self._send(500, {'error': 'config_error', 'detail': str(e)})
        except Exception as e:
            self._send(500, {'error': 'server_error', 'detail': str(e)})

    def do_GET(self):
        self._send(405, {'error': 'method_not_allowed', 'detail': 'use POST'})
