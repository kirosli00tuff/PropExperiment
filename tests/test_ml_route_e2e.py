"""The E.ML-train entry end to end on a synthetic step 2 store (preflight, the frozen-input
loader and the block cut replaced by test doubles; everything else is the real job)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from ml_route.ledger import Ledger, verify_chain
from ml_route.synthetic import (
    synthetic_bars,
    synthetic_events,
    synthetic_inputs,
    write_step2_store,
)

FIRST, LAST = date(2019, 5, 6), date(2020, 12, 31)
HARNESS = "ab" * 32


@pytest.fixture(scope="module")
def store(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("step2")
    write_step2_store(root, {"ZN": synthetic_bars("ZN", "rates", FIRST, LAST, 41, 0.015625, 125.0),
                             "TN": synthetic_bars("TN", "rates", FIRST, LAST, 42, 0.015625,
                                                  140.0)})
    return root


@pytest.fixture()
def doubles(monkeypatch: pytest.MonkeyPatch) -> None:
    import ml_route.blocks as blocks
    import ml_route.inputs as inputs_mod
    import screening.harness_freeze as hf
    from data.group_session import trade_dates_between

    events = synthetic_events(["ZN", "TN"], FIRST, LAST, 43)
    inputs = synthetic_inputs({"ZN": FIRST, "TN": date(2019, 6, 3)}, events)
    monkeypatch.setattr(hf, "preflight", lambda expected, root=None: expected)
    monkeypatch.setattr(inputs_mod, "load_route_inputs", lambda: inputs)
    cal = trade_dates_between(inputs_mod._group_calendar("rates"), FIRST, LAST)
    monkeypatch.setattr(blocks, "frozen_block_cut", lambda: blocks.cut_blocks(cal))


def _run(store: Path, out: Path, challenger: str, horizon: str) -> dict:
    from ml_route.train import main

    assert main(["fit", "--challenger", challenger, "--horizon", horizon, "--store-root",
                 str(store), "--out-dir", str(out), "--harness-sha256", HARNESS]) == 0
    return json.loads((out / "candidates" / f"{challenger}_{horizon}.json").read_text(
        encoding="utf-8"))


def test_lightgbm_fit_entry_end_to_end(store: Path, tmp_path: Path, doubles) -> None:
    cand = _run(store, tmp_path, "lgbm", "h30")
    assert cand["harness_sha256"] == HARNESS and len(cand["scores"]) == 8
    assert [s["cluster"] for s in cand["surrogates"]] == ["K2"]
    led = Ledger(tmp_path / "ledger" / "lgbm_h30.jsonl")
    assert verify_chain(led) == 81
    assert all(r["harness_sha256"] == HARNESS for r in led.records())
    idx = np.load(tmp_path / "row_index_lgbm_h30.npz")
    assert idx["day"].max() <= np.datetime64("2024-02-29")
    assert idx["day"][idx["product"] == "TN"].min() >= np.datetime64("2019-06-03")  # S_X cut
    assert (tmp_path / "models" / cand["model_file"]).exists()
    for rule in cand["candidates"]:
        assert rule["provenance"]["harness_sha256"] == HARNESS


def _cuda_available() -> bool:
    import torch

    return bool(torch.cuda.is_available())


@pytest.mark.skipif(not _cuda_available(), reason="V7 and review NOTE-5: LSTM training refuses without CUDA; this machine has none")
def test_lstm_fit_entry_end_to_end(store: Path, tmp_path: Path, doubles) -> None:
    cand = _run(store, tmp_path, "lstm", "h30")
    assert len(cand["scores"]) == 4 and cand["selected"]["hidden"] in (16, 32)
    assert verify_chain(Ledger(tmp_path / "ledger" / "lstm_h30.jsonl")) == 41


def test_fit_entry_refuses_the_research_store_root(tmp_path: Path, doubles) -> None:
    from data.config import PROCESSED_ROOT
    from ml_route.store import StoreRefused
    from ml_route.train import main

    with pytest.raises(StoreRefused, match="research"):
        main(["fit", "--challenger", "lgbm", "--horizon", "h30", "--store-root",
              str(PROCESSED_ROOT), "--out-dir", str(tmp_path), "--harness-sha256", HARNESS])
