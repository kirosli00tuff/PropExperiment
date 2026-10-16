"""forward.strategy.target_positions: the same targets as the historical book (one frozen
implementation), both history formats, and one integration run of forward.runner with the real
strategy (synthetic data only, no network)."""

from __future__ import annotations

import copy
import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from forward import ledger as FL
from forward import rolls as R
from forward import strategy as ST
from forward.history import HistoryRow
from forward.runner import PaperRunner, RunnerConfig
from forward.sources import InMemorySettlementSource
from microbook import book as B
from microbook.config_build import build_config, build_tables, extension_cost_row
from microbook.universe import BY_CODE, MICROS

CODES = ["MNG", "M6E", "MZC"]
REPO = Path(__file__).resolve().parents[1]


def _config(codes, method="greedy", warmup=60):
    rows = {m.code: extension_cost_row(m) for m in MICROS}
    n = len(codes)
    corr = np.full((n, n), 0.2)
    np.fill_diagonal(corr, 1.0)
    cfg = build_config(fdm=1.1, fdm_corr=None, idm=1.5, idm_corr=corr.tolist(), idm_codes=codes,
                       cost_rows=rows)
    cfg["instruments_order"] = list(codes)
    cfg["instruments"] = {c: cfg["instruments"][c] for c in codes}
    cfg["rounding_method"]["value"] = method
    cfg["warmup_diffs"]["value"] = warmup
    return cfg


