"""Stage E.2b G4 follow-up (lead's Task 8 ruling on reports/stage_e2b_harness_review.md):
NOTE-4 (the training store books every row on the group calendar), NOTE-5 (no silent CPU
fallback for the LSTM; the device in every fit record), NOTE-11 (the LSTM machine record written
before the first fit and checked by every later fit) and F-4 (E.ML-test's Holm entry names
k_from_tiers and the (K + 1) rule). Synthetic data; the GPU only in the one real-CUDA test."""

from __future__ import annotations

import inspect
import json
from datetime import UTC, date, datetime, time
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from ml_route import lstm_machine
from ml_route.adapters import LstmAdapter, adapter_for
from ml_route.lstm_machine import LstmMachineRefused, check_fit_batch, ensure_lstm_machine
from ml_route.store import StoreRefused, read_product_bars
from ml_route.synthetic import synthetic_bars, synthetic_inputs, write_step2_store

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
FIRST = date(2023, 11, 1)


# ------------------------------------------------------------ NOTE-4: bookings ----
@pytest.fixture(scope="module")
def frame() -> pd.DataFrame:
    return synthetic_bars("NQ", "equity", FIRST, date(2024, 2, 29), 3, 0.25, 16000.0)


def _row(frame: pd.DataFrame, when: datetime, label: str) -> pd.DataFrame:
    row = frame.iloc[[-1]].copy()
    row["ts_event"] = int(when.astimezone(UTC).timestamp()) * NS
    row["trade_date"] = label
    return pd.concat([frame, row], ignore_index=True)


def _read(tmp_path: Path, frame: pd.DataFrame):  # noqa: ANN202
    write_step2_store(tmp_path / "s", {"NQ": frame})
    return read_product_bars(tmp_path / "s", "NQ", FIRST, forbidden_root=tmp_path / "p")


class TestStoreBookings:
    def test_an_honest_store_books_cleanly(self, tmp_path, frame) -> None:
        assert len(_read(tmp_path, frame)) == len(frame)

    def test_a_march_2024_bar_labelled_february_is_refused(self, tmp_path, frame) -> None:
        bad = _row(frame, datetime(2024, 3, 4, 9, 0, tzinfo=CT), "2024-02-29")
        with pytest.raises(StoreRefused, match="HoldoutRowRefused.*embargo"):
            _read(tmp_path, bad)

    def test_a_research_window_bar_relabelled_2023_is_refused(self, tmp_path, frame) -> None:
        bad = _row(frame, datetime(2025, 5, 1, 9, 0, tzinfo=CT), "2023-12-01")
        with pytest.raises(StoreRefused, match="HoldoutRowRefused.*outside the step2 store"):
            _read(tmp_path, bad)

    def test_a_row_labelled_with_another_trade_date_is_refused(self, tmp_path, frame) -> None:
        ok_day = sorted(frame["trade_date"].unique())[5]
        when = datetime.combine(date.fromisoformat(ok_day), time(9, 0), tzinfo=CT)
        moved = frame[frame["trade_date"] != sorted(frame["trade_date"].unique())[4]]
        bad = _row(moved, when, sorted(frame["trade_date"].unique())[4])
        with pytest.raises(StoreRefused, match="TradeDateMismatch"):
            _read(tmp_path, bad)


# -------------------------------------------------- NOTE-5 / NOTE-11: the machine ----
CARD = {"host": "pc", "gpu_name": "NVIDIA GeForce RTX 3050 4GB Laptop GPU",
        "total_vram_mib": 4096.0}


def _fake_a1(free: dict[int, float]):  # noqa: ANN202
    seen: list[int] = []

    def step(batch: int, total_mib: float) -> dict:
        seen.append(batch)
        return {"batch": batch, "peak_mib": total_mib - free[batch],
                "free_of_4gb_mib": free[batch], "leaves_0_5gb_free": free[batch] >= 512}

    step.seen = seen  # type: ignore[attr-defined]
    return step


