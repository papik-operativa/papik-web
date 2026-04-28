/* ═══════════════════════════════════════════════════════════
   PAPIK · MOTION ENGINE — v2
   - data-anim with IntersectionObserver (fade-up/left/right/scale/in)
   - hero word-by-word reveal ([data-reveal-words])
   - cursor-following spotlight ([data-spotlight] / .card / .list-item)
   - header background on scroll (.header-top)
   - hero stagger (subtitle / actions)
   - animated counters ([data-count])
   - respects prefers-reduced-motion
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasIO = 'IntersectionObserver' in window;

  document.documentElement.classList.add('js-ready');

  /* ══════════════════ Reduced motion fallback ══════════════════ */
  if (reduced || !hasIO) {
    document.querySelectorAll('[data-anim]').forEach(function (el) {
      el.classList.add('is-visible');
    });
    document.querySelectorAll('[data-reveal-words]').forEach(function (el) {
      el.classList.add('is-revealed');
    });
    document.querySelectorAll('.hero__subtitle, .hero__actions').forEach(function (el) {
      el.classList.add('is-revealed');
    });
    return;
  }

  /* ══════════════════ Scroll reveal observer ══════════════════ */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-visible');
      io.unobserve(e.target);
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  function register(el) {
    var rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      // already in view: micro-delay to avoid flash
      setTimeout(function () { el.classList.add('is-visible'); }, 60);
    } else {
      io.observe(el);
    }
  }

  document.querySelectorAll('[data-anim]').forEach(register);

  /* Auto-mark common section structures */
  function autoMark(el, type, delay) {
    if (!el || el.hasAttribute('data-anim')) return;
    el.setAttribute('data-anim', type || 'fade-up');
    if (delay) el.style.transitionDelay = delay + 'ms';
    register(el);
  }

  document.querySelectorAll('section:not(.header-sticky):not(.hero) > .container > h2, section:not(.header-sticky):not(.hero) h2.section-header__title').forEach(function (el) {
    autoMark(el, 'fade-up');
  });
  document.querySelectorAll('section:not(.header-sticky):not(.hero) h2 + p, section:not(.header-sticky):not(.hero) h2 + .t16').forEach(function (el) {
    autoMark(el, 'fade-up', 80);
  });

  /* Stagger inside grids */
  ['.card-grid', '.stats-grid'].forEach(function (sel) {
    document.querySelectorAll(sel).forEach(function (container) {
      Array.from(container.children).forEach(function (child, i) {
        autoMark(child, 'fade-up', i * 80);
      });
    });
  });

  /* List items / steps */
  document.querySelectorAll('.list-item, .list-step').forEach(function (el, i) {
    autoMark(el, 'fade-up', Math.min(i, 5) * 60);
  });

  /* ══════════════════ Hero word-by-word reveal ══════════════════ */
  document.querySelectorAll('[data-reveal-words]').forEach(function (title) {
    if (title.dataset.revealDone === '1') return;
    var text = title.textContent.trim();
    title.innerHTML = text.split(/\s+/).map(function (word, i) {
      return '<span class="word" style="transition-delay:' + (i * 0.08) + 's">' + word + '</span>';
    }).join(' ');
    title.dataset.revealDone = '1';
    setTimeout(function () { title.classList.add('is-revealed'); }, 100);
  });

  /* Reveal subtitle and actions in any .hero, with stagger */
  document.querySelectorAll('.hero').forEach(function (hero) {
    var sub = hero.querySelector('.hero__subtitle');
    var act = hero.querySelector('.hero__actions');
    setTimeout(function () { if (sub) sub.classList.add('is-revealed'); }, 200);
    setTimeout(function () { if (act) act.classList.add('is-revealed'); }, 350);
  });

  /* ══════════════════ Cursor-following spotlight ══════════════════ */
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    function attachSpotlight(items, selector, radius, alpha) {
      items.forEach(function (item) {
        var hover = item.querySelector(selector);
        if (!hover) return;
        item.addEventListener('mousemove', function (e) {
          var rect = item.getBoundingClientRect();
          var x = e.clientX - rect.left;
          var y = e.clientY - rect.top;
          hover.style.background = 'radial-gradient(' + radius + 'px circle at ' + x + 'px ' + y + 'px, rgba(149,187,165,' + alpha + ') 0%, transparent 70%)';
        });
        item.addEventListener('mouseleave', function () { hover.style.background = ''; });
      });
    }

    attachSpotlight(document.querySelectorAll('.list-item'),       '.list-item__hover',       280, 0.10);
    attachSpotlight(document.querySelectorAll('.card'),            '.card__spotlight',        280, 0.12);
    attachSpotlight(document.querySelectorAll('.featured-card'),   '.featured-card__spotlight', 400, 0.12);
    attachSpotlight(document.querySelectorAll('.blog-list-item'),  '.blog-list-item__hover',  280, 0.10);
    attachSpotlight(document.querySelectorAll('.blog-grid-card'),  '.blog-grid-card__spotlight', 280, 0.12);
  }

  /* ══════════════════ Animated counters ══════════════════ */
  var cio = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      var el = e.target;
      var raw = el.dataset.raw || el.textContent.trim();
      el.dataset.raw = raw;
      var m = raw.match(/^([\d]+(?:[.,]\d+)?)(.*)$/);
      if (!m) { cio.unobserve(el); return; }
      var target = parseFloat(m[1].replace(',', '.'));
      var suffix = m[2] || '';
      var isInt = (m[1].indexOf('.') === -1 && m[1].indexOf(',') === -1);
      var dur = 1100, t0 = performance.now();
      (function step(now) {
        var p = Math.min((now - t0) / dur, 1);
        var v = target * (1 - Math.pow(1 - p, 3));
        el.textContent = (isInt ? Math.round(v) : v.toFixed(1)) + suffix;
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = raw;
      })(t0);
      cio.unobserve(el);
    });
  }, { threshold: 0.5 });

  // Only animate counters explicitly marked with data-count to avoid
  // mangling stats whose value contains text (e.g. "+30 anys", "4 mesos").
  document.querySelectorAll('[data-count]').forEach(function (el) {
    cio.observe(el);
  });

  /* ══════════════════ Header backdrop on scroll ══════════════════ */
  var hdr = document.querySelector('.header-top');
  if (hdr) {
    var _scrolled = false;
    window.addEventListener('scroll', function () {
      var s = window.scrollY > 60;
      if (s !== _scrolled) { hdr.classList.toggle('hdr-scrolled', s); _scrolled = s; }
    }, { passive: true });
  }

  /* ══════════════════ Header hide/show on scroll ══════════════════ */
  if (hdr) {
    var lastY = 0;
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      if (y > 80 && y > lastY) hdr.classList.add('hidden');
      else hdr.classList.remove('hidden');
      lastY = y;
    }, { passive: true });
  }
})();
