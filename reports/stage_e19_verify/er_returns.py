"""EconReviewer Phase A item 1: independent rebuild of the per-path day-session table.

Written from reports/stage_e19_briefs/sim_spec.md section 1 and the definitions block of
reports/stage_e19_returns_summary.json, without importing prop_econ. Reads only the five E.12 training
stores (columns ts_event, open, high, low, close, instrument_id, trade_date), reports/stage_e2a_costs.json
and screening/vehicles.py's D6_SESSIONS. Prints summaries only, never rows.

Outputs (reports/stage_e19_verify/):
  er_returns.npz          per path: z_long, w_long, z_short, w_short, r_usd, dates (kept), sigma_full
  er_returns_check.json   my numbers next to the summary's, with pass/fail flags
"""
from __future__ import annotations

import json
import os
import sys
import time as _time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

os.nice(10)
REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from screening.vehicles import D6_SESSIONS, METALS_SUBGROUP  # noqa: E402

OUT = REPO / "reports" / "stage_e19_verify"
SUMMARY = json.loads((REPO / "reports" / "stage_e19_returns_summary.json").read_text())
COSTS = json.loads((REPO / "reports" / "stage_e2a_costs.json").read_text())
ROOTS = ("NQ", "CL", "GC", "ZN", "6E")
GROUP = {"NQ": "equity", "CL": "energy", "GC": METALS_SUBGROUP["GC"], "ZN": "rates", "6E": "fx"}
MICRO = {"NQ": "MNQ", "CL": "MCL", "GC": "MGC", "ZN": None, "6E": "M6E"}
TRAIN_FIRST, TRAIN_LAST = "2019-05-06", "2024-02-29"
SKIPS = ("no_bars_in_window", "instrument_change", "missing_open_bar", "missing_close_bar")


def store(root: str) -> Path:
    fs = sorted((REPO / "data" / "processed_step2" / root).glob("*.parquet"))
    assert len(fs) == 1, fs
    return fs[0]


def multiplier(root: str) -> float:
    e = COSTS["products"][root]
    return float(e["tick_value_usd"]) / float(e["tick_size"])


