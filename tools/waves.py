"""One periodic water-height field drives surface waves and sand caustics offline."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_dilation, gaussian_filter
ROOT=Path(__file__).resolve().parents[1]
FRAMES=32;PERIOD=8.0
FLOOR=[(0,1095),(230,1075),(320,1010),(800,935),(930,850),(1080,825),(1200,835),(1360,855),(1540,870),(1700,940),(1860,1000),(2048,1050),(2048,1152),(0,1152)]

def sand_mask(size=(2048,1152)):
    im=Image.new('L',(2048,1152));ImageDraw.Draw(im).polygon(FLOOR,fill=255)
    photo=Image.open(ROOT/'assets/source/reef-original.png').convert('RGB').resize((2048,1152),Image.Resampling.LANCZOS)
    rgb=np.asarray(photo,dtype=float)/255
    high=rgb.max(axis=2);low=rgb.min(axis=2)
    saturation=(high-low)/np.maximum(high,.001)
    luminance=rgb@np.array([.2126,.7152,.0722])
    sand=np.clip((.60-saturation)/.2,0,1)*np.clip((luminance-.22)/.10,0,1)
    alpha=np.asarray(im.filter(ImageFilter.GaussianBlur(9)),dtype=float)*gaussian_filter(sand,1)
    return Image.fromarray(np.uint8(alpha)).resize(size,Image.Resampling.LANCZOS)

def height(x,phase):
    a=2*np.pi*x/512-phase
    return np.sin(a)+.38*np.sin(2*a+phase*3+.7)+.16*np.sin(3*a-phase*2+1.1)

def flatten_sand(photo):
    # Inpaint only bright static caustic ridges, preserving sand grains and shadows.
    raw=np.asarray(photo,dtype=float)
    low=np.asarray(photo.filter(ImageFilter.GaussianBlur(12)),dtype=float)
    luminance=np.array([.2126,.7152,.0722])
    floor=np.asarray(sand_mask())
    ridge=((raw-low)@luminance>7)&(floor>80)
    ridge=binary_dilation(ridge,iterations=3)
    known=(~ridge).astype(float);denominator=gaussian_filter(known,8)
    filled=np.stack([gaussian_filter(raw[:,:,c]*known,8)/np.maximum(denominator,.001)for c in range(3)],-1)
    grain=np.clip(raw-np.asarray(photo.filter(ImageFilter.GaussianBlur(1.5)),dtype=float),-4,4)
    local=Image.fromarray(np.uint8(np.clip(filled+grain,0,255)))
    edge=Image.fromarray(np.uint8(ridge)*255).filter(ImageFilter.GaussianBlur(1.5))
    corrected=Image.composite(local,photo,edge)
    return Image.composite(corrected,photo,sand_mask())

def build():
    out=ROOT/'roku/images'
    surface=Image.new('RGBA',(2048,512))
    caustics=Image.new('RGBA',(2048,704))
    sy,sx=np.mgrid[:128,:256];fy,fx=np.mgrid[:88,:512]
    ground=np.asarray(sand_mask().crop((0,800,2048,1152)).resize((512,88),Image.Resampling.LANCZOS),dtype=float)/255
    for frame in range(FRAMES):
        phase=frame*2*np.pi/FRAMES
        crest=np.zeros((128,256));trough=np.zeros_like(crest)
        for band in range(4):
            ridge=13+band*25+(8-band*.8)*height(sx*2+band*43,phase)
            crest+=np.exp(-((sy-ridge)/1.6)**2)*(1-.16*band)
            trough+=np.exp(-((sy-ridge-4)/3.0)**2)*.45
        fade=np.clip(1-sy/128,0,1)**1.6
        alpha=np.clip((crest*145+trough*85)*fade,0,155)
        rgba=np.zeros((128,256,4),dtype=np.uint8)
        bright=crest>=trough
        rgba[:,:,:3]=np.where(bright[:,:,None],np.array([255,238,223]),np.array([62,48,75]))
        rgba[:,:,3]=np.uint8(alpha)
        surface.paste(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(.65)),((frame%8)*256,(frame//8)*128))
        # The same height field and phase refract into elongated moving floor lines.
        depth=fy/88
        bend=height(fx*4+depth*95,phase)
        cross=np.sin(fy/8+height(fx*4+60,phase)*1.3+phase)
        focus=bend+.65*cross
        light=np.exp(-((focus-.08)/.14)**2)*(.65+.35*np.cos(depth*3+phase))
        rgba=np.zeros((88,512,4),dtype=np.uint8);rgba[:,:,:3]=[255,240,210]
        rgba[:,:,3]=np.uint8(np.clip(light*ground*115,0,115))
        caustics.paste(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(.65)),((frame%4)*512,(frame//4)*88))
    surface.save(out/'surface-waves.png',optimize=True)
    caustics.save(out/'sand-caustics.png',optimize=True)
    (ROOT/'roku/scenes/waves.json').write_text(json.dumps({'frames':FRAMES,'period':PERIOD,'surface':{'width':256,'height':128,'columns':8,'scale':2},'sand':{'width':512,'height':88,'columns':4,'scale':4,'x':0,'y':800}},indent=2)+'\n')
    for pattern in ['caustic-*.png','surface-ripples.png','sun-dapple.png']:
        for p in out.glob(pattern):p.unlink()
    (ROOT/'roku/scenes/dapple.json').unlink(missing_ok=True)
    print('32 synchronized surface-wave / sand-refraction frames ready',flush=True)
if __name__=='__main__':build()
