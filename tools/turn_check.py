"""Quantize real fish transforms and compare view changes against atlas snapping."""
from pathlib import Path
import json,math,struct,bisect
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def f32(x):return struct.unpack('f',struct.pack('f',x))[0]
def check_geometry():
    worst=0
    for scale in [2/3,1]:
        for flip in [-1,1]:
            for pitch in np.linspace(-12.5,12.5,51):
                for step in range(60):
                    x=(700+step*.37)*scale;y=(410+step*.13)*scale
                    sx=flip*.91*scale;sy=.91*scale;angle=math.floor(pitch*256+.5)/256
                    c=math.cos(math.radians(angle));sn=math.sin(math.radians(angle));anchor=4096
                    px=math.floor(x-anchor*(c*sx+sn*sy));py=math.floor(y-anchor*(-sn*sx+c*sy))
                    dx=x-px-anchor*(c*sx+sn*sy);dy=y-py-anchor*(-sn*sx+c*sy)
                    sx=f32(sx+(c*dx-sn*dy)/anchor);sy=f32(sy+(sn*dx+c*dy)/anchor)
                    c=f32(c);sn=f32(sn)
                    actualx=f32(px+f32(anchor*f32(f32(c*sx)+f32(sn*sy))))
                    actualy=f32(py+f32(anchor*f32(f32(-sn*sx)+f32(c*sy))))
                    worst=max(worst,abs(actualx-x),abs(actualy-y))
    if worst>.002:raise AssertionError(f'Float32 fish center drift {worst}')
    return worst

def check_adaptive_turns():
    r=ROOT;sps=json.loads((r/'roku/scenes/species.json').read_text());out={}
    for name,sp in sps.items():
     atlas=Image.open(r/'roku'/sp['image'][5:]).convert('RGBA');angles=sp['bodyAngles'];cache={}
     for i,f in enumerate(sp['frames']):
      im=Image.new('RGBA',(sp['frameW'],sp['frameH']));im.alpha_composite(atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h'])),(round(sp['frameW']/2-f['anchorX']),round(sp['frameH']/2-f['anchorY'])));cache[i]=im
     coarse=[i for i,a in enumerate(angles)if abs(math.degrees(a)/5.625-round(math.degrees(a)/5.625))<1e-6]
     def render(a,indices):
      vals=[angles[i]for i in indices];lo=bisect.bisect_right(vals,a)-1;hi=(lo+1)%len(vals);upper=vals[hi]if hi else 2*math.pi;t=(a-vals[lo])/(upper-vals[lo]);i=indices[lo if t<.5 else hi]
      width=sp['bodyViewWidths'][indices[lo]]*(1-t)+sp['bodyViewWidths'][indices[hi]]*t;sx=width/sp['bodyViewWidths'][i];w,h=cache[i].size
      def warped(index):
       scale=width/sp['bodyViewWidths'][index]
       return cache[index].transform((w,h),Image.Transform.AFFINE,(1/scale,0,w/2-w/(2*scale),0,1,0),Image.Resampling.BICUBIC)
      bg=Image.new('RGBA',(w,h),(60,50,80,255))
      if len(indices)>len(coarse):
       bg.alpha_composite(warped(indices[lo]));layer=warped(indices[hi]);layer.putalpha(layer.getchannel('A').point(lambda v:round(v*t)));bg.alpha_composite(layer)
      else:bg.alpha_composite(warped(i))
      return np.asarray(bg,dtype=float)[:,:,:3]
     peaks=[]
     for indices in [coarse,list(range(len(angles)))]:
      last=None;diff=[]
      for a in np.radians(np.linspace(80,100,121)):
       cur=render(a,indices)
       if last is not None:diff.append(np.abs(cur-last).sum())
       last=cur
      peaks.append(max(diff))
     out[name]=round(peaks[1]/peaks[0],3)
    if max(out.values())>=.75:raise AssertionError('Head-on angle sampling failed to reduce peak image changes: '+str(out))
    return out

if __name__=='__main__':
    report={'float32_max_center_error_px':check_geometry(),'head_on_peak_frame_change_ratio_vs_64_angles':check_adaptive_turns(),'scope':'Host geometry and body-view interpolation checks; actual Roku GPU/FPS require device validation.'}
    (ROOT/'docs/turn-visual-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
