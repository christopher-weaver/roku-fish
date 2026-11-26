"""Width / tip-to-tip length model targets, not specimen measurements.

See docs/FISH_ANATOMY.md for morphological references and limitations.
"""
import numpy as np
WIDTHS={'ocellaris_clownfish':.18,'yellow_tang':.12,'royal_gramma':.145,
        'emperor_angelfish':.14,'moorish_idol':.10,'green_chromis':.14,
        'blue_tang':.125,'copperband_butterflyfish':.16,
        'banggai_cardinalfish':.125,'mandarin_dragonet':.18}
AMPLITUDE=.055
START=.28
TURN_AMPLITUDE=.04
TURN_START=.15
def curve(u):
    u=np.clip((u-START)/(1-START),0,1)
    return u*u*np.sin(1.5*np.pi*u)
def flex(vertices,phase):
    result=vertices.astype(float).copy();span=np.ptp(vertices[:,0])
    u=(vertices[:,0].max()-vertices[:,0])/span
    result[:,2]+=phase*AMPLITUDE*span*curve(u)
    return result
def turn_curve(u):
    return np.clip((u-TURN_START)/(1-TURN_START),0,1)**2
def turn_flex(vertices,amount):
    result=vertices.astype(float).copy();span=np.ptp(vertices[:,0])
    u=(vertices[:,0].max()-vertices[:,0])/span
    result[:,2]+=amount*TURN_AMPLITUDE*span*turn_curve(u)
    return result
def rescale(data,name):
    v=data['vertices'];span=np.ptp(v[:,0]);factor=WIDTHS[name]*span/np.ptp(v[:,2])
    if abs(factor-1)>1e-6:
        for key in ['vertices','fin_vertices']:data[key][:,2]*=factor
        data['normals'][:,2]/=factor
        data['normals']/=np.linalg.norm(data['normals'],axis=1)[:,None]
    return float(factor)
