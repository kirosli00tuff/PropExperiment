"""ml_route_v2.models: closed-form ridge and shallow LightGBM, determinism and hashes (V2.6)."""

from __future__ import annotations

import hashlib
import struct

import numpy as np
import pytest

from ml_route_v2.configs import lgbm_spec, ridge_spec
from ml_route_v2.constants import LGBM_FIXED, SEED
from ml_route_v2.models import FittedModel, ModelError, fit_model, lgbm_params, predict


def _data(n=400, p=5, seed=1):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n, p))
    y = 3.0 + X @ np.arange(1, p + 1) * 0.5 + rng.standard_normal(n)
    return X, y


def test_ridge_matches_hand_closed_form_with_unpenalized_intercept():
    X, y = _data()
    lam = 0.1
    model = fit_model(ridge_spec(lam), X, y)
    xm, ym = X.mean(0), y.mean()
    Xc = X - xm
    coef = np.linalg.solve(Xc.T @ Xc + lam * len(y) * np.eye(X.shape[1]), Xc.T @ (y - ym))
    expected = X @ coef + (ym - xm @ coef)
    np.testing.assert_allclose(predict(model, X), expected, rtol=1e-12, atol=1e-12)


def test_ridge_alpha_scales_with_n_train():
    X, y = _data()
    one = predict(fit_model(ridge_spec(1.0), X, y), X)
    doubled = predict(fit_model(ridge_spec(1.0), np.vstack([X, X]), np.concatenate([y, y])), X)
    np.testing.assert_allclose(one, doubled, rtol=1e-10)


def test_ridge_large_penalty_keeps_the_intercept():
    X, y = _data()
    pred = predict(fit_model(ridge_spec(1e9), X, y), X)
    np.testing.assert_allclose(pred, y.mean(), atol=1e-6)


def test_ridge_payload_layout_and_determinism():
    X, y = _data()
    a, b = fit_model(ridge_spec(0.01), X, y), fit_model(ridge_spec(0.01), X, y)
    assert a.sha256 == b.sha256 == hashlib.sha256(a.payload).hexdigest()
    assert struct.unpack("<q", a.payload[:8])[0] == X.shape[1]
    assert len(a.payload) == 8 + 8 * (X.shape[1] + 1)
    assert predict(a, X).dtype == np.float64
    assert fit_model(ridge_spec(0.1), X, y).sha256 != a.sha256


def test_lgbm_params_pin_depth_leaves_and_seeds():
    p = lgbm_params(3)
    assert p["max_depth"] == 3 and p["num_leaves"] == 8
    assert all(p[k] == SEED for k in ("seed", "bagging_seed", "feature_fraction_seed",
                                      "data_random_seed"))
    assert "num_boost_round" not in p
    assert p["min_data_in_leaf"] == LGBM_FIXED["min_data_in_leaf"] == 2000
    assert p["deterministic"] is True and p["num_threads"] == 8


def test_lgbm_is_deterministic_and_learns_a_planted_signal():
    rng = np.random.default_rng(3)
    X = rng.standard_normal((6000, 4))
    y = 0.8 * X[:, 0] + rng.standard_normal(6000)
    a, b = fit_model(lgbm_spec(2), X, y), fit_model(lgbm_spec(2), X, y)
    assert a.sha256 == b.sha256
    pa = predict(a, X)
    np.testing.assert_array_equal(pa, predict(b, X))
    assert pa.dtype == np.float64
    assert np.corrcoef(pa, X[:, 0])[0, 1] > 0.8
    assert fit_model(lgbm_spec(3), X, y).sha256 != a.sha256


def test_predict_rejects_tampered_payload_and_wrong_width():
    X, y = _data()
    model = fit_model(ridge_spec(0.1), X, y)
    tampered = FittedModel(model.spec, model.sha256, model.payload[:-1] + b"\x00")
    with pytest.raises(ModelError, match="sha256"):
        predict(tampered, X)
    with pytest.raises(ModelError, match="columns"):
        predict(model, X[:, :3])


def test_fit_rejects_non_finite_and_misaligned_inputs():
    X, y = _data()
    Xn = X.copy()
    Xn[0, 0] = np.nan
    with pytest.raises(ModelError, match="non-finite"):
        fit_model(ridge_spec(0.1), Xn, y)
    with pytest.raises(ModelError, match="does not match"):
        fit_model(ridge_spec(0.1), X, y[:-1])
    assert not np.isnan(X).any()  # inputs untouched


def test_the_ridge_fit_runs_under_one_blas_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    """Code review C-07: the closed-form ridge is fitted under one thread of numpy's BLAS (the
    library its matmul and solve call) whatever the caller's limit, so its bytes (and the sha256
    a resumed run checks) do not depend on the thread count."""
    from threadpoolctl import threadpool_info, threadpool_limits

    import ml_route_v2.models as models

    rng = np.random.default_rng(3)
    X = rng.standard_normal((400, 12))
    y = X[:, 0] * 0.3 + rng.standard_normal(400)
    seen: list[set[int]] = []
    original = models._ridge_payload

    def spy(lam, X_, y_):  # noqa: ANN001, ANN202 - test double
        seen.append({i["num_threads"] for i in threadpool_info()
                     if i["user_api"] == "blas" and "numpy" in i["filepath"]})
        return original(lam, X_, y_)

    monkeypatch.setattr(models, "_ridge_payload", spy)
    with threadpool_limits(limits=4, user_api="blas"):
        four = fit_model(ridge_spec(0.1), X, y)
    with threadpool_limits(limits=1, user_api="blas"):
        one = fit_model(ridge_spec(0.1), X, y)
    assert seen == [{1}, {1}]
    assert four.sha256 == one.sha256 and four.payload == one.payload
