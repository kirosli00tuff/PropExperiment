"""The engine's limit-lock test on every fill (freeze review F-07, lead ruling).

screening/stage_e_rules.py StageERules._locked, called per fill: on a hard-limit product
(rules.price_limits.HARD_LIMIT_PRODUCTS) with a LIMITS period on the fill's trade date (the
table starts 2019-05-01), the prior settlement proxy is D9.7's (pl.settlement_proxy over the
prior trade date's bars in pl.settlement_window_utc: the VWAP of the closes in the window, else
the last close before its end; the prior trade date from the 2019-on group calendar, as the
engine's previous_trade_date); band = pl.limit_band(root, trade date, the fill bar's open, s);
up, down = pl.limit_prices(band, s); a buy is locked when the bar's low >= up, a sell when its
high <= down. A locked fill excludes the unit ("limit locked"). No reference, a pending limit
period, or a date before the table: no lock can be shown (the engine's reading RR-4).
Prices as the engine sees them: Decimal(repr(float)) of the vendor price.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import numpy as np

from base_rules.store import ProductBars
from data.group_session import GroupCalendar, previous_trade_date
from rules import price_limits as pl
from rules.products import PRICE_SCALE, product

NS = 1_000_000_000


def _utc(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / NS, tz=UTC)


class LockRule:
    """``rule(i, trade)``: True when a fill of signed ``trade`` contracts at bar ``i`` is locked."""

    def __init__(self, bars: ProductBars, frozen_cal: GroupCalendar) -> None:
        self.bars, self.cal = bars, frozen_cal
        self.root = bars.root
        self.tick = product(self.root).vendor_tick_fixed
        self.active = (self.root in pl.HARD_LIMIT_PRODUCTS and bars.high_t is not None
                       and bars.low_t is not None and bars.volume is not None)
        self._proxy: dict[date, Decimal | None] = {}
        self.pending = 0  # fills whose limit period is pending or absent (diagnostic)

    def _price(self, ticks: int) -> Decimal:
        return Decimal(repr(ticks * self.tick / PRICE_SCALE))

    def prior_settlement(self, day: date) -> Decimal | None:
        if day in self._proxy:
            return self._proxy[day]
        prev = previous_trade_date(self.cal, day)
        value = None
        if prev is not None:
            w0, w1 = pl.settlement_window_utc(self.root, prev)
            b = self.bars
            lo = int(np.searchsorted(b.ts, int(w0.timestamp() * NS) - 3600 * NS * 24))
            hi = int(np.searchsorted(b.ts, int(w1.timestamp() * NS)))
            prints = [pl.BarPrint(_utc(int(b.ts[k])), self._price(int(b.close_t[k])),
                                  int(b.volume[k]))
                      for k in range(lo, hi) if int(b.td[k]) == prev.toordinal()]
            got = pl.settlement_proxy(prints, w0, w1)
            value = None if got is None else got.value
        self._proxy[day] = value
        return value

    def __call__(self, i: int, trade: int) -> bool:
        if not self.active:
            return False
        day = date.fromordinal(int(self.bars.td[i]))
        if day < pl.TABLE_WINDOW[0]:
            return False
        s = self.prior_settlement(day)
        if s is None:
            return False
        try:
            band = pl.limit_band(self.root, day, _utc(int(self.bars.ts[i])), s)
        except (pl.LimitPending, KeyError):
            self.pending += 1
            return False
        up, down = pl.limit_prices(band, s)
        hi = self._price(int(self.bars.high_t[i]))
        lo = self._price(int(self.bars.low_t[i]))
        if trade < 0:
            return down is not None and hi <= down
        return up is not None and lo >= up


__all__ = ["LockRule"]
