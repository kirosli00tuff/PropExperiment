"""Bounded store reads for multi-day books (Stage E.24, V41; E.23 VerdictVerifier NOTE-2).

``load_product_bounded(root, refs, cals, bound)`` returns what base_rules.store.load_product
returns with every row booked after ``bound`` (the read window's last trade date, ctx.last)
left out, and loads no such row where the store format allows:

1. a store whose NAME puts its first trade date after the bound is never opened (no hash, no
   metadata, no row): base_rules.store.refuse_path still runs on its path first, so a sealed,
   research, MES or foreign path is refused even when it is skipped;
2. every other store passes base_rules.store's input checks unchanged (path, sha256 of the
   file's bytes, metadata, plan window, hist calendar: ``_checked_input``); the sha256 streams
   the whole file's bytes through the hash, but no row is decoded by it;
3. rows are read per parquet row group: a row group whose trade_date statistics put every row
   after the bound, and count no row without a label, is never decoded; every decoded batch (at
   most BATCH_ROWS rows) is filtered to trade_date <= bound in Arrow before any table reaches
   pandas. A row group that straddles the bound (or has no statistics, or may hold a row with no
   trade_date label) is decoded and filtered batch by batch: those later rows are decoded, never
   kept. A row with no trade_date label is always kept, so step 4's booking check refuses the
   store as read_era refuses it (TradeDateMismatch), never dropped (A2 review SHOULD-FIX-1).
   Plain statement: inside a straddling row group the bound is a post-decode truncation; across
   row groups it is pruning;
4. the kept rows pass the frozen booking checks (hist_plan.check_bookings or
   data.stage_e_bars.check_bookings), the 2024-02-29 refusal and the splice/blackout check of
   the store's metadata, exactly as base_rules.store.read_era runs them, and then the bound is
   ASSERTED (``check_bound``: no label and no booked trade date after the bound, else
   BoundBreached, which is not a refusal and stops the run);
5. the product is assembled as base_rules.store.load_product assembles it (overlap refusal,
   strictly increasing bars, splices from each loaded store's rolls, blackout union).

An era contributes rows, splices, blackout and a record only when it contributes a row; with the
bound at or after the last store date the result equals load_product's field by field
(tests/test_mdio_bounded.py). Rows after the bound inside a loaded store are not checked: the
bounded read never looks at them (the full read of the same file would).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from base_rules import constants as BK
from base_rules import hist_plan as HP
from base_rules.common import RunContext
from base_rules.store import (
    COLUMNS,
    ERAS,
    EXT2010,
    STEP2_ERA,
    ProductBars,
    RunManifest,
    Splice,
    StoreRef,
    StoreRefused,
    _checked_input,
    refuse_path,
    to_ticks,
)
from data.group_session import GroupCalendar
from data.stage_e_bars import STEP2, book_trade_dates, check_bookings, splices_and_blackout

BATCH_ROWS = 65_536  # rows decoded at a time; later rows of a straddling group never pile up
DICTIONARY_COLUMNS = ("raw_symbol", "trade_date")  # as base_rules.store._read reads them


class BoundBreached(RuntimeError):
    """A loaded row is dated after the bound: a code or data invariant failed. Deliberately NOT a
    StageEBarRefusal, so base_rules.common.load_or_exclude never turns it into an exclusion."""


@dataclass(frozen=True)
class EraLoad:
    """What one store load read (the replay's evidence)."""

    root: str
    era: str
    path: str
    bound: str
    skipped: bool  # never opened: the store's name starts after the bound
    why: str | None
    row_groups_total: int
    row_groups_read: tuple[int, ...]
    straddling: tuple[int, ...]  # read row groups whose statistics straddle the bound
    rows_in_file: int
    rows_decoded: int
    rows_kept: int
    max_trade_date: str | None
    max_ts_ns: int | None

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: list(v) if isinstance(v, tuple) else v for k, v in d.items()}


def _check_bound_type(bound: object) -> date:
    if not isinstance(bound, date) or isinstance(bound, datetime):
        raise TypeError(f"the bound must be a datetime.date (a trade date), got {bound!r}")
    return bound


