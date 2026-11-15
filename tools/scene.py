"""Close reef composition, registered depth masks and photographic sand."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageEnhance
from scipy.ndimage import maximum_filter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'roku/images'
SOURCE=ROOT/'assets/source/reef-close-reference.png'
W,H=2048,1152
CREST=[(0,.19),(.02,.15),(.04,.12),(.075,.085),(.12,.11),(.155,.19),(.19,.20),(.23,.32),(.25,.25),(.265,.14),(.28,.095),(.32,.075),(.38,.09),(.41,.12),(.46,.17),(.49,.24),(.535,.23),(.58,.15),(.61,.11),(.64,.055),(.68,.11),(.70,.08),(.72,.017),(.745,.05),(.765,.13),(.79,.135),(.82,.08),(.85,.10),(.88,.07),(.90,.13),(.91,.095),(.93,.12),(.94,.19),(.97,.27),(1,.27)]

def photo():
    im=Image.open(SOURCE).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    return ImageEnhance.Sharpness(ImageEnhance.Color(im).enhance(1.04)).enhance(1.10)

def reef_cutout():
    source=Image.open(ROOT/'assets/source/reef-midground-cutout.png').convert('RGBA')
    reef=Image.new('RGBA',(W,H))
    reef.alpha_composite(source.resize((W,1048),Image.Resampling.LANCZOS))
    return reef

def build(splash):
    import waves
    im=photo();a=np.asarray(im,dtype=float);yy,xx=np.mgrid[:H,:W]
    sand=np.asarray(waves.sand_mask(),dtype=float)/255
    cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());cfg.pop('layers',None)
    cfg['formations']=[];cfg['occlusionDepths']=[];planes=[];union=np.zeros((H,W))
    # Independent islands leave broad open-water/sand channels between layers.
    layout=[
        ('right-garden',.24,.025,1660,550,380,380),
        ('white-crown',.40,.04,400,335,650,635),
        ('branching-coral',.49,.04,1230,170,690,800),
        ('green-cup',.62,.035,-70,590,540,435),
        ('brain-coral',.70,.04,1230,600,490,490),
        ('central-clam',.76,.025,850,760,360,330),
    ]
    def grid(alpha):
        return [''.join('#' if np.any(alpha[y:y+8,x:x+8]>.12) else '.' for x in range(0,W,8))for y in range(0,H,8)]
    for name,z,half,x,y,width,height in layout:
        image='reef-'+name+'.webp'
        # All three actual mesh-rendered view silhouettes reserve collision space.
        atlas=Image.open(OUT/image).convert('RGBA');fw=atlas.width//3;fh=atlas.height
        footprint=Image.open(ROOT/'assets/source/coral-islands'/(name+'-footprint.png')).resize((width,height),Image.Resampling.LANCZOS)
        canvas=Image.new('L',(W,H));canvas.paste(footprint,(x,y));alpha=np.asarray(canvas,dtype=float)/255
        union=np.maximum(union,alpha);parallax=.58+.42*z
        cfg['formations'].append(dict(id=name,x=x,y=y,width=width,height=height,z=z,halfDepth=half,parallax=parallax,image='pkg:/images/'+image,frames=3,frameWidth=fw,frameHeight=fh,renderedMesh=True))
        cfg['occlusionDepths'].append(z)
        planes.append(dict(id=name,z=z,halfDepth=half,parallax=parallax,rows=grid(alpha)))
    # Only water and sand live in the background. No fixed coral is baked into it.
    background=np.zeros_like(a);last=np.array([115.,75.,115.])
    crest=np.interp(np.arange(W)/W,[p[0]for p in CREST],[p[1]*H for p in CREST])
    for y in range(H):
        samples=a[y,(y<crest-30)]
        if len(samples)>80 and y<350:last=np.median(samples,axis=0)
        background[y]=last*np.array([1-.00015*y,1-.00012*y,1-.0001*y])
    # Extend distant floor beneath the separate islands; retain original sharp
    # foreground grain/ridges. The far floor fades naturally into ambient water.
    rng=np.random.default_rng(47831)
    fy,fx=np.mgrid[:360,:W];depth=fy/360
    ripples=np.sin(fy*.095+np.sin(fx/240)*.8)+.3*np.cos(fy*.19+fx/700)
    grain=rng.normal(0,3.2,(360,W))
    for row in range(360):
        y=680+row;weight=min(1,max(0,(row-15)/125))
        lighting=(ripples[row]*10+grain[row])*(.35+.65*row/360)
        pixel=np.array([158.,112.,111.])+lighting[:,None]*np.array([1,.82,.7])
        haze=(1-row/360)*.3
        pixel=pixel*(1-haze)+np.array([105,75,105])*haze
        background[y]=background[y]*(1-weight)+pixel*weight
    background=background*(1-sand[:,:,None])+a*sand[:,:,None]
    from PIL import ImageFilter
    sy,sx=np.mgrid[:48,:128]
    shadow=Image.new('RGBA',(128,48));shadow.putalpha(Image.fromarray(np.uint8(np.exp(-(((sx-64)/44)**2+((sy-24)/12)**2))*75)).filter(ImageFilter.GaussianBlur(2)))
    shadow.save(OUT/'coral-shadow.png')
    warm=Image.fromarray(np.uint8(np.clip(background,0,255)))
    warm.save(OUT/'water-sunset.webp',quality=74,method=6)
    cool=np.asarray(warm,dtype=float);luminance=cool@np.array([.2126,.7152,.0722])
    blue=np.stack([luminance*.20+8,luminance*.75+28,luminance*1.05+38],-1)
    water=1-sand
    cool=cool*(1-water[:,:,None])+blue*water[:,:,None]
    Image.fromarray(np.uint8(np.clip(cool,0,255))).save(OUT/'water-day.webp',quality=74,method=6)
    cfg['softCoral']=None
    cfg['notes']='Six separated coral islands with three offline relief-mesh views each, stronger depth parallax, swim-through arch and sand channels. Camera is presented with adjacent-pixel opaque-frame blending.'
    (ROOT/'roku/scenes/tank.json').write_text(json.dumps(cfg,indent=2)+'\n')
    occ={'cell':8,'rows':grid(union),'planes':planes}
    (ROOT/'roku/scenes/occupancy.json').write_text(json.dumps(occ,separators=(',',':')))
    build_navigation(occ)
    for name in ['reef-mid.webp','reef-front.webp','soft-coral.webp','reef-sea-fan.webp','reef-center-rock.webp']:(OUT/name).unlink(missing_ok=True)
    mask=union
    for name,size in [('icon-fhd',(540,405)),('icon-hd',(290,218)),('icon-sd',(214,144)),('splash-fhd',(1920,1080)),('splash-hd',(1280,720)),('splash-sd',(720,480))]:
        pic=im.resize(size,Image.Resampling.LANCZOS) if name.startswith('icon') else splash(size)
        pic.save(OUT/(name+'.jpg'),quality=91)
    for name in ['reef-mid-sunset.webp','reef-front-sunset.webp','soft-coral.png','soft-coral-sunset.png']:(OUT/name).unlink(missing_ok=True)
    Image.fromarray(np.uint8(mask*255)).resize((1024,576)).save(ROOT/'docs/previews/reef-mask.png')
    print('Six sparse mesh-rendered reef formations, pure-water backdrop and photographic sand ready',flush=True)


def build_navigation(occ):
    """Shared conservative graph, checked against the largest fully posed fish.

    Graph edges are swept volumes, including every camera position. Runtime BFS
    only visits this small graph on a new destination, never once per frame.
    """
    species=json.loads((ROOT/'roku/scenes/species.json').read_text())
    cell=occ['cell'];masks=[np.array([[c=='#'for c in row]for row in p['rows']])for p in occ['planes']]
    def blocked(a,b):
        for sp in species.values():
            radius=sp['bodyThickness']*sp['length']*1.12/1728+.012
            scale=(.70+.30*max(a[2],b[2]))*sp['length']/sp['renderLength']*1.12
            for volume in occ.get('volumes',[]):
                extent=[volume['halfWidth']+(sp['collisionHalfWidth']+sp['collisionHalfHeight']*.22)*scale+30,
                        volume['halfHeight']+(sp['collisionHalfHeight']+sp['collisionHalfWidth']*.22)*scale+16,
                        volume['halfDepth']+radius]
                enter,leave=0.,1.
                for axis,key in enumerate(['x','y','z']):
                    delta=b[axis]-a[axis];lo=volume[key]-extent[axis];hi=volume[key]+extent[axis]
                    if abs(delta)<1e-9:
                        if not lo<=a[axis]<=hi:enter=2
                    else:
                        t0,t1=sorted([(lo-a[axis])/delta,(hi-a[axis])/delta]);enter=max(enter,t0);leave=min(leave,t1)
                if enter<=leave:return True
            for plane,mask in zip(occ['planes'],masks):
                if max(a[2],b[2])+radius<plane['z']-plane['halfDepth'] or min(a[2],b[2])-radius>plane['z']+plane['halfDepth']:continue
                scale=(.70+.30*max(a[2],b[2]))*sp['length']/sp['renderLength']*1.12
                hw=(sp['collisionHalfWidth']+sp['collisionHalfHeight']*.22)*scale+12
                hh=(sp['collisionHalfHeight']+sp['collisionHalfWidth']*.22)*scale+12
                pan=plane['parallax']
                xs=[p[0]+64*(1-pan)+cam*(pan-(.70+.30*p[2]))for p in [a,b]for cam in [8,120]]
                ys=[p[1]+(1-p[2])*30+36 for p in [a,b]]
                left=max(0,int((min(xs)-hw)//cell));right=min(255,int((max(xs)+hw)//cell))
                top=max(0,int((min(ys)-hh)//cell));bottom=min(143,int((max(ys)+hh)//cell))
                if mask[top:bottom+1,left:right+1].any():return True
        return False
    xs=[180,400,650,790,1030,1230,1500,1780,1920];ys=[100,260,440,630,790,910];zs=[.12,.28,.42,.54,.72,.86,.94]
    nodes=[];lookup={}
    for xi,x in enumerate(xs):
        for yi,y in enumerate(ys):
            for zi,z in enumerate(zs):
                point=[x,y,z]
                if not blocked(point,point):
                    lookup[xi,yi,zi]=len(nodes);nodes.append(dict(x=x,y=y,z=z,edges=[]))
    for key,i in lookup.items():
        for axis in range(3):
            other=list(key);other[axis]+=1;j=lookup.get(tuple(other))
            if j is not None and not blocked([nodes[i][k]for k in ['x','y','z']],[nodes[j][k]for k in ['x','y','z']]):
                nodes[i]['edges'].append(j);nodes[j]['edges'].append(i)
    # Discard islands. Every published destination must have a route through
    # open water to the rest of the reef on both sides.
    seen={0};queue=[0]
    for i in queue:
        for j in nodes[i]['edges']:
            if j not in seen:seen.add(j);queue.append(j)
    remap={old:new for new,old in enumerate(sorted(seen))}
    nodes=[dict(node,edges=[remap[j]for j in node['edges']if j in seen])for i,node in enumerate(nodes)if i in seen]
    next_hop=[]
    for start in range(len(nodes)):
        hops=[-1]*len(nodes);hops[start]=start;queue=[start]
        for here in queue:
            for there in nodes[here]['edges']:
                if hops[there]<0:
                    hops[there]=there if here==start else hops[here];queue.append(there)
        next_hop.append(hops)
    (ROOT/'roku/scenes/navigation.json').write_text(json.dumps({'nodes':nodes,'nextHop':next_hop,'clearance':'All species, maximum size/pitch/tail/fin pose; full camera sweep; 4px extra margin.'},separators=(',',':')))
    print('Connected clearance graph:',len(nodes),'nodes,',sum(len(n['edges'])for n in nodes)//2,'edges',flush=True)
