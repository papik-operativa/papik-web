/* ═══════════════════════════════════════════════════════════
   PAPIK · Configurador de Pressupost
   Lògica del configurador (4 passos · overlay · càlcul via API)
   API: POST /api/calcular
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  const STORAGE_KEY = 'papik_conf_state_v1';
  const TOTAL_SECTIONS = 4;

  const SECTION_TITLES = {
    1: 'ESTRUCTURA I DIMENSIONS',
    2: 'MATERIALS I ACABATS',
    3: 'EQUIPAMENT I EXTRES',
    4: 'UBICACIÓ I CONTACTE',
  };

  // ── DOM helpers ────────────────────────────────────────────
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const fmtEur = (n) => new Intl.NumberFormat('ca-ES', {
    style: 'currency', currency: 'EUR', maximumFractionDigits: 0,
  }).format(Math.round(n || 0));
  const fmtNum = (n) => new Intl.NumberFormat('ca-ES', {
    maximumFractionDigits: 0,
  }).format(Math.round(n || 0));

  // ── Estat ─────────────────────────────────────────────────
  const state = {
    activeSection: null,           // secció oberta a l'overlay (null = cap)
    completed: { 1: false, 2: false, 3: false, 4: false },
    result: null,                  // resposta de l'API
  };

  function saveState() {
    try {
      // Guardem només l'estat de progress, no els valors (els valors viuen al DOM)
      const snapshot = {
        completed: state.completed,
        formValues: collectAllFormValues(),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
    } catch (e) { /* quota o privat */ }
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const snap = JSON.parse(raw);
      if (snap.completed) state.completed = snap.completed;
      if (snap.formValues) restoreFormValues(snap.formValues);
    } catch (e) { /* corrupte → ignorem */ }
  }

  function collectAllFormValues() {
    const values = {};
    // Inputs amb id
    ['f_m2', 'f_m2_garatge', 'f_m2_porxos', 'f_ubicacio', 'f_nom', 'f_email', 'f_tel'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) values[id] = el.value;
    });
    // Radios checked
    ['plantes', 'banys', 'garatge', 'escala', 'coberta', 'façana', 'paviment', 'nivell_bany',
     'solar', 'persianes', 'fancoils', 'llarfoc', 'rado', 'domotica'].forEach((name) => {
      const checked = document.querySelector(`input[name="${name}"]:checked`);
      if (checked) values[`r_${name}`] = checked.value;
    });
    return values;
  }

  function restoreFormValues(values) {
    Object.keys(values).forEach((key) => {
      if (key.startsWith('r_')) {
        const name = key.slice(2);
        const radio = document.querySelector(`input[name="${name}"][value="${values[key]}"]`);
        if (radio) {
          radio.checked = true;
          markRadioSelected(radio);
        }
      } else {
        const el = document.getElementById(key);
        if (el) el.value = values[key];
      }
    });
  }

  // ── Cards: estats card-locked / card-unlocked / card-done ──
  function getSection(n) {
    return document.querySelector(`.conf-section[data-section="${n}"]`);
  }

  function setCardState(n, status) {
    const section = getSection(n);
    if (!section) return;
    section.classList.remove('card-locked', 'card-unlocked', 'card-done');
    section.classList.add(`card-${status}`);
    const cta = section.querySelector('.card-body-preview__cta');
    if (cta) {
      if (status === 'locked') cta.textContent = 'Bloquejat';
      else if (status === 'done') cta.textContent = 'Editar';
      else cta.textContent = n === 1 && !state.completed[1] ? 'Comença' : 'Continuar';
    }
  }

  function refreshCards() {
    // Section 1 sempre desbloquejada
    setCardState(1, state.completed[1] ? 'done' : 'unlocked');
    // Section 2 desbloquejada si 1 done
    setCardState(2, state.completed[2] ? 'done' : (state.completed[1] ? 'unlocked' : 'locked'));
    // Section 3 desbloquejada si 2 done
    setCardState(3, state.completed[3] ? 'done' : (state.completed[2] ? 'unlocked' : 'locked'));
    // Section 4 visible només si 3 done
    const sec4 = getSection(4);
    if (sec4) {
      if (state.completed[3]) {
        sec4.style.display = '';
        sec4.classList.add('panel-active'); // necessari pel fade-in CSS
        setCardState(4, state.completed[4] ? 'done' : 'unlocked');
      } else {
        sec4.style.display = 'none';
        sec4.classList.remove('panel-active');
      }
    }
    updateProgress();
  }

  function updateProgress() {
    const done = Object.values(state.completed).filter(Boolean).length;
    const pct = Math.round((done / TOTAL_SECTIONS) * 100);
    const fill = document.getElementById('progressFill');
    const txt = document.getElementById('progressPercent');
    const wrap = document.getElementById('confProgress');
    if (fill) fill.style.width = pct + '%';
    if (txt) txt.textContent = pct + '%';
    if (wrap) wrap.style.display = done > 0 && !state.result ? 'flex' : 'none';
  }

  // ── Conditionals (mostrem/amaguem camps segons valors) ─────
  function applyConditionals() {
    // m2 garatge → si garatge=si
    const garatge = document.querySelector('input[name="garatge"]:checked');
    const fieldGaratge = document.getElementById('field_m2_garatge');
    if (fieldGaratge) {
      const show = garatge && garatge.value === 'si';
      fieldGaratge.classList.toggle('hidden-field', !show);
    }
    // Escala → si plantes != 1
    const plantes = document.querySelector('input[name="plantes"]:checked');
    const fieldEscala = document.getElementById('field_escala');
    if (fieldEscala) {
      const show = plantes && plantes.value !== '1';
      fieldEscala.classList.toggle('hidden-field', !show);
    }
  }

  // ── Visual selecció radios ─────────────────────────────────
  function markRadioSelected(radio) {
    const name = radio.name;
    document.querySelectorAll(`input[name="${name}"]`).forEach((r) => {
      const opt = r.closest('.conf-option');
      if (opt) opt.classList.toggle('selected', r.checked);
    });
  }

  function refreshAllRadioSelections() {
    document.querySelectorAll('input[type="radio"]:checked').forEach(markRadioSelected);
  }

  // ── Overlay open / close ───────────────────────────────────
  function openOverlay(n) {
    if (state.activeSection === n) return;

    // Si hi ha overlay obert, tanquem primer (sense marcar com a complet)
    if (state.activeSection !== null) {
      moveBodyBackToCard(state.activeSection);
    }

    const section = getSection(n);
    if (!section) return;
    if (section.classList.contains('card-locked')) return;

    const body = section.querySelector('.panel-body');
    const overlayForm = document.getElementById('overlayForm');
    if (!body || !overlayForm) return;

    // Moure els fills de panel-body cap a overlay
    while (body.firstChild) overlayForm.appendChild(body.firstChild);

    // Header
    const titleSpan = document.querySelector('#overlayTitle span:last-child');
    const numSpan = document.querySelector('#overlayTitle .panel-header__num');
    if (numSpan) numSpan.textContent = n;
    if (titleSpan) titleSpan.textContent = SECTION_TITLES[n];
    const stepLabel = document.getElementById('overlayStepLabel');
    if (stepLabel) stepLabel.textContent = `Pas ${n} de ${TOTAL_SECTIONS}`;

    state.activeSection = n;
    document.getElementById('confOverlay').classList.add('active');
    document.body.style.overflow = 'hidden';

    applyConditionals();
    refreshAllRadioSelections();

    // Focus al primer input visible
    setTimeout(() => {
      const first = overlayForm.querySelector('input:not([type=radio]):not([type=hidden]), select');
      if (first && !first.closest('.hidden-field')) first.focus();
    }, 200);
  }

  function moveBodyBackToCard(n) {
    const section = getSection(n);
    const body = section?.querySelector('.panel-body');
    const overlayForm = document.getElementById('overlayForm');
    if (!body || !overlayForm) return;
    while (overlayForm.firstChild) body.appendChild(overlayForm.firstChild);
  }

  function closeOverlay() {
    if (state.activeSection === null) return;
    moveBodyBackToCard(state.activeSection);
    state.activeSection = null;
    document.getElementById('confOverlay').classList.remove('active');
    document.body.style.overflow = '';
  }

  // ── Validació per secció ───────────────────────────────────
  function getRadio(name) {
    const r = document.querySelector(`input[name="${name}"]:checked`);
    return r ? r.value : null;
  }

  function validateSection(n) {
    if (n === 1) {
      const m2 = parseFloat(document.getElementById('f_m2').value);
      if (!m2 || m2 < 80) return { field: 'f_m2', msg: 'Indica una superfície mínima de 80 m²' };
      if (!getRadio('plantes')) return { field: null, msg: 'Selecciona el nombre de plantes' };
      if (!getRadio('banys')) return { field: null, msg: 'Selecciona el nombre de banys' };
      const garatge = getRadio('garatge');
      if (!garatge) return { field: null, msg: 'Indica si vol garatge' };
      if (garatge === 'si') {
        const mg = parseFloat(document.getElementById('f_m2_garatge').value);
        if (!mg || mg < 1) return { field: 'f_m2_garatge', msg: 'Indica la superfície del garatge' };
      }
      if (getRadio('plantes') !== '1' && !getRadio('escala')) {
        return { field: null, msg: "Selecciona el tipus d'escala" };
      }
    }
    if (n === 2) {
      if (!getRadio('coberta')) return { msg: 'Selecciona el tipus de coberta' };
      if (!getRadio('façana')) return { msg: 'Selecciona el tipus de façana' };
      if (!getRadio('paviment')) return { msg: 'Selecciona el paviment interior' };
      if (!getRadio('nivell_bany')) return { msg: 'Selecciona el nivell dels banys' };
    }
    if (n === 3) {
      const required = ['solar', 'persianes', 'fancoils', 'llarfoc', 'rado'];
      for (const k of required) if (!getRadio(k)) return { msg: 'Respon totes les preguntes d\'aquesta secció' };
      // domotica és opcional → la donem per "no" si no es respon
      if (!getRadio('domotica')) {
        // marcar per defecte
        const d = document.querySelector('input[name="domotica"][value="no"]');
        if (d) { d.checked = true; markRadioSelected(d); }
      }
    }
    if (n === 4) {
      const ubic = document.getElementById('f_ubicacio').value;
      if (!ubic) return { field: 'f_ubicacio', msg: 'Selecciona la ubicació de l\'obra' };
      const nom = document.getElementById('f_nom').value.trim();
      if (!nom) return { field: 'f_nom', msg: 'Introdueix el teu nom' };
      const email = document.getElementById('f_email').value.trim();
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return { field: 'f_email', msg: 'Introdueix un correu electrònic vàlid' };
      }
    }
    return null;
  }

  // ── Toast notification ─────────────────────────────────────
  function showToast(msg) {
    const old = document.querySelector('.conf-toast');
    if (old) old.remove();
    const t = document.createElement('div');
    t.className = 'conf-toast';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => {
      t.classList.add('hiding');
      setTimeout(() => t.remove(), 350);
    }, 2800);
  }

  // ── Navegació entre passos ─────────────────────────────────
  function handleNext() {
    const n = state.activeSection;
    if (n === null) return;
    const err = validateSection(n);
    if (err) {
      showToast(err.msg);
      if (err.field) {
        const el = document.getElementById(err.field);
        if (el) { el.focus(); el.classList.add('conf-input--error'); setTimeout(() => el.classList.remove('conf-input--error'), 2000); }
      }
      return;
    }
    state.completed[n] = true;
    saveState();
    moveBodyBackToCard(n);
    state.activeSection = null;
    refreshCards();

    if (n < TOTAL_SECTIONS) {
      // Obrir següent automàticament
      setTimeout(() => openOverlay(n + 1), 250);
    } else {
      // Final → tancar overlay i calcular
      document.getElementById('confOverlay').classList.remove('active');
      document.body.style.overflow = '';
      handleCalc();
    }
  }

  function handleBack() {
    const n = state.activeSection;
    if (n === null || n === 1) {
      closeOverlay();
      return;
    }
    moveBodyBackToCard(n);
    state.activeSection = null;
    setTimeout(() => openOverlay(n - 1), 200);
  }

  // ── Càlcul (crida al servidor) ─────────────────────────────
  function buildPayload() {
    const ubicacioSelect = document.getElementById('f_ubicacio');
    let municipi = '';
    if (ubicacioSelect && ubicacioSelect.selectedIndex >= 0) {
      const txt = ubicacioSelect.options[ubicacioSelect.selectedIndex].text || '';
      municipi = txt.replace(/\s*\([^)]*\)\s*$/, '').trim();
    }
    return {
      m2: parseFloat(document.getElementById('f_m2').value || 0),
      plantes: getRadio('plantes') || '2',
      num_banys: parseInt(getRadio('banys') || '2', 10),
      garatge: getRadio('garatge') || 'no',
      m2_garatge: parseFloat(document.getElementById('f_m2_garatge').value || 0),
      m2_porxos: parseFloat(document.getElementById('f_m2_porxos').value || 0),
      tipus_escala: getRadio('escala') || 'no',
      tipus_coberta: getRadio('coberta') || 'teula',
      tipus_facana: getRadio('façana') || 'sate',
      tipus_paviment: getRadio('paviment') || 'ceramic',
      nivell_bany: getRadio('nivell_bany') || 'alt',
      plaques_solars: getRadio('solar') || 'no',
      persianes: getRadio('persianes') || 'no',
      fan_coils: getRadio('fancoils') || 'no',
      llar_foc: getRadio('llarfoc') || 'no',
      membrana_rado: getRadio('rado') || 'no',
      domotica: getRadio('domotica') || 'no',
      municipi: municipi,
      nom: document.getElementById('f_nom').value.trim(),
      email: document.getElementById('f_email').value.trim(),
      telefon: document.getElementById('f_tel').value.trim(),
    };
  }

  async function handleCalc() {
    const calcBtn = document.getElementById('btnCalc');
    if (calcBtn) { calcBtn.disabled = true; calcBtn.textContent = 'Calculant…'; }

    const payload = buildPayload();
    try {
      const res = await fetch('/api/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const result = await res.json();
      state.result = result;
      renderResult(result, payload);
    } catch (err) {
      console.error('Calc error:', err);
      showToast('No s\'ha pogut calcular. Torna a provar en uns moments.');
      if (calcBtn) { calcBtn.disabled = false; calcBtn.textContent = 'Calcular pressupost'; }
    }
  }

  // ── Render del resum de la configuració ───────────────────
  function renderSummary(payload, result) {
    const summary = document.getElementById('confSummary');
    if (!summary) return;
    summary.innerHTML = '';

    const v = result.variables_derivades || {};

    // Etiquetes humanes per a cada valor
    const labelize = (key, val) => {
      const map = {
        plantes: { '1': '1 planta', '2': '2 plantes', '3': 'Més de 2 plantes' },
        garatge: { si: 'Sí', no: 'No' },
        tipus_escala: { fusta: 'Escala fusta', metallica: 'Escala metàl·lica', no: 'Sense escala' },
        plaques_solars: { si: 'Sí', no: 'No' },
        persianes: { si: 'Sí', no: 'No' },
        fan_coils: { si: 'Sí', no: 'No' },
        llar_foc: { si: 'Sí', no: 'No' },
        membrana_rado: { si: 'Sí', no: 'No' },
        domotica: { si: 'Sí', no: 'No' },
      };
      return map[key]?.[val] || val || '—';
    };

    const items = [
      { label: 'Superfície', value: `${fmtNum(payload.m2)} m²` },
      { label: 'Plantes', value: labelize('plantes', payload.plantes) },
      { label: 'Banys', value: `${payload.num_banys} banys` },
      { label: 'Garatge', value: payload.garatge === 'si' ? `Sí (${fmtNum(payload.m2_garatge)} m²)` : 'No' },
    ];
    if (payload.m2_porxos > 0) {
      items.push({ label: 'Pòrxos / terrasses', value: `${fmtNum(payload.m2_porxos)} m²` });
    }
    if (payload.plantes !== '1' && payload.tipus_escala && payload.tipus_escala !== 'no') {
      items.push({ label: 'Escala', value: labelize('tipus_escala', payload.tipus_escala) });
    }
    items.push(
      { label: 'Coberta', value: v.coberta_label || payload.tipus_coberta },
      { label: 'Façana', value: v.facana_label || payload.tipus_facana },
      { label: 'Paviment', value: v.paviment_label || payload.tipus_paviment },
      { label: 'Banys (qualitat)', value: v.bany_label || payload.nivell_bany },
    );
    // Equipament (només els que valen "sí")
    const equip = [];
    if (payload.plaques_solars === 'si') equip.push('Plaques solars');
    if (payload.persianes === 'si') equip.push('Persianes motoritzades');
    if (payload.fan_coils === 'si') equip.push('Fan coils');
    if (payload.llar_foc === 'si') equip.push('Llar de foc');
    if (payload.membrana_rado === 'si') equip.push('Membrana radó');
    if (payload.domotica === 'si') equip.push('Domòtica Loxone');
    items.push({ label: 'Equipament', value: equip.length ? equip.join(' · ') : 'Bàsic' });

    items.push({ label: 'Ubicació', value: `${v.municipi || '—'} (${v.km_transport || 0} km)` });

    items.forEach((it) => {
      const div = document.createElement('div');
      div.className = 'conf-summary__item';
      div.innerHTML = `<span class="conf-summary__label">${it.label}</span><span class="conf-summary__value">${it.value}</span>`;
      summary.appendChild(div);
    });
  }

  // ── Render del resultat ────────────────────────────────────
  function renderResult(result, payload) {
    const m2 = result.variables_derivades?.m2 || payload.m2 || 1;
    const total = result.total_pressupost || 0;
    const perM2 = total / m2;

    document.getElementById('resultTotal').textContent = fmtEur(total);
    document.getElementById('resultPerM2').textContent = `≈ ${fmtEur(perM2)}/m² · ${fmtNum(m2)} m² construïts`;

    renderSummary(payload, result);

    const breakdown = document.getElementById('confBreakdown');
    breakdown.innerHTML = '';

    const packs = [
      { title: 'Envolvent tèrmic', data: result.pack_envolvent, lines: [
        ['Estructura vertical', 'estructura_vertical'],
        ['Coberta i forjats', 'coberta_forjats'],
        ['Finestres', 'finestres'],
        ['Façana (suplement)', 'increment_facana'],
        ['Porta d\'entrada', 'porta_entrada'],
        ['Grua i mitjans', 'grua'],
      ]},
      { title: 'Instal·lacions', data: result.pack_installacions, lines: [
        ['Telecomunicacions', 'telecomunicacions'],
        ['Sanejament', 'sanejament_interior'],
        ['Electricitat', 'electricitat_interior'],
        ['Aigua', 'agua_interior'],
        ['Escomeses', 'escomeses'],
        ['Pre-instal·lació ventilació', 'preinstallacio_ventilacio'],
        ['Recuperador Zehnder', 'zehnder'],
        ['Aerotèrmia', 'aerotermia'],
        ['Fan coils', 'fan_coils'],
        ['Llar de foc', 'llar_foc'],
        ['Plaques solars', 'solar'],
        ['Persianes motoritzades', 'persianes'],
        ['Membrana anti-radó', 'membrana_rado'],
        ['Domòtica Loxone', 'domotica'],
      ]},
      { title: 'Parking i exteriors', data: result.pack_parking, lines: [
        ['Porta peatonal', 'porta_peatonal'],
        ['Porta motoritzada', 'porta_motoritzada'],
        ['Estructura garatge', 'garatge_estructura'],
        ['Pòrxos i terrasses', 'porxos_terrasses'],
      ]},
      { title: 'Acabats interiors', data: result.pack_acabats, lines: [
        ['Pintura', 'pintura'],
        ['Pladur', 'pladur'],
        ['Cuina', 'cuina'],
        ['Paviments', 'paviments'],
        ['Portes interiors', 'portes_interiors'],
        ['Estructura Krona', 'estructura_krona'],
        ['Banys', 'banys'],
        ['Escala', 'escala'],
      ]},
    ];

    packs.forEach((pack) => {
      if (!pack.data) return;
      const wrap = document.createElement('div');
      wrap.className = 'conf-pack';
      const title = document.createElement('div');
      title.className = 'conf-pack__title';
      title.textContent = pack.title;
      wrap.appendChild(title);
      pack.lines.forEach(([label, key]) => {
        const value = pack.data[key];
        if (!value || value === 0) return;
        const row = document.createElement('div');
        row.className = 'conf-line';
        row.innerHTML = `<span class="conf-line__label">${label}</span><span class="conf-line__value">${fmtEur(value)}</span>`;
        wrap.appendChild(row);
      });
      const subtotal = document.createElement('div');
      subtotal.className = 'conf-line';
      subtotal.style.cssText = 'border-top:1px solid rgba(86,104,94,0.18);margin-top:6px;padding-top:14px;font-weight:500;';
      subtotal.innerHTML = `<span class="conf-line__label">Subtotal ${pack.title.toLowerCase()}</span><span class="conf-line__value">${fmtEur(pack.data.total)}</span>`;
      wrap.appendChild(subtotal);
      breakdown.appendChild(wrap);
    });

    // Transport + contractació externa + IVA
    const extra = document.createElement('div');
    extra.className = 'conf-pack';
    extra.innerHTML = `
      <div class="conf-pack__title">Altres conceptes</div>
      <div class="conf-line"><span class="conf-line__label">Transport (${result.variables_derivades?.km_transport || 0} km)</span><span class="conf-line__value">${fmtEur(result.transport)}</span></div>
      <div class="conf-line"><span class="conf-line__label">Projecte arquitectònic</span><span class="conf-line__value">${fmtEur(result.contractacio_externa?.projecte_arquitectonic)}</span></div>
      <div class="conf-line"><span class="conf-line__label">Seguretat i salut</span><span class="conf-line__value">${fmtEur(result.contractacio_externa?.seguretat_salut)}</span></div>
      <div class="conf-line"><span class="conf-line__label">Fonamentació</span><span class="conf-line__value">${fmtEur(result.contractacio_externa?.fonamentacio)}</span></div>
      <div class="conf-line"><span class="conf-line__label">IVA (10%)</span><span class="conf-line__value">${fmtEur(result.iva)}</span></div>
    `;
    breakdown.appendChild(extra);

    // Total
    const totalRow = document.createElement('div');
    totalRow.className = 'conf-total';
    totalRow.innerHTML = `<span class="conf-total__label">Total estimat (IVA inclòs)</span><span class="conf-total__value">${fmtEur(total)}</span>`;
    breakdown.appendChild(totalRow);

    // Mostrar resultat, amagar cards
    document.getElementById('confResult').classList.add('active');
    document.querySelectorAll('.conf-form .conf-section').forEach((s) => { s.style.display = 'none'; });
    updateProgress();

    // Scroll suau cap al resultat
    setTimeout(() => {
      document.getElementById('confResult').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 150);
  }

  // ── Restart ────────────────────────────────────────────────
  function handleRestart() {
    if (!confirm('Estàs segur? Es perdrà la configuració actual.')) return;
    localStorage.removeItem(STORAGE_KEY);
    location.reload();
  }

  // ── PDF (server-side · POST a /api/download-pdf) ──────────
  async function handleDownloadPdf() {
    if (!state.result) return;
    const btn = document.getElementById('btnDownloadPdf');
    const original = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.innerHTML = 'Generant PDF…'; }

    try {
      const payload = buildPayload();
      const res = await fetch('/api/download-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payload, result: state.result }),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const today = new Date().toISOString().slice(0, 10);
      a.download = `pressupost-papik-${today}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (err) {
      console.error('PDF error:', err);
      showToast('No s\'ha pogut generar el PDF. Torna a provar en uns moments.');
    } finally {
      if (btn) { btn.disabled = false; btn.innerHTML = original; }
    }
  }

  // ── Init ───────────────────────────────────────────────────
  function bindEvents() {
    document.body.addEventListener('click', (e) => {
      const cta = e.target.closest('.card-body-preview__cta[data-open]');
      if (cta) {
        const card = cta.closest('.conf-section');
        if (card?.classList.contains('card-locked')) return;
        const n = parseInt(cta.dataset.open, 10);
        openOverlay(n);
        return;
      }

      // Card hovered → click anywhere on done card opens overlay too
      const cardHeader = e.target.closest('.conf-section.card-done .panel-header, .conf-section.card-done .conf-card__img-wrap');
      if (cardHeader) {
        const card = cardHeader.closest('.conf-section');
        const n = parseInt(card.dataset.section, 10);
        openOverlay(n);
        return;
      }

      const id = e.target.id || e.target.closest('button')?.id;
      if (!id) return;
      if (id.startsWith('btnNext') && id !== 'btnCalc') { handleNext(); return; }
      if (id.startsWith('btnBack')) { handleBack(); return; }
      if (id === 'btnCalc') { handleNext(); return; } // section 4 's submit
      if (id === 'btnRestart') { handleRestart(); return; }
      if (id === 'btnDownloadPdf') { handleDownloadPdf(); return; }
      if (id === 'overlayClose' || e.target.closest('#overlayClose')) { closeOverlay(); return; }
      if (id === 'overlayBackdrop') { closeOverlay(); return; }
    });

    // Canvis en radio → marquem visualment + apliquem condicionals
    document.body.addEventListener('change', (e) => {
      if (e.target.type === 'radio') {
        markRadioSelected(e.target);
        applyConditionals();
        saveState();
      } else if (e.target.matches('input, select, textarea')) {
        saveState();
      }
    });

    // ESC tanca overlay
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && state.activeSection !== null) closeOverlay();
    });
  }

  function init() {
    if (!document.querySelector('.conf-section')) return; // no és la pàgina del configurador
    loadState();
    refreshCards();
    refreshAllRadioSelections();
    applyConditionals();
    bindEvents();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
