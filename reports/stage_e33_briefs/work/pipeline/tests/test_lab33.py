"""Unit tests for lab33 (Coder-A labels) on hand-built books; every expected value is worked out by hand in
the comments. Synthetic data only (INTERFACE rule 1 does not bind synthetic data)."""

from __future__ import annotations

import math
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lab33 as lb  # noqa: E402
import mbo_book31 as mb  # noqa: E402

NS, MIN = lb.NS, lb.MIN_NS
TICK = 100_000_000  # ZM 0.10 USD in Databento fixed point (1e-9)
CT = ZoneInfo("America/Chicago")
D = date(2023, 3, 15)  # CDT: 08:35 CT = 13:35 UTC
F = lb.FEE_TICKS


def ct(hh: int, mm: int, ss: float = 0.0) -> int:
    whole = int(ss)
    base = int(datetime(D.year, D.month, D.day, hh, mm, whole, tzinfo=CT).timestamp()) * NS
    return base + round((ss - whole) * NS)


T0 = ct(8, 35)


def day(**kw) -> lb.DayInputs:
    args = dict(
        date=D.isoformat(),
        t0_ns=T0,
        close_ns=ct(13, 13),
        session_end_ns=ct(13, 20),
        releases=(),
        limits=None,
        tick=TICK,
        excluded=False,
        sigma_zm=2.0,
    )
    args.update(kw)
    return lb.DayInputs(**args)


def hist(states) -> lb.BookHistory:
    """states: (ts, bid ticks or None, ask ticks or None[, good]); an update per state."""
    t, b, a, g = [], [], [], []
    for s in states:
        t.append(s[0])
        b.append(lb.NO_PX if s[1] is None else s[1])
        a.append(lb.NO_PX if s[2] is None else s[2])
        g.append(s[3] if len(s) > 3 else True)
    return lb.BookHistory.of(np.array(t), np.array(b), np.array(a), np.array(g))


BASE = (ct(8, 0), 4000, 4001)  # bid 4000, ask 4001 from 08:00


# ------------------------------------------------------------------------------- record tapes (replay) --
class Tape:
    """Hand-built MBO records for one instrument: one resting order per side."""

    def __init__(self, iid: int = 7) -> None:
        self.rows: list[tuple] = []
        self.iid = iid
        self.next_oid = 1
        self.live = {"B": None, "A": None}  # side code -> (oid, price)

    def rec(self, ts, act, side, px=0, sz=0, oid=0, flags=0, ts_event=None, iid=None):
        self.rows.append(
            (
                ts,
                ts if ts_event is None else ts_event,
                self.iid if iid is None else iid,
                oid,
                px,
                sz,
                flags,
                ord(act),
                ord(side),
            )
        )

    def snapshot(self, ts, bid, ask):
        self.rec(ts, "R", "N", flags=mb.F_SNAPSHOT | mb.F_BAD_TS_RECV)
        self.live = {"B": None, "A": None}
        self._add(ts, "B", bid, mb.F_SNAPSHOT)
        self._add(ts, "A", ask, mb.F_SNAPSHOT | mb.F_LAST)

    def _add(self, ts, side, px_ticks, flags=0, ts_event=None):
        oid = self.next_oid
        self.next_oid += 1
        self.rec(ts, "A", side, px_ticks * TICK, 5, oid, flags, ts_event)
        self.live[side] = (oid, px_ticks)

    def quote(self, ts, bid="keep", ask="keep", flags=0, last=True, ts_event=None):
        """Replace the bid and/or ask (None empties that side); the last record carries F_LAST."""
        ops = []
        for side, new in (("B", bid), ("A", ask)):
            if new == "keep":
                continue
            if self.live[side] is not None:
                ops.append(("C", side, self.live[side]))
            if new is not None:
                ops.append(("A", side, new))
        if not ops:
            ops.append(("N", "N", None))
        for j, (act, side, arg) in enumerate(ops):
            fl = flags | (mb.F_LAST if last and j == len(ops) - 1 else 0)
            if act == "C":
                oid, px = arg
                self.rec(ts, "C", side, px * TICK, 5, oid, fl, ts_event)
                self.live[side] = None
            elif act == "A":
                self._add(ts, side, arg, fl, ts_event)
            else:
                self.rec(ts, "N", "N", flags=fl, ts_event=ts_event)

    def records(self) -> dict[str, np.ndarray]:
        cols = list(zip(*self.rows, strict=True))
        names = (
            "ts_recv",
            "ts_event",
            "instrument_id",
            "order_id",
            "price",
            "size",
            "flags",
            "action",
            "side",
        )
        dt = (
            np.int64,
            np.int64,
            np.uint32,
            np.uint64,
            np.int64,
            np.uint32,
            np.uint8,
            np.uint8,
            np.uint8,
        )
        return {n: np.array(c, dtype=d) for n, c, d in zip(names, cols, dt, strict=True)}


def test_replay_updates_only_at_f_last_and_skips_records_before_start():
    tape = Tape()
    tape.rec(ct(7, 0), "A", "B", 3999 * TICK, 1, 99, mb.F_LAST)  # before the first R: skipped
    tape.snapshot(ct(7, 1), 4000, 4001)
    tape.quote(ct(7, 2), bid=4001, last=False)  # mid-event: no update
    tape.quote(ct(7, 2, 0.5), ask=4002)  # closes the event: one update with bid 4001, ask 4002
    tape.rec(ct(7, 3), "A", "B", 1, 1, 50, mb.F_LAST, iid=8)  # another instrument: ignored
    h = lb.replay(tape.records(), 7, TICK)
    assert h.t.tolist() == [ct(7, 1), ct(7, 2, 0.5)]
    assert h.bid.tolist() == [4000, 4001] and h.ask.tolist() == [4001, 4002]
    assert h.good.tolist() == [True, True]
    assert h.stats["records_before_start"] == 1


