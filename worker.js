// tinydesktrend Worker: static assets + email/password auth + credits + Stripe Checkout + MetaSo H3 recast jobs.
// Bindings: ASSETS (static), DB (D1 tinydesktrend-db), VIDEOS (KV). Secrets: METASO_API_KEY, STRIPE_SECRET_KEY,
// STRIPE_WEBHOOK_SECRET, ADMIN_TOKEN. Vars: STRIPE_PRICE_STARTER/PLUS/PRO, SOURCE_FILE.
// Provider/Stripe logic adapted from CatFugue/ai-bulin47 worker/providers/metaso.ts and worker/payments/stripe.ts.
import PROMPT from './prompt.txt';

const SITE = 'tinydesktrend';
const ORIGINS = ['https://tinydesktrend.com', 'https://tinydesktrend.yininglian.workers.dev'];
const VIDEO_CREDITS = 100;
const SUPPLY_CENTI = 17732; // 177.32 MetaSo credits per 13 s 480p recast
const PACKS = {
  starter: { cents: 999, credits: 300, env: 'STRIPE_PRICE_STARTER', name: 'Starter' },
  plus: { cents: 1999, credits: 700, env: 'STRIPE_PRICE_PLUS', name: 'Plus' },
  pro: { cents: 4999, credits: 1800, env: 'STRIPE_PRICE_PRO', name: 'Pro' },
};
const H3 = 'https://metaso.cn/api/minimax';
const STRIPE_VERSION = '2026-09-30.endive';
const SESSION_DAYS = 30;
const VIDEO_TTL = 7 * 86400;
const JOB_TIMEOUT = 20 * 60;
const PBKDF2_ITER = 100000;
const now = () => Math.floor(Date.now() / 1000);
const enc = new TextEncoder();
const hex = (buf) => [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, '0')).join('');
const rid = (n = 16) => hex(crypto.getRandomValues(new Uint8Array(n)));
const sha256 = async (s) => hex(await crypto.subtle.digest('SHA-256', enc.encode(s)));
const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...headers } });
const err = (status, error) => json({ error }, status);

const CSP = [
  "default-src 'self'",
  "script-src 'self' 'wasm-unsafe-eval' blob:",
  "worker-src 'self' blob:",
  "connect-src 'self' https://cdn.jsdelivr.net blob: data:",
  "img-src 'self' data: blob:",
  "media-src 'self' blob:",
  "style-src 'self'",
  "font-src 'self'",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self' https://checkout.stripe.com",
].join('; ');
function secure(res) {
  const h = new Headers(res.headers);
  h.set('X-Content-Type-Options', 'nosniff');
  h.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  h.set('X-Frame-Options', 'DENY');
  h.set('Content-Security-Policy', CSP);
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
}

