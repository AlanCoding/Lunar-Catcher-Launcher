# Supplemental numerical validation

The sweep's nine outbound-clear trajectories were independently rerun through
first contact at 0.125 m path sampling, finer than the saved 0.25 m results.
All classifications agree. The largest impact-time difference is
**6.09e-11 seconds**.

See [per-case refinement checks](survivor_refinement.json). This checks numerical
search stability within the interpolated DEM, not physical terrain accuracy.
Ten unit/regression checks passed, including an independent Cartesian integrator,
node/capture geometry, analytic altitude-skip bounds, synthetic return impact,
conditional statistical denominators and agreement with the preserved demo.
The six original demo report/data/figure files retain their recorded SHA-256
hashes. See [full results and provenance](results.json).
