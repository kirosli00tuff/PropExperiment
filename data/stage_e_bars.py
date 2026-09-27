"""Stage E bar loading with trade-date refusals (Stage E.2b Task 1, design D4, rulings L-8 and L-9).

The only way the generalized screening runner (screening/stage_e_runner.py) reads bars.

Two stores, each under an explicit root the caller passes (never assumed to be REPO_ROOT/data, so
the Windows backend runs the same code on another machine):
- research: ``<research_root>/<ROOT>/ohlcv-1m_<ROOT>_v_0_2025-04-01_2026-06-19_research.parquet``
  (data/build_bars.py; MES's own research parquet has the same name and schema). Its sha256 must
  equal the value E.2a recorded (screening.stage_e_frozen).
- confirmation (step 2): ``data.step2_store.step2_parquet_path(root, step2_root)`` (Task 4's
  builder; trade dates 2019-05-06..2024-02-29, S_X not applied in the store). A missing module or
  file is refused by name (``ConfirmationStoreMissing``); the caller cuts at S_X. Its sha256 must
  equal the one the start-rule file recorded for the root (the store S_X was computed from,
  review F-3); the caller passes it, there is no default.

Every row is booked to its CME trade date by the product's GROUP calendar
(data.group_session.assign_trade_dates, the builder's own call with the close-minute rule L-3),
never by timestamp, and the loader refuses the whole leg when any row:
- books to no trade date the calendar can show (a minute past the calendar's coverage could be a
  holdout-1 minute): ``TradeDateUnbookable``;
- books to a holdout-1 trade date (>= 2026-06-22), a holdout-2 trade date (2024-04-01..2025-03-31)
  or an embargo trade date (March 2024): ``HoldoutRowRefused``. This is how MBT's 1,617 bars of
  2026-06-18 16:02 CT .. 2026-06-20, which CME books to trade date 2026-06-22 (ruling L-9), are
  refused even when the file labels them otherwise;
- carries a ``trade_date`` label that differs from its calendar booking: ``TradeDateMismatch``;
- lies outside the store's own range (research 2025-04-01..2026-06-19; step 2
  2019-05-06..2024-02-29): ``HoldoutRowRefused`` (class "outside the store").
The check runs on the whole file before any row is returned, so a refused file yields nothing.

Roll blackouts (L-8): the splice trade dates are the ``rolls`` metadata instants booked by the
group calendar; the blackout is the splice date and the two group trade dates before it
(data.group_session.roll_blackout). Where the file's metadata records its own splice or blackout
dates (the Stage E builds do; MES's older parquet does not), they must agree, else refused.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from data.group_session import (
    GroupCalendar,
    assign_trade_dates,
    load_group_calendar,
    open_intervals,
    roll_blackout,
    trade_date_of_instant,
)
from data.research_bars import EMBARGO2_END, EMBARGO2_START, HOLDOUT2_END, HOLDOUT2_START
from data.splits import HOLDOUT_START
from rules.products import product

RESEARCH_FIRST_TRADE_DATE = date(2025, 4, 1)
RESEARCH_LAST_TRADE_DATE = date(2026, 6, 19)
STEP2_FIRST_TRADE_DATE = date(2019, 5, 6)
CONFIRMATION_LAST_TRADE_DATE = date(2024, 2, 29)
HOLDOUT1_FIRST_TRADE_DATE = HOLDOUT_START  # 2026-06-22
ROLL_BLACKOUT_SESSIONS = 2  # NULL_CRITERIA_E 4: the splice date and the two sessions before it
BOOKING_MARGIN_DAYS = 7
BAR_COLUMNS = (
    "ts_event", "open", "high", "low", "close", "volume", "instrument_id", "raw_symbol",
    "trade_date", "in_flatten_window", "in_no_new_positions_window", "early_halt_ct",
    "in_scheduled_closure", "is_roll_session", "gap_before_minutes", "vendor_degraded_day",
)
RESEARCH = "research"
STEP2 = "step2"


class StageEBarRefusal(RuntimeError):
    """The bars cannot be used; nothing is returned."""


class HoldoutRowRefused(StageEBarRefusal):
    """A row is booked to a holdout-1, holdout-2, embargo or out-of-store trade date."""


class TradeDateUnbookable(StageEBarRefusal):
    """A row books to no trade date the group calendar can show."""


class TradeDateMismatch(StageEBarRefusal):
    """A row's trade_date label differs from its group-calendar booking."""


