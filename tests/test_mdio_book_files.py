"""mdio.book_files and mdio.trigger_books (Stage E.24, V41; E.23 VerdictVerifier NOTE-5): a
multi-day book writes per-unit and per-fill files in E.21's per-root layout
(multiday.evaluate._root_rows: per_contract_daily_dollars, holdings, fills, counters) plus each
book's units; the trigger-hold adapter returns exactly trigger_hold.evaluate.read_root's records
and the books behind them. Synthetic worlds only (tests.test_multiday_world)."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import replace
from datetime import date, time
from pathlib import Path

import numpy as np
import pytest

from base_rules.store import RunManifest, StoreRefused
from data.config import REPO_ROOT
from data.session import ct_ns
from mdio import book_files as BF
from mdio import trigger_books as TB
from mdio.bounded import BoundBreached, BoundedLoader
from multiday import evaluate as ME
from tests.test_multiday_world import all_cals, ctx_for, walk_prices, window, world_bars
from trigger_hold import constants as K
from trigger_hold.book import prepare_root, unit_book
from trigger_hold.config import parse_config
from trigger_hold.evaluate import read_root
from trigger_hold.types import TriggerEvent, events_record
from trigger_hold.units import BarMarks, Window, build_units


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return all_cals()


def _nq(cals, first: date = date(2016, 1, 4), last: date = date(2016, 12, 30)):  # noqa: ANN001, ANN202
    days = window(cals["equity"], first, last)
    price = walk_prices(days, drift=0.0003, vol=0.01, seed=9)
    bars = world_bars("NQ", days, lambda d: price[d])
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    ctx.last = K.W_EXT_LAST
    return days, bars, ctx


def _events(days) -> list[TriggerEvent]:  # noqa: ANN001
    return [TriggerEvent(days[k], ct_ns(days[k], time(9)), 1 if k % 2 else -1, "X")
            for k in range(70, 240, 3)]


def _roundtrip(obj):  # noqa: ANN001, ANN202
    return json.loads(json.dumps(obj, default=str))


def test_the_per_root_record_has_e21s_layout_plus_units(cals) -> None:
    days, bars, ctx = _nq(cals)
    rd = prepare_root(ctx, bars, "NQ")
    src = BarMarks(ctx, bars, "NQ", rd.path.marks)
    units, _ = build_units(src, _events(days), Window(K.W_EXT, days[0], days[-1]), m=1, h=5)
    book = unit_book(rd, units)
    rec = BF.per_root_record(rd, {"X": book}, {"X": units})
    e21 = ME._root_rows(rd, {"T1": ME.TestOutput("T1", {}, Counter(),
                                                 holdings={"NQ": book.holdings},
                                                 fills={"NQ": book.fills}),
                             "T2": ME.TestOutput("T2", {}, Counter()),
                             "T3": ME.TestOutput("T3", {}, Counter())})
    assert set(e21) <= set(rec) and rec["schema"] == BF.PER_ROOT_SCHEMA
    assert rec["layout"] == e21["schema"]
    for key in ("root", "vehicle", "tick_value_cents", "per_contract_daily_dollars", "counters"):
        assert rec[key] == e21[key], key
    assert rec["holdings"] == {"X": e21["holdings"]["T1"]}
    assert rec["fills"] == {"X": e21["fills"]["T1"]}
    assert len(rec["fills"]["X"]) == len(book.fills) > 10
    assert rec["book_counters"]["X"] == dict(sorted(book.counters.items()))
    rows = rec["units"]["X"]
    assert len(rows) == len(units) > 10
    assert rows[0] == {"d_e": str(units[0].d_e), "d_x": str(units[0].d_x), "u": units[0].u,
                       "trigger_id": "X", "root": "NQ", "d0": str(units[0].d0),
                       "h": units[0].h}


def test_the_record_refuses_books_and_units_that_do_not_match(cals) -> None:
    with pytest.raises(ValueError, match="units"):
        BF.unit_rows([{"d_e": "2016-01-04"}])  # type: ignore[list-item]
    days, bars, ctx = _nq(cals, last=date(2016, 6, 30))
    rd = prepare_root(ctx, bars, "NQ")
    with pytest.raises(ValueError, match="no book"):
        BF.per_root_record(rd, {"X": unit_book(rd, [])}, {"Z": []})


def test_write_per_root_writes_once_and_round_trips(cals, tmp_path) -> None:
    days, bars, ctx = _nq(cals)
    rd = prepare_root(ctx, bars, "NQ")
    src = BarMarks(ctx, bars, "NQ", rd.path.marks)
    units, _ = build_units(src, _events(days), Window(K.W_EXT, days[0], days[-1]), m=-1, h=20)
    rec = BF.per_root_record(rd, {"Y": unit_book(rd, units)}, {"Y": units})
    out = BF.write_per_root(tmp_path / "run", rec)
    assert out == tmp_path / "run" / "per_root" / "NQ.json"
    assert json.loads(out.read_text()) == _roundtrip(rec)
    with pytest.raises(FileExistsError):
        BF.write_per_root(tmp_path / "run", rec)


def _discovery_world(cals, tmp_path: Path):  # noqa: ANN001, ANN202
    days, bars, ctx = _nq(cals)
    evp = tmp_path / "X_NQ__ext.json"
    evp.write_text(json.dumps(events_record("X", "NQ", K.W_EXT, _events(days), {}, {})))
    rows = [{"id": f"E23-X-NQ-h{h}", "trigger_id": "X", "root": "NQ", "m": m, "h": h,
             "s_x": None, "events": {"W_ext": str(evp), "W_cf": None}}
            for h, m in ((5, 1), (20, -1))]
    cfg = parse_config({"schema": K.CONFIG_SCHEMA, "registry_test": "E23", "n_before": 533,
                        "trigger_holds": rows})
    rng = np.random.default_rng(1)
    trend = tmp_path / "trend"
    trend.mkdir()
    (trend / "NQ.json").write_text(json.dumps({
        "schema": K.TREND_SCHEMA, "check": {"T1": {"passed": True}, "T2": {"passed": True}},
        **{f"v_{t}": {str(d): float(rng.normal(0, 1e-3)) for d in days} for t in ("T1", "T2")}}))
    return ctx, cfg, trend


class _BoundedWorld(BoundedLoader):
    """Test double: the synthetic world's in-memory loader passed off as a BoundedLoader bound
    to ``bound`` (these roots have no store). read_root_books refuses any other loader."""

    def __init__(self, inner, bound: date) -> None:  # noqa: ANN001
        super().__init__(RunManifest({}, "0" * 64, "synthetic"), {}, bound)
        self._inner = inner

    def __call__(self, root: str):  # noqa: ANN204
        bars = self._inner(root)
        assert int(bars.td.max()) <= self.bound.toordinal()
        return bars


def _bounded(ctx):  # noqa: ANN001, ANN202
    return replace(ctx, load_bars=_BoundedWorld(ctx.load_bars, ctx.last))


def test_read_root_books_returns_read_roots_records_and_the_books(cals, tmp_path) -> None:
    ctx, cfg, trend = _discovery_world(cals, tmp_path)
    frozen = read_root(ctx, "NQ", cfg.rows, K.W_EXT, trend_dir=trend)
    out, rec = TB.read_root_books(_bounded(ctx), "NQ", cfg.rows, K.W_EXT, trend_dir=trend)
    assert json.dumps(out, sort_keys=True, default=str) == \
        json.dumps(frozen, sort_keys=True, default=str)
    assert rec is not None and set(rec["units"]) == set(cfg.ids)
    for i in cfg.ids:
        assert len(rec["units"][i]) == out[i]["units"]
        assert len(rec["fills"][i]) == out[i]["fill_diagnostics"]["fills"]
        net = sum(f["cost"][K.BASE] for f in rec["fills"][i])
        assert net == pytest.approx(out[i]["gross_costs"][K.BASE]["costs"], rel=1e-12)


def test_a_refused_store_gives_read_roots_record_and_no_file(cals, tmp_path) -> None:
    ctx, cfg, trend = _discovery_world(cals, tmp_path)

    def refused(p: str):  # noqa: ANN202
        raise StoreRefused("synthetic refusal")

    ctx.load_bars = refused
    frozen = read_root(ctx, "NQ", cfg.rows, K.W_EXT, trend_dir=trend)
    out, rec = TB.read_root_books(_bounded(ctx), "NQ", cfg.rows, K.W_EXT, trend_dir=trend)
    assert out == frozen and rec is None
    assert all(r["status"] == "store refused" for r in out.values())


def test_read_root_books_refuses_a_context_that_is_not_bounded_before_any_load(cals,
                                                                               tmp_path) -> None:
    """A2 review SHOULD-FIX-2: the bound is mandatory on this path (mdio.bounded.check_bounded
    first): an unbounded loader, or ctx.last moved after binding, stops the read with
    BoundBreached (never an exclusion) before any bar is loaded."""
    ctx, cfg, trend = _discovery_world(cals, tmp_path)
    asked: list[str] = []
    inner = ctx.load_bars

    def spy(root: str):  # noqa: ANN202
        asked.append(root)
        return inner(root)

    ctx.load_bars = spy
    with pytest.raises(BoundBreached, match="not bounded"):
        TB.read_root_books(ctx, "NQ", cfg.rows, K.W_EXT, trend_dir=trend)
    moved = _bounded(ctx)
    moved.last = date(2016, 6, 30)
    with pytest.raises(BoundBreached, match="not ctx.last"):
        TB.read_root_books(moved, "NQ", cfg.rows, K.W_EXT, trend_dir=trend)
    assert asked == []
    TB.read_root_books(_bounded(ctx), "NQ", cfg.rows, K.W_EXT, trend_dir=trend)
    assert asked == ["NQ"]


def test_the_mirror_is_pinned_to_the_frozen_read_root() -> None:
    """mdio.trigger_books mirrors trigger_hold.evaluate.read_root; a change to the frozen file
    (E.23 freeze) must fail here so the mirror is reviewed."""
    for rel, want in TB.MIRRORED_SHA256.items():
        got = hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()
        assert got == want, rel
