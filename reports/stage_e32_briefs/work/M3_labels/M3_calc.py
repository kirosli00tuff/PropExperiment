"""M3_labels worked-example arithmetic (E.32). No market data is read; inputs are the brief's standard numbers.

Prints every number used in reports/stage_e32_briefs/M3_labels.md so a reviewer can recompute them.
"""
import math

SIG1 = 3.15          # ticks, ZM sigma_1m, main session, A0 Table 1
FEE = 0.528          # ticks per round trip, Topstep ZM (5.28 USD / 10 USD per tick)
SPREAD = 1.0         # ticks, E.28 default S_rt (unsourced, "u")
C_MKT = FEE + SPREAD # 1.528, E.28 c_mkt
BE = 1.59            # E.28 ranking row 130, mu*_mkt (prop-account break-even incl. account economics)
SESSION = 290        # minutes, 08:30-13:20 CT
HORIZONS = [1, 5, 15, 30, 60, 120, 240]
SQ2PI = math.sqrt(2 / math.pi)


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def p_strip_survive(a):
    """P(sup_{0<=t<=1} |W_t| < a) for standard Brownian motion (Feller series)."""
    s = 0.0
    for n in range(200):
        k = 2 * n + 1
        s += (-1) ** n / k * math.exp(-k * k * math.pi ** 2 / (8 * a * a))
    return 4 / math.pi * s


def horizon_table():
    print("== (e/f) per-horizon break-even table, cost BE=%.3f ticks (alt c_mkt=%.3f)" % (BE, C_MKT))
    rows = [(str(h), h) for h in HORIZONS]
    rows.append(("close, entry 08:30 (290)", SESSION))
    # mean of sigma over a uniform entry time in the session: E[sqrt(U*290)] = (2/3) sqrt(290)
    rows.append(("close, uniform entry (eff.)", (2 / 3) ** 2 * SESSION))
    print("h | sigma_h | E|dP| | p*_fixed(BE) | p*_fixed(c_mkt) | BE/sigma_h | p*_sym(k=sigma_h) | P(vertical first,k=sigma_h) | p*_sym(k=2sigma_h)")
    for name, h in rows:
        sh = SIG1 * math.sqrt(h)
        ead = sh * SQ2PI
        p_fix = 0.5 + BE / (2 * ead)
        p_fix_c = 0.5 + C_MKT / (2 * ead)
        p_sym = 0.5 + BE / (2 * sh)
        pv = p_strip_survive(1.0)
        p_sym2 = 0.5 + BE / (2 * 2 * sh)
        print(f"{name} | {sh:.3f} | {ead:.3f} | {p_fix:.4f} | {p_fix_c:.4f} | {BE/sh:.4f} | {p_sym:.4f} | {pv:.4f} | {p_sym2:.4f}")
    print("P(vertical first) for k = 2 sigma_h:", round(p_strip_survive(2.0), 4))


def fixed_barriers():
    print("== fixed +-k tick barriers (planner's +-4-6): break-even hit rate and expected first-exit time")
    for k in (2, 3, 4, 5, 6, 8):
        p = 0.5 + BE / (2 * k)
        et = k * k / SIG1 ** 2  # minutes, E[tau] = a^2/sigma^2 for driftless BM in (-a, a)
        # horizon by which 95% of paths have exited: solve P(survive) at a = k/(SIG1 sqrt(h)) = 0.05
        lo, hi = 0.01, 1000.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if p_strip_survive(k / (SIG1 * math.sqrt(mid))) > 0.05:
                lo = mid  # still more than 5% of paths inside the strip: need a longer horizon
            else:
                hi = mid
        print(f"k={k}: p*={p:.4f}  E[tau]={et:.3f} min  t95={hi:.2f} min  net win={k-BE:.2f} net loss={-k-BE:.2f}")


def sharpe_link():
    print("== hit rate to per-trade Sharpe, symmetric +-5 barriers, cost BE")
    k = 5
    for p in (0.659, 0.68, 0.70):
        m = (2 * p - 1) * k - BE
        s = 2 * k * math.sqrt(p * (1 - p))
        print(f"p={p}: mean={m:.4f} sd={s:.4f} SR/trade={m/s:.4f}")