@pytest.fixture
def gpu(monkeypatch):  # noqa: ANN201
    monkeypatch.setattr(lstm_machine, "_cuda_available", lambda: True)
    monkeypatch.setattr(lstm_machine, "card", lambda: dict(CARD))

    def use(free: dict[int, float]):  # noqa: ANN202
        fake = _fake_a1(free)
        monkeypatch.setattr(lstm_machine, "a1_step", fake)
        return fake

    return use


class TestMachineRecord:
    def test_no_cuda_is_refused_by_name_and_nothing_is_written(self, monkeypatch,
                                                                tmp_path) -> None:
        monkeypatch.setattr(lstm_machine, "_cuda_available", lambda: False)
        with pytest.raises(LstmMachineRefused, match="no CPU fallback"):
            ensure_lstm_machine(tmp_path, "a" * 64)
        assert not (tmp_path / lstm_machine.MACHINE_FILE).exists()

    def test_the_training_adapter_refuses_without_cuda_before_any_read(self, monkeypatch,
                                                                       tmp_path) -> None:
        monkeypatch.setattr(lstm_machine, "_cuda_available", lambda: False)
        with pytest.raises(LstmMachineRefused):
            adapter_for("lstm", tmp_path / "no_store", synthetic_inputs({}, None), tmp_path,
                        "a" * 64)

    def test_the_first_fit_writes_the_record_with_a1s_batch(self, gpu, tmp_path) -> None:
        fake = gpu({512: 300.0, 256: 900.0, 128: 2000.0, 64: 3000.0})
        got = ensure_lstm_machine(tmp_path, "a" * 64)
        rec = json.loads((tmp_path / lstm_machine.MACHINE_FILE).read_text(encoding="utf-8"))
        assert rec["batch_size"] == 256 == got["batch_size"] and fake.seen == [512, 256]
        assert rec["host"] == "pc" and rec["gpu_name"].startswith("NVIDIA")
        assert rec["total_vram_mib"] == 4096.0 and len(rec["a1_steps"]) == 2
        assert rec["harness_sha256"] == "a" * 64

    def test_later_fits_keep_the_record_and_check_the_card(self, gpu, tmp_path) -> None:
        gpu({512: 300.0, 256: 900.0, 128: 2000.0, 64: 3000.0})
        ensure_lstm_machine(tmp_path, "a" * 64)
        before = (tmp_path / lstm_machine.MACHINE_FILE).read_bytes()
        fake = gpu({256: 700.0})
        again = ensure_lstm_machine(tmp_path, "b" * 64)
        assert fake.seen == [256] and again["batch_size"] == 256
        assert again["this_fit"]["a1_check"]["free_of_4gb_mib"] == 700.0
        assert (tmp_path / lstm_machine.MACHINE_FILE).read_bytes() == before  # written once
        gpu({256: 400.0})  # the card no longer holds 256 with 0.5 GB free
        with pytest.raises(LstmMachineRefused, match="does not hold the recorded batch 256"):
            ensure_lstm_machine(tmp_path, "a" * 64)

    def test_a1_with_no_fitting_batch_stops_to_the_user(self, gpu, tmp_path) -> None:
        gpu({512: 100.0, 256: 200.0, 128: 300.0, 64: 400.0})
        with pytest.raises(LstmMachineRefused, match="stop to the user"):
            ensure_lstm_machine(tmp_path, "a" * 64)
        assert not (tmp_path / lstm_machine.MACHINE_FILE).exists()

    def test_a_corrupt_record_is_refused(self, gpu, tmp_path) -> None:
        gpu({256: 900.0})
        (tmp_path / lstm_machine.MACHINE_FILE).write_text("{}", encoding="utf-8")
        with pytest.raises(LstmMachineRefused, match="not an LSTM machine record"):
            ensure_lstm_machine(tmp_path, "a" * 64)

    def test_a_fit_with_another_batch_or_on_the_cpu_is_refused(self) -> None:
        record = {"batch_size": 256}
        check_fit_batch(record, 256)
        with pytest.raises(LstmMachineRefused, match="plans 256"):
            check_fit_batch(record, 512)
        inputs = synthetic_inputs({}, None)
        adapter = LstmAdapter(None, inputs, batch_size=512, device="cuda", machine=record)
        with pytest.raises(LstmMachineRefused, match="plans 256"):
            adapter.fit(None, np.arange(3), {"lookback": 24}, "h30")
        from ml_route.inputs import RouteInputMissing

        with pytest.raises(RouteInputMissing, match="no CPU fallback"):
            LstmAdapter(None, inputs, batch_size=256, device="cpu", machine=record)

    def test_the_manifest_carries_the_record(self, gpu, tmp_path) -> None:
        gpu({512: 900.0})
        ensure_lstm_machine(tmp_path, "a" * 64)
        assert lstm_machine.read_machine_record(tmp_path)["batch_size"] == 512
        assert lstm_machine.read_machine_record(tmp_path / "none") is None


