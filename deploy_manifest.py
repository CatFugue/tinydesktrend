# Writes /workspace/manifest-tdt.json for the Workers assets upload session.
import os,hashlib,json
m={}
for root,_,fs in os.walk('public'):
    for f in fs:
        p=os.path.join(root,f); b=open(p,'rb').read()
        m['/'+os.path.relpath(p,'public')]={"hash":hashlib.sha256(b).hexdigest()[:32],"size":len(b)}
json.dump(m,open('/workspace/manifest-tdt.json','w'),separators=(',',':'))
code="async () => { const manifest = "+json.dumps(m,separators=(',',':'))+"; const r = await cloudflare.request({method:'POST', path:`/accounts/${accountId}/workers/scripts/tinydesktrend/assets-upload-session`, body:{manifest}}); return {jwt: r.result.jwt, buckets: r.result.buckets || []}; }"
open('/workspace/tdt-session.js','w').write(code)
print(len(m),'files')
