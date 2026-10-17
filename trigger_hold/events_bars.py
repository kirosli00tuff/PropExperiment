"""Minute bars for the trigger extraction (lead_spec section 6; TriggerCoder brief item 1).

A frozen Stage E member is driven by the Stage E engine (screening.stage_e_engine.run_engine with
screening.stage_e_rules.StageERules), exactly as screening.stage_e_runner drives it; only the
bars come from another loader. Per leg:

1. the store root: the vehicle's price-path root (base_rules.constants.VEHICLE_OF inverted: MGC
   -> GC, MNQ -> NQ, M2K -> RTY, MCL -> CL, as harness v13 maps MGC to GC), refused unless
   data.stage_e_bars.check_price_path accepts the pair (same group, vendor tick, tick size);
2. base_rules.store.load_product on the E.17 run manifest (both eras, every refusal: path
   layout, sha256, plan, hist calendar, bookings, no trade date after 2024-02-29, splices and
   the roll blackout on each era's calendar);
3. the window's era file (W_ext: ext2010/ext2010h, W_cf: step 2) is read again for the engine's
   full column set (data.stage_e_bars.BAR_COLUMNS: instrument_id, the flatten, no-new, early
   halt, closure, roll-session and degraded flags) after its sha256 is checked again, and every
   row must equal load_product's (timestamps, the trade-date booking of the era's calendar, the
   closure flag), else refused;
4. the frame is cut to the window's trade dates and becomes a data.stage_e_bars.LegFrame (root =
   the vehicle, the store root's splices and roll blackout, both eras unioned), the object the
   harness's member_window and engine take.
No price leaves this module; callers get frames for the engine only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from base_rules import constants as BK
from base_rules.calendars import GroupCalendars, load_calendars
from base_rules.store import EXT2010, STEP2_ERA, RunManifest, load_manifest, load_product
from data.group_session import session_intervals
from data.stage_e_bars import BAR_COLUMNS, LegFrame, _check_hash, check_price_path
from screening.stage_e_align import COVERAGE_MIN, Coverage
from screening.stage_e_frozen import sha256_file
from strategy.stage_e.interface import TradingInterval

W_EXT, W_CF = "W_ext", "W_cf"
WINDOW_ERA = {W_EXT: EXT2010, W_CF: STEP2_ERA}
RUN_MANIFEST_PATH = Path("reports/stage_e17_run_manifest.json")
CT = ZoneInfo("America/Chicago")
NS_PER_MIN = 60 * 1_000_000_000


class BarsRefused(RuntimeError):
    """A leg's bars cannot be given to the engine (refused by name; nothing is returned)."""


@dataclass(frozen=True)
class LoadedLeg:
    leg: LegFrame
    store_root: str
    era: str
    calendar: Any  # the era's group calendar (hist before 2019-05-01, the frozen one after)
    info: Mapping[str, Any]  # paths, sha256s and row counts (no price)


def store_root_of(vehicle: str) -> str:
    """The root whose store gives ``vehicle``'s bars: its full-size sibling for a micro."""
    sources = sorted(r for r, v in BK.VEHICLE_OF.items() if v == vehicle and r != vehicle)
    if not sources:
        return vehicle
    if len(sources) > 1:
        raise BarsRefused(f"{vehicle}: several price-path roots {sources}")
    check_price_path(vehicle, sources[0])  # refuses unless group and ticks agree (v13 N1)
    return sources[0]


def manifest(path: Path = RUN_MANIFEST_PATH) -> RunManifest:
    full = BK.repo_path(path)
    return load_manifest(full, sha256_file(full))


def _era_slice(records: Sequence[Mapping[str, Any]], era: str) -> slice:
    start = 0
    for rec in records:
        n = int(rec["rows"])
        if rec["era"] == era:
            return slice(start, start + n)
        start += n
    raise BarsRefused(f"no {era} store was loaded")


def _iso_of_ordinals(td: np.ndarray) -> np.ndarray:
    uniq, inv = np.unique(td, return_inverse=True)
    names = np.array([date.fromordinal(int(o)).isoformat() for o in uniq], dtype=object)
    return names[inv]


def _read_columns(path: Path, sha256: str, where: str) -> pd.DataFrame:
    _check_hash(path, sha256, where)
    frame = pd.read_parquet(path, columns=list(BAR_COLUMNS))
    return frame.sort_values("ts_event", kind="stable").reset_index(drop=True)


