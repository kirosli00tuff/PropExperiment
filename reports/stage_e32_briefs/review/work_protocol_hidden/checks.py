"""DofReviewer checks on the protocol text (no market data). Prints results only."""
import math, re, statistics, sys
from datetime import date, timedelta
from statistics import NormalDist
sys.path.insert(0, ".")
from funnel.multiple_comparisons import deflated_sharpe_ratio, expected_max_sharpe
from screening import trial_registry as tr
import numpy as np
Z = NormalDist()

print("== 1. registry ID regex vs P7.1 ids")
ids = ["E33-S1-FH05-L-C0.01-r0", "E33-S5-TB30-G-d3-m200", "E33-S1FH05LC001r0"]
for i in ids:
    print(f"  {i!r:32} fullmatch _ID: {bool(tr._ID.fullmatch(i))}")
print("  _TEST 'E33':", bool(tr._TEST.fullmatch("E33")), "current_n:", tr.current_n())

print("== 2. P4.2 binomials")
def binom_tail(n, p, k):  # P(X >= k)
    return sum(math.comb(n, j) * p**j * (1-p)**(n-j) for j in range(k, n+1))
print(f"  P(>=2 of 20 | 0.05) = {binom_tail(20, 0.05, 2):.3f}  (protocol 0.26)")
print(f"  P(>=14 of 20 | 0.80) = {binom_tail(20, 0.80, 14):.3f}  (protocol 0.91)")
print(f"  300 x P(Z > 4.86) = {300*(1-Z.cdf(4.86)):.2e}  (protocol ~2e-4)")
print(f"  P(Tier A non-empty | null, 20 seeds, true 0.05): P(0 of 20)={0.95**20:.3f}")

print("== 3. sample vs population SD on SR_d at T=796 near the tie tolerance 1e-4")
T = 796
for sr in (0.17, 0.20, 0.25):
    print(f"  SR_pop {sr:.4f} -> SR_sample {sr*math.sqrt((T-1)/T):.6f}  diff {sr - sr*math.sqrt((T-1)/T):.2e}")

print("== 4. decision grid counts 08:35..13:12-h")
for h in (5, 15, 30, 60):
    start = 8*60+35; end = 13*60+12-h
    print(f"  h={h}: {end-start+1} (protocol {dict(zip((5,15,30,60),(273,263,248,218)))[h]})")

print("== 5. folds and quarters")
print("  133*4+132*2 =", 133*4+132*2)
print("  months 2020-12..2024-02 =", (2024-2020)*12 + (2-12) + 1, "; quarters Dec-Feb.. =", 39/3)

print("== 6. thresholds via program functions (N 838)")
def req(n, t, v, sk=0.0, ku=3.0, target=0.95):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo+hi)/2
        if deflated_sharpe_ratio(mid, t, n, v, sk, ku)["deflated_sharpe_ratio"] >= target: hi = mid
        else: lo = mid
    return hi
def se(sr, t, sk=0.0, ku=3.0): return math.sqrt((1 - sk*sr + (ku-1)/4*sr*sr)/(t-1))
def g4(b, t):
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid=(lo+hi)/2
        if mid - se(mid, t) >= b: hi = mid
        else: lo = mid
    return hi
N, Td, Tt = 838, 796, 870
g3 = req(N, Td, 1/(Td-1)); dsr_t = req(N, Tt, 1/(Tt-1)); tbar = 3/math.sqrt(Tt)
print(f"  SR0 {expected_max_sharpe(N, 1/(Td-1)):.4f}  G3 {g3:.4f} (t {g3*math.sqrt(Td):.2f})  G3 fat {req(N,Td,1/(Td-1),-0.5,6):.4f}")
print(f"  test: t>3 {tbar:.4f}; DSR_test {dsr_t:.4f}; b_test {max(tbar,dsr_t):.4f}; G4 {g4(max(tbar,dsr_t),Td):.4f}; G4 if dropped {g4(tbar,Td):.4f}")
print(f"  G3 at N 839..1138 (if another stage registers first): N 900 {req(900,Td,1/(Td-1)):.4f}, N 1138 {req(1138,Td,1/(Td-1)):.4f}")
print(f"  G3 if T_disc were 764 (E.31's kept dates): {req(N,764,1/763):.4f}")
# G3 with the configuration's own moments: how much skew/kurtosis moves the bar
for sk, ku in ((-1.0, 8.0), (0.5, 4.0), (-2.0, 15.0)):
    print(f"  G3 at skew {sk} kurt {ku}: {req(N,Td,1/(Td-1),sk,ku):.4f}")

print("== 7. program DSR variance under near-duplicate Tier B (test window, T 870, N 838)")
rng = np.random.default_rng(20261027)
def sim(rho_b, true_sr=0.0, reps=4000):
    # Tier A true SR true_sr; Tier B1, B2 daily returns correlated rho_b with A; all null unless true_sr
    ems, dsr_pass = [], 0
    for _ in range(reps):
        a = rng.standard_normal(Tt) + true_sr
        b1 = rho_b*a + math.sqrt(1-rho_b**2)*rng.standard_normal(Tt)
        b2 = rho_b*a + math.sqrt(1-rho_b**2)*rng.standard_normal(Tt)
        srs = [x.mean()/x.std() for x in (a, b1, b2)]
        v = statistics.pvariance(srs)
        em = expected_max_sharpe(N, v); ems.append(em)
        d = deflated_sharpe_ratio(srs[0], Tt, N, v)["deflated_sharpe_ratio"]
        dsr_pass += d > 0.95
    return float(np.median(ems)), dsr_pass/reps
for rho in (0.0, 0.7, 0.9, 0.98):
    em0, p0 = sim(rho, 0.0); em1, p1 = sim(rho, 0.12)
    print(f"  rho(A,B)={rho:.2f}: median E[maxSR] null {em0:.4f}; P(DSR>0.95 | null) {p0:.3f}; P(DSR>0.95 | true SR 0.12, below b_test 0.1649) {p1:.3f}")
print(f"  reference: protocol-added V=1/(T-1): E[maxSR] {expected_max_sharpe(N, 1/(Tt-1)):.4f}")

print("== 8. LGBM min_data_in_leaf vs rows per fold")
rows_fold = 263*796*5/6
for h in (5, 15, 30, 60):
    print(f"  h={h}: 50h={50*h}, 200h={200*h}; ~rows/fold at 263/date {rows_fold:.0f}; share {200*h/rows_fold:.3%}")

print("== 9. entry cap 20 vs grid")
for h in (5, 15, 30, 60):
    g = {5:273,15:263,30:248,60:218}[h]
    print(f"  h={h}: max back-to-back FH trades/date = {math.ceil(g/(h+1))} (grid {g}); cap 20 binds: {math.ceil(g/(h+1))>20}")
