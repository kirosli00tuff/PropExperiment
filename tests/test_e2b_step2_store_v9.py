"""Stage E.12 harness v9: data/step2_store.py's closure-ruling path (user decision 2026-10-03:
keep and flag, L-3's principle) and the loader check (data.stage_e_bars reads a store the v9 path
built, with ruled bars at an equity-halt minute and a daily-break minute, under the REAL equity
and FX group calendars).

Synthetic chunk files only: 58 zstd DBN files per product under tmp_path, a purchase manifest
listing them, tmp ruling and condition files. No network, no vendor file, no real store is read.
Every planted minute is a Central Time minute on the real group calendar (data.group_session):
equity's 15:15-15:30 CT halt and 16:00-17:00 CT break, FX's 16:00-17:00 CT break, in 2020.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import databento_dbn as dbn
import pandas as pd
import pyarrow.parquet as pq
import pytest
import zstandard

from data import stage_e_bars as seb
from data import step2_store as st
from data.group_session import group_of, load_group_calendar
from data.research_bars import CONFIRMATION_RAW_CHUNKS
from rules.products import product
from screening import harness_freeze

IID = 5150
HARNESS = "ab" * 32
# (price, tick) in 1e-9 units: NQ 10000.00 with tick 0.25; 6A 0.65000 with tick 0.00005.
PRICES = {"NQ": (10_000_000_000_000, 250_000_000), "6A": (650_000_000, 50_000)}
STORE_START = date(2019, 5, 6)

# Real-calendar minutes (CT). The deep closure bars are the held bars of reports/step2.
NQ_NORMAL = ("2020-03-30 15:00", "2020-03-30 15:30", "2020-06-30 15:59", "2020-06-30 17:00")
NQ_HALT = ("2020-03-30 15:29", "2020-03-30 Mon 15:29", "2020-03-30")  # equity halt minute
NQ_BREAK = ("2020-06-30 16:59", "2020-06-30 Tue 16:59", "2020-07-01")  # daily-break minute
NQ_EXTRA = ("2020-03-31 16:59", "2020-03-31 Tue 16:59", "2020-04-01")
FX_NORMAL = ("2020-06-30 15:59", "2020-06-30 17:00")
FX_BREAK = ("2020-06-30 16:59", "2020-06-30 Tue 16:59", "2020-07-01")


def ct_ns(stamp: str) -> int:
    return int(pd.Timestamp(stamp, tz="America/Chicago").tz_convert("UTC").value)


def values(root: str, k: int) -> tuple[int, int, int, int, int]:
    """Distinct on-tick OHLCV for bar k (high >= open, close >= low)."""
    px, tick = PRICES[root]
    return (px + k * tick, px + (k + 2) * tick, px + (k - 1) * tick, px + (k + 1) * tick, 10 + k)


def plant(root: str, minutes: tuple[str, ...]) -> dict[int, tuple[int, ...]]:
    """ts_ns -> planted OHLCV, one distinct bar per CT minute."""
    return {ct_ns(m): values(root, k) for k, m in enumerate(minutes, start=1)}


def _utc_ns(day: str) -> int:
    return int(pd.Timestamp(day, tz="UTC").value)


def write_chunk(path: Path, root: str, start: str, end: str,
                bars: list[tuple[int, tuple[int, ...]]]) -> None:
    mapping = SimpleNamespace(raw_symbol=f"{root}.v.0", intervals=[SimpleNamespace(
        start_date=date.fromisoformat(start), end_date=date.fromisoformat(end), symbol=str(IID))])
    meta = dbn.Metadata("GLBX.MDP3", _utc_ns(start), dbn.SType.CONTINUOUS,
                        dbn.SType.INSTRUMENT_ID, dbn.Schema.OHLCV_1M, symbols=[f"{root}.v.0"],
                        partial=[], not_found=[], mappings=[mapping], end=_utc_ns(end))
    raw = bytes(meta.encode()) + b"".join(
        bytes(dbn.OHLCVMsg(0x21, 1, IID, ts, o, h, lo, c, v)) for ts, (o, h, lo, c, v) in bars)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(zstandard.ZstdCompressor().compress(raw))


def make_inputs(tmp_path: Path, root: str, planted: dict[int, tuple[int, ...]]) -> Path:
    """The root's 58 synthetic chunks and purchase manifest; returns the reports base."""
    directory = tmp_path / "v" / "GLBX.MDP3" / "ohlcv-1m" / f"{root}_v_0"
    files = []
    for start, end in CONFIRMATION_RAW_CHUNKS:
        name = f"range={start}_{end}.dbn.zst"
        bars = sorted((ts, v) for ts, v in planted.items() if _utc_ns(start) <= ts < _utc_ns(end))
        write_chunk(directory / name, root, start, end, bars)
        files.append({"name": name, "path": str(directory / name), "request_start": start,
                      "request_end": end, "sha256": hashlib.sha256(
                          (directory / name).read_bytes()).hexdigest(),
                      "record_count": len(bars), "instrument_ids": [str(IID)]})
    reports = tmp_path / "reports"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / f"purchase_{root}.json").write_text(json.dumps(
        {"product": root, "files": files, "sealed_chunks": []}), encoding="utf-8")
    (tmp_path / "cond.json").write_text(json.dumps(
        [{"date": "2020-03-30", "condition": "available"}]), encoding="utf-8")
    return reports


