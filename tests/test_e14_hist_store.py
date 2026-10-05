"""Harness v10 (Stage E.14): data.hist_store (the es2011 and ext2010 stores) and data.hist_bars
(their loader).

Synthetic DBN chunks, purchase manifests, symbology and condition files under tmp_path, and the
synthetic fixture calendars; no vendor call, no real data. Rows the build must never read are
planted invalid (off the tick grid, high below low): a check that read them would fail the build.
"""

from __future__ import annotations

import json
import stat
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from data import build_bars as bb
from data import hist_bars as hb
from data import hist_store as hs
from data import pull_hist as ph
from data.stage_e_bars import HoldoutRowRefused, ParquetHashMismatch, StageEBarRefusal
from screening import harness_freeze
from tests._e14_fixtures import (
    FIXTURE_DIR,
    PX,
    TICK_ES,
    bar,
    ct,
    fixture_payload,
    make_store_inputs,
    write_calendar,
)

HARNESS = "ef" * 32
IIDS, RAWS, SPLICE = (1001, 1002), ("ESM3", "ESU3"), "2013-06-13"
BAD = (PX + 7, PX - 10 * TICK_ES, PX + 10 * TICK_ES, PX + 3, 5)  # off tick AND high < low


def good(ts: int, k: int = 0) -> tuple[int, ...]:
    return bar(ts, PX + k * TICK_ES, PX + (k + 1) * TICK_ES)


ES_BARS = [
    good(ct("2011-05-01", "17:00")),  # the first trade date's evening (2011-05-02)
    good(ct("2011-05-02", "14:59")), good(ct("2011-05-03", "14:29")),
    good(ct("2011-05-03", "14:30"), 1), good(ct("2011-05-03", "15:00"), 2),
    good(ct("2011-05-03", "15:15")),  # the close minute of the 15:15 halt: L-3, kept
    good(ct("2011-05-03", "15:20")),  # inside the 15:15-15:30 halt: kept and flagged
    good(ct("2012-10-29", "10:00")),  # inside the Sandy closure: booked to 10-30, flagged
    good(ct("2012-10-30", "10:00")), good(ct("2013-06-12", "10:00")),
    good(ct("2013-06-13", "10:00")),
    (ct("2015-06-15", "10:00"), *BAD), (ct("2015-06-15", "10:01"), *BAD),  # unsourced date
    good(ct("2019-04-30", "15:00")),
    (ct("2019-04-30", "17:30"), *BAD), (ct("2019-04-30", "17:31"), *BAD),  # 2019-05-01
    (ct("2019-04-30", "17:32"), *BAD),
]


