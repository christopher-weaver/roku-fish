"""Rasterize captured native draw commands for host visual regressions."""
from pathlib import Path
import math
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
CACHE={}
def render(f,size=(380,260),asset_root=None,body_only=False):
    root=Path(asset_root)if asset_root else ROOT/'roku'
    ox=f['p']['x']-size[0]/2;oy=f['p']['y']-size[1]/2
    canvas=Image.new('RGBA',size)
    for d in f['draws']:
        if body_only and d['part']!='body':continue
        path=root/d['file'][5:]
        if path not in CACHE:CACHE[path]=Image.open(path).convert('RGBA')
        im=CACHE[path].crop((d['cropX'],d['cropY'],d['cropX']+d['w'],d['cropY']+d['h']))
        a=math.radians(d['angle']);co=math.cos(a);sn=math.sin(a);x=d['x']-ox;y=d['y']-oy
        matrix=(co/d['sx'],-sn/d['sx'],(-co*x+sn*y)/d['sx']-d['px'],sn/d['sy'],co/d['sy'],(-sn*x-co*y)/d['sy']-d['py'])
        im=im.transform(size,Image.Transform.AFFINE,matrix,Image.Resampling.BILINEAR)
        if 'rgba' in d:
            tint=d['rgba']&0xffffffff
            from PIL import ImageChops
            im=ImageChops.multiply(im,Image.new('RGBA',im.size,((tint>>24)&255,(tint>>16)&255,(tint>>8)&255,255)))
        if d['alpha']<255:im.putalpha(im.getchannel('A').point(lambda v:round(v*d['alpha']/255)))
        canvas.alpha_composite(im)
    return canvas
