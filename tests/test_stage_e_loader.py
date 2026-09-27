"""Stage E bar loader (data/stage_e_bars.py): trade-date refusals by the group calendar, roll
blackouts from the group calendar (L-8), the research and step 2 stores. Synthetic files only."""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from data import stage_e_bars as sb
from data.stage_e_bars import (
    ConfirmationStoreMissing,
    HoldoutRowRefused,
    ParquetHashMismatch,
    RollMetadataMismatch,
    TradeDateMismatch,
    TradeDateUnbookable,
    forbidden_class,
    load_confirmation_leg,
    load_research_leg,
    read_leg_dates,
    research_parquet_path,
)
from tests._stage_e_synthetic import product_frame, ts_ns, write_parquet

MBT_DAY = date(2026, 6, 18)


def _meta(rolls: list[dict] | None = None, **extra: object) -> dict:
    return {"rolls": rolls or [], **extra}


def _write(root: str, frame: pd.DataFrame, base: Path, meta: dict | None = None
           ) -> tuple[Path, str]:
    path = research_parquet_path(root, base)
    write_parquet(frame, path, meta or _meta())
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _mbt_frame() -> pd.DataFrame:
    return product_frame("MBT", [MBT_DAY], 3, start=(10, 0), end=(11, 0), base_ticks=20000)


def _planted_row(frame: pd.DataFrame, ns: int, label: str) -> pd.DataFrame:
    row = frame.iloc[[-1]].copy()
    row["ts_event"] = ns
    row["trade_date"] = label
    return pd.concat([frame, row], ignore_index=True)


def test_forbidden_classes_cover_holdout1_holdout2_and_the_march_2024_embargo() -> None:
    assert forbidden_class(date(2026, 6, 22)) == "holdout-1"
    assert forbidden_class(date(2027, 1, 4)) == "holdout-1"
    assert forbidden_class(date(2024, 4, 1)) == "holdout-2"
    assert forbidden_class(date(2025, 3, 31)) == "holdout-2"
    assert forbidden_class(date(2024, 3, 15)) == "embargo (March 2024)"
    assert forbidden_class(date(2024, 2, 29)) is None
    assert forbidden_class(date(2025, 4, 1)) is None
    assert forbidden_class(date(2026, 6, 19)) is None


def test_a_clean_mbt_file_loads_with_its_calendar_trade_dates(tmp_path: Path) -> None:
    _, sha = _write("MBT", _mbt_frame(), tmp_path)
    leg = load_research_leg("MBT", tmp_path, expected_sha256=sha)
    assert leg.trade_dates == (MBT_DAY,)
    assert len(leg.frame) == 60 and leg.sha256 == sha


def test_mbt_rows_booked_to_holdout1_trade_date_2026_06_22_are_refused_ruling_L9(
        tmp_path: Path) -> None:
    """Ruling L-9 (the lead's Task 9 DECISIONS entry cites this test): CME books MBT's trading
    from Thursday 2026-06-18 16:02 CT through Saturday 2026-06-20 to trade date 2026-06-22
    (holdout-1). A row stamped 2026-06-19 12:00 CT is refused even when the file labels it
    2026-06-19 (booking by the crypto calendar, not by the label or the timestamp)."""
    planted = _planted_row(_mbt_frame(), ts_ns(date(2026, 6, 19), 12, 0), "2026-06-19")
    _, sha = _write("MBT", planted, tmp_path)
    with pytest.raises(HoldoutRowRefused, match="holdout-1 \\(first 2026-06-22\\)"):
        load_research_leg("MBT", tmp_path, expected_sha256=sha)


def test_mbt_rows_labelled_2026_06_22_are_refused_too(tmp_path: Path) -> None:
    planted = _planted_row(_mbt_frame(), ts_ns(MBT_DAY, 16, 5), "2026-06-22")
    _, sha = _write("MBT", planted, tmp_path)
    with pytest.raises(HoldoutRowRefused, match="holdout-1"):
        load_research_leg("MBT", tmp_path, expected_sha256=sha)


def test_a_row_past_the_calendar_coverage_is_unbookable_and_refused(tmp_path: Path) -> None:
    frame = product_frame("ZN", [date(2026, 6, 19)], 1, start=(9, 0), end=(9, 30))
    planted = _planted_row(frame, ts_ns(date(2026, 6, 22), 9, 0), "2026-06-19")
    _, sha = _write("ZN", planted, tmp_path)
    with pytest.raises(TradeDateUnbookable, match="could belong to holdout-1"):
        load_research_leg("ZN", tmp_path, expected_sha256=sha)


