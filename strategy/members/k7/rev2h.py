"""K7-rev2h-01: two-hour reversal in the MBT day session (Stage E.6;
reports/stage_e6_member_specs.md section 5; catalog reports/stage_e0_catalog_K7.md lines
518-593; readings K7-L-01, K7-L-03, K7-L-06, K7-L-07, K7-L-08).

Rule (every clock time CT; bars of trade date d on CT date d only, S0.4):
- Dates: every trade date d in CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED (S0.8).
- Blocks from the anchor O = 08:30 (frozen day_session_ct): B1 = [08:30, 10:30),
  B2 = [10:30, 12:30), B3 = [12:30, 14:30).
- Decision 10:30: r1 = close of the 10:29 bar - open of the 08:30 bar, in ticks; target1 =
  -sign(r1) x q; 0 if r1 = 0, if the 08:30 or 10:29 bar is missing, or if the 08:30 and 10:29 bars
  carry different instrument_ids. Decision 12:30: the same with the 10:30 and 12:29 bars.
- Orders at each decision, decided at the close of the bar at decision - 1 min with the account's
  position then: hold if the target equals the position (the position is always 0 or +-q, so
  equal signs); otherwise, if a position is open, a flatten intent on that bar (fills at the
  decision-time open; if the bar is missing, on the first later present bar, with target 0,
  K7-L-08); then, if the target is nonzero, an entry intent on the decision-time bar (10:30 or
  12:30, fills one minute later), sent only if the account is then flat, that bar exists and it
  carries the signal bars' instrument_id (S0.6, S0.9, K7-L-06).
- Final exit: market intent on the 14:29 bar, filling at the 14:30 open; if missing, the first
  later present bar (S0.7).
- A position the engine closes before 12:30 leaves the account flat, and the 12:30 decision
  applies as written (K7-L-07). At most 2 entries a trade date.
The rule itself is strategy.members.k7._event_common.DecisionBook with direction -1.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date

from rules.xfa_rules import Refusal
from strategy.members.k7._event_common import (
    ROOT,
    DaySchedule,
    Decision,
    DecisionBook,
    LegFacts,
    clock_minute,
    clock_of,
    ct_open_ns,
    is_entry_date,
    label,
    leg_facts,
)
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)

MEMBER_ID = "K7-rev2h-01"
BLOCK_MINUTES = 120  # B1, B2, B3 are 120 minutes each from the anchor O
BLOCKS = 3
DECISION_BLOCKS = (1, 2)  # decisions at the ends of B1 (10:30) and B2 (12:30)
SIGNAL_END_BEFORE_T_MIN = 1  # r closes at, and orders are decided on, the bar at t - 1
FINAL_EXIT_BEFORE_END_MIN = 1  # the final exit goes on the bar at 14:29 (B3's end - 1)
WINDOW_END_AFTER_BLOCKS_MIN = 1  # S0.12: to the 14:30 exit fill bar inclusive, (08:30, 14:31)
DIRECTION = -1  # reversal: target = -sign(r) x q


def day_schedule(day: date, anchor_minute: int) -> DaySchedule:
    """The two decisions and the final exit bar of trade date ``day`` (CT date ``day``)."""
    decisions = []
    for k in DECISION_BLOCKS:
        t = anchor_minute + k * BLOCK_MINUTES
        decisions.append(Decision(ct_open_ns(day, t - BLOCK_MINUTES),
                                  ct_open_ns(day, t - SIGNAL_END_BEFORE_T_MIN),
                                  ct_open_ns(day, t)))
    end = anchor_minute + BLOCKS * BLOCK_MINUTES
    return DaySchedule(tuple(decisions), ct_open_ns(day, end - FINAL_EXIT_BEFORE_END_MIN))


@dataclass
class TwoHourReversal:
    """K7-rev2h-01 on MBT. Day state resets when the bar's trade date changes."""

    root: str = field(default=ROOT, init=False)
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _leg: LegFacts = field(init=False, repr=False)
    _anchor: int = field(init=False, repr=False)
    _day: date | None = field(default=None, init=False, repr=False)
    _book: DecisionBook | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._leg = leg_facts()
        self.name = label(MEMBER_ID)
        self.legs = self._leg.legs
        self._anchor = clock_minute(self._leg.o)
        end = self._anchor + BLOCKS * BLOCK_MINUTES + WINDOW_END_AFTER_BLOCKS_MIN
        self.trading_windows = {self.root: (TradingInterval(self._leg.o, clock_of(end)),)}

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._day = bar.trade_date
            self._book = (DecisionBook(day_schedule(self._day, self._anchor), DIRECTION,
                                       self._leg.q, self._leg.tick, self.root)
                          if is_entry_date(self._day) else None)
        if self._book is None:
            return ()
        return self._book.on_bar(view, account, bar)


def make_mbt() -> TwoHourReversal:
    return TwoHourReversal()


__all__ = ["BLOCK_MINUTES", "DECISION_BLOCKS", "MEMBER_ID", "TwoHourReversal", "day_schedule",
           "make_mbt"]
