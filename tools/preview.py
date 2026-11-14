"""Render previews from actual BrightScript-exported world snapshots, not a Python fish brain."""
from pathlib import Path
import json, math, argparse
from PIL import Image,ImageChops,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];IM=ROOT/'roku/images';PRE=ROOT/'docs/previews'
SPEC=json.loads((ROOT/'roku/scenes/species.json').read_text())
CACHE={}
def asset(name):
    if name not in CACHE:CACHE[name]=Image.open(IM/name).convert('RGBA')
    return CACHE[name]
def paste(canvas,im,x,y,sx=1,sy=None,opacity=1):
    if im is None:return
    sy=sx if sy is None else sy
    if sx!=1 or sy!=1:im=im.resize((max(1,round(im.width*sx)),max(1,round(im.height*sy))),Image.Resampling.LANCZOS)
    if opacity!=1:im=im.copy();im.putalpha(im.getchannel('A').point(lambda v:round(v*opacity)))
    canvas.alpha_composite(im,(round(x),round(y)))
def fish(canvas,f,mode):
    sp=SPEC[f['name']];yaw=int((f['heading']%(2*math.pi))*sp['yawCount']/(2*math.pi)+.5)%sp['yawCount']
    pose=int((math.sin(f['phase'])+1)*.5*(sp['poseCount']-1)+.5);fr=sp['frames'][yaw*sp['poseCount']+pose]
    im=Image.new('RGBA',(sp['frameW'],sp['frameH']))
    body=asset(sp['image'].split('/')[-1]).crop((fr['x'],fr['y'],fr['x']+fr['w'],fr['y']+fr['h']))
    im.alpha_composite(body,(round(sp['frameW']/2-fr['anchorX']),round(sp['frameH']/2-fr['anchorY'])))
    finpose=int((math.sin(f.get('finPhase',f['phase']*.6))+1)*.5*(sp['finPoseCount']-1)+.5)
    fr=sp['finFrames'][yaw*sp['finPoseCount']+finpose]
    fin=asset(sp['finImage'].split('/')[-1]).crop((fr['x'],fr['y'],fr['x']+fr['w'],fr['y']+fr['h']))
    im.alpha_composite(fin,(round(sp['frameW']/2-fr['anchorX']),round(sp['frameH']/2-fr['anchorY'])))
    haze=1-f['z'];tint=(255,int(239-haze*25),int(240-haze*10))if mode=='Sunset'else(int(255-haze*65),int(247-haze*32),255)
    im=ImageChops.multiply(im,Image.new('RGBA',im.size,(*tint,255)))
    sc=f['scale']*sp['length']/sp['renderLength']*f['size'];im=im.resize((max(1,round(im.width*sc)),max(1,round(im.height*sc))),Image.Resampling.LANCZOS)
    angle=f['pitch']*57.29578*(-1 if math.cos(f['heading'])<0 else 1)
    im=im.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    paste(canvas,im,f['sx']-im.width/2,f['sy']-im.height/2)