class ConfirmationStoreMissing(StageEBarRefusal):
    """The step 2 store (module or file) does not exist."""


class ParquetHashMismatch(StageEBarRefusal):
    """A research parquet differs from the file E.2a recorded."""


class RollMetadataMismatch(StageEBarRefusal):
    """The file's recorded splice or blackout dates disagree with the group calendar."""


# ------------------------------------------------------------- date classes ----
def forbidden_class(day: date) -> str | None:
    """The holdout class of a trade date, or None when Stage E may read it at all."""
    if day >= HOLDOUT1_FIRST_TRADE_DATE:
        return "holdout-1"
    if HOLDOUT2_START <= day <= HOLDOUT2_END:
        return "holdout-2"
    if EMBARGO2_START <= day <= EMBARGO2_END:
        return "embargo (March 2024)"
    return None


def store_range(store: str) -> tuple[date, date]:
    if store == RESEARCH:
        return RESEARCH_FIRST_TRADE_DATE, RESEARCH_LAST_TRADE_DATE
    if store == STEP2:
        return STEP2_FIRST_TRADE_DATE, CONFIRMATION_LAST_TRADE_DATE
    raise ValueError(f"unknown store {store!r}")


def refuse_trade_dates(root: str, days: Iterable[date], store: str, where: str) -> None:
    """HoldoutRowRefused naming the first offending date of each class."""
    first, last = store_range(store)
    bad: dict[str, date] = {}
    for d in days:
        cls = forbidden_class(d) or (None if first <= d <= last else f"outside the {store} store "
                                     f"({first}..{last})")
        if cls is not None and (cls not in bad or d < bad[cls]):
            bad[cls] = d
    if bad:
        detail = "; ".join(f"{cls} (first {d})" for cls, d in sorted(bad.items()))
        raise HoldoutRowRefused(f"{where}: {root} rows booked to forbidden trade dates: {detail}")


# ----------------------------------------------------------------- booking ----
def _utc_date(ns: int) -> date:
    return datetime.fromtimestamp(ns / 1e9, tz=UTC).date()


def book_trade_dates(cal: GroupCalendar, ts_ns: np.ndarray) -> list[date | None]:
    """Each instant's CME trade date on the group calendar (L-3 close-minute rule); None when no
    covered open interval follows."""
    ts = np.asarray(ts_ns, dtype=np.int64)
    if not len(ts):
        return []
    lo = _utc_date(int(ts.min())) - timedelta(days=BOOKING_MARGIN_DAYS)
    hi = _utc_date(int(ts.max())) + timedelta(days=BOOKING_MARGIN_DAYS)
    opened = open_intervals(cal, lo, hi)
    return assign_trade_dates(opened, ts, close_minute_to_previous=True).as_dates()


def check_bookings(root: str, cal: GroupCalendar, frame: pd.DataFrame, store: str,
                   where: str) -> tuple[date, ...]:
    """Refuse the frame unless every row books to an allowed trade date equal to its label.
    Returns each row's trade date."""
    booked = book_trade_dates(cal, frame["ts_event"].to_numpy())
    unbookable = [i for i, d in enumerate(booked) if d is None]
    if unbookable:
        ns = int(frame["ts_event"].iloc[unbookable[0]])
        raise TradeDateUnbookable(
            f"{where}: {len(unbookable)} {root} rows book to no trade date the {cal.group} "
            f"calendar can show (first {datetime.fromtimestamp(ns / 1e9, tz=UTC).isoformat()}); "
            "past the calendar's coverage a row could belong to holdout-1")
    days = tuple(d for d in booked if d is not None)
    refuse_trade_dates(root, set(days), store, where)
    labels = frame["trade_date"].astype(str).to_numpy()
    mismatch = [i for i, (lab, d) in enumerate(zip(labels, days, strict=True))
                if lab != d.isoformat()]
    if mismatch:
        i = mismatch[0]
        raise TradeDateMismatch(f"{where}: {len(mismatch)} {root} rows labelled with a trade date "
                                f"other than their {cal.group}-calendar booking (first: label "
                                f"{labels[i]}, booked {days[i]})")
    return days


# ------------------------------------------------------------------- rolls ----
def _meta(path: Path) -> dict:
    import pyarrow.parquet as pq

    raw = pq.read_schema(path).metadata or {}
    if b"propexperiment" not in raw:
        raise RollMetadataMismatch(f"{path}: no propexperiment metadata (rolls unknown)")
    return json.loads(raw[b"propexperiment"])


