"""
Vercel Python Serverless Function · POST /api/notificar-equip

Avisa l'equip comercial de PAPIK per Telegram quan un client acaba de
configurar un pressupost a l'atelier ('lead') o reserva una visita
comercial ('reserva'). El missatge inclou un resum de la configuració,
les dades de contacte i una etiqueta de PRIORITAT calculada al frontend
(pressupost alt · municipi objectiu · superfície gran).

Connecta amb el flux de Cal.eu: la 'reserva' es dispara des de l'event
`bookingSuccessful` de l'embed, així el cap rep al mòbil qui acaba
d'agendar i a quina franja, a banda de l'avís propi de Cal a la seva
agenda.

Stdlib only. Sense cap dependència nova. Configuració per variables
d'entorn al projecte de Vercel:

    TELEGRAM_BOT_TOKEN   token del bot creat amb @BotFather
    TELEGRAM_CHAT_ID     id del xat (o grup) on rebre els avisos

Si falten, l'endpoint respon 200 amb {ok:false, skipped:"not_configured"}
perquè el frontend (fire-and-forget) no peti i tot segueixi funcionant
fins que l'equip configuri el bot.
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error


TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID   = os.environ.get('TELEGRAM_CHAT_ID', '')
TELEGRAM_API       = 'https://api.telegram.org'

# Persistencia opcional a Supabase (font del resum setmanal). Si no hi ha
# credencials, l'esdeveniment no es desa pero l'avis de Telegram segueix.
SUPABASE_URL         = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')


# ── Etiquetes ───────────────────────────────────────────────────────────────
PRIORITY_BADGE = {
    'alta':    '\U0001F534 PRIORITAT ALTA',     # 🔴
    'mitjana': '\U0001F7E1 Prioritat mitjana',  # 🟡
    'baixa':   '\U0001F4A4 Prioritat baixa',    # 💤
}
EVENT_HEADER = {
    'lead':    '\U0001F195 Nou pressupost configurat',  # 🆕
    'reserva': '\U0001F4C5 VISITA RESERVADA',           # 📅
}

GARATGE_LABEL = {'si': 'Sí', 'no': 'No'}


def _esc(value):
    """Escapa el mínim per a parse_mode=HTML de Telegram (& < >)."""
    s = '' if value is None else str(value)
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _fmt_eur(n):
    try:
        return f"{int(round(float(n))):,}".replace(',', '.') + ' €'
    except (TypeError, ValueError):
        return '—'


def _fmt_num(n):
    try:
        return f"{int(round(float(n)))}"
    except (TypeError, ValueError):
        return '—'


def _format_message(payload):
    """Construeix el text HTML del missatge de Telegram a partir del cos
    enviat pel frontend. Tot el contingut d'usuari va escapat."""
    event    = (payload.get('event') or 'lead').strip().lower()
    priority = payload.get('priority') or {}
    lead     = payload.get('lead') or {}
    summary  = payload.get('summary') or {}
    slot     = payload.get('slot')

    level   = (priority.get('level') or 'baixa').strip().lower()
    reasons = priority.get('reasons') or []

    header = EVENT_HEADER.get(event, EVENT_HEADER['lead'])
    badge  = PRIORITY_BADGE.get(level, PRIORITY_BADGE['baixa'])

    lines = [f"<b>{header}</b>", badge, '']

    # Motius de la prioritat
    if reasons:
        motius = ', '.join(_esc(r) for r in reasons if r)
        if motius:
            lines.append(f"\U0001F4CC {motius}")  # 📌
            lines.append('')

    # Contacte
    nom     = (lead.get('nom') or '').strip()
    email   = (lead.get('email') or '').strip()
    telefon = (lead.get('telefon') or '').strip()
    lines.append('<b>Contacte</b>')
    lines.append(f"\U0001F464 {_esc(nom) or '—'}")             # 👤
    if telefon:
        lines.append(f"\U0001F4F1 {_esc(telefon)}")            # 📱
    if email:
        lines.append(f"✉️ {_esc(email)}")            # ✉️
    lines.append('')

    # Resum de la configuració
    lines.append('<b>Configuració</b>')
    if summary.get('municipi'):
        lines.append(f"\U0001F4CD {_esc(summary.get('municipi'))}")  # 📍
    detall = []
    if summary.get('m2'):
        detall.append(f"{_fmt_num(summary.get('m2'))} m²")
    if summary.get('plantes'):
        p = str(summary.get('plantes'))
        detall.append('1 planta' if p == '1' else f"{_esc(p)} plantes")
    if summary.get('num_banys'):
        nb = summary.get('num_banys')
        detall.append(f"{_fmt_num(nb)} bany" + ('' if str(nb) == '1' else 's'))
    if summary.get('num_habitacions'):
        nh = summary.get('num_habitacions')
        detall.append(f"{_fmt_num(nh)} hab.")
    if detall:
        lines.append('\U0001F4D0 ' + ' · '.join(detall))  # 📐
    gar = (summary.get('garatge') or '').strip().lower()
    if gar in GARATGE_LABEL:
        g = f"Garatge: {GARATGE_LABEL[gar]}"
        if gar == 'si' and summary.get('m2_garatge'):
            g += f" ({_fmt_num(summary.get('m2_garatge'))} m²)"
        lines.append('\U0001F697 ' + g)  # 🚗
    if summary.get('total'):
        lines.append(f"\U0001F4B0 <b>{_fmt_eur(summary.get('total'))}</b> (IVA inclòs, fonamentació a part)")  # 💰

    # Franja reservada (només event 'reserva')
    if slot:
        lines.append('')
        lines.append(f"\U0001F557 <b>Franja:</b> {_esc(slot)}")  # 🕗

    return '\n'.join(lines)


