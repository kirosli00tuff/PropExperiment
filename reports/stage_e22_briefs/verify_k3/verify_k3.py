"""VerdictVerifier-K3 (Fable): independent recomputation of reports/stage_e22_k3_verdict.json.

Own code throughout (numpy, math, statistics). funnel.null_generator.stationary_bootstrap_indices is
called only to cross-check my own index builder on a few draws; funnel.multiple_comparisons only as a
second check after my own DSR / t / PBO formulas. Nothing under screening/ is imported or called.
Writes reports/stage_e22_briefs/verify_k3/figures.json and prints a short summary.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
LIST = ROOT / "reports/stage_e22_k3_confirmation_list.json"
VERDICT = ROOT / "reports/stage_e22_k3_verdict.json"
MARKER = ROOT / "reports/stage_e22_K3_RUN_ONCE.json"
RUN_DIR = ROOT / "reports/stage_e22_confirm_k3"
COSTS = ROOT / "reports/stage_e2a_costs.json"
EPS = ROOT / "reports/stage_e2a_epsilon.json"
OUT = ROOT / "reports/stage_e22_briefs/verify_k3/figures.json"
HARNESS_V13 = "dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4"
LIST_SHA = "43456def5b4f627e384eb42de3a84c8c1f0ee5b9c3be403eda6a7d9a21f1e2b4"
FLATTENED_14 = ("2022-01-17", "2022-02-21", "2022-05-30", "2022-06-20", "2022-07-04", "2022-09-05",
                "2022-11-24", "2023-01-16", "2023-02-20", "2023-05-29", "2023-06-19", "2023-07-04",
                "2023-09-04", "2023-11-23")
CT = ZoneInfo("America/Chicago")
EULER = 0.57721566490153286
ND = statistics.NormalDist()

findings: list[str] = []


def note(msg: str) -> None:
    findings.append(msg)


def rec_name(member: str) -> str:
    return f"K3_{member.replace(' ', '_')}_confirmation.json"


# ------------------------------------------------------------------ my bootstrap ----
def my_sb_indices(rng: np.random.Generator, n: int, mean_block: float) -> np.ndarray:
    """Circular stationary bootstrap, my own formulation: draw n uniform starts and n renewal
    flags (p = 1/mean_block, the first forced), then index = start of the current block plus the
    offset since that renewal, modulo n. Same generator consumption order as the program's."""
    starts = rng.integers(0, n, size=n)
    renew = rng.random(n) < 1.0 / mean_block
    renew[0] = True
    pos = np.arange(n)
    last_renew = np.maximum.accumulate(np.where(renew, pos, 0))
    return (starts[last_renew] + (pos - last_renew)) % n


def my_sb_indices_loop(rng: np.random.Generator, n: int, mean_block: float) -> list[int]:
    starts = rng.integers(0, n, size=n)
    renew = rng.random(n) < 1.0 / mean_block
    renew[0] = True
    out: list[int] = []
    for i in range(n):
        out.append(int(starts[i]) if renew[i] else (out[-1] + 1) % n)
    return out


def bootstrap(values: np.ndarray, seed: int, b: int, mean_block: float) -> dict:
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(b)
    for i in range(b):
        means[i] = values[my_sb_indices(rng, n, mean_block)].mean()
    theta = float(values.mean())
    return {"theta_hat": theta, "ucb95": float(np.quantile(means, 0.95)),
            "se_boot": float(np.std(means)),
            "p_upper": (1 + int(np.sum(means - theta >= theta))) / (b + 1),
            "n_days": n}


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def my_moments(xs: np.ndarray) -> dict:
    n = len(xs)
    mean = float(xs.mean())
    sd = float(np.sqrt(((xs - mean) ** 2).mean()))
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurt": 3.0, "sharpe": 0.0}
    z = (xs - mean) / sd
    return {"n": n, "mean": mean, "sd": sd, "skew": float((z ** 3).mean()),
            "kurt": float((z ** 4).mean()), "sharpe": mean / sd}


def my_expected_max_sharpe(n_trials: int, var: float) -> float:
    if n_trials == 1:
        return 0.0
    return math.sqrt(var) * ((1 - EULER) * ND.inv_cdf(1 - 1.0 / n_trials)
                             + EULER * ND.inv_cdf(1 - 1.0 / (n_trials * math.e)))


