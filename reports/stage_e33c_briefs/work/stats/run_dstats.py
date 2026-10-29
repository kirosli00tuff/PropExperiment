"""Stage E.33c Part D, branch N (Tier A empty): D1, D3 and P10 null-report items (i)-(vi).

    PYTHONPYCACHEPREFIX=<scratch> nice -n 10 uv run python reports/stage_e33c_briefs/work/stats/run_dstats.py

Writes reports/stage_e33c_briefs/work/D_stats.json, work/stats/fig/fig_data.json and the full per-configuration
table derived/e33/stats_c/per_config_full.json. Prints counts and summaries only. Never re-selects: the selection
is select33's output, which is compared against, not replaced.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
for _p in (str(REPO), str(HERE), str(REPO / "reports" / "stage_e32_briefs" / "protocol")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import dstats_io as IO  # noqa: E402
import dstats_lib as L  # noqa: E402
import p7_final as P7  # noqa: E402
from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe  # noqa: E402
from screening.stage_e_verdict import moments, pbo as verdict_pbo, t_stat  # noqa: E402

N_REGISTERED = 838
NUM_FIELDS = ("sharpe", "t", "dsr", "se", "sr_lower", "trade_count", "dates_with_trade", "mean_net_per_trade",
              "total_net", "trades_per_date", "share_dates_with_trade")
G5_FIELDS = ("quarters_positive", "max_month_sum", "max_month_share", "min_lomo_t", "lomo_undefined", "total")


# ---------------------------------------------------------------- thresholds (P7.2 via p7_final)
def thresholds(n: int) -> dict:
    t_disc = P7.trade_dates(*P7.DISCOVERY) - P7.BURN_IN
    t_test = P7.trade_dates(*P7.TEST_MBO) - P7.BURN_IN
    sr0 = expected_max_sharpe(n, 1 / (t_disc - 1))
    g3 = P7.required_sharpe(n, t_disc, 1 / (t_disc - 1), 0.0, 3.0)
    g3_fat = P7.required_sharpe(n, t_disc, 1 / (t_disc - 1), -0.5, 6.0)
    b_test = max(3.0 / math.sqrt(t_test), P7.required_sharpe(n, t_test, 1 / (t_test - 1), 0.0, 3.0))
    g4 = P7.g4_threshold(b_test, t_disc)
    return {"N": n, "T_disc": t_disc, "T_test": t_test, "SR0": sr0, "G3": g3, "G3_skew-0.5_kurt6": g3_fat,
            "b_test": b_test, "G4": g4, "binding": max(g3, g4), "source": "p7_final.py functions at N"}


# ---------------------------------------------------------------- P6.2 recomputation per configuration
def p62(c: dict, dates: list, sigma: list) -> dict:
    x, net = c["x"], c["trade_net"]
    folds = {str(k + 1): math.fsum(x[j] for j in s) for k, s in enumerate(L.fold_slices(len(x)))}
    quarters = {k: {"sum": math.fsum(x[j] for j in idx), "mean": math.fsum(x[j] for j in idx) / len(idx),
                    "n_dates": len(idx)} for k, idx in L.group_indices(dates, L.quarter_key).items()}
    months = {k: {"sum": math.fsum(x[j] for j in idx), "n_dates": len(idx)}
              for k, idx in L.group_indices(dates, lambda d: d[:7]).items()}
    terc = [math.fsum(x[j] for j in s) / len(s) for s in L.tercile_slices(dates, sigma)]
    n = len(net)
    return {"hit_rate": float(np.mean(net > 0)) if n else None,
            "mean_net_per_trade_from_trades": float(math.fsum(net) / n) if n else None,
            "trades_rows": n, "per_fold_sums": folds, "per_quarter": quarters, "per_month_sums": months,
            "tercile_means": terc}


def diff_num(a, b) -> float | None:
    """Absolute difference; inf when exactly one side is undefined; None when both are."""
    if a is None and b is None:
        return None
    if a is None or b is None:
        return math.inf
    if isinstance(a, bool) or isinstance(b, bool):
        return 0.0 if a == b else math.inf
    return abs(float(a) - float(b))


def check_vs_stats(cid: str, mine: dict, rec: dict, st: dict) -> dict:
    """Max abs differences between my recomputation and the configuration's stats.json (search output)."""
    m = mine["moments"]
    d = {k: diff_num(m[k], st["moments"][k]) for k in ("mean", "sd", "skew", "kurtosis", "sharpe")}
    d["t"] = diff_num(mine["t"], st.get("t_stat"))
    d["trade_count"] = diff_num(mine["trade_count"], st["trade_count"])
    d["mean_net_per_trade"] = diff_num(mine["mean_net_per_trade"], st.get("mean_net_per_trade"))
    d["hit_rate"] = diff_num(rec["hit_rate"], st.get("hit_rate"))
    d["per_fold"] = max([diff_num(rec["per_fold_sums"][k], st["per_fold"][k]["sum"]) for k in st["per_fold"]])
    d["per_quarter"] = max([diff_num(rec["per_quarter"][k]["sum"], v["sum"]) for k, v in st["per_quarter"].items()])
    d["per_month"] = max([diff_num(rec["per_month_sums"][k]["sum"], v["sum"]) for k, v in st["per_month"].items()])
    d["terciles"] = max([diff_num(rec["tercile_means"][i], st["vol_terciles"][str(i + 1)]["mean"])
                         for i in range(3)])
    d["trades_vs_daily_mnpt"] = diff_num(rec["mean_net_per_trade_from_trades"], mine["mean_net_per_trade"])
    return d


