# P1: eastward launches below the hilltop tangent plane

[Radial terrain profile](README.md) · [Publication packet](../publication/README.md)

**All five tested release heights clear the terrain outbound to 25 km apoapsis.** P1 retains its 5.716 km horizontal arm radius and intended southern release point.

The published 50-g go-kart reference has an apex height of **28.68 m**. Its loaded endpoint is 0.8768 m above the original central tangent plane; site selection added 0.5 m, giving the current **1.3768 m** endpoint offset. Subtracting the 28.68 m support height from that current endpoint puts release **27.30 m below the hub tangent plane**.

| Release case | Height relative to hub tangent plane (m) | Ground clearance at release (m) | Minimum outbound terrain clearance (m) | Eastward clears? |
|---|---:|---:|---:|:---:|
| Existing reference | +1.38 | 1514.7 | 647.9 | Yes |
| Subtract reference pole height | -27.30 | 1486.1 | 619.3 | Yes |
| 100 m below hub tangent plane | -100.00 | 1413.5 | 546.6 | Yes |
| 200 m below hub tangent plane | -200.00 | 1313.6 | 446.7 | Yes |
| 300 m below hub tangent plane | -300.00 | 1213.7 | 346.8 | Yes |

## Publication takeaway

At P1, a payload released 300 m below the hilltop tangent plane still clears the eastward terrain on its way to a 25 km apoapsis. The smallest modeled clearance along that outbound flight is **347 m**. The hill provides substantial room for a lower release height.

## Geometry and model

Offsets −100, −200 and −300 m are measured from the hub tangent plane. At horizontal arm radius a, the tip has axial coordinate Z = R + h_hub + offset and lunar-center radius sqrt(Z² + a²). Its latitude follows the corresponding angle atan(a/Z) southward from the hub. This preserves the arm radius while lowering the endpoint; latitude changes slightly as well. Local ground clearance and radial altitude include lunar curvature.

Each shot is horizontal and directly eastward at periapsis. Its speed is recalculated to retain the 25 km apoapsis. The calculation uses the established spherical-gravity model, lunar rotation, and terrain at the actual evolving latitude and longitude. The off-equator orbit reaches apoapsis at the opposite latitude; equatorial catcher targeting remains a separate calculation.

These cases test endpoint departure geometry. The separate sag/taper study will determine cable shapes, tension, supports and full-path hardware clearance at lowered endpoints. Translating the reference endpoint by the pole height is a geometric sensitivity case.

The existing minimum tip-ring terrain height is about 422.2 m below the hub tangent plane. A horizontal endpoint circle at −300 m therefore retains about **122.2 m** of minimum rim clearance. The intended southern release point lies above lower terrain, explaining its larger local release clearance in the table.

Every trajectory was sampled at 15 m and 7.5 m orbital-arc spacing, with local refinement of its minimum gap. Both resolutions agree on every classification and minimum clearances agree within 0.1 m. DEM resolution is approximately 59 m; the numerical agreement describes the interpolated terrain model.

- [Full results](lowered_release.json) · [CSV](lowered_release.csv).
- [Generator](lowered_release.py): `.env/hub/bin/python -m llo_catcher.site_selection.radial_terrain.lowered_release`.
- Reference support height: [published design dimensions](../../../sling_launcher/publication/DESIGN_AT_A_GLANCE.md).
