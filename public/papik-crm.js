/**
 * PAPIK CRM — Shared Component Library
 * ======================================
 * Provides navigation, modals, toasts, tables, forms, data fetchers,
 * chart helpers, file uploads, formatting utilities, and UI components
 * shared across all CRM dashboards.
 *
 * Dependencies:
 *   - Supabase client at window._papikClient
 *   - User info at window.papikUser (set by papik:user-ready event)
 *   - Config: window.PAPIK_SUPABASE_URL, window.PAPIK_SUPABASE_ANON_KEY
 *   - Chart.js loaded via CDN (for chart helpers)
 *
 * Usage:
 *   <script src="papik-crm.js"></script>
 *   Then call PapikCRM.initNav(), PapikCRM.toast(), etc.
 */

/* =================================================================
   1. INIT — Namespace
   ================================================================= */

window.PapikCRM = {
  client: null,
  user: null,
  currentSection: null
};

/* -----------------------------------------------------------------
   Bootstrap: bind client & user as soon as they are available
   ----------------------------------------------------------------- */
(function () {
  function _bindClient() {
    if (window._papikClient) {
      PapikCRM.client = window._papikClient;
    }
  }

  function _bindUser() {
    if (window.papikUser) {
      PapikCRM.user = window.papikUser;
    }
  }

  // Try immediately
  _bindClient();
  _bindUser();

  // Also listen for the user-ready event
  document.addEventListener('papik:user-ready', function () {
    _bindUser();
    _bindClient();
  });

  // Fallback: poll briefly in case scripts load out of order
  var _pollCount = 0;
  var _pollTimer = setInterval(function () {
    _bindClient();
    _bindUser();
    _pollCount++;
    if ((PapikCRM.client && PapikCRM.user) || _pollCount > 30) {
      clearInterval(_pollTimer);
    }
  }, 200);
})();


/* =================================================================
   2. SECTION NAVIGATION (SPA-like)
   ================================================================= */

PapikCRM.initNav = function () {
  // Read initial hash
  var hash = window.location.hash || '';
  var match = hash.match(/section=([^&]+)/);
  var initialSection = match ? match[1] : null;

  // Attach click handlers
  var navItems = document.querySelectorAll('.nav-item[data-section]');
  for (var i = 0; i < navItems.length; i++) {
    (function (item) {
      item.addEventListener('click', function (e) {
        e.preventDefault();
        var sectionId = item.getAttribute('data-section');
        PapikCRM.showSection(sectionId);
      });
    })(navItems[i]);
  }

  // Restore section from hash or show the first one
  if (initialSection) {
    PapikCRM.showSection(initialSection);
  } else if (navItems.length > 0) {
    PapikCRM.showSection(navItems[0].getAttribute('data-section'));
  }

  // Listen for popstate (browser back / forward)
  window.addEventListener('popstate', function () {
    var h = window.location.hash || '';
    var m = h.match(/section=([^&]+)/);
    if (m) {
      PapikCRM.showSection(m[1], true); // true = skip pushState
    }
  });
};

/**
 * Show a CRM section by its id.
 * @param {string} sectionId — matches data-section and .crm-section id
 * @param {boolean} [skipHash] — if true, do not update the URL hash
 */
PapikCRM.showSection = function (sectionId, skipHash) {
  // Hide all sections
  var sections = document.querySelectorAll('.crm-section');
  for (var i = 0; i < sections.length; i++) {
    sections[i].style.display = 'none';
    sections[i].classList.remove('active');
  }

  // Show the target
  var target = document.getElementById(sectionId);
  if (target) {
    target.style.display = '';
    target.classList.add('active');
  }

  // Update nav items
  var navItems = document.querySelectorAll('.nav-item[data-section]');
  for (var j = 0; j < navItems.length; j++) {
    if (navItems[j].getAttribute('data-section') === sectionId) {
      navItems[j].classList.add('active');
    } else {
      navItems[j].classList.remove('active');
    }
  }

  // Update topbar title
  var activeNav = document.querySelector('.nav-item[data-section="' + sectionId + '"]');
  var topbarTitle = document.querySelector('.crm-topbar__title');
  if (topbarTitle && activeNav) {
    var label = activeNav.getAttribute('data-label') || activeNav.textContent.trim();
    topbarTitle.textContent = label;
  }

  // Update hash
  if (!skipHash) {
    window.location.hash = 'section=' + sectionId;
  }

  PapikCRM.currentSection = sectionId;
};


/* =================================================================
   3. MODAL SYSTEM
   ================================================================= */

PapikCRM.openModal = function (id) {
  var overlay = document.getElementById(id);
  if (!overlay) return;
  overlay.style.display = 'flex';
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
};

PapikCRM.closeModal = function (id) {
  var overlay = document.getElementById(id);
  if (!overlay) return;
  overlay.classList.remove('active');
  overlay.style.display = 'none';
  // Restore scroll only if no other modals open
  var openModals = document.querySelectorAll('.modal-overlay.active');
  if (openModals.length === 0) {
    document.body.style.overflow = '';
  }
};

PapikCRM.closeAllModals = function () {
  var overlays = document.querySelectorAll('.modal-overlay');
  for (var i = 0; i < overlays.length; i++) {
    overlays[i].classList.remove('active');
    overlays[i].style.display = 'none';
  }
  document.body.style.overflow = '';
};

