"""M5b part 2: hit-rate <-> edge mapping for importance units; MDA noise. Arithmetic only."""
import math
from statistics import NormalDist
Phi = NormalDist().cdf
S1, C = 3.15, 1.59
print("== hit rate needed: gross = (2p-1) E|r|, E|r| = sigma_h sqrt(2/pi) (normal, sign independent of size: ASSUMPTION)")
for h in (5, 15, 60):
    s = S1*math.sqrt(h); ea = s*math.sqrt(2/math.pi)
    row = ", ".join(f"mu={mu}: p={0.5+(C+mu)/(2*ea):.4f}" for mu in (0, 0.25, 0.5, 1.0))
    print(f"h={h}: sigma={s:.3f} E|r|={ea:.3f} ticks; {row}; 1pp accuracy = {0.02*ea:.3f} ticks gross")
print("== log-loss gain of a calibrated p vs 0.5: ln2 - H(p)")
for p in (0.52, 0.55, 0.5817, 0.6074):
    H = -(p*math.log(p)+(1-p)*math.log(1-p)); print(f"p={p}: H={H:.6f} gain={math.log(2)-H:.6f} nats")
print("== MDA (accuracy) noise: permutation flips the prediction on a share f of test rows; SE(dAcc) ~ sqrt(f/n) (upper bound, each flip +-1/n)")
for n in (10_000, 100_000, 800_000):
    print(f"n={n}: " + ", ".join(f"f={f}: SE={math.sqrt(f/n):.5f}" for f in (0.05, 0.2, 0.5)))
print("== purged-fold sample: one 15-min label per 15 min, 1055 min/day x 816 days / 15 =", round(1055*816/15))