def load_leg(vehicle: str, window: str, first: date, last: date, *,
             run_manifest: RunManifest, calendars: Mapping[str, GroupCalendars]) -> LoadedLeg:
    """``vehicle``'s bars on trade dates first..last of ``window`` for the engine."""
    if window not in WINDOW_ERA:
        raise BarsRefused(f"window {window!r} is not one of {tuple(WINDOW_ERA)}")
    src = store_root_of(vehicle)
    if src not in run_manifest.stores:
        raise BarsRefused(f"{vehicle}: the run manifest has no store for {src}")
    era = WINDOW_ERA[window]
    ref = run_manifest.stores[src].get(era)
    if ref is None:
        raise BarsRefused(f"{src}: no {era} store in the run manifest")
    cals = calendars[BK.GROUP_OF[src]]
    pb = load_product(src, run_manifest.stores[src], {EXT2010: cals.hist, STEP2_ERA: cals.frozen})
    sl = _era_slice(pb.records, era)
    path = BK.repo_path(ref.path)
    where = f"trigger extraction {era} bars {path.name}"
    frame = _read_columns(path, ref.sha256, where)
    ts, td, usable = pb.ts[sl], pb.td[sl], pb.usable[sl]
    if len(frame) != len(ts) or not np.array_equal(frame["ts_event"].to_numpy("int64"), ts):
        raise BarsRefused(f"{where}: rows differ from load_product's")
    labels = frame["trade_date"].astype(str).to_numpy()
    if not np.array_equal(labels, _iso_of_ordinals(td)):
        raise BarsRefused(f"{where}: a trade-date label differs from load_product's booking")
    if not np.array_equal(frame["in_scheduled_closure"].to_numpy(bool), ~usable):
        raise BarsRefused(f"{where}: closure flags differ from load_product's")
    keep = (td >= first.toordinal()) & (td <= last.toordinal())
    cut = frame[keep].reset_index(drop=True)
    days = tuple(date.fromordinal(int(o)) for o in np.unique(td[keep]))
    splices = tuple(sorted({s.trade_date for s in pb.splices}))
    leg = LegFrame(vehicle, era, str(path), ref.sha256, cut, days, splices, pb.blackout)
    info = {"vehicle": vehicle, "store_root": src, "era": era, "path": str(ref.path),
            "sha256": ref.sha256, "era_rows": int(len(frame)), "window_rows": int(len(cut)),
            "window_trade_dates": len(days),
            "stores_checked": [{"era": r["era"], "path": r["path"], "sha256": r["sha256"]}
                               for r in pb.records]}
    calendar = cals.hist if era == EXT2010 else cals.frozen
    return LoadedLeg(leg, src, era, calendar, info)


def load_calendars_for(roots: Sequence[str]) -> dict[str, GroupCalendars]:
    groups = tuple(sorted({BK.GROUP_OF[store_root_of(r)] for r in roots}))
    return load_calendars(groups)


# ------------------------------------------------------------------ coverage (D9) ----
def _ns(day: date, offset: int, at: Any) -> int:
    local = datetime.combine(day + timedelta(days=offset), at, tzinfo=CT)
    return int(local.timestamp()) * 1_000_000_000


def leg_coverage_on(calendar: Any, leg: LegFrame, dates: Sequence[date],
                    intervals: Sequence[TradingInterval]) -> Coverage:
    """screening.stage_e_align.leg_coverage with the era's calendar passed in (the harness's
    function loads the 2019-on calendar, which has no 2010-2019 sessions)."""
    if not intervals:
        raise BarsRefused(f"{leg.root}: the member declares no trading interval for this leg")
    ts = np.sort(leg.frame["ts_event"].to_numpy(dtype="int64"))
    present = expected = 0
    for day in dates:
        opened = session_intervals(calendar, day)
        for iv in intervals:
            lo = _ns(day, iv.start_offset_days, iv.start_ct)
            hi = _ns(day, iv.end_offset_days, iv.end_ct)
            if hi <= lo:
                raise ValueError(f"trading interval {iv} is empty or reversed")
            for s, e in opened:
                a, b = max(lo, s), min(hi, e)
                if b <= a:
                    continue
                a_min = -(-a // NS_PER_MIN) * NS_PER_MIN
                expected += max(0, (b - a_min + NS_PER_MIN - 1) // NS_PER_MIN)
                present += int(np.searchsorted(ts, b, side="left")
                               - np.searchsorted(ts, a_min, side="left"))
    return Coverage(leg.root, present, expected)


__all__ = ["COVERAGE_MIN", "RUN_MANIFEST_PATH", "W_CF", "W_EXT", "WINDOW_ERA", "BarsRefused",
           "LoadedLeg", "leg_coverage_on", "load_calendars_for", "load_leg", "manifest",
           "store_root_of"]
