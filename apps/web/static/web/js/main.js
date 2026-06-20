// ============================================
// Utilitaires partagés
// ============================================

function initHeaderScroll() {
  const header = document.querySelector('.header:not(.connected)');
  if (!header) return;
  const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 30);
  window.addEventListener('scroll', onScroll);
  onScroll();
}

function toast(message, type = '') {
  let el = document.querySelector('.toast');
  if (!el) {
    el = document.createElement('div');
    el.className = 'toast';
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.className = `toast ${type} show`;
  setTimeout(() => el.classList.remove('show'), 3000);
}

function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('active');
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('active');
}
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) e.target.classList.remove('active');
  if (e.target.dataset.modalOpen)  openModal(e.target.dataset.modalOpen);
  if (e.target.dataset.modalClose) closeModal(e.target.dataset.modalClose);
});

function formatPrice(p) {
  if (p == null || p === 0 || p === '0') return 'Gratuit';
  return `${parseFloat(p).toFixed(2)} DH`;
}

function initials(name = '') {
  return name.trim().split(/\s+/).map(s => s[0]).slice(0, 2).join('').toUpperCase() || '?';
}

function timeAgo(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const diff = (Date.now() - d.getTime()) / 1000;
  if (diff < 60)    return 'à l\'instant';
  if (diff < 3600)  return `${Math.floor(diff/60)} min`;
  if (diff < 86400) return `${Math.floor(diff/3600)} h`;
  if (diff < 2592000) return `${Math.floor(diff/86400)} j`;
  return d.toLocaleDateString('fr-FR');
}

// Render le slot utilisateur si le header HTML est déjà présent
function renderConnectedHeader() {
  const user = Auth.getUser() || window.DJANGO_USER;
  const slot = document.querySelector('.user-slot');
  if (slot && user) {
    const nom = `${user.prenom || user.first_name || ''} ${user.nom || user.last_name || ''}`.trim() || user.username || 'Utilisateur';
    slot.innerHTML = `
      <a href="/profil/" class="icon-btn" title="${nom}">${initials(nom)}</a>
      <button class="icon-btn" title="Déconnexion" onclick="Auth.logout()">⎋</button>
    `;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  initHeaderScroll();
  renderConnectedHeader();
});

// Résout l'URL complète d'une image de livre (image_url absolu prioritaire,
// sinon on reconstruit depuis MEDIA_URL)
function resolveImg(imgObj) {
  if (!imgObj) return null;
  if (imgObj.image_url) return imgObj.image_url;
  if (!imgObj.image)    return null;
  if (imgObj.image.startsWith('http')) return imgObj.image;
  return CONFIG.MEDIA_URL.replace(/\/$/, '') + '/' + imgObj.image.replace(/^\//, '');
}