/* Auto-close on click-outside and Escape key */
(function () {
  document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal-overlay') && e.target.classList.contains('active')) {
      PapikCRM.closeModal(e.target.id);
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      PapikCRM.closeAllModals();
    }
  });
})();


/* =================================================================
   4. TOAST NOTIFICATIONS
   ================================================================= */

/**
 * Show a toast notification.
 * @param {string} message
 * @param {string} [type='success'] — 'success' | 'error' | 'warning'
 * @param {number} [duration=4000]
 * @returns {HTMLElement} the toast element
 */
PapikCRM.toast = function (message, type, duration) {
  type = type || 'success';
  duration = duration != null ? duration : 4000;

  // Ensure container exists
  var container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    container.style.cssText = 'position:fixed;top:24px;right:24px;z-index:10000;display:flex;flex-direction:column;gap:10px;pointer-events:none;';
    document.body.appendChild(container);
  }

  var iconMap = {
    success: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>',
    error: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>',
    warning: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
  };

  var bgMap = {
    success: '#3a7d44',
    error: '#c0392b',
    warning: '#e67e22'
  };

  var toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.style.cssText = 'pointer-events:auto;display:flex;align-items:center;gap:10px;padding:14px 20px;border-radius:8px;color:#fff;font-family:"DM Sans",sans-serif;font-size:14px;box-shadow:0 4px 16px rgba(0,0,0,.2);transform:translateX(120%);transition:transform .35s cubic-bezier(.4,0,.2,1),opacity .3s;opacity:0;background:' + (bgMap[type] || bgMap.success) + ';max-width:400px;';

  toast.innerHTML = (iconMap[type] || '') + '<span>' + message + '</span>';

  container.appendChild(toast);

  // Animate in
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      toast.style.transform = 'translateX(0)';
      toast.style.opacity = '1';
    });
  });

  // Auto-remove
  var removeTimer = setTimeout(function () {
    toast.style.transform = 'translateX(120%)';
    toast.style.opacity = '0';
    setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 400);
  }, duration);

  // Allow manual dismiss on click
  toast.addEventListener('click', function () {
    clearTimeout(removeTimer);
    toast.style.transform = 'translateX(120%)';
    toast.style.opacity = '0';
    setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 400);
  });

  return toast;
};


/* =================================================================
   5. DATA TABLE RENDERING
   ================================================================= */

/**
 * Render a full data table with search filtering.
 *
 * @param {string} tableId — DOM element id to render into
 * @param {object} config
 *   - columns: [{key, label, sortable, render}]
 *   - data: array of row objects
 *   - searchKey: string key or function(row, query) => boolean
 *   - emptyMessage: string
 * @returns {{refresh: function(data)}}
 */
PapikCRM.renderTable = function (tableId, config) {
  var container = document.getElementById(tableId);
  if (!container) return { refresh: function () {} };

  var columns = config.columns || [];
  var data = config.data || [];
  var searchKey = config.searchKey || null;
  var emptyMessage = config.emptyMessage || 'No hi ha dades disponibles.';
  var currentData = data.slice();
  var searchQuery = '';

  function render(rows) {
    var html = '';

    // Search toolbar
    if (searchKey) {
      html += '<div class="table-toolbar" style="margin-bottom:12px;">';
      html += '<input type="text" class="table-search-input" placeholder="Cercar..." value="' + _escAttr(searchQuery) + '" style="padding:8px 12px;border:1px solid #C5CAC8;border-radius:6px;font-size:14px;font-family:DM Sans,sans-serif;width:260px;outline:none;">';
      html += '</div>';
    }

    if (rows.length === 0) {
      html += '<div class="table-empty" style="padding:40px;text-align:center;color:#888;font-size:14px;">' + emptyMessage + '</div>';
      container.innerHTML = html;
      _bindSearch();
      return;
    }

    html += '<div class="table-wrapper" style="overflow-x:auto;">';
    html += '<table class="crm-table" style="width:100%;border-collapse:collapse;font-size:14px;font-family:DM Sans,sans-serif;">';

    // Header
    html += '<thead><tr>';
    for (var c = 0; c < columns.length; c++) {
      html += '<th style="text-align:left;padding:10px 12px;border-bottom:2px solid #C5CAC8;font-weight:600;color:#2C4A6E;white-space:nowrap;">' + columns[c].label + '</th>';
    }
    html += '</tr></thead>';

    // Body
    html += '<tbody>';
    for (var r = 0; r < rows.length; r++) {
      html += '<tr style="border-bottom:1px solid #eee;">';
      for (var c2 = 0; c2 < columns.length; c2++) {
        var col = columns[c2];
        var val = rows[r][col.key];
        var display = col.render ? col.render(val, rows[r]) : (val != null ? _esc(String(val)) : '—');
        html += '<td style="padding:10px 12px;vertical-align:middle;">' + display + '</td>';
      }
      html += '</tr>';
    }
    html += '</tbody></table></div>';

    container.innerHTML = html;
    _bindSearch();
  }

  function _bindSearch() {
    var input = container.querySelector('.table-search-input');
    if (!input) return;
    input.addEventListener('input', function () {
      searchQuery = input.value.toLowerCase();
      var filtered = _filterData(currentData, searchQuery);
      // Re-render body only (keep search value)
      render(filtered);
      // Restore focus and cursor
      var newInput = container.querySelector('.table-search-input');
      if (newInput) {
        newInput.focus();
        newInput.setSelectionRange(newInput.value.length, newInput.value.length);
      }
    });
  }

  function _filterData(rows, query) {
    if (!query || !searchKey) return rows;
    return rows.filter(function (row) {
      if (typeof searchKey === 'function') {
        return searchKey(row, query);
      }
      var val = row[searchKey];
      return val != null && String(val).toLowerCase().indexOf(query) !== -1;
    });
  }

  // Initial render
  render(_filterData(currentData, searchQuery));

  return {
    refresh: function (newData) {
      currentData = (newData || []).slice();
      searchQuery = '';
      render(currentData);
    }
  };
};


