"""The 2010-2019 swap context of E20-B1 (reports/stage_e20_plan.md sections 2, 10 and 10.1; tables
S1-S12 of reports/stage_e20_briefs/backward_swap_table.md). It opens no store: every source is a
calendar or release file under data/calendars/hist2010 or reports/, read by path and sha256.

``backward_tables()`` builds every table from its pinned source with the frozen generators' rules
(each rule is quoted from its generator, file:line in the swap table, and reproduces the frozen
2019-on table on the 2019-05 overlap; tests check that):
- S1: the seven hist group calendars (data.hist_calendar; E.16's livestock calendar is the
  seventh), the metals one carrying the frozen calendar's product sub-group map (ruling 1);
- S2: rules.sessions holidays and scheduled late opens per group, livestock included (ruling 1);
- S3: Rule H-1 Topstep rows from the hist equity calendar (c1_replication.tables.h1_rows) and the
  30-minute early-close lead for 2010-2018 (C1's L-E5-2);
- S4: EQUITY_FULL_SESSIONS (gen_k1_tables.py:138-150: an equity trade date with no early halt and
  F = 15:08, computed under S1-S3);
- S5: TREASURY_AUCTIONS from EC-AUC (gen_k2_releases.py build(): -2Y/-5Y/-10Y/-30Y rows, T_a in CT;
  the tenor from the row id, so a cross-tenor reopening keeps its original-term label, ruling 7);
- S6: k2 monthend EVENT_DATES (gen_k2_month_end.py month_end_rows() on the hist rates calendar);
- S7: the WPSR table in eiafade's schema (gen_k4_releases.py wpsr_rows(); WPSR-2012-11-01 has no
  instant and is left out, ruling 5) behind a make_mcl factory swap;
- S8: the NGS table (c1_replication.tables.load_releases) behind a make_ng factory swap;
- S9: ENERGY_FULL_SESSIONS (E.14's file, checked against the rule by C1's loader);
- S10: METALS_FULL_SESSIONS (gen_k5_calendar.py's rule on the hist metals calendar).
Every derived table is the hist rows before 2019-05-01 plus the frozen rows from 2019-05-01.

``backward_context(tables)`` swaps each attribute in ``PATCHES`` by setattr while the block runs,
clears every functools cache of the modules that read a calendar on entry and on exit, restores
every original object on exit (also on an exception), and refuses nesting (pattern of
c1_replication/context.hist_tables, extended to all seven groups and the KEPT members' tables).

S11 (the release calendar argument) is ``backward_release_rules``: E.16's combined rows
(base_rules.costs.build_release_rules: the frozen D8 rows from 2019-05-01, E.14's FOMC/NGS/WPSR rows
and EC-AUC's auction rows before it), with the fallback minutes of every release type that touches
one of the 17 vehicles in the frozen calendar and has no 2010-2019 rows (ruling 4).

The rulings that act only in the B1 evaluation (not built in Step 6; unused by the search) are
functions here: ``late_always_applicable_mask`` (ruling 2), ``session_end_exits`` (ruling 3),
``apply_fallback_costs`` (ruling 4), ``unsourced_release_exclusions`` (ruling 5),
``unsourced_calendar_exclusions`` (ruling 6), ``reopening_record`` (ruling 7, recorded only).
"""

from __future__ import annotations

import dataclasses
import importlib
import json
import threading
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from pattern_search import constants as K
from pattern_search import guard  # noqa: F401  (F3)

CT = ZoneInfo("America/Chicago")
NS_MIN = 60_000_000_000
FROZEN_FIRST = date(2019, 5, 1)  # the 2019-on tables and calendars take over from this date
B1_LAST = date(2019, 4, 30)  # the stores' last date (plan 2)
B1_FIRST = MappingProxyType({  # plan 2: the later of E.16's window start and R-S4's listing
    **{p: date(2010, 7, 1) for p in K.PATH_ROOTS},
    "TN": date(2016, 1, 11), "RTY": date(2017, 7, 10), "HE": date(2017, 7, 1),
    "LE": date(2014, 12, 15)})
