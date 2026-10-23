"""Stage E.31 Part 3: constants and request guards of the ZM order-book pilot purchase.

Used by pull31.py (span search, quote, buy), verify31.py (manifest) and tests/test_pull31.py.
Importing this module puts the repo root on sys.path, so the scripts run as
``uv run python reports/stage_e31_briefs/work/pilot/<script>.py`` from the repo root. The repo's
modules are imported read-only (nothing under data/ is edited); acct-3's pilot-only guard
(data.config.PILOT_ONLY_ACCOUNTS) stays: the scripts use data.spend_gate.SpendGate directly and
never data.pull_step2 or data.pull_hist.

Spec: reports/stage_e31_pilot_spec.md sections 0, 1 and 9.
- Four series, GLBX.MDP3, one request per series per month (4k requests for k months):
  Z1 mbo [ZM.v.0, ZM.v.1] continuous; Z2 mbp-1 [ZS.v.0] continuous; Z3 mbp-1 [ZL.v.0]
  continuous; Z4 definition [ZM.FUT, ZS.FUT, ZL.FUT] parent.
- Month m's request: 16:00 America/Chicago on the last calendar day of the month before m, to
  16:00 America/Chicago on m's last calendar day, in UTC (21:00Z under CDT, 22:00Z under CST).
  The last month is 2024-02, whose end is exactly 2024-02-29T22:00:00Z. The earliest month is
  2019-06 (the grains calendar covers trade dates from 2019-05-01).
- Every request is refused before any vendor call when it is not exactly one of these: another
  dataset, root, schema, symbol set or stype; a window other than the month rule's; a month
  after 2024-02 or before 2019-06; an overlap with the embargo and holdout 2, the research
  window, holdout 1 or a sealed range; a minute the grains calendar books to a holdout trade
  date (data.trade_date_guard). Any account but acct-3 is refused.
- TARGET = (125.00 - acct-3's committed USD outside this pilot's sessions) - 2.00, rounded
  down to the cent, and never above the spec's 122.27 (section 0). The pilot's sessions are the
  buy session, the span session and the retry session (spec v2 section 9, recovery): a retry is
  paid from the 2.00 margin, so it does not lower TARGET; acct-3's 125.00 cap bounds it.
- Retry (spec v2 section 9, SpecReviewer pass 1 item 4): a request whose download failed after
  its commit may be re-quoted and retried once, in session RETRY_SESSION, whose cap is
  125.00 - acct-3 committed so far (the failed commit counted as spent): retry_cap_usd.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dataclasses import dataclass  # noqa: E402
from datetime import UTC, date, datetime, time, timedelta  # noqa: E402
from decimal import ROUND_FLOOR, Decimal  # noqa: E402
from functools import lru_cache  # noqa: E402
from typing import Any  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

from data import holdout as ho  # noqa: E402
from data import trade_date_guard as tdg  # noqa: E402
from data.calendars import GROUP_OF_PRODUCT  # noqa: E402
from data.config import (  # noqa: E402
    ACCOUNT_3_CAP_USD,
    ACCOUNT_3_ID,
    DATASET,
    PILOT_ONLY_ACCOUNTS,
    VENDOR_ROOT,
)
from data.group_session import GroupCalendar, load_group_calendar  # noqa: E402
from data.pull_universe import (  # noqa: E402
    EMBARGO_END_UTC,
    EMBARGO_START_UTC,
    WINDOW_END_UTC,
    WINDOW_START_UTC,
    bound_token,
)
from data.quote_universe import iso_z, parse_utc, request_key  # noqa: E402
from data.spend_gate import RequestParams  # noqa: E402

# ------------------------------------------------------------------ constants ----
PILOT_ACCOUNT = ACCOUNT_3_ID
ACCOUNT_CAP_USD = ACCOUNT_3_CAP_USD  # 125.00
PILOT_DATASET = DATASET  # GLBX.MDP3
PILOT_VENDOR_ROOT = VENDOR_ROOT
PILOT_SESSION = "stage-E.31-2026-10-22-pilot"  # --quote and --buy
SPAN_SESSION = "stage-E.31-2026-10-22-pilot-span"  # --span-search (cap 0.00, quotes only)
RETRY_SESSION = "stage-E.31-2026-10-22-pilot-retry"  # --retry-download (spec v2 s9, recovery)
PILOT_SESSIONS = (PILOT_SESSION, SPAN_SESSION, RETRY_SESSION)
LOCK_FILE = ".buy31.lock"  # runs/.buy31.lock: one --buy or --retry-download at a time
VOLUME_SESSION = "stage-E.31-2026-10-22-volume"  # Part 1, the one other allowed acct-3 commit
VOLUME_REQUEST: dict[str, Any] = {
    "dataset": "GLBX.MDP3", "symbols": ["QM.FUT", "ZM.FUT"], "schema": "ohlcv-1d",
    "stype_in": "parent", "start": "2023-01-01", "end": "2026-10-22T00:00:00.000000000Z"}
SPEC_TARGET_USD = 122.27  # spec section 0: 125.00 - 0.72502180934 - 2.00, down to the cent
TARGET_MARGIN_USD = 2.00
LAST_MONTH = date(2024, 2, 1)
EARLIEST_MONTH = date(2019, 6, 1)  # grains calendar coverage starts 2019-05-01
CUTOFF_BOUND = "2024-02-29T22:00:00Z"  # the last month's exclusive end (16:00 CST)
CUTOFF_UTC = datetime(2024, 2, 29, 22, 0, tzinfo=UTC)
NO_RECORD_FROM_UTC = datetime(2024, 3, 1, 0, 0, tzinfo=UTC)  # spec 9: nothing on/after it
LAST_TRADE_DATE = date(2024, 2, 29)
MIN_MONTHS_TO_BUY = 2  # spec 1 and 9: k >= 2 or nothing is bought
QUOTE_MAX_AGE_H = 24.0
REQUOTE_TOLERANCE = 0.01  # a buy's fresh re-quote may exceed its quote31 value by 1% at most
BILLED_OVER_QUOTE_STOP = 0.03  # billing more than 3% above the quote stops the remaining buys
USD_DECIMALS = 9

CT = ZoneInfo("America/Chicago")
PT = ZoneInfo("America/Vancouver")
MONTH_BOUNDARY_CT = time(16, 0)
NS = 1_000_000_000

RC_OK, RC_STOPPED, RC_REFUSED, RC_QUALITY = 0, 1, 2, 3
DBN_SUFFIX = ".dbn.zst"


class PilotRefused(RuntimeError):
    """A request, argument, file or ledger state is outside what this pilot may touch."""


@dataclass(frozen=True, slots=True)
class Series:
    name: str
    schema: str
    symbols: tuple[str, ...]
    stype_in: str
    roots: tuple[str, ...]


SERIES: tuple[Series, ...] = (
    Series("Z1", "mbo", ("ZM.v.0", "ZM.v.1"), "continuous", ("ZM",)),
    Series("Z2", "mbp-1", ("ZS.v.0",), "continuous", ("ZS",)),
    Series("Z3", "mbp-1", ("ZL.v.0",), "continuous", ("ZL",)),
    Series("Z4", "definition", ("ZM.FUT", "ZS.FUT", "ZL.FUT"), "parent", ("ZM", "ZS", "ZL")),
)
SERIES_BY_NAME = {s.name: s for s in SERIES}
PILOT_ROOTS = frozenset({"ZM", "ZS", "ZL"})  # literal: the guard does not follow SERIES
if not {r for s in SERIES for r in s.roots} <= PILOT_ROOTS:
    raise RuntimeError("a pilot series names a root outside ZM, ZS, ZL")
EXPECTED_RTYPE = {"mbo": 0xA0, "mbp-1": 0x01, "definition": 0x13}


@dataclass(frozen=True, slots=True)
class Planned:
    """One request of the plan: a series, a month and the exact request sent."""

    series: Series
    month: date
    params: RequestParams

    @property
    def key(self) -> str:
        return request_key(self.params.as_kwargs())

    @property
    def month_label(self) -> str:
        return f"{self.month:%Y-%m}"

    @property
    def label(self) -> str:
        return f"{self.series.name} {self.month_label}"


# ------------------------------------------------------------------ months ----
def add_months(month: date, n: int) -> date:
    index = month.year * 12 + month.month - 1 + n
    return date(index // 12, index % 12 + 1, 1)


def last_day(month: date) -> date:
    return add_months(month, 1) - timedelta(days=1)


def _ct_bound(day: date) -> str:
    return iso_z(datetime.combine(day, MONTH_BOUNDARY_CT, tzinfo=CT))


def month_bounds(month: date) -> tuple[str, str]:
    """Month ``month``'s request: 16:00 CT on the previous month's last day to 16:00 CT on its
    own last day, both in UTC (zoneinfo handles CDT/CST)."""
    first = date(month.year, month.month, 1)
    return _ct_bound(first - timedelta(days=1)), _ct_bound(last_day(first))


def n_available_months() -> int:
    years = LAST_MONTH.year - EARLIEST_MONTH.year
    return years * 12 + LAST_MONTH.month - EARLIEST_MONTH.month + 1


def months_back(k: int) -> list[date]:
    """The k months ending with LAST_MONTH, latest first. Refuses k < 1 or before 2019-06."""
    if not isinstance(k, int) or k < 1:
        raise PilotRefused(f"--months {k!r} refused: k must be a whole number >= 1")
    if k > n_available_months():
        raise PilotRefused(f"--months {k} refused: the earliest month is {EARLIEST_MONTH:%Y-%m} "
                           f"(at most {n_available_months()} months end with {LAST_MONTH:%Y-%m})")
    return [add_months(LAST_MONTH, -i) for i in range(k)]


def span_months() -> list[date]:
    """Every month the span search may quote: 2024-02 back to 2019-06."""
    return months_back(n_available_months())


def parse_month(label: Any) -> date:
    """'YYYY-MM' -> the month's first day; anything else is refused."""
    text = str(label or "")
    if len(text) != 7 or text[4] != "-" or not (text[:4] + text[5:]).isdigit():
        raise PilotRefused(f"month {label!r} refused: give YYYY-MM")
    year, month = int(text[:4]), int(text[5:])
    if not 1 <= month <= 12:
        raise PilotRefused(f"month {label!r} refused: no month {month}")
    return date(year, month, 1)


