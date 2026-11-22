"""Soft perspective caustic shadows, restricted to receiving surfaces."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import minimum_filter
import imagequant
ROOT=Path(__file__).resolve().parents[1]

def field(x,y,time):
    # A tilted projector with a vanishing line above the image. Apparent cells
    # grow toward the foreground in both axes rather than forming a flat grid.
    depth=np.maximum(.135,(y+180)/1332)
    u=(x-1024)/(240*depth);v=-3.3/depth;p=time*2*np.pi/8
    a=np.sin(2*np.pi*u+.85*np.sin(2*np.pi*v+p)+p)
    b=np.sin(2*np.pi*v+.70*np.sin(2*np.pi*u-p)-p)
    return 72*(.60*np.exp(-a*a/.34)+.40*np.exp(-b*b/.55))

def conservative_mask(alpha):
    solid=(alpha>250).reshape(72,16,128,16).all(axis=(1,3))
    return minimum_filter(solid,size=3,mode='constant',cval=0)

def build():
    from formation_frames import footprint
    from waves import sand_mask
    tankpath=ROOT/'roku/scenes/tank.json';tank=json.loads(tankpath.read_text())
    sy,sx=np.mgrid[:72,:128];worldx=sx*16+8;worldy=sy*16+8
    for f in tank['formations']:
        if f.get('animation'):continue
        canvas=Image.new('L',(2048,1152));canvas.paste(footprint(f),(f['x'],f['y']));mask=conservative_mask(np.asarray(canvas));atlas=Image.new('RGBA',(1024,288))
        name='shadow-'+f['id']+'.webp'
        if not mask.any():
            f.pop('surfaceShadow',None);(ROOT/'roku/images'/name).unlink(missing_ok=True)
            print('Skipped empty surface shadow',f['id'],flush=True);continue
        for i in range(32):
            rgba=np.zeros((72,128,4),dtype='uint8');rgba[:,:,:3]=[18,23,32];rgba[:,:,3]=np.uint8(field(worldx,worldy,i/4)*mask)
            atlas.paste(Image.fromarray(rgba),((i%8)*128,(i//8)*72))
        # Quantize before cropping: every retained receiver pixel stays identical.
        compact=imagequant.quantize_pil_image(atlas,max_colors=24,dithering_level=0,max_quality=95).convert('RGBA')
        yy,xx=np.nonzero(mask);left=max(0,int(xx.min())-2);top=max(0,int(yy.min())-2)
        right=min(128,int(xx.max())+3);bottom=min(72,int(yy.max())+3);width=right-left;height=bottom-top
        cropped=Image.new('RGBA',(width*8,height*4))
        for i in range(32):
            x=i%8*128;y=i//8*72
            cropped.paste(compact.crop((x+left,y+top,x+right,y+bottom)),(i%8*width,i//8*height))
        cropped.save(ROOT/'roku/images'/name,lossless=True,method=6,exact=True)
        f['surfaceShadow']={'image':'pkg:/images/'+name,'width':width,'height':height,'columns':8,'scale':16,'x':left*16,'y':top*16,'frames':32}
        print('Surface-only shadow',f['id'],flush=True)
    ground=np.asarray(sand_mask().crop((0,960,2048,1152)),dtype=np.uint8)
    # Whole neighbourhood coverage makes interpolation incapable of leaking
    # beyond the physical sand receiver into water or coral silhouettes.
    safe=minimum_filter((ground>220).reshape(24,8,256,8).all(axis=(1,3)),size=3,mode='constant',cval=0)
    y,x=np.mgrid[:24,:256];atlas=Image.new('RGBA',(2048,96))
    for i in range(32):
        rgba=np.zeros((24,256,4),dtype='uint8');rgba[:,:,:3]=[18,23,32];rgba[:,:,3]=np.uint8(field(x*8+4,y*8+964,i/4)*safe)
        atlas.paste(Image.fromarray(rgba),((i%8)*256,(i//8)*24))
    imagequant.quantize_pil_image(atlas,max_colors=32,dithering_level=0,max_quality=95).save(ROOT/'roku/images/sand-wave-shadows.png',optimize=True)
    (ROOT/'roku/images/wave-net.webp').unlink(missing_ok=True)
    tankpath.write_text(json.dumps(tank,indent=2)+'\n')
if __name__=='__main__':build()
