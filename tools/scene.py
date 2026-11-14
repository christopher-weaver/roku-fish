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
    cutout=reef_cutout()
    mask=np.asarray(cutout.getchannel('A'),dtype=float)/255
    sand=np.asarray(waves.sand_mask(),dtype=float)/255
    mask*=1-sand
    # Individual mid-ground formations, with overlapping seam underpainting.
    # The reef remains continuous across the tank; open water above it is now
    # navigable rather than a perspective-compressed backdrop.
    shrink=.80;anchor=1048
    def lower(alpha):
        source=Image.fromarray(np.uint8(np.clip(alpha,0,1)*255))
        return np.asarray(source.transform((W,H),Image.Transform.AFFINE,
            (1,0,0,0,1/shrink,anchor-anchor/shrink),Image.Resampling.BICUBIC))/255
    reef=cutout.transform((W,H),Image.Transform.AFFINE,
        (1,0,0,0,1/shrink,anchor-anchor/shrink),Image.Resampling.BICUBIC)
    cup=((xx-265)/270)**2+((yy-760)/240)**2<1
    brain=((xx-1420)/290)**2+((yy-690)/235)**2<1
    clam=((xx-1140)/250)**2+((yy-925)/155)**2<1
    reserved=cup|brain|clam
    groups=[
        ('sea-fan',.38,.035,(xx<510)&~reserved),
        ('white-crown',.48,.045,(xx>=510)&(xx<1130)&(yy<620)&~reserved),
        ('branching-coral',.43,.045,(xx>=1130)&(yy<570)&~reserved),
        ('green-cup',.66,.045,cup&~clam),
        ('center-rock',.57,.045,(xx>=510)&(xx<1180)&(yy>=620)&~reserved),
        ('brain-coral',.70,.045,brain&~clam),
        ('right-garden',.61,.045,(xx>=1180)&(yy>=570)&~reserved),
        ('central-clam',.76,.025,clam),
    ]
    assigned=np.logical_or.reduce([g[3]for g in groups])
    groups[4]=(*groups[4][:3],groups[4][3]|~assigned)
    cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());cfg.pop('layers',None)
    cfg['formations']=[];cfg['occlusionDepths']=[];planes=[];union=np.zeros((H,W))
    def grid(alpha):
        return [''.join('#' if np.any(alpha[y:y+8,x:x+8]>.12) else '.' for x in range(0,W,8))for y in range(0,H,8)]
    for name,z,half,region in sorted(groups,key=lambda g:g[1]):
        alpha=np.round(lower(mask*maximum_filter(region,size=11))*31)/31;union=np.maximum(union,alpha)
        rgba=reef.copy();rgba.putalpha(Image.fromarray(np.uint8(alpha*255)))
        box=rgba.getchannel('A').getbbox();x,y,x1,y1=box
        image=f'reef-{name}.webp'
        rgba.crop(box).save(OUT/image,quality=72,method=6,exact=True)
        parallax=.78+.22*z
        cfg['formations'].append(dict(id=name,x=x,y=y,width=x1-x,height=y1-y,z=z,halfDepth=half,parallax=parallax,image='pkg:/images/'+image))
        cfg['occlusionDepths'].append(z)
        planes.append(dict(id=name,z=z,halfDepth=half,parallax=parallax,rows=grid(alpha)))
    # Only water and sand live in the background. No fixed coral is baked into it.
    background=np.zeros_like(a);last=np.array([115.,75.,115.])
    crest=np.interp(np.arange(W)/W,[p[0]for p in CREST],[p[1]*H for p in CREST])
    for y in range(H):
        samples=a[y,(y<crest-30)]
        if len(samples)>80 and y<350:last=np.median(samples,axis=0)
        background[y]=last*np.array([1-.00015*y,1-.00012*y,1-.0001*y])
    background=background*(1-sand[:,:,None])+a*sand[:,:,None]
    warm=Image.fromarray(np.uint8(np.clip(background,0,255)))
    warm.save(OUT/'water-sunset.webp',quality=74,method=6)
    cool=np.asarray(warm,dtype=float);luminance=cool@np.array([.2126,.7152,.0722])
    blue=np.stack([luminance*.20+8,luminance*.75+28,luminance*1.05+38],-1)
    water=1-sand
    cool=cool*(1-water[:,:,None])+blue*water[:,:,None]
    Image.fromarray(np.uint8(np.clip(cool,0,255))).save(OUT/'water-day.webp',quality=74,method=6)
    cfg['softCoral']=None
    cfg['notes']='Eight finite mid-ground formations with registered swept collision volumes, depth parallax and a clearance-validated navigation graph. Water/sand background contains no reef.'
    (ROOT/'roku/scenes/tank.json').write_text(json.dumps(cfg,indent=2)+'\n')
    occ={'cell':8,'rows':grid(union),'planes':planes}
    (ROOT/'roku/scenes/occupancy.json').write_text(json.dumps(occ,separators=(',',':')))
    build_navigation(occ)
    for name in ['reef-mid.webp','reef-front.webp','soft-coral.webp']:(OUT/name).unlink(missing_ok=True)
    mask=union
    for name,size in [('icon-fhd',(540,405)),('icon-hd',(290,218)),('icon-sd',(214,144)),('splash-fhd',(1920,1080)),('splash-hd',(1280,720)),('splash-sd',(720,480))]:
        pic=im.resize(size,Image.Resampling.LANCZOS) if name.startswith('icon') else splash(size)
        pic.save(OUT/(name+'.jpg'),quality=91)
    for name in ['reef-mid-sunset.webp','reef-front-sunset.webp','soft-coral.png','soft-coral-sunset.png']:(OUT/name).unlink(missing_ok=True)
    Image.fromarray(np.uint8(mask*255)).resize((1024,576)).save(ROOT/'docs/previews/reef-mask.png')
    print('Eight navigable reef formations, pure-water backdrop and photographic sand ready',flush=True)


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
    xs=[220,440,700,960,1220,1500,1810];ys=[100,260,440,630,800];zs=[.12,.28,.42,.54,.72,.86,.94]
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
    (ROOT/'roku/scenes/navigation.json').write_text(json.dumps({'nodes':nodes,'clearance':'All species, maximum size/pitch/tail/fin pose; full camera sweep; 4px extra margin.'},separators=(',',':')))
    print('Connected clearance graph:',len(nodes),'nodes,',sum(len(n['edges'])for n in nodes)//2,'edges',flush=True)
