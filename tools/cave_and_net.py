"""Offline cave inhabitant, inset shadow and periodic water-net shadow artwork."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import label
import imagequant
ROOT=Path(__file__).resolve().parents[1]
def build():
 from connected_scene import source_reef
 src=ROOT/'assets/source/cave-eel-original.png';out=ROOT/'roku/images'
 im=Image.open(src).convert('RGBA');a=np.array(im.getchannel('A'));a[a<8]=0;im.putalpha(Image.fromarray(a));im=im.crop(im.getchannel('A').getbbox()).resize((114,140),Image.Resampling.LANCZOS)
 imagequant.quantize_pil_image(im,max_colors=160,dithering_level=0,max_quality=95).convert('RGBA').save(out/'cave-eel.webp',lossless=True,method=6,exact=True)
 alpha=np.asarray(source_reef().getchannel('A'));labs,_=label(alpha<40);component=labs[850,773];assert component not in [0,labs[0,0]],"Cave anchor must be inside the enclosed tunnel"
 mask=Image.fromarray(np.uint8(labs[808:907,715:831]==component)*255).filter(ImageFilter.GaussianBlur(.5));yy,xx=np.mgrid[:99,:116]
 rgba=np.zeros((99,116,4),dtype='uint8');shade=np.clip((xx-58)**2/160+(99-yy)/8,0,25)
 rgba[:,:,:3]=np.stack((16+shade*.65,9+shade*.42,20+shade*.8),axis=2).astype('uint8');rgba[:,:,3]=np.asarray(mask);Image.fromarray(rgba).save(out/'cave-interior.png',optimize=True)
 net=Image.new('RGBA',(1056,528));y,x=np.mgrid[:128,:128];u=x*2*np.pi/128;v=y*2*np.pi/128
 rng=np.random.default_rng(731);sites=np.array([(col*32+16+rng.uniform(-8,8),row*32+16+rng.uniform(-8,8),rng.uniform(0,2*np.pi))for row in range(4)for col in range(4)])
 for frame in range(32):
  phase=frame*2*np.pi/32
  wx=x+4*np.sin(v+phase)+2*np.sin(2*v-phase)
  wy=y+4*np.sin(u-phase)+2*np.cos(2*u+phase)
  distances=[]
  for sx,sy,offset in sites:
   dx=(wx-sx-3*np.sin(phase+offset)+64)%128-64
   dy=(wy-sy-3*np.cos(phase+offset)+64)%128-64
   distances.append(np.sqrt(dx*dx+dy*dy))
  nearest=np.partition(np.stack(distances),1,axis=0)[:2];gap=np.abs(nearest[1]-nearest[0])
  mesh=np.exp(-(gap/1.45)**2)*(.83+.17*np.sin(u+v+phase)**2)
  rgba=np.zeros((128,128,4),dtype='uint8');rgba[:,:,:3]=[18,29,40];rgba[:,:,3]=np.uint8(mesh*62)
  from scipy.ndimage import gaussian_filter
  rgba[:,:,3]=np.uint8(gaussian_filter(rgba[:,:,3].astype(float),.48,mode='wrap'))
  net.paste(Image.fromarray(np.pad(rgba,((2,2),(2,2),(0,0)),mode='wrap')),((frame%8)*132,(frame//8)*132))
 imagequant.quantize_pil_image(net,max_colors=16,dithering_level=0,max_quality=95).convert('RGBA').save(out/'wave-net.webp',lossless=True,method=6,exact=True)
 print('Cave eel, tunnel interior and 32 phase-matched net shadows built',flush=True)
if __name__=='__main__':build()
