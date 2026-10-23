"""OpusVerifier step 1: kill-rule numbers from placements.parquet and loop.parquet only.

Own code; does not import the producer's stats modules. Reads days.parquet only for the population
cross-check, and data.calendars.grains for the calendar check. Writes v1_numbers.json beside itself.
"""
import json
import os
import sys
from datetime import date, datetime, timedelta, time
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

os.nice(10)
REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from data.calendars import grains  # noqa: E402

RUNS = REPO / "reports/stage_e31_briefs/work/pilot/runs"
MEAS = RUNS / "measure31"
OUT = Path(__file__).resolve().parent / "v1_numbers.json"
CT = ZoneInfo("America/Chicago")
FEE = 0.264
FEE_RT = 0.528
B = 2000
COLS = ["trade_date", "session", "symbol", "model", "side", "g_ns", "j_ns", "price", "filled",
        "t_fill_ns", "trigger", "wait_s", "mid0", "c_half", "mo_10", "mo_nd_10", "instrument_id"]


def load():
    dates = [l.strip() for l in (RUNS / "expected31.txt").read_text().split() if l.strip()]
    pl, lp, dy = [], [], []
    for d in dates:
        p = MEAS / d
        assert (p / "DONE").exists(), d
        t = pq.read_table(p / "placements.parquet", columns=COLS).to_pandas()
        pl.append(t[(t.session == "DAY") & (t.symbol == "ZM.v.0") & (t.model == "c")])
        lp.append(pq.read_table(p / "loop.parquet").to_pandas())
        dy.append(pq.read_table(p / "days.parquet").to_pandas())
    return dates, pd.concat(pl, ignore_index=True), pd.concat(lp, ignore_index=True), \
        pd.concat(dy, ignore_index=True)


def ct_clock(ns):
    return pd.to_datetime(ns, utc=True).tz_convert(CT)


def calendar_trade_dates():
    out, d = [], date(2020, 12, 1)
    while d <= date(2024, 2, 29):
        h = grains.HOLIDAYS.get(d)
        full = h is not None and h.kind.name == "FULL_CLOSURE"
        if d.weekday() < 5 and not full:
            out.append(d)
        d += timedelta(days=1)
    return out


def boot(per_day_num, per_day_den, seed, b=B):
    rng = np.random.default_rng(seed)
    n = len(per_day_num)
    idx = rng.integers(0, n, size=(b, n))
    stat = per_day_num[idx].sum(1) / per_day_den[idx].sum(1)
    return np.percentile(stat, [2.5, 97.5]), stat


