"""VerdictVerifier-FableXHigh, Stage E.23: file-based recomputation of every verdict number.

Own implementations only (no import of trigger_hold, base_rules, screening, funnel). Reads the
discovery result, the trend files, E.21's T1/T2 results, the power table, the events files, the
settlement table, the D8 cost table, the markers, the registry and the freeze. Writes
recompute_file_based.json beside this script. No bar store is opened here.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
import subprocess
from datetime import date, datetime, time
from itertools import combinations
from zoneinfo import ZoneInfo

import numpy as np
from scipy.stats import norm
from scipy.stats import t as student_t

ROOT = "/home/kiros-li/Documents/GitHub/PropExperiment"
OUT_DIR = f"{ROOT}/reports/stage_e23_briefs/verify"
CT = ZoneInfo("America/Chicago")
W_FIRST, W_LAST = date(2011, 7, 27), date(2019, 4, 30)
CF_FIRST, CF_LAST = date(2019, 5, 6), date(2024, 2, 29)
ALPHA, T_BAR, SHARPE_BAR, MAX_SURV, N_TRIALS, BLOCKS = 0.05, 2.0, 0.3, 4, 538, 8
EULER = 0.5772156649015329
REL_TOL = 1e-9


def load(p: str):
    with open(f"{ROOT}/{p}") as f:
        return json.load(f)


def sha(p: str) -> str:
    return hashlib.sha256(open(f"{ROOT}/{p}", "rb").read()).hexdigest()


def match(run, mine, rel: float = REL_TOL, abs_tol: float = 1e-12) -> bool:
    if run is None or mine is None:
        return run is None and mine is None
    if isinstance(run, bool) or isinstance(mine, bool):
        return bool(run) == bool(mine)
    if isinstance(run, (list, str, dict)) or isinstance(mine, (list, str, dict)):
        return run == mine
    return math.isclose(float(run), float(mine), rel_tol=rel, abs_tol=abs_tol)


def row(name, run, mine, **extra):
    return {"name": name, "run": run, "mine": mine, "match": match(run, mine), **extra}


# ------------------------------------------------------------------ statistics (own code) ----
def nw_se_mean(x: np.ndarray, lags: int) -> float:
    n = len(x)
    e = x - x.mean()
    lrv = float(e @ e) / n
    for lag in range(1, min(lags, n - 1) + 1):
        w = 1.0 - lag / (lags + 1.0)
        lrv += 2.0 * w * float(e[lag:] @ e[:-lag]) / n
    return math.sqrt(max(lrv, 0.0) / n)


def raw(x: np.ndarray, lags: int) -> dict:
    n = len(x)
    mean, sd = float(x.mean()), float(x.std(ddof=1))
    return {"n": n, "mean": mean, "sd": sd, "sharpe": mean / sd * math.sqrt(252),
            "t": mean / (sd / math.sqrt(n)), "t_nw": mean / nw_se_mean(x, lags)}


def ols_hac(y: np.ndarray, regs: list[np.ndarray], lags: int) -> dict:
    n = len(y)
    X = np.column_stack([np.ones(n), *regs])
    k = X.shape[1]
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    e = y - X @ beta
    sse = float(e @ e)
    sst = float(((y - y.mean()) ** 2).sum())
    se_plain = math.sqrt(sse / (n - k) * XtX_inv[0, 0])
    xe = X * e[:, None]
    S = xe.T @ xe
    for lag in range(1, min(lags, n - 1) + 1):
        w = 1.0 - lag / (lags + 1.0)
        G = xe[lag:].T @ xe[:-lag]
        S = S + w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se_hac = math.sqrt(V[0, 0])
    a = float(beta[0])
    t_plain, t_nw = a / se_plain, a / se_hac
    p_plain = float(student_t.sf(t_plain, n - k))
    p_nw = float(norm.sf(t_nw))
    return {"n": n, "k": k, "alpha": a, "betas": [float(b) for b in beta[1:]],
            "se_plain": se_plain, "se_hac": se_hac, "t_plain": t_plain, "t_nw": t_nw,
            "p_plain": p_plain, "p_nw": p_nw, "p_alpha": max(p_plain, p_nw),
            "r2": 1.0 - sse / sst,
            "corr": [float(np.corrcoef(y, r)[0, 1]) for r in regs]}


def holm(p: dict[str, float], alpha: float) -> dict[str, bool]:
    m = len(p)
    order = sorted(p, key=lambda k: (p[k], k))
    out = {k: False for k in p}
    for i, k in enumerate(order):
        if p[k] > alpha / (m - i):
            break
        out[k] = True
    return out


def moments(x: np.ndarray) -> dict:
    n = len(x)
    mean = float(x.mean())
    sd = float(x.std(ddof=0))
    z = (x - mean) / sd
    return {"n": n, "sharpe": mean / sd, "skew": float((z ** 3).mean()),
            "kurt": float((z ** 4).mean())}


def expected_max_sharpe(n_trials: int, var: float) -> float:
    g = EULER
    return math.sqrt(var) * ((1 - g) * norm.ppf(1 - 1 / n_trials)
                             + g * norm.ppf(1 - 1 / (n_trials * math.e)))


def dsr_of(mom: dict, n_trials: int, var: float) -> float:
    sr = mom["sharpe"]
    bench = expected_max_sharpe(n_trials, var)
    den = math.sqrt(1 - mom["skew"] * sr + 0.25 * (mom["kurt"] - 1) * sr ** 2)
    return float(norm.cdf((sr - bench) * math.sqrt(mom["n"] - 1) / den))


def cscv_pbo(mat: dict[str, np.ndarray], n_blocks: int, floor_blocks: bool) -> dict:
    labels = list(mat)
    n_days = len(next(iter(mat.values())))
    if floor_blocks:
        w = n_days // n_blocks
        perf = [[float(mat[k][b * w:(b + 1) * w].sum()) for b in range(n_blocks)]
                for k in labels]
        dropped = n_days - w * n_blocks
    else:
        perf = [[float(s.sum()) for s in np.array_split(mat[k], n_blocks)] for k in labels]
        dropped = 0
    n = len(labels)
    logits, oos_best = [], []
    for train in combinations(range(n_blocks), n_blocks // 2):
        test = [b for b in range(n_blocks) if b not in train]
        ins = [sum(perf[s][b] for b in train) for s in range(n)]
        oos = [sum(perf[s][b] for b in test) for s in range(n)]
        best = max(range(n), key=lambda s: ins[s])  # first maximum on ties
        worse = sum(1 for s in range(n) if oos[s] < oos[best])
        r = min(max((worse + 0.5) / n, 1e-9), 1 - 1e-9)
        logits.append(math.log(r / (1 - r)))
        oos_best.append(oos[best])
    return {"pbo": sum(1 for lg in logits if lg <= 0) / len(logits), "n_splits": len(logits),
            "n_days": n_days, "block_days": n_days // n_blocks, "dropped_days": dropped,
            "winner_mean_oos": statistics.fmean(oos_best),
            "p_winner_positive_oos": sum(1 for v in oos_best if v > 0) / len(oos_best)}


def phi(x: float) -> float:
    return float(norm.cdf(x))


def power(n_dates: int, hurdle: float) -> float:
    return 1.0 - phi(hurdle - 0.5 * math.sqrt(n_dates / 252))


# ------------------------------------------------------------------ main ----
def main() -> None:
    disc = load("reports/stage_e23_runs/discovery/discovery_result.json")
    conf = load("reports/stage_e23_runs/confirmation/confirmation_result.json")
    pw = load("reports/stage_e23_power.json")
    reg = load("reports/stage_e23_registration.json")
    settle = load("reports/stage_e16_settlement.json")
    costs = load("reports/stage_e2a_costs.json")
    report: dict = {"rows": [], "notes": []}
    ths = disc["trigger_holds"]
    trend = {r: load(f"reports/stage_e23_trend_per_root/{r}.json") for r in ("ZF", "ZN", "ZB", "NQ")}

    # 1. per trigger-hold, per case statistics
    base_series, base_rows = {}, {}
    for tid, th in ths.items():
        root, h = th["root"], th["h"]
        for case in ("base", "stress"):
            ser = th["series"][case]
            dates = [d for d, _ in ser]
            y = np.array([v for _, v in ser], dtype=float)
            x1 = np.array([trend[root]["v_T1"].get(d, 0.0) for d in dates])
            x2 = np.array([trend[root]["v_T2"].get(d, 0.0) for d in dates])
            r_mine, r_run = raw(y, h), th["cases"][case]["raw"]
            for k in ("n", "mean", "sd", "sharpe", "t", "t_nw"):
                report["rows"].append(row(f"{tid}/{case}/raw/{k}", r_run[k], r_mine[k]))
            a_mine, a_run = ols_hac(y, [x1, x2], h), th["cases"][case]["alpha"]
            for k in ("alpha", "se_plain", "se_hac", "t_plain", "t_nw", "p_plain", "p_nw",
                      "p_alpha", "r2"):
                report["rows"].append(row(f"{tid}/{case}/alpha/{k}", a_run[k], a_mine[k]))
            for j in range(2):
                report["rows"].append(row(f"{tid}/{case}/alpha/beta{j + 1}", a_run["betas"][j],
                                          a_mine["betas"][j]))
                report["rows"].append(row(f"{tid}/{case}/alpha/corr{j + 1}", a_run["corr"][j],
                                          a_mine["corr"][j]))
            if case == "base":
                base_series[tid] = (dates, y)
                base_rows[tid] = {"p_alpha": a_mine["p_alpha"], "t_nw": a_mine["t_nw"],
                                  "sharpe": r_mine["sharpe"]}
            # series sanity
            ds = [date.fromisoformat(d) for d in dates]
            report["rows"].append(row(f"{tid}/{case}/series/n_dates", th["n_dates"], len(ds)))
            report["rows"].append(row(f"{tid}/{case}/series/sorted_distinct", True,
                                      ds == sorted(set(ds))))
            report["rows"].append(row(f"{tid}/{case}/series/inside_W_ext", True,
                                      ds[0] >= W_FIRST and ds[-1] <= W_LAST))
            zero_reg = sum(1 for d in dates if d not in trend[root]["v_T1"])
            report["notes"].append(f"{tid}/{case}: {zero_reg} series dates with no v_T1 value "
                                   f"(zero-filled, spec 1): {[d for d in dates if d not in trend[root]['v_T1']][:3]}")
        # in-market fraction (units-based in the run); nonzero-value share as a bound
        dates, y = base_series[tid]
        nz = int((y != 0).sum())
        report["notes"].append(f"{tid}: nonzero base values {nz}/{len(y)} = {nz / len(y):.6f}; run "
                               f"in_market_fraction_units {th['in_market_fraction_units']:.6f} "
                               f"(= {round(th['in_market_fraction_units'] * len(y))} days)")

    # 2. Holm, survivors, DSR, PBO
    rej = holm({k: v["p_alpha"] for k, v in base_rows.items()}, ALPHA)
    for tid in ths:
        ch = disc["screen"]["checks"][tid]
        report["rows"].append(row(f"{tid}/screen/holm_rejects", ch["holm_rejects"], rej[tid]))
        report["rows"].append(row(f"{tid}/screen/t_nw_at_least_2", ch["t_nw_at_least_2"],
                                  base_rows[tid]["t_nw"] >= T_BAR))
        report["rows"].append(row(f"{tid}/screen/sharpe_at_least_0.3", ch["sharpe_at_least_0.3"],
                                  base_rows[tid]["sharpe"] >= SHARPE_BAR))
    eligible = [k for k in ths if rej[k] and base_rows[k]["t_nw"] >= T_BAR
                and base_rows[k]["sharpe"] >= SHARPE_BAR]
    ranked = sorted(eligible, key=lambda k: (-base_rows[k]["t_nw"], -base_rows[k]["sharpe"], k))
    report["rows"].append(row("screen/survivors", disc["screen"]["survivors"], ranked[:MAX_SURV]))
    report["rows"][-1]["match"] = disc["screen"]["survivors"] == ranked[:MAX_SURV]
    report["rows"].append(row("screen/smallest_p_alpha", None, None))
    report["rows"][-1].update({"run": min(ths[k]["cases"]["base"]["alpha"]["p_alpha"] for k in ths),
                               "mine": min(v["p_alpha"] for v in base_rows.values())})
    report["rows"][-1]["match"] = match(report["rows"][-1]["run"], report["rows"][-1]["mine"])
    # Holm step-1 threshold vs smallest p
    report["notes"].append(f"Holm step 1 threshold 0.05/5 = 0.01; smallest p_alpha = "
                           f"{min(v['p_alpha'] for v in base_rows.values()):.6f}; largest t_nw = "
                           f"{max(v['t_nw'] for v in base_rows.values()):.6f}; largest base Sharpe = "
                           f"{max(v['sharpe'] for v in base_rows.values()):.6f}")
    moms = {k: moments(base_series[k][1]) for k in ths}
    var = statistics.pvariance([m["sharpe"] for m in moms.values()])
    dd = disc["dsr_descriptive"]
    report["rows"].append(row("dsr/n_trials", dd["n_trials"], N_TRIALS))
    report["rows"].append(row("dsr/sharpe_variance", dd["sharpe_variance"], var))
    report["rows"].append(row("dsr/expected_max_daily_sharpe_under_null",
                              dd["expected_max_daily_sharpe_under_null"],
                              expected_max_sharpe(N_TRIALS, var)))
    for k in ths:
        report["rows"].append(row(f"dsr/{k}", dd["dsr"][k], dsr_of(moms[k], N_TRIALS, var)))
    grid = sorted({d for k in ths for d in base_series[k][0]})
    idx = {d: i for i, d in enumerate(grid)}
    mat = {}
    for k in ths:
        v = np.zeros(len(grid))
        for d, x in zip(*base_series[k]):
            v[idx[d]] = x
        mat[k] = v
    pb = cscv_pbo(mat, BLOCKS, floor_blocks=True)
    pd_ = disc["pbo_descriptive"]
    for a, b in (("pbo", "pbo"), ("n_splits", "n_splits"), ("n_days", "n_days"),
                 ("block_days", "block_days"), ("winner_mean_oos_ticks_per_micro", "winner_mean_oos"),
                 ("p_winner_positive_oos", "p_winner_positive_oos")):
        report["rows"].append(row(f"pbo/{a}", pd_[a], pb[b]))
    report["rows"].append(row("pbo/aligned_dates", pd_["aligned_dates"], len(grid)))
    report["rows"].append(row("pbo/first", pd_["first"], grid[0]))
    report["rows"][-1]["match"] = pd_["first"] == grid[0]
    report["rows"].append(row("pbo/last", pd_["last"], grid[-1]))
    report["rows"][-1]["match"] = pd_["last"] == grid[-1]
    pb2 = cscv_pbo(mat, BLOCKS, floor_blocks=False)
    report["notes"].append(f"PBO sensitivity: floor blocks (helper convention, {pb['dropped_days']} "
                           f"trailing days dropped) pbo={pb['pbo']:.6f}; equal-split blocks "
                           f"(np.array_split, no day dropped) pbo={pb2['pbo']:.6f}")

    # 3. power table and the W_cf gate
    for tid, wins in pw["rows"].items():
        for wname, r in wins.items():
            et = 0.5 * math.sqrt(r["n_dates"] / 252)
            report["rows"].append(row(f"power/{tid}/{wname}/expected_t", r["expected_t"], et))
            report["rows"].append(row(f"power/{tid}/{wname}/power_gate", r["power_gate"],
                                      power(r["n_dates"], T_BAR)))
            report["rows"].append(row(f"power/{tid}/{wname}/power_holm1", r["power_holm1"],
                                      power(r["n_dates"], max(T_BAR, float(norm.ppf(1 - ALPHA / 5))))))
            incon = r["nonoverlapping"] < 30 or power(r["n_dates"], T_BAR) < 0.2
            report["rows"].append(row(f"power/{tid}/{wname}/inconclusive_by_design",
                                      r["inconclusive_by_design"], incon))
            if wname == "W_ext":
                th = ths[tid]
                report["notes"].append(
                    f"{tid} W_ext: power table n_dates {r['n_dates']} units {r['units']} nonoverlap "
                    f"{r['nonoverlapping']} imf {r['in_market_fraction']:.6f} | discovery n_dates "
                    f"{th['n_dates']} units {th['units']} nonoverlap {th['nonoverlapping']} imf "
                    f"{th['in_market_fraction_units']:.6f}; power unit_counts {r['unit_counts']}; "
                    f"discovery unit_counts {th['unit_counts']}")
    gate = {}
    for s in range(1, 5):
        b = max(T_BAR, float(norm.ppf(1 - ALPHA / s)))
        gate[s] = {tid: power(wins["W_cf"]["n_dates"], b) for tid, wins in pw["rows"].items()}
        gate[s]["hurdle"] = b
        gate[s]["all_below_0.2"] = all(v < 0.2 for k, v in gate[s].items() if k != "hurdle")
    report["w_cf_gate"] = gate
    report["rows"].append(row("confirmation/s", conf["s"], len(ranked[:MAX_SURV])))
    report["rows"].append(row("confirmation/survivors_empty", conf["survivors"] == [], True))
    report["rows"].append(row("confirmation/trigger_holds_empty (nothing read)",
                              conf["trigger_holds"] == {}, True))
    report["rows"].append(row("confirmation/window", conf["window"] == "W_cf", True))
    report["rows"].append(row("confirmation/n_trials", conf["n_trials"], N_TRIALS))
    report["rows"].append(row("discovery/n_trials", disc["n_trials"], N_TRIALS))
    report["rows"].append(row("discovery/k", disc["k"], 5))
    report["rows"].append(row("discovery/window", disc["window"] == "W_ext", True))
    # no W_cf series anywhere in the outputs
    all_dates = [date.fromisoformat(d) for th in ths.values() for c in th["series"].values()
                 for d, _ in c]
    report["rows"].append(row("outputs/max_series_date_<=_2019-04-30", True,
                              max(all_dates) <= W_LAST))
    report["rows"][-1]["detail"] = str(max(all_dates))
    report["rows"].append(row("outputs/no_W_cf_series", True,
                              not any(th.get("window") == "W_cf" for th in ths.values())
                              and conf["trigger_holds"] == {}))

    # 4. events: decision time vs settlement bar open; window counts
    def settle_minute(root: str, d: date) -> int | None:
        for r in settle["products"][root]["settle"]:
            if date.fromisoformat(r["from"]) <= d <= date.fromisoformat(r["to"]):
                hh, mm = r["minute_ct"].split(":")
                return int(hh) * 60 + int(mm)
        return None

    ev_report = {}
    for th in reg["trigger_holds"]:
        for wname, p in th["events"].items():
            ev = load(p)
            root = ev["root"]
            lo, hi = (W_FIRST, W_LAST) if wname == "W_ext" else (CF_FIRST, CF_LAST)
            tau_times, late, outside, mismatch_day = set(), 0, 0, 0
            for e in ev["events"]:
                d0 = date.fromisoformat(e["d0"])
                t_ct = datetime.fromtimestamp(e["tau_ns"] / 1e9, tz=ZoneInfo("UTC")).astimezone(CT)
                tau_times.add(t_ct.strftime("%H:%M"))
                if t_ct.date() != d0:
                    mismatch_day += 1
                s = settle_minute(root, d0)
                s_open_ns = int(datetime.combine(d0, time(s // 60, s % 60), tzinfo=CT).timestamp() * 1e9)
                if e["tau_ns"] >= s_open_ns:
                    late += 1
                if not (lo <= d0 <= hi):
                    outside += 1
            ev_report[f"{th['id']}/{wname}"] = {
                "events": len(ev["events"]), "tau_ct_times": sorted(tau_times),
                "tau_at_or_after_settle_open": late, "tau_date_ne_d0": mismatch_day,
                "d0_outside_window": outside, "sha256": sha(p),
                "sha256_in_power_table": pw["events_sha256"].get(p) == sha(p)}
            if wname == "W_ext":
                report["rows"].append(row(f"events/{th['id']}/excluded_outside_window",
                                          ths[th["id"]]["unit_counts"]["excluded: event outside the window"],
                                          outside))
                report["rows"].append(row(f"events/{th['id']}/events", ths[th["id"]]["unit_counts"]["events"],
                                          len(ev["events"])))
                report["rows"].append(row(f"events/{th['id']}/tau_before_settlement_open (all)", True,
                                          late == 0))
    report["events"] = ev_report

    # 5. trend sum check against E.21's published series (all 17 roots)
    roots17 = [os.path.basename(p)[:-5] for p in sorted(os.listdir(f"{ROOT}/reports/stage_e23_trend_per_root"))]
    trend_all = {r: load(f"reports/stage_e23_trend_per_root/{r}.json") for r in roots17}
    for tname in ("T1", "T2"):
        pub = load(f"reports/stage_e21_runs/{tname}_result.json")["series"]["base"]
        total: dict[str, float] = {}
        for r in roots17:
            for d, v in trend_all[r][f"v_{tname}"].items():
                total[d] = total.get(d, 0.0) + v
        diffs = [abs(total.get(d, 0.0) - v) for d, v in pub]
        extra = [d for d in total if d not in {d for d, _ in pub}]
        report["rows"].append(row(f"trend/{tname}/max_abs_diff_vs_E21_series", 0.0, max(diffs), rel=0))
        report["rows"][-1]["match"] = max(diffs) <= 1e-12
        report["rows"][-1]["detail"] = f"{len(pub)} published dates; {len(extra)} per-root dates off the series"
        report["rows"].append(row(f"trend/{tname}/published_sha256_matches",
                                  trend["ZF"]["check"][tname]["published_sha256"],
                                  sha(f"reports/stage_e21_runs/{tname}_result.json")))
        report["rows"][-1]["match"] = report["rows"][-1]["run"] == report["rows"][-1]["mine"]

    # 6. D8 cost identity from the entry-day values: stress/base = (2 base - comm)/base
    vehicle = {"ZF": "ZF", "ZN": "ZN", "ZB": "ZB", "NQ": "MNQ"}
    cost_rows = {}
    for tid, th in ths.items():
        root = th["root"]
        prod = costs["readings"][vehicle[root]] if "readings" in costs and vehicle[root] in costs["readings"] else None
        b0 = th["series"]["base"][0]
        s0 = th["series"]["stress"][0]
        ratio = s0[1] / b0[1]
        cost_rows[tid] = {"first_date": b0[0], "base_value": b0[1], "stress_value": s0[1],
                          "observed_stress_over_base": ratio,
                          "implied_comm_share_of_base": 2.0 - ratio}
        if prod is not None:
            cost_rows[tid]["table_commission_rt_usd"] = prod.get("commission_rt_usd")
            cost_rows[tid]["table_tick_value_usd"] = prod.get("tick_value_usd")
    report["cost_identity"] = cost_rows
    report["notes"].append("cost table layout: top keys " + ", ".join(list(costs.keys())[:16]))

    # 7. markers, timestamps, order, registry, freeze
    def mtime(p: str) -> str:
        return datetime.fromtimestamp(os.stat(f"{ROOT}/{p}").st_mtime, tz=ZoneInfo("America/Vancouver")).isoformat(timespec="microseconds")

    mk_d, mk_c = load("reports/stage_e23_RUN_ONCE_discovery.json"), load("reports/stage_e23_RUN_ONCE_confirmation.json")
    reg_lines = open(f"{ROOT}/ledger/trial_registrations.jsonl").read().splitlines()
    r008 = json.loads(reg_lines[-1])
    git_freeze = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%H %cI", "--",
                                 "reports/stage_e23_freeze.json"], capture_output=True, text=True).stdout.strip()
    order = {
        "freeze_commit": git_freeze,
        "registration_time_local": r008["time_local"],
        "discovery_marker_written_local": mk_d["written_local"],
        "discovery_marker_mtime": mtime("reports/stage_e23_RUN_ONCE_discovery.json"),
        "discovery_result_mtime": mtime("reports/stage_e23_runs/discovery/discovery_result.json"),
        "discovery_started_local": disc["started_local"], "discovery_finished_local": disc["finished_local"],
        "confirmation_marker_written_local": mk_c["written_local"],
        "confirmation_marker_mtime": mtime("reports/stage_e23_RUN_ONCE_confirmation.json"),
        "confirmation_result_mtime": mtime("reports/stage_e23_runs/confirmation/confirmation_result.json"),
        "confirmation_started_local": conf["started_local"], "confirmation_finished_local": conf["finished_local"],
        "marker_modes": {p: oct(os.stat(f"{ROOT}/{p}").st_mode & 0o777) for p in
                         ("reports/stage_e23_RUN_ONCE_discovery.json", "reports/stage_e23_RUN_ONCE_confirmation.json")},
    }
    report["order"] = order
    st_d = os.stat(f"{ROOT}/reports/stage_e23_RUN_ONCE_discovery.json").st_mtime
    st_dr = os.stat(f"{ROOT}/reports/stage_e23_runs/discovery/discovery_result.json").st_mtime
    st_c = os.stat(f"{ROOT}/reports/stage_e23_RUN_ONCE_confirmation.json").st_mtime
    st_cr = os.stat(f"{ROOT}/reports/stage_e23_runs/confirmation/confirmation_result.json").st_mtime
    report["rows"].append(row("order/discovery_marker_before_result", True, st_d < st_dr))
    report["rows"].append(row("order/confirmation_marker_before_result", True, st_c < st_cr))
    report["rows"].append(row("order/registration_after_freeze_commit", True,
                              datetime.fromisoformat(r008["time_local"]) > datetime.fromisoformat(git_freeze.split()[1])))
    report["rows"].append(row("order/registration_before_discovery_marker", True,
                              datetime.fromisoformat(r008["time_local"]) < datetime.fromisoformat(mk_d["written_local"])))
    report["rows"].append(row("order/discovery_result_before_confirmation_marker", True, st_dr < st_c))
    freeze_sha = sha("reports/stage_e23_freeze.json")
    report["freeze_sha256"] = freeze_sha
    for name, got in (("discovery_marker", mk_d["freeze_sha256"]), ("confirmation_marker", mk_c["freeze_sha256"]),
                      ("discovery_result", disc["freeze_sha256"]), ("confirmation_result", conf["freeze_sha256"]),
                      ("registry_r008", r008["freeze_sha256"])):
        report["rows"].append(row(f"freeze_sha256/{name}", got, freeze_sha))
        report["rows"][-1]["match"] = got == freeze_sha
    reg_sha = sha("ledger/trial_registrations.jsonl")
    for name, got in (("discovery_marker", mk_d["registry"]["sha256"]), ("confirmation_marker", mk_c["registry"]["sha256"])):
        report["rows"].append(row(f"registry_sha256/{name}", got, reg_sha))
        report["rows"][-1]["match"] = got == reg_sha
    disc_sha = sha("reports/stage_e23_runs/discovery/discovery_result.json")
    report["rows"].append(row("confirmation_marker/discovery_result_sha256", mk_c["discovery_result_sha256"], disc_sha))
    report["rows"][-1]["match"] = mk_c["discovery_result_sha256"] == disc_sha
    report["rows"].append(row("registry/r008/n_before", r008["n_before"], 533))
    report["rows"].append(row("registry/r008/n_after", r008["n_after"], 538))
    report["rows"].append(row("registry/r008/label", r008["test"] == "E23" and r008["entry_id"] == "r008-E23", True))
    report["rows"].append(row("registry/r008/ids", sorted(r008["test_ids"]) == sorted(disc["test_ids"]) == sorted(reg["trigger_holds"][i]["id"] for i in range(5)), True))
    report["rows"].append(row("registry/lines", len(reg_lines), 9))
    report["rows"].append(row("registry/r008/harness_sha256", r008["harness_sha256"],
                              "dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4"))
    report["rows"][-1]["match"] = r008["harness_sha256"] == "dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4"
    n_prev = sum(1 for ln in reg_lines[:-1] if ln.strip())
    prev = json.loads(reg_lines[-2])
    report["rows"].append(row("registry/r007_n_after_equals_r008_n_before", prev.get("n_after"), r008["n_before"]))
    report["rows"][-1]["detail"] = f"previous entry {prev.get('entry_id')}; {n_prev} earlier lines"

    mism = [r for r in report["rows"] if not r["match"]]
    report["summary"] = {"rows": len(report["rows"]), "mismatches": len(mism),
                         "mismatch_names": [r["name"] for r in mism]}
    with open(f"{OUT_DIR}/recompute_file_based.json", "w") as f:
        json.dump(report, f, indent=1, default=str)
    print(json.dumps(report["summary"], indent=1))
    for r in mism:
        print("MISMATCH", r["name"], r["run"], r["mine"])
    print("W_cf gate:", json.dumps(gate, indent=None, default=str)[:1500])
    for n in report["notes"]:
        print("NOTE", n)
    print("events:", json.dumps(ev_report, indent=None)[:3000])
    print("cost identity:", json.dumps(cost_rows, indent=None)[:1500])
    print("order:", json.dumps(order, indent=None)[:1500])


if __name__ == "__main__":
    main()
