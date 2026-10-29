"""Run frozen retreat trade study for a scenario and print concise summary."""

from __future__ import annotations

from src.scenario import Scenario, run_trade_study


def main() -> None:
    scenario = Scenario()
    out = run_trade_study(scenario)

    print("Trade study summary (baseline):")
    print(f"catch_relative_velocity_m_s: {out['section_3']['v_rel_catch_m_s']:.3f}")
    print(f"impact_velocity_km_s: {out['section_4']['v_impact_m_s']/1000.0:.6f}")
    print(f"dv_30_to_120_m_s: {out['section_5']['dv_30_to_120_m_s']:.3f}")
    print(f"rock_delivered_per_cycle_t: {out['section_8']['delivered_rocks_t']:.3f}")
    print(f"up_leg_prop_t: {out['section_8']['up_leg_prop_t']:.3f}")
    print(f"down_leg_prop_t: {out['section_8']['down_leg_prop_t']:.3f}")
    print(f"bridge_time_days: {out['section_9']['bridge_time_days']:.2f}")


if __name__ == "__main__":
    main()