def month_of_end(end: str) -> date:
    """The month whose month-rule end would be ``end`` (by its America/Chicago date)."""
    moment = parse_utc(end).astimezone(CT)
    return date(moment.year, moment.month, 1)


# ------------------------------------------------------------------ requests ----
def request_for(series: Series, month: date) -> RequestParams:
    start, end = month_bounds(month)
    return RequestParams(PILOT_DATASET, series.symbols, series.schema, series.stype_in, start, end)


def plan(k: int) -> list[Planned]:
    """The 4k requests in buy order (Z1 latest month first, then earlier Z1 months, then Z2, Z3,
    Z4 in the same month order). Every request is checked before it is returned."""
    months = months_back(k)
    return [Planned(s, m, check_request(request_for(s, m))) for s in SERIES for m in months]


def span_order(months: list[date]) -> list[Planned]:
    """Month by month (latest first), all four series of each month."""
    return [Planned(s, m, check_request(request_for(s, m))) for m in months for s in SERIES]


def series_of(params: RequestParams) -> Series | None:
    for s in SERIES:
        if (params.schema, tuple(params.symbols), params.stype_in) == (s.schema, s.symbols,
                                                                         s.stype_in):
            return s
    return None


def require_account(account: str) -> str:
    if account != PILOT_ACCOUNT or account not in PILOT_ONLY_ACCOUNTS:
        raise PilotRefused(f"account {account!r} refused: this pilot buys on {PILOT_ACCOUNT} "
                           "only (data.config.PILOT_ONLY_ACCOUNTS)")
    return account