def test_replay_bad_flag_marks_bad_until_next_clear_and_keeps_same_ts_updates():
    tape = Tape()
    tape.snapshot(ct(7, 0), 4000, 4001)
    tape.quote(ct(7, 1), bid=4001, flags=mb.F_MAYBE_BAD_BOOK)
    tape.quote(ct(7, 1), ask=4003)  # same ts_recv: a second update, still bad
    tape.snapshot(ct(7, 2), 3990, 3991)  # R clears the bad mark
    h = lb.replay(tape.records(), 7, TICK)
    assert h.t.tolist() == [ct(7, 0), ct(7, 1), ct(7, 1), ct(7, 2)]
    assert h.good.tolist() == [True, False, False, True]
    assert h.both_ok.tolist() == [True, False, False, True]


def test_replay_end_ns_truncates_at_ts_recv_inclusive():
    tape = Tape()
    tape.snapshot(ct(7, 0), 4000, 4001)
    tape.quote(ct(7, 1), bid=4001)
    tape.quote(ct(7, 2), bid=3999)
    h = lb.replay(tape.records(), 7, TICK, end_ns=ct(7, 1))
    assert h.t.tolist() == [ct(7, 0), ct(7, 1)]


def test_lt4_ts_recv_clock_and_order():
    """Records with ts_recv < ts_event stay in ts_recv order; update times are ts_recv; an input not in
    ts_recv order is stable-sorted (counted) and gives the same history as the sorted input."""
    tape = Tape()
    tape.snapshot(ct(7, 0), 4000, 4001)
    # ts_recv 07:01 but ts_event 07:03 (ts_recv < ts_event), then ts_recv 07:02 with ts_event 07:01
    tape.quote(ct(7, 1), bid=4001, ts_event=ct(7, 3))
    tape.quote(ct(7, 2), bid=4002, ts_event=ct(7, 1))
    rec = tape.records()
    h = lb.replay(rec, 7, TICK)
    assert h.t.tolist() == [ct(7, 0), ct(7, 1), ct(7, 2)]  # ts_recv, not ts_event
    assert h.bid.tolist() == [4000, 4001, 4002]
    assert h.stats["ts_recv_decreases"] == 0
    perm = np.array(
        [0, 1, 2, 5, 6, 3, 4]
    )  # the 07:02 event moved before the 07:01 event in file order
    assert len(rec["ts_recv"]) == 7
    shuffled = {k: v[perm] for k, v in rec.items()}
    h2 = lb.replay(shuffled, 7, TICK)
    assert h2.stats["ts_recv_decreases"] == 1
    assert h2.t.tolist() == h.t.tolist() and h2.bid.tolist() == h.bid.tolist()


def test_replay_rejects_off_tick_prices():
    tape = Tape()
    tape.rec(ct(7, 0), "R", "N", flags=mb.F_SNAPSHOT)
    tape.rec(ct(7, 0), "A", "B", 4000 * TICK + 1, 1, 1, mb.F_SNAPSHOT | mb.F_LAST)
    with pytest.raises(lb.LabelError):
        lb.replay(tape.records(), 7, TICK)


# ------------------------------------------------------------------------------------ executable prices --
def test_entry_fills_as_of_t_plus_L_inclusive():
    t = T0
    h = hist([BASE, (t + 500_000_000, 4001, 4002), (t + NS, 4002, 4003), (t + NS + 1, 4005, 4006)])
    # as of t + L = t + 1 s: the update stamped exactly t + 1 s counts, the one 1 ns later does not
    long_ = lb.entry_fill(h, "FH", 15, t, lb.LONG)
    short = lb.entry_fill(h, "FH", 15, t, lb.SHORT)
    assert (long_.made, long_.fill_ns, long_.price, long_.flags) == (True, t + NS, 4003, 0)
    assert (short.made, short.fill_ns, short.price, short.flags) == (True, t + NS, 4002, 0)


def test_entry_fallback_and_exit_fallback():
    t = T0
    h = hist(
        [
            BASE,
            (t + 500_000_000, 4000, None),  # ask empty at t + L
            (t + 3 * NS, 4000, 4002),  # ask back at t + 3 s: the long's entry fill
            (t + 15 * MIN + 500_000_000, None, 4006),  # bid empty at t + h + L
            (t + 15 * MIN + 5 * NS, 4004, 4006),
        ]
    )  # bid back: the long's exit fill
    o = lb.simulate_side(h, day(), "FH", 15, t, lb.LONG)
    # long: buy 4002 at t + 3 s (fallback), sell 4004 at t + 15 min + 5 s (fallback): 4004 - 4002 - 0.528
    assert o.made and o.entry_ns == t + 3 * NS and o.exit_ns == t + 15 * MIN + 5 * NS
    assert o.flags == lb.FLAG_ENTRY_FALLBACK | lb.FLAG_EXIT_FALLBACK
    assert o.net == 2.0 - 0.528
    s = lb.simulate_side(h, day(), "FH", 15, t, lb.SHORT)
    # short: sell bid 4000 at t + L (no fallback), buy ask 4006 at t + h + L (ask present): 4000 - 4006 - f
    assert s.made and s.flags == 0 and s.entry_ns == t + NS and s.exit_ns == t + 15 * MIN + NS
    assert s.net == -6.0 - 0.528


