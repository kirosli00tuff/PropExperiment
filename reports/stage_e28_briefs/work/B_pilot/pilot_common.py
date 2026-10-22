"""Stage E.28 Part B pilot: shared constants, request guards, sessions and day exclusions.

Used by pilot_pull.py (purchase), verify.py (manifest) and measure.py (spec sections 2 to 4).
Importing this module puts the repo root on sys.path, so the scripts run from anywhere as
``uv run python reports/stage_e28_briefs/work/B_pilot/<script>.py``. The repo's modules are
imported read-only; nothing here writes outside the paths a caller passes.

Conventions, stated once:
- Time is UTC nanoseconds (int). Request bounds are canonical strings: ``YYYY-MM-DD`` (00:00 UTC)
  or ``YYYY-MM-DDTHH:MM:SSZ`` (data.quote_universe.parse_utc / iso_z).
- The pilot request: GLBX.MDP3, mbp-1, ``QM.v.0`` (PILOT_ROOT, the frozen spec's one contract,
  section 0; pilot_pull.py refuses any other root in every mode, RD-01), stype_in continuous,
  on acct-3 only, end exactly 2024-02-29T22:00:00Z (exclusive; 16:00 CT, the end of CME trade
  date 2024-02-29, so no record of trade date 2024-03-01 is bought: frozen spec sections 0 and 6,
  RS-01; any other end is refused, RD-02). request_refusals stays root-generic (verify.py and
  measure.py read files of any calendar root); check_request adds the two pins.
- The minimum span (frozen spec section 6, RS-07 as corrected for QM) is
  [start_bound(2024-01-12), end): a request starting later is never bought. 2024-01-12 is the QM
  value (QM rolls monthly, so about 8 roll-day exclusions in four months); the QG value
  2024-01-18 of spec v1 is not used.
- A trade date D (spec section 2): the CME Globex trade date, 17:00 CT of D-1 to 16:00 CT of D.
  Its open time comes from the repo's group calendar (data.group_session.session_intervals:
  holidays, early halts, late opens, the daily maintenance halt and any intra-day pause).
- Record grouping: a record belongs to trade date D when its ts_recv lies in
  [D-1 16:00 CT, D 16:00 CT): the hour before the 17:00 CT open (the pre-open) seeds D's book.
- ``start_bound(D)`` = D-1 16:00 CT in UTC: a request starting there holds the whole of D.
- Sessions (spec section 2), in America/Vancouver clock time on the trade date: MAIN =
  06:30-13:00, OVERNIGHT = the rest of the trade date's open time. A "session piece" is one
  contiguous stretch of open time with one label (OVERNIGHT is usually two pieces: the evening
  to 06:30 and 13:00 to the 14:00 PT close). Placements: the 5-minute clock grid g with
  piece_lo + 5 min <= g < piece_hi - 5 min (first and last 5 minutes of every piece excluded;
  closed time, including the maintenance halt, holds no piece).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import re  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from datetime import UTC, date, datetime, time, timedelta  # noqa: E402
from typing import Any  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

import numpy as np  # noqa: E402

from data import holdout as ho  # noqa: E402
from data import trade_date_guard as tdg  # noqa: E402
from data.calendars import GROUP_OF_PRODUCT  # noqa: E402
from data.config import (  # noqa: E402
    ACCOUNT_3_CAP_USD,
    ACCOUNT_3_ID,
    DATASET,
    PILOT_ONLY_ACCOUNTS,
)
from data.group_session import GroupCalendar, load_group_calendar, session_intervals  # noqa: E402
from data.pull_universe import (  # noqa: E402
    EMBARGO_END_UTC,
    EMBARGO_START_UTC,
    MBP_1,
    WINDOW_END_UTC,
    WINDOW_START_UTC,
)
from data.quote_universe import iso_z, parse_utc  # noqa: E402
from data.session import CME_TZ, ct_ns  # noqa: E402
from data.spend_gate import RequestParams  # noqa: E402

# ------------------------------------------------------------------ constants ----
PILOT_ACCOUNT = ACCOUNT_3_ID
PILOT_ACCOUNT_CAP_USD = ACCOUNT_3_CAP_USD
PILOT_ROOT = "QM"  # frozen spec section 0: the one contract this pilot buys (RD-01)
PILOT_DATASET = DATASET  # GLBX.MDP3
PILOT_SCHEMA = MBP_1  # mbp-1
PILOT_STYPE_IN = "continuous"
CUTOFF_BOUND = "2024-02-29T22:00:00Z"  # exclusive request end: 16:00 CT, end of trade date 02-29
CUTOFF_UTC = datetime(2024, 2, 29, 22, 0, tzinfo=UTC)
CUTOFF_TRADE_DATE = date(2024, 3, 1)  # no trade date on or after it is ever measured
# verify.py: no record with ts_event at or after the 17:00 CT open of trade date 2024-03-01
# (2024-02-29T23:00:00Z); records in [22:00Z, 23:00Z) (the maintenance hour) are counted only.
CUTOFF_OPEN_NS = ct_ns(date(2024, 2, 29), time(17, 0))
LAST_PILOT_TRADE_DATE = date(2024, 2, 29)
# RS-07 (frozen spec section 6, "Corrected after review"): for QM the first trade date is no
# later than 2024-01-12, i.e. the minimum span is [2024-01-12, 2024-02-29T22:00Z): 26 usable
# trade dates after holiday and monthly-roll exclusions. (2024-01-18 was the QG value.)
MIN_SPAN_FIRST_TRADE_DATE = date(2024, 1, 12)
BALANCE_MARGIN_MIN_USD = 3.00  # RS-08: TARGET = B - max(3.00, 0.03 x B), down to the cent
BALANCE_MARGIN_SHARE = 0.03
DATASET_FIRST_DATE = date(2010, 6, 6)  # GLBX.MDP3 starts 2010-06-06 (data.pull_hist)
PILOT_VENDOR_ROOT = Path("/mnt/large-storage/market_data/PropExperiment/data/vendor/databento")
QUOTE_SESSION_ID = "stage-E.28-pilot"  # --quote and --buy (the buy uses this session's quote)
SPAN_SESSION_ID = "stage-E.28-pilot-span"  # --span-search quotes only
SESSION_ID_PREFIX = "stage-E.28-pilot"

PT = ZoneInfo("America/Vancouver")
CT = CME_TZ
MAIN_START_PT = time(6, 30)
MAIN_END_PT = time(13, 0)
DAY_BOUNDARY_CT = time(16, 0)
MAIN, OVERNIGHT = "MAIN", "OVERNIGHT"
SESSIONS = (MAIN, OVERNIGHT)

NS = 1_000_000_000
MS = 1_000_000
GRID_NS = 300 * NS
EDGE_NS = 300 * NS
LATENCY_NS = 50 * MS
LIFE_NS = 60 * NS
HORIZONS_S = (1, 10, 60)
MAX_MAIN_GAP_NS = 60 * NS

RC_OK, RC_STOPPED, RC_REFUSED = 0, 1, 2

_DAY = r"\d{4}-\d{2}-\d{2}"
_TOKEN = rf"{_DAY}(?:T\d{{6}}Z)?"
_RANGE_NAME = re.compile(rf"range=({_TOKEN})_({_TOKEN})\.dbn\.zst")


class PilotRefused(RuntimeError):
    """A pilot request, file or argument is outside what the pilot may touch."""


# ------------------------------------------------------------------ time helpers ----
def ns_of(moment: datetime) -> int:
    return int(moment.astimezone(UTC).timestamp()) * NS + moment.microsecond * 1000


def bound_ns(stamp: str) -> int:
    return ns_of(parse_utc(stamp))


def canonical_bound(stamp: str) -> datetime:
    """A request bound in canonical form, else PilotRefused (as data.pull_universe)."""
    try:
        moment = parse_utc(stamp)
    except ValueError as exc:
        raise PilotRefused(f"unparseable request bound {stamp!r}") from exc
    canonical = moment.date().isoformat() if "T" not in stamp else iso_z(moment)
    if canonical != stamp:
        raise PilotRefused(f"request bound {stamp!r} is not canonical ({canonical!r})")
    return moment


def pt_ns(day: date, at: time) -> int:
    return ns_of(datetime.combine(day, at, tzinfo=PT))


def iso_ns(ns: int) -> str:
    seconds, frac = divmod(int(ns), NS)
    return f"{datetime.fromtimestamp(seconds, UTC):%Y-%m-%dT%H:%M:%S}.{frac:09d}Z"


def local_iso(ns: int) -> str:
    return datetime.fromtimestamp(int(ns) / NS, PT).isoformat(timespec="milliseconds")


def start_bound(day: date) -> str:
    """The request start that holds trade date ``day`` whole: D-1 16:00 CT, in UTC."""
    return iso_z(datetime.combine(day - timedelta(days=1), DAY_BOUNDARY_CT, tzinfo=CT))


def day_window_ns(day: date) -> tuple[int, int]:
    """Record-grouping window of trade date ``day``: [D-1 16:00 CT, D 16:00 CT) by ts_recv."""
    return ct_ns(day - timedelta(days=1), DAY_BOUNDARY_CT), ct_ns(day, DAY_BOUNDARY_CT)


def day_boundaries(first: date, last: date) -> tuple[list[date], np.ndarray]:
    """Days first..last and the ns where each one's grouping window starts (sorted)."""
    days = [first + timedelta(days=n) for n in range((last - first).days + 1)]
    return days, np.array([day_window_ns(d)[0] for d in days], dtype=np.int64)


