"""Stage D.1f list 5.7: the 2019-2024 release table and the declared E-H1/E-H2 amendment.

The table is checked against reports/stage_d1f_release_sources.json (the verified
extraction) entry by entry, and against a hand spot-check. The amendment is checked three
ways: undoing it textually gives back the pre-amendment sha256 of list section 0 (nothing
else changed); the table argument is actually read (synthetic bars); and both modules
reproduce reports/stage_d1d_accounting.json on the train union to the cent under the
no-argument factory and the combined-table factory (list 2.1 A1, NEW-1). The two train-union
screens are the only real-data runs here (sanctioned by the stage prompt).
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

import strategy.research.e_calendar_event._release_table_2019_2024 as rt
from data.research_bars import RESEARCH_SERIES_PATH
from strategy.interface import Bar, construct_bar
from strategy.research.e_calendar_event._release_table_2019_2024 import (
    CPI,
    DROPPED_RELEASES,
    FOMC,
    NFP,
    RELEASE_TABLE_2019_2024,
    SOURCES,
    ReleaseSource,
)
from strategy.research.e_calendar_event.h1_scheduled_macro_drift import (
    RELEASE_TABLE_ET,
    H1ScheduledMacroDrift,
)
from strategy.research.e_calendar_event.h2_post_release_momentum import H2PostReleaseMomentum

ET = ZoneInfo("America/New_York")
CT = ZoneInfo("America/Chicago")
EXTRACTION = Path("reports/stage_d1f_release_sources.json")
H1_PATH = Path("strategy/research/e_calendar_event/h1_scheduled_macro_drift.py")
H2_PATH = Path("strategy/research/e_calendar_event/h2_post_release_momentum.py")
H1_OLD_SHA = "94e92ff15efe2160c5e967da6d1a415385681a43cf500505004b87b363ab25b2"
H2_OLD_SHA = "b2f09ab6e71dafe554c8db35c04a02f3476cb25e0f3783ca740ebffc19b5f005"
COMBINED = RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024
needs_research = pytest.mark.skipif(not RESEARCH_SERIES_PATH.exists(),
                                    reason="research parquet not present")


def _kind_counts() -> dict[str, int]:
    kinds = [s.kind for s in SOURCES.values()]
    return {k: kinds.count(k) for k in (FOMC, CPI, NFP)}


# ------------------------------------------------------------------------ the table ----
def test_counts_range_and_no_duplicates() -> None:
    assert _kind_counts() == {FOMC: 35, CPI: 58, NFP: 58}
    assert len(RELEASE_TABLE_2019_2024) == 151 == len(set(RELEASE_TABLE_2019_2024))
    assert min(RELEASE_TABLE_2019_2024) == date(2019, 5, 1)
    assert max(RELEASE_TABLE_2019_2024) <= date(2024, 2, 29)
    assert type(RELEASE_TABLE_2019_2024) is dict


def test_extraction_counts_37_fomc_58_cpi_58_nfp() -> None:
    releases = json.loads(EXTRACTION.read_text())["releases"]
    kinds = [r["kind"] for r in releases]
    assert (len(releases), kinds.count(FOMC), kinds.count(CPI), kinds.count(NFP)) == (
        153, 37, 58, 58)


def test_times_are_et_and_by_kind() -> None:
    for day, at in RELEASE_TABLE_2019_2024.items():
        assert at.tzinfo is not None and at.tzinfo.key == "America/New_York", day
        assert at.date() == day
        want = time(14, 0) if SOURCES[day].kind == FOMC else time(8, 30)
        assert at.timetz().replace(tzinfo=None) == want, day
        assert at.utcoffset() in (timedelta(hours=-4), timedelta(hours=-5)), day
        assert at == SOURCES[day].release_et


def test_every_extraction_record_is_kept_or_ruled_out_verbatim() -> None:
    releases = json.loads(EXTRACTION.read_text())["releases"]
    dropped = {(s.release_date, s.kind): s for s in DROPPED_RELEASES}
    for r in releases:
        key = (date.fromisoformat(r["date"]), r["kind"])
        src = dropped.get(key) or SOURCES[key[0]]
        assert (src.release_date, src.kind) == key, r
        assert (src.url, src.quote, src.note) == (r["source_url"], r["quote"], r["note"]), r
    assert len(SOURCES) + len(DROPPED_RELEASES) == len(releases)


def test_every_entry_has_a_source_whose_quote_names_its_date() -> None:
    assert set(SOURCES) == set(RELEASE_TABLE_2019_2024)
    for day, src in SOURCES.items():
        assert src.quote and "[unverified]" not in src.quote, day
        if src.kind == FOMC:
            assert src.url.startswith("https://www.federalreserve.gov/monetarypolicy/fomc")
            assert f"monetary{day:%Y%m%d}a.htm" in src.quote, day
            continue
        name = "Consumer Price Index" if src.kind == CPI else "Employment Situation"
        assert src.url.startswith("https://www.bls.gov/schedule/") and name in src.quote
        assert "08:30 AM" in src.quote, day
        if day.year == 2024:  # month-view calendar cells
            assert src.url.endswith(f"/2024/{day:%m}_sched.htm")
            assert src.quote.startswith(f"{day.day}<br>"), day
        else:
            assert src.url.endswith(f"/{day.year}/home.htm")
            spelled = {f"{day:%A}, {day:%B} {d}, {day.year}" for d in (f"{day:%d}", day.day)}
            assert any(x in src.quote for x in spelled), day


@pytest.mark.parametrize(("day", "kind"), [
    (date(2019, 5, 1), FOMC), (date(2020, 3, 11), CPI), (date(2020, 7, 2), NFP),
    (date(2020, 11, 5), FOMC), (date(2021, 6, 10), CPI), (date(2022, 3, 16), FOMC),
    (date(2022, 6, 10), CPI), (date(2022, 7, 8), NFP), (date(2023, 2, 14), CPI),
    (date(2023, 3, 10), NFP), (date(2024, 1, 31), FOMC), (date(2024, 2, 13), CPI),
])
def test_spot_checks(day: date, kind: str) -> None:
    assert SOURCES[day].kind == kind
    hour, minute = (14, 0) if kind == FOMC else (8, 30)
    assert RELEASE_TABLE_2019_2024[day] == datetime(day.year, day.month, day.day, hour, minute,
                                                    tzinfo=ET)


def test_unscheduled_and_cancelled_fomc_actions_are_absent() -> None:
    for day in (date(2019, 10, 4), date(2019, 10, 11), date(2020, 3, 3), date(2020, 3, 15),
                date(2020, 3, 16), date(2020, 3, 18), date(2020, 3, 19), date(2020, 3, 23),
                date(2020, 3, 31), date(2020, 8, 27)):
        assert day not in RELEASE_TABLE_2019_2024 or SOURCES[day].kind != FOMC, day


def test_the_two_collisions_keep_the_earliest_release_as_ruled() -> None:
    for day in (date(2019, 12, 11), date(2020, 6, 10)):
        assert SOURCES[day].kind == CPI
        assert RELEASE_TABLE_2019_2024[day] == datetime.combine(day, time(8, 30), tzinfo=ET)
    assert [(s.release_date, s.kind) for s in DROPPED_RELEASES] == [
        (date(2019, 12, 11), FOMC), (date(2020, 6, 10), FOMC)]
    ruled = rt.RULED_COLLISIONS
    assert ruled == {date(2019, 12, 11): CPI, date(2020, 6, 10): CPI}


def _src(day: date, kind: str) -> ReleaseSource:
    return ReleaseSource(day, kind, "https://example.invalid", "quote")


def test_builder_refuses_duplicates_other_than_the_ruled_ones() -> None:
    ruled = (_src(date(2019, 12, 11), FOMC), _src(date(2019, 12, 11), CPI),
             _src(date(2020, 6, 10), CPI), _src(date(2020, 6, 10), FOMC))
    table, sources, dropped = rt._build_release_table(ruled)
    assert {d: s.kind for d, s in sources.items()} == {date(2019, 12, 11): CPI,
                                                       date(2020, 6, 10): CPI}
    assert [s.kind for s in dropped] == [FOMC, FOMC] and len(table) == 2
    with pytest.raises(ValueError, match="duplicate release date"):
        rt._build_release_table((*ruled, _src(date(2021, 1, 13), CPI),
                                 _src(date(2021, 1, 13), NFP)))
    with pytest.raises(ValueError, match="does not resolve as ruled"):
        rt._build_release_table((*ruled[2:], _src(date(2019, 12, 11), CPI),
                                 _src(date(2019, 12, 11), CPI)))
    with pytest.raises(ValueError, match="ruled collisions not found"):
        rt._build_release_table(ruled[:2])
    with pytest.raises(ValueError, match="outside"):
        rt._build_release_table((*ruled, _src(date(2024, 3, 1), CPI)))


def test_no_key_overlaps_the_hashed_table_and_the_union_is_a_plain_dict() -> None:
    assert not set(RELEASE_TABLE_ET) & set(RELEASE_TABLE_2019_2024)
    assert type(COMBINED) is dict and len(COMBINED) == len(RELEASE_TABLE_ET) + 151
    assert all(COMBINED[d] == RELEASE_TABLE_ET[d] for d in RELEASE_TABLE_ET)


# -------------------------------------------------------------------- the amendment ----
H1_AMENDMENT = (
    ("    release_table: dict[date, datetime] = field(\n"
     "        default_factory=lambda: RELEASE_TABLE_ET, repr=False, compare=False)\n", ""),
    ("self.release_table.get(bar.trade_date)", "RELEASE_TABLE_ET.get(bar.trade_date)"),
)
H2_AMENDMENT = (
    ("    release_table: dict = field(\n"
     "        default_factory=lambda: RELEASE_TABLE_ET, repr=False, compare=False)\n", ""),
    ("self.release_table.get(bar.trade_date)", "RELEASE_TABLE_ET.get(bar.trade_date)"),
)


@pytest.mark.parametrize(("path", "undo", "old_sha"), [
    (H1_PATH, H1_AMENDMENT, H1_OLD_SHA), (H2_PATH, H2_AMENDMENT, H2_OLD_SHA)])
def test_undoing_the_amendment_restores_the_section_0_hash(path, undo, old_sha) -> None:
    text = path.read_text()
    assert hashlib.sha256(text.encode()).hexdigest() != old_sha
    for new, old in undo:
        assert text.count(new) == 1
        text = text.replace(new, old)
    assert hashlib.sha256(text.encode()).hexdigest() == old_sha


def test_default_table_is_the_hashed_table_and_a_plain_dict_is_accepted() -> None:
    for cls in (H1ScheduledMacroDrift, H2PostReleaseMomentum):
        assert cls().release_table is RELEASE_TABLE_ET
        assert cls(release_table=COMBINED).release_table is COMBINED
        assert "release_table" not in repr(cls(release_table=COMBINED))
        assert cls() == cls(release_table=COMBINED)  # compare=False: eq as before


def _bar(open_ct: datetime, trade_date: date, o: float, h: float, lo: float, c: float) -> Bar:
    bar = construct_bar(
        ts_event_ns=int(open_ct.astimezone(UTC).timestamp()) * 1_000_000_000, open=o, high=h,
        low=lo, close=c, volume=10, instrument_id=1, raw_symbol="MESH1", trade_date=trade_date,
        in_flatten_window=False, in_no_new_positions_window=False, early_halt_ct=None,
        in_scheduled_closure=False, is_roll_session=False, gap_before_minutes=0,
        vendor_degraded_day=False)
    assert isinstance(bar, Bar), bar
    return bar


FLAT = SimpleNamespace(position_micros=0, pending_signed_micros=0)


def test_h1_reads_the_table_argument() -> None:
    day = date(2021, 3, 17)  # FOMC, only in the 2019-2024 table
    bar = _bar(datetime(2021, 3, 16, 17, 0, tzinfo=CT), day, 3900.0, 3900.25, 3899.75, 3900.0)
    assert H1ScheduledMacroDrift().on_bar(bar, FLAT) == ()
    intents = H1ScheduledMacroDrift(release_table=COMBINED).on_bar(bar, FLAT)
    assert len(intents) == 1 and intents[0].side == "buy"


def test_h2_reads_the_table_argument() -> None:
    day = date(2021, 3, 10)  # CPI 08:30 ET = 07:30 CT, only in the 2019-2024 table
    bars, price = [], 3900.0
    for i in range(100):  # 06:00 .. 07:39 CT
        at = datetime(2021, 3, 10, 6, 0, tzinfo=CT) + timedelta(minutes=i)
        post = at >= datetime(2021, 3, 10, 7, 29, tzinfo=CT)
        step = 2.0 if post else 0.0
        bars.append(_bar(at, day, price, price + step + 0.25, price - 0.25 * (not post),
                         price + step))
        price += step

    def run(strategy) -> list:
        return [i for b in bars for i in strategy.on_bar(b, FLAT)]

    assert run(H2PostReleaseMomentum()) == []
    intents = run(H2PostReleaseMomentum(release_table=COMBINED))
    assert len(intents) == 1 and intents[0].side == "buy"


@pytest.fixture(scope="module")
def continuity():
    from screening.runner import screen_candidate, train_union_window
    from strategy.research._d1d_accounting import ALL_TRIALS

    trials = dict(ALL_TRIALS)
    window = train_union_window()
    out = {}
    for label, cls in (("E-H1 scheduled macro drift", H1ScheduledMacroDrift),
                       ("E-H2 post-release momentum", H2PostReleaseMomentum)):
        assert trials[label] is cls  # the continuity factory is the no-argument class
        out[label] = (
            screen_candidate(label, trials[label], window),
            screen_candidate(label, lambda cls=cls: cls(release_table=COMBINED), window))
    return out


@needs_research
@pytest.mark.parametrize("label", ["E-H1 scheduled macro drift", "E-H2 post-release momentum"])
@pytest.mark.parametrize("factory", [0, 1], ids=["no-argument", "combined-table"])
def test_amended_modules_reproduce_the_train_union_to_the_cent(continuity, label,
                                                               factory) -> None:
    from strategy.research._d1b_accounting import _moments

    logged = json.loads(Path("reports/stage_d1d_accounting.json").read_text())
    row = next(r for r in logged["runs"] if r["label"] == label)
    report = continuity[label][factory]
    assert report.window == "train_union" and report.n_dates == 289
    assert round(report.net_pnl_usd, 2) == round(row["net_pnl_usd"], 2)
    assert report.n_trips == row["n_trips"]
    assert report.trades_per_day == pytest.approx(row["trades_per_day"], abs=1e-12)
    assert report.zero_edge.win_probability == row["win_probability"]
    assert report.zero_edge.win_loss_ratio == row["win_loss_ratio"]
    assert (report.zero_edge.robust, report.drift_verdict, report.verdict) == (
        row["robust"], row["drift_verdict"], row["verdict"])
    sharpe = _moments(list(report.daily_net_usd))["sharpe"]
    assert abs(sharpe - logged["per_trial"][label]["sharpe"]) <= 1e-6
    assert continuity[label][0].daily_net_usd == continuity[label][1].daily_net_usd
