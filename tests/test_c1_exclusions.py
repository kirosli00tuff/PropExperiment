"""Ruling C12 for test C1 (c1_replication.exclusions) on SYNTHETIC calendars: candidates, each
exclusion reason, the share and the 2% stop. Calendars only, no bar.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from c1_replication.exclusions import REASONS, c12_exclusions
from data.hist_calendar import parse_hist_calendar
from tests._c1_fixtures import GROUPS, calendar_payload

FIRST, LAST = date(2011, 1, 3), date(2011, 3, 31)


def _cals(tmp: Path, unsourced: dict | None = None, entries: dict | None = None) -> dict:
    out = {}
    for g in GROUPS:
        listed = [(d, "SYNTHETIC") for d in (unsourced or {}).get(g, [])]
        payload = calendar_payload(g, entries=(entries or {}).get(g), unsourced=listed)
        p = tmp / f"{g}.json"
        p.write_text(json.dumps(payload))
        out[g] = parse_hist_calendar(p.read_bytes(), g, p)
    return out


def test_clean_calendars_exclude_nothing(tmp_path):
    r = c12_exclusions(_cals(tmp_path), (), first=FIRST, last=LAST)
    span = range((LAST - FIRST).days + 1)
    weekdays = sum((FIRST + timedelta(days=i)).weekday() < 5 for i in span)
    assert r.n_candidates == weekdays and r.share == 0.0 and not r.stops
    assert r.excluded_dates() == frozenset()


def test_each_reason(tmp_path):
    cals = _cals(tmp_path, unsourced={"energy": ["2011-02-09"], "equity": ["2011-02-14"],
                                      "grains": ["2011-03-01"], "fx": ["2011-03-02"]})
    r = c12_exclusions(cals, (date(2011, 3, 10),), first=FIRST, last=LAST)
    assert r.excluded[date(2011, 2, 9)] == ("energy_unsourced",)
    assert r.excluded[date(2011, 2, 10)] == ("energy_prior_unsourced",)
    assert r.excluded[date(2011, 2, 14)] == ("equity_unsourced",)
    assert r.excluded[date(2011, 3, 1)] == ("grains_unsourced",)
    assert r.excluded[date(2011, 3, 2)] == ("fx_unsourced",)
    assert r.excluded[date(2011, 3, 10)] == ("release_unsourced",)
    assert len(r.excluded) == 6
    rec = r.record()
    assert set(rec["by_reason"]) == set(REASONS) and rec["by_reason"]["energy_unsourced"] == 1


def test_a_prior_unsourced_weekday_across_a_weekend_excludes_monday(tmp_path):
    cals = _cals(tmp_path, unsourced={"energy": ["2011-02-04"]})  # a Friday
    r = c12_exclusions(cals, (), first=FIRST, last=LAST)
    assert r.excluded[date(2011, 2, 7)] == ("energy_prior_unsourced",)


def test_sourced_closures_are_not_candidates_unsourced_ones_are(tmp_path):
    entries = {"energy": [("2011-02-21", "x", "full_closure", None, "cme"),
                          ("2011-03-07", "x", "full_closure", None, "unverified")]}
    r = c12_exclusions(_cals(tmp_path, entries=entries), (), first=FIRST, last=LAST)
    assert date(2011, 2, 21) not in r.candidates
    assert date(2011, 3, 7) in r.candidates
    assert "energy_unsourced" in r.excluded[date(2011, 3, 7)]
    assert r.excluded[date(2011, 3, 8)] == ("energy_prior_unsourced",)


def test_share_above_two_percent_stops(tmp_path):
    cals = _cals(tmp_path, unsourced={"metals": ["2011-01-04"]})
    r = c12_exclusions(cals, (), first=FIRST, last=LAST)
    assert r.share == 1 / r.n_candidates and not r.stops
    days = [d.isoformat() for d in (FIRST + timedelta(days=i) for i in range(20))
            if d.weekday() < 5][:3]
    r2 = c12_exclusions(_cals(tmp_path, unsourced={"rates": days}), (), first=FIRST, last=LAST)
    assert r2.share == 3 / r2.n_candidates > 0.02 and r2.stops