HIST_GROUPS = ("equity", "rates", "fx", "energy", "metals", "grains", "livestock")
SOURCES = MappingProxyType({  # path, sha256 (reports/stage_e20_briefs/backward_swap_table.json)
    "hist_equity": ("data/calendars/hist2010/equity.json",
                    "b12aee433635bc8334adb15d8f06c21255b0cb24889ea123a4d4375fb22657be"),
    "hist_rates": ("data/calendars/hist2010/rates.json",
                   "099ac84eb88c4e2bef67814e668d04fc4e88ad2ef1b3ea52114c53abd25382a4"),
    "hist_fx": ("data/calendars/hist2010/fx.json",
                "463c256b38a530fb1b150b542db21449d704d5b4cfa5308bd018d2e0e05b0591"),
    "hist_energy": ("data/calendars/hist2010/energy.json",
                    "c7a58e904571028f412dfe7f1039aa3c6cc89da8117e112e99a39d6d0bdeee6c"),
    "hist_metals": ("data/calendars/hist2010/metals.json",
                    "7eb64ead635aafb932422f5f31d2ff483ed22247ae0eaacccc71f798386991e9"),
    "hist_grains": ("data/calendars/hist2010/grains.json",
                    "1197496f224636e7330f6da0b50ae45063ffb085fc780e95b54bc078955a7a61"),
    "hist_livestock": ("data/calendars/hist2010/livestock.json",
                       "802a4dd98a71776af58748c43c2a70772a966a2e37dd08e32fef1ebfe023ba5d"),
    "e14_releases": ("reports/stage_e14_cal_releases.json",
                     "9a051211fe381cd2d1894180259624cc6729e8ddc89649e398b59e13666080a7"),
    "e14_energy_full": ("reports/stage_e14_cal_energy_full_sessions.json",
                        "3f2a273a61613a73867929160d777367e06749b963fcf18b0b27e3f325083d74"),
    "ec_auc": ("reports/stage_e16_calendars/ec_auc_2010_2019.json",
               "e3b5f4522dad8e8dd9ad4a1f4fa04750bab769b089c54ced6f67a01a5a00b9e5"),
    "e2b_frozen": ("reports/stage_e2b_release_calendar.json",
                   "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"),
})
TENORS = ("2Y", "5Y", "10Y", "30Y")  # gen_k2_releases.py:30
STANDARD_WPSR_ET = "10:30"  # gen_k4_releases.py:48
WEDNESDAY = 2
EQUITY_REGULAR_F = time(15, 8)  # gen_k1_tables.py REGULAR_F
EQUITY_ROOTS = ("MNQ", "M2K", "MYM")  # gen_k1_tables.py ROOTS: one F for the three

PATCHES: tuple[tuple[str, str], ...] = (
    ("data.group_session", "load_group_calendar"),  # S1
    ("ml_route.inputs", "_group_calendar"),  # S1
    ("rules.sessions", "_DEFAULT"),  # S2
    ("rules.sessions", "_DEFAULT_LATE"),  # S2
    ("rules.sessions", "TOPSTEP_HOLIDAYS"),  # S3
    ("rules.sessions", "TOPSTEP_EARLY_CLOSE_LEAD"),  # S3
    ("strategy.members.k1._calendar", "EQUITY_FULL_SESSIONS"),  # S4
    ("strategy.members.k2._releases", "TREASURY_AUCTIONS"),  # S5
    ("strategy.members.k2.monthend", "EVENT_DATES"),  # S6
    ("strategy.members.k4.eiafade", "make_mcl"),  # S7
    ("strategy.members.k4.ngpre", "make_ng"),  # S8
    ("strategy.members.k4._calendar", "ENERGY_FULL_SESSIONS"),  # S9
    ("strategy.members.k4.ovr", "ENERGY_FULL_SESSIONS"),
    ("strategy.members.k4.ovr", "_FULL_SESSIONS"),
    ("strategy.members.k4.ovr", "_FULL_ORDINALS"),
    ("strategy.members.k5._calendar", "METALS_FULL_SESSIONS"),  # S10
    ("strategy.members.k5.ovr", "METALS_FULL_SESSIONS"),
    ("strategy.members.k5.ovr", "_FULL_SESSIONS"),
    ("strategy.members.k5.ovr", "_FULL_ORDINALS"),
)
CALENDAR_PATCHES = PATCHES[:6]
CACHE_MODULES: tuple[str, ...] = (
    "ml_route.inputs", "ml_route_v2.clock", "ml_route_v2.synthetic", "ml_route_v2.targets",
    "ml_route_v2.signals._core", "ml_route_v2.signals._daily", "ml_route_v2.signals._events",
    "ml_route_v2.signals.generic", "ml_route_v2.signals.ports", "ml_route_v2.signals.k1",
    "ml_route_v2.signals.k2", "ml_route_v2.signals.k3", "ml_route_v2.signals.k4",
    "ml_route_v2.signals.k5", "ml_route_v2.signals.k6", "ml_route_v2.signals.k7",
    "ml_route_v2.signals.k8", "ml_route_v2.signals.k9", "data.group_session", "rules.sessions",
    "strategy.members.k1._calendar", "strategy.members.k2._releases",
    "strategy.members.k2.monthend", "strategy.members.k4.eiafade", "strategy.members.k4.ngpre",
    "strategy.members.k4.ovr", "strategy.members.k5.ovr",
)
_LOCK = threading.Lock()
_ACTIVE = {"on": False}


class BackwardError(RuntimeError):
    """A 2010-2019 table is missing, malformed or disagrees with the frozen table on the overlap,
    or the context is already active."""


def _repo() -> Path:
    from data.config import REPO_ROOT

    return Path(REPO_ROOT)


def read_source(key: str) -> bytes:
    """A pinned source's bytes (sha256 checked)."""
    import hashlib

    rel, sha = SOURCES[key]
    path = _repo() / rel
    if not path.is_file():
        raise BackwardError(f"{rel} does not exist")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise BackwardError(f"{rel}: sha256 is not the pinned {sha[:12]}...")
    return raw


