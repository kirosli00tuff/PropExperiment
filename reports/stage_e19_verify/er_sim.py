"""EconReviewer Phase A item 2: an independent funnel simulator (numpy only; no prop_econ import).

Written from reports/stage_e19_briefs/sim_spec.md sections 2 to 5, the FINAL rules
reports/stage_e19_rules.json and the lead's rulings L-1..L-17 (reports/stage_e19_STATE.md). Shocks come from
my own returns table (er_returns.npz, built by er_returns.py) with my own 5-day block bootstrap.

Grid recomputed: sizes 50K/100K/150K; payout path standard/consistency; DLL off; pricing standard; API fee
$14.50 per started 21-trading-day period included; payout policy max (keep_d 0); edges zero (k = 1) and net
Sharpe 0.5; f in {0.05, 0.10, 0.15, 0.20, 0.25}. N_PATHS attempts and XFAs per configuration (common random
numbers across f, edge, size and path), N_CYCLES cycles.

Conventions the spec leaves open (my readings; Phase B compares them with the code's):
  C1 a reset happens the trading day after a fail and the new attempt trades on that day;
  C2 a rebill falling on the pass day is paid (the subscription is alive at the start of that day);
  C3 a rebill due on a reset day is paid first and its credit pays the reset (L-17);
  C4 no reset is charged after the 60th failed attempt (the cycle ends with no XFA);
  C5 the API fee counts started 21-day periods of the cycle length (first day to the XFA's end day);
  C6 the Combine consistency is strict (best < 0.55 x B, rules combine_consistency_inclusive false);
  C7 the XFA consistency is inclusive (best <= 0.4 x window net, rules xfa_consistency_inclusive true);
  C8 a payout request needs amount >= 125; otherwise the window keeps accumulating.
Usage: python er_sim.py "<date string>"  -> writes recompute.json, er_sim.log
"""
from __future__ import annotations

import json
import math
import os
import sys
import time as _time
from pathlib import Path

import numpy as np

os.nice(10)
REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports" / "stage_e19_verify"
RULES = json.loads((REPO / "reports" / "stage_e19_rules.json").read_text())
assert RULES["status"] == "FINAL"
CHECK = json.loads((OUT / "er_returns_check.json").read_text())
NPZ = np.load(OUT / "er_returns.npz")

ROOTS = ("NQ", "CL", "GC", "ZN", "6E")
MICRO = {"NQ": "MNQ", "CL": "MCL", "GC": "MGC", "ZN": None, "6E": "M6E"}
N_PATHS = int(os.environ.get("ER_N_PATHS", "20000"))
N_CYCLES = int(os.environ.get("ER_N_CYCLES", "20000"))
N_DAYS = 756
BLOCK = 5
BILLING_DAYS = 21  # 30 calendar days x 252/365 = 20.7 -> 21
ATTEMPT_CAP = 60
API_FEE = float(RULES["global"]["api_access_monthly_usd"])
SPLIT = float(RULES["global"]["profit_split_trader"])
MIN_REQUEST = float(RULES["global"]["payout_min_request_usd"])
SQRT252 = math.sqrt(252.0)
SIZES = ("50K", "100K", "150K")
PATHS = ("standard", "consistency")
EDGES = (("zero_k1", "zero", 0.0, 1), ("sharpe_0.5", "sharpe", 0.5, 1))
FS = (0.05, 0.10, 0.15, 0.20, 0.25)
SEED_OFFSET = int(os.environ.get("ER_SEED_OFFSET", "0"))  # 0 = the blind run; 100, 200 = the spread runs
SEED_SHOCKS_ATTEMPT = 7_190_001 + SEED_OFFSET
SEED_SHOCKS_XFA = 7_190_002 + SEED_OFFSET
SEED_CYCLES = 7_190_003 + SEED_OFFSET
LOG = open(OUT / "er_sim.log", "a")


def log(*a) -> None:
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n"); LOG.flush()


