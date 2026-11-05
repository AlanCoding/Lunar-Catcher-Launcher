"""Equatorial prograde release-height survey, with exact piecewise-linear DEM cells.

No finite sling offset; release at periapsis and capture at 25 km apoapsis.
All post-miss trajectories stop at first impact or 1.5 payload periods.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json, csv, hashlib
import numpy as np
from scipy.optimize import brentq
from llo_catcher.analysis.terrain.terrain_band import TerrainBand, RADIUS
from llo_catcher.analysis.terrain.impact_demo import MU, MOON_OMEGA

OUT=Path(__file__).resolve().parent
RC=RADIUS+25000.
STEP=2*np.pi/(360*512)
_GROUND=None

def initialize():
    global _GROUND
    band=TerrainBand()
    _GROUND=np.concatenate([.5*(a[127].astype(float)+a[128].astype(float))*1000 for a in band.tiles])


def terrain(lon):
    u=np.asarray(lon)/STEP-.5;i=np.floor(u).astype(np.int64);w=u-i
    return (1-w)*_GROUND[i%len(_GROUND)]+w*_GROUND[(i+1)%len(_GROUND)]


def orbit(lon_deg,height):
    lon=np.radians(lon_deg);ground=float(terrain(lon));rp=RADIUS+ground+height
    assert 0<rp<RC
    a=(rp+RC)/2;e=(RC-rp)/(RC+rp);p=rp*(1+e);h=np.sqrt(MU*p);n=np.sqrt(MU/a**3)
    return dict(lon=lon,height=height,ground=ground,rp=rp,a=a,e=e,p=p,h=h,n=n,T=2*np.pi/n)


def motion(f,o):
    f=np.asarray(f);wrapped=f%(2*np.pi)
    E=np.arctan2(np.sqrt(1-o['e']**2)*np.sin(wrapped),o['e']+np.cos(wrapped))%(2*np.pi)
    t=(E-o['e']*np.sin(E)+2*np.pi*np.floor(f/(2*np.pi)))/o['n']
    r=o['p']/(1+o['e']*np.cos(f))
    return r,t


def at_longitude(x,o):
    """Invert monotonic body-fixed angular travel x=f-Omega*t(f)."""
    x=np.asarray(x);f=x/(1-MOON_OMEGA/o['n'])
    for _ in range(4):
        r,t=motion(f,o);f-=(f-MOON_OMEGA*t-x)/(1-MOON_OMEGA*r*r/o['h'])
    r,t=motion(f,o)
    rp=o['p']*o['e']*np.sin(f)/(1+o['e']*np.cos(f))**2
    slope=rp/(1-MOON_OMEGA*r*r/o['h'])
    return r,t,f,slope


def intervals(o,return_only=False):
    ceiling=RADIUS+float(_GROUND.max())+.01
    if o['rp']>=ceiling:return []
    fc=np.arccos(np.clip((o['p']/ceiling-1)/o['e'],-1,1))
    # This ensures radial height vs body longitude is strictly convex on all
    # possible-contact intervals; each linear DEM cell has at most one minimum.
    assert fc<np.pi/2
    fs=[(2*np.pi-fc,2*np.pi+fc)] if return_only else [(0.,fc)]
    return [(float(lo-MOON_OMEGA*motion(lo,o)[1]),float(hi-MOON_OMEGA*motion(hi,o)[1])) for lo,hi in fs]


def profile(o,lo,hi,refine=False):
    # Include every terrain interpolation knot; optionally every half-cell too.
    k0=int(np.ceil((o['lon']+lo)/STEP-.5));k1=int(np.floor((o['lon']+hi)/STEP-.5))
    xs=np.r_[lo,(np.arange(k0,k1+1)+.5)*STEP-o['lon'],hi]
    xs=np.unique(xs)
    if refine:xs=np.sort(np.r_[xs,(xs[:-1]+xs[1:])/2])
    r,t,f,slope=at_longitude(xs,o);heights=terrain(o['lon']+xs)
    gap=r-RADIUS-heights
    ground_slope=np.diff(heights)/np.diff(xs)
    # Convexity makes these all possible interior minima. Check them exactly,
    # including grazing dips whose cell endpoints are both above terrain.
    cells=np.flatnonzero((slope[:-1]<ground_slope)&(slope[1:]>ground_slope))
    roots=[]
    for i in cells:
        root=brentq(lambda x:float(at_longitude(x,o)[3])-ground_slope[i],xs[i],xs[i+1],xtol=1e-14)
        roots.append(root)
    if roots:
        xs=np.sort(np.r_[xs,roots]);r,t,_,_=at_longitude(xs,o);gap=r-RADIUS-terrain(o['lon']+xs)
    return xs,gap


def minimum_outbound(lon_deg,height,refine=False):
    o=orbit(lon_deg,height);bounds=intervals(o)
    if not bounds:return o['rp']-RADIUS-float(_GROUND.max())
    return min(float(profile(o,lo,hi,refine)[1].min()) for lo,hi in bounds)


def threshold(lon):
    ground=float(terrain(np.radians(lon)));high=max(1.,float(_GROUND.max())-ground+1)
    g0=minimum_outbound(lon,0.)
    h=0. if g0>=-1e-8 else brentq(lambda h:minimum_outbound(lon,h),0,high,xtol=.001)
    o=orbit(lon,h);bounds=intervals(o)
    critical={}
    if bounds:
        lo,hi=bounds[0];xs,gaps=profile(o,lo,hi);x=xs[int(np.argmin(gaps))]
        r,t,_,_=at_longitude(x,o)
        critical=dict(limiting_terrain_longitude_deg_east=float(np.degrees(o['lon']+x)%360),
            limiting_distance_from_release_km=float(x*RADIUS/1000),limiting_time_s=float(t),
            terrain_rise_to_limiting_point_m=float(terrain(o['lon']+x))-ground,
            payload_radial_rise_to_limiting_point_m=float(r-o['rp']))
    return dict(longitude_deg_east=lon,local_ground_height_m=ground,clearance_threshold_m=h,**critical)


def first_contact(o,return_only=False,refine=False):
    for lo,hi in intervals(o,return_only):
        xs,gap=profile(o,lo,hi,refine);hit=np.flatnonzero(gap<=0)
        if len(hit):
            i=int(hit[0]);x=xs[i]
            if i:
                x=brentq(lambda x:float(at_longitude(x,o)[0])-RADIUS-float(terrain(o['lon']+x)),xs[i-1],xs[i],xtol=1e-14)
            r,t,f,_=at_longitude(x,o)
            assert float(t)<=1.5*o['T']+1e-7
            return dict(impact_time_s=float(t),impact_longitude_deg_east=float(np.degrees(o['lon']+x)%360),impact_orbits=float(t/o['T']))
    return None


def classify(args):
    lon,height,refine=args;o=orbit(lon,height)
    impact=first_contact(o,refine=refine)
    if impact:status='outbound_collision'
    else:
        impact=first_contact(o,True,refine)
        status='return_impact' if impact else 'not_arrested'
    speed=o['h']/o['rp'];vapo=o['h']/RC;vc=np.sqrt(MU/RC)
    return dict(longitude_deg_east=lon,release_height_m=height,status=status,
        release_ground_elevation_m=o['ground'],release_radius_m=o['rp'],
        inertial_release_speed_m_s=speed,surface_relative_release_speed_m_s=speed-MOON_OMEGA*o['rp'],
        catch_relative_speed_m_s=vc-vapo,catch_time_s=o['T']/2,horizon_s=1.5*o['T'],
        period_s=o['T'],**(impact or dict(impact_time_s=None,impact_longitude_deg_east=None,impact_orbits=None)))


def counts(rows,height):
    subset=[x for x in rows if x['release_height_m']==height]
    c={s:sum(x['status']==s for x in subset) for s in ['outbound_collision','return_impact','not_arrested']}
    clear=c['return_impact']+c['not_arrested']
    return dict(release_height_m=height,total=len(subset),outbound_clear=clear,outbound_clear_fraction=clear/len(subset),
        conditional_return_impact_fraction=c['return_impact']/clear if clear else None,**c)


def run():
    initialize()
    with ProcessPoolExecutor(max_workers=4,initializer=initialize) as pool:
        thresholds=[]
        for row in pool.map(threshold,range(360),chunksize=1):
            thresholds.append(row)
            if len(thresholds)%30==0:print(f'Thresholds: {len(thresholds)}/360',flush=True)
        sorted_h=sorted(r['clearance_threshold_m'] for r in thresholds)
        # Strict clearance excludes the grazing equality; round upward to .1 m.
        h50=np.ceil((sorted_h[179]+.001)*10)/10
        heights=sorted(set([3.,10.,30.,100.,300.,1000.,3000.,6000.,10000.,h50]))
        rows=[]
        for height in heights:
            rr=list(pool.map(classify,[(lon,height,False) for lon in range(360)],chunksize=1));rows+=rr
            print(json.dumps(counts(rr,height)),flush=True)
        # Full 360-case classification check with half-cell subdivision at H50.
        fine=list(pool.map(classify,[(lon,h50,True) for lon in range(360)],chunksize=1))
    selected=[r for r in rows if r['release_height_m']==h50]
    assert all(a['status']==b['status'] for a,b in zip(selected,fine))
    errors=[abs(a['impact_time_s']-b['impact_time_s']) for a,b in zip(selected,fine) if a['impact_time_s'] is not None]
    assert max(errors,default=0)<1e-5
    summary=[counts(rows,h) for h in heights]
    # Validate that site thresholds predict every independent height-scan outcome.
    by_lon={t['longitude_deg_east']:t['clearance_threshold_m'] for t in thresholds}
    for row in rows:
        assert (row['status']!='outbound_collision') == (row['release_height_m']>by_lon[row['longitude_deg_east']])
    assert next(c for c in summary if c['release_height_m']==h50)['outbound_clear']>=180
    result=dict(model='Equatorial point release, prograde, local height above SLDEM2015; periapsis release, 25 km apoapsis catcher, two-body gravity and rotating terrain',
        mu_m3_s2=MU,reference_radius_m=RADIUS,moon_spin_rad_s=MOON_OMEGA,catcher_altitude_m=25000,max_payload_orbits=1.5,
        longitude_spacing_deg=1,site_count=360,threshold_180th_m=sorted_h[179],threshold_181st_m=sorted_h[180],selected_height_for_at_least_50_percent_m=float(h50),
        height_scan=summary,site_thresholds=thresholds,trajectories=rows,
        validation=dict(half_cell_all_360_classifications_agree=True,all_scanned_heights_agree_with_site_thresholds=True,max_impact_time_change_s=max(errors,default=0)),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        terrain_manifest_sha256=hashlib.sha256((OUT.parent/'terrain/band_manifest.json').read_bytes()).hexdigest())
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,data in [('site_thresholds.csv',thresholds),('trajectories.csv',rows),('height_scan.csv',summary)]:
        with (OUT/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    plot(result)
    print('FINAL',json.dumps({k:v for k,v in result.items() if k not in ['site_thresholds','trajectories']}),flush=True)


def plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    palette=['#b85543','#53866a','#4d7da5'];labels=['Departure blocked','Clears outbound, then impacts','Clear through 1.5 payload orbits']
    hs=np.sort([x['clearance_threshold_m'] for x in result['site_thresholds']]);h50=result['selected_height_for_at_least_50_percent_m']
    fig,axs=plt.subplots(2,1,figsize=(11,8),layout='constrained')
    axs[0].step(np.maximum(hs,.001),np.arange(1,361)/3.6,where='post',color='#265e80')
    axs[0].axvline(h50,color='black',ls=':',label=f'50% height: {h50:.1f} m');axs[0].axvline(10,color='#b37b30',ls='--',label='10 m reference')
    axs[0].axhline(50,color='gray',lw=.8);axs[0].set_xscale('log');axs[0].set_xlim(1,max(10000,hs[-1]*1.1));axs[0].set_ylim(0,101)
    axs[0].set_ylabel('Outbound-clear sites (%)');axs[0].set_xlabel('Release height above local terrain (m)');axs[0].legend();axs[0].grid(alpha=.2)
    summary=result['height_scan'];positions=np.arange(len(summary));bottom=np.zeros(len(summary))
    for key,label,color in zip(['outbound_collision','return_impact','not_arrested'],labels,palette):
        vals=np.array([c[key] for c in summary]);axs[1].bar(positions,vals,bottom=bottom,color=color,label=label)
        for x,y,b in zip(positions,vals,bottom):
            if y>15:axs[1].text(x,b+y/2,str(y),ha='center',va='center',color='white',fontsize=9)
        bottom+=vals
    axs[1].set_xticks(positions,[f'{c["release_height_m"]:g}' for c in summary]);axs[1].set_xlabel('Release height above local terrain (m)');axs[1].set_ylabel('Sites (360 total)');axs[1].legend(loc='upper center',bbox_to_anchor=(.5,-.19),fontsize=9,ncol=1)
    fig.suptitle('Single equatorial release: height needed to clear terrain\n25 km prograde apoapsis catcher; 360 longitudes; correct launch, missed capture')
    fig.savefig(OUT/'height_scan.png',dpi=160,bbox_inches='tight');fig.savefig(OUT/'height_scan.svg',bbox_inches='tight');plt.close(fig)
    rows=[r for r in result['trajectories'] if r['release_height_m']==h50];mapping={'outbound_collision':0,'return_impact':1,'not_arrested':2}
    fig,ax=plt.subplots(figsize=(13,2.7),layout='constrained')
    ax.imshow([[mapping[r['status']] for r in rows]],aspect='auto',cmap=ListedColormap(palette),vmin=0,vmax=2,extent=(-.5,359.5,-.5,.5),interpolation='nearest')
    ax.set_yticks([]);ax.set_xticks(range(0,360,30));ax.set_xlabel('Release longitude (degrees east)');ax.set_title(f'Outcomes at {h50:.1f} m above local ground')
    ax.legend(handles=[Patch(color=c,label=l) for c,l in zip(palette,labels)],loc='upper center',bbox_to_anchor=(.5,-.35),ncol=3,fontsize=9)
    fig.savefig(OUT/'longitude_outcomes.png',dpi=160,bbox_inches='tight');fig.savefig(OUT/'longitude_outcomes.svg',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':run()
