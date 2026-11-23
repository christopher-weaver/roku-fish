"""Independently project shared mesh joints and rasterize production submissions."""
import json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/'roku/scenes/species.json').read_text());CACHE={}
def targets(f,overlap):
    sp=SPEC[f['name']];root=sp['tailRig']['body'];body=f['body'];scale=f['fishScale'];sinphase=math.sin(f['phase']);points=[]
    for view in [body['first'],body['second']]:
        a=sp['bodyAngles'][view];co=math.cos(a);sn=math.sin(a)
        x=(root[0]*co-root[2]*sn)*sp['frameW']*.45;y=-root[1]*sp['frameH']*.45
        fr=sp['frames'][view*3+1];pixel=fr['anchorX']+x;left=math.floor(pixel);blend=pixel-left;shift=0
        for col,w in [(left,1-blend),(left+1,blend)]:
            u=np.clip(.5-(1 if co>=0 else -1)*(col-fr['anchorX'])/(sp['frameW']*.9),0,1)
            d=sp['renderLength']*sp['bodySwimAmplitude']*abs(co)*u*u*math.sin(-u*2*math.pi)
            k=-math.floor(.5-d)if sinphase>=0 else -math.floor(.5+d)
            shift+=w*k*abs(sinphase)
        points.append((x/sp['bodyViewWidths'][view],y+shift))
    mix=body['blend'];tx=scale*body['width']*(points[0][0]+(points[1][0]-points[0][0])*mix)
    ty=scale*(points[0][1]+(points[1][1]-points[0][1])*mix)
    tx+=overlap*scale*math.cos(f['heading'])
    angle=f['pitch']*(1 if math.cos(f['heading'])>=0 else -1)*57.29578
    if f.get('fractional',True):angle=math.floor(angle*256+.5)/256
    co=math.cos(math.radians(angle));sn=math.sin(math.radians(angle))
    x=(f['p']['x']+f['canvas'])*f['scale'];y=f['p']['y']*f['scale']
    if not f.get('fractional',True):x=math.floor(x+.5);y=math.floor(y+.5)
    return (x+(co*tx+sn*ty)*f['scale'],y+(co*ty-sn*tx)*f['scale'])
def source_root(f):
    sp=SPEC[f['name']];yaw=f['view']['index'];pose=int((math.sin(f['phase'])+1)*.5*(sp['tailPoseCount']-1)+.5)
    frame=sp['tailFrames'][yaw*sp['tailPoseCount']+pose];angle=math.radians(frame['yaw'])
    if frame['yaw']>180:angle=2*math.pi-angle;pose=sp['tailPoseCount']-1-pose
    v=sp['tailRig']['posesXZ'][pose]
    return ((v[0]*math.cos(angle)-v[1]*math.sin(angle))*sp['frameW']*.45,-sp['tailRig']['body'][1]*sp['frameH']*.45)
def raster(f,center,size=(84,64)):
    ox=center[0]-size[0]/2;oy=center[1]-size[1]/2
    canvas=Image.new('RGBA',size);layers={p:Image.new('RGBA',size)for p in ['body','tail']}
    for d in f['draws']:
        path=d['file']
        if path not in CACHE:CACHE[path]=Image.open(ROOT/'roku'/path[5:]).convert('RGBA')
        im=CACHE[path].crop((d['cropX'],d['cropY'],d['cropX']+d['w'],d['cropY']+d['h']))
        a=math.radians(d['angle']);co=math.cos(a);sn=math.sin(a);x=d['x']-ox;y=d['y']-oy
        matrix=(co/d['sx'],-sn/d['sx'],(-co*x+sn*y)/d['sx']-d['px'],sn/d['sy'],co/d['sy'],(-sn*x-co*y)/d['sy']-d['py'])
        im=im.transform(size,Image.Transform.AFFINE,matrix,Image.Resampling.BILINEAR)
        if d['alpha']<255:im.putalpha(im.getchannel('A').point(lambda v:round(v*d['alpha']/255)))
        canvas.alpha_composite(im);layers[d['part']].alpha_composite(im)
    intersection=(np.asarray(layers['body'])[:,:,3]>64)&(np.asarray(layers['tail'])[:,:,3]>64)
    # Only count the collar immediately around the anatomical attachment.
    yy,xx=np.mgrid[:size[1],:size[0]];near=(xx-size[0]/2)**2+(yy-size[1]/2)**2<14**2
    return canvas,int((intersection&near).sum())
def validate(path,overlap=True,preview=None):
    cases=0;max_error=0.;max_fractional=0.;max_integer=0.;no_overlap=[];worst=[];order_errors=0
    for line in Path(path).read_text().splitlines():
        if not line.startswith('JOINT '):continue
        f=json.loads(line[6:]);cases+=1
        sp=SPEC[f['name']];wanted=targets(f,sp['tailRig']['overlap']if overlap else 0)
        d=next(d for d in f['draws']if d['part']=='tail');root=source_root(f)
        # Fractional native regions pretranslate by 4096 minus the crop anchor.
        a=math.radians(d['angle']);co=math.cos(a);sn=math.sin(a)
        anchor=4096 if f.get('fractional',True)else 0
        actual=(d['x']+co*d['sx']*(root[0]+anchor)+sn*d['sy']*(root[1]+anchor),d['y']+co*d['sy']*(root[1]+anchor)-sn*d['sx']*(root[0]+anchor))
        error=math.dist(actual,wanted);max_error=max(max_error,error)
        if f.get('fractional',True):max_fractional=max(max_fractional,error)
        else:max_integer=max(max_integer,error)
        if f['draws'][0]['part']!='tail':order_errors+=1
        if f['scale']==1 and abs(math.cos(f['heading']))>.65:
            center=targets(f,0);im,area=raster(f,center)
            if area==0:no_overlap.append([f['name'],f['heading'],f['phase']])
            worst.append((error,f,im))
    if not cases:raise ValueError('No production joint captures')
    if preview:
        from PIL import ImageDraw
        selected=sorted(worst,key=lambda x:-x[0])[:8];sheet=Image.new('RGB',(672,156*2),(19,31,39));draw=ImageDraw.Draw(sheet)
        for i,(error,f,im)in enumerate(selected):
            x=(i%4)*168;y=(i//4)*156;im=im.resize((168,128),Image.Resampling.NEAREST);sheet.paste(im,(x,y+24),im);draw.text((x+3,y+3),f['name'][:19],fill='white')
        sheet.save(preview)
    return {'cases':cases,'max_root_error_pixels':round(max_error,6),'max_fractional_root_error_pixels':round(max_fractional,6),'max_integer_root_error_pixels':round(max_integer,6),'side_view_collars_without_overlap':len(no_overlap),'tail_not_before_body_cases':order_errors,'failing_collars':no_overlap[:12]}
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('path');p.add_argument('--baseline',action='store_true');p.add_argument('--preview');a=p.parse_args()
    report=validate(a.path,not a.baseline,a.preview);print(json.dumps(report,indent=2))
    if not a.baseline and(report['max_fractional_root_error_pixels']>.02 or report['max_integer_root_error_pixels']>.75 or report['side_view_collars_without_overlap']or report['tail_not_before_body_cases']):raise SystemExit('FAIL caudal attachment')