def test_entry_not_made_when_no_valid_update_before_planned_exit():
    t = T0
    states = [BASE, (t + 500_000_000, 4000, None)]
    # FH15: the planned exit is t + 15 min; an ask that returns exactly then is too late
    h = hist(states + [(t + 15 * MIN, 4000, 4002)])
    e = lb.entry_fill(h, "FH", 15, t, lb.LONG)
    assert (e.made, e.flags) == (False, lb.FLAG_ENTRY_FALLBACK | lb.FLAG_ENTRY_NOT_MADE)
    o = lb.simulate_side(h, day(), "FH", 15, t, lb.LONG)
    assert (o.made, o.entry_ns, o.exit_ns, math.isnan(o.net)) == (False, -1, -1, True)
    # 1 ns earlier it is made
    h2 = hist(states + [(t + 15 * MIN - 1, 4000, 4002)])
    assert lb.entry_fill(h2, "FH", 15, t, lb.LONG).made
    # TB15: the planned exit is the vertical barrier t + L + 15 min, so t + 15 min still fills
    assert lb.entry_fill(h, "TB", 15, t, lb.LONG).made
    h3 = hist(states + [(t + NS + 15 * MIN, 4000, 4002)])
    assert not lb.entry_fill(h3, "TB", 15, t, lb.LONG).made


def test_exit_limit_mark():
    t = T0
    lim = (4100 * TICK, 3900 * TICK)  # HL 4100, LL 3900 ticks
    h = hist([BASE, (t + 15 * MIN + 500_000_000, None, None)])  # both sides gone until 13:20
    o = lb.simulate_side(h, day(limits=lim), "FH", 15, t, lb.LONG)
    # long exit marked at the low limit: 3900 - 4001 - 0.528
    assert o.flags == lb.FLAG_EXIT_FALLBACK | lb.FLAG_EXIT_LIMIT and o.exit_ns == ct(13, 20)
    assert o.net == -101.0 - 0.528
    s = lb.simulate_side(h, day(limits=lim), "FH", 15, t, lb.SHORT)
    # short exit marked at the high limit: 4000 - 4100 - 0.528
    assert s.flags == lb.FLAG_EXIT_FALLBACK | lb.FLAG_EXIT_LIMIT and s.net == -100.0 - 0.528


def test_exit_fallback_window_ends_before_1320():
    t = T0
    lim = (4100 * TICK, 3900 * TICK)
    h = hist([BASE, (t + 15 * MIN + 500_000_000, None, 4001), (ct(13, 20), 4000, 4001)])
    o = lb.simulate_side(h, day(limits=lim), "FH", 15, t, lb.LONG)
    assert o.flags & lb.FLAG_EXIT_LIMIT  # the bid returns at 13:20:00, not before it
    h2 = hist([BASE, (t + 15 * MIN + 500_000_000, None, 4001), (ct(13, 20) - 1, 4000, 4001)])
    o2 = lb.simulate_side(h2, day(limits=lim), "FH", 15, t, lb.LONG)
    assert o2.flags == lb.FLAG_EXIT_FALLBACK and o2.exit_ns == ct(13, 20) - 1


def test_exit_last_touch_mark_without_limits():
    t = T0
    h = hist(
        [
            BASE,
            (t + 10 * MIN, 4003, 4004),
            (t + 12 * MIN, 4007, 4008, False),  # bad book: its touch is not valid
            (t + 13 * MIN, None, 4008),
        ]
    )  # bid empty from here to 13:20
    o = lb.simulate_side(h, day(limits=None), "FH", 15, t, lb.LONG)
    # last valid bid before the bid emptied or the book went bad: 4003 at t + 10 min; 4003 - 4001 - 0.528
    assert o.flags == lb.FLAG_EXIT_FALLBACK | lb.FLAG_EXIT_LAST_TOUCH and o.net == 2.0 - 0.528
    assert o.exit_ns == ct(13, 20)


# ------------------------------------------------------------------------------------------ FH labels --
def test_fh_up_down_and_dead_zone():
    t = T0
    up = hist([BASE, (t + 500_000_000, 4001, 4002), (t + 15 * MIN + 500_000_000, 4005, 4006)])
    r = lb.label_row(up, "FH", 15, t, None)
    # N_long = 4005 - 4002 - 0.528 = 2.472 > 0; N_short = 4001 - 4006 - 0.528
    assert r.ok and r.y == 1 and r.n_long == 3.0 - 0.528 and r.n_short == -5.0 - 0.528
    assert r.span_end_ns == t + 15 * MIN + NS
    dn = hist([BASE, (t + 15 * MIN + 500_000_000, 3995, 3996)])
    r = lb.label_row(dn, "FH", 15, t, None)
    # N_short = 4000 - 3996 - 0.528 = 3.472 > 0; N_long = 3995 - 4001 - 0.528
    assert r.ok and r.y == -1 and r.n_short == 4.0 - 0.528 and r.n_long == -6.0 - 0.528
    flat = hist([BASE])
    r = lb.label_row(flat, "FH", 15, t, None)
    # dead zone: both -1.528; N_long + N_short = -s - s - 2f = -3.056 < 0
    assert r.ok and r.y == 0 and r.n_long == r.n_short == -1.0 - 0.528
    assert r.n_long + r.n_short < 0
    # a 1-tick move does not clear the spread plus fee: N_long = 4001 - 4001 - 0.528
    small = hist([BASE, (t + 15 * MIN, 4001, 4002)])
    assert lb.label_row(small, "FH", 15, t, None).y == 0