/* =================================================================
   6. FORM HELPERS
   ================================================================= */

/**
 * Read all named form fields into a plain object.
 */
PapikCRM.getFormData = function (formEl) {
  var data = {};
  if (!formEl) return data;
  var elements = formEl.querySelectorAll('input, select, textarea');
  for (var i = 0; i < elements.length; i++) {
    var el = elements[i];
    var name = el.getAttribute('name');
    if (!name) continue;

    if (el.type === 'checkbox') {
      data[name] = el.checked;
    } else if (el.type === 'radio') {
      if (el.checked) data[name] = el.value;
    } else if (el.type === 'number') {
      data[name] = el.value !== '' ? parseFloat(el.value) : null;
    } else if (el.type === 'file') {
      data[name] = el.files && el.files.length > 0 ? el.files : null;
    } else {
      data[name] = el.value;
    }
  }
  return data;
};

/**
 * Clear all fields in a form element.
 */
PapikCRM.resetForm = function (formEl) {
  if (!formEl) return;
  if (typeof formEl.reset === 'function') {
    formEl.reset();
  } else {
    var elements = formEl.querySelectorAll('input, select, textarea');
    for (var i = 0; i < elements.length; i++) {
      var el = elements[i];
      if (el.type === 'checkbox' || el.type === 'radio') {
        el.checked = false;
      } else if (el.tagName === 'SELECT') {
        el.selectedIndex = 0;
      } else {
        el.value = '';
      }
    }
  }
};

/**
 * Fill a form from a data object (keys = name attributes).
 */
PapikCRM.setFormData = function (formEl, data) {
  if (!formEl || !data) return;
  var elements = formEl.querySelectorAll('input, select, textarea');
  for (var i = 0; i < elements.length; i++) {
    var el = elements[i];
    var name = el.getAttribute('name');
    if (!name || !(name in data)) continue;

    if (el.type === 'checkbox') {
      el.checked = !!data[name];
    } else if (el.type === 'radio') {
      el.checked = (el.value === String(data[name]));
    } else {
      el.value = data[name] != null ? data[name] : '';
    }
  }
};


/* =================================================================
   7. SUPABASE DATA FETCHERS
   ================================================================= */

/**
 * Internal helper: get the Supabase client, throwing if unavailable.
 */
function _client() {
  var c = PapikCRM.client || window._papikClient;
  if (!c) throw new Error('PapikCRM: Supabase client not available');
  return c;
}

/**
 * Internal helper: add computed full_name to profile join objects.
 * Walks data recursively looking for objects with first_name/last_name.
 */
function _addFullName(data) {
  if (!data) return data;
  if (Array.isArray(data)) {
    for (var i = 0; i < data.length; i++) _addFullName(data[i]);
    return data;
  }
  if (typeof data === 'object') {
    if (data.first_name !== undefined || data.last_name !== undefined) {
      data.full_name = ((data.first_name || '') + ' ' + (data.last_name || '')).trim();
    }
    // Check nested profile joins
    var keys = Object.keys(data);
    for (var k = 0; k < keys.length; k++) {
      var val = data[keys[k]];
      if (val && typeof val === 'object') _addFullName(val);
    }
  }
  return data;
}

/**
 * Get a full name from a profile object.
 */
PapikCRM.fullName = function (profile) {
  if (!profile) return '--';
  if (profile.full_name) return profile.full_name;
  return ((profile.first_name || '') + ' ' + (profile.last_name || '')).trim() || '--';
};

/**
 * Fetch projects with optional filters.
 * Joins profiles for client display name.
 */
PapikCRM.fetchProjects = async function (filters) {
  var q = _client()
    .from('projects')
    .select('*, profiles:client_id(id, first_name, last_name, email)')
    .order('created_at', { ascending: false });

  if (filters) {
    if (filters.status) q = q.eq('status', filters.status);
    if (filters.client_id) q = q.eq('client_id', filters.client_id);
  }

  var res = await q;
  if (res.error) {
    console.error('fetchProjects error:', res.error);
    return [];
  }
  return _addFullName(res.data || []);
};

/**
 * Fetch full project detail including related data.
 */
