"""H4 -- Turn-of-month mechanical flow (last session of month + first ~3 sessions of new month).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: go long once at the start of each session that is EITHER the last
trading day of its calendar month OR one of the first TOM_FOLLOWING_DAYS
trading days of the following month, holding to a fixed self-managed exit
late in that same session, on the classic turn-of-month calendar-anomaly
theory (pension/mutual-fund reinvestment flows timed to calendar month-end).

HARNESS-COMPATIBILITY ADAPTATION (stated up front): the literature's actual
claim is a MULTI-SESSION drift spanning the month-end date through several
following sessions -- i.e. a position that would, in its original form, be
carried overnight across several trade dates. ``rules/xfa_rules.py`` forces
every position flat by 15:10 CT and blocks new entries from 15:08 CT, on
EVERY trade date (``data/splits.py``: "no position ever spans a trade-date
boundary"), so this harness cannot hold a single continuous multi-day
position at all. The only harness-legal operationalization is the one
implemented here: independent, same-session long bets on each of the
target days, each entered and exited within its own session. This measures
"is each of these specific calendar days individually long-biased," which
is a meaningfully weaker claim than "is there a continuous multi-day
drift," and is recorded as a degradation from the literature's design, not
a silent equivalence.

CALENDAR-ONLY, NO EXTERNAL TABLE: "last trading day of month" and "Nth
trading day of month" are computed from ``bar.trade_date`` plus
``data.cme_calendar.HOLIDAYS`` (read-only import; this file does not modify
that module), mirroring exactly the weekday + FULL_CLOSURE exclusion logic
``data/splits.py`` already uses to build the research trade-date list. No
external date table is needed for this hypothesis, unlike H1/H2.

SOURCE CITATION AND ITS OWN WEAKNESS (stated plainly): read only via a
third-party secondary summary of an underlying academic study; the primary
paper (Carchano & Pardo, "Calendar Anomalies in Stock Index Futures", SSRN
1958587) was retrieval_blocked on both SSRN and an alternate mirror this
session. This is the WEAKEST evidentiary chain of the four hypotheses in
this family. The one full-text source that could be read on this specific
question reports the S&P-futures-specific turn-of-month effect "disappears
after 1990" -- a finding this hypothesis is flagged as testing/falsifying,
not assuming away, precisely because the primary source that would let
anyone verify or update that 1990 cutoff was blocked, not read.

FALSIFICATION-FIRST FRAMING: given (a) the harness-forced degradation above
and (b) the cited "disappears after 1990" finding from a source itself one
level removed from primary text, this hypothesis should be treated as
PRIMARILY a falsification exercise on the current MES sample. Any pass
should be scrutinized hard rather than reported as a discovery, given how
weak its own sourcing is relative to H1-H3.

Parameters (ONE setting, chosen before any backtest was run):
    TOM_FOLLOWING_DAYS = 3        (first 3 trading days of the new month)
    EXIT_CT_TIME = 15:00 CT       (self-managed, safely before the 15:08/15:10
                                    CT new-position/flatten cutoffs)
    QUANTITY_MICROS = 1

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the measured T;
  (b) that pass uses the MEASURED p and R, not a hand-picked grid point;
  (c) a first-fold pass is re-run across all 8 train folds and the ROBUST
      verdict does not flip to "fail" on most of them;
  (d) given the "disappears after 1990" prior and the multi-day-drift
      degradation above, a pass here carries a materially higher prior of
      being an artifact than H1-H3's passes and should be reported with
      that context attached, not as a clean discovery.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) a refute here is fully consistent with (and does not update) the
      "disappears after 1990" prior already in the sourcing -- it should be
      reported as confirming the existing literature, not as new news.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass, field
from datetime import date, time
from zoneinfo import ZoneInfo

from data.cme_calendar import HOLIDAYS, HolidayKind
from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

CT_TZ = ZoneInfo("America/Chicago")
TOM_FOLLOWING_DAYS = 3
EXIT_CT_TIME = time(15, 0)
QUANTITY_MICROS = 1


def _is_trading_day(day: date) -> bool:
    if day.weekday() >= 5:
        return False
    holiday = HOLIDAYS.get(day)
    return holiday is None or holiday.kind is not HolidayKind.FULL_CLOSURE


def _trading_days_in_month(year: int, month: int) -> list[date]:
    n_days = calendar.monthrange(year, month)[1]
    days = (date(year, month, d) for d in range(1, n_days + 1))
    return [day for day in days if _is_trading_day(day)]


def is_last_trading_day_of_month(trade_date: date) -> bool:
    days = _trading_days_in_month(trade_date.year, trade_date.month)
    return bool(days) and days[-1] == trade_date


def trading_day_index_in_month(trade_date: date) -> int | None:
    """1-based index of ``trade_date`` among its month's trading days, or None."""
    days = _trading_days_in_month(trade_date.year, trade_date.month)
    return days.index(trade_date) + 1 if trade_date in days else None


def is_turn_of_month_day(trade_date: date, following_days: int) -> bool:
    if is_last_trading_day_of_month(trade_date):
        return True
    idx = trading_day_index_in_month(trade_date)
    return idx is not None and idx <= following_days


@dataclass(frozen=True)
class H4TurnOfMonthLong:
    """Long, same-session-only, on the last trading day of month and the first N of the next."""

    name: str = "h4_turn_of_month_long"
    following_days: int = TOM_FOLLOWING_DAYS
    exit_ct_time: time = EXIT_CT_TIME
    quantity_micros: int = QUANTITY_MICROS
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _entered_today: list[bool] = field(default_factory=lambda: [False])

    def __post_init__(self) -> None:
        if self.following_days < 1:
            raise ValueError(f"following_days {self.following_days!r} must be >= 1")
        if not isinstance(self.exit_ct_time, time):
            raise ValueError(f"exit_ct_time {self.exit_ct_time!r} must be a time")
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        if self._current_trade_date[0] != bar.trade_date:
            self._current_trade_date[0] = bar.trade_date
            self._entered_today[0] = False

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        if flat and not self._entered_today[0] and is_turn_of_month_day(
            bar.trade_date, self.following_days
        ):
            self._entered_today[0] = True
            return (market_intent(bar, "buy", self.quantity_micros),)

        bar_ct_time = bar.decision_ts_utc.astimezone(CT_TZ).time()
        if account.position_micros != 0 and bar_ct_time >= self.exit_ct_time:
            side = "sell" if account.position_micros > 0 else "buy"
            return (market_intent(bar, side, abs(account.position_micros)),)
        return ()
