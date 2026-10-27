"""R5: rho needed at 5/15/30/60 min for 4 trades/day in the 290-min day session; gross at planning rhos."""
from math import sqrt, exp, pi
from statistics import NormalDist
N = NormalDist(); phi = lambda x: exp(-x*x/2)/sqrt(2*pi)
for h in (5, 15, 30, 60):
    s = 3.15*sqrt(h); nb = 290/h; q = min(4/nb, 1.0)
    c = N.inv_cdf(1-q/2); k = 2*phi(c)/q
    need = [round(G/(s*k), 4) for G in (1.59, 2.4, 2.8)]
    gross = [round(r*s*k, 2) for r in (0.03, 0.05, 0.08, 0.10)]
    print(f"h={h} sigma={s:.3f} bars={nb:.3f} q={q:.4f} c={c:.4f} k={k:.4f} rho_need(1.59,2.4,2.8)={need} gross@rho(.03,.05,.08,.10)={gross}")