def splices_and_blackout(root: str, cal: GroupCalendar, meta: dict, where: str
                         ) -> tuple[tuple[date, ...], frozenset[date]]:
    """Splice trade dates (group calendar, L-8) and their roll blackout, checked against the
    file's own record when it has one."""
    rolls = meta.get("rolls")
    if rolls is None:
        raise RollMetadataMismatch(f"{where}: {root} metadata has no rolls")
    instants = [int(r["ts_ns"]) for r in rolls]
    if instants:
        lo = _utc_date(min(instants)) - timedelta(days=BOOKING_MARGIN_DAYS)
        hi = _utc_date(max(instants)) + timedelta(days=BOOKING_MARGIN_DAYS)
        opened = open_intervals(cal, lo, hi)
        booked = [trade_date_of_instant(opened, ns) for ns in instants]
    else:
        booked = []
    if any(d is None for d in booked):
        raise RollMetadataMismatch(f"{where}: a {root} splice books to no trade date")
    splices = tuple(sorted({d for d in booked if d is not None}))
    blackout = roll_blackout(cal, splices, ROLL_BLACKOUT_SESSIONS)
    recorded = meta.get("splice_trade_dates")
    if recorded is not None and tuple(sorted(date.fromisoformat(d) for d in recorded)) != splices:
        raise RollMetadataMismatch(f"{where}: {root} recorded splice dates differ from the group "
                                   "calendar's booking of its rolls")
    rec_black = meta.get("roll_blackout_dates")
    if rec_black is not None and frozenset(date.fromisoformat(d) for d in rec_black) != blackout:
        raise RollMetadataMismatch(f"{where}: {root} recorded roll-blackout dates differ from the "
                                   "group calendar's (L-8)")
    return splices, blackout


# ------------------------------------------------------------------ frames ----
@dataclass(frozen=True)
class LegFrame:
    """One leg's bars, checked. ``frame`` holds BAR_COLUMNS, sorted by ts_event."""

    root: str
    store: str
    path: str
    sha256: str
    frame: pd.DataFrame
    trade_dates: tuple[date, ...]  # every trade date with bars, ascending
    splice_trade_dates: tuple[date, ...]
    roll_blackout: frozenset[date]


def research_parquet_path(root: str, research_root: Path) -> Path:
    from data.build_bars import research_parquet_path as _path

    return _path(root, Path(research_root))


def _step2_parquet_path(root: str, step2_root: Path) -> Path:
    try:
        from data.step2_store import step2_parquet_path
    except ImportError as exc:  # the store's builder is Task 4's; until it exists, refuse
        raise ConfirmationStoreMissing(f"data.step2_store is not available ({exc}); the step 2 "
                                       "store has not been built") from exc
    return Path(step2_parquet_path(root, Path(step2_root)))


def _sha256(path: Path) -> str:
    from screening.stage_e_frozen import sha256_file

    return sha256_file(path)


def _checked_expected(expected_sha256: object, where: str) -> str:
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(
            c not in "0123456789abcdef" for c in expected_sha256):
        raise ValueError(f"{where}: expected sha256 {expected_sha256!r} is not a sha256; every "
                         "store read is pinned (no default)")
    return expected_sha256


def _check_hash(path: Path, expected_sha256: str, where: str) -> str:
    digest = _sha256(path)
    if digest != expected_sha256:
        raise ParquetHashMismatch(f"{where}: sha256 {digest[:12]}... is not the recorded "
                                  f"{expected_sha256[:12]}...")
    return digest


def read_leg(root: str, path: Path, store: str, *, expected_sha256: str) -> LegFrame:
    """Read and check one leg's parquet (every refusal above). ``expected_sha256``: research, the
    E.2a record; step 2, the start-rule file's record for the root (review F-3)."""
    path = Path(path)
    where = f"{store} bars {path.name}"
    _checked_expected(expected_sha256, where)
    if not path.is_file():
        cls = ConfirmationStoreMissing if store == STEP2 else StageEBarRefusal
        raise cls(f"{where}: {path} does not exist")
    digest = _check_hash(path, expected_sha256, where)
    frame = pd.read_parquet(path, columns=list(BAR_COLUMNS))
    frame = frame.sort_values("ts_event", kind="stable").reset_index(drop=True)
    if frame["ts_event"].duplicated().any():
        raise StageEBarRefusal(f"{where}: duplicate bar timestamps")
    cal = load_group_calendar(product(root).group)
    days = check_bookings(root, cal, frame, store, where)
    splices, blackout = splices_and_blackout(root, cal, _meta(path), where)
    return LegFrame(root, store, str(path), digest, frame, tuple(sorted(set(days))), splices,
                    blackout)


