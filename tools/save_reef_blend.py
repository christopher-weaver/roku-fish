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
  v=data['vertices'].copy();v[:,1]*=-1;faces=data['faces'][:,::-1];uv=data['material_uv']if item['name']=='articulated-clam'else data['uv'];norm=data['normals'].copy();norm[:,1]*=-1
  rgb=data['rgb'].copy()if 'rgb'in data else None
 mesh=bpy.data.meshes.new(item['name']);mesh.from_pydata(v.tolist(),[],faces.tolist());mesh.update();o=bpy.data.objects.new(item['name'],mesh);scene.collection.objects.link(o);o.data.materials.append(wall if item['name']=='hollow-tunnel'else mat)
 layer=mesh.uv_layers.new(name='reference projection')
 for loop in mesh.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
 for polygon in mesh.polygons:polygon.use_smooth=True
 try:mesh.normals_split_custom_set_from_vertices(norm.tolist())
 except Exception:pass
 if rgb is not None:
  colors=mesh.color_attributes.new(name='sculpted colour',type='FLOAT_COLOR',domain='POINT');colors.data.foreach_set('color',np.column_stack([rgb,np.ones(len(rgb))]).ravel());material=bpy.data.materials.new(item['name']+' shaded material');material.use_nodes=True;node=material.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='sculpted colour';material.node_tree.links.new(node.outputs['Color'],material.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);
  if (folder/(item['name']+'-colour.png')).exists():
   texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(folder/(item['name']+'-colour.png')));texture.image.pack();material.node_tree.links.new(texture.outputs['Color'],material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
  if item['name']=='anemone-base-rocks':
   for polygon in mesh.polygons:polygon.use_smooth=False
   principled=material.node_tree.nodes.get('Principled BSDF');principled.inputs['Roughness'].default_value=.94
   noise=material.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=32;noise.inputs['Detail'].default_value=3
   bump=material.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.25;bump.inputs['Distance'].default_value=.12;material.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);material.node_tree.links.new(bump.outputs['Normal'],principled.inputs['Normal'])
  if item['name']=='articulated-clam':
   texture=material.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(ROOT/'assets/source/marine-renders/clam-material.png'));texture.image.pack();material.node_tree.links.new(texture.outputs['Color'],material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
  o.data.materials.clear();o.data.materials.append(material)
 if item['name']=='articulated-clam':
  o.shape_key_add(name='Basis');key=o.shape_key_add(name='Upper valve open at hinge');opened=np.load(folder/'clam-open.npz')['vertices'].copy();opened[:,1]*=-1;key.data.foreach_set('co',opened.ravel())
 o['anatomical_group']=item['group'];o['closed_volume']=item['closed']
 print('Imported',o.name,len(v),flush=True)
# The ridged, textured floor and closed rock footings share the reef's axes.
for name in ['seafloor','grounded-footings']:
 with np.load(folder/(name+'.npz'))as data:
  v=data['vertices'].copy();v[:,1]*=-1;faces=data['faces'][:,::-1];uv=data['uv']
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(v.tolist(),[],faces.tolist());mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o)
 if name=='seafloor':
  m=bpy.data.materials.new('original sand colour on ridged floor');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.92;t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(folder/'seafloor-sunset-projection.png'));t.image.pack();m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);o.data.materials.append(m)
 else:o.data.materials.append(mat)
 layer=mesh.uv_layers.new(name='ground texture UV')
 for loop in mesh.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
 for polygon in mesh.polygons:polygon.use_smooth=True
