"""Build slim textured fish volumes and independently articulated pectoral fins.
All poses are rendered offline; runtime uses cropped atlas regions and no shaders.
"""
from pathlib import Path
import json, math, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from scipy.ndimage import distance_transform_edt, gaussian_filter
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'assets/source';OUT=ROOT/'roku/images'
SPECIES=[
 ('ocellaris_clownfish','Ocellaris clownfish',120,36,2.8,False,.28,1.8),
 ('yellow_tang','Yellow tang',155,49,2.0,False,.20,1.25),
 ('royal_gramma','Royal gramma',110,33,2.6,False,.216,1.6),
 ('emperor_angelfish','Emperor angelfish',190,44,1.8,False,.216,1.05),
 ('moorish_idol','Moorish idol',172,43,2.0,False,.168,1.3),
 ('green_chromis','Blue-green chromis',90,53,3.2,True,.24,2.0)]
# Texture-space fin outlines and the forward attachment point. Fish face right.
FIN_RIGS={
 'ocellaris_clownfish': ([(.69,.45),(.60,.43),(.49,.51),(.48,.65),(.58,.70),(.68,.60)],(.69,.48)),
 'yellow_tang': ([(.72,.48),(.65,.46),(.56,.54),(.58,.66),(.69,.61)],(.72,.49)),
 'royal_gramma': ([(.70,.46),(.64,.45),(.54,.57),(.59,.67),(.68,.59)],(.70,.48)),
 'emperor_angelfish': ([(.75,.57),(.68,.55),(.59,.66),(.65,.78),(.74,.68)],(.75,.58)),
 'moorish_idol': ([(.76,.64),(.69,.61),(.60,.68),(.64,.80),(.74,.73)],(.76,.65)),
 'green_chromis': ([(.69,.45),(.62,.46),(.53,.57),(.58,.70),(.67,.61)],(.69,.47))}
YAW_COUNT=64;UNIQUE_VIEWS=YAW_COUNT;BODY_BENDS=list(np.linspace(-.19,.19,4));FIN_ANGLES=list(np.linspace(0,.8,5))
VS='''#version 330
in vec3 pos;in vec2 uv;uniform float yaw;uniform float bend;
uniform float finAngle;uniform float finPass;uniform vec2 hinge;
out vec2 texuv;out float shade;
void main(){vec3 p=pos;
if(finPass>.5){float travel=max(0.0,hinge.x-p.x);float side=sign(p.z);p.x+=travel*(1.0-cos(finAngle));p.z+=side*sin(finAngle)*travel;}
float rear=max(0.0,.28-p.x);p.z+=bend*rear*rear;p.x+=bend*bend*rear*rear*rear*.85;
float c=cos(yaw),s=sin(yaw);vec3 q=vec3(p.x*c-p.z*s,p.y,p.x*s+p.z*c);
gl_Position=vec4(q.x*.9,q.y*.9,-q.z*.4,1);texuv=uv;shade=.86+.14*(p.y+1.0)/2.0;}
'''
FS='''#version 330
uniform sampler2D photo;uniform float depthOnly;in vec2 texuv;in float shade;out vec4 outcol;
void main(){vec4 c=texture(photo,texuv);if(c.a<.08)discard;outcol=depthOnly>.5?vec4(0):vec4(c.rgb*shade,c.a);}
'''

def prepare_texture(name):
    im=Image.open(SRC/(name+'.png')).convert('RGBA');im=im.crop(im.getchannel('A').getbbox())
    im=ImageEnhance.Color(im).enhance(.94);im=ImageEnhance.Contrast(im).enhance(1.02);im=ImageEnhance.Sharpness(im).enhance(1.22)
    outline,hinge=FIN_RIGS[name]
    mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon([(round(x*im.width),round(y*im.height))for x,y in outline],fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(max(.6,im.width*.002)))
    fin=im.copy();fin.putalpha(Image.fromarray(np.minimum(np.asarray(mask),np.asarray(im.getchannel('A')))))
    # Underpaint the old fin with nearby body scales so the moving fin is not duplicated.
    shift=max(2,round(im.height*.14));sample=im.copy()
    sample.paste(im.crop((0,0,im.width,im.height-shift)),(0,shift))
    body=Image.composite(sample,im,mask);body.putalpha(im.getchannel('A'))
    body.save(SRC/(name+'-texture.png'));fin.save(SRC/(name+'-pectoral.png'))
    return im,body,fin,mask,hinge