PapikCRM.fetchProjectDetail = async function (projectId) {
  var c = _client();

  var results = await Promise.all([
    c.from('projects').select('*, profiles:client_id(id, first_name, last_name, email)').eq('id', projectId).single(),
    c.from('project_members').select('*, profiles:user_id(id, first_name, last_name, email, role)').eq('project_id', projectId),
    c.from('documents').select('*, profiles:uploaded_by(id, first_name, last_name)').eq('project_id', projectId).order('created_at', { ascending: false }),
    c.from('tasks').select('*, profiles:assigned_to(id, first_name, last_name)').eq('project_id', projectId).order('created_at', { ascending: false }),
    c.from('project_notes').select('*, profiles:author_id(id, first_name, last_name)').eq('project_id', projectId).order('created_at', { ascending: false }),
    c.from('budget_items').select('*').eq('project_id', projectId).order('created_at', { ascending: false })
  ]);

  var detail = {
    project: _addFullName(results[0].data || null),
    members: _addFullName(results[1].data || []),
    documents: _addFullName(results[2].data || []),
    tasks: _addFullName(results[3].data || []),
    notes: _addFullName(results[4].data || []),
    budget_items: results[5].data || []
  };
  return detail;
};

/**
 * Fetch all user profiles.
 */
PapikCRM.fetchUsers = async function () {
  var res = await _client()
    .from('profiles')
    .select('*')
    .order('created_at', { ascending: false });

  if (res.error) {
    console.error('fetchUsers error:', res.error);
    return [];
  }
  return res.data || [];
};

/**
 * Fetch invoices with optional filters.
 */
PapikCRM.fetchInvoices = async function (filters) {
  var q = _client()
    .from('invoices')
    .select('*, profiles:client_id(id, first_name, last_name, email), projects:project_id(id, name)')
    .order('created_at', { ascending: false });

  if (filters) {
    if (filters.status) q = q.eq('status', filters.status);
    if (filters.client_id) q = q.eq('client_id', filters.client_id);
    if (filters.project_id) q = q.eq('project_id', filters.project_id);
  }

  var res = await q;
  if (res.error) {
    console.error('fetchInvoices error:', res.error);
    return [];
  }
  return _addFullName(res.data || []);
};

/**
 * Fetch documents with optional filters.
 */
PapikCRM.fetchDocuments = async function (filters) {
  var q = _client()
    .from('documents')
    .select('*, profiles:uploaded_by(id, first_name, last_name)')
    .order('created_at', { ascending: false });

  if (filters) {
    if (filters.project_id) q = q.eq('project_id', filters.project_id);
    if (filters.category) q = q.eq('category', filters.category);
  }

  var res = await q;
  if (res.error) {
    console.error('fetchDocuments error:', res.error);
    return [];
  }
  return _addFullName(res.data || []);
};

/**
 * Fetch tasks with optional filters.
 */
PapikCRM.fetchTasks = async function (filters) {
  var q = _client()
    .from('tasks')
    .select('*, profiles:assigned_to(id, first_name, last_name)')
    .order('created_at', { ascending: false });

  if (filters) {
    if (filters.project_id) q = q.eq('project_id', filters.project_id);
    if (filters.assigned_to) q = q.eq('assigned_to', filters.assigned_to);
    if (filters.status) q = q.eq('status', filters.status);
  }

  var res = await q;
  if (res.error) {
    console.error('fetchTasks error:', res.error);
    return [];
  }
  return _addFullName(res.data || []);
};

/**
 * Fetch activity log entries.
 */
PapikCRM.fetchActivity = async function (limit) {
  limit = limit || 20;
  var res = await _client()
    .from('activity_log')
    .select('*, profiles:user_id(id, first_name, last_name)')
    .order('created_at', { ascending: false })
    .limit(limit);

  if (res.error) {
    console.error('fetchActivity error:', res.error);
    return [];
  }
  return _addFullName(res.data || []);
};

/**
 * Fetch budget items for a project.
 */
PapikCRM.fetchBudgetItems = async function (projectId) {
  var res = await _client()
    .from('budget_items')
    .select('*')
    .eq('project_id', projectId)
    .order('created_at', { ascending: false });

  if (res.error) {
    console.error('fetchBudgetItems error:', res.error);
    return [];
  }
  return res.data || [];
};

/**
 * Fetch budget configs for a client.
 */
PapikCRM.fetchBudgetConfigs = async function (clientId) {
  var res = await _client()
    .from('budget_configs')
    .select('*')
    .eq('client_id', clientId)
    .order('created_at', { ascending: false });

  if (res.error) {
    console.error('fetchBudgetConfigs error:', res.error);
    return [];
  }
  return res.data || [];
};

/**
 * Fetch projects where the current user is a member.
 */
PapikCRM.fetchMyProjects = async function () {
  var userId = PapikCRM.user && PapikCRM.user.id;
  if (!userId) {
    console.warn('fetchMyProjects: no current user');
    return [];
  }

  var memberRes = await _client()
    .from('project_members')
    .select('project_id')
    .eq('user_id', userId);

  if (memberRes.error || !memberRes.data || memberRes.data.length === 0) return [];

  var projectIds = memberRes.data.map(function (m) { return m.project_id; });

  var res = await _client()
    .from('projects')
    .select('*, profiles:client_id(id, first_name, last_name, email)')
    .in('id', projectIds)
    .order('created_at', { ascending: false });

  if (res.error) {
    console.error('fetchMyProjects error:', res.error);
    return [];
  }
  return _addFullName(res.data || []);
};

/**
 * Fetch tasks assigned to the current user.
 */
