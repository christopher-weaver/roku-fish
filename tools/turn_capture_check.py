"""Check the actual C-turn submissions across infinitesimal yaw boundaries."""
import json,sys
from pathlib import Path
import numpy as np
from capture_raster import render

def validate(path,asset_root=None):
    frames={}
    for line in Path(path).read_text().splitlines():
        if line.startswith('TURN '):
            f=json.loads(line[5:]);frames.setdefault((f['name'],f.get('turnSign',1),round(f['boundary'],4)),{})[f['side']]=f
    results=[]
    for (name,direction,angle),pair in frames.items():
        if len(pair)!=2:raise ValueError('Incomplete turn pair')
        images=[np.asarray(render(pair[side],asset_root=asset_root,body_only=True)).astype(float)for side in [-1,1]]
        alphas=[a[:,:,3]/255 for a in images];areas=[a.sum()for a in alphas]
        yy,xx=np.mgrid[:images[0].shape[0],:images[0].shape[1]]
        centers=[np.array([(xx*a).sum(),(yy*a).sum()])/a.sum()for a in alphas]
        bg=np.array([19,42,55]);rgb=[im[:,:,:3]*a[:,:,None]+bg*(1-a[:,:,None])for im,a in zip(images,alphas)]
        results.append({'name':name,'turn_direction':direction,'yaw_degrees':angle,'centroid_jump_px':float(np.linalg.norm(centers[1]-centers[0])),'area_jump_fraction':abs(areas[1]-areas[0])/max(areas),'rgb_jump_per_body_pixel':float(np.abs(rgb[1]-rgb[0]).sum()/3/max(areas))})
    if not results:raise ValueError('No turn captures')
    species={}
    for name in sorted({r['name']for r in results}):
        rows=[r for r in results if r['name']==name]
        species[name]={k:max(r[k]for r in rows)for k in ['centroid_jump_px','area_jump_fraction','rgb_jump_per_body_pixel']}
    return {'boundary_pairs':len(results),'max_centroid_jump_px':max(r['centroid_jump_px']for r in results),'max_area_jump_fraction':max(r['area_jump_fraction']for r in results),'max_rgb_jump_per_body_pixel':max(r['rgb_jump_per_body_pixel']for r in results),'species':species,'worst':sorted(results,key=lambda r:-r['rgb_jump_per_body_pixel'])[:8]}
if __name__=='__main__':
    report=validate(sys.argv[1],sys.argv[2]if len(sys.argv)>2 else None);print(json.dumps(report,indent=2))
