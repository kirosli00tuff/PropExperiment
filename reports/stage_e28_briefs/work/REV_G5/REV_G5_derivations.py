#!/usr/bin/env python3
"""REV_G5 independent re-derivations for C2_DeepLOB.md and C2_OFI.md.
Every number printed is recomputed from the inputs stated in the reviewed
text; the label after each line says which file:line it checks.
Run: uv run python reports/stage_e28_briefs/work/REV_G5/REV_G5_derivations.py
"""
import math

import numpy as np
import sympy as sp
from scipy.stats import norm

print("=== C2_DeepLOB.md ===")
# 0. cost yardstick (lines 29-37)
fee_rt = 1.22 / 1.25
print(f"[D:31] fee RT ticks = {fee_rt:.4f}; tick bp @4700 = {0.25/4700*1e4:.3f}; @5000 = {0.25/5000*1e4:.3f}; "
      f"taker RT = {1+fee_rt:.3f}")
# 1.2 parameter count (lines 116-121)
conv = lambda h, w, cin, cout: (h * w * cin + 1) * cout
b1 = conv(1, 2, 1, 16) + 2 * conv(4, 1, 16, 16)
b2 = conv(1, 2, 16, 16) + 2 * conv(4, 1, 16, 16)
b3 = conv(1, 10, 16, 16) + 2 * conv(4, 1, 16, 16)
inc = conv(1, 1, 16, 32) + conv(3, 1, 32, 32) + conv(1, 1, 16, 32) + conv(5, 1, 32, 32) + conv(1, 1, 16, 32)
H, d = 64, 96
lstm_keras = 4 * (H * (d + H) + H)
dense = 64 * 3 + 3
tot = b1 + b2 + b3 + inc + lstm_keras + dense
print(f"[D:118-121] blocks {b1},{b2},{b3} inception {inc} lstm {lstm_keras} dense {dense} total {tot}; "
      f"pytorch(+4H) {tot + 4*H}; lstm share {lstm_keras/tot:.3f}")
# 1.5 label worked example (lines 151-161)
past = np.array([4700.000, 4700.125, 4700.125, 4700.250, 4700.250, 4700.375])
fut = np.array([4700.375, 4700.500, 4700.625, 4700.625, 4700.750])
m_minus = past.mean()           # 1/(k+1), i=0..k  (k=5, six terms)
m_plus = fut.mean()
pt = past[-1]
l3 = (m_plus - pt) / pt
l4 = (m_plus - m_minus) / m_minus
print(f"[D:155-157] sum past {past.sum():.3f} m- {m_minus:.4f} m+ {m_plus:.4f} l3 {l3:.4e} ({l3*1e4:.3f} bp) "
      f"l4 {l4:.4e} ({l4*1e4:.3f} bp); m+-pt {m_plus-pt:.3f} pts = {(m_plus-pt)/0.25:.2f} ticks")
m_minus_5 = past[1:].mean()
print(f"[D:script .out] reader script 'm- (i=0..k-1)' = {m_minus_5:.4f} -> l4 {(m_plus-m_minus_5)/m_minus_5*1e4:.3f} bp "
      f"(differs from text 0.82 bp; text follows its stated 1/(k+1) definition)")
for a in (0.25e-4, 1e-4, 2e-3):
    lab = lambda l: 1 if l > a else (-1 if l < -a else 0)
    print(f"   alpha {a:.2e}: eq3 {lab(l3)} eq4 {lab(l4)}")
# 1.3 scale (line 134-135)
print(f"[D:134] 80 / (250*5) stock-days = 1/{250*5/80:.1f}; 100 events x 0.192 s = {100*0.192:.1f} s; k=20 -> {20*0.192:.2f} s")
# 1.7 sample size (lines 193-195)
za, zb = 3.0, norm.ppf(0.80)
n = lambda sd, dl: 2 * (za + zb) ** 2 * sd**2 / dl**2
print(f"[D:194-195] z_beta={zb:.4f}; n(sd=2,d=0.5)={n(2,0.5):.1f} -> ceil {math.ceil(n(2,0.5))}; total x3 = {3*math.ceil(n(2,0.5))}; "
      f"n(sd=2,d=0.25)={math.ceil(n(2,0.25))}; with z_beta=0.84 exactly: {2*(3.84)**2*4/0.25:.1f}")
