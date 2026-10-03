"""ml_route_v2.signals.k9: K9-anncday-01's EC-K9 announcement-day flag (V23 item 8; design V2.3).

The training-window file (reports/stage_e12_ec_k9_2019_2024.json) is written by the E.12 calendar
builder in parallel; these tests use fixture files in its schema ("ec_k9/1"), and one test, skipped
while the real file is absent, runs assert_causal on the real file over a synthetic row set.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from ml_route_v2.clock import decision_rows
from ml_route_v2.signals import REGISTRY, SignalContext, compute_signals
from ml_route_v2.signals import k9 as k9mod
from ml_route_v2.signals.k9 import K9CalendarError, K9CalendarMissing

CT = ZoneInfo("America/Chicago")
EVENTS = {"FOMC": ["2021-09-22"], "NFP": ["2021-10-08"], "GDP_first_last": ["2021-09-30"],
          "ISM_manufacturing_scheduled": ["2021-10-01"],
          "inflation_earlier_of_CPI_PPI_by_reference_month": ["2021-10-13", "2021-09-22"]}


def write_calendar(tmp: Path, *, events: dict | None = None, date_set: list | None = None,
                   uncovered: list | None = None, schema: str = "ec_k9/1",
                   window: tuple = ("2019-05-01", "2024-02-29")) -> Path:
    ev = EVENTS if events is None else events
    ds = sorted(set().union(*map(set, ev.values()))) if date_set is None else date_set
    raw = {"schema": schema, "window": list(window), "event_dates": ev, "date_set": ds,
           "uncovered_spans": [["2021-10-04", "2021-10-06"]] if uncovered is None else uncovered,
           "sources": ["fixture"]}
    path = tmp / "ec_k9_fixture.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return path


def weekdays(first: date, last: date) -> list[date]:
    n = (last - first).days + 1
    return [first + timedelta(i) for i in range(n) if (first + timedelta(i)).weekday() < 5]


def context(days: list[date], roots: tuple[str, ...] = ("MNQ", "MGC", "MYM", "M2K")
            ) -> SignalContext:
    rows = decision_rows(roots, {r: days for r in roots})
    return SignalContext(rows, {}, None, pd.Series(np.nan, index=rows.index))


def flag_frame(ctx: SignalContext) -> pd.DataFrame:
    """compute_signals (assert_causal runs inside) for k9_anncday, with the rows beside it."""
    out = compute_signals(ctx, ["k9_anncday"])
    return pd.concat([ctx.rows[["root", "trade_date", "decision_ts_ns"]], out], axis=1)


def evening_before(day: date) -> int:
    return int(pd.Timestamp(datetime.combine(day - timedelta(1), time(17, 59)), tz=CT).value)


def test_spec_and_the_catalog_agree_with_the_module_literals() -> None:
    spec = REGISTRY["k9_anncday"]
    assert (spec.family, spec.cluster, spec.kind, spec.normalize) == (
        "K9-anncday-01", "K9", "flag", False)
    raw = json.loads(k9mod.CATALOG_PATH.read_text(encoding="utf-8"))
    member = raw["members"][0]
    assert member["id"] == k9mod.FAMILY
    assert sorted(member["vehicles"].values()) == sorted(k9mod.VEHICLES)
    assert "17:59 CT" in member["decision_time_ct"]
    union = set().union(*(set(member["event_dates"][k]) for k in k9mod.EVENT_KEYS))
    research = k9mod.research_dates()
    assert len(research.dates) == len(union) == 60
    assert (research.first, research.last) == (date(2025, 4, 1).toordinal() - 719163,
                                               date(2026, 6, 19).toordinal() - 719163)


def test_values_applicability_and_availability_on_the_training_window(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(k9mod, "TRAIN_CALENDAR_PATH", write_calendar(tmp_path))
    days = weekdays(date(2021, 9, 20), date(2021, 10, 15))
    f = flag_frame(context(days))
    day = pd.to_datetime(f["trade_date"]).dt.date
    k9_rows = f["root"].isin(("MNQ", "M2K", "MYM")).to_numpy()
    uncovered = day.isin([date(2021, 10, 4), date(2021, 10, 5), date(2021, 10, 6)]).to_numpy()
    events = day.isin([date.fromisoformat(d) for d in
                       sorted(set().union(*map(set, EVENTS.values())))]).to_numpy()
    app = f["app_k9_anncday"].to_numpy() > 0
    raw = f["raw_k9_anncday"].to_numpy()
    assert (app == (k9_rows & ~uncovered)).all()
    assert (raw[app] == events[app].astype(float)).all()
    assert (raw[~app] == 0.0).all()
    assert raw[app].sum() > 0 and (raw[app] == 0).sum() > 0
    want_avail = np.array([evening_before(d) for d in day])
    assert (f["avail_k9_anncday"].to_numpy()[app] == want_avail[app]).all()
    assert (f["avail_k9_anncday"].to_numpy()[app] < f["decision_ts_ns"].to_numpy()[app]).all()
    # MGC (no K9 vehicle): not applicable, avail = t
    mgc = (f["root"] == "MGC").to_numpy()
    assert (f["avail_k9_anncday"].to_numpy()[mgc] == f["decision_ts_ns"].to_numpy()[mgc]).all()


def test_research_window_uses_the_catalog_and_other_dates_are_not_covered(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(k9mod, "TRAIN_CALENDAR_PATH", write_calendar(tmp_path))
    days = [date(2024, 3, 4), date(2024, 6, 3), date(2025, 3, 31), date(2025, 5, 6),
            date(2025, 5, 7)]
    f = flag_frame(context(days, ("MNQ",)))
    by_day = f.groupby(pd.to_datetime(f["trade_date"]).dt.date)
    app = by_day["app_k9_anncday"].max().to_dict()
    raw = by_day["raw_k9_anncday"].max().to_dict()
    # 2024-03 (embargo) and 2024-06 / 2025-03-31 (holdout-2): no date set covers them
    assert app == {date(2024, 3, 4): 0.0, date(2024, 6, 3): 0.0, date(2025, 3, 31): 0.0,
                   date(2025, 5, 6): 1.0, date(2025, 5, 7): 1.0}
    assert raw[date(2025, 5, 7)] == 1.0 and raw[date(2025, 5, 6)] == 0.0  # FOMC 2025-05-07


@pytest.mark.parametrize("change,match", [
    ({"date_set": ["2021-09-22", "2021-09-30", "2021-10-01", "2021-10-08"]}, "union"),
    ({"date_set": ["2021-09-22", "2021-09-30", "2021-10-01", "2021-10-08", "2021-10-13",
                   "2021-10-20"]}, "union"),
    ({"date_set": ["2021-09-30", "2021-09-22", "2021-10-01", "2021-10-08", "2021-10-13"]},
     "sorted"),
    ({"schema": "ec_k9/0"}, "schema"),
    ({"window": ("2019-05-06", "2024-02-29")}, "window"),
    ({"uncovered": [["2021-10-06", "2021-10-04"]]}, "uncovered span"),
    ({"uncovered": [["2021-10-04"]]}, "uncovered span"),
    ({"events": {k: v for k, v in EVENTS.items() if k != "NFP"}}, "lacks"),
    ({"events": {**EVENTS, "FOMC": ["2025-05-07"]}, "date_set": [
        "2021-09-22", "2021-09-30", "2021-10-01", "2021-10-08", "2021-10-13", "2025-05-07"]},
     "outside the window"),
])
def test_a_bad_training_file_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
                                    change: dict, match: str) -> None:
    monkeypatch.setattr(k9mod, "TRAIN_CALENDAR_PATH", write_calendar(tmp_path, **change))
    with pytest.raises(K9CalendarError, match=match):
        flag_frame(context(weekdays(date(2021, 9, 20), date(2021, 9, 24)), ("MNQ",)))


def test_an_absent_training_file_warns_and_leaves_the_training_window_not_applicable(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(k9mod, "TRAIN_CALENDAR_PATH", tmp_path / "absent.json")
    assert not k9mod.training_calendar_present()
    with pytest.warns(K9CalendarMissing):
        f = flag_frame(context([date(2021, 9, 22), date(2025, 5, 7)], ("MNQ",)))
    day = pd.to_datetime(f["trade_date"]).dt.date
    assert (f.loc[(day == date(2021, 9, 22)).to_numpy(), "app_k9_anncday"] == 0).all()
    assert (f.loc[(day == date(2025, 5, 7)).to_numpy(), "raw_k9_anncday"] == 1).all()


def test_no_warning_when_no_k9_row_lies_in_the_training_window(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch, recwarn: pytest.WarningsRecorder) -> None:
    monkeypatch.setattr(k9mod, "TRAIN_CALENDAR_PATH", tmp_path / "absent.json")
    flag_frame(context([date(2021, 9, 22)], ("MGC",)))
    flag_frame(context([date(2025, 5, 7)], ("MNQ",)))
    assert not [w for w in recwarn if issubclass(w.category, K9CalendarMissing)]


@pytest.mark.skipif(not k9mod.TRAIN_CALENDAR_PATH.exists(),
                    reason="reports/stage_e12_ec_k9_2019_2024.json not written yet")
def test_the_real_training_file_is_causal_over_the_training_window() -> None:
    real = k9mod.training_dates()
    assert real is not None and len(real.dates) > 0
    days = weekdays(date(2019, 5, 6), date(2024, 2, 29))
    f = flag_frame(context(days, k9mod.VEHICLES))  # assert_causal runs inside compute_signals
    app = f["app_k9_anncday"].to_numpy() > 0
    assert app.sum() > 0 and f["raw_k9_anncday"].to_numpy()[app].sum() > 0
