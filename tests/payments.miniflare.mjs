// Local payment tests (Miniflare 3, mock Stripe, self-signed webhooks, dummy secrets). Run: cd /tmp/mf && npm i miniflare@3 && node <this file>
import { Miniflare } from 'miniflare';
import fs from 'node:fs';
import crypto from 'node:crypto';
const SRC = '/workspace/sites/tinydesktrend';
const WH = 'whsec_' + 'T'.repeat(32), ADMIN = 'adm_' + 'x'.repeat(40);
const B = 'https://tinydesktrend.com';
// ---- mock Stripe ----
const sessions = new Map(); let failNext = null; const created = [];
function form(s) { const o = {}; for (const [k, v] of new URLSearchParams(s)) o[k] = v; return o; }
async function outbound(req) {
  const u = new URL(req.url);
  if (u.hostname !== 'api.stripe.com') return new Response('blocked ' + u.hostname, { status: 599 });
  if (req.method === 'POST' && u.pathname === '/v1/checkout/sessions') {
    const f = form(await req.text()); created.push(f);
    if (failNext) { const e = failNext; failNext = null; return Response.json({ error: { type: 'invalid_request_error', code: 'secret_internal_code', message: e } }, { status: 400 }); }
    const id = 'cs_test_' + crypto.randomBytes(8).toString('hex');
    const meta = {}; for (const k in f) { const m = k.match(/^metadata\[(.+)\]$/); if (m) meta[m[1]] = f[k]; }
    const s = { id, object: 'checkout.session', url: 'https://checkout.stripe.com/c/pay/' + id, client_reference_id: f.client_reference_id, metadata: meta, currency: 'usd',
      amount_total: { starter: 999, plus: 1999, pro: 4999 }[meta.pack_id], payment_status: 'unpaid', status: 'open', payment_intent: null };
    sessions.set(id, s); return Response.json(s);
  }
  const m = u.pathname.match(/^\/v1\/checkout\/sessions\/(cs_\w+)$/);
  if (req.method === 'GET' && m) { const s = sessions.get(m[1]); return s ? Response.json(s) : Response.json({ error: { type: 'invalid_request_error' } }, { status: 404 }); }
  return new Response('unmocked', { status: 598 });
}
const mf = new Miniflare({
  modules: true, modulesRoot: SRC, scriptPath: SRC + '/worker.js', modulesRules: [{ type: 'Text', include: ['**/*.txt'] }],
  compatibilityDate: '2026-10-01', d1Databases: ['DB'], kvNamespaces: ['VIDEOS'],
  bindings: { ADMIN_TOKEN: ADMIN, STRIPE_SECRET_KEY: 'sk_test_' + 'a'.repeat(24), STRIPE_WEBHOOK_SECRET: WH,
    STRIPE_PRICE_STARTER: 'price_teststarter1', STRIPE_PRICE_PLUS: 'price_testplus001', STRIPE_PRICE_PRO: 'price_testpro0001', SOURCE_FILE: 'mm_file://0' },
  outboundService: outbound,
});
const db = await mf.getD1Database('DB');
for (const f of ['0001_initial.sql', '0002_payments_fix.sql']) {
  const sql = fs.readFileSync(`${SRC}/migrations/${f}`, 'utf8').split('\n').map((l) => l.replace(/--.*$/, '')).join('\n');
  for (const st of (sql + '\n').split(/;\s*\n/).map((x) => x.trim()).filter(Boolean)) await db.prepare(st).run();
}
// ---- helpers ----
const results = []; const ok = (name, cond, info = '') => { results.push([name, !!cond]); console.log((cond ? 'PASS ' : 'FAIL ') + name + (info ? '  ' + info : '')); };
const q1 = async (sql, ...a) => (await db.prepare(sql).bind(...a).first());
async function call(path, { method = 'GET', body, cookie, headers = {} } = {}) {
  const h = { Origin: B, ...headers }; if (cookie) h.Cookie = cookie; if (body !== undefined) h['Content-Type'] = 'application/json';
  return mf.dispatchFetch(B + path, { method, headers: h, body: body === undefined ? undefined : JSON.stringify(body), redirect: 'manual' });
}
async function user(tag) {
  const r = await call('/api/auth/signup', { method: 'POST', body: { email: `${tag}@t.test`, password: 'Passw0rd-xyz' } });
  const c = (r.headers.get('set-cookie') || '').split(';')[0]; const u = await q1('SELECT id FROM users WHERE email=?', `${tag}@t.test`); return { cookie: c, id: u.id };
}
const bal = async (uid) => (await q1('SELECT COALESCE(SUM(delta),0) b FROM credit_ledger WHERE user_id=?', uid)).b;
async function buy(u, pack = 'starter') {
  const r = await call('/api/checkout', { method: 'POST', cookie: u.cookie, body: { pack } }); const j = await r.json();
  const s = j.url ? sessions.get(j.url.split('/').pop()) : null; return { r, j, s, order: s ? s.client_reference_id : j.ref };
}
let evn = 0;
async function hook(type, obj, { id, secret = WH, ts } = {}) {
  const ev = { id: id || `evt_${++evn}_${Date.now()}`, type, data: { object: obj } }; const body = JSON.stringify(ev);
  const t = ts || Math.floor(Date.now() / 1000); const sig = crypto.createHmac('sha256', secret).update(`${t}.${body}`).digest('hex');
  const r = await mf.dispatchFetch(B + '/api/stripe/webhook', { method: 'POST', body, headers: { 'Stripe-Signature': `t=${t},v1=${sig}`, 'Content-Type': 'application/json' } });
  return { status: r.status, j: await r.json().catch(() => ({})), id: ev.id };
}
const pay = (s, pi) => { s.payment_status = 'paid'; s.status = 'complete'; s.payment_intent = pi || 'pi_' + s.id.slice(8); return s; };
const ret = (sid) => call('/api/stripe/return?session_id=' + sid);
const cron = async () => { const w = await mf.getWorker(); await w.scheduled({ cron: '* * * * *' }); };
const funnelPaid = async (oid) => (await q1("SELECT COUNT(*) n FROM funnel_events WHERE event='paid' AND reference=?", oid)).n;
const anomalies = async (kind, oid) => (await q1('SELECT COUNT(*) n FROM payment_anomalies WHERE kind=? AND order_id=?', kind, oid)).n;