@pytest.mark.skipif(not __import__("torch").cuda.is_available(), reason="no CUDA device")
def test_the_real_card_gets_a_record_with_an_a1_batch(tmp_path) -> None:
    rec = ensure_lstm_machine(tmp_path, "a" * 64)
    assert rec["batch_size"] in (512, 256, 128, 64) and rec["total_vram_mib"] > 0
    assert rec["a1_steps"][-1]["leaves_0_5gb_free"] is True
    assert ensure_lstm_machine(tmp_path, "a" * 64)["this_fit"]["a1_check"]["leaves_0_5gb_free"]


# ------------------------------------------------- NOTE-5: device in every record ----
class _FakeAdapter:
    challenger = "lgbm"
    device = "cpu"

    def grid(self) -> list[dict]:
        return [{"num_leaves": 7, "min_data_in_leaf": 500, "lambda_l2": 1.0}]

    def config_id(self, config: dict) -> str:
        return "fake"

    def usable_rows(self, table, horizon: str) -> np.ndarray:  # noqa: ANN001
        return np.ones(len(table.t_ns), dtype=bool)

    def fit(self, table, rows, config, horizon):  # noqa: ANN001, ANN201
        return None, b"model", "e" * 64

    def predict(self, model, table, rows, config) -> np.ndarray:  # noqa: ANN001
        return np.full(len(rows), 1.0)


def test_every_fit_record_carries_the_device(tmp_path) -> None:
    from ml_route.blocks import cut_blocks
    from ml_route.ledger import Ledger
    from ml_route.train import FitContext, run_fit

    days = [date(2020, 1, 1) + pd.Timedelta(days=i).to_pytimedelta() for i in range(36)]
    t = np.array([int(datetime.combine(d, time(9, k * 30), tzinfo=CT).timestamp()) * NS
                  for d in days for k in (0, 1)], dtype=np.int64)
    n = len(t)
    table = SimpleNamespace(
        product=np.full(n, "ZN", dtype=object),
        day=np.repeat(np.array(days, dtype="datetime64[D]"), 2), t_ns=t,
        exit_ns={"h30": t + 30 * 60 * NS}, y={"h30": np.linspace(-1, 1, n)},
        cost={"h30": np.full(n, 0.01)})
    ctx = FitContext("lgbm", "h30", tmp_path, "a" * 64)
    run_fit(ctx, table, _FakeAdapter(), cut_blocks(days), SimpleNamespace(s_x={"ZN": days[0]}),
            log=lambda _: None)
    records = list(Ledger(tmp_path / "ledger" / "lgbm_h30.jsonl").records())
    assert len(records) == 11 and all(r["device"] == "cpu" for r in records)


# -------------------------------------------------------------- F-4: Holm entry ----
def test_the_holm_entry_names_k_from_tiers_and_the_k_plus_one_rule() -> None:
    from ml_route.test import route_family
    from screening import stage_e_stats

    holm = route_family([])["holm"]
    assert holm["status"] == "not computed"
    assert holm["k_function"] == "screening.stage_e_stats.k_from_tiers(tiers, route_tested=True)"
    assert "0.05 / (K + 1)" in holm["alpha_rule"] and "k_from_tiers" in holm["reason"]
    param = inspect.signature(stage_e_stats.k_from_tiers).parameters["route_tested"]
    assert param.kind is inspect.Parameter.KEYWORD_ONLY and param.default is param.empty
    assert stage_e_stats.MAX_FAMILIES == 9
    assert callable(stage_e_stats.holm_alpha_k)