# ------------------------------------------------------------------------------------------ TB labels --
B15 = 2.0 * math.sqrt(15)  # sigma 2.0 ticks, h = 15: b = 7.746 ticks


def test_tb_up_down_vertical():
    t = T0
    # m0 = M(t + L) = 4000.5; up barrier M >= 4008.246; down M <= 3992.754
    up = hist(
        [
            BASE,
            (t + 3 * MIN, 4007, 4009),  # M 4008: not yet
            (t + 5 * MIN, 4008, 4009),  # M 4008.5: up
            (t + 5 * MIN + 500_000_000, 4010, 4011),
        ]
    )  # moves before tau + L
    r = lb.label_row(up, "TB", 15, t, B15)
    # tau = t + 5 min; exit as of tau + L: bid 4010 ask 4011; N_long = 4010 - 4001 - f; N_short = 4000 - 4011 - f
    assert r.ok and r.y == 1 and r.span_end_ns == t + 5 * MIN + NS
    assert r.n_long == 9.0 - 0.528 and r.n_short == -11.0 - 0.528
    dn = hist([BASE, (t + 7 * MIN, 3992, 3993)])  # M 3992.5 <= 3992.754: down
    r = lb.label_row(dn, "TB", 15, t, B15)
    assert r.ok and r.y == -1 and r.span_end_ns == t + 7 * MIN + NS
    assert r.n_short == 4000 - 3993 - 0.528
    vert = hist([BASE, (t + 7 * MIN, 3993, 3994)])  # M 3993.5: inside
    r = lb.label_row(vert, "TB", 15, t, B15)
    # tau = t + L + 15 min; exit as of tau + L = t + 2 s + 15 min
    assert r.ok and r.y == 0 and r.span_end_ns == t + 2 * NS + 15 * MIN
    assert r.n_long == 3993 - 4001 - 0.528


def test_tb_barrier_hit_exactly_at_vertical_and_just_after():
    t = T0
    end = t + NS + 15 * MIN
    at = hist([BASE, (end, 4008, 4009)])
    r = lb.label_row(at, "TB", 15, t, B15)
    assert r.y == 1 and r.span_end_ns == end + NS  # (t + L, t + L + h] is closed on the right
    after = hist([BASE, (end + 1, 4008, 4009)])
    r = lb.label_row(after, "TB", 15, t, B15)
    assert r.y == 0 and r.n_long == 4008 - 4001 - 0.528  # exit as of end + L sees the later update


def test_tb_barrier_ignores_undefined_mids():
    t = T0
    h = hist(
        [
            BASE,
            (t + 2 * MIN, 4020, 4021, False),  # bad book: M undefined, ignored
            (t + 3 * MIN, 4012, 4010),  # crossed (bid >= ask): M undefined, ignored
            (t + 4 * MIN, 4000, 4001),
            (t + 6 * MIN, 3992, 3993),
        ]
    )  # first defined crossing: down
    # the simulated trade (no row rule) sees the down barrier at t + 6 min
    kh, direction = lb.first_barrier(h, h.asof(t + NS), t + NS + 15 * MIN, B15)
    assert (int(h.t[kh]), direction) == (t + 6 * MIN, -1)
    o = lb.simulate_side(h, day(), "TB", 15, t, lb.SHORT)
    assert o.made and o.exit_ns == t + 6 * MIN + NS and o.net == 4000 - 3993 - 0.528
    # the row: the bad-book update lies in the span -> removed by the locked-book row rule
    assert lb.label_row(h, "TB", 15, t, B15).fail == "r5_locked_span"
    # without the bad update the crossed one stays (both sides present, not bad: READING LOCKED-LITERAL)
    h2 = hist(
        [BASE, (t + 3 * MIN, 4012, 4010), (t + 4 * MIN, 4000, 4001), (t + 6 * MIN, 3992, 3993)]
    )
    r = lb.label_row(h2, "TB", 15, t, B15)
    assert r.ok and r.y == -1


def test_one_update_cannot_hit_both_barriers_assertion():
    h = hist([BASE, (T0 + 2 * NS, 4000, 4001)])
    with pytest.raises(lb.LabelError):
        lb.first_barrier(h, 0, T0 + MIN, 0.0)  # b = 0 makes d = 0 hit both: the assertion fires
    with pytest.raises(lb.LabelError):
        lb.barrier_half_width(0.0, 15)
    with pytest.raises(lb.LabelError):
        lb.barrier_half_width(None, 15)


def test_tb_m0_at_entry_fill_update_per_side():
    t = T0
    h = hist(
        [
            BASE,
            (t + 500_000_000, 4000, None),  # ask empty at t + L: M undefined
            (t + 3 * NS, 4004, 4005),  # long's fallback fill: m0 = 4004.5
            (t + 4 * MIN, 4012, 4013),
        ]
    )  # M 4012.5 - 4004.5 = 8 >= 7.746: up for the long
    lo = lb.simulate_side(h, day(), "TB", 15, t, lb.LONG)
    assert lo.made and lo.flags == lb.FLAG_ENTRY_FALLBACK and lo.entry_ns == t + 3 * NS
    assert lo.exit_ns == t + 4 * MIN + NS and lo.net == 4012 - 4005 - 0.528
    # the short sells the bid at t + L (no fallback) but M is undefined at that update: not made (flag 32)
    sh = lb.simulate_side(h, day(), "TB", 15, t, lb.SHORT)
    assert (sh.made, sh.flags) == (False, lb.FLAG_TB_NOT_MADE)
    # had m0 been M(t + L) of the base book (4000.5), the up barrier would have been hit earlier: check not
    h2 = hist(
        [BASE, (t + 500_000_000, 4000, None), (t + 3 * NS, 4004, 4005), (t + 2 * MIN, 4009, 4010)]
    )
    lo2 = lb.simulate_side(h2, day(), "TB", 15, t, lb.LONG)
    assert lo2.exit_ns == t + NS + 15 * MIN + NS  # 4009.5 - 4004.5 = 5 < 7.746: vertical exit


