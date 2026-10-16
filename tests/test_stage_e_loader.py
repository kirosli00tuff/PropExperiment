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


# ================================== harness v13 (Stage E.22): price path, MES ====
import json  # noqa: E402

from data.stage_e_bars import (  # noqa: E402
    ClosureRulingMismatch,
    PricePathMismatch,
    check_confirmation_store,
    check_price_path,
)

GC_DAYS = [date(2020, 1, 2), date(2020, 1, 3), date(2020, 1, 6), date(2020, 1, 7)]


def _gc_store(base: Path) -> tuple[Path, str]:
    """A GC step 2 store with one roll on 2020-01-06 (data.step2_store's layout)."""
    from data.step2_store import step2_parquet_path

    path = step2_parquet_path("GC", base)
    rolls = [{"ts_ns": ts_ns(GC_DAYS[2], 9, 0)}]
    write_parquet(product_frame("GC", GC_DAYS, 7, start=(9, 0), end=(9, 5), base_ticks=15000),
                  path, _meta(rolls))
    return path, _sha(path)


def test_v13_a_mapped_leg_reads_the_path_store_keyed_and_booked_as_the_vehicle(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """N1: MGC's confirmation leg on GC's store: the vehicle's root and group calendar, the path
    file's name and pinned sha256, the path store's own splices as the roll blackout; MGC's own
    store is never opened (none exists)."""
    path, sha = _gc_store(tmp_path)
    groups: list[str] = []
    real = sb.load_group_calendar
    monkeypatch.setattr(sb, "load_group_calendar", lambda g: groups.append(g) or real(g))
    leg = load_confirmation_leg("MGC", tmp_path, GC_DAYS[1], expected_sha256=sha,
                                path_root="GC")
    assert leg.root == "MGC" and Path(leg.path) == path and leg.sha256 == sha
    assert leg.trade_dates == tuple(GC_DAYS[1:]) and leg.store == sb.STEP2
    assert leg.splice_trade_dates == (GC_DAYS[2],) and GC_DAYS[2] in leg.roll_blackout
    assert set(groups) == {sb.product("MGC").group}
    dates, blackout = read_leg_dates("MGC", tmp_path, GC_DAYS[1], expected_sha256=sha,
                                     path_root="GC")
    assert dates == leg.trade_dates and blackout == leg.roll_blackout
    got = check_confirmation_store("MGC", tmp_path, expected_sha256=sha, path_root="GC")
    assert got == {"root": "MGC", "path": str(path), "sha256": sha}
    with pytest.raises(ConfirmationStoreMissing):  # unmapped, MGC reads its own (absent) store
        load_confirmation_leg("MGC", tmp_path, GC_DAYS[1], expected_sha256=sha)
    with pytest.raises(ParquetHashMismatch):  # the path store is pinned like any other
        load_confirmation_leg("MGC", tmp_path, GC_DAYS[1], expected_sha256="0" * 64,
                              path_root="GC")


@pytest.mark.parametrize(("vehicle", "path_root", "match"), [
    ("MGC", "NQ", "group"), ("MGC", "SI", "tick"), ("MCL", "NG", "tick"),
    ("MGC", "MGC", "another root"), ("MES", "ES", "never mapped"), ("ES", "MES", "never mapped"),
])
def test_v13_a_price_path_must_share_group_grid_and_tick(tmp_path: Path, vehicle: str,
                                                         path_root: str, match: str) -> None:
    with pytest.raises(PricePathMismatch, match=match):
        check_price_path(vehicle, path_root)
    with pytest.raises(PricePathMismatch, match=match):
        load_confirmation_leg(vehicle, tmp_path, date(2020, 1, 2), expected_sha256="0" * 64,
                              path_root=path_root, research_root=tmp_path)
    assert check_price_path("MGC", "GC") == "GC" and check_price_path("MNQ", "NQ") == "NQ"


# ------------------------------------------------ N3: MES's Stage D store ----
MES_DAYS = [date(2020, 3, 30), date(2020, 3, 31), date(2020, 4, 1), date(2020, 4, 2)]
CLOSURE_PRINTS = [(MES_DAYS[0], MES_DAYS[1]), (MES_DAYS[1], MES_DAYS[2])]  # (label, booking)


def _mes_store(research: Path, extra: list[tuple[date, str]] = ()) -> tuple[Path, str]:
    """D.1f's layout under the research root: 16:59 CT closure prints labelled with the session
    they follow (D.1's builder), which the equity calendar books to the next trade date."""
    frame = product_frame("MES", MES_DAYS, 11, start=(9, 0), end=(9, 5), base_ticks=10000)
    for label, _booked in CLOSURE_PRINTS:
        frame = _planted_row(frame, ts_ns(label, 16, 59), label.isoformat())
    for day, label in extra:
        frame = _planted_row(frame, ts_ns(day, 16, 59), label)
    path = sb.mes_confirmation_path(research)
    write_parquet(frame.sort_values("ts_event").reset_index(drop=True), path, _meta())
    return path, _sha(path)


def _rulings(tmp: Path, store_sha: str, monkeypatch: pytest.MonkeyPatch,
             entries: list[dict] | None = None) -> Path:
    if entries is None:
        entries = [{"root": "MES", "ts_event_ns": ts_ns(label, 16, 59),
                    "ct": sb._ct_str(ts_ns(label, 16, 59)), "store_label": label.isoformat(),
                    "trade_date": booked.isoformat(), "ruling": "rebook_and_flag"}
                   for label, booked in CLOSURE_PRINTS]
    path = tmp / "rulings.json"
    path.write_text(json.dumps({"schema": sb.MES_CLOSURE_RULINGS_SCHEMA, "ruling": "test",
                                "store": {"path": "x", "sha256": store_sha},
                                "entries": entries}), encoding="utf-8")
    monkeypatch.setattr(sb, "MES_CLOSURE_RULINGS_PATH", path)
    monkeypatch.setattr(sb, "MES_CLOSURE_RULINGS_SHA256", _sha(path))
    return path


def test_v13_mes_reads_d1fs_store_under_the_research_root_with_the_enumerated_rebookings(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    research = tmp_path / "research"
    path, sha = _mes_store(research)
    _rulings(tmp_path, sha, monkeypatch)
    leg = load_confirmation_leg("MES", tmp_path / "no_step2", MES_DAYS[0], expected_sha256=sha,
                                research_root=research)
    assert leg.root == "MES" and Path(leg.path) == path and leg.sha256 == sha
    assert path.name == "ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet"
    for label, booked in CLOSURE_PRINTS:
        row = leg.frame[leg.frame["ts_event"] == ts_ns(label, 16, 59)].iloc[0]
        assert row["trade_date"] == booked.isoformat() and bool(row["in_scheduled_closure"])
    assert int(leg.frame["in_scheduled_closure"].sum()) == len(CLOSURE_PRINTS)
    dates, _ = read_leg_dates("MES", tmp_path / "no_step2", MES_DAYS[1], expected_sha256=sha,
                              research_root=research)
    assert dates == tuple(MES_DAYS[1:])
    later = load_confirmation_leg("MES", tmp_path, MES_DAYS[2], expected_sha256=sha,
                                  research_root=research)  # cut at S after the whole check
    assert later.trade_dates == tuple(MES_DAYS[2:])
    got = check_confirmation_store("MES", tmp_path, expected_sha256=sha, research_root=research)
    assert got["closure_rulings"]["rows"] == 2 and got["path"] == str(path)


def test_v13_mes_a_mismatch_the_rulings_do_not_enumerate_still_refuses(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    research = tmp_path / "research"
    _path, sha = _mes_store(research, extra=[(MES_DAYS[2], MES_DAYS[2].isoformat())])
    _rulings(tmp_path, sha, monkeypatch)
    with pytest.raises(TradeDateMismatch, match="1 MES rows"):
        load_confirmation_leg("MES", tmp_path, MES_DAYS[0], expected_sha256=sha,
                              research_root=research)
    with pytest.raises(TradeDateMismatch, match="1 MES rows"):
        read_leg_dates("MES", tmp_path, MES_DAYS[0], expected_sha256=sha,
                       research_root=research)


def test_v13_mes_without_the_rulings_refuses_as_e12_did(tmp_path: Path,
                                                        monkeypatch: pytest.MonkeyPatch) -> None:
    research = tmp_path / "research"
    path, sha = _mes_store(research)
    with pytest.raises(TradeDateMismatch, match="2 MES rows"):  # read_leg without rebooking
        sb.read_leg("MES", path, sb.STEP2, expected_sha256=sha)
    with pytest.raises(ConfirmationStoreMissing, match="research root"):
        load_confirmation_leg("MES", tmp_path, MES_DAYS[0], expected_sha256=sha)


@pytest.mark.parametrize("mutate", ["wrong_sha", "other_store", "no_row", "wrong_label",
                                    "not_closure", "wrong_booking", "extra_key", "repeat"])
def test_v13_mes_rulings_that_are_not_exact_refuse(tmp_path: Path,
                                                   monkeypatch: pytest.MonkeyPatch,
                                                   mutate: str) -> None:
    research = tmp_path / "research"
    _path, sha = _mes_store(research)
    entries = [{"root": "MES", "ts_event_ns": ts_ns(label, 16, 59),
                "ct": sb._ct_str(ts_ns(label, 16, 59)), "store_label": label.isoformat(),
                "trade_date": booked.isoformat(), "ruling": "rebook_and_flag"}
               for label, booked in CLOSURE_PRINTS]
    store_sha, match = sha, "matches no row exactly"
    if mutate == "other_store":
        store_sha, match = "e" * 64, "another store"
    elif mutate == "no_row":
        entries[0] = {**entries[0], "ts_event_ns": ts_ns(MES_DAYS[3], 16, 59),
                      "ct": sb._ct_str(ts_ns(MES_DAYS[3], 16, 59))}
    elif mutate == "wrong_label":
        entries[0] = {**entries[0], "store_label": "2020-03-29"}
    elif mutate == "not_closure":  # an open-session minute is not a closure print
        entries[0] = {**entries[0], "ts_event_ns": ts_ns(MES_DAYS[0], 9, 1),
                      "ct": sb._ct_str(ts_ns(MES_DAYS[0], 9, 1)), "trade_date": "2020-03-30"}
    elif mutate == "wrong_booking":
        entries[0] = {**entries[0], "trade_date": "2020-04-02"}
    elif mutate == "extra_key":
        entries[0] = {**entries[0], "note": "x"}
        match = "exactly"
    elif mutate == "repeat":
        entries.append(dict(entries[0]))
        match = "exactly"
    _rulings(tmp_path, store_sha, monkeypatch, entries)
    if mutate == "wrong_sha":
        monkeypatch.setattr(sb, "MES_CLOSURE_RULINGS_SHA256", "f" * 64)
        match = "not the pinned"
    with pytest.raises(ClosureRulingMismatch, match=match):
        load_confirmation_leg("MES", tmp_path, MES_DAYS[0], expected_sha256=sha,
                              research_root=research)


def test_v13_the_pinned_mes_rulings_file_names_three_closure_prints_of_d1fs_store() -> None:
    """The real rulings file (no bar read): pinned sha256, D.1f's store sha256, three 16:59 CT
    prints whose CT minute, closure status and booking follow from the timestamp alone."""
    d1f = json.loads(Path("reports/stage_d1f_step5_start_rule.json").read_text("utf-8"))
    store_sha = d1f["run_inputs_sha256"]["confirmation_parquet"]["sha256"]
    rebookings, prov = sb.load_mes_closure_rulings(store_sha)
    assert prov["sha256"] == sb.MES_CLOSURE_RULINGS_SHA256 and prov["rows"] == 3
    assert [r.ct for r in rebookings] == ["2020-03-30 Mon 16:59", "2020-03-31 Tue 16:59",
                                          "2020-06-30 Tue 16:59"]
    cal = sb.load_group_calendar(sb.product("MES").group)
    ts = np.array([r.ts_event_ns for r in rebookings], dtype=np.int64)
    got = sb.assign_trade_dates(sb.open_intervals(cal, date(2020, 3, 20), date(2020, 7, 10)),
                                ts, close_minute_to_previous=True)
    assert got.in_closure.all() and not got.boundary.any()
    assert [d.isoformat() for d in got.as_dates()] == [r.trade_date for r in rebookings]
    assert all(sb._ct_str(r.ts_event_ns) == r.ct for r in rebookings)
