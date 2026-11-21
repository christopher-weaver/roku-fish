"""Depth-render the moray INSIDE its curved rock cave in one shared scene.

The coral is a depth holdout: the lip hides the animal while it is recessed,
and the animal can cross in front of that lip when it actually emerges.
No screen-space sliding, repair patches, or alpha crossfades are involved.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import moderngl,imagequant
from cave_geometry import STAGE,COUNT,FRAME_COUNT,animal
from reef_geometry import FS
ROOT=Path(__file__).resolve().parents[1]
VS='''#version 330
in vec3 position;in vec2 uv;in vec3 normal;in float kind;in vec3 skin;uniform vec4 stage;
out vec2 texuv;out vec3 n;out vec3 world;out float material;out vec3 skinPoint;
void main(){gl_Position=vec4((position.x-stage.x)/stage.z*2-1,1-(position.y-stage.y)/stage.w*2,-position.z/500.0,1);texuv=uv;n=normal;world=position;material=kind;skinPoint=skin;}'''
EEL_FS='''#version 330
in vec3 n;in vec3 world;in float material;in vec3 skinPoint;out vec4 color;
float hash3(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453123);}
float noise3(vec3 p){vec3 cell=floor(p),q=fract(p);q=q*q*(3.0-2.0*q);return mix(mix(mix(hash3(cell),hash3(cell+vec3(1,0,0)),q.x),mix(hash3(cell+vec3(0,1,0)),hash3(cell+vec3(1,1,0)),q.x),q.y),mix(mix(hash3(cell+vec3(0,0,1)),hash3(cell+vec3(1,0,1)),q.x),mix(hash3(cell+vec3(0,1,1)),hash3(cell+vec3(1,1,1)),q.x),q.y),q.z);}
float organic(vec3 p){return .58*noise3(p)+.28*noise3(p*1.93+vec3(8.3,2.8,13.4))+.14*noise3(p*4.17+vec3(17.1,11.8,3.9));}
void main(){
vec3 base=vec3(.39,.30,.10);
if(material<.5){vec3 p=skinPoint*6.5;vec3 warp=vec3(noise3(p*.67+9.2),noise3(p*.81+21.7),noise3(p*.73+4.8));float mottles=organic(p+warp*1.8);float pores=noise3(skinPoint*83.0);base=mix(vec3(.20,.18,.11),vec3(.52,.48,.30),smoothstep(.24,.76,mottles));base*=.96+.08*pores;}
else if(material<1.5)base=vec3(.82,.73,.40);
else if(material<2.5)base=vec3(.44,.19,.035);
else if(material<3.5)base=vec3(.018,.012,.016);
else base=vec3(.83,.79,.60);
vec3 normal=normalize(n);float diffuse=.43+.57*max(0.0,dot(normal,normalize(vec3(-.4,-.7,1))));
float spec=pow(max(0.0,dot(reflect(-normalize(vec3(-.4,-.7,1)),normal),vec3(0,0,1))),26.0)*.16;
float ambient=clamp((world.z+190.0)/250.0,.13,1.0);
float exposed=smoothstep(95.0,260.0,world.z);diffuse=mix(diffuse,.65+.35*max(0.0,dot(normal,normalize(vec3(-.4,-.7,1)))),exposed);ambient*=1.0+.32*exposed;
color=vec4((base*diffuse+spec)*ambient,1);
}'''
HOLDOUT='''#version 330
uniform sampler2D photo;in vec2 texuv;out vec4 color;
void main(){if(texture(photo,texuv).a<.95)discard;color=vec4(0);}'''

def build():
    folder=ROOT/'assets/source/reef-model';ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST)
    shaders=[ctx.program(vertex_shader=VS,fragment_shader=fs)for fs in [FS,EEL_FS,HOLDOUT]]
    # Shader compilers remove unused attributes; bind only the active ones.
    def draw(index,v,uv,n,f,kind=None):
        p=shaders[index];p['stage'].value=STAGE
        skin=np.load(ROOT/'assets/source/eel-model/zany-moray.npz')['vertices']if index==1 else np.zeros_like(v)
        data=np.column_stack([v,uv,n,np.zeros(len(v))if kind is None else kind,skin]).astype('f4')
        names=['position','uv','normal','kind','skin'];sizes=[3,2,3,1,3];fmt=' '.join(str(size)+'f'if name in p else str(size*4)+'x'for name,size in zip(names,sizes));active=[name for name in names if name in p]
        vb=ctx.buffer(data.tobytes());ib=ctx.buffer(f.astype('i4').tobytes());vao=ctx.vertex_array(p,[(vb,fmt,*active)],ib);vao.render();vao.release();vb.release();ib.release()
    photo=Image.open(folder/'reef-projection.png').convert('RGBA');tex=ctx.texture(photo.size,4,photo.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);tex.use()
    record=json.loads((folder/'model.json').read_text());holdouts=[]
    for item in record['objects']:
        if item['name']=='hollow-tunnel':continue
        m=np.load(folder/item['file']);v=m['vertices'];f=m['faces'];tri=v[f]
        keep=(tri[:,:,0].max(axis=1)>=STAGE[0])&(tri[:,:,0].min(axis=1)<=STAGE[0]+STAGE[2])&(tri[:,:,1].max(axis=1)>=STAGE[1])&(tri[:,:,1].min(axis=1)<=STAGE[1]+STAGE[3])
        if keep.any():holdouts.append((v,m['uv'],m['normals'],f[keep]))
    cave=np.load(folder/'hollow-tunnel.npz');wall=shaders[0];wall['wall'].value=1
    fbo=ctx.simple_framebuffer((STAGE[2]*2,STAGE[3]*2),components=4);fbo.use()
    cols=8;poses=[];frames=[];out=ROOT/'work/cave-stage';out.mkdir(exist_ok=True)
    states=[(i/64,0.,0.)for i in range(65)]+[(1.,i/16,0.)for i in range(1,17)]+[(1.,0.,i/16)for i in range(1,17)]
    for i,(peek,mouth,funny)in enumerate(states):
        fbo.clear(0,0,0,0,depth=1)
        draw(0,cave['vertices'],cave['uv'],cave['normals'],cave['faces'])
        v,n,f,kind=animal(peek,mouth,funny);draw(1,v,np.zeros((len(v),2)),n,f,kind)
        # Holdouts write transparent pixels AND depth, using actual reef geometry.
        for args in holdouts:draw(2,*args)
        im=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize(STAGE[2:],Image.Resampling.LANCZOS)
        # Guard tiny resampling halos and keep opaque rock/animal interiors opaque.
        rgba=np.array(im);rgba[:,:,3][rgba[:,:,3]<5]=0;rgba[:,:,3][rgba[:,:,3]>250]=255;rgba[rgba[:,:,3]==0,:3]=0;im=Image.fromarray(rgba)
        poses.append(im)
        if i in [0,16,32,48,64]:im.save(out/f'pose-{i:02d}.png')
    # Crop the shared stage once, preserving identical placement in every state.
    # Transparent margins should not consume scarce device texture memory.
    boxes=[im.getbbox()for im in poses];left=max(0,min(b[0]for b in boxes)-2);top=max(0,min(b[1]for b in boxes)-2)
    right=min(STAGE[2],max(b[2]for b in boxes)+2);bottom=min(STAGE[3],max(b[3]for b in boxes)+2)
    width,height=right-left,bottom-top;stride=(width+4,height+4);atlas=Image.new('RGBA',(cols*stride[0],13*stride[1]))
    for i,im in enumerate(poses):
        x=i%cols*stride[0]+2;y=i//cols*stride[1]+2;atlas.paste(im.crop((left,top,right,bottom)),(x,y))
        frames.append(dict(x=x,y=y,w=width,h=height,anchorX=0,anchorY=0))
    # Lossless spatial storage, one shared colour palette for temporally stable detail.
    compact=imagequant.quantize_pil_image(atlas,max_colors=80,dithering_level=0,max_quality=95).convert('RGBA');compact.save(ROOT/'roku/images/cave-eel-3d.webp',lossless=True,method=6,exact=True)
    cfg=dict(image='pkg:/images/cave-eel-3d.webp',count=FRAME_COUNT,emergenceCount=COUNT,expressionSteps=16,frames=frames,x=STAGE[0]+left,y=STAGE[1]+top,model='shared 3D bending blind cave and pinned articulated moray',sharedDepthTest=True,root=[824,850,-158],headDepth=[-124,280])
    (ROOT/'roku/scenes/eel.json').write_text(json.dumps(cfg,indent=2)+'\n');(folder/'cave-stage.json').write_text(json.dumps(cfg,indent=2)+'\n')
    (ROOT/'roku/images/cave-interior.png').unlink(missing_ok=True)
    print('Packed',FRAME_COUNT,'joint cave/animal/expression states:',(ROOT/'roku/images/cave-eel-3d.webp').stat().st_size,'bytes',flush=True)
if __name__=='__main__':build()
