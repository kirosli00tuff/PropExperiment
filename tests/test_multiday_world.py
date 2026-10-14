"""Synthetic worlds for the multiday tests (no market data): bars at the settlement minute S and
S - 1 of each trade date, splices at 00:00 UTC, contexts from tests._base_rules_fixtures."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, date, datetime

import numpy as np

from base_rules import constants as BK
from base_rules.store import ProductBars
from multiday import constants as K
from tests._base_rules_fixtures import SM, calendars, context, make_bars, trade_dates

GROUPS = tuple(sorted({BK.GROUP_OF[r] for r in K.ROOTS}))


def utc_midnight(day: date) -> int:
    return int(datetime(day.year, day.month, day.day, tzinfo=UTC).timestamp()) * 10**9


def all_cals():  # noqa: ANN201
    return calendars(GROUPS)


def s_minute(root: str) -> int:
    return SM[BK.GROUP_OF[root]][0]


def world_bars(root: str, dates: Sequence[date], price: Callable[[date], int],
               symbol: Callable[[date], str] = lambda d: "C1",
               splices: Sequence[date] = (), blackout: Sequence[date] = (),
               extra_rows: Sequence[tuple] = ()) -> ProductBars:
    """Bars at S - 1 and S (open = close = price(d)) on ``dates``; a splice at 00:00 UTC of each
    date in ``splices`` (the date's own session; the old contract's last bar is the previous
    trade date's bar S)."""
    s = s_minute(root)
    rows = [(d, m, price(d), price(d), symbol(d)) for d in dates for m in (s - 1, s)]
    rows += list(extra_rows)
    sp = [(utc_midnight(d), d) for d in splices]
    return make_bars(root, rows, sp, blackout)


def walk_prices(dates: Sequence[date], *, drift: float, vol: float, seed: int,
                start: int = 400_000) -> dict[date, int]:
    rng = np.random.default_rng(seed)
    out, p = {}, float(start)
    for d in dates:
        p *= float(np.exp(drift + vol * rng.standard_normal()))
        out[d] = max(int(round(p)), 1)
    return out


def ctx_for(cals: Mapping, bars: Mapping[str, ProductBars], starts: Mapping[str, date] | None
            = None, releases=None):  # noqa: ANN001, ANN201
    return context(cals, bars, starts=starts, releases=releases)


def window(cal, first: date, last: date) -> list[date]:  # noqa: ANN001
    return trade_dates(cal, first, last)


def test_world_bars_sit_at_s_minus_one_and_s() -> None:
    cals = all_cals()
    days = window(cals["equity"], date(2016, 3, 1), date(2016, 3, 10))
    bars = world_bars("NQ", days, lambda d: 100 + d.day)
    assert bars.bar(days[0], 15 * 60) is not None and bars.bar(days[0], 15 * 60 - 1) is not None
    assert bars.bar(days[0], 15 * 60 + 1) is None