def test_holdout2_and_embargo_rows_are_refused_in_the_step2_store(tmp_path: Path, monkeypatch
                                                                    ) -> None:
    monkeypatch.setattr(sb, "_step2_parquet_path", lambda root, base: Path(base) / f"{root}.pq")
    for day, cls in ((date(2024, 4, 2), "holdout-2"), (date(2024, 3, 4), "embargo")):
        frame = product_frame("ZN", [date(2024, 2, 27), day], 2, start=(9, 0), end=(9, 10))
        base = tmp_path / cls
        write_parquet(frame, base / "ZN.pq", _meta())
        with pytest.raises(HoldoutRowRefused, match=cls):
            load_confirmation_leg("ZN", base, date(2019, 5, 6),
                                  expected_sha256=_sha(base / "ZN.pq"))


def test_a_research_row_outside_the_research_store_range_is_refused(tmp_path: Path) -> None:
    frame = product_frame("ZN", [date(2025, 3, 31), date(2025, 4, 1)], 2, start=(9, 0),
                          end=(9, 10))
    _, sha = _write("ZN", frame, tmp_path)
    with pytest.raises(HoldoutRowRefused, match="holdout-2"):
        load_research_leg("ZN", tmp_path, expected_sha256=sha)
    frame = product_frame("ZN", [date(2024, 2, 27)], 2, start=(9, 0), end=(9, 10))
    _, sha = _write("ZN", frame, tmp_path / "old")
    with pytest.raises(HoldoutRowRefused, match="outside the research store"):
        load_research_leg("ZN", tmp_path / "old", expected_sha256=sha)


def test_a_label_that_differs_from_the_calendar_booking_is_refused(tmp_path: Path) -> None:
    frame = product_frame("ZN", [date(2025, 6, 2)], 1, start=(9, 0), end=(9, 10))
    frame.loc[3, "trade_date"] = "2025-06-03"
    _, sha = _write("ZN", frame, tmp_path)
    with pytest.raises(TradeDateMismatch, match="label 2025-06-03, booked 2025-06-02"):
        load_research_leg("ZN", tmp_path, expected_sha256=sha)


def test_a_research_parquet_whose_hash_differs_from_the_recorded_one_is_refused(
        tmp_path: Path) -> None:
    _write("ZN", product_frame("ZN", [date(2025, 6, 2)], 1, start=(9, 0), end=(9, 10)), tmp_path)
    with pytest.raises(ParquetHashMismatch):
        load_research_leg("ZN", tmp_path, expected_sha256="0" * 64)


def test_roll_blackout_comes_from_the_group_calendar_L8(tmp_path: Path) -> None:
    """A grain splice at 00:00 UTC Monday 2025-06-16 books to that trade date; its blackout adds
    the two GRAIN trade dates before it (Thursday 06-12 and Friday 06-13), and a metadata record
    that disagrees is refused."""
    days = [date(2025, 6, 12), date(2025, 6, 13), date(2025, 6, 16)]
    frame = product_frame("ZC", days, 4, start=(9, 0), end=(9, 10), base_ticks=1800)
    splice = {"ts_ns": ts_ns(date(2025, 6, 15), 19, 0)}  # 00:00 UTC Monday
    _, sha = _write("ZC", frame, tmp_path, _meta([splice]))
    leg = load_research_leg("ZC", tmp_path, expected_sha256=sha)
    assert leg.splice_trade_dates == (date(2025, 6, 16),)
    assert leg.roll_blackout == {date(2025, 6, 12), date(2025, 6, 13), date(2025, 6, 16)}
    _, sha = _write("ZC", frame, tmp_path / "bad",
                    _meta([splice], roll_blackout_dates=["2025-06-16"]))
    with pytest.raises(RollMetadataMismatch, match="L-8"):
        load_research_leg("ZC", tmp_path / "bad", expected_sha256=sha)


