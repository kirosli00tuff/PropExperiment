"""trigger_hold.run, config and freeze_manifest: the run-once marker (written BEFORE the
computation, a second run refused with exit 2, a stop after the marker exit 1), output-path
refusal, the config schema, the freeze build / verify / tamper refusal, the power row from a
calendar-only source and addition (a)/(c) (series from the first unit, in-market fraction)."""

from __future__ import annotations

import argparse
import json
from datetime import date, time
from pathlib import Path

import pytest

from data.session import ct_ns
from tests.test_multiday_world import all_cals, ctx_for, walk_prices, window, world_bars
from trigger_hold import constants as K
from trigger_hold import freeze_manifest as FM
from trigger_hold import run as R
from trigger_hold.book import buy_hold_returns, prepare_root
from trigger_hold.config import ConfigError, parse_config
from trigger_hold.power import power_row
from trigger_hold.types import TriggerEvent, events_record
from trigger_hold.units import (
    BarMarks,
    CalendarMarks,
    Unit,
    Window,
    book_days,
    build_units,
    in_market_fraction,
)


class _Cfg:
    ids = ["E23-X-h5"]


def _args(tmp: Path, phase: str = "discovery") -> argparse.Namespace:
    return argparse.Namespace(phase=phase, freeze="f", freeze_sha256="0" * 64,
                              out_dir=str(tmp / "out"), marker=str(tmp / "marker.json"))


def _pre(tmp: Path):  # noqa: ANN202
    def fn(a):  # noqa: ANN001, ANN202
        R.check_output_free(Path(a.marker), Path(a.out_dir), a.phase)
        return {"cfg": _Cfg(), "registration": "r", "registry": {}, "manifest_sha256": "m",
                "stores": [], "out_dir": Path(a.out_dir), "marker": Path(a.marker)}
    return fn


def test_the_marker_is_written_before_any_computation_and_a_second_run_is_refused(tmp_path):
    a = _args(tmp_path)
    seen = []

    def compute(pre, phase):  # noqa: ANN001, ANN202
        seen.append(Path(a.marker).is_file())
        return {"phase": phase, "x": 1}

    assert R.run_phase(a, pre_fn=_pre(tmp_path), compute_fn=compute) == K.RC_OK
    assert seen == [True]
    rec = json.loads((tmp_path / "out" / "discovery_result.json").read_text())
    assert rec["status"] == "complete" and rec["phase"] == "discovery"
    assert R.run_phase(a, pre_fn=_pre(tmp_path), compute_fn=compute) == K.RC_REFUSED
    assert seen == [True]  # the second run computed nothing


def test_a_marker_present_without_a_result_still_refuses(tmp_path) -> None:
    a = _args(tmp_path)
    R.write_marker(Path(a.marker), {"x": 1})
    with pytest.raises(R.Refused):
        R.write_marker(Path(a.marker), {"x": 2})
    assert R.run_phase(a, pre_fn=_pre(tmp_path), compute_fn=lambda p, ph: {}) == K.RC_REFUSED


def test_an_error_after_the_marker_stops_with_exit_1(tmp_path) -> None:
    a = _args(tmp_path, "confirmation")

    def boom(pre, phase):  # noqa: ANN001, ANN202
        raise ValueError("synthetic")

    assert R.run_phase(a, pre_fn=_pre(tmp_path), compute_fn=boom) == K.RC_STOPPED
    stop = json.loads((tmp_path / "out" / "STOPPED.json").read_text())
    assert stop["status"] == "STOPPED" and Path(a.marker).is_file()
    assert R.run_phase(a, pre_fn=_pre(tmp_path), compute_fn=boom) == K.RC_REFUSED


def test_a_refused_precondition_writes_nothing(tmp_path) -> None:
    a = _args(tmp_path)

    def refuse(_a):  # noqa: ANN001, ANN202
        raise R.Refused("no")

    assert R.run_phase(a, pre_fn=refuse, compute_fn=lambda p, ph: {}) == K.RC_REFUSED
    assert not Path(a.marker).exists() and not (tmp_path / "out").exists()


