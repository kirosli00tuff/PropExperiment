"""M3 challenger 1: LightGBM regression (L2) on the normalized net target.

Grid (8 configurations per horizon): num_leaves {7, 31} x min_data_in_leaf {500, 2000} x
lambda_l2 {1.0, 10.0}; every other setting is ``constants.LGBM_FIXED`` (400 rounds, no early
stopping, deterministic, force_col_wise, 8 threads, all seeds 20260924). F18 and F19 enter as
one-hot columns: one per product with rows in the training table, one per cluster (ML-A12).
The model's identity is the sha256 of ``Booster.model_to_string()``.
"""

from __future__ import annotations

from collections.abc import Sequence
from itertools import product as cartesian

import numpy as np

from ml_route.constants import CLUSTER_IDS, FEATURES_DISTILLABLE, LGBM_FIXED, LGBM_GRID_AXES
from ml_route.ledger import sha256_bytes


def grid() -> list[dict]:
    names = [a for a, _ in LGBM_GRID_AXES]
    return [dict(zip(names, vals, strict=True))
            for vals in cartesian(*(v for _, v in LGBM_GRID_AXES))]


def config_id(config: dict) -> str:
    return (f"lgbm_nl{config['num_leaves']}_md{config['min_data_in_leaf']}"
            f"_l2{config['lambda_l2']:g}")


def design_matrix(X: np.ndarray, product: np.ndarray, cluster: np.ndarray,
                  products_with_rows: Sequence[str]) -> tuple[np.ndarray, list[str]]:
    """F1-F17 plus the one-hot product and cluster columns, float64."""
    prod = np.asarray(product).astype(str)
    clus = np.asarray(cluster).astype(str)
    unknown = set(prod) - set(products_with_rows)
    if unknown:
        raise ValueError(f"rows of products outside the one-hot list: {sorted(unknown)}")
    onehot_p = np.stack([(prod == p) for p in products_with_rows], axis=1).astype(np.float64)
    onehot_k = np.stack([(clus == k) for k in CLUSTER_IDS], axis=1).astype(np.float64)
    names = (list(FEATURES_DISTILLABLE) + [f"F18_{p}" for p in products_with_rows]
             + [f"F19_{k}" for k in CLUSTER_IDS])
    return np.hstack([np.asarray(X, dtype=np.float64), onehot_p, onehot_k]), names


def params(config: dict) -> dict:
    out = {k: v for k, v in LGBM_FIXED.items() if k != "num_boost_round"}
    out.update({"num_leaves": int(config["num_leaves"]),
                "min_data_in_leaf": int(config["min_data_in_leaf"]),
                "lambda_l2": float(config["lambda_l2"])})
    return out


def fit(X: np.ndarray, y: np.ndarray, names: list[str], config: dict):  # noqa: ANN201
    """(booster, model text bytes, sha256)."""
    import lightgbm as lgb

    p = params(config)
    data = lgb.Dataset(X, label=np.asarray(y, dtype=np.float64), feature_name=names,
                       params=p, free_raw_data=True)
    booster = lgb.train(p, data, num_boost_round=int(LGBM_FIXED["num_boost_round"]))
    text = booster.model_to_string().encode("utf-8")
    return booster, text, sha256_bytes(text)


def load(text: bytes):  # noqa: ANN201
    import lightgbm as lgb

    return lgb.Booster(model_str=text.decode("utf-8"))


def predict(booster, X: np.ndarray) -> np.ndarray:  # noqa: ANN001
    return np.asarray(booster.predict(X, num_threads=int(LGBM_FIXED["num_threads"])),
                      dtype=np.float64)
