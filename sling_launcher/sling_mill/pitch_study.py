"""Independent station-pitch study at fixed drum and payload dimensions."""
import csv,json
import numpy as np
import matplotlib.pyplot as plt
from run import ROOT,compute,save
from kinematics import evaluate
from draw import system_pattern,drum,save as save_drawing


def main():
    base=json.loads((ROOT/'config.json').read_text())
    rows=[]
    for pitch in [.20,.22,.25,.30,.40,.50,.60,.75,.90,1.0,1.1]:
        c=base.copy();c['pitch']=pitch
        # Resolve the same 20-mm contact patch at every pitch.
        c['integration_steps_per_pitch']=max(60,int(np.ceil(pitch/(c['contact_patch']/10))))
        row=dict(pitch_m=pitch,clear_gap_m=pitch-2*c['radius'],rod_length_over_pitch=c['payload_length']/pitch)
        try:
            r,st,mass=compute(c)
            row.update(status='Contact covered',installed_pairs=r['installed_pairs'],
                ideal_power_MW=r['ideal_power_W']/1e6,sliding_heat_MW=r['slip_heat_W']/1e6,
                peak_pair_traction_kN=r['contact_peak_force_pair_N']/1000,
                peak_normal_per_drum_kN=float(st['normal_per_drum_N'].max()/1000),
                maximum_belt_thickness_mm=r['maximum_belt_thickness_m']*1000,
                euler_buckling_load_kN=r['stability']['buckling_load_N']/1000,
                fiber_mass_t=sum(mass[k] for k in ['outer_belts','radial_cables','torque_cables'])/1000,
                conditional_inventory_t=r['conditional_installed_mass_kg']/1000,
                installed_drive_rating_MW=r['peak_installed_motor_power_W']/1e6,
                energy_error_fraction=r['energy_error_fraction'])
        except ValueError as error:
            row.update(status=str(error),**{k:float('nan') for k in rows[0] if k not in row and k!='status'})
        rows.append(row)
    with (ROOT/'results/pitch_sweep.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    rr=[r for r in rows if r['status']=='Contact covered'];x=[r['pitch_m'] for r in rr]
    fig,axes=plt.subplots(2,2,figsize=(11,7))
    metrics=[('installed_pairs','Installed drum pairs'),('peak_pair_traction_kN','Peak traction per pair (kN)'),('sliding_heat_MW','Total sliding heat (MW)'),('fiber_mass_t','Conditional belt + cable inventory (t)')]
    for ax,(key,label) in zip(axes.flat,metrics):
        ax.plot(x,[r[key] for r in rr],'o-',color='#426e60')
        ax.axvline(.30,color='#a25c43',ls='--',alpha=.8,label='Illustrated 0.30 m pitch')
        ax.set(xlabel='Station pitch (m)',ylabel=label);ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=9)
    fig.suptitle('Pitch alone varies · 0.20 m drums · 1 m rods · fixed 10 Mt/year')
    fig.tight_layout();save(fig,'pitch_tradeoffs')
    # Scale-comparable short corridor sections.
    from matplotlib.patches import Rectangle
    fig,axs=plt.subplots(4,1,figsize=(12,8),sharex=True)
    for ax,pitch in zip(axs,[.22,.30,.50,.75]):
        R=base['radius'];D=base['payload_depth'];h=R*base['hub_ratio']
        for xx in np.arange(pitch/2,2.05,pitch):
            drum(ax,(xx,R+D/2),R,h,1,6);drum(ax,(xx,-R-D/2),R,h,-1,6)
        ax.add_patch(Rectangle((.1,-D/2),base['payload_length'],D,fc='#c9bb98',ec='#665c43'))
        ax.text(2.16,.04,f'Pitch {pitch:.2f} m\nGap {pitch-2*R:.2f} m\nL / pitch = {1/pitch:.2f}',fontsize=11,va='center')
        ax.set(aspect='equal',xlim=(-.02,2.65),ylim=(-.25,.25));ax.axis('off')
    fig.suptitle('Spacing alternatives · identical drum and rod dimensions',fontsize=16)
    fig.tight_layout();save_drawing(fig,'04_pitch_comparison')
    spaced=json.loads((ROOT/'config_spaced.json').read_text())
    k,_=evaluate(spaced);system_pattern(spaced,k)
    text=['# Drum spacing: an independent design variable','', '[Sling mill overview](README.md) · [Model](MODEL.md) · [CSV](results/pitch_sweep.csv)','',
    'Station pitch is independent of drum radius. Increasing it beyond 2R creates a physical gap while reducing the number of pairs. The original handoff example has 200 mm drums on 200 mm pitch; that remains the numerical validation case. The **system-pattern drawing now uses 300 mm pitch, giving a 100 mm clear gap**, with the same drums and rods. Its full parameter file is [config_spaced.json](config_spaced.json).','',
    '![Spacing alternatives](figures/04_pitch_comparison.svg)','',
    '## Fixed inputs and measured consequences','',
    'This sweep holds drum diameter at 200 mm, hub radius at 25 mm, rod dimensions at 1 m × 60 mm × 40 mm, acceleration at 1,000 g, entry/exit speeds at 100/1,600 m/s, and throughput at 10 million tonnes/year. It changes only station pitch. Contact-patch integration resolution is increased with pitch so narrow edge transitions remain resolved.','',
    '| Pitch m | Clear gap m | Installed pairs | L/pitch | Peak pair traction kN | Sliding heat MW | Conditional fiber tonnes |','|---:|---:|---:|---:|---:|---:|---:|']
    for row in rr:
        text.append(f'| {row["pitch_m"]:.2f} | {row["clear_gap_m"]:.2f} | {row["installed_pairs"]} | {row["rod_length_over_pitch"]:.2f} | {row["peak_pair_traction_kN"]:.2f} | {row["sliding_heat_MW"]:.3f} | {row["fiber_mass_t"]:.3f} |')
    text+=['', 'L/pitch describes mean engagement in the uniform interior. Actual contact count is discrete, with fractional patch overlap at rod ends. For example, the 300 mm layout generally shares traction among three or four pairs. The force peaks reflect the moments with fewer engaged pairs.','',
    '![Pitch tradeoffs](results/pitch_tradeoffs.svg)','',
    '## Interpretation','',
    '- **Fewer stations:** pitch increases reduce installed drum pairs, foundations and local mechanisms. Active acceleration distance, mass flow and ideal kinetic power stay fixed.',
    '- **Higher individual loads:** fewer simultaneous contacts must still supply the same total rod acceleration. Normal force, torque and local belt/cable loads increase. Peak loads change unevenly as the discrete engagement pattern changes.',
    '- **Slip heat remains close to the original value:** each station still contacts a passing 1 m rod. Rod length and acceleration govern much of the per-contact speed range. Station spacing changes the discrete sharing and edge details, producing smaller variations in total heat.',
    '- **Longer unsupported rod spans:** bending and buckling checks worsen. The modeled Euler load scales as 1/pitch²; actual guide support and internal axial-force distribution must be resolved.',
    '- **An engagement limit eventually appears:** the 1.10 m case has intervals with no contact for a 1 m rod and 20 mm patches. The constant-acceleration model rejects it. A different acceleration program with coasting could be studied explicitly.',
    '- **The flexible-contact screen remains open:** fiber inventory and full hardware estimates retain the earlier panel-model limitations. Increasing pitch is permitted and useful to explore, but its larger per-drum loads do not automatically resolve contact support.',
    '', 'The 300 mm illustration is a clear example with space between drums. It is a candidate layout, with no optimum selected. [The complete CSV](results/pitch_sweep.csv) also gives normal loads, conditional system mass, motor ratings, belt thickness and buckling screens.','',
    '## Reproduce','', '```bash','MPLCONFIGDIR=/tmp/lunar-sling-mpl-cache OPENBLAS_NUM_THREADS=1 .env/hub/bin/python sling_launcher/sling_mill/pitch_study.py','```','',
    'The script regenerates this page, both pitch-study figures and the main system-pattern drawing. The main `run.py` also uses `config_spaced.json` for that drawing while retaining the original baseline for its numerical results.','']
    (ROOT/'PITCH_STUDY.md').write_text('\n'.join(text))
    print('\n'.join(str(row) for row in rows))
if __name__=='__main__':main()
