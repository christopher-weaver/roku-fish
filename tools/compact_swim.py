"""Repack selected native-resolution swim views without changing visible pixels."""
import json,math
from PIL import Image
from lateral_swim import ROOT,swim_angles,directions,TURN_ANGLES
from fish_mesh import pack

def compact():
    p=ROOT/'roku/scenes/species.json';species=json.loads(p.read_text())
    rp=ROOT/'assets/source/fish-rest/species.json';rest=json.loads(rp.read_text())
    unique=swim_angles();yaws=unique+[360-a for a in reversed(unique[1:-1])]
    for name,sp in species.items():
        path=ROOT/'roku'/sp['image'][5:];atlas=Image.open(path).convert('RGBA')
        lookup={round(math.degrees(a),6):i for i,a in enumerate(sp['bodyAngles'])}
        shots=[];widths=[]
        for yaw in unique:
            idx=lookup[round(yaw,6)]
            for pose in range(3):
                f=sp['frames'][idx*3+pose];im=atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']));shots.append((im,dict(f)))
        turn=sp['turnViews'];old_turn={round(math.degrees(a),6):i for i,a in enumerate(turn['bodyAngles'])}
        turn_unique=TURN_ANGLES;turn_yaws=turn_unique+[360-a for a in reversed(turn_unique[1:-1])]
        if any(round(yaw,6) not in old_turn for yaw in turn_unique):
            raise ValueError('Missing true turn views; rebuild with tools/lateral_swim.py before repacking')
        turn_widths=[turn['bodyViewWidths'][old_turn[round(yaw,6)]]for yaw in turn_yaws]
        turn_weights=[turn.get('bendWeights',[1]*len(old_turn))[old_turn[round(yaw,6)]]for yaw in turn_yaws]
        for yaw in turn_unique:
            i=old_turn[round(yaw,6)]
            for pose in range(2):
                f=sp['frames'][sp['turnOffset']+i*2+pose];im=atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']));shots.append((im,dict(f)))
        out,frames=pack(shots,2048);out.save(path,lossless=True,quality=100,method=6,exact=True)
        body=directions(frames[:len(unique)*3],3,yaws,unique,True)
        bends=directions(frames[len(unique)*3:],2,turn_yaws,turn_unique,True)
        for yaw in yaws:widths.append(sp['bodyViewWidths'][lookup[round(yaw,6)]])
        sp.update(frames=body+bends,width=out.width,height=out.height,bodyAngles=[math.radians(a)for a in yaws],bodyYawCount=len(yaws),bodyViewWidths=widths,turnOffset=len(body),turnViews={'bodyAngles':[math.radians(a)for a in turn_yaws],'bodyYawCount':len(turn_yaws),'bodyViewWidths':turn_widths,'bendWeights':turn_weights})
        rs=rest[name];rs.update(frames=[rs['frames'][lookup[round(yaw,6)]]for yaw in yaws],bodyAngles=sp['bodyAngles'],bodyYawCount=len(yaws),bodyViewWidths=widths)
        print(name,'views',len(yaws),'bytes',path.stat().st_size,flush=True)
    p.write_text(json.dumps(species,indent=2));rp.write_text(json.dumps(rest,indent=2))
    from catalog import catalog
    catalog()
if __name__=='__main__':compact()
