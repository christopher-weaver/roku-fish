"""Shared cave/animal coordinates used by the depth renderer and Blender source.

Reef X/Y are photograph pixels; Z points toward the viewer. The animal's
rear attachment stays inside a bending, blind chamber for its entire cycle.
"""
from pathlib import Path
import json, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
STAGE=(686,766,192,196)
COUNT=65
EXCLUSION=dict(id='resident-eel-cave',x=779,y=809,z=.47,halfWidth=88,halfHeight=81,halfDepth=.36)

def normals(v,f):
    out=np.zeros_like(v)
    q=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
    for col in range(3):np.add.at(out,f[:,col],q)
    return out/np.maximum(np.linalg.norm(out,axis=1)[:,None],1e-8)

def chamber(front,uv):
    n=len(front);vertices=[];coords=[];faces=[]
    # A curved interior with a blind rear wall, rather than an open flat arch.
    for depth,shift,scale in [(90,0,1),(35,8,1.05),(-35,24,1.15),(-105,43,1.15),(-180,55,1.12)]:
        ring=front.copy();ring[:,:2]=[773+shift,857.5+6*shift/55]+(front[:,:2]-[773,857.5])*scale;ring[:,2]=depth
        vertices.extend(ring);coords.extend(uv)
    for row in range(4):
        for i in range(n):
            a=row*n+i;b=row*n+(i+1)%n;faces.extend([(a,b,b+n),(a,b+n,a+n)])
    # The rear wall is actual geometry and closes the cave behind the moray.
    center=len(vertices);vertices.append((828,863.5,-180));coords.append(uv[0])
    for i in range(n):faces.append((4*n+i,4*n+(i+1)%n,center))
    v=np.array(vertices,dtype='f4');f=np.array(faces,dtype='i4')
    return v,np.array(coords,dtype='f4'),normals(v,f),f

def head_pose(peek):
    # Stay below the tunnel roof; only lift after the snout clears the mouth.
    t=np.clip((peek-.62)/.38,0,1);lift=t*t*t*(t*(t*6-15)+10)
    return np.array([812-39*peek,875-27*lift,-124+354*peek])

def animal(peek):
    source=np.load(ROOT/'assets/source/eel-model/zany-moray.npz');v=source['vertices'].copy();f=source['faces'];record=json.loads((ROOT/'assets/source/eel-model/model.json').read_text())
    # Pose zero is wholly behind the mouth, deep in the right-hand chamber.
    center=head_pose(peek);scale=76.
    yaw=math.radians(12-19*peek);c=math.cos(yaw);s=math.sin(yaw)
    palette=[];offset=0
    for part in record['meshes']:
        end=offset+part['vertices'];p=v[offset:end].copy();name=part['name']
        if name=='moray neck volume':
            t=np.repeat(np.linspace(0,1,40),40);angle=np.tile(np.arange(40)*2*np.pi/40,40)
            root=np.array([824,850,-158]);tip=center+np.array([0,-.19*scale,-.12*scale])
            ease=t*t*(3-2*t);centers=root[None,:]*(1-ease[:,None])+tip[None,:]*ease[:,None]
            radius=(.13+.13*t)*scale
            p=centers+np.column_stack([radius*np.cos(angle),radius*.82*np.sin(angle),np.zeros(len(t))])
        else:
            # The original head/jaw/eyeballs remain real, separately modeled volumes.
            if 'lower jaw'in name:p[:,2]-=.025*peek
            local=np.column_stack([p[:,0]*c-p[:,1]*s,-p[:,2],-p[:,0]*s-p[:,1]*c])*scale
            p=local+center
        v[offset:end]=p
        color=0
        if 'eye'in name:color=1
        if 'iris'in name:color=2
        if 'pupil'in name or 'nostril'in name or 'mouth recess'in name:color=3
        if 'tooth'in name:color=4
        palette.extend([color]*part['vertices']);offset=end
    return v,normals(v,f),f,np.array(palette,dtype='f4')
