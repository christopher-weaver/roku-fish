"""Paired textured eyeball volumes attached to the photographed head anatomy."""
import numpy as np
from PIL import Image
# Eye centers/radii in the existing cropped photograph, fish facing right.
EYES={
 'ocellaris_clownfish':(.822,.460,.022), 'yellow_tang':(.800,.430,.022),
 'royal_gramma':(.833,.460,.018), 'emperor_angelfish':(.872,.550,.020),
 'moorish_idol':(.772,.471,.020), 'green_chromis':(.833,.460,.020),
 'blue_tang':(.878,.411,.022), 'copperband_butterflyfish':(.756,.500,.020),
 'banggai_cardinalfish':(.894,.489,.023), 'mandarin_dragonet':(.889,.411,.028)}
def build(data,name,texture,path):
    u,v,r=EYES[name];w,h=texture.size
    center=np.array([2*u-1,(1-2*v)*h/w*.92])
    vertices=data['vertices'];front=vertices[vertices[:,2]>=0]
    nearest=np.argmin(np.sum((front[:,:2]-center)**2,axis=1));depth=float(front[nearest,2])
    rx=2*r;ry=rx*.92;rz=rx*.72
    points=[];normals=[];uv=[];faces=[];rings=16;segments=32
    for side in [-1,1]:
        offset=len(points)
        for row in range(rings+1):
            theta=np.pi*row/rings
            for col in range(segments+1):
                phi=2*np.pi*col/segments
                q=np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
                points.append([center[0]+q[0]*rx,center[1]+q[1]*ry,side*(depth-rz*.25+q[2]*rz)])
                n=q/np.array([rx,ry,rz]);n[2]*=side;normals.append(n/np.linalg.norm(n))
                uv.append([.5+q[0]*.5,.5+q[1]*.5])
        for row in range(rings):
            for col in range(segments):
                a=offset+row*(segments+1)+col;b=a+segments+1
                faces.extend([[a,b,a+1],[a+1,b,b+1]])
    data.update(eye_vertices=np.array(points,'f4'),eye_normals=np.array(normals,'f4'),eye_uv=np.array(uv,'f4'),eye_faces=np.array(faces,'i4'))
    box=((u-r)*w,(v-r)*h,(u+r)*w,(v+r)*h)
    eye=texture.crop(tuple(round(n) for n in box)).resize((96,96),Image.Resampling.LANCZOS)
    eye.save(path)
    return {'centerUV':[u,v],'radiusUV':r,'vertices':len(points),'triangles':len(faces),'projection':'paired ellipsoids, photo iris and pupil'}