# ------------------------------------------------------------------ the tables ----
@dataclass(frozen=True)
class BackwardTables:
    calendars: Mapping[str, Any]  # group -> HistGroupCalendar (metals with the frozen map)
    holidays: Mapping[str, Any]  # rules.sessions._DEFAULT replacement
    late_opens: Mapping[str, Any]  # rules.sessions._DEFAULT_LATE replacement
    topstep_rows: Mapping[date, Any]  # hist Rule H-1 rows plus the frozen rows
    topstep_leads: Mapping[int, Any]
    equity_full: tuple[str, ...] = ()
    auctions: tuple[tuple[str, str, str], ...] = ()
    month_end_dates: frozenset[date] = frozenset()
    wpsr: tuple[tuple[str, str, int, bool], ...] = ()
    ngs: tuple[tuple[str, str], ...] = ()
    energy_full: tuple[str, ...] = ()
    metals_full: tuple[str, ...] = ()
    record: Mapping[str, Any] = field(default_factory=dict)


def hist_calendars() -> dict[str, Any]:
    """The seven hist calendars (S1), the metals one with the frozen sub-group map (ruling 1)."""
    from data.group_session import load_group_calendar
    from data.hist_calendar import load_hist_group_calendar

    out = {}
    for g in HIST_GROUPS:
        out[g] = load_hist_group_calendar(g, expected_sha256=SOURCES[f"hist_{g}"][1])
    frozen_map = dict(load_group_calendar("metals").subgroup_of_product)
    if not frozen_map:
        raise BackwardError("the frozen metals calendar has no product sub-group map")
    out["metals"] = dataclasses.replace(out["metals"], subgroup_of_product=frozen_map)
    return out


def _calendar_tables(calendars: Mapping[str, Any]) -> BackwardTables:
    from c1_replication.constants import H1_LEAD, H1_LEAD_YEARS
    from c1_replication.tables import h1_rows
    from rules import sessions

    rows = h1_rows(calendars["equity"])
    overlap = set(rows) & set(sessions.TOPSTEP_HOLIDAYS)
    if overlap:
        raise BackwardError(f"Rule H-1 rows overlap the frozen Topstep rows: {sorted(overlap)[:3]}")
    return BackwardTables(
        calendars=MappingProxyType(dict(calendars)),
        holidays=MappingProxyType({g: dict(c.holidays) for g, c in calendars.items()}),
        late_opens=MappingProxyType({g: dict(getattr(c, "scheduled_late_opens", {}))
                                     for g, c in calendars.items()}),
        topstep_rows=MappingProxyType({**rows, **sessions.TOPSTEP_HOLIDAYS}),
        topstep_leads=MappingProxyType({**{y: H1_LEAD for y in H1_LEAD_YEARS},
                                        **sessions.TOPSTEP_EARLY_CLOSE_LEAD}),
        record={"h1_rows": len(rows)})


def _ct(instant_utc: str) -> datetime:
    return datetime.fromisoformat(instant_utc.replace("Z", "+00:00")).astimezone(CT)


def derive_equity_full(cal: Any) -> tuple[str, ...]:
    """gen_k1_tables.py:138-150 on ``cal`` (run under S1-S3): no early halt and F = 15:08."""
    from data.group_session import trade_dates_between
    from rules import sessions

    first, last = cal.coverage
    out = []
    for d in trade_dates_between(cal, first, last):
        flats = {r: sessions.flatten_time_ct(r, d) for r in EQUITY_ROOTS}
        if len(set(flats.values())) != 1:
            raise BackwardError(f"{d}: the equity roots have different F {flats}")
        f = flats[EQUITY_ROOTS[0]]
        no_halt, regular = cal.early_halt_ct(d) is None, f == EQUITY_REGULAR_F
        if no_halt != regular:
            raise BackwardError(f"{d}: early halt and F disagree (gen_k1_tables's assert)")
        if no_halt and regular:
            out.append(d.isoformat())
    return tuple(out)


def derive_auctions(raw: bytes) -> tuple[tuple[str, str, str], ...]:
    """gen_k2_releases.py build()'s auction rows from EC-AUC (no DROPPED rows before 2019-05)."""
    doc = json.loads(raw)
    rows = doc.get("releases", doc.get("rows"))
    order = {t: i for i, t in enumerate(TENORS)}
    out = []
    for e in rows:
        if e.get("release") != "TREASURY_AUCTION":
            continue
        tenor = str(e["id"]).rsplit("-", 1)[1]
        if tenor not in TENORS:
            continue
        ct = _ct(e["instant_utc"])
        if ct.date().isoformat() != e["date"]:
            raise BackwardError(f"{e['id']}: the CT date differs from the row date")
        out.append((e["date"], tenor, ct.strftime("%H:%M")))
    keys = [(d, t) for d, t, _ in out]
    if len(keys) != len(set(keys)):
        raise BackwardError("two auctions of one tenor on one date")
    return tuple(sorted(out, key=lambda a: (a[0], order[a[1]])))