def name_range(root: str, era: str, ref: StoreRef) -> tuple[date, date]:
    """The store's trade-date range from its NAME (no file is opened), after
    base_rules.store.refuse_path."""
    refuse_path(root, era, ref.path, ref.plan)
    if era == EXT2010:
        return HP.check_name(root, str(ref.plan), Path(ref.path))
    return BK.STEP2_FIRST, BK.WINDOW_LAST


def _text(v: object) -> str:
    return v.decode() if isinstance(v, bytes) else str(v)


def _may_hold_nulls(st: pq.Statistics) -> bool:
    return not st.has_null_count or st.null_count > 0


def plan_row_groups(md: pq.FileMetaData, bound_iso: str) -> tuple[list[int], list[int]]:
    """(row groups to read, of which straddling) from each group's trade_date statistics; a
    group without min/max statistics, or whose statistics report (or do not count) rows with no
    trade_date label, is read (and filtered): min/max ignore such rows, so pruning the group
    would drop them unseen where base_rules.store.read_era refuses the store."""
    names = [md.schema.column(i).name for i in range(md.num_columns)]
    col = names.index("trade_date")
    read, straddle = [], []
    for rg in range(md.num_row_groups):
        st = md.row_group(rg).column(col).statistics
        if st is None or not st.has_min_max or _may_hold_nulls(st):
            read.append(rg)
            straddle.append(rg)
            continue
        lo, hi = _text(st.min), _text(st.max)
        if lo > bound_iso:
            continue  # every row after the bound: never decoded
        read.append(rg)
        if hi > bound_iso:
            straddle.append(rg)
    return read, straddle


def _keep_mask(batch: pa.RecordBatch, bound_iso: str) -> np.ndarray:
    """Rows labelled on or before the bound, and every row with no trade_date label: such a row
    is kept so the frozen booking check (read_era_bounded) refuses the store exactly as
    base_rules.store.read_era does (TradeDateMismatch, a StageEBarRefusal), never dropped."""
    col = batch.column("trade_date")
    if pa.types.is_dictionary(col.type):
        col = col.dictionary_decode()
    keep = pc.less_equal(pc.cast(col, pa.large_string()), pa.scalar(bound_iso, pa.large_string()))
    return np.asarray(keep.fill_null(True).to_numpy(zero_copy_only=False), dtype=bool)


def _to_frame(table: pa.Table) -> pd.DataFrame:
    """The only place a bounded read's rows reach pandas (already filtered)."""
    return table.to_pandas()


def read_bounded(path: Path, bound: date) -> tuple[pd.DataFrame | None, dict]:
    """base_rules.store._read restricted to trade_date <= ``bound`` (module docstring 3): the
    same columns and dtypes, sorted by ts_event, duplicates refused. None: no row kept."""
    bound_iso = _check_bound_type(bound).isoformat()
    pf = pq.ParquetFile(path, read_dictionary=list(DICTIONARY_COLUMNS))
    md = pf.metadata
    read, straddle = plan_row_groups(md, bound_iso)
    batches, decoded = [], 0
    for rg in read:
        for batch in pf.iter_batches(batch_size=BATCH_ROWS, row_groups=[rg],
                                     columns=list(COLUMNS)):
            decoded += batch.num_rows
            kept = batch.filter(pa.array(_keep_mask(batch, bound_iso), type=pa.bool_()))
            if kept.num_rows:
                batches.append(kept)
    stats = {"row_groups_total": md.num_row_groups, "row_groups_read": tuple(read),
             "straddling": tuple(straddle), "rows_in_file": md.num_rows,
             "rows_decoded": decoded, "rows_kept": sum(b.num_rows for b in batches)}
    if not batches:
        return None, stats
    frame = _to_frame(pa.Table.from_batches(batches))
    frame = frame.sort_values("ts_event", kind="stable").reset_index(drop=True)
    if frame["ts_event"].duplicated().any():
        raise StoreRefused(f"{Path(path).name}: duplicate bar timestamps")
    return frame, stats


def check_bound(days: tuple[date, ...], labels: np.ndarray, bound: date, where: str) -> None:
    """The bound, asserted on the kept rows: no trade-date label and no booked trade date after
    ``bound``."""
    b = bound.isoformat()
    text = np.asarray(labels, dtype=str)
    late = text > b
    if late.any():
        raise BoundBreached(f"{where}: {int(late.sum())} rows labelled after the bound {b} "
                            f"(first {text[np.flatnonzero(late)[0]]})")
    if days and max(days) > bound:
        raise BoundBreached(f"{where}: rows booked after the bound {b} (last {max(days)})")


