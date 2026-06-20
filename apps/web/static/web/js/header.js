// ============================================
// Header dynamique + Notifications temps réel
// ============================================

function injectConnectedHeader(active = '') {
  const user     = Auth.getUser() || window.DJANGO_USER;
  const isLogged = Boolean(user);
  const mount    = document.getElementById('header-mount');
  if (!mount) return;

  let tpl = '';

  if (isLogged && user) {
    const nom = `${user.prenom || user.first_name || ''} ${user.nom || user.last_name || ''}`.trim() || user.username || 'Utilisateur';
    const isAdmin = user.est_administrateur;

    tpl = `
    <header class="header connected solid">
      <div class="container header-inner">
        <a href="/" class="logo">
          <img src="/static/web/images/logo-emsi.png" alt="Logo" class="logo-img" />
          <div class="logo-text">Bourse aux Livres<small>EMSI</small></div>
        </a>
        <div class="search-bar">
          <input type="search" id="global-search" placeholder="Rechercher un livre, matière, niveau…" />
        </div>
        <nav class="header-actions">
          ${isAdmin ? `<a href="/admin-panel/" class="btn" style="background:linear-gradient(135deg,#4f46e5,#7c3aed);color:#fff;font-weight:700;">🛡️ Admin</a>` : ''}
          <a href="/vendre/" class="btn btn-primary">+ Vendre</a>

          <!-- Favoris -->
          <a href="/profil/#favoris" class="icon-btn" title="Mes favoris">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
            </svg>
          </a>

          <!-- Messages -->
          <a href="/messagerie/" class="icon-btn" title="Messages" style="position:relative">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
            </svg>
          </a>

          <!-- Notifications -->
          <div style="position:relative">
            <button class="icon-btn" title="Notifications" onclick="toggleNotifPanel()" id="notif-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0M3.124 7.5A8.969 8.969 0 0 1 5.292 3m13.416 0a8.969 8.969 0 0 1 2.168 4.5" />
              </svg>
              <span class="badge-count" id="notif-count" style="display:none;position:absolute;top:-4px;right:-4px;background:#ef4444;color:#fff;border-radius:50%;width:18px;height:18px;font-size:10px;display:none;align-items:center;justify-content:center;font-weight:700;">0</span>
            </button>

            <!-- Panneau dropdown notifications -->
            <div id="notif-panel" style="display:none;position:absolute;right:0;top:52px;width:380px;background:#fff;border:1px solid #e5e7eb;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,.15);z-index:9999;">
              <div style="padding:14px 16px;border-bottom:1px solid #f3f4f6;display:flex;justify-content:space-between;align-items:center;">
                <strong style="font-size:15px;">🔔 Notifications</strong>
                <button onclick="marquerToutesLues()" style="background:none;border:none;color:#4f46e5;cursor:pointer;font-size:13px;font-weight:600;">Tout marquer lu</button>
              </div>
              <div id="notif-list" style="max-height:420px;overflow-y:auto;"></div>
              <div style="padding:12px;border-top:1px solid #f3f4f6;text-align:center;">
                <a href="/profil/" onclick="activerOngletNotifs()" style="font-size:13px;color:#4f46e5;font-weight:600;text-decoration:none;">Voir toutes les notifications →</a>
              </div>
            </div>
          </div>

          <!-- Profil -->
          <a href="/profil/" class="icon-btn avatar" title="${nom}" id="header-avatar-link" style="width:36px;height:36px;border-radius:50%;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;text-decoration:none;overflow:hidden;flex-shrink:0;">
            ${user.photo_url ? `<img src="${user.photo_url}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="Photo" onerror="this.parentElement.innerHTML='${initials(nom)}';this.parentElement.style.background='var(--primary)';">` : initials(nom)}
          </a>

          <!-- Déconnexion -->
          <button class="icon-btn" title="Déconnexion" onclick="Auth.logout()" style="color:var(--gray-500);">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
            </svg>
          </button>
        </nav>
      </div>
    </header>`;
  } else {
    tpl = `
    <header class="header solid">
      <div class="container header-inner">
        <a href="/" class="logo">
          <img src="/static/web/images/logo-emsi.png" alt="Logo" class="logo-img" />
          <div class="logo-text">Bourse aux Livres<small>EMSI</small></div>
        </a>
        <div class="search-bar">
          <input type="search" id="global-search" placeholder="Rechercher un livre, matière, niveau…" />
        </div>
        <nav class="header-actions">
          <a href="/catalogue/" class="btn btn-outline">Explorer</a>
          <a href="/connexion/" class="btn btn-primary">Connexion</a>
          <a href="/inscription/" class="btn btn-outline">Inscription</a>
        </nav>
      </div>
    </header>`;
  }

  mount.outerHTML = tpl;

  setTimeout(() => {
    // Recherche globale
    const search = document.getElementById('global-search');
    if (search) {
      search.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && search.value.trim()) {
          window.location.href = `/catalogue/?q=${encodeURIComponent(search.value.trim())}`;
        }
      });
    }

    if (isLogged && user) {
      // Charger le compteur au départ
      loadNotifCount();
      // Fermer panel si clic en dehors
      document.addEventListener('click', (e) => {
        const panel = document.getElementById('notif-panel');
        const btn   = document.getElementById('notif-btn');
        if (panel && btn && !panel.contains(e.target) && !btn.contains(e.target)) {
          panel.style.display = 'none';
        }
      });
    }
  }, 0);
}

// ── Compteur notifications ────────────────────────────────────────────────────
async function loadNotifCount() {
  if (!Auth.isLogged()) return;
  try {
    const data  = await API.get(ENDPOINTS.NOTIF_NON_LUES);
    const count = data.count || 0;
    const badge = document.getElementById('notif-count');
    if (badge) {
      badge.textContent = count > 99 ? '99+' : count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }
  } catch {}
}

// ── Toggle panneau ────────────────────────────────────────────────────────────
async function toggleNotifPanel() {
  const panel = document.getElementById('notif-panel');
  if (!panel) return;
  if (panel.style.display === 'none' || !panel.style.display) {
    panel.style.display = 'block';
    await loadNotifsList();
  } else {
    panel.style.display = 'none';
  }
}

// ── Charger notifications dans le panel ───────────────────────────────────────
async function loadNotifsList() {
  const list = document.getElementById('notif-list');
  if (!list) return;
  list.innerHTML = '<div style="padding:20px;text-align:center;color:#9ca3af;font-size:13px;">Chargement…</div>';
  try {
    const data   = await API.get(ENDPOINTS.NOTIFICATIONS + '?page_size=15');
    const notifs = Array.isArray(data) ? data : (data.results || []);

    if (!notifs.length) {
      list.innerHTML = '<div style="padding:32px;text-align:center;color:#9ca3af;font-size:14px;">🔕 Aucune notification</div>';
      return;
    }

    list.innerHTML = notifs.map(n => {
      const isCommande = n.type_notification === 'COMMANDE';
      const bg = n.est_lue ? '#fff' : '#eef2ff';
      const dot = n.est_lue ? '' : '<span style="width:8px;height:8px;border-radius:50%;background:#4f46e5;display:inline-block;margin-right:8px;flex-shrink:0;margin-top:4px;"></span>';

      const typeIcon = {
        'COMMANDE'                : '📦',
        'COMMANDE_ACCEPTEE'       : '✅',
        'COMMANDE_REFUSEE'        : '❌',
        'MESSAGE'                 : '💬',
        'FAVORI_DEVENU_DISPONIBLE': '❤️',
        'ADMIN_MESSAGE'           : '📣',
        'ALERTE_SYSTEME'          : '⚠️',
      }[n.type_notification] || '🔔';

      return `
      <div style="padding:14px 16px;border-bottom:1px solid #f9fafb;background:${bg};cursor:pointer;"
           onclick="handleNotifClick(${n.id}, '${n.lien || ''}', ${n.commande || 'null'}, '${n.type_notification}')">
        <div style="display:flex;align-items:flex-start;gap:8px;">
          ${dot}
          <span style="font-size:18px;flex-shrink:0;">${typeIcon}</span>
          <div style="flex:1;min-width:0;">
            <div style="font-size:13px;line-height:1.4;color:#111827;">${n.contenu}</div>
            ${isCommande && n.commande ? `
            <div style="display:flex;gap:8px;margin-top:10px;">
              <button onclick="event.stopPropagation();accepterCommande(${n.commande},this)"
                style="background:#10b981;color:#fff;border:none;padding:6px 14px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;">
                ✅ Accepter
              </button>
              <button onclick="event.stopPropagation();refuserCommande(${n.commande},this)"
                style="background:#ef4444;color:#fff;border:none;padding:6px 14px;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;">
                ❌ Refuser
              </button>
            </div>` : ''}
            <div style="font-size:11px;color:#9ca3af;margin-top:6px;">${timeAgo(n.date_creation)}</div>
          </div>
        </div>
      </div>`;
    }).join('');

    // Marquer toutes comme lues automatiquement
    await marquerToutesLues();

  } catch (e) {
    list.innerHTML = '<div style="padding:20px;text-align:center;color:#ef4444;font-size:13px;">Erreur de chargement</div>';
  }
}

// ── Actions notifications ─────────────────────────────────────────────────────
async function handleNotifClick(notifId, lien, commandeId, type) {
  try { await API.patch(`${ENDPOINTS.NOTIFICATIONS}${notifId}/mark-read/`, {}); } catch {}
  if (lien && lien !== 'null' && lien !== '') {
    document.getElementById('notif-panel').style.display = 'none';
    window.location.href = lien;
  }
}

async function accepterCommande(commandeId, btn) {
  btn.disabled    = true;
  btn.textContent = '…';
  try {
    await API.post(ENDPOINTS.COMMANDE_ACCEPTER(commandeId), {});
    toast('✅ Commande acceptée ! L\'acheteur a été notifié.', 'success');
    await loadNotifsList();
    await loadNotifCount();
  } catch (e) {
    toast(e.message || 'Erreur', 'error');
    btn.disabled    = false;
    btn.textContent = '✅ Accepter';
  }
}

async function refuserCommande(commandeId, btn) {
  btn.disabled    = true;
  btn.textContent = '…';
  try {
    await API.post(ENDPOINTS.COMMANDE_REFUSER(commandeId), {});
    toast('❌ Commande refusée. Le livre est de nouveau disponible.', 'success');
    await loadNotifsList();
    await loadNotifCount();
  } catch (e) {
    toast(e.message || 'Erreur', 'error');
    btn.disabled    = false;
    btn.textContent = '❌ Refuser';
  }
}

async function marquerToutesLues() {
  try {
    await API.post(ENDPOINTS.NOTIF_ALL_READ, {});
    const badge = document.getElementById('notif-count');
    if (badge) badge.style.display = 'none';
  } catch {}
}

function activerOngletNotifs() {
  localStorage.setItem('profil_tab', 'notifs');
}
