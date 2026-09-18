"""H4 -- Full-session overnight(ETH)-vs-RTH return decomposition.

PRE-REGISTRATION (written before this strategy was ever run on any fold).

Mechanism: the same dealer-inventory/liquidity-provision story as H1,
generalized -- return accrual is structurally uneven across the full session
cycle, with a disproportionate share historically earned outside regular
trading hours (ETH: the overnight session) rather than during RTH.

Source: Cooper, Cliff & Gulen (2008) and Bondarenko & Muravyev (2023, JFQA)
as cited (Bondarenko-Muravyev headline numbers explicitly marked
UNVERIFIED -- SSRN-gated, no free mirror found) inside Glasserman,
Krstovski, Laliberte & Mamaysky, "Does Overnight News Explain Overnight
Returns?" (arXiv 2507.04481, 2025), whose own verified text states both
papers "find over-intra outperformance in S&P 500 index futures."

Why this is the family's parent/baseline decomposition: it is the same
clock-defined ETH/RTH split that H1 (a specific one-hour sub-window of ETH)
and H2 (a specific 30-minute sub-window of RTH) are special cases of. Testing
it is a pure clock split -- no price-level conditioning -- computable
directly from the session boundary already encoded in ``bar.trade_date``
(one CME trade date spans the whole ETH+RTH cycle, from 17:00 CT the prior
evening through that afternoon's close) and the ET wall-clock RTH window
shared with H2/H3.

Why BOTH legs are pre-registered LONG (not one long / one short): the cited
literature's finding is a RELATIVE one -- ETH earns more of the day's total
return than RTH, not necessarily that RTH is expected to lose money in
isolation. Testing long-only in both legs lets the two closed-round-trip
ledgers be compared directly (same direction, same instrument, same cost
model) to see where the account's P&L actually concentrates, without
presupposing a sign for the RTH leg that the mechanism does not claim. This
is 2 pre-specified trials -- ``session="eth"`` and ``session="rth"`` -- run
and reported together, both counting toward the family's multiple-
comparisons denominator.

Formalization: for ``session="eth"``, enter long at the FIRST bar of a new
trade date (the session's own open), exit unconditionally at the first bar
whose decision time enters RTH (09:30 ET). For ``session="rth"``, enter long
at the first bar whose decision time enters RTH (09:30 ET), exit
unconditionally at the first bar whose decision time reaches RTH close
(16:00 ET). Each leg trades at most once per trade date.

Parameters (ONE split; RTH boundary shared with H2/H3, no independent
tuning):
    RTH_OPEN_ET, RTH_CLOSE_ET = 09:30, 16:00
    QUANTITY_MICROS = 1
    session in {"eth", "rth"}  -- both pre-specified, both run

SUPPORT CONDITION: measured on TRAIN folds only, from the closed-round-trip
ledger, after the modelled $2.64/RT MES cost. This hypothesis is read as a
DECOMPOSITION, not a single pass/fail: "support" for the classic
over-intra-outperformance pattern requires ALL of:
  (a) the ETH leg clears the ROBUST verdict from
      funnel.power_gate.screen(..., robust=True) as "pass" (or at least
      shows a materially larger measured edge -- higher p*R at similar T -
      than the RTH leg), at the nearest available segments_per_day grid
      point to the measured T (T=1 by construction for either leg);
  (b) the RTH leg does NOT clear the ROBUST verdict at a comparable or
      better level than the ETH leg (if RTH clears it just as well, that
      contradicts the decomposition story, not confirms it);
  (c) both legs' measured p/R/T are the actual ledger figures, not
      hand-picked grid points;
  (d) any ETH-leg pass replicates across all 8 train folds per the task's
      re-run requirement, without the ROBUST verdict flipping fold to fold;
  (e) the ETH-leg result is read jointly with H1's result (H1 is a specific
      one-hour sub-window of this same ETH leg): if H1 shows no residual
      drift in its narrower window but this broader ETH leg does, the
      driving hours must be identified before either is trusted, not simply
      reported as two independent confirmations of the same thing.

REFUTE CONDITION: ANY of the following is sufficient to refute the
"ETH structurally outperforms RTH for MES on this sample" pattern:
  (a) neither leg clears the ROBUST verdict on its first fold;
  (b) net P&L over the closed round trips is <= $0 after cost for the ETH
      leg specifically;
  (c) the RTH leg clears the ROBUST verdict at least as well as the ETH leg
      (the classic pattern would not survive a strict cost/power screen for
      MES's specific research window);
  (d) the MATCHED verdict passes but the ROBUST verdict does not, for the
      ETH leg;
  (e) trades per day is necessarily ~1 by construction per leg, so fewer
      than ~30 closed round trips over a fold's train window is
      UNDERPOWERED and must be reported as such, not folded into a
      pass/fail count.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from rules.xfa_rules import OrderIntent, Refusal
from strategy.interface import AccountView, Bar, market_intent
from strategy.research.a_session_clock._clock import is_rth

QUANTITY_MICROS = 1
SESSIONS = ("eth", "rth")


@dataclass(frozen=True)
class H4EthVsRthDecomposition:
    """Long-only, once per trade date, in exactly one of the ETH or RTH clock legs.

    ``session`` is a pre-registered strategy parameter, not a tuned one -- see the
    module docstring: both "eth" and "rth" are formalized and screened together.
    """

    session: str
    name: str = "h4_eth_vs_rth_decomposition"
    quantity_micros: int = QUANTITY_MICROS
    _current_trade_date: list[date | None] = field(default_factory=lambda: [None])
    _traded_today: list[bool] = field(default_factory=lambda: [False])

    def __post_init__(self) -> None:
        if self.session not in SESSIONS:
            raise ValueError(f"session {self.session!r} must be one of {SESSIONS}")
        if isinstance(self.quantity_micros, bool) or not isinstance(self.quantity_micros, int) \
                or self.quantity_micros <= 0:
            raise ValueError(f"quantity_micros {self.quantity_micros!r} must be a positive int")

    def _reset_on_new_session(self, bar: Bar) -> bool:
        """Returns True exactly on the first bar processed for a new trade date."""
        is_new = self._current_trade_date[0] != bar.trade_date
        if is_new:
            self._current_trade_date[0] = bar.trade_date
            self._traded_today[0] = False
        return is_new

    def _eth_on_bar(self, bar: Bar, account: AccountView, is_new_day: bool
                    ) -> tuple[OrderIntent | Refusal, ...]:
        rth_now = is_rth(bar.decision_ts_utc)
        if account.position_micros != 0 and rth_now:
            return (market_intent(bar, "sell", abs(account.position_micros)),)
        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        if flat and not self._traded_today[0] and is_new_day and not rth_now:
            self._traded_today[0] = True
            return (market_intent(bar, "buy", self.quantity_micros),)
        return ()

    def _rth_on_bar(self, bar: Bar, account: AccountView
                    ) -> tuple[OrderIntent | Refusal, ...]:
        rth_now = is_rth(bar.decision_ts_utc)
        if account.position_micros != 0 and not rth_now:
            return (market_intent(bar, "sell", abs(account.position_micros)),)
        flat = account.position_micros == 0 and account.pending_signed_micros == 0
        if flat and not self._traded_today[0] and rth_now:
            self._traded_today[0] = True
            return (market_intent(bar, "buy", self.quantity_micros),)
        return ()

    def on_bar(self, bar: Bar, account: AccountView) -> tuple[OrderIntent | Refusal, ...]:
        is_new_day = self._reset_on_new_session(bar)
        if self.session == "eth":
            return self._eth_on_bar(bar, account, is_new_day)
        return self._rth_on_bar(bar, account)
