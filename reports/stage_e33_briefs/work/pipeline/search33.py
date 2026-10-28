"""Stage E.33 pipeline A search engine (SearchCoder).

One configuration (feature set, label, grid point) -> six P6.1 folds with P5's models, P3.5's EV rule,
P3.8's simulation and P6.2's statistics, written per INTERFACE.md 4.3 under <root>/search/<config_id>/.
<root> is the real DERIVED tree or a synthetic proof tree (DERIVED/proofs/seed<s>/): the engine reads
features and labels only through the INTERFACE.md 4.1 and 4.2 schemas.

Protocol: reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...), cited P<n>. Readings are marked
`# READING S<n>` and logged in reports/stage_e33_briefs/work/SearchCoder_readings.md.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
import traceback
import warnings
from dataclasses import dataclass
from datetime import date as _date
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from screening.stage_e_verdict import moments, t_stat  # noqa: E402  (0.3, P6.2)

# ---------------------------------------------------------------- declared constants (P5, P6.1, P3.8)
SEED = 20261027
N_OOF = 796
N_FOLDS = 6
EMBARGO = 21
FOLD_SIZES_796 = (133, 133, 133, 133, 132, 132)
TRAIN_DATES_796 = (642, 642, 642, 642, 643, 664)
ENTRY_CAP = 20
N_FEATURE_MINUTES = 273
DATE_MIN, DATE_MAX = "2020-12-01", "2024-02-29"  # P1.4 universe; nothing on or after 2024-03-01 (P1.2)
CLASSES = (-1, 0, 1)

LOGIT_MAX_ITER, LOGIT_TOL = 2000, 1e-4
LGBM_ROUNDS, LGBM_STOP, INNER_VAL_PCT = 500, 50, 15
CAL_C, CAL_MAX_ITER, CAL_TOL = 1e4, 1000, 1e-6

_FAMILIES = (("C", 15), ("F1", 8), ("F2", 11), ("F3", 12), ("F4", 13))
FEATURE_COLUMNS = tuple(f"{fam}_{j}" for fam, n in _FAMILIES for j in range(1, n + 1))
_FAM_COLS = {fam: tuple(f"{fam}_{j}" for j in range(1, n + 1)) for fam, n in _FAMILIES}
SETS = {"S1": _FAM_COLS["C"] + _FAM_COLS["F1"], "S2": _FAM_COLS["C"] + _FAM_COLS["F2"],
        "S3": _FAM_COLS["C"] + _FAM_COLS["F3"], "S4": _FAM_COLS["C"] + _FAM_COLS["F4"],
        "S5": FEATURE_COLUMNS}
LABEL_H = {"F05": 5, "F15": 15, "F30": 30, "F60": 60, "T15": 15, "T30": 30}
GRID = {"L001A": ("LOGIT", {"C": 0.01, "rho": 0.0}), "L001E": ("LOGIT", {"C": 0.01, "rho": 0.5}),
        "L010A": ("LOGIT", {"C": 0.1, "rho": 0.0}), "L010E": ("LOGIT", {"C": 0.1, "rho": 0.5}),
        "L100A": ("LOGIT", {"C": 1.0, "rho": 0.0}), "L100E": ("LOGIT", {"C": 1.0, "rho": 0.5}),
        "G2050": ("LGBM", {"depth": 2, "leaf_mult": 50}), "G2200": ("LGBM", {"depth": 2, "leaf_mult": 200}),
        "G3050": ("LGBM", {"depth": 3, "leaf_mult": 50}), "G3200": ("LGBM", {"depth": 3, "leaf_mult": 200})}
SET_ORDER = ("S5", "S1", "S3", "S2", "S4")          # P5 run order
LABEL_ORDER = ("F15", "F30", "F05", "F60", "T15", "T30")
GRID_ORDER = tuple(GRID)                              # P7.1 order
ID_PREFIXES = ("E33", "E33A")                         # P7.1; E33A = P4.1 LT7 re-registration

SIDE_FIELDS = ("made", "net", "entry_ns", "exit_ns", "flags")
LABEL_COLUMNS = ("i", "t_ns", "entry_ok", "row_ok", "y", "n_long", "n_short", "w", "span_end_ns") + tuple(
    f"{s}_{f}" for s in ("long", "short") for f in SIDE_FIELDS)
OPTIONAL_LABEL_COLUMNS = ("mid_move",)  # READING S8: reported-only mid-sign hit rate needs it


class FitError(RuntimeError):
    """A fit that raised or gave non-finite probabilities: the configuration is failed (P5 DO-22)."""


class StaleMarkerError(RuntimeError):
    """A marker written by another pipeline version or on other tables (SF1): the run refuses it."""


PIPE_DIR = Path(__file__).resolve().parent


def pipeline_files() -> list:
    """search33.py, run_search33.py and every pipeline/ module they import, transitively (SF1)."""
    import ast
    seen: dict = {}
    todo = ["search33", "run_search33"]
    while todo:
        name = todo.pop()
        path = PIPE_DIR / f"{name}.py"
        if name in seen or not path.exists():
            continue
        seen[name] = path
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                todo += [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                todo.append(node.module.split(".")[0])
    return [seen[n] for n in sorted(seen)]


def _pipeline_sha() -> str:
    h = hashlib.sha256()
    for path in pipeline_files():
        h.update(path.name.encode() + b"\0" + hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


PIPELINE_SHA = _pipeline_sha()  # the code this process runs (taken at import)


# ---------------------------------------------------------------- configurations
@dataclass(frozen=True)
class Config:
    cid: str
    prefix: str
    set_name: str
    label: str
    grid: str
    h: int
    family: str
    params: dict
    columns: tuple


def parse_config_id(cid: str) -> Config:
    prefix, _, body = cid.partition("-")
    if prefix not in ID_PREFIXES or len(body) != 10:
        raise ValueError(f"not a P7.1 id: {cid!r}")
    set_name, label, grid = body[:2], body[2:5], body[5:]
    if set_name not in SETS or label not in LABEL_H or grid not in GRID:
        raise ValueError(f"not a P7.1 id: {cid!r}")
    family, params = GRID[grid]
    return Config(cid, prefix, set_name, label, grid, LABEL_H[label], family, dict(params), SETS[set_name])


def all_config_ids(prefix: str = "E33") -> list[str]:
    """The 300 P7.1 ids in P5's run order (set, label, grid)."""
    return [f"{prefix}-{s}{lab}{g}" for s in SET_ORDER for lab in LABEL_ORDER for g in GRID_ORDER]