def session_table(root: str) -> dict:
    o_t, c_t = D6_SESSIONS[GROUP[root]]
    o_min, c_min = o_t.hour * 60 + o_t.minute, c_t.hour * 60 + c_t.minute
    t = pq.read_table(store(root), columns=["ts_event", "open", "high", "low", "close",
                                            "instrument_id", "trade_date"])
    ts = t.column("ts_event").to_numpy()
    td = np.asarray(t.column("trade_date").to_numpy(zero_copy_only=False), dtype="U10")
    td_sorted = np.sort(td)
    assert td_sorted[0] >= TRAIN_FIRST and td_sorted[-1] <= TRAIN_LAST, (td_sorted[0], td_sorted[-1])
    ct = pd.to_datetime(ts, utc=True).tz_convert("America/Chicago")
    ct_min = (ct.hour * 60 + ct.minute).to_numpy()
    ct_date = ct.strftime("%Y-%m-%d").to_numpy().astype("U10")
    same_day = ct_date == td
    in_win = same_day & (ct_min >= o_min) & (ct_min < c_min)
    all_dates = np.unique(td)
    op = t.column("open").to_numpy()
    hi = t.column("high").to_numpy()
    lo = t.column("low").to_numpy()
    cl = t.column("close").to_numpy()
    iid = t.column("instrument_id").to_numpy()
    # restrict to the window, then group by trade date
    w_td, w_min, w_op, w_hi, w_lo, w_cl, w_iid = (a[in_win] for a in
                                                 (td, ct_min, op, hi, lo, cl, iid))
    order = np.lexsort((w_min, w_td))
    w_td, w_min, w_op, w_hi, w_lo, w_cl, w_iid = (a[order] for a in
                                                 (w_td, w_min, w_op, w_hi, w_lo, w_cl, w_iid))
    starts = np.r_[0, np.flatnonzero(w_td[1:] != w_td[:-1]) + 1, len(w_td)]
    win_dates = w_td[starts[:-1]]
    skips = {k: 0 for k in SKIPS}
    skipped_dates: dict[str, list[str]] = {k: [] for k in SKIPS}
    kept_dates, O, H, L, C = [], [], [], [], []
    have = set(win_dates.tolist())
    for d in all_dates.tolist():
        if d not in have:
            skips["no_bars_in_window"] += 1
            skipped_dates["no_bars_in_window"].append(d)
    mult = multiplier(root)
    for i in range(len(win_dates)):
        a, b = starts[i], starts[i + 1]
        mins = w_min[a:b]
        if len(np.unique(w_iid[a:b])) != 1:
            skips["instrument_change"] += 1
            skipped_dates["instrument_change"].append(win_dates[i])
            continue
        if mins[0] != o_min:
            skips["missing_open_bar"] += 1
            skipped_dates["missing_open_bar"].append(win_dates[i])
            continue
        if mins[-1] != c_min - 1:
            skips["missing_close_bar"] += 1
            skipped_dates["missing_close_bar"].append(win_dates[i])
            continue
        kept_dates.append(win_dates[i])
        O.append(w_op[a]); C.append(w_cl[b - 1]); H.append(w_hi[a:b].max()); L.append(w_lo[a:b].min())
    O, H, L, C = (np.asarray(x, dtype=float) for x in (O, H, L, C))
    r = (C - O) * mult
    up = (H - O) * mult
    dn = (L - O) * mult
    assert np.all(up >= 0) and np.all(dn <= 0) and np.all(up >= r) and np.all(dn <= r)
    mean_r = r.mean()
    rp = r - mean_r
    sigma = rp.std(ddof=1)
    z_l = rp / sigma
    w_l = np.minimum(np.minimum(dn, rp), 0.0) / sigma
    z_s = -rp / sigma
    w_s = np.minimum(np.minimum(-up, -rp), 0.0) / sigma
    m2, m3, m4 = (np.mean(z_l ** k) for k in (2, 3, 4))
    out = {
        "root": root, "window_ct": f"{o_t:%H:%M}-{c_t:%H:%M}", "multiplier": mult,
        "trade_dates": int(len(all_dates)), "dates_kept": int(len(kept_dates)),
        "first_kept": kept_dates[0], "last_kept": kept_dates[-1], "skips": skips,
        "mean_r_removed_usd_full": float(mean_r), "sigma_full_usd": float(sigma),
        "mean_rp_abs": float(abs(rp.mean())),
        "z_skew_pop": float(m3 / m2 ** 1.5), "z_excess_kurtosis_pop": float(m4 / m2 ** 2 - 3),
        "share_abs_z_gt_4": float(np.mean(np.abs(z_l) > 4)),
        "w_long": {"mean": float(w_l.mean()), "p01": float(np.percentile(w_l, 1))},
        "w_short": {"mean": float(w_s.mean()), "p01": float(np.percentile(w_s, 1))},
        "w_le_min0z_long": bool(np.all(w_l <= np.minimum(0, z_l) + 1e-12)),
        "w_le_min0z_short": bool(np.all(w_s <= np.minimum(0, z_s) + 1e-12)),
        "w_le_min0z_long_strict_count_viol": int(np.sum(w_l > np.minimum(0, z_l))),
        "w_le_min0z_short_strict_count_viol": int(np.sum(w_s > np.minimum(0, z_s))),
        "mult_check_vs_summary": float(SUMMARY_PATH(root)["multiplier_usd_per_point"]),
    }
    arrays = {"z_long": z_l, "w_long": w_l, "z_short": z_s, "w_short": w_s, "r_usd": r,
              "dates": np.asarray(kept_dates, dtype="U10"), "sigma_full": np.asarray([sigma])}
    return out, arrays, skipped_dates


def SUMMARY_PATH(root: str) -> dict:
    return next(p for p in SUMMARY["paths"] if p["root"] == root)


def d8_rt() -> dict:
    """Mean over the D8 day-session buckets of (commission + buy side + sell side) x tick value."""
    out = {}
    for root in ROOTS:
        for v in (root, MICRO[root]):
            if v is None:
                continue
            e = COSTS["products"][v]
            assert e["calibrated"] is True
            tv = float(e["tick_value_usd"])
            comm_ticks = float(e["commission_rt_usd"]) / tv
            o, c = e["day_session_ct"]["open"], e["day_session_ct"]["close"]
            o_m = int(o[:2]) * 60 + int(o[3:]); c_m = int(c[:2]) * 60 + int(c[3:])
            day = [b for b in e["buckets"] if b["day_session"]]
            inside = [b for b in e["buckets"] if b["start_min"] >= o_m and b["end_min"] <= c_m]
            rts = [(comm_ticks + b["side_ticks"]["buy"] + b["side_ticks"]["sell"]) * tv for b in day]
            rts_inside = [(comm_ticks + b["side_ticks"]["buy"] + b["side_ticks"]["sell"]) * tv
                          for b in inside]
            ref = e["headline_day_session"]["round_turn_usd"]["mean"]
            out[v] = {"rt_d8_mean_usd": float(np.mean(rts)), "n_day_buckets": len(day),
                      "rt_mean_window_buckets": float(np.mean(rts_inside)),
                      "n_window_buckets": len(inside),
                      "day_flag_equals_window": sorted(b["key"] for b in day) ==
                      sorted(b["key"] for b in inside),
                      "fallback_day_buckets": int(sum(b["fallback"] for b in day)),
                      "table_headline_mean": ref, "commission_rt_usd": e["commission_rt_usd"],
                      "q_c": e["q_c"], "d6_window": D6_SESSIONS[GROUP[root]].__repr__(),
                      "d8_window": f"{o}-{c}"}
    return out


