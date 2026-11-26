"""Bake lateral 3D flex, slim anatomy and independent tail/fin poses.

Three complete mesh poses retain native four-layer blending. Model Y never
changes with swim phase. No runtime geometry or image slicing is required.
"""
import argparse,json,math
import numpy as np
from PIL import Image
import moderngl,imagequant
import fish_mesh as fm
from fish_anatomy import WIDTHS,AMPLITUDE,START,TURN_AMPLITUDE,TURN_START,rescale,curve
from fish_eyes import build as build_eyes
from dense_turns import angles
from tail_rig import build as bind
ROOT=fm.ROOT
def swim_angles():
    # Retain all 25 dense frontal views. Profile views blend over a wider arc;
    # fewer redundant side images make room for genuine eyes and C-turn poses.
    return [a for a in angles() if 78.75<=a<=101.25 or a in [0,22.5,45,67.5,112.5,135,157.5,180]]
TURN_ANGLES=sorted(set(swim_angles()+[56.25,73.125,106.875,123.75]))
VS=fm.VS.replace('uniform float finAngle;', 'uniform float swim;uniform float turning;uniform vec2 extent;uniform float finAngle;')
VS=VS.replace('float c=cos(yaw)', '''float u=clamp(((extent.y-p.x)/(extent.y-extent.x)-0.28)/0.72,0.0,1.0);
float amount=swim*(extent.y-extent.x);
p.z+=amount*u*u*sin(4.71238898*u);
float cshape=clamp(((extent.y-p.x)/(extent.y-extent.x)-0.15)/0.85,0.0,1.0);
p.z+=turning*(extent.y-extent.x)*cshape*cshape;
float slope=-amount/((extent.y-extent.x)*0.72)*(2.0*u*sin(4.71238898*u)+4.71238898*u*u*cos(4.71238898*u))-turning*2.0*cshape/0.85;
float c=cos(yaw)''')
VS=VS.replace('normal.x*c-normal.z*s,normal.y,normal.x*s+normal.z*c',
              '(normal.x-slope*normal.z)*c-normal.z*s,normal.y,(normal.x-slope*normal.z)*s+normal.z*c')
def save(shots,path,colors,width=2048):
    atlas,frames=fm.pack(shots,width)
    imagequant.quantize_pil_image(atlas,max_colors=colors,dithering_level=0,max_quality=95).convert('RGBA').save(path,lossless=True,quality=100,method=6,exact=True)
    return atlas.size,frames
def directions(frames,count,yaws,unique,reverse=False):
    lookup={round(a,6):i for i,a in enumerate(unique)};result=[]
    for yaw in yaws:
        back=yaw>180;view=lookup[round(min(yaw,360-yaw),6)]
        for pose in range(count):
            source=count-1-pose if reverse and back else pose
            result.append(dict(frames[view*count+source],yaw=yaw,pose=pose,flipX=False))
    return result
