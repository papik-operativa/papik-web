/* ═══════════════════════════════════════════════════════════
   ATELIER · PAPIK · client logic (full flow)
   ─────────────────────────────────────────────────────────────
   13 step screens + reveal. Same questions, same payload schema,
   same /api/calcular contract as the legacy configurador.
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // ═══════════════════════════════════════════════════════════
  // BOOKING · Cal.com (cal.eu, instància EU) routing per m²
  // ───────────────────────────────────────────────────────────
  // Cases sota 150 m² → l'equip operatiu d'habitatges petits.
  // Cases de 150 m² o més → l'equip operatiu de projectes grans.
  // Per canviar les URLs (o el llindar), edita només aquestes constants.
  // ═══════════════════════════════════════════════════════════
  // calLink = el username + slug de l'event type, sense domini.
  // El widget s'encarrega d'apuntar a app.cal.eu (l'embed.js oficial
  // gestiona la X-Frame-Options que el domini públic cal.eu bloqueja).
  const CAL_LINK_SMALL    = 'operativa-papik/visita-comercial-per-a-l-analisi-del-pressupost-menys-150';
  const CAL_LINK_LARGE    = 'operativa-papik/visita-comercial-per-a-l-analisi-del-pressupost-mes-150';
  // Cal redirects cal.eu → www.cal.eu, so we tell the embed to use the
  // canonical origin directly. Otherwise the postMessage handshake
  // ('linkReady') fails and the iframe stays hidden forever.
  const CAL_EMBED_JS      = 'https://app.cal.eu/embed/embed.js';
  const CAL_EMBED_ORIGIN  = 'https://www.cal.eu';
  const CAL_THRESHOLD_M2  = 150;

  // ═══════════════════════════════════════════════════════════
  // AVISOS A L'EQUIP · Telegram (api/notificar-equip.py)
  // ───────────────────────────────────────────────────────────
  // Quan un client acaba el pressupost ('lead') o reserva visita
  // ('reserva'), enviem un avís al mòbil del cap amb resum + una
  // etiqueta de PRIORITAT. La prioritat surt de tres senyals; per
  // afinar-la, edita només aquestes constants (el backend no en sap
  // res, només formata el que el frontend li passa).
  //   · Pressupost alt   → total amb IVA ≥ PRIORITY_BUDGET_HIGH
  //   · Superfície gran  → m² ≥ PRIORITY_M2_LARGE
  //   · Municipi objectiu→ coincideix amb PRIORITY_MUNICIPIS
  // Nivell: 2+ senyals = alta · 1 senyal = mitjana · 0 = baixa.
  // ═══════════════════════════════════════════════════════════
  const NOTIFY_ENDPOINT     = '/api/notificar-equip';
  const PRIORITY_BUDGET_HIGH = 500000;   // € · llindar orientatiu, calibra'l amb dades reals
  const PRIORITY_M2_LARGE    = CAL_THRESHOLD_M2;  // mateix llindar que el routing de Cal
  // Noms normalitzats (minúscules, sense accents). `includes` sobre el
  // municipi triat, així "sant cugat del valles" cau dins "sant cugat".
  const PRIORITY_MUNICIPIS   = ['bellaterra', 'sant cugat', 'matadepera', 'sant quirze del valles'];

  // ── State (mirrors the backend's expected payload) ──────────
  // Defaults are intentionally empty/0. Each step applies its
  // `default` when the user lands on it for the first time, so
  // the summary ticker only shows values the user has reached.
  const state = {
    m2: 0,
    plantes: '',
    num_banys: 0,
    num_habitacions: 0,
    garatge: '',
    m2_garatge: 0,
    m2_porxos: 0,
    tipus_escala: 'no',
    tipus_coberta: '',
    tipus_facana: '',
    tipus_paviment: '',
    nivell_bany: '',
    plaques_solars: 'no',
    persianes: 'no',
    fan_coils: 'no',
    llar_foc: 'no',
    membrana_rado: 'no',
    domotica: 'no',
    municipi: '',
    nom: '',
    email: '',
    telefon: '',
  };

  // ── Step definitions ────────────────────────────────────────
  // `stage` controls which bg photo is active.
  // `summary` is the footer ticker key + label + formatter.
  // `if` is an optional predicate for conditional steps (e.g. escala).
  const fmtNum = (n) => new Intl.NumberFormat('ca-ES', { maximumFractionDigits: 0 }).format(n || 0);

  const STEPS = [
    // ── INTRO · plan upload OR manual start ───────────────────
    {
      id: 'intro', stage: 'estructura',
      eyebrow: 'Inici',
      title: 'Tens els plànols arquitectònics?',
      hint: "Puja un PDF o imatge i la nostra IA llegirà la superfície, plantes, banys i annexos per pre-omplir la configuració. Si no, comença des de zero.",
      type: 'intro',
      noCounter: true,
      validate: () => null,
      summary: null,
      ctaLabel: 'Començar configuració manual',
    },
    {
      id: 'm2', stage: 'estructura',
      eyebrow: 'Estructura',
      title: 'Quants m² té la casa?',
      hint: 'Superfície construïda total. Mínim 80 m².',
      type: 'number', stateKey: 'm2', unit: 'm²',
      min: 80, max: 700, default: 160,
      chips: [100, 140, 160, 200, 260],
      validate: (v) => (!v || v < 80) ? 'Cal una superfície mínima de 80 m².'
                     : (v > 700) ? 'Sembla massa gran. Confirma els metres quadrats.' : null,
      summary: { key: 'm2', label: 'Superfície', format: (v) => v ? `${fmtNum(v)} m²` : '—' },
    },
    {
      id: 'plantes', stage: 'estructura',
      eyebrow: 'Estructura',
      title: 'Quantes plantes té la casa?',
      hint: 'Inclou les plantes habitables (planta baixa, primera, segona…).',
      type: 'cards', stateKey: 'plantes',
      choices: [
        { value: '1', label: '1 planta',       sub: 'Compacta i sense escala' },
        { value: '2', label: '2 plantes',      sub: 'La distribució més habitual' },
        { value: '3', label: '3 o més',        sub: 'Verticalitat i jerarquia' },
      ],
      validate: (v) => v ? null : 'Selecciona el nombre de plantes.',
      summary: { key: 'plantes', label: 'Plantes',
                 format: (v) => ({ '1': '1 planta', '2': '2 plantes', '3': '3+ plantes' })[v] || '—' },
    },
    {
      id: 'escala', stage: 'estructura',
      if: () => state.plantes && state.plantes !== '1',
      eyebrow: 'Estructura',
      title: "Tipus d'escala interior?",
      hint: 'Acabat estructural i visual de l\'escala.',
      type: 'cards', stateKey: 'tipus_escala',
      choices: [
        { value: 'fusta',     label: 'Fusta estàndard',   sub: 'Càlida, neutra, transitable' },
        { value: 'metallica', label: 'Metàl·lica amb fusta', sub: 'Estructura industrial, graó càlid' },
        { value: 'no',        label: 'No necessito escala', sub: 'Avorrible si la casa té més plantes' },
      ],
      validate: (v) => v ? null : 'Selecciona el tipus d\'escala.',
      summary: { key: 'escala', label: 'Escala',
                 format: (v) => ({ fusta: 'Fusta', metallica: 'Metàl·lica', no: '—' })[v] || '—' },
    },
    {
      id: 'banys', stage: 'estructura',
      eyebrow: 'Estructura',
      title: 'Quants banys vol la casa?',
      hint: 'Compta cada espai amb wc, dutxa o banyera (incloent lavabos i en suite).',
      type: 'number', stateKey: 'num_banys', unit: '',
      min: 1, max: 10, default: 2,
      chips: [1, 2, 3, 4, 5],
      validate: (v) => (!v || v < 1) ? 'Cal almenys un bany.' : null,
      summary: { key: 'banys', label: 'Banys',
                 format: (v) => v ? `${v} bany${v === 1 ? '' : 's'}` : '—' },
    },
    {
      id: 'habitacions', stage: 'estructura',
      eyebrow: 'Estructura',
      title: "Quantes habitacions té la casa?",
      hint: "Compta dormitoris i sales independents (no banys ni cuina). Determina el nombre de fan coils.",
      type: 'number', stateKey: 'num_habitacions', unit: '',
      min: 1, max: 10, default: 3,
      chips: [2, 3, 4, 5, 6],
      validate: (v) => (!v || v < 1) ? "Indica el nombre d'habitacions." : null,
      summary: { key: 'habitacions', label: 'Habitacions',
                 format: (v) => v ? `${v} hab.` : '—' },
    },
    {
      id: 'nivell_bany', stage: 'estructura',
      eyebrow: 'Estructura',
      title: 'Quin nivell de bany vol?',
      hint: 'Qualitat i acabats dels banys.',
      type: 'cards', stateKey: 'nivell_bany',
      choices: [
        { value: 'estandar', label: 'Estàndard', sub: 'Sanitaris Roca bàsics' },
        { value: 'alt',      label: 'Alt',       sub: 'Roca ONA, aixeteria Tres Study' },
        { value: 'premium',  label: 'Premium',   sub: 'Disseny exclusiu, banyera exempta' },
      ],
      validate: (v) => v ? null : 'Selecciona el nivell de bany.',
      summary: { key: 'nivell_bany', label: 'Nivell bany',
                 format: (v) => ({ estandar: 'Estàndard', alt: 'Alt', premium: 'Premium' })[v] || '—' },
    },
    {
      id: 'garatge', stage: 'estructura',
      eyebrow: 'Estructura',
      title: 'Vol garatge?',
      hint: 'Si trieu sí, indica també la superfície del garatge.',
      type: 'yesno-with-conditional',
      stateKey: 'garatge',
      conditionalKey: 'm2_garatge',
      conditionalLabel: 'Quants m² té el garatge?',
      conditionalUnit: 'm²',
      conditionalDefault: 30,
      validate: () => {
        if (!state.garatge) return 'Indica si vols garatge.';
        if (state.garatge === 'si' && (!state.m2_garatge || state.m2_garatge < 1))
          return 'Indica la superfície del garatge.';
        return null;
      },
      summary: { key: 'garatge', label: 'Garatge',
                 format: () => state.garatge === 'si' ? `Sí · ${fmtNum(state.m2_garatge)} m²`
                              : state.garatge === 'no' ? 'No' : '—' },
    },
    {
      id: 'porxos', stage: 'estructura',
      eyebrow: 'Estructura',
      title: 'Quants m² de pòrxos o terrasses cobertes?',
      hint: 'Superfície de zones exteriors cobertes. Posa 0 si no n\'hi ha.',
      type: 'number', stateKey: 'm2_porxos', unit: 'm²',
      min: 0, max: 300, default: 0,
      chips: [0, 10, 20, 40, 80],
      validate: () => null,
      summary: { key: 'porxos', label: 'Pòrxos',
                 format: (v) => v > 0 ? `${fmtNum(v)} m²` : 'Sense' },
    },
    {
      id: 'coberta', stage: 'materials',
      eyebrow: 'Materials',
      title: 'Quin tipus de coberta?',
      hint: 'El tipus de teulat marca el caràcter exterior i el cost de la coberta.',
      type: 'cards', stateKey: 'tipus_coberta',
      choices: [
        { value: 'teula', label: 'Inclinada amb teula', sub: 'Àrab o mixta, registre tradicional' },
        { value: 'plana', label: 'Plana',               sub: 'Grava o transitable, registre modern' },
        { value: 'xapa',  label: 'Xapa metàl·lica',     sub: 'Zinc o galvanitzada, perfil industrial' },
      ],
      validate: (v) => v ? null : 'Selecciona el tipus de coberta.',
      summary: { key: 'coberta', label: 'Coberta',
                 format: (v) => ({ teula: 'Teula', plana: 'Plana', xapa: 'Xapa metàl·lica' })[v] || '—' },
    },
    {
      id: 'facana', stage: 'materials',
      eyebrow: 'Materials',
      title: 'Quina façana?',
      hint: 'Material exterior dels murs. Cada opció té una despesa i una durabilitat diferents.',
      type: 'cards', stateKey: 'tipus_facana',
      choices: [
        { value: 'sate',      label: 'SATE estàndard',  sub: 'Arrebossat, mat, sense relleu' },
        { value: 'ventilada', label: 'Façana ventilada',sub: 'Llistons de fusta verticals' },
        { value: 'suro',      label: 'Suro natural',    sub: 'Aïllant orgànic, color terra' },
        { value: 'accoya',    label: 'Fusta Accoya',    sub: 'Alta durada, daurada amb el temps' },
      ],
      validate: (v) => v ? null : 'Selecciona el tipus de façana.',
      summary: { key: 'facana', label: 'Façana',
                 format: (v) => ({ sate: 'SATE', ventilada: 'Ventilada', suro: 'Suro', accoya: 'Accoya' })[v] || '—' },
    },
    {
      id: 'paviment', stage: 'materials',
      eyebrow: 'Materials',
      title: 'Paviment interior?',
      hint: 'L\'acabat del terra a tota la casa (excepte els banys).',
      type: 'cards', stateKey: 'tipus_paviment',
      choices: [
        { value: 'formigo', label: 'Formigó polit', sub: 'Microciment, registre contemporani' },
        { value: 'ceramic', label: 'Ceràmic',       sub: 'Gres porcel·lànic, durador i neutre' },
        { value: 'parquet', label: 'Parquet',       sub: 'Fusta natural, càlid' },
      ],
      validate: (v) => v ? null : 'Selecciona el paviment.',
      summary: { key: 'paviment', label: 'Paviment',
                 format: (v) => ({ formigo: 'Formigó', ceramic: 'Ceràmic', parquet: 'Parquet' })[v] || '—' },
    },
    {
      id: 'equipament', stage: 'equipament',
      eyebrow: 'Equipament',
      title: 'Quin equipament vols?',
      hint: 'Tria els sistemes i extres que vols incloure. Tots són opcionals.',
      type: 'toggles',
      items: [
        { key: 'plaques_solars', label: 'Plaques solars fotovoltaiques', sub: 'Instal·lació d\'autoconsum (~4 kWp)' },
        { key: 'persianes',      label: 'Persianes motoritzades',         sub: 'Tipus Griesser o similar, amb comandament' },
        { key: 'fan_coils',      label: 'Fan coils',                       sub: 'Climatització per conductes, calor i fred' },
        { key: 'llar_foc',       label: 'Llar de foc',                     sub: 'Xemeneia de llenya o biomassa' },
        { key: 'membrana_rado',  label: 'Membrana anti-radó',              sub: 'Obligatòria en zones de risc moderat o alt' },
        { key: 'domotica',       label: 'Domòtica Loxone',                 sub: 'Control intel·ligent de llums, persianes, clima' },
      ],
      validate: () => null,
      summary: { key: 'equipament', label: 'Equipament',
                 format: () => {
                   const on = ['plaques_solars','persianes','fan_coils','llar_foc','membrana_rado','domotica']
                     .filter(k => state[k] === 'si');
                   return on.length ? `${on.length} extra${on.length === 1 ? '' : 's'}` : 'Bàsic';
                 } },
    },
    {
      id: 'ubicacio', stage: 'lloc',
      eyebrow: 'Lloc',
      title: 'On vols construir-la?',
      hint: 'El transport entre Sant Cugat i l\'obra forma part del pressupost.',
      type: 'select', stateKey: 'municipi',
      choices: [
        'Sant Cugat del Vallès', 'Bellaterra', 'Valldoreix',
        'Rubí', 'Cerdanyola del Vallès', 'Barberà del Vallès',
        'Sant Quirze del Vallès', 'Ripollet', 'Sabadell', 'Terrassa',
        'Barcelona', "L'Hospitalet de Llobregat", 'Molins de Rei',
        'Martorell', 'Badalona', 'Castelldefels', 'Granollers',
        'Sitges', 'Vilafranca del Penedès', 'Mataró', 'Manresa',
        'Igualada', 'Begues', 'Sant Quirze Safaja', 'Collsuspina',
        'Premià de Dalt', 'Sant Boi de Llobregat',
        'Santa Coloma de Gramenet', 'Vacarisses', 'Vallvidrera',
        'Matadepera', 'Llinars del Vallès', 'Sant Celoni',
        'Argentona', 'Castellar del Vallès', 'Vilanova i la Geltrú',
        'Vic', 'Altra localització (a consultar)',
      ],
      validate: (v) => v ? null : "Selecciona la ubicació de l'obra.",
      summary: { key: 'lloc', label: 'Lloc', format: (v) => v || '—' },
    },
    {
      id: 'contacte', stage: 'lloc',
      eyebrow: 'Final',
      title: 'Com t\'enviem el pressupost?',
      hint: 'Necessitem només dues dades per fer-te arribar el detall complet en PDF.',
      type: 'contact',
      validate: () => {
        if (!state.nom || !state.nom.trim()) return 'Introdueix el teu nom.';
        if (!state.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email)) return 'Introdueix un correu electrònic vàlid.';
        return null;
      },
      summary: null, // contact does not appear in the pill ticker
      ctaLabel: 'Veure el pressupost',
    },
  ];

  // Step ids that appear in the summary footer (in display order)
  const SUMMARY_LAYOUT = [
    { key: 'm2',         label: 'Superfície' },
    { key: 'plantes',    label: 'Plantes' },
    { key: 'banys',      label: 'Banys' },
    { key: 'habitacions',label: 'Habitacions' },
    { key: 'nivell_bany',label: 'Nivell bany' },
    { key: 'coberta',    label: 'Coberta' },
    { key: 'facana',     label: 'Façana' },
    { key: 'paviment',   label: 'Paviment' },
    { key: 'equipament', label: 'Equipament' },
    { key: 'lloc',       label: 'Lloc' },
  ];

  // ── DOM
  const container    = document.getElementById('stepContainer');
  const btnNext      = document.getElementById('btnNext');
  const btnNextLabel = document.getElementById('btnNextLabel');
  const btnBack      = document.getElementById('btnBack');
  const stepCurrent  = document.getElementById('stepCurrent');
  const stepTotal    = document.getElementById('stepTotal');
  const summaryEl    = document.getElementById('atelierSummary');
  const stageTitle   = document.getElementById('stageTitle');
  const stageSub     = document.getElementById('stageSub');

  // Index in STEPS we're currently showing
  let currentIdx = 0;
  // Cached result from /api/calcular (set after submit)
  let lastResult = null;

  // ── Helpers
  // `activeSteps()` excludes conditional steps (e.g. escala when plantes=1).
  // `countedSteps()` further excludes steps with `noCounter` (the intro screen).
  // We use the counted set for the "Pas X / Y" indicator.
  const activeSteps = () => STEPS.filter((s) => !s.if || s.if());
  const countedSteps = () => activeSteps().filter((s) => !s.noCounter);
  const stepNumberOf = (idx) => {
    const step = STEPS[idx];
    if (!step || step.noCounter) return 0;
    return countedSteps().findIndex((s) => s === step) + 1;
  };
  const totalSteps = () => countedSteps().length;

  function pad2 (n) { return String(n).padStart(2, '0'); }

  function setStage (stage) {
    document.body.dataset.stage = stage;
    document.querySelectorAll('.atelier-bg__image').forEach((el) => {
      el.classList.toggle('atelier-bg__image--active', el.dataset.stage === stage);
    });
  }

  function setStageCopy (eyebrow) {
    const titles = {
      Estructura: { h: 'Estructura i dimensions',  s: 'Defineix la geometria bàsica de la casa: superfície, plantes, banys i annexos.' },
      Materials:  { h: 'Materials i acabats',      s: 'Decideix el caràcter exterior i interior amb materials reals i durables.' },
      Equipament: { h: 'Equipament i confort',     s: 'Tria els sistemes que faran la casa més eficient i còmoda.' },
      Lloc:       { h: 'Lloc i contacte',          s: 'L\'última informació per ajustar el transport i fer-te arribar el detall.' },
      Final:      { h: 'Estem a punt',             s: 'Una última dada i veuràs el pressupost complet.' },
    };
    const copy = titles[eyebrow];
    if (copy && stageTitle && stageSub) {
      stageTitle.innerHTML = copy.h;
      stageSub.textContent  = copy.s;
    }
  }

  // ── Renderers per type ─────────────────────────────────────
  function renderNumber (step) {
    const v = state[step.stateKey] != null ? state[step.stateKey] : (step.default || 0);
    const chips = (step.chips || []).map((c) => {
      const active = c === v ? ' atelier-chip--active' : '';
      return `<button type="button" class="atelier-chip${active}" data-chip="${c}">${c}${step.unit ? ' ' + step.unit : ''}</button>`;
    }).join('');
    return `
      <div class="atelier-input">
        <input type="text" inputmode="numeric" id="qNumber" class="atelier-input__field" value="${v}"
               autocomplete="off" spellcheck="false" aria-label="${step.title}">
        ${step.unit ? `<span class="atelier-input__unit">${step.unit}</span>` : ''}
      </div>
      ${chips ? `<div class="atelier-chips" role="group" aria-label="Valors freqüents">${chips}</div>` : ''}
    `;
  }

  function renderCards (step) {
    const current = state[step.stateKey];
    return `
      <div class="atelier-options" role="radiogroup">
        ${step.choices.map((c) => {
          const active = c.value === current ? ' atelier-option--active' : '';
          return `
            <button type="button" class="atelier-option${active}" data-value="${c.value}" role="radio" aria-checked="${c.value === current}">
              <span class="atelier-option__head">
                <span class="atelier-option__label">${c.label}</span>
                <span class="atelier-option__check" aria-hidden="true">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2 7l3.5 3.5L12 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </span>
              <span class="atelier-option__sub">${c.sub}</span>
            </button>`;
        }).join('')}
      </div>
    `;
  }

  function renderYesNoConditional (step) {
    const current = state[step.stateKey];
    const condVal = state[step.conditionalKey] || step.conditionalDefault || '';
    const showCond = current === 'si';
    return `
      <div class="atelier-options atelier-options--yn" role="radiogroup">
        ${['si','no'].map((v) => {
          const active = v === current ? ' atelier-option--active' : '';
          const label = v === 'si' ? 'Sí, vull garatge' : 'No, sense garatge';
          const sub = v === 'si' ? 'Volum annex per als vehicles' : 'Aparcament exterior o no cal';
          return `
            <button type="button" class="atelier-option${active}" data-value="${v}" role="radio" aria-checked="${v === current}">
              <span class="atelier-option__head">
                <span class="atelier-option__label">${label}</span>
                <span class="atelier-option__check" aria-hidden="true">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2 7l3.5 3.5L12 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </span>
              </span>
              <span class="atelier-option__sub">${sub}</span>
            </button>`;
        }).join('')}
      </div>
      <div class="atelier-conditional ${showCond ? 'atelier-conditional--open' : ''}" id="condWrap">
        <label class="atelier-conditional__label" for="qConditional">${step.conditionalLabel}</label>
        <div class="atelier-input">
          <input type="text" inputmode="numeric" id="qConditional" class="atelier-input__field atelier-input__field--sm"
                 value="${condVal}" autocomplete="off" spellcheck="false">
          ${step.conditionalUnit ? `<span class="atelier-input__unit">${step.conditionalUnit}</span>` : ''}
        </div>
      </div>
    `;
  }

  function renderToggles (step) {
    return `
      <div class="atelier-toggles" role="group">
        ${step.items.map((it) => {
          const on = state[it.key] === 'si';
          return `
            <button type="button" class="atelier-toggle ${on ? 'atelier-toggle--on' : ''}" data-toggle="${it.key}" aria-pressed="${on}">
              <span class="atelier-toggle__copy">
                <span class="atelier-toggle__label">${it.label}</span>
                <span class="atelier-toggle__sub">${it.sub}</span>
              </span>
              <span class="atelier-toggle__switch" aria-hidden="true"><span class="atelier-toggle__knob"></span></span>
            </button>`;
        }).join('')}
      </div>
    `;
  }

  function renderSelect (step) {
    const current = state[step.stateKey] || '';
    return `
      <div class="atelier-select" role="group">
        <input type="text" id="qSelectSearch" class="atelier-select__search"
               placeholder="Cerca el teu municipi…" autocomplete="off" spellcheck="false">
        <div class="atelier-select__list" id="qSelectList">
          ${step.choices.map((c) => {
            const active = c === current ? ' atelier-select__opt--active' : '';
            return `<button type="button" class="atelier-select__opt${active}" data-value="${c}">${c}</button>`;
          }).join('')}
        </div>
      </div>
    `;
  }

  function renderContact () {
    return `
      <div class="atelier-form">
        <label class="atelier-form__field">
          <span class="atelier-form__label">Nom i cognoms</span>
          <input type="text" id="qNom" class="atelier-form__input" value="${state.nom || ''}"
                 autocomplete="name" placeholder="El teu nom complet">
        </label>
        <label class="atelier-form__field">
          <span class="atelier-form__label">Correu electrònic</span>
          <input type="email" id="qEmail" class="atelier-form__input" value="${state.email || ''}"
                 autocomplete="email" placeholder="correu@exemple.com">
        </label>
        <label class="atelier-form__field">
          <span class="atelier-form__label">Telèfon <em class="atelier-form__opt">(opcional)</em></span>
          <input type="tel" id="qTel" class="atelier-form__input" value="${state.telefon || ''}"
                 autocomplete="tel" placeholder="Ex: 612 345 678">
        </label>
      </div>
    `;
  }

  // INTRO step · plan upload dropzone + manual start path.
  function renderIntro () {
    return `
      <div class="atelier-intro">
        <div class="atelier-dropzone" id="planDropzone" tabindex="0" role="button"
             aria-label="Pujar plànol arquitectònic">
          <input type="file" id="planInput" accept=".pdf,.png,.jpg,.jpeg,.webp" hidden>
          <span class="atelier-dropzone__badge">IA · OpenAI Vision</span>
          <svg class="atelier-dropzone__icon" width="48" height="48" viewBox="0 0 48 48" fill="none" aria-hidden="true">
            <path d="M24 6v24M14 18l10-12 10 12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 30v8a4 4 0 0 0 4 4h24a4 4 0 0 0 4-4v-8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          </svg>
          <h3 class="atelier-dropzone__title">Arrossega el teu plànol</h3>
          <p class="atelier-dropzone__hint">
            o fes clic per seleccionar un fitxer<br>
            <span class="atelier-dropzone__formats">PDF · PNG · JPG · màx. 40 MB</span>
          </p>
        </div>

        <div class="atelier-intro__divider"><span>o bé</span></div>

        <p class="atelier-intro__alt">
          Si encara no tens els plànols, comença la configuració des de zero clicant <strong>Continuar</strong>.
        </p>
      </div>
    `;
  }

  // ANALYSIS view · cinematic scanner with rotating messages.
  // Replaces the question card in-place while /api/analitzar-plans works.
  let analysisMsgTimer = null;
  const ANALYSIS_MESSAGES = [
    'Llegint el document…',
    'Detectant superfície…',
    'Analitzant distribució…',
    'Interpretant estructura…',
    'Comptant banys…',
    'Identificant garatge…',
    'Calibrant proporcions…',
    'Configurant la teva casa…',
  ];

  function showAnalysisView (firstFileName) {
    document.body.dataset.stage = 'analyzing';
    container.innerHTML = `
      <div class="atelier-analysis">
        <div class="atelier-analysis__scanner" id="planScanner">
          <div class="atelier-analysis__placeholder">
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M14 3H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7l-4-4Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
              <path d="M14 3v4h4" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="atelier-analysis__image" id="planImage"></div>
          <div class="atelier-analysis__beam" aria-hidden="true"></div>
          <div class="atelier-analysis__brackets" aria-hidden="true">
            <span></span><span></span><span></span><span></span>
          </div>
          <div class="atelier-analysis__dots" aria-hidden="true">
            <span style="left:22%; top:32%;"></span>
            <span style="left:68%; top:48%;"></span>
            <span style="left:44%; top:72%;"></span>
            <span style="left:82%; top:24%;"></span>
            <span style="left:14%; top:62%;"></span>
          </div>
        </div>

        <div class="atelier-analysis__copy">
          <span class="atelier-pill atelier-pill--accent">Analitzant amb intel·ligència artificial</span>
          <h2 class="atelier-analysis__msg" id="analysisMsg">${ANALYSIS_MESSAGES[0]}</h2>
          <p class="atelier-analysis__file">${firstFileName || ''}</p>
        </div>
      </div>
    `;

    // Hide the footer during analysis (no controls available)
    const footer = document.querySelector('.atelier-footer');
    if (footer) footer.style.display = 'none';

    // Rotate the message every 1.8s
    if (analysisMsgTimer) clearInterval(analysisMsgTimer);
    let i = 0;
    analysisMsgTimer = setInterval(() => {
      i = (i + 1) % ANALYSIS_MESSAGES.length;
      const el = document.getElementById('analysisMsg');
      if (!el) return;
      el.style.opacity = '0';
      setTimeout(() => {
        if (el) { el.textContent = ANALYSIS_MESSAGES[i]; el.style.opacity = '1'; }
      }, 220);
    }, 1800);
  }

  function setAnalysisPlanImage (dataUrl) {
    const img = document.getElementById('planImage');
    if (img && dataUrl) {
      img.style.backgroundImage = `url(${dataUrl})`;
      img.classList.add('atelier-analysis__image--visible');
      // Hide the placeholder icon
      const ph = document.querySelector('.atelier-analysis__placeholder');
      if (ph) ph.style.display = 'none';
    }
  }

  function showAnalysisDone (data) {
    if (analysisMsgTimer) { clearInterval(analysisMsgTimer); analysisMsgTimer = null; }
    const found = [];
    if (data.m2)        found.push(`${Math.round(data.m2)} m²`);
    if (data.plantes)   found.push(`${data.plantes} plantes`);
    if (data.num_banys) found.push(`${data.num_banys} banys`);
    if (data.garatge === true) found.push('garatge');
    const msg = document.getElementById('analysisMsg');
    if (msg) {
      msg.style.opacity = '0';
      setTimeout(() => {
        if (msg) {
          msg.textContent = found.length ? 'Plànol llegit · ' + found.join(' · ') : 'Plànol llegit.';
          msg.style.opacity = '1';
        }
      }, 200);
    }
    const wrap = document.querySelector('.atelier-analysis');
    if (wrap) wrap.classList.add('atelier-analysis--done');
  }

  function showAnalysisError (errMsg) {
    if (analysisMsgTimer) { clearInterval(analysisMsgTimer); analysisMsgTimer = null; }
    const msg = document.getElementById('analysisMsg');
    if (msg) {
      msg.style.opacity = '0';
      setTimeout(() => {
        if (msg) { msg.textContent = errMsg || "No s'ha pogut llegir el plànol."; msg.style.opacity = '1'; }
      }, 200);
    }
    const wrap = document.querySelector('.atelier-analysis');
    if (wrap) wrap.classList.add('atelier-analysis--error');
    // Show a "skip and continue" CTA in this error state.
    const copy = document.querySelector('.atelier-analysis__copy');
    if (copy && !copy.querySelector('.atelier-cta')) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'atelier-cta';
      btn.style.marginTop = '16px';
      btn.innerHTML = '<span>Continuar manualment</span>';
      btn.addEventListener('click', () => {
        const footer = document.querySelector('.atelier-footer');
        if (footer) footer.style.display = '';
        document.body.dataset.stage = STEPS[currentIdx]?.stage || 'estructura';
        const nextIdx = nextActiveFrom(currentIdx, 'forward');
        if (nextIdx !== -1) transitionTo(nextIdx, 'forward');
      });
      copy.appendChild(btn);
    }
  }

  function applyPlanData (data) {
    if (data.m2)        state.m2        = Math.round(data.m2);
    if (data.plantes)   state.plantes   = String(data.plantes);
    if (data.num_banys) state.num_banys = parseInt(data.num_banys, 10);
    if (data.garatge === true) {
      state.garatge    = 'si';
      state.m2_garatge = data.m2_garatge ? Math.round(data.m2_garatge) : 30;
    } else if (data.garatge === false) {
      state.garatge = 'no';
    }
    if (data.porxos === true && data.m2_porxos) {
      state.m2_porxos = Math.round(data.m2_porxos);
    }
    // For multi-floor houses, pre-select a sensible default for the escala
    // step so the user isn't blocked by validation when speeding through.
    if (state.plantes && state.plantes !== '1') {
      if (!state.tipus_escala || state.tipus_escala === 'no') {
        state.tipus_escala = 'fusta';
      }
    }
    updateSummary();
  }

  // ── PDF rasterisation (pdf.js, same pattern as the legacy code) ─────
  const PDF_RENDER_SCALE = 2.2;
  const JPEG_QUALITY     = 0.82;
  const MAX_PDF_PAGES    = 4;

  async function pdfToJpegs (file) {
    const buf = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buf }).promise;
    const total = pdf.numPages;
    const indices = total <= MAX_PDF_PAGES
      ? Array.from({ length: total }, (_, i) => i + 1)
      : await pickBestPdfPages(pdf, MAX_PDF_PAGES);
    const out = [];
    for (const idx of indices) {
      try {
        const page = await pdf.getPage(idx);
        const viewport = page.getViewport({ scale: PDF_RENDER_SCALE });
        const canvas = document.createElement('canvas');
        canvas.width  = viewport.width;
        canvas.height = viewport.height;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        await page.render({ canvasContext: ctx, viewport }).promise;
        const blob = await new Promise((res) => canvas.toBlob(res, 'image/jpeg', JPEG_QUALITY));
        if (!blob) continue;
        const base = file.name.replace(/\.pdf$/i, '');
        out.push(new File([blob], `${base}-p${idx}.jpg`, { type: 'image/jpeg' }));
      } catch (e) { /* skip page */ }
    }
    return out;
  }

  // Score each PDF page by text content to pick the most plan-like ones.
  async function pickBestPdfPages (pdf, maxPages) {
    const total = pdf.numPages;
    const results = [];
    for (let i = 1; i <= total; i++) {
      try {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        const text = (content.items || []).map((it) => it.str).join(' ').toLowerCase();
        let score = 0;
        if (/planta|floor|plant/.test(text)) score += 6;
        if (/\d+[.,]?\d*\s*m[²2]/.test(text)) score += 12;
        if (/acotad|cotat|dimension/.test(text)) score += 10;
        const dims = (text.match(/\b\d+[.,]\d{2}\b/g) || []).length;
        score += Math.min(Math.floor(dims / 2), 10);
        results.push({ page: i, score });
      } catch (e) { results.push({ page: i, score: -100 }); }
    }
    results.sort((a, b) => b.score - a.score);
    const top = results.slice(0, maxPages).sort((a, b) => a.page - b.page);
    return top.map((x) => x.page);
  }

  function fileToBase64 (file) {
    return new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload = () => {
        const result = String(fr.result || '');
        const comma  = result.indexOf(',');
        resolve({ name: file.name, mime: file.type || '',
                  data_b64: comma >= 0 ? result.slice(comma + 1) : result });
      };
      fr.onerror = () => reject(fr.error);
      fr.readAsDataURL(file);
    });
  }

  function fileToDataUrl (file) {
    return new Promise((resolve, reject) => {
      const fr = new FileReader();
      fr.onload  = () => resolve(String(fr.result || ''));
      fr.onerror = () => reject(fr.error);
      fr.readAsDataURL(file);
    });
  }

  // ── Plan upload flow · entry point from the intro step ─────────────
  async function onPlanUpload (files) {
    const ACCEPT_RE = /\.(pdf|png|jpe?g|webp)$/i;
    const MAX_MB    = 40;
    const valid = files.filter((f) => ACCEPT_RE.test(f.name)).slice(0, 3);
    if (!valid.length) {
      alert('Format no acceptat. Puja PDF, PNG, JPG o WEBP.');
      return;
    }
    const oversized = valid.find((f) => f.size > MAX_MB * 1024 * 1024);
    if (oversized) {
      alert(`«${oversized.name}» supera ${MAX_MB} MB. Comprimeix-lo i torna-ho a provar.`);
      return;
    }
    if (!window.pdfjsLib && valid.some((f) => /\.pdf$/i.test(f.name))) {
      alert('PDF.js encara s\'està carregant. Espera un segon i torna-ho a provar.');
      return;
    }

    // Switch to the analysis view immediately so the user sees motion.
    showAnalysisView(valid[0].name);

    let expanded = [];
    try {
      for (const f of valid) {
        const isPdf = /\.pdf$/i.test(f.name) || f.type === 'application/pdf';
        if (isPdf) {
          const pages = await pdfToJpegs(f);
          if (!pages.length) throw new Error(`No s'ha pogut renderitzar «${f.name}».`);
          expanded.push(...pages);
        } else {
          expanded.push(f);
        }
      }
    } catch (err) {
      showAnalysisError(err.message || 'Error preparant els fitxers.');
      return;
    }

    // Show the rasterised first image inside the scanner.
    try {
      const previewUrl = await fileToDataUrl(expanded[0]);
      setAnalysisPlanImage(previewUrl);
    } catch (e) { /* ignore preview errors */ }

    try {
      const encoded = await Promise.all(expanded.map(fileToBase64));
      const res = await fetch('/api/analitzar-plans', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ files: encoded }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || 'No s\'han pogut analitzar els plànols.');
      }
      applyPlanData(data);
      showAnalysisDone(data);
      // Restore footer + auto-advance to step m² with pre-filled values
      setTimeout(() => {
        const footer = document.querySelector('.atelier-footer');
        if (footer) footer.style.display = '';
        const nextIdx = nextActiveFrom(currentIdx, 'forward');
        if (nextIdx !== -1) transitionTo(nextIdx, 'forward');
      }, 2000);
    } catch (err) {
      showAnalysisError(err.message || 'Error de connexió. Torna-ho a provar.');
    }
  }

  // Layout per step type — drives card width + alignment.
  // The card morphs between layouts during step transitions.
  function layoutForStep (step) {
    if (!step) return 'compact';
    if (step.layout) return step.layout;
    switch (step.type) {
      case 'intro':                  return 'center';  // welcome card centered
      case 'number':                 return 'compact'; // right-anchored, slim
      case 'cards':                  return 'center';  // centered, medium
      case 'yesno-with-conditional': return 'center';
      case 'contact':                return 'center';
      case 'toggles':                return 'wide';    // centered, wider for the list
      case 'select':                 return 'wide';
      default:                       return 'compact';
    }
  }

  function renderStep (idx) {
    const step = STEPS[idx];
    if (!step) return;

    // Apply step default on first visit if state is empty/0.
    // For `yesno-with-conditional` we don't auto-fill (user must pick).
    if (step.stateKey && step.default != null && (!state[step.stateKey] || state[step.stateKey] === 0)
        && step.type !== 'yesno-with-conditional') {
      state[step.stateKey] = step.default;
    }

    // Apply step layout (compact / center / wide) before rendering content.
    // This drives both the body[data-layout] CSS and the FLIP transition.
    const layout = layoutForStep(step);
    document.body.dataset.layout = layout;

    const stepN = stepNumberOf(idx);
    const totalN = totalSteps();

    let body = '';
    switch (step.type) {
      case 'number':                   body = renderNumber(step); break;
      case 'cards':                    body = renderCards(step); break;
      case 'yesno-with-conditional':   body = renderYesNoConditional(step); break;
      case 'toggles':                  body = renderToggles(step); break;
      case 'select':                   body = renderSelect(step); break;
      case 'contact':                  body = renderContact(step); break;
      case 'intro':                    body = renderIntro(step); break;
    }

    // Header: counter pill text + per-step counter ratio.
    // Intro skips the "Pas X · …" numbering and uses just the eyebrow.
    const pillText = step.noCounter ? step.eyebrow : `Pas ${pad2(stepN)} · ${step.eyebrow}`;
    const counterHtml = step.noCounter
      ? ''
      : `<span class="atelier-card__counter" aria-hidden="true">
           <span class="atelier-card__counter-current">${stepN}</span>
           <span class="atelier-card__counter-sep">de</span>
           <span class="atelier-card__counter-total">${totalN}</span>
         </span>`;

    container.innerHTML = `
      <header class="atelier-card__head">
        <span class="atelier-pill atelier-pill--accent">${pillText}</span>
        ${counterHtml}
      </header>
      <h2 class="atelier-card__question">${step.title}</h2>
      <p class="atelier-card__hint">${step.hint}</p>
      ${body}
      <p class="atelier-card__feedback" id="qFeedback" role="status"></p>
    `;

    // Wire inputs by type
    wireStepBehavior(step);

    // Stage bg + copy
    setStage(step.stage);
    setStageCopy(step.eyebrow);

    // Top bar counter — hide for intro (no number applicable)
    const barNav = document.querySelector('.atelier-bar__nav');
    if (barNav) barNav.style.visibility = step.noCounter ? 'hidden' : 'visible';
    if (stepCurrent) stepCurrent.textContent = pad2(stepN);
    if (stepTotal)   stepTotal.textContent   = pad2(totalN);

    // Back button visibility — hidden on intro (no previous step) and on step 1
    if (btnBack) btnBack.hidden = step.noCounter || stepN === 1;

    // CTA label changes on last step
    if (btnNextLabel) {
      btnNextLabel.textContent = step.ctaLabel || (stepN === totalN ? 'Veure el pressupost' : 'Continuar');
    }

    updateSummary();
  }

  // ── Wire inputs ────────────────────────────────────────────
  function wireStepBehavior (step) {
    if (step.type === 'intro') {
      const dz   = document.getElementById('planDropzone');
      const inp  = document.getElementById('planInput');
      if (!dz || !inp) return;

      dz.addEventListener('click', () => inp.click());
      dz.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); inp.click(); }
      });
      inp.addEventListener('change', () => {
        if (inp.files && inp.files.length) onPlanUpload(Array.from(inp.files));
      });
      ['dragenter', 'dragover'].forEach((ev) => {
        dz.addEventListener(ev, (e) => {
          e.preventDefault(); e.stopPropagation();
          dz.classList.add('atelier-dropzone--over');
        });
      });
      ['dragleave', 'drop'].forEach((ev) => {
        dz.addEventListener(ev, (e) => {
          e.preventDefault(); e.stopPropagation();
          dz.classList.remove('atelier-dropzone--over');
        });
      });
      dz.addEventListener('drop', (e) => {
        const files = Array.from((e.dataTransfer && e.dataTransfer.files) || []);
        if (files.length) onPlanUpload(files);
      });
      return;
    }

    if (step.type === 'number') {
      const inp = document.getElementById('qNumber');
      const chips = container.querySelectorAll('.atelier-chip');
      if (inp) {
        const onInput = () => {
          const v = parseInt((inp.value || '').replace(/[^\d]/g, ''), 10);
          state[step.stateKey] = isNaN(v) ? 0 : v;
          chips.forEach((c) => c.classList.toggle('atelier-chip--active', parseInt(c.dataset.chip, 10) === state[step.stateKey]));
          updateSummary();
          clearFeedback();
        };
        inp.addEventListener('input', onInput);
        inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); onNext(); } });
        setTimeout(() => inp.focus({ preventScroll: true }), 350);
      }
      chips.forEach((chip) => chip.addEventListener('click', () => {
        const v = parseInt(chip.dataset.chip, 10);
        state[step.stateKey] = v;
        if (inp) inp.value = String(v);
        chips.forEach((c) => c.classList.toggle('atelier-chip--active', c === chip));
        updateSummary();
        clearFeedback();
      }));
    }

    if (step.type === 'cards') {
      const opts = container.querySelectorAll('.atelier-option');
      opts.forEach((opt) => opt.addEventListener('click', () => {
        const v = opt.dataset.value;
        state[step.stateKey] = v;
        opts.forEach((o) => {
          o.classList.toggle('atelier-option--active', o === opt);
          o.setAttribute('aria-checked', o === opt ? 'true' : 'false');
        });
        updateSummary();
        clearFeedback();
      }));
    }

    if (step.type === 'yesno-with-conditional') {
      const opts = container.querySelectorAll('.atelier-option');
      const condWrap = document.getElementById('condWrap');
      const condInp  = document.getElementById('qConditional');

      opts.forEach((opt) => opt.addEventListener('click', () => {
        const v = opt.dataset.value;
        state[step.stateKey] = v;
        opts.forEach((o) => {
          o.classList.toggle('atelier-option--active', o === opt);
          o.setAttribute('aria-checked', o === opt ? 'true' : 'false');
        });
        const show = v === 'si';
        if (condWrap) condWrap.classList.toggle('atelier-conditional--open', show);
        if (show && (!state[step.conditionalKey] || state[step.conditionalKey] < 1)) {
          state[step.conditionalKey] = step.conditionalDefault || 0;
          if (condInp) condInp.value = String(state[step.conditionalKey]);
        }
        if (!show) state[step.conditionalKey] = 0;
        updateSummary();
        clearFeedback();
        if (show && condInp) setTimeout(() => condInp.focus({ preventScroll: true }), 400);
      }));

      if (condInp) {
        condInp.addEventListener('input', () => {
          const v = parseInt((condInp.value || '').replace(/[^\d]/g, ''), 10);
          state[step.conditionalKey] = isNaN(v) ? 0 : v;
          updateSummary();
          clearFeedback();
        });
      }
    }

    if (step.type === 'toggles') {
      const btns = container.querySelectorAll('.atelier-toggle');
      btns.forEach((btn) => btn.addEventListener('click', () => {
        const key = btn.dataset.toggle;
        const next = state[key] === 'si' ? 'no' : 'si';
        state[key] = next;
        btn.classList.toggle('atelier-toggle--on', next === 'si');
        btn.setAttribute('aria-pressed', next === 'si' ? 'true' : 'false');
        updateSummary();
      }));
    }

    if (step.type === 'select') {
      const search = document.getElementById('qSelectSearch');
      const list   = document.getElementById('qSelectList');
      if (search && list) {
        search.addEventListener('input', () => {
          const q = search.value.trim().toLowerCase();
          list.querySelectorAll('.atelier-select__opt').forEach((opt) => {
            const txt = opt.textContent.toLowerCase();
            opt.style.display = !q || txt.includes(q) ? '' : 'none';
          });
        });
        list.addEventListener('click', (e) => {
          const opt = e.target.closest('.atelier-select__opt');
          if (!opt) return;
          state.municipi = opt.dataset.value;
          list.querySelectorAll('.atelier-select__opt').forEach((o) => o.classList.toggle('atelier-select__opt--active', o === opt));
          search.value = opt.textContent;
          updateSummary();
          clearFeedback();
        });
        setTimeout(() => search.focus({ preventScroll: true }), 350);
      }
    }

    if (step.type === 'contact') {
      const nom = document.getElementById('qNom');
      const em  = document.getElementById('qEmail');
      const tel = document.getElementById('qTel');
      if (nom) nom.addEventListener('input', () => { state.nom = nom.value; clearFeedback(); });
      if (em)  em.addEventListener('input',  () => { state.email = em.value; clearFeedback(); });
      if (tel) tel.addEventListener('input', () => { state.telefon = tel.value; });
      setTimeout(() => nom && nom.focus({ preventScroll: true }), 350);
    }
  }

  // ── Summary ticker ─────────────────────────────────────────
  function updateSummary () {
    if (!summaryEl) return;
    const html = SUMMARY_LAYOUT.map((item) => {
      const step = STEPS.find((s) => s.summary && s.summary.key === item.key);
      let val = '—';
      let filled = false;
      if (step) {
        const sKey = step.stateKey;
        const raw  = sKey ? state[sKey] : null;
        const out = step.summary.format(raw);
        val = out;
        filled = out !== '—' && out !== 'Sense' && out !== 'Bàsic';
      }
      // Active = current step's summary
      const currentStep = STEPS[currentIdx];
      const isActive = currentStep && currentStep.summary && currentStep.summary.key === item.key;
      const cls = `atelier-summary__item${filled ? ' atelier-summary__item--filled' : ''}${isActive ? ' atelier-summary__item--active' : ''}`;
      return `
        <div class="${cls}" role="listitem" data-key="${item.key}">
          <span class="atelier-summary__key">${item.label}</span>
          <span class="atelier-summary__val">${val}</span>
        </div>`;
    }).join('');
    summaryEl.innerHTML = html;
    updatePlanta();
  }

  // ═══════════════════════════════════════════════════════════
  // PLANTA VIVA · esquema 2D que es dibuixa sol amb la config
  // ───────────────────────────────────────────────────────────
  // SVG generat per codi des de `state`. NO és el plànol
  // definitiu: és un esquema il·lustratiu (cap distribució real
  // es deriva només de m² + nº d'estances). Es redibuixa a cada
  // updateSummary() i s'anima amb GSAP.
  // ═══════════════════════════════════════════════════════════
  let plantaFloor = 0;     // pis actiu a les pestanyes
  let plantaOpen  = true;  // panell desplegat?

  // Reparteix un rectangle entre estances (treemap binari simple).
  function plantaTreemap (rect, items) {
    const total = items.reduce((s, it) => s + it.weight, 0) || 1;
    function split (r, list, sum) {
      if (list.length === 1) {
        list[0].x = r.x; list[0].y = r.y; list[0].w = r.w; list[0].h = r.h; return;
      }
      let acc = 0, i = 0; const half = sum / 2;
      while (i < list.length - 1 && acc + list[i].weight < half) { acc += list[i].weight; i++; }
      const a = list.slice(0, i + 1), b = list.slice(i + 1);
      const aSum = a.reduce((s, it) => s + it.weight, 0);
      const bSum = sum - aSum;
      if (r.w >= r.h) {
        const wa = r.w * (aSum / sum);
        split({ x: r.x, y: r.y, w: wa, h: r.h }, a, aSum);
        split({ x: r.x + wa, y: r.y, w: r.w - wa, h: r.h }, b, bSum);
      } else {
        const ha = r.h * (aSum / sum);
        split({ x: r.x, y: r.y, w: r.w, h: ha }, a, aSum);
        split({ x: r.x, y: r.y + ha, w: r.w, h: r.h - ha }, b, bSum);
      }
    }
    split(rect, items, total);
    return items;
  }

  // Llista d'estances per a un pis donat (esquemàtic, honest).
  function plantaRooms (floor) {
    const banys = Math.max(0, parseInt(state.num_banys || 0, 10) || 0);
    const habs  = Math.max(0, parseInt(state.num_habitacions || 0, 10) || 0);
    const plantes = parseInt(state.plantes || '1', 10) || 1;
    const rooms = [];
    const R = (label, weight, cls) => rooms.push({ label, weight, cls });
    if (plantes <= 1) {
      R('Sala-menjador', 3, 'sala');
      R('Cuina', 1.6, 'cuina');
      for (let i = 0; i < habs; i++) R('Dormitori', 1.7, 'dorm');
      for (let i = 0; i < banys; i++) R('Bany', 0.9, 'bany');
    } else if (floor === 0) {
      R('Sala-menjador', 3, 'sala');
      R('Cuina', 1.6, 'cuina');
      R('Bany', 0.9, 'bany');
      R('Escala', 0.7, 'escala');
    } else {
      const uppers = plantes - 1;
      const habsUp = Math.ceil(habs / uppers) || 0;
      const start = (floor - 1) * habsUp;
      const thisHabs = Math.max(0, Math.min(habsUp, habs - start));
      for (let i = 0; i < thisHabs; i++) R('Dormitori', 1.7, 'dorm');
      const banysUp = Math.max(0, banys - 1);
      const banysPerUp = Math.ceil(banysUp / uppers) || 0;
      const bStart = (floor - 1) * banysPerUp;
      const thisBanys = Math.max(0, Math.min(banysPerUp, banysUp - bStart));
      for (let i = 0; i < thisBanys; i++) R('Bany', 0.9, 'bany');
      R('Escala', 0.7, 'escala');
    }
    if (!rooms.length) R('Estança', 1, 'sala');
    return rooms;
  }

  // Etiqueta d'estança (s'amaga si l'estança és massa petita).
  function plantaLabel (cx, cy, name, sub, w, h) {
    if (w < 34 || h < 22) return '';
    const ny = sub ? cy - 4 : cy;
    const nameT = `<text class="planta-room__name" x="${cx.toFixed(1)}" y="${ny.toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${name}</text>`;
    const subT = sub ? `<text class="planta-room__sub" x="${cx.toFixed(1)}" y="${(cy + 9).toFixed(1)}" text-anchor="middle" dominant-baseline="middle">${sub}</text>` : '';
    return nameT + subT;
  }

  // ── Helpers de dibuix arquitectònic (línia fina, símbols escalats) ──
  function F (n) { return Math.round(n * 10) / 10; }

  // Mobiliari segons el tipus d'estança, encaixat dins el rectangle.
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
    }
    return s;
  }

  // Cotxe esquemàtic per al garatge.
  function fxCar (r) {
    const bw = Math.min(r.w * 0.5, 42), bh = Math.min(r.h * 0.78, 72);
    const bx = r.x + (r.w - bw) / 2, by = r.y + (r.h - bh) / 2;
    return `<rect class="planta-fx" x="${F(bx)}" y="${F(by)}" width="${F(bw)}" height="${F(bh)}" rx="6"/>` +
           `<rect class="planta-fx" x="${F(bx + bw * 0.18)}" y="${F(by + bh * 0.12)}" width="${F(bw * 0.64)}" height="${F(bh * 0.3)}" rx="3"/>`;
  }

  // Porta amb buit + arc d'obertura sobre una aresta (vertical o horitzontal).
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

  // Finestra: buit blanc dins la banda de mur + línia de vidre.
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

  // Línia de cota amb marques i etiqueta.
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

  // Distribució realista: estances a banda i banda d'un distribuïdor
  // central, amb porta de cada estança cap al passadís i columna d'escala
  // a un extrem. NO canvia quines/quantes estances hi ha (això ve de
  // plantaRooms); només com es col·loquen a l'espai.
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

    // 3+ estances: distribuïdor horitzontal + columna d'escala a la dreta
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

  // Construeix l'SVG d'una planta concreta (estil plànol arquitectònic).
  function buildPlantaSVG (floor) {
    const VW = 420, VH = 320, pad = 40;
    const m2 = Math.max(0, parseFloat(state.m2 || 0) || 0);
    if (!m2) return '';

    const plantes = parseInt(state.plantes || '1', 10) || 1;
    const footM2 = m2 / plantes;
    const wM = Math.sqrt(footM2 * 4 / 3);
    const hM = footM2 / wM;

    const hasGar = state.garatge === 'si' && (parseFloat(state.m2_garatge || 0) || 0) > 0;
    const garM2  = hasGar ? parseFloat(state.m2_garatge) : 0;
    const garWM  = hasGar ? Math.min(wM, Math.sqrt(garM2 * 1.2)) : 0;
    const garHM  = hasGar ? garM2 / Math.max(1, garWM) : 0;
    const hasPor = (parseFloat(state.m2_porxos || 0) || 0) > 0;
    const porM2  = hasPor ? parseFloat(state.m2_porxos) : 0;

    const showGar = hasGar && floor === 0;
    const showPor = hasPor && floor === 0;

    const totalWM = wM + (showGar ? garWM + 1.0 : 0);
    const totalHM = Math.max(hM, showGar ? garHM : 0);
    const porBand = showPor ? 2.4 : 0;
    const scale = Math.min((VW - 2 * pad) / totalWM, (VH - 2 * pad) / (totalHM + porBand));
    const ox = pad + ((VW - 2 * pad) - totalWM * scale) / 2;
    const oy = pad + ((VH - 2 * pad) - (totalHM + porBand) * scale) / 2;
    const px = (mx) => ox + mx * scale;
    const py = (my) => oy + my * scale;
    const houseX0 = showGar ? garWM + 1.0 : 0;

    const hx = px(houseX0), hy = py(0), hw = wM * scale, hh = hM * scale;
    const wallT = Math.max(3, Math.min(6, hw * 0.022));

    let walls = '', fx = '', doors = '', wins = '', labels = '';

    // Garatge (caixa amb mur i cotxe)
    if (showGar) {
      const gx = px(0), gy = py((hM - garHM) / 2), gw = garWM * scale, gh = garHM * scale;
      walls += `<rect class="planta-wall-fill" x="${F(gx)}" y="${F(gy)}" width="${F(gw)}" height="${F(gh)}"/>`;
      walls += `<rect class="planta-room-fill" x="${F(gx + wallT)}" y="${F(gy + wallT)}" width="${F(gw - 2 * wallT)}" height="${F(gh - 2 * wallT)}"/>`;
      fx += fxCar({ x: gx + wallT, y: gy + wallT, w: gw - 2 * wallT, h: gh - 2 * wallT });
      labels += plantaLabel(gx + gw / 2, gy + gh - 8, 'Garatge', '', gw, gh);
    }

    // Casa: poché del mur exterior
    walls += `<rect class="planta-wall-fill" x="${F(hx)}" y="${F(hy)}" width="${F(hw)}" height="${F(hh)}"/>`;
    walls += `<rect class="planta-room-fill" x="${F(hx + wallT)}" y="${F(hy + wallT)}" width="${F(hw - 2 * wallT)}" height="${F(hh - 2 * wallT)}"/>`;

    const inX0 = hx + wallT, inY0 = hy + wallT, inX1 = hx + hw - wallT, inY1 = hy + hh - wallT;
    const layout = layoutPlanta(plantaRooms(floor), inX0, inY0, inX1, inY1, scale);

    layout.rooms.forEach((r) => {
      walls += `<rect class="planta-partition" x="${F(r.x)}" y="${F(r.y)}" width="${F(r.w)}" height="${F(r.h)}"/>`;
      fx += furnish(r.cls, r);
      labels += plantaLabel(r.x + r.w / 2, r.y + 9, r.label, '', r.w, r.h);

      // Porta cap al distribuïdor segons la posició de l'estança
      if (r.door) {
        const d = r.door;
        if (d.edge === 'B')      doors += doorOnEdge(r.x, r.y + r.h, false, r.w, false);
        else if (d.edge === 'T') doors += doorOnEdge(r.x, r.y, false, r.w, true);
        else if (d.edge === 'R') doors += doorOnEdge(r.x + r.w, r.y, true, r.h, false);
        else if (d.edge === 'L') doors += doorOnEdge(r.x, d.atY != null ? d.atY : r.y, true, d.len != null ? d.len : r.h, true);
      }

      // Finestres a les parets exteriors que toca l'estança
      const ex = r.exposed || {};
      if (ex.t) wins += windowBand(r.x, hy, r.w, wallT, false);
      if (ex.b) wins += windowBand(r.x, hy + hh - wallT, r.w, wallT, false);
      if (ex.l) wins += windowBand(hx, r.y, r.h, wallT, true);
      if (ex.r) wins += windowBand(hx + hw - wallT, r.y, r.h, wallT, true);
    });

    // Porta d'entrada (planta baixa) al distribuïdor, a la paret esquerra
    if (floor === 0 && layout.corridor) {
      doors += doorOnEdge(hx + wallT, layout.corridor.y, true, layout.corridor.h, true);
    }

    // Pòrxo (llosa exterior puntejada)
    let porBottom = hy + hh;
    if (showPor) {
      const pY = hy + hh + 6, ph = 2.0 * scale;
      walls += `<rect class="planta-porch" x="${F(hx)}" y="${F(pY)}" width="${F(hw)}" height="${F(ph)}"/>`;
      labels += plantaLabel(hx + hw / 2, pY + ph / 2, 'Pòrxo', Math.round(porM2) + ' m²', hw, ph);
      porBottom = pY + ph;
    }

    // Cotes (amplada a sota, fons a l'esquerra) + àrea
    const dims = dimLine(hx, porBottom + 14, hw, false, F(wM) + ' m') +
                 dimLine(hx - 14, hy, hh, true, F(hM) + ' m');
    labels += `<text class="planta-area" x="${F(hx + hw / 2)}" y="${F(porBottom + 30)}" text-anchor="middle">${Math.round(footM2)} m² · planta</text>`;

    return `<svg viewBox="0 0 ${VW} ${VH}" class="planta-svg" role="img" aria-label="Plànol esquemàtic de la planta">` +
           walls + wins + doors + fx + dims + labels + `</svg>`;
  }

  // Redibuixa el panell (pestanyes + SVG) i anima amb GSAP.
  function updatePlanta () {
    const panel = document.getElementById('plantaPanel');
    if (!panel) return;
    const wrap = document.getElementById('plantaSvgWrap');
    const tabsEl = document.getElementById('plantaTabs');
    const plantes = parseInt(state.plantes || '1', 10) || 1;

    if (plantaFloor > plantes - 1) plantaFloor = plantes - 1;
    if (plantaFloor < 0) plantaFloor = 0;

    if (tabsEl) {
      if (plantes <= 1) {
        tabsEl.innerHTML = ''; tabsEl.hidden = true;
      } else {
        tabsEl.hidden = false;
        let t = '';
        for (let f = 0; f < plantes; f++) {
          const label = f === 0 ? 'Planta baixa' : ('Planta ' + f);
          t += `<button type="button" class="planta-tab${f === plantaFloor ? ' is-active' : ''}" data-floor="${f}">${label}</button>`;
        }
        tabsEl.innerHTML = t;
      }
    }

    if (wrap) {
      if (!parseFloat(state.m2 || 0)) {
        wrap.innerHTML = '<div class="planta-empty">Respon les primeres preguntes i veuràs la teva planta dibuixar-se aquí.</div>';
      } else {
        wrap.innerHTML = buildPlantaSVG(plantaFloor);
        if (window.gsap) {
          window.gsap.from(wrap.querySelectorAll('.planta-wall-fill, .planta-room-fill, .planta-partition'), {
            opacity: 0, duration: 0.4, stagger: 0.04, ease: 'power2.out'
          });
          window.gsap.from(wrap.querySelectorAll('.planta-fx, .planta-door, .planta-window'), {
            opacity: 0, duration: 0.35, stagger: 0.015, delay: 0.2, ease: 'power1.out'
          });
          window.gsap.from(wrap.querySelectorAll('text'), { opacity: 0, duration: 0.3, delay: 0.3 });
        }
      }
    }
  }

  // Lliga toggle + pestanyes del panell de planta.
  function wirePlanta () {
    const panel = document.getElementById('plantaPanel');
    if (!panel) return;
    const toggle = document.getElementById('plantaToggle');
    const tabsEl = document.getElementById('plantaTabs');
    plantaOpen = window.matchMedia('(min-width: 1024px)').matches;
    panel.classList.toggle('is-open', plantaOpen);
    if (toggle) {
      toggle.setAttribute('aria-expanded', String(plantaOpen));
      toggle.addEventListener('click', () => {
        plantaOpen = !plantaOpen;
        panel.classList.toggle('is-open', plantaOpen);
        toggle.setAttribute('aria-expanded', String(plantaOpen));
      });
    }
    if (tabsEl) tabsEl.addEventListener('click', (e) => {
      const b = e.target.closest('.planta-tab');
      if (!b) return;
      plantaFloor = parseInt(b.dataset.floor, 10) || 0;
      updatePlanta();
    });
    updatePlanta();
  }

  // ── Feedback
  function setFeedback (text, kind) {
    const fb = document.getElementById('qFeedback');
    if (!fb) return;
    fb.textContent = text || '';
    fb.classList.remove('atelier-card__feedback--error', 'atelier-card__feedback--ok');
    if (kind === 'error') fb.classList.add('atelier-card__feedback--error');
    else if (kind === 'ok') fb.classList.add('atelier-card__feedback--ok');
  }
  function clearFeedback () { setFeedback('', null); }

  // ── Navigation · FLIP-style transition.
  // Captures the card's bounding box, swaps layout + content, then animates
  // from the old box to the new one. Gives the cinematic "the panel changes
  // shape and position" feel between question types.
  function transitionTo (newIdx, direction) {
    if (currentIdx === newIdx) return;

    const newStep = STEPS[newIdx];
    if (!newStep) return;

    const oldLayout = document.body.dataset.layout || 'compact';
    const newLayout = layoutForStep(newStep);
    const layoutChanged = oldLayout !== newLayout;

    const dir = direction === 'back' ? -1 : 1;

    // Kill any pending tweens on the container. The entry animation in
    // particular leaves a `.from()` queued that, if it gets choked by other
    // GSAP work, can leave the container stuck at opacity 0 forever.
    if (window.gsap) {
      window.gsap.killTweensOf(container);
      window.gsap.set(container, { opacity: 1, clearProps: 'transform' });
    }

    // FIRST: capture the CURRENT geometry so we can FLIP-animate from it.
    const firstRect = container.getBoundingClientRect();

    // ── Synchronous swap ────────────────────────────────────────────
    // The state and DOM update happen *immediately*, not inside a GSAP
    // onComplete callback. This way the configurator keeps working even
    // if the GSAP animation later fails (which we've seen happen when
    // the global ticker is saturated with leftover tweens).
    currentIdx = newIdx;
    renderStep(currentIdx);

    if (!window.gsap) return;

    // LAST: re-read the geometry after layout settled.
    container.offsetWidth; // force a layout flush
    const lastRect = container.getBoundingClientRect();

    const dx = firstRect.left - lastRect.left;
    const dy = firstRect.top  - lastRect.top;
    const sx = firstRect.width  / Math.max(1, lastRect.width);
    const sy = firstRect.height / Math.max(1, lastRect.height);

    // PLAY: animate from the old geometry to identity. We only morph
    // scale/translate when the layout actually changed; for same-layout
    // transitions we keep a quick slide-from-side feel.
    if (layoutChanged) {
      window.gsap.fromTo(container,
        { x: dx, y: dy, scaleX: sx, scaleY: sy, opacity: 0, transformOrigin: 'top left' },
        { x: 0, y: 0, scaleX: 1, scaleY: 1, opacity: 1,
          duration: 0.6, ease: 'power3.out', overwrite: 'auto' });
    } else {
      window.gsap.fromTo(container,
        { opacity: 0, x: 16 * dir, scale: 0.97 },
        { opacity: 1, x: 0, scale: 1, duration: 0.45, ease: 'power3.out', overwrite: 'auto' });
    }
  }

  function nextActiveFrom (idx, direction) {
    const dir = direction === 'back' ? -1 : 1;
    let i = idx + dir;
    while (i >= 0 && i < STEPS.length) {
      const s = STEPS[i];
      if (!s.if || s.if()) return i;
      i += dir;
    }
    return -1;
  }

  function onNext () {
    const step = STEPS[currentIdx];
    if (!step) return;
    const err = step.validate ? step.validate(state[step.stateKey]) : null;
    if (err) {
      setFeedback(err, 'error');
      const inp = container.querySelector('input');
      if (inp) {
        inp.focus();
        const wrap = inp.closest('.atelier-input');
        if (wrap) {
          wrap.classList.add('atelier-input--error');
          setTimeout(() => wrap.classList.remove('atelier-input--error'), 600);
        }
      }
      return;
    }

    const nextIdx = nextActiveFrom(currentIdx, 'forward');
    if (nextIdx === -1) {
      // Final step → submit
      submit();
      return;
    }
    transitionTo(nextIdx, 'forward');
  }

  function onBack () {
    const prevIdx = nextActiveFrom(currentIdx, 'back');
    if (prevIdx === -1) return;
    transitionTo(prevIdx, 'back');
  }

  // ── Submit + Reveal
  function buildPayload () {
    return {
      m2: state.m2,
      plantes: state.plantes || '2',
      num_banys: state.num_banys || 2,
      num_habitacions: state.num_habitacions || 3,
      garatge: state.garatge || 'no',
      m2_garatge: state.m2_garatge || 0,
      m2_porxos: state.m2_porxos || 0,
      tipus_escala: state.tipus_escala || 'no',
      tipus_coberta: state.tipus_coberta || 'teula',
      tipus_facana: state.tipus_facana || 'sate',
      tipus_paviment: state.tipus_paviment || 'ceramic',
      nivell_bany: state.nivell_bany || 'alt',
      plaques_solars: state.plaques_solars || 'no',
      persianes: state.persianes || 'no',
      fan_coils: state.fan_coils || 'no',
      llar_foc: state.llar_foc || 'no',
      membrana_rado: state.membrana_rado || 'no',
      domotica: state.domotica || 'no',
      municipi: state.municipi || '',
      nom: (state.nom || '').trim(),
      email: (state.email || '').trim(),
      telefon: (state.telefon || '').trim(),
    };
  }

  function fmtEur (n) {
    return new Intl.NumberFormat('ca-ES', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(Math.round(n || 0));
  }

  async function submit () {
    // Hide footer back; show loading state on CTA
    if (btnNext) {
      btnNext.disabled = true;
      btnNextLabel.textContent = 'Calculant…';
    }
    showRevealLoading();

    try {
      const payload = buildPayload();
      const res = await fetch('/api/calcular', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      lastResult = data;
      window._confData = payload;
      window._confResult = data;
      renderReveal(data, payload);
    } catch (err) {
      console.error('Atelier submit error:', err);
      renderRevealError();
    }
  }

  function showRevealLoading () {
    container.innerHTML = `
      <div class="atelier-reveal atelier-reveal--loading">
        <span class="atelier-pill atelier-pill--accent">Calculant el teu pressupost</span>
        <div class="atelier-reveal__spinner" aria-hidden="true"></div>
        <p class="atelier-reveal__loading-msg">Recopilant les decisions i creuant amb les ràtios de projectes reals…</p>
      </div>
    `;
  }

  function renderRevealError () {
    container.innerHTML = `
      <div class="atelier-reveal">
        <span class="atelier-pill atelier-pill--accent">Algun error</span>
        <h2 class="atelier-reveal__title">No hem pogut calcular el pressupost.</h2>
        <p class="atelier-reveal__sub">Comprova la connexió i torna a provar.</p>
        <button class="atelier-cta" id="btnRetry" type="button"><span>Tornar a provar</span></button>
      </div>
    `;
    document.getElementById('btnRetry')?.addEventListener('click', submit);
    if (btnNext) { btnNext.disabled = false; btnNextLabel.textContent = 'Veure el pressupost'; }
  }

  // ── Reveal renderers ─────────────────────────────────────────
  // The left pane embeds the actual corporate PDF (same one users
  // download) inside an iframe. We do NOT regenerate it on every chat
  // change because that's 2-3 seconds per call; instead we mark it as
  // "stale" with an overlay showing the new total, and let the user
  // refresh on demand. The right pane is the conversational guide.

  // Tracks the latest blob URL so we can revoke the previous one when
  // a new PDF is generated (prevents memory leaks).
  let revealPdfBlobUrl = null;
  let revealPdfBusy    = false;

  async function fetchPdfBlobUrl (payload, result) {
    const res = await fetch('/api/download-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ payload, result }),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const blob = await res.blob();
    return URL.createObjectURL(blob);
  }

  async function mountRevealPdf (payload, result) {
    if (revealPdfBusy) return;
    revealPdfBusy = true;
    const wrap    = document.getElementById('revealPdfWrap');
    const loading = document.getElementById('revealPdfLoading');
    const frame   = document.getElementById('revealPdfFrame');
    if (!wrap || !loading || !frame) { revealPdfBusy = false; return; }

    // Show loading state
    loading.hidden = false;
    frame.classList.remove('atelier-reveal__pdf-frame--ready');

    try {
      const url = await fetchPdfBlobUrl(payload, result);
      // Swap in the new blob URL and revoke the previous one (if any)
      const previous = revealPdfBlobUrl;
      revealPdfBlobUrl = url;
      // Append #toolbar=0 to hide native PDF toolbar in Chromium where supported.
      // Note: not all browsers honor this hash; we accept the toolbar elsewhere.
      frame.src = url + '#toolbar=0&navpanes=0&view=FitH';
      // Wait for the iframe to actually paint before hiding the spinner.
      const onload = () => {
        frame.classList.add('atelier-reveal__pdf-frame--ready');
        loading.hidden = true;
        frame.removeEventListener('load', onload);
      };
      frame.addEventListener('load', onload);
      // Defensive: hide the spinner after 1.2s even if the load event is
      // unreliable (some browsers don't fire it for same-origin blob URLs).
      setTimeout(onload, 1200);
      if (previous) URL.revokeObjectURL(previous);
    } catch (err) {
      console.error('PDF preview error:', err);
      loading.hidden = true;
      const errEl = document.getElementById('revealPdfError');
      if (errEl) errEl.hidden = false;
    } finally {
      revealPdfBusy = false;
    }
  }

  function updateRevealHero (data, payload) {
    const priceEl   = document.getElementById('revealPrice');
    const perm2El   = document.getElementById('revealPerm2Val');
    const m2El      = document.getElementById('revealM2Val');
    const pendingEl = document.getElementById('revealPendingFonamentacioVal');
    if (!priceEl) return;
    const newTotal = data.total_pressupost || 0;
    const m2       = data.variables_derivades?.m2 || payload.m2 || 1;
    const fromVal  = parseFloat(priceEl.dataset.target || '0') || 0;
    priceEl.dataset.target = String(newTotal);
    if (m2El)    m2El.textContent    = fmtNum(m2);
    if (perm2El) perm2El.textContent = fmtEur(newTotal / m2);
    if (pendingEl) {
      pendingEl.textContent = '~ ' + fmtEur(data.contractacio_externa?.fonamentacio_estimat_pendent || 0);
    }

    if (window.gsap) {
      const obj = { v: fromVal };
      priceEl.classList.add('atelier-reveal__hero-price--bumping');
      window.gsap.to(obj, {
        v: newTotal,
        duration: 0.9,
        ease: 'power2.out',
        onUpdate: () => { priceEl.textContent = fmtEur(obj.v); },
        onComplete: () => {
          priceEl.textContent = fmtEur(newTotal);
          priceEl.classList.remove('atelier-reveal__hero-price--bumping');
        },
      });
    } else {
      priceEl.textContent = fmtEur(newTotal);
    }
  }

  function markRevealPdfStale (newTotal) {
    const stale = document.getElementById('revealPdfStale');
    const totalEl = document.getElementById('revealPdfStaleTotal');
    if (!stale) return;
    if (totalEl) totalEl.textContent = fmtEur(newTotal);
    stale.hidden = false;
    if (window.gsap) {
      window.gsap.fromTo(stale,
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.45, ease: 'power3.out' });
    }
  }

  function clearRevealPdfStale () {
    const stale = document.getElementById('revealPdfStale');
    if (stale && !stale.hidden) {
      if (window.gsap) {
        window.gsap.to(stale, {
          y: 12, opacity: 0, duration: 0.25, ease: 'power2.in',
          onComplete: () => { stale.hidden = true; },
        });
      } else {
        stale.hidden = true;
      }
    }
  }

  async function refreshRevealPdf () {
    const payload = window._confData   || buildPayload();
    const result  = window._confResult || lastResult;
    if (!payload || !result) return;
    await mountRevealPdf(payload, result);
    clearRevealPdfStale();
  }

  function renderReveal (data, payload) {
    const total    = data.total_pressupost || 0;
    const m2       = data.variables_derivades?.m2 || payload.m2 || 1;
    const perM2    = total / m2;
    const municipi = payload.municipi || data.variables_derivades?.municipi || '';

    container.innerHTML = `
      <div class="atelier-reveal">

        <!-- HERO · the big number stays above the PDF + chat, updates live -->
        <header class="atelier-reveal__hero">
          <span class="atelier-pill atelier-pill--accent">Pressupost estimat · ${data.data_emissio || ''}</span>
          <p class="atelier-reveal__hero-intro">La teva casa Passivhaus${municipi ? ` a <strong>${municipi}</strong>` : ''}.</p>
          <h2 class="atelier-reveal__hero-price" id="revealPrice" data-target="${total}">${fmtEur(total)}</h2>
          <p class="atelier-reveal__hero-perm2" id="revealPerm2">
            ≈ <span id="revealPerm2Val">${fmtEur(perM2)}</span>/m² ·
            <span id="revealM2Val">${fmtNum(m2)}</span> m² construïts · IVA inclòs
          </p>
          <!-- Fonamentació es factura a part (PAPIK la marca cas per cas, 0 € a
               52.000 €). Mostrem una estimació informativa ~ 300 €/m² perquè
               el client sàpiga que el preu final inclourà aquesta partida. -->
          <p class="atelier-reveal__hero-pending" id="revealPendingFonamentacio">
            + Fonamentació pendent de valorar
            <span id="revealPendingFonamentacioVal">~ ${fmtEur(data.contractacio_externa?.fonamentacio_estimat_pendent || 0)}</span>
          </p>
        </header>

        <div class="atelier-reveal__layout">

          <!-- LEFT · the actual corporate PDF (iframe) -->
          <article class="atelier-reveal__pdf-wrap" id="revealPdfWrap" aria-label="Vista prèvia del pressupost">
            <div class="atelier-reveal__pdf-loading" id="revealPdfLoading">
              <div class="atelier-reveal__spinner" aria-hidden="true"></div>
              <p>Generant la teva proposta corporativa…</p>
              <small>Tipografia, color i estructura oficials de PAPIK</small>
            </div>
            <div class="atelier-reveal__pdf-error" id="revealPdfError" hidden>
              <p>No s'ha pogut generar la previsualització.</p>
              <button type="button" class="atelier-cta atelier-cta--ghost" id="revealPdfRetry">Tornar a provar</button>
            </div>
            <iframe class="atelier-reveal__pdf-frame" id="revealPdfFrame"
                    title="Vista prèvia del pressupost" loading="lazy"></iframe>

            <!-- Stale overlay: appears after the chat modifies the budget -->
            <div class="atelier-reveal__pdf-stale" id="revealPdfStale" hidden>
              <div class="atelier-reveal__pdf-stale-text">
                <span class="atelier-reveal__pdf-stale-eyebrow">Nou pressupost</span>
                <span class="atelier-reveal__pdf-stale-total" id="revealPdfStaleTotal">—</span>
                <span class="atelier-reveal__pdf-stale-hint">El document encara mostra la versió anterior.</span>
              </div>
              <button type="button" class="atelier-reveal__pdf-stale-btn" id="revealPdfRefresh">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M21 12a9 9 0 1 1-3-6.7M21 4v5h-5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>Actualitzar PDF</span>
              </button>
            </div>
          </article>

          <!-- RIGHT · the conversational guide -->
          <section class="atelier-reveal__chat-wrap atelier-reveal-chat" aria-label="Guia virtual del pressupost">
            <header class="atelier-reveal-chat__head">
              <span class="atelier-pill atelier-pill--accent">Guia virtual</span>
              <h3 class="atelier-reveal-chat__title">Revisem el pressupost junts</h3>
              <p class="atelier-reveal-chat__sub">Pots fer canvis (treure piscina, més banys, façana ventilada…) i ho actualitzo a l'instant. No hi ha res definitiu fins que tu ho diguis.</p>
            </header>

            <div class="atelier-reveal-chat__messages" id="revealChatMessages" role="log" aria-live="polite">
              <div class="atelier-chat__msg atelier-chat__msg--bot">
                Hola. El teu pressupost ja és aquí. Demana'm canvis (ex: «treu la piscina», «vull 3 banys», «façana ventilada»…) o pregunta pel detall de qualsevol partida.
              </div>
            </div>

            <div class="atelier-reveal-chat__suggestions" id="revealChatSuggestions">
              <button type="button" class="atelier-reveal-chat__chip" data-q="Com puc reduir el pressupost sense perdre la certificació Passivhaus?">
                Com puc reduir el pressupost?
              </button>
              <button type="button" class="atelier-reveal-chat__chip" data-q="Treu les plaques solars del pressupost.">
                Treu les plaques solars
              </button>
              <button type="button" class="atelier-reveal-chat__chip" data-q="Què passaria si triés façana ventilada de fusta?">
                Què passa amb façana ventilada?
              </button>
            </div>

            <form class="atelier-reveal-chat__input-row" id="revealChatForm">
              <input type="text" class="atelier-chat__input" id="revealChatInput"
                     placeholder="Escriu un canvi o una pregunta…" autocomplete="off" spellcheck="false">
              <button type="submit" class="atelier-chat__send" aria-label="Enviar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M5 12l14-7-7 18-3-7-4-4Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
                </svg>
              </button>
            </form>
          </section>
        </div>

        <div class="atelier-reveal__actions">
          <button class="atelier-cta" id="btnFinalize" type="button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M5 12l5 5L20 7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Aquest és el meu pressupost · envia-me'l per email</span>
          </button>
          <button class="atelier-cta atelier-cta--outline" id="btnBooking" type="button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M8 2v4M16 2v4M3 10h18M5 6h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>Agendar visita comercial</span>
          </button>
          <button class="atelier-cta atelier-cta--outline" id="btnDownloadPdf" type="button">
            <span>Descarregar PDF</span>
            <svg width="18" height="12" viewBox="0 0 18 12" fill="none" aria-hidden="true">
              <path d="M9 1v9M4 6l5 5 5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="atelier-cta atelier-cta--ghost" id="btnRestart" type="button">
            <span>Començar de nou</span>
          </button>
        </div>
      </div>

      <!-- Nudge popup · fires after 20s of inactivity on the reveal -->
      <div class="atelier-nudge" id="revealNudge" hidden role="dialog" aria-modal="false" aria-labelledby="revealNudgeTitle">
        <button class="atelier-nudge__close" id="revealNudgeClose" type="button" aria-label="Tancar">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
            <path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </button>
        <span class="atelier-nudge__eyebrow">Guia virtual</span>
        <h4 class="atelier-nudge__title" id="revealNudgeTitle">Revisem el pressupost?</h4>
        <p class="atelier-nudge__text">Pots demanar canvis a la guia (treure piscina, més habitacions, façana ventilada…) i ho actualitzo a l'instant. No hi ha res definitiu fins que tu ho diguis.</p>
        <button class="atelier-nudge__cta" type="button" id="revealNudgeFocus">D'acord, parlem-ne</button>
      </div>

      <!-- Finalize confirmation toast -->
      <div class="atelier-finalized" id="revealFinalized" hidden role="status" aria-live="polite">
        <div class="atelier-finalized__icon" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path d="M5 12l5 5L20 7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h4 class="atelier-finalized__title">Perfecte, pressupost confirmat</h4>
        <p class="atelier-finalized__text">L'equip de PAPIK rebrà aquest pressupost al teu nom. Aviat habilitarem l'enviament directe per email; mentrestant, pots descarregar el PDF o agendar visita.</p>
      </div>
    `;

    // Hide top-bar nav + footer
    document.querySelector('.atelier-footer')?.setAttribute('hidden', '');
    document.querySelector('.atelier-bar__nav')?.setAttribute('hidden', '');
    document.body.dataset.stage = 'reveal';
    // Override the per-step layout so .atelier-card can expand to ~1180px
    // for the 2-column document + chat composition.
    document.body.dataset.layout = 'reveal';

    // Wire the inline post-budget chat (handles form_updates → mark stale)
    wireRevealChat();

    // Entry animation: fade in the reveal + count the price up
    if (window.gsap) {
      window.gsap.fromTo('.atelier-reveal', { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' });
      const priceEl = document.getElementById('revealPrice');
      if (priceEl) {
        const obj = { v: 0 };
        window.gsap.to(obj, {
          v: total,
          duration: 1.4,
          ease: 'power2.out',
          delay: 0.2,
          onUpdate: () => { priceEl.textContent = fmtEur(obj.v); },
          onComplete: () => { priceEl.textContent = fmtEur(total); },
        });
      }
    }

    // Kick off the PDF generation in the background. Spinner is already
    // shown by the loading state inside the wrap until the iframe paints.
    mountRevealPdf(payload, data);

    document.getElementById('btnRestart')?.addEventListener('click', () => {
      // Clean up the blob URL before unloading the page
      if (revealPdfBlobUrl) URL.revokeObjectURL(revealPdfBlobUrl);
      location.reload();
    });
    document.getElementById('btnDownloadPdf')?.addEventListener('click', downloadPdf);
    document.getElementById('btnBooking')?.addEventListener('click', openBookingModal);
    document.getElementById('btnFinalize')?.addEventListener('click', finalizeBudget);
    document.getElementById('revealPdfRefresh')?.addEventListener('click', refreshRevealPdf);
    document.getElementById('revealPdfRetry')?.addEventListener('click', () => {
      const errEl = document.getElementById('revealPdfError');
      if (errEl) errEl.hidden = true;
      mountRevealPdf(payload, data);
    });

    // Nudge: surface the chat after 20s if the user has done nothing.
    scheduleRevealNudge();

    // Avisa l'equip que hi ha un nou lead amb pressupost configurat.
    // Un sol cop per sessió (els re-render del chat no el repeteixen).
    if (!leadNotified) {
      leadNotified = true;
      notifyTeam('lead');
    }
  }

  // ── Inline reveal chat · standalone module, /api/chat-pressupost only
  // Lives inside the reveal card. Beyond Q&A it can MODIFY the budget:
  // when the backend returns form_updates, we apply them to state, ping
  // /api/calcular and re-render only the document subtree so the price
  // animates to its new value without resetting the conversation.
  function wireRevealChat () {
    const msgs = document.getElementById('revealChatMessages');
    const input = document.getElementById('revealChatInput');
    const form  = document.getElementById('revealChatForm');
    const sugg  = document.getElementById('revealChatSuggestions');
    if (!msgs || !input || !form) return;

    let convId = null;
    let busy = false;

    const append = (text, kind) => {
      const el = document.createElement('div');
      el.className = `atelier-chat__msg atelier-chat__msg--${kind}`;
      el.textContent = text;
      msgs.appendChild(el);
      msgs.scrollTop = msgs.scrollHeight;
      return el;
    };
    const appendTyping = () => {
      const el = document.createElement('div');
      el.className = 'atelier-chat__msg atelier-chat__msg--bot atelier-chat__typing';
      el.innerHTML = '<span></span><span></span><span></span>';
      msgs.appendChild(el);
      msgs.scrollTop = msgs.scrollHeight;
      return el;
    };

    async function recalcAndRefresh (updates) {
      // Apply updates to state, recalc the budget, mark the embedded PDF
      // as stale (with the new total shown over the iframe). The actual
      // PDF is NOT regenerated automatically — the user clicks "Actualitzar
      // PDF" when ready. Cheap, snappy, no flicker.
      const applied = chatApplyFormUpdates(updates);
      if (!applied.length) return { ok: false, applied: [] };
      const newPayload = buildPayload();
      try {
        const res = await fetch('/api/calcular', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newPayload),
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        lastResult = data;
        window._confData = newPayload;
        window._confResult = data;
        const newTotal = data.total_pressupost || 0;
        updateRevealHero(data, newPayload);
        markRevealPdfStale(newTotal);
        return { ok: true, applied, total: newTotal };
      } catch (err) {
        console.error('Reveal recalc error:', err);
        return { ok: false, applied };
      }
    }

    async function send (text) {
      const q = (text || '').trim();
      if (!q || busy) return;
      // Any interaction cancels the pending nudge popup.
      cancelRevealNudge();
      append(q, 'user');
      input.value = '';
      busy = true;
      input.disabled = true;
      const typing = appendTyping();
      try {
        const res = await fetch('/api/chat-pressupost', {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({
            message:         q,
            conversation_id: convId,
            budget_input:    window._confData   || buildPayload(),
            budget_result:   window._confResult || lastResult,
          }),
        });
        const data = await res.json();
        if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
        if (!res.ok || data.error) {
          append(data?.error || 'No he pogut respondre ara mateix.', 'bot');
        } else {
          if (data.answer) append(data.answer, 'bot');
          if (data.conversation_id) convId = data.conversation_id;
          if (data.form_updates && Object.keys(data.form_updates).length) {
            const recalc = await recalcAndRefresh(data.form_updates);
            if (recalc.ok) {
              const toast = chatFormatAppliedToast(recalc.applied);
              if (toast) append(toast, 'bot-note');
              append(`Nou pressupost: ${fmtEur(recalc.total)} (IVA inclòs).`, 'bot-note');
            } else if (recalc.applied.length) {
              append("He aplicat els canvis però no he pogut recalcular ara mateix. Torna-ho a intentar.", 'bot-note');
            }
          }
        }
      } catch (err) {
        if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
        append("No he pogut connectar amb la guia ara mateix. Torna-ho a provar en uns segons.", 'bot');
      } finally {
        busy = false;
        input.disabled = false;
        input.focus({ preventScroll: true });
      }
    }

    form.addEventListener('submit', (e) => { e.preventDefault(); send(input.value); });
    if (sugg) sugg.addEventListener('click', (e) => {
      const btn = e.target.closest('.atelier-reveal-chat__chip');
      if (!btn) return;
      const q = btn.dataset.q || btn.textContent || '';
      input.value = q;
      send(q);
    });
    // Cancel the nudge as soon as the user types or focuses the input.
    input.addEventListener('focus', cancelRevealNudge, { once: true });
    input.addEventListener('input', cancelRevealNudge, { once: true });
  }

  // ── Finalize budget · CTA placeholder (email pipeline lands in Fase 2)
  function finalizeBudget () {
    cancelRevealNudge();
    const toast = document.getElementById('revealFinalized');
    const btn   = document.getElementById('btnFinalize');
    if (btn) {
      btn.disabled = true;
      btn.classList.add('atelier-cta--success');
    }
    if (toast) {
      toast.hidden = false;
      if (window.gsap) {
        window.gsap.fromTo(toast,
          { opacity: 0, y: 18 },
          { opacity: 1, y: 0, duration: 0.55, ease: 'power3.out' });
      }
      toast.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  // ── Nudge popup · surfaces the chat after 20s of inactivity ─────
  let revealNudgeTimer = null;
  let revealNudgeShown = false;

  function scheduleRevealNudge () {
    cancelRevealNudge();
    revealNudgeShown = false;
    revealNudgeTimer = setTimeout(showRevealNudge, 20000);

    const close = document.getElementById('revealNudgeClose');
    const focusBtn = document.getElementById('revealNudgeFocus');
    if (close) close.addEventListener('click', hideRevealNudge);
    if (focusBtn) focusBtn.addEventListener('click', () => {
      hideRevealNudge();
      const input = document.getElementById('revealChatInput');
      if (input) {
        input.focus({ preventScroll: false });
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }

  function showRevealNudge () {
    if (revealNudgeShown) return;
    const el = document.getElementById('revealNudge');
    if (!el) return;
    el.hidden = false;
    revealNudgeShown = true;
    if (window.gsap) {
      window.gsap.fromTo(el,
        { opacity: 0, y: 14, scale: 0.96 },
        { opacity: 1, y: 0, scale: 1, duration: 0.5, ease: 'power3.out' });
    }
  }

  function hideRevealNudge () {
    const el = document.getElementById('revealNudge');
    if (!el || el.hidden) return;
    if (window.gsap) {
      window.gsap.to(el, {
        opacity: 0, y: 8, duration: 0.28, ease: 'power2.in',
        onComplete: () => { el.hidden = true; },
      });
    } else {
      el.hidden = true;
    }
  }

  function cancelRevealNudge () {
    if (revealNudgeTimer) {
      clearTimeout(revealNudgeTimer);
      revealNudgeTimer = null;
    }
    hideRevealNudge();
  }

  // ═══════════════════════════════════════════════════════════
  // BOOKING MODAL · official Cal.com embed.js
  // ───────────────────────────────────────────────────────────
  // We mount Cal's inline widget inside #bookingInline. The embed.js
  // bootstrapping snippet sets up window.Cal as a queue API, loads the
  // real script async, and replays queued calls when it's ready.
  // Reference: https://cal.com/docs/embed/embed-inline
  // ═══════════════════════════════════════════════════════════

  // Standard Cal embed bootstrapper. Copies the official one from their docs
  // verbatim (only the script URL is the EU instance). Sets up `window.Cal`.
  function loadCalEmbed () {
    if (window.Cal && window.Cal.loaded) return;
    (function (C, A, L) {
      var p = function (a, ar) { a.q.push(ar); };
      var d = C.document;
      C.Cal = C.Cal || function () {
        var cal = C.Cal;
        var ar = arguments;
        if (!cal.loaded) {
          cal.ns = {};
          cal.q = cal.q || [];
          d.head.appendChild(d.createElement('script')).src = A;
          cal.loaded = true;
        }
        if (ar[0] === L) {
          var api = function () { p(api, arguments); };
          var namespace = ar[1];
          api.q = api.q || [];
          if (typeof namespace === 'string') {
            cal.ns[namespace] = cal.ns[namespace] || api;
            p(cal.ns[namespace], ar);
            p(cal, ['initNamespace', namespace]);
          } else { p(cal, ar); }
          return;
        }
        p(cal, ar);
      };
    })(window, CAL_EMBED_JS, 'init');
    window.Cal('init', { origin: CAL_EMBED_ORIGIN });

    // Quan el client confirma la reserva dins l'iframe de Cal, Cal dispara
    // `bookingSuccessful`. Ho aprofitem per avisar l'equip al moment (push
    // de Telegram) amb la franja triada, a banda de l'avís propi de Cal.
    // loadCalEmbed és idempotent (guard a dalt), així el handler es
    // registra un sol cop.
    try {
      window.Cal('on', {
        action: 'bookingSuccessful',
        callback: (e) => {
          const d = (e && e.detail && e.detail.data) || {};
          const slot = d.date || d.startTime || (d.booking && d.booking.startTime) || '';
          notifyTeam('reserva', slot ? { slot } : {});
        },
      });
    } catch (_) { /* si l'API on no existeix, l'avís de 'lead' ja ha anat */ }
  }

  function pickCalLink () {
    const m2 = state.m2 || 0;
    return m2 < CAL_THRESHOLD_M2 ? CAL_LINK_SMALL : CAL_LINK_LARGE;
  }

  // ───────────────────────────────────────────────────────────
  // PRIORITAT DEL LEAD + AVÍS A L'EQUIP (Telegram)
  // ───────────────────────────────────────────────────────────
  function _norm (s) {
    return (s || '').toString().toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
  }

  // Calcula la prioritat a partir de tres senyals (pressupost · m² ·
  // municipi). Retorna nivell + motius llegibles per posar-los tant a
  // l'avís de Telegram com a les notes de la reserva de Cal.
  function computeLeadPriority () {
    const total = lastResult?.total_pressupost || 0;
    const m2    = state.m2 || 0;
    const muni  = _norm(state.municipi);
    const reasons = [];
    let score = 0;
    if (total >= PRIORITY_BUDGET_HIGH) { score++; reasons.push(`Pressupost alt (${fmtEur(total)})`); }
    if (m2 >= PRIORITY_M2_LARGE)       { score++; reasons.push(`Superfície gran (${fmtNum(m2)} m²)`); }
    if (muni && PRIORITY_MUNICIPIS.some(t => muni.includes(t))) {
      score++; reasons.push(`Municipi objectiu (${state.municipi})`);
    }
    const level = score >= 2 ? 'alta' : score === 1 ? 'mitjana' : 'baixa';
    return { level, score, reasons };
  }

  // Evita duplicar l'avís de 'lead' si el reveal es torna a renderitzar.
  let leadNotified = false;

  // Fire-and-forget: mai bloqueja la UI ni propaga errors. `keepalive`
  // perquè l'avís de 'reserva' sobrevisqui si Cal navega tot seguit.
  function notifyTeam (event, extra) {
    try {
      const body = {
        event,
        priority: computeLeadPriority(),
        lead: {
          nom:     state.nom     || '',
          email:   state.email   || '',
          telefon: state.telefon || '',
        },
        summary: {
          m2:              state.m2 || 0,
          plantes:         state.plantes || '',
          num_banys:       state.num_banys || 0,
          num_habitacions: state.num_habitacions || 0,
          garatge:         state.garatge || '',
          m2_garatge:      state.m2_garatge || 0,
          municipi:        state.municipi || '',
          total:           lastResult?.total_pressupost || 0,
        },
        ...(extra || {}),
      };
      fetch(NOTIFY_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        keepalive: true,
      }).catch(() => {});
    } catch (_) { /* mai trenquem el flux del client per un avís */ }
  }

  function buildCalConfig () {
    const notesParts = [];
    // Etiqueta de prioritat al davant perquè el cap la vegi a la nota de
    // la reserva de Cal (a banda del push de Telegram).
    const prio = computeLeadPriority();
    const prioLabel = prio.level === 'alta' ? 'PRIORITAT ALTA'
                    : prio.level === 'mitjana' ? 'Prioritat mitjana'
                    : 'Prioritat baixa';
    notesParts.push(prio.reasons.length ? `[${prioLabel} · ${prio.reasons.join(', ')}]` : `[${prioLabel}]`);
    if (state.telefon)   notesParts.push(`Tel: ${state.telefon}`);
    if (state.m2)        notesParts.push(`Superfície ${fmtNum(state.m2)} m²`);
    if (state.plantes)   notesParts.push(state.plantes === '1' ? '1 planta' : `${state.plantes} plantes`);
    if (state.num_banys) notesParts.push(`${state.num_banys} bany${state.num_banys === 1 ? '' : 's'}`);
    if (state.municipi)  notesParts.push(`Lloc: ${state.municipi}`);
    if (lastResult?.total_pressupost) {
      notesParts.push(`Pressupost estimat ${fmtEur(lastResult.total_pressupost)}`);
    }
    return {
      layout: 'month_view',
      theme:  'light',
      name:   state.nom   || '',
      email:  state.email || '',
      notes:  notesParts.join(' · '),
    };
  }

  let calMounted = false;

  function mountCalInline () {
    if (!window.Cal) return;
    const calLink = pickCalLink();
    const config  = buildCalConfig();
    // Clear any previous embed (e.g. if the user reopens after a m² change
    // that should route to the other commercial).
    const host = document.getElementById('bookingInline');
    if (host) host.innerHTML = '';
    window.Cal('inline', {
      elementOrSelector: '#bookingInline',
      calLink,
      config,
    });
    // Apply UI options after mount (theme + brand colour to match PAPIK)
    window.Cal('ui', {
      theme: 'light',
      cssVarsPerTheme: { light: { 'cal-brand': '#002819' } },
      hideEventTypeDetails: false,
      layout: 'month_view',
    });
    calMounted = true;
  }

  function openBookingModal () {
    const modal   = document.getElementById('bookingModal');
    const sub     = document.getElementById('bookingSub');
    const loading = document.getElementById('bookingLoading');
    if (!modal) return;

    // Routed sub-copy: tell the user which team will attend
    const m2 = state.m2 || 0;
    if (sub) {
      const equip = m2 < CAL_THRESHOLD_M2
        ? "l'equip comercial d'habitatges fins a 150 m²"
        : "l'equip comercial de projectes a partir de 150 m²";
      sub.textContent = `Tria un dia i hora per a la visita amb ${equip}. Ja sabran el detall del teu pressupost.`;
    }

    // Bootstrap Cal embed (idempotent) and mount the inline widget.
    // Hide the spinner once the iframe Cal creates has loaded; we listen
    // for the global `linkReady` event Cal dispatches via postMessage.
    if (loading) loading.style.display = 'flex';
    loadCalEmbed();
    mountCalInline();

    // Safety timeout in case the iframe load event is missed
    setTimeout(() => { if (loading) loading.style.display = 'none'; }, 2500);

    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('atelier-modal-open');
  }

  function closeBookingModal () {
    const modal = document.getElementById('bookingModal');
    if (!modal) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('atelier-modal-open');
    // Clear the embed host so a subsequent open re-mounts fresh
    // (with the right routing if m² changed in between).
    const host = document.getElementById('bookingInline');
    if (host) setTimeout(() => { host.innerHTML = ''; calMounted = false; }, 300);
  }

  function wireBookingModal () {
    document.getElementById('bookingClose')?.addEventListener('click', closeBookingModal);
    document.getElementById('bookingBackdrop')?.addEventListener('click', closeBookingModal);
    document.addEventListener('keydown', (e) => {
      const modal = document.getElementById('bookingModal');
      if (e.key === 'Escape' && modal && !modal.hidden) closeBookingModal();
    });
  }

  async function downloadPdf () {
    const btn = document.getElementById('btnDownloadPdf');
    const original = btn ? btn.innerHTML : '';
    if (btn) { btn.disabled = true; btn.innerHTML = '<span>Generant PDF…</span>'; }
    try {
      const payload = window._confData || buildPayload();
      const result  = window._confResult || lastResult;
      const res = await fetch('/api/download-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payload, result }),
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
      console.error('PDF download error:', err);
      if (btn) {
        btn.innerHTML = '<span>Ho sento, torna-ho a provar</span>';
        setTimeout(() => { btn.innerHTML = original; btn.disabled = false; }, 2500);
      }
    } finally {
      if (btn) { btn.disabled = false; btn.innerHTML = original; }
    }
  }

  // ═══════════════════════════════════════════════════════════
  // CHAT · floating assistant (DocsGPT via /api/chat-*)
  // While on a question step  → /api/chat-configurador
  // After the reveal          → /api/chat-pressupost
  // ═══════════════════════════════════════════════════════════
  const chat = {
    convId: null,
    busy: false,
    open: false,
    panel: null,
    fab: null,
    msgs: null,
    input: null,
    form: null,
    closeBtn: null,
    greet: null,
  };

  function chatStepNumber () {
    // Map the active stage to the legacy 1-4 step index expected by
    // /api/chat-configurador's context formatter.
    const stage = document.body.dataset.stage || 'estructura';
    return ({ estructura: 1, materials: 2, equipament: 3, lloc: 4, reveal: 4 })[stage] || 1;
  }

  function chatBuildConfigState () {
    // The chat backend reads `config_state` to know what the user has
    // already answered. We pass the live state verbatim.
    return {
      municipi:       state.municipi || '',
      m2:             state.m2 || 0,
      plantes:        state.plantes || '',
      num_banys:      state.num_banys || 0,
      num_habitacions: state.num_habitacions || 0,
      garatge:        state.garatge || '',
      m2_garatge:     state.m2_garatge || 0,
      m2_porxos:      state.m2_porxos || 0,
      tipus_coberta:  state.tipus_coberta || '',
      tipus_facana:   state.tipus_facana || '',
      tipus_paviment: state.tipus_paviment || '',
      nivell_bany:    state.nivell_bany || '',
    };
  }

  function chatAppendMsg (text, kind) {
    if (!chat.msgs) return;
    const el = document.createElement('div');
    el.className = `atelier-chat__msg atelier-chat__msg--${kind}`;
    el.textContent = text;
    chat.msgs.appendChild(el);
    chat.msgs.scrollTop = chat.msgs.scrollHeight;
    return el;
  }

  function chatAppendTyping () {
    if (!chat.msgs) return null;
    const el = document.createElement('div');
    el.className = 'atelier-chat__msg atelier-chat__msg--bot atelier-chat__typing';
    el.innerHTML = '<span></span><span></span><span></span>';
    chat.msgs.appendChild(el);
    chat.msgs.scrollTop = chat.msgs.scrollHeight;
    return el;
  }

  function chatSetBusy (busy) {
    chat.busy = busy;
    if (chat.input) chat.input.disabled = busy;
    if (chat.form)  chat.form.classList.toggle('atelier-chat__input-row--busy', busy);
  }

  // Apply form_updates returned by the chat backend to the live state and
  // re-render the current step if its key changed.
  // Catalog must mirror api/chat-pressupost.py sanitizer + state schema.
  const CHAT_INT_FIELDS = new Set(['m2', 'num_banys', 'num_habitacions', 'm2_garatge', 'm2_porxos']);
  const CHAT_CANONICAL_FIELDS = new Set([
    'm2', 'plantes', 'num_banys', 'num_habitacions',
    'garatge', 'm2_garatge', 'm2_porxos',
    'tipus_escala', 'tipus_coberta', 'tipus_facana', 'tipus_paviment',
    'nivell_bany',
    'plaques_solars', 'persianes', 'fan_coils', 'llar_foc',
    'membrana_rado', 'domotica',
    'energia_prioritat', 'climatitzacio', 'qualitat_aire', 'estil_acabats',
    'municipi',
  ]);

  // Pretty Catalan labels for the inline confirmation toast.
  const CHAT_FIELD_LABELS = {
    m2: 'superfície', plantes: 'plantes', num_banys: 'banys',
    num_habitacions: 'habitacions',
    garatge: 'garatge', m2_garatge: 'm² de garatge', m2_porxos: 'm² de pòrxos',
    tipus_escala: 'escala', tipus_coberta: 'coberta', tipus_facana: 'façana',
    tipus_paviment: 'paviment', nivell_bany: 'nivell de bany',
    plaques_solars: 'plaques solars', persianes: 'persianes',
    fan_coils: 'fan coils', llar_foc: 'llar de foc',
    membrana_rado: 'membrana radó', domotica: 'domòtica',
    energia_prioritat: 'prioritat energètica', climatitzacio: 'climatització',
    qualitat_aire: "qualitat de l'aire", estil_acabats: 'estil d\'acabats',
    municipi: 'municipi',
  };

  function chatApplyFormUpdates (updates) {
    if (!updates || typeof updates !== 'object') return [];
    const applied = [];
    let touchesCurrent = false;
    Object.keys(updates).forEach((k) => {
      if (!CHAT_CANONICAL_FIELDS.has(k)) return;
      let v = updates[k];
      if (CHAT_INT_FIELDS.has(k)) {
        v = parseInt(v, 10);
        if (isNaN(v)) return;
      }
      state[k] = v;
      applied.push(k);
      const stepKey = STEPS[currentIdx]?.stateKey;
      if (stepKey === k) touchesCurrent = true;
    });

    // Downstream consistency: if plantes drops to 1, force escala="no"; if it
    // rises above 1 and escala was "no", clear it so the user picks one
    // (or the chat sets it explicitly on the same turn).
    if ('plantes' in updates) {
      if (state.plantes === '1') state.tipus_escala = 'no';
      else if (state.tipus_escala === 'no') state.tipus_escala = '';
    }
    // If garatge becomes "no", zero out m² of garatge.
    if (updates.garatge === 'no') state.m2_garatge = 0;

    // Re-render current step if its field was touched
    if (touchesCurrent) renderStep(currentIdx);
    // Refresh summary
    updateSummary();
    return applied;
  }

  function chatFormatAppliedToast (applied) {
    if (!applied.length) return '';
    const parts = applied.map((k) => {
      const label = CHAT_FIELD_LABELS[k] || k;
      const v = state[k];
      if (k === 'm2' || k === 'm2_garatge' || k === 'm2_porxos') {
        return `${label}: ${fmtNum(v)} m²`;
      }
      if (k === 'num_banys') return `${label}: ${v}`;
      if (k === 'municipi') return `${label}: ${v}`;
      return `${label}: ${v}`;
    });
    return '✓ Actualitzat · ' + parts.join(' · ');
  }

  async function chatSend (text) {
    if (!text.trim() || chat.busy) return;
    chatAppendMsg(text.trim(), 'user');
    chat.input.value = '';
    chatSetBusy(true);
    const typing = chatAppendTyping();
    const usePost = !!lastResult;
    const endpoint = usePost ? '/api/chat-pressupost' : '/api/chat-configurador';
    const body = usePost
      ? {
          message: text.trim(),
          conversation_id: chat.convId,
          budget_input:  window._confData   || buildPayload(),
          budget_result: window._confResult || lastResult,
        }
      : {
          message: text.trim(),
          conversation_id: chat.convId,
          step: chatStepNumber(),
          config_state: chatBuildConfigState(),
        };
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      if (!res.ok || data.error) {
        chatAppendMsg(data?.error || 'Ho sento, no he pogut respondre ara mateix.', 'bot');
      } else {
        if (data.answer) chatAppendMsg(data.answer, 'bot');
        if (data.conversation_id) chat.convId = data.conversation_id;
        const applied = chatApplyFormUpdates(data.form_updates);
        if (applied.length) {
          chatAppendMsg('✓ He actualitzat: ' + applied.join(', ') + '. Revisa-ho al formulari.', 'bot-note');
        }
      }
    } catch (err) {
      if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
      chatAppendMsg("No he pogut connectar amb la guia ara mateix. Torna-ho a provar en uns segons.", 'bot');
    } finally {
      chatSetBusy(false);
      if (chat.input) chat.input.focus({ preventScroll: true });
    }
  }

  function chatToggle (open) {
    chat.open = open == null ? !chat.open : !!open;
    if (chat.panel) chat.panel.classList.toggle('atelier-chat--open', chat.open);
    if (chat.fab)   chat.fab.classList.toggle('atelier-fab--active', chat.open);
    document.body.classList.toggle('atelier-chat-open', chat.open);
    if (chat.open && chat.input) setTimeout(() => chat.input.focus({ preventScroll: true }), 320);
    // Dismiss greet bubble forever once user opens the panel
    if (chat.open && chat.greet && !chat.greet.hidden) {
      chat.greet.classList.add('atelier-chat-greet--hiding');
      setTimeout(() => { chat.greet.hidden = true; }, 280);
      try { sessionStorage.setItem('atelier_chat_greet', '1'); } catch (e) {}
    }
  }

  function chatInit () {
    chat.fab     = document.getElementById('chatFab');
    chat.panel   = document.getElementById('chatPanel');
    chat.msgs    = document.getElementById('chatMessages');
    chat.input   = document.getElementById('chatInput');
    chat.form    = document.getElementById('chatForm');
    chat.closeBtn= document.getElementById('chatClose');
    chat.greet   = document.getElementById('chatGreet');

    if (!chat.fab || !chat.panel) return;

    chat.fab.addEventListener('click', () => chatToggle());
    if (chat.closeBtn) chat.closeBtn.addEventListener('click', () => chatToggle(false));
    if (chat.form) chat.form.addEventListener('submit', (e) => {
      e.preventDefault();
      const v = chat.input ? chat.input.value : '';
      chatSend(v);
    });

    // Esc closes the panel
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && chat.open) chatToggle(false);
    });

    // Greet bubble: shows once per session ~4s after load if user hasn't
    // opened the chat. Goes away after 20s or on first interaction.
    let greetDismissed = false;
    try { greetDismissed = sessionStorage.getItem('atelier_chat_greet') === '1'; } catch (e) {}
    if (chat.greet && !greetDismissed) {
      setTimeout(() => {
        if (!chat.open) chat.greet.hidden = false;
      }, 3800);
      setTimeout(() => {
        if (chat.greet && !chat.greet.hidden) {
          chat.greet.classList.add('atelier-chat-greet--hiding');
          setTimeout(() => { chat.greet.hidden = true; }, 280);
        }
      }, 22000);
      chat.greet.addEventListener('click', (e) => {
        if (e.target.closest('.atelier-chat-greet__close')) return;
        chatToggle(true);
      });
      const greetClose = chat.greet.querySelector('.atelier-chat-greet__close');
      if (greetClose) greetClose.addEventListener('click', (e) => {
        e.stopPropagation();
        chat.greet.classList.add('atelier-chat-greet--hiding');
        setTimeout(() => { chat.greet.hidden = true; }, 280);
        try { sessionStorage.setItem('atelier_chat_greet', '1'); } catch (e) {}
      });
    }
  }

  // ── Boot
  function entryAnimation () {
    if (!window.gsap) return;
    const tl = window.gsap.timeline({ defaults: { ease: 'power3.out' } });
    tl.from('.atelier-bar',          { opacity: 0, y: -14, duration: 0.5 }, 0);
    tl.from('.atelier-stage__tags',  { opacity: 0, y: -8,  duration: 0.6 }, 0.15);
    tl.from('.atelier-stage__title', { opacity: 0, y: 24,  duration: 0.9 }, 0.25);
    tl.from('#stepContainer',        { opacity: 0, y: 32,  duration: 0.9 }, 0.4);
    tl.from('.atelier-footer',       { opacity: 0, y: 14,  duration: 0.55 }, 0.55);
    tl.from('.atelier-fab',          { opacity: 0, scale: 0.7, duration: 0.5, ease: 'back.out(1.7)' }, 1.1);
  }

  function init () {
    // Mark elements so we can diagnose mis-bindings via dev tools.
    if (btnNext) { btnNext.addEventListener('click', onNext); btnNext.dataset.bound = '1'; }
    if (btnBack) { btnBack.addEventListener('click', onBack); btnBack.dataset.bound = '1'; }
    renderStep(0);
    entryAnimation();
    chatInit();
    wireBookingModal();
    wirePlanta();
    if (typeof window !== 'undefined') {
      window.__atelierInit = { btnNextExists: !!btnNext, btnBackExists: !!btnBack, ts: Date.now() };
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
