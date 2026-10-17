"""VerdictVerifier-K6 (Fable): independent recomputation of every K6 verdict figure.

Own code throughout (numpy, math, statistics). The only program function called is
funnel.null_generator.stationary_bootstrap_indices (the frozen generator), so that the
seeded draw sequence can be reproduced to 1e-9. funnel.multiple_comparisons is called
only as a second check, after the own formula, and the output says which is which.
Never imports or calls screening.stage_e_verdict.

Writes reports/stage_e22_briefs/verify_k6/figures.json and prints a short summary.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from datetime import date, datetime, timezone
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from funnel.null_generator import stationary_bootstrap_indices  # noqa: E402  (permitted)

LIST = REPO / "reports/stage_e22_k6_confirmation_list.json"
RUN = REPO / "reports/stage_e22_confirm_k6"
MARKER = REPO / "reports/stage_e22_K6_RUN_ONCE.json"
VERDICT = REPO / "reports/stage_e22_k6_verdict.json"
COSTS = REPO / "reports/stage_e2a_costs.json"
RELEASES = REPO / "reports/stage_e2b_release_calendar.json"
OUT = REPO / "reports/stage_e22_briefs/verify_k6/figures.json"
CT = ZoneInfo("America/Chicago")

B = 10_000
MEAN_BLOCK = 5.0
UCB_Q = 0.95
Z_NULL = 1.645
POWER_MIN = 0.80
INACTIVITY_MIN = 30
N_BLOCKS = 8
EVENT_WINDOW_MIN = 30  # D8: [release, release + 30 min); confirmed against the code constant
ND = statistics.NormalDist()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(a: float, b: float) -> float:
    if a == b:
        return 0.0
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


# ----------------------------------------------------------------- item 1 ----
def bootstrap_figures(values: np.ndarray, seed: int, eps: float, n_trips: int) -> dict:
    n = len(values)
    theta = float(values.mean())
    rng = np.random.default_rng(seed)
    means = np.empty(B)
    for i in range(B):
        idx = stationary_bootstrap_indices(rng, n, n, MEAN_BLOCK)
        means[i] = values[idx].mean()
    ucb = float(np.quantile(means, UCB_Q))
    se = float(np.std(means))  # ddof 0
    p_upper = (1 + int(np.sum((means - theta) >= theta))) / (B + 1)
    power = 0.0 if se <= 0 else ND.cdf(eps / se - Z_NULL)
    rate = n_trips / n
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
        status = "inconclusive"
    elif n_trips < INACTIVITY_MIN:
        status = "null by inactivity"
    else:
        status = "null"
    return {"n_days": n, "theta_hat": theta, "ucb95": ucb, "se_boot": se, "p_upper": p_upper,
            "null_power": power, "trips_per_day": rate, "n_trips": n_trips,
            "theta_per_trade": theta / rate if rate else None,
            "ucb95_per_trade": ucb / rate if rate else None, "status": status,
            "reasons": reasons, "ucb_below_eps": ucb < eps, "power_ok": power >= POWER_MIN}


# ----------------------------------------------------------------- item 3 ----
def own_moments(xs: np.ndarray) -> dict:
    n = len(xs)
    mean = float(xs.mean())
    sd = float(np.sqrt(np.mean((xs - mean) ** 2)))
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurtosis": 3.0, "sharpe": 0.0}
    skew = float(np.mean((xs - mean) ** 3) / sd**3)
    kurt = float(np.mean((xs - mean) ** 4) / sd**4)
    return {"n": n, "mean": mean, "sd": sd, "skew": skew, "kurtosis": kurt, "sharpe": mean / sd}


def own_expected_max_sharpe(n_trials: int, var: float) -> float:
    g = 0.5772156649015329
    return math.sqrt(var) * ((1 - g) * ND.inv_cdf(1 - 1 / n_trials)
                             + g * ND.inv_cdf(1 - 1 / (n_trials * math.e)))


def own_dsr(mom: dict, n_trials: int, var: float) -> float:
    sr = mom["sharpe"]
    em = own_expected_max_sharpe(n_trials, var)
    denom = 1 - mom["skew"] * sr + 0.25 * (mom["kurtosis"] - 1) * sr**2
    z = (sr - em) * math.sqrt(mom["n"] - 1) / math.sqrt(denom)
    return ND.cdf(z)


def own_t(mom: dict) -> float:
    return mom["mean"] / (mom["sd"] / math.sqrt(mom["n"]))


def own_blocks_floor(series: np.ndarray) -> list[float]:
    """D.1b convention: 8 blocks of n // 8 days each; the trailing n mod 8 days are dropped."""
    w = len(series) // N_BLOCKS
    return [float(series[b * w:(b + 1) * w].sum()) for b in range(N_BLOCKS)]


