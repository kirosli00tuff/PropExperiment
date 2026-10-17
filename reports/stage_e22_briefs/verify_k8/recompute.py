#!/usr/bin/env python3
"""VerdictVerifier-K8 (Fable 5.1, xhigh): independent recomputation of reports/stage_e22_k8_verdict.json.

Items 0-4 and 6 of reports/stage_e22_briefs/brief_verdict_verify.md. Own numpy / math / statistics
code. The one program function called for a figure is funnel.null_generator.stationary_bootstrap_indices
(the frozen generator NULL_CRITERIA_E 3 names). funnel.multiple_comparisons is called AFTERWARDS as a
labelled second check. Nothing under screening/ is imported or run. No bar data is read.

Outputs: figures.json and recompute.log beside this file. Read-only otherwise.
"""
from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from funnel.null_generator import stationary_bootstrap_indices  # noqa: E402  (frozen generator, allowed)
from funnel import multiple_comparisons as mc  # noqa: E402  (second check only)

OUT_DIR = REPO / "reports/stage_e22_briefs/verify_k8"
LIST = REPO / "reports/stage_e22_k8_confirmation_list.json"
VERDICT = REPO / "reports/stage_e22_k8_verdict.json"
RUN_DIR = REPO / "reports/stage_e22_confirm_k8"
MARKER = REPO / "reports/stage_e22_K8_RUN_ONCE.json"
NOTRUN = REPO / "reports/stage_e22_notrun_K8.json"
EPSILON = REPO / "reports/stage_e2a_epsilon.json"
LEDGER = REPO / "ledger/trial_registrations.jsonl"
FROZEN_FILES = {
    "costs": REPO / "reports/stage_e2a_costs.json",
    "epsilon": REPO / "reports/stage_e2a_epsilon.json",
    "sizes": REPO / "reports/stage_e2a_vehicle_sizes.json",
    "vehicles": REPO / "reports/stage_e2a_vehicles.json",
}
RELEASE_CAL = REPO / "reports/stage_e2b_release_calendar.json"
COMMIT_LIST_SHA = "28ad6f63630681dbb1baeb14d0384f5fbfd6c794c160d32d9380166d3d039ca5"  # ccd7fa7 message
HARNESS_V13 = "dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4"

# Criteria constants (NULL_CRITERIA_E 3, 6; D5; the E.22 rulings)
SEED_BASE = 20260923
B = 10_000
MEAN_BLOCK = 5.0
UCB_Q = 0.95
NULL_Z = 1.645
POWER_MIN = 0.80
INACTIVITY_MIN = 30
T_MIN = 3.0
DSR_MIN = 0.95
PBO_BLOCKS = 8
PBO_MAX = 0.5
K_HOLM = 5  # R-E22-A10
K_DESCRIPTIVE = 9  # V14 (b), descriptive only
PROGRAM_N = 533  # R-E22-A11
REL_TOL = 1e-9

ND = statistics.NormalDist()
LOG: list[str] = []
CHECKS: list[dict] = []


def log(msg: str) -> None:
    LOG.append(msg)
    print(msg)


def check(name: str, ok: bool, detail: str = "") -> bool:
    CHECKS.append({"check": name, "ok": bool(ok), "detail": detail})
    log(f"{'PASS' if ok else 'FAIL'} {name}" + (f": {detail}" if detail else ""))
    return bool(ok)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(a: float, b: float) -> float:
    if a == b:
        return 0.0
    den = max(abs(a), abs(b))
    return abs(a - b) / den if den else float("inf")


def close(a, b, tol=REL_TOL) -> bool:
    if a is None or b is None:
        return a is b
    return rel(float(a), float(b)) <= tol


def load(path: Path):
    return json.loads(path.read_text())


def record_name(member: str) -> str:
    return f"K8_{member.replace(' ', '_')}_confirmation.json"


