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
 m=Model();sides=192;rows=36;v=[];colors=[];faces=[];uv=[]
 # Outer and inner surfaces meet in a continuous rolled/scalloped rim.
 profile=[(r,False)for r in np.linspace(.008,1,rows)]+[(r,True)for r in np.linspace(1,.008,rows)]
 for r,inside in profile:
  for col in range(sides):
   a=col*2*np.pi/sides;flute=np.sin(9*a+.3)
   radius=r*(1+.038*flute*r*r);dome=(1-r*r)**.65
   height=(35*dome+12 if upper else -27*dome)+10*flute*r**3
   height+=(-4 if upper else 4)if inside else 0
   point=CENTER+np.array([152*radius*np.cos(a),0,0])+V*(73*radius*np.sin(a))+UP*height
   uv.append(((.5 if inside else 0)+.499*np.clip((point[0]-CENTER[0])/320+.5,0,1),np.clip((point[1]-CENTER[1])/170+.5,0,1)))
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
 m.add(v,np.array(faces)if upper else np.array(faces)[:,::-1],np.ones((len(v),3)),uv=uv)
 # Thick soft mantle follows the irregular shell lip, with living colour.
 a=np.linspace(0,2*np.pi,385);path=[];palette=[]
 for angle in a:
  flute=np.sin(9*angle+.3);point=CENTER+np.array([152*1.038*np.cos(angle),0,0])+V*(73*1.038*np.sin(angle))+UP*((12 if upper else 0)+10*flute)
  if upper:
   pp=point-HINGE;co=np.cos(opening*.86);sn=np.sin(opening*.86);point=HINGE+[pp[0],pp[1]*co-pp[2]*sn,pp[1]*sn+pp[2]*co]
  path.append(point);palette.append(np.array([.35,.49,.48])*(.8+.17*np.sin(angle*31+.6*np.cos(angle*17))))
 start=len(m.v)
 m.tube(path,np.full(len(a),5.3),(.35,.49,.48),sides=12,row_colors=np.array(palette))
 for i in range(start,len(m.v)):
  point=np.array(m.v[i]);m.uv[i]=[.5+.499*np.clip((point[0]-CENTER[0])/320+.5,0,1),np.clip((point[1]-CENTER[1])/170+.5,0,1)];m.rgb[i]=np.ones(3)
 return m

def model(opening):
 m=Model();m.sphere(CENTER-UP*12,(124,9,50),(.78,.68,.64),ridges=.025)
 for i,point in enumerate(m.v):m.uv[i]=[.5+.499*np.clip((point[0]-CENTER[0])/260+.5,0,1),np.clip((point[1]-CENTER[1])/140+.5,0,1)]
 m.frontStart=len(m.f)
 for upper in [False,True]:
  part=valve(upper,opening);m.add(part.v,part.f,np.array(part.rgb),uv=part.uv)
 # Turn toward the right side and reduce every dimension by 30 percent.
 v=np.array(m.v)-CENTER;axis=UP/np.linalg.norm(UP);angle=np.radians(-55);v=v*np.cos(angle)+np.cross(axis,v)*np.sin(angle)+np.outer(v@axis,axis)*(1-np.cos(angle));m.v=list(v*.70+np.array([1080.,1001.,240.]))
 return m

