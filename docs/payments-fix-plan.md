# tinydesktrend.com 付款修复方案（草稿，仅方案）

- 日期：2026-11-01（JST）
- 范围：`worker.js` 中 Stripe 下单、webhook、对账、退款和争议处理，以及 `static/app.js` 的支付回跳提示。
- 状态：**未部署，线上和 Stripe 设置都没动。** 草稿只放在本地分支 `fix/payments`，包括本文档和 `migrations/0002_payments_fix.sql`。
- 代码基准：`main` 分支的 `9b2d1b0`。下文行号以该版本为准，和站点经营看到的版本可能有偏移。
- 模板对照：**已对照** ShipAny TanStack 模板（用户电脑 `E:\Projects\shipany-tanstack`，只读，先读了 AGENTS.md 定位）。
  看过的文件：
  - `src/routes/api/payment/checkout.ts`
  - `src/routes/api/payment/callback.ts`
  - `src/modules/payment/service.ts`
  - `src/core/payment/stripe.ts`
  - `src/modules/credits/service.ts`
  - `src/modules/notify/service.ts`

> 先说结论：模板最值得移植的是两样。
> 1. **"回跳页向 Stripe 查单"和"webhook"共用同一个结算函数。**
> 2. **结算时用"带状态条件的原子更新 + 每个订单只发一次积分"做幂等。**
>
> 第 3 条（清理旧单）、第 5 条（异步付款失败）、第 6 条里的部分退款、第 7 条（争议）、第 8 条（报错原文），模板在 Stripe 这条路径上**也没有处理**，这几条按 Stripe 最佳实践补。

---

## 1（中）回跳不对账，webhook 失败时付了钱拿不到积分

**当前代码：问题存在。**
- `checkout()`（约 L229）的 `success_url` 写死为 `https://tinydesktrend.com/?paid=1#create`，没有带 `{CHECKOUT_SESSION_ID}`。
- 积分只在 `webhook()`（L275–318）里发。webhook 一旦没送达，或返回 500，用户就只能等 Stripe 重试，而且没有任何补单途径。
- 金额不符时返回 500（L293–297）。Stripe 会一直重试，最多约 3 天，但没有记录，也没有报警。

**模板怎么做：**
- 下单时把 `success_url` 设成 `/api/payment/callback?order_no=<订单号>&redirect=<同源路径>`（`modules/payment/service.ts` 里的 `createCheckout`）。
- `callback.ts` 先调 `handlePaymentCallback(orderNo)`：订单已经 PAID 就直接返回；否则用 `provider.getPaymentSession()`，也就是 `checkout.sessions.retrieve`，向 Stripe 查最新状态，再交给**和 webhook 同一个** `handleCheckoutSuccess` → `settleCheckoutOrder` 处理。最后 302 跳到同源页面。
- `settleCheckoutOrder` 的关键是把下面几步放进同一个事务：
  - 更新订单时带条件 `WHERE status IN (created, pending)`；
  - 发积分用唯一的 `transactionNo = grant_<orderNo>`，并且检查"该订单还没有 grant 记录"；
  - 并发时只有一个调用方能提交成功，另一个视为"已结算"，安静返回。
- 金额校验：模板**只对支付宝和微信**做严格的金额相等校验，Stripe 这条路径不校验金额。
- 报警：`notifyPaymentSuccess` 只在付款成功时发 bot 通知，没有"金额不符"的报警。

**我们怎么移植：**
1. 把 `success_url` 改成 `https://tinydesktrend.com/api/stripe/return?session_id={CHECKOUT_SESSION_ID}`。我们是直接拼给 Stripe 的字符串，花括号要原样传过去。订单号已经写在 `client_reference_id` 和 metadata 里，不必再放进 URL。
2. 新增 `GET /api/stripe/return`：
   - 校验 `session_id` 格式（`cs_(live|test)_…`）。
   - 用 `getSecret('STRIPE_SECRET_KEY')` 调 `GET /v1/checkout/sessions/{id}`。现有受限密钥已经证明能读 session（2026-10-28 验证过）。
   - 用 `client_reference_id` 找到订单后调 `settleOrder(env, order, session, 'return')`。
   - 无论结果如何，都 302 到 `/?paid=1#create`（失败时用 `?paid=pending`）。前端提示改成"已到账"或"处理中"。
   - **不要求登录态**：结算只依据 Stripe 返回的数据，回跳本身不发任何东西给访问者，所以不会泄露信息。
