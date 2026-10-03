"""Gate 0: the pre-cost component audit (V2.2b, F2; interfaces section 5).

Family A, one test per (signal, horizon), pooled over products, on the horizon's usable rows
(ok_<h>, admissible pairs only when the caller passes them):
- m_d = mean over the date's rows of z_<signal> x y_norm_<h> (z is 0 where the signal does not
  apply, so such rows add 0 to the date's sum and count in its row total);
- t = mean(m_d) / (sd(m_d, ddof=1) / sqrt(n_dates)); two-sided p from Student's t, n_dates - 1 df;
- descriptive: the pooled Spearman rank IC of z and y_norm, and the mean gross ticks
  (y_gross_<h>) of the sign(z) position over rows with z != 0.

Family B, one test per admissible (root, horizon):
- ridge at GATE0_RIDGE_LAMBDA on all features, pooled across products, one model per horizon;
  outer CPCV as V2.9 (15 splits, purge, embargo); a row's OOF prediction is the mean of its 5;
- the pair's trades are its rows with |r_hat| (the model's normalized prediction) among the top
  floor(GATE0_TOP_FRACTION x n) of the pair's OOF |r_hat| (stable order on ties), side sign(r_hat);
- g = side x y_gross_<h> in vehicle ticks; mean g is compared with GATE0_COST_MULTIPLE x the mean
  round trip of the sides taken; t on the per-date means of g; one-sided p (mean g > 0).

gate0_verdict: Holm at GATE0_FAMILY_ALPHA across families A and B (B only if holm_includes_a is
False). Pass iff some B test has mean g >= multiple x cost, t >= GATE0_T_MIN, a Holm rejection and
at least GATE0_MIN_TRADES trades.

Every test is registered in the ledger before any computation (V2.9), and |A| + |B| tests count
toward N. The OOF predictions are cached per (horizon, split) under state_dir (resumable; a meta
file pins the inputs and the constants fingerprint, fingerprint.constants_fingerprint: code review
C-01).
"""

from __future__ import annotations

import json
import math
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml_route_v2.configs import ConfigLedger, ridge_spec
from ml_route_v2.constants import (
    GATE0_COST_MULTIPLE,
    GATE0_FAMILY_ALPHA,
    GATE0_HOLM_INCLUDES_FAMILY_A,
    GATE0_MIN_TRADES,
    GATE0_RIDGE_LAMBDA,
    GATE0_T_MIN,
    GATE0_TOP_FRACTION,
    HORIZONS,
    N_TEST_BLOCKS,
)
from ml_route_v2.cpcv import (
    CPCVError,
    StateMismatchError,
    assert_fold,
    calendar_blocks,
    horizon_data,
    input_fingerprint,
    outer_splits,
    split_masks,
)
from ml_route_v2.fingerprint import constants_fingerprint
from ml_route_v2.models import fit_model, predict

B_META_FILE = "gate0B_meta.json"


class Gate0Error(RuntimeError):
    """Gate 0 inputs are unusable."""


@dataclass(frozen=True)
class Gate0Test:
    test_id: str
    family: str  # "A" | "B"
    signal: str | None  # family A
    root: str | None  # family B
    horizon: str
    n_dates: int
    n_obs: int
    mean: float  # A: mean of m_d; B: mean gross ticks per trade
    t: float
    p: float  # A two-sided, B one-sided
    cost_ticks: float | None = None  # B: mean round trip of the sides taken
    n_trades: int | None = None  # B
    ic_spearman: float | None = None  # A, descriptive
    gross_ticks_sign: float | None = None  # A, descriptive: mean gross ticks of sign(z)


@dataclass(frozen=True)
class Gate0Rule:
    cost_multiple: float = GATE0_COST_MULTIPLE
    t_min: float = GATE0_T_MIN
    alpha: float = GATE0_FAMILY_ALPHA
    top_fraction: float = GATE0_TOP_FRACTION
    min_trades: int = GATE0_MIN_TRADES
    holm_includes_a: bool = GATE0_HOLM_INCLUDES_FAMILY_A


