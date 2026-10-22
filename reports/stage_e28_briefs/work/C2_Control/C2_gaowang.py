"""C2_Control: Gao-Wang (2020) per-fill value with fees. E[profit|fill] = lp/(lp+lam/2) - 0.5 ticks (their Thm 4.1 discussion).
With a per-side fee f (ticks) the order is worth posting only if lp/(lp+lam/2) > 0.5 + f."""
import math
for name, tv, rt in (("MES", 1.25, 1.22), ("ES", 12.50, 3.78)):
    f = rt / 2 / tv
    need = 0.5 + f
    ratio = need / (1 - need)  # lp/(lam/2) needed
    print(f"{name}: fee/side={f:.4f} tick; need benign-fill share > {need:.4f}; lp > {ratio:.3f} x (lam/2) = {ratio/2:.3f} x lam")
    for share in (0.6, 0.7, 0.8):
        ev = share * 0.5 - (1 - share) * 0.5 - f
        print(f"   benign share {share:.2f}: E[net per fill] = {ev:+.4f} tick = ${ev*tv:+.3f}")
# sample size to show benign share > threshold at t>3 (binomial, iid fills; clustering inflates this)
for thr, true in ((0.6512, 0.70), (0.6512, 0.75), (0.9880, 0.995)):
    n = 9 * true * (1 - true) / (true - thr) ** 2
    print(f"threshold {thr}, true share {true}: n ~ {n:,.0f} fills (iid binomial, t=3)")
