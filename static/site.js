// Shared header: auth modal, account menu, credits. No third-party trackers.
export const $ = (s, r = document) => r.querySelector(s);
export async function api(path, opts = {}) {
  const r = await fetch(path, { credentials: 'same-origin', ...opts });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || `Request failed (${r.status})`);
  return data;
}
export const postJSON = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
export function msg(el, text, kind = '') { if (el) { el.textContent = text; el.className = 'msg small ' + kind; } }

export const state = { cfg: null, listeners: [] };
let afterAuth = null;

export async function refresh() {
  state.cfg = await api('/api/config');
  const u = state.cfg.user;
  $('#hdr-out').hidden = !!u;
  $('#hdr-in').hidden = !u;
  if (u) {
    $('#hdr-credits').textContent = u.credits;
    $('#hdr-email').textContent = u.email;
    $('#acct-initial').textContent = (u.email || '?')[0];
  }
  document.documentElement.dataset.auth = u ? 'in' : 'out';
  state.listeners.forEach((f) => f(state.cfg));
  return state.cfg;
}
export const onConfig = (f) => state.listeners.push(f);

let mode = 'login';
function setMode(m) {
  mode = m;
  document.querySelectorAll('.tabs button').forEach((b) => b.classList.toggle('on', b.dataset.tab === m));
  $('#auth-title').textContent = m === 'signup' ? 'Create your account' : 'Sign in';
  $('#auth-submit').textContent = m === 'signup' ? 'Create account' : 'Sign in';
  $('#password').autocomplete = m === 'signup' ? 'new-password' : 'current-password';
  msg($('#auth-msg'), '');
}
export function openAuth(m = 'login', then = null, sub = '') {
  afterAuth = then;
  setMode(m);
  $('#auth-sub').textContent = sub || 'Use your email and a password. No email verification needed.';
  const d = $('#auth-modal');
  if (!d.open) d.showModal();
  setTimeout(() => $('#email').focus(), 30);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-auth]').forEach((b) => (b.onclick = () => openAuth(b.dataset.auth)));
  document.querySelectorAll('.tabs button').forEach((b) => (b.onclick = () => setMode(b.dataset.tab)));
  $('#auth-modal').addEventListener('click', (e) => { if (e.target.id === 'auth-modal') e.target.close(); });
  $('#auth-form').onsubmit = async (e) => {
    e.preventDefault();
    const m = $('#auth-msg');
    $('#auth-submit').disabled = true;
    try {
      msg(m, mode === 'signup' ? 'Creating account…' : 'Signing in…');
      await postJSON(`/api/auth/${mode}`, { email: $('#email').value, password: $('#password').value });
      $('#password').value = '';
      $('#auth-modal').close();
      await refresh();
      if (location.pathname === '/login/') location.href = '/#create';
      const f = afterAuth; afterAuth = null;
      if (f) f();
    } catch (err) { msg(m, err.message, 'error'); }
    $('#auth-submit').disabled = false;
  };
  const menu = $('#acct-menu'), btn = $('#acct-btn');
  btn.onclick = (e) => { e.stopPropagation(); menu.hidden = !menu.hidden; btn.setAttribute('aria-expanded', String(!menu.hidden)); };
  document.addEventListener('click', (e) => { if (!menu.hidden && !menu.contains(e.target)) { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); } });
  menu.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => { menu.hidden = true; }));
  $('#hdr-logout').onclick = async () => { menu.hidden = true; await postJSON('/api/auth/logout', {}); await refresh(); };
  const burger = $('#burger'), nav = $('#main-nav');
  burger.onclick = () => { nav.classList.toggle('open'); burger.setAttribute('aria-expanded', String(nav.classList.contains('open'))); };
  nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => nav.classList.remove('open')));
  if (location.pathname === '/login/') openAuth(new URLSearchParams(location.search).get('mode') === 'signup' ? 'signup' : 'login');
  refresh().then(() => { document.documentElement.dataset.ready = '1'; }).catch(() => {});
});