def test_a_taken_output_path_refuses(tmp_path) -> None:
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "discovery_result.json").write_text("{}")
    with pytest.raises(R.Refused):
        R.check_output_free(tmp_path / "m.json", tmp_path / "out", "discovery")


def test_fixed_paths_outside_the_test_mode(tmp_path) -> None:
    with pytest.raises(R.Refused):
        R._fixed_paths(_args(tmp_path), test_mode=False)


def test_the_test_mode_refuses_the_real_run_manifest(tmp_path, monkeypatch) -> None:
    # review C-01: --input-paths '{}' must not reach the real stores without the real marker
    (tmp_path / "paths.json").write_text("{}")
    a = _args(tmp_path)
    a.input_paths = str(tmp_path / "paths.json")
    real = {"path": str(K.repo_path(K.RUN_MANIFEST_PATH)), "sha256": "0" * 64}
    monkeypatch.setattr(R.FM, "verify", lambda *_a, **_k: {"inputs": {"run_manifest": real}})
    with pytest.raises(R.Refused, match="C-01"):
        R.preconditions(a)


# ------------------------------------------------------------------ config ----
def _cfg_row(**kw) -> dict:
    row = {"id": "E23-K2-ZF-h5", "trigger_id": "K2-monthend-01", "root": "ZF", "m": 1, "h": 5,
           "s_x": None, "events": {"W_ext": "a.json", "W_cf": None}}
    return {**row, **kw}


def _cfg(rows) -> dict:  # noqa: ANN001
    return {"schema": K.CONFIG_SCHEMA, "registry_test": "E23", "n_before": 533,
            "trigger_holds": rows}


def test_the_config_schema() -> None:
    cfg = parse_config(_cfg([_cfg_row(), _cfg_row(id="E23-NQ-h20", trigger_id="E20H6-T1",
                                                    root="NQ", m=-1, h=20)]))
    assert cfg.ids == ["E23-K2-ZF-h5", "E23-NQ-h20"] and cfg.roots == ["NQ", "ZF"]
    for bad in (_cfg_row(h=10), _cfg_row(m=0), _cfg_row(root="ES"), _cfg_row(id="E21-x"),
                {**_cfg_row(), "pnl": 1}, _cfg_row(events={"W_ext": None, "W_cf": None})):
        with pytest.raises(ConfigError):
            parse_config(_cfg([bad]))
    with pytest.raises(ConfigError):
        parse_config(_cfg([_cfg_row(), _cfg_row()]))
    with pytest.raises(ConfigError):
        parse_config(_cfg([_cfg_row(id=f"E23-{i}", h=5 if i % 2 else 20, m=1 if i < 13 else -1,
                                    trigger_id=f"T{i}") for i in range(25)]))


# ------------------------------------------------------------------ freeze ----
def test_the_freeze_builds_verifies_and_refuses_a_changed_file(tmp_path) -> None:
    ev = tmp_path / "ev.json"
    ev.write_text(json.dumps(events_record("T", "ZF", K.W_EXT, [], {}, {})))
    cfgp = tmp_path / "config.json"
    cfgp.write_text(json.dumps(_cfg([_cfg_row(events={"W_ext": str(ev), "W_cf": None})])))
    extra = {}
    for role in ("spec", "prereg", "power"):
        p = tmp_path / f"{role}.txt"
        p.write_text(role)
        extra[role] = str(p)
    trend = tmp_path / "trend"
    trend.mkdir()
    for r in K.ROOTS:
        (trend / f"{r}.json").write_text("{}")
    inputs = FM.resolve_inputs({**extra, "config": str(cfgp)})
    out = FM.build(tmp_path / "freeze.json", inputs, trend_dir=trend)
    from base_rules.guards import sha256_file

    sha = sha256_file(out)
    got = FM.verify(out, sha)
    assert got["test_ids"] == ["E23-K2-ZF-h5"]
    with pytest.raises(FileExistsError):
        FM.build(out, inputs, trend_dir=trend)
    ev.write_text(ev.read_text() + " ")
    with pytest.raises(FM.FreezeRefused):
        FM.verify(out, sha)
    with pytest.raises(FM.FreezeRefused):
        FM.verify(out, "f" * 64)


