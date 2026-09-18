"""H1 -- Scheduled-macro-announcement drift (pre-FOMC / pre-CPI / pre-NFP).

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: on a trade date carrying a known, scheduled FOMC statement release
(2:00pm ET) or a known, scheduled CPI/NFP release (8:30am ET), go long once
at the very start of that trade date's session and hold through to just
before the release, then flatten. This directly targets the pre-announcement
"risk premium" drift Lucca & Moench (2011/2015, NY Fed SR512) document on the
E-mini S&P 500 futures contract itself (49bp average 24h pre-FOMC drift,
Sharpe > 1.1) and the elevated announcement-related excess return Savor &
Wilson (2013, JFQA) document pooled across CPI/PPI/employment/FOMC days
(11.4bp vs 1.1bp on non-announcement days, 1958-2009). Both anchor papers use
the E-mini S&P 500 (or the index it tracks) directly, so mechanism transfer
to MES is about as close as this research program gets.

HARNESS-COMPATIBILITY ADAPTATION (a designed substitution, stated up front,
not discovered after a bad result): ``rules/xfa_rules.py`` enforces a hard,
non-overridable flatten at 15:10 CT and blocks new positions from 15:08 CT,
on EVERY trade date -- ``data/splits.py`` states this plainly: "positions are
flat by 15:10 CT ... no position ever spans a trade-date boundary." That
means this harness can never replicate Lucca & Moench's literal 24-hour,
close-to-close, through-the-overnight-halt holding window; ANY strategy in
this repository is structurally intraday-only. But "trade_date" in this
schema is NOT a calendar day -- ``data/session.py`` defines each trade
date's session as [D-1 17:00 CT reopen .. D's own ~15:10 CT flatten], i.e.
close to 22 continuous session-hours bundled under ONE trade_date label with
no flatten in between. Because FOMC's 2:00pm ET (1:00pm CT) release and
CPI/NFP's 8:30am ET (7:30am CT) release both fall on the SAME trade_date as
the calendar date they are published on, and well before that trade date's
own 15:08/15:10 CT cutoffs, entering at the FIRST bar of the release's own
trade_date and exiting right at the release timestamp reproduces ~14.5-20
hours of the literature's pre-announcement window inside a single,
harness-legal, non-flattened session -- the closest a strategy in this
harness can get to the papers' actual design, not a token same-day-only
proxy. This is recorded as a designed adaptation, not silently assumed.

FALSIFICATION-FIRST FRAMING: Kurov, Wolfe & Gilbert (2020) document the
pre-FOMC drift specifically weakening/disappearing after January 2016, on a
sample that predates this repository's 2025-2026 MES data by nearly a
decade. This hypothesis is therefore weighted, going in, toward "the classic
drift has decayed and should NOT be expected to reappear at 2011-2015
magnitude" -- H1 is run as much to falsify that prior finding's continued
relevance as to search for a live edge.

Calendar table (hardcoded, sourced; covers the RESEARCH_START..RESEARCH_END
window 2025-04-01..2026-06-12; all dates fetched directly from the primary
source pages on 2026-09-18, not from search-result snippets):

- FOMC statement dates: federalreserve.gov/monetarypolicy/fomccalendars.htm
  (the Fed's own meeting-calendar page). Statement release time 2:00pm ET is
  the FOMC's own stated release time for every regularly scheduled meeting.
- NFP (Employment Situation) dates: bls.gov/schedule/2025/home.htm and
  bls.gov/schedule/news_release/current_year.asp (BLS's own schedule pages),
  8:30am ET each. The 2025 government-shutdown lapse (Oct 2025) skipped a
  standalone September-2025 release; it was folded into the 2025-11-20
  release. The ACTUALLY-PUBLISHED date is used below (the market could not
  react to a release that never happened on the originally-scheduled date).
- CPI dates: same BLS schedule pages, 8:30am ET each. The 2025-10 CPI report
  (September data) actually published 2025-10-24; the following month's
  report was skipped and folded into the 2025-12-18 release covering
  November data (same shutdown). Again, the actually-published dates are
  used.
- No date below is [unverified]: every one was read directly off a
  federalreserve.gov or bls.gov page this session, not inferred or taken
  from a secondary summary.

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. Support requires ALL of:
  (a) the ROBUST verdict from funnel.power_gate.screen(..., robust=True) is
      "pass" at the nearest segments_per_day grid point to the measured T;
  (b) that pass uses the MEASURED p and R, not a hand-picked grid point;
  (c) the direction is consistent with the mechanism (net long, profiting on
      the pre-release session, not some other artifact of the fill/cost
      model);
  (d) a first-fold pass is re-run across all 8 train folds and the ROBUST
      verdict does not flip to "fail" on most of them -- a single lucky fold,
      especially given only ~9-14 release events of each type total across
      the whole research window, is not support.
Given the Kurov-Wolfe-Gilbert decay finding above, a pass here should be
treated with EXTRA scrutiny, not less -- it would be surprising by the
family's own cited literature.

REFUTE CONDITION: ANY of the following is sufficient to refute, at the
modelled cost:
  (a) the ROBUST verdict is "fail" or "marginal";
  (b) net P&L over the closed round trips is <= $0 after cost;
  (c) the MATCHED verdict passes but the ROBUST verdict does not;
  (d) fewer than ~20 closed round trips over the train sample (there are at
      most ~9 FOMC + ~14 NFP + ~14 CPI = 37 release dates in the FULL
      research window, so a single train fold has meaningfully fewer than
      that and this hypothesis is inherently low-N; that must be reported as
      an underpowered result, not folded into a clean pass/fail count).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent

ET_TZ = ZoneInfo("America/New_York")
QUANTITY_MICROS = 1

# ---- FOMC statement dates, federalreserve.gov/monetarypolicy/fomccalendars.htm, 2:00pm ET ----
_FOMC_STATEMENT_DATES: tuple[date, ...] = (
    date(2025, 5, 7), date(2025, 6, 18), date(2025, 7, 30), date(2025, 9, 17),
    date(2025, 10, 29), date(2025, 12, 10), date(2026, 1, 28), date(2026, 3, 18),
    date(2026, 4, 29),
)
_FOMC_RELEASE_ET = time(14, 0)

# ---- NFP (Employment Situation) dates, bls.gov schedule pages, 8:30am ET ----
_NFP_DATES: tuple[date, ...] = (
    date(2025, 4, 4), date(2025, 5, 2), date(2025, 6, 6), date(2025, 7, 3), date(2025, 8, 1),
    date(2025, 9, 5), date(2025, 11, 20), date(2025, 12, 16), date(2026, 1, 9),
    date(2026, 2, 11), date(2026, 3, 6), date(2026, 4, 3), date(2026, 5, 8), date(2026, 6, 5),
)

# ---- CPI dates, bls.gov schedule pages, 8:30am ET ----
_CPI_DATES: tuple[date, ...] = (
    date(2025, 4, 10), date(2025, 5, 13), date(2025, 6, 11), date(2025, 7, 15),
    date(2025, 8, 12), date(2025, 9, 11), date(2025, 10, 24), date(2025, 12, 18),
    date(2026, 1, 13), date(2026, 2, 13), date(2026, 3, 11), date(2026, 4, 10),
    date(2026, 5, 12), date(2026, 6, 10),
)
_CPI_NFP_RELEASE_ET = time(8, 30)


def _build_release_table() -> dict[date, datetime]:
    """One entry per release trade_date -> its ET release datetime. No date collides."""
    table: dict[date, datetime] = {}
    for release_date in _FOMC_STATEMENT_DATES:
        if release_date in table:
            raise ValueError(f"duplicate release date {release_date} in H1 calendar table")
        table[release_date] = datetime.combine(release_date, _FOMC_RELEASE_ET, tzinfo=ET_TZ)
    for release_date in (*_NFP_DATES, *_CPI_DATES):
        if release_date in table:
            raise ValueError(f"duplicate release date {release_date} in H1 calendar table")
        table[release_date] = datetime.combine(release_date, _CPI_NFP_RELEASE_ET, tzinfo=ET_TZ)
    return table


RELEASE_TABLE_ET: dict[date, datetime] = _build_release_table()


@dataclass(frozen=True)
class H1ScheduledMacroDrift:
    """Long from session-open to just-before-release, on known FOMC/CPI/NFP release dates."""

    name: str = "h1_scheduled_macro_drift"
    quantity_micros: int = QUANTITY_MICROS
    _current_trade_date: list[object] = field(default_factory=lambda: [None])
    _entered_for_date: list[object] = field(default_factory=lambda: [None])
    _release_ts_utc: list[object] = field(default_factory=lambda: [None])

    def __post_init__(self) -> None:
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        intents: tuple[OrderIntent | Refusal, ...] = ()
        is_new_session = self._current_trade_date[0] != bar.trade_date
        if is_new_session:
            self._current_trade_date[0] = bar.trade_date
            release_et = RELEASE_TABLE_ET.get(bar.trade_date)
            flat = account.position_micros == 0 and account.pending_signed_micros == 0
            if release_et is not None and flat:
                intents = (market_intent(bar, "buy", self.quantity_micros),)
                self._entered_for_date[0] = bar.trade_date
                self._release_ts_utc[0] = release_et.astimezone(UTC)

        waiting_to_exit = (
            self._entered_for_date[0] == bar.trade_date
            and self._release_ts_utc[0] is not None
            and account.position_micros != 0
        )
        if waiting_to_exit and bar.decision_ts_utc >= self._release_ts_utc[0]:
            side = "sell" if account.position_micros > 0 else "buy"
            intents = (*intents, market_intent(bar, side, abs(account.position_micros)))
            self._entered_for_date[0] = None
            self._release_ts_utc[0] = None
        return intents
