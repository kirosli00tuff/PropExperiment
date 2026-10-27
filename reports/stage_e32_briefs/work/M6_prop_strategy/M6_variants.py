"""M6 (E.32): per-firm, per-execution-variant values of a directional ZM signal (stylised model, no data).

Same Brownian model as M6_limit.py (sigma 3.15 ticks/sqrt(min), spread 1 tick, horizon 15 min, constant drift,
1-second grid, buy limit at the bid: TT fills when mid <= -1.0, queue proxy Q when mid <= -0.5), run on a grid of
alpha = E[X_H] with common random numbers. For each firm and each variant its route admits, per SIGNAL (ticks):
  M     market entry, market exit:            alpha - 1 - F
  L     limit entry (timeout tau), no chase:  p (E[G|F] - cal - F)            (0 when unfilled)
  LC    limit, chase at market after tau:     p (E[G|F] - cal - F) + (1-p)(E[X_H - X_tau | nF] - 1 - F)
cal = E.31 excess adverse markout per fill beyond the model's own (TT 0.470; Q-K 0.287; Q-FIFO 0.252), or 0 ("BM").
Break-even alpha (value 0) and the alpha giving 1.0 tick net per EXECUTED trade are found by linear interpolation.
Then the funnel (M6_funnel.run) is run for S15 (alpha 2.0, 6 signals a day) per firm and variant.
Run: nice -n 10 python3 M6_variants.py   (writes M6_variants_out.json, prints a compact table)
"""
import json
import math
import os

import numpy as np

SIG = 3.15
H = 15.0
DT = 1.0 / 60.0
NSTEP = int(round(H / DT))
NPATH = 100_000
CHUNK = 20_000
SEED = 20261027
TAUS = (0.5, 1.0, 5.0)
ALPHAS = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0)
D_FILL = {"TT": 1.0, "Q": 0.5}
FEE = {"topstep": 0.528, "lucid": 0.560, "lucid_u": 0.920, "tradeify": 0.920, "mffu": 0.612, "bulenox": 0.572}
CAL = {"TT": 0.470, "QK": 0.287, "QF": 0.252}
# variants admitted per firm route: (label, fill rule, calibration key or None)
ROUTES = {
    "topstep": [("TT", "TT")],
    "lucid": [("TT[CQG assumed]", "TT"), ("QK[Rithmic]", "QK"), ("QF[Rithmic]", "QF")],
    "lucid_u": [("TT[CQG assumed]", "TT"), ("QK[Rithmic]", "QK"), ("QF[Rithmic]", "QF")],
    "tradeify": [("TT[Tradovate]", "TT"), ("QK[Rithmic]", "QK"), ("QF[Rithmic]", "QF")],
    "mffu": [("TT", "TT")],
    "bulenox": [("QK", "QK"), ("QF", "QF")],
}