def own_blocks_split(series: np.ndarray) -> list[float]:
    """Sensitivity only: np.array_split (every day used, block widths differ by one)."""
    return [float(x.sum()) for x in np.array_split(series, N_BLOCKS)]


def own_cscv(matrix: list[list[float]]) -> dict:
    s_n = len(matrix)
    logits, oos_winner = [], []
    for train in combinations(range(N_BLOCKS), N_BLOCKS // 2):
        test = [b for b in range(N_BLOCKS) if b not in train]
        ins = [sum(row[b] for b in train) for row in matrix]
        oos = [sum(row[b] for b in test) for row in matrix]
        best = max(range(s_n), key=lambda s: ins[s])  # first maximum on ties
        worse = sum(1 for s in range(s_n) if oos[s] < oos[best])
        rank = min(max((worse + 0.5) / s_n, 1e-9), 1 - 1e-9)
        logits.append(math.log(rank / (1 - rank)))
        oos_winner.append(oos[best])
    return {"pbo": sum(1 for lg in logits if lg <= 0) / len(logits), "n_splits": len(logits),
            "winner_mean_oos": statistics.fmean(oos_winner),
            "p_winner_positive_oos": sum(1 for x in oos_winner if x > 0) / len(oos_winner)}


def own_holm(pvalues: dict[str, float], k: int) -> dict:
    alpha_k = 0.05 / k
    m = len(pvalues)
    order = sorted(pvalues.items(), key=lambda kv: (kv[1], kv[0]))
    rows, still = [], True
    for i, (member, p) in enumerate(order):
        thr = alpha_k / (m - i)
        reject = still and p <= thr
        if not reject:
            still = False
        rows.append({"member": member, "p_value": p, "rank": i + 1, "threshold": thr,
                     "reject": reject})
    return {"k": k, "alpha_k": alpha_k, "m": m, "rows": rows}


# ----------------------------------------------------------------- item 5 ----
def parse_cents(v) -> Fraction:
    return Fraction(v) if isinstance(v, str) else Fraction(int(v))


def ct_minute_of(utc_iso: str) -> int:
    dt = datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(CT)
    return dt.hour * 60 + dt.minute


def ct_hhmm(utc_iso: str) -> str:
    dt = datetime.fromisoformat(utc_iso.replace("Z", "+00:00")).astimezone(CT)
    return dt.strftime("%H:%M")


def bucket_side_ticks(product: dict, minute: int) -> tuple[str, float]:
    found = [b for b in product["buckets"] if b["start_min"] <= minute < b["end_min"]]
    if len(found) != 1:
        raise ValueError(f"no unique bucket at CT minute {minute}")
    return found[0]["key"], float(found[0]["side_ticks"]["buy"])  # buy == sell checked


def slippage_cents(qty: int, slip_ticks: float, tick_value_cents: int) -> int:
    return math.ceil(round(qty * slip_ticks * float(tick_value_cents), 6))


def rebuild_trips(trips: list[dict], product: dict, release_ns: np.ndarray) -> list[dict]:
    tv_cents = int(round(product["tick_value_usd"] * 100))
    comm_side = Fraction(str(product["commission_rt_usd"])) * 100 / 2
    event_ticks = float(product["event_window_side_ticks"]["buy"])
    out = []
    for t in trips:
        qty = int(t["contracts"])
        gross = parse_cents(t["gross_cents"])
        net = parse_cents(t["net_cents"])

        def side(ts_ns: int, utc: str, force: bool) -> tuple[int, str, str]:
            i = int(np.searchsorted(release_ns, ts_ns, side="right")) - 1
            in_rel = i >= 0 and ts_ns < release_ns[i] + EVENT_WINDOW_MIN * 60 * 10**9
            key, bticks = bucket_side_ticks(product, ct_minute_of(utc))
            if force or in_rel:
                return slippage_cents(qty, event_ticks, tv_cents), key, (
                    "event(price_limit_exit)" if force else "event(release)")
            return slippage_cents(qty, bticks, tv_cents), key, "bucket"

        e_slip, e_key, e_kind = side(t["open_ts_ns"], t["open_utc"], False)
        x_slip, x_key, x_kind = side(t["close_ts_ns"], t["close_utc"],
                                     t["close_reason"] == "price_limit_exit")
        cost = 2 * qty * comm_side + e_slip + x_slip
        net_rebuilt = gross - cost
        out.append({"trade_date": t["trade_date"], "entry_ct": ct_hhmm(t["open_utc"]),
                    "exit_ct": ct_hhmm(t["close_utc"]), "close_reason": t["close_reason"],
                    "contracts": qty, "gross_cents": str(gross), "net_cents_record": str(net),
                    "commission_cents": str(2 * qty * comm_side), "entry_bucket": e_key,
                    "entry_slip_cents": e_slip, "entry_kind": e_kind, "exit_bucket": x_key,
                    "exit_slip_cents": x_slip, "exit_kind": x_kind,
                    "net_cents_rebuilt": str(net_rebuilt), "match": net_rebuilt == net,
                    "gross_ticks": float(gross / tv_cents)})
    return out


# -------------------------------------------------------------------- main ----
def main() -> None:
    clist = json.loads(LIST.read_text())
    verdict = json.loads(VERDICT.read_text())
    marker = json.loads(MARKER.read_text())
    costs = json.loads(COSTS.read_text())["products"]
    cluster_rec = json.loads((RUN / "K6_confirmation_cluster.json").read_text())
    report: dict = {"list_sha256": sha256(LIST), "item0": {}, "trials": {}, "item2": {},
                    "item3": {}, "item4": {}, "item5": {}, "item6": []}

    # ---- item 0: inputs equal the hashed list -------------------------------
    i0 = report["item0"]
    i0["marker_list_sha256_equal"] = marker["list"]["sha256"] == report["list_sha256"]
    i0["marker_harness_equal"] = marker["harness_sha256"] == clist["harness_sha256"]
    i0["marker_freeze_equal"] = marker["cluster_freeze_sha256"] == clist["cluster_freeze_sha256"]
    i0["marker_members"] = marker["members"]
    i0["marker_not_run"] = marker["not_run"]
    run_trials = [t for t in clist["trials"] if t["run"]]
    i0["list_trials"] = len(clist["trials"])
    i0["list_run_trials"] = len(run_trials)
    rec_files = sorted(p.name for p in RUN.glob("K6_*_confirmation.json"))
    trip_files = sorted(p.name for p in RUN.glob("K6_*_confirmation_trips.json"))
    i0["record_files"] = len(rec_files)
    i0["trip_files"] = len(trip_files)
    expected = sorted(f"K6_{t['member'].replace(' ', '_')}_confirmation.json" for t in run_trials)
    i0["record_set_equals_run_trials"] = rec_files == expected
    i0["cluster_record_members_equal_list"] = (
        cluster_rec["members"] == [t["member"] for t in clist["trials"]]
        and cluster_rec["refused_members"] == {}
        and cluster_rec["harness_sha256"] == clist["harness_sha256"])
    field_mismatches = []
    records, trips_all = {}, {}
    for t in run_trials:
        name = f"K6_{t['member'].replace(' ', '_')}_confirmation"
        rec = json.loads((RUN / f"{name}.json").read_text())
        tr = json.loads((RUN / f"{name}_trips.json").read_text())
        records[t["member"]], trips_all[t["member"]] = rec, tr
        checks = {
            "harness": rec["harness_sha256"] == clist["harness_sha256"],
            "freeze": rec["cluster_freeze_sha256"] == clist["cluster_freeze_sha256"],
            "member": rec["member"] == t["member"],
            "ordinal": rec["ordinal"] == t["ordinal"],
            "window": rec["window"] == "confirmation",
            "s_x": rec["s_x"] == t["s_x"],
            "legs": [lg["root"] for lg in rec["legs"]] == t["legs"]
                    and all(lg["traded"] for lg in rec["legs"]),
            "price_path": rec["price_path"] == t["price_path"],
            "vehicle": rec["primary_vehicle"] == t["vehicle"] == rec["series"]["vehicle"],
            "status_run": rec["status"] == "run",
            "series_len": len(rec["series"]["dates"]) == len(rec["series"]["values"])
                          == rec["window_dates"]["n"],
            "series_dates_first_last": (rec["series"]["dates"][0] == rec["window_dates"]["first"]
                                        and rec["series"]["dates"][-1]
                                        == rec["window_dates"]["last"]),
            "window_within_list": (rec["window_dates"]["first"]
                                   >= max(clist["confirmation_window"][r][0] for r in t["legs"])
                                   and rec["window_dates"]["last"]
                                   <= min(clist["confirmation_window"][r][1] for r in t["legs"])),
            "excluded_not_in_series": not (set(rec["window_dates"]["excluded"]["roll_blackout_any_leg"])
                                           & set(rec["series"]["dates"])),
            "trips_record_sha": tr["record_sha256"] == sha256(RUN / f"{name}.json"),
            "trips_n": tr["n_trips"] == len(tr["trips"]) == rec["series"]["n_trips"]
                       == rec["trade_rate"]["n_trips"],
            "trips_member": tr["member"] == t["member"] and tr["status"] == "run",
            "unit": rec["series"]["unit"] == "net ticks per contract per day",
        }
        bad = [k for k, v in checks.items() if not v]
        if bad:
            field_mismatches.append({"member": t["member"], "failed": bad})
    i0["record_field_mismatches"] = field_mismatches
    i0["records_checked"] = len(records)

    # ---- item 1: per-trial figures ------------------------------------------
    vrows = {r["member"]: r for r in verdict["trials"]}
    series_np: dict[str, np.ndarray] = {}
    dates_map: dict[str, list[str]] = {}
    maxrel = {k: 0.0 for k in ("theta_hat", "ucb95", "se_boot", "p_upper", "null_power",
                               "trips_per_day", "theta_per_trade", "ucb95_per_trade")}
    status_mismatch = []
    for t in run_trials:
        rec = records[t["member"]]
        vals = np.asarray(rec["series"]["values"], dtype=float)
        series_np[t["member"]] = vals
        dates_map[t["member"]] = rec["series"]["dates"]
        seed_expected = clist["bootstrap"]["seed_base"] + t["ordinal"]
        mine = bootstrap_figures(vals, t["bootstrap_seed"], float(t["eps_ticks"]),
                                 rec["series"]["n_trips"])
        mine["seed"] = t["bootstrap_seed"]
        mine["seed_equals_base_plus_ordinal"] = t["bootstrap_seed"] == seed_expected
        mine["eps_ticks"] = float(t["eps_ticks"])
        v = vrows[t["member"]]
        cmp = {}
        for k in maxrel:
            a, b = mine[k], v.get(k)
            if a is None or b is None:
                cmp[k] = (a is None and b is None)
            else:
                d = rel(a, b)
                cmp[k] = d
                maxrel[k] = max(maxrel[k], d)
        cmp["n_days"] = mine["n_days"] == v["n_days"]
        cmp["n_trips"] = mine["n_trips"] == v["n_trips"]
        cmp["status"] = mine["status"] == v["status"]
        cmp["reasons"] = mine["reasons"] == v["reasons"]
        cmp["seed"] = mine["seed"] == v["seed"]
        cmp["eps"] = mine["eps_ticks"] == v["eps_ticks"]
        if not cmp["status"] or not cmp["reasons"]:
            status_mismatch.append(t["member"])
        report["trials"][t["member"]] = {"mine": mine, "verdict": {k: v.get(k) for k in (
            "n_days", "n_trips", "theta_hat", "ucb95", "se_boot", "p_upper", "null_power",
            "trips_per_day", "theta_per_trade", "ucb95_per_trade", "status", "reasons",
            "seed", "eps_ticks", "tier", "covered")}, "compare": cmp,
            "tier": t["tier"], "vehicle": t["vehicle"], "ordinal": t["ordinal"]}
    report["item1_max_rel_diff"] = maxrel
    report["item1_status_mismatch"] = status_mismatch

    # ---- item 2: Holm ---------------------------------------------------------
    tier_a = [t["member"] for t in clist["trials"] if t["tier"] == "A"]
    pvals = {m: (report["trials"][m]["mine"]["p_upper"] if m in report["trials"] else 1.0)
             for m in tier_a}
    h5 = own_holm(pvals, clist["k_holm"])
    h9 = own_holm(pvals, 9)
    report["item2"] = {"tier_a": tier_a, "pvalues": pvals, "holm_k5": h5, "holm_k9": h9,
                       "verdict_holm": verdict["edge_chain"]["holm"],
                       "verdict_holm_k9": verdict["edge_chain"]["holm_descriptive_k9"]}

    # ---- item 3: DSR, t, PBO -------------------------------------------------
    run_members = [t["member"] for t in run_trials]
    moms = {m: own_moments(series_np[m]) for m in run_members}
    a_series = [m for m in tier_a if m in series_np]
    var_over = a_series if len(a_series) >= 2 else run_members
    sharpes = [moms[m]["sharpe"] for m in var_over]
    var = float(np.mean((np.asarray(sharpes) - np.mean(sharpes)) ** 2))  # population variance
    em = own_expected_max_sharpe(clist["program_n"], var)
    dsr_vals = {m: own_dsr(moms[m], clist["program_n"], var) for m in a_series}
    t_vals = {m: own_t(moms[m]) for m in a_series}
    # PBO over every run trial (one Tier A series), aligned on the union of window dates
    union = sorted(set().union(*(set(d) for d in dates_map.values())))
    idx = {d: i for i, d in enumerate(union)}
    aligned = {}
    for m in run_members:
        arr = np.zeros(len(union))
        for d, v in zip(dates_map[m], series_np[m], strict=True):
            arr[idx[d]] = v
        aligned[m] = arr
    pbo_set = a_series if len(a_series) >= 2 else run_members
    mat_floor = [own_blocks_floor(aligned[m]) for m in pbo_set]
    mat_split = [own_blocks_split(aligned[m]) for m in pbo_set]
    pbo_floor = own_cscv(mat_floor)
    pbo_split = own_cscv(mat_split)
    # second check with the program's functions
    from funnel.multiple_comparisons import (deflated_sharpe_ratio,  # noqa: E402
                                             harvey_liu_zhu_verdict,
                                             probability_of_backtest_overfitting)
    prog_dsr = {m: deflated_sharpe_ratio(moms[m]["sharpe"], moms[m]["n"], clist["program_n"],
                                         var, moms[m]["skew"], moms[m]["kurtosis"])
                for m in a_series}
    prog_t = {m: harvey_liu_zhu_verdict(moms[m]["mean"], moms[m]["sd"], moms[m]["n"])["t_stat"]
              for m in a_series}
    prog_pbo = probability_of_backtest_overfitting(mat_floor, N_BLOCKS)
    vd = verdict["edge_chain"]["dsr"]
    vp = verdict["edge_chain"]["pbo"]
    vt = verdict["edge_chain"]["trials"]
    report["item3"] = {
        "moments_tier_a": {m: moms[m] for m in a_series},
        "variance_over_n": len(var_over), "variance_over_equals_verdict": var_over == vd["variance_over"],
        "sharpe_variance_mine": var, "sharpe_variance_verdict": vd["sharpe_variance"],
        "sharpe_variance_rel": rel(var, vd["sharpe_variance"]),
        "expected_max_mine": em, "expected_max_verdict": vd["expected_max_daily_sharpe_under_null"],
        "expected_max_rel": rel(em, vd["expected_max_daily_sharpe_under_null"]),
        "dsr_mine": dsr_vals, "dsr_program_fn": {m: prog_dsr[m]["deflated_sharpe_ratio"] for m in a_series},
        "dsr_verdict": {m: vt[m]["dsr"] for m in a_series},
        "dsr_rel": {m: rel(dsr_vals[m], vt[m]["dsr"]) for m in a_series},
        "dsr_z": {m: prog_dsr[m]["z"] for m in a_series},
        "t_mine": t_vals, "t_program_fn": prog_t, "t_verdict": {m: vt[m]["t_stat"] for m in a_series},
        "t_rel": {m: rel(t_vals[m], vt[m]["t_stat"]) for m in a_series},
        "union_days": len(union), "union_first": union[0], "union_last": union[-1],
        "block_days_floor": len(union) // N_BLOCKS, "dropped_tail_days": len(union) % N_BLOCKS,
        "dropped_tail_dates": union[(len(union) // N_BLOCKS) * N_BLOCKS:],
        "pbo_set_n": len(pbo_set), "pbo_set_equals_verdict": pbo_set == vp["over"],
        "pbo_mine_floor": pbo_floor, "pbo_program_fn_floor": prog_pbo.pbo,
        "pbo_verdict": {k: vp[k] for k in ("pbo", "n_splits", "n_days", "block_days", "n_strategies",
                                           "window_days", "winner_mean_oos_ticks_per_micro",
                                           "p_winner_positive_oos", "degenerate", "undefined")},
        "pbo_sensitivity_array_split": pbo_split,
        "sharpes_by_member": {m: moms[m]["sharpe"] for m in run_members},
    }

    # ---- item 4: chain verdict and statement ----------------------------------
    chain = {}
    for m in tier_a:
        holm_pass = any(r["reject"] for r in h5["rows"] if r["member"] == m)
        d_pass = m in dsr_vals and dsr_vals[m] > 0.95
        t_pass = m in t_vals and t_vals[m] > 3.0
        p_pass = pbo_floor["pbo"] < 0.5
        steps = [("holm", holm_pass), ("dsr", d_pass), ("t", t_pass), ("pbo", p_pass)]
        first_fail = next((s for s, ok in steps if not ok), None)
        all_pass = all(ok for _, ok in steps)
        wording = "edge candidate, composite pending" if all_pass else "no edge"
        chain[m] = {"passes": dict(steps), "first_failing_step": first_fail, "verdict": wording,
                    "verdict_file": vt[m]["verdict"], "verdict_file_first_fail": vt[m]["first_failing_step"],
                    "verdict_file_passes": vt[m]["passes"]}
    my_status = {m: report["trials"][m]["mine"]["status"] for m in run_members}
    covered = [t["member"] for t in clist["trials"]
               if t["run"] and "inconclusive by design" not in t["labels"]]
    blocking = [m for m in covered if my_status[m] not in ("null", "null by inactivity")]
    statement = "null" if covered and not blocking else "no statement"
    inactivity = [m for m in covered if my_status[m] == "null by inactivity"]
    resolution = []
    for veh in sorted({t["vehicle"] for t in clist["trials"]}):
        ts = [t for t in clist["trials"] if t["vehicle"] == veh]
        fig = [(report["trials"][t["member"]]["mine"] | {"member": t["member"]})
               for t in ts if t["member"] in covered]
        fewest = min(fig, key=lambda r: (r["n_trips"], r["member"]))
        pt = [r for r in fig if r["ucb95_per_trade"] is not None]
        largest = max(pt, key=lambda r: (r["ucb95_per_trade"], r["member"])) if pt else None
        resolution.append({"vehicle": veh, "q_c": ts[0]["q_c"], "eps_ticks": float(ts[0]["eps_ticks"]),
                           "eps_usd_per_day_at_q": ts[0]["eps_usd_per_day_at_q"],
                           "fewest_trips": {"member": fewest["member"], "n_trips": fewest["n_trips"]},
                           "largest_ucb95_per_trade": None if largest is None else {
                               "member": largest["member"], "ticks": largest["ucb95_per_trade"]},
                           "null_by_inactivity": [r["member"] for r in fig if r["status"] == "null by inactivity"],
                           "not_covered": [t["member"] for t in ts if t["member"] not in covered]})
    vres = {r["vehicle"]: r for r in verdict["resolution"]}
    res_cmp = []
    for r in resolution:
        v = vres[r["vehicle"]]
        ok = (r["q_c"] == v["q_c"] and r["eps_ticks"] == v["eps_ticks"]
              and r["eps_usd_per_day_at_q"] == v["eps_usd_per_day_at_q"]
              and r["fewest_trips"] == v["fewest_trips"]
              and r["null_by_inactivity"] == v["null_by_inactivity"]
              and r["not_covered"] == v["not_covered"]
              and (r["largest_ucb95_per_trade"] is None) == (v["largest_ucb95_per_trade"] is None)
              and (r["largest_ucb95_per_trade"] is None or (
                  r["largest_ucb95_per_trade"]["member"] == v["largest_ucb95_per_trade"]["member"]
                  and rel(r["largest_ucb95_per_trade"]["ticks"], v["largest_ucb95_per_trade"]["ticks"]) < 1e-9)))
        res_cmp.append({"vehicle": r["vehicle"], "equal": ok})
    vs = verdict["statement"]
    report["item4"] = {
        "chain": chain, "statement_mine": statement, "statement_verdict": vs["verdict"],
        "covered_mine_n": len(covered), "covered_equal": covered == vs["covered"],
        "blocking_mine": blocking, "blocking_verdict": [b["member"] for b in vs["blocking"]],
        "blocking_reasons_verdict": {b["member"]: b["reasons"] for b in vs["blocking"]},
        "inactivity_mine": inactivity, "inactivity_verdict": vs["null_by_inactivity"],
        "not_covered_verdict": vs["not_covered"], "resolution_mine": resolution,
        "resolution_compare": res_cmp,
        "edge_word_scan": sorted({k for k in json.dumps(verdict).split('"')
                                  if k.strip().lower() in ("edge", "edge exists")}),
    }

    # ---- item 5: trip rebuild (K6-limitcont-01 HE in full; daily sums for all) --
    rel_cal = json.loads(RELEASES.read_text())
    he_rel = sorted(int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
                        .timestamp() * 10**9) for r in rel_cal["releases"] if "HE" in r["products"])
    he_rel_ns = np.asarray(he_rel, dtype=np.int64)
    lim = "K6-limitcont-01 HE"
    tr = trips_all[lim]["trips"]
    rebuilt = rebuild_trips(tr, costs["HE"], he_rel_ns)
    tv_he = int(round(costs["HE"]["tick_value_usd"] * 100))
    daily: dict[str, Fraction] = {}
    for t in tr:
        daily[t["trade_date"]] = daily.get(t["trade_date"], Fraction(0)) + parse_cents(t["net_cents"]) / int(t["contracts"])
    rec = records[lim]
    series_rebuilt = [float(daily.get(d, Fraction(0)) / tv_he) for d in rec["series"]["dates"]]
    diffs = np.abs(np.asarray(series_rebuilt) - np.asarray(rec["series"]["values"], dtype=float))
    report["item5"] = {
        "member": lim, "he_release_instants": len(he_rel), "trips": rebuilt,
        "all_net_match": all(r["match"] for r in rebuilt),
        "trip_dates_in_series_dates": all(t["trade_date"] in set(rec["series"]["dates"]) for t in tr),
        "trip_dates_not_excluded": not (set(t["trade_date"] for t in tr)
                                        & set(rec["window_dates"]["excluded"]["roll_blackout_any_leg"])),
        "series_max_abs_diff": float(diffs.max()), "series_nonzero_days": int(np.count_nonzero(series_rebuilt)),
        "series_mean_rebuilt": float(np.mean(series_rebuilt)),
        "daily_net_usd_consistent": all(abs(float(daily.get(d, Fraction(0))) / 100 - u) < 1e-9
                                        for d, u in zip(rec["series"]["dates"], rec["daily_net_usd"], strict=True)),
        "tick_value_usd": costs["HE"]["tick_value_usd"], "commission_rt_usd": costs["HE"]["commission_rt_usd"],
        "engine_counters": rec["engine"]["counters"],
        "close_reason_counts": {r: sum(1 for t in tr if t["close_reason"] == r)
                                for r in sorted({t["close_reason"] for t in tr})},
    }
    # daily-sum reproduction for every run trial (cost model not re-applied here)
    daily_all = {}
    for m in run_members:
        t_list = trips_all[m]["trips"]
        legs = [lg["root"] for lg in records[m]["legs"]]
        primary = records[m]["primary_vehicle"]
        tvp = int(round(costs[primary]["tick_value_usd"] * 100))
        q_c = next(t["q_c"] for t in clist["trials"] if t["member"] == m)
        dd: dict[str, Fraction] = {}
        for t in t_list:
            if len(legs) == 1:
                dd[t["trade_date"]] = dd.get(t["trade_date"], Fraction(0)) + parse_cents(t["net_cents"]) / int(t["contracts"])
            else:  # multi-leg: combined net dollars / (q_X x tick value of the primary leg)
                dd[t["trade_date"]] = dd.get(t["trade_date"], Fraction(0)) + parse_cents(t["net_cents"]) / q_c
        reb = np.asarray([float(dd.get(d, Fraction(0)) / tvp) for d in records[m]["series"]["dates"]])
        mx = float(np.abs(reb - series_np[m]).max())
        stray = sorted(set(dd) - set(records[m]["series"]["dates"]))
        contracts = sorted({int(t["contracts"]) for t in t_list})
        roots = sorted({t["root"] for t in t_list})
        daily_all[m] = {"max_abs_diff": mx, "trips": len(t_list), "trip_dates_outside_series": stray,
                        "contracts_seen": contracts, "roots_seen": roots, "legs": legs}
    report["item5_daily_sums_all"] = daily_all
    report["item5_daily_sums_all_max"] = max(v["max_abs_diff"] for v in daily_all.values())

    # ---- item 6: verdict JSON vs list and records ------------------------------
    i6 = report["item6"]
    if verdict["list_sha256"] != report["list_sha256"]:
        i6.append("verdict list_sha256 differs from the list file's sha256")
    if verdict["harness_sha256"] != clist["harness_sha256"]:
        i6.append("verdict harness_sha256 differs from the list")
    if verdict["cluster_freeze_sha256"] != clist["cluster_freeze_sha256"]:
        i6.append("verdict cluster_freeze_sha256 differs from the list")
    if verdict["k_holm"] != clist["k_holm"] or verdict["program_n"] != clist["program_n"]:
        i6.append("verdict k_holm or program_n differs from the list")
    c = verdict["constants"]
    lb = clist["bootstrap"]
    if not (c["seed_base"] == lb["seed_base"] and c["resamples"] == lb["resamples"]
            and c["mean_block"] == lb["mean_block"] and c["ucb_quantile"] == lb["ucb_quantile"]):
        i6.append("verdict constants differ from the list's bootstrap block")
    for t in clist["trials"]:
        v = vrows[t["member"]]
        rec = records.get(t["member"])
        probs = []
        if v["ordinal"] != t["ordinal"]: probs.append("ordinal")
        if v["vehicle"] != t["vehicle"]: probs.append("vehicle")
        if v["tier"] != t["tier"]: probs.append("tier")
        if v["q_c"] != t["q_c"]: probs.append("q_c")
        if v["labels"] != t["labels"]: probs.append("labels")
        if v["run"] != t["run"]: probs.append("run")
        if v["seed"] != t["bootstrap_seed"]: probs.append("seed")
        if float(v["eps_ticks"]) != float(t["eps_ticks"]): probs.append("eps_ticks")
        if v["d4_power"] != t["power"]: probs.append("d4_power vs list power")
        if v["covered"] != (t["run"] and "inconclusive by design" not in t["labels"]): probs.append("covered")
        if rec is not None:
            if v["n_days"] != rec["window_dates"]["n"]: probs.append("n_days vs record")
            if v["n_trips"] != rec["series"]["n_trips"]: probs.append("n_trips vs record")
            if v["record_status"] != rec["status"]: probs.append("record_status")
        if probs:
            i6.append(f"{t['member']}: {', '.join(probs)}")
    if verdict["edge_chain"]["composite"] != "pending":
        i6.append("composite is not 'pending'")
    if set(verdict["statement"]["covered"]) != set(covered):
        i6.append("statement.covered differs from the list's covered trials")

    OUT.write_text(json.dumps(report, indent=1, default=str))
    # ---- short summary --------------------------------------------------------
    print("item0:", {k: v for k, v in i0.items() if k != "record_field_mismatches"},
          "mismatches:", i0["record_field_mismatches"])
    print("item1 max rel diffs:", {k: f"{v:.2e}" for k, v in maxrel.items()},
          "status mismatches:", status_mismatch)
    print("item2 holm k5:", h5["rows"], "| verdict:", verdict["edge_chain"]["holm"]["rows"])
    print("item2 holm k9 thr:", h9["rows"][0]["threshold"], "| verdict:",
          verdict["edge_chain"]["holm_descriptive_k9"]["rows"][0]["threshold"])
    i3 = report["item3"]
    print("item3 var:", i3["sharpe_variance_mine"], i3["sharpe_variance_verdict"], f"rel {i3['sharpe_variance_rel']:.2e}",
          "| EM:", i3["expected_max_mine"], i3["expected_max_verdict"], f"rel {i3['expected_max_rel']:.2e}")
    print("item3 dsr:", i3["dsr_mine"], i3["dsr_program_fn"], i3["dsr_verdict"], {m: f"{x:.2e}" for m, x in i3["dsr_rel"].items()})
    print("item3 t:", i3["t_mine"], i3["t_program_fn"], i3["t_verdict"], {m: f"{x:.2e}" for m, x in i3["t_rel"].items()})
    print("item3 union days:", i3["union_days"], "block", i3["block_days_floor"], "dropped tail", i3["dropped_tail_dates"])
    print("item3 pbo mine(floor):", i3["pbo_mine_floor"], "| program fn:", i3["pbo_program_fn_floor"],
          "| verdict:", i3["pbo_verdict"])
    print("item3 pbo sensitivity (array_split):", i3["pbo_sensitivity_array_split"])
    print("item4 chain:", chain)
    print("item4 statement:", statement, "|", vs["verdict"], "| covered equal:", report["item4"]["covered_equal"],
          "| blocking:", blocking, vs["blocking"][0]["member"] if vs["blocking"] else None,
          "| inactivity:", inactivity, vs["null_by_inactivity"], "| resolution:", res_cmp,
          "| edge words:", report["item4"]["edge_word_scan"])
    i5 = report["item5"]
    print("item5 all_net_match:", i5["all_net_match"], "series max abs diff:", i5["series_max_abs_diff"],
          "dates ok:", i5["trip_dates_in_series_dates"], i5["trip_dates_not_excluded"],
          "daily_net_usd consistent:", i5["daily_net_usd_consistent"], "HE releases:", i5["he_release_instants"])
    for r in rebuilt:
        print("  ", r["trade_date"], r["entry_ct"], r["exit_ct"], r["close_reason"], r["gross_cents"],
              r["net_cents_record"], r["net_cents_rebuilt"], r["entry_bucket"], r["entry_slip_cents"], r["entry_kind"],
              r["exit_bucket"], r["exit_slip_cents"], r["exit_kind"], "MATCH" if r["match"] else "DIFF")
    print("item5 daily sums all trials: max abs diff", report["item5_daily_sums_all_max"],
          "stray dates:", {m: v["trip_dates_outside_series"] for m, v in daily_all.items() if v["trip_dates_outside_series"]},
          "contracts:", sorted({c for v in daily_all.values() for c in v["contracts_seen"]}))
    print("item6:", i6 if i6 else "none")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