# ------------------------------------------------------------------ request guards ----
def symbol_for(root: str) -> str:
    return f"{root}.v.0"


def require_root(root: str) -> str:
    if root not in GROUP_OF_PRODUCT:
        raise PilotRefused(f"root {root!r} has no CME group calendar in data.calendars "
                           f"(known: {', '.join(sorted(GROUP_OF_PRODUCT))}); the lead decides")
    return root


def calendar_for(root: str) -> GroupCalendar:
    return load_group_calendar(GROUP_OF_PRODUCT[require_root(root)])


def pilot_params(root: str, start: str, end: str = CUTOFF_BOUND, *, dataset: str = PILOT_DATASET,
                 schema: str = PILOT_SCHEMA, symbol: str | None = None,
                 stype_in: str = PILOT_STYPE_IN) -> RequestParams:
    sym = symbol_for(root) if symbol is None else symbol
    return RequestParams(dataset, (sym,), schema, stype_in, start, end)


def require_account(account: str) -> str:
    if account != PILOT_ACCOUNT or account not in PILOT_ONLY_ACCOUNTS:
        raise PilotRefused(f"account {account!r} refused: the pilot buys on {PILOT_ACCOUNT} only "
                           "(V44, data.config.PILOT_ONLY_ACCOUNTS)")
    return account


