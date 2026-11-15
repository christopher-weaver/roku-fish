"""Shared offline readers for immutable static and whole-pose formation atlases."""
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def frame(formation,index,cache=None):
 cache={}if cache is None else cache
 if 'animation'in formation:
  cfg=formation['animation'];page=index//cfg['framesPerPage'];local=index%cfg['framesPerPage'];path=formation['images'][page];x=cfg['gutter']+local%formation['columns']*cfg['strideX'];y=cfg['gutter']+local//formation['columns']*cfg['strideY']
 else:
  path=formation['image'];x=index%formation['columns']*formation['frameWidth'];y=index//formation['columns']*formation['frameHeight']
 if path not in cache:cache[path]=Image.open(ROOT/'roku'/path[5:]).convert('RGBA')
 return cache[path].crop((x,y,x+formation['frameWidth'],y+formation['frameHeight']))
def footprint(formation):
 if 'animation'in formation:
  return Image.open(ROOT/'assets/source/marine-renders'/(formation['id']+'-motion-footprint.png')).convert('L')
 cache={};alpha=np.zeros((formation['height'],formation['width']),dtype=np.uint8)
 for i in range(formation['frames']):
  im=frame(formation,i,cache).resize((formation['width'],formation['height']),Image.Resampling.LANCZOS)
  alpha=np.maximum(alpha,np.asarray(im.getchannel('A')))
 return Image.fromarray(alpha)
def reserve_navigation():
 import json
 from scipy.ndimage import maximum_filter
 import scene
 p=ROOT/'roku/scenes/occupancy.json';tank=json.loads((ROOT/'roku/scenes/tank.json').read_text());planes=[];union=np.zeros((144,256),dtype=bool)
 for f in tank['formations']:
  canvas=Image.new('L',(2048,1152));canvas.paste(footprint(f),(f['x'],f['y']));alpha=np.asarray(canvas)
  grid=(alpha.reshape(144,8,256,8)>31).any(axis=(1,3))
  if 'animation'in f:grid=maximum_filter(grid,size=3)
  union|=grid;planes.append(dict(id=f['id'],z=f['z'],halfDepth=f['halfDepth'],parallax=f['parallax'],rows=[''.join('#'if v else'.'for v in row)for row in grid]))
 occ={'cell':8,'rows':[''.join('#'if v else'.'for v in row)for row in union],'planes':planes};p.write_text(json.dumps(occ,separators=(',',':')));scene.build_navigation(occ)
if __name__=='__main__':reserve_navigation()
