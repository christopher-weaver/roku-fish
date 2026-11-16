"""Textured, ridged 3D seabed and the shared solid-floor navigation surface."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image
import moderngl
ROOT=Path(__file__).resolve().parents[1]
FLOOR=dict(baseY=865.,slope=205.,ridgeClearance=4.,nearZ=1.30,farZ=0.)

def ceiling(z,half_height,depth_radius):
    return FLOOR['baseY']+FLOOR['slope']*(z-depth_radius)-half_height-FLOOR['ridgeClearance']

def geometry():
    z,x=np.meshgrid(np.linspace(0,1.30,65),np.linspace(0,2048,257),indexing='ij')
    ridge=1.5*np.sin(z*110+np.sin(x/240)*.8)+.5*np.cos(z*220+x/700)
    y=FLOOR['baseY']+FLOOR['slope']*z+(1-z)*30+36-ridge
    v=np.column_stack([x.ravel(),y.ravel(),((z-.48)*600+90).ravel()]).astype('f4')
    uv=np.column_stack([x.ravel()/2048,1-(y.ravel()-920)/232]).astype('f4')
    row,col=np.mgrid[:64,:256];a=(row*257+col).ravel();b=a+1;c=a+257;d=c+1
    f=np.vstack([np.column_stack([a,b,c]),np.column_stack([b,d,c])]).astype('i4')
    from cave_geometry import normals
    return v,uv,normals(v,f),f

def build(refresh=False):
    folder=ROOT/'assets/source/reef-model';v,uv,n,f=geometry();np.savez_compressed(folder/'seafloor.npz',vertices=v,uv=uv,normals=n,faces=f)
    ctx=moderngl.create_standalone_context(backend='egl')
    p=ctx.program(vertex_shader='''#version 330
in vec3 position;in vec2 uv;out vec2 texuv;out float depth;
void main(){gl_Position=vec4(position.x/1024-1,1-(position.y-920)/116,0,1);texuv=uv;depth=(position.z-90)/600+.48;}''',fragment_shader='''#version 330
uniform sampler2D photo;in vec2 texuv;in float depth;out vec4 color;
void main(){vec3 c=texture(photo,texuv).rgb;color=vec4(c,smoothstep(0.0,.15,depth));}''')
    vb=ctx.buffer(np.column_stack([v,uv]).astype('f4').tobytes());ib=ctx.buffer(f.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 2f','position','uv')],ib)
    fb=ctx.simple_framebuffer((2048,232),components=4);fb.use();ctx.enable(moderngl.DEPTH_TEST)
    for mode in ['sunset','day']:
        path=ROOT/'roku/images'/('water-'+mode+'.webp');ref=folder/('water-'+mode+'-reference.webp')
        if refresh or not ref.exists():shutil.copy2(path,ref)
        source=Image.open(ref).convert('RGB');tile=source.crop((0,920,2048,1152));tile.save(folder/('seafloor-'+mode+'-projection.png'))
        tex=ctx.texture(tile.size,3,tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);tex.use();fb.clear(0,0,0,0,depth=1);vao.render()
        image=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);
        if mode=='sunset':image.save(ROOT/'roku/images'/'seafloor-sunset.webp',quality=84,method=6,exact=True)
        # Separate water and ground; no buried fish can hide in a sand backdrop.
        water=source.copy();water.paste(source.crop((0,920,2048,921)).resize((2048,232)),(0,920));water.save(path,quality=74,method=6)
        tex.release()
    cfgpath=ROOT/'roku/scenes/tank.json';cfg=json.loads(cfgpath.read_text());cfg['floor']=dict(FLOOR,x=0,y=920,width=2048,height=232,images={'Sunset':'pkg:/images/seafloor-sunset.webp','Daylight':'pkg:/images/seafloor-sunset.webp'},mesh='assets/source/reef-model/seafloor.npz');cfgpath.write_text(json.dumps(cfg,indent=2)+'\n')
    (ROOT/'roku/images/seafloor-day.webp').unlink(missing_ok=True)
    print('Built textured 3D seabed:',len(v),'vertices;',len(f),'triangles',flush=True)
if __name__=='__main__':build()