DEFAULT_RULE = Gate0Rule()  # the frozen V2.2b bar (a frozen dataclass, safe as a default)


@dataclass(frozen=True)
class Gate0Verdict:
    passed: bool
    passing: tuple[str, ...]
    n_tests: int
    holm: list[dict] = field(default_factory=list)


# ------------------------------------------------------------------ statistics ----
def date_t(per_date: np.ndarray) -> float:
    """mean / (sd(ddof=1) / sqrt(n)); NaN below 2 dates or with sd 0 and mean 0."""
    x = np.asarray(per_date, dtype=np.float64)
    if x.size < 2:
        return float("nan")
    mean, sd = float(x.mean()), float(x.std(ddof=1))
    if sd == 0:
        return float("nan") if mean == 0 else math.copysign(math.inf, mean)
    return mean / (sd / math.sqrt(x.size))


def p_value(t: float, n_dates: int, *, two_sided: bool) -> float:
    """Student's t p-value with n_dates - 1 df; 1.0 when t is NaN."""
    if not math.isfinite(t):
        if math.isnan(t):
            return 1.0
        return 0.0 if (two_sided or t > 0) else 1.0
    from scipy.stats import t as student_t  # scipy ships with the pinned lightgbm

    df = max(n_dates - 1, 1)
    return float(2.0 * student_t.sf(abs(t), df)) if two_sided else float(student_t.sf(t, df))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Rank correlation with average ranks; NaN when either side is constant."""
    if len(a) < 2:
        return float("nan")
    ra = pd.Series(np.asarray(a, dtype=np.float64)).rank().to_numpy()
    rb = pd.Series(np.asarray(b, dtype=np.float64)).rank().to_numpy()
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def _per_date_means(days: np.ndarray, values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return np.zeros(0, dtype=np.float64)
    uniq, inv = np.unique(days, return_inverse=True)
    sums = np.bincount(inv, weights=values, minlength=len(uniq))
    counts = np.bincount(inv, minlength=len(uniq))
    return sums / counts


# ------------------------------------------------------------------ registration ----
def _horizons(panel: Any) -> tuple[str, ...]:
    hs = tuple(getattr(panel, "horizons", HORIZONS))
    unknown = set(hs) - set(HORIZONS)
    if unknown:
        raise Gate0Error(f"unknown horizons {sorted(unknown)}")
    return hs


def family_a_id(signal: str, horizon: str) -> str:
    return f"gate0A_{signal}_{horizon}"


def family_b_id(root: str, horizon: str) -> str:
    return f"gate0B_{root}_{horizon}"


def _register_a(panel: Any, ledger: ConfigLedger) -> list[tuple[str, str]]:
    pairs = [(s, h) for h in _horizons(panel) for s in panel.signal_names]
    for s, h in pairs:
        ledger.register(family_a_id(s, h), "gate0_A",
                        {"family": "A", "signal": s, "horizon": h, "sided": "two",
                         "statistic": "date-clustered mean of z x y_norm"})
    return pairs


def _b_pairs(panel: Any, admissible: Collection[tuple[str, str]] | None) -> list[tuple[str, str]]:
    if admissible is not None:
        pairs = sorted({(str(r), str(h)) for r, h in admissible})
        unknown = {h for _, h in pairs} - set(HORIZONS)
        if unknown:
            raise Gate0Error(f"admissible pairs name unknown horizons {sorted(unknown)}")
        return pairs
    frame = panel.frame
    return sorted({(r, h) for h in _horizons(panel)
                   for r in frame.loc[frame[f"ok_{h}"].to_numpy(dtype=bool), "root"].unique()})


def _register_b(pairs: Sequence[tuple[str, str]], ledger: ConfigLedger, rule: Gate0Rule) -> None:
    for r, h in pairs:
        ledger.register(family_b_id(r, h), "gate0_B",
                        {"family": "B", "root": r, "horizon": h, "model": "ridge",
                         "lambda": GATE0_RIDGE_LAMBDA, "top_fraction": rule.top_fraction,
                         "sided": "one", "statistic": "date-clustered mean gross ticks"})


# ------------------------------------------------------------------ family A ----
def _family_a_horizon(panel: Any, h: str, signals: Sequence[str],
                      admissible: Collection[tuple[str, str]] | None) -> list[Gate0Test]:
    frame = panel.frame
    ok = frame[f"ok_{h}"].to_numpy(dtype=bool)
    if admissible is not None:
        # A fresh array: to_numpy may return a read-only view of the panel (pandas
        # copy-on-write), so it is never modified in place (bug G0-1).
        keep = frame["root"].isin({r for r, hh in admissible if hh == h}).to_numpy(dtype=bool)
        mask = np.logical_and(ok, keep)
    else:
        mask = ok
    rows = frame.loc[mask]
    y = rows[f"y_norm_{h}"].to_numpy(dtype=np.float64)
    yg = rows[f"y_gross_{h}"].to_numpy(dtype=np.float64)
    if not (np.isfinite(y).all() and np.isfinite(yg).all()):
        raise Gate0Error(f"{h}: a target is non-finite on an ok row")
    days = pd.to_datetime(rows["trade_date"]).to_numpy(dtype="datetime64[D]")
    out = []
    for s in signals:
        col = f"z_{s}"
        if col not in rows.columns:
            raise Gate0Error(f"panel frame lacks {col}")
        z = rows[col].to_numpy(dtype=np.float64)
        if not np.isfinite(z).all():
            raise Gate0Error(f"{col} is non-finite on an ok row")
        m_d = _per_date_means(days, z * y)
        t = date_t(m_d)
        nz = z != 0
        out.append(Gate0Test(
            test_id=family_a_id(s, h), family="A", signal=s, root=None, horizon=h,
            n_dates=int(m_d.size), n_obs=int(z.size),
            mean=float(m_d.mean()) if m_d.size else float("nan"), t=t,
            p=p_value(t, int(m_d.size), two_sided=True), ic_spearman=spearman(z, y),
            gross_ticks_sign=float((np.sign(z[nz]) * yg[nz]).mean()) if nz.any() else None))
    return out


def gate0_family_a(panel: Any, *, ledger: ConfigLedger,
                   admissible: Collection[tuple[str, str]] | None = None) -> list[Gate0Test]:
    """Family A: every (signal, horizon); all registered before the first computation."""
    pairs = _register_a(panel, ledger)
    ledger.require([family_a_id(s, h) for s, h in pairs])
    return [t for h in _horizons(panel)
            for t in _family_a_horizon(panel, h, panel.signal_names, admissible)]


# ------------------------------------------------------------------ family B ----
def _b_state(panel: Any, state_dir: Path, blocks: Sequence[Sequence[date]],
             admissible: Collection[tuple[str, str]] | None) -> Path:
    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=True)
    extra = {"features": list(panel.feature_cols), "lambda": GATE0_RIDGE_LAMBDA,
             "blocks": [[d.isoformat() for d in b] for b in blocks],
             "admissible": None if admissible is None else sorted(map(list, admissible)),
             "constants": constants_fingerprint()}  # code review C-01
    fp = input_fingerprint(panel.frame, extra)
    meta = root / B_META_FILE
    if meta.exists():
        if json.loads(meta.read_text(encoding="utf-8")).get("fingerprint") != fp:
            raise StateMismatchError(f"{meta} was written from other inputs")
    else:
        meta.write_text(json.dumps({"fingerprint": fp}), encoding="utf-8")
    return root


def _oof(panel: Any, h: str, blocks: Sequence[Sequence[date]], state: Path,
         admissible: Collection[tuple[str, str]] | None) -> tuple[Any, np.ndarray]:
    """(horizon data, OOF prediction per row = mean of its outer-test predictions)."""
    data = horizon_data(panel, h, admissible)
    sums = np.zeros(data.y.shape[0], dtype=np.float64)
    counts = np.zeros(data.y.shape[0], dtype=np.int64)
    spec = ridge_spec(GATE0_RIDGE_LAMBDA)
    for split in outer_splits(blocks):
        train, test = split_masks(split, data.days, data.t_ns, data.x_ns)
        assert_fold(split, data.days, data.t_ns, data.x_ns, train, test)
        path = state / f"gate0B_{h}_s{split.index:02d}.npy"
        if path.exists():
            pred = np.load(path)
            if pred.shape[0] != int(test.sum()):
                raise StateMismatchError(f"{path} holds {pred.shape[0]} predictions, the split "
                                         f"tests {int(test.sum())} rows")
        elif not train.any() or not test.any():
            pred = np.zeros(int(test.sum()), dtype=np.float64)
        else:
            pred = predict(fit_model(spec, data.X[train], data.y[train]), data.X[test])
            tmp = path.with_suffix(".tmp.npy")
            np.save(tmp, pred)
            tmp.replace(path)
        sums[test] += pred
        counts[test] += 1
    n_paths = math.comb(len(blocks) - 1, N_TEST_BLOCKS - 1)  # splits that test a given block
    if data.y.shape[0] and not (counts == n_paths).all():
        raise CPCVError(f"{h}: a row is out of fold {sorted(set(counts.tolist()))} times, "
                        f"not {n_paths}")
    return data, np.divide(sums, np.maximum(counts, 1))


def _top_trades(r_hat: np.ndarray, top_fraction: float) -> np.ndarray:
    """Indices of the top floor(fraction x n) |r_hat| among non-zero predictions (stable)."""
    nz = np.flatnonzero(r_hat != 0)
    n_take = int(math.floor(top_fraction * r_hat.shape[0] + 1e-9))
    order = np.argsort(-np.abs(r_hat[nz]), kind="stable")
    return np.sort(nz[order[:n_take]])


def gate0_b_trades(panel: Any, *, ledger: ConfigLedger, state_dir: Path,
                   admissible: Collection[tuple[str, str]] | None = None,
                   calendar: Sequence[date] | None = None,
                   rule: Gate0Rule = DEFAULT_RULE) -> pd.DataFrame:
    """Family B's trades of every pair (registers the B tests before the first fit)."""
    pairs = _b_pairs(panel, admissible)
    _register_b(pairs, ledger, rule)
    ledger.require([family_b_id(r, h) for r, h in pairs])
    dates = (calendar if calendar is not None
             else np.unique(pd.to_datetime(panel.frame["trade_date"]).to_numpy(
                 dtype="datetime64[D]")).tolist())
    blocks = calendar_blocks(dates)
    state = _b_state(panel, state_dir, blocks, admissible)
    adm = pairs if admissible is not None else None
    frames = []
    for h in sorted({h for _, h in pairs}, key=HORIZONS.index):
        data, r_hat = _oof(panel, h, blocks, state, adm)
        roots = data.rows["root"].to_numpy()
        for r in sorted({rr for rr, hh in pairs if hh == h}):
            pos = np.flatnonzero(roots == r)
            take = pos[_top_trades(r_hat[pos], rule.top_fraction)]
            side = np.sign(r_hat[take]).astype(np.int8)
            rows = data.rows.iloc[take]
            cost = np.where(side > 0, rows[f"cost_long_{h}"].to_numpy(dtype=np.float64),
                            rows[f"cost_short_{h}"].to_numpy(dtype=np.float64))
            frames.append(pd.DataFrame({
                "test_id": family_b_id(r, h), "root": r, "horizon": h,
                "trade_date": data.days[take], "decision_ts_ns": data.t_ns[take],
                "r_hat": r_hat[take], "side": side,
                "g_ticks": side * rows[f"y_gross_{h}"].to_numpy(dtype=np.float64),
                "cost_ticks": cost, "n_pair_rows": int(pos.size)}))
    cols = ["test_id", "root", "horizon", "trade_date", "decision_ts_ns", "r_hat", "side",
            "g_ticks", "cost_ticks", "n_pair_rows"]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=cols)


