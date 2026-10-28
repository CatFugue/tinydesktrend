# tinydesktrend.com

Unofficial Tiny Desk AI generator. Static pages (build.py -> public/) + Worker `tinydesktrend` (worker.js).

- Build: `python3 build.py` (copies static/ into public/).
- Deploy (no wrangler login on the box): `deploy_manifest.py` -> Cloudflare API assets-upload-session -> `deploy_upload.py` -> `deploy_script.py <completion-jwt|-> [--with-secrets]` -> PUT script via Cloudflare API.
- Bindings: ASSETS, DB (D1 tinydesktrend-db 5338cb59-…), VIDEOS (KV a5fbe0d6…, generated videos 7 days + encrypted cfg/ secrets), vars STRIPE_PRICE_*, SOURCE_FILE (MetaSo mm_file of seg1 0-13 s). Cron: every minute.
- Secrets: STRIPE_WEBHOOK_SECRET, ADMIN_TOKEN as Worker secrets. STRIPE_SECRET_KEY and METASO_API_KEY are stored AES-GCM-encrypted in KV (cfg/*) via POST /api/admin/secret because the deploy tool redacted those values; a real Worker secret with the same name takes precedence.
- Migrations: migrations/*.sql, applied with the D1 query API.
- Admin (Bearer ADMIN_TOKEN): /api/admin/supply (GET/POST), /api/admin/grant, /api/admin/funnel, /api/admin/diag.
