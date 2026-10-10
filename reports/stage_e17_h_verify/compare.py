"""Compare my recomputation (recompute.json, series_*.json) with the result files' statistics
and series and with verdict.json. This is the only script that reads a result's `stats` or
verdict.json; it runs after every number of mine is on disk. Writes comparison.json."""
from __future__ import annotations

import json
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from vv_common import CASES, OUT, RUNS, TESTS, iter_units, write_json  # noqa: E402

KEYMAP = {"n": "n", "mean": "mean", "sd": "sd", "t": "t", "t_stat": "t", "t_nw": "t_nw",
          "nw_t": "t_nw", "t_newey_west": "t_nw", "p_t": "p_t", "p_plain": "p_t", "p_nw": "p_nw",
          "p": "p", "p_max": "p", "nw_lag": "lag", "lag": "lag", "nw_lags": "lag"}


def rel_diff(a, b) -> float:
    if a is None or b is None:
        return float("nan")
    a, b = float(a), float(b)
    return abs(a - b) / max(1.0, abs(a), abs(b))


def compare_stats(test: str, theirs: dict, mine: dict) -> dict:
    out = {"their_keys": sorted(theirs), "fields": {}, "unmapped": []}
    for key, value in theirs.items():
        mapped = KEYMAP.get(key)
        if mapped is None:
            if isinstance(value, dict) and ("pass" in value or "years" in value):
                ys = mine["year_stability"]
                out["fields"]["year_stability"] = {"theirs": {k: v for k, v in value.items() if k != "years"},
                                                   "mine": {k: v for k, v in ys.items() if k != "years"}}
            else:
                out["unmapped"].append(key)
            continue
        out["fields"][mapped] = {"theirs": value, "mine": mine.get(mapped),
                                 "rel_diff": rel_diff(value, mine.get(mapped))}
    return out


def compare_series(test: str, theirs: list, mine: dict) -> dict:
    t_dates = [d for d, _ in theirs]
    t_vals = np.asarray([v for _, v in theirs], dtype=float)
    m_vals = np.asarray(mine["values"], dtype=float)
    rec = {"n_theirs": len(theirs), "n_mine": len(m_vals), "dates_equal": t_dates == mine["dates"]}
    if len(t_vals) == len(m_vals):
        rec["max_abs_diff"] = float(np.max(np.abs(t_vals - m_vals)))
        rec["values_over_1e-9"] = int(np.sum(np.abs(t_vals - m_vals) > 1e-9))
    return rec


def exclusions_vs_units(test: str, exclusions: dict) -> dict:
    counts = Counter(row["status"] for row in iter_units(test, traded_only=False))
    return {"result_exclusions": exclusions, "units_status_counts": dict(counts),
            "traded_match": exclusions.get("traded") == counts.get("traded"),
            "warmup_match": exclusions.get("warmup", exclusions.get("leg warmup")) == counts.get("warmup")}


def main() -> None:
    with open(OUT / "recompute.json", encoding="utf-8") as handle:
        mine = json.load(handle)
    out = {"per_test": {}, "verdict": {}}
    for test in TESTS:
        with open(RUNS / f"{test}_result.json", encoding="utf-8") as handle:
            res = json.load(handle)
        with open(OUT / f"series_{test}.json", encoding="utf-8") as handle:
            my_series = json.load(handle)
        rec = {"stats": {}, "series": {}}
        for case in CASES:
            rec["stats"][case] = compare_stats(test, res["stats"][case], mine["stats"][test][case])
            rec["series"][case] = compare_series(test, res["series"][case], my_series[case])
        if test != "H5":
            rec["exclusions"] = exclusions_vs_units(test, res["exclusions"])
        else:
            rec["exclusions"] = {"result_exclusions": res["exclusions"], "grid_dates": len(res["grid_dates"])}
            with open(OUT / "h5_build.json", encoding="utf-8") as handle:
                rec["my_grid_dates"] = json.load(handle)["grid_dates"]
        rec["descriptive_note_keys"] = sorted((res.get("notes") or {}).get("descriptive", {}).keys())
        out["per_test"][test] = rec
        worst = max(f["rel_diff"] for c in CASES for f in rec["stats"][c]["fields"].values()
                    if "rel_diff" in f and f["rel_diff"] == f["rel_diff"])
        print(test, "series max|diff|:", {c: rec["series"][c].get("max_abs_diff") for c in CASES},
              "stats worst rel diff:", f"{worst:.3g}", "unmapped keys:", rec["stats"]["base"]["unmapped"])
    # ------------------------------------------------------------- verdict.json (read last)
    with open(RUNS / "verdict.json", encoding="utf-8") as handle:
        verdict = json.load(handle)
    out["verdict"]["raw_top_keys"] = sorted(verdict)
    out["verdict"]["raw"] = verdict
    out["verdict"]["mine"] = {"holm": mine["holm_base"], "pass_bar": mine["pass_bar"],
                              "dsr_base": {t: mine["dsr_at_N"]["base"]["dsr"][t]["dsr"] for t in TESTS},
                              "sharpe_variance_base": mine["dsr_at_N"]["base"]["sharpe_variance"],
                              "n_trials": mine["n_trials_from_registry"]}
    write_json(OUT / "comparison.json", out)
    print("verdict.json top keys:", sorted(verdict))
    print(json.dumps({k: v for k, v in verdict.items() if k not in ("tests", "per_test", "results")}, indent=None)[:1500])
    for key in ("tests", "per_test", "results"):
        if key in verdict:
            print(f"--- verdict[{key}]:")
            print(json.dumps(verdict[key], indent=None)[:3000])


if __name__ == "__main__":
    main()
