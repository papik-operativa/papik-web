/* ============================================================
 * PAPIK · Editor de plànols (rejilla · arrossegar i redimensionar)
 * ------------------------------------------------------------
 * Llenç en blanc sobre una graella de 0,5 m. L'usuari afegeix
 * estances des de la paleta i les arrossega / redimensiona on
 * vol. Els murs (poché exterior + tabics interiors) es deriven
 * sols de la disposició; la forma en L surt de la unió. Multi-
 * planta. Esquema il·lustratiu, no és el plànol executiu.
 *
 * Autocontingut: no toca atelier.js ni el configurador de
 * pressupost. Reutilitza les classes CSS planta-*.
 * Fase 2a: geometria + arrossegar. Portes/finestres = fase 2b.
 * ============================================================ */
(function () {
  'use strict';

  const CELL_M = 0.5;        // metres per cel·la
  const COLS = 44, ROWS = 30;
  const CPX = 16;            // píxels per cel·la (viewBox)
  const VBW = COLS * CPX, VBH = ROWS * CPX;
  const WALL = 4;            // gruix de mur (px)

  const PALETTE = [
    { key: 'sala',     cls: 'sala',     label: 'Sala-menjador', w: 8, h: 6 },
    { key: 'cuina',    cls: 'cuina',    label: 'Cuina',         w: 5, h: 4 },
    { key: 'dorm',     cls: 'dorm',     label: 'Dormitori',     w: 6, h: 5 },
    { key: 'suite',    cls: 'dorm',     label: 'Suite',         w: 7, h: 6 },
    { key: 'bany',     cls: 'bany',     label: 'Bany',          w: 4, h: 3 },
    { key: 'lavabo',   cls: 'bany',     label: 'Lavabo',        w: 3, h: 2 },
    { key: 'cuinaoffice', cls: 'cuina', label: 'Office',        w: 4, h: 3 },
    { key: 'despatx',  cls: 'despatx',  label: 'Despatx',       w: 5, h: 4 },
    { key: 'vestidor', cls: 'vestidor', label: 'Vestidor',      w: 3, h: 3 },
    { key: 'safareig', cls: 'servei',   label: 'Safareig',      w: 3, h: 3 },
    { key: 'rebost',   cls: 'servei',   label: 'Rebost',        w: 3, h: 2 },
    { key: 'escala',   cls: 'escala',   label: 'Escala',        w: 3, h: 5 },
    { key: 'garatge',  cls: 'garatge',  label: 'Garatge',       w: 6, h: 6 },
  ];

  const state = { plantes: 1, floor: 0, floors: [[]], selected: null, nextId: 1 };

  function curRooms () { return state.floors[state.floor]; }

  function ensureFloors () {
    while (state.floors.length < state.plantes) state.floors.push([]);
    state.floors.length = state.plantes;
    if (state.floor > state.plantes - 1) state.floor = state.plantes - 1;
    if (state.floor < 0) state.floor = 0;
  }

  // ── Geometria de cel·les ──
  function overlaps (a, b) {
    return a.c < b.c + b.cw && a.c + a.cw > b.c && a.r < b.r + b.ch && a.r + a.ch > b.r;
  }
  function collides (room, exceptId) {
    return curRooms().some((o) => o.id !== exceptId && overlaps(room, o));
  }
  function inBounds (room) {
    return room.c >= 0 && room.r >= 0 && room.c + room.cw <= COLS && room.r + room.ch <= ROWS;
  }
  function occSet () {
    const s = new Set();
    curRooms().forEach((o) => { for (let c = o.c; c < o.c + o.cw; c++) for (let r = o.r; r < o.r + o.ch; r++) s.add(c + ',' + r); });
    return s;
  }
  // Una vora és exterior si alguna cel·la veïna a través seu és buida.
  function sideExterior (room, side, occ) {
    if (side === 'L') { for (let r = room.r; r < room.r + room.ch; r++) if (!occ.has((room.c - 1) + ',' + r)) return true; return false; }
    if (side === 'R') { for (let r = room.r; r < room.r + room.ch; r++) if (!occ.has((room.c + room.cw) + ',' + r)) return true; return false; }
    if (side === 'T') { for (let c = room.c; c < room.c + room.cw; c++) if (!occ.has(c + ',' + (room.r - 1))) return true; return false; }
    for (let c = room.c; c < room.c + room.cw; c++) if (!occ.has(c + ',' + (room.r + room.ch))) return true; return false;
  }

  // ── Helpers de dibuix (reutilitzats de l'atelier) ──
  function F (n) { return Math.round(n * 10) / 10; }

  function furnish (cls, r) {
    const pad = Math.min(r.w, r.h) * 0.14;
    const x = r.x + pad, y = r.y + pad, w = r.w - 2 * pad, h = r.h - 2 * pad;
    if (w < 14 || h < 14) return '';
    const cx = x + w / 2;
    let s = '';
    if (cls === 'sala') {
      const sw = Math.min(w * 0.62, w), sh = Math.min(h * 0.26, 16);
      const sx = cx - sw / 2, sy = y + h - sh;
      s += `<rect class="planta-fx" x="${F(sx)}" y="${F(sy)}" width="${F(sw)}" height="${F(sh)}" rx="2"/>`;
      s += `<line class="planta-fx" x1="${F(sx)}" y1="${F(sy + sh * 0.42)}" x2="${F(sx + sw)}" y2="${F(sy + sh * 0.42)}"/>`;
      const tw = sw * 0.5, th = Math.min(sh * 0.6, 8);
      s += `<rect class="planta-fx" x="${F(cx - tw / 2)}" y="${F(sy - th - 5)}" width="${F(tw)}" height="${F(th)}" rx="1"/>`;
    } else if (cls === 'cuina') {
      const d = Math.min(h * 0.24, 11);
      s += `<rect class="planta-fx" x="${F(x)}" y="${F(y)}" width="${F(w)}" height="${F(d)}"/>`;
      s += `<rect class="planta-fx" x="${F(x)}" y="${F(y)}" width="${F(d)}" height="${F(h)}"/>`;
      s += `<circle class="planta-fx" cx="${F(x + w * 0.6)}" cy="${F(y + d / 2)}" r="${F(d * 0.28)}"/>`;
    } else if (cls === 'dorm') {
      const bw = Math.min(w * 0.62, 42), bh = Math.min(h * 0.72, 48);
      const bx = cx - bw / 2, by = y;
      s += `<rect class="planta-fx" x="${F(bx)}" y="${F(by)}" width="${F(bw)}" height="${F(bh)}" rx="2"/>`;
      s += `<line class="planta-fx" x1="${F(bx)}" y1="${F(by + bh * 0.26)}" x2="${F(bx + bw)}" y2="${F(by + bh * 0.26)}"/>`;
    } else if (cls === 'bany') {
      const tw = Math.min(w * 0.9, w), th = Math.min(h * 0.32, 14);
      s += `<rect class="planta-fx" x="${F(x)}" y="${F(y)}" width="${F(tw)}" height="${F(th)}" rx="3"/>`;
      s += `<ellipse class="planta-fx" cx="${F(x + w - 7)}" cy="${F(y + h - 8)}" rx="5" ry="6"/>`;
    } else if (cls === 'escala') {
      const steps = Math.max(4, Math.round(h / 7));
      for (let i = 0; i <= steps; i++) { const yy = y + (h / steps) * i; s += `<line class="planta-fx" x1="${F(x)}" y1="${F(yy)}" x2="${F(x + w)}" y2="${F(yy)}"/>`; }
      s += `<line class="planta-fx" x1="${F(cx)}" y1="${F(y)}" x2="${F(cx)}" y2="${F(y + h)}"/>`;
    } else if (cls === 'garatge') {
      const bw = Math.min(w * 0.5, 42), bh = Math.min(h * 0.78, 72);
      const bx = cx - bw / 2, by = y + (h - bh) / 2;
      s += `<rect class="planta-fx" x="${F(bx)}" y="${F(by)}" width="${F(bw)}" height="${F(bh)}" rx="6"/>`;
    }
    return s;
  }

  function roomPx (o) { return { x: o.c * CPX, y: o.r * CPX, w: o.cw * CPX, h: o.ch * CPX }; }

  // ── Render ──
  let svg, elPalette, elTabs, elInfo;

  function gridSVG () {
    let g = '';
    for (let c = 0; c <= COLS; c++) g += `<line class="pl-gl${c % 2 === 0 ? ' pl-gl--m' : ''}" x1="${c * CPX}" y1="0" x2="${c * CPX}" y2="${VBH}"/>`;
    for (let r = 0; r <= ROWS; r++) g += `<line class="pl-gl${r % 2 === 0 ? ' pl-gl--m' : ''}" x1="0" y1="${r * CPX}" x2="${VBW}" y2="${r * CPX}"/>`;
    return g;
  }

  function draw () {
    const rooms = curRooms();
    const occ = occSet();
    let body = `<g class="pl-gridlayer">${gridSVG()}</g>`;

    // Poché (mur exterior) de cada estança
    let poche = '', inners = '', fx = '', labels = '', overlay = '';
    rooms.forEach((o) => {
      const p = roomPx(o);
      poche += `<rect class="planta-wall-fill" x="${F(p.x)}" y="${F(p.y)}" width="${F(p.w)}" height="${F(p.h)}"/>`;
      const iL = sideExterior(o, 'L', occ) ? WALL : WALL / 2;
      const iR = sideExterior(o, 'R', occ) ? WALL : WALL / 2;
      const iT = sideExterior(o, 'T', occ) ? WALL : WALL / 2;
      const iB = sideExterior(o, 'B', occ) ? WALL : WALL / 2;
      const ix = p.x + iL, iy = p.y + iT, iw = p.w - iL - iR, ih = p.h - iT - iB;
      inners += `<rect class="planta-room-fill" x="${F(ix)}" y="${F(iy)}" width="${F(iw)}" height="${F(ih)}"/>`;
      const inner = { x: ix, y: iy, w: iw, h: ih };
      fx += furnish(o.cls, inner);
      const m2 = (o.cw * o.ch * CELL_M * CELL_M);
      if (iw > 40 && ih > 26) {
        labels += `<text class="planta-room__name" x="${F(p.x + p.w / 2)}" y="${F(p.y + p.h / 2 - 4)}" text-anchor="middle" dominant-baseline="middle">${o.label}</text>`;
        labels += `<text class="planta-room__sub" x="${F(p.x + p.w / 2)}" y="${F(p.y + p.h / 2 + 8)}" text-anchor="middle" dominant-baseline="middle">${m2.toFixed(1)} m²</text>`;
      }
      // capa de selecció / interacció
      const sel = state.selected === o.id;
      overlay += `<g class="pl-room${sel ? ' is-sel' : ''}" data-id="${o.id}">` +
        `<rect class="pl-room__hit" x="${F(p.x)}" y="${F(p.y)}" width="${F(p.w)}" height="${F(p.h)}"/>`;
      if (sel) {
        overlay += `<rect class="pl-room__sel" x="${F(p.x)}" y="${F(p.y)}" width="${F(p.w)}" height="${F(p.h)}"/>`;
        overlay += `<rect class="pl-handle" data-role="resize" data-id="${o.id}" x="${F(p.x + p.w - 9)}" y="${F(p.y + p.h - 9)}" width="14" height="14" rx="2"/>`;
        overlay += `<g class="pl-del" data-role="del" data-id="${o.id}"><circle cx="${F(p.x + p.w - 2)}" cy="${F(p.y + 2)}" r="8"/><line x1="${F(p.x + p.w - 5)}" y1="${F(p.y - 1)}" x2="${F(p.x + p.w + 1)}" y2="${F(p.y + 5)}"/><line x1="${F(p.x + p.w + 1)}" y1="${F(p.y - 1)}" x2="${F(p.x + p.w - 5)}" y2="${F(p.y + 5)}"/></g>`;
      }
      overlay += `</g>`;
    });

    svg.innerHTML = body + poche + inners + fx + labels + overlay;
    renderInfo();
  }

  function renderTabs () {
    let h = '';
    for (let f = 0; f < state.plantes; f++) {
      const n = state.floors[f] ? state.floors[f].length : 0;
      const lbl = f === 0 ? 'Planta baixa' : ('Planta ' + f);
      h += `<button type="button" class="pl-tab${f === state.floor ? ' is-active' : ''}" data-floor="${f}">${lbl} <span class="pl-tab__n">${n}</span></button>`;
    }
    elTabs.innerHTML = h;
  }

  function renderPalette () {
    let plantes = '';
    [1, 2, 3].forEach((p) => { plantes += `<button type="button" class="pl-seg${state.plantes === p ? ' is-active' : ''}" data-plantes="${p}">${p}</button>`; });
    let chips = PALETTE.map((it) => `<button type="button" class="pl-chip" data-add="${it.key}">+ ${it.label}</button>`).join('');
    elPalette.innerHTML = `
      <div class="pl-field"><label class="pl-field__label">Plantes</label><div class="pl-seg-group">${plantes}</div></div>
      <div class="pl-field"><label class="pl-field__label">Afegeix estances</label><div class="pl-chips">${chips}</div></div>
      <div class="pl-field"><div class="pl-info" id="plInfo"></div></div>
      <p class="pl-help">Arrossega per moure · tira de la cantonada per redimensionar · toca una estança i la ✕ per esborrar. Col·loca-les com vulguis (fins i tot en forma de L).</p>`;
    elInfo = document.getElementById('plInfo');
  }

  function renderInfo () {
    if (!elInfo) return;
    const rooms = curRooms();
    const m2 = rooms.reduce((s, o) => s + o.cw * o.ch * CELL_M * CELL_M, 0);
    const sel = rooms.find((o) => o.id === state.selected);
    elInfo.innerHTML = `<div class="pl-info__row"><span>Estances</span><b>${rooms.length}</b></div>` +
      `<div class="pl-info__row"><span>Superfície planta</span><b>${m2.toFixed(1)} m²</b></div>` +
      (sel ? `<div class="pl-info__row pl-info__row--sel"><span>${sel.label}</span><b>${(sel.cw * CELL_M).toFixed(1)} × ${(sel.ch * CELL_M).toFixed(1)} m</b></div>` : '');
  }

  // ── Afegir / esborrar ──
  function freeSpot (w, h) {
    for (let r = 1; r + h <= ROWS - 1; r++) for (let c = 1; c + w <= COLS - 1; c++) {
      const cand = { c, r, cw: w, ch: h };
      if (!collides(cand, -1)) return { c, r };
    }
    return { c: 1, r: 1 };
  }
  function addRoom (key) {
    const it = PALETTE.find((p) => p.key === key); if (!it) return;
    const spot = freeSpot(it.w, it.h);
    const room = { id: state.nextId++, cls: it.cls, label: it.label, c: spot.c, r: spot.r, cw: it.w, ch: it.h };
    curRooms().push(room);
    state.selected = room.id;
    renderTabs(); draw();
  }
  function delRoom (id) {
    const a = curRooms(); const i = a.findIndex((o) => o.id === id);
    if (i >= 0) a.splice(i, 1);
    if (state.selected === id) state.selected = null;
    renderTabs(); draw();
  }

  // ── Interacció (pointer: ratolí + tàctil) ──
  let drag = null;
  function evCell (e) {
    const rect = svg.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width * VBW;
    const y = (e.clientY - rect.top) / rect.height * VBH;
    return { c: x / CPX, r: y / CPX };
  }

  function onDown (e) {
    const delEl = e.target.closest('[data-role="del"]');
    if (delEl) { delRoom(parseInt(delEl.dataset.id, 10)); return; }
    const hEl = e.target.closest('[data-role="resize"]');
    if (hEl) {
      const id = parseInt(hEl.dataset.id, 10); const o = curRooms().find((x) => x.id === id);
      state.selected = id; drag = { mode: 'resize', id, start: evCell(e), o0: Object.assign({}, o) };
      try { svg.setPointerCapture(e.pointerId); } catch (err) {} draw(); e.preventDefault(); return;
    }
    const rEl = e.target.closest('.pl-room');
    if (rEl) {
      const id = parseInt(rEl.dataset.id, 10); const o = curRooms().find((x) => x.id === id);
      state.selected = id;
      const cell = evCell(e);
      drag = { mode: 'move', id, offC: cell.c - o.c, offR: cell.r - o.r };
      try { svg.setPointerCapture(e.pointerId); } catch (err) {} draw(); e.preventDefault(); return;
    }
    // clic en buit: deselecciona
    if (state.selected != null) { state.selected = null; draw(); }
  }

  function onMove (e) {
    if (!drag) return;
    const cell = evCell(e);
    const o = curRooms().find((x) => x.id === drag.id); if (!o) return;
    if (drag.mode === 'move') {
      const nc = Math.round(cell.c - drag.offC), nr = Math.round(cell.r - drag.offR);
      const cand = { c: nc, r: nr, cw: o.cw, ch: o.ch };
      if (inBounds(cand) && !collides(cand, o.id)) { o.c = nc; o.r = nr; draw(); }
    } else {
      const ncw = Math.max(2, Math.round(cell.c - o.c)), nch = Math.max(2, Math.round(cell.r - o.r));
      const cand = { c: o.c, r: o.r, cw: ncw, ch: nch };
      if (inBounds(cand) && !collides(cand, o.id)) { o.cw = ncw; o.ch = nch; draw(); }
    }
    e.preventDefault();
  }
  function onUp () { drag = null; }

  // ── Esdeveniments globals ──
  function onClick (e) {
    const tab = e.target.closest('.pl-tab');
    if (tab) { state.floor = parseInt(tab.dataset.floor, 10) || 0; state.selected = null; renderTabs(); draw(); return; }
    const seg = e.target.closest('.pl-seg');
    if (seg) { state.plantes = parseInt(seg.dataset.plantes, 10) || 1; ensureFloors(); state.selected = null; renderPalette(); renderTabs(); draw(); return; }
    const add = e.target.closest('.pl-chip');
    if (add) { addRoom(add.dataset.add); return; }
  }

  function init () {
    svg = document.getElementById('plSvg');
    elPalette = document.getElementById('plPalette');
    elTabs = document.getElementById('plTabs');
    if (!svg || !elPalette || !elTabs) return;
    svg.setAttribute('viewBox', `0 0 ${VBW} ${VBH}`);
    renderPalette(); renderTabs(); draw();
    document.addEventListener('click', onClick);
    svg.addEventListener('pointerdown', onDown);
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