# ------------------------------------------- F-3 (b): the store pinned to the start rule ----
def _sha(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestPinnedStore:
    def test_a_doctored_store_is_refused_against_the_start_rules_sha256(self, tmp_path,
                                                                         frame) -> None:
        write_step2_store(tmp_path / "s", {"NQ": frame})
        path = next((tmp_path / "s").rglob("*.parquet"))
        pinned = _sha(path)
        got = read_product_bars(tmp_path / "s", "NQ", FIRST, forbidden_root=tmp_path / "p",
                                expected_sha256=pinned)
        assert got.file_sha256 == pinned
        doctored = frame.copy()
        doctored.loc[doctored.index[100], "close"] += 0.25  # one price changed, labels intact
        write_step2_store(tmp_path / "s", {"NQ": doctored})
        assert _sha(path) != pinned
        with pytest.raises(StoreRefused, match="the start rule's recorded step 2 parquet"):
            read_product_bars(tmp_path / "s", "NQ", FIRST, forbidden_root=tmp_path / "p",
                              expected_sha256=pinned)

    def test_the_training_dataset_uses_and_records_the_pinned_sha(self, tmp_path,
                                                                  frame) -> None:
        from dataclasses import replace

        from ml_route.dataset import build_dataset
        from ml_route.inputs import RouteInputMissing
        from ml_route.synthetic import synthetic_events

        write_step2_store(tmp_path / "s", {"NQ": frame})
        pinned = _sha(next((tmp_path / "s").rglob("*.parquet")))
        base = synthetic_inputs({"NQ": FIRST},
                                synthetic_events(["NQ"], FIRST, date(2024, 2, 29), 1))
        with pytest.raises(StoreRefused, match="start rule"):
            build_dataset(tmp_path / "s", replace(base, step2_sha256={"NQ": "0" * 64}))
        with pytest.raises(RouteInputMissing, match="no pinned step 2 sha256 for NQ"):
            build_dataset(tmp_path / "s", replace(base, step2_sha256={}))
        table = build_dataset(tmp_path / "s", replace(base, step2_sha256={"NQ": pinned}))
        assert table.store_sha256 == {"NQ": pinned}

    def test_the_manifest_records_and_checks_the_store_hashes(self) -> None:
        from types import SimpleNamespace

        from ml_route.manifest import ManifestError, store_hashes

        cands = {("lgbm", "h30"): {"step2_store_sha256": {"ZN": "a" * 64}},
                 ("lstm", "h30"): {"step2_store_sha256": {"ZN": "a" * 64}}}
        pinned = SimpleNamespace(step2_sha256={"ZN": "a" * 64}, traded=lambda: ("ZN",))
        assert store_hashes(cands, pinned) == {"ZN": "a" * 64}
        assert store_hashes(cands, SimpleNamespace(step2_sha256=None)) == {"ZN": "a" * 64}
        other = {**cands, ("lgbm", "hF"): {"step2_store_sha256": {"ZN": "b" * 64}}}
        with pytest.raises(ManifestError, match="another ZN step 2 parquet"):
            store_hashes(other, pinned)
        wrong = SimpleNamespace(step2_sha256={"ZN": "c" * 64}, traded=lambda: ("ZN",))
        with pytest.raises(ManifestError, match="the start rule pins"):
            store_hashes(cands, wrong)
        missing = SimpleNamespace(step2_sha256={"ZN": "a" * 64, "ZF": "d" * 64},
                                  traded=lambda: ("ZN", "ZF"))
        with pytest.raises(ManifestError, match="ZF"):
            store_hashes(cands, missing)
