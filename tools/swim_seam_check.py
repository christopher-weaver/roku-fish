"""Check joins using captured production region crops and native draw transforms."""
import json,math,sys
import numpy as np
from pathlib import Path

def validate(transcript):
    cases=samples=gaps=0
    for line in transcript.splitlines():
        if not line.startswith('SEAM '):continue
        f=json.loads(line[5:]);cases+=1
        for seam in range(1,8):
            cut=int(f['w']*seam/8)-f['ax']
            # Dense neighborhoods catch subpixel wedges beside a rotating join.
            pivots=np.linspace(cut-4,cut+4,17)
            ys=np.arange(1,f['h']-1,.5)-f['ay']
            pivot,local_y=np.meshgrid(pivots,ys)
            u=np.clip(.5-f['sign']*pivot/f['length'],0,1)
            phase=f['phase']-u*2*math.pi
            dy=f['amplitude']*u*u*np.sin(phase)
            slope=f['amplitude']*(2*u*np.sin(phase)-2*math.pi*u*u*np.cos(phase))*(-f['sign'])/f['length']
            angle=-np.arctan(slope)
            x=(500.25+pivot+np.sin(angle)*local_y)*f['scale']
            y=(300.25+dy+np.cos(angle)*local_y)*f['scale']
            covered=np.zeros(x.shape,dtype=bool)
            for d in f['draws']:
                a=math.radians(d['angle']);co=math.cos(a);sn=math.sin(a)
                dx=x-d['x'];dy2=y-d['y']
                tx=(co*dx-sn*dy2)/d['sx']-d['px']
                ty=(sn*dx+co*dy2)/d['sy']-d['py']
                guard=2.0/abs(d['sx'])
                covered|=(tx>=guard)&(tx<=d['w']-guard)&(ty>=0)&(ty<=d['h'])
            samples+=covered.size
            gaps+=int((~covered).sum())
    if not cases:raise ValueError('No production seam captures')
    return {'cases':cases,'seam_points':samples,'filter_guard_pixels':2,'unprotected':gaps}

if __name__=='__main__':
    report=validate(Path(sys.argv[1]).read_text());print(json.dumps(report))
    if report['unprotected']:raise SystemExit('FAIL body joins lack a two-pixel filter guard')
