"""Stage E.14 (harness v10): the loader of the hist bar stores (data.hist_store).

    leg = load_hist_leg("ES", "es2011", expected_sha256=<the store's sha256>)

Gives the ``data.stage_e_bars.LegFrame`` shape the step 2 loader gives (BAR_COLUMNS, sorted by
ts_event, the trade dates, the splice trade dates and the roll blackout), read only from the
plan's store under HIST_ROOT and pinned by sha256 (no default). Every row is booked to its CME
trade date by the root's HIST group calendar (data.hist_calendar, the L-3 close-minute rule),
never by timestamp, and the whole leg is refused when any row:
- books to no trade date the hist calendar can show (``TradeDateUnbookable``);
- books to a trade date outside the plan's window or to a holdout trade date
  (``HoldoutRowRefused``);
- books to an UNSOURCED calendar date (``UnsourcedRowRefused``; the store drops those rows);
- carries a trade_date label other than its booking (``TradeDateMismatch``).
The file's metadata must name the plan and the same hist calendar file (sha256) the loader reads
(``HistStoreMismatch``). The roll blackout is the splice trade date and the two group trade dates
before it (data/stage_e_bars.py:30-33, ``splices_and_blackout``), on the hist calendar.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from data.config import HIST_ROOT
from data.group_session import group_of
from data.hist_calendar import HIST_CALENDAR_DIR, HistGroupCalendar, load_hist_group_calendar
from data.hist_store import hist_parquet_path
from data.pull_hist import get_plan
from data.stage_e_bars import (
    BAR_COLUMNS,
    HoldoutRowRefused,
    LegFrame,
    StageEBarRefusal,
    TradeDateMismatch,
    TradeDateUnbookable,
    _check_hash,
    _checked_expected,
    _meta,
    book_trade_dates,
    forbidden_class,
    splices_and_blackout,
)


class UnsourcedRowRefused(StageEBarRefusal):
    """A row is booked to an unsourced calendar date (C1 ruling C12, C2 section 3)."""


class HistStoreMismatch(StageEBarRefusal):
    """The file's metadata names another plan or another hist calendar file."""


def hist_store_name(plan: str) -> str:
    return f"hist:{plan}"


def check_hist_bookings(root: str, plan: str, cal: HistGroupCalendar, frame: pd.DataFrame,
                        where: str) -> tuple[date, ...]:
    """Refuse the frame unless every row books to a sourced trade date of the plan's window,
    equal to its label. Returns each row's trade date."""
    p = get_plan(plan)
    booked = book_trade_dates(cal, frame["ts_event"].to_numpy())
    if any(d is None for d in booked):
        raise TradeDateUnbookable(f"{where}: {sum(d is None for d in booked)} {root} rows book "
                                  f"to no trade date the {cal.group} hist calendar can show")
    days = tuple(d for d in booked if d is not None)
    distinct = set(days)
    outside = sorted(d for d in distinct if forbidden_class(d) is not None
                     or not p.first_trade_date <= d <= p.last_trade_date)
    if outside:
        raise HoldoutRowRefused(f"{where}: {root} rows booked outside the {plan} store "
                                f"({p.first_trade_date}..{p.last_trade_date}), first {outside[0]}")
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


def load_hist_leg(root: str, plan: str, *, expected_sha256: str, hist_root: Path = HIST_ROOT,
                  calendar_base: Path = HIST_CALENDAR_DIR,
                  calendar: HistGroupCalendar | None = None) -> LegFrame:
    """Read and check one root's hist store of ``plan`` (every refusal above). ``calendar``: an
    already loaded hist calendar of the root's group (else it is loaded from ``calendar_base``)."""
    p = get_plan(plan)
    if root not in p.roots:
        raise StageEBarRefusal(f"{root!r} is not a root of plan {plan}")
    path = hist_parquet_path(root, plan, Path(hist_root))
    where = f"{hist_store_name(plan)} bars {path.name}"
    _checked_expected(expected_sha256, where)
    if not path.is_file():
        raise StageEBarRefusal(f"{where}: {path} does not exist")
    digest = _check_hash(path, expected_sha256, where)
    cal = calendar or load_hist_group_calendar(group_of(root), base=calendar_base)
    if cal.group != group_of(root):
        raise HistStoreMismatch(f"{where}: calendar {cal.group} is not {root}'s group")
    meta = _meta(path)
    recorded = (meta.get("hist_calendar") or {}).get("sha256")
    if meta.get("plan") != plan or recorded != cal.file_sha256:
        raise HistStoreMismatch(f"{where}: the file was built for plan {meta.get('plan')!r} on "
                                f"calendar sha256 {str(recorded)[:12]}..., not {plan} on "
                                f"{cal.file_sha256[:12]}...")
    frame = pd.read_parquet(path, columns=list(BAR_COLUMNS))
    frame = frame.sort_values("ts_event", kind="stable").reset_index(drop=True)
    if frame["ts_event"].duplicated().any():
        raise StageEBarRefusal(f"{where}: duplicate bar timestamps")
    days = check_hist_bookings(root, plan, cal, frame, where)
    splices, blackout = splices_and_blackout(root, cal, meta, where)
    return LegFrame(root, hist_store_name(plan), str(path), digest, frame,
                    tuple(sorted(set(days))), splices, blackout)


__all__ = ["HistStoreMismatch", "UnsourcedRowRefused", "check_hist_bookings", "hist_store_name",
           "load_hist_leg"]