def _as_num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _as_int(v):
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None


def _store_supabase(payload):
    """Desa l'esdeveniment a la taula atelier_events via PostgREST amb la
    service_role key. Best-effort: torna False si no esta configurat o si
    falla, sense propagar mai l'error (no ha de tombar l'avis de Telegram)."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return False
    event = (payload.get('event') or 'lead').strip().lower()
    if event not in ('lead', 'reserva'):
        event = 'lead'
    pr   = payload.get('priority') or {}
    lead = payload.get('lead') or {}
    s    = payload.get('summary') or {}
    reasons = [r for r in (pr.get('reasons') or []) if r]

    row = {
        'event':            event,
        'priority_level':   (pr.get('level') or None),
        'priority_reasons': reasons or None,
        'nom':              (lead.get('nom') or None),
        'email':            (lead.get('email') or None),
        'telefon':          (lead.get('telefon') or None),
        'municipi':         (s.get('municipi') or None),
        'm2':               _as_num(s.get('m2')),
        'plantes':          (str(s.get('plantes')) if s.get('plantes') is not None else None),
        'num_banys':        _as_int(s.get('num_banys')),
        'num_habitacions':  _as_int(s.get('num_habitacions')),
        'garatge':          (s.get('garatge') or None),
        'm2_garatge':       _as_num(s.get('m2_garatge')),
        'total':            _as_num(s.get('total')),
        'slot':             (payload.get('slot') or None),
        'raw':              payload,
    }
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/atelier_events",
            data=json.dumps(row).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'apikey': SUPABASE_SERVICE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                'Prefer': 'return=minimal',
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def _send_telegram(text):
    """Envia el missatge a Telegram. Retorna el dict de resposta de l'API.
    Llança RuntimeError si no hi ha token/chat configurats."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError('not_configured')

    url = f"{TELEGRAM_API}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body = json.dumps({
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }).encode('utf-8')

    req = urllib.request.Request(
        url, data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def notify(payload):
    """Orquestra l'enviament. No llança per 'not_configured' (retorna
    skipped) perquè el frontend és fire-and-forget."""
    if not isinstance(payload, dict):
        return 400, {'ok': False, 'error': 'invalid_input'}
    # Persistencia best-effort (resum setmanal). No bloqueja l'avis.
    _store_supabase(payload)
    text = _format_message(payload)
    try:
        result = _send_telegram(text)
    except RuntimeError:
        return 200, {'ok': False, 'skipped': 'not_configured'}
    if not result.get('ok'):
        return 502, {'ok': False, 'error': 'telegram_error', 'detail': result}
    return 200, {'ok': True}


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
            status, body = notify(payload)
            self._send(status, body)
        except urllib.error.HTTPError as e:
            self._send(502, {'ok': False, 'error': f'telegram_http_{e.code}', 'detail': e.reason})
        except urllib.error.URLError as e:
            self._send(504, {'ok': False, 'error': 'telegram_unreachable', 'detail': str(e.reason)})
        except (ValueError, TypeError) as e:
            self._send(400, {'ok': False, 'error': 'invalid_input', 'detail': str(e)})
        except Exception as e:
            self._send(500, {'ok': False, 'error': 'server_error', 'detail': str(e)})

    def do_GET(self):
        self._send(405, {'error': 'method_not_allowed', 'detail': 'use POST'})