PapikCRM.fetchMyTasks = async function () {
  var userId = PapikCRM.user && PapikCRM.user.id;
  if (!userId) {
    console.warn('fetchMyTasks: no current user');
    return [];
  }

  var res = await _client()
    .from('tasks')
    .select('*, projects:project_id(id, name)')
    .eq('assigned_to', userId)
    .order('created_at', { ascending: false });

  if (res.error) {
    console.error('fetchMyTasks error:', res.error);
    return [];
  }
  return res.data || [];
};


/* =================================================================
   8. ACTIVITY LOGGER
   ================================================================= */

/**
 * Insert an entry into the activity_log table.
 */
PapikCRM.logActivity = async function (activity, description, projectId, metadata) {
  var userId = PapikCRM.user && PapikCRM.user.id;
  var payload = {
    activity: activity,
    description: description,
    user_id: userId || null,
    project_id: projectId || null,
    metadata: metadata || null
  };

  var res = await _client()
    .from('activity_log')
    .insert(payload);

  if (res.error) {
    console.error('logActivity error:', res.error);
  }
  return res;
};


/* =================================================================
   9. FORMATTING UTILITIES
   ================================================================= */

/**
 * Format a date string as DD/MM/YYYY.
 */
PapikCRM.formatDate = function (dateStr) {
  if (!dateStr) return '\u2014';
  var d = new Date(dateStr);
  if (isNaN(d.getTime())) return '\u2014';
  var dd = String(d.getDate()).padStart(2, '0');
  var mm = String(d.getMonth() + 1).padStart(2, '0');
  var yyyy = d.getFullYear();
  return dd + '/' + mm + '/' + yyyy;
};

/**
 * Format a date string as DD/MM/YYYY HH:mm.
 */
PapikCRM.formatDateTime = function (dateStr) {
  if (!dateStr) return '\u2014';
  var d = new Date(dateStr);
  if (isNaN(d.getTime())) return '\u2014';
  var dd = String(d.getDate()).padStart(2, '0');
  var mm = String(d.getMonth() + 1).padStart(2, '0');
  var yyyy = d.getFullYear();
  var hh = String(d.getHours()).padStart(2, '0');
  var min = String(d.getMinutes()).padStart(2, '0');
  return dd + '/' + mm + '/' + yyyy + ' ' + hh + ':' + min;
};

/**
 * Format a number as European currency: 1.234,56 EUR
 */
PapikCRM.formatCurrency = function (amount) {
  if (amount == null || amount === 0) return '\u2014';
  var num = parseFloat(amount);
  if (isNaN(num)) return '\u2014';
  // Format with 2 decimals, then swap . and ,
  var parts = num.toFixed(2).split('.');
  var intPart = parts[0];
  var decPart = parts[1];
  // Add thousands separator (.)
  var sign = '';
  if (intPart[0] === '-') {
    sign = '-';
    intPart = intPart.substring(1);
  }
  var formatted = '';
  for (var i = intPart.length - 1, count = 0; i >= 0; i--, count++) {
    if (count > 0 && count % 3 === 0) formatted = '.' + formatted;
    formatted = intPart[i] + formatted;
  }
  return sign + formatted + ',' + decPart + ' \u20AC';
};

/**
 * Format bytes into human-readable file size.
 */