def test_the_confirmation_path_refuses_cleanly_when_the_step2_store_is_absent(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def no_store(name: str, *args: object, **kwargs: object) -> object:
        if name == "data.step2_store":
            raise ImportError("No module named 'data.step2_store'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_store)
    with pytest.raises(ConfirmationStoreMissing, match="step 2 store has not been built"):
        load_confirmation_leg("ZN", tmp_path, date(2020, 1, 2), expected_sha256="0" * 64)
    monkeypatch.setattr(builtins, "__import__", real_import)
    monkeypatch.setattr(sb, "_step2_parquet_path", lambda root, base: Path(base) / f"{root}.pq")
    with pytest.raises(ConfirmationStoreMissing, match="does not exist"):
        load_confirmation_leg("ZN", tmp_path, date(2020, 1, 2), expected_sha256="0" * 64)


def test_the_confirmation_path_cuts_at_s_x_after_checking_the_whole_file(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sb, "_step2_parquet_path", lambda root, base: Path(base) / f"{root}.pq")
    days = [date(2020, 1, 2), date(2020, 1, 3), date(2020, 1, 6)]
    write_parquet(product_frame("ZN", days, 5, start=(9, 0), end=(9, 5)), tmp_path / "ZN.pq",
                  _meta())
    sha = _sha(tmp_path / "ZN.pq")
    leg = load_confirmation_leg("ZN", tmp_path, date(2020, 1, 3), expected_sha256=sha)
    assert leg.trade_dates == (date(2020, 1, 3), date(2020, 1, 6)) and len(leg.frame) == 10
    assert leg.sha256 == sha
    dates, blackout = read_leg_dates("ZN", tmp_path, date(2020, 1, 3), expected_sha256=sha)
    assert dates == leg.trade_dates and blackout == frozenset()
    with pytest.raises(ValueError, match="outside"):
        load_confirmation_leg("ZN", tmp_path, date(2019, 5, 3), expected_sha256=sha)


def test_the_research_root_is_the_callers_not_the_repositorys(tmp_path: Path) -> None:
    path = research_parquet_path("ZN", tmp_path)
    assert path.parent == tmp_path / "ZN" and path.name.endswith("_research.parquet")
    assert not np.any([str(p).startswith(str(Path("data") / "processed")) for p in [path]])


def test_the_confirmation_path_reads_the_step2_store_layout_of_data_step2_store(
        tmp_path: Path) -> None:
    """No monkeypatch: the path comes from data.step2_store.step2_parquet_path(root, base), the
    layout PurchaseCoder2 fixed (data/processed_step2/<ROOT>/..._step2.parquet under the root)."""
    from data.step2_store import step2_parquet_path

    days = [date(2020, 1, 2), date(2020, 1, 3)]
    path = step2_parquet_path("ZN", tmp_path)
    assert path.parent == tmp_path / "ZN" and path.name.endswith("_step2.parquet")
    write_parquet(product_frame("ZN", days, 5, start=(9, 0), end=(9, 5)), path, _meta())
    leg = load_confirmation_leg("ZN", tmp_path, date(2020, 1, 2), expected_sha256=_sha(path))
    assert leg.trade_dates == tuple(days) and leg.store == "step2"


# ------------------------------------ review F-3: the step 2 store read is pinned ----
def test_a_step2_store_other_than_the_one_the_start_rule_read_is_refused(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sb, "_step2_parquet_path", lambda root, base: Path(base) / f"{root}.pq")
    days = [date(2020, 1, 2), date(2020, 1, 3)]
    frame = product_frame("ZN", days, 5, start=(9, 0), end=(9, 5))
    write_parquet(frame, tmp_path / "ZN.pq", _meta())
    recorded = _sha(tmp_path / "ZN.pq")  # what the start-rule file recorded
    doctored = frame.assign(volume=frame["volume"] * 3)  # volumes changed, prices untouched
    write_parquet(doctored, tmp_path / "ZN.pq", _meta())
    with pytest.raises(ParquetHashMismatch, match="not the recorded"):
        load_confirmation_leg("ZN", tmp_path, date(2020, 1, 2), expected_sha256=recorded)
    with pytest.raises(ParquetHashMismatch, match="not the recorded"):
        read_leg_dates("ZN", tmp_path, date(2020, 1, 2), expected_sha256=recorded)


@pytest.mark.parametrize("expected", [None, "", "A" * 64, "0" * 63])
def test_a_step2_read_without_a_pinned_sha256_is_refused(tmp_path: Path, monkeypatch,
                                                         expected) -> None:
    monkeypatch.setattr(sb, "_step2_parquet_path", lambda root, base: Path(base) / f"{root}.pq")
    write_parquet(product_frame("ZN", [date(2020, 1, 2)], 5, start=(9, 0), end=(9, 5)),
                  tmp_path / "ZN.pq", _meta())
    with pytest.raises(ValueError, match="not a sha256"):
        load_confirmation_leg("ZN", tmp_path, date(2020, 1, 2), expected_sha256=expected)
    with pytest.raises(ValueError, match="not a sha256"):
        read_leg_dates("ZN", tmp_path, date(2020, 1, 2), expected_sha256=expected)