@pytest.fixture(autouse=True)
def preflight_ok(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []
    monkeypatch.setattr(harness_freeze, "preflight",
                        lambda expected, root=None: seen.append(expected) or expected)
    return seen


def build(tmp_path: Path, root: str = "ES", plan: str = "es2011", bars: list | None = None,
          calendar_base: Path = FIXTURE_DIR, **inputs: Any) -> dict:
    paths = make_store_inputs(tmp_path, ph.get_plan(plan), root,
                              ES_BARS if bars is None else bars, splice=SPLICE, iids=IIDS,
                              raws=inputs.pop("raws", RAWS), **inputs)
    return hs.run_product(root, plan, expected_harness_sha256=HARNESS,
                          out_base=tmp_path / "store", reports_base=paths["reports"],
                          rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                          calendar_base=calendar_base, log=lambda m: None)


@pytest.fixture
def es_store(tmp_path: Path) -> tuple[dict, Path]:
    summary = build(tmp_path, degraded=("2011-05-03",))
    return summary, hs.hist_parquet_path("ES", "es2011", tmp_path / "store")


# ------------------------------------------------------------------ build ----
def test_the_store_lives_under_its_own_root_with_plan_specific_names() -> None:
    path = hs.hist_parquet_path("ES", "es2011")
    assert path.parts[-4:] == ("processed_hist", "es2011", "ES",
                               "ohlcv-1m_ES_v_0_2011-05-02_2019-04-30_es2011.parquet")
    assert "data/processed_hist" in harness_freeze.DATA_SUBDIRS
    assert hs.summary_path("NG", "ext2010").name == "bars_NG_ext2010.json"
    assert hs.expected_names("NG", ph.EXT2010)[0] == "range=2010-06-06_2010-07-01.dbn.zst"
    assert len(hs.expected_names("ES", ph.ES2011)) == 96


def test_the_es2011_build_drops_rows_outside_the_window_and_on_unsourced_dates_unread(
        es_store: tuple[dict, Path]) -> None:
    # Arrange
    summary, out = es_store

    # Act
    frame = pq.read_table(out).to_pandas()

    # Assert
    assert summary["status"] == "built", summary["refusal_causes"]
    drops = summary["window_drops"]
    assert drops["after_last_trade_date_rows_dropped_unread"] == 3
    assert drops["after_last_trade_dates"] == ["2019-05-01"]
    assert drops["unsourced_rows_dropped_unread"] == 2
    assert drops["unsourced_trade_dates_with_rows"] == {"2015-06-15": 2}
    assert summary["raw_checks"]["off_tick_prices"] == 0  # the checks never saw the bad rows
    assert summary["validation"]["hard_failures"] == []
    assert sorted(set(frame["trade_date"])) == [
        "2011-05-02", "2011-05-03", "2012-10-30", "2013-06-12", "2013-06-13", "2019-04-30"]
    assert summary["first_trade_date"] == "2011-05-02" and summary["bars"] == len(frame) == 12
    assert stat.S_IMODE(out.stat().st_mode) == 0o444
    assert summary["parquet"]["sha256"] == bb.sha256_file(out)


def test_closure_bars_beyond_the_close_minute_are_kept_flagged_and_counted(
        es_store: tuple[dict, Path]) -> None:
    summary, out = es_store
    frame = pq.read_table(out).to_pandas()
    closure = summary["closure_bars"]
    assert closure["beyond_close_minute_kept_and_flagged"] == 2 and closure["close_minute"] == 1
    assert closure["beyond_close_minute_by_trade_date"] == {"2011-05-03": 1, "2012-10-30": 1}
    assert int(frame["in_scheduled_closure"].sum()) == closure["total"] == 3  # L-3 bar too
    assert summary["status"] == "built" and "keep_and_flag" in summary["closure_policy"]


def test_the_summary_and_metadata_record_the_calendar_rolls_and_hashes(
        es_store: tuple[dict, Path]) -> None:
    summary, out = es_store
    meta = json.loads(pq.read_schema(out).metadata[b"propexperiment"])
    cal_sha = summary["hist_calendar"]["sha256"]
    assert meta["plan"] == "es2011" and meta["hist_calendar"]["sha256"] == cal_sha
    assert cal_sha == bb.sha256_file(FIXTURE_DIR / "equity.json")
    assert meta["splice_trade_dates"] == ["2013-06-13"]
    assert meta["roll_blackout_dates"] == ["2013-06-11", "2013-06-12", "2013-06-13"]
    assert meta["harness_sha256"] == HARNESS and summary["harness_sha256"] == HARNESS
    assert summary["degraded"]["on_store_trade_dates"] == ["2011-05-03"]
    assert summary["calendar_unsourced"]["unsourced_trade_dates"] == 1
    assert set(summary["metadata_files"]) == {"condition", "symbology"}
    assert summary["purchase_manifest"]["path"].endswith("purchase_ES_es2011.json")


def test_the_build_prints_counts_only(tmp_path: Path) -> None:
    logs: list[str] = []
    paths = make_store_inputs(tmp_path, ph.ES2011, "ES", ES_BARS, splice=SPLICE, iids=IIDS,
                              raws=RAWS)
    hs.run_product("ES", "es2011", expected_harness_sha256=HARNESS,
                   out_base=tmp_path / "store", reports_base=paths["reports"],
                   rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                   calendar_base=FIXTURE_DIR, log=logs.append)
    text = "\n".join(logs)
    assert "built" in text and "1300" not in text and "unsourced" in text


def test_an_existing_store_is_never_overwritten(tmp_path: Path) -> None:
    build(tmp_path)
    with pytest.raises(hs.HistStoreRefused, match="already exists"):
        hs.run_product("ES", "es2011", expected_harness_sha256=HARNESS,
                       out_base=tmp_path / "store", reports_base=tmp_path / "reports",
                       rolls_dir=tmp_path / "rolls", condition_dir=tmp_path / "condition",
                       calendar_base=FIXTURE_DIR, log=lambda m: None)


def test_the_ext2010_store_starts_with_the_june_2010_partial_chunk(tmp_path: Path) -> None:
    # Arrange: NG bars on the first trade date (its Sunday-evening open) and the last
    px = 4_000_000_000  # 4.000 (NG tick 0.001 = 1,000,000)
    bars = [bar(ct("2010-06-06", "18:00"), px, px + 1_000_000),
            bar(ct("2010-06-07", "10:00"), px, px), bar(ct("2019-04-30", "10:00"), px, px),
            (ct("2019-04-30", "17:30"), px + 7, px - 10, px + 10, px + 3, 1)]

    # Act
    summary = build(tmp_path, "NG", "ext2010", bars, raws=("NGN0", "NGQ0"))

    # Assert
    assert summary["status"] == "built", summary["refusal_causes"]
    assert summary["first_trade_date"] == "2010-06-07" and summary["trade_dates"] == 2
    assert summary["window_drops"]["after_last_trade_date_rows_dropped_unread"] == 1
    assert summary["input_files"][0]["name"] == "range=2010-06-06_2010-07-01.dbn.zst"
    assert len(summary["input_files"]) == 107


# ------------------------------------------------------------------ refusals ----
def _no_load(paths: list[Path]) -> Any:
    pytest.fail("a file was opened")


def test_inputs_other_than_the_plans_chunks_are_refused_before_any_file_is_opened(
        tmp_path: Path) -> None:
    paths = make_store_inputs(tmp_path, ph.ES2011, "ES", [], splice=SPLICE, iids=IIDS, raws=RAWS)
    manifest = json.loads(paths["manifest"].read_text())
    manifest["files"] = manifest["files"][1:]
    paths["manifest"].write_text(json.dumps(manifest))
    with pytest.raises(hs.HistStoreRefused, match="96 plan chunks"):
        hs.run_product("ES", "es2011", expected_harness_sha256=HARNESS,
                       out_base=tmp_path / "store", reports_base=paths["reports"],
                       rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                       calendar_base=FIXTURE_DIR, log=lambda m: None)
    spec = hs.hist_spec("ES", ph.ES2011, out_base=tmp_path / "store",
                        reports_base=paths["reports"], rolls_dir=paths["rolls"])
    with pytest.raises(hs.HistStoreRefused):
        hs.build_hist_product(spec, ph.ES2011, None, [], [], None, "x",  # type: ignore[arg-type]
                              harness_sha256=HARNESS, load_bars=_no_load)


def test_a_manifest_of_another_plan_or_a_root_outside_the_plan_is_refused(tmp_path: Path) -> None:
    paths = make_store_inputs(tmp_path, ph.ES2011, "ES", [], splice=SPLICE, iids=IIDS, raws=RAWS)
    manifest = json.loads(paths["manifest"].read_text())
    paths["manifest"].write_text(json.dumps({**manifest, "plan": "ext2010"}))
    with pytest.raises(hs.HistStoreRefused, match="not ES es2011"):
        hs.hist_spec("ES", ph.ES2011, reports_base=paths["reports"])
    with pytest.raises(hs.HistStoreRefused, match="not a root"):
        hs.run_product("NQ", "es2011", expected_harness_sha256=HARNESS,
                       reports_base=paths["reports"], log=lambda m: None)


def test_a_sealed_or_foreign_input_path_is_refused(tmp_path: Path) -> None:
    files = tuple(bb.InputFile(tmp_path / "sealed" / "ES_v_0" / n, "0" * 64, 0)
                  for n in hs.expected_names("ES", ph.ES2011))
    with pytest.raises(hs.HistStoreRefused, match="sealed store"):
        hs.refuse_inputs("ES", ph.ES2011, files, sealed_roots=(tmp_path / "sealed",))
    files = tuple(bb.InputFile(tmp_path / "NQ_v_0" / n, "0" * 64, 0)
                  for n in hs.expected_names("ES", ph.ES2011))
    with pytest.raises(hs.HistStoreRefused, match="own directory"):
        hs.refuse_inputs("ES", ph.ES2011, files, sealed_roots=())


@pytest.mark.parametrize("missing", ["symbology", "condition"])
def test_missing_free_metadata_is_refused_the_store_never_calls_the_vendor(
        tmp_path: Path, missing: str) -> None:
    paths = make_store_inputs(tmp_path, ph.ES2011, "ES", [], splice=SPLICE, iids=IIDS, raws=RAWS)
    victim = (ph.symbology_cache_path("ES", ph.ES2011, paths["rolls"]) if missing == "symbology"
              else ph.condition_path(ph.ES2011, paths["condition_dir"]))
    victim.unlink()
    with pytest.raises(hs.HistStoreRefused, match="missing"):
        hs.run_product("ES", "es2011", expected_harness_sha256=HARNESS,
                       out_base=tmp_path / "store", reports_base=paths["reports"],
                       rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                       calendar_base=FIXTURE_DIR, log=lambda m: None)


def test_a_root_the_hist_calendar_does_not_list_is_refused(tmp_path: Path) -> None:
    payload = fixture_payload("equity")
    payload["products"] = ["ES"]
    write_calendar(tmp_path / "cal", payload)
    with pytest.raises(hs.HistStoreRefused, match="not a product"):
        build(tmp_path, "NQ", "ext2010", [], calendar_base=tmp_path / "cal",
              raws=("NQM0", "NQU0"))


def test_the_store_refuses_when_the_harness_preflight_raises(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(expected: str, root: Path | None = None) -> str:
        raise harness_freeze.HarnessFreezeError("tree differs")

    monkeypatch.setattr(harness_freeze, "preflight", refuse)
    with pytest.raises(harness_freeze.HarnessFreezeError):
        hs.run_product("ES", "es2011", expected_harness_sha256=HARNESS, log=lambda m: None)
    assert hs.cli(["--plan", "es2011", "--harness-sha256", HARNESS]) == 2


# ------------------------------------------------------------------ the loader ----
def test_load_hist_leg_gives_the_leg_frame_with_the_roll_blackout(
        es_store: tuple[dict, Path], tmp_path: Path) -> None:
    # Arrange
    summary, out = es_store

    # Act
    leg = hb.load_hist_leg("ES", "es2011", expected_sha256=summary["parquet"]["sha256"],
                           hist_root=tmp_path / "store", calendar_base=FIXTURE_DIR)

    # Assert
    assert leg.store == "hist:es2011" and len(leg.frame) == 12
    assert leg.trade_dates[0] == date(2011, 5, 2) and leg.trade_dates[-1] == date(2019, 4, 30)
    assert leg.splice_trade_dates == (date(2013, 6, 13),)
    assert leg.roll_blackout == frozenset({date(2013, 6, 11), date(2013, 6, 12),
                                           date(2013, 6, 13)})


def test_load_hist_leg_refuses_an_unpinned_or_wrong_sha_and_another_calendar(
        es_store: tuple[dict, Path], tmp_path: Path) -> None:
    summary, _ = es_store
    sha = summary["parquet"]["sha256"]
    kw = {"hist_root": tmp_path / "store", "calendar_base": FIXTURE_DIR}
    with pytest.raises(ValueError, match="not a sha256"):
        hb.load_hist_leg("ES", "es2011", expected_sha256="", **kw)
    with pytest.raises(ParquetHashMismatch):
        hb.load_hist_leg("ES", "es2011", expected_sha256="0" * 64, **kw)
    with pytest.raises(StageEBarRefusal, match="not a root"):
        hb.load_hist_leg("NQ", "es2011", expected_sha256=sha, **kw)
    payload = fixture_payload("equity")
    payload["unsourced"].append({"day": "2016-06-15", "reason": "another file"})
    write_calendar(tmp_path / "other", payload)
    with pytest.raises(hb.HistStoreMismatch, match="calendar sha256"):
        hb.load_hist_leg("ES", "es2011", expected_sha256=sha, hist_root=tmp_path / "store",
                         calendar_base=tmp_path / "other")


def _rewrite(out: Path, base: Path, extra: pd.DataFrame) -> str:
    """The built store plus ``extra`` rows, same metadata, under ``base``; returns its sha."""
    table = pq.read_table(out)
    frame = pd.concat([table.to_pandas(), extra], ignore_index=True)
    target = hs.hist_parquet_path("ES", "es2011", base)
    target.parent.mkdir(parents=True)
    new = pa.Table.from_pandas(frame, preserve_index=False).replace_schema_metadata(
        table.schema.metadata)
    pq.write_table(new, target)
    return bb.sha256_file(target)


@pytest.mark.parametrize("stamp,label,error", [
    (("2019-04-30", "17:30"), "2019-05-01", HoldoutRowRefused),
    (("2015-06-15", "10:00"), "2015-06-15", hb.UnsourcedRowRefused),
    (("2011-05-04", "10:00"), "2011-05-05", hb.TradeDateMismatch),
])
def test_load_hist_leg_refuses_rows_outside_the_window_on_unsourced_dates_or_mislabelled(
        es_store: tuple[dict, Path], tmp_path: Path, stamp: tuple[str, str], label: str,
        error: type[Exception]) -> None:
    # Arrange
    _, out = es_store
    template = pq.read_table(out).to_pandas().iloc[[1]].copy()
    template["ts_event"] = ct(*stamp)
    template["trade_date"] = label
    sha = _rewrite(out, tmp_path / "bad", template)

    # Act / Assert
    with pytest.raises(error):
        hb.load_hist_leg("ES", "es2011", expected_sha256=sha, hist_root=tmp_path / "bad",
                         calendar_base=FIXTURE_DIR)
