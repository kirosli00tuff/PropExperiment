"""Stage E.10 Task 1(a): the K9 cost wall per traded exposure, from frozen tables only.

Inputs (frozen, read-only): reports/stage_e2a_costs.json (D8 slippage per 30-minute bucket,
commission), reports/stage_e2a_epsilon.json (q_c, operative eps, E|m_1| for context).
Design rules (fixed in reports/stage_e10_design_target.md before any source is read):
  RT_X  = commission_rt_ticks + 2 x max over the product's buckets of side_ticks   (worst bucket pair)
  M_X   = 3 x RT_X                                       (minimum gross move per trade)
  G_X(f)= eps_X / f + RT_X                               (gross per trade to net eps_X per trade date)
No market data, no Stage E screen figure is read.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COSTS = ROOT / "reports/stage_e2a_costs.json"
EPS = ROOT / "reports/stage_e2a_epsilon.json"
OUT = ROOT / "reports/stage_e10_research/cost_wall.json"
FREQS = (0.40, 0.20, 0.10)  # entries per research date: the cap (2/week), 1/week, the 30-trip floor


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    costs = json.loads(COSTS.read_text())["products"]
    eps_rows = json.loads(EPS.read_text())["exposures"]
    rows = []
    for e in eps_rows:
        v = e["vehicle"]
        c = costs[v]
        sides = [max(b["side_ticks"]["buy"], b["side_ticks"]["sell"]) if isinstance(b["side_ticks"], dict)
                 else b["side_ticks"] for b in c["buckets"]]
        max_side = max(sides)
        rt = c["commission_rt_ticks"] + 2 * max_side
        hd = c["headline_day_session"]["round_turn_ticks"]["mean"]
        em1 = e["e_abs_move_ticks"]["1"] if isinstance(e["e_abs_move_ticks"], dict) else None
        eps = e["eps_operative"]
        row = {
            "cluster": e["cluster"], "exposure": e["exposure"], "vehicle": v, "q_c": e["q_c"],
            "tick_value_usd": c["tick_value_usd"], "status": e["status"],
            "eps_operative": eps, "eps_translated": e["eps_translated"],
            "commission_rt_ticks": round(c["commission_rt_ticks"], 3),
            "max_side_ticks": round(max_side, 3),
            "rt_wall_ticks": round(rt, 3),
            "event_window_rt_ticks": round(c["event_window_round_turn_ticks"], 3),
            "day_session_rt_mean_ticks": round(hd, 3),
            "M_X_ticks": round(3 * rt, 2),
            "M_X_usd_at_q": round(3 * rt * c["tick_value_usd"] * e["q_c"], 2),
            "G_ticks": {f"{f:.2f}": round(eps / f + rt, 1) for f in FREQS},
            "G_usd_at_q": {f"{f:.2f}": round((eps / f + rt) * c["tick_value_usd"] * e["q_c"], 0) for f in FREQS},
            "E_abs_m1_ticks_context": round(em1, 2) if em1 else None,
            "G_over_Em1_context": {f"{f:.2f}": round((eps / f + rt) / em1, 2) for f in FREQS} if em1 else None,
        }
        rows.append(row)
    out = {"stage": "E.10", "task": "1(a)", "rules": __doc__,
           "inputs_sha256": {str(COSTS.relative_to(ROOT)): sha(COSTS), str(EPS.relative_to(ROOT)): sha(EPS)},
           "freqs": FREQS, "rows": rows}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"rows {len(rows)} written {OUT.relative_to(ROOT)}")
    print("| Cl | Exposure | Veh | q_c | eps | comm | max side | RT_X | evt RT | day RT | M_X | G(0.4) | G(0.2) | G(0.1) | $G(0.4) | G0.4/E|m1| | G0.2/E|m1| |")
    for r in rows:
        g, gu, gr = r["G_ticks"], r["G_usd_at_q"], r["G_over_Em1_context"] or {}
        print(f"| {r['cluster']} | {r['exposure']} | {r['vehicle']} | {r['q_c']} | {r['eps_operative']} | "
              f"{r['commission_rt_ticks']:.2f} | {r['max_side_ticks']:.2f} | {r['rt_wall_ticks']:.2f} | "
              f"{r['event_window_rt_ticks']:.2f} | {r['day_session_rt_mean_ticks']:.2f} | {r['M_X_ticks']:.1f} | "
              f"{g['0.40']} | {g['0.20']} | {g['0.10']} | {gu['0.40']:.0f} | {gr.get('0.40')} | {gr.get('0.20')} |")


if __name__ == "__main__":
    main()
