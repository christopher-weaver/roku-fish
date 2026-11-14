"""Check production pan transforms at native float32 drawing precision."""
import json,struct,math,sys
from pathlib import Path

def validate(output):
    previous={};worst=step=stretch=0;records=0
    for line in output.splitlines():
        if not line.startswith('PAN '):continue
        record=json.loads(line[4:]);tr=record['transform'];records+=1
        sx=struct.unpack('f',struct.pack('f',tr['sx']))[0]
        sy=struct.unpack('f',struct.pack('f',tr['sy']))[0]
        actual=tr['x']+65536*sx;actual_y=tr['y']+65536*sy
        if not math.isfinite(actual+actual_y):raise ValueError('Invalid transform')
        worst=max(worst,abs(actual-record['target']),abs(actual_y+36*record['targetScale']))
        stretch=max(stretch,abs(sx-record['targetScale'])*2048,abs(sy-record['targetScale'])*2048)
        if record['width']in previous:step=max(step,abs(actual-previous[record['width']]))
        previous[record['width']]=actual
    if records!=362 or set(previous)!={1280,1920}:raise ValueError('Missing HD/FHD pan samples')
    if worst>.009 or step>.04 or stretch>.032:raise ValueError(f'Precision error={worst} step={step} stretch={stretch}')
    return f'PASS float32 pan placement: max error {worst:.6f}px, max frame step {step:.6f}px, max 2048px-layer stretch {stretch:.6f}px\n'

if __name__=='__main__':
    try:print(validate(Path(sys.argv[1]).read_text()),end='')
    except (ValueError,IndexError)as error:raise SystemExit(str(error))
