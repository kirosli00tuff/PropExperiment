"""Stage E.19 returns module: synthetic bars and synthetic paths only (no data store is read)."""

from __future__ import annotations

import json
import math
from datetime import date, time, timedelta
from decimal import Decimal

import numpy as np
import pytest

from data.session import ct_ns
from prop_econ import returns as R
from prop_econ.types import ShockSet

NQ = R.Contract("NQ", "equity", Decimal("0.25"), Decimal("5"), time(8, 30), time(15, 0))
D0 = date(2023, 3, 6)  # a Monday, CST
D1 = date(2023, 3, 14)  # a Tuesday, CDT (after the DST switch)


def _day_bars(d: date, o: float, h: float, lo: float, c: float, inst: int = 1,
              skip_first: bool = False, skip_last: bool = False, roll_at: int | None = None
              ) -> list[tuple]:
    """Bars 08:00..15:29 CT on day d; the [08:30, 15:00) window carries O, H, L, C exactly and
    the bars outside it carry extreme prices that must be ignored."""
    o_min, c_min = 8 * 60 + 30, 15 * 60
    rows = []
    for k in range(8 * 60, 15 * 60 + 30):
        if (skip_first and k == o_min) or (skip_last and k == c_min - 1):
            continue
        if o_min <= k < c_min:
            bar_o, bar_c = o, (c if k == c_min - 1 else o)
            bar_h, bar_l = max(bar_o, bar_c), min(bar_o, bar_c)
            bar_h = max(bar_h, h) if k == 10 * 60 else bar_h
            bar_l = min(bar_l, lo) if k == 11 * 60 else bar_l
        else:
            bar_o, bar_c, bar_h, bar_l = 100.0, 100.0, 10_000.0, 1.0
        iid = inst + (1 if roll_at is not None and k >= roll_at else 0)
        rows.append((ct_ns(d, time(k // 60, k % 60)), d, bar_o, bar_h, bar_l, bar_c, iid))
    return rows


def _moves(rows: list[tuple], c: R.Contract = NQ) -> R.SessionMoves:
    ts, d, o, h, lo, cl, iid = (np.array(x) for x in zip(*rows, strict=True))
    return R.session_moves(ts, d.astype("datetime64[D]"), o, h, lo, cl, iid, c)


def test_session_moves_exact_r_up_dn_in_usd_per_full_contract():
    rows = _day_bars(D0, o=12000.0, h=12050.25, lo=11990.5, c=12010.75)
    rows += _day_bars(D1, o=12100.0, h=12100.0, lo=12000.0, c=12000.0)
    m = _moves(rows)
    assert list(m.dates.astype(str)) == ["2023-03-06", "2023-03-14"]
    # NQ: $5 per 0.25 tick = $20 per point
    assert m.r.tolist() == [10.75 * 20, -100.0 * 20]
    assert m.up.tolist() == [50.25 * 20, 0.0]
    assert m.dn.tolist() == [-9.5 * 20, -100.0 * 20]
    assert m.skips == dict.fromkeys(R.SKIP_REASONS, 0)
    assert m.n_trade_dates == 2


def test_session_moves_skips_roll_missing_bars_and_empty_window_by_reason():
    d = [D0 + timedelta(days=i) for i in range(5)]  # Mon..Fri
    rows = _day_bars(d[0], 100.0, 101.0, 99.0, 100.5)  # kept
    rows += _day_bars(d[1], 100.0, 101.0, 99.0, 100.5, roll_at=12 * 60)  # instrument change
    rows += _day_bars(d[2], 100.0, 101.0, 99.0, 100.5, skip_first=True)  # no O_X bar
    rows += _day_bars(d[3], 100.0, 101.0, 99.0, 100.5, skip_last=True)  # no C_X-1 bar
    cut = ct_ns(d[4], time(8, 30))
    rows += [r for r in _day_bars(d[4], 100.0, 101.0, 99.0, 100.5) if r[0] < cut]  # none in window
    m = _moves(rows)
    assert m.dates.astype(str).tolist() == [str(d[0])]
    assert m.skips == {"no_bars_in_window": 1, "instrument_change": 1, "missing_open_bar": 1,
                       "missing_close_bar": 1}


def test_session_moves_rejects_dates_outside_training_window_and_off_grid_prices():
    with pytest.raises(R.ReturnsError, match="leave"):
        _moves(_day_bars(date(2024, 3, 4), 100.0, 101.0, 99.0, 100.5))
    with pytest.raises(R.ReturnsError, match="tick grid"):
        _moves(_day_bars(D0, 100.0, 101.0, 99.0, 100.1))


def test_evening_bars_of_the_next_trade_date_give_no_kept_date():
    rows = _day_bars(D0, 100.0, 101.0, 99.0, 100.5)
    nxt = D0 + timedelta(days=1)  # 17:00-17:30 CT on D0 belongs to the next trade date
    rows += [(ct_ns(D0, time(17, k)), nxt, 100.0, 100.0, 100.0, 100.0, 1) for k in range(30)]
    m = _moves(rows)
    assert m.dates.astype(str).tolist() == [str(D0)] and m.r.tolist() == [0.5 * 20]
    assert m.n_trade_dates == 2 and m.skips["no_bars_in_window"] == 1
    with pytest.raises(R.ReturnsError, match="increasing"):
        _moves(rows[::-1])


def _synthetic_moves(n: int, seed: int = 0, root: str = "NQ") -> R.SessionMoves:
    g = np.random.default_rng(seed)
    r = np.round(g.standard_normal(n) * 40) * 5 + 25.0
    up = np.maximum(r, 0) + np.round(np.abs(g.standard_normal(n)) * 20) * 5
    dn = np.minimum(r, 0) - np.round(np.abs(g.standard_normal(n)) * 20) * 5
    d0 = np.datetime64("2020-01-01")
    dates = np.arange(d0, d0 + np.timedelta64(n, "D"))
    return R.SessionMoves(root, dates, r, up, dn, n, dict.fromkeys(R.SKIP_REASONS, 0), 0)


def test_standardize_demeans_exactly_and_bounds_w():
    m = _synthetic_moves(500)
    p = R.standardize(m)
    assert abs(p.z_long.mean()) < 1e-12 and abs(p.z_short.mean()) < 1e-12
    assert p.mean_r_usd == pytest.approx(m.r.mean())
    assert np.std(p.z_long, ddof=1) == pytest.approx(1.0)
    assert np.all(p.w_long <= np.minimum(0, p.z_long))
    assert np.all(p.w_short <= np.minimum(0, p.z_short))
    np.testing.assert_array_equal(p.z_short, -p.z_long)


def test_standardize_hand_values():
    r = np.array([30.0, -10.0, -20.0])
    up, dn = np.array([40.0, 0.0, 5.0]), np.array([0.0, -50.0, -20.0])
    m = R.SessionMoves("X", np.arange(3).astype("datetime64[D]"), r, up, dn, 3, {}, 0)
    rp = r - 0.0  # mean is exactly 0
    s = float(np.std(rp, ddof=1))
    p = R.PathShocks(m, 0.0, s, rp / s, np.minimum(np.minimum(dn, rp), 0) / s, -rp / s,
                     np.minimum(np.minimum(-up, -rp), 0) / s)
    with pytest.raises(R.ReturnsError):
        R.standardize(m)  # too few dates for 5-day blocks
    # day 0: long w = min(0, 30, 0) = 0; short w = min(-40, -30, 0) = -40
    assert p.w_long[0] == 0.0 and p.w_short[0] == pytest.approx(-40 / s)
    # day 1: long w = min(-50, -10) = -50; short w = min(0, 10, 0) = 0
    assert p.w_long[1] == pytest.approx(-50 / s) and p.w_short[1] == 0.0


def _index_paths(sizes: tuple[int, ...] = (40, 30, 25, 20, 50)) -> tuple[R.PathShocks, ...]:
    """Paths whose z_long encodes (path, kept index) so draws can be decoded."""
    out = []
    for k, (root, n) in enumerate(zip(R.ROOTS, sizes, strict=True)):
        z = (k * 1000 + np.arange(n)).astype(float)
        m = R.SessionMoves(root, np.arange(n).astype("datetime64[D]"), z, z, z, n, {}, 0)
        out.append(R.PathShocks(m, 0.0, 1.0, z, np.minimum(z, 0) - 1, -z,
                                np.minimum(-z, 0) - 1 - 0.5))
    return tuple(out)


SPECS = R.product_specs(dict.fromkeys(R.ROOTS, 100.0), "d8")


def test_bootstrap_is_deterministic_by_seed_and_blocks_stay_in_one_path():
    paths = _index_paths()
    a = R.bootstrap_shocks(paths, SPECS, R.draw_layout(50, 23, seed=7, direction="long"))
    b = R.bootstrap_shocks(paths, SPECS, R.draw_layout(50, 23, seed=7, direction="long"))
    c = R.bootstrap_shocks(paths, SPECS, R.draw_layout(50, 23, seed=8, direction="long"))
    np.testing.assert_array_equal(a.z, b.z)
    assert not np.array_equal(a.z, c.z)
    assert isinstance(a, ShockSet) and a.z.shape == (50, 23)
    path_of, pos = (a.z // 1000).astype(int), (a.z % 1000).astype(int)
    np.testing.assert_array_equal(path_of, a.prod)
    sizes = np.array([p.n_kept for p in paths])
    for blk in range(0, 23, R.BLOCK_DAYS):
        seg = slice(blk, min(blk + R.BLOCK_DAYS, 23))
        assert (path_of[:, seg] == path_of[:, [blk]]).all()  # one path per block
        assert (np.diff(pos[:, seg], axis=1) == 1).all()  # consecutive kept dates
        width = seg.stop - seg.start
        if width == R.BLOCK_DAYS:  # blocks never wrap: start <= n_kept - 5
            assert (pos[:, blk] <= sizes[path_of[:, blk]] - R.BLOCK_DAYS).all()


def test_bootstrap_block_starts_cover_the_whole_path():
    paths = _index_paths()
    s = R.bootstrap_shocks(paths, SPECS, R.draw_layout(4000, 5, seed=1, direction="long",
                                                       products="ZN"))
    starts = (s.z[:, 0] % 1000).astype(int)
    assert set(starts) == set(range(paths[3].n_kept - R.BLOCK_DAYS + 1))
    assert (s.prod == R.ROOTS.index("ZN")).all()


def test_direction_modes_random_and_long():
    paths = _index_paths()
    rnd = R.bootstrap_shocks(paths, SPECS, R.draw_layout(400, 50, seed=3))
    lng = R.bootstrap_shocks(paths, SPECS, R.draw_layout(400, 50, seed=3, direction="long"))
    assert (lng.z >= 0).all()  # always the long column
    short_share = np.mean(rnd.z < 0)  # the short column is -z_long
    assert 0.47 < short_share < 0.53
    np.testing.assert_array_equal(np.abs(rnd.z), lng.z)  # same blocks, only the sign differs
    # w comes from the matching column
    assert np.all(rnd.w[rnd.z < 0] == np.minimum(rnd.z[rnd.z < 0], 0) - 1.5)


def test_per_product_restriction_and_bad_arguments():
    lay = R.draw_layout(100, 10, seed=2, products="6E")
    assert (lay.prod == R.ROOTS.index("6E")).all()
    for kw in ({"products": "ES"}, {"direction": "short"}, {"products": ()}):
        with pytest.raises(ValueError):
            R.draw_layout(10, 10, seed=1, **kw)
    with pytest.raises(ValueError):
        R.build_shocks(10, 10, 1, tail="t", paths=_index_paths())
    with pytest.raises(ValueError):
        R.product_specs(dict.fromkeys(R.ROOTS, 1.0), "x")


def test_build_shocks_with_supplied_paths_and_both_tails_share_products():
    paths = _index_paths()
    b = R.build_shocks(200, 30, 11, tail="bootstrap", paths=paths)
    n = R.build_shocks(200, 30, 11, tail="normal", paths=paths)
    np.testing.assert_array_equal(b.prod, n.prod)
    assert b.products == n.products and len(b.products) == 5
    lay = R.draw_layout(200, 30, 11)
    np.testing.assert_array_equal(np.sign(b.z), lay.sign * (b.z != 0))


def test_normal_source_moments_and_bridge_bound():
    s = R.normal_shocks(SPECS, R.draw_layout(400, 500, seed=5), seed=5)
    assert np.all(s.w <= np.minimum(0.0, s.z))
    assert abs(s.z.mean()) < 0.01 and abs(s.z.var() - 1.0) < 0.01
    # the minimum of a free Brownian motion on [0, 1]: E = -sqrt(2/pi)
    assert s.w.mean() == pytest.approx(-math.sqrt(2 / math.pi), abs=0.01)
    assert R.bridge_min(np.array([1.5, -2.0]), np.array([1.0, 1.0])).tolist() == [0.0, -2.0]


def test_product_specs_values_from_the_cost_files():
    costs = json.loads(R.COST_TABLE.read_text())["products"]
    wall_rows = {r["vehicle"]: r for r in json.loads(R.COST_WALL.read_text())["rows"]}
    sig = {"NQ": 400.0, "CL": 900.0, "GC": 1200.0, "ZN": 300.0, "6E": 500.0}
    d8 = {s.name: s for s in R.product_specs(sig, "d8")}
    for root in R.ROOTS:
        hd = costs[root]["headline_day_session"]["round_turn_usd"]["mean"]
        assert d8[root].rt_full_usd == pytest.approx(hd, rel=1e-12)
        micro = R.MICRO_OF[root]
        if micro is None:
            assert d8[root].sigma_micro_usd is None and not d8[root].has_micro
            continue
        assert d8[root].micro_name == micro
        assert d8[root].sigma_micro_usd == pytest.approx(sig[root] / 10)
        mh = costs[micro]["headline_day_session"]["round_turn_usd"]["mean"]
        assert d8[root].rt_micro_usd == pytest.approx(mh, rel=1e-12)
    assert d8["NQ"].rt_full_usd == pytest.approx(15.552175306459402)
    wall = {s.name: s for s in R.product_specs(sig, "wall")}
    assert wall["ZN"].rt_full_usd == pytest.approx(wall_rows["ZN"]["rt_wall_ticks"] * 15.625)
    assert wall["NQ"].rt_micro_usd == pytest.approx(wall_rows["MNQ"]["rt_wall_ticks"] * 0.5)
    assert wall["6E"].rt_full_usd == pytest.approx(wall_rows["6E"]["rt_wall_ticks"] * 6.25)
    rule_nq = R._wall_rule_ticks(costs["NQ"]) * 5.0  # no cost_wall row for NQ
    assert wall["NQ"].rt_full_usd == pytest.approx(rule_nq)
    _, src = R.wall_round_trips()
    assert {v for v, s in src.items() if "rule" in s} == {"NQ", "CL", "GC", "M6E"}


def test_contract_facts_match_d6_and_d8():
    assert (R.contract("NQ").open_ct, R.contract("NQ").close_ct) == (time(8, 30), time(15, 0))
    assert (R.contract("GC").open_ct, R.contract("GC").close_ct) == (time(7, 20), time(12, 30))
    assert R.contract("CL").multiplier == 1000 and R.contract("ZN").multiplier == 1000
    assert R.contract("6E").multiplier == 125_000 and R.contract("NQ").multiplier == 20


def test_read_store_on_a_synthetic_parquet(tmp_path):
    pa = pytest.importorskip("pyarrow")
    import pyarrow.parquet as pq

    rows = _day_bars(D0, 100.0, 101.0, 99.0, 100.5)
    ts, d, o, h, lo, cl, iid = zip(*rows, strict=True)
    t = pa.table({"ts_event": list(ts), "open": list(o), "high": list(h), "low": list(lo),
                  "close": list(cl), "instrument_id": list(iid),
                  "trade_date": [str(x) for x in d], "volume": [1] * len(ts)})
    f = tmp_path / "s.parquet"
    pq.write_table(t, f)
    m = R.read_store(f, NQ)
    assert m.r.tolist() == [10.0] and m.up.tolist() == [20.0] and m.dn.tolist() == [-20.0]