def canonical_bound(stamp: str) -> datetime:
    try:
        moment = parse_utc(stamp)
    except (TypeError, ValueError) as exc:
        raise PilotRefused(f"unparseable request bound {stamp!r}") from exc
    canonical = moment.date().isoformat() if "T" not in stamp else iso_z(moment)
    if canonical != stamp:
        raise PilotRefused(f"request bound {stamp!r} is not canonical ({canonical!r})")
    return moment


def window_refusals(start: str, end: str) -> list[str]:
    """The embargo and holdout 2, the research window, holdout 1 (data.pull_universe's windows)
    and data.holdout's sealed-window check."""
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


@lru_cache(maxsize=8)
def calendar_for(root: str) -> GroupCalendar:
    return load_group_calendar(GROUP_OF_PRODUCT[root])


def booking_refusals(root: str, start: str, end: str) -> list[str]:
    """data.trade_date_guard's holdout-trade-date refusal on the covered part of [start, end)."""
    cal = calendar_for(root)
    cover_from = datetime.combine(cal.coverage[0] + timedelta(days=8), time(0), tzinfo=UTC)
    lo = max(parse_utc(start), cover_from)
    if lo >= parse_utc(end):
        return []
    try:
        tdg.refuse_holdout_bookings(root, iso_z(lo), end)
    except tdg.TradeDateRefused as exc:
        return [f"trade-date guard ({root}): {exc}"]
    return []


