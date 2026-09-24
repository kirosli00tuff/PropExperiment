#!/usr/bin/env python
"""Stage D.1f (run) independent verification scratch: NumberVerifier-FableXHigh.

Read-only on every input. Re-computes the verdict-bearing numbers of the D.1f run from the
runner's output JSONs and the frozen rules (reports/stage_d1f_confirmation_list.md 3.1-3.5,
docs/NULL_CRITERIA.md 3, 4.1, 6, 7) and writes one results JSON to the session scratchpad.
It never imports strategy.research._d1f_*.

Run: OPENBLAS_NUM_THREADS=1 nice -n 10 uv run python reports/_d1f_run_verify_scratch.py
"""
from __future__ import annotations

import os

os.nice(10)

import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from itertools import combinations  # noqa: E402

import numpy as np  # noqa: E402

ROOT = "/home/kiros-li/Documents/GitHub/PropExperiment"
sys.path.insert(0, ROOT)

from funnel.multiple_comparisons import (  # noqa: E402
    deflated_sharpe_ratio,
    expected_max_sharpe,
    harvey_liu_zhu_verdict,
    probability_of_backtest_overfitting,
)
from funnel.null_generator import stationary_bootstrap_indices  # noqa: E402
from strategy.research._d1b_accounting import _moments as runner_moments  # noqa: E402

EPS_DAY = 34.0
B_RESAMPLES = 10_000
SEED_RUNNER = 20260921
SEED_INDEPENDENT = 20260923
MEAN_BLOCK = 5.0
ALPHA_HOLM = 0.05
Q_BH = 0.10
N_PBO_BLOCKS = 8
N_TRIALS_AFTER = 58
TICK_USD = 1.25
Z_ONE_SIDED_95 = 1.645
POWER_TARGET = 0.80
INACTIVITY_COUNT = 30
TOL_EXACT = 1e-9

INPUTS = {
    "step5": f"{ROOT}/reports/stage_d1f_step5_start_rule.json",
    "step7": f"{ROOT}/reports/stage_d1f_step7_list_run.json",
    "tier_a": f"{ROOT}/reports/stage_d1f_tier_a.json",
    "tier_b": f"{ROOT}/reports/stage_d1f_tier_b.json",
    "decisions": f"{ROOT}/reports/stage_d1f_decisions.json",
    "list": f"{ROOT}/reports/stage_d1f_confirmation_list.md",
    "criteria": f"{ROOT}/docs/NULL_CRITERIA.md",
}
BINDING = {
    "C1": "A-H4 rth leg",
    "C2": "G3.RTH.5",
    "C3": "F1_1_h1_RTH",
    "C4": "F2_4_15min_vol_tercile_top",
    "C5": "E-H1 scheduled macro drift",
    "C6": "C-H4 passive-fill reversal",
    "C7": "H6 prior-close location follow-through",
}
OUT_DIR = os.environ.get(
    "VERIFY_OUT_DIR",
    "/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/"
    "c39a9cf3-de81-44e4-96f7-c074621e99f7/scratchpad",
)


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ----------------------------------------------------------------------------- bootstrap
def exact_bootstrap(d: np.ndarray) -> dict:
    """List 3.1 verbatim: fresh default_rng(20260921), B = 10,000, the funnel helper."""
    n = len(d)
    theta = float(d.mean())
    rng = np.random.default_rng(SEED_RUNNER)
    means = np.empty(B_RESAMPLES)
    for i in range(B_RESAMPLES):
        means[i] = d[stationary_bootstrap_indices(rng, n, n, MEAN_BLOCK)].mean()
    ucb = float(np.quantile(means, 0.95))
    se = float(np.std(means))
    p = (1 + int(np.sum(means - theta >= theta))) / (B_RESAMPLES + 1)
    power = norm_cdf(EPS_DAY / se - Z_ONE_SIDED_95) if se > 0 else 0.0
    return {"theta_hat": theta, "ucb95": ucb, "se_boot": se, "p_one_sided": p,
            "power": power, "n": n}