def require_session_id(session_id: str) -> str:
    if not session_id.startswith(SESSION_ID_PREFIX):
        raise PilotRefused(f"session id {session_id!r} must start with {SESSION_ID_PREFIX!r}")
    return session_id


def window_refusals(start: str, end: str) -> list[str]:
    """Overlaps with the embargo and holdout 2, the research window and holdout 1 (the windows
    of data.pull_universe), and data.holdout's sealed-window check."""
    out = []
    s, e = parse_utc(start), parse_utc(end)
    if s < EMBARGO_END_UTC and e > EMBARGO_START_UTC:
        out.append(f"{start}..{end} touches the embargo and holdout 2 "
                   f"{iso_z(EMBARGO_START_UTC)}..{iso_z(EMBARGO_END_UTC)}")
    if s < WINDOW_END_UTC and e > WINDOW_START_UTC:
        out.append(f"{start}..{end} touches the research window "
                   f"{iso_z(WINDOW_START_UTC)}..{iso_z(WINDOW_END_UTC)}")
    if e > WINDOW_END_UTC:
        out.append(f"{start}..{end} reaches holdout 1 (from {iso_z(WINDOW_END_UTC)})")
    if ho.request_touches_sealed_window(start, end):
        out.append(f"{start}..{end} touches a sealed holdout window (data.holdout)")
    return out