# ------------------------------------------------------------------------------------- P3.6 rules --
def fails(h, h_min=15, t=T0, **kw):
    return lb.entry_rule_fails(h, day(**kw), h_min, t)


def test_rule1_open_and_rule2_close():
    h = hist([(ct(7, 0), 4000, 4001)])
    assert fails(h, t=ct(8, 34))["r1_open"] and not fails(h, t=ct(8, 35))["r1_open"]
    # G_15 ends at 13:12 - 15 = 12:57: span end 12:57 + 15 min + 1 s = 13:12:01 <= 13:13
    assert not fails(h, t=ct(12, 57))["r2_close"]
    assert fails(h, t=ct(12, 58))["r2_close"]  # 13:13:01 > 13:13:00 (off the grid)
    assert lb.grid(15)[-1] == 277 - 15 and len(lb.grid(5)) == 273 and len(lb.grid(60)) == 218


def test_rule3_release_window():
    h = hist([(ct(7, 0), 4000, 4001)])
    rel = (ct(11, 0),)  # R - 2 min = 10:58, R + 30 min = 11:30
    assert not fails(h, t=ct(10, 42), releases=rel)["r3_release"]  # span ends 10:57:01
    assert fails(h, t=ct(10, 43), releases=rel)["r3_release"]  # span ends 10:58:01
    assert fails(h, t=ct(11, 30), releases=rel)["r3_release"]  # starts at R + 30 min (closed)
    assert not fails(h, t=ct(11, 31), releases=rel)["r3_release"]
    assert not fails(h, t=ct(10, 43))["r3_release"]  # no release that day


def test_rule3_release_parse_via_cal33_if_available():
    cal33 = pytest.importorskip("cal33")
    if not hasattr(cal33, "releases"):
        pytest.skip("cal33.releases not written yet")
    try:
        rel = cal33.releases(
            D.replace(month=1, day=12)
        )  # 2023-01-12: USDA WASDE and NASS Crop Production
    except TypeError:
        rel = cal33.releases("2023-01-12")
    eleven = int(datetime(2023, 1, 12, 11, 0, tzinfo=CT).timestamp()) * NS
    assert eleven in list(rel)
    try:
        none = cal33.releases(date(2023, 1, 13))
    except TypeError:
        none = cal33.releases("2023-01-13")
    assert len(list(none)) == 0


def test_rule4_excluded_date_removes_every_row():
    cols, excl = lb.compute_label(None, day(excluded=True), "F15")
    assert not cols["entry_ok"].any() and not cols["row_ok"].any() and not cols["long_made"].any()
    assert excl["rows_removed_first_rule"]["r4_roll_calendar"] == len(lb.grid(15))
    cols, _ = lb.compute_label(hist([BASE]), day(), "F15")
    assert cols["row_ok"].all()


def test_rule5_limit_proximity_and_skip():
    h = hist([(ct(7, 0), 4000, 4001)])  # M = 4000.5 ticks
    # c = (HL + LL)/2; remove when M >= HL - 0.02c or M <= LL + 0.02c
    # HL 4082, LL 3900: c 3991, HL - 0.02c = 4002.18 -> 4000.5 kept; HL 4080: c 3990, 4000.2 -> removed
    assert not fails(h, limits=(4082 * TICK, 3900 * TICK))["r5_limit"]
    assert fails(h, limits=(4080 * TICK, 3900 * TICK))["r5_limit"]
    # LL side: LL 3920, HL 4100: c 4010, LL + 0.02c = 4000.2 -> 4000.5 kept; LL 3921: 4001.22 -> removed
    assert not fails(h, limits=(4100 * TICK, 3920 * TICK))["r5_limit"]
    assert fails(h, limits=(4100 * TICK, 3921 * TICK))["r5_limit"]
    # equality is removed: HL 4081, LL 3919: c 4000, HL - 0.02c = 4001 and M = (4000 + 4002)/2 = 4001
    h2 = hist([(ct(7, 0), 4000, 4002)])
    assert fails(h2, limits=(4081 * TICK, 3919 * TICK))["r5_limit"]
    # skip case: no limits on D
    assert not fails(h, limits=None)["r5_limit"]
    with pytest.raises(ValueError):
        day(limits=(mb.UNDEF_PRICE, 3900 * TICK))


