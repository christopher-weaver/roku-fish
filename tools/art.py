"""Deterministic offline plates, masks, soft-coral poses and effect sprites.
Source photographs are checked in; no generation service is needed to rebuild.
"""
from pathlib import Path
import json, math, hashlib
import waves
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
    import connected_scene
    connected_scene.build(splash)
    waves.build()
    # Reuse the small bubble / mote / ray sources already bundled with the app.
    print('Close reef scene and wave-linked ridge lighting ready',flush=True)

if __name__=='__main__':build()