# Include the existing 3D fan/anemone volumes in the same reviewable scene.
# Blender's bundled Python may not include Pillow; the fixed texture tiles are
# authored by connected_scene in the normal Python build before this exporter.
for name,ox,oy,width,height,base_z in [('sea-fan',80,430,600,565,-45),('sea-anemone',1330,815,285,215,135)]:
 if name=='sea-fan':
  with np.load(ROOT/'assets/source/marine-renders/sea-fan-volume.npz')as data:v=data['vertices'].copy();uv=data['uv'];faces=data['faces'][:,::-1]
  v[:,0]=(v[:,0]+1)*(width+16)/2+ox-8;v[:,1]=-((1-v[:,1])*(height+16)/2+oy-8);v[:,2]=v[:,2]*100+base_z
  mesh=bpy.data.meshes.new('approved lacy sea fan');mesh.from_pydata(v.tolist(),[],faces.tolist());mesh.update();o=bpy.data.objects.new('restored approved sea fan',mesh);scene.collection.objects.link(o)
  material=bpy.data.materials.new('approved sea fan colour');material.use_nodes=True;node=material.node_tree.nodes.new('ShaderNodeTexImage');node.image=bpy.data.images.load(str(folder/'sea-fan-projection.png'));node.image.pack();material.node_tree.links.new(node.outputs['Color'],material.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);material.node_tree.links.new(node.outputs['Alpha'],material.node_tree.nodes.get('Principled BSDF').inputs['Alpha']);o.data.materials.append(material)
  layer=mesh.uv_layers.new(name='approved fan UV')
  for loop in mesh.loops:layer.data[loop.index].uv=uv[loop.vertex_index]
  for polygon in mesh.polygons:polygon.use_smooth=True
  continue
 path=ROOT/'assets/source/marine-renders'/(name+'-sculpted.npz')
 with np.load(path)as data:v=data['vertices'].copy();rgb=data['rgb'];opacity=data['opacity'];material_uv=data['material_uv'];flow=data['flow'].copy();faces=data['faces'][:,::-1];edge_shade=1-.62*np.where(opacity>.99,1.,.25)*(1-np.clip(np.abs(data['normals'][:,2]),0,1))**1.2
 v[:,1]*=-1;flow[:,1]*=-1
 mesh=bpy.data.meshes.new(name+' sculpted anatomy');mesh.from_pydata(v.tolist(),[],faces.tolist());mesh.update();o=bpy.data.objects.new(name+' individual 3D branches and tentacles',mesh);scene.collection.objects.link(o)
 colors=mesh.color_attributes.new(name='sculpted colour',type='FLOAT_COLOR',domain='POINT');colors.data.foreach_set('color',np.column_stack([rgb,opacity]).ravel())
 m=bpy.data.materials.new(name+' shaded tissue');m.use_nodes=True;node=m.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name='sculpted colour';m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.38;p.inputs['Subsurface Weight'].default_value=.16;p.inputs['Transmission Weight'].default_value=.06;p.inputs['Alpha'].default_value=.8;m.node_tree.links.new(node.outputs['Alpha'],p.inputs['Alpha']);texture=m.node_tree.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(ROOT/'assets/source/marine-renders/anemone-material.png'));texture.image.pack();m.node_tree.links.new(texture.outputs['Color'],p.inputs['Base Color']);o.data.materials.append(m)
 shade=mesh.color_attributes.new(name='rounded edge shade',type='FLOAT_COLOR',domain='POINT');shade.data.foreach_set('color',np.column_stack([edge_shade,edge_shade,edge_shade,np.ones(len(edge_shade))]).ravel())
 edge_node=m.node_tree.nodes.new('ShaderNodeVertexColor');edge_node.layer_name='rounded edge shade'
 multiply=m.node_tree.nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=1.;m.node_tree.links.new(texture.outputs['Color'],multiply.inputs[1]);m.node_tree.links.new(edge_node.outputs['Color'],multiply.inputs[2]);m.node_tree.links.new(multiply.outputs[0],p.inputs['Base Color'])
 uv=mesh.uv_layers.new(name='reference tissue colour')
 for loop in mesh.loops:
  uv.data[loop.index].uv=material_uv[loop.vertex_index]
 for polygon in mesh.polygons:polygon.use_smooth=True
 o.shape_key_add(name='Basis')
 for index,strength in enumerate([-1.,0.,1.]):
  key=o.shape_key_add(name='individual tip motion %d'%index);key.data.foreach_set('co',(v+flow*strength).ravel())
 o['motion']='individually pinned branches/tentacles bending in all three axes'
# Use exactly the same pinned animal poses and cave coordinates as the render.
import sys
sys.path.insert(0,str(ROOT/'tools'))
from cave_geometry import animal,COUNT,FRAME_COUNT
v,n,faces,kind=animal(0)
v[:,1]*=-1
mesh=bpy.data.meshes.new('moray shared cave geometry');mesh.from_pydata(v.tolist(),[],faces[:,::-1].tolist());mesh.update()
o=bpy.data.objects.new('moray anchored inside blind cave',mesh);scene.collection.objects.link(o)
for name,color in [('mottled moray skin',(.38,.35,.22)),('eyeball',(.82,.73,.40)),('iris',(.44,.19,.035)),('pupil and mouth',(.018,.012,.016)),('teeth',(.83,.79,.60))]:
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*color,1);o.data.materials.append(m)
rest=np.load(ROOT/'assets/source/eel-model/zany-moray.npz')['vertices']
attribute=mesh.attributes.new(name='skin_rest',type='FLOAT_VECTOR',domain='POINT');attribute.data.foreach_set('vector',rest.ravel())
skin=o.data.materials[0];nodes=skin.node_tree.nodes;links=skin.node_tree.links;principled=nodes.get('Principled BSDF');coordinate=nodes.new('ShaderNodeAttribute');coordinate.attribute_name='skin_rest';noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=6.5;noise.inputs['Detail'].default_value=3;links.new(coordinate.outputs['Vector'],noise.inputs['Vector']);ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[0].color=(.20,.18,.11,1);ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(.52,.48,.30,1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],principled.inputs['Base Color']);principled.inputs['Roughness'].default_value=.36
for polygon in mesh.polygons:polygon.use_smooth=True;polygon.material_index=int(kind[polygon.vertices[0]])
o.shape_key_add(name='Basis')
for index in range(COUNT):
 v,_,_,_=animal(index/(COUNT-1));v[:,1]*=-1;key=o.shape_key_add(name='cave emergence %02d'%index)
 key.data.foreach_set('co',v.ravel());key.value=0;key.keyframe_insert('value',frame=max(0,index));key.value=1;key.keyframe_insert('value',frame=index+1);key.value=0;key.keyframe_insert('value',frame=index+2)
for kind in ['mouth','funny']:
 for step in range(1,17):
  v,_,_,_=animal(1.,step/16 if kind=='mouth'else 0.,step/16 if kind=='funny'else 0.);v[:,1]*=-1;key=o.shape_key_add(name=kind+' expression %02d'%step);key.data.foreach_set('co',v.ravel())
o['pinned_rear_attachment']=[824,-850,-158];o['shared_cave_depth_test']=True
scene.frame_start=1;scene.frame_end=COUNT;scene.frame_set(49)
bpy.ops.object.camera_add(location=(1024,-576,3000));camera=bpy.context.object;camera.rotation_euler=(0,0,0);camera.data.type='ORTHO';camera.data.ortho_scale=2048;scene.camera=camera
bpy.ops.object.light_add(type='AREA',location=(200,200,1800));light=bpy.context.object;light.data.energy=1200000;light.data.size=1800;light.rotation_euler=(Vector((1024,-576,0))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.25,.25,.25);bpy.ops.wm.save_as_mainfile(filepath=str(folder/'reef-scene.blend'),compress=True)
