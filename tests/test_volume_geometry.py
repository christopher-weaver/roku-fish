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
  for name,folder in [('clam-sculpted','marine-renders'),('sea-anemone-sculpted','marine-renders'),('grounded-footings','reef-model')]:
   with self.subTest(object=name),np.load(ROOT/'assets/source'/folder/(name+'.npz'))as m:
    self.assert_closed(m['vertices'],m['faces']);self.assertGreater(np.ptp(m['vertices'][:,2]),30)
    if name=='sea-anemone-sculpted':
     flow=m['flow'];self.assertTrue(np.any(np.linalg.norm(flow,axis=1)<.001));self.assertGreater(np.max(np.linalg.norm(flow,axis=1)),5)
     self.assertGreater(np.ptp(flow[:,2]),3)
 def test_reference_anemone_has_fewer_plumper_tentacles(self):
  from scipy.sparse import coo_matrix
  from scipy.sparse.csgraph import connected_components
  with np.load(ROOT/'assets/source/marine-renders/sea-anemone-sculpted.npz')as m:
   v=m['vertices'];f=m['faces'];a=np.concatenate([f[:,0],f[:,1],f[:,2]]);b=np.concatenate([f[:,1],f[:,2],f[:,0]])
   graph=coo_matrix((np.ones(len(a)),(a,b)),shape=(len(v),len(v))).tocsr();count,labels=connected_components(graph,directed=False)
   self.assertEqual(count-1,64)
   body=np.argmax(np.bincount(labels))
   for component in range(count):
    if component==body:continue
    root=v[labels==component][:18]
    diameter=np.linalg.norm(root[:,None,:]-root[None,:,:],axis=2).max()
    self.assertGreater(diameter,10);self.assertLess(diameter,15.5)
 def test_anemone_is_slightly_translucent_and_surface_stays_above_fish(self):
  cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());f=next(f for f in cfg['formations']if f['id']=='sea-anemone')
  alpha=np.asarray(Image.open(ROOT/'roku'/f['image'][5:]).convert('RGBA'))[:,:,3]
  tissue=alpha[(alpha>=198)&(alpha<=210)];self.assertGreater(len(tissue),1000);self.assertAlmostEqual(float(np.median(tissue)),204,delta=2)
  with np.load(ROOT/'assets/source/marine-renders/sea-anemone-sculpted.npz')as mesh:
   self.assertGreater(np.mean(np.isclose(mesh['opacity'],.8)),.9)
  waves=np.asarray(Image.open(ROOT/'roku/images/surface-waves.png').convert('RGBA'))[:,:,3]
  for row in range(4):self.assertEqual(waves[row*128+57:(row+1)*128].max(),0)
  self.assertGreater(cfg['waterline']['clearanceY'],cfg['waterline']['maxWaveY'])
  self.assertEqual(cfg['waterline']['maxWaveY'],96)
  waves_cfg=json.loads((ROOT/'roku/scenes/waves.json').read_text());self.assertEqual(waves_cfg['surface']['scale'],4);self.assertEqual(waves_cfg['surface']['scaleY'],2)
 def test_clam_side_view_texture_and_interior_occlusion(self):
  from formation_frames import front_frame,frame
  cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());f=next(f for f in cfg['formations']if f['id']=='clam')
  self.assertEqual(f['yawDegrees'],-55);self.assertLess(f['width'],240)
  self.assertEqual(len(f['frontRects']),65)
  x=int((1085-f['x'])*f['frameWidth']/f['width']);y=int((1007-f['y'])*f['frameHeight']/f['height']);a=np.asarray(front_frame(f,0))[:,:,3]
  self.assertGreater(a[y-8:y+8,x-14:x+14].mean(),245)
  partial=np.asarray(front_frame(f,24))[:,:,3];self.assertLess(partial[y-8:y+8,x-14:x+14].mean(),100,'Contents must be revealed before full opening')
  lining=np.asarray(frame(f,64))[:,:,:3];self.assertGreater(lining[y-8:y+8,x-14:x+14].mean(),70,'Interior must have a visible mantle, not a black hole')
  self.assertLess(f['x']+f['width'],1220-20)
  import preview
  closed=Image.new('RGBA',(1920,1080));closed.alpha_composite(front_frame(f,0),(f['x'],f['y']-36));covered=np.asarray(closed)[:,:,3]>220
  for name,sp in preview.SPEC.items():
   baby=dict(name=name,x=1085,y=970,z=.97,sx=1085,sy=970.9,scale=.991,size=min(.27,48/sp['length']),heading=.36,pitch=0,phase=0,finPhase=.4)
   canvas=Image.new('RGBA',(1920,1080));preview.fish(canvas,baby,'Sunset',0);pixels=np.asarray(canvas)[:,:,3]>100
   self.assertFalse(np.any(pixels&~covered),name+' must already fit behind the closed shell')
  for name in ['anemone-material.png','clam-material.png']:
   material=np.asarray(Image.open(ROOT/'assets/source/marine-renders'/name).convert('RGB'));self.assertGreater(material.std(),25)
 def test_complete_anemone_stands_on_sandy_rock_platform(self):
  cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());plant=next(f for f in cfg['formations']if f['id']=='sea-anemone');platform=next(f for f in cfg['formations']if f['id']=='anemone-platform')
  self.assertLess(platform['z'],plant['z'],'Support must draw behind the complete base')
  self.assertFalse(any(f['id']=='anemone-rim'for f in cfg['formations']))
  self.assertTrue(cfg['anemonePlatform']['fullBase']);self.assertTrue(cfg['anemonePlatform']['sandApron'])
  with np.load(ROOT/'assets/source/marine-renders/sea-anemone-sculpted.npz')as m:
   v=m['vertices'][:1760];self.assertGreater(v[:,1].max(),1018,'Full pedal column must be restored')
   self.assert_closed(m['vertices'],m['faces'])
  with np.load(ROOT/'assets/source/reef-model/anemone-platform.npz')as m:
   self.assert_closed(m['vertices'],m['faces']);self.assertGreater(np.ptp(m['vertices'][:,0]),400);self.assertGreater(np.ptp(m['vertices'][:,2]),50)
  pixels=np.asarray(Image.open(ROOT/'roku/images/reef-anemone-platform.webp').convert('RGBA'));self.assertTrue(((pixels[:,:,3]>0)&(pixels[:,:,3]<240)).any(),'Sand apron must feather into seabed')
 def test_approved_fan_is_restored_exactly(self):
  approved=ROOT/'assets/source/marine-renders/approved-fan'
  self.assertEqual((approved/'atlas.webp').read_bytes(),(ROOT/'roku/images/reef-sea-fan-motion-0.webp').read_bytes())
  self.assertFalse((ROOT/'roku/images/reef-sea-fan-motion-1.webp').exists())
  cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());f=next(f for f in cfg['formations']if f['id']=='sea-fan')
  self.assertEqual(f,json.loads((approved/'formation.json').read_text()))
 def test_eel_expressions_are_geometry_and_not_constant(self):
  from cave_geometry import animal,expression,expression_frame
  neutral=animal(1)[0];gape=animal(1,mouth=1)[0];funny=animal(1,funny=1)[0]
  self.assertTrue(np.array_equal(neutral[:1600],gape[:1600]));self.assertGreater(np.linalg.norm(neutral-gape,axis=1).max(),8)
  self.assertGreater(np.linalg.norm(neutral-funny,axis=1).max(),2)
  actions=[expression(t/60)for t in range(3720)]
  self.assertGreater(sum(m>.5 for m,f in actions),20);self.assertGreater(sum(f>.5 for m,f in actions),20)
  self.assertGreater(sum(m==0 and f==0 for m,f in actions),3000)
  self.assertEqual(expression_frame(.7,1),80);self.assertEqual(expression_frame(3.4,1),96)
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
