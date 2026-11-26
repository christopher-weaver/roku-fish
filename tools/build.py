"""Portable, standard-library-only Roku validation and reproducible ZIP packaging."""
from pathlib import Path
import argparse,json,re,struct,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[1];ROKU=ROOT/'roku'

def dimensions(p):
    b=p.read_bytes()
    if b[:8]==b'\x89PNG\r\n\x1a\n':return struct.unpack('>II',b[16:24])
    if b[:4]==b'RIFF' and b[8:12]==b'WEBP':
        # Extended WebP stores its canvas dimensions in VP8X (24-bit LE, minus one).
        if b[12:16]==b'VP8X':return (int.from_bytes(b[24:27],'little')+1,int.from_bytes(b[27:30],'little')+1)
        if b[12:16]==b'VP8L':
            packed=int.from_bytes(b[21:25],'little');return ((packed&0x3fff)+1,((packed>>14)&0x3fff)+1)
    if b[:4]==b'RIFF' and b[8:12]==b'WEBP' and b[12:16]==b'VP8 ':
        return (int.from_bytes(b[26:28],'little')&0x3fff,int.from_bytes(b[28:30],'little')&0x3fff)
    if b[:2]==b'\xff\xd8':
        i=2
        while i<len(b):
            if b[i]!=255:i+=1;continue
            while b[i]==255:i+=1
            marker=b[i];i+=1
            if marker in [0xd8,0xd9]:continue
            length=int.from_bytes(b[i:i+2],'big')
            if marker in [0xc0,0xc1,0xc2]:return (int.from_bytes(b[i+5:i+7],'big'),int.from_bytes(b[i+3:i+5],'big'))
            i+=length
    raise ValueError('Unsupported/corrupt image: '+str(p))

