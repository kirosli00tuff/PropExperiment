"""The 2010-2024 splice loader: one product's 2010-2019 store (its fixed plan, F-01) and its E.12
step 2 store (2019-05-06..2024-02-29), from a run manifest E.17 writes, one product at a time.

Guarantees, in order, before any row is returned:
1. paths: the step 2 layout (data.step2_store's name, the root's own directory) and the hist layout
   of base_rules.hist_plan (the root's fixed plan: <plan>/<ROOT>/..._<first>_2019-04-30_<plan>);
   anything under a ``sealed`` directory, the research store (data/processed), an MES store, or
   another name is refused (``StoreRefused`` / ``PlanRefused``);
2. sha256 of each file verified against the manifest (data.stage_e_bars._check_hash);
3. the hist file's metadata names the manifest's plan, its trade_date_range lies inside the
   named window, which equals the plan resolver's, and it names the hist calendar the loader reads;
4. every row booked by the frozen checks: hist rows as data.hist_bars.check_hist_bookings books
   them, on the plan's window (hist_plan.check_bookings), step 2 rows by
   data.stage_e_bars.check_bookings on the 2019-on calendar (holdout, embargo, outside the store);
5. no trade date after 2024-02-29; a trade date present in both stores is refused;
6. splice trade dates and the roll blackout per store by data.stage_e_bars.splices_and_blackout
   (L-8: the splice date and the two group trade dates before it), unioned.
``preflight`` runs 1-3 and the roll booking without reading a row (before the run-once marker,
R-B3). Columns read: ts_event, open, high, low, close, volume, raw_symbol, trade_date,
in_scheduled_closure, in_no_new_positions_window (F-07). A bar flagged in_scheduled_closure is
never a usable bar (OC-T).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from base_rules import constants as K
from base_rules import hist_plan as HP
from data.config import PROCESSED_ROOT, REPO_ROOT
from data.group_session import GroupCalendar
from data.session import ct_ns
from data.stage_e_bars import (
    STEP2,
    StageEBarRefusal,
    _check_hash,
    _checked_expected,
    _meta,
    book_trade_dates,
    check_bookings,
    splices_and_blackout,
)
from rules.products import PRICE_SCALE, product

EXT2010, STEP2_ERA = "ext2010", "step2"
ERAS = (EXT2010, STEP2_ERA)
COLUMNS = ("ts_event", "open", "high", "low", "close", "volume", "raw_symbol", "trade_date",
           "in_scheduled_closure", "in_no_new_positions_window")


class StoreRefused(StageEBarRefusal):
    """A store path, hash, booking or date is refused; nothing is returned."""


def step2_name(root: str) -> str:
    return f"ohlcv-1m_{root}_v_0_{K.STEP2_FIRST}_{K.WINDOW_LAST}_step2.parquet"


def refuse_path(root: str, era: str, path: Path, plan: str | None = None) -> None:
    """Refuse every path that is not the root's own store of ``era`` (module docstring 1)."""
    path = Path(path)
    resolved = path.resolve()
    parts = {p.lower() for p in resolved.parts}
    if root not in K.PRODUCTS or root == "MES":
        raise StoreRefused(f"{root!r} is not one of the 27 test products (MES never read)")
    if "sealed" in parts or resolved.is_relative_to((REPO_ROOT / "data" / "sealed").resolve()):
        raise StoreRefused(f"{path}: a sealed store is never read")
    if resolved.is_relative_to(Path(PROCESSED_ROOT).resolve()) or "research" in path.name:
        raise StoreRefused(f"{path}: the research store is never read")
    if "MES" in path.name.split("_") or "mes" in parts:
        raise StoreRefused(f"{path}: an MES store is never read")
    if era == EXT2010:
        HP.check_name(root, str(plan), path)
        return
    if era != STEP2_ERA or path.name != step2_name(root) or resolved.parent.name != root:
        raise StoreRefused(f"{path}: not the {era} store layout <base>/{root}/"
                           f"{step2_name(root)} (holdout, embargo and other ranges are refused "
                           "by name)")


# ------------------------------------------------------------------ the manifest ----
@dataclass(frozen=True)
class StoreRef:
    path: Path
    sha256: str
    plan: str | None = None  # ext2010 entries: the root's fixed plan (F-01)


@dataclass(frozen=True)
class RunManifest:
    stores: Mapping[str, Mapping[str, StoreRef | None]]  # root -> era -> ref (ext2010 may be None)
    sha256: str
    source: str

    def fallback(self, root: str) -> bool:
        """The product runs on the fallback window (no 2010-2019 store bought)."""
        return self.stores[root].get(EXT2010) is None


