"""Extract the selected 50 mph, one-pass family; no new physical calculation."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path(__file__).resolve().parent
rows=json.loads((out/'all_estimates.json').read_text())
rows=[r for r in rows if r['rover_mph']==50 and r['passes']==1 and r['assumptions']['name']=='reference']
plt.rcParams.update({'svg.hashsalt':'50mph-focus','font.size':11})
fig,ax=plt.subplots(figsize=(10,5.8))
x=[r['acceleration_g'] for r in rows]
for key,label,color in [('physical_ratio','Total permanent mass, including local rock','#787878'),('imported_ratio','Imported permanent mass','#2368a0')]:
    ax.plot(x,[r[key] if r.get(key) is not None else np.nan for r in rows],'-o',color=color,label=label,markersize=4)
best=min((r for r in rows if r['converged']),key=lambda r:r['imported_ratio'])
ax.scatter([best['acceleration_g']],[best['imported_ratio']],s=170,marker='*',color='#2368a0',edgecolor='black',zorder=5)
ax.annotate('Sampled imported-mass minimum\n75 g; ratio 1,536',(75,best['imported_ratio']),xytext=(100,1050),arrowprops=dict(arrowstyle='->'),fontsize=10)
bad=[r for r in rows if r['converged'] and not(r['frame_chord_fits'] and r['reel_envelopes_fit'] and r['wheel_envelopes_fit'] and r['pole_source_domain_ok'])]
ax.scatter([r['acceleration_g'] for r in bad],[r['imported_ratio'] for r in bad],marker='x',color='#c24642',label='Section/fit screen fails',zorder=5)
ax.set(xlim=(30,310),ylim=(800,5500),xlabel='Release acceleration (Earth g)',ylabel='Permanent system mass / useful payload mass',title='50 mph • One catcher pass • Reference hardware estimates')
ax.grid(alpha=.2);ax.legend(loc='upper left',fontsize=10)
fig.text(.5,.015,'All points retain unresolved sideways force/moment balance.\nFixed-reduction wheel drives assumed; direct drive has not yet been sized.',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.09,1,1))
for ext in ['svg','png']:
    p=out/f'focus_50mph_one_pass.{ext}';fig.savefig(p,dpi=150,bbox_inches='tight')
    if ext=='svg':p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
plt.close(fig)