def validate():
    errors=[];text=(ROKU/'manifest').read_text(encoding='utf-8')
    if not text.endswith('\n'):errors.append('Manifest needs final newline')
    manifest={}
    for line in text.splitlines():
        if line.strip() and not line.startswith('#'):
            if '=' not in line:errors.append('Invalid manifest line '+line);continue
            k,v=line.split('=',1)
            if k in manifest:errors.append('Duplicate manifest key '+k)
            manifest[k]=v
    for key in ['screensaver_title','major_version','minor_version','build_version','rsg_version','mm_icon_focus_fhd','mm_icon_focus_hd']:
        if not manifest.get(key):errors.append('Missing manifest '+key)
    if 'title' in manifest:errors.append('Standalone screensaver must omit ordinary channel title')
    if manifest.get('rsg_version')!='1.3':errors.append('Expected rsg_version=1.3')
    for key in ['major_version','minor_version','build_version']:
        if not manifest.get(key,'').isdigit():errors.append('Version must be an integer: '+key)
    source='\n'.join(p.read_text(encoding='utf-8')for p in (ROKU/'source').glob('*.brs'))
    for name in ['RunScreenSaver','RunScreenSaverSettings']:
        if not re.search(r'(?im)^\s*(sub|function)\s+'+name+r'\s*\(',source):errors.append('Missing '+name)
    if re.search(r'(?im)^\s*(sub|function)\s+(Main|RunUserInterface)\s*\(',source):errors.append('Normal channel entry point is forbidden')
    if re.search(r'(?i)CreateObject\("(?:roVideoPlayer|roAudioPlayer|roUrlTransfer)"',source):errors.append('Playback/network component in screensaver')
    for key,val in manifest.items():
        if val.startswith('pkg:/') and not (ROKU/val[5:]).is_file():errors.append('Missing '+val)
    for raw in re.findall(r'pkg:/[^\s"<>]+',source):
        if '+' not in raw and '.' in Path(raw).name and not (ROKU/raw[5:]).exists():errors.append('Missing literal asset '+raw)
    # Complete catalog catches dynamic sprite / lighting filenames, too.
    catalog=json.loads((ROKU/'scenes/assets.json').read_text())
    total_texture=0
    for name,record in catalog.items():
        p=ROKU/'images'/name
        if not p.exists():errors.append('Missing catalog asset '+name);continue
        try:
            w,h=dimensions(p)
            if (w,h)!=(record['width'],record['height']):errors.append('Dimensions differ: '+name)
            if w>2048 or h>2048:errors.append('Texture exceeds Roku 2048px limit: '+name)
            if hashlib.sha256(p.read_bytes()).hexdigest()!=record['sha256']:errors.append('Asset changed; regenerate catalog: '+name)
            total_texture+=w*h*4
        except ValueError as e:errors.append(str(e))
    species=json.loads((ROKU/'scenes/species.json').read_text())
    if len(species)<10:errors.append('Need at least ten species')
    for name,sp in species.items():
        rig=sp.get('tailRig')
        if sp.get('bodyRenderMode')=='whole-swim' and (not rig or len(rig.get('body',[]))!=3 or len(rig.get('posesXZ',[]))!=sp['tailPoseCount']):
            errors.append('Missing model tail attachment: '+name+'; run tools/tail_rig.py')
        for image_key,frames_key,pose_key in [('image','frames','poseCount'),('finImage','finFrames','finPoseCount'),('tailImage','tailFrames','tailPoseCount')]:
            image=ROKU/sp[image_key][5:]
            if not image.exists():errors.append('Missing atlas '+str(image));continue
            w,h=dimensions(image)
            expected=(sp.get('bodyYawCount',sp['yawCount']) if frames_key=='frames' else sp['yawCount'])*sp[pose_key]
            if frames_key=='frames' and 'turnViews' in sp:
                if sp['turnOffset']!=expected:errors.append('Turn atlas offset '+name)
                expected+=sp['turnViews']['bodyYawCount']*2
            if len(sp[frames_key])!=expected:errors.append('Atlas frame count '+name+' '+frames_key)
            for f in sp[frames_key]:
                if min(f['x'],f['y'])<0 or min(f['w'],f['h'])<1 or f['x']+f['w']>w or f['y']+f['h']>h:errors.append('Out-of-bounds frame '+name)
                if 'anchorX' not in f or 'anchorY' not in f:errors.append('Missing cropped-frame anchor '+name)
    tank=json.loads((ROKU/'scenes/tank.json').read_text())
    for name,sp in species.items():
        if 'turnCoreImage' not in sp:continue
        w,h=dimensions(ROKU/sp['turnCoreImage'][5:])
        if len(sp['turnCoreFrames'])!=sp['turnViews']['bodyYawCount']*2:errors.append('Turn interior frame count '+name)
        for f in sp['turnCoreFrames']:
            if f['x']<0 or f['y']<0 or f['x']+f['w']>w or f['y']+f['h']>h:errors.append('Turn interior outside atlas '+name)
            if f['coreWidth']<=0:errors.append('Invalid turn interior reference '+name)
    for f in tank['formations']:
        if 'animation'not in f:continue
        cfg=f['animation']
        for i in range(f['frames']):
            page=i//cfg['framesPerPage'];local=i%cfg['framesPerPage']
            path=ROKU/f['images'][page][5:];w,h=dimensions(path)
            x=cfg['gutter']+local%f['columns']*cfg['strideX'];y=cfg['gutter']+local//f['columns']*cfg['strideY']
            if x+f['frameWidth']>w or y+f['frameHeight']>h:errors.append('Marine pose outside atlas '+f['id'])
    for fhd,size in [('icon-fhd.jpg',(540,405)),('icon-hd.jpg',(290,218)),('splash-fhd.jpg',(1920,1080)),('splash-hd.jpg',(1280,720)),('splash-sd.jpg',(720,480))]:
        if dimensions(ROKU/'images'/fhd)!=size:errors.append('Manifest art dimensions '+fhd)
    if errors:raise ValueError('\n'.join(errors))
    print(f'Validated manifest, native entry points, {len(species)} species, {len(catalog)} images and all atlas regions')
    return {'images':len(catalog),'species':len(species),'all_variant_texture_mib':round(total_texture/1048576,2)}

def build(increment=False):
    from collision_index import write_index
    write_index()
    if increment:
        p=ROKU/'manifest';text=p.read_text();text=re.sub(r'(?m)^build_version=(\d+)',lambda m:'build_version='+str(int(m[1])+1),text);p.write_text(text,newline='\n')
    report=validate();dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    path=dist/'deep-reef-screensaver.zip'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(ROKU.rglob('*')):
            if not p.is_file() or p.name.startswith('.'):continue
            rel=p.relative_to(ROKU)
            if rel.parts[0] not in ['manifest','source','components','scenes','images','licenses']:continue
            if p.suffix.lower() not in ['','.brs','.xml','.json','.jpg','.png','.webp','.txt']:continue
            info=zipfile.ZipInfo(rel.as_posix(),(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes())
    size=path.stat().st_size
    if size>4*1024*1024:raise ValueError(f'Package is {size:,} bytes; exceeds 4 MiB (4,194,304-byte) limit. Run tools/optimize.py.')
    with zipfile.ZipFile(path)as z:
        if 'manifest' not in z.namelist() or z.testzip():raise ValueError('ZIP integrity or root manifest failed')
    report.update(package_bytes=size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (dist/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'{path}\n{size:,} bytes; ZIP integrity verified; SHA256 {report["sha256"]}')
    return path
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--increment',action='store_true');p.add_argument('--validate-only',action='store_true');args=p.parse_args()
    try:validate() if args.validate_only else build(args.increment)
    except (ValueError,OSError,KeyError)as e:p.exit(1,'Validation failed: '+str(e)+'\n')
