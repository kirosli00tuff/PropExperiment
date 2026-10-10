"""Rebuild H5 per cost case as lead_spec section 4 (H5) defines it.

Components: x_H1, x_H4 = the daily pooled net series rebuilt by recompute_series.py (0 on grid
dates with no trade); x_H2, x_H3 = the daily mark-to-settlement series in risk units. The daily
marks are not in the units files (only fills are), so x_H2 and x_H3 are taken from the H2/H3
result files' `component` series AFTER a telescoping check against the units: the sum of a
unit's daily values over its open dates must equal its net_ru (entry fill, marks and exit fill
telescope), per unit for H2 (no overlap) and in total for H3 (tenors overlap in time).
Grid: the union of the H1 and H4 results' grid_dates (eligible dates, whatever the signal; not
reconstructible from the units files) and the open dates of traded H2/H3 units.
sigma_i,d = sample std (ddof 1) of x_i over the 60 grid dates strictly before d; H5_d = mean over
components with a defined, positive sigma of x_i,d / sigma_i,d; the first 60 grid dates warm up.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from vv_common import CASES, OUT, RUNS, iter_units, write_json  # noqa: E402

WARMUP = 60


def load_result_fields(test: str, fields: tuple[str, ...]) -> dict:
    with open(RUNS / f"{test}_result.json", encoding="utf-8") as handle:
        raw = json.load(handle)
    return {f: raw[f] for f in fields}


def telescoping_check(test: str, component: dict[str, dict[str, float]]) -> dict:
    """Sum of the daily component values equals the sum of the units' net_ru (per case); for H2
    also per unit over its open dates (both legs share the open dates)."""
    out = {}
    units = list(iter_units(test))
    open_dates_all = set()
    for row in units:
        open_dates_all.update(row["open_dates"])
    for case in CASES:
        total_units = sum(row["net_ru"][case] for row in units)
        total_series = sum(component[case].values())
        rec = {"units_total": total_units, "series_total": total_series,
               "abs_diff": abs(total_units - total_series),
               "series_dates": len(component[case]),
               "series_dates_not_open": sum(1 for d in component[case] if d not in open_dates_all),
               "open_dates_not_in_series": sum(1 for d in open_dates_all if d not in component[case])}
        if test == "H2":
            by_date: dict[str, list[dict]] = defaultdict(list)
            for row in units:
                by_date[row["date"]].append(row)
            worst = 0.0
            for d, legs in by_date.items():
                unit_total = sum(r["net_ru"][case] for r in legs)
                series_sum = sum(component[case].get(x, 0.0) for x in legs[0]["open_dates"])
                worst = max(worst, abs(unit_total - series_sum))
            rec["per_unit_worst_abs_diff"] = worst
        out[case] = rec
    return out


def h5_series(grid: list[str], comps: dict[str, dict[str, np.ndarray]], case: str) -> dict:
    n = len(grid)
    names = ["H1", "H2", "H3", "H4"]
    x = {k: comps[k][case] for k in names}
    values, dates, used, scaled_max = [], [], [], {k: 0.0 for k in names}
    per_comp_scaled = {k: [] for k in names}
    for i in range(WARMUP, n):
        terms = []
        for k in names:
            window = x[k][i - WARMUP:i]
            sigma = float(np.std(window, ddof=1))
            if sigma > 0:
                z = float(x[k][i] / sigma)
                terms.append(z)
                per_comp_scaled[k].append((grid[i], z))
                scaled_max[k] = max(scaled_max[k], abs(z))
        values.append(float(np.mean(terms)) if terms else 0.0)
        used.append(len(terms))
        dates.append(grid[i])
    return {"dates": dates, "values": values, "components_used_hist":
            dict(sorted(__import__("collections").Counter(used).items())),
            "max_abs_scaled_component": scaled_max,
            "top_abs_dates": sorted(zip(map(abs, values), dates), reverse=True)[:12],
            "per_component_scaled": per_comp_scaled}


def main() -> None:
    h1 = load_result_fields("H1", ("grid_dates",))
    h4 = load_result_fields("H4", ("grid_dates",))
    h2 = load_result_fields("H2", ("component", "grid_dates"))
    h3 = load_result_fields("H3", ("component", "grid_dates"))
    tele = {"H2": telescoping_check("H2", h2["component"]),
            "H3": telescoping_check("H3", h3["component"])}
    grid = set(h1["grid_dates"]) | set(h4["grid_dates"])
    for test in ("H2", "H3"):
        for row in iter_units(test):
            grid.update(row["open_dates"])
    grid = sorted(grid)
    comps: dict[str, dict[str, np.ndarray]] = {}
    for test in ("H1", "H4"):
        with open(OUT / f"series_{test}.json", encoding="utf-8") as handle:
            mine = json.load(handle)
        comps[test] = {}
        for case in CASES:
            lookup = dict(zip(mine[case]["dates"], mine[case]["values"]))
            comps[test][case] = np.asarray([lookup.get(d, 0.0) for d in grid])
    for test, res in (("H2", h2), ("H3", h3)):
        comps[test] = {case: np.asarray([res["component"][case].get(d, 0.0) for d in grid])
                       for case in CASES}
    out = {}
    for case in CASES:
        out[case] = h5_series(grid, comps, case)
        print(case, "n", len(out[case]["values"]), "components used hist",
              out[case]["components_used_hist"], "max |scaled comp|",
              {k: round(v, 2) for k, v in out[case]["max_abs_scaled_component"].items()})
    write_json(OUT / "series_H5.json", {c: {"dates": out[c]["dates"], "values": out[c]["values"]}
                                        for c in CASES})
    write_json(OUT / "h5_build.json", {
        "grid_dates": len(grid), "grid_first": grid[0], "grid_last": grid[-1],
        "grid_from": {"H1_grid": len(h1["grid_dates"]), "H4_grid": len(h4["grid_dates"]),
                      "H2_grid_in_result": len(h2["grid_dates"]),
                      "H3_grid_in_result": len(h3["grid_dates"])},
        "telescoping": tele,
        "per_case": {c: {k: v for k, v in out[c].items() if k not in ("dates", "values",
                                                                        "per_component_scaled")}
                     for c in CASES},
        "per_component_scaled": {c: out[c]["per_component_scaled"] for c in CASES}})
    print("telescoping:", json.dumps(tele))
    print("grid", len(grid), grid[0], grid[-1])


if __name__ == "__main__":
    main()
