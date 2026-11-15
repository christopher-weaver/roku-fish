"""Bake complete root-pinned mesh poses: no runtime bands or moving transforms."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
import moderngl,imagequant
ROOT=Path(__file__).resolve().parents[1]
VERT='''#version 330
in vec3 position;in vec2 uv;uniform float strength;uniform float amplitude;uniform float kind;
out vec2 texuv;
void main(){vec3 p=position;float v=clamp((p.y+1.0)*.5,0.0,1.0);float w=v*v;
float phase=uv.x*10.0+v*4.0;
p.x+=amplitude*w*(strength*(.76+.24*sin(phase))+.16*strength*strength*sin(phase+2.0));
p.y+=amplitude*.27*w*strength*sin(uv.x*8.0+v*3.0);
p.z+=amplitude*.35*w*strength*cos(phase+kind);
gl_Position=vec4(p.x,p.y,-p.z*.3,1);texuv=uv;}'''
FRAG='''#version 330
uniform sampler2D photo;in vec2 texuv;out vec4 color;
void main(){vec4 c=texture(photo,texuv);if(c.a<.02)discard;color=c;}'''
COUNT=65;SCALE=.75

def build():
 from connected_scene import marine,source_reef
 ctx=moderngl.create_standalone_context(backend='egl');p=ctx.program(vertex_shader=VERT,fragment_shader=FRAG);ctx.enable(moderngl.DEPTH_TEST)
 folder=ROOT/'assets/source/marine-renders';original=json.loads((folder/'views.json').read_text());tank=ROOT/'roku/scenes/tank.json';cfg=json.loads(tank.read_text());reef=source_reef().getchannel('A')
 for kind,(name,ox,oy,width,height,amplitude,period)in enumerate([('sea-fan',80,430,600,565,5.5,9.0),('sea-anemone',1330,815,285,215,4.0,7.5)]):
  base=original[name];image=marine(name,width,height);pad=8;tile=Image.new('RGBA',(width+pad*2,height+pad*2));tile.alpha_composite(image,(pad,pad));fw,fh=tile.size
  with np.load(folder/(name+'-volume.npz'))as mesh:vertices=np.hstack([mesh['vertices'],mesh['uv']]).astype('f4');faces=mesh['faces']
  vb=ctx.buffer(vertices.tobytes());ib=ctx.buffer(faces.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 2f','position','uv')],ib)
  tex=ctx.texture(tile.size,4,tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);tex.use()
  fbo=ctx.simple_framebuffer((fw*2,fh*2),components=4);fbo.use();p['amplitude'].value=amplitude*2/fw;p['kind'].value=float(kind)
  margin=8;bx=base['x']-(ox-pad);by=base['y']-(oy-pad);box=(bx-margin,by-margin,bx+base['width']+margin,by+base['height']+margin)
  dw=base['width']+margin*2;dh=base['height']+margin*2;scale=.5 if name=='sea-fan'else .75;tw=round(dw*scale);th=round(dh*scale)
  cols=2044//(tw+4);rows=2044//(th+4);capacity=cols*rows;shots=[];union=np.zeros((dh,dw),dtype=np.uint8)
  cover=np.asarray(reef.crop((ox-pad,oy-pad,ox-pad+fw,oy-pad+fh)))>250
  for index in range(COUNT):
   p['strength'].value=-1+index*2/(COUNT-1);fbo.clear(0,0,0,0,depth=1);vao.render()
   shot=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
   a=np.array(shot.getchannel('A'));a[a<6]=0
   if name=='sea-fan':a[cover]=0
   shot.putalpha(Image.fromarray(a));shot=shot.crop(box);union=np.maximum(union,np.asarray(shot.getchannel('A')))
   shots.append(shot.resize((tw,th),Image.Resampling.LANCZOS))
  pages=[]
  for first in range(0,COUNT,capacity):
   batch=shots[first:first+capacity];atlas=Image.new('RGBA',(cols*(tw+4)+4,math.ceil(len(batch)/cols)*(th+4)+4))
   for local,shot in enumerate(batch):atlas.paste(shot,(2+(local%cols)*(tw+4),2+(local//cols)*(th+4)))
   rgba=np.array(atlas);rgba[:,:,:3][rgba[:,:,3]==0]=0
   raw=ROOT/'work/marine-animation';raw.mkdir(parents=True,exist_ok=True);Image.fromarray(rgba).save(raw/f'{name}-{len(pages)}.png')
   compact=imagequant.quantize_pil_image(Image.fromarray(rgba),max_colors=64 if name=='sea-fan'else 80,dithering_level=0,max_quality=95)
   normalized=np.array(compact.convert('RGBA'));normalized[:,:,3][normalized[:,:,3]>245]=255
   filename=f'reef-{name}-motion-{len(pages)}.webp';Image.fromarray(normalized).save(ROOT/'roku/images'/filename,lossless=True,method=6,exact=True);pages.append('pkg:/images/'+filename)
  for formation in cfg['formations']:
   if formation['id']==name:
    formation.update(x=base['x']-margin,y=base['y']-margin,width=dw,height=dh,frameWidth=tw,frameHeight=th,columns=cols,frames=COUNT,image=pages[0],images=pages,animation={'period':period,'count':COUNT,'framesPerPage':capacity,'strideX':tw+4,'strideY':th+4,'gutter':2})
    formation.pop('motion',None);formation.pop('angles',None)
  Image.fromarray(union).save(folder/(name+'-motion-footprint.png'))
  for o in [vao,vb,ib,tex,fbo]:o.release()
  print(name,COUNT,'whole mesh poses',tw,th,'pages',len(pages),flush=True)
 tank.write_text(json.dumps(cfg,indent=2)+'\n')
 for name in original:(ROOT/'roku/images'/('reef-'+name+'.webp')).unlink(missing_ok=True)
 used={path.split('/')[-1]for f in cfg['formations']for path in f.get('images',[f['image']])}
 for path in (ROOT/'roku/images').glob('reef-*-motion-*.webp'):
  if path.name not in used:path.unlink()
if __name__=='__main__':build()
