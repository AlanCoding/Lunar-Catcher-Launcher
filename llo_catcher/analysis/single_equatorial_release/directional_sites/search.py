"""Directional corridor and hilltop catalogs; preserves original work."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json,csv
import numpy as np
from scipy.optimize import brentq
from . import orbits
OUT=Path(__file__).parent

def sample(args):
    lon,direction=args
    return (lon,orbits.clearance(lon,direction))

def corridors(direction):
    survey=json.loads((OUT/'degree_survey.json').read_text())[direction]
    seeds=[int(r['longitude_deg_east']) for r in survey if r['status']!='outbound_collision']
    windows=[]
    for seed in seeds:
        lo,hi=seed-1,seed+1
        if windows and lo<=windows[-1][1]:windows[-1][1]=hi
        else:windows.append([lo,hi])
    cache={};levels=[]
    with ProcessPoolExecutor(max_workers=4,initializer=orbits.initialize) as pool:
        for ppd in [512,1024,2048,4096]:
            grid=sorted(set(float(k/ppd) for lo,hi in windows for k in range(lo*ppd,hi*ppd+1)))
            missing=[x for x in grid if x not in cache]
            for j,(lon,gap) in enumerate(pool.map(sample,[(x,direction) for x in missing],chunksize=16)):
                cache[lon]=gap
                if j%2000==0:print(direction,ppd,j,len(missing),flush=True)
            bands=[]
            for lo,hi in windows:
                xs=[x for x in grid if lo<=x<=hi];good=np.array([cache[x]>0 for x in xs])
                assert not good[0] and not good[-1], 'Expand search window at clear edge'
                for a in np.where(good & ~np.r_[False,good[:-1]])[0]:
                    b=a
                    while b+1<len(xs) and good[b+1]:b+=1
                    left=brentq(lambda x:orbits.clearance(x,direction),xs[a-1],xs[a],xtol=1e-10)
                    right=brentq(lambda x:orbits.clearance(x,direction),xs[b],xs[b+1],xtol=1e-10)
                    bands.append(dict(start_deg_east=left,end_deg_east=right,length_km=(right-left)*orbits.base.RADIUS*np.pi/180/1000))
            levels.append(dict(samples_per_degree=ppd,intervals=len(bands),total_km=sum(x['length_km'] for x in bands)))
            print(direction,levels[-1],flush=True)
    result=dict(direction=direction,seeds=seeds,windows=windows,bands=bands,convergence=levels,scope='Local ±1 degree neighborhoods of successful one-degree seeds; not globally exhaustive')
    (OUT/f'{direction}_corridors.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    import sys
    orbits.initialize()
    if sys.argv[1]=='degree':
        survey={d:[orbits.classify(lon,d) for lon in range(360)] for d in ['east','west']}
        (OUT/'degree_survey.json').write_text(json.dumps(survey,indent=2)+'\n')
    else:corridors(sys.argv[1])
