"""Synthetic tests for the E.31 stats layer (stats31.py, stats31_core.py, stats31_report.py).

Known answers only: no DBN file, no network. Tables follow TABLES31.md.
Run: uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_stats31.py
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

PILOT = Path(__file__).resolve().parents[1]
if str(PILOT) not in sys.path:
    sys.path.insert(0, str(PILOT))

import stats31 as st  # noqa: E402
import stats31_core as core  # noqa: E402
import stats31_report as report  # noqa: E402

NS = 1_000_000_000
F64, I64, STR, BOOL = pa.float64(), pa.int64(), pa.string(), pa.bool_()
MO_COLS = [f"{p}{h}" for p in ("mo_", "mo_nd_") for h in (1, 10, 60)]
PLACEMENT_SCHEMA = pa.schema(
    [("trade_date", pa.date32()), ("session", STR), ("symbol", STR), ("instrument_id", pa.uint32()),
     ("raw_symbol", STR), ("model", STR), ("side", pa.int8()), ("g_ns", I64), ("j_ns", I64),
     ("price", F64), ("stale", BOOL), ("filled", BOOL), ("t_fill_ns", I64), ("trigger", STR),
     ("wait_s", F64), ("mid0", F64), ("c_half", F64), *[(c, F64) for c in MO_COLS],
     ("zs_d1", F64), ("zs_d10", F64), ("zl_d1", F64), ("zl_d10", F64), ("usda_min", F64),
     ("imb", F64), ("touched", BOOL)])
LOOP_SCHEMA = pa.schema([("trade_date", pa.date32()), ("symbol", STR), ("model", STR),
                         ("round_trips", pa.int32()), ("entries_filled", pa.int32()),
                         ("orders_placed", pa.int32()), ("mean_rt_s", F64)])
IMPLIED_SCHEMA = pa.schema([("trade_date", pa.date32()), ("symbol", STR), ("session", STR),
                            *[(c, I64) for c in st.IMPLIED_COUNTS]])
DAYS_SCHEMA = pa.schema([("trade_date", pa.date32()), ("symbol", STR),
                         ("instrument_id", pa.uint32()), ("raw_symbol", STR),
                         ("included", BOOL), ("reason", STR),
                         *[(c, I64) for c in ("n_records", "inversions", "bad_flag_records",
                                              "crossed_moments")],
                         ("max_gap_day_s", F64), ("placements_day", I64), ("placements_on", I64)])
NAN = float("nan")


# ------------------------------------------------------------------ synthetic tables ----
def _d(date: str) -> dt.date:
    return dt.date.fromisoformat(date)


def placement(date: str, k: int, *, model: str = "c", session: str = "DAY",
              symbol: str = "ZM.v.0", side: int = 1, imb: float = 0.0, **kw: Any) -> dict[str, Any]:
    """An unfilled placement; keyword arguments override any column."""
    j = 1_700_000_000 * NS + k * 300 * NS
    row = {"trade_date": _d(date), "session": session, "symbol": symbol, "instrument_id": 1,
           "raw_symbol": "ZMH4" if symbol == "ZM.v.0" else "ZMK4", "model": model, "side": side,
           "g_ns": j - 50_000_000, "j_ns": j, "price": 350.0, "stale": False, "filled": False,
           "t_fill_ns": -1, "trigger": "", "wait_s": 60.05, "mid0": NAN, "c_half": NAN,
           **{c: NAN for c in MO_COLS}, "zs_d1": NAN, "zs_d10": NAN, "zl_d1": NAN, "zl_d10": NAN,
           "usda_min": NAN, "imb": imb, "touched": False}
    row.update(kw)
    return row


def fill(date: str, k: int, edge: float, *, c: float = 0.5, wait: float = 5.0,
         nodrop: float | None = None, dropped: bool = False, trigger: str = "through",
         **kw: Any) -> dict[str, Any]:
    """A filled placement with E_h = edge at every h (markout = edge - c). ``dropped``: the
    headline markouts are NaN; the no-drop edge is ``nodrop`` (default: edge)."""
    nd = edge if nodrop is None else nodrop
    row = placement(date, k, **kw)
    mo = {f"mo_{h}": (NAN if dropped else edge - c) for h in (1, 10, 60)}
    row.update(filled=True, trigger=trigger, wait_s=wait, t_fill_ns=row["j_ns"] + int(wait * NS),
               mid0=350.05, c_half=c, touched=True, **mo,
               **{f"mo_nd_{h}": nd - c for h in (1, 10, 60)})
    row.update({k2: v for k2, v in kw.items() if k2 in row})
    return row


def day_rows(date: str, symbols: tuple[str, ...] = st.SYMBOLS, included: bool = True,
             reason: str = "") -> list[dict[str, Any]]:
    return [{"trade_date": _d(date), "symbol": s, "instrument_id": 1, "raw_symbol": "ZMH4",
             "included": included, "reason": reason, "n_records": 1000, "inversions": 0,
             "bad_flag_records": 0, "crossed_moments": 2, "max_gap_day_s": 3.0,
             "placements_day": 114, "placements_on": 300} for s in symbols]


def loop_row(date: str, rt: int, model: str = "c") -> dict[str, Any]:
    return {"trade_date": _d(date), "symbol": "ZM.v.0", "model": model, "round_trips": rt,
            "entries_filled": rt, "orders_placed": 3 * rt + 1,
            "mean_rt_s": 30.0 if rt else NAN}


def write_day(root: Path, date: str, placements: list[dict[str, Any]],
              loops: list[dict[str, Any]] | None = None,
              implied: list[dict[str, Any]] | None = None,
              days: list[dict[str, Any]] | None = None, done: bool = True) -> Path:
    folder = root / date
    folder.mkdir(parents=True)
    for name, rows, schema in (("placements", placements, PLACEMENT_SCHEMA),
                               ("loop", loops or [], LOOP_SCHEMA),
                               ("implied", implied or [], IMPLIED_SCHEMA),
                               ("days", day_rows(date) if days is None else days, DAYS_SCHEMA)):
        pq.write_table(pa.Table.from_pylist(rows, schema=schema), folder / f"{name}.parquet")
    if done:
        (folder / "DONE").write_text("ok\n")
    return folder


def compute(root: Path, boot: int = core.BOOT_REPLICATES) -> dict[str, Any]:
    return st.to_jsonable(st.compute_all(st.load_runs(root), boot=boot))


DATES5 = ("2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-08")


def scenario(root: Path, edges: tuple[float, ...], fills_per_day: int,
             loops: tuple[int, ...], dropped_per_day: int = 0,
             nodrop_edges: tuple[float, ...] | None = None, dropped_nodrop: float = 1.0) -> Path:
    """Five dates. Primary population (c, DAY, ZM.v.0): ``fills_per_day`` fills with dropping
    E_10 = edges[d] and no-drop E_10 = nodrop_edges[d] (default: the same), plus as many unfilled
    placements, plus ``dropped_per_day`` fills whose dropping markouts are NaN and whose no-drop
    edge is ``dropped_nodrop`` (NaN: no valid markout of either variant). Decoys with E = -5 in
    models a and b, in ZM.v.1 and in the overnight session, and decoy loops of 0 for models a and
    b: any wrong wiring of the primary population flips the verdict."""
    for d, date in enumerate(DATES5):
        rows: list[dict[str, Any]] = []
        k = 0
        for i in range(fills_per_day):
            nd = None if nodrop_edges is None else nodrop_edges[d]
            rows.append(fill(date, k, edges[d], nodrop=nd, side=1 if i % 2 else -1))
            rows.append(placement(date, k + 1, side=1 if i % 2 else -1))
            k += 2
        for _ in range(dropped_per_day):
            rows.append(fill(date, k, 0.5, nodrop=dropped_nodrop, dropped=True))
            k += 1
        for model, symbol, session in (("a", "ZM.v.0", "DAY"), ("b", "ZM.v.0", "DAY"),
                                       ("c", "ZM.v.1", "DAY"), ("c", "ZM.v.0", "OVERNIGHT")):
            for i in range(150):
                rows.append(fill(date, k, -5.0, model=model, symbol=symbol, session=session,
                                 side=1 if i % 2 else -1, trigger="queue" if model != "c"
                                 else "through"))
                k += 1
        write_day(root, date, rows, loops=[loop_row(date, loops[d]), loop_row(date, 0, "a"),
                                           loop_row(date, 0, "b")])
    return root


# ------------------------------------------------------------------ fill rate and KM ----
def test_fill_rate_and_km_on_a_hand_case(tmp_path: Path) -> None:
    date = "2024-01-02"
    rows = [fill(date, 0, 1.0, wait=0.5), fill(date, 1, 1.0, wait=5.0),
            fill(date, 2, 1.0, wait=45.0), fill(date, 3, 1.0, wait=60.03),
            placement(date, 4, wait_s=20.0), placement(date, 5)]
    write_day(tmp_path, date, rows)
    cell = compute(tmp_path, boot=200)["cells"]["c"]["ZM.v.0"]["DAY"]["pooled"]
    assert (cell["placements"], cell["fills"], cell["fills_in_cancel_latency"]) == (6, 4, 1)
    assert cell["fill_rate"]["value"] == pytest.approx(4 / 6)
    km = cell["km"]
    # S: 5/6 after 0.5 s, 4/6 after 5 s, (4/6)(2/3) = 4/9 after 45 s (at risk: 45, 60, 60).
    assert km["p_fill_by_1s"]["value"] == pytest.approx(1 / 6)
    assert km["p_fill_by_10s"]["value"] == pytest.approx(1 / 3)
    assert km["p_fill_by_60s"]["value"] == pytest.approx(5 / 9)
    assert km["median_s"] == pytest.approx(45.0)
    assert km["censored_before_60s"] == 1
    # one trade date: every replicate is that date, so the interval is the point
    assert km["p_fill_by_60s"]["ci95"] == pytest.approx([5 / 9, 5 / 9])
    assert cell["fill_rate"]["ci95"] == pytest.approx([4 / 6, 4 / 6])


def test_km_counts_events_before_censorings_at_a_tie() -> None:
    dur, event = np.array([10.0, 10.0, 20.0]), np.array([True, False, True])
    cdf, med = core.km_weighted(dur, event, np.zeros(3, dtype=np.int64), 1, np.ones((1, 1)),
                                (10, 20))
    assert cdf[0] == pytest.approx([1 / 3, 1.0])  # at 10 s all three are at risk
    assert med[0] == pytest.approx(20.0)


def test_weighted_km_equals_km_on_the_resampled_dates() -> None:
    rng = np.random.default_rng(5)
    dur = rng.uniform(0, 70, 40).round(1)
    day = np.repeat([0, 1, 2], [10, 12, 18])
    dur_c, event = core.km_inputs(dur, rng.uniform(size=40) < 0.6)
    cdf_w, med_w = core.km_weighted(dur_c, event, day, 3, np.array([[2, 0, 1]]), (1, 10, 60))
    keep = np.concatenate([np.flatnonzero(day == 0)] * 2 + [np.flatnonzero(day == 2)])
    cdf_r, med_r = core.km_weighted(dur_c[keep], event[keep], np.zeros(len(keep), dtype=np.int64),
                                    1, np.ones((1, 1)), (1, 10, 60))
    assert cdf_w[0] == pytest.approx(cdf_r[0])
    assert med_w[0] == pytest.approx(med_r[0], nan_ok=True)


# ------------------------------------------------------------------ bootstrap ----
def test_bootstrap_weights_draw_whole_dates_reproducibly() -> None:
    w = core.bootstrap_weights(7, 300, 31)
    assert w.shape == (300, 7) and (w.sum(axis=1) == 7).all()
    assert (w == core.bootstrap_weights(7, 300, 31)).all()
    assert (w != core.bootstrap_weights(7, 300, 32)).any()


def test_bootstrap_resamples_dates_not_fills(tmp_path: Path) -> None:
    """Date A: 10 fills with E_10 = 1; date B: 30 fills with E_10 = 3. Resampling the two dates
    gives only the means 1 (A twice), 2.5 (A and B) and 3 (B twice), so the interval is [1, 3];
    resampling fills would give a narrow interval around 2.5."""
    write_day(tmp_path, "2024-01-02", [fill("2024-01-02", k, 1.0) for k in range(10)])
    write_day(tmp_path, "2024-01-03", [fill("2024-01-03", k, 3.0) for k in range(30)])
    res = compute(tmp_path)
    mean = res["cells"]["c"]["ZM.v.0"]["DAY"]["pooled"]["horizons"]["drop"]["10"]["edge_mean"]
    assert mean["value"] == pytest.approx(2.5)
    assert mean["ci95"] == pytest.approx([1.0, 3.0])
    w = core.bootstrap_weights(2).astype(float)
    reps = core.ratio(w @ np.array([10.0, 90.0]), w @ np.array([10.0, 30.0]))
    assert set(np.round(reps, 9)) == {1.0, 2.5, 3.0}


def test_ratio_stat_replicate_is_the_weighted_date_ratio() -> None:
    num_d, den_d = np.array([3.0, 0.0, 5.0]), np.array([4.0, 2.0, 5.0])
    w = core.bootstrap_weights(3, 50, 31).astype(float)
    reps = core.ratio(w @ num_d, w @ den_d)
    for r in range(5):
        assert reps[r] == pytest.approx((w[r] * num_d).sum() / (w[r] * den_d).sum())
    assert core.ratio_stat(num_d, den_d, w)["value"] == pytest.approx(8 / 11)


# ------------------------------------------------------------------ kill rule ----
FRAGILE = "PASS, fragile (fee reading)"


@pytest.mark.parametrize(("k1d", "k1n", "fills", "loop", "full_d", "full_n", "holding", "line"), [
    (0.1, 0.1, 500, 25.0, 0.05, 0.05, set(), "PASS"),
    (0.0, 0.1, 500, 25.0, 0.05, 0.05, {"K1"}, "FAIL"),  # dropping alone; 0 is not above 0
    (0.1, 0.0, 500, 25.0, 0.05, 0.05, {"K1"}, "FAIL"),  # no-drop alone
    (-0.2, 0.1, 500, 25.0, 0.05, 0.05, {"K1"}, "FAIL"),
    (None, 0.1, 500, 25.0, 0.05, 0.05, {"K1"}, "FAIL"),
    (0.1, None, 500, 25.0, 0.05, 0.05, {"K1"}, "FAIL"),
    (0.1, 0.1, 399, 25.0, 0.05, 0.05, {"K2"}, "FAIL"),
    (0.1, 0.1, 400, 25.0, 0.05, 0.05, set(), "PASS"),
    (0.1, 0.1, 500, 19.99, 0.05, 0.05, {"K3"}, "FAIL"),
    (0.1, 0.1, 500, 20.0, 0.05, 0.05, set(), "PASS"),
    (0.1, 0.1, 500, None, 0.05, 0.05, {"K3"}, "FAIL"),
    (0.1, 0.1, 500, 25.0, 0.0, 0.05, set(), FRAGILE),  # 0.528 dropping bound not above 0
    (0.1, 0.1, 500, 25.0, 0.05, -0.01, set(), FRAGILE),  # 0.528 no-drop bound below 0
    (0.1, 0.1, 500, 25.0, None, 0.05, set(), FRAGILE),
    (-0.1, 0.1, 500, 25.0, -0.3, -0.3, {"K1"}, "FAIL"),  # a FAIL is never labelled fragile
    (-1.0, -1.0, 10, 0.0, -2.0, -2.0, {"K1", "K2", "K3"}, "FAIL")])
def test_evaluate_kill(k1d: float | None, k1n: float | None, fills: int, loop: float | None,
                       full_d: float | None, full_n: float | None, holding: set[str],
                       line: str) -> None:
    out = st.evaluate_kill(k1d, k1n, fills, loop, full_d, full_n)
    assert {k for k in ("K1", "K2", "K3") if out[k]["holds"]} == holding
    assert out["verdict"] == ("FAIL" if holding else "PASS")
    assert out["verdict_line"] == line
    assert out["fragile"] == (line == FRAGILE)


CLEAN = (0.95, 1.0, 1.05, 1.0, 1.0)  # clears K1 at 0.264 and at 0.528
PASS_EDGES = (0.45, 0.5, 0.55, 0.5, 0.5)  # clears K1 at 0.264, not at 0.528
LOW = (0.1, 0.3, 0.2, 0.25, 0.3)  # mean 0.23 < 0.264
PASS_LOOPS = (25, 22, 30, 21, 24)


@pytest.mark.parametrize(
    ("edges", "fills", "loops", "dropped", "nodrop", "dropped_nd", "holding", "k1dn", "line"), [
        (CLEAN, 100, PASS_LOOPS, 20, None, 1.0, set(), (False, False), "PASS"),
        (LOW, 100, PASS_LOOPS, 0, CLEAN, 1.0, {"K1"}, (True, False), "FAIL"),  # dropping alone
        (CLEAN, 100, PASS_LOOPS, 0, LOW, 1.0, {"K1"}, (False, True), "FAIL"),  # no-drop alone
        # the dropping variant flatters: the fills it drops are at -10 in the no-drop variant
        (CLEAN, 100, PASS_LOOPS, 20, None, -10.0, {"K1"}, (False, True), "FAIL"),
        (CLEAN, 79, PASS_LOOPS, 0, None, 1.0, {"K2"}, (False, False), "FAIL"),
        # K2 counts fills before any markout drop: 79 valid + 1 without any markout = 80 per date
        (CLEAN, 79, PASS_LOOPS, 1, None, NAN, set(), (False, False), "PASS"),
        (CLEAN, 100, (20, 20, 19, 20, 20), 0, None, 1.0, {"K3"}, (False, False), "FAIL"),
        (PASS_EDGES, 100, PASS_LOOPS, 0, None, 1.0, set(), (False, False), FRAGILE),
        (CLEAN, 100, PASS_LOOPS, 0, PASS_EDGES, 1.0, set(), (False, False), FRAGILE)])
def test_kill_rule_end_to_end_each_test_alone(
        tmp_path: Path, edges: tuple[float, ...], fills: int, loops: tuple[int, ...],
        dropped: int, nodrop: tuple[float, ...] | None, dropped_nd: float, holding: set[str],
        k1dn: tuple[bool, bool], line: str) -> None:
    kr = compute(scenario(tmp_path, edges, fills, loops, dropped, nodrop, dropped_nd))[
        "kill_rule"]
    assert {k for k in ("K1", "K2", "K3") if kr[k]["holds"]} == holding
    assert (kr["K1"]["holds_drop"], kr["K1"]["holds_nodrop"]) == k1dn
    assert kr["verdict"] == ("FAIL" if holding else "PASS")
    assert kr["verdict_line"] == line
    assert kr["K2"]["value"] == 5 * (fills + dropped)
    assert kr["K3"]["value"] == pytest.approx(np.mean(loops))
    assert kr["K1"]["interval_drop"]["n"] == 5 * fills  # dropped markouts are not in K1
    nodrop_valid = dropped if np.isfinite(dropped_nd) else 0
    assert kr["K1"]["interval_nodrop"]["n"] == 5 * (fills + nodrop_valid)
    assert kr["K1"]["interval_drop"]["value"] == pytest.approx(np.mean(edges) - 0.264)
    assert kr["K1"]["lower_drop"] == kr["K1"]["interval_drop"]["ci95"][0]


def test_k1_no_drop_is_a_pooled_ratio_of_sums(tmp_path: Path) -> None:
    kr = compute(scenario(tmp_path, CLEAN, 100, PASS_LOOPS, 20, None, -10.0))["kill_rule"]
    # per date: 100 fills at edges[d] and 20 at -10, pooled over the five dates
    expected = (100 * sum(CLEAN) + 5 * 20 * -10.0) / (5 * 120) - 0.264
    assert kr["K1"]["interval_nodrop"]["value"] == pytest.approx(expected)
    assert kr["K1"]["lower_nodrop"] < 0 < kr["K1"]["lower_drop"]


def test_fragile_label_uses_both_0528_bounds_and_never_decides(tmp_path: Path) -> None:
    kr = compute(scenario(tmp_path, CLEAN, 100, PASS_LOOPS, 0, PASS_EDGES))["kill_rule"]
    info = kr["information_only"]
    assert info["K1_bound_0.528_drop"]["ci95"][0] > 0  # dropping clears 0.528
    assert info["K1_bound_0.528_nodrop"]["value"] == pytest.approx(0.5 - 0.528)
    assert info["K1_bound_0.528_nodrop"]["ci95"][0] < 0  # no-drop does not
    assert (kr["verdict"], kr["fragile"], kr["verdict_line"]) == ("PASS", True, FRAGILE)


# ------------------------------------------------------------------ fees ----
def test_fee_per_fill_is_half_the_round_trip_in_ticks() -> None:
    spec = {"Topstep": 0.264, "Lucid": 0.280, "Bulenox": 0.286, "MFFU": 0.306, "Tradeify": 0.460}
    assert spec == core.FEE_PER_FILL_TICKS
    for firm, rt in core.FEES_RT_USD.items():
        assert rt / 2 / core.ZM_TICK_USD == pytest.approx(spec[firm], abs=1e-12)
    assert pytest.approx(0.528) == st.FULL_RT_TOPSTEP_TICKS


def test_net_edge_and_vpo_for_the_five_firms(tmp_path: Path) -> None:
    cell = compute(scenario(tmp_path, PASS_EDGES, 100, PASS_LOOPS))["cells"]["c"]["ZM.v.0"][
        "DAY"]["pooled"]
    rate = cell["fill_rate"]["value"]
    assert rate == pytest.approx(0.5)
    for h in ("1", "10", "60"):
        hb = cell["horizons"]["drop"][h]
        e = hb["edge_mean"]
        assert e["value"] == pytest.approx(0.5)
        assert hb["markout_mean"]["value"] == pytest.approx(0.0)  # c = 0.5 on every fill
        for firm, fee in core.FEE_PER_FILL_TICKS.items():
            net = hb["net"][firm]
            assert net["mean"]["value"] == pytest.approx(0.5 - fee)
            assert net["mean"]["ci95"] == pytest.approx([e["ci95"][0] - fee, e["ci95"][1] - fee])
            assert net["median"] == pytest.approx(0.5 - fee)
            assert net["vpo"]["value"] == pytest.approx(rate * (0.5 - fee))


# ------------------------------------------------------------------ buckets ----
def test_move_bucket_edges_and_missing() -> None:
    side = np.array([1, 1, 1, -1, -1, 1, 1])
    d = np.array([-0.5, 0.0, 0.5, -0.5, 0.5, NAN, 1e-9])
    assert core.move_bucket(side, d).tolist() == [
        "against", "flat", "with", "with", "against", "missing", "flat"]


def test_joint_bucket_and_missing() -> None:
    zs = np.array(["against", "with", "against", "flat", "missing", "with"], dtype=object)
    zl = np.array(["against", "with", "with", "flat", "against", "missing"], dtype=object)
    assert core.joint_bucket(zs, zl).tolist() == [
        "both against", "both with", "other", "other", "missing", "missing"]


def test_usda_bucket_edges() -> None:
    m = np.array([-30.0, -29.99, -0.01, 0.0, 4.99, 5.0, 29.99, 30.0, 400.0, NAN])
    assert core.usda_bucket(m).tolist() == [
        "other", "pre (-30, 0)", "pre (-30, 0)", "post [0, 5)", "post [0, 5)", "post [5, 30)",
        "post [5, 30)", "other", "other", "other"]  # NaN = no release that date -> other


def test_imbalance_bucket_edges_and_missing() -> None:
    x = np.array([-1.0, -0.99, -0.6, -0.59, -0.2, -0.19, 0.0, 0.19, 0.2, 0.59, 0.6, 0.99, 1.0,
                  NAN, 3 / 5, -(1 / 5)])
    assert core.imb_bucket(x).tolist() == [
        "outside (-1, 1)", "(-1, -0.6]", "(-1, -0.6]", "(-0.6, -0.2]", "(-0.6, -0.2]",
        "(-0.2, 0.2)", "(-0.2, 0.2)", "(-0.2, 0.2)", "[0.2, 0.6)", "[0.2, 0.6)", "[0.6, 1)",
        "[0.6, 1)", "outside (-1, 1)", "missing", "[0.6, 1)", "(-0.6, -0.2]"]


def test_splits_send_missing_moves_to_missing(tmp_path: Path) -> None:
    date = "2024-01-02"
    rows = [fill(date, 0, 1.0, zs_d1=0.5, zl_d1=0.5), fill(date, 1, 2.0, zs_d1=NAN, zl_d1=0.5),
            fill(date, 2, 3.0, side=-1, zs_d1=1.0, zl_d1=-0.5), placement(date, 3, imb=NAN),
            placement(date, 4, imb=0.6)]
    write_day(tmp_path, date, rows)
    sp = compute(tmp_path, boot=100)["splits"]["c"]["ZM.v.0"]["DAY"]
    zs = {b: blk["fills"] for b, blk in sp["ZS L=1 s"].items()}
    assert zs == {"against": 1, "flat": 0, "with": 1, "missing": 1}
    joint = {b: blk["fills"] for b, blk in sp["ZS+ZL L=1 s"].items()}
    # fill 0: with / with; fill 1: ZS missing; fill 2 (a sell): ZS against, ZL with
    assert joint == {"both against": 0, "both with": 1, "other": 1, "missing": 1}
    assert sp["ZS L=1 s"]["missing"]["horizons"]["10"]["edge_mean"]["value"] == pytest.approx(2.0)
    assert "placements" not in sp["ZS L=1 s"]["missing"]  # a fill-time condition
    imb = sp["queue imbalance"]
    assert imb["missing"]["placements"] == 1 and imb["[0.6, 1)"]["placements"] == 1
    assert imb["(-0.2, 0.2)"]["placements"] == 3 and imb["(-0.2, 0.2)"]["fills"] == 3
    assert sp["USDA release"]["other"]["fills"] == 3


# ------------------------------------------------------------------ loop, implied, days ----
def test_loop_distribution_and_mean(tmp_path: Path) -> None:
    loop = compute(scenario(tmp_path, PASS_EDGES, 10, (0, 4, 25, 21, 120)))["loop"]["ZM.v.0"]["c"]
    assert loop["dates"] == 5 and loop["round_trips_total"] == 170
    assert loop["mean"]["value"] == pytest.approx(34.0) and loop["median"] == 21.0
    assert loop["histogram"]["0"] == 1 and loop["histogram"]["1-4"] == 1
    assert loop["histogram"]["20-29"] == 2 and loop["histogram"]["100+"] == 1
    lo, hi = loop["mean"]["ci95"]
    assert 0 <= lo < 34.0 < hi <= 120


def test_implied_shares_and_exclusion_counts(tmp_path: Path) -> None:
    imp = [{"trade_date": _d("2024-01-02"), "symbol": "ZM.v.0", "session": "DAY", "n_ab": 100,
            "vol_ab": 400, "n_none": 5, "vol_none": 40, "n_short": 10, "vol_short": 100,
            "n_n": 2, "vol_n": 6}]
    write_day(tmp_path, "2024-01-02", [placement("2024-01-02", 0)], implied=imp,
              days=day_rows("2024-01-02", ("ZM.v.0",)) + day_rows(
                  "2024-01-02", ("ZM.v.1",), included=False, reason="roll"))
    res = compute(tmp_path, boot=100)
    b = res["implied"]["ZM.v.0"]["DAY"]
    assert b["share_prints_no_resting"]["value"] == pytest.approx(0.05)
    assert b["share_volume_no_resting"]["value"] == pytest.approx(0.10)
    assert b["share_prints_short"]["value"] == pytest.approx(0.10)
    assert b["share_volume_short"]["value"] == pytest.approx(0.25)
    assert b["share_prints_side_n_of_all"]["value"] == pytest.approx(2 / 102)
    assert res["days"]["ZM.v.1"]["excluded_by_reason"] == {"roll": 1}
    assert res["days"]["ZM.v.0"]["included"] == 1


# ------------------------------------------------------------------ CLI and completeness gate ----
def _cli(tmp_path: Path, root: Path, dates: list[str]) -> tuple[int, Path, Path]:
    exp = tmp_path / "expected.txt"
    exp.write_text("\n".join(dates) + "\n")
    out_json, out_md = tmp_path / "out" / "s.json", tmp_path / "out" / "s.md"
    rc = st.main(["--runs", str(root), "--out-json", str(out_json), "--out-md", str(out_md),
                  "--expect-dates", str(exp), "--boot", "300"])
    return rc, out_json, out_md


def test_cli_writes_json_and_markdown_with_the_verdict_first(tmp_path: Path) -> None:
    root = scenario(tmp_path / "runs", CLEAN, 100, PASS_LOOPS)
    write_day(root, "2024-01-09", [placement("2024-01-09", 0)], done=False)  # not expected
    rc, out_json, out_md = _cli(tmp_path, root, list(DATES5))
    assert rc == 0
    res = json.loads(out_json.read_text())
    assert res["kill_rule"]["verdict_line"] == "PASS"
    assert res["meta"]["folders_skipped_no_marker"] == ["2024-01-09"]
    assert res["meta"]["expected_dates"]["count"] == 5
    headings = [ln for ln in out_md.read_text().splitlines() if ln.startswith("## ")]
    assert headings[0] == "## Verdict: PASS"
    assert headings[1].startswith("## Primary population, the three models side by side")


def test_cli_verdict_heading_carries_the_fragile_label(tmp_path: Path,
                                                      capsys: pytest.CaptureFixture[str]) -> None:
    root = scenario(tmp_path / "runs", PASS_EDGES, 100, PASS_LOOPS)
    rc, _, out_md = _cli(tmp_path, root, list(DATES5))
    assert rc == 0
    assert f"## Verdict: {FRAGILE}" in out_md.read_text().splitlines()
    assert capsys.readouterr().out.strip().splitlines()[-1] == f"VERDICT {FRAGILE}"


# ------------------------------------------------------------------ model (a) from 2023-11-01 ----
def _model_a_runs(root: Path, dates: tuple[str, ...]) -> Path:
    """Model (a) fills at E = -5 before 2023-11-01 and E = 2 from it; loops 3 and 7."""
    for date in dates:
        edge, rt = (-5.0, 3) if date < st.MODEL_A_FIRST_DATE else (2.0, 7)
        rows = [fill(date, k, edge, model="a", trigger="queue") for k in range(10)]
        write_day(root, date, [*rows, fill(date, 10, 1.0)],
                  loops=[loop_row(date, rt, "a"), loop_row(date, 25)])
    return root


def test_model_a_block_uses_dates_from_2023_11_01_alone(tmp_path: Path) -> None:
    root = _model_a_runs(tmp_path, ("2023-10-30", "2023-10-31", "2023-11-01", "2023-11-02"))
    res = compute(root)
    blk = res["model_a_from_2023_11_01"]
    assert blk["dates"] == 2 and blk["date_range"] == ["2023-11-01", "2023-11-02"]
    assert set(blk["cells"]) == {"a"}  # model (a) only
    cell = blk["cells"]["a"]["ZM.v.0"]["DAY"]["pooled"]
    mean = cell["horizons"]["drop"]["10"]["edge_mean"]
    assert cell["fills"] == 20 and mean["value"] == pytest.approx(2.0)
    assert mean["ci95"] == pytest.approx([2.0, 2.0])  # earlier dates are not in its pool
    assert blk["loop"]["ZM.v.0"]["a"]["mean"]["value"] == pytest.approx(7.0)
    full = res["cells"]["a"]["ZM.v.0"]["DAY"]["pooled"]["horizons"]["drop"]["10"]["edge_mean"]
    assert full["value"] == pytest.approx(-1.5)  # the main cells keep every date
    assert res["kill_rule"]["verdict"] == "FAIL"  # 4 model (c) fills: the block decides nothing
    text = report.render(st.to_jsonable(res))
    assert "## Model (a), trade dates from 2023-11-01 alone (spec 3.1; decides nothing)" in text


def test_model_a_block_without_dates_from_2023_11_01(tmp_path: Path) -> None:
    res = compute(_model_a_runs(tmp_path, ("2023-10-30", "2023-10-31")), boot=100)
    blk = res["model_a_from_2023_11_01"]
    assert blk["dates"] == 0 and "cells" not in blk and "no done trade date" in blk["note"]
    assert "no done trade date" in report.render(res)


def test_cli_refuses_when_an_expected_date_has_no_done_marker(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = scenario(tmp_path / "runs", PASS_EDGES, 10, PASS_LOOPS)
    (root / DATES5[2] / "DONE").unlink()
    rc, out_json, out_md = _cli(tmp_path, root, list(DATES5))
    assert rc == 2 and not out_json.exists() and not out_md.exists()
    assert "REFUSED" in capsys.readouterr().err


def test_cli_refuses_an_expected_date_without_folder_or_an_unexpected_done_folder(
        tmp_path: Path) -> None:
    root = scenario(tmp_path / "runs", PASS_EDGES, 10, PASS_LOOPS)
    assert _cli(tmp_path, root, [*DATES5, "2024-01-10"])[0] == 2
    assert _cli(tmp_path, root, list(DATES5[:4]))[0] == 2


def test_cli_refuses_a_malformed_expected_dates_file(tmp_path: Path) -> None:
    root = scenario(tmp_path / "runs", PASS_EDGES, 10, PASS_LOOPS)
    assert _cli(tmp_path, root, [*DATES5[:4], "2024-02-30"])[0] == 2
    assert _cli(tmp_path, root, [*DATES5, DATES5[0]])[0] == 2


def test_completeness_gate_lists_missing_and_unexpected(tmp_path: Path) -> None:
    root = tmp_path / "runs"
    write_day(root, "2024-01-02", [placement("2024-01-02", 0)])
    write_day(root, "2024-01-03", [placement("2024-01-03", 0)], done=False)
    gaps = st.completeness(root, ["2024-01-03", "2024-01-04"])
    assert gaps == {"missing": ["2024-01-03", "2024-01-04"], "unexpected": ["2024-01-02"]}


def test_validation_rejects_values_outside_the_interface(tmp_path: Path) -> None:
    write_day(tmp_path, "2024-01-02", [placement("2024-01-02", 0, model="d")])
    with pytest.raises(ValueError, match="model"):
        st.compute_all(st.load_runs(tmp_path), boot=10)


def test_json_has_no_nan(tmp_path: Path) -> None:
    write_day(tmp_path, "2024-01-02", [placement("2024-01-02", 0)])  # no fill anywhere
    res = compute(tmp_path, boot=50)
    text = json.dumps(res, allow_nan=False)  # raises on NaN or inf
    assert "NaN" not in text
    kr = res["kill_rule"]
    assert kr["verdict"] == "FAIL" and kr["K1"]["lower_drop"] is None
    assert kr["K1"]["lower_nodrop"] is None and kr["K1"]["holds"]