def _skipped(root: str, era: str, ref: StoreRef, bound: date, first: date) -> EraLoad:
    return EraLoad(root, era, str(ref.path), str(bound), True,
                   f"the store's name starts {first}, after the bound", 0, (), (), 0, 0, 0, None,
                   None)


def read_era_bounded(root: str, era: str, ref: StoreRef, cal: GroupCalendar, bound: date,
                     resolver: HP.Resolver = HP.default_resolver
                     ) -> tuple[pd.DataFrame | None, dict | None, EraLoad]:
    """base_rules.store.read_era through ``bound`` (module docstring 1-4)."""
    first, _last = name_range(root, era, ref)
    if first > bound:
        return None, None, _skipped(root, era, ref, bound, first)
    digest, meta, window, where = _checked_input(root, era, ref, cal, resolver)
    frame, st = read_bounded(Path(ref.path), bound)
    if frame is None:
        return None, None, EraLoad(root, era, str(ref.path), str(bound), False,
                                   "no row on or before the bound", st["row_groups_total"],
                                   st["row_groups_read"], st["straddling"], st["rows_in_file"],
                                   st["rows_decoded"], 0, None, None)
    if era == EXT2010:
        assert window is not None
        days = HP.check_bookings(root, window, cal, frame, where)
    else:
        days = check_bookings(root, cal, frame, STEP2, where)
    late = [d for d in set(days) if d > BK.WINDOW_LAST]
    if late:
        raise StoreRefused(f"{where}: trade dates after {BK.WINDOW_LAST} (first {min(late)})")
    check_bound(days, frame["trade_date"].astype(str).to_numpy(), bound, where)
    splices, blackout = splices_and_blackout(root, cal, meta, where)
    rolls = [int(r["ts_ns"]) for r in meta.get("rolls", [])]
    frame["_td"] = np.fromiter((d.toordinal() for d in days), dtype=np.int64, count=len(days))
    record = {"era": era, "plan": ref.plan, "path": str(ref.path), "sha256": digest,
              "rows": int(len(frame)), "trade_dates": len(set(days)),
              "splice_trade_dates": [str(d) for d in splices], "roll_instants_ns": rolls,
              "blackout": sorted(blackout)}
    load = EraLoad(root, era, str(ref.path), str(bound), False, None, st["row_groups_total"],
                   st["row_groups_read"], st["straddling"], st["rows_in_file"],
                   st["rows_decoded"], st["rows_kept"], str(max(days)),
                   int(frame["ts_event"].max()))
    return frame, record, load


def load_product_bounded(root: str, refs: Mapping[str, StoreRef | None],
                         cals: Mapping[str, GroupCalendar], bound: date,
                         resolver: HP.Resolver = HP.default_resolver
                         ) -> tuple[ProductBars, tuple[EraLoad, ...]]:
    """base_rules.store.load_product through ``bound`` (module docstring 5), and what each store
    load read."""
    bound = _check_bound_type(bound)
    frames, records, loads = [], [], []
    for era in ERAS:
        ref = refs.get(era)
        if ref is None:
            continue
        frame, rec, load = read_era_bounded(root, era, ref, cals[era], bound, resolver)
        loads.append(load)
        if frame is not None:
            frames.append(frame)
            records.append(rec)
    if not frames:
        raise StoreRefused(f"{root}: no store row on or before the bound {bound}")
    pb = _assemble(root, frames, records, cals)
    if int(pb.td.max()) > bound.toordinal():
        raise BoundBreached(f"{root}: a bar booked after the bound {bound} (code invariant)")
    return pb, tuple(loads)


