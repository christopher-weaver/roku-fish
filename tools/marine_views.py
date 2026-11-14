"""Fish-style textured closed volumes: seven sharp marine views, no view blending."""
from pathlib import Path
import json,math
import imagequant
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,gaussian_filter
ROOT=Path(__file__).resolve().parents[1]
VERT='''#version 330
in vec3 position;in vec2 uv;uniform float yaw;out vec2 texuv;
void main(){float c=cos(yaw),s=sin(yaw);vec3 q=vec3(c*position.x-s*position.z,position.y,s*position.x+c*position.z);gl_Position=vec4(q.x,q.y,-q.z*.3,1);texuv=uv;}'''
FRAG='''#version 330
uniform sampler2D photo;in vec2 texuv;out vec4 color;
void main(){vec4 c=texture(photo,texuv);if(c.a<.02)discard;color=c;}'''

def build():
 import moderngl
 from connected_scene import source_reef,marine
 ctx=moderngl.create_standalone_context(backend='egl');program=ctx.program(vertex_shader=VERT,fragment_shader=FRAG)
 reef=source_reef().getchannel('A');result={};folder=ROOT/'assets/source/marine-renders'
 for name,x,y,width,height,thickness in [('sea-fan',80,430,600,565,.035),('sea-anemone',1330,815,285,215,.32)]:
  image=marine(name,width,height);pad=8;tile=Image.new('RGBA',(width+pad*2,height+pad*2));tile.alpha_composite(image,(pad,pad));fw,fh=tile.size;x-=pad;y-=pad
  w=224;h=round(w*fh/fw);small=tile.resize((w,h),Image.Resampling.LANCZOS);alpha=np.asarray(small.getchannel('A'))>25
  distance=gaussian_filter(distance_transform_edt(alpha),.6);depth=np.sqrt(distance/max(distance.max(),1))*thickness
  yy,xx=np.mgrid[:h,:w]
  bend=np.zeros_like(depth)
  if name=='sea-fan':bend=.065*np.sin((xx/(w-1)-.5)*math.pi*1.6)*np.sin(yy/(h-1)*math.pi)*alpha
  vertices=[];uv=[];indices={};faces=[]
  for side in [-1,1]:
   for row in range(h):
    for col in range(w):
     if alpha[row,col]:
      indices[side,row,col]=len(vertices)
      vertices.append((col/(w-1)*2-1,1-row/(h-1)*2,bend[row,col]+side*depth[row,col]));uv.append((col/(w-1),1-row/(h-1)))
  for side in [-1,1]:
   for row in range(h-1):
    for col in range(w-1):
     keys=[(side,row,col),(side,row+1,col),(side,row,col+1),(side,row+1,col+1)]
     if all(k in indices for k in keys):
      a,b,c,d=[indices[k]for k in keys];faces.extend([(a,b,c),(c,b,d)])
  # Stitch the contour, like the fish's silhouette-derived volume.
  for row in range(h-1):
   for col in range(w-1):
    for dr,dc in [(1,0),(0,1)]:
     if alpha[row,col] and alpha[row+dr,col+dc] and distance[row,col]<1.6:
      a=indices[1,row,col];b=indices[1,row+dr,col+dc];c=indices[-1,row,col];d=indices[-1,row+dr,col+dc];faces.extend([(a,b,c),(b,d,c)])
  positions=np.array(vertices,dtype='f4');uv=np.array(uv,dtype='f4');faces=np.array(faces,dtype='i4')
  np.savez_compressed(folder/(name+'-volume.npz'),vertices=positions,uv=uv,faces=faces)
  vb=ctx.buffer(np.hstack([positions,uv]).astype('f4').tobytes());ib=ctx.buffer(faces.tobytes());vao=ctx.vertex_array(program,[(vb,'3f 2f','position','uv')],ib)
  texture=ctx.texture(tile.size,4,tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());texture.filter=(moderngl.LINEAR,moderngl.LINEAR);texture.use()
  fbo=ctx.simple_framebuffer((fw*2,fh*2),components=4);fbo.use();ctx.enable(moderngl.DEPTH_TEST)
  views=[];union=np.zeros((fh,fw),dtype=np.uint8)
  cover=np.asarray(reef.crop((x,y,x+fw,y+fh)))>250
  for angle in np.linspace(-8,8,7):
   program['yaw'].value=math.radians(float(angle));fbo.clear(0,0,0,0,depth=1);vao.render()
   shot=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
   a=np.array(shot.getchannel('A'));a[a<6]=0
   if name=='sea-fan':a[cover]=0  # Hidden root pixels are occluded by fixed reef.
   shot.putalpha(Image.fromarray(a));union=np.maximum(union,a);views.append(shot)
  box=Image.fromarray(union).getbbox();bx,by,x1,y1=box;fw=x1-bx;fh=y1-by
  atlas=Image.new('RGBA',(fw*3,fh*3))
  for i,shot in enumerate(views):atlas.paste(shot.crop(box),((i%3)*fw,(i//3)*fh))
  rgba=np.array(atlas);rgba[:,:,:3][rgba[:,:,3]==0]=0
  runtime=ROOT/'roku/images'/('reef-'+name+'.webp')
  raw=ROOT/'work/marine-raw';raw.mkdir(parents=True,exist_ok=True);Image.fromarray(rgba).save(raw/(name+'.png'))
  compact=imagequant.quantize_pil_image(Image.fromarray(rgba),max_colors=128,dithering_level=0,max_quality=95)
  compact.convert('RGBA').save(runtime,lossless=True,method=6,exact=True)
  footprint=Image.fromarray(union).crop(box);footprint.save(folder/(name+'-views-footprint.png'))
  result[name]={'x':x+bx,'y':y+by,'width':fw,'height':fh,'frameWidth':fw,'frameHeight':fh,'frames':7,'columns':3,'angles':[round(float(v),4)for v in np.linspace(-8,8,7)],'meshVertices':len(vertices),'meshTriangles':len(faces),'rootY':y+pad+height,'image':'pkg:/images/'+runtime.name}
  for obj in [vao,vb,ib,texture,fbo]:obj.release()
  print(name,'closed textured volume,',len(vertices),'vertices, 7 views,',atlas.size,flush=True)
 (folder/'views.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':build()
