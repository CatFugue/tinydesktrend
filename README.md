# tinydesktrend.com

Unofficial Tiny Desk AI generator. Static pages (build.py -> public/) + Worker `tinydesktrend` (worker.js).

- Build: `python3 build.py` (copies static/ into public/; on Windows run `python -X utf8 build.py`). Styles live in `static/style.css`, fonts are self-hosted in `static/fonts/` because the CSP only allows same-origin styles and fonts.
- Deploy with wrangler: `npx wrangler deploy` (config in `wrangler.jsonc`, secrets stay on the Worker).
- Deploy (no wrangler login on the box): `deploy_manifest.py` -> Cloudflare API assets-upload-session -> `deploy_upload.py` -> `deploy_script.py <completion-jwt|-> [--with-secrets]` -> PUT script via Cloudflare API.
- Bindings: ASSETS, DB (D1 tinydesktrend-db 5338cb59-…), VIDEOS (KV a5fbe0d6…, generated videos 7 days + encrypted cfg/ secrets), vars STRIPE_PRICE_*, SOURCE_FILE (MetaSo mm_file of seg1 0-13 s). Cron: every minute.
- Stripe: dedicated account acct_1UVPOC4VJta90MPR (restricted key). Product prod_VWSYQIpgXKn1XI (tax_code txcd_10000000), webhook we_1UVPdA4VJta90MPRJr8I4snO.
- Secrets/config: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_STARTER/PLUS/PRO and METASO_API_KEY are stored AES-GCM-encrypted in KV (cfg/*) via POST /api/admin/secret (the deploy tool redacts secret values). The KV value wins over a Worker binding of the same name; isolates re-read KV every 60 s. ADMIN_TOKEN is a Worker secret.
- Migrations: migrations/*.sql, applied with the D1 query API.
- Admin (Bearer ADMIN_TOKEN): /api/admin/supply (GET/POST), /api/admin/grant, /api/admin/funnel, /api/admin/diag.