// ---------- auth ----------
async function pbkdf2(password, saltHex, iter) {
  const key = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveBits']);
  const salt = new Uint8Array(saltHex.match(/../g).map((x) => parseInt(x, 16)));
  return hex(await crypto.subtle.deriveBits({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: iter }, key, 256));
}
async function safeEqual(a, b) {
  const [x, y] = await Promise.all([sha256(a), sha256(b)]);
  let d = 0;
  for (let i = 0; i < x.length; i++) d |= x.charCodeAt(i) ^ y.charCodeAt(i);
  return d === 0;
}
function cookie(req, name) {
  const c = req.headers.get('Cookie') || '';
  for (const part of c.split(';')) {
    const [k, ...v] = part.trim().split('=');
    if (k === name) return v.join('=');
  }
  return null;
}
const sessionCookie = (token, maxAge) =>
  `td_session=${token}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
async function currentUser(req, env) {
  const t = cookie(req, 'td_session');
  if (!t || !/^[a-f0-9]{64}$/.test(t)) return null;
  return env.DB.prepare(
    'SELECT u.id, u.email FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.id_hash = ? AND s.expires_at > ?',
  ).bind(await sha256(t), now()).first();
}
async function newSession(env, userId) {
  const token = rid(32);
  await env.DB.prepare('INSERT INTO sessions(id_hash, user_id, expires_at, created_at) VALUES(?,?,?,?)')
    .bind(await sha256(token), userId, now() + SESSION_DAYS * 86400, now()).run();
  return sessionCookie(token, SESSION_DAYS * 86400);
}
async function limited(env, key, max, windowSec) {
  const t = now();
  const row = await env.DB.prepare(
    `INSERT INTO rate_limits(key, count, window_start) VALUES(?1, 1, ?2)
     ON CONFLICT(key) DO UPDATE SET count = CASE WHEN window_start <= ?2 - ?3 THEN 1 ELSE count + 1 END,
       window_start = CASE WHEN window_start <= ?2 - ?3 THEN ?2 ELSE window_start END
     RETURNING count`,
  ).bind(key, t, windowSec).first();
  return row.count > max;
}
const ip = (req) => req.headers.get('CF-Connecting-IP') || 'unknown';
const funnel = (env, event, userId, ref) =>
  env.DB.prepare('INSERT INTO funnel_events(event, user_id, reference, created_at) VALUES(?,?,?,?)').bind(event, userId, ref || null, now()).run();

async function signup(req, env) {
  if (await limited(env, `signup:${ip(req)}`, 10, 3600)) return err(429, 'Too many sign-ups from this network. Try again later.');
  const b = await req.json().catch(() => ({}));
  const email = String(b.email || '').trim().toLowerCase();
  const password = String(b.password || '');
  if (!/^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,}$/.test(email)) return err(400, 'Enter a valid email address.');
  if (password.length < 8 || password.length > 200) return err(400, 'Use a password of at least 8 characters.');
  const salt = rid(16);
  const id = 'u_' + rid(12);
  try {
    await env.DB.prepare('INSERT INTO users(id, email, pw_hash, pw_salt, pw_iter, created_at) VALUES(?,?,?,?,?,?)')
      .bind(id, email, await pbkdf2(password, salt, PBKDF2_ITER), salt, PBKDF2_ITER, now()).run();
  } catch {
    return err(409, 'An account with this email already exists. Log in instead.');
  }
  await funnel(env, 'signup', id);
  return json({ ok: true, email }, 200, { 'Set-Cookie': await newSession(env, id) });
}
async function login(req, env) {
  if (await limited(env, `login:${ip(req)}`, 30, 600)) return err(429, 'Too many attempts. Wait a few minutes.');
  const b = await req.json().catch(() => ({}));
  const email = String(b.email || '').trim().toLowerCase();
  const u = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
  const ok = u && (await safeEqual(await pbkdf2(String(b.password || ''), u.pw_salt, u.pw_iter), u.pw_hash));
  if (!ok) return err(401, 'Email or password is incorrect.');
  return json({ ok: true, email }, 200, { 'Set-Cookie': await newSession(env, u.id) });
}
async function logout(req, env) {
  const t = cookie(req, 'td_session');
  if (t) await env.DB.prepare('DELETE FROM sessions WHERE id_hash = ?').bind(await sha256(t)).run();
  return json({ ok: true }, 200, { 'Set-Cookie': sessionCookie('', 0) });
}

// ---------- credits / supply ----------
const balance = async (env, userId) =>
  (await env.DB.prepare('SELECT COALESCE(SUM(delta),0) AS b FROM credit_ledger WHERE user_id = ?').bind(userId).first()).b;
const supplyAvailable = async (env) =>
  (await env.DB.prepare('SELECT COALESCE(SUM(delta_centi),0) AS s FROM supply_ledger WHERE counted = 1').first()).s;
const credit = (env, userId, delta, kind, ref, note) =>
  env.DB.prepare('INSERT OR IGNORE INTO credit_ledger(user_id, delta, kind, reference, note, created_at) VALUES(?,?,?,?,?,?)')
    .bind(userId, delta, kind, ref, note || null, now()).run();
const supply = (env, delta, kind, ref, note) =>
  env.DB.prepare('INSERT OR IGNORE INTO supply_ledger(delta_centi, kind, reference, counted, note, created_at) VALUES(?,?,?,1,?,?)')
    .bind(delta, kind, ref, note || null, now()).run();

async function config(req, env) {
  const user = await currentUser(req, env);
  const avail = await supplyAvailable(env);
  const payments = !!(await getSecret(env, 'STRIPE_SECRET_KEY')) && !!(await getSecret(env, 'STRIPE_WEBHOOK_SECRET')) && (await Promise.all(Object.values(PACKS).map((p) => getSecret(env, p.env)))).every(Boolean);
  return json({
    payments,
    soldOut: avail < SUPPLY_CENTI,
    generator: !!(await getSecret(env, 'METASO_API_KEY')) && !!env.SOURCE_FILE,
    videoCredits: VIDEO_CREDITS,
    packs: Object.entries(PACKS).map(([id, p]) => ({ id, name: p.name, cents: p.cents, credits: p.credits, videos: Math.floor(p.credits / VIDEO_CREDITS) })),
    user: user ? { email: user.email, credits: await balance(env, user.id) } : null,
  });
}
async function me(req, env) {
  const user = await currentUser(req, env);
  if (!user) return err(401, 'Log in first.');
  const jobs = await env.DB.prepare('SELECT id, status, error, created_at, finished_at, video_key FROM jobs WHERE user_id = ? ORDER BY created_at DESC LIMIT 10').bind(user.id).all();
  return json({
    email: user.email,
    credits: await balance(env, user.id),
    jobs: jobs.results.map((j) => ({ id: j.id, status: j.status, error: j.error, createdAt: j.created_at, hasVideo: !!j.video_key && j.finished_at > now() - VIDEO_TTL })),
  });
}

// ---------- secrets stored encrypted in KV (fallback when a secret binding could not be set) ----------
const secretCache = {};
async function aesKey(env, name) {
  const raw = await crypto.subtle.digest('SHA-256', enc.encode(`${env.ADMIN_TOKEN}:${name}`));
  return crypto.subtle.importKey('raw', raw, 'AES-GCM', false, ['encrypt', 'decrypt']);
}
const validSecret = {
  STRIPE_SECRET_KEY: (v) => /^(sk|rk)_(live|test)_[A-Za-z0-9]{20,}$/.test(v || ''),
  STRIPE_WEBHOOK_SECRET: (v) => /^whsec_[A-Za-z0-9+/=]{20,}$/.test(v || ''),
  STRIPE_PRICE_STARTER: (v) => /^price_[A-Za-z0-9]{8,}$/.test(v || ''),
  STRIPE_PRICE_PLUS: (v) => /^price_[A-Za-z0-9]{8,}$/.test(v || ''),
  STRIPE_PRICE_PRO: (v) => /^price_[A-Za-z0-9]{8,}$/.test(v || ''),
  METASO_API_KEY: (v) => (v || '').trim().length >= 20,
};
// Encrypted KV value (cfg/<name>, set via /api/admin/secret) wins over the Worker binding, so a
// value can be rotated without redeploying; the binding is the fallback.
async function getSecret(env, name) {
  const c = secretCache[name];
  if (c && Date.now() - c.t < 60000) return c.v;
  const blob = env.ADMIN_TOKEN ? await env.VIDEOS.get(`cfg/${name}`, 'arrayBuffer') : null;
  if (blob) {
    try {
      const b = new Uint8Array(blob);
      const pt = new TextDecoder().decode(await crypto.subtle.decrypt({ name: 'AES-GCM', iv: b.slice(0, 12) }, await aesKey(env, name), b.slice(12)));
      if (validSecret[name](pt)) { secretCache[name] = { v: pt, t: Date.now() }; return pt; }
    } catch {}
  }
  return validSecret[name](env[name]) ? env[name].trim() : null;
}
async function putSecret(env, name, value) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, await aesKey(env, name), enc.encode(value)));
  const out = new Uint8Array(12 + ct.length); out.set(iv); out.set(ct, 12);
  await env.VIDEOS.put(`cfg/${name}`, out);
  secretCache[name] = { v: value, t: Date.now() };
}

// ---------- Stripe ----------
async function checkout(req, env) {
  const user = await currentUser(req, env);
  if (!user) return err(401, 'Log in or create an account first.');
  const b = await req.json().catch(() => ({}));
  const pack = PACKS[b.pack];
  if (!pack) return err(400, 'Choose a credit pack.');
  const price = await getSecret(env, pack.env);
  const stripeKey = await getSecret(env, 'STRIPE_SECRET_KEY');
  if (!stripeKey || !price) return err(503, 'Payments are not available right now.');
  if (await limited(env, `checkout:${user.id}`, 20, 3600)) return err(429, 'Too many checkout attempts. Try again later.');
  const orderId = 'o_' + rid(12);
  await env.DB.prepare('INSERT INTO orders(id, user_id, pack_id, cents, credits, status, created_at, updated_at) VALUES(?,?,?,?,?,?,?,?)')
    .bind(orderId, user.id, b.pack, pack.cents, pack.credits, 'pending', now(), now()).run();
  const meta = { site: SITE, order_id: orderId, user_id: user.id, pack_id: b.pack, credits: String(pack.credits) };
  const body = new URLSearchParams();
  body.set('mode', 'payment');
  body.set('client_reference_id', orderId);
  body.set('success_url', 'https://tinydesktrend.com/?paid=1#create');
  body.set('cancel_url', 'https://tinydesktrend.com/?canceled=1#pricing');
  body.set('line_items[0][price]', price);
  body.set('line_items[0][quantity]', '1');
  body.set('customer_email', user.email);
  for (const [k, v] of Object.entries(meta)) {
    body.set(`metadata[${k}]`, v);
    body.set(`payment_intent_data[metadata][${k}]`, v);
  }
  const r = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${stripeKey}`,
      'Content-Type': 'application/x-www-form-urlencoded',
      'Idempotency-Key': `order:${orderId}`,
      'Stripe-Version': STRIPE_VERSION,
    },
    body,
  });
  const s = await r.json().catch(() => ({}));
  if (r.status !== 200 || typeof s.url !== 'string' || !s.url.startsWith('https://checkout.stripe.com/')) {
    console.error(JSON.stringify({ event: 'stripe_checkout_failed', status: r.status, code: s.error?.code }));
    return json({ error: 'Could not open checkout. Please try again.', code: s.error?.code || s.error?.type || r.status, detail: String(s.error?.message || '').slice(0, 160) }, 502);
  }
  await env.DB.prepare('UPDATE orders SET session_id = ?, updated_at = ? WHERE id = ?').bind(s.id, now(), orderId).run();
  await funnel(env, 'checkout_opened', user.id, orderId);
  return json({ url: s.url });
}
async function verifyStripe(body, header, secret) {
  if (!secret || !header) return false;
  let t = '';
  const sigs = [];
  for (const part of header.split(',')) {
    const i = part.indexOf('=');
    if (i < 0) continue;
    const k = part.slice(0, i).trim(), v = part.slice(i + 1).trim();
    if (k === 't') t = v;
    else if (k === 'v1') sigs.push(v);
  }
  if (!/^\d{10}$/.test(t) || !sigs.length || Math.abs(now() - Number(t)) > 300) return false;
  const key = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const expected = hex(await crypto.subtle.sign('HMAC', key, enc.encode(`${t}.${body}`)));
  let ok = false;
  for (const s of sigs) if (await safeEqual(s, expected)) ok = true;
  return ok;
}
async function webhook(req, env) {
  const body = await req.text();
  if (!(await verifyStripe(body, req.headers.get('Stripe-Signature'), await getSecret(env, 'STRIPE_WEBHOOK_SECRET')))) return err(400, 'Invalid signature.');
  let ev;
  try { ev = JSON.parse(body); } catch { return err(400, 'Invalid event.'); }
  const obj = ev?.data?.object || {};
  const meta = obj.metadata || {};
  if (meta.site !== SITE) return json({ received: true, ignored: true }); // other sites on the same Stripe account
  const orderId = meta.order_id || obj.client_reference_id;
  const order = orderId ? await env.DB.prepare('SELECT * FROM orders WHERE id = ?').bind(orderId).first() : null;
  const payEvent = ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded' || ev.type === 'charge.refunded';
  if (!order) return payEvent ? err(500, 'Order not found yet.') : json({ received: true, ignored: true });
  const seen = await env.DB.prepare('SELECT id FROM payment_events WHERE id = ?').bind(ev.id).first();
  if (seen) return json({ received: true, duplicate: true });
  const record = env.DB.prepare('INSERT OR IGNORE INTO payment_events(id, order_id, type, created_at) VALUES(?,?,?,?)').bind(ev.id, order.id, ev.type, now());
  const t = now();
  if (ev.type === 'checkout.session.completed' || ev.type === 'checkout.session.async_payment_succeeded') {
    if (obj.payment_status !== 'paid') { await record.run(); return json({ received: true }); }
    if (String(obj.currency).toLowerCase() !== 'usd' || typeof obj.amount_total !== 'number' || obj.amount_total < order.cents ||
        meta.user_id !== order.user_id || meta.credits !== String(order.credits)) {
      console.error(JSON.stringify({ event: 'stripe_mismatch', id: ev.id, order: order.id }));
      return err(500, 'Order mismatch.');
    }
    await env.DB.batch([
      record,
      env.DB.prepare("UPDATE orders SET status='paid', updated_at=? WHERE id=? AND status='pending'").bind(t, order.id),
      env.DB.prepare("INSERT OR IGNORE INTO credit_ledger(user_id, delta, kind, reference, note, created_at) SELECT user_id, credits, 'purchase', id, pack_id, ? FROM orders WHERE id=? AND status='paid'").bind(t, order.id),
      env.DB.prepare("INSERT INTO funnel_events(event, user_id, reference, created_at) VALUES('paid', ?, ?, ?)").bind(order.user_id, order.id, t),
    ]);
  } else if (ev.type === 'charge.refunded') {
    const full = obj.refunded === true || (obj.amount > 0 && obj.amount_refunded >= obj.amount);
    if (!full) { await record.run(); return json({ received: true }); }
    await env.DB.batch([
      record,
      env.DB.prepare("UPDATE orders SET status='refunded', updated_at=? WHERE id=? AND status='paid'").bind(t, order.id),
      env.DB.prepare("INSERT OR IGNORE INTO credit_ledger(user_id, delta, kind, reference, note, created_at) SELECT user_id, -credits, 'refund_clawback', id, 'stripe full refund', ? FROM orders WHERE id=? AND status='refunded'").bind(t, order.id),
    ]);
  } else if (ev.type === 'checkout.session.expired') {
    await env.DB.batch([record, env.DB.prepare("UPDATE orders SET status='expired', updated_at=? WHERE id=? AND status='pending'").bind(t, order.id)]);
  } else {
    await record.run();
  }
  return json({ received: true });
}

