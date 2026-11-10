"""Publication names, scalar ridge summaries, and global-context strip maps."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator, NullFormatter
from ...global_hills.search import GlobalTerrain,RADIUS
ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'svg.fonttype':'none'})

def main():
    source=ROOT.parent/'expanded/results.json';d=json.loads(source.read_text());comp=json.loads((ROOT.parent/'expanded/comparison.json').read_text())
    rows=[r for r in d['rows'] if r['extra_release_height_m']>.1 and r['contact_anomaly_deg']>.05]
    xy=np.radians([[r['contact_longitude_deg'],r['contact_latitude_deg']] for r in rows])*RADIUS
    edges=list(cKDTree(xy).query_pairs(80))
    for region in d['regions']:
        for lon in region['longitudes']:
            ids=sorted([i for i,r in enumerate(rows) if r['region']==region['label'] and r['start_longitude_deg']==lon],key=lambda i:rows[i]['source_north_m'])
            edges.extend((i,j) for i,j in zip(ids,ids[1:]) if rows[j]['source_north_m']-rows[i]['source_north_m']<=126 and np.linalg.norm(xy[j]-xy[i])<=1000)
    a,b=np.array(edges).T
    n,labels=connected_components(coo_matrix((np.ones(len(a)),(a,b)),shape=(len(rows),len(rows))),directed=False)
    groups=[np.where(labels==i)[0] for i in range(n)]
    groups=[g for g in groups if len(set(round(rows[i]['contact_latitude_deg'],5) for i in g))>=3]
    groups.sort(key=lambda g:(float(np.median(xy[g,0])),float(np.median(xy[g,1]))))
    catalog=[];membership={}
    for k,g in enumerate(groups,1):
        rid=f'ER-{k:03d}'
        # Deduplicate to ~59 m map cells before calculating representative statistics.
        cells={}
        for i in g:cells.setdefault(tuple(np.round(xy[i]/59).astype(int)),i)
        ids=list(cells.values());coords=xy[ids];center=np.median(coords,axis=0)
        med=ids[int(np.argmin(np.linalg.norm(coords-center,axis=1)))];rr=rows[med]
        elev=[rows[i]['contact_elevation_m'] for i in g]
        cat=dict(ridge=rid,representative_latitude_deg=rr['contact_latitude_deg'],representative_longitude_deg=(rr['contact_longitude_deg']+180)%360-180,
          longitude_deg_east=rr['contact_longitude_deg'],north_min_km=float(xy[g,1].min()/1000),north_max_km=float(xy[g,1].max()/1000),
          north_south_span_km=float(np.ptp(xy[g,1])/1000),elevation_min_m=float(min(elev)),elevation_max_m=float(max(elev)),
          longitude_min_deg_east=float(xy[g,0].min()/RADIUS*180/np.pi),longitude_max_deg_east=float(xy[g,0].max()/RADIUS*180/np.pi),
          samples=len(g),deduplicated_cells=len(ids),featured_sites=[])
        catalog.append(cat)
        for i in g:membership[i]=rid
    featured=[]
    for c in comp:
        r=c['nearest_hub_contact']
        index=next(i for i,a in enumerate(rows) if a['region']==r['region'] and a['start_longitude_deg']==r['start_longitude_deg'] and a['source_north_m']==r['source_north_m'])
        rid=membership[index];cat=next(a for a in catalog if a['ridge']==rid);cat['featured_sites'].append(c['site'])
        featured.append(dict(site=c['site'],hub_latitude_deg=c['hub_latitude_deg'],hub_longitude_deg=c['hub_longitude_deg'],ridge=rid))
    output=dict(version=1,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),ridges=catalog,featured_hubs=featured,unnamed_contact_samples=len(rows)-len(membership))
    (ROOT/'ridges.json').write_text(json.dumps(output,indent=2)+'\n')
    for filename,items in [('ridges.csv',catalog),('featured_hubs.csv',featured)]:
        with (ROOT/filename).open('w') as f:
            w=csv.DictWriter(f,fieldnames=items[0]);w.writeheader();w.writerows(items)
    lines=['# Eastward launch-ridge catalog','',
      '[Ridge investigation](../README.md) · [Expanded search](../expanded/README.md)','',
      '**ER-001, ER-002, … are study names for mapped contact-ridge segments.** This first catalog contains '+str(len(catalog))+' traced segments from the four regional searches. Names refer to this version of the catalog and should be retained through a crosswalk if future sampling splits or joins segments.','',
      'The algorithm samples four regional longitude windows at 1.5° intervals and the ±6 km equatorial band at 125 m intervals. This finite coverage and spacing can miss qualifying ridges and narrow branches. The catalog therefore describes the features found in this search; further sampling can extend it.','',
      '## Featured ridges','',
      'Coordinates are a representative sampled point on each segment, in signed decimal degrees (north/east positive). Elevations use the lunar reference sphere. The north–south span measures the extent of the mapped samples.','',
      '| Ridge | Associated hub | Representative latitude | Representative longitude | North–south span (km) | Elevation range (m) |',
      '|---|---|---:|---:|---:|---:|']
    for c in catalog:
        if c['featured_sites']:lines.append(f"| {c['ridge']} | {', '.join(c['featured_sites'])} | {c['representative_latitude_deg']:+.6f} | {c['representative_longitude_deg']:+.6f} | {c['north_south_span_km']:.2f} | {c['elevation_min_m']:.0f}–{c['elevation_max_m']:.0f} |")
    lines+=['','## Hilltops and their ridges','',
      '| Hilltop | Hub latitude | Hub longitude | Ridge |','|---|---:|---:|---|']
    for c in featured:lines.append(f"| {c['site']} | {c['hub_latitude_deg']:+.8f} | {c['hub_longitude_deg']:+.8f} | {c['ridge']} |")
    lines+=['','## Equatorial ridge map','',
      '- **[Twelve stacked equatorial strips](equator_strips.png)** ([SVG](equator_strips.svg)): 30° longitude per row, with all named traces and labels for the four featured ridges.',
      '- [Detailed terrain maps of the four featured ridges](../expanded/README.md#terrain-maps).','',
      'The map covers all longitudes. Blue bars locate the four seed-longitude windows, sampled every 1.5°. Terrain contacts can lie beyond those windows because trajectories are followed to apoapsis. Empty areas show where these searches contributed no cataloged traces. The north–south scale is stretched for visibility. The muted terrain background uses coarser sampling; ridge coordinates retain the original native-grid calculations.','',
      'Dark lines show the mapped contact-ridge segments. Orange lines and labels highlight the four segments associated with P1–P4. The expanded analysis provides the required fresh-launch heights along these traces.','',
      '## How a segment is defined','',
      'We keep downstream contacts only (release-height raising >0.1 m and contact anomaly >0.05°). Consecutive samples from a common seed meridian are linked when their seed northing differs by at most 126 m and their contact separation is at most 1 km. Contacts from different seed paths within 80 m are merged to remove repeated discoveries. Connected components with at least three distinct contact latitudes (rounded to 0.00001°) receive names, sorted by median east longitude and then latitude. These thresholds define reproducible connected segments. Nearby branches can remain separate and disconnected portions of one physical ridge can have different names.','',
      'Scalar ranges use the component’s actual contact samples. Representative coordinates are the sample nearest the median coordinates after collapsing repeated samples into approximately 59 m cells. Lines between samples are visual interpolation. We avoid total line length because overlap, branching and incomplete sampling would make it misleading.','',
      f"The catalog excludes {output['unnamed_contact_samples']} isolated or insufficiently traced contact samples from naming. They remain in the source results. The original six geographic groups used broader longitude-based grouping; this catalog separates connected traces within the expanded search.",'',
      'The hub latitudes were selected previously to favor a roughly 5.8 km sling reaching near the equator. Their hubs lie about 3.5–5.2 km north or south of the equator. The expanded ridge search covers ±6 km, which itself limits the mapped segment spans.','',
      '## Data and reproduction','',
      '- [Full ridge table](ALL_RIDGES.md), [CSV](ridges.csv), [JSON with source hash](ridges.json).',
      '- [Publication hilltop–ridge table CSV](featured_hubs.csv).',
      '- [Generator](build.py): `.env/hub/bin/python -m llo_catcher.site_selection.launch_ridges.catalog.build` using the existing environment and DEM cache. This groups existing results; it performs no new orbit search.','']
    (ROOT/'README.md').write_text('\n'.join(lines))
    table=['# All named contact-ridge segments','','[Definitions and scope](README.md). Signed decimal degrees; elevations above the lunar reference sphere.','', '| Ridge | Latitude | Longitude | North–south span (km) | Elevation range (m) | Featured hub |','|---|---:|---:|---:|---:|---|']
    for c in catalog:table.append(f"| {c['ridge']} | {c['representative_latitude_deg']:+.6f} | {c['representative_longitude_deg']:+.6f} | {c['north_south_span_km']:.2f} | {c['elevation_min_m']:.0f}–{c['elevation_max_m']:.0f} | {', '.join(c['featured_sites']) or '—'} |")
    (ROOT/'ALL_RIDGES.md').write_text('\n'.join(table)+'\n')
    terrain=GlobalTerrain();norm=Normalize(-4000,8000);featured_ids={r['ridge'] for r in featured}
    terrain_cmap=LinearSegmentedColormap.from_list('muted_terrain',['#d2dce0','#dde2da','#e6e2d7','#eee6df'])
    for name,nrows,width in [('equator_strips',12,30)]:
        fig,axes=plt.subplots(nrows,1,figsize=(14,1.68*nrows+1),squeeze=False)
        fig.subplots_adjust(left=.10,right=.85,top=.93,bottom=.08,hspace=.55)
        for k,ax in enumerate(axes[:,0]):
            lo=k*width;hi=lo+width
            lon=np.linspace(lo,hi,1600);north=np.linspace(-6,6,101);xx,yy=np.meshgrid(lon,north)
            z=terrain.height(np.degrees(yy*1000/RADIUS),xx)
            ax.imshow(z,extent=[lo,hi,-6,6],origin='lower',aspect='auto',cmap=terrain_cmap,norm=norm)
            for i,j in edges:
                if i not in membership or j not in membership:continue
                lx=xy[[i,j],0]/RADIUS*180/np.pi;ny=xy[[i,j],1]/1000
                if lx.max()<lo or lx.min()>hi:continue
                marked=membership[i] in featured_ids
                ax.plot(lx,ny,color='#ec8e18' if marked else '#283c50',lw=2.3 if marked else 1.1,alpha=.95,zorder=4 if marked else 3)
            for region in d['regions']:
                a=max(lo,min(region['longitudes']));b=min(hi,max(region['longitudes']))
                if b>a:ax.plot([a,b],[7.1,7.1],color='#367da7',lw=4,solid_capstyle='butt')
            for c in catalog:
                if c['ridge'] in featured_ids and lo<=c['longitude_deg_east']<hi:
                    hub=next(s for s,f in zip(d['sites'],featured) if f['ridge']==c['ridge'])
                    hx=hub['longitude_deg_east'];hy=np.radians(hub['hub_latitude_deg'])*RADIUS/1000
                    ax.scatter(hx,hy,marker='*',s=35,c='#ec8e18',edgecolors='black',zorder=6)
                    ax.annotate(c['ridge'],(hx,hy),xytext=(8,10 if hy<0 else -20),textcoords='offset points',fontsize=16,bbox=dict(facecolor='white',alpha=.9,edgecolor='none'),zorder=8)
            ax.axhline(0,color='white',lw=.5,alpha=.65)
            ax.set(xlim=(lo,hi),ylim=(-6.5,8),yticks=[-6,0,6],xticks=np.arange(lo,hi+.01,10))
            ax.set_ylabel('North (km)',fontsize=16)
            if k==nrows-1:ax.set_xlabel('Longitude east (degrees)',fontsize=20,labelpad=8)
            ax.xaxis.set_minor_locator(MultipleLocator(1))
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.tick_params(axis='both',which='major',labelsize=20,length=5)
            ax.tick_params(axis='x',which='minor',length=2.5,width=.7)
        cax=fig.add_axes([.88,.23,.015,.54]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=terrain_cmap),cax=cax)
        cb.set_label('Terrain elevation (m)',fontsize=20,labelpad=10);cb.ax.tick_params(labelsize=20)
        fig.suptitle('Eastward launch ridges · equatorial context\nRegional discoveries on a global map; north–south scale stretched',fontsize=24)
        fig.legend(handles=[Line2D([],[],color='#283c50',label='Named contact traces'),Line2D([],[],color='#ec8e18',lw=2.3,label='Featured ridge'),Line2D([],[],color='#367da7',lw=4,label='Sampled seed-longitude windows')],loc='lower center',ncol=3,fontsize=18)
        for ext in ['png','svg']:fig.savefig(ROOT/f'{name}.{ext}',dpi=180,bbox_inches='tight')
        plt.close(fig)
    print('Catalog:',len(catalog),'segments; featured:',featured,flush=True)
if __name__=='__main__':main()
