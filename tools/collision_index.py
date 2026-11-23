"""Exact row-union sparse table: any rectangle needs at most two string searches.

Each level ORs 2**level consecutive occupancy rows. Two overlapping bands of
that size cover every query height exactly. Shared mask strings keep the parsed
index small; this does not dilate, simplify or otherwise change the reef grid.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'roku/scenes/collision-index.json'

def make_index(occupancy):
    masks=[]; unique={}; planes=[]
    for plane in occupancy['planes']:
        rows=plane['rows']; levels=[]; span=1
        while span<=len(plane['rows']):
            if span>1:
                half=span//2
                rows=[''.join('#' if a=='#' or b=='#' else '.' for a,b in zip(rows[i],rows[i+half]))
                      for i in range(len(plane['rows'])-span+1)]
            indices=[]
            for row in rows:
                if row not in unique:
                    unique[row]=len(masks); masks.append(row)
                indices.append(unique[row])
            levels.append(indices); span*=2
        planes.append({'id':plane['id'],'levels':levels})
    height=len(occupancy['rows'])
    levels=[0]+[n.bit_length()-1 for n in range(1,height+1)]
    return {'cell':occupancy['cell'],'masks':masks,'planes':planes,
            'levelByHeight':levels,'spanByHeight':[2**level for level in levels]}

def encoded(occupancy):
    return json.dumps(make_index(occupancy),separators=(',',':'))+'\n'

def write_index():
    PATH.write_text(encoded(json.loads((ROOT/'roku/scenes/occupancy.json').read_text())))

if __name__=='__main__':
    write_index(); print(f'Wrote exact collision index: {PATH.stat().st_size:,} bytes')
