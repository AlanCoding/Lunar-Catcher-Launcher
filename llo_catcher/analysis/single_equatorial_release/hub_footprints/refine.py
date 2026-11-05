"""Recompute local optimizations from saved coarse samples without rescreening."""
import json,csv
from concurrent.futures import ProcessPoolExecutor
from . import survey as s

def main():
    s.initialize();rows=list(csv.DictReader((s.ROOT/'footprints.csv').open()))
    bands=json.loads((s.ROOT.parent/'local_corridors/results.json').read_text())['both_ranges'];tasks=[]
    for b in bands:
        for side in ['north','south']:
            group=[r for r in rows if r['hub_side']==side and b['start_deg_east']<float(r['release_longitude_deg_east'])<b['end_deg_east']]
            best=min(group,key=lambda r:float(r['maximum_rise_above_hub_m']))
            tasks.append((float(best['release_longitude_deg_east']),1 if side=='north' else -1,b['start_deg_east'],b['end_deg_east']))
    with ProcessPoolExecutor(max_workers=4,initializer=s.initialize) as pool:results=list(pool.map(s.refine_candidate,tasks))
    results.sort(key=lambda x:(x['maximum_rise_above_hub_m'],x['total_relief_m']))
    p=s.ROOT/'results.json';r=json.loads(p.read_text());r['refined_best_per_corridor_side']=results;r['refined_pass_count']=sum(x['passes_10m_rise'] for x in results)
    r['refinement']='Local longitude minimization within one coarse sample spacing, native DEM vertices retained plus half-cell samples, 7200-point circle rim'
    p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(results[:5],indent=2))

if __name__=='__main__':main()
