"""Stage E.4 Part 3 K3 members of MemberCoder-B, part 1: the synthetic kit, the table pins
(_calendar.py and _clocks.py recomputed from their sources), the declarations and what all five
members share (reports/stage_e4c_member_specs.md sections 0, 4, 5, 7-11).

The members' own rules are pinned in tests/test_e4_k3_members_b_ldn.py (K3-ldnrev-01,
K3-ldnmom-01), tests/test_e4_k3_members_b_ecb.py (K3-ecbfix-01) and
tests/test_e4_k3_members_b_tky.py (K3-tkypre-01, K3-tkypost-01), which reuse this file's kit
(adapted from tests/test_e4_k3_members_a.py and tests/test_e4_k5_members_b.py, not imported from
them).

Synthetic bars only, run through the real Stage E engine (screening.stage_e_engine.run_engine under
StageERules, built by the canary kit's rules_for), with direct calls where the engine cannot reach a
case (a None bar). The pins read the K3 check (reports/stage_e4c_release_check.json), the frozen
release calendar JSON and EC-CAL; no bar file is read, no runner is run, and no freeze is written
into the repository (the freeze test writes under tmp_path). Expected clock times are literals.
"""

from __future__ import annotations

import ast
import calendar as pycal
import difflib
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

from data.group_session import load_group_calendar, trade_dates_between
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
from strategy.members.k3 import _calendar as cal_tables
from strategy.members.k3 import _clocks as clocks
from strategy.members.k3 import ecbfix, ldnmom, ldnrev, tkypost, tkypre
from strategy.members.k3._event_common import (
    FixEvent,
    Plan,
    clock_minute,
    ct_open_ns,
    field_ticks,
    price_ticks,
)
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
MINUTES_PER_DAY = 1440
REPO = Path(__file__).resolve().parents[1]
K3_DIR = REPO / "strategy" / "members" / "k3"
CODER_B_FILES = ("_calendar.py", "_clocks.py", "_event_common.py", "ldnrev.py", "ldnmom.py",
                 "ecbfix.py", "tkypre.py", "tkypost.py")
MEMBER_FILES = ("ldnrev.py", "ldnmom.py", "ecbfix.py", "tkypre.py", "tkypost.py")
CHECK_JSON = REPO / "reports" / "stage_e4c_release_check.json"
CHECK_SHA256 = "c63c13a69559c90efdb72969e20244a261343839660436082fcaf44a35f931e9"
RELEASE_CALENDAR_JSON = REPO / "reports" / "stage_e2b_release_calendar.json"
RELEASE_CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
GENERATOR = REPO / "reports" / "stage_e4_briefs" / "gen_k3_tables.py"
K3_ROOTS = ("6E", "6A", "6B", "6C", "6J", "6S", "6N")
# (module, factory, root, S0.2 ordinal); 27 is K3-mehedge-01 6J (MemberCoder-A)
DECLS: tuple[tuple[ModuleType, str, str, int], ...] = (
    (ldnrev, "make_6e", "6E", 22), (ldnrev, "make_6j", "6J", 23), (ldnrev, "make_6s", "6S", 24),
    (ldnmom, "make_6e", "6E", 25), (ldnmom, "make_6j", "6J", 26),
    (ecbfix, "make_6e", "6E", 28), (tkypre, "make_6j", "6J", 29), (tkypost, "make_6j", "6J", 30))
BASE_PRICE = MappingProxyType({"6E": 1.1, "6J": 0.0067, "6S": 1.15})
Ticks = tuple[int, int, int, int]  # (open, high, low, close) offsets from the base, in ticks


def hm(hh: int, mm: int) -> int:
    """A minute key on CT calendar date d (the trade date)."""
    return hh * 60 + mm


def eve(hh: int, mm: int) -> int:
    """A minute key on CT calendar date d-1 (the evening that opens trade date d)."""
    return hh * 60 + mm - MINUTES_PER_DAY


def flat(x: int) -> Ticks:
    return (x, x, x, x)


# --------------------------------------------------------------------- synthetic bars ----
@dataclass(frozen=True)
class Day:
    """One trade date d of synthetic bars over the minute keys [start, end) (negative keys are
    minutes of CT date d-1, the evening that opens d), flat at the root's base price unless
    ``paths`` overrides a key (tick offsets from the base)."""

    trade_date: date
    paths: Mapping[int, Ticks] = field(default_factory=dict)
    skip: frozenset[int] = frozenset()  # minute keys with no bar
    ids: Mapping[int, int] = field(default_factory=dict)  # per-key instrument_id overrides
    instrument_id: int = 777
    halt: str = ""  # early_halt_ct label of CT date d
    evening_halt: str = ""  # early_halt_ct label of CT date d-1
    start: int = eve(17, 0)
    end: int = hm(15, 12)
    flatten_from: int | None = None  # a synthetic F: in_flatten_window from this key


def ct_day_minute(trade_date: date, key: int) -> tuple[date, int]:
    return (trade_date - timedelta(days=1) if key < 0 else trade_date), key % MINUTES_PER_DAY


