"""Rebuild H1-H4's unit series per cost case from the units files alone, re-deriving each row's
net_ru from (gross - cost) / 100 / sigma and each row's sigma from the trailing-20 g (lead_spec
section 3, coder choice 8). Writes series_<test>.json and series_checks.json. No price is printed."""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from fractions import Fraction

import numpy as np

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
from vv_common import CASES, OUT, iter_units, money, write_json  # noqa: E402

TRAIL = 20
REL_TOL = 1e-9


def net_ru_from_row(row: dict, case: str) -> float:
    gross = money(row["gross_cents"])
    cost = money(row["costs_cents"][case])
    return float((gross - cost) / 100) / float(row["sigma"])


def trailing_sigma(prior_g: list[tuple[str, str, int, float]], entry_date: str) -> tuple[float | None, int]:
    """Sample std (ddof 1) of the last TRAIL g values of units whose exit date < entry_date,
    ordered by exit date (then entry date, then row order)."""
    eligible = [g for g in prior_g if g[0] < entry_date]
    eligible.sort()
    window = [g[3] for g in eligible[-TRAIL:]]
    if len(window) < 2:
        return None, len(window)
    return float(np.std(np.asarray(window), ddof=1)), len(window)


def rebuild(test: str) -> dict:
    per_date: dict[str, dict[str, list[float]]] = {c: defaultdict(list) for c in CASES}
    legs_per_date: Counter = Counter()
    flags = Counter()
    mism = Counter()
    sigma_dev = []
    g_by_key: dict[str, list[tuple[str, str, int, float]]] = defaultdict(list)
    rows_by_key_order: Counter = Counter()
    n_rows = 0
    per_product = Counter()
    for row in iter_units(test, traded_only=False):
        key = row["key"]
        g_value = float(money(row["gross_cents"]) / 100)
        order = rows_by_key_order[key]
        rows_by_key_order[key] += 1
        if row["status"] == "traded":
            n_rows += 1
            per_product[key] += 1
            sig_mine, n_win = trailing_sigma(g_by_key[key], row["entry_date"])
            if sig_mine is None:
                mism["sigma_undefined_mine"] += 1
            else:
                rel = abs(sig_mine - row["sigma"]) / max(abs(row["sigma"]), 1e-12)
                sigma_dev.append(rel)
                if rel > 1e-9:
                    mism["sigma_mismatch"] += 1
                if n_win != TRAIL:
                    mism[f"sigma_window_{n_win}"] += 1
            for case in CASES:
                mine = net_ru_from_row(row, case)
                theirs = row["net_ru"][case]
                if abs(mine - theirs) > REL_TOL * max(1.0, abs(theirs)):
                    mism[f"net_ru_mismatch_{case}"] += 1
                per_date[case][row["date"]].append(theirs)
            legs_per_date[row["date"]] += 1
            for fill in row["fills"]:
                flags[f"fill_{fill[1]}"] += 1
                flags["fill_event"] += int(fill[4])
                flags["fill_at_close"] += int(fill[5])
                flags["fill_uncalibrated"] += int(fill[6])
            for name in ("after_1508", "exit_at_close", "entry_no_new", "ref_exit_at_close",
                         "entry_after_closure"):
                if row.get(name):
                    flags[name] += 1
            if isinstance(row["gross_cents"], str):
                flags["gross_fraction_str"] += 1
        else:
            flags[f"status_{row['status']}"] += 1
        # g holds every unit that passed every exclusion with a non-zero signal (warm-up included)
        g_by_key[key].append((row["exit_date"], row["entry_date"], order, g_value))
    series = {}
    for case in CASES:
        dates = sorted(per_date[case])
        if test in ("H1", "H4"):
            values = [float(np.mean(per_date[case][d])) for d in dates]
        elif test == "H2":  # the pair: the sum of the two legs' risk-unit P&Ls
            values = [float(np.sum(per_date[case][d])) for d in dates]
            bad = [d for d in dates if legs_per_date[d] != 2]
            if bad:
                mism["h2_dates_without_two_legs"] = len(bad)
        else:  # H3: the unit is the AUCTION (dated t); two tenors may share a date (kept apart)
            pairs = [(d, v) for d in dates for v in per_date[case][d]]
            dates = [d for d, _ in pairs]
            values = [float(v) for _, v in pairs]
            multi = [d for d in set(dates) if legs_per_date[d] > 1]
            if multi:
                mism["h3_dates_with_several_units"] = len(multi)
        series[case] = {"dates": dates, "values": values}
    checks = {"traded_rows": n_rows, "units_dates": len(series["base"]["dates"]),
              "per_product_traded": dict(sorted(per_product.items())),
              "flags": dict(sorted(flags.items())), "mismatches": dict(sorted(mism.items())),
              "sigma_rel_dev_max": max(sigma_dev) if sigma_dev else None,
              "sigma_checked": len(sigma_dev),
              "legs_per_date_hist": dict(sorted(Counter(legs_per_date.values()).items()))}
    return {"series": series, "checks": checks}


def main() -> None:
    all_checks = {}
    for test in ("H1", "H2", "H3", "H4"):
        out = rebuild(test)
        write_json(OUT / f"series_{test}.json", out["series"])
        all_checks[test] = out["checks"]
        c = out["checks"]
        print(test, "traded rows", c["traded_rows"], "unit dates", c["units_dates"],
              "mismatches", c["mismatches"], "sigma max rel dev", c["sigma_rel_dev_max"])
    write_json(OUT / "series_checks.json", all_checks)


if __name__ == "__main__":
    main()
