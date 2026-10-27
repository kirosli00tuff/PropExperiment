"""M6 (E.32): stylised Brownian model of a directional limit entry vs a market entry on ZM.

No market data is read. Every number is a model output from the stated assumptions:
  mid X_t (ticks, signed in the signal's direction, X_0 = 0) = drift + sigma W_t,
  sigma = 3.15 ticks per sqrt(minute) (E.28 A0 Table 1, ZM sigma_1m), spread 1 tick,
  signal horizon H = 15 min, expected move alpha = E[X_H] = 2.0 ticks.
Drift profiles: 'const' (mu = alpha / H) and 'front' (rate (alpha/(1-exp(-H/theta)))/theta * exp(-t/theta),
theta = 3 min, so E[X_H] = alpha and most of it arrives early).
Fill rules for a buy limit at the bid (price -0.5): trade-through (TT) fills when X_t <= -1.0;
queue proxy (Q) fills when X_t <= -0.5. A sell limit at price L fills when X >= L + 0.5 (TT) or X >= L (Q).
Run: nice -n 10 python3 M6_limit.py  (prints a compact table; writes M6_limit_out.json)
"""
import json
import math
import os

import numpy as np

SIG = 3.15          # ticks / sqrt(min)
H = 15.0            # min
ALPHA = 2.0         # ticks over H
DT = 1.0 / 60.0     # 1 second in minutes
NSTEP = int(round(H / DT))
NPATH = 200_000
CHUNK = 20_000
SEED = 20261027
THETA = 3.0
TAUS = (0.5, 1.0, 2.0, 5.0)
D_FILL = {"TT": 1.0, "Q": 0.5}


def drift_increments(profile):
    t = np.arange(NSTEP + 1) * DT
    if profile == "const":
        cum = ALPHA * t / H
    else:
        cum = ALPHA * (1 - np.exp(-t / THETA)) / (1 - np.exp(-H / THETA))
    return np.diff(cum)


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def closed_form_const(d, tau):
    """P(min_{t<=tau} X_t <= -d) and E[t_f | t_f <= tau] for X = mu t + sig W, mu = ALPHA/H."""
    mu = ALPHA / H
    s = SIG * math.sqrt(tau)
    p = norm_cdf((-d - mu * tau) / s) + math.exp(-2 * mu * d / SIG ** 2) * norm_cdf((-d + mu * tau) / s)
    # first-passage density to -d with drift +mu: d/(sig sqrt(2 pi t^3)) exp(-(d + mu t)^2/(2 sig^2 t))
    n = 200_000
    t = (np.arange(n) + 0.5) * tau / n
    f = d / (SIG * np.sqrt(2 * np.pi * t ** 3)) * np.exp(-(d + mu * t) ** 2 / (2 * SIG ** 2 * t))
    p_int = float(np.sum(f) * tau / n)
    et = float(np.sum(t * f) * tau / n) / p_int
    return p, p_int, et