// ---------- MetaSo H3 ----------
class H3Error extends Error {
  constructor(msg, status, definite) { super(msg); this.status = status; this.definite = definite; }
}
async function h3(env, path, init) {
  let r;
  try {
    r = await fetch(H3 + path, {
      ...init,
      redirect: 'manual',
      signal: AbortSignal.timeout(60000),
      headers: { Authorization: `Bearer ${await getSecret(env, 'METASO_API_KEY')}`, Accept: 'application/json', ...(init.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }) },
    });
  } catch (e) {
    throw new H3Error('transport', 0, false);
  }
  const text = await r.text();
  let data = null;
  try { data = JSON.parse(text); } catch {}
  if (!r.ok) throw new H3Error(`http_${r.status}:${text.slice(0, 200)}`, r.status, r.status >= 400 && r.status < 500);
  if (!data || data.error || (data.base_resp && data.base_resp.status_code !== 0))
    throw new H3Error(`api_error:${text.slice(0, 200)}`, r.status, true);
  return data;
}
async function h3Upload(env, file) {
  const form = new FormData();
  form.append('purpose', 'video_generation_input');
  form.append('file', file, 'photo.' + (file.type.split('/')[1] || 'jpg'));
  const d = await h3(env, '/v1/files/upload', { method: 'POST', body: form });
  const id = d.file?.file_id;
  if ((typeof id === 'string' && /^\d+$/.test(id)) || (typeof id === 'number' && id > 0)) return `mm_file://${id}`;
  throw new H3Error('upload_no_file_id', 200, true);
}
async function h3Submit(env, photoRef) {
  const payload = {
    model: 'MiniMax-H3',
    content: [
      { type: 'text', text: PROMPT.trim() },
      { type: 'image_url', role: 'reference_image', image_url: { url: photoRef } },
      { type: 'video_url', role: 'reference_video', video_url: { url: env.SOURCE_FILE } },
    ],
    resolution: '480p',
    duration: 13,
    ratio: '9:16',
    fast_mode: false,
    context_ir_enabled: false,
  };
  const d = await h3(env, '/v2/video_generation', { method: 'POST', body: JSON.stringify(payload) });
  const id = d.task_id ?? d.task?.id ?? d.task?.task_id;
  if (!/^[a-zA-Z0-9_-]{1,255}$/.test(String(id ?? ''))) throw new H3Error('submit_no_task_id', 200, false);
  return String(id);
}
async function h3Query(env, id) {
  const d = await h3(env, `/v2/query/video_generation/${encodeURIComponent(id)}`, { method: 'GET' });
  const t = d.task ?? d;
  const s = String(t.status || '').toLowerCase();
  if (['queued', 'pending', 'running', 'processing'].includes(s)) return { status: 'processing' };
  if (['succeeded', 'success', 'completed'].includes(s)) return { status: 'succeeded', url: t.content?.url, usage: t.usage };
  if (['failed', 'failure', 'cancelled', 'canceled'].includes(s)) return { status: 'failed', reason: String(t.error?.message || t.fail_reason || s).slice(0, 200) };
  return { status: 'unknown' };
}

