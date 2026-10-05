"""Test C1's table context (c1_replication.context.hist_tables): inside it the frozen code reads
the replication's 2010-2019 tables; on exit every patched name is the original object again, the
calendar caches are empty, and no frozen file changed (byte-identical; the v2 freeze still
verifies). SYNTHETIC calendars only (tests/_c1_fixtures.py).
"""

from __future__ import annotations

import hashlib
import importlib
from datetime import date, time
from pathlib import Path

import pytest

from c1_replication import context as cx
from c1_replication.constants import V2_FREEZE_MANIFEST, V2_FREEZE_SHA256
from c1_replication.evaluate import load_calendars
from c1_replication.guards import verify_v2
from tests._c1_fixtures import write_inputs

E12_CONSTANTS_SHA256 = "e107d7feb5e4fc4d6933bb3c9d33677149feb8f891613817f1f3b3b8317b9ef4"
E12_CONSTANTS_FINGERPRINT = "013fa5a4e4ab40b36a45085ce07fae9c59a298d431615c12a0121975c557d0c4"


@pytest.fixture(scope="module")
def tables(tmp_path_factory):
    inp = write_inputs(tmp_path_factory.mktemp("c1_ctx"))
    return load_calendars(inp.hashes, date(2010, 6, 7), date(2019, 4, 30))


def _module_files() -> dict[str, str]:
    names = {m for m, _ in cx.PATCHES} | set(cx.CACHE_MODULES) | {"ml_route_v2.constants"}
    out = {}
    for n in sorted(names):
        f = Path(importlib.import_module(n).__file__)
        out[n] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


def test_inside_the_frozen_code_reads_the_hist_tables(tables):
    from data import group_session
    from ml_route import inputs
    from ml_route_v2.clock import decision_rows, minutes_after_midnight_ct
    from rules import sessions
    from strategy.members.k4 import ngpre, ovr

    t = tables["tables"]
    with cx.hist_tables(t):
        assert group_session.load_group_calendar("energy") is t.calendars["energy"]
        assert inputs._group_calendar("metals") is t.calendars["metals"]
        assert sessions.default_holidays()["equity"] == dict(t.calendars["equity"].holidays)
        # 2010-11-26: energy halts 12:45 (- 15 min = 12:30), equity 12:15 -> Rule H-1 close-by
        # 11:45 (30 min lead): F = 11:45, and the date has no decision row (early halt)
        assert sessions.TOPSTEP_HOLIDAYS[date(2010, 11, 26)].close_by_ct == time(11, 45)
        assert sessions.flatten_time_ct("NG", date(2010, 11, 26)) == time(11, 45)
        assert sessions.flatten_time_ct("NG", date(2010, 7, 5)) is None
        rows = decision_rows(("NG",), {"NG": [date(2010, 11, 26), date(2010, 11, 29)]})
        assert set(rows["trade_date"].dt.date) == {date(2010, 11, 29)}
        mins = sorted(minutes_after_midnight_ct(rows["decision_ts_ns"].to_numpy()).tolist())
        assert mins == [8 * 60 + 30, 10 * 60 + 30, 13 * 60]
        ngs = ngpre.make_ng().ngs
        assert ngs == t.ngs_table and ngpre.schedule(ngs)
        assert min(ngpre.schedule(ngs)) >= date(2010, 6, 1)
        refs = ovr.reference_dates(date(2011, 3, 1))
        assert len(refs) == ovr.REFERENCE_DATES
        assert {d.isoformat() for d in refs} <= set(t.full_sessions)
        assert sessions.TOPSTEP_EARLY_CLOSE_LEAD[2012].total_seconds() == 1800


def test_every_patched_name_is_restored_and_no_frozen_file_changes(tables):
    before_files = _module_files()
    before = cx.originals()
    with cx.hist_tables(tables["tables"]) as values:
        inside = cx.originals()
        assert all(inside[k] is values[k] for k in cx.PATCHES)
        assert all(inside[k] is not before[k] for k in cx.PATCHES)
    after = cx.originals()
    assert all(after[k] is before[k] for k in cx.PATCHES)
    assert _module_files() == before_files
    assert before_files["ml_route_v2.constants"] == E12_CONSTANTS_SHA256
    from ml_route_v2.fingerprint import constants_fingerprint

    assert constants_fingerprint() == E12_CONSTANTS_FINGERPRINT
    assert verify_v2(V2_FREEZE_MANIFEST, V2_FREEZE_SHA256)["files"] > 0
    assert not cx.is_active()


def test_restored_after_an_exception_and_nesting_refused(tables):
    before = cx.originals()
    with pytest.raises(RuntimeError, match="boom"), cx.hist_tables(tables["tables"]):
        with pytest.raises(cx.ContextError, match="already active"), \
                cx.hist_tables(tables["tables"]):
            pass
        raise RuntimeError("boom")
    after = cx.originals()
    assert all(after[k] is before[k] for k in cx.PATCHES) and not cx.is_active()


def test_a_group_without_a_hist_calendar_raises_inside(tables):
    from data import group_session
    from data.hist_calendar import HistCalendarError

    with cx.hist_tables(tables["tables"]), pytest.raises(HistCalendarError, match="crypto"):
        group_session.load_group_calendar("crypto")


def test_calendar_caches_are_cleared_on_entry_and_exit(tables):
    from ml_route_v2 import clock
    from ml_route_v2.signals import generic

    clock._day_times("NG", date(2021, 3, 3))  # a frozen-calendar value cached before
    assert clock._day_times.cache_info().currsize > 0
    with cx.hist_tables(tables["tables"]):
        assert clock._day_times.cache_info().currsize == 0
        clock._day_times("NG", date(2012, 3, 7))
        generic._previous_trade_day("NG", 15400)
        assert clock._day_times.cache_info().currsize == 1
    assert clock._day_times.cache_info().currsize == 0
    assert generic._previous_trade_day.cache_info().currsize == 0
    assert "ml_route_v2.clock._day_times" in cx.clear_caches()


def test_tables_must_name_all_six_groups(tables):
    cals = dict(tables["calendars"])
    cals.pop("grains")
    with pytest.raises(cx.ContextError, match="grains"):
        cx.HistTables(cals, {}, (), ())


def test_h1_rows_overlapping_the_frozen_rows_are_refused(tables):
    from rules.sessions import TOPSTEP_HOLIDAYS

    t = tables["tables"]
    day = sorted(TOPSTEP_HOLIDAYS)[0]
    bad = cx.HistTables(t.calendars, {**t.topstep_rows, day: TOPSTEP_HOLIDAYS[day]},
                        t.ngs_table, t.full_sessions)
    with pytest.raises(cx.ContextError, match="overlap"), cx.hist_tables(bad):
        pass
    assert not cx.is_active()