def derive_month_end(cal: Any) -> tuple[tuple[str, str, str], ...]:
    """gen_k2_month_end.py month_end_rows() on ``cal``: (YYYY-MM, N-1, N) per covered month."""
    from data.group_session import previous_trade_date, trade_dates_between

    first, last = cal.coverage
    rows = []
    year, month = first.year, first.month
    while date(year, month, 1) <= last:
        start = date(year, month, 1)
        nxt = date(year + (month == 12), month % 12 + 1, 1)
        days = trade_dates_between(cal, start, nxt - timedelta(days=1))
        if days and cal.covers(days[-1]):
            n = days[-1]
            n1 = previous_trade_date(cal, n)
            if n1 is None or not cal.covers(n1):
                raise BackwardError(f"{n}: no covered previous trade date")
            rows.append((f"{year:04d}-{month:02d}", n1.isoformat(), n.isoformat()))
        year, month = nxt.year, nxt.month
    return tuple(rows)


def derive_wpsr(raw: bytes) -> tuple[tuple[tuple[str, str, int, bool], ...], tuple[str, ...]]:
    """gen_k4_releases.py wpsr_rows() on E.14's rows; (rows, dates without an instant)."""
    doc = json.loads(raw)
    out, untimed = [], []
    for r in doc["releases"]:
        if r.get("release") != "WPSR":
            continue
        if not r.get("instant_utc"):
            untimed.append(str(r["date"]))
            continue
        ct = _ct(r["instant_utc"])
        if ct.date().isoformat() != r["date"] or r.get("tz") != "America/New_York":
            raise BackwardError(f"{r['id']}: CT date or time zone differs (wpsr_rows' assert)")
        weekday = date.fromisoformat(r["date"]).weekday()
        standard = weekday == WEDNESDAY and r.get("time_local") == STANDARD_WPSR_ET
        out.append((r["date"], ct.strftime("%H:%M"), weekday, standard))
    out.sort()
    if len({row[0] for row in out}) != len(out):
        raise BackwardError("two WPSR rows on one date")
    return tuple(out), tuple(sorted(untimed))


def _before(rows: Any, key: Callable[[Any], str]) -> list[Any]:
    return [r for r in rows if key(r) < FROZEN_FIRST.isoformat()]


def backward_tables() -> BackwardTables:
    """Every table of the swap context (module docstring), hist rows before 2019-05-01 plus the
    frozen rows from 2019-05-01."""
    from c1_replication.tables import full_sessions_rule, load_full_sessions, load_releases
    from strategy.members.k1._calendar import EQUITY_FULL_SESSIONS
    from strategy.members.k2._releases import TREASURY_AUCTIONS
    from strategy.members.k2.monthend import EVENT_DATES
    from strategy.members.k4._calendar import ENERGY_FULL_SESSIONS
    from strategy.members.k4._releases import NGS, WPSR
    from strategy.members.k5._calendar import METALS_FULL_SESSIONS

    cals = hist_calendars()
    base = _calendar_tables(cals)
    with backward_context(base, patches=CALENDAR_PATCHES):
        equity = derive_equity_full(cals["equity"])
    auctions = derive_auctions(read_source("ec_auc"))
    months = derive_month_end(cals["rates"])
    wpsr, untimed = derive_wpsr(read_source("e14_releases"))
    rel_path, rel_sha = SOURCES["e14_releases"]
    ngs = load_releases(_repo() / rel_path, rel_sha).ngs_table
    e_path, e_sha = SOURCES["e14_energy_full"]
    energy = load_full_sessions(_repo() / e_path, e_sha, cals["energy"])
    first, last = cals["metals"].coverage
    metals = full_sessions_rule(cals["metals"], first, last)
    hist_months = {date.fromisoformat(x) for _, n1, n in months for x in (n1, n)}
    return dataclasses.replace(
        base,
        equity_full=tuple(_before(equity, str)) + tuple(EQUITY_FULL_SESSIONS),
        auctions=tuple(_before(auctions, lambda r: r[0])) + tuple(TREASURY_AUCTIONS),
        month_end_dates=frozenset({d for d in hist_months if d < FROZEN_FIRST}
                                  | set(EVENT_DATES)),
        wpsr=tuple(_before(wpsr, lambda r: r[0])) + tuple(WPSR),
        ngs=tuple(_before(ngs, lambda r: r[0])) + tuple(NGS),
        energy_full=tuple(_before(energy, str)) + tuple(ENERGY_FULL_SESSIONS),
        metals_full=tuple(_before(metals, str)) + tuple(METALS_FULL_SESSIONS),
        record={**dict(base.record), "derived_hist": {
            "equity_full": len(equity), "auctions": len(auctions), "month_end_rows": len(months),
            "wpsr": len(wpsr), "wpsr_untimed": list(untimed), "ngs": len(ngs),
            "energy_full": len(energy), "metals_full": len(metals)},
            "overlap": overlap_record(equity, auctions, months, wpsr, ngs, energy, metals)})


