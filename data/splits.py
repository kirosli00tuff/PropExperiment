"""Research / embargo / sealed-holdout boundaries for the MES series (Stage C, Task 5).

Boundaries are CME trade dates (``data.session.trade_date``), never calendar or
UTC dates: a trade date's session opens at 17:00 CT the previous evening, so a
UTC-date split would cut a session in half.

Data on disk: 379 trade dates, 2025-04-01 .. 2026-09-16. The first
(2025-04-01) is missing its 17:00-19:00 CT open because the pull starts at
00:00 UTC; the last (2026-09-16) is a 118-bar overnight stub.

- RESEARCH  2025-04-01 .. 2026-06-12  (311 trade dates) — walk-forward folds live here.
- EMBARGO   2026-06-15 .. 2026-06-19  (5)  — the June 2026 roll week. The splice is
  06-17; 06-15/06-16 trade the thinning MESM6 at ~20% of normal volume
  (reports/bar_validation_summary.json ``roll_volume_context``). Roll-blackout days
  are untradeable in the engine anyway, so the embargo costs almost nothing and
  keeps the last research session a full week away from the first holdout session.
- HOLDOUT   2026-06-22 .. 2026-09-16  (62 complete + 1 partial) — sealed; Stage D.2 only.

Why ~3 months of holdout (16.6%): it must be the most recent slice, and it must
leave the walk-forward enough folds. With 62 complete days, a one-sided test at
80% confidence with 80% power detects a mean daily P&L of about 0.21 daily
standard deviations ((0.8416 + 0.8416) / sqrt(62)). Stage D.2's pre-registered
bar has to be set with that resolution in mind, and Stage E's forward test adds
out-of-sample evidence that the holdout alone cannot.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from data.cme_calendar import HOLIDAYS, HolidayKind
from data.config import REPO_ROOT

RESEARCH_START = date(2025, 4, 1)
RESEARCH_END = date(2026, 6, 12)  # inclusive
EMBARGO_START = date(2026, 6, 15)
EMBARGO_END = date(2026, 6, 19)  # inclusive
HOLDOUT_START = date(2026, 6, 22)  # inclusive; everything from here on is sealed
DATA_LAST_TRADE_DATE = date(2026, 9, 16)  # partial overnight stub


def is_research_trade_date(trade_date: date) -> bool:
    return RESEARCH_START <= trade_date <= RESEARCH_END


def is_holdout_trade_date(trade_date: date) -> bool:
    return trade_date >= HOLDOUT_START


# ==================================================== Walk-forward folds (Stage C, Task 5)
#
# Unit: CME trade dates (``datetime.date``), research slice only. 311 research
# trade dates on disk (RESEARCH_START..RESEARCH_END inclusive).
#
# WF_TEST_DAYS = 21 -- one month of trading sessions: the Combine bills
# monthly and a calendar month holds several XFA payout windows (see
# rules/xfa_rules.py), so a fold's test slice is long enough to see a
# handful of payout-eligible weeks. ~21 daily P&L points per fold.
#
# WF_STEP_DAYS = WF_TEST_DAYS -- folds are non-overlapping in the test
# dimension: every research date is out-of-sample in AT MOST ONE fold, so
# concatenating every fold's test-window P&L never double-counts a day.
#
# WF_EMBARGO_DAYS = 1 -- positions are flat by 15:10 CT (the auto-flatten in
# rules/xfa_rules.py), so no position ever spans a trade-date boundary. The
# one-session embargo exists only to guard a feature that looks across the
# 17:00 CT overnight session open (e.g. something computed off the prior
# day's settle) from leaking the first test day's own overnight bar into the
# adjoining train window.
#
# WF_N_FOLDS = 8, WF_TRAIN_DAYS = 142 -- WF_TRAIN_DAYS is DERIVED, not chosen,
# and derived from the CALENDAR-COMPUTED research date count (below), never
# from a hardcoded literal: derive_train_days(n_research_days, 21, 1, 8) =
# n_research_days - 8*21 - 1. Today n_research_days == 311, so 311 - 168 - 1
# == 142 (~6.7 months, at least two quarterly futures rolls in every train
# window). Anchoring the fold grid at the END of the research slice (fold
# 7's test window ends on RESEARCH_END) means this particular train length
# makes fold 0's train window start EXACTLY on RESEARCH_START -- every one
# of the research dates gets used by the grid; none is stranded before fold
# 0's train start. Deriving from the actual calendar list (instead of the
# literal 311) means a calendar correction that changes the count moves
# WF_TRAIN_DAYS with it automatically, rather than going stale silently;
# test_311_research_trade_dates in tests/test_walk_forward.py still pins the
# count itself so a change is visible at review time.
WF_TEST_DAYS = 21
WF_STEP_DAYS = WF_TEST_DAYS
WF_EMBARGO_DAYS = 1
WF_N_FOLDS = 8


def derive_train_days(n_research_days: int, test_days: int, embargo_days: int, n_folds: int) -> int:
    """Train-window length that lets fold 0's train window start at index 0.

    The grid is anchored at the end: the last fold's test window ends on the
    last research date, and (because the test step equals the test length)
    fold 0's test window starts at index ``n_research_days - n_folds *
    test_days``. Fold 0's train window ends ``embargo_days`` sessions before
    that. A train window of exactly ``n_research_days - n_folds * test_days -
    embargo_days`` days therefore runs from index 0 with nothing left over.
    """
    return n_research_days - n_folds * test_days - embargo_days


def research_trade_dates_from_calendar() -> tuple[date, ...]:
    """Research-slice trade dates derived independently from the calendar.

    Weekdays from RESEARCH_START to RESEARCH_END inclusive, excluding
    ``FULL_CLOSURE`` days in ``data.cme_calendar.HOLIDAYS``. ``EARLY_HALT``
    days (e.g. Good Friday 2026, half-session holidays) ARE trade dates: the
    session still opens and settles, just early.
    """
    dates: list[date] = []
    one_day = timedelta(days=1)
    day = RESEARCH_START
    while day <= RESEARCH_END:
        if day.weekday() < 5:  # Monday=0 .. Friday=4
            holiday = HOLIDAYS.get(day)
            if holiday is None or holiday.kind is not HolidayKind.FULL_CLOSURE:
                dates.append(day)
        day += one_day
    return tuple(dates)


WF_TRAIN_DAYS = derive_train_days(
    len(research_trade_dates_from_calendar()), WF_TEST_DAYS, WF_EMBARGO_DAYS, WF_N_FOLDS
)  # 142


@dataclass(frozen=True)
class Fold:
    index: int
    train_dates: tuple[date, ...]
    embargo_dates: tuple[date, ...]
    test_dates: tuple[date, ...]

    @property
    def train_start(self) -> date:
        return self.train_dates[0]

    @property
    def train_end(self) -> date:
        return self.train_dates[-1]

    @property
    def test_start(self) -> date:
        return self.test_dates[0]

    @property
    def test_end(self) -> date:
        return self.test_dates[-1]


def _refuse_if_not_research_date(trade_date_: date) -> None:
    """The walk-forward must never see an embargo or holdout date."""
    if is_research_trade_date(trade_date_):
        return
    if trade_date_ >= HOLDOUT_START:
        raise ValueError(
            f"{trade_date_} is a sealed holdout trade date (>= {HOLDOUT_START}); "
            "the walk-forward must never see it"
        )
    if EMBARGO_START <= trade_date_ <= EMBARGO_END:
        raise ValueError(
            f"{trade_date_} is an embargo trade date ({EMBARGO_START}..{EMBARGO_END}); "
            "the walk-forward must never see it"
        )
    raise ValueError(f"{trade_date_} is not a research trade date")


def build_walk_forward_folds(
    trade_dates: Sequence[date],
    *,
    train_days: int,
    test_days: int,
    step_days: int,
    embargo_days: int,
    n_folds: int,
) -> tuple[Fold, ...]:
    """Build ``n_folds`` walk-forward folds anchored at the end of ``trade_dates``.

    The last fold's test window ends on the last date in ``trade_dates``; each
    earlier fold's test window ends ``step_days`` earlier. Each fold's train
    window is the ``train_days`` dates ending ``embargo_days`` sessions before
    that fold's first test date (a fixed-length rolling window). Folds are
    returned in chronological order (index 0 = earliest).

    Raises ``ValueError`` if ``trade_dates`` is not strictly increasing and
    unique, if any date falls outside the research slice (an embargo or
    holdout date must never reach the walk-forward), if any fold would need
    train history before the first date supplied, or if the fold parameters
    themselves are invalid: ``train_days``, ``test_days`` and ``n_folds`` must
    each be at least 1, ``embargo_days`` must be at least 0, and ``step_days``
    must be at least ``test_days`` (otherwise consecutive folds' test windows
    would overlap, and a date could be out-of-sample in more than one fold).
    """
    if train_days < 1:
        raise ValueError(f"train_days must be >= 1, got {train_days}")
    if test_days < 1:
        raise ValueError(f"test_days must be >= 1, got {test_days}")
    if n_folds < 1:
        raise ValueError(f"n_folds must be >= 1, got {n_folds}")
    if embargo_days < 0:
        raise ValueError(f"embargo_days must be >= 0, got {embargo_days}")
    if step_days < test_days:
        raise ValueError(
            f"step_days ({step_days}) must be >= test_days ({test_days}); a smaller "
            "step would make consecutive folds' test windows overlap"
        )

    dates = tuple(trade_dates)
    for earlier, later in zip(dates, dates[1:], strict=False):
        if later <= earlier:
            raise ValueError(
                f"trade_dates must be strictly increasing and unique: {earlier} then {later}"
            )
    for one_date in dates:
        _refuse_if_not_research_date(one_date)

    n_dates = len(dates)
    folds: list[Fold] = []
    for fold_index in range(n_folds):
        distance_from_end = (n_folds - 1 - fold_index) * step_days
        test_end_idx = (n_dates - 1) - distance_from_end
        test_start_idx = test_end_idx - test_days + 1
        embargo_start_idx = test_start_idx - embargo_days
        train_end_idx = embargo_start_idx - 1
        train_start_idx = train_end_idx - train_days + 1
        if test_start_idx < 0 or train_start_idx < 0:
            raise ValueError(
                f"fold {fold_index} lacks {train_days} days of history before its "
                f"test window (need {train_days - (train_end_idx + 1)} more leading dates)"
            )
        folds.append(
            Fold(
                index=fold_index,
                train_dates=dates[train_start_idx : train_end_idx + 1],
                embargo_dates=dates[embargo_start_idx:test_start_idx],
                test_dates=dates[test_start_idx : test_end_idx + 1],
            )
        )
    return tuple(folds)


def walk_forward_folds(trade_dates: Sequence[date]) -> tuple[Fold, ...]:
    """``build_walk_forward_folds`` using the module's WF_* constants."""
    return build_walk_forward_folds(
        trade_dates,
        train_days=WF_TRAIN_DAYS,
        test_days=WF_TEST_DAYS,
        step_days=WF_STEP_DAYS,
        embargo_days=WF_EMBARGO_DAYS,
        n_folds=WF_N_FOLDS,
    )


