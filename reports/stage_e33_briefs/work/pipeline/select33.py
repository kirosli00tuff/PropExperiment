"""Stage E.33 P8 selection rule, mechanical (ProofCoder).

Inputs: the OOF daily series X_D (796 values) of every configuration and its trade counts (P6.2), failed
configurations included (they fail G1). Output: every configuration on every gate, the funnel (each gate alone
and in order G1..G5), the total-order ranking, the Tier A walk and the Tier B walk, and reports that are never
gates (PBO, BH and Holm on one-sided p-values of the daily t, the P7.2 reference thresholds).

Protocol: reports/stage_e32_discovery_protocol.md P8 (and P6.2, P7.2, 0.3). Statistics of daily series are
screening.stage_e_verdict.moments() and t_stat() (population SD); the DSR is
funnel.multiple_comparisons.deflated_sharpe_ratio; b_test comes from p7_final.py at the registered N
(unrounded). Readings are marked `# READING Q<n>` and logged in ProofCoder_readings.md.

  uv run python select33.py --root DIR --all --n 838 --out FILE.json
  uv run python select33.py --root DIR --ids E33-S5F15L001A ... --n 838 --out FILE.json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
P7_DIR = REPO / "reports" / "stage_e32_briefs" / "protocol"
for _p in (str(REPO), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from funnel.multiple_comparisons import deflated_sharpe_ratio  # noqa: E402
from screening.stage_e_verdict import moments, t_stat  # noqa: E402
from screening.stage_e_verdict import pbo as verdict_pbo  # noqa: E402

# ---------------------------------------------------------------- declared constants (P8, P7)
T_DISC = 796
N_EXPECTED = 838
B_TEST_838_DISPLAYED = 0.164882        # P7.2: p7_final.py's unrounded value at N 838, shown to 6 decimals
G1_MIN_TRADES_PER_DATE = 1.0           # at least 796 trades
G1_MIN_SHARE_DATES = 0.5               # a trade on at least 50% of the OOF dates
G2_MIN_NET = 0.50                      # ticks per trade (Topstep, market, L = 1 s)
G3_DSR = 0.95                          # DSR > 0.95 (strict, the program's sign)
G5A_MIN_QUARTERS, G5A_N_QUARTERS = 9, 13
G5B_MAX_MONTH_SHARE = 0.25
G5C_MIN_T = 2.5
N_MONTHS = 39
TIER_A_MAX, TIER_B_N, RHO_MAX = 3, 2, 0.70
GATES = ("G1", "G2", "G3", "G4", "G5")
Z = NormalDist()

SET_INDEX = {"S1": 1, "S2": 2, "S3": 3, "S4": 4, "S5": 5}
LABEL_KEY = {"F05": (5, 0), "F15": (15, 0), "F30": (30, 0), "F60": (60, 0), "T15": (15, 1), "T30": (30, 1)}
GRID_ORDER = ("L001A", "L001E", "L010A", "L010E", "L100A", "L100E", "G2050", "G2200", "G3050", "G3200")
PREFIXES = ("E33", "E33A")


def parse_id(cid: str) -> dict:
    """P7.1 id E33-<set><label><grid> -> its parts (the ranking's tie-breaks)."""
    prefix, _, body = cid.partition("-")
    if prefix not in PREFIXES or len(body) != 10:
        raise ValueError(f"not a P7.1 id: {cid!r}")
    st, lab, grid = body[:2], body[2:5], body[5:]
    if st not in SET_INDEX or lab not in LABEL_KEY or grid not in GRID_ORDER:
        raise ValueError(f"not a P7.1 id: {cid!r}")
    return {"set": st, "label": lab, "grid": grid, "family": "LOGIT" if grid[0] == "L" else "LGBM",
            "h": LABEL_KEY[lab][0]}


# ---------------------------------------------------------------- thresholds at N (P7.2)
@lru_cache(maxsize=8)
def b_test_at(n_trials: int) -> float:
    """b_test = max(daily t > 3.0 bar, DSR >= 0.95 at N with V = 1/(T_test - 1), normal moments) exactly as
    p7_final.py's report() computes it, unrounded (P7.2, P8 G4)."""
    if str(P7_DIR) not in sys.path:
        sys.path.insert(0, str(P7_DIR))
    import p7_final as p7
    t_test = p7.trade_dates(*p7.TEST_MBO) - p7.BURN_IN
    if t_test != 870:
        raise AssertionError(f"T_test {t_test} != 870 (P9)")
    v_t = 1 / (t_test - 1)
    b = max(3.0 / math.sqrt(t_test), p7.required_sharpe(n_trials, t_test, v_t, 0.0, 3.0))
    if n_trials == N_EXPECTED and round(b, 6) != B_TEST_838_DISPLAYED:
        raise AssertionError(f"b_test at N 838 = {b!r}, protocol pins {B_TEST_838_DISPLAYED}")
    return b


def se_sharpe(sr: float, skew: float, kurt: float, t: int) -> float | None:
    """P8 G4: se(SR_d) = sqrt((1 - g3 SR + (g4 - 1)/4 SR^2)/(T - 1)); None if the radicand is not positive."""
    rad = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    if not rad > 0:  # READING Q4: a non-positive radicand leaves se undefined -> G4 fails
        return None
    return math.sqrt(rad / (t - 1))


# ---------------------------------------------------------------- calendar groupings (P8 G5)
def quarter_key(d: str) -> str:
    """Calendar quarters Dec-Feb, Mar-May, Jun-Aug, Sep-Nov, named by their first month."""
    y, m = int(d[:4]), int(d[5:7])
    if m == 12:
        return f"{y:04d}-12"
    if m <= 2:
        return f"{y - 1:04d}-12"
    return f"{y:04d}-{3 * (m // 3):02d}"


def _groups(dates, keyf) -> dict:
    out: dict = {}
    for j, d in enumerate(dates):
        out.setdefault(keyf(d), []).append(j)
    return out


def tercile_slices(dates, sigma) -> list:
    """G5 (d): dates sorted by sigma_ZM(D) ascending, ties by date; ranks 1-265, 266-530, 531-796."""
    order = sorted(range(len(dates)), key=lambda j: (float(sigma[j]), dates[j]))
    n3 = len(dates) // 3
    return [order[:n3], order[n3:2 * n3], order[2 * n3:]]


# ---------------------------------------------------------------- one configuration
def _defined(x) -> bool:
    return x is not None


def evaluate(cid: str, x, n_trades, dates, sigma, n_trials: int, b_test: float, *, strict: bool = True) -> dict:
    """Every gate for one configuration. x None = failed configuration (P5): it fails every gate.
    strict: the production calendar (796 dates, 13 quarters, 39 months) is asserted."""
    t = len(dates)
    res = {"config": cid, **parse_id(cid), "failed": x is None}
    if x is None:
        res.update({"defined": False, "constant": None, "gates": dict.fromkeys(GATES, False), "sharpe": None,
                    "trade_count": 0})
        return res
    x = [float(v) for v in x]
    nt = [int(v) for v in n_trades]
    if len(x) != t or len(nt) != t:
        raise ValueError(f"{cid}: series of {len(x)} values, {t} dates")
    mom = moments(x)
    tt = t_stat(mom)
    count = sum(nt)
    with_trade = sum(1 for k in nt if k > 0)
    total = math.fsum(x)
    res.update({"defined": True, "constant": mom["sd"] == 0, "moments": mom, "sharpe": mom["sharpe"],
                "t": tt, "trade_count": count, "trades_per_date": count / t, "dates_with_trade": with_trade,
                "share_dates_with_trade": with_trade / t, "total_net": total,
                # READING Q2: mean net per trade = sum of the daily nets / trade count (the trades' nets summed)
                "mean_net_per_trade": total / count if count else None})
    g = {}
    # G1 activity: count >= 1.0 x T and 2 x dates_with_trade >= T, integer comparisons
    g["G1"] = count >= G1_MIN_TRADES_PER_DATE * t and with_trade >= G1_MIN_SHARE_DATES * t
    g["G2"] = res["mean_net_per_trade"] is not None and res["mean_net_per_trade"] >= G2_MIN_NET
    # G3 significance: DSR at N, V = 1/(T - 1), T = T_disc, own skewness and raw kurtosis; undefined fails
    dsr = None
    if mom["sd"] > 0:
        try:
            dsr = deflated_sharpe_ratio(mom["sharpe"], t, n_trials, 1.0 / (t - 1), mom["skew"],
                                        mom["kurtosis"])["deflated_sharpe_ratio"]
        except ValueError:
            dsr = None
    res["dsr"] = dsr
    g["G3"] = dsr is not None and dsr > G3_DSR
    # G4 power: SR - se(SR) >= b_test (unrounded)
    se = se_sharpe(mom["sharpe"], mom["skew"], mom["kurtosis"], t) if mom["sd"] > 0 else None
    res["se"] = se
    res["sr_lower"] = None if se is None else mom["sharpe"] - se
    g["G4"] = se is not None and mom["sharpe"] - se >= b_test
    g5, detail = g5_stability(x, dates, sigma, strict=strict)
    res["g5"] = detail
    g["G5"] = g5
    res["gates"] = g
    return res


def g5_stability(x: list, dates, sigma, *, strict: bool = True) -> tuple:
    """P8 G5 (a)-(d); returns (pass, details)."""
    quarters = _groups(dates, quarter_key)
    months = _groups(dates, lambda d: d[:7])
    if strict and (len(quarters) != G5A_N_QUARTERS or len(months) != N_MONTHS or len(dates) != T_DISC):
        raise AssertionError(f"{len(dates)} dates, {len(quarters)} quarters, {len(months)} months")
    q_means = {k: math.fsum(x[j] for j in idx) / len(idx) for k, idx in quarters.items()}
    a_count = sum(1 for v in q_means.values() if v > 0)
    a = a_count >= G5A_MIN_QUARTERS
    total = math.fsum(x)
    m_sums = {k: math.fsum(x[j] for j in idx) for k, idx in months.items()}
    max_month = max(m_sums.values())
    b = total > 0 and max_month <= G5B_MAX_MONTH_SHARE * total  # "no month above 25% of the total"
    lomo = {}
    for k, idx in months.items():
        drop = set(idx)
        rest = [x[j] for j in range(len(x)) if j not in drop]
        lomo[k] = t_stat(moments(rest)) if len(rest) >= 2 else None
    c = all(v is not None and v >= G5C_MIN_T for v in lomo.values())  # READING Q5: undefined t fails
    terc = [math.fsum(x[j] for j in s) / len(s) for s in tercile_slices(dates, sigma)]
    d = all(v > 0 for v in terc)
    lomo_def = [v for v in lomo.values() if v is not None]
    return (a and b and c and d), {
        "a": a, "quarters_positive": a_count, "n_quarters": len(quarters), "quarter_means": q_means,
        "b": b, "total": total, "max_month_sum": max_month,
        "max_month_share": (max_month / total) if total > 0 else None,
        "c": c, "min_lomo_t": min(lomo_def) if lomo_def else None,
        "lomo_undefined": sum(1 for v in lomo.values() if v is None),
        "d": d, "tercile_means": terc}


# ---------------------------------------------------------------- funnel, ranking, walks
def funnel(results: list) -> dict:
    alone = {gname: sum(1 for r in results if r["gates"][gname]) for gname in GATES}
    in_order, alive = {}, list(results)
    for gname in GATES:
        alive = [r for r in alive if r["gates"][gname]]
        in_order["..".join(("G1", gname)) if gname != "G1" else "G1"] = len(alive)
    return {"n_configs": len(results), "alone": alone, "in_order": in_order,
            "failed_configs": sum(1 for r in results if r["failed"])}


def rank_key(r: dict) -> tuple:
    """P8 total order: SR_d rounded to 4 decimals (Python round, half to even) descending; fewer trades per
    date; LOGIT before LGBM; lower set index; shorter horizon (FH before TB at equal h); earlier grid point.
    Configurations without a series sort last (they are never ranked or walked)."""
    lab = LABEL_KEY[r["label"]]
    if not r["defined"]:
        return (1, 0.0, 0, 0, SET_INDEX[r["set"]], lab[0], lab[1], GRID_ORDER.index(r["grid"]), r["config"])
    return (0, -round(r["sharpe"], 4), r["trade_count"], 0 if r["family"] == "LOGIT" else 1,
            SET_INDEX[r["set"]], lab[0], lab[1], GRID_ORDER.index(r["grid"]), r["config"])


def pearson(a, b) -> float | None:
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    if np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def _corr_ok(cid: str, taken: list, series: dict) -> tuple:
    rhos = {o: pearson(series[cid], series[o]) for o in taken}
    # READING Q6: an undefined correlation (a constant series) never qualifies in a walk
    ok = all(v is not None and v <= RHO_MAX for v in rhos.values())
    return ok, rhos


def tier_a_walk(ranked_pass: list, series: dict) -> tuple:
    """Walk the passing configurations in rank order; take one if rho <= 0.70 with every one taken; stop at 3.
    Returns (taken, log, index in ranked_pass of the last configuration examined or -1)."""
    taken, log, last = [], [], -1
    for pos, cid in enumerate(ranked_pass):
        last = pos
        ok, rhos = _corr_ok(cid, taken, series)
        log.append({"config": cid, "taken": ok, "rho_with_taken": rhos})
        if ok:
            taken.append(cid)
            if len(taken) == TIER_A_MAX:
                break
    return taken, log, last


def tier_b_walk(ranked_all: list, by_id: dict, tier_a: list, series: dict, start: int) -> dict:
    """P8 Tier B: walk ranked_all (all configurations, gates ignored) from position `start`, skipping failed and
    constant series and those taken, taking the next two with rho <= 0.70 against all taken (Tier A and B); if
    fewer than two qualify, fill with the highest-ranked remaining configurations with a defined series and
    report their correlations."""
    taken, picked, log = list(tier_a), [], []
    for cid in ranked_all[start:]:
        if len(picked) == TIER_B_N:
            break
        r = by_id[cid]
        if cid in taken or not r["defined"] or r["constant"]:
            continue
        ok, rhos = _corr_ok(cid, taken, series)
        log.append({"config": cid, "taken": ok, "rho_with_taken": rhos})
        if ok:
            taken.append(cid)
            picked.append(cid)
    filled = []
    for cid in ranked_all:
        if len(picked) + len(filled) >= TIER_B_N:
            break
        r = by_id[cid]
        if cid in taken or cid in filled or not r["defined"]:
            continue
        filled.append(cid)
    fill_rhos = {cid: {o: pearson(series[cid], series[o]) for o in taken + [f for f in filled if f != cid]}
                 for cid in filled}
    return {"walked": picked, "filled": filled, "tier_b": picked + filled, "log": log,
            "fill_correlations": fill_rhos, "start_position": start}


# ---------------------------------------------------------------- reports (never gates)
def one_sided_p(t: float | None) -> float:
    """READING Q7: one-sided p = 1 - Phi(t) of the daily t (normal reference; 795 df make Student t
    indistinguishable); a configuration without a t (failed or constant) enters with p = 1."""
    return 1.0 if t is None else 1.0 - Z.cdf(t)


def bh_holm(results: list, q: float = 0.05) -> dict:
    p = {r["config"]: one_sided_p(r.get("t")) for r in results}
    m = len(p)
    order = sorted(p, key=lambda k: (p[k], k))
    k_bh = 0
    for rank, cid in enumerate(order, 1):
        if p[cid] <= rank * q / m:
            k_bh = rank
    holm = []
    for rank, cid in enumerate(order, 1):
        if p[cid] <= q / (m - rank + 1):
            holm.append(cid)
        else:
            break
    return {"m": m, "q": q, "bh_rejected": order[:k_bh], "holm_rejected": holm,
            "min_p": p[order[0]] if order else None, "p_values": p,
            "note": "reports only, never gates (P8); one-sided p = 1 - Phi(daily t)"}


def reference_thresholds(m: int, n_trials: int) -> dict:
    """P7.2 reference z thresholds (one-sided 0.05); none is a gate."""
    c_m = sum(1 / j for j in range(1, m + 1))
    zq = lambda a: Z.inv_cdf(1 - a)  # noqa: E731
    return {"bonferroni_holm_step1_m": zq(0.05 / m), "bh_rank1": zq(0.05 / m),
            "by_rank1": zq(0.05 / (m * c_m)), "by_c_m": c_m, "bonferroni_at_N": zq(0.05 / n_trials),
            "test_holm_K9": {k: zq(0.05 / (9 * k)) for k in (1, 2, 3)}, "hlz_t": 3.0, "m": m, "N": n_trials}


def pbo_report(results: list, series: dict) -> dict:
    """CSCV PBO over the configurations with a series (READING Q8: failed ones have none and are left out)."""
    use = {r["config"]: np.asarray(series[r["config"]], dtype=np.float64) for r in results if r["defined"]}
    if len(use) < 2:
        return {"n_strategies": len(use), "pbo": None, "degenerate": True}
    out = verdict_pbo(use)
    return {k: out[k] for k in ("n_strategies", "n_days", "block_days", "pbo", "n_splits", "degenerate",
                                "winner_mean_oos_ticks_per_micro", "p_winner_positive_oos")}


# ---------------------------------------------------------------- the whole rule
def select(configs: dict, dates, sigma, n_trials: int, *, b_test: float | None = None, strict: bool = True,
           tier_b_reading: str = "continue") -> dict:
    """configs: {cid: None (failed) or (x, n_trades)}. Returns the full P8 result (JSON-serialisable)."""
    dates = [str(d) for d in dates]
    if len(set(dates)) != len(dates) or dates != sorted(dates):
        raise ValueError("dates must be unique and sorted")
    if b_test is None:
        b_test = b_test_at(n_trials)
    results = []
    for cid, val in configs.items():
        x, nt = (None, None) if val is None else val
        results.append(evaluate(cid, x, nt, dates, sigma, n_trials, b_test, strict=strict))
    by_id = {r["config"]: r for r in results}
    series = {cid: list(map(float, val[0])) for cid, val in configs.items() if val is not None}
    for r in results:
        r["passes_all"] = all(r["gates"].values())
    ranked_all = [r["config"] for r in sorted(results, key=rank_key)]
    ranked_pass = [c for c in ranked_all if by_id[c]["passes_all"]]
    tier_a, a_log, last = tier_a_walk(ranked_pass, series)
    start_continue = ranked_all.index(ranked_pass[last]) + 1 if last >= 0 else 0
    tb = {"continue": tier_b_walk(ranked_all, by_id, tier_a, series, start_continue),
          "restart": tier_b_walk(ranked_all, by_id, tier_a, series, 0)}
    if tier_b_reading not in tb:
        raise ValueError(f"tier_b_reading {tier_b_reading!r}")
    # READING Q9: the reported best configuration = first in the total order among non-constant series
    best = next((c for c in ranked_all if by_id[c]["defined"] and not by_id[c]["constant"]), None)
    return {"n_trials": n_trials, "b_test": b_test, "t_disc": len(dates), "strict": strict,
            "funnel": funnel(results), "ranking_pass": ranked_pass, "ranking_all": ranked_all,
            "tier_a": tier_a, "tier_a_log": a_log,
            # READING Q3: Tier B "continue" walks on from the last configuration the Tier A walk examined
            "tier_b_reading": tier_b_reading, "tier_b": tb[tier_b_reading]["tier_b"], "tier_b_detail": tb,
            "best_config": best, "best_sharpe": by_id[best]["sharpe"] if best else None,
            "configs": results,
            "reports": {"pbo": pbo_report(results, series), "bh_holm": bh_holm(results),
                        "reference_thresholds": reference_thresholds(len(results), n_trials),
                        "note": "PBO, FDR and reference thresholds are reports, never gates (P8, D1)"}}


# ---------------------------------------------------------------- loading a search root (INTERFACE 4.3)
def _sha_dir(parent: Path, sha: str | None) -> Path:
    if sha:
        return parent / sha
    subs = sorted(p for p in parent.iterdir() if p.is_dir() and len(p.name) == 12
                  and all(c in "0123456789abcdef" for c in p.name))
    if len(subs) != 1:
        raise ValueError(f"{parent}: {len(subs)} code_sha12 folders; pass the sha explicitly")
    return subs[0]


def load_root(root, cids, feat_sha: str | None = None) -> tuple:
    """(dates, sigma_ZM per date, {cid: None | (x, n_trades)}) from <root>/search/<cid>/ and the features' _day.
    Every configuration must carry its DONE marker (P10: unrun configurations are not passed here)."""
    import pandas as pd
    root = Path(root)
    configs, dates, missing = {}, None, []
    for cid in cids:
        parse_id(cid)
        base = root / "search" / cid
        if not (base / "DONE").exists():
            missing.append(cid)
            continue
        stats = json.loads((base / "stats.json").read_text())
        if stats.get("failed"):
            configs[cid] = None
            continue
        daily = pd.read_parquet(base / "daily.parquet")
        d = [str(v) for v in daily["date"]]
        if dates is None:
            dates = d
        elif d != dates:
            raise ValueError(f"{cid}: daily dates differ from the other configurations'")
        x = daily["X_D"].to_numpy(dtype=np.float64)
        nt = daily["n_trades"].to_numpy(dtype=np.int64)
        mom = moments(list(x))
        if stats["trade_count"] != int(nt.sum()) or not math.isclose(mom["sharpe"], stats["moments"]["sharpe"],
                                                                      rel_tol=1e-12, abs_tol=1e-15):
            raise ValueError(f"{cid}: daily.parquet disagrees with stats.json")
        configs[cid] = (x, nt)
    if missing:
        raise RuntimeError(f"configurations without a DONE marker: {missing}")
    if dates is None:
        raise RuntimeError("no configuration has a series")
    fdir = _sha_dir(root / "features", feat_sha)
    sigma = []
    for d in dates:
        v = json.loads((fdir / "_day" / f"{d}.json").read_text()).get("sigma_zm")
        if v is None or not math.isfinite(float(v)) or float(v) <= 0:
            raise ValueError(f"{d}: sigma_zm {v!r}")
        sigma.append(float(v))
    return dates, sigma, configs


def summary_lines(res: dict) -> list:
    f = res["funnel"]
    return [f"N = {res['n_trials']}, b_test = {res['b_test']:.6f}, T = {res['t_disc']}",
            f"funnel alone {f['alone']}; in order {f['in_order']}; failed {f['failed_configs']}",
            f"Tier A {res['tier_a']}; Tier B ({res['tier_b_reading']}) {res['tier_b']}",
            f"best {res['best_config']} SR_d {res['best_sharpe']}"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", type=Path, required=True)
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--ids", nargs="+")
    grp.add_argument("--ids-file", type=Path)
    grp.add_argument("--all", action="store_true", help="the 300 E33 ids")
    ap.add_argument("--n", type=int, required=True, help="the registered N (P7.1)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--feat-sha")
    ap.add_argument("--tier-b-reading", choices=("continue", "restart"), default="continue")
    ap.add_argument("--not-strict", action="store_true", help="tests only: no 796-date calendar assertion")
    args = ap.parse_args(argv)
    if args.all:
        ids = [f"E33-{s}{lab}{g}" for s in ("S5", "S1", "S3", "S2", "S4")
               for lab in ("F15", "F30", "F05", "F60", "T15", "T30") for g in GRID_ORDER]
    elif args.ids_file:
        ids = [ln.strip() for ln in args.ids_file.read_text().splitlines() if ln.strip()]
    else:
        ids = list(args.ids)
    dates, sigma, configs = load_root(args.root, ids, args.feat_sha)
    res = select(configs, dates, sigma, args.n, strict=not args.not_strict, tier_b_reading=args.tier_b_reading)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out.with_name(args.out.name + ".tmp")
    tmp.write_text(json.dumps(res, indent=1, sort_keys=True, default=float))
    tmp.replace(args.out)
    print("\n".join(summary_lines(res)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
