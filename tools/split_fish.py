"""Split the checked-in photographic refinement into the six normalized source portraits."""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def split():
    im=Image.open(ROOT/'assets/source/fish-photographic-sheet.png').convert('RGBA')
    names=['ocellaris_clownfish','yellow_tang','royal_gramma','emperor_angelfish','moorish_idol','green_chromis']
    for i,name in enumerate(names):
        box=(round(i%3*im.width/3),round(i//3*im.height/2),round((i%3+1)*im.width/3),round((i//3+1)*im.height/2))
        fish=im.crop(box);fish=fish.crop(fish.getchannel('A').getbbox());fish.save(ROOT/'assets/source'/(name+'.png'))
if __name__=='__main__':split()