# 2.2 FI-2010 threshold (line 241)
print(f"[D:241] 0.002*4700 = {0.002*4700:.2f} pts = {0.002*4700/0.25:.1f} ticks; @5000 {0.002*5000/0.25:.1f} ticks")
# 3.1 receptive field (line 304)
print(f"[D:304] receptive field kernel 2, dilations 1..16 = 1 + {sum([1,2,4,8,16])} = {1+sum([1,2,4,8,16])}")
# 3.2 thresholds in ticks (lines 352-353)
tick_bp = 0.25 / 4700 * 1e4
print(f"[D:352-353] 0.10 bp = {0.10/tick_bp:.3f} ticks; 3.05 bp = {3.05/tick_bp:.3f}; 0.40 bp = {0.40/tick_bp:.3f}; 270/96 = {270/96:.2f}")
# 3.3 mutual information (lines 395-397)
p = np.array([[0.4, 0.1], [0.1, 0.4]])
px, py = p.sum(1), p.sum(0)
mi = sum(p[i, j] * math.log(p[i, j] / (px[i] * py[j])) for i in range(2) for j in range(2))
print(f"[D:396-397] MI = {mi:.4f} nats; terms 0.8*ln1.6={0.8*math.log(1.6):.4f}, 0.2*ln0.4={0.2*math.log(0.4):.4f}")
# 3.4 Adam bytes (line 448)
print(f"[D:448] 1e7 params x 16 B = {1e7*16/1e9:.2f} GB")
# 3.5 MBO F1 differences (lines 484-486)
print(f"[D:485-486] 68.40-61.75={68.40-61.75:.2f}; 69.02-68.40={69.02-68.40:.2f}; 61.82-61.10={61.82-61.10:.2f}; 61.10-54.79={61.10-54.79:.2f}")
# 4.1 LOBCAST scores (lines 518-521)
print(f"[D:518-521] robustness: 100-87.6={100-87.6:.1f}; |A|={78.9-71.4:.1f} -> S={100-87.6-(78.9-71.4):.1f}; "
      f"gen 2021: |A|={78.9-59.5:.1f}, 100-73.7={100-73.7:.1f} -> S={100-73.7-(78.9-59.5):.1f}")
# 4.3 pT example (line 597) and compute (line 607)
print(f"[D:597] pT = 10/(100+100-10) = {10/190:.4f}; [D:607] 959h16m27s/135 = {(959+16/60+27/3600)/135:.2f} GPU-h")
# 5.1 Eurodollar (lines 693-695)
print(f"[D:693-695] 12*0.005 = {12*0.005:.3f} bp; /0.5 = {12*0.005/0.5:.2%}")
# 5.2 Dixon toy (lines 724-729)
good, bad = 1 - fee_rt, -1 - fee_rt
blind = 0.8 * good + 0.2 * bad
filt = 0.8 * 0.9 * good + 0.2 * 0.25 * bad
print(f"[D:725-729] good {good:.3f} bad {bad:.3f}; blind {blind:.3f}; filtered {filt:.3f} (weights 0.72 / 0.05)")
# 6.3 break-even hit rate (lines 808-816), symbolic
h, g, l, c = sp.symbols("h g l c", positive=True)
hstar = sp.solve(sp.Eq(h * g - (1 - h) * l - c, 0), h)[0]
print(f"[D:809] h* = {sp.simplify(hstar)}")
for cc in (fee_rt, 1 + fee_rt):
    print("   c=%.3f: " % cc + ", ".join(f"g=l={x}: {float(hstar.subs({g: x, l: x, c: cc})):.3f}" for x in (1, 2, 4)))
ev = lambda pu, ps, pd, m: pu * m - pd * m
print(f"[D:812-814] 1.5-tick: gross {ev(.6,.25,.15,1.5):.3f} net {ev(.6,.25,.15,1.5)-fee_rt:.3f}; "
      f"3-tick: gross {ev(.6,.25,.15,3):.3f} net {ev(.6,.25,.15,3)-fee_rt:.3f} net-1tick {ev(.6,.25,.15,3)-fee_rt-1:.3f}")
# 9 latency ratios (lines 864-865)
print(f"[D:864-865] 10-100 ms vs 200 us: {10e-3/200e-6:.0f}-{100e-3/200e-6:.0f}x; vs 0.1-1 ms: {10e-3/1e-3:.0f}-{100e-3/0.1e-3:.0f}x; "
      f"vs 2 us: {10e-3/2e-6:.0f}-{100e-3/2e-6:.0f}x")
# 10.2 training time (lines 904-908)
for name, thr in (("paper", 5247), ("pytorch32", 2092), ("translob", 7725)):
    for spd in (50_000, 200_000):
        s = spd * 80
        print(f"[D:906-908] {name} {s/1e6:.0f}M/epoch: {s/thr/3600:.2f} h/epoch, 40 ep {40*s/thr/3600:.1f} h")