// ===== tests =====
const u1 = await user('u1');
let o = await buy(u1);
ok('checkout returns checkout.stripe.com url', o.j.url?.startsWith('https://checkout.stripe.com/'));
ok('success_url carries {CHECKOUT_SESSION_ID}', created.at(-1).success_url === 'https://tinydesktrend.com/api/stripe/return?session_id={CHECKOUT_SESSION_ID}');
pay(o.s);
let h = await hook('checkout.session.completed', o.s);
ok('webhook paid -> +300 credits', h.status === 200 && (await bal(u1.id)) === 300, `bal=${await bal(u1.id)}`);
const h2 = await hook('checkout.session.completed', o.s, { id: h.id });
ok('webhook replay (same event id) no double credit', h2.j.duplicate && (await bal(u1.id)) === 300);
await hook('checkout.session.async_payment_succeeded', o.s);
ok('second paid event (new id) no double credit', (await bal(u1.id)) === 300);
let r = await ret(o.s.id);
ok('return after webhook: no double, redirect ?paid=1', r.status === 302 && r.headers.get('location').includes('paid=1') && (await bal(u1.id)) === 300, r.headers.get('location'));
ok('paid funnel counted once', (await funnelPaid(o.order)) === 1);

// bad signature / stale / foreign
ok('bad signature -> 400', (await hook('checkout.session.completed', o.s, { secret: 'whsec_wrong' + 'x'.repeat(30) })).status === 400);
ok('stale timestamp -> 400', (await hook('checkout.session.completed', o.s, { ts: Math.floor(Date.now() / 1000) - 1000 })).status === 400);
const foreign = await hook('checkout.session.completed', { id: 'cs_test_other', payment_status: 'paid', metadata: { site: 'ai-bulin47', order_id: 'o_x' }, amount_total: 999, currency: 'usd' });
ok('other-site event ignored (200, ignored)', foreign.status === 200 && foreign.j.ignored);

