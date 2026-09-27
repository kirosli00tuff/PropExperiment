"""Stage E.2b Task 4: data/step2_store.py (the step 2 bar store builder).

Synthetic chunk files only (the step 2 history is not bought): 58 zstd DBN files for ZN written
under tmp_path, a purchase manifest listing them, a tmp condition file. No network, no vendor
file, no Stage E parquet is read. The ts of every planted bar is chosen against the rates
calendar (session 17:00 CT the evening before to 16:00 CT).
"""

from __future__ import annotations

import hashlib
import json
import stat
from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import databento_dbn as dbn
import pyarrow.parquet as pq
import pytest
import zstandard

from data import build_bars as bb
from data import step2_store as st
from data.config import PROCESSED_ROOT
from data.research_bars import CONFIRMATION_RAW_CHUNKS, HoldoutLeakError
from screening import harness_freeze

IID = 4242
HARNESS = "cd" * 32
PX = 110_000_000_000  # 110.0 in 1e-9 units; ZN's tick is 15,625,000
TICK = 15_625_000


def ns(stamp: str) -> int:
    return int(datetime.fromisoformat(stamp).replace(tzinfo=UTC).timestamp()) * 10**9


GOOD = (PX, PX + TICK, PX - TICK, PX, 5)
BAD = (PX + 7, PX - 10 * TICK, PX + 10 * TICK, PX + 3, 5)  # off tick AND high < low
PLANTED = {
    "range=2019-05-01_2019-06-01.dbn.zst": [
        (ns("2019-05-03T14:00:00"), *GOOD), (ns("2019-05-03T14:01:00"), *GOOD),  # before 05-06
        (ns("2019-05-06T13:30:00"), *GOOD), (ns("2019-05-06T13:31:00"), *GOOD),
        (ns("2019-05-06T13:32:00"), *GOOD)],
    "range=2024-02-01_2024-03-01.dbn.zst": [
        (ns("2024-02-29T15:00:00"), *GOOD), (ns("2024-02-29T15:01:00"), *GOOD),
        # booked to 2024-03-01 (17:30 CT, the embargo): invalid on purpose, never to be read
        (ns("2024-02-29T23:30:00"), *BAD), (ns("2024-02-29T23:30:00"), *BAD),
        (ns("2024-02-29T23:31:00"), *BAD)],
}


def write_bars(path: Path, start: str, end: str, bars: list[tuple[int, ...]]) -> None:
    t0 = int(datetime.fromisoformat(start).replace(tzinfo=UTC).timestamp()) * 10**9
    t1 = int(datetime.fromisoformat(end).replace(tzinfo=UTC).timestamp()) * 10**9
    mapping = SimpleNamespace(raw_symbol="ZN.v.0", intervals=[SimpleNamespace(
        start_date=date.fromisoformat(start), end_date=date.fromisoformat(end), symbol=str(IID))])
    meta = dbn.Metadata("GLBX.MDP3", t0, dbn.SType.CONTINUOUS, dbn.SType.INSTRUMENT_ID,
                        dbn.Schema.OHLCV_1M, symbols=["ZN.v.0"], partial=[], not_found=[],
                        mappings=[mapping], end=t1)
    raw = bytes(meta.encode()) + b"".join(
        bytes(dbn.OHLCVMsg(0x21, 1, IID, ts, o, h, lo, c, v)) for ts, o, h, lo, c, v in bars)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(zstandard.ZstdCompressor().compress(raw))


def make_inputs(tmp_path: Path, planted: dict[str, list] | None = None,
                names: list[tuple[str, str]] | None = None) -> Path:
    """58 synthetic chunks and ZN's purchase manifest; returns the reports base."""
    planted = PLANTED if planted is None else planted
    directory = tmp_path / "v" / "GLBX.MDP3" / "ohlcv-1m" / "ZN_v_0"
    files = []
    for start, end in names or CONFIRMATION_RAW_CHUNKS:
        name = f"range={start}_{end}.dbn.zst"
        bars = planted.get(name, [])
        write_bars(directory / name, start, end, bars)
        files.append({"name": name, "path": str(directory / name), "request_start": start,
                      "request_end": end, "sha256": hashlib.sha256(
                          (directory / name).read_bytes()).hexdigest(),
                      "record_count": len(bars), "instrument_ids": [str(IID)]})
    reports = tmp_path / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "purchase_ZN.json").write_text(json.dumps(
        {"product": "ZN", "files": files, "sealed_chunks": []}), encoding="utf-8")
    (tmp_path / "cond.json").write_text(json.dumps([
        {"date": "2024-02-29", "condition": "degraded"},
        {"date": "2019-05-07", "condition": "available"}]), encoding="utf-8")
    return reports


