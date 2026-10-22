"""Synthetic mbp-1 records, books and DBN files for the pilot tests. No network, no real data."""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pilot_common as pc
from pilot_stream import DayAccumulator, DayBook

TICK = 0.25
TICK_1E9 = 250_000_000
S = pc.NS
MS = pc.MS
UNDEF = np.iinfo(np.int64).max
DAY = date(2023, 11, 14)  # a regular Tuesday (CST), MAIN 14:30Z-21:00Z
G = pc.ns_of(datetime(2023, 11, 14, 15, 0, tzinfo=UTC))  # a MAIN grid time
J = G + pc.LATENCY_NS
IID = 111

DTYPE = np.dtype([("rtype", "u1"), ("instrument_id", "<u4"), ("ts_event", "<u8"),
                  ("price", "<i8"), ("size", "<u4"), ("action", "S1"), ("side", "S1"),
                  ("flags", "u1"), ("ts_recv", "<u8"), ("sequence", "<u4"),
                  ("bid_px_00", "<i8"), ("ask_px_00", "<i8"), ("bid_sz_00", "<u4"),
                  ("ask_sz_00", "<u4")])


def px(ticks: int | None) -> int:
    return UNDEF if ticks is None else int(ticks) * TICK_1E9


class Tape:
    """Builds a time-ordered record list; the book carries over between records."""

    def __init__(self, bid: int | None = 100, ask: int | None = 101, bsz: int = 1,
                 asz: int = 1) -> None:
        self.book = {"bid": bid, "ask": ask, "bsz": bsz, "asz": asz}
        self.rows: list[dict[str, Any]] = []

    def quote(self, t: int, **book: Any) -> Tape:
        self.book = {**self.book, **book}
        self.rows.append({"t": t, "action": "A", **self.book})
        return self

    def trade(self, t: int, price: int, size: int, side: str, **extra: Any) -> Tape:
        self.rows.append({"t": t, "action": "T", "price": price, "size": size, "side": side,
                          **self.book, **extra})
        return self

    def array(self) -> np.ndarray:
        return records(self.rows)


def records(rows: list[dict[str, Any]]) -> np.ndarray:
    out = np.zeros(len(rows), dtype=DTYPE)
    for k, r in enumerate(rows):
        out[k] = (1, r.get("iid", IID), r["t"], px(r.get("price")), r.get("size", 0),
                  r.get("action", "A").encode(), r.get("side", "N").encode(), r.get("flags", 0),
                  r.get("recv", r["t"] + 1000), r.get("seq", k + 1), px(r.get("bid")),
                  px(r.get("ask")), r.get("bsz", 0) if r.get("bid") is not None else 0,
                  r.get("asz", 0) if r.get("ask") is not None else 0)
    return out


def main_plan(grid: list[int] | None = None, lo: int | None = None,
              hi: int | None = None) -> pc.DayPlan:
    lo = G - 10 * 60 * S if lo is None else lo
    hi = G + 10 * 60 * S if hi is None else hi
    return pc.make_test_plan(DAY, [pc.Piece(pc.MAIN, lo, hi)], [G] if grid is None else grid)


def book_from(tape: Tape | np.ndarray, plan: pc.DayPlan | None = None,
              segments: int = 1) -> DayBook:
    arr = tape.array() if isinstance(tape, Tape) else tape
    acc = DayAccumulator(main_plan() if plan is None else plan, TICK_1E9)
    for part in np.array_split(arr, segments):
        acc.feed(part)
    return acc.finish()


# ------------------------------------------------------------------ DBN files ----
def write_dbn(path: Path, rows: list[dict[str, Any]], *, root: str, start_ns: int, end_ns: int,
              intervals: list[tuple[date, date, str]], schema: str = "mbp-1",
              dataset: str = "GLBX.MDP3") -> Path:
    """A zstd DBN file with an mbp-1 header (symbology mappings included) and ``rows``."""
    import databento_dbn as dbn
    import zstandard

    symbol = pc.symbol_for(root)
    mapping = SimpleNamespace(raw_symbol=symbol, intervals=[
        SimpleNamespace(start_date=a, end_date=b, symbol=s) for a, b, s in intervals])
    kind = dbn.Schema.MBP_1 if schema == "mbp-1" else dbn.Schema.OHLCV_1M
    meta = dbn.Metadata(dataset, start_ns, dbn.SType.CONTINUOUS, dbn.SType.INSTRUMENT_ID, kind,
                        symbols=[symbol], partial=[], not_found=[], mappings=[mapping],
                        end=end_ns)
    actions = {"A": dbn.Action.ADD, "C": dbn.Action.CANCEL, "M": dbn.Action.MODIFY,
               "R": dbn.Action.CLEAR, "T": dbn.Action.TRADE}
    sides = {"A": dbn.Side.ASK, "B": dbn.Side.BID, "N": dbn.Side.NONE}
    raw = bytes(meta.encode())
    for k, r in enumerate(rows):
        bid, ask = r.get("bid"), r.get("ask")
        level = dbn.BidAskPair(bid_px=px(bid), ask_px=px(ask),
                               bid_sz=r.get("bsz", 0) if bid is not None else 0,
                               ask_sz=r.get("asz", 0) if ask is not None else 0,
                               bid_ct=1, ask_ct=1)
        rec = dbn.MBP1Msg(1, int(r.get("iid", IID)), int(r["t"]), px(r.get("price")),
                          int(r.get("size", 0)), actions[r.get("action", "A")],
                          sides[r.get("side", "N")], 0, int(r.get("recv", r["t"] + 1000)),
                          flags=int(r.get("flags", 0)), sequence=int(r.get("seq", k + 1)),
                          levels=level)
        raw += bytes(rec)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(zstandard.ZstdCompressor().compress(raw))
    return path


def pilot_file(base: Path, root: str, start: str, end: str) -> Path:
    from data.pull_universe import bound_token

    name = f"range={bound_token(start)}_{bound_token(end)}.dbn.zst"
    return base / "GLBX.MDP3" / "mbp-1" / f"{root}_v_0" / name


def session_tape(day: date, cal: Any, every_s: int = 30, bid: int = 100, ask: int = 101,
                 trades_every: int = 7) -> list[dict[str, Any]]:
    """A quiet, valid book over the whole trade date: a quote every ``every_s`` seconds and a
    sell-aggressor trade at the bid every ``trades_every`` quotes."""
    plan = pc.build_day_plan(cal, day)
    rows: list[dict[str, Any]] = []
    lo = pc.day_window_ns(day)[0] + 30 * 60 * S  # 16:30 CT, in the pre-open hour
    hi = plan.open_hi
    t, k = lo, 0
    while t < hi:
        rows.append({"t": t, "action": "A", "bid": bid, "ask": ask, "bsz": 5, "asz": 5})
        if k % trades_every == 0:
            rows.append({"t": t + 1 * S, "action": "T", "price": bid, "size": 3, "side": "A",
                         "bid": bid, "ask": ask, "bsz": 5, "asz": 5})
        t += every_s * S
        k += 1
    return rows
