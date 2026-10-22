"""C2_Filter compute probes on SYNTHETIC data only (no market data is read).

Measures wall time on this laptop for:
  1. scalar Kalman filter, local-level model (python loop and steady-state lfilter), plus MLE of (q, r)
  2. 2-state Gaussian HMM: forward filter and Baum-Welch iterations (numpy, loop over t)
  3. bootstrap particle filter for the canonical SV model (numpy, vectorised over particles; optional torch GPU)
Writes C2F_bench_results.json next to this file. Run with: nice -n 10 uv run python -I C2F_bench.py
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

os.nice(10)
os.environ.setdefault("OMP_NUM_THREADS", "4")

import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402
from scipy.signal import lfilter  # noqa: E402

OUT = Path(__file__).with_name("C2F_bench_results.json")
RNG = np.random.default_rng(20261021)


def sim_local_level(n: int, q: float, r: float) -> np.ndarray:
    x = np.cumsum(RNG.normal(0.0, np.sqrt(q), n))
    return x + RNG.normal(0.0, np.sqrt(r), n)


def kf_local_level(y: np.ndarray, q: float, r: float) -> tuple[np.ndarray, float]:
    """Scalar Kalman filter; returns filtered means and the Gaussian log-likelihood."""
    n = y.size
    xf = np.empty(n)
    x, p = y[0], r  # diffuse-ish start at first observation
    ll = 0.0
    log2pi = np.log(2 * np.pi)
    for t in range(1, n):
        pp = p + q  # time update (A = 1)
        f = pp + r  # innovation variance
        v = y[t] - x  # innovation
        k = pp / f  # Kalman gain
        x = x + k * v
        p = (1 - k) * pp
        ll += -0.5 * (log2pi + np.log(f) + v * v / f)
        xf[t] = x
    xf[0] = y[0]
    return xf, ll


def kf_steady_state(y: np.ndarray, q: float, r: float) -> np.ndarray:
    ppred = (q + np.sqrt(q * q + 4 * q * r)) / 2
    k = ppred / (ppred + r)
    # x_t = (1-k) x_{t-1} + k y_t : an exponential smoother
    return lfilter([k], [1, -(1 - k)], y, zi=[(1 - k) * y[0]])[0]


def ss_negll(theta: np.ndarray, dy: np.ndarray) -> float:
    """Negative log-likelihood of the MA(1) implied by the steady-state local level model,
    via its exact Gaussian moments approximated with the steady-state innovations form."""
    q, r = np.exp(theta)
    ppred = (q + np.sqrt(q * q + 4 * q * r)) / 2
    f = ppred + r
    k = ppred / f
    # innovations v_t = y_t - xhat_{t|t-1}; in differences: v_t - (1-k) v_{t-1} = dy_t
    v = lfilter([1.0], [1.0, -(1 - k)], dy)
    return 0.5 * (dy.size * (np.log(2 * np.pi) + np.log(f)) + np.sum(v * v) / f)


def hmm_sim(n: int, p11: float, p22: float, s1: float, s2: float) -> tuple[np.ndarray, np.ndarray]:
    s = np.empty(n, dtype=np.int8)
    s[0] = 0
    u = RNG.random(n)
    for t in range(1, n):
        stay = p11 if s[t - 1] == 0 else p22
        s[t] = s[t - 1] if u[t] < stay else 1 - s[t - 1]
    sig = np.where(s == 0, s1, s2)
    return RNG.normal(0, 1, n) * sig, s


def gauss_pdf(y: np.ndarray, sig: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * (y[:, None] / sig[None, :]) ** 2) / (np.sqrt(2 * np.pi) * sig[None, :])


def hmm_forward(eta: np.ndarray, P: np.ndarray, xi0: np.ndarray) -> tuple[np.ndarray, float]:
    """Hamilton filter. P[i, j] = Pr(s_t = j | s_{t-1} = i). Returns filtered probs and loglik."""
    n, k = eta.shape
    xi = np.empty((n, k))
    prev = xi0
    ll = 0.0
    for t in range(n):
        pred = prev @ P
        joint = pred * eta[t]
        f = joint.sum()
        ll += np.log(f)
        prev = joint / f
        xi[t] = prev
    return xi, ll


def hmm_backward_smooth(eta: np.ndarray, P: np.ndarray, xi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Scaled backward pass (uses FUTURE data). Returns smoothed probs and expected transition counts."""
    n, k = eta.shape
    beta = np.ones(k)
    sm = np.empty((n, k))
    sm[-1] = xi[-1]
    trans = np.zeros((k, k))
    for t in range(n - 2, -1, -1):
        b = eta[t + 1] * beta
        tmp = (xi[t][:, None] * P) * b[None, :]
        z = tmp.sum()
        trans += tmp / z
        beta = (P @ b)
        beta = beta / beta.sum()
        g = xi[t] * beta
        sm[t] = g / g.sum()
    return sm, trans


def baum_welch(y: np.ndarray, iters: int) -> dict:
    P = np.array([[0.95, 0.05], [0.10, 0.90]])
    sig = np.array([np.std(y) * 0.5, np.std(y) * 2.0])
    xi0 = np.array([0.5, 0.5])
    lls = []
    for _ in range(iters):
        eta = gauss_pdf(y, sig)
        xi, ll = hmm_forward(eta, P, xi0)
        sm, trans = hmm_backward_smooth(eta, P, xi)
        lls.append(ll)
        P = trans / trans.sum(axis=1, keepdims=True)
        sig = np.sqrt((sm * y[:, None] ** 2).sum(axis=0) / sm.sum(axis=0))
    return {"P": P.tolist(), "sig": sig.tolist(), "loglik_path": [round(v, 2) for v in lls]}


