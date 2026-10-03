"""Nested combinatorial purged cross-validation, PBO and DSR wiring (V2.9, F4).

Partition (v1 M7.3 rule, cut from the date list given): calendar_blocks cuts the sorted unique
dates into N_BLOCKS contiguous blocks of floor(n / N_BLOCKS) dates, the last taking the remainder.
Blocks are numbered 0..N_BLOCKS-1 in calendar order.

Outer CPCV: every pair of test blocks, C(6,2) = 15 splits (itertools.combinations order). Embargo:
EMBARGO_DATES full trade dates on each side of every test block, removed from training. Purge: a
training row whose [decision_ts_ns, exit_ts_ns] interval intersects the span [earliest decision,
latest exit] of any test date's rows is removed (ml_route/blocks.validation_spans, on timestamps).
assemble_paths gives the 5 backtest paths: block b goes, in path j, to the j-th split (in index
order) among those that test b.

Inner CPCV: inside an outer split's 4 training blocks, 4 folds, each holding out one block (its
dates that are outer training dates), with the same embargo and purge. Inner rows are also inside
the outer split's purged training rows, so the inner selection never reads an outer test row, an
outer embargo date or a label that overlaps an outer test date (asserted, LeakageError).

nested_cpcv: per outer split, every configuration is scored on the 4 inner folds by the injected
score_fn (the V2.9 selection metric); it is eligible only with >= MIN_TRADES trades and a finite
score in every fold; the best mean inner score wins, ties by configs.tie_break_key; none eligible
means the split trades nothing. Every configuration is also refit on the outer training rows and
scored on the outer test rows: the selected one's result is the nested out-of-sample record, and
all of them form the CPCV out-of-sample matrix (dates x configurations, each date averaged over the
5 splits that test its block, i.e. the 5 paths) for PBO and the per-configuration daily Sharpes
for the DSR's variance. final_selection applies the same selection to the 15 outer splits of the
full window, then refits the winner once on all rows.

Model inputs per horizon h: rows with ok_<h> True (and, if given, an admissible (root, h) pair),
X = frame[feature_cols] as float64, y = y_norm_<h>. Predictions are multiplied by the row's sigma_d
(vehicle ticks) before score_fn.

score_fn receives a copy of the validation rows only. Its daily P&L must sit on that validation
set's dates and its trade count cannot exceed the rows it got; otherwise LeakageError (the planted
"selection step that reads the test block" canary).

The risk table per split (design review D-04): with ``risk_fn`` (training rows -> risk table, e.g.
cost_filter.risk_table), every validation set is scored with the table of its own training rows:
an outer split's purged and embargoed training rows, an inner fold's inner training rows (inside
the outer training rows). score_fn is then called as score_fn(rows, r_hat, config, risk=table),
so a test block's volatility never sizes its own trades. The table is computed once per (split,
fold, horizon) and shared by the configurations of that horizon. Without ``risk_fn`` (None) the
contract is the old one, score_fn(rows, r_hat, config); with it, the callback's name joins the
fingerprint. A unit record carries ``n_risk_unknown``, the validation candidates whose pair has
no usable sigma or loss in the split's table (SplitScore.n_risk_unknown, code review C-02).

Resumability: each finished (config, split) unit is one line of state_dir/cpcv_units.jsonl. The
first line pins a fingerprint of the inputs (panel frame, features, blocks, admissible pairs, the
score function's and risk function's names with a functools.partial's bound arguments hashed, and
the constants fingerprint, fingerprint.constants_fingerprint: code review C-01); a restart with
other inputs or other constants raises StateMismatchError, and a restart with the same inputs
skips the finished units. Every configuration is registered in the ledger before the first fit
(V2.9).

pbo_cscv and dsr_at_n wrap funnel.multiple_comparisons (imported, not edited).
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Collection, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from funnel.multiple_comparisons import (
    deflated_sharpe_ratio,
    probability_of_backtest_overfitting,
)
from ml_route.accounting import moments
from ml_route_v2.configs import (
    Config,
    ConfigLedger,
    SplitScore,
    register_configs,
    tie_break_key,
)
from ml_route_v2.constants import EMBARGO_DATES, MIN_TRADES, N_BLOCKS, N_TEST_BLOCKS, PBO_BLOCKS
from ml_route_v2.fingerprint import constants_fingerprint, value_digest
from ml_route_v2.models import FittedModel, fit_model, predict

__all__ = [
    "CPCVError", "LeakageError", "StateMismatchError", "Split", "SplitScore", "ScoreFn", "RiskFn",
    "split_risk",
    "NestedResult", "FinalResult", "HorizonData", "calendar_blocks", "outer_splits",
    "inner_splits", "split_masks", "assert_fold", "assemble_paths", "horizon_data",
    "nested_cpcv", "final_selection", "pbo_cscv", "dsr_at_n", "sharpe_variance",
]

ScoreFn = Callable[[pd.DataFrame, np.ndarray, Config], SplitScore]
RiskFn = Callable[[pd.DataFrame], pd.DataFrame]  # training rows -> risk table (D-04)
UNITS_FILE = "cpcv_units.jsonl"
_OUTER = -1  # the inner index of an outer unit


class CPCVError(RuntimeError):
    """A split, a panel or a score is unusable for CPCV."""


class LeakageError(CPCVError):
    """A fit or a selection step could read data it must not see (V2.9 leakage controls)."""


class StateMismatchError(CPCVError):
    """A state directory holds results computed from other inputs."""


@dataclass(frozen=True)
class Split:
    index: int
    test_blocks: tuple[int, ...]
    train_dates: frozenset[date]
    test_dates: frozenset[date]
    embargo_dates: frozenset[date]


# ------------------------------------------------------------------ dates and blocks ----
def _to_date(value: Any) -> date:
    if isinstance(value, datetime):  # includes pd.Timestamp
        return value.date()
    if isinstance(value, date):
        return value
    return pd.Timestamp(value).date()


def _day_array(values: Any) -> np.ndarray:
    """Any date-like 1-D input (datetime64, Timestamp, date, ISO string) as datetime64[D]."""
    if isinstance(values, np.ndarray) and values.dtype == np.dtype("datetime64[D]"):
        return values
    ser = values if isinstance(values, pd.Series) else pd.Series(
        values if isinstance(values, np.ndarray) else list(values))
    return pd.to_datetime(ser).to_numpy(dtype="datetime64[D]")


def _dates_to_days(dates: Iterable[date]) -> np.ndarray:
    return np.array(sorted(dates), dtype="datetime64[D]")


def _calendar(blocks: Sequence[Sequence[date]]) -> list[date]:
    cal = [d for b in blocks for d in b]
    if any(a >= b for a, b in zip(cal, cal[1:], strict=False)):
        raise CPCVError("blocks are not contiguous, sorted and disjoint")
    return cal


def calendar_blocks(dates: Sequence[date],
                    n_blocks: int = N_BLOCKS) -> tuple[tuple[date, ...], ...]:
    """N contiguous blocks of floor(n / N) sorted unique dates, the last taking the remainder."""
    uniq = sorted({_to_date(d) for d in dates})
    size = len(uniq) // n_blocks if n_blocks >= 2 else 0
    if size < 1:
        raise CPCVError(f"{len(uniq)} dates cannot form {n_blocks} blocks")
    return tuple(tuple(uniq[i * size:(i + 1) * size]) if i < n_blocks - 1
                 else tuple(uniq[i * size:]) for i in range(n_blocks))


def _neighbours(cal: list[date], first: date, last: date, width: int) -> set[date]:
    """The `width` calendar dates before `first` and after `last`."""
    lo, hi = cal.index(first), cal.index(last)
    out = set()
    for e in range(1, width + 1):
        for j in (lo - e, hi + e):
            if 0 <= j < len(cal):
                out.add(cal[j])
    return out


def outer_splits(blocks: Sequence[Sequence[date]], n_test_blocks: int = N_TEST_BLOCKS,
                 embargo: int = EMBARGO_DATES) -> tuple[Split, ...]:
    """Every combination of n_test_blocks test blocks: C(6,2) = 15 splits."""
    cal = _calendar(blocks)
    splits = []
    for idx, test in enumerate(combinations(range(len(blocks)), n_test_blocks)):
        test_dates = {d for b in test for d in blocks[b]}
        emb: set[date] = set()
        for b in test:
            emb |= _neighbours(cal, blocks[b][0], blocks[b][-1], embargo) - test_dates
        train = set(cal) - test_dates - emb
        splits.append(Split(idx, tuple(test), frozenset(train), frozenset(test_dates),
                            frozenset(emb)))
    return tuple(splits)


def _assert_inner_isolated(outer: Split, inner: Split) -> None:
    seen = inner.train_dates | inner.test_dates
    forbidden = outer.test_dates | outer.embargo_dates
    if seen & forbidden:
        bad = sorted(seen & forbidden)[:3]
        raise LeakageError(f"inner fold {inner.index} of outer split {outer.index} reads outer "
                           f"test or embargo dates: {bad}")
    if not seen <= outer.train_dates:
        raise LeakageError(f"inner fold {inner.index} of outer split {outer.index} reads dates "
                           "outside the outer training dates")


def inner_splits(outer: Split, blocks: Sequence[Sequence[date]],
                 embargo: int = EMBARGO_DATES) -> tuple[Split, ...]:
    """Leave-one-block-out folds over the outer split's training blocks (4 for 6 blocks, 2 test)."""
    cal = _calendar(blocks)
    folds = []
    train_blocks = [b for b in range(len(blocks)) if b not in outer.test_blocks]
    for f, b in enumerate(train_blocks):
        test = set(blocks[b]) & outer.train_dates
        emb = (_neighbours(cal, blocks[b][0], blocks[b][-1], embargo) & outer.train_dates) - test
        train = outer.train_dates - test - emb
        split = Split(f, (b,), frozenset(train), frozenset(test), frozenset(emb))
        _assert_inner_isolated(outer, split)
        folds.append(split)
    return tuple(folds)


