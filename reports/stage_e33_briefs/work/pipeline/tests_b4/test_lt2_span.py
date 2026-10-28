"""Unit tests of LT2's span rule (tests_b4/lt2_span.py) after ruling R-L10: a TB row is checked over every span the
label can have, [t, t + 2L + h], whatever its realised tau; an FH row over [t, t + L + h]. Hand-built book and a
stub calendar (no market data, no label values)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lt2_span as lt  # noqa: E402

NS, L, MIN = lt.NS, lt.L, lt.MIN
DAY0 = 1_700_000_000 * NS  # the stub calendar's midnight (any epoch works: the stub defines every time)
HHMM = {"08:35:00": 8 * 3600 + 35 * 60, "13:13:00": 13 * 3600 + 13 * 60}


def _ct(hh: int, mm: int, ss: float = 0.0) -> int:
    return DAY0 + int(round((hh * 3600 + mm * 60 + ss) * NS))


@pytest.fixture()
def stub_cal(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    releases: list[int] = []
    cal = SimpleNamespace(ct_ns=lambda _d, s: DAY0 + HHMM[s] * NS, excluded=lambda _d: (False, ""),
                          releases=lambda _d: list(releases), limits=lambda _d: None, tick=lambda _r: 1)
    monkeypatch.setattr(lt, "cal33", cal)
    return releases


def _book(bad_at: list[int]) -> dict:
    """One book side: two-sided valid updates every second 08:30-13:20, plus a bad (one-sided) update at each
    bad_at time."""
    good = np.arange(_ct(8, 30), _ct(13, 20), NS, dtype=np.int64)
    t = np.sort(np.concatenate([good, np.asarray(bad_at, dtype=np.int64)]))
    ok = ~np.isin(t, np.asarray(bad_at, dtype=np.int64))
    bid = np.full(len(t), 100, dtype=np.int64)
    ask = np.where(ok, 101, -1).astype(np.int64)
    return {"X": {"pre": lt._bad_prefix(t, ok), "t": t, "bid": bid, "ask": ask, "ok": ok}}


def _row(t: int, end: int) -> pd.DataFrame:
    i = (t - _ct(8, 35)) // MIN
    return pd.DataFrame({"i": [int(i)], "t_ns": [t], "row_ok": [True], "span_end_ns": [end]})


def test_span_hi_tb_is_t_plus_2l_plus_h_whatever_tau() -> None:
    t = _ct(10, 0)
    early_end = t + L + 5 * NS  # tau = t + 5 s, exit at tau + L
    assert lt.span_hi("T15", t, early_end) == t + 2 * L + 15 * MIN
    assert lt.span_hi("T30", t, t + 2 * L + 30 * MIN) == t + 2 * L + 30 * MIN
    assert lt.span_hi("F15", t, t + L + 15 * MIN) == t + L + 15 * MIN


def test_tb_row_with_early_tau_is_checked_to_t_plus_2l_plus_h(stub_cal: list[int]) -> None:
    t = _ct(10, 0)
    early_end = t + L + 5 * NS
    inside = t + L + 15 * MIN + NS // 2  # after t + L + h (the old union reading's end), before t + 2L + h
    v = lt.check_table(_row(t, early_end), "T15", "d", _book([inside]), "X")
    assert v["book_side_or_bad_in_span"] == 1
    assert v["tb_end_range"] == 0


def test_tb_bad_update_just_after_the_possible_span_is_not_counted(stub_cal: list[int]) -> None:
    t = _ct(10, 0)
    after = t + 2 * L + 15 * MIN + 1
    v = lt.check_table(_row(t, t + L + 5 * NS), "T15", "d", _book([after]), "X")
    assert v["book_side_or_bad_in_span"] == 0
    assert sum(v.values()) == 0


def test_fh_span_ends_at_t_plus_l_plus_h(stub_cal: list[int]) -> None:
    t = _ct(10, 0)
    end = t + L + 15 * MIN
    assert lt.check_table(_row(t, end), "F15", "d", _book([end]), "X")["book_side_or_bad_in_span"] == 1
    assert lt.check_table(_row(t, end), "F15", "d", _book([end + 1]), "X")["book_side_or_bad_in_span"] == 0


def test_tb_close_rule_uses_the_whole_possible_span(stub_cal: list[int]) -> None:
    t = _ct(12, 57, 59)  # t + L + h = 13:13:00 (allowed); t + 2L + h = 13:13:01 (past the close)
    v = lt.check_table(_row(t, t + L + 5 * NS), "T15", "d", _book([]), "X")
    assert v["close_1313"] == 1
    v_fh = lt.check_table(_row(t, t + L + 15 * MIN), "F15", "d", _book([]), "X")
    assert v_fh["close_1313"] == 0


def test_tb_release_rule_uses_the_whole_possible_span(stub_cal: list[int]) -> None:
    r = _ct(11, 0)
    stub_cal.append(r)
    t = r - 2 * MIN - 2 * L - 15 * MIN  # t + 2L + h = R - 2 min exactly: intersects the window
    v = lt.check_table(_row(t, t + L + 5 * NS), "T15", "d", _book([]), "X")
    assert v["release_window"] == 1
    v_clear = lt.check_table(_row(t - 1, t - 1 + L + 5 * NS), "T15", "d", _book([]), "X")
    assert v_clear["release_window"] == 0
