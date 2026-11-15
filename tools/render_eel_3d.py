"""Blender: an original fully modeled moray, articulated jaw, eyes and neck."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/eel-3d';OUT.mkdir(parents=True,exist_ok=True);SRC=ROOT/'assets/source/eel-model';SRC.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=False
scene.render.resolution_x=228;scene.render.resolution_y=280;scene.render.resolution_percentage=100;scene.render.film_transparent=True
scene.world.color=(.18,.18,.18);scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
def material(name,color,rough=.4):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m
skin=material('olive gold honeycomb skin',(.28,.19,.045));n=skin.node_tree.nodes;l=skin.node_tree.links;p=n.get('Principled BSDF');coord=n.new('ShaderNodeTexCoord');vor=n.new('ShaderNodeTexVoronoi');vor.inputs['Scale'].default_value=18;vor.feature='DISTANCE_TO_EDGE';l.new(coord.outputs['Generated'],vor.inputs['Vector']);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.035;ramp.color_ramp.elements[0].color=(.055,.035,.008,1);ramp.color_ramp.elements[1].position=.11;ramp.color_ramp.elements[1].color=(.42,.31,.10,1);l.new(vor.outputs['Distance'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color']);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=90;bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.018;l.new(coord.outputs['Generated'],noise.inputs['Vector']);l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
cream=material('warm golden eyeballs',(.70,.62,.28),.2);iris=material('amber iris',(.30,.11,.018),.22);black=material('pupils and mouth',(.006,.003,.004),.18);ivory=material('tiny ivory teeth',(.77,.72,.51),.3)
root=bpy.data.objects.new('head articulation',None);scene.collection.objects.link(root)
def ellipsoid(name,loc,scale,mat,parent=root):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat)
 for face in o.data.polygons:face.use_smooth=True
 if parent:o.parent=parent
 return o
ellipsoid('rounded moray cranium',(0,.02,.25),(.29,.34,.28),skin)
ellipsoid('long upper snout',(0,-.32,.20),(.245,.44,.15),skin)
ellipsoid('mouth recess',(0,-.32,.075),(.23,.40,.075),black)
jaw=bpy.data.objects.new('jaw hinge',None);scene.collection.objects.link(jaw);jaw.parent=root;jaw.location=(0,.05,.075)
ellipsoid('articulated lower jaw',(0,-.32,-.018),(.24,.42,.085),skin,jaw)
# Slightly unequal eye focus, with true spherical eyeballs, irises and pupils.
for side in [-1,1]:
 x=side*.247
 ellipsoid('protruding eye '+str(side),(x,-.14,.415),(.122,.110,.122),cream)
 ellipsoid('iris '+str(side),(x-side*.012,-.235,.423),(.081,.034,.083),iris)
 ellipsoid('pupil '+str(side),(x-side*.021,-.263,.433+side*.008),(.049,.015,.054),black)
 ellipsoid('nostril '+str(side),(side*.12,-.566,.24),(.024,.019,.019),black)
 # Upper teeth stay small and friendly, never a flat painted mouth.
 for i in range(3):
  bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.003,radius2=.015,depth=.053,location=(side*(.10+i*.045),-.48+i*.045,.068));o=bpy.context.object;o.name='upper tooth';o.parent=root;o.data.materials.append(ivory)
# Closed swept neck with a pinned lower attachment and 33 real shape keys.
verts=[];faces=[];rings=40;sides=40
for row in range(rings):
 t=row/(rings-1);z=-.95+t*1.14;radius=.18+.09*t
 for col in range(sides):
  a=col*2*math.pi/sides;verts.append((radius*math.cos(a),.12+radius*.82*math.sin(a),z))
for row in range(rings-1):
 for col in range(sides):
  a=row*sides+col;b=row*sides+(col+1)%sides;c=a+sides;d=b+sides;faces.extend([(a,b,d),(a,d,c)])
faces.append(tuple(reversed(range(sides))));faces.append(tuple((rings-1)*sides+i for i in range(sides)))
mesh=bpy.data.meshes.new('closed articulated neck');mesh.from_pydata(verts,[],faces);mesh.update();body=bpy.data.objects.new('moray neck volume',mesh);scene.collection.objects.link(body);body.data.materials.append(skin)
for f in mesh.polygons:f.use_smooth=True
body.shape_key_add(name='Basis')
for index in range(25):
 strength=-1+index/12;key=body.shape_key_add(name='neck pose %02d'%index)
 for i,(x,y,z)in enumerate(verts):
  t=(z+.95)/1.14;key.data[i].co=(x+strength*.055*t*t,y+strength*.015*t*t,z)
 key.value=0;key.keyframe_insert('value',frame=max(1,index));key.value=1;key.keyframe_insert('value',frame=index+1);key.value=0;key.keyframe_insert('value',frame=index+2)
 root.location=(strength*.055,strength*.015,0);root.rotation_euler=(0,math.radians(2)*strength,math.radians(12)*strength);root.keyframe_insert('location',frame=index+1);root.keyframe_insert('rotation_euler',frame=index+1)
 jaw.rotation_euler.x=math.radians(3+7*(strength+1)/2);jaw.keyframe_insert('rotation_euler',frame=index+1)
# Camera and genuine area lighting; no portrait image is used by any material.
bpy.ops.object.camera_add(location=(2.8,-5.2,1.0));camera=bpy.context.object;camera.name='portrait render camera';target=Vector((0,-.10,-.12));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=1.80;scene.camera=camera
for name,loc,power,color,size in [('warm key',(-2,-3,4),180,(1,.75,.56),3),('cool fill',(3,-1,2),95,(.55,.77,1),2),('rim',(1,3,2),140,(1,.5,.35),2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
scene.frame_start=1;scene.frame_end=25;scene.frame_set(13);bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'zany-moray.blend'))
record={'type':'procedural articulated closed 3D moray','frames':25,'meshes':[],'uses_portrait_texture':False}
import numpy as np
allverts=[];allfaces=[]
for o in scene.objects:
 if o.type!='MESH':continue
 offset=len(allverts);allverts.extend([tuple(o.matrix_world@v.co)for v in o.data.vertices]);o.data.calc_loop_triangles();allfaces.extend([tuple(offset+i for i in t.vertices)for t in o.data.loop_triangles]);record['meshes'].append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles)})
np.savez_compressed(SRC/'zany-moray.npz',vertices=np.array(allverts,dtype='f4'),faces=np.array(allfaces,dtype='i4'));(SRC/'model.json').write_text(json.dumps(record,indent=2)+'\n')
for frame in range(1,26):
 scene.frame_set(frame);scene.render.filepath=str(OUT/f'pose-{frame-1:02d}.png');bpy.ops.render.render(write_still=True)
