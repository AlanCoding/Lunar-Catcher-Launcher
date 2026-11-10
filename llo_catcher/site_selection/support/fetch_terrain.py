"""Fetch the final SLDEM2015 band directly, preserving source byte hashes."""
from urllib.request import Request,urlopen
import hashlib,json,re
import numpy as np
from .terrain import CACHE,ROWS,PPD,COLS,RADIUS
BASE='https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/data/sldem2015/tiles/float_img/'

def field(label,name):
    m=re.search(r'^\s*'+re.escape(name)+r'\s*=\s*([^\r\n]+)',label,re.M)
    if not m:raise ValueError(name)
    return m.group(1).strip().strip('"')

def fetch(west):
    CACHE.mkdir(parents=True,exist_ok=True);dest=CACHE/f'{west:03d}.npy';meta=dest.with_suffix('.json')
    if dest.exists() and meta.exists():
        assert np.load(dest,mmap_mode='r').shape==(2*ROWS,COLS)
        return json.loads(meta.read_text())
    bands=[];sources=[]
    for side,first in [('00n_30n',30*PPD-ROWS),('30s_00s',0)]:
        stem=f'sldem2015_512_{side}_{west:03d}_{west+45:03d}_float'
        with urlopen(BASE+stem+'.lbl',timeout=45) as response:raw_label=response.read(65536)
        label=raw_label.decode('ascii')
        assert field(label,'SAMPLE_TYPE')=='PC_REAL' and int(field(label,'SAMPLE_BITS'))==32
        assert field(label,'UNIT')=='KILOMETER' and float(field(label,'SCALING_FACTOR'))==1
        assert float(field(label,'OFFSET'))==RADIUS/1000
        assert field(label,'COORDINATE_SYSTEM_NAME')=='MEAN EARTH/POLAR AXIS OF DE421'
        assert int(field(label,'LINE_SAMPLES'))==COLS and int(field(label,'LINES'))==30*PPD
        start=first*COLS*4;end=(first+ROWS)*COLS*4-1;expected=f'bytes {start}-{end}/{30*PPD*COLS*4}'
        with urlopen(Request(BASE+stem+'.img',headers={'Range':f'bytes={start}-{end}'}),timeout=60) as response:
            assert response.status==206 and response.headers['Content-Range']==expected
            raw=response.read(ROWS*COLS*4+1)
        assert len(raw)==ROWS*COLS*4
        a=np.frombuffer(raw,dtype='<f4').reshape(ROWS,COLS);assert np.isfinite(a).all()
        bands.append(a);sources.append(dict(url=BASE+stem+'.img',content_range=expected,sha256=hashlib.sha256(raw).hexdigest(),label_sha256=hashlib.sha256(raw_label).hexdigest()))
        (CACHE/(stem+'.lbl')).write_bytes(raw_label)
    np.save(dest,np.concatenate(bands));result=dict(west_deg=west,sources=sources)
    meta.write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    for west in range(0,360,45):fetch(west);print('Ready:',west,flush=True)