def make_mesh(name,thick):
    original,body,fin,finmask,hinge=prepare_texture(name)
    w=320;h=max(40,round(w*original.height/original.width))
    a=np.asarray(original.resize((w,h),Image.Resampling.LANCZOS).getchannel('A'))
    mask=a>50;dist=distance_transform_edt(mask);depth=gaussian_filter(dist,.65);depth=depth/max(depth.max(),1)*thick
    verts=[];uv=[];faces=[];ids={}
    for side in [-1,1]:
        for y in range(h):
            for x in range(w):
                if mask[y,x]:
                    ids[side,y,x]=len(verts)
                    verts.append([2*x/(w-1)-1,(1-2*y/(h-1))*h/w*.92,side*depth[y,x]])
                    uv.append([x/(w-1),1-y/(h-1)])
    for side in [-1,1]:
        for y in range(h-1):
            for x in range(w-1):
                keys=[(side,y,x),(side,y,x+1),(side,y+1,x),(side,y+1,x+1)]
                if all(k in ids for k in keys):
                    i,j,k,l=[ids[q]for q in keys];faces.extend([[i,k,j],[j,k,l]]if side==1 else [[i,j,k],[j,l,k]])
    for y in range(h-1):
        for x in range(w-1):
            for dy,dx in [(0,1),(1,0)]:
                if (1,y,x)not in ids or (1,y+dy,x+dx)not in ids:continue
                if dist[y,x]>1.5 and dist[y+dy,x+dx]>1.5:continue
                i=ids[1,y,x];j=ids[1,y+dy,x+dx];k=ids[-1,y,x];l=ids[-1,y+dy,x+dx];faces.extend([[i,j,k],[j,l,k]])
    v=np.array(verts,np.float32);uv=np.array(uv,np.float32);faces=np.array(faces,np.int32)
    fm=np.asarray(finmask.resize((w,h),Image.Resampling.LANCZOS));fins=[]
    for face in faces:
        points=v[face];ys=np.rint((1-points[:,1]/(.92*h/w))*.5*(h-1)).astype(int);xs=np.rint((points[:,0]+1)*.5*(w-1)).astype(int)
        if np.all(fm[np.clip(ys,0,h-1),np.clip(xs,0,w-1)]>20):fins.append(face)
    fv=v.copy();fv[:,2]+=np.sign(fv[:,2])*.012
    fins=np.array(fins,np.int32)
    np.savez_compressed(SRC/(name+'.npz'),vertices=v,uv=uv,faces=faces,fin_vertices=fv,fin_faces=fins,fin_hinge=np.array([hinge[0]*2-1,(1-hinge[1]*2)*h/w*.92]))
    return v,uv,faces,fv,fins,body,fin,hinge

def pack(images,width=1024):
    x=y=row_h=0;positions=[]
    for im,meta in images:
        if x+im.width+4>width:x=0;y+=row_h+4;row_h=0
        positions.append((x+2,y+2,im,meta));x+=im.width+4;row_h=max(row_h,im.height)
    height=y+row_h+4
    if height>2048:
        if width==2048:raise ValueError('Atlas exceeds Roku texture limit')
        return pack(images,2048)
    atlas=Image.new('RGBA',(width,height));frames=[]
    for x,y,im,meta in positions:
        atlas.paste(im,(x,y));frames.append(dict(meta,x=x,y=y,w=im.width,h=im.height))
    return atlas,frames

