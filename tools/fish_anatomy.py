"""Width / tip-to-tip length model targets, not specimen measurements.

See docs/FISH_ANATOMY.md for morphological references and limitations.
"""
import numpy as np
WIDTHS={'ocellaris_clownfish':.145,'yellow_tang':.085,'royal_gramma':.115,
        'emperor_angelfish':.10,'moorish_idol':.065,'green_chromis':.11,
        'blue_tang':.09,'copperband_butterflyfish':.06,
        'banggai_cardinalfish':.09,'mandarin_dragonet':.15}
AMPLITUDE=.025
START=.45
def curve(u):
    u=np.clip((u-START)/(1-START),0,1)
    return u*u*np.sin(1.5*np.pi*u)
def flex(vertices,phase):
    result=vertices.astype(float).copy();span=np.ptp(vertices[:,0])
    u=(vertices[:,0].max()-vertices[:,0])/span
    result[:,2]+=phase*AMPLITUDE*span*curve(u)
    return result
def rescale(data,name):
    v=data['vertices'];span=np.ptp(v[:,0]);factor=WIDTHS[name]*span/np.ptp(v[:,2])
    if abs(factor-1)>1e-6:
        for key in ['vertices','fin_vertices']:data[key][:,2]*=factor
        data['normals'][:,2]/=factor
        data['normals']/=np.linalg.norm(data['normals'],axis=1)[:,None]
    return float(factor)
