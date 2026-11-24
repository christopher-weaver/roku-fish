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
 ('green_chromis','Blue-green chromis',90,53,3.2,True,.24,2.0),
 ('blue_tang','Regal blue tang',165,46,2.1,False,.20,1.4),
 ('copperband_butterflyfish','Copperband butterflyfish',155,37,1.9,False,.17,1.2),
 ('banggai_cardinalfish','Banggai cardinalfish',120,29,2.4,False,.18,1.5),
 ('mandarin_dragonet','Mandarin dragonet',115,25,2.2,False,.24,1.7)]
# Texture-space fin outlines and the forward attachment point. Fish face right.
FIN_RIGS={
 'ocellaris_clownfish': ([(.69,.45),(.60,.43),(.49,.51),(.48,.65),(.58,.70),(.68,.60)],(.69,.48)),
 'yellow_tang': ([(.72,.48),(.65,.46),(.56,.54),(.58,.66),(.69,.61)],(.72,.49)),
 'royal_gramma': ([(.70,.46),(.64,.45),(.54,.57),(.59,.67),(.68,.59)],(.70,.48)),
 'emperor_angelfish': ([(.75,.57),(.68,.55),(.59,.66),(.65,.78),(.74,.68)],(.75,.58)),
 'moorish_idol': ([(.76,.64),(.69,.61),(.60,.68),(.64,.80),(.74,.73)],(.76,.65)),
 'green_chromis': ([(.69,.45),(.62,.46),(.53,.57),(.58,.70),(.67,.61)],(.69,.47))}
FIN_RIGS.update({
 'blue_tang': ([(.75,.46),(.68,.43),(.57,.49),(.62,.69),(.72,.65)],(.75,.47)),
 'copperband_butterflyfish': ([(.70,.48),(.64,.45),(.52,.48),(.52,.64),(.67,.65)],(.70,.49)),
 'banggai_cardinalfish': ([(.76,.55),(.68,.53),(.56,.63),(.62,.76),(.73,.67)],(.76,.56)),
 'mandarin_dragonet': ([(.74,.53),(.65,.53),(.49,.69),(.53,.92),(.74,.97),(.82,.81)],(.74,.54))})
# Caudal peduncle cut in normalized source space. The idol's dorsal streamer
# remains on the body even where it extends behind the tail attachment.
TAIL_RIGS={name:(.24,0,1)for name,*_ in SPECIES}
TAIL_RIGS.update(moorish_idol=(.27,.42,.91),blue_tang=(.25,0,1),
 copperband_butterflyfish=(.11,.32,.78),banggai_cardinalfish=(.35,.23,.76),
 mandarin_dragonet=(.29,.32,.91))
