import json,sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from formation_frames import footprint
from surface_lighting import field
class ThreeDAndSurfaceChecks(unittest.TestCase):
 def test_reef_objects_are_closed_volumes(self):
  folder=ROOT/'assets/source/reef-model';model=json.loads((folder/'model.json').read_text());groups=set()
  for item in model['objects']:
   groups.add(item['group'])
   with np.load(folder/item['file'])as m:
    v=m['vertices'];f=m['faces'];self.assertGreater(np.ptp(v[:,2]),15)
    if item['closed']:
     edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges.sort(axis=1);keys=edges[:,0].astype('int64')*len(v)+edges[:,1]
     _,counts=np.unique(keys,return_counts=True);self.assertTrue(np.all(counts==2),item['name'])
    else:
     self.assertEqual(item['name'],'hollow-tunnel');self.assertGreater(np.ptp(v[:,2]),75)
     self.assertLess(np.ptp(v[:192,0]),np.ptp(v[-193:-1,0]));self.assertLess(v[:,2].min(),-150)
     edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges.sort(axis=1);unique,counts=np.unique(edges,axis=0,return_counts=True)
     boundary=unique[counts==1];self.assertEqual(len(boundary),192);self.assertTrue(np.all(v[boundary,2]==90))
     self.assertTrue(np.all((counts==1)|(counts==2)))
  self.assertGreaterEqual(len(groups),11);self.assertTrue((folder/'reef-scene.blend').exists())
 def test_eel_is_modeled_and_articulated(self):
  folder=ROOT/'assets/source/eel-model';model=json.loads((folder/'model.json').read_text())
  self.assertFalse(model['uses_portrait_texture']);self.assertTrue(any('jaw'in m['name']for m in model['meshes']))
  self.assertTrue(any('pupil'in m['name']for m in model['meshes']))
  with np.load(folder/'zany-moray.npz')as m:self.assertTrue((np.ptp(m['vertices'],axis=0)>.4).all())
  cfg=json.loads((ROOT/'roku/scenes/eel.json').read_text());image=Image.open(ROOT/'roku'/cfg['image'][5:]).convert('RGBA')
  self.assertEqual(len(cfg['frames']),65);self.assertTrue(cfg['sharedDepthTest'])
  for frame in cfg['frames']:self.assertLessEqual(frame['x']+frame['w'],image.width);self.assertLessEqual(frame['y']+frame['h'],image.height)
  self.assertFalse((ROOT/'roku/images/cave-eel.webp').exists())
  from cave_geometry import animal
  first,_,_,_=animal(0);last,_,_,_=animal(1)
  # The closed rear body ring stays in place while the head crosses the lip.
  self.assertTrue(np.allclose(first[:40],last[:40]))
  self.assertLess(first[1600:,2].max(),0);self.assertGreater(last[1600:,2].max(),150)
  self.assertFalse((ROOT/'roku/images/cave-interior.png').exists())
 def test_no_coral_shadow_can_touch_water(self):
  tank=json.loads((ROOT/'roku/scenes/tank.json').read_text())
  for f in tank['formations']:
   if 'surfaceShadow'not in f:continue
   receiver=Image.new('L',(2048,1152));receiver.paste(footprint(f),(f['x'],f['y']));outside=np.asarray(receiver)<251
   c=f['surfaceShadow'];atlas=Image.open(ROOT/'roku'/c['image'][5:]).convert('RGBA')
   for i in range(32):
    x=i%c['columns']*c['width'];y=i//c['columns']*c['height'];mask=atlas.crop((x,y,x+c['width'],y+c['height'])).getchannel('A').resize((2048,1152),Image.Resampling.BILINEAR)
    self.assertEqual(np.asarray(mask)[outside].max(),0,f['id'])
 def test_soft_shadow_projector_has_floor_perspective(self):
  for y in [300.,970.,1150.]:
   cell=240*(y+180)/1332;x=np.linspace(0,1000,99)
   self.assertTrue(np.allclose(field(x,y,1.25),field(x+cell,y,1.25)))
  self.assertGreater(240*(1150+180)/1332,240*(970+180)/1332)
  profile=field(np.arange(2048),1100.,2.0);self.assertLess(np.abs(np.diff(profile)).max(),10.)
