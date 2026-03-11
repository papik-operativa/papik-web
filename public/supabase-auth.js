// ══════════════════════════════════════════════════════════════
// PAPik — Supabase Authentication
// Include in usuaris.html BEFORE the closing </body>:
//   <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
//   <script src="supabase-auth.js"></script>
// ══════════════════════════════════════════════════════════════

// ─── Config (on window so guard.js can access them) ───
window.PAPIK_SUPABASE_URL = 'https://ubjsiqmtusnkfmhgfgkm.supabase.co';
window.PAPIK_SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVianNpcW10dXNua2ZtaGdmZ2ttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5NzM0NTAsImV4cCI6MjA4ODU0OTQ1MH0.E4bBxaVN3925C2Ugu3gUfo0Z3hhrq-esQwll029MQNM';

// ─── Dashboard routes by role ───
window.PAPIK_DASHBOARD_ROUTES = {
  cliente:    'dashboard-cliente.html',
  arquitecto: 'dashboard-arquitecto.html',
  empleado:   'dashboard-empleado.html',
  secretario: 'dashboard-secretario.html',
  admin:      'dashboard-admin.html'
};

// Shortcuts for this file
var SUPABASE_URL = window.PAPIK_SUPABASE_URL;
var SUPABASE_ANON_KEY = window.PAPIK_SUPABASE_ANON_KEY;
var DASHBOARD_ROUTES = window.PAPIK_DASHBOARD_ROUTES;

// ══════════════════════════════════════════════
// STEP 1: Intercept forms IMMEDIATELY (before Supabase loads)
// This prevents the native POST on all browsers
// ══════════════════════════════════════════════

var loginForm = document.getElementById('form-login');
var registerForm = document.getElementById('form-register');

if (loginForm) {
  loginForm.addEventListener('submit', function(e) {
    e.preventDefault();
    e.stopPropagation();
    handleLogin();
  });
}

if (registerForm) {
  registerForm.addEventListener('submit', function(e) {
    e.preventDefault();
    e.stopPropagation();
    showFormMessage(
      registerForm,
      'La creació de comptes està restringida. Contacta amb PAPIK per obtenir accés.',
      'error'
    );
  });
}

// ══════════════════════════════════════════════
// STEP 2: Initialize Supabase client
// Store on window to share across scripts safely
// ══════════════════════════════════════════════

window._papikClient = null;

function initSupabase() {
  if (window._papikClient) return window._papikClient;
  // The CDN puts createClient on window.supabase
  if (typeof window.supabase !== 'undefined' &&
      window.supabase !== null &&
      typeof window.supabase.createClient === 'function') {
    window._papikClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    console.log('PAPik: Supabase client initialized');
    return window._papikClient;
  }
  return null;
}

// Try init immediately (SDK may already be loaded)
initSupabase();

// Also try after a short delay if SDK is loading
if (!window._papikClient) {
  setTimeout(initSupabase, 500);
  setTimeout(initSupabase, 1500);
}

// ══════════════════════════════════════════════
// STEP 3: Check if already logged in
// ══════════════════════════════════════════════

(async function checkSession() {
  // Only redirect from login page — skip on dashboard pages
  if (!window.location.pathname.includes('usuaris.html') &&
      !window.location.pathname.endsWith('/')) return;

  // Wait for Supabase to be ready
  var attempts = 0;
  while (!initSupabase() && attempts < 20) {
    await new Promise(function(r) { setTimeout(r, 200); });
    attempts++;
  }
  if (!window._papikClient) return;

  try {
    var sessionResult = await window._papikClient.auth.getSession();
    var session = sessionResult.data.session;
    if (session) {
      var profileResult = await window._papikClient
        .from('profiles')
        .select('role, is_active')
        .eq('id', session.user.id)
        .single();

      var profile = profileResult.data;
      if (profile && profile.is_active) {
        window.location.href = DASHBOARD_ROUTES[profile.role] || 'dashboard-cliente.html';
      }
    }
  } catch (err) {
    console.warn('PAPik: session check error', err);
  }
})();

// ══════════════════════════════════════════════
// STEP 4: Login handler
// ══════════════════════════════════════════════

