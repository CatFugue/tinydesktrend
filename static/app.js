// Tiny Desk AI generator (homepage). No third-party trackers.
import { $, api, postJSON, msg as _msg, state, refresh, onConfig, openAuth } from '/site.js';
const FFMPEG_WASM = 'https://cdn.jsdelivr.net/npm/@ffmpeg/core@0.12.10/dist/esm/ffmpeg-core.wasm';
let photoOk = false;
const msg = (el, t, k = '') => { el.textContent = t; el.className = 'msg ' + k; };
const cfgOf = () => state.cfg;

onConfig((cfg) => {
  $('#sold-out').hidden = !cfg.soldOut;
  updateGenerate();
  if (cfg.user) loadHistory(); else $('#videos').hidden = true;
  $('#account').dataset.ready = '1';
});
function updateGenerate() {
  const cfg = cfgOf();
  const b = $('#generate');
  b.disabled = !(cfg && cfg.generator && !cfg.soldOut && photoOk && $('#consent').checked);
  const hint = $('#gen-hint');
  if (!cfg) return;
  if (cfg.soldOut) hint.textContent = 'Sold out for now. Please check back soon.';
  else if (!photoOk) hint.textContent = 'Choose a photo to start.';
  else if (!$('#consent').checked) hint.textContent = 'Tick the permission box to continue.';
  else if (!cfg.user) hint.textContent = 'You will be asked to sign in or create a free account.';
  else if (cfg.user.credits < cfg.videoCredits) hint.textContent = `You have ${cfg.user.credits} credits. Pick a pack to continue.`;
  else hint.textContent = `You have ${cfg.user.credits} credits.`;
}
function needCredits() {
  const cfg = cfgOf();
  msg($('#buy-msg'), `A video costs ${cfg.videoCredits} credits and you have ${cfg.user.credits}. Pick a pack, then come back to Generate.`, 'error');
  $('#pricing').scrollIntoView({ behavior: 'smooth' });
}
function onGenerate() {
  const cfg = cfgOf();
  if (!cfg.user) return openAuth('signup', onGenerate, 'Create a free account (or sign in) to generate your video. Your photo stays selected.');
  if (cfg.user.credits < cfg.videoCredits) return needCredits();
  generate();
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
// Pin the accepted photo onto the sample as a "now on lead" sticker.
function castOnLead(src) {
  const cast = $('#cast');
  if (!cast) return;
  if (src) $('#cast-img').src = src;
  cast.classList.toggle('on', !!src);
  $('#lead-tag').classList.toggle('peeled', !!src);
  $('#drop').classList.toggle('cast-on', !!src);
  $('#see-sample').hidden = !src;
}
async function checkPhoto(file) {
  const m = $('#photo-msg');
  photoOk = false; updateGenerate(); castOnLead(null);
  if (!file) return;
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 10 * 1024 * 1024) {
    msg(m, 'Use a JPEG, PNG or WebP photo up to 10 MB.', 'error'); return;
  }
  const img = $('#preview');
  img.src = URL.createObjectURL(file);
  img.hidden = false;
  $('#drop-text b').textContent = 'Change photo';
  await img.decode().catch(() => {});
  msg(m, 'Checking for a face…');
  try {
    const d = await Promise.race([getDetector(), new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 45000))]);
    const faces = d.detect(img).detections || [];
    if (!faces.length) { msg(m, 'No face found. Use a clear, front-facing photo of one person.', 'error'); return; }
    const w = faces.map((f) => f.boundingBox.width).sort((a, b) => b - a);
    photoOk = true;
    castOnLead(img.src);
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
    await refresh();
    poll(j.id);
  } catch (e) { msg(st, e.message, 'error'); updateGenerate(); }
}
async function poll(id) {
  const st = $('#gen-status');
  const t0 = Date.now();
  for (;;) {
    let j;
    try { j = await api(`/api/jobs/${id}`); } catch (e) { msg(st, e.message, 'error'); return; }
    if (j.status === 'succeeded' && j.hasVideo) { localStorage.removeItem('td_job'); await finish(id); refresh(); return; }
    if (j.status === 'failed') { localStorage.removeItem('td_job'); msg(st, 'The video could not be made. Your credits were refunded.', 'error'); refresh(); return; }
    if (j.status === 'reconcile') { msg(st, 'This is taking longer than usual. Your credits were refunded; if the video still arrives it will show up under "My videos".', 'error'); refresh(); return; }
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
        b.onclick = () => { finish(j.id); $('#result').scrollIntoView({ behavior: 'smooth', block: 'center' }); };
        li.append(' · ', b);
      }
      list.append(li);
    }
    $('#videos').hidden = !m.jobs.length;
  } catch {}
}

async function buy(pack) {
  const m = $('#buy-msg');
  const cfg = cfgOf();
  if (!cfg?.payments) return msg(m, 'Payments are not available right now.', 'error');
  if (!cfg.user) return openAuth('signup', () => buy(pack), 'Create a free account (or sign in) to buy credits.');
  try { msg(m, 'Opening secure checkout…'); const r = await postJSON('/api/checkout', { pack }); location.href = r.url; }
  catch (e) { msg(m, e.message, 'error'); }
}

function openVideos() { const d = $('#videos'); if (!d.hidden) { d.open = true; d.scrollIntoView({ behavior: 'smooth', block: 'center' }); } }
document.addEventListener('DOMContentLoaded', () => {
  // Sample video: autoplay unless the visitor prefers reduced motion; authored play/pause and sound stickers.
  const v = $('.phone video'), play = $('#sample-play'), sound = $('#sample-sound');
  const showPlaying = (on) => {
    play.classList.toggle('paused', !on);
    play.setAttribute('aria-pressed', String(!on));
    play.setAttribute('aria-label', on ? 'Pause sample' : 'Play sample');
  };
  v.addEventListener('play', () => showPlaying(true));
  v.addEventListener('pause', () => showPlaying(false));
  showPlaying(false);
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    // Only fetch and play the sample once it is on screen.
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { io.disconnect(); v.play().catch(() => {}); }
    });
    io.observe(v);
  }
  play.onclick = () => (v.paused ? v.play().catch(() => {}) : v.pause());
  sound.onclick = () => {
    v.muted = !v.muted;
    if (!v.muted) v.play().catch(() => {});
    sound.setAttribute('aria-pressed', String(!v.muted));
    sound.querySelector('span').textContent = v.muted ? 'Sound on' : 'Sound off';
  };
  $('#photo').onchange = (e) => checkPhoto(e.target.files[0]);
  $('#consent').onchange = updateGenerate;
  $('#generate').onclick = onGenerate;
  document.querySelectorAll('.buy').forEach((b) => (b.onclick = () => buy(b.dataset.pack)));
  document.querySelectorAll('[data-menu="videos"]').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); openVideos(); }));
  const q = new URLSearchParams(location.search);
  if (q.get('paid')) msg($('#gen-status'), 'Payment received. Credits appear in the top-right corner within a minute.', 'ok');
  const t = setInterval(() => { if (cfgOf()) { clearInterval(t); if (location.hash === '#videos') openVideos(); const j = localStorage.getItem('td_job'); if (j && cfgOf().user) poll(j); } }, 200);
});
