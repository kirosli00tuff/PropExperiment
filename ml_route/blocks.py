"""M7.3: the calendar-only block cut and the CPCV splitter by trade date (Stage E.2b Task 2).

Block cut (Stage E.2a ruling on audit ML-A03). The training calendar is every CME trade date from
2019-05-06 to 2024-02-29 that is a trade date of at least one group calendar (data/calendars/,
data.group_session). Its n dates are cut in time order into six contiguous blocks of floor(n / 6)
dates; the sixth takes the remainder. No bar is read. The boundaries are the same for every
product and go into the route manifest before any fit.

CPCV (M7.3, M5.1). Blocks 1-5 only (block 6 is M5's pre-test). Every choice of two test blocks out
of five is one split (10 splits). For a split:
- validation dates = the dates of its two test blocks;
- embargo dates = one full calendar trade date on each side of each validation block (the date
  just before the block's first date and the date just after its last date, in the training
  calendar), unless that date is itself a validation date;
- training dates = the dates of blocks 1-5 that are neither validation nor embargo dates;
- purge: a training row whose target window [t, exit] overlaps the span of any validation date
  is dropped. A validation date's span is [earliest decision time, latest exit] over that date's
  rows (all products). Targets never cross a trade date, so on real data the purge removes
  nothing beyond the dates themselves; it is implemented and tested anyway.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from itertools import combinations

import numpy as np

from ml_route.constants import (
    CPCV_BLOCKS,
    CPCV_TEST_BLOCKS,
    EARLIEST_S_X,
    N_BLOCKS,
    TRAIN_LAST,
)


class BlockCutError(ValueError):
    """The block cut or a split violates M7.3."""


@dataclass(frozen=True)
class Block:
    number: int  # 1..6
    first: date
    last: date
    n_dates: int


@dataclass(frozen=True)
class BlockCut:
    dates: tuple[date, ...]  # the training calendar, ascending
    blocks: tuple[Block, ...]

    def block_of(self, day: date) -> int:
        for b in self.blocks:
            if b.first <= day <= b.last:
                return b.number
        raise BlockCutError(f"{day} is not in the training calendar's blocks")

    def dates_of(self, number: int) -> tuple[date, ...]:
        b = self.blocks[number - 1]
        return tuple(d for d in self.dates if b.first <= d <= b.last)

    def as_manifest(self) -> dict:
        return {"n_dates": len(self.dates),
                "blocks": [{"block": b.number, "first": b.first.isoformat(),
                            "last": b.last.isoformat(), "n_dates": b.n_dates}
                           for b in self.blocks]}


def training_calendar() -> tuple[date, ...]:
    """Every trade date of at least one group calendar, 2019-05-06..2024-02-29 (ML-A03)."""
    from data.calendars import GROUPS
    from data.group_session import load_group_calendar, trade_dates_between

    union: set[date] = set()
    for group in GROUPS:
        union.update(trade_dates_between(load_group_calendar(group), EARLIEST_S_X, TRAIN_LAST))
    return tuple(sorted(union))


def cut_blocks(dates: Sequence[date]) -> BlockCut:
    """Six contiguous blocks of floor(n / 6) dates in time order, the sixth taking the rest."""
    ordered = tuple(dates)
    if list(ordered) != sorted(set(ordered)):
        raise BlockCutError("the training calendar must be strictly ascending without repeats")
    n = len(ordered)
    if n < N_BLOCKS:
        raise BlockCutError(f"{n} dates cannot make {N_BLOCKS} blocks")
    size = n // N_BLOCKS
    blocks = []
    for k in range(N_BLOCKS):
        lo = k * size
        hi = n if k == N_BLOCKS - 1 else (k + 1) * size
        blocks.append(Block(k + 1, ordered[lo], ordered[hi - 1], hi - lo))
    return BlockCut(ordered, tuple(blocks))


def frozen_block_cut() -> BlockCut:
    return cut_blocks(training_calendar())


@dataclass(frozen=True)
class Split:
    index: int  # 0..9, in itertools.combinations order of the test-block pairs
    test_blocks: tuple[int, ...]
    validation_dates: frozenset[date]
    embargo_dates: frozenset[date]
    training_dates: frozenset[date]

    def label(self) -> str:
        return "split" + "".join(str(b) for b in self.test_blocks)


def cpcv_splits(cut: BlockCut) -> tuple[Split, ...]:
    """The 10 CPCV splits over blocks 1-5, two test blocks each (M7.3)."""
    pos = {d: i for i, d in enumerate(cut.dates)}
    pool = {d for b in CPCV_BLOCKS for d in cut.dates_of(b)}
    splits = []
    for idx, test in enumerate(combinations(CPCV_BLOCKS, CPCV_TEST_BLOCKS)):
        val = {d for b in test for d in cut.dates_of(b)}
        emb: set[date] = set()
        for b in test:
            block = cut.blocks[b - 1]
            for neighbour in (pos[block.first] - 1, pos[block.last] + 1):
                if 0 <= neighbour < len(cut.dates) and cut.dates[neighbour] not in val:
                    emb.add(cut.dates[neighbour])
        train = pool - val - emb
        splits.append(Split(idx, tuple(test), frozenset(val), frozenset(emb), frozenset(train)))
    return tuple(splits)


def validation_spans(days: np.ndarray, t_ns: np.ndarray, exit_ns: np.ndarray,
                     validation_dates: Iterable[date]) -> list[tuple[int, int]]:
    """[earliest decision time, latest exit] of every validation date that has rows."""
    val = set(validation_dates)
    spans: dict[date, list[int]] = {}
    for d, t, x in zip(days.tolist(), t_ns.tolist(), exit_ns.tolist(), strict=True):
        if d in val:
            s = spans.setdefault(d, [t, x])
            s[0], s[1] = min(s[0], t), max(s[1], x)
    return sorted((s[0], s[1]) for s in spans.values())


def split_masks(split: Split, days: np.ndarray, t_ns: np.ndarray,
                exit_ns: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    """(training mask, validation mask, rows purged) over a row table's (date, t, exit)."""
    day_list = days.tolist()
    val_mask = np.fromiter((d in split.validation_dates for d in day_list), bool, len(day_list))
    train_mask = np.fromiter((d in split.training_dates for d in day_list), bool, len(day_list))
    spans = validation_spans(days, t_ns, exit_ns, split.validation_dates)
    overlap = np.zeros(len(day_list), dtype=bool)
    for lo, hi in spans:
        overlap |= (t_ns <= hi) & (exit_ns >= lo)
    purged = int(np.count_nonzero(train_mask & overlap))
    return train_mask & ~overlap, val_mask, purged


def assert_fold(split: Split, days: np.ndarray, t_ns: np.ndarray, exit_ns: np.ndarray,
                train_mask: np.ndarray, val_mask: np.ndarray) -> None:
    """M7.3's fold test on a saved row index: raises on any violation."""
    tr_days = {d for d, m in zip(days.tolist(), train_mask.tolist(), strict=True) if m}
    va_days = {d for d, m in zip(days.tolist(), val_mask.tolist(), strict=True) if m}
    if tr_days & va_days:
        both = sorted(tr_days & va_days)[:3]
        raise BlockCutError(f"{split.label()}: dates on both sides: {both}")
    if tr_days & split.embargo_dates:
        raise BlockCutError(f"{split.label()}: embargo dates in training")
    if tr_days - split.training_dates:
        raise BlockCutError(f"{split.label()}: training rows outside the split's training dates")
    for lo, hi in validation_spans(days, t_ns, exit_ns, split.validation_dates):
        bad = train_mask & (t_ns <= hi) & (exit_ns >= lo)
        if bad.any():
            raise BlockCutError(f"{split.label()}: a training target window overlaps a "
                                "validation date")
