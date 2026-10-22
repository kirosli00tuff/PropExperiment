"""C2_OFI worked examples. Toy numbers only (no market data read)."""
import math

def cks_e(pb, qb, pa, qa, pb0, qb0, pa0, qa0):
    # Cont-Kukanov-Stoikov 2014 event contribution e_n
    return ((pb >= pb0) * qb - (pb <= pb0) * qb0 - (pa <= pa0) * qa + (pa >= pa0) * qa0)

print("== 1. OFI on four toy MES BBO updates (prices in index points)")
states = [(5000.00, 20, 5000.25, 15),   # start
          (5000.00, 25, 5000.25, 15),   # +5 bid added
          (5000.00, 25, 5000.25, 10),   # 5 removed from ask (trade or cancel)
          (5000.00, 25, 5000.50, 30),   # ask queue depleted, new ask level 30
          (5000.00, 18, 5000.50, 30)]   # 7 removed from bid
ofi = 0
for k in range(1, len(states)):
    e = cks_e(*states[k], *states[k-1]); ofi += e
    print(f"  event {k}: e = {e:+d}")
print(f"  OFI = {ofi}")
mid0 = (states[0][0] + states[0][2]) / 2; mid1 = (states[-1][0] + states[-1][2]) / 2
print(f"  mid change = {(mid1-mid0)/0.25:.2f} ticks")
for D in (20, 100, 630):
    print(f"  stylized dP = OFI/(2D), D={D}: {ofi/(2*D):.4f} ticks; OFI for 1 tick = {2*D}")

print("== 2. predictive R2 from contemporaneous R2 (dP_k = b*OFI_k + eps, OFI AR(1) rho)")
for R2c in (0.65,):
    for rho in (0.05, 0.1, 0.2):
        print(f"  R2c={R2c}, rho={rho}: predictive R2 = {R2c*rho**2:.5f}")

print("== 3. cost hurdles (rules/products.py: MES tick $1.25 RT 122c; ES tick $12.50 RT 378c)")
for name, tv, rt in (("MES", 1.25, 1.22), ("ES", 12.50, 3.78)):
    f = rt / tv
    print(f"  {name}: fees = {f:.4f} ticks/RT; taker RT (1-tick spread) = {1+f:.4f} ticks = ${tv*(1+f):.2f}; maker RT max gross 1 tick, net {1-f:.4f} ticks = ${tv*(1-f):.2f}")
sig = 1.0
for R2 in (0.01, 0.05, 0.20):
    em = math.sqrt(R2) * sig * math.sqrt(2/math.pi)
    print(f"  R2={R2}: E|forecast| with sd(dP)=1 tick = {em:.3f} ticks")

print("== 4. queue imbalance and logistic map (Gould-Bonart eq 7, logistic with x0, x1)")
for nb, na in ((40, 10), (10, 40), (25, 25)):
    I = (nb - na) / (nb + na)
    for x0, x1 in ((0.0, 2.0),):
        p = 1 / (1 + math.exp(-(x0 + I * x1)))
        print(f"  nb={nb}, na={na}: I={I:.3f}, p_up={p:.3f}")

print("== 5. XGBoost leaf weight (Chen-Guestrin eq 5,6) squared loss, h_i = 1")
g = [-0.5, -0.2, 0.1]; lam = 1.0; gam = 0.0
G = sum(g); H = len(g)
w = -G / (H + lam); score = -0.5 * G**2 / (H + lam) + gam
print(f"  G={G:.2f}, H={H}, lambda={lam}: w*={w:.4f}, leaf objective={score:.4f}")

print("== 6. integrated OFI (Cont-Cucuringu-Zhang eq 4), toy weights")
w1 = [0.4, 0.3, 0.2, 0.1]; ofiv = [1.0, 0.5, -0.2, 0.3]
val = sum(a*b for a, b in zip(w1, ofiv)) / sum(abs(a) for a in w1)
print(f"  ofi_I = {val:.3f}")

print("== 7. sample sizes: two-group mean difference in markouts (two-sided 5%, power 80%)")
za, zb = 1.959964, 0.841621
for sd, d in ((1.0, 0.10), (1.0, 0.20), (2.0, 0.20), (3.0, 0.25)):
    n = 2 * (za + zb)**2 * sd**2 / d**2
    print(f"  sd={sd} ticks, delta={d} ticks: n per group = {math.ceil(n)}")
print("  AUC test: n for AUC=0.55 vs 0.5 (Hanley-McNeil approx, equal classes)")
for A in (0.52, 0.55, 0.60):
    Q1 = A/(2-A); Q2 = 2*A*A/(1+A)
    var1 = (A*(1-A) + 0*(Q1-A*A) + 0*(Q2-A*A))  # placeholder not used
    # Hanley-McNeil variance with nA=nN=n: V = [A(1-A) + (n-1)(Q1-A^2) + (n-1)(Q2-A^2)]/n^2
    for n in (500, 2000, 10000):
        V = (A*(1-A) + (n-1)*(Q1-A*A) + (n-1)*(Q2-A*A)) / n**2
        z = (A-0.5)/math.sqrt(V)
        if n == 2000 or A == 0.52:
            print(f"   AUC={A}, n per class={n}: z = {z:.2f}")

print("== 8. data and memory, ES BBO event rate 45/s (Takahashi 2025 Table 1, 2008-2013)")
ev_day_rth = 45 * 6.5 * 3600; days = 84
print(f"  RTH events/day = {ev_day_rth:,.0f}; 84 days = {ev_day_rth*days:,.0f}")
for nfeat in (10, 20, 40):
    gb = ev_day_rth * days * nfeat * 4 / 1e9
    print(f"  {nfeat} float32 features per event: {gb:.1f} GB")
print("  10-second bars: per RTH day", 6.5*360, "; 84 days =", int(6.5*360*84))

print("== 9. cloud cost (RunPod RTX 4090 $0.89/h; A100 PCIe 80GB $1.79/h; Lambda H100 PCIe $3.29/h)")
for hrs in (10, 50, 200):
    print(f"  {hrs} GPU-h: 4090 ${0.89*hrs:.0f}; A100 ${1.79*hrs:.0f}; H100 ${3.29*hrs:.0f}")

print("== 10. slow maker break-even toxic share (BCS eq 6.4 logic, sniper wins w.p. 1)")
for name, fee_side in (("MES", 0.976/2), ("ES", 0.3024/2)):
    for J in (1.0, 2.0):
        s2 = 0.5  # half spread, 1-tick spread
        # net per fill = (1-pi)*s2 - pi*(J - s2) - fee_side = 0  -> pi = (s2 - fee_side)/J
        pi = (s2 - fee_side) / J
        print(f"  {name}: J={J} tick jump, fee/side={fee_side:.3f}: break-even toxic share = {pi:.3%}")