// concurrent return + webhook
const u2 = await user('u2'); o = await buy(u2); pay(o.s);
const [a, b] = await Promise.all([ret(o.s.id), hook('checkout.session.completed', o.s)]);
ok('return + webhook concurrent -> credited once', (await bal(u2.id)) === 300 && (await q1("SELECT COUNT(*) n FROM credit_ledger WHERE kind='purchase' AND reference=?", o.order)).n === 1, `bal=${await bal(u2.id)}`);
ok('concurrent: funnel once', (await funnelPaid(o.order)) === 1);

// webhook lost -> return credits
const u3 = await user('u3'); o = await buy(u3); pay(o.s);
r = await ret(o.s.id);
ok('webhook lost: return settles (+300, ?paid=1)', (await bal(u3.id)) === 300 && r.headers.get('location').includes('paid=1'));
const sv = await q1('SELECT status, settled_via, payment_intent, amount_paid FROM orders WHERE id=?', o.order);
ok('order fields set (paid/return/pi/amount)', sv.status === 'paid' && sv.settled_via === 'return' && sv.payment_intent && sv.amount_paid === 999, JSON.stringify(sv));
// return while unpaid -> pending, no anomaly
const u3b = await user('u3b'); o = await buy(u3b);
r = await ret(o.s.id);
ok('return while unpaid -> ?paid=pending, no anomaly', r.headers.get('location').includes('paid=pending') && (await bal(u3b.id)) === 0 && (await anomalies('amount_mismatch', o.order)) === 0);
ok('return with bad session_id -> pending', (await ret('nope')).headers.get('location').includes('paid=pending'));

// cron reconcile
const u4 = await user('u4');
const cA = await buy(u4); pay(cA.s);
const cB = await buy(u4); cB.s.status = 'expired';
const cC = await buy(u4);
const cD = await buy(u4);
const old = Math.floor(Date.now() / 1000);
await db.prepare('UPDATE orders SET created_at=?, updated_at=? WHERE id IN (?,?)').bind(old - 900, old - 900, cA.order, cB.order).run();
await db.prepare('UPDATE orders SET created_at=?, updated_at=? WHERE id=?').bind(old - 26 * 3600, old - 26 * 3600, cC.order).run();
await db.prepare('UPDATE orders SET session_id=NULL, created_at=?, updated_at=? WHERE id=?').bind(old - 900, old - 900, cD.order).run();
await cron();
const st = async (id) => (await q1('SELECT status FROM orders WHERE id=?', id)).status;
ok('cron: paid session settled (+300, via cron)', (await bal(u4.id)) === 300 && (await q1('SELECT settled_via v FROM orders WHERE id=?', cA.order)).v === 'cron');
ok('cron: expired session -> expired', (await st(cB.order)) === 'expired');
ok('cron: >25h pending -> expired', (await st(cC.order)) === 'expired');
ok('cron: no session_id -> failed', (await st(cD.order)) === 'failed');
// open session throttle
const cE = await buy(u4); await db.prepare('UPDATE orders SET created_at=?, updated_at=? WHERE id=?').bind(old - 900, old - 900, cE.order).run();
await cron(); const upd = (await q1('SELECT updated_at u FROM orders WHERE id=?', cE.order)).u;
ok('cron: open session stays pending, re-poll throttled', (await st(cE.order)) === 'pending' && upd >= old - 5);
// late webhook on expired order still credits
pay(cC.s); await hook('checkout.session.completed', cC.s);
ok('late paid webhook on expired order settles', (await st(cC.order)) === 'paid' && (await bal(u4.id)) === 600);

// amount mismatch / session mismatch
const u5 = await user('u5'); o = await buy(u5); pay(o.s); o.s.amount_total = 500;
h = await hook('checkout.session.completed', o.s);
ok('amount mismatch -> no credit, anomaly, 200', h.status === 200 && (await bal(u5.id)) === 0 && (await anomalies('amount_mismatch', o.order)) === 1);
o = await buy(u5); pay(o.s); o.s.metadata.user_id = 'u_attacker';
await hook('checkout.session.completed', o.s);
ok('metadata user mismatch -> no credit, session_mismatch anomaly', (await bal(u5.id)) === 0 && (await anomalies('session_mismatch', o.order)) === 1);
o = await buy(u5); pay(o.s); o.s.currency = 'eur';
await hook('checkout.session.completed', o.s);
ok('currency mismatch -> no credit', (await bal(u5.id)) === 0 && (await anomalies('amount_mismatch', o.order)) === 1);

