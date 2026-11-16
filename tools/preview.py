"""Render previews from actual BrightScript-exported world snapshots, not a Python fish brain."""
from pathlib import Path
import json, math, argparse, bisect
from PIL import Image,ImageChops,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];IM=ROOT/'roku/images';PRE=ROOT/'docs/previews'
SPEC=json.loads((ROOT/'roku/scenes/species.json').read_text())
TANK=json.loads((ROOT/'roku/scenes/tank.json').read_text())
WAVES=json.loads((ROOT/'roku/scenes/waves.json').read_text())
EEL=json.loads((ROOT/'roku/scenes/eel.json').read_text())
from surface_lighting import field
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
def fish(canvas,f,mode,t=0):
    sp=SPEC[f['name']]
    position=(f['heading']%(2*math.pi))*sp['yawCount']/(2*math.pi)
    lo=int(position)%sp['yawCount'];blend=position-int(position)
    width=sp['viewWidths'][lo]*(1-blend)+sp['viewWidths'][(lo+1)%sp['yawCount']]*blend
    im=Image.new('RGBA',(sp['frameW'],sp['frameH']))
    for part in ['body','tail','fin']:
        count=sp['poseCount']if part=='body'else sp['tailPoseCount']if part=='tail'else sp['finPoseCount']
        phase=f['phase']if part!='fin'else f.get('finPhase',f['phase']*.6)
        pose=int((math.sin(phase)+1)*.5*(count-1)+.5)
        view=int(position+.5)%sp['yawCount'];part_width=width;source_width=sp['viewWidths'][view]
        if part=='body' and 'bodyAngles'in sp:
            heading=f['heading']%(2*math.pi);lo=bisect.bisect_right(sp['bodyAngles'],heading)-1;hi=(lo+1)%sp['bodyYawCount']
            upper=sp['bodyAngles'][hi]if hi else 2*math.pi;u=(heading-sp['bodyAngles'][lo])/(upper-sp['bodyAngles'][lo])
            view=lo if u<.5 else hi;part_width=sp['bodyViewWidths'][lo]*(1-u)+sp['bodyViewWidths'][hi]*u;source_width=sp['bodyViewWidths'][view]
        atlas=asset(sp['image'if part=='body'else 'tailImage'if part=='tail'else 'finImage'].split('/')[-1])
        fr=sp['frames'if part=='body'else 'tailFrames'if part=='tail'else 'finFrames'][view*count+pose]
        layer=Image.new('RGBA',im.size)
        piece=atlas.crop((fr['x'],fr['y'],fr['x']+fr['w'],fr['y']+fr['h']))
        texture_scale=sp.get('finTextureScale',1)if part=='fin'else 1
        if texture_scale!=1:piece=piece.resize((piece.width*texture_scale,piece.height*texture_scale),Image.Resampling.LANCZOS)
        layer.alpha_composite(piece,(round(sp['frameW']/2-fr['anchorX']*texture_scale),round(sp['frameH']/2-fr['anchorY']*texture_scale)))
        width_scale=part_width/source_width
        layer=layer.resize((round(layer.width*width_scale),layer.height),Image.Resampling.LANCZOS)
        im.alpha_composite(layer,(round((im.width-layer.width)/2),0))
    haze=1-f['z'];tint=(255,int(239-haze*25),int(240-haze*10))if mode=='Sunset'else(int(255-haze*65),int(247-haze*32),255)
    day={'Moonlight':.12,'Dusk':.52}.get(mode,1)
    shade=1-float(field(f['x'],f['sy']+36,t))/255*.30*(.35+.65*day)
    tint=tuple(int(c*shade)for c in tint)
    im=ImageChops.multiply(im,Image.new('RGBA',im.size,(*tint,255)))
    sc=f['scale']*sp['length']/sp['renderLength']*f['size'];im=im.resize((max(1,round(im.width*sc)),max(1,round(im.height*sc))),Image.Resampling.LANCZOS)
    angle=f['pitch']*57.29578*(-1 if math.cos(f['heading'])<0 else 1)
    im=im.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    paste(canvas,im,f['sx']-im.width/2,f['sy']-im.height/2)

def eel_pose(t):
    q=(t+15)%31
    def ease(v):
        v=max(0,min(1,v));return v*v*v*(v*(v*6-15)+10)
    peek=ease((q-7)/7)if 7<=q<14 else 1 if 14<=q<20 else 1-ease((q-20)/8)if 20<=q<28 else 0
    return round(peek*64)

