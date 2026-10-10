"""Harness v12 (Stage E.17): data.hist_store builds plan "ext2010h" stores, and base_rules'
hist_plan checks (check_name, check_plan with the default resolver, check_bookings) and its store
reader accept them.

Synthetic DBN chunks, purchase manifests, symbology and condition files under tmp_path; the real
2010-2019 group calendars in data/calendars/hist2010 (fx, rates and the v12 livestock copy). Three
roots: 6A (from 2010-07: its first trade date 2010-07-01 is partial, the 2010-06-30 17:00-19:00 CT
part of its Globex session lies in the unbought June chunk), TN (from 2016-01, with symbology that
starts in 2016 like the vendor's) and LE (livestock). Rows the build must never read are planted
invalid (off the tick grid, high below low): a check that read them would fail the build.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

from base_rules import hist_plan as HP
from base_rules import store as BS
from data import build_bars as bb
from data import hist_calendar as hc
from data import hist_store as hs
from data import pull_hist as ph
from screening import harness_freeze
from tests._e14_fixtures import bar, ct, make_store_inputs

HARNESS = "ef" * 32


@dataclass(frozen=True)
class Case:
    root: str
    group: str
    px: int  # 1e-9 units, on the root's tick grid
    splice: str
    iids: tuple[int, int]
    raws: tuple[str, str]
    bars: tuple[tuple[int, ...], ...]
    trade_dates: tuple[str, ...]  # expected in the store
    symbology_from: str | None = None  # a late root's vendor-like symbology start (UTC date)


def tick(root: str) -> int:
    return bb.tick_fixed(bb.load_ticks()[root][0])


def good(root: str, px: int, ts: int, k: int = 0) -> tuple[int, ...]:
    return bar(ts, px + k * tick(root), px + (k + 1) * tick(root))


def bad(root: str, px: int, ts: int) -> tuple[int, ...]:
    t = tick(root)
    return (ts, px + 7, px - 10 * t, px + 10 * t, px + 3, 5)  # off tick AND high < low


PX_6A, PX_TN, PX_LE = 900_000_000, 130_000_000_000, 950_000_000
SIX_A = Case("6A", "fx", PX_6A, "2010-09-13", (2001, 2002), ("6AU0", "6AZ0"), (
    good("6A", PX_6A, ct("2010-06-30", "19:00")),  # 00:00 UTC 07-01: the July chunk's first minute
    good("6A", PX_6A, ct("2010-06-30", "19:05"), 1),
    good("6A", PX_6A, ct("2010-07-01", "10:00"), 2),
    good("6A", PX_6A, ct("2010-09-14", "10:00")),  # after the splice
    good("6A", PX_6A, ct("2019-04-30", "10:00")),
    bad("6A", PX_6A, ct("2019-04-30", "17:30")),  # books to 2019-05-01: dropped unread
), ("2010-07-01", "2010-09-14", "2019-04-30"))
TN = Case("TN", "rates", PX_TN, "2016-02-26", (3001, 3002), ("TNH6", "TNM6"), (
    good("TN", PX_TN, ct("2016-01-10", "17:00")),  # Sunday evening, books to 2016-01-11
    good("TN", PX_TN, ct("2016-01-11", "10:00"), 1),
    good("TN", PX_TN, ct("2016-03-01", "10:00")),
    good("TN", PX_TN, ct("2019-04-30", "10:00")),
    bad("TN", PX_TN, ct("2019-04-30", "17:30")),  # books to 2019-05-01: dropped unread
), ("2016-01-11", "2016-03-01", "2019-04-30"), symbology_from="2016-01-10")
LE = Case("LE", "livestock", PX_LE, "2010-08-31", (4001, 4002), ("LEQ0", "LEV0"), (
    good("LE", PX_LE, ct("2010-06-30", "19:00")),  # the partial first trade date 2010-07-01
    good("LE", PX_LE, ct("2010-07-01", "10:00"), 1),
    good("LE", PX_LE, ct("2010-09-01", "10:00")),
    bad("LE", PX_LE, ct("2013-01-22", "10:00")),  # an unsourced (listed) date: dropped unread
    good("LE", PX_LE, ct("2019-04-30", "10:00")),
), ("2010-07-01", "2010-09-01", "2019-04-30"))


@pytest.fixture(autouse=True)
def preflight_ok(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    seen: list[str] = []
    monkeypatch.setattr(harness_freeze, "preflight",
                        lambda expected, root=None: seen.append(expected) or expected)
    return seen


def late_symbology(case: Case, path: Path) -> None:
    """Rewrite the cached symbology as the vendor would answer for a root listed later than the
    plan's data start: no mapping before ``symbology_from``."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    sym = f"{case.root}.v.0"
    payload["continuous_to_instrument_id"]["result"][sym][0]["d0"] = case.symbology_from
    for rows in payload["instrument_id_to_raw_symbol"]["result"].values():
        rows[0]["d0"] = case.symbology_from
    path.chmod(0o644)
    path.write_text(json.dumps(payload), encoding="utf-8")


