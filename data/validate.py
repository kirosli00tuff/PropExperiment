"""Integrity checks for MES 1-minute bars and for tick-data ordering.

Ported discipline from MLCryptoEngine ``data/databento/validate.py``: a check
that never ran is reported as not run, never as a pass; coverage is measured
only against scheduled-open time; and absence is FLAGGED, never filled.

Bar schema note: ohlcv-1m carries ``ts_event`` (bar open) only — there is no
``ts_recv`` on a bar — so bars are ordered on ``ts_event``. The ported
``ts_recv`` ordering check applies to the tick data (trades / mbp-10) used in
the cross-check and cost model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

import numpy as np
import pandas as pd

from data.cme_calendar import HOLIDAYS, Holiday, HolidayKind
from data.session import CME_TZ, HALT_END, HALT_START, closed_windows_range_ns, ct_ns

NS_PER_MIN = 60 * 1_000_000_000
MES_TICK_FIXED = 250_000_000
RTH_START_MIN, RTH_END_MIN = 8 * 60 + 30, 15 * 60  # 08:30-15:00 CT


@dataclass(frozen=True)
class GapRun:
    start_ns: int  # first missing minute
    minutes: int
    segment: str  # "RTH" (08:30-15:00 CT) or "ETH"

    @property
    def start_ct(self) -> str:
        return pd.Timestamp(self.start_ns, tz="UTC").tz_convert(CME_TZ).strftime(
            "%Y-%m-%d %a %H:%M"
        )


@dataclass
class BarValidation:
    rows: int = 0
    first_ns: int | None = None
    last_ns: int | None = None
    non_increasing_steps: int = 0
    duplicate_timestamps: int = 0
    negative_volume: int = 0
    zero_volume: int = 0
    off_tick_prices: int = 0
    ohlc_inconsistent: int = 0
    bars_in_scheduled_closure: list[int] = field(default_factory=list)
    expected_minutes: int = 0
    present_expected_minutes: int = 0
    gap_runs: list[GapRun] = field(default_factory=list)

    @property
    def hard_failures(self) -> list[str]:
        out = []
        if self.non_increasing_steps:
            out.append(f"{self.non_increasing_steps} non-increasing timestamp steps")
        if self.duplicate_timestamps:
            out.append(f"{self.duplicate_timestamps} duplicate timestamps")
        if self.negative_volume:
            out.append(f"{self.negative_volume} negative volumes")
        if self.off_tick_prices:
            out.append(f"{self.off_tick_prices} prices off the 0.25 tick grid")
        if self.ohlc_inconsistent:
            out.append(f"{self.ohlc_inconsistent} bars with high/low inconsistent with open/close")
        return out


def ordering_counts(ts: np.ndarray) -> tuple[int, int]:
    """(non-increasing steps, duplicate values) — strict monotonicity check."""
    steps = np.diff(ts)
    return int((steps <= 0).sum()), int(len(ts) - len(np.unique(ts)))


def in_windows(ts: np.ndarray, starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    if starts.size == 0:
        return np.zeros(ts.shape, dtype=bool)
    idx = np.searchsorted(starts, ts, side="right") - 1
    return (idx >= 0) & (ts < ends[np.clip(idx, 0, None)])


def expected_minutes(
    start_ns: int, end_ns: int, starts: np.ndarray, ends: np.ndarray
) -> np.ndarray:
    """Minute starts in [start, end) that fall in scheduled-open time."""
    grid = np.arange(start_ns, end_ns, NS_PER_MIN, dtype=np.int64)
    return grid[~in_windows(grid, starts, ends)]


def gap_runs(expected: np.ndarray, present: np.ndarray) -> tuple[list[GapRun], np.ndarray]:
    """Consecutive runs of expected minutes with no bar, plus per-present-bar
    ``gap_before_minutes`` (aligned to ``present`` order)."""
    have = np.isin(expected, present)
    missing_idx = np.flatnonzero(~have)
    runs: list[GapRun] = []
    if missing_idx.size:
        breaks = np.flatnonzero(np.diff(missing_idx) != 1) + 1
        for group in np.split(missing_idx, breaks):
            start = int(expected[group[0]])
            local = pd.Timestamp(start, tz="UTC").tz_convert(CME_TZ)
            minute = local.hour * 60 + local.minute
            seg = "RTH" if RTH_START_MIN <= minute < RTH_END_MIN else "ETH"
            runs.append(GapRun(start, int(group.size), seg))
    # gap_before: for each expected minute that is present, count missing expected
    # minutes since the previous present expected minute.
    cum_missing = np.cumsum(~have)
    present_pos = np.flatnonzero(have)
    before = np.diff(np.concatenate([[0], cum_missing[present_pos]]))
    before_by_ts = dict(zip(expected[present_pos].tolist(), before.tolist(), strict=True))
    aligned = np.array([before_by_ts.get(int(t), 0) for t in present], dtype=np.int64)
    return runs, aligned


def validate_bars(
    raw: pd.DataFrame, start_ns: int, end_ns: int, starts: np.ndarray, ends: np.ndarray
) -> tuple[BarValidation, np.ndarray]:
    ts = raw["ts_event"].to_numpy()
    report = BarValidation(rows=len(raw))
    if len(raw) == 0:
        return report, np.array([], dtype=np.int64)
    report.first_ns, report.last_ns = int(ts.min()), int(ts.max())
    report.non_increasing_steps, report.duplicate_timestamps = ordering_counts(ts)
    report.negative_volume = int((raw["volume"] < 0).sum())
    report.zero_volume = int((raw["volume"] == 0).sum())
    prices = raw[["open_fixed", "high_fixed", "low_fixed", "close_fixed"]].to_numpy()
    report.off_tick_prices = int((prices % MES_TICK_FIXED != 0).sum())
    o, h, lo, c = prices.T
    report.ohlc_inconsistent = int(
        ((h < np.maximum(o, c)) | (lo > np.minimum(o, c)) | (lo > h)).sum()
    )
    closure = in_windows(ts, starts, ends)
    report.bars_in_scheduled_closure = ts[closure].tolist()
    expected = expected_minutes(start_ns, end_ns, starts, ends)
    report.expected_minutes = int(expected.size)
    report.present_expected_minutes = int(np.isin(expected, ts).sum())
    report.gap_runs, gap_before = gap_runs(expected, ts)
    return report, gap_before


# ------------------------------------------------ empirical calendar checks ----
@dataclass(frozen=True)
class HolidayObservation:
    day: date
    name: str
    kind: str
    calendar_halt_ct: str
    last_bar_before_ct: str
    first_bar_after_ct: str
    bars_inside_closure: int
    consistent: bool
    note: str


def _fmt(ns: int | None) -> str:
    if ns is None:
        return "—"
    return pd.Timestamp(ns, tz="UTC").tz_convert(CME_TZ).strftime("%a %m-%d %H:%M")


def observe_holidays(
    ts: np.ndarray, starts: np.ndarray, ends: np.ndarray, first: date, last: date
) -> list[HolidayObservation]:
    """For each calendar holiday inside the data window, where did trading stop/resume?"""
    ts_sorted = np.sort(ts)
    out: list[HolidayObservation] = []
    for day, hol in sorted(HOLIDAYS.items()):
        if not first <= day <= last:
            continue
        if hol.kind is HolidayKind.EARLY_HALT:
            assert hol.halt_ct is not None
            boundary = ct_ns(day, hol.halt_ct)
            label = hol.halt_ct.strftime("%H:%M")
        else:
            boundary = ct_ns(day - timedelta(days=1), HALT_START)
            label = "closed"
        win_idx = np.searchsorted(starts, boundary, side="right") - 1
        w_start, w_end = int(starts[win_idx]), int(ends[win_idx])
        i = np.searchsorted(ts_sorted, w_start, side="left")
        last_before = int(ts_sorted[i - 1]) if i > 0 else None
        j = np.searchsorted(ts_sorted, w_end, side="left")
        first_after = int(ts_sorted[j]) if j < ts_sorted.size else None
        inside = int(j - i)
        expected_last = w_start - NS_PER_MIN
        consistent = inside == 0 and last_before == expected_last and first_after == w_end
        note = []
        if inside:
            note.append(f"{inside} bars inside the calendar closure")
        if last_before != expected_last:
            note.append(f"last bar {_fmt(last_before)} != expected {_fmt(expected_last)}")
        if first_after != w_end:
            note.append(f"first bar after {_fmt(first_after)} != reopen {_fmt(w_end)}")
        out.append(
            HolidayObservation(
                day, hol.name, hol.kind.value, label, _fmt(last_before), _fmt(first_after),
                inside, consistent, "; ".join(note) or "matches calendar",
            )
        )
    return out


def daily_halt_observation(ts: np.ndarray) -> dict[str, int]:
    """How often trading prints in/around the 16:00-17:00 CT halt."""
    local = pd.to_datetime(ts, utc=True).tz_convert(CME_TZ)
    minutes = local.hour * 60 + local.minute
    halt_lo, halt_hi = HALT_START.hour * 60, HALT_END.hour * 60
    return {
        "bars_starting_16:00-16:59_CT": int(((minutes >= halt_lo) & (minutes < halt_hi)).sum()),
        "bars_at_15:59_CT": int((minutes == halt_lo - 1).sum()),
        "bars_at_17:00_CT": int((minutes == halt_hi).sum()),
    }


def ts_recv_ordering(ts_recv: np.ndarray) -> dict[str, int]:
    """Ported MLCryptoEngine ordering check for tick data: ts_recv must be monotone."""
    steps = np.diff(ts_recv)
    return {"records": int(ts_recv.size), "ts_recv_regressions": int((steps < 0).sum())}


def ct_time(ns: int) -> time:
    return datetime.fromtimestamp(ns / 1e9, tz=CME_TZ).time()


# ------------------------------- Stage D.1f step 4b: calendar validation (D-2) ----
# reports/stage_d1f_confirmation_list.md 1.5 step 4b, run on the confirmation bars before step
# 5: (1) every weekday with no bars is a listed full closure; (2) every day whose last RTH bar
# opens before 14:59 CT is a listed early halt whose halt time equals the observed last minute
# plus one; (3) every listed 2019-2024 entry inside the bars' date span is observed. Any
# discrepancy fails the step; the lead decides before step 5.
UNLISTED_CLOSURE = "weekday_without_bars_not_a_listed_full_closure"
EARLY_STOP_NOT_LISTED = "early_stop_not_a_listed_early_halt_at_that_time"
ENTRY_NOT_OBSERVED = "listed_entry_not_observed"
STEP4B_ENTRY_YEARS = (2019, 2024)
RTH_CLOSE_CT = time(15, 0)
RTH_LAST_MINUTE_CT = time(14, 59)
_MIDDAY_CT = time(12, 0)


@dataclass(frozen=True)
class CalendarDiscrepancy:
    kind: str  # one of the three constants above
    day: date
    detail: str


@dataclass(frozen=True)
class CalendarValidation:
    first_day: date
    last_day: date
    weekdays_checked: int
    entries_checked: tuple[date, ...]
    discrepancies: tuple[CalendarDiscrepancy, ...]

    @property
    def passed(self) -> bool:
        return self.weekdays_checked > 0 and not self.discrepancies

    def as_dict(self) -> dict:
        return {
            "passed": self.passed, "first_day": str(self.first_day),
            "last_day": str(self.last_day), "weekdays_checked": self.weekdays_checked,
            "entries_checked": [str(d) for d in self.entries_checked],
            "discrepancies": [{"kind": d.kind, "day": str(d.day), "detail": d.detail}
                              for d in self.discrepancies],
        }


def session_day(ns: int) -> date:
    """Calendar-free trade date: the CT date, one day later from the 17:00 CT reopen, weekends
    skipped. Holidays are deliberately NOT consulted: the calendar is what is under test."""
    local = pd.Timestamp(ns, tz="UTC").tz_convert(CME_TZ)
    day = local.date() + timedelta(days=int(local.time() >= HALT_END))
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day


def _listed(day: date) -> str:
    hol = HOLIDAYS.get(day)
    if hol is None:
        return "no calendar entry"
    halt = f" {hol.halt_ct:%H:%M}" if hol.halt_ct else ""
    return f"listed {hol.kind.value}{halt} ({hol.name})"


def _check_weekday(ts: np.ndarray, day: date) -> list[CalendarDiscrepancy]:
    """Rules (1) and (2) for one weekday. Its session is [day-1 17:00, day 17:00) CT (Sunday
    17:00 for a Monday), fixed by the weekly schedule alone."""
    lo, hi = ct_ns(day - timedelta(days=1), HALT_END), ct_ns(day, HALT_END)
    i, j = np.searchsorted(ts, [lo, hi], side="left")
    hol: Holiday | None = HOLIDAYS.get(day)
    if i == j:
        if hol is not None and hol.kind is HolidayKind.FULL_CLOSURE:
            return []
        return [CalendarDiscrepancy(UNLISTED_CLOSURE, day,
                                    f"no bar in the session {_fmt(lo)} .. {_fmt(hi)} CT; "
                                    f"{_listed(day)}")]
    k = int(np.searchsorted(ts, ct_ns(day, RTH_CLOSE_CT), side="left"))
    last = int(ts[k - 1]) if k > i else None  # the day's last bar opening before 15:00 CT
    if last is not None and last >= ct_ns(day, RTH_LAST_MINUTE_CT):
        return []  # the 14:59 CT bar exists: a full RTH session
    if (last is not None and hol is not None and hol.kind is HolidayKind.EARLY_HALT
            and hol.halt_ct is not None and last + NS_PER_MIN == ct_ns(day, hol.halt_ct)):
        return []
    # A session with no bar before 15:00 CT at all (e.g. an 08:15 halt misread) is treated as
    # a day whose last RTH bar opens before 14:59: stricter than skipping it.
    implied = "none (no bar before 15:00 CT)" if last is None else _fmt(last + NS_PER_MIN)
    after = int(ts[k]) if k < ts.size else None
    return [CalendarDiscrepancy(
        EARLY_STOP_NOT_LISTED, day,
        f"last bar before 15:00 CT {_fmt(last)} (implied halt {implied}); {_listed(day)}; "
        f"next bar {_fmt(after)}; {j - i} bars in the session")]


def _observe_closure(ts: np.ndarray, day: date, starts: np.ndarray,
                     ends: np.ndarray) -> str | None:
    """Rule (3) for a FULL_CLOSURE: no bar from the day-1 17:00 CT reopen to the calendar's
    reopen, and the first bar after it at exactly the reopen. The previous session's last bar
    is NOT required to be 15:59 CT (as observe_holidays requires): before 2021-06-28 CME equity
    futures traded to 16:15 CT, which data/session.py's fixed 16:00 halt does not model, and
    that close belongs to the previous day, not to this entry."""
    lo, probe = ct_ns(day - timedelta(days=1), HALT_END), ct_ns(day, _MIDDAY_CT)
    w = int(np.searchsorted(starts, probe, side="right")) - 1
    if w < 0 or probe >= ends[w]:
        return "the session calendar has no closed window on this day"
    reopen = int(ends[w])
    i, j = np.searchsorted(ts, [lo, reopen], side="left")
    first_after = int(ts[j]) if j < ts.size else None
    notes = []
    if j > i:
        notes.append(f"{j - i} bars inside the closure {_fmt(lo)} .. {_fmt(reopen)} "
                     f"(first {_fmt(int(ts[i]))})")
    if first_after != reopen:
        notes.append(f"first bar after {_fmt(first_after)} != reopen {_fmt(reopen)}")
    return "; ".join(notes) or None


def validate_calendar_step4b(
    ts: np.ndarray, first: date | None = None, last: date | None = None,
    entry_years: tuple[int, int] = STEP4B_ENTRY_YEARS,
) -> CalendarValidation:
    """Step 4b over bar open times ``ts`` (UTC ns). The span defaults to the calendar-free
    session days of the first and last bar. Returns every discrepancy; ``passed`` only if
    there is none. Rule (3) uses ``observe_holidays`` for early halts (its last-bar, no-bar and
    reopen tests all belong to the entry) and ``_observe_closure`` for full closures."""
    ts_sorted = np.sort(np.asarray(ts, dtype=np.int64))
    if ts_sorted.size == 0:
        raise ValueError("no bars: the step-4b calendar validation cannot run")
    first = first or session_day(int(ts_sorted[0]))
    last = last or session_day(int(ts_sorted[-1]))
    days = [first + timedelta(days=n) for n in range((last - first).days + 1)]
    weekdays = [d for d in days if d.weekday() < 5]
    found = [x for d in weekdays for x in _check_weekday(ts_sorted, d)]

    closed = closed_windows_range_ns(first, last)
    starts = np.array([w[0] for w in closed], dtype=np.int64)
    ends = np.array([w[1] for w in closed], dtype=np.int64)
    listed = [h for d, h in sorted(HOLIDAYS.items())
              if first <= d <= last and entry_years[0] <= d.year <= entry_years[1]]
    halts = {o.day: o for o in observe_holidays(ts_sorted, starts, ends, first, last)}
    for hol in listed:
        if hol.kind is HolidayKind.EARLY_HALT:
            obs = halts[hol.day]
            note = None if obs.consistent else obs.note
            label = f"early halt {obs.calendar_halt_ct}"
        else:
            note = _observe_closure(ts_sorted, hol.day, starts, ends)
            label = "full closure"
        if note:
            found.append(CalendarDiscrepancy(ENTRY_NOT_OBSERVED, hol.day,
                                             f"{hol.name}, {label}: {note}"))
    return CalendarValidation(first, last, len(weekdays), tuple(h.day for h in listed),
                              tuple(sorted(found, key=lambda x: (x.day, x.kind))))
