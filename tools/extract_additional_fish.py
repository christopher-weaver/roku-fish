"""Reproduce the four new source portraits from the checked-in generated sheet."""
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'assets/source'
def extract():
    sheet=Image.open(SRC/'fish-additional-sheet.png').convert('RGBA')
    boxes={'blue_tang':(0,0,768,480),'copperband_butterflyfish':(768,0,1536,512),'banggai_cardinalfish':(0,480,768,1024),'mandarin_dragonet':(768,512,1536,1024)}
    for name,box in boxes.items():
        im=sheet.crop(box);alpha=np.asarray(im.getchannel('A'))
        alpha=np.where(alpha<8,0,np.minimum(255,alpha.astype(float)*255/252)).astype('uint8')
        im.putalpha(Image.fromarray(alpha));im.crop(im.getchannel('A').getbbox()).save(SRC/(name+'.png'))
if __name__=='__main__':extract()
