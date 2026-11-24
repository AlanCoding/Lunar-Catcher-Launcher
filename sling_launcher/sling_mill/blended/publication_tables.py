"""Refresh numerical publication tables without rewriting editorial prose."""
from pathlib import Path
import json,re
P=Path(__file__).parent

def refresh():
    d=json.loads((P/'search_results/iron_reference.json').read_text());c=d['parameters'];s=d['summary'];m=d['masses']
    ratios=json.loads((P/'search_results/architecture_taper_comparison.json').read_text())
    g=s['acceleration_exit_m_s2']/9.80665
    rows=[('Useful delivery','10 million tonnes per 365 operating days (317.10 kg/s)'),
      ('Exit speed',f"{c['v_exit']:,.0f} m/s"),
      ('Iron bar dimensions',f"{c['payload_length']:.3f} m × {c['payload_width']*1000:.1f} mm × {c['payload_depth']*1000:.2f} mm"),
      ('Bar mass / feed frequency',f"{s['payload_mass_kg']:.3f} kg / {s['launch_frequency_Hz']:.2f} bars/s"),
      ('Maximum acceleration',f"{g:.1f} Earth g"),
      ('Roller diameter / station pitch',f"{2*c['radius']:.3f} m / {c['radius']*c['pitch_over_radius']:.3f} m"),
      ('Accelerator length',f"{s['corridor_length_m']/1000:.3f} km"),
      ('Mean electrical input',f"{s['electrical_mean_W']/1e6:.2f} MW"),
      ('Structural Zylon working ceiling','1.0 GPa; tapered drum cables assumed'),
      ('Peak belt stress including traction',f"{s['maximum_belt_stress_Pa']/1e9:.3f} GPa"),
      ('Largest drum-cable area taper',f"{ratios['sling_mill']['taper_area_ratio']:.2f}:1"),
      ('Iron axial working allowable','70 MPa'),
      ('Accelerator hardware',f"{(sum(m.values())-m['solar_array'])/1000:,.0f} tonnes"),
      ('Full-sun solar array',f"{m['solar_array']/1000:,.0f} tonnes"),
      ('**Total included mass**',f"**{sum(m.values())/1000:,.0f} tonnes**"),
      ('**Gross mass payoff**',f"**{s['gross_operating_payback_hours']:.2f} operating hours**")]
    reference='| Quantity | Selected reference |\n|---|---:|\n'+''.join(f'| {k} | {v} |\n' for k,v in rows)
    comparison=f'''| Design | Payload acceleration | Structural fiber working stress | Useful flow (kg/s) | Gross mass payoff | Included inventory |
|---|---|---|---:|---|---|
| **[Sling mill](../blended/IRON_REFERENCE.md)** | **{g:.1f} g maximum** | Zylon, 1.0 GPa with tapered drum cables | **{s['mass_flow_kg_s']:.2f}** | **{s['gross_operating_payback_hours']:.2f} operating hours** | **{sum(m.values())/1000:,.0f} t**: accelerator hardware, foundations, cooling and full-sun solar |
| [Go-kart sling](../../publication/MASS_PAYOFF.md) | 50 g at release | Tapered Kevlar, 1.0 GPa | 0.151 | 188 operating days | 2,446 t: equipment, solar and local ballast, within the source study's exclusions |
| [Slider straw](../../lunar_slider_straw/RING_REFERENCE.md) | 50 g at release | Tapered Kevlar, 2.438 GPa in the recorded 3:1 sizing case | 1.206 | 22.4 operating days | 2,329 t: installed machine, foundations, solar and battery |
| [Conveyor](../../architecture_comparison/publication/TECH_NOTE.md) | Approximately 50 g rotational scale near tip | 2.9 GPa | 0.151 | **2.41 operating hours, tether-only** | 1.308 t useful-arm loop; opposing arm and hardware additional |
'''
    structural='| Design | Structural fiber | Working stress (GPa) | Specific working stress (MJ/kg) | Area taper, root:tip |\n|---|---|---:|---:|---:|\n'
    for key,label,fiber in [('sling_mill','Sling mill','Zylon'),('go_kart','Go-kart sling','Kevlar'),('slider_straw','Slider straw','Kevlar'),('conveyor','Conveyor','Zylon')]:
        v=ratios[key]
        structural+=f"| {label} | {fiber} | {v['stress_GPa']:.3f} | {v['specific_stress_MJ_kg']:.3f} | {v['taper_area_ratio']:.2f}:1 |\n"
    comparison=structural+"\nTaper is the ratio of material cross-sectional **areas**. For a round cable, the diameter ratio is its square root. The mill value is the last-stage radial/torque cable ratio; its outer belt is constant-section. Specific working stress is working stress divided by fiber density. These are the sizing assumptions of each recorded case; the mill's computed peak belt stress is 0.922 GPa.\n\n"+comparison
    matched=json.loads((P/'search_results/conveyor_matched_acceleration.json').read_text())
    fm=matched['mill']
    paired='| Design | Conveyor circulation speed | Structural fiber mass | Fiber-only gross payoff |\n|---|---:|---:|---:|\n'
    paired+=f"| **Sling mill** | — | **{fm['structural_fiber_mass_kg']/1000:.2f} t** | **{fm['fiber_payoff_s']:.1f} seconds** |\n"
    for v in matched['cases']:
        paired+=f"| Conveyor, opposed pair | {v['feed_speed_m_s']:.0f} m/s | {v['opposed_pair_fiber_mass_kg']/1000:,.2f} t | {v['opposed_pair_payoff_s']/60:.2f} minutes |\n"
    comparison=comparison[:comparison.index('| [Conveyor](../../architecture_comparison/publication/TECH_NOTE.md) |')]
    comparison+='\n### Matched mill–conveyor comparison\n\nBoth calculations deliver **317.10 kg/s useful payload at 1,600 m/s**, with a **493.6 g maximum modeled loaded acceleration**. Conveyor circulation speed is the line speed through its feed pulley, in addition to the rotation of the entire launcher.\n\n'+paired
    comparison+='\nThe conveyor uses uniform-section Zylon at 2.9 GPa and includes two equally loaded arms, with one arm delivering useful payload and the opposing arm carrying disposable countermass. The mill includes structural belts, radial cables and torque cables in both rollers at every station, sized at a 1.0 GPa working ceiling with taper. Contact layers, motors, structures and power supply are excluded from these **fiber-only** totals. A whole-machine conveyor estimate remains open. [Method, scaling and limitations](PAYLOAD_AND_PAYOFF.md#matched-acceleration-conveyor-comparison).\n'
    # Publication sequence: material assumptions, matched fiber comparison, then whole-machine context.
    legacy_start=comparison.index('| Design | Payload acceleration |')
    matched_start=comparison.index('### Matched mill–conveyor comparison')
    legacy=comparison[legacy_start:matched_start].strip()
    comparison=comparison[:legacy_start]+comparison[matched_start:]+'\n### Earlier complete-machine studies\n\nThese recorded cases use different flows and equipment boundaries.\n\n'+legacy+'\n'
    article=P.parent/'publication/ARTICLE.md';text=article.read_text()
    for name,table in [('REFERENCE_TABLE',reference),('COMPARISON_TABLE',comparison)]:
        pattern=rf'<!-- BEGIN {name} -->.*?<!-- END {name} -->'
        assert len(re.findall(pattern,text,re.S))==1,name
        text=re.sub(pattern,lambda _:f'<!-- BEGIN {name} -->\n\n{table}\n<!-- END {name} -->',text,flags=re.S)
    article.write_text(text)
if __name__=='__main__':refresh()
