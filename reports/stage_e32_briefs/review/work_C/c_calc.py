"""MathReviewer C: independent recomputation of every closed-form number in M5a (d), (f), M5b (0),
(a.3), (b.3), (c), (d) and the p7 threshold output. Own formulas only; the program's code is not
imported here. Prints compact results.
"""
from __future__ import annotations

import math
from statistics import NormalDist

N_ = NormalDist()
PHI, PPF = N_.cdf, N_.inv_cdf
GAMMA = 0.5772156649015329
SIG1 = 3.15
COST = 1.59
ZB80 = PPF(0.8)


def sig(h: float) -> float:
    return SIG1 * math.sqrt(h)


def e_n(n: int) -> float:
    return (1 - GAMMA) * PPF(1 - 1 / n) + GAMMA * PPF(1 - 1 / (n * math.e))


def exact_emax(n: int) -> float:
    """E[max of n iid N(0,1)] by integrating 1 - F(x)^n on x>0 minus F(x)^n on x<0 (trapezoid)."""
    lo, hi, steps = -8.0, 8.0, 32000
    dx = (hi - lo) / steps
    tot = 0.0
    for i in range(steps + 1):
        x = lo + i * dx
        f = PHI(x) ** n
        g = (1 - f) if x >= 0 else -f
        w = 0.5 if i in (0, steps) else 1.0
        tot += w * g
    return tot * dx


def dsr(sr: float, t: int, sr0: float, g3: float, g4: float) -> float:
    d = 1 - g3 * sr + (g4 - 1) / 4 * sr * sr
    return PHI((sr - sr0) * math.sqrt(t - 1) / math.sqrt(d))


def solve_sr(t: int, n: int, v: float, g3: float, g4: float, target: float = 0.95) -> float:
    sr0 = math.sqrt(v) * e_n(n)
    lo, hi = 0.0, 1.5
    for _ in range(200):
        mid = (lo + hi) / 2
        if dsr(mid, t, sr0, g3, g4) >= target:
            hi = mid
        else:
            lo = mid
    return hi


def harmonic(m: int) -> float:
    return sum(1 / i for i in range(1, m + 1))


def max_equicorr_q(m: int, rho: float, q: float = 0.95) -> float:
    """q-quantile of max of m equicorrelated N(0,1) via P(max<=x)=E_z[Phi((x-sqrt(rho)z)/sqrt(1-rho))^m]."""
    def cdf(x: float) -> float:
        lo, hi, steps = -8.0, 8.0, 4000
        dz = (hi - lo) / steps
        s = 0.0
        for i in range(steps + 1):
            z = lo + i * dz
            w = 0.5 if i in (0, steps) else 1.0
            s += w * N_.pdf(z) * PHI((x - math.sqrt(rho) * z) / math.sqrt(1 - rho)) ** m
        return s * dz
    lo, hi = 0.0, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cdf(mid) >= q:
            hi = mid
        else:
            lo = mid
    return hi


def binom_tail(m: int, k: int) -> float:
    return sum(math.comb(m, j) for j in range(k, m + 1)) / 2 ** m


