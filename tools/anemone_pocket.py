"""Attach the complete anemone directly to the existing modeled reef crevice."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def build():
    path=ROOT/'roku/scenes/tank.json';cfg=json.loads(path.read_text())
    props={'anemone-rim','anemone-platform','anemone-lip','anemone-foot-rocks'}
    cfg['formations']=[f for f in cfg['formations']if f['id']not in props]
    cfg['occlusionDepths']=[f['z']for f in cfg['formations']]
    cfg.pop('anemonePocket',None);cfg.pop('anemonePlatform',None)
    cfg['anemoneHabitat']={'support':'foreground-reef','fullBase':True,'drapedTentacles':True,'seatOffsetY':12,'sandTransition':'existing modeled seabed'}
    path.write_text(json.dumps(cfg,indent=2)+'\n')
    folder=ROOT/'assets/source/reef-model';path=folder/'model.json';record=json.loads(path.read_text())
    record['objects']=[o for o in record['objects']if o['name']not in ['anemone-pocket-rim','anemone-platform']]
    path.write_text(json.dumps(record,indent=2)+'\n')
    for name in props:
        for prefix in ['reef-','shadow-']:(ROOT/'roku/images'/f'{prefix}{name}.webp').unlink(missing_ok=True)
    for name in ['anemone-platform.npz','anemone-platform-colour.png','anemone-platform-sand.png','anemone-platform-lip.png','anemone-pocket-rim.npz','anemone-pocket-rim-colour.png']:(folder/name).unlink(missing_ok=True)
    print('Anemone attached to existing closed reef volumes and seabed; no rim or platform props',flush=True)
if __name__=='__main__':build()
