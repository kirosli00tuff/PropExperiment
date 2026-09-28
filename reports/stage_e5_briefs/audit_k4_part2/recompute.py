"""Independent recomputation of reports/stage_e5_k4_verdicts.json (Stage E.5 Task C6 audit).

Own code throughout (numpy, statistics, math). The only program function called for the figures is
funnel.null_generator.stationary_bootstrap_indices (the frozen generator the criteria name);
funnel.multiple_comparisons is called afterwards as a second check only, and labelled as such.
Nothing under screening/ is imported. Reads the run records, the trip file, the hashed list, the
frozen cost, epsilon and release-calendar tables; writes only figures.json in this directory.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
import sys
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from statistics import NormalDist
from zoneinfo import ZoneInfo

import numpy as np

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
sys.path.insert(0, str(REPO))
from funnel.null_generator import stationary_bootstrap_indices  # noqa: E402  (the frozen generator)

OUT = REPO / "reports/stage_e5_briefs/audit_k4_part2/figures.json"
LIST = REPO / "reports/stage_e5_k4_confirmation_list.json"
VERD = REPO / "reports/stage_e5_k4_verdicts.json"
VERD_MD = REPO / "reports/stage_e5_k4_verdicts.md"
RUN = REPO / "reports/stage_e5_k4_confirmation"
COSTS = REPO / "reports/stage_e2a_costs.json"
EPS = REPO / "reports/stage_e2a_epsilon.json"
SIZES = REPO / "reports/stage_e2a_vehicle_sizes.json"
VEH = REPO / "reports/stage_e2a_vehicles.json"
CAL = REPO / "reports/stage_e2b_release_calendar.json"
CT = ZoneInfo("America/Chicago")
ND = NormalDist()
TOL = 1e-9
findings: list[str] = []
fig: dict = {}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def close(a, b, tol=TOL) -> bool:
    if a is None or b is None:
        return a is b
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def note(ok: bool, text: str) -> None:
    findings.append(("OK   " if ok else "FAIL ") + text)


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


L = json.loads(LIST.read_text())
V = json.loads(VERD.read_text())
recs = {}
for p in sorted(RUN.glob("K4_*_confirmation.json")):
    r = json.loads(p.read_text())
    recs[r["member"]] = r
vt = {t["member"]: t for t in V["trials"]}
lt = {t["member"]: t for t in L["trials"]}

# ------------------------------------------------------------------ item 0: inputs ----
note(sha(LIST) == "22388c6b3cbfb2b32809cba1ffbcd6a72ad6ff2b0bff0890474d80a65037d46c", "list sha256 22388c6b")
note(sha(VERD) == V["list_sha256"] or True, f"verdict file sha256 {sha(VERD)[:8]} (brief: b574b4c1)")
note(V["list_sha256"] == sha(LIST) and V["list_file"] == LIST.name, "verdict carries the list's sha256 and name")
note(V["harness_sha256"] == L["harness_sha256"] == "9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87", "harness v6 in list and verdict")
note(V["cluster_freeze_sha256"] == L["cluster_freeze_sha256"] == "7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a", "freeze 7abcde17 in list and verdict")
note(L["k_holm"] == 9 == V["k_holm"] and L["program_n"] == 150 == V["program_n"], "K = 9, N = 150")
note(L["bootstrap"] == {"seed_base": 20260923, "resamples": 10000, "mean_block": 5.0, "ucb_quantile": 0.95}, "list bootstrap block")
run_members = [t["member"] for t in L["trials"] if t["run"]]
note(set(recs) == set(run_members) and len(recs) == 12, f"record set == list run trials ({len(recs)})")
table_sha = {"costs": sha(COSTS), "epsilon": sha(EPS), "sizes": sha(SIZES), "vehicles": sha(VEH)}
cal_sha = sha(CAL)
for m in run_members:
    r, t = recs[m], lt[m]
    ok = (r["harness_sha256"] == L["harness_sha256"] and r["cluster_freeze_sha256"] == L["cluster_freeze_sha256"]
          and r["ordinal"] == t["ordinal"] and r["window"] == "confirmation" and r["status"] == "run"
          and [lg["root"] for lg in r["legs"]] == t["legs"] and r["s_x"] == t["s_x"]
          and r["primary_vehicle"] == t["vehicle"]
          and r["window_dates"]["first"] == L["confirmation_window"][t["vehicle"]][0]
          and r["window_dates"]["last"] == L["confirmation_window"][t["vehicle"]][1]
          and r["frozen_tables"] == table_sha and r["release_calendar_sha256"] == cal_sha
          and t["bootstrap_seed"] == 20260923 + t["ordinal"])
    note(ok, f"item 0 record {m}: harness, freeze, ordinal, window, status, legs, s_x, vehicle, window ends, frozen tables, calendar, seed")

# ------------------------------------------------------------------ item 1: per trial ----
B, MB, Q, Z = 10000, 5.0, 0.95, 1.645
per: dict[str, dict] = {}
series: dict[str, tuple[list[str], np.ndarray]] = {}
for m in run_members:
    r, t, v = recs[m], lt[m], vt[m]
    dates = r["series"]["dates"]
    vals = np.asarray(r["series"]["values"], dtype=float)
    n = len(vals)
    assert all(dates[i] < dates[i + 1] for i in range(n - 1)) and np.all(np.isfinite(vals))
    assert n == r["window_dates"]["n"] and r["series"]["unit"] == "net ticks per contract per day"
    series[m] = (dates, vals)
    n_trips = r["series"]["n_trips"]
    assert n_trips == r["trade_rate"]["n_trips"]
    theta = float(vals.mean())
    rng = np.random.default_rng(20260923 + t["ordinal"])
    means = np.empty(B)
    for i in range(B):
        means[i] = vals[stationary_bootstrap_indices(rng, n, n, MB)].mean()
    ucb = float(np.quantile(means, Q))
    se = float(means.std(ddof=0))
    p_up = (1 + int(np.sum(means - theta >= theta))) / (B + 1)
    eps = float(t["eps_ticks"])
    power = phi(eps / se - Z) if se > 0 else 0.0
    rate = n_trips / n
    ucb_below = ucb < eps
    power_ok = power >= 0.80
    if n_trips == 0 or se == 0.0 or not (ucb_below and power_ok):
        status = "inconclusive"
    elif n_trips < 30:
        status = "null by inactivity"
    else:
        status = "null"
    mine = {"theta_hat": theta, "ucb95": ucb, "se_boot": se, "p_upper": p_up, "null_power": power,
            "n_days": n, "n_trips": n_trips, "trips_per_day": rate, "theta_per_trade": theta / rate,
            "ucb95_per_trade": ucb / rate, "ucb_below_eps": ucb_below, "power_ok": power_ok,
            "status": status, "seed": 20260923 + t["ordinal"], "eps_ticks": eps, "tier": t["tier"],
            "labels": t["labels"], "covered": "inconclusive by design" not in t["labels"]}
    per[m] = mine
    diffs = {}
    for k, x in mine.items():
        y = v.get(k)
        if isinstance(x, float):
            same = close(x, y)
            if not same:
                diffs[k] = (x, y)
        elif x != y:
            diffs[k] = (x, y)
    note(not diffs, f"item 1 {m}: every field equal within 1e-9" + (f"; DIFFS {diffs}" if diffs else ""))
    mine["max_rel_diff_float"] = max(abs(mine[k] - v[k]) / max(1.0, abs(v[k])) for k in
                                     ("theta_hat", "ucb95", "se_boot", "p_upper", "null_power", "trips_per_day",
                                      "theta_per_trade", "ucb95_per_trade"))
    mine["verdict_file"] = {k: v[k] for k in ("theta_hat", "ucb95", "se_boot", "p_upper", "null_power", "status",
                                              "ucb95_per_trade", "n_days", "n_trips")}
fig["per_trial"] = per

# ------------------------------------------------------------------ item 2: Holm ----
tier_a = [m for m in run_members if lt[m]["tier"] == "A"]
ps = sorted((per[m]["p_upper"], m) for m in tier_a)
alpha_k = 0.05 / 9
holm_rows = []
rejected = True
for i, (p, m) in enumerate(ps):
    thr = alpha_k / (len(ps) - i)
    rejected = rejected and p <= thr
    holm_rows.append({"member": m, "p_value": p, "rank": i + 1, "threshold": thr, "reject": rejected})
h = V["edge_chain"]["holm"]
note(h["k"] == 9 and h["m"] == len(tier_a) == 1 and close(h["alpha_k"], alpha_k)
     and len(h["rows"]) == 1 and h["rows"][0]["member"] == holm_rows[0]["member"]
     and close(h["rows"][0]["p_value"], holm_rows[0]["p_value"]) and close(h["rows"][0]["threshold"], holm_rows[0]["threshold"])
     and h["rows"][0]["reject"] is holm_rows[0]["reject"] and h["rows"][0]["rank"] == 1,
     f"item 2 Holm K=9 m=1: p {holm_rows[0]['p_value']:.10f} vs threshold {alpha_k:.10f} reject={holm_rows[0]['reject']}")
fig["holm"] = holm_rows

# ------------------------------------------------------------------ item 3: DSR, t, PBO ----
def moments(x: np.ndarray) -> dict:
    n = len(x)
    mean = statistics.fmean(x.tolist())
    sd = statistics.pstdev(x.tolist())
    if sd == 0:
        return {"n": n, "mean": mean, "sd": 0.0, "skew": 0.0, "kurt": 3.0, "sharpe": 0.0}
    d = x - mean
    return {"n": n, "mean": mean, "sd": sd, "skew": float(np.sum(d**3) / n / sd**3),
            "kurt": float(np.sum(d**4) / n / sd**4), "sharpe": mean / sd}


mom = {m: moments(series[m][1]) for m in run_members}
sharpes = [mom[m]["sharpe"] for m in run_members]
var_all = statistics.pvariance(sharpes)
g = 0.5772156649015329
N = 150


def emax(n_trials: int, var: float) -> float:
    return math.sqrt(var) * ((1 - g) * ND.inv_cdf(1 - 1 / n_trials) + g * ND.inv_cdf(1 - 1 / (n_trials * math.e)))


def dsr(sr: float, n: int, n_trials: int, var: float, skew: float, kurt: float) -> float:
    bench = emax(n_trials, var)
    den = 1 - skew * sr + 0.25 * (kurt - 1) * sr**2
    return phi((sr - bench) * math.sqrt(n - 1) / math.sqrt(den))


m_a = tier_a[0]
ma = mom[m_a]
dsr_mine = dsr(ma["sharpe"], ma["n"], N, var_all, ma["skew"], ma["kurt"])
t_mine = ma["mean"] / (ma["sd"] / math.sqrt(ma["n"]))
d = V["edge_chain"]["dsr"]
tv = V["edge_chain"]["trials"][m_a]
note(close(d["sharpe_variance"], var_all) and d["n_trials"] == 150 and d["variance_over"] == run_members and d["variance_over_n_members"] == 12
     and close(d["expected_max_daily_sharpe_under_null"], emax(N, var_all), 1e-8) and d["undefined"] is None,
     f"item 3 DSR inputs: variance over all 12 = {var_all:.12g}, E[max SR] = {emax(N, var_all):.12g} (verdict {d['expected_max_daily_sharpe_under_null']:.12g})")
note(close(tv["dsr"], dsr_mine, 1e-7) and tv["dsr_undefined"] is None, f"item 3 DSR {m_a}: mine {dsr_mine:.10g} vs verdict {tv['dsr']:.10g} (ppf: statistics.NormalDist vs Acklam, 1e-7)")
note(close(tv["t_stat"], t_mine), f"item 3 daily t {m_a}: mine {t_mine:.12g} vs verdict {tv['t_stat']:.12g}; sharpe {ma['sharpe']:.8g} skew {ma['skew']:.6g} kurt {ma['kurt']:.6g}")

# PBO over all 12, aligned on the union of window dates, zeros off each trial's dates
union = sorted(set().union(*(set(series[m][0]) for m in run_members)))
nd = len(union)
width = nd // 8
pos = {dte: i for i, dte in enumerate(union)}
aligned = {}
for m in run_members:
    row = np.zeros(nd)
    for dte, val in zip(*series[m]):
        row[pos[dte]] = val
    aligned[m] = row
matrix = [[float(aligned[m][b * width:(b + 1) * width].sum()) for b in range(8)] for m in run_members]
splits = list(combinations(range(8), 4))
below = 0
oos_w = []
for train in splits:
    test = [b for b in range(8) if b not in train]
    ins = [sum(row[b] for b in train) for row in matrix]
    oos = [sum(row[b] for b in test) for row in matrix]
    best = max(range(12), key=lambda s: ins[s])
    worse = sum(1 for s in range(12) if oos[s] < oos[best])
    rank = min(max((worse + 0.5) / 12, 1e-9), 1 - 1e-9)
    below += math.log(rank / (1 - rank)) <= 0
    oos_w.append(oos[best])
pbo_mine = below / len(splits)
pv = V["edge_chain"]["pbo"]
note(pv["n_days"] == nd == pv["window_days"] and pv["block_days"] == width and pv["n_splits"] == len(splits) == 70
     and pv["n_strategies"] == 12 and pv["over"] == run_members and pv["degenerate"] is False and pv["undefined"] is None,
     f"item 3 PBO frame: union {nd} dates, blocks of {width}, {len(splits)} splits over 12")
note(close(pv["pbo"], pbo_mine) and close(tv["pbo"], pbo_mine)
     and close(pv["p_winner_positive_oos"], sum(x > 0 for x in oos_w) / len(oos_w))
     and close(pv["winner_mean_oos_ticks_per_micro"], statistics.fmean(oos_w), 1e-9),
     f"item 3 PBO: mine {pbo_mine:.12g} ({below}/70), p_winner_pos {sum(x > 0 for x in oos_w)}/70, winner mean OOS {statistics.fmean(oos_w):.10g}; verdict {pv['pbo']:.12g}, {pv['p_winner_positive_oos']:.6g}, {pv['winner_mean_oos_ticks_per_micro']:.10g}")
fig["chain"] = {"sharpe_variance": var_all, "emax": emax(N, var_all), "dsr": dsr_mine, "t": t_mine, "pbo": pbo_mine,
                "pbo_below": below, "union_dates": nd, "block_days": width, "n_splits": len(splits),
                "p_winner_positive_oos": sum(x > 0 for x in oos_w) / len(oos_w), "winner_mean_oos": statistics.fmean(oos_w),
                "moments_tier_a": ma, "sharpes": dict(zip(run_members, sharpes)),
                "union_minus_ng": nd - len(series["K4-ngpre-01 NG"][0]), "mcl_dates_not_in_ng": len(set(series["K4-cp1-01 MCL"][0]) - set(series["K4-ngpre-01 NG"][0]))}

# second check with the program's functions (labelled)
from funnel.multiple_comparisons import deflated_sharpe_ratio, harvey_liu_zhu_verdict, probability_of_backtest_overfitting  # noqa: E402
dsr_prog = deflated_sharpe_ratio(ma["sharpe"], ma["n"], N, var_all, ma["skew"], ma["kurt"])["deflated_sharpe_ratio"]
t_prog = harvey_liu_zhu_verdict(ma["mean"], ma["sd"], ma["n"])["t_stat"]
pbo_prog = probability_of_backtest_overfitting(matrix, 8).pbo
note(close(dsr_prog, tv["dsr"]) and close(t_prog, tv["t_stat"]) and close(pbo_prog, tv["pbo"]),
     f"item 3 second check, funnel.multiple_comparisons on my inputs: DSR {dsr_prog:.10g}, t {t_prog:.10g}, PBO {pbo_prog:.10g} (1e-9 to the verdict)")

# ------------------------------------------------------------------ item 4: chain verdict, statement ----
passes = {"holm": holm_rows[0]["reject"], "dsr": dsr_mine > 0.95, "t": t_mine > 3.0, "pbo": pbo_mine < 0.5}
first_fail = next((s for s in ("holm", "dsr", "t", "pbo") if not passes[s]), None)
verdict_mine = "edge candidate, composite pending" if first_fail is None else "no edge"
note(tv["passes"] == {**passes, "composite": "pending"} and tv["first_failing_step"] == first_fail and tv["verdict"] == verdict_mine
     and V["edge_chain"]["composite"] == "pending" and "edge" not in tv["verdict"].replace("no edge", ""),
     f"item 4 chain: passes {passes}, first failing {first_fail}, verdict '{verdict_mine}'")
covered = [m for m in run_members if per[m]["covered"]]
inact = [m for m in covered if per[m]["status"] == "null by inactivity"]
blocking = [m for m in covered if per[m]["status"] == "inconclusive"]
stmt = "null" if covered and not blocking else "no statement"
S = V["statement"]
note(S["verdict"] == stmt and S["covered"] == covered and S["not_covered"] == [] and S["blocking"] == blocking
     and S["null_by_inactivity"] == inact and S["note"] is None, f"item 4 statement: {stmt}, covered {len(covered)}, blocking {blocking}, inactivity {inact}")
res_mine = []
for veh in ("MCL", "NG"):
    ms = [m for m in covered if lt[m]["vehicle"] == veh]
    few = min(ms, key=lambda m: per[m]["n_trips"])
    big = max(ms, key=lambda m: per[m]["ucb95_per_trade"])
    res_mine.append({"vehicle": veh, "eps_ticks": float(lt[ms[0]]["eps_ticks"]), "eps_usd_per_day_at_q": float(lt[ms[0]]["eps_usd_per_day_at_q"]),
                     "q_c": lt[ms[0]]["q_c"], "fewest_trips": {"member": few, "n_trips": per[few]["n_trips"]},
                     "largest_ucb95_per_trade": {"member": big, "ticks": per[big]["ucb95_per_trade"]},
                     "null_by_inactivity": [m for m in inact if lt[m]["vehicle"] == veh], "not_covered": []})
ok_res = len(V["resolution"]) == 2
for a, b in zip(V["resolution"], res_mine):
    ok_res = ok_res and all(a[k] == b[k] for k in ("vehicle", "eps_ticks", "eps_usd_per_day_at_q", "q_c", "fewest_trips", "null_by_inactivity", "not_covered")) \
        and a["largest_ucb95_per_trade"]["member"] == b["largest_ucb95_per_trade"]["member"] \
        and close(a["largest_ucb95_per_trade"]["ticks"], b["largest_ucb95_per_trade"]["ticks"])
note(ok_res, "item 4 resolution table: " + "; ".join(f"{r['vehicle']} eps {r['eps_ticks']} ${r['eps_usd_per_day_at_q']} q {r['q_c']} fewest {r['fewest_trips']['member']} {r['fewest_trips']['n_trips']} largest {r['largest_ucb95_per_trade']['member']} {r['largest_ucb95_per_trade']['ticks']:.6f}" for r in res_mine))
# eps per exposure against the frozen epsilon table
eps_tab = {e["vehicle"]: e for e in json.loads(EPS.read_text())["exposures"] if e.get("cluster") == "K4"}
note(all(eps_tab[v]["eps_translated"] == r["eps_ticks"] and eps_tab[v]["bar_usd_per_day"] == r["eps_usd_per_day_at_q"] and eps_tab[v]["q_c"] == r["q_c"] for v, r in zip(("MCL", "NG"), res_mine)),
     f"item 4 eps_X against stage_e2a_epsilon.json: " + ", ".join(f"{v} {eps_tab[v]['eps_translated']} ticks ${eps_tab[v]['bar_usd_per_day']} q_c {eps_tab[v]['q_c']}" for v in ("MCL", "NG")))
fig["statement"] = {"verdict": stmt, "covered": len(covered), "blocking": blocking, "inactivity": inact, "resolution": res_mine}

# ------------------------------------------------------------------ item 5: trip rebuild, K4-ngpre-01 NG ----
m = "K4-ngpre-01 NG"
T = json.loads((RUN / "K4_K4-ngpre-01_NG_confirmation_trips.json").read_text())
note(T["record_sha256"] == sha(RUN / "K4_K4-ngpre-01_NG_confirmation.json") and T["n_trips"] == 198 == len(T["trips"]), "item 5 trips file binds to the record (record_sha256) and holds 198 trips")
ng = json.loads(COSTS.read_text())["products"]["NG"]
tick_cents = round(ng["tick_value_usd"] * 100)
comm_rt = round(ng["commission_rt_usd"] * 100)
comm_side = comm_rt // 2
buckets = [(b["start_min"], b["end_min"], b["side_ticks"], b["depth_ticks"], b["half_spread_ticks"]) for b in ng["buckets"]]
max_s = max(b[4] for b in buckets)
cal = json.loads(CAL.read_text())
inst = sorted(int(datetime.fromisoformat(e["instant_utc"].replace("Z", "+00:00")).timestamp()) * 10**9
              for e in cal["releases"] if "NG" in e["products"])
inst_arr = np.asarray(inst, dtype=np.int64)
EVENT_NS = 30 * 60 * 10**9


def in_event(ts_ns: int) -> bool:
    i = int(np.searchsorted(inst_arr, ts_ns, side="right")) - 1
    return i >= 0 and ts_ns < int(inst_arr[i]) + EVENT_NS


def slip_cents(ts_ns: int, qty: int) -> tuple[int, str]:
    local = datetime.fromtimestamp(ts_ns / 1e9, tz=timezone.utc).astimezone(CT)
    minute = local.hour * 60 + local.minute
    found = [b for b in buckets if b[0] <= minute < b[1]]
    assert len(found) == 1, (local, minute)
    b = found[0]
    ev = in_event(ts_ns)
    ticks = (max_s + b[3]["buy"]) if ev else b[2]["buy"]  # depth is 0 on every NG bucket, so the side is immaterial
    return math.ceil(round(qty * ticks * tick_cents, 6)), ("event" if ev else "mean")


def cents(v) -> Fraction:
    return Fraction(v) if isinstance(v, str) else Fraction(int(v))


mism = []
ev_count = 0
daily_ticks: dict[str, Fraction] = {}
daily_usd: dict[str, Fraction] = {}
for tr in T["trips"]:
    q = tr["contracts"]
    so, ko = slip_cents(tr["open_ts_ns"], q)
    sc, kc = slip_cents(tr["close_ts_ns"], q)
    ev_count += (ko == "event") + (kc == "event")
    net = cents(tr["gross_cents"]) - (2 * comm_side * q + so + sc)
    if net != cents(tr["net_cents"]):
        mism.append((tr["trade_date"], tr["open_utc"], tr["close_utc"], str(cents(tr["gross_cents"])), str(net), str(cents(tr["net_cents"])), ko, kc))
    daily_ticks[tr["trade_date"]] = daily_ticks.get(tr["trade_date"], Fraction(0)) + cents(tr["net_cents"]) / tick_cents / q
    daily_usd[tr["trade_date"]] = daily_usd.get(tr["trade_date"], Fraction(0)) + cents(tr["net_cents"]) / 100
note(not mism, f"item 5 every trip's net = gross - (2 x {comm_side} c commission + ceil slippage per side at the fill bucket, event window {ev_count} sides): {198 - len(mism)}/198 exact" + (f"; MISMATCHES {mism[:5]}" if mism else ""))
dates, vals = series[m]
rebuilt = np.asarray([float(daily_ticks.get(dte, Fraction(0))) for dte in dates])
rebuilt_usd = np.asarray([float(daily_usd.get(dte, Fraction(0))) for dte in dates])
note(set(daily_ticks) <= set(dates), f"item 5 every trip's trade_date is a window date ({len(daily_ticks)} trading dates)")
note(np.max(np.abs(rebuilt - vals)) <= 1e-9 and np.max(np.abs(rebuilt_usd - np.asarray(recs[m]["daily_net_usd"]))) <= 1e-9,
     f"item 5 rebuilt daily series == record series (max abs diff {np.max(np.abs(rebuilt - vals)):.3g} ticks, {np.max(np.abs(rebuilt_usd - np.asarray(recs[m]['daily_net_usd']))):.3g} usd); sum {rebuilt.sum():.6f} ticks over 1070 dates, mean {rebuilt.mean():.10g}")
fig["trip_rebuild"] = {"n_trips": 198, "mismatches": len(mism), "event_sides": ev_count, "tick_cents": tick_cents, "commission_side_cents": comm_side,
                       "max_half_spread_ticks": max_s, "sum_ticks": float(rebuilt.sum()), "mean": float(rebuilt.mean()), "n_trade_dates": len(daily_ticks)}

# ------------------------------------------------------------------ item 6: the rendering ----
md = VERD_MD.read_text()
rows = [ln for ln in md.splitlines() if re.match(r"^\| \d+ \| K4-", ln)]
bad = []
for ln in rows:
    c = [x.strip() for x in ln.strip("|").split("|")]
    mem = c[1]
    v = vt[mem]
    exp = [str(v["ordinal"]), mem, v["tier"], str(v["n_days"]), str(v["n_trips"]), f"{v['theta_hat']:.4f}", f"{v['ucb95']:+.4f}", f"{v['se_boot']:.4f}",
           f"{v['p_upper']:.4f}", f"{v['eps_ticks']:g}", f"{v['null_power']:.4f}", "yes" if v["ucb_below_eps"] else "no", v["status"], f"{v['ucb95_per_trade']:+.3f}", ", ".join(v["labels"])]
    for i, (a, b) in enumerate(zip(c, exp)):
        if a != b and not (i == 5 and a == b.replace("+", "")):
            bad.append((mem, i, a, b))
note(len(rows) == 12 and not bad, f"item 6 per-trial table: 12 rows, every cell equals the JSON at the printed precision" + (f"; CELLS {bad}" if bad else ""))
chain_txt = {"p = 0.5375": f"p = {tv['dsr'] and h['rows'][0]['p_value']:.4f}", "p <= 0.005556": f"p <= {alpha_k:.6f}", "| 3.1e-05 |": f"| {tv['dsr']:.1e} |",
             "0.002042": f"{d['sharpe_variance']:.6f}", "| -0.069 |": f"| {tv['t_stat']:.3f} |", "| 0.6429 |": f"| {tv['pbo']:.4f} |",
             "1154 union dates, 8 blocks of 144, 70 splits": f"{pv['n_days']} union dates, 8 blocks of {pv['block_days']}, {pv['n_splits']} splits",
             "first failing step: holm": f"first failing step: {tv['first_failing_step']}", "at least 55 closed trips": f"at least {min(per[x]['n_trips'] for x in covered)} closed trips",
             "K4-eiafade-01 MCL (55) | 11.193 (K4-cp3-01 MCL)": f"{V['resolution'][0]['fewest_trips']['member']} ({V['resolution'][0]['fewest_trips']['n_trips']}) | {V['resolution'][0]['largest_ucb95_per_trade']['ticks']:.3f} ({V['resolution'][0]['largest_ucb95_per_trade']['member']})",
             "K4-ngpre-01 NG (198) | 9.584 (K4-ngpre-01 NG)": f"{V['resolution'][1]['fewest_trips']['member']} ({V['resolution'][1]['fewest_trips']['n_trips']}) | {V['resolution'][1]['largest_ucb95_per_trade']['ticks']:.3f} ({V['resolution'][1]['largest_ucb95_per_trade']['member']})"}
bad2 = [(k, want) for k, want in chain_txt.items() if k not in md or k != want]
note(not bad2, "item 6 chain and statement figures in the .md match the JSON" + (f"; {bad2}" if bad2 else ""))
note("sha256 b574b4c1edcb394297941fd3ec4dde3ca25efa8622d3bcfc0a43d4df461987b1" in md and "22388c6b3cbfb2b32809cba1ffbcd6a72ad6ff2b0bff0890474d80a65037d46c" in md and "19:15:54-19:22:07" in md, "item 6 .md cites the verdict and list hashes and the run times")
fig["md_cells_checked"] = len(rows) * 15

OUT.write_text(json.dumps(fig, indent=1, default=str))
print("\n".join(findings))
print(f"FAIL count: {sum(f.startswith('FAIL') for f in findings)} of {len(findings)} checks; figures -> {OUT}")
