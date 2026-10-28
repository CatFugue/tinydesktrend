# usage: python3 deploy_script.py <completion_jwt|-> [--with-secrets]; writes /workspace/secrets/tdt-deploy.js (600)
import json,sys,os
jwt=sys.argv[1]; with_secrets='--with-secrets' in sys.argv
S='/workspace/secrets/'
prices=json.load(open(S+'tinydesktrend-stripe.json'))['prices']
bindings=[{"type":"assets","name":"ASSETS"},
 {"type":"d1","name":"DB","id":"5338cb59-c4c7-42cd-8a48-1287bf4bdf67"},
 {"type":"kv_namespace","name":"VIDEOS","namespace_id":"a5fbe0d6cec1495dae0c8679aea8aae4"},
 {"type":"plain_text","name":"STRIPE_PRICE_STARTER","text":prices['starter']},
 {"type":"plain_text","name":"STRIPE_PRICE_PLUS","text":prices['plus']},
 {"type":"plain_text","name":"STRIPE_PRICE_PRO","text":prices['pro']},
 {"type":"plain_text","name":"SOURCE_FILE","text":"mm_file://2115297117809086464"}]
meta={"main_module":"index.js","compatibility_date":"2026-10-01","bindings":bindings}
if with_secrets:
    sec={"METASO_API_KEY":os.environ['METASO_API_KEY'].strip(),"STRIPE_SECRET_KEY":open(S+'stripe-secret-key.txt').read().strip(),
         "STRIPE_WEBHOOK_SECRET":open(S+'tinydesktrend-stripe-webhook-secret.txt').read().strip(),"ADMIN_TOKEN":open(S+'tinydesktrend-admin-token.txt').read().strip()}
    bindings+= [{"type":"secret_text","name":k,"text":v} for k,v in sec.items()]
else:
    meta["keep_bindings"]=["secret_text"]
meta["assets"]={"config":{"html_handling":"auto-trailing-slash","not_found_handling":"404-page","run_worker_first":True}}
if jwt!='-': meta["assets"]["jwt"]=jwt
else: meta["keep_assets"]=True
code=open('worker.js').read(); prompt=open('prompt.txt').read()
js=f"""async () => {{
const metadata = {json.dumps(meta)};
const parts = [["metadata","metadata.json","application/json",JSON.stringify(metadata)],["index.js","index.js","application/javascript+module",{json.dumps(code)}],["prompt.txt","prompt.txt","text/plain",{json.dumps(prompt)}]];
const b = `----F${{Date.now()}}`;
const body = parts.map(([n,f,t,c]) => `--${{b}}\\r\\nContent-Disposition: form-data; name="${{n}}"; filename="${{f}}"\\r\\nContent-Type: ${{t}}\\r\\n\\r\\n${{c}}\\r\\n`).join('') + `--${{b}}--\\r\\n`;
const put = await cloudflare.request({{ method: 'PUT', path: `/accounts/${{accountId}}/workers/scripts/tinydesktrend`, body, contentType: `multipart/form-data; boundary=${{b}}`, rawBody: true }});
const cron = await cloudflare.request({{ method: 'PUT', path: `/accounts/${{accountId}}/workers/scripts/tinydesktrend/schedules`, body: [{{ cron: '* * * * *' }}] }}).then(r => r.success).catch(e => String(e.message).slice(0,300));
return {{ ok: put.success, has_assets: put.result?.has_assets, cron }};
}}"""
out=S+'tdt-deploy.js'; open(out,'w').write(js); os.chmod(out,0o600); print(out, len(js))
