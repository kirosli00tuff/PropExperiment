"""H3 -- Quarterly triple/quadruple-witching mechanical expiration-flow effect.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: on the quarterly witching Friday (3rd Friday of March / June /
September / December), short MES for the last LAST_MINUTES_BEFORE_CLOSE of
the regular session, on the theory that mechanical unwind/roll of expiring
index futures and options positions produces the classic "last-half-hour"
downward pressure the Stoll & Whaley triple-witching-hour literature
documents. Entry is a fixed CT clock time (well before the harness's own
15:08/15:10 CT new-position/flatten cutoffs -- see the timing note below),
hold LAST_MINUTES_BEFORE_CLOSE minutes, then flatten.

LOWEST DATA-RISK HYPOTHESIS IN THIS FAMILY: the witching calendar (3rd
Friday of Mar/Jun/Sep/Dec) is fully computable from ``bar.trade_date``
already on disk, with no external date table needed and no [unverified]
entries -- unlike H1/H2, there is nothing here that could be wrong because a
web fetch was blocked.

SUBSUMES THE "INDEX RECONSTITUTION" SCOPE ITEM: S&P 500 quarterly
reconstitution also takes effect on the same 3rd-Friday date. The
reconstitution literature's headline effect (single-name inclusion/exclusion
price pressure) is a stock-SELECTION effect that does not mechanically
transfer to an index-level future the way it does to the added/deleted
single names -- MES has no "additions" or "deletions" -- so no separate
reconstitution-direction hypothesis is proposed here. H3 is framed broadly
enough (abnormal range/volume, not just direction) to be the right place to
catch any residual index-future-specific effect from that same date, but
this file's TESTABLE, SCREENABLE rule is the last-half-hour directional
pressure specifically, because a pure "is range/volume abnormal" finding is
not itself a round-trip P&L series that ``funnel.power_gate.screen`` can
evaluate.

SOURCE CITATION: classic Stoll & Whaley "triple witching hour" literature
(increased last-half-hour volume; a detectable pre-1987 DOWNWARD price
pressure into the close, which diminished after CME's 1987 move to
open-based settlement for index futures/options), corroborated qualitatively
by multiple independent secondary sources on the same well-established
mechanism. The primary CME-authored articles on this exact mechanism
("Navigating the S&P 500 Rebalance", the month-end futures product article)
could not be retrieved this session (repeated cmegroup.com timeouts,
consistent with the blocking behavior data/cme_calendar.py already
documents) and remain unread; this file relies on the classic Stoll &
Whaley literature and its secondary corroboration only.

FALSIFICATION-FIRST FRAMING: because the settlement-mechanics change that
diminished the pre-1987 pressure happened almost four decades before this
repository's 2025-2026 MES sample, this hypothesis is run primarily to
FALSIFY a residual short-into-the-close effect, not to hunt for one --
finding nothing here is the expected, literature-consistent result.

TIMING NOTE: ``rules/xfa_rules.py`` blocks new positions from 15:08 CT and
force-flattens at 15:10 CT, every trade date. ENTRY_CT_TIME = 14:30 CT with
LAST_MINUTES_BEFORE_CLOSE = 30 puts this rule's entry and self-managed exit
(15:00 CT) safely inside that boundary; it is not the CME's own official
close clock, only a fixed within-harness proxy for "the last half hour of
the session."

Parameters (ONE setting, chosen before any backtest was run):
    ENTRY_CT_TIME = 14:30 CT
    LAST_MINUTES_BEFORE_CLOSE = 30 minutes  (Stoll & Whaley's "last half hour")
    QUANTITY_MICROS = 1

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the measured T;
  (b) that pass uses the MEASURED p and R, not a hand-picked grid point;
  (c) a first-fold pass is re-run across all 8 train folds and the ROBUST
      verdict does not flip to "fail" on most of them;
  (d) N.B. there are only 4 witching Fridays per year, so at most 3-4 in
      TRAIN slice of any one 142-day fold; ANY apparent pass here is, by
      construction, a 3-4-trade result and must be reported as such --
      not treated as comparable in strength to a hypothesis firing daily.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) with typically 3-4 closed round trips per train fold, "refute" here
      realistically means "no support was found in a low-N, literature-
      consistent-with-null setting," not a high-confidence rejection --
      report the trade count explicitly alongside any verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from zoneinfo import ZoneInfo

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

CT_TZ = ZoneInfo("America/Chicago")
ENTRY_CT_TIME = time(14, 30)
LAST_MINUTES_BEFORE_CLOSE = 30
QUANTITY_MICROS = 1
_WITCHING_MONTHS = frozenset({3, 6, 9, 12})


def is_quarterly_witching_friday(trade_date: date) -> bool:
    """3rd Friday of March / June / September / December: 15 <= day <= 21, weekday Friday."""
    return (
        trade_date.month in _WITCHING_MONTHS
        and trade_date.weekday() == 4  # Friday
        and 15 <= trade_date.day <= 21
    )


@dataclass(frozen=True)
class H3QuarterlyWitchingShort:
    """Short the last LAST_MINUTES_BEFORE_CLOSE minutes of a quarterly witching Friday."""

    name: str = "h3_quarterly_witching_short"
    entry_ct_time: time = ENTRY_CT_TIME
    last_minutes_before_close: int = LAST_MINUTES_BEFORE_CLOSE
    quantity_micros: int = QUANTITY_MICROS
    _entered_today: list[object] = field(default_factory=lambda: [None])
    _hold_bars_elapsed: list[int] = field(default_factory=lambda: [-1])

    def __post_init__(self) -> None:
        if not isinstance(self.entry_ct_time, time):
            raise ValueError(f"entry_ct_time {self.entry_ct_time!r} must be a time")
        if self.last_minutes_before_close < 1:
            raise ValueError(
                f"last_minutes_before_close {self.last_minutes_before_close!r} must be >= 1"
            )
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        if self._entered_today[0] is not None and self._entered_today[0] != bar.trade_date:
            self._entered_today[0] = None
            self._hold_bars_elapsed[0] = -1

        if account.position_micros != 0 and self._hold_bars_elapsed[0] >= 0:
            self._hold_bars_elapsed[0] += 1
            if self._hold_bars_elapsed[0] >= self.last_minutes_before_close:
                side = "sell" if account.position_micros > 0 else "buy"
                self._hold_bars_elapsed[0] = -1
                return (market_intent(bar, side, abs(account.position_micros)),)

        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        already_entered = self._entered_today[0] == bar.trade_date
        bar_ct_time = bar.decision_ts_utc.astimezone(CT_TZ).time()
        eligible = (
            flat and not already_entered
            and is_quarterly_witching_friday(bar.trade_date)
            and bar_ct_time >= self.entry_ct_time
        )
        if eligible:
            self._entered_today[0] = bar.trade_date
            self._hold_bars_elapsed[0] = 0
            return (market_intent(bar, "sell", self.quantity_micros),)
        return ()
