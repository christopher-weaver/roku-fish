import unittest,json,sys,re,zipfile,tempfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import build
class PackageChecks(unittest.TestCase):
    def test_manifest_and_assets(self):self.assertEqual(build.validate()['species'],6)
    def test_real_screensaver_only(self):
        s='\n'.join(p.read_text()for p in (ROOT/'roku/source').glob('*.brs'))
        self.assertRegex(s,r'sub RunScreenSaver\(');self.assertNotRegex(s,r'(?im)^\s*(sub|function)\s+(Main|RunUserInterface)\s*\(')
    def test_zip_root_and_integrity(self):
        p=ROOT/'dist/deep-reef-screensaver.zip'
        with zipfile.ZipFile(p)as z:
            self.assertIn('manifest',z.namelist());self.assertIsNone(z.testzip())
            self.assertTrue(all(not n.startswith(('roku/','assets/','tests/','tools/'))for n in z.namelist()))
    def test_archive_budget(self):self.assertLessEqual((ROOT/'dist/deep-reef-screensaver.zip').stat().st_size,4_000_000)
    def test_no_lfs_placeholders(self):
        for p in (ROOT/'roku/images').iterdir():self.assertNotIn(b'version https://git-lfs',p.read_bytes()[:150])
    def test_three_swim_poses_and_full_turn(self):
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for sp in species.values():
            self.assertEqual(len(sp['frames']),sp['yawCount']*sp['poseCount'])
            self.assertEqual({f['pose']for f in sp['frames']},set(range(sp['poseCount'])))
            self.assertGreaterEqual(sp['poseCount'],4)
            self.assertEqual(len({f['yaw']for f in sp['frames']}),sp['yawCount'])
            from PIL import Image,ImageChops
            atlas=Image.open(ROOT/'roku'/sp['image'][5:]).convert('RGBA')
            first,second=sp['frames'][:2]
            def crop(f):
                im=Image.new('RGBA',(sp['frameW'],sp['frameH']))
                part=atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']))
                im.alpha_composite(part,(int(sp['frameW']/2-f['anchorX']),int(sp['frameH']/2-f['anchorY'])))
                return im
            self.assertIsNotNone(ImageChops.difference(crop(first),crop(second)).getbbox(), 'Side-view tail poses must visibly differ')
    def test_occlusion_masks_have_alpha(self):
        from PIL import Image
        for name in ['reef-mid.webp','reef-front.webp']:
            im=Image.open(ROOT/'roku/images'/name).convert('RGBA');ext=im.getchannel('A').getextrema();self.assertEqual(ext,(0,255))
    def test_all_textures_within_hardware_limit(self):
        for p in (ROOT/'roku/images').iterdir():
            w,h=build.dimensions(p);self.assertLessEqual(max(w,h),2048)
    def test_corrupt_manifest_rejected(self):
        import shutil
        original=build.ROKU
        with tempfile.TemporaryDirectory() as td:
            copy=Path(td)/'roku';shutil.copytree(original,copy)
            (copy/'manifest').write_text((copy/'manifest').read_text().replace('screensaver_title=Deep Reef','title=Invalid'))
            try:
                build.ROKU=copy
                with self.assertRaisesRegex(ValueError,'screensaver_title'):
                    build.validate()
            finally:build.ROKU=original
    def test_runtime_offline(self):
        source=''.join(p.read_text()for p in (ROOT/'roku/source').glob('*.brs'))
        self.assertNotRegex(source,r'(?i)roUrlTransfer|roVideoPlayer|roAudioPlayer|https?://')
    def test_required_notices_shipped(self):
        with zipfile.ZipFile(ROOT/'dist/deep-reef-screensaver.zip')as z:
            self.assertIn('licenses/ROKU-FISHTANK-MIT.txt',z.namelist())
            self.assertIn('licenses/REEF-GLASS-APACHE-2.0.txt',z.namelist())
    def test_deploy_refuses_missing_configuration(self):
        import os
        env=dict(os.environ);env.pop('ROKU_IP',None);env.pop('ROKU_DEV_PASSWORD',None)
        r=subprocess.run([sys.executable,str(ROOT/'tools/deploy.py')],capture_output=True,text=True,env=env)
        self.assertNotEqual(r.returncode,0);self.assertIn('Set ROKU_IP',r.stderr)
    def test_independent_fin_atlases(self):
        from PIL import Image,ImageChops
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for sp in species.values():
            self.assertEqual(len(sp['finFrames']),sp['yawCount']*sp['finPoseCount'])
            atlas=Image.open(ROOT/'roku'/sp['finImage'][5:]).convert('RGBA')
            poses=[]
            for f in [sp['finFrames'][0],sp['finFrames'][sp['finPoseCount']-1]]:
                self.assertLess(f['w']*f['h'],sp['frameW']*sp['frameH']*.3,'Fin texture must not contain an entire fish')
                self.assertLessEqual(f['x']+f['w'],atlas.width);self.assertLessEqual(f['y']+f['h'],atlas.height)
                im=Image.new('RGBA',(sp['frameW'],sp['frameH']))
                im.alpha_composite(atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h'])),(int(sp['frameW']/2-f['anchorX']),int(sp['frameH']/2-f['anchorY'])))
                poses.append(im)
            self.assertIsNotNone(ImageChops.difference(*poses).getbbox())
    def test_slim_fish_geometry(self):
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for sp in species.values():
            self.assertEqual(sp['bodyHeightFactor'],.92)
            self.assertLessEqual(sp['bodyThickness'],.28)
    def test_settings_rows_have_system_fonts_above_highlight(self):
        import xml.etree.ElementTree as ET
        root=ET.parse(ROOT/'roku/components/ReefSettings.xml').getroot()
        children=root.find('.//Group[@id="layout"]');ids=[node.get('id')for node in children]
        self.assertLess(ids.index('highlight'),ids.index('rows'))
        group=next(node for node in children if node.get('id')=='rows')
        self.assertEqual(len(group.findall('Label')),22)
        for node in group:self.assertTrue(node.get('font','').startswith('font:'))
    def test_wave_assets_and_removed_dapple(self):
        from PIL import Image,ImageChops
        cfg=json.loads((ROOT/'roku/scenes/waves.json').read_text())
        self.assertEqual(cfg['frames'],32)
        for key,name in [('surface','surface-waves.png'),('sand','sand-caustics.png')]:
            data=cfg[key];atlas=Image.open(ROOT/'roku/images'/name).convert('RGBA')
            self.assertEqual(atlas.size,(data['width']*data['columns'],data['height']*((cfg['frames']+data['columns']-1)//data['columns'])))
            def frame(i):
                x=i%data['columns']*data['width'];y=i//data['columns']*data['height']
                return atlas.crop((x,y,x+data['width'],y+data['height']))
            self.assertIsNotNone(ImageChops.difference(frame(0),frame(1)).getbbox())
            self.assertGreater(atlas.getchannel('A').getextrema()[1],40)
        self.assertFalse((ROOT/'roku/images/sun-dapple.png').exists())
        self.assertFalse((ROOT/'roku/scenes/dapple.json').exists())
        with zipfile.ZipFile(ROOT/'dist/deep-reef-screensaver.zip')as z:
            self.assertNotIn('images/sun-dapple.png',z.namelist())
            self.assertNotIn('scenes/dapple.json',z.namelist())
    def test_sand_highlights_stay_on_floor(self):
        from PIL import Image
        atlas=Image.open(ROOT/'roku/images/sand-caustics.png').convert('RGBA')
        # At the distant sand edge the side reefs must remain unlit.
        for frame in range(32):
            x=frame%4*512;y=frame//4*88
            self.assertEqual(atlas.crop((x,y,x+100,y+20)).getchannel('A').getextrema()[1],0)
    def test_frame_wait_precedes_buffer_swap(self):
        source=(ROOT/'roku/source/main.brs').read_text()
        self.assertLess(source.index('Sleep(pacing.sleepMs)'),source.index('screen.SwapBuffers()'))
    def test_fine_per_plane_collision_masks(self):
        occ=json.loads((ROOT/'roku/scenes/occupancy.json').read_text())
        self.assertEqual(occ['cell'],8)
        self.assertEqual([p['z']for p in occ['planes']],[.48,.78])
        for plane in occ['planes']:
            self.assertEqual(len(plane['rows']),144)
            self.assertTrue(all(len(row)==256 for row in plane['rows']))
    def test_surface_atlas_and_larger_bubble(self):
        self.assertEqual(build.dimensions(ROOT/'roku/images/surface-waves.png'),(2048,512))
        self.assertEqual(build.dimensions(ROOT/'roku/images/bubble.png'),(32,32))
if __name__=='__main__':unittest.main()
