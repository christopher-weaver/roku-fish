"""Repartition a species' existing mesh and rebake its body/tail attachment.

Retains the approved geometry, textures, pectoral fins and all other species.
Usage: python tools/rebind_tail.py copperband_butterflyfish
"""
import argparse,json,math,subprocess,sys
import numpy as np
from PIL import Image
import moderngl,imagequant
import fish_mesh as mesh
from dense_turns import build as bake_body
from tail_rig import build as bind_roots

def build(name):
    path=mesh.SRC/(name+'.npz')
    with np.load(path) as source:data={key:source[key] for key in source.files}
    root,top,bottom=mesh.TAIL_RIGS[name]
    centers=data['uv'][data['faces']].mean(axis=1)
    tail=(centers[:,0]<root)&(centers[:,1]>1-bottom)&(centers[:,1]<1-top)
    data['body_faces']=data['faces'][~tail];data['tail_faces']=data['faces'][tail]
    np.savez_compressed(path,**data)
    species_path=mesh.ROOT/'roku/scenes/species.json'
    species=json.loads(species_path.read_text());sp=species[name]
    ctx=moderngl.create_standalone_context(backend='egl')
    program=ctx.program(vertex_shader=mesh.VS,fragment_shader=mesh.FS)
    ctx.enable(moderngl.DEPTH_TEST)
    vertices=np.hstack((data['vertices'],data['uv'],data['normals'])).astype('f4')
    vb=ctx.buffer(vertices.tobytes())
    def vao(faces):
        return ctx.vertex_array(program,[(vb,'3f 2f 3f','pos','uv','normal')],ctx.buffer(faces.tobytes()))
    body=vao(data['body_faces']);caudal=vao(data['tail_faces'])
    image=Image.open(mesh.SRC/(name+'-texture.png')).convert('RGBA')
    texture=ctx.texture(image.size,4,image.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes())
    texture.filter=(moderngl.LINEAR,moderngl.LINEAR);texture.use()
    fw,fh=sp['frameW'],sp['frameH'];fbo=ctx.simple_framebuffer((fw*4,fh*4),components=4);fbo.use()
    for key,value in dict(finPass=0,finAngle=0,hinge=(0,0),tailRoot=root*2-1).items():program[key].value=value
    shots=[]
    for yaw in range(mesh.UNIQUE_VIEWS):
        program['yaw'].value=yaw*2*math.pi/mesh.YAW_COUNT
        for pose,bend in enumerate(mesh.BODY_BENDS):
            fbo.clear(0,0,0,0,depth=1)
            program['bend'].value=0;program['depthOnly'].value=1;body.render()
            program['bend'].value=bend;program['depthOnly'].value=0;caudal.render()
            shot=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
            shots.append(mesh.cropped(shot,yaw,pose,fw,fh))
    atlas,unique=mesh.pack(shots)
    frames=[];count=len(mesh.BODY_BENDS)
    for yaw in range(mesh.YAW_COUNT):
        view=min(yaw,mesh.YAW_COUNT-yaw)
        for pose in range(count):
            source=count-1-pose if yaw>mesh.YAW_COUNT//2 else pose
            frames.append(dict(unique[view*count+source],yaw=yaw*360/mesh.YAW_COUNT,pose=pose,flipX=False))
    imagequant.quantize_pil_image(atlas,max_colors=80,dithering_level=0,max_quality=95).convert('RGBA').save(mesh.ROOT/'roku'/sp['tailImage'][5:],lossless=True,method=6,exact=True)
    sp['tailFrames']=frames;species_path.write_text(json.dumps(species,indent=2))
    bind_roots()
    bake_body([name])
    # Save the neutral views before whole_swim creates its three complete poses.
    species=json.loads(species_path.read_text());rest=mesh.SRC/'fish-rest'
    (rest/(name+'.webp')).write_bytes((mesh.ROOT/'roku'/sp['image'][5:]).read_bytes())
    neutral=json.loads((rest/'species.json').read_text());neutral[name]=dict(species[name])
    neutral[name].pop('bodyRenderMode',None);neutral[name].pop('bodySwimAmplitude',None)
    (rest/'species.json').write_text(json.dumps(neutral,indent=2))
    subprocess.run([sys.executable,str(mesh.ROOT/'tools/whole_swim.py'),'--species',name],check=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('species',choices=list(mesh.TAIL_RIGS))
    build(parser.parse_args().species)