3. 把 webhook 里的结算逻辑抽成 `settleOrder()`，webhook、回跳、cron（见第 3 条）三处共用：
   - 在一个 `DB.batch` 里依次执行：
     - `UPDATE orders SET status='paid', payment_intent=?, amount_paid=?, settled_via=? WHERE id=? AND status IN ('pending','failed','expired')`
     - 加积分：`INSERT OR IGNORE INTO credit_ledger … kind='purchase', reference=order.id`。已有的 `UNIQUE(kind, reference)` 保证每单只发一次，相当于模板的 `grant_<orderNo>`。
     - paid 漏斗用 `INSERT OR IGNORE`（见第 4 条）。
   - 允许从 `failed`/`expired` 补成 `paid`，是为了处理"异步付款最终到账"和"本地已标过期、实际已付"这两种边界情况。前提是 Stripe 显示 `payment_status='paid'`。
4. 金额或币种不符时：
   - 不发积分；
   - 写一行 `payment_anomalies(kind='amount_mismatch', detail={expected, got, currency, session})`；
   - 打 `console.error`，Workers Logs 里能检索到；
   - webhook **返回 200**。否则 Stripe 会白白重试 3 天，而且我们已经记下了。
   - 报警方式需要用户拍板（见文末）。默认先做 `GET /api/admin/anomalies`，并在 admin 漏斗接口里显示未处理的异常数。
5. 规则保持现状：`amount_total >= order.cents` 且币种为 usd。目前没开优惠码和自动税；以后如果开了自动税，`amount_total` 会大于标价，这条规则依然成立。

- 是否需要 D1 迁移：需要。`orders` 加 `payment_intent`、`amount_paid`、`settled_via`，新建 `payment_anomalies` 表（见草稿 0002）。
- 是否需要改 Stripe 事件：不需要。

## 2（低）先插订单，Stripe 创建失败不回滚，留下脏 pending

**当前代码：问题存在。** L223 先 `INSERT orders(status='pending')`。L249–252 Stripe 失败时直接返回 502，订单一直停在 pending。

**模板怎么做：** 先调 `pm.createPayment()` 创建 Checkout，**成功后**才 `insert(order)`，并把 sessionId 一起写进去。所以 Stripe 失败不会留下订单。

**我们怎么移植：** 保留"先插订单"的顺序，因为 orderId 要当 Idempotency-Key 和 metadata，先插可以避免"Stripe 已建单、本地没有记录"。失败时改为：
`UPDATE orders SET status='failed', error=? WHERE id=? AND status='pending'`。
`error` 只存 Stripe 的 `code` 和 `type`，不回前端。这和模板等价，而且比模板多一个优点：网络超时后，如果 Stripe 其实已经建好了 session，cron 也能用 orderId 找回来。

- 是否需要 D1 迁移：需要，`orders.error`（草稿 0002）。

## 3（低）cron 不清理超过 24 小时的 pending

**当前代码：问题存在。** `cron()`（L535）只轮询生成任务、清理会话和限流记录，不碰 `orders`。

**模板怎么做：** 没有清理任务。模板靠 `checkout.session.expired` 映射成 CANCELED 来处理，而且 Stripe 适配器里 `mapStripeEventType` 并没有订阅 expired。

**我们怎么移植：** 在 `cron()` 里加 `reconcileOrders(env)`，每分钟最多处理 10 单：
- `pending` 且创建于 10 分钟到 25 小时前、有 `session_id`：调 `GET /v1/checkout/sessions/{id}`。
  - 显示 `paid` → `settleOrder(…,'cron')`。这是 webhook 和回跳都失败时的**第三道补单**。
  - 显示 `expired` → 标 `expired`。
  - 显示 `open` → 跳过。
- `pending` 超过 25 小时：Checkout 默认 24 小时过期。仍为 open 或查不到就标 `expired`；没有 `session_id` 的标 `failed`。
- 需要给 orders 加一个 `polled_at` 列或用 `updated_at` 做节流，避免每分钟反复查同一单。草稿里直接复用 `updated_at` 加条件，不另加列。

- 是否需要 D1 迁移：只要加 `orders_status` 索引（草稿 0002）。
- 是否需要改 Stripe 事件：不需要。

## 4（低）paid 漏斗事件无条件插入，可能重复计数

