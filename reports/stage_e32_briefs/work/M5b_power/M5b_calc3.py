"""M5b part 3: spike-month counter-case. Synthetic only."""
import numpy as np, math
rng = np.random.default_rng(7); R = 2_000_000
for spike in (6.0, 10.0):
    x = rng.standard_normal((R, 43)); x[:, 0] += spike
    tot = x.sum(1); ok = tot/math.sqrt(43) > 3
    share = x.max(1)/tot; lomo_min = ((tot[:, None]-x)/math.sqrt(42)).min(1)
    print(f"spike={spike}: P(t>3)={ok.mean():.4f}; P(share>0.25|t>3)={np.mean(share[ok]>0.25):.3f}; P(LOMO min t<=2.5|t>3)={np.mean(lomo_min[ok]<=2.5):.3f}; P(either|t>3)={np.mean((share[ok]>0.25)|(lomo_min[ok]<=2.5)):.3f}")