def render(frame,mode='Sunset',density='Medium'):
    cam=frame['camera'];t=frame.get('displayTime',frame['time']);warm=mode=='Sunset';suf='-sunset' if warm else ''
    img=Image.new('RGBA',(1920,1080),(24,42,66,255))
    paste(img,asset('water-sunset.webp' if warm else 'water-day.webp'),-cam,-36)
    floor=asset('seafloor-sunset.webp')
    if not warm:floor=ImageChops.multiply(floor,Image.new('RGBA',floor.size,(221,235,255,255)))
    paste(img,floor,-cam,920-36)
    day={'Moonlight':.12,'Dusk':.52}.get(mode,1);night=(1-day)*150/255
    fs=sorted(frame['fish'],key=lambda f:f['z'])
    if density=='Low':fs=[f for f in fs if f['id']<TANK['populations']['Low']]
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
    previous=0;fish_index=0
    for formation in TANK['formations']:
        depth=formation['z'];effects(previous,depth);previous=depth
        while fish_index<len(fs) and fs[fish_index]['z']<depth:
            fish(img,fs[fish_index],mode,t);fish_index+=1
        from formation_frames import frame as formation_frame
        if 'animation'in formation:
            view=round((math.sin((t%formation['animation']['period'])*2*math.pi/formation['animation']['period'])+1)*.5*(formation['frames']-1))
        else:view=0
        layer=formation_frame(formation,view,CACHE).resize((formation['width'],formation['height']),Image.Resampling.LANCZOS)
        offset=64+(cam-64)*formation['parallax']
        if mode!='Sunset':layer=ImageChops.multiply(layer,Image.new('RGBA',layer.size,(221,235,255,255)))
        strength=1 if 'animation'in formation else .35
        light=int(255*(1-float(field(formation['x']+formation['width']*.5,formation['y']+formation['height']*.45,t))/255*strength*(.35+.65*day)))
        layer=ImageChops.multiply(layer,Image.new('RGBA',layer.size,(light,light,light,255)))
        paste(img,layer,formation['x']-offset,formation['y']-36)
        if 'surfaceShadow'in formation:
            c=formation['surfaceShadow'];atlas=asset(c['image'].split('/')[-1]);phase=t%8*4;first=int(phase);blend=phase-first
            for j in range(2):
                i=(first+j)%32;x=i%c['columns']*c['width'];y=i//c['columns']*c['height'];part=atlas.crop((x,y,x+c['width'],y+c['height']))
                paste(img,part,-cam,-36,c['scale'],opacity=(blend if j else 1-blend)*.65*(.35+.65*day))
        if formation['id']=='connected-reef':
            fr=EEL['frames'][eel_pose(t)];atlas=asset(EEL['image'].split('/')[-1]);actor=atlas.crop((fr['x'],fr['y'],fr['x']+fr['w'],fr['y']+fr['h']))
            light=int(255*(1-float(field(773,858,t))/255*.30*(.35+.65*day)))
            actor=ImageChops.multiply(actor,Image.new('RGBA',actor.size,(light,light,light,255)))
            paste(img,actor,EEL['x']-cam,EEL['y']-36)
    phase=t%WAVES['period']*WAVES['frames']/WAVES['period'];first=int(phase);blend=phase-first
    for key,name in [('sand','sand-caustics.png'),('shadow','sand-wave-shadows.png')]:
        cfg=WAVES[key];sand=asset(name)
        for j in range(2):
            index=(first+j)%WAVES['frames'];x=index%cfg['columns']*cfg['width'];y=index//cfg['columns']*cfg['height']
            piece=sand.crop((x,y,x+cfg['width'],y+cfg['height']))
            opacity=225/255*day if key=='sand'else .25+.75*day
            paste(img,piece,cfg['x']-cam,cfg['y']-36,cfg['scale'],opacity=(blend if j else 1-blend)*opacity)
    for f in fs[fish_index:]:fish(img,f,mode,t)
    effects(previous,1.01)
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
    if len(frames)<21:raise RuntimeError('Export must complete at least 21 production-world frames')
    (PRE/'frames.json').write_text(json.dumps(frames,separators=(',',':')))
    at=lambda t:min(frames,key=lambda f:abs(f['time']-t))
    frame=at(1.5)
    for mode in ['Sunset','Daylight','Dusk','Moonlight']:render(frame,mode).save(PRE/(mode.lower()+'.png'),optimize=True)
    render(frame,'Sunset','Low').save(PRE/'low-density.png')
    render(frame,'Sunset','High').save(PRE/'high-density.png')
    for t in [0,1,2,3]:render(at(t)).save(PRE/f'time-{t:02}.jpg',quality=94)
    # Explicit visual fixtures for occlusion (production projection and real asset masks).
    import copy
    f=copy.deepcopy(frame);f['fish']=[]
    for z,x,label in [(.25,270,'behind'),(.92,360,'front')]:
        sample=copy.deepcopy(frame['fish'][0]);sample.update(name='yellow_tang',z=z,sx=x,sy=670,scale=.70+.30*z,heading=0,phase=1,size=1.25)
        f['fish']=[sample];render(f).save(PRE/('occlusion-'+label+'.png'))
    sample.update(z=.95,sx=1000,sy=430,scale=.978,heading=math.pi/4,size=2.0)
    f['fish']=[sample];render(f).save(PRE/'three-quarter.png')
    print('Rendered sunset/day/dusk/moonlight, densities, occlusion pair, three-quarter and timeline frames')
if __name__=='__main__':make_previews()
