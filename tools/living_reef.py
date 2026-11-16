"""Sculpted marine life: closed tubes, spheres, cups and ridged coral anatomy.

Materials are shaded on actual rounded geometry. No photographs or ripple
warps supply the shape or colour of these animals and coral sculptures.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
import moderngl,imagequant
ROOT=Path(__file__).resolve().parents[1]
VS='''#version 330
in vec3 position;in vec3 normal;in vec3 rgb;in vec3 flow;uniform vec4 stage;uniform float strength;
out vec3 n;out vec3 color;out vec3 world;out vec2 texuv;
void main(){vec3 p=position+flow*strength;gl_Position=vec4((p.x-stage.x)/stage.z*2-1,1-(p.y-stage.y)/stage.w*2,-p.z/500.0,1);n=normal;color=rgb;world=p;texuv=vec2(position.x/2048.0,1.0-position.y/1152.0);}'''
FS='''#version 330
uniform sampler2D photo;uniform float usePhoto;in vec3 n;in vec3 color;in vec3 world;in vec2 texuv;out vec4 outcol;
void main(){vec3 normal=normalize(n);vec3 light=normalize(vec3(-.35,-.7,1));float lambert=max(0.0,dot(normal,light));float shine=pow(max(0.0,dot(normal,normalize(light+vec3(0,0,1)))),30.0)*.07;
float grain=sin(world.x*2.7+sin(world.y*3.1))*sin(world.z*2.3)*.018;
vec3 base=usePhoto>.5?texture(photo,texuv).rgb:color;outcol=vec4(base*(.65+.35*lambert+grain)+shine*.3,1);}'''
class Model:
 def __init__(self):self.v=[];self.f=[];self.rgb=[];self.flow=[]
 def add(self,v,f,color,flow=None):
  v=np.asarray(v,dtype='f4');offset=len(self.v);self.v.extend(v);self.f.extend(np.asarray(f,dtype='i4')+offset)
  self.rgb.extend(np.broadcast_to(color,(len(v),3)));self.flow.extend(np.zeros_like(v)if flow is None else flow)
 def arrays(self):
  from cave_geometry import normals
  v=np.array(self.v,dtype='f4');f=np.array(self.f,dtype='i4');return v,normals(v,f),f,np.array(self.rgb,dtype='f4'),np.array(self.flow,dtype='f4')
 def sphere(self,center,radius,color,ridges=0):
  rows,sides=20,32;v=[np.array(center)+[0,-radius[1],0]]
  for row in range(1,rows):
   a=np.pi*row/rows
   for col in range(sides):
    b=2*np.pi*col/sides;wave=1+ridges*np.sin(23*b+4*np.sin(a*8))*np.sin(a)**2
    v.append(np.array(center)+np.array([np.sin(a)*np.cos(b),-np.cos(a),np.sin(a)*np.sin(b)])*radius*wave)
  v.append(np.array(center)+[0,radius[1],0]);f=[]
  for i in range(sides):f.append((0,1+(i+1)%sides,1+i))
  for row in range(rows-2):
   for i in range(sides):
    a=1+row*sides+i;b=1+row*sides+(i+1)%sides;c=a+sides;d=b+sides;f.extend([(a,b,c),(b,d,c)])
  end=len(v)-1
  for i in range(sides):f.append((end,1+(rows-2)*sides+i,1+(rows-2)*sides+(i+1)%sides))
  self.add(v,np.asarray(f)[:,::-1],color)
 def tube(self,path,radii,color,tip_color=None,flow=None,sides=12):
  path=np.asarray(path);tangent=np.gradient(path,axis=0);tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-6)
  reference=np.tile([0,0,1.],(len(path),1));reference[np.abs(tangent[:,2])>.9]=[0,1,0]
  right=np.cross(tangent,reference);right/=np.maximum(np.linalg.norm(right,axis=1)[:,None],1e-6);up=np.cross(right,tangent)
  v=[];colors=[];moves=[]
  for row,(center,radius)in enumerate(zip(path,radii)):
   t=row/(len(path)-1)
   for col in range(sides):
    a=2*np.pi*col/sides;v.append(center+radius*(np.cos(a)*right[row]+np.sin(a)*up[row]));colors.append(np.array(color)*(1-t)+np.array(tip_color or color)*t);moves.append(np.zeros(3)if flow is None else flow[row])
  f=[]
  for row in range(len(path)-1):
   for i in range(sides):
    a=row*sides+i;b=row*sides+(i+1)%sides;c=a+sides;d=b+sides;f.extend([(a,c,b),(b,c,d)])
  v.extend([path[0],path[-1]]);colors.extend([color,tip_color or color]);moves.extend([moves[0],moves[-1]])
  for i in range(sides):f.extend([(len(v)-2,i,(i+1)%sides),(len(v)-1,(len(path)-1)*sides+(i+1)%sides,(len(path)-1)*sides+i)])
  self.add(v,f,np.array(colors),np.array(moves))
 def cup(self,cx,cy,rx,ry,depth,color):
  sides=128;v=[];f=[];colors=[]
  # A continuous inner bowl, rolled rim, outer wall and closed underside.
  for radius,z in [(0.01,0),(.16,2),(.35,depth*.13),(.58,depth*.38),(.78,depth*.69),(.94,depth*.95),(1,depth),(.98,depth-9),(.78,depth*.55),(.5,-10),(.01,-20)]:
   for i in range(sides):
    a=i*2*np.pi/sides;flute=1+.022*np.cos(a*23);v.append((cx+rx*radius*np.cos(a)*flute,cy+ry*radius*np.sin(a)*flute,z+175));colors.append(np.array(color)*(.85+.15*radius))
  for row in range(10):
   for i in range(sides):
    a=row*sides+i;b=row*sides+(i+1)%sides;c=a+sides;d=b+sides;f.extend([(a,b,c),(b,d,c)])
  # The small central rings are capped, so there is no open seam.
  for i in range(1,sides-1):f.extend([(0,i+1,i),(10*sides,10*sides+i,10*sides+i+1)])
  self.add(v,np.asarray(f)[:,::-1],np.array(colors))

def anemone():
 m=Model();rng=np.random.default_rng(482);m.sphere((1474,1005,125),(104,25,55),(.25,.35,.27));m.sphere((1475,990,145),(66,15,35),(.43,.40,.33))
 for i in range(84):
  a=i*2.399963;r=82*np.sqrt((i+.5)/84);root=np.array([1475+r*np.cos(a),998+9*np.sin(a),145+r*.50*np.sin(a)])
  length=rng.uniform(84,155)*(1-.17*r/82);t=np.linspace(0,1,26)
  path=root+np.column_stack([np.cos(a)*(r*.18*t+24*np.sin(t*np.pi)), -length*np.sin(t*np.pi/2)+15*t**4, np.sin(a)*28*t+14*np.sin(t*3)])
  radius=(5.5+1.7*np.sin(i*2.3))*(1-.42*t);radius[-5:]*=[1.08,1.18,1.10,.83,.32]
  color=(.37+.07*np.sin(i),.44+.04*np.cos(i),.42+.08*np.sin(i*.3));tip=(.78,.67+.08*np.sin(i),.63+.08*np.cos(i))
  flow=np.column_stack([(5+3*np.sin(i*.7))*t*t,1.8*np.sin(i)*t*t,(3+3*np.cos(i))*t*t])
  m.tube(path,radius,color,tip,flow)
 return m

def fan():
 m=Model();t=np.linspace(0,1,28);root=np.array([345,1002,-45]);path=root+np.column_stack([8*np.sin(t*3),-435*t,8*np.sin(t*2)]);m.tube(path,6*(1-.8*t),(.40,.22,.17),(.69,.39,.28),np.column_stack([10*t*t,np.zeros(len(t)),4*t*t]))
 rng=np.random.default_rng(236)
 for level in range(9):
  start=root+np.array([6*np.sin(level*.3),-90-level*35,3]);spread=90+145*np.sin((level+2)/12*np.pi)
  for side in [-1,1]:
   q=np.linspace(0,1,23);branch=start+np.column_stack([side*spread*q,-(75+30*level/12)*q-18*np.sin(q*np.pi),18*np.sin(q*3+level)])
   motion=np.column_stack([((1002-branch[:,1])/435)**2*9,np.zeros(len(q)),q*q*5]);m.tube(branch,3.4*(1-.8*q),(.48,.25,.20),(.70,.42,.32),motion,sides=10)
   for j in range(3,21,3):
    base=branch[j];u=np.linspace(0,1,13);length=rng.uniform(28,61);twig=base+np.column_stack([side*length*.32*u,-length*u,5*np.sin(u*2+level)])
    w=((1002-twig[:,1])/435)**2;m.tube(twig,1.9*(1-.82*u),(.56,.29,.23),(.77,.51,.39),np.column_stack([8*w,np.sin(level)*w,4*w]),sides=8)
 return m

def corals():
 result={};m=Model();rng=np.random.default_rng(37)
 for i in range(95):
  a=i*2.399963;r=np.sqrt((i+.5)/95);x=1187+157*r*np.cos(a);y=592+106*r*np.sin(a);z=150+85*np.sqrt(1-r*r);radius=rng.uniform(16,28);m.sphere((x,y,z),(radius,radius*.88,radius),(.60+.08*r,.45+.09*r,.57+.09*r))
 result['sculpted-bubble-coral']=('connected-reef',m)
 m=Model();m.sphere((1302,831,240),(145,133,100),(.57,.38,.38),ridges=.046);result['sculpted-brain-coral']=('foreground-reef',m)
 return result

def photo_material(name,folder):
 from scipy.ndimage import distance_transform_edt,gaussian_filter
 from connected_scene import source_reef
 photo=np.array(source_reef());y,x=np.mgrid[:1152,:2048]
 cx,cy,rx,ry={'sculpted-green-cup':(390,820,250,205),'sculpted-bubble-coral':(1190,590,200,165),'sculpted-brain-coral':(1310,825,160,155)}[name]
 safe=((x-cx)/rx)**2+((y-cy)/ry)**2<1
 safe&=photo[:,:,3]>250
 if name=='sculpted-green-cup':safe&=photo[:,:,1]>photo[:,:,0]*1.02
 distance,indices=distance_transform_edt(~safe,return_indices=True)
 rgb=photo[indices[0],indices[1],:3].astype(float);soft=gaussian_filter(rgb,(10,10,0));blend=np.clip(distance/24,0,1)[:,:,None];rgb=rgb*(1-blend)+soft*blend
 far=np.clip((distance-24)/40,0,1)[:,:,None];rgb=rgb*(1-far)+np.median(photo[safe,:3],axis=0)*far
 image=Image.fromarray(np.uint8(rgb));image.save(folder/(name+'-colour.png'));return image

def save(name,model,folder):
 v,n,f,rgb,flow=model.arrays();uv=np.column_stack([v[:,0]/2048,1-v[:,1]/1152]).astype('f4');np.savez_compressed(folder/(name+'.npz'),vertices=v,normals=n,faces=f,rgb=rgb,flow=flow,uv=uv);return v,n,f,rgb,flow

def build_marine():
 folder=ROOT/'assets/source/marine-renders';cfgpath=ROOT/'roku/scenes/tank.json';cfg=json.loads(cfgpath.read_text());ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST);p=ctx.program(vertex_shader=VS,fragment_shader=FS)
 for name,model,period,scale in [('sea-anemone',anemone(),7.5,.72),('sea-fan',fan(),9.,.48)]:
  v,n,f,rgb,flow=save(name+'-sculpted',model,folder)
  # Compatibility geometry export uses normalized coordinates but retains real tubes.
  x0,y0=np.floor(np.min(v[:,:2]-np.abs(flow[:,:2]),axis=0)-8).astype(int);x1,y1=np.ceil(np.max(v[:,:2]+np.abs(flow[:,:2]),axis=0)+8).astype(int);w,h=x1-x0,y1-y0
  normalized=v.copy();normalized[:,0]=(v[:,0]-x0)/w*2-1;normalized[:,1]=1-(v[:,1]-y0)/h*2;normalized[:,2]=v[:,2]/100
  np.savez_compressed(folder/(name+'-volume.npz'),vertices=normalized,uv=np.column_stack([(v[:,0]-x0)/w,1-(v[:,1]-y0)/h]),faces=f)
  tw,th=round(w*scale),round(h*scale);cols=2044//(tw+4);capacity=cols*(2044//(th+4));p['stage'].value=(x0,y0,w,h)
  vb=ctx.buffer(np.column_stack([v,n,rgb,flow]).astype('f4').tobytes());ib=ctx.buffer(f.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f','position','normal','rgb','flow')],ib);fb=ctx.simple_framebuffer((w*2,h*2),components=4);fb.use();shots=[];union=np.zeros((h,w),dtype='uint8')
  for index in range(65):
   p['strength'].value=-1+index/32;fb.clear(0,0,0,0,depth=1);vao.render();im=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((w,h),Image.Resampling.LANCZOS);a=np.array(im.getchannel('A'));a[a<6]=0;im.putalpha(Image.fromarray(a));union=np.maximum(union,a);shots.append(im.resize((tw,th),Image.Resampling.LANCZOS))
  pages=[]
  for first in range(0,65,capacity):
   batch=shots[first:first+capacity];atlas=Image.new('RGBA',(cols*(tw+4)+4,math.ceil(len(batch)/cols)*(th+4)+4))
   for i,im in enumerate(batch):atlas.paste(im,(2+i%cols*(tw+4),2+i//cols*(th+4)))
   compact=imagequant.quantize_pil_image(atlas,max_colors=16 if name=='sea-fan'else 48,dithering_level=0,max_quality=95).convert('RGBA');filename=f'reef-{name}-motion-{len(pages)}.webp';normalized=np.array(compact);normalized[:,:,3][normalized[:,:,3]>245]=255;normalized[:,:,3][normalized[:,:,3]<6]=0;normalized[normalized[:,:,3]==0,:3]=0;Image.fromarray(normalized).save(ROOT/'roku/images'/filename,lossless=True,method=6,exact=True);pages.append('pkg:/images/'+filename)
  Image.fromarray(union).save(folder/(name+'-motion-footprint.png'))
  for formation in cfg['formations']:
   if formation['id']==name:formation.update(x=int(x0),y=int(y0),width=int(w),height=int(h),frameWidth=tw,frameHeight=th,columns=cols,frames=65,image=pages[0],images=pages,meshVertices=len(v),meshTriangles=len(f),geometryType='closed sculpted tubes and solid anatomy',animation=dict(period=period,count=65,framesPerPage=capacity,strideX=tw+4,strideY=th+4,gutter=2))
  for item in [vao,vb,ib,fb]:item.release()
  print('Sculpted',name,len(v),'vertices,',len(f),'triangles,',len(pages),'atlas pages',flush=True)
 cfgpath.write_text(json.dumps(cfg,indent=2)+'\n')
 used={path.split('/')[-1]for formation in cfg['formations']for path in formation.get('images',[formation['image']])}
 for path in (ROOT/'roku/images').glob('reef-*-motion-*.webp'):
  if path.name not in used:path.unlink()
if __name__=='__main__':build_marine()
