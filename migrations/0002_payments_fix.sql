-- DRAFT (fix/payments) — 未在生产执行。见 docs/payments-fix-plan.md
-- 1) 订单补充对账字段
ALTER TABLE orders ADD COLUMN payment_intent TEXT;          -- pi_...，dispute / refund 反查订单用
ALTER TABLE orders ADD COLUMN amount_paid INTEGER;          -- Stripe amount_total（美分）
ALTER TABLE orders ADD COLUMN refunded_cents INTEGER NOT NULL DEFAULT 0;  -- 累计退款额（来自 charge.amount_refunded）
ALTER TABLE orders ADD COLUMN settled_via TEXT;             -- webhook | return | cron
ALTER TABLE orders ADD COLUMN error TEXT;                   -- 创建 Checkout 失败等的内部原因（不回前端）
CREATE INDEX IF NOT EXISTS orders_pi ON orders(payment_intent);
CREATE INDEX IF NOT EXISTS orders_status ON orders(status, created_at);
-- status 取值扩展为：pending | paid | failed | expired | refunded | partially_refunded | disputed | dispute_lost

-- 2) paid 漏斗去重（每个订单只记一次）
CREATE UNIQUE INDEX IF NOT EXISTS funnel_paid_once ON funnel_events(event, reference) WHERE event = 'paid';

-- 3) 付款异常记录（金额不符、退款扣分不足、争议等），admin 可查
CREATE TABLE IF NOT EXISTS payment_anomalies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT,
  kind TEXT NOT NULL,        -- amount_mismatch | clawback_shortfall | dispute_opened | dispute_closed | orphan_event
  detail TEXT,               -- JSON，不含卡号/密钥
  resolved INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS anomalies_open ON payment_anomalies(resolved, created_at);

-- 4) 账户冻结（第 6 条选项 B / 第 7 条争议期间用；选项 A 不用也可保留）
ALTER TABLE users ADD COLUMN frozen_at INTEGER;
ALTER TABLE users ADD COLUMN frozen_reason TEXT;
