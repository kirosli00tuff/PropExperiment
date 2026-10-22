"""C2_Hawkes small worked-example arithmetic (no data)."""
import json, sys
import numpy as np
from scipy import stats, integrate
out = {}
# Bacry et al. 2013 signature plot, their convention phi(t)=a exp(-b t), ||phi||=a/b
mu, norm, b = 0.2, 0.6, 2.0
a = norm * b; gam = a + b; Lam = 2 * mu / (1 - norm); kap = 1 / (1 + norm)
C = lambda tau: Lam * (kap**2 + (1 - kap**2) * (1 - np.exp(-gam * tau)) / (gam * tau))
out["signature"] = {"mu": mu, "norm": norm, "b": b, "a": a, "gamma": gam, "Lambda": Lam, "kappa": kap,
                    "C_0": Lam, "C_inf": Lam * kap**2, **{f"C_{t}s": float(C(t)) for t in (0.1, 1.0, 10.0, 60.0)}}
# bivariate buy/sell exponential Hawkes stationarity
A = np.array([[0.5, 0.2], [0.2, 0.5]]); m = np.array([0.3, 0.3])
out["bivariate"] = {"eig": sorted(np.linalg.eigvals(A).real.tolist()), "Lambda": np.linalg.solve(np.eye(2) - A, m).tolist()}
# power-law kernel norm alpha/gamma
al, be, ga = 0.3, 10.0, 0.4
val, _ = integrate.quad(lambda t: al * be / (1 + be * t) ** (1 + ga), 0, np.inf, limit=500)
out["powerlaw_norm"] = {"numeric": val, "closed_form": al / ga}
# inhomogeneous Poisson: rate 5/s first, then 1/s; prob of no event in 2 s windows; expected count 9:30-9:31 profile example
out["inhom"] = {"P0_2s_rate5": float(np.exp(-10)), "P0_2s_rate1": float(np.exp(-2)),
                "count_mixed_1s_at5_then_1s_at1": 6.0, "P0_mixed": float(np.exp(-6))}
# sample sizes for a two-group difference in mean markout, sd=1 tick, delta=0.1 tick
for z in (1.96, 3.0):
    out[f"n_per_group_z{z}"] = 2 * (z + 0.8416) ** 2 * (1.0 / 0.1) ** 2
# Hawkes-implied cluster size and endogenous fraction for n = 0.8
n = 0.8; out["cluster"] = {"mean_cluster_size": 1 / (1 - n), "endog_fraction": n, "Lambda_mu0.5": 0.5 / (1 - n)}
json.dump(out, open(sys.argv[1], "w"), indent=1); print(json.dumps(out))
