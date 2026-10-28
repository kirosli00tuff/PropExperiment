"""Hand-built cases for implementation B's labels (labB.py), book driver (labB_book.py) and
exclusion calendar (labB_cal.py). Synthetic book updates only, except the release-calendar and
B3-date checks, which read reference data and the program calendar (no market data)."""

from __future__ import annotations

import math
import sys
from datetime import date, time
from pathlib import Path

import numpy as np
import pytest

IMPL = Path(__file__).resolve().parents[1]
if str(IMPL) not in sys.path:
    sys.path.insert(0, str(IMPL))

import labB as lb  # noqa: E402

DAY = date(2023, 3, 15)  # any weekday; only the CT clock matters
T0 = lb.ct_ns(DAY, time(8, 35))
S = lb.NS
MIN = lb.MIN_NS
F = lb.FEE


def upd(rows: list[tuple]) -> lb.Updates:
    """rows: (offset_ns from 08:35, bid or None, ask or None[, bad])."""
    t, b, a, hb, ha, bad = [], [], [], [], [], []
    for r in rows:
        t.append(T0 + r[0])
        b.append(0 if r[1] is None else r[1])
        a.append(0 if r[2] is None else r[2])
        hb.append(r[1] is not None)
        ha.append(r[2] is not None)
        bad.append(bool(r[3]) if len(r) > 3 else False)
    return lb.Updates(np.array(t, dtype=np.int64), np.array(b, dtype=np.int64),
                      np.array(a, dtype=np.int64), np.array(hb), np.array(ha), np.array(bad))


def ctx(**kw) -> lb.DayContext:
    return lb.DayContext(day=DAY, **kw)


def sim(u: lb.Updates, c: lb.DayContext, label: str, offset: int, side: str) -> lb.Fill:
    kind, h = lb.LABELS[label]
    return lb.simulate(u, lb.derive(u), c, kind, h, T0 + offset, side,
                       lb.tb_half_width(c, h) if kind == "TB" else None)


# ------------------------------------------------------------------ grid, clock ----
def test_grid_sizes_match_protocol():
    assert [len(lb.grid(DAY, h)[0]) for h in (5, 15, 30, 60)] == [273, 263, 248, 218]
    i, t = lb.grid(DAY, 60)
    assert t[0] == T0 and t[-1] == lb.ct_ns(DAY, time(12, 12))


