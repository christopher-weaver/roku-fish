"""Blender source scene for every individually modeled reef piece and bore."""
import bpy,json
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'assets/source/reef-model'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.use_denoising=False;scene.cycles.samples=32;scene.render.resolution_x=2048;scene.render.resolution_y=1152;scene.render.resolution_percentage=100;scene.render.film_transparent=True
photo=bpy.data.images.load(str(folder/'reef-projection.png'));photo.pack()
mat=bpy.data.materials.new('original projected coral colour');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.85;t=n.new('ShaderNodeTexImage');t.image=photo;l.new(t.outputs['Color'],p.inputs['Base Color']);l.new(t.outputs['Alpha'],p.inputs['Alpha'])
wall=bpy.data.materials.new('recessed rock bore');wall.diffuse_color=(.20,.12,.12,1);wall.use_nodes=True;p=wall.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.20,.12,.12,1);p.inputs['Roughness'].default_value=.9;wt=wall.node_tree.nodes.new('ShaderNodeTexImage');wt.image=photo;wall.node_tree.links.new(wt.outputs['Color'],p.inputs['Base Color'])
record=json.loads((folder/'model.json').read_text())
for item in record['objects']:
 with np.load(folder/item['file'])as data:
  v=data['vertices'].copy();v[:,1]*=-1;faces=data['faces'][:,::-1];uv=data['uv'];norm=data['normals'].copy();norm[:,1]*=-1
 mesh=bpy.data.meshes.new(item['name']);mesh.from_pydata(v.tolist(),[],faces.tolist());mesh.update();o=bpy.data.objects.new(item['name'],mesh);scene.collection.objects.link(o);o.data.materials.append(wall if item['name']=='hollow-tunnel'else mat)
 layer=mesh.uv_layers.new(name='reference projection')
 for loop in mesh.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
 for polygon in mesh.polygons:polygon.use_smooth=True
 try:mesh.normals_split_custom_set_from_vertices(norm.tolist())
 except Exception:pass
 o['anatomical_group']=item['group'];o['closed_volume']=item['closed']
 print('Imported',o.name,len(v),flush=True)
# Include the existing 3D fan/anemone volumes in the same reviewable scene.
# Blender's bundled Python may not include Pillow; the fixed texture tiles are
# authored by connected_scene in the normal Python build before this exporter.
for name,ox,oy,width,height,base_z in [('sea-fan',80,430,600,565,-45),('sea-anemone',1330,815,285,215,135)]:
 path=ROOT/'assets/source/marine-renders'/(name+'-volume.npz')
 with np.load(path)as data:
  v=data['vertices'].copy();uv=data['uv'];faces=data['faces'][:,::-1]
 v[:,0]=(v[:,0]+1)*(width+16)/2+ox-8
 v[:,1]=-((1-v[:,1])*(height+16)/2+oy-8)
 v[:,2]=v[:,2]*100+base_z
 mesh=bpy.data.meshes.new(name+' closed volume');mesh.from_pydata(v.tolist(),[],faces.tolist());mesh.update();o=bpy.data.objects.new(name+' modeled volume',mesh);scene.collection.objects.link(o)
 m=bpy.data.materials.new(name+' original finished material');m.use_nodes=True;node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(folder/(name+'-projection.png')));node.image.pack();principled=m.node_tree.nodes.get('Principled BSDF');m.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);m.node_tree.links.new(node.outputs['Alpha'],principled.inputs['Alpha']);principled.inputs['Roughness'].default_value=.7;o.data.materials.append(m)
 layer=mesh.uv_layers.new(name='volume UV')
 for loop in mesh.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
 for polygon in mesh.polygons:polygon.use_smooth=True
# Append the actual articulated animal and place it inside the modeled bore.
eel_path=ROOT/'assets/source/eel-model/zany-moray.blend'
if eel_path.exists():
 with bpy.data.libraries.load(str(eel_path),link=False)as (src,dst):dst.objects=[name for name in src.objects if name not in ['portrait render camera','warm key','cool fill','rim']]
 assembly=bpy.data.objects.new('tunnel moray assembly',None);scene.collection.objects.link(assembly);assembly.rotation_euler.x=-1.57079632679;assembly.scale=(80,80,80)
 for o in dst.objects:
  if o is not None:
   scene.collection.objects.link(o)
   if o.parent is None:o.parent=assembly
 for frame,position in [(1,(773,-886,-30)),(13,(773,-864,55)),(25,(773,-886,-30))]:
  assembly.location=position;assembly.keyframe_insert('location',frame=frame)
 scene.frame_start=1;scene.frame_end=25;scene.frame_set(13)
bpy.ops.object.camera_add(location=(1024,-576,3000));camera=bpy.context.object;camera.rotation_euler=(0,0,0);camera.data.type='ORTHO';camera.data.ortho_scale=2048;scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(200,200,1800));light=bpy.context.object;light.data.energy=1200000;light.data.size=1800;light.rotation_euler=(Vector((1024,-576,0))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.25,.25,.25);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'reef-scene.blend'),compress=True)