def cropped(shot,yaw,pose,fw,fh):
    alpha=shot.getchannel('A').point(lambda v:0 if v<4 else v);shot.putalpha(alpha)
    box=alpha.getbbox() or (fw//2,fh//2,fw//2+1,fh//2+1)
    x0,y0,x1,y1=box;box=(max(0,x0-2),max(0,y0-2),min(fw,x1+2),min(fh,y1+2))
    return shot.crop(box),{'yaw':yaw*360/YAW_COUNT,'pose':pose,'anchorX':fw/2-box[0],'anchorY':fh/2-box[1]}

def build(species_list=None):
    import moderngl
    ctx=moderngl.create_standalone_context(backend='egl');p=ctx.program(vertex_shader=VS,fragment_shader=FS)
    fw,fh=224,196;fbo=ctx.simple_framebuffer((fw*4,fh*4),components=4);fbo.use();ctx.enable(moderngl.DEPTH_TEST)
    contact=Image.new('RGB',(6*256,6*150),(27,45,58));atlasdata={}
    for row,(name,label,size,speed,beat,school,thick,finbeat)in enumerate(SPECIES if species_list is None else species_list):
        if name in ['ocellaris_clownfish','royal_gramma','green_chromis']:
            fw,fh=208,182
        else:
            fw,fh=224,196
        fbo.release();fbo=ctx.simple_framebuffer((fw*4,fh*4),components=4);fbo.use()
        v,uv,faces,fv,fins,body,fin,hinge=make_mesh(name,thick)
        vb=ctx.buffer(np.hstack((v,uv)).astype('f4').tobytes());ib=ctx.buffer(faces.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 2f','pos','uv')],ib)
        fb=ctx.buffer(np.hstack((fv,uv)).astype('f4').tobytes());fi=ctx.buffer(fins.tobytes());fvao=ctx.vertex_array(p,[(fb,'3f 2f','pos','uv')],fi)
        tex=ctx.texture(body.size,4,body.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());ftex=ctx.texture(fin.size,4,fin.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes())
        for t in [tex,ftex]:t.filter=(moderngl.LINEAR,moderngl.LINEAR)
        p['hinge'].value=(hinge[0]*2-1,0)
        def read():return Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
        shots=[];finshots=[]
        for yaw in range(UNIQUE_VIEWS):
            p['yaw'].value=yaw*2*math.pi/YAW_COUNT
            for pose,bend in enumerate(BODY_BENDS):
                p['bend'].value=bend;p['finPass'].value=0;p['finAngle'].value=0;p['depthOnly'].value=0;tex.use()
                fbo.color_mask=(True,True,True,True);fbo.clear(0,0,0,0,depth=1);vao.render();shot=read()
                shots.append(cropped(shot,yaw,pose,fw,fh))
                if pose==1 and yaw in [0,4,8,12,16,24]:
                    col=[0,4,8,12,16,24].index(yaw);thumb=shot.copy();thumb.thumbnail((250,142));contact.paste(thumb,(col*256,row*150),thumb)
            for pose,angle in enumerate(FIN_ANGLES):
                fbo.color_mask=(True,True,True,True);fbo.clear(0,0,0,0,depth=1)
                p['bend'].value=0;p['finPass'].value=0;p['depthOnly'].value=1;tex.use();vao.render()
                p['depthOnly'].value=0;p['finPass'].value=1;p['finAngle'].value=angle;ftex.use();fvao.render()
                finshots.append(cropped(read(),yaw,pose,fw,fh))
        atlas,unique=pack(shots)
        finshots=[(shot.resize((max(1,round(shot.width/2)),max(1,round(shot.height/2))),Image.Resampling.LANCZOS),dict(meta,anchorX=meta['anchorX']/2,anchorY=meta['anchorY']/2))for shot,meta in finshots]
        finatlas,unique_fins=pack(finshots,512)
        # All directions are actual upright renders. Runtime uses positive
        # scales on every device; no reflection/negative-scale driver path.
        frames=[dict(f,flipX=False)for f in unique]
        finframes=[dict(f,flipX=False)for f in unique_fins]
        view_widths=[max(f['w']-4 for f in frames[yaw*len(BODY_BENDS):(yaw+1)*len(BODY_BENDS)])for yaw in range(YAW_COUNT)]
        atlas.save(OUT/(name+'-atlas.png'),optimize=True);finatlas.save(OUT/(name+'-fins.png'),optimize=True)
        raw=ROOT/'work/fish-raw';raw.mkdir(parents=True,exist_ok=True)
        for suffix in ['-atlas.png','-fins.png']:shutil.copy2(OUT/(name+suffix),raw/(name+suffix))
        atlasdata[name]={'label':label,'image':'pkg:/images/'+name+'-atlas.webp','width':atlas.width,'height':atlas.height,'frameW':fw,'frameH':fh,'yawCount':YAW_COUNT,'viewWidths':view_widths,'poseCount':len(BODY_BENDS),'length':size*1.6,'renderLength':fw*.9,'speed':speed,'beat':beat,'school':school,'frames':frames,'finTextureScale':2,'finImage':'pkg:/images/'+name+'-fins.webp','finPoseCount':len(FIN_ANGLES),'finBeat':finbeat,'finFrames':finframes,'bodyHeightFactor':.92,'bodyThickness':thick,'collisionHalfWidth':max(max(f['anchorX'],f['w']-f['anchorX']) for f in frames+[dict(f,anchorX=f['anchorX']*2,anchorY=f['anchorY']*2,w=f['w']*2,h=f['h']*2)for f in finframes]),'collisionHalfHeight':max(max(f['anchorY'],f['h']-f['anchorY']) for f in frames+[dict(f,anchorX=f['anchorX']*2,anchorY=f['anchorY']*2,w=f['w']*2,h=f['h']*2)for f in finframes])}
        for obj in [vao,vb,ib,fvao,fb,fi,tex,ftex]:obj.release()
        print(name,len(frames),'body poses,',len(finframes),'independent fin poses; atlas',atlas.size,flush=True)
    (ROOT/'roku/scenes/species.json').write_text(json.dumps(atlasdata,indent=2))
    contact.save(ROOT/'docs/previews/fish-orientations.jpg',quality=94)
if __name__=='__main__':build()
