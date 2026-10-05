"""Test C1's table builders (c1_replication.tables) on SYNTHETIC calendar files: NG's D8 release
calendar, the K4 NGS table with ruling C13's drops, the unsourced release dates, the energy full
sessions (recomputed and compared), and the Topstep rows by Rule H-1.
"""

from __future__ import annotations

import json
from datetime import date, time
from pathlib import Path

import pytest

from c1_replication import tables as tb
from data.hist_calendar import parse_hist_calendar
from tests._c1_fixtures import calendar_payload, release_payload, sha


def _parse(doc: dict, tmp: Path) -> tb.HistReleases:
    p = tmp / "rel.json"
    p.write_text(json.dumps(doc))
    return tb.load_releases(p, sha(p))


def test_d8_calendar_ngs_table_drops_and_unsourced(tmp_path):
    doc = release_payload(unverified=["2012-03-08"], drops=["2012-03-15"],
                          unsourced=["2013-01-03"])
    rel = _parse(doc, tmp_path)
    d8 = [r for r in doc["releases"] if r["release"] in ("NGS", "WPSR", "FOMC")]
    assert len(rel.calendar.by_root["NG"]) == len({r["instant_utc"] for r in d8})
    assert rel.calendar.first == date(2010, 6, 1) and rel.calendar.last == date(2019, 5, 31)
    ngs = dict(rel.ngs_table)
    assert ngs["2012-03-08"] == "09:30"  # 10:30 ET is 09:30 CT (K4-L-02)
    assert "2012-03-15" not in ngs and rel.ngs_dropped == ("2012-03-15",)
    assert set(rel.unsourced) == {date(2012, 3, 8), date(2013, 1, 3)}
    assert rel.counts["ngs_dropped_c13"] == 1
    assert "NFP" not in rel.counts["d8_rows_by_release"]


@pytest.mark.parametrize(("edit", "match"), [
    (lambda d: d.update(schema="x"), "schema"),
    (lambda d: d["releases"][0].update(instant_utc="2010-06-02T14:30:30Z"), "minute"),
    (lambda d: d["releases"][0].update(instant_utc="2010-06-02T14:30:00"), "timezone"),
    (lambda d: d["releases"][0].update(date="2010-06-04"), "is not on"),
    (lambda d: d["releases"][0].update(evidence="verified"), "evidence"),
    (lambda d: d["releases"][0].update(drop_actual_differs="yes"), "true or false"),
    (lambda d: d["releases"][0].pop("drop_actual_differs"), "every NGS row"),
    (lambda d: d["releases"].append(dict(d["releases"][0])), "two NGS rows"),
    (lambda d: d.update(coverage={"first": "2011-01-01", "last": "2019-05-31"}), "outside"),
])
def test_release_file_refusals(tmp_path, edit, match):
    doc = release_payload()
    first_ngs = next(i for i, r in enumerate(doc["releases"]) if r["release"] == "NGS")
    doc["releases"].insert(0, doc["releases"].pop(first_ngs))
    edit(doc)
    with pytest.raises(tb.TableError, match=match):
        _parse(doc, tmp_path)


def _untimed(doc: dict, kind: str) -> dict:
    """The first row of ``kind`` with its time set to null (as the real WPSR-2012-11-01)."""
    row = next(r for r in doc["releases"] if r["release"] == kind)
    row.update(time_local=None, instant_utc=None, time_evidence="unverified")
    return row


def test_a_null_time_row_listed_by_id_is_accepted_as_an_unsourced_date(tmp_path):
    full = _parse(release_payload(), tmp_path)
    doc = release_payload()
    row = _untimed(doc, "WPSR")
    ngs = _untimed(doc, "NGS")
    doc["unsourced"] = [{"id": row["id"], "what": "time", "reason": "SYNTHETIC: no time"},
                        {"id": ngs["id"], "what": "time", "reason": "SYNTHETIC: no time"}]
    rel = _parse(doc, tmp_path)
    day, ngs_day = date.fromisoformat(row["date"]), date.fromisoformat(ngs["date"])
    assert set(rel.unsourced) == {day, ngs_day}
    assert "unsourced (time)" in rel.unsourced[day][0]
    assert len(rel.calendar.by_root["NG"]) == len(full.calendar.by_root["NG"]) - 2
    assert ngs["date"] not in dict(rel.ngs_table) and ngs["date"] not in rel.ngs_dropped
    assert rel.counts["untimed_rows_listed"] == 2 and rel.counts["ngs_untimed_listed"] == 1
    assert rel.counts["d8_rows"] == full.counts["d8_rows"]


