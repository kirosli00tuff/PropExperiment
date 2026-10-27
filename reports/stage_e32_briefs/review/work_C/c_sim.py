"""MathReviewer C: independent Monte Carlo checks of the simulated tables in M5a (e.3 PBO noise,
e.3 hand example, d.3(iv) per-trade vs daily) and M5b (b.3 quarters/months rule, dominance,
c.3 overlap D). Own code, fixed seeds, small sizes; prints results only."""
from __future__ import annotations

import os
from itertools import combinations
from math import sqrt

import numpy as np

os.nice(10)
rng = np.random.default_rng(20261027)


def pbo_cscv(perf: np.ndarray, s: int) -> tuple[float, float]:
    """perf: dates x configs. Returns (PBO, share of splits where IS winner has OOS sum < 0)."""
    t, n = perf.shape
    w = t // s
    blocks = np.array([perf[b * w:(b + 1) * w].sum(axis=0) for b in range(s)])  # s x n
    below, loss, total = 0, 0, 0
    for train in combinations(range(s), s // 2):
        test = [b for b in range(s) if b not in train]
        r_is = blocks[list(train)].sum(axis=0)
        r_oos = blocks[test].sum(axis=0)
        star = int(np.argmax(r_is))
        worse = int((r_oos < r_oos[star]).sum())
        omega = (worse + 0.5) / n
        below += omega <= 0.5
        loss += r_oos[star] < 0
        total += 1
    return below / total, loss / total


def main() -> None:
    print("== M5a e.3 hand example ==")
    m = np.array([[5, -3, 4, -2, 6, -4, 3, -1], [2, 2, -1, 1, 0, 1, -2, 2],
                  [-4, 6, -3, 5, -2, 4, -1, 3], [1, -1, 1, -1, 1, -1, 1, -1]], dtype=float).T
    pbo, loss = pbo_cscv(m, 8)
    print(f"PBO={pbo:.3f} ({round(pbo*70)}/70), OOS loss share={loss:.3f} ({round(loss*70)}/70)")

    print("== M5a e.3 PBO noise (iid N(0,1), 816 days) ==")
    for n_cfg, s, reps in ((10, 8, 200), (50, 8, 200), (200, 16, 6)):
        vals = [pbo_cscv(rng.standard_normal((816, n_cfg)), s)[0] for _ in range(reps)]
        v = np.array(vals)
        print(f"N={n_cfg} S={s} reps={reps}: mean {v.mean():.3f} sd {v.std():.3f} 5-95% {np.quantile(v,.05):.3f}-{np.quantile(v,.95):.3f}"
              f"  P(PBO<0.4)={np.mean(v < 0.4):.2f}")
    vals = []
    for _ in range(200):
        p = rng.standard_normal((816, 50))
        p[:, 0] += 0.10
        vals.append(pbo_cscv(p, 8)[0])
    v = np.array(vals)
    print(f"N=50 one true SR .10: mean {v.mean():.3f} 5-95% {np.quantile(v,.05):.3f}-{np.quantile(v,.95):.3f}")

    print("== M5a d.3(iv) per-trade vs daily-with-zeros ==")
    z_tr, z_day = [], []
    for _ in range(1000):
        days = 816
        trade = rng.random(days) < 0.5
        x = rng.standard_t(5, days) / sqrt(5 / 3) + 0.08
        per_trade = x[trade]
        daily = np.where(trade, x, 0.0)
        z_tr.append(per_trade.mean() / per_trade.std() * sqrt(len(per_trade)))
        z_day.append(daily.mean() / daily.std() * sqrt(days))
    print(f"mean z per-trade {np.mean(z_tr):.3f}, daily {np.mean(z_day):.3f}, corr {np.corrcoef(z_tr, z_day)[0,1]:.4f}")

    print("== M5b b.3 quarters / months rule cost ==")
    for q, k, delta, label in ((13, 9, 3.8416, "disc Q=13 d3.84"), (14, 10, 3.8416, "test Q=14 d3.84"),
                               (13, 9, 3.0, "disc Q=13 d3.0"), (43, 29, 3.8416, "test months d3.84"),
                               (43, 29, 3.0, "test months d3.0")):
        x = rng.standard_normal((200000, q)) + delta / sqrt(q)
        t = x.sum(axis=1) / sqrt(q)
        rule = (x > 0).sum(axis=1) >= k
        print(f"{label}: P(rule)={rule.mean():.3f} P(t>3)={np.mean(t>3):.3f} P(t>3 & rule)={np.mean((t>3)&rule):.3f}")
    print("== M5b b.3 dominance (43 months, delta 3.84, given t>3) ==")
    x = rng.standard_normal((200000, 43)) + 3.8416 / sqrt(43)
    t = x.sum(axis=1) / sqrt(43)
    sel = x[t > 3]
    share = sel.max(axis=1) / sel.sum(axis=1)
    tot = sel.sum(axis=1)
    lomo = (tot[:, None] - sel) / sqrt(42)
    print(f"median max-month share {np.median(share):.3f}, 99% {np.quantile(share,.99):.3f}, P(share<=.25)={np.mean(share<=.25):.4f}; "
          f"LOMO min t 1% {np.quantile(lomo.min(axis=1),.01):.2f}, P(all LOMO>2.5)={np.mean(lomo.min(axis=1)>2.5):.4f}")
    x = rng.standard_normal((400000, 43)); x[:, 0] += 6.0
    t = x.sum(axis=1) / sqrt(43)
    fp = x[t > 3]
    share = fp.max(axis=1) / fp.sum(axis=1)
    lomo = (fp.sum(axis=1)[:, None] - fp) / sqrt(42)
    print(f"spike +6 (own noise): P(t>3)={np.mean(t>3):.4f}; caught by 25% rule {np.mean(share>.25):.3f}, by LOMO<=2.5 {np.mean(lomo.min(axis=1)<=2.5):.3f}, either {np.mean((share>.25)|(lomo.min(axis=1)<=2.5)):.3f}")

    print("== M5b c.3 overlap D for m=3 ==")
    steps = rng.standard_normal((2000, 600))
    cum = np.cumsum(steps, axis=1)
    ret15 = cum[:, 3:] - cum[:, :-3]  # 15-minute returns entered every 5 minutes
    var_mean = ret15.mean(axis=1).var()
    d = var_mean * ret15.shape[1] / 3.0  # per-trade variance is 3
    print(f"D = Var(mean)*n/sigma^2 = {d:.2f} (theory 3)")


if __name__ == "__main__":
    main()
