"""PilotVerifier step 1: own K1/K2/K3 from placements.parquet / loop.parquet / days.parquet only.

Independent of the producer's stats31*.py. Reads no stats31.json / stats31.md.
Run: uv run python -I reports/stage_e31_briefs/work/verify_pilot/step1_numbers.py
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

os.nice(10)

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
RUNS = ROOT / "reports/stage_e31_briefs/work/pilot/runs"
MEAS = RUNS / "measure31"
OUT = ROOT / "reports/stage_e31_briefs/work/verify_pilot"

FEE_TOPSTEP_FILL = 0.264  # ticks per fill
FEE_RT = 0.528
NREP = 2000
PCOLS = ["trade_date", "session", "symbol", "model", "side", "filled", "stale", "touched",
         "trigger", "wait_s", "c_half", "mo_10", "mo_nd_10", "t_fill_ns", "j_ns", "g_ns", "price"]


def load():
    expected = [ln.strip() for ln in (RUNS / "expected31.txt").read_text().split() if ln.strip()]
    missing_done = [d for d in expected if not (MEAS / d / "DONE").exists()]
    dirs = sorted(p.name for p in MEAS.iterdir() if p.is_dir())
    extra = sorted(set(dirs) - set(expected))
    pl, lp, dy = [], [], []
    for d in expected:
        b = MEAS / d
        p = pq.read_table(b / "placements.parquet", columns=PCOLS).to_pandas()
        pl.append(p[(p.symbol == "ZM.v.0") & (p.session == "DAY") & (p.model == "c")])
        lp.append(pd.read_parquet(b / "loop.parquet"))
        dy.append(pd.read_parquet(b / "days.parquet"))
    return (expected, missing_done, extra, pd.concat(pl, ignore_index=True),
            pd.concat(lp, ignore_index=True), pd.concat(dy, ignore_index=True))


def boot_ratio(num, den, rng, nrep=NREP):
    """num, den: per-date sums (length N). Ratio of sums inside each replicate."""
    n = len(num)
    idx = rng.integers(0, n, size=(nrep, n))
    s_n = num[idx].sum(axis=1)
    s_d = den[idx].sum(axis=1)
    ok = s_d > 0
    r = s_n[ok] / s_d[ok]
    return r, int((~ok).sum())


def pct(r):
    return float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))


def main():
    expected, missing_done, extra, P, L, D = load()
    res = {"n_expected": len(expected), "missing_done": missing_done, "extra_dirs": extra}
    res["placements_rows_primary"] = int(len(P))
    # population dates
    Dz = D[D.symbol == "ZM.v.0"].copy()
    inc = Dz[Dz.included]
    res["days_rows_zm0"] = int(len(Dz))
    res["days_zm0_included"] = int(len(inc))
    res["days_zm0_excluded_reasons"] = Dz[~Dz.included].reason.value_counts().to_dict()
    pdates = set(P.trade_date.unique())
    res["dates_with_primary_placements"] = len(pdates)
    res["primary_dates_not_included_in_days"] = sorted(map(str, pdates - set(inc.trade_date)))[:10]
    res["included_dates_without_primary_placements"] = sorted(map(str, set(inc.trade_date) - pdates))[:10]
    # sanity on columns
    res["placements_per_date_counts"] = P.groupby("trade_date").size().value_counts().to_dict()
    res["sides"] = P.side.value_counts().to_dict()
    res["filled_dtype_counts"] = P.filled.value_counts().to_dict()
    res["trigger_counts_filled"] = P[P.filled].trigger.value_counts().to_dict()
    res["touched_vs_filled"] = pd.crosstab(P.touched, P.filled).to_dict()
    # --- K2
    F = P[P.filled].copy()
    res["K2_fills"] = int(len(F))
    res["K2_rule_min"] = 400
    res["K2_fail"] = bool(len(F) < 400)
    res["placements_total"] = int(len(P))
    res["fill_rate"] = float(len(F) / len(P))
    # sanity: any filled with NaN t_fill / wait > 60.05
    res["filled_nan_tfill"] = int(F.t_fill_ns.isna().sum()) if F.t_fill_ns.dtype != "int64" else int((F.t_fill_ns <= 0).sum())
    res["filled_wait_gt_60.05"] = int((F.wait_s > 60.05 + 1e-9).sum())
    res["filled_wait_max"] = float(F.wait_s.max())
    res["filled_wait_lt0"] = int((F.wait_s < 0).sum())
    res["unfilled_with_wait"] = int((P[~P.filled].wait_s.notna()).sum())
    res["trigger_through_on_filled_only_through"] = bool((F.trigger == "through").all())
    # --- K1
    dates = np.array(sorted(inc.trade_date.unique()))
    seeds = [31, 7, 101, 20260]
    out = {}
    for var, col in [("drop", "mo_10"), ("nodrop", "mo_nd_10")]:
        E = F[col] + F.c_half
        valid = E.notna()
        N = E - FEE_TOPSTEP_FILL
        Fv = F.assign(N=N, E=E)[valid]
        gb = Fv.groupby("trade_date").N.agg(["sum", "count"])
        # population A: all included DAY dates (zero-fill dates keep a draw slot)
        numA = gb["sum"].reindex(dates, fill_value=0.0).to_numpy()
        denA = gb["count"].reindex(dates, fill_value=0).to_numpy().astype(float)
        # population B: only dates having >= 1 valid fill
        numB, denB = gb["sum"].to_numpy(), gb["count"].to_numpy().astype(float)
        mean_net = float(Fv.N.sum() / len(Fv))
        v = {"n_valid": int(len(Fv)), "n_filled": int(len(F)), "n_dropped": int(len(F) - len(Fv)),
             "mean_E10": float(Fv.E.mean()), "mean_N10_topstep": mean_net,
             "mean_N10_at_0.528": float(Fv.E.mean() - FEE_RT), "dates_popA": int(len(dates)),
             "dates_popB": int(len(gb)), "dates_without_valid_fill": int(len(dates) - len(gb))}
        for pop, (nu, de) in {"A": (numA, denA), "B": (numB, denB)}.items():
            for s in seeds:
                r, bad = boot_ratio(nu, de, np.random.default_rng(s))
                lo, hi = pct(r)
                v[f"pop{pop}_seed{s}"] = {"lo": lo, "hi": hi, "n_rep_nonempty": int(len(r))}
        # same but fee 0.528
        nu528 = numA - 0.264 * denA  # extra fee 0.264 per fill on top of 0.264
        for s in [31]:
            r, _ = boot_ratio(nu528, denA, np.random.default_rng(s))
            lo, hi = pct(r)
            v[f"popA_fee0.528_seed{s}"] = {"lo": lo, "hi": hi}
        out[var] = v
    res["K1"] = out
    # --- K3
    Lz = L[(L.symbol == "ZM.v.0") & (L.model == "c")]
    res["loop_rows_c_zm0"] = int(len(Lz))
    res["loop_dates_unique"] = int(Lz.trade_date.nunique())
    Lz_inc = Lz[Lz.trade_date.isin(set(inc.trade_date))]
    res["loop_rows_c_zm0_included"] = int(len(Lz_inc))
    res["loop_rows_outside_included"] = int(len(Lz) - len(Lz_inc))
    rt = Lz_inc.set_index("trade_date").round_trips.reindex(dates)
    res["loop_missing_for_included_dates"] = int(rt.isna().sum())
    rtv = rt.fillna(0).to_numpy().astype(float)
    res["K3_mean_rt_per_date"] = float(rtv.mean())
    res["K3_mean_all_loop_rows_c"] = float(Lz.round_trips.mean())
    res["K3_min_max_median"] = [float(rtv.min()), float(np.median(rtv)), float(rtv.max())]
    res["K3_rule_min"] = 20
    res["K3_fail"] = bool(rtv.mean() < 20)
    res["K3_boot"] = {}
    for s in seeds:
        rng = np.random.default_rng(s)
        idx = rng.integers(0, len(rtv), size=(NREP, len(rtv)))
        m = rtv[idx].mean(axis=1)
        res["K3_boot"][f"seed{s}"] = pct(m)
    res["K3_dates_below_20"] = int((rtv < 20).sum())
    # monthly / yearly split for context
    P["year"] = pd.to_datetime(P.trade_date).dt.year
    res["fills_by_year"] = F.assign(year=pd.to_datetime(F.trade_date).dt.year).groupby("year").size().to_dict()
    (OUT / "my_numbers.json").write_text(json.dumps(res, indent=1, default=str))
    # short print
    k = res
    print("expected", k["n_expected"], "missing_done", len(missing_done), "extra", extra)
    print("days zm0 rows/included", k["days_rows_zm0"], k["days_zm0_included"], k["days_zm0_excluded_reasons"])
    print("primary dates", k["dates_with_primary_placements"], "rows", k["placements_rows_primary"],
          "per-date counts", k["placements_per_date_counts"])
    print("K2 fills", k["K2_fills"], "rate", round(k["fill_rate"], 4), "fail", k["K2_fail"])
    for var in ("drop", "nodrop"):
        v = out[var]
        print(var, "n_valid", v["n_valid"], "dropped", v["n_dropped"], "meanE10", round(v["mean_E10"], 4),
              "meanN10", round(v["mean_N10_topstep"], 4))
        for pop in "AB":
            print("   pop", pop, {s: (round(v[f'pop{pop}_seed{s}']['lo'], 4), round(v[f'pop{pop}_seed{s}']['hi'], 4)) for s in seeds})
        print("   fee0.528 mean", round(v["mean_N10_at_0.528"], 4), v["popA_fee0.528_seed31"])
    print("K3 mean rt", round(k["K3_mean_rt_per_date"], 3), "min/med/max", k["K3_min_max_median"],
          "boot", {s: tuple(round(x, 2) for x in b) for s, b in k["K3_boot"].items()}, "fail", k["K3_fail"])
    print("loop rows c zm0", k["loop_rows_c_zm0"], "included", k["loop_rows_c_zm0_included"],
          "missing", k["loop_missing_for_included_dates"])


if __name__ == "__main__":
    main()
