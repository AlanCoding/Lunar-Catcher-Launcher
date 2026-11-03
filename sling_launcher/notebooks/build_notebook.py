"""Build the small Phase 4 companion notebook; computations stay in modules."""
from pathlib import Path
import argparse
import nbformat as nbf


def build():
    notebook=nbf.v4.new_notebook()
    notebook.metadata.kernelspec=dict(display_name='Lunar hub study',language='python',name='hub-study')
    md=nbf.v4.new_markdown_cell
    code=nbf.v4.new_code_cell
    notebook.cells=[
        md('# Orbital geometry and conditional cycle bounds\n\n'
           'Phase 4 supporting calculations, not a feasible launcher design. '
           'The reviewed architecture uses fixed deployed slings, two A-frames, '
           'four powered and four passive fore/aft wheels. '
           'See [the review report](../docs/orbit_cycle_review.md) for equations, sources and limitations.'),
        code('from pathlib import Path\nimport sys\n'
             'repo = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "sling_launcher/config.py").is_file())\n'
             'if str(repo) not in sys.path: sys.path.insert(0, str(repo))\n'
             'from dataclasses import asdict\nfrom pprint import pprint\n'
             'from IPython.display import Image, Markdown, display\n'
             'from sling_launcher.study_inputs import OrbitCycleStudy\n'
             'from sling_launcher.run_orbit_cycle import write_results\n'
             'study = OrbitCycleStudy()\nresults = write_results(study)\n'
             'output_dir = repo / "sling_launcher/results"\n'
             'pprint(results["versions"])'),
        md('## 1. Inputs and provenance\n\nSI internally. Environment constants are sourced in environment.py; '
           'mission targets in config.py; illustrative control/scale inputs in study_inputs.py. '
           'Tip tangent height is not pole height. Efficiencies and timing allowances are unverified sensitivities.'),
        code('pprint(asdict(study))\npprint(results["environment_derived"])'),
        md('## 2. Point-launch comparison and site-relative repeat\n\n'
           'The zero-size equatorial apoapsis transfer is a regression comparison. '
           'The next section uses the actual off-equator tip position.'),
        code('pprint(results["point_reference"])'),
        md('## 3. Finite horizontal-sling node intercept\n\n'
           'Purely eastward release occurs at a tip north/south of the hub. '
           'The first equator crossing is 90 degrees along its inclined orbit. '
           'Setting semilatus rectum equal to catcher radius gives the derived node solution.'),
        code('for case in results["finite_tip_cases"]:\n'
             '    pprint({k: case[k] for k in ["tip_offset_m", "inclination_deg", "site_tip_speed_m_s", '
             '"flight_s", "catch_relative_m_s", "numerical_position_error_m"]})\n'
             'display(Image(filename=str(output_dir / "orbit_node.png")))'),
        md('## 4. Countermass trajectories\n\n'
           'Equal-radius and 1% shorter rock-side radii are separate geometric cases. '
           'The cycle example below remains equal-radius; do not combine these into an asserted feasible design. '
           'Spherical impact coordinates do not establish disposal safety.'),
        code('case = results["finite_tip_cases"][1]\n'
             'pprint(case["equal_radius_counter"])\npprint(case["shorter_radius_counter"])\n'
             'display(Image(filename=str(output_dir / "countermass_altitude.png")))'),
        md('## 5. Complete-cycle kinematic bound and phase closure\n\n'
           'Includes rest-to-rest outward and return travel, selected loading/settling allowances, '
           'and skipped site-relative passes. Fixed-speed rotation alone does not close the release phase.'),
        code('for case in results["cycles"]: pprint(case)\n'
             'print("Required phase correction [rad]", results["required_phase_integral_correction_rad"])\n'
             'print("Mean correction over slack time [rad/s]", results["ideal_phase_correction_mean_rad_s"])'),
        md('## 6. Instantaneous power with no recovery credit\n\n'
           'Straight-sling constant-spin moving-mass calculation only. Positive wheel/radial-drive work '
           'is charged through explicit efficiencies; braking energy is dissipated. '
           'Climber mass is unsized: primary comparison uses the zero-mass limit; nonzero masses are sensitivities. '
           'Outward radial braking is energy output, while the wheel drive supplies torque under the constant-spin assumption. '
           'See [radial energy clarification](../docs/radial_energy_review.md). '
           'Rolling loss, auxiliary demand, cable dynamics and phase-correction power are not included.'),
        code('pprint(results["climber_mass_sensitivity"])\n'
             'display(Image(filename=str(output_dir / "cycle_power_bound.png")))'),
        md('## 7. Sunlight availability and conditional throughput\n\n'
           '10-degree minimum solar elevation is an operating-window assumption, not panel sizing. '
           'No operation or electrical buffering through night is assumed.'),
        code('pprint(results["sun"])'),
        md('## 8. Generated tables and open feasibility requirements\n\n'
           'A sustainable 20 km equatorial catcher orbit needs gravity-harmonic and terrain checks. '
           'Tether droop, unloaded-cable behavior, stabilizer/structural loads, climber contact, '
           'phase-restoration control and installed panel mass remain unresolved. No optimization is performed.'),
        code('display(Markdown((output_dir / "orbit_cycle_tables.md").read_text()))'),
    ]
    path=Path(__file__).with_name('02_orbit_cycle_feasibility.ipynb')
    nbf.write(notebook,path)
    return path


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    path=build()
    if args.execute:
        from nbclient import NotebookClient
        notebook=nbf.read(path,as_version=4)
        NotebookClient(notebook,timeout=180,kernel_name='hub-study',
                       resources={'metadata':{'path':str(path.parent)}}).execute()
        nbf.write(notebook,path)
    print(path)
