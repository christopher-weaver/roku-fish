"""Optional Blender inspection of the same slim fish and hinged pectoral meshes.
blender --background --python tools/blender_render.py -- --species yellow_tang --limit 1
"""
import sys,argparse,math,json
from pathlib import Path
import bpy
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int,default=256);parser.add_argument('--species',default='yellow_tang');parser.add_argument('--output',default='work/blender');parser.add_argument('--fin-pose',type=int,choices=range(9),default=2)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]if '--'in sys.argv else [])
out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
spec=json.loads((ROOT/'roku/scenes/species.json').read_text())[args.species]
data=np.load(ROOT/'assets/source'/(args.species+'.npz'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def textured_object(label,verts,faces,image_name):
    mesh=bpy.data.meshes.new(label);mesh.from_pydata(verts.tolist(),[],faces.tolist());mesh.update()
    obj=bpy.data.objects.new(label,mesh);bpy.context.collection.objects.link(obj);layer=mesh.uv_layers.new()
    for poly in mesh.polygons:
        for loop in poly.loop_indices:layer.data[loop].uv=data['uv'][mesh.loops[loop].vertex_index]
    mat=bpy.data.materials.new(label+' texture');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'assets/source'/image_name))
    emit=nodes.new('ShaderNodeEmission');transparent=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader');output=nodes.new('ShaderNodeOutputMaterial')
    links=mat.node_tree.links;links.new(tex.outputs['Color'],emit.inputs['Color']);links.new(tex.outputs['Alpha'],mix.inputs[0]);links.new(transparent.outputs[0],mix.inputs[1]);links.new(emit.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],output.inputs['Surface']);obj.data.materials.append(mat)
    return obj
body=textured_object(args.species,data['vertices'],data['faces'],args.species+'-texture.png')
fin=textured_object(args.species+' pectorals',data['fin_vertices'],data['fin_faces'],args.species+'-pectoral.png')
bpy.ops.object.camera_add(location=(0,0,5));camera=bpy.context.object;camera.data.type='ORTHO';camera.data.ortho_scale=2.22
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=False
scene.render.resolution_x=192;scene.render.resolution_y=168;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='Standard'
rendered=0
for yaw in range(spec['yawCount']):
    for pose,bend in enumerate(np.linspace(-.19,.19,spec['poseCount'])):
        for obj,key in [(body,'vertices'),(fin,'fin_vertices')]:
            v=data[key].copy()
            if obj==fin:
                travel=np.maximum(0,data['fin_hinge'][0]-v[:,0]);angle=args.fin_pose*.8/(spec['finPoseCount']-1)
                v[:,0]+=travel*(1-math.cos(angle));v[:,2]+=np.sign(v[:,2])*math.sin(angle)*travel
            rear=np.maximum(0,.28-v[:,0]);v[:,2]+=bend*rear**2;v[:,0]+=bend*bend*rear**3*.85
            for index,vertex in enumerate(obj.data.vertices):vertex.co=v[index]
            obj.rotation_euler=(0,-yaw*2*math.pi/spec['yawCount'],0)
        scene.render.filepath=str(out/f'{args.species}-{yaw:02}-{pose}-fin{args.fin_pose}.png');bpy.ops.render.render(write_still=True)
        rendered+=1
        if rendered>=args.limit:break
    if rendered>=args.limit:break
bpy.ops.wm.save_as_mainfile(filepath=str(out/(args.species+'.blend')))
print('Saved',rendered,'fish views with articulated fins and editable blend')