// checkout create failure
failNext = 'No such price: price_secret_internal';
o = await buy(u5);
const bodyTxt = JSON.stringify(o.j);
ok('stripe create fail -> 502 generic, no raw error', o.r.status === 502 && o.j.error === 'Could not open checkout. Please try again.' && !/price_secret|secret_internal_code|No such/.test(bodyTxt) && /^o_/.test(o.j.ref || ''), bodyTxt);
const fo = await q1('SELECT status, error FROM orders WHERE id=?', o.order);
ok('failed order marked failed with internal error', fo.status === 'failed' && /secret_internal_code/.test(fo.error));

// async payment failed
o = await buy(u5); await hook('checkout.session.async_payment_failed', o.s);
ok('async_payment_failed -> failed', (await st(o.order)) === 'failed');

// refunds (option A)
const u6 = await user('u6'); o = await buy(u6); pay(o.s, 'pi_u6'); await hook('checkout.session.completed', o.s);
const ch = (refunded) => ({ id: 'ch_u6', object: 'charge', payment_intent: 'pi_u6', amount: 999, amount_refunded: refunded, refunded: refunded >= 999, metadata: { ...o.s.metadata } });
const rf1 = await hook('charge.refunded', ch(299));
ok('partial refund 299/999 -> -89, partially_refunded', (await bal(u6.id)) === 211 && (await st(o.order)) === 'partially_refunded', `bal=${await bal(u6.id)}`);
await hook('charge.refunded', ch(299), { id: rf1.id });
await hook('charge.refunded', ch(299));
ok('refund replay (same + new id, same amount) no extra clawback', (await bal(u6.id)) === 211);
await hook('charge.refunded', ch(999));
ok('then full refund -> total -300, bal 0, refunded', (await bal(u6.id)) === 0 && (await st(o.order)) === 'refunded');
await hook('charge.refunded', ch(299));
ok('out-of-order older refund event ignored', (await bal(u6.id)) === 0 && (await q1('SELECT refunded_cents r FROM orders WHERE id=?', o.order)).r === 999);
const u7 = await user('u7'); o = await buy(u7); pay(o.s, 'pi_u7'); await hook('checkout.session.completed', o.s);
await db.prepare("INSERT INTO credit_ledger(user_id,delta,kind,reference,created_at) VALUES(?,?,?,?,?)").bind(u7.id, -200, 'job', 'j_test_u7', old).run();
await hook('charge.refunded', { id: 'ch_u7', payment_intent: 'pi_u7', amount: 999, amount_refunded: 999, refunded: true, metadata: {} });
ok('full refund after spending: floor 0 + clawback_shortfall', (await bal(u7.id)) === 0 && (await anomalies('clawback_shortfall', o.order)) === 1, `bal=${await bal(u7.id)}`);