# ----------------------------------------------------------------------------------------------
# Item 0: the run's inputs equal the hashed list
# ----------------------------------------------------------------------------------------------
def item0(lst, verdict, marker, notrun, records):
    log("== Item 0: run inputs equal the hashed list")
    list_sha = sha256(LIST)
    check("0.1 list sha256 equals commit ccd7fa7's figure", list_sha == COMMIT_LIST_SHA, list_sha)
    check("0.2 marker names this list and sha", marker["list"]["path"].endswith("stage_e22_k8_confirmation_list.json")
          and marker["list"]["sha256"] == list_sha, json.dumps(marker["list"]))
    check("0.3 verdict carries the list's name and sha", verdict["list_file"] == LIST.name and verdict["list_sha256"] == list_sha)
    check("0.4 list harness = v13 and marker/verdict harness equal it",
          lst["harness_sha256"] == HARNESS_V13 == marker["harness_sha256"] == verdict["harness_sha256"])
    check("0.5 cluster_freeze_sha256 equal in list, marker, verdict",
          lst["cluster_freeze_sha256"] == marker["cluster_freeze_sha256"] == verdict["cluster_freeze_sha256"])
    notrun_sha = sha256(NOTRUN)
    check("0.6 marker not_run declaration sha equals the file", marker["not_run_declaration"]["sha256"] == notrun_sha, notrun_sha)
    declared = {m: v["label"] for m, v in notrun["members"].items()}
    listed_not_run = [t["member"] for t in lst["trials"] if not t["run"]]
    check("0.7 marker not_run = list's run:false trials = declaration members",
          sorted(marker["not_run"]) == sorted(listed_not_run) == sorted(declared), f"{listed_not_run}")
    check("0.8 marker members = 4 = list trials", marker["members"] == len(lst["trials"]) == 4)

    present = sorted(p.name for p in RUN_DIR.glob("*_confirmation.json"))
    expected = sorted(record_name(t["member"]) for t in lst["trials"])
    check("0.9 record set = exactly the list's trials (run + the one declared not-run record)", present == expected,
          f"present {len(present)}, expected {len(expected)}")

    frozen_sha = {k: sha256(p) for k, p in FROZEN_FILES.items()}
    cal_sha = sha256(RELEASE_CAL)
    for t in lst["trials"]:
        m = t["member"]
        r = records[m]
        tag = f"0.rec[{t['ordinal']}] {m}"
        check(f"{tag}: harness/freeze/member/ordinal/window/cluster",
              r["harness_sha256"] == lst["harness_sha256"] and r["cluster_freeze_sha256"] == lst["cluster_freeze_sha256"]
              and r["member"] == m and r["ordinal"] == t["ordinal"] and r["window"] == "confirmation" and r["cluster"] == "K8")
        check(f"{tag}: legs roots (and order) equal the list", [lg["root"] for lg in r["legs"]] == t["legs"], f"{t['legs']}")
        check(f"{tag}: primary vehicle equals the list's vehicle", r["primary_vehicle"] == t["vehicle"])
        check(f"{tag}: seed = 20260923 + ordinal in the list", t["bootstrap_seed"] == SEED_BASE + t["ordinal"], str(t["bootstrap_seed"]))
        if t["run"]:
            check(f"{tag}: status run", r["status"] == "run", r["status"])
            check(f"{tag}: s_x equals the list's s_x", r["s_x"] == t["s_x"], json.dumps(r["s_x"]))
            check(f"{tag}: s_x equals the list's start_dates for each leg",
                  all(r["s_x"][leg] == lst["start_dates"][leg] for leg in t["legs"]))
            check(f"{tag}: price_path equals the list", r["price_path"] == t["price_path"], json.dumps(r["price_path"]))
            check(f"{tag}: price-path declaration sha equals reports/stage_e22_price_paths.json",
                  r["price_path_declaration"]["sha256"] == sha256(REPO / "reports/stage_e22_price_paths.json"))
            check(f"{tag}: labels equal the list", r["labels"] == t["labels"])
            check(f"{tag}: frozen tables (costs, epsilon, sizes, vehicles) equal the files' sha256 now",
                  all(r["frozen_tables"][k] == frozen_sha[k] for k in frozen_sha))
            check(f"{tag}: release calendar sha equals reports/stage_e2b_release_calendar.json",
                  r["release_calendar_sha256"] == cal_sha)
            # bars / stores
            for leg in t["legs"]:
                path_root = t["price_path"].get(leg, leg)
                bar = r["bars"][leg]
                check(f"{tag}: {leg} bars file is {path_root}'s store and matches the marker's store hash",
                      path_root in bar["path"] and any(s[0] == leg and s[1] == bar["path"] and s[2] == bar["sha256"] for s in marker["stores"]),
                      bar["path"])
            # window: intersection of the legs' windows, inside the list's confirmation_window
            w = r["window_dates"]
            s_max = max(t["s_x"].values())
            check(f"{tag}: window inside [max S_X over legs, 2024-02-29] and n = len(series)",
                  w["first"] >= s_max and w["last"] <= "2024-02-29" and w["n"] == len(r["series"]["dates"]) == len(r["series"]["values"]),
                  f"first {w['first']} last {w['last']} n {w['n']} (max S_X {s_max})")
            check(f"{tag}: series dates = window dates (first/last) and unit is net ticks per contract per day",
                  r["series"]["dates"][0] == w["first"] and r["series"]["dates"][-1] == w["last"]
                  and r["series"]["unit"] == "net ticks per contract per day" and r["series"]["vehicle"] == t["vehicle"])
            dates_before_first = [d for d in t["s_x"].values()]
            excl = w["excluded"]
            gap = [d for d in [s_max] if d < w["first"]]
            if gap:
                where = [k for k, v in excl.items() if s_max in v]
                check(f"{tag}: S_X date {s_max} precedes window first {w['first']}; excluded under {where}", bool(where), str(where))
            trips_path = RUN_DIR / record_name(m).replace("_confirmation.json", "_confirmation_trips.json")
            tr = load(trips_path)
            check(f"{tag}: trips file binds to the record (record_sha256) and n_trips agree",
                  tr["record_sha256"] == sha256(RUN_DIR / record_name(m)) and tr["n_trips"] == len(tr["trips"]) == r["series"]["n_trips"] == r["trade_rate"]["n_trips"],
                  f"n_trips {tr['n_trips']}")
        else:
            check(f"{tag}: not-run record status not_run and carries exactly the declared label",
                  r["status"] == "not_run" and r["labels"] == [declared[m]], f"record labels {r['labels']}, declared {declared[m]!r}, list labels {t['labels']}")
            check(f"{tag}: not-run record names the declaration file and sha", r["not_run_declaration"]["sha256"] == notrun_sha)
            check(f"{tag}: not-run record has no series", r["series"] is None)
            check(f"{tag}: list labels include the declared label", declared[m] in t["labels"], f"{t['labels']}")
    return {"list_sha256": list_sha, "notrun_sha256": notrun_sha, "frozen_sha": frozen_sha, "release_calendar_sha": cal_sha}


