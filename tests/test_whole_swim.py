"""Continuous body images preserve each column's pixel sequence without cuts."""
import json,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

class WholeSwimChecks(unittest.TestCase):
    def test_complete_curves_preserve_pixels_and_column_topology(self):
        rest=json.loads((ROOT/'assets/source/fish-rest/species.json').read_text())
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        checked=0
        for name,sp in species.items():
            self.assertEqual(sp['bodyRenderMode'],'whole-swim')
            self.assertEqual(sp['poseCount'],3)
            self.assertEqual(sp['bodyAngles'],rest[name]['bodyAngles'])
            self.assertEqual(sp['frameW'],rest[name]['frameW'])
            self.assertEqual(sp['frameH'],rest[name]['frameH'])
            original=Image.open(ROOT/'assets/source/fish-rest'/(name+'.webp')).convert('RGBA')
            atlas=Image.open(ROOT/'roku'/sp['image'][5:]).convert('RGBA')
            visited=set();varied=0
            for yaw,old in enumerate(rest[name]['frames']):
                key=old['x'],old['y']
                if key in visited:continue
                visited.add(key)
                source=np.asarray(original.crop((old['x'],old['y'],old['x']+old['w'],old['y']+old['h'])))
                poses=[]
                for pose in range(3):
                    f=sp['frames'][yaw*3+pose]
                    actual=np.asarray(atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h'])))
                    delta_x=round(old['anchorX']-f['anchorX'])
                    for x in range(source.shape[1]):
                        col=source[:,x];occupied=np.flatnonzero(col[:,3])
                        if not len(occupied):continue
                        a=col[occupied[0]:occupied[-1]+1]
                        candidate=actual[:,x-delta_x];occupied_new=np.flatnonzero(candidate[:,3])
                        self.assertTrue(len(occupied_new),(name,yaw,pose,x))
                        b=candidate[occupied_new[0]:occupied_new[-1]+1]
                        if pose==1:
                            self.assertEqual(occupied[0]-old['anchorY'],occupied_new[0]-f['anchorY'])
                        # Exact alpha topology and every visible color value: no new seam.
                        np.testing.assert_array_equal(a[:,3],b[:,3],err_msg=str((name,yaw,pose,x)))
                        np.testing.assert_array_equal(a[a[:,3]>0],b[b[:,3]>0])
                    poses.append(actual[:,:,3].tobytes())
                    checked+=1
                if len(set(poses))>1:varied+=1
            self.assertGreater(varied,0,'Body must actually form different S poses: '+name)
        self.assertEqual(checked,1710)

    def test_loader_does_not_construct_body_slices(self):
        source=(ROOT/'roku/source/assets.brs').read_text()
        self.assertNotIn('strips.Push',source)
        self.assertNotIn('.bands=',source)
        renderer=(ROOT/'roku/source/renderer.brs').read_text()
        self.assertNotIn('region.bands',renderer)
        self.assertNotIn('strip.centerX',renderer)