def _cache(code: str, n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    m = BY_CODE[code]
    level = {"MNG": 3.0, "M6E": 1.1, "MZC": 4.5}[code]
    step = rng.normal(0.0004, 0.012, n).cumsum()
    price = level * np.exp(step + 0.3 * np.sin(np.arange(n) / 40.0))
    dp = np.concatenate([[np.nan], np.diff(price)])
    return pd.DataFrame({"date": pd.bdate_range("2018-01-01", periods=n), "contract": m.code,
                         "price": price, "dp": dp, "fail": "", "n_rolls": 0, "roll_long_c": 0.0,
                         "roll_short_c": 0.0, "cost_buy_c": np.nan, "cost_sell_c": np.nan,
                         "comm_side_c": np.nan, "event": False})


@pytest.mark.parametrize("method", ["greedy", "simple"])
def test_strategy_targets_equal_the_historical_book(method):
    # Arrange: three instruments, one book through microbook.book
    cfg = _config(CODES, method)
    caches = {c: _cache(c, 260, seed) for seed, c in enumerate(CODES)}
    insts = [B.prepare(BY_CODE[c], caches[c], cfg)[0] for c in CODES]
    for ins in insts:
        B.add_combined(ins, cfg, cfg["fdm"]["value"])
    grid = B.build_grid(insts)
    corr_t = B.correlations(grid, cfg)
    idm_t = B.idm_series(grid, np.asarray(cfg["idm"]["correlation"]), 2.5)
    run = B.simulate(grid, cfg, method, 25_000, idm_t, corr_t)
    assert np.abs(run.targets[-60:]).sum() > 0  # the book trades in this window
    # Act / Assert: the strategy on data through date k gives the book's target at k
    for k in range(len(grid.dates) - 60, len(grid.dates), 7):
        hist = {c: pd.DataFrame({"adj_price": caches[c]["price"].to_numpy()[: k + 1],
                                 "price": caches[c]["price"].to_numpy()[: k + 1]},
                                index=grid.dates[: k + 1]) for c in CODES}
        prev = {c: int(run.targets[k - 1, j]) for j, c in enumerate(CODES)}
        got = ST.target_positions(hist, prev, cfg)
        assert got == {c: int(run.targets[k, j]) for j, c in enumerate(CODES)}


def test_history_rows_and_frames_give_the_same_targets():
    cfg = _config(CODES, "greedy")
    caches = {c: _cache(c, 200, 10 + s) for s, c in enumerate(CODES)}
    dates = pd.bdate_range("2018-01-01", periods=200)
    rows = tuple(HistoryRow(d.date(), {c: {f"{c}H19": float(caches[c]["price"].iloc[i])}
                                       for c in CODES}, {c: f"{c}H19" for c in CODES})
                 for i, d in enumerate(dates))
    frames = {c: pd.DataFrame({"adj_price": caches[c]["price"].to_numpy(),
                               "price": caches[c]["price"].to_numpy()}, index=dates) for c in CODES}
    prev = {"MNG": 1, "M6E": 0, "MZC": -1}
    assert ST.target_positions(rows, prev, cfg) == ST.target_positions(frames, prev, cfg)


def test_not_live_gives_zero_and_missing_day_carries():
    cfg = _config(CODES, "simple", warmup=500)  # nobody is live
    caches = {c: _cache(c, 100, s) for s, c in enumerate(CODES)}
    dates = pd.bdate_range("2018-01-01", periods=100)
    frames = {c: pd.DataFrame({"adj_price": caches[c]["price"].to_numpy(),
                               "price": caches[c]["price"].to_numpy()}, index=dates) for c in CODES}
    frames["MZC"] = frames["MZC"].iloc[:-1]  # no settlement on t: keeps its position
    got = ST.target_positions(frames, {"MNG": 2, "M6E": -1, "MZC": 3}, cfg)
    assert got == {"MNG": 0, "M6E": 0, "MZC": 3}


def test_strategy_returns_python_ints_for_every_instrument():
    cfg = _config(CODES, "greedy")
    caches = {c: _cache(c, 120, s) for s, c in enumerate(CODES)}
    dates = pd.bdate_range("2018-01-01", periods=120)
    frames = {c: pd.DataFrame({"adj_price": caches[c]["price"].to_numpy(),
                               "price": caches[c]["price"].to_numpy()}, index=dates) for c in CODES}
    got = ST.target_positions(frames, {}, cfg)
    assert set(got) == set(CODES) and all(type(v) is int for v in got.values())


# ------------------------------------------------------------------ runner integration ----
RUN_CODES = ["MNQ", "MGC", "M6E", "MZC", "10Y"]
LEVEL = {"MNQ": 18000.0, "MGC": 2000.0, "M6E": 1.10, "MZC": 4.50, "10Y": 4.00}
DAILY = {"MNQ": 0.012, "MGC": 0.009, "M6E": 0.005, "MZC": 0.014, "10Y": 0.0}
TICK = {"MNQ": 0.25, "MGC": 0.1, "M6E": 0.0001, "MZC": 0.005, "10Y": 0.001}


def _bdays(start: date, n: int) -> list[date]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def _synthetic_world(days, rolls, seed=7):
    """Settlements of the active contract and the previous day's active one (both on a roll
    day), a shared random walk per instrument plus a per-contract basis."""
    rng = np.random.default_rng(seed)
    data = {}
    level = dict(LEVEL)
    for k, d in enumerate(days):
        day = {}
        for c in RUN_CODES:
            if c == "10Y":
                level[c] = max(0.5, level[c] + rng.normal(0.0, 0.05) + 0.02 * np.sin(k / 30))
            else:
                level[c] *= float(np.exp(rng.normal(0.0004, DAILY[c]) + 0.004 * np.sin(k / 30)))
            cids = {R.active_contract(rolls[c], d)}
            if k:
                cids.add(R.active_contract(rolls[c], days[k - 1]))
            prices = {}
            for cid in sorted(cids):
                basis = (R.parse_contract(rolls[c], cid)[1] % 3) * 10 * TICK[c]
                prices[cid] = round(round((level[c] + basis) / TICK[c]) * TICK[c], 6)
            day[c] = prices
        data[d] = day
    return data


def test_runner_with_the_real_strategy_300_days(tmp_path):
    # Arrange: the study's frozen config (simple rounding, R-B7) restricted to five instruments,
    # the real roll table
    full = json.loads((REPO / "forward" / "config_f1.json").read_text(encoding="utf-8"))
    if full["idm"]["correlation"] is None:
        pytest.skip("forward/config_f1.json has no IDM yet (run microbook.run study)")
    assert full["rounding_method"]["value"] == "simple"  # lead ruling R-B7: E22-F1 rounds simple
    cfg = copy.deepcopy(full)
    order = full["idm"]["instruments"]
    idx = [order.index(c) for c in RUN_CODES]
    cfg["idm"]["correlation"] = [[full["idm"]["correlation"][i][j] for j in idx] for i in idx]
    cfg["idm"]["instruments"] = list(RUN_CODES)
    cfg["instruments_order"] = list(RUN_CODES)
    cfg["instruments"] = {c: full["instruments"][c] for c in RUN_CODES}
    tables = build_tables(cfg)
    rolls = {c: spec for c, spec in R.load_rolls().items() if c in RUN_CODES}
    days = _bdays(date(2025, 1, 6), 280 + 300)
    data = _synthetic_world(days, rolls)
    warm = tuple(HistoryRow(d, data[d], {c: R.active_contract(rolls[c], d) for c in RUN_CODES})
                 for d in days[:280])
    run_days = days[280:]
    source = InMemorySettlementSource({d: data[d] for d in run_days})
    config = RunnerConfig(tables["multipliers"], tables["cost_per_side"], rolls, cfg)
    runner = PaperRunner(tmp_path / "f1.jsonl", source, config, warmup=warm)
    # Act
    records = [runner.run_date(d) for d in run_days]
    # Assert: a verifying chain, integer positions, orders at t filled at t+1's settlement
    report = FL.verify(tmp_path / "f1.jsonl")
    assert report.ok and report.n_records == 300
    traded = 0
    for k, rec in enumerate(records):
        for c, pos in rec["positions"].items():
            assert type(pos["qty"]) is int
        assert all(type(q) is int for q in rec["orders"].values())
        if k == 0:
            assert rec["fills"] == []
            continue
        # the runner's "orders" are the strategy's target positions where they differ from held
        prev_targets = records[k - 1]["orders"]
        prev_held = {i: p["qty"] for i, p in records[k - 1]["positions"].items()}
        fills = {f["instrument"]: f for f in rec["fills"]}
        assert {i: f["qty"] for i, f in fills.items()} == {
            i: t - prev_held.get(i, 0) for i, t in prev_targets.items()}
        for i, f in fills.items():
            assert f["price"] == data[run_days[k]][i][f["contract"]]  # t+1's settlement
            assert rec["positions"][i]["qty"] == prev_targets[i]
        traded += len(fills)
    assert traded > 0
    assert any(rec["rolls"] for rec in records)