PapikCRM.formatFileSize = function (bytes) {
  if (bytes == null || bytes === 0) return '0 B';
  var b = parseInt(bytes, 10);
  if (isNaN(b)) return '0 B';
  if (b < 1024) return b + ' B';
  if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
  if (b < 1024 * 1024 * 1024) return (b / (1024 * 1024)).toFixed(1) + ' MB';
  return (b / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
};

/**
 * Relative time in Catalan (e.g. "fa 2 hores", "fa 3 dies").
 */
PapikCRM.timeAgo = function (dateStr) {
  if (!dateStr) return '\u2014';
  var now = Date.now();
  var then = new Date(dateStr).getTime();
  if (isNaN(then)) return '\u2014';

  var diff = now - then;
  var seconds = Math.floor(diff / 1000);
  var minutes = Math.floor(seconds / 60);
  var hours = Math.floor(minutes / 60);
  var days = Math.floor(hours / 24);
  var weeks = Math.floor(days / 7);
  var months = Math.floor(days / 30);
  var years = Math.floor(days / 365);

  if (seconds < 60) return 'ara mateix';
  if (minutes === 1) return 'fa 1 minut';
  if (minutes < 60) return 'fa ' + minutes + ' minuts';
  if (hours === 1) return 'fa 1 hora';
  if (hours < 24) return 'fa ' + hours + ' hores';
  if (days === 1) return 'fa 1 dia';
  if (days < 7) return 'fa ' + days + ' dies';
  if (weeks === 1) return 'fa 1 setmana';
  if (weeks < 5) return 'fa ' + weeks + ' setmanes';
  if (months === 1) return 'fa 1 mes';
  if (months < 12) return 'fa ' + months + ' mesos';
  if (years === 1) return 'fa 1 any';
  return 'fa ' + years + ' anys';
};


/* =================================================================
   10. BADGE GENERATORS
   ================================================================= */

/**
 * Generate a role badge HTML string.
 */
PapikCRM.roleBadge = function (role) {
  if (!role) return '';
  return '<span class="badge badge-' + _esc(role) + '">' + _esc(role.toUpperCase()) + '</span>';
};

/**
 * Generate a status badge with Catalan labels.
 */
PapikCRM.statusBadge = function (status) {
  var labelMap = {
    draft: 'Esborrany',
    in_progress: 'En curs',
    completed: 'Completat',
    archived: 'Arxivat',
    paid: 'Pagada',
    sent: 'Enviada',
    overdue: 'Ven\u00E7uda',
    cancelled: 'Cancel\u00B7lada',
    pending: 'Pendent'
  };
  var label = labelMap[status] || status || '\u2014';
  var cssClass = status ? _esc(status) : 'default';
  return '<span class="badge badge-' + cssClass + '">' + _esc(label) + '</span>';
};

/**
 * Generate a priority badge with Catalan labels.
 */
PapikCRM.priorityBadge = function (priority) {
  var labelMap = {
    low: 'Baixa',
    medium: 'Mitjana',
    high: 'Alta',
    urgent: 'Urgent'
  };
  var label = labelMap[priority] || priority || '\u2014';
  var cssClass = priority ? _esc(priority) : 'default';
  return '<span class="badge badge-priority-' + cssClass + '">' + _esc(label) + '</span>';
};


/* =================================================================
   11. ACTIVITY ICON MAP
   ================================================================= */

PapikCRM.activityIcon = function (type) {
  var icons = {
    project_created: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>',
    project_updated: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2C4A6E" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
    task_created: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>',
    task_completed: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/></svg>',
    task_updated: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e67e22" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>',
    document_uploaded: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2C4A6E" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9,15 12,12 15,15"/></svg>',
    document_deleted: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#c0392b" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="9" y1="13" x2="15" y2="13"/></svg>',
    invoice_created: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><rect x="2" y="3" width="20" height="18" rx="2"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="12" y2="15"/></svg>',
    invoice_paid: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
    user_created: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>',
    user_updated: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2C4A6E" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    budget_updated: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e67e22" stroke-width="2"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="12" y2="14"/></svg>',
    note_added: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2C4A6E" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
    member_added: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
    member_removed: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#c0392b" stroke-width="2"><path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="23" y1="11" x2="17" y2="11"/></svg>',
    login: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#3a7d44" stroke-width="2"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10,17 15,12 10,7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>',
    logout: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16,17 21,12 16,7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>'
  };

  return icons[type] || '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
};


/* =================================================================
   12. CHART HELPERS (Chart.js)
   ================================================================= */

/**
 * Helper to resolve CSS custom properties.
 */
function _cssVar(varName, fallback) {
  try {
    var val = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
    return val || fallback;
  } catch (e) {
    return fallback;
  }
}

var _chartColors = {
  green: '#3a7d44',
  darkGreen: '#4A6741',
  lightGreen: '#6B8F71',
  blue: '#2C4A6E',
  orange: '#e67e22',
  red: '#c0392b',
  grey: '#888'
};

var _chartDefaults = {
  fontFamily: '"DM Sans", sans-serif',
  borderRadius: 4,
  gridColor: '#C5CAC8',
  legendFontSize: 12
};

/**
 * Create a bar chart.
 */
PapikCRM.createBarChart = function (canvasId, labels, datasets, options) {
  var canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') {
    console.warn('createBarChart: canvas or Chart.js not found');
    return null;
  }

  // Destroy existing chart if any
  if (canvas._papikChart) {
    canvas._papikChart.destroy();
  }

  var defaultColors = [_chartColors.green, _chartColors.darkGreen, _chartColors.lightGreen, _chartColors.blue];

  var chartDatasets = datasets.map(function (ds, i) {
    return Object.assign({
      backgroundColor: ds.backgroundColor || defaultColors[i % defaultColors.length],
      borderRadius: _chartDefaults.borderRadius,
      borderSkipped: false
    }, ds);
  });

  var cfg = {
    type: 'bar',
    data: {
      labels: labels,
      datasets: chartDatasets
    },
    options: Object.assign({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { family: _chartDefaults.fontFamily, size: _chartDefaults.legendFontSize },
            padding: 16
          }
        }
      },
      scales: {
        x: {
          grid: { color: _cssVar('--border', _chartDefaults.gridColor) },
          ticks: { font: { family: _chartDefaults.fontFamily, size: 12 } }
        },
        y: {
          grid: { color: _cssVar('--border', _chartDefaults.gridColor) },
          ticks: { font: { family: _chartDefaults.fontFamily, size: 12 } },
          beginAtZero: true
        }
      }
    }, options || {})
  };

  var chart = new Chart(canvas.getContext('2d'), cfg);
  canvas._papikChart = chart;
  return chart;
};

/**
 * Create a doughnut chart.
 */
PapikCRM.createDoughnutChart = function (canvasId, labels, data, colors) {
  var canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') {
    console.warn('createDoughnutChart: canvas or Chart.js not found');
    return null;
  }

  if (canvas._papikChart) {
    canvas._papikChart.destroy();
  }

  var defaultColors = [_chartColors.green, _chartColors.blue, _chartColors.orange, _chartColors.lightGreen, _chartColors.darkGreen, _chartColors.red, _chartColors.grey];

  var cfg = {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors || defaultColors.slice(0, data.length),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { family: _chartDefaults.fontFamily, size: _chartDefaults.legendFontSize },
            padding: 16,
            usePointStyle: true,
            pointStyle: 'circle'
          }
        }
      }
    }
  };

  var chart = new Chart(canvas.getContext('2d'), cfg);
  canvas._papikChart = chart;
  return chart;
};