// ---------- jobs ----------
async function refundJob(env, job, reason, releaseSupply) {
  await credit(env, job.user_id, job.credits, 'job_refund', job.id, reason);
  if (releaseSupply) await supply(env, job.supply_centi, 'job_release', job.id, reason);
}
async function createJob(req, env) {
  const user = await currentUser(req, env);
  if (!user) return err(401, 'Log in first.');
  if (!(await getSecret(env, 'METASO_API_KEY')) || !env.SOURCE_FILE) return err(503, 'The generator is not available right now.');
  const form = await req.formData().catch(() => null);
  if (!form) return err(400, 'Upload a photo.');
  if (form.get('consent') !== 'yes') return err(400, 'Confirm the photo is of you or someone who agreed.');
  const photo = form.get('photo');
  if (!(photo instanceof File) || !['image/jpeg', 'image/png', 'image/webp'].includes(photo.type) || photo.size <= 0 || photo.size > 10 * 1024 * 1024)
    return err(400, 'Use a JPEG, PNG or WebP photo up to 10 MB.');
  const active = await env.DB.prepare("SELECT COUNT(*) AS n FROM jobs WHERE user_id = ? AND status IN ('submitting','processing')").bind(user.id).first();
  if (active.n >= 2) return err(429, 'You already have 2 videos in progress. Wait for one to finish.');
  if (await limited(env, `job:${user.id}`, 15, 3600)) return err(429, 'Too many videos this hour. Try again a little later.');
  const id = 'j_' + rid(12);
  const t = now();
  const prior = await env.DB.prepare('SELECT COUNT(*) AS n FROM jobs WHERE user_id = ?').bind(user.id).first();
  await env.DB.prepare('INSERT INTO jobs(id, user_id, status, credits, supply_centi, created_at, updated_at) VALUES(?,?,?,?,?,?,?)')
    .bind(id, user.id, 'submitting', VIDEO_CREDITS, SUPPLY_CENTI, t, t).run();
  const fail = (status, msg, code) => env.DB.prepare("UPDATE jobs SET status='failed', error=?, updated_at=?, finished_at=? WHERE id=?").bind(code, now(), now(), id).run().then(() => err(status, msg));
  const res = await env.DB.prepare(
    "INSERT INTO supply_ledger(delta_centi, kind, reference, counted, note, created_at) SELECT ?, 'job_reserve', ?, 1, NULL, ? WHERE (SELECT COALESCE(SUM(delta_centi),0) FROM supply_ledger WHERE counted = 1) >= ?",
  ).bind(-SUPPLY_CENTI, id, t, SUPPLY_CENTI).run();
  if (!res.meta.changes) return fail(409, 'Sold out for now. No credits were used. Please check back soon.', 'sold_out');
  const deb = await env.DB.prepare(
    "INSERT INTO credit_ledger(user_id, delta, kind, reference, note, created_at) SELECT ?, ?, 'job', ?, NULL, ? WHERE (SELECT COALESCE(SUM(delta),0) FROM credit_ledger WHERE user_id = ?) >= ?",
  ).bind(user.id, -VIDEO_CREDITS, id, t, user.id, VIDEO_CREDITS).run();
  if (!deb.meta.changes) {
    await supply(env, SUPPLY_CENTI, 'job_release', id, 'insufficient_credits');
    return fail(402, `You need ${VIDEO_CREDITS} credits for a video. Buy a pack below.`, 'insufficient_credits');
  }
  const job = { id, user_id: user.id, credits: VIDEO_CREDITS, supply_centi: SUPPLY_CENTI };
  let photoRef;
  try {
    photoRef = await h3Upload(env, photo);
  } catch (e) {
    console.error(JSON.stringify({ event: 'h3_upload_failed', job: id, msg: e.message }));
    await refundJob(env, job, 'upload_failed', true);
    return fail(502, 'Could not send your photo to the video service. Your credits were refunded.', 'upload_failed');
  }
  let taskId;
  try {
    taskId = await h3Submit(env, photoRef);
  } catch (e) {
    console.error(JSON.stringify({ event: 'h3_submit_failed', job: id, msg: e.message, definite: e.definite }));
    await refundJob(env, job, 'submit_failed', !!e.definite);
    if (!e.definite) {
      await env.DB.prepare("UPDATE jobs SET status='reconcile', error='submit_unconfirmed', updated_at=? WHERE id=?").bind(now(), id).run();
      return err(502, 'The video service did not confirm your request. Your credits were refunded.');
    }
    return fail(502, 'The video service rejected this request (it may not accept this photo). Your credits were refunded.', 'submit_rejected');
  }
  await env.DB.prepare("UPDATE jobs SET status='processing', task_id=?, updated_at=?, polled_at=? WHERE id=?").bind(taskId, now(), now(), id).run();
  if (!prior.n) await funnel(env, 'first_generation', user.id, id);
  return json({ id, status: 'processing' });
}
async function pollJob(env, job) {
  if (!job.task_id || !['processing', 'reconcile'].includes(job.status)) return job;
  await env.DB.prepare('UPDATE jobs SET polled_at = ? WHERE id = ?').bind(now(), job.id).run();
  let q;
  try { q = await h3Query(env, job.task_id); } catch (e) { q = { status: 'unknown', reason: e.message }; }
  const t = now();
  if (q.status === 'succeeded' && q.url) {
    try {
      const u = new URL(q.url);
      if (u.protocol !== 'https:') throw new Error('bad_url');
      const r = await fetch(q.url, { signal: AbortSignal.timeout(60000) });
      if (!r.ok) throw new Error(`fetch_${r.status}`);
      const buf = await r.arrayBuffer();
      if (buf.byteLength < 1000 || buf.byteLength > 50 * 1024 * 1024) throw new Error('bad_size');
      const key = `v/${job.id}.mp4`;
      await env.VIDEOS.put(key, buf, { expirationTtl: VIDEO_TTL });
      await env.DB.prepare("UPDATE jobs SET status='succeeded', video_key=?, error=NULL, updated_at=?, finished_at=? WHERE id=?").bind(key, t, t, job.id).run();
      return { ...job, status: 'succeeded', video_key: key, finished_at: t };
    } catch (e) {
      console.error(JSON.stringify({ event: 'video_copy_failed', job: job.id, msg: e.message }));
      return job;
    }
  }
  if (q.status === 'failed') {
    await refundJob(env, job, 'provider_failed', true);
    await env.DB.prepare("UPDATE jobs SET status='failed', error=?, updated_at=?, finished_at=? WHERE id=?").bind('provider_failed', t, t, job.id).run();
    return { ...job, status: 'failed', error: 'provider_failed' };
  }
  if (job.status === 'processing' && t - job.created_at > JOB_TIMEOUT) {
    // Timed out: refund the user, keep supply reserved until reconciled; never resubmit automatically.
    await credit(env, job.user_id, job.credits, 'job_refund', job.id, 'timeout');
    await env.DB.prepare("UPDATE jobs SET status='reconcile', error='timeout', updated_at=? WHERE id=?").bind(t, job.id).run();
    return { ...job, status: 'reconcile', error: 'timeout' };
  }
  return job;
}
const publicJob = (j) => ({ id: j.id, status: j.status, error: j.error || null, hasVideo: !!j.video_key });
async function getJob(req, env, id) {
  const user = await currentUser(req, env);
  if (!user) return err(401, 'Log in first.');
  let job = await env.DB.prepare('SELECT * FROM jobs WHERE id = ? AND user_id = ?').bind(id, user.id).first();
  if (!job) return err(404, 'Not found.');
  if (['processing', 'reconcile'].includes(job.status) && now() - (job.polled_at || 0) >= 8) job = await pollJob(env, job);
  return json(publicJob(job));
}
async function getVideo(req, env, id) {
  const user = await currentUser(req, env);
  if (!user) return err(401, 'Log in first.');
  const job = await env.DB.prepare('SELECT video_key FROM jobs WHERE id = ? AND user_id = ?').bind(id, user.id).first();
  if (!job?.video_key) return err(404, 'Not found.');
  const v = await env.VIDEOS.get(job.video_key, 'stream');
  if (!v) return err(410, 'This video has expired (kept 7 days).');
  return new Response(v, { headers: { 'Content-Type': 'video/mp4', 'Cache-Control': 'private, no-store', 'Content-Disposition': `inline; filename="tiny-desk-${id}.mp4"` } });
}

