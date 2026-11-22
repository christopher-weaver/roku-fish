"""Photo-derived tissue and shell maps, shared by the mesh and Blender source."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[1]
def patch(image,box,size):
 im=image.crop(box).convert('RGBA');a=np.asarray(im);valid=a[:,:,3]>220
 _,indices=distance_transform_edt(~valid,return_indices=True)
 rgb=a[indices[0],indices[1],:3];return Image.fromarray(rgb).resize(size,Image.Resampling.LANCZOS)
def build():
 folder=ROOT/'assets/source/marine-renders'
 an=Image.open(folder/'sea-anemone-finished.png')
 # Genuine wrinkles, translucency and fine tissue grain from the approved art.
 oral=patch(an,(230,430,640,700),(512,512));tissue=patch(an,(330,160,600,510),(512,512))
 # The pedal column occupies the left UV tile. Its lower rows in model space
 # map to the top of this image (the upload flips the photo vertically).
 # Bake a soft static grounding gradient into tissue, leaving fingers unchanged.
 world_y=850+155*(1-np.linspace(0,1,512))
 foot=np.clip((world_y-965)/40,0,1);foot=foot*foot*(3-2*foot)
 oral=Image.fromarray(np.uint8(np.asarray(oral).astype(float)*(1-.45*foot[:,None,None])))
 atlas=Image.new('RGB',(1024,512));atlas.paste(oral);atlas.paste(tissue,(512,0));atlas.save(folder/'anemone-material.png',optimize=True)
 clam=Image.open(ROOT/'assets/source/coral-islands/central-clam.png')
 shell=patch(clam,(72,105,416,330),(512,512));mantle=patch(clam,(160,130,395,305),(512,512))
 atlas=Image.new('RGB',(1024,512));atlas.paste(shell);atlas.paste(mantle,(512,0));atlas.save(folder/'clam-material.png',optimize=True)
 return folder
VS='''#version 330
in vec3 position;in vec3 normal;in vec3 rgb;in vec3 flow;in vec2 surfaceUV;in float opacity;
uniform vec4 stage;uniform float strength;out vec3 n;out vec3 color;out vec3 world;out vec2 texuv;out float alphaMaterial;
void main(){vec3 p=position+flow*strength;gl_Position=vec4((p.x-stage.x)/stage.z*2-1,1-(p.y-stage.y)/stage.w*2,-p.z/500.0,1);n=normal;color=rgb;world=p;texuv=surfaceUV;alphaMaterial=opacity;}
'''
FS='''#version 330
uniform sampler2D photo;uniform float clipDepth;uniform float edgeDarkening;in vec3 n;in vec3 color;in vec3 world;in vec2 texuv;in float alphaMaterial;out vec4 outcol;
void main(){if(world.z<clipDepth)discard;vec3 normal=normalize(n);vec3 base=texture(photo,texuv).rgb;
vec2 step=vec2(1.0/1024.0,1.0/512.0);float bx=dot(texture(photo,texuv+vec2(step.x,0)).rgb-texture(photo,texuv-vec2(step.x,0)).rgb,vec3(.2126,.7152,.0722));float by=dot(texture(photo,texuv+vec2(0,step.y)).rgb-texture(photo,texuv-vec2(0,step.y)).rgb,vec3(.2126,.7152,.0722));normal=normalize(normal+vec3(-bx,-by,0)*.55);
vec3 light=normalize(vec3(-.35,-.7,1));float diffuse=max(0.0,dot(normal,light));float sheen=pow(max(0.0,dot(normal,normalize(light+vec3(0,0,1)))),38.0)*.035;
float edge=1.0-edgeDarkening*(alphaMaterial>.99?1.0:.25)*pow(max(0.0,1.0-abs(normalize(n).z)),1.2);
base=mix(base,color,.13);outcol=vec4((base*(.78+.22*diffuse)+sheen)*edge,alphaMaterial);}
'''
