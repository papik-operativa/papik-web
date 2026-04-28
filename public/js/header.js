/* ═══════════════════════════════════════════════════════════
   PAPIK · HEADER BEHAVIOR
   Submenus open/close, mobile nav overlay, search expand.
═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var fadeBg = document.getElementById('fadeBg');
  var headerSticky = document.getElementById('headerSticky');
  var mobileNav = document.getElementById('mobileNav');
  var burgerBtn = document.getElementById('burgerBtn');
  var mobileNavClose = document.getElementById('mobileNavClose');
  var searchTrigger = document.getElementById('searchTrigger');
  var searchClose = document.getElementById('searchClose');

  var activeSubmenu = null;

  function openSubmenu(id) {
    closeAllSubmenus();
    var sub = document.getElementById('sub-' + id);
    if (sub) {
      sub.classList.add('submenu-open');
      document.body.classList.add('submenu-open');
      activeSubmenu = id;
    }
  }
  function closeAllSubmenus() {
    document.querySelectorAll('.submenu').forEach(function (s) { s.classList.remove('submenu-open'); });
    if (mobileNav && !mobileNav.classList.contains('open')) {
      document.body.classList.remove('submenu-open');
    } else if (!mobileNav) {
      document.body.classList.remove('submenu-open');
    }
    activeSubmenu = null;
  }

  document.querySelectorAll('.menu-btn[data-menu]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var id = btn.dataset.menu;
      if (activeSubmenu === id) closeAllSubmenus();
      else openSubmenu(id);
    });
  });

  if (fadeBg) fadeBg.addEventListener('click', function () {
    closeAllSubmenus();
    closeMobileNav();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeAllSubmenus(); closeMobileNav(); }
  });

  /* Search */
  if (searchTrigger && headerSticky) {
    searchTrigger.addEventListener('click', function () {
      headerSticky.classList.add('search-open');
      closeAllSubmenus();
      setTimeout(function () {
        var inp = document.querySelector('.form-search__content input');
        if (inp) inp.focus();
      }, 200);
    });
  }
  if (searchClose && headerSticky) {
    searchClose.addEventListener('click', function () {
      headerSticky.classList.remove('search-open');
    });
  }

  /* Mobile nav */
  function closeMobileNav() {
    if (!mobileNav) return;
    mobileNav.classList.remove('open');
    document.body.style.overflow = '';
    if (fadeBg) fadeBg.style.zIndex = '70';
    document.body.classList.remove('submenu-open');
  }

  if (burgerBtn && mobileNav) {
    burgerBtn.addEventListener('click', function () {
      mobileNav.classList.add('open');
      document.body.style.overflow = 'hidden';
      if (fadeBg) fadeBg.style.zIndex = '190';
      document.body.classList.add('submenu-open');
    });
  }
  if (mobileNavClose) mobileNavClose.addEventListener('click', closeMobileNav);
  if (mobileNav) mobileNav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', closeMobileNav);
  });
})();