def manifest_from_dict(raw: Any, sha256: str, source: str) -> RunManifest:
    if not isinstance(raw, dict) or raw.get("schema") != K.RUN_MANIFEST_SCHEMA:
        raise StoreRefused(f"{source}: schema is not {K.RUN_MANIFEST_SCHEMA!r}")
    stores = {}
    for root, entry in (raw.get("stores") or {}).items():
        if root not in K.PRODUCTS:
            raise StoreRefused(f"{source}: {root!r} is not a test product")
        refs: dict[str, StoreRef | None] = {}
        for era in ERAS:
            item = entry.get(era) if isinstance(entry, dict) else None
            if item is None:
                if era == STEP2_ERA:
                    raise StoreRefused(f"{source}: {root} has no step 2 store")
                refs[era] = None
                continue
            plan = HP.fixed_plan(root, item.get("plan")) if era == EXT2010 else None
            refs[era] = StoreRef(Path(item["path"]), _checked_expected(item["sha256"], source),
                                 plan)
        stores[root] = refs
    return RunManifest(stores, sha256, source)


def load_manifest(path: Path, expected_sha256: str) -> RunManifest:
    from hashlib import sha256

    path = Path(path)
    raw = path.read_bytes()
    got = sha256(raw).hexdigest()
    if got != expected_sha256:
        raise StoreRefused(f"{path.name}: sha256 {got[:12]}... is not {expected_sha256[:12]}...")
    return manifest_from_dict(json.loads(raw), got, str(path))


# ------------------------------------------------------------------ one product ----
@dataclass(frozen=True)
class Splice:
    ts_ns: int
    trade_date: date


