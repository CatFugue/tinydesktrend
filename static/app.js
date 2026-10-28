// Tiny Desk AI generator front end. No third-party trackers.
const $ = (s, r = document) => r.querySelector(s);
const FFMPEG_WASM = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.10/dist/esm/ffmpeg-core.wasm';
let cfg = null;
let photoOk = false;

async function api(path, opts = {}) {
  const r = await fetch(path, { credentials: 'same-origin', ...opts });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || `Request failed (${r.status})`);
  return data;
}
const postJSON = (path, body) => api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
function msg(el, text, kind = '') { el.textContent = text; el.className = 'msg ' + kind; }

async function loadConfig() {
  cfg = await api('/api/config');
  const acct = $('#account');
  if (cfg.user) {
    $('#auth-forms').hidden = true;
    $('#signed-in').hidden = false;
    $('#who').textContent = cfg.user.email;
    $('#credits').textContent = cfg.user.credits;
  } else {
    $('#auth-forms').hidden = false;
    $('#signed-in').hidden = true;
  }
  $('#sold-out').hidden = !cfg.soldOut;
  $('#buy').disabled = !cfg.payments;
  updateGenerate();
  if (cfg.user) loadHistory();
  acct.dataset.ready = '1';
}
function updateGenerate() {
  const b = $('#generate');
  const ok = cfg && cfg.user && cfg.generator && !cfg.soldOut && photoOk && $('#consent').checked;
  b.disabled = !ok;
  const hint = $('#gen-hint');
  if (!cfg) return;
  if (!cfg.user) hint.textContent = 'Create a free account or log in to generate.';
  else if (cfg.soldOut) hint.textContent = 'Sold out for now. Please check back soon.';
  else if (cfg.user.credits < cfg.videoCredits) hint.textContent = `You have ${cfg.user.credits} credits. A video costs ${cfg.videoCredits}. Pick a pack below.`;
  else hint.textContent = `Uses ${cfg.videoCredits} credits. You have ${cfg.user.credits}.`;
}

// ---- auth ----
async function auth(kind) {
  const m = $('#auth-msg');
  try {
    msg(m, kind === 'signup' ? 'Creating account…' : 'Logging in…');
    await postJSON(`/api/auth/${kind}`, { email: $('#email').value, password: $('#password').value });
    msg(m, '');
    await loadConfig();
  } catch (e) { msg(m, e.message, 'error'); }
}

// ---- face check (MediaPipe BlazeFace, runs in your browser) ----
let detector = null;
async function getDetector() {
  if (detector) return detector;
  const { FilesetResolver, FaceDetector } = await import('/vendor/mediapipe/vision_bundle.mjs');
  const files = await FilesetResolver.forVisionTasks('/vendor/mediapipe/wasm');
  detector = await FaceDetector.createFromOptions(files, {
    baseOptions: { modelAssetPath: '/vendor/mediapipe/blaze_face_short_range.tflite', delegate: 'CPU' },
    runningMode: 'IMAGE', minDetectionConfidence: 0.5,
  });
  return detector;
}
async function checkPhoto(file) {
  const m = $('#photo-msg');
  photoOk = false; updateGenerate();
  if (!file) return;
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 10 * 1024 * 1024) {
    msg(m, 'Use a JPEG, PNG or WebP photo up to 10 MB.', 'error'); return;
  }
  const img = $('#preview');
  img.src = URL.createObjectURL(file);
  img.hidden = false;
  await img.decode().catch(() => {});
  msg(m, 'Checking for a face…');
  try {
    const d = await Promise.race([getDetector(), new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 45000))]);
    const faces = d.detect(img).detections || [];
    if (!faces.length) { msg(m, 'No face found. Use a clear, front-facing photo of one person.', 'error'); return; }
    const w = faces.map((f) => f.boundingBox.width).sort((a, b) => b - a);
    photoOk = true;
    msg(m, w.length > 1 && w[1] >= w[0] / 2 ? 'Face found. Tip: one person per photo works best.' : 'Face found. Looks good.', 'ok');
  } catch (e) {
    msg(m, 'Face check could not run in this browser. Try another browser.', 'error');
  }
  updateGenerate();
}

// ---- generation ----
async function generate() {
  const st = $('#gen-status');
  $('#generate').disabled = true;
  try {
    const fd = new FormData();
    fd.append('photo', $('#photo').files[0]);
    fd.append('consent', $('#consent').checked ? 'yes' : '');
    msg(st, 'Uploading…');
    const r = await fetch('/api/jobs', { method: 'POST', body: fd, credentials: 'same-origin' });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error || 'Could not start.');
    localStorage.setItem('td_job', j.id);
    await loadConfig();
    poll(j.id);
  } catch (e) { msg(st, e.message, 'error'); updateGenerate(); }
}
async function poll(id) {
  const st = $('#gen-status');
  const t0 = Date.now();
  for (;;) {
    let j;
    try { j = await api(`/api/jobs/${id}`); } catch (e) { msg(st, e.message, 'error'); return; }
    if (j.status === 'succeeded' && j.hasVideo) { localStorage.removeItem('td_job'); await finish(id); loadConfig(); return; }
    if (j.status === 'failed') { localStorage.removeItem('td_job'); msg(st, 'The video could not be made. Your credits were refunded.', 'error'); loadConfig(); return; }
    if (j.status === 'reconcile') { msg(st, 'This is taking longer than usual. Your credits were refunded; if the video still arrives it will show up under "Your videos".', 'error'); loadConfig(); return; }
    msg(st, `Making your video… ${Math.round((Date.now() - t0) / 1000)} s (usually about 2 minutes). You can leave this page open.`);
    await new Promise((r) => setTimeout(r, 8000));
  }
}

