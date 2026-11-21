"""Articulated, closed 3D clam valves, pearlescent tissue and event sprites."""
from pathlib import Path
import json,math
from io import BytesIO
import numpy as np
from PIL import Image
import moderngl,imagequant
from living_reef import Model,VS,FS,save
ROOT=Path(__file__).resolve().parents[1]
CENTER=np.array([1080.,987.,240.]);V=np.array([0.,.40,.916515]);UP=np.array([0.,-.916515,.40]);HINGE=CENTER-V*65

def valve(upper,opening):
 m=Model();sides=192;rows=36;v=[];colors=[];faces=[]
 # Outer and inner surfaces meet in a continuous rolled/scalloped rim.
 profile=[(r,False)for r in np.linspace(.008,1,rows)]+[(r,True)for r in np.linspace(1,.008,rows)]
 for r,inside in profile:
  for col in range(sides):
   a=col*2*np.pi/sides;flute=np.sin(9*a+.3)
   radius=r*(1+.038*flute*r*r);dome=(1-r*r)**.65
   height=(35*dome+12 if upper else -27*dome)+10*flute*r**3
   height+=(-4 if upper else 4)if inside else 0
   point=CENTER+np.array([152*radius*np.cos(a),0,0])+V*(73*radius*np.sin(a))+UP*height
   if upper:
    p=point-HINGE;angle=opening*.86;c=np.cos(angle);s=np.sin(angle)
    point=HINGE+[p[0],p[1]*c-p[2]*s,p[1]*s+p[2]*c]
   v.append(point)
   if inside:color=np.array([.30,.57,.52])*(.82+.13*np.sin(a*9+r*11))
   else:
    growth=.09*np.cos(r*103+np.sin(a*9))+.10*np.sin(a*9)
    color=np.array([.72,.66,.55])*(.86+growth)+np.array([.05,.035,.07])*np.sin(r*17+a*2)
   colors.append(color)
 for row in range(len(profile)-1):
  for i in range(sides):
   a=row*sides+i;b=row*sides+(i+1)%sides;c=a+sides;d=b+sides;faces.extend([(a,c,b),(b,c,d)])
 for i in range(1,sides-1):faces.extend([(0,i+1,i),((len(profile)-1)*sides,(len(profile)-1)*sides+i,(len(profile)-1)*sides+i+1)])
 m.add(v,np.array(faces)if upper else np.array(faces)[:,::-1],np.array(colors))
 # Thick soft mantle follows the irregular shell lip, with living colour.
 a=np.linspace(0,2*np.pi,385);path=[];palette=[]
 for angle in a:
  flute=np.sin(9*angle+.3);point=CENTER+np.array([152*1.038*np.cos(angle),0,0])+V*(73*1.038*np.sin(angle))+UP*((12 if upper else 0)+10*flute)
  if upper:
   pp=point-HINGE;co=np.cos(opening*.86);sn=np.sin(opening*.86);point=HINGE+[pp[0],pp[1]*co-pp[2]*sn,pp[1]*sn+pp[2]*co]
  path.append(point);palette.append(np.array([.35,.49,.48])*(.8+.17*np.sin(angle*31+.6*np.cos(angle*17))))
 m.tube(path,np.full(len(a),5.3),(.35,.49,.48),sides=12,row_colors=np.array(palette))
 return m

def model(opening):
 m=Model();m.sphere(CENTER+UP*2,(130,13,57),(.14,.18,.17),ridges=.025)
 for upper in [False,True]:
  part=valve(upper,opening);m.add(part.v,part.f,np.array(part.rgb))
 return m

