import unittest,json,sys,re,zipfile,tempfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import build
class PackageChecks(unittest.TestCase):
    def test_manifest_and_assets(self):self.assertEqual(build.validate()['species'],10)
    def test_real_screensaver_only(self):
        s='\n'.join(p.read_text()for p in (ROOT/'roku/source').glob('*.brs'))
        self.assertRegex(s,r'sub RunScreenSaver\(');self.assertNotRegex(s,r'(?im)^\s*(sub|function)\s+(Main|RunUserInterface)\s*\(')
    def test_zip_root_and_integrity(self):
        p=ROOT/'dist/deep-reef-screensaver.zip'
        with zipfile.ZipFile(p)as z:
            self.assertIn('manifest',z.namelist());self.assertIsNone(z.testzip())
            self.assertTrue(all(not n.startswith(('roku/','assets/','tests/','tools/'))for n in z.namelist()))
    def test_archive_budget(self):self.assertLessEqual((ROOT/'dist/deep-reef-screensaver.zip').stat().st_size,4*1024*1024)
    def test_no_lfs_placeholders(self):
        for p in (ROOT/'roku/images').iterdir():self.assertNotIn(b'version https://git-lfs',p.read_bytes()[:150])
    def test_independent_tail_poses_and_full_turn(self):
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for sp in species.values():
            self.assertEqual(sp['turnOffset'],sp['bodyYawCount']*sp['poseCount'])
            self.assertEqual(len(sp['frames']),sp['turnOffset']+sp['turnViews']['bodyYawCount']*2)
            self.assertEqual({f['pose']for f in sp['frames']},set(range(sp['poseCount'])))
            self.assertEqual(sp['poseCount'],3)
            self.assertEqual(sp['bodyRenderMode'],'whole-swim')
            self.assertGreaterEqual(sp['tailPoseCount'],4)
            self.assertEqual(len({f['yaw']for f in sp['frames'][:sp['turnOffset']]}),sp.get('bodyYawCount',sp['yawCount']))
            from PIL import Image,ImageChops
            atlas=Image.open(ROOT/'roku'/sp['tailImage'][5:]).convert('RGBA')
            first,second=sp['tailFrames'][8*sp['tailPoseCount']],sp['tailFrames'][9*sp['tailPoseCount']-1]
            def crop(f):
                im=Image.new('RGBA',(sp['frameW'],sp['frameH']))
                part=atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']))
                im.alpha_composite(part,(int(sp['frameW']/2-f['anchorX']),int(sp['frameH']/2-f['anchorY'])))
                return im
            self.assertIsNotNone(ImageChops.difference(crop(first),crop(second)).getbbox(), 'Three-quarter tail deflections must visibly differ')
    def test_tail_geometry_partition_and_model_detail(self):
        import numpy as np
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for name,sp in species.items():
            with np.load(ROOT/'assets/source'/(name+'.npz'))as mesh:
                body={tuple(f)for f in mesh['body_faces']};tail={tuple(f)for f in mesh['tail_faces']}
                self.assertFalse(body & tail,'Caudal tail must not appear in the body image')
                self.assertEqual(len(body)+len(tail),len(mesh['faces']))
                self.assertGreater(len(tail),100)
                self.assertGreater(len(mesh['vertices']),20000)
                self.assertTrue(np.isfinite(mesh['normals']).all())
                self.assertEqual(sp['meshRevision'],5)
                self.assertGreaterEqual(sp['frameW'],224)
    def test_sparse_roster_and_shadow_mask(self):
        from PIL import Image
        import numpy as np
        from waves import sand_mask
        cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text())
        self.assertEqual(cfg['populations'],{'Low':6,'Medium':8,'High':10})
        self.assertEqual(len(set(cfg['speciesOrder'])),10)
        waves=json.loads((ROOT/'roku/scenes/waves.json').read_text());c=waves['shadow']
        atlas=np.asarray(Image.open(ROOT/'roku/images/sand-wave-shadows.png').convert('RGBA'))
        self.assertGreater(atlas[:,:,3].max(),50);self.assertLessEqual(atlas[:,:,3].max(),96)
        ground=np.asarray(sand_mask().crop((0,960,2048,1152)).resize((256,24),Image.Resampling.LANCZOS))
        for i in range(waves['frames']):
            x=i%c['columns']*c['width'];y=i//c['columns']*c['height']
            self.assertLessEqual(atlas[y:y+24,x:x+256,3][ground==0].max(),3)
    def test_dense_frontal_angles_and_pinned_marine_rigs(self):
        import math
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for sp in species.values():
            angles=sp['bodyAngles'];self.assertEqual(angles,sorted(set(angles)))
            self.assertEqual(sp['bodyYawCount'],64)
            frontal=[a for a in angles if math.radians(78.75)-1e-7<=a<=math.radians(101.25)+1e-7]
            self.assertEqual(len(frontal),25)
            self.assertLessEqual(max(b-a for a,b in zip(frontal,frontal[1:])),math.radians(1.40625)+1e-8)
        tank=json.loads((ROOT/'roku/scenes/tank.json').read_text())
        self.assertEqual({f['id']for f in tank['formations']if 'animation'in f},{'sea-fan','sea-anemone','clam'})
    def test_coherent_marine_frames_and_cave_net(self):
        from PIL import Image,ImageChops
        from formation_frames import frame
        tank=json.loads((ROOT/'roku/scenes/tank.json').read_text())
        for f in tank['formations']:
            if 'animation'in f:
                self.assertEqual(f['animation']['count'],65)
                self.assertIsNotNone(ImageChops.difference(frame(f,0),frame(f,64)).getbbox())
        runtime=(ROOT/'roku/source/renderer.brs').read_text()
        self.assertNotIn('ReefMarineBand',runtime)
        self.assertNotIn('marineBands',runtime)
        eel=json.loads((ROOT/'roku/scenes/eel.json').read_text());self.assertEqual(eel['emergenceCount'],65);self.assertEqual(eel['count'],97)
        self.assertFalse((ROOT/'roku/images/wave-net.webp').exists())
        self.assertTrue(all(f['renderedMesh']for f in tank['formations']))
        self.assertEqual(tank['camera']['Slow']['period'],180)
    def test_occlusion_masks_have_alpha(self):
        from PIL import Image
        for formation in json.loads((ROOT/'roku/scenes/tank.json').read_text())['formations']:
            im=Image.open(ROOT/'roku'/formation['image'][5:]).convert('RGBA');ext=im.getchannel('A').getextrema();self.assertEqual(ext[0],0);self.assertGreaterEqual(ext[1],230)
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
            # Anatomy remains slim; collision depth also reserves the larger
            # S/C sweep and must not be capped at the old resting-body value.
            self.assertLessEqual(sp['modelWidthRatio'],.20)
            self.assertGreaterEqual(sp['bodyThickness'],sp['modelWidthRatio'])
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
        for key,name in [('surface','surface-waves.png'),('sand','sand-caustics.png'),('shadow','sand-wave-shadows.png')]:
            data=cfg[key];atlas=Image.open(ROOT/'roku/images'/name).convert('RGBA')
            self.assertEqual(atlas.size,(data['width']*data['columns'],data['height']*((cfg['frames']+data['columns']-1)//data['columns'])))
            def frame(i):
                x=i%data['columns']*data['width'];y=i//data['columns']*data['height']
                return atlas.crop((x,y,x+data['width'],y+data['height']))
            self.assertIsNotNone(ImageChops.difference(frame(0),frame(1)).getbbox())
            self.assertGreater(atlas.getchannel('A').getextrema()[1],10 if key=='sand' else 40)
            if key=='sand':self.assertLessEqual(atlas.getchannel('A').getextrema()[1],48)
        self.assertFalse((ROOT/'roku/images/sun-dapple.png').exists())
        self.assertFalse((ROOT/'roku/scenes/dapple.json').exists())
        with zipfile.ZipFile(ROOT/'dist/deep-reef-screensaver.zip')as z:
            self.assertNotIn('images/sun-dapple.png',z.namelist())
            self.assertNotIn('scenes/dapple.json',z.namelist())
    def test_sand_highlights_stay_on_floor(self):
        from PIL import Image
        atlas=Image.open(ROOT/'roku/images/sand-caustics.png').convert('RGBA')
        cfg=json.loads((ROOT/'roku/scenes/waves.json').read_text())['sand']
        # Sand illumination starts near the floor; it cannot cover the upper reef.
        self.assertGreaterEqual(cfg['y'],950)
        self.assertEqual(cfg['width']*cfg['scale'],2048)
        self.assertEqual(cfg['height']*cfg['scale'],192)
        self.assertLessEqual(atlas.getchannel('A').getextrema()[1],48)
    def test_reference_composition_and_detail(self):
        from PIL import Image
        mask=Image.open(ROOT/'docs/previews/reef-mask.png').convert('L')
        center=mask.crop((350,200,680,480))
        import statistics
        self.assertGreater(statistics.mean(center.getdata()),50)
        self.assertGreater(statistics.mean(center.getdata()),100,'Reference reef must fill its connected middle')
        cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text())
        for layer in cfg['formations']:
            from formation_frames import frame
            for i in range(layer['frames']):self.assertEqual(frame(layer,i).size,(layer['frameWidth'],layer['frameHeight']))
            self.assertLessEqual(layer['x']+layer['width'],2048)
            self.assertLessEqual(layer['y']+layer['height'],1152)
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        self.assertGreaterEqual(species['emperor_angelfish']['length'],300)
        self.assertGreaterEqual(species['yellow_tang']['frameW'],224)
        self.assertTrue(all(sp['frameW']>192 for sp in species.values()))
    def test_sand_grain_is_preserved(self):
        from PIL import Image,ImageChops,ImageFilter,ImageStat
        source=Image.open(ROOT/'assets/source/background-matched-sunset.png').convert('RGB').resize((2048,1152),Image.Resampling.LANCZOS)
        actual=Image.new('RGBA',(2048,1152));actual.alpha_composite(Image.open(ROOT/'roku/images/seafloor-sunset.webp').convert('RGBA'),(0,920));actual=actual.convert('RGB')
        box=(256,1040,1792,1110)
        def grain(im):
            crop=im.crop(box).convert('L')
            return ImageStat.Stat(ImageChops.difference(crop,crop.filter(ImageFilter.GaussianBlur(1.5)))).mean[0]
        self.assertGreater(grain(actual),grain(source)*.55)
    def test_frame_wait_precedes_buffer_swap(self):
        source=(ROOT/'roku/source/main.brs').read_text()
        self.assertLess(source.index('Sleep(pacing.sleepMs)'),source.index('screen.SwapBuffers()'))
    def test_fine_per_plane_collision_masks(self):
        occ=json.loads((ROOT/'roku/scenes/occupancy.json').read_text())
        self.assertEqual(occ['cell'],8)
        self.assertEqual(len(occ['planes']),7)
        cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text())
        self.assertEqual([(p['id'],p['z'],p['parallax'])for p in occ['planes'] if p['id']!='grounded-rock-base'],[(p['id'],p['z'],p['parallax'])for p in cfg['formations']])
        for plane in occ['planes']:
            self.assertEqual(len(plane['rows']),144)
            self.assertTrue(all(len(row)==256 for row in plane['rows']))
    def test_connected_reef_navigation(self):
        nodes=json.loads((ROOT/'roku/scenes/navigation.json').read_text())['nodes']
        seen={0};queue=[0]
        for i in queue:
            for j in nodes[i]['edges']:
                self.assertIn(i,nodes[j]['edges'])
                if j not in seen:seen.add(j);queue.append(j)
        self.assertEqual(len(seen),len(nodes))
        self.assertTrue(any(n['z']<.2 and n['y']>600 for n in nodes))
        self.assertTrue(any(n['z']>.9 and n['y']>600 for n in nodes))
        self.assertTrue(any(.3<n['z']<.8 and n['y']<250 for n in nodes))
    def test_all_turn_views_are_baked_upright(self):
        species=json.loads((ROOT/'roku/scenes/species.json').read_text())
        for sp in species.values():
            self.assertEqual(sp['yawCount'],64)
            self.assertEqual(len(sp['viewWidths']),64)
            self.assertFalse(any(f['flipX']for f in sp['frames']))
            for pose in range(sp['poseCount']):
                count=sp['bodyYawCount']//2+1 if pose==1 else sp['bodyYawCount']
                self.assertEqual(len({(f['x'],f['y'])for f in sp['frames'][:sp['turnOffset']][pose::sp['poseCount']]}),count)
            self.assertEqual(sp['poseCount'],3)
            self.assertEqual(sp['bodyRenderMode'],'whole-swim')
            self.assertEqual(sp['tailPoseCount'],4)
            self.assertEqual(sp['finPoseCount'],5)
    def test_precomputed_routes_and_coral_renders(self):
        nav=json.loads((ROOT/'roku/scenes/navigation.json').read_text());nodes=nav['nodes']
        self.assertEqual(len(nav['nextHop']),len(nodes))
        for start in range(len(nodes)):
            for goal in range(len(nodes)):
                hop=nav['nextHop'][start][goal]
                self.assertTrue(hop==start==goal or hop in nodes[start]['edges'])
        cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text())
        self.assertTrue(all(f['renderedMesh']for f in cfg['formations']))
        for f in cfg['formations']:
            self.assertEqual(f['frames'],65 if 'animation'in f else 1)
            if 'animation'in f:
                self.assertGreater(f['meshVertices'],10000)
                mesh_path=ROOT/'assets/source/marine-renders'/(f['id']+'-volume.npz')
                self.assertTrue(mesh_path.exists())
                import numpy as np
                with np.load(mesh_path)as mesh:
                    self.assertEqual(len(mesh['vertices']),f['meshVertices'])
                    self.assertGreater(np.ptp(mesh['vertices'][:,2]),.05,'Marine mesh must have real depth')
    def test_connected_foundation_and_common_baseline(self):
        from PIL import Image
        import numpy as np
        cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text())
        union=np.zeros((1152,2048),dtype=np.uint8)
        for f in cfg['formations']:
            from formation_frames import footprint as formation_footprint
            footprint=formation_footprint(f)
            canvas=Image.new('L',(2048,1152));canvas.paste(footprint,(f['x'],f['y']))
            union=np.maximum(union,np.asarray(canvas))
            if 'animation'in f:self.assertLessEqual(abs(f.get('rootY',f['y']+f['height'])-cfg['baseline']),cfg['baselineTolerance'])
            self.assertEqual(f['parallax'],1)
            self.assertEqual(footprint.size,(f['width'],f['height']))
        # Every interior column intersects the touching low rock foundation.
        self.assertTrue((union[995:1056,32:2000]>32).any(axis=0).all())
        from scipy.ndimage import label
        components,_=label(union>32);sizes=np.bincount(components.ravel())[1:]
        self.assertGreater(sizes.max()/sizes.sum(),.995,'Reef pieces must touch as one dominant assemblage')
    def test_surface_atlas_and_larger_bubble(self):
        self.assertEqual(build.dimensions(ROOT/'roku/images/surface-waves.png'),(2048,512))
        self.assertEqual(build.dimensions(ROOT/'roku/images/bubble.png'),(32,32))
if __name__=='__main__':unittest.main()
