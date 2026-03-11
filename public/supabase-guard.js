// ══════════════════════════════════════════════════════════════
// PAPik — Auth Guard for Dashboard Pages
// Include in every dashboard page AFTER supabase-auth.js:
//   <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
//   <script src="supabase-auth.js"></script>
//   <script src="supabase-guard.js"></script>
//
// Usage: set a data attribute on <body> to restrict access:
//   <body data-allowed-roles="secretario,admin">
// ══════════════════════════════════════════════════════════════

(async function guard() {
  console.log('PAPik Guard: starting...');

  try {
    // ─── Get or create Supabase client ───
    var client = null;
    var attempts = 0;
    var maxAttempts = 50; // 10 seconds max

    while (!client && attempts < maxAttempts) {
      // Try 1: Use shared client from supabase-auth.js
      if (window._papikClient) {
        client = window._papikClient;
        break;
      }
      // Try 2: Use initSupabase function from supabase-auth.js
      if (typeof initSupabase === 'function') {
        client = initSupabase();
        if (client) break;
      }
      // Try 3: Create our own client directly
      if (typeof window.supabase !== 'undefined' &&
          window.supabase !== null &&
          typeof window.supabase.createClient === 'function' &&
          window.PAPIK_SUPABASE_URL && window.PAPIK_SUPABASE_ANON_KEY) {
        client = window.supabase.createClient(
          window.PAPIK_SUPABASE_URL,
          window.PAPIK_SUPABASE_ANON_KEY
        );
        window._papikClient = client;
        break;
      }

      await new Promise(function(r) { setTimeout(r, 200); });
      attempts++;
    }

    if (!client) {
      console.error('PAPik Guard: Supabase client not available after ' + attempts + ' attempts');
      window.location.href = 'usuaris.html';
      return;
    }

    console.log('PAPik Guard: client ready, checking session...');

    // ─── Check session ───
    var sessionResult = await client.auth.getSession();
    var session = sessionResult.data.session;

    if (!session) {
      console.log('PAPik Guard: no session, redirecting to login');
      window.location.href = 'usuaris.html';
      return;
    }

    console.log('PAPik Guard: session found for ' + session.user.email);

    // ─── Get profile ───
    var profileResult = await client
      .from('profiles')
      .select('role, is_active, first_name, last_name')
      .eq('id', session.user.id)
      .single();

    var profile = profileResult.data;
    var profileError = profileResult.error;

    if (profileError) {
      console.error('PAPik Guard: profile query error:', profileError);
    }

    if (!profile || !profile.is_active) {
      console.log('PAPik Guard: profile missing or inactive, signing out');
      await client.auth.signOut();
      window.location.href = 'usuaris.html';
      return;
    }

    console.log('PAPik Guard: profile loaded, role=' + profile.role);

    // ─── Check role against allowed roles ───
    var allowedRoles = document.body.dataset.allowedRoles;
    if (allowedRoles) {
      var roles = allowedRoles.split(',').map(function(r) { return r.trim(); });
      if (!roles.includes(profile.role)) {
        var routes = window.PAPIK_DASHBOARD_ROUTES || {};
        console.log('PAPik Guard: role "' + profile.role + '" not in allowed roles, redirecting');
        window.location.href = routes[profile.role] || 'usuaris.html';
        return;
      }
    }

    // ─── Expose user info globally for dashboard scripts ───
    window.papikUser = {
      id: session.user.id,
      email: session.user.email,
      firstName: profile.first_name,
      lastName: profile.last_name,
      role: profile.role
    };

    console.log('PAPik Guard: user ready, dispatching event');

    // Dispatch event so dashboard scripts know the user is ready
    document.dispatchEvent(new CustomEvent('papik:user-ready', { detail: window.papikUser }));

  } catch (err) {
    console.error('PAPik Guard error:', err);
    window.location.href = 'usuaris.html';
  }
})();

// ─── Create User (for Secretario/Admin dashboard) ───
async function papikCreateUser(opts) {
  var client = window._papikClient;
  if (!client) throw new Error('No inicialitzat');
  var sessionResult = await client.auth.getSession();
  var session = sessionResult.data.session;
  if (!session) throw new Error('No autoritzat');

  var response = await fetch(
    window.PAPIK_SUPABASE_URL + '/functions/v1/create-user',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + session.access_token,
        'apikey': window.PAPIK_SUPABASE_ANON_KEY
      },
      body: JSON.stringify(opts)
    }
  );

  var result = await response.json();
  if (!response.ok) throw new Error(result.error);
  return result;
}

// ─── List Users (for admin dashboard) ───
async function papikListUsers() {
  var client = window._papikClient;
  if (!client) throw new Error('No inicialitzat');
  var result = await client
    .from('profiles')
    .select('id, first_name, last_name, role, phone, company, is_active, created_at')
    .order('created_at', { ascending: false });

  if (result.error) throw result.error;
  return result.data;
}

// ─── Toggle User Active Status (admin only) ───
async function papikToggleUserActive(userId, isActive) {
  var client = window._papikClient;
  if (!client) throw new Error('No inicialitzat');
  var result = await client
    .from('profiles')
    .update({ is_active: isActive })
    .eq('id', userId);

  if (result.error) throw result.error;
}
