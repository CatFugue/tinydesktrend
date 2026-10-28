# usage: J=<upload jwt> python3 deploy_upload.py '<buckets json>'  -> prints completion jwt
import json,base64,mimetypes,subprocess,sys,os
jwt=os.environ['J']; m=json.load(open('/workspace/manifest-tdt.json'))
h2p={v['hash']:k for k,v in m.items()}; last=None
for b in [[h] for bb in json.loads(sys.argv[1]) for h in bb]:
    args=['curl','-sS','-X','POST','https://api.cloudflare.com/client/v4/accounts/1e5fedf5e38af3ee52e34f007e3790d0/workers/assets/upload?base64=true','-H','Authorization: Bearer '+jwt]
    for h in b:
        p=h2p[h]; fn='/tmp/a_'+h; open(fn,'w').write(base64.b64encode(open('public'+p,'rb').read()).decode())
        args+=['-F',f'{h}=@{fn};filename={h};type={mimetypes.guess_type(p)[0] or "application/octet-stream"}']
    r=json.loads(subprocess.run(args,capture_output=True,text=True).stdout); print(r.get('success'),r.get('errors'),file=sys.stderr)
    for h in b: os.remove('/tmp/a_'+h)
    if r.get('result') and r['result'].get('jwt'): last=r['result']['jwt']
print(last)