def test_rule5_book_at_t_and_crossed_reading():
    t = T0
    no_ask = hist([(ct(7, 0), 4000, None)])
    assert fails(no_ask)["r5_book_at_t"]
    bad = hist([(ct(7, 0), 4000, 4001, False)])
    assert fails(bad)["r5_book_at_t"]
    ok = hist([(ct(7, 0), 4000, 4001)])
    assert not fails(ok)["r5_book_at_t"]
    # an update at exactly t is known at t (ts_recv <= t)
    late = hist([(ct(7, 0), 4000, None), (t, 4000, 4001)])
    assert not fails(late)["r5_book_at_t"]
    # crossed at t (lead ruling D2): no entry, with or without limits; the limit part is then not evaluated
    crossed = hist([(ct(7, 0), 4002, 4001)])
    with_lim = fails(crossed, limits=(4100 * TICK, 3900 * TICK))
    assert with_lim["r5_book_at_t"] and not with_lim["r5_limit"]
    assert fails(crossed)["r5_book_at_t"]
    # label_row alone (no entry check) still refuses the row: M_ZM(t) undefined (P3.7)
    assert lb.label_row(crossed, "FH", 15, t, None).fail == "p37_mid_t"


def test_rule5_locked_span_row_rule():
    t = T0
    inside = hist([BASE, (t + 15 * MIN + NS, 4000, None), (t + 15 * MIN + 2 * NS, 4000, 4001)])
    assert (
        lb.label_row(inside, "FH", 15, t, None).fail == "r5_locked_span"
    )  # at the span end (closed)
    after = hist([BASE, (t + 15 * MIN + NS + 1, 4000, None), (t + 15 * MIN + 2 * NS, 4000, 4001)])
    assert lb.label_row(after, "FH", 15, t, None).ok
    # TB: realised span [t, tau + L] can end after t + L + h; READING TB-SPAN checks the union
    end = t + NS + 15 * MIN
    tb = hist(
        [BASE, (end, 4008, 4009), (end + 500_000_000, 4008, None), (end + 2 * NS, 4008, 4009)]
    )
    assert (
        lb.label_row(tb, "TB", 15, t, B15).fail == "r5_locked_span"
    )  # bad update in (end, tau + L]
    tb_poss = hist(
        [
            BASE,
            (t + 5 * MIN, 4008, 4009),
            (t + 5 * MIN + 2 * NS, 4008, None),
            (t + 5 * MIN + 3 * NS, 4008, 4009),
        ]
    )
    # tau + L = t + 5 min + 1 s; the bad update at t + 5 min + 2 s is inside [t, t + L + h] -> removed too
    assert lb.label_row(tb_poss, "TB", 15, t, B15).fail == "r5_locked_span"


def test_rule6_zs_zl_have_no_input_here():
    """P3.6 rule 6 keeps rows when ZS or ZL is invalid: the label code takes no ZS/ZL input at all."""
    import inspect

    params = set(inspect.signature(lb.compute_label).parameters)
    assert params == {"hist", "day", "label"}
    assert not any(
        "zs" in f or "zl" in f for f in lb.DayInputs.__dataclass_fields__ if f != "sigma_zm"
    )


def test_entry_ok_versus_row_ok():
    t = T0
    # ask missing between t + 0.5 s and t + 3 s: entry rules hold at t (book good at t) -> entry_ok, the long
    # fills by fallback; the span holds an update without an ask -> not a row
    h = hist([BASE, (t + 500_000_000, 4000, None), (t + 3 * NS, 4000, 4001)])
    cols, excl = lb.compute_label(h, day(), "F15")
    assert cols["entry_ok"][0] and not cols["row_ok"][0]
    assert cols["long_made"][0] and cols["long_flags"][0] == lb.FLAG_ENTRY_FALLBACK
    assert cols["short_made"][0] and cols["short_flags"][0] == 0
    assert math.isnan(cols["n_long"][0]) and cols["y"][0] == 0 and cols["span_end_ns"][0] == -1
    assert math.isnan(cols["w"][0])
    assert excl["rows_removed_first_rule"]["r5_locked_span"] == 1
    assert cols["row_ok"][1:].all()  # minute 1 starts after the gap closed


