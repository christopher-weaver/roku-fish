"""Add true mesh views near head-on turns, retaining existing tail/fin atlases."""
from pathlib import Path
import json,math,sys
import numpy as np
from PIL import Image
import moderngl,imagequant
import fish_mesh
ROOT=Path(__file__).resolve().parents[1]
def angles():
    values={i*5.625 for i in range(33)}
    for i in range(12,20):values.add((i+.5)*5.625)
    for i in range(14,18):
        values.update([(i+.25)*5.625,(i+.75)*5.625])
    values.update([85.078125,86.484375,87.890625,89.296875,90.703125,92.109375,93.515625,94.921875])
    return sorted(values)
def build(names=None):
    path=ROOT/'roku/scenes/species.json';data=json.loads(path.read_text())
    ctx=moderngl.create_standalone_context(backend='egl');p=ctx.program(vertex_shader=fish_mesh.VS,fragment_shader=fish_mesh.FS);ctx.enable(moderngl.DEPTH_TEST)
    unique_angles=angles();all_angles=unique_angles+[360-a for a in reversed(unique_angles[1:-1])]
    for name,sp in data.items():
        if names is not None and name not in names:continue
        with np.load(ROOT/'assets/source'/(name+'.npz'))as m:
            vertices=np.hstack((m['vertices'],m['uv'],m['normals'])).astype('f4');faces=m['body_faces']
        vb=ctx.buffer(vertices.tobytes());ib=ctx.buffer(faces.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 2f 3f','pos','uv','normal')],ib)
        im=Image.open(ROOT/'assets/source'/(name+'-texture.png')).convert('RGBA');tex=ctx.texture(im.size,4,im.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());tex.filter=(moderngl.LINEAR,moderngl.LINEAR);tex.use()
        fw,fh=sp['frameW'],sp['frameH'];fbo=ctx.simple_framebuffer((fw*4,fh*4),components=4);fbo.use()
        p['bend'].value=0;p['finPass'].value=0;p['finAngle'].value=0;p['depthOnly'].value=0;p['hinge'].value=(0,0);p['tailRoot'].value=0
        shots=[]
        for angle in unique_angles:
            p['yaw'].value=math.radians(angle);fbo.clear(0,0,0,0,depth=1);vao.render()
            shot=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
            piece,meta=fish_mesh.cropped(shot,0,0,fw,fh);meta['yaw']=angle;shots.append((piece,meta))
        atlas,unique=fish_mesh.pack(shots);lookup={angle:i for i,angle in enumerate(unique_angles)}
        frames=[dict(unique[lookup[min(a,360-a)]],yaw=a,flipX=False)for a in all_angles]
        sp.update(frames=frames,poseCount=1,width=atlas.width,height=atlas.height,bodyYawCount=len(frames),bodyAngles=[math.radians(a)for a in all_angles],bodyViewWidths=[max(1,f['w']-4)for f in frames])
        raw=ROOT/'work/fish-raw';raw.mkdir(parents=True,exist_ok=True);atlas.save(raw/(name+'-atlas.png'))
        (ROOT/'roku/images'/(name+'-atlas.png')).unlink(missing_ok=True)
        compact=imagequant.quantize_pil_image(atlas,max_colors=80 if name in ['green_chromis','royal_gramma']else 96,dithering_level=0,max_quality=95)
        compact.convert('RGBA').save(ROOT/'roku'/sp['image'][5:],lossless=True,method=6,exact=True)
        for o in [vao,vb,ib,tex,fbo]:o.release()
        print(name,len(frames),'body slots /',len(unique),'unique head-on-refined views',flush=True)
    path.write_text(json.dumps(data,indent=2))
if __name__=='__main__':build()
