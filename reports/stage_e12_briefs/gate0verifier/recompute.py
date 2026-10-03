"""Independent recomputation of the Stage E.12 Gate 0 numbers (Gate0Verifier-FableXHigh).

Reads only the saved phase-1 panel pickle (read-only) and the registered test list. Does NOT
import ml_route_v2.gate0 / cpcv / cost_filter / models; the panel module is imported only so the
pickle can be unpickled (the Panel dataclass). Writes everything under
reports/stage_e12_briefs/gate0verifier/ BEFORE any comparison with the lead's output.

Rules implemented from docs/STAGE_E_ML_V2_DESIGN.md V2.2 (filter), V2.2b (families A, B, bar),
V2.5 (targets), V2.9 (partition) and ml_route_v2/constants.py literals.
"""
from __future__ import annotations

import json
import math
import os
import pickle
import sys
import time
from itertools import combinations
from pathlib import Path

os.nice(10)

import numpy as np
import pandas as pd
from scipy.linalg import cho_factor, cho_solve
from scipy.stats import t as student_t

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
OUT = REPO / "reports/stage_e12_briefs/gate0verifier"
STAGES = Path(os.path.expanduser("~/.cache/propexp_e12_phase1/stages"))
LIST = REPO / "reports/stage_e12_gate0_list.json"

