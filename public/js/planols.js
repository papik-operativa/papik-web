/* ============================================================
 * PAPIK · Editor de plànols (graella · multi-mode)
 * ------------------------------------------------------------
 * Modes (pestanyes del llenç):
 *   1) Forma      → afegir/moure/redimensionar estances. Murs
 *                   derivats sols (poché exterior + tabics). Forma
 *                   en L per unió. Estances buides (sense mobles).
 *   2) Mobiliari  → paleta de mobles que s'arrosseguen, giren i
 *                   esborren. L'usuari compon cada estança.
 *   3) Obertures  → portes i finestres (fase 2b, properament).
 *
 * Graella de 0,5 m. Multi-planta. Pointer (ratolí + tàctil).
 * Autocontingut: no toca el configurador de pressupost.
 * ============================================================ */
(function () {
  'use strict';

  const CELL_M = 0.5;
  const COLS = 44, ROWS = 30, CPX = 16;
  const VBW = COLS * CPX, VBH = ROWS * CPX;
  const WALL = 4;

  const ROOMS = [
    { key: 'sala',     cls: 'sala',     label: 'Sala-menjador', w: 8, h: 6 },
    { key: 'cuina',    cls: 'cuina',    label: 'Cuina',         w: 5, h: 4 },
    { key: 'dorm',     cls: 'dorm',     label: 'Dormitori',     w: 6, h: 5 },
    { key: 'suite',    cls: 'dorm',     label: 'Suite',         w: 7, h: 6 },
    { key: 'bany',     cls: 'bany',     label: 'Bany',          w: 4, h: 3 },
    { key: 'lavabo',   cls: 'bany',     label: 'Lavabo',        w: 3, h: 2 },
    { key: 'despatx',  cls: 'despatx',  label: 'Despatx',       w: 5, h: 4 },
    { key: 'vestidor', cls: 'vestidor', label: 'Vestidor',      w: 3, h: 3 },
    { key: 'safareig', cls: 'servei',   label: 'Safareig',      w: 3, h: 3 },
    { key: 'rebost',   cls: 'servei',   label: 'Rebost',        w: 3, h: 2 },
    { key: 'escala',   cls: 'escala',   label: 'Escala',        w: 3, h: 5 },
    { key: 'garatge',  cls: 'garatge',  label: 'Garatge',       w: 6, h: 6 },
  ];

  // Mobles (mida en cel·les; dibuix per tipus). w/h en cel·les de 0,5 m.
  const FURN = [
    { key: 'llitDoble', label: 'Llit doble',     w: 3, h: 4, d: 'bed' },
    { key: 'llitIndiv', label: 'Llit individual', w: 2, h: 4, d: 'bed' },
    { key: 'sofa',      label: 'Sofà',           w: 4, h: 2, d: 'sofa' },
    { key: 'taula',     label: 'Taula menjador',  w: 3, h: 2, d: 'table' },
    { key: 'cuina',     label: 'Cuina (bancada)', w: 5, h: 1, d: 'kitchen' },
    { key: 'illa',      label: 'Illa',           w: 3, h: 2, d: 'island' },
    { key: 'nevera',    label: 'Nevera',         w: 2, h: 2, d: 'fridge' },
    { key: 'desk',      label: 'Taula despatx',   w: 3, h: 2, d: 'desk' },
    { key: 'armari',    label: 'Armari',         w: 3, h: 1, d: 'wardrobe' },
    { key: 'wc',        label: 'WC',             w: 1, h: 2, d: 'wc' },
    { key: 'sink',      label: 'Lavabo',         w: 2, h: 1, d: 'sink' },
    { key: 'dutxa',     label: 'Dutxa',          w: 2, h: 2, d: 'shower' },
    { key: 'banyera',   label: 'Banyera',        w: 4, h: 2, d: 'bath' },
  ];

  const MODES = [
    { key: 'forma', label: 'Forma' },
    { key: 'moble', label: 'Mobiliari' },
    { key: 'obre',  label: 'Obertures' },
  ];

  const state = {
    plantes: 1, floor: 0, mode: 'forma', tool: 'door',
    floors: [{ rooms: [], furn: [], openings: [] }],
    selRoom: null, selFurn: null, nextId: 1, nextFurn: 1, nextOpen: 1,
  };

  function flo () { return state.floors[state.floor]; }
  function rooms () { return flo().rooms; }
  function furns () { return flo().furn; }
  function opens () { return flo().openings || (flo().openings = []); }

  function ensureFloors () {
    while (state.floors.length < state.plantes) state.floors.push({ rooms: [], furn: [], openings: [] });
    state.floors.length = state.plantes;
    state.floor = Math.max(0, Math.min(state.floor, state.plantes - 1));
  }

  // ── Geometria d'estances ──
  function overlaps (a, b) { return a.c < b.c + b.cw && a.c + a.cw > b.c && a.r < b.r + b.ch && a.r + a.ch > b.r; }
  function collides (room, id) { return rooms().some((o) => o.id !== id && overlaps(room, o)); }
  function inBounds (room) { return room.c >= 0 && room.r >= 0 && room.c + room.cw <= COLS && room.r + room.ch <= ROWS; }
  function occSet () {
    const s = new Set();
    rooms().forEach((o) => { for (let c = o.c; c < o.c + o.cw; c++) for (let r = o.r; r < o.r + o.ch; r++) s.add(c + ',' + r); });
    return s;
  }
  function sideExterior (room, side, occ) {
    if (side === 'L') { for (let r = room.r; r < room.r + room.ch; r++) if (!occ.has((room.c - 1) + ',' + r)) return true; return false; }
    if (side === 'R') { for (let r = room.r; r < room.r + room.ch; r++) if (!occ.has((room.c + room.cw) + ',' + r)) return true; return false; }
    if (side === 'T') { for (let c = room.c; c < room.c + room.cw; c++) if (!occ.has(c + ',' + (room.r - 1))) return true; return false; }
    for (let c = room.c; c < room.c + room.cw; c++) if (!occ.has(c + ',' + (room.r + room.ch))) return true; return false;
  }

  // ── Parets (vores de graella) i obertures ──
  function ownerMap () {
    const m = new Map();
    rooms().forEach((o) => { for (let c = o.c; c < o.c + o.cw; c++) for (let r = o.r; r < o.r + o.ch; r++) m.set(c + ',' + r, o.id); });
    return m;
  }
  // Tipus de paret en una vora: 'ext', 'int' o null (no hi ha paret).
  function edgeWall (orient, c, r, own) {
    let a, b;
    if (orient === 'V') { a = own.get((c - 1) + ',' + r); b = own.get(c + ',' + r); }
    else { a = own.get(c + ',' + (r - 1)); b = own.get(c + ',' + r); }
    if (a == null && b == null) return null;
    if (a != null && b != null) return a === b ? null : 'int';
    return 'ext';
  }
  function wallEdges (own) {
    const seen = new Set(), list = [];
    own.forEach((id, key) => {
      const p = key.split(','), c = +p[0], r = +p[1];
      [['V', c, r], ['V', c + 1, r], ['H', c, r], ['H', c, r + 1]].forEach((e) => {
        const k = e[0] + ',' + e[1] + ',' + e[2]; if (seen.has(k)) return; seen.add(k);
        const t = edgeWall(e[0], e[1], e[2], own); if (t) list.push({ orient: e[0], c: e[1], r: e[2], type: t });
      });
    });
    return list;
  }

  function F (n) { return Math.round(n * 10) / 10; }

  // Dibuixa una obertura (porta/finestra/pas) sobre una vora de paret.
  function drawOpening (op, own) {
    const t = edgeWall(op.orient, op.c, op.r, own) || 'ext';
    let s = '';
    if (op.orient === 'V') {
      const xl = op.c * CPX, y0 = op.r * CPX, y1 = y0 + CPX;
      const leftOcc = own.get((op.c - 1) + ',' + op.r) != null;
      let g0, g1;
      if (t === 'int') { g0 = xl - WALL / 2; g1 = xl + WALL / 2; }
      else if (leftOcc) { g0 = xl - WALL; g1 = xl; }
      else { g0 = xl; g1 = xl + WALL; }
      s += `<rect class="planta-win-gap" x="${F(g0)}" y="${F(y0)}" width="${F(g1 - g0)}" height="${CPX}"/>`;
      if (op.type === 'door') {
        const dir = leftOcc ? -1 : 1;
        s += `<line class="planta-door" x1="${F(xl)}" y1="${F(y0)}" x2="${F(xl + dir * CPX)}" y2="${F(y0)}"/>`;
        s += `<path class="planta-door" d="M ${F(xl + dir * CPX)} ${F(y0)} A ${CPX} ${CPX} 0 0 ${dir > 0 ? 1 : 0} ${F(xl)} ${F(y1)}"/>`;
      } else if (op.type === 'window') {
        s += `<line class="planta-window" x1="${F(xl)}" y1="${F(y0)}" x2="${F(xl)}" y2="${F(y1)}"/>`;
      }
    } else {
      const yl = op.r * CPX, x0 = op.c * CPX, x1 = x0 + CPX;
      const topOcc = own.get(op.c + ',' + (op.r - 1)) != null;
      let g0, g1;
      if (t === 'int') { g0 = yl - WALL / 2; g1 = yl + WALL / 2; }
      else if (topOcc) { g0 = yl - WALL; g1 = yl; }
      else { g0 = yl; g1 = yl + WALL; }
      s += `<rect class="planta-win-gap" x="${F(x0)}" y="${F(g0)}" width="${CPX}" height="${F(g1 - g0)}"/>`;
      if (op.type === 'door') {
        const dir = topOcc ? -1 : 1;
        s += `<line class="planta-door" x1="${F(x0)}" y1="${F(yl)}" x2="${F(x0)}" y2="${F(yl + dir * CPX)}"/>`;
        s += `<path class="planta-door" d="M ${F(x0)} ${F(yl + dir * CPX)} A ${CPX} ${CPX} 0 0 ${dir > 0 ? 0 : 1} ${F(x1)} ${F(yl)}"/>`;
      } else if (op.type === 'window') {
        s += `<line class="planta-window" x1="${F(x0)}" y1="${F(yl)}" x2="${F(x1)}" y2="${F(yl)}"/>`;
      }
    }
    return s;
  }

  // ── Símbols de mobiliari (coords locals 0..W,0..H en px) ──
  function drawFurn (kind, W, H) {
    const R = (x, y, w, h, rx) => `<rect class="planta-fx" x="${F(x)}" y="${F(y)}" width="${F(w)}" height="${F(h)}"${rx ? ` rx="${rx}"` : ''}/>`;
    const L = (x1, y1, x2, y2) => `<line class="planta-fx" x1="${F(x1)}" y1="${F(y1)}" x2="${F(x2)}" y2="${F(y2)}"/>`;
    const C = (x, y, r) => `<circle class="planta-fx" cx="${F(x)}" cy="${F(y)}" r="${F(r)}"/>`;
    const E = (x, y, rx, ry) => `<ellipse class="planta-fx" cx="${F(x)}" cy="${F(y)}" rx="${F(rx)}" ry="${F(ry)}"/>`;
    let s = '';
    if (kind === 'bed') {
      s += R(0, 0, W, H, 3);
      s += R(W * 0.12, H * 0.06, W * 0.76, H * 0.16, 2); // coixí
      s += L(0, H * 0.32, W, H * 0.32);                  // límit edredó
    } else if (kind === 'sofa') {
      s += R(0, 0, W, H, 3);
      s += R(0, 0, W, H * 0.28, 2);                       // respatller
      s += L(W * 0.5, H * 0.28, W * 0.5, H);
    } else if (kind === 'table') {
      s += R(W * 0.16, H * 0.18, W * 0.68, H * 0.64, 2);
      [[0.5, 0.06], [0.5, 0.94], [0.08, 0.5], [0.92, 0.5]].forEach(([px, py]) => { s += C(W * px, H * py, Math.min(W, H) * 0.07); });
    } else if (kind === 'kitchen') {
      s += R(0, 0, W, H);
      s += C(W * 0.2, H * 0.5, H * 0.3); s += C(W * 0.35, H * 0.5, H * 0.3); // fogons
      s += R(W * 0.62, H * 0.2, W * 0.28, H * 0.6, 1);    // pica
    } else if (kind === 'island') {
      s += R(0, 0, W, H, 2); s += C(W * 0.3, H * 0.5, H * 0.18);
    } else if (kind === 'fridge') {
      s += R(0, 0, W, H, 2); s += L(0, H * 0.5, W, H * 0.5); s += L(W * 0.8, H * 0.2, W * 0.8, H * 0.4);
    } else if (kind === 'desk') {
      s += R(0, 0, W, H * 0.55, 1); s += C(W * 0.5, H * 0.8, Math.min(W, H) * 0.12);
    } else if (kind === 'wardrobe') {
      s += R(0, 0, W, H); s += L(W * 0.5, 0, W * 0.5, H);
    } else if (kind === 'wc') {
      s += R(W * 0.15, 0, W * 0.7, H * 0.28, 1); s += E(W * 0.5, H * 0.62, W * 0.4, H * 0.34);
    } else if (kind === 'sink') {
      s += R(0, 0, W, H, 2); s += E(W * 0.5, H * 0.55, W * 0.32, H * 0.3); s += C(W * 0.5, H * 0.16, 1.4);
    } else if (kind === 'shower') {
      s += R(0, 0, W, H); s += L(0, 0, W, H); s += L(W, 0, 0, H); s += C(W * 0.5, H * 0.5, 1.6);
    } else if (kind === 'bath') {
      s += R(0, 0, W, H, 4); s += E(W * 0.46, H * 0.5, W * 0.36, H * 0.32); s += C(W * 0.85, H * 0.5, 1.6);
    }
    return s;
  }

  // ── Render ──
  let svg, elModes, elTabs, elPanel, elInfo;

  function gridSVG () {
    let g = '';
    for (let c = 0; c <= COLS; c++) g += `<line class="pl-gl${c % 2 === 0 ? ' pl-gl--m' : ''}" x1="${c * CPX}" y1="0" x2="${c * CPX}" y2="${VBH}"/>`;
    for (let r = 0; r <= ROWS; r++) g += `<line class="pl-gl${r % 2 === 0 ? ' pl-gl--m' : ''}" x1="0" y1="${r * CPX}" x2="${VBW}" y2="${r * CPX}"/>`;
    return g;
  }

  function draw () {
    const occ = occSet();
    const own = ownerMap();
    let base = `<g class="pl-gridlayer">${gridSVG()}</g>`;
    let poche = '', inners = '', labels = '';

    rooms().forEach((o) => {
      const x = o.c * CPX, y = o.r * CPX, w = o.cw * CPX, h = o.ch * CPX;
      poche += `<rect class="planta-wall-fill" x="${F(x)}" y="${F(y)}" width="${F(w)}" height="${F(h)}"/>`;
      const iL = sideExterior(o, 'L', occ) ? WALL : WALL / 2, iR = sideExterior(o, 'R', occ) ? WALL : WALL / 2;
      const iT = sideExterior(o, 'T', occ) ? WALL : WALL / 2, iB = sideExterior(o, 'B', occ) ? WALL : WALL / 2;
      inners += `<rect class="planta-room-fill" x="${F(x + iL)}" y="${F(y + iT)}" width="${F(w - iL - iR)}" height="${F(h - iT - iB)}"/>`;
      const m2 = o.cw * o.ch * CELL_M * CELL_M;
      if (w > 44 && h > 30) {
        labels += `<text class="planta-room__name" x="${F(x + w / 2)}" y="${F(y + h / 2 - 4)}" text-anchor="middle" dominant-baseline="middle">${o.label}</text>`;
        labels += `<text class="planta-room__sub" x="${F(x + w / 2)}" y="${F(y + h / 2 + 8)}" text-anchor="middle" dominant-baseline="middle">${m2.toFixed(1)} m²</text>`;
      }
    });

    // Mobiliari (sempre visible; editable només en mode 'moble')
    let furnSVG = '';
    furns().forEach((it) => {
      const W = it.w * CPX, H = it.h * CPX, x = it.c * CPX, y = it.r * CPX;
      const sel = state.mode === 'moble' && state.selFurn === it.id;
      const lock = state.mode !== 'moble';
      furnSVG += `<g class="pl-furn${lock ? ' pl-furn--lock' : ''}${sel ? ' is-sel' : ''}" data-furn="${it.id}" transform="translate(${F(x)},${F(y)}) rotate(${it.rot || 0} ${F(W / 2)} ${F(H / 2)})">`;
      furnSVG += `<rect class="pl-furn__hit" x="0" y="0" width="${F(W)}" height="${F(H)}"/>`;
      furnSVG += drawFurn(it.d, W, H);
      if (sel) {
        furnSVG += `<rect class="pl-furn__sel" x="-1" y="-1" width="${F(W + 2)}" height="${F(H + 2)}"/>`;
        furnSVG += `<g class="pl-rot" data-role="rot" data-furn="${it.id}"><circle cx="0" cy="0" r="8"/><path d="M -3 -1 A 3 3 0 1 1 -2.2 2" fill="none"/><path d="M -3 -3 L -3 -0.5 L -0.7 -1.2 Z"/></g>`;
        furnSVG += `<g class="pl-del" data-role="delf" data-furn="${it.id}"><circle cx="${F(W)}" cy="0" r="8"/><line x1="${F(W - 3)}" y1="-3" x2="${F(W + 3)}" y2="3"/><line x1="${F(W + 3)}" y1="-3" x2="${F(W - 3)}" y2="3"/></g>`;
      }
      furnSVG += `</g>`;
    });

    // Obertures (sempre visibles; s'amaguen si ja no toquen cap paret)
    let openSVG = '';
    opens().forEach((op) => { if (edgeWall(op.orient, op.c, op.r, own)) openSVG += drawOpening(op, own); });

    // Capa d'interacció d'estances (només mode 'forma')
    let overlay = '';
    if (state.mode === 'obre') {
      const HS = 7;
      wallEdges(own).forEach((e) => {
        if (e.orient === 'V') overlay += `<rect class="pl-hot" data-edge="V,${e.c},${e.r}" x="${F(e.c * CPX - HS / 2)}" y="${F(e.r * CPX)}" width="${HS}" height="${CPX}"/>`;
        else overlay += `<rect class="pl-hot" data-edge="H,${e.c},${e.r}" x="${F(e.c * CPX)}" y="${F(e.r * CPX - HS / 2)}" width="${CPX}" height="${HS}"/>`;
      });
    }
    if (state.mode === 'forma') {
      rooms().forEach((o) => {
        const x = o.c * CPX, y = o.r * CPX, w = o.cw * CPX, h = o.ch * CPX;
        const sel = state.selRoom === o.id;
        overlay += `<g class="pl-room${sel ? ' is-sel' : ''}" data-id="${o.id}">` +
          `<rect class="pl-room__hit" x="${F(x)}" y="${F(y)}" width="${F(w)}" height="${F(h)}"/>`;
        if (sel) {
          overlay += `<rect class="pl-room__sel" x="${F(x)}" y="${F(y)}" width="${F(w)}" height="${F(h)}"/>`;
          overlay += `<rect class="pl-handle" data-role="resize" data-id="${o.id}" x="${F(x + w - 9)}" y="${F(y + h - 9)}" width="14" height="14" rx="2"/>`;
          overlay += `<g class="pl-del" data-role="del" data-id="${o.id}"><circle cx="${F(x + w - 2)}" cy="${F(y + 2)}" r="8"/><line x1="${F(x + w - 5)}" y1="${F(y - 1)}" x2="${F(x + w + 1)}" y2="${F(y + 5)}"/><line x1="${F(x + w + 1)}" y1="${F(y - 1)}" x2="${F(x + w - 5)}" y2="${F(y + 5)}"/></g>`;
        }
        overlay += `</g>`;
      });
    }

    svg.innerHTML = base + poche + inners + labels + openSVG + furnSVG + overlay;
    renderInfo();
  }

  function renderModes () {
    elModes.innerHTML = MODES.map((m) => `<button type="button" class="pl-mode${state.mode === m.key ? ' is-active' : ''}${m.soon ? ' is-soon' : ''}" data-mode="${m.key}">${m.label}${m.soon ? ' <span class="pl-soon">aviat</span>' : ''}</button>`).join('');
  }

  function renderTabs () {
    let h = '';
    for (let f = 0; f < state.plantes; f++) {
      const n = state.floors[f] ? state.floors[f].rooms.length : 0;
      h += `<button type="button" class="pl-tab${f === state.floor ? ' is-active' : ''}" data-floor="${f}">${f === 0 ? 'Planta baixa' : 'Planta ' + f} <span class="pl-tab__n">${n}</span></button>`;
    }
    elTabs.innerHTML = h;
  }

  function renderPanel () {
    let plantes = '';
    [1, 2, 3].forEach((p) => { plantes += `<button type="button" class="pl-seg${state.plantes === p ? ' is-active' : ''}" data-plantes="${p}">${p}</button>`; });
    const plantesField = `<div class="pl-field"><label class="pl-field__label">Plantes</label><div class="pl-seg-group">${plantes}</div></div>`;

    if (state.mode === 'forma') {
      const chips = ROOMS.map((it) => `<button type="button" class="pl-chip" data-add="${it.key}">+ ${it.label}</button>`).join('');
      elPanel.innerHTML = plantesField +
        `<div class="pl-field"><label class="pl-field__label">Afegeix estances</label><div class="pl-chips">${chips}</div></div>` +
        `<div class="pl-field"><div class="pl-info" id="plInfo"></div></div>` +
        `<p class="pl-help">Arrossega per moure · tira de la cantonada per redimensionar · ✕ per esborrar. Col·loca-les com vulguis (fins i tot en L).</p>`;
    } else if (state.mode === 'moble') {
      const chips = FURN.map((it) => `<button type="button" class="pl-chip" data-furn-add="${it.key}">+ ${it.label}</button>`).join('');
      elPanel.innerHTML = plantesField +
        `<div class="pl-field"><label class="pl-field__label">Afegeix mobles</label><div class="pl-chips">${chips}</div></div>` +
        `<div class="pl-field"><div class="pl-info" id="plInfo"></div></div>` +
        `<p class="pl-help">Arrossega els mobles per col·locar-los · ↻ per girar · ✕ per esborrar. Compon cada estança com vulguis.</p>`;
    } else {
      const tools = [['door', 'Porta'], ['window', 'Finestra'], ['open', 'Pas obert']]
        .map(([k, l]) => `<button type="button" class="pl-seg${state.tool === k ? ' is-active' : ''}" data-tool="${k}">${l}</button>`).join('');
      elPanel.innerHTML = plantesField +
        `<div class="pl-field"><label class="pl-field__label">Eina</label><div class="pl-seg-group pl-seg-group--wrap">${tools}</div></div>` +
        `<div class="pl-field"><div class="pl-info" id="plInfo"></div></div>` +
        `<p class="pl-help">Clica un tram de paret per posar-hi l'element triat. Torna a clicar-lo per treure'l. El <b>pas obert</b> serveix per obrir la cuina a la sala. Crea primer la forma al mode Forma.</p>`;
    }
    elInfo = document.getElementById('plInfo');
  }

  function renderInfo () {
    if (!elInfo) return;
    const m2 = rooms().reduce((s, o) => s + o.cw * o.ch * CELL_M * CELL_M, 0);
    let h = `<div class="pl-info__row"><span>Estances</span><b>${rooms().length}</b></div>` +
            `<div class="pl-info__row"><span>Superfície planta</span><b>${m2.toFixed(1)} m²</b></div>`;
    if (state.mode === 'forma') {
      const sel = rooms().find((o) => o.id === state.selRoom);
      if (sel) h += `<div class="pl-info__row pl-info__row--sel"><span>${sel.label}</span><b>${(sel.cw * CELL_M).toFixed(1)} × ${(sel.ch * CELL_M).toFixed(1)} m</b></div>`;
    } else if (state.mode === 'moble') {
      h += `<div class="pl-info__row"><span>Mobles</span><b>${furns().length}</b></div>`;
    } else if (state.mode === 'obre') {
      const o = opens();
      h += `<div class="pl-info__row"><span>Portes</span><b>${o.filter((x) => x.type === 'door').length}</b></div>`;
      h += `<div class="pl-info__row"><span>Finestres</span><b>${o.filter((x) => x.type === 'window').length}</b></div>`;
    }
    elInfo.innerHTML = h;
  }

  // ── Afegir ──
  function freeSpot (w, h) {
    for (let r = 1; r + h <= ROWS - 1; r++) for (let c = 1; c + w <= COLS - 1; c++) if (!collides({ c, r, cw: w, ch: h }, -1)) return { c, r };
    return { c: 1, r: 1 };
  }
  function addRoom (key) {
    const it = ROOMS.find((p) => p.key === key); if (!it) return;
    const s = freeSpot(it.w, it.h);
    rooms().push({ id: state.nextId++, cls: it.cls, label: it.label, c: s.c, r: s.r, cw: it.w, ch: it.h });
    state.selRoom = state.nextId - 1; renderTabs(); draw();
  }
  function addFurn (key) {
    const it = FURN.find((p) => p.key === key); if (!it) return;
    const c = Math.round(COLS / 2 - it.w / 2), r = Math.round(ROWS / 2 - it.h / 2);
    furns().push({ id: state.nextFurn++, d: it.d, label: it.label, c: c, r: r, w: it.w, h: it.h, rot: 0 });
    state.selFurn = state.nextFurn - 1; draw();
  }

  // ── Interacció ──
  let drag = null;
  function evCell (e) {
    const rect = svg.getBoundingClientRect();
    return { c: (e.clientX - rect.left) / rect.width * VBW / CPX, r: (e.clientY - rect.top) / rect.height * VBH / CPX };
  }
  const snap2 = (v) => Math.round(v * 2) / 2;

  function onDown (e) {
    if (state.mode === 'forma') {
      const del = e.target.closest('[data-role="del"]');
      if (del) { const a = rooms(), i = a.findIndex((o) => o.id === +del.dataset.id); if (i >= 0) a.splice(i, 1); state.selRoom = null; renderTabs(); draw(); return; }
      const hz = e.target.closest('[data-role="resize"]');
      if (hz) { const o = rooms().find((x) => x.id === +hz.dataset.id); state.selRoom = o.id; drag = { mode: 'resize', id: o.id }; try { svg.setPointerCapture(e.pointerId); } catch (x) {} draw(); e.preventDefault(); return; }
      const rm = e.target.closest('.pl-room');
      if (rm) { const o = rooms().find((x) => x.id === +rm.dataset.id); state.selRoom = o.id; const cl = evCell(e); drag = { mode: 'move', id: o.id, offC: cl.c - o.c, offR: cl.r - o.r }; try { svg.setPointerCapture(e.pointerId); } catch (x) {} draw(); e.preventDefault(); return; }
      if (state.selRoom != null) { state.selRoom = null; draw(); }
    } else if (state.mode === 'moble') {
      const del = e.target.closest('[data-role="delf"]');
      if (del) { const a = furns(), i = a.findIndex((o) => o.id === +del.dataset.furn); if (i >= 0) a.splice(i, 1); state.selFurn = null; draw(); return; }
      const rot = e.target.closest('[data-role="rot"]');
      if (rot) { const o = furns().find((x) => x.id === +rot.dataset.furn); o.rot = ((o.rot || 0) + 90) % 360; state.selFurn = o.id; draw(); return; }
      const fg = e.target.closest('.pl-furn');
      if (fg) { const o = furns().find((x) => x.id === +fg.dataset.furn); state.selFurn = o.id; const cl = evCell(e); drag = { mode: 'furn', id: o.id, offC: cl.c - o.c, offR: cl.r - o.r }; try { svg.setPointerCapture(e.pointerId); } catch (x) {} draw(); e.preventDefault(); return; }
      if (state.selFurn != null) { state.selFurn = null; draw(); }
    } else if (state.mode === 'obre') {
      const hot = e.target.closest('.pl-hot');
      if (hot) {
        const p = hot.dataset.edge.split(','), orient = p[0], c = +p[1], r = +p[2];
        const arr = opens();
        const i = arr.findIndex((o) => o.orient === orient && o.c === c && o.r === r);
        if (i >= 0) { if (arr[i].type === state.tool) arr.splice(i, 1); else arr[i].type = state.tool; }
        else arr.push({ id: state.nextOpen++, orient, c, r, type: state.tool });
        draw();
      }
    }
  }

  function onMove (e) {
    if (!drag) return;
    const cl = evCell(e);
    if (drag.mode === 'move') {
      const o = rooms().find((x) => x.id === drag.id); if (!o) return;
      const nc = Math.round(cl.c - drag.offC), nr = Math.round(cl.r - drag.offR);
      const cand = { c: nc, r: nr, cw: o.cw, ch: o.ch };
      if (inBounds(cand) && !collides(cand, o.id)) { o.c = nc; o.r = nr; draw(); }
    } else if (drag.mode === 'resize') {
      const o = rooms().find((x) => x.id === drag.id); if (!o) return;
      const ncw = Math.max(2, Math.round(cl.c - o.c)), nch = Math.max(2, Math.round(cl.r - o.r));
      const cand = { c: o.c, r: o.r, cw: ncw, ch: nch };
      if (inBounds(cand) && !collides(cand, o.id)) { o.cw = ncw; o.ch = nch; draw(); }
    } else if (drag.mode === 'furn') {
      const o = furns().find((x) => x.id === drag.id); if (!o) return;
      o.c = Math.max(0, Math.min(COLS - o.w, snap2(cl.c - drag.offC)));
      o.r = Math.max(0, Math.min(ROWS - o.h, snap2(cl.r - drag.offR)));
      draw();
    }
    e.preventDefault();
  }
  function onUp () { drag = null; }

  function onClick (e) {
    const mode = e.target.closest('.pl-mode');
    if (mode) { state.mode = mode.dataset.mode; state.selRoom = null; state.selFurn = null; renderModes(); renderPanel(); draw(); return; }
    const tab = e.target.closest('.pl-tab');
    if (tab) { state.floor = +tab.dataset.floor || 0; state.selRoom = null; state.selFurn = null; renderTabs(); draw(); return; }
    const tool = e.target.closest('[data-tool]');
    if (tool) { state.tool = tool.dataset.tool; renderPanel(); draw(); return; }
    const seg = e.target.closest('.pl-seg');
    if (seg) { state.plantes = +seg.dataset.plantes || 1; ensureFloors(); renderPanel(); renderTabs(); draw(); return; }
    const add = e.target.closest('[data-add]');
    if (add) { addRoom(add.dataset.add); return; }
    const fadd = e.target.closest('[data-furn-add]');
    if (fadd) { addFurn(fadd.dataset.furnAdd); return; }
  }

  function init () {
    svg = document.getElementById('plSvg');
    elModes = document.getElementById('plModes');
    elTabs = document.getElementById('plTabs');
    elPanel = document.getElementById('plPanel');
    if (!svg || !elModes || !elTabs || !elPanel) return;
    svg.setAttribute('viewBox', `0 0 ${VBW} ${VBH}`);
    renderModes(); renderPanel(); renderTabs(); draw();
    document.addEventListener('click', onClick);
    svg.addEventListener('pointerdown', onDown);
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
