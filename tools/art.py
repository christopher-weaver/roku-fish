"""Deterministic offline plates, masks, soft-coral poses and effect sprites.
Source photographs are checked in; no generation service is needed to rebuild.
"""
from pathlib import Path
import json, math, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from scipy.ndimage import gaussian_filter, binary_fill_holes, binary_closing, binary_erosion, label
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/source'; OUT=ROOT/'roku/images'; OUT.mkdir(parents=True,exist_ok=True)
W,H=2048,1152

def sunset(a):
    f=np.asarray(a.convert('RGB'),np.float32)/255
    lum=f@np.array([.2126,.7152,.0722])
    blue=np.clip((f[:,:,2]-f[:,:,0])*2.3,0,1)
    # Warm red / violet water, amber highlights, preserving luminance detail.
    warm=np.stack([.98*lum+.24,.34*lum+.06,.40*lum+.12],-1)
    g=f*(1-blue[:,:,None]*.73)+warm*blue[:,:,None]*.73
    g=g*np.array([1.12,.91,.96])+lum[:,:,None]*np.array([.055,.012,.012])
    return ImageEnhance.Color(Image.fromarray(np.uint8(np.clip(g,0,1)*255))).enhance(1.18)

def splash(size):
    from PIL import ImageFont
    w,h=size;y,x=np.mgrid[:h,:w];glow=np.exp(-(((x-w*.55)/(w*.65))**2+((y-h*.8)/(h*.7))**2))
    a=np.zeros((h,w,3));a[:]=[24,20,33];a+=glow[:,:,None]*np.array([44,13,18]);im=Image.fromarray(np.uint8(a));d=ImageDraw.Draw(im)
    try:
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',int(w*.065))
        sub=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',int(w*.015))
    except OSError:
        font=ImageFont.load_default(size=int(w*.065));sub=ImageFont.load_default(size=int(w*.015))
    d.text((w/2,h*.47),'Deep Reef',anchor='mm',font=font,fill=(255,215,196))
    d.text((w/2,h*.59),'S U N S E T   A Q U A R I U M',anchor='mm',font=sub,fill=(192,148,150))
    return im