def check_vs_select(mine: dict, sel: dict) -> dict:
    d = {k: diff_num(mine[k], sel[k]) for k in NUM_FIELDS}
    d.update({f"g5.{k}": diff_num(mine["g5"][k], sel["g5"][k]) for k in G5_FIELDS})
    d["g5.tercile_means"] = max(diff_num(a, b) for a, b in zip(mine["g5"]["tercile_means"], sel["g5"]["tercile_means"]))
    d["gates_mismatch"] = sum(1 for g in mine["gates"] if mine["gates"][g] != sel["gates"][g])
    d["g5_parts_mismatch"] = sum(1 for p in "abcd" if mine["g5"][p] != sel["g5"][p])
    return d


def max_diffs(rows: dict) -> dict:
    out = {}
    for r in rows.values():
        for k, v in r.items():
            if v is None:
                continue
            out[k] = max(out.get(k, 0.0), v)
    return out


# ---------------------------------------------------------------- the real 300 (D1)
def d1(dates, sigma, real, sel, thr) -> tuple:
    per, vs_stats, vs_sel = {}, {}, {}
    for cid, c in real.items():
        mine = L.evaluate(c["x"], c["nt"], dates, sigma, N_REGISTERED, sel["b_test"], moments, t_stat,
                          deflated_sharpe_ratio)
        rec = p62(c, dates, sigma)
        vs_stats[cid] = check_vs_stats(cid, mine, rec, c["stats"])
        vs_sel[cid] = check_vs_select(mine, sel["configs"][cid])
        firms = {f: L.firm_net(mine["mean_net_per_trade"], fee) for f, fee in L.FEES.items()}
        st = c["stats"]
        per[cid] = {**L.parse_id(cid), **mine, "p62": rec, "firm_mean_net_per_trade": firms,
                    "p_one_sided": L.one_sided_p(mine["t"]), "counts_p32": st["counts"],
                    "reported_only": st["reported_only"], "sd_daily": mine["moments"]["sd"]}
    gate_rows = [per[c]["gates"] for c in per]
    fun = L.funnel(gate_rows)
    order = sorted(per, key=lambda c: L.rank_key(c, per[c]["sharpe"], per[c]["trade_count"]))
    pv = [per[c]["p_one_sided"] for c in per]
    pbo = verdict_pbo({c: np.asarray(real[c]["x"], dtype=np.float64) for c in per})
    pbo = {k: pbo[k] for k in ("n_strategies", "n_days", "block_days", "pbo", "n_splits", "degenerate",
                                "winner_mean_oos_ticks_per_micro", "p_winner_positive_oos")}
    agree = {
        "funnel_equal": fun["alone"] == sel["funnel"]["alone"] and fun["in_order"] == sel["funnel"]["in_order"],
        "ranking_all_equal": order == sel["ranking_all"],
        "first_rank_difference": next((i for i, (a, b) in enumerate(zip(order, sel["ranking_all"])) if a != b), None),
        "bh_equal": L.bh_count(pv) == sel["bh"]["n_bh"], "holm_equal": L.holm_count(pv) == sel["bh"]["n_holm"],
        "min_p_diff": abs(min(pv) - sel["bh"]["min_p"]),
        "p_values_max_diff": max(abs(per[c]["p_one_sided"] - sel["bh"]["p_values"][c]) for c in per),
        "pbo_equal": all(pbo[k] == sel["pbo"][k] for k in pbo),
        "b_test_diff": abs(thr["b_test"] - sel["b_test"]),
        "max_diff_vs_select": max_diffs(vs_sel), "max_diff_vs_stats_json": max_diffs(vs_stats),
        "configs_with_gate_mismatch": [c for c, d in vs_sel.items() if d["gates_mismatch"]],
        "configs_with_g5_part_mismatch": [c for c, d in vs_sel.items() if d["g5_parts_mismatch"]],
    }
    multi = {"m": len(pv), "q": 0.05, "bh_rejections": L.bh_count(pv), "holm_rejections": L.holm_count(pv),
             "min_p": min(pv), "min_p_config": min(per, key=lambda c: (per[c]["p_one_sided"], c)),
             "reading": "P07: p = 1 - Phi(daily t), no t -> p = 1 counted in m; BH q 0.05; Holm 0.05",
             "reference_thresholds_select33": sel["reference_thresholds"]}
    return per, fun, order, multi, pbo, agree


