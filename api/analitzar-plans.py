"""
Vercel Python Serverless Function · POST /api/analitzar-plans

Analitza plànols arquitectònics (PDF + imatges) amb GPT-4o Vision i
retorna els camps del configurador (m², plantes, banys, garatge…).

Per als PDFs fem rasterització a PNG amb PyMuPDF (fitz). Així GPT-4o
Vision rep imatges reals del plànol enlloc de només el text extret,
que en plànols CAD és pràcticament inservible (cotes soltes, etiquetes
disperses). Això recupera la capacitat del sistema Flask original
que feia servir pdf2image (Poppler), no disponible al runtime de
Vercel — PyMuPDF du la seva pròpia llibreria MuPDF dins del wheel.

API key: variable d'entorn `OPENAI_API_KEY` configurada a Vercel.

Body JSON esperat:
{
  "files": [
    { "name": "plano.pdf", "mime": "application/pdf", "data_b64": "JVBE…" },
    ...                                                    (màx. 3)
  ]
}
"""
from http.server import BaseHTTPRequestHandler
import base64
import io
import json
import os
import re


OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
SQ_FT_TO_M2 = 0.09290304

PROMPT_PLANS = """You are an expert residential architectural plan reader.

You receive 1–4 HIGH-RESOLUTION images of pages from the SAME single-family
house project (floor plans, sections, elevations, title blocks, area
schedules). For PDF inputs the pages have been rasterised to PNG so you
can READ THE DRAWING VISUALLY just like a human architect would. You
may also receive extracted text from the source PDF as supplementary
context, but the IMAGES ARE YOUR PRIMARY SOURCE — read dimensions,
room layouts and labels off the actual drawing.

Your task: extract technical data and return ONLY a valid JSON object.
No explanations, no markdown.

═══ EXTRACTION RULES ═══

1. TOTAL AREA (m²) — CRITICAL: this field MUST be a number for any legible
   architectural plan. NEVER return null unless the plan is genuinely unreadable.
   Use this priority, falling through if a higher option is unavailable:

   a. EXPLICIT total: look in title blocks, area schedules, summary tables
      for "Superfície", "Superficie", "Area", "Built area", "Living area",
      "Construïda", "Útil", "m²", "m2", "sqft", "SF". Take the largest
      reasonable value.

   b. SUM of per-floor areas if a table lists them (e.g. PB: 80 m², P1: 75 m²
      → total 155 m²).

   c. VISUAL ESTIMATE — this is the most common path for CAD plans without
      explicit area labels. ALGORITHM:
       1. Identify the OVERALL EXTERIOR rectangle of the building footprint
          (the outermost outline of one floor plan).
       2. Read the largest LONGITUDINAL dimension off the cotes (typical
          residential: 8–25 m).
       3. Read the largest TRANSVERSE dimension off the cotes (typical
          residential: 4–15 m).
       4. Compute footprint_m² = longitudinal × transverse.
       5. total_m² = footprint_m² × number_of_habitable_floors × 0.92
          (the 0.92 factor accounts for wall thickness + stair voids).
       6. Return that number. Use confidence 0.4–0.6 for estimates this way.

   Examples: cotes "12,76" and "5,69" with 3 floors → 12.76 × 5.69 × 3 × 0.92
   ≈ 200 m². Cotes "9,50" and "8,20" with 2 floors → 9.5 × 8.2 × 2 × 0.92
   ≈ 143 m².

   If the area is given in sq ft / SF, convert: 1 sq ft = 0.092903 m².
   Return ONLY m².

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


# ── PDF helpers ─────────────────────────────────────────────────────────────

def _clean_pdf_text(text):
    if not text:
        return ''
    text = re.sub(r'(.)\1{4,}', r'\1', text)
    text = re.sub(r'[^\x20-\x7E\xA0-\xFF\n\r\t]', ' ', text)
    text = re.sub(r'[ \t]{3,}', ' ', text)
    return text.strip()


def _extract_areas_from_text(text):
    areas = []
    if not text:
        return areas
    m2_patterns = [
        r'(\d[\d\s.,]{0,8})\s*m[²2]',
        r'(?:superfici[ea]|àrea|area|total|construïda?|construida?|habitable)'
        r'[^\d]{0,40}(\d[\d.,]{1,6})\s*m',
        r'm[²2]\s*[:\-–]?\s*(\d[\d.,]{1,6})',
    ]
    for pat in m2_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            try:
                v = float(m.group(1).replace(' ', '').replace(',', '.'))
                if 30 < v < 5000:
                    ctx = text[max(0, m.start() - 40):m.end() + 40].strip()
                    areas.append({'value': v, 'unit': 'm2', 'context': ctx})
            except Exception:
                pass
    sqft_patterns = [
        r'(\d[\d,]{1,6})\s*(?:sq\.?\s*ft\.?|SF|square\s*fe?e?t)',
        r'(?:area|floor|total|living|gross)[^\d]{0,40}(\d[\d,]{1,6})\s*(?:sq\.?\s*ft\.?|SF)',
        r'(?:sq\.?\s*ft\.?|SF)\s*[:\-–]?\s*(\d[\d,]{1,6})',
    ]
    for pat in sqft_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            try:
                v = float(m.group(1).replace(',', ''))
                if 300 < v < 54000:
                    ctx = text[max(0, m.start() - 40):m.end() + 40].strip()
                    areas.append({'value': v, 'unit': 'sqft', 'context': ctx})
            except Exception:
                pass
    return areas


def _sqft_to_m2(v):
    return round(v * SQ_FT_TO_M2, 1)


def _best_area_from_texts(page_texts):
    candidates = []
    for txt in page_texts:
        for a in _extract_areas_from_text(txt):
            v_m2 = a['value'] if a['unit'] == 'm2' else _sqft_to_m2(a['value'])
            if 50 < v_m2 < 1500:
                candidates.append({'value_m2': v_m2, 'context': a['context'],
                                   'unit': a['unit'], 'raw': a['value']})
    return max(candidates, key=lambda c: c['value_m2']) if candidates else None


def _estimate_m2_from_cotes(page_texts, floors):
    """Last-resort estimator: scan all cota-style numbers (e.g. 12,76)
    and assume the two largest plausible dimensions are the exterior
    bounding box. Multiply by the floor count and a 0.92 wall/voids
    factor. Returns {'m2', 'a', 'b', 'floors'} or None if implausible."""
    candidates = []
    for txt in page_texts:
        # Match numbers with at least one decimal: 12,76 / 12.76 / 5,69 …
        for m in re.finditer(r'\b(\d{1,2}[.,]\d{1,2})\b', txt or ''):
            try:
                v = float(m.group(1).replace(',', '.'))
            except ValueError:
                continue
            # Realistic exterior dimension range for residential (in metres).
            # Anything below 3 m is a room dimension, above 30 m is a parcel.
            if 3.0 <= v <= 30.0:
                candidates.append(v)
    if len(candidates) < 2:
        return None
    candidates.sort(reverse=True)
    a, b = candidates[0], candidates[1]
    f = max(1, int(floors or 1))
    estimated = a * b * f * 0.92
    if 50 <= estimated <= 800:
        return {'m2': round(estimated), 'a': a, 'b': b, 'floors': f}
    return None


def _score_pdf_page(text):
    """Heuristic relevance score for a PDF page based on its text.
    Higher score = more likely to be a floor plan with measurable data."""
    score = 0
    t = (text or '').lower()

    # Floor plan keywords (CA / ES / EN)
    floor_kws = ['planta baixa', 'planta primera', 'planta segunda', 'planta pis',
                 'ground floor', 'first floor', 'second floor', 'floor plan',
                 'pb', 'p1', 'p2', 'plano', 'plante']
    if any(kw in t for kw in floor_kws):
        score += 6
    if 'acotada' in t or 'dimensioned' in t or 'cotat' in t:
        score += 10

    # Area / surface mentions
    area_kws = ['superfície', 'superficie', 'àrea', 'area', 'm²', 'm2',
                'sq ft', 'sqft', 'square feet', 'square foot',
                'habitable', 'construïda', 'construida', 'útil']
    if any(kw in t for kw in area_kws):
        score += 6
    if _extract_areas_from_text(t):
        score += 12

    # Rooms / spaces
    rooms = ['bany', 'wc', 'lavabo', 'toilet', 'bathroom', 'bath',
             'garatge', 'garaje', 'garage', 'parking',
             'porxo', 'porche', 'porch', 'terrassa', 'terraza',
             'dormitori', 'habitació', 'bedroom', 'living', 'cuina', 'kitchen']
    score += min(2 * sum(1 for kw in rooms if kw in t), 14)

    # Numeric dimensions (e.g. 3.50 / 4,20)
    dim_count = len(re.findall(r'\b\d+[.,]\d{2}\b', t))
    score += min(dim_count // 2, 10)

    # Penalise non-plan pages
    for kw in ['elevation', 'alçat', 'façana', 'fachada', 'section', 'secció',
               'cover', 'portada', 'index', 'notes', 'specifications']:
        if kw in t:
            score -= 3
    return score


def _pdf_pages_to_images_and_text(raw_bytes, max_pages=4, dpi=200):
    """Render the most relevant pages of a PDF as PNG + extract their
    text using PyMuPDF (fitz). PyMuPDF ships its own MuPDF binary in
    the wheel, so it works on the Vercel runtime without Poppler.

    Returns (list_of_b64_pngs, list_of_text_per_page) for up to
    `max_pages` pages ordered by descending relevance score."""
    images, texts = [], []
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return images, texts

    try:
        doc = fitz.open(stream=raw_bytes, filetype='pdf')
    except Exception:
        return images, texts

    try:
        total = doc.page_count
        # Score every page; if the document only has a few pages we
        # still want them all (a single-page residential floor plan is
        # very common, e.g. the Pellaires-31 test case).
        scored = []
        for i in range(total):
            try:
                txt = _clean_pdf_text(doc[i].get_text('text') or '')
            except Exception:
                txt = ''
            scored.append((_score_pdf_page(txt), i, txt))

        if total <= max_pages:
            chosen = sorted(range(total))           # keep original order
            chosen = [(scored[i][1], scored[i][2]) for i in chosen]
        else:
            scored.sort(reverse=True)
            top = scored[:max_pages]
            top.sort(key=lambda x: x[1])             # restore reading order
            chosen = [(idx, txt) for _, idx, txt in top]

        for idx, txt in chosen:
            try:
                page = doc[idx]
                # 144 DPI = good legibility for cotes without bloating
                # the payload (Vercel body limit is 4.5 MB on Hobby).
                pix = page.get_pixmap(dpi=dpi, alpha=False)
                png_bytes = pix.tobytes('png')
                images.append(base64.b64encode(png_bytes).decode('ascii'))
                texts.append(txt)
            except Exception:
                # Skip the offending page but keep going
                pass
    finally:
        doc.close()

    return images, texts


# ── Validació post-extracció ────────────────────────────────────────────────

def _validate_extraction(extracted, page_texts=None):
    if not isinstance(extracted, dict):
        return extracted

    m2 = extracted.get('m2')
    floors = extracted.get('floors')
    bathrooms = extracted.get('num_bathrooms')
    confidence = float(extracted.get('confidence', 0.5))
    issues = []

    if m2 is not None:
        if m2 > 700:
            converted = _sqft_to_m2(m2)
            if 50 < converted < 800:
                extracted['m2'] = converted
                extracted['_auto_converted'] = f'Convertit automàticament de {m2:.0f} sq ft → {converted} m²'
                confidence = max(0.0, confidence - 0.10)
                issues.append('auto_sqft_conversion')
            else:
                confidence = max(0.0, confidence - 0.30)
                issues.append('m2_too_large')
        elif m2 < 25:
            confidence = max(0.0, confidence - 0.30)
            issues.append('m2_too_small')

    if floors is not None and (floors < 1 or floors > 4):
        confidence = max(0.0, confidence - 0.20)
        issues.append('floors_out_of_range')

    if bathrooms is not None and (bathrooms < 1 or bathrooms > 8):
        confidence = max(0.0, confidence - 0.20)
        issues.append('bathrooms_out_of_range')

    if m2 is not None and floors is not None and floors > 0:
        per_floor = extracted.get('m2', m2) / floors
        if per_floor > 600:
            confidence = max(0.0, confidence - 0.15)
            issues.append('high_m2_per_floor')
        elif per_floor < 20:
            confidence = max(0.0, confidence - 0.20)
            issues.append('low_m2_per_floor')

    if extracted.get('m2') is None and page_texts:
        best = _best_area_from_texts(page_texts)
        if best:
            extracted['m2'] = best['value_m2']
            extracted['_text_fallback'] = (
                f"m² recuperat del text PDF: '{best['context']}'"
                + (f' ({best["raw"]:.0f} sq ft)' if best['unit'] == 'sqft' else '')
            )
            confidence = max(0.3, confidence - 0.05)
            issues.append('m2_from_text_fallback')
        else:
            # Last-ditch heuristic: scan the cotes (numbers like 12,76)
            # and assume the two largest plausible dimensions are the
            # exterior bounding box. Multiply by the floor count.
            est = _estimate_m2_from_cotes(page_texts, extracted.get('floors'))
            if est:
                extracted['m2'] = est['m2']
                extracted['_cotes_fallback'] = (
                    f"m² estimat de cotes: {est['a']:.2f}×{est['b']:.2f} "
                    f"× {est['floors']} plantes"
                )
                confidence = max(0.3, confidence - 0.20)
                issues.append('m2_from_cotes_fallback')

    extracted['confidence'] = round(max(0.0, min(1.0, confidence)), 2)
    if issues:
        extracted['_validation_issues'] = issues
    return extracted


# ── Mapeig EN → CA per al frontend ──────────────────────────────────────────

FIELD_MAP = {
    'floors':        'plantes',
    'num_bathrooms': 'num_banys',
    'garage':        'garatge',
    'm2_garage':     'm2_garatge',
    'porches':       'porxos',
    'm2_porches':    'm2_porxos',
}


def _analyse(files):
    """Crida OpenAI Vision i retorna el dict de camps. Llença excepcions."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY no configurada al servidor. "
            "Defineix-la com a variable d'entorn al projecte de Vercel."
        )

    # Import only when we'll actually call OpenAI — keeps cold-start cheap
    # when the function is invoked without files.
    import openai

    content_images = []
    all_page_texts = []

    for f in files[:3]:
        name = (f.get('name') or '').lower()
        mime = (f.get('mime') or '').lower()
        b64 = f.get('data_b64') or ''
        if not b64:
            continue

        try:
            raw = base64.b64decode(b64, validate=False)
        except Exception:
            continue

        is_pdf = mime == 'application/pdf' or name.endswith('.pdf')
        is_img = (
            mime in ('image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif')
            or name.endswith(('.png', '.jpg', '.jpeg', '.webp'))
        )

        if is_pdf:
            # Rasterise the most relevant pages to PNG so Vision can
            # actually SEE the drawing (text-only extraction on a CAD
            # plan returns just dimension numbers with no context).
            pdf_imgs, pdf_texts = _pdf_pages_to_images_and_text(raw, max_pages=4)
            for png_b64 in pdf_imgs:
                content_images.append({
                    'type': 'image_url',
                    'image_url': {
                        'url': f'data:image/png;base64,{png_b64}',
                        'detail': 'high',
                    },
                })
            all_page_texts.extend(pdf_texts)
        elif is_img:
            data_url = f'data:{mime or "image/png"};base64,{b64}'
            content_images.append({
                'type': 'image_url',
                'image_url': {'url': data_url, 'detail': 'high'},
            })

    if not content_images and not any(t.strip() for t in all_page_texts):
        raise ValueError('Formats acceptats: PDF, PNG, JPG, WEBP.')

    text_context = ''
    if all_page_texts:
        combined = '\n---\n'.join(t for t in all_page_texts if t.strip())
        if combined.strip():
            combined = combined[:3000]
            text_context = (
                f'\n\nEXTRACTED TEXT FROM PDF (use this to help identify areas, '
                f'room names and dimensions):\n"""\n{combined}\n"""'
            )

    prompt_with_context = PROMPT_PLANS + text_context
    content = [{'type': 'text', 'text': prompt_with_context}] + content_images

    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model='gpt-4o',
        max_tokens=900,
        temperature=0,
        messages=[{'role': 'user', 'content': content}],
    )
    raw = (response.choices[0].message.content or '').strip()

    if '```' in raw:
        parts = raw.split('```')
        raw = parts[1] if len(parts) > 1 else raw
        if raw.lower().startswith('json'):
            raw = raw[4:]
    raw = raw.strip()

    extracted = json.loads(raw)
    extracted = _validate_extraction(extracted, page_texts=all_page_texts)

    mapped = {}
    for k, v in extracted.items():
        mapped[FIELD_MAP.get(k, k)] = v
    return mapped


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
            if length <= 0:
                self._send(400, {'error': 'empty_body'})
                return
            raw = self.rfile.read(length).decode('utf-8')
            payload = json.loads(raw)

            files = payload.get('files') or []
            if not isinstance(files, list) or not files:
                self._send(400, {'error': "No s'han rebut fitxers."})
                return

            mapped = _analyse(files)
            self._send(200, mapped)

        except ValueError as e:
            self._send(400, {'error': str(e)})
        except RuntimeError as e:
            self._send(503, {'error': str(e)})
        except json.JSONDecodeError:
            self._send(500, {'error': "No s'ha pogut interpretar la resposta de la IA."})
        except Exception as e:
            # Mantenim missatge amigable a la UI però guardem detalls als logs
            try:
                import openai as _o
                if isinstance(e, _o.AuthenticationError):
                    self._send(401, {'error': 'Clau API OpenAI incorrecta.'})
                    return
                if isinstance(e, _o.RateLimitError):
                    self._send(429, {'error': 'OpenAI ha limitat les peticions. Torna-ho a provar.'})
                    return
            except Exception:
                pass
            self._send(500, {'error': 'server_error', 'detail': str(e)})

    def do_GET(self):
        self._send(405, {'error': 'method_not_allowed', 'detail': 'use POST'})
