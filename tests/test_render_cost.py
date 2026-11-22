"""Prevent empty/full-screen receiver maps from quietly returning."""
import json,sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from formation_frames import footprint
from surface_lighting import conservative_mask
class RenderCostChecks(unittest.TestCase):
 def test_receiver_maps_have_bounds_and_never_cover_open_water(self):
  tank=json.loads((ROOT/'roku/scenes/tank.json').read_text());area=0
  for f in tank['formations']:
   if f.get('animation'):continue
   canvas=Image.new('L',(2048,1152));canvas.paste(footprint(f),(f['x'],f['y']));mask=conservative_mask(np.asarray(canvas))
   if not mask.any():self.assertNotIn('surfaceShadow',f);continue
   c=f['surfaceShadow'];self.assertEqual(c['x']%16,0);self.assertEqual(c['y']%16,0)
   atlas=Image.open(ROOT/'roku'/c['image'][5:]).convert('RGBA')
   area+=2*c['width']*c['height']*c['scale']**2
   for i in range(c['frames']):
    x=i%c['columns']*c['width'];y=i//c['columns']*c['height'];image=Image.new('RGBA',(128,72))
    image.paste(atlas.crop((x,y,x+c['width'],y+c['height'])),(c['x']//16,c['y']//16))
    alpha=np.asarray(image)[:,:,3];self.assertEqual(alpha[~mask].max(),0)
  self.assertLess(area,6_000_000,'Receiver rendering must stay below the former 14 million pixels/frame')
