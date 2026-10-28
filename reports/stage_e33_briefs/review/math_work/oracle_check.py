"""Independent check of the P4.2 oracle on check seed 80001 (synthetic data: anything allowed).
Uses synth33 only to GENERATE the seed's data; the class probabilities (numerical integral, own code),
class means, P3.8 simulation and Sharpe are recomputed here."""
import os, sys, math, json
os.nice(10)
sys.path.insert(0, "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/work/pipeline")
import numpy as np
from scipy.special import ndtr
import synth33 as s33
seed = 80001
data = s33.generate(seed, "planted", with_features=False, labels=("F15",))
lab, path, cal, beta = data.labels["F15"], data.path, data.cal, data.beta
h, phi, q = 15, math.exp(-1 / 5), 0.10
c = [59 / 60] + [1.0] * (h - 1) + [1 / 60]
g = sum(c[m] * phi ** m for m in range(h + 1))
a = [sum(c[m] * phi ** (m - k) for m in range(k, h + 1)) for k in range(1, h + 1)]
vz = (1 - phi * phi) * sum(x * x for x in a)
print(f"beta {beta} g {g:.6f} vz {vz:.6f}; synth33 drift_moments {s33.drift_moments(beta, h)}")
oof = slice(20, len(cal.dates)); n = lab["t_ns"].shape[1]
z = path.z[oof][:, 60:60 + n]
m = beta * g * z
v = (path.sigma[oof] ** 2 * h)[:, None] + beta * beta * vz
s = np.sqrt(v)
# own class probabilities by a numerical integral over the fractional part u (midpoint rule, 400 points per half)
p_up = np.zeros_like(m); p_dn = np.zeros_like(m)
for s_e, pe in ((1, 1 - q), (2, q)):
    for s_x, px in ((1, 1 - q), (2, q)):
        for lo, hi in ((0.0, 0.5), (0.5, 1.0)):
            upper = lo >= 0.5
            a_e = 1 + (1 if (s_e == 2 and upper) else 0)
            b_e = 0 if s_e == 1 else (0 if upper else -1)
            k_up = a_e + (1.0 if s_x == 1 else 1.5)
            k_dn = b_e - (1.0 if s_x == 1 else 1.5)
            us = lo + (hi - lo) * (np.arange(400) + 0.5) / 400
            acc_up = np.zeros_like(m); acc_dn = np.zeros_like(m)
            for u in us:
                acc_up += 1.0 - ndtr((k_up - u - m) / s)
                acc_dn += ndtr((k_dn - u - m) / s)
            p_up += pe * px * (hi - lo) * acc_up / len(us)
            p_dn += pe * px * (hi - lo) * acc_dn / len(us)
pu2, pd2 = s33.fh_class_probs(m, v)
print(f"max |p_up own - synth33| {np.max(np.abs(p_up - pu2)):.2e}; max |p_dn| {np.max(np.abs(p_dn - pd2)):.2e}")
# empirical calibration on row_ok rows (synthetic labels): deciles of p_up and p_dn
ok = lab["row_ok"]; y = lab["y"]
for name, pp, kk in (("p_up", p_up, 1), ("p_dn", p_dn, -1)):
    edges = np.quantile(pp[ok], np.linspace(0, 1, 11))
    rows = []
    for j in range(10):
        sel = ok & (pp >= edges[j]) & (pp < edges[j + 1] if j < 9 else pp <= edges[j + 1])
        rows.append((round(float(pp[sel].mean()), 4), round(float((y[sel] == kk).mean()), 4), int(sel.sum())))
    print(name, "deciles (model mean, empirical share, n):", rows)
# own class means (P3.7 weights) and EV
w, nl, ns = lab["w"], lab["n_long"], lab["n_short"]
mu_l = {k: float(np.sum(w[ok & (y == k)] * nl[ok & (y == k)]) / np.sum(w[ok & (y == k)])) for k in (-1, 0, 1)}
mu_s = {k: float(np.sum(w[ok & (y == k)] * ns[ok & (y == k)]) / np.sum(w[ok & (y == k)])) for k in (-1, 0, 1)}
print("mu_long", mu_l, "mu_short", mu_s)
p0 = 1 - p_up - p_dn
ev_l = p_dn * mu_l[-1] + p0 * mu_l[0] + p_up * mu_l[1]
ev_s = p_dn * mu_s[-1] + p0 * mu_s[0] + p_up * mu_s[1]
# own P3.8 simulation: one position, cap 20, exit at t + h + L -> next decision at grid minute i + h + 1
x = []; ntr = []
for d in range(lab["t_ns"].shape[0]):
    tot, k, i = 0.0, 0, 0
    eo = lab["entry_ok"][d]
    while i < n and k < 20:
        if not eo[i]:
            i += 1; continue
        el, es = ev_l[d, i], ev_s[d, i]
        if el > max(es, 0.0):
            tot += float(lab["long_net"][d, i]); k += 1; i += h + 1
        elif es > max(el, 0.0):
            tot += float(lab["short_net"][d, i]); k += 1; i += h + 1
        else:
            i += 1
    x.append(tot); ntr.append(k)
x = np.array(x)
sharpe = x.mean() / x.std()
print(f"own oracle: dates {len(x)} trades {sum(ntr)} ({sum(ntr) / len(x):.2f}/date) mean {x.mean():.4f} pstd {x.std():.4f} Sharpe {sharpe:.6f}")
ref = s33.oracle_fh(cal, path, lab, beta)
print(f"synth33 oracle_fh: Sharpe {ref['sharpe']:.6f} trades {ref['trades']} mu_long {ref['mu_long']} mu_short {ref['mu_short']}")
cj = json.load(open("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e33_briefs/work/ProofCoder_calibration.json"))
print(f"calibration.json check_values[0] (seed 80001) {cj['check_values'][0]:.6f}; check_mean {cj['check_mean']:.4f} se {cj['check_se']:.4f}; calib_mean {cj['calib_mean']:.4f} se {cj['calib_se']:.4f}; slope {cj['d_sr_d_beta_approx']:.3f} -> se(beta) about {cj['calib_se'] / cj['d_sr_d_beta_approx']:.4f}")
