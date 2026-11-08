"""Validate saved comparisons and record source provenance."""
import hashlib,json,platform
from pathlib import Path
import numpy as np
import scipy
from .compare import OUT,REFERENCE

def main():
    root=Path(__file__).resolve().parents[2]
    data=json.loads((OUT/'comparison.json').read_text())
    for row in data['rows']:
        c=row['conveyor'];s=row['spool']
        assert abs(s['mean_flow_kg_s']/data['matched_mean_flow_kg_s']-1)<1e-10
        assert s['force_integral_relative_error']<1e-6
        if 'material_mass_kg' not in c:
            assert c['unloaded_stress_Pa']>row['allowance_Pa'];continue
        assert abs(c['mass_flow_kg_s']/data['matched_mean_flow_kg_s']-1)<1e-10
        assert abs(c['release_center_speed_m_s']/data['matched_release_speed_m_s']-1)<1e-6
        assert abs(c['max_stress_GPa']*1e9/row['allowance_Pa']-1)<1e-6
        assert c['integrated_force_residual_scaled']<1e-5
        assert c['min_effective_tension_N']>0
        assert c['boundary_residual']<1e-7
    same=json.loads((OUT/'same_mass.json').read_text());c=same['conveyor']
    assert abs(c['bare_loop_mass_kg']/same['common_material_mass_kg']-1)<1e-7
    assert abs(c['mass_flow_kg_s']/data['matched_mean_flow_kg_s']-1)<1e-10
    assert abs(c['release_center_speed_m_s']/data['matched_release_speed_m_s']-1)<1e-6
    files=[Path(__file__).with_name(n) for n in ['compare.py','plot.py','validate.py']]
    files += [REFERENCE,root/'sling_launcher/cable_shape.py',root/'sling_launcher/orbit.py',
              root/'sling_launcher/conveyor_loop/steady/model.py',root/'sling_launcher/environment.py']
    manifest=dict(checks='All saved-scenario assertions passed',python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
                  sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(manifest['checks'])
if __name__=='__main__':main()
