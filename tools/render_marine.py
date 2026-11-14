"""Offline true-geometry sea fan and anemone; Blender/Cycles, transparent RGBA."""
from pathlib import Path
import bpy,math,random
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/source/marine-renders';OUT.mkdir(exist_ok=True)
rng=random.Random(47831)
def clear():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,color,rough=.55):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=75;noise.inputs['Detail'].default_value=3
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.012
 m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 return m

def paths(name,lines,radius,mat):
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=2;curve.bevel_depth=radius;curve.bevel_resolution=3;curve.use_fill_caps=True
 for points,weights in lines:
  spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
  for point,co,weight in zip(spline.points,points,weights):point.co=(*co,1);point.radius=weight
 obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
 return obj

def render(name,target,ortho,location):
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=False
 scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
 scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='AgX'
 world=bpy.data.worlds.new('Marine ambient');scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.43,.50,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55
 for loc,power,size,color in [((-3,-4,6),650,4,(1,.88,.75)),((3,-2,3),350,3,(.65,.82,1)),((1,3,5),500,3,(1,.66,.49))]:
  bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=power;lamp.data.shape='DISK';lamp.data.size=size;lamp.data.color=color;lamp.rotation_euler=(Vector(target)-lamp.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=location);camera=bpy.context.object;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=ortho;scene.camera=camera
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))

clear();fanmat=material('Gorgonian copper polyps',(.5,.12,.025));lines=[];ribs=25;rings=25
points={}
for i in range(ribs):
 angle=(i/(ribs-1)-.5)*1.8
 line=[]
 for j in range(rings):
  r=.12+j/(rings-1)*1.42
  x=math.sin(angle)*r*(.82+.18*j/(rings-1))+.014*math.sin(j*1.2+i)
  z=.08+math.cos(angle)*r
  y=.05*math.sin(i*.6+j*.19)+.04*(x*x)
  points[i,j]=(x,y,z);line.append((x,y,z))
 lines.append((line,[1.4-.9*j/(rings-1)for j in range(rings)]))
for j in range(3,rings):
 for i in range(ribs-1):
  if rng.random()<.13:continue
  a=points[i,j];b=points[i+1,j];mid=tuple((a[k]+b[k])*.5+(rng.uniform(-.012,.012)if k!=2 else rng.uniform(-.018,.018))for k in range(3))
  lines.append(([a,mid,b],[.55,.48,.55]))
  if j<rings-1 and rng.random()<.55:lines.append(([a,points[i+1,j+1]],[.34,.34]))
lines.append(([(0,0,0),(0,0,.25)],[3,1.8]));paths('Reticulated living sea fan',lines,.0075,fanmat)
render('sea-fan',(0,0,.82),2.9,(.1,-5,1.05))
clear();tentacle=material('Anemone living tissue',(.5,.66,.32),.42);bs=tentacle.node_tree.nodes.get('Principled BSDF');bs.inputs['Subsurface Weight'].default_value=.12
n=tentacle.node_tree.nodes;tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.07,.19,.12,1);ramp.color_ramp.elements[1].color=(.95,.78,.51,1)
tentacle.node_tree.links.new(tex.outputs['Generated'],sep.inputs[0]);tentacle.node_tree.links.new(sep.outputs['Z'],ramp.inputs[0]);tentacle.node_tree.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
lines=[]
for i in range(150):
 theta=i*2.39996323;r=.19+.5*math.sqrt((i+.5)/150);h=rng.uniform(.24,.48);points=[];weights=[]
 for j in range(15):
  t=j/14;spread=.12*math.sin(t*math.pi*.75);curl=.09*math.sin(t*math.pi*1.4+i*.19)
  points.append((math.cos(theta)*(r+spread)+math.sin(theta)*curl,math.sin(theta)*(r+spread)-math.cos(theta)*curl,.10+h*t-.045*t*t))
  weights.append(.95-.52*t+.25*math.exp(-((t-.92)/.1)**2))
 lines.append((points,weights))
paths('Individual curved anemone tentacles',lines,.024,tentacle)
rockmat=material('Encrusted anemone rock',(.22,.16,.12),.8);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=(0,0,-.025));rock=bpy.context.object;rock.scale=(.72,.62,.12);rock.data.materials.append(rockmat)
for polygon in rock.data.polygons:polygon.use_smooth=True
bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=24,radius=1,location=(0,0,.09));disc=bpy.context.object;disc.scale=(.35,.3,.045);disc.data.materials.append(tentacle)
for polygon in disc.data.polygons:polygon.use_smooth=True
render('sea-anemone',(0,0,.19),2.05,(0,-4,2.55))
print('Rendered true-geometry fan and anemone',flush=True)
