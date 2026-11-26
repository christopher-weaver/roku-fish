"""Compact fish colors at native resolution, preserving every alpha pixel."""
import json
from pathlib import Path
from PIL import Image
import numpy as np,imagequant
ROOT=Path(__file__).resolve().parents[1]
def compact(colors=None,names=None,part='body'):
    species=json.loads((ROOT/'roku/scenes/species.json').read_text());report={}
    for name,sp in species.items():
        if names and name not in names:continue
        key={'body':'image','tail':'tailImage','fin':'finImage'}[part]
        palette_key=part+'PaletteColors'
        default=(96 if name=='mandarin_dragonet' else 64)if part=='body'else(80 if part=='tail'else 64)
        chosen=colors if colors is not None else sp.get(palette_key,default)
        if sp.get(palette_key)==chosen:continue
        path=ROOT/'roku'/sp[key][5:];im=Image.open(path).convert('RGBA')
        q=imagequant.quantize_pil_image(im,max_colors=chosen,dithering_level=0,max_quality=95).convert('RGBA');q.putalpha(im.getchannel('A'))
        a=np.asarray(im).astype(float);b=np.asarray(q).astype(float);visible=a[:,:,3]>128
        error=float(np.abs(a[:,:,:3]-b[:,:,:3])[visible].mean())
        if error>4:raise ValueError('Excessive color error '+name+': '+str(error))
        before=path.stat().st_size;q.save(path,lossless=True,quality=100,method=6,exact=True)
        sp[palette_key]=chosen
        report[name]={'part':part,'palette':chosen,'before_bytes':before,'after_bytes':path.stat().st_size,'visible_rgb_mae':round(error,4),'alpha_identical':True}
        print(name,report[name],flush=True)
    (ROOT/'work/palette-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'roku/scenes/species.json').write_text(json.dumps(species,indent=2))
    from catalog import catalog
    catalog()
    return report
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--colors',type=int);p.add_argument('--species',nargs='+');p.add_argument('--part',choices=['body','tail','fin'],default='body');args=p.parse_args();compact(args.colors,args.species,args.part)
