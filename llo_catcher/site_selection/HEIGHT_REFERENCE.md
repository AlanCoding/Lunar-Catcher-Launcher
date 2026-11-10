# Terrain and release-height reference

[Site-selection guide](README.md).

The current go-kart endpoint plane is **1.3768157 m above the hub tangent plane**: 0.8768157 m from the saved loaded-tether geometry plus the chosen 0.5 m margin. Local ground clearance depends on hub elevation, surrounding terrain and lunar curvature.

For hub terrain elevation h₀, endpoint axial coordinate Z = R + h₀ + plane offset, and horizontal arm radius a:

```
release radius = sqrt(Z² + a²)
local release clearance = release radius − R − terrain height at release
```

For terrain height h at central angle θ from the hub:

```
projected terrain height = (R + h) cos θ − (R + h₀)
```

A positive tip-circle clearance means the endpoint plane stays above the terrain around the sampled circumference. The [radial terrain envelope](radial_terrain/README.md) extends that check across radii and supplies the boundary for the separate [sag/taper design study](../../sling_launcher/sag_taper_trade/README.md).

Earlier point-release examples use 10 m above local ground and remain in [equatorial_context](equatorial_context/README.md). The current hilltop and ridge studies use the hub-relative convention. Saved `height_audit.json` and `height_validation.json` retain the regression evidence used when the global search was checked against earlier candidate coordinates.