print(f"[D:912] 200k x 40 x 4 B = {200e3*40*4/1e6:.0f} MB; x80 = {200e3*40*4*80/1e9:.2f} GB")
# 10.3 cloud costs (lines 924-925, 931-932)
for hrs in (18, 100, 500, 1000):
    print(f"[D:924,932] {hrs} GPU-h: 4090 ${hrs*0.89:.0f}, A100 ${hrs*1.79:.0f}, Lambda A100 ${hrs*1.99:.0f}; 1000 h = {1000/24/7:.1f} weeks")
print(f"[D:958] 3*3*2*5 = {3*3*2*5}")

print("\n=== C2_OFI.md ===")
# 0.1 cost hurdle table (lines 34-37)
for nm, tick, rt in (("MES", 1.25, 1.22), ("ES", 12.50, 3.78)):
    f = rt / tick
    print(f"[O:36-37] {nm}: fee {f:.4f} ticks; taker {1+f:.4f} ticks = ${(1+f)*tick:.2f}; maker {1-f:.4f} ticks = ${(1-f)*tick:.2f}; f/2 {f/2:.3f}")
# 1.5 OFI toy (lines 133-147), CKS e_n with indicator definition
def e_n(pb0, qb0, pa0, qa0, pb1, qb1, pa1, qa1):
    return ((pb1 >= pb0) * qb1 - (pb1 <= pb0) * qb0 - (pa1 <= pa0) * qa1 + (pa1 >= pa0) * qa0)
states = [(5000.00, 20, 5000.25, 15), (5000.00, 25, 5000.25, 15), (5000.00, 25, 5000.25, 10),
          (5000.00, 25, 5000.50, 30), (5000.00, 18, 5000.50, 30)]
es = [e_n(*states[i], *states[i + 1]) for i in range(4)]
mid0 = (states[0][0] + states[0][2]) / 2
mid1 = (states[-1][0] + states[-1][2]) / 2
print(f"[O:137-142] e_n = {es}; OFI = {sum(es)}; mid {mid0} -> {mid1} = {(mid1-mid0)/0.25:.2f} ticks; "
      f"OFI/(2D): D=20 {sum(es)/40:.3f}, D=100 {sum(es)/200:.3f}; 2*630 = {2*630}")
# 1.8 memory (lines 186-187)
ev_day = 45 * 6.5 * 3600
print(f"[O:186-187] events/day {ev_day:,.0f}; 84 days {84*ev_day/1e6:.1f} M; x10 f32 {84*ev_day*40/1e9:.2f} GB; x20 {84*ev_day*80/1e9:.2f} GB")
# 2.3 windows (line 239)
print(f"[O:239] 84*13 = {84*13}; XGH 252*11 = {252*11} per stock; x6 stocks = {6*2772}; ratios {84*13/2772:.2f} (per stock) {84*13/(6*2772):.3f} (all)")
# 2.5 MLOFI toy (lines 249-252)
print(f"[O:250-252] MLOFI2 = 30 - (-10) = {30-(-10)}; fit 0.02*13 + 0.005*40 = {0.02*13+0.005*40:.2f}")
# 3.5 integrated OFI toy (line 336)
w = np.array([0.4, 0.3, 0.2, 0.1]); x = np.array([1.0, 0.5, -0.2, 0.3])
print(f"[O:336] ofi_I = {w @ x / np.abs(w).sum():.3f}")
# 3.2 PCA derivation check (lines 318-321): top eigenvector maximizes variance
S = np.array([[4, 2, 1], [2, 3, 1], [1, 1, 2]], float)
vals, vecs = np.linalg.eigh(S)
rng = np.random.default_rng(0); best = max(float(v @ S @ v) for v in (lambda z: z / np.linalg.norm(z, axis=1, keepdims=True))(rng.normal(size=(20000, 3))))
print(f"[O:318-321] top eigenvalue {vals[-1]:.4f} vs max over 20000 random unit vectors {best:.4f}")
# 4.3 rolling weeks (line 432)
print(f"[O:432] 17 - 5 = {17-5} test weeks; 52 - 5 = {52-5}")
# 4.5 forecast scale (lines 443-446)
print(f"[O:443-446] sqrt(0.02) = {math.sqrt(0.02):.4f}; x sqrt(2/pi) = {math.sqrt(0.02)*math.sqrt(2/math.pi):.4f}; 1.976/0.1414 = {1.976/math.sqrt(0.02):.1f} sd")
# 4.7 n for t=3 (line 471-472)
print(f"[O:471-472] n = 9/0.01 = {9/0.01:.0f}; 9/0.001 = {9/0.001:.0f}; exact t for rho=0.1,n=900: {0.1*math.sqrt(898)/math.sqrt(1-0.01):.3f}")
# 4.8 cloud (line 488)
print(f"[O:488] 50 h: 4090 ${50*0.89:.1f}, A100 ${50*1.79:.1f}, H100 ${50*3.29:.1f}")
# 5.1 queue imbalance (line 542) and Hanley-McNeil (line 558)
I = (40 - 10) / 50
print(f"[O:542] I = {I:.1f}; P(up) = {1/(1+math.exp(-2*I)):.3f}; reversed {1/(1+math.exp(2*I)):.3f}; (1+I)/2 = {(1+I)/2:.2f} = nb/(nb+na) = {40/50:.2f}")
def hm_z(A, n1, n2):
    Q1, Q2 = A / (2 - A), 2 * A**2 / (1 + A)
    se = math.sqrt((A * (1 - A) + (n1 - 1) * (Q1 - A**2) + (n2 - 1) * (Q2 - A**2)) / (n1 * n2))
    return (A - 0.5) / se
