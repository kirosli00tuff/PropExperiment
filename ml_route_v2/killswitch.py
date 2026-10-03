"""Kill switches KS1-KS5 of ML route v2 (docs/STAGE_E_ML_V2_DESIGN.md V2.8, the table; F10).

``KillSwitches`` is a frozen state; every transition returns a new state.
- KS1 daily loss stop: the day's P&L (realized + unrealized) <= -KS1_DAILY_LOSS_FRACTION x D_open,
  or -DLL when the DLL was added and is nearer: flatten all, no entry for the rest of the date.
- KS2 drawdown-distance stop: D < KS2_HALF_SIZE_BELOW x MLL -> size multiplier KS2_SIZE_MULTIPLIER
  until D >= KS2_HALF_SIZE_BELOW x MLL (read at each entry from the D of that moment).
- KS2b drawdown-distance halt: D < KS2B_HALT_BELOW x MLL -> no new entries; the account halts
  pending the user's review (sticky; the backtest reports "halted", not ruin).
- KS3 consecutive-loss stop: KS3_LOSING_DATES consecutive losing trade dates -> no entries on the
  next trade date; the counter resets. A date with P&L >= 0 (no trade included) breaks the run.
- KS4 live-versus-expected drift: paper and live only; ``ks4_fires`` reports when it would fire.
- KS5 stale data: no entry when the product's latest closed bar is older than
  KS5_STALE_ENTRY_MIN minutes at t or an input is missing (``ks5_blocks_entry``); the 5-minute
  flatten is live only (``ks5_flatten_due`` for the live code).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from math import isfinite, sqrt

from ml_route_v2.constants import (
    KS1_DAILY_LOSS_FRACTION,
    KS2_HALF_SIZE_BELOW,
    KS2_SIZE_MULTIPLIER,
    KS2B_HALT_BELOW,
    KS3_LOSING_DATES,
    KS4_SE_MULTIPLE,
    KS4_WINDOW_DATES,
    KS5_STALE_ENTRY_MIN,
    KS5_STALE_FLATTEN_MIN,
)

NS_PER_MIN = 60_000_000_000
NS_PER_BAR = NS_PER_MIN  # a one-minute bar closes 60 s after its open


@dataclass(frozen=True)
class KillSwitches:
    """KS1-KS3 state of one account (KS4 and KS5 are stateless checks below)."""

    mll_usd: float
    dll_usd: float | None = None  # set when the DLL was added
    d_open: float = 0.0
    ks1_tripped: bool = False  # for the current trade date
    halted: bool = False  # KS2b, sticky
    losing_streak: int = 0
    skip_today: bool = False  # KS3 on the current trade date

    def __post_init__(self) -> None:
        if not (isfinite(self.mll_usd) and self.mll_usd > 0):
            raise ValueError(f"killswitch_bad_mll: {self.mll_usd!r}")

    # -- the trade date ----------------------------------------------------------------------
    def start_day(self, d_open: float) -> KillSwitches:
        """A new trade date: KS1 re-arms; KS3 blocks this date after a full losing run (and
        resets the counter); KS2b halts when D_open is already below its threshold."""
        skip = self.losing_streak >= KS3_LOSING_DATES
        return replace(self, d_open=d_open, ks1_tripped=False, skip_today=skip,
                       losing_streak=0 if skip else self.losing_streak,
                       halted=self.halted or d_open < KS2B_HALT_BELOW * self.mll_usd)

    def end_day(self, day_pnl: float) -> KillSwitches:
        """KS3's counter after the date's final P&L."""
        return replace(self, losing_streak=self.losing_streak + 1 if day_pnl < 0 else 0)

    # -- intraday ----------------------------------------------------------------------------
    def ks1_threshold(self) -> float:
        """The loss (positive dollars) at which KS1 fires on this date."""
        limit = KS1_DAILY_LOSS_FRACTION * self.d_open
        return min(limit, self.dll_usd) if self.dll_usd is not None else limit

    def on_day_pnl(self, day_pnl_now: float) -> KillSwitches:
        """KS1 on the date's running P&L (realized + unrealized)."""
        if self.ks1_tripped or day_pnl_now > -self.ks1_threshold():
            return self
        return replace(self, ks1_tripped=True)

    def on_entry(self, d_now: float) -> tuple[KillSwitches, bool]:
        """KS2b at an entry (sticky halt), then whether any switch blocks the entry."""
        state = self
        if not self.halted and d_now < KS2B_HALT_BELOW * self.mll_usd:
            state = replace(self, halted=True)
        allowed = not (state.halted or state.ks1_tripped or state.skip_today)
        return state, allowed

    def size_multiplier(self, d_now: float) -> float:
        """KS2: half size while D < 0.50 x MLL."""
        return KS2_SIZE_MULTIPLIER if d_now < KS2_HALF_SIZE_BELOW * self.mll_usd else 1.0

    @property
    def entries_blocked(self) -> bool:
        return self.halted or self.ks1_tripped or self.skip_today


def ks4_fires(daily_pnl: Sequence[float], mu_expected: float, sd_expected: float,
              window: int = KS4_WINDOW_DATES) -> bool:
    """KS4: the trailing ``window``-date mean daily P&L < mu - KS4_SE_MULTIPLE x sd / sqrt(window).
    Fewer than ``window`` dates: it cannot fire yet."""
    if len(daily_pnl) < window:
        return False
    tail = list(daily_pnl)[-window:]
    return sum(tail) / window < mu_expected - KS4_SE_MULTIPLE * sd_expected / sqrt(window)


def ks5_blocks_entry(latest_bar_open_ns: int | None, decision_ts_ns: int,
                     inputs_complete: bool) -> bool:
    """KS5 at an entry: a missing input, or the latest closed bar older than 2 minutes at t."""
    if not inputs_complete or latest_bar_open_ns is None:
        return True
    age_ns = decision_ts_ns - (latest_bar_open_ns + NS_PER_BAR)
    return age_ns > KS5_STALE_ENTRY_MIN * NS_PER_MIN


def ks5_flatten_due(latest_bar_open_ns: int | None, now_ns: int) -> bool:
    """KS5 in a position (live only): no bar for 5 minutes -> flatten at the next bar."""
    if latest_bar_open_ns is None:
        return True
    return now_ns - (latest_bar_open_ns + NS_PER_BAR) >= KS5_STALE_FLATTEN_MIN * NS_PER_MIN


__all__ = ["KillSwitches", "ks4_fires", "ks5_blocks_entry", "ks5_flatten_due"]
