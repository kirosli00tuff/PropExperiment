"""E22-F2 positions (prereg section 4): same rule as E22-F1, cap, buffer, granularity."""

import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from forward import core, strategy_f2
from forward.etf_bars import EtfBar
from forward.strategy import instrument_state

ROOT = Path(__file__).resolve().parents[1]
F1 = json.loads((ROOT / "forward/config_f1.json").read_text())
F2 = strategy_f2.load_config()
ETFS = F2["instruments_order"]


def synthetic_rows(n=320, seed=7, start=date(2025, 1, 2)):
    rng = np.random.RandomState(seed)
    days, d = [], start
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    rows, prev = [], {}
    base = {s: 20.0 + 10 * k for k, s in enumerate(ETFS)}
    price = dict(base)
    for k, day in enumerate(days):
        bars = {}
        for j, s in enumerate(ETFS):
            r = 0.0005 * (j - 5) + 0.01 * rng.standard_normal()
            if k == 0:
                bars[s] = EtfBar(price[s])
            else:
                price[s] = price[s] * (1 + r)
                bars[s] = EtfBar(round(price[s], 4), r, prev[s])
            prev[s] = day
        rows.append((day, bars))
    return rows


def test_back_adjusted_latest_equals_raw_and_divides_back():
    adj = strategy_f2.back_adjusted([100.0, 50.5, 51.0], [None, 0.01, 51.0 / 50.5 - 1])
    assert adj[-1] == 51.0
    assert adj[1] == pytest.approx(50.5)
    assert adj[0] == pytest.approx(50.5 / 1.01)  # a 2:1 split inside r(1): no jump


def test_rule_equals_e22_f1_before_the_cap():
    rows = synthetic_rows()
    frames = strategy_f2.frames_from_history(rows, ETFS)
    micros = F2["idm"]["e22_f1_instruments"]
    pairs = zip(ETFS, micros, strict=True)
    f1_states = {m: instrument_state(frames[s], F1["instruments"][m], F1) for s, m in pairs}
    live12 = np.array([m in f1_states and f1_states[m]["live"] for m in F1["instruments_order"]])
    idm_f1 = core.idm_for_live(np.asarray(F1["idm"]["correlation"]), live12, 2.5)
    dec = strategy_f2.decide(rows, {}, F2)
    assert dec.exposure["idm"] == pytest.approx(idm_f1, rel=1e-15)
    assert dec.exposure["n_live"] == 11
    for s, m in zip(ETFS, micros, strict=True):
        st = f1_states[m]
        sig = dec.signals[s]
        assert sig["F"] == st["F"]  # same forecast
        n_f1 = core.unrounded_position(st["F"], 25000.0, 0.2, idm_f1, 1 / 11, st["V"])
        mult = F1["instruments"][m]["multiplier"]
        # same unrounded target per unit of dollar vol: n x V equal
        assert sig["n_unrounded"] * sig["V"] == pytest.approx(float(n_f1) * st["V"], rel=1e-12)
        assert sig["V"] == pytest.approx(st["V"] / mult, rel=1e-12)


def test_cap_not_binding_and_binding_proportional():
    syms = ["A", "B"]
    kw = dict(cap_usd=50000.0, buffer_size=0.1, steps=1000)
    res = strategy_f2.position_steps(
        syms,
        {"A": 10.0, "B": -5.0},
        {"A": 10.0, "B": 10.0},
        {},
        {"A": 100.0, "B": 100.0},
        set(),
        **kw,
    )
    assert not res.cap_bound and res.cap_scale == 1.0
    assert res.targets == {
        "A": 9.0,
        "B": -4.0,
    }  # q=0 below lower edge 9; above upper -4 -> trunc -4
    res = strategy_f2.position_steps(
        syms,
        {"A": 600.0, "B": -400.0},
        {"A": 100.0, "B": 100.0},
        {"A": 300.0, "B": -200.0},
        {"A": 100.0, "B": 100.0},
        set(),
        **kw,
    )
    assert res.cap_bound and res.unrounded_gross_usd == 100000.0 and res.cap_scale == 0.5
    assert res.n_capped == {"A": 300.0, "B": -200.0} and res.a_capped == {"A": 50.0, "B": 50.0}
    assert res.targets == {"A": 300.0, "B": -200.0}


def test_buffer_inside_and_edges():
    assert strategy_f2.buffered(100.0, 50.0, 103.0, 0.1) == 103.0
    assert strategy_f2.buffered(100.0, 50.0, 110.0, 0.1) == 105.0
    assert strategy_f2.buffered(100.0, 50.0, 80.0, 0.1) == 95.0


def test_granularity_fractional_longs_whole_shorts_toward_zero():
    g = strategy_f2.granular
    assert g(12.3456, 1000) == 12.346
    assert g(0.0004, 1000) == 0.0
    assert g(2.5, 1) == 3.0
    assert g(-3.7, 1000) == -3.0
    assert g(-0.4, 1000) == 0.0 and str(g(-0.4, 1000)) == "0.0"


def test_second_check_scales_longs_and_shorts():
    # holdings inside the band push gross above B after the cap: every new-target position,
    # long or short, scaled by max(0, B - C) / its gross (wave 3, S1; was: longs only)
    res = strategy_f2.position_steps(
        ["A", "B"],
        {"A": 300.0, "B": -200.0},
        {"A": 100.0, "B": 100.0},
        {"A": 309.0, "B": -209.0},
        {"A": 100.0, "B": 100.0},
        set(),
        cap_usd=50000.0,
        buffer_size=0.1,
        steps=1000,
    )
    assert not res.cap_bound
    assert res.second_check["applied"] and res.second_check["gross_before_usd"] == 51800.0
    assert res.second_check["factor"] == pytest.approx(50000.0 / 51800.0)
    assert res.targets["B"] == -201.0  # -209 x 0.9653 = -201.7, toward zero to whole shares
    assert res.targets["A"] == 298.262  # 309 x 0.9653 = 298.2625, toward zero to 0.001
    assert res.target_gross_usd <= 50000.0


def test_missing_close_keeps_shares_nonlive_zero():
    res = strategy_f2.position_steps(
        ["A", "B", "C"],
        {"A": 10.0},
        {"A": 10.0},
        {"B": 7.0, "C": 3.0},
        {"A": 10.0, "B": 10.0, "C": 10.0},
        {"C"},
        cap_usd=1e9,
        buffer_size=0.1,
        steps=1000,
    )
    assert res.targets == {"A": 9.0, "B": 7.0, "C": 0.0}


def test_short_history_is_flat():
    rows = synthetic_rows(n=200)
    dec = strategy_f2.decide(rows, {"QQQ": 5.0}, F2)
    assert dec.exposure["n_live"] == 0
    assert all(v == 0.0 for v in dec.targets.values())


def test_mapping_history_matches_rows():
    rows = synthetic_rows()
    frames = strategy_f2.frames_from_history(rows, ETFS)
    a = strategy_f2.target_shares(rows, {}, F2)
    b = strategy_f2.target_shares(frames, {}, F2)
    assert a == b
    assert isinstance(frames["QQQ"], pd.DataFrame)