def render(frame,mode='Sunset',density='Medium'):
    cam=frame['camera'];t=frame.get('displayTime',frame['time']);warm=mode=='Sunset';suf='-sunset' if warm else ''
    img=Image.new('RGBA',(1920,1080),(24,42,66,255))
    paste(img,asset('water-sunset.webp' if warm else 'water-day.webp'),-cam,-36)
    day={'Moonlight':.12,'Dusk':.52}.get(mode,1);night=(1-day)*150/255
    fs=sorted(frame['fish'],key=lambda f:f['z'])
    if density=='Low':fs=[f for f in fs if f['id']<12]
    if density=='High':
        # Density preview comes from a separate production-world export when available.
        high=ROOT/'docs/previews/high-frame.json'
        if high.exists():fs=sorted(json.loads(high.read_text())['fish'],key=lambda f:f['z'])
    def effects(lo,hi):
        for e in frame['effects']:
            if not lo<=e['z']<hi:continue
            if e['bubble']:
                if e['active']-48>=6:continue
                sc=.42+e['z']*.45;al=max(0,min(1,(e['y']-38)/50))*150/255
                paste(img,asset('bubble.png'),e['x']-cam*(.6+e['z']*.4),e['y'],sc,opacity=al)
            elif e['active']<24:
                sc=.25+e['z']*.4
                paste(img,asset('mote.png'),e['x']-cam*(.4+e['z']*.6),e['y'],sc,opacity=105/255)
    effects(0,.48)
    for f in fs:
        if f['z']<.48:fish(img,f,mode)
    paste(img,asset('reef-mid'+suf+'.webp'),-cam,124)
    for f in fs:
        if .48<=f['z']<.78:fish(img,f,mode)
    paste(img,asset('reef-front'+suf+'.webp'),-cam,124)
    cor=asset('soft-coral'+suf+'.png');phase=t/5.5%3
    for j in range(2):
        ix=(int(phase)+j)%3
        paste(img,cor.crop((ix*350,0,(ix+1)*350,370)),375-cam,569,opacity=phase%1 if j else 1-phase%1)
    phase=t%8*4;first=int(phase);blend=phase-first
    sand=asset('sand-caustics.png')
    for j in range(2):
        index=(first+j)%32
        piece=sand.crop(((index%4)*512,(index//4)*88,(index%4+1)*512,(index//4+1)*88))
        paste(img,piece,-cam,764,4,opacity=(blend if j else 1-blend)*225/255*day)
    for f in fs:
        if f['z']>=.78:fish(img,f,mode)
    effects(.48,1.01)
    for k in range(3):paste(img,asset('ray.png'),150+k*590+math.sin(t*.07+k)*24-cam*.25,-70,2,1.8,(65+18*math.sin(t*.13+k))/255*day)
    phase=t%8*4;first=int(phase);blend=phase-first
    surface=asset('surface-waves.png')
    for j in range(2):
        index=(first+j)%32
        piece=surface.crop(((index%8)*256,(index//8)*128,(index%8+1)*256,(index//8+1)*128))
        for tile in range(5):paste(img,piece,-512+tile*512-cam,-8,2,1,opacity=(blend if j else 1-blend)*(160+75*day)/255)
    if night:paste(img,Image.new('RGBA',img.size,(8,16,57,round(night*255))),0,0)
    warmth={'Sunset':38,'Dusk':20.9}.get(mode,0)
    if warmth:paste(img,Image.new('RGBA',img.size,(241,105,108,round(warmth))),0,0)
    return img.convert('RGB')
def make_previews():
    PRE.mkdir(parents=True,exist_ok=True)
    log=(ROOT/'work/frames.log').read_text();allframes=[json.loads(l[6:])for l in log.splitlines()if l.startswith('FRAME ')]
    high=[f for f in allframes if f['time']<0]
    if high:(PRE/'high-frame.json').write_text(json.dumps(high[0]))
    frames=[f for f in allframes if f['time']>=0]
    if len(frames)<601:raise RuntimeError('Export must complete all 601 production-world frames')
    (PRE/'frames.json').write_text(json.dumps(frames,separators=(',',':')))
    at=lambda t:min(frames,key=lambda f:abs(f['time']-t))
    frame=at(20)
    for mode in ['Sunset','Daylight','Dusk','Moonlight']:render(frame,mode).save(PRE/(mode.lower()+'.png'),optimize=True)
    render(frame,'Sunset','Low').save(PRE/'low-density.png')
    render(frame,'Sunset','High').save(PRE/'high-density.png')
    for t in [0,12,40,60]:render(at(t)).save(PRE/f'time-{t:02}.jpg',quality=94)
    # Explicit visual fixtures for occlusion (production projection and real asset masks).
    import copy
    f=copy.deepcopy(frame);f['fish']=[]
    for z,x,label in [(.25,270,'behind'),(.92,360,'front')]:
        sample=copy.deepcopy(frame['fish'][0]);sample.update(name='yellow_tang',z=z,sx=x,sy=670,scale=.56+.44*z,heading=0,phase=1,size=1.25)
        f['fish']=[sample];render(f).save(PRE/('occlusion-'+label+'.png'))
    sample.update(z=.95,sx=1000,sy=430,scale=.978,heading=math.pi/4,size=2.0)
    f['fish']=[sample];render(f).save(PRE/'three-quarter.png')
    print('Rendered sunset/day/dusk/moonlight, densities, occlusion pair, three-quarter and timeline frames')
if __name__=='__main__':make_previews()