# ----------------------------------------------------------------------------------------------
# Item 1: per run trial
# ----------------------------------------------------------------------------------------------
def bootstrap(values: np.ndarray, seed: int):
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(B)
    for b in range(B):
        idx = stationary_bootstrap_indices(rng, n, n, MEAN_BLOCK)
        means[b] = values[idx].mean()
    theta = float(values.mean())
    ucb = float(np.quantile(means, UCB_Q))
    se = float(np.std(means))  # ddof 0
    p_shift = (1 + int(np.sum((means - theta) >= theta))) / (B + 1)
    p_le0 = (1 + int(np.sum(means <= 0.0))) / (B + 1)
    return theta, ucb, se, p_shift, p_le0


def item1(lst, verdict, records, eps_table):
    log("== Item 1: per run trial")
    vrows = {t["member"]: t for t in verdict["trials"]}
    out = {}
    for t in lst["trials"]:
        if not t["run"]:
            continue
        m = t["member"]
        r = records[m]
        v = vrows[m]
        vals = np.asarray(r["series"]["values"], dtype=float)
        n_days = len(vals)
        n_trips = int(r["series"]["n_trips"])
        eps = float(t["eps_ticks"])
        theta, ucb, se, p_shift, p_le0 = bootstrap(vals, SEED_BASE + t["ordinal"])
        rate = n_trips / n_days
        power = ND.cdf(eps / se - NULL_Z) if se > 0 else None
        if n_trips == 0 or se == 0:
            status = "inconclusive"
        elif ucb < eps and power >= POWER_MIN:
            status = "null by inactivity" if n_trips < INACTIVITY_MIN else "null"
        else:
            status = "inconclusive"
        mine = {
            "ordinal": t["ordinal"], "member": m, "tier": t["tier"], "eps_ticks": eps, "seed": SEED_BASE + t["ordinal"],
            "n_days": n_days, "n_trips": n_trips, "theta_hat": theta, "ucb95": ucb, "se_boot": se,
            "p_upper": p_shift, "p_alt_le0": p_le0, "trips_per_day": rate, "theta_per_trade": theta / rate,
            "ucb95_per_trade": ucb / rate, "null_power": power, "ucb_below_eps": ucb < eps, "power_ok": power >= POWER_MIN,
            "status": status,
        }
        cmp = {}
        for k in ("theta_hat", "ucb95", "se_boot", "p_upper", "trips_per_day", "theta_per_trade", "ucb95_per_trade", "null_power"):
            cmp[k] = rel(mine[k], v[k])
        maxrel = max(cmp.values())
        ints_ok = (v["n_days"] == n_days and v["n_trips"] == n_trips and v["seed"] == mine["seed"] and v["resamples"] == B
                   and v["ordinal"] == t["ordinal"] and close(v["eps_ticks"], eps) and v["tier"] == t["tier"])
        flags_ok = (v["status"] == status and v["ucb_below_eps"] == mine["ucb_below_eps"] and v["power_ok"] == mine["power_ok"]
                    and v["covered"] is True and v["run"] is True and v["record_status"] == "run" and v["reasons"] == [])
        check(f"1.[{t['ordinal']}] {m}: floats to 1e-9 relative", maxrel <= REL_TOL,
              f"max rel {maxrel:.3e}; theta {theta:.12g} ucb {ucb:.12g} se {se:.12g} p {p_shift:.12g} power {power:.12g}")
        check(f"1.[{t['ordinal']}] {m}: integers, seed, resamples, eps, tier", ints_ok,
              f"n_days {n_days} n_trips {n_trips} seed {mine['seed']}")
        check(f"1.[{t['ordinal']}] {m}: status and flags", flags_ok, f"mine {status!r}, verdict {v['status']!r}")
        check(f"1.[{t['ordinal']}] {m}: p convention (shifted theta*-theta_hat >= theta_hat) matches the verdict; alt #(theta*<=0) differs or equals",
              close(p_shift, v["p_upper"]), f"p_shift {p_shift:.10f} p_le0 {p_le0:.10f} verdict {v['p_upper']:.10f}")
        # eps cross-check against the frozen epsilon table
        e = eps_table[t["vehicle"]]
        check(f"1.[{t['ordinal']}] {m}: eps_X = epsilon.json eps_operative, tick value x q_c gives the list's dollars",
              close(e["eps_operative"], eps) and close(e["eps_operative"] * e["tick_value_usd"] * e["q_c"], t["eps_usd_per_day_at_q"]) and e["q_c"] == t["q_c"],
              f"eps_operative {e['eps_operative']} tick {e['tick_value_usd']} q_c {e['q_c']}")
        mine["rel_diff"] = cmp
        mine["verdict"] = {k: v[k] for k in ("theta_hat", "ucb95", "se_boot", "p_upper", "null_power", "trips_per_day", "theta_per_trade", "ucb95_per_trade", "status", "n_days", "n_trips")}
        out[m] = mine
    return out


