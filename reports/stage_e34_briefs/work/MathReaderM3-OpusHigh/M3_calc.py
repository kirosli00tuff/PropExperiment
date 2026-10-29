"""E.34 M3 (ZL labels and holding band): closed-form and synthetic arithmetic only.

Inputs are the shared standard numbers of BRIEFS.md (sigma_h of ZL from E.32b F3, Topstep fee, grid rules of the
E.32 protocol). No market data is read; the simulation is a stylised Brownian mid (seeded), as in E.32 M6.
Run: nice -n 10 python3 -I M3_calc.py > M3_calc.out
"""
import math
import os

import numpy as np

os.nice(10)

SIG = {1: 5.52, 5: 12.05, 15: 20.37, 30: 28.10, 60: 38.21}  # ZL day-session sigma_h, ticks (E.32b F3)
FEE = 5.28 / 6.00  # Topstep RT fee in ZL ticks
CF = 2.38  # E.32b c_f (S 1.0 u + 0.5 slippage + fee)
E80_TEST = {15: 0.90, 30: 1.81, 60: 3.70}
SR80_TEST = 0.1936
B = (15, 30, 60)
L_S = 1.0
GRID_LAST = 277  # 08:35 + 277 min = 13:12 CT


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def hhmm(minutes_after_0835, offset_h=0):
    m = 8 * 60 + 35 + minutes_after_0835 - offset_h * 60
    return f"{m // 60:02d}:{m % 60:02d}"


def p_no_hit(k):
    """P(driftless BM with unit variance per unit time stays inside +-k*sqrt(T) up to T)."""
    s = 0.0
    for n in range(200):
        s += (-1) ** n / (2 * n + 1) * math.exp(-((2 * n + 1) ** 2) * math.pi ** 2 / (8 * k * k))
    return 4 / math.pi * s