def grid_size(h: int) -> int:
    """|G_h(D)|: minutes i = 0..277-h (INTERFACE 3)."""
    return 278 - h


# ---------------------------------------------------------------- folds (P6.1)
@dataclass(frozen=True)
class Fold:
    k: int
    eval_dates: tuple
    train_dates: tuple
    embargo_dates: tuple


def fold_sizes(n: int) -> tuple:
    base, rem = divmod(n, N_FOLDS)
    return tuple(base + (1 if k < rem else 0) for k in range(N_FOLDS))


def make_folds(dates, embargo: int = EMBARGO, expected_n: int | None = N_OOF) -> list[Fold]:
    dates = tuple(dates)
    if list(dates) != sorted(set(dates)):
        raise ValueError("OOF dates must be unique and sorted")
    if expected_n is not None and len(dates) != expected_n:
        raise ValueError(f"{len(dates)} OOF dates, expected {expected_n}")
    sizes = fold_sizes(len(dates))
    if len(dates) == N_OOF and sizes != FOLD_SIZES_796:
        raise AssertionError(sizes)
    folds, start = [], 0
    for k, size in enumerate(sizes, 1):
        ev = dates[start:start + size]
        emb = dates[start + size:start + size + embargo]
        drop = set(ev) | set(emb)
        folds.append(Fold(k, ev, tuple(d for d in dates if d not in drop), emb))
        start += size
    if len(dates) == N_OOF and tuple(len(f.train_dates) for f in folds) != TRAIN_DATES_796:
        raise AssertionError([len(f.train_dates) for f in folds])
    return folds


# ---------------------------------------------------------------- tables (INTERFACE 4.1, 4.2)
@dataclass
class Tables:
    dates: tuple
    label: str
    h: int
    feat_sha: str
    label_sha: str
    date_idx: np.ndarray
    i: np.ndarray
    t_ns: np.ndarray
    X: np.ndarray          # all 59 FEATURE_COLUMNS, rows = label grid rows
    lab: dict              # label columns (LABEL_COLUMNS minus i, t_ns; plus optional ones present)
    sigma_zm: np.ndarray   # per OOF date (P8 G5 d)
    fingerprint: str = ""  # sha256 over every table file read (SF1)

    def cols(self, columns) -> np.ndarray:
        idx = [FEATURE_COLUMNS.index(c) for c in columns]
        return np.ascontiguousarray(self.X[:, idx])


def resolve_sha_dir(parent: Path, sha: str | None) -> Path:
    if sha:
        path = parent / sha
        if not path.is_dir():
            raise FileNotFoundError(path)
        return path
    subs = sorted(p for p in parent.iterdir() if p.is_dir() and len(p.name) == 12
                  and all(c in "0123456789abcdef" for c in p.name))
    if len(subs) != 1:  # READING S9: never guess between code versions
        raise ValueError(f"{parent}: {len(subs)} code_sha12 folders; pass the sha explicitly")
    return subs[0]


DERIVED_E33 = Path("/mnt/large-storage/market_data/PropExperiment/derived/e33")


def guard_for(root):
    """guard33 (P1.2) for roots inside the E.33 DERIVED tree (real and proof tables); None for synthetic
    roots elsewhere (tests, scratch), which hold no real data and which the guard's allowlist refuses
    by design. READING S12."""
    try:
        Path(root).resolve().relative_to(DERIVED_E33.resolve())
    except ValueError:
        return None
    import guard33  # pipeline A (DataCoder)
    return guard33


def _date_files(folder: Path) -> list[str]:
    return sorted(p.stem for p in folder.glob("*.parquet"))


def _check_dates(dates) -> None:
    for d in dates:
        _date.fromisoformat(d)
        if not (DATE_MIN <= d <= DATE_MAX):  # P1.2: refuse dates outside the discovery universe
            raise ValueError(f"date {d} outside {DATE_MIN}..{DATE_MAX}")


def _read_bytes(path: Path, digest, tag: str) -> bytes:
    """Read a table file once and add (tag, name, sha256 of its bytes) to the tables fingerprint (SF1)."""
    data = Path(path).read_bytes()
    digest.update(f"{tag}/{Path(path).name}".encode() + b"\0" + hashlib.sha256(data).digest())
    return data


def _read_parquet(source, columns=None) -> dict:
    import pyarrow as pa
    import pyarrow.parquet as pq
    if isinstance(source, bytes):
        source = pa.BufferReader(source)
    table = pq.read_table(source, columns=list(columns) if columns else None)
    return {name: table.column(name).to_numpy(zero_copy_only=False) for name in table.column_names}


_TABLE_CACHE: dict = {}