# ----------------------------------------------------------------------------------------------
# Item 2: Holm
# ----------------------------------------------------------------------------------------------
def holm(pvals: dict[str, float], alpha: float):
    order = sorted(pvals.items(), key=lambda kv: (kv[1], kv[0]))
    m = len(order)
    rows = []
    still = True
    for i, (member, p) in enumerate(order, start=1):
        thr = alpha / (m - i + 1)
        rej = still and p <= thr
        if not rej:
            still = False
        rows.append({"member": member, "p_value": p, "rank": i, "threshold": thr, "reject": rej})
    return rows


def item2(lst, verdict, per_trial):
    log("== Item 2: Holm at K = 5 (and descriptive K = 9)")
    tier_a = [t for t in lst["trials"] if t["tier"] == "A"]
    pvals = {}
    for t in tier_a:
        pvals[t["member"]] = per_trial[t["member"]]["p_upper"] if t["run"] else 1.0  # R-E22-A13
    out = {}
    for label, k, vkey in (("k5", K_HOLM, "holm"), ("k9", K_DESCRIPTIVE, "holm_descriptive_k9")):
        alpha = 0.05 / k
        rows = holm(pvals, alpha)
        v = verdict["edge_chain"][vkey]
        ok_rows = len(rows) == len(v["rows"]) and all(
            a["member"] == b["member"] and close(a["p_value"], b["p_value"]) and a["rank"] == b["rank"]
            and close(a["threshold"], b["threshold"]) and a["reject"] == b["reject"] for a, b in zip(rows, v["rows"]))
        check(f"2.{label} Holm rows (member, p, rank, threshold, reject) equal; m = {len(rows)}; alpha_k = {alpha:.10g}",
              ok_rows and v["m"] == len(rows) and v["k"] == k and close(v["alpha_k"], alpha),
              "; ".join(f"{r['member']} p {r['p_value']:.10f} thr {r['threshold']:.10f} rej {r['reject']}" for r in rows))
        out[label] = {"alpha_k": alpha, "k": k, "m": len(rows), "rows": rows}
    check("2.family = screened Tier A size 2 (HEOD run, wkndbtc not run at p = 1)", len(pvals) == 2 and pvals.get("K8-wkndbtc-01 MNQ") == 1.0)
    check("2.list k_holm = 5 and verdict k_holm = 5", lst["k_holm"] == K_HOLM == verdict["k_holm"])
    return out


# ----------------------------------------------------------------------------------------------
# Item 3: DSR, t, PBO
# ----------------------------------------------------------------------------------------------
def moments(vals: np.ndarray):
    mu = vals.mean()
    d = vals - mu
    m2 = float((d ** 2).mean())
    m3 = float((d ** 3).mean())
    m4 = float((d ** 4).mean())
    sd = math.sqrt(m2)
    return mu, sd, m3 / m2 ** 1.5 if m2 > 0 else float("nan"), m4 / m2 ** 2 if m2 > 0 else float("nan")


def expected_max_sr(n: int, var: float) -> float:
    g = 0.5772156649015329
    return math.sqrt(var) * ((1 - g) * ND.inv_cdf(1 - 1 / n) + g * ND.inv_cdf(1 - 1 / (n * math.e)))