def booking_refusals(root: str, start: str, end: str, cal: GroupCalendar) -> list[str]:
    """data.trade_date_guard's holdout-trade-date refusal on the part of [start, end) the
    group calendar covers (it cannot book minutes before its coverage)."""
    cover_from = datetime.combine(cal.coverage[0] + timedelta(days=8), time(0), tzinfo=UTC)
    lo = max(parse_utc(start), cover_from)
    if lo >= parse_utc(end):
        return []
    try:
        tdg.refuse_holdout_bookings(root, iso_z(lo), end)
    except tdg.TradeDateRefused as exc:
        return [f"trade-date guard: {exc}"]
    return []


def request_refusals(params: RequestParams, root: str) -> list[str]:
    """Every reason ``params`` is not the pilot request of ``root``; empty when admissible.
    Collects all reasons (a refusal names each), checked before any vendor call."""
    out: list[str] = []
    if root not in GROUP_OF_PRODUCT:
        out.append(f"root {root!r} has no CME group calendar in data.calendars")
    if params.dataset != PILOT_DATASET:
        out.append(f"dataset {params.dataset!r} refused: the pilot is {PILOT_DATASET} only")
    if params.schema != PILOT_SCHEMA:
        out.append(f"schema {params.schema!r} refused: the pilot is {PILOT_SCHEMA} only (B1)")
    if params.stype_in != PILOT_STYPE_IN:
        out.append(f"stype_in {params.stype_in!r} refused: {PILOT_STYPE_IN} only")
    if params.symbols != (symbol_for(root),):
        out.append(f"symbols {list(params.symbols)} refused: only {symbol_for(root)} "
                   "(the --root contract's volume-based continuous front)")
    try:
        s, e = canonical_bound(params.start), canonical_bound(params.end)
    except PilotRefused as exc:
        return [*out, str(exc)]
    if not s < e:
        out.append(f"empty or inverted window {params.start}..{params.end}")
    if e > CUTOFF_UTC:
        out.append(f"end {params.end} is after {CUTOFF_BOUND} (exclusive end, 16:00 CT on "
                   "2024-02-29): no record of trade date 2024-03-01 or later is bought")
    if s < datetime.combine(DATASET_FIRST_DATE, time(0), tzinfo=UTC):
        out.append(f"start {params.start} is before {PILOT_DATASET}'s first date "
                   f"{DATASET_FIRST_DATE}")
    out.extend(window_refusals(params.start, params.end))
    if root in GROUP_OF_PRODUCT and s < e:
        out.extend(booking_refusals(root, params.start, params.end, calendar_for(root)))
    return out


def min_span_refusal(start: str) -> str | None:
    """RS-07: the start must hold MIN_SPAN_FIRST_TRADE_DATE (2024-01-12 for QM) whole, i.e.
    start <= its start bound (2024-01-11T22:00:00Z)."""
    limit = start_bound(MIN_SPAN_FIRST_TRADE_DATE)
    if bound_ns(start) > bound_ns(limit):
        return (f"start {start} is later than {limit}, the start of the minimum span "
                f"[{MIN_SPAN_FIRST_TRADE_DATE}, {CUTOFF_BOUND}) (frozen spec section 6, RS-07): "
                "nothing is bought")
    return None


def margin_target(balance_usd: float) -> float:
    """RS-08: TARGET = B - max(3.00, 0.03 x B), rounded down to the cent."""
    from decimal import ROUND_FLOOR, Decimal

    b = Decimal(str(balance_usd))
    margin = max(Decimal(str(BALANCE_MARGIN_MIN_USD)), Decimal(str(BALANCE_MARGIN_SHARE)) * b)
    return float((b - margin).quantize(Decimal("0.01"), rounding=ROUND_FLOOR))


