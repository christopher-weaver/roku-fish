"""Closed rock platform with a low retaining lip and feathered sand apron."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
import moderngl
from living_reef import Model,save,VS
ROOT=Path(__file__).resolve().parents[1]

def stone(model,cx,cy,rx,ry,height,seed):
    sides=128;vertices=[];faces=[]
    # Broad, gently uneven upper shelf, a broken edge and a closed underside.
    profile=[(.015,0,height),(.50,0,height+3),(.91,1,height),(1.,5,height-7),(.98,16,height-20),(.80,24,height-34),(.015,24,height-38)]
    for ring,(r,drop,z) in enumerate(profile):
        for i in range(sides):
            a=i*2*np.pi/sides
            rough=1+.033*np.sin(a*7+seed)+.019*np.sin(a*13-seed)
            vertices.append((cx+rx*r*np.cos(a)*rough,cy+ry*r*np.sin(a)*rough+drop,z+2.5*np.sin(a*5+seed)*r))
    for row in range(len(profile)-1):
        for i in range(sides):
            a=row*sides+i;b=row*sides+(i+1)%sides;c=a+sides;d=b+sides
            faces.extend([(a,b,c),(b,d,c)])
    for i in range(1,sides-1):faces.extend([(0,i+1,i),((len(profile)-1)*sides,(len(profile)-1)*sides+i,(len(profile)-1)*sides+i+1)])
    model.add(vertices,np.asarray(faces),(0.7,0.6,0.5))

def build():
    folder=ROOT/'assets/source/reef-model';cfgpath=ROOT/'roku/scenes/tank.json';cfg=json.loads(cfgpath.read_text())
    model=Model()
    # The apron is also a closed shallow volume. Its outer pixels feather into sand.
    model.sphere((1474,1053,75),(222,42,8),(.1,.1,.1),ridges=.035)
    stone(model,1474,1023,166,29,158,3)
    # Only a few pixels of front curb overlap the very tip of the full foot.
    # Keep it separate from the broad rear platform so it reads as a tiny lip.
    angle=np.linspace(-.28,np.pi+.28,129)
    lip_path=np.column_stack([1474+92*np.cos(angle),1005+13*np.sin(angle),210+1.4*np.sin(angle*5)])
    lip_start=len(model.f)
    model.tube(lip_path,3.8+.3*np.sin(angle*7)**2,(.84,.72,.6),sides=20)
    lip_end=len(model.f)
    stone(model,1308,1041,34,14,145,7)
    stone(model,1640,1037,31,15,147,11)
    v,n,f,rgb,flow=save('anemone-platform',model,folder)
    yy,xx=np.mgrid[:1152,:2048]
    reef=Image.open(folder/'reef-projection.png').convert('RGB')
    rock=np.asarray(reef.crop((800,610,1180,870)).resize((430,165),Image.Resampling.LANCZOS))
    rock=rock[np.clip(yy-947,0,164),np.clip(xx-1259,0,429)].astype(float)
    sand=np.asarray(Image.open(folder/'seafloor-sunset-projection.png').convert('RGB'))
    sand=sand[np.clip(yy-920,0,sand.shape[0]-1),xx].astype(float)
    Image.fromarray(np.uint8(sand)).save(folder/'anemone-platform-sand.png')
    # Sparse settled grains across the ledge and continuous sand along its foot.
    grain=(np.sin(xx*2.13+yy*3.19)*np.sin(xx*.73-yy*1.27)+1)*.5
    edge=np.clip((yy-1043+3*np.sin(xx*.08))/18,0,1)
    dust=np.clip((grain-.87)*3,0,.18)+np.clip((yy-1034)/60,0,.12)
    blend=np.maximum(edge,dust)[:,:,None]
    color=np.uint8(np.clip(rock*(1-blend)+sand*blend,0,255))
    color=Image.fromarray(color);color.save(folder/'anemone-platform-colour.png')
    ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST)
    fs='''#version 330
uniform sampler2D photo;uniform sampler2D sandPhoto;in vec3 n;in vec3 color;in vec3 world;in vec2 texuv;out vec4 outcol;
void main(){vec3 base=texture(photo,texuv).rgb;float a=1.;float light=.83+.17*max(0.,dot(normalize(n),normalize(vec3(-.35,-.7,1.))));if(color.r>.8){base=min(base*1.20,vec3(.92));light=.67+.33*max(0.,dot(normalize(n),normalize(vec3(-.35,-.7,1.))));}if(color.r<.2){float r=length(vec2((world.x-1474.)/222.,(world.y-1053.)/42.));a=1.-smoothstep(.65,.99,r);light=1.;base=texture(sandPhoto,texuv).rgb;}outcol=vec4(base*light,a);}'''
    p=ctx.program(vertex_shader=VS,fragment_shader=fs);p['stage'].value=(0,0,2048,1152);p['strength'].value=0
    texture=ctx.texture(color.size,3,color.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());texture.filter=(moderngl.LINEAR,moderngl.LINEAR);texture.use(location=0);p['photo'].value=0
    sand_texture=ctx.texture(color.size,3,Image.fromarray(np.uint8(sand)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());sand_texture.filter=(moderngl.LINEAR,moderngl.LINEAR);sand_texture.use(location=1);p['sandPhoto'].value=1
    vb=ctx.buffer(np.column_stack([v,n,rgb,flow]).astype('f4').tobytes());platform_faces=np.concatenate([f[:lip_start],f[lip_end:]])
    ib=ctx.buffer(platform_faces.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f','position','normal','rgb','flow')],ib)
    fb=ctx.simple_framebuffer((2048,1152),components=4);fb.use();fb.clear(0,0,0,0,depth=1);vao.render()
    im=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);box=im.getchannel('A').getbbox();im=im.crop(box)
    im.save(ROOT/'roku/images/reef-anemone-platform.webp',quality=84,method=6,exact=True)
    formation=dict(id='anemone-platform',image='pkg:/images/reef-anemone-platform.webp',x=box[0],y=box[1],width=im.width,height=im.height,frameWidth=im.width,frameHeight=im.height,frames=1,columns=1,z=.74,halfDepth=.035,parallax=1,renderedMesh=True,meshVertices=len(v),meshTriangles=len(f),meshObjects=['anemone-platform'])
    # The small front curb uses the same immutable mesh and photographic map.
    lip_ib=ctx.buffer(f[lip_start:lip_end].tobytes());lip_vao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f','position','normal','rgb','flow')],lip_ib)
    fb.clear(0,0,0,0,depth=1);lip_vao.render();lip=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);lip_box=lip.getchannel('A').getbbox();lip=lip.crop(lip_box);lip.save(ROOT/'roku/images/reef-anemone-lip.webp',quality=85,method=6,exact=True)
    lip_formation=dict(id='anemone-lip',image='pkg:/images/reef-anemone-lip.webp',x=lip_box[0],y=lip_box[1],width=lip.width,height=lip.height,frameWidth=lip.width,frameHeight=lip.height,frames=1,columns=1,z=.76,halfDepth=.01,parallax=1,renderedMesh=True,meshVertices=129*20+2,meshTriangles=lip_end-lip_start,meshObjects=['anemone-platform'])
    cfg['formations']=[f for f in cfg['formations']if f['id']not in ['anemone-rim','anemone-platform','anemone-lip']]+[formation,lip_formation];cfg['formations'].sort(key=lambda f:f['z']);cfg['occlusionDepths']=[f['z']for f in cfg['formations']]
    cfg.pop('anemonePocket',None);cfg['anemonePlatform']={'x':1474,'supportY':1023,'lip':{'centerY':1005,'radiusX':92,'radiusY':13,'thickness':3.8,'formation':'anemone-lip'},'fullBase':True,'sandApron':True,'formation':'anemone-platform'}
    cfgpath.write_text(json.dumps(cfg,indent=2)+'\n')
    p=folder/'model.json';record=json.loads(p.read_text());record['objects']=[o for o in record['objects']if o['name']not in ['anemone-pocket-rim','anemone-platform']]
    record['objects'].append(dict(name='anemone-platform',group='anemone-platform',layer='anemone-platform',file='anemone-platform.npz',vertices=len(v),triangles=len(f),closed=True,sculpted=True));p.write_text(json.dumps(record,indent=2)+'\n')
    for old in [ROOT/'roku/images/reef-anemone-rim.webp',ROOT/'roku/images/shadow-anemone-rim.webp',folder/'anemone-pocket-rim.npz',folder/'anemone-pocket-rim-colour.png']:old.unlink(missing_ok=True)
    print('Rock platform with small retaining lip, complete base and sand apron:',im.size,flush=True)
if __name__=='__main__':build()
