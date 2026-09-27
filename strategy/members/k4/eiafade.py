"""K4-eiafade-01, post-WPSR overreaction fade (Stage E.4; specs section 6; C 588-659).

MCL only (q_c 4). Event set (K4-L-03): every row of _releases.WPSR (section 11's drops already
out) whose T_W + 15 <= 13:13 CT, T_W = the release instant in CT (K4-L-02); that keeps the 09:30,
10:00, 11:00 and 12:00 CT slots and leaves out the 16:00 CT row.
- signal: t0 = ticks(close of the bar at T_W - 1), t14 = ticks(close of the bar at T_W + 14);
  M = (t14 - t0) / t0 needs t0 > 0 (C10), else no trade;
- guard (S0.9): the T_W - 1 and T_W + 14 bars present and carrying one instrument_id;
- entry (K4-L-05, exact integers): BUY if 200 x (t14 - t0) <= -t0 (M <= -0.005), SELL if
  200 x (t14 - t0) >= t0 (M >= +0.005), else no trade; market intent on the bar at T_W + 14,
  filling at the T_W + 15 open; no entry when that bar is missing (S0.6) or carries
  early_halt_ct (S0.8);
- exit: market intent on the first present bar at or after 13:28 (C - 2), filling nominally at
  the 13:29 open (S0.7).
A date not in the table is not traded.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal

from rules.products import product
from rules.xfa_rules import Refusal
from screening.stage_e_frozen import load_frozen_tables
from strategy.members.k4._event_common import (
    BUY,
    SELL,
    check_exposure,
    clock_minute,
    ct_open_ns,
    exit_items,
    price_ticks,
)
from strategy.members.k4._releases import WPSR
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
    leg_market_intent,
)

MEMBER_ID = "K4-eiafade-01"
EXPOSURES = ("MCL",)  # C 592-593; vehicles: crude -> MCL
BASE_OFFSET_MIN = -1  # the bar at T_W - 1 (C 611-612)
ENTRY_DECISION_OFFSET_MIN = 14  # the bar at T_W + 14; fills at the T_W + 15 open (C 613-617)
ENTRY_FILL_OFFSET_MIN = 15  # the 15-minute measurement window (C 627-635)
LATEST_ENTRY_FILL_CT = time(13, 13)  # T_W + 15 <= 13:13 CT (C 608-610)
EXIT_DECISION_CT = time(13, 28)  # the first bar at or after 13:28, the ports' C - 2 (C 618-620)
THRESHOLD_DENOMINATOR = 200  # |M| >= 0.005 = 1 / 200 of the T_W - 1 close (C 613-617, K4-L-05)
TRADING_WINDOWS = (TradingInterval(time(9, 29), time(13, 30)),)  # S0.12


def release_minutes(wpsr: Sequence[tuple[str, str, int, bool]]) -> dict[date, int]:
    """Release date -> T_W as a CT clock minute, for the rows with T_W + 15 <= 13:13 CT."""
    latest = clock_minute(LATEST_ENTRY_FILL_CT)
    return {date.fromisoformat(day): clock_minute(t_w) for day, t_w, _weekday, _standard in wpsr
            if clock_minute(t_w) + ENTRY_FILL_OFFSET_MIN <= latest}


def fade_side(t0: int, t14: int) -> str | None:
    """The entry side from the two closes in integer ticks (K4-L-05), or None: no trade.
    t0 <= 0 is C10's non-positive denominator: no trade."""
    if t0 <= 0:
        return None
    scaled_move = THRESHOLD_DENOMINATOR * (t14 - t0)
    if scaled_move <= -t0:
        return BUY
    if scaled_move >= t0:
        return SELL
    return None


@dataclass
class EiaFade:
    root: str
    wpsr: tuple[tuple[str, str, int, bool], ...] = WPSR  # the frozen table; a test may pass another
    name: str = field(init=False)
    legs: tuple[LegSpec, ...] = field(init=False)
    trading_windows: dict = field(init=False)
    _q: int = field(init=False)
    _tick: Decimal = field(init=False)
    _releases: Mapping[date, int] = field(init=False)
    _day: date | None = field(default=None, init=False)
    _base_ns: int | None = field(default=None, init=False)
    _entry_ns: int | None = field(default=None, init=False)
    _exit_ns: int | None = field(default=None, init=False)
    _base: tuple[int, int] | None = field(default=None, init=False)  # (t0, instrument_id)
    _entry_done: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        check_exposure(self.root, EXPOSURES, MEMBER_ID)
        self.name = f"{MEMBER_ID} {self.root}"
        self.legs = (LegSpec(self.root, True),)
        self.trading_windows = {self.root: TRADING_WINDOWS}
        self._q = load_frozen_tables().vehicles[self.root].q_c
        self._tick = product(self.root).vendor_tick
        self._releases = release_minutes(self.wpsr)

    def _new_day(self, day: date) -> None:
        t_w = self._releases.get(day)
        self._day = day
        self._entry_done = False
        self._base = None
        self._base_ns = None if t_w is None else ct_open_ns(day, t_w + BASE_OFFSET_MIN)
        self._entry_ns = None if t_w is None else ct_open_ns(day, t_w + ENTRY_DECISION_OFFSET_MIN)
        self._exit_ns = None if t_w is None else ct_open_ns(day, clock_minute(EXIT_DECISION_CT))

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> tuple[LegIntent | Refusal, ...]:
        bar = view.bar(self.root)
        if bar is None:  # no bar: no decision at this minute (never forward fill)
            return ()
        if bar.trade_date != self._day:
            self._new_day(bar.trade_date)
        if bar.ts_event_ns == self._base_ns:
            self._base = (price_ticks(bar.close, self._tick), bar.instrument_id)
        if account.position(self.root):
            return exit_items(view, account, self.root, self._exit_ns)
        if self._entry_done or bar.ts_event_ns != self._entry_ns:
            return ()
        self._entry_done = True  # the named entry bar is exact: one chance per trade date
        if account.pending.get(self.root, 0) or bar.early_halt_ct is not None:
            return ()
        if self._base is None or self._base[1] != bar.instrument_id:
            return ()  # the T_W - 1 bar is missing or on another contract (C4 guard)
        side = fade_side(self._base[0], price_ticks(bar.close, self._tick))
        if side is None:
            return ()  # |M| below 0.005, or C10 (t0 <= 0)
        return (leg_market_intent(view, self.root, side, self._q),)


def make_mcl() -> EiaFade:
    return EiaFade("MCL")


__all__ = ["EiaFade", "fade_side", "make_mcl", "release_minutes"]
