"""Compare captured production turns and frontal proportions before/after."""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from capture_raster import ROOT,render
PRE=ROOT/'docs/previews';WORK=ROOT/'work'
def read(path,prefix):
    return {(f['name'],f['tick']):f for line in Path(path).read_text().splitlines()if line.startswith(prefix)for f in [json.loads(line[len(prefix):]) ]}
def build():
    before=read(WORK/'v35-turn-before.txt','TURN ');after=read(WORK/'v35-turn-after.txt','TURN ')
    names=['copperband_butterflyfish','blue_tang','emperor_angelfish'];labels=['Copperband butterflyfish','Regal blue tang','Emperor angelfish']
    frames=[]
    for tick in range(0,181,2):
        canvas=Image.new('RGBA',(760,810),(19,42,55,255));d=ImageDraw.Draw(canvas)
        for row,name in enumerate(names):
            for col,(source,root)in enumerate([(before,WORK/'v35-before-pkg'),(after,None)]):
                im=render(source[name,tick],asset_root=root);canvas.alpha_composite(im,(380*col,270*row+15))
                d.text((380*col+10,270*row+8),labels[row]+(' | previous'if col==0 else' | corrected'),fill='white')
        d.text((10,795),'Tilted 180-degree turn | Host reconstruction of actual draw commands; not a Roku recording.',fill=(180,210,220))
        frames.append(canvas.convert('RGB'))
    frames[45].save(PRE/'turn-comparison.png')
    palette=frames[0].quantize(colors=224);gif=[im.quantize(palette=palette,dither=Image.Dither.NONE)for im in frames]
    gif[0].save(PRE/'turn-comparison.gif',save_all=True,append_images=gif[1:],duration=116,loop=0,disposal=2,optimize=False)
    old=read(WORK/'v35-front-before.txt','FRONT ');new=read(WORK/'v35-front-after.txt','FRONT ')
    canvas=Image.new('RGBA',(960,350),(19,42,55,255));d=ImageDraw.Draw(canvas)
    for col,(source,tick,root,label)in enumerate([(old,1,WORK/'v35-before-pkg','Previous frontal shape'),(new,1,None,'Fuller frontal shape'),(new,0,None,'Side silhouette preserved')]):
        im=render(source['copperband_butterflyfish',tick],(320,300),root);canvas.alpha_composite(im,(col*320,20));d.text((col*320+12,12),label,fill='white')
    d.text((12,329),'Copperband butterflyfish | Same native canvas resolution | Host-rendered model preview.',fill=(180,210,220))
    canvas.convert('RGB').save(PRE/'copperband-front.png')
    print('Saved turn comparison animation and copperband frontal comparison.')
if __name__=='__main__':build()
