"""M7.5 normalization test, M7.6 hash chain and determinism, resumable ledgers, LSTM inputs."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from ml_route import lgbm
from ml_route.blocks import cut_blocks
from ml_route.constants import TRAIN_LAST
from ml_route.dataset import build_from_bars
from ml_route.features import Bars
from ml_route.ledger import (
    HashChainError,
    Ledger,
    check_refit,
    machine_id,
    verify_chain,
    verify_model_file,
)
from ml_route.synthetic import bars_from_frame, synthetic_bars, synthetic_events, synthetic_inputs

NS_MIN = 60_000_000_000
SMALL = {"num_leaves": 7, "min_data_in_leaf": 500, "lambda_l2": 1.0}


# ------------------------------------------------------------------ M7.5 ----
@pytest.fixture(scope="module")
def late_world() -> dict:
    first, last = date(2023, 6, 1), date(2024, 5, 31)  # bars run past the training window
    frames = {"NQ": synthetic_bars("NQ", "equity", first, last, 21, 0.25, 15000.0),
              "ZN": synthetic_bars("ZN", "rates", first, last, 22, 0.015625, 110.0)}
    bars = {r: bars_from_frame(r, f) for r, f in frames.items()}
    inputs = synthetic_inputs({r: first for r in frames},
                              synthetic_events(list(frames), first, last, 23))
    return {"bars": bars, "inputs": inputs}


def _perturb_after_window(b: Bars, seed: int) -> Bars:
    rng = np.random.default_rng(seed)
    late = b.trade_date > np.datetime64(TRAIN_LAST)
    scale = 1 + 0.2 * rng.standard_normal(int(late.sum()))
    out = {k: getattr(b, k).copy() for k in ("open", "high", "low", "close", "volume")}
    for k in ("open", "high", "low", "close"):
        out[k][late] *= scale
    out["volume"][late] = rng.integers(1, 5000, int(late.sum()))
    return replace(b, **out)


def _fit_sha(table) -> str:  # noqa: ANN001
    rows = np.flatnonzero(table.complete_mask("h30"))
    products = sorted(set(table.product.astype(str)))
    X, names = lgbm.design_matrix(table.X, table.product, table.cluster, products)
    return lgbm.fit(X[rows], table.y["h30"][rows], names, SMALL)[2]


def test_perturbing_every_row_after_the_training_window_leaves_the_model_hash(late_world) -> None:
    tb0 = build_from_bars(late_world["bars"], late_world["inputs"])
    assert tb0.day.max() <= np.datetime64(TRAIN_LAST)
    assert int(tb0.complete_mask("h30").sum()) > 200
    bars1 = {r: _perturb_after_window(b, 7) for r, b in late_world["bars"].items()}
    tb1 = build_from_bars(bars1, late_world["inputs"])
    assert _fit_sha(tb0) == _fit_sha(tb1)


def test_the_normalization_test_has_teeth(late_world) -> None:
    """Negative control: rows past the window (never used by the route) do change the hash."""
    last = date(2024, 5, 31)
    tb0 = build_from_bars(late_world["bars"], late_world["inputs"], last=last)
    bars1 = {r: _perturb_after_window(b, 7) for r, b in late_world["bars"].items()}
    tb1 = build_from_bars(bars1, late_world["inputs"], last=last)
    assert _fit_sha(tb0) != _fit_sha(tb1)


# ------------------------------------------------------------------ M7.6 ----
def test_lightgbm_fit_is_deterministic() -> None:
    rng = np.random.default_rng(3)
    X = rng.standard_normal((6000, 20))
    y = X[:, 0] + rng.standard_normal(6000)
    names = [f"c{i}" for i in range(20)]
    a = lgbm.fit(X, y, names, SMALL)
    b = lgbm.fit(X, y, names, SMALL)
    assert a[2] == b[2] and a[1] == b[1]
    assert lgbm.predict(lgbm.load(a[1]), X[:5]).tolist() == lgbm.predict(a[0], X[:5]).tolist()


def _tiny_lstm_fit(device: str) -> str:
    from ml_route import lstm

    rng = np.random.default_rng(4)
    n, lb = 300, 24
    seq = rng.standard_normal((n, lb, 3)).astype(np.float32)
    lens = rng.integers(1, lb + 1, n)
    prod = rng.integers(0, 3, n)
    static = rng.standard_normal((n, 24)).astype(np.float32)
    y = rng.standard_normal(n)

    def fn(r):  # noqa: ANN001, ANN202
        return seq[r], lens[r], prod[r], static[r]

    return lstm.fit(n, fn, y, 3, 24, {"hidden": 16, "lookback": lb}, 64, device)[2]


def test_lstm_fit_is_deterministic_on_cpu() -> None:
    assert _tiny_lstm_fit("cpu") == _tiny_lstm_fit("cpu")


def test_lstm_fit_is_deterministic_on_the_gpu() -> None:
    torch = pytest.importorskip("torch")
    if not torch.cuda.is_available():
        pytest.skip("no CUDA device")
    assert _tiny_lstm_fit("cuda") == _tiny_lstm_fit("cuda")


def test_ledger_is_a_hash_chain(tmp_path: Path) -> None:
    led = Ledger(tmp_path / "l.jsonl")
    led.append({"key": "a", "model_sha256": "1" * 64, "machine": {"host": "x"}})
    led.append({"key": "b", "model_sha256": "2" * 64, "machine": {"host": "x"}})
    assert verify_chain(led) == 2 and led.keys() == {"a", "b"}
    with pytest.raises(HashChainError):
        led.append({"key": "a", "model_sha256": "3" * 64})
    lines = led.path.read_text(encoding="utf-8").splitlines()
    edited = json.loads(lines[0])
    edited["model_sha256"] = "9" * 64
    led.path.write_text(json.dumps(edited) + "\n" + lines[1] + "\n", encoding="utf-8")
    with pytest.raises(HashChainError, match="edited"):
        verify_chain(led)
    led.path.write_text(lines[1] + "\n" + lines[0] + "\n", encoding="utf-8")
    with pytest.raises(HashChainError, match="does not follow"):
        verify_chain(led)


def test_refit_hash_checks_same_machine_only(tmp_path: Path) -> None:
    me = machine_id()
    rec = {"key": "k", "model_sha256": "a" * 64, "machine": me}
    check_refit(rec, "a" * 64, me)
    with pytest.raises(HashChainError, match="same machine"):
        check_refit(rec, "b" * 64, me)
    check_refit(rec, "b" * 64, {**me, "host": "the-windows-pc"})  # recorded, never compared


def test_saved_model_with_other_bytes_is_refused(tmp_path: Path) -> None:
    from ml_route.ledger import sha256_bytes

    path = tmp_path / "m.bin"
    path.write_bytes(b"model")
    verify_model_file(path, sha256_bytes(b"model"))
    path.write_bytes(b"model!")
    with pytest.raises(HashChainError, match="REFUSED"):
        verify_model_file(path, sha256_bytes(b"model"))


def test_run_fit_resumes_from_the_ledger_and_reproduces_the_refit(tmp_path: Path) -> None:
    from data.group_session import trade_dates_between
    from ml_route.adapters import LgbmAdapter
    from ml_route.inputs import _group_calendar
    from ml_route.train import FitContext, run_fit

    first, last = date(2019, 5, 6), date(2020, 12, 31)
    frames = {"ZN": synthetic_bars("ZN", "rates", first, last, 31, 0.015625, 125.0)}
    bars = {r: bars_from_frame(r, f) for r, f in frames.items()}
    inputs = synthetic_inputs({"ZN": first}, synthetic_events(["ZN"], first, last, 32))
    table = build_from_bars(bars, inputs)
    cut = cut_blocks(trade_dates_between(_group_calendar("rates"), first, last))
    ctx = FitContext("lgbm", "h30", tmp_path, "c" * 64)
    ad = LgbmAdapter()
    ad.attach(table)
    out1 = run_fit(ctx, table, ad, cut, inputs, log=lambda s: None)
    led = Ledger(tmp_path / "ledger" / "lgbm_h30.jsonl")
    n1 = verify_chain(led)
    assert n1 == 8 * 10 + 1
    recs = list(led.records())
    assert all(r["harness_sha256"] == "c" * 64 for r in recs)
    assert all(r["train"]["row_index_sha256"] != r["validation"]["row_index_sha256"]
               for r in recs[:-1])
    out2 = run_fit(ctx, table, ad, cut, inputs, log=lambda s: None)
    assert verify_chain(led) == n1  # every key skipped on restart, nothing appended
    assert out2["model_sha256"] == out1["model_sha256"]
    verify_model_file(tmp_path / "models" / out1["model_file"], out1["model_sha256"])


# ------------------------------------------------------------------ LSTM inputs ----
def _hand_bars() -> Bars:
    base = np.datetime64("2020-01-06T15:00", "ns").astype(np.int64)  # 09:00 CT
    ts = base + np.arange(12, dtype=np.int64) * NS_MIN
    ts = np.concatenate([ts, ts + 86_400 * 10**9])
    o = np.arange(24, dtype=float) + 100
    c = o + 0.5
    days = np.array(["2020-01-06"] * 12 + ["2020-01-07"] * 12, dtype="datetime64[D]")
    return Bars("ZN", ts, o, c + 1, o - 1, c, np.ones(24) * 10, np.ones(24, dtype=np.int64), days)


def test_five_minute_bars_known_answer_and_no_crossing_of_trade_dates() -> None:
    from ml_route.lstm_data import five_minute_bars, gather, sequence_index

    fb = five_minute_bars(_hand_bars(), per_unit=2.0)
    assert len(fb.end_ns) == 6  # 5 + 5 + 2 minutes per date
    assert fb.oc_ticks[0] == pytest.approx((104.5 - 100) * 2)
    assert fb.hl_ticks[0] == pytest.approx((105.5 - 99) * 2)
    t2 = np.datetime64("2020-01-07T15:10", "ns").astype(np.int64)
    idx = sequence_index(fb, np.array(["2020-01-07"], dtype="datetime64[D]"), np.array([t2]), 72)
    assert idx.length[0] == 2 and idx.end[0] == 4  # never reaches the previous date's bars
    seq, lens = gather(fb, idx, np.array([0]), np.array([2.0]), 72)
    assert lens[0] == 2 and np.all(seq[0, 2:] == 0) and seq[0, 0, 0] == fb.oc_ticks[3] / 2.0


def test_padding_is_masked_and_serialization_round_trips() -> None:
    torch = pytest.importorskip("torch")
    from ml_route.lstm import build_model, deserialize, serialize

    model = build_model(3, 5, 16).eval()
    g = torch.Generator().manual_seed(1)
    seq = torch.randn(1, 7, 3, generator=g)
    padded = torch.cat([seq, torch.randn(1, 65, 3, generator=g)], dim=1)  # junk after the end
    prod, static = torch.tensor([1]), torch.randn(1, 5, generator=g)
    a = model(seq, torch.tensor([7]), prod, static)
    b = model(padded, torch.tensor([7]), prod, static)
    assert torch.equal(a, b)
    data = serialize(model.state_dict())
    other = build_model(3, 5, 16)
    other.load_state_dict(deserialize(data))
    assert serialize(other.state_dict()) == data