def main() -> None:
    print("== constants ==")
    for h in (5, 15, 30, 60, 75, 120, 240):
        print(f"sigma_{h} = {sig(h):.3f}")
    print(f"z(0.05)={PPF(0.95):.4f} z(0.05/3)={PPF(1-0.05/3):.4f} z80={ZB80:.4f} p(t>3) one-sided={1-PHI(3):.5f}")

    print("\n== M5a d.3(i) e(N) vs exact E[max] ==")
    for n in (45, 538, 738, 1038, 1538, 5538):
        print(f"N={n}: e(N)={e_n(n):.4f}  exact E[max]={exact_emax(n):.4f}  sqrt(2lnN)={math.sqrt(2*math.log(n)):.4f}"
              f"  e^2={e_n(n)**2:.2f}  e/sqrt(3.25)={e_n(n)/math.sqrt(3.25):.2f}")

    print("\n== M5a d.3(ii) DSR bar rows (V=1/T) ==")
    rows = [(15, 408, 738), (15, 408, 1538), (15, 408, 5538), (15, 816, 738), (15, 816, 1538), (15, 816, 5538),
            (15, 3264, 738), (15, 3264, 5538), (60, 816, 738), (60, 816, 5538), (60, 3264, 5538)]
    for h, t, n in rows:
        v = 1 / t
        sr0 = math.sqrt(v) * e_n(n)
        s3 = solve_sr(t, n, v, 0, 3)
        s8 = solve_sr(t, n, v, 0, 8)
        sk = solve_sr(t, n, v, -0.5, 8)
        tstar = s3 * math.sqrt(t)
        gross = COST + s3 * sig(h)
        q = t / 3.25
        print(f"h={h} T={t} N={n}: SR0={sr0:.4f} SR*={s3:.4f}/{s8:.4f}/{sk:.4f} t*={tstar:.2f} "
              f"gross={gross:.2f} q={q:.1f} SRann={s3*math.sqrt(q):.2f} e+1.645={e_n(n)+PPF(0.95):.3f}")

    print("\n== M5a d.3(iii) fixed candidate h=15 T=816 g4=8 ==")
    for gross in (3.0, 3.5):
        sr = (gross - COST) / sig(15)
        t = sr * math.sqrt(816)
        out = [f"{dsr(sr, 816, math.sqrt(1/816)*e_n(n), 0, 8):.3f}" for n in (538, 738, 1538, 5538)]
        print(f"gross {gross}: SR={sr:.4f} t={t:.2f} DSR@538/738/1538/5538 = {' '.join(out)}")

    print("\n== M5a d.3(v) effective N table e(N_hat+538) ==")
    for m in (200, 1000, 5000):
        cells = []
        for rho in (0.3, 0.5, 0.7, 0.9):
            nh = rho + (1 - rho) * m
            cells.append(f"{nh:.1f} (N {nh+538:.0f}, e {e_n(round(nh+538)):.3f})")
        print(f"M={m}: " + " | ".join(cells))
    for k, rho in ((1000, 0.5), (1000, 0.8)):
        print(f"K_eff one-factor K={k} rho={rho}: {k/(1+(k-1)*rho*rho):.2f}")
    print(f"K_eff 50x20 within .95: {1e6/(1000+1000*19*0.95**2):.1f}; 200x5 within .9: {1e6/(1000+1000*4*0.81):.1f}")
    print(f"(1-rho)/T at rho .5: {0.5/816:.6f}")

    print("\n== M5a f.3 thresholds ==")
    for m in (3, 200, 738, 1000, 1538, 5000, 5538):
        pb = 0.05 / m
        lm = harmonic(m)
        pby = 0.05 / (m * lm)
        p3 = min(3 * 0.05 / m, 0.5)
        print(f"m={m}: Bonf p={pb:.3g} z={PPF(1-pb):.3f} | BY p={pby:.3g} z={PPF(1-pby):.3f} L_m={lm:.3f} | BH3 p={p3:.3g} z={PPF(1-p3):.3f}")
    print(f"HLZ: one-sided p={1-PHI(3):.5f}; 0.05/p = {0.05/(1-PHI(3)):.1f}")
    for n, tstar in ((738, e_n(738) + PPF(0.95)), (1538, e_n(1538) + PPF(0.95)), (5538, e_n(5538) + PPF(0.95))):
        size = 1 - PHI(tstar) ** n
        print(f"DSR-as-test N={n} t*={tstar:.3f} size={size:.2e}  (x0.05 => {0.05/size:.0f} times stricter)")
    print(f"Bonf 3x4: z={PPF(1-0.05/12):.3f}; 3x5: z={PPF(1-0.05/15):.3f}; Holm over 3: {PPF(1-0.05/3):.3f} {PPF(1-0.025):.3f} {PPF(0.95):.3f}")

    print("\n== M5a f.3 equicorrelated max 95% quantile (numerical integration) ==")
    for m in (738, 1538, 5538):
        print(f"m={m}: rho0={PPF(0.95**(1/m)):.3f} rho.5={max_equicorr_q(m,0.5):.3f} rho.8={max_equicorr_q(m,0.8):.3f} Bonf={PPF(1-0.05/m):.3f}")

    print("\n== M5a f.3 ZM units at the test (h=15, sigma 12.20, c 1.59) ==")
    for tdates in (899, 905):
        for z, lab in ((PPF(0.95), "1.645"), (PPF(1-0.05/3), "2.128"), (3.0, "3.0")):
            sr = z / math.sqrt(tdates)
            print(f"T={tdates} z={lab}: SR={sr:.4f} net={sr*sig(15):.2f} gross={COST+sr*sig(15):.2f}")
        sr = PPF(1-0.05/3) / math.sqrt(tdates / 2)
        print(f"T={tdates}/2 z=2.128: SR={sr:.4f} net={sr*sig(15):.2f} gross={COST+sr*sig(15):.2f}")
        for s in (0.1689, 0.0845, 0.060):
            ez = s * math.sqrt(tdates)
            print(f"  true SR {s}: E z={ez:.2f} power@2.128={PHI(ez-PPF(1-0.05/3)):.3f} power@3={PHI(ez-3):.3f}")

    print("\n== p7 cross-check: required daily SR for DSR>=0.95 at N=1038 ==")
    n = 1038
    for t in (816, 905):
        for c in (0.25, 0.5, 1.0, 2.0):
            v = c / (t - 1)
            emax = math.sqrt(v) * e_n(n)
            sn = solve_sr(t, n, v, 0, 3)
            sf = solve_sr(t, n, v, -0.5, 6)
            print(f"T={t} c={c}: V={v:.6f} Emax={emax:.4f} SR*norm={sn:.4f} ann={sn*math.sqrt(252):.2f} "
                  f"SR*skew={sf:.4f} ann={sf*math.sqrt(252):.2f} t*={sn*math.sqrt(t):.2f}")
    t = 905
    tbar = 3 / math.sqrt(t)
    print(f"t-bar daily SR at T=905: {tbar:.4f}; +z80/sqrt(T) = {tbar + ZB80/math.sqrt(t):.4f}; ann {(tbar + ZB80/math.sqrt(t))*math.sqrt(252):.2f}")
    sreq = solve_sr(905, 1038, 1 / 904, 0, 3) + ZB80 / math.sqrt(905)
    print(f"binding (c=1) true daily SR for 80% power: {sreq:.4f}; implied t-equivalent of bar: {solve_sr(905,1038,1/904,0,3)*math.sqrt(905):.2f}")
    for h in (5, 15, 30, 60):
        cells = [f"n={k}: mu={sreq*sig(h)/math.sqrt(k):.2f}" for k in (1, 2, 4, 8, 12) if k <= 290 // h]
        print(f"  h={h}: " + "; ".join(cells))
    print("trades_needed (alpha .05/3, power .8):")
    for h in (5, 15, 30, 60, 120, 240):
        cells = []
        for mu in (0.25, 0.5, 1.0, 1.5, 2.0):
            nn = ((PPF(1-0.05/3) + ZB80) * sig(h) / mu) ** 2
            cells.append(f"{mu}:{nn:,.0f}/{nn/905:.2f}")
        print(f"  h={h} cap={290//h}: " + " ".join(cells))

    print("\n== M5b section 0 / a.3 ==")
    for h in (5, 15, 60):
        er = sig(h) * math.sqrt(2 / math.pi)
        p = 0.5 + (0.5 + COST) / (2 * er)
        print(f"h={h}: E|r|={er:.3f} p for net 0.5 = {p:.4f} ({(p-0.5)*100:.1f} pts); 1pt = {0.02*er:.3f} ticks")
    p = 0.5 + 2.09 / (2 * sig(15) * math.sqrt(2 / math.pi))
    H = -p * math.log(p) - (1 - p) * math.log(1 - p)
    print(f"ln2 - H({p:.4f}) = {math.log(2) - H:.5f}")
    print(f"rows: {1055*816/15:.0f} all, {290*816/15:.0f} day; SE bound sqrt(.2/57392)={math.sqrt(0.2/57392):.5f}; x0.195x2 = {2*math.sqrt(0.2/57392)*0.195:.3f} ticks")
    print(f"memory 860880x64x4 = {860880*64*4/1e6:.1f} MB; 860880x100x4 = {860880*100*4/1e6:.0f} MB")

    print("\n== M5b b.3 binomials ==")
    for m, k in ((43, 29), (43, 26), (43, 33), (39, 26), (13, 9), (14, 10)):
        print(f"P(Bin({m},.5) >= {k}) = {binom_tail(m, k):.4f}  (k for 2/3 of {m}: {math.ceil(2*m/3)})")
    print(f"normal approx 43/29: z={(28.5-21.5)/math.sqrt(43*0.25):.3f} tail={1-PHI((28.5-21.5)/math.sqrt(43*0.25)):.4f}")
    d = 3.0 + ZB80
    print(f"delta={d:.3f}; Phi(d/sqrt13)={PHI(d/math.sqrt(13)):.4f}; terciles: Phi(d/sqrt3)={PHI(d/math.sqrt(3)):.4f} ^3={PHI(d/math.sqrt(3))**3:.3f}; "
          f"z>1.645: {PHI(d/math.sqrt(3)-PPF(0.95))**3:.3f}; z>1: {PHI(d/math.sqrt(3)-1)**3:.3f}")
    print(f"spike: 42 null months + fixed +6: P(t>3) = {1-PHI((3*math.sqrt(43)-6)/math.sqrt(42)):.4f}; with spike noise: {1-PHI((3*math.sqrt(43)-6)/math.sqrt(43)):.4f}")
    for T in (904, 905, 816):
        for phi in (0.05, 0.1, 0.2, 0.3):
            b = T ** (1/3) * (2 * phi / (1 - phi * phi)) ** (2/3)
            print(f"  b_SB T={T} phi={phi}: {b:.2f}", end="")
        print()
    for T in (816, 904, 905):
        print(f"NW auto lag T={T}: floor(4(T/100)^(2/9)) = {math.floor(4*(T/100)**(2/9))}")

    print("\n== M5b c.3 power table (D=1) ==")
    for h in (5, 15, 60):
        for mu in (0.25, 0.5, 1.0):
            n1 = ((PPF(1-0.05/3) + ZB80) * sig(h) / mu) ** 2
            n3 = ((3 + ZB80) * sig(h) / mu) ** 2
            print(f"h={h} mu={mu}: n(.05/3)={n1:,.0f} /905={n1/905:.2f} /904={n1/904:.2f} /816={n1/816:.2f} | n(t>3)={n3:,.0f} /905={n3/905:.2f} /904={n3/904:.2f} /816={n3/816:.2f}")
    print("MDE over 904 dates by trades/day:")
    for h in (5, 15, 60):
        for c, lab in ((PPF(1-0.05/3), ".05/3"), (3.0, "t>3")):
            cells = [f"{(c+ZB80)*sig(h)/math.sqrt(904*k):.3f}" for k in (1, 2, 5, 10, 20)]
            print(f"  h={h} {lab}: " + " ".join(cells))
    nw = 1 + 2 * sum((1 - j / 6) * 0.2 ** j for j in range(1, 6))
    print(f"NW 5 lags AR(1) .2: {nw:.4f}; true 1.5; t inflation sqrt = {math.sqrt(1.5/nw):.4f}")
    print(f"D same-day k=10 rho .05: {1+9*0.05:.2f}; rho .1: {1+9*0.1:.2f}")

    print("\n== M5b c.4 events (sigma_75) ==")
    for ne, kev in ((24, 1.0), (40, 1.0), (40, 1.5), (40, 2.0), (49, 1.0), (54, 1.0)):
        s = sig(75) * kev
        mde = [f"{(c+ZB80)*s/math.sqrt(ne):.2f}" for c in (PPF(0.95), PPF(1-0.05/3), 3.0)]
        pw = [f"{1-PHI(c-2*math.sqrt(ne)/s):.3f}" for c in (PPF(0.95), PPF(1-0.05/3), 3.0)]
        print(f"n={ne} k={kev} sigma={s:.2f}: MDE {' '.join(mde)} | power@2 {' / '.join(pw)}")

    print("\n== M5b d.3 Sharpe SE / MinTRL ==")
    sr = 1 / sig(15)
    v_iid = 1 + sr * sr / 2
    v_m = v_iid + 0.5 * sr + (8 - 3) / 4 * sr * sr
    v_m2 = v_iid + 1.0 * sr + (20 - 3) / 4 * sr * sr
    print(f"SR={sr:.5f} SR^2={sr*sr:.6f} naive={1/math.sqrt(5000):.6f} Lo={math.sqrt(v_iid/5000):.6f} "
          f"Mertens(-.5,8)={math.sqrt(v_m/5000):.6f} V={v_m:.6f} Mertens(-1,20)={math.sqrt(v_m2/5000):.6f} sqrt1.45={math.sqrt(1.45):.3f}")
    for lab, s, c in (("h15 mu1 c3", 1 / sig(15), 3.0), ("h15 mu1 c2.128", 1 / sig(15), PPF(1-0.05/3)),
                      ("h5 mu.5 c3", 0.5 / sig(5), 3.0), ("h60 mu1 c3", 1 / sig(60), 3.0)):
        vi = 1 + s * s / 2
        vm = vi + 0.5 * s + 1.25 * s * s
        mintrl = 1 + vi * (c / s) ** 2
        mintrl_m = 1 + vm * (c / s) ** 2
        n80 = ((c + ZB80) / s) ** 2
        print(f"{lab}: SR={s:.5f} MinTRL={mintrl:,.0f} ({mintrl_m:,.0f}) n80={n80:,.0f} ratio={n80/mintrl:.3f}")
    for c in (3.0, PPF(1-0.05/3), PPF(0.95)):
        print(f"((c+z80)/c)^2 at c={c:.3f}: {((c+ZB80)/c)**2:.3f}")
    print(f"ann SR 1 trade/day mu1 h15: {sr*math.sqrt(251):.2f}; MinTRL years {1345/251:.2f}; 904/251={904/251:.2f}; "
          f"delta@904={sr*math.sqrt(904):.3f} power@3={1-PHI(3-sr*math.sqrt(904)):.3f}")


if __name__ == "__main__":
    main()
