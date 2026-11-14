"""Verify actual production adjacent-pixel pan weights, without anchor assumptions."""
import json,sys
from pathlib import Path
def validate(log):
 records=[json.loads(line[4:])for line in log.splitlines()if line.startswith('PAN ')]
 if len(records)!=362:raise AssertionError('Expected HD and FHD pan samples')
 error=0;largest=0
 for width in [1280,1920]:
  previous=None
  for r in [r for r in records if r['width']==width]:
   x=r['first']+r['alpha']/255
   error=max(error,abs(x-r['target']))
   if previous is not None:largest=max(largest,abs(x-previous))
   previous=x
 if error>.002 or largest>.04:raise AssertionError((error,largest))
 return f'PASS adjacent-pixel pan: maximum centroid error {error:.6f}px; maximum 60Hz increment {largest:.6f}px; no large-anchor transforms\n'
if __name__=='__main__':print(validate(Path(sys.argv[1]).read_text()),end='')
