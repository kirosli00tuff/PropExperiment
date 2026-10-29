"""P6.2 statistics, the P8 gates G1-G5, the funnel, the ranking, the Tier A / Tier B walks and
the near-threshold list for all 300 configurations, computed twice: from the own re-simulated
series (derived/e33/verify_c/resim/<cid>.json and .trades.parquet) and from the pipeline's
daily.parquet / trades.parquet. Writes derived/e33/verify_c/gates_<source>.json and prints counts.

Usage: gates_all.py --source own|parquet
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_common as vc  # noqa: E402

FOLD_BLOCKS = [133, 133, 133, 133, 132, 132]


def fold_of_index() -> list[int]:
    out = []
    for k, n in enumerate(FOLD_BLOCKS, start=1):
        out += [k] * n
    assert len(out) == vc.T_DISC
    return out


def load_series(cid: str, source: str, dates: list[str]):
    """(X_D[796], n_trades[796], trade nets array, fold_of_date[796])."""
    if source == "own":
        r = json.load(open(vc.OUT / "resim" / f"{cid}.json"))
        if r["dates"] != dates:
            raise RuntimeError(f"{cid}: own dates differ")
        tr = pq.read_table(vc.OUT / "resim" / f"{cid}.trades.parquet", columns=["net"])
        return (np.asarray(r["X_D"], dtype=np.float64), np.asarray(r["n_trades_per_date"], dtype=np.int64),
                tr.column("net").to_numpy(zero_copy_only=False).astype(np.float64), r["fold_of_date"])
    root = vc.SEARCH / cid
    d = pq.read_table(root / "daily.parquet").to_pandas()
    if list(d["date"]) != dates:
        raise RuntimeError(f"{cid}: daily.parquet dates differ from the OOF dates")
    tr = pq.read_table(root / "trades.parquet", columns=["net"])
    nets = tr.column("net").to_numpy(zero_copy_only=False).astype(np.float64) if tr.num_rows else np.zeros(0)
    return (d["X_D"].to_numpy(dtype=np.float64), d["n_trades"].to_numpy(dtype=np.int64), nets, fold_of_index())


def p62_stats(cid: str, x: np.ndarray, n_tr: np.ndarray, nets: np.ndarray, folds: list[int],
              dates: list[str], terc: dict[str, int]) -> dict:
    info = vc.parse_config(cid)
    mom = vc.moments(x)
    count = int(n_tr.sum())
    if count != nets.size:
        raise RuntimeError(f"{cid}: n_trades sum {count} != trades rows {nets.size}")
    total = math.fsum(x.tolist())
    if count and not vc.rel_equal(total, math.fsum(nets.tolist()), rel=1e-9, abs_=1e-9):
        raise RuntimeError(f"{cid}: sum X_D {total} != sum trade nets {math.fsum(nets.tolist())}")
    dates_with_trade = int((n_tr > 0).sum())
    per_fold = {str(k): 0.0 for k in range(1, 7)}
    per_month, per_quarter = {}, {}
    terc_vals = {1: [], 2: [], 3: []}
    for j, ds in enumerate(dates):
        per_fold[str(folds[j])] += x[j]
        per_month[vc.month_key(ds)] = per_month.get(vc.month_key(ds), 0.0) + x[j]
        per_quarter[vc.quarter_key(ds)] = per_quarter.get(vc.quarter_key(ds), 0.0) + x[j]
        terc_vals[terc[ds]].append(x[j])
    # exact sums with fsum
    per_month = {m: math.fsum(x[j] for j, ds in enumerate(dates) if vc.month_key(ds) == m) for m in per_month}
    per_quarter = {q: math.fsum(x[j] for j, ds in enumerate(dates) if vc.quarter_key(ds) == q) for q in per_quarter}
    per_fold = {k: math.fsum(x[j] for j in range(len(dates)) if folds[j] == int(k)) for k in per_fold}
    if len(per_month) != 39 or len(per_quarter) != 13:
        raise RuntimeError(f"{cid}: {len(per_month)} months, {len(per_quarter)} quarters")
    vol = {str(k): {"n": len(v), "sum": math.fsum(v), "mean": math.fsum(v) / len(v)} for k, v in terc_vals.items()}
    st = {
        "config": cid, **info, "moments": mom, "t_stat": vc.t_stat(mom), "trade_count": count,
        "trades_per_date": count / vc.T_DISC,
        "mean_net_per_trade": (total / count) if count else None,
        "hit_rate": (float((nets > 0).sum()) / count) if count else None,
        "dates_with_trade": dates_with_trade, "share_dates_with_trade": dates_with_trade / vc.T_DISC,
        "total_net": total, "per_fold": per_fold, "per_month": per_month, "per_quarter": per_quarter,
        "vol_terciles": vol, "constant_series": mom["sd"] == 0.0,
    }
    return st


def gates(st: dict, x: np.ndarray, dates: list[str], b_test: float) -> dict:
    mom = st["moments"]
    sr, g3, g4 = mom["sharpe"], mom["skew"], mom["kurtosis"]
    v = 1.0 / (vc.T_DISC - 1)
    out = {}
    out["G1"] = (st["trade_count"] >= vc.G1_TRADES_PER_DATE * vc.T_DISC
                 and st["dates_with_trade"] >= vc.G1_SHARE_DATES * vc.T_DISC)
    out["G2"] = st["mean_net_per_trade"] is not None and st["mean_net_per_trade"] >= vc.G2_MEAN_NET
    prog = vc.program_dsr(sr, vc.T_DISC, vc.N_TRIALS, v, g3, g4)
    own = vc.own_dsr(sr, vc.T_DISC, vc.N_TRIALS, v, g3, g4)
    out["dsr_program"], out["dsr_own"] = prog, own
    out["G3"] = prog["dsr"] is not None and prog["dsr"] > vc.DSR_TARGET
    out["G3_own_formula"] = own["dsr"] is not None and own["dsr"] > vc.DSR_TARGET
    se = vc.se_sharpe(sr, vc.T_DISC, g3, g4)
    out["se_sharpe"] = se
    out["sr_minus_se"] = (sr - se) if se is not None else None
    out["b_test"] = b_test
    out["G4"] = se is not None and (sr - se) >= b_test
    # G5
    q_pos = sum(1 for q, s in st["per_quarter"].items() if s / sum(1 for d in dates if vc.quarter_key(d) == q) > 0)
    out["G5a_quarters_positive"] = q_pos
    out["G5a"] = q_pos >= vc.G5A_QUARTERS
    total = st["total_net"]
    max_month = max(st["per_month"].values()) if st["per_month"] else 0.0
    out["G5b_total"] = total
    out["G5b_max_month_share"] = (max_month / total) if total > 0 else None
    out["G5b"] = total > 0 and all(m <= vc.G5B_MONTH_SHARE * total for m in st["per_month"].values())
    months = sorted(st["per_month"])
    loo_t = {}
    for m in months:
        keep = np.array([vc.month_key(d) != m for d in dates])
        mm = vc.moments(x[keep])
        loo_t[m] = vc.t_stat(mm)
    out["G5c_loo_t"] = loo_t
    finite = [t for t in loo_t.values() if t is not None]
    out["G5c_min_t"] = min(finite) if len(finite) == len(loo_t) else None
    out["G5c"] = len(finite) == len(loo_t) and all(t >= vc.G5C_T for t in finite)
    tm = [st["vol_terciles"][k]["mean"] for k in ("1", "2", "3")]
    out["G5d_tercile_means"] = tm
    out["G5d"] = all(m > 0 for m in tm)
    out["G5"] = out["G5a"] and out["G5b"] and out["G5c"] and out["G5d"]
    out["pass_all"] = out["G1"] and out["G2"] and out["G3"] and out["G4"] and out["G5"]
    return out


def rank_key(st: dict):
    return (-round(st["moments"]["sharpe"], 4), st["trades_per_date"], 0 if st["family"] == "LOGIT" else 1,
            st["set_idx"], st["h"], st["kind"], st["grid_idx"])


def near_threshold(st: dict, g: dict) -> list[dict]:
    """Within 10% of a gate threshold: |v - thr| <= 0.1 |thr| for thr != 0; for the zero thresholds
    (G5 b total > 0, G5 d tercile mean > 0) within 0.1 standard errors of zero."""
    sd = st["moments"]["sd"]
    items = []

    def chk(name, v, thr, scale=None):
        if v is None:
            return
        tol = vc.NEAR_FRAC * (abs(thr) if thr != 0 else (scale or 0.0))
        if abs(v - thr) <= tol:
            items.append({"gate": name, "value": v, "threshold": thr, "tolerance": tol})

    chk("G1 trade_count", st["trade_count"], vc.G1_TRADES_PER_DATE * vc.T_DISC)
    chk("G1 dates_with_trade", st["dates_with_trade"], vc.G1_SHARE_DATES * vc.T_DISC)
    chk("G2 mean_net_per_trade", st["mean_net_per_trade"], vc.G2_MEAN_NET)
    chk("G3 DSR", g["dsr_program"]["dsr"], vc.DSR_TARGET)
    chk("G4 SR-se", g["sr_minus_se"], g["b_test"])
    chk("G5a quarters_positive", g["G5a_quarters_positive"], vc.G5A_QUARTERS)
    chk("G5b total", g["G5b_total"], 0.0, scale=sd * math.sqrt(vc.T_DISC))
    chk("G5b max_month_share", g["G5b_max_month_share"], vc.G5B_MONTH_SHARE)
    chk("G5c min_loo_t", g["G5c_min_t"], vc.G5C_T)
    for k, m in enumerate(g["G5d_tercile_means"], start=1):
        n_k = st["vol_terciles"][str(k)]["n"]
        chk(f"G5d tercile{k} mean", m, 0.0, scale=sd / math.sqrt(n_k))
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["own", "parquet"], required=True)
    a = ap.parse_args()
    dates = vc.oof_dates()
    sigma = vc.load_sigma_zm(dates)
    terc = vc.tercile_of_dates(dates, sigma)
    bt = vc.b_test_values()
    b_test = bt["b_test_program"]
    vc.log("b_test values", json.dumps(bt))
    ids = vc.all_config_ids()
    stats, gts, series = {}, {}, {}
    for cid in ids:
        x, n_tr, nets, folds = load_series(cid, a.source, dates)
        st = p62_stats(cid, x, n_tr, nets, folds, dates, terc)
        g = gates(st, x, dates, b_test)
        stats[cid], gts[cid], series[cid] = st, g, x
    # funnel
    alone = {k: sum(1 for c in ids if gts[c][k]) for k in ("G1", "G2", "G3", "G4", "G5")}
    in_order, passing = {}, list(ids)
    for k in ("G1", "G2", "G3", "G4", "G5"):
        passing = [c for c in passing if gts[c][k]]
        in_order["G1" if k == "G1" else f"G1..{k}"] = len(passing)
    alone_own_dsr = sum(1 for c in ids if gts[c]["G3_own_formula"])
    # ranking and walks
    order = sorted(ids, key=lambda c: rank_key(stats[c]))
    passers = [c for c in order if gts[c]["pass_all"]]

    def corr_ok(c, taken):
        for t in taken:
            r = np.corrcoef(series[c], series[t])[0, 1]
            if not math.isfinite(r) or r > vc.CORR_MAX:
                return False
        return True

    tier_a, pos = [], 0
    for pos, c in enumerate(order):
        if len(tier_a) >= 3:
            break
        if gts[c]["pass_all"] and corr_ok(c, tier_a):
            tier_a.append(c)
    # Tier B (R-L8: continue from where the Tier A walk stopped; here from the position reached)
    start = 0 if not tier_a else order.index(tier_a[-1]) + 1
    tier_b, tier_b_corr = [], {}
    for c in order[start:]:
        if len(tier_b) >= 2:
            break
        if stats[c]["constant_series"]:
            continue
        taken = tier_a + tier_b
        rs = [float(np.corrcoef(series[c], series[t])[0, 1]) for t in taken]
        if all(math.isfinite(r) and r <= vc.CORR_MAX for r in rs):
            tier_b.append(c)
            tier_b_corr[c] = rs
    near = {c: near_threshold(stats[c], gts[c]) for c in ids}
    near = {c: v for c, v in near.items() if v}
    top10 = order[:10]
    summary = {
        "source": a.source, "n_configs": len(ids), "N": vc.N_TRIALS, "T": vc.T_DISC, "b_test_values": bt,
        "funnel_alone": alone, "funnel_in_order": in_order, "G3_alone_own_formula": alone_own_dsr,
        "passers": passers, "tier_a": tier_a, "tier_b": tier_b, "tier_b_corr": tier_b_corr,
        "ranking": order, "top10": top10, "near_threshold": near,
        "n_constant_series": sum(1 for c in ids if stats[c]["constant_series"]),
        "n_with_trades": sum(1 for c in ids if stats[c]["trade_count"] > 0),
        "sigma_terciles_bounds": {
            "t1_max_sigma": max(sigma[d] for d in dates if terc[d] == 1),
            "t2_min_sigma": min(sigma[d] for d in dates if terc[d] == 2),
            "t2_max_sigma": max(sigma[d] for d in dates if terc[d] == 2),
            "t3_min_sigma": min(sigma[d] for d in dates if terc[d] == 3)},
    }
    vc.write_json(vc.OUT / f"gates_{a.source}.json", {"summary": summary, "stats": stats, "gates": gts})
    vc.log(f"source {a.source}: funnel alone {alone}; in order {in_order}; G3 own-formula alone {alone_own_dsr}")
    vc.log(f"passers {passers}; tier_a {tier_a}; tier_b {tier_b} corr {tier_b_corr}")
    vc.log(f"top10 {top10}")
    vc.log(f"near-threshold configs {len(near)}: " + "; ".join(f"{c}:{[i['gate'] for i in v]}" for c, v in near.items()))
    vc.log(f"constant series {summary['n_constant_series']}, with trades {summary['n_with_trades']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