def build(tmp_path: Path, case: Case) -> tuple[dict, Path]:
    paths = make_store_inputs(tmp_path, ph.EXT2010H, case.root, list(case.bars),
                              splice=case.splice, iids=case.iids, raws=case.raws)
    if case.symbology_from is not None:
        late_symbology(case, ph.symbology_cache_path(case.root, ph.EXT2010H, paths["rolls"]))
    summary = hs.run_product(case.root, "ext2010h", expected_harness_sha256=HARNESS,
                             out_base=tmp_path / "store", reports_base=paths["reports"],
                             rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                             calendar_base=hc.HIST_CALENDAR_DIR, log=lambda m: None)
    return summary, hs.hist_parquet_path(case.root, "ext2010h", tmp_path / "store")


@pytest.fixture(scope="module", params=[SIX_A, TN, LE], ids=lambda c: c.root)
def built(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory
          ) -> tuple[Case, dict, Path]:
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(harness_freeze, "preflight", lambda expected, root=None: expected)
        case = request.param
        summary, out = build(tmp_path_factory.mktemp(f"v12_{case.root}"), case)
    return case, summary, out


# ------------------------------------------------------------------ build ----
def test_the_store_is_built_with_the_ext2010h_name_window_and_metadata(
        built: tuple[Case, dict, Path]) -> None:
    # Arrange
    case, summary, out = built

    # Act
    meta = json.loads(pq.read_schema(out).metadata[b"propexperiment"])
    frame = pq.read_table(out).to_pandas()

    # Assert
    assert summary["status"] == "built", summary["refusal_causes"]
    assert out.name == f"ohlcv-1m_{case.root}_v_0_2010-07-01_2019-04-30_ext2010h.parquet"
    assert out.parent.name == case.root and out.parent.parent.name == "ext2010h"
    assert summary["window_trade_dates"] == ["2010-07-01", "2019-04-30"]
    assert summary["data_utc"] == ["2010-07-01", "2019-05-01"]
    assert meta["plan"] == "ext2010h" and meta["test"] == "E16"
    assert meta["trade_date_range"] == [case.trade_dates[0], case.trade_dates[-1]]
    assert tuple(sorted(set(frame["trade_date"]))) == case.trade_dates
    assert summary["first_trade_date"] == case.trade_dates[0]
    assert summary["raw_checks"]["off_tick_prices"] == 0  # the checks never saw the bad rows
    assert summary["validation"]["hard_failures"] == []
    assert summary["parquet"]["sha256"] == bb.sha256_file(out)
    cal = hc.load_hist_group_calendar(case.group)
    assert meta["hist_calendar"]["sha256"] == cal.file_sha256
    assert summary["purchase_manifest"]["path"].endswith(f"purchase_{case.root}_ext2010h.json")


def test_the_inputs_are_exactly_the_roots_own_chunk_list(built: tuple[Case, dict, Path]) -> None:
    case, summary, _ = built
    names = [f["name"] for f in summary["input_files"]]
    own = ph.EXT2010H.chunks_of(case.root)
    assert names == [f"range={s}_{e}.dbn.zst" for s, e in own]
    assert len(names) == {"6A": 106, "TN": 40, "LE": 106}[case.root]


def test_the_partial_first_trade_date_is_kept_and_rows_outside_are_dropped_unread(
        built: tuple[Case, dict, Path]) -> None:
    case, summary, out = built
    frame = pq.read_table(out).to_pandas()
    drops = summary["window_drops"]
    assert drops["before_first_trade_date"] == {}
    if case.root in ("6A", "LE"):  # the 2010-06-30 19:00 CT bar (00:00 UTC) books to 07-01
        first = frame[frame["trade_date"] == "2010-07-01"]
        assert len(first) == (3 if case.root == "6A" else 2)
        assert int(first["ts_event"].astype("int64").min()) == ct("2010-06-30", "19:00")
    if case.root in ("6A", "TN"):
        assert drops["after_last_trade_date_rows_dropped_unread"] == 1
        assert drops["after_last_trade_dates"] == ["2019-05-01"]
    if case.root == "LE":
        assert drops["unsourced_rows_dropped_unread"] == 1
        assert drops["unsourced_trade_dates_with_rows"] == {"2013-01-22": 1}


def test_base_rules_hist_plan_checks_accept_the_written_store(
        built: tuple[Case, dict, Path]) -> None:
    # Arrange
    case, _, out = built
    cal = hc.load_hist_group_calendar(case.group)
    meta = json.loads(pq.read_schema(out).metadata[b"propexperiment"])
    frame = pq.read_table(out).to_pandas()

    # Act
    first, last = HP.check_name(case.root, "ext2010h", out)
    window = HP.check_plan(case.root, "ext2010h", first, last, meta, HP.default_resolver, "t")
    booked = HP.check_bookings(case.root, window, cal, frame, "t")

    # Assert
    assert (first, last) == (date(2010, 7, 1), date(2019, 4, 30))
    assert window == HP.PlanWindow("ext2010h", date(2010, 7, 1), date(2019, 4, 30))
    assert tuple(sorted({d.isoformat() for d in booked})) == case.trade_dates