def _b_test(test_id: str, root: str, horizon: str, trades: pd.DataFrame,
            n_obs: int) -> Gate0Test:
    g = trades["g_ticks"].to_numpy(dtype=np.float64)
    if not np.isfinite(g).all():
        raise Gate0Error(f"{test_id}: a gross target is non-finite on a trade")
    per_date = _per_date_means(trades["trade_date"].to_numpy(dtype="datetime64[D]"), g)
    t = date_t(per_date)
    return Gate0Test(
        test_id=test_id, family="B", signal=None, root=root, horizon=horizon,
        n_dates=int(per_date.size), n_obs=int(n_obs),
        mean=float(g.mean()) if g.size else float("nan"), t=t,
        p=p_value(t, int(per_date.size), two_sided=False),
        cost_ticks=float(trades["cost_ticks"].mean()) if g.size else float("nan"),
        n_trades=int(g.size))


def gate0_family_b(panel: Any, *, ledger: ConfigLedger, state_dir: Path,
                   admissible: Collection[tuple[str, str]] | None = None,
                   calendar: Sequence[date] | None = None,
                   rule: Gate0Rule = DEFAULT_RULE) -> list[Gate0Test]:
    """Family B: every admissible (root, horizon) pair; registered before the first fit."""
    pairs = _b_pairs(panel, admissible)
    trades = gate0_b_trades(panel, ledger=ledger, state_dir=state_dir, admissible=admissible,
                            calendar=calendar, rule=rule)
    out = []
    for r, h in pairs:
        tid = family_b_id(r, h)
        sub = trades.loc[trades["test_id"] == tid]
        n_obs = int(sub["n_pair_rows"].iloc[0]) if len(sub) else 0
        out.append(_b_test(tid, r, h, sub, n_obs))
    return out


