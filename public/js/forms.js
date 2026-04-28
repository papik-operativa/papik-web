/* ════════════════════════════════════════════════════════════════
   PAPIK · Forms (frontend skeleton)
   - Validates required fields, email/phone formats
   - Inline error display
   - Posts JSON to /api/forms/<name> (backend NOT implemented yet)
   - GDPR consent checkbox required (RGPD Art. 7)
   - Honeypot anti-spam field
   - i18n strings (CA/ES/EN) auto-detected from <html lang>
════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  /* ── i18n ────────────────────────────────────────────────────── */
  var I18N = {
    ca: {
      required: 'Aquest camp és obligatori.',
      email: 'Introdueix un correu electrònic vàlid.',
      phone: 'Introdueix un telèfon vàlid.',
      consent: 'Has d\'acceptar la política de privacitat.',
      success: 'Hem rebut la teva sol·licitud. Et respondrem aviat.',
      error: 'No s\'ha pogut enviar el formulari. Torna-ho a provar.',
      sending: 'Enviant…'
    },
    es: {
      required: 'Este campo es obligatorio.',
      email: 'Introduce un correo electrónico válido.',
      phone: 'Introduce un teléfono válido.',
      consent: 'Debes aceptar la política de privacidad.',
      success: 'Hemos recibido tu solicitud. Te responderemos pronto.',
      error: 'No se ha podido enviar el formulario. Inténtalo de nuevo.',
      sending: 'Enviando…'
    },
    en: {
      required: 'This field is required.',
      email: 'Please enter a valid email address.',
      phone: 'Please enter a valid phone number.',
      consent: 'You must accept the privacy policy.',
      success: 'We have received your request. We will reply soon.',
      error: 'The form could not be submitted. Please try again.',
      sending: 'Sending…'
    }
  };

  function detectLang() {
    var html = (document.documentElement.getAttribute('lang') || '').toLowerCase().slice(0, 2);
    if (I18N[html]) return html;
    var path = location.pathname || '';
    if (path.indexOf('/es/') === 0) return 'es';
    if (path.indexOf('/en/') === 0) return 'en';
    return 'ca';
  }

  var LANG = detectLang();
  var T = I18N[LANG];

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var PHONE_RE = /^[+()\d\s.\-]{7,20}$/;

  /* ── Helpers ─────────────────────────────────────────────────── */
  function setError(field, msg) {
    clearError(field);
    var err = document.createElement('p');
    err.className = 'papik-form__error';
    err.id = 'err-' + (field.id || field.name || Math.random().toString(36).slice(2, 7));
    err.setAttribute('role', 'alert');
    err.textContent = msg;
    field.setAttribute('aria-invalid', 'true');
    field.setAttribute('aria-describedby', err.id);
    field.classList.add('is-invalid');
    var anchor = field.closest('label') || field.parentNode;
    anchor.appendChild(err);
  }

  function clearError(field) {
    field.removeAttribute('aria-invalid');
    field.classList.remove('is-invalid');
    var describedBy = field.getAttribute('aria-describedby');
    if (describedBy) {
      var existing = document.getElementById(describedBy);
      if (existing && existing.classList.contains('papik-form__error')) existing.remove();
      field.removeAttribute('aria-describedby');
    }
  }

  function showFormStatus(form, msg, kind) {
    var status = form.querySelector('.papik-form__status');
    if (!status) {
      status = document.createElement('div');
      status.className = 'papik-form__status';
      status.setAttribute('role', kind === 'error' ? 'alert' : 'status');
      form.insertBefore(status, form.firstChild);
    }
    status.dataset.kind = kind || 'info';
    status.textContent = msg;
  }

  function validate(form, schema) {
    var ok = true;
    schema.forEach(function (rule) {
      var field = form.querySelector('[name="' + rule.name + '"]');
      if (!field) return;
      clearError(field);
      var value = (field.type === 'checkbox') ? field.checked : (field.value || '').trim();
      if (rule.required) {
        if (rule.type === 'consent' && value !== true) { setError(field, T.consent); ok = false; return; }
        if (!value) { setError(field, T.required); ok = false; return; }
      }
      if (!value) return;
      if (rule.type === 'email' && !EMAIL_RE.test(value)) { setError(field, T.email); ok = false; }
      if (rule.type === 'phone' && !PHONE_RE.test(value)) { setError(field, T.phone); ok = false; }
    });
    return ok;
  }

  function honeypotTriggered(form) {
    var hp = form.querySelector('[name="company_website"]');
    return hp && hp.value && hp.value.length > 0;
  }

  function serialize(form) {
    var data = {};
    var fd = new FormData(form);
    fd.forEach(function (v, k) { data[k] = v; });
    var consent = form.querySelector('[name="gdpr_consent"]');
    data.gdpr_consent = !!(consent && consent.checked);
    data.lang = LANG;
    delete data.company_website; // never forward honeypot
    return data;
  }

  function bindForm(form, opts) {
    if (!form || form.dataset.papikBound === '1') return;
    form.dataset.papikBound = '1';
    form.setAttribute('novalidate', 'novalidate');

    // Inject honeypot if missing
    if (!form.querySelector('[name="company_website"]')) {
      var hp = document.createElement('div');
      hp.setAttribute('aria-hidden', 'true');
      hp.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden;';
      hp.innerHTML = '<label>Website <input type="text" name="company_website" tabindex="-1" autocomplete="off"></label>';
      form.appendChild(hp);
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (honeypotTriggered(form)) return; // silently drop bots
      if (!validate(form, opts.schema)) return;

      var btn = form.querySelector('button[type="submit"], input[type="submit"]');
      var origLabel = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = T.sending; }

      var payload = serialize(form);
      payload._form = opts.name;

      fetch('/api/forms/' + opts.name, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.json().catch(function () { return {}; });
        })
        .then(function () {
          form.style.display = 'none';
          var success = document.createElement('div');
          success.className = 'papik-form__success';
          success.setAttribute('role', 'status');
          success.textContent = T.success;
          form.parentNode.insertBefore(success, form);
        })
        .catch(function () {
          if (btn) { btn.disabled = false; btn.textContent = origLabel; }
          showFormStatus(form, T.error, 'error');
        });
    });

    // Live-clear errors as the user fixes them
    form.addEventListener('input', function (e) {
      if (e.target.matches('input, textarea, select')) clearError(e.target);
    });
  }

  /* ── Schemas ─────────────────────────────────────────────────── */
  var SCHEMAS = {
    newsletter: [
      { name: 'email', required: true, type: 'email' },
      { name: 'gdpr_consent', required: true, type: 'consent' }
    ],
    contact: [
      { name: 'name', required: true },
      { name: 'email', required: true, type: 'email' },
      { name: 'phone', required: false, type: 'phone' },
      { name: 'message', required: true },
      { name: 'gdpr_consent', required: true, type: 'consent' }
    ],
    'presupuesto-lite': [
      { name: 'name', required: true },
      { name: 'email', required: true, type: 'email' },
      { name: 'phone', required: true, type: 'phone' },
      { name: 'project_type', required: true },
      { name: 'description', required: true },
      { name: 'gdpr_consent', required: true, type: 'consent' }
    ]
  };

  function init() {
    var pairs = [
      ['#newsletter-form', 'newsletter'],
      ['#contact-form', 'contact'],
      ['#presupuesto-lite-form', 'presupuesto-lite'],
      ['#presupost-form', 'presupuesto-lite'],
      ['#budget-form', 'presupuesto-lite']
    ];
    pairs.forEach(function (pair) {
      document.querySelectorAll(pair[0]).forEach(function (form) {
        bindForm(form, { name: pair[1], schema: SCHEMAS[pair[1]] });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
