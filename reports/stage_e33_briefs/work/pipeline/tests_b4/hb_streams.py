"""Hand-built ZM MBO streams for B4 known-answer cases (LT4 and the record-level checks of P4.2 first bullet).

A stream is a list of events; each event is one or more MBO records, the last carrying F_LAST. The book has one
order per side (oid 1 bid, oid 2 ask by default) so the touch is set explicitly by `touch(...)`. Prices are in
ticks here and converted to Databento fixed point (ZM tick 0.10 USD = 100,000,000). Synthetic data only."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from synth_streams import (  # noqa: E402
    A_, C_, F_BAD, F_LAST, F_SNAP, MBO, N_, NS, R_, SA, SB, SN, TICK_FP, ct_ns,
)

IID = 900_001
TICK = TICK_FP["ZM"]
D = date(2023, 3, 15)  # CDT


def at(hh: int, mm: int, ss: float = 0.0, day: date = D) -> int:
    return ct_ns(day, hh, mm, ss)


@dataclass
class HB:
    """Builder: keeps the live order ids per side so `touch` can cancel and re-add in one event."""

    day: date = D
    rows: list[tuple] = field(default_factory=list)
    live: dict[int, list[tuple[int, int, int]]] = field(default_factory=lambda: {SB: [], SA: []})
    next_oid: int = 10

    def _rec(self, ts: int, oid: int, px: int, sz: int, fl: int, act: int, side: int, te: int | None) -> None:
        self.rows.append((ts, ts - 500_000 if te is None else te, IID, oid, px * TICK, sz, fl, act, side, 0))

    def snapshot(self, ts: int, bid: int | None, ask: int | None, flags_r: int = 0) -> "HB":
        self._rec(ts, 0, 0, 0, F_SNAP | flags_r, R_, SN, ts - 3600 * NS)
        self.live = {SB: [], SA: []}
        recs = []
        for side, px in ((SB, bid), (SA, ask)):
            if px is not None:
                oid = self.next_oid
                self.next_oid += 1
                self.live[side].append((oid, px, 5))
                recs.append((oid, px, side))
        for k, (oid, px, side) in enumerate(recs):
            self._rec(ts, oid, px, 5, F_SNAP | (F_LAST if k == len(recs) - 1 else 0), A_, side, ts - 3600 * NS)
        if not recs:
            self.rows[-1] = self.rows[-1][:6] + (self.rows[-1][6] | F_LAST,) + self.rows[-1][7:]
        return self

    def touch(self, ts: int, bid: int | None, ask: int | None, te: int | None = None, keep: tuple = ()) -> "HB":
        """One event: cancel every live order on the sides being set, add one order at the new price (None leaves
        that side empty; a side named in `keep` is left as is)."""
        recs: list[tuple] = []
        for side, px in ((SB, bid), (SA, ask)):
            if side in keep:
                continue
            for oid, opx, sz in self.live[side]:
                recs.append((oid, opx, sz, C_, side))
            self.live[side] = []
            if px is not None:
                oid = self.next_oid
                self.next_oid += 1
                self.live[side].append((oid, px, 5))
                recs.append((oid, px, 5, A_, side))
        if not recs:
            recs.append((0, 0, 0, N_, SN))
        for k, (oid, px, sz, act, side) in enumerate(recs):
            self._rec(ts, oid, px, sz, F_LAST if k == len(recs) - 1 else 0, act, side, te)
        return self

    def flag_bad(self, ts: int) -> "HB":
        self._rec(ts, 0, 0, 0, F_BAD | F_LAST, N_, SN, None)
        return self

    def build(self) -> np.ndarray:
        arr = np.array(self.rows, dtype=MBO)
        order = np.argsort(arr["ts_recv"], kind="stable")
        if not np.array_equal(order, np.arange(len(arr))):
            raise AssertionError("hand-built events must be written in ts_recv order")
        return arr
