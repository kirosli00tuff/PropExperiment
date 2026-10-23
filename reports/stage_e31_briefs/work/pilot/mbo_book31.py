"""The ZM order book of one instrument, rebuilt order by order from Databento MBO: spec section 3.

Record semantics (reports/stage_e31_briefs/research/data_facts.md a1-a2 and Databento's own book
example, research/pages/data/db_ex_lob.html.txt):
- A add (back of its level); C cancel ``size`` lots (full or partial; the order leaves at 0);
  M modify to the record's price and size: a size decrease keeps priority, a size increase or a
  price change sends the order to the back of its (new) level; a modify of an unknown order is an
  add; R clear (snapshot start, or a CME channel reset); T, F and N do not change the book.
- Snapshot (00:00 UTC each weekday): R then A records with F_SNAPSHOT in priority order per level;
  the snapshot ends at its F_LAST record (or at the first record without F_SNAPSHOT).
- F_MAYBE_BAD_BOOK marks the book bad until the next R (spec section 2, book validity).

TOP state (spec 3.1, CME S4 text): one TOP order per side.
- An order entering (add, or a price-changing modify) becomes TOP when its displayed size is at
  least TOP Min and (i) its price betters the best price on its side (or the side is empty), or
  (ii) it joins the side's best level and that level has had no TOP order since it was
  established. A new TOP replaces the side's old one.
- TOP is lost on a full cancel, a size increase, a price change to a level that does not better
  the market, a new TOP order on the side, or when the lots counted against TOP Max reach it
  (counted from F records of the TOP order; before trade date 2023-10-02 the order's own initially
  aggressed quantity counts too, CME S7). A size decrease keeps TOP.
- Snapshot: TOP is not disseminated, so at the snapshot's end the first order of each side's best
  level is taken as TOP with 0 lots counted, the best levels are marked as having had a TOP and
  the other levels as not (the conservative reading for the virtual order: a TOP order only ever
  takes volume ahead of it). Stated in README_measure31.md.
Prices are int64 fixed point (1e-9); sides are 0 = bid, 1 = ask.
"""

from __future__ import annotations

import bisect

import numpy as np

BID, ASK = 0, 1
ACT_ADD, ACT_CANCEL, ACT_MODIFY = ord("A"), ord("C"), ord("M")
ACT_CLEAR, ACT_TRADE, ACT_FILL, ACT_NONE = ord("R"), ord("T"), ord("F"), ord("N")
SIDE_ASK_CODE, SIDE_BID_CODE, SIDE_NONE_CODE = ord("A"), ord("B"), ord("N")
F_LAST, F_TOB, F_SNAPSHOT, F_MBP = 1 << 7, 1 << 6, 1 << 5, 1 << 4
F_BAD_TS_RECV, F_MAYBE_BAD_BOOK = 1 << 3, 1 << 2
UNDEF_PRICE = int(np.iinfo(np.int64).max)

# order record: [side, price, size, prio]; level record: [total size, {oid: None} in priority
# order, had_top]
O_SIDE, O_PRICE, O_SIZE, O_PRIO = 0, 1, 2, 3
L_TOTAL, L_ORDERS, L_HAD_TOP = 0, 1, 2


def book_side(side_code: int) -> int:
    """MBO side code (A ask, B bid) -> 0 bid / 1 ask; -1 for N."""
    if side_code == SIDE_BID_CODE:
        return BID
    if side_code == SIDE_ASK_CODE:
        return ASK
    return -1


def time_axis(ts_event: np.ndarray, ts_recv: np.ndarray, flags: np.ndarray
              ) -> tuple[np.ndarray, int]:
    """Spec section 2: ts_event made non-decreasing in file order. Snapshot records carry the
    snapshot generation time (ts_recv) instead of an event time, so they enter the running maximum
    with ts_recv; inversions are counted over the other records only. Returns (time, inversions)."""
    ev = ts_event.astype(np.int64)
    snap = (flags & F_SNAPSHOT) != 0
    eff = np.where(snap, ts_recv.astype(np.int64), ev)
    t = np.maximum.accumulate(eff) if len(eff) else eff
    real = ev[~snap]
    inversions = int(np.count_nonzero(real[1:] < np.maximum.accumulate(real)[:-1])) if len(
        real) > 1 else 0
    return t, inversions


