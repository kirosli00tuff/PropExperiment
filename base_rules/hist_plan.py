"""The 2010-2019 store of a root under its fixed plan (freeze review F-01, lead ruling).

C1's frozen plan "ext2010" holds NG, NQ, ZN, 6E, GC and ZC; the 21 other roots are bought by E.17
under plan "ext2010h" (constants.HIST_PLAN_OF). The run manifest's ext2010 entry carries
{"path", "sha256", "plan"} and a plan other than the root's fixed one is refused. The file is
<base>/<plan>/<ROOT>/ohlcv-1m_<ROOT>_v_0_<first>_<last>_<plan>.parquet (data.hist_store.
hist_parquet_path's layout) with last == 2019-04-30 and 2010-06-06 <= first <= the product's
window start; first and last are read from the name, must equal the plan's window from the plan
resolver (data.pull_hist.get_plan by default; injectable, since harness v10 has no "ext2010h"),
and the file's metadata must name the plan and hold its trade_date_range inside them. Rows are
booked as data.hist_bars.check_hist_bookings books them (the frozen booking, the plan window,
unsourced and holdout refusals), with the plan's window from the resolver.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from base_rules import constants as K
from data.hist_bars import UnsourcedRowRefused
from data.stage_e_bars import (
    HoldoutRowRefused,
    StageEBarRefusal,
    TradeDateMismatch,
    TradeDateUnbookable,
    book_trade_dates,
    forbidden_class,
)

NAME = re.compile(r"ohlcv-1m_(?P<root>[A-Z0-9]+)_v_0_(?P<first>\d{4}-\d{2}-\d{2})_"
                  r"(?P<last>\d{4}-\d{2}-\d{2})_(?P<plan>[a-z0-9]+)\.parquet")


class PlanRefused(StageEBarRefusal):
    """A hist store's plan, name or metadata is not the root's fixed plan."""


@dataclass(frozen=True)
class PlanWindow:
    name: str
    first_trade_date: date
    last_trade_date: date


def default_resolver(plan: str) -> PlanWindow:
    from data.pull_hist import get_plan

    p = get_plan(plan)
    return PlanWindow(p.name, p.first_trade_date, p.last_trade_date)


Resolver = Callable[[str], PlanWindow]


def fixed_plan(root: str, plan: str | None) -> str:
    want = K.HIST_PLAN_OF[root]
    if plan != want:
        raise PlanRefused(f"{root}: ext2010 store under plan {plan!r}; its fixed plan is {want!r}")
    return want


def expected_name(root: str, plan: str, first: date, last: date) -> str:
    return f"ohlcv-1m_{root}_v_0_{first}_{last}_{plan}.parquet"


def check_name(root: str, plan: str, path: Path) -> tuple[date, date]:
    """(first, last) from the file name, every layout rule of the module docstring checked."""
    fixed_plan(root, plan)
    path = Path(path)
    m = NAME.fullmatch(path.name)
    if m is None or m["root"] != root or m["plan"] != plan:
        raise PlanRefused(f"{path.name}: not ohlcv-1m_{root}_v_0_<first>_<last>_{plan}.parquet")
    if path.resolve().parent.name != root or path.resolve().parent.parent.name != plan:
        raise PlanRefused(f"{path}: not under <base>/{plan}/{root}/")
    first, last = date.fromisoformat(m["first"]), date.fromisoformat(m["last"])
    if last != K.HIST_LAST or not K.HIST_FIRST_MIN <= first <= K.WINDOW_START[root]:
        raise PlanRefused(f"{path.name}: trade dates {first}..{last}, not <first in "
                          f"{K.HIST_FIRST_MIN}..{K.WINDOW_START[root]}>..{K.HIST_LAST}")
    return first, last


def check_plan(root: str, plan: str, first: date, last: date, meta: dict[str, Any],
               resolver: Resolver, where: str) -> PlanWindow:
    """The plan window equals the name's; the metadata names the plan and its data lie inside."""
    window = resolver(plan)
    if (window.first_trade_date, window.last_trade_date) != (first, last):
        raise PlanRefused(f"{where}: plan {plan} spans {window.first_trade_date}.."
                          f"{window.last_trade_date}, the file name {first}..{last}")
    if meta.get("plan") != plan:
        raise PlanRefused(f"{where}: metadata plan {meta.get('plan')!r} is not {plan!r}")
    rng = meta.get("trade_date_range")
    if not isinstance(rng, list) or len(rng) != 2:
        raise PlanRefused(f"{where}: metadata has no trade_date_range")
    lo, hi = date.fromisoformat(str(rng[0])), date.fromisoformat(str(rng[1]))
    if not first <= lo <= hi <= last:
        raise PlanRefused(f"{where}: metadata trade_date_range {lo}..{hi} is outside "
                          f"{first}..{last}")
    return window


def check_bookings(root: str, window: PlanWindow, cal: Any, frame: pd.DataFrame,  # noqa: ANN401
                   where: str) -> tuple[date, ...]:
    """data.hist_bars.check_hist_bookings with the plan window given (same order, same
    refusals): every row books to a sourced trade date of the window, equal to its label."""
    booked = book_trade_dates(cal, frame["ts_event"].to_numpy())
    if any(d is None for d in booked):
        raise TradeDateUnbookable(f"{where}: {sum(d is None for d in booked)} {root} rows book "
                                  f"to no trade date the {cal.group} hist calendar can show")
    days = tuple(d for d in booked if d is not None)
    distinct = set(days)
    outside = sorted(d for d in distinct if forbidden_class(d) is not None
                     or not window.first_trade_date <= d <= window.last_trade_date)
    if outside:
        raise HoldoutRowRefused(f"{where}: {root} rows booked outside the {window.name} store "
                                f"({window.first_trade_date}..{window.last_trade_date}), first "
                                f"{outside[0]}")
    unsourced = sorted(distinct & cal.unsourced)
    if unsourced:
        raise UnsourcedRowRefused(f"{where}: {root} rows booked to {len(unsourced)} unsourced "
                                  f"calendar date(s), first {unsourced[0]}")
    labels = frame["trade_date"].astype(str).to_numpy()
    mismatch = [i for i, (lab, d) in enumerate(zip(labels, days, strict=True))
                if lab != d.isoformat()]
    if mismatch:
        i = mismatch[0]
        raise TradeDateMismatch(f"{where}: {len(mismatch)} {root} rows labelled with a trade date "
                                f"other than their hist-calendar booking (first: label "
                                f"{labels[i]}, booked {days[i]})")
    return days


__all__ = ["NAME", "PlanRefused", "PlanWindow", "Resolver", "check_bookings", "check_name",
           "check_plan", "default_resolver", "expected_name", "fixed_plan"]