def cscv(perf: list[list[float]], n_blocks: int):
    n_s = len(perf)
    logits, win_pos, win_oos = [], 0, []
    ties = 0
    for train in combinations(range(n_blocks), n_blocks // 2):
        test = [b for b in range(n_blocks) if b not in set(train)]
        ins = [sum(row[b] for b in train) for row in perf]
        oos = [sum(row[b] for b in test) for row in perf]
        best_val = max(ins)
        best = ins.index(best_val)  # first max, the program's convention
        if ins.count(best_val) > 1:
            ties += 1
        worse = sum(1 for s in range(n_s) if oos[s] < oos[best])
        rank = min(max((worse + 0.5) / n_s, 1e-9), 1 - 1e-9)
        logits.append(math.log(rank / (1 - rank)))
        win_pos += oos[best] > 0
        win_oos.append(oos[best])
    n_splits = len(logits)
    return {"pbo": sum(1 for lg in logits if lg <= 0) / n_splits, "n_splits": n_splits, "n_strategies": n_s,
            "p_winner_positive_oos": win_pos / n_splits, "winner_mean_oos": statistics.fmean(win_oos), "is_ties": ties}


def item3(lst, verdict, records, per_trial):
    log("== Item 3: DSR at N = 533, daily t, CSCV PBO")
    run_members = [t["member"] for t in lst["trials"] if t["run"]]
    tier_a_run = [t["member"] for t in lst["trials"] if t["run"] and t["tier"] == "A"]
    variance_over = tier_a_run if len(tier_a_run) >= 2 else run_members  # V14 (c), R-E22-A14
    sharpes = {}
    stats = {}
    for m in run_members:
        vals = np.asarray(records[m]["series"]["values"], dtype=float)
        mu, sd, skew, kurt = moments(vals)
        sharpes[m] = mu / sd
        stats[m] = {"n": len(vals), "mean": mu, "sd_pop": sd, "skew": skew, "kurt_raw": kurt, "sharpe": mu / sd}
    var = statistics.pvariance([sharpes[m] for m in variance_over])
    vd = verdict["edge_chain"]["dsr"]
    check("3a.variance_over = the three run trials (one Tier A series; V14 c / R-E22-A14)",
          vd["variance_over"] == variance_over and vd["variance_over_n_members"] == len(variance_over), str(variance_over))
    check("3a.Sharpe variance (population, daily Sharpes mean/pop sd) to 1e-9", close(var, vd["sharpe_variance"]),
          f"mine {var:.15g} verdict {vd['sharpe_variance']:.15g}")
    sr0 = expected_max_sr(PROGRAM_N, var)
    check("3a.E[max SR] at N = 533 (NormalDist.inv_cdf) vs verdict (Acklam ppf) within 1e-8",
          rel(sr0, vd["expected_max_daily_sharpe_under_null"]) <= 1e-8, f"mine {sr0:.15g} verdict {vd['expected_max_daily_sharpe_under_null']:.15g} rel {rel(sr0, vd['expected_max_daily_sharpe_under_null']):.2e}")
    check("3a.n_trials = 533 = list program_n = verdict program_n", vd["n_trials"] == PROGRAM_N == lst["program_n"] == verdict["program_n"])
    chain = {}
    for m in tier_a_run:
        st = stats[m]
        sr = st["sharpe"]
        den_sq = 1 - st["skew"] * sr + 0.25 * (st["kurt_raw"] - 1) * sr ** 2
        z = (sr - sr0) * math.sqrt(st["n"] - 1) / math.sqrt(den_sq)
        dsr = ND.cdf(z)
        tail = 0.5 * math.erfc(-z / math.sqrt(2))  # the same quantity without the 1 + erf cancellation
        t_stat = st["mean"] / (st["sd_pop"] / math.sqrt(st["n"]))
        vt = verdict["edge_chain"]["trials"][m]
        check(f"3a.DSR {m}: mine {dsr:.6g} (z {z:.6f}; exact tail {tail:.3e}) vs verdict {vt['dsr']}",
              abs(dsr - vt["dsr"]) <= 1e-12 and vt["dsr_undefined"] is None,
              f"SR {sr:.10g} skew {st['skew']:.6g} kurt {st['kurt_raw']:.6g} n {st['n']}")
        check(f"3b.daily t {m}: mean / (pop sd / sqrt n) to 1e-9", close(t_stat, vt["t_stat"]), f"mine {t_stat:.15g} verdict {vt['t_stat']:.15g}")
        # second check: the program's functions on my inputs
        d2 = mc.deflated_sharpe_ratio(sr, st["n"], PROGRAM_N, var, st["skew"], st["kurt_raw"])
        t2 = mc.harvey_liu_zhu_verdict(st["mean"], st["sd_pop"], st["n"])
        check(f"3.second check funnel.multiple_comparisons on my inputs: DSR {d2['deflated_sharpe_ratio']:.6g}, E[max] {d2['expected_max_sharpe_under_null']:.12g}, t {t2['t_stat']:.12g}",
              abs(d2["deflated_sharpe_ratio"] - vt["dsr"]) <= 1e-12 and close(t2["t_stat"], vt["t_stat"]) and close(d2["expected_max_sharpe_under_null"], vd["expected_max_daily_sharpe_under_null"]))
        chain[m] = {"sharpe": sr, "skew": st["skew"], "kurt_raw": st["kurt_raw"], "n": st["n"], "z": z, "dsr": dsr, "dsr_exact_tail": tail,
                    "t_stat": t_stat, "sr0": sr0, "sharpe_variance": var, "second_check": {"dsr": d2["deflated_sharpe_ratio"], "t": t2["t_stat"]}}
    # PBO by L-E5-3 over every run trial, union of window dates, zeros off a trial's dates
    pbo_over = tier_a_run if len(tier_a_run) >= 2 else run_members
    union = sorted(set().union(*[set(records[m]["series"]["dates"]) for m in pbo_over]))
    n_days = len(union)
    block = n_days // PBO_BLOCKS
    perf = []
    for m in pbo_over:
        s = dict(zip(records[m]["series"]["dates"], records[m]["series"]["values"]))
        aligned = [float(s.get(d, 0.0)) for d in union]
        perf.append([sum(aligned[b * block:(b + 1) * block]) for b in range(PBO_BLOCKS)])
    res = cscv(perf, PBO_BLOCKS)
    vp = verdict["edge_chain"]["pbo"]
    check("3c.PBO set = the three run trials; union dates, block size, splits",
          vp["over"] == pbo_over and vp["n_days"] == n_days == vp["window_days"] and vp["block_days"] == block and vp["n_splits"] == res["n_splits"] and vp["n_strategies"] == len(pbo_over) and vp["degenerate"] is False,
          f"union {n_days} dates, 8 blocks of {block} ({n_days - 8 * block} dates outside every block), {res['n_splits']} splits, IS ties {res['is_ties']}")
    check("3c.PBO value to 1e-9", close(res["pbo"], vp["pbo"]), f"mine {res['pbo']:.12g} verdict {vp['pbo']:.12g} = {round(res['pbo'] * res['n_splits'])}/{res['n_splits']}")
    check("3c.winner positive OOS fraction and winner mean OOS sum to 1e-9",
          close(res["p_winner_positive_oos"], vp["p_winner_positive_oos"]) and close(res["winner_mean_oos"], vp["winner_mean_oos_ticks_per_micro"]),
          f"mine {res['p_winner_positive_oos']:.12g}, {res['winner_mean_oos']:.12g}; verdict {vp['p_winner_positive_oos']:.12g}, {vp['winner_mean_oos_ticks_per_micro']:.12g}")
    pb2 = mc.probability_of_backtest_overfitting(perf, PBO_BLOCKS)
    check("3c.second check funnel.multiple_comparisons.probability_of_backtest_overfitting on my blocks", close(pb2.pbo, vp["pbo"]) and pb2.n_splits == vp["n_splits"], f"{pb2.pbo:.12g}")
    union_extra = {m: len(set(union) - set(records[m]["series"]["dates"])) for m in pbo_over}
    return {"sharpes": sharpes, "stats": stats, "sharpe_variance": var, "variance_over": variance_over, "sr0": sr0, "chain": chain,
            "pbo": {**res, "n_days": n_days, "block_days": block, "over": pbo_over, "dates_off_each_trial": union_extra, "block_sums": perf}}


# ----------------------------------------------------------------------------------------------
# Item 4: chain verdict wording, cluster statement, resolution table
# ----------------------------------------------------------------------------------------------
def item4(lst, verdict, records, per_trial, holm_out, chain_out, eps_table):
    log("== Item 4: Tier A chain verdict, wording, null statement, resolution table")
    tier_a = [t for t in lst["trials"] if t["tier"] == "A"]
    holm_rej = {r["member"]: r["reject"] for r in holm_out["k5"]["rows"]}
    for t in tier_a:
        m = t["member"]
        vt = verdict["edge_chain"]["trials"][m]
        if t["run"]:
            c = chain_out["chain"][m]
            passes = {"holm": holm_rej[m], "dsr": c["dsr"] > DSR_MIN, "t": c["t_stat"] > T_MIN, "pbo": chain_out["pbo"]["pbo"] < PBO_MAX}
        else:
            passes = {"holm": False, "dsr": False, "t": False, "pbo": chain_out["pbo"]["pbo"] < PBO_MAX}
        first_fail = next((s for s in ("holm", "dsr", "t", "pbo") if not passes[s]), None)
        all_pass = all(passes.values())
        expected_verdict = ("edge candidate, composite pending" + ("; no edge claim without a registered holdout read" if "source-overlap" in t["labels"] else "")) if all_pass else "no edge"
        vp = {k: vt["passes"][k] for k in ("holm", "dsr", "t", "pbo")}
        check(f"4.{m}: passes {passes} and first failing step {first_fail!r}", vp == passes and vt["first_failing_step"] == first_fail and vt["passes"]["composite"] == "pending",
              f"verdict passes {vp}, first failing {vt['first_failing_step']!r}")
        check(f"4.{m}: verdict wording {vt['verdict']!r} is the rule's ({expected_verdict!r}); never a bare 'edge'",
              vt["verdict"] == expected_verdict and vt["verdict"] != "edge" and ("edge" not in vt["verdict"] or vt["verdict"].startswith("no edge") or "edge candidate" in vt["verdict"]))
        if not t["run"]:
            check(f"4.{m}: not run -> dsr None ('no series'), t None, cluster PBO carried", vt["dsr"] is None and vt["dsr_undefined"] == "no series" and vt["t_stat"] is None and close(vt["pbo"], chain_out["pbo"]["pbo"]))
    check("4.composite pending (V14 a)", verdict["edge_chain"]["composite"] == "pending")
    # cluster statement (NULL_CRITERIA_E 1, 6)
    run_members = [t["member"] for t in lst["trials"] if t["run"]]
    statuses = {m: per_trial[m]["status"] for m in run_members}
    covered = [m for m in run_members]
    inact = [m for m in run_members if statuses[m] == "null by inactivity"]
    blocking = [m for m in run_members if statuses[m] == "inconclusive"]
    not_covered = [t for t in lst["trials"] if not t["run"]]
    pre_declared = all(("inconclusive by design" in t["labels"]) or ("untestable" in " ".join(t["labels"])) for t in not_covered)
    cluster_verdict = "null" if (not blocking and pre_declared) else "no statement"
    st = verdict["statement"]
    check("4.statement: covered = the three run trials, all 'null'", st["covered"] == covered and all(statuses[m] == "null" for m in covered), str(statuses))
    check("4.statement: blocking [] and null_by_inactivity [] (min closed trips 231 >= 30; no zero-SE)", st["blocking"] == blocking == [] and st["null_by_inactivity"] == inact == [])
    check("4.statement: not_covered = wkndbtc with its list labels and reason 'not run: inconclusive by design'",
          [x["member"] for x in st["not_covered"]] == [t["member"] for t in not_covered] and st["not_covered"][0]["labels"] == not_covered[0]["labels"]
          and st["not_covered"][0]["reason"] == "not run: inconclusive by design", json.dumps(st["not_covered"]))
    check(f"4.statement verdict {st['verdict']!r} = mine {cluster_verdict!r}; note None", st["verdict"] == cluster_verdict and st["note"] is None)
    # resolution table per exposure (vehicle) (NULL_CRITERIA_E 7)
    vehicles = sorted({t["vehicle"] for t in lst["trials"]})
    mine_res = []
    for veh in vehicles:
        ts = [t for t in lst["trials"] if t["vehicle"] == veh]
        run_ts = [t for t in ts if t["run"]]
        eps = ts[0]["eps_ticks"]
        row = {"vehicle": veh, "eps_ticks": float(eps), "eps_usd_per_day_at_q": float(ts[0]["eps_usd_per_day_at_q"]), "q_c": ts[0]["q_c"],
               "not_covered": [t["member"] for t in ts if not t["run"]], "null_by_inactivity": [t["member"] for t in run_ts if statuses[t["member"]] == "null by inactivity"]}
        if run_ts:
            min_trips = min(per_trial[t["member"]]["n_trips"] for t in run_ts)
            fewest = [t["member"] for t in run_ts if per_trial[t["member"]]["n_trips"] == min_trips]
            row["fewest_trips"] = {"member": fewest[0], "n_trips": min_trips, "tied": fewest}
            best = max(run_ts, key=lambda t: per_trial[t["member"]]["ucb95_per_trade"])
            row["largest_ucb95_per_trade"] = {"member": best["member"], "ticks": per_trial[best["member"]]["ucb95_per_trade"]}
        else:
            row["fewest_trips"] = None
            row["largest_ucb95_per_trade"] = None
        mine_res.append(row)
    vres = {r["vehicle"]: r for r in verdict["resolution"]}
    for row in mine_res:
        v = vres[row["vehicle"]]
        ok = (close(v["eps_ticks"], row["eps_ticks"]) and close(v["eps_usd_per_day_at_q"], row["eps_usd_per_day_at_q"]) and v["q_c"] == row["q_c"]
              and v["not_covered"] == row["not_covered"] and v["null_by_inactivity"] == row["null_by_inactivity"])
        if row["fewest_trips"] is None:
            ok = ok and v["fewest_trips"] is None and v["largest_ucb95_per_trade"] is None
        else:
            ok = ok and v["fewest_trips"]["n_trips"] == row["fewest_trips"]["n_trips"] and v["fewest_trips"]["member"] in row["fewest_trips"]["tied"] \
                and v["largest_ucb95_per_trade"]["member"] == row["largest_ucb95_per_trade"]["member"] and close(v["largest_ucb95_per_trade"]["ticks"], row["largest_ucb95_per_trade"]["ticks"])
        tie_note = f"; fewest-trips tie among {row['fewest_trips']['tied']} (verdict picked {v['fewest_trips']['member']}, the lower ordinal)" if row["fewest_trips"] and len(row["fewest_trips"]["tied"]) > 1 else ""
        check(f"4.resolution {row['vehicle']}: eps {row['eps_ticks']} ticks (${row['eps_usd_per_day_at_q']} at q_c {row['q_c']}), fewest trips, largest UCB95/trip, not covered", ok,
              json.dumps({k: row[k] for k in ("fewest_trips", "largest_ucb95_per_trade", "not_covered")}) + tie_note)
    check("4.resolution rows = one per vehicle (6C, MGC, MNQ)", sorted(vres) == vehicles)
    return {"statuses": statuses, "cluster_verdict": cluster_verdict, "resolution": mine_res}


# ----------------------------------------------------------------------------------------------
# Item 6: anything in the verdict JSON contradicting the list or the records
# ----------------------------------------------------------------------------------------------
def item6(lst, verdict, records, per_trial):
    log("== Item 6: verdict JSON against the list and the records")
    vrows = {t["member"]: t for t in verdict["trials"]}
    for t in lst["trials"]:
        m = t["member"]
        v = vrows[m]
        r = records[m]
        same = (v["ordinal"] == t["ordinal"] and v["tier"] == t["tier"] and v["labels"] == t["labels"] and v["q_c"] == t["q_c"] and v["vehicle"] == t["vehicle"]
                and v["run"] == t["run"] and v["d4_power"] == t["power"])
        check(f"6.[{t['ordinal']}] {m}: verdict row ordinal/tier/labels/q_c/vehicle/run/d4_power equal the list", same)
        if t["run"]:
            check(f"6.[{t['ordinal']}] {m}: verdict n_days = window n = len(series); n_trips = series.n_trips = trade_rate.n_trips; eps = list; seed = list",
                  v["n_days"] == r["window_dates"]["n"] == len(r["series"]["values"]) and v["n_trips"] == r["series"]["n_trips"] == r["trade_rate"]["n_trips"]
                  and close(v["eps_ticks"], t["eps_ticks"]) and v["seed"] == t["bootstrap_seed"] and v["record_status"] == r["status"] == "run")
        else:
            check(f"6.[{t['ordinal']}] {m}: verdict not-run row: status 'not run', covered false, record_status not_run, reason names the label",
                  v["status"] == "not run" and v["covered"] is False and v["record_status"] == r["status"] == "not_run" and "inconclusive by design" in " ".join(v["reasons"]),
                  str(v["reasons"]))
    c = verdict["constants"]
    bs = lst["bootstrap"]
    check("6.constants equal the list's bootstrap block and the criteria (1.645, 0.80, 30, 3.0, 0.95, 8, 0.5)",
          c["seed_base"] == bs["seed_base"] == SEED_BASE and c["resamples"] == bs["resamples"] == B and c["mean_block"] == bs["mean_block"] == MEAN_BLOCK
          and c["ucb_quantile"] == bs["ucb_quantile"] == UCB_Q and c["null_z"] == NULL_Z and c["null_power_min"] == POWER_MIN and c["inactivity_min"] == INACTIVITY_MIN
          and c["t_min"] == T_MIN and c["dsr_min"] == DSR_MIN and c["pbo_blocks"] == PBO_BLOCKS and c["pbo_max"] == PBO_MAX)
    # program N against the ledger's last entry (independent of screening.trial_registry)
    last = None
    for line in LEDGER.read_text().splitlines():
        if line.strip():
            last = json.loads(line)
    check("6.program_n 533 = list = ledger last entry n_after (r007-E22) = verdict program_n_check",
          lst["program_n"] == verdict["program_n"] == PROGRAM_N == last["n_after"] and verdict["program_n_check"]["equal"] is True
          and verdict["program_n_check"]["registry_current_n"] == last["n_after"], f"ledger {last['entry_id']} n_before {last['n_before']} n_after {last['n_after']}")
    # the word "edge" anywhere in the verdict's string values
    bad = []

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str) and "edge" in o.lower() and o != "no edge":
            bad.append((path, o))
    walk(verdict)
    check("6.no string value in the verdict says 'edge' other than 'no edge'", not bad, str(bad[:5]))
    check("6.schema and cluster", verdict["schema"] == "stage_e_confirmation_verdict/1" and verdict["cluster"] == "K8")