def my_dsr(mom: dict, n_trials: int, var: float) -> float:
    bench = my_expected_max_sharpe(n_trials, var)
    sr = mom["sharpe"]
    denom = 1.0 - mom["skew"] * sr + 0.25 * (mom["kurt"] - 1.0) * sr ** 2
    z = (sr - bench) * math.sqrt(mom["n"] - 1) / math.sqrt(denom)
    return ND.cdf(z)


def my_pbo(matrix: list[list[float]], n_blocks: int = 8) -> dict:
    s = len(matrix)
    splits = list(combinations(range(n_blocks), n_blocks // 2))
    below_median = 0
    oos_w = []
    for train in splits:
        test = [k for k in range(n_blocks) if k not in train]
        ins = [sum(row[k] for k in train) for row in matrix]
        oos = [sum(row[k] for k in test) for row in matrix]
        best = ins.index(max(ins))  # first index on a tie, as D.1f's max(range, key) does
        worse = sum(1 for v in oos if v < oos[best])
        rank = (worse + 0.5) / s
        if rank <= 0.5:
            below_median += 1
        oos_w.append(oos[best])
    return {"pbo": below_median / len(splits), "n_splits": len(splits),
            "winner_mean_oos": statistics.fmean(oos_w),
            "p_winner_positive_oos": sum(v > 0 for v in oos_w) / len(oos_w)}


def my_holm(pvals: dict[str, float], k: int) -> dict:
    alpha_k = 0.05 / k
    m = len(pvals)
    order = sorted(pvals.items(), key=lambda kv: (kv[1], kv[0]))
    rows, still = [], True
    for i, (member, p) in enumerate(order, start=1):
        thr = alpha_k / (m - i + 1)
        rej = still and p <= thr
        if not rej:
            still = False
        rows.append({"member": member, "p_value": p, "rank": i, "threshold": thr, "reject": rej})
    return {"k": k, "alpha_k": alpha_k, "m": m, "rows": rows}


def close(a, b, rel=1e-9, abs_=1e-12) -> bool:
    if a is None or b is None:
        return a is b
    return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)


def main() -> int:
    clist = json.loads(LIST.read_text())
    verdict = json.loads(VERDICT.read_text())
    marker = json.loads(MARKER.read_text())
    costs = json.loads(COSTS.read_text())
    eps_tab = {x["vehicle"]: x for x in json.loads(EPS.read_text())["exposures"]}
    out: dict = {"items": {}, "trials": {}, "trip_rebuild": {}, "flattened_14": {}}
    trials = clist["trials"]
    by_member = {t["member"]: t for t in trials}
    bs = clist["bootstrap"]

    # ---------------------------------------------------------------- item 0 ----
    i0 = []
    if marker["list"]["sha256"] != LIST_SHA or marker["list"]["path"] != "reports/stage_e22_k3_confirmation_list.json":
        i0.append("marker list sha/path differs")
    if marker["harness_sha256"] != HARNESS_V13 or clist["harness_sha256"] != HARNESS_V13:
        i0.append("harness sha differs")
    if marker["cluster_freeze_sha256"] != clist["cluster_freeze_sha256"]:
        i0.append("marker freeze sha differs")
    if verdict["list_sha256"] != LIST_SHA or verdict["harness_sha256"] != HARNESS_V13:
        i0.append("verdict list/harness sha differs")
    if verdict["k_holm"] != clist["k_holm"] or verdict["program_n"] != clist["program_n"]:
        i0.append("verdict k_holm/program_n differs")
    c = verdict["constants"]
    if (c["seed_base"], c["resamples"], c["mean_block"], c["ucb_quantile"]) != (
            bs["seed_base"], bs["resamples"], bs["mean_block"], bs["ucb_quantile"]):
        i0.append("verdict constants differ from list bootstrap block")
    present = sorted(p.name for p in RUN_DIR.glob("K3_*_confirmation.json"))
    expected_run = sorted(rec_name(t["member"]) for t in trials if t["run"])
    expected_all = sorted(rec_name(t["member"]) for t in trials)
    extra = sorted(set(present) - set(expected_all))
    missing_run = sorted(set(expected_run) - set(present))
    notrun_present = sorted(set(present) & set(rec_name(t["member"]) for t in trials if not t["run"]))
    records: dict[str, dict] = {}
    field_mismatch = []
    for t in trials:
        p = RUN_DIR / rec_name(t["member"])
        if not p.exists():
            continue
        r = json.loads(p.read_text())
        records[t["member"]] = r
        probs = []
        if r["harness_sha256"] != HARNESS_V13: probs.append("harness")
        if r["cluster_freeze_sha256"] != clist["cluster_freeze_sha256"]: probs.append("freeze")
        if r["member"] != t["member"]: probs.append("member")
        if r["ordinal"] != t["ordinal"]: probs.append("ordinal")
        if r["window"] != "confirmation": probs.append("window")
        if r["s_x"] != t["s_x"]: probs.append("s_x")
        if sorted(l["root"] for l in r["legs"]) != sorted(t["legs"]): probs.append("legs")
        if r["price_path"] != t["price_path"]: probs.append("price_path")
        v = t["vehicle"]
        cw = clist["confirmation_window"][v]
        if (r["window_dates"]["first"], r["window_dates"]["last"]) != tuple(cw): probs.append("window_dates")
        if r["marker_list_sha256"] != LIST_SHA if "marker_list_sha256" in r else False: probs.append("list sha")
        if t["run"] and r["status"] not in ("run", "excluded_before_screening"): probs.append(f"status {r['status']}")
        if not t["run"]:
            declared = [l for l in t["labels"] if l != "source-overlap"]
            if r["status"] != "excluded_before_screening" or sorted(r["labels"]) != sorted(declared):
                probs.append(f"not-run record status/labels {r['status']} {r['labels']}")
        if probs:
            field_mismatch.append((t["member"], probs))
    run_with_series = [t["member"] for t in trials if t["run"] and records[t["member"]].get("series")]
    run_no_series = [(t["member"], records[t["member"]]["status"], records[t["member"]].get("coverage"))
                     for t in trials if t["run"] and not records[t["member"]].get("series")]
    out["items"]["0"] = {"marker_ok": not i0, "problems": i0, "records_present": len(present),
                         "extra_records": extra, "missing_run_records": missing_run,
                         "not_run_records_present": notrun_present, "field_mismatch": field_mismatch,
                         "run_with_series": len(run_with_series), "run_without_series": run_no_series,
                         "marker_members": marker["members"], "marker_not_run": marker["not_run"]}

    # ---------------------------------------------------------------- item 1 ----
    # cross-check my index builder against the program's frozen generator and a pure loop
    from funnel.null_generator import stationary_bootstrap_indices as frozen_sb
    xchk = True
    for seed in (1, 20260945, 777):
        a = my_sb_indices(np.random.default_rng(seed), 1191, 5.0)
        b = frozen_sb(np.random.default_rng(seed), 1191, 1191, 5.0)
        c3 = np.array(my_sb_indices_loop(np.random.default_rng(seed), 1191, 5.0))
        xchk &= bool(np.array_equal(a, b) and np.array_equal(a, c3))
    out["items"]["1_index_builder_equals_frozen_and_loop"] = xchk

    vrows = {r["member"]: r for r in verdict["trials"]}
    series: dict[str, tuple[list[str], np.ndarray]] = {}
    n_trips_src: dict[str, dict] = {}
    for m in run_with_series:
        t = by_member[m]
        r = records[m]
        s = r["series"]
        vals = np.asarray(s["values"], dtype=float)
        series[m] = (s["dates"], vals)
        seed = bs["seed_base"] + t["ordinal"]
        fig = bootstrap(vals, seed, bs["resamples"], bs["mean_block"])
        eps = float(t["eps_ticks"])
        n_tr = s["n_trips"]
        trips_file = json.loads((RUN_DIR / rec_name(m).replace(".json", "_trips.json")).read_text())
        n_trips_src[m] = {"series": n_tr, "trade_rate": r["trade_rate"]["n_trips"],
                          "trips_file": trips_file["n_trips"], "trips_len": len(trips_file["trips"])}
        rate = n_tr / fig["n_days"]
        power = phi(eps / fig["se_boot"] - 1.645) if fig["se_boot"] > 0 else 0.0
        ucb_below, power_ok = fig["ucb95"] < eps, power >= 0.80
        if n_tr == 0 or fig["se_boot"] == 0 or not ucb_below or not power_ok:
            status = "inconclusive"
        elif n_tr < 30:
            status = "null by inactivity"
        else:
            status = "null"
        mine = {**fig, "seed": seed, "eps": eps, "n_trips": n_tr, "trips_per_day": rate,
                "theta_per_trade": fig["theta_hat"] / rate, "ucb95_per_trade": fig["ucb95"] / rate,
                "null_power": power, "status": status, "tier": t["tier"],
                "flattened_14_trips": sum(1 for x in trips_file["trips"] if x["trade_date"] in FLATTENED_14),
                "flattened_14_close_reasons": sorted({x["close_reason"] for x in trips_file["trips"]
                                                      if x["trade_date"] in FLATTENED_14})}
        v = vrows[m]
        cmp = {}
        for key, vk in (("theta_hat", "theta_hat"), ("ucb95", "ucb95"), ("se_boot", "se_boot"),
                        ("p_upper", "p_upper"), ("n_days", "n_days"), ("n_trips", "n_trips"),
                        ("trips_per_day", "trips_per_day"), ("theta_per_trade", "theta_per_trade"),
                        ("ucb95_per_trade", "ucb95_per_trade"), ("null_power", "null_power"),
                        ("eps", "eps_ticks"), ("seed", "seed")):
            cmp[key] = close(mine[key], v[vk]) if isinstance(mine[key], float) else mine[key] == v[vk]
        cmp["status"] = mine["status"] == v["status"]
        cmp["labels"] = sorted(t["labels"]) == sorted(v["labels"])
        cmp["tier"] = t["tier"] == v["tier"]
        cmp["eps_operative"] = eps == float(eps_tab[t["vehicle"]]["eps_operative"])
        cmp["eps_usd"] = close(t["eps_usd_per_day_at_q"], eps * eps_tab[t["vehicle"]]["tick_value_usd"] * t["q_c"])
        cmp["n_trips_sources_agree"] = len({n_tr, r["trade_rate"]["n_trips"], trips_file["n_trips"],
                                            len(trips_file["trips"])}) == 1
        cmp["dates_match_window"] = (s["dates"][0], s["dates"][-1], len(s["dates"])) == (
            r["window_dates"]["first"], r["window_dates"]["last"], r["window_dates"]["n"])
        out["trials"][m] = {"mine": mine, "verdict": {k: v.get(k) for k in (
            "theta_hat", "ucb95", "se_boot", "p_upper", "n_days", "n_trips", "trips_per_day",
            "theta_per_trade", "ucb95_per_trade", "null_power", "status", "eps_ticks", "seed")},
            "agree": cmp, "all_agree": all(cmp.values())}

    # ---------------------------------------------------------------- item 2 ----
    tier_a = [t["member"] for t in trials if t["tier"] == "A"]
    pvals = {m: (out["trials"][m]["mine"]["p_upper"] if m in out["trials"] else 1.0) for m in tier_a}
    h5 = my_holm(pvals, clist["k_holm"])
    h9 = my_holm(pvals, 9)
    vh5, vh9 = verdict["edge_chain"]["holm"], verdict["edge_chain"]["holm_descriptive_k9"]

    def holm_eq(mine, theirs):
        if (mine["k"], mine["m"]) != (theirs["k"], theirs["m"]) or not close(mine["alpha_k"], theirs["alpha_k"]):
            return False
        for a, b in zip(mine["rows"], theirs["rows"]):
            if a["member"] != b["member"] or a["rank"] != b["rank"] or a["reject"] != b["reject"]:
                return False
            if not close(a["p_value"], b["p_value"]) or not close(a["threshold"], b["threshold"]):
                return False
        return True
    out["items"]["2"] = {"tier_a": tier_a, "mine_k5": h5, "mine_k9": h9,
                         "equal_k5": holm_eq(h5, vh5), "equal_k9": holm_eq(h9, vh9),
                         "tier_a_count_matches_family": len(tier_a) == vh5["m"]}

    # ---------------------------------------------------------------- item 3 ----
    moms = {m: my_moments(series[m][1]) for m in run_with_series}
    a_series = [m for m in tier_a if m in series]
    var_over = a_series if len(a_series) >= 2 else run_with_series
    var = statistics.pvariance([moms[m]["sharpe"] for m in var_over])
    n_prog = clist["program_n"]
    bench = my_expected_max_sharpe(n_prog, var)
    vd = verdict["edge_chain"]["dsr"]
    chain = {}
    for m in tier_a:
        mom = moms.get(m)
        d = my_dsr(mom, n_prog, var) if mom else None
        tv = mom["mean"] / (mom["sd"] / math.sqrt(mom["n"])) if mom and mom["sd"] > 0 else None
        chain[m] = {"dsr": d, "t": tv, "moments": mom}
    # PBO over the V14 c set aligned on the union of run trials' dates
    union = sorted(set().union(*(set(series[m][0]) for m in run_with_series)))
    idx = {d: i for i, d in enumerate(union)}
    pbo_set = a_series if len(a_series) >= 2 else run_with_series
    width = len(union) // 8
    matrix = []
    for m in pbo_set:
        al = np.zeros(len(union))
        for d, v in zip(*series[m]):
            al[idx[d]] = v
        matrix.append([float(al[k * width:(k + 1) * width].sum()) for k in range(8)])
    pb = my_pbo(matrix)
    vp = verdict["edge_chain"]["pbo"]
    # second check with the program's functions
    from funnel.multiple_comparisons import (deflated_sharpe_ratio, harvey_liu_zhu_verdict,
                                             probability_of_backtest_overfitting)
    second = {}
    for m in a_series:
        mom = moms[m]
        second[m] = {
            "dsr_funnel": deflated_sharpe_ratio(mom["sharpe"], mom["n"], n_prog, var, mom["skew"],
                                                mom["kurt"])["deflated_sharpe_ratio"],
            "t_funnel": harvey_liu_zhu_verdict(mom["mean"], mom["sd"], mom["n"])["t_stat"]}
    second["pbo_funnel"] = probability_of_backtest_overfitting(matrix, 8).pbo
    vt = verdict["edge_chain"]["trials"]
    out["items"]["3"] = {
        "variance_over_n": len(var_over), "variance_over_equals_verdict": sorted(var_over) == sorted(vd["variance_over"]),
        "sharpe_variance_mine": var, "sharpe_variance_verdict": vd["sharpe_variance"],
        "sharpe_variance_equal": close(var, vd["sharpe_variance"]),
        "bench_mine": bench, "bench_verdict": vd["expected_max_daily_sharpe_under_null"],
        "bench_equal": close(bench, vd["expected_max_daily_sharpe_under_null"], rel=1e-9),
        "bench_rel_diff": abs(bench - vd["expected_max_daily_sharpe_under_null"]) / abs(vd["expected_max_daily_sharpe_under_null"]),
        "n_trials_equal": vd["n_trials"] == n_prog,
        "chain_mine": chain, "chain_verdict": {m: {k: vt[m][k] for k in ("dsr", "t_stat", "pbo", "first_failing_step", "verdict", "passes")} for m in tier_a},
        "dsr_equal": {m: close(chain[m]["dsr"], vt[m]["dsr"], rel=1e-6) for m in tier_a},
        "dsr_rel_diff": {m: (abs(chain[m]["dsr"] - vt[m]["dsr"]) / abs(vt[m]["dsr"]) if chain[m]["dsr"] and vt[m]["dsr"] else None) for m in tier_a},
        "t_equal": {m: close(chain[m]["t"], vt[m]["t_stat"]) for m in tier_a},
        "pbo_mine": pb, "pbo_verdict": {k: vp[k] for k in ("pbo", "n_splits", "n_strategies", "block_days", "n_days", "window_days", "winner_mean_oos_ticks_per_micro", "p_winner_positive_oos", "degenerate")},
        "pbo_equal": close(pb["pbo"], vp["pbo"]) and pb["n_splits"] == vp["n_splits"] and len(pbo_set) == vp["n_strategies"]
                     and width == vp["block_days"] and len(union) == vp["window_days"]
                     and close(pb["winner_mean_oos"], vp["winner_mean_oos_ticks_per_micro"], rel=1e-9)
                     and close(pb["p_winner_positive_oos"], vp["p_winner_positive_oos"]),
        "pbo_set_equals_verdict": sorted(pbo_set) == sorted(vp["over"]),
        "union_days": len(union), "all_series_same_dates": all(series[m][0] == union for m in run_with_series),
        "second_check_funnel": second,
        "second_check_equal_mine": {m: close(second[m]["dsr_funnel"], chain[m]["dsr"], rel=1e-9) and close(second[m]["t_funnel"], chain[m]["t"]) for m in a_series} | {"pbo": close(second["pbo_funnel"], pb["pbo"])},
    }

    # ---------------------------------------------------------------- item 4 ----
    covered = [t["member"] for t in trials if t["tier"] in ("A", "B") and t["run"]]
    statuses = {m: (out["trials"][m]["mine"]["status"] if m in out["trials"] else "inconclusive (no series)") for m in covered}
    blocking = [m for m in covered if statuses[m] not in ("null", "null by inactivity")]
    stmt = verdict["statement"]
    chain_ok = {}
    for m in tier_a:
        passes = (h5["rows"][[r["member"] for r in h5["rows"]].index(m)]["reject"]
                  and chain[m]["dsr"] is not None and chain[m]["dsr"] > 0.95
                  and chain[m]["t"] is not None and chain[m]["t"] > 3.0 and pb["pbo"] < 0.5)
        expect = ("edge candidate, composite pending" if passes else "no edge")
        chain_ok[m] = {"expected_verdict": expect, "verdict_says": vt[m]["verdict"],
                       "first_failing_mine": next((k for k, ok in (("holm", h5["rows"][0]["reject"]), ("dsr", chain[m]["dsr"] > 0.95), ("t", chain[m]["t"] > 3.0), ("pbo", pb["pbo"] < 0.5)) if not ok), None),
                       "first_failing_verdict": vt[m]["first_failing_step"], "uses_word_edge_alone": vt[m]["verdict"] == "edge"}
    # resolution table
    res_mine = []
    for v in sorted({t["vehicle"] for t in trials}):
        tv_ = [t for t in trials if t["vehicle"] == v]
        fig = [(m, out["trials"][m]["mine"]) for m in (t["member"] for t in tv_) if m in covered and m in out["trials"]]
        fewest = min(fig, key=lambda kv: (kv[1]["n_trips"], kv[0])) if fig else None
        largest = max(fig, key=lambda kv: (kv[1]["ucb95_per_trade"], kv[0])) if fig else None
        res_mine.append({"vehicle": v, "eps_ticks": float(tv_[0]["eps_ticks"]), "q_c": tv_[0]["q_c"],
                         "fewest": None if not fewest else {"member": fewest[0], "n_trips": fewest[1]["n_trips"]},
                         "largest": None if not largest else {"member": largest[0], "ticks": largest[1]["ucb95_per_trade"]},
                         "not_covered_listed": [t["member"] for t in tv_ if t["member"] not in covered],
                         "run_without_series": [t["member"] for t in tv_ if t["member"] in covered and t["member"] not in out["trials"]]})
    res_eq = []
    for mine_r, their in zip(res_mine, verdict["resolution"]):
        ok = (mine_r["vehicle"] == their["vehicle"] and mine_r["eps_ticks"] == their["eps_ticks"]
              and mine_r["q_c"] == their["q_c"]
              and ((mine_r["fewest"] is None and their["fewest_trips"] is None) or
                   (mine_r["fewest"] and their["fewest_trips"] and mine_r["fewest"]["member"] == their["fewest_trips"]["member"] and mine_r["fewest"]["n_trips"] == their["fewest_trips"]["n_trips"]))
              and ((mine_r["largest"] is None and their["largest_ucb95_per_trade"] is None) or
                   (mine_r["largest"] and their["largest_ucb95_per_trade"] and mine_r["largest"]["member"] == their["largest_ucb95_per_trade"]["member"] and close(mine_r["largest"]["ticks"], their["largest_ucb95_per_trade"]["ticks"])))
              and sorted(mine_r["not_covered_listed"]) == sorted(their["not_covered"]))
        res_eq.append((their["vehicle"], ok))
    out["items"]["4"] = {
        "covered_mine": covered, "covered_equal": sorted(covered) == sorted(stmt["covered"]),
        "blocking_mine": blocking, "blocking_verdict": [b["member"] for b in stmt["blocking"]],
        "blocking_equal": sorted(blocking) == sorted(b["member"] for b in stmt["blocking"]),
        "statement_mine": "null" if covered and not blocking else "no statement", "statement_verdict": stmt["verdict"],
        "not_covered_mine": [t["member"] for t in trials if t["member"] not in covered],
        "not_covered_verdict": [x["member"] for x in stmt["not_covered"]],
        "null_by_inactivity_mine": [m for m in covered if statuses[m] == "null by inactivity"],
        "null_by_inactivity_verdict": stmt["null_by_inactivity"],
        "status_counts": {s: sum(1 for m in covered if statuses[m] == s) for s in set(statuses.values())},
        "chain_wording": chain_ok, "resolution_mine": res_mine, "resolution_equal": res_eq,
        "resolution_omits_run_without_series": [(r["vehicle"], r["run_without_series"]) for r in res_mine if r["run_without_series"]],
    }

    # ---------------------------------------------------------------- item 5 ----
    for m in ("K3-ldnrev-01 6E", "K3-ldnrev-01 6J", "K3-ldnrev-01 6S"):
        veh = by_member[m]["vehicle"]
        p = costs["products"][veh]
        tick_val = float(p["tick_value_usd"])
        comm_cents = round(float(p["commission_rt_usd"]) * 100, 6)
        buckets = p["buckets"]
        trips_file = json.loads((RUN_DIR / rec_name(m).replace(".json", "_trips.json")).read_text())
        r = records[m]
        dates, vals = series[m]
        rebuilt = dict.fromkeys(dates, 0.0)
        max_cost_err = 0.0
        cost_detail = []
        frac = 0
        dir_amb = 0
        for x in trips_file["trips"]:
            if not isinstance(x["gross_cents"], int) or not isinstance(x["net_cents"], int):
                frac += 1
            g, n_ = float(x["gross_cents_float"]), float(x["net_cents_float"])
            q = x["contracts"]
            # the modelled cost from the frozen table: commission + entry + exit side slippage
            def bucket(ts_ns: int) -> dict:
                dt = datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc).astimezone(CT)
                minute = dt.hour * 60 + dt.minute
                found = [b for b in buckets if b["start_min"] <= minute < b["end_min"]]
                assert len(found) == 1, (m, x["open_utc"], minute)
                return found[0]
            be, bx = bucket(x["open_ts_ns"]), bucket(x["close_ts_ns"])
            cands = []
            for es, xs in (("buy", "sell"), ("sell", "buy")):
                slip = be["side_ticks"][es] + bx["side_ticks"][xs]
                cands.append(q * (comm_cents + slip * tick_val * 100))
            observed = g - n_
            err = min(abs(cc - observed) for cc in cands)
            if abs(cands[0] - cands[1]) > 1e-6:
                dir_amb += 1
            max_cost_err = max(max_cost_err, err)
            if err > 0.5 + 1e-6:
                cost_detail.append((x["trade_date"], observed, cands, be["key"], bx["key"]))
            if x["trade_date"] not in rebuilt:
                cost_detail.append(("date not in series", x["trade_date"]))
                continue
            rebuilt[x["trade_date"]] += n_ / 100.0 / tick_val / q
        rb = np.array([rebuilt[d] for d in dates])
        usd = np.asarray(r["daily_net_usd"], dtype=float)
        out["trip_rebuild"][m] = {
            "tick_value_usd": tick_val, "commission_rt_usd": p["commission_rt_usd"], "q_c": by_member[m]["q_c"],
            "n_trips": len(trips_file["trips"]), "fractional_cents_trips": frac,
            "max_abs_series_diff_ticks": float(np.max(np.abs(rb - vals))),
            "series_equal_1e-9": bool(np.allclose(rb, vals, rtol=1e-9, atol=1e-9)),
            "daily_net_usd_equals_series_x_tick_x_q": bool(np.allclose(usd, vals * tick_val * by_member[m]["q_c"], rtol=1e-9, atol=1e-9)),
            "max_abs_cost_error_cents_vs_table": max_cost_err, "direction_ambiguous_trips": dir_amb,
            "cost_mismatch_detail": cost_detail[:5],
            "trips_on_flattened_14": [(x["trade_date"], x["close_reason"], x["close_utc"]) for x in trips_file["trips"] if x["trade_date"] in FLATTENED_14],
            "close_reasons": sorted({x["close_reason"] for x in trips_file["trips"]}),
            "flattened_dates_in_window": [d for d in FLATTENED_14 if d in set(dates)],
        }
    out["flattened_14"] = {m: out["trials"][m]["mine"]["flattened_14_trips"] for m in out["trials"]}
    out["flattened_14_total_trips"] = sum(out["flattened_14"].values())
    out["flattened_14_close_reasons"] = sorted(set().union(*(set(out["trials"][m]["mine"]["flattened_14_close_reasons"]) for m in out["trials"])))

    # ---------------------------------------------------------------- summary ----
    OUT.write_text(json.dumps(out, indent=1, default=str))
    print("item0", out["items"]["0"]["problems"], "present", len(present), "extra", extra, "missing_run", missing_run,
          "notrun_present", len(notrun_present), "field_mismatch", field_mismatch, "run_without_series", [(a, b) for a, b, _ in run_no_series])
    print("item1 index builder == frozen == loop:", xchk)
    dis = [m for m, v in out["trials"].items() if not v["all_agree"]]
    print("item1 trials recomputed", len(out["trials"]), "all agree", not dis, "disagree:", dis)
    for m in dis:
        print("   ", m, {k: v for k, v in out["trials"][m]["agree"].items() if not v})
    print("item2 holm k5 equal", out["items"]["2"]["equal_k5"], "k9 equal", out["items"]["2"]["equal_k9"], "p", pvals)
    i3 = out["items"]["3"]
    print("item3 var equal", i3["sharpe_variance_equal"], "bench equal", i3["bench_equal"], "bench rel diff %.2e" % i3["bench_rel_diff"],
          "dsr", {m: (chain[m]["dsr"], vt[m]["dsr"]) for m in tier_a}, "dsr rel diff", i3["dsr_rel_diff"],
          "t equal", i3["t_equal"], {m: (chain[m]["t"], vt[m]["t_stat"]) for m in tier_a})
    print("item3 pbo", pb, "verdict", i3["pbo_verdict"]["pbo"], "equal", i3["pbo_equal"], "set equal", i3["pbo_set_equals_verdict"],
          "union", len(union), "same dates", i3["all_series_same_dates"], "second check", i3["second_check_equal_mine"])
    i4 = out["items"]["4"]
    print("item4 statement", i4["statement_mine"], i4["statement_verdict"], "covered equal", i4["covered_equal"], "blocking", i4["blocking_mine"], i4["blocking_equal"],
          "status counts", i4["status_counts"], "nbi", i4["null_by_inactivity_mine"], i4["null_by_inactivity_verdict"])
    print("item4 chain", i4["chain_wording"])
    print("item4 resolution equal", i4["resolution_equal"], "omits", i4["resolution_omits_run_without_series"])
    for m, v in out["trip_rebuild"].items():
        print("item5", m, {k: v[k] for k in ("n_trips", "fractional_cents_trips", "max_abs_series_diff_ticks", "series_equal_1e-9",
                                             "daily_net_usd_equals_series_x_tick_x_q", "max_abs_cost_error_cents_vs_table",
                                             "direction_ambiguous_trips", "trips_on_flattened_14", "flattened_dates_in_window")}, v["cost_mismatch_detail"][:2])
    print("flattened14 trips per run trial (nonzero):", {m: n for m, n in out["flattened_14"].items() if n}, "total", out["flattened_14_total_trips"], "close reasons", out["flattened_14_close_reasons"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
