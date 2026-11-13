"""High-quality, alpha-preserving libimagequant palettes and compact manifest art."""
from pathlib import Path
from PIL import Image
import imagequant
ROOT=Path(__file__).resolve().parents[1]
def optimize(atlases_only=False):
    for p in sorted((ROOT/'roku/images').glob('*.png')):
        if atlases_only and 'atlas' not in p.name:continue
        im=Image.open(p).convert('RGBA')
        if 'reef-' in p.name:colors=256;dither=.75
        elif 'atlas' in p.name:colors=192;dither=.45
        else:colors=160;dither=.4
        im=imagequant.quantize_pil_image(im,max_colors=colors,dithering_level=dither,max_quality=90)
        im.save(p,optimize=True)
        print('Optimized',p.name,flush=True)
    if atlases_only:return
    for p in sorted((ROOT/'roku/images').glob('*.jpg')):
        im=Image.open(p).convert('RGB')
        if p.name.startswith('splash'):
            original=im.size;im.thumbnail((960,540));im=im.resize(original,Image.Resampling.LANCZOS);quality=66
        else:quality=78
        im.save(p,quality=quality,optimize=True,subsampling=2)
if __name__=='__main__':optimize()