// ---------- admin ----------
async function admin(req, env, path) {
  const auth = req.headers.get('Authorization') || '';
  if (!env.ADMIN_TOKEN || !(await safeEqual(auth, `Bearer ${env.ADMIN_TOKEN}`))) return err(401, 'Unauthorized.');
  if (path === '/api/admin/grant' && req.method === 'POST') {
    const b = await req.json();
    const u = await env.DB.prepare('SELECT id FROM users WHERE email = ?').bind(String(b.email || '').toLowerCase()).first();
    if (!u || !Number.isInteger(b.credits)) return err(400, 'user/credits');
    await credit(env, u.id, b.credits, 'admin_grant', String(b.reference || rid(8)), String(b.note || ''));
    return json({ ok: true, credits: await balance(env, u.id) });
  }
  if (path === '/api/admin/supply' && req.method === 'POST') {
    const b = await req.json();
    if (!Number.isInteger(b.delta_centi) || !['allocation', 'adjust'].includes(b.kind) || !b.reference) return err(400, 'delta_centi/kind/reference');
    await supply(env, b.delta_centi, b.kind, String(b.reference), String(b.note || ''));
  }
  if (path === '/api/admin/supply') {
    const rows = await env.DB.prepare('SELECT * FROM supply_ledger ORDER BY id').all();
    return json({ availableCredits: (await supplyAvailable(env)) / 100, rows: rows.results });
  }
  if (path === '/api/admin/secret' && req.method === 'POST') {
    const b = await req.json();
    if (!validSecret[b.name] || !validSecret[b.name](b.value)) return err(400, 'name/value');
    await putSecret(env, b.name, String(b.value).trim());
    return json({ ok: true });
  }
  if (path === '/api/admin/diag') {
    const k = (await getSecret(env, 'STRIPE_SECRET_KEY')) || '';
    const m = (await getSecret(env, 'METASO_API_KEY')) || '';
    return json({ stripeLen: k.length, stripeHash: (await sha256(k)).slice(0, 12), metasoLen: m.length, metasoHash: (await sha256(m)).slice(0, 12), whHash: (await sha256((await getSecret(env, 'STRIPE_WEBHOOK_SECRET')) || '')).slice(0, 12), prices: await Promise.all(Object.values(PACKS).map((p) => getSecret(env, p.env))) });
  }
  if (path === '/api/admin/funnel') {
    const rows = await env.DB.prepare('SELECT event, COUNT(*) AS n FROM funnel_events GROUP BY event').all();
    return json(rows.results);
  }
  return err(404, 'Not found.');
}

