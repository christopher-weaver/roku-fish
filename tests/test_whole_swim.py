"""Mesh flex must be lateral; profile pixels must never bob vertically."""
import json,unittest,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from fish_anatomy import WIDTHS,flex,turn_flex
class WholeSwimChecks(unittest.TestCase):
    def test_lateral_geometry_and_species_proportions(self):
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for name,sp in species.items():
            self.assertEqual(sp['swimAxis'],'lateral')
            with np.load(ROOT/'assets/source'/(name+'.npz')) as mesh:v=mesh['vertices']
            self.assertAlmostEqual(np.ptp(v[:,2])/np.ptp(v[:,0]),WIDTHS[name],places=6)
            a,b=flex(v,-1),flex(v,1)
            np.testing.assert_array_equal(a[:,:2],b[:,:2])
            np.testing.assert_allclose(a[:,2]+b[:,2],2*v[:,2],atol=1e-7)
            self.assertGreater(np.max(np.abs(a[:,2]-b[:,2])),.04)
            atlas=Image.open(ROOT/'roku'/sp['image'][5:]).convert('RGBA')
            for yaw in [0,45,180]:
                index=next(i for i,f in enumerate(sp['frames'][:sp['turnOffset']][::3]) if f['yaw']==yaw)
                masks=[]
                for pose in range(3):
                    f=sp['frames'][index*3+pose];im=Image.new('RGBA',(sp['frameW'],sp['frameH']))
                    piece=atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']))
                    im.alpha_composite(piece,(round(sp['frameW']/2-f['anchorX']),round(sp['frameH']/2-f['anchorY'])))
                    masks.append(np.asarray(im)[:,:,3])
                if yaw==45:
                    self.assertFalse(np.array_equal(masks[0],masks[2]),'Baked oblique mesh must actually flex: '+name)
                else:
                    # Z-only flex cannot move the profile's dorsal/ventral outline.
                    for mask in masks:
                        rows=np.flatnonzero((mask>128).any(axis=1));reference=np.flatnonzero((masks[1]>128).any(axis=1))
                        np.testing.assert_array_equal(rows,reference,err_msg=name)
            self.assertEqual(sp['poseCount'],3)
            # C turns curve to one side, with a stable front and no Y bobbing.
            c=turn_flex(v,1)
            np.testing.assert_array_equal(c[:,:2],v[:,:2])
            self.assertTrue(np.all(c[:,2]>=v[:,2]))
            deflection=np.max(c[:,2]-v[:,2])/np.ptp(v[:,0])
            self.assertGreater(deflection,.035)
            self.assertLess(deflection,.045)
            with np.load(ROOT/'assets/source'/(name+'.npz')) as mesh:
                self.assertGreater(len(mesh['eye_faces']),1000)
                self.assertTrue(np.any(mesh['eye_vertices'][:,2]>0))
                self.assertTrue(np.any(mesh['eye_vertices'][:,2]<0))

    def test_loader_does_not_construct_body_slices(self):
        source=(ROOT/'roku/source/assets.brs').read_text()
        self.assertNotIn('strips.Push',source)
        self.assertNotIn('.bands=',source)
        renderer=(ROOT/'roku/source/renderer.brs').read_text()
        self.assertNotIn('region.bands',renderer)
        self.assertNotIn('strip.centerX',renderer)
