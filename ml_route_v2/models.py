"""The two learners of ML route v2: closed-form ridge and shallow LightGBM (V2.6).

- Ridge: X and y are centred on the training rows, the intercept is unpenalized, and
  alpha = lambda x n_train. The coefficients solve (Xc'Xc + alpha I) b = Xc'yc with LAPACK's LU
  solver (np.linalg.solve), which is deterministic for a fixed input and a fixed BLAS thread
  count; the fit runs under ONE BLAS thread (threadpoolctl, RIDGE_BLAS_THREADS; code review C-07),
  so its bytes, and the sha256 a resumed run checks, do not depend on OPENBLAS_NUM_THREADS or the
  machine's cores. Payload: the feature count
  as little-endian int64, the coefficients as little-endian float64, then the intercept as
  little-endian float64.
- LightGBM: L2 regression with constants.LGBM_FIXED (300 rounds, no early stopping, deterministic,
  force_col_wise, 8 threads), max_depth = d, num_leaves = 2**d, and every seed = constants.SEED.
  Payload: Booster.model_to_string() in UTF-8.
- FittedModel.sha256 is the sha256 of the payload: the model's identity (the hash chain of V2.9's
  leakage controls). predict() re-hashes the payload and raises on a mismatch.

Inputs are float64; predictions are float64 in the units of y (the normalized target, V2.5).
ml_route/lstm.py is not reused (V2.6: no deep sequence model).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import cache

import numpy as np
from threadpoolctl import ThreadpoolController

from ml_route_v2.configs import ModelSpec
from ml_route_v2.constants import LGBM_FIXED, SEED

_SEED_KEYS = ("seed", "bagging_seed", "feature_fraction_seed", "data_random_seed", "extra_seed",
              "drop_seed", "objective_seed")
_INT64 = np.dtype("<i8")
_FLOAT64 = np.dtype("<f8")


class ModelError(ValueError):
    """A fit or a prediction got unusable input, or a payload does not match its hash."""


@dataclass(frozen=True)
class FittedModel:
    spec: ModelSpec
    sha256: str
    payload: bytes


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _check_xy(X: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Xa = np.asarray(X, dtype=np.float64)
    ya = np.asarray(y, dtype=np.float64)
    if Xa.ndim != 2:
        raise ModelError(f"X must be 2-D, got shape {Xa.shape}")
    if ya.ndim != 1 or ya.shape[0] != Xa.shape[0]:
        raise ModelError(f"y shape {ya.shape} does not match X rows {Xa.shape[0]}")
    if Xa.shape[0] < 1 or Xa.shape[1] < 1:
        raise ModelError(f"empty design matrix {Xa.shape}")
    if not (np.isfinite(Xa).all() and np.isfinite(ya).all()):
        raise ModelError("X or y holds a non-finite value")
    return Xa, ya


def lgbm_params(depth: int, seed: int = SEED) -> dict:
    """LGBM_FIXED (minus the round count) plus the grid's depth and every seed."""
    out = {k: v for k, v in LGBM_FIXED.items() if k != "num_boost_round"}
    out.update({"max_depth": int(depth), "num_leaves": 2 ** int(depth)})
    out.update({k: int(seed) for k in _SEED_KEYS})
    return out


RIDGE_BLAS_THREADS = 1  # code review C-07


@cache
def _blas_controller() -> ThreadpoolController:
    """Built once, at the first ridge fit (introspection costs about 4 ms a call): it holds
    numpy's BLAS, loaded with numpy, which is the library the fit's matmul and solve call."""
    return ThreadpoolController()


def _fit_ridge(lam: float, X: np.ndarray, y: np.ndarray) -> bytes:
    """The closed-form ridge under RIDGE_BLAS_THREADS BLAS threads (module docstring, C-07)."""
    with _blas_controller().limit(limits=RIDGE_BLAS_THREADS, user_api="blas"):
        return _ridge_payload(lam, X, y)


