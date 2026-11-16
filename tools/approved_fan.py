"""Restore the user-approved lacy sea fan, including its existing slow motion."""
from pathlib import Path
import json,shutil
ROOT=Path(__file__).resolve().parents[1]
def restore(cfg):
    source=ROOT/'assets/source/marine-renders/approved-fan'
    formation=json.loads((source/'formation.json').read_text())
    shutil.copy2(source/'atlas.webp',ROOT/'roku/images/reef-sea-fan-motion-0.webp')
    shutil.copy2(source/'footprint.png',ROOT/'assets/source/marine-renders/sea-fan-motion-footprint.png')
    shutil.copy2(source/'volume.npz',ROOT/'assets/source/marine-renders/sea-fan-volume.npz')
    for i,current in enumerate(cfg['formations']):
        if current['id']=='sea-fan':cfg['formations'][i]=formation
