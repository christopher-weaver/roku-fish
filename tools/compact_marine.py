"""Keep photographic marine art inside the native package budget."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imagequant
ROOT=Path(__file__).resolve().parents[1]
def compact(only=None):
 from formation_frames import frame
 p=ROOT/'roku/scenes/tank.json';cfg=json.loads(p.read_text())
 for f in cfg['formations']:
  if f['id']not in ['clam','sea-anemone'] or (only is not None and f['id']not in only):continue
  scale=.75 if f['id']=='sea-anemone'else 1.
  tw,th=round(f['width']*scale),round(f['height']*scale);cols=2044//(tw+4);capacity=cols*(2044//(th+4));cache={};shots=[]
  for i in range(f['frames']):shots.append(frame(f,i,cache).resize((tw,th),Image.Resampling.LANCZOS))
  pages=[]
  for first in range(0,len(shots),capacity):
   batch=shots[first:first+capacity];atlas=Image.new('RGBA',(cols*(tw+4)+4,((len(batch)+cols-1)//cols)*(th+4)+4))
   for i,im in enumerate(batch):atlas.paste(im,(2+i%cols*(tw+4),2+i//cols*(th+4)))
   a=np.array(atlas);a[:,:,3]=np.uint8(np.round(a[:,:,3]/17)*17);a[a[:,:,3]==0,:3]=0
   name=f"reef-{f['id']}-motion-{len(pages)}.webp";Image.fromarray(a).save(ROOT/'roku/images'/name,quality=54 if f['id']=='sea-anemone'else 75,method=6,exact=False);pages.append('pkg:/images/'+name)
  f.update(image=pages[0],images=pages,frameWidth=tw,frameHeight=th,columns=cols);f['animation'].update(framesPerPage=capacity,strideX=tw+4,strideY=th+4)
 p.write_text(json.dumps(cfg,indent=2)+'\n')
 if only is not None:return
 # Low-entropy branded menu artwork reserves scene quality for moving animals.
 fontpath=Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')
 for prefix,sizes in [('icon',[(540,405,'fhd'),(290,218,'hd'),(214,144,'sd')]),('splash',[(1920,1080,'fhd'),(1280,720,'hd'),(720,480,'sd')])]:
  for w,h,label in sizes:
   im=Image.new('RGB',(w,h),(46,31,55));d=ImageDraw.Draw(im)
   for y in range(h):
    u=y/max(1,h-1);d.line((0,y,w,y),fill=(int(76-30*u),int(40-9*u),int(63-8*u)))
   font=ImageFont.truetype(str(fontpath),int(h*.11));title='Deep Reef';box=d.textbbox((0,0),title,font=font);d.text(((w-box[2])/2,h*.43),title,font=font,fill=(245,205,190));im.save(ROOT/'roku/images'/f'{prefix}-{label}.jpg',quality=75,optimize=True)
 for name in ['surface-waves.png','sand-caustics.png']:
  p=ROOT/'roku/images'/name;im=Image.open(p).convert('RGBA');imagequant.quantize_pil_image(im,max_colors=32,dithering_level=0,max_quality=95).save(p,optimize=True)
if __name__=='__main__':compact()