def assemble_paths(splits: Sequence[Split], n_blocks: int = N_BLOCKS) -> tuple[dict[int, int], ...]:
    """CPCV paths: in path j, block b is tested by the j-th split (index order) that tests b."""
    testers = {b: sorted(s.index for s in splits if b in s.test_blocks) for b in range(n_blocks)}
    counts = {len(v) for v in testers.values()}
    if len(counts) != 1 or 0 in counts:
        raise CPCVError(f"blocks are tested unequally often: {sorted(counts)}")
    n_paths = counts.pop()
    return tuple({b: testers[b][j] for b in range(n_blocks)} for j in range(n_paths))


# ------------------------------------------------------------------ purge and embargo ----
def _test_spans(days: np.ndarray, t_ns: np.ndarray, x_ns: np.ndarray,
                test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Merged, sorted, disjoint [lo, hi] spans of the test dates' rows."""
    if not test.any():
        return np.zeros(0, np.int64), np.zeros(0, np.int64)
    uniq, inv = np.unique(days[test], return_inverse=True)
    lo = np.full(len(uniq), np.iinfo(np.int64).max, dtype=np.int64)
    hi = np.full(len(uniq), np.iinfo(np.int64).min, dtype=np.int64)
    np.minimum.at(lo, inv, t_ns[test])
    np.maximum.at(hi, inv, x_ns[test])
    order = np.argsort(lo, kind="stable")
    merged: list[list[int]] = []
    for a, b in zip(lo[order].tolist(), hi[order].tolist(), strict=True):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    arr = np.asarray(merged, dtype=np.int64)
    return arr[:, 0], arr[:, 1]


def _intersects(t_ns: np.ndarray, x_ns: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """Row interval [t, x] meets any of the disjoint sorted spans [lo, hi]."""
    if lo.size == 0:
        return np.zeros(t_ns.shape[0], dtype=bool)
    idx = np.searchsorted(lo, x_ns, side="right") - 1
    ok = idx >= 0
    return ok & (hi[np.clip(idx, 0, None)] >= t_ns)


def _ts(values: Any, name: str) -> np.ndarray:
    arr = np.asarray(values)
    if arr.dtype.kind == "f":
        if not np.isfinite(arr).all():
            raise CPCVError(f"{name} holds a missing timestamp")
        arr = arr.astype(np.int64)
    return arr.astype(np.int64, copy=False)


def split_masks(split: Split, trade_date: np.ndarray, decision_ts_ns: np.ndarray,
                exit_ts_ns: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(training mask after embargo and purge, test mask) over a row table."""
    days = _day_array(trade_date)
    t_ns = _ts(decision_ts_ns, "decision_ts_ns")
    x_ns = _ts(exit_ts_ns, "exit_ts_ns")
    if not (days.shape[0] == t_ns.shape[0] == x_ns.shape[0]):
        raise CPCVError("trade_date, decision_ts_ns and exit_ts_ns differ in length")
    if (x_ns < t_ns).any():
        raise CPCVError("an exit precedes its decision")
    test = np.isin(days, _dates_to_days(split.test_dates))
    train = np.isin(days, _dates_to_days(split.train_dates))
    lo, hi = _test_spans(days, t_ns, x_ns, test)
    return train & ~_intersects(t_ns, x_ns, lo, hi), test


def assert_fold(split: Split, trade_date: np.ndarray, decision_ts_ns: np.ndarray,
                exit_ts_ns: np.ndarray, train: np.ndarray, test: np.ndarray) -> None:
    """The fold test (V2.9): raises LeakageError on any violation."""
    days = _day_array(trade_date)
    t_ns, x_ns = _ts(decision_ts_ns, "decision_ts_ns"), _ts(exit_ts_ns, "exit_ts_ns")
    if (train & test).any():
        raise LeakageError(f"split {split.index}: a row is in training and test")
    tr_days = days[train]
    forbidden = _dates_to_days(split.test_dates | split.embargo_dates)
    if np.isin(tr_days, forbidden).any():
        raise LeakageError(f"split {split.index}: a test or embargo date is in training")
    lo, hi = _test_spans(days, t_ns, x_ns, np.isin(days, _dates_to_days(split.test_dates)))
    if (train & _intersects(t_ns, x_ns, lo, hi)).any():
        raise LeakageError(f"split {split.index}: a training label overlaps a test date")


# ------------------------------------------------------------------ panel access ----
@dataclass(frozen=True)
class HorizonData:
    """One horizon's model rows: ok_<h> (and admissible) rows of the panel, in panel order."""

    horizon: str
    rows: pd.DataFrame
    X: np.ndarray
    y: np.ndarray
    days: np.ndarray  # datetime64[D]
    t_ns: np.ndarray
    x_ns: np.ndarray
    sigma: np.ndarray


def _admissible_mask(frame: pd.DataFrame, horizon: str,
                     admissible: Collection[tuple[str, str]] | None) -> np.ndarray:
    if admissible is None:
        return np.ones(len(frame), dtype=bool)
    roots = {r for r, h in admissible if h == horizon}
    return frame["root"].isin(roots).to_numpy()


def horizon_data(panel: Any, horizon: str,
                 admissible: Collection[tuple[str, str]] | None = None) -> HorizonData:
    """X, y_norm, timestamps and sigma_d of the horizon's usable rows (raises on bad values)."""
    frame: pd.DataFrame = panel.frame
    cols = list(panel.feature_cols)
    need = ["root", "trade_date", "decision_ts_ns", "sigma_d", f"ok_{horizon}",
            f"y_norm_{horizon}", f"exit_ts_ns_{horizon}", *cols]
    missing = [c for c in need if c not in frame.columns]
    if missing:
        raise CPCVError(f"panel frame lacks columns {missing[:5]}")
    mask = frame[f"ok_{horizon}"].to_numpy(dtype=bool) & _admissible_mask(frame, horizon,
                                                                           admissible)
    rows = frame.loc[mask]
    X = rows[cols].to_numpy(dtype=np.float64)
    y = rows[f"y_norm_{horizon}"].to_numpy(dtype=np.float64)
    sigma = rows["sigma_d"].to_numpy(dtype=np.float64)
    if not np.isfinite(X).all():
        raise CPCVError(f"{horizon}: a feature is non-finite on an ok row")
    if not np.isfinite(y).all():
        raise CPCVError(f"{horizon}: y_norm_{horizon} is non-finite on an ok row")
    if not (np.isfinite(sigma).all() and (sigma > 0).all()):
        raise CPCVError(f"{horizon}: sigma_d is non-positive or non-finite on an ok row")
    return HorizonData(horizon, rows, X, y, _day_array(rows["trade_date"]),
                       _ts(rows["decision_ts_ns"], "decision_ts_ns"),
                       _ts(rows[f"exit_ts_ns_{horizon}"], f"exit_ts_ns_{horizon}"), sigma)


# ------------------------------------------------------------------ resumable state ----
def _callable_name(fn: Any) -> str:
    """Module and qualified name; for a functools.partial also a digest of its bound positional
    and keyword arguments (code review C-01)."""
    base = getattr(fn, "func", fn)  # functools.partial
    name = getattr(base, "__qualname__", type(base).__name__)
    out = f"{getattr(base, '__module__', '?')}.{name}"
    args, keywords = getattr(fn, "args", ()), getattr(fn, "keywords", None)
    if base is fn or not (args or keywords):
        return out
    bound = [value_digest(a) for a in args]
    bound += [f"{k}={value_digest(v)}" for k, v in sorted((keywords or {}).items())]
    return f"{out}({hashlib.sha256(repr(bound).encode()).hexdigest()})"


def input_fingerprint(frame: pd.DataFrame, extra: Mapping[str, Any]) -> str:
    h = hashlib.sha256()
    h.update(pd.util.hash_pandas_object(frame, index=True).to_numpy().tobytes())
    h.update(json.dumps([list(map(str, frame.columns))], sort_keys=True).encode())
    h.update(json.dumps(extra, sort_keys=True, default=str).encode())
    return h.hexdigest()


class JsonlStore:
    """Append-only JSONL of finished units; line 1 pins the input fingerprint."""

    def __init__(self, path: Path, fingerprint: str) -> None:
        self._path = Path(path)
        self._records: dict[tuple, dict] = {}
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if self._path.exists() and self._path.stat().st_size > 0:
            self._load(fingerprint)
        else:
            self._append({"unit": "meta", "fingerprint": fingerprint})

    @staticmethod
    def key(rec: Mapping) -> tuple:
        return (rec["unit"], rec["config_id"], int(rec["outer"]), int(rec["inner"]))

    def _load(self, fingerprint: str) -> None:
        raw = self._path.read_bytes()
        cut = raw.rfind(b"\n") + 1
        if cut < len(raw):  # a crash mid-line: drop the fragment
            with self._path.open("r+b") as fh:
                fh.truncate(cut)
        lines = raw[:cut].decode("utf-8").splitlines()
        if not lines:
            self._append({"unit": "meta", "fingerprint": fingerprint})
            return
        meta = json.loads(lines[0])
        if meta.get("unit") != "meta" or meta.get("fingerprint") != fingerprint:
            raise StateMismatchError(f"{self._path} was written from other inputs")
        for line in lines[1:]:
            rec = json.loads(line)
            self._records[self.key(rec)] = rec

    def _append(self, rec: Mapping) -> None:
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
            fh.flush()

    def has(self, key: tuple) -> bool:
        return key in self._records

    def get(self, key: tuple) -> dict:
        return self._records[key]

    def put(self, rec: Mapping) -> None:
        key = self.key(rec)
        if key in self._records:
            raise CPCVError(f"unit {key} written twice")
        self._append(rec)
        self._records[key] = dict(rec)


# ------------------------------------------------------------------ scoring ----
def _finite_or_none(x: float) -> float | None:
    return float(x) if x is not None and math.isfinite(float(x)) else None


def _daily_dates(daily: pd.Series) -> list[date]:
    return [_to_date(d) for d in daily.index]


def _guarded_score(score_fn: ScoreFn, rows: pd.DataFrame, r_hat: np.ndarray, config: Config,
                   allowed: frozenset[date], risk: pd.DataFrame | None = None) -> SplitScore:
    """Call score_fn on a copy of the validation rows (and of the split's risk table, when
    given); reject a score that read other rows."""
    if risk is None:
        res = score_fn(rows.copy(), r_hat.copy(), config)
    else:
        res = score_fn(rows.copy(), r_hat.copy(), config, risk=risk.copy())
    if not isinstance(res, SplitScore):
        raise CPCVError(f"score_fn returned {type(res).__name__}, not SplitScore")
    outside = sorted(set(_daily_dates(res.daily)) - allowed)
    if outside:
        raise LeakageError(f"{config.config_id}: score_fn returned P&L on {len(outside)} dates "
                           f"outside the validation set, e.g. {outside[:2]}")
    if not 0 <= int(res.n_trades) <= len(rows):
        raise LeakageError(f"{config.config_id}: score_fn counted {res.n_trades} trades on "
                           f"{len(rows)} validation rows")
    return res


def _unit_record(unit: str, config: Config, outer: int, inner: int, score: SplitScore | None,
                 model: FittedModel | None, n_train: int, n_test: int,
                 keep_daily: bool) -> dict:
    sharpe = _finite_or_none(score.sharpe) if score is not None else None
    n_trades = int(score.n_trades) if score is not None else 0
    rec = {"unit": unit, "config_id": config.config_id, "outer": outer, "inner": inner,
           "sharpe": sharpe, "n_trades": n_trades,
           "eligible": bool(sharpe is not None and n_trades >= MIN_TRADES),
           "sha256": model.sha256 if model is not None else None,
           "n_train": int(n_train), "n_test": int(n_test),
           "n_risk_unknown": int(getattr(score, "n_risk_unknown", 0)) if score is not None
           else 0}  # code review C-02
    if keep_daily:
        daily = {} if score is None else {
            _to_date(d).isoformat(): float(v) for d, v in score.daily.items()}
        if any(not math.isfinite(v) for v in daily.values()):
            raise CPCVError(f"{config.config_id}: non-finite daily P&L")
        rec["daily"] = daily
    return rec


def _fit_and_score(spec_configs: Sequence[Config], data: HorizonData, train: np.ndarray,
                   test: np.ndarray, split: Split, score_fn: ScoreFn, store: JsonlStore,
                   unit: str, outer: int, inner: int,
                   risk_of: Callable[[], pd.DataFrame] | None = None) -> None:
    """One fit shared by the configs that differ only in k; one record per config.
    ``risk_of`` gives the split's own risk table (D-04), computed only when scoring happens."""
    keep_daily = unit == "outer"
    n_train, n_test = int(train.sum()), int(test.sum())
    if n_train == 0 or n_test == 0:
        for c in spec_configs:
            store.put(_unit_record(unit, c, outer, inner, None, None, n_train, n_test,
                                   keep_daily))
        return
    model = fit_model(spec_configs[0].model, data.X[train], data.y[train])
    r_hat = predict(model, data.X[test]) * data.sigma[test]
    rows = data.rows.iloc[np.flatnonzero(test)]
    risk = risk_of() if risk_of is not None else None
    for c in spec_configs:
        score = _guarded_score(score_fn, rows, r_hat, c, split.test_dates, risk)
        store.put(_unit_record(unit, c, outer, inner, score, model, n_train, n_test, keep_daily))


def _assert_rows_isolated(outer: Split, data: HorizonData, outer_test: np.ndarray,
                          used: np.ndarray) -> None:
    """Inner rows: no outer test or embargo date, no label overlapping an outer test date."""
    forbidden = _dates_to_days(outer.test_dates | outer.embargo_dates)
    if np.isin(data.days[used], forbidden).any():
        raise LeakageError(f"outer split {outer.index}: the inner selection reads an outer test "
                           "or embargo row")
    lo, hi = _test_spans(data.days, data.t_ns, data.x_ns, outer_test)
    if (used & _intersects(data.t_ns, data.x_ns, lo, hi)).any():
        raise LeakageError(f"outer split {outer.index}: an inner row's label overlaps an outer "
                           "test date")


def _groups(configs: Sequence[Config]) -> dict[tuple[str, str], list[Config]]:
    out: dict[tuple[str, str], list[Config]] = {}
    for c in configs:
        out.setdefault((c.model.model_id, c.horizon), []).append(c)
    return out


@dataclass(frozen=True)
class _Run:
    """The fixed inputs of one CPCV run."""

    blocks: tuple[tuple[date, ...], ...]
    outer: tuple[Split, ...]
    data: Mapping[str, HorizonData]
    store: JsonlStore


def _prepare(panel: Any, configs: Sequence[Config], score_fn: ScoreFn, ledger: ConfigLedger,
             state_dir: Path, admissible: Collection[tuple[str, str]] | None,
             calendar: Sequence[date] | None, risk_fn: RiskFn | None = None) -> _Run:
    if not configs:
        raise CPCVError("no configurations")
    if len({c.config_id for c in configs}) != len(configs):
        raise CPCVError("duplicate config_id")
    register_configs(ledger, tuple(configs))  # V2.9: before the first fit
    dates = (calendar if calendar is not None
             else np.unique(_day_array(panel.frame["trade_date"])).tolist())
    blocks = calendar_blocks(dates)
    horizons = sorted({c.horizon for c in configs})
    data = {h: horizon_data(panel, h, admissible) for h in horizons}
    extra = {"features": list(panel.feature_cols),
             "blocks": [[d.isoformat() for d in b] for b in blocks],
             "admissible": None if admissible is None else sorted(map(list, admissible)),
             "score_fn": _callable_name(score_fn), "embargo": EMBARGO_DATES,
             "min_trades": MIN_TRADES, "constants": constants_fingerprint()}  # C-01
    if risk_fn is not None:
        extra["risk_fn"] = _callable_name(risk_fn)  # D-04
    store = JsonlStore(Path(state_dir) / UNITS_FILE, input_fingerprint(panel.frame, extra))
    return _Run(blocks, outer_splits(blocks), data, store)


def split_risk(risk_fn: RiskFn | None, data: HorizonData, train: np.ndarray,
               cache: dict[tuple, pd.DataFrame], key: tuple) -> Callable[[], pd.DataFrame] | None:
    """A thunk giving risk_fn on the split's training rows (cached by ``key``), or None."""
    if risk_fn is None:
        return None

    def thunk() -> pd.DataFrame:
        if key not in cache:
            cache[key] = risk_fn(data.rows.iloc[np.flatnonzero(train)])
        return cache[key]

    return thunk


def _compute_units(run: _Run, configs: Sequence[Config], score_fn: ScoreFn, *,
                   with_inner: bool, risk_fn: RiskFn | None = None) -> None:
    for osplit in run.outer:
        s = osplit.index
        folds = inner_splits(osplit, run.blocks) if with_inner else ()
        cache: dict[tuple, pd.DataFrame] = {}  # (fold, horizon) -> the split's risk table
        for (_, h), cfgs in _groups(configs).items():
            data = run.data[h]
            otrain, otest = split_masks(osplit, data.days, data.t_ns, data.x_ns)
            assert_fold(osplit, data.days, data.t_ns, data.x_ns, otrain, otest)
            for fold in folds:
                todo = [c for c in cfgs if not run.store.has(("inner", c.config_id, s, fold.index))]
                if not todo:
                    continue
                _assert_inner_isolated(osplit, fold)
                itrain, itest = split_masks(fold, data.days, data.t_ns, data.x_ns)
                itrain, itest = itrain & otrain, itest & otrain
                assert_fold(fold, data.days, data.t_ns, data.x_ns, itrain, itest)
                _assert_rows_isolated(osplit, data, otest, itrain | itest)
                _fit_and_score(todo, data, itrain, itest, fold, score_fn, run.store, "inner", s,
                               fold.index, split_risk(risk_fn, data, itrain, cache,
                                                      (fold.index, h)))
            todo = [c for c in cfgs if not run.store.has(("outer", c.config_id, s, _OUTER))]
            if todo:
                _fit_and_score(todo, data, otrain, otest, osplit, score_fn, run.store, "outer", s,
                               _OUTER, split_risk(risk_fn, data, otrain, cache, (_OUTER, h)))


# ------------------------------------------------------------------ selection ----
def _select(configs: Sequence[Config], records: Mapping[str, list[dict]],
            n_required: int) -> tuple[Config | None, list[dict]]:
    """Best mean score among configs eligible on every one of n_required validation sets."""
    table, best, best_key = [], None, None
    for c in configs:
        recs = records.get(c.config_id, [])
        eligible = len(recs) == n_required and all(r["eligible"] for r in recs)
        mean = (sum(r["sharpe"] for r in recs) / len(recs)) if eligible else None
        table.append({"config_id": c.config_id, "mean_score": mean, "n_sets": len(recs),
                      "eligible": eligible,
                      "min_trades": min((r["n_trades"] for r in recs), default=0)})
        if eligible:
            key = (-mean, tie_break_key(c))
            if best_key is None or key < best_key:
                best, best_key = c, key
    return best, table


def _block_dates(blocks: Sequence[Sequence[date]]) -> list[date]:
    return [d for b in blocks for d in b]


def _outer_daily(run: _Run, config_id: str, s: int) -> dict[str, float]:
    return run.store.get(("outer", config_id, s, _OUTER))["daily"]


def _path_series(run: _Run, path: Mapping[int, int],
                 config_of_split: Callable[[int], str | None]) -> np.ndarray:
    out = []
    for b, block in enumerate(run.blocks):
        cid = config_of_split(path[b])
        daily = _outer_daily(run, cid, path[b]) if cid is not None else {}
        out.extend(daily.get(d.isoformat(), 0.0) for d in block)
    return np.asarray(out, dtype=np.float64)


def _sharpe(xs: np.ndarray) -> float:
    return float(moments(xs.tolist())["sharpe"]) if xs.size else float("nan")


@dataclass(frozen=True)
class NestedResult:
    blocks: tuple[tuple[date, ...], ...]
    splits: tuple[Split, ...]
    paths: tuple[dict[int, int], ...]
    selected: tuple[str | None, ...]  # per outer split; None: no eligible configuration
    selected_sha256: tuple[str | None, ...]  # the selected refit's model hash per outer split
    inner_table: pd.DataFrame  # per (config, outer split): mean inner score, eligibility
    outer_table: pd.DataFrame  # per (config, outer split): outer test score
    path_daily: pd.DataFrame  # calendar dates x 5 paths: the nested OOS daily net $
    config_daily: pd.DataFrame  # calendar dates x configs: CPCV OOS daily, mean over 5 paths
    config_sharpes: pd.Series  # daily Sharpe of each config_daily column (population sd)
    config_path_sharpes: pd.DataFrame  # config x path: each path's daily Sharpe


def _config_daily(run: _Run, configs: Sequence[Config]) -> pd.DataFrame:
    testers = {b: [s.index for s in run.outer if b in s.test_blocks]
               for b in range(len(run.blocks))}
    cols = {}
    for c in configs:
        vals = []
        for b, block in enumerate(run.blocks):
            dailies = [_outer_daily(run, c.config_id, s) for s in testers[b]]
            vals.extend(sum(dl.get(d.isoformat(), 0.0) for dl in dailies) / len(dailies)
                        for d in block)
        cols[c.config_id] = vals
    return pd.DataFrame(cols, index=pd.Index(_block_dates(run.blocks), name="trade_date"))


def _outer_records(run: _Run, configs: Sequence[Config]) -> dict[str, list[dict]]:
    return {c.config_id: [run.store.get(("outer", c.config_id, s.index, _OUTER))
                          for s in run.outer] for c in configs}


def nested_cpcv(panel: Any, configs: Sequence[Config], score_fn: ScoreFn, *,
                ledger: ConfigLedger, state_dir: Path,
                admissible: Collection[tuple[str, str]] | None = None,
                calendar: Sequence[date] | None = None,
                risk_fn: RiskFn | None = None) -> NestedResult:
    """Nested CPCV (V2.9 F4); resumable per (config, split) unit under state_dir. ``risk_fn``:
    the per-split risk table (D-04, module docstring)."""
    run = _prepare(panel, configs, score_fn, ledger, state_dir, admissible, calendar, risk_fn)
    _compute_units(run, configs, score_fn, with_inner=True, risk_fn=risk_fn)
    n_folds = len(run.blocks) - len(run.outer[0].test_blocks)
    selected, shas, inner_rows = [], [], []
    for osplit in run.outer:
        s = osplit.index
        recs = {c.config_id: [run.store.get(("inner", c.config_id, s, f)) for f in range(n_folds)]
                for c in configs}
        best, table = _select(configs, recs, n_folds)
        inner_rows.extend({"split": s, **row} for row in table)
        selected.append(best.config_id if best is not None else None)
        shas.append(run.store.get(("outer", best.config_id, s, _OUTER))["sha256"]
                    if best is not None else None)
    paths = assemble_paths(run.outer, len(run.blocks))
    index = pd.Index(_block_dates(run.blocks), name="trade_date")
    path_daily = pd.DataFrame({j: _path_series(run, p, lambda s: selected[s])
                               for j, p in enumerate(paths)}, index=index)
    outer_rows = [{"split": r["outer"], "config_id": r["config_id"], "sharpe": r["sharpe"],
                   "n_trades": r["n_trades"], "eligible": r["eligible"], "sha256": r["sha256"]}
                  for recs in _outer_records(run, configs).values() for r in recs]
    config_daily = _config_daily(run, configs)
    path_sh = {c.config_id: [_sharpe(_path_series(run, p, lambda s, cid=c.config_id: cid))
                             for p in paths] for c in configs}
    return NestedResult(
        blocks=run.blocks, splits=run.outer, paths=paths, selected=tuple(selected),
        selected_sha256=tuple(shas), inner_table=pd.DataFrame(inner_rows),
        outer_table=pd.DataFrame(outer_rows), path_daily=path_daily, config_daily=config_daily,
        config_sharpes=pd.Series({cid: _sharpe(config_daily[cid].to_numpy())
                                  for cid in config_daily.columns}, name="sharpe"),
        config_path_sharpes=pd.DataFrame.from_dict(path_sh, orient="index"))


@dataclass(frozen=True)
class FinalResult:
    config: Config | None  # None: no configuration is eligible on all 15 outer splits
    table: pd.DataFrame  # per config: mean outer score, eligibility
    model: FittedModel | None  # the selected configuration refit on all rows (the frozen model)
    n_train_rows: int


def final_selection(panel: Any, configs: Sequence[Config], score_fn: ScoreFn, *,
                    ledger: ConfigLedger, state_dir: Path,
                    admissible: Collection[tuple[str, str]] | None = None,
                    calendar: Sequence[date] | None = None,
                    risk_fn: RiskFn | None = None) -> FinalResult:
    """The same selection over the 15 outer splits, then one refit on every row (V2.9). The
    outer units (and so ``risk_fn``) are nested_cpcv's; the frozen model's own risk table is
    the caller's, from all six blocks (D-04)."""
    run = _prepare(panel, configs, score_fn, ledger, state_dir, admissible, calendar, risk_fn)
    _compute_units(run, configs, score_fn, with_inner=False, risk_fn=risk_fn)
    best, table = _select(configs, _outer_records(run, configs), len(run.outer))
    if best is None:
        return FinalResult(None, pd.DataFrame(table), None, 0)
    data = run.data[best.horizon]
    model = fit_model(best.model, data.X, data.y)
    return FinalResult(best, pd.DataFrame(table), model, int(data.X.shape[0]))


# ------------------------------------------------------------------ PBO and DSR ----
def pbo_cscv(perf: np.ndarray, n_blocks: int = PBO_BLOCKS) -> dict:
    """CSCV PBO over the configurations (V2.9).

    perf: rows = dates (calendar order), columns = configurations. The dates are cut into n_blocks
    contiguous blocks of floor(n / n_blocks) dates, the last taking the remainder; each block's P&L
    is summed per configuration and funnel.multiple_comparisons.probability_of_backtest_overfitting
    receives rows = configurations, columns = blocks.
    """
    mat = np.asarray(perf, dtype=np.float64)
    if mat.ndim != 2:
        raise CPCVError(f"perf must be 2-D (dates x configs), got shape {mat.shape}")
    if not np.isfinite(mat).all():
        raise CPCVError("perf holds a non-finite value")
    n_dates = mat.shape[0]
    width = n_dates // n_blocks
    if width < 1:
        raise CPCVError(f"{n_dates} dates cannot form {n_blocks} blocks")
    edges = [i * width for i in range(n_blocks)] + [n_dates]
    sums = np.stack([mat[edges[i]:edges[i + 1]].sum(axis=0) for i in range(n_blocks)], axis=1)
    res = probability_of_backtest_overfitting(sums.tolist(), n_blocks)
    return {"pbo": res.pbo, "n_splits": res.n_splits, "n_strategies": res.n_strategies,
            "n_blocks": n_blocks, "n_dates": n_dates,
            "block_dates": [edges[i + 1] - edges[i] for i in range(n_blocks)],
            "degenerate": res.degenerate, "note": res.note}


def sharpe_variance(sharpes: Sequence[float]) -> float:
    """Population variance of the configurations' daily Sharpes (as D.1's dsr_table)."""
    xs = np.asarray(sharpes, dtype=np.float64)
    if xs.size == 0 or not np.isfinite(xs).all():
        raise CPCVError("Sharpe variance needs finite Sharpes")
    return float(xs.var(ddof=0))


def dsr_at_n(daily: np.ndarray, n_trials: int, sharpe_variance: float) -> dict:
    """DSR of a daily series at N trials (funnel.multiple_comparisons.deflated_sharpe_ratio).

    Moments are ml_route.accounting.moments (population sd, raw kurtosis), daily, unannualized.
    """
    xs = np.asarray(daily, dtype=np.float64).ravel()
    if not np.isfinite(xs).all():
        raise CPCVError("daily series holds a non-finite value")
    if xs.size < 2:
        return {"status": "undefined", "reason": "fewer than 2 dates", "n_trials": n_trials}
    mom = moments(xs.tolist())
    if mom["sd"] <= 0:
        return {"status": "undefined", "reason": "sd = 0", "n_trials": n_trials, "moments": mom}
    try:
        out = deflated_sharpe_ratio(mom["sharpe"], mom["n"], int(n_trials), float(sharpe_variance),
                                    mom["skew"], mom["kurtosis"])
    except ValueError as exc:
        return {"status": "undefined", "reason": str(exc), "n_trials": n_trials, "moments": mom}
    return {"status": "computed", **out, "moments": mom}