YAW_COUNT=64;UNIQUE_VIEWS=YAW_COUNT//2+1;BODY_BENDS=list(np.linspace(-.19,.19,4));FIN_ANGLES=list(np.linspace(0,.8,5))
VS='''#version 330
in vec3 pos;in vec2 uv;in vec3 normal;uniform float yaw;uniform float bend;uniform float tailRoot;
uniform float finAngle;uniform float finPass;uniform vec2 hinge;
out vec2 texuv;out float shade;
void main(){vec3 p=pos;
if(finPass>.5){float travel=max(0.0,hinge.x-p.x);float side=sign(p.z);p.x+=travel*(1.0-cos(finAngle));p.z+=side*sin(finAngle)*travel;}
float rear=max(0.0,tailRoot-p.x);p.z+=bend*rear*rear;p.x+=bend*bend*rear*rear*rear*.85;
float c=cos(yaw),s=sin(yaw);vec3 q=vec3(p.x*c-p.z*s,p.y,p.x*s+p.z*c);
gl_Position=vec4(q.x*.9,q.y*.9,-q.z*.4,1);texuv=uv;
vec3 n=normalize(vec3(normal.x*c-normal.z*s,normal.y,normal.x*s+normal.z*c));
shade=.83+.17*max(0.0,dot(n,normalize(vec3(-.25,.65,1.0))));}
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
    from skin_repair import repair
    body=repair(im,mask)
    body=wrap_texture(body,opaque=True)
    fin=wrap_texture(fin,opaque=False)
    body.save(SRC/(name+'-texture.png'));fin.save(SRC/(name+'-pectoral.png'))
    return im,body,fin,mask,hinge

def wrap_texture(image,opaque):
    """Bleed interior RGB through the outline; geometry owns body coverage.

    Photograph cutouts contain dark/transparent fringe pixels. Sampling those
    on a sidewall draws a black belt at head-on angles even on a closed mesh.
    """
    rgba=np.array(image);alpha=rgba[:,:,3];distance=distance_transform_edt(alpha>230)
    width=max(2,image.width*.007)
    safe=distance>=width
    if not safe.any():safe=alpha>200
    _,nearest=distance_transform_edt(~safe,return_indices=True)
    donor=rgba[nearest[0],nearest[1],:3].astype(float)
    blend=np.clip(distance/width,0,1)[:,:,None]
    rgba[:,:,:3]=np.uint8(rgba[:,:,:3]*blend+donor*(1-blend))
    if opaque:rgba[:,:,3]=255
    return Image.fromarray(rgba)

def closed_shell(mask,depth):
    """Two sampled surfaces joined by one smooth, manifold rounded perimeter."""
    h,w=mask.shape;cells=mask[:-1,:-1]&mask[:-1,1:]&mask[1:,:-1]&mask[1:,1:]
    corners=np.zeros((h,w),bool)
    for dy,dx in [(0,0),(0,1),(1,0),(1,1)]:corners[dy:dy+h-1,dx:dx+w-1]|=cells
    yy,xx=np.nonzero(corners);ids=np.full((h,w),-1,dtype='i4');ids[yy,xx]=np.arange(len(xx))
    padded=np.pad(cells,1);tl=padded[:h,:w];tr=padded[:h,1:w+1];bl=padded[1:h+1,:w];br=padded[1:h+1,1:w+1]
    ay,ax=np.nonzero((tl&br&~tr&~bl)|(tr&bl&~tl&~br));lower=ids.copy();lower[ay,ax]=len(xx)+np.arange(len(ax))
    xx=np.concatenate([xx,ax]);yy=np.concatenate([yy,ay]);count=len(xx)
    front=np.column_stack([2*xx/(w-1)-1,(1-2*yy/(h-1))*h/w*.92,depth[yy,xx]]).astype('f4')
    coords=np.column_stack([xx/(w-1),1-yy/(h-1)]).astype('f4')
    y,x=np.nonzero(cells);a=lower[y,x];b=lower[y,x+1];c=ids[y+1,x];d=ids[y+1,x+1]
    top=np.vstack([np.column_stack([a,c,b]),np.column_stack([b,c,d])]).astype('i4')
    edges=np.concatenate([top[:,[0,1]],top[:,[1,2]],top[:,[2,0]]]);ordered=np.sort(edges,axis=1)
    _,inverse,counts=np.unique(ordered,axis=0,return_inverse=True,return_counts=True)
    boundary=edges[counts[inverse]==1];rim=np.unique(boundary)
    tangent=front[boundary[:,1],:2]-front[boundary[:,0],:2]
    outward=np.column_stack([tangent[:,1],-tangent[:,0]]);outward/=np.maximum(np.linalg.norm(outward,axis=1)[:,None],1e-8)
    direction=np.zeros((count,2),dtype='f4')
    for i in range(2):np.add.at(direction,boundary[:,i],outward)
    direction/=np.maximum(np.linalg.norm(direction,axis=1)[:,None],1e-8)
    back=front.copy();back[:,2]*=-1
    vertices=[front,back];uvs=[coords,coords];faces=[top,top[:,::-1]+count]
    previous=np.arange(count);offset=count*2
    # Five intermediate rings remove the flat dark join between the two halves.
    for theta in np.linspace(0,np.pi,7)[1:]:
        if theta==np.pi:current=np.arange(count)+count
        else:
            ring=front[rim].copy();ring[:,:2]+=direction[rim]*np.minimum(front[rim,2:3],.010)*np.sin(theta);ring[:,2]*=np.cos(theta)
            vertices.append(ring);uvs.append(coords[rim]);current=np.full(count,-1,dtype='i4');current[rim]=offset+np.arange(len(rim));offset+=len(rim)
        a=previous[boundary[:,0]];b=previous[boundary[:,1]];c=current[boundary[:,0]];d=current[boundary[:,1]]
        faces.extend([np.column_stack([b,a,c]),np.column_stack([b,c,d])]);previous=current
    vertices=np.vstack(vertices).astype('f4');uv=np.vstack(uvs).astype('f4');faces=np.vstack(faces).astype('i4')
    normal=np.zeros_like(vertices);q=np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],vertices[faces[:,2]]-vertices[faces[:,0]])
    for col in range(3):np.add.at(normal,faces[:,col],q)
    normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-8)
    return vertices,uv,normal,faces

def make_mesh(name,thick):
    original,body,fin,finmask,hinge=prepare_texture(name)
    w=384;h=max(40,round(w*original.height/original.width))
    a=np.asarray(original.resize((w,h),Image.Resampling.LANCZOS).getchannel('A'))
    mask=a>50;dist=distance_transform_edt(mask)
    # Rounded anatomical cross-sections; narrow peripheral fins stay thin instead
    # of inflating along with the torso. Preserve the approved slim proportions.
    radius=gaussian_filter(dist.max(axis=0),4)
    center=gaussian_filter(np.argmax(dist,axis=0).astype(float),4)
    yy,xx=np.mgrid[:h,:w];cross=np.clip(1-((yy-center)/np.maximum(radius*1.15,1))**2,0,1)**.5
    bulk=(radius/max(radius.max(),1))**.65
    depth=(.006+cross*bulk*thick)*np.clip(dist/2,0,1)
    depth=gaussian_filter(depth,.65)*mask
    v,uv,normals,faces=closed_shell(mask,depth)
    fm=np.asarray(finmask.resize((w,h),Image.Resampling.LANCZOS));fins=[]
    for face in faces:
        points=v[face];ys=np.rint((1-points[:,1]/(.92*h/w))*.5*(h-1)).astype(int);xs=np.rint((points[:,0]+1)*.5*(w-1)).astype(int)
        if np.all(fm[np.clip(ys,0,h-1),np.clip(xs,0,w-1)]>20):fins.append(face)
    fv=v.copy();fv[:,2]+=np.sign(fv[:,2])*.012
    fins=np.array(fins,np.int32)
    root,top,bottom=TAIL_RIGS[name]
    centroids=uv[faces].mean(axis=1);caudal=(centroids[:,0]<root)&(centroids[:,1]>1-bottom)&(centroids[:,1]<1-top)
    body_faces=faces[~caudal];tail_faces=faces[caudal];normals=np.array(normals,np.float32)
    np.savez_compressed(SRC/(name+'.npz'),vertices=v,uv=uv,normals=normals,faces=faces,body_faces=body_faces,tail_faces=tail_faces,fin_vertices=fv,fin_faces=fins,fin_hinge=np.array([hinge[0]*2-1,(1-hinge[1]*2)*h/w*.92]))
    return v,uv,normals,body_faces,tail_faces,fv,fins,body,fin,hinge

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

def contact_sheet(data):
    contact=Image.new('RGB',(6*256,len(data)*150),(27,45,58))
    for row,(name,sp)in enumerate(data.items()):
        for col,yaw in enumerate([0,4,8,12,16,24]):
            shot=Image.new('RGBA',(sp['frameW'],sp['frameH']))
            for suffix,key,count,pose,scale in [('-atlas','frames',1,0,1),('-tails','tailFrames',sp['tailPoseCount'],1,1),('-fins','finFrames',sp['finPoseCount'],2,sp['finTextureScale'])]:
                atlas=Image.open(ROOT/'work/fish-raw'/(name+suffix+'.png')).convert('RGBA')
                f=sp[key][yaw*count+pose];part=atlas.crop((f['x'],f['y'],f['x']+f['w'],f['y']+f['h']))
                if scale!=1:part=part.resize((part.width*scale,part.height*scale),Image.Resampling.LANCZOS)
                shot.alpha_composite(part,(round(sp['frameW']/2-f['anchorX']*scale),round(sp['frameH']/2-f['anchorY']*scale)))
            shot.thumbnail((250,130));contact.paste(shot,(col*256,row*150),shot)
        ImageDraw.Draw(contact).text((3,row*150+133),sp['label'],fill=(230,235,240))
    contact.save(ROOT/'docs/previews/fish-orientations.jpg',quality=94)

def build(species_list=None):
    import moderngl
    ctx=moderngl.create_standalone_context(backend='egl');p=ctx.program(vertex_shader=VS,fragment_shader=FS)
    fw,fh=224,196;fbo=ctx.simple_framebuffer((fw*4,fh*4),components=4);fbo.use();ctx.enable(moderngl.DEPTH_TEST)
    atlasdata={}
    for row,(name,label,size,speed,beat,school,thick,finbeat)in enumerate(SPECIES if species_list is None else species_list):
        if name in ['ocellaris_clownfish','royal_gramma','green_chromis']:
            fw,fh=224,196
        else:
            fw,fh=240,210
        fbo.release();fbo=ctx.simple_framebuffer((fw*4,fh*4),components=4);fbo.use()
        v,uv,normals,faces,tails,fv,fins,body,fin,hinge=make_mesh(name,thick)
        vb=ctx.buffer(np.hstack((v,uv,normals)).astype('f4').tobytes());ib=ctx.buffer(faces.tobytes());vao=ctx.vertex_array(p,[(vb,'3f 2f 3f','pos','uv','normal')],ib)
        ti=ctx.buffer(tails.tobytes());tvao=ctx.vertex_array(p,[(vb,'3f 2f 3f','pos','uv','normal')],ti)
        fb=ctx.buffer(np.hstack((fv,uv,normals)).astype('f4').tobytes());fi=ctx.buffer(fins.tobytes());fvao=ctx.vertex_array(p,[(fb,'3f 2f 3f','pos','uv','normal')],fi)
        tex=ctx.texture(body.size,4,body.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes());ftex=ctx.texture(fin.size,4,fin.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes())
        for t in [tex,ftex]:t.filter=(moderngl.LINEAR,moderngl.LINEAR)
        p['hinge'].value=(hinge[0]*2-1,0)
        p['tailRoot'].value=TAIL_RIGS[name][0]*2-1
        def read():return Image.frombytes('RGBA',fbo.size,fbo.read(components=4)).transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize((fw,fh),Image.Resampling.LANCZOS)
        shots=[];tailshots=[];finshots=[]
        for yaw in range(UNIQUE_VIEWS):
            p['yaw'].value=yaw*2*math.pi/YAW_COUNT
            p['bend'].value=0;p['finPass'].value=0;p['finAngle'].value=0;p['depthOnly'].value=0;tex.use()
            fbo.color_mask=(True,True,True,True);fbo.clear(0,0,0,0,depth=1);vao.render()
            shots.append(cropped(read(),yaw,0,fw,fh))
            for pose,bend in enumerate(BODY_BENDS):
                fbo.clear(0,0,0,0,depth=1);p['bend'].value=0;p['depthOnly'].value=1;vao.render()
                p['depthOnly'].value=0;p['bend'].value=bend;tvao.render();shot=read()
                tailshots.append(cropped(shot,yaw,pose,fw,fh))
            for pose,angle in enumerate(FIN_ANGLES):
                fbo.color_mask=(True,True,True,True);fbo.clear(0,0,0,0,depth=1)
                p['bend'].value=0;p['finPass'].value=0;p['depthOnly'].value=1;tex.use();vao.render()
                p['depthOnly'].value=0;p['finPass'].value=1;p['finAngle'].value=angle;ftex.use();fvao.render()
                finshots.append(cropped(read(),yaw,pose,fw,fh))
        atlas,unique=pack(shots)
        tailatlas,unique_tails=pack(tailshots)
        finshots=[(shot.resize((max(1,round(shot.width/2)),max(1,round(shot.height/2))),Image.Resampling.LANCZOS),dict(meta,anchorX=meta['anchorX']/2,anchorY=meta['anchorY']/2))for shot,meta in finshots]
        finatlas,unique_fins=pack(finshots,512)
        # The model has bilateral texture/geometry. Share actual upright
        # views on its reverse side, never a runtime reflection. Tail bends
        # reverse phase on that side so their world-space deflection agrees.
        def directions(unique,count,tail=False):
            result=[]
            for yaw in range(YAW_COUNT):
                view=min(yaw,YAW_COUNT-yaw)
                for pose in range(count):
                    source=count-1-pose if tail and yaw>YAW_COUNT//2 else pose
                    result.append(dict(unique[view*count+source],yaw=yaw*360/YAW_COUNT,pose=pose,flipX=False))
            return result
        frames=directions(unique,1)
        finframes=directions(unique_fins,len(FIN_ANGLES))
        tailframes=directions(unique_tails,len(BODY_BENDS),True)
        def full_width(yaw):
            parts=[frames[yaw]]+tailframes[yaw*len(BODY_BENDS):(yaw+1)*len(BODY_BENDS)]
            return max(1,max(f['w']-f['anchorX']for f in parts)+max(f['anchorX']for f in parts)-4)
        view_widths=[full_width(yaw)for yaw in range(YAW_COUNT)]
        atlas.save(OUT/(name+'-atlas.png'),optimize=True);tailatlas.save(OUT/(name+'-tails.png'),optimize=True);finatlas.save(OUT/(name+'-fins.png'),optimize=True)
        raw=ROOT/'work/fish-raw';raw.mkdir(parents=True,exist_ok=True)
        for suffix in ['-atlas.png','-fins.png','-tails.png']:shutil.copy2(OUT/(name+suffix),raw/(name+suffix))
        atlasdata[name]={'label':label,'image':'pkg:/images/'+name+'-atlas.webp','width':atlas.width,'height':atlas.height,'frameW':fw,'frameH':fh,'yawCount':YAW_COUNT,'uniqueYawViews':UNIQUE_VIEWS,'viewWidths':view_widths,'poseCount':1,'tailPoseCount':len(BODY_BENDS),'tailFrames':tailframes,'tailImage':'pkg:/images/'+name+'-tails.webp','meshRevision':3,'meshVertices':len(v),'meshTriangles':len(faces)+len(tails),'length':size*1.6,'renderLength':fw*.9,'speed':speed,'beat':beat,'school':school,'frames':frames,'finTextureScale':2,'finImage':'pkg:/images/'+name+'-fins.webp','finPoseCount':len(FIN_ANGLES),'finBeat':finbeat,'finFrames':finframes,'bodyHeightFactor':.92,'bodyThickness':thick,'collisionHalfWidth':max(max(f['anchorX'],f['w']-f['anchorX']) for f in frames+tailframes+[dict(f,anchorX=f['anchorX']*2,anchorY=f['anchorY']*2,w=f['w']*2,h=f['h']*2)for f in finframes]),'collisionHalfHeight':max(max(f['anchorY'],f['h']-f['anchorY']) for f in frames+tailframes+[dict(f,anchorX=f['anchorX']*2,anchorY=f['anchorY']*2,w=f['w']*2,h=f['h']*2)for f in finframes])}
        for obj in [vao,tvao,ti,vb,ib,fvao,fb,fi,tex,ftex]:obj.release()
        print(name,len(frames),'body poses,',len(finframes),'independent fin poses; atlas',atlas.size,flush=True)
    (ROOT/'roku/scenes/species.json').write_text(json.dumps(atlasdata,indent=2))
    contact_sheet(atlasdata)
if __name__=='__main__':build()
