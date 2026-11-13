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
            self.assertEqual(len(sp['frames']),48)
            self.assertEqual({f['pose']for f in sp['frames']},{0,1,2})
            self.assertEqual(len({f['yaw']for f in sp['frames']}),16)
            from PIL import Image,ImageChops
            atlas=Image.open(ROOT/'roku'/sp['image'][5:]).convert('RGBA')
            first,second=sp['frames'][:2]
            def crop(f):return atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']))
            self.assertIsNotNone(ImageChops.difference(crop(first),crop(second)).getbbox(), 'Side-view tail poses must visibly differ')
    def test_occlusion_masks_have_alpha(self):
        from PIL import Image
        for name in ['reef-mid.png','reef-front.png']:
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
if __name__=='__main__':unittest.main()
