"""Tail binds are anatomical shared mesh vertices, not a generic crop position."""
import json,unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
class TailRigChecks(unittest.TestCase):
    def test_root_is_the_shared_mesh_boundary(self):
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for name,sp in species.items():
            with np.load(ROOT/'assets/source'/(name+'.npz'))as mesh:
                common=np.intersect1d(mesh['body_faces'].ravel(),mesh['tail_faces'].ravel())
                vertices=mesh['vertices'][common].astype(float)
            self.assertGreater(len(common),20)
            np.testing.assert_allclose(sp['tailRig']['body'],vertices.mean(axis=0),atol=1e-7,rtol=0)
            self.assertEqual(len(sp['tailRig']['posesXZ']),sp['tailPoseCount'])
            self.assertLessEqual(sp['tailRig']['overlap'],3)

    def test_tail_stays_below_the_body_without_extra_passes(self):
        source=(ROOT/'roku/source/renderer.brs').read_text()
        self.assertLess(source.index('then ReefDrawBoundTail'),source.index('        ReefDrawWholeBody'))
        block=source[source.index('sub ReefDrawBoundTail'):source.index('sub ReefDrawFishPart')]
        self.assertEqual(block.count('ReefDrawFishRegion('),1)
        self.assertNotIn('sy=sy*warp.sy',block)