// ---- ffmpeg.wasm: trim to exactly 13.000 s (312 frames at 24 fps), add the song / make a silent copy ----
let ff = null;
async function getFFmpeg() {
  if (ff) return ff;
  const { FFmpeg } = await import('/vendor/ffmpeg/index.js');
  const f = new FFmpeg();
  await f.load({ coreURL: new URL('/vendor/ffcore/ffmpeg-core.js', location.href).href, wasmURL: FFMPEG_WASM });
  ff = f;
  return ff;
}
async function finish(id) {
  const st = $('#gen-status');
  const out = $('#result');
  msg(st, 'Video ready. Preparing the song and silent versions in your browser…');
  const raw = new Uint8Array(await (await fetch(`/api/jobs/${id}/video`, { credentials: 'same-origin' })).arrayBuffer());
  const rawUrl = URL.createObjectURL(new Blob([raw], { type: 'video/mp4' }));
  out.hidden = false;
  $('#dl-raw').href = rawUrl;
  try {
    const f = await getFFmpeg();
    const song = new Uint8Array(await (await fetch('/media/outstanding-0-13.m4a')).arrayBuffer());
    await f.writeFile('raw.mp4', raw);
    await f.writeFile('song.m4a', song);
    await f.exec(['-i', 'raw.mp4', '-map', '0:v:0', '-an', '-frames:v', '312', '-t', '13', '-c', 'copy', '-movflags', '+faststart', 'silent.mp4']);
    await f.exec(['-i', 'silent.mp4', '-i', 'song.m4a', '-map', '0:v:0', '-map', '1:a:0', '-t', '13', '-c', 'copy', '-movflags', '+faststart', 'song.mp4']);
    const a = await f.readFile('song.mp4');
    const b = await f.readFile('silent.mp4');
    if (a.length < 1000 || b.length < 1000) throw new Error('empty output');
    const songUrl = URL.createObjectURL(new Blob([a.buffer], { type: 'video/mp4' }));
    $('#dl-song').href = songUrl;
    $('#dl-song').hidden = false;
    $('#dl-silent').href = URL.createObjectURL(new Blob([b.buffer], { type: 'video/mp4' }));
    $('#dl-silent').hidden = false;
    $('#result-video').src = songUrl;
    msg(st, 'Done! Download the version with the song, or the silent copy for apps that mute music.', 'ok');
  } catch (e) {
    console.error(e);
    $('#result-video').src = rawUrl;
    msg(st, 'Your video is ready, but this browser could not add the song. Download the original file below.', 'error');
  }
}

async function loadHistory() {
  try {
    const m = await api('/api/me');
    const list = $('#history');
    list.innerHTML = '';
    for (const j of m.jobs) {
      const li = document.createElement('li');
      li.textContent = `${new Date(j.createdAt * 1000).toLocaleString()} · ${j.status}`;
      if (j.hasVideo) {
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'link'; b.textContent = 'Open';
        b.onclick = () => finish(j.id);
        li.append(' · ', b);
      }
      list.append(li);
    }
    $('#history-wrap').hidden = !m.jobs.length;
  } catch {}
}

async function buy() {
  const m = $('#buy-msg');
  const pack = document.querySelector('input[name="pack"]:checked')?.value || 'starter';
  if (!cfg?.user) { msg(m, 'Create a free account or log in first (top of the page).', 'error'); $('#create').scrollIntoView(); return; }
  try { msg(m, 'Opening secure checkout…'); const r = await postJSON('/api/checkout', { pack }); location.href = r.url; }
  catch (e) { msg(m, e.message, 'error'); }
}

document.addEventListener('DOMContentLoaded', () => {
  $('#signup').onclick = () => auth('signup');
  $('#login').onclick = () => auth('login');
  $('#logout').onclick = async () => { await postJSON('/api/auth/logout', {}); loadConfig(); };
  $('#photo').onchange = (e) => checkPhoto(e.target.files[0]);
  $('#consent').onchange = updateGenerate;
  $('#generate').onclick = generate;
  $('#buy').onclick = buy;
  const q = new URLSearchParams(location.search);
  if (q.get('paid')) msg($('#gen-status'), 'Payment received. Credits appear here within a minute.', 'ok');
  loadConfig().then(() => { const j = localStorage.getItem('td_job'); if (j && cfg.user) poll(j); }).catch(() => {});
});