def build():
    reef=Image.open(SRC/'reef-original.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    empty=Image.open(SRC/'empty-original.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    a=np.asarray(reef,dtype=float); yy,xx=np.mgrid[:H,:W];u=xx/W;v=yy/H
    # Hand-reviewed silhouette envelopes. Blue-water rejection retains fine branches and caves.
    left=[(0,.255),(.08,.23),(.14,.18),(.23,.29),(.27,.40),(.29,.5),(.36,.60),(.43,.74),(.44,.88),(0,.98)]
    right=[(.51,.79),(.57,.65),(.65,.49),(.71,.31),(.74,.17),(.84,.12),(.9,.22),(1,.21),(1,1),(.5,1)]
    env=Image.new('L',(W,H));d=ImageDraw.Draw(env)
    for p in [left,right]:d.polygon([(int(x*W),int(y*H))for x,y in p],fill=255)
    # Water is strongly cyan/blue. Keep neutral sand below the reef to hide cut bases.
    water=np.clip((a[:,:,2]-a[:,:,0]-16)/30,0,1)*np.clip((a[:,:,1]-a[:,:,0]-10)/24,0,1)
    mask=np.array(env,dtype=float)/255*(1-water)
    # Texture in porous reef stays opaque; isolated water holes stay transparent.
    mask=np.clip(gaussian_filter(mask,.6)*1.8,0,1)
    base=np.clip((v-.82)/.11,0,1)*np.array(env)/255
    mask=np.maximum(mask,base)
    # Close tiny cyan texture holes inside solid coral, preserving actual archways.
    core=binary_closing(mask>.22,iterations=2)
    holes=binary_fill_holes(core)&~core
    components,n=label(holes);counts=np.bincount(components.ravel())
    small=counts<=4096;small[0]=False
    core|=small[components]
    mask=np.maximum(mask,gaussian_filter(core.astype(float),.6))
    mask[binary_erosion(core,iterations=2)]=1
    # Split back rock ledges and front anemone / low coral into two actual occlusion surfaces.
    front=(v>.67)&((u<.33)|(u>.82))
    # The swaying soft coral is drawn at the front plane, including its crown.
    soft_envelope=Image.new('L',(W,H));sd=ImageDraw.Draw(soft_envelope)
    sd.polygon([(405,975),(405,770),(455,650),(510,610),(570,650),(630,690),(705,860),(710,975)],fill=255)
    front|=np.asarray(soft_envelope)>0
    mid=mask.copy(); mid[front]=0
    near=mask.copy();near[~front]=0
    reef=ImageEnhance.Color(reef).enhance(1.28)
    reef=ImageEnhance.Contrast(reef).enhance(1.04)
    for name,alpha in [('reef-mid',mid),('reef-front',near)]:
        for suffix,colors in [('',reef),('-sunset',sunset(reef))]:
            im=colors.convert('RGBA');im.putalpha(Image.fromarray(np.uint8(alpha*255)))
            # WebP keeps lossless alpha and a compact photograph on Roku OS 9.4+.
            im.crop((0,160,W,H)).save(OUT/(name+suffix+'.webp'),quality=70,method=6,exact=True)
    reef.save(OUT/'water-day.jpg',quality=93,optimize=True)
    sunset(reef).save(OUT/'water-sunset.jpg',quality=93,optimize=True)
    # Soft coral: original image's cream soft coral, cut into a local registered sprite.
    box=(375,605,725,975)
    soft=reef.crop(box).convert('RGBA'); w,h=soft.size
    local=Image.new('L',(w,h));dd=ImageDraw.Draw(local)
    dd.polygon([(45,350),(35,175),(85,50),(135,15),(185,55),(245,95),(318,260),(330,370)],fill=255)
    local=local.filter(ImageFilter.GaussianBlur(8));soft.putalpha(local)
    atlas=Image.new('RGBA',(w*3,h))
    for phase in range(3):
        # Scan-line deformation leaves attachment fixed while the crown sways.
        dst=Image.new('RGBA',(w,h))
        for y in range(h):
            shift=int(math.sin(phase*2*math.pi/3)*5*(1-y/h)**1.8)
            dst.paste(soft.crop((0,y,w,y+1)),(shift,y))
        atlas.paste(dst,(phase*w,0))
    atlas.save(OUT/'soft-coral.png',optimize=True)
    warm=sunset(atlas).convert('RGBA');warm.putalpha(atlas.getchannel('A'));warm.save(OUT/'soft-coral-sunset.png',optimize=True)
    # Small periodic precomputed caustic tiles, blue noise-like gentle highlights.
    for k in range(8):
        y,x=np.mgrid[:192,:384];t=k*2*math.pi/8
        f=np.sin(x/23+np.sin(y/19+t)*1.7+t)+np.cos(y/17+np.sin(x/31-t)*1.4)
        al=np.uint8(np.exp(-((np.abs(f)-.13)/.14)**2)*38)
        c=np.zeros((192,384,4),dtype=np.uint8);c[:,:,:3]=[255,225,195];c[:,:,3]=al
        Image.fromarray(c).filter(ImageFilter.GaussianBlur(1)).save(OUT/f'caustic-{k}.png')
    y,x=np.mgrid[:512,:128];a=np.exp(-((x-64)/28)**2)*(1-y/512)**1.5
    ray=np.zeros((512,128,4),dtype=np.uint8);ray[:,:,:3]=[255,210,190];ray[:,:,3]=(a*60).astype('uint8');Image.fromarray(ray).save(OUT/'ray.png')
    for name,size in [('mote',8),('bubble',32)]:
        im=Image.new('RGBA',(size,size));d=ImageDraw.Draw(im)
        if name=='bubble':
            d.ellipse((2,2,size-3,size-3),outline=(220,235,255,120),width=2);d.arc((4,3,size-7,size-7),200,270,fill=(255,245,240,175),width=2)
        else:d.ellipse((2,2,5,5),fill=(255,225,220,120));im=im.filter(ImageFilter.GaussianBlur(.7))
        im.save(OUT/(name+'.png'))
    # Seamless drifting wavelets at the water surface, faded into the open water.
    surface=Image.new('RGBA',(2048,240))
    yy,xx=np.mgrid[:80,:512];envelope=np.clip(1-yy/80,0,1)**1.5
    for frame in range(12):
        phase=frame*2*math.pi/12
        ribbons=np.zeros((80,512),dtype=float)
        for layer in range(4):
            ridge=10+layer*17+3*np.sin(xx*2*math.pi/512*(layer+1)+phase)+2*np.sin(xx*4*math.pi/512-phase+layer)
            ribbons+=np.exp(-((yy-ridge)/1.2)**2)*(.7+.3*np.cos(xx*2*math.pi/512+phase+layer))
        rgba=np.zeros((80,512,4),dtype=np.uint8);rgba[:,:,:3]=[255,245,235];rgba[:,:,3]=np.uint8(np.clip(ribbons*envelope*86,0,110))
        surface.paste(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(.7)),((frame%4)*512,(frame//4)*80))
    surface.save(OUT/'surface-ripples.png',optimize=True)
    # Fine, conservative per-plane maps use ANY occupied pixel, never a cell average.
    # Include every sway pose, so transparent holes / thin branches cannot be crossed.
    sway=np.zeros((H,W),dtype=float)
    for pose in range(3):
        alpha=np.asarray(atlas.crop((pose*350,0,(pose+1)*350,370)).getchannel('A'))/255
        sway[605:975,375:725]=np.maximum(sway[605:975,375:725],alpha)
    near=np.maximum(near,sway)
    def grid(alpha,cell=8):
        return [''.join('#' if np.any(alpha[y:y+cell,x:x+cell]>.2) else '.' for x in range(0,W,cell)) for y in range(0,H,cell)]
    occupancy={'cell':8,'rows':grid(np.maximum(mid,near)), 'planes':[
        {'z':.48,'halfDepth':.025,'rows':grid(mid)},
        {'z':.78,'halfDepth':.025,'rows':grid(near)}]}
    (ROOT/'roku/scenes/occupancy.json').write_text(json.dumps(occupancy,separators=(',',':')))
    # Warm dappled sunlight is registered to terrain, including rock and sand.
    positions=[(60,250),(300,420),(80,720),(1580,260),(1440,560),(1700,760),(750,870),(1050,830)]
    terrain=np.maximum(mask,np.clip((v-.70)/.09,0,1)*(np.asarray(reef,dtype=float)[:,:,0]+np.asarray(reef,dtype=float)[:,:,1]>110))
    dapple=Image.new('RGBA',(1024,1152));py,px=np.mgrid[:96,:128]
    fade=np.sin(np.pi*(px+.5)/128)**2*np.sin(np.pi*(py+.5)/96)**2
    for frame in range(12):
        phase=frame*2*np.pi/12
        for patch,(left,top) in enumerate(positions):
            ground=Image.fromarray(np.uint8(terrain[top:top+240,left:left+320]*255)).resize((128,96),Image.Resampling.LANCZOS)
            waves=np.sin(px/13+np.sin(py/17+phase+patch)*1.3+phase)+np.cos(py/11+np.sin(px/19-phase)*1.1-phase+patch)
            spots=np.clip((waves+.6)/2.5,0,1)**1.5
            rgba=np.zeros((96,128,4),dtype=np.uint8);rgba[:,:,:3]=[255,226,165]
            rgba[:,:,3]=np.uint8(spots*fade*np.asarray(ground)/255*110)
            dapple.paste(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(1.2)),(patch*128,frame*96))
    dapple.save(OUT/'sun-dapple.png',optimize=True)
    (ROOT/'roku/scenes/dapple.json').write_text(json.dumps({'positions':positions,'frames':12,'period':24,'width':128,'height':96,'scale':2.5}))
    for name,size in [('icon-fhd',(540,405)),('icon-hd',(290,218)),('icon-sd',(214,144)),('splash-fhd',(1920,1080)),('splash-hd',(1280,720)),('splash-sd',(720,480))]:
        im=sunset(reef).resize(size,Image.Resampling.LANCZOS)
        if name.startswith('icon'):
            d=ImageDraw.Draw(im);d.rounded_rectangle((size[0]*.12,size[1]*.72,size[0]*.88,size[1]*.91),10,fill=(26,19,40));
            from PIL import ImageFont
            try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',int(size[0]*.075))
            except OSError:font=ImageFont.load_default(size=int(size[0]*.075))
            d.text((size[0]*.5,size[1]*.81),'Deep Reef',anchor='mm',font=font,fill=(255,215,194))
        if name.startswith("splash"):im=splash(size)
        im.save(OUT/(name+'.jpg'),quality=91)
    for old in OUT.glob('reef-*.png'):old.unlink()
    print('Reef plates, two occlusion surfaces, three coral poses, eight caustics: ready')
if __name__=='__main__':build()
