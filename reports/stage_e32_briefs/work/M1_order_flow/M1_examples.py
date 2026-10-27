"""M1_order_flow worked-example arithmetic (Stage E.32). No data read; inputs are E.28 standard numbers and stated assumptions."""
import math
from statistics import NormalDist
N = NormalDist()
s1 = 3.15            # ZM sigma_1m, ticks (A0 Table 1)
be = 1.59            # Topstep ZM market-order break-even, ticks (E.28 ranking row 130, mu*_mkt)
print("== (a) sigma_h under random walk, required R2 for mean|forecast| = break-even, top-decile mean |f|")
k = math.sqrt(2/math.pi)
tdec = 2*N.pdf(N.inv_cdf(0.95))/0.10   # E[|Z| | |Z|>z_0.95]
print(f"sqrt(2/pi)={k:.4f}; top-decile factor E[|Z| | |Z|>1.645]={tdec:.4f}")
for h in (1,5,15,30,60):
    sh = s1*math.sqrt(h); r2 = (be/(sh*k))**2
    print(f"h={h:>2} min sigma_h={sh:6.3f} ticks  R2 needed (mean rule)={r2:.5f}  R2 needed (top decile rule)={(be/(sh*tdec))**2:.5f}")
for lab, r2, h in (("CRS1996 OIB# 30min",0.0028,30),("CRS2002 OIB# 30min",0.0007,30),("CRS2002 OIB# 5min",0.0028,5),("CRS1996 OIB# 5min",0.0261,5)):
    sh=s1*math.sqrt(h); sf=math.sqrt(r2)*sh
    print(f"{lab}: R2={r2} s_f={sf:.3f} ticks mean|f|={sf*k:.3f} top-decile mean|f|={sf*tdec:.3f}")
print("== (a) CKS stylized: D=50 per level")
D=50; print("OFI for 1 tick =", 2*D, "; OFI=+30 ->", 30/(2*D), "ticks")
print("R2_pred = rho^2 R2_c with R2_c=0.65:", [(r, round(r*r*0.65,5)) for r in (0.05,0.1,0.2)])
print("== (b) BGPW eq 8 check, FT: C0=0.2 gamma=0.2 N=1000")
C0,g=0.2,0.2; exact=1+sum(C0*l**-g for l in range(1,1001)); approx=1+C0/(1-g)*1000**(1-g)
print(f"exact sum={exact:.2f} approx formula={approx:.2f} (paper says ~50)")
print("ZM illustrative C0=0.2, gamma=0.6, lags 1..100:", round(1+sum(0.2*l**-0.6 for l in range(1,101)),3))
eps=0.2; th=0.5; rp=th*(1-eps); rm=th*(1+eps); pp=(1+eps)/2; pm=(1-eps)/2
print(f"BFL asym liquidity: eps_hat={eps} theta={th}: r+={rp} r-={rm} phi+={pp} phi-={pm} E[r]={pp*rp-pm*rm:.6f}")
print("== (c) Patzelt-Bouchaud slope scaling N^-0.25, lambda_1=0.02 ticks/contract per 1-min bucket (trade-count proxy)")
for h in (1,5,15,30,60):
    print(f"h={h}: factor={h**-0.25:.4f} lambda_h={0.02*h**-0.25:.5f}")
lam=0.02; sdq=60; r2c=(lam*sdq)**2/s1**2; print(f"R2_c with lambda 0.02, sd(Q)=60: {(lam*sdq):.2f} ticks; R2_c={r2c:.4f}")
print("Hasbrouck check: sqrt(10000)*7e-6 =", math.sqrt(10000)*7e-6)
print("== (d) microprice toy (1-tick spread, weighted mid): Qb=40,Qa=10")
I=40/50; print("I=",I,"adj=",I-0.5,"ticks; CdL toy adj=", round((2*(2/math.pi)*math.atan(40/10)-1),4))
print("== (e) exponential refill tau=2 s: share recovered at 6 s =", round(1-math.exp(-3),4))
print("== (f) square-root impact: day-session sigma (RW, 290 min)")
sd=s1*math.sqrt(290); Q=1000; V=36690; I=sd*math.sqrt(Q/V)
print(f"sigma_day={sd:.2f} ticks sqrt(Q/V)={math.sqrt(Q/V):.4f} I(Y=1)={I:.2f} ticks; 1/3 reversion={I/3:.2f}")
print("== (g) VPIN: V=ADV/50 =", V/50)
imb=[200,150,400,100,300]; Vb=round(V/50); print("Vb=",Vb,"VPIN=", round(sum(imb)/(len(imb)*Vb),4))
print("== family 5: ZC drift bursts 97 in 1528 days at cv4.0; per 39 months (~816 trade dates):", round(97/1528*816,1))
print("five-minute reversal b=-0.20: pre-burst 5-min move 15 ticks -> expected post move", -0.20*15, "ticks")