# ------------------------------------------------------------------------------------------- weights --
def test_interval_set_more_than_one_second():
    base = 1_000_000 * MIN
    assert lb.interval_set(base, base + 15 * MIN + NS) == [
        base // MIN + k for k in range(15)
    ]  # h intervals
    assert lb.interval_set(base, base + MIN + NS + 1) == [
        base // MIN,
        base // MIN + 1,
    ]  # 1 s + 1 ns counts
    assert lb.interval_set(base, base + NS) == []
    assert lb.interval_set(base, base + NS + 1) == [base // MIN]


def test_uniqueness_weights_hand_example():
    base = 1_000_000 * MIN
    starts = [base, base + MIN, base + 2 * MIN, base + 10 * MIN]
    ends = [
        base + 2 * MIN + NS,
        base + 3 * MIN + NS,
        base + 4 * MIN + NS,
        base + 10 * MIN + 30 * NS,
    ]
    # intervals: r0 {0,1}, r1 {1,2}, r2 {2,3}, r3 {10}; c = {0:1, 1:2, 2:2, 3:1, 10:1}
    # u0 = (1 + 1/2)/2 = 0.75; u1 = (1/2 + 1/2)/2 = 0.5; u2 = (1/2 + 1)/2 = 0.75; u3 = 1
    w = lb.uniqueness_weights(starts, ends)
    assert w.tolist() == [0.75, 0.5, 0.75, 1.0]
    # three identical spans of 2 intervals: 1/3 each (raw, no renormalisation)
    w3 = lb.uniqueness_weights([base] * 3, [base + 2 * MIN + NS] * 3)
    assert w3.tolist() == [1 / 3] * 3


def test_weights_in_compute_label_flat_book():
    cols, _ = lb.compute_label(hist([BASE]), day(), "F05")
    w = cols["w"]
    # FH05 rows every minute, each covering 5 intervals; interior interval counts are 5 -> interior u = 0.2;
    # row 0 covers intervals 0..4 with counts 1,2,3,4,5 -> mean(1, 1/2, 1/3, 1/4, 1/5)
    assert w[10] == pytest.approx(0.2, abs=1e-15)
    assert w[0] == pytest.approx((1 + 1 / 2 + 1 / 3 + 1 / 4 + 1 / 5) / 5, abs=1e-15)
    assert w[-1] == w[0]


# --------------------------------------------------------------------------------------- invariants --
def _busy_history():
    rng = np.random.default_rng(5)
    t, b, a, g = [ct(8, 0)], [4000], [4001], [True]
    ts = ct(8, 0)
    mid = 4000
    while ts < ct(13, 19):
        ts += int(rng.integers(200_000_000, 20 * NS))
        mid += int(rng.integers(-2, 3))
        spread = int(rng.integers(1, 3))
        roll = rng.random()
        bid, ask, good = mid, mid + spread, True
        if roll < 0.001:
            ask = lb.NO_PX
        elif roll < 0.0015:
            good = False
        elif roll < 0.002:
            bid = lb.NO_PX
        t.append(ts)
        b.append(bid)
        a.append(ask)
        g.append(good)
    return lb.BookHistory.of(np.array(t), np.array(b), np.array(a), np.array(g))


@pytest.mark.parametrize("label", list(lb.LABELS))
def test_s_net_equals_n_s_where_row_and_no_fallback(label):
    h = _busy_history()
    lim = (4300 * TICK, 3700 * TICK)
    cols, excl = lb.compute_label(h, day(limits=lim, releases=(ct(11, 0),)), label)
    row = cols["row_ok"]
    assert row.any() and (~row & cols["entry_ok"]).any()  # both kinds present
    for s, n in (("long", "n_long"), ("short", "n_short")):
        nofb = row & ((cols[f"{s}_flags"] & 3) == 0)
        assert nofb.sum() == row.sum()  # no fallback can fire inside a kept row
        assert np.array_equal(cols[f"{s}_net"][nofb], cols[n][nofb])
    assert excl["rows_kept"] == int(row.sum())
    assert list(cols) == list(lb.COLUMNS)


def test_check_invariants_catches_a_tampered_net():
    cols, _ = lb.compute_label(hist([BASE]), day(), "F15")
    bad = dict(cols)
    bad["long_net"] = cols["long_net"].copy()
    bad["long_net"][3] += 1.0
    with pytest.raises(lb.LabelError):
        lb.check_invariants(bad)


def test_nets_are_bit_equal_integer_difference_minus_fee():
    t = T0
    h = hist([BASE, (t + 15 * MIN, 4003, 4004)])
    r = lb.label_row(h, "FH", 15, t, None)
    assert r.n_long == float(4003 - 4001) - 0.528
    assert r.n_long.hex() == (2.0 - 0.528).hex()


def test_entry_fill_from_records_lt7_hook():
    tape = Tape()
    tape.snapshot(ct(8, 0), 4000, 4001)
    tape.quote(T0 + 500_000_000, ask=None)  # ask empty at t + L
    tape.quote(T0 + 3 * NS, ask=4002)  # fallback fill update
    tape.quote(T0 + 4 * NS, ask=4009)  # after the fill: must not matter
    rec = tape.records()
    full = lb.entry_fill(lb.replay(rec, 7, TICK), "FH", 15, T0, lb.LONG)
    cut = lb.entry_fill_from_records(rec, 7, TICK, full.fill_ns, "FH", 15, T0, lb.LONG)
    assert (full.made, full.fill_ns, full.price, full.flags) == (True, T0 + 3 * NS, 4002, 1)
    assert (cut.made, cut.fill_ns, cut.price, cut.flags) == (
        full.made,
        full.fill_ns,
        full.price,
        full.flags,
    )


def test_lt2_span_check_counts_a_tampered_row():
    t = T0
    h = hist([BASE, (t + 20 * MIN, 4000, None), (t + 20 * MIN + 2 * NS, 4000, 4001)])
    d = day(releases=(ct(11, 0),))
    cols, excl = lb.compute_label(h, d, "F15")
    assert excl["lt2_span_violations"] == 0
    assert (
        not cols["row_ok"][5] and cols["row_ok"][4]
    )  # t + 5 min: span ends t + 20 min + 1 s (holds the gap)
    bad = {k: v.copy() for k, v in cols.items()}
    bad["row_ok"][5] = True
    bad["span_end_ns"][5] = int(cols["t_ns"][5]) + 15 * MIN + NS
    assert lb.span_violations(bad, h, d, "F15") == 1
    rel = {k: v.copy() for k, v in cols.items()}
    k = int(np.searchsorted(cols["t_ns"], ct(10, 43)))
    assert not cols["row_ok"][k]
    rel["row_ok"][k] = True
    rel["span_end_ns"][k] = ct(10, 43) + 15 * MIN + NS
    assert lb.span_violations(rel, h, d, "F15") == 1


def test_mid_move_column_hand_example():
    t = T0
    h = hist(
        [
            BASE,
            (t + 500_000_000, 4001, 4002),
            (t + NS + 15 * MIN, 4005, 4007),
            (t + NS + 15 * MIN + 1, 4100, 4101),
        ]
    )
    # M(t + L) = (4001 + 4002)/2 = 4001.5; M(t + L + 15 min) = (4005 + 4007)/2 = 4006 (the update stamped exactly
    # t + L + h counts, the one 1 ns later does not): 4006 - 4001.5 = 4.5 ticks
    assert lb.mid_move(h, t, 15) == 4.5
    assert lb.compute_label(h, day(), "F15")[0]["mid_move"][0] == 4.5
    assert lb.compute_label(h, day(), "T15")[0]["mid_move"][0] == 4.5  # TB: the vertical h
    # F05 at t: M(t + L + 5 min) = 4001.5 -> 0.0
    assert lb.compute_label(h, day(), "F05")[0]["mid_move"][0] == 0.0
    # undefined mid at either end -> NaN
    assert math.isnan(lb.mid_move(hist([BASE, (t + NS + 15 * MIN, 4005, None)]), t, 15))
    assert math.isnan(lb.mid_move(hist([BASE, (t + 500_000_000, 4002, 4001)]), t, 15))  # crossed
    assert math.isnan(lb.mid_move(hist([BASE, (t, 4000, 4001, False)]), t, 15))  # bad book
    assert math.isnan(lb.mid_move(hist([(t + 2 * NS, 4000, 4001)]), t, 15))  # no update by t + L
    # every grid minute: filled on a non-row minute too, and on an excluded date when a book is given
    gap = hist([BASE, (t + 500_000_000, 4000, None), (t + 3 * NS, 4000, 4001)])
    cols, _ = lb.compute_label(gap, day(), "F15")
    assert not cols["row_ok"][0] and math.isnan(cols["mid_move"][0])  # M(t + L) undefined
    assert not np.isnan(cols["mid_move"][1:]).any()
    cols_x, _ = lb.compute_label(h, day(excluded=True), "F15")
    assert not cols_x["entry_ok"].any() and cols_x["mid_move"][0] == 4.5
    assert np.isnan(lb.compute_label(None, day(excluded=True), "F15")[0]["mid_move"]).all()


def test_d1_r_record_with_bad_flag_leaves_book_bad_until_next_r():
    """Lead ruling D1: an R record carrying F_MAYBE_BAD_BOOK clears first, then marks the book bad; the book
    update at that state is bad, and only the next R (without the flag) makes the book good again."""
    tape = Tape()
    tape.snapshot(ct(7, 0), 4000, 4001)
    tape.quote(ct(7, 1), bid=4001, flags=mb.F_MAYBE_BAD_BOOK)  # bad from here
    # snapshot whose R carries the flag: cleared, rebuilt, still bad
    tape.rec(ct(7, 2), "R", "N", flags=mb.F_SNAPSHOT | mb.F_MAYBE_BAD_BOOK)
    tape.live = {"B": None, "A": None}
    tape._add(ct(7, 2), "B", 3990, mb.F_SNAPSHOT)
    tape._add(ct(7, 2), "A", 3991, mb.F_SNAPSHOT | mb.F_LAST)
    tape.quote(ct(7, 3), ask=3992)  # a later ordinary update: still bad (no R in between)
    tape.snapshot(ct(7, 4), 3995, 3996)  # a plain R: good again
    h = lb.replay(tape.records(), 7, TICK)
    assert h.t.tolist() == [ct(7, 0), ct(7, 1), ct(7, 2), ct(7, 3), ct(7, 4)]
    assert h.bid.tolist() == [4000, 4001, 3990, 3990, 3995]  # the clear did rebuild the book
    assert h.good.tolist() == [True, False, False, False, True]
    assert h.stats["bad_marks"] == 2  # once before the flagged R, once after it
    # on the decision grid: a minute inside the bad stretch has no entry, a minute after the plain R has one
    d = lb.DayInputs(
        date=D.isoformat(),
        t0_ns=ct(7, 0),
        close_ns=ct(7, 0) + (13 * 60 + 13 - 515) * MIN,
        session_end_ns=ct(7, 0) + (13 * 60 + 20 - 515) * MIN,
        releases=(),
        limits=None,
        tick=TICK,
        excluded=False,
    )
    assert lb.entry_rule_fails(h, d, 5, ct(7, 3))["r5_book_at_t"]
    assert not lb.entry_rule_fails(h, d, 5, ct(7, 5))["r5_book_at_t"]


def test_d2_entry_needs_defined_mid_on_a_date_without_limits():
    """Lead ruling D2: a locked (bid_1 == ask_1) or crossed book at t blocks the entry on every date, including
    one without limit prices; no trade outcome is filled at that minute."""
    t = T0 + 25 * MIN  # grid minute i = 25 (09:00)
    h = hist([BASE, (t - 500_000_000, 4001, 4001), (t + 500_000_000, 4000, 4001)])
    cols, excl = lb.compute_label(h, day(limits=None), "F05")
    assert not cols["entry_ok"][25] and not cols["row_ok"][25]
    assert (
        not cols["long_made"][25]
        and cols["long_flags"][25] == 0
        and math.isnan(cols["long_net"][25])
    )
    assert (
        cols["entry_ok"][24] and cols["entry_ok"][26] and cols["row_ok"][24] and cols["row_ok"][26]
    )
    assert (
        excl["rows_removed_first_rule"]["r5_book_at_t"] == 1
        and excl["book_crossed_or_locked_at_t"] == 1
    )
    assert excl["rows_removed_first_rule"]["p37_mid_t"] == 0
    # the same with limits on D: also blocked, by the same rule
    cols_l, excl_l = lb.compute_label(h, day(limits=(4100 * TICK, 3900 * TICK)), "F05")
    assert not cols_l["entry_ok"][25] and excl_l["rows_removed_first_rule"]["r5_book_at_t"] == 1
