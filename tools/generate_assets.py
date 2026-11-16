"""Rebuild native art from checked-in source pixels and real 3D geometry."""
from pathlib import Path
import subprocess
import seafloor,art,fish_mesh,dense_turns,marine_animation,reef_geometry,pack_eel_3d,formation_frames,waves,surface_lighting,optimize,catalog
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    fish_mesh.build();dense_turns.build();art.build();marine_animation.build();reef_geometry.build();seafloor.build(refresh=True)
    subprocess.run(['blender','--background','--threads','4','--python','tools/render_eel_3d.py','--','--model-only'],cwd=ROOT,check=True)
    pack_eel_3d.build();formation_frames.reserve_navigation();
    subprocess.run(['blender','--background','--threads','4','--python','tools/save_reef_blend.py'],cwd=ROOT,check=True)
    waves.build();surface_lighting.build();optimize.optimize();catalog.catalog()
