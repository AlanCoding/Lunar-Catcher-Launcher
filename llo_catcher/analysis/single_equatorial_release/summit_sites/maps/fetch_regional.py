"""Cache only +/-4.5 degrees of public LOLA LDEM64 for context maps."""
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib,json
import numpy as np
from ....terrain.terrain_band import CACHE as OLD
ROOT=Path(__file__).parent
CACHE=OLD.parent/'lola64_context'
BASE='https://imbrium.mit.edu/DATA/LOLA_GDR/CYLINDRICAL/IMG/'

def main():
    CACHE.mkdir(parents=True,exist_ok=True)
    if (CACHE/'band.npy').exists():return
    with urlopen(BASE+'LDEM_64.LBL',timeout=60) as r:label=r.read()
    assert b'LSB_INTEGER' in label and b'SCALING_FACTOR        = 0.5' in label
    cols=23040;first=5472;count=576;start=first*cols*2;end=(first+count)*cols*2-1
    with urlopen(Request(BASE+'LDEM_64.IMG',headers={'Range':f'bytes={start}-{end}'}),timeout=60) as r:
        assert r.status==206 and r.headers['Content-Range']==f'bytes {start}-{end}/{11520*cols*2}'
        raw=r.read(end-start+2)
    assert len(raw)==end-start+1
    np.save(CACHE/'band.npy',np.frombuffer(raw,dtype='<i2').reshape(count,cols))
    (ROOT/'LDEM_64.LBL').write_bytes(label)
    (ROOT/'regional_source.json').write_text(json.dumps(dict(url=BASE+'LDEM_64.IMG',first_row=first,rows=count,cols=cols,ppd=64,scale_m=.5,byte_range=[start,end],sha256=hashlib.sha256(raw).hexdigest(),frame='ME/PA DE421',reference_radius_m=1737400),indent=2)+'\n')
    print('Cached regional terrain:',len(raw),'bytes')
if __name__=='__main__':main()
