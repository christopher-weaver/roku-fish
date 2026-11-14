"""Quantize real fish transforms and compare view changes against atlas snapping."""
from pathlib import Path
import json,math,struct
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

def check_blending():
    species=json.loads((ROOT/'roku/scenes/species.json').read_text());results={}
    for name,sp in species.items():
        atlas=Image.open(ROOT/'roku'/sp['image'][5:]).convert('RGBA');size=(sp['frameW']*2,sp['frameH']*2);cache={}
        for yaw in range(sp['yawCount']):
            fr=sp['frames'][yaw*sp['poseCount']+3];im=Image.new('RGBA',(sp['frameW'],sp['frameH']))
            im.alpha_composite(atlas.crop((fr['x'],fr['y'],fr['x']+fr['w'],fr['y']+fr['h'])),(int(sp['frameW']/2-fr['anchorX']),int(sp['frameH']/2-fr['anchorY'])))
            if fr['flipX']:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            cache[yaw]=im
        def render(angle,blend):
            position=angle/(2*math.pi)*sp['yawCount'];lo=int(position)%sp['yawCount'];fraction=position-int(position)
            nearest=round(position)%sp['yawCount'];width=sp['viewWidths'][lo]*(1-fraction)+sp['viewWidths'][(lo+1)%sp['yawCount']]*fraction
            canvas=Image.new('RGBA',size,(72,45,81,255))
            for view,alpha in ([(lo,1),((lo+1)%sp['yawCount'],fraction)]if blend else [(nearest,1)]):
                source=cache[view];sx=width/sp['viewWidths'][view]if blend else 1
                # Fixed output grid, matching continuous native scaling rather
                # than introducing integer-resize steps into this measurement.
                layer=source.transform(size,Image.Transform.AFFINE,(1/sx,0,sp['frameW']/2-size[0]/(2*sx),0,1,-sp['frameH']/2),Image.Resampling.BICUBIC)
                if alpha<1:layer.putalpha(layer.getchannel('A').point(lambda v:round(v*alpha)))
                canvas.alpha_composite(layer)
            return np.asarray(canvas,dtype=np.float32)[:,:,:3]
        snap=[];smooth=[];last_a=last_b=None
        for degrees in np.linspace(10,80,281):
            a=render(math.radians(degrees),False);b=render(math.radians(degrees),True)
            if last_a is not None:snap.append(float(np.abs(a-last_a).sum()));smooth.append(float(np.abs(b-last_b).sum()))
            last_a=a;last_b=b
        ratio=max(smooth)/max(snap)
        if ratio>=.65:raise AssertionError(f'{name}: turn transition peak remains {ratio:.3f} of snapped views')
        results[name]=round(ratio,3)
    return results
if __name__=='__main__':
    report={'float32_max_center_error_px':check_geometry(),'peak_frame_change_ratio_vs_snapped_views':check_blending(),'scope':'Host math and raster comparison; actual Roku GPU/frame rate require device validation.'}
    (ROOT/'docs/turn-visual-results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
