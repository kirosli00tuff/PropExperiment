"""B4 LT4 (clock) and record-level known-answer label cases, run through BOTH label implementations (Coder-A
pipeline/lab33.py and Coder-B implB/labB*.py) on hand-built ZM MBO streams. Every expected value is worked out by
hand in the comments from protocol P3.2-P3.7 (f = 0.528 ticks, L = 1 s). Synthetic data only.

Latent label differences found in B3 (B3_agreement.md D1, D2, D5) are tested against the lead's rulings
(reports/stage_e33_protocol_readings.md, "B3 rulings", 02:47 PDT 2026-10-28): D1 and D2 now as agreement tests with
the ruled behaviour on both sides; D5 (no effect on the data) stays documented."""

from __future__ import annotations

import math
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
for _p in (str(HERE), str(HERE.parent / "tests_b3")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import synth_labels as sl  # noqa: E402  (puts pipeline/ and implB/ on sys.path)
import lab33  # noqa: E402
from hb_streams import D, HB, IID, at  # noqa: E402
from synth_streams import F_BAD, NS, SB  # noqa: E402

F = 0.528
L = NS
IMPLS = ("A", "B")


def run(arr: np.ndarray, impl: str, labels: tuple[str, ...], **ctx) -> dict:
    c = sl.SynthCtx(day=ctx.pop("day", D), iid=IID, **ctx)
    return (sl.run_a if impl == "A" else sl.run_b)(arr, c, labels)


def row(df, i: int) -> dict:
    r = df[df["i"] == i]
    assert len(r) == 1
    return {k: r.iloc[0][k] for k in df.columns}


def eqf(a: float, b: float) -> bool:
    return (math.isnan(a) and math.isnan(b)) or a == b


# ---------------------------------------------------------------- LT4: ts_recv clock --
def lt4_stream() -> np.ndarray:
    hb = HB().snapshot(at(8, 0), 1000, 1001)
    # E2: ts_recv 08:35:00.9 <= t + L, ts_event 08:35:02 (ts_recv < ts_event): visible at t + L by ts_recv
    hb.touch(at(8, 35, 0.9), None, 1002, te=at(8, 35, 2.0), keep=(SB,))  # keep the bid
    # E1: ts_recv 1 ns after t + L, ts_event 08:35:00.5 (before t + L): NOT visible at t + L by ts_recv
    hb.touch(at(8, 35, 1.0) + 1, None, 1003, te=at(8, 35, 0.5), keep=(SB,))
    # E3: ts_recv exactly 08:40:01 (= t + h + L for i = 0, h = 5): visible (ts_recv <= u)
    hb.touch(at(8, 40, 1.0), 1006, 1007, te=at(8, 40, 1.5))
    # E4: 1 ns later: not visible at 08:40:01
    hb.touch(at(8, 40, 1.0) + 1, 1010, 1011)
    return hb.build()


@pytest.mark.parametrize("impl", IMPLS)
def test_lt4_fh_prices_by_ts_recv(impl: str) -> None:
    out = run(lt4_stream(), impl, ("F05",))["F05"]
    r0 = row(out, 0)  # t = 08:35: ask(t+L) = 1002 (E2), bid(t+L) = 1000; bid/ask(t+h+L) = 1006/1007 (E3, not E4)
    assert r0["row_ok"] and r0["entry_ok"]
    assert r0["n_long"] == 1006 - 1002 - F and r0["n_short"] == 1000 - 1007 - F and r0["y"] == 1
    assert r0["t_ns"] == at(8, 35) and r0["span_end_ns"] == at(8, 40, 1.0)
    assert r0["long_entry_ns"] == at(8, 35, 1.0) and r0["long_exit_ns"] == at(8, 40, 1.0)
    assert r0["long_net"] == r0["n_long"] and r0["short_net"] == r0["n_short"]
    assert r0["long_flags"] == 0 and r0["short_flags"] == 0
    r1 = row(out, 1)  # t = 08:36: as of 08:36:01 bid 1000 / ask 1003 (E1); exit as of 08:41:01: 1010 / 1011 (E4)
    assert r1["n_long"] == 1010 - 1003 - F and r1["n_short"] == 1000 - 1011 - F and r1["y"] == 1
    r5 = row(out, 5)  # t = 08:40: as of 08:40:01: 1006 / 1007 (E3 at exactly 08:40:01; E4 1 ns later is not)
    assert r5["n_long"] == 1010 - 1007 - F and r5["n_short"] == 1006 - 1011 - F


@pytest.mark.parametrize("impl", IMPLS)
@pytest.mark.parametrize("day", [date(2023, 3, 15), date(2023, 1, 10), date(2023, 3, 13)])
def test_lt4_label_starts_are_ct_minute_marks(impl: str, day: date) -> None:
    """t_ns = 08:35:00 CT + i minutes on D in UTC ns (DST-aware: CST, CDT, the Monday after the change)."""
    hb = HB(day=day).snapshot(at(8, 0, day=day), 1000, 1001)
    for lab, h in (("F05", 5), ("F60", 60), ("T30", 30)):
        out = run(hb.build(), impl, (lab,), day=day)[lab]
        assert list(out["i"]) == list(range(0, 278 - h))
        assert list(out["t_ns"]) == [at(8, 35, day=day) + k * 60 * NS for k in range(0, 278 - h)]


def test_lt4_replay_orders_by_ts_recv_not_ts_event() -> None:
    """A stream handed over in ts_event order is replayed in ts_recv order (A's replay sorts stably); the
    loader (data33) does the same before either implementation sees the records."""
    import data33

    arr = lt4_stream()
    shuffled = arr[np.argsort(arr["ts_event"], kind="stable")]
    assert not np.array_equal(shuffled["ts_recv"], np.sort(shuffled["ts_recv"]))
    h1 = lab33.replay(arr, IID, sl.TICK_FP["ZM"])
    h2 = lab33.replay(shuffled, IID, sl.TICK_FP["ZM"])
    assert np.array_equal(h1.t, h2.t) and np.array_equal(h1.bid, h2.bid) and np.array_equal(h1.ask, h2.ask)
    fixed = data33._in_ts_recv_order(shuffled, "ZM", D)
    assert np.array_equal(fixed["ts_recv"], np.sort(arr["ts_recv"]))
    # the ts_recv < ts_event record keeps its place by ts_recv
    neg = np.flatnonzero(fixed["ts_recv"] < fixed["ts_event"])
    assert len(neg) >= 1 and np.all(np.diff(fixed["ts_recv"]) >= 0)


def test_lt4_truncate_is_ts_recv_inclusive() -> None:
    import data33

    arr = lt4_stream()
    cut = at(8, 35, 1.0)
    t = data33.truncate(arr, cut)
    assert int(t["ts_recv"].max()) <= cut and len(t) == int((arr["ts_recv"] <= cut).sum())
    # E2 (ts_recv < ts_event, ts_event after the cut) is kept; E1 (ts_event before the cut) is dropped
    assert bool(np.any(t["ts_event"] > cut)) and not bool(np.any(t["ts_recv"] == cut + 1))


# ---------------------------------------------------------------- TB --
def tb_stream() -> np.ndarray:
    hb = HB().snapshot(at(8, 0), 1000, 1001)  # m0 = M(08:35:01) = 1000.5
    hb.touch(at(8, 36), 1002, 1003)  # mid 1002.5: below m0 + b = 1003.1
    hb.touch(at(8, 37), 1002, 1004)  # mid 1003.0: below 1003.1
    hb.touch(at(8, 38, 0.25), 1003, 1004, te=at(8, 38, 0.9))  # mid 1003.5: up barrier, tau = 08:38:00.25
    hb.touch(at(8, 38, 1.0), 1004, 1005)  # state as of tau + L = 08:38:01.25
    hb.touch(at(8, 38, 1.25) + 1, 990, 991)  # 1 ns after tau + L: not used
    return hb.build()


@pytest.mark.parametrize("impl", IMPLS)
def test_tb_up_barrier_known_answer(impl: str) -> None:
    sigma = 2.6 / math.sqrt(15)  # b = sigma sqrt(15) = 2.6 ticks (up to rounding; no tie at 0.5-tick mids)
    out = run(tb_stream(), impl, ("T15",), sigma_ticks=sigma)["T15"]
    r = row(out, 0)
    assert r["row_ok"] and r["y"] == 1
    assert r["n_long"] == 1004 - 1001 - F and r["n_short"] == 1000 - 1005 - F
    assert r["span_end_ns"] == at(8, 38, 1.25)
    assert r["long_exit_ns"] == at(8, 38, 1.25) and r["short_exit_ns"] == at(8, 38, 1.25)
    assert r["long_net"] == r["n_long"] and r["short_net"] == r["n_short"]


# ---------------------------------------------------------------- P3.2 fallback and marks --
def fallback_stream() -> np.ndarray:
    hb = HB().snapshot(at(8, 0), 1000, 1001)
    hb.touch(at(8, 35, 0.5), None, None, keep=(SB,))  # ask side empty from 08:35:00.5
    hb.touch(at(8, 35, 3.0), None, 1002, keep=(SB,))  # ask back at 08:35:03
    hb.touch(at(8, 39), 1005, 1006)
    return hb.build()


@pytest.mark.parametrize("impl", IMPLS)
def test_entry_fallback_known_answer(impl: str) -> None:
    out = run(fallback_stream(), impl, ("F05",))["F05"]
    r = row(out, 0)
    # entry rule at t = 08:35:00: both sides present -> entry_ok; the span holds an update without an ask -> no row
    assert r["entry_ok"] and not r["row_ok"] and r["y"] == 0
    assert math.isnan(r["n_long"]) and math.isnan(r["w"]) and r["span_end_ns"] == -1
    # long: ask empty at 08:35:01 -> fills at the first later update with an ask: 1002 at 08:35:03 (flag 1);
    # exit sells bid as of 08:40:01 = 1005
    assert r["long_made"] and r["long_entry_ns"] == at(8, 35, 3.0) and r["long_flags"] == 1
    assert r["long_net"] == 1005 - 1002 - F and r["long_exit_ns"] == at(8, 40, 1.0)
    # short: sells bid 1000 at 08:35:01, buys ask 1006 at 08:40:01
    assert r["short_made"] and r["short_flags"] == 0 and r["short_net"] == 1000 - 1006 - F


def mark_stream() -> np.ndarray:
    hb = HB().snapshot(at(8, 0), 1000, 1001)
    hb.touch(at(12, 55, 0.5), None, None, keep=(SB,))  # ask empty from 12:55:00.5 to the end
    return hb.build()


@pytest.mark.parametrize("impl", IMPLS)
@pytest.mark.parametrize("limits,net,flags", [((1100, 900), 1000 - 1100 - F, 2 | 4), (None, 1000 - 1001 - F, 2 | 8)])
def test_exit_mark_known_answer(impl: str, limits, net: float, flags: int) -> None:
    out = run(mark_stream(), impl, ("F05",), limits_ticks=limits)["F05"]
    r = row(out, 255)  # t = 12:50; short exit buys the ask at 12:55:01: empty until 13:20 -> marked
    assert r["entry_ok"] and not r["row_ok"]
    assert r["short_made"] and r["short_net"] == net and r["short_flags"] == flags
    assert r["short_exit_ns"] == at(13, 20)
    assert r["long_net"] == 1000 - 1001 - F and r["long_flags"] == 0
    assert not row(out, 261)["entry_ok"]  # t = 12:56: the book at t has no ask


# ---------------------------------------------------------------- P3.6 rules 3, 4, 5 --
@pytest.mark.parametrize("impl", IMPLS)
def test_release_window_closed_edges(impl: str) -> None:
    arr = HB().snapshot(at(8, 0), 1000, 1001).build()
    out = run(arr, impl, ("F05", "F60"), releases_ns=(at(11, 0),))
    # F05: span [t, t + 5 min + 1 s] meets [10:58, 11:30] for t in 10:53 .. 11:30 -> i 138 .. 175
    bad = set(range(138, 176))
    assert {int(i) for i, e in zip(out["F05"]["i"], out["F05"]["entry_ok"]) if not e} == bad
    # F60: t + 60 min + 1 s >= 10:58 from t = 09:58 (i 83) .. 11:30 (i 175)
    assert {int(i) for i, e in zip(out["F60"]["i"], out["F60"]["entry_ok"]) if not e} == set(range(83, 176))


@pytest.mark.parametrize("impl", IMPLS)
def test_excluded_date_all_false(impl: str) -> None:
    arr = HB().snapshot(at(8, 0), 1000, 1001).build()
    for lab, df in run(arr, impl, ("F15", "T30"), excluded=True).items():
        assert not df["entry_ok"].any() and not df["row_ok"].any() and (df["y"] == 0).all()
        assert not df["long_made"].any() and not df["short_made"].any(), lab


@pytest.mark.parametrize("impl", IMPLS)
def test_limit_proximity(impl: str) -> None:
    hb = HB().snapshot(at(8, 0), 1000, 1001)
    hb.touch(at(9, 0, 0.5), 1020, 1021)  # mid 1020.5 >= HL - 0.02 c = 1040 - 20 = 1020
    hb.touch(at(9, 10, 0.5), 1019, 1020)  # mid 1019.5 < 1020
    out = run(hb.build(), impl, ("F05",), limits_ticks=(1040, 960))["F05"]
    assert {int(i) for i, e in zip(out["i"], out["entry_ok"]) if not e} == set(range(26, 36))  # 09:01 .. 09:10


# ---------------------------------------------------------------- latent A/B differences --
def _agree(arr: np.ndarray, labels: tuple[str, ...], **ctx) -> bool:
    import compare_b3 as cb

    a, b = run(arr, "A", labels, **ctx), run(arr, "B", labels, **ctx)
    rules = {c: ("weight" if c == "w" else "exact") for c in cb.LABEL_COLS}
    return all(cb.compare_frames(a[x], b[x], rules)[0].rows_with_mismatch == 0 for x in labels)



def test_d1_bad_flag_on_clear_agrees() -> None:
    hb = HB().snapshot(at(8, 0), 1000, 1001).flag_bad(at(9, 0)).snapshot(at(9, 30), 1000, 1001, flags_r=F_BAD)
    assert _agree(hb.build(), ("F05", "T15"))


@pytest.mark.parametrize("impl", IMPLS)
def test_d1_ruled_behaviour(impl: str) -> None:
    """R-B3-D1: an R record carrying F_MAYBE_BAD_BOOK leaves the book bad until the next R."""
    hb = HB().snapshot(at(8, 0), 1000, 1001).flag_bad(at(9, 0)).snapshot(at(9, 30), 1000, 1001, flags_r=F_BAD)
    out = run(hb.build(), impl, ("F05",))["F05"]
    assert not row(out, 65)["entry_ok"]  # 09:40: still bad after the flagged R
    assert not row(out, 30)["entry_ok"]  # 09:05: bad
    assert row(out, 20)["entry_ok"]  # 08:55: before the flag


def locked_stream() -> np.ndarray:
    hb = HB().snapshot(at(8, 0), 1000, 1001)
    hb.touch(at(8, 59, 59.5), 1001, 1001)  # locked book as of t = 09:00 (i 25)
    hb.touch(at(9, 0, 0.5), 1000, 1001)
    return hb.build()


def test_d2_locked_at_t_no_limits_agrees() -> None:
    assert _agree(locked_stream(), ("F05", "T15"), limits_ticks=None)


def test_d2_agree_when_limits_exist() -> None:
    assert _agree(locked_stream(), ("F05", "T15"), limits_ticks=(1100, 900))


@pytest.mark.parametrize("impl", IMPLS)
def test_d2_ruled_behaviour(impl: str) -> None:
    """R-B3-D2: entry_ok requires M_ZM(t) defined, with or without limit prices."""
    for lim in (None, (1100, 900)):
        r = row(run(locked_stream(), impl, ("F05",), limits_ticks=lim)["F05"], 25)
        assert not r["entry_ok"] and not r["row_ok"]


def test_d5_tb_sigma_undefined_documented() -> None:
    """D5: sigma_ZM(D) undefined on a non-excluded date: A stops (LabelError, TB-SIGMA), B removes every TB row and
    entry (LB-8). Not reached on OOF dates when sigma is defined there."""
    arr = HB().snapshot(at(8, 0), 1000, 1001).build()
    with pytest.raises(lab33.LabelError):
        run(arr, "A", ("T15",), sigma_ticks=None)
    b = run(arr, "B", ("T15",), sigma_ticks=None)["T15"]
    assert not b["entry_ok"].any() and not b["row_ok"].any()
