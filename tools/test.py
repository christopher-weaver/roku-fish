"""Run structural tests plus direct production BrightScript tests. Fail on interpreter diagnostics."""
from pathlib import Path
import os,subprocess,sys,shutil,re
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['math','camera','aquarium','fish','schooling','effects']
def binary(name):
    env=os.environ.get(name.upper()+'_BIN')
    if env:return env
    local=ROOT/'node_modules/.bin'/name
    if local.exists():return str(local)
    found=shutil.which(name)
    if found:return found
    raise RuntimeError(f'{name} unavailable: run npm install or set {name.upper()}_BIN')
def brs_run(test,log):
    work=ROOT/'work';work.mkdir(exist_ok=True)
    settings=(ROOT/'roku/source/settings-model.brs').read_text().replace('CreateObject("roRegistrySection", "deep-reef-v1")','ReefTestRegistry("deep-reef-v1")')
    (work/'settings-test.brs').write_text(settings)
    extra=['roku/components/ReefSettings.brs'] if test=='settings_ui' else ['roku/source/renderer.brs'] if test in ['render_depth','upright_present','swim_sway','clam_night_surface','clam_contents','wave_equivalence'] else []
    if test=='collision_equivalence':extra+=['tests/collision-reference.brs']
    if test in ['runtime_stability','clam_night_surface']:extra+=['roku/source/assets.brs']
    if test in ['tail_attachment','export_turn_boundaries']:
        assets=(ROOT/'roku/source/assets.brs').read_text().replace('CreateObject("roRegion",','JointRegion(')
        (work/'assets-joint-test.brs').write_text(assets)
        extra+=['roku/source/renderer.brs','work/assets-joint-test.brs']
    args=['node','tests/roku_runner.cjs','--root','roku']+[f'roku/source/{s}.brs'for s in SOURCES]+['work/settings-test.brs','tests/registry-stub.brs',f'tests/{test}.brs']+extra
    result=subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=dict(os.environ,BRS_BIN=binary('brs')))
    (ROOT/log).write_text(result.stdout)
    if result.returncode or re.search(r'(?m)^FAIL|not a function|Attempting to return|Syntax|Error|error:',result.stdout):raise RuntimeError(result.stdout[-5000:])
    return result.stdout
if __name__=='__main__':
    try:
        check=subprocess.run([binary('bsc'),'--project','bsconfig.json'],cwd=ROOT,capture_output=True,text=True)
        (ROOT/'docs/compiler-results.txt').write_text(check.stdout+check.stderr)
        if check.returncode:raise RuntimeError(check.stdout+check.stderr)
        subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],cwd=ROOT,check=True)
        if '--quick' not in sys.argv:
            output=brs_run('simulation','docs/simulation-results.txt')
            if not re.search(r'RESULT passed=\s*32\s+failed=\s*0',output):raise RuntimeError('Simulation did not complete 32 checks')
        print(brs_run('activity','docs/activity-results.txt'))
        print(brs_run('movement_regression','docs/movement-regression-results.txt'))
        if '--quick' not in sys.argv:print(output)
        print(brs_run('fish_traffic','docs/fish-traffic-results.txt'))
        print(brs_run('route_recovery','docs/route-recovery-results.txt'))
        print(brs_run('contact_release','docs/contact-release-results.txt'))
        print(brs_run('coral_pileup','docs/coral-pileup-results.txt'))
        print(brs_run('clam_contents','docs/clam-contents-results.txt'))
        print(brs_run('clam_night_surface','docs/clam-night-surface-results.txt'))
        print(brs_run('appendage_smoothness','docs/appendage-smoothness-results.txt'))
        print(brs_run('swim_sway','docs/swim-sway-results.txt'))
        from tail_check import validate as validate_tail
        import json
        brs_run('tail_attachment','work/tail-joints-current.txt')
        joint=validate_tail(ROOT/'work/tail-joints-current.txt')
        if joint['max_fractional_root_error_pixels']>.02 or joint['max_integer_root_error_pixels']>.75 or joint['side_view_collars_without_overlap']or joint['tail_not_before_body_cases']or joint['tail_phase_mismatch_cases']:raise RuntimeError(str(joint))
        (ROOT/'docs/tail-attachment-results.json').write_text(json.dumps(joint,indent=2)+'\n')
        print('PASS shared mesh tail attachment: '+str(joint))
        brs_run('export_turn_boundaries','work/turn-boundaries-current.txt')
        from turn_capture_check import validate as validate_turn_boundaries
        boundaries=validate_turn_boundaries(ROOT/'work/turn-boundaries-current.txt')
        if boundaries['max_centroid_jump_px']>.5 or boundaries['max_area_jump_fraction']>.02 or boundaries['max_rgb_jump_per_body_pixel']>1.5:raise RuntimeError(str(boundaries))
        (ROOT/'docs/turn-boundaries-results.json').write_text(json.dumps(boundaries,indent=2)+'\n')
        print('PASS actual C-turn outline continuity: '+str({k:v for k,v in boundaries.items()if k not in ['species','worst']}))
        print(brs_run('cpu_workload','docs/cpu-workload-results.txt'))
        print(brs_run('collision_equivalence','docs/collision-equivalence-results.txt'))
        print(brs_run('frame_profile','docs/frame-profile-results.txt'))
        print(brs_run('runtime_stability','docs/runtime-stability-results.txt'))
        print(brs_run('wave_equivalence','docs/wave-equivalence-results.txt'))
        print(brs_run('fish_profile','docs/fish-profile-results.txt'))
        print(brs_run('floor_collision','docs/floor-collision-results.txt'))
        print(brs_run('cave_collision','docs/cave-collision-results.txt'))
        print(brs_run('marine_motion','docs/marine-motion-results.txt'))
        print(brs_run('surface_lighting','docs/surface-lighting-results.txt'))
        print(brs_run('settings_ui','docs/settings-results.txt'))
        if '--quick' not in sys.argv:print(brs_run('reef_collision','docs/collision-results.txt'))
        else:print(brs_run('quick_collision','docs/collision-results.txt'))
        print(brs_run('waves_smoothness','docs/wave-smoothness-results.txt'))
        print(brs_run('render_depth','docs/render-depth-results.txt'))
        print(brs_run('upright_present','docs/upright-present-results.txt'))
        print(brs_run('turn_smoothness','docs/turn-smoothness-results.txt'))
        subprocess.run([sys.executable,'tools/turn_check.py'],cwd=ROOT,check=True)
        pan=brs_run('pan_precision','docs/pan-precision-results.txt')
        from pan_check import validate
        summary=validate(pan)
        (ROOT/'docs/pan-precision-results.txt').write_text(pan+summary)
        print(summary)
        if '--three-minute'in sys.argv:print(brs_run('three_minute','docs/three-minute-after.txt'))
        if '--scene-soak'in sys.argv:print(brs_run('scene_soak','docs/scene-soak-results.txt'))
        if '--soak'in sys.argv:
            output=brs_run('soak','docs/soak-results.txt')
            if not re.search(r'SOAK RESULT violations=\s*0',output):raise RuntimeError(output[-2000:])
            print(output)
        print('All requested checks passed')
    except (RuntimeError,subprocess.CalledProcessError)as e:raise SystemExit(str(e))
