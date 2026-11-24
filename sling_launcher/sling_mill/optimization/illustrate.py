"""Small-radius retention and roller-gap sensitivity, with stated assumptions."""
import sys,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from contact import normal_force,compliance
c=json.loads((ROOT/'config_spaced.json').read_text());a=json.loads((ROOT/'optimization/assumptions.json').read_text())
def save(fig,name):
    for ext in ['svg','png']:fig.savefig(ROOT/'optimization/results'/f'{name}.{ext}',dpi=160,bbox_inches='tight')
    plt.close(fig)
plt.rcParams['svg.fonttype']='none'
r=np.geomspace(.05,5,150)
fig,ax=plt.subplots(figsize=(8,4.5))
for t in [.0001,.0005,.001]:
    ax.loglog(r,a['coating_density_kg_m3']*t*c['v_exit']**2/r/1e6,label=f'{t*1000:g} mm layer')
ax.axhline(a['bond_tensile_allowable_Pa']/1e6,color='brown',ls='--',label='Assumed 5 MPa bond limit')
ax.set(xlabel='Drum radius (m)',ylabel='Required centrifugal bond traction (MPa)',title='Contact-layer retention at 1,600 m/s · 1,400 kg/m³')
ax.grid(alpha=.2);ax.legend();save(fig,'layer_retention')
interference=np.linspace(0,.0005,200)
fig,axs=plt.subplots(1,2,figsize=(11,4))
N=normal_force(interference/2,c['radius'],c['payload_width'],compliance(a))
axs[0].plot(interference*1e6,N/1000,color='#426e60')
axs[0].set(ylabel='Normal force per drum (kN)')
axs[1].plot(interference*1e6,interference/2/compliance(a)/1e6,color='#49677e')
axs[1].set(ylabel='Peak contact pressure (MPa)')
for ax in axs:ax.set_xlabel('Bar thickness minus roller gap (µm)');ax.grid(alpha=.2)
fig.suptitle('Gap sensitivity · 200 mm drums · 60 mm bar width · illustrative compliance')
fig.tight_layout();save(fig,'gap_sensitivity')