def write_rulings(path: Path, rows: list[tuple[str, str, str]]) -> Path:
    path.write_text(json.dumps({
        "schema": "closure_rulings/1", "ruling": "test: keep and flag",
        "entries": [{"root": r, "ct": ct, "trade_date": td, "ruling": "keep_and_flag"}
                    for r, ct, td in rows]}, indent=1), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def preflight_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(harness_freeze, "preflight", lambda expected, root=None: expected)


def build(tmp_path: Path, root: str, minutes: tuple[str, ...], rulings: Path
          ) -> tuple[dict, dict[int, tuple[int, ...]]]:
    planted = plant(root, minutes)
    reports = make_inputs(tmp_path, root, planted)
    summary = st.run_product(root, expected_harness_sha256=HARNESS, out_base=tmp_path / "store",
                             reports_base=reports, rolls_dir=tmp_path / "rolls",
                             condition=tmp_path / "cond.json", client_factory=None,
                             log=lambda m: None, closure_rulings=rulings)
    return summary, planted


def store(tmp_path: Path, root: str) -> Path:
    return st.step2_parquet_path(root, tmp_path / "store")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def deep_bars(summary: dict) -> list[tuple[str, str]]:
    return [(c["ct"], c["trade_date"]) for c in summary["closure_bars"] if not c["close_minute"]]


# ------------------------------------------------------------------ the default ----
def test_the_ruling_file_is_the_stage_e12_report_and_a_frozen_input() -> None:
    rel = "reports/stage_e12_closure_rulings.json"
    assert rel == st.CLOSURE_RULINGS_PATH.relative_to(st.REPO_ROOT).as_posix()
    assert rel in harness_freeze.FROZEN_INPUTS  # hashed by the manifest, checked by preflight


def test_the_stage_e12_ruling_file_is_well_formed_when_present() -> None:
    if not st.CLOSURE_RULINGS_PATH.is_file():
        pytest.skip("the lead has not written the ruling file yet")
    entries, _ = st.load_closure_rulings(st.CLOSURE_RULINGS_PATH)
    assert entries and all(e["ruling"] == st.KEEP_AND_FLAG for e in entries)
    assert all(pd.Timestamp(e["ct"][:10]) <= pd.Timestamp(e["trade_date"]) for e in entries)


# ------------------------------------------------------------------- the hold ----
def test_without_a_ruling_file_a_deep_closure_bar_is_held_as_before(tmp_path: Path) -> None:
    # Arrange / Act
    summary, _ = build(tmp_path, "NQ", (*NQ_NORMAL, NQ_HALT[0]), tmp_path / "absent.json")

    # Assert
    assert summary["status"] == "held_for_lead"
    assert deep_bars(summary) == [NQ_HALT[1:]]
    assert summary["refusal_causes"][0] == (
        "1 bars inside a scheduled closure beyond the close minute (first 2020-03-30 Mon 15:29 "
        "CT): held for the lead before building (ruling L-3)")
    assert "no closure ruling file" in summary["refusal_causes"][1]
    assert "closure_ruling" not in summary and not store(tmp_path, "NQ").exists()


def test_an_unlisted_deep_bar_keeps_the_hold_and_is_named(tmp_path: Path) -> None:
    rulings = write_rulings(tmp_path / "r.json", [("NQ", *NQ_HALT[1:]), ("NQ", *NQ_BREAK[1:])])

    summary, _ = build(tmp_path, "NQ", (*NQ_NORMAL, NQ_HALT[0], NQ_BREAK[0], NQ_EXTRA[0]),
                       rulings)

    assert summary["status"] == "held_for_lead"
    assert summary["refusal_causes"][0].startswith("3 bars inside a scheduled closure")
    assert summary["refusal_causes"][1] == (
        "1 of them not listed in r.json: 2020-03-31 Tue 16:59 CT (trade date 2020-04-01)")
    assert "closure_ruling" not in summary and not store(tmp_path, "NQ").exists()


# ------------------------------------------------------------------- refusals ----
@pytest.mark.parametrize("listed", [
    [("NQ", *NQ_HALT[1:]), ("NQ", *NQ_BREAK[1:])],  # the 16:59 bar is not in the data
    [("NQ", NQ_HALT[1], "2020-03-31")],  # the right minute under the wrong trade date
])
def test_a_listed_entry_without_its_bar_refuses(tmp_path: Path,
                                                listed: list[tuple[str, str, str]]) -> None:
    rulings = write_rulings(tmp_path / "r.json", listed)

    summary, _ = build(tmp_path, "NQ", (*NQ_NORMAL, NQ_HALT[0]), rulings)

    assert summary["status"] == "refused"
    cause = summary["refusal_causes"][0]
    assert cause.startswith("closure ruling r.json (sha256 " + sha(rulings))
    assert "not bars inside a scheduled closure beyond the close minute" in cause
    assert f"{listed[-1][1]} CT (trade date {listed[-1][2]})" in cause
    assert "closure_ruling" not in summary and not store(tmp_path, "NQ").exists()


def test_a_listed_entry_refuses_even_when_the_build_has_no_deep_bar(tmp_path: Path) -> None:
    rulings = write_rulings(tmp_path / "r.json", [("NQ", *NQ_HALT[1:])])

    summary, _ = build(tmp_path, "NQ", NQ_NORMAL, rulings)

    assert summary["status"] == "refused" and "lists 1 NQ bar(s)" in summary["refusal_causes"][0]
    assert not store(tmp_path, "NQ").exists()


def test_a_malformed_ruling_file_refuses_the_build(tmp_path: Path) -> None:
    rulings = tmp_path / "r.json"
    rulings.write_text(json.dumps({"schema": "closure_rulings/0", "ruling": "x", "entries": []}),
                       encoding="utf-8")

    summary, _ = build(tmp_path, "NQ", (*NQ_NORMAL, NQ_HALT[0]), rulings)

    assert summary["status"] == "refused" and "schema" in summary["refusal_causes"][0]
    assert not store(tmp_path, "NQ").exists()


ENTRY = {"root": "NQ", "ct": NQ_HALT[1], "trade_date": NQ_HALT[2], "ruling": "keep_and_flag"}


@pytest.mark.parametrize(("payload", "match"), [
    (b"not json", "not JSON"),
    ({"schema": "closure_rulings/2", "ruling": "x", "entries": [ENTRY]}, "schema"),
    ({"schema": "closure_rulings/1", "ruling": " ", "entries": [ENTRY]}, "ruling text"),
    ({"schema": "closure_rulings/1", "ruling": "x", "entries": {"NQ": ENTRY}}, "entries list"),
    ({"schema": "closure_rulings/1", "ruling": "x", "entries": [{**ENTRY, "ruling": "drop"}]},
     "applies 'keep_and_flag' only"),
    ({"schema": "closure_rulings/1", "ruling": "x", "entries": [{**ENTRY, "note": "n"}]},
     "must hold exactly"),
    ({"schema": "closure_rulings/1", "ruling": "x", "entries": [{**ENTRY, "ct": 1529}]},
     "must hold exactly"),
    ({"schema": "closure_rulings/1", "ruling": "x", "entries": [ENTRY, dict(ENTRY)]}, "repeats"),
])
def test_load_closure_rulings_refuses_a_malformed_file(tmp_path: Path, payload: object,
                                                       match: str) -> None:
    path = tmp_path / "r.json"
    path.write_bytes(payload if isinstance(payload, bytes) else json.dumps(payload).encode())
    with pytest.raises(st.Step2StoreRefused, match=match):
        st.load_closure_rulings(path)


def test_load_closure_rulings_returns_the_entries_and_the_sha_of_the_bytes(tmp_path: Path
                                                                           ) -> None:
    path = write_rulings(tmp_path / "r.json", [("NQ", *NQ_HALT[1:]), ("6A", *FX_BREAK[1:])])
    entries, digest = st.load_closure_rulings(path)
    assert digest == sha(path) and [e["root"] for e in entries] == ["NQ", "6A"]


# -------------------------------------------------------------------- the build ----
def test_the_exact_ruling_builds_with_the_ruled_bars_flagged_and_unchanged(tmp_path: Path
                                                                           ) -> None:
    # Arrange: the file also rules a 6A bar, which the NQ build ignores.
    rulings = write_rulings(tmp_path / "r.json", [
        ("NQ", *NQ_HALT[1:]), ("6A", *FX_BREAK[1:]), ("NQ", *NQ_BREAK[1:])])

    # Act
    summary, planted = build(tmp_path, "NQ", (*NQ_NORMAL, NQ_HALT[0], NQ_BREAK[0]), rulings)

    # Assert: built, every bar written, the ruled ones flagged with their planted values
    assert summary["status"] == "built", summary["refusal_causes"]
    assert deep_bars(summary) == [NQ_HALT[1:], NQ_BREAK[1:]]
    out = store(tmp_path, "NQ")
    table = pq.read_table(out)
    frame = table.to_pandas()
    assert len(frame) == len(planted) == 6 and summary["bars"] == 6
    for minute, td in ((NQ_HALT[0], NQ_HALT[2]), (NQ_BREAK[0], NQ_BREAK[2])):
        row = frame[frame["ts_event"] == ct_ns(minute)]
        assert len(row) == 1 and bool(row["in_scheduled_closure"].iloc[0])
        assert str(row["trade_date"].iloc[0]) == td
        o, h, lo, c, v = planted[ct_ns(minute)]
        assert [row[k].iloc[0] for k in ("open", "high", "low", "close")] == [
            x / 1e9 for x in (o, h, lo, c)]
        assert int(row["volume"].iloc[0]) == v
    others = frame[~frame["ts_event"].isin([ct_ns(NQ_HALT[0]), ct_ns(NQ_BREAK[0])])]
    assert not others["in_scheduled_closure"].any()
    assert summary["flag_counts"]["in_scheduled_closure"] == 2
    # the ruling is recorded, with the file's sha256, in the summary, on disk and in the parquet
    expected = {"path": str(rulings), "sha256": sha(rulings), "bars_ruled": 2, "entries": [
        {"root": "NQ", "ct": NQ_HALT[1], "trade_date": NQ_HALT[2], "ruling": "keep_and_flag"},
        {"root": "NQ", "ct": NQ_BREAK[1], "trade_date": NQ_BREAK[2], "ruling": "keep_and_flag"}]}
    assert summary["closure_ruling"] == expected
    written = json.loads((tmp_path / "reports" / "bars_NQ.json").read_text(encoding="utf-8"))
    assert written["closure_ruling"] == expected and written["parquet"]["sha256"] == sha(out)
    meta = json.loads(table.schema.metadata[b"propexperiment"])
    assert meta["closure_ruling"] == expected and meta["harness_sha256"] == HARNESS


def test_a_build_without_deep_bars_records_no_ruling(tmp_path: Path) -> None:
    rulings = write_rulings(tmp_path / "r.json", [("6A", *FX_BREAK[1:])])

    summary, _ = build(tmp_path, "NQ", NQ_NORMAL, rulings)

    assert summary["status"] == "built" and deep_bars(summary) == []
    meta = json.loads(pq.read_schema(store(tmp_path, "NQ")).metadata[b"propexperiment"])
    assert "closure_ruling" not in summary and "closure_ruling" not in meta


def test_close_minute_bars_are_unchanged_and_cannot_be_ruled(tmp_path: Path) -> None:
    # 16:00 CT is the close minute of the equity day session (L-3: booked to that session).
    summary, _ = build(tmp_path, "NQ", (*NQ_NORMAL, "2020-06-30 16:00"), tmp_path / "absent.json")
    assert summary["status"] == "built", summary["refusal_causes"]
    assert [c["close_minute"] for c in summary["closure_bars"]] == [True]
    assert summary["closure_bars"][0]["trade_date"] == "2020-06-30"
    assert "closure_ruling" not in summary

    other = tmp_path / "second"
    other.mkdir()
    rulings = write_rulings(other / "r.json", [("NQ", "2020-06-30 Tue 16:00", "2020-06-30")])
    summary, _ = build(other, "NQ", (*NQ_NORMAL, "2020-06-30 16:00"), rulings)
    assert summary["status"] == "refused" and "lists 1 NQ bar(s)" in summary["refusal_causes"][0]


# --------------------------------------------------------------- the loader check ----
def _loader_reads(tmp_path: Path, root: str, summary: dict, ruled: list[tuple[str, ...]]) -> None:
    """data.stage_e_bars reads the v9 store (no TradeDateUnbookable, TradeDateMismatch or
    HoldoutRowRefused) and books every ruled bar to the trade date the summary shows."""
    out = store(tmp_path, root)
    digest = summary["parquet"]["sha256"]
    assert digest == sha(out)
    shown = {c["ct"]: c["trade_date"] for c in summary["closure_bars"]}
    leg = seb.read_leg(root, out, seb.STEP2, expected_sha256=digest)
    conf = seb.load_confirmation_leg(root, tmp_path / "store", STORE_START,
                                     expected_sha256=digest)
    dates, _ = seb.read_leg_dates(root, tmp_path / "store", STORE_START, expected_sha256=digest)
    assert len(leg.frame) == len(conf.frame) == summary["bars"]
    assert set(dates) == set(conf.trade_dates) == set(leg.trade_dates)
    for minute, ct, td in ruled:
        assert shown[ct] == td
        for frame in (leg.frame, conf.frame):
            row = frame[frame["ts_event"] == ct_ns(minute)]
            assert len(row) == 1 and str(row["trade_date"].iloc[0]) == td
            assert bool(row["in_scheduled_closure"].iloc[0])
        assert date.fromisoformat(td) in conf.trade_dates
    booked = seb.book_trade_dates(load_group_calendar(product(root).group),
                                  conf.frame["ts_event"].to_numpy())
    assert [d.isoformat() for d in booked] == list(conf.frame["trade_date"].astype(str))


def test_the_loader_reads_a_v9_equity_store_with_ruled_halt_and_break_bars(tmp_path: Path
                                                                          ) -> None:
    # Arrange: NQ's held minutes of reports/step2/bars_NQ.json, on the REAL equity calendar
    ruled = [NQ_HALT, NQ_EXTRA, NQ_BREAK]
    rulings = write_rulings(tmp_path / "r.json", [("NQ", ct, td) for _, ct, td in ruled])
    summary, _ = build(tmp_path, "NQ", (*NQ_NORMAL, *(m for m, _, _ in ruled)), rulings)
    assert summary["status"] == "built", summary["refusal_causes"]
    assert group_of("NQ") == product("NQ").group == "equity"
    assert "data/calendars/equity.py" in summary["calendar_modules"]

    # Act / Assert
    _loader_reads(tmp_path, "NQ", summary, ruled)
    cut = seb.load_confirmation_leg("NQ", tmp_path / "store", date(2020, 4, 1),
                                    expected_sha256=summary["parquet"]["sha256"])
    assert ct_ns(NQ_EXTRA[0]) in set(cut.frame["ts_event"])  # 03-31 16:59 CT is 04-01's bar
    assert ct_ns(NQ_HALT[0]) not in set(cut.frame["ts_event"])


def test_the_loader_reads_a_v9_fx_store_with_a_ruled_break_bar(tmp_path: Path) -> None:
    # Arrange: 6A's held minute of reports/step2/bars_6A.json, on the REAL FX calendar
    rulings = write_rulings(tmp_path / "r.json", [("6A", *FX_BREAK[1:])])
    summary, _ = build(tmp_path, "6A", (*FX_NORMAL, FX_BREAK[0]), rulings)
    assert summary["status"] == "built", summary["refusal_causes"]
    assert group_of("6A") == product("6A").group == "fx"
    assert "data/calendars/fx.py" in summary["calendar_modules"]

    # Act / Assert
    _loader_reads(tmp_path, "6A", summary, [FX_BREAK])
