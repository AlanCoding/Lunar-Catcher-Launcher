"""Publication terrain-envelope figure and a four-hill comparison."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .calculate import ROOT
plt.rcParams.update({'svg.fonttype':'none','font.size':13})

def save(fig,name):
    for ext in ['png','svg']:fig.savefig(ROOT/f'{name}.{ext}',dpi=180,bbox_inches='tight')
    plt.close(fig)

def main():
    d=json.loads((ROOT/'results.json').read_text());chosen=d['selected_site'];s=next(a for a in d['summaries'] if a['site']==chosen);profile=next(a['profile'] for a in d['profiles'] if a['site']==chosen)
    x=np.array([a['radius_m']/1000 for a in profile]);y=np.array([a['max_tangent_height_m'] for a in profile])
    fig,ax=plt.subplots(figsize=(11,6),layout='constrained')
    ax.axhline(0,color='#797d80',lw=1,label='Hub tangent plane')
    ax.fill_between(x,y,0,color='#dce5e3',alpha=.6)
    ax.plot(x,y,color='#28665f',lw=2.7,label='Highest terrain around each ring')
    ax.axvline(s['tip_radius_m']/1000,color='#b37837',ls='--',lw=1.5,label=f"Release radius · {s['tip_radius_m']/1000:.3f} km")
    ax.scatter([s['tip_radius_m']/1000],[s['tip_ring_height_m']],c='#b37837',s=45,zorder=5)
    ax.annotate(f"{abs(s['tip_ring_height_m']):.1f} m below hub tangent plane",(s['tip_radius_m']/1000,s['tip_ring_height_m']),xytext=(-15,-35),textcoords='offset points',ha='right',fontsize=12,arrowprops=dict(arrowstyle='-',color='#b37837'))
    ax.axvline(d['track_radius_m']/1000,color='#777777',lw=.8,ls=':')
    ax.annotate('Rover track · 76.79 m',(d['track_radius_m']/1000,s['track_ring_height_m']),xytext=(35,22),textcoords='offset points',fontsize=11,arrowprops=dict(arrowstyle='-',color='#777777'))
    ax.set(xlim=(0,6.5),xlabel='Horizontal radius from hub (km)',ylabel='Maximum terrain height relative to hub tangent plane (m)')
    ax.set_title(f"{chosen} · Terrain clearance around a hilltop launcher\nHub {s['hub_latitude_deg']:+.6f}°, {s['hub_longitude_deg']:+.6f}°",fontsize=17,pad=18)
    ax.set_ylim(min(y.min()-55,-100),55);ax.grid(alpha=.2);ax.legend(loc='lower left',fontsize=11)
    save(fig,'selected_hill_terrain')
    fig,ax=plt.subplots(figsize=(11,6),layout='constrained')
    for a in d['profiles']:
        xx=np.array([r['radius_m']/1000 for r in a['profile']]);yy=[r['max_tangent_height_m'] for r in a['profile']]
        ax.plot(xx,yy,lw=2,label=a['site'])
    ax.axhline(0,color='#777777',lw=.7);ax.axvline(d['common_comparison_radius_m']/1000,color='#777777',ls=':',label='Common ranking radius')
    ax.set(xlim=(0,6.5),xlabel='Horizontal radius from hub (km)',ylabel='Maximum terrain height relative to hub tangent plane (m)',title='Four adjusted hilltops · maximum terrain around each ring');ax.grid(alpha=.2);ax.legend()
    save(fig,'four_hill_comparison')
    lines=['# Radial terrain envelope for the featured hill','',
      '[Publication packet](../publication/README.md) · [Separate sling sag/taper plan](../../../sling_launcher/sag_taper_trade/README.md)','',
      f"**{chosen} is the selected terrain-profile illustration.** It has the greatest mean drop of the maximum-around-ring terrain envelope over the common comparison interval, from the 76.79 m track to {d['common_comparison_radius_m']/1000:.3f} km. This terrain-only ranking describes how much vertical space the hill provides; the sling-design study will combine it with the cable shape and support loads.",'',
      '**[Lowered-release check](LOWERED_RELEASE.md):** eastward departure tested after subtracting the reference pole height, and at 100, 200 and 300 m below the hub tangent plane.','', '## Publication figure','',
      '![Terrain versus radius](selected_hill_terrain.png)','',
      '[PNG](selected_hill_terrain.png) · [SVG](selected_hill_terrain.svg) · [Four-hill comparison](four_hill_comparison.png) ([SVG](four_hill_comparison.svg)).','',
      'Each plotted value is the **highest ground point around the entire circle at that radius**, measured vertically relative to the hub’s tangent plane. Negative values put the entire sampled ring below that plane. Lunar curvature is included. The profile preserves intermediate rises, which may control cable clearance.','',
      f"At {chosen}’s {s['tip_radius_m']/1000:.3f} km release radius, the highest ground is **{abs(s['tip_ring_height_m']):.1f} m below the hub tangent plane**. With the existing endpoint plane 1.3768 m above that reference, this recovers **{s['tip_clearance_check_m']:.1f} m** of tip-circle clearance. At the rover-track radius the ring maximum is {s['track_ring_height_m']:.2f} m relative to the hub plane.",'',
      '## Four-hill selection','',
      '| Hill | Mean ring drop over common interval (m) | Maximum ground at own tip (m relative to hub plane) | Own tip radius (km) |',
      '|---|---:|---:|---:|']
    for a in sorted(d['summaries'],key=lambda a:-a['mean_ring_drop_m']):lines.append(f"| {a['site']} | {a['mean_ring_drop_m']:.1f} | {a['tip_ring_height_m']:.1f} | {a['tip_radius_m']/1000:.3f} |")
    lines+=['',
      'Mean ring drop is the radial integral of −T(r), divided by the comparison interval length. This common interval makes the terrain comparison independent of the slightly different tip radii. The curves can cross: the ranking is a scalar summary of available terrain drop. A final support-height ranking depends on the chosen tether profile and clearance requirement.','',
      '## Numerical method and checks','',
      'Use R = 1,737,400 m and the stored summit height h₀. At horizontal radius r, sample terrain elevation h at the spherical destination whose central angle satisfies r = (R + h) sin θ. The projected height is z = (R + h) cos θ − (R + h₀). Iterate the angle five times against bilinear SLDEM2015 terrain, then maximize z around the ring.','',
      'Radii extend from 0 to 6.5 km every 12.5 m, with the track and each tip radius included explicitly. Angular spacing is at most 15 m along the horizontal ring, with a minimum of 128 bearings. Refine the five highest sampled local peaks to resolve competing terrain maxima. A 30 m angular-spacing calculation checks the coarser radial grid and design radii.','',
      f"The largest angular-refinement change across the four hills is {max(a['max_angular_refinement_change_m'] for a in d['summaries']):.3f} m. Changing radial spacing from 25 m to 12.5 m changes the mean-drop metric by at most {max(a['radial_score_change_m'] for a in d['summaries']):.3f} m. Tip-circle clearance agrees with the earlier independent rim calculation to within {max(abs(a['tip_clearance_difference_m']) for a in d['summaries']):.3f} m.",'',
      'These checks measure numerical consistency on the interpolated DEM. The native grid is approximately 59 m; terrain uncertainty and unresolved obstacles require separate engineering margins. The r = 0 value is fixed to the summit reference. The spherical projection gives the expected downward curvature away from the tangent plane.','',
      '## Design handoff','',
      'For a cable drop d(r) below support datum H and vertical clearance allowance c(r), the steady geometric requirement is H ≥ max[T(r) + d(r) + c(r)] over the cable’s occupied radii. Pole lengths also depend on the terrain at their bases. The [sag/taper work item](../../../sling_launcher/sag_taper_trade/README.md) will calculate d(r), material stress, taper and support loads. This terrain figure supplies T(r).','',
      '## Files and reproduction','',
      '- Profiles: [P1](P1_profile.csv), [P2](P2_profile.csv), [P3](P3_profile.csv), [P4](P4_profile.csv). Columns include radius, maximum tangent-plane height, radial-elevation difference at that point, and controlling azimuth (clockwise from north).',
      '- [Results, selection metric, convergence checks and source hash](results.json); [flat-sphere projection check](validation.json).',
      '- Code: [calculate.py](calculate.py), [report.py](report.py).','',
      '```bash','export MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache','export OPENBLAS_NUM_THREADS=1',
      '.env/hub/bin/python -m llo_catcher.site_selection.radial_terrain.calculate',
      '.env/hub/bin/python -m llo_catcher.site_selection.radial_terrain.report','```','']
    (ROOT/'README.md').write_text('\n'.join(lines))
if __name__=='__main__':main()