def firm_summary(per: dict) -> dict:
    out = {}
    for f, fee in L.FEES.items():
        vals = [(c, r["firm_mean_net_per_trade"][f]) for c, r in per.items() if r["trade_count"] > 0]
        best = max(vals, key=lambda v: (v[1], v[0]))
        out[f] = {"fee": fee, "n_with_trades": len(vals), "n_ge_0.50": sum(1 for _, v in vals if v >= 0.5),
                  "n_gt_0": sum(1 for _, v in vals if v > 0), "max": best[1], "max_config": best[0],
                  "median": statistics.median(v for _, v in vals)}
    return out


# ---------------------------------------------------------------- null (D3)
def null_block(dates, null, thr) -> dict:
    vals, per_seed, by_cfg, stats_diff = [], {}, {}, 0.0
    b5 = IO.b5_null_best()
    for s, seed in null.items():
        srs = {}
        for cid, c in seed.items():
            m = moments(c["x"])
            stats_diff = max(stats_diff, abs(m["sharpe"] - c["stats"]["moments"]["sharpe"]))
            srs[cid] = {"sharpe": m["sharpe"], "constant": m["sd"] == 0, "trade_count": int(sum(c["nt"]))}
            vals.append(m["sharpe"])
            by_cfg.setdefault(cid, []).append(m["sharpe"])
        traded = {k: v for k, v in srs.items() if not v["constant"]}
        best = min(traded, key=lambda k: L.rank_key(k, traded[k]["sharpe"], traded[k]["trade_count"])) if traded else None
        per_seed[s] = {"max_sharpe": traded[best]["sharpe"] if best else None, "best": best,
                       "n_constant": sum(1 for v in srs.values() if v["constant"]),
                       "b5_best": b5[s][0], "b5_best_sr": b5[s][1],
                       "agree_b5": best is not None and best.endswith(b5[s][0]) and round(traded[best]["sharpe"], 4) == b5[s][1]}
    nonconst = [v for s in null.values() for c in s.values() for v in [moments(c["x"])] if v["sd"] > 0]
    centred = [v - statistics.fmean(by_cfg[c]) for c in by_cfg for v in by_cfg[c]]
    maxima = [v["max_sharpe"] for v in per_seed.values() if v["max_sharpe"] is not None]
    m0, s0 = statistics.fmean(vals), statistics.pstdev(vals)
    nc_vals = [v["sharpe"] for v in nonconst]
    m1, s1 = statistics.fmean(nc_vals), statistics.pstdev(nc_vals)
    rng = np.random.default_rng(20261028)
    arr = np.asarray(vals)
    boot300 = float(np.mean([arr[rng.integers(0, len(arr), 300)].max() for _ in range(10000)]))
    boot20 = float(np.mean([arr[rng.integers(0, len(arr), 20)].max() for _ in range(10000)]))
    sig_c = statistics.pstdev(centred)
    sig_c_df = sig_c * math.sqrt(20 / 19)
    mu_c = np.asarray([statistics.fmean(by_cfg[c]) for c in by_cfg])
    sims = mu_c[None, :] + sig_c_df * rng.standard_normal((100000, len(mu_c)))
    mc20 = float(sims.max(axis=1).mean())
    maxima_se = statistics.stdev(maxima) / math.sqrt(len(maxima))
    dev = np.asarray([[v - statistics.fmean(by_cfg[c]) for v in by_cfg[c]] for c in by_cfg])  # configs x seeds
    with np.errstate(invalid="ignore", divide="ignore"):
        cm = np.corrcoef(dev)
    off = cm[~np.eye(len(cm), dtype=bool)]
    dev_corr = float(np.nanmean(off))
    return {
        "n_series": len(vals), "n_constant": len(vals) - len(nonconst), "n_nonconstant": len(nonconst),
        "n_nonconstant_in_configs_with_2plus": sum(
            k for k in (sum(1 for s in null.values() if moments(s[c]["x"])["sd"] > 0) for c in by_cfg) if k >= 2),
        "sharpe_all": vals, "per_seed": per_seed, "seed_maxima": maxima,
        "summary_all": {"mean": m0, "sd": s0, **L.quantiles(vals)},
        "summary_nonconstant": {"mean": m1, "sd": s1, **L.quantiles(nc_vals)},
        "centred_sd_all": statistics.pstdev(centred), "maxima_summary": {"mean": statistics.fmean(maxima),
                                                                          **L.quantiles(maxima)},
        "stats_json_max_sharpe_diff": stats_diff,
        "b5_agreement_seeds": sum(1 for v in per_seed.values() if v["agree_b5"]),
        "expected_max_report": {
            "method": ("REPORT, not a gate. The null's per-configuration spread is P4.2's statistic: the SD of the "
                       "400 null daily Sharpes, each centred on its configuration's mean over the 20 seeds "
                       "(sigma_c, population; df-corrected x sqrt(20/19)). Zero-edge null for the 300: every "
                       "configuration's true daily Sharpe 0, independent sampling errors with SD sigma_c; "
                       "E[max over n] = expected_max_sharpe(n, sigma_c^2) (Bailey and Lopez de Prado 2014 eq. 3, "
                       "the program's function; the same construction as SR0, which uses 1/sqrt(T_disc - 1) in "
                       "place of sigma_c). Check of the construction at n = 20 in B5's own setting: "
                       "E[max_c (mu_c + sigma_c,df eps_c)] by Monte Carlo (100,000 draws, seed 20261028; mu_c = "
                       "each null configuration's mean over the seeds) against the mean of the 20 observed per-seed "
                       "maxima. Caveats: independence overstates the max for correlated configurations; true "
                       "Sharpes of a real null search are below 0 by costs (the B5 null mean is negative), which "
                       "lowers the max; the null covers S5 x {F15, T30} only."),
            "sigma_c": sig_c, "sigma_c_df": sig_c_df,
            "E_max_300_zero_edge": expected_max_sharpe(300, sig_c ** 2),
            "E_max_300_zero_edge_df": expected_max_sharpe(300, sig_c_df ** 2),
            "E_max_838_zero_edge_df": expected_max_sharpe(838, sig_c_df ** 2),
            "check_n20_monte_carlo": mc20, "check_n20_observed_mean_of_seed_maxima": statistics.fmean(maxima),
            "check_n20_observed_se": maxima_se,
            "null_mean_pairwise_corr_of_sharpe_errors": dev_corr,
            "null_corr_pairs_defined": int(np.sum(~np.isnan(off))),
            "alternatives_not_used": {
                "reason": ("pooling the 400 values as iid draws (mean m, SD s) mixes the configurations' different "
                           "null means into the spread; its n = 20 prediction misses the observed per-seed maxima "
                           "by far, so it is not used"),
                "m_all": m0, "s_all": s0,
                "E_max_20_pooled_formula": m0 + expected_max_sharpe(20, s0 ** 2),
                "E_max_20_pooled_empirical": boot20,
                "E_max_300_pooled_formula": m0 + expected_max_sharpe(300, s0 ** 2),
                "E_max_300_pooled_empirical": boot300}},
        "source": "derived/e33/proofs/seed1..seed20/search/<cid>/daily.parquet (B5_proofs.md lines 3, 38-41)",
    }