# ----------------------------------------------------------------------------- products and shocks
def products() -> dict:
    sig_full = np.array([float(NPZ[f"{r}_sigma_full"][0]) for r in ROOTS])
    rt_full = np.array([CHECK["d8_rt"][r]["rt_d8_mean_usd"] for r in ROOTS])
    has_micro = np.array([MICRO[r] is not None for r in ROOTS])
    sig_micro = np.where(has_micro, sig_full / 10.0, np.nan)
    rt_micro = np.array([CHECK["d8_rt"][MICRO[r]]["rt_d8_mean_usd"] if MICRO[r] else np.nan for r in ROOTS])
    n_kept = np.array([len(NPZ[f"{r}_dates"]) for r in ROOTS])
    return {"sig_full": sig_full, "rt_full": rt_full, "has_micro": has_micro, "sig_micro": sig_micro,
            "rt_micro": rt_micro, "n_kept": n_kept}


def draw_shocks(n_paths: int, n_days: int, seed: int, prods: dict) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pooled 5-path block bootstrap, random direction: returns z, w (float64) and prod (int8)."""
    rng = np.random.Generator(np.random.PCG64(seed))
    n_blocks = -(-n_days // BLOCK)
    prod_block = rng.integers(0, len(ROOTS), size=(n_paths, n_blocks))
    start_u = rng.random((n_paths, n_blocks))
    sign = rng.integers(0, 2, size=(n_paths, n_days)).astype(np.int8) * 2 - 1
    start = np.floor(start_u * (prods["n_kept"][prod_block] - BLOCK + 1)).astype(np.int64)
    prod = np.repeat(prod_block, BLOCK, axis=1)[:, :n_days].astype(np.int8)
    day_in_block = np.tile(np.arange(BLOCK), n_blocks)[:n_days]
    idx = np.repeat(start, BLOCK, axis=1)[:, :n_days] + day_in_block[None, :]
    z = np.empty((n_paths, n_days)); w = np.empty((n_paths, n_days))
    for p, r in enumerate(ROOTS):
        m = prod == p
        zl, wl, zs, ws = (NPZ[f"{r}_{k}"] for k in ("z_long", "w_long", "z_short", "w_short"))
        ii = idx[m]; sg = sign[m]
        z[m] = np.where(sg > 0, zl[ii], zs[ii])
        w[m] = np.where(sg > 0, wl[ii], ws[ii])
    assert np.all(w <= np.minimum(0.0, z) + 1e-12)
    return z, w, prod


# ----------------------------------------------------------------------------- daily step
def tier_cap(balance: np.ndarray, tiers: list[dict], boundary: str) -> np.ndarray:
    cap = np.full(balance.shape, tiers[-1]["max_minis"], dtype=np.int64)
    assigned = np.zeros(balance.shape, dtype=bool)
    for t in tiers[:-1]:
        hit = (balance <= t["below_usd"]) if boundary == "lower" else (balance < t["below_usd"])
        pick = hit & ~assigned
        cap[pick] = t["max_minis"]; assigned |= pick
    return cap


def day_step(B: np.ndarray, F: np.ndarray, p: np.ndarray, z: np.ndarray, w: np.ndarray, f: float,
             edge: str, sharpe: float, k: int, cap_minis: np.ndarray, prods: dict) -> tuple[np.ndarray, np.ndarray]:
    """sim_spec section 2 with the DLL off: returns (pnl, breach)."""
    D = B - F
    s = f * D
    sig_full = prods["sig_full"][p]
    full = (~prods["has_micro"][p]) | (s >= sig_full)
    sigma = np.where(full, sig_full, prods["sig_micro"][p])
    rt = np.where(full, prods["rt_full"][p], prods["rt_micro"][p])
    n = np.maximum(s / sigma, 1.0)
    n = np.minimum(n, cap_minis * np.where(full, 1.0, 10.0))
    if edge == "zero":
        close = n * sigma * z - n * k * rt
    else:
        close = n * sigma * (z + sharpe / SQRT252)
    worst = n * sigma * w - n * k * rt
    breach = worst <= -D
    pnl = np.where(breach, -D, close)
    return pnl, breach


# ----------------------------------------------------------------------------- Combine attempts
def run_attempts(z, w, prod, size: dict, f: float, edge: str, sharpe: float, k: int, prods: dict) -> dict:
    c = size["combine"]
    n = z.shape[0]
    mll, T = float(c["mll_usd"]), float(c["profit_target_usd"])
    frac = float(c["consistency"]["frac"]); assert c["consistency"]["type"] == "best_day_max_frac_of_profit"
    strict = not RULES["global"]["combine_consistency_inclusive"]
    cap = np.full(n, int(c["max_minis"]))
    B = np.zeros(n); F = np.full(n, -mll); best = np.full(n, -np.inf)
    alive = np.ones(n, dtype=bool)
    length = np.full(n, N_DAYS, dtype=np.int64); passed = np.zeros(n, dtype=bool); timeout = np.zeros(n, dtype=bool)
    for d in range(N_DAYS):
        pnl, breach = day_step(B, F, prod[:, d], z[:, d], w[:, d], f, edge, sharpe, k, cap, prods)
        B = np.where(alive, B + pnl, B)
        best = np.where(alive, np.maximum(best, pnl), best)
        F = np.where(alive, np.maximum(F, np.minimum(B - mll, float(c["mll_floor_max_rel_usd"]))), F)
        cons = (best < frac * B) if strict else (best <= frac * B)
        ok = (B >= T) & cons & (d + 1 >= int(c["min_trading_days"])) & ~breach
        done = alive & (breach | ok)
        length[done] = d + 1; passed[done & ok] = True
        alive &= ~done
        if not alive.any():
            break
    timeout[alive] = True
    return {"passed": passed, "length": length, "timeout": timeout}


# ----------------------------------------------------------------------------- XFA lives
def run_xfas(z, w, prod, size: dict, path: str, f: float, edge: str, sharpe: float, k: int, prods: dict) -> dict:
    x = size["xfa"]; pr = x["payout"][path]
    n = z.shape[0]
    mll = float(x["mll_usd"]); lock = float(x["mll_floor_lock_usd"])
    after_first = x["mll_after_first_payout_usd"]
    cap_usd = float(pr["cap_usd"]); frac_b = float(pr["frac_of_balance"])
    B = np.full(n, float(x["start_balance_usd"])); F = B - mll
    close_prev = B.copy()
    floor_fixed = np.zeros(n, dtype=bool)
    alive = np.ones(n, dtype=bool)
    n_pay = np.zeros(n, dtype=np.int64); gross = np.zeros(n); first_day = np.full(n, -1, dtype=np.int64)
    end_day = np.full(n, N_DAYS, dtype=np.int64); breached = np.zeros(n, dtype=bool)
    win_cnt = np.zeros(n, dtype=np.int64); win_net = np.zeros(n); win_traded = np.zeros(n, dtype=np.int64)
    win_best = np.full(n, -np.inf)
    payout_day_hist = np.zeros(N_DAYS + 1, dtype=np.int64)
    for d in range(N_DAYS):
        # start of day: payout request (never on day 1: the window is empty)
        if path == "standard":
            net_ok = np.where(n_pay >= 1, win_net > 0, B > 0) if pr["net_positive_since_last"] else (B > 0)
            elig = (win_cnt >= int(pr["winning_days"])) & net_ok
        else:
            inclusive = RULES["global"]["xfa_consistency_inclusive"]
            best_ok = (win_best <= float(pr["best_day_max_frac"]) * win_net) if inclusive else \
                (win_best < float(pr["best_day_max_frac"]) * win_net)
            elig = (win_traded >= int(pr["traded_days"])) & (win_net > 0) & best_ok
        amount = np.floor(np.minimum(np.minimum(cap_usd, frac_b * B), B - 0.0 * mll) * 100.0 + 1e-9) / 100.0
        req = alive & elig & (amount >= MIN_REQUEST)
        if req.any():
            B[req] -= amount[req]
            if after_first is not None:
                F[req] = float(after_first); floor_fixed[req] = True
            n_pay[req] += 1; gross[req] += amount[req]
            first_day[req & (first_day < 0)] = d + 1
            win_cnt[req] = 0; win_net[req] = 0.0; win_traded[req] = 0; win_best[req] = -np.inf
            payout_day_hist[d + 1] += int(req.sum())
            if np.any(B[req] - F[req] <= 0):
                raise RuntimeError("D_open <= 0 after a payout")
        cap = tier_cap(close_prev, x["scaling"], x["scaling_boundary"])
        pnl, breach = day_step(B, F, prod[:, d], z[:, d], w[:, d], f, edge, sharpe, k, cap, prods)
        B = np.where(alive, B + pnl, B)
        upd = alive & ~req
        win_cnt[upd] += (pnl[upd] >= float(pr.get("winning_day_usd", np.inf)))
        win_net[upd] += pnl[upd]; win_traded[upd] += 1; win_best[upd] = np.maximum(win_best[upd], pnl[upd])
        trail = alive & ~floor_fixed
        F = np.where(trail, np.maximum(F, np.minimum(B - mll, lock)), F)
        done = alive & breach
        end_day[done] = d + 1; breached[done] = True
        alive &= ~done
        close_prev = B.copy()
    return {"n_pay": n_pay, "gross": gross, "first_day": first_day, "end_day": end_day, "breached": breached,
            "alive_horizon": alive, "end_balance": B, "payout_day_hist": payout_day_hist}


# ----------------------------------------------------------------------------- cycles (fees)
def assemble_cycles(att: dict, xfa: dict, size: dict, rng: np.random.Generator, n_cycles: int,
                    pricing: str = "standard") -> dict:
    c = size["combine"]
    P = float(c["monthly_price_usd"][pricing]); R = float(c["reset_price_usd"][pricing])
    act = float(size["activation_fee_usd"][pricing])
    adds_credit = RULES["global"]["rebill_adds_reset_credit"]; pushes = RULES["global"]["reset_pushes_rebill"]
    na, nx = len(att["passed"]), len(xfa["n_pay"])
    idx = rng.integers(0, na, size=(n_cycles, ATTEMPT_CAP))
    xidx = rng.integers(0, nx, size=n_cycles)
    t = np.ones(n_cycles, dtype=np.int64)  # first trading day of the current attempt
    anchor = np.ones(n_cycles, dtype=np.int64)  # rebill clock anchor (last start or reset)
    credits = np.zeros(n_cycles, dtype=np.int64)
    purchases = np.ones(n_cycles, dtype=np.int64)  # P at the start
    fee_sub = np.full(n_cycles, P); fee_act = np.zeros(n_cycles)
    done = np.zeros(n_cycles, dtype=bool); reached_xfa = np.zeros(n_cycles, dtype=bool)
    xfa_start = np.zeros(n_cycles, dtype=np.int64); n_attempts = np.zeros(n_cycles, dtype=np.int64)
    cycle_end = np.zeros(n_cycles, dtype=np.int64)
    for j in range(ATTEMPT_CAP):
        a = ~done
        L = att["length"][idx[:, j]]; ps = att["passed"][idx[:, j]]
        end = t + L - 1
        nreb = np.maximum((end - anchor) // BILLING_DAYS, 0)  # rebills on anchor + 21 m <= end (C2)
        fee_sub[a] += nreb[a] * P; purchases[a] += nreb[a]
        if adds_credit:
            credits[a] += nreb[a]
        n_attempts[a] += 1
        # pass
        pj = a & ps
        reached_xfa[pj] = True; fee_act[pj] += act; xfa_start[pj] = end[pj] + 1; done[pj] = True
        # fail
        fj = a & ~ps
        if j == ATTEMPT_CAP - 1:
            cycle_end[fj] = end[fj]; done[fj] = True  # C4: no reset after the capped attempt
            break
        reset_day = end + 1
        reb_on_reset = fj & (((reset_day - anchor) % BILLING_DAYS) == 0) & (reset_day > anchor)  # C3
        fee_sub[reb_on_reset] += P; purchases[reb_on_reset] += 1
        if adds_credit:
            credits[reb_on_reset] += 1
        use_credit = fj & (credits > 0)
        credits[use_credit] -= 1
        pay_reset = fj & ~use_credit
        fee_sub[pay_reset] += R; purchases[pay_reset] += 1
        if pushes:
            anchor[fj] = reset_day[fj]
        t[fj] = reset_day[fj]  # C1
        if done.all():
            break
    # XFA
    xg = xfa["gross"][xidx]; xn = xfa["n_pay"][xidx]; xend = xfa["end_day"][xidx]
    cash = np.where(reached_xfa, SPLIT * xg, 0.0)
    n_pay = np.where(reached_xfa, xn, 0)
    cycle_end = np.where(reached_xfa, xfa_start + xend - 1, cycle_end)
    api = API_FEE * np.ceil(cycle_end / BILLING_DAYS)  # C5
    fees = fee_sub + fee_act + api
    net = cash - fees
    net_noapi = cash - fee_sub - fee_act
    return {"net": net, "net_noapi": net_noapi, "purchases": purchases, "fees": fees, "fee_sub": fee_sub,
            "fee_act": fee_act, "api": api, "cash": cash, "n_pay": n_pay, "reached_xfa": reached_xfa,
            "n_attempts": n_attempts, "cycle_end": cycle_end}


def stats(v: np.ndarray) -> dict:
    return {"mean": float(v.mean()), "se": float(v.std(ddof=1) / math.sqrt(len(v)))}


def main() -> None:
    stamp = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    t0 = _time.time()
    prods = products()
    log(f"start {stamp}; n_paths {N_PATHS} n_cycles {N_CYCLES}; sig_full {np.round(prods['sig_full'], 2).tolist()}")
    za, wa, pa = draw_shocks(N_PATHS, N_DAYS, SEED_SHOCKS_ATTEMPT, prods)
    zx, wx, px = draw_shocks(N_PATHS, N_DAYS, SEED_SHOCKS_XFA, prods)
    log(f"shocks drawn {_time.time() - t0:.1f}s; attempt z mean {za.mean():.5f} sd {za.std():.4f}; "
        f"xfa z mean {zx.mean():.5f} sd {zx.std():.4f}; prod shares {np.bincount(pa.ravel(), minlength=5) / pa.size}")
    results = {"generated_date_cmd": stamp, "n_paths": N_PATHS, "n_cycles": N_CYCLES, "n_days": N_DAYS,
               "seeds": {"shocks_attempt": SEED_SHOCKS_ATTEMPT, "shocks_xfa": SEED_SHOCKS_XFA,
                         "cycles": SEED_CYCLES},
               "code": ["reports/stage_e19_verify/er_returns.py", "reports/stage_e19_verify/er_sim.py"],
               "conventions": [ln.strip() for ln in __doc__.splitlines() if ln.strip().startswith("C")],
               "products": {r: {"sigma_full": float(prods["sig_full"][i]), "rt_full": float(prods["rt_full"][i]),
                                "sigma_micro": None if not prods["has_micro"][i] else float(prods["sig_micro"][i]),
                                "rt_micro": None if not prods["has_micro"][i] else float(prods["rt_micro"][i])}
                             for i, r in enumerate(ROOTS)},
               "shock_check": {"attempt_z_mean": float(za.mean()), "attempt_z_sd": float(za.std()),
                               "xfa_z_mean": float(zx.mean()), "xfa_z_sd": float(zx.std()),
                               "w_le_min0z": True},
               "configs": []}
    for size_name in SIZES:
        size = RULES["sizes"][size_name]
        for edge_name, edge, S, k in EDGES:
            for f in FS:
                ta = _time.time()
                att = run_attempts(za, wa, pa, size, f, edge, S, k, prods)
                p_pass = float(att["passed"].mean())
                for path in PATHS:
                    xfa = run_xfas(zx, wx, px, size, path, f, edge, S, k, prods)
                    rng = np.random.Generator(np.random.PCG64(SEED_CYCLES))  # paired across configs
                    cyc = assemble_cycles(att, xfa, size, rng, N_CYCLES)
                    rec = {
                        "size": size_name, "path": path, "edge": edge_name, "f": f, "dll": False,
                        "pricing": "standard", "api_fee": "included", "policy": "max",
                        "attempt": {"p_pass": p_pass, "p_pass_se": float(math.sqrt(p_pass * (1 - p_pass) / N_PATHS)),
                                    "mean_length": float(att["length"].mean()),
                                    "timeout_share": float(att["timeout"].mean())},
                        "xfa": {"mean_user_cash": stats(SPLIT * xfa["gross"]),
                                "p_any_payout": float((xfa["n_pay"] >= 1).mean()),
                                "p_any_payout_se": float(math.sqrt((xfa["n_pay"] >= 1).mean() * (1 - (xfa["n_pay"] >= 1).mean()) / N_PATHS)),
                                "mean_n_payouts": float(xfa["n_pay"].mean()),
                                "mean_first_payout_day_given": float(xfa["first_day"][xfa["first_day"] > 0].mean())
                                if (xfa["first_day"] > 0).any() else None,
                                "breach_share": float(xfa["breached"].mean()),
                                "alive_at_horizon": float(xfa["alive_horizon"].mean()),
                                "mean_life": float(xfa["end_day"].mean())},
                        "cycle": {"net": stats(cyc["net"]), "net_noapi": stats(cyc["net_noapi"]),
                                  "p_no_payout": float((cyc["n_pay"] == 0).mean()),
                                  "p_reach_xfa": float(cyc["reached_xfa"].mean()),
                                  "mean_purchases": float(cyc["purchases"].mean()),
                                  "mean_purchases_se": float(cyc["purchases"].std(ddof=1) / math.sqrt(N_CYCLES)),
                                  "p_no_payout_se": float(math.sqrt(max((cyc["n_pay"] == 0).mean() * (1 - (cyc["n_pay"] == 0).mean()), 0) / N_CYCLES)),
                                  "mean_fees": float(cyc["fees"].mean()),
                                  "mean_fee_sub": float(cyc["fee_sub"].mean()),
                                  "mean_fee_act": float(cyc["fee_act"].mean()),
                                  "mean_api": float(cyc["api"].mean()),
                                  "mean_cash": float(cyc["cash"].mean()),
                                  "mean_attempts": float(cyc["n_attempts"].mean()),
                                  "mean_length": float(cyc["cycle_end"].mean()),
                                  "net_per_purchase": float(cyc["net"].mean() / cyc["purchases"].mean()),
                                  "p5": float(np.percentile(cyc["net"], 5)),
                                  "p50": float(np.percentile(cyc["net"], 50)),
                                  "p95": float(np.percentile(cyc["net"], 95))},
                        "funded_xfa_net_of_activation": float(SPLIT * xfa["gross"].mean()
                                                              - size["activation_fee_usd"]["standard"]),
                    }
                    results["configs"].append(rec)
                    log(f"{size_name} {path:11s} {edge_name:10s} f={f:.2f} P(pass)={p_pass:.4f} "
                        f"cash/XFA={rec['xfa']['mean_user_cash']['mean']:8.1f} P(any)={rec['xfa']['p_any_payout']:.3f} "
                        f"net={rec['cycle']['net']['mean']:8.1f}+-{rec['cycle']['net']['se']:.1f} "
                        f"Pnopay={rec['cycle']['p_no_payout']:.3f} purch={rec['cycle']['mean_purchases']:.2f} "
                        f"net/purch={rec['cycle']['net_per_purchase']:.1f} [{_time.time() - ta:.1f}s]")
    results["elapsed_s"] = round(_time.time() - t0, 1)
    (OUT / os.environ.get("ER_OUT", "recompute.json")).write_text(json.dumps(results, indent=1))
    log(f"done {results['elapsed_s']}s -> recompute.json")


if __name__ == "__main__":
    main()
