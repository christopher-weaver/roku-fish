"""Render previews from actual BrightScript-exported world snapshots, not a Python fish brain."""
from pathlib import Path
import json, math, argparse, bisect
import numpy as np
from scipy.ndimage import map_coordinates
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
        pose_value=(math.sin(phase)+1)*.5*(count-1);pose=int(pose_value+.5)
        view=int(position+.5)%sp['yawCount'];part_width=width;source_width=sp['viewWidths'][view]
        if part=='body' and 'bodyAngles'in sp:
            heading=f['heading']%(2*math.pi);lo=bisect.bisect_right(sp['bodyAngles'],heading)-1;hi=(lo+1)%sp['bodyYawCount']
            upper=sp['bodyAngles'][hi]if hi else 2*math.pi;u=(heading-sp['bodyAngles'][lo])/(upper-sp['bodyAngles'][lo])
            view=lo if u<.5 else hi;part_width=sp['bodyViewWidths'][lo]*(1-u)+sp['bodyViewWidths'][hi]*u;source_width=sp['bodyViewWidths'][view]
        atlas=asset(sp['image'if part=='body'else 'tailImage'if part=='tail'else 'finImage'].split('/')[-1])
        samples=[(view,1.)]
        if part=='body' and 'bodyAngles'in sp:samples=[(lo,1.),(hi,u)]
        for source_view,opacity in samples:
            fr=sp['frames'if part=='body'else 'tailFrames'if part=='tail'else 'finFrames'][source_view*count+pose]
            layer=Image.new('RGBA',im.size);piece=atlas.crop((fr['x'],fr['y'],fr['x']+fr['w'],fr['y']+fr['h']))
            texture_scale=sp.get('finTextureScale',1)if part=='fin'else 1
            anchor_x,anchor_y=fr['anchorX'],fr['anchorY']
            if part!='body':
                metadata=sp['tailFrames'if part=='tail'else 'finFrames'];first=int(pose_value);second=min(first+1,count-1);blend_pose=pose_value-first;fa,fb=metadata[source_view*count+first],metadata[source_view*count+second]
                if min(fa['w'],fb['w'],fr['w'],fa['h'],fb['h'],fr['h'])>=6:
                    tw=fa['w']+(fb['w']-fa['w'])*blend_pose;th=fa['h']+(fb['h']-fa['h'])*blend_pose
                    piece=piece.resize((max(1,round(tw)),max(1,round(th))),Image.Resampling.LANCZOS)
                    anchor_x=fa['anchorX']+(fb['anchorX']-fa['anchorX'])*blend_pose;anchor_y=fa['anchorY']+(fb['anchorY']-fa['anchorY'])*blend_pose
            if texture_scale!=1:piece=piece.resize((piece.width*texture_scale,piece.height*texture_scale),Image.Resampling.LANCZOS)
            layer.alpha_composite(piece,(round(sp['frameW']/2-anchor_x*texture_scale),round(sp['frameH']/2-anchor_y*texture_scale)))
            source_width=sp['bodyViewWidths'][source_view]if part=='body'else sp['viewWidths'][source_view]
            width_scale=part_width/source_width;layer=layer.resize((round(layer.width*width_scale),layer.height),Image.Resampling.LANCZOS)
            if opacity<1:layer.putalpha(layer.getchannel('A').point(lambda v:round(v*opacity)))
            im.alpha_composite(layer,(round((im.width-layer.width)/2),0))
    haze=1-f['z'];tint=(255,int(239-haze*25),int(240-haze*10))if mode=='Sunset'else(int(255-haze*65),int(247-haze*32),255)
    day={'Night':.06,'Moonlight':.12,'Dusk':.52}.get(mode,1)
    shade=1-float(field(f['x'],f['sy']+36,t))/255*.30*(.35+.65*day)
    tint=tuple(int(c*shade)for c in tint)
    im=ImageChops.multiply(im,Image.new('RGBA',im.size,(*tint,255)))
    sc=f['scale']*sp['length']/sp['renderLength']*f['size'];im=im.resize((max(1,round(im.width*sc)),max(1,round(im.height*sc))),Image.Resampling.LANCZOS)
    yy,xx=np.mgrid[:im.height,:im.width];length=sp['frameW']*.9*sc;sign=1 if math.cos(f['heading'])>=0 else -1;u=np.clip(.5-sign*(xx-im.width/2)/length,0,1);effort=min(1,f.get('speed',sp['speed']*.6)/sp['speed']);amp=sp['length']*f['size']*f['scale']*.012*(.25+.75*effort)*abs(math.cos(f['heading']));bend=amp*u*u*np.sin(f['phase']-u*2*math.pi);pixels=np.asarray(im);im=Image.fromarray(np.stack([map_coordinates(pixels[:,:,c],[yy-bend,xx],order=1,mode='constant',cval=0)for c in range(4)],axis=2))
    angle=f['pitch']*57.29578*(-1 if math.cos(f['heading'])<0 else 1)
    im=im.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    paste(canvas,im,f['sx']-im.width/2,f['sy']-im.height/2)

def clam_opening(t):
    q=(t+7)%47
    def ease(v):
        v=max(0,min(1,v));return v*v*v*(v*(v*6-15)+10)
    return 0 if q<8 or q>=27 else ease((q-8)/5)if q<13 else 1 if q<22 else 1-ease((q-22)/5)