def load_tables(root, label: str, feat_sha: str | None = None, label_sha: str | None = None,
                expected_n: int | None = N_OOF) -> Tables:
    """Features gathered at the label's grid rows, label fields and sigma_ZM(D); cached per process."""
    root = Path(root)
    fdir = resolve_sha_dir(root / "features", feat_sha)
    ldir = resolve_sha_dir(root / "labels", label_sha) / label
    key = (str(fdir), str(ldir), expected_n)
    if key in _TABLE_CACHE:
        return _TABLE_CACHE[key]
    h = LABEL_H[label]
    dates = tuple(_date_files(fdir))
    if tuple(_date_files(ldir)) != dates:
        raise ValueError(f"feature dates and {label} label dates differ")
    if expected_n is not None and len(dates) != expected_n:
        raise ValueError(f"{len(dates)} OOF dates, expected {expected_n}")
    _check_dates(dates)
    guard = guard_for(root)
    if guard is not None:  # READING S12: folders once (15 ms a call), dates each, symlinked files each
        for folder in (fdir, ldir, fdir / "_day"):
            guard.check_path(folder)
    gs = grid_size(h)
    digest = hashlib.sha256(f"{label}".encode())
    parts_x, parts_t, parts_lab = [], [], []
    for d in dates:
        if guard is not None:
            guard.check_date(d, where="search33")
            for path in (fdir / f"{d}.parquet", ldir / f"{d}.parquet", fdir / "_day" / f"{d}.json"):
                if path.is_symlink():
                    guard.check_path(path)
        feat = _read_parquet(_read_bytes(fdir / f"{d}.parquet", digest, "features"),
                             ("date", "i", "t_ns") + FEATURE_COLUMNS)
        order = np.argsort(feat["i"], kind="stable")
        if not np.array_equal(feat["i"][order], np.arange(N_FEATURE_MINUTES)):
            raise ValueError(f"{d}: feature minutes are not 0..272")
        if not np.all(feat["date"] == d):
            raise ValueError(f"{d}: feature 'date' column mismatch")
        x = np.column_stack([np.asarray(feat[c], dtype=np.float64)[order] for c in FEATURE_COLUMNS])
        if not np.all(np.isfinite(x)):
            raise ValueError(f"{d}: non-finite feature values (G3 makes invalid features 0)")
        lab = _read_parquet(_read_bytes(ldir / f"{d}.parquet", digest, "labels"))
        missing = [c for c in LABEL_COLUMNS if c not in lab]
        if missing:
            raise ValueError(f"{d}: label table lacks {missing}")
        lorder = np.argsort(lab["i"], kind="stable")
        lab = {c: np.asarray(v)[lorder] for c, v in lab.items()}
        if not np.array_equal(lab["i"], np.arange(gs)):
            raise ValueError(f"{d}: {label} rows are not the grid 0..{gs - 1}")
        t_feat = np.asarray(feat["t_ns"], dtype=np.int64)[order][: gs]
        if not np.array_equal(t_feat, lab["t_ns"].astype(np.int64)):
            raise ValueError(f"{d}: t_ns of features and labels differ")
        parts_x.append(x[:gs])
        parts_t.append(t_feat)
        parts_lab.append(lab)
    sigma = np.array([_sigma_zm(fdir, d, digest) for d in dates], dtype=np.float64)
    labcols = {}
    for c in LABEL_COLUMNS[2:] + OPTIONAL_LABEL_COLUMNS:
        present = [c in p for p in parts_lab]
        if all(present):
            labcols[c] = np.concatenate([p[c] for p in parts_lab])
            if c in OPTIONAL_LABEL_COLUMNS:
                labcols[c] = labcols[c].astype(np.float64)
        elif any(present):
            raise ValueError(f"label column {c} present on some dates only")
    for c in ("entry_ok", "row_ok", "long_made", "short_made"):
        labcols[c] = labcols[c].astype(bool)
    labcols["y"] = labcols["y"].astype(np.int8)
    tables = Tables(dates=dates, label=label, h=h, feat_sha=fdir.name, label_sha=ldir.parent.name,
                    date_idx=np.repeat(np.arange(len(dates), dtype=np.int32), gs),
                    i=np.tile(np.arange(gs, dtype=np.int16), len(dates)),
                    t_ns=np.concatenate(parts_t), X=np.concatenate(parts_x), lab=labcols, sigma_zm=sigma,
                    fingerprint=digest.hexdigest())
    _check_rows(tables)
    _TABLE_CACHE.clear()  # one table per process: about 0.13 GB for S5 at 209,000 grid rows
    _TABLE_CACHE[key] = tables
    return tables


def _sigma_zm(fdir: Path, d: str, digest) -> float:
    value = json.loads(_read_bytes(fdir / "_day" / f"{d}.json", digest, "day")).get("sigma_zm")
    # READING S5: an OOF date without a finite positive sigma_ZM(D) stops the run (G5 d undefined)
    if value is None or not math.isfinite(float(value)) or float(value) <= 0:
        raise ValueError(f"{d}: sigma_zm {value!r} is not finite and positive")
    return float(value)


def _check_rows(t: Tables) -> None:
    lab, ok = t.lab, t.lab["row_ok"]
    if not np.all(np.isin(lab["y"][ok], CLASSES)):
        raise ValueError("y outside {-1, 0, 1} on a row")
    for c in ("n_long", "n_short", "w"):
        if not np.all(np.isfinite(lab[c][ok])):
            raise ValueError(f"non-finite {c} on a row")
    if not np.all(lab["w"][ok] > 0):
        raise ValueError("non-positive weight on a row")
    if np.any(lab["y"][~ok] != 0):
        raise ValueError("y != 0 outside rows")
    if t.label.startswith("F") and (np.any(ok & (lab["y"] == 1) & ~(lab["n_long"] > 0)) or
                                    np.any(ok & (lab["y"] == -1) & ~(lab["n_short"] > 0)) or
                                    np.any(ok & (lab["y"] == 0) & ((lab["n_long"] > 0) | (lab["n_short"] > 0)))):
        raise ValueError("FH class and net disagree (P3.3)")  # TB classes follow the mid barrier (P3.4)


# ---------------------------------------------------------------- fold arrays
def date_mask(tables: Tables, dates) -> np.ndarray:
    pick = np.zeros(len(tables.dates), dtype=bool)
    pos = {d: j for j, d in enumerate(tables.dates)}
    pick[[pos[d] for d in dates]] = True
    return pick[tables.date_idx]


def training_mask(tables: Tables, fold: Fold) -> np.ndarray:
    """Training rows = row_ok rows on the fold's training dates (P6.1, P3.7)."""
    return date_mask(tables, fold.train_dates) & tables.lab["row_ok"]


def class_means(y, w, n_long, n_short) -> tuple:
    """mu_long_k and mu_short_k, k in (-1, 0, +1): weighted means over training rows with y = k (P3.5)."""
    mu_l, mu_s = [], []
    for k in CLASSES:
        m = y == k
        sw = float(np.sum(w[m])) if np.any(m) else 0.0
        if sw <= 0:  # READING S1: a class without a training row fails the fit (P5 failed fits)
            raise FitError(f"class {k} has no training row")
        mu_l.append(float(np.sum(w[m] * n_long[m]) / sw))
        mu_s.append(float(np.sum(w[m] * n_short[m]) / sw))
    return mu_l, mu_s


def weighted_scaler(X: np.ndarray, w: np.ndarray) -> tuple:
    """G5: weighted mean and population-weighted SD (0.3) of the training fold; SD 0 -> feature 0."""
    sw = np.sum(w)
    mean = np.sum(w[:, None] * X, axis=0) / sw
    sd = np.sqrt(np.sum(w[:, None] * (X - mean) ** 2, axis=0) / sw)
    constant = np.max(X, axis=0) == np.min(X, axis=0)  # READING S2: exact SD 0 = a constant column
    sd = np.where(constant | (sd == 0), 0.0, sd)
    return mean, sd


def standardise(X: np.ndarray, mean, sd) -> np.ndarray:
    mean, sd = np.asarray(mean, dtype=np.float64), np.asarray(sd, dtype=np.float64)
    Z = np.zeros(X.shape, dtype=np.float64)
    live = sd > 0
    Z[:, live] = (X[:, live] - mean[live]) / sd[live]
    return Z


