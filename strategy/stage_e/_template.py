"""Stage E member template (Stage E.2b Task 1). Copy it; do not import it from a member.

HOW A CLUSTER SESSION WRITES AND RUNS A MEMBER
1. Copy this file to strategy/members/<k#>/<member_file>.py, add an empty
   strategy/members/<k#>/__init__.py, rename the class, and write the rule from the frozen list
   entry. strategy/members/__init__.py is PROVIDED by the harness: empty (0 bytes) and frozen in
   the harness manifest; never create, edit or fill it (the freeze refuses unless it is empty,
   review finding F-1). Never place a member under strategy/stage_e/ (harness code).
   Every *.py file of the cluster directory must pass the freeze's static check
   (screening.stage_e_freeze.check_member_source, run when the freeze is written, verified and
   before a member is imported):
   - imports ONLY from: __future__, datetime, math, decimal, zoneinfo, dataclasses, typing,
     collections (and collections.abc), enum, functools, itertools, statistics, numpy,
     rules.products, rules.xfa_rules, screening.stage_e_frozen, strategy.stage_e.interface, and
     the member's own cluster package strategy.members.<k#>; no ``import *``;
   - never names open, exec, eval, compile, __import__, globals, setattr, delattr, getattr, vars,
     locals, __builtins__, breakpoint, input, importlib, os, sys, pathlib, subprocess or builtins;
     no dunder attribute other than __init__, __post_init__, __name__ and __doc__;
   - never assigns to, deletes or mutates (update, pop, clear, cache_clear, ...) anything
     reached from an imported module, and reads or writes no file (numpy's load, save,
     loadtxt, fromfile, tofile, memmap; a Path's read_text or write_bytes, ...).
   This template passes the check (tests/test_stage_e_freeze.py).
2. Give it a module-level zero-argument factory (``make_member`` below): the runner calls it once
   per screen, so every run starts from fresh state.
3. Declare every leg the member reads in the freeze (screening.stage_e_freeze.MemberDecl):
   traded legs are Stage E vehicles (reports/stage_e2a_vehicles.json); signal legs are read only.
   The FIRST traded leg is the primary leg whose vehicle, q_c and eps the series uses.
4. Freeze the cluster's code before running anything:
       from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
       write_cluster_freeze("K1", [MemberDecl("K1-cp2-01 MNQ", 1, "strategy.members.k1.cp2",
                                              "make_member", (LegSpec("MNQ", True),)), ...])
5. Run it: python -m screening.stage_e_runner --harness-sha256 <sha> --cluster K1 --all
       --window research --research-root data/processed --step2-root data/processed_step2
       --out-dir reports/stage_e_k1_screen

WHAT THE MEMBER SEES AND MAY DO (strategy/stage_e/interface.py has the full contract)
- ``on_minute(view, account)`` once per minute of the member's shared UTC grid. ``view.bars[root]``
  is the completed bar of each leg opening at that minute, or None: never forward fill a None.
- Prices are in VENDOR units: ZC, ZW, ZS, ZL, HE and LE are quoted in cents (their tick is 100 x
  the exchange tick); use ``rules.products.product(root).vendor_tick`` for tick arithmetic, never a
  literal.
- Sizes are contracts of the vehicle: trade ``q_c`` from the frozen vehicle table
  (screening.stage_e_frozen.load_frozen_tables().vehicles[root].q_c), never more (D2, D9.5).
- Clock times (D6's O and C per product) come from the frozen tables
  (``load_frozen_tables().day_session_ct[root]``); F comes from rules/sessions.py, which the
  engine enforces by itself (the member cannot hold past F).
- Declare ``trading_windows``: for every leg, the CT intervals the member reads or trades on it.
  D9's coverage check measures bars against exactly these minutes; a leg below 0.95 excludes the
  member before screening.
- The engine enforces, and counts, D9's floor: at most 20 entries per product per trade date and
  no exit less than 2 full minutes after the last opening fill. A member whose rule would breach
  either is labelled (not dropped); write the rule so it cannot (D9: re-write at design). If an
  entry's own exit would come sooner than 2 minutes after its fill, skip the entry for the day.
- Orders fill at the next bar's open of their leg (market) or on trade-through (limit); fills in
  the first two minutes after a scheduled release are delayed by the engine (D9.5a).

THE EXAMPLE: an opening-range breakout on one traded leg, the D6 CP2 port's shape (range [O, O+15),
entry on the first close beyond it by 4 ticks, exit 75 minutes after the fill or at C-2). It is a
template, not a catalog member: nothing screens it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

CT = ZoneInfo("America/Chicago")
RANGE_MINUTES = 15
BUFFER_TICKS = 4
HOLD = timedelta(minutes=75)


def _minus(at: time, minutes: int) -> time:
    return (datetime(2000, 1, 3, at.hour, at.minute) - timedelta(minutes=minutes)).time()


@dataclass
class TemplateBreakout:
    """One traded leg; every constant from the frozen tables or this module."""

    root: str
    name: str = "stage_e_template_breakout"
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _o: time = field(init=False)
    _c: time = field(init=False)
    _q: int = field(init=False)
    _buffer: float = field(init=False)
    _day: object = field(default=None, init=False)
    _hi: float | None = field(default=None, init=False)
    _lo: float | None = field(default=None, init=False)
    _done: bool = field(default=False, init=False)
    _entry_at: datetime | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        tables = load_frozen_tables()
        self._o, self._c = tables.day_session_ct[self.root]
        self._q = tables.vehicles[self.root].q_c
        self._buffer = float(Decimal(BUFFER_TICKS) * product(self.root).vendor_tick)
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: (TradingInterval(self._o, self._c),)}

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._day, self._hi, self._lo, self._done, self._entry_at = (bar.trade_date, None,
                                                                          None, False, None)
        opened = datetime.fromtimestamp(bar.ts_event_ns / 1e9, tz=UTC).astimezone(CT)
        t = opened.time()
        range_end = (datetime.combine(opened.date(), self._o) + timedelta(minutes=RANGE_MINUTES)
                     ).time()
        position = account.position(self.root)
        if position:
            due = self._entry_at is not None and view.decision_ts_utc >= self._entry_at + HOLD
            if due or t >= _minus(self._c, 2):
                side = "sell" if position > 0 else "buy"
                return (leg_market_intent(view, self.root, side, abs(position)),)
            return ()
        if self._o <= t < range_end:
            self._hi = bar.high if self._hi is None else max(self._hi, bar.high)
            self._lo = bar.low if self._lo is None else min(self._lo, bar.low)
            return ()
        if self._done or self._hi is None or self._lo is None or not range_end <= t < self._c:
            return ()
        if account.pending.get(self.root):
            return ()
        if bar.close >= self._hi + self._buffer:
            side = "buy"
        elif bar.close <= self._lo - self._buffer:
            side = "sell"
        else:
            return ()
        self._done = True  # one entry per trade date
        self._entry_at = view.decision_ts_utc
        return (leg_market_intent(view, self.root, side, self._q),)


def make_member() -> TemplateBreakout:
    """The module-level factory a freeze names (here on MNQ, for illustration only)."""
    return TemplateBreakout("MNQ")


__all__ = ["TemplateBreakout", "make_member"]
