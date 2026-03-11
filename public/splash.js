/* ══════════════════════════════════════════════════════════════════
   PAPIK Group · Splash Screen v5
   ──────────────────────────────────────────────────────────────────
   Concepto: solo el logotipo.
   El logo aparece primero a gran escala como outline fantasma muy
   tenue (decorativo), mientras el logo principal se traza letra a
   letra encima y finalmente solidifica. Sin elementos externos.
   Duration: 3 000 ms
   ══════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* Uncomment for production:
  if (sessionStorage.getItem('papik_splash')) return;
  sessionStorage.setItem('papik_splash', '1');        */

  /* ── CSS ──────────────────────────────────────────────────────── */
  var S = document.createElement('style');
  S.textContent = ''
  + '#pks{'
  +   'position:fixed;inset:0;z-index:9999;background:#fff;'
  +   'display:flex;align-items:center;justify-content:center;'
  +   'overflow:hidden'
  + '}'

  /* Logo fantasma — fill tenue, SIN trazo (nunca compite con el drawing) */
  + '#pks-ghost{'
  +   'position:absolute;'
  +   'width:92vw;height:auto;'
  +   'opacity:0;transition:opacity .65s ease'
  + '}'
  + '#pks-ghost.on {opacity:.20}'
  + '#pks-ghost.off{opacity:0;transition-duration:.7s}'
  + '#pks-ghost path,#pks-ghost polygon{'
  +   'fill:#002819;stroke:none'
  + '}'

  /* Logo principal — tamaño normal, se traza y rellena */
  + '#pks-logo path,#pks-logo polygon{'
  +   'fill:none;stroke:#002819;stroke-width:.9;'
  +   'stroke-linejoin:round;opacity:0'
  + '}'
  + '#pks-logo.rdy path,#pks-logo.rdy polygon{opacity:1}'
  + '#pks-logo.solid path,#pks-logo.solid polygon{'
  +   'fill:#002819;stroke:none;opacity:1;'
  +   'transition:fill .44s cubic-bezier(.4,0,.2,1),opacity .1s ease'
  + '}'

  /* Salida */
  + '#pks.exit{'
  +   'opacity:0;pointer-events:none;'
  +   'transition:opacity .48s cubic-bezier(.4,0,.6,1)'
  + '}';

  document.head.appendChild(S);

  /* ── DOM helpers ──────────────────────────────────────────────── */
  function d(tag) { return document.createElement(tag); }
  function sv()   { return document.createElementNS('http://www.w3.org/2000/svg','svg'); }

  /* Root */
  var pks = d('div'); pks.id = 'pks'; pks.setAttribute('aria-hidden','true');

  /* Paths compartidos — mismo logotipo para ambas capas */
  var PATHS = ''
    + '<polygon points="184.4,302.8 184.4,256.8 184.4,232.2 158.2,232.2 158.2,364 184.4,364 184.4,327.7"/>'
    + '<path d="M208.9,232.2h-11.3v24.6h11.7c14.8,0,23.3,7.1,23.3,18.9c0,10.8-7.9,18.9-23.1,22l-11.9,2.4v25l11.7-2.3c34.3-7,49.9-24.7,49.9-48.2C259.2,248.9,239.4,232.2,208.9,232.2z"/>'
    + '<polygon points="318,232.2 290.1,232.2 236.4,364 264.5,364 272.2,344.4 315.7,336.7 306.8,314 282.4,318.2 303.9,262.8 343.5,364 371.7,364"/>'
    + '<polygon points="403.8,232.2 377.6,232.2 377.6,364 403.8,364 403.8,302.8"/>'
    + '<path d="M428.4,232.2H417v24.6h11.7c14.8,0,23.3,7.1,23.3,18.9c0,10.8-7.9,18.9-23.1,22l-11.9,2.4v25l11.7-2.3c34.3-7,49.9-24.7,49.9-48.2C478.6,248.9,458.8,232.2,428.4,232.2z"/>'
    + '<path d="M489.9,232.2h26.2V364h-26.2V232.2z"/>'
    + '<path d="M533.6,232.2h26.2V364h-26.2V232.2z"/>'
    + '<path d="M614.3,297.6c31.3-22.9,33.7-65.3,33.7-65.3h-26.2c0,0-1,34.1-27.1,49.2c0,0-5.5,3.4-10.1,5.4c-4.6,2.1-13.1,5.1-13.1,5.1v25.1l19.2-7.9l31.5,54.9h29.5L614.3,297.6z"/>'
    + '<path d="M659.7,243.4c0-7,5.2-12.1,12.2-12.1c7,0,12.2,5.1,12.2,12.1c0,7-5.2,12.1-12.2,12.1C664.9,255.5,659.7,250.3,659.7,243.4z M681.3,243.4c0-5.7-3.9-9.7-9.4-9.7c-5.6,0-9.4,4-9.4,9.7s3.9,9.7,9.4,9.7C677.5,253.1,681.3,249.1,681.3,243.4z M667.5,236.9h4.4c3.2,0,5,1.6,5,3.8c0,1.3-0.8,2.4-2.5,3.4l3.2,5.3h-2.9l-3.6-6l1.6-0.8c1.1-0.6,1.5-1.1,1.5-1.9c0-1.1-0.9-1.6-2.4-1.6H670v10.2h-2.6V236.9z"/>';

  /* Logo fantasma — fill sólido muy tenue (5%), ligeramente más grande */
  var ghost = sv(); ghost.id = 'pks-ghost';
  ghost.setAttribute('viewBox','155 228 535 140');
  /* tamaño controlado por CSS (92vw), sin fijar píxeles */
  ghost.setAttribute('shape-rendering','geometricPrecision');
  ghost.innerHTML = PATHS;
  pks.appendChild(ghost);

  /* Logo principal — tamaño normal, centrado */
  var logo = sv(); logo.id = 'pks-logo';
  logo.setAttribute('viewBox','155 228 535 140');
  logo.setAttribute('width', '292');
  logo.setAttribute('height', '77');
  logo.setAttribute('shape-rendering','geometricPrecision');
  logo.setAttribute('aria-label','PAPIK');
  logo.innerHTML = PATHS;
  pks.appendChild(logo);

  document.body.insertBefore(pks, document.body.firstChild);

  /* ── Prime stroke-dashoffset en logo principal ────────────────── */
  var lps = Array.from(logo.querySelectorAll('path,polygon'));
  lps.forEach(function (p) {
    var l = p.getTotalLength ? p.getTotalLength() : 400;
    p.style.strokeDasharray  = l;
    p.style.strokeDashoffset = l;
  });
  logo.classList.add('rdy');

  /* ── Timeline ────────────────────────────────────────────────────
     t=60      Logo fantasma aparece (outline tenue, 640px)
     t=200     Logo principal empieza a trazarse (P A P I K ® × 85ms)
                último trazo ≈ t=880ms
     t=980     Logo solidifica (fill #002819)
     t=1100    Logo fantasma desaparece
     t=2400    Splash fade-out
     t=2900    DOM eliminado
  ──────────────────────────────────────────────────────────────── */
  /* Fase 1 — fantasma (fill tenue): aparece solo, sin competencia */
  tick(60,  function () { ghost.classList.add('on'); });
  /* empieza a desvanecerse antes de que el trazo sea visible */
  tick(550, function () { ghost.classList.replace('on','off'); });

  /* Fase 2 — logo principal: empieza cuando el fantasma ya se va */
  lps.forEach(function (p, i) {
    tick(700 + i * 82, function () {
      p.style.transition       = 'stroke-dashoffset .17s cubic-bezier(.4,0,.2,1)';
      p.style.strokeDashoffset = '0';
    });
  });
  /* fantasma completamente invisible a t≈1250ms (700ms transición) */
  /* último trazo termina ≈ t=1436ms */

  /* Fase 3 — solidificar */
  tick(1500, function () { logo.classList.add('solid'); });

  /* Salida */
  tick(2400, function () { pks.classList.add('exit'); });
  tick(2900, function () { pks.parentNode && pks.parentNode.removeChild(pks); });

  function tick(ms, fn) { setTimeout(fn, ms); }

})();