def pilot_root_refusal(root: str) -> str | None:
    """RD-01: the pilot buys the frozen spec's contract only (section 0: QM, QM.v.0)."""
    if root != PILOT_ROOT:
        return (f"root {root!r} refused: the frozen spec (section 0) fixes the pilot contract "
                f"at {PILOT_ROOT} ({symbol_for(PILOT_ROOT)}); no other contract is quoted or "
                "bought (RD-01)")
    return None


def require_pilot_root(root: str) -> str:
    reason = pilot_root_refusal(root)
    if reason:
        raise PilotRefused(reason)
    return root


def end_pin_refusal(end: str) -> str | None:
    """RD-02: the request end is exactly CUTOFF_BOUND (spec sections 0 and 6), so every bought
    span holds the whole minimum span once its start passes min_span_refusal."""
    if end != CUTOFF_BOUND:
        return (f"end {end} refused: the pilot request ends exactly at {CUTOFF_BOUND} (frozen "
                "spec sections 0 and 6, RD-02)")
    return None


def pilot_refusals(params: RequestParams, root: str) -> list[str]:
    """request_refusals plus the pilot's two pins: root = PILOT_ROOT, end = CUTOFF_BOUND."""
    pins = [r for r in (pilot_root_refusal(root), end_pin_refusal(params.end)) if r]
    return [*pins, *request_refusals(params, root)]


def check_request(params: RequestParams, root: str) -> RequestParams:
    reasons = pilot_refusals(params, root)
    if reasons:
        raise PilotRefused("; ".join(reasons))
    return params


# ------------------------------------------------------------------ DBN file guard ----
def parse_range_name(name: str) -> tuple[str, str] | None:
    match = _RANGE_NAME.fullmatch(name)
    if match is None:
        return None
    return tuple(_token_bound(t) for t in match.groups())  # type: ignore[return-value]


def _token_bound(token: str) -> str:
    if "T" not in token:
        return date.fromisoformat(token).isoformat()
    return iso_z(datetime.strptime(token, "%Y-%m-%dT%H%M%SZ").replace(tzinfo=UTC))


def file_name_refusals(path: Path, root: str) -> list[str]:
    """A pilot file sits at GLBX.MDP3/mbp-1/<ROOT>_v_0/range=<start>_<end>.dbn.zst with an end
    at or before CUTOFF_BOUND: research-window mbp-1 files in the same folder are never read."""
    path = Path(path)
    out = []
    bounds = parse_range_name(path.name)
    if bounds is None:
        return [f"{path.name}: not a range=<start>_<end>.dbn.zst file"]
    if parse_utc(bounds[1]) > CUTOFF_UTC:
        out.append(f"{path.name}: its range ends after {CUTOFF_BOUND}; refused unread")
    parts = path.parts[-4:-1]
    if tuple(parts) != (PILOT_DATASET, PILOT_SCHEMA, symbol_for(root).replace(".", "_")):
        out.append(f"{path}: not under {PILOT_DATASET}/{PILOT_SCHEMA}/"
                   f"{symbol_for(root).replace('.', '_')}/")
    return out


def metadata_refusals(meta: Any, root: str) -> list[str]:
    """The DBN header must describe exactly the pilot request."""
    out = []
    if str(meta.dataset) != PILOT_DATASET:
        out.append(f"metadata dataset {meta.dataset!r}")
    if str(meta.schema) != PILOT_SCHEMA:
        out.append(f"metadata schema {meta.schema!r}")
    if str(meta.stype_in) != PILOT_STYPE_IN:
        out.append(f"metadata stype_in {meta.stype_in!r}")
    if list(meta.symbols) != [symbol_for(root)]:
        out.append(f"metadata symbols {list(meta.symbols)}")
    end = getattr(meta, "end", None)
    if end is None or int(end) > ns_of(CUTOFF_UTC):
        out.append(f"metadata end {end!r} is missing or after {CUTOFF_BOUND}")
    return out


# ------------------------------------------------------------------ sessions ----
@dataclass(frozen=True)
class Piece:
    label: str
    lo: int
    hi: int