def sv_sim(n: int, alpha: float, sigma: float, beta: float) -> np.ndarray:
    x = np.empty(n)
    x[0] = RNG.normal(0, sigma / np.sqrt(1 - alpha ** 2))
    for t in range(1, n):
        x[t] = alpha * x[t - 1] + sigma * RNG.normal()
    return beta * np.exp(x / 2) * RNG.normal(0, 1, n)


def bootstrap_pf(y: np.ndarray, n_part: int, alpha: float, sigma: float, beta: float) -> tuple[float, float]:
    x = RNG.normal(0, sigma / np.sqrt(1 - alpha ** 2), n_part)
    ll = 0.0
    resamples = 0
    for t in range(y.size):
        x = alpha * x + sigma * RNG.normal(size=n_part)
        var = beta ** 2 * np.exp(x)
        logw = -0.5 * (np.log(2 * np.pi * var) + y[t] ** 2 / var)
        m = logw.max()
        w = np.exp(logw - m)
        sw = w.sum()
        ll += m + np.log(sw / n_part)
        w /= sw
        ess = 1.0 / np.sum(w * w)
        if ess < n_part / 2:
            idx = np.searchsorted(np.cumsum(w), (RNG.random() + np.arange(n_part)) / n_part)
            x = x[np.minimum(idx, n_part - 1)]
            resamples += 1
    return ll, resamples / y.size


def timed(fn, *a, **k):
    t0 = time.perf_counter()
    out = fn(*a, **k)
    return out, time.perf_counter() - t0


def main() -> None:
    res: dict = {"note": "synthetic data only; wall seconds on ThinkPad (nice 10)"}
    # 1. Kalman
    q, r = 0.01, 0.015625
    y = sim_local_level(1_000_000, q, r)
    (_, ll), t_loop = timed(kf_local_level, y, q, r)
    res["kf_loop_1e6_s"] = round(t_loop, 3)
    y10 = sim_local_level(10_000_000, q, r)
    _, t_ss = timed(kf_steady_state, y10, q, r)
    res["kf_steady_lfilter_1e7_s"] = round(t_ss, 3)
    dy = np.diff(y)
    opt, t_mle = timed(minimize, ss_negll, np.log([0.02, 0.02]), args=(dy,), method="Nelder-Mead")
    res["kf_mle_1e6"] = {"q_hat": float(np.exp(opt.x[0])), "r_hat": float(np.exp(opt.x[1])),
                         "true_q": q, "true_r": r, "seconds": round(t_mle, 2), "nfev": int(opt.nfev)}
    rho1 = float(np.corrcoef(dy[1:], dy[:-1])[0, 1])
    res["kf_mom_rho1"] = {"sample": round(rho1, 4), "theory": round(-r / (q + 2 * r), 4)}
    # 2. HMM
    yh, s = hmm_sim(200_000, 0.995, 0.98, 1.0, 3.0)
    eta = gauss_pdf(yh, np.array([1.0, 3.0]))
    P = np.array([[0.995, 0.005], [0.02, 0.98]])
    (xi, llh), t_fwd = timed(hmm_forward, eta, P, np.array([0.8, 0.2]))
    res["hmm_forward_2e5_s"] = round(t_fwd, 3)
    (sm, _), t_bwd = timed(hmm_backward_smooth, eta, P, xi)
    res["hmm_backward_2e5_s"] = round(t_bwd, 3)
    acc_f = float(np.mean((xi[:, 1] > 0.5) == (s == 1)))
    acc_s = float(np.mean((sm[:, 1] > 0.5) == (s == 1)))
    res["hmm_classification_accuracy"] = {"filtered": round(acc_f, 4), "smoothed_lookahead": round(acc_s, 4)}
    bw, t_bw = timed(baum_welch, yh, 10)
    res["hmm_baum_welch_10iter_2e5"] = {"seconds": round(t_bw, 2), **bw,
                                        "true": {"P": [[0.995, 0.005], [0.02, 0.98]], "sig": [1.0, 3.0]}}
    # 3. particle filter
    ysv = sv_sim(100_000, 0.98, 0.15, 1.0)
    (llpf, rr), t_pf = timed(bootstrap_pf, ysv, 1000, 0.98, 0.15, 1.0)
    res["pf_sv_1e5_steps_1000_particles"] = {"seconds": round(t_pf, 2), "loglik": round(llpf, 1),
                                             "resample_rate": round(rr, 3)}
    try:
        import torch
        if torch.cuda.is_available():
            dev = torch.device("cuda")
            yt = torch.tensor(ysv[:10_000], device=dev, dtype=torch.float32)
            npart = 100_000
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            x = torch.randn(npart, device=dev) * 0.15 / (1 - 0.98 ** 2) ** 0.5
            for t in range(yt.numel()):
                x = 0.98 * x + 0.15 * torch.randn(npart, device=dev)
                logw = -0.5 * (x + yt[t] ** 2 * torch.exp(-x))
                w = torch.softmax(logw, 0)
                idx = torch.multinomial(w, npart, replacement=True)
                x = x[idx]
            torch.cuda.synchronize()
            res["pf_sv_gpu_1e4_steps_1e5_particles_s"] = round(time.perf_counter() - t0, 2)
            res["gpu_peak_mem_MB"] = round(torch.cuda.max_memory_allocated() / 1e6, 1)
    except Exception as exc:  # report, do not hide
        res["gpu_probe_error"] = repr(exc)
    OUT.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "hmm_baum_welch_10iter_2e5"}))


if __name__ == "__main__":
    main()
