"""Context-matched body texture synthesis under independently moving fins."""
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation,binary_erosion,uniform_filter,gaussian_filter
from scipy.signal import fftconvolve

def repair(image,finmask):
    scale=min(1.,384/image.width);size=(round(image.width*scale),round(image.height*scale))
    rgba=np.array(image.resize(size,Image.Resampling.LANCZOS));rgb=rgba[:,:,:3].astype('f4')/255
    hole=np.asarray(finmask.resize(size,Image.Resampling.LANCZOS))>22
    hole&=rgba[:,:,3]>220
    original=hole.copy();valid=rgba[:,:,3]>230;radius=7;diameter=2*radius+1
    donor=binary_erosion(valid&~binary_dilation(original,iterations=2),iterations=radius,border_value=0)
    # Do not clone the eyes or snout into the torso.
    donor[:,int(size[0]*.81):]=False
    confidence=(~hole&valid).astype('f4');iterations=0
    while hole.any() and iterations<600:
        boundary=hole&binary_dilation(~hole)&valid
        if not boundary.any() or not donor.any():break
        priority=uniform_filter(confidence,size=diameter,mode='constant')
        priority[~boundary]=-1;y,x=np.unravel_index(np.argmax(priority),priority.shape)
        y=int(np.clip(y,radius,size[1]-radius-1));x=int(np.clip(x,radius,size[0]-radius-1))
        region=(slice(y-radius,y+radius+1),slice(x-radius,x+radius+1))
        known=(~hole[region]&valid[region]).astype('f4');target=rgb[region]
        if known.sum()<3:break
        # Search a neighborhood wide enough to continue the species' actual
        # stripes/scales, rather than shifting an unrelated band down the body.
        top=max(0,y-110);left=max(0,x-140);bottom=min(size[1],y+111);right=min(size[0],x+141)
        window=rgb[top:bottom,left:right];candidates=donor[top+radius:bottom-radius,left+radius:right-radius]
        if not candidates.any():
            top=left=0;bottom=size[1];right=size[0];window=rgb;candidates=donor[radius:bottom-radius,radius:right-radius]
        kernel=known[::-1,::-1];score=np.zeros((window.shape[0]-diameter+1,window.shape[1]-diameter+1),dtype='f4')
        for channel in range(3):
            data=window[:,:,channel];patch=target[:,:,channel]
            score+=fftconvolve(data*data,kernel,mode='valid')-2*fftconvolve(data,(patch*known)[::-1,::-1],mode='valid')
        score/=known.sum()
        yy,xx=np.mgrid[:score.shape[0],:score.shape[1]]
        score+=((xx+left+radius-x)**2+(yy+top+radius-y)**2)*.0000004
        score[~candidates]=np.inf;sy,sx=np.unravel_index(np.argmin(score),score.shape)
        source=rgb[top+sy:top+sy+diameter,left+sx:left+sx+diameter].copy()
        unknown=hole[region].copy();rgb[region][unknown]=source[unknown]
        confidence[region][unknown]=max(.01,float(confidence[region].mean()))
        hole[region][unknown]=False;iterations+=1
    if hole.any():
        from scipy.ndimage import distance_transform_edt
        _,indices=distance_transform_edt(hole,return_indices=True);rgb[hole]=rgb[indices[0][hole],indices[1][hole]]
    repaired=Image.fromarray(np.uint8(np.clip(rgb*255,0,255))).resize(image.size,Image.Resampling.LANCZOS)
    weight=gaussian_filter(original.astype(float),1.1);weight=Image.fromarray(np.uint8(weight*255)).resize(image.size,Image.Resampling.LANCZOS)
    result=Image.composite(repaired,image.convert('RGB'),weight).convert('RGBA');result.putalpha(image.getchannel('A'))
    return result