def _linear(Z: np.ndarray, coef, intercept) -> np.ndarray:
    """Logits with a fixed summation order (no BLAS), so predictions are bit-reproducible."""
    coef, intercept = np.asarray(coef, dtype=np.float64), np.asarray(intercept, dtype=np.float64)
    out = np.empty((Z.shape[0], coef.shape[0]), dtype=np.float64)
    for c in range(coef.shape[0]):
        acc = np.full(Z.shape[0], intercept[c], dtype=np.float64)
        for j in range(coef.shape[1]):
            acc += Z[:, j] * coef[c, j]
        out[:, c] = acc
    return out


def _softmax(logits: np.ndarray) -> np.ndarray:
    e = np.exp(logits - logits.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def make_logit(C: float, rho: float, *, max_iter: int = LOGIT_MAX_ITER, tol: float = LOGIT_TOL):
    """P5 LOGIT. sklearn 1.9.1: `penalty` is deprecated (left at its default) and the penalty is set by
    l1_ratio (0 -> L2, 0.5 -> elastic net); there is no multi_class parameter and saga minimises the
    multinomial loss for 3 classes: C sum_i s_i l_i + (1 - l1_ratio)/2 ||b||^2 + l1_ratio ||b||_1,
    intercepts unpenalised (proved in tests/test_search33.py)."""
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(C=C, l1_ratio=rho, solver="saga", max_iter=max_iter, tol=tol,
                              random_state=SEED)


def make_calibrator():
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(C=CAL_C, solver="lbfgs", max_iter=CAL_MAX_ITER, tol=CAL_TOL)


def _fit_recorded(est, X, y, w) -> list:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            est.fit(X, y, sample_weight=w)
        except (ValueError, ArithmeticError, np.linalg.LinAlgError) as exc:  # SF2: the fit's own failure
            raise FitError(f"{type(exc).__name__} in {type(est).__name__}.fit: {exc}") from exc
    if tuple(int(c) for c in est.classes_) != CLASSES:
        raise FitError(f"classes {est.classes_} != {CLASSES}")
    return sorted({f"{w_.category.__name__}: {w_.message}" for w_ in caught})


def lgb_call(fn, *args, **kwargs):
    """A LightGBM call. SF2: its own error (LightGBMError) is a failed fit, except a C++ allocation
    failure (std::bad_alloc), which is an out-of-memory interruption (P5, P10)."""
    import lightgbm as lgb
    try:
        return fn(*args, **kwargs)
    except lgb.basic.LightGBMError as exc:
        if "bad_alloc" in str(exc):
            raise MemoryError(f"LightGBM: {exc}") from exc
        raise FitError(f"LightGBMError: {exc}") from exc


def lgbm_params(depth: int, leaf_mult: int, h: int, threads: int) -> dict:
    return {"objective": "multiclass", "num_class": 3, "boosting": "gbdt", "learning_rate": 0.05,
            "max_depth": depth, "num_leaves": 2 ** depth, "min_data_in_leaf": leaf_mult * h,
            "feature_fraction": 0.8, "bagging_fraction": 0.8, "bagging_freq": 1, "lambda_l2": 1.0,
            "min_gain_to_split": 0.0, "max_bin": 255, "seed": SEED, "deterministic": True,
            "force_row_wise": True, "num_threads": threads, "metric": "None", "verbosity": -1}


LOG_EPS = 1e-15  # LightGBM's kEpsilon in multi_logloss


def weighted_mlogloss_feval(y: np.ndarray, w: np.ndarray):
    """P5's early-stopping metric, the weighted multi_logloss of the inner validation block, as a
    LightGBM feval: float64 weights and a fixed summation order. READING S11: LightGBM's built-in
    metric casts weights to float32 and sums with an OpenMP reduction whose order varies between runs,
    which can move the stopping point between reruns (seen in testing)."""
    y = np.asarray(y, dtype=np.int64)
    w = np.asarray(w, dtype=np.float64)
    rows, sw = np.arange(len(y)), float(np.sum(w))

    def feval(preds, _data):
        p = np.asarray(preds, dtype=np.float64).reshape(len(y), 3)[rows, y]
        return "w_multi_logloss", float(np.sum(w * -np.log(np.maximum(p, LOG_EPS))) / sw), False
    return feval


def inner_split(train_dates) -> tuple:
    """Inner validation = the latest 15% of the fold's training dates, rounded up to whole dates (P5)."""
    n_val = (INNER_VAL_PCT * len(train_dates) + 99) // 100
    return tuple(train_dates[:-n_val]), tuple(train_dates[-n_val:])


# ---------------------------------------------------------------- fold models
def fit_logit(cfg: Config, Xtr, ytr, wtr) -> tuple:
    mean, sd = weighted_scaler(Xtr, wtr)
    est = make_logit(cfg.params["C"], cfg.params["rho"])
    caught = _fit_recorded(est, standardise(Xtr, mean, sd), ytr, wtr)
    n_iter = int(np.max(est.n_iter_))
    model = {"family": "LOGIT", "classes": list(CLASSES), "columns": list(cfg.columns),
             "mean": mean.tolist(), "sd": sd.tolist(), "coef": est.coef_.tolist(),
             "intercept": est.intercept_.tolist()}
    meta = {"n_iter": n_iter, "converged": n_iter < LOGIT_MAX_ITER, "warnings": caught,
            "n_zero_sd": int(np.sum(sd == 0))}
    return model, meta


def fit_lgbm(cfg: Config, tables: Tables, fold: Fold, threads: int) -> tuple:
    import lightgbm as lgb
    inner_tr, inner_val = inner_split(fold.train_dates)
    ok = tables.lab["row_ok"]
    m_tr, m_val = date_mask(tables, inner_tr) & ok, date_mask(tables, inner_val) & ok
    if not m_tr.any() or not m_val.any():
        raise FitError("empty inner block")
    X = tables.cols(cfg.columns)
    y, w = tables.lab["y"].astype(np.int64), tables.lab["w"]
    params = lgbm_params(cfg.params["depth"], cfg.params["leaf_mult"], cfg.h, threads)
    dtr = lgb.Dataset(X[m_tr], label=y[m_tr] + 1, weight=w[m_tr], params=params, free_raw_data=False)
    dval = lgb.Dataset(X[m_val], label=y[m_val] + 1, weight=w[m_val], reference=dtr, params=params,
                       free_raw_data=False)
    history: dict = {}
    booster = lgb_call(lgb.train, params, dtr, num_boost_round=LGBM_ROUNDS, valid_sets=[dval],
                        valid_names=["inner_val"], feval=weighted_mlogloss_feval(y[m_val] + 1, w[m_val]),
                        callbacks=[lgb.early_stopping(LGBM_STOP, first_metric_only=True, verbose=False),
                                   lgb.record_evaluation(history)])
    best_reported, built = int(booster.best_iteration), int(booster.current_iteration())
    # when no leaf can split any more, LightGBM adds no trees but keeps evaluating the same model:
    # the model at a later "best" iteration is the model with all `built` iterations
    best = min(best_reported, built)
    if best < 1:
        raise FitError(f"best_iteration {best_reported}, built {built}")
    model_str = booster.model_to_string(num_iteration=best)
    kept = lgb_call(lgb.Booster, model_str=model_str)
    if kept.current_iteration() != best:
        raise FitError("kept booster has the wrong number of iterations")
    raw_val = lgb_call(kept.predict, X[m_val], raw_score=True, num_threads=threads)
    cal = make_calibrator()
    yv = tables.lab["y"][m_val].astype(np.int64)
    if set(np.unique(yv).tolist()) != set(CLASSES):  # READING S1 (calibrator side)
        raise FitError("inner validation block lacks a class")
    caught = _fit_recorded(cal, raw_val, yv, w[m_val])
    cal_iter = int(np.max(cal.n_iter_))
    model = {"family": "LGBM", "classes": list(CLASSES), "columns": list(cfg.columns),
             "booster": model_str, "best_iteration": best, "cal_coef": cal.coef_.tolist(),
             "cal_intercept": cal.intercept_.tolist()}
    meta = {"best_iteration": best, "best_iteration_reported": best_reported, "iterations_built": built,
            "rounds_run": len(history["inner_val"]["w_multi_logloss"]),
            "inner_val_logloss": history["inner_val"]["w_multi_logloss"],
            "cal_n_iter": cal_iter, "cal_converged": cal_iter < CAL_MAX_ITER, "warnings": caught,
            "n_inner_train_dates": len(inner_tr), "n_inner_val_dates": len(inner_val),
            "n_inner_train_rows": int(m_tr.sum()), "n_inner_val_rows": int(m_val.sum()),
            "trees_sha256": hashlib.sha256(model_str.split("\nparameters:")[0].encode()).hexdigest()}
    return model, meta


def fit_fold(cfg: Config, tables: Tables, fold: Fold, threads: int = 1) -> tuple:
    """Fit one fold; returns (model dict incl. mu_k, meta). Raises FitError on a failed fit."""
    m_tr = training_mask(tables, fold)
    lab = tables.lab
    ytr, wtr = lab["y"][m_tr].astype(np.int64), lab["w"][m_tr]
    mu_long, mu_short = class_means(ytr, wtr, lab["n_long"][m_tr], lab["n_short"][m_tr])
    t0 = time.perf_counter()
    if cfg.family == "LOGIT":
        model, meta = fit_logit(cfg, tables.cols(cfg.columns)[m_tr], ytr, wtr)
    else:
        model, meta = fit_lgbm(cfg, tables, fold, threads)
    meta["seconds"] = time.perf_counter() - t0
    model.update({"config": cfg.cid, "fold": fold.k, "mu_long": mu_long, "mu_short": mu_short,
                  "seed": SEED, "versions": library_versions()})
    meta.update({"seed": SEED, "threads": threads, "n_train_rows": int(m_tr.sum()),
                 "n_train_dates": len(fold.train_dates), "n_eval_dates": len(fold.eval_dates)})
    return model, meta


def model_bytes(model: dict) -> bytes:
    """Canonical JSON: floats round-trip exactly (repr), keys sorted, so the bytes are deterministic."""
    return json.dumps(model, sort_keys=True, allow_nan=False).encode()


def load_fold_model(path) -> dict:
    with open(path, "rb") as fh:
        model = json.loads(fh.read())
    if model["family"] == "LGBM":
        import lightgbm as lgb
        model["_booster"] = lgb_call(lgb.Booster, model_str=model["booster"])
    return model


def predict_proba(model: dict, X: np.ndarray, threads: int = 1) -> np.ndarray:
    """Calibrated (p_-1, p_0, p_+1) of a stored fold model; X holds the model's columns in order."""
    X = np.ascontiguousarray(X, dtype=np.float64)
    if X.ndim != 2 or X.shape[1] != len(model["columns"]):
        raise ValueError("X does not match the model's columns")
    if model["family"] == "LOGIT":
        logits = _linear(standardise(X, model["mean"], model["sd"]), model["coef"], model["intercept"])
    else:
        booster = model.get("_booster")
        if booster is None:
            import lightgbm as lgb
            booster = model["_booster"] = lgb_call(lgb.Booster, model_str=model["booster"])
        raw = lgb_call(booster.predict, X, raw_score=True, num_threads=threads)
        logits = _linear(np.ascontiguousarray(raw, dtype=np.float64), model["cal_coef"], model["cal_intercept"])
    return _softmax(logits)


# ---------------------------------------------------------------- EV rule and simulation (P3.5, P3.8)
def expected_values(p: np.ndarray, mu_long, mu_short) -> tuple:
    """EV_side = sum_k p_k mu_side_k, summed in class order (-1, 0, +1)."""
    ev_l = p[:, 0] * mu_long[0] + p[:, 1] * mu_long[1] + p[:, 2] * mu_long[2]
    ev_s = p[:, 0] * mu_short[0] + p[:, 1] * mu_short[1] + p[:, 2] * mu_short[2]
    return ev_l, ev_s


def decide(ev_long: float, ev_short: float) -> int:
    """P3.5: +1 long if EV_long > max(EV_short, 0); -1 short if EV_short > max(EV_long, 0); else 0."""
    ev_long, ev_short = float(ev_long), float(ev_short)
    if not (math.isfinite(ev_long) and math.isfinite(ev_short)):
        raise ValueError(f"non-finite EV ({ev_long}, {ev_short})")
    if ev_long > max(ev_short, 0.0):
        return 1
    if ev_short > max(ev_long, 0.0):
        return -1
    return 0


def simulate_date(t_ns, entry_ok, ev_long, ev_short, outcome: dict) -> tuple:
    """One date's P3.8 simulation. outcome[side][field] are arrays over the date's grid minutes.
    Returns (trades, not_made): lists of (row position, side, ...)."""
    trades, not_made = [], []
    n, pos, entries = len(t_ns), 0, 0
    while pos < n and entries < ENTRY_CAP:
        if not entry_ok[pos]:
            pos += 1
            continue
        side = decide(ev_long[pos], ev_short[pos])
        if side == 0:
            pos += 1
            continue
        o = outcome["long" if side == 1 else "short"]
        if not o["made"][pos]:
            # READING S3: an entry not made leaves the account flat; the next minute is decided, and it
            # does not count toward the cap of 20 entries made
            not_made.append((pos, side, int(o["flags"][pos])))
            pos += 1
            continue
        net, ent, ext = float(o["net"][pos]), int(o["entry_ns"][pos]), int(o["exit_ns"][pos])
        if not math.isfinite(net) or ent < t_ns[pos] or ext <= ent:
            raise ValueError(f"inconsistent made trade at grid position {pos}")
        trades.append((pos, side, net, ent, ext, int(o["flags"][pos])))
        entries += 1
        nxt = int(np.searchsorted(t_ns, ext, side="left"))  # first grid minute at or after the exit fill
        if nxt <= pos:
            raise ValueError("next decision not after the entry")
        pos = nxt
    return trades, not_made


# ---------------------------------------------------------------- outputs and statistics (P6.2)
def config_dir(root, cid: str) -> Path:
    return Path(root) / "search" / cid


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_write_bytes(path: Path, data: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def atomic_write_json(path: Path, obj) -> None:
    atomic_write_bytes(path, json.dumps(obj, sort_keys=True, indent=1, allow_nan=False).encode())


def library_versions() -> dict:
    import lightgbm
    import sklearn
    return {"python": sys.version.split()[0], "numpy": np.__version__, "sklearn": sklearn.__version__,
            "lightgbm": lightgbm.__version__}


def now_local() -> str:
    return datetime.now(UTC).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def _quarter_key(d: str) -> str:
    y, m = int(d[:4]), int(d[5:7])
    if m == 12:
        return f"{y:04d}-12"
    if m <= 2:
        return f"{y - 1:04d}-12"
    return f"{y:04d}-{3 * (m // 3):02d}"


def _group(dates, x, keyf) -> dict:
    out: dict = {}
    for d, v in zip(dates, x, strict=True):
        out.setdefault(keyf(d), []).append(float(v))
    return {k: {"sum": float(sum(v)), "mean": float(sum(v) / len(v)), "n_dates": len(v)} for k, v in out.items()}


def _pearson(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    if len(a) < 2 or np.std(a) == 0 or np.std(b) == 0:
        return None
    return float(np.corrcoef(a, b)[0, 1])


def vol_terciles(dates, sigma, x) -> dict:
    """P8 G5 (d): dates sorted by sigma_ZM(D) ascending, ties by date; ranks 1-265, 266-530, 531-796."""
    order = sorted(range(len(dates)), key=lambda j: (sigma[j], dates[j]))
    n3 = len(dates) // 3
    cuts = ((0, n3), (n3, 2 * n3), (2 * n3, len(dates)))
    return {str(t + 1): {"mean": float(np.mean([x[j] for j in order[a:b]])), "n_dates": b - a,
                         "sigma_min": float(sigma[order[a]]), "sigma_max": float(sigma[order[b - 1]])}
            for t, (a, b) in enumerate(cuts)}


def reported_only(tables: Tables, ev_l, ev_s) -> dict:
    """P6.2 reported-only items over all OOF rows (READING S7, S8)."""
    rows = tables.lab["row_ok"] & (ev_l != ev_s)
    side = np.where(ev_l > ev_s, 1, -1)[rows]
    ev = np.maximum(ev_l, ev_s)[rows]
    net = np.where(side == 1, tables.lab["n_long"][rows], tables.lab["n_short"][rows])
    out = {"n_rows": int(rows.sum()), "rho_chosen_ev_net_rows": _pearson(ev, net)}
    k = math.ceil(len(ev) / 10)
    order = np.lexsort((tables.i[rows], tables.date_idx[rows], -ev))[:k]
    out.update({"top_decile_n": int(k), "top_decile_mean_net": float(np.mean(net[order])) if k else None})
    return out


MID_SIGN_RULE = ("share of trades whose realised mid move M_ZM(t + L + h) - M_ZM(t + L) (label column mid_move; "
                 "TB: the vertical h) has the sign of the chosen side; trades whose mid_move is NaN or exactly 0 "
                 "are left out of the share and counted in n_nan and n_zero")


def mid_sign_hit(mid_move, side) -> dict:
    """P6.2 reported-only hit rate of the realised mid-move sign given the chosen side (READING S8)."""
    mv = np.asarray(mid_move, dtype=np.float64)
    side = np.asarray(side, dtype=np.int64)
    nan = ~np.isfinite(mv)
    zero = mv == 0
    used = ~nan & ~zero
    return {"hit_rate": float(np.mean(np.sign(mv[used]) == side[used])) if used.any() else None,
            "n_used": int(used.sum()), "n_nan": int(nan.sum()), "n_zero": int(zero.sum()), "rule": MID_SIGN_RULE}


def run_simulation(tables: Tables, folds, fold_payloads: dict) -> dict:
    """Assemble OOF probabilities from the six folds, run P3.8 on every OOF date, return series + trades."""
    n = len(tables.t_ns)
    ev_l, ev_s = np.full(n, np.nan), np.full(n, np.nan)
    fold_of_date = np.zeros(len(tables.dates), dtype=np.int8)
    for f in folds:
        pay = fold_payloads[f.k]
        m = date_mask(tables, f.eval_dates)
        if not (np.array_equal(pay["t_ns"], tables.t_ns[m]) and np.array_equal(pay["i"], tables.i[m])):
            raise ValueError(f"fold {f.k} rows do not match the label grid")
        if np.any(np.isfinite(ev_l[m])):
            raise ValueError("a row is in two folds")
        ev_l[m], ev_s[m] = expected_values(pay["p"], pay["mu_long"], pay["mu_short"])
        fold_of_date[[tables.dates.index(d) for d in f.eval_dates]] = f.k
    if not (np.all(np.isfinite(ev_l)) and np.all(np.isfinite(ev_s))):
        raise ValueError("a grid row has no OOF prediction")
    lab = tables.lab
    starts = np.searchsorted(tables.date_idx, np.arange(len(tables.dates) + 1))
    x_d, n_tr, trades, not_made, trade_rows = [], [], [], [], []
    for di, d in enumerate(tables.dates):
        a, b = starts[di], starts[di + 1]
        outcome = {s: {f: lab[f"{s}_{f}"][a:b] for f in SIDE_FIELDS} for s in ("long", "short")}
        tr, nm = simulate_date(tables.t_ns[a:b], lab["entry_ok"][a:b], ev_l[a:b], ev_s[a:b], outcome)
        x_d.append(float(sum(t[2] for t in tr)))
        n_tr.append(len(tr))
        for pos, side, net, ent, ext, flags in tr:
            trades.append((d, int(tables.i[a + pos]), side, net, ent, ext, flags,
                           float(ev_l[a + pos]), float(ev_s[a + pos])))
            trade_rows.append(a + pos)
        for pos, side, flags in nm:
            not_made.append((d, int(tables.i[a + pos]), side, flags, float(ev_l[a + pos]), float(ev_s[a + pos])))
    return {"x": x_d, "n_trades": n_tr, "trades": trades, "not_made": not_made, "ev_long": ev_l,
            "ev_short": ev_s, "fold_of_date": fold_of_date, "trade_rows": np.array(trade_rows, dtype=np.int64)}


def compute_stats(tables: Tables, sim: dict) -> dict:
    x, dates = sim["x"], tables.dates
    mom = moments(x)
    nets = [t[3] for t in sim["trades"]]
    flags = [t[6] for t in sim["trades"]]
    n_trades = len(nets)
    trade_ev = [max(t[7], t[8]) for t in sim["trades"]]
    stats = {
        "n_dates": len(dates), "moments": mom, "t_stat": t_stat(mom),
        "trade_count": n_trades, "trades_per_date": n_trades / len(dates),
        "mean_net_per_trade": float(sum(nets) / n_trades) if n_trades else None,
        "hit_rate": float(sum(1 for v in nets if v > 0) / n_trades) if n_trades else None,
        "share_dates_with_trade": sum(1 for c in sim["n_trades"] if c > 0) / len(dates),
        "per_fold": {str(k): {"sum": float(sum(v for v, f in zip(x, sim["fold_of_date"], strict=True) if f == k)),
                              "n_dates": int(np.sum(sim["fold_of_date"] == k))} for k in range(1, N_FOLDS + 1)},
        "per_quarter": _group(dates, x, _quarter_key),
        "per_month": _group(dates, x, lambda d: d[:7]),
        "vol_terciles": vol_terciles(dates, tables.sigma_zm, x),
        "counts": {"entries_not_made": len(sim["not_made"]),
                   "not_made_flag16": sum(1 for t in sim["not_made"] if t[3] & 16),
                   "not_made_flag32": sum(1 for t in sim["not_made"] if t[3] & 32),
                   "entry_fallback_fills": sum(1 for f in flags if f & 1),
                   "exit_fallback_fills": sum(1 for f in flags if f & 2),
                   "exit_limit_marks": sum(1 for f in flags if f & 4),
                   "exit_last_touch_marks": sum(1 for f in flags if f & 8)},
        "reported_only": reported_only(tables, sim["ev_long"], sim["ev_short"]),
    }
    stats["reported_only"]["rho_chosen_ev_net_trades"] = _pearson(trade_ev, nets)
    if "mid_move" in tables.lab:
        stats["reported_only"]["mid_sign"] = mid_sign_hit(tables.lab["mid_move"][sim["trade_rows"]],
                                                          [t[2] for t in sim["trades"]])
        stats["reported_only"]["mid_sign_hit_rate"] = stats["reported_only"]["mid_sign"]["hit_rate"]
    else:
        stats["reported_only"]["mid_sign_hit_rate"] = "not available"
    return stats


# ---------------------------------------------------------------- per-(config, fold) and per-config work
def fold_paths(root, cid: str, k: int) -> dict:
    base = config_dir(root, cid)
    return {"npz": base / f"fold{k}.npz", "model": base / f"fold{k}.model.json",
            "done": base / f"fold{k}.DONE", "failed": base / f"fold{k}.FAILED",
            "attempts": base / f"fold{k}.attempts"}


def read_attempts(root, cid: str, k: int) -> int:
    path = fold_paths(root, cid, k)["attempts"]
    return len(path.read_text().splitlines()) if path.exists() else 0


def record_attempt(root, cid: str, k: int) -> None:
    """P5/P10: one start record per attempt, written before the tables load (SF4)."""
    path = fold_paths(root, cid, k)["attempts"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as fh:
        fh.write(json.dumps({"start": now_local(), "pid": os.getpid(), "pipeline_sha": PIPELINE_SHA}) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _write_failed(paths: dict, cid: str, k: int, exc: Exception, tables) -> dict:
    atomic_write_json(paths["failed"], {"config": cid, "fold": k, "error": repr(exc), "time": now_local(),
                                        "traceback": traceback.format_exc(), "pipeline_sha": PIPELINE_SHA,
                                        "tables_fingerprint": tables.fingerprint})
    return {"config": cid, "fold": k, "status": "failed", "error": repr(exc)}


def run_fold(root, cid: str, k: int, *, feat_sha=None, label_sha=None, threads: int = 1,
             expected_n: int | None = N_OOF) -> dict:
    """Worker entry: fit fold k of cid, write fold<k>.model.json, fold<k>.npz and fold<k>.DONE, or
    fold<k>.FAILED when the fit itself fails (FitError: the fit raised, or non-finite probabilities; P5).
    Every other error (loading, writing, bookkeeping, a code bug, MemoryError) propagates: the fold is
    an interruption, rerun once from the markers, and the runner stops (SF2)."""
    cfg = parse_config_id(cid)
    paths = fold_paths(root, cid, k)
    record_attempt(root, cid, k)
    tables = load_tables(root, cfg.label, feat_sha, label_sha, expected_n)
    fold = make_folds(tables.dates, expected_n=expected_n)[k - 1]
    m_ev = date_mask(tables, fold.eval_dates)
    try:
        model, meta = fit_fold(cfg, tables, fold, threads)
    except FitError as exc:
        return _write_failed(paths, cid, k, exc, tables)
    atomic_write_bytes(paths["model"], model_bytes(model))
    model_sha = sha256_file(paths["model"])
    try:
        p = predict_proba(load_fold_model(paths["model"]), tables.cols(cfg.columns)[m_ev], threads)
        if not np.all(np.isfinite(p)):
            raise FitError("non-finite probabilities")
    except FitError as exc:
        return _write_failed(paths, cid, k, exc, tables)
    meta.update({"model_sha256": model_sha, "feat_sha": tables.feat_sha, "label_sha": tables.label_sha,
                 "eval_first": fold.eval_dates[0], "eval_last": fold.eval_dates[-1],
                 "n_eval_rows": int(m_ev.sum()), "versions": library_versions(), "pipeline_sha": PIPELINE_SHA,
                 "tables_fingerprint": tables.fingerprint})
    tmp = paths["npz"].with_name(paths["npz"].name + ".tmp")
    with open(tmp, "wb") as fh:
        np.savez(fh, date=np.array([tables.dates[j] for j in tables.date_idx[m_ev]]), i=tables.i[m_ev],
                 t_ns=tables.t_ns[m_ev], p=p, mu_long=np.array(model["mu_long"]),
                 mu_short=np.array(model["mu_short"]), meta=np.array(json.dumps(meta, sort_keys=True)))
    os.replace(tmp, paths["npz"])
    atomic_write_json(paths["done"], {"config": cid, "fold": k, "npz_sha256": sha256_file(paths["npz"]),
                                      "model_sha256": model_sha, "seconds": meta["seconds"],
                                      "time": now_local(), "pipeline_sha": PIPELINE_SHA,
                                      "tables_fingerprint": tables.fingerprint})
    return {"config": cid, "fold": k, "status": "done", "seconds": meta["seconds"]}


def check_markers(root, cid: str) -> None:
    """SF1: every marker of cid (DONE, fold DONE, FAILED, attempts records) must carry the running
    pipeline_sha; otherwise refuse with a clear message (READING S21)."""
    base = config_dir(root, cid)
    if not base.exists():
        return
    bad = []
    for path in sorted(base.glob("*DONE")) + sorted(base.glob("*.FAILED")):
        if json.loads(path.read_text()).get("pipeline_sha") != PIPELINE_SHA:
            bad.append(path.name)
    for path in sorted(base.glob("*.attempts")):
        if any(json.loads(line).get("pipeline_sha") != PIPELINE_SHA for line in path.read_text().splitlines()):
            bad.append(path.name)
    if bad:
        raise StaleMarkerError(
            f"{cid}: markers {bad} were written by another pipeline version (running pipeline_sha "
            f"{PIPELINE_SHA[:12]}); refusing to reuse them. Move {base} aside (or delete it) to rerun this "
            f"configuration under the running code.")


def load_fold_payload(root, cid: str, k: int) -> dict:
    paths = fold_paths(root, cid, k)
    done = json.loads(paths["done"].read_text())
    if done.get("pipeline_sha") != PIPELINE_SHA:
        raise StaleMarkerError(f"{cid} fold {k}: DONE written by another pipeline version")
    if sha256_file(paths["npz"]) != done["npz_sha256"] or sha256_file(paths["model"]) != done["model_sha256"]:
        raise ValueError(f"{cid} fold {k}: files changed after their DONE marker")
    with np.load(paths["npz"], allow_pickle=False) as z:
        pay = {name: z[name] for name in z.files}
    pay["meta"] = json.loads(str(pay["meta"]))
    return pay


def fold_state(root, cid: str, k: int) -> str:
    paths = fold_paths(root, cid, k)
    if paths["done"].exists():
        return "done"
    if paths["failed"].exists():
        return "failed"
    return "pending"


def finalize_config(root, cid: str, *, feat_sha=None, label_sha=None,
                    expected_n: int | None = N_OOF) -> dict:
    """After all six folds: P3.8 simulation, daily.parquet, trades.parquet, stats.json and DONE."""
    import pandas as pd
    cfg = parse_config_id(cid)
    base = config_dir(root, cid)
    check_markers(root, cid)
    states = {k: fold_state(root, cid, k) for k in range(1, N_FOLDS + 1)}
    if any(s == "failed" for s in states.values()):
        errors = {k: json.loads(fold_paths(root, cid, k)["failed"].read_text())["error"]
                  for k, s in states.items() if s == "failed"}
        stats = {"config": cid, "failed": True, "errors": errors, "time": now_local(),
                 "pipeline_sha": PIPELINE_SHA}
        atomic_write_json(base / "stats.json", stats)
        atomic_write_json(base / "DONE", {"config": cid, "status": "failed", "time": now_local(),
                                          "stats_sha256": sha256_file(base / "stats.json"),
                                          "pipeline_sha": PIPELINE_SHA})
        return stats
    if any(s != "done" for s in states.values()):
        raise RuntimeError(f"{cid}: folds not finished {states}")
    tables = load_tables(root, cfg.label, feat_sha, label_sha, expected_n)
    folds = make_folds(tables.dates, expected_n=expected_n)
    payloads = {k: load_fold_payload(root, cid, k) for k in range(1, N_FOLDS + 1)}
    for k, pay in payloads.items():
        if (pay["meta"]["feat_sha"], pay["meta"]["label_sha"]) != (tables.feat_sha, tables.label_sha) or \
                pay["meta"].get("tables_fingerprint") != tables.fingerprint:
            raise StaleMarkerError(f"{cid} fold {k} was fitted on other tables (the table files changed); "
                                   f"move {base} aside to refit")
    sim = run_simulation(tables, folds, payloads)
    stats = compute_stats(tables, sim)
    stats.update({"config": cid, "failed": False, "set": cfg.set_name, "label": cfg.label, "h": cfg.h,
                  "family": cfg.family, "params": cfg.params, "feat_sha": tables.feat_sha,
                  "label_sha": tables.label_sha, "seed": SEED, "versions": library_versions(),
                  "pipeline_sha": PIPELINE_SHA, "tables_fingerprint": tables.fingerprint,
                  "folds": {str(k): {key: pay["meta"].get(key) for key in
                                     ("seconds", "n_iter", "converged", "best_iteration", "cal_converged",
                                      "n_train_rows", "model_sha256", "warnings")}
                            for k, pay in payloads.items()}})
    daily = pd.DataFrame({"date": list(tables.dates), "X_D": sim["x"], "n_trades": sim["n_trades"]})
    trades = pd.DataFrame(sim["trades"], columns=["date", "i", "side", "net", "entry_ns", "exit_ns", "flags",
                                                  "ev_long", "ev_short"]).astype(
        {"i": "int16", "side": "int8", "entry_ns": "int64", "exit_ns": "int64", "flags": "int16"})
    not_made = pd.DataFrame(sim["not_made"], columns=["date", "i", "side", "flags", "ev_long", "ev_short"]).astype(
        {"i": "int16", "side": "int8", "flags": "int16"})
    for name, frame in (("daily", daily), ("trades", trades), ("not_made", not_made)):
        tmp = base / f"{name}.parquet.tmp"
        frame.to_parquet(tmp, index=False)
        os.replace(tmp, base / f"{name}.parquet")
    atomic_write_json(base / "stats.json", stats)
    atomic_write_json(base / "DONE", {"config": cid, "status": "ok", "time": now_local(),
                                      **{f"{n}_sha256": sha256_file(base / f"{n}.parquet")
                                         for n in ("daily", "trades", "not_made")},
                                      "stats_sha256": sha256_file(base / "stats.json"),
                                      "pipeline_sha": PIPELINE_SHA, "tables_fingerprint": tables.fingerprint})
    return stats
