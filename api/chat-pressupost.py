"""
Vercel Python Serverless Function · POST /api/chat-pressupost

Assessor Virtual de PAPIK que respon dubtes sobre el pressupost
generat pel configurador. La primera pregunta injecta com a prefix
un resum estructurat del pressupost (input + resultat del càlcul).
Les preguntes següents s'envien amb conversation_id i DocsGPT manté
l'historial.

A més de respondre, el chat pot **modificar el pressupost en directe**.
Quan l'usuari demana canvis ("treu la piscina", "afegeix un bany",
"vull façana ventilada"...), retorna un bloc ocult al final de la
resposta amb el format `<!--FORM:{...}-->`. El frontend l'extreu,
aplica els canvis al state, recrida /api/calcular i actualitza el
preu sense que l'usuari hagi de tornar enrere al formulari.

Portat des de app.py (Flask `/chat-pressupost`). Stdlib only.
API key des de la variable d'entorn `DOCSGPT_API_KEY`.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import urllib.request
import urllib.error


DOCSGPT_URL = 'https://gptcloud.arc53.com/api/answer'
DOCSGPT_API_KEY = os.environ.get('DOCSGPT_API_KEY', '')


# ── Valors acceptats per a cada camp ────────────────────────────────────────
ENUM_FIELDS = {
    'plantes':         {'1', '2', '3'},
    'garatge':         {'si', 'no'},
    'tipus_escala':    {'fusta', 'metallica', 'no'},
    'tipus_coberta':   {'teula', 'plana', 'xapa'},
    'tipus_facana':    {'sate', 'ventilada', 'suro', 'accoya'},
    'tipus_paviment':  {'formigo', 'ceramic', 'parquet'},
    'nivell_bany':     {'estandar', 'alt', 'premium'},
    'plaques_solars':  {'si', 'no'},
    'persianes':       {'si', 'no'},
    'fan_coils':       {'si', 'no'},
    'llar_foc':        {'si', 'no'},
    'membrana_rado':   {'si', 'no'},
    'domotica':        {'si', 'no'},
    'energia_prioritat': {'max_eficiencia', 'equilibri', 'confort'},
    'climatitzacio':   {'total', 'acs', 'no'},
    'qualitat_aire':   {'excel_lent', 'bona'},
    'estil_acabats':   {'funcional', 'alta_qualitat', 'exclusiu'},
}
INT_FIELDS = {'m2', 'num_banys', 'm2_garatge', 'm2_porxos'}
INT_RANGES = {
    'm2':         (80, 800),
    'num_banys':  (1, 4),
    'm2_garatge': (0, 200),
    'm2_porxos':  (0, 200),
}
STR_FIELDS = {'municipi'}


def _format_budget_for_context(budget_input, budget_result):
    """Resum estructurat del pressupost per al context del xat."""
    lines = ['═══ PRESSUPOST PERSONALITZAT PAPIK ═══\n']

    bi = budget_input or {}
    br = budget_result or {}

    m2 = bi.get('m2', '—')
    plantes = bi.get('plantes', '—')
    num_banys = bi.get('num_banys', '—')
    municipi = bi.get('municipi', '')

    lines.append(f'Superfície construïda: {m2} m²')
    if municipi:
        lines.append(f'Municipi: {municipi}')
    lines.append(f'Nombre de plantes: {plantes}')
    lines.append(f'Nombre de banys: {num_banys}')

    garatge = bi.get('garatge', False)
    m2_gar = bi.get('m2_garatge', 0)
    porxos = bi.get('porxos', False) or (bi.get('m2_porxos', 0) and float(bi.get('m2_porxos', 0)) > 0)
    m2_por = bi.get('m2_porxos', 0)
    lines.append(f"Garatge: {'Sí (' + str(m2_gar) + ' m²)' if garatge else 'No'}")
    lines.append(f"Pòrxos/Terrassa coberta: {'Sí (' + str(m2_por) + ' m²)' if porxos else 'No'}")

    energia_labels = {
        'max_eficiencia': 'Màxima eficiència (Passivhaus)',
        'equilibri': 'Alt rendiment energètic',
        'confort': 'Qualitat estàndard',
    }
    clima_labels = {
        'total': 'ACS + Calefacció per aerotèrmia',
        'acs': 'ACS per aerotèrmia',
        'no': 'Sense aerotèrmia',
    }
    lines.append(f"Eficiència energètica: {energia_labels.get(bi.get('energia_prioritat', 'equilibri'), '—')}")
    lines.append(f"Climatització: {clima_labels.get(bi.get('climatitzacio', 'acs'), '—')}")
    if bi.get('qualitat_aire') == 'excel_lent':
        lines.append('Sistema Zehnder (recuperació de calor): Inclòs')
    if bi.get('estil_acabats') == 'exclusiu':
        lines.append("Acabats: Disseny d'interiors personalitzat (Krona)")

    if br:
        vd = br.get('variables_derivades', {})
        pe = br.get('pack_envolvent', {})
        pi = br.get('pack_installacions', {})
        pp = br.get('pack_parking', {})
        pa = br.get('pack_acabats', {})
        ce = br.get('contractacio_externa', {})
        fmt = lambda x: f"{float(x):,.0f} €" if x else '0 €'

        lines.append("\n─── DESGLOSSAMENT DE COSTOS ───")
        lines.append(f"Finestres: {vd.get('finestres_label', '—')}")
        lines.append(f"Aerotèrmia: {vd.get('aerotermia_label', '—')}")
        lines.append(f"Km transport: {vd.get('km_transport', '—')} km")
        lines.append(f"\nPack Envolvent Tèrmic:     {fmt(pe.get('total', 0))}")
        lines.append(f"Pack Instal·lacions:       {fmt(pi.get('total', 0))}")
        lines.append(f"Pack Parking i Exteriors:  {fmt(pp.get('total', 0))}")
        lines.append(f"Pack Acabats Interiors:    {fmt(pa.get('total', 0))}")
        lines.append(f"Honoraris i Gestió Tècnica: {fmt(ce.get('total', 0))}")
        lines.append(f"\nSubtotal sense IVA: {fmt(br.get('total_sense_iva', 0))}")
        lines.append(f"IVA (10%): {fmt(br.get('iva', 0))}")
        lines.append(f"TOTAL AMB IVA: {fmt(br.get('total_pressupost', 0))}")
        lines.append(f"Vàlid fins: {br.get('data_validesa', '—')}")

    lines.append('')
    lines.append(
        "[INSTRUCCIÓ TÈCNICA · només per al sistema, no per a l'usuari] "
        "Si en algun moment de la conversa l'usuari demana modificar el pressupost "
        "(p. ex. \"treu la piscina\", \"afegeix un bany\", \"vull façana ventilada\", "
        "\"canvia a 220 m²\", \"sense plaques solars\", \"acabats premium\", etc.), "
        "respon explicant breument el canvi i, al final de la teva resposta, afegeix "
        "una ÚNICA línia separada amb el format EXACTE: "
        "<!--FORM:{\"camp\":valor,\"camp2\":valor2}-->\n"
        "Els camps acceptats i els seus valors són:\n"
        "  · m2 = enter 80-800 (superfície construïda)\n"
        "  · plantes = \"1\" | \"2\" | \"3\"\n"
        "  · num_banys = enter 1-4\n"
        "  · garatge = \"si\" | \"no\"\n"
        "  · m2_garatge = enter (només si garatge=\"si\")\n"
        "  · m2_porxos = enter (0 si no en vol)\n"
        "  · tipus_escala = \"fusta\" | \"metallica\" | \"no\"\n"
        "  · tipus_coberta = \"teula\" | \"plana\" | \"xapa\"\n"
        "  · tipus_facana = \"sate\" | \"ventilada\" | \"suro\" | \"accoya\"\n"
        "  · tipus_paviment = \"formigo\" | \"ceramic\" | \"parquet\"\n"
        "  · nivell_bany = \"estandar\" | \"alt\" | \"premium\"\n"
        "  · plaques_solars = \"si\" | \"no\" (fotovoltaiques)\n"
        "  · persianes = \"si\" | \"no\" (motoritzades)\n"
        "  · fan_coils = \"si\" | \"no\" (climatització per conductes)\n"
        "  · llar_foc = \"si\" | \"no\"\n"
        "  · membrana_rado = \"si\" | \"no\"\n"
        "  · domotica = \"si\" | \"no\" (Loxone)\n"
        "  · energia_prioritat = \"max_eficiencia\" | \"equilibri\" | \"confort\"\n"
        "  · climatitzacio = \"total\" | \"acs\" | \"no\" (aerotèrmia)\n"
        "  · qualitat_aire = \"excel_lent\" | \"bona\" (excel·lent = sistema Zehnder)\n"
        "  · estil_acabats = \"funcional\" | \"alta_qualitat\" | \"exclusiu\" (exclusiu = Krona)\n"
        "  · municipi = nom de municipi català\n"
        "Inclou només els camps que canvien. Si l'usuari només pregunta informació, "
        "NO afegeixis aquest bloc. Mai mostris el bloc en text visible: ha d'anar dins "
        "del comentari HTML <!--FORM:...-->. El frontend l'extreu i actualitza el pressupost."
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


def _sanitize_form_updates(updates):
    """Valida les claus i valors retornats per l'LLM contra el catàleg
    canonical. Descarta qualsevol cosa que no encaixi per evitar que el
    frontend rebi state corrupte."""
    if not isinstance(updates, dict):
        return {}
    clean = {}
    for k, v in updates.items():
        if k in ENUM_FIELDS:
            sv = str(v).strip().lower()
            # Some leniency: accept "yes"/"sí"/"true" as "si", "no"/"false" as "no"
            if ENUM_FIELDS[k] == {'si', 'no'}:
                if sv in {'si', 'sí', 'yes', 'true', '1'}: sv = 'si'
                elif sv in {'no', 'false', '0'}: sv = 'no'
            if sv in ENUM_FIELDS[k]:
                clean[k] = sv
        elif k in INT_FIELDS:
            try:
                iv = int(float(v))
            except (TypeError, ValueError):
                continue
            lo, hi = INT_RANGES.get(k, (0, 10**9))
            if lo <= iv <= hi:
                clean[k] = iv
        elif k in STR_FIELDS:
            sv = str(v).strip()
            if 0 < len(sv) <= 80:
                clean[k] = sv
    return clean


def _docsgpt_call(question, conversation_id):
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

    return (
        data.get('answer') or "No s'ha pogut obtenir resposta de l'agent.",
        data.get('conversation_id'),
    )


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

            user_message = (payload.get('message') or payload.get('question') or '').strip()
            conversation_id = payload.get('conversation_id')
            budget_input = payload.get('budget_input') or {}
            budget_result = payload.get('budget_result') or {}

            if not user_message:
                self._send(400, {'error': 'Missatge buit.'})
                return

            if not conversation_id:
                ctx = _format_budget_for_context(budget_input, budget_result)
                full_question = (
                    f"[CONTEXT DEL PRESSUPOST PERSONALITZAT DEL CLIENT]\n{ctx}\n\n"
                    f"[PREGUNTA DEL CLIENT]\n{user_message}"
                )
            else:
                # Even on follow-up turns, remind the agent of the FORM contract
                # so it doesn't forget across multi-turn conversations.
                full_question = (
                    f"[RECORDATORI · si l'usuari demana canvis al pressupost, "
                    f"afegeix un bloc <!--FORM:{{...}}--> al final amb els camps a actualitzar.]\n\n"
                    f"{user_message}"
                )

            answer, new_cid = _docsgpt_call(full_question, conversation_id)
            answer, raw_updates = _extract_form_from_answer(answer)
            form_updates = _sanitize_form_updates(raw_updates)

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