def real_mean_corr(per: dict, real: dict) -> dict:
    """Mean pairwise Pearson correlation of the non-constant real OOF daily series (descriptive)."""
    ids = [c for c in per if not per[c]["constant"]]
    cm = np.corrcoef(np.asarray([real[c]["x"] for c in ids]))
    off = cm[~np.eye(len(ids), dtype=bool)]
    return {"n_series": len(ids), "mean_pairwise_corr": float(off.mean()),
            "share_pairs_above_0.70": float(np.mean(off > 0.70))}


def real_distribution(per: dict, null: dict, thr: dict) -> dict:
    allv = [r["sharpe"] for r in per.values()]
    nc = [r["sharpe"] for r in per.values() if not r["constant"]]
    q95 = null["summary_all"]["q0.95"]
    nmax = max(null["sharpe_all"])
    return {"n": len(allv), "n_constant": len(allv) - len(nc), "n_nonconstant": len(nc),
            "summary_all": {"mean": statistics.fmean(allv), "sd": statistics.pstdev(allv), **L.quantiles(allv)},
            "summary_nonconstant": {"mean": statistics.fmean(nc), "sd": statistics.pstdev(nc), **L.quantiles(nc)},
            "n_above": {"SR0": sum(v >= thr["SR0"] for v in allv), "G3": sum(v >= thr["G3"] for v in allv),
                        "binding": sum(v >= thr["binding"] for v in allv), "null_q95_all": sum(v > q95 for v in allv),
                        "null_max_of_400": sum(v > nmax for v in allv), "zero": sum(v > 0 for v in allv)},
            "null_q95_all": q95, "null_max_of_400": nmax}