def test_a_null_time_row_not_listed_is_refused(tmp_path):
    doc = release_payload()
    row = _untimed(doc, "WPSR")
    with pytest.raises(tb.TableError, match="no instant_utc"):
        _parse(doc, tmp_path)
    doc["unsourced"] = [{"id": "WPSR-1999-01-06", "what": "time", "reason": "other id"}]
    with pytest.raises(tb.TableError, match="no instant_utc"):
        _parse(doc, tmp_path)
    doc["unsourced"] = [{"id": row["id"], "what": "time", "reason": "listed"}]
    row["time_local"] = "10:30"  # a time without an instant is still refused
    with pytest.raises(tb.TableError, match="no instant_utc"):
        _parse(doc, tmp_path)


def test_an_unsourced_row_naming_no_release_row_is_refused(tmp_path):
    doc = release_payload()
    doc["unsourced"] = [{"id": "WPSR-1999-01-06", "what": "time", "reason": "x"}]
    with pytest.raises(tb.TableError, match="no release row has"):
        _parse(doc, tmp_path)
    doc["unsourced"] = [{"what": "time", "reason": "x"}]
    with pytest.raises(tb.TableError, match="neither a date nor a release id"):
        _parse(doc, tmp_path)


def test_a_wrong_sha256_is_refused(tmp_path):
    p = tmp_path / "rel.json"
    p.write_text(json.dumps(release_payload()))
    with pytest.raises(tb.TableError, match="sha256"):
        tb.load_releases(p, "0" * 64)
    with pytest.raises(tb.TableError, match="does not exist"):
        tb.load_releases(tmp_path / "none.json", "0" * 64)


def _energy(tmp: Path, payload: dict | None = None):
    p = tmp / "energy.json"
    p.write_text(json.dumps(payload or calendar_payload("energy")))
    return parse_hist_calendar(p.read_bytes(), "energy", p)


def _full_doc(energy, days=None, **extra) -> dict:
    rng = (date(2010, 6, 1), date(2019, 5, 31))
    listed = list(days if days is not None else tb.full_sessions_rule(energy, *rng))
    return {"range": {"first": "2010-06-01", "last": "2019-05-31"},
            "source_sha256": energy.file_sha256, "ENERGY_FULL_SESSIONS": listed, **extra}


def test_full_sessions_must_equal_the_rule_on_the_pinned_energy_calendar(tmp_path):
    energy = _energy(tmp_path)
    good = _full_doc(energy)
    days = tb.parse_full_sessions(json.dumps(good).encode(), tmp_path / "f.json", energy)
    assert "2010-11-26" not in days and "2010-07-05" not in days  # halt, closure
    assert "2010-11-29" in days and len(days) == len(good["ENERGY_FULL_SESSIONS"])
    short = _full_doc(energy, good["ENERGY_FULL_SESSIONS"][1:])
    with pytest.raises(tb.TableError, match="differ from the rule"):
        tb.parse_full_sessions(json.dumps(short).encode(), tmp_path / "f.json", energy)
    other = {**good, "source_sha256": "1" * 64}
    with pytest.raises(tb.TableError, match="derived from"):
        tb.parse_full_sessions(json.dumps(other).encode(), tmp_path / "f.json", energy)
    unsorted = _full_doc(energy, list(reversed(good["ENERGY_FULL_SESSIONS"])))
    with pytest.raises(tb.TableError, match="sorted"):
        tb.parse_full_sessions(json.dumps(unsorted).encode(), tmp_path / "f.json", energy)


def test_rule_h1_rows_from_the_equity_calendar(tmp_path):
    from rules.sessions import TOPSTEP_HOLIDAYS

    entries = [("2010-07-05", "x", "full_closure", None, "cme"),
               ("2010-11-26", "x", "early_halt", "12:15", "cme"),
               ("2012-07-03", "x", "early_halt", "12:00", "cme"),
               ("2016-03-25", "x", "full_closure", None, "unverified"),
               ("2019-05-27", "x", "early_halt", "12:00", "cme")]
    p = tmp_path / "equity.json"
    p.write_text(json.dumps(calendar_payload("equity", entries=entries)))
    equity = parse_hist_calendar(p.read_bytes(), "equity", p)
    rows = tb.h1_rows(equity)
    assert rows[date(2010, 7, 5)].close_by_ct is None
    assert rows[date(2010, 11, 26)].close_by_ct == time(11, 45)
    assert date(2012, 7, 3) not in rows  # every July 3 is unsettled
    assert date(2019, 5, 27) not in rows  # E.5's derived rows begin 2019-05-01
    assert rows[date(2016, 3, 25)].close_by_ct is None  # derived; the date itself is unsourced
    assert not set(rows) & set(TOPSTEP_HOLIDAYS)
    assert tb.h1_unsettled(equity) == (date(2012, 7, 3),)