/**
 * Create a line chart.
 */
PapikCRM.createLineChart = function (canvasId, labels, datasets) {
  var canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') {
    console.warn('createLineChart: canvas or Chart.js not found');
    return null;
  }

  if (canvas._papikChart) {
    canvas._papikChart.destroy();
  }

  var defaultColors = [_chartColors.green, _chartColors.blue, _chartColors.orange, _chartColors.lightGreen];

  var chartDatasets = datasets.map(function (ds, i) {
    var color = ds.borderColor || defaultColors[i % defaultColors.length];
    return Object.assign({
      borderColor: color,
      backgroundColor: color + '1A', // 10% opacity
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: color,
      tension: 0.3,
      fill: true
    }, ds);
  });

  var cfg = {
    type: 'line',
    data: {
      labels: labels,
      datasets: chartDatasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { family: _chartDefaults.fontFamily, size: _chartDefaults.legendFontSize },
            padding: 16
          }
        }
      },
      scales: {
        x: {
          grid: { color: _cssVar('--border', _chartDefaults.gridColor) },
          ticks: { font: { family: _chartDefaults.fontFamily, size: 12 } }
        },
        y: {
          grid: { color: _cssVar('--border', _chartDefaults.gridColor) },
          ticks: { font: { family: _chartDefaults.fontFamily, size: 12 } },
          beginAtZero: true
        }
      }
    }
  };

  var chart = new Chart(canvas.getContext('2d'), cfg);
  canvas._papikChart = chart;
  return chart;
};


/* =================================================================
   13. FILE UPLOAD HELPER
   ================================================================= */

/**
 * Upload a file to Supabase Storage and insert a document record.
 * @param {File} file
 * @param {string} projectId
 * @param {string} category
 * @returns {object} the inserted document record
 */
PapikCRM.uploadFile = async function (file, projectId, category) {
  var c = _client();
  var timestamp = Date.now();
  var safeName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
  var path = projectId + '/' + (category || 'general') + '/' + timestamp + '_' + safeName;

  // Upload to storage
  var uploadRes = await c.storage
    .from('documents')
    .upload(path, file, {
      cacheControl: '3600',
      upsert: false
    });

  if (uploadRes.error) {
    console.error('uploadFile storage error:', uploadRes.error);
    throw uploadRes.error;
  }

  // Insert document record
  var userId = PapikCRM.user && PapikCRM.user.id;
  var docRes = await c
    .from('documents')
    .insert({
      project_id: projectId,
      title: file.name,
      file_path: path,
      file_size: file.size,
      mime_type: file.type || 'application/octet-stream',
      category: category || 'other',
      uploaded_by: userId || null
    })
    .select()
    .single();

  if (docRes.error) {
    console.error('uploadFile insert error:', docRes.error);
    throw docRes.error;
  }

  return docRes.data;
};

/**
 * Get a signed URL for a file in storage (60 min expiry).
 */
PapikCRM.getFileUrl = async function (filePath) {
  var res = await _client().storage
    .from('documents')
    .createSignedUrl(filePath, 3600); // 60 minutes

  if (res.error) {
    console.error('getFileUrl error:', res.error);
    return null;
  }
  return res.data.signedUrl || res.data.signedURL || null;
};


/* =================================================================
   14. CONFIRM DIALOG
   ================================================================= */

/**
 * Show a confirmation dialog.
 * @param {string} message
 * @param {function} onConfirm — called if user clicks Confirmar
 */
PapikCRM.confirm = function (message, onConfirm) {
  // Create overlay
  var overlay = document.createElement('div');
  overlay.className = 'modal-overlay active';
  overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;z-index:9999;';

  var dialog = document.createElement('div');
  dialog.className = 'confirm-dialog';
  dialog.style.cssText = 'background:#fff;border-radius:12px;padding:32px;max-width:420px;width:90%;box-shadow:0 8px 32px rgba(0,0,0,.2);font-family:"DM Sans",sans-serif;';

  var msgEl = document.createElement('p');
  msgEl.style.cssText = 'margin:0 0 24px;font-size:15px;color:#333;line-height:1.5;';
  msgEl.textContent = message;

  var btnRow = document.createElement('div');
  btnRow.style.cssText = 'display:flex;justify-content:flex-end;gap:12px;';

  var cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel\u00B7lar';
  cancelBtn.style.cssText = 'padding:10px 20px;border:1px solid #C5CAC8;border-radius:8px;background:#fff;color:#333;font-size:14px;font-family:"DM Sans",sans-serif;cursor:pointer;';

  var confirmBtn = document.createElement('button');
  confirmBtn.textContent = 'Confirmar';
  confirmBtn.style.cssText = 'padding:10px 20px;border:none;border-radius:8px;background:#3a7d44;color:#fff;font-size:14px;font-family:"DM Sans",sans-serif;cursor:pointer;';

  btnRow.appendChild(cancelBtn);
  btnRow.appendChild(confirmBtn);
  dialog.appendChild(msgEl);
  dialog.appendChild(btnRow);
  overlay.appendChild(dialog);
  document.body.appendChild(overlay);

  function close() {
    if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    document.body.style.overflow = '';
  }

  cancelBtn.addEventListener('click', close);

  confirmBtn.addEventListener('click', function () {
    close();
    if (typeof onConfirm === 'function') onConfirm();
  });

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) close();
  });

  document.body.style.overflow = 'hidden';
};