def _identity_refusals(params: RequestParams) -> tuple[list[str], Series | None]:
    out: list[str] = []
    if params.dataset != PILOT_DATASET:
        out.append(f"dataset {params.dataset!r} refused: {PILOT_DATASET} only")
    roots = sorted({str(sym).split(".")[0] for sym in params.symbols})
    if not roots or not set(roots) <= PILOT_ROOTS:
        out.append(f"root(s) {roots} refused: only {sorted(PILOT_ROOTS)}")
    series = series_of(params)
    if series is None:
        out.append(f"schema {params.schema!r}, symbols {list(params.symbols)}, stype_in "
                   f"{params.stype_in!r} refused: not one of the four pilot series ("
                   + "; ".join(f"{s.name} {s.schema} {list(s.symbols)} {s.stype_in}"
                               for s in SERIES) + ")")
    return out, series


def _month_refusals(params: RequestParams, s: datetime, e: datetime) -> list[str]:
    out: list[str] = []
    if not s < e:
        out.append(f"empty or inverted window {params.start}..{params.end}")
    if e > CUTOFF_UTC:
        out.append(f"end {params.end} is after {CUTOFF_BOUND}: no month after "
                   f"{LAST_MONTH:%Y-%m} is quoted or bought")
    month = month_of_end(params.end)
    expected = month_bounds(month)
    if (params.start, params.end) != expected:
        out.append(f"window {params.start}..{params.end} is not the month rule's window for "
                   f"{month:%Y-%m} ({expected[0]}..{expected[1]}: 16:00 CT on the previous "
                   "month's last day to 16:00 CT on the month's last day)")
    if month > LAST_MONTH:
        out.append(f"month {month:%Y-%m} is after {LAST_MONTH:%Y-%m}")
    if month < EARLIEST_MONTH:
        out.append(f"month {month:%Y-%m} is before {EARLIEST_MONTH:%Y-%m} (grains calendar)")
    return out


def request_refusals(params: RequestParams) -> list[str]:
    """Every reason ``params`` is not one of the pilot's requests; empty when admissible."""
    out, series = _identity_refusals(params)
    try:
        s, e = canonical_bound(params.start), canonical_bound(params.end)
    except PilotRefused as exc:
        return [*out, str(exc)]
    out.extend(_month_refusals(params, s, e))
    out.extend(window_refusals(params.start, params.end))
    if series is not None and s < e:
        for root in series.roots:
            out.extend(booking_refusals(root, params.start, params.end))
    return out