def test_base_rules_store_reader_accepts_the_written_store(
        built: tuple[Case, dict, Path]) -> None:
    case, summary, out = built
    cal = hc.load_hist_group_calendar(case.group)
    ref = BS.StoreRef(out, summary["parquet"]["sha256"], "ext2010h")
    frame, record = BS.read_era(case.root, BS.EXT2010, ref, cal)
    assert record["plan"] == "ext2010h" and record["rows"] == len(frame) == summary["bars"]
    assert record["trade_dates"] == len(case.trade_dates)
    assert len(record["splice_trade_dates"]) == 1


def test_a_late_roots_symbology_starts_with_its_listing_not_the_plans_data_start(
        built: tuple[Case, dict, Path]) -> None:
    case, summary, _ = built
    payload = json.loads(Path(summary["metadata_files"]["symbology"]["path"]).read_text())
    intervals = payload["continuous_to_instrument_id"]["result"][f"{case.root}.v.0"]
    want = case.symbology_from or "2010-07-01"
    assert intervals[0]["d0"] == want and payload["start_date"] == "2010-07-01"
    assert summary["rolls"]["splice_trade_dates"] == [
        {"6A": "2010-09-13", "TN": "2016-02-26", "LE": "2010-08-31"}[case.root]]


def test_base_rules_refuses_the_store_under_another_plan(built: tuple[Case, dict, Path]) -> None:
    case, summary, out = built
    with pytest.raises(HP.PlanRefused, match="fixed plan is 'ext2010h'"):
        HP.check_name(case.root, "ext2010", out)
    meta = {**json.loads(pq.read_schema(out).metadata[b"propexperiment"]), "plan": "ext2010"}
    with pytest.raises(HP.PlanRefused, match="metadata plan"):
        HP.check_plan(case.root, "ext2010h", date(2010, 7, 1), date(2019, 4, 30), meta,
                      HP.default_resolver, "t")


# ------------------------------------------------------------------ refusals ----
def test_an_input_list_other_than_the_roots_own_chunks_is_refused_unopened(
        tmp_path: Path) -> None:
    # Arrange: TN's manifest with the 2015-12 chunk added in front
    paths = make_store_inputs(tmp_path, ph.EXT2010H, "TN", [], splice=TN.splice, iids=TN.iids,
                              raws=TN.raws)
    manifest = json.loads(paths["manifest"].read_text())
    extra = dict(manifest["files"][0], name="range=2015-12-01_2016-01-01.dbn.zst",
                 request_start="2015-12-01", request_end="2016-01-01")
    manifest["files"] = [extra, *manifest["files"]]
    paths["manifest"].write_text(json.dumps(manifest))

    # Act / Assert
    with pytest.raises(hs.HistStoreRefused, match="inputs must be its 40 plan chunks"):
        hs.run_product("TN", "ext2010h", expected_harness_sha256=HARNESS,
                       out_base=tmp_path / "store", reports_base=paths["reports"],
                       rolls_dir=paths["rolls"], condition_dir=paths["condition_dir"],
                       calendar_base=hc.HIST_CALENDAR_DIR, log=lambda m: None)
    assert not (tmp_path / "store").exists()


def test_a_c1_root_or_a_non_root_is_refused_under_ext2010h(tmp_path: Path) -> None:
    for root in ("NG", "ES"):
        with pytest.raises(hs.HistStoreRefused, match="not a root of plan ext2010h"):
            hs.run_product(root, "ext2010h", expected_harness_sha256=HARNESS,
                           out_base=tmp_path / "store", reports_base=tmp_path / "r",
                           rolls_dir=tmp_path / "rolls", condition_dir=tmp_path / "c",
                           calendar_base=hc.HIST_CALENDAR_DIR, log=lambda m: None)


def test_the_cli_accepts_plan_ext2010h_and_runs_each_named_root() -> None:
    seen: list[tuple[str, str]] = []

    def runner(root: str, plan: str, **kwargs: object) -> dict:
        seen.append((root, plan))
        return {"status": "built"}

    assert hs.cli(["--plan", "ext2010h", "--products", "6A", "LE", "--harness-sha256", HARNESS],
                  runner=runner) == 0
    assert seen == [("6A", "ext2010h"), ("LE", "ext2010h")]
    seen.clear()
    assert hs.cli(["--plan", "ext2010h", "--harness-sha256", HARNESS], runner=runner) == 0
    assert [r for r, _ in seen] == list(ph.EXT2010H.roots)


def test_frame_columns_match_the_ext2010_store_layout(built: tuple[Case, dict, Path]) -> None:
    _, _, out = built
    frame: pd.DataFrame = pq.read_table(out).to_pandas()
    assert set(BS.COLUMNS) <= set(frame.columns)