@dataclass(frozen=True)
class ProductBars:
    root: str
    ts: np.ndarray  # int64 bar opens, UTC ns, strictly increasing
    open_t: np.ndarray  # int64 vendor ticks
    close_t: np.ndarray
    sym: np.ndarray  # int32 index into ``symbols``
    symbols: tuple[str, ...]
    usable: np.ndarray  # bool: not flagged in_scheduled_closure
    td: np.ndarray  # int64 trade-date ordinals
    splices: tuple[Splice, ...]
    blackout: frozenset[date]
    records: tuple[dict, ...]
    high_t: np.ndarray | None = None  # F-07: the engine's limit-lock test reads high and low
    low_t: np.ndarray | None = None
    volume: np.ndarray | None = None  # the settlement proxy's VWAP
    no_new: np.ndarray | None = None  # in_no_new_positions_window

    def bar(self, day: date, minute: int) -> int | None:
        """Index of bar(p, d, m): opening at CT minute ``minute`` of calendar day ``day``,
        booked to trade date ``day``, usable; None when absent (no forward fill)."""
        return self.bar_ns(ct_ns(day, time(minute // 60, minute % 60)), day)

    def bar_ns(self, target: int, day: date) -> int | None:
        """Index of the usable bar opening at UTC ns ``target`` booked to trade date ``day``."""
        i = int(np.searchsorted(self.ts, target))
        if i < len(self.ts) and int(self.ts[i]) == target and int(self.td[i]) == \
                day.toordinal() and bool(self.usable[i]):
            return i
        return None

    def last_before(self, ts_ns: int) -> int | None:
        i = int(np.searchsorted(self.ts, ts_ns)) - 1
        while i >= 0 and not self.usable[i]:
            i -= 1
        return i if i >= 0 else None

    def first_at_or_after(self, ts_ns: int) -> int | None:
        i = int(np.searchsorted(self.ts, ts_ns))
        while i < len(self.ts) and not self.usable[i]:
            i += 1
        return i if i < len(self.ts) else None

    def splices_between(self, lo_ns: int, hi_ns: int) -> list[Splice]:
        """Splices s with lo < s <= hi (a position held from lo to hi crosses them)."""
        return [s for s in self.splices if lo_ns < s.ts_ns <= hi_ns]

    def contract(self, i: int) -> str:
        return self.symbols[int(self.sym[i])]


def to_ticks(root: str, prices: np.ndarray) -> np.ndarray:
    """Vendor prices -> integer vendor ticks; a price off the grid refuses the store."""
    tick_fixed = product(root).vendor_tick_fixed
    fixed = np.rint(prices * PRICE_SCALE).astype(np.int64)
    off = (fixed % tick_fixed != 0) | (np.abs(fixed / PRICE_SCALE - prices) > 1e-6)
    if off.any():
        raise StoreRefused(f"{root}: price {prices[int(np.flatnonzero(off)[0])]} is off the "
                           "vendor tick grid")
    return fixed // tick_fixed


def _read(path: Path) -> pd.DataFrame:
    table = pq.read_table(path, columns=list(COLUMNS), read_dictionary=["raw_symbol",
                                                                        "trade_date"])
    frame = table.to_pandas()
    frame = frame.sort_values("ts_event", kind="stable").reset_index(drop=True)
    if frame["ts_event"].duplicated().any():
        raise StoreRefused(f"{path.name}: duplicate bar timestamps")
    return frame


def _checked_input(root: str, era: str, ref: StoreRef, cal: GroupCalendar,
                   resolver: HP.Resolver) -> tuple[str, dict, HP.PlanWindow | None, str]:
    """Module docstring 1-3: no row read. Returns (digest, metadata, plan window, where)."""
    refuse_path(root, era, ref.path, ref.plan)
    where = f"{era} bars {Path(ref.path).name}"
    if not Path(ref.path).is_file():
        raise StoreRefused(f"{where}: {ref.path} does not exist")
    digest = _check_hash(Path(ref.path), _checked_expected(ref.sha256, where), where)
    meta = _meta(Path(ref.path))
    window = None
    if era == EXT2010:
        first, last = HP.check_name(root, str(ref.plan), Path(ref.path))
        window = HP.check_plan(root, str(ref.plan), first, last, meta, resolver, where)
        recorded = (meta.get("hist_calendar") or {}).get("sha256")
        if recorded != getattr(cal, "file_sha256", None):
            raise StoreRefused(f"{where}: built on calendar {str(recorded)[:12]}..., not the "
                               "loaded hist calendar")
    return digest, meta, window, where


def preflight(root: str, refs: Mapping[str, StoreRef | None], cals: Mapping[str, GroupCalendar],
              resolver: HP.Resolver = HP.default_resolver) -> list[dict]:
    """Every INPUT check of a product's stores that needs no row (R-B3, before the run-once
    marker): module docstring 1-3 and the rolls booked on the calendar. One record per store."""
    out = []
    for era in ERAS:
        ref = refs.get(era)
        if ref is None:
            if era == STEP2_ERA:
                raise StoreRefused(f"{root}: no step 2 store")
            continue
        digest, meta, _window, where = _checked_input(root, era, ref, cals[era], resolver)
        splices, _ = splices_and_blackout(root, cals[era], meta, where)
        out.append({"root": root, "era": era, "plan": ref.plan, "sha256": digest,
                    "splices": len(splices)})
    return out


def read_era(root: str, era: str, ref: StoreRef, cal: GroupCalendar,
             resolver: HP.Resolver = HP.default_resolver) -> tuple[pd.DataFrame, dict]:
    """One store file, checked (module docstring 1-4, 6)."""
    digest, meta, window, where = _checked_input(root, era, ref, cal, resolver)
    frame = _read(Path(ref.path))
    if era == EXT2010:
        assert window is not None
        days = HP.check_bookings(root, window, cal, frame, where)
    else:
        days = check_bookings(root, cal, frame, STEP2, where)
    late = [d for d in set(days) if d > K.WINDOW_LAST]
    if late:
        raise StoreRefused(f"{where}: trade dates after {K.WINDOW_LAST} (first {min(late)})")
    splices, blackout = splices_and_blackout(root, cal, meta, where)
    rolls = [int(r["ts_ns"]) for r in meta.get("rolls", [])]
    frame["_td"] = np.fromiter((d.toordinal() for d in days), dtype=np.int64, count=len(days))
    record = {"era": era, "plan": ref.plan, "path": str(ref.path), "sha256": digest,
              "rows": int(len(frame)), "trade_dates": len(set(days)),
              "splice_trade_dates": [str(d) for d in splices], "roll_instants_ns": rolls,
              "blackout": sorted(blackout)}
    return frame, record


def load_product(root: str, refs: Mapping[str, StoreRef | None],
                 cals: Mapping[str, GroupCalendar],
                 resolver: HP.Resolver = HP.default_resolver) -> ProductBars:
    """The spliced 2010-2024 bars of ``root`` (``cals``: era -> calendar)."""
    frames, records = [], []
    for era in ERAS:
        ref = refs.get(era)
        if ref is None:
            continue
        frame, rec = read_era(root, era, ref, cals[era], resolver)
        frames.append(frame)
        records.append(rec)
    if not frames:
        raise StoreRefused(f"{root}: no store")
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


__all__ = ["COLUMNS", "ERAS", "EXT2010", "STEP2_ERA", "ProductBars", "RunManifest", "Splice",
           "StoreRef", "StoreRefused", "load_manifest", "load_product", "manifest_from_dict",
           "preflight", "read_era", "refuse_path", "step2_name", "to_ticks"]
