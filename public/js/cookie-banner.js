/* ════════════════════════════════════════════════════════════════
   PAPIK · Cookie Consent Banner (AEPD / RGPD compliant)
   - First-visit banner, equal-weight Accept / Reject / Configure
   - Granular categories + persistent localStorage
   - Re-display on version bump
   - Footer "Cookies" link to re-open at any time
   - GTM dataLayer push for downstream analytics gates
════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var STORAGE_KEY = 'papik_cookie_consent';
  var CONSENT_VERSION = '1.0';

  /* ── i18n strings ────────────────────────────────────────────── */
  var I18N = {
    ca: {
      title: 'Aquesta web utilitza galetes',
      body: 'Utilitzem galetes pròpies i de tercers per analitzar el nostre servei i mostrar-te publicitat relacionada amb les teves preferències. Pots acceptar-les totes, rebutjar-les totes o configurar-les. Més informació a la nostra <a href="/politica-cookies.html">Política de galetes</a>.',
      acceptAll: 'Acceptar tot',
      rejectAll: 'Rebutjar tot',
      configure: 'Configurar',
      modalTitle: 'Configuració de galetes',
      save: 'Desar preferències',
      close: 'Tancar',
      catTechnical: 'Tècniques (sempre actives)',
      catTechnicalDesc: 'Imprescindibles perquè la web funcioni. No es poden desactivar.',
      catPreferences: 'Preferències',
      catPreferencesDesc: 'Recorden la teva configuració (idioma, regió) per millorar la teva experiència.',
      catAnalytics: 'Analítiques',
      catAnalyticsDesc: 'Ens permeten mesurar el trànsit i entendre com s\'utilitza la web (Google Analytics).',
      catAdvertising: 'Publicitàries',
      catAdvertisingDesc: 'Permeten mostrar-te anuncis personalitzats segons els teus interessos.',
      footerLink: 'Galetes'
    },
    es: {
      title: 'Esta web utiliza cookies',
      body: 'Utilizamos cookies propias y de terceros para analizar nuestro servicio y mostrarte publicidad relacionada con tus preferencias. Puedes aceptarlas todas, rechazarlas todas o configurarlas. Más información en nuestra <a href="/es/politica-cookies.html">Política de cookies</a>.',
      acceptAll: 'Aceptar todo',
      rejectAll: 'Rechazar todo',
      configure: 'Configurar',
      modalTitle: 'Configuración de cookies',
      save: 'Guardar preferencias',
      close: 'Cerrar',
      catTechnical: 'Técnicas (siempre activas)',
      catTechnicalDesc: 'Imprescindibles para que la web funcione. No pueden desactivarse.',
      catPreferences: 'Preferencias',
      catPreferencesDesc: 'Recuerdan tu configuración (idioma, región) para mejorar tu experiencia.',
      catAnalytics: 'Analíticas',
      catAnalyticsDesc: 'Nos permiten medir el tráfico y entender cómo se usa la web (Google Analytics).',
      catAdvertising: 'Publicitarias',
      catAdvertisingDesc: 'Permiten mostrarte anuncios personalizados según tus intereses.',
      footerLink: 'Cookies'
    },
    en: {
      title: 'This site uses cookies',
      body: 'We use our own and third-party cookies to analyse our service and to show you advertising related to your preferences. You can accept all, reject all or configure them. More info in our <a href="/en/cookie-policy.html">Cookie Policy</a>.',
      acceptAll: 'Accept all',
      rejectAll: 'Reject all',
      configure: 'Configure',
      modalTitle: 'Cookie settings',
      save: 'Save preferences',
      close: 'Close',
      catTechnical: 'Technical (always on)',
      catTechnicalDesc: 'Required for the site to work. Cannot be disabled.',
      catPreferences: 'Preferences',
      catPreferencesDesc: 'Remember your settings (language, region) to improve your experience.',
      catAnalytics: 'Analytics',
      catAnalyticsDesc: 'Help us measure traffic and understand how the site is used (Google Analytics).',
      catAdvertising: 'Advertising',
      catAdvertisingDesc: 'Allow us to show you personalised ads based on your interests.',
      footerLink: 'Cookies'
    }
  };

  /* ── Utilities ───────────────────────────────────────────────── */
  function detectLang() {
    var html = document.documentElement.getAttribute('lang') || '';
    var l = html.toLowerCase().slice(0, 2);
    if (I18N[l]) return l;
    var path = window.location.pathname || '';
    if (path.indexOf('/es/') === 0) return 'es';
    if (path.indexOf('/en/') === 0) return 'en';
    return 'ca';
  }

  function readConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (!parsed || parsed.version !== CONSENT_VERSION) return null;
      return parsed;
    } catch (e) { return null; }
  }

  function writeConsent(categories) {
    var payload = {
      categories: categories,
      timestamp: new Date().toISOString(),
      version: CONSENT_VERSION
    };
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(payload)); } catch (e) {}
    pushDataLayer(payload);
    return payload;
  }

  function pushDataLayer(payload) {
    if (typeof window === 'undefined') return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: 'cookie_consent_update',
      consent: payload
    });
  }

  /* ── Focus trap ──────────────────────────────────────────────── */
  function trapFocus(container, onEsc) {
    var focusable = container.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) return function () {};
    var first = focusable[0];
    var last = focusable[focusable.length - 1];
    function handler(e) {
      if (e.key === 'Escape') { e.preventDefault(); onEsc(); return; }
      if (e.key !== 'Tab') return;
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault(); last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault(); first.focus();
      }
    }
    container.addEventListener('keydown', handler);
    setTimeout(function () { first.focus(); }, 30);
    return function () { container.removeEventListener('keydown', handler); };
  }

  /* ── Banner & modal rendering ────────────────────────────────── */
  var lang = detectLang();
  var t = I18N[lang];
  var releaseFocus = null;
  var lastFocused = null;

  function $(sel, root) { return (root || document).querySelector(sel); }

  function showBanner() {
    var banner = $('#papik-cc-banner');
    if (banner) banner.hidden = false;
  }
  function hideBanner() {
    var banner = $('#papik-cc-banner');
    if (banner) banner.hidden = true;
  }

  function openModal() {
    lastFocused = document.activeElement;
    var existing = readConsent();
    var cats = existing ? existing.categories : { technical: true, preferences: false, analytics: false, advertising: false };
    var modal = $('#papik-cc-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'papik-cc-modal';
      modal.className = 'papik-cc-modal';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-labelledby', 'papik-cc-modal-title');
      modal.innerHTML =
        '<div class="papik-cc-modal__backdrop" data-cc-close></div>' +
        '<div class="papik-cc-modal__panel">' +
          '<button type="button" class="papik-cc-modal__close" data-cc-close aria-label="' + t.close + '">&times;</button>' +
          '<h2 id="papik-cc-modal-title" class="papik-cc-modal__title">' + t.modalTitle + '</h2>' +
          '<ul class="papik-cc-cats">' +
            cat('technical', t.catTechnical, t.catTechnicalDesc, true, true) +
            cat('preferences', t.catPreferences, t.catPreferencesDesc, !!cats.preferences, false) +
            cat('analytics', t.catAnalytics, t.catAnalyticsDesc, !!cats.analytics, false) +
            cat('advertising', t.catAdvertising, t.catAdvertisingDesc, !!cats.advertising, false) +
          '</ul>' +
          '<div class="papik-cc-modal__actions">' +
            '<button type="button" class="papik-cc-btn papik-cc-btn--ghost" data-cc-action="reject">' + t.rejectAll + '</button>' +
            '<button type="button" class="papik-cc-btn papik-cc-btn--ghost" data-cc-action="accept">' + t.acceptAll + '</button>' +
            '<button type="button" class="papik-cc-btn papik-cc-btn--primary" data-cc-action="save">' + t.save + '</button>' +
          '</div>' +
        '</div>';
      document.body.appendChild(modal);
      modal.addEventListener('click', function (e) {
        var act = e.target.getAttribute('data-cc-action');
        if (e.target.hasAttribute('data-cc-close')) closeModal();
        else if (act === 'accept') decideAll(true);
        else if (act === 'reject') decideAll(false);
        else if (act === 'save') saveFromModal();
      });
    }
    modal.hidden = false;
    document.body.classList.add('papik-cc-no-scroll');
    releaseFocus = trapFocus(modal, closeModal);
  }

  function cat(key, label, desc, checked, locked) {
    return '<li class="papik-cc-cat">' +
      '<div class="papik-cc-cat__head">' +
        '<span class="papik-cc-cat__label">' + label + '</span>' +
        '<label class="papik-cc-toggle">' +
          '<input type="checkbox" data-cc-cat="' + key + '"' +
            (checked ? ' checked' : '') + (locked ? ' disabled' : '') + '>' +
          '<span class="papik-cc-toggle__track"></span>' +
        '</label>' +
      '</div>' +
      '<p class="papik-cc-cat__desc">' + desc + '</p>' +
    '</li>';
  }

  function closeModal() {
    var modal = $('#papik-cc-modal');
    if (modal) modal.hidden = true;
    document.body.classList.remove('papik-cc-no-scroll');
    if (typeof releaseFocus === 'function') releaseFocus();
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  function decideAll(value) {
    writeConsent({ technical: true, preferences: value, analytics: value, advertising: value });
    closeModal();
    hideBanner();
  }

  function saveFromModal() {
    var modal = $('#papik-cc-modal');
    var inputs = modal.querySelectorAll('input[data-cc-cat]');
    var cats = { technical: true, preferences: false, analytics: false, advertising: false };
    inputs.forEach(function (el) { cats[el.getAttribute('data-cc-cat')] = !!el.checked; });
    cats.technical = true;
    writeConsent(cats);
    closeModal();
    hideBanner();
  }

  /* ── Banner wiring ───────────────────────────────────────────── */
  function init() {
    var banner = $('#papik-cc-banner');
    if (banner) {
      // Localise text (the static HTML uses CA defaults).
      var titleEl = banner.querySelector('[data-cc-text="title"]');
      var bodyEl = banner.querySelector('[data-cc-text="body"]');
      var btnA = banner.querySelector('[data-cc-action="accept"]');
      var btnR = banner.querySelector('[data-cc-action="reject"]');
      var btnC = banner.querySelector('[data-cc-action="configure"]');
      if (titleEl) titleEl.textContent = t.title;
      if (bodyEl) bodyEl.innerHTML = t.body;
      if (btnA) btnA.textContent = t.acceptAll;
      if (btnR) btnR.textContent = t.rejectAll;
      if (btnC) btnC.textContent = t.configure;

      banner.addEventListener('click', function (e) {
        var act = e.target.getAttribute('data-cc-action');
        if (act === 'accept') decideAll(true);
        else if (act === 'reject') decideAll(false);
        else if (act === 'configure') openModal();
      });
    }

    // Footer "Cookies" link — re-open settings any time.
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest && e.target.closest('[data-cc-open]');
      if (trigger) { e.preventDefault(); openModal(); }
    });

    var existing = readConsent();
    if (!existing) {
      showBanner();
    } else {
      pushDataLayer(existing);
      hideBanner();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Public API
  window.PapikCookieConsent = {
    open: openModal,
    get: readConsent,
    reset: function () { try { localStorage.removeItem(STORAGE_KEY); } catch (e) {} showBanner(); }
  };
})();
