"""One periodic water-height field drives surface waves and sand caustics offline."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import gaussian_filter
ROOT=Path(__file__).resolve().parents[1]
FRAMES=32;PERIOD=8.0

def sand_mask(size=(2048,1152)):
    im=Image.new('L',(2048,1152));ImageDraw.Draw(im).polygon([(0,971),(300,995),(640,986),(900,1000),(1140,1030),(1420,995),(1780,980),(2048,975),(2048,1152),(0,1152)],fill=255)
    im=im.filter(ImageFilter.GaussianBlur(8))
    tank=ROOT/'roku/scenes/tank.json'
    if tank.exists():
        occupied=np.zeros((1152,2048),dtype=float)
        for formation in json.loads(tank.read_text()).get('formations',[]):
            from formation_frames import footprint as formation_footprint
            footprint=formation_footprint(formation)
            matte=Image.new('L',(2048,1152));matte.paste(footprint,(formation['x'],formation['y']))
            occupied=np.maximum(occupied,np.asarray(matte,dtype=float)/255)
        im=Image.fromarray(np.uint8(np.asarray(im)*(1-occupied)))
    return im.resize(size,Image.Resampling.LANCZOS)

def height(x,phase):
    a=2*np.pi*x/512-phase
    return np.sin(a)+.38*np.sin(2*a+phase*3+.7)+.16*np.sin(3*a-phase*2+1.1)

def build():
    out=ROOT/'roku/images'
    surface=Image.new('RGBA',(2048,512))
    caustics=Image.new('RGBA',(2048,96))
    shadows=Image.new('RGBA',(2048,96))
    sy,sx=np.mgrid[:128,:256];fy,fx=np.mgrid[:24,:256]
    ground=np.asarray(sand_mask().crop((0,960,2048,1152)).resize((256,24),Image.Resampling.LANCZOS),dtype=float)/255
    rgb=np.asarray(Image.open(ROOT/'assets/source/background-matched-sunset.png').convert('RGB').resize((2048,1152),Image.Resampling.LANCZOS).crop((0,960,2048,1152)).resize((256,24)),dtype=float)
    luminance=gaussian_filter(rgb@np.array([.2126,.7152,.0722]),1.5)
    ridge_detail=np.clip((luminance-gaussian_filter(luminance,4))/18+.5,0,1)
    for frame in range(FRAMES):
        phase=frame*2*np.pi/FRAMES
        depth=sy/48
        z=depth*depth*75
        dx=np.zeros((128,256));dz=np.zeros_like(dx)
        for kx,kz,speed,amp,offset in [(1,1,1,.45,0),(2,-1,-2,.20,1.7),(3,2,3,.09,.8),(5,-3,-1,.04,2.8)]:
            arg=2*np.pi*(kx*sx/256+kz*z/180)+speed*phase+offset
            dx+=amp*kx*np.cos(arg);dz+=amp*kz*np.cos(arg)
        reflection=np.clip(.56+dz*.28+dx*.12,0,1)
        glint=np.exp(-((dz+.35+dx*.18)/.18)**2)
        fade=np.clip((48-sy)/28,0,1)**1.7
        alpha=np.clip((30+reflection*70+glint*100)*fade,0,190)
        rgba=np.zeros((128,256,4),dtype=np.uint8)
        dark=np.array([58,74,91]);light=np.array([244,239,232])
        rgba[:,:,:3]=np.uint8(dark+(light-dark)*np.clip(reflection*.75+glint*.35,0,1)[:,:,None])
        rgba[:,:,3]=np.uint8(alpha)
        surface.paste(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(.5)),((frame%8)*256,(frame//8)*128))
        # Preserve the photograph's ridges. Waves gently change the light on them,
        # rather than replacing the sand texture with a large moving bright net.
        depth=fy/24
        signal=(.75*height(fx*8+depth*40,phase)+.25*np.cos(fy/7+phase))/1.5
        rgba=np.zeros((24,256,4),dtype=np.uint8)
        rgba[:,:,:3]=np.where((signal>0)[:,:,None],np.array([255,235,197]),np.array([35,24,32]))
        rgba[:,:,3]=np.uint8(np.clip(np.abs(signal)*ground*(18+30*ridge_detail),0,48))
        caustics.paste(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(.4)),((frame%8)*256,(frame//8)*24))
        # Wave troughs bend and sweep a translucent shadow across the existing
        # photographed sand highlights. Width and strength vary with the SAME
        # periodic wave field as the surface; all coral remains masked out.
        warped=fx*8+depth*105+24*height(fx*3+fy*6,phase)
        trough=np.clip((-height(warped,phase)-.10)/1.15,0,1)**1.4
        strength=.72+.28*np.sin(phase+fx/37+fy/8)**2
        highlight=np.clip(luminance/180,.45,1)*(0.65+0.35*ridge_detail)
        rgba=np.zeros((24,256,4),dtype=np.uint8);rgba[:,:,:3]=[28,24,43]
        rgba[:,:,3]=np.uint8(np.clip(trough*strength*highlight*ground*105,0,96))
        shadows.paste(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(.32)),((frame%8)*256,(frame//8)*24))
    shadows.save(out/'sand-wave-shadows.png',optimize=True)
    surface.save(out/'surface-waves.png',optimize=True)
    caustics.save(out/'sand-caustics.png',optimize=True)
    (ROOT/'roku/scenes/waves.json').write_text(json.dumps({'frames':FRAMES,'period':PERIOD,'maxWaveY':96,'surface':{'width':256,'height':128,'columns':8,'scale':4,'scaleY':2},'sand':{'width':256,'height':24,'columns':8,'scale':8,'x':0,'y':960},'shadow':{'width':256,'height':24,'columns':8,'scale':8,'x':0,'y':960}},indent=2)+'\n')
    for pattern in ['caustic-*.png','surface-ripples.png','sun-dapple.png']:
        for p in out.glob(pattern):p.unlink()
    (ROOT/'roku/scenes/dapple.json').unlink(missing_ok=True)
    print('32 synchronized surface-wave / sand-refraction frames ready',flush=True)
if __name__=='__main__':build()
