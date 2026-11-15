"""Build only the recessed tunnel matte; eel and lighting now use 3D/surface assets."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import label
ROOT=Path(__file__).resolve().parents[1]
def build():
 from connected_scene import source_reef
 alpha=np.asarray(source_reef().getchannel('A'));labs,_=label(alpha<40);component=labs[850,773]
 assert component not in [0,labs[0,0]]
 mask=Image.fromarray(np.uint8(labs[808:907,715:831]==component)*255).filter(ImageFilter.GaussianBlur(.5));yy,xx=np.mgrid[:99,:116]
 rgba=np.zeros((99,116,4),dtype='uint8');shade=np.clip((xx-58)**2/160+(99-yy)/8,0,25)
 rgba[:,:,:3]=np.stack((16+shade*.65,9+shade*.42,20+shade*.8),axis=2).astype('uint8');rgba[:,:,3]=np.asarray(mask)
 Image.fromarray(rgba).save(ROOT/'roku/images/cave-interior.png',optimize=True)
if __name__=='__main__':build()
