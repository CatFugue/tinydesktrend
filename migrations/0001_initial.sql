-- tinydesktrend-db initial schema
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  pw_hash TEXT NOT NULL,
  pw_salt TEXT NOT NULL,
  pw_iter INTEGER NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  id_hash TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id),
  expires_at INTEGER NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id);
-- user credits: balance = SUM(delta)
CREATE TABLE IF NOT EXISTS credit_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  delta INTEGER NOT NULL,
  kind TEXT NOT NULL,        -- purchase | job | job_refund | refund_clawback | admin_grant
  reference TEXT NOT NULL,
  note TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(kind, reference)
);
CREATE INDEX IF NOT EXISTS credit_user ON credit_ledger(user_id);
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  pack_id TEXT NOT NULL,
  cents INTEGER NOT NULL,
  credits INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending | paid | refunded | expired
  session_id TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS payment_events (
  id TEXT PRIMARY KEY,
  order_id TEXT,
  type TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  status TEXT NOT NULL,      -- submitting | processing | succeeded | failed | reconcile
  task_id TEXT,
  credits INTEGER NOT NULL,
  supply_centi INTEGER NOT NULL,
  error TEXT,
  video_key TEXT,
  polled_at INTEGER,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  finished_at INTEGER
);
CREATE INDEX IF NOT EXISTS jobs_user ON jobs(user_id, created_at);
CREATE INDEX IF NOT EXISTS jobs_status ON jobs(status);
-- MetaSo supply carved out of the shared balance, in 1/100 MetaSo credits.
-- available = SUM(delta_centi) over counted rows (counted=1).
CREATE TABLE IF NOT EXISTS supply_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  delta_centi INTEGER NOT NULL,
  kind TEXT NOT NULL,        -- allocation | job_reserve | job_release | external_test | adjust
  reference TEXT NOT NULL,
  counted INTEGER NOT NULL DEFAULT 1,
  note TEXT,
  created_at INTEGER NOT NULL,
  UNIQUE(kind, reference)
);
CREATE TABLE IF NOT EXISTS funnel_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event TEXT NOT NULL,       -- signup | first_generation | checkout_opened | paid
  user_id TEXT,
  reference TEXT,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS funnel_event ON funnel_events(event, created_at);
CREATE TABLE IF NOT EXISTS rate_limits (
  key TEXT PRIMARY KEY,
  count INTEGER NOT NULL,
  window_start INTEGER NOT NULL
);
-- seed supply: 3000 MetaSo credits carved for Tiny Desk; earlier sample tests recorded but not counted.
INSERT OR IGNORE INTO supply_ledger(delta_centi, kind, reference, counted, note, created_at)
VALUES (300000, 'allocation', 'initial-2026-10-28', 1, 'Carve-out of shared MetaSo balance for Tiny Desk (Halo can change)', 1793160000);
INSERT OR IGNORE INTO supply_ledger(delta_centi, kind, reference, counted, note, created_at)
VALUES (-35464, 'external_test', 'tinydesk-sample-tests-2026-10-28', 0, 'Tiny Desk 样片测试 2 runs: balance 11491.78 -> 11137.14; already spent, outside the 3000 allocation', 1793160000);