**当前代码：问题存在。** L302 在 batch 里无条件 `INSERT INTO funnel_events('paid', …)`。只要同一订单收到两个都带 `payment_status=paid` 的不同事件，就会重复计数。例如 `completed` 之后又来 `async_payment_succeeded`，或者以后加了回跳补单，回跳和 webhook 各结算一次。

**模板怎么做：** 用条件更新加 `onConflict` 判断"本次是否真的完成了结算"。只有真正提交的调用方才执行 `notifyPaymentSuccess`，相当于"副作用只做一次"。

**我们怎么移植：**
- 加部分唯一索引：`funnel_events(event, reference) WHERE event='paid'`。
- paid 漏斗改用 `INSERT OR IGNORE`。
- 上线前要清理已有的重复数据（目前生产还没有真实的 paid 记录，预计为空）。

- 是否需要 D1 迁移：需要（草稿 0002 第 2 段）。

## 5（低）async_payment_failed 不改订单状态

**当前代码：问题存在。** 这个事件落到 L314 的 `else` 分支，只记了 `payment_events`，订单一直停在 pending。

**模板怎么做：** `settleCheckoutOrder` 遇到 `PaymentStatus.FAILED` 或 `CANCELED` 时，把订单从 created/pending 改成 FAILED（L485–497）。但 Stripe 适配器没把 `checkout.session.async_payment_failed` 映射过来，所以实际上 Stripe 这条路径用不上。

**我们怎么移植：** 收到 `checkout.session.async_payment_failed` 时执行 `UPDATE orders SET status='failed' WHERE id=? AND status='pending'`。前端历史和订单列表里如果有展示，就显示"付款失败"。

- 是否需要改 Stripe 事件：不需要，该事件已经订阅。

## 6（策略）部分退款不扣分；全额退款可能让余额变负

**当前代码：问题存在。**
- L305–306：只要不是全额退款就直接 `return`，不扣分。
- L310：全额退款时 `-credits` 无条件写进账本。如果用户已经用掉了这些积分，余额会变负。负余额会挡住后续生成，因为 L411 的扣分有余额 ≥ 判断，但界面上会显示负数。

**模板怎么做：**
- 退款只能由管理员发起（`refundOrder`）：先把订单抢占为 `REFUNDING`，再调 Stripe 退款（幂等键 `refund_<orderNo>`），然后在原子事务里扣分并标记 `REFUNDED`。
- 扣分用 `credits/service.ts` 里的 `planDeductForRefund`：**只扣剩余积分，最多扣到 0，不会出现负数**，返回实际扣掉的数量 `deducted`。管理员可以用 `deductCredits` 指定扣多少，默认是整单的积分。
- 模板不处理 Stripe 后台发起的退款，也就是不订阅 `charge.refunded`。

**我们怎么移植：** `charge.refunded` 事件已经订阅，继续用它，覆盖在 Stripe 后台操作的退款。实现上用 `payment_intent` 或 metadata 找到订单，用 `charge.amount_refunded`（**累计值**）对比 `orders.refunded_cents` 算出本次新增的退款，保证重复事件和多次部分退款都是幂等的。

请用户**二选一**：

### 选项 A：按比例扣积分，最低扣到 0（推荐，和模板 `planDeductForRefund` 的思路一致）
- 目标扣分 = `floor(credits × amount_refunded / amount_paid)`，减去本订单已经扣过的。
- 实际扣分 = `min(目标扣分, 当前余额)`，余额最低到 0，永远不为负。
- 扣不足的部分写 `payment_anomalies(kind='clawback_shortfall')`，只记录，不冻结账户。
- 订单状态：部分退款为 `partially_refunded`，退满为 `refunded`。
- 账本：每次退款写一行，`kind='refund_clawback'`，`reference='<orderId>:<累计退款额>'`，天然幂等。
- 优点：公平、自动，不会出现负余额。缺点：用户可以"先用光积分再申请退款"，平台要承担这部分损失。

### 选项 B：全额退款时清空本单积分并冻结账户；部分退款不自动扣分
- 全额退款：扣 `min(本单积分, 当前余额)`。如果扣不足，说明本单积分已经用掉了，就冻结账户（`users.frozen_at`），冻结后不能生成也不能下单，前端提示联系客服。
- 部分退款：不自动扣分，只写 `payment_anomalies(kind='partial_refund')`，由管理员手动用 `/api/admin/grant` 加负数处理。
- 优点：能防"用完再退"的滥用。缺点：需要人工处理，可能误伤正常用户。

