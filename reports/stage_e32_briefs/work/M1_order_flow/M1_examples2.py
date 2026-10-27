"""M1_order_flow worked examples, v2 (re-spawn run, Stage E.32). No data read.
Inputs: E.28 standard ZM numbers (A0 Table 1), E.28 ranking row 130 (mu*_mkt = 1.59 ticks), and stated assumptions.
Supersedes M1_examples.py, whose CRS R2 inputs were not traceable to the CRS table (corrected here from Table 5)."""
import math
from statistics import NormalDist
N = NormalDist()
s1, BE, ADV, DAYSHARE = 3.15, 1.59, 36690, 0.83
k = math.sqrt(2 / math.pi)
z95 = N.inv_cdf(0.95); tdec = N.pdf(z95) / 0.05     # E[|Z| | |Z|>z_0.95] (two-sided top decile of |Z|)
print(f"sqrt(2/pi)={k:.4f} z95={z95:.4f} pdf={N.pdf(z95):.5f} top-decile factor={tdec:.4f}")
print("== A1 sigma_h (random walk) and R2 needed")
for h in (1, 5, 15, 30):
    sh = s1 * math.sqrt(h)
    print(f"h={h:>2} sigma_h={sh:6.3f} R2_all={(BE/(sh*k))**2:.5f} R2_topdec={(BE/(sh*tdec))**2:.5f}")
print("== A2 CRS Table 5 OIB# R2 (percent -> fraction) mapped to ZM")
for lab, r2pct, h in (("1996 5m", 3.32, 5), ("1996 30m", 0.53, 30), ("2002 5m", 0.54, 5), ("2002 30m", 0.18, 30)):
    sh = s1 * math.sqrt(h); sf = math.sqrt(r2pct/100) * sh
    print(f"{lab}: R2={r2pct/100:.4f} sigma_f={sf:.3f} mean|f|={sf*k:.3f} topdec|f|={sf*tdec:.3f} (BE {BE})")
print("== A3 CKS stylized D=50: 1 tick needs OFI", 2*50, "; OFI=+30 ->", 30/(2*50), "tick")
for rho in (0.05, 0.1, 0.2): print(f"rho={rho} R2_pred=rho^2*0.65={rho*rho*0.65:.5f}")
print("== A4 KTW 'two average price changes' in ZM, unit-step RW assumption")
steps = s1**2 / 1.0; dt = 60/steps
print(f"mid changes per min ~ {steps:.2f}; mean interval {dt:.2f} s; two changes ~ {2*dt:.1f} s")
print("== B1 BGPW eq 8, FT C0=0.2 gamma=0.2 N=1000")
exact = 1 + sum(0.2 * l**-0.2 for l in range(1, 1001)); approx = 1 + 0.2/0.8 * 1000**0.8
print(f"exact={exact:.2f} closed form={approx:.2f} (paper text: ~50)")
print("== B2 BFL asymmetric liquidity eps_hat=0.2 theta=0.5 (ticks)")
e, th = 0.2, 0.5; rp, rm = th*(1-e), th*(1+e); pp, pm = (1+e)/2, (1-e)/2
print(f"r+={rp} r-={rm} phi+={pp} phi-={pm} E[r]={pp*rp-pm*rm:.6f}")
print("== C1 Patzelt-Bouchaud slope ~ N^-0.25; trades-per-minute proportional to minutes (assumption)")
for h in (1, 5, 15, 30): print(f"h={h} factor={h**-0.25:.4f} lambda_h={0.02*h**-0.25:.5f} ticks/contract")
lam, sdQ = 0.02, 60; r2c = (lam*sdQ)**2 / s1**2
print(f"lambda*sdQ={lam*sdQ:.2f} ticks; R2_c={r2c:.4f}; rho=0.1 -> R2_pred={0.01*r2c:.5f}")
dayvol = ADV*DAYSHARE; print(f"day-session volume {dayvol:.0f} over 290 min = {dayvol/290:.1f} contracts/min")
print("Hasbrouck check sqrt(10000)*7e-6 =", math.sqrt(10000)*7e-6)
print("== D1 microprice Brownian toy: Qb=40 Qa=10 -> I =", 40/50, "adj =", round(40/50-0.5, 3), "tick; max |adj| 0.5 tick =", round(0.5/BE, 3), "of BE")
print("== E1 refill tau=2 s: recovered by 6 s =", round(1-math.exp(-3), 4), "; tau=20 s by 6 s =", round(1-math.exp(-0.3), 4))
print("== F1 square-root impact, day-session sigma under RW over 290 min")
sd = s1*math.sqrt(290); print(f"sigma_day={sd:.2f} ticks")
for Q in (40, 120, 1000): print(f"Q={Q}: sqrt(Q/V)={math.sqrt(Q/ADV):.5f} I(Y=1)={sd*math.sqrt(Q/ADV):.2f} ticks")
inc = sd*(math.sqrt(120/ADV)-math.sqrt(40/ADV)); print(f"incremental impact 40->120 = {inc:.2f} ticks vs BE {BE}")
print("== G1 VPIN")
V = ADV/50; print(f"V=ADV/50={V:.1f} -> 734"); imb = [200, 150, 400, 100, 300]
print("VPIN(n=5)=", round(sum(imb)/(5*734), 4))
print("bulk volume: dP=+3 ticks sigma=3.15 -> Z =", round(N.cdf(3/3.15), 4))
print("== H1 family 5: ZC 97 bursts / 1528 days (|T|>4.0); ZM discovery days (assume 252/yr x 3.25 yr) =", 252*3.25)
print("scaled count:", round(97/1528*819, 1))
pre = 15; print(f"pre-burst 15 ticks = {pre/(s1*math.sqrt(5)):.2f} sigma_5m; b=-0.20 -> E[post] = {-0.20*pre:.1f} ticks; net of BE = {0.20*pre-BE:.2f}")
print("break-even pre-burst move for b=-0.20:", round(BE/0.20, 2), "ticks; for b=-0.10:", round(BE/0.10, 1))
