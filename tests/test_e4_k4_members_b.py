"""Stage E.4 K4 members of MemberCoder-B, part 1: the release tables' pin, the declarations,
K4-ngpre-01 and K4-apipre-01 (reports/stage_e4_member_specs.md sections 0, 4, 5, 10, 11).
K4-eiafade-01 and K4-eiamom-01 are in tests/test_e4_k4_members_b_eia.py, which reuses this file's
synthetic kit.

Synthetic bars only. Each rule is pinned on hand-built cases run through the real Stage E engine
(screening.stage_e_engine.run_engine under StageERules, built by the canary kit's rules_for), with
direct calls where the engine cannot reach a case (a None bar). The pin tests read the two frozen
JSON sources the tables were generated from, and Stage E.5's NGS check (Task C3: the five
confirmation-window NGS drops of ruling R-C3-1); no bar file is read, no runner is run, and no
freeze is written into the repository (the freeze test writes under tmp_path).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from functools import cache
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from rules import sessions
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import Phase, Status
from screening.stage_e_engine import EngineResult, Fill, IntentRecord, run_engine
from screening.stage_e_freeze import (
    MemberDecl,
    check_member_source,
    load_cluster_freeze,
    verify_cluster_code,
    write_cluster_freeze,
)
from screening.stage_e_frozen import load_frozen_tables
from screening.stage_e_rules import ReleaseCalendar, StageERules, release_calendar_from_dict
from strategy.interface import Bar
from strategy.members.k4 import _releases as tables
from strategy.members.k4 import apipre, eiafade, eiamom, ngpre
from strategy.members.k4._calendar import ENERGY_FULL_SESSIONS
from strategy.members.k4._event_common import clock_minute, ct_open_ns, price_ticks
from strategy.stage_e.interface import (
    LegSpec,
    MemberAccountView,
    MinuteView,
    StageEMember,
    TradingInterval,
)
from tests._stage_e_canary_kit import NO_RELEASES, release_calendar, rules_for

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
REPO = Path(__file__).resolve().parents[1]
K4_DIR = REPO / "strategy" / "members" / "k4"
CODER_B_FILES = ("ngpre.py", "apipre.py", "eiafade.py", "eiamom.py", "_event_common.py",
                 "_releases.py")
CALENDAR_JSON = REPO / "reports" / "stage_e2b_release_calendar.json"
CHECK_JSON = REPO / "reports" / "stage_e4_release_check.json"
GENERATOR = REPO / "reports" / "stage_e4_briefs" / "gen_k4_releases.py"
CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
CHECK_SHA256 = "4c71d7985c3471a86cbbd88b613b9a2f81d1b08f7aa60eb442f3c77834a04896"  # R-T3-1
# Stage E.5 Task C3: the confirmation-window NGS check and the generator applying its drops.
E5_CHECK_JSON = REPO / "reports" / "stage_e5_ngs_check.json"
E5_GENERATOR = REPO / "reports" / "stage_e5_briefs" / "gen_k4_releases_e5.py"
E5_CHECK_SHA256 = "ddfecb3e1575dc817aaeebc0f8795ebcbbbd10e78b4a936ec8b454d277706b44"
S_NG = ("2019-05-06", "2024-02-29")  # the E.5 confirmation window for NGS
# (module, factory, root, S0.2 ordinal)
DECLS: tuple[tuple[ModuleType, str, str, int], ...] = (
    (ngpre, "make_ng", "NG", 7), (apipre, "make_mcl", "MCL", 8), (eiafade, "make_mcl", "MCL", 9),
    (eiamom, "make_mcl", "MCL", 10))
BASE_PRICE = MappingProxyType({"MCL": 70.0, "NG": 3.0})


def hm(hh: int, mm: int) -> int:
    return hh * 60 + mm


DAY_START, DAY_END = hm(7, 0), hm(15, 45)  # the synthetic day segment of trade date d, CT date d

# regular energy trade dates (EC-CAL full sessions, F 15:08), a standard week of 2025-06
MON, TUE, WED, THU = date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4), date(2025, 6, 5)


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date of synthetic bars on CT date d, [start, end), every bar flat at
    o = h = l = c = the root's base price plus ``closes[minute]`` ticks."""

    trade_date: date
    closes: Mapping[int, int] = field(default_factory=dict)  # CT minute -> tick offset
    skip: frozenset[int] = frozenset()  # CT minutes of date d with no bar
    ids: Mapping[int, int] = field(default_factory=dict)  # per-minute instrument_id overrides
    instrument_id: int = 777
    halt: str = ""  # early_halt_ct label of CT date d
    flatten_from: int | None = None  # a synthetic F: in_flatten_window from this minute
    start: int = DAY_START
    end: int = DAY_END


def base_ticks(root: str) -> int:
    return price_ticks(BASE_PRICE[root], product(root).vendor_tick)


def ns_at(day: date, minute: int) -> int:
    utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
    return int(utc.timestamp()) * NS


