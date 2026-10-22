"""Section 9 and 11 worked numbers (hypothetical inputs, clearly labelled in C2_LOB.md)."""
import math
import numpy as np
from scipy.linalg import expm
def back_of_queue_fill_cdf(b, mu, th, ts):
    """Pure-death time to clear b units (ours last, never cancels): rates mu + th*(i-1), i=b..1 (CST eq 14)."""
    G = np.zeros((b + 1, b + 1))           # state k = units left including ours, k=0 absorbing (filled)
    for k in range(1, b + 1):
        r = mu + th * (k - 1); G[k, k] = -r; G[k, k - 1] = r
    out = []
    for t in ts:
        P = expm(G * t); out.append(P[b, 0])
    mean = sum(1 / (mu + th * (k - 1)) for k in range(1, b + 1))
    return out, mean
for b, mu, th in [(51, 2.0, 0.0), (51, 2.0, 0.02), (201, 2.0, 0.02), (11, 2.0, 0.02)]:
    cdf, m = back_of_queue_fill_cdf(b, mu, th, [1, 10, 60])
    print(f"b={b} (ahead={b-1}) mu={mu}/s theta={th}/s: P(fill<=1s,10s,60s)={[round(x,3) for x in cdf]} mean={m:.1f}s")
# pro-rata (Allocation algorithm, 2-lot minimum) for a 1-lot in a 1,000-lot level hit by a 50-lot aggressor
Q, ours, agg = 1000, 1, 50
share = agg * ours / Q
print(f"pro-rata raw share={share:.3f} lots -> floor {math.floor(share)}; 2-lot minimum -> 0")
# a 40-lot resting order would get floor(50*40/1000)=2
print("40-lot order pro-rata:", math.floor(agg * 40 / Q))
# markout decomposition example
half_spread = 0.5; adverse = 0.57; fee_ticks = 0.0
print(f"m_h = half-spread - adverse = {half_spread-adverse:+.2f} tick")
# Fee in ticks for a hypothetical all-in fee of $0.50 per side on MES (1 tick = $1.25)
print("fee $0.50 per side = %.2f tick; round trip $1.00 = %.2f tick" % (0.50/1.25, 1.00/1.25))