def build():
 folder=ROOT/'assets/source/marine-renders';cfgpath=ROOT/'roku/scenes/tank.json';cfg=json.loads(cfgpath.read_text())
 ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST);noise_shader=FS.replace('void main(){','''float hash(vec3 p){p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z);}
float noise3(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
void main(){''').replace('float alpha=1.0;', 'grain=0.0;base*=.82+.25*noise3(world*.18)+.11*noise3(world*.83);float alpha=1.0;')
 p=ctx.program(vertex_shader=VS,fragment_shader=noise_shader);p['usePhoto'].value=0;p['tissue'].value=0;p['strength'].value=0
 bounds=np.concatenate([model(i).arrays()[0]for i in [0,1]]);x0,y0=np.floor(bounds[:,:2].min(axis=0)-5).astype(int);x1,y1=np.ceil(bounds[:,:2].max(axis=0)+5).astype(int);w,h=int(x1-x0),int(y1-y0);scale=.65;tw,th=round(w*scale),round(h*scale);cols=2044//(tw+4);capacity=cols*(2044//(th+4));p['stage'].value=(int(x0),int(y0),w,h)
 texture=ctx.texture((1,1),3,bytes([255]*3));texture.use();fb=ctx.simple_framebuffer((w*2,h*2),components=4);fb.use();shots=[];union=np.zeros((h,w),dtype='uint8')
 for i in range(65):
  m=model(i/64);v,n,f,rgb,flow=m.arrays()
  if i==0:
   save('clam-sculpted',m,folder);nv=v.copy();nv[:,0]=(v[:,0]-x0)/w*2-1;nv[:,1]=1-(v[:,1]-y0)/h*2;nv[:,2]/=100;np.savez_compressed(folder/'clam-volume.npz',vertices=nv,uv=np.column_stack([(v[:,0]-x0)/w,1-(v[:,1]-y0)/h]),faces=f)
   # Editable scene has the actual shell hinge as a shape key.
   dest=ROOT/'assets/source/reef-model';save('articulated-clam',m,dest);opened=model(1).arrays()[0];np.savez_compressed(dest/'clam-open.npz',vertices=opened);record=json.loads((dest/'model.json').read_text());record['objects']=[o for o in record['objects']if o['name']!='articulated-clam'];
   for o in record['objects']:
    if o['group']=='central-clam':o['group']='clam-rock-bed'
   record['objects'].append(dict(name='articulated-clam',group='central-clam',layer='clam',vertices=len(v),triangles=len(f),file='articulated-clam.npz',closed=True,sculpted=True));(dest/'model.json').write_text(json.dumps(record,indent=2)+'\n')
  vb=ctx.buffer(np.column_stack([v,n,rgb,flow]).astype('f4').tobytes());ib=ctx.buffer(f.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f','position','normal','rgb','flow')],ib);fb.clear(0,0,0,0,depth=1);vao.render();im=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((w,h),Image.Resampling.LANCZOS);a=np.array(im.getchannel('A'));a[a<6]=0;im.putalpha(Image.fromarray(a));union=np.maximum(union,a);shots.append(im.resize((tw,th),Image.Resampling.LANCZOS));vao.release();vb.release();ib.release()
 pages=[]
 for first in range(0,65,capacity):
  batch=shots[first:first+capacity];atlas=Image.new('RGBA',(cols*(tw+4)+4,math.ceil(len(batch)/cols)*(th+4)+4))
  for i,im in enumerate(batch):atlas.paste(im,(2+i%cols*(tw+4),2+i//cols*(th+4)))
  image=imagequant.quantize_pil_image(atlas,max_colors=64,dithering_level=0,max_quality=95).convert('RGBA');name=f'reef-clam-motion-{len(pages)}.webp';# Bound the new decorative atlas without changing fish texture quality.
  for quality in [84,80,76,72,68]:
   encoded=BytesIO();image.save(encoded,format='WEBP',quality=quality,method=6,exact=True)
   if encoded.tell()<=180000:break
  (ROOT/'roku/images'/name).write_bytes(encoded.getvalue());pages.append('pkg:/images/'+name)
 Image.fromarray(union).save(folder/'clam-motion-footprint.png')
 formation=dict(id='clam',x=int(x0),y=int(y0),width=w,height=h,frameWidth=tw,frameHeight=th,columns=cols,frames=65,image=pages[0],images=pages,z=.83,halfDepth=.025,parallax=1,rootY=1030,renderedMesh=True,meshVertices=len(v),meshTriangles=len(f),geometryType='closed articulated ridged bivalve shell',animation=dict(period=47,count=65,framesPerPage=capacity,strideX=tw+4,strideY=th+4,gutter=2))
 cfg['formations']=[f for f in cfg['formations']if f['id']!='clam']+[formation];cfg['formations'].sort(key=lambda f:f['z']);cfg['occlusionDepths']=[f['z']for f in cfg['formations']];cfgpath.write_text(json.dumps(cfg,indent=2)+'\n')
 # Small luminous sprites are loaded once; pearl has modeled spherical shading.
 y,x=np.mgrid[:40,:40];nx=(x-19.5)/17;ny=(y-19.5)/17;r2=nx*nx+ny*ny;nz=np.sqrt(np.clip(1-r2,0,1));light=np.clip(-nx*.35-ny*.5+nz*.8,0,1);spec=np.exp(-((nx+.30)**2+(ny+.40)**2)/.025);rgba=np.zeros((40,40,4),dtype='uint8');rgba[:,:,:3]=np.uint8(np.clip(np.array([180,196,196])[None,None,:]*(.58+.42*light[:,:,None])+spec[:,:,None]*60,0,255));rgba[:,:,3]=np.uint8(np.clip((1-r2)*15,0,1)*255);Image.fromarray(rgba).save(ROOT/'roku/images/clam-pearl.png',optimize=True)
 y,x=np.mgrid[:32,:32];r2=((x-15.5)/9)**2+((y-15.5)/9)**2;rgba=np.full((32,32,4),255,dtype='uint8');rgba[:,:,3]=np.uint8(np.exp(-r2*1.4)*190);Image.fromarray(rgba).save(ROOT/'roku/images/bioluminescence.png',optimize=True)
 print('Articulated clam',w,h,len(v),'vertices',len(pages),'atlas pages',flush=True)
if __name__=='__main__':build()
