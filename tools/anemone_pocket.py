"""A modeled live-rock pocket with its front/side rim above the anemone base."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
import moderngl
from living_reef import Model,save,VS,FS
ROOT=Path(__file__).resolve().parents[1]
def build():
 folder=ROOT/'assets/source/reef-model';cfgpath=ROOT/'roku/scenes/tank.json';cfg=json.loads(cfgpath.read_text())
 angle=np.linspace(0,np.pi,145);path=np.column_stack([1474+120*np.cos(angle),950+23*np.sin(angle),285+20*np.sin(angle)])
 radius=12+4*np.sin(angle)**2+2*np.sin(angle*7)
 model=Model();model.tube(path,radius,(.54,.40,.36),sides=24)
 v,n,f,rgb,flow=save('anemone-pocket-rim',model,folder)
 source=np.asarray(Image.open(folder/'reef-projection.png').convert('RGBA'));valid=source[:,:,3]>230
 _,indices=distance_transform_edt(~valid,return_indices=True);color=Image.fromarray(source[indices[0],indices[1],:3]);color.save(folder/'anemone-pocket-rim-colour.png')
 ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST);p=ctx.program(vertex_shader=VS,fragment_shader=FS);p['stage'].value=(0,0,2048,1152);p['strength'].value=0;p['usePhoto'].value=1;p['tissue'].value=0
 texture=ctx.texture(color.size,3,color.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());texture.filter=(moderngl.LINEAR,moderngl.LINEAR);texture.use()
 vb=ctx.buffer(np.column_stack([v,n,rgb,flow]).astype('f4').tobytes());ib=ctx.buffer(f.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 3f 3f 3f','position','normal','rgb','flow')],ib);fb=ctx.simple_framebuffer((2048,1152),components=4);fb.use();fb.clear(0,0,0,0,depth=1);vao.render();im=Image.frombytes('RGBA',fb.size,fb.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM);matched=Image.new('RGBA',(2048,1152));
 for reef in cfg['formations']:
  if reef['id']in ['connected-reef','foreground-reef']:matched.alpha_composite(Image.open(ROOT/'roku'/reef['image'].replace('pkg:/','')).convert('RGBA'),(reef['x'],reef['y']))
 match=np.asarray(matched);pixels=np.asarray(im).copy();pixels[:,:,:3]=np.where((match[:,:,3]>200)[:,:,None],match[:,:,:3],source[:,:,:3]);pixels[:,:,3]=np.minimum(pixels[:,:,3],source[:,:,3]);im=Image.fromarray(pixels);box=im.getchannel('A').getbbox();im=im.crop(box);im.save(ROOT/'roku/images/reef-anemone-rim.webp',quality=85,method=6,exact=True)
 formation=dict(id='anemone-rim',image='pkg:/images/reef-anemone-rim.webp',x=box[0],y=box[1],width=im.width,height=im.height,frameWidth=im.width,frameHeight=im.height,frames=1,columns=1,z=.80,halfDepth=.028,parallax=1,renderedMesh=True,meshVertices=len(v),meshTriangles=len(f),meshObjects=['anemone-pocket-rim'])
 cfg['formations']=[f for f in cfg['formations']if f['id']!='anemone-rim']+[formation];cfg['formations'].sort(key=lambda f:f['z']);cfg['occlusionDepths']=[f['z']for f in cfg['formations']];cfg['anemonePocket']={'x':1474,'y':970,'width':220,'height':124,'recessDepth':55,'frontRim':'anemone-rim'};cfgpath.write_text(json.dumps(cfg,indent=2)+'\n')
 p=folder/'model.json';record=json.loads(p.read_text());record['objects']=[o for o in record['objects']if o['name']!='anemone-pocket-rim'];record['objects'].append(dict(name='anemone-pocket-rim',group='anemone-pocket-rim',layer='anemone-rim',file='anemone-pocket-rim.npz',vertices=len(v),triangles=len(f),closed=True,sculpted=True));p.write_text(json.dumps(record,indent=2)+'\n')
 print('Recessed anemone pocket and shared live-rock rim:',im.size,flush=True)
if __name__=='__main__':build()
