"""REV_G3: recompute the C2_Pooled worked examples (sections 1.6, 1.8, 2.6, 3.5, 6.2-6.5, 7.3, 8).
Run: python -I REV_G3_pooled_arith.py"""
import math

import numpy as np

print("1.6(a) SE and n:", math.sqrt(0.25 / 1e6), 0.01 / math.sqrt(0.25 / 1e6),
      [(d, (3 * 0.5 / d) ** 2) for d in (0.02, 0.01, 0.005)])
print("1.6(b) edge $:", (2 * 0.55 - 1) * 0.5 * 1.25, " cost:", 1.25 + 1.22, " ratio:", (1.25 + 1.22) / ((2 * 0.55 - 1) * 0.5 * 1.25))
print("1.7 fills per tercile:", 2 * (3 * 1 / 0.1) ** 2)
print("1.8 LSTM params:", 4 * (50 * 90 + 50), 2 * 4 * (50 * 100 + 50), 4 * (50 * 90 + 50) + 2 * 4 * (50 * 100 + 50))
H = [0.7, 0.6, 0.5]
p = [H[0], (1 - H[0]) * H[1], (1 - H[0]) * (1 - H[1]) * H[2], (1 - H[0]) * (1 - H[1]) * (1 - H[2])]
print("2.6 hazard chain:", [round(x, 3) for x in p], sum(p), "E>=", sum((i + 1) * x for i, x in enumerate(p)), "$", 1.25 * sum((i + 1) * x for i, x in enumerate(p)))
print("3.5 bps:", 0.25 / 4500 * 1e4, 0.25 / 15500 * 1e4, 0.7 / (0.25 / 4500 * 1e4), 0.7 / (0.25 / 15500 * 1e4))
print("6.2:", 1 / 6.61, 1 / 27.83, 27.83 / 6.61, 6.61 * 1.25, 27.83 * 0.5, 10.01 * 0.5, 12.14 * 0.5)
print("6.3:", 1637 / 60 / 2, 300 / (1637 / 120), 15 / (984 / 120), 10 / (255 / 120), 8 / (226 / 120))
print("6.4 K_eff:", [(r, 3 / (1 + 2 * r)) for r in (0.3, 0.6, 0.8, 0.9)])
# 6.5 DerSimonian-Laird
y = np.array([-0.30, -0.45, -0.20]); s = np.array([0.05, 0.08, 0.10]); w = 1 / s ** 2
ybar = (w * y).sum() / w.sum()
Q = (w * (y - ybar) ** 2).sum()
C = w.sum() - (w ** 2).sum() / w.sum()
tau2 = max(0.0, (Q - (len(y) - 1)) / C)
wr = 1 / (s ** 2 + tau2)
mu = (wr * y).sum() / wr.sum()
B = s ** 2 / (s ** 2 + tau2)
print(f"6.5 DL: ybar={ybar:.4f} Q={Q:.3f} tau2={tau2:.5f} tau={math.sqrt(tau2):.4f} mu={mu:.4f} SE={1 / math.sqrt(wr.sum()):.4f}")
print("     B:", np.round(B, 3), " shrunk:", np.round(B * mu + (1 - B) * y, 4))
print("7.3 3/sqrt(D):", [(D, round(3 / math.sqrt(D), 3)) for D in (20, 40, 60, 80)])
print("7.4 grid:", 3 * 2 * 2 * 3 * 3)
print("8 peak TFLOPs:", 2048 * 2 * 1.74e9 / 1e12, 2048 * 2 * 0.99e9 / 1e12)
per_seq = 3 * 2 * 58600 * 100
print("8 per seq MFLOP:", per_seq / 1e6, " per epoch:", per_seq * 5e6, " s/epoch at 1.4,0.5 TFLOPs:", per_seq * 5e6 / 1.4e12, per_seq * 5e6 / 0.5e12,
      " h/20 epochs:", per_seq * 5e6 / 1.4e12 * 20 / 3600, per_seq * 5e6 / 0.5e12 * 20 / 3600)
print("8 memory GB:", 5e6 * 40 * 4 / 1e9, " 3000h*0.89:", 3000 * 0.89)
