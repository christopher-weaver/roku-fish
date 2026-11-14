from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def catalog():
    data={}
    for p in sorted((ROOT/'roku/images').iterdir()):
        if p.suffix not in ['.png','.jpg','.webp']:continue
        with Image.open(p)as im:w,h=im.size
        data[p.name]={'width':w,'height':h,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    (ROOT/'roku/scenes/assets.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Cataloged',len(data),'runtime images')
if __name__=='__main__':catalog()
