"""Cache ±3 degree latitude, 13–19.5 E, from source SLDEM2015 rows."""
from pathlib import Path
import hashlib,json
import numpy as np
from urllib.request import Request,urlopen
from llo_catcher.site_selection.support.fetch_terrain import BASE,field
P=Path(__file__).parent;PPD=512;ROWS=1536;COLS=45*PPD

def main():
 bands=[];sources=[]
 for side,first in [('00n_30n',30*PPD-ROWS),('30s_00s',0)]:
  stem=f'sldem2015_512_{side}_000_045_float'
  label=urlopen(BASE+stem+'.lbl',timeout=60).read();txt=label.decode('ascii')
  assert field(txt,'SAMPLE_TYPE')=='PC_REAL' and field(txt,'UNIT')=='KILOMETER'
  start=first*COLS*4;end=(first+ROWS)*COLS*4-1
  with urlopen(Request(BASE+stem+'.img',headers={'Range':f'bytes={start}-{end}'}),timeout=120) as f:
   assert f.status==206 and f.headers['Content-Range']==f'bytes {start}-{end}/{30*PPD*COLS*4}'
   raw=f.read()
  assert len(raw)==ROWS*COLS*4
  arr=np.frombuffer(raw,dtype='<f4').reshape(ROWS,COLS)[:,13*PPD:int(19.5*PPD)].copy();bands.append(arr)
  sources.append(dict(url=BASE+stem+'.img',range=[start,end],response_sha256=hashlib.sha256(raw).hexdigest(),label_sha256=hashlib.sha256(label).hexdigest()))
  print('Fetched',side,flush=True)
 patch=np.concatenate(bands);np.save(P/'p1_dem_patch.npy',patch)
 (P/'terrain_provenance.json').write_text(json.dumps(dict(rows=3072,columns=3328,ppd=512,west_deg=13,north_deg=3,sources=sources,patch_sha256=hashlib.sha256((P/'p1_dem_patch.npy').read_bytes()).hexdigest()),indent=2)+'\n')
if __name__=='__main__':main()