def uniqueness_15m():
    print("== average uniqueness, 15-min labels sampled every minute, one 290-min session")
    h = 15
    starts = list(range(0, SESSION - h + 1))  # t0 = 0..275; label uses returns t0+1..t0+h
    n_lab = len(starts)
    c = [0] * (SESSION + 1)
    for t0 in starts:
        for j in range(t0 + 1, t0 + h + 1):
            c[j] += 1
    ubar = []
    for t0 in starts:
        u = sum(1 / c[j] for j in range(t0 + 1, t0 + h + 1)) / h
        ubar.append(u)
    covered = sum(1 for j in range(1, SESSION + 1) if c[j] > 0)
    print("labels", n_lab, "bars covered", covered, "max c", max(c))
    print("u_bar first 3:", [round(x, 4) for x in ubar[:3]], "interior:", round(ubar[100], 4), "last:", round(ubar[-1], 4))
    print("mean u_bar", round(sum(ubar) / n_lab, 5), "n_eff = sum u_bar", round(sum(ubar), 4), "check covered/h", round(covered / h, 4))
    # hand check for first label t0=0: c_j = j for j=1..15 -> u = (1/15) * H_15
    H15 = sum(1 / j for j in range(1, 16))
    print("first label by hand (1/15)*H_15 =", round(H15 / 15, 4))
    # 39 months scale: ~ 815 DAY dates (E.31 had 816 trade dates)
    print("per 816 dates: labels", n_lab * 816, "n_eff", round(sum(ubar) * 816, 1))


def time_decay():
    print("== time-decay weights (AFML 4.7 as implemented in mlfinpy), c=0.5 and c=-0.25, 4 labels with u_bar")
    u = [0.5, 0.5, 1.0, 1.0]
    cum = [sum(u[:i + 1]) for i in range(len(u))]
    tot = cum[-1]
    for cdec in (0.5, -0.25):
        slope = (1 - cdec) / tot if cdec >= 0 else 1 / ((cdec + 1) * tot)
        const = 1 - slope * tot
        w = [max(0.0, const + slope * x) for x in cum]
        print(f"c={cdec}: slope={slope:.4f} const={const:.4f} weights={[round(x, 4) for x in w]}")


def exec_vs_mid():
    print("== executable vs mid labels and latency")
    for lat in (0.3, 1.0):
        sd = SIG1 * math.sqrt(lat / 60)
        print(f"latency {lat}s: sd of mid move during latency = {sd:.3f} ticks")
    # exp. adverse drift if the signal's expected move mu_h accrues linearly: loss = mu_h * L/(60 h)
    for h in (1, 5, 15):
        print(f"h={h}: fraction of linear-accrual edge lost to 1 s latency = {1/(60*h):.4f}")


def dead_zone():
    print("== dead-zone classification on a fixed horizon, tau = BE")
    for h in (5, 15, 60):
        sh = SIG1 * math.sqrt(h)
        p0 = 2 * norm_cdf(BE / sh) - 1
        print(f"h={h}: P(|dP|<=BE) under N(0,sigma_h) = {p0:.4f}")


def cusum_example():
    print("== symmetric CUSUM toy, threshold 6 ticks, on price changes in ticks")
    dp = [2, 1, -1, 3, 1, -2, -3, -2, 1, -2, 0, 4]
    sp = sn = 0
    ev = []
    for i, y in enumerate(dp, 1):
        sp = max(0, sp + y)
        sn = min(0, sn + y)
        tag = ""
        if sn < -6:
            sn = 0
            tag = "EVENT(-)"
            ev.append(i)
        elif sp > 6:
            sp = 0
            tag = "EVENT(+)"
            ev.append(i)
        print(f"t={i} y={y:+d} S+={sp} S-={sn} {tag}")
    print("events at", ev)
    # expected CUSUM sampling rate under a RW: E[time to |S| > h] ~ order h^2 / sigma^2
    for thr in (6, 10, 15):
        print(f"thr={thr} ticks: one-sided reflected-RW mean time to cross (upper bound on spacing) thr^2/sigma_1m^2 = {thr*thr/SIG1**2:.2f} min")


if __name__ == "__main__":
    horizon_table()
    fixed_barriers()
    sharpe_link()
    uniqueness_15m()
    time_decay()
    exec_vs_mid()
    dead_zone()
    cusum_example()


def detectability():
    """Day-session non-overlapping trades over 816 trade dates; t-stat of a classifier sitting exactly at p*."""
    print("== detectability: n_indep = 816 * floor(290/h); se = 0.5/sqrt(n); t at p* = (p*-0.5)/se")
    for name, h in [(str(x), x) for x in HORIZONS] + [("close(290)", SESSION)]:
        n = 816 * (SESSION // h)
        se = 0.5 / math.sqrt(n)
        ead = SIG1 * math.sqrt(h) * SQ2PI
        pst = 0.5 + BE / (2 * ead)
        print(f"h={name}: n={n} se={se:.5f} p*-0.5={pst-0.5:.4f} t_at_p*={(pst-0.5)/se:.2f} p_needed_for_t3_vs_p*={pst+3*se:.4f}")


if __name__ == "__main__":
    detectability()
