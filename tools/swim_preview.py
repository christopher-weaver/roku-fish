"""Reconstruct the export_swim.brs production draw capture and proportion sheet."""
from pathlib import Path
import json,math,sys
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from capture_raster import render
samples={}
for line in (root/'work/v35-swim-preview.txt').read_text().splitlines():
 if line.startswith('SWIM '):
  f=json.loads(line[5:]);samples[f['name'],f['view'],f['tick']]=f
assert len(samples)==360,len(samples)
frames=[];names=['blue_tang','emperor_angelfish'];labels=['Regal blue tang','Emperor angelfish'];views=['Profile S swim','Oblique S swim','Front / raised eyes','Turning left / C bend','Turning right / C bend']
for tick in range(36):
 sheet=Image.new('RGBA',(1900,590),(19,42,55,255));draw=ImageDraw.Draw(sheet)
 for row,name in enumerate(names):
  for col in range(5):
   im=render(samples[name,col,tick]);sheet.alpha_composite(im,(col*380,row*285+25));draw.text((col*380+12,row*285+7),labels[row]+' | '+views[col],fill=(235,244,245))
 draw.text((12,574),'Slow-motion host reconstruction of production draws: stronger lateral S swim, signed C-turn geometry, paired raised eyeballs. Not a Roku screenshot.',fill=(177,204,214))
 frames.append(sheet.convert('RGB'))
frames[9].save(root/'docs/previews/lateral-swim.png')
palette=frames[0].quantize(colors=224);gif=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
gif[0].save(root/'docs/previews/lateral-swim.gif',save_all=True,append_images=gif[1:],duration=60,loop=0,disposal=2,optimize=False)
from preview import fish,SPEC
sheet=Image.new('RGBA',(760,1000),(19,42,55,255));draw=ImageDraw.Draw(sheet)
for i,(name,sp) in enumerate(SPEC.items()):
 x=i%2*380;y=i//2*200
 for heading,sx in [(0,x+115),(math.pi/2,x+300)]:
  f=dict(name=name,heading=heading,phase=0,finPhase=.4,pitch=0,speed=sp['speed'],x=1000,sy=y+112,sx=sx,z=.7,scale=1,size=190/sp['length'])
  fish(sheet,f,'Sunset')
 draw.text((x+8,y+6),sp['label']+' | width/length '+str(round(sp['modelWidthRatio']*100,1))+'%',fill=(235,244,245))
sheet.convert('RGB').save(root/'docs/previews/fish-proportions.png')
print('Saved production swim captures and ten-species proportions contact.')
