"""C2_StatsRMT worked examples and laptop timings (synthetic data only; no market data read).

Writes C2_StatsRMT_examples.json next to this script and prints a short summary.
Run: nice -n 10 uv run python -I C2_StatsRMT_examples.py
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
os.nice(10)

import json
import math
import time
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.spatial import cKDTree
from scipy.special import digamma
from sklearn.covariance import LedoitWolf

OUT = Path(__file__).with_name("C2_StatsRMT_examples.json")
RNG = np.random.default_rng(20261021)
EULER_GAMMA = 0.5772156649
RES: dict = {}


def mp_edges(n_vars: int, n_obs: int, sigma2: float = 1.0) -> dict:
    q = n_vars / n_obs
    return {"N": n_vars, "T": n_obs, "q": q,
            "lambda_minus": sigma2 * (1 - math.sqrt(q)) ** 2,
            "lambda_plus": sigma2 * (1 + math.sqrt(q)) ** 2}


def expected_max_sr(n_trials: float, var_sr: float) -> float:
    """Bailey and Lopez de Prado (2014) expected maximum Sharpe ratio of n_trials null trials."""
    if n_trials <= 1:
        return 0.0
    z1 = stats.norm.ppf(1 - 1 / n_trials)
    z2 = stats.norm.ppf(1 - 1 / (n_trials * math.e))
    return math.sqrt(var_sr) * ((1 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)


# ---------------------------------------------------------------- A. MP edges
def part_a() -> None:
    RES["A_mp_edges"] = {
        "laloux_sp500": mp_edges(406, 1309),
        "roots45_4y_daily": mp_edges(45, 1000),
        "trials538_5y_daily": mp_edges(538, 1250),
        "one_contract_40_book_fields_1s_84d": mp_edges(40, 84 * 23400),
    }


# ------------------------------------------- B. effective number of trials
def block_corr(m: int, n_clusters: int, rho_in: float, rho_all: float) -> np.ndarray:
    c = np.full((m, m), rho_all)
    size = m // n_clusters
    for k in range(n_clusters):
        sl = slice(k * size, (k + 1) * size)
        c[sl, sl] = rho_in
    np.fill_diagonal(c, 1.0)
    return c


def eff_counts(eig: np.ndarray, m: int, t: int, corr: np.ndarray) -> dict:
    lam_plus = mp_edges(m, t)["lambda_plus"]
    p = eig / eig.sum()
    p = p[p > 0]
    rho_bar = (corr.sum() - m) / (m * (m - 1))
    return {"n_above_mp_edge": int((eig > lam_plus).sum()),
            "entropy_eff_rank": float(math.exp(-(p * np.log(p)).sum())),
            "participation_ratio": float(eig.sum() ** 2 / (eig ** 2).sum()),
            "bailey_ldp_rho_bar": float(rho_bar),
            "bailey_ldp_N_hat": float(rho_bar + (1 - rho_bar) * m),
            "mp_lambda_plus": lam_plus}


def part_b() -> None:
    m, t, reps = 200, 750, 400
    corr = block_corr(m, 5, 0.6, 0.1)
    chol = np.linalg.cholesky(corr)
    max_sr, var_sr, effs = [], [], []
    t0 = time.perf_counter()
    for r in range(reps):
        x = RNG.standard_normal((t, m)) @ chol.T  # null: zero mean daily returns
        sr = x.mean(0) / x.std(0)
        max_sr.append(sr.max())
        var_sr.append(sr.var())
        if r < 20:
            ec = np.corrcoef(x, rowvar=False)
            effs.append(eff_counts(np.linalg.eigvalsh(ec), m, t, ec))
    elapsed = time.perf_counter() - t0
    mean_max, mean_var = float(np.mean(max_sr)), float(np.mean(var_sr))
    eff_mean = {k: float(np.mean([e[k] for e in effs])) for k in effs[0]}
    # N that reproduces the Monte Carlo expected max under the DSR formula
    grid = np.arange(1, m + 1)
    implied = int(grid[np.argmin([abs(expected_max_sr(n, mean_var) - mean_max) for n in grid])])
    true_eig = np.linalg.eigvalsh(corr)
    RES["B_effective_trials"] = {
        "M": m, "T": t, "reps": reps, "design": "5 clusters of 40, rho_in 0.6, rho_all 0.1, null SR 0",
        "mc_mean_max_daily_sr": mean_max, "mc_mean_cross_sectional_var_sr": mean_var,
        "formula_E_max_with_N_M": expected_max_sr(m, mean_var),
        "formula_E_max_with_each_estimate": {k: expected_max_sr(eff_mean[k], mean_var)
                                             for k in ("n_above_mp_edge", "entropy_eff_rank",
                                                       "participation_ratio", "bailey_ldp_N_hat")},
        "N_implied_by_mc": implied, "effective_counts_mean_of_20": eff_mean,
        "true_corr_top_eigs": [float(v) for v in true_eig[-6:][::-1]],
        "seconds": elapsed}


# --------------------------------------------- C. covariance cleaning race
def clip_mp(s: np.ndarray, t: int) -> np.ndarray:
    d = np.sqrt(np.diag(s))
    c = s / np.outer(d, d)
    lam, u = np.linalg.eigh(c)
    lp = mp_edges(len(lam), t)["lambda_plus"]
    noise = lam < lp
    lam2 = lam.copy()
    lam2[noise] = lam[noise].mean()  # trace preserving (Bun et al. eq. 7.55)
    c2 = (u * lam2) @ u.T
    return c2 * np.outer(d, d)


def analytic_nls(x: np.ndarray) -> np.ndarray:
    """Ledoit and Wolf (2020) analytical nonlinear shrinkage, p <= n case, data already demeaned."""
    n, p = x.shape
    s = x.T @ x / n
    lam, u = np.linalg.eigh(s)
    lam = np.maximum(lam, 1e-12)
    h = n ** (-1 / 3)
    hl = h * lam[None, :]
    xx = (lam[:, None] - lam[None, :]) / hl
    f = (3 / 4 / math.sqrt(5)) * np.mean(np.maximum(1 - xx ** 2 / 5, 0) / hl, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        hf = (-3 / 10 / math.pi) * xx + (3 / 4 / math.sqrt(5) / math.pi) * (1 - xx ** 2 / 5) * \
            np.log(np.abs((math.sqrt(5) - xx) / (math.sqrt(5) + xx)))
    edge = np.isclose(np.abs(xx), math.sqrt(5))
    hf[edge] = (-3 / 10 / math.pi) * xx[edge]
    hft = np.mean(hf / hl, axis=1)
    c = p / n
    d = lam / ((math.pi * c * lam * f) ** 2 + (1 - c - math.pi * c * lam * hft) ** 2)
    return (u * d) @ u.T


def rie(x: np.ndarray) -> np.ndarray:
    """Bun-Bouchaud-Potters RIE (eq. 6.5 form) with eta = N^-1/2, on the sample covariance."""
    n, p = x.shape
    s = x.T @ x / n
    lam, u = np.linalg.eigh(s)
    q = p / n
    z = lam - 1j * p ** -0.5
    g = np.mean(1.0 / (z[:, None] - lam[None, :]), axis=1)
    xi = lam / np.abs(1 - q + q * z * g) ** 2
    xi *= lam.sum() / xi.sum()  # keep the trace
    return (u * xi) @ u.T


def gmv_oos_var(est: np.ndarray, sigma: np.ndarray) -> float:
    ones = np.ones(len(sigma))
    w = np.linalg.solve(est, ones)
    w /= w.sum()
    return float(w @ sigma @ w)


def part_c() -> None:
    p, n, reps = 100, 200, 60
    pop = np.concatenate([np.full(80, 1.0), np.full(15, 3.0), np.full(5, 10.0)])
    q_rot, _ = np.linalg.qr(RNG.standard_normal((p, p)))
    sigma = (q_rot * pop) @ q_rot.T
    chol = np.linalg.cholesky(sigma)
    oracle = 1.0 / (np.ones(p) @ np.linalg.solve(sigma, np.ones(p)))
    names = ["sample", "clip_mp", "ledoit_wolf_linear", "analytic_nonlinear", "rie"]
    out = {k: [] for k in names}
    t_used = {k: 0.0 for k in names}
    for _ in range(reps):
        x = RNG.standard_normal((n, p)) @ chol.T
        x = x - x.mean(0)
        for k in names:
            t0 = time.perf_counter()
            if k == "sample":
                est = x.T @ x / n
            elif k == "clip_mp":
                est = clip_mp(x.T @ x / n, n)
            elif k == "ledoit_wolf_linear":
                est = LedoitWolf(assume_centered=True).fit(x).covariance_
            elif k == "analytic_nonlinear":
                est = analytic_nls(x)
            else:
                est = rie(x)
            t_used[k] += time.perf_counter() - t0
            out[k].append(gmv_oos_var(est, sigma) / oracle)
    lw_shrink = LedoitWolf(assume_centered=True).fit(x).shrinkage_
    RES["C_cleaning_race"] = {
        "p": p, "n": n, "q": p / n, "reps": reps,
        "population_eigs": "80 x 1, 15 x 3, 5 x 10 (random rotation)",
        "gmv_oos_variance_over_oracle_mean": {k: float(np.mean(v)) for k, v in out.items()},
        "gmv_oos_variance_over_oracle_se": {k: float(np.std(v) / math.sqrt(reps)) for k, v in out.items()},
        "ms_per_estimate": {k: 1000 * v / reps for k, v in t_used.items()},
        "lw_shrinkage_intensity_last_rep": float(lw_shrink)}


# ---------------------------------------------- D. James-Stein / EB on Sharpe
def eb_normal(z: np.ndarray, se: float) -> dict:
    k = len(z)
    zbar = float(z.mean())
    ss = float(((z - zbar) ** 2).sum())
    b_js = min(1.0, (k - 3) * se ** 2 / ss)  # Efron-Morris positive-part, shrink to grand mean
    tau2 = max(0.0, ss / (k - 1) - se ** 2)  # method of moments
    kappa = tau2 / (tau2 + se ** 2)
    return {"K": k, "zbar": zbar, "sum_sq_dev": ss, "se": se,
            "js_shrink_B": b_js, "js_estimates": [zbar + (1 - b_js) * (v - zbar) for v in z],
            "tau2_mom": tau2, "kappa": kappa,
            "eb_estimates": [zbar + kappa * (v - zbar) for v in z],
            "dsr_expected_max_null_annual_sr": expected_max_sr(k, se ** 2)}


def part_d() -> None:
    z = np.array([1.9, 1.2, 0.8, 0.5, 0.3, 0.1, -0.2, -0.4, -0.6, -0.9, -1.1, -1.5])
    se_84d = math.sqrt(252 / 84)   # SE of an annualized Sharpe from 84 daily obs (iid normal approx)
    se_1000d = math.sqrt(252 / 1000)
    RES["D_eb_sharpe"] = {"observed_annual_sr": z.tolist(),
                          "T84": eb_normal(z, se_84d),
                          "T1000": eb_normal(z, se_1000d)}
    # Two-level: 3 families x 4 configs of a markout mean (ticks), common SE
    fam = np.array([[0.30, 0.22, 0.18, 0.10], [0.05, 0.02, -0.04, -0.08], [-0.10, -0.12, -0.20, -0.25]])
    se = 0.08
    fam_means = fam.mean(1)
    within_ss = float(((fam - fam_means[:, None]) ** 2).sum())
    tau_w2 = max(0.0, within_ss / (fam.size - len(fam)) - se ** 2)
    k_w = tau_w2 / (tau_w2 + se ** 2)
    se_fam = se / 2  # SE of a family mean of 4 independent configs
    tau_b2 = max(0.0, float(fam_means.var(ddof=1)) - se_fam ** 2)
    k_b = tau_b2 / (tau_b2 + se_fam ** 2)  # family means shrunk toward 0 (prior mean 0)
    post_fam = k_b * fam_means
    post = post_fam[:, None] + k_w * (fam - fam_means[:, None])
    RES["D_two_level"] = {"obs": fam.tolist(), "se": se, "tau_within2": tau_w2, "kappa_within": k_w,
                          "tau_between2": tau_b2, "kappa_between": k_b,
                          "posterior_family_means": post_fam.tolist(), "posterior": post.round(4).tolist()}


# ---------------------------------------------------------------- E. BMA/BIC
def part_e() -> None:
    n = 2000
    imb = RNG.uniform(-1, 1, n)
    spread = RNG.integers(1, 3, n).astype(float)
    y = -0.15 * imb + RNG.normal(0, 1.5, n)  # synthetic 60 s markout in ticks
    designs = {"M0_const": np.ones((n, 1)),
               "M1_imb": np.column_stack([np.ones(n), imb]),
               "M2_imb_spread": np.column_stack([np.ones(n), imb, spread])}
    bic, beta_imb = {}, {}
    for k, xm in designs.items():
        b, *_ = np.linalg.lstsq(xm, y, rcond=None)
        rss = float(((y - xm @ b) ** 2).sum())
        bic[k] = n * math.log(rss / n) + xm.shape[1] * math.log(n)
        beta_imb[k] = float(b[1]) if xm.shape[1] > 1 else 0.0
    bmin = min(bic.values())
    w = {k: math.exp(-0.5 * (v - bmin)) for k, v in bic.items()}
    tot = sum(w.values())
    w = {k: v / tot for k, v in w.items()}
    RES["E_bma"] = {"n": n, "true_beta_imb": -0.15, "noise_sd": 1.5, "bic": bic, "weights": w,
                    "beta_imb_by_model": beta_imb,
                    "bma_beta_imb": sum(w[k] * beta_imb[k] for k in w)}


# ------------------------------------------------------------ F. entropies
def plugin_entropy(sym: np.ndarray, base: float = 2.0) -> float:
    _, c = np.unique(sym, return_counts=True)
    p = c / c.sum()
    return float(-(p * np.log(p)).sum() / math.log(base))


def block_entropy_rate(sym: np.ndarray, k: int, alpha: int) -> float:
    def hk(kk):
        if kk == 0:
            return 0.0
        codes = np.zeros(len(sym) - kk + 1, dtype=np.int64)
        for j in range(kk):
            codes = codes * alpha + sym[j:len(sym) - kk + 1 + j]
        return plugin_entropy(codes)
    return hk(k + 1) - hk(k)


def lz_kontoyiannis(sym: np.ndarray) -> float:
    """H_lz = n log2 n / sum_i Lambda_i (Kontoyiannis estimator as written in Fiedor 2014 eq. 5)."""
    s = bytes((sym + 65).astype(np.uint8))
    n = len(s)
    total, lam = 1, 1
    for i in range(1, n):
        lam = max(1, lam - 1)
        while i + lam <= n and s.find(s[i:i + lam], 0, i + lam - 1) != -1:
            lam += 1
        total += lam
    return n * math.log2(n) / total


def markov_chain(n: int, p_mat: np.ndarray) -> np.ndarray:
    cum = np.cumsum(p_mat, axis=1)
    u = RNG.random(n)
    out = np.empty(n, dtype=np.int64)
    s = 1
    for t in range(n):
        s = int(np.searchsorted(cum[s], u[t]))
        out[t] = s
    return out


def apen_sampen(x: np.ndarray, m: int = 2, r_mult: float = 0.2) -> tuple:
    r = r_mult * x.std()
    n = len(x)

    def phi_counts(mm):
        emb = np.lib.stride_tricks.sliding_window_view(x, mm)[: n - m]
        tree = cKDTree(emb)
        cnt = np.array([len(v) for v in tree.query_ball_point(emb, r, p=np.inf)])  # includes self
        return cnt, len(emb)
    cm, nm = phi_counts(m)
    cm1, _ = phi_counts(m + 1)
    apen = float(np.mean(np.log(cm / nm)) - np.mean(np.log(cm1 / nm)))
    sampen = float(-math.log((cm1 - 1).sum() / (cm - 1).sum()))
    return apen, sampen


def part_f() -> None:
    res = {}
    p3 = np.array([0.1, 0.8, 0.1])
    res["H_iid_3sym_bits"] = float(-(p3 * np.log2(p3)).sum())
    # bounce chain on {down=0, flat=1, up=2}: after a move, a reversal is more likely
    pm = np.array([[0.05, 0.75, 0.20], [0.10, 0.80, 0.10], [0.20, 0.75, 0.05]])
    evals, evecs = np.linalg.eig(pm.T)
    pi = np.real(evecs[:, np.argmin(np.abs(evals - 1))])
    pi = pi / pi.sum()
    h_rate = float(-(pi[:, None] * pm * np.log2(pm)).sum())
    res["bounce_chain"] = {"P": pm.tolist(), "stationary": pi.tolist(),
                           "true_entropy_rate_bits": h_rate,
                           "marginal_entropy_bits": float(-(pi * np.log2(pi)).sum())}
    est = {}
    for n in (2_000, 20_000, 200_000):
        sym = markov_chain(n, pm)
        t0 = time.perf_counter()
        lz = lz_kontoyiannis(sym) if n <= 200_000 else None
        t_lz = time.perf_counter() - t0
        est[str(n)] = {"plugin_H1": plugin_entropy(sym),
                       "block_rate_k1": block_entropy_rate(sym, 1, 3),
                       "block_rate_k4": block_entropy_rate(sym, 4, 3),
                       "block_rate_k8": block_entropy_rate(sym, 8, 3),
                       "lz_kontoyiannis": lz, "lz_seconds": t_lz,
                       "miller_madow_k4_bias_bits": (3 ** 5 - 1) / (2 * n * math.log(2))}
    res["estimates"] = est
    sym_iid = RNG.choice(3, size=200_000, p=p3)
    res["iid_check_200k"] = {"block_rate_k4": block_entropy_rate(sym_iid, 4, 3),
                             "lz_kontoyiannis": lz_kontoyiannis(sym_iid)}
    # ApEn / SampEn: iid vs AR(1) phi=0.5, n=2000 and timing n=20000
    e = RNG.standard_normal(20_000)
    ar = np.empty_like(e)
    ar[0] = e[0]
    for t in range(1, len(e)):
        ar[t] = 0.5 * ar[t - 1] + e[t]
    ap = {}
    for name, ser in (("iid", e), ("ar1_0.5", ar)):
        for n in (2_000, 20_000):
            t0 = time.perf_counter()
            a, s = apen_sampen(ser[:n])
            ap[f"{name}_{n}"] = {"apen": a, "sampen": s, "seconds": time.perf_counter() - t0}
    res["apen_sampen"] = ap
    RES["F_entropy"] = res


# ---------------------------------------------------------------- G. MI / TE
def te_plugin(src: np.ndarray, dst: np.ndarray, alpha: int) -> float:
    """TE src->dst in nats with k = l = 1 (Schreiber 2000 eq. 4)."""
    y1, y0, x0 = dst[1:], dst[:-1], src[:-1]
    n = len(y1)
    j3 = np.zeros((alpha, alpha, alpha))
    np.add.at(j3, (y1, y0, x0), 1)
    p3 = j3 / n
    p_y0x0 = p3.sum(0)
    p_y1y0 = p3.sum(2)
    p_y0 = p3.sum((0, 2))
    with np.errstate(divide="ignore", invalid="ignore"):
        term = p3 * np.log(p3 * p_y0[None, :, None] / (p_y1y0[:, :, None] * p_y0x0[None, :, :]))
    return float(np.nansum(term))


def ksg_mi(x: np.ndarray, y: np.ndarray, k: int = 3) -> float:
    """Kraskov-Stoegbauer-Grassberger estimator 1 (their eq. 8), max-norm."""
    n = len(x)
    xy = np.column_stack([x, y])
    d, _ = cKDTree(xy).query(xy, k + 1, p=np.inf)
    eps = d[:, -1]
    tx, ty = cKDTree(x[:, None]), cKDTree(y[:, None])
    nx = np.array([len(v) - 1 for v in tx.query_ball_point(x[:, None], eps - 1e-12, p=np.inf)])
    ny = np.array([len(v) - 1 for v in ty.query_ball_point(y[:, None], eps - 1e-12, p=np.inf)])
    return float(digamma(k) - np.mean(digamma(nx + 1) + digamma(ny + 1)) + digamma(n))


def part_g() -> None:
    res = {}
    for n, follow in ((20_000, 0.05), (200_000, 0.02)):
        lead = RNG.choice(3, size=n, p=[0.1, 0.8, 0.1])
        noise = RNG.choice(3, size=n, p=[0.1, 0.8, 0.1])
        copy = RNG.random(n) < follow
        foll = np.where(copy, np.roll(lead, 1), noise)
        foll[0] = noise[0]
        te_xy, te_yx = te_plugin(lead, foll, 3), te_plugin(foll, lead, 3)
        nu = 3 * (3 - 1) * (3 - 1)  # Bongiorno-Challet eq. 6 with n_A = n_B = 3, k = 1
        shuf = [te_plugin(RNG.permutation(lead), foll, 3) for _ in range(100)]
        res[f"n{n}_copy{follow}"] = {
            "TE_lead_to_follow_nats": te_xy, "TE_follow_to_lead_nats": te_yx,
            "chi2_stat_2nTE": 2 * (n - 1) * te_xy, "nu": nu,
            "p_chi2_lead_to_follow": float(stats.chi2.sf(2 * (n - 1) * te_xy, nu)),
            "p_chi2_follow_to_lead": float(stats.chi2.sf(2 * (n - 1) * te_yx, nu)),
            "shuffle_mean_TE": float(np.mean(shuf)), "shuffle_p95_TE": float(np.quantile(shuf, 0.95)),
            "null_bias_expected_nu_over_2n": nu / (2 * (n - 1))}
    # sample size for TE detection: noncentral chi2 power
    need = {}
    for nu in (2, 12):  # binary k=l=1: (2-1)*2*(2-1) = 2; three symbols: (3-1)*3*(3-1) = 12
        crit = stats.chi2.isf(0.05, nu)
        for te in (1e-4, 1e-3, 1e-2):
            lo, hi = 10, 10 ** 9
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if stats.ncx2.sf(crit, nu, 2 * mid * te) >= 0.8:
                    hi = mid
                else:
                    lo = mid
            need[f"nu{nu}_te{te}"] = hi
    res["n_for_80pct_power_alpha05"] = need
    # KSG check on Gaussian rho=0.3: true MI = -0.5 ln(1-rho^2)
    rho = 0.3
    ksg = {}
    for n in (2_000, 20_000, 100_000):
        x = RNG.standard_normal(n)
        y = rho * x + math.sqrt(1 - rho ** 2) * RNG.standard_normal(n)
        t0 = time.perf_counter()
        ksg[str(n)] = {"ksg": ksg_mi(x, y), "seconds": time.perf_counter() - t0}
    res["ksg_gauss_rho0.3"] = {"true_mi_nats": -0.5 * math.log(1 - rho ** 2), "est": ksg}
    RES["G_mi_te"] = res


# ---------------------------------------------------------------- H. sizing
def part_h() -> None:
    res = {}
    z = stats.norm.ppf
    sd, delta = 1.5, 0.1
    for k in (1, 12, 50):
        za = z(1 - 0.05 / (2 * k))
        res[f"fills_needed_K{k}"] = math.ceil(((za + z(0.8)) * sd / delta) ** 2)
    res["assumptions"] = "60 s markout sd 1.5 ticks (assumed, not measured), effect 0.1 tick, two-sided, Bonferroni over K, power 0.8"
    t = {}
    for m in (538, 2000):
        a = RNG.standard_normal((m + 50, m))
        c = np.corrcoef(a, rowvar=False)
        t0 = time.perf_counter()
        np.linalg.eigh(c)
        t[f"eigh_{m}"] = time.perf_counter() - t0
    big = RNG.standard_normal((1_000_000, 40)).astype(np.float64)
    t0 = time.perf_counter()
    np.cov(big, rowvar=False)
    t["cov_1e6_by_40"] = time.perf_counter() - t0
    del big
    res["seconds"] = t
    RES["H_sizing"] = res


if __name__ == "__main__":
    for fn in (part_a, part_b, part_c, part_d, part_e, part_f, part_g, part_h):
        t0 = time.perf_counter()
        fn()
        print(fn.__name__, f"{time.perf_counter() - t0:.1f}s", flush=True)
        OUT.write_text(json.dumps(RES, indent=1, default=float))
    print("wrote", OUT)