def _fold_report(fold: Fold) -> dict[str, object]:
    return {
        "index": fold.index,
        "train_start": fold.train_start.isoformat(),
        "train_end": fold.train_end.isoformat(),
        "n_train": len(fold.train_dates),
        "embargo_dates": [d.isoformat() for d in fold.embargo_dates],
        "test_start": fold.test_start.isoformat(),
        "test_end": fold.test_end.isoformat(),
        "n_test": len(fold.test_dates),
    }


def main() -> None:
    """Write reports/walk_forward_folds.json. Reads no parquet or vendor file."""
    trade_dates = research_trade_dates_from_calendar()
    folds = walk_forward_folds(trade_dates)

    report = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "constants": {
            "WF_TEST_DAYS": WF_TEST_DAYS,
            "WF_STEP_DAYS": WF_STEP_DAYS,
            "WF_EMBARGO_DAYS": WF_EMBARGO_DAYS,
            "WF_N_FOLDS": WF_N_FOLDS,
            "WF_TRAIN_DAYS": WF_TRAIN_DAYS,
        },
        "derivation": {
            "n_research_days": len(trade_dates),
            "formula": "n_research_days - n_folds * test_days - embargo_days",
            "arithmetic": (
                f"{len(trade_dates)} - {WF_N_FOLDS} * {WF_TEST_DAYS} - {WF_EMBARGO_DAYS} "
                f"= {WF_TRAIN_DAYS}"
            ),
        },
        "folds": [_fold_report(fold) for fold in folds],
    }

    out_path = REPO_ROOT / "reports" / "walk_forward_folds.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=1) + "\n")
    print(f"wrote {out_path} ({len(folds)} folds, {len(trade_dates)} research trade dates)")


if __name__ == "__main__":
    main()
