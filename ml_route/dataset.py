"""The training-window row table of all traded products (M2, M4), read only from the step 2 store.

``build_dataset(store_root, inputs)`` reads every traded price-path contract through
``ml_route.store.read_product_bars`` (path allowlist, window refusals, row bookings, the parquet
pinned to the start rule's sha256, the S_X cut; the sha256s read are kept in
``table.store_sha256``), computes the
cluster leads first (F16 reads them), builds each product's rows, joins them, runs M7.1's
availability validator and M7.4's window test on the joined row index, and returns the table.
``build_from_bars`` is the same pipeline on in-memory bars (tests of M7.2 and M7.5 perturb bars
there; the training job never uses it).
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from pathlib import Path

import numpy as np

from ml_route.constants import CLUSTER_OF, LEAD_OF_CLUSTER, TRAIN_LAST
from ml_route.features import Bars, LeadContext, RowTable, build_daily
from ml_route.inputs import DayTimes, RouteInputs, day_times
from ml_route.rows import build_rows, concat_tables, validate_availability
from ml_route.store import ProductBars, assert_window, read_product_bars


def bars_from_store(pb: ProductBars) -> Bars:
    return Bars(pb.root, pb.ts, pb.open, pb.high, pb.low, pb.close, pb.volume, pb.instrument_id,
                pb.trade_date)


def session_times(root: str, group: str, dates: np.ndarray) -> dict[date, DayTimes]:
    out = {}
    for d in np.unique(dates):
        day = d.astype(object)
        dt = day_times(root, group, day)
        if dt is not None:
            out[day] = dt
    return out


def _cut(bars: Bars, s_x: date, last: date) -> Bars:
    keep = (bars.trade_date >= np.datetime64(s_x)) & (bars.trade_date <= np.datetime64(last))
    return Bars(bars.root, bars.ts[keep], bars.open[keep], bars.high[keep], bars.low[keep],
                bars.close[keep], bars.volume[keep], bars.instrument_id[keep],
                bars.trade_date[keep])


def build_from_bars(all_bars: Mapping[str, Bars], inputs: RouteInputs,
                    blackout: Mapping[str, frozenset[date]] | None = None,
                    last: date = TRAIN_LAST) -> RowTable:
    """Rows of every traded product in ``all_bars``, bars cut to [S_X, last] first."""
    blackout = blackout or {}
    cut = {r: _cut(b, inputs.s_x[r], last) for r, b in all_bars.items() if r in inputs.s_x}
    dailies = {}
    for root, bars in cut.items():
        spec = inputs.products[root]
        if spec.vehicle is None:
            continue
        dailies[root] = build_daily(bars, spec, session_times(root, spec.group, bars.trade_date))
    tables = []
    for root in inputs.traded():
        if root not in cut or root not in dailies:
            continue
        spec = inputs.products[root]
        lead_root = LEAD_OF_CLUSTER[CLUSTER_OF[root]]
        lead = None
        if lead_root in dailies:
            lead = LeadContext(lead_root, cut[lead_root], dailies[lead_root],
                               inputs.products[lead_root].vehicle_ticks_per_vendor_unit)
        cpi = inputs.events.cpi
        tables.append(build_rows(cut[root], dailies[root], spec, inputs.costs[spec.vehicle],
                                 frozenset(blackout.get(root, frozenset())),
                                 inputs.events.of(root), cpi, lead))
    table = concat_tables(tables)
    validate_availability(table)
    return table


def build_dataset(store_root: Path, inputs: RouteInputs) -> RowTable:
    """The training job's row table: store reads only, then M7.1 and M7.4 on the saved index."""
    bars: dict[str, Bars] = {}
    blackout: dict[str, frozenset[date]] = {}
    cuts: dict[str, int] = {}
    shas: dict[str, str] = {}
    for root in inputs.traded():
        pb = read_product_bars(store_root, root, inputs.s_x[root],
                               expected_sha256=pinned_store_sha256(inputs, root))
        shas[root] = pb.file_sha256
        bars[root] = bars_from_store(pb)
        blackout[root] = pb.roll_blackout_dates
        cuts[root] = pb.rows_cut_before_s_x
    table = build_from_bars(bars, inputs, blackout)
    for root in inputs.traded():
        assert_window(root, inputs.s_x[root], table.day[table.product == root], "row table")
    table.counts["bars_cut_before_s_x"] = int(sum(cuts.values()))
    table.store_sha256 = shas
    return table


def pinned_store_sha256(inputs: RouteInputs, root: str) -> str | None:
    """The step 2 parquet sha256 the root's start rule recorded (review F-3 (b)); None only for
    synthetic inputs, which carry no pinned store. A pinned mapping without the root is refused."""
    if inputs.step2_sha256 is None:
        return None
    sha = inputs.step2_sha256.get(root)
    if sha is None:
        from ml_route.inputs import RouteInputMissing

        raise RouteInputMissing(f"no pinned step 2 sha256 for {root} (review F-3)")
    return sha
