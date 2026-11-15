"""Pack Blender renders of the actual moray model, including articulated poses."""
from pathlib import Path
import json
from PIL import Image
import numpy as np,imagequant
ROOT=Path(__file__).resolve().parents[1]
def build():
 frames=[];atlas=Image.new('RGBA',(8*118,4*144))
 for i in range(25):
  im=Image.open(ROOT/'work/eel-3d'/f'pose-{i:02d}.png').convert('RGBA').resize((114,140),Image.Resampling.LANCZOS);x=i%8*118+2;y=i//8*144+2;atlas.paste(im,(x,y));frames.append(dict(x=x,y=y,w=114,h=140,anchorX=57,anchorY=140))
 raw=ROOT/'assets/source/eel-model';atlas.save(raw/'rendered-poses.png')
 compact=imagequant.quantize_pil_image(atlas,max_colors=96,dithering_level=0,max_quality=95).convert('RGBA');rgba=np.array(compact);rgba[:,:,3][rgba[:,:,3]>245]=255
 Image.fromarray(rgba).save(ROOT/'roku/images/cave-eel-3d.webp',lossless=True,method=6,exact=True)
 (ROOT/'roku/scenes/eel.json').write_text(json.dumps({'image':'pkg:/images/cave-eel-3d.webp','count':25,'frames':frames,'model':'original procedural articulated 3D moray'},indent=2)+'\n')
 (ROOT/'roku/images/cave-eel.webp').unlink(missing_ok=True)
 print('Packed 25 true 3D eel renders',flush=True)
if __name__=='__main__':build()