print(f"[O:558] HM z: AUC 0.55 n=2000/class {hm_z(0.55,2000,2000):.2f}; AUC 0.52 {hm_z(0.52,2000,2000):.2f}")
# 1.7 sample sizes (lines 173-176), two-sided 5%, power 80%
n2 = lambda sd, dl: 2 * (norm.ppf(0.975) + norm.ppf(0.8)) ** 2 * sd**2 / dl**2
print(f"[O:174-176] n(sd=1,d=0.2) = {n2(1,0.2):.1f} -> {math.ceil(n2(1,0.2))}; x3 = {3*math.ceil(n2(1,0.2))}; n(sd=1,d=0.1) = {math.ceil(n2(1,0.1))}")
# 6.3 XGBoost leaf (lines 622-626)
G, Hh, lam = -0.6, 3, 1.0
print(f"[O:623-625] w* = {-G/(Hh+lam):.3f}; obj = {-0.5*G**2/(Hh+lam):.4f}; lambda=0: {-G/Hh:.3f}")
# 6.8 memory (line 675)
print(f"[O:675] 84*23*3600 = {84*23*3600:,} rows; x40 f32 = {84*23*3600*40*4/1e9:.2f} GB")
# 7.2 symbolic derivation R2_pred = rho^2 R2_c (lines 700-710)
beta, rho, vO, s2 = sp.symbols("beta rho V_OFI sigma2", positive=True)
vP = beta**2 * vO + s2
R2c = beta**2 * vO / vP
cov = beta * rho * vO
R2p = cov**2 / (vO * vP)
print(f"[O:707] R2_pred / (rho^2 R2_c) simplifies to: {sp.simplify(R2p / (rho**2 * R2c))}")
print(f"[O:710] 0.65*rho^2: rho=0.1 {0.65*0.01:.4f}, 0.05 {0.65*0.0025:.4f}, 0.2 {0.65*0.04:.3f}")
# 7.4 forecast magnitude (lines 729-731)
for r2 in (0.01, 0.05, 0.20):
    print(f"[O:729] R2={r2}: E|f| = {math.sqrt(r2)*math.sqrt(2/math.pi):.3f} ticks; /1.976 = {math.sqrt(r2)*math.sqrt(2/math.pi)/1.976:.3f}")
# 8.3 triple barrier (lines 796-804)
fM = 1.22 / 1.25
print(f"[O:796-804] ceil(1+f)= {math.ceil(1+fM)} ticks; net up {2-fM:.3f} = ${(2-fM)*1.25:.2f}; net down {-(4+fM):.3f} = ${-(4+fM)*1.25:.2f}; "
      f"p* = {(4+fM)/((2-fM)+(4+fM)):.4f}; symmetric 2: {(2+fM)/((2-fM)+(2+fM)):.4f}")
# 10.1 sniping break-even (lines 924-933), symbolic
pi_, J, f = sp.symbols("pi J f", positive=True)
net = (1 - pi_) * sp.Rational(1, 2) - pi_ * (J - sp.Rational(1, 2)) - f / 2
print(f"[O:927] net per fill simplifies to {sp.simplify(net)}; break-even pi = {sp.solve(sp.Eq(net, 0), pi_)[0]}")
for nm, fr in (("MES", 0.976), ("ES", 0.3024)):
    print(f"   {nm}: f/2 {fr/2:.3f}; J=1 {(0.5-fr/2)/1:.3%}; J=2 {(0.5-fr/2)/2:.3%}; 1/pi = {1/((0.5-fr/2)):.0f}")
# 9.1 SW ratio (line 853), 10.4 SE (line 993), 13.1 sums (line 1079)
print(f"[O:853] 0.26/0.32 = {0.26/0.32:.2%}; [O:993] SE = {math.sqrt(0.05*0.95/400):.4f}; [O:1079] fixed {1+1+1+1+1}, all horizons {1+3+3+3+1}")