def ns_at(trade_date: date, key: int) -> int:
    day, minute = ct_day_minute(trade_date, key)
    utc = datetime.combine(day, time(minute // 60, minute % 60), tzinfo=CT).astimezone(UTC)
    return int(utc.timestamp()) * NS


def base_ticks(root: str) -> int:
    return price_ticks(BASE_PRICE[root], product(root).vendor_tick)


def _rows(root: str, d: Day) -> list[dict]:
    b, fixed = base_ticks(root), product(root).vendor_tick_fixed
    out = []
    for key in range(d.start, d.end):
        if key in d.skip:
            continue
        o, h, lo, c = (b + x for x in d.paths.get(key, (0, 0, 0, 0)))
        ts = ns_at(d.trade_date, key)
        state = sessions.session_state(root, datetime.fromtimestamp(ts // NS, tz=UTC))
        synthetic_f = d.flatten_from is not None and key >= d.flatten_from
        out.append({
            "ts_event": ts, "open": o * fixed / PRICE_SCALE, "high": h * fixed / PRICE_SCALE,
            "low": lo * fixed / PRICE_SCALE, "close": c * fixed / PRICE_SCALE, "volume": 10,
            "instrument_id": d.ids.get(key, d.instrument_id), "raw_symbol": f"{root}M5",
            "trade_date": d.trade_date.isoformat(),
            "in_flatten_window": bool(state.must_be_flat) or synthetic_f,
            "in_no_new_positions_window": bool(not state.can_open) or synthetic_f,
            "early_halt_ct": d.evening_halt if key < 0 else d.halt,
            "in_scheduled_closure": False, "is_roll_session": False,
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
    on the bars opening at ``force_at_ns`` while the leg holds exposure. No FX root is in
    rules.price_limits.HARD_LIMIT_PRODUCTS (C11), so the real D9.7 exit cannot fire on them; this
    shows what the member does when the engine closes its position on its own (S0.7)."""

    force_at_ns: frozenset[int] = frozenset()

    def forced_reasons(self, run: Any, root: str, bar: Bar) -> tuple[str, ...]:
        base = super().forced_reasons(run, root, bar)
        if base or bar.ts_event_ns not in self.force_at_ns or not run.exposure(root):
            return base
        return ("price_limit_exit",)


def forced_limit_rules(member: Any, days: Sequence[Day], at: Sequence[tuple[date, int]]
                       ) -> StageERules:
    return rules_for(member.legs, [d.trade_date for d in days], NO_RELEASES,
                     cls=ForcedLimitRules, force_at_ns=frozenset(ns_at(d, k) for d, k in at))


def ct(ns: int) -> datetime:
    return datetime.fromtimestamp(ns // NS, tz=UTC).astimezone(CT)


def stamp(trade_date: date | None, ns: int) -> str:
    """CT "HH:MM" of an instant, prefixed "d-1 " when it lies on the evening before trade_date."""
    local = ct(ns)
    return f"d-1 {local:%H:%M}" if trade_date is not None and local.date() < trade_date \
        else f"{local:%H:%M}"


def fills(res: EngineResult) -> list[tuple[date | None, str, str, str]]:
    """(trade date, fill bar CT hh:mm, side, reason) of every fill."""
    return [(f.trade_date, stamp(f.trade_date, f.fill_ts_ns), f.side, f.reason)
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


def release_at(root: str, trade_date: date, key: int) -> ReleaseCalendar:
    return release_calendar(root, [ns_at(trade_date, key)])


# direct calls (the engine never calls a one-leg member on a minute without its bar)
def view_of(root: str, ts_ns: int, bar: Bar | None) -> MinuteView:
    return MinuteView(ts_ns, MappingProxyType({root: bar}))


def account_of(root: str, position: int = 0, pending: int = 0) -> MemberAccountView:
    return MemberAccountView(Phase.XFA, Status.ACTIVE, None, 0, 0,
                             MappingProxyType({root: position}), MappingProxyType({root: pending}),
                             MappingProxyType({root: None}), MappingProxyType({root: 0}))


def bar_at(root: str, trade_date: date, key: int, offsets: Ticks = (0, 0, 0, 0), *,
           instrument_id: int = 777) -> Bar:
    b, fixed = base_ticks(root), product(root).vendor_tick_fixed
    o, h, lo, c = ((b + x) * fixed / PRICE_SCALE for x in offsets)
    return Bar(ns_at(trade_date, key), o, h, lo, c, 10, instrument_id, f"{root}M5", trade_date,
               False, False, None, False, False, 0, False)


def state_of(member: Any) -> dict:
    """The member's whole mutable state, its FixEvent core's included."""
    core = vars(member).get("_core")
    return {**vars(member), **({} if core is None else {f"core.{k}": v
                                                        for k, v in vars(core).items()})}


def make(module: ModuleType, root: str) -> Any:
    return vars(module)[f"make_{root.lower()}"]()


# ------------------------------------------------------------------ table sources ----
@cache
def check() -> dict:
    return json.loads(CHECK_JSON.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _weekdays(first: date, last: date) -> list[date]:
    days = (first + timedelta(days=n) for n in range((last - first).days + 1))
    return [d for d in days if d.weekday() < 5]


def _ct_hhmm(day: date, hh: int, mm: int, zone: str) -> tuple[date, str]:
    local = datetime.combine(day, time(hh, mm), tzinfo=ZoneInfo(zone)).astimezone(CT)
    return local.date(), f"{local:%H:%M}"


def _easter(year: int) -> date:
    """Gregorian Easter Sunday (Meeus/Jones/Butcher), written independently of the generator."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    month = (h + el - 7 * m + 114) // 31
    day = (h + el - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def _tokyo_business_day(d: date, holidays: frozenset[str]) -> bool:
    return (d.weekday() < 5 and d.isoformat() not in holidays
            and not (d.month == 12 and d.day == 31) and not (d.month == 1 and d.day <= 3))


def _range_weekdays(ranges: Sequence[str], first: date, last: date) -> list[str]:
    out: list[str] = []
    for text in ranges:
        lo, hi = (date.fromisoformat(x) for x in text.split(".."))
        out += [d.isoformat() for d in _weekdays(max(lo, first), min(hi, last))]
    return sorted(out)


RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
# K3-L-11: the dates the second condition removes (named in the specs; the generator lists them)
EARLY_F_DATES = (
    "2024-01-15", "2024-02-19", "2024-05-27", "2024-06-19", "2024-07-03", "2024-07-04",
    "2024-09-02", "2024-11-28", "2025-01-20", "2025-02-17", "2025-05-26", "2025-06-19",
    "2025-09-01", "2025-11-27", "2026-01-19", "2026-02-16", "2026-05-25")
C9_1100_RANGES = (  # catalog C9, the computed weekday ranges at 11:00 CT
    "2019-03-11..2019-03-29", "2019-10-28..2019-11-01", "2020-03-09..2020-03-27",
    "2020-10-26..2020-10-30", "2021-03-15..2021-03-26", "2021-11-01..2021-11-05",
    "2022-03-14..2022-03-25", "2022-10-31..2022-11-04", "2023-03-13..2023-03-24",
    "2023-10-30..2023-11-03", "2024-03-11..2024-03-29", "2024-10-28..2024-11-01",
    "2025-03-10..2025-03-28", "2025-10-27..2025-10-31", "2026-03-09..2026-03-27")


# --------------------------------------------------------------------- table pins ----
# Lead ruling R-A2-1 and review SF-2 (Stage E.5): K3's frozen tables were generated under the v4
# rules/sessions.py, whose sha256 _calendar.SOURCE_SHA256 pins; harness v5 changed that file and
# moves exactly 14 frozen full FX sessions to an 11:30 CT flatten (K3's confirmation session
# decides). The three tests below pin v5 exactly and fail on any other drift.
V4_SESSIONS_SHA256 = "d9a7fcfe6724f066ad709ee1dd2b8bab322e74837f7524555c3608c069d83c13"
V5_SESSIONS_SHA256 = "beb9501d6235299cd716868a8c14cf1df1b3cc71fa0b58c4e9780e9035b07d28"
V5_FLATTENED_FX_DATES = (
    "2022-01-17", "2022-02-21", "2022-05-30", "2022-06-20", "2022-07-04", "2022-09-05",
    "2022-11-24", "2023-01-16", "2023-02-20", "2023-05-29", "2023-06-19", "2023-07-04",
    "2023-09-04", "2023-11-23")


def test_every_source_file_has_the_pinned_sha256() -> None:
    assert _sha(CHECK_JSON) == CHECK_SHA256
    pinned = dict(cal_tables.SOURCE_SHA256)
    assert set(pinned) == {"data/calendars/fx.py", "rules/sessions.py",
                           "reports/stage_e4c_release_check.json"}
    assert pinned["rules/sessions.py"] == V4_SESSIONS_SHA256  # K3's frozen pin (R-A2-1)
    for rel, sha in pinned.items():
        # R-A2-1, review SF-2: rules/sessions.py must be exactly the harness v5 file
        expected = V5_SESSIONS_SHA256 if rel == "rules/sessions.py" else sha
        assert _sha(REPO / rel) == expected, rel
    assert dict(clocks.SOURCE_SHA256) == {"reports/stage_e4c_release_check.json": CHECK_SHA256}
    assert cal_tables.EC_CAL_COVERAGE == ("2019-05-01", "2026-06-19")  # K4-L-13
    assert cal_tables.TOKYO_RANGE == clocks.CLOCK_RANGE == ("2019-04-01", "2026-06-19")  # K3-L-01


def _module_values(text: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    exec(compile(text, "<k3 table module>", "exec"), namespace)  # a data-only module
    return {k: v for k, v in namespace.items() if not k.startswith("__") and k != "annotations"}


_V5_TABLE_LINE = re.compile(r'^\s*("\d{4}-\d{2}-\d{2}",?\s*)+$|^# .*\(\d+ dates\)$')


def test_both_modules_are_exactly_the_generators_output() -> None:
    """Under v5 (R-A2-1, review SF-2) _clocks.py regenerates exactly; _calendar.py differs in
    exactly three names, all from the 14 dates: FX_FULL_SESSIONS loses them, FX_EARLY_F_DATES
    (the generator's complement list) gains them, and SOURCE_SHA256 carries the v5 sessions
    sha256. Every other value, and every other line of text, is equal."""
    spec = importlib.util.spec_from_file_location("gen_k3_tables", GENERATOR)
    assert spec is not None and spec.loader is not None
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    texts = gen.build()
    cal_rel, clocks_rel = "strategy/members/k3/_calendar.py", "strategy/members/k3/_clocks.py"
    assert set(texts) == {cal_rel, clocks_rel}
    assert (REPO / clocks_rel).read_text(encoding="utf-8") == texts[clocks_rel]
    frozen_text = (REPO / cal_rel).read_text(encoding="utf-8")
    frozen, regenerated = _module_values(frozen_text), _module_values(texts[cal_rel])
    changed = {k for k in frozen.keys() | regenerated.keys() if frozen.get(k) != regenerated.get(k)}
    assert changed == {"FX_FULL_SESSIONS", "FX_EARLY_F_DATES", "SOURCE_SHA256"}
    flattened = set(V5_FLATTENED_FX_DATES)
    assert flattened <= set(frozen["FX_FULL_SESSIONS"])
    assert regenerated["FX_FULL_SESSIONS"] == tuple(d for d in frozen["FX_FULL_SESSIONS"]
                                                    if d not in flattened)
    assert regenerated["FX_EARLY_F_DATES"] == tuple(sorted(frozen["FX_EARLY_F_DATES"]
                                                           + V5_FLATTENED_FX_DATES))
    assert dict(regenerated["SOURCE_SHA256"]) == {**dict(frozen["SOURCE_SHA256"]),
                                                  "rules/sessions.py": V5_SESSIONS_SHA256}
    diff = [line[1:] for line in difflib.unified_diff(frozen_text.splitlines(),
                                                      texts[cal_rel].splitlines(), lineterm="",
                                                      n=0)
            if line[:1] in "+-" and not line.startswith(("+++", "---"))]
    other = [line for line in diff if not (_V5_TABLE_LINE.match(line)
                                           or V4_SESSIONS_SHA256 in line
                                           or V5_SESSIONS_SHA256 in line)]
    assert diff and other == []


def test_fx_full_sessions_are_ec_cal_dates_without_halt_and_with_the_regular_f() -> None:
    """K3-L-11: no early_halt_ct AND the engine's F = 15:08 CT for every K3 root. Under v5 it
    holds for every frozen date but the 14 of R-A2-1 (review SF-2), which the engine now
    flattens early."""
    cal = load_group_calendar("fx")
    assert tuple(cal.coverage) == (date(2019, 5, 1), date(2026, 6, 19))
    full, removed = [], []
    for d in trade_dates_between(cal, *cal.coverage):
        if cal.early_halt_ct(d) is not None:
            continue
        fs = {sessions.flatten_time_ct(r, d) for r in K3_ROOTS}
        (full if fs == {time(15, 8)} else removed).append(d.isoformat())
    flattened = set(V5_FLATTENED_FX_DATES)
    assert tuple(full) == tuple(d for d in cal_tables.FX_FULL_SESSIONS if d not in flattened)
    assert len(cal_tables.FX_FULL_SESSIONS) == 1797 and len(full) == 1797 - 14
    assert tuple(removed) == tuple(sorted(cal_tables.FX_EARLY_F_DATES + V5_FLATTENED_FX_DATES))
    assert cal_tables.FX_EARLY_F_DATES == EARLY_F_DATES
    # the specs' named US holidays are among the removed dates (K3-L-11)
    assert {"2025-09-01", "2025-11-27", "2026-01-19", "2026-02-16", "2026-05-25"} <= set(removed)
    window = [d for d in full if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
    halts = [d for d in trade_dates_between(cal, *RESEARCH) if cal.early_halt_ct(d) is not None]
    assert [d.isoformat() for d in halts] == [  # specs line 20-21
        "2025-07-04", "2025-11-28", "2025-12-24", "2026-04-03", "2026-06-19"]
    assert len(trade_dates_between(cal, *RESEARCH)) == 316
    assert len(window) == 316 - 5 - 7  # the research window's halts and early-F dates


def test_v5_flattens_exactly_14_frozen_full_fx_sessions_all_before_2024() -> None:
    """R-A2-1: the frozen FX_FULL_SESSIONS dates whose v5 F for 6E is not the regular 15:08 are
    exactly the 14 derived-row dates, every one before 2024-01-01."""
    changed = tuple(d for d in cal_tables.FX_FULL_SESSIONS
                    if sessions.flatten_time_ct("6E", date.fromisoformat(d)) != time(15, 8))
    assert changed == V5_FLATTENED_FX_DATES
    for d in map(date.fromisoformat, changed):
        row = sessions.TOPSTEP_HOLIDAYS[d]
        assert row.source == "topstep_derived_e5_equity_calendar" and d < date(2024, 1, 1)
        assert sessions.flatten_time_ct("6E", d) == row.close_by_ct == time(11, 30)

def test_month_ends_are_the_last_ec_cal_date_of_each_covered_month() -> None:
    cal = load_group_calendar("fx")
    last: dict[str, str] = {}
    for d in trade_dates_between(cal, *cal.coverage):
        last[d.isoformat()[:7]] = d.isoformat()
    rows = tuple((m, me) for m, me in sorted(last.items())
                 if date(int(m[:4]), int(m[5:]), pycal.monthrange(int(m[:4]), int(m[5:]))[1])
                 <= cal.coverage[1])
    assert rows == cal_tables.MONTH_ENDS and len(rows) == 85  # 2019-05..2026-05
    assert rows == tuple((r["month"], r["me_date"]) for r in check()["month_ends"]
                         if r["in_ec_cal_coverage"])
    assert ("2026-06", "2026-06-19") not in rows  # 06-19 is not June 2026's month-end
    halted = [me for _, me in rows if me not in cal_tables.FX_FULL_SESSIONS]
    assert halted == ["2019-11-29", "2021-05-31", "2024-11-29", "2025-11-28"]  # K3-L-06
    assert [me for _, me in rows if me in cal_tables.EW_BANK_HOLIDAYS] == [
        "2020-08-31", "2021-05-31"]  # the EC-EW drop (section 11)


def test_ew_and_target_holidays_are_the_checks_rows() -> None:
    ew = tuple(sorted(r["date"] for r in check()["ec_ew"]))
    assert ew == cal_tables.EW_BANK_HOLIDAYS and len(ew) == 63
    in_window = [d for d in ew if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
    assert len(in_window) == 12  # section 11
    tgt = tuple(sorted({r["date"] for r in check()["ec_tgt"]}))
    assert tgt == cal_tables.TGT_CLOSING_DAYS and len(tgt) == 48
    rule = sorted(x.isoformat() for y in range(2019, 2027) for x in (
        date(y, 1, 1), _easter(y) - timedelta(days=2), _easter(y) + timedelta(days=1),
        date(y, 5, 1), date(y, 12, 25), date(y, 12, 26)))
    assert list(tgt) == rule  # six a year: the ECB rule (section 11)
    assert [d for d in tgt if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()] == [
        "2025-04-18", "2025-04-21", "2025-05-01", "2025-12-25", "2025-12-26", "2026-01-01",
        "2026-04-03", "2026-04-06", "2026-05-01"]  # section 11's list


def test_tokyo_business_days_gotobi_and_month_ends_follow_ec_jp() -> None:
    holidays = frozenset(r["date"] for r in check()["ec_jp_holidays"])
    assert len(holidays) == 148
    counts = {str(y): sum(1 for d in _weekdays(date(y, 1, 1), date(y, 12, 31))
                          if _tokyo_business_day(d, holidays)) for y in range(2019, 2027)}
    assert counts == check()["tokyo_business_days_count"]
    first, last = date(2019, 4, 1), date(2026, 6, 19)
    business = [d for d in _weekdays(first, date(2026, 6, 30)) if _tokyo_business_day(d, holidays)]
    table = tuple(d.isoformat() for d in business if d <= last)
    assert table == cal_tables.TOKYO_BUSINESS_DAYS and len(table) == 1761
    month_end = sorted({d.strftime("%Y-%m"): d.isoformat() for d in business}.values())
    assert month_end == check()["tokyo_month_end"] and len(month_end) == 87
    gotobi = [d for d in table if int(d[8:]) % 5 == 0]
    assert gotobi == check()["gotobi"] and len(gotobi) == 350
    events = tuple(d for d in table if d in set(gotobi) | set(month_end))
    assert events == cal_tables.GOTOBI_OR_TOKYO_MONTH_END and len(events) == 404
    assert "2026-06-30" not in events  # after the range; no member trades it anyway
    for d in ("2025-12-31", "2026-01-01", "2026-01-02", "2025-05-05", "2025-11-03"):
        assert d not in table  # year-end rule; Children's Day; Culture Day
    assert "2025-12-30" in events and "2026-02-27" in events  # month-ends that are not day 31


def test_clocks_are_zoneinfo_instants_and_pass_c9_and_the_check() -> None:
    weekdays = _weekdays(date(2019, 4, 1), date(2026, 6, 19))
    t_l, t_e = [], []
    for d in weekdays:
        (dl, tl), (de, te) = _ct_hhmm(d, 16, 0, "Europe/London"), _ct_hhmm(d, 14, 15,
                                                                           "Europe/Berlin")
        assert dl == de == d
        t_l.append((d.isoformat(), tl))
        t_e.append((d.isoformat(), te))
    assert tuple(t_l) == clocks.T_L and tuple(t_e) == clocks.T_E and len(t_l) == 1885
    at_1100 = [d for d, t in t_l if t == "11:00"]
    assert at_1100 == _range_weekdays(C9_1100_RANGES, date(2019, 4, 1), date(2026, 6, 19))
    assert at_1100 == [d for d, t in t_e if t == "08:15"]  # the same weeks (C9)
    assert {t for _, t in t_l} == {"10:00", "11:00"} and {t for _, t in t_e} == {"07:15", "08:15"}
    t_t = []
    for d in cal_tables.TOKYO_BUSINESS_DAYS:
        day, hhmm = _ct_hhmm(date.fromisoformat(d), 9, 55, "Asia/Tokyo")
        assert day == date.fromisoformat(d) - timedelta(days=1)  # always the evening of d-1
        t_t.append((d, hhmm))
    assert tuple(t_t) == clocks.T_T and {t for _, t in t_t} == {"18:55", "19:55"}
    tl, te, tt = dict(clocks.T_L), dict(clocks.T_E), dict(clocks.T_T)
    # C9's known-answer tests and computed examples (catalog lines 186-194 and 176-178)
    assert [tl[d] for d in ("2025-03-10", "2025-03-31", "2025-10-27", "2025-11-03")] == [
        "11:00", "10:00", "11:00", "10:00"]
    assert {tl[f"2021-11-0{i}"] for i in range(1, 6)} == {"11:00"}
    assert (te["2025-03-10"], te["2025-04-01"]) == ("08:15", "07:15")
    assert (tt["2025-11-04"], tt["2025-01-10"], tt["2025-03-10"], tt["2025-07-10"]) == (
        "18:55", "18:55", "19:55", "19:55")
    for key, table in (("t_l", tl), ("t_e", te)):
        for ka in check()[key]["known_answer"]:
            assert table[ka["date"]] == ka["expected_ct"] == ka["computed_ct"]
    for ka in check()["t_t"]["known_answer"]:
        assert ka["pass"] and tt[ka["d"]] == ka["computed"].split(" ")[1]


def test_every_event_date_of_every_member_has_its_clock() -> None:
    full = set(cal_tables.FX_FULL_SESSIONS)
    assert full <= set(dict(clocks.T_L)) and full <= set(dict(clocks.T_E))
    assert set(cal_tables.GOTOBI_OR_TOKYO_MONTH_END) <= set(cal_tables.TOKYO_BUSINESS_DAYS)
    assert set(cal_tables.TOKYO_BUSINESS_DAYS) == set(dict(clocks.T_T))


def test_the_event_set_sizes() -> None:
    """ldnrev 85 - 4 halted - 1 more E&W = 80; ldnmom 1797 - 36 E&W full sessions; ecbfix 1797 -
    17 TARGET full sessions; tkypre and tkypost: the Tokyo tables on full sessions."""
    assert len(ldnrev.event_dates(cal_tables.MONTH_ENDS, cal_tables.FX_FULL_SESSIONS,
                                  cal_tables.EW_BANK_HOLIDAYS)) == 80
    assert len(ldnmom.event_dates(cal_tables.FX_FULL_SESSIONS, cal_tables.EW_BANK_HOLIDAYS)) == 1761
    assert len(ecbfix.event_dates(cal_tables.FX_FULL_SESSIONS,
                                  cal_tables.TGT_CLOSING_DAYS)) == 1780
    assert len(tkypre.event_dates(cal_tables.GOTOBI_OR_TOKYO_MONTH_END,
                                  cal_tables.FX_FULL_SESSIONS)) == 378
    assert len(tkypost.event_dates(cal_tables.TOKYO_BUSINESS_DAYS,
                                   cal_tables.FX_FULL_SESSIONS)) == 1681
    research = [d for d in ldnrev.event_dates(cal_tables.MONTH_ENDS, cal_tables.FX_FULL_SESSIONS,
                                              cal_tables.EW_BANK_HOLIDAYS)
                if RESEARCH[0] <= d <= RESEARCH[1]]
    assert len(research) == 13  # 14 month-ends 2025-04..2026-05 less 2025-11-28 (halted)


def test_no_nominal_fill_on_any_event_date_meets_the_frozen_fill_guard() -> None:
    """The frozen calendar's rows naming 6E, 6J, 6S are NFP 07:30 CT and FOMC 13:00 CT (no fix
    instant is a release row, specs line 29): D9.5a leaves every nominal fill of the five members
    alone on every event date (a missing bar can still move a fill, S0.7)."""
    raw = json.loads(RELEASE_CALENDAR_JSON.read_text(encoding="utf-8"))
    assert _sha(RELEASE_CALENDAR_JSON) == RELEASE_CALENDAR_SHA256
    frozen = release_calendar_from_dict(raw, RELEASE_CALENDAR_SHA256, "frozen")
    rows = set()
    for r in raw["releases"]:
        if {"6E", "6J", "6S"} & set(r["products"]):
            utc = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
            rows.add((r["release"], f"{utc.astimezone(CT):%H:%M}"))
    assert rows == {("NFP", "07:30"), ("FOMC", "13:00")}
    checked = 0
    for module, roots in ((ldnrev, ("6E", "6J", "6S")), (ldnmom, ("6E", "6J")),
                          (tkypre, ("6J",)), (tkypost, ("6J",))):
        for root in roots:
            for plan in make(module, root)._core.plans.values():
                for ns in (plan.entry_ns + 60 * NS, plan.exit_ns + 60 * NS):
                    assert not frozen.in_fill_guard(root, ns)
                    checked += 1
    for plan in ecbfix.make_6e()._plans.values():
        for ns in (plan.leg1_entry_ns, plan.leg1_exit_ns, plan.leg2_entry_ns, plan.leg2_exit_ns):
            assert not frozen.in_fill_guard("6E", ns + 60 * NS)
            checked += 1
    assert checked == 2 * (3 * 80 + 2 * 1761 + 378 + 1681) + 4 * 1780


# ---------------------------------------------------------------- declarations ----
@pytest.mark.parametrize("name", CODER_B_FILES)
def test_every_coder_b_file_passes_the_freeze_static_check(name: str) -> None:
    rel = f"strategy/members/k3/{name}"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K3") == []


@pytest.mark.parametrize("name", CODER_B_FILES)
def test_no_member_file_uses_a_zone_other_than_the_ct_clock(name: str) -> None:
    """K3-L-02: the fix instants are literal tables; only the CT clock (America/Chicago, S0.4) is
    a zone at run time, and only in _event_common."""
    text = (K3_DIR / name).read_text(encoding="utf-8")
    zones = re.findall(r'ZoneInfo\("([^"]+)"\)', text)
    assert zones == (["America/Chicago"] if name == "_event_common.py" else [])
    tree = ast.parse(text)
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
                for a in n.names if n.module == "zoneinfo"}
    assert imported == ({"ZoneInfo"} if name == "_event_common.py" else set())


@pytest.mark.parametrize("decl", DECLS, ids=lambda d: f"{d[0].MEMBER_ID}-{d[2]}")
def test_factories_name_the_label_and_trade_one_leg(decl: tuple) -> None:
    module, factory, root, _ = decl
    member = vars(module)[factory]()
    assert isinstance(member, StageEMember)
    assert member.name == f"{module.MEMBER_ID} {root}"  # S0.2
    assert member.root == root and member.legs == (LegSpec(root, True),)  # S0.1
    assert list(member.trading_windows) == [root]
    assert vars(module)[factory]() is not member  # every call starts from fresh state


def test_each_module_declares_exactly_its_exposures() -> None:
    expected = {ldnrev: ("6E", "6J", "6S"), ldnmom: ("6E", "6J"), ecbfix: ("6E",),
                tkypre: ("6J",), tkypost: ("6J",)}
    for module, roots in expected.items():
        assert roots == module.EXPOSURES
        factories = sorted(n for n in vars(module) if n.startswith("make_"))
        assert factories == sorted(f"make_{r.lower()}" for r in roots)
    classes = (ldnrev.LdnRev, ldnmom.LdnMom, ecbfix.EcbFix, tkypre.TkyPre, tkypost.TkyPost)
    for cls, roots in zip(classes, expected.values(), strict=True):
        for root in set(K3_ROOTS) - set(roots):
            with pytest.raises(ValueError):
                cls(root)


def test_trading_windows_are_the_s0_12_intervals() -> None:
    assert ldnrev.make_6e().trading_windows["6E"] == (
        TradingInterval(time(9, 49), time(10, 21)), TradingInterval(time(10, 49), time(11, 21)))
    assert ldnmom.make_6j().trading_windows["6J"] == (
        TradingInterval(time(9, 45), time(10, 6)), TradingInterval(time(10, 45), time(11, 6)))
    assert ecbfix.make_6e().trading_windows["6E"] == (TradingInterval(time(0, 59),
                                                                      time(15, 6)),)
    assert tkypre.make_6j().trading_windows["6J"] == (
        TradingInterval(time(17, 29), time(19, 56), -1, -1),)
    assert tkypost.make_6j().trading_windows["6J"] == (
        TradingInterval(time(18, 55), time(1, 1), -1, 0),)


def test_size_is_the_frozen_q_c_and_prices_are_integer_ticks() -> None:
    frozen = load_frozen_tables()
    for root in ("6E", "6J", "6S"):
        assert frozen.vehicles[root].q_c == 1  # S0.3
        assert frozen.day_session_ct[root] == (time(7, 20), time(14, 0))
    assert product("6E").vendor_tick == Decimal("0.00005")
    assert product("6J").vendor_tick == Decimal("0.0000005")
    assert product("6S").vendor_tick == Decimal("0.00005")
    assert price_ticks(1.10005, product("6E").vendor_tick) == 22001  # S0.10
    assert price_ticks(0.0067005, product("6J").vendor_tick) == 13401
    bar = bar_at("6E", date(2025, 6, 3), hm(9, 45), (3, 5, -2, 1))
    assert field_ticks(bar, "open", product("6E").vendor_tick) == base_ticks("6E") + 3
    assert field_ticks(bar, "close", product("6E").vendor_tick) == base_ticks("6E") + 1
    with pytest.raises(ValueError):
        field_ticks(bar, "high", product("6E").vendor_tick)
    assert clock_minute("19:55") == hm(19, 55) and clock_minute(time(0, 59)) == 59
    assert ct_open_ns(date(2025, 3, 9), hm(19, 55)) == ns_at(date(2025, 3, 10), eve(19, 55))


def test_the_8_declarations_freeze_and_verify_under_tmp_path(tmp_path: Path) -> None:
    """Coder B's declarations (S0.2 ordinals 22-26 and 28-30) pass the real freeze code; the
    freeze is written under tmp_path only (never the repository's write-once file)."""
    members_dir = tmp_path / "strategy" / "members"
    (members_dir / "k3").mkdir(parents=True)
    (members_dir / "__init__.py").write_bytes(b"")
    (members_dir / "k3" / "__init__.py").write_bytes(b"")
    for name in CODER_B_FILES:
        shutil.copyfile(K3_DIR / name, members_dir / "k3" / name)
    decls = [MemberDecl(f"{m.MEMBER_ID} {root}", ordinal, m.__name__, factory,
                        (LegSpec(root, True),)) for m, factory, root, ordinal in DECLS]
    write_cluster_freeze("K3", decls, tmp_path)
    freeze = load_cluster_freeze("K3", tmp_path)
    verify_cluster_code(freeze)
    assert [(m.label, m.ordinal) for m in freeze.members] == [
        ("K3-ldnrev-01 6E", 22), ("K3-ldnrev-01 6J", 23), ("K3-ldnrev-01 6S", 24),
        ("K3-ldnmom-01 6E", 25), ("K3-ldnmom-01 6J", 26), ("K3-ecbfix-01 6E", 28),
        ("K3-tkypre-01 6J", 29), ("K3-tkypost-01 6J", 30)]


PROBES = (
    (ldnrev, "6E", date(2025, 6, 30), hm(9, 49)), (ldnrev, "6J", date(2025, 6, 30), hm(10, 4)),
    (ldnmom, "6E", date(2025, 6, 3), hm(9, 47)), (ecbfix, "6E", date(2025, 6, 3), hm(0, 59)),
    (ecbfix, "6E", date(2025, 6, 3), hm(7, 15)), (tkypre, "6J", date(2025, 6, 5), eve(17, 29)),
    (tkypost, "6J", date(2025, 6, 4), eve(19, 55)))


@pytest.mark.parametrize("probe", PROBES, ids=lambda p: f"{p[0].MEMBER_ID}-{p[1]}-{p[3]}")
def test_a_none_bar_is_no_decision_and_changes_no_state(probe: tuple) -> None:
    module, root, day, key = probe
    member = make(module, root)
    before = state_of(member)
    for position in (0, -1, 1):
        assert member.on_minute(view_of(root, ns_at(day, key), None),
                                account_of(root, position)) == ()
    assert state_of(member) == before


def test_fix_event_core_one_chance_no_entry_while_pending_or_on_other_dates() -> None:
    """S0.6 on the shared core: the named entry bar only, once; never while an order is
    pending; a date without a plan is not traded."""
    day = date(2025, 6, 3)
    plan = Plan((), ns_at(day, hm(10, 4)), ns_at(day, hm(10, 19)))
    core = FixEvent("6E", {day: plan}, lambda ticks: "sell")
    entry = bar_at("6E", day, hm(10, 4))
    assert core.on_minute(view_of("6E", entry.ts_event_ns, entry), account_of("6E",
                                                                             pending=-1)) == ()
    assert core.on_minute(view_of("6E", entry.ts_event_ns, entry), account_of("6E")) == ()
    fresh = FixEvent("6E", {day: plan}, lambda ticks: "sell")
    other = bar_at("6E", day, hm(10, 3))
    assert fresh.on_minute(view_of("6E", other.ts_event_ns, other), account_of("6E")) == ()
    first = fresh.on_minute(view_of("6E", entry.ts_event_ns, entry), account_of("6E"))
    assert [(i.side, i.quantity) for i in first] == [("sell", 1)]
    assert fresh.on_minute(view_of("6E", entry.ts_event_ns, entry), account_of("6E")) == ()
    elsewhere = bar_at("6E", date(2025, 6, 4), hm(10, 4))
    blank = FixEvent("6E", {day: plan}, lambda ticks: "sell")
    assert blank.on_minute(view_of("6E", elsewhere.ts_event_ns, elsewhere),
                           account_of("6E")) == ()
    exit_bar = bar_at("6E", day, hm(10, 19))
    assert fresh.on_minute(view_of("6E", exit_bar.ts_event_ns, exit_bar),
                           account_of("6E", -1, pending=1)) == ()  # an exit is pending
    out = fresh.on_minute(view_of("6E", exit_bar.ts_event_ns, exit_bar), account_of("6E", -1))
    assert [(i.side, i.quantity) for i in out] == [("buy", 1)]