def eel_pose(t):
    q=(t+15)%31
    def ease(v):
        v=max(0,min(1,v));return v*v*v*(v*(v*6-15)+10)
    peek=ease((q-7)/7)if 7<=q<14 else 1 if 14<=q<20 else 1-ease((q-20)/8)if 20<=q<28 else 0
    from cave_geometry import expression_frame
    return expression_frame(t,peek)

def render(frame,mode='Sunset',density='Medium'):
    cam=frame['camera'];t=frame.get('displayTime',frame['time']);warm=mode=='Sunset';suf='-sunset' if warm else ''
    img=Image.new('RGBA',(1920,1080),(24,42,66,255))
    paste(img,asset('water-sunset.webp' if warm else 'water-day.webp'),-cam,-36)
    day={'Night':.06,'Moonlight':.12,'Dusk':.52}.get(mode,1)
    phase=t%8*4;first=int(phase);blend=phase-first
    surface=asset('surface-waves.png')
    for j in range(2):
        index=(first+j)%32
        piece=surface.crop(((index%8)*256,(index//8)*128,(index%8+1)*256,(index//8+1)*128))
        for tile in range(4):paste(img,piece,-1024+tile*1024-cam,-8,4,2,opacity=(blend if j else 1-blend)*(205+50*day)/255)
    floor=asset('seafloor-sunset.webp')
    if not warm:floor=ImageChops.multiply(floor,Image.new('RGBA',floor.size,(221,235,255,255)))
    paste(img,floor,-cam,920-36)
    day={'Night':.06,'Moonlight':.12,'Dusk':.52}.get(mode,1);night=(1-day)*150/255
    staged=[f for f in frame['fish']if f.get('emerging')];fs=sorted([f for f in frame['fish']if not f.get('emerging')],key=lambda f:f['z'])
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
        if formation['id']=='clam':view=round(frame.get('clam',{}).get('opening',clam_opening(t))*64)
        layer=formation_frame(formation,view,CACHE).resize((formation['width'],formation['height']),Image.Resampling.LANCZOS)
        offset=64+(cam-64)*formation['parallax']
        if mode!='Sunset':layer=ImageChops.multiply(layer,Image.new('RGBA',layer.size,(221,235,255,255)))
        strength=0 if 'animation'in formation else .35
        light=int(255*(1-float(field(formation['x']+formation['width']*.5,formation['y']+formation['height']*.45,t))/255*strength*(.35+.65*day)))
        layer=ImageChops.multiply(layer,Image.new('RGBA',layer.size,(light,light,light,255)))
        paste(img,layer,formation['x']-offset,formation['y']-36)
        if formation['id']=='clam':
            c=frame.get('clam',{});event=c.get('event',0);enabled=c.get('enabled',True)
            if enabled and event==0:paste(img,asset('clam-pearl.png'),1075-cam,960,.5)
            if enabled and event==1:
                for e in c.get('bubbles',[]):
                    age=max(0,t-e['born'])if c.get('released')else 0
                    y=e['originY']-age*e['speed'];x=e['x']+(math.sin(age*1.3+e['phase'])-math.sin(e['phase']))*6-cam
                    if y>45:paste(img,asset('bubble.png'),x,y,e['scale'],opacity=180/255*min(1,(y-45)/45))
            for child in staged:fish(img,child,mode,t)
            if enabled and (event in [0,1]or staged):
                from formation_frames import front_frame
                lip=front_frame(formation,view,CACHE).resize((formation['width'],formation['height']),Image.Resampling.LANCZOS)
                if not warm:lip=ImageChops.multiply(lip,Image.new('RGBA',lip.size,(221,235,255,255)))
                paste(img,lip,formation['x']-offset,formation['y']-36)
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
    if night:paste(img,Image.new('RGBA',img.size,(8,16,57,205 if mode=='Night'else round(night*255))),0,0)
    warmth={'Sunset':38,'Dusk':20.9}.get(mode,0)
    if warmth:paste(img,Image.new('RGBA',img.size,(241,105,108,round(warmth))),0,0)
    if mode=='Night':
        for site in frame.get('bioluminescence',[]):
            sc=site['size'];pulse=.72+.28*math.sin(t*.32+site['phase']);glow=ImageChops.multiply(asset('bioluminescence.png'),Image.new('RGBA',(32,32),(52,255,202,255)))
            paste(img,glow,site['x']-cam-16*sc,site['y']-36-16*sc,sc,opacity=190/255*pulse)
        for e in frame['effects'][:12]:
            glow=ImageChops.multiply(asset('bioluminescence.png'),Image.new('RGBA',(32,32),(70,214,255,255)))
            paste(img,glow,e['x']-cam*(.4+e['z']*.6)-5,e['y']-5,.32,opacity=170/255*(.55+.45*math.sin(t*.7+e.get('phase',0)*4)))
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
    for mode in ['Sunset','Daylight','Dusk','Moonlight','Night']:render(frame,mode).save(PRE/(mode.lower()+'.png'),optimize=True)
    import copy
    pearl=copy.deepcopy(frame);pearl['displayTime']=9;pearl['clam']['event']=0;pearl['clam']['opening']=1;pearl['fish']=[f for f in pearl['fish']if not f.get('emerging')];render(pearl).save(PRE/'clam-pearl.png',optimize=True)
    bubble=copy.deepcopy(frame);bubble['displayTime']=12;bucket=bubble['clam'];bucket.update(event=1,opening=1,released=True);bubble['fish']=[f for f in bubble['fish']if not f.get('emerging')];
    for i,e in enumerate(bubble['clam']['bubbles']):e['born']=7+i*.14
    render(bubble).save(PRE/'clam-bubbles.png',optimize=True)
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