def section_grid():
    print("== 1. Grid, latest entries, trades a day (P0.3 grid, P3.8 re-entry rule)")
    for h in B:
        n_starts = GRID_LAST - h + 1
        last = GRID_LAST - h
        # P3.8: FH exit fill at t + h + L; the next decision is the first grid minute at or after it: t + h + 1
        n_max_p38 = (last) // (h + 1) + 1
        n_max_reentry_same_minute = last // h + 1
        n_cap_e32b = min(20, 290 // h)
        e80_p38 = SR80_TEST * SIG[h] / math.sqrt(n_max_p38)
        print(f"h={h}: starts {n_starts}; latest start {hhmm(last)} CT = {hhmm(last, 2)} PT; "
              f"max FH trades/day P3.8 {n_max_p38}, if re-entry at the exit minute {n_max_reentry_same_minute}, "
              f"E.32b n_cap {n_cap_e32b}; e80_test at P3.8 max {e80_p38:.3f} (E.32b {E80_TEST[h]})")


def section_deadzone():
    print("== 2. Dead zone and break-even hit rates (normal, magnitudes independent of sign)")
    for label, c in (("s=1 + fee", 1.0 + FEE), ("c_f E.32b", CF), ("s=2.06 (u) + fee", 2.06 + FEE)):
        for h in B:
            sg = SIG[h]
            dz = 2 * phi(c / sg) - 1
            q = 0.5 + c / (2 * 0.79788 * sg)
            print(f"{label:18s} h={h}: threshold |dM| > {c:.3f} = {c / sg:.4f} sigma; P(dead zone) {dz:.4f}; "
                  f"q* {q:.4f}")


def section_tb(rng):
    print("== 3. Triple barrier b = kappa sigma_1 sqrt(h), kappa 1")
    for h in B:
        b = SIG[1] * math.sqrt(h)
        ratio = b / SIG[h]
        pv_bm1 = p_no_hit(1.0)
        pv_eff = p_no_hit(ratio)
        pstar_mid = 0.5 + (1.0 + FEE) / (2 * b)
        print(f"h={h}: b {b:.2f} ticks ({b * 6:.0f} USD); b/sigma_h {ratio:.3f}; P(vertical) BM at sigma_1 "
              f"{pv_bm1:.4f}, BM at sigma_h/sqrt(h) {pv_eff:.4f}; p* barrier exits (mid barriers, cost s+f=1.88) "
              f"{pstar_mid:.4f}")
    # expected exit time E[min(tau, h)]/h for a driftless BM, barrier ratio k (simulated, 1 s grid relative)
    n, steps = 40_000, 3600
    for k in (1.0, 1.05, 1.076, 1.119):
        dt = 1.0 / steps
        x = np.zeros(n)
        alive = np.ones(n, bool)
        t_exit = np.ones(n)
        for i in range(1, steps + 1):
            x[alive] += rng.standard_normal(alive.sum()) * math.sqrt(dt)
            hit = alive & (np.abs(x) >= k)
            t_exit[hit] = i * dt
            alive &= ~hit
        print(f"k={k}: E[min(tau,h)]/h {t_exit.mean():.4f}; P(vertical) sim {alive.mean():.4f} (series "
              f"{p_no_hit(k):.4f}, discrete grid biases it up)")


def section_weights():
    print("== 4. Rows and n_eff per date (P3.7 uniqueness; release window [10:58, 11:30])")
    for h in B:
        rows = GRID_LAST - h + 1
        neff = (GRID_LAST) / h  # covered minutes 08:35-13:12 (+1 s) / h
        excl = h + 33  # t in [10:58 - h, 11:30]
        block1 = 143  # 08:35-10:58
        block2 = 101  # 11:31-13:12
        neff_rel = (block1 + block2) / h
        print(f"h={h}: rows {rows}, n_eff {neff:.2f}; over 796 dates rows {rows * 796:,}, n_eff "
              f"{neff * 796:,.0f}; release day rows {rows - excl} (excluded {excl}), n_eff {neff_rel:.2f}")


def section_latency():
    print("== 5. Latency drift SD (BM)")
    for L in (0.3, 1.0):
        print(f"L={L}s: sd {SIG[1] * math.sqrt(L / 60):.3f} ticks")


def section_tt(rng):
    print("== 6. Trade-through limit entry vs market (stylised BM, sigma_1 5.52, W = 60 s, 1 s grid)")
    n = 400_000
    w = 60
    for s in (1.0, 2.0):
        for h in B:
            for alpha in (0.0, CF, CF + 1.0, CF + E80_TEST[h]):
                mu_s = alpha / (h * 60)  # drift per second
                sd_s = SIG[1] / math.sqrt(60)
                inc = rng.standard_normal((n, w)) * sd_s + mu_s
                path = np.cumsum(inc, axis=1)
                fill = (path <= -s).any(axis=1)  # buy limit at bid (-s/2) fills when mid reaches -s (B6-TT)
                x_w = path[:, -1]
                rest = (h * 60 - w)
                x_h = x_w + rng.standard_normal(n) * sd_s * math.sqrt(rest) + mu_s * rest
                p = fill.mean()
                v_m = (x_h - s - FEE).mean()
                v_l = np.where(fill, x_h - FEE, 0.0).mean()
                v_lc = np.where(fill, x_h - FEE, x_h - x_w - s - FEE).mean()
                g_f = x_h[fill].mean()
                g_nf = x_h[~fill].mean()
                oc = (1 - p) * (g_nf - s - FEE)
                print(f"s={s} h={h} alpha={alpha:.2f}: p_fill {p:.4f}; E[G|fill] {g_f:.3f}; E[G|no fill] {g_nf:.3f}; "
                      f"V_M {v_m:.3f}; V_L {v_l:.3f}; V_LC {v_lc:.3f}; OC {oc:.3f}; p*s {p * s:.3f}")


if __name__ == "__main__":
    rng = np.random.default_rng(20261029)
    section_grid()
    section_deadzone()
    section_tb(rng)
    section_weights()
    section_latency()
    section_tt(rng)
