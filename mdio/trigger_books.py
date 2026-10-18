"""The E.23 trigger-hold read of one root with its book files (Stage E.24, V41; NOTE-5).

``read_root_books`` is trigger_hold.evaluate.read_root (frozen by the E.23 freeze, which also
refuses any new file in trigger_hold/) mirrored statement for statement, returning the same
records plus the per-root book record (mdio.book_files.per_root_record) built from the very
RootData, units and BookResults the records come from. The frozen file's sha256 is pinned in
MIRRORED_SHA256: tests/test_mdio_book_files.py fails if it changes, so the mirror is reviewed;
the same test checks the records equal read_root's on a synthetic root. One statement is added
before the mirror: ``check_bounded(ctx)``, so this path never reads bars past ctx.last.
"""

from __future__ import annotations

import gc
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from base_rules.common import RunContext, load_or_exclude, lock_rule
from mdio.book_files import per_root_record
from mdio.bounded import check_bounded
from trigger_hold import constants as K
from trigger_hold.book import (
    book_summary,
    buy_hold_returns,
    daily_series,
    prepare_root,
    regressor_on,
    unit_book,
)
from trigger_hold.config import TriggerHold
from trigger_hold.power import nonoverlapping
from trigger_hold.stats import case_record
from trigger_hold.trend import load_trend
from trigger_hold.units import BarMarks, book_days, build_units, in_market_fraction, window_for

MIRRORED_SHA256 = {
    "trigger_hold/evaluate.py": "bb3c59e3c0ea3ea9e2406fe29481d7b0ea0251a4efc8299e0b9da022a146b8d8",
}


def read_root_books(ctx: RunContext, root: str, ths: Sequence[TriggerHold], window: str, *,
                    trend_dir: Path = K.TREND_DIR, use_locks: bool = True
                    ) -> tuple[dict[str, dict], dict | None]:
    """(trigger_hold.evaluate.read_root's records, the per-root book record or None when the
    store is refused). The bound is mandatory: ``ctx.load_bars`` must be a
    mdio.bounded.BoundedLoader bound to ctx.last (mdio.bounded.bound_context), checked before
    any load; otherwise BoundBreached, which is not a refusal and stops the run (A2 review
    SHOULD-FIX-2)."""
    check_bounded(ctx)
    notes: dict = {}
    load_counts: Counter = Counter()
    bars = load_or_exclude(ctx, root, load_counts, notes)
    if bars is None:
        return {th.id: {"status": "store refused", "notes": notes} for th in ths}, None
    locks = lock_rule(ctx, bars) if use_locks else None
    rd = prepare_root(ctx, bars, root, locks=locks)
    src = BarMarks(ctx, bars, root, rd.path.marks)
    staged = {}
    for th in ths:
        ev = th.events_file(window)
        win = window_for(src, window, th.s_x)
        units, ucounts = build_units(src, ev.events if ev else (), win, m=th.m, h=th.h)
        staged[th.id] = (th, win, units, ucounts, book_days(src, win, units))
    del bars, locks, src
    gc.collect()
    trend = load_trend(root, trend_dir)
    bh_counts: Counter = Counter()
    bh = buy_hold_returns(rd, bh_counts)
    out, books, units_of = {}, {}, {}
    for tid, (th, win, units, ucounts, days) in staged.items():
        book = unit_book(rd, units)
        books[tid], units_of[tid] = book, units
        c: Counter = Counter()
        series = daily_series(book, days, c)
        dates = [d for d, _ in series[K.BASE]]
        x1, x2 = regressor_on(trend["T1"], dates), regressor_on(trend["T2"], dates)
        x3 = regressor_on(bh, dates)
        out[tid] = {"status": "read", "root": root, "window": window, "first": str(win.first),
                    "last": str(win.last), "m": th.m, "h": th.h, "units": len(units),
                    "nonoverlapping": nonoverlapping(units), "n_dates": len(dates),
                    "in_market_fraction_units": in_market_fraction(units, dates),
                    "buy_hold_counts": dict(bh_counts),
                    "unit_counts": dict(sorted(ucounts.items())),
                    "book_counters": dict(sorted((book.counters + c).items())),
                    **book_summary(book),
                    "cases": {cs: case_record(series[cs], x1, x2, th.h, x3) for cs in K.CASES},
                    "series": {cs: [[str(d), v] for d, v in series[cs]] for cs in K.CASES}}
    return out, per_root_record(rd, books, units_of)


__all__ = ["MIRRORED_SHA256", "read_root_books"]
