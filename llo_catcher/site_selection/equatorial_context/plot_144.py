"""Regenerate the publication's 144-degree trajectory illustration."""
from pathlib import Path
import json
import numpy as np
from ..support import equatorial as c
OUT=Path(__file__).resolve().parent

def main():
    c.initialize()
    result=json.loads((OUT/'east_corridors.json').read_text())
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(12,5.7),layout='constrained');o=c.orbit(144,10.)
    lon=np.arange(144,240,1/512);ground=c.terrain(np.radians(lon))/1000
    r,_,_,_=c.at_longitude(np.radians(lon-144),o)
    ax.plot(lon,ground,color='#82745f',lw=1,label='Equatorial terrain');ax.plot(lon,(r-c.RADIUS)/1000,color='#265e80',lw=2,label='Payload released at 144° E, 10 m above local ground')
    b=result['audit_144']['regional_mountain'];x=b['longitude_deg'];y=b['payload_elevation_m']/1000
    ax.scatter([x],[y],color='#265e80',s=35);ax.annotate(f'Later mountain range: {b["clearance_m"]:.1f} m clearance',xy=(x,y),xytext=(160,13),arrowprops=dict(arrowstyle='->'),fontsize=10)
    ax.set_xlim(144,240);ax.set_xlabel('Longitude east (degrees)');ax.set_ylabel('Elevation above reference sphere (km)');ax.set_title('Why 144° E clears: compare terrain with the rising orbital trajectory');ax.grid(alpha=.2);ax.legend(loc='upper left')
    fig.savefig(OUT/'trajectory_144.png',dpi=160,bbox_inches='tight');fig.savefig(OUT/'trajectory_144.svg',bbox_inches='tight');plt.close(fig)

if __name__=='__main__':main()