def _assemble(root: str, frames: list[pd.DataFrame], records: list[dict],
              cals: Mapping[str, GroupCalendar]) -> ProductBars:
    """base_rules.store.load_product's assembly, unchanged."""
    if len(frames) == 2:
        both = set(frames[0]["_td"].unique()) & set(frames[1]["_td"].unique())
        if both:
            raise StoreRefused(f"{root}: trade date {date.fromordinal(int(min(both)))} is in "
                               "both stores (no date is counted twice)")
    frame = pd.concat(frames, ignore_index=True) if len(frames) == 2 else frames[0]
    ts = frame["ts_event"].to_numpy(dtype=np.int64)
    if len(ts) > 1 and not bool(np.all(ts[1:] > ts[:-1])):
        raise StoreRefused(f"{root}: bars are not strictly increasing across the two stores")
    sym_cat = pd.Categorical(frame["raw_symbol"].astype(str))
    splices = []
    for rec in records:
        booked = book_trade_dates(cals[rec["era"]], np.array(rec["roll_instants_ns"],
                                                             dtype=np.int64))
        splices += [Splice(ns, d) for ns, d in zip(rec["roll_instants_ns"], booked, strict=True)
                    if d is not None]
    blackout = frozenset(d for rec in records for d in rec["blackout"])
    for rec in records:
        rec["blackout"] = [str(d) for d in rec["blackout"]]
    return ProductBars(
        root=root, ts=ts,
        open_t=to_ticks(root, frame["open"].to_numpy(dtype="float64")),
        close_t=to_ticks(root, frame["close"].to_numpy(dtype="float64")),
        sym=np.asarray(sym_cat.codes, dtype=np.int32),
        symbols=tuple(str(c) for c in sym_cat.categories),
        usable=~frame["in_scheduled_closure"].to_numpy(dtype=bool),
        td=frame["_td"].to_numpy(dtype=np.int64),
        splices=tuple(sorted(splices, key=lambda s: s.ts_ns)), blackout=blackout,
        records=tuple(records),
        high_t=to_ticks(root, frame["high"].to_numpy(dtype="float64")),
        low_t=to_ticks(root, frame["low"].to_numpy(dtype="float64")),
        volume=frame["volume"].to_numpy(dtype=np.int64),
        no_new=frame["in_no_new_positions_window"].to_numpy(dtype=bool))


class BoundedLoader:
    """A run context's ``load_bars`` through ``bound`` (base_rules.context.store_loader's lookup
    of a root's stores and era calendars), recording every store load."""

    def __init__(self, manifest: RunManifest, calendars: Mapping, bound: date,
                 resolver: HP.Resolver = HP.default_resolver) -> None:
        self._manifest = manifest
        self._calendars = calendars
        self._bound = _check_bound_type(bound)
        self._resolver = resolver
        self._loads: list[EraLoad] = []

    @property
    def bound(self) -> date:
        return self._bound

    @property
    def loads(self) -> tuple[EraLoad, ...]:
        return tuple(self._loads)

    def max_trade_date_loaded(self) -> str | None:
        got = [ld.max_trade_date for ld in self._loads if ld.max_trade_date is not None]
        return max(got) if got else None

    def __call__(self, root: str) -> ProductBars:
        cals = self._calendars[BK.GROUP_OF[root]]
        pb, loads = load_product_bounded(root, self._manifest.stores[root],
                                         {EXT2010: cals.hist, STEP2_ERA: cals.frozen},
                                         self._bound, self._resolver)
        self._loads.extend(loads)
        return pb


def bound_context(ctx: RunContext, manifest: RunManifest,
                  resolver: HP.Resolver = HP.default_resolver
                  ) -> tuple[RunContext, BoundedLoader]:
    """A copy of ``ctx`` whose bars load only through ctx.last (call it once ctx.last is the read
    window's last trade date); ``ctx`` itself is not changed."""
    loader = BoundedLoader(manifest, ctx.calendars, ctx.last, resolver)
    return replace(ctx, load_bars=loader), loader


def check_bounded(ctx: RunContext) -> BoundedLoader:
    """For a multi-day runner, before its first load: the context's loader is a BoundedLoader
    whose bound is ctx.last (refuses an unbounded loader, or ctx.last moved after binding)."""
    loader = ctx.load_bars
    if not isinstance(loader, BoundedLoader):
        raise BoundBreached(f"the context's loader {loader!r} is not bounded (mdio.bounded)")
    if loader.bound != ctx.last:
        raise BoundBreached(f"the loader's bound {loader.bound} is not ctx.last {ctx.last}")
    return loader


__all__ = ["BATCH_ROWS", "BoundBreached", "BoundedLoader", "EraLoad", "bound_context",
           "check_bound", "check_bounded", "load_product_bounded", "name_range",
           "plan_row_groups", "read_bounded", "read_era_bounded"]