def simulate(profile):
    rng = np.random.default_rng(SEED)
    inc_mu = drift_increments(profile).astype(np.float64)
    acc = {}
    def add(k, v):
        acc[k] = acc.get(k, 0.0) + float(v)
    for c in range(NPATH // CHUNK):
        z = rng.standard_normal((CHUNK, NSTEP)).astype(np.float32)
        x = np.cumsum(z * np.float32(SIG * math.sqrt(DT)) + inc_mu.astype(np.float32), axis=1)
        x = np.concatenate([np.zeros((CHUNK, 1), np.float32), x], axis=1)
        xh = x[:, -1].astype(np.float64)
        add("n", CHUNK); add("sum_xh", xh.sum())
        runmin = np.minimum.accumulate(x, axis=1)
        for rule, d in D_FILL.items():
            for tau in TAUS:
                k = int(round(tau / DT))
                filled = runmin[:, k] <= -d
                xt = x[:, k].astype(np.float64)
                key = f"{rule}_{tau}"
                add(key + "_nf", filled.sum())
                add(key + "_xh_f", xh[filled].sum())
                add(key + "_xh_nf", xh[~filled].sum())
                add(key + "_chase_nf", (xh[~filled] - xt[~filled] - 0.5).sum())
                add(key + "_xt_nf", xt[~filled].sum())
                # fill time
                hit = np.argmax(x[filled, : k + 1] <= -d, axis=1) * DT
                add(key + "_tf", hit.sum())
        # bracket: market buy at +0.5; TP sell limit at L = 0.5 + A; stop when mid <= -B (sell at mid - 0.5);
        # time stop at H (sell at X_H - 0.5). Trigger level for the TP: TT mid >= L + 0.5; Q mid >= L.
        for a_tp in (4.0, 6.0, 10.0):
            b_sl = 6.0
            L = 0.5 + a_tp
            for rule, trig in (("TT", L + 0.5), ("Q", L), ("MKTatTT", L + 0.5)):
                up = x >= trig
                dn = x <= -b_sl
                t_up = np.where(up.any(1), up.argmax(1), NSTEP + 1)
                t_dn = np.where(dn.any(1), dn.argmax(1), NSTEP + 1)
                tp = t_up < t_dn
                sl = (t_dn < t_up)
                ts = ~(tp | sl)
                exit_tp = L if rule != "MKTatTT" else (L + 0.5 - 0.5)   # market sell at bid = mid - 0.5
                pnl = np.empty(CHUNK)
                pnl[tp] = exit_tp - 0.5
                # stop: mid crosses -B on a 1 s grid; sell at the bid at that moment
                pnl[sl] = x[sl, t_dn[sl]] - 0.5 - 0.5
                pnl[ts] = xh[ts] - 0.5 - 0.5
                key = f"BR_{a_tp}_{rule}"
                add(key + "_pnl", pnl.sum()); add(key + "_ptp", tp.sum()); add(key + "_psl", sl.sum())
        del z, x, runmin
    n = acc["n"]
    out = {"alpha_sim": acc["sum_xh"] / n}
    for rule in D_FILL:
        for tau in TAUS:
            key = f"{rule}_{tau}"
            nf = acc[key + "_nf"]
            p = nf / n
            e_f = acc[key + "_xh_f"] / nf
            e_nf = acc[key + "_xh_nf"] / (n - nf)
            out[key] = {
                "p_fill": p, "E_XH_fill": e_f, "E_XH_nofill": e_nf,
                "E_tf_fill": acc[key + "_tf"] / nf,
                "E_Xtau_nofill": acc[key + "_xt_nf"] / (n - nf),
                "limit_entry_value_per_signal": p * (e_f + 0.5),
                "limit_entry_value_per_fill": e_f + 0.5,
                "chase_value_given_nofill": acc[key + "_chase_nf"] / (n - nf),
                "limit_plus_chase_per_signal": p * (e_f + 0.5) + acc[key + "_chase_nf"] / n,
            }
    for a_tp in (4.0, 6.0, 10.0):
        for rule in ("TT", "Q", "MKTatTT"):
            key = f"BR_{a_tp}_{rule}"
            out[key] = {"E_pnl_gross_ex_fee": acc[key + "_pnl"] / n, "P_tp": acc[key + "_ptp"] / n,
                        "P_sl": acc[key + "_psl"] / n}
    out["market_entry_value"] = out["alpha_sim"] - 0.5
    return out


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    res = {"params": {"sigma": SIG, "H": H, "alpha": ALPHA, "dt_min": DT, "npath": NPATH, "seed": SEED,
                      "theta": THETA, "d_fill": D_FILL}}
    res["closed_form_const"] = {f"{r}_{t}": closed_form_const(d, t) for r, d in D_FILL.items() for t in TAUS}
    for prof in ("const", "front"):
        res[prof] = simulate(prof)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "M6_limit_out.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    for prof in ("const", "front"):
        r = res[prof]
        print(prof, "alpha_sim %.3f market %.3f" % (r["alpha_sim"], r["market_entry_value"]))
        for rule in D_FILL:
            for tau in TAUS:
                v = r[f"{rule}_{tau}"]
                print(" %s tau=%.1f p=%.3f E|f=%.3f E|nf=%.3f tf=%.3f lim/sig=%.3f lim/fill=%.3f chase|nf=%.3f lim+chase=%.3f" % (
                    rule, tau, v["p_fill"], v["E_XH_fill"], v["E_XH_nofill"], v["E_tf_fill"],
                    v["limit_entry_value_per_signal"], v["limit_entry_value_per_fill"],
                    v["chase_value_given_nofill"], v["limit_plus_chase_per_signal"]))
        for a_tp in (4.0, 6.0, 10.0):
            print(" BR a=%g " % a_tp + " ".join("%s:E=%.3f,Ptp=%.3f,Psl=%.3f" % (
                rl, r[f"BR_{a_tp}_{rl}"]["E_pnl_gross_ex_fee"], r[f"BR_{a_tp}_{rl}"]["P_tp"],
                r[f"BR_{a_tp}_{rl}"]["P_sl"]) for rl in ("TT", "Q", "MKTatTT")))
    for k, v in res["closed_form_const"].items():
        print(" CF", k, "p=%.4f p_int=%.4f E_tf=%.3f" % v)


if __name__ == "__main__":
    main()
