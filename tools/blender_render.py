"""Optional editable Blender scene / renderer for the same checked-in fish meshes.
blender --background --python tools/blender_render.py -- --species yellow_tang --output work/blender
Uses Blender's built-in renderer; no addons or model downloads.
"""
import sys,argparse,math
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=48);parser.add_argument('--species',default='yellow_tang');parser.add_argument('--output',default='work/blender')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else [])
out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
data=np.load(ROOT/'assets/source'/(args.species+'.npz'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
verts=data['vertices'];faces=data['faces'];uv=data['uv']
mesh=bpy.data.meshes.new(args.species);mesh.from_pydata(verts.tolist(),[],faces.tolist());mesh.update()
obj=bpy.data.objects.new(args.species,mesh);bpy.context.collection.objects.link(obj)
layer=mesh.uv_layers.new()
for poly in mesh.polygons:
    for loop in poly.loop_indices:
        layer.data[loop].uv=uv[mesh.loops[loop].vertex_index]
mat=bpy.data.materials.new('photo texture');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'assets/source'/(args.species+'-texture.png')))
shader=nodes.new('ShaderNodeEmission');output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Color']);mat.node_tree.links.new(shader.outputs[0],output.inputs['Surface']);obj.data.materials.append(mat)
# Transparent film and orthographic image plane match the production offline renderer.
bpy.ops.object.camera_add(location=(0,0,5));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=2.22
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=False
scene.render.resolution_x=256;scene.render.resolution_y=224;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard'
base=verts.copy()
rendered=0
for yaw in range(16):
    for pose,bend in enumerate([-.19,0,.19]):
        v=base.copy();rear=np.maximum(0,.28-v[:,0]);v[:,2]+=bend*rear**2;v[:,0]+=bend*bend*rear**3*.85
        for index,vertex in enumerate(mesh.vertices):vertex.co=v[index]
        obj.rotation_euler=(0,-yaw*math.pi/8,0)
        scene.render.filepath=str(out/f'{args.species}-{yaw:02}-{pose}.png');bpy.ops.render.render(write_still=True)
        rendered+=1
        if rendered>=args.limit:break
    if rendered>=args.limit:break
bpy.ops.wm.save_as_mainfile(filepath=str(out/(args.species+'.blend')))
print('Saved',rendered,'editable Blender-rendered views and source blend')
