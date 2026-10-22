"""C2_Hawkes: timing of a D-dimensional exponential-kernel log-likelihood (single shared beta), synthetic data.
lambda_k(t) = mu_k + beta * sum_j alpha_kj * R_j(t-),  R_j(t) = sum_{t_m<t, k_m=j} exp(-beta (t - t_m)).
log L = sum_m log lambda_{k_m}(t_m) - sum_k mu_k T - sum_m (sum_k alpha_{k,k_m}) (1 - exp(-beta (T - t_m))).
"""
import json, os, sys, time
import numpy as np
os.nice(10)
from tick.hawkes import SimuHawkesExpKernels

def loglik_multi(times, types, T, mu, alpha, beta):
    D = len(mu)
    R = np.zeros(D)
    s = 0.0
    prev = times[0]
    ab = alpha * beta
    for t, k in zip(times, types):
        R *= np.exp(-beta * (t - prev))
        s += np.log(mu[k] + ab[k] @ R)
        R[k] += 1.0
        prev = t
    colsum = alpha.sum(axis=0)
    comp = mu.sum() * T + np.sum(colsum[types] * (1.0 - np.exp(-beta * (T - times))))
    return s - comp

adj = np.array([[0.45,0.05,0,0.05],[0.05,0.45,0.05,0],[0.10,0,0.30,0.05],[0,0.10,0.05,0.30]])
base = np.array([0.4,0.4,2.0,2.0]); beta = 5.0
out = {}
for n_target in (100000, 1000000):
    lam = np.linalg.solve(np.eye(4)-adj, base); end = n_target/lam.sum()
    sim = SimuHawkesExpKernels(adjacency=adj, decays=beta, baseline=base, end_time=end, verbose=False, seed=11)
    sim.simulate(); ts = sim.timestamps
    times = np.concatenate(ts); types = np.concatenate([np.full(len(x), i) for i, x in enumerate(ts)])
    o = np.argsort(times, kind="stable"); times, types = times[o], types[o]
    t1 = time.time(); ll_true = loglik_multi(times, types, end, base, adj, beta); dt = time.time()-t1
    ll_zero = loglik_multi(times, types, end, lam, np.zeros((4,4)), beta)  # Poisson with the right rates
    out[f"N{len(times)}"] = {"eval_seconds_python": dt, "loglik_true_params": ll_true,
                             "loglik_poisson_same_rates": ll_zero, "llr_per_event": (ll_true-ll_zero)/len(times)}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out))
