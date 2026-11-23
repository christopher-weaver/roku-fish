"""Extract shared caudal/body attachment vertices from the existing fish meshes."""
from pathlib import Path
import json
import numpy as np
from fish_mesh import TAIL_RIGS,BODY_BENDS
ROOT=Path(__file__).resolve().parents[1]
def build():
    path=ROOT/'roku/scenes/species.json';species=json.loads(path.read_text())
    for name,sp in species.items():
        with np.load(ROOT/'assets/source'/(name+'.npz'))as mesh:
            shared=np.intersect1d(mesh['body_faces'].ravel(),mesh['tail_faces'].ravel())
            vertices=mesh['vertices'][shared].astype(float)
        center=vertices.mean(axis=0);poses=[];cut=TAIL_RIGS[name][0]*2-1
        for bend in BODY_BENDS:
            posed=vertices.copy();rear=np.maximum(0,cut-posed[:,0])
            posed[:,2]+=bend*rear*rear;posed[:,0]+=bend*bend*rear**3*.85
            point=posed.mean(axis=0);poses.append([round(float(point[0]),8),round(float(point[2]),8)])
        sp['tailRig']={'body':[round(float(v),8)for v in center],'posesXZ':poses,'overlap':3}
    path.write_text(json.dumps(species,indent=2))
if __name__=='__main__':build()