def independent_bootstrap(d: np.ndarray, seed: int, n_resamples: int = B_RESAMPLES) -> dict:
    """Own stationary bootstrap: geometric block lengths (mean 5, support 1..), uniform
    block starts, circular wrap-around, blocks concatenated and truncated to n."""
    n = len(d)
    rng = np.random.default_rng(seed)
    dd = np.concatenate([d, d])
    means = np.empty(n_resamples)
    out = np.empty(n)
    p_renew = 1.0 / MEAN_BLOCK
    for i in range(n_resamples):
        pos = 0
        while pos < n:
            start = int(rng.integers(0, n))
            length = min(int(rng.geometric(p_renew)), n - pos)
            out[pos:pos + length] = dd[start:start + length]
            pos += length
        means[i] = out.mean()
    return {"ucb95": float(np.quantile(means, 0.95)), "se_boot": float(np.std(means)),
            "mean_of_means": float(means.mean())}


# ----------------------------------------------------------------------------- accounting
def my_moments(xs: list[float]) -> dict:
    """Re-implementation of strategy.research._d1b_accounting._moments (population sd)."""
    arr = np.asarray(xs, dtype=float)
    n = len(arr)
    mean = float(arr.mean())
    sd = float(np.sqrt(np.mean((arr - mean) ** 2)))
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    z = (arr - mean) / sd
    return {"n": n, "mean": mean, "sd": sd, "skew": float(np.mean(z ** 3)),
            "kurtosis": float(np.mean(z ** 4)), "sharpe": mean / sd}


def my_expected_max_sharpe(n_trials: int, variance: float) -> float:
    nd = statistics.NormalDist()
    g = 0.5772156649015329
    term = (1 - g) * nd.inv_cdf(1 - 1.0 / n_trials) + g * nd.inv_cdf(1 - 1.0 / (n_trials * math.e))
    return math.sqrt(variance) * term


def my_dsr(sharpe: float, n: int, n_trials: int, variance: float, skew: float, kurt: float) -> dict:
    bench = my_expected_max_sharpe(n_trials, variance)
    den = 1.0 - skew * sharpe + 0.25 * (kurt - 1.0) * sharpe ** 2
    z = (sharpe - bench) * math.sqrt(n - 1) / math.sqrt(den)
    return {"dsr": norm_cdf(z), "z": z, "benchmark": bench}