- 是否需要 D1 迁移：需要。`orders.refunded_cents` 两个选项都要；B 还要 `users.frozen_at`、`frozen_reason`（草稿 0002 都已包含）。
- 是否需要改 Stripe 事件：不需要。

## 7（低）没有处理 charge.dispute.*

**当前代码：问题存在。** 新账户的 webhook `we_1UVPdA4VJta90MPRJr8I4snO` 只订阅了 5 个事件，不包括 dispute；代码里也没有相关分支。另外，dispute 对象的 `metadata` 通常是空的，现有的 `meta.site !== SITE` 判断会直接把它忽略掉。所以只加订阅不改代码也不够，要靠 `payment_intent` 反查订单。

**模板怎么做：** 只读检查下全仓搜不到 `dispute`。只有 `src/core/payment/creem.ts` 出现过这个词，Stripe 部分没有处理争议。

**我们怎么移植：**
- 代码：
  - `settleOrder` 时把 `session.payment_intent` 存进 `orders.payment_intent`。
  - webhook 收到 dispute 事件时，用 `obj.payment_intent` 查订单，不再依赖 metadata。site 判断改成"metadata 匹配**或者**能用 payment_intent 找到本站订单"。新账户是 Tiny Desk 独享的，这样改是安全的。
  - `charge.dispute.created`：
    - 订单标 `disputed`；
    - 按第 6 条选定的策略暂扣本单积分，最低到 0；
    - 冻结账户（可选，看用户选择）；
    - 写 `payment_anomalies(kind='dispute_opened')`。
  - `charge.dispute.closed`：
    - `status=won`：退回暂扣的积分（`kind='dispute_reversal'`），解冻，订单恢复 `paid`；
    - `status=lost`：订单标 `dispute_lost`，积分不退回；
    - 写一行 `dispute_closed` 记录。
- **需要改 Stripe 设置，请用户决定。** 站点经营说"事件不用改"，但 dispute 必须在新 webhook 上**加订阅**：
  - `charge.dispute.created`
  - `charge.dispute.closed`
  - 可选 `charge.dispute.funds_withdrawn`，只用来记账，不是必需的。
- 不加订阅的替代方案：cron 每天调 `GET /v1/disputes?created[gte]=…` 轮询。这需要给受限密钥加 **Disputes: Read** 权限，同样要改 Stripe 设置。
- 如果两者都不做：第 7 条只能先把代码写好，一直不会触发，争议靠 Stripe 后台邮件人工处理。

- 是否需要 D1 迁移：需要，`orders.payment_intent` 和索引、`users.frozen_*`（草稿 0002）。

## 8（低）把 Stripe 原始报错返回给前端

**当前代码：问题存在。** L251 的 502 响应里带了 `detail: s.error.message` 和 `code`。10-28 那次就把"缺商品税码"的原文暴露给了浏览器。

**模板怎么做：** `checkout.ts` 的 catch 里写的是 `respErr(error.message || 'Checkout failed')`，**同样会把原始报错返回给前端**，模板在这一点上没有更好的做法。

**我们怎么移植：**
- 前端只收到 `{ error: 'Could not open checkout. Please try again.', ref: '<orderId>' }`。
- 完整的 `code`、`type`、`message`（截断后）只写进 `console.error` 和 `orders.error`。
- 用户把 ref 发给客服，管理员就能查到原因。

---

## 改动清单（计划在 `fix/payments` 分支实现）

| 文件 | 改动 |
|---|---|
| `worker.js` | 新增 `settleOrder()`、`reconcileOrders()`、`stripeGet()`、`anomaly()`、`GET /api/stripe/return`、`GET /api/admin/anomalies`。改动 `checkout()` 的 success_url 和失败处理、`webhook()` 的分支和 site 判断、`cron()`。如选冻结方案，`createJob()` 和 `checkout()` 要检查 `frozen_at` |
| `static/app.js` | 根据 `?paid=1`、`?paid=pending` 显示"已到账"或"处理中，稍后刷新"，并刷新积分 |
| `migrations/0002_payments_fix.sql` | 草稿已写。在生产执行前由用户审阅；只能执行一次，因为 ALTER 不幂等 |
| `build.py` | 不改 |
| Stripe 设置 | 默认不改。第 7 条需要用户决定是否在 `we_1UVPdA4VJta90MPRJr8I4snO` 上加 `charge.dispute.created` 和 `charge.dispute.closed` |