def simulate():
    rng = np.random.default_rng(SEED)
    acc = {}

    def add(k, v):
        acc[k] = acc.get(k, 0.0) + float(v)

    t = np.arange(1, NSTEP + 1, dtype=np.float32) * np.float32(DT)
    for _ in range(NPATH // CHUNK):
        w = np.cumsum(rng.standard_normal((CHUNK, NSTEP)).astype(np.float32) * np.float32(SIG * math.sqrt(DT)),
                      axis=1)
        for a in ALPHAS:
            x = w + np.float32(a / H) * t
            xh = x[:, -1].astype(np.float64)
            add(f"{a}_n", CHUNK)
            add(f"{a}_xh", xh.sum())
            for rule, d in D_FILL.items():
                for tau in TAUS:
                    k = int(round(tau / DT))
                    filled = (x[:, :k].min(axis=1) <= -d)
                    xt = x[:, k - 1].astype(np.float64)
                    key = f"{a}_{rule}_{tau}"
                    add(key + "_nf", filled.sum())
                    add(key + "_xhf", xh[filled].sum())
                    add(key + "_xhnf", xh[~filled].sum())
                    add(key + "_chase", (xh[~filled] - xt[~filled]).sum())
        del w
    res = {}
    for a in ALPHAS:
        n = acc[f"{a}_n"]
        res[a] = {"alpha_sim": acc[f"{a}_xh"] / n}
        for rule in D_FILL:
            for tau in TAUS:
                key = f"{a}_{rule}_{tau}"
                nf = acc[key + "_nf"]
                res[a][f"{rule}_{tau}"] = dict(p=nf / n, EGf=acc[key + "_xhf"] / nf,
                                               EGnf=acc[key + "_xhnf"] / (n - nf),
                                               chase=acc[key + "_chase"] / (n - nf))
    return res


def values(res, a, fee, rule_key, tau, calibrated):
    """Per-signal values (ticks) and per-executed-trade value for one alpha."""
    r = res[a]
    out = {"M": r["alpha_sim"] - 1 - fee}
    fill = "TT" if rule_key == "TT" else "Q"
    q = r[f"{fill}_{tau}"]
    cal = CAL[rule_key] if calibrated else 0.0
    p = q["p"]
    vf = q["EGf"] - cal - fee
    out["L"] = p * vf
    out["L_per_trade"] = vf
    out["LC"] = p * vf + (1 - p) * (q["chase"] - 1 - fee)
    out["p"] = p
    return out


def interp_root(xs, ys, target):
    for i in range(len(xs) - 1):
        y0, y1 = ys[i] - target, ys[i + 1] - target
        if y0 == 0:
            return xs[i]
        if y0 < 0 <= y1 or y0 > 0 >= y1:
            return xs[i] + (xs[i + 1] - xs[i]) * (-y0) / (y1 - y0)
    return None


def main():
    try:
        os.nice(10)
    except OSError:
        pass
    res = simulate()
    out = {"params": dict(SIG=SIG, H=H, NPATH=NPATH, SEED=SEED, TAUS=TAUS, ALPHAS=ALPHAS, CAL=CAL, FEE=FEE),
           "sim": {str(a): res[a] for a in ALPHAS}, "firm": {}}
    xs = [res[a]["alpha_sim"] for a in ALPHAS]
    for firm, fee in FEE.items():
        f_out = {}
        vm = [values(res, a, fee, "TT", 1.0, False)["M"] for a in ALPHAS]
        f_out["M"] = dict(alpha_be=interp_root(xs, vm, 0.0), alpha_net1=interp_root(xs, vm, 1.0),
                          S15=values(res, 2.0, fee, "TT", 1.0, False)["M"])
        for label, rk in ROUTES[firm]:
            for tau in TAUS:
                for cal in (False, True):
                    v = [values(res, a, fee, rk, tau, cal) for a in ALPHAS]
                    tag = f"{label}|tau={tau}|{'E31cal' if cal else 'BM'}"
                    f_out[tag] = dict(
                        alpha_be_L=interp_root(xs, [z["L"] for z in v], 0.0),
                        alpha_net1_per_trade_L=interp_root(xs, [z["L_per_trade"] for z in v], 1.0),
                        alpha_be_LC=interp_root(xs, [z["LC"] for z in v], 0.0),
                        alpha_net1_LC=interp_root(xs, [z["LC"] for z in v], 1.0),
                        S15=values(res, 2.0, fee, rk, tau, cal))
        out["firm"][firm] = f_out
    # funnel per firm and variant for S15 (tau = 1, E.31-calibrated limit values; BM shown in json only)
    import M6_funnel as fn
    fun = []
    base_T = fn.T_TRADES
    for firm in ("topstep", "lucid", "tradeify", "mffu", "bulenox"):
        f_out = out["firm"][firm]
        cases = [("M", f_out["M"]["S15"], base_T)]
        for tag, d in f_out.items():
            if tag == "M" or "|tau=1.0|E31cal" not in tag:
                continue
            s = d["S15"]
            cases.append((tag + "|L", s["L_per_trade"], base_T * s["p"]))
            cases.append((tag + "|LC", s["LC"], base_T))
        for tag, mu, T in cases:
            fn.T_TRADES = T
            r = fn.run(firm, mu, 1)
            r.update(case=tag, T=T)
            fun.append(r)
    fn.T_TRADES = base_T
    out["funnel_S15"] = fun
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "M6_variants_out.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("alpha_sim:", [round(x, 3) for x in xs])
    for firm, f_out in out["firm"].items():
        for tag, d in f_out.items():
            if tag != "M" and "|tau=1.0|" not in tag:
                continue
            if tag == "M":
                print(f"{firm:9s} M  be={d['alpha_be']:.3f} net1={d['alpha_net1']:.3f} S15={d['S15']:.3f}")
            else:
                s = d["S15"]
                fmt = lambda z: "None" if z is None else f"{z:.3f}"
                print(f"{firm:9s} {tag:34s} p={s['p']:.3f} S15 L={s['L']:.3f} L/tr={s['L_per_trade']:.3f} "
                      f"LC={s['LC']:.3f} beL={fmt(d['alpha_be_L'])} net1trL={fmt(d['alpha_net1_per_trade_L'])} "
                      f"beLC={fmt(d['alpha_be_LC'])} net1LC={fmt(d['alpha_net1_LC'])}")
    for r in fun:
        print(f"FUN {r['firm']:8s} {r['case']:40s} mu={r['mu_net']:.3f} T={r['T']:.2f} dll={r['p_dll_eval_m1']:.4f} "
              f"br={r['p_breach_eval_m1']:.3f} pass={r['p_pass_first_attempt']:.3f} paid={r['p_paid_within_756']:.3f} "
              f"days={r['mean_days_to_first_payout']} fees={r['mean_fees_to_first_payout']}")


if __name__ == "__main__":
    main()
