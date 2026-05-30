"""
Dev server local · simula el comportament de Vercel per al projecte estàtic.

- Serveix `public/` com a static root
- Suporta `cleanUrls`: `/pressupost` → `pressupost.html`
- Munta `api/calcular.py` i `api/download-pdf.py` com a endpoints POST

Ús:
    python3 dev_server.py            (port 8765)
    PORT=3000 python3 dev_server.py  (port custom)
"""
import os
import sys
import importlib.util
from flask import Flask, request, send_from_directory, jsonify, Response, abort

ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(ROOT, 'public')
API_DIR = os.path.join(ROOT, 'api')

sys.path.insert(0, API_DIR)
from calcular import calculate_budget  # noqa: E402

# Carregar download-pdf.py (no és nom de mòdul Python vàlid pel guió)
_dpdf_spec = importlib.util.spec_from_file_location(
    'download_pdf', os.path.join(API_DIR, 'download-pdf.py')
)
_dpdf = importlib.util.module_from_spec(_dpdf_spec)
_dpdf_spec.loader.exec_module(_dpdf)

# Carregar chat-pressupost.py (per provar el flux complet en local)
_cp_spec = importlib.util.spec_from_file_location(
    'chat_pressupost', os.path.join(API_DIR, 'chat-pressupost.py')
)
_cp = importlib.util.module_from_spec(_cp_spec)
_cp_spec.loader.exec_module(_cp)

# Carregar chat-configurador.py també per coherència
_cc_spec = importlib.util.spec_from_file_location(
    'chat_configurador', os.path.join(API_DIR, 'chat-configurador.py')
)
_cc = importlib.util.module_from_spec(_cc_spec)
_cc_spec.loader.exec_module(_cc)

# Carregar notificar-equip.py (avisos Telegram a l'equip comercial)
_ne_spec = importlib.util.spec_from_file_location(
    'notificar_equip', os.path.join(API_DIR, 'notificar-equip.py')
)
_ne = importlib.util.module_from_spec(_ne_spec)
_ne_spec.loader.exec_module(_ne)

app = Flask(__name__, static_folder=None)


def _proxy_chat_endpoint(module):
    """Reusa la lògica de l'endpoint de Vercel cridant directament les seves
    funcions internes. Així no calen handlers HTTP separats al dev_server."""
    import urllib.error
    payload = request.get_json(silent=True) or {}
    user_message = (payload.get('message') or payload.get('question') or '').strip()
    if not user_message:
        return jsonify({'error': 'Missatge buit.'}), 400
    conversation_id = payload.get('conversation_id')

    try:
        if hasattr(module, '_format_budget_for_context'):
            # chat-pressupost flow
            budget_input  = payload.get('budget_input')  or {}
            budget_result = payload.get('budget_result') or {}
            if not conversation_id:
                ctx = module._format_budget_for_context(budget_input, budget_result)
                full_question = (
                    f"[CONTEXT DEL PRESSUPOST PERSONALITZAT DEL CLIENT]\n{ctx}\n\n"
                    f"[PREGUNTA DEL CLIENT]\n{user_message}"
                )
            else:
                full_question = (
                    "[RECORDATORI · si l'usuari demana canvis al pressupost, "
                    "afegeix un bloc <!--FORM:{...}--> al final amb els camps a actualitzar.]\n\n"
                    + user_message
                )
            answer, new_cid = module._docsgpt_call(full_question, conversation_id)
            answer, raw_updates = module._extract_form_from_answer(answer)
            form_updates = module._sanitize_form_updates(raw_updates)
            return jsonify({
                'answer': answer,
                'conversation_id': new_cid,
                'form_updates': form_updates or None,
            })
        else:
            # chat-configurador flow
            step = payload.get('step', 1)
            cs   = payload.get('config_state') or {}
            if not conversation_id:
                ctx = module._format_config_context(step, cs)
                full_question = (
                    f"[CONTEXT DE CONFIGURACIÓ — PAS {step}]\n{ctx}\n\n"
                    f"[PREGUNTA DE L'USUARI]\n{user_message}"
                )
            else:
                full_question = user_message
            regex_updates = module._extract_form_from_message(user_message, step)
            answer, new_cid = module._docsgpt_call(full_question, conversation_id)
            answer, ai_updates = module._extract_form_from_answer(answer)
            form_updates = {**regex_updates, **ai_updates}
            return jsonify({
                'answer': answer,
                'conversation_id': new_cid,
                'form_updates': form_updates or None,
            })
    except RuntimeError as e:
        # No DOCSGPT_API_KEY a l'entorn local — retornem un missatge clar
        # perquè es vegi al chat però sense esfondrar el dev server.
        return jsonify({
            'answer': "(mode dev sense DOCSGPT_API_KEY) " + str(e),
            'conversation_id': conversation_id,
            'form_updates': None,
        }), 200
    except urllib.error.HTTPError as e:
        return jsonify({'error': f'DocsGPT HTTP {e.code}', 'detail': str(e.reason)}), e.code
    except urllib.error.URLError as e:
        return jsonify({'error': "No s'ha pogut connectar amb DocsGPT", 'detail': str(e.reason)}), 504
    except Exception as e:
        return jsonify({'error': 'server_error', 'detail': str(e)}), 500


@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    data = request.get_json(silent=True) or {}
    return jsonify(calculate_budget(data))


@app.route('/api/chat-pressupost', methods=['POST'])
def api_chat_pressupost():
    return _proxy_chat_endpoint(_cp)


@app.route('/api/chat-configurador', methods=['POST'])
def api_chat_configurador():
    return _proxy_chat_endpoint(_cc)


@app.route('/api/notificar-equip', methods=['POST'])
def api_notificar_equip():
    payload = request.get_json(silent=True) or {}
    status, body = _ne.notify(payload)
    return jsonify(body), status


@app.route('/api/download-pdf', methods=['POST'])
def api_download_pdf():
    data = request.get_json(silent=True) or {}
    payload = data.get('payload', {})
    result = data.get('result', {})
    if not result:
        return jsonify({'error': 'missing_result'}), 400
    pdf_bytes = _dpdf.generate_pdf(payload, result)
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename="pressupost-papik.pdf"',
            'Cache-Control': 'no-store',
        },
    )


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    """Vercel-style static serving with cleanUrls."""
    if path == '':
        return send_from_directory(PUBLIC, 'index.html')

    full = os.path.join(PUBLIC, path)

    # 1. Fitxer existent (qualsevol extensió)
    if os.path.isfile(full):
        return send_from_directory(PUBLIC, path)

    # 2. Carpeta amb index.html
    if os.path.isdir(full) and os.path.isfile(os.path.join(full, 'index.html')):
        return send_from_directory(PUBLIC, os.path.join(path, 'index.html'))

    # 3. cleanUrls: prova `path.html`
    if os.path.isfile(full + '.html'):
        return send_from_directory(PUBLIC, path + '.html')

    abort(404)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8765))
    print(f'\n  PAPIK · dev server\n  http://localhost:{port}\n')
    app.run(host='127.0.0.1', port=port, debug=False, threaded=True)
