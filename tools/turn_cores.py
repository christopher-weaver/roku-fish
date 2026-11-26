"""Bake small opaque undercoat masks inside both neighboring C silhouettes.

The masks let textured outlines genuinely crossfade while retaining an opaque
interior. White masks are quarter resolution; the photographed skins are not.
"""
import json,math
import numpy as np
from PIL import Image,ImageFilter
from fish_mesh import ROOT,pack

def build(names=None):
    path=ROOT/'roku/scenes/species.json';species=json.loads(path.read_text())
    for name,sp in species.items():
        if names and name not in names:continue
        atlas=Image.open(ROOT/'roku'/sp['image'][5:]).convert('RGBA')
        pixels=np.asarray(atlas);solid=pixels[:,:,3]>240
        color=np.uint8(np.rint(pixels[:,:,:3][solid].mean(axis=0))).tolist()
        count=sp['turnViews']['bodyYawCount'];cache={};shots=[];indices=[];refs=[]
        fw,fh=sp['frameW'],sp['frameH'];pw=math.ceil(fw/4)*4;ph=math.ceil(fh/4)*4
        for view in range(count):
            for pose in range(2):
                a=sp['frames'][sp['turnOffset']+view*2+pose]
                b=sp['frames'][sp['turnOffset']+((view+1)%count)*2+pose]
                key=tuple(sorted([(a['x'],a['y']),(b['x'],b['y'])]))
                width=(a['w']+b['w']-8)/2;anchor=(a['anchorX']+b['anchorX']-4)/2
                if key not in cache:
                    masks=[]
                    for f in [a,b]:
                        source=atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h'])).getchannel('A')
                        sx=width/(f['w']-4);offset=(f['anchorX']-2)*sx-anchor
                        matrix=(1/sx,0,f['anchorX']-(fw/2+offset)/sx,0,1,f['anchorY']-fh/2)
                        masks.append(np.asarray(source.transform((pw,ph),Image.Transform.AFFINE,matrix,Image.Resampling.BILINEAR)))
                    mask=Image.fromarray(np.uint8(np.minimum(*masks)>250)*255).filter(ImageFilter.MinFilter(13))
                    mask=mask.resize((pw//4,ph//4),Image.Resampling.LANCZOS)
                    mask=mask.point(lambda v:round(round(v*31/255)*255/31))
                    box=mask.getbbox()or(0,0,1,1);x0,y0,x1,y1=box
                    box=(max(0,x0-1),max(0,y0-1),min(pw//4,x1+1),min(ph//4,y1+1))
                    im=Image.new('RGBA',(pw//4,ph//4),'white');im.putalpha(mask);im=im.crop(box)
                    cache[key]=len(shots)
                    shots.append((im,{'anchorX':fw/8-box[0],'anchorY':fh/8-box[1]}))
                indices.append(cache[key]);refs.append((width,anchor))
        out,frames=pack(shots,512);image=sp['image'].replace('-atlas.webp','-turn-cores.webp')
        out.save(ROOT/'roku'/image[5:],lossless=True,quality=100,method=6,exact=True)
        sp.update(turnCoreImage=image,turnCoreScale=4,turnCoreColor=color,turnCoreFrames=[dict(frames[i],coreWidth=w,coreAnchor=a)for i,(w,a)in zip(indices,refs)])
        print(name,'undercoat masks',len(shots),out.size,flush=True)
    path.write_text(json.dumps(species,indent=2))
    from catalog import catalog
    catalog()
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--species',nargs='+');args=p.parse_args();build(args.species)
