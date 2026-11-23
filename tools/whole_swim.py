"""Bake complete S / neutral / inverse-S body images from immutable mesh views.

No runtime body slices. Pixel colors/alpha come directly from the approved rest
atlases; each column moves as a whole, and native opacity interpolates the poses.
Requires Pillow, numpy and scipy; compressed output can vary with libwebp version.
"""
import json,math,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
root=Path(__file__).resolve().parents[1]
REST=root/'assets/source/fish-rest'
out=root/'work/whole-swim-regenerated';out.mkdir(parents=True,exist_ok=True)
rest=json.loads((REST/'species.json').read_text())
spec=json.loads((root/'roku/scenes/species.json').read_text());catalog={};total=0
for name,sp in spec.items():
 src=Image.open(REST/(name+'.webp')).convert('RGBA');unique={};pieces=[];frames=[];bycoords={}
 for i,f in enumerate(rest[name]['frames']):
  key=(f['x'],f['y'])
  if key in bycoords:
   frames.extend([dict(v,yaw=f['yaw']) for v in bycoords[key]]);continue
  original=src.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']));pixels=np.asarray(original)
  yy,xx=np.mgrid[:f['h']+12,:f['w']];xx=xx.astype(float);yy=yy.astype(float)-6
  sign=1 if math.cos(sp['bodyAngles'][i])>=0 else -1
  u=np.clip(.5-sign*(xx-f['anchorX'])/(sp['frameW']*.9),0,1)
  amp=sp['renderLength']*.009*abs(math.cos(sp['bodyAngles'][i]));poses=[]
  for pose in range(3):
   displacement=(pose-1)*amp*u*u*np.sin(0-u*2*math.pi)
   im=Image.fromarray(np.stack([map_coordinates(pixels[:,:,c],[yy-displacement,xx],order=0,mode='constant',cval=0)for c in range(4)],axis=2))
   box=im.getchannel('A').getbbox();box=(max(0,box[0]-2),max(0,box[1]-2),min(im.width,box[2]+2),min(im.height,box[3]+2));im=im.crop(box)
   ax=f['anchorX']-box[0];ay=f['anchorY']+6-box[1];digest=hashlib.sha256(im.tobytes()+str((ax,ay,im.size)).encode()).hexdigest()
   if digest not in unique:unique[digest]=len(pieces);pieces.append((im,ax,ay))
   poses.append(dict(piece=unique[digest],yaw=f['yaw'],pose=pose,flipX=False))
  bycoords[key]=poses;frames.extend(poses)
 # Shelf pack without repeated atlas allocations.
 pages=[];placements=[];x=y=rowh=0;page=0
 for im,ax,ay in pieces:
  if x+im.width+4>2048:x=0;y+=rowh+4;rowh=0
  if y+im.height+4>2048:pages.append((2048,y+rowh+4));page+=1;x=y=rowh=0
  placements.append(dict(page=page,x=x+2,y=y+2,w=im.width,h=im.height,anchorX=ax,anchorY=ay))
  x+=im.width+4;rowh=max(rowh,im.height)
 pages.append((2048,y+rowh+4));images=[]
 for page,size in enumerate(pages):
  atlas=Image.new('RGBA',size)
  for (im,ax,ay),p in zip(pieces,placements):
   if p['page']==page:atlas.paste(im,(p['x'],p['y']))
  path=out/f'{name}-swim-{page}.webp';atlas.save(path,lossless=True,quality=100,method=6,exact=True);images.append(str(path));total+=path.stat().st_size
 frames=[dict(placements[v.pop('piece')],**v)for v in frames]
 catalog[name]={'frames':frames,'images':images,'sizes':pages,'bytes':sum(Path(p).stat().st_size for p in images)}
 if len(pages)!=1:raise ValueError('Whole body atlas exceeds a single Roku texture: '+name)
 target=root/'roku'/sp['image'][5:];shutil.copy2(images[0],target)
 sp.update(frames=frames,poseCount=3,width=pages[0][0],height=pages[0][1],bodyRenderMode='whole-swim',bodySwimAmplitude=.009)
 print(name,len(pieces),pages,catalog[name]['bytes'],flush=True)
(root/'roku/scenes/species.json').write_text(json.dumps(spec,indent=2));print('TOTAL',total,flush=True)
from catalog import catalog as write_catalog
write_catalog()
