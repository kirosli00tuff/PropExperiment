"""Check 2 (VerdictVerifier-FableXHigh, Stage E.18): compare recompute.json (written first) with
the lead's result reports/stage_e18_c1b_result.json: every float to 1e-9 absolute, counts and
strings exactly. Writes reports/stage_e18_verify/compare.json; prints a summary only."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
MINE = REPO / "reports" / "stage_e18_verify" / "recompute.json"
RESULT = REPO / "reports" / "stage_e18_c1b_result.json"
OUT = REPO / "reports" / "stage_e18_verify" / "compare.json"
TOL = 1e-9
TEST_IDS = ("C1b-T1", "C1b-T2")


def same(a, b) -> bool:  # noqa: ANN001
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if isinstance(a, int) and isinstance(b, int):
            return a == b
        return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= TOL
    return a == b


def main() -> int:
    mine = json.loads(MINE.read_bytes())
    res = json.loads(RESULT.read_bytes())
    rows = []

    def cmp(label: str, a, b) -> None:  # noqa: ANN001
        rows.append({"item": label, "mine": a, "result": b, "equal": same(a, b)})

    cmp("verdict", mine["verdict_with_trade_level_mean"], res.get("verdict"))
    cmp("passing_tests", mine["passing_tests_trade_level_mean"], res.get("passing_tests"))
    cmp("schema", "stage_e14_c1_result/1", res.get("schema"))
    cmp("test", "C1b", res.get("test"))
    cmp("test_ids", list(TEST_IDS), res.get("test_ids"))
    cmp("trades_sha256", mine["trades_sha256"], res.get("trades_sha256"))
    for tid in TEST_IDS:
        m, r = mine["tests"][tid], res["tests"][tid]
        cmp(f"{tid}.horizon", m["horizon"], r["horizon"])
        cmp(f"{tid}.n_trades", m["n_trades"], r["n_trades"])
        cmp(f"{tid}.n_dates", m["n_dates"], r["n_dates"])
        cmp(f"{tid}.n_rows", m["n_rows"], r["n_rows"])
        cmp(f"{tid}.mean_gross_ticks (trade-level)", m["mean_gross_ticks_trade_level"],
            r["mean_gross_ticks"])
        cmp(f"{tid}.cost_ticks", m["cost_ticks"], r["cost_ticks"])
        cmp(f"{tid}.bar_ticks", m["bar_ticks"], r["bar_ticks"])
        cmp(f"{tid}.t_B", m["t_B"], r["t_B"])
        cmp(f"{tid}.p_one_sided", m["p_one_sided"], r["p_one_sided"])
        cmp(f"{tid}.criteria.mean_ge_1_5c", m["criteria"]["mean_ge_1_5c_trade_level"],
            r["criteria"]["mean_ge_1_5c"])
        cmp(f"{tid}.criteria.p_le_0_025", m["criteria"]["p_le_0_025"], r["criteria"]["p_le_0_025"])
        cmp(f"{tid}.criteria.n_ge_30", m["criteria"]["n_ge_30"], r["criteria"]["n_ge_30"])
        cmp(f"{tid}.decision", m["decision_trade_level_mean"], r["decision"])
        md, rd = mine["descriptive"][tid], res["descriptive"][tid]
        for k in ("commission_rt_ticks", "mean_cost_ticks", "bar_ticks", "mean_ge_bar"):
            cmp(f"{tid}.c14.{k}", md["c14_slippage_1_5x"][k], rd["c14_slippage_1_5x"][k])
        cmp(f"{tid}.c15.share", md["c15"]["share_of_rows_at_or_above_q"],
            rd["c15"]["share_of_rows_at_or_above_q"])
        cmp(f"{tid}.c15.n_rows", md["c15"]["n_rows"], rd["c15"]["n_rows"])
        for sd in ("long", "short"):
            cmp(f"{tid}.c15.{sd}.n", md["c15"][sd]["n"], rd["c15"][sd]["n"])
            cmp(f"{tid}.c15.{sd}.mean", md["c15"][sd]["mean_gross_ticks"],
                rd["c15"][sd]["mean_gross_ticks"])
        cmp(f"{tid}.c15.trades_per_year", md["c15"]["trades_per_year"], rd["c15"]["trades_per_year"])
    # Guards: C10 counts per horizon and signal, exactly.
    g = res["guards"]["C10"]
    for h in ("h60", "hF"):
        cmp(f"C10.{h}.ng_ok_rows", mine["c10"]["counts"][h]["ng_ok_rows"], g[h]["ng_ok_rows"])
        diffs = {s: (n, g[h]["applicable"].get(s)) for s, n in mine["c10"]["counts"][h]["applicable"].items()
                 if n != g[h]["applicable"].get(s)}
        cmp(f"C10.{h}.applicable (64 signals, differing)", {}, diffs)
        cmp(f"C10.{h}.signal_set", sorted(mine["c10"]["counts"][h]["applicable"]),
            sorted(g[h]["applicable"]))
    cmp("guards.C11", "feature_cols equal E.12's", res["guards"].get("C11"))
    cmp("world.roots", mine["world"]["roots"], res["world"]["roots"])
    cmp("world.calendar_dates", mine["world"]["calendar_dates"], res["world"]["calendar_dates"])
    cmp("world.excluded_dates", mine["world"]["excluded_dates"], res["world"]["excluded_dates"])
    cmp("panel_counts", mine["panel_counts"], res["panel_counts"])
    cmp("c12.record", mine["c12"], res["inputs"]["c12"])
    unequal = [r for r in rows if not r["equal"]]
    out = {"schema": "stage_e18_verify/compare/1", "tolerance_abs": TOL, "n_items": len(rows),
           "n_unequal": len(unequal), "unequal": unequal, "rows": rows,
           "result_started_local": res.get("started_local"),
           "result_finished_local": res.get("finished_local"),
           "mine_started_local": mine["started_local"], "mine_finished_local": mine["finished_local"]}
    OUT.write_text(json.dumps(out, indent=1, allow_nan=False) + "\n")
    print(f"items {len(rows)}, unequal {len(unequal)}")
    for r in unequal:
        print(f"  UNEQUAL {r['item']}: mine {r['mine']!r} result {r['result']!r}")
    print(f"result verdict {res.get('verdict')} started {res.get('started_local')} finished "
          f"{res.get('finished_local')}; written {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