def overlap_record(equity: Any, auctions: Any, months: Any, wpsr: Any, ngs: Any, energy: Any,
                   metals: Any) -> dict[str, bool]:
    """Each derived hist table equals the frozen table on 2019-05 (auctions 2019-05..06)."""
    from strategy.members.k1._calendar import EQUITY_FULL_SESSIONS
    from strategy.members.k2._month_end import MONTH_END
    from strategy.members.k2._releases import TREASURY_AUCTIONS
    from strategy.members.k4._calendar import ENERGY_FULL_SESSIONS
    from strategy.members.k4._releases import NGS, WPSR
    from strategy.members.k5._calendar import METALS_FULL_SESSIONS

    def may(rows: Any, key: Callable[[Any], str], hi: str = "2019-05-31") -> list[Any]:
        return [tuple(r) if isinstance(r, (list, tuple)) else r for r in rows
                if "2019-05-01" <= key(r) <= hi]

    return {
        "equity_full": may(equity, str) == may(EQUITY_FULL_SESSIONS, str),
        "auctions": may(auctions, lambda r: r[0], "2019-06-30")
        == may(TREASURY_AUCTIONS, lambda r: r[0], "2019-06-30"),
        "month_end": [r for r in months if r[0] == "2019-05"]
        == [tuple(r) for r in MONTH_END if r[0] == "2019-05"],
        "wpsr": may(wpsr, lambda r: r[0]) == may(WPSR, lambda r: r[0]),
        "ngs": may(ngs, lambda r: r[0]) == may(NGS, lambda r: r[0]),
        "energy_full": may(energy, str) == may(ENERGY_FULL_SESSIONS, str),
        "metals_full": may(metals, str) == may(METALS_FULL_SESSIONS, str),
    }


# ------------------------------------------------------------------ the context ----
def _module(name: str) -> Any:
    return importlib.import_module(name)


def clear_caches() -> list[str]:
    cleared = []
    for name in CACHE_MODULES:
        mod = _module(name)
        for attr, obj in sorted(vars(mod).items()):
            fn = getattr(obj, "cache_clear", None)
            if callable(fn) and getattr(obj, "__module__", None) == name:
                fn()
                cleared.append(f"{name}.{attr}")
    return cleared


def _loader(calendars: Mapping[str, Any]) -> Callable[[str], Any]:
    def load(group: str) -> Any:
        from data.hist_calendar import HistCalendarError

        cal = calendars.get(group)
        if cal is None:
            raise HistCalendarError(f"E20-B1: no hist calendar for group {group!r}")
        return cal

    return load


def replacement_values(t: BackwardTables) -> dict[tuple[str, str], Any]:
    from strategy.members.k4 import eiafade, ngpre

    loader = _loader(MappingProxyType(dict(t.calendars)))
    wpsr, ngs = tuple(t.wpsr), tuple(t.ngs)
    energy = tuple(date.fromisoformat(d) for d in t.energy_full)
    metals = tuple(date.fromisoformat(d) for d in t.metals_full)

    def make_mcl() -> Any:
        return eiafade.EiaFade("MCL", wpsr=wpsr)

    def make_ng() -> Any:
        return ngpre.NgPre("NG", ngs=ngs)

    return {
        ("data.group_session", "load_group_calendar"): loader,
        ("ml_route.inputs", "_group_calendar"): loader,
        ("rules.sessions", "_DEFAULT"): {g: dict(v) for g, v in t.holidays.items()},
        ("rules.sessions", "_DEFAULT_LATE"): {g: dict(v) for g, v in t.late_opens.items()},
        ("rules.sessions", "TOPSTEP_HOLIDAYS"): dict(t.topstep_rows),
        ("rules.sessions", "TOPSTEP_EARLY_CLOSE_LEAD"): dict(t.topstep_leads),
        ("strategy.members.k1._calendar", "EQUITY_FULL_SESSIONS"): tuple(t.equity_full),
        ("strategy.members.k2._releases", "TREASURY_AUCTIONS"): tuple(t.auctions),
        ("strategy.members.k2.monthend", "EVENT_DATES"): frozenset(t.month_end_dates),
        ("strategy.members.k4.eiafade", "make_mcl"): make_mcl,
        ("strategy.members.k4.ngpre", "make_ng"): make_ng,
        ("strategy.members.k4._calendar", "ENERGY_FULL_SESSIONS"): tuple(t.energy_full),
        ("strategy.members.k4.ovr", "ENERGY_FULL_SESSIONS"): tuple(t.energy_full),
        ("strategy.members.k4.ovr", "_FULL_SESSIONS"): energy,
        ("strategy.members.k4.ovr", "_FULL_ORDINALS"): np.array([d.toordinal() for d in energy],
                                                               dtype=np.int64),
        ("strategy.members.k5._calendar", "METALS_FULL_SESSIONS"): tuple(t.metals_full),
        ("strategy.members.k5.ovr", "METALS_FULL_SESSIONS"): tuple(t.metals_full),
        ("strategy.members.k5.ovr", "_FULL_SESSIONS"): metals,
        ("strategy.members.k5.ovr", "_FULL_ORDINALS"): np.array([d.toordinal() for d in metals],
                                                               dtype=np.int64),
    }