def my_pbo(matrix: list[list[float]]) -> dict:
    s_count = len(matrix)
    blocks = range(N_PBO_BLOCKS)
    logits, oos_winner = [], []
    for train in combinations(blocks, N_PBO_BLOCKS // 2):
        test = [b for b in blocks if b not in set(train)]
        ins = [sum(row[b] for b in train) for row in matrix]
        oos = [sum(row[b] for b in test) for row in matrix]
        best = max(range(s_count), key=lambda s: ins[s])
        worse = sum(1 for s in range(s_count) if oos[s] < oos[best])
        rank = min(max((worse + 0.5) / s_count, 1e-9), 1 - 1e-9)
        logits.append(math.log(rank / (1 - rank)))
        oos_winner.append(oos[best])
    return {"pbo": sum(1 for lg in logits if lg <= 0) / len(logits), "n_splits": len(logits),
            "winner_mean_oos": float(np.mean(oos_winner)),
            "p_winner_positive_oos": float(np.mean([x > 0 for x in oos_winner]))}


def blocks_of(series: list[float]) -> list[float]:
    width = len(series) // N_PBO_BLOCKS
    return [float(sum(series[b * width:(b + 1) * width])) for b in range(N_PBO_BLOCKS)]


def holm(pvals: dict[str, float], alpha: float) -> dict:
    order = sorted(pvals, key=lambda k: (pvals[k], k))
    m = len(order)
    out, still = {}, True
    for rank, k in enumerate(order, start=1):
        thr = alpha / (m - rank + 1)
        reject = still and pvals[k] <= thr
        if not reject:
            still = False
        out[k] = {"rank": rank, "threshold": thr, "reject": reject}
    return out


def bh(pvals: dict[str, float], q: float) -> dict:
    order = sorted(pvals, key=lambda k: (pvals[k], k))
    m = len(order)
    cutoff = 0
    for rank, k in enumerate(order, start=1):
        if pvals[k] <= q * rank / m:
            cutoff = rank
    return {k: {"rank": r, "threshold": q * r / m, "reject": r <= cutoff}
            for r, k in enumerate(order, start=1)}


# ----------------------------------------------------------------------------- start rule
def start_rule_from_logged(sr: dict) -> dict:
    ref = sr["reference_monthly_medians"]
    v_ref = statistics.median(ref.values())
    ext = sr["extension_monthly_medians"]
    months = sorted(ext)
    first = sr["extension_first_trade_dates"]
    out = {"v_ref": v_ref, "n_reference_months": len(ref), "by_fraction": {}}
    for frac in (0.25, 0.15, 0.40):
        thr = frac * v_ref
        m_star = None
        for i, m in enumerate(months):
            if all(ext[x] >= thr for x in months[i:]):
                m_star = m
                break
        out["by_fraction"][str(frac)] = {"threshold": thr, "m_star": m_star,
                                         "s": first[m_star] if m_star else None}
    return out


def monthly_medians_from_bars(frame, first_month: str, last_month: str) -> tuple[dict, dict]:
    """RTH = America/Chicago clock minute of the bar's ts_event (its open) in 08:30..14:59;
    month = the trade_date's month; median of volume over the RTH bars present."""
    import pandas as pd
    ts = pd.to_datetime(frame["ts_event"].to_numpy(), utc=True).tz_convert("America/Chicago")
    minute = ts.hour * 60 + ts.minute
    rth = (minute >= 8 * 60 + 30) & (minute <= 14 * 60 + 59)
    month = frame["trade_date"].astype(str).str.slice(0, 7).to_numpy()
    vol = frame["volume"].to_numpy()
    medians, firsts = {}, {}
    for m in sorted(set(month)):
        if not (first_month <= m <= last_month):
            continue
        sel = (month == m) & rth
        if sel.any():
            medians[m] = float(np.median(vol[sel]))
        dates = frame["trade_date"].to_numpy()[month == m]
        firsts[m] = str(min(dates))
    return medians, firsts


# ----------------------------------------------------------------------------- main
def main() -> None:
    log("hashing inputs")
    hashes = {k: sha256(p) for k, p in INPUTS.items()}
    step5 = json.load(open(INPUTS["step5"]))
    step7 = json.load(open(INPUTS["step7"]))
    tier_a = json.load(open(INPUTS["tier_a"]))
    tier_b = json.load(open(INPUTS["tier_b"]))
    decisions = json.load(open(INPUTS["decisions"]))
    rows = {**tier_a["members"], **tier_b["members"]}
    members = {m["id"]: m for m in step7["members"]}
    window_dates = list(step7["window_dates"])
    statistic_dates = list(step7["statistic_dates"])
    results: dict = {"inputs_sha256": hashes, "n_members": len(members),
                     "n_tier_a": len(tier_a["members"]), "n_tier_b": len(tier_b["members"]),
                     "n_window_dates": len(window_dates), "n_statistic_dates": len(statistic_dates)}

    # -- series consistency between step 7 and the tier files
    series_mismatch = []
    for mid, m in members.items():
        r = rows[mid]
        a = np.asarray(m["daily"], dtype=float)
        b = np.asarray(r["daily_ticks_per_micro"], dtype=float)
        dates = window_dates if m["dates_ref"] == "window" else statistic_dates
        if len(a) != len(b) or np.max(np.abs(a - b)) > 0 or list(r["dates"]) != dates \
                or list(m["daily_activity"]) != list(r["daily_activity"]):
            series_mismatch.append(mid)
    results["series_step7_vs_tier_mismatch"] = series_mismatch

    # -- exact bootstrap, all 101 members
    log("exact bootstrap over 101 members")
    exact, dev = {}, {"theta_hat": 0.0, "ucb95": 0.0, "se_boot": 0.0, "p_one_sided": 0.0,
                      "power": 0.0}
    dev_member = {k: None for k in dev}
    for mid, m in members.items():
        d = np.asarray(m["daily"], dtype=float)
        e = exact_bootstrap(d)
        r = rows[mid]
        runner = {"theta_hat": r["theta_hat"], "ucb95": r["ucb95"], "se_boot": r["se_boot"],
                  "p_one_sided": r["p_one_sided"], "power": r["null"]["achieved_power"]}
        e["runner"] = runner
        e["abs_diff"] = {k: abs(e[k] - runner[k]) for k in dev}
        for k in dev:
            if e["abs_diff"][k] > dev[k]:
                dev[k], dev_member[k] = e["abs_diff"][k], mid
        e["n_activity"] = int(sum(m["daily_activity"]))
        e["runner_n_activity"] = r["n_activity"]
        e["activity_per_own_date"] = e["n_activity"] / e["n"]
        e["runner_activity_per_day"] = r["activity_per_day"]
        e["tier"], e["kind"], e["class"] = m["tier"], m["kind"], m["class"]
        e["composite"] = m["composite"]
        e["null_meets"] = bool(e["ucb95"] < EPS_DAY and e["power"] >= POWER_TARGET
                               and e["n_activity"] > 0 and e["se_boot"] > 0)
        e["runner_null_meets"] = r["null"]["meets"]
        e["runner_status"] = r["status"]
        e["runner_labels"] = list(r["labels"])
        e["per_trade_ucb95"] = e["ucb95"] / e["activity_per_own_date"] if e["n_activity"] else None
        e["runner_per_trade_ucb95"] = r["per_trade"]["ucb95"]
        exact[mid] = e
    results["exact"] = exact
    results["exact_max_abs_dev"] = dev
    results["exact_max_abs_dev_member"] = dev_member
    log(f"exact max abs dev: {dev}")

    # -- independent bootstrap for the binding members and the near-threshold members
    near = [mid for mid, e in exact.items()
            if 30.6 <= e["ucb95"] <= 37.4 or abs(e["se_boot"] - EPS_DAY / 2.4865) <= 0.1 * EPS_DAY / 2.4865]
    targets = list(dict.fromkeys([*BINDING.values(), *near]))
    results["near_threshold_members"] = near
    log(f"independent bootstrap for {targets}")
    indep = {}
    for mid in targets:
        d = np.asarray(members[mid]["daily"], dtype=float)
        ib = independent_bootstrap(d, SEED_INDEPENDENT)
        se_ref = exact[mid]["se_boot"]
        d_ucb = abs(ib["ucb95"] - exact[mid]["ucb95"])
        d_se = abs(ib["se_boot"] - exact[mid]["se_boot"])
        sd_ucb = 0.0299 * se_ref  # MC sd of the difference of two independent 95th percentiles
        sd_se = 0.0100 * se_ref  # MC sd of the difference of two independent bootstrap SEs
        ib.update({"exact_ucb95": exact[mid]["ucb95"], "exact_se_boot": se_ref,
                   "diff_ucb95": d_ucb, "diff_se": d_se, "tol_ucb95": 4 * sd_ucb,
                   "tol_se": 4 * sd_se, "z_ucb95": d_ucb / sd_ucb, "z_se": d_se / sd_se,
                   "within": bool(d_ucb <= 4 * sd_ucb and d_se <= 4 * sd_se),
                   "power_from_indep_se": norm_cdf(EPS_DAY / ib["se_boot"] - Z_ONE_SIDED_95)})
        indep[mid] = ib
    results["independent"] = indep

    # -- Holm over the 58 Tier A one-sided p-values (my p-values), BH over Tier B
    log("Holm and BH")
    p_a = {mid: exact[mid]["p_one_sided"] for mid in tier_a["members"]}
    my_holm = holm(p_a, ALPHA_HOLM)
    holm_cmp = {}
    for mid in tier_a["members"]:
        rh = rows[mid]["holm"]
        holm_cmp[mid] = {"my": my_holm[mid], "runner": rh,
                         "rank_equal": my_holm[mid]["rank"] == rh["rank"],
                         "thr_diff": abs(my_holm[mid]["threshold"] - rh["threshold"]),
                         "reject_equal": my_holm[mid]["reject"] == rh["reject"]}
    results["holm"] = {"per_member": holm_cmp,
                       "my_rejected": [k for k, v in my_holm.items() if v["reject"]],
                       "runner_rejected": decisions["family"]["holm"]["rejected"],
                       "runner_alpha": decisions["family"]["holm"]["alpha"],
                       "runner_m": decisions["family"]["holm"]["m"],
                       "min_p": min(p_a.values()), "min_p_member": min(p_a, key=p_a.get),
                       "first_threshold": ALPHA_HOLM / len(p_a),
                       "ordering": sorted(p_a, key=lambda k: (p_a[k], k))}
    p_b = {mid: exact[mid]["p_one_sided"] for mid in tier_b["members"]}
    my_bh = bh(p_b, Q_BH)
    bh_cmp = {}
    for mid in tier_b["members"]:
        rb = rows[mid]["anomaly"]["bh"]
        bh_cmp[mid] = {"my": my_bh[mid], "runner": rb,
                       "rank_equal": my_bh[mid]["rank"] == rb["rank"],
                       "thr_diff": abs(my_bh[mid]["threshold"] - rb["threshold"]),
                       "reject_equal": my_bh[mid]["reject"] == rb["reject"]}
    results["bh_tier_b"] = {"per_member": bh_cmp,
                            "my_rejected": [k for k, v in my_bh.items() if v["reject"]]}

    # -- moments, DSR at N = 58, t, PBO over the 58 Tier A series
    log("accounting (moments, DSR, t, PBO)")
    acc = {}
    for mid in tier_a["members"]:
        d = list(map(float, members[mid]["daily"]))
        mine = my_moments(d)
        theirs = runner_moments(d)
        stored = rows[mid]["accounting"]["moments"]
        acc[mid] = {"my_moments": mine, "helper_moments": theirs, "stored_moments": stored,
                    "moments_max_abs_dev_vs_stored": max(abs(mine[k] - stored[k])
                                                         for k in ("mean", "sd", "skew", "kurtosis", "sharpe"))}
    sharpes = [acc[mid]["my_moments"]["sharpe"] for mid in tier_a["members"]]
    var58 = statistics.pvariance(sharpes)
    bench_my = my_expected_max_sharpe(N_TRIALS_AFTER, var58)
    bench_helper = expected_max_sharpe(N_TRIALS_AFTER, var58)
    for mid in tier_a["members"]:
        mm = acc[mid]["my_moments"]
        dsr_mine = my_dsr(mm["sharpe"], mm["n"], N_TRIALS_AFTER, var58, mm["skew"], mm["kurtosis"])
        dsr_helper = deflated_sharpe_ratio(mm["sharpe"], mm["n"], N_TRIALS_AFTER, var58,
                                           mm["skew"], mm["kurtosis"])
        t_mine = mm["mean"] / (mm["sd"] / math.sqrt(mm["n"]))
        t_helper = harvey_liu_zhu_verdict(mm["mean"], mm["sd"], mm["n"])["t_stat"]
        stored = rows[mid]["accounting"]
        acc[mid].update({
            "dsr_my": dsr_mine["dsr"], "dsr_z_my": dsr_mine["z"],
            "dsr_helper": dsr_helper["deflated_sharpe_ratio"], "dsr_stored": stored["dsr_n58"],
            "t_my": t_mine, "t_helper": t_helper, "t_stored": stored["t_stat"],
        })
    # PBO: full window date list, 0 off own dates, 8 blocks of n // 8 dates
    date_index = {d: i for i, d in enumerate(window_dates)}
    matrix = []
    for mid in tier_a["members"]:
        m = members[mid]
        dates = window_dates if m["dates_ref"] == "window" else statistic_dates
        full = np.zeros(len(window_dates))
        for dt, v in zip(dates, m["daily"], strict=True):
            full[date_index[dt]] = float(v)
        matrix.append(blocks_of(full.tolist()))
    pbo_mine = my_pbo(matrix)
    pbo_helper = probability_of_backtest_overfitting(matrix, N_PBO_BLOCKS)
    stored_pbo = decisions["family"]["pbo_n58"]
    results["family"] = {
        "sharpe_variance_58_my": var58, "sharpe_variance_58_stored": decisions["family"]["dsr_n58"]["sharpe_variance"],
        "expected_max_sharpe_my": bench_my, "expected_max_sharpe_helper": bench_helper,
        "expected_max_sharpe_stored": decisions["family"]["dsr_n58"]["expected_max_daily_sharpe_under_null"],
        "pbo_my": pbo_mine, "pbo_helper": {"pbo": pbo_helper.pbo, "n_splits": pbo_helper.n_splits},
        "pbo_stored": stored_pbo, "block_days": len(window_dates) // N_PBO_BLOCKS,
        "max_dsr_my": max(acc[mid]["dsr_my"] for mid in acc),
        "max_dsr_member": max(acc, key=lambda k: acc[k]["dsr_my"]),
        "max_t_my": max(acc[mid]["t_my"] for mid in acc),
        "max_t_member": max(acc, key=lambda k: acc[k]["t_my"]),
    }
    # reported-only: PBO at N = 101 and the 101-member Sharpe variance
    matrix101 = list(matrix)
    for mid in tier_b["members"]:
        m = members[mid]
        dates = window_dates if m["dates_ref"] == "window" else statistic_dates
        full = np.zeros(len(window_dates))
        for dt, v in zip(dates, m["daily"], strict=True):
            full[date_index[dt]] = float(v)
        matrix101.append(blocks_of(full.tolist()))
    sharpes101 = sharpes + [my_moments(list(map(float, members[mid]["daily"])))["sharpe"]
                            for mid in tier_b["members"]]
    results["family"]["reported_only"] = {
        "pbo_101_my": my_pbo(matrix101), "pbo_101_stored": decisions["family"]["reported_pbo_n101"],
        "sharpe_variance_101_my": statistics.pvariance(sharpes101),
        "sharpe_variance_101_stored": decisions["family"]["reported_dsr_n101"]["sharpe_variance"],
    }
    # five edge conditions per Tier A member
    edge = {}
    for mid in tier_a["members"]:
        conds = {"holm_reject": my_holm[mid]["reject"],
                 "composite_pass": members[mid]["composite"] == "pass",
                 "dsr_above_0_95": acc[mid]["dsr_my"] > 0.95,
                 "t_above_3": acc[mid]["t_my"] > 3.0,
                 "pbo_below_0_5": pbo_mine["pbo"] < 0.5}
        stored = rows[mid]["edge_checks"]
        edge[mid] = {"my": conds, "my_passes": all(conds.values()),
                     "stored": stored,
                     "equal": all(conds[k] == stored[k] for k in conds) and stored["passes"] == all(conds.values()),
                     "failing": [k for k, v in conds.items() if not v]}
    results["edge"] = edge
    results["accounting"] = acc
    results["any_edge_my"] = [k for k, v in edge.items() if v["my_passes"]]
    results["any_edge_stored"] = [k for k, v in edge.items() if v["stored"]["passes"]]
    results["status_counts"] = {"A": {}, "B": {}}
    for mid, r in rows.items():
        c = results["status_counts"][r["tier"]]
        c[r["status"]] = c.get(r["status"], 0) + 1

    # -- start rule from logged medians, then medians from the parquets
    log("start rule from logged medians")
    sr = step5["start_rule"]
    results["start_rule_logged"] = start_rule_from_logged(sr)
    results["start_rule_runner"] = {"v_ref": sr["v_ref"], "binding": sr["binding"],
                                    "sensitivity": sr["sensitivity"], "S": sr["S"]}
    log("monthly medians from the parquets (loaders only)")
    from data.research_bars import load_confirmation_bars, load_research_bars
    research = load_research_bars(("ts_event", "volume", "trade_date"))
    ref_med, _ = monthly_medians_from_bars(research, "2025-04", "2026-05")
    del research
    conf = load_confirmation_bars(("ts_event", "volume", "trade_date"))
    ext_med, ext_first = monthly_medians_from_bars(conf, "2019-05", "2024-02")
    conf_dates = sorted(set(conf["trade_date"].astype(str)))
    del conf
    ref_dev = {m: abs(ref_med.get(m, float("nan")) - v) for m, v in sr["reference_monthly_medians"].items()}
    ext_dev = {m: abs(ext_med.get(m, float("nan")) - v) for m, v in sr["extension_monthly_medians"].items()}
    first_dev = {m: ext_first.get(m) == v for m, v in sr["extension_first_trade_dates"].items()}
    recomputed = start_rule_from_logged({"reference_monthly_medians": ref_med,
                                         "extension_monthly_medians": ext_med,
                                         "extension_first_trade_dates": ext_first})
    results["start_rule_parquet"] = {
        "reference_monthly_medians": ref_med, "extension_monthly_medians": ext_med,
        "extension_first_trade_dates": ext_first,
        "reference_max_abs_dev": max(ref_dev.values()), "extension_max_abs_dev": max(ext_dev.values()),
        "reference_months_missing": [m for m in sr["reference_monthly_medians"] if m not in ref_med],
        "extension_months_missing": [m for m in sr["extension_monthly_medians"] if m not in ext_med],
        "extra_months": sorted(set(ext_med) - set(sr["extension_monthly_medians"])),
        "first_dates_all_equal": all(first_dev.values()),
        "first_dates_unequal": [m for m, ok in first_dev.items() if not ok],
        "recomputed_rule": recomputed,
        "window_trade_dates_from_parquet": len([d for d in conf_dates if d >= sr["S"]]),
        "window_dates_equal_to_step7": [d for d in conf_dates if d >= sr["S"]] == window_dates,
    }

    # -- class verdicts and statement fields (list 3.3-3.5, NULL_CRITERIA 6-7)
    log("class verdicts and statement fields")
    classes = {}
    for cls, dec in decisions["classes"].items():
        mids = [mid for mid, e in exact.items() if e["class"] == cls]
        not_meeting = [mid for mid in mids if not exact[mid]["null_meets"]]
        no_evidence = [mid for mid in mids if exact[mid]["n_activity"] == 0 or exact[mid]["se_boot"] == 0]
        inactivity = [mid for mid in mids if exact[mid]["null_meets"] and exact[mid]["n_activity"] < INACTIVITY_COUNT]
        if cls == "C6":
            verdict = "inconclusive until Stage D.1g (list 3.5)"
        elif not_meeting:
            verdict = "inconclusive"
        else:
            verdict = "null"
        trials = [mid for mid in mids if exact[mid]["kind"] == "trial"]
        freq = statistics.median([exact[mid]["activity_per_own_date"] for mid in trials]) if trials else None
        least = min(mids, key=lambda k: exact[k]["n_activity"])
        largest = max(mids, key=lambda k: exact[k]["per_trade_ucb95"])
        sf = dec["statement_fields"]
        classes[cls] = {
            "my_members": sorted(mids), "runner_members": sorted(dec["members"]),
            "members_equal": sorted(mids) == sorted(dec["members"]),
            "my_verdict": verdict, "runner_verdict": dec["verdict"],
            "my_not_meeting": not_meeting, "runner_not_meeting": dec["members_not_meeting_null"],
            "my_no_evidence": no_evidence,
            "my_inactivity": inactivity, "runner_inactivity": sf["null_by_inactivity_members"],
            "my_label": "null by inactivity" if inactivity else None, "runner_label": sf["label"],
            "my_frequency": freq, "runner_frequency": sf["class_frequency_trades_per_day"],
            "my_eps_per_trade": EPS_DAY / freq if freq else None, "runner_eps_per_trade": sf["epsilon_per_trade"],
            "my_least": {"id": least, "count": exact[least]["n_activity"]}, "runner_least": sf["least_active_member"],
            "my_largest": {"member": largest, "value": exact[largest]["per_trade_ucb95"]},
            "runner_largest": sf["largest_per_trade_ucb95"],
            "trial_members": trials,
        }
    results["classes"] = classes
    results["blocking_members"] = [mid for mid, e in exact.items() if not e["null_meets"]]
    results["inactivity_members_all"] = [mid for mid, e in exact.items() if e["n_activity"] < INACTIVITY_COUNT]
    results["runner_class_verdicts"] = decisions["summary"]["class_verdicts"]
    results["runner_void"] = decisions["void"]
    results["c_h4"] = {"ucb95": exact[BINDING["C6"]]["ucb95"], "labels": rows[BINDING["C6"]]["labels"],
                       "status": rows[BINDING["C6"]]["status"]}

    # -- rebuild every trial's per-micro daily series from raw_trial_series
    log("raw trial series rebuild")
    raw_cmp = {}
    for rts in step7["raw_trial_series"]:
        mid = rts["label"]
        pnls = np.asarray(rts["trip_pnls_usd"], dtype=float)
        micros = np.asarray(rts["trip_micros"], dtype=float)
        n_per_day = np.asarray(rts["daily_n_trips"], dtype=int)
        per_micro = pnls / (TICK_USD * micros)
        bounds = np.concatenate([[0], np.cumsum(n_per_day)])
        rebuilt = np.array([per_micro[bounds[i]:bounds[i + 1]].sum() for i in range(len(n_per_day))])
        usd = np.array([pnls[bounds[i]:bounds[i + 1]].sum() for i in range(len(n_per_day))])
        member_daily = np.asarray(members[mid]["daily"], dtype=float)
        raw_cmp[mid] = {
            "n_trips": int(len(pnls)), "sum_daily_n_trips": int(n_per_day.sum()),
            "n_days": int(len(n_per_day)), "member_n_days": int(len(member_daily)),
            "max_abs_dev_daily": float(np.max(np.abs(rebuilt - member_daily))) if len(rebuilt) == len(member_daily) else None,
            "max_abs_dev_daily_net_usd": float(np.max(np.abs(usd - np.asarray(rts["daily_net_usd"], dtype=float)))),
            "activity_equal": list(map(int, n_per_day)) == list(map(int, members[mid]["daily_activity"])),
            "micros_set": sorted(set(int(x) for x in micros)) if len(micros) else [],
            "n_trips_equals_runner_n_activity": int(len(pnls)) == rows[mid]["n_activity"],
        }
    results["raw_rebuild"] = raw_cmp
    results["raw_rebuild_max_dev"] = max((v["max_abs_dev_daily"] or 0.0) for v in raw_cmp.values())
    results["raw_rebuild_n_trials"] = len(raw_cmp)
    results["trial_members_without_raw"] = [mid for mid, e in exact.items() if e["kind"] == "trial" and mid not in raw_cmp]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "d1f_run_verify_results.json")
    with open(out_path, "w") as fh:
        json.dump(results, fh, indent=1, default=float)
    log(f"wrote {out_path}")


if __name__ == "__main__":
    main()
