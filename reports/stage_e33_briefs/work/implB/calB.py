"""Implementation B (E.33 B2, FeatureCoder2): calendar helpers written from the protocol text.

Protocol: reports/stage_e32_discovery_protocol.md (cited P<n>). Nothing here imports cal33.

- Trade dates (P1.4): the 816 regular grains trade dates 2020-12-01..2024-02-29 from the program
  calendar (measure31.grains / month_trade_dates); the first 20 are burn-in, 796 OOF.
- Fronts (P0.3): measure31.instrument_on over the discovery manifest's symbology (file headers'
  "mappings"), ZM.v.0, ZS.v.0, ZL.v.0.
- Segments (P4 G2): maximal runs of universe trade dates with unchanged (ZM, ZS, ZL) fronts.
- Releases (P3.6 rule 3): the parse rule, the count assertion and the NOPA rule dates.
- Open-time axis (P0.3 "Window of k minutes ending at t"): grains open intervals
  (data.group_session.session_intervals), the 07:45-08:30 pause and 13:20-19:00 close skipped.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent / "pipeline"
if str(PIPELINE) not in sys.path:
    sys.path.insert(0, str(PIPELINE))

import guard33 as g  # noqa: E402  (adds REPO and the E.31 pilot folder to sys.path)
import measure31 as m31  # noqa: E402
from data.group_session import session_intervals  # noqa: E402
from data.session import ct_ns  # noqa: E402

NS = 1_000_000_000
MIN_NS = 60 * NS
CT = ZoneInfo("America/Chicago")
FIRST, LAST = date(2020, 12, 1), date(2024, 2, 29)  # P1.4
N_DATES, N_BURN = 816, 20  # P1.4
SERIES_OF = {"ZM": ("Z1", "ZM.v.0"), "ZS": ("Z2", "ZS.v.0"), "ZL": ("Z3", "ZL.v.0")}

# P3.6 rule 3: the reports kept, and the counts E.33 asserts before any label.
RELEASE_REPORTS = ("USDA WASDE", "NASS Crop Production", "NASS Crop Production Annual",
                   "NASS Grain Stocks", "NASS Prospective Plantings", "NASS Acreage",
                   "NOPA Monthly Crush (not USDA)")
RELEASE_COUNTS = {"USDA WASDE": 39, "NASS Crop Production": 39,
                  "NASS Crop Production Annual": 4, "NASS Grain Stocks": 13,
                  "NASS Prospective Plantings": 3, "NASS Acreage": 3,
                  "NOPA Monthly Crush (not USDA)": 37}
NOPA = "NOPA Monthly Crush (not USDA)"
N_NOPA_RULE_DATES = 2
RELEASE_FILES = (g.RESEARCH31 / "usda_releases_ext.csv", g.RESEARCH31 / "usda_releases.csv")


# ------------------------------------------------------------------ trade dates (P1.4) ----
@lru_cache(maxsize=1)
def grains():  # noqa: ANN201 - data.group_session.GroupCalendar
    return m31.grains()


@lru_cache(maxsize=1)
def trade_dates() -> tuple[date, ...]:
    """P1.4: the 816 regular grains trade dates 2020-12-01..2024-02-29."""
    months, d = [], FIRST.replace(day=1)
    while d <= LAST:
        months.append(f"{d:%Y-%m}")
        d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    days = tuple(x for x in m31.month_trade_dates(grains(), months) if FIRST <= x <= LAST)
    if len(days) != N_DATES:
        raise RuntimeError(f"P1.4 expects {N_DATES} trade dates, found {len(days)}")
    return days


def oof_dates() -> tuple[date, ...]:
    return trade_dates()[N_BURN:]


@lru_cache(maxsize=1)
def date_index() -> dict[date, int]:
    return {d: k for k, d in enumerate(trade_dates())}


def previous_dates(d: date, n: int) -> list[date]:
    """The n universe trade dates before d (fewer near the start; oldest first)."""
    k = date_index()[d]
    return list(trade_dates()[max(0, k - n):k])


def prev_trade_date(d: date) -> date | None:
    """The previous grains trade date (calendar), None if none within 10 days."""
    cal = grains()
    for n in range(1, 11):
        x = d - timedelta(days=n)
        if cal.covers(x) and cal.is_trade_date(x):
            return x
    return None


# ------------------------------------------------------------------ fronts (P0.3) ----
@lru_cache(maxsize=1)
def _mappings() -> dict[str, m31.Mappings]:
    man = g.discovery_manifest()
    out = {}
    for root, (series, symbol) in SERIES_OF.items():
        heads = [f["header"] for f in man["files"] if f["series"] == series]
        maps = m31.merge_mappings(heads)
        if symbol not in maps:
            raise RuntimeError(f"no {symbol} mapping in the {series} headers")
        out[root] = maps
    return out


def front(root: str, d: date) -> int | None:
    """P0.3: the instrument_id mapped to <root>.v.0 for UTC date d (measure31.instrument_on)."""
    return m31.instrument_on(_mappings()[root], SERIES_OF[root][1], d)


def fronts(d: date) -> tuple[int | None, int | None, int | None]:
    return front("ZM", d), front("ZS", d), front("ZL", d)


@lru_cache(maxsize=1)
def segment_ids() -> dict[date, int]:
    """P4 G2: a segment is a maximal run of trade dates on which the three fronts are unchanged;
    a date with an unknown front starts its own segment (READING B-SEG-1)."""
    out, seg, last = {}, -1, None
    for d in trade_dates():
        fr = fronts(d)
        if fr != last or None in fr:
            seg += 1
        out[d], last = seg, fr
    return out


# ------------------------------------------------------------------ calendar flags ----
def is_monday_or_after_closure(d: date) -> bool:
    """C.10: D is a Monday, or a calendar day strictly between the previous trade date and D is a
    full closure (READING B-C10)."""
    if d.weekday() == 0:
        return True
    prev = prev_trade_date(d)
    if prev is None:
        return False
    cal = grains()
    x = prev + timedelta(days=1)
    while x < d:
        if cal.is_full_closure(x):
            return True
        x += timedelta(days=1)
    return False


def trade_date_of_ns(ns: int) -> date:
    """The trade date whose window [D-1 16:00 CT, D 16:00 CT) holds the instant."""
    local = datetime.fromtimestamp(ns / NS, CT)
    return local.date() + timedelta(days=1) if local.time() >= time(16, 0) else local.date()


def trade_dates_to(d: date, end: date) -> int:
    """C.7: the number of grains trade dates x with d < x <= end (0 if end <= d;
    READING B-C7)."""
    cal, n, x = grains(), 0, d + timedelta(days=1)
    while x <= end:
        if cal.covers(x) and cal.is_trade_date(x):
            n += 1
        x += timedelta(days=1)
    return n


# ------------------------------------------------------------------ releases (P3.6 rule 3) ----
def _valid_day(text: str) -> date | None:
    try:
        if len(text) != 10:
            return None
        return date.fromisoformat(text)
    except ValueError:
        return None


@lru_cache(maxsize=1)
def releases() -> dict[date, tuple[int, ...]]:
    """P3.6 rule 3: release instants R (UTC ns, 11:00:00 CT) by calendar date, with the asserted
    counts and the NOPA rule dates for months without a valid NOPA row."""
    counts = dict.fromkeys(RELEASE_REPORTS, 0)
    out: dict[date, set[int]] = {}
    nopa_months: set[tuple[int, int]] = set()
    for path in RELEASE_FILES:
        g.check_reference(path)
        with Path(path).open(encoding="utf-8") as fh:
            lines = [ln for ln in fh if not ln.startswith("#")]
        for row in csv.DictReader(lines):
            day = _valid_day((row.get("date") or "").strip())
            if day is None:
                continue
            report = (row.get("report") or "").strip()
            if (row.get("time_et") or "").strip() != "12:00" or report not in RELEASE_REPORTS:
                continue
            counts[report] += 1
            if report == NOPA:
                nopa_months.add((day.year, day.month))
            out.setdefault(day, set()).add(ct_ns(day, time(11, 0)))
    if counts != RELEASE_COUNTS:
        raise RuntimeError(f"P3.6 rule 3 counts differ: {counts}")
    rule_dates = []
    d = FIRST.replace(day=1)
    while d <= LAST:
        if (d.year, d.month) not in nopa_months:
            x = d.replace(day=15)
            while not (grains().covers(x) and grains().is_trade_date(x)):
                x += timedelta(days=1)
            rule_dates.append(x)
            out.setdefault(x, set()).add(ct_ns(x, time(11, 0)))
        d = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
    if len(rule_dates) != N_NOPA_RULE_DATES:
        raise RuntimeError(f"P3.6 rule 3: {len(rule_dates)} NOPA rule dates, expected 2")
    return {k: tuple(sorted(v)) for k, v in out.items()}


def release_count_table() -> dict[str, int]:
    """Printed by the builder (P3.6 rule 3 asks E.33 to print them)."""
    releases()
    return {**RELEASE_COUNTS, "NOPA rule dates": N_NOPA_RULE_DATES}


def has_release(d: date) -> bool:
    """C.8: D carries an 11:00 release of P3.6 rule 3."""
    return d in releases()


def release_clear_mask(d: date, marks_ns: np.ndarray) -> np.ndarray:
    """F1.3: True where a minute mark is clear of every [R - 2 min, R + 30 min] of D (closed
    interval; READING B-F13-REL)."""
    clear = np.ones(len(marks_ns), dtype=bool)
    for r in releases().get(d, ()):
        clear &= ~((marks_ns >= r - 2 * MIN_NS) & (marks_ns <= r + 30 * MIN_NS))
    return clear


# ------------------------------------------------------------------ clock helpers ----
def ct(d: date, hh: int, mm: int) -> int:
    return ct_ns(d, time(hh, mm))


def grid_ns(d: date, n: int = 279) -> np.ndarray:
    """Wall-clock minute marks 08:35, 08:36, ... (n of them) on D in UTC ns."""
    return ct(d, 8, 35) + MIN_NS * np.arange(n, dtype=np.int64)


# ------------------------------------------------------------------ open-time axis (P0.3) ----
@dataclass(frozen=True)
class OpenAxis:
    """Open intervals [lo, hi) of some trade dates; pos(u) = open nanoseconds before u."""

    lo: np.ndarray
    hi: np.ndarray
    day: tuple[date, ...]
    cum: np.ndarray  # open ns before each interval

    @classmethod
    def of(cls, days: list[date]) -> OpenAxis:
        rows = []
        for d in days:
            rows.extend((lo, hi, d) for lo, hi in session_intervals(grains(), d))
        rows.sort()
        lo = np.array([r[0] for r in rows], dtype=np.int64)
        hi = np.array([r[1] for r in rows], dtype=np.int64)
        if np.any(lo[1:] < hi[:-1]):
            raise RuntimeError("open intervals overlap")
        cum = np.concatenate([[0], np.cumsum(hi - lo)[:-1]]).astype(np.int64)
        return cls(lo, hi, tuple(r[2] for r in rows), cum)

    def pos(self, u: np.ndarray) -> np.ndarray:
        """Open nanoseconds in [lo_0, u): a closed instant gets the position of the next open
        instant (the end of the previous open interval)."""
        u = np.asarray(u, dtype=np.int64)
        k = np.searchsorted(self.lo, u, side="right") - 1
        kk = np.clip(k, 0, None)
        inside = np.minimum(u - self.lo[kk], self.hi[kk] - self.lo[kk])
        return np.where(k >= 0, self.cum[kk] + inside, 0).astype(np.int64)

    def is_open(self, u: np.ndarray) -> np.ndarray:
        u = np.asarray(u, dtype=np.int64)
        k = np.searchsorted(self.lo, u, side="right") - 1
        kk = np.clip(k, 0, None)
        return (k >= 0) & (u < self.hi[kk])

    def marks(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """The whole-minute points of the open-time axis (wall ns), their positions and their
        interval index into ``day``; consecutive marks are one open minute apart. READING
        B-OPEN-1: the point shared by the end of one open interval and the start of the next
        (07:45 / 08:30, 13:20 / 19:00, an early halt / the next open) is the end of the earlier
        interval (07:45:00): the skipped pause, and every record in it, never enters a sample.
        Marks of interval k: lo_k (first interval only), lo_k + 1 min, ..., hi_k."""
        walls, days = [], []
        for k in range(len(self.lo)):
            first = self.lo[k] if k == 0 else self.lo[k] + MIN_NS
            w = np.arange(first, self.hi[k] + 1, MIN_NS, dtype=np.int64)
            walls.append(w)
            days.append(np.full(len(w), k, dtype=np.int32))
        wall = np.concatenate(walls) if walls else np.zeros(0, np.int64)
        kday = np.concatenate(days) if days else np.zeros(0, np.int32)
        return wall, self.pos(wall), kday
