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

app = Flask(__name__, static_folder=None)


@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    data = request.get_json(silent=True) or {}
    return jsonify(calculate_budget(data))


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