def originals() -> dict[tuple[str, str], Any]:
    return {(m, a): getattr(_module(m), a) for m, a in PATCHES}


@contextmanager
def backward_context(tables: BackwardTables, *, patches: tuple[tuple[str, str], ...] = PATCHES
                     ) -> Iterator[dict[tuple[str, str], Any]]:
    """Swap ``patches`` for the 2010-2019 tables while the block runs (module docstring)."""
    with _LOCK:
        if _ACTIVE["on"]:
            raise BackwardError("the E20-B1 swap context is already active (no nesting)")
        _ACTIVE["on"] = True
    saved: dict[tuple[str, str], Any] = {}
    try:
        values = replacement_values(tables) if patches == PATCHES else {
            k: v for k, v in _calendar_values(tables).items() if k in patches}
        clear_caches()
        for key in patches:
            mod = _module(key[0])
            saved[key] = getattr(mod, key[1])
            setattr(mod, key[1], values[key])
        clear_caches()
        yield values
    finally:
        for key in reversed(patches):
            if key in saved:
                setattr(_module(key[0]), key[1], saved[key])
        clear_caches()
        with _LOCK:
            _ACTIVE["on"] = False


def _calendar_values(t: BackwardTables) -> dict[tuple[str, str], Any]:
    loader = _loader(MappingProxyType(dict(t.calendars)))
    return {
        ("data.group_session", "load_group_calendar"): loader,
        ("ml_route.inputs", "_group_calendar"): loader,
        ("rules.sessions", "_DEFAULT"): {g: dict(v) for g, v in t.holidays.items()},
        ("rules.sessions", "_DEFAULT_LATE"): {g: dict(v) for g, v in t.late_opens.items()},
        ("rules.sessions", "TOPSTEP_HOLIDAYS"): dict(t.topstep_rows),
        ("rules.sessions", "TOPSTEP_EARLY_CLOSE_LEAD"): dict(t.topstep_leads),
    }


def is_active() -> bool:
    return bool(_ACTIVE["on"])


# ------------------------------------------------------------------ S11, ruling 4 ----
def touching_types(vehicles: tuple[str, ...] = K.VEHICLES) -> dict[str, list[str]]:
    """Release type -> the plan roots (paths or vehicles) its frozen 2019-05..2024-02 rows
    concern (ruling 4: types that touch a vehicle in the frozen calendar)."""
    doc = json.loads(read_source("e2b_frozen"))
    roots = set(vehicles) | {K.VEHICLE_PATHS[v] for v in vehicles}
    out: dict[str, set[str]] = {}
    for r in doc["releases"]:
        if not ("2019-05-01" <= str(r["date"]) <= "2024-02-29") or not r.get("instant_utc"):
            continue
        hit = roots & set(r.get("products") or ())
        if hit:
            out.setdefault(str(r["release"]), set()).update(hit)
    return {k: sorted(v) for k, v in sorted(out.items())}


def backward_release_rules() -> Any:
    """E.16's ReleaseRules over the combined rows (module docstring, S11 and ruling 4)."""
    from base_rules.costs import build_release_rules

    for key in ("e2b_frozen", "e14_releases", "ec_auc"):
        read_source(key)  # the pinned bytes (build_release_rules reads the same paths)
    return build_release_rules(touching=touching_types())


def fallback_hits(rules: Any, path_root: str, ts_ns: np.ndarray) -> np.ndarray:
    """Ruling 4: fills before 2019-05-01 whose CT minute lies in [m, m + 30) for a fallback
    minute m of the vehicle (E.16's ReleaseRules._fallback_hit, vectorized)."""
    from base_rules import constants as BK

    ts_ns = np.asarray(ts_ns, dtype=np.int64)
    out = np.zeros(len(ts_ns), dtype=bool)
    mins = sorted({m for r in rules._roots(path_root) for m in rules.fallback.get(r, ())})
    ok = ts_ns > 0
    if not mins or not ok.any():
        return out
    local = pd.to_datetime(ts_ns[ok], utc=True).tz_convert(CT)
    minute = (local.hour * 60 + local.minute).to_numpy()
    early = np.asarray(local.date) < BK.FROZEN_CAL_FIRST
    hit = np.zeros(ok.sum(), dtype=bool)
    for m in mins:
        hit |= (minute >= m) & (minute < m + BK.EVENT_MINUTES)
    out[ok] = hit & early
    return out