@dataclass(frozen=True)
class DayPlan:
    """Trade date ``day``: its session pieces, placement grid and static calendar flags."""

    day: date
    pieces: tuple[Piece, ...]
    grid_ns: np.ndarray  # sorted grid times g
    grid_piece: np.ndarray  # index into pieces for each g
    in_calendar: bool
    is_trade_date: bool
    holiday: str | None = None
    late_open: bool = False
    flags: dict[str, Any] = field(default_factory=dict)

    @property
    def open_lo(self) -> int | None:
        return min(p.lo for p in self.pieces) if self.pieces else None

    @property
    def open_hi(self) -> int | None:
        return max(p.hi for p in self.pieces) if self.pieces else None

    def main_pieces(self) -> list[Piece]:
        return [p for p in self.pieces if p.label == MAIN]


def split_pieces(day: date, opened: list[tuple[int, int]]) -> list[Piece]:
    """Cut the trade date's open intervals at MAIN's edges; merge touching same-label pieces."""
    m_lo, m_hi = pt_ns(day, MAIN_START_PT), pt_ns(day, MAIN_END_PT)
    raw: list[Piece] = []
    for lo, hi in sorted(opened):
        for label, a, b in ((OVERNIGHT, lo, min(hi, m_lo)), (MAIN, max(lo, m_lo), min(hi, m_hi)),
                            (OVERNIGHT, max(lo, m_hi), hi)):
            if a < b:
                raw.append(Piece(label, a, b))
    raw.sort(key=lambda p: p.lo)
    merged: list[Piece] = []
    for piece in raw:
        if merged and merged[-1].label == piece.label and merged[-1].hi == piece.lo:
            merged[-1] = Piece(piece.label, merged[-1].lo, piece.hi)
        else:
            merged.append(piece)
    return merged


