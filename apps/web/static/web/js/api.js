const Auth = {
  getAccess() { return localStorage.getItem(STORAGE_KEYS.ACCESS); },
  getRefresh() { return localStorage.getItem(STORAGE_KEYS.REFRESH); },
  getUser() {
    if (Object.prototype.hasOwnProperty.call(window, 'DJANGO_USER')) {
      return window.DJANGO_USER;
    }
    try { return JSON.parse(localStorage.getItem(STORAGE_KEYS.USER) || 'null'); }
    catch { return null; }
  },
  isLogged() { return Boolean(this.getUser()); },
  setSession(access, refresh, user) {
    if (access) localStorage.setItem(STORAGE_KEYS.ACCESS, access);
    if (refresh) localStorage.setItem(STORAGE_KEYS.REFRESH, refresh);
    if (user) localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  },
  clearSession() {
    localStorage.removeItem(STORAGE_KEYS.ACCESS);
    localStorage.removeItem(STORAGE_KEYS.REFRESH);
    localStorage.removeItem(STORAGE_KEYS.USER);
  },
  logout() {
    this.clearSession();
    window.location.href = '/deconnexion/';
  },
  requireAuth() {
    if (!this.isLogged()) {
      this.clearSession();
      window.location.href = '/connexion/';
      return false;
    }
    return true;
  },
};

function getCookie(name) {
  const prefix = name + "=";
  const cookie = document.cookie
    .split(";")
    .map(value => value.trim())
    .find(value => value.startsWith(prefix));
  return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

function addCsrfHeader(headers, method = "GET") {
  if (["POST", "PUT", "PATCH", "DELETE"].indexOf(method.toUpperCase()) === -1) return;
  const csrfToken = getCookie("csrftoken");
  if (csrfToken && headers["X-CSRFToken"] === undefined) {
    headers["X-CSRFToken"] = csrfToken;
  }
}

async function refreshToken() {
  const refresh = Auth.getRefresh();
  if (!refresh) return false;
  try {
    const headers = { "Content-Type": "application/json" };
    addCsrfHeader(headers, "POST");
    const response = await fetch(ENDPOINTS.REFRESH, {
      method: "POST",
      headers,
      credentials: "same-origin",
      body: JSON.stringify({ refresh }),
    });
    if (!response.ok) {
      Auth.clearSession();
      return false;
    }
    const data = await response.json();
    Auth.setSession(data.access, null, null);
    return true;
  } catch {
    return false;
  }
}

async function apiRequest(url, options = {}) {
  const headers = { ...(options.headers || {}) };
  const isFormData = options.body instanceof FormData;
  const method = (options.method || "GET").toUpperCase();

  if (!isFormData && options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  addCsrfHeader(headers, method);

  const token = Auth.getAccess();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response = await fetch(url, { ...options, headers, credentials: "same-origin" });

  if (response.status === 401 && Auth.getRefresh()) {
    const refreshed = await refreshToken();
    if (refreshed) {
      headers.Authorization = `Bearer ${Auth.getAccess()}`;
      response = await fetch(url, { ...options, headers, credentials: "same-origin" });
    } else {
      Auth.clearSession();
      delete headers.Authorization;
      response = await fetch(url, { ...options, headers, credentials: "same-origin" });
    }
  }

  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; }
  catch { data = text; }

  if (!response.ok) {
    let message = `Erreur ${response.status}`;
    if (data && typeof data === 'object') {
      message = Object.entries(data)
        .map(([key, value]) => {
          const values = Array.isArray(value) ? value.join(' ') : String(value);
          return key === 'non_field_errors' ? values : `${key}: ${values}`;
        })
        .join(' • ');
    } else if (typeof data === 'string' && data) {
      message = data;
    }
    const error = new Error(message);
    error.data = data;
    error.status = response.status;
    throw error;
  }

  return data;
}

const API = {
  get: url => apiRequest(url, { method: 'GET' }),
  post: (url, body) => apiRequest(url, { method: 'POST', body: body instanceof FormData ? body : JSON.stringify(body) }),
  put: (url, body) => apiRequest(url, { method: 'PUT', body: body instanceof FormData ? body : JSON.stringify(body) }),
  patch: (url, body) => apiRequest(url, { method: 'PATCH', body: body instanceof FormData ? body : JSON.stringify(body) }),
  delete: url => apiRequest(url, { method: 'DELETE' }),
};
