"""Render three real relief-mesh views per isolated coral; no runtime mesh/shader."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,gaussian_filter
ROOT=Path(__file__).resolve().parents[1]
VERT='''#version 330
in vec3 position;in vec2 uv;in vec3 normal;uniform float yaw;
out vec2 texuv;out float light;
void main(){float c=cos(yaw),s=sin(yaw);vec3 p=position;
vec3 q=vec3(c*p.x-s*p.z,p.y,s*p.x+c*p.z);
vec3 n=vec3(c*normal.x-s*normal.z,normal.y,s*normal.x+c*normal.z);
gl_Position=vec4(q.x*.94,q.y*.94,-q.z*.25,1);
texuv=uv;light=.86+.14*max(0.0,dot(normalize(n),normalize(vec3(-.4,.65,1.0))));}'''
FRAG='''#version 330
uniform sampler2D photo;in vec2 texuv;in float light;out vec4 color;
void main(){vec4 c=texture(photo,texuv);if(c.a<.02)discard;color=vec4(c.rgb*light,c.a);}'''
NAMES=['white-crown','branching-coral','green-cup','brain-coral','central-clam','right-garden']
def build():
 import moderngl
 ctx=moderngl.create_standalone_context(backend='egl');program=ctx.program(vertex_shader=VERT,fragment_shader=FRAG)
 source=Image.open(ROOT/'assets/source/coral-islands-sheet.png').convert('RGBA');cw,ch=source.width//3,source.height//2
 folder=ROOT/'assets/source/coral-islands';folder.mkdir(exist_ok=True);result={}
 for i,name in enumerate(NAMES):
  im=source.crop(((i%3)*cw,(i//3)*ch,(i%3+1)*cw,(i//3+1)*ch))
  alpha=np.array(im.getchannel('A'));alpha[alpha>245]=255;alpha[alpha<8]=0;im.putalpha(Image.fromarray(alpha))
  box=im.getchannel('A').getbbox();im=im.crop(box);im.thumbnail((480,480),Image.Resampling.LANCZOS)
  tile=Image.new('RGBA',(512,512));tile.alpha_composite(im,((512-im.width)//2,(512-im.height)//2));tile.save(folder/(name+'.png'))
  # A curved depth field supplies real perspective changes and surface normals.
  sample=np.asarray(tile.resize((129,129),Image.Resampling.LANCZOS),dtype=float)/255
  a=sample[:,:,3];distance=distance_transform_edt(a>.25);distance=gaussian_filter(distance,1)
  depth=np.sqrt(distance/max(distance.max(),1))*.32
  lum=sample[:,:,:3]@np.array([.2126,.7152,.0722]);depth+=(lum-gaussian_filter(lum,2))*.025*(a>.4)
  dy,dx=np.gradient(depth,2/128,2/128);normal=np.stack([-dx,dy,np.ones_like(dx)],-1);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
  yy,xx=np.mgrid[:129,:129];vertices=np.concatenate([np.stack([xx/64-1,1-yy/64,depth],-1),np.stack([xx/128,1-yy/128],-1),normal],-1).astype('f4')
  faces=[]
  for y in range(128):
   for x in range(128):
    j=y*129+x;faces.extend([j,j+129,j+1,j+1,j+129,j+130])
  vb=ctx.buffer(vertices.tobytes());ib=ctx.buffer(np.array(faces,dtype='i4').tobytes());vao=ctx.vertex_array(program,[(vb,'3f 2f 3f','position','uv','normal')],ib)
  texture=ctx.texture(tile.size,4,tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());texture.filter=(moderngl.LINEAR,moderngl.LINEAR);texture.use()
  fbo=ctx.simple_framebuffer((1024,1024),components=4);fbo.use();ctx.enable(moderngl.DEPTH_TEST)
  atlas=Image.new('RGBA',(1536,512));silhouette=Image.new('L',(512,512))
  for view,angle in enumerate([-5,0,5]):
   program['yaw'].value=math.radians(angle);fbo.clear(0,0,0,0,depth=1);vao.render()
   shot=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((512,512),Image.Resampling.LANCZOS)
   a=np.asarray(shot.getchannel('A'));a=np.round(a/255*31)*255/31;shot.putalpha(Image.fromarray(a.astype('uint8')))
   atlas.paste(shot,(view*512,0));silhouette=Image.fromarray(np.maximum(np.asarray(silhouette),np.asarray(shot.getchannel('A'))))
  atlas=atlas.resize((1344,448),Image.Resampling.LANCZOS)
  atlas.save(ROOT/'roku/images'/('reef-'+name+'.webp'),quality=69,method=6,exact=True)
  silhouette.save(folder/(name+'-footprint.png'));result[name]={'frames':3,'frameWidth':512,'frameHeight':512,'angles':[-5,0,5],'meshVertices':129*129,'meshTriangles':128*128*2}
  for obj in [vao,vb,ib,texture,fbo]:obj.release()
  print('Rendered',name,'3 relief-mesh views',flush=True)
 (folder/'renders.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':build()