def load_research_leg(root: str, research_root: Path, *, expected_sha256: str) -> LegFrame:
    return read_leg(root, research_parquet_path(root, research_root), RESEARCH,
                    expected_sha256=expected_sha256)


def load_confirmation_leg(root: str, step2_root: Path, start: date, *,
                          expected_sha256: str) -> LegFrame:
    """The step 2 store's bars from ``start`` (S_X) through 2024-02-29. The file must hash to
    ``expected_sha256`` (the store the start rule read, review F-3); the whole file is booked and
    checked first; then the frame is cut at S_X."""
    if not STEP2_FIRST_TRADE_DATE <= start <= CONFIRMATION_LAST_TRADE_DATE:
        raise ValueError(f"S_X {start} is outside {STEP2_FIRST_TRADE_DATE}.."
                         f"{CONFIRMATION_LAST_TRADE_DATE}")
    leg = read_leg(root, _step2_parquet_path(root, step2_root), STEP2,
                   expected_sha256=expected_sha256)
    keep = np.array([date.fromisoformat(d) >= start
                     for d in leg.frame["trade_date"].astype(str).to_numpy()], dtype=bool)
    frame = leg.frame[keep].reset_index(drop=True)
    days = tuple(d for d in leg.trade_dates if d >= start)
    return LegFrame(root, STEP2, leg.path, leg.sha256, frame, days, leg.splice_trade_dates,
                    leg.roll_blackout)


def read_leg_dates(root: str, step2_root: Path, start: date, *, expected_sha256: str
                   ) -> tuple[tuple[date, ...], frozenset[date]]:
    """The step 2 store's trade dates from ``start`` (S_X) and its roll blackout, reading only
    the timestamp and trade-date columns (no price): the confirmation supply of D4's power check.
    Every refusal of ``read_leg`` applies, the pinned sha256 included (review F-3)."""
    if not STEP2_FIRST_TRADE_DATE <= start <= CONFIRMATION_LAST_TRADE_DATE:
        raise ValueError(f"S_X {start} is outside {STEP2_FIRST_TRADE_DATE}.."
                         f"{CONFIRMATION_LAST_TRADE_DATE}")
    path = _step2_parquet_path(root, step2_root)
    where = f"{STEP2} dates {path.name}"
    _checked_expected(expected_sha256, where)
    if not path.is_file():
        raise ConfirmationStoreMissing(f"{where}: {path} does not exist")
    _check_hash(path, expected_sha256, where)
    frame = pd.read_parquet(path, columns=["ts_event", "trade_date"])
    frame = frame.sort_values("ts_event", kind="stable").reset_index(drop=True)
    cal = load_group_calendar(product(root).group)
    days = check_bookings(root, cal, frame, STEP2, where)
    _, blackout = splices_and_blackout(root, cal, _meta(path), where)
    return tuple(sorted({d for d in days if d >= start})), blackout


def restrict(leg: LegFrame, dates: Sequence[date]) -> pd.DataFrame:
    """The leg's bars on ``dates`` only (the engine's feed for a window)."""
    wanted = {d.isoformat() for d in dates}
    mask = leg.frame["trade_date"].astype(str).isin(wanted).to_numpy()
    return leg.frame[mask].reset_index(drop=True)


__all__ = [
    "BAR_COLUMNS", "CONFIRMATION_LAST_TRADE_DATE", "HOLDOUT1_FIRST_TRADE_DATE", "RESEARCH",
    "RESEARCH_FIRST_TRADE_DATE", "RESEARCH_LAST_TRADE_DATE", "ROLL_BLACKOUT_SESSIONS", "STEP2",
    "STEP2_FIRST_TRADE_DATE", "ConfirmationStoreMissing", "HoldoutRowRefused", "LegFrame",
    "ParquetHashMismatch", "RollMetadataMismatch", "StageEBarRefusal", "TradeDateMismatch",
    "TradeDateUnbookable", "book_trade_dates", "check_bookings", "forbidden_class",
    "load_confirmation_leg", "load_research_leg", "read_leg", "read_leg_dates",
    "refuse_trade_dates",
    "research_parquet_path", "restrict", "splices_and_blackout", "store_range",
]
