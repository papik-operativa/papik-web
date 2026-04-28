// ══════════════════════════════════════════════════════════════
// PAPik — Dashboard Auth Guard
// Include in ALL dashboard pages AFTER the Supabase CDN:
//   <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
//   <script src="dashboard-guard.js"></script>
// ══════════════════════════════════════════════════════════════

(async function dashboardGuard() {
  'use strict';

  // ─── Config (same as supabase-auth.js) ───
  var SB_URL  = 'https://ubjsiqmtusnkfmhgfgkm.supabase.co';
  var SB_KEY  = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVianNpcW10dXNua2ZtaGdmZ2ttIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI5NzM0NTAsImV4cCI6MjA4ODU0OTQ1MH0.E4bBxaVN3925C2Ugu3gUfo0Z3hhrq-esQwll029MQNM';

  // ─── Initialize Supabase client ───
  if (!window._papikClient) {
    var attempts = 0;
    while (typeof window.supabase === 'undefined' && attempts < 30) {
      await new Promise(function(r) { setTimeout(r, 150); });
      attempts++;
    }
    if (typeof window.supabase !== 'undefined' && window.supabase.createClient) {
      window._papikClient = window.supabase.createClient(SB_URL, SB_KEY);
    }
  }

  // ─── Detect language from path ───
  var isES = window.location.pathname.indexOf('/es/') !== -1;
  var loginPage = isES ? 'usuaris.html' : 'usuaris.html';

  if (!window._papikClient) {
    console.error('PAPik Guard: Supabase SDK not available');
    window.location.href = loginPage;
    return;
  }

  var sb = window._papikClient;

  // ─── Check session ───
  var sessionResult = await sb.auth.getSession();
  var session = sessionResult.data.session;

  if (!session) {
    window.location.href = loginPage;
    return;
  }

  // ─── Fetch profile ───
  var profileResult = await sb
    .from('profiles')
    .select('*')
    .eq('id', session.user.id)
    .single();

  var profile = profileResult.data;

  if (!profile || !profile.is_active) {
    await sb.auth.signOut();
    window.location.href = loginPage;
    return;
  }

  // ─── Expose user globally ───
  window.PAPIK_USER = {
    id: session.user.id,
    email: session.user.email,
    first_name: profile.first_name,
    last_name: profile.last_name,
    role: profile.role,
    phone: profile.phone,
    company: profile.company,
    is_active: profile.is_active
  };

  // ─── Logout utility ───
  window.papikLogout = async function() {
    await sb.auth.signOut();
    window.location.href = loginPage;
  };

  // ─── Listen for sign-out ───
  sb.auth.onAuthStateChange(function(event) {
    if (event === 'SIGNED_OUT') {
      window.location.href = loginPage;
    }
  });

  // ─── Notify dashboard that auth is ready ───
  if (typeof window.onPapikReady === 'function') {
    window.onPapikReady(window.PAPIK_USER);
  }

  console.log('PAPik Guard: authenticated as', profile.first_name, '(' + profile.role + ')');
})();
