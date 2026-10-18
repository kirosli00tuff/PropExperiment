"""mdio.bounded (Stage E.24, V41): a multi-day read loads each store only through the read
window's last trade date (the bound, ctx.last). Synthetic stores in base_rules.store's real
layouts and the frozen booking:

- with the bound at or after the last date, the bars equal base_rules.store.load_product's;
- a store whose name puts its first date after the bound is never opened (deleted here);
- rows after a mid-era bound are never returned; row groups wholly after it are never decoded
  (spied); a straddling row group is filtered before any table reaches pandas;
- the bound is asserted (a kept row after it raises BoundBreached, which load_or_exclude never
  swallows); the input refusals still apply;
- results of the frozen multi-day book (multiday.book via trigger_hold.book) are equal with and
  without the bound.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from base_rules import constants as BK
from base_rules import hist_plan as HP
from base_rules import store as S
from base_rules.calendars import load_calendars
from base_rules.common import load_or_exclude
from base_rules.context import empty_release_rules, make_context
from data.stage_e_bars import ParquetHashMismatch, StageEBarRefusal, TradeDateMismatch
from mdio import bounded as B
from mdio.book_files import per_root_record
from tests._base_rules_fixtures import ns, settlement, store_frame, store_rows, trade_dates
from trigger_hold.book import prepare_root, unit_book
from trigger_hold.units import Unit

ROOT = "ZN"
MINUTES = (13 * 60 + 59, 14 * 60)  # S - 1 and S of the rates group (fixtures' SM)
SPLICE = int(datetime(2019, 4, 12, tzinfo=UTC).timestamp()) * 10**9  # 19:00 CT on 04-11
HIST_FIRST = date(2018, 11, 1)
STEP2_LAST = date(2019, 5, 31)


@pytest.fixture(scope="module")
def gcal():  # noqa: ANN201
    return load_calendars(("rates",))["rates"]


@pytest.fixture(scope="module")
def eras(gcal):  # noqa: ANN001, ANN201
    return {S.EXT2010: gcal.hist, S.STEP2_ERA: gcal.frozen}


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _write(base: Path, era: str, rows: list, meta: dict, row_group_rows: int | None,
           null_rows: tuple[int, ...] = ()) -> S.StoreRef:
    """base_rules.store's layouts, written like data.build_mes_bars._write_read_only_parquet
    (trade_date as text, the propexperiment metadata) with a chosen row-group size; the rows at
    ``null_rows`` (file positions) carry no trade_date label (a corrupt store)."""
    plan = BK.HIST_PLAN_OF[ROOT]
    out = (base / plan / ROOT / HP.expected_name(ROOT, plan, BK.PROMPT_FIRST, BK.HIST_LAST)
           if era == S.EXT2010 else base / "step2" / ROOT / S.step2_name(ROOT))
    frame = store_frame(ROOT, rows)
    labels = frame["trade_date"].astype(str)
    if null_rows:
        labels = labels.astype(object)
        labels.iloc[list(null_rows)] = None
    table = pa.Table.from_pandas(frame.assign(trade_date=labels), preserve_index=False)
    table = table.replace_schema_metadata({**(table.schema.metadata or {}),
                                           b"propexperiment": json.dumps(meta).encode()})
    out.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, out, row_group_size=row_group_rows)
    return S.StoreRef(out, _sha(out), plan if era == S.EXT2010 else None)


def _world(tmp: Path, gcal, *, hist_rg: int | None = None,  # noqa: ANN001
           step2_symbol: str = "Z9", nulls: dict[str, tuple[int, ...]] | None = None
           ) -> tuple[dict, list[date], list[date]]:
    hd = trade_dates(gcal, HIST_FIRST, BK.HIST_LAST)
    sd = trade_dates(gcal, BK.STEP2_FIRST, STEP2_LAST)
    rng = np.random.default_rng(7)
    level = 8000 + np.cumsum(rng.integers(-9, 10, size=len(hd) + len(sd)))
    price = {ns(d, m): int(level[k]) + j for k, d in enumerate([*hd, *sd])
             for j, m in enumerate(MINUTES)}
    hist_rows = store_rows(ROOT, gcal.hist, hd, MINUTES, lambda t: "M9" if t < SPLICE else "U9",
                           lambda t: price[t])
    meta = {"plan": BK.HIST_PLAN_OF[ROOT], "hist_calendar": {"sha256": gcal.hist.file_sha256},
            "trade_date_range": [str(hd[0]), str(hd[-1])],
            "rolls": [{"ts_ns": SPLICE, "from_raw_symbol": "M9", "to_raw_symbol": "U9"}]}
    s_rows = store_rows(ROOT, gcal.frozen, sd, MINUTES, lambda t: step2_symbol,
                        lambda t: price[t])
    nulls = nulls or {}
    refs = {S.EXT2010: _write(tmp, S.EXT2010, hist_rows, meta, hist_rg,
                              nulls.get(S.EXT2010, ())),
            S.STEP2_ERA: _write(tmp, S.STEP2_ERA, s_rows, {"rolls": []}, None,
                                nulls.get(S.STEP2_ERA, ()))}
    return refs, hd, sd


ARRAYS = ("ts", "open_t", "close_t", "usable", "td", "high_t", "low_t", "volume", "no_new")


def _assert_same(a: S.ProductBars, b: S.ProductBars) -> None:
    assert a.root == b.root
    for name in (*ARRAYS, "sym"):
        x, y = getattr(a, name), getattr(b, name)
        assert x.dtype == y.dtype and np.array_equal(x, y), name
    assert a.symbols == b.symbols and a.splices == b.splices and a.blackout == b.blackout
    assert a.records == b.records


def _assert_restricted(full: S.ProductBars, got: S.ProductBars, bound: date) -> None:
    keep = full.td <= bound.toordinal()
    for name in ARRAYS:
        assert np.array_equal(getattr(full, name)[keep], getattr(got, name)), name
    assert [full.contract(i) for i in np.flatnonzero(keep)] == \
        [got.contract(i) for i in range(len(got.ts))]


def _manifest(refs: dict) -> S.RunManifest:
    return S.RunManifest({ROOT: refs}, "0" * 64, "synthetic")


# ------------------------------------------------------------------ equality ----
def test_with_the_bound_at_or_after_the_last_date_the_bars_equal_load_product(tmp_path, gcal,
                                                                               eras) -> None:
    refs, _, sd = _world(tmp_path, gcal)
    full = S.load_product(ROOT, refs, eras)
    for bound in (sd[-1], BK.WINDOW_LAST):
        got, loads = B.load_product_bounded(ROOT, refs, eras, bound)
        _assert_same(full, got)
        assert [ld.era for ld in loads] == [S.EXT2010, S.STEP2_ERA]
        assert not any(ld.skipped for ld in loads)


def test_the_reader_equals_the_frozen_reader_without_a_bound(tmp_path, gcal) -> None:
    refs, _, _ = _world(tmp_path, gcal, hist_rg=40)
    for era in S.ERAS:
        path = Path(refs[era].path)
        mine, stats = B.read_bounded(path, BK.WINDOW_LAST)
        ref = S._read(path)  # the frozen reader (base_rules.store)
        for col in ("raw_symbol", "trade_date"):
            assert isinstance(mine[col].dtype, pd.CategoricalDtype)
            mine[col] = mine[col].astype(str)
            ref[col] = ref[col].astype(str)
        pd.testing.assert_frame_equal(mine, ref)
        assert stats["rows_decoded"] == stats["rows_kept"] == len(ref)


# ------------------------------------------------------------------ the bound ----
def test_with_the_bound_at_the_era_end_the_step2_store_is_never_opened(tmp_path, gcal,
                                                                        eras) -> None:
    refs, hd, _ = _world(tmp_path, gcal)
    expected = S.load_product(ROOT, {S.EXT2010: refs[S.EXT2010], S.STEP2_ERA: None}, eras)
    step2 = Path(refs[S.STEP2_ERA].path)
    step2.chmod(0o644)
    step2.unlink()  # any open, hash or metadata read of it would raise
    gone = {**refs, S.STEP2_ERA: S.StoreRef(step2, "f" * 64)}
    got, loads = B.load_product_bounded(ROOT, gone, eras, BK.HIST_LAST)
    _assert_same(expected, got)
    assert int(got.td.max()) == hd[-1].toordinal()
    by_era = {ld.era: ld for ld in loads}
    assert by_era[S.STEP2_ERA].skipped and by_era[S.STEP2_ERA].rows_decoded == 0
    assert by_era[S.STEP2_ERA].row_groups_read == ()
    assert by_era[S.EXT2010].max_trade_date == str(BK.HIST_LAST)


def test_rows_after_a_mid_era_bound_are_never_returned(tmp_path, gcal, eras) -> None:
    refs, hd, _ = _world(tmp_path, gcal)
    full = S.load_product(ROOT, refs, eras)
    bound = hd[60]
    got, loads = B.load_product_bounded(ROOT, refs, eras, bound)
    _assert_restricted(full, got, bound)
    assert int(got.td.max()) == bound.toordinal()
    assert got.splices == full.splices and got.blackout == full.blackout
    assert got.records[0]["rows"] == int((full.td <= bound.toordinal()).sum())
    assert [r["era"] for r in got.records] == [S.EXT2010]
    assert {ld.era: ld.skipped for ld in loads} == {S.EXT2010: False, S.STEP2_ERA: True}


def test_a_bound_inside_the_step2_era_loads_and_truncates_the_step2_store(tmp_path, gcal,
                                                                          eras) -> None:
    """A2 review NOTE-3: a bound inside 2019-05-06..2024-02-29 opens the step 2 store and keeps
    only its rows through the bound (data.stage_e_bars.check_bookings on the kept rows)."""
    refs, hd, sd = _world(tmp_path, gcal)
    full = S.load_product(ROOT, refs, eras)
    bound = sd[10]
    got, loads = B.load_product_bounded(ROOT, refs, eras, bound)
    _assert_restricted(full, got, bound)
    assert int(got.td.max()) == bound.toordinal()
    assert got.splices == full.splices and got.blackout == full.blackout
    assert [r["era"] for r in got.records] == [S.EXT2010, S.STEP2_ERA]
    step2 = next(ld for ld in loads if ld.era == S.STEP2_ERA)
    in_step2 = int(((full.td > hd[-1].toordinal()) & (full.td <= bound.toordinal())).sum())
    assert not step2.skipped and step2.straddling == (0,)
    assert step2.max_trade_date == str(bound)
    assert step2.rows_kept == got.records[1]["rows"] == in_step2
    assert 0 < step2.rows_kept < step2.rows_decoded == step2.rows_in_file


class _Spy:
    """Records the row groups pyarrow is asked to decode and the latest trade date of every table
    mdio.bounded hands to pandas (its single conversion point); refuses any whole-file read."""

    def __init__(self, monkeypatch) -> None:  # noqa: ANN001
        self.groups: list[int] = []
        self.to_pandas_max: list[str] = []
        orig_iter = pq.ParquetFile.iter_batches
        orig_to_frame = B._to_frame

        def iter_batches(pf, *a, **k):  # noqa: ANN001, ANN202
            self.groups.extend(k.get("row_groups") or [])
            return orig_iter(pf, *a, **k)

        def to_frame(table):  # noqa: ANN001, ANN202
            col = table.column("trade_date").cast(pa.large_string())
            self.to_pandas_max.append(max(col.to_pylist()))
            return orig_to_frame(table)

        def refuse(*a, **k):  # noqa: ANN002, ANN003, ANN202
            raise AssertionError("a whole-file read")

        monkeypatch.setattr(pq.ParquetFile, "iter_batches", iter_batches)
        monkeypatch.setattr(B, "_to_frame", to_frame)  # pa.Table is immutable: spy the hook
        monkeypatch.setattr(pq.ParquetFile, "read", refuse)
        monkeypatch.setattr(pq.ParquetFile, "read_row_groups", refuse)
        monkeypatch.setattr(pq, "read_table", refuse)


def test_row_groups_wholly_after_the_bound_are_never_decoded(tmp_path, gcal, eras,
                                                             monkeypatch) -> None:
    refs, hd, _ = _world(tmp_path, gcal, hist_rg=20)  # 10 trade dates per row group
    bound = hd[29]  # the last date of row group 2
    spy = _Spy(monkeypatch)
    got, loads = B.load_product_bounded(ROOT, refs, eras, bound)
    n_groups = pq.ParquetFile(refs[S.EXT2010].path).metadata.num_row_groups
    assert n_groups > 5
    assert spy.groups == [0, 1, 2]
    hist = next(ld for ld in loads if ld.era == S.EXT2010)
    assert hist.row_groups_read == (0, 1, 2) and hist.straddling == ()
    assert hist.row_groups_total == n_groups
    assert hist.rows_decoded == hist.rows_kept == 60
    assert max(spy.to_pandas_max) == str(bound)
    assert int(got.td.max()) == bound.toordinal()


def test_a_straddling_row_group_is_filtered_before_rows_reach_pandas(tmp_path, gcal, eras,
                                                                     monkeypatch) -> None:
    refs, hd, _ = _world(tmp_path, gcal, hist_rg=20)
    full = S.load_product(ROOT, refs, eras)
    bound = hd[24]  # inside row group 2
    spy = _Spy(monkeypatch)
    got, loads = B.load_product_bounded(ROOT, refs, eras, bound)
    hist = next(ld for ld in loads if ld.era == S.EXT2010)
    assert spy.groups == [0, 1, 2]
    assert hist.straddling == (2,) and hist.rows_decoded == 60 and hist.rows_kept == 50
    assert max(spy.to_pandas_max) <= str(bound)
    _assert_restricted(full, got, bound)


def test_a_kept_row_after_the_bound_raises_a_breach_that_is_never_swallowed(
        tmp_path, gcal, eras, monkeypatch) -> None:
    refs, hd, _ = _world(tmp_path, gcal, hist_rg=20)
    monkeypatch.setattr(B, "_keep_mask", lambda batch, bound_iso: np.ones(batch.num_rows,
                                                                            dtype=bool))
    with pytest.raises(B.BoundBreached):
        B.load_product_bounded(ROOT, refs, eras, hd[24])
    assert not issubclass(B.BoundBreached, StageEBarRefusal)
    ctx = make_context({"rates": gcal}, settlement(), {ROOT: HIST_FIRST},
                       B.BoundedLoader(_manifest(refs), {"rates": gcal}, hd[24]), (),
                       empty_release_rules())
    with pytest.raises(B.BoundBreached):
        load_or_exclude(ctx, ROOT, Counter(), {})


def test_the_bound_check_refuses_any_later_label_or_booking() -> None:
    days = (date(2019, 4, 29), date(2019, 4, 30))
    B.check_bound(days, np.array(["2019-04-29", "2019-04-30"]), date(2019, 4, 30), "w")
    with pytest.raises(B.BoundBreached):
        B.check_bound(days, np.array(["2019-04-29", "2019-04-30"]), date(2019, 4, 29), "w")
    with pytest.raises(B.BoundBreached):
        B.check_bound(days[:1], np.array(["2019-05-06"]), date(2019, 4, 30), "w")


# ------------------------------------------------------------------ context ----
def test_the_bounded_context_reads_through_ctx_last_and_leaves_the_original_unchanged(
        tmp_path, gcal, eras) -> None:
    refs, _, _ = _world(tmp_path, gcal)
    full_loader = lambda p: S.load_product(p, refs, eras)  # noqa: E731
    ctx = make_context({"rates": gcal}, settlement(), {ROOT: HIST_FIRST}, full_loader, (),
                       empty_release_rules())
    ctx.last = BK.HIST_LAST
    ctx_b, loader = B.bound_context(ctx, _manifest(refs))
    assert ctx_b is not ctx and ctx.load_bars is full_loader and ctx_b.load_bars is loader
    assert ctx_b.last == ctx.last and ctx_b.starts == ctx.starts
    bars = ctx_b.load_bars(ROOT)
    assert int(bars.td.max()) <= BK.HIST_LAST.toordinal()
    assert loader.bound == BK.HIST_LAST
    assert [(ld.era, ld.skipped) for ld in loader.loads] == [(S.EXT2010, False),
                                                             (S.STEP2_ERA, True)]
    assert loader.max_trade_date_loaded() == str(BK.HIST_LAST)
    assert B.check_bounded(ctx_b) is loader
    with pytest.raises(B.BoundBreached, match="not bounded"):
        B.check_bounded(ctx)
    ctx_b.last = BK.WINDOW_LAST  # moved after binding: refused
    with pytest.raises(B.BoundBreached, match="not ctx.last"):
        B.check_bounded(ctx_b)


def test_input_refusals_still_apply(tmp_path, gcal, eras) -> None:
    refs, hd, _ = _world(tmp_path, gcal)
    bad = {**refs, S.EXT2010: S.StoreRef(refs[S.EXT2010].path, "0" * 64, refs[S.EXT2010].plan)}
    with pytest.raises(ParquetHashMismatch):
        B.load_product_bounded(ROOT, bad, eras, BK.HIST_LAST)
    sealed = tmp_path / "sealed" / ROOT / S.step2_name(ROOT)
    with pytest.raises(S.StoreRefused, match="sealed"):  # refused even though it is skipped
        B.load_product_bounded(ROOT, {**refs, S.STEP2_ERA: S.StoreRef(sealed, "0" * 64)}, eras,
                               BK.HIST_LAST)
    with pytest.raises(S.StoreRefused, match="no store row"):
        B.load_product_bounded(ROOT, refs, eras, date(2018, 10, 31))
    with pytest.raises(TypeError):
        B.load_product_bounded(ROOT, refs, eras, "2019-04-30")  # type: ignore[arg-type]


@pytest.mark.parametrize(("era", "row", "bound_at"), [
    (S.EXT2010, 7, ("hist", 29)),     # in a row group decoded in full
    (S.EXT2010, 201, ("hist", 29)),   # in a row group whose labelled rows are all after the bound
    (S.STEP2_ERA, 5, ("step2", 10)),  # before the bound in the straddling step 2 group
    (S.STEP2_ERA, 31, ("step2", 10)),  # after the bound in it
])
def test_a_row_with_no_trade_date_label_is_refused_as_the_frozen_path_refuses_it(
        tmp_path, gcal, eras, era, row, bound_at) -> None:
    """A2 review SHOULD-FIX-1: the frozen read_era keeps a null-labelled row and its booking
    check refuses the store (TradeDateMismatch); the bounded read refuses it the same way
    (same class, same message, so load_or_exclude excludes and counts it identically) instead
    of dropping the row, wherever the row sits relative to the bound."""
    refs, hd, sd = _world(tmp_path, gcal, hist_rg=20, nulls={era: (row,)})
    bound = (hd if bound_at[0] == "hist" else sd)[bound_at[1]]
    ctx = make_context({"rates": gcal}, settlement(), {ROOT: HIST_FIRST},
                       lambda p: S.load_product(p, refs, eras), (), empty_release_rules())
    ctx.last = bound
    ctx_b, _ = B.bound_context(ctx, _manifest(refs))
    got = {}
    for name, c in (("frozen", ctx), ("bounded", ctx_b)):
        counts: Counter = Counter()
        notes: dict = {}
        assert load_or_exclude(c, ROOT, counts, notes) is None, name
        got[name] = (dict(counts), notes)
    assert got["bounded"] == got["frozen"]
    assert got["bounded"][0] == {"store refused": 1}
    assert got["bounded"][1]["store_refused"][ROOT].startswith(
        f"{TradeDateMismatch.__name__}: ")


# ------------------------------------------------------------------ results ----
def _record(ctx, units):  # noqa: ANN001, ANN202
    bars = ctx.load_bars(ROOT)
    rd = prepare_root(ctx, bars, ROOT)
    rec = per_root_record(rd, {"X": unit_book(rd, units)}, {"X": units})
    return json.loads(json.dumps(rec, default=str)), rd


def test_results_of_the_frozen_book_are_equal_with_and_without_the_bound(tmp_path, gcal,
                                                                         eras) -> None:
    refs, hd, _ = _world(tmp_path, gcal, hist_rg=50)
    ctx = make_context({"rates": gcal}, settlement(), {ROOT: HIST_FIRST},
                       lambda p: S.load_product(p, refs, eras), (), empty_release_rules())
    ctx.last = BK.HIST_LAST
    ctx_b, loader = B.bound_context(ctx, _manifest(refs))
    k = [hd.index(d) for d in hd if d >= date(2019, 3, 1)]
    units = [Unit(hd[k[0]], hd[k[5]], 1, "X", ROOT, hd[k[0]], 5),
             Unit(hd[k[8]], hd[k[13]], -1, "X", ROOT, hd[k[8]], 5),
             Unit(hd[k[-6]], hd[-1], 1, "X", ROOT, hd[k[-6]], 5)]
    rec_full, rd_full = _record(ctx, units)
    rec_bound, _ = _record(ctx_b, units)
    assert rec_full == rec_bound
    assert len(rec_bound["fills"]["X"]) >= 4 and len(rec_bound["units"]["X"]) == 3
    assert max(rec_bound["per_contract_daily_dollars"]) <= str(BK.HIST_LAST)
    assert loader.max_trade_date_loaded() == str(BK.HIST_LAST)
    assert rd_full.root == ROOT