# ---------------------------------------------------------------- P10 (v): minimum detectable edge
def mde(per: dict, real: dict, thr: dict) -> dict:
    t = thr["T_disc"]
    bars = {"G3": thr["G3"], "binding": thr["binding"]}
    s80 = {k: L.s80_at_bar(v, t) for k, v in bars.items()}
    s80x = {k: L.s80_exact(v, t) for k, v in bars.items()}
    out = {"T_disc": t, "bars": bars, "s80_bar_convention": s80, "s80_exact": s80x, "horizons": {}}
    for lab in ("F05", "F15", "F30", "F60", "T15", "T30"):
        h = L.LABEL_KEY[lab][0]
        cids = [c for c in per if per[c]["label"] == lab]
        nets = np.concatenate([real[c]["trade_net"] for c in cids])
        sig_meas = float(np.std(nets)) if len(nets) else None
        traded = [c for c in cids if per[c]["trade_count"] > 0 and per[c]["sd_daily"] > 0]
        g1 = [c for c in traded if per[c]["gates"]["G1"]]
        e_cfg = {c: L.mde_measured(s80["binding"], per[c]["sd_daily"], per[c]["trades_per_date"]) for c in traded}
        rows = []
        for n in (1, 2, 4, 8, 12):
            if n > L.DECISION_MINUTES[h] // h:
                continue
            rows.append({"n_per_date": n,
                         "mu_at_binding_P72": L.mde_random_walk(thr["binding"], h, n),
                         "e80_G3": L.mde_random_walk(s80["G3"], h, n),
                         "e80_binding": L.mde_random_walk(s80["binding"], h, n),
                         "e80_binding_measured_sigma": (s80["binding"] * sig_meas / math.sqrt(n)) if sig_meas else None})
        tpd = [per[c]["trades_per_date"] for c in traded]
        out["horizons"][lab] = {
            "h": h, "sigma_h_standard": L.SIGMA_1M * math.sqrt(h), "sigma_trade_measured": sig_meas,
            "n_trades_pooled": int(len(nets)), "n_configs": len(cids), "n_traded": len(traded),
            "trades_per_date_traded_median": statistics.median(tpd) if tpd else None,
            "trades_per_date_traded_max": max(tpd) if tpd else None, "standard_rows": rows,
            "measured_per_config_e80_binding": {
                "all_traded": L.quantiles([v for v in e_cfg.values()], (0.0, 0.25, 0.5)),
                "g1_passers_n": len(g1),
                "g1_passers": L.quantiles([e_cfg[c] for c in g1], (0.0, 0.25, 0.5)) if g1 else {}},
            "g2_floor": L.G2_MIN_NET}
    out["formula"] = ("e80 = s80 x sigma_h / sqrt(n): P7.2 'Per trade (random-walk sigma_h; independent trades every "
                      "date): 0.71 ticks net at 5-minute holds and 4 trades a date ...' (p7_final 'mu at selection "
                      "threshold' = threshold x sigma_h / sqrt(n), sigma_h = 3.15 sqrt(h)), with the threshold "
                      "replaced by s80 = bar + z_0.80 se(bar), se = sqrt((1 + bar^2/2)/(T_disc - 1)) (p7_final's s80 "
                      "convention, its test line '80% power needs a true daily Sharpe of 0.1936'), T_disc = 796")
    return out


