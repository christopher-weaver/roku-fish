"""Closed, individually named phototextured reef volumes and a hollow tunnel."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,gaussian_filter
import moderngl
ROOT=Path(__file__).resolve().parents[1];W,H=2048,1152
FEATURES=[('green-cup',390,820,305,230),('white-branching-coral',770,440,325,300),('orange-antler-coral',1440,280,445,285),('pink-bubble-coral',1190,590,240,205),('brain-coral',1310,825,205,200),('central-clam',1080,960,200,140),('right-plating-coral',1830,600,285,310),('right-sponge-garden',1730,970,300,170),('left-plating-garden',125,780,245,240)]
VS='''#version 330
in vec3 position;in vec2 uv;in vec3 normal;uniform vec2 canvas;out vec2 texuv;out vec3 n;out vec3 world;
void main(){gl_Position=vec4(position.x/canvas.x*2-1,1-position.y/canvas.y*2,-position.z/500.0,1);texuv=uv;n=normal;world=position;}'''
FS='''#version 330
uniform sampler2D photo;uniform float wall;in vec2 texuv;in vec3 n;in vec3 world;out vec4 color;
void main(){vec4 c=texture(photo,texuv);if(wall<.5&&c.a<.025)discard;
float light=.82+.18*max(0.0,dot(normalize(n),normalize(vec3(-.35,-.65,1))));
if(wall>.5){float grain=sin(world.x*.23+sin(world.y*.31))*sin(world.y*.17);c=vec4(min(c.rgb*.65,vec3(.16,.13,.14)),1);light=(.42+.28*max(0.0,dot(normalize(n),normalize(vec3(-.35,-.65,1)))))*clamp((world.z+215.0)/305.0,.12,1.0);}
color=vec4(c.rgb*light,c.a);}'''

def volume(mask,depth):
 h,w=mask.shape;corners=np.zeros((h+1,w+1),dtype=bool)
 for dy,dx in [(0,0),(0,1),(1,0),(1,1)]:corners[dy:dy+h,dx:dx+w]|=mask
 ys,xs=np.nonzero(corners);xy=np.stack([xs*2,ys*2],axis=1).astype('f4')
 # Split opposite occupied quadrants at a checkerboard corner. Sharing their
 # vertical edge would produce a non-manifold four-face contact.
 pad=np.pad(mask,1)
 tl=pad[:h+1,:w+1];tr=pad[:h+1,1:w+2];bl=pad[1:h+2,:w+1];br=pad[1:h+2,1:w+2]
 ambiguous=(tl&br&~tr&~bl)|(tr&bl&~tl&~br)
 ay,ax=np.nonzero(ambiguous);base_count=len(xs)
 xy=np.vstack([xy,np.column_stack([ax*2,ay*2]).astype('f4')]);sample_y=np.concatenate([ys,ay]);sample_x=np.concatenate([xs,ax])
 sample=depth[np.clip(sample_y,0,h-1),np.clip(sample_x,0,w-1)]
 vertices=np.vstack([np.column_stack([xy,sample]),np.column_stack([xy,np.full(len(xy),-8)])]).astype('f4')
 ids=np.full(corners.shape,-1,dtype='i4');ids[ys,xs]=np.arange(base_count);lower_ids=ids.copy();lower_ids[ay,ax]=base_count+np.arange(len(ax));offset=len(xy);faces=[]
 yy,xx=np.nonzero(mask)
 for y,x in zip(yy.tolist(),xx.tolist()):
  a,b,c,d=lower_ids[y,x],lower_ids[y,x+1],ids[y+1,x+1],ids[y+1,x]
  faces.extend([(a,b,c),(a,c,d),(a+offset,c+offset,b+offset),(a+offset,d+offset,c+offset)])
  for ny,nx,i,j in [(y-1,x,a,b),(y,x+1,b,c),(y+1,x,c,d),(y,x-1,d,a)]:
   if ny<0 or nx<0 or ny>=h or nx>=w or not mask[ny,nx]:faces.extend([(j,i,i+offset),(j,i+offset,j+offset)])
 faces=np.array(faces,dtype='i4');gy,gx=np.gradient(depth,2,2);normals=np.zeros_like(vertices)
 normals[:offset]=np.column_stack([-gx[np.clip(sample_y,0,h-1),np.clip(sample_x,0,w-1)],-gy[np.clip(sample_y,0,h-1),np.clip(sample_x,0,w-1)],np.ones(offset)])
 normals[offset:,2]=-1;normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-6)
 uv=np.column_stack([vertices[:,0]/W,1-vertices[:,1]/H]).astype('f4')
 return vertices,uv,normals,faces

def tunnel():
 from connected_scene import source_reef
 alpha=np.asarray(source_reef().getchannel('A'));n=192;vertices=[];faces=[];sample_uv=[];radii=[];cx,cy=773.,857.5
 # Follow the actual irregular opening instead of placing a perfect ellipse
 # over the photographed rock. Sample stone beyond each rim for wall UVs.
 for i in range(n):
  angle=i*2*math.pi/n;dx,dy=math.cos(angle),math.sin(angle);radius=8.
  for r in np.arange(8.,90.,.5):
   x=int(round(cx+r*dx));y=int(round(cy+r*dy))
   if alpha[y,x]>80:radius=r;break
  radii.append(radius)
  sample=radius+5
  for r in np.arange(radius+3,radius+32,1):
   x=int(round(cx+r*dx));y=int(round(cy+r*dy))
   if alpha[y,x]>245:sample=r;break
  sample_uv.append(((cx+sample*dx)/W,1-(cy+sample*dy)/H))
 front=np.array([(cx+r*math.cos(i*2*math.pi/n),cy+r*math.sin(i*2*math.pi/n),90)for i,r in enumerate(radii)],dtype='f4')
 from cave_geometry import chamber
 return chamber(front,np.array(sample_uv,dtype='f4'))

def build():
 from connected_scene import source_reef,marine
 folder=ROOT/'assets/source/reef-model';folder.mkdir(parents=True,exist_ok=True)
 for name,width,height in [('sea-fan',600,565),('sea-anemone',285,215)]:
  image=marine(name,width,height);tile=Image.new('RGBA',(width+16,height+16));tile.alpha_composite(image,(8,8));tile.save(folder/(name+'-projection.png'))
 photo=source_reef()
 # Replace the former photographed clam with matching stone beneath the new
 # articulated animal. Keep the reef opaque so an open shell reveals rock.
 pixels=np.array(photo);yy0,xx0=np.mgrid[:H,:W];weight=np.clip((1-((xx0-1080)/185)**2-((yy0-944)/142)**2)*12,0,1)
 dy=np.abs((yy0%390)-195);dx=np.abs((xx0%220)-110);donor=pixels[610+dy,805+dx,:3];pixels[:,:,:3]=np.uint8(pixels[:,:,:3]*(1-weight[:,:,None])+donor*weight[:,:,None]);photo=Image.fromarray(pixels)
 photo.save(folder/'reef-projection.png');a=np.asarray(photo.getchannel('A'));mask=(a.reshape(H//2,2,W//2,2)>8).any(axis=(1,3))
 y,x=np.mgrid[:H//2,:W//2];xx=x*2;yy=y*2
 distance=distance_transform_edt(mask)*2;depth=18+np.minimum(distance*.55,44)
 scores=[]
 for name,cx,cy,rx,ry in FEATURES:scores.append(((xx-cx)/rx)**2+((yy-cy)/ry)**2)
 scores=np.stack(scores);labels=np.argmin(scores,axis=0)+1;labels[np.min(scores,axis=0)>1]=0
 # Shared analytic anatomy/depth field keeps touching volumes registered.
 for i,(name,cx,cy,rx,ry)in enumerate(FEATURES,1):
  r=np.sqrt(((xx-cx)/rx)**2+((yy-cy)/ry)**2);envelope=np.exp(-r*r*2)
  if name=='green-cup':shape=85*np.exp(-((r-.66)/.22)**2)+9*np.cos(np.arctan2(yy-cy,xx-cx)*16)*envelope
  elif name=='pink-bubble-coral':shape=65*envelope+13*np.sin(xx*.085)*np.cos(yy*.075)*envelope
  elif name=='brain-coral':shape=75*envelope+8*np.sin(xx*.17+4*np.sin(yy*.07))*envelope
  elif name=='central-clam':shape=58*envelope+12*np.cos(np.arctan2(yy-cy,xx-cx)*13)*envelope
  elif name=='right-plating-coral' or name=='left-plating-garden':shape=42*envelope+14*np.sin(yy*.055+np.sin(xx*.02))*envelope
  else:shape=65*envelope+8*np.sin(xx*.047)*np.cos(yy*.041)*envelope
  depth+=shape
 depth=gaussian_filter(depth,.7)
 front=(((xx-415)/270)**2+((yy-845)/230)**2<1)|(((xx-1290)/210)**2+((yy-820)/245)**2<1)|(((xx-1080)/190)**2+((yy-960)/150)**2<1)|(yy>960)|((xx>1450)&(yy>850))
 meshes=[];record={'method':'closed shared-surface phototextured volumes with anatomical curvature','objects':[]}
 for label,name in [(0,'live-rock-foundation')]+[(i+1,v[0])for i,v in enumerate(FEATURES)]:
  for layer,select in [('connected-reef',~front),('foreground-reef',front)]:
   occupied=mask&(labels==label)&select
   if not occupied.any():continue
   v,uv,n,f=volume(occupied,depth);key=name+'-'+layer;np.savez_compressed(folder/(key+'.npz'),vertices=v,uv=uv,normals=n,faces=f)
   meshes.append((key,layer,v,uv,n,f,False));record['objects'].append({'name':key,'group':name,'layer':layer,'vertices':len(v),'triangles':len(f),'file':key+'.npz','closed':True})
 v,uv,n,f=tunnel();np.savez_compressed(folder/'hollow-tunnel.npz',vertices=v,uv=uv,normals=n,faces=f);meshes.append(('hollow-tunnel','connected-reef',v,uv,n,f,True));record['objects'].append({'name':'hollow-tunnel','group':'hollow-tunnel','layer':'connected-reef','vertices':len(v),'triangles':len(f),'file':'hollow-tunnel.npz','closed':False,'type':'bending blind cave with five depth rings and rear wall'})
 from living_reef import corals,save,photo_material,VS as SCULPT_VS,FS as SCULPT_FS
 for name,(layer,model)in corals().items():
  v,n,f,rgb,flow=save(name,model,folder);photo_material(name,folder);uv=np.column_stack([v[:,0]/W,1-v[:,1]/H]).astype('f4')
  meshes.append((name,layer,v,uv,n,f,2));record['objects'].append({'name':name,'group':name,'layer':layer,'vertices':len(v),'triangles':len(f),'file':name+'.npz','closed':True,'sculpted':True})
 ctx=moderngl.create_standalone_context(backend='egl');p=ctx.program(vertex_shader=VS,fragment_shader=FS);p['canvas'].value=(W,H);ctx.enable(moderngl.DEPTH_TEST)
 sculpt=ctx.program(vertex_shader=SCULPT_VS,fragment_shader=SCULPT_FS);sculpt['stage'].value=(0,0,W,H);sculpt['strength'].value=0
 tex=ctx.texture(photo.size,4,photo.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);tex.use();fbo=ctx.simple_framebuffer((W,H),components=4);fbo.use()
 cfgpath=ROOT/'roku/scenes/tank.json';cfg=json.loads(cfgpath.read_text())
 for layer in ['connected-reef','foreground-reef']:
  fbo.clear(0,0,0,0,depth=1)
  members=[m for m in meshes if m[1]==layer]
  for key,_,v,uv,n,f,wall in members:
   ib=ctx.buffer(f.tobytes())
   if wall==2:
    image=Image.open(folder/(key+'-colour.png'));sculptTexture=ctx.texture(image.size,3,image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());sculptTexture.filter=(moderngl.LINEAR,moderngl.LINEAR);sculptTexture.use();sculpt['usePhoto'].value=1
    data=np.load(folder/(key+'.npz'));vb=ctx.buffer(np.column_stack([v,n,data['rgb'],data['flow']]).astype('f4').tobytes());vao=ctx.vertex_array(sculpt,[(vb,'3f 3f 3f 3f','position','normal','rgb','flow')],ib)
   else:
    tex.use();vb=ctx.buffer(np.hstack([v,uv,n]).astype('f4').tobytes());vao=ctx.vertex_array(p,[(vb,'3f 2f 3f','position','uv','normal')],ib);p['wall'].value=float(wall)
   vao.render();vao.release();vb.release();ib.release()
   if wall==2:sculptTexture.release()
  shot=Image.frombytes('RGBA',(W,H),fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);alpha=shot.getchannel('A');box=alpha.getbbox();part=shot.crop(box);filename='reef-'+layer+'.webp';part.save(ROOT/'roku/images'/filename,quality=87,method=6,exact=True)
  for formation in cfg['formations']:
   if formation['id']==layer:
    formation.update(x=box[0],y=box[1],width=part.width,height=part.height,frameWidth=part.width,frameHeight=part.height,renderedMesh=True,meshVertices=sum(len(m[2])for m in members),meshTriangles=sum(len(m[5])for m in members),meshObjects=[m[0]for m in members]);formation.pop('images',None)
  print(layer,len(members),'closed/structural 3D objects',part.size,flush=True)
 cfg['notes']='All coral/live-rock groups have actual closed UV-textured meshes; bending blind cave, closed rear wall and pinned articulated moray. Offline rendering preserves native Roku draw performance.'
 cfgpath.write_text(json.dumps(cfg,indent=2)+'\n');(folder/'model.json').write_text(json.dumps(record,indent=2)+'\n')
if __name__=='__main__':build()