async function handleLogin() {
  // Ensure Supabase is ready
  if (!initSupabase()) {
    showFormMessage(loginForm, 'Carregant... torna-ho a provar en un moment.', 'error');
    return;
  }

  var email = document.getElementById('login-email').value.trim();
  var password = document.getElementById('login-pass').value;
  var submitBtn = loginForm.querySelector('.form-submit');

  if (!email || !password) {
    showFormMessage(loginForm, 'Introdueix el correu i la contrasenya.', 'error');
    return;
  }

  // Disable button while processing
  submitBtn.disabled = true;
  submitBtn.style.opacity = '0.6';

  try {
    var loginResult = await window._papikClient.auth.signInWithPassword({
      email: email,
      password: password
    });

    if (loginResult.error) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = '1';
      showFormMessage(loginForm, translateAuthError(loginResult.error.message), 'error');
      return;
    }

    // Get user profile with role
    var profileResult = await window._papikClient
      .from('profiles')
      .select('role, is_active, first_name')
      .eq('id', loginResult.data.user.id)
      .single();

    if (profileResult.error || !profileResult.data) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = '1';
      showFormMessage(loginForm, 'Error carregant el perfil. Contacta amb suport.', 'error');
      return;
    }

    var profile = profileResult.data;

    if (!profile.is_active) {
      await window._papikClient.auth.signOut();
      submitBtn.disabled = false;
      submitBtn.style.opacity = '1';
      showFormMessage(loginForm, 'El teu compte està desactivat. Contacta amb PAPIK.', 'error');
      return;
    }

    // Redirect to role-specific dashboard
    showFormMessage(loginForm, 'Benvingut, ' + (profile.first_name || email) + '!', 'success');
    setTimeout(function() {
      window.location.href = DASHBOARD_ROUTES[profile.role] || 'dashboard-cliente.html';
    }, 800);

  } catch (err) {
    submitBtn.disabled = false;
    submitBtn.style.opacity = '1';
    showFormMessage(loginForm, 'Error de connexió. Torna-ho a provar.', 'error');
  }
}

// ══════════════════════════════════════════════
// UI Helpers
// ══════════════════════════════════════════════

function showFormMessage(form, message, type) {
  var existing = form.querySelector('.form-message');
  if (existing) existing.remove();

  var div = document.createElement('div');
  div.className = 'form-message';
  div.textContent = message;
  div.style.cssText =
    'padding: 12px 16px; margin-bottom: 16px; border-radius: 6px; font-size: 13px; line-height: 1.5; ' +
    (type === 'error'
      ? 'background: #fef2f2; color: #991b1b; border: 1px solid #fecaca;'
      : 'background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0;');
  form.insertBefore(div, form.firstChild);
  setTimeout(function() { if (div.parentNode) div.remove(); }, 6000);
}

function translateAuthError(msg) {
  var errors = {
    'Invalid login credentials': 'Correu o contrasenya incorrectes.',
    'Email not confirmed': 'El correu electrònic no ha estat confirmat.',
    'User not found': "No s'ha trobat cap compte amb aquest correu.",
    'Too many requests': 'Massa intents. Espera uns minuts i torna-ho a provar.',
    'User already registered': 'Aquest correu ja està registrat.',
  };
  return errors[msg] || "Error d'autenticació. Torna-ho a provar.";
}

// ─── Logout utility (call from dashboard pages) ───
async function papikLogout() {
  if (window._papikClient) {
    await window._papikClient.auth.signOut();
  }
  window.location.href = 'usuaris.html';
}

// ─── Get current user info (for dashboard pages) ───
async function papikGetCurrentUser() {
  if (!window._papikClient && !initSupabase()) return null;
  var sessionResult = await window._papikClient.auth.getSession();
  var session = sessionResult.data.session;
  if (!session) return null;

  var profileResult = await window._papikClient
    .from('profiles')
    .select('*')
    .eq('id', session.user.id)
    .single();

  return { id: session.user.id, email: session.user.email, ...profileResult.data };
}

// ─── Auth state change listener ───
(function setupAuthListener() {
  if (!initSupabase()) {
    setTimeout(setupAuthListener, 500);
    return;
  }
  window._papikClient.auth.onAuthStateChange(function(event, session) {
    if (event === 'SIGNED_OUT') {
      if (!window.location.pathname.includes('usuaris.html')) {
        window.location.href = 'usuaris.html';
      }
    }
  });
})();