def check_request(params: RequestParams) -> RequestParams:
    reasons = request_refusals(params)
    if reasons:
        raise PilotRefused("; ".join(reasons))
    return params


# ------------------------------------------------------------------ paths ----
def series_dir_name(series: Series) -> str:
    return f"{series.name}_" + "-".join(sym.replace(".", "_") for sym in series.symbols)


def target_path(item: Planned, vendor_root: Path = PILOT_VENDOR_ROOT) -> Path:
    """VENDOR_ROOT/GLBX.MDP3/<schema>/<SERIES>_<SYMBOLS>/range=<start>_<end>.dbn.zst"""
    p = item.params
    name = f"range={bound_token(p.start)}_{bound_token(p.end)}{DBN_SUFFIX}"
    return Path(vendor_root) / p.dataset / p.schema / series_dir_name(item.series) / name


def record_name(item: Planned) -> str:
    return f"purchase31_{item.series.name}_{item.month_label}.json"


def bound_ns(stamp: str) -> int:
    moment = parse_utc(stamp)
    return int(moment.timestamp()) * NS + moment.microsecond * 1000


def iso_ns(ns: int) -> str:
    seconds, frac = divmod(int(ns), NS)
    return f"{datetime.fromtimestamp(seconds, UTC):%Y-%m-%dT%H:%M:%S}.{frac:09d}Z"


# ------------------------------------------------------------------ ledger ----
def floor_cent(usd: float) -> float:
    return float(Decimal(repr(usd)).quantize(Decimal("0.01"), rounding=ROUND_FLOOR))


def acct3_lines(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [e for e in entries if e.get("account") == PILOT_ACCOUNT]


def spend_target(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """TARGET from the ledger: (cap - acct-3 committed outside this pilot's sessions) - 2.00,
    rounded down to the cent; never above the spec's 122.27."""
    outside = sum(float(e.get("usd", 0.0)) for e in acct3_lines(entries)
                  if e.get("session_id") not in PILOT_SESSIONS)
    rule = floor_cent(ACCOUNT_CAP_USD - outside - TARGET_MARGIN_USD)
    target = min(rule, SPEC_TARGET_USD)
    return {"target_usd": target, "rule_target_usd": rule, "spec_target_usd": SPEC_TARGET_USD,
            "acct3_committed_before_pilot_usd": round(outside, 11),
            "rule": "floor_cent((125.00 - acct-3 committed outside the pilot sessions) - 2.00), "
                    "capped at the spec's 122.27"}


def retry_cap_usd(account_committed_usd: float) -> float:
    """The retry session's cap: 125.00 - acct-3 committed so far (every acct-3 line, the failed
    commit and any earlier retry included), to USD_DECIMALS. An earlier retry is therefore
    counted twice by the session check (its own lines plus this cap), which only tightens it."""
    return round(ACCOUNT_CAP_USD - float(account_committed_usd), USD_DECIMALS)


def other_commits(entries: list[dict[str, Any]], plan_keys: set[str]) -> list[str]:
    """acct-3 commit lines other than Part 1's volume request and this plan's requests (in the
    pilot session or its retry session), described briefly. A commit line without a request
    counts as another one."""
    volume_key = request_key(VOLUME_REQUEST)
    out = []
    for e in acct3_lines(entries):
        if e.get("event") != "commit":
            continue
        key = request_key(e["request"]) if isinstance(e.get("request"), dict) else None
        session = e.get("session_id")
        if session == VOLUME_SESSION and key == volume_key:
            continue
        if session in (PILOT_SESSION, RETRY_SESSION) and key in plan_keys:
            continue
        req = e.get("request") or {}
        out.append(f"{e.get('ts')} {session} {req.get('schema')} {req.get('symbols')} "
                   f"{req.get('start')}..{req.get('end')} usd={e.get('usd')}")
    return out
