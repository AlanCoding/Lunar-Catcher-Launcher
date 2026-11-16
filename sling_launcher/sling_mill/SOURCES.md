# Material sources and provenance

Accessed 2026-11-15. The supplier values describe fibers; manufactured belts and joints need their own allowables.

- [DuPont Kevlar technical guide](https://www.dupont.com/content/dam/dupont/amer/us/en/safety/public/documents/en/Kevlar_Technical_Guide_0319.pdf): Kevlar 49 nominal yarn density 1,440 kg/m³, tensile strength 3.0 GPa and modulus 112.4 GPa. The search-indexed official guide supplied these values; direct PDF retrieval returned 404 in this session. [Toray–DuPont material-property table](https://www.td-net.co.jp/kevlar/data/) provides a second official property reference.
- [Toyobo Zylon technical information](https://cn.toyobo-global.com/seihin/kc/pbo/zylon-p/bussei-p/technical.pdf) and [Toyobo MC English data sheet](https://www.toyobo-mc.jp/wordpress/wp-content/uploads/2023/09/hp_fiber_data_zylon_en.pdf): nominal AS/HM strength 5.8 GPa, densities 1,540/1,560 kg/m³ and moduli 180/270 GPa. These nominal values enter the material library. Environmental protection, joints, wear and fatigue require product-specific qualification.
- [Teijin Zylon product page](https://www.teijin-frontier-usa.com/zylon/): reference supplied in the handoff; direct access returned 403, with properties available in indexed results.

The baseline allowable is nominal tensile strength × 0.8 joint efficiency × 0.8 environmental factor / 2 safety factor. These deratings are **study assumptions**, giving Zylon HM 1.856 GPa working stress. They do not establish lifetime under sliding contact, repeated bending, ultraviolet exposure or storage conditions. The calculation also retains the free-ring stress benchmark and a separately derived supported-panel screen.

Friction coefficient 0.5, contact patch 20 mm, payload properties, motor mass intensity, foundation mass, bearing allowance and radiator mass intensity are declared engineering inputs. No retrieved source establishes high-speed vacuum friction or wear performance for the proposed contact. No qualified motor, bearing, belt joint or payload material has been selected.

The author's [handoff](BRIEF.md) supplies the architecture and numerical validation example. Existing sling models establish comparison context; this mill's mass and power figures are calculated independently.
