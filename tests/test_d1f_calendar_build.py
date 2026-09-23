"""Stage D.1f Task 3b: the 2019-2024 CME calendar, the coverage assertion, the confirmation
bar build and the step-4b calendar validator. Synthetic data only; every written path is under
tmp_path; no Databento call (fetchers are injected and fail the test if called unexpectedly).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import stat
import subprocess
from dataclasses import astuple
from datetime import date, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pytest

import data.build_mes_bars as bmb
from data.adapter import MES_CONTINUOUS, OHLCV_1M, RollBoundary, raw_path, write_rolls
from data.bars import add_flags, is_mes_outright, raw_symbols_on_bar_dates
from data.cme_calendar import (
    CALENDAR_COVERAGE,
    ENTRIES_2025_2026_SHA256,
    HOLIDAYS,
    NO_ENTRY_FINDINGS_2019_2024,
    SOURCES_2019_2024,
    CalendarCoverageError,
    HolidayKind,
    assert_calendar_coverage,
    entries_2025_2026_block,
)
from data.config import REPO_ROOT
from data.research_bars import (
    CONFIRMATION_RAW_CHUNKS,
    CONFIRMATION_SERIES_PATH,
    HOLDOUT2_RAW_CHUNKS,
    load_confirmation_bars,
)
from data.session import HALT_END, closed_windows_range_ns, ct_ns
from data.validate import (
    EARLY_STOP_NOT_LISTED,
    ENTRY_NOT_OBSERVED,
    UNLISTED_CLOSURE,
    in_windows,
    validate_calendar_step4b,
)
from sim.engine import splice_trade_dates_from_parquet

M = 60 * 1_000_000_000
CALENDAR = REPO_ROOT / "data" / "cme_calendar.py"
EXTRACTION = REPO_ROOT / "reports" / "stage_d1f_calendar_sources.json"
PINNED_COMMIT = "9cbd815"
PRICE = 4_000_000_000_000  # 4000.00 in Databento fixed point, on the 0.25 grid


# ------------------------------------------------------------------ helpers ----
def _open_minutes(first_day: date, last_day: date) -> np.ndarray:
    """Every scheduled-open minute (data.session's windows) of the trade dates first..last."""
    closed = closed_windows_range_ns(first_day, last_day)
    starts = np.array([w[0] for w in closed], dtype=np.int64)
    ends = np.array([w[1] for w in closed], dtype=np.int64)
    grid = np.arange(ct_ns(first_day - timedelta(days=1), HALT_END), ct_ns(last_day, HALT_END),
                     M, dtype=np.int64)
    return grid[~in_windows(grid, starts, ends)]


def _drop(ts: np.ndarray, lo: int, hi: int) -> np.ndarray:
    return ts[(ts < lo) | (ts >= hi)]


def _raw(ts: np.ndarray, ids: np.ndarray, source_file: str) -> pd.DataFrame:
    n = len(ts)
    return pd.DataFrame({
        "ts_event": np.asarray(ts, dtype=np.int64), "instrument_id": np.asarray(ids, np.int64),
        "open_fixed": [PRICE] * n, "high_fixed": [PRICE + 250_000_000] * n,
        "low_fixed": [PRICE - 250_000_000] * n, "close_fixed": [PRICE] * n,
        "volume": [5] * n, "source_file": [source_file] * n,
    })


def _never(*_args: object) -> object:
    raise AssertionError("a vendor fetch was attempted where none may happen")


# ------------------------------------------- the calendar: pins and citations ----
def test_2025_2026_entry_lines_keep_the_pinned_hash() -> None:
    block = entries_2025_2026_block(CALENDAR.read_text())
    assert hashlib.sha256(block.encode()).hexdigest() == ENTRIES_2025_2026_SHA256
    assert block.count("\n") == 37


def _pinned_source() -> str:
    if shutil.which("git") is None:
        pytest.skip("git not available")
    proc = subprocess.run(["git", "show", f"{PINNED_COMMIT}:data/cme_calendar.py"],
                          cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        pytest.skip(f"commit {PINNED_COMMIT} not in this clone")
    return proc.stdout


def test_2025_2026_entry_lines_are_byte_identical_to_the_declared_commit() -> None:
    old = _pinned_source()
    # The declared file (list section 0) hashed to 5f24edda...; its entry block is ours.
    assert hashlib.sha256(old.encode()).hexdigest().startswith("5f24edda9504ca7e")
    assert entries_2025_2026_block(CALENDAR.read_text()) == entries_2025_2026_block(old)
    assert hashlib.sha256(entries_2025_2026_block(old).encode()).hexdigest() == \
        ENTRIES_2025_2026_SHA256


def test_holidays_for_2025_2026_are_unchanged(tmp_path: Path,
                                              monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib.util
    import sys

    source = tmp_path / "cme_calendar_9cbd815.py"
    source.write_text(_pinned_source())
    spec = importlib.util.spec_from_file_location("cme_calendar_9cbd815", source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "cme_calendar_9cbd815", module)
    spec.loader.exec_module(module)
    old = {d: (h.name, h.kind.value, h.halt_ct, h.evidence, h.time_evidence)
           for d, h in module.HOLIDAYS.items()}
    new = {d: (h.name, h.kind.value, h.halt_ct, h.evidence, h.time_evidence)
           for d, h in HOLIDAYS.items() if d.year >= 2025}
    assert new == old and len(old) == 26


def test_every_2019_2024_entry_has_a_source_and_a_grade() -> None:
    early = {d: h for d, h in HOLIDAYS.items() if d.year < 2025}
    assert len(early) == 68 and set(early) == set(SOURCES_2019_2024)
    assert min(early) >= CALENDAR_COVERAGE[0]
    for day, hol in early.items():
        cite = SOURCES_2019_2024[day]
        assert cite.status_quote.strip(), day
        assert hol.evidence in {"cme", "secondary", "unverified"}, day
        assert hol.time_evidence in {"cme", "secondary", "inferred", "unverified", "n/a"}, day
        if hol.evidence != "unverified":
            assert cite.status_url and cite.status_url.startswith("https://"), day
        if hol.kind is HolidayKind.FULL_CLOSURE:
            assert hol.halt_ct is None and hol.time_evidence == "n/a", day
        else:
            assert hol.halt_ct is not None and cite.time_quote and cite.time_url, day
        if "unverified" in (hol.evidence, hol.time_evidence):
            assert "[unverified]" in cite.status_quote + cite.note, day
    assert HOLIDAYS[date(2021, 1, 1)].evidence == "unverified"
    assert HOLIDAYS[date(2021, 4, 2)].time_evidence == "unverified"


def test_2019_2024_quotes_are_verbatim_from_the_extraction() -> None:
    rows = {r["date"]: r for r in json.loads(EXTRACTION.read_text())}
    cited = {**SOURCES_2019_2024, **NO_ENTRY_FINDINGS_2019_2024}
    assert len(rows) == 71 and {d.isoformat() for d in cited} == set(rows)
    for day, cite in cited.items():
        row = rows[day.isoformat()]
        assert (cite.status_url, cite.status_quote) == (row["status_source_url"],
                                                        row["status_quote"]), day
        assert (cite.time_url, cite.time_quote) == (row["time_source_url"],
                                                    row["time_quote"]), day


def test_judgment_calls_are_the_documented_ones() -> None:
    # 12:00 CT equity SETTLEMENT lines -> 12:15 CT close, graded inferred (2025 convention).
    for day in (date(2019, 7, 3), date(2019, 11, 29), date(2019, 12, 24), date(2020, 11, 27),
                date(2020, 12, 24), date(2021, 11, 26), date(2022, 11, 25), date(2023, 7, 3),
                date(2023, 11, 24), date(2024, 7, 3), date(2024, 11, 29), date(2024, 12, 24)):
        assert HOLIDAYS[day].halt_ct == time(12, 15), day
        assert HOLIDAYS[day].time_evidence == "inferred", day
    for day in (date(2021, 4, 2), date(2023, 4, 7)):  # jobs-report Good Fridays
        assert HOLIDAYS[day].kind is HolidayKind.EARLY_HALT
        assert HOLIDAYS[day].halt_ct == time(8, 15)
    # CME-direct NORMAL days carry no entry; Jan 1 2022 (a Saturday) has none either.
    for day in (*NO_ENTRY_FINDINGS_2019_2024, date(2022, 1, 1)):
        assert day not in HOLIDAYS, day


# ------------------------------------------------------- the coverage assertion ----
def test_calendar_coverage_is_2019_through_2026() -> None:
    assert (date(2019, 1, 1), date(2026, 12, 31)) == CALENDAR_COVERAGE
    assert_calendar_coverage([date(2019, 1, 1), date(2022, 6, 1), date(2026, 12, 31)])
    with pytest.raises(CalendarCoverageError, match="2018-12-31"):
        assert_calendar_coverage([date(2019, 5, 6), date(2018, 12, 31)])
    with pytest.raises(CalendarCoverageError):
        assert_calendar_coverage([date(2027, 1, 4)])


def _flag(ts: list[int]) -> pd.DataFrame:
    raw = _raw(np.array(ts), np.array([1] * len(ts)), "x")
    return add_flags(raw, [], np.array([], dtype=np.int64), np.array([], dtype=np.int64),
                     np.zeros(len(ts), dtype=np.int64), set())


def test_bar_builder_refuses_a_2018_trade_date_and_accepts_2019_to_2026() -> None:
    with pytest.raises(CalendarCoverageError):
        _flag([ct_ns(date(2018, 6, 5), time(10, 0))])
    out = _flag([ct_ns(date(2019, 5, 6), time(10, 0)), ct_ns(date(2026, 12, 30), time(10, 0))])
    assert [str(d) for d in out["trade_date"]] == ["2019-05-06", "2026-12-30"]


# --------------------------------------------------- the per-date raw-symbol rule ----
SYMBOLOGY_2019 = {
    "7849": [{"d0": "2019-04-01", "d1": "2019-04-14", "s": "DNMH929 C35"},
             {"d0": "2019-04-14", "d1": "2019-06-17", "s": "MESM9"}],
    "7859": [{"d0": "2019-06-17", "d1": "2019-09-16", "s": "MESU9"}],
}


def test_mes_outright_pattern() -> None:
    for sym in ("MESM9", "MESH0", "MESZ3", "MESF4"):
        assert is_mes_outright(sym), sym
    for sym in ("DNMH929 C35", "MESM19", "MES", "MESA9", "ESM9", "MESM9-MESU9", " MESM9"):
        assert not is_mes_outright(sym), sym


def test_raw_symbol_is_the_one_mapped_on_the_bars_own_date() -> None:
    ts = np.array([ct_ns(date(2019, 4, 10), time(10, 0)),  # 7849 is 'DNMH929 C35' that day
                   ct_ns(date(2019, 5, 6), time(10, 0)),  # 7849 is MESM9 from 04-14
                   ct_ns(date(2019, 6, 20), time(10, 0)),  # 7859 is MESU9
                   ct_ns(date(2019, 6, 20), time(10, 1)),  # 7849 is unmapped after 06-17
                   ct_ns(date(2019, 5, 6), time(10, 1))])  # 4242 is not in the symbology
    ids = np.array([7849, 7849, 7859, 7849, 4242])
    symbols, unmapped = raw_symbols_on_bar_dates(ts, ids, SYMBOLOGY_2019)
    assert symbols.tolist() == ["", "MESM9", "MESU9", "", ""]
    assert sorted((u["utc_date"], u["instrument_id"], tuple(u["mapped_symbols"]))
                  for u in unmapped) == [("2019-04-10", 7849, ("DNMH929 C35",)),
                                         ("2019-05-06", 4242, ()), ("2019-06-20", 7849, ())]


def test_raw_symbol_uses_the_utc_date_at_the_splice() -> None:
    # 2019-04-13 23:30 UTC is 18:30 CDT on 04-13 (trade date Monday 04-15) but UTC 04-13:
    # symbology still says 'DNMH929 C35'; half an hour later (UTC 04-14) it says MESM9.
    before = int(pd.Timestamp("2019-04-13T23:30:00Z").value)
    after = int(pd.Timestamp("2019-04-14T00:00:00Z").value)
    symbols, _ = raw_symbols_on_bar_dates(np.array([before, after]), np.array([7849, 7849]),
                                          SYMBOLOGY_2019)
    assert symbols.tolist() == ["", "MESM9"]


def test_two_outrights_on_one_id_and_date_raise() -> None:
    bad = {"1": [{"d0": "2020-01-01", "d1": "2020-02-01", "s": "MESH0"},
                 {"d0": "2020-01-15", "d1": "2020-03-01", "s": "MESM0"}]}
    with pytest.raises(ValueError, match="several MES outrights"):
        raw_symbols_on_bar_dates(np.array([ct_ns(date(2020, 1, 20), time(9, 0))]),
                                 np.array([1]), bad)


def test_confirmation_drops_before_the_stop_date_do_not_stop() -> None:
    ts = np.concatenate([_open_minutes(date(2019, 5, 2), date(2019, 5, 3)),
                         _open_minutes(date(2019, 5, 6), date(2019, 5, 6))])
    symbology = {"7849": [{"d0": "2019-04-01", "d1": "2019-05-05", "s": "DNMH929 C35"},
                          {"d0": "2019-05-05", "d1": "2019-06-17", "s": "MESM9"}]}
    keep, symbols, log = bmb.confirmation_drops(_raw(ts, np.full(ts.size, 7849), "x"),
                                                symbology)
    drops = log["raw_symbol_drops"]
    assert drops["total"] == 2 * 1380 and drops["on_or_after_stop_date"] == 0
    assert drops["by_trade_month"] == {"2019-05": 2 * 1380}
    assert {g["utc_date"] for g in drops["groups"]} == {"2019-05-01", "2019-05-02",
                                                         "2019-05-03"}
    assert set(symbols[keep]) == {"MESM9"} and keep.sum() == 1380


# ------------------------------------------------------ the confirmation build ----
def _inputs(tmp_path: Path) -> bmb.ConfirmationInputs:
    vendor = tmp_path / "vendor"
    for s, e in CONFIRMATION_RAW_CHUNKS:  # empty stand-ins: the loader is injected
        path = raw_path(MES_CONTINUOUS, OHLCV_1M, s, e, vendor)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    return bmb.ConfirmationInputs.under(vendor, out=tmp_path / "processed" / "conf.parquet",
                                        summary=tmp_path / "reports" / "build.json")


def _condition(extra: dict[str, str]) -> list[dict]:
    days = [*bmb.DEGRADED_DATES_AT_DECLARATION, "2024-02-26"]
    return [{"date": d, "condition": extra.get(d, "degraded"), "last_modified_date": d}
            for d in days]


def _symbology_fetcher(result: dict, calls: list) -> object:
    def fetch(ids: list[str]) -> dict:
        calls.append(ids)
        return {"queried_instrument_ids": ids, "start_date": "2019-04-01",
                "end_date": "2024-03-01", "response": {"result": result}}
    return fetch


FEB24 = raw_path(MES_CONTINUOUS, OHLCV_1M, "2024-02-01", "2024-03-01", Path("/x")).name
ROLL_FEB24 = RollBoundary("MES.v.0", "2024-02-28", int(pd.Timestamp("2024-02-28", tz="UTC").value),
                          "12", "13", "MESH4", "MESM4")
SYMBOLOGY_2024 = {"12": [{"d0": "2023-09-15", "d1": "2024-03-16", "s": "MESH4"}],
                  "13": [{"d0": "2023-12-15", "d1": "2024-06-21", "s": "MESM4"}]}


def _feb24_bars() -> pd.DataFrame:
    # Trade dates 2024-02-26..03-01; the Feb chunk ends 2024-03-01 00:00 UTC, so only the
    # first hour of trade date 03-01 (Thu 17:00-18:00 CST) is in it and must be dropped.
    ts = _open_minutes(date(2024, 2, 26), date(2024, 3, 1))
    ts = ts[ts < int(pd.Timestamp("2024-03-01", tz="UTC").value)]
    ids = np.where(ts < ROLL_FEB24.ts_ns, 12, 13)
    return _raw(ts, ids, FEB24)


def test_confirmation_build_end_to_end(tmp_path: Path) -> None:
    inputs = _inputs(tmp_path)
    write_rolls([ROLL_FEB24], inputs.rolls)
    seen: list = []
    sym_calls: list = []
    cond_calls: list = []
    rc = bmb.build_confirmation(
        inputs, load_bars=lambda paths: seen.append(list(paths)) or _feb24_bars(),
        fetch_condition=lambda: cond_calls.append(1) or _condition({"2022-01-02": "available"}),
        fetch_raw_symbols=_symbology_fetcher(SYMBOLOGY_2024, sym_calls), log=lambda _m: None,
        manifest_sha256="e" * 64)
    assert rc == 0
    assert seen == [bmb.confirmation_raw_paths(inputs.vendor_root)] and len(seen[0]) == 58
    assert len(cond_calls) == 1 and sym_calls == [["12", "13"]]

    summary = json.loads(inputs.summary.read_text())
    assert summary["manifest_sha256"] == "e" * 64  # review F2: the freeze it was built under
    assert json.loads(pq.read_schema(inputs.out).metadata[b"propexperiment"])[
        "manifest_sha256"] == "e" * 64
    assert summary["trade_date_window_drops"]["after_last_trade_date"] == {"2024-03-01": 60}
    assert summary["raw_symbol_drops"]["total"] == 0 and summary[bmb.STOP_KEY] is False
    assert summary["trade_date_range"] == ["2024-02-26", "2024-02-29"]
    assert summary["calendar_validation_step4b"]["passed"] is True
    cmp = summary["degraded_dates_comparison"]
    assert cmp["added_since_declaration"] == ["2024-02-26"]
    assert cmp["missing_since_declaration"] == ["2022-01-02"] and cmp["identical"] is False

    assert not inputs.out.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    assert not inputs.condition.stat().st_mode & stat.S_IWUSR
    bars = load_confirmation_bars(path=inputs.out)
    assert str(bars["trade_date"].max()) == "2024-02-29" and len(bars) == 4 * 1380
    assert set(bars["raw_symbol"]) == {"MESH4", "MESM4"}
    assert set(bars.loc[bars["instrument_id"] == 13, "raw_symbol"]) == {"MESM4"}
    assert splice_trade_dates_from_parquet(inputs.out) == (date(2024, 2, 28),)
    assert bars.loc[bars["trade_date"] == "2024-02-28", "is_roll_session"].all()
    assert bars.loc[bars["trade_date"] == "2024-02-26", "vendor_degraded_day"].any()

    # Re-run: the output exists, so it refuses before reading anything or fetching anything.
    assert bmb.build_confirmation(inputs, load_bars=_never, fetch_condition=_never,
                                  fetch_raw_symbols=_never, log=lambda _m: None) == 5
    # Nothing reached the repository's own processed/ or reports/ paths.
    assert not CONFIRMATION_SERIES_PATH.exists()
    assert not bmb.CONFIRMATION_SUMMARY_PATH.exists()


def test_a_raw_symbol_drop_from_2019_05_06_stops_the_run(tmp_path: Path) -> None:
    inputs = _inputs(tmp_path)
    write_rolls([RollBoundary("MES.v.0", "2019-06-17",
                              int(pd.Timestamp("2019-06-17", tz="UTC").value), "7849", "7859",
                              "DNMH929 C35", "MESU9")], inputs.rolls)
    # 7849 still maps to the non-outright through UTC 2019-05-06: the whole trade date
    # 2019-05-06 (Sun 17:00 CDT .. Mon 16:00 CDT) is dropped, and that must stop the run.
    symbology = {"7849": [{"d0": "2019-04-01", "d1": "2019-05-07", "s": "DNMH929 C35"},
                          {"d0": "2019-05-07", "d1": "2019-06-17", "s": "MESM9"}]}
    ts = _open_minutes(date(2019, 5, 6), date(2019, 5, 8))
    name = raw_path(MES_CONTINUOUS, OHLCV_1M, "2019-05-01", "2019-06-01", Path("/x")).name
    rc = bmb.build_confirmation(
        inputs, load_bars=lambda _p: _raw(ts, np.full(ts.size, 7849), name),
        fetch_condition=lambda: _condition({}), log=lambda _m: None,
        fetch_raw_symbols=_symbology_fetcher(symbology, []))
    assert rc == bmb.RC_STOP_FOR_LEAD
    summary = json.loads(inputs.summary.read_text())
    drops = summary["raw_symbol_drops"]
    assert summary[bmb.STOP_KEY] is True and summary["stop_reasons"]
    assert drops["on_or_after_stop_date"] == drops["total"] > 0
    assert set(drops["by_trade_month"]) == {"2019-05"}
    assert {tuple(g["mapped_symbols"]) for g in drops["groups"]} == {("DNMH929 C35",)}
    meta = json.loads(pq.read_schema(inputs.out).metadata[b"propexperiment"])
    assert meta[bmb.STOP_KEY] is True and meta["raw_symbol_drops_total"] == drops["total"]
    assert set(load_confirmation_bars(path=inputs.out)["raw_symbol"]) == {"MESM9"}


def test_a_hard_failure_writes_no_series(tmp_path: Path) -> None:
    inputs = _inputs(tmp_path)
    write_rolls([ROLL_FEB24], inputs.rolls)
    bars = _feb24_bars()
    bars.loc[5, "close_fixed"] = PRICE + 1  # off the 0.25 tick grid
    rc = bmb.build_confirmation(inputs, load_bars=lambda _p: bars, log=lambda _m: None,
                                fetch_condition=lambda: _condition({}),
                                fetch_raw_symbols=_symbology_fetcher(SYMBOLOGY_2024, []))
    assert rc == 2 and not inputs.out.exists()
    assert json.loads(inputs.summary.read_text())["raw_hard_failures"]


def test_holdout2_and_foreign_chunk_paths_are_refused(tmp_path: Path) -> None:
    root = tmp_path / "vendor"
    bmb.check_confirmation_paths(bmb.confirmation_raw_paths(root), root)  # all 58 pass
    for s, e in HOLDOUT2_RAW_CHUNKS:
        with pytest.raises(bmb.ConfirmationBuildRefused, match="holdout-2"):
            bmb.check_confirmation_paths([raw_path(MES_CONTINUOUS, OHLCV_1M, s, e, root)], root)
    elsewhere = raw_path(MES_CONTINUOUS, OHLCV_1M, "2024-03-01", "2024-04-01", tmp_path / "o")
    with pytest.raises(bmb.ConfirmationBuildRefused, match="holdout-2"):
        bmb.check_confirmation_paths([elsewhere], root)
    for s, e in (("2025-04-01", "2025-05-01"), ("2019-04-01", "2019-05-01")):
        with pytest.raises(bmb.ConfirmationBuildRefused, match="not one of the 58"):
            bmb.check_confirmation_paths([raw_path(MES_CONTINUOUS, OHLCV_1M, s, e, root)], root)
    moved = raw_path(MES_CONTINUOUS, OHLCV_1M, "2020-01-01", "2020-02-01", tmp_path / "other")
    with pytest.raises(bmb.ConfirmationBuildRefused, match="not one of the 58"):
        bmb.check_confirmation_paths([moved], root)


def test_bars_from_a_file_outside_the_list_are_refused(tmp_path: Path) -> None:
    inputs = _inputs(tmp_path)
    write_rolls([ROLL_FEB24], inputs.rolls)
    sealed = raw_path(MES_CONTINUOUS, OHLCV_1M, "2024-03-01", "2024-04-01", Path("/x")).name
    bars = _feb24_bars().assign(source_file=sealed)
    with pytest.raises(bmb.ConfirmationBuildRefused, match="outside the 58"):
        bmb.build_confirmation(inputs, load_bars=lambda _p: bars, log=lambda _m: None,
                               fetch_condition=lambda: _condition({}),
                               fetch_raw_symbols=_symbology_fetcher(SYMBOLOGY_2024, []))
    assert not inputs.out.exists()


def test_a_frozen_symbology_file_for_other_ids_is_refused(tmp_path: Path) -> None:
    inputs = _inputs(tmp_path)
    write_rolls([ROLL_FEB24], inputs.rolls)
    inputs.symbology.parent.mkdir(parents=True)
    inputs.symbology.write_text(json.dumps({"queried_instrument_ids": ["12"],
                                            "response": {"result": SYMBOLOGY_2024}}))
    with pytest.raises(bmb.ConfirmationBuildRefused, match=r"\['13'\]"):
        bmb.build_confirmation(inputs, load_bars=lambda _p: _feb24_bars(), log=lambda _m: None,
                               fetch_condition=lambda: _condition({}), fetch_raw_symbols=_never)


def test_cli_routes_the_confirmation_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bmb, "d1f_freeze_check", lambda: ([], "f" * 64))
    monkeypatch.setattr(bmb, "build_confirmation",
                        lambda **kw: 41 if kw == {"manifest_sha256": "f" * 64} else 0)
    monkeypatch.setattr(bmb, "main", lambda: 40)
    assert bmb.cli(["--confirmation"]) == 41 and bmb.cli([]) == 40
    # review F2: a harness that differs from the freeze manifest is refused before any read
    monkeypatch.setattr(bmb, "d1f_freeze_check", lambda: (["manifest file changed: x"], "f" * 64))
    assert bmb.cli(["--confirmation"]) == bmb.RC_FREEZE_REFUSED


# ---------------------------------------------------- the degraded-date compare ----
def test_degraded_date_comparison() -> None:
    declared = [{"date": d, "condition": "degraded"} for d in bmb.DEGRADED_DATES_AT_DECLARATION]
    same = bmb.compare_degraded_dates(declared)
    assert same["identical"] and not same["added_since_declaration"]
    assert not same["missing_since_declaration"] and len(same["frozen"]) == 8
    changed = [d for d in declared if d["date"] != "2020-05-05"]
    changed.append({"date": "2023-03-10", "condition": "missing"})
    diff = bmb.compare_degraded_dates(changed)
    assert not diff["identical"]
    assert diff["added_since_declaration"] == ["2023-03-10"]
    assert diff["missing_since_declaration"] == ["2020-05-05"]


# ------------------------------------------------------ the step-4b validator ----
# 2019-11-25 .. 2020-01-03 holds Thanksgiving (12:00 halt), the day after (12:15), Christmas
# Eve (12:15), Christmas (closure) and New Year's Day 2020 (closure after a normal day).
SPAN = (date(2019, 11, 25), date(2020, 1, 3))
LISTED_IN_SPAN = (date(2019, 11, 28), date(2019, 11, 29), date(2019, 12, 24),
                  date(2019, 12, 25), date(2020, 1, 1))


@pytest.fixture(scope="module")
def clean_ts() -> np.ndarray:
    return _open_minutes(*SPAN)


def _kinds(ts: np.ndarray) -> set[tuple[str, date]]:
    return {(d.kind, d.day) for d in validate_calendar_step4b(ts).discrepancies}


def test_step4b_passes_a_clean_series(clean_ts: np.ndarray) -> None:
    result = validate_calendar_step4b(clean_ts)
    assert result.passed and not result.discrepancies
    assert (result.first_day, result.last_day) == SPAN
    assert result.entries_checked == LISTED_IN_SPAN
    assert result.as_dict()["passed"] is True


def test_step4b_passes_the_pre_2021_schedule(clean_ts: np.ndarray) -> None:
    # Before 2021-06-28 equity futures traded to 16:15 CT with a 15:15-15:30 CT pause. The
    # calendar is not at fault for either, so step 4b must not report them.
    extra, gone = [], []
    for n in range((SPAN[1] - SPAN[0]).days + 1):
        day = SPAN[0] + timedelta(days=n)
        if day.weekday() < 5 and day not in HOLIDAYS:
            extra += [ct_ns(day, time(16, m)) for m in range(15)]
            gone.append((ct_ns(day, time(15, 15)), ct_ns(day, time(15, 30))))
    ts = clean_ts
    for lo, hi in gone:
        ts = _drop(ts, lo, hi)
    assert validate_calendar_step4b(np.concatenate([ts, extra])).passed


def test_step4b_catches_an_unlisted_weekday_closure(clean_ts: np.ndarray) -> None:
    ts = _drop(clean_ts, ct_ns(date(2019, 12, 2), HALT_END), ct_ns(date(2019, 12, 3), HALT_END))
    assert _kinds(ts) == {(UNLISTED_CLOSURE, date(2019, 12, 3))}


def test_step4b_catches_an_unlisted_early_halt(clean_ts: np.ndarray) -> None:
    ts = _drop(clean_ts, ct_ns(date(2019, 12, 4), time(13, 0)),
               ct_ns(date(2019, 12, 4), HALT_END))
    assert _kinds(ts) == {(EARLY_STOP_NOT_LISTED, date(2019, 12, 4))}
    detail = validate_calendar_step4b(ts).discrepancies[0].detail
    assert "12:59" in detail and "no calendar entry" in detail


def test_step4b_catches_a_listed_halt_at_the_wrong_time(clean_ts: np.ndarray) -> None:
    day = date(2019, 11, 29)  # listed 12:15; the bars stop after 11:59
    ts = _drop(clean_ts, ct_ns(day, time(12, 0)), ct_ns(day, time(12, 15)))
    assert _kinds(ts) == {(EARLY_STOP_NOT_LISTED, day), (ENTRY_NOT_OBSERVED, day)}


def test_step4b_catches_a_listed_entry_not_observed(clean_ts: np.ndarray) -> None:
    # Christmas 2019: the reopen bar at 17:00 CT is missing. Christmas Eve's 12:15 halt runs
    # into the same closed window, so both entries see it.
    reopen = ct_ns(date(2019, 12, 25), HALT_END)
    assert _kinds(_drop(clean_ts, reopen, reopen + M)) == {
        (ENTRY_NOT_OBSERVED, date(2019, 12, 24)), (ENTRY_NOT_OBSERVED, date(2019, 12, 25))}
    # A Friday-evening reopen is not involved: dropping New Year's 2020 reopen hits only it.
    reopen = ct_ns(date(2020, 1, 1), HALT_END)
    assert _kinds(_drop(clean_ts, reopen, reopen + M)) == {
        (ENTRY_NOT_OBSERVED, date(2020, 1, 1))}
    # Thanksgiving 2019 traded through its listed 12:00 CT halt to the normal close.
    day = date(2019, 11, 28)
    extra = np.arange(ct_ns(day, time(12, 0)), ct_ns(day, time(16, 0)), M, dtype=np.int64)
    assert _kinds(np.concatenate([clean_ts, extra])) == {(ENTRY_NOT_OBSERVED, day)}
    # New Year's Day 2020 had bars: a listed closure that did not happen.
    inside = np.array([ct_ns(date(2020, 1, 1), time(9, 0))], dtype=np.int64)
    found = _kinds(np.concatenate([clean_ts, inside]))
    assert (ENTRY_NOT_OBSERVED, date(2020, 1, 1)) in found


def test_step4b_refuses_to_pass_on_no_bars() -> None:
    with pytest.raises(ValueError, match="no bars"):
        validate_calendar_step4b(np.array([], dtype=np.int64))


def test_holiday_dataclass_roundtrip_is_stable() -> None:
    # astuple keeps the Holiday fields positional: the consumers (session, engine, splits)
    # read day, kind and halt_ct only.
    hol = HOLIDAYS[date(2019, 12, 24)]
    assert astuple(hol)[:4] == (date(2019, 12, 24), "Christmas Eve", HolidayKind.EARLY_HALT,
                                time(12, 15))
