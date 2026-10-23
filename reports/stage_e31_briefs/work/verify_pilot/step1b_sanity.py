"""Population-level sanity checks on the producer's per-day tables (no raw data), plus roll/calendar exclusions."""
import json, os
from datetime import date, datetime
from pathlib import Path
import numpy as np, pandas as pd
from data.calendars.grains import HOLIDAYS, LATE_OPENS
os.nice(10)
ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
RUNS = ROOT / "reports/stage_e31_briefs/work/pilot/runs"; MEAS = RUNS / "measure31"; OUT = ROOT / "reports/stage_e31_briefs/work/verify_pilot"
exp = RUNS.joinpath("expected31.txt").read_text().split()
P, D = [], []
for d in exp:
    p = pd.read_parquet(MEAS / d / "placements.parquet")
    P.append(p[(p.symbol == "ZM.v.0") & (p.session == "DAY") & (p.model == "c")])
    D.append(pd.read_parquet(MEAS / d / "days.parquet"))
P = pd.concat(P, ignore_index=True); D = pd.concat(D, ignore_index=True)
res = {}
F = P[P.filled].copy()
F["E_drop"] = F.mo_10 + F.c_half; F["E_nd"] = F.mo_nd_10 + F.c_half
res["mo10_equals_mond10_all"] = bool(np.array_equal(F.mo_10.to_numpy(), F.mo_nd_10.to_numpy(), equal_nan=True))
res["mo10_nan"] = int(F.mo_10.isna().sum()); res["mond10_nan"] = int(F.mo_nd_10.isna().sum()); res["c_half_nan"] = int(F.c_half.isna().sum())
res["date_range"] = [str(P.trade_date.min()), str(P.trade_date.max())]
res["wait_consistency_maxabs_s"] = float(np.abs((F.t_fill_ns - F.j_ns) / 1e9 - F.wait_s).max())
res["wait_max"] = float(F.wait_s.max()); res["wait_min"] = float(F.wait_s.min())
res["j_minus_g_all_50ms"] = bool(((P.j_ns - P.g_ns) == 50_000_000).all())
res["unfilled_have_tfill"] = int((P[~P.filled].t_fill_ns > 0).sum()) if P.t_fill_ns.dtype.kind in "iu" else None
res["trigger_filled"] = F.trigger.value_counts().to_dict(); res["trigger_unfilled"] = P[~P.filled].trigger.value_counts().to_dict()
res["mean_c_half"] = float(F.c_half.mean()); res["mean_mo10"] = float(F.mo_10.mean()); res["mean_E10"] = float(F.E_drop.mean())
res["std_E10"] = float(F.E_drop.std()); res["median_E10"] = float(F.E_drop.median()); res["share_E10_pos"] = float((F.E_drop > 0).mean())
F["year"] = pd.to_datetime(F.trade_date).dt.year; F["ym"] = pd.to_datetime(F.trade_date).dt.to_period("M")
res["meanN10_by_year"] = (F.groupby("year").apply(lambda g: float((g.E_drop - 0.264).mean()))).round(4).to_dict()
res["meanN10_by_side"] = (F.groupby("side").apply(lambda g: float((g.E_drop - 0.264).mean()))).round(4).to_dict()
bym = F.groupby("ym").apply(lambda g: float((g.E_drop - 0.264).mean()))
res["months_total"] = int(len(bym)); res["months_with_positive_meanN10"] = int((bym > 0).sum()); res["max_month_meanN10"] = float(bym.max())
res["fills_by_side"] = F.side.value_counts().to_dict()
res["fills_per_date_min_med_max"] = F.groupby("trade_date").size().agg(["min", "median", "max"]).tolist()
# half-spread sanity: buy at best bid => mid0 - p >= 0 unless stale
res["c_half_negative_share"] = float((F.c_half < 0).mean())
# ----- exclusions: roll days from the instrument sequence, calendar closures/late opens
Z = D[D.symbol == "ZM.v.0"].copy(); Z["td"] = pd.to_datetime(Z.trade_date).dt.date
Z = Z.sort_values("td").reset_index(drop=True)
chg = Z.instrument_id != Z.instrument_id.shift(1)
chg.iloc[0] = False
roll_dates = set(Z.td[chg]); after = set(Z.td.shift(-0)[chg.shift(1, fill_value=False)])
exp_excl = roll_dates | after
res["instrument_change_dates"] = len(roll_dates)
excl = Z[~Z.included]
rd = excl[excl.reason == "roll_day"].td; ar = excl[excl.reason == "after_roll_day"].td
res["roll_day_equals_change_dates"] = bool(set(rd) == roll_dates)
res["after_roll_day_equals_next_dates"] = bool(set(ar) == after)
res["excl_reasons"] = excl.reason.value_counts().to_dict()
cal_h = {d for d in Z.td if d in HOLIDAYS}; cal_l = {d for d in Z.td if d in LATE_OPENS}
res["calendar_holiday_dates_in_expected"] = len(cal_h); res["calendar_late_open_dates_in_expected"] = len(cal_l)
res["included_but_holiday"] = sorted(map(str, set(Z.td[Z.included]) & set(HOLIDAYS)))
res["included_but_late_open"] = sorted(map(str, set(Z.td[Z.included]) & set(LATE_OPENS)))
res["excluded_cme_reason_dates_in_calendar"] = bool(set(excl[excl.reason == "cme_holiday_or_early_close"].td) <= set(HOLIDAYS))
res["excluded_late_open_dates_in_calendar"] = bool(set(excl[excl.reason == "scheduled_late_open"].td) <= set(LATE_OPENS))
res["holiday_dates_not_excluded_as_cme"] = sorted(map(str, cal_h - set(excl[excl.reason == "cme_holiday_or_early_close"].td)))[:12]
res["late_open_dates_not_excluded"] = sorted(map(str, cal_l - set(excl[excl.reason == "scheduled_late_open"].td)))[:12]
res["max_gap_day_s_included_max"] = float(Z[Z.included].max_gap_day_s.max())
res["included_bad_flag_records_total"] = int(Z[Z.included].bad_flag_records.sum()); res["included_crossed_moments_total"] = int(Z[Z.included].crossed_moments.sum())
(OUT / "sanity.json").write_text(json.dumps(res, indent=1, default=str))
for k, v in res.items(): print(k, v)
