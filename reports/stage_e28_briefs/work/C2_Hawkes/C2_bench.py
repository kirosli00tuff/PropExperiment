"""C2_Hawkes worked examples and speed probes on SYNTHETIC data only (no market data).

Run (ephemeral env, not a project dependency):
  nice -n 10 uv run --no-project --python 3.12 --with tick==0.8.0.2 --with scipy \
      python -I C2_bench.py <out_json>
Each part writes into the JSON as it finishes; finished parts are skipped on restart.
Kernel convention everywhere: phi(t) = alpha * beta * exp(-beta t), so alpha = ||phi|| = branching ratio n.
"""
import json
import os
import resource
import sys
import time

import numpy as np
from scipy import optimize, stats

os.nice(10)
OUT = sys.argv[1]
N_THREADS = min(8, (os.cpu_count() or 2) // 2)
RES = json.load(open(OUT)) if os.path.exists(OUT) else {}


def save(key, val):
    RES[key] = val
    with open(OUT, "w") as fh:
        json.dump(RES, fh, indent=1, default=float)
    print(key, "done", flush=True)


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


# ---------- core O(N) exponential-kernel likelihood (Ozaki-type recursion) ----------
def loglik_exp(t, T, mu, alpha, beta):
    """log L = sum_i log(mu + alpha*beta*A_i) - [mu*T + alpha*sum_i (1 - exp(-beta (T - t_i)))],
    A_1 = 0, A_i = exp(-beta (t_i - t_{i-1})) * (1 + A_{i-1})."""
    a = 0.0
    s = 0.0
    prev = None
    for ti in t:
        if prev is not None:
            a = np.exp(-beta * (ti - prev)) * (1.0 + a)
        s += np.log(mu + alpha * beta * a)
        prev = ti
    comp = mu * T + alpha * np.sum(1.0 - np.exp(-beta * (T - t)))
    return s - comp


def loglik_exp_naive(t, T, mu, alpha, beta):
    """O(N^2) version: lambda(t_i) = mu + sum_{j<i} alpha beta exp(-beta (t_i - t_j))."""
    d = t[:, None] - t[None, :]
    k = np.where(d > 0, alpha * beta * np.exp(-beta * np.clip(d, 0, None)), 0.0)
    lam = mu + k.sum(axis=1)
    comp = mu * T + alpha * np.sum(1.0 - np.exp(-beta * (T - t)))
    return np.sum(np.log(lam)) - comp


def rescaled_increments(t, mu, alpha, beta):
    """tau_k = Lambda(t_k) - Lambda(t_{k-1}) = mu*D_k + alpha*B_{k-1}*(1 - exp(-beta D_k)),
    B_k = 1 + exp(-beta D_k) * (B_{k-1} - 1) ... computed as B_k = sum_{j<=k} exp(-beta (t_k - t_j))."""
    out = np.empty(len(t))
    out[0] = mu * t[0]
    b = 1.0
    for k in range(1, len(t)):
        dk = t[k] - t[k - 1]
        out[k] = mu * dk + alpha * b * (1.0 - np.exp(-beta * dk))
        b = 1.0 + np.exp(-beta * dk) * b
    return out


def simulate_exp_hawkes(mu, alpha, beta, T, rng):
    """Ogata thinning for the univariate exponential Hawkes process."""
    t, out, lam_excess = 0.0, [], 0.0  # lam_excess = sum alpha beta exp(-beta (t - t_j))
    while True:
        lam_bar = mu + lam_excess
        w = rng.exponential(1.0 / lam_bar)
        t_new = t + w
        lam_excess *= np.exp(-beta * w)
        t = t_new
        if t > T:
            break
        if rng.uniform() * lam_bar <= mu + lam_excess:
            out.append(t)
            lam_excess += alpha * beta
    return np.array(out)


def fit_exp_mle(t, T, x0=(0.5, 0.5, 1.0)):
    """MLE over (mu, alpha, beta) with log-parametrisation for mu, beta and logit for alpha in (0,1)."""
    def unpack(z):
        return np.exp(z[0]), 1.0 / (1.0 + np.exp(-z[1])), np.exp(z[2])

    def nll(z):
        mu, al, be = unpack(z)
        return -loglik_exp(t, T, mu, al, be)

    z0 = np.array([np.log(x0[0]), np.log(x0[1] / (1 - x0[1])), np.log(x0[2])])
    best = None
    for shift in (0.0, 1.5, -1.5):  # a few starts on beta (likelihood can be multi-modal)
        z = z0.copy()
        z[2] += shift
        r = optimize.minimize(nll, z, method="L-BFGS-B")
        if best is None or r.fun < best.fun:
            best = r
    mu, al, be = unpack(best.x)
    return {"mu": mu, "n": al, "beta": be, "loglik": -best.fun, "nit": int(best.nit)}


def ks_uniform(t, mu, al, be):
    tau = rescaled_increments(t, mu, al, be)
    z = 1.0 - np.exp(-tau)
    ks = stats.kstest(z, "uniform")
    lb_lag1 = np.corrcoef(tau[:-1], tau[1:])[0, 1]
    return {"ks_stat": ks.statistic, "ks_p": ks.pvalue, "mean_tau": float(tau.mean()),
            "var_tau": float(tau.var()), "lag1_autocorr_tau": float(lb_lag1), "n_events": len(t)}


# ---------- Part 1: hand example ----------
def part_hand():
    t = np.array([0.5, 1.0, 1.2, 3.0])
    T, mu, al, be = 4.0, 0.5, 0.6, 2.0
    rows, a, prev = [], 0.0, None
    for ti in t:
        if prev is not None:
            a = np.exp(-be * (ti - prev)) * (1.0 + a)
        rows.append({"t": ti, "A": a, "lambda": mu + al * be * a})
        prev = ti
    comp_terms = (al * (1 - np.exp(-be * (T - t)))).tolist()
    ll = loglik_exp(t, T, mu, al, be)
    ll_naive = loglik_exp_naive(t, T, mu, al, be)
    tau = rescaled_increments(t, mu, al, be)
    save("hand", {"rows": rows, "compensator_kernel_terms": comp_terms, "mu_T": mu * T,
                  "compensator": mu * T + sum(comp_terms), "loglik": ll, "loglik_naive": ll_naive,
                  "tau": tau.tolist(), "z": (1 - np.exp(-tau)).tolist()})


# ---------- Part 2: Hardiman-Bouchaud variance estimator on simulated data ----------
def part_hb():
    rng = np.random.default_rng(1)
    mu, al, be = 0.5, 0.8, 1.0
    T = 200000.0
    t = simulate_exp_hawkes(mu, al, be, T, rng)
    out = {"true": {"mu": mu, "n": al, "beta": be}, "n_events": len(t),
           "Lambda_theory": mu / (1 - al), "Lambda_empirical": len(t) / T}
    for w in (10.0, 100.0, 1000.0):
        counts = np.histogram(t, bins=np.arange(0, T + w, w))[0]
        m, v = counts.mean(), counts.var()
        out[f"window_{int(w)}s"] = {"mean": m, "var": v, "n_hat": 1 - np.sqrt(m / v)}
    save("hb_estimator", out)


# ---------- Part 3: fill probability, Poisson vs Hawkes with the same mean rate ----------
def part_fill():
    rng = np.random.default_rng(2)
    lam_total, q_ahead = 2.0, 20  # 2 unit-size market sells per second hitting our bid level; 20 lots ahead
    res = {"lam_total": lam_total, "queue_ahead": q_ahead, "assumptions":
           "unit MO size, no cancellations ahead, queue only depletes by MOs, level not cleared otherwise"}
    for T in (1.0, 10.0, 60.0):
        res[f"poisson_T{int(T)}"] = float(stats.poisson.sf(q_ahead, lam_total * T))  # P(N_T >= Q+1)
    al, be = 0.7, 1.0
    mu = lam_total * (1 - al)
    Tsim = 400000.0
    ev = simulate_exp_hawkes(mu, al, be, Tsim, rng)
    starts = rng.uniform(1000.0, Tsim - 100.0, 20000)
    for T in (1.0, 10.0, 60.0):
        n_in = np.searchsorted(ev, starts + T) - np.searchsorted(ev, starts)
        res[f"hawkes_T{int(T)}"] = float(np.mean(n_in >= q_ahead + 1))
        res[f"hawkes_T{int(T)}_mean_count"] = float(n_in.mean())
        res[f"hawkes_T{int(T)}_var_count"] = float(n_in.var())
    res["hawkes_params"] = {"mu": mu, "n": al, "beta": be, "n_events": len(ev)}
    save("fill_prob", res)


# ---------- Part 4: spurious criticality from regime-switching Poisson ----------
def part_spurious():
    rng = np.random.default_rng(3)
    T, seg = 20000.0, 300.0
    ev, t0 = [], 0.0
    while t0 < T:
        rate = rng.choice([0.3, 3.0])
        k = rng.poisson(rate * seg)
        ev.append(np.sort(rng.uniform(t0, t0 + seg, k)))
        t0 += seg
    ev = np.concatenate(ev)
    ev = ev[ev < T]
    t1 = time.time()
    fit = fit_exp_mle(ev, T)
    fit["seconds"] = time.time() - t1
    fit["gof"] = ks_uniform(ev, fit["mu"], fit["n"], fit["beta"])
    rng2 = np.random.default_rng(4)
    ev_h = simulate_exp_hawkes(0.5, 0.6, 2.0, 20000.0, rng2)
    fit_h = fit_exp_mle(ev_h, 20000.0)
    fit_h["gof"] = ks_uniform(ev_h, fit_h["mu"], fit_h["n"], fit_h["beta"])
    save("spurious", {"regime_poisson_true_n": 0.0, "n_events": len(ev), "fit": fit,
                      "control_true": {"mu": 0.5, "n": 0.6, "beta": 2.0}, "control_fit": fit_h})


# ---------- Part 5: speed ----------
def part_speed_python():
    rng = np.random.default_rng(5)
    out = {}
    for n_ev in (2000, 5000, 10000):
        t = np.sort(rng.uniform(0, n_ev, n_ev))
        t1 = time.time(); a = loglik_exp_naive(t, float(n_ev), 0.5, 0.5, 1.0); dt_n = time.time() - t1
        t1 = time.time(); b = loglik_exp(t, float(n_ev), 0.5, 0.5, 1.0); dt_r = time.time() - t1
        out[f"N{n_ev}"] = {"naive_s": dt_n, "recursion_s": dt_r, "abs_diff": abs(a - b)}
    for n_ev in (100000, 1000000):
        t = np.sort(rng.uniform(0, n_ev, n_ev))
        t1 = time.time(); loglik_exp(t, float(n_ev), 0.5, 0.5, 1.0)
        out[f"N{n_ev}_recursion_python_s"] = time.time() - t1
    t = simulate_exp_hawkes(0.5, 0.6, 2.0, 80000.0, np.random.default_rng(6))
    t1 = time.time(); f = fit_exp_mle(t, 80000.0)
    out["full_mle_python"] = {"n_events": len(t), "seconds": time.time() - t1, "fit": f}
    out["rss_mb"] = rss_mb()
    save("speed_python", out)


def part_speed_tick():
    from tick.hawkes import HawkesEM, HawkesExpKern, HawkesSumExpKern, SimuHawkesExpKernels
    # 4-D: [MO buy, MO sell, LO bid, LO ask] ; illustrative parameters only
    adj = np.array([[0.45, 0.05, 0.00, 0.05],
                    [0.05, 0.45, 0.05, 0.00],
                    [0.10, 0.00, 0.30, 0.05],
                    [0.00, 0.10, 0.05, 0.30]])
    rho = float(max(abs(np.linalg.eigvals(adj))))
    beta = 5.0
    base = np.array([0.4, 0.4, 2.0, 2.0])
    lam = np.linalg.solve(np.eye(4) - adj, base)
    end = 1.0e6 / lam.sum()
    out = {"spectral_radius": rho, "stationary_rates": lam.tolist(), "end_time": end, "threads": N_THREADS}
    sim = SimuHawkesExpKernels(adjacency=adj, decays=beta, baseline=base, end_time=end, verbose=False, seed=7)
    t1 = time.time(); sim.simulate(); out["simulate_s"] = time.time() - t1
    ts = sim.timestamps
    out["n_events"] = int(sum(len(x) for x in ts))
    for gofit, solver in (("least-squares", "agd"), ("likelihood", "bfgs")):
        try:
            lrn = HawkesExpKern(decays=beta, gofit=gofit, solver=solver, penalty="none",
                                max_iter=200, tol=1e-6, verbose=False)
            t1 = time.time(); lrn.fit(ts); dt = time.time() - t1
            out[f"expkern_{gofit}"] = {"seconds": dt, "adjacency_hat": lrn.adjacency.round(3).tolist(),
                                       "baseline_hat": lrn.baseline.round(3).tolist(),
                                       "max_abs_err_adj": float(np.abs(lrn.adjacency - adj).max())}
        except Exception as e:  # record, do not hide
            out[f"expkern_{gofit}"] = {"error": repr(e)[:300]}
    try:
        lrn = HawkesSumExpKern(decays=[0.5, 5.0, 50.0], penalty="none", max_iter=200, verbose=False)
        t1 = time.time(); lrn.fit(ts); dt = time.time() - t1
        out["sumexp_3decays_ls"] = {"seconds": dt,
                                    "norm_hat": lrn.adjacency.sum(axis=2).round(3).tolist()}
    except Exception as e:
        out["sumexp_3decays_ls"] = {"error": repr(e)[:300]}
    try:
        t_one = [ts[0][: 100000]]
        em = HawkesEM(kernel_support=5.0, kernel_size=25, n_threads=N_THREADS, max_iter=100, verbose=False)
        t1 = time.time(); em.fit(t_one); dt = time.time() - t1
        norm = float(em.get_kernel_norms()[0, 0])
        out["em_nonparam_1d_100k"] = {"seconds": dt, "norm_hat": norm, "n_events": len(t_one[0])}
    except Exception as e:
        out["em_nonparam_1d_100k"] = {"error": repr(e)[:300]}
    out["rss_mb"] = rss_mb()
    save("speed_tick", out)


PARTS = [("hand", part_hand), ("hb_estimator", part_hb), ("fill_prob", part_fill),
         ("spurious", part_spurious), ("speed_python", part_speed_python), ("speed_tick", part_speed_tick)]

if __name__ == "__main__":
    for key, fn in PARTS:
        if key in RES:
            print(key, "skip (done)")
            continue
        t0 = time.time()
        fn()
        print(key, f"{time.time() - t0:.1f}s rss={rss_mb():.0f}MB", flush=True)