def _ridge_payload(lam: float, X: np.ndarray, y: np.ndarray) -> bytes:
    n, p = X.shape
    x_mean = X.mean(axis=0)
    y_mean = float(y.mean())
    Xc = X - x_mean
    yc = y - y_mean
    alpha = float(lam) * n
    gram = Xc.T @ Xc
    gram[np.diag_indices(p)] += alpha
    coef = np.linalg.solve(gram, Xc.T @ yc)
    intercept = y_mean - float(x_mean @ coef)
    return (np.asarray([p], dtype=_INT64).tobytes() + coef.astype(_FLOAT64).tobytes()
            + np.asarray([intercept], dtype=_FLOAT64).tobytes())


def _ridge_unpack(payload: bytes) -> tuple[np.ndarray, float]:
    p = int(np.frombuffer(payload[:8], dtype=_INT64)[0])
    if len(payload) != 8 + 8 * (p + 1):
        raise ModelError(f"ridge payload of {len(payload)} bytes does not hold {p} coefficients")
    coef = np.frombuffer(payload[8:8 + 8 * p], dtype=_FLOAT64).astype(np.float64)
    intercept = float(np.frombuffer(payload[8 + 8 * p:], dtype=_FLOAT64)[0])
    return coef, intercept


def _fit_lgbm(depth: int, X: np.ndarray, y: np.ndarray, seed: int) -> bytes:
    import lightgbm as lgb

    params = lgbm_params(depth, seed)
    data = lgb.Dataset(X, label=y, params=params, free_raw_data=True)
    booster = lgb.train(params, data, num_boost_round=int(LGBM_FIXED["num_boost_round"]))
    return booster.model_to_string().encode("utf-8")


def fit_model(spec: ModelSpec, X: np.ndarray, y: np.ndarray, *, seed: int = SEED) -> FittedModel:
    """Fit one learner on (X, y); X and y are not modified."""
    Xa, ya = _check_xy(X, y)
    if spec.kind == "ridge":
        if not spec.param > 0:
            raise ModelError(f"ridge lambda {spec.param!r} must be > 0")
        payload = _fit_ridge(spec.param, Xa, ya)
    elif spec.kind == "lgbm":
        if int(spec.param) != spec.param or spec.param < 1:
            raise ModelError(f"LightGBM depth {spec.param!r} must be a positive integer")
        payload = _fit_lgbm(int(spec.param), Xa, ya, seed)
    else:
        raise ModelError(f"unknown model kind {spec.kind!r}")
    return FittedModel(spec, _sha256(payload), payload)


def predict(model: FittedModel, X: np.ndarray) -> np.ndarray:
    """Predictions in the target's units, float64, deterministic."""
    if _sha256(model.payload) != model.sha256:
        raise ModelError(f"{model.spec.model_id}: payload does not match its sha256")
    Xa = np.asarray(X, dtype=np.float64)
    if Xa.ndim != 2:
        raise ModelError(f"X must be 2-D, got shape {Xa.shape}")
    if Xa.shape[0] == 0:
        return np.zeros(0, dtype=np.float64)
    if not np.isfinite(Xa).all():
        raise ModelError("X holds a non-finite value")
    if model.spec.kind == "ridge":
        coef, intercept = _ridge_unpack(model.payload)
        if Xa.shape[1] != coef.shape[0]:
            raise ModelError(f"X has {Xa.shape[1]} columns, the model {coef.shape[0]}")
        return np.asarray(Xa @ coef + intercept, dtype=np.float64)
    if model.spec.kind == "lgbm":
        import lightgbm as lgb

        booster = lgb.Booster(model_str=model.payload.decode("utf-8"))
        if Xa.shape[1] != booster.num_feature():
            raise ModelError(f"X has {Xa.shape[1]} columns, the model {booster.num_feature()}")
        return np.asarray(booster.predict(Xa, num_threads=int(LGBM_FIXED["num_threads"])),
                          dtype=np.float64)
    raise ModelError(f"unknown model kind {model.spec.kind!r}")