## 工作量估计

- 第 1、2、3、4、5、8 条（核心对账和幂等）：约 0.5 天写代码，0.5 天本地测试。
- 第 6 条：选项 A 约 2 小时，选项 B 约 3 小时（含冻结逻辑和前端提示）。
- 第 7 条：代码约 2 小时；加订阅由用户在 Stripe 后台点一下，或我按批准用 API 加。
- 合计约 1.5 到 2 天，部署本身只需几分钟。

## 风险

- **D1 迁移**：`ALTER TABLE` 不可回滚，但只加列和索引，不破坏现有数据。执行前先导出 `orders`、`credit_ledger`、`funnel_events` 做备份。
- **回跳补单不要求登录**：只以 Stripe 返回的数据为准，攻击者伪造 `session_id` 也查不到属于本站的订单；同时对 `/api/stripe/return` 按 IP 限流，防止被拿来刷 Stripe API。
- **cron 调 Stripe 的频率**：每分钟最多 10 单，远低于 Stripe 限流（live 模式 100 次/秒）。
- **受限密钥权限**：回跳、cron 只用 `checkout.sessions` 读权限，已具备。dispute 轮询方案需要额外的 Disputes Read。
- **重复发积分**：靠 `UNIQUE(kind, reference)` 加条件 UPDATE 双保险，测试计划里有并发重放用例。
- **site 判断放宽**（仅第 7 条）：新账户 Tiny Desk 独享，影响有限；仍然要求能对上本站订单。

## 上线前测试计划（不真付款、不调生成接口）

1. **本地 miniflare**（`wrangler dev --local`，用本地 D1 和 KV，Stripe 密钥用 test 模式或 mock）：
   - 先在本地 D1 执行 0001 和 0002。
   - 用 `fetch` mock 掉 `api.stripe.com`：`/v1/checkout/sessions/{id}` 返回 open、paid（金额正确）、paid（金额偏低）、expired、unpaid 等固定样例。
2. **模拟 webhook**：用本地测试 secret 生成 `Stripe-Signature`（`t=…,v1=HMAC`），构造并 POST 下面这些事件：
   - `checkout.session.completed`（paid / unpaid）
   - `async_payment_succeeded` / `async_payment_failed`
   - `expired`
   - `charge.refunded`：部分退款 30%，再退到 100%；以及余额不足时的退款
   - `charge.dispute.created` / `charge.dispute.closed`（won / lost）
   - 同一事件重放 2 次；回跳和 webhook 同时结算同一订单（`Promise.all`）
3. **每个用例都要断言**：
   - 订单状态；
   - `credit_ledger` 只有一行 purchase；
   - 余额 ≥ 0（选项 A）；
   - 漏斗 paid 只有 1 条；
   - 异常表行数；
   - 前端只拿到通用报错文案。
4. **cron**：手动调用 `scheduled()`，覆盖 pending 订单 10 分钟后补单、25 小时后标 expired、无 session_id 标 failed 三种情况。
5. **回归**：本地确认注册、登录、创建 Checkout 跳转（mock）、`/api/config` 都正常。
6. **上线后**：先执行迁移，再部署 Worker。然后用冒烟账号创建 Checkout，**不付款**，确认 `success_url` 里带 `{CHECKOUT_SESSION_ID}`。
7. **$9.99 真实测试**：由站点经营执行，**必须先经用户批准**。测试内容：付款、回跳显示已到账、积分 +300、webhook 和回跳不重复发分、在 Stripe 后台退款后按选定策略扣分。

## 需要用户拍板

1. **第 6 条退款策略**：选项 A（按比例扣分、最低到 0，推荐）还是选项 B（全额退款清零加冻结、部分退款人工处理）。
2. **第 7 条争议**：是否在新 webhook 上加 `charge.dispute.created` 和 `charge.dispute.closed`。或者改为给受限密钥加 Disputes Read，由 cron 轮询。或者暂不处理。
3. **异常报警渠道**：只用 admin 接口查看（默认）、Workers Logs 告警，还是推送到某个 IM 或邮箱。注意 privacy@ 的邮件转发还没配置。
4. 争议期间**是否冻结账户**。
5. 是否同意执行 D1 迁移 `0002`（执行前备份）。
6. 上线后 $9.99 实测的时间和批准。