@pytest.fixture(autouse=True)
def preflight_ok(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []
    monkeypatch.setattr(harness_freeze, "preflight",
                        lambda expected, root=None: seen.append(expected) or expected)
    return seen


def build(tmp_path: Path, reports: Path) -> dict:
    return st.run_product("ZN", expected_harness_sha256=HARNESS, out_base=tmp_path / "store",
                          reports_base=reports, rolls_dir=tmp_path / "rolls",
                          condition=tmp_path / "cond.json", client_factory=None,
                          log=lambda m: None)


# ----------------------------------------------------------------- layout ----
def test_the_store_lives_under_its_own_root_never_data_processed() -> None:
    path = st.step2_parquet_path("NQ")
    assert path.parent.parent == st.STEP2_ROOT and st.STEP2_ROOT.name == "processed_step2"
    assert path.name == "ohlcv-1m_NQ_v_0_2019-05-06_2024-02-29_step2.parquet"
    assert PROCESSED_ROOT not in path.parents and st.STEP2_ROOT != PROCESSED_ROOT
    assert st.summary_path("NQ").name == "bars_NQ.json"
    assert len(st.UNSEALED_NAMES) == 58 and len(st.SEALED_NAMES) == 13


# ------------------------------------------------------------------ build ----
def test_the_build_drops_embargo_rows_unread_and_writes_only_window_dates(tmp_path: Path) -> None:
    # Arrange: the embargo rows are off-tick and high < low; reading them would fail the build.
    reports = make_inputs(tmp_path)

    # Act
    summary = build(tmp_path, reports)

    # Assert
    assert summary["status"] == "built", summary["refusal_causes"]
    out = st.step2_parquet_path("ZN", tmp_path / "store")
    table = pq.read_table(out)
    frame = table.to_pandas()
    assert len(frame) == 5 and sorted(set(frame["trade_date"])) == ["2019-05-06", "2024-02-29"]
    assert frame["ts_event"].max() < ns("2024-02-29T23:00:00")  # no embargo row written
    assert frame["vendor_degraded_day"].sum() == 2
    assert list(frame.columns) == [
        "ts_event", "open", "high", "low", "close", "volume", "instrument_id", "raw_symbol",
        "in_flatten_window", "in_no_new_positions_window", "early_halt_ct",
        "in_scheduled_closure", "trade_date", "is_roll_session", "gap_before_minutes",
        "vendor_degraded_day"]
    drops = summary["window_drops"]
    assert drops["embargo_rows_dropped_unread"] == 3 and drops["embargo_trade_dates"] == [
        "2024-03-01"]
    assert drops["before_first_trade_date"] == {"2019-05-03": 2}
    assert drops["rows_decoded"] == 10 and drops["rows_in_window"] == 5
    assert summary["raw_checks"]["off_tick_prices"] == 0  # the checks never saw the bad rows
    meta = json.loads(table.schema.metadata[b"propexperiment"])
    assert meta["harness_sha256"] == HARNESS and meta["store"] == "step2"
    assert meta["trade_date_range"] == ["2019-05-06", "2024-02-29"]
    assert len(meta["sealed_chunks_not_opened"]) == 13
    assert meta["purchase_manifest"]["sha256"] == hashlib.sha256(
        (reports / "purchase_ZN.json").read_bytes()).hexdigest()
    assert stat.S_IMODE(out.stat().st_mode) == 0o444
    written = json.loads((reports / "bars_ZN.json").read_text(encoding="utf-8"))
    assert written["parquet"]["sha256"] == bb.sha256_file(out)


def test_an_existing_store_is_never_overwritten(tmp_path: Path) -> None:
    reports = make_inputs(tmp_path)
    build(tmp_path, reports)
    with pytest.raises(st.Step2StoreRefused, match="already exists"):
        build(tmp_path, reports)


def test_a_holdout2_row_in_an_unsealed_file_is_a_leak_and_nothing_is_written(
        tmp_path: Path) -> None:
    planted = {**PLANTED, "range=2024-01-01_2024-02-01.dbn.zst": [
        (ns("2024-01-10T15:00:00"), *GOOD), (ns("2024-04-02T15:00:00"), *GOOD)]}
    reports = make_inputs(tmp_path, planted)
    with pytest.raises(HoldoutLeakError, match="holdout-2 or later"):
        build(tmp_path, reports)
    assert not st.step2_parquet_path("ZN", tmp_path / "store").exists()


# --------------------------------------------------------------- refusals ----
def _spec(tmp_path: Path, files: tuple[bb.InputFile, ...]) -> bb.ProductSpec:
    return bb.ProductSpec(root="ZN", group="rates", tick="0.015625", tick_source="test",
                          files=files, rolls_path=tmp_path / "r.jsonl", symbology_path=None,
                          policy=bb.STAGE_E_POLICIES["rates"], out=tmp_path / "o.parquet")


def _no_load(paths: list[Path]) -> Any:
    raise AssertionError("a file was opened")


@pytest.mark.parametrize("swap", ["range=2024-03-01_2024-04-01.dbn.zst",
                                  "range=2025-03-01_2025-04-01.dbn.zst"])
def test_a_sealed_chunk_input_is_refused_before_any_file_is_opened(tmp_path: Path,
                                                                    swap: str) -> None:
    reports = make_inputs(tmp_path)
    files = list(st.input_files("ZN", reports / "purchase_ZN.json"))
    files[-1] = bb.InputFile(files[-1].path.with_name(swap), None, 0)
    spec = _spec(tmp_path, tuple(files))
    with pytest.raises(st.Step2StoreRefused, match="sealed-only"):
        st.build_step2_product(spec, SimpleNamespace(), [], [], None, "none",
                               harness_sha256=HARNESS, load_bars=_no_load)


def test_an_input_under_a_sealed_store_or_in_a_holdout_manifest_is_refused(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = make_inputs(tmp_path)
    files = st.input_files("ZN", reports / "purchase_ZN.json")
    with pytest.raises(st.Step2StoreRefused, match="under a sealed store"):
        st.refuse_inputs("ZN", files, sealed_roots=(tmp_path / "v",))
    monkeypatch.setattr(st.ho, "is_sealed_raw", lambda path, paths=None: True)
    with pytest.raises(st.Step2StoreRefused, match="listed in a holdout manifest"):
        st.refuse_inputs("ZN", files)


def test_a_missing_or_foreign_chunk_is_refused(tmp_path: Path) -> None:
    reports = make_inputs(tmp_path, names=list(CONFIRMATION_RAW_CHUNKS[:-1]))
    with pytest.raises(st.Step2StoreRefused, match="its 58 unsealed chunks"):
        st.refuse_inputs("ZN", st.input_files("ZN", reports / "purchase_ZN.json"))
    reports = make_inputs(tmp_path)
    with pytest.raises(st.Step2StoreRefused, match="not 'ZB'"):
        st.input_files("ZB", reports / "purchase_ZN.json")
    files = list(st.input_files("ZN", reports / "purchase_ZN.json"))
    moved = tmp_path / "ZB_v_0" / files[0].path.name
    files[0] = bb.InputFile(moved, None, 0)
    with pytest.raises(st.Step2StoreRefused, match="own directory"):
        st.refuse_inputs("ZN", files)


def test_a_late_listed_product_expects_its_inputs_from_its_first_priced_month(
        tmp_path: Path) -> None:
    # OC-R: MBT is bought from 2021-04, so its store is built from 35 unsealed chunks.
    names = st.expected_names("MBT")
    assert len(names) == 35 and names[0] == "range=2021-04-01_2021-05-01.dbn.zst"
    assert names[-1] == "range=2024-02-01_2024-03-01.dbn.zst" and len(st.expected_names("ZN")) == 58
    directory = tmp_path / "MBT_v_0"
    full = tuple(bb.InputFile(directory / n, None, 0) for n in st.UNSEALED_NAMES)
    with pytest.raises(st.Step2StoreRefused, match="its 35 unsealed chunks 2021-04-01"):
        st.refuse_inputs("MBT", full, sealed_roots=())
    st.refuse_inputs("MBT", tuple(f for f in full if f.path.name in names), sealed_roots=())


# -------------------------------------------------------------------- CLI ----
def test_the_entry_points_refuse_when_the_harness_preflight_raises(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reports = make_inputs(tmp_path)

    def refuse(expected: str, root: Path | None = None) -> str:
        raise harness_freeze.HarnessFreezeError("planted")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    monkeypatch.setattr(st.bb, "verify_inputs", lambda spec: pytest.fail("a file was read"))
    ran: list[str] = []
    rc = st.cli(["--products", "ZN", "--harness-sha256", HARNESS],
                runner=lambda root, **k: ran.append(root) or {"status": "built"})
    assert rc == 2 and ran == []
    with pytest.raises(harness_freeze.HarnessFreezeError, match="planted"):
        build(tmp_path, reports)  # run_product itself refuses too: no way around it
    assert not (reports / "bars_ZN.json").exists()


def test_the_cli_passes_the_expected_sha_to_every_product(preflight_ok: list[str]) -> None:
    seen: list[tuple[str, str]] = []

    def runner(root: str, **kw: Any) -> dict:
        seen.append((root, kw["expected_harness_sha256"]))
        return {"status": "built" if root == "ZN" else "refused"}

    rc = st.cli(["--products", "ZN", "ZB", "--harness-sha256", HARNESS], runner=runner)
    assert seen == [("ZN", HARNESS), ("ZB", HARNESS)] and rc == 1 and preflight_ok == [HARNESS]


def test_run_product_records_the_preflights_returned_sha(tmp_path: Path,
                                                         monkeypatch: pytest.MonkeyPatch) -> None:
    reports = make_inputs(tmp_path)
    monkeypatch.setattr(harness_freeze, "preflight", lambda e, root=None: "ee" * 32)
    summary = build(tmp_path, reports)
    assert summary["harness_sha256"] == "ee" * 32
