/* ============================================================
 * PAPIK · Configurador de plànols (eina separada del pressupost)
 * ------------------------------------------------------------
 * L'usuari tria plantes i assigna estances a cada planta (p. ex.
 * dos banys a la planta baixa). El plànol es redibuixa en viu per
 * planta amb un esquema de distribuïdor central. Esquema il·lustratiu,
 * no és un plànol d'arquitecte.
 *
 * Autocontingut a propòsit: NO toca atelier.js ni la lògica del
 * configurador de pressupost. Reutilitza el motor de dibuix (còpia
 * de les funcions pures de l'atelier) i les classes CSS planta-*.
 * ============================================================ */
(function () {
  'use strict';

  // ── Catàleg d'estances que l'usuari pot afegir ──
  const CATALOG = [
    { key: 'sala',     cls: 'sala',     label: 'Sala-menjador', weight: 3.2 },
    { key: 'cuina',    cls: 'cuina',    label: 'Cuina',         weight: 1.7 },
    { key: 'dorm',     cls: 'dorm',     label: 'Dormitori',     weight: 1.7 },
    { key: 'suite',    cls: 'dorm',     label: 'Suite',         weight: 2.4 },
    { key: 'bany',     cls: 'bany',     label: 'Bany',          weight: 0.9 },
    { key: 'lavabo',   cls: 'bany',     label: 'Lavabo',        weight: 0.6 },
    { key: 'despatx',  cls: 'despatx',  label: 'Despatx',       weight: 1.3 },
    { key: 'vestidor', cls: 'vestidor', label: 'Vestidor',      weight: 0.8 },
    { key: 'safareig', cls: 'servei',   label: 'Safareig',      weight: 0.7 },
    { key: 'rebost',   cls: 'servei',   label: 'Rebost',        weight: 0.6 },
  ];

  const state = { plantes: 2, totalM2: 150, floor: 0, floors: [] };

  function blankFloor () { const o = {}; CATALOG.forEach((c) => { o[c.key] = 0; }); return o; }

  function ensureFloors () {
    while (state.floors.length < state.plantes) state.floors.push(blankFloor());
    state.floors.length = state.plantes;
    if (state.floor > state.plantes - 1) state.floor = state.plantes - 1;
    if (state.floor < 0) state.floor = 0;
  }

  function seedDefaults () {
    ensureFloors();
    const pb = state.floors[0];
    pb.sala = 1; pb.cuina = 1; pb.lavabo = 1;
    if (state.plantes > 1) { const p1 = state.floors[1]; p1.dorm = 3; p1.bany = 1; p1.suite = 1; }
  }

  function floorCount (f) {
    const c = state.floors[f] || {};
    return CATALOG.reduce((s, cat) => s + (c[cat.key] || 0), 0);
  }

  // Llista d'estances explícita d'una planta + escala automàtica si cal.
  function roomsForFloor (f) {
    const counts = state.floors[f] || blankFloor();
    const rooms = [];
    CATALOG.forEach((c) => { for (let i = 0; i < (counts[c.key] || 0); i++) rooms.push({ label: c.label, cls: c.cls, weight: c.weight }); });
    if (state.plantes > 1) rooms.push({ label: 'Escala', cls: 'escala', weight: 0.7 });
    return rooms;
  }

  // ════════════════════════════════════════════════════════════
  // MOTOR DE DIBUIX (còpia de les funcions pures de l'atelier)
  // ════════════════════════════════════════════════════════════
  function F (n) { return Math.round(n * 10) / 10; }

  function plantaLabel (cx, cy, name, sub, w, h) {
    if (w < 34 || h < 22) return '';
    const ny = sub ? cy - 4 : cy;
    const nameT = `<text class="planta-room__name" x="${cx.toFixed(1)}" y="${ny.toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${name}</text>`;
    const subT = sub ? `<text class="planta-room__sub" x="${cx.toFixed(1)}" y="${(cy + 9).toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${sub}</text>` : '';
    return nameT + subT;
  }

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
      const bx = x + w * 0.85, by = y + d / 2, br = d * 0.16;
      [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(([dx, dy]) => {
        s += `<circle class="planta-fx" cx="${F(bx + dx * br * 1.5)}" cy="${F(by + dy * br * 1.2)}" r="${F(br)}"/>`;
      });
    } else if (cls === 'dorm') {
      const bw = Math.min(w * 0.62, 42), bh = Math.min(h * 0.72, 48);
      const bx = cx - bw / 2, by = y;
      s += `<rect class="planta-fx" x="${F(bx)}" y="${F(by)}" width="${F(bw)}" height="${F(bh)}" rx="2"/>`;
      s += `<line class="planta-fx" x1="${F(bx)}" y1="${F(by + bh * 0.26)}" x2="${F(bx + bw)}" y2="${F(by + bh * 0.26)}"/>`;
      s += `<rect class="planta-fx" x="${F(bx + bw * 0.1)}" y="${F(by + 3)}" width="${F(bw * 0.34)}" height="${F(bh * 0.15)}" rx="1"/>`;
      s += `<rect class="planta-fx" x="${F(bx + bw * 0.56)}" y="${F(by + 3)}" width="${F(bw * 0.34)}" height="${F(bh * 0.15)}" rx="1"/>`;
    } else if (cls === 'bany') {
      const tw = Math.min(w * 0.9, w), th = Math.min(h * 0.32, 14);
      s += `<rect class="planta-fx" x="${F(x)}" y="${F(y)}" width="${F(tw)}" height="${F(th)}" rx="3"/>`;
      s += `<circle class="planta-fx" cx="${F(x + tw * 0.85)}" cy="${F(y + th / 2)}" r="${F(th * 0.18)}"/>`;
      s += `<rect class="planta-fx" x="${F(x)}" y="${F(y + h - 11)}" width="13" height="9" rx="2"/>`;
      s += `<ellipse class="planta-fx" cx="${F(x + w - 7)}" cy="${F(y + h - 8)}" rx="5" ry="6"/>`;
    } else if (cls === 'escala') {
      const steps = Math.max(4, Math.round(h / 7));
      for (let i = 0; i <= steps; i++) {
        const yy = y + (h / steps) * i;
        s += `<line class="planta-fx" x1="${F(x)}" y1="${F(yy)}" x2="${F(x + w)}" y2="${F(yy)}"/>`;
      }
      s += `<line class="planta-fx" x1="${F(cx)}" y1="${F(y)}" x2="${F(cx)}" y2="${F(y + h)}"/>`;
    } else if (cls === 'vestidor') {
      s += `<rect class="planta-fx" x="${F(x)}" y="${F(y)}" width="${F(w)}" height="${F(Math.min(h * 0.2, 9))}"/>`;
    } else if (cls === 'despatx') {
      const dw = Math.min(w * 0.6, 34), dh = Math.min(h * 0.3, 16);
      s += `<rect class="planta-fx" x="${F(cx - dw / 2)}" y="${F(y + h - dh)}" width="${F(dw)}" height="${F(dh)}" rx="1"/>`;
    }
    return s;
  }

  function doorOnEdge (ex, ey, vertical, length, intoPositive) {
    const dw = Math.min(Math.max(length * 0.45, 8), 16);
    let s = '';
    if (vertical) {
      const my = ey + (length - dw) / 2, dir = intoPositive ? 1 : -1;
      s += `<line class="planta-door-cut" x1="${F(ex)}" y1="${F(my)}" x2="${F(ex)}" y2="${F(my + dw)}"/>`;
      s += `<line class="planta-door" x1="${F(ex)}" y1="${F(my)}" x2="${F(ex + dir * dw)}" y2="${F(my)}"/>`;
      s += `<path class="planta-door" d="M ${F(ex + dir * dw)} ${F(my)} A ${F(dw)} ${F(dw)} 0 0 ${dir > 0 ? 1 : 0} ${F(ex)} ${F(my + dw)}"/>`;
    } else {
      const mx = ex + (length - dw) / 2, dir = intoPositive ? 1 : -1;
      s += `<line class="planta-door-cut" x1="${F(mx)}" y1="${F(ey)}" x2="${F(mx + dw)}" y2="${F(ey)}"/>`;
      s += `<line class="planta-door" x1="${F(mx)}" y1="${F(ey)}" x2="${F(mx)}" y2="${F(ey + dir * dw)}"/>`;
      s += `<path class="planta-door" d="M ${F(mx)} ${F(ey + dir * dw)} A ${F(dw)} ${F(dw)} 0 0 ${dir > 0 ? 0 : 1} ${F(mx + dw)} ${F(ey)}"/>`;
    }
    return s;
  }

  function windowBand (bx, by, len, t, vertical) {
    const ww = Math.min(len * 0.5, 22);
    if (ww < 6) return '';
    if (vertical) {
      const my = by + (len - ww) / 2;
      return `<rect class="planta-win-gap" x="${F(bx)}" y="${F(my)}" width="${F(t)}" height="${F(ww)}"/>` +
             `<line class="planta-window" x1="${F(bx + t / 2)}" y1="${F(my)}" x2="${F(bx + t / 2)}" y2="${F(my + ww)}"/>`;
    }
    const mx = bx + (len - ww) / 2;
    return `<rect class="planta-win-gap" x="${F(mx)}" y="${F(by)}" width="${F(ww)}" height="${F(t)}"/>` +
           `<line class="planta-window" x1="${F(mx)}" y1="${F(by + t / 2)}" x2="${F(mx + ww)}" y2="${F(by + t / 2)}"/>`;
  }

  function dimLine (x, y, len, vertical, label) {
    let s = '';
    if (vertical) {
      s += `<line class="planta-dimline" x1="${F(x)}" y1="${F(y)}" x2="${F(x)}" y2="${F(y + len)}"/>`;
      s += `<line class="planta-dimline" x1="${F(x - 3)}" y1="${F(y)}" x2="${F(x + 3)}" y2="${F(y)}"/>`;
      s += `<line class="planta-dimline" x1="${F(x - 3)}" y1="${F(y + len)}" x2="${F(x + 3)}" y2="${F(y + len)}"/>`;
      s += `<text class="planta-dim" x="${F(x - 5)}" y="${F(y + len / 2)}" text-anchor="middle" transform="rotate(-90 ${F(x - 5)} ${F(y + len / 2)})">${label}</text>`;
    } else {
      s += `<line class="planta-dimline" x1="${F(x)}" y1="${F(y)}" x2="${F(x + len)}" y2="${F(y)}"/>`;
      s += `<line class="planta-dimline" x1="${F(x)}" y1="${F(y - 3)}" x2="${F(x)}" y2="${F(y + 3)}"/>`;
      s += `<line class="planta-dimline" x1="${F(x + len)}" y1="${F(y - 3)}" x2="${F(x + len)}" y2="${F(y + 3)}"/>`;
      s += `<text class="planta-dim" x="${F(x + len / 2)}" y="${F(y + 11)}" text-anchor="middle">${label}</text>`;
    }
    return s;
  }

  function layoutPlanta (roomsIn, X0, Y0, X1, Y1, scale) {
    const W = X1 - X0, H = Y1 - Y0;
    const rooms = roomsIn.map((r) => Object.assign({}, r));
    const out = { rooms: [], corridor: null };

    if (rooms.length === 1) {
      const r = rooms[0];
      r.x = X0; r.y = Y0; r.w = W; r.h = H;
      r.exposed = { t: 1, b: 1, l: 1, r: 1 }; r.door = null;
      out.rooms.push(r); return out;
    }
    if (rooms.length === 2) {
      const tot = (rooms[0].weight + rooms[1].weight) || 1;
      const w0 = W * rooms[0].weight / tot;
      rooms[0].x = X0;      rooms[0].y = Y0; rooms[0].w = w0;     rooms[0].h = H;
      rooms[1].x = X0 + w0; rooms[1].y = Y0; rooms[1].w = W - w0; rooms[1].h = H;
      rooms[0].door = { edge: 'R' }; rooms[1].door = null;
      rooms[0].exposed = { t: 1, b: 1, l: 1, r: 0 };
      rooms[1].exposed = { t: 1, b: 1, l: 0, r: 1 };
      out.rooms.push(rooms[0], rooms[1]); return out;
    }

    let usableX1 = X1, stair = null;
    const stIdx = rooms.findIndex((r) => r.cls === 'escala');
    if (stIdx >= 0) {
      const stW = Math.min(Math.max(scale * 2.4, 26), W * 0.26);
      stair = rooms.splice(stIdx, 1)[0];
      usableX1 = X1 - stW;
      stair.x = usableX1; stair.y = Y0; stair.w = stW; stair.h = H;
      stair.exposed = { t: 0, b: 0, l: 0, r: 1 };
    }
    const Wu = usableX1 - X0;
    const corridorH = Math.min(Math.max(scale * 1.25, 13), H * 0.22);

    const sorted = rooms.slice().sort((a, b) => b.weight - a.weight);
    const top = [], bot = []; let wt = 0, wb = 0;
    sorted.forEach((r) => { if (wt <= wb) { top.push(r); wt += r.weight; } else { bot.push(r); wb += r.weight; } });

    const zoneH = H - corridorH;
    let topH = zoneH * (wt / (wt + wb || 1));
    topH = Math.max(zoneH * 0.38, Math.min(zoneH * 0.62, topH));
    const corrY = Y0 + topH;

    function placeRow (list, y, h, edge) {
      const tw = list.reduce((s, r) => s + r.weight, 0) || 1;
      let x = X0;
      list.forEach((r, i) => {
        const last = i === list.length - 1;
        const w = last ? (usableX1 - x) : Wu * (r.weight / tw);
        r.x = x; r.y = y; r.w = w; r.h = h;
        r.door = { edge };
        r.exposed = {
          t: edge === 'B' ? 1 : 0,
          b: edge === 'T' ? 1 : 0,
          l: i === 0 ? 1 : 0,
          r: (last && !stair) ? 1 : 0,
        };
        x += w;
        out.rooms.push(r);
      });
    }
    placeRow(top, Y0, topH, 'B');
    placeRow(bot, corrY + corridorH, zoneH - topH, 'T');

    if (stair) {
      stair.door = { edge: 'L', atY: corrY, len: corridorH };
      out.rooms.push(stair);
    }
    out.corridor = { x: X0, y: corrY, w: Wu, h: corridorH };
    return out;
  }

  // Construeix l'SVG d'una planta a partir d'una llista explícita d'estances.
  function buildPlan (rooms, footM2, isGround) {
    const VW = 440, VH = 340, pad = 42;
    if (!rooms.length || !footM2) return '';
    const wM = Math.sqrt(footM2 * 4 / 3), hM = footM2 / wM;
    const scale = Math.min((VW - 2 * pad) / wM, (VH - 2 * pad) / hM);
    const ox = pad + ((VW - 2 * pad) - wM * scale) / 2;
    const oy = pad + ((VH - 2 * pad) - hM * scale) / 2;
    const hx = ox, hy = oy, hw = wM * scale, hh = hM * scale;
    const wallT = Math.max(3, Math.min(6, hw * 0.022));

    let walls = '', fx = '', doors = '', wins = '', labels = '';
    walls += `<rect class="planta-wall-fill" x="${F(hx)}" y="${F(hy)}" width="${F(hw)}" height="${F(hh)}"/>`;
    walls += `<rect class="planta-room-fill" x="${F(hx + wallT)}" y="${F(hy + wallT)}" width="${F(hw - 2 * wallT)}" height="${F(hh - 2 * wallT)}"/>`;

    const inX0 = hx + wallT, inY0 = hy + wallT, inX1 = hx + hw - wallT, inY1 = hy + hh - wallT;
    const layout = layoutPlanta(rooms, inX0, inY0, inX1, inY1, scale);

    layout.rooms.forEach((r) => {
      walls += `<rect class="planta-partition" x="${F(r.x)}" y="${F(r.y)}" width="${F(r.w)}" height="${F(r.h)}"/>`;
      fx += furnish(r.cls, r);
      labels += plantaLabel(r.x + r.w / 2, r.y + 9, r.label, '', r.w, r.h);
      if (r.door) {
        const d = r.door;
        if (d.edge === 'B')      doors += doorOnEdge(r.x, r.y + r.h, false, r.w, false);
        else if (d.edge === 'T') doors += doorOnEdge(r.x, r.y, false, r.w, true);
        else if (d.edge === 'R') doors += doorOnEdge(r.x + r.w, r.y, true, r.h, false);
        else if (d.edge === 'L') doors += doorOnEdge(r.x, d.atY != null ? d.atY : r.y, true, d.len != null ? d.len : r.h, true);
      }
      const ex = r.exposed || {};
      if (ex.t) wins += windowBand(r.x, hy, r.w, wallT, false);
      if (ex.b) wins += windowBand(r.x, hy + hh - wallT, r.w, wallT, false);
      if (ex.l) wins += windowBand(hx, r.y, r.h, wallT, true);
      if (ex.r) wins += windowBand(hx + hw - wallT, r.y, r.h, wallT, true);
    });

    if (isGround && layout.corridor) {
      doors += doorOnEdge(hx + wallT, layout.corridor.y, true, layout.corridor.h, true);
    }

    const dims = dimLine(hx, hy + hh + 16, hw, false, F(wM) + ' m') +
                 dimLine(hx - 16, hy, hh, true, F(hM) + ' m');
    labels += `<text class="planta-area" x="${F(hx + hw / 2)}" y="${F(hy + hh + 32)}" text-anchor="middle">${Math.round(footM2)} m² · planta</text>`;

    return `<svg viewBox="0 0 ${VW} ${VH}" class="planta-svg" role="img" aria-label="Plànol esquemàtic de la planta">` +
           walls + wins + doors + fx + dims + labels + `</svg>`;
  }

  // ════════════════════════════════════════════════════════════
  // UI
  // ════════════════════════════════════════════════════════════
  let elTabs, elPlan, elControls, elTotals;

  function floorLabel (f) { return f === 0 ? 'Planta baixa' : ('Planta ' + f); }

  function renderTabs () {
    let h = '';
    for (let f = 0; f < state.plantes; f++) {
      h += `<button type="button" class="pl-tab${f === state.floor ? ' is-active' : ''}" data-floor="${f}">${floorLabel(f)} <span class="pl-tab__n">${floorCount(f)}</span></button>`;
    }
    elTabs.innerHTML = h;
  }

  function renderControls () {
    const counts = state.floors[state.floor] || blankFloor();
    let rows = CATALOG.map((c) => {
      const n = counts[c.key] || 0;
      return `<div class="pl-room${n > 0 ? ' is-on' : ''}">
        <span class="pl-room__label">${c.label}</span>
        <span class="pl-stepper">
          <button type="button" class="pl-step" data-act="dec" data-key="${c.key}" aria-label="Treure ${c.label}">−</button>
          <span class="pl-step__n" data-count="${c.key}">${n}</span>
          <button type="button" class="pl-step" data-act="inc" data-key="${c.key}" aria-label="Afegir ${c.label}">+</button>
        </span>
      </div>`;
    }).join('');

    let plantesBtns = '';
    [1, 2, 3].forEach((p) => {
      plantesBtns += `<button type="button" class="pl-seg${state.plantes === p ? ' is-active' : ''}" data-plantes="${p}">${p === 1 ? '1 planta' : p + ' plantes'}</button>`;
    });

    elControls.innerHTML = `
      <div class="pl-field">
        <label class="pl-field__label">Plantes</label>
        <div class="pl-seg-group" id="plPlantes">${plantesBtns}</div>
      </div>
      <div class="pl-field">
        <label class="pl-field__label" for="plM2">Superfície total construïda</label>
        <div class="pl-m2"><input id="plM2" type="number" min="40" max="2000" step="10" value="${state.totalM2}" inputmode="numeric"> <span>m²</span></div>
        <p class="pl-field__hint">Es reparteix entre les ${state.plantes === 1 ? 'planta' : state.plantes + ' plantes'} (${Math.round(state.totalM2 / state.plantes)} m² per planta).</p>
      </div>
      <div class="pl-field">
        <label class="pl-field__label">Estances a <b>${floorLabel(state.floor)}</b></label>
        <div class="pl-rooms" id="plRooms">${rows}</div>
      </div>`;
  }

  function renderPlan () {
    const footM2 = Math.max(20, (parseFloat(state.totalM2) || 120) / state.plantes);
    const rooms = roomsForFloor(state.floor);
    const realRooms = rooms.filter((r) => r.cls !== 'escala');
    if (!realRooms.length) {
      elPlan.innerHTML = `<div class="planta-empty">Afegeix estances a <b>${floorLabel(state.floor)}</b> i el plànol es dibuixarà aquí.</div>`;
      return;
    }
    elPlan.innerHTML = buildPlan(rooms, footM2, state.floor === 0);
    if (window.gsap) {
      window.gsap.from(elPlan.querySelectorAll('.planta-partition, .planta-wall-fill'), { opacity: 0, duration: 0.35, stagger: 0.02, ease: 'power2.out' });
      window.gsap.from(elPlan.querySelectorAll('.planta-fx, text, .planta-door, .planta-window'), { opacity: 0, duration: 0.3, delay: 0.12 });
    }
  }

  function render () { ensureFloors(); renderTabs(); renderControls(); renderPlan(); }

  function onClick (e) {
    const tab = e.target.closest('.pl-tab');
    if (tab) { state.floor = parseInt(tab.dataset.floor, 10) || 0; render(); return; }
    const seg = e.target.closest('.pl-seg');
    if (seg) { state.plantes = parseInt(seg.dataset.plantes, 10) || 1; ensureFloors(); render(); return; }
    const step = e.target.closest('.pl-step');
    if (step) {
      const key = step.dataset.key, act = step.dataset.act;
      const f = state.floors[state.floor];
      const prev = f[key] || 0;
      f[key] = Math.max(0, Math.min(8, prev + (act === 'inc' ? 1 : -1)));
      if (f[key] === prev) return;
      // Actualització parcial: només el comptador, l'estat visual i el plànol.
      const nEl = elControls.querySelector(`.pl-step__n[data-count="${key}"]`);
      if (nEl) {
        nEl.textContent = f[key];
        const roomEl = nEl.closest('.pl-room');
        if (roomEl) roomEl.classList.toggle('is-on', f[key] > 0);
      }
      renderTabs();
      renderPlan();
      return;
    }
  }

  function onInput (e) {
    if (e.target && e.target.id === 'plM2') {
      const v = parseFloat(e.target.value);
      if (!isNaN(v)) { state.totalM2 = Math.max(40, Math.min(2000, v)); renderPlan(); updateHint(); }
    }
  }

  function updateHint () {
    const hint = document.querySelector('.pl-field__hint');
    if (hint) hint.textContent = `Es reparteix entre les ${state.plantes === 1 ? 'planta' : state.plantes + ' plantes'} (${Math.round(state.totalM2 / state.plantes)} m² per planta).`;
  }

  function init () {
    elTabs = document.getElementById('plTabs');
    elPlan = document.getElementById('plPlan');
    elControls = document.getElementById('plControls');
    if (!elTabs || !elPlan || !elControls) return;
    seedDefaults();
    document.addEventListener('click', onClick);
    document.addEventListener('input', onInput);
    render();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