def apply_fallback_costs(rows: pd.DataFrame, targets: pd.DataFrame, releases: Any,
                         costs: Mapping[str, Any], rules: Any) -> pd.DataFrame:
    """Ruling 4: the targets with each fill's side cost at the event-window slippage when the
    frozen calendar's event window or the fallback window covers the fill (a copy). Only the
    cost columns change: no deferral, no release-window refusal for the fallback types."""
    from ml_route_v2.constants import HORIZONS
    from ml_route_v2.signals._core import release_times
    from ml_route_v2.targets import (
        EVENT_WINDOW_NS,
        _cost_parts,
        _in_window,
        _side_ticks,
        minute_table,
    )

    out = targets.copy()
    for v in pd.unique(rows["root"]):
        sel = np.flatnonzero((rows["root"] == v).to_numpy())
        path = K.VEHICLE_PATHS.get(v, v)
        pc, comm = _cost_parts(costs[v], v)
        table = minute_table(pc)
        rel = np.asarray(release_times(releases, v), dtype=np.int64)
        e_ns = targets["entry_ts_ns"].to_numpy(np.int64)[sel]
        ev_e = _in_window(e_ns, rel, EVENT_WINDOW_NS) | fallback_hits(rules, path, e_ns)
        for h in HORIZONS:
            x_ns = targets[f"exit_ts_ns_{h}"].to_numpy(np.int64)[sel]
            ok = x_ns > 0
            ev_x = _in_window(x_ns, rel, EVENT_WINDOW_NS) | fallback_hits(rules, path, x_ns)
            ee = np.where(ok, e_ns, -1)
            long_ = comm + _side_ticks(table, ee, ev_e, 0) + _side_ticks(table, x_ns, ev_x, 1)
            short = comm + _side_ticks(table, ee, ev_e, 1) + _side_ticks(table, x_ns, ev_x, 0)
            for col, val in ((f"cost_long_{h}", long_), (f"cost_short_{h}", short)):
                arr = out[col].to_numpy(np.float64).copy()
                arr[sel] = np.where(ok, val, arr[sel])
                out[col] = arr
    return out


# ------------------------------------------------------------------ rulings 2, 3, 5, 6, 7 ----
def late_always_applicable_mask(ctx: Any, signals: tuple[str, ...] = K.KEPT_SIGNALS
                                ) -> np.ndarray:
    """Ruling 2: rows whose decision time precedes the availability of an always-applicable
    feature (its frame not applicable there, or present with avail > t). Computed from each
    spec's own function, before compute_signals' causality check would raise."""
    from ml_route_v2.signals import ALWAYS_APPLICABLE, REGISTRY

    t = ctx.rows["decision_ts_ns"].to_numpy(np.int64)
    mask = np.zeros(len(t), dtype=bool)
    for name in signals:
        if name not in ALWAYS_APPLICABLE:
            continue
        frame = REGISTRY[name].fn(ctx)
        app = frame["applicable"].to_numpy(np.float64) > 0
        val = frame["value"].to_numpy(np.float64)
        avail = frame["avail_ts_ns"].to_numpy(np.int64)
        mask |= ~app | (app & np.isfinite(val) & (avail > t))
    return mask


