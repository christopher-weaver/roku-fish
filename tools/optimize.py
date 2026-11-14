"""High-quality, alpha-preserving libimagequant palettes and compact manifest art."""
from pathlib import Path
from PIL import Image
import imagequant
ROOT=Path(__file__).resolve().parents[1]
def optimize(atlases_only=False,effects_only=False):
    for p in sorted((ROOT/'roku/images').glob('*.png')):
        if effects_only and p.name not in ['surface-waves.png','sand-caustics.png']:continue
        if atlases_only and 'atlas' not in p.name and '-fins' not in p.name:continue
        if Image.open(p).mode=='P':continue
        im=Image.open(p).convert('RGBA')
        if p.name in ['surface-waves.png','sand-caustics.png']:colors=96;dither=0
        elif 'reef-' in p.name:colors=256;dither=.75
        elif 'atlas' in p.name or '-fins' in p.name:
            colors=64 if '-fins' in p.name else 80 if p.name.startswith(('ocellaris_clownfish','royal_gramma','green_chromis')) else 88
            dither=0
        else:colors=160;dither=.4
        im=imagequant.quantize_pil_image(im,max_colors=colors,dithering_level=dither,max_quality=95)
        if 'atlas' in p.name or '-fins' in p.name:
            im.convert('RGBA').save(p.with_suffix('.webp'),lossless=True,method=6,exact=True)
            p.unlink()
        else:
            im.save(p,optimize=True)
        print('Optimized',p.name,flush=True)
    if atlases_only or effects_only:return
    for p in sorted((ROOT/'roku/images').glob('*.jpg')):
        im=Image.open(p).convert('RGB')
        if p.name.startswith('splash'):
            original=im.size;im.thumbnail((960,540));im=im.resize(original,Image.Resampling.LANCZOS);quality=66
        else:quality=78
        im.save(p,quality=quality,optimize=True,subsampling=2)
if __name__=='__main__':optimize()