def build():
 folder=ROOT/'assets/source/marine-renders';cfgpath=ROOT/'roku/scenes/tank.json';cfg=json.loads(cfgpath.read_text())
 from marine_materials import build as build_materials,VS as MATERIAL_VS,FS as MATERIAL_FS
 build_materials();ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST);p=ctx.program(vertex_shader=MATERIAL_VS,fragment_shader=MATERIAL_FS.replace('base=mix(base,color,.13);','base*=color;'));p['strength'].value=0;p['clipDepth'].value=-500
 bounds=np.concatenate([model(i).arrays()[0]for i in [0,1]]);x0,y0=np.floor(bounds[:,:2].min(axis=0)-5).astype(int);x1,y1=np.ceil(bounds[:,:2].max(axis=0)+5).astype(int);w,h=int(x1-x0),int(y1-y0);scale=1.0;tw,th=round(w*scale),round(h*scale);cols=2044//(tw+4);capacity=cols*(2044//(th+4));p['stage'].value=(int(x0),int(y0),w,h)
 photo=Image.open(folder/'clam-material.png');texture=ctx.texture(photo.size,3,photo.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());texture.build_mipmaps();texture.filter=(moderngl.LINEAR_MIPMAP_LINEAR,moderngl.LINEAR);texture.anisotropy=8;texture.use();fb=ctx.simple_framebuffer((w*2,h*2),components=4);fb.use();shots=[];frontShots=[];union=np.zeros((h,w),dtype='uint8')
 for i in range(65):
  m=model(i/64);v,n,f,rgb,flow=m.arrays()
  if i==0:
   save('clam-sculpted',m,folder);nv=v.copy();nv[:,0]=(v[:,0]-x0)/w*2-1;nv[:,1]=1-(v[:,1]-y0)/h*2;nv[:,2]/=100;np.savez_compressed(folder/'clam-volume.npz',vertices=nv,uv=np.column_stack([(v[:,0]-x0)/w,1-(v[:,1]-y0)/h]),faces=f)
   # Editable scene has the actual shell hinge as a shape key.
   dest=ROOT/'assets/source/reef-model';save('articulated-clam',m,dest);opened=model(1).arrays()[0];np.savez_compressed(dest/'clam-open.npz',vertices=opened);record=json.loads((dest/'model.json').read_text());record['objects']=[o for o in record['objects']if o['name']!='articulated-clam'];
   for o in record['objects']:
    if o['group']=='central-clam':o['group']='clam-rock-bed'
   record['objects'].append(dict(name='articulated-clam',group='central-clam',layer='clam',vertices=len(v),triangles=len(f),file='articulated-clam.npz',closed=True,sculpted=True));(dest/'model.json').write_text(json.dumps(record,indent=2)+'\n')
  vb=ctx.buffer(np.column_stack([v,n,rgb,flow,m.uv,m.opacity]).astype('f4').tobytes());ib=ctx.buffer(f.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f 2f 1f','position','normal','rgb','flow','surfaceUV','opacity')],ib);p['clipDepth'].value=-500;fb.clear(0,0,0,0,depth=1);vao.render();im=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((w,h),Image.Resampling.LANCZOS);a=np.array(im.getchannel('A'));a[a<6]=0;im.putalpha(Image.fromarray(a));union=np.maximum(union,a);shots.append(im.resize((tw,th),Image.Resampling.LANCZOS));frontIb=ctx.buffer(f[m.frontStart:].tobytes());frontVao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f 2f 1f','position','normal','rgb','flow','surfaceUV','opacity')],frontIb);p['clipDepth'].value=275;fb.clear(0,0,0,0,depth=1);frontVao.render();front=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((tw,th),Image.Resampling.LANCZOS);frontShots.append(front);frontVao.release();frontIb.release();vao.release();vb.release();ib.release()
 pages=[];frontPages=[]
 for collection,target,prefix in [(shots,pages,'reef-clam-motion')]:
  for first in range(0,65,capacity):
   batch=collection[first:first+capacity];atlas=Image.new('RGBA',(cols*(tw+4)+4,math.ceil(len(batch)/cols)*(th+4)+4))
   for i,im in enumerate(batch):atlas.paste(im,(2+i%cols*(tw+4),2+i//cols*(th+4)))
   name=f'{prefix}-{len(target)}.webp';a=np.array(atlas);a[:,:,3]=np.uint8(np.round(a[:,:,3]/17)*17);Image.fromarray(a).save(ROOT/'roku/images'/name,quality=75,method=6,exact=False);target.append('pkg:/images/'+name)
 Image.fromarray(union).save(folder/'clam-motion-footprint.png')
 from clam_occlusion import rectangles
 frontRects=[rectangles(np.asarray(im)[:,:,3])for im in frontShots]
 formation=dict(id='clam',x=int(x0),y=int(y0),width=w,height=h,frameWidth=tw,frameHeight=th,columns=cols,frames=65,image=pages[0],images=pages,frontRects=frontRects,yawDegrees=-55,modelScale=.7,mouth={'x':1085,'y':970,'z':.97,'exitX':1220,'exitY':875},z=.83,halfDepth=.025,parallax=1,rootY=1030,renderedMesh=True,meshVertices=len(v),meshTriangles=len(f),geometryType='closed articulated ridged bivalve shell',animation=dict(period=47,count=65,framesPerPage=capacity,strideX=tw+4,strideY=th+4,gutter=2))
 cfg['formations']=[f for f in cfg['formations']if f['id']!='clam']+[formation];cfg['formations'].sort(key=lambda f:f['z']);cfg['occlusionDepths']=[f['z']for f in cfg['formations']];cfgpath.write_text(json.dumps(cfg,indent=2)+'\n')
 # Small luminous sprites are loaded once; pearl has modeled spherical shading.
 y,x=np.mgrid[:40,:40];nx=(x-19.5)/17;ny=(y-19.5)/17;r2=nx*nx+ny*ny;nz=np.sqrt(np.clip(1-r2,0,1));light=np.clip(-nx*.35-ny*.5+nz*.8,0,1);spec=np.exp(-((nx+.30)**2+(ny+.40)**2)/.025);rgba=np.zeros((40,40,4),dtype='uint8');rgba[:,:,:3]=np.uint8(np.clip(np.array([180,196,196])[None,None,:]*(.58+.42*light[:,:,None])+spec[:,:,None]*60,0,255));rgba[:,:,3]=np.uint8(np.clip((1-r2)*15,0,1)*255);Image.fromarray(rgba).save(ROOT/'roku/images/clam-pearl.png',optimize=True)
 y,x=np.mgrid[:32,:32];r2=((x-15.5)/9)**2+((y-15.5)/9)**2;rgba=np.full((32,32,4),255,dtype='uint8');rgba[:,:,3]=np.uint8(np.exp(-r2*1.4)*190);Image.fromarray(rgba).save(ROOT/'roku/images/bioluminescence.png',optimize=True)
 print('Articulated clam',w,h,len(v),'vertices',len(pages),'atlas pages',flush=True)
if __name__=='__main__':build()
