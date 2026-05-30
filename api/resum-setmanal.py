"""
Vercel Python Serverless Function · GET /api/resum-setmanal

Resum setmanal per al cap: quants clients han configurat un pressupost
('lead') i quants han reservat visita ('reserva') durant els darrers 7
dies, amb desglossament de prioritat, volum configurat i top municipis.

El dispara un Vercel Cron Job (vercel.json -> "crons") cada dilluns al
mati. Llegeix les dades de Supabase via la funcio RPC `resum_setmanal`
i envia el missatge a un SEGON bot de Telegram (diferent del d'avisos en
calent), perque el destinatari del resum no es el mateix que el comercial.

Stdlib only. Variables d'entorn al projecte de Vercel:

    SUPABASE_URL                 https://<ref>.supabase.co
    SUPABASE_SERVICE_KEY         service_role key (secreta, server-side)
    TELEGRAM_RESUM_BOT_TOKEN     token del segon bot (@BotFather)
    TELEGRAM_RESUM_CHAT_ID       xat/grup on rep el resum el cap
    CRON_SECRET                  (opcional) protegeix l'endpoint; Vercel
                                 l'envia com a 'Authorization: Bearer ...'

Si falten Supabase o el bot, respon 200 amb {ok:false, skipped:...}
perque el cron no es marqui com a fallit.
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
import urllib.request
import urllib.error


SUPABASE_URL             = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_SERVICE_KEY     = os.environ.get('SUPABASE_SERVICE_KEY', '')
TELEGRAM_RESUM_BOT_TOKEN = os.environ.get('TELEGRAM_RESUM_BOT_TOKEN', '')
TELEGRAM_RESUM_CHAT_ID   = os.environ.get('TELEGRAM_RESUM_CHAT_ID', '')
CRON_SECRET              = os.environ.get('CRON_SECRET', '')
TELEGRAM_API             = 'https://api.telegram.org'


def _esc(value):
    s = '' if value is None else str(value)
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _fmt_eur(n):
    try:
        return f"{int(round(float(n))):,}".replace(',', '.') + ' €'
    except (TypeError, ValueError):
        return '—'


def _fetch_resum(days):
    """Crida la RPC resum_setmanal(days) a Supabase. Torna el dict de
    resultat o llanca RuntimeError('not_configured') si no hi ha credencials."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError('not_configured')
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/rpc/resum_setmanal",
        data=json.dumps({'days': days}).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _format_message(data):
    days     = data.get('days') or 7
    leads    = int(data.get('leads') or 0)
    reserves = int(data.get('reserves') or 0)
    alta     = int(data.get('leads_alta') or 0)
    mitjana  = int(data.get('leads_mitjana') or 0)
    baixa    = int(data.get('leads_baixa') or 0)
    suma     = data.get('suma_total') or 0
    mitja    = data.get('mitjana_total') or 0
    tops     = data.get('top_municipis') or []

    lines = [
        "\U0001F4CA <b>Resum setmanal · PAPIK Atelier</b>",  # 📊
        f"\U0001F5D3️ Darrers {days} dies",             # 🗓️
        '',
    ]

    if leads == 0 and reserves == 0:
        lines.append("Aquesta setmana no hi ha hagut activitat a l'atelier.")
        lines.append('')
        lines.append("\U0001F4A1 Bon moment per impulsar una acció de captació.")  # 💡
        return '\n'.join(lines)

    lines.append(f"\U0001F3D7️ <b>Pressupostos configurats:</b> {leads}")  # 🏗️
    if leads:
        lines.append(f"   \U0001F534 {alta} alta · \U0001F7E1 {mitjana} mitjana · \U0001F4A4 {baixa} baixa")
    lines.append(f"\U0001F4C5 <b>Visites reservades:</b> {reserves}")  # 📅
    if leads:
        conv = round(reserves * 100.0 / leads)
        lines.append(f"\U0001F504 Conversió a visita: {conv}%")  # 🔄
    lines.append('')

    lines.append(f"\U0001F4B0 Volum configurat: <b>{_fmt_eur(suma)}</b>")  # 💰
    if leads:
        lines.append(f"   Mitjana per pressupost: {_fmt_eur(mitja)}")
    lines.append("   <i>(IVA inclòs, fonamentació a part)</i>")

    if tops:
        lines.append('')
        lines.append("\U0001F4CD <b>Top municipis</b>")  # 📍
        for i, t in enumerate(tops, 1):
            muni = _esc(t.get('municipi'))
            n = int(t.get('n') or 0)
            lines.append(f"   {i}. {muni} · {n}")

    return '\n'.join(lines)


def _send_telegram(text):
    if not TELEGRAM_RESUM_BOT_TOKEN or not TELEGRAM_RESUM_CHAT_ID:
        raise RuntimeError('not_configured')
    req = urllib.request.Request(
        f"{TELEGRAM_API}/bot{TELEGRAM_RESUM_BOT_TOKEN}/sendMessage",
        data=json.dumps({
            'chat_id': TELEGRAM_RESUM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def run(days=7):
    try:
        data = _fetch_resum(days)
    except RuntimeError:
        return 200, {'ok': False, 'skipped': 'supabase_not_configured'}
    except urllib.error.HTTPError as e:
        return 502, {'ok': False, 'error': f'supabase_http_{e.code}', 'detail': e.reason}
    except urllib.error.URLError as e:
        return 504, {'ok': False, 'error': 'supabase_unreachable', 'detail': str(e.reason)}

    text = _format_message(data if isinstance(data, dict) else {})
    try:
        result = _send_telegram(text)
    except RuntimeError:
        return 200, {'ok': False, 'skipped': 'telegram_not_configured', 'data': data}
    if not result.get('ok'):
        return 502, {'ok': False, 'error': 'telegram_error', 'detail': result}
    return 200, {'ok': True, 'data': data}


def _authorized(headers, query):
    """Si CRON_SECRET esta definit, exigeix-lo (header Authorization que
    Vercel envia automaticament, o ?key=). Si no, permet (dev/local)."""
    if not CRON_SECRET:
        return True
    auth = headers.get('Authorization') or headers.get('authorization') or ''
    if auth == f'Bearer {CRON_SECRET}':
        return True
    if (query.get('key') or [''])[0] == CRON_SECRET:
        return True
    return False


class handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode('utf-8'))

    def _handle(self):
        try:
            q = parse_qs(urlparse(self.path).query)
            if not _authorized(self.headers, q):
                return self._send(401, {'ok': False, 'error': 'unauthorized'})
            try:
                days = int((q.get('days') or ['7'])[0])
            except ValueError:
                days = 7
            days = max(1, min(days, 90))
            status, body = run(days)
            self._send(status, body)
        except Exception as e:
            self._send(500, {'ok': False, 'error': 'server_error', 'detail': str(e)})

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()
