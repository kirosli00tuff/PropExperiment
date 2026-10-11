"""EconReviewer Phase C: independent recompute of the verdict cells the lead listed (ER-13).

My own simulator extended (no prop_econ simulation code imported): DLL in both phases (stop at -DLL when
DLL < D_open - 1e-6, else the MLL governs), doubled payout caps with the DLL, keep-D payout policy, Back2Funded
chains (fee at the breach, fresh XFA, at most max_per_xfa, before the first payout only), per-payout records,
cycle event times, and a 5-slot campaign (events merged in time order, fees before cash on a day; a target is
reached at the first event with cumulative user cash >= target unless cumulative Combine purchases exceed 400
first; P50/P80 by the inverted CDF with inf for "not reached"; API fee 14.50 x (floor(t/21) + 1) at the crossing).
Shocks: "same" = the grid's own ShockSets rebuilt with prop_econ.returns.build_shocks from the job seeds (so the
pools are identical and only the cycle / campaign index draws differ); "own" = my independent shocks (er_sim seeds).
Writes phase_c.json and phase_c.log.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

os.nice(10)
REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports" / "stage_e19_verify"
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(OUT))
import er_sim as E  # noqa: E402
from prop_econ.returns import build_shocks  # noqa: E402  (the grid's shock generator, verified in Phase A)

RULES = E.RULES
SIZE = RULES["sizes"]["50K"]
G = RULES["global"]
N = 20000; N_DAYS = 756; N_CYC = int(os.environ.get("PC_N_CYC", "20000")); N_REPS = int(os.environ.get("PC_N_REPS", "20000")); CAP_ATT = 60; PCAP = 400; MAXPAY = 192; PER = 21
API = float(G["api_access_monthly_usd"]); SPLIT = float(G["profit_split_trader"]); MINREQ = float(G["payout_min_request_usd"])
JOB = json.loads((REPO / "reports" / "stage_e19_runs" / "bootstrap-random-all-d8-continuous__50K__zero_k1__f0.25__dll0__base.json").read_text())
SEEDS = JOB["seeds"]
RES = json.loads((REPO / "reports" / "stage_e19_results.json").read_text())
LOG = open(OUT / "phase_c.log", "a")


def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()


# ------------------------------------------------------------------------------- daily step with DLL
def day_step(B, F, p, z, w, f, edge, S, k, cap_minis, prods, dll):
    D = B - F; s = f * D
    full = (~prods["has_micro"][p]) | (s >= prods["sig_full"][p])
    sigma = np.where(full, prods["sig_full"][p], prods["sig_micro"][p])
    rt = np.where(full, prods["rt_full"][p], prods["rt_micro"][p])
    n = np.minimum(np.maximum(s / sigma, 1.0), cap_minis * np.where(full, 1.0, 10.0))
    close = n * sigma * z - n * k * rt if edge == "zero" else n * sigma * (z + S / E.SQRT252)
    worst = n * sigma * w - n * k * rt
    if dll is None:
        hit = np.zeros(B.shape, dtype=bool)
    else:
        hit = (worst <= -dll) & (dll < D - 1e-6)
    breach = ~hit & (worst <= -D)
    pnl = np.where(hit, -(dll or 0.0), np.where(breach, -D, close))
    return pnl, breach


def run_attempts(z, w, prod, f, edge, S, k, prods, dll):
    c = SIZE["combine"]; n = z.shape[0]
    mll, T, frac = float(c["mll_usd"]), float(c["profit_target_usd"]), float(c["consistency"]["frac"])
    cap = np.full(n, int(c["max_minis"]))
    B = np.zeros(n); F = np.full(n, -mll); best = np.full(n, -np.inf)
    alive = np.ones(n, dtype=bool); length = np.full(n, N_DAYS); passed = np.zeros(n, dtype=bool)
    reason = np.full(n, 2)  # 0 breach, 1 pass, 2 timeout
    for d in range(N_DAYS):
        pnl, breach = day_step(B, F, prod[:, d], z[:, d], w[:, d], f, edge, S, k, cap, prods, dll)
        B = np.where(alive, B + pnl, B); best = np.where(alive, np.maximum(best, pnl), best)
        F = np.where(alive, np.maximum(F, np.minimum(B - mll, float(c["mll_floor_max_rel_usd"]))), F)
        ok = (B >= T) & (best < frac * B) & (d + 1 >= int(c["min_trading_days"])) & ~breach
        done = alive & (breach | ok)
        length[done] = d + 1; passed[done & ok] = True; reason[done & ok] = 1; reason[done & breach] = 0
        alive &= ~done
        if not alive.any():
            break
    return {"passed": passed, "length": length, "reason": reason}


def run_xfas(z, w, prod, path, f, edge, S, k, prods, dll, keep_d):
    x = SIZE["xfa"]; pr = x["payout"][path]; n = z.shape[0]
    mll = float(x["mll_usd"]); lock = float(x["mll_floor_lock_usd"]); after_first = x["mll_after_first_payout_usd"]
    cap_usd = float(pr["cap_usd_dll"]) if (dll is not None and G["dll_doubles_payout_caps"]) else float(pr["cap_usd"])
    frac_b = float(pr["frac_of_balance"])
    B = np.zeros(n); F = B - mll; close_prev = B.copy(); fixed = np.zeros(n, dtype=bool); alive = np.ones(n, dtype=bool)
    n_pay = np.zeros(n, dtype=np.int64); gross = np.zeros(n); end_day = np.full(n, N_DAYS); breached = np.zeros(n, dtype=bool)
    pay_days = np.full((n, MAXPAY), -1, dtype=np.int32); pay_gross = np.zeros((n, MAXPAY))
    wc = np.zeros(n, dtype=np.int64); wn = np.zeros(n); wt = np.zeros(n, dtype=np.int64); wb = np.full(n, -np.inf)
    for d in range(N_DAYS):
        if path == "standard":
            net_ok = np.where(n_pay >= 1, wn > 0, B > 0) if pr["net_positive_since_last"] else (B > 0)
            elig = (wc >= int(pr["winning_days"])) & net_ok
        else:
            best_ok = (wb <= float(pr["best_day_max_frac"]) * wn) if G["xfa_consistency_inclusive"] else (wb < float(pr["best_day_max_frac"]) * wn)
            elig = (wt >= int(pr["traded_days"])) & (wn > 0) & best_ok
        amount = np.floor(np.round(np.minimum(np.minimum(cap_usd, frac_b * B), B - keep_d * mll) * 100.0, 6)) / 100.0
        req = alive & elig & (amount >= MINREQ)
        if req.any():
            ri = np.flatnonzero(req); slot = n_pay[ri]
            assert np.all(slot < MAXPAY)
            pay_days[ri, slot] = d; pay_gross[ri, slot] = amount[ri]
            B[req] -= amount[req]
            if after_first is not None:
                F[req] = float(after_first); fixed[req] = True
            n_pay[req] += 1; gross[req] += amount[req]
            wc[req] = 0; wn[req] = 0.0; wt[req] = 0; wb[req] = -np.inf
            if np.any(B[req] - F[req] <= 0):
                raise RuntimeError("D_open <= 0 after a payout")
        cap = E.tier_cap(close_prev, x["scaling"], x["scaling_boundary"])
        pnl, breach = day_step(B, F, prod[:, d], z[:, d], w[:, d], f, edge, S, k, cap, prods, dll)
        B = np.where(alive, B + pnl, B)
        upd = alive & ~req & ~breach
        if path == "standard":
            wc[upd] += (pnl[upd] >= float(pr["winning_day_usd"]))
        wn[upd] += pnl[upd]; wt[upd] += 1; wb[upd] = np.maximum(wb[upd], pnl[upd])
        trail = alive & ~fixed & ~breach
        F = np.where(trail, np.maximum(F, np.minimum(B - mll, lock)), F)
        done = alive & breach
        end_day[done] = d + 1; breached[done] = True; alive &= ~done
        close_prev = B.copy()
    return {"n_pay": n_pay, "gross": gross, "end_day": end_day, "breached": breached, "pay_days": pay_days,
            "pay_gross": pay_gross}


# ------------------------------------------------------------------------------- cycles with events
def assemble(att_idx, xfa_idx, att, xfa, P, R, act, b2f_price, b2f_on, b2f_max=2):
    """Their 0-based time convention (start at time 0, attempt occupies [t, t + L)); my readings C1-C8."""
    n = att_idx.shape[0]
    ev_c, ev_t, ev_cash, ev_pur, ev_fee, ev_usd = [], [], [], [], [], []

    def emit(c, t, is_cash, pur, fee, cash):
        if c.size:
            ev_c.append(c); ev_t.append(t); ev_cash.append(np.full(c.size, is_cash, dtype=np.int8))
            ev_pur.append(np.full(c.size, pur, dtype=np.int64)); ev_fee.append(fee if np.ndim(fee) else np.full(c.size, float(fee)))
            ev_usd.append(cash if np.ndim(cash) else np.full(c.size, float(cash)))

    t = np.zeros(n, dtype=np.int64); nxt = np.full(n, PER, dtype=np.int64); credits = np.zeros(n, dtype=np.int64)
    active = np.ones(n, dtype=bool); passed = np.zeros(n, dtype=bool); n_att = np.zeros(n, dtype=np.int64)
    emit(np.arange(n), np.zeros(n, dtype=np.int64), 0, 1, P, 0.0)

    def rebills(ci, bound, inclusive):
        nr = nxt[ci]; gap = bound - nr
        cnt = np.maximum(gap // PER + 1 if inclusive else (gap + PER - 1) // PER, 0)
        tot = int(cnt.sum())
        if tot:
            first = np.cumsum(cnt) - cnt
            kk = np.arange(tot) - np.repeat(first, cnt)
            emit(np.repeat(ci, cnt), np.repeat(nr, cnt) + PER * kk, 0, 1, P, 0.0)
        if G["rebill_adds_reset_credit"]:
            credits[ci] += cnt
        nxt[ci] = nr + cnt * PER

    for j in range(CAP_ATT):
        ci = np.flatnonzero(active)
        if ci.size == 0:
            break
        a = att_idx[ci, j]
        if j > 0:
            rebills(ci, t[ci], True)
            has = credits[ci] > 0; credits[ci] -= has
            pay = ci[~has]; emit(pay, t[pay], 0, 1, R, 0.0)
            if G["reset_pushes_rebill"]:
                nxt[ci] = t[ci] + PER
        end = t[ci] + att["length"][a]
        rebills(ci, end, False)
        n_att[ci] += 1; t[ci] = end
        won = att["passed"][a]; passed[ci[won]] = True; active[ci[won]] = False
    end_c = t.copy(); n_xfas = np.zeros(n, dtype=np.int64)
    chain = np.flatnonzero(passed); start = t[chain]
    emit(chain, start, 0, 0, act, 0.0)
    for j in range(1 + b2f_max):
        if chain.size == 0:
            break
        x = xfa_idx[chain, j]; n_xfas[chain] += 1
        days = xfa["pay_days"][x]; rows, cols = np.nonzero(days >= 0)
        emit(chain[rows], start[rows] + days[rows, cols], 1, 0, 0.0, SPLIT * xfa["pay_gross"][x[rows], cols])
        stop = start + xfa["end_day"][x]; end_c[chain] = stop
        if not b2f_on or j == b2f_max:
            break
        again = xfa["breached"][x] & (xfa["n_pay"][x] == 0)
        chain, start = chain[again], stop[again]
        emit(chain, start, 0, 0, b2f_price, 0.0)
    c = np.concatenate(ev_c); tt = np.concatenate(ev_t); isc = np.concatenate(ev_cash); pur = np.concatenate(ev_pur)
    fee = np.concatenate(ev_fee); usd = np.concatenate(ev_usd)
    order = np.lexsort((isc, tt, c)); c, tt, isc, pur, fee, usd = (v[order] for v in (c, tt, isc, pur, fee, usd))
    off = np.searchsorted(c, np.arange(n + 1))
    api = API * np.ceil(end_c / PER)
    return {"end": end_c, "passed": passed, "n_att": n_att, "n_xfas": n_xfas,
            "purchases": np.bincount(c, weights=pur, minlength=n), "fees": np.bincount(c, weights=fee, minlength=n),
            "cash": np.bincount(c, weights=usd, minlength=n), "api": api,
            "ev": {"c": c, "t": tt, "isc": isc, "pur": pur, "fee": fee, "usd": usd, "off": off}}


def campaign(cyc, rng, n_reps, slots, targets, cap):
    ev = cyc["ev"]; off = ev["off"]; n = cyc["end"].size
    out = {t: {"reached": np.zeros(n_reps, dtype=bool), "purch": np.full(n_reps, -1), "fees": np.full(n_reps, np.nan),
               "days": np.full(n_reps, -1)} for t in targets}
    for r in range(n_reps):
        k = 16; drawn = [rng.integers(0, n, size=k) for _ in range(slots)]
        while True:
            cs = np.concatenate(drawn); ends = cyc["end"][cs]
            starts = np.concatenate([np.cumsum(cyc["end"][d]) - cyc["end"][d] for d in drawn])
            horizon = min(cyc["end"][d].sum() for d in drawn)
            ln = off[cs + 1] - off[cs]; tot = int(ln.sum())
            idx = np.repeat(off[cs] - (np.cumsum(ln) - ln), ln) + np.arange(tot)
            tm = ev["t"][idx] + np.repeat(starts, ln)
            sel = tm < horizon
            tm = tm[sel]; isc = ev["isc"][idx][sel]; pur = ev["pur"][idx][sel]; fee = ev["fee"][idx][sel]; usd = ev["usd"][idx][sel]
            o = np.lexsort((isc, tm)); tm, pur, fee, usd = tm[o], pur[o], fee[o], usd[o]
            cc = np.cumsum(usd); cp = np.cumsum(pur); m = tm.size
            over = int(np.searchsorted(cp, cap, side="right"))
            hits = [int(np.searchsorted(cc, tg, side="left")) for tg in targets]
            if hits[-1] == m and over == m:
                drawn = [np.concatenate([d, rng.integers(0, n, size=k)]) for d in drawn]; k *= 2
                continue
            cf = np.cumsum(fee)
            for tg, h in zip(targets, hits):
                if h < m and h < over:
                    o_ = out[tg]; o_["reached"][r] = True; o_["purch"][r] = cp[h]
                    o_["fees"][r] = cf[h] + API * (tm[h] // PER + 1); o_["days"][r] = tm[h]
            break
    return out


def q_inv(vals, reached, p):
    v = np.where(reached, vals.astype(float), np.inf)
    return float(np.quantile(v, p, method="inverted_cdf"))


def boot_se(vals, reached, p, rng, b=200):
    n = vals.size; qs = []
    for _ in range(b):
        i = rng.integers(0, n, size=n); qs.append(q_inv(vals[i], reached[i], p))
    qs = np.array(qs); qs = qs[np.isfinite(qs)]
    return float(qs.std(ddof=1)) if qs.size > 1 else float("nan")


def products_from_shockset(ss):
    sp = ss.products
    return {"sig_full": np.array([s.sigma_full_usd for s in sp]), "rt_full": np.array([s.rt_full_usd for s in sp]),
            "has_micro": np.array([s.has_micro for s in sp]),
            "sig_micro": np.array([s.sigma_micro_usd if s.has_micro else np.nan for s in sp]),
            "rt_micro": np.array([s.rt_micro_usd if s.has_micro else np.nan for s in sp])}


def grid_rec(path, edge, f, dll, b2f, variant="base"):
    return next(r for r in RES["records"] if r["size"] == "50K" and r["path"] == path and r["edge"] == edge and r["f"] == f
                and r["dll"] == dll and r["pricing"] == "standard" and r["b2f"] == b2f and r["variant"] == variant
                and r["tail"] == "bootstrap" and r["direction"] == "random" and r["products"] == "all" and r["cost"] == "d8"
                and r["mode"] == "continuous")


EDGES = {"zero_k1": ("zero", 0.0, 1), "S0.5": ("sharpe", 0.5, 1), "S1": ("sharpe", 1.0, 1)}
C = SIZE["combine"]; X = SIZE["xfa"]
P_STD = float(C["monthly_price_usd"]["standard"]); R_STD = float(C["reset_price_usd"]["standard"])
ACT = float(SIZE["activation_fee_usd"]["standard"]); B2F = float(X["back2funded"]["price_usd"]); B2F_DISC = float(X["back2funded"]["dll_discount_usd"])
DLL_C = float(C["dll_option_usd"]); DLL_X = float(X["dll_option_usd"])


def main():
    t0 = time.time(); results = {"shock_sets": {}, "campaign": [], "cells": []}
    for label in ("same", "own"):
        if label == "same":
            sa = build_shocks(N, N_DAYS, SEEDS["attempt_shock"]); sx = build_shocks(N, N_DAYS, SEEDS["xfa_shock"])
            prods = products_from_shockset(sa)
            za, wa, pa = sa.z, sa.w, sa.prod.astype(np.int64); zx, wx, px = sx.z, sx.w, sx.prod.astype(np.int64)
            mine = E.products()
            results["shock_sets"][label] = {"seeds": {k: SEEDS[k] for k in ("attempt_shock", "xfa_shock")},
                                            "products_equal_mine": bool(np.allclose(prods["sig_full"], mine["sig_full"]) and np.allclose(prods["rt_full"], mine["rt_full"]))}
        else:
            prods = E.products()
            za, wa, pa = E.draw_shocks(N, N_DAYS, E.SEED_SHOCKS_ATTEMPT, prods); zx, wx, px = E.draw_shocks(N, N_DAYS, E.SEED_SHOCKS_XFA, prods)
            results["shock_sets"][label] = {"seeds": {"attempt": E.SEED_SHOCKS_ATTEMPT, "xfa": E.SEED_SHOCKS_XFA}}
        log(f"[{label}] shocks ready {time.time() - t0:.0f}s")
        rng = np.random.Generator(np.random.PCG64(77_000 + (0 if label == "same" else 1)))
        att_idx = rng.integers(0, N, size=(N_CYC, CAP_ATT)); xfa_idx = rng.integers(0, N, size=(N_CYC, 3))
        # ---- (1) campaigns: 50K standard f 0.25, dll off, b2f off
        for edge in ("zero_k1", "S0.5", "S1"):
            e, S, k = EDGES[edge]
            att = run_attempts(za, wa, pa, 0.25, e, S, k, prods, None)
            xfa = run_xfas(zx, wx, px, "standard", 0.25, e, S, k, prods, None, 0.0)
            cyc = assemble(att_idx, xfa_idx, att, xfa, P_STD, R_STD, ACT, B2F, False)
            net = cyc["cash"] - cyc["fees"] - cyc["api"]
            g = grid_rec("standard", edge, 0.25, False, False)
            crng = np.random.Generator(np.random.PCG64(88_000 + (0 if label == "same" else 1)))
            camp = campaign(cyc, crng, N_REPS, 5, (5000.0, 10000.0), PCAP)
            brng = np.random.Generator(np.random.PCG64(99))
            row = {"shocks": label, "edge": edge, "cycle_net_mine": float(net.mean()), "cycle_net_se": float(net.std(ddof=1) / math.sqrt(N_CYC)),
                   "cycle_net_grid": g["net_mean"], "p_pass_mine": float(att["passed"].mean()), "p_pass_grid": g["att_p_pass"], "targets": {}}
            for tg in (5000.0, 10000.0):
                o = camp[tg]; gc = g["campaigns"]["slots5"][f"{tg:g}"]
                tr = {"share_not_reached_mine": float(1 - o["reached"].mean()), "share_not_reached_grid": gc["share_not_reached"]}
                for p, tag in ((0.5, "p50"), (0.8, "p80")):
                    tr[f"purchases_{tag}"] = {"mine": q_inv(o["purch"], o["reached"], p), "grid": gc[f"purchases_{tag}"],
                                              "boot_se_mine": boot_se(o["purch"], o["reached"], p, brng)}
                    tr[f"fees_{tag}"] = {"mine": q_inv(o["fees"], o["reached"], p), "grid": gc[f"fees_{tag}"],
                                         "boot_se_mine": boot_se(o["fees"], o["reached"], p, brng)}
                    tr[f"days_{tag}"] = {"mine": q_inv(o["days"], o["reached"], p), "grid": gc[f"days_{tag}"]}
                row["targets"][f"{tg:g}"] = tr
                log(f"[{label}] campaign {edge} ${tg:g}: purchases P50/P80 mine {tr['purchases_p50']['mine']:.0f}/{tr['purchases_p80']['mine']:.0f} grid "
                    f"{gc['purchases_p50']:.0f}/{gc['purchases_p80']:.0f}; fees mine {tr['fees_p50']['mine']:.0f}/{tr['fees_p80']['mine']:.0f} grid "
                    f"{gc['fees_p50']:.0f}/{gc['fees_p80']:.0f}; not reached {tr['share_not_reached_mine']:.4f}/{gc['share_not_reached']:.4f} [{time.time() - t0:.0f}s]")
            results["campaign"].append(row)
        # ---- (2)-(4) cycle cells
        cells = [("2a", "consistency", "S0.5", 0.20, False, False, 0.0), ("2b", "consistency", "S0.5", 0.20, False, True, 0.0),
                 ("2c", "consistency", "S0.5", 0.25, True, False, 0.0), ("2d", "consistency", "S0.5", 0.25, True, True, 0.0),
                 ("3", "standard", "S0.5", 0.25, False, False, 0.5),
                 ("4a", "standard", "zero_k1", 0.50, True, False, 0.0), ("4b", "standard", "zero_k1", 0.50, True, True, 0.0)]
        cache = {}
        for cid, path, edge, f, dll, b2f, keep_d in cells:
            e, S, k = EDGES[edge]
            ka = (f, edge, dll)
            if ka not in cache:
                cache[ka] = run_attempts(za, wa, pa, f, e, S, k, prods, DLL_C if dll else None)
            att = cache[ka]
            kx = (path, f, edge, dll, keep_d)
            if kx not in cache:
                cache[kx] = run_xfas(zx, wx, px, path, f, e, S, k, prods, DLL_X if dll else None, keep_d)
            xfa = cache[kx]
            cyc = assemble(att_idx, xfa_idx, att, xfa, P_STD, R_STD, ACT, B2F - (B2F_DISC if dll else 0.0), b2f)
            net = cyc["cash"] - cyc["fees"] - cyc["api"]
            g = grid_rec(path, edge, f, dll, b2f, "keepd0.5" if keep_d else "base")
            row = {"cell": cid, "shocks": label, "path": path, "edge": edge, "f": f, "dll": dll, "b2f": b2f, "keep_d": keep_d,
                   "net_mine": float(net.mean()), "net_se_mine": float(net.std(ddof=1) / math.sqrt(N_CYC)), "net_grid": g["net_mean"], "net_se_grid": g["net_se"],
                   "purchases_mine": float(cyc["purchases"].mean()), "purchases_grid": g["mean_purchases"],
                   "p_pass_mine": float(att["passed"].mean()), "p_pass_grid": g["att_p_pass"],
                   "xfa_cash_mine": float(SPLIT * xfa["gross"].mean()), "xfa_cash_grid": g["xfa_mean_user_cash"],
                   "p_any_mine": float((xfa["n_pay"] > 0).mean()), "p_any_grid": g["xfa_p_any_payout"],
                   "mean_xfas_mine": float(cyc["n_xfas"].mean()), "mean_xfas_grid": g["mean_xfas"],
                   "api_mine": float(cyc["api"].mean()), "api_grid": g["fees_api"]}
            row["z_within"] = (row["net_mine"] - row["net_grid"]) / math.sqrt(row["net_se_mine"] ** 2 + row["net_se_grid"] ** 2)
            results["cells"].append(row)
            log(f"[{label}] cell {cid} {path} {edge} f={f} dll={dll} b2f={b2f} keep_d={keep_d}: net mine {row['net_mine']:.1f} ({row['net_se_mine']:.1f}) grid "
                f"{row['net_grid']:.1f} ({row['net_se_grid']:.1f}) z {row['z_within']:+.2f}; P(pass) {row['p_pass_mine']:.4f}/{row['p_pass_grid']:.4f}; "
                f"cash/XFA {row['xfa_cash_mine']:.1f}/{row['xfa_cash_grid']:.1f}; xfas {row['mean_xfas_mine']:.3f}/{row['mean_xfas_grid']:.3f} [{time.time() - t0:.0f}s]")
    results["elapsed_s"] = round(time.time() - t0, 1)
    (OUT / "phase_c.json").write_text(json.dumps(results, indent=1, default=str))
    log("done", results["elapsed_s"])


if __name__ == "__main__":
    main()
