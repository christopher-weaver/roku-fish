"""Shared-atlas conservative front-shell masks."""
import numpy as np
def rectangles(alpha):
 # Cover the front geometry using rectangles cut from the SAME photo atlas.
 # A two-pixel conservative mask keeps the baby behind the lip at all poses.
 h,w=alpha.shape;cell=2;mask=np.zeros(((h+1)//2,(w+1)//2),dtype=bool)
 for y in range(mask.shape[0]):
  for x in range(mask.shape[1]):mask[y,x]=np.any(alpha[y*2:y*2+2,x*2:x*2+2]>100)
 result=[]
 for y in range(mask.shape[0]):
  for x in range(mask.shape[1]):
   if not mask[y,x]:continue
   right=x
   while right<mask.shape[1]and mask[y,right]:right+=1
   bottom=y+1
   while bottom<mask.shape[0]and mask[bottom,x:right].all():bottom+=1
   mask[y:bottom,x:right]=False
   result.append(dict(x=x*2,y=y*2,w=min(w,right*2)-x*2,h=min(h,bottom*2)-y*2))
 return result
