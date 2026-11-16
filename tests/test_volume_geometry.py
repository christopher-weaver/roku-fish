"""Geometry regressions for visible seams, cave clipping and solid ground."""
import json,sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
class VolumeGeometryChecks(unittest.TestCase):
 def assert_closed(self,v,f):
  edges=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]),axis=1)
  _,counts=np.unique(edges,axis=0,return_counts=True)
  self.assertTrue(np.all(counts==2),'Every edge must join exactly two faces')
 def test_all_fish_have_seamless_closed_shells(self):
  for name in json.loads((ROOT/'roku/scenes/species.json').read_text()):
   with self.subTest(species=name),np.load(ROOT/'assets/source'/(name+'.npz'))as m:
    self.assert_closed(m['vertices'],m['faces']);self.assertTrue(np.isfinite(m['normals']).all())
    self.assertTrue(np.all(np.linalg.norm(m['normals'],axis=1)>.99))
   self.assertEqual(Image.open(ROOT/'assets/source'/(name+'-texture.png')).getchannel('A').getextrema(),(255,255))
 def test_tentacles_branches_and_footings_are_closed_geometry(self):
  for name,folder in [('sea-anemone-sculpted','marine-renders'),('sea-fan-sculpted','marine-renders'),('grounded-footings','reef-model')]:
   with self.subTest(object=name),np.load(ROOT/'assets/source'/folder/(name+'.npz'))as m:
    self.assert_closed(m['vertices'],m['faces']);self.assertGreater(np.ptp(m['vertices'][:,2]),30)
    if 'flow'in m:
     flow=m['flow'];self.assertTrue(np.any(np.linalg.norm(flow,axis=1)<.001));self.assertGreater(np.max(np.linalg.norm(flow,axis=1)),5)
     self.assertGreater(np.ptp(flow[:,2]),3)
 def test_ground_is_a_textured_ridged_depth_surface(self):
  with np.load(ROOT/'assets/source/reef-model/seafloor.npz')as m:
   v=m['vertices'];self.assertGreater(np.ptp(v[:,2]),700);self.assertGreater(len(m['faces']),30000)
   z=(v[:,2]-90)/600+.48;expected=865+205*z+(1-z)*30+36
   self.assertGreater(np.std(v[:,1]-expected),.8);self.assertLess(np.max(np.abs(v[:,1]-expected)),2.01)
   self.assertTrue(np.isfinite(m['uv']).all())
 def test_eel_stays_inside_cave_until_it_emerges(self):
  from cave_geometry import animal,head_pose
  cave=np.load(ROOT/'assets/source/reef-model/hollow-tunnel.npz')['vertices'];n=192
  for pose in np.linspace(0,1,65):
   v,_,_,_=animal(pose)
   self.assertGreaterEqual(v[:,2].min(),-180)
   for ring in range(4):
    hi=cave[ring*n,2];lo=cave[(ring+1)*n,2];points=v[(v[:,2]>=lo)&(v[:,2]<hi)]
    if not len(points):continue
    t=(hi-points[:,2])/(hi-lo);poly=cave[ring*n:(ring+1)*n,:2][None,:,:]*(1-t[:,None,None])+cave[(ring+1)*n:(ring+2)*n,:2][None,:,:]*t[:,None,None]
    a=poly;b=np.roll(poly,-1,axis=1);x=points[:,0,None];y=points[:,1,None];dy=b[:,:,1]-a[:,:,1]
    cross=a[:,:,0]+(b[:,:,0]-a[:,:,0])*(y-a[:,:,1])/np.where(np.abs(dy)>1e-8,dy,1e-8)
    inside=np.count_nonzero(((a[:,:,1]>y)!=(b[:,:,1]>y))&(x<cross),axis=1)%2==1
    self.assertTrue(inside.all(),f'eel intersects cave wall at pose {pose}, ring {ring}')
  self.assertEqual(head_pose(0)[1],head_pose(.6)[1]);self.assertLess(head_pose(1)[1],head_pose(.8)[1])
  final=animal(1)[0][1600:];self.assertGreater(final[:,2].min(),180)
if __name__=='__main__':unittest.main()