# ---------------------------------------------------------------- P10 (vi): null statement per family
QUOTES = [
    ("1", "tested on the pre-registered confirmation windows (trade dates S_X to 2024-02-29 for each exposure X"),
    ("1", "Members and their definitions: {reports/stage_e1_confirmation_list_K#.md, sha256}"),
    ("3", "Null for a cluster: every member (Tier A and Tier B, D5) has UCB95 < eps_X and achieved null power"),
    ("3", "Rules found by the Stage E ML route are pre-registered and tested as ordinary members"),
    ("6", "signals needing order-book data; constructions not on the frozen lists"),
    ("1", "The statement is made per cluster, never for"),
]
FAMILY_OF = {"S1": "F1 crush-residual reversion (+C)", "S2": "F2 cross-asset propagation (+C)",
             "S3": "F3 ZM order flow and book state (+C)", "S4": "F4 ZM own price path (+C)",
             "S5": "pooled F1-F4 (+C)"}


def families(per: dict) -> dict:
    # blockquote lines (section 1) carry a "> " prefix: strip it before the whitespace-normalised match
    lines = [ln[2:] if ln.startswith("> ") else ln for ln in IO.NULL_CRITERIA.read_text().splitlines()]
    text = " ".join(" ".join(lines).split())
    found = {q: (" ".join(q.split()) in text) for _, q in QUOTES}
    k6 = IO.k6_zm_members()
    out = {"criteria_file": str(IO.NULL_CRITERIA.relative_to(IO.REPO)), "criteria_sha256": IO.sha256(IO.NULL_CRITERIA),
           "quotes": [{"section": s, "text": q, "found_verbatim": found[q]} for s, q in QUOTES], "k6": k6,
           "families": {}}
    for st, name in FAMILY_OF.items():
        cids = [c for c in per if per[c]["set"] == st]
        nonconst = [c for c in cids if not per[c]["constant"]]   # reading Q9: best among series that traded
        best = min(nonconst, key=lambda c: L.rank_key(c, per[c]["sharpe"], per[c]["trade_count"]))
        out["families"][st] = {
            "family": name, "n_configs": len(cids), "n_traded": sum(1 for c in cids if per[c]["trade_count"] > 0),
            "n_G1": sum(1 for c in cids if per[c]["gates"]["G1"]), "best": best, "best_sharpe": per[best]["sharpe"],
            "best_trade_count": per[best]["trade_count"],
            "n_sharpe_gt_0": sum(1 for c in cids if per[c]["sharpe"] > 0),
            "statement": "no statement",
            "reasons": ["not members of a hashed confirmation list (section 1; section 6 'constructions not on the "
                        "frozen lists'); ZM's cluster K6 list holds 27 members, none an E.33 configuration",
                        "the 796 OOF dates are discovery (search) dates, not a pre-registered confirmation read; "
                        "an ML-route rule becomes a member only after pre-registration and a test (section 3, U6)",
                        "every set includes C.3 (ZM spread) and C.4 (ZM touch depth) from the MBO book and trades at "
                        "book prices: 'signals needing order-book data' are out of scope (section 6)",
                        "no UCB95 or SE_boot (section 3) is computed for these series: the comparable day-block bootstrap "
                        "is a P6.5 item, run only after a hashed test list; with it, reasons 1-3 would still stand"]}
    return out