class Book:
    """One instrument's displayed outright book with time priority and TOP state."""

    __slots__ = ("orders", "levels", "prices", "top", "top_count", "seq", "started", "bad",
                 "in_snapshot", "top_min", "top_max", "count_initial", "anomalies")

    def __init__(self, top_min: int = 1, top_max: int = 100, count_initial: bool = False) -> None:
        self.orders: dict[int, list[int]] = {}
        self.levels: tuple[dict[int, list], dict[int, list]] = ({}, {})
        self.prices: tuple[list[int], list[int]] = ([], [])  # ascending
        self.top = [0, 0]  # TOP order id per side (0 = none)
        self.top_count = [0, 0]  # lots counted against TOP Max
        self.seq = 0  # next priority number
        self.started = False  # an R record has been seen (valid start)
        self.bad = False  # F_MAYBE_BAD_BOOK seen since the last R
        self.in_snapshot = False
        self.top_min, self.top_max, self.count_initial = top_min, top_max, count_initial
        self.anomalies: dict[str, int] = {}

    # ------------------------------------------------------------------ queries ----
    def best(self, side: int) -> int | None:
        p = self.prices[side]
        if not p:
            return None
        return p[-1] if side == BID else p[0]

    def level_total(self, side: int, price: int) -> int:
        lvl = self.levels[side].get(price)
        return 0 if lvl is None else lvl[L_TOTAL]

    def queue(self, side: int, price: int) -> list[tuple[int, int, int]]:
        """[(order id, size, prio)] at (side, price) in time priority order."""
        lvl = self.levels[side].get(price)
        if lvl is None:
            return []
        orders = self.orders
        return [(oid, orders[oid][O_SIZE], orders[oid][O_PRIO]) for oid in lvl[L_ORDERS]]

    def is_valid(self) -> bool:
        """Spec section 2: a started, not-bad book with both sides present, neither crossed nor
        locked."""
        if not self.started or self.bad:
            return False
        bp, ap = self.prices
        return bool(bp) and bool(ap) and bp[-1] < ap[0]

    def _note(self, key: str) -> None:
        self.anomalies[key] = self.anomalies.get(key, 0) + 1

    # ------------------------------------------------------------------ mutations ----
    def clear(self, snapshot: bool) -> None:
        self.orders = {}
        self.levels = ({}, {})
        self.prices = ([], [])
        self.top = [0, 0]
        self.top_count = [0, 0]
        self.started = True
        self.bad = False
        self.in_snapshot = snapshot

    def mark_bad(self) -> None:
        self.bad = True

    def end_snapshot(self) -> None:
        """Conservative TOP state after a snapshot (module docstring)."""
        if not self.in_snapshot:
            return
        self.in_snapshot = False
        for side in (BID, ASK):
            for lvl in self.levels[side].values():
                lvl[L_HAD_TOP] = False
            price = self.best(side)
            if price is None:
                continue
            lvl = self.levels[side][price]
            lvl[L_HAD_TOP] = True
            first = next(iter(lvl[L_ORDERS]))
            if self.orders[first][O_SIZE] >= self.top_min:
                self.top[side] = first
                self.top_count[side] = 0

    def _betters(self, side: int, price: int) -> bool:
        b = self.best(side)
        if b is None:
            return True
        return price > b if side == BID else price < b

    def _insert(self, oid: int, side: int, price: int, size: int) -> list:
        levels = self.levels[side]
        lvl = levels.get(price)
        if lvl is None:
            lvl = levels[price] = [0, {}, False]
            bisect.insort(self.prices[side], price)
        prio = self.seq
        self.seq += 1
        self.orders[oid] = [side, price, size, prio]
        lvl[L_ORDERS][oid] = None
        lvl[L_TOTAL] += size
        return lvl

    def _remove(self, oid: int, order: list[int]) -> None:
        side, price = order[O_SIDE], order[O_PRICE]
        lvl = self.levels[side][price]
        del lvl[L_ORDERS][oid]
        lvl[L_TOTAL] -= order[O_SIZE]
        if not lvl[L_ORDERS]:
            del self.levels[side][price]
            self.prices[side].remove(price)
        del self.orders[oid]

    def _grant_top(self, side: int, oid: int, lvl: list, counted: int) -> None:
        if counted >= self.top_max:
            return
        self.top[side] = oid
        self.top_count[side] = counted
        lvl[L_HAD_TOP] = True

    def _entry_top(self, oid: int, side: int, price: int, size: int, betters: bool,
                   lvl: list, counted: int) -> None:
        if size < self.top_min:
            return
        if betters or not lvl[L_HAD_TOP] and self.best(side) == price and len(lvl[L_ORDERS]) > 1:
            self._grant_top(side, oid, lvl, counted)

    def add(self, oid: int, side: int, price: int, size: int, aggressed: int = 0) -> None:
        """A record. ``aggressed``: lots this order took as an aggressor just before resting
        (counted against TOP Max only under the pre-2023-10-02 rule)."""
        if oid in self.orders:
            self._note("add_duplicate_id")
            self.cancel(oid, self.orders[oid][O_SIZE])
        if size <= 0:
            self._note("add_nonpositive_size")
            return
        betters = self._betters(side, price)
        lvl = self._insert(oid, side, price, size)
        if not self.in_snapshot:
            self._entry_top(oid, side, price, size, betters, lvl,
                            aggressed if self.count_initial else 0)

    def cancel(self, oid: int, size: int) -> None:
        """C record: ``size`` lots leave the order; the order leaves at 0 (a full cancel loses
        TOP; a partial one keeps priority and TOP)."""
        order = self.orders.get(oid)
        if order is None:
            self._note("cancel_unknown_order")
            return
        side = order[O_SIDE]
        if size >= order[O_SIZE]:
            if size > order[O_SIZE]:
                self._note("cancel_more_than_size")
            self._remove(oid, order)
            if self.top[side] == oid:
                self.top[side] = 0
            return
        order[O_SIZE] -= size
        self.levels[side][order[O_PRICE]][L_TOTAL] -= size

    def modify(self, oid: int, side: int, price: int, size: int) -> None:
        """M record (module docstring)."""
        order = self.orders.get(oid)
        if order is None:
            self._note("modify_unknown_order_as_add")
            self.add(oid, side, price, size)
            return
        if order[O_SIDE] != side:
            self._note("modify_side_change")
            self.cancel(oid, order[O_SIZE])
            self.add(oid, side, price, size)
            return
        if size <= 0:
            self.cancel(oid, order[O_SIZE])
            return
        was_top = self.top[side] == oid
        if price != order[O_PRICE]:
            counted = self.top_count[side]
            self._remove(oid, order)
            if was_top:
                self.top[side] = 0
            betters = self._betters(side, price)
            lvl = self._insert(oid, side, price, size)
            if was_top:  # keeps TOP only on a price change that betters the market (S4)
                if betters and size >= self.top_min:
                    self._grant_top(side, oid, lvl, counted)
            elif not self.in_snapshot:
                self._entry_top(oid, side, price, size, betters, lvl, 0)
            return
        lvl = self.levels[side][price]
        if size > order[O_SIZE]:
            del lvl[L_ORDERS][oid]
            lvl[L_ORDERS][oid] = None
            order[O_PRIO] = self.seq
            self.seq += 1
            if was_top:
                self.top[side] = 0
        lvl[L_TOTAL] += size - order[O_SIZE]
        order[O_SIZE] = size

    def on_fill(self, oid: int, size: int) -> None:
        """F record of a resting order: lots counted against TOP Max."""
        order = self.orders.get(oid)
        if order is None:
            return
        side = order[O_SIDE]
        if self.top[side] == oid:
            self.top_count[side] += size
            if self.top_count[side] >= self.top_max:
                self.top[side] = 0  # keeps its timestamp (CME S3/S4)

    def top_at(self, side: int, price: int) -> tuple[int, int] | None:
        """(TOP order id, TOP room) when the side's TOP order rests at ``price``."""
        oid = self.top[side]
        if oid == 0:
            return None
        order = self.orders.get(oid)
        if order is None or order[O_PRICE] != price:
            return None
        return oid, self.top_max - self.top_count[side]
