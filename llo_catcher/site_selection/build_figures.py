"""Blog navigation figures and hub-relative diagnostic footprint maps."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from ..analysis.single_equatorial_release.directional_sites import build_maps
ROOT=Path(__file__).parent

def main():
    survey=json.loads((ROOT.parent/'analysis/single_equatorial_release/directional_sites/degree_survey.json').read_text())
    colors=['#b85543','#53866a','#4d7da5'];labels=['Hits before catcher','Clears; impacts after miss','Clears; no impact by 1.5 orbits']
    states={'outbound_collision':0,'return_impact':1,'not_arrested':2}
    fig,axes=plt.subplots(2,1,figsize=(13,5),layout='constrained')
    for ax,d in zip(axes,['east','west']):
        rows=survey[d];values=[states[r['status']] for r in rows]
        ax.imshow([values],extent=(-.5,359.5,0,1),aspect='auto',interpolation='nearest',cmap=ListedColormap(colors),vmin=0,vmax=2)
        for r in rows:
            if r['status']!='outbound_collision':
                x=r['longitude_deg_east'];ax.plot([x,x],[1,1.12],color='#53866a',clip_on=False)
        counts=[values.count(k) for k in range(3)]
        ax.set(yticks=[],xlim=(-.5,359.5),xticks=np.arange(0,360,30),title=f'{d.capitalize()}ward: {counts[0]} blocked, {counts[1]} clear then impact, {counts[2]} clear without impact',xlabel='Longitude east (degrees)')
    fig.suptitle('Initial search: equatorial release 10 m above LOCAL ground\n25 km catcher · one-degree samples · before choosing or raising hilltop hubs',fontsize=13)
    axes[-1].legend(handles=[Patch(color=c,label=l) for c,l in zip(colors,labels)],loc='upper center',bbox_to_anchor=(.5,-.4),ncol=3,fontsize=9)
    for ext in ['png','svg']:fig.savefig(ROOT/f'search_outcomes.{ext}',dpi=180)
    plt.close(fig)
    # Reuse the reviewed terrain styling, with the new plane/radius values.
    build_maps.ROOT=ROOT/'maps';build_maps.ROOT.mkdir(exist_ok=True)
    build_maps.main()
    for p in ROOT.rglob('*.svg'):p.write_text('\n'.join(x.rstrip() for x in p.read_text().splitlines())+'\n')
if __name__=='__main__':main()