def gate0_b_pooled(trades: pd.DataFrame) -> dict:
    """The pooled family B result over all pairs (descriptive, V2.2b; not a test)."""
    t = _b_test("gate0B_pooled", "*", "*", trades, len(trades))
    return {"mean_g_ticks": t.mean, "mean_cost_ticks": t.cost_ticks, "t": t.t,
            "n_trades": t.n_trades, "n_dates": t.n_dates}


# ------------------------------------------------------------------ verdict ----
def holm(tests: Sequence[Gate0Test], alpha: float) -> list[dict]:
    """Holm step-down over the tests' p-values (ties by test_id)."""
    order = sorted(tests, key=lambda t: (t.p, t.test_id))
    m = len(order)
    rows, still = [], True
    for i, t in enumerate(order):
        threshold = alpha / (m - i)
        still = still and t.p <= threshold
        rows.append({"test_id": t.test_id, "family": t.family, "p": t.p, "rank": i + 1,
                     "threshold": threshold, "rejected": still})
    return rows


def gate0_verdict(tests: Sequence[Gate0Test], rule: Gate0Rule = DEFAULT_RULE) -> Gate0Verdict:
    """V2.2b pass bar over all of Gate 0's tests."""
    ids = [t.test_id for t in tests]
    if len(set(ids)) != len(ids):
        raise Gate0Error("duplicate Gate 0 test ids")
    family = [t for t in tests if t.family == "B" or (rule.holm_includes_a and t.family == "A")]
    table = holm(family, rule.alpha)
    rejected = {row["test_id"] for row in table if row["rejected"]}
    passing = tuple(
        t.test_id for t in tests
        if t.family == "B" and t.test_id in rejected and t.n_trades is not None
        and t.n_trades >= rule.min_trades and t.t >= rule.t_min
        and t.cost_ticks is not None and t.mean >= rule.cost_multiple * t.cost_ticks)
    return Gate0Verdict(bool(passing), passing, len(tests), table)
