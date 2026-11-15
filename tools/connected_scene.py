"""Reference-aligned connected reef, true-geometry marine assets and matched plate."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageEnhance,ImageFilter
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'roku/images';W,H=2048,1152

def source_reef():
    im=Image.open(ROOT/'assets/source/reef-connected-reference.png').convert('RGBA').resize((W,1110),Image.Resampling.LANCZOS)
    reef=Image.new('RGBA',(W,H));reef.alpha_composite(im,(0,-15))
    a=np.array(reef.getchannel('A'));a[a<8]=0;a[a>245]=255;reef.putalpha(Image.fromarray(a))
    return reef

def marine(name,width,height):
    im=Image.open(ROOT/'assets/source/marine-renders'/(name+'-finished.png')).convert('RGBA')
    a=im.getchannel('A');box=a.point(lambda x:255 if x>6 else 0).getbbox();im=im.crop(box).resize((width,height),Image.Resampling.LANCZOS)
    return im

def make_layers():
    reef=source_reef();a=np.asarray(reef.getchannel('A'));yy,xx=np.mgrid[:H,:W]
    front=(((xx-415)/270)**2+((yy-845)/230)**2<1)|(((xx-1290)/210)**2+((yy-820)/245)**2<1)|(((xx-1080)/190)**2+((yy-960)/150)**2<1)|(yy>960)|((xx>1450)&(yy>850))
    layers=[]
    for name,z,mask in [('connected-reef',.48,~front),('foreground-reef',.70,front)]:
        im=reef.copy();im.putalpha(Image.fromarray(np.where(mask,a,0).astype('uint8')))
        box=im.getchannel('A').getbbox();layers.append((name,z,.025,box[0],box[1],im.crop(box),False))
    layers+=[('sea-fan',.26,.018,80,430,marine('sea-fan',600,565),True),('sea-anemone',.75,.025,1330,815,marine('sea-anemone',285,215),True)]
    return sorted(layers,key=lambda layer:layer[1])

def guide():
    plate=Image.open(OUT/'water-sunset.webp').convert('RGBA').resize((W,H),Image.Resampling.LANCZOS)
    for name,z,half,x,y,im,rendered in make_layers():plate.alpha_composite(im,(x,y))
    path=ROOT/'assets/source/reef-layout-guide.png';plate.save(path);print(path,flush=True)

def build(splash):
    import scene,marine_views
    views=marine_views.build()
    cfg=json.loads((ROOT/'roku/scenes/tank.json').read_text());cfg['formations']=[];cfg['occlusionDepths']=[];planes=[];union=np.zeros((H,W),dtype=np.uint8)
    def grid(alpha):
        return [''.join('#'if np.any(alpha[y:y+8,x:x+8]>31)else'.'for x in range(0,W,8))for y in range(0,H,8)]
    used=set()
    for name,z,half,x,y,im,rendered in make_layers():
        if rendered:
            view=views[name];x=view['x'];y=view['y'];width=view['width'];height=view['height']
            im=Image.new('RGBA',(width,height));im.putalpha(Image.open(ROOT/'assets/source/marine-renders'/(name+'-views-footprint.png')))
            path=OUT/f'reef-{name}.webp'
            formation=dict(view,id=name,z=z,halfDepth=half,parallax=1,renderedMesh=True)
            if name=='sea-fan':formation['motion']={'amplitude':5.0,'period':11.0,'spread':.006,'lift':.8,'bandHeight':8,'clearance':9}
            if name=='sea-anemone':formation['motion']={'amplitude':3.5,'period':8.5,'spread':.012,'lift':1.2,'bandHeight':8,'clearance':7}
        else:
            rgba=np.array(im);alpha=rgba[:,:,3];valid=alpha>0
            distance,indices=distance_transform_edt(~valid,return_indices=True)
            near=(~valid)&(distance<=2)
            rgba[:,:,:3][near]=rgba[:,:,:3][indices[0][near],indices[1][near]]
            rgba[:,:,:3][(~valid)&~near]=0
            path=OUT/f'reef-{name}.webp';Image.fromarray(rgba).save(path,quality=88,method=6,exact=True)
            width,height=im.size
            formation=dict(id=name,x=x,y=y,width=width,height=height,z=z,halfDepth=half,parallax=1,image='pkg:/images/'+path.name,frames=1,columns=1,frameWidth=width,frameHeight=height,renderedMesh=False)
        used.add(path.name);cfg['formations'].append(formation)
        cfg['occlusionDepths'].append(z)
        canvas=Image.new('L',(W,H));canvas.paste(im.getchannel('A'),(x,y));mask=np.array(canvas);union=np.maximum(union,mask)
        plane_rows=grid(mask)
        if rendered:
            from scipy.ndimage import maximum_filter
            solid=np.array([[v=='#'for v in row]for row in plane_rows])
            solid=maximum_filter(solid,size=5 if name=='sea-fan'else 3)
            plane_rows=[''.join('#'if v else'.'for v in row)for row in solid]
        planes.append(dict(id=name,z=z,halfDepth=half,parallax=1,rows=plane_rows))
    for path in OUT.glob('reef-*.webp'):
        if path.name not in used:path.unlink()
    for name in ['coral-shadow.png']:(OUT/name).unlink(missing_ok=True)
    cfg['notes']='Connected reference-aligned reef, shared 1025px foundation, slight staggering. Sharp single images; seven-view textured 3D volumes for fan and anemone. Background recreated after final layout.'
    cfg['baseline']=1025;cfg['baselineTolerance']=30
    (ROOT/'roku/scenes/tank.json').write_text(json.dumps(cfg,indent=2)+'\n')
    occupied=np.array([[[v=='#'for v in row]for row in plane['rows']]for plane in planes]).any(axis=0)
    occ={'cell':8,'rows':[''.join('#'if v else'.'for v in row)for row in occupied],'planes':planes};(ROOT/'roku/scenes/occupancy.json').write_text(json.dumps(occ,separators=(',',':')))
    scene.build_navigation(occ)
    Image.fromarray(union).resize((1024,576)).save(ROOT/'docs/previews/reef-mask.png')
    background=Image.open(ROOT/'assets/source/background-matched-sunset.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    background=ImageEnhance.Sharpness(background).enhance(1.12);background.save(OUT/'water-sunset.webp',quality=88,method=6)
    cool=np.asarray(background,dtype=float);yy=np.arange(H)[:,None,None];water=np.clip((1040-yy)/200,0,1)
    blue=cool*np.array([.38,1.07,1.27])+np.array([0,8,15]);cool=cool*(1-water)+blue*water
    Image.fromarray(np.uint8(np.clip(cool,0,255))).save(OUT/'water-day.webp',quality=88,method=6)
    preview=background.convert('RGBA')
    for name,z,half,x,y,im,rendered in make_layers():preview.alpha_composite(im,(x,y))
    for name,size in [('icon-fhd',(540,405)),('icon-hd',(290,218)),('icon-sd',(214,144)),('splash-fhd',(1920,1080)),('splash-hd',(1280,720)),('splash-sd',(720,480))]:
        picture=preview.convert('RGB').resize(size,Image.Resampling.LANCZOS)if name.startswith('icon')else splash(size)
        picture.save(OUT/(name+'.jpg'),quality=78 if name.startswith('icon')else 66,optimize=True)
    print('Connected reef, true 3D fan/anemone and layout-matched backgrounds built',flush=True)
if __name__=='__main__':guide()
