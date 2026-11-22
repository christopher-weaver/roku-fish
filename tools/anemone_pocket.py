"""A small, broken border of closed natural stones around the anemone foot."""
from pathlib import Path
import json
import numpy as np
import moderngl
from PIL import Image
from scipy.spatial import ConvexHull
from living_reef import Model,save,VS
ROOT=Path(__file__).resolve().parents[1]

def build():
    path=ROOT/'roku/scenes/tank.json';cfg=json.loads(path.read_text());folder=ROOT/'assets/source/reef-model'
    rng=np.random.default_rng(2401);model=Model()
    for index,angle in enumerate(np.linspace(-.14,np.pi+.14,9)):
        center=np.array([1474+66*np.cos(angle)+rng.uniform(-2,2),1022+13*np.sin(angle)+rng.uniform(-1.5,1.5),209+rng.uniform(-2,2)])
        radius=np.array([rng.uniform(9,13.5),rng.uniform(4.5,6.5),rng.uniform(6,10)])
        t=(np.arange(58)+.5)/58;y=1-2*t;theta=np.arange(58)*2.399963
        points=np.column_stack([np.sqrt(1-y*y)*np.cos(theta),y,np.sqrt(1-y*y)*np.sin(theta)])
        points=center+points*radius*rng.uniform(.81,1.12,(58,1))
        hull=ConvexHull(points);faces=hull.simplices.copy()
        for i,face in enumerate(faces):
            if np.dot(np.cross(points[face[1]]-points[face[0]],points[face[2]]-points[face[0]]),hull.equations[i,:3])<0:faces[i]=face[[0,2,1]]
        used=np.unique(faces);remap=np.full(len(points),-1,dtype=int);remap[used]=np.arange(len(used))
        model.add(points[used],remap[faces],np.array([.46,.44,.39])*(.94+.13*np.sin(index*2.399)))
    v,n,f,rgb,flow=save('anemone-base-rocks',model,folder)
    ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST)
    fs='''#version 330
in vec3 n;in vec3 color;in vec3 world;in vec2 texuv;out vec4 outcol;
float hash(vec3 p){return fract(sin(dot(p,vec3(127.1,311.7,74.7)))*43758.5453);}
float noise(vec3 p){vec3 i=floor(p),u=fract(p);u=u*u*(3.-2.*u);return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),u.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),u.x),u.y),mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),u.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),u.x),u.y),u.z);}
void main(){float grain=noise(world*1.6);float pores=pow(max(0.,noise(world*3.7)-.62),1.5);vec3 base=color*(.88+.20*grain-.35*pores);vec3 face=normalize(cross(dFdx(world),dFdy(world)));if(dot(face,n)<0.)face=-face;float light=.40+.60*max(0.,dot(face,normalize(vec3(-.35,-.7,1.))));outcol=vec4(base*light,1.);}'''
    p=ctx.program(vertex_shader=VS,fragment_shader=fs);p['stage'].value=(0,0,2048,1152);p['strength'].value=0
    vb=ctx.buffer(np.column_stack([v,n,rgb,flow]).astype('f4').tobytes());ib=ctx.buffer(f.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f','position','normal','rgb','flow')],ib)
    fb=ctx.simple_framebuffer((2048,1152),components=4);fb.use();fb.clear(0,0,0,0,depth=1);vao.render()
    im=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);box=im.getchannel('A').getbbox();im=im.crop(box);im.save(ROOT/'roku/images/reef-anemone-base-rocks.webp',quality=88,method=6,exact=True)
    props={'anemone-rim','anemone-platform','anemone-lip','anemone-foot-rocks','anemone-base-rocks'}
    cfg['formations']=[f for f in cfg['formations']if f['id']not in props]
    cfg['formations'].append(dict(id='anemone-base-rocks',image='pkg:/images/reef-anemone-base-rocks.webp',x=box[0],y=box[1],width=im.width,height=im.height,frameWidth=im.width,frameHeight=im.height,frames=1,columns=1,z=.76,halfDepth=.015,parallax=1,renderedMesh=True,meshVertices=len(v),meshTriangles=len(f),meshObjects=['anemone-base-rocks']))
    cfg['formations'].sort(key=lambda f:f['z']);cfg['occlusionDepths']=[f['z']for f in cfg['formations']]
    cfg.pop('anemonePocket',None);cfg.pop('anemonePlatform',None)
    cfg['anemoneHabitat']={'support':'foreground-reef','fullBase':True,'drapedTentacles':False,'seatOffsetY':12,'border':'anemone-base-rocks','edgeDarkening':.62,'sandTransition':'existing modeled seabed'}
    path.write_text(json.dumps(cfg,indent=2)+'\n');path=folder/'model.json';record=json.loads(path.read_text())
    record['objects']=[o for o in record['objects']if o['name']not in ['anemone-pocket-rim','anemone-platform','anemone-base-rocks']]
    record['objects'].append(dict(name='anemone-base-rocks',group='anemone-base-rocks',layer='anemone-base-rocks',file='anemone-base-rocks.npz',vertices=len(v),triangles=len(f),closed=True,sculpted=True));path.write_text(json.dumps(record,indent=2)+'\n')
    for name in props-{'anemone-base-rocks'}:
        for prefix in ['reef-','shadow-']:(ROOT/'roku/images'/f'{prefix}{name}.webp').unlink(missing_ok=True)
    print('Small rock border:',im.size,'9 independent closed stones; no continuous rim',flush=True)
if __name__=='__main__':build()
