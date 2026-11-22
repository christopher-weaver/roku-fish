"""Audit real atlas work and verify a cropped-shadow rebuild against saved originals.

Call with --baseline work/perf-before; this measures source work, not Roku FPS.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def cost(tank):
 maps=[f['surfaceShadow']for f in tank['formations']if 'surfaceShadow'in f]
 return {'shadow_passes':2*len(maps),'shadow_source_pixels_per_fhd_frame':sum(2*c['width']*c['height']*c['scale']**2 for c in maps)}
def verify(before,after,folder):
 frames=0
 for original in before['formations']:
  if 'surfaceShadow'not in original:continue
  c=original['surfaceShadow'];old=Image.open(folder/Path(c['image']).name).convert('RGBA')
  target=next(f for f in after['formations']if f['id']==original['id']).get('surfaceShadow')
  atlas=Image.open(ROOT/'roku'/target['image'][5:]).convert('RGBA')if target else None
  for i in range(c['frames']):
   x=i%c['columns']*c['width'];y=i//c['columns']*c['height'];expected=np.asarray(old.crop((x,y,x+c['width'],y+c['height'])))
   actual=Image.new('RGBA',(128,72))
   if target:
    x=i%target['columns']*target['width'];y=i//target['columns']*target['height']
    actual.paste(atlas.crop((x,y,x+target['width'],y+target['height'])),(target['x']//16,target['y']//16))
   actual=np.asarray(actual);assert np.array_equal(actual[:,:,3],expected[:,:,3]),original['id']
   visible=expected[:,:,3]>0;assert np.array_equal(actual[visible],expected[visible]),original['id']
   frames+=1
 return {'frames_verified':frames,'alpha_error':0,'visible_color_error':0}
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,default=ROOT/'docs/performance-audit.json');a=p.parse_args()
 before=json.loads((a.baseline/'tank.json').read_text());after=json.loads((ROOT/'roku/scenes/tank.json').read_text())
 report={'scope':'Source work counts and host regression checks, not measured Roku GPU time or device FPS','before':cost(before),'after':cost(after),'shadow_reconstruction':verify(before,after,a.baseline),'performance_canvas_pixels':{'before':2048*1080,'after':1365*720},'default_medium_fish_transform_draws_per_frame':8*18,'fish_regions_for_eight_unique_species':8*1620}
 old=json.loads((a.baseline/'calls.json').read_text())['counts'];new=json.loads((ROOT/'work/calls-after.json').read_text())['counts']
 keys=['sin','cos','atn','sqr','reeffishtransform']
 report['body_render_fixture']={'frames':120,'before':{k:old.get(k,0)for k in keys},'after':{k:new.get(k,0)for k in keys},'draws_before':old.get('drawtransformedobject',0),'draws_after':new.get('drawtransformedobject',0)}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