async function cron(env) {
  const jobs = await env.DB.prepare(
    "SELECT * FROM jobs WHERE (status = 'processing' OR (status = 'reconcile' AND task_id IS NOT NULL AND created_at > ?)) AND (polled_at IS NULL OR polled_at < ?) ORDER BY created_at LIMIT 10",
  ).bind(now() - 86400, now() - 30).all();
  for (const j of jobs.results) await pollJob(env, j);
  await env.DB.prepare('DELETE FROM sessions WHERE expires_at < ?').bind(now()).run();
  await env.DB.prepare('DELETE FROM rate_limits WHERE window_start < ?').bind(now() - 86400).run();
}

async function api(req, env, url) {
  const p = url.pathname;
  if (req.method === 'POST' && p !== '/api/stripe/webhook' && !p.startsWith('/api/admin/')) {
    const o = req.headers.get('Origin');
    if (!o || !ORIGINS.includes(o)) return err(403, 'Bad origin.');
  }
  if (p === '/api/config' && req.method === 'GET') return config(req, env);
  if (p === '/api/me' && req.method === 'GET') return me(req, env);
  if (p === '/api/auth/signup' && req.method === 'POST') return signup(req, env);
  if (p === '/api/auth/login' && req.method === 'POST') return login(req, env);
  if (p === '/api/auth/logout' && req.method === 'POST') return logout(req, env);
  if (p === '/api/checkout' && req.method === 'POST') return checkout(req, env);
  if (p === '/api/stripe/webhook' && req.method === 'POST') return webhook(req, env);
  if (p === '/api/jobs' && req.method === 'POST') return createJob(req, env);
  let m = p.match(/^\/api\/jobs\/(j_[a-f0-9]{24})$/);
  if (m && req.method === 'GET') return getJob(req, env, m[1]);
  m = p.match(/^\/api\/jobs\/(j_[a-f0-9]{24})\/video$/);
  if (m && req.method === 'GET') return getVideo(req, env, m[1]);
  if (p.startsWith('/api/admin/')) return admin(req, env, p);
  return err(404, 'Not found.');
}

export default {
  async fetch(req, env) {
    const u = new URL(req.url);
    if (u.hostname === 'www.tinydesktrend.com') {
      u.hostname = 'tinydesktrend.com';
      return Response.redirect(u.toString(), 301);
    }
    if (u.pathname.startsWith('/api/')) {
      try {
        return secure(await api(req, env, u));
      } catch (e) {
        console.error(JSON.stringify({ event: 'api_error', path: u.pathname, msg: String(e?.message || e).slice(0, 300) }));
        return secure(err(500, 'Something went wrong. Please try again.'));
      }
    }
    const r = await env.ASSETS.fetch(req);
    if (r.status === 307 || r.status === 308) {
      const loc = r.headers.get('Location');
      if (loc) return Response.redirect(new URL(loc, u).toString(), 301);
    }
    return secure(r);
  },
  async scheduled(_event, env, ctx) {
    ctx.waitUntil(cron(env));
  },
};
