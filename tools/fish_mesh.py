"""Construct textured volume meshes from licensed alpha silhouettes; render real yaw / bend poses.
Mesh reconstruction is deliberately lightweight, not a substitute for a sculpted anatomical model.
The checked-in .npz files can also be imported into Blender with tools/blender_render.py.
"""
from pathlib import Path
import json, math, os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from scipy.ndimage import distance_transform_edt, gaussian_filter
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'assets/source';OUT=ROOT/'roku/images'
SPECIES=[
 ('ocellaris_clownfish','Ocellaris clownfish',120,36,2.8,False,.35),
 ('yellow_tang','Yellow tang',155,49,2.0,False,.25),
 ('royal_gramma','Royal gramma',110,33,2.6,False,.27),
 ('emperor_angelfish','Emperor angelfish',190,44,1.8,False,.27),
 ('moorish_idol','Moorish idol',172,43,2.0,False,.21),
 ('green_chromis','Blue-green chromis',90,53,3.2,True,.30)]
VS='''#version 330
in vec3 pos;in vec2 uv;uniform float yaw;uniform float bend;out vec2 texuv;out float shade;
void main(){vec3 p=pos;float rear=max(0.0,0.28-p.x);p.z+=bend*rear*rear;p.x+=bend*bend*rear*rear*rear*.85;float c=cos(yaw),s=sin(yaw);vec3 q=vec3(p.x*c-p.z*s,p.y,p.x*s+p.z*c);gl_Position=vec4(q.x*.9,q.y*.9,-q.z*.4,1);texuv=uv;shade=.86+.14*(p.y+1.0)/2.0;}
'''
FS='''#version 330
uniform sampler2D photo;in vec2 texuv;in float shade;out vec4 outcol;
void main(){vec4 c=texture(photo,texuv);if(c.a<.08)discard;outcol=vec4(c.rgb*shade,c.a);}
'''
def make_mesh(name,thick):
    im=Image.open(SRC/(name+'.png')).convert('RGBA');bb=im.getchannel('A').getbbox();im=im.crop(bb)
    im=ImageEnhance.Color(im).enhance(.84);im=ImageEnhance.Contrast(im).enhance(.94)
    w=200;h=max(40,round(w*im.height/im.width));small=im.resize((w,h),Image.Resampling.LANCZOS)
    a=np.asarray(small.getchannel('A'));mask=a>50;dist=distance_transform_edt(mask)
    # Smooth lens volume; fins remain thin. A thick peduncle and rounded snout survive turns.
    depth=gaussian_filter(dist,.65);depth=depth/max(depth.max(),1)*thick
    verts=[];uv=[];faces=[]
    ids={}
    for side in [-1,1]:
        for y in range(h):
            for x in range(w):
                if mask[y,x]:
                    ids[side,y,x]=len(verts)
                    verts.append([2*x/(w-1)-1, (1-2*y/(h-1))*h/w,side*depth[y,x]])
                    uv.append([x/(w-1),1-y/(h-1)])
    for side in [-1,1]:
        for y in range(h-1):
            for x in range(w-1):
                keys=[(side,y,x),(side,y,x+1),(side,y+1,x),(side,y+1,x+1)]
                if all(k in ids for k in keys):
                    i,j,k,l=[ids[q]for q in keys];faces.extend([[i,k,j],[j,k,l]] if side==1 else [[i,j,k],[j,l,k]])
    # Stitch the silhouette rim so front and back turns show volume instead of a flat card.
    for y in range(h-1):
        for x in range(w-1):
            for dy,dx in [(0,1),(1,0)]:
                a0=(1,y,x);b0=(1,y+dy,x+dx)
                if a0 not in ids or b0 not in ids:continue
                # All neighboring edges can be stitched; internal strips are hidden by depth test.
                if dist[y,x] > 1.5 and dist[y+dy,x+dx]>1.5:continue
                i=ids[a0];j=ids[b0];k=ids[-1,y,x];l=ids[-1,y+dy,x+dx];faces.extend([[i,j,k],[j,l,k]])
    verts=np.array(verts,np.float32);uv=np.array(uv,np.float32);faces=np.array(faces,np.int32)
    np.savez_compressed(SRC/(name+'.npz'),vertices=verts,uv=uv,faces=faces)
    im.save(SRC/(name+'-texture.png'))
    return verts,uv,faces,im

def build():
    import moderngl
    ctx=moderngl.create_standalone_context(backend='egl');p=ctx.program(vertex_shader=VS,fragment_shader=FS)
    fw,fh=192,168;fbo=ctx.simple_framebuffer((fw*2,fh*2),components=4);fbo.use();ctx.enable(moderngl.DEPTH_TEST)
    atlasdata={};contact=Image.new('RGB',(6*256,6*150),(27,45,58))
    for row,(name,label,size,speed,beat,school,thick) in enumerate(SPECIES):
        v,uv,faces,im=make_mesh(name,thick)
        vb=ctx.buffer(np.hstack((v,uv)).astype('f4').tobytes());ib=ctx.buffer(faces.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 2f','pos','uv')],ib)
        tex=ctx.texture(im.size,4,im.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);tex.use()
        # 16 full-circle views and three distinct volume-bent body/tail poses (no mirrored frames).
        aw,ah=fw*8,fh*6;atlas=Image.new('RGBA',(aw,ah));frames=[]
        for yaw in range(16):
            for phase,bend in enumerate([-.19,0,.19]):
                p['yaw'].value=yaw*2*math.pi/16;p['bend'].value=bend
                fbo.clear(0,0,0,0,depth=1);vao.render()
                shot=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
                index=yaw*3+phase;x=index%8*fw;y=index//8*fh
                atlas.paste(shot,(x,y));frames.append({'x':x,'y':y,'w':fw,'h':fh,'yaw':yaw*22.5,'pose':phase})
                if phase==1 and yaw in [0,2,4,6,8,12]:
                    col=[0,2,4,6,8,12].index(yaw);thumb=shot.copy();thumb.thumbnail((250,142));contact.paste(thumb,(col*256,row*150),thumb)
        atlas.save(OUT/(name+'-atlas.png'),optimize=True)
        atlasdata[name]={'label':label,'image':'pkg:/images/'+name+'-atlas.png','width':aw,'height':ah,'frameW':fw,'frameH':fh,'yawCount':16,'poseCount':3,'length':size,'renderLength':fw*.9,'speed':speed,'beat':beat,'school':school,'frames':frames}
        vao.release();vb.release();ib.release();tex.release();print(name,'48 mesh-rendered frames')
    (ROOT/'roku/scenes/species.json').write_text(json.dumps(atlasdata,indent=2))
    (ROOT/'docs/previews').mkdir(exist_ok=True,parents=True);contact.save(ROOT/'docs/previews/fish-orientations.jpg',quality=94)
if __name__=='__main__':build()
