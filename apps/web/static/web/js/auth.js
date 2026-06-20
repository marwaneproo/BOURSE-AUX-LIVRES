// ============================================
// Auth — login & register
// ============================================

async function handleLogin(e) {
  e.preventDefault();
  const form = e.target;
  const errorBox = form.querySelector('.form-error');
  const btn = form.querySelector('button[type="submit"]');
  errorBox.classList.remove('active');
  btn.disabled = true; btn.textContent = 'Connexion…';

  try {
    const data = await API.post(ENDPOINTS.LOGIN, {
      username: form.username.value.trim(),
      password: form.password.value,
    });
    // data.user contient id, username, email, nom, prenom renvoyés par CustomTokenObtainPairSerializer
    Auth.setSession(data.access, data.refresh, data.user || { username: form.username.value.trim() });
    toast('Connexion réussie', 'success');
    setTimeout(() => window.location.href = '/accueil/', 600);
  } catch (err) {
    errorBox.textContent = err.message || 'Identifiants incorrects';
    errorBox.classList.add('active');
  } finally {
    btn.disabled = false; btn.textContent = 'Se connecter';
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const form = e.target;
  const errorBox = form.querySelector('.form-error');
  const btn = form.querySelector('button[type="submit"]');
  errorBox.classList.remove('active');

  if (form.password.value !== form.password2.value) {
    errorBox.textContent = 'Les mots de passe ne correspondent pas';
    errorBox.classList.add('active');
    return;
  }
  if (!form.emsi.checked) {
    errorBox.textContent = 'Vous devez confirmer être étudiant EMSI';
    errorBox.classList.add('active');
    return;
  }

  btn.disabled = true; btn.textContent = 'Création…';
  try {
    await API.post(ENDPOINTS.REGISTER, {
      username: form.username.value.trim(),
      email: form.email.value.trim(),
      password: form.password.value,
      nom: form.nom.value.trim(),
      prenom: form.prenom.value.trim(),
      est_acheteur: true,
      est_vendeur: form.vendeur.checked,
    });
    toast('Compte créé, connexion automatique…', 'success');
    // Auto login — récupérer les données complètes user
    const data = await API.post(ENDPOINTS.LOGIN, {
      username: form.username.value.trim(),
      password: form.password.value,
    });
    Auth.setSession(data.access, data.refresh, data.user || {
      username: form.username.value.trim(),
      nom: form.nom.value.trim(),
      prenom: form.prenom.value.trim(),
      email: form.email.value.trim(),
    });
    setTimeout(() => window.location.href = '/accueil/', 600);
  } catch (err) {
    errorBox.textContent = err.message || 'Erreur lors de la création du compte';
    errorBox.classList.add('active');
  } finally {
    btn.disabled = false; btn.textContent = 'Créer mon compte';
  }
}