def _rows(root: str, d: Day) -> list[dict]:
    b, fixed = base_ticks(root), product(root).vendor_tick_fixed
    out = []
    for minute in range(d.start, d.end):
        if minute in d.skip:
            continue
        px = (b + d.closes.get(minute, 0)) * fixed / PRICE_SCALE
        utc = datetime.combine(d.trade_date, time(minute // 60, minute % 60),
                               tzinfo=CT).astimezone(UTC)
        state = sessions.session_state(root, utc)
        synthetic_f = d.flatten_from is not None and minute >= d.flatten_from
        out.append({
            "ts_event": int(utc.timestamp()) * NS, "open": px, "high": px, "low": px,
            "close": px, "volume": 10, "instrument_id": d.ids.get(minute, d.instrument_id),
            "raw_symbol": f"{root}Q5", "trade_date": d.trade_date.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": d.halt, "in_scheduled_closure": False, "is_roll_session": False,
            "gap_before_minutes": 0, "vendor_degraded_day": False})
    return out


def frame(root: str, days: Sequence[Day]) -> pd.DataFrame:
    rows = [r for d in days for r in _rows(root, d)]
    return pd.DataFrame(rows).sort_values("ts_event", ignore_index=True)


def run(member: Any, days: Sequence[Day], *, releases: ReleaseCalendar = NO_RELEASES,
        rules: StageERules | None = None) -> EngineResult:
    if rules is None:
        rules = rules_for(member.legs, [d.trade_date for d in days], releases)
    return run_engine({member.root: frame(member.root, days)}, member, member.legs, rules)


@dataclass(frozen=True)
class ForcedLimitRules(StageERules):
    """TEST ONLY: the real rules plus an engine-forced D9.7 exit (reason price_limit_exit) queued
    on the bars opening at ``force_at_ns`` while the leg holds exposure. MCL and NG are not in
    rules.price_limits.HARD_LIMIT_PRODUCTS, so the real D9.7 exit cannot fire on them; this shows
    what the member does when the engine closes its position on its own (S0.7)."""

    force_at_ns: frozenset[int] = frozenset()

    def forced_reasons(self, run: Any, root: str, bar: Bar) -> tuple[str, ...]:
        base = super().forced_reasons(run, root, bar)
        if base or bar.ts_event_ns not in self.force_at_ns or not run.exposure(root):
            return base
        return ("price_limit_exit",)


def forced_limit_rules(member: Any, days: Sequence[Day], at: Sequence[tuple[date, int]]
                       ) -> StageERules:
    return rules_for(member.legs, [d.trade_date for d in days], NO_RELEASES,
                     cls=ForcedLimitRules, force_at_ns=frozenset(ns_at(d, m) for d, m in at))


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def fills(res: EngineResult) -> list[tuple[date, str, str, str]]:
    """(trade date, fill bar CT hh:mm, side, reason) of every fill."""
    return [(f.trade_date, f"{ct(f.fill_ts_ns):%H:%M}", f.side, f.reason)
            for f in res.events(Fill)]


def intents(res: EngineResult) -> list[tuple[date, str, bool, str | None]]:
    """(CT date, the emitting bar's CT hh:mm, accepted, refusal reason) of every intent."""
    out = []
    for r in res.events(IntentRecord):
        bar_open = ct(r.decision_ts_ns - 60 * NS)
        out.append((bar_open.date(), f"{bar_open:%H:%M}", r.accepted,
                    None if r.refusal is None else r.refusal.reason))
    return out


def trade(day: date, entry: str, exit_: str, side: str = "buy",
          exit_reason: str = "strategy") -> list[tuple[date, str, str, str]]:
    other = "sell" if side == "buy" else "buy"
    return [(day, entry, side, "strategy"), (day, exit_, other, exit_reason)]


def decided(day: date, *hhmm: str) -> list[tuple[date, str, bool, None]]:
    """Accepted intents emitted on the bars at ``hhmm`` of CT date ``day``."""
    return [(day, t, True, None) for t in hhmm]


def release_at(root: str, day: date, hh: int, mm: int) -> ReleaseCalendar:
    return release_calendar(root, [ns_at(day, hm(hh, mm))])


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def view_of(root: str, ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({root: bar}))


def account_of(root: str, position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({root: position}), MappingProxyType({root: pending}),
                             MappingProxyType({root: None}), MappingProxyType({root: 0}))


def bar_at(root: str, day: date, minute: int, offset: int = 0, *, instrument_id: int = 777,
           halt: time | None = None) -> Bar:
    px = (base_ticks(root) + offset) * product(root).vendor_tick_fixed / PRICE_SCALE
    return Bar(ns_at(day, minute), px, px, px, px, 10, instrument_id, f"{root}Q5", day, False,
               False, halt, False, False, 0, False)


# ------------------------------------------------------------------ table pin ----
@cache
def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ct_of(instant_utc: str) -> datetime:
    return datetime.fromisoformat(instant_utc.replace("Z", "+00:00")).astimezone(CT)


SECTION_11_WPSR_DROPS = ("2025-12-29", "2026-05-28")  # 2025-07-16 restored (R-T3-1)
SECTION_11_NGS_DROPS = ("2025-12-29",)
SECTION_11_NGS_UNVERIFIABLE = ("2025-05-01", "2025-05-29", "2025-06-18")
# Ruling R-C3-1 (C9's first drop rule): the E.5 check's drop_actual_differs rows.
E5_NGS_DROPS = ("2019-12-26", "2020-01-02", "2020-11-12", "2021-01-21", "2023-11-09")
# sha256 of the 21 source lines holding the 63 research-window NGS rows (2025-04-03..2026-06-18),
# joined by "\n", as the Stage E.4 module wrote them (before the E.5 amendment).
RESEARCH_WINDOW_NGS_LINES_SHA256 = (
    "d1a4ccf4cb541d25bd0a446e408323fa0daa23c63e066ad9ad616d557fcc3746")


def test_both_sources_have_the_pinned_sha256() -> None:
    assert _sha(CALENDAR_JSON) == CALENDAR_SHA256 == tables.RELEASE_CALENDAR_SHA256
    assert _sha(CHECK_JSON) == CHECK_SHA256 == tables.RELEASE_CHECK_SHA256
    assert tuple(_json(CHECK_JSON)["window"]) == tables.RESEARCH_CHECK_WINDOW


def test_the_drops_are_the_release_checks_drop_verdicts_as_section_11_lists_them() -> None:
    check = _json(CHECK_JSON)
    wpsr = {r["date"]: r["verdict"] for r in check["wpsr"] if r["verdict"].startswith("drop")}
    ngs = {r["date"]: r["verdict"] for r in check["ngs"]
           if r["verdict"].startswith("drop") or r["verdict"] == "updated"}
    assert tuple(d for d, _ in tables.DROPPED_WPSR) == tuple(sorted(wpsr)) == SECTION_11_WPSR_DROPS
    assert tuple(d for d, _ in tables.DROPPED_NGS) == tuple(sorted(ngs)) == SECTION_11_NGS_DROPS
    for rows, verdicts in ((tables.DROPPED_WPSR, wpsr), (tables.DROPPED_NGS, ngs)):
        for day, reason in rows:
            assert reason.startswith(f"{verdicts[day]}: "), (day, reason)
    kept = {r["verdict"] for r in check["wpsr"]} | {r["verdict"] for r in check["ngs"]}
    assert kept == {"keep", "drop_actual_differs", "unverifiable", "updated"}  # nothing else


def test_wpsr_table_is_every_calendar_row_less_the_drops_with_t_w_in_ct() -> None:
    dropped = {d for d, _ in tables.DROPPED_WPSR}
    expected = []
    for r in _json(CALENDAR_JSON)["releases"]:
        if r["release"] != "WPSR" or r["date"] in dropped:
            continue
        local = _ct_of(r["instant_utc"])
        assert local.date().isoformat() == r["date"] and r["tz"] == "America/New_York"
        weekday = date.fromisoformat(r["date"]).weekday()
        expected.append((r["date"], f"{local:%H:%M}", weekday,
                         weekday == 2 and r["time_local"] == "10:30"))
    assert tuple(sorted(expected)) == tables.WPSR
    assert len(tables.WPSR) == 371 - 2 and sum(1 for row in tables.WPSR if row[3]) == 317
    assert all(row[2] == 2 and row[1] == "09:30" for row in tables.WPSR if row[3])  # K4-L-02
    assert {row[1] for row in tables.WPSR} == {"09:30", "10:00", "11:00", "12:00"}
    window = [row for row in tables.WPSR if "2025-04-01" <= row[0] <= "2026-06-19"]
    assert len(window) == 62 and sum(1 for row in window if row[3]) == 56  # section 11


def test_ngs_table_is_every_calendar_row_less_the_drop_with_t_n_in_ct() -> None:
    dropped = {d for d, _ in tables.DROPPED_NGS} | {d for d, _ in tables.DROPPED_NGS_CONFIRMATION}
    expected = []
    for r in _json(CALENDAR_JSON)["releases"]:
        if r["release"] != "NGS" or r["date"] in dropped:
            continue
        local = _ct_of(r["instant_utc"])
        assert local.date().isoformat() == r["date"]
        expected.append((r["date"], f"{local:%H:%M}"))
    assert tuple(sorted(expected)) == tables.NGS
    assert len(tables.NGS) == 373 - 1 - 5 and {t for _, t in tables.NGS} == {"09:30", "11:00"}
    assert len([d for d, _ in tables.NGS if "2025-04-01" <= d <= "2026-06-19"]) == 63


def test_the_e5_check_has_the_pinned_sha256_and_window() -> None:
    assert _sha(E5_CHECK_JSON) == E5_CHECK_SHA256 == tables.E5_NGS_CHECK_SHA256
    assert tuple(_json(E5_CHECK_JSON)["window"]) == S_NG == tables.CONFIRMATION_CHECK_WINDOW
    assert S_NG[1] < tables.RESEARCH_CHECK_WINDOW[0]  # the two windows do not overlap


def test_the_e5_drops_are_the_e5_checks_drop_verdicts_on_or_after_s_ng() -> None:
    rows = _json(E5_CHECK_JSON)["ngs"]
    assert {r["verdict"] for r in rows} == {"keep", "drop_actual_differs"}  # nothing else
    calendar = sorted((r["date"], r["time_local"]) for r in _json(CALENDAR_JSON)["releases"]
                      if r["release"] == "NGS" and S_NG[0] <= r["date"] <= S_NG[1])
    assert sorted((r["date"], r["time_et"]) for r in rows) == calendar and len(calendar) == 252
    drops = {r["date"]: r for r in rows
             if r["verdict"] == "drop_actual_differs" and r["date"] >= S_NG[0]}
    confirmation = tables.DROPPED_NGS_CONFIRMATION
    assert tuple(d for d, _ in confirmation) == tuple(sorted(drops)) == E5_NGS_DROPS
    for day, reason in confirmation:
        assert reason == f"drop_actual_differs: {drops[day]['reason']}", day
    ngs_days = {d for d, _ in tables.NGS}
    assert not ngs_days & set(E5_NGS_DROPS)
    assert not {d for d, _ in tables.DROPPED_NGS} & set(E5_NGS_DROPS)
    fridays = {r["actual_date"] for r in drops.values() if r["actual_date"] is not None}
    assert len(fridays) == 4 and not fridays & ngs_days  # a drop only: no Friday row is added
    assert not {date.fromisoformat(d) for d in E5_NGS_DROPS} & set(ngpre.schedule(tables.NGS))


def _block(text: str, name: str) -> str:
    """The literal `name: ... = (...)` block of a generated module (a one-line `()` included)."""
    start = text.index(f"\n{name}: ") + 1
    line_end = text.index("\n", start)
    if text[start:line_end].endswith("= ()"):
        return text[start:line_end + 1]
    return text[start:text.index("\n)\n", start) + 3]


def test_research_window_ngs_rows_are_unchanged_by_the_e5_drops() -> None:
    e4_dropped = {d for d, _ in tables.DROPPED_NGS}
    research = sorted((r["date"], f"{_ct_of(r['instant_utc']):%H:%M}")
                      for r in _json(CALENDAR_JSON)["releases"]
                      if r["release"] == "NGS" and r["date"] not in e4_dropped
                      and "2025-04-01" <= r["date"] <= "2026-06-19")
    assert len(research) == 63
    assert tuple(row for row in tables.NGS if "2025-04-01" <= row[0] <= "2026-06-19") == tuple(
        research)
    lines = _block((K4_DIR / "_releases.py").read_text(encoding="utf-8"), "NGS").split("\n")
    window = [ln for ln in lines if "2025-04-01" <= ln.strip()[2:12] <= "2026-06-19"]
    assert len(window) == 21 and sum(ln.count("(") for ln in window) == 63
    assert hashlib.sha256("\n".join(window).encode()).hexdigest() == (
        RESEARCH_WINDOW_NGS_LINES_SHA256)


def _generators() -> tuple[ModuleType, ModuleType]:
    mods = []
    for name, path in (("gen_k4_releases", GENERATOR), ("gen_k4_releases_e5", E5_GENERATOR)):
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mods.append(mod)
    return mods[0], mods[1]


def test_the_e5_amendment_removes_the_five_ngs_rows_and_nothing_else() -> None:
    gen, e5 = _generators()
    e4_text = e5.e4_text(gen, _json(CALENDAR_JSON), _json(CHECK_JSON))
    text = (K4_DIR / "_releases.py").read_text(encoding="utf-8")
    for name in ("DROPPED_WPSR", "DROPPED_NGS", "API_DROPPED_WEEKS", "NGS_UNVERIFIED_IN_WINDOW",
                 "WPSR", "FEDERAL_MONDAY_HOLIDAYS", "NYSE_NOT_FULL"):
        assert _block(text, name) == _block(e4_text, name), name  # byte-identical
    old, new = _block(e4_text, "NGS").split("\n"), _block(text, "NGS").split("\n")
    assert len(old) == len(new)  # no line lost every row
    literals = [f'("{d}", "09:30"),' for d in E5_NGS_DROPS]  # all five at 09:30 CT
    changed = [(o, n) for o, n in zip(old, new, strict=True) if o != n]
    assert len(changed) == 4  # 2019-12-26 and 2020-01-02 share a line
    for o, n in changed:
        items = re.findall(r'\("\d{4}-\d\d-\d\d", "\d\d:\d\d"\),', o)
        assert o == "    " + " ".join(items)
        assert n == "    " + " ".join(x for x in items if x not in literals)
    assert all(any(lit in o for o, _ in changed) for lit in literals)
    assert not any(lit in text for lit in literals)


def test_unverifiable_storage_releases_are_kept_and_labelled() -> None:
    check = _json(CHECK_JSON)
    unverifiable = tuple(sorted(r["date"] for r in check["ngs"]
                                if r["verdict"] == "unverifiable"))
    assert unverifiable == tables.NGS_UNVERIFIED_IN_WINDOW
    assert tables.NGS_UNVERIFIED_IN_WINDOW == SECTION_11_NGS_UNVERIFIABLE
    ngs_days = {d for d, _ in tables.NGS}
    assert all(d in ngs_days for d in tables.NGS_UNVERIFIED_IN_WINDOW)


def test_api_dropped_weeks_is_empty_per_the_check() -> None:
    weeks = _json(CHECK_JSON)["api_weeks"]
    assert len(weeks) == 56  # section 11: 56 standard weeks in the window
    assert tables.API_DROPPED_WEEKS == tuple(sorted(
        w["wpsr_date"] for w in weeks if w["monday_federal_holiday"]
        or w["api_row_date"] != w["tuesday"] or w["api_row_time_et"] != "16:30")) == ()


def test_federal_monday_holidays_are_the_checks_dates() -> None:
    raw = _json(CHECK_JSON)["federal_monday_holidays"]
    assert len(raw) == 47  # 2025-01-20 is both MLK Day and Inauguration Day: 46 dates
    assert tuple(sorted({h["date"] for h in raw})) == tables.FEDERAL_MONDAY_HOLIDAYS
    assert len(tables.FEDERAL_MONDAY_HOLIDAYS) == 46
    assert all(date.fromisoformat(d).weekday() == 0 for d in tables.FEDERAL_MONDAY_HOLIDAYS)


def test_nyse_not_full_is_every_closure_and_early_close_of_the_check() -> None:
    nyse = _json(CHECK_JSON)["nyse"]
    assert (len(nyse["full_closures"]), len(nyse["early_closes"])) == (69, 15)
    listed = {x["date"] for x in nyse["full_closures"]} | {x["date"] for x in nyse["early_closes"]}
    assert tuple(sorted(listed)) == tables.NYSE_NOT_FULL
    assert len(tables.NYSE_NOT_FULL) == 84
    for d in ("2025-07-03", "2025-11-28", "2025-12-24", "2025-01-09"):
        assert d in tables.NYSE_NOT_FULL


def test_the_module_is_exactly_the_generators_output() -> None:
    gen, e5 = _generators()
    calendar, check = _json(CALENDAR_JSON), _json(CHECK_JSON)
    gen.check_window_rows(calendar, check)
    dropped_wpsr = gen.drops(check, "WPSR", gen.SECTION11_WPSR)
    dropped_ngs = gen.drops(check, "NGS", gen.SECTION11_NGS)
    text = gen.render(gen.wpsr_rows(calendar, {d for d, _ in dropped_wpsr}),
                      gen.ngs_rows(calendar, {d for d, _ in dropped_ngs}), dropped_wpsr,
                      dropped_ngs, gen.api_dropped(check), gen.federal_mondays(check),
                      gen.nyse_not_full(check), gen.unverified_ngs(check), check["window"])
    assert e5.e4_text(gen, calendar, check) == text  # the Stage E.4 module, rendered as before
    amended = e5.amend(gen, calendar, check, _json(E5_CHECK_JSON))  # plus the E.5 drops (C3)
    assert (K4_DIR / "_releases.py").read_text(encoding="utf-8") == amended


# ---------------------------------------------------------------- declarations ----
@pytest.mark.parametrize("name", CODER_B_FILES)
def test_every_coder_b_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k4/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K4") == []


@pytest.mark.parametrize("decl", DECLS, ids=lambda d: d[0].MEMBER_ID)
def test_factories_name_the_label_and_trade_one_leg(decl: tuple) -> None:
    module, factory, root, _ = decl
    member = vars(module)[factory]()
    assert isinstance(member, StageEMember)
    assert member.name == f"{module.MEMBER_ID} {root}"  # S0.2
    assert member.root == root and member.legs == (LegSpec(root, True),)  # S0.1
    assert list(member.trading_windows) == [root]
    assert (root,) == module.EXPOSURES
    assert vars(module)[factory]() is not member  # every call starts from fresh state
    other = "make_mcl" if factory == "make_ng" else "make_ng"
    assert other not in vars(module) and "make_rb" not in vars(module)


def test_trading_windows_are_the_s0_12_intervals() -> None:
    assert ngpre.make_ng().trading_windows["NG"] == (
        TradingInterval(time(7, 59), time(10, 1)), TradingInterval(time(9, 29), time(11, 31)))
    assert apipre.make_mcl().trading_windows["MCL"] == (
        TradingInterval(time(15, 24), time(15, 25)), TradingInterval(time(15, 39), time(15, 40)),
        TradingInterval(time(7, 29), time(9, 30)))  # K4-L-07: offset 0
    assert eiafade.make_mcl().trading_windows["MCL"] == (TradingInterval(time(9, 29),
                                                                         time(13, 30)),)
    assert eiamom.make_mcl().trading_windows["MCL"] == (
        TradingInterval(time(9, 29), time(10, 0)), TradingInterval(time(14, 29), time(15, 0)))


def test_size_is_the_frozen_q_c_and_the_clock_is_ct() -> None:
    frozen = load_frozen_tables()
    assert (frozen.vehicles["MCL"].q_c, frozen.vehicles["NG"].q_c) == (4, 1)  # S0.3
    assert frozen.day_session_ct["MCL"] == (time(8, 0), time(13, 30))
    assert time(13, 28) == eiafade.EXIT_DECISION_CT  # C - 2 (C 618-620)
    c = frozen.day_session_ct["MCL"][1]
    assert clock_minute(eiafade.EXIT_DECISION_CT) == clock_minute(c) - 2
    assert ct_open_ns(WED, hm(7, 29)) == ns_at(WED, hm(7, 29))
    assert price_ticks(70.01, product("MCL").vendor_tick) == 7001  # S0.10
    assert price_ticks(3.001, product("NG").vendor_tick) == 3001
    assert product("MCL").vendor_tick == Decimal("0.01")
    assert product("NG").vendor_tick == Decimal("0.001")


def test_the_4_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """Coder B's declarations (S0.2 ordinals 7-10) pass the real freeze code; the freeze is
    written under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k4").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k4" / "__init__.py").write_bytes(b"")
    for name in (*CODER_B_FILES, "_calendar.py"):  # apipre imports _calendar (read only here)
        shutil.copyfile(K4_DIR / name, members_dir / "k4" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} {root}", ordinal, m.__name__, factory,
                        (LegSpec(root, True),)) for m, factory, root, ordinal in DECLS]
    write_cluster_freeze("K4", decls, tmp_path)
    freeze = load_cluster_freeze("K4", tmp_path)
    verify_cluster_code(freeze)
    assert [(m.label, m.ordinal) for m in freeze.members] == [
        ("K4-ngpre-01 NG", 7), ("K4-apipre-01 MCL", 8), ("K4-eiafade-01 MCL", 9),
        ("K4-eiamom-01 MCL", 10)]


def test_a_member_refuses_an_exposure_it_does_not_trade() -> None:
    with pytest.raises(ValueError):
        ngpre.NgPre("MCL")
    for cls in (apipre.ApiPre, eiafade.EiaFade, eiamom.EiaMom):
        with pytest.raises(ValueError):
            cls("NG")


def test_a_none_bar_is_no_decision_and_changes_no_state() -> None:
    for member, root in ((ngpre.make_ng(), "NG"), (apipre.make_mcl(), "MCL"),
                         (eiafade.make_mcl(), "MCL"), (eiamom.make_mcl(), "MCL")):
        before = dict(vars(member))
        assert member.on_minute(view_of(root, ns_at(WED, hm(9, 29)), None),
                                account_of(root)) == ()
        assert dict(vars(member)) == before


# ---------------------------------------------------------------------- ngpre ----
NG_SLOTS = {"2025-06-05": "09:30", "2025-06-18": "11:00", "2025-11-14": "09:30"}


def test_ngpre_table_rows_used_by_the_tests() -> None:
    ngs = dict(tables.NGS)
    assert {d: ngs[d] for d in NG_SLOTS} == NG_SLOTS
    assert date.fromisoformat("2025-11-14").weekday() == 4  # a Friday 10:30 ET exception
    assert date.fromisoformat("2025-06-18").weekday() == 2  # a Wednesday 12:00 ET exception
    assert "2025-12-29" not in ngs and "2025-06-03" not in ngs  # dropped; not a release date
    assert ngpre.schedule((("2025-06-05", "09:30"), ("2025-06-18", "11:00"))) == {
        THU: (hm(7, 59), hm(9, 59)), date(2025, 6, 18): (hm(9, 29), hm(11, 29))}


def test_ngpre_standard_thursday_sells_at_0800_and_exits_at_1000() -> None:
    res = run(ngpre.make_ng(), [Day(THU)])
    assert intents(res) == decided(THU, "07:59", "09:59")
    assert fills(res) == trade(THU, "08:00", "10:00", side="sell")
    assert [f.qty for f in res.events(Fill)] == [1, 1]  # q_c NG = 1


def test_ngpre_wednesday_1200_et_release_moves_both_decisions_to_t_1100_ct() -> None:
    day = date(2025, 6, 18)
    res = run(ngpre.make_ng(), [Day(day)])
    assert intents(res) == decided(day, "09:29", "11:29")
    assert fills(res) == trade(day, "09:30", "11:30", side="sell")


def test_ngpre_friday_1030_et_release_trades_the_0930_ct_slot() -> None:
    day = date(2025, 11, 14)
    res = run(ngpre.make_ng(), [Day(day)])
    assert fills(res) == trade(day, "08:00", "10:00", side="sell")


def test_ngpre_a_dropped_release_and_a_non_table_date_are_not_traded() -> None:
    days = [Day(TUE), Day(date(2025, 12, 29))]  # not a release date; the dropped NGS row
    res = run(ngpre.make_ng(), days)
    assert intents(res) == [] and fills(res) == []


def test_ngpre_an_early_halt_date_is_not_traded() -> None:
    res = run(ngpre.make_ng(), [Day(THU, halt="12:00")])
    assert intents(res) == [] and fills(res) == []


def test_ngpre_a_missing_entry_bar_means_no_trade() -> None:
    res = run(ngpre.make_ng(), [Day(THU, skip=frozenset({hm(7, 59)}))])
    assert intents(res) == [] and fills(res) == []


def test_ngpre_a_missing_t_plus_29_bar_sends_the_exit_on_the_next_present_bar() -> None:
    res = run(ngpre.make_ng(), [Day(THU, skip=frozenset({hm(9, 59), hm(10, 0)}))])
    assert intents(res) == decided(THU, "07:59", "10:01")
    assert fills(res) == trade(THU, "08:00", "10:02", side="sell")


def test_ngpre_the_fill_guard_at_t_does_not_touch_the_t_minus_90_or_t_plus_30_fills() -> None:
    res = run(ngpre.make_ng(), [Day(THU)], releases=release_at("NG", THU, 9, 30))
    assert fills(res) == trade(THU, "08:00", "10:00", side="sell")
    assert res.counters.get("fill_guard_deferral", 0) == 0


def test_ngpre_a_release_at_the_entry_fill_is_deferred_by_d9_5a() -> None:
    """What the engine's D9.5a guard does to a fill landing in [release, release + 2 min): the
    08:00 entry waits for the first bar at or after 08:02 (a synthetic release at 08:00)."""
    res = run(ngpre.make_ng(), [Day(THU)], releases=release_at("NG", THU, 8, 0))
    assert fills(res) == trade(THU, "08:02", "10:00", side="sell")
    assert res.counters["fill_guard_deferral"] == 2


def test_ngpre_a_1100_ct_release_on_a_wpsr_wednesday_meets_the_0930_fill_guard() -> None:
    """The frozen release calendar lists the 09:30 CT WPSR for NG. On a Wednesday 12:00 ET
    storage release (2025-06-18, T 11:00 CT) the T - 90 entry fill (09:30) lands in that
    release's [09:30, 09:32), so the engine's D9.5a guard moves it to 09:32 (the member still
    decides on the 09:29 bar; the guard is the engine's, specs section 0). The same holds on
    2025-11-26 and 2025-12-31 in the research window."""
    day = date(2025, 6, 18)
    frozen = release_calendar_from_dict(_json(CALENDAR_JSON), CALENDAR_SHA256, "frozen")
    assert frozen.in_fill_guard("NG", ns_at(day, hm(9, 30)))
    assert not frozen.in_fill_guard("NG", ns_at(day, hm(11, 30)))
    res = run(ngpre.make_ng(), [Day(day)], releases=frozen)
    assert intents(res) == decided(day, "09:29", "11:29")
    assert fills(res) == trade(day, "09:32", "11:30", side="sell")


def test_ngpre_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(ngpre.make_ng(), [Day(THU, flatten_from=hm(9, 0))])
    assert fills(res) == trade(THU, "08:00", "09:01", side="sell", exit_reason="forced_flatten")
    assert intents(res) == decided(THU, "07:59")  # no exit of its own, no re-entry


def test_ngpre_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = ngpre.make_ng()
    days = [Day(THU)]
    res = run(member, days, rules=forced_limit_rules(member, days, [(THU, hm(8, 30))]))
    assert fills(res) == trade(THU, "08:00", "08:31", side="sell",
                               exit_reason="price_limit_exit")
    assert intents(res) == decided(THU, "07:59")


def test_ngpre_one_entry_per_date_across_consecutive_release_dates() -> None:
    days = [Day(THU), Day(date(2025, 6, 6)), Day(date(2025, 6, 12))]
    res = run(ngpre.make_ng(), days)
    assert fills(res) == (trade(THU, "08:00", "10:00", side="sell")
                          + trade(date(2025, 6, 12), "08:00", "10:00", side="sell"))


# --------------------------------------------------------------------- apipre ----
def _api_week(r_start: int = 0, r_end: int = 5, *, tue: dict | None = None,
              wed: dict | None = None) -> list[Day]:
    """The standard week of WED: Tuesday closes at 15:24 and 15:39 (tick offsets), Wednesday."""
    return [Day(TUE, closes={hm(15, 24): r_start, hm(15, 39): r_end}, **(tue or {})),
            Day(WED, **(wed or {}))]


def test_apipre_event_set_of_the_frozen_tables() -> None:
    events = apipre.event_wednesdays(tables.WPSR, ENERGY_FULL_SESSIONS,
                                     tables.FEDERAL_MONDAY_HOLIDAYS, tables.API_DROPPED_WEEKS)
    assert WED in events and date(2025, 7, 16) in events  # restored by ruling R-T3-1
    assert date(2019, 5, 1) not in events  # its Tuesday precedes EC-CAL's coverage (K4-L-13)
    assert date(2025, 5, 28) not in events and date(2025, 5, 29) not in events  # a Thursday week
    window = [w for w in events if date(2025, 4, 1) <= w <= date(2026, 6, 19)]
    assert len(window) == 56  # section 11: 56 standard weeks before the member's own exclusions
    standard = {date.fromisoformat(r[0]) for r in tables.WPSR if r[3]}
    assert events == standard - {date(2019, 5, 1)}


def test_apipre_r_api_from_the_tuesday_1524_and_1539_closes_buys() -> None:
    days = _api_week(0, 5)
    frame_ = frame("MCL", days)
    after_f = frame_[frame_["ts_event"].isin([ns_at(TUE, hm(15, 24)), ns_at(TUE, hm(15, 39))])]
    assert after_f["in_flatten_window"].all()  # read after F (15:08) and the 13:30 settlement
    res = run(apipre.make_mcl(), days)
    assert intents(res) == decided(WED, "07:29", "09:28")
    assert fills(res) == trade(WED, "07:30", "09:29", side="buy")
    assert [f.qty for f in res.events(Fill)] == [4, 4]  # q_c MCL = 4


def test_apipre_a_negative_r_api_sells() -> None:
    res = run(apipre.make_mcl(), _api_week(2, -1))
    assert fills(res) == trade(WED, "07:30", "09:29", side="sell")


def test_apipre_r_api_zero_is_no_trade() -> None:
    res = run(apipre.make_mcl(), _api_week(3, 3))
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("case", ["1524", "1539", "0729"])
def test_apipre_a_bar_on_another_instrument_is_no_trade(case: str) -> None:
    minute = {"1524": hm(15, 24), "1539": hm(15, 39), "0729": hm(7, 29)}[case]
    where = {"tue": {"ids": {minute: 778}}} if case != "0729" else {"wed": {"ids": {minute: 778}}}
    res = run(apipre.make_mcl(), _api_week(0, 5, **where))
    assert intents(res) == [] and fills(res) == []


@pytest.mark.parametrize("missing", ["1524", "1539", "0729"])
def test_apipre_a_missing_signal_or_entry_bar_is_no_trade(missing: str) -> None:
    minute = {"1524": hm(15, 24), "1539": hm(15, 39), "0729": hm(7, 29)}[missing]
    skip = {"skip": frozenset({minute})}
    where = {"tue": skip} if missing != "0729" else {"wed": skip}
    res = run(apipre.make_mcl(), _api_week(0, 5, **where))
    assert intents(res) == [] and fills(res) == []


def test_apipre_the_exit_is_before_the_0930_release_and_the_fill_guard_leaves_it() -> None:
    res = run(apipre.make_mcl(), _api_week(0, 5), releases=release_at("MCL", WED, 9, 30))
    assert fills(res) == trade(WED, "07:30", "09:29", side="buy")
    assert res.counters.get("fill_guard_deferral", 0) == 0


def test_apipre_a_missing_0928_bar_exits_on_the_next_bar_and_d9_5a_defers_that_fill() -> None:
    """The exit goes on the first later bar (09:29); its 09:30 fill lands in the WPSR release's
    [09:30, 09:32), so the engine's fill guard moves it to 09:32."""
    days = _api_week(0, 5, wed={"skip": frozenset({hm(9, 28)})})
    res = run(apipre.make_mcl(), days)
    assert intents(res) == decided(WED, "07:29", "09:29")
    assert fills(res) == trade(WED, "07:30", "09:30", side="buy")
    res = run(apipre.make_mcl(), days, releases=release_at("MCL", WED, 9, 30))
    assert fills(res) == trade(WED, "07:30", "09:32", side="buy")


def test_apipre_a_non_standard_week_is_not_traded() -> None:
    """The Memorial Day week of 2025: WPSR on Thursday 2025-05-29 at 12:00 ET (T_W 11:00 CT)."""
    assert ("2025-05-29", "11:00", 3, False) in tables.WPSR
    days = [Day(date(2025, 5, 27), closes={hm(15, 24): 0, hm(15, 39): 5}), Day(date(2025, 5, 28)),
            Day(date(2025, 5, 29))]
    res = run(apipre.make_mcl(), days)
    assert intents(res) == [] and fills(res) == []


def test_apipre_a_monday_federal_holiday_week_is_not_traded() -> None:
    """No standard week of the frozen WPSR table has a holiday Monday, so the rule is shown on
    an injected one-row table: the same week trades without the holiday and not with it."""
    wpsr = (("2025-06-04", "09:30", 2, True),)
    assert run(apipre.ApiPre("MCL", wpsr=wpsr, monday_holidays=()), _api_week()).events(Fill)
    res = run(apipre.ApiPre("MCL", wpsr=wpsr, monday_holidays=(MON.isoformat(),)), _api_week())
    assert intents(res) == [] and fills(res) == []


def test_apipre_a_tuesday_not_in_energy_full_sessions_is_not_traded() -> None:
    full = tuple(d for d in ENERGY_FULL_SESSIONS if d != TUE.isoformat())
    res = run(apipre.ApiPre("MCL", full_sessions=full), _api_week())
    assert intents(res) == [] and fills(res) == []


def test_apipre_an_api_dropped_week_is_not_traded() -> None:
    res = run(apipre.ApiPre("MCL", api_dropped=(WED.isoformat(),)), _api_week())
    assert intents(res) == [] and fills(res) == []


def test_apipre_a_wednesday_with_an_early_halt_is_not_traded() -> None:
    res = run(apipre.make_mcl(), _api_week(0, 5, wed={"halt": "12:00"}))
    assert intents(res) == [] and fills(res) == []


def test_apipre_a_signal_is_used_only_by_the_next_calendar_days_event() -> None:
    """A Tuesday's R_API serves only the Wednesday after it: when the next standard week's
    Tuesday has no bars, the earlier week's signal is not carried over (no forward fill)."""
    tue0, wed0 = date(2025, 5, 20), date(2025, 5, 21)
    assert (wed0.isoformat(), "09:30", 2, True) in tables.WPSR
    days = [Day(tue0, closes={hm(15, 24): 0, hm(15, 39): 5}), Day(wed0), Day(WED)]
    res = run(apipre.make_mcl(), days)
    assert fills(res) == trade(wed0, "07:30", "09:29")


def test_apipre_a_position_open_at_a_synthetic_f_is_closed_by_the_engine() -> None:
    res = run(apipre.make_mcl(), _api_week(0, 5, wed={"flatten_from": hm(8, 30)}))
    assert fills(res) == trade(WED, "07:30", "08:31", exit_reason="forced_flatten")
    assert intents(res) == decided(WED, "07:29")


def test_apipre_d9_7_engine_exit_no_duplicate_exit_no_reentry() -> None:
    member = apipre.make_mcl()
    days = _api_week(0, 5)
    res = run(member, days, rules=forced_limit_rules(member, days, [(WED, hm(8, 0))]))
    assert fills(res) == trade(WED, "07:30", "08:01", exit_reason="price_limit_exit")
    assert intents(res) == decided(WED, "07:29")


def test_apipre_two_consecutive_standard_weeks_each_use_their_own_tuesday() -> None:
    tue2, wed2 = TUE + timedelta(days=7), WED + timedelta(days=7)
    days = [*_api_week(0, 5), Day(THU), Day(tue2, closes={hm(15, 24): 0, hm(15, 39): -2}),
            Day(wed2)]
    res = run(apipre.make_mcl(), days)
    assert fills(res) == trade(WED, "07:30", "09:29") + trade(wed2, "07:30", "09:29", "sell")
