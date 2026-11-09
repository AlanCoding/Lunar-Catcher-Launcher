from pathlib import Path
import json,argparse
import numpy as np
from .model import Config,Tether
OUT=Path(__file__).parent/'results'
def angular_envelope(X,cutoff=500.):
    """Include exact cutoff-circle intersections of each piecewise-linear cable."""
    radius=np.linalg.norm(X,axis=2)
    theta=np.unwrap(np.arctan2(X[:,:,1],X[:,:,0]),axis=1)
    lo=np.min(np.where(radius>=cutoff,theta,np.inf),axis=1)
    hi=np.max(np.where(radius>=cutoff,theta,-np.inf),axis=1)
    P=X[:,:-1];D=np.diff(X,axis=1);a=np.sum(D*D,axis=2);b=2*np.sum(P*D,axis=2);c=np.sum(P*P,axis=2)-cutoff**2
    disc=b*b-4*a*c
    for sign in [-1,1]:
        u=(-b+sign*np.sqrt(np.maximum(disc,0)))/(2*np.maximum(a,1e-20))
        valid=(disc>=0)&(u>=0)&(u<=1)&(a>0)
        cross=P+u[:,:,None]*D
        raw=np.arctan2(cross[:,:,1],cross[:,:,0])
        angle=theta[:,:-1]+(raw-theta[:,:-1]+np.pi)%(2*np.pi)-np.pi
        lo=np.minimum(lo,np.min(np.where(valid,angle,np.inf),axis=1))
        hi=np.maximum(hi,np.max(np.where(valid,angle,-np.inf),axis=1))
    empty = ~np.isfinite(lo)
    lo[empty] = np.nan
    hi[empty] = np.nan
    return np.degrees(lo),np.degrees(hi)

def run(c):
    m=Tether(c);records,solver=m.run();fields=[r[2] for r in records]
    X=np.array([f['X'] for f in fields]);radius=np.linalg.norm(X,axis=2)
    angles=np.unwrap(np.arctan2(X[:,:,1],X[:,:,0]),axis=1)*180/np.pi
    low,high=angular_envelope(X)
    stem=f'{c.name}_n{c.nodes}';OUT.mkdir(exist_ok=True)
    data=dict(time_s=np.array([r[0] for r in records]),phase=np.array([r[1] for r in records]),
              xy_m=X,stress_Pa=np.array([f['stress'] for f in fields]),strain=np.array([f['strain'] for f in fields]),
              material_velocity_m_s=np.array([f['material_velocity'] for f in fields]),
              q_m=np.array([f['q'] for f in fields]),angle_min_deg=low,angle_max_deg=high,tip_angle_deg=angles[:,-1])
    np.savez_compressed(OUT/f'{stem}.npz',**data)
    summary=m.metadata();summary['solver']=solver;summary['phase_metrics']=[]
    for name in dict.fromkeys(data['phase']):
        mask=data['phase']==name
        occupied=mask & np.isfinite(low)
        summary['phase_metrics'].append(dict(phase=str(name),min_angle_deg=float(low[occupied].min()) if occupied.any() else None,max_angle_deg=float(high[occupied].max()) if occupied.any() else None,
                 max_simultaneous_width_deg=float((high-low)[occupied].max()) if occupied.any() else None,peak_sampled_stress_Pa=float(data['stress_Pa'][mask].max()),
                 minimum_sampled_stress_Pa=float(data['stress_Pa'][mask].min())))
    (OUT/f'{stem}.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--nodes',type=int,default=32);p.add_argument('--ratio3',action='store_true');p.add_argument('--method',choices=['BDF','Radau'],default='BDF');a=p.parse_args()
    run(Config(nodes=a.nodes,method=a.method,name='kevlar_ratio3' if a.ratio3 else 'kevlar_1p5GPa',target_tether_payload_ratio=3. if a.ratio3 else 0.))
