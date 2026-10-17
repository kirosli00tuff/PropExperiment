"""VerdictVerifier-K5 (Fable): independent recompute of reports/stage_e22_k5_verdict.json.

Own code for every figure (numpy, math, statistics). The only program function called for the
figures is funnel.null_generator.stationary_bootstrap_indices (the frozen generator, allowed by
the brief); funnel.multiple_comparisons is called afterwards as a second check and labelled so.
screening.stage_e_verdict is never imported. No bar data is read.

Writes reports/stage_e22_briefs/verify_k5/recompute.json and prints a short summary.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from datetime import date, datetime, timezone
from itertools import combinations
from pathlib import Path
from statistics import NormalDist

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from funnel.null_generator import stationary_bootstrap_indices  # noqa: E402  (allowed)

LIST = REPO / "reports/stage_e22_k5_confirmation_list.json"
VERDICT = REPO / "reports/stage_e22_k5_verdict.json"
RUN_DIR = REPO / "reports/stage_e22_confirm_k5"
MARKER = REPO / "reports/stage_e22_K5_RUN_ONCE.json"
COSTS = REPO / "reports/stage_e2a_costs.json"
EPS = REPO / "reports/stage_e2a_epsilon.json"
OUT = REPO / "reports/stage_e22_briefs/verify_k5/recompute.json"

SEED_BASE, B, MEAN_BLOCK, Q = 20260923, 10_000, 5.0, 0.95
Z_NULL, POWER_MIN, INACTIVITY_MIN = 1.645, 0.80, 30
DSR_MIN, T_MIN, PBO_MAX, N_BLOCKS = 0.95, 3.0, 0.5, 8
EULER = 0.5772156649015329
ND = NormalDist()
REL_TOL = 1e-9


def rel_close(a: float | None, b: float | None, tol: float = REL_TOL) -> bool:
    if a is None or b is None:
        return a is b
    if a == b:
        return True
    return abs(a - b) <= tol * max(abs(a), abs(b), 1e-300)


def rec_name(cluster: str, member: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9._-]+", "_", f"{cluster}_{member}_confirmation").strip("_") + ".json"


# ----------------------------------------------------------------- item 1 ----
def my_bootstrap(values: np.ndarray, seed: int) -> dict:
    """theta_hat, UCB95, SE_boot, p_upper by my own formulas on the frozen generator's indices."""
    n = len(values)
    rng = np.random.default_rng(seed)
    means = np.empty(B)
    for i in range(B):
        idx = stationary_bootstrap_indices(rng, n, n, MEAN_BLOCK)
        means[i] = values[idx].mean()
    theta = float(values.mean())
    # one-sided p for H0: theta <= 0, D.1f convention: P*(theta* - theta_hat >= theta_hat)
    p_upper = (1 + int(np.sum((means - theta) >= theta))) / (B + 1)
    return {"theta_hat": theta, "ucb95": float(np.quantile(means, Q)),
            "se_boot": float(np.std(means)), "p_upper": p_upper, "n_days": n}


def my_power(se: float, eps: float) -> float:
    if se <= 0:
        return 0.0
    return ND.cdf(eps / se - Z_NULL)


def my_status(n_trips: int, se: float, ucb: float, power: float, eps: float) -> tuple[str, list[str]]:
    reasons = []
    if n_trips == 0:
        reasons.append("zero trips")
    if se == 0.0:
        reasons.append("SE_boot = 0")
    if not ucb < eps:
        reasons.append("UCB95 >= eps_X")
    if not power >= POWER_MIN:
        reasons.append("null power < 0.80")
    if reasons:
        return "inconclusive", reasons
    return ("null by inactivity" if n_trips < INACTIVITY_MIN else "null"), []


# ----------------------------------------------------------------- item 2 ----
def my_holm(pvals: dict[str, float], k: int) -> dict:
    alpha_k = 0.05 / k
    m = len(pvals)
    order = sorted(pvals, key=lambda key: (pvals[key], key))
    rows, rejecting = [], True
    for i, key in enumerate(order):
        thr = alpha_k / (m - i)
        rejecting = rejecting and pvals[key] <= thr
        rows.append({"member": key, "p_value": pvals[key], "rank": i + 1, "threshold": thr,
                     "reject": rejecting})
    return {"k": k, "alpha_k": alpha_k, "m": m, "rows": rows}