def main() -> None:
    lst = load(LIST)
    verdict = load(VERDICT)
    marker = load(MARKER)
    notrun = load(NOTRUN)
    records = {t["member"]: load(RUN_DIR / record_name(t["member"])) for t in lst["trials"]}
    eps_rows = load(EPSILON)["exposures"]
    eps_table = {e["vehicle"]: e for e in eps_rows}
    log(f"verdict sha256 {sha256(VERDICT)}; list sha256 {sha256(LIST)}")
    meta = item0(lst, verdict, marker, notrun, records)
    per_trial = item1(lst, verdict, records, eps_table)
    holm_out = item2(lst, verdict, per_trial)
    chain_out = item3(lst, verdict, records, per_trial)
    stmt = item4(lst, verdict, records, per_trial, holm_out, chain_out, eps_table)
    item6(lst, verdict, records, per_trial)
    n_fail = sum(1 for c in CHECKS if not c["ok"])
    log(f"== {len(CHECKS)} checks, {n_fail} FAIL")
    figures = {"meta": meta, "per_trial": per_trial, "holm": holm_out, "chain": {k: v for k, v in chain_out.items() if k != "pbo"},
               "pbo": chain_out["pbo"], "statement": stmt, "checks": CHECKS, "verdict_sha256": sha256(VERDICT)}
    (OUT_DIR / "figures.json").write_text(json.dumps(figures, indent=1, default=str))
    (OUT_DIR / "recompute.log").write_text("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