# ---------------------------------------------------------------- main
def _jsonable(o):
    if isinstance(o, float) and not math.isfinite(o):
        return None if math.isnan(o) else ("inf" if o > 0 else "-inf")
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return _jsonable(o.item())
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _write(path: Path, obj) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(_jsonable(obj), indent=1, sort_keys=True))
    tmp.replace(path)
    return IO.sha256(path)


def main() -> int:
    t0 = time.time()
    hashes = IO.check_hashes()
    ids = L.all_ids()
    dates, real = IO.load_real(ids)
    sigma = IO.load_sigma(dates)
    sel = IO.load_selection_fields()
    if sel["n_trials"] != N_REGISTERED or sel["t_disc"] != len(dates) or set(sel["configs"]) != set(ids):
        raise SystemExit("REFUSE: selection JSON does not match N 838, T 796 and the 300 ids")
    thr = thresholds(N_REGISTERED)
    per, fun, order, multi, pbo, agree = d1(dates, sigma, real, sel, thr)
    null = load_null_safe(dates, thr)
    dist = real_distribution(per, null, thr) | {"correlation": real_mean_corr(per, real)}
    top10 = order[:10]
    top = {c: {k: per[c][k] for k in ("set", "label", "grid", "family", "h", "moments", "t", "trade_count",
                                       "trades_per_date", "mean_net_per_trade", "share_dates_with_trade",
                                       "dates_with_trade", "dsr", "se", "sr_lower", "gates", "g5",
                                       "firm_mean_net_per_trade", "reported_only", "counts_p32", "p_one_sided")}
               | {"p62": per[c]["p62"], "rank": i + 1} for i, c in enumerate(top10)}
    core_keys = ("set", "label", "grid", "family", "h", "sharpe", "t", "constant", "trade_count", "trades_per_date",
                 "dates_with_trade", "share_dates_with_trade", "mean_net_per_trade", "total_net", "dsr", "se",
                 "sr_lower", "gates", "firm_mean_net_per_trade", "p_one_sided", "counts_p32")
    core = {c: {k: per[c][k] for k in core_keys} | {"moments": per[c]["moments"],
            "g5": {k: v for k, v in per[c]["g5"].items()}, "hit_rate": per[c]["p62"]["hit_rate"]} for c in ids}
    full_sha = _write(IO.STATS_C / "per_config_full.json", {"dates": dates, "configs": per})
    out = {
        "written_by": "reports/stage_e33c_briefs/work/stats/run_dstats.py", "branch": "N (Tier A empty)",
        "inputs": {**hashes, "search_root": str(IO.SEARCH), "feature_sha": IO.FEAT_SHA, "label_sha": IO.LABEL_SHA,
                   "n_dates": len(dates), "first_date": dates[0], "last_date": dates[-1]},
        "thresholds": thr,
        "selection_as_written": {k: sel[k] for k in ("n_trials", "b_test", "funnel", "tier_a", "tier_b",
                                                     "tier_b_reading", "best_config", "best_sharpe", "pbo")}
                                | {"bh": {k: v for k, v in sel["bh"].items() if k != "p_values"}},
        "agreement_with_select33": agree, "funnel": fun, "ranking_top10": top10, "multiple_comparisons": multi,
        "pbo": pbo | {"null_band_M5a_e": [0.13, 0.83], "set": "P08: every configuration with a series, constants "
                                                               "included (300; 0 failed)"},
        "firm_summary": firm_summary(per),
        "g2_passers": {c: {"trade_count": per[c]["trade_count"], "dates_with_trade": per[c]["dates_with_trade"],
                           "firm_mean_net_per_trade": per[c]["firm_mean_net_per_trade"], "sharpe": per[c]["sharpe"]}
                       for c in ids if per[c]["gates"]["G2"]},
        "top10": top, "configs": core, "real_distribution": dist, "null": null, "mde": mde(per, real, thr),
        "families": families(per), "per_config_full": {"path": str(IO.STATS_C / "per_config_full.json"),
                                                        "sha256": full_sha},
    }
    sha = _write(IO.WORK / "D_stats.json", out)
    fig = {"real_sharpe": [per[c]["sharpe"] for c in ids], "real_constant": [per[c]["constant"] for c in ids],
           "null_sharpe": null["sharpe_all"], "null_seed_maxima": null["seed_maxima"],
           "null_n_constant": null["n_constant"], "lines": {k: thr[k] for k in ("SR0", "G3", "binding")},
           "e_max_300_report": null["expected_max_report"]["E_max_300_zero_edge_df"]}
    _write(HERE / "fig" / "fig_data.json", fig)
    print(f"D_stats.json sha256 {sha[:16]}; per_config_full sha256 {full_sha[:16]}; {time.time() - t0:.1f} s")
    print(f"thresholds SR0 {thr['SR0']:.4f} G3 {thr['G3']:.4f} binding {thr['binding']:.4f} b_test {thr['b_test']:.6f}")
    print(f"funnel alone {fun['alone']} in order {fun['in_order']}")
    print("agreement:", {k: v for k, v in agree.items() if k not in ("max_diff_vs_select", "max_diff_vs_stats_json")})
    print("max diff vs select33:", {k: f"{v:.2e}" for k, v in agree["max_diff_vs_select"].items()})
    print("max diff vs stats.json:", {k: f"{v:.2e}" for k, v in agree["max_diff_vs_stats_json"].items()})
    print(f"BH {multi['bh_rejections']} Holm {multi['holm_rejections']} min p {multi['min_p']:.4f}; PBO {pbo['pbo']:.4f}")
    print(f"null: {null['n_series']} series, {null['n_constant']} constant; centred SD {null['centred_sd_all']:.4f}; "
          f"B5 agree {null['b5_agreement_seeds']}/20; stats diff {null['stats_json_max_sharpe_diff']:.1e}")
    print("E[max] report:", {k: round(v, 4) for k, v in null["expected_max_report"].items() if isinstance(v, float)})
    print("real:", dist["n_above"], f"max {dist['summary_all']['q1']:.4f}")
    return 0


def load_null_safe(dates, thr) -> dict:
    return null_block(dates, IO.load_null(dates), thr)


if __name__ == "__main__":
    sys.exit(main())
