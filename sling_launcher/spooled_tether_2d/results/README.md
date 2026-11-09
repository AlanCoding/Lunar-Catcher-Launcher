# 2D spool results: shapes first

[Model, assumptions and findings](../README.md). All images have a matching SVG
with the same basename. The frame rotates with the feed station, and colors show
axial stress. Late retraction is exploratory, not a certified clearance envelope.

- **Faster-start controls:** [time-domain comparison](payout_control_comparison.png),
  [values](payout_control_comparison.json), and [interpretation/retraction sequences](../CONTROL_COMPARISON.md).
  The two new commands retain distributed cable and payload inertia.
- **3:1 Kevlar taper:** [extension snapshots](kevlar_ratio3_n32_extension.png) and
  [empty retraction snapshots](kevlar_ratio3_n32_retraction.png). This 3-tonne
  cable carries a 1-tonne payload and retains a 10 kg end device after release;
  abrupt-release stress approaches nominal fiber strength.
- **Thicker Kevlar taper:** [extension snapshots](kevlar_1p5GPa_n64_extension.png) and
  [empty retraction snapshots](kevlar_1p5GPa_n64_retraction.png). Static sizing at
  1.5 GPa requires 7.31 tonnes of cable. Its late return stops at a
  damping-sensitive retension event, so the last frames need refinement.
- **Stress and angular histories:** [comparison](stress_and_angles.png),
  [3:1 angular occupancy](kevlar_ratio3_n32_angles.png), and
  [thicker-taper angular occupancy](kevlar_1p5GPa_n64_angles.png). Filled bands show
  instantaneous cable angle ranges outside 500 m radius; tip angle is a line.
- **Saved simulation states:** [3:1, 32 cells](kevlar_ratio3_n32.npz),
  [thicker, 64 cells](kevlar_1p5GPa_n64.npz), and
  [thicker, 32-cell comparison](kevlar_1p5GPa_n32.npz). NumPy fields include
  `time_s`, `phase`, `xy_m`, `stress_Pa`, `strain`, `material_velocity_m_s`,
  `q_m`, `angle_min_deg`, `angle_max_deg`, and `tip_angle_deg`.
- **Inputs and phase extrema:** [3:1 JSON](kevlar_ratio3_n32.json),
  [thicker 64-cell JSON](kevlar_1p5GPa_n64.json), and
  [thicker 32-cell JSON](kevlar_1p5GPa_n32.json). Stress maxima at accepted
  integration steps are retained separately from the plotted samples.
- **Checks:** [validation](validation.json) and [source/environment manifest](manifest.json).
  Extension agrees closely across meshes/integrators; late retraction does not.