// disputes (lookup by payment_intent, metadata empty)
const u8 = await user('u8'); const d1o = await buy(u8); pay(d1o.s, 'pi_d1'); await hook('checkout.session.completed', d1o.s);
const d2o = await buy(u8); pay(d2o.s, 'pi_d2'); await hook('checkout.session.completed', d2o.s);
ok('dispute setup: 2 orders = 600', (await bal(u8.id)) === 600);
const dsp = (pi, status) => ({ id: 'dp_' + pi, object: 'dispute', payment_intent: pi, charge: 'ch_' + pi, amount: 999, status, metadata: {} });
const dc = await hook('charge.dispute.created', dsp('pi_d1', 'needs_response'));
ok('dispute.created via payment_intent: holds only that order (300)', dc.status === 200 && (await bal(u8.id)) === 300 && (await st(d1o.order)) === 'disputed', `bal=${await bal(u8.id)}`);
await hook('charge.dispute.created', dsp('pi_d1', 'needs_response'), { id: dc.id });
await hook('charge.dispute.created', dsp('pi_d1', 'needs_response'));
ok('dispute.created replay (same + new id) no extra hold', (await bal(u8.id)) === 300);
const dw = await hook('charge.dispute.closed', dsp('pi_d1', 'won'));
ok('dispute won -> hold returned, order paid', (await bal(u8.id)) === 600 && (await st(d1o.order)) === 'paid');
await hook('charge.dispute.closed', dsp('pi_d1', 'won'), { id: dw.id }); await hook('charge.dispute.closed', dsp('pi_d1', 'won'));
ok('dispute won replay no double return', (await bal(u8.id)) === 600);
await hook('charge.dispute.created', dsp('pi_d2', 'needs_response'));
await hook('charge.dispute.closed', dsp('pi_d2', 'lost'));
ok('dispute lost -> hold kept, dispute_lost', (await bal(u8.id)) === 300 && (await st(d2o.order)) === 'dispute_lost');
const u9 = await user('u9'); o = await buy(u9); pay(o.s, 'pi_d3'); await hook('checkout.session.completed', o.s);
await db.prepare("INSERT INTO credit_ledger(user_id,delta,kind,reference,created_at) VALUES(?,?,?,?,?)").bind(u9.id, -300, 'job', 'j_test_u9', old).run();
await hook('charge.dispute.created', dsp('pi_d3', 'needs_response'));
ok('dispute after spending: hold floors at 0', (await bal(u9.id)) === 0);
const unk = await hook('charge.dispute.created', dsp('pi_unknown', 'needs_response'));
ok('dispute for unknown payment_intent ignored (200)', unk.status === 200 && unk.j.ignored);
ok('dispute anomalies recorded', (await anomalies('dispute_opened', d1o.order)) === 1 && (await anomalies('dispute_closed', d1o.order)) === 1);

// funnel totals
const paidOrders = (await q1("SELECT COUNT(*) n FROM credit_ledger WHERE kind='purchase'")).n;
ok('paid funnel rows == purchases', (await q1("SELECT COUNT(*) n FROM funnel_events WHERE event='paid'")).n === paidOrders, `purchases=${paidOrders}`);

// admin anomalies
ok('anomalies: no token -> 401', (await call('/api/admin/anomalies')).status === 401);
ok('anomalies: wrong token -> 401', (await call('/api/admin/anomalies', { headers: { Authorization: 'Bearer nope' } })).status === 401);
const A = { Authorization: 'Bearer ' + ADMIN };
let an = await (await call('/api/admin/anomalies', { headers: A })).json();
ok('anomalies: with token -> list + open count', an.count > 0 && an.open === an.count && typeof an.anomalies[0].detail === 'object', `open=${an.open}`);
an = await (await call('/api/admin/anomalies?limit=2', { headers: A })).json(); ok('anomalies: ?limit=2', an.count === 2);
an = await (await call(`/api/admin/anomalies?since=${old + 3600}`, { headers: A })).json(); ok('anomalies: ?since=future -> 0', an.count === 0);
await db.prepare('UPDATE payment_anomalies SET resolved=1 WHERE id=(SELECT MIN(id) FROM payment_anomalies)').run();
an = await (await call('/api/admin/anomalies?open=1', { headers: A })).json(); const all = await (await call('/api/admin/anomalies?limit=500', { headers: A })).json();
ok('anomalies: ?open=1 excludes resolved', an.count === all.count - 1 && an.anomalies.every((x) => x.resolved === 0));
fs.writeFileSync('/tmp/mf/anomalies-sample.json', JSON.stringify((await (await call('/api/admin/anomalies?limit=2', { headers: A })).json()), null, 1));

// regression: auth + config + no generation called
ok('config ok', (await (await call('/api/config')).json()).payments === true);
ok('logout ok', (await call('/api/auth/logout', { method: 'POST', cookie: u1.cookie, body: {} })).status === 200);
const failed = results.filter((x) => !x[1]); console.log(`\n${results.length - failed.length}/${results.length} passed`); if (failed.length) console.log('FAILED:', failed.map((x) => x[0]));
await mf.dispose();
