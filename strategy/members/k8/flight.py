"""K8-flight-01: flight to gold after an extreme negative 5-minute S&P 500 move, traded on MGC
with MES as the signal leg (Stage E.9; reports/stage_e9_member_specs.md section 1 and S0.1-S0.12;
catalog reports/stage_e0_catalog_K8.md lines 252-371; readings K8-L-02..K8-L-10, E.3-L-08,
E.3-L-22, K4-L-09). Two trials, one class: H30 (ordinal 1) and HEOD (ordinal 2) differ only in
the exit.

Rule (every clock time CT; "the bar at hh:mm" of a leg on trade date d is that leg's bar opening
hh:mm:00 on CT date d whose trade_date is d, S0.4, K8-L-02):
- Blocks B_k = [08:30 + 5(k-1), 08:30 + 5k), k = 1..77; decision time t_k = 08:30 + 5k, 08:35 to
  14:55. r_k = (c1 - c6) / c6, c1 and c6 the closes, in integer MES vendor ticks, of the MES bars
  at t_k - 1 and t_k - 6 (for k = 1 the bars at 08:34 and 08:29). Both bars present with ONE
  instrument_id and c6 > 0, else r_k is undefined and there is no trigger at t_k (S0.9, K8-L-05,
  K8-L-10). r_k is an exact rational (numerator, positive denominator) compared by integer
  cross-multiplication: the freeze's import list has no fractions module, and the comparisons
  are exactly those of fractions.Fraction (K8-L-09).
- Reference dates: the 20 most recent FLIGHT_DATES (EQUITY and METALS full sessions) strictly
  before d, roll-blackout dates included (K8-L-04). Reference values: every defined r_k of those
  dates (a date with no bars gives none); n = their count. Warm-up: no trade on d while any
  reference date precedes the trade date of the first bar the member received in the run
  (K4-L-09). n < 1,200: no trade on d. Q(d) = the m-th smallest value, duplicates counted,
  m = (n + 199) // 200 = ceil(0.005 n). Q(d) reads only dates before d.
- Trigger at t_k: r_k <= Q(d) and r_k < 0. d must be in FLIGHT_DATES (S0.8).
- C6 (S0.10, K8-L-08): a trigger whose fill minute t_k lies in [R, R + 2 min) of an MGC release
  instant R (_releases.in_guard) is skipped, does not use the day's entry, and later blocks are
  watched.
- Entry: the FIRST trigger of d that C6 does not skip uses the day's one entry, refused by the
  engine or not (E.3-L-08): BUY q_c MGC, market intent on the view at t_k - 1 whose MGC bar is the
  bar at t_k - 1 (S0.6), filling at the open of the MGC bar at t_k. If that MGC bar is missing,
  there is no entry and no trade on d (K8-L-06). No entry while MGC holds a position or a pending
  order (S0.6).
- T_e (K8-L-07): the CT open of the bar at which the account first shows the position (the engine
  fills at that bar's open before calling the member): t_k, or later if the bar at t_k is missing.
- Exit: H30 market intent on the MGC bar at min(T_e + 29, 15:04); HEOD on the MGC bar at 15:04;
  sent on the first present MGC bar at or after it while the position is non-zero and nothing is
  pending on MGC, so a refused exit is resent (S0.7, E.3-L-22). Exit bars are never guarded. The
  engine's flatten at F 15:08, its D9.7 exit and MLL are the backstops; a flat account sends no
  exit.
- Not here (the engine and runner, S0 preamble): window dates and roll blackouts of both legs
  (D4, V16(a)), D9.5a's deferral of exits, the open refusal when a leg lacks the bar (D11.5),
  costs, F.
One traded leg, q_c contracts of MGC (1); MES never takes a position.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from functools import cmp_to_key
from typing import Any
from zoneinfo import ZoneInfo

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k8._calendar import FLIGHT_DATES, previous_dates
from strategy.members.k8._releases import in_guard
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K8-flight-01"
TRADED = "MGC"  # the one traded leg (gold, C lines 253-257)
SIGNAL = "MES"  # the signal leg (S&P 500), read only
VARIANTS = ("H30", "HEOD")
CT = ZoneInfo("America/Chicago")
NS_PER_S = 1_000_000_000
NS_PER_MIN = 60 * NS_PER_S
BLOCK_CLOCK_START = time(8, 30)  # B_1 = [08:30, 08:35)
BLOCK_MINUTES = 5
BLOCKS = 77  # k = 1..77: t_k = 08:35..14:55
END_BAR_BEFORE_T_MIN = 1  # r_k's end bar and the entry bar: the bar at t_k - 1
START_BAR_BEFORE_T_MIN = 6  # r_k's start bar: the bar at t_k - 6
REFERENCE_DATES = 20  # the 20 most recent FLIGHT_DATES strictly before d
MIN_VALUES = 1200  # n >= 1,200, else no trade on d
TAIL_DIVISOR = 200  # m = ceil(0.005 n) = (n + 199) // 200
H30_INTENT_AFTER_FILL_MIN = 29  # H30: intent on the bar at T_e + 29 (fill T_e + 30)
LAST_EXIT_BAR = time(15, 4)  # HEOD's exit bar and H30's cap (fill 15:05)
_ANCHOR_DAY = date(2000, 1, 3)  # any date: clock arithmetic on a time of day
_FLIGHT_SET = frozenset(FLIGHT_DATES)

Ratio = tuple[int, int]  # (numerator, denominator > 0): an exact rational


def shift(at: time, minutes: int) -> time:
    """A clock time ``minutes`` later (negative: earlier) on the same CT day."""
    return (datetime.combine(_ANCHOR_DAY, at) + timedelta(minutes=minutes)).time()


def decision_times() -> tuple[time, ...]:
    """t_k = 08:30 + 5k for k = 1..77: 08:35, 08:40, ..., 14:55."""
    return tuple(shift(BLOCK_CLOCK_START, BLOCK_MINUTES * k) for k in range(1, BLOCKS + 1))


def ct_open(bar: Any) -> datetime:
    """The bar's open (``ts_event_ns``; bars sit on whole seconds) in CT."""
    return datetime.fromtimestamp(bar.ts_event_ns // NS_PER_S, tz=UTC).astimezone(CT)


def to_ticks(price: float, tick: Decimal) -> int:
    """round(price / vendor_tick), exactly in Decimal."""
    return round(Decimal(repr(price)) / tick)


def compare(a: Ratio, b: Ratio) -> int:
    """-1, 0 or 1 as a <, =, > b, exactly (denominators positive)."""
    lhs, rhs = a[0] * b[1], b[0] * a[1]
    return (lhs > rhs) - (lhs < rhs)


def block_return(c6: int, c1: int) -> Ratio | None:
    """r_k = (c1 - c6) / c6 from integer ticks; None when c6 <= 0 (K8-L-10)."""
    if c6 <= 0:
        return None
    return (c1 - c6, c6)


def threshold(values: Sequence[Ratio]) -> Ratio | None:
    """Q(d): the m-th smallest reference value, duplicates counted, m = (n + 199) // 200; None
    when n < 1,200 (no trade on d)."""
    n = len(values)
    if n < MIN_VALUES:
        return None
    m = (n + TAIL_DIVISOR - 1) // TAIL_DIVISOR
    return sorted(values, key=cmp_to_key(compare))[m - 1]


def triggers(r: Ratio, q: Ratio) -> bool:
    """The trigger at t_k: r_k <= Q(d) and r_k < 0, exactly."""
    return r[0] < 0 and compare(r, q) <= 0


def reference_dates(day: date) -> tuple[date, ...]:
    """The 20 most recent FLIGHT_DATES strictly before ``day``, oldest first."""
    return previous_dates(FLIGHT_DATES, day, REFERENCE_DATES)


def _minute_of_day(at: time) -> int:
    return at.hour * 60 + at.minute


@dataclass
class FlightToGold:
    """K8-flight-01 (H30 or HEOD): MGC traded, MES read. The r_k of each MES trade date are filed
    when the next one starts and kept only while a later reference set can use them."""

    variant: str
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q_c: int = field(init=False, repr=False)
    _tick: Decimal = field(init=False, repr=False)  # MES vendor tick
    _k_of_end_bar: dict = field(init=False, repr=False)  # minute of day of t_k - 1 -> k
    _k_of_start_bar: dict = field(init=False, repr=False)  # minute of day of t_k - 6 -> k
    _first_day: date | None = field(default=None, init=False, repr=False)
    # signal state, per MES trade date
    _sig_day: date | None = field(default=None, init=False, repr=False)
    _starts: dict = field(default_factory=dict, init=False, repr=False)  # k -> (c6, id)
    _today: tuple = field(default=(), init=False, repr=False)  # defined r_k of _sig_day
    _history: dict = field(default_factory=dict, init=False, repr=False)  # date -> r values
    # decision state, per trade date d
    _day: date | None = field(default=None, init=False, repr=False)
    _q: Ratio | None = field(default=None, init=False, repr=False)  # Q(d); None: no trade on d
    _done: bool = field(default=False, init=False, repr=False)  # the day's entry is used
    # position state
    _t_e_ns: int | None = field(default=None, init=False, repr=False)
    _exit_ns: int | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.variant not in VARIANTS:
            raise ValueError(f"{MEMBER_ID} variant {self.variant!r} is not one of {VARIANTS}")
        self.name = f"{MEMBER_ID} {self.variant} {TRADED}"
        self.legs = (LegSpec(TRADED, True), LegSpec(SIGNAL, False))
        self._q_c = load_frozen_tables().vehicles[TRADED].q_c
        self._tick = product(SIGNAL).vendor_tick
        times = decision_times()
        self._k_of_end_bar = {_minute_of_day(shift(t, -END_BAR_BEFORE_T_MIN)): k
                              for k, t in enumerate(times, start=1)}
        self._k_of_start_bar = {_minute_of_day(shift(t, -START_BAR_BEFORE_T_MIN)): k
                                for k, t in enumerate(times, start=1)}
        # S0.12: MGC from the first entry bar (08:34) to the last exit fill (15:05); MES the
        # signal bars 08:29..14:54
        self.trading_windows = {
            TRADED: (TradingInterval(shift(times[0], -END_BAR_BEFORE_T_MIN),
                                     shift(LAST_EXIT_BAR, 2)),),
            SIGNAL: (TradingInterval(shift(times[0], -START_BAR_BEFORE_T_MIN), times[-1]),),
        }

    # -- the signal (MES) ---------------------------------------------------------------
    def _roll_signal(self, day: date) -> None:
        """File the ending MES trade date's r values, keep only the dates a reference set of
        ``day`` or later can use (reference sets read FLIGHT_DATES only), then start ``day``."""
        merged = self._history
        if self._sig_day is not None:
            merged = {**merged, self._sig_day: self._today}
        refs = reference_dates(day)
        oldest = refs[0] if refs else day
        self._history = {d: v for d, v in merged.items() if d >= oldest}
        self._sig_day, self._starts, self._today = day, {}, ()

    def _signal(self, bar: Any) -> tuple[date, Ratio | None] | None:
        """Record ``bar`` (an MES bar or None). When it is the bar at t_k - 1 of its trade date,
        return (d, r_k), r_k None when undefined; otherwise None."""
        if bar is None:
            return None
        opened = ct_open(bar)
        day = bar.trade_date
        if opened.date() != day:
            return None  # the previous CT evening: no block bar of trade date d
        if day != self._sig_day:
            self._roll_signal(day)
        minute = _minute_of_day(opened.time())
        out = None
        k_end = self._k_of_end_bar.get(minute)
        if k_end is not None:
            r = self._block_return(k_end, bar)
            if r is not None:  # every defined r_k is a future reference value, traded or not
                self._today = (*self._today, r)
            out = (day, r)
        k_start = self._k_of_start_bar.get(minute)
        if k_start is not None:
            first = (to_ticks(bar.close, self._tick), bar.instrument_id)
            self._starts = {**self._starts, k_start: first}
        return out

    def _block_return(self, k: int, bar: Any) -> Ratio | None:
        start = self._starts.get(k)
        if start is None:
            return None  # the bar at t_k - 6 is missing
        c6, start_id = start
        if start_id != bar.instrument_id:
            return None  # two instrument_ids inside the block (K8-L-05)
        return block_return(c6, to_ticks(bar.close, self._tick))

    # -- the entry (MGC) ----------------------------------------------------------------
    def _threshold_for(self, day: date) -> Ratio | None:
        if day not in _FLIGHT_SET:
            return None  # S0.8: not an EQUITY and METALS full session
        refs = reference_dates(day)
        if len(refs) < REFERENCE_DATES or self._first_day is None or refs[0] < self._first_day:
            return None  # warm-up (K4-L-09)
        return threshold([v for d in refs for v in self._history.get(d, ())])

    def _entry(self, view: MinuteView, account: MemberAccountView, day: date,
               r: Ratio | None) -> Sequence[LegIntent | Refusal]:
        if day != self._day:
            self._day, self._done, self._q = day, False, self._threshold_for(day)
        if self._done or self._q is None or r is None or not triggers(r, self._q):
            return ()
        if in_guard(TRADED, view.decision_ts_ns):
            return ()  # C6: the fill minute t_k is guarded; skipped, the day's entry kept
        self._done = True  # the first non-skipped trigger uses the day's entry (E.3-L-08)
        bar = view.bar(TRADED)
        if bar is None or bar.trade_date != day:
            return ()  # K8-L-06: the entry bar at t_k - 1 is missing: no trade on d
        if account.position(TRADED) or account.pending.get(TRADED, 0):
            return ()  # S0.6
        return (leg_market_intent(view, TRADED, "buy", self._q_c),)

    # -- the exit -----------------------------------------------------------------------
    def _exit_due_ns(self, t_e_ns: int) -> int:
        """The exit bar's open: H30 min(T_e + 29, 15:04), HEOD 15:04, on T_e's CT date."""
        t_e = datetime.fromtimestamp(t_e_ns // NS_PER_S, tz=UTC).astimezone(CT)
        cap = datetime.combine(t_e.date(), LAST_EXIT_BAR, tzinfo=CT)
        cap_ns = int(cap.timestamp()) * NS_PER_S
        if self.variant == "HEOD":
            return cap_ns
        return min(t_e_ns + H30_INTENT_AFTER_FILL_MIN * NS_PER_MIN, cap_ns)

    def _exit(self, view: MinuteView, account: MemberAccountView, position: int
              ) -> Sequence[LegIntent | Refusal]:
        if self._t_e_ns is None:  # K8-L-07: the first view showing the position is T_e's
            self._t_e_ns = view.ts_event_ns
            self._exit_ns = self._exit_due_ns(view.ts_event_ns)
        bar = view.bar(TRADED)
        if bar is None or account.pending.get(TRADED, 0):
            return ()
        if self._exit_ns is None or bar.ts_event_ns < self._exit_ns:
            return ()
        side = "sell" if position > 0 else "buy"
        return (leg_market_intent(view, TRADED, side, abs(position)),)

    # -- the member contract ------------------------------------------------------------
    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        if self._first_day is None:
            days = [b.trade_date for b in view.bars.values() if b is not None]
            if days:
                self._first_day = min(days)  # K4-L-09: the first bar received in the run
        decision = self._signal(view.bar(SIGNAL))
        position = account.position(TRADED)
        if position:
            return self._exit(view, account, position)
        self._t_e_ns, self._exit_ns = None, None
        if decision is None:
            return ()
        day, r = decision
        return self._entry(view, account, day, r)


def make_h30() -> FlightToGold:
    return FlightToGold("H30")


def make_heod() -> FlightToGold:
    return FlightToGold("HEOD")


__all__ = [
    "BLOCKS", "MEMBER_ID", "MIN_VALUES", "REFERENCE_DATES", "SIGNAL", "TRADED", "VARIANTS",
    "FlightToGold", "block_return", "compare", "decision_times", "make_h30", "make_heod",
    "reference_dates", "threshold", "triggers",
]
