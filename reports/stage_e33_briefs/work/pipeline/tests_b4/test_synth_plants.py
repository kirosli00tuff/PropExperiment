"""The generator's planted B3 cases (synth_streams.Episodes.mixed_trades, unbooked_fills) have the record structure
of R-B3-FD6 and R-B3-FD7 when replayed with the E.31 book (mbo_book31). Synthetic data only."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import synth_streams as ss  # noqa: E402
import mbo_book31 as mb  # noqa: E402

DAY = date(2023, 3, 1)
MIXED = ((9, 0, 7.3), (10, 0, 30.1), (11, 3, 1.0), (12, 0, 0.5))
UNBOOKED = ((9, 30, 2.5), (10, 30, 3.5))


def _replay_events(arr: np.ndarray, iid: int) -> list[dict]:
    """Per event (records up to F_LAST) of instrument iid: its records (with booked-before flag) and the
    level totals after it at the prices it names."""
    book = mb.Book()
    events, cur = [], []
    for r in arr[arr["instrument_id"] == iid]:
        act, side, px, sz, oid, fl = (int(r[k]) for k in ("action", "side", "price", "size", "order_id", "flags"))
        cur.append((int(r["ts_recv"]), act, side, px, sz, oid, oid in book.orders))
        if act == ss.R_:
            book.clear(bool(fl & ss.F_SNAP))
        elif book.started:
            if book.in_snapshot and not fl & ss.F_SNAP:
                book.end_snapshot()
            if act in (ss.A_, ss.M_) and side in (ss.SB, ss.SA):
                bs = mb.BID if side == ss.SB else mb.ASK
                (book.add if act == ss.A_ else book.modify)(oid, bs, px, sz)
            elif act == ss.C_:
                book.cancel(oid, sz)
            if fl & ss.F_SNAP and fl & ss.F_LAST:
                book.end_snapshot()
        if fl & ss.F_LAST:
            events.append({"recs": cur})
            cur = []
            events[-1]["level_after"] = {(s, p): book.level_total(s, p) for s in (mb.BID, mb.ASK)
                                         for p in {x[3] for x in events[-1]["recs"] if x[3]}}
    return events


def test_planted_mixed_and_unbooked_cases_have_the_ruled_structure() -> None:
    prm = ss.ZMParams()
    ep = ss.Episodes(mixed_trades=MIXED, unbooked_fills=UNBOOKED, neg_latency_share=0.0, equal_recv_share=0.0)
    arr, _ = ss.make_zm_day(DAY, 99, prm, ep, fair0=4000)
    assert bool(np.all(np.diff(arr["ts_recv"]) >= 0))
    events = _replay_events(arr, prm.iid)
    mixed = unbooked = 0
    for k, e in enumerate(events):
        acts = [x[1] for x in e["recs"]]
        if acts and acts[0] == ss.T_:
            fills = {x[5]: x[4] for x in e["recs"] if x[1] == ss.F_}
            cancels = [x for x in e["recs"] if x[1] == ss.C_]
            last = cancels[-1] if cancels else None
            # FD6: the level's last record is a C of an order partly filled (fill lots < its cancelled size)
            added = {x[5] for x in e["recs"] if x[1] == ss.A_}
            if last is not None and last[5] in fills and fills[last[5]] < last[4] and last[5] not in added:
                side = mb.BID if last[2] == ss.SB else mb.ASK
                assert e["level_after"][(side, last[3])] == 0  # that one record emptied the touch level
                nxt = events[k + 1]["recs"][0]
                assert nxt[1] == ss.A_ and nxt[3] == last[3] and 0 < nxt[0] - last[0] <= 100 * ss.MS
                mixed += 1
            # FD7: an F record whose order was not in the book when the F arrived, added and cancelled after it
            for x in e["recs"]:
                if x[1] == ss.F_ and not x[6]:
                    same = [y for y in e["recs"] if y[5] == x[5]]
                    assert [y[1] for y in same] == [ss.F_, ss.A_, ss.C_]
                    unbooked += 1
    assert mixed == len(MIXED)
    assert unbooked == len(UNBOOKED)


def test_no_plants_by_default_keeps_the_stream_unchanged() -> None:
    a, _ = ss.make_zm_day(DAY, 5, ss.ZMParams(rate_day=2.0, rate_night=0.5), ss.Episodes(), fair0=4000)
    b, _ = ss.make_zm_day(DAY, 5, ss.ZMParams(rate_day=2.0, rate_night=0.5),
                          ss.Episodes(mixed_trades=(), unbooked_fills=()), fair0=4000)
    assert a.tobytes() == b.tobytes()