# ---- literals (ml_route_v2/constants.py, read 2026-10-03) ----
TAU = 0.167
HORIZONS = ("h60", "h120", "hF")
N_BLOCKS = 6
N_TEST_BLOCKS = 2
EMBARGO = 1
LAMBDA = 0.1
TOP_FRACTION = 0.20
COST_MULTIPLE = 1.5
T_MIN = 3.0
MIN_TRADES = 30
ALPHA = 0.05
N_PROGRAM = 198


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------ statistics ----
def per_date_means(days: np.ndarray, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    uniq, inv = np.unique(days, return_inverse=True)
    sums = np.bincount(inv, weights=values, minlength=len(uniq))
    cnt = np.bincount(inv, minlength=len(uniq))
    return uniq, sums / cnt


def date_t(m: np.ndarray) -> float:
    if m.size < 2:
        return float("nan")
    sd = m.std(ddof=1)
    if sd == 0:
        return float("nan") if m.mean() == 0 else math.copysign(math.inf, m.mean())
    return float(m.mean() / (sd / math.sqrt(m.size)))


def p_two(t: float, n: int) -> float:
    if math.isnan(t):
        return 1.0
    if math.isinf(t):
        return 0.0
    return float(2.0 * student_t.sf(abs(t), max(n - 1, 1)))


def p_one(t: float, n: int) -> float:
    if math.isnan(t):
        return 1.0
    if math.isinf(t):
        return 0.0 if t > 0 else 1.0
    return float(student_t.sf(t, max(n - 1, 1)))


def spearman_avg_rank(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2:
        return float("nan")
    ra = pd.Series(a).rank(method="average").to_numpy()
    rb = pd.Series(b).rank(method="average").to_numpy()
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


# ------------------------------------------------------------------ load ----
log("loading panel pickle")
with open(STAGES / "phase1_panel.pkl", "rb") as fh:
    d = pickle.load(fh)
out = d["out"]
panel = out["panel"]
frame: pd.DataFrame = panel.frame
calendar = [pd.Timestamp(x).date() for x in out["calendar"]]
feature_cols = list(panel.feature_cols)
signal_names = list(panel.signal_names)
log(f"frame {frame.shape}; calendar {len(calendar)} dates {calendar[0]}..{calendar[-1]}; "
    f"{len(feature_cols)} features; {len(signal_names)} signals")

roots_all = sorted(map(str, frame["root"].unique()))
root_arr = frame["root"].to_numpy(object).astype(str)
days_all = frame["trade_date"].to_numpy(dtype="datetime64[D]")

# window guard: nothing at or after 2024-03-01
assert days_all.max() <= np.datetime64("2024-02-29"), "a row is past the training window"
panel_dates = set(pd.to_datetime(frame["trade_date"]).dt.date.unique())
not_in_cal = sorted(panel_dates - set(calendar))
log(f"panel dates {len(panel_dates)}; not in calendar: {len(not_in_cal)}")

# ------------------------------------------------------------------ step 1: c/sigma ----
log("step 1: c/sigma filter")
recs = []
for r in roots_all:
    sel = root_arr == r
    for h in HORIZONS:
        ok = sel & frame[f"ok_{h}"].to_numpy(bool)
        y = frame.loc[ok, f"y_gross_{h}"].to_numpy(np.float64)
        cl = frame.loc[ok, f"cost_long_{h}"].to_numpy(np.float64)
        cs = frame.loc[ok, f"cost_short_{h}"].to_numpy(np.float64)
        n = int(ok.sum())
        c_max = float(np.maximum(cl, cs).mean()) if n else float("nan")
        c_avg = float(((cl + cs) / 2).mean()) if n else float("nan")
        sd = float(np.std(y, ddof=1)) if n >= 2 else float("nan")
        ratio = c_max / sd if (n >= 2 and sd > 0) else float("nan")
        ratio_avg = c_avg / sd if (n >= 2 and sd > 0) else float("nan")
        recs.append({"root": r, "horizon": h, "n_rows": n, "c_ticks": c_max,
                     "c_ticks_avg_sides": c_avg, "sigma_ticks": sd, "ratio": ratio,
                     "ratio_avg_sides": ratio_avg,
                     "admissible": bool(np.isfinite(ratio) and ratio <= TAU),
                     "admissible_avg_sides": bool(np.isfinite(ratio_avg) and ratio_avg <= TAU)})
csig = pd.DataFrame(recs)
csig.to_csv(OUT / "my_c_sigma.csv", index=False)
admissible = [(r["root"], r["horizon"]) for r in recs if r["admissible"]]
log(f"admissible pairs: {len(admissible)} of {len(recs)}; "
    f"max ratio {csig['ratio'].max():.4f}; differs under avg-sides reading: "
    f"{int((csig['admissible'] != csig['admissible_avg_sides']).sum())}")

# ------------------------------------------------------------------ step 2: CPCV ridge ----
log("step 2: blocks and splits")
n_cal = len(calendar)
size = n_cal // N_BLOCKS
blocks = [calendar[i * size:(i + 1) * size] if i < N_BLOCKS - 1 else calendar[i * size:]
          for i in range(N_BLOCKS)]
cal_index = {dte: i for i, dte in enumerate(calendar)}
splits = []
for idx, test_blocks in enumerate(combinations(range(N_BLOCKS), N_TEST_BLOCKS)):
    test_dates = set()
    for b in test_blocks:
        test_dates |= set(blocks[b])
    emb = set()
    for b in test_blocks:
        lo, hi = cal_index[blocks[b][0]], cal_index[blocks[b][-1]]
        for e in range(1, EMBARGO + 1):
            for j in (lo - e, hi + e):
                if 0 <= j < n_cal:
                    emb.add(calendar[j])
    emb -= test_dates
    train_dates = set(calendar) - test_dates - emb
    splits.append((idx, test_blocks, train_dates, test_dates, emb))
block_doc = {"n_calendar": n_cal, "block_size": size,
             "blocks": [{"i": i, "first": b[0].isoformat(), "last": b[-1].isoformat(),
                         "n": len(b)} for i, b in enumerate(blocks)],
             "splits": [{"index": s[0], "test_blocks": list(s[1]), "n_train_dates": len(s[2]),
                         "n_test_dates": len(s[3]), "embargo": sorted(x.isoformat() for x in s[4])}
                        for s in splits]}
(OUT / "my_blocks.json").write_text(json.dumps(block_doc, indent=1))


def ridge_fit_predict(Xtr: np.ndarray, ytr: np.ndarray, Xte: np.ndarray, lam: float) -> np.ndarray:
    """Centred ridge, unpenalized intercept, alpha = lam x n_train, Cholesky solve."""
    n = Xtr.shape[0]
    xm = Xtr.mean(axis=0)
    ym = ytr.mean()
    Xc = Xtr - xm
    yc = ytr - ym
    G = Xc.T @ Xc
    G[np.diag_indices_from(G)] += lam * n
    beta = cho_solve(cho_factor(G, lower=True), Xc.T @ yc)
    return (Xte - xm) @ beta + ym


def row_intervals_intersect(t_ns, x_ns, lo, hi):
    """Row [t, x] meets any of the disjoint sorted spans [lo, hi]."""
    if lo.size == 0:
        return np.zeros(t_ns.shape[0], dtype=bool)
    idx = np.searchsorted(lo, x_ns, side="right") - 1
    ok = idx >= 0
    return ok & (hi[np.clip(idx, 0, None)] >= t_ns)


trade_frames = []
b_tests = []
oof_store = {}
for h in HORIZONS:
    adm_roots = {r for r, hh in admissible if hh == h}
    mask = frame[f"ok_{h}"].to_numpy(bool) & np.isin(root_arr, sorted(adm_roots))
    rows = frame.loc[mask]
    X = rows[feature_cols].to_numpy(np.float64)
    y = rows[f"y_norm_{h}"].to_numpy(np.float64)
    yg = rows[f"y_gross_{h}"].to_numpy(np.float64)
    days = rows["trade_date"].to_numpy(dtype="datetime64[D]")
    t_ns = rows["decision_ts_ns"].to_numpy(np.int64)
    x_ns = rows[f"exit_ts_ns_{h}"].to_numpy(np.int64)
    assert np.isfinite(X).all() and np.isfinite(y).all() and np.isfinite(yg).all()
    assert (x_ns >= t_ns).all()
    rroot = rows["root"].to_numpy(object).astype(str)
    log(f"{h}: {len(rows)} rows, {len(adm_roots)} roots; fitting 15 ridge splits")
    sums = np.zeros(len(rows))
    counts = np.zeros(len(rows), dtype=np.int64)
    purged_total = 0
    for idx, test_blocks, train_dates, test_dates, emb in splits:
        te_days = np.array(sorted(test_dates), dtype="datetime64[D]")
        tr_days = np.array(sorted(train_dates), dtype="datetime64[D]")
        test = np.isin(days, te_days)
        train = np.isin(days, tr_days)
        # purge: training rows whose [t, x] overlaps any test row span (merged per test date)
        if test.any():
            uniq, inv = np.unique(days[test], return_inverse=True)
            lo = np.full(len(uniq), np.iinfo(np.int64).max, dtype=np.int64)
            hi = np.full(len(uniq), np.iinfo(np.int64).min, dtype=np.int64)
            np.minimum.at(lo, inv, t_ns[test])
            np.maximum.at(hi, inv, x_ns[test])
            order = np.argsort(lo, kind="stable")
            merged = []
            for a, b in zip(lo[order].tolist(), hi[order].tolist()):
                if merged and a <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            arr = np.asarray(merged, dtype=np.int64)
            overlap = row_intervals_intersect(t_ns, x_ns, arr[:, 0], arr[:, 1])
        else:
            overlap = np.zeros(len(rows), dtype=bool)
        purged = train & overlap
        purged_total += int(purged.sum())
        train = train & ~overlap
        assert not (train & test).any()
        pred = ridge_fit_predict(X[train], y[train], X[test], LAMBDA)
        sums[test] += pred
        counts[test] += 1
    n_paths = math.comb(N_BLOCKS - 1, N_TEST_BLOCKS - 1)
    assert (counts == n_paths).all(), f"{h}: OOF counts {sorted(set(counts.tolist()))}"
    r_hat = sums / counts
    oof_store[h] = {"n_rows": int(len(rows)), "purged_rows_total": purged_total,
                    "r_hat_mean": float(r_hat.mean()), "r_hat_sd": float(r_hat.std()),
                    "n_zero_pred": int((r_hat == 0).sum()),
                    "oof_corr_y_norm": float(np.corrcoef(r_hat, y)[0, 1])}
    np.save(OUT / f"my_oof_{h}.npy", r_hat)
    for r in sorted(adm_roots):
        pos = np.flatnonzero(rroot == r)
        rp = r_hat[pos]
        n = pos.size
        n_take = n // 5  # floor(0.2 n) exactly
        nz = np.flatnonzero(rp != 0)
        order = np.argsort(-np.abs(rp[nz]), kind="stable")
        take = np.sort(pos[nz[order[:n_take]]])
        side = np.sign(r_hat[take])
        g = side * yg[take]
        cost = np.where(side > 0, rows[f"cost_long_{h}"].to_numpy(np.float64)[take],
                        rows[f"cost_short_{h}"].to_numpy(np.float64)[take])
        udays, md = per_date_means(days[take], g)
        tb = date_t(md)
        b_tests.append({"test_id": f"gate0B_{r}_{h}", "root": r, "horizon": h,
                        "n_pair_rows": int(n), "n_trades": int(g.size), "n_dates": int(md.size),
                        "mean_g_ticks": float(g.mean()), "cost_ticks": float(cost.mean()),
                        "cost_multiple": float(g.mean() / cost.mean()),
                        "bar1_mean_ge_1p5c": bool(g.mean() >= COST_MULTIPLE * cost.mean()),
                        "t_B": tb, "p_one_sided": p_one(tb, int(md.size)),
                        "bar2_t_ge_3": bool(tb >= T_MIN), "bar4_n_ge_30": bool(g.size >= MIN_TRADES),
                        "n_long": int((side > 0).sum()), "n_short": int((side < 0).sum())})
        trade_frames.append(pd.DataFrame({"test_id": f"gate0B_{r}_{h}", "root": r, "horizon": h,
                                          "trade_date": days[take], "decision_ts_ns": t_ns[take],
                                          "r_hat": r_hat[take], "side": side.astype(np.int8),
                                          "g_ticks": g, "cost_ticks": cost}))
trades = pd.concat(trade_frames, ignore_index=True)
trades.to_parquet(OUT / "my_b_trades.parquet", index=False)
bt = pd.DataFrame(b_tests)
bt.to_csv(OUT / "my_family_b.csv", index=False)
_, md_pool = per_date_means(trades["trade_date"].to_numpy(dtype="datetime64[D]"),
                            trades["g_ticks"].to_numpy(np.float64))
pooled = {"mean_g_ticks": float(trades["g_ticks"].mean()),
          "mean_cost_ticks": float(trades["cost_ticks"].mean()), "t": date_t(md_pool),
          "n_trades": int(len(trades)), "n_dates": int(md_pool.size)}
elig = bt[bt["n_trades"] >= MIN_TRADES]
best = elig.sort_values("t_B", ascending=False).iloc[0]
log(f"family B done: {len(bt)} pairs; best t_B {best['test_id']} t={best['t_B']:.4f} "
    f"mean g {best['mean_g_ticks']:.4f} c {best['cost_ticks']:.4f} n {best['n_trades']}; "
    f"pairs with t>=3: {int((bt['t_B'] >= 3).sum())}; pooled t {pooled['t']:.3f}")

# ------------------------------------------------------------------ step 3: family A ----
log("step 3: family A (all 192; three seeded for the formal check)")
lst = json.loads(LIST.read_text())
a_ids_list_order = [t["test_id"] for t in lst["tests"] if t["kind"] == "gate0_A"]
list_sha = "53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea"
seed = int(list_sha[:8], 16)
rng = np.random.default_rng(seed)
chosen = [a_ids_list_order[i] for i in sorted(rng.choice(len(a_ids_list_order), 3, replace=False))]
a_tests = []
for h in HORIZONS:
    adm_roots = {r for r, hh in admissible if hh == h}
    mask = frame[f"ok_{h}"].to_numpy(bool) & np.isin(root_arr, sorted(adm_roots))
    rows = frame.loc[mask]
    y = rows[f"y_norm_{h}"].to_numpy(np.float64)
    yg = rows[f"y_gross_{h}"].to_numpy(np.float64)
    days = rows["trade_date"].to_numpy(dtype="datetime64[D]")
    for s in signal_names:
        z = rows[f"z_{s}"].to_numpy(np.float64)
        assert np.isfinite(z).all()
        udays, md = per_date_means(days, z * y)
        t = date_t(md)
        nz = z != 0
        a_tests.append({"test_id": f"gate0A_{s}_{h}", "signal": s, "horizon": h,
                        "n_dates": int(md.size), "n_obs": int(z.size),
                        "mean_m_d": float(md.mean()), "t": t, "p_two_sided": p_two(t, int(md.size)),
                        "ic_spearman": spearman_avg_rank(z, y),
                        "gross_ticks_sign": float((np.sign(z[nz]) * yg[nz]).mean()) if nz.any() else None,
                        "n_nonzero_z": int(nz.sum()), "seeded_choice": f"gate0A_{s}_{h}" in chosen})
at = pd.DataFrame(a_tests)
at.to_csv(OUT / "my_family_a.csv", index=False)
log(f"family A done: {len(at)} tests; min p {at['p_two_sided'].min():.4g} "
    f"({at.loc[at['p_two_sided'].idxmin(), 'test_id']}); seeded: {chosen}")

# ------------------------------------------------------------------ my own Holm + verdict ----
fam = pd.concat([at[["test_id"]].assign(family="A", p=at["p_two_sided"]),
                 bt[["test_id"]].assign(family="B", p=bt["p_one_sided"])], ignore_index=True)
fam = fam.sort_values(["p", "test_id"]).reset_index(drop=True)
m = len(fam)
fam["rank"] = np.arange(1, m + 1)
fam["threshold"] = ALPHA / (m - fam["rank"] + 1)
still, rej = True, []
for p_, th in zip(fam["p"], fam["threshold"]):
    still = still and (p_ <= th)
    rej.append(still)
fam["rejected"] = rej
fam.to_csv(OUT / "my_holm.csv", index=False)
rejected = set(fam.loc[fam["rejected"], "test_id"])
passing = [r["test_id"] for r in b_tests if r["test_id"] in rejected and r["bar4_n_ge_30"]
           and r["bar2_t_ge_3"] and r["bar1_mean_ge_1p5c"]]
best_row = fam.loc[fam["test_id"] == best["test_id"]].iloc[0]

summary = {
    "written_before_reading_lead_json": True,
    "panel": {"rows": int(len(frame)), "roots": roots_all, "n_roots": len(roots_all),
              "n_features": len(feature_cols), "n_signals": len(signal_names),
              "trade_dates": len(panel_dates), "panel_dates_not_in_calendar": [str(x) for x in not_in_cal],
              "created_pdt": out["created_pdt"], "input_fingerprint": out["input_fingerprint"],
              "constants_fingerprint": d["constants"]},
    "step1_filter": {"tau": TAU, "n_pairs": len(recs), "n_admissible": len(admissible),
                     "admissible": admissible, "max_ratio": float(csig["ratio"].max()),
                     "n_admissibility_changes_under_avg_sides_reading":
                         int((csig["admissible"] != csig["admissible_avg_sides"]).sum())},
    "step2_cpcv": {"blocks": block_doc["blocks"], "n_splits": len(splits), "oof": oof_store,
                   "pooled_b": pooled, "n_pairs_t_ge_3": int((bt["t_B"] >= 3).sum()),
                   "best_pair_by_t_B_n_ge_30": best.to_dict(),
                   "best_pair_holm": {"rank": int(best_row["rank"]), "threshold": float(best_row["threshold"]),
                                      "rejected": bool(best_row["rejected"])},
                   "top5_by_t_B": elig.sort_values("t_B", ascending=False).head(5)[
                       ["test_id", "mean_g_ticks", "cost_ticks", "cost_multiple", "t_B", "p_one_sided", "n_trades"]
                   ].to_dict(orient="records")},
    "step3_family_a": {"seed_hex": list_sha[:8], "seed": seed, "chosen": chosen,
                       "chosen_rows": at[at["seeded_choice"]].drop(columns=["seeded_choice"]).to_dict(orient="records"),
                       "min_p": float(at["p_two_sided"].min()),
                       "min_p_test": at.loc[at["p_two_sided"].idxmin(), "test_id"]},
    "my_holm": {"m": m, "n_rejected": int(fam["rejected"].sum()), "first_threshold": float(fam["threshold"].iloc[0]),
                "rank1": fam.iloc[0][["test_id", "p", "threshold", "rejected"]].to_dict()},
    "my_verdict": {"passed": bool(passing), "passing": passing},
    "step7_N": {"n_a": len(at), "n_b": len(bt), "n_a_plus_b": len(at) + len(bt),
                "n_program_new": N_PROGRAM + len(at) + len(bt)},
}
(OUT / "my_summary.json").write_text(json.dumps(summary, indent=1, default=str))
log("written my_summary.json; verdict", summary["my_verdict"])