def main():
    dates, pl, lp, dy = load()
    res = {"n_expected_dates": len(dates)}
    # ---- calendar cross-check
    cal = calendar_trade_dates()
    res["calendar_trade_dates"] = len(cal)
    res["expected_minus_calendar"] = sorted(set(dates) - {c.isoformat() for c in cal})
    res["calendar_minus_expected"] = sorted({c.isoformat() for c in cal} - set(dates))
    excl_cal = {d.isoformat() for d, h in grains.HOLIDAYS.items()} | \
        {d.isoformat() for d in grains.LATE_OPENS}
    pl["td"] = pl.trade_date.astype(str)
    pop_dates = sorted(pl.td.unique())
    res["pop_dates"] = len(pop_dates)
    res["pop_dates_in_calendar_exclusions"] = sorted(set(pop_dates) & excl_cal)
    d0 = dy[dy.symbol == "ZM.v.0"].copy()
    d0["td"] = d0.trade_date.astype(str)
    inc = set(d0[d0.included].td)
    res["days_v0_included"] = len(inc)
    res["pop_dates_not_included"] = sorted(set(pop_dates) - inc)
    res["included_without_placements"] = sorted(inc - set(pop_dates))
    res["v0_reasons"] = d0[~d0.included].reason.value_counts().to_dict()
    # roll check from the logged instrument per date (all dates in file order)
    d0 = d0.sort_values("td")
    chg = d0.instrument_id.values[1:] != d0.instrument_id.values[:-1]
    roll = set(d0.td.values[1:][chg])
    after = {d0.td.values[i + 2] for i in np.where(chg)[0] if i + 2 < len(d0)}
    res["roll_days"] = sorted(roll)
    res["pop_dates_on_roll_or_after"] = sorted(set(pop_dates) & (roll | after))
    # ---- placement-grid checks
    g = ct_clock(pl.g_ns.values)
    mins = g.hour * 60 + g.minute
    res["grid_min_ct"] = str(g.min().time()) if len(g) else None
    res["grid_bad_clock"] = int(((mins < 8 * 60 + 35) | (mins > 13 * 60 + 10) | (g.second != 0)
                                 | (g.minute % 5 != 0)).sum())
    res["grid_ct_dates_differ"] = int((pd.Series(g.date).astype(str).values != pl.td.values).sum())
    res["j_minus_g_not_50ms"] = int(((pl.j_ns - pl.g_ns) != 50_000_000).sum())
    per_day = pl.groupby("td").size()
    res["placements_total"] = int(len(pl))
    res["placements_per_day_min_max"] = [int(per_day.min()), int(per_day.max())]
    res["days_with_lt_112"] = int((per_day < 112).sum())
    dup = pl.duplicated(["td", "g_ns", "side"]).sum()
    res["duplicate_g_side"] = int(dup)
    # ---- K2
    f = pl[pl.filled].copy()
    res["K2_fills"] = int(len(f))
    res["fills_buy_sell"] = [int((f.side == 1).sum()), int((f.side == -1).sum())]
    res["fill_rate"] = len(f) / len(pl)
    res["trigger_counts"] = f.trigger.value_counts().to_dict()
    life = (f.t_fill_ns - f.j_ns) / 1e9
    res["fill_outside_life"] = int(((life <= 0) | (life >= 60.05)).sum())
    res["wait_s_mismatch"] = int((np.abs(f.wait_s - life) > 1e-6).sum())
    res["c_half_mismatch"] = int((np.abs(f.c_half - f.side * (f.mid0 - f.price) / 0.1) > 1e-6).sum())
    res["unfilled_with_tfill"] = int((pl[~pl.filled].t_fill_ns != -1).sum())
    # ---- K1
    per = {}
    for var, col in (("drop", "mo_10"), ("nodrop", "mo_nd_10")):
        v = f[np.isfinite(f[col]) & np.isfinite(f.c_half)].copy()
        v["E10"] = v[col] + v.c_half
        r = {"n_valid": int(len(v)), "n_dropped": int(len(f) - len(v)),
             "mean_E10": float(v.E10.mean()),
             "mean_N10_0264": float(v.E10.mean() - FEE),
             "mean_N10_0528": float(v.E10.mean() - FEE_RT),
             "mean_mo10": float(v[col].mean()), "mean_c": float(v.c_half.mean())}
        s = v.groupby("td").E10.sum().reindex(pop_dates, fill_value=0.0).values
        n = v.groupby("td").size().reindex(pop_dates, fill_value=0).values.astype(float)
        num264 = s - FEE * n
        num528 = s - FEE_RT * n
        ci, st = boot(num264, n, 31)
        ci528, _ = boot(num528, n, 31)
        r["ci95_N10_0264_seed31"] = ci.tolist()
        r["ci95_N10_0528_seed31"] = ci528.tolist()
        r["boot_reps_nan"] = int(np.isnan(st).sum())
        lows = {}
        for sd in (7, 2024, 987654):
            c2, _ = boot(num264, n, sd)
            lows[str(sd)] = c2.tolist()
        r["ci95_N10_0264_other_seeds"] = lows
        r["lower_spread_across_4_seeds"] = float(
            max([ci[0]] + [x[0] for x in lows.values()]) - min([ci[0]] + [x[0] for x in lows.values()]))
        # alternate resampling unit: only dates with >=1 valid fill
        m = n > 0
        c3, _ = boot(num264[m], n[m], 31)
        r["ci95_N10_0264_seed31_dates_with_fills_only"] = c3.tolist()
        r["n_boot_dates"] = len(pop_dates)
        r["n_dates_with_valid_fill"] = int(m.sum())
        per[var] = r
    res["K1"] = per
    # ---- K3
    lc = lp[(lp.symbol == "ZM.v.0") & (lp.model == "c")].copy()
    lc["td"] = lc.trade_date.astype(str)
    res["loop_rows_c"] = int(len(lc))
    res["loop_dup_dates"] = int(lc.td.duplicated().sum())
    res["loop_dates_not_in_pop"] = sorted(set(lc.td) - set(pop_dates))
    res["pop_dates_without_loop"] = sorted(set(pop_dates) - set(lc.td))
    rt = lc.round_trips.values.astype(float)
    res["K3_mean_rt"] = float(rt.mean())
    res["K3_median_rt"] = float(np.median(rt))
    res["K3_min_max"] = [float(rt.min()), float(rt.max())]
    rng = np.random.default_rng(31)
    idx = rng.integers(0, len(rt), size=(B, len(rt)))
    res["K3_ci95_seed31"] = np.percentile(rt[idx].mean(1), [2.5, 97.5]).tolist()
    res["K3_dates_lt_20"] = int((rt < 20).sum())
    # ---- verdict
    k1 = {k: per[k]["ci95_N10_0264_seed31"][0] > 0 for k in per}
    k1_528 = {k: per[k]["ci95_N10_0528_seed31"][0] > 0 for k in per}
    fails = []
    if not all(k1.values()):
        fails.append("K1")
    if res["K2_fills"] < 400:
        fails.append("K2")
    if res["K3_mean_rt"] < 20:
        fails.append("K3")
    res["K1_clear"] = k1
    res["K1_clear_at_0528"] = k1_528
    res["fails"] = fails
    verdict = "FAIL" if fails else "PASS"
    if verdict == "PASS" and not all(k1_528.values()):
        verdict = "PASS, fragile (fee reading)"
    res["verdict"] = verdict
    OUT.write_text(json.dumps(res, indent=1, default=str))
    print("written", OUT)
    print("K2", res["K2_fills"], "K3", round(res["K3_mean_rt"], 4), "verdict", verdict, fails)
    for k in per:
        print(k, per[k]["n_valid"], round(per[k]["mean_N10_0264"], 5),
              [round(x, 5) for x in per[k]["ci95_N10_0264_seed31"]],
              [round(x, 5) for x in per[k]["ci95_N10_0528_seed31"]],
              "spread", round(per[k]["lower_spread_across_4_seeds"], 5))


if __name__ == "__main__":
    main()