def session_end_exits(rows: pd.DataFrame, targets: pd.DataFrame, bars: Mapping[str, Any],
                      costs: Mapping[str, Any], releases: Any
                      ) -> tuple[pd.DataFrame, dict[str, int]]:
    """Ruling 3 (grains; E.16 R-B1; recheck PR-17): a post-step on the targets frame, before the
    purge reads exit_ts_ns. Where F_X falls at or after the trade date's session close (no bar
    opens at F_X), the hF exit and t4's h60 exit (the F_X exit) fill at the close of the last bar
    before the session close, priced with that bar's minute bucket (and the frozen event-window
    flag at that bar); y_gross, y_norm, both cost columns, exit_ts_ns (that bar's close) and ok
    are set. B1 applies it before apply_fallback_costs. A copy of the targets and the count of
    rows changed per horizon."""
    from data.group_session import session_intervals
    from ml_route.inputs import _group_calendar
    from ml_route_v2.signals._core import bar_arrays, per_unit, release_times
    from ml_route_v2.targets import (
        EVENT_WINDOW_NS,
        MIN_HOLD_NS,
        _cost_parts,
        _in_window,
        _side_ticks,
        minute_table,
    )

    out = targets.copy()
    counts = {"hF": 0, "h60_t4": 0}
    grains = (rows["group"] == "grains").to_numpy()
    for v in pd.unique(rows.loc[grains, "root"]):
        sel = np.flatnonzero(grains & (rows["root"] == v).to_numpy())
        path = K.VEHICLE_PATHS.get(v, v)
        b = bar_arrays(path, bars[path])
        pc, comm = _cost_parts(costs[v], v)
        table = minute_table(pc)
        cal = _group_calendar("grains")
        flat = rows["flatten_ts_ns"].to_numpy(np.int64)[sel]
        days = pd.to_datetime(rows["trade_date"].to_numpy()[sel]).date
        ends = np.array([max((hi for _lo, hi in session_intervals(cal, d)), default=-1)
                         for d in days], dtype=np.int64)
        late = (flat >= ends) & (ends > 0) & (b.at(flat) < 0)
        last_bar = np.searchsorted(b.ts, ends, side="left") - 1
        dnum = np.array([(d - date(1970, 1, 1)).days for d in days], dtype=np.int64)
        ok_bar = late & (last_bar >= 0) & b.on_day(np.where(last_bar >= 0, last_bar, -1), dnum)
        e_ns = targets["entry_ts_ns"].to_numpy(np.int64)[sel]
        entry = targets["entry_price"].to_numpy(np.float64)[sel]
        t4 = (rows["t_index"].to_numpy()[sel] == K.T4_INDEX)
        rel = np.asarray(release_times(releases, v), dtype=np.int64)
        ev_e = _in_window(e_ns, rel, EVENT_WINDOW_NS)
        for h, which in (("hF", np.ones(len(sel), dtype=bool)), ("h60", t4)):
            x_close = np.where(ok_bar, b.ts[np.clip(last_bar, 0, None)] + NS_MIN, -1)
            fix = ok_bar & which & (e_ns > 0) & ((x_close - e_ns) >= MIN_HOLD_NS)
            if not fix.any():
                continue
            y = (b.close[np.clip(last_bar, 0, None)] - entry) * per_unit(v)
            bar_ts = np.where(fix, b.ts[np.clip(last_bar, 0, None)], -1)
            ee = np.where(fix, e_ns, -1)
            ev_x = _in_window(bar_ts, rel, EVENT_WINDOW_NS)
            long_ = comm + _side_ticks(table, ee, ev_e, 0) + _side_ticks(table, bar_ts, ev_x, 1)
            short = comm + _side_ticks(table, ee, ev_e, 1) + _side_ticks(table, bar_ts, ev_x, 0)
            for col, val in ((f"y_gross_{h}", y), (f"cost_long_{h}", long_),
                             (f"cost_short_{h}", short), (f"exit_ts_ns_{h}", x_close)):
                arr = out[col].to_numpy().copy()
                arr[sel[fix]] = val[fix]
                out[col] = arr
            sig = out["sigma_d"].to_numpy(np.float64)
            for col in (f"y_norm_{h}",):
                arr = out[col].to_numpy(np.float64).copy()
                arr[sel[fix]] = y[fix] / sig[sel[fix]]
                out[col] = arr
            okc = out[f"ok_{h}"].to_numpy(bool).copy()
            fin = (np.isfinite(out[f"y_gross_{h}"].to_numpy(np.float64))
                   & np.isfinite(out[f"cost_long_{h}"].to_numpy(np.float64))
                   & np.isfinite(out[f"cost_short_{h}"].to_numpy(np.float64))
                   & (sig > 0))
            okc[sel[fix]] = fin[sel[fix]]
            out[f"ok_{h}"] = okc
            counts["hF" if h == "hF" else "h60_t4"] += int(fix.sum())
    return out, counts


def unsourced_release_exclusions() -> dict[str, frozenset[date]]:
    """Ruling 5: the WPSR dates without a sourced time (E.14 unsourced[]), excluded for MCL."""
    _rows, untimed = derive_wpsr(read_source("e14_releases"))
    return {"MCL": frozenset(date.fromisoformat(d) for d in untimed)}


def unsourced_calendar_exclusions(calendars: Mapping[str, Any]) -> dict[str, frozenset[date]]:
    """Ruling 6: each vehicle's hist-calendar unsourced dates inside its B1 window."""
    from data.calendars import GROUP_OF_PRODUCT

    out = {}
    for v, path in K.VEHICLE_PATHS.items():
        cal = calendars[GROUP_OF_PRODUCT[v]]
        lo = B1_FIRST[path]
        out[v] = frozenset(d for d in getattr(cal, "unsourced", ()) if lo <= d <= B1_LAST)
    return out


def b1_exclusions(calendars: Mapping[str, Any]) -> dict[str, frozenset[date]]:
    """Rulings 5 and 6 together: vehicle -> dates excluded as action dates in E20-B1."""
    cal = unsourced_calendar_exclusions(calendars)
    rel = unsourced_release_exclusions()
    return {v: frozenset(cal.get(v, frozenset()) | rel.get(v, frozenset())) for v in K.VEHICLES}


def reopening_record(tables: BackwardTables) -> dict[str, Any]:
    """Ruling 7: the auction rows keep the frozen original-term labels (recorded, not
    corrected); the hist rows per tenor in the B1 window."""
    rows = [r for r in tables.auctions if "2010-07-01" <= r[0] <= B1_LAST.isoformat()]
    return {"convention": "tenor from the EC-AUC row id (original security term), as E.2b",
            "rows_in_window_by_tenor": {t: sum(1 for r in rows if r[1] == t) for t in TENORS}}


__all__ = ["B1_FIRST", "B1_LAST", "CALENDAR_PATCHES", "PATCHES", "SOURCES", "BackwardError",
           "BackwardTables", "apply_fallback_costs", "b1_exclusions", "backward_context",
           "backward_release_rules", "backward_tables", "clear_caches", "derive_auctions",
           "derive_equity_full", "derive_month_end", "derive_wpsr", "fallback_hits",
           "hist_calendars", "is_active", "late_always_applicable_mask", "originals",
           "overlap_record", "read_source", "reopening_record", "replacement_values",
           "session_end_exits", "touching_types", "unsourced_calendar_exclusions",
           "unsourced_release_exclusions"]