def test_ct_clock_is_dst_aware():
    winter = lb.ct_ns(date(2023, 1, 10), time(8, 35))
    summer = lb.ct_ns(date(2023, 7, 11), time(8, 35))
    assert (winter // S) % 86400 == (14 * 3600 + 35 * 60)  # CST = UTC-6
    assert (summer // S) % 86400 == (13 * 3600 + 35 * 60)  # CDT = UTC-5


# ------------------------------------------------------------------ FH prices ----
def fh_book() -> lb.Updates:
    return upd([(-60 * S, 3000, 3001), (S // 2, 3001, 3002), (S, 3002, 3003),
                (S + 1, 3010, 3011), (5 * MIN + S, 3020, 3021), (5 * MIN + S + 1, 3030, 3031)])


def test_exec_prices_use_asof_t_plus_latency_inclusive():
    cols, _ = lb.label_table(fh_book(), ctx(), "F05")
    # i = 0: entry as of 08:35:01 (the update at exactly t + L counts, the one 1 ns later not);
    # exit as of 08:40:01 (same rule).
    assert cols["row_ok"][0]
    assert cols["n_long"][0] == (3020 - 3003) - F
    assert cols["n_short"][0] == (3002 - 3021) - F
    assert cols["y"][0] == 1
    # i = 1: entry as of 08:36:01 -> the 08:35:01+1ns update; exit as of 08:41:01
    assert cols["n_long"][1] == (3030 - 3011) - F
    assert cols["span_end_ns"][0] == T0 + 5 * MIN + S


def test_fh_dead_zone_and_short_label():
    flat = upd([(-60 * S, 3000, 3001), (5 * MIN + S, 3000, 3001)])
    cols, _ = lb.label_table(flat, ctx(), "F05")
    assert cols["y"][0] == 0 and cols["n_long"][0] == -1 - F and cols["n_short"][0] == -1 - F
    down = upd([(-60 * S, 3000, 3001), (5 * MIN, 2990, 2991)])
    cols, _ = lb.label_table(down, ctx(), "F05")
    assert cols["y"][0] == -1 and cols["n_short"][0] == (3000 - 2991) - F
    one_tick = upd([(-60 * S, 3000, 3001), (5 * MIN, 3002, 3003)])  # bid gains exactly 1 tick
    cols, _ = lb.label_table(one_tick, ctx(), "F05")
    assert cols["n_long"][0] == 1 - F and cols["y"][0] == 1


def test_clean_row_simulation_equals_label_exactly():
    cols, _ = lb.label_table(fh_book(), ctx(), "F05")
    rows = cols["row_ok"] & (cols["long_flags"] == 0)
    assert np.array_equal(cols["long_net"][rows], cols["n_long"][rows])
    assert np.array_equal(cols["short_net"][rows], cols["n_short"][rows])
    assert cols["long_entry_ns"][0] == T0 + S and cols["long_exit_ns"][0] == T0 + 5 * MIN + S


# ------------------------------------------------------------------ fallbacks ----
def test_entry_fallback_fills_at_first_valid_update():
    u = upd([(-60 * S, 3000, 3001), (S // 2, 3000, None), (3 * S, 3000, 3004)])
    f = sim(u, ctx(), "F05", 0, "long")
    assert f.made and f.flags == lb.FL_ENTRY_FALLBACK and f.entry_ns == T0 + 3 * S
    assert f.net == (3000 - 3004) - F
    g = sim(u, ctx(), "F05", 0, "short")  # the bid side was there: no fallback
    assert g.made and g.flags == 0 and g.entry_ns == T0 + S
    cols, ex = lb.label_table(u, ctx(), "F05")
    assert cols["entry_ok"][0] and not cols["row_ok"][0]  # rule 5 row part only
    assert ex["removed_first_rule"]["r5_row"] >= 1


def test_entry_fallback_bad_book_counts_as_missing():
    u = upd([(-60 * S, 3000, 3001), (S // 2, 3000, 3001, True), (2 * S, 3000, 3002)])
    f = sim(u, ctx(), "F05", 0, "long")
    assert f.flags == lb.FL_ENTRY_FALLBACK and f.entry_ns == T0 + 2 * S


def test_entry_not_made_when_no_update_before_planned_exit():
    at_exit = upd([(-60 * S, 3000, 3001), (S // 2, 3000, None), (5 * MIN, 3000, 3002)])
    f = sim(at_exit, ctx(), "F05", 0, "long")  # the update at exactly t + h is not "before"
    assert not f.made and f.flags == lb.FL_ENTRY_FALLBACK | lb.FL_ENTRY_NOT_MADE
    assert math.isnan(f.net) and f.entry_ns == -1 and f.exit_ns == -1
    just_before = upd([(-60 * S, 3000, 3001), (S // 2, 3000, None), (5 * MIN - 1, 3000, 3002)])
    assert sim(just_before, ctx(), "F05", 0, "long").made
    tb_before_vertical = upd([(-60 * S, 3000, 3001), (S // 2, 3000, None),
                              (15 * MIN, 3000, 3002)])
    f = sim(tb_before_vertical, ctx(sigma_ticks=1.0), "T15", 0, "long")
    assert f.made  # TB's planned exit is the vertical barrier t + L + h


def test_exit_fallback_then_limit_then_last_touch():
    deadline = lb.ct_ns(DAY, time(13, 20)) - T0
    later = upd([(-60 * S, 3000, 3001), (290 * S, 3015, 3016), (300 * S + S // 2, None, 3016),
                 (305 * S, 3012, 3016)])
    f = sim(later, ctx(), "F05", 0, "long")
    assert f.flags == lb.FL_EXIT_FALLBACK and f.exit_ns == T0 + 305 * S
    assert f.net == (3012 - 3001) - F
    never = upd([(-60 * S, 3000, 3001), (290 * S, 3015, 3016), (300 * S + S // 2, None, 3016),
                 (deadline, 3012, 3016)])  # back exactly at 13:20:00: too late
    lim = sim(never, ctx(limits=(3300, 2700)), "F05", 0, "long")
    assert lim.flags == lb.FL_EXIT_FALLBACK | lb.FL_EXIT_LIMIT
    assert lim.net == (2700 - 3001) - F and lim.exit_ns == T0 + deadline
    short = sim(never, ctx(limits=(3300, 2700)), "F05", 0, "short")
    assert short.flags == 0 and short.net == (3000 - 3016) - F
    touch = sim(never, ctx(), "F05", 0, "long")
    assert touch.flags == lb.FL_EXIT_FALLBACK | lb.FL_EXIT_LAST_TOUCH
    assert touch.net == (3015 - 3001) - F and touch.exit_ns == T0 + deadline


def test_short_exit_limit_uses_high_limit():
    deadline = lb.ct_ns(DAY, time(13, 20)) - T0
    u = upd([(-60 * S, 3000, 3001), (300 * S + S // 2, 3000, None), (deadline + S, 3000, 3001)])
    f = sim(u, ctx(limits=(3300, 2700)), "F05", 0, "short")
    assert f.flags == lb.FL_EXIT_FALLBACK | lb.FL_EXIT_LIMIT and f.net == (3000 - 3300) - F


# ------------------------------------------------------------------ TB ----
def tb_book(second_hit: tuple[int, int]) -> lb.Updates:
    return upd([(-60 * S, 3000, 3001), (100 * S, 3003, 3004), (200 * S, *second_hit),
                (200 * S + S // 2, 3006, 3007), (400 * S, 2990, 2991)])


def test_tb_up_barrier():
    c = ctx(sigma_ticks=1.0)  # b = sqrt(15) = 3.873 ticks; 2b = 7.746 on the 2 x mid axis
    u = tb_book((3004, 3005))  # 2 x mid 6009 - 6001 = 8 >= 7.746 at 200 s; 6 at 100 s is not
    cols, _ = lb.label_table(u, c, "T15")
    assert cols["row_ok"][0] and cols["y"][0] == 1
    assert cols["span_end_ns"][0] == T0 + 201 * S
    assert cols["n_long"][0] == (3006 - 3001) - F and cols["n_short"][0] == (3000 - 3007) - F
    f = sim(u, c, "T15", 0, "long")
    assert f.flags == 0 and f.net == cols["n_long"][0] and f.exit_ns == T0 + 201 * S


def test_tb_down_barrier():
    c = ctx(sigma_ticks=1.0)
    u = upd([(-60 * S, 3000, 3001), (50 * S, 2996, 2997), (51 * S, 2995, 2996)])
    cols, _ = lb.label_table(u, c, "T15")
    # 2 x mid: 6001 -> 5993 (diff -8 <= -7.746) at 50 s
    assert cols["y"][0] == -1 and cols["span_end_ns"][0] == T0 + 51 * S
    assert cols["n_short"][0] == (3000 - 2996) - F


def test_tb_vertical_barrier():
    c = ctx(sigma_ticks=10.0)  # b = 38.7 ticks: nothing reaches it
    u = tb_book((3004, 3005))
    cols, _ = lb.label_table(u, c, "T15")
    assert cols["y"][0] == 0
    assert cols["span_end_ns"][0] == T0 + 15 * MIN + 2 * S  # tau = t + L + h, exit at tau + L
    assert cols["n_long"][0] == (2990 - 3001) - F


def test_tb_barrier_ignores_crossed_and_bad_updates():
    c = ctx(sigma_ticks=1.0)
    crossed = upd([(-60 * S, 3000, 3001), (150 * S, 3010, 3009), (160 * S, 3001, 3002)])
    cols, _ = lb.label_table(crossed, c, "T15")
    assert cols["row_ok"][0] and cols["y"][0] == 0  # the crossed book never triggers
    bad = upd([(-60 * S, 3000, 3001), (150 * S, 3010, 3011, True), (160 * S, 3001, 3002)])
    f = sim(bad, c, "T15", 0, "long")
    assert f.made and f.exit_ns == T0 + 15 * MIN + 2 * S  # vertical


def test_tb_entry_not_made_when_mid_undefined_at_fill_update():
    c = ctx(sigma_ticks=1.0)
    u = upd([(-60 * S, 3000, 3001), (S // 2, 3001, 3001), (5 * S, 3000, 3001)])  # locked
    f = sim(u, c, "T15", 0, "long")
    assert not f.made and f.flags == lb.FL_TB_NOT_MADE
    cols, ex = lb.label_table(u, c, "T15")
    assert cols["entry_ok"][0] and not cols["row_ok"][0]
    assert ex["removed_any_rule"]["label_undef"] >= 1


def test_tb_without_sigma_has_no_entries():
    cols, ex = lb.label_table(tb_book((3004, 3005)), ctx(sigma_ticks=None), "T15")
    assert not cols["entry_ok"].any() and ex["removed_first_rule"]["tb_sigma"] == 263


def test_first_passage_rejects_double_touch_with_zero_width():
    u = upd([(-60 * S, 3000, 3001), (10 * S, 3000, 3001)])
    with pytest.raises(AssertionError):
        lb.first_passage(u, lb.derive(u), 0, 2, 6001, 0.0)


# ------------------------------------------------------------------ P3.6 rules ----
def steady() -> lb.Updates:
    return upd([(-60 * S, 3000, 3001)])


def test_rule3_release_window_boundaries():
    r = lb.ct_ns(DAY, time(11, 0))
    cols, ex = lb.label_table(steady(), ctx(releases_ns=(r,)), "F05")
    i_of = {lb.ct_ns(DAY, time(hh, mm)): k for k, (hh, mm) in
            enumerate((8 + (35 + j) // 60, (35 + j) % 60) for j in range(273))}
    assert cols["entry_ok"][i_of[lb.ct_ns(DAY, time(10, 52))]]
    assert not cols["entry_ok"][i_of[lb.ct_ns(DAY, time(10, 53))]]  # ends 10:58:01
    assert not cols["entry_ok"][i_of[lb.ct_ns(DAY, time(11, 30))]]  # starts at R + 30
    assert cols["entry_ok"][i_of[lb.ct_ns(DAY, time(11, 31))]]
    assert ex["removed_first_rule"]["r3_release"] == 38  # 10:53..11:30


def test_rule4_excluded_date_and_burn_in():
    cols, ex = lb.label_table(steady(), ctx(excluded=True, exclusion_reasons=("roll_day",)),
                              "F15")
    assert not cols["entry_ok"].any() and not cols["row_ok"].any()
    assert ex["removed_first_rule"]["burn_or_excluded"] == 263
    cols, _ = lb.label_table(steady(), ctx(), "F15", burn_in=True)
    assert not cols["entry_ok"].any() and np.isnan(cols["w"]).all()


def test_rule5_limit_proximity_exact_boundaries():
    lim = (1100, 900)  # c = 1000; excluded when M >= 1080 or M <= 920
    for bid, ask, out in ((1079, 1080, False), (1080, 1081, True), (1079, 1081, True),
                          (920, 921, False), (919, 921, True), (919, 920, True)):
        cols, _ = lb.label_table(upd([(-60 * S, bid, ask)]), ctx(limits=lim), "F05")
        assert bool(cols["entry_ok"][0]) is (not out), (bid, ask)


def test_near_limit_matches_float_formula():
    rng = np.random.default_rng(1)
    for _ in range(200):
        hl, ll = int(rng.integers(3000, 5000)), int(rng.integers(1000, 2900))
        s2 = rng.integers(2 * ll - 50, 2 * hl + 50, size=50)
        c = (hl + ll) / 2
        m = s2 / 2
        ref = (m >= hl - 0.02 * c + 1e-9) | (m <= ll + 0.02 * c - 1e-9)
        got = lb.near_limit(s2, (hl, ll))
        exact = np.isclose(m, hl - 0.02 * c) | np.isclose(m, ll + 0.02 * c)
        assert np.array_equal(got[~exact], ref[~exact])


def test_rule5_row_part_locked_halted_book():
    gap = upd([(-60 * S, 3000, 3001), (150 * S, None, 3001), (151 * S, 3000, 3001)])
    cols, _ = lb.label_table(gap, ctx(), "F05")
    # spans [t, t + 5 min + 1 s] that contain 08:37:30 are removed as rows; entries stay
    removed = ~cols["row_ok"][:6]
    assert removed.tolist() == [True, True, True, False, False, False]
    assert cols["entry_ok"][:6].all()


def test_crossed_book_at_t_blocks_entry_and_row():
    cols, ex = lb.label_table(upd([(-60 * S, 3001, 3000)]), ctx(), "F05")
    assert not cols["entry_ok"].any() and ex["removed_first_rule"]["mid_t"] == 273


def test_empty_side_at_t_blocks_entry():
    cols, ex = lb.label_table(upd([(-60 * S, None, 3000)]), ctx(), "F05")
    assert not cols["entry_ok"].any() and ex["removed_first_rule"]["book_t"] == 273


# ------------------------------------------------------------------ weights ----
def brute_weights(t: np.ndarray, end: np.ndarray) -> np.ndarray:
    slots = [(T0 + m * MIN, T0 + (m + 1) * MIN) for m in range(lb.N_MINUTE_SLOTS)]
    cover = [[m for m, (a, b) in enumerate(slots) if min(e, b) - max(s, a) > S]
             for s, e in zip(t.tolist(), end.tolist(), strict=True)]
    c = np.zeros(len(slots))
    for ms in cover:
        for m in ms:
            c[m] += 1
    return np.array([sum(1.0 / c[m] for m in ms) / len(ms) for ms in cover])


def test_intervals_covered_more_than_one_second():
    t = np.array([T0] * 5)
    end = T0 + np.array([5 * MIN + S, 61 * S, 61 * S + S // 2, 62 * S, 120 * S + S])
    assert lb.intervals_covered(t, end).tolist() == [5, 1, 2, 2, 2]


def test_fh_weights_match_brute_force():
    cols, _ = lb.label_table(steady(), ctx(), "F05")
    rows = cols["row_ok"]
    assert rows.all()
    ref = brute_weights(cols["t_ns"][rows], cols["span_end_ns"][rows])
    assert np.allclose(cols["w"][rows], ref, rtol=1e-15, atol=0)
    assert cols["w"][0] == pytest.approx((1 + 1 / 2 + 1 / 3 + 1 / 4 + 1 / 5) / 5)


def test_tb_weights_use_realised_spans():
    c = ctx(sigma_ticks=1.0)
    u = upd([(-60 * S, 3000, 3001), (100 * S + 7, 3004, 3005), (500 * S, 3000, 3001)])
    cols, _ = lb.label_table(u, c, "T15")
    rows = cols["row_ok"]
    ref = brute_weights(cols["t_ns"][rows], cols["span_end_ns"][rows])
    assert np.allclose(cols["w"][rows], ref, rtol=1e-15, atol=0)
    assert cols["span_end_ns"][0] == T0 + 101 * S + 7


def test_weights_count_rows_only():
    gap = upd([(-60 * S, 3000, 3001), (600 * S, None, 3001), (601 * S, 3000, 3001)])
    cols, _ = lb.label_table(gap, ctx(), "F05")
    rows = cols["row_ok"]
    assert not rows.all()
    ref = brute_weights(cols["t_ns"][rows], cols["span_end_ns"][rows])
    assert np.allclose(cols["w"][rows], ref, rtol=1e-15, atol=0)
    assert np.isnan(cols["w"][~rows]).all() and (cols["span_end_ns"][~rows] == -1).all()


# ------------------------------------------------------------------ schema ----
def test_columns_and_dtypes():
    cols, _ = lb.label_table(fh_book(), ctx(), "F30")
    assert tuple(cols) == lb.COLUMNS
    assert cols["i"].dtype == np.int16 and cols["y"].dtype == np.int8
    assert cols["long_flags"].dtype == np.int16 and cols["span_end_ns"].dtype == np.int64
    assert all(len(v) == 248 for v in cols.values())
    assert not cols["long_made"][~cols["entry_ok"]].any()


def test_updates_must_be_in_ts_recv_order():
    with pytest.raises(ValueError):
        upd([(10 * S, 3000, 3001), (5 * S, 3000, 3001)])


# ------------------------------------------------------------------ book driver ----
def test_book_driver_updates_bad_flag_and_start():
    import labB_book as bk
    import mbo_book31 as mb
    tick = 100_000_000
    rows = []

    def rec(ts, act, side, px, oid, fl, size=1):
        rows.append((T0 + ts, T0 + ts, 7, oid, px * tick, size, fl, ord(act), ord(side), 0))

    L_, SN, BAD = mb.F_LAST, mb.F_SNAPSHOT, mb.F_MAYBE_BAD_BOOK
    rec(1, "A", "B", 2999, 99, L_)  # before any R: not applied, update invalid
    rec(2, "R", "N", 0, 0, SN)
    rec(3, "A", "B", 3000, 1, SN)
    rec(4, "A", "A", 3001, 2, SN | L_)
    rec(5, "A", "B", 3001, 3, L_)  # locked
    rec(6, "C", "B", 3001, 3, L_)
    rec(7, "M", "A", 3002, 2, L_)
    rec(8, "T", "A", 3002, 0, 0)
    rec(8, "F", "A", 3002, 2, L_)
    rec(9, "A", "B", 2998, 4, BAD | L_)
    rec(10, "A", "B", 2997, 5, L_)
    rec(11, "R", "N", 0, 0, 0)
    rec(12, "A", "B", 2990, 6, 0)
    rec(12, "A", "A", 2991, 7, L_)
    rec(13, "A", "A", 3500, 8, 0)  # not F_LAST: no update row
    from measure31 import MBO_COMPACT
    arr = np.array(rows, dtype=MBO_COMPACT)
    other = arr.copy()
    other["instrument_id"] = 8
    u, counts = bk.front_updates(np.concatenate([arr, other]), 7, tick)
    assert counts["records"] == len(rows) and counts["before_start"] == 1
    assert u.t.tolist() == [T0 + x for x in (1, 4, 5, 6, 7, 8, 9, 10, 12)]
    assert u.bid.tolist() == [0, 3000, 3001, 3000, 3000, 3000, 3000, 3000, 2990]
    assert u.ask.tolist() == [0, 3001, 3001, 3001, 3002, 3002, 3002, 3002, 2991]
    assert u.bad.tolist() == [True, False, False, False, False, False, True, True, False]
    d = lb.derive(u)
    assert d.mid_ok.tolist() == [False, True, False, True, True, True, False, False, True]


def test_sigma_pools_valid_changes_population_sd():
    import labB_book as bk
    s2a = np.array([6000, 6002, 6002, 6006], dtype=np.int64)
    va = np.array([True, True, False, True])
    s2b = np.array([6000, 5998], dtype=np.int64)
    vb = np.array([True, True])
    got = bk.sigma_from_mids([(s2a, va), (s2b, vb)])
    assert got == pytest.approx(float(np.std([1.0, -1.0], ddof=0)))
    assert bk.sigma_from_mids([(s2a[:1], va[:1])]) is None


# ------------------------------------------------------------------ calendar ----
def test_release_calendar_counts_and_b3_dates():
    import labB_cal as cal
    rel, found = cal.releases()
    assert found["NOPA rule dates"] == 2 and found["USDA WASDE"] == 39
    assert found["nopa_rule_dates"] == ["2022-11-15", "2022-12-15"]
    assert lb.ct_ns(date(2022, 11, 15), time(11, 0)) in rel[date(2022, 11, 15)]
    b3 = cal.b3_dates()
    assert len(b3) == 20 and b3[0] == date(2021, 1, 19) and b3[-1] == date(2024, 2, 15)