def placement_grid(pieces: tuple[Piece, ...] | list[Piece]) -> tuple[np.ndarray, np.ndarray]:
    times, owner = [], []
    for k, piece in enumerate(pieces):
        first = -(-(piece.lo + EDGE_NS) // GRID_NS) * GRID_NS
        for g in range(first, piece.hi - EDGE_NS, GRID_NS):
            times.append(g)
            owner.append(k)
    return np.array(times, dtype=np.int64), np.array(owner, dtype=np.int64)


def build_day_plan(cal: GroupCalendar, day: date) -> DayPlan:
    empty = np.zeros(0, dtype=np.int64)
    if not cal.covers(day):
        return DayPlan(day, (), empty, empty, in_calendar=False, is_trade_date=False)
    if not cal.is_trade_date(day):
        return DayPlan(day, (), empty, empty, in_calendar=True, is_trade_date=False)
    hol = cal.holiday(day)
    late = day in cal.scheduled_late_opens or day in cal.late_opens
    pieces = tuple(split_pieces(day, session_intervals(cal, day)))
    grid, owner = placement_grid(pieces)
    return DayPlan(day, pieces, grid, owner, in_calendar=True, is_trade_date=True,
                   holiday=None if hol is None else f"{hol.name} ({hol.kind.value})",
                   late_open=late)


def make_test_plan(day: date, pieces: list[Piece], grid: list[int] | None = None) -> DayPlan:
    """A plan with explicit pieces (and optionally an explicit grid), for synthetic tests."""
    pieces_t = tuple(pieces)
    if grid is None:
        g, owner = placement_grid(pieces_t)
    else:
        g = np.array(sorted(grid), dtype=np.int64)
        owner = np.array([next(k for k, p in enumerate(pieces_t) if p.lo <= t < p.hi)
                          for t in g], dtype=np.int64)
    return DayPlan(day, pieces_t, g, owner, in_calendar=True, is_trade_date=True)


# ------------------------------------------------------------------ exclusions ----
EXCL_CUTOFF = "on_or_after_2024-03-01"
EXCL_CALENDAR = "outside_calendar_coverage"
EXCL_NOT_TRADE = "not_a_trade_date"
EXCL_HOLIDAY = "cme_holiday_or_early_close"
EXCL_LATE_OPEN = "scheduled_late_open"
EXCL_COVERAGE = "incomplete_file_coverage"
EXCL_NO_RECORDS = "no_records"
EXCL_GAP = "main_gap_gt_60s"
EXCL_ROLL = "roll_day"
EXCL_AFTER_ROLL = "after_roll_day"


def static_exclusions(plan: DayPlan, cover_lo: int, cover_hi: int) -> list[str]:
    """Reasons known before reading any record of the day."""
    out = []
    if plan.day >= CUTOFF_TRADE_DATE:
        out.append(EXCL_CUTOFF)
    if not plan.in_calendar:
        return [*out, EXCL_CALENDAR]
    if not plan.is_trade_date:
        return [*out, EXCL_NOT_TRADE]
    if plan.holiday is not None:
        out.append(EXCL_HOLIDAY)
    if plan.late_open:
        out.append(EXCL_LATE_OPEN)
    if plan.open_lo is None or cover_lo > plan.open_lo or cover_hi < plan.open_hi:
        out.append(EXCL_COVERAGE)
    return out


def candidate_days(cal: GroupCalendar, cover_lo: int, cover_hi: int) -> list[date]:
    """Calendar days whose trade-date window [D-1 17:00 CT, D 16:00 CT) overlaps the file."""
    first = datetime.fromtimestamp(cover_lo / NS, CT).date()
    last = datetime.fromtimestamp(cover_hi / NS, CT).date() + timedelta(days=1)
    out = []
    for n in range((last - first).days + 1):
        day = first + timedelta(days=n)
        lo = ct_ns(day - timedelta(days=1), time(17, 0))
        hi = ct_ns(day, DAY_BOUNDARY_CT)
        if lo < cover_hi and hi > cover_lo and day.weekday() < 5:
            out.append(day)
    return out


def mapped_ids(intervals: list[dict[str, Any]], lo_ns: int, hi_ns: int) -> list[str]:
    """Instrument ids of the symbology intervals (UTC dates, end exclusive) overlapping
    [lo_ns, hi_ns), in time order."""
    out: list[str] = []
    for entry in sorted(intervals, key=lambda e: str(e["start_date"])):
        sym = str(entry["symbol"]).strip()
        if not sym:
            continue
        a = ns_of(datetime.combine(_as_date(entry["start_date"]), time(0), tzinfo=UTC))
        b = ns_of(datetime.combine(_as_date(entry["end_date"]), time(0), tzinfo=UTC))
        if a < hi_ns and b > lo_ns and sym not in out:
            out.append(sym)
    return out


def _as_date(value: Any) -> date:
    return value if isinstance(value, date) else date.fromisoformat(str(value)[:10])


def ordered_union(first: list[str], second: list[str]) -> list[str]:
    return [*first, *[s for s in second if s not in first]]


def roll_exclusions(days: list[date], ids_by_day: dict[date, list[str]],
                    cal: GroupCalendar) -> dict[date, str]:
    """Spec section 2: trade dates on which the v.0 instrument changes (two instruments inside
    the day, or a first instrument other than the previous trade date's last) and the trade
    date after each are excluded. ``days``: the calendar trade dates considered, sorted."""
    out: dict[date, str] = {}
    trade_days = sorted(d for d in days if cal.covers(d) and cal.is_trade_date(d))
    for k, day in enumerate(trade_days):
        ids = ids_by_day.get(day) or []
        prev = ids_by_day.get(trade_days[k - 1]) if k > 0 else None
        changed = len(ids) > 1 or bool(prev and ids and prev[-1] != ids[0])
        if not changed:
            continue
        out[day] = EXCL_ROLL
        if k + 1 < len(trade_days):
            out.setdefault(trade_days[k + 1], EXCL_AFTER_ROLL)
    return out


def first_whole_trade_date(start: str, cal: GroupCalendar) -> date | None:
    """The first trade date whose whole open time lies at or after ``start``."""
    s = bound_ns(start)
    day = datetime.fromtimestamp(s / NS, CT).date()
    for n in range(0, 15):
        d = day + timedelta(days=n)
        if not (cal.covers(d) and cal.is_trade_date(d)):
            continue
        opened = session_intervals(cal, d)
        if opened and min(lo for lo, _ in opened) >= s:
            return d
    return None