/* =================================================================
   15. SIDEBAR LOGO SVG (white version for dark background)
   ================================================================= */

PapikCRM.logoSVG = '<svg height="24" viewBox="155 228 535 140" xmlns="http://www.w3.org/2000/svg" style="display:block;overflow:visible;">' +
  '<path fill="#ffffff" d="M659.7,243.4c0-7,5.2-12.1,12.2-12.1c7,0,12.2,5.1,12.2,12.1c0,7-5.2,12.1-12.2,12.1 C664.9,255.5,659.7,250.3,659.7,243.4z M681.3,243.4c0-5.7-3.9-9.7-9.4-9.7c-5.6,0-9.4,4-9.4,9.7s3.9,9.7,9.4,9.7 C677.5,253.1,681.3,249.1,681.3,243.4z M667.5,236.9h4.4c3.2,0,5,1.6,5,3.8c0,1.3-0.8,2.4-2.5,3.4l3.2,5.3h-2.9l-3.6-6l1.6-0.8 c1.1-0.6,1.5-1.1,1.5-1.9c0-1.1-0.9-1.6-2.4-1.6H670v10.2h-2.6V236.9z"/>' +
  '<path fill="#ffffff" d="M489.9,232.2h26.2V364h-26.2V232.2z"/>' +
  '<path fill="#ffffff" d="M533.6,232.2h26.2V364h-26.2V232.2z"/>' +
  '<polygon fill="#ffffff" points="318,232.2 290.1,232.2 236.4,364 264.5,364 272.2,344.4 315.7,336.7 306.8,314 282.4,318.2 303.9,262.8 319.8,303.5 319.8,303.5 341,357.6 341,357.6 343.5,364 371.7,364"/>' +
  '<polygon fill="#ffffff" points="403.8,302.8 403.8,256.8 403.8,232.2 377.6,232.2 377.6,364 403.8,364 403.8,343.4 403.8,327.7"/>' +
  '<path fill="#ffffff" d="M428.4,232.2H417v24.6h11.7c14.8,0,23.3,7.1,23.3,18.9c0,10.8-7.9,18.9-23.1,22l-11.9,2.4v25l11.7-2.3 c34.3-7,49.9-24.7,49.9-48.2C478.6,248.9,458.8,232.2,428.4,232.2z"/>' +
  '<polygon fill="#ffffff" points="184.4,302.8 184.4,302.8 184.4,256.8 184.4,256.8 184.4,232.2 158.2,232.2 158.2,364 184.4,364 184.4,327.7 184.4,327.7"/>' +
  '<path fill="#ffffff" d="M208.9,232.2h-11.3v24.6h11.7c14.8,0,23.3,7.1,23.3,18.9c0,10.8-7.9,18.9-23.1,22l-11.9,2.4v25l11.7-2.3 c34.3-7,49.9-24.7,49.9-48.2C259.2,248.9,239.4,232.2,208.9,232.2z"/>' +
  '<path fill="#ffffff" d="M614.3,297.6c31.3-22.9,33.7-65.3,33.7-65.3h-26.2c0,0-1,34.1-27.1,49.2c0,0-5.5,3.4-10.1,5.4 c-4.6,2.1-13.1,5.1-13.1,5.1v25.1l19.2-7.9l31.5,54.9h29.5L614.3,297.6z"/>' +
  '</svg>';


/* =================================================================
   16. NAVIGATION ICONS (SVG strings, 20x20, stroke-based)
   ================================================================= */

PapikCRM.icons = {
  home: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>',

  users: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',

  projects: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"/><line x1="12" y1="12" x2="12" y2="12.01"/></svg>',

  invoices: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="18" rx="2"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="16" y2="11"/><line x1="8" y1="15" x2="12" y2="15"/></svg>',

  documents: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>',

  budgets: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="16" y2="10"/><line x1="8" y1="14" x2="16" y2="14"/><line x1="8" y1="18" x2="12" y2="18"/></svg>',

  settings: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>',

  tasks: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><rect x="3" y="3" width="18" height="18" rx="2"/></svg>',

  team: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',

  blueprints: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 2l4.5 4.5"/><path d="M22 2l-4.5 4.5"/><circle cx="12" cy="12" r="8"/><line x1="12" y1="4" x2="12" y2="12"/><line x1="12" y1="12" x2="17.66" y2="17.66"/></svg>',

  permits: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><path d="M9 15l2 2 4-4"/></svg>',

  consumption: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',

  myproject: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>'
};


/* =================================================================
   PRIVATE HELPERS (HTML escaping)
   ================================================================= */

/**
 * Escape HTML entities in a string.
 */
function _esc(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Escape for use inside HTML attribute values.
 */
function _escAttr(str) {
  return _esc(str);
}


/* =================================================================
   READY LOG
   ================================================================= */

console.log('%c PAPIK CRM %c Component library loaded', 'background:#3a7d44;color:#fff;padding:2px 8px;border-radius:3px 0 0 3px;font-weight:bold;', 'background:#2C4A6E;color:#fff;padding:2px 8px;border-radius:0 3px 3px 0;');