def build(names=None,supersample=2,body_only=False):
    path=ROOT/'roku/scenes/species.json';species=json.loads(path.read_text())
    restpath=fm.SRC/'fish-rest/species.json';rest=json.loads(restpath.read_text())
    audit={};ctx=moderngl.create_standalone_context(backend='egl');ctx.enable(moderngl.DEPTH_TEST)
    program=ctx.program(vertex_shader=VS,fragment_shader=fm.FS)
    dense=swim_angles();yaws=dense+[360-a for a in reversed(dense[1:-1])]
    coarse=[i*360/fm.YAW_COUNT for i in range(fm.UNIQUE_VIEWS)]
    for name,sp in species.items():
        if names and name not in names:continue
        meshpath=fm.SRC/(name+'.npz')
        with np.load(meshpath) as source:data={key:source[key].copy() for key in source.files}
        before=float(np.ptp(data['vertices'][:,2])/np.ptp(data['vertices'][:,0]));factor=rescale(data,name)
        eye_info=build_eyes(data,name,Image.open(fm.SRC/(name+'-texture.png')).convert('RGBA'),fm.SRC/(name+'-eyes.png'))
        np.savez_compressed(meshpath,**data)
        v=data['vertices'];span=float(np.ptp(v[:,0]));extent=(float(v[:,0].min()),float(v[:,0].max()))
        def vao(vertices,faces):
            vb=ctx.buffer(np.hstack((vertices,data['uv'],data['normals'])).astype('f4').tobytes());ib=ctx.buffer(faces.tobytes())
            return ctx.vertex_array(program,[(vb,'3f 2f 3f','pos','uv','normal')],ib),vb,ib
        body,bv,bi=vao(v,data['body_faces']);tail,tv,ti=vao(v,data['tail_faces']);fin,fv,fi=vao(data['fin_vertices'],data['fin_faces'])
        ev=ctx.buffer(np.hstack((data['eye_vertices'],data['eye_uv'],data['eye_normals'])).astype('f4').tobytes());ei=ctx.buffer(data['eye_faces'].tobytes())
        eyes=ctx.vertex_array(program,[(ev,'3f 2f 3f','pos','uv','normal')],ei)
        def texture(suffix):
            im=Image.open(fm.SRC/(name+suffix)).convert('RGBA')
            t=ctx.texture(im.size,4,im.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());t.filter=(moderngl.LINEAR,moderngl.LINEAR);return t
        skin=texture('-texture.png');fintex=texture('-pectoral.png');eyetex=texture('-eyes.png')
        fw,fh=sp['frameW'],sp['frameH'];fbo=ctx.simple_framebuffer((fw*supersample,fh*supersample),components=4);fbo.use()
        program['extent'].value=extent;program['hinge'].value=tuple(data['fin_hinge'])
        program['tailRoot'].value=fm.TAIL_RIGS[name][0]*2-1
        def reset(yaw):
            fbo.clear(0,0,0,0,depth=1);skin.use()
            for key,value in dict(yaw=math.radians(yaw),bend=0,finPass=0,finAngle=0,depthOnly=0,swim=0,turning=0).items():program[key].value=value
        def render_body():
            skin.use();body.render();eyetex.use();eyes.render();skin.use()
        def read(yaw,pose):
            im=Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
            piece,meta=fm.cropped(im,yaw,pose,fw,fh);return piece,dict(meta,yaw=yaw)
        shots=[]
        for yaw in dense:
            for pose in range(3):
                reset(yaw);program['swim'].value=(pose-1)*AMPLITUDE;render_body();shots.append(read(yaw,pose))
        turn_angles=TURN_ANGLES;turn_yaws=turn_angles+[360-a for a in reversed(turn_angles[1:-1])]
        turn_shots=[];turn_neutral=[];turn_sources=[];turn_weights=[]
        for yaw in turn_angles:
            if yaw<=45 or yaw>=135:
                source=dense.index(yaw)*3+1
                turn_neutral.append(max(1,shots[source][0].width-4))
                turn_sources.extend([source,source]);turn_weights.append(0)
                continue
            reset(yaw);render_body();piece,meta=read(yaw,1);turn_neutral.append(max(1,piece.width-4))
            turn_weights.append(1)
            for pose in range(2):
                turn_sources.append(len(dense)*3+len(turn_shots))
                reset(yaw);program['turning'].value=(pose*2-1)*TURN_AMPLITUDE;render_body();turn_shots.append(read(yaw,pose))
        shots+=turn_shots
        colors=sp.get('bodyPaletteColors',96 if name=='mandarin_dragonet' else 64)
        size,frames=save(shots,ROOT/'roku'/sp['image'][5:],colors)
        sp['bodyPaletteColors']=colors
        bodyframes=directions(frames[:len(dense)*3],3,yaws,dense,True)
        turnframes=directions([frames[i]for i in turn_sources],2,turn_yaws,turn_angles,True)
        turn_widths=[]
        for yaw in turn_yaws:
            turn_widths.append(turn_neutral[turn_angles.index(round(min(yaw,360-yaw),6))])
        sp.update(turnOffset=len(bodyframes),turnViews={'bodyAngles':[math.radians(yaw) for yaw in turn_yaws],'bodyYawCount':len(turn_yaws),'bodyViewWidths':turn_widths,'bendWeights':[turn_weights[turn_angles.index(round(min(yaw,360-yaw),6))]for yaw in turn_yaws]},bodyTurnAmplitude=TURN_AMPLITUDE,turnStart=TURN_START,eyes=eye_info)
        neutral=[shots[i*3+1] for i in range(len(dense))]
        nsize,nframes=save(neutral,fm.SRC/'fish-rest'/(name+'.webp'),96,1024)
        neutralframes=directions(nframes,1,yaws,dense)
        if body_only:
            sp.update(frames=bodyframes+turnframes,width=size[0],height=size[1],bodySwimAmplitude=AMPLITUDE,swimStart=START,bodyAngles=[math.radians(yaw) for yaw in yaws],bodyYawCount=len(yaws),bodyViewWidths=[max(1,f['w']-4) for f in neutralframes],finSwimOffset=float(span*AMPLITUDE*curve((extent[1]-float(data['fin_hinge'][0]))/span)*fw*.45))
            rest[name]=dict(sp,frames=neutralframes,width=nsize[0],height=nsize[1],poseCount=1);rest[name].pop('bodyRenderMode',None)
            for key in ['turnCoreImage','turnCoreFrames','turnCoreScale','turnCoreColor']:rest[name].pop(key,None)
            for obj in [body,bv,bi,tail,tv,ti,fin,fv,fi,eyes,ev,ei,skin,fintex,eyetex,fbo]:obj.release()
            print(name,'body-only',size,flush=True)
            continue
        tailshots=[];finshots=[];coarsebody=[]
        for yaw in coarse:
            reset(yaw);render_body();im,meta=read(yaw,1)
            coarsebody.append(dict(meta,w=im.width,h=im.height))
            for pose,bend in enumerate(fm.BODY_BENDS):
                reset(yaw);program['depthOnly'].value=1;render_body()
                program['depthOnly'].value=0;program['bend'].value=bend;tail.render();tailshots.append(read(yaw,pose))
            for pose,angle in enumerate(fm.FIN_ANGLES):
                reset(yaw);program['depthOnly'].value=1;render_body()
                program['depthOnly'].value=0;program['finPass'].value=1;program['finAngle'].value=angle;fintex.use();fin.render()
                im,meta=read(yaw,pose);im=im.resize((max(1,round(im.width/2)),max(1,round(im.height/2))),Image.Resampling.LANCZOS)
                finshots.append((im,dict(meta,anchorX=meta['anchorX']/2,anchorY=meta['anchorY']/2)))
        _,tails=save(tailshots,ROOT/'roku'/sp['tailImage'][5:],sp.get('tailPaletteColors',80),1024)
        _,fins=save(finshots,ROOT/'roku'/sp['finImage'][5:],sp.get('finPaletteColors',64),512)
        coarseall=[i*360/fm.YAW_COUNT for i in range(fm.YAW_COUNT)]
        tailframes=directions(tails,4,coarseall,coarse,True);finframes=directions(fins,5,coarseall,coarse)
        bw=[max(1,f['w']-4) for f in neutralframes];fullwidth=[]
        for i,yaw in enumerate(coarseall):
            b=coarsebody[min(i,fm.YAW_COUNT-i)];parts=[b]+tailframes[i*4:(i+1)*4]
            fullwidth.append(max(1,max(f['w']-f['anchorX'] for f in parts)+max(f['anchorX'] for f in parts)-4))
        hinge=float(data['fin_hinge'][0]);u=(extent[1]-hinge)/span
        turn_u=max(0,min(1,(u-TURN_START)/(1-TURN_START)))
        sp.update(frames=bodyframes+turnframes,poseCount=3,width=size[0],height=size[1],bodyRenderMode='whole-swim',swimAxis='lateral',bodySwimAmplitude=AMPLITUDE,swimStart=START,swimSpan=span,swimExtent=list(extent),finSwimOffset=float(span*AMPLITUDE*curve(u)*fw*.45),finTurnOffset=float(span*TURN_AMPLITUDE*turn_u*turn_u*fw*.45),bodyAngles=[math.radians(yaw) for yaw in yaws],bodyYawCount=len(yaws),bodyViewWidths=bw,tailFrames=tailframes,finFrames=finframes,viewWidths=fullwidth,modelWidthRatio=WIDTHS[name],meshRevision=5)
        sp['bodyThickness']=max(sp['bodyThickness'],float((np.abs(v[:,2]).max()+max(AMPLITUDE,TURN_AMPLITUDE)*span)*1.1))
        allframes=bodyframes+turnframes+tailframes+[dict(f,w=f['w']*2,h=f['h']*2,anchorX=f['anchorX']*2,anchorY=f['anchorY']*2) for f in finframes]
        sp['collisionHalfWidth']=max(sp['collisionHalfWidth'],max(max(f['anchorX'],f['w']-f['anchorX']) for f in allframes))
        sp['collisionHalfHeight']=max(sp['collisionHalfHeight'],max(max(f['anchorY'],f['h']-f['anchorY']) for f in allframes))
        rest[name]=dict(sp,frames=neutralframes,width=nsize[0],height=nsize[1],poseCount=1);rest[name].pop('bodyRenderMode',None)
        for key in ['turnCoreImage','turnCoreFrames','turnCoreScale','turnCoreColor']:rest[name].pop(key,None)
        audit[name]={'before_width_length':round(before,5),'after_width_length':round(float(np.ptp(v[:,2])/span),5),'target':WIDTHS[name],'z_scale':round(factor,5)}
        for obj in [body,bv,bi,tail,tv,ti,fin,fv,fi,eyes,ev,ei,skin,fintex,eyetex,fbo]:obj.release()
        print(name,'3D lateral poses',size,'width/length',audit[name]['after_width_length'],flush=True)
    path.write_text(json.dumps(species,indent=2));restpath.write_text(json.dumps(rest,indent=2));bind()
    if audit:(ROOT/'work/anatomy-bake.json').write_text(json.dumps(audit,indent=2)+'\n')
    from catalog import catalog
    catalog()
    from turn_cores import build as build_cores
    build_cores(names)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--species',nargs='+',choices=list(WIDTHS));parser.add_argument('--supersample',type=int,default=2);parser.add_argument('--body-only',action='store_true')
    args=parser.parse_args();build(args.species,args.supersample,args.body_only)
