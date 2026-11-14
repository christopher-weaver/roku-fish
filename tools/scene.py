"""Close reef composition, registered depth masks and photographic sand."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageEnhance
from scipy.ndimage import gaussian_filter,gaussian_gradient_magnitude,watershed_ift,binary_erosion,binary_closing,maximum_filter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'roku/images'
SOURCE=ROOT/'assets/source/reef-close-reference.png'
W,H=2048,1152
CREST=[(0,.19),(.02,.15),(.04,.12),(.075,.085),(.12,.11),(.155,.19),(.19,.20),(.23,.32),(.25,.25),(.265,.14),(.28,.095),(.32,.075),(.38,.09),(.41,.12),(.46,.17),(.49,.24),(.535,.23),(.58,.15),(.61,.11),(.64,.055),(.68,.11),(.70,.08),(.72,.017),(.745,.05),(.765,.13),(.79,.135),(.82,.08),(.85,.10),(.88,.07),(.90,.13),(.91,.095),(.93,.12),(.94,.19),(.97,.27),(1,.27)]

def photo():
    im=Image.open(SOURCE).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    return ImageEnhance.Sharpness(ImageEnhance.Color(im).enhance(1.04)).enhance(1.10)

def matte(im):
    a=np.asarray(im,dtype=float);yy,xx=np.mgrid[:H,:W]
    crest=np.interp(np.arange(W)/W,[p[0]for p in CREST],[p[1]*H for p in CREST])[None,:]
    gradient=np.maximum.reduce([gaussian_gradient_magnitude(a[:,:,c],1.0) for c in range(3)])
    markers=np.zeros((H,W),dtype=np.int32)
    markers[yy<crest-75]=1;markers[:5,:]=1
    markers[yy>crest+100]=2
    regions=watershed_ift(np.uint8(np.clip(gradient*4,0,255)),markers)
    solid=binary_closing(regions==2,iterations=1)
    mask=gaussian_filter(solid.astype(float),.55)
    mask[binary_erosion(solid,iterations=2)]=1
    return mask

def build(splash):
    import waves
    im=photo();a=np.asarray(im,dtype=float);yy,xx=np.mgrid[:H,:W]
    mask=matte(im)
    sand=np.asarray(waves.sand_mask(),dtype=float)/255
    mask*=1-sand
    front=(yy>H*.59)|(((xx-W*.16)/(W*.16))**2+((yy-H*.65)/(H*.24))**2<1)|(((xx-W*.69)/(W*.18))**2+((yy-H*.63)/(H*.22))**2<1)
    mid=mask.copy();mid[front]=0
    near=mask.copy();near[~front]=0
    cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());cfg['layers']={}
    for name,alpha in [('mid',mid),('front',near)]:
        rgba=im.convert('RGBA');rgba.putalpha(Image.fromarray(np.uint8(alpha*255)))
        box=rgba.getchannel('A').getbbox();x,y,x1,y1=box
        rgba.crop(box).save(OUT/f'reef-{name}.webp',quality=74,method=6,exact=True)
        cfg['layers'][name]={'x':x,'y':y,'width':x1-x,'height':y1-y}
    # Keep original sand grain/ridges and sky; replace hidden reef in the rear plate
    # with soft ambient water rather than storing the same coral photograph twice.
    background=a.copy();open_water=mask<.05
    last=np.array([105.,70.,105.])
    for y in range(H):
        samples=a[y,open_water[y]&(sand[y]<.05)]
        if len(samples)>16 and y<H*.58:last=np.median(samples,axis=0)
        background[y]=a[y]*(1-mask[y,:,None])+last*mask[y,:,None]
        if y>=960:background[y]=a[y]
    warm=Image.fromarray(np.uint8(np.clip(background,0,255)))
    warm.save(OUT/'water-sunset.webp',quality=74,method=6)
    cool=np.asarray(warm,dtype=float);luminance=cool@np.array([.2126,.7152,.0722])
    blue=np.stack([luminance*.20+8,luminance*.75+28,luminance*1.05+38],-1)
    water=1-sand
    cool=cool*(1-water[:,:,None])+blue*water[:,:,None]
    Image.fromarray(np.uint8(np.clip(cool,0,255))).save(OUT/'water-day.webp',quality=74,method=6)
    # The white branching crown is a mid-depth object. Only its bright branches sway.
    box=(530,80,1090,470);soft=im.crop(box).convert('RGBA');sw,sh=soft.size
    rgb=np.asarray(soft,dtype=float)[:,:,:3]/255;maximum=rgb.max(axis=2);minimum=rgb.min(axis=2)
    white=np.clip((minimum-.44)/.22,0,1)*np.clip(1-(maximum-minimum)/.32,0,1)
    white=(white>.35).astype(float)*mask[box[1]:box[3],box[0]:box[2]]
    soft.putalpha(Image.fromarray(np.uint8(gaussian_filter(white,.6)*255)))
    # One high-detail crown texture is moved fractionally at runtime, avoiding
    # three copies of the same delicate branching detail.
    soft.save(OUT/'soft-coral.webp',quality=76,method=6,exact=True)
    sway=np.zeros((H,W));sway[box[1]:box[3],box[0]:box[2]]=np.asarray(soft.getchannel('A'))/255
    sway=maximum_filter(sway,size=5)
    cfg['softCoral']={'x':box[0],'y':box[1]-36,'frameWidth':sw,'frameHeight':sh,'frames':1,'depth':.48,'image':'pkg:/images/soft-coral.webp'}
    cfg['notes']='Close continuous reef composed from the user reference. Fractional placement keeps the existing 240-second horizontal camera cycle smooth.'
    (ROOT/'roku/scenes/tank.json').write_text(json.dumps(cfg,indent=2)+'\n')
    mid=np.maximum(mid,sway)
    def grid(alpha):
        return [''.join('#' if np.any(alpha[y:y+8,x:x+8]>.2) else '.' for x in range(0,W,8))for y in range(0,H,8)]
    occ={'cell':8,'rows':grid(np.maximum(mid,near)),'planes':[{'z':.48,'halfDepth':.025,'rows':grid(mid)},{'z':.78,'halfDepth':.025,'rows':grid(near)}]}
    (ROOT/'roku/scenes/occupancy.json').write_text(json.dumps(occ,separators=(',',':')))
    for name,size in [('icon-fhd',(540,405)),('icon-hd',(290,218)),('icon-sd',(214,144)),('splash-fhd',(1920,1080)),('splash-hd',(1280,720)),('splash-sd',(720,480))]:
        pic=im.resize(size,Image.Resampling.LANCZOS) if name.startswith('icon') else splash(size)
        pic.save(OUT/(name+'.jpg'),quality=91)
    for name in ['reef-mid-sunset.webp','reef-front-sunset.webp','soft-coral.png','soft-coral-sunset.png']:(OUT/name).unlink(missing_ok=True)
    Image.fromarray(np.uint8(mask*255)).resize((1024,576)).save(ROOT/'docs/previews/reef-mask.png')
    print('Close continuous reef, photographic sand ridges and registered depth masks ready',flush=True)
