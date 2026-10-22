#!/usr/bin/env python3
"""REV_G2 independent replication of C2_Hawkes section 6 'measured cautionary result':
a Poisson process whose rate is drawn from {0.3, 3.0} per s on each 300 s segment (true
branching ratio 0) is fitted with a univariate exponential Hawkes model by MLE, and the
time-rescaling KS test is applied. Own code, own seeds; prints n_hat, beta_hat, mu_hat and
the KS p-value for three seeds, plus a correctly specified control (mu 0.5, n 0.6, beta 2).
Synthetic data only."""
import math
import sys
import time

import numpy as np
from scipy import optimize, stats


def loglik(t, T, mu, n, beta):
    a = 0.0
    s = 0.0
    prev = t[0]
    for i, ti in enumerate(t):
        if i:
            a = math.exp(-beta * (ti - prev)) * (1.0 + a)
        s += math.log(mu + n * beta * a)
        prev = ti
    return s - mu * T - n * float(np.sum(1.0 - np.exp(-beta * (T - t))))


def rescaled(t, mu, n, beta):
    out = np.empty(len(t))
    out[0] = mu * t[0]
    b = 1.0
    for k in range(1, len(t)):
        d = t[k] - t[k - 1]
        e = math.exp(-beta * d)
        out[k] = mu * d + n * b * (1.0 - e)
        b = 1.0 + e * b
    return out


def fit(t, T):
    def unpack(z):
        return math.exp(z[0]), 1.0 / (1.0 + math.exp(-z[1])), math.exp(z[2])

    def nll(z):
        mu, n, beta = unpack(z)
        return -loglik(t, T, mu, n, beta)

    best = None
    for b0 in (0.05, 0.5, 5.0):
        for n0 in (0.3, 0.8):
            z0 = np.array([math.log(0.5), math.log(n0 / (1 - n0)), math.log(b0)])
            r = optimize.minimize(nll, z0, method="L-BFGS-B")
            if best is None or r.fun < best.fun:
                best = r
    mu, n, beta = unpack(best.x)
    return mu, n, beta, -best.fun


def simulate_regime(rng, T=20000.0, seg=300.0, rates=(0.3, 3.0)):
    ev = []
    t0 = 0.0
    while t0 < T:
        rate = rng.choice(rates)
        k = rng.poisson(rate * seg)
        ev.append(np.sort(rng.uniform(t0, t0 + seg, k)))
        t0 += seg
    ev = np.concatenate(ev)
    return ev[ev < T]


def simulate_hawkes(rng, mu, n, beta, T):
    t, out, ex = 0.0, [], 0.0
    while True:
        lb = mu + ex
        w = rng.exponential(1.0 / lb)
        ex *= math.exp(-beta * w)
        t += w
        if t > T:
            break
        if rng.uniform() * lb <= mu + ex:
            out.append(t)
            ex += n * beta
    return np.array(out)


def report(label, t, T):
    t1 = time.time()
    mu, n, beta, ll = fit(t, T)
    tau = rescaled(t, mu, n, beta)
    z = 1.0 - np.exp(-tau)
    ks = stats.kstest(z, "uniform")
    ac1 = np.corrcoef(tau[:-1], tau[1:])[0, 1]
    print(f"{label}: N={len(t)} mu_hat={mu:.4f} n_hat={n:.4f} beta_hat={beta:.4f} "
          f"KS p={ks.pvalue:.3f} mean_tau={tau.mean():.4f} var_tau={tau.var():.4f} lag1={ac1:.4f} ({time.time() - t1:.1f}s)")


if __name__ == "__main__":
    T = 20000.0
    for seed in (101, 202, 303):
        rng = np.random.default_rng(seed)
        report(f"regime-switching Poisson, seed {seed}", simulate_regime(rng, T), T)
    rng = np.random.default_rng(404)
    report("control Hawkes (0.5, 0.6, 2.0), seed 404", simulate_hawkes(rng, 0.5, 0.6, 2.0, T), T)