def main() -> None:
    t0 = _time.time()
    OUT.mkdir(exist_ok=True)
    checks, arrays_all, skipped_all = {}, {}, {}
    for root in ROOTS:
        res, arrays, skipped = session_table(root)
        s = SUMMARY_PATH(root)
        res["vs_summary"] = {
            "dates_kept": [res["dates_kept"], s["dates_kept"]],
            "skips": [res["skips"], s["skips"]],
            "sigma_full_usd": [res["sigma_full_usd"], s["sigma_full_usd"],
                               abs(res["sigma_full_usd"] - s["sigma_full_usd"])],
            "mean_r_removed": [res["mean_r_removed_usd_full"], s["mean_r_removed_usd_full"]],
            "z_skew": [res["z_skew_pop"], s["z_skew"]],
            "z_exkurt": [res["z_excess_kurtosis_pop"], s["z_excess_kurtosis"]],
            "share_abs_z_gt_4": [res["share_abs_z_gt_4"], s["share_abs_z_gt_4"]],
            "w_long": [res["w_long"], s["w_long"]], "w_short": [res["w_short"], s["w_short"]],
        }
        res["match"] = {
            "dates_kept": res["dates_kept"] == s["dates_kept"],
            "skips": res["skips"] == s["skips"],
            "sigma_1e-6": abs(res["sigma_full_usd"] - s["sigma_full_usd"]) < 1e-6,
            "mean_r_1e-6": abs(res["mean_r_removed_usd_full"] - s["mean_r_removed_usd_full"]) < 1e-6,
            "skew_1e-9": abs(res["z_skew_pop"] - s["z_skew"]) < 1e-9,
            "kurt_1e-9": abs(res["z_excess_kurtosis_pop"] - s["z_excess_kurtosis"]) < 1e-9,
            "w_long_mean_1e-9": abs(res["w_long"]["mean"] - s["w_long"]["mean"]) < 1e-9,
            "w_long_p01_1e-9": abs(res["w_long"]["p01"] - s["w_long"]["p01"]) < 1e-9,
            "w_short_mean_1e-9": abs(res["w_short"]["mean"] - s["w_short"]["mean"]) < 1e-9,
            "w_short_p01_1e-9": abs(res["w_short"]["p01"] - s["w_short"]["p01"]) < 1e-9,
            "demeaned_mean_lt_1e-9_usd": res["mean_rp_abs"] < 1e-9,
            "multiplier": res["multiplier"] == s["multiplier_usd_per_point"],
        }
        checks[root] = res
        skipped_all[root] = skipped
        for k, v in arrays.items():
            arrays_all[f"{root}_{k}"] = v
        print(root, "kept", res["dates_kept"], "skips", res["skips"], "sigma", round(res["sigma_full_usd"], 3),
              "match", all(res["match"].values()), flush=True)
    rt = d8_rt()
    rt_match = {}
    for root in ROOTS:
        s = SUMMARY_PATH(root)
        for v, x in s["vehicles"].items():
            rt_match[v] = {"mine": rt[v]["rt_d8_mean_usd"], "summary": x["rt_d8_usd"],
                           "table_headline": rt[v]["table_headline_mean"],
                           "match_1e-9": abs(rt[v]["rt_d8_mean_usd"] - x["rt_d8_usd"]) < 1e-9,
                           "sigma_micro_is_tenth": (x["sigma_usd"] == s["sigma_full_usd"]
                                                    if v == root else
                                                    abs(x["sigma_usd"] - s["sigma_full_usd"] / 10) < 1e-9)}
    np.savez_compressed(OUT / "er_returns.npz", **arrays_all)
    report = {"generated": datetime.now(timezone.utc).astimezone().isoformat(),
              "elapsed_s": round(_time.time() - t0, 1), "paths": checks, "d8_rt": rt,
              "d8_rt_vs_summary": rt_match, "skipped_dates": skipped_all,
              "all_paths_match": all(all(c["match"].values()) for c in checks.values()),
              "all_rt_match": all(m["match_1e-9"] for m in rt_match.values())}
    (OUT / "er_returns_check.json").write_text(json.dumps(report, indent=1, default=str))
    print("all_paths_match", report["all_paths_match"], "all_rt_match", report["all_rt_match"],
          "elapsed", report["elapsed_s"])


if __name__ == "__main__":
    main()
