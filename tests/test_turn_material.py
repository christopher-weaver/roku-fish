"""Reference-facing proportions and turn material resources."""
import json,math,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class TurnMaterialChecks(unittest.TestCase):
    def test_copperband_frontal_proportion(self):
        sp=json.loads((ROOT/'roku/scenes/species.json').read_text())['copperband_butterflyfish']
        view=min(range(len(sp['bodyAngles'])),key=lambda i:abs(sp['bodyAngles'][i]-math.pi/2))
        f=sp['frames'][view*sp['poseCount']+1]
        ratio=(f['w']-4)/(f['h']-4)
        self.assertGreaterEqual(ratio,.25,'Frontal copperband must have a rounded face/body, not a paper edge')
        self.assertLessEqual(ratio,.36)
    def test_turn_views_preserve_frontal_detail(self):
        for sp in json.loads((ROOT/'roku/scenes/species.json').read_text()).values():
            values=[a for a in sp['turnViews']['bodyAngles']if math.radians(78.75)-1e-7<=a<=math.radians(101.25)+1e-7]
            self.assertEqual(len(values),25)
            self.assertLessEqual(max(b-a for a,b in zip(values,values[1:])),math.radians(1.40625)+1e-8)
    def test_undercoat_masks_are_small_and_material_colored(self):
        for sp in json.loads((ROOT/'roku/scenes/species.json').read_text()).values():
            self.assertEqual(sp['turnCoreScale'],4)
            self.assertEqual(len(sp['turnCoreFrames']),2*sp['turnViews']['bodyYawCount'])
            im=Image.open(ROOT/'roku'/sp['turnCoreImage'][5:]).convert('RGBA')
            self.assertLess(im.width*im.height,100_000)
            self.assertLessEqual(len(im.getchannel('A').getcolors(256)),32)
            for frame in sp['turnCoreFrames']:
                self.assertGreater(frame['coreWidth'],0)