# ----------------------------------------------------------------- item 3 ----
def my_moments(xs: list[float]) -> dict:
    n = len(xs)
    mean = statistics.fmean(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    skew = sum((x - mean) ** 3 for x in xs) / n / sd ** 3
    kurt = sum((x - mean) ** 4 for x in xs) / n / sd ** 4
    return {"n": n, "mean": mean, "sd": sd, "skew": skew, "kurtosis": kurt, "sharpe": mean / sd}


def my_expected_max_sharpe(n_trials: int, var: float) -> float:
    if n_trials == 1:
        return 0.0
    return math.sqrt(var) * ((1 - EULER) * ND.inv_cdf(1 - 1 / n_trials)
                             + EULER * ND.inv_cdf(1 - 1 / (n_trials * math.e)))


def my_dsr(mom: dict, n_trials: int, var: float) -> tuple[float | None, float]:
    sr0 = my_expected_max_sharpe(n_trials, var)
    sr = mom["sharpe"]
    denom_sq = 1 - mom["skew"] * sr + 0.25 * (mom["kurtosis"] - 1) * sr ** 2
    if mom["sd"] <= 0 or denom_sq <= 0:
        return None, sr0
    z = (sr - sr0) * math.sqrt(mom["n"] - 1) / math.sqrt(denom_sq)
    return ND.cdf(z), sr0


def my_t(mom: dict) -> float | None:
    if mom["sd"] <= 0 or mom["n"] < 2:
        return None
    return mom["mean"] / (mom["sd"] / math.sqrt(mom["n"]))


def my_pbo(aligned: dict[str, np.ndarray]) -> dict:
    """CSCV on 8 contiguous blocks of n // 8 dates (the trailing n % 8 dates are dropped)."""
    labels = list(aligned)
    n = len(next(iter(aligned.values())))
    width = n // N_BLOCKS
    perf = {k: [float(aligned[k][b * width:(b + 1) * width].sum()) for b in range(N_BLOCKS)]
            for k in labels}
    logits, oos_best = [], []
    for train in combinations(range(N_BLOCKS), N_BLOCKS // 2):
        test = [b for b in range(N_BLOCKS) if b not in train]
        ins = {k: sum(perf[k][b] for b in train) for k in labels}
        oos = {k: sum(perf[k][b] for b in test) for k in labels}
        best = max(labels, key=lambda k: ins[k])  # first max on ties, as max() does
        worse = sum(1 for k in labels if oos[k] < oos[best])
        rank = min(max((worse + 0.5) / len(labels), 1e-9), 1 - 1e-9)
        logits.append(math.log(rank / (1 - rank)))
        oos_best.append(oos[best])
    return {"n_strategies": len(labels), "n_days": n, "block_days": width,
            "n_splits": len(logits), "pbo": sum(1 for lg in logits if lg <= 0) / len(logits),
            "winner_mean_oos": statistics.fmean(oos_best),
            "p_winner_positive_oos": sum(1 for x in oos_best if x > 0) / len(oos_best)}


# ----------------------------------------------------------------- item 5 ----
def rebuild_series(trips: list[dict], window_dates: list[str], tick_value_usd: float,
                   commission_rt_usd: float, event_side_ticks: float, bucket_side_ticks) -> dict:
    """Daily net ticks per contract from the trip list and the cost table.
    net_cents(trip) = gross_cents - contracts*(2*commission_side_cents) - 2*slippage_cents(side).
    slippage_cents = ceil(round(qty * slip_ticks * tick_value_cents, 6)) (sim fill-model rule)."""
    tick_cents = tick_value_usd * 100
    comm_side_cents = commission_rt_usd * 100 / 2
    daily: dict[str, float] = {d: 0.0 for d in window_dates}
    n_match_event, n_match_bucket, n_match_neither, grid_ok = 0, 0, 0, 0
    for t in trips:
        gross, net, q = t["gross_cents"], t["net_cents"], t["contracts"]
        if not (isinstance(gross, int) and isinstance(net, int)):
            raise ValueError("fractional cents in a trip; extend the rebuild")
        if gross % round(tick_cents) == 0:
            grid_ok += 1
        slip_event = math.ceil(round(q * event_side_ticks * tick_cents, 6))
        cost_event = 2 * round(q * comm_side_cents) + 2 * slip_event
        open_ct = bucket_side_ticks(t["open_utc"])
        close_ct = bucket_side_ticks(t["close_utc"])
        cost_bucket = (2 * round(q * comm_side_cents)
                       + math.ceil(round(q * open_ct * tick_cents, 6))
                       + math.ceil(round(q * close_ct * tick_cents, 6)))
        if gross - net == cost_event:
            n_match_event += 1
        elif gross - net == cost_bucket:
            n_match_bucket += 1
        else:
            n_match_neither += 1
        daily[t["trade_date"]] += (net / 100) / tick_value_usd / q
    return {"daily": daily, "n_trips": len(trips), "n_cost_matches_event_window": n_match_event,
            "n_cost_matches_regular_bucket": n_match_bucket, "n_cost_matches_neither": n_match_neither,
            "n_gross_on_tick_grid": grid_ok}


def ct_minute(utc_text: str) -> int:
    """UTC ISO text -> CT minute of day (America/Chicago)."""
    from zoneinfo import ZoneInfo
    ts = datetime.fromisoformat(utc_text.replace("Z", "+00:00")).astimezone(ZoneInfo("America/Chicago"))
    return ts.hour * 60 + ts.minute


def main() -> None:
    L = json.loads(LIST.read_text())
    V = json.loads(VERDICT.read_text())
    marker = json.loads(MARKER.read_text())
    costs = json.loads(COSTS.read_text())
    eps_tab = json.loads(EPS.read_text())
    out: dict = {"items": {}}
    vtr = {t["member"]: t for t in V["trials"]}

    # ---- item 0: inputs equal the hashed list
    item0 = {"marker_list_sha256_equals_list": marker["list"]["sha256"] == V["list_sha256"],
             "marker_harness": marker["harness_sha256"], "marker_members": marker["members"],
             "marker_not_run": marker["not_run"], "records": {}, "mismatches": []}
    records = {}
    for t in L["trials"]:
        p = RUN_DIR / rec_name("K5", t["member"])
        if not p.exists():
            item0["records"][t["member"]] = "NO RECORD"
            if t["run"]:
                item0["mismatches"].append(f"{t['member']}: run: true but no record")
            continue
        r = json.loads(p.read_text())
        records[t["member"]] = r
        checks = {
            "harness": r.get("harness_sha256") == L["harness_sha256"],
            "freeze": r.get("cluster_freeze_sha256") == L["cluster_freeze_sha256"],
            "member": r.get("member") == t["member"], "ordinal": r.get("ordinal") == t["ordinal"],
            "window": r.get("window") == "confirmation", "s_x": r.get("s_x") == t["s_x"],
            "legs": [lg["root"] for lg in r.get("legs", [])] == t["legs"],
            "price_path": r.get("price_path") == t["price_path"],
            "schema": r.get("schema") == "stage_e_member_record/1",
        }
        bad = [k for k, ok in checks.items() if not ok]
        item0["records"][t["member"]] = {"status": r.get("status"), "labels": r.get("labels"),
                                         "list_run": t["run"], "list_tier": t["tier"],
                                         "list_labels": t["labels"], "field_mismatches": bad,
                                         "coverage": r.get("coverage")}
        if bad:
            item0["mismatches"].append(f"{t['member']}: {bad}")
    extra = sorted(set(p.name for p in RUN_DIR.glob("K5_*_confirmation.json"))
                   - {rec_name("K5", t["member"]) for t in L["trials"]})
    item0["records_not_in_list"] = extra
    item0["n_records"] = len(records)
    item0["n_list_run_true"] = sum(1 for t in L["trials"] if t["run"])
    out["items"]["0"] = item0

    # ---- item 1: per run trial
    series: dict[str, tuple[list[str], np.ndarray, int]] = {}
    item1 = {}
    for t in L["trials"]:
        r = records.get(t["member"])
        if r is None or r.get("status") != "run":
            continue
        s = r["series"]
        vals = np.asarray(s["values"], dtype=float)
        if t["run"]:
            series[t["member"]] = (s["dates"], vals, s["n_trips"])
        seed = SEED_BASE + t["ordinal"]
        bt = my_bootstrap(vals, seed)
        power = my_power(bt["se_boot"], t["eps_ticks"])
        status, reasons = my_status(s["n_trips"], bt["se_boot"], bt["ucb95"], power, t["eps_ticks"])
        rate = s["n_trips"] / bt["n_days"]
        mine = {**bt, "seed": seed, "list_seed": t["bootstrap_seed"], "n_trips": s["n_trips"],
                "trips_per_day": rate, "theta_per_trade": bt["theta_hat"] / rate if rate else None,
                "ucb95_per_trade": bt["ucb95"] / rate if rate else None, "null_power": power,
                "status": status, "reasons": reasons, "series_unit": s["unit"],
                "series_vehicle": s["vehicle"], "eps_ticks": t["eps_ticks"]}
        v = vtr[t["member"]]
        cmp = {}
        for key in ("theta_hat", "ucb95", "se_boot", "p_upper", "n_days", "n_trips",
                    "trips_per_day", "theta_per_trade", "ucb95_per_trade", "null_power"):
            cmp[key] = rel_close(mine[key], v.get(key)) if key in v else "absent in verdict"
        cmp["status"] = (mine["status"] == v.get("status")) if t["run"] else "verdict: not used"
        cmp["seed"] = (seed == t["bootstrap_seed"] == v.get("seed", seed))
        item1[t["member"]] = {"mine": mine, "verdict": {k: v.get(k) for k in
                              ("theta_hat", "ucb95", "se_boot", "p_upper", "n_days", "n_trips",
                               "trips_per_day", "theta_per_trade", "ucb95_per_trade", "null_power",
                               "status", "seed", "record_status", "covered", "tier")},
                              "equal": cmp}
    out["items"]["1"] = item1

    # ---- item 2: Holm
    tier_a = [t["member"] for t in L["trials"] if t["tier"] == "A"]
    pvals = {m: (item1[m]["mine"]["p_upper"] if m in item1 else 1.0) for m in tier_a}
    h5, h9 = my_holm(pvals, L["k_holm"]), my_holm(pvals, 9)
    vh, vh9 = V["edge_chain"]["holm"], V["edge_chain"]["holm_descriptive_k9"]
    out["items"]["2"] = {"tier_a": tier_a, "pvalues": pvals, "mine_k5": h5, "mine_k9": h9,
                         "verdict_k5": vh, "verdict_k9": vh9,
                         "equal_k5": (h5["k"] == vh["k"] and rel_close(h5["alpha_k"], vh["alpha_k"])
                                      and h5["m"] == vh["m"] and all(
                             a["member"] == b["member"] and rel_close(a["p_value"], b["p_value"])
                             and rel_close(a["threshold"], b["threshold"]) and a["reject"] == b["reject"]
                             for a, b in zip(h5["rows"], vh["rows"], strict=True))),
                         "equal_k9": (h9["k"] == vh9["k"] and rel_close(h9["alpha_k"], vh9["alpha_k"])
                                      and all(a["reject"] == b["reject"] and rel_close(a["threshold"], b["threshold"])
                                              for a, b in zip(h9["rows"], vh9["rows"], strict=True)))}

    # ---- item 3: DSR, t, PBO
    run_members = [t["member"] for t in L["trials"] if t["member"] in series]
    a_series = [m for m in tier_a if m in series]
    moms = {m: my_moments(series[m][1].tolist()) for m in run_members}
    dsr_over = a_series if len(a_series) >= 2 else run_members
    var = statistics.pvariance([moms[m]["sharpe"] for m in dsr_over])
    sr0 = my_expected_max_sharpe(L["program_n"], var)
    dsr_vals = {m: my_dsr(moms[m], L["program_n"], var) for m in tier_a if m in moms}
    t_vals = {m: my_t(moms[m]) for m in tier_a if m in moms}
    # PBO: union of run trials' window dates, zeros off a trial's own dates
    union = sorted(set().union(*(set(series[m][0]) for m in run_members)))
    idx = {d: i for i, d in enumerate(union)}
    pbo_set = a_series if len(a_series) >= 2 else run_members
    aligned = {}
    for m in pbo_set:
        arr = np.zeros(len(union))
        for d, v in zip(series[m][0], series[m][1], strict=True):
            arr[idx[d]] = v
        aligned[m] = arr
    pb = my_pbo(aligned) if len(pbo_set) >= 2 else None
    vd, vp = V["edge_chain"]["dsr"], V["edge_chain"]["pbo"]
    vt = V["edge_chain"]["trials"]
    item3 = {"dsr_over": dsr_over, "sharpe_by_member": {m: moms[m]["sharpe"] for m in run_members},
             "moments_tier_a": {m: moms[m] for m in a_series},
             "sharpe_variance_pop": var, "expected_max_sharpe": sr0,
             "dsr": {m: d[0] for m, d in dsr_vals.items()}, "t_stat": t_vals,
             "pbo": pb, "pbo_over": pbo_set, "union_days": len(union),
             "verdict": {"dsr": vd, "pbo": vp, "trials": vt},
             "equal": {"variance_over": dsr_over == vd["variance_over"],
                       "sharpe_variance": rel_close(var, vd["sharpe_variance"]),
                       "expected_max": rel_close(sr0, vd["expected_max_daily_sharpe_under_null"]),
                       "dsr_per_tier_a": {m: rel_close(dsr_vals[m][0], vt[m]["dsr"]) for m in dsr_vals},
                       "t_per_tier_a": {m: rel_close(t_vals[m], vt[m]["t_stat"]) for m in t_vals},
                       "pbo_over": pbo_set == vp["over"],
                       "pbo": rel_close(pb["pbo"], vp["pbo"]) if pb else None,
                       "pbo_block_days": pb["block_days"] == vp["block_days"] if pb else None,
                       "pbo_n_splits": pb["n_splits"] == vp["n_splits"] if pb else None,
                       "pbo_winner_mean_oos": rel_close(pb["winner_mean_oos"], vp["winner_mean_oos_ticks_per_micro"]) if pb else None,
                       "pbo_p_winner_pos": rel_close(pb["p_winner_positive_oos"], vp["p_winner_positive_oos"]) if pb else None}}
    # second check with the program's functions (labelled)
    try:
        from funnel.multiple_comparisons import (deflated_sharpe_ratio, harvey_liu_zhu_verdict,
                                                 probability_of_backtest_overfitting)
        prog = {"dsr": {m: deflated_sharpe_ratio(moms[m]["sharpe"], moms[m]["n"], L["program_n"], var,
                                                 moms[m]["skew"], moms[m]["kurtosis"])["deflated_sharpe_ratio"]
                        for m in dsr_vals},
                "t": {m: harvey_liu_zhu_verdict(moms[m]["mean"], moms[m]["sd"], moms[m]["n"])["t_stat"]
                      for m in t_vals}}
        if pb:
            width = len(union) // N_BLOCKS
            matrix = [[float(aligned[m][b * width:(b + 1) * width].sum()) for b in range(N_BLOCKS)]
                      for m in pbo_set]
            prog["pbo"] = probability_of_backtest_overfitting(matrix, N_BLOCKS).pbo
        item3["program_second_check"] = prog
        item3["program_equals_mine"] = {
            "dsr": {m: rel_close(prog["dsr"][m], dsr_vals[m][0]) for m in dsr_vals},
            "t": {m: rel_close(prog["t"][m], t_vals[m]) for m in t_vals},
            "pbo": rel_close(prog.get("pbo"), pb["pbo"]) if pb else None}
    except Exception as exc:  # noqa: BLE001
        item3["program_second_check"] = f"failed: {exc}"
    out["items"]["3"] = item3

    # ---- item 4: chain verdict and statement (my own logic)
    chain = {}
    for m in tier_a:
        holm_rej = next(r["reject"] for r in h5["rows"] if r["member"] == m)
        d = dsr_vals.get(m, (None,))[0]
        tv = t_vals.get(m)
        p = pb["pbo"] if pb else None
        steps = {"holm": holm_rej, "dsr": d is not None and d > DSR_MIN,
                 "t": tv is not None and tv > T_MIN, "pbo": p is not None and p < PBO_MAX}
        failing = next((k for k in ("holm", "dsr", "t", "pbo") if not steps[k]), None)
        labels = next(t["labels"] for t in L["trials"] if t["member"] == m)
        if failing:
            verdict = "no edge"
        else:
            verdict = ("edge candidate, composite pending" + ("; source-overlap: no edge claim without a registered holdout read" if "source-overlap" in labels else ""))
        chain[m] = {"steps": steps, "first_failing": failing, "verdict": verdict,
                    "verdict_file": vt[m]["verdict"], "equal": vt[m]["verdict"] == verdict and vt[m]["first_failing_step"] == failing}
    # statement by NULL_CRITERIA_E 1, 6, 7 and L-E5-5
    covered, not_covered, blocking = [], [], []
    for t in L["trials"]:
        if not t["run"] or "inconclusive by design" in t["labels"]:
            not_covered.append(t["member"])
            continue
        covered.append(t["member"])
        st = item1[t["member"]]["mine"]["status"] if t["member"] in item1 else "inconclusive (no series)"
        if st not in ("null", "null by inactivity"):
            blocking.append({"member": t["member"], "status": st,
                             "record_status": records[t["member"]].get("status")})
    statement = "null" if covered and not blocking else "no statement"
    vs = V["statement"]
    # resolution table, my own
    resolution = []
    for veh in sorted({t["vehicle"] for t in L["trials"]}):
        trials = [t for t in L["trials"] if t["vehicle"] == veh]
        fig = [(t["member"], item1[t["member"]]["mine"]) for t in trials
               if t["member"] in covered and t["member"] in item1]
        fewest = min(fig, key=lambda x: (x[1]["n_trips"], x[0])) if fig else None
        largest = max(fig, key=lambda x: (x[1]["ucb95_per_trade"], x[0])) if fig else None
        resolution.append({"vehicle": veh, "q_c": trials[0]["q_c"], "eps_ticks": trials[0]["eps_ticks"],
                           "eps_usd": trials[0]["eps_usd_per_day_at_q"],
                           "fewest_trips": None if not fewest else {"member": fewest[0], "n_trips": fewest[1]["n_trips"]},
                           "largest_ucb95_per_trade": None if not largest else {"member": largest[0], "ticks": largest[1]["ucb95_per_trade"]},
                           "null_by_inactivity": [m for m, f in fig if f["status"] == "null by inactivity"],
                           "not_covered": [t["member"] for t in trials if t["member"] in not_covered]})
    vr = V["resolution"]
    res_equal = all(
        a["vehicle"] == b["vehicle"] and a["q_c"] == b["q_c"] and a["eps_ticks"] == b["eps_ticks"]
        and a["eps_usd"] == b["eps_usd_per_day_at_q"] and a["fewest_trips"] == b["fewest_trips"]
        and ((a["largest_ucb95_per_trade"] is None and b["largest_ucb95_per_trade"] is None) or
             (a["largest_ucb95_per_trade"]["member"] == b["largest_ucb95_per_trade"]["member"]
              and rel_close(a["largest_ucb95_per_trade"]["ticks"], b["largest_ucb95_per_trade"]["ticks"])))
        and a["null_by_inactivity"] == b["null_by_inactivity"] and a["not_covered"] == b["not_covered"]
        for a, b in zip(resolution, vr, strict=True))
    out["items"]["4"] = {"chain": chain, "statement_mine": statement, "statement_file": vs["verdict"],
                         "covered_mine": covered, "covered_file": vs["covered"],
                         "not_covered_mine": not_covered, "not_covered_file": [x["member"] for x in vs["not_covered"]],
                         "blocking_mine": blocking, "blocking_file": vs["blocking"],
                         "resolution_mine": resolution, "resolution_equal": res_equal,
                         "equal": statement == vs["verdict"] and covered == vs["covered"]
                         and not_covered == [x["member"] for x in vs["not_covered"]]
                         and [b["member"] for b in blocking] == [b["member"] for b in vs["blocking"]]}

    # ---- item 5: rebuild the Tier A daily series from trips and the cost table
    item5 = {}
    for m in a_series:
        r = records[m]
        trips_path = RUN_DIR / rec_name("K5", m).replace(".json", "_trips.json")
        T = json.loads(trips_path.read_text())
        veh = next(t["vehicle"] for t in L["trials"] if t["member"] == m)
        P = costs["products"][veh]
        bucket_lookup = {(b["start_min"], b["end_min"]): b["side_ticks"]["buy"] for b in P["buckets"]}

        def side_ticks_at(utc_text: str, _bl=bucket_lookup) -> float:
            minute = ct_minute(utc_text)
            for (s, e), v in _bl.items():
                if s <= minute < e:
                    return v
            raise KeyError(f"no bucket at CT minute {minute}")

        rb = rebuild_series(T["trips"], r["series"]["dates"], P["tick_value_usd"], P["commission_rt_usd"],
                            P["event_window_side_ticks"]["buy"], side_ticks_at)
        rebuilt = np.asarray([rb["daily"][d] for d in r["series"]["dates"]])
        recorded = np.asarray(r["series"]["values"], dtype=float)
        usd = np.asarray(r["daily_net_usd"], dtype=float)
        eps_row = next(x for x in eps_tab["exposures"] if x["vehicle"] == veh)
        gc = costs["products"]["GC"]
        item5[m] = {"vehicle": veh, "price_path": r["price_path"], "bars_path": r["bars"][veh]["path"],
                    "tick_value_usd_used_in_rebuild": P["tick_value_usd"],
                    "epsilon_table_tick_value": eps_row["tick_value_usd"], "epsilon_q_c": eps_row["q_c"],
                    "commission_rt_usd": P["commission_rt_usd"], "event_side_ticks": P["event_window_side_ticks"],
                    "gc_tick_value_usd": gc["tick_value_usd"], "gc_commission_rt_usd": gc["commission_rt_usd"],
                    "gc_event_side_ticks": gc["event_window_side_ticks"],
                    "n_trips_record": r["series"]["n_trips"], "n_trips_file": T["n_trips"],
                    "trips_dates_in_window": all(t["trade_date"] in idx or t["trade_date"] in set(r["series"]["dates"]) for t in T["trips"]),
                    "cost_match": {k: v for k, v in rb.items() if k != "daily"},
                    "series_equal_1e-9": bool(np.all(np.abs(rebuilt - recorded) <= 1e-9 * np.maximum(1.0, np.abs(recorded)))),
                    "max_abs_diff_ticks": float(np.max(np.abs(rebuilt - recorded))),
                    "daily_usd_equals_series_x_tick": bool(np.allclose(usd, recorded * P["tick_value_usd"], atol=1e-9)),
                    "gross_cents_all_multiple_of_tick_cents": rb["n_gross_on_tick_grid"] == len(T["trips"]),
                    "gross_cents_count_multiple_of_1000": sum(1 for t in T["trips"] if t["gross_cents"] % 1000 == 0),
                    "contracts": sorted({t["contracts"] for t in T["trips"]}),
                    "sum_net_usd_trips": sum(t["net_cents"] for t in T["trips"]) / 100,
                    "sum_series_ticks": float(recorded.sum())}
    out["items"]["5"] = item5

    # ---- item 6: contradictions between verdict JSON and list/records
    item6 = {"list_sha256_in_verdict": V["list_sha256"], "harness_equal": V["harness_sha256"] == L["harness_sha256"],
             "freeze_equal": V["cluster_freeze_sha256"] == L["cluster_freeze_sha256"],
             "k_holm_equal": V["k_holm"] == L["k_holm"], "program_n_equal": V["program_n"] == L["program_n"],
             "per_trial": {}}
    for t in L["trials"]:
        v = vtr[t["member"]]
        r = records.get(t["member"])
        checks = {"tier": v["tier"] == t["tier"], "run": v["run"] == t["run"], "labels": v["labels"] == t["labels"],
                  "ordinal": v["ordinal"] == t["ordinal"], "q_c": v["q_c"] == t["q_c"], "vehicle": v["vehicle"] == t["vehicle"],
                  "record_status": (r.get("status") if r else None) == v["record_status"],
                  "d4_power": v["d4_power"] == t["power"],
                  "eps": ("eps_ticks" not in v) or v["eps_ticks"] == t["eps_ticks"],
                  "covered_rule": v["covered"] == (t["run"] and "inconclusive by design" not in t["labels"])}
        if r and r.get("status") == "run" and "n_trips" in v:
            checks["n_trips_vs_record"] = v["n_trips"] == r["series"]["n_trips"]
            checks["n_days_vs_record"] = v["n_days"] == len(r["series"]["values"])
        item6["per_trial"][t["member"]] = [k for k, ok in checks.items() if not ok] or "all equal"
    out["items"]["6"] = item6

    OUT.write_text(json.dumps(out, indent=1, default=str))
    # ---- short summary
    print("item0 mismatches:", item0["mismatches"], "| records", item0["n_records"], "| list run:true", item0["n_list_run_true"],
          "| extra records", extra, "| marker sha ok", item0["marker_list_sha256_equals_list"])
    for m, d in item1.items():
        bad = [k for k, ok in d["equal"].items() if ok is not True and ok != "verdict: not used"]
        print(f"item1 {m}: status mine={d['mine']['status']} file={d['verdict']['status']} | theta={d['mine']['theta_hat']:.12g} ucb={d['mine']['ucb95']:.12g} se={d['mine']['se_boot']:.12g} p={d['mine']['p_upper']:.12g} pow={d['mine']['null_power']:.6g} | unequal: {bad}")
    print("item2 equal k5:", out["items"]["2"]["equal_k5"], "k9:", out["items"]["2"]["equal_k9"], "| pvals", pvals)
    print("item3 equal:", json.dumps(item3["equal"]), "| program==mine:", json.dumps(item3.get("program_equals_mine")))
    print(f"item3 var={var:.12g} sr0={sr0:.12g} dsr={ {m: d[0] for m, d in dsr_vals.items()} } t={t_vals} pbo={pb['pbo'] if pb else None} block={pb['block_days'] if pb else None}")
    print("item4 chain:", {m: (c['verdict'], c['equal']) for m, c in chain.items()}, "| statement mine/file:", statement, "/", vs["verdict"], "| equal", out["items"]["4"]["equal"], "| resolution equal", res_equal)
    print("item4 blocking mine:", blocking)
    for m, d in item5.items():
        print(f"item5 {m}: series equal {d['series_equal_1e-9']} maxdiff {d['max_abs_diff_ticks']} | cost match {d['cost_match']} | usd==ticks*tick {d['daily_usd_equals_series_x_tick']} | gross on tick grid {d['gross_cents_all_multiple_of_tick_cents']} | mult of 1000: {d['gross_cents_count_multiple_of_1000']}/{d['n_trips_file']} | tick {d['tick_value_usd_used_in_rebuild']} vs GC {d['gc_tick_value_usd']}")
    print("item6:", {k: v for k, v in item6.items() if k != "per_trial"}, "| per trial:", item6["per_trial"])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
