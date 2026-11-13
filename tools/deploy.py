"""Deploy only when explicitly invoked and both Roku environment variables exist."""
from pathlib import Path
import os,ipaddress,urllib.request,urllib.error,uuid,argparse
ROOT=Path(__file__).resolve().parents[1]
def deploy():
    ip=os.environ.get('ROKU_IP','');password=os.environ.get('ROKU_DEV_PASSWORD','')
    if not ip or not password:raise ValueError('Set ROKU_IP and ROKU_DEV_PASSWORD before invoking this helper')
    address=ipaddress.ip_address(ip);host='['+ip+']' if address.version==6 else ip
    base='http://'+host;url=base+'/plugin_install';p=ROOT/'dist/deep-reef-screensaver.zip'
    if not p.is_file():raise ValueError('Build dist/deep-reef-screensaver.zip first')
    boundary='DeepReef'+uuid.uuid4().hex;parts=[]
    for name,value in [('mysubmit','Install'),('archive',p.read_bytes())]:
        header=f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
        if isinstance(value,bytes):header+='; filename="deep-reef-screensaver.zip"\r\nContent-Type: application/zip'
        parts.extend([header.encode()+b'\r\n\r\n',value if isinstance(value,bytes)else value.encode(),b'\r\n'])
    parts.append(('--'+boundary+'--\r\n').encode());body=b''.join(parts)
    mgr=urllib.request.HTTPPasswordMgrWithDefaultRealm();mgr.add_password(None,base,'rokudev',password)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),urllib.request.HTTPDigestAuthHandler(mgr))
    req=urllib.request.Request(url,data=body,headers={'Content-Type':'multipart/form-data; boundary='+boundary})
    with opener.open(req,timeout=90)as response:result=response.read().decode('utf-8','replace')
    # Do not equate a 200 installer error page with a successful install.
    if 'Install Success' not in result and 'Application Received' not in result:
        raise ValueError('Installer did not confirm success. Open the Developer Application Installer to inspect its status.')
    print('Installer accepted Deep Reef. Select it under Settings → Theme → Screensavers.')
if __name__=='__main__':
    try:deploy()
    except (ValueError,OSError,urllib.error.URLError)as e:raise SystemExit(str(e))