# ------------------------------------------------------------------ power on a calendar ----
@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return all_cals()


def test_power_row_from_calendars_only_and_the_series_start_at_the_first_unit(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    bars = world_bars("NQ", days, lambda d: 100)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    src = CalendarMarks(ctx, "NQ", frozenset())
    assert list(src.mark_days())[: len(days)] == days
    win = Window(K.W_EXT, days[0], days[-1])
    evs = [TriggerEvent(days[k], ct_ns(days[k], time(9, 0)), 1, "X") for k in (40, 42, 60)]
    row = power_row(src, evs, win, m=-1, h=5, k_family=5)
    assert row["units"] == 3 and row["nonoverlapping"] == 2
    assert row["first_book_date"] == str(days[40])
    assert row["n_dates"] == len([d for d in days if days[40] <= d])
    # in market on (d_e, d_x]: days 41..47 (units 40-45 and 42-47 overlap) and 61..65
    assert row["in_market_fraction"] == pytest.approx(12 / row["n_dates"])
    assert row["inconclusive_by_design"]  # 2 non-overlapping events


def test_in_market_fraction_counts_the_clip_zero() -> None:
    ds = [date(2016, 1, d) for d in range(4, 16)]
    units = [Unit(ds[0], ds[4], 1, "X", "NQ", ds[0], 4),
             Unit(ds[0], ds[2], -1, "X", "NQ", ds[0], 2)]
    # ds1, ds2: +1 - 1 = 0; ds3, ds4: +1
    assert in_market_fraction(units, ds) == pytest.approx(2 / 12)
    assert in_market_fraction([], []) is None


def test_book_days_and_buy_hold_returns_on_bars(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    price = walk_prices(days, drift=0.0, vol=0.01, seed=2)
    bars = world_bars("NQ", days, lambda d: price[d])
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = prepare_root(ctx, bars, "NQ")
    src = BarMarks(ctx, bars, "NQ", rd.path.marks)
    win = Window(K.W_EXT, days[0], days[-1])
    units, _ = build_units(src, [TriggerEvent(days[90], ct_ns(days[90], time(9)), 1, "X")], win,
                           m=1, h=5)
    assert book_days(src, win, units)[0] == days[90] and book_days(src, win, []) == []
    from collections import Counter

    bh = buy_hold_returns(rd, Counter())
    for k in (10, 50, 120):
        assert bh[days[k]] == pytest.approx(price[days[k]] / price[days[k - 1]] - 1.0)


# ------------------------------------------------------------------ discovery end to end ----
def test_discovery_end_to_end_on_a_synthetic_root(cals, tmp_path) -> None:
    import numpy as np

    from trigger_hold.config import load_config
    from trigger_hold.evaluate import discovery, survivors_from

    days = window(cals["equity"], date(2016, 1, 4), date(2016, 12, 30))
    price = walk_prices(days, drift=0.0003, vol=0.01, seed=9)
    bars = world_bars("NQ", days, lambda d: price[d])
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    ctx.last = K.W_EXT_LAST
    evs = [TriggerEvent(days[k], ct_ns(days[k], time(9)), 1 if k % 2 else -1, "X")
           for k in range(70, 240, 3)]
    evp = tmp_path / "X_NQ__ext.json"
    evp.write_text(json.dumps(events_record("X", "NQ", K.W_EXT, evs, {}, {})))
    rows = [{"id": f"E23-X-NQ-h{h}", "trigger_id": "X", "root": "NQ", "m": m, "h": h,
             "s_x": None, "events": {"W_ext": str(evp), "W_cf": None}}
            for h, m in ((5, 1), (20, -1))]
    cfgp = tmp_path / "config.json"
    cfgp.write_text(json.dumps(_cfg(rows)))
    cfg = load_config(cfgp)
    rng = np.random.default_rng(1)
    trend = tmp_path / "trend"
    trend.mkdir()
    (trend / "NQ.json").write_text(json.dumps({
        "schema": K.TREND_SCHEMA, "check": {"T1": {"passed": True}, "T2": {"passed": True}},
        **{f"v_{t}": {str(d): float(rng.normal(0, 1e-3)) for d in days} for t in ("T1", "T2")}}))
    power = {"rows": {i: {K.W_EXT: {"inconclusive_by_design": False}, K.W_CF: None}
                      for i in cfg.ids}}
    res = discovery(ctx, cfg, power, 538, trend_dir=trend)
    for i in cfg.ids:
        rec = res["trigger_holds"][i]
        assert rec["status"] == "read" and rec["units"] > 10
        base = rec["cases"][K.BASE]
        assert base["alpha"]["p_alpha"] is not None and "alpha3_descriptive" in base
        first = rec["series"][K.BASE][0][0]
        assert first == str(days[70])  # the first unit's entry mark date (addition (a))
        assert rec["n_dates"] == len(rec["series"][K.BASE])
        stress = rec["gross_costs"][K.STRESS]["costs"]
        assert stress > rec["gross_costs"][K.BASE]["costs"] > 0
    assert res["screen"]["k"] == 2 and res["pbo_descriptive"]["n_strategies"] == 2
    assert res["dsr_descriptive"]["n_trials"] == 538
    disc = {**res, "status": "complete"}
    assert survivors_from(disc, cfg) == res["screen"]["survivors"]
    power2 = {"rows": {cfg.ids[0]: {K.W_EXT: {"inconclusive_by_design": True}, K.W_CF: None},
                       cfg.ids[1]: {K.W_EXT: {"inconclusive_by_design": False}, K.W_CF: None}}}
    res2 = discovery(ctx, cfg, power2, 538, trend_dir=trend)
    assert res2["trigger_holds"][cfg.ids[0]]["status"] == K.INCONCLUSIVE
    assert not res2["screen"]["checks"][cfg.ids[0]]["holm_rejects"]


def test_the_confirmation_gate() -> None:
    from trigger_hold.config import TriggerHold
    from trigger_hold.evaluate import confirmation_gate

    th = TriggerHold("E23-A", "A", "NQ", 1, 5, None, {K.W_EXT: "x", K.W_CF: "y"})
    none = TriggerHold("E23-B", "A", "NQ", 1, 5, None, {K.W_EXT: "x", K.W_CF: None})
    pw = {"rows": {"E23-A": {K.W_CF: {"n_dates": 1953, "nonoverlapping": 40}},
                   "E23-B": {K.W_CF: None}}}
    assert confirmation_gate(none, pw, 1)[0] == K.UNCONFIRMABLE
    g, info = confirmation_gate(th, pw, 1)  # b = 2.0: power 0.272
    assert g == "read" and info["power_at_hurdle"] == pytest.approx(0.2716, abs=1e-3)
    assert confirmation_gate(th, pw, 4)[0] == K.INCONCLUSIVE  # b = 2.24: power < 0.2
    pw["rows"]["E23-A"][K.W_CF] = {"n_dates": 1953, "nonoverlapping": 29}
    assert confirmation_gate(th, pw, 1)[0] == K.INCONCLUSIVE
    pw["rows"]["E23-A"][K.W_CF] = {"n_dates": 1187, "nonoverlapping": 55}
    assert confirmation_gate(th, pw, 1)[0] == K.INCONCLUSIVE  # 0.18 < 0.2
