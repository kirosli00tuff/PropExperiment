"""Stage E.31 Part 3: run the ZM order-book engine over every purchased trade date.

Usage (repo root; detach long runs, README_measure31.md):
  uv run python reports/stage_e31_briefs/work/pilot/measure31.py --manifest runs/manifest31.json \
      --out reports/stage_e31_briefs/work/pilot/runs/measure31 [--workers N] [--dates FILE] \
      [--write-expected-dates FILE] [--derived DIR]

Steps: (1) the manifest (verify31.py) gives every purchased file (path, series, month, sha256);
guards refuse a failed manifest, a request ending after 2024-02-29T22:00Z or touching a sealed
window, and a file whose sha256 differs. (2) Definitions (Z4) are read first: match algorithm, tick
and implied fields of every ZM, ZS and ZL outright go to <out>/definitions31.json. (3) Split: each
Z1, Z2 and Z3 file is streamed once into per-trade-date compact arrays under
<derived>/<series>/<YYYY-MM-DD>.npy (trade date = [D-1 16:00 CT, D 16:00 CT) by ts_recv), with a
marker per file; any record dated on or after 2024-03-01 stops the run. (4) Per trade date, in
worker processes at nice 10 (at most min(8, cpu_count // 2)), measure31_core writes
<out>/<YYYY-MM-DD>/{placements,loop,implied,days}.parquet and diag.json, then the DONE marker
last (lead note 2026-10-22); a date with DONE is skipped on restart.
No network, no API key; nothing here writes outside --out and --derived.
"""
# ruff: noqa: I001 - measure31_core sets sys.path for the repo imports

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import json
import os
import re
import sys
import time as _time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np

import measure31_core as core  # sets sys.path (repo root, this folder)
from data import holdout as ho  # noqa: E402
from data.group_session import GroupCalendar, load_group_calendar  # noqa: E402

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1] / "research"
DERIVED_ROOT = Path("/mnt/large-storage/market_data/PropExperiment/derived/e31")
USDA_BASE = RESEARCH / "usda_releases.csv"
USDA_EXT = RESEARCH / "usda_releases_ext.csv"
USDA_BASE_RANGE = (date(2022, 11, 1), date(2024, 2, 29))  # data_facts.md section (b) title
CUTOFF_BOUND = "2024-02-29T22:00:00Z"
CUTOFF_END_NS = 1_709_244_000 * core.NS  # 2024-02-29T22:00:00Z
CT = ZoneInfo("America/Chicago")
ET = ZoneInfo("America/New_York")
SYMBOLS = ("ZM.v.0", "ZM.v.1")
COND_SYMBOLS = {"Z2": "ZS.v.0", "Z3": "ZL.v.0"}
SPLIT_SERIES = ("Z1", "Z2", "Z3")
RC_OK, RC_STOPPED, RC_REFUSED = 0, 1, 2
MANIFEST_RC_REFUSED = 2
ZM_TICK_1E9 = 100_000_000  # 0.10 USD/short ton
DEFAULT_CHUNK = 1_000_000
DONE = "DONE"
REASON_HOLIDAY = "cme_holiday_or_early_close"
REASON_LATE_OPEN = "scheduled_late_open"
REASON_ROLL, REASON_AFTER_ROLL = "roll_day", "after_roll_day"
REASON_ROLL_UNKNOWN = "roll_status_unknown"
REASON_NO_MAPPING = "no_symbol_mapping"

MBO_COMPACT = np.dtype([("ts_recv", "<i8"), ("ts_event", "<i8"), ("instrument_id", "<u4"),
                        ("order_id", "<u8"), ("price", "<i8"), ("size", "<u4"), ("flags", "u1"),
                        ("action", "u1"), ("side", "u1"), ("sequence", "<u4")])
MBP_COMPACT = np.dtype([("ts_recv", "<i8"), ("ts_event", "<i8"), ("instrument_id", "<u4"),
                        ("flags", "u1"), ("bid_px", "<i8"), ("ask_px", "<i8"),
                        ("sequence", "<u4")])
MBP_SOURCE = {"bid_px": "bid_px_00", "ask_px": "ask_px_00"}


class Refused(RuntimeError):
    """A manifest, file, date or record this run may not use."""


# ------------------------------------------------------------------ manifest ----
@dataclass(frozen=True)
class SourceFile:
    series: str
    month: str
    path: Path
    sha256: str
    start: str
    end: str


def load_manifest(path: Path) -> list[SourceFile]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("exit_code") == MANIFEST_RC_REFUSED:
        raise Refused(f"{path}: verify31 exit code {data.get('exit_code')} (hard failure)")
    out = []
    for f in data.get("files", []):
        hard = [c["name"] for c in f.get("checks", [])
                if c.get("severity") == "hard" and not c.get("passed")]
        if hard:
            raise Refused(f"{f.get('series')} {f.get('month')}: failed hard checks {hard}")
        req = f.get("request") or {}
        out.append(SourceFile(str(f["series"]), str(f["month"]), Path(f["path"]),
                              str(f["sha256"]), str(req.get("start", "")),
                              str(req.get("end", ""))))
    for sf in out:
        guard_request(sf)
    if not any(sf.series == "Z1" for sf in out):
        raise Refused(f"{path}: no Z1 (ZM MBO) file")
    if not any(sf.series == "Z4" for sf in out):
        raise Refused(f"{path}: no Z4 (definition) file; definitions are read first (spec 1)")
    return out


def _utc_ns(stamp: str) -> int:
    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return int(moment.timestamp()) * core.NS + moment.microsecond * 1000


def guard_request(sf: SourceFile) -> None:
    if sf.series not in ("Z1", "Z2", "Z3", "Z4"):
        raise Refused(f"unknown series {sf.series!r}")
    if not sf.start or not sf.end or _utc_ns(sf.end) > CUTOFF_END_NS:
        raise Refused(f"{sf.series} {sf.month}: request end {sf.end!r} is after {CUTOFF_BOUND}")
    if ho.request_touches_sealed_window(sf.start[:10], sf.end[:10]):
        raise Refused(f"{sf.series} {sf.month}: request touches a sealed holdout window")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def open_store(sf: SourceFile, check_sha: bool = True) -> Any:
    import databento  # lazy: tests never need it

    if check_sha and file_sha256(sf.path) != sf.sha256:
        raise Refused(f"{sf.path}: sha256 differs from the manifest")
    store = databento.DBNStore.from_file(sf.path)
    end = store.metadata.end
    if end is None or int(end) > CUTOFF_END_NS:
        raise Refused(f"{sf.path}: metadata end {end} is after {CUTOFF_BOUND}")
    return store


def guard_chunk(ts_recv: np.ndarray, ts_event: np.ndarray, where: str) -> None:
    if len(ts_recv) and (int(ts_recv.max()) >= core.CUTOFF_NS
                         or int(ts_event.max()) >= core.CUTOFF_NS):
        raise Refused(f"{where}: a record is dated on or after 2024-03-01; stopped")


# ------------------------------------------------------------------ definitions ----
def _text(value: Any) -> str:
    if isinstance(value, bytes | np.bytes_):
        return value.decode("ascii", "replace").rstrip("\x00").strip()
    return str(value).strip()


def definition_rows(records: np.ndarray) -> dict[int, dict[str, Any]]:
    """The last definition of every outright future (instrument_class F) of ZM, ZS and ZL."""
    names = records.dtype.names or ()
    out: dict[int, dict[str, Any]] = {}
    for r in records:
        raw = _text(r["raw_symbol"])
        root = raw[:2]
        if root not in ("ZM", "ZS", "ZL") or _text(r["instrument_class"]) != "F":
            continue
        attrib = int(r["inst_attrib_value"]) if "inst_attrib_value" in names else 0

        def num(field: str, rec: Any = r) -> int | None:
            return int(rec[field]) if field in names else None

        out[int(r["instrument_id"])] = {
            "raw_symbol": raw, "root": root, "match_algorithm": _text(r["match_algorithm"]),
            "min_price_increment": int(r["min_price_increment"]),
            "unit_of_measure_qty": num("unit_of_measure_qty"),
            "min_price_increment_amount": num("min_price_increment_amount"),
            "display_factor": num("display_factor"),
            "market_depth_implied": int(r["market_depth_implied"])
            if "market_depth_implied" in names else None,
            "implied_eligible_bit19": bool(attrib & (1 << 19)),
            "ts_recv": int(r["ts_recv"])}
    return out


def read_definitions(files: list[SourceFile]) -> dict[int, dict[str, Any]]:
    defs: dict[int, dict[str, Any]] = {}
    for sf in sorted((f for f in files if f.series == "Z4"), key=lambda f: f.month):
        store = open_store(sf)
        for chunk in store.to_ndarray(count=DEFAULT_CHUNK):
            guard_chunk(chunk["ts_recv"], chunk["ts_event"], str(sf.path))
            defs.update(definition_rows(chunk))
    return defs


TICK_VALUE_USD = {"ZM": 10.00, "ZS": 12.50, "ZL": 6.00}  # spec 0; lead note item 2
# Databento quotes ZM in USD per short ton but ZS and ZL in US cents (per bushel, per pound), as
# the 2024-01 definitions show. Lead ruling 2026-10-23: the check accepts USD or cents for ZS and
# ZL; ticks are used as found (the engine only divides by them).
PRICE_UNIT_TO_USD = {"ZM": (1.0,), "ZS": (1.0, 0.01), "ZL": (1.0, 0.01)}


def root_tick(defs: dict[int, dict[str, Any]], root: str) -> int | None:
    ticks = {d["min_price_increment"] for d in defs.values() if d["root"] == root}
    if len(ticks) > 1:
        raise Refused(f"{root} outrights carry several ticks {sorted(ticks)}")
    return next(iter(ticks)) if ticks else None


def checked_tick(defs: dict[int, dict[str, Any]], root: str) -> int:
    """The root's tick (1e-9 price units) from the Z4 definitions, after the lead's check
    tick x contract size (unit_of_measure_qty) = the spec's tick value in USD."""
    rows = [d for d in defs.values() if d["root"] == root]
    tick = root_tick(defs, root)
    if tick is None:
        raise Refused(f"no {root} outright definition in the Z4 files; stopped")
    for d in rows:
        size = d.get("unit_of_measure_qty")
        value = None if size is None else tick * size / 1e18
        if value is None or all(abs(value * f - TICK_VALUE_USD[root]) > 1e-6
                                for f in PRICE_UNIT_TO_USD[root]):
            raise Refused(
                f"{root} {d['raw_symbol']}: tick {tick / 1e9} x contract size "
                f"{None if size is None else size / 1e9} = {value}, expected "
                f"{TICK_VALUE_USD[root]:.2f} USD (min_price_increment_amount "
                f"{d.get('min_price_increment_amount')}, display_factor "
                f"{d.get('display_factor')}); stopped for the lead")
    return tick


def definitions_summary(defs: dict[int, dict[str, Any]]) -> dict[str, Any]:
    by_root: dict[str, Any] = {}
    for iid, d in sorted(defs.items()):
        by_root.setdefault(d["root"], {})[str(iid)] = {k: v for k, v in d.items()
                                                       if k != "root"}
    zm = [d for d in defs.values() if d["root"] == "ZM"]
    return {"outrights": by_root,
            "zm_outrights_all_K": bool(zm) and all(d["match_algorithm"] == "K" for d in zm),
            "match_algorithms": {r: sorted({d["match_algorithm"] for d in defs.values()
                                            if d["root"] == r}) for r in ("ZM", "ZS", "ZL")},
            "ticks_1e9": {r: root_tick(defs, r) for r in ("ZM", "ZS", "ZL")}}


# ------------------------------------------------------------------ USDA ----
def _covered_range(path: Path) -> tuple[date, date]:
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s*(?:\.\.|to|-|/)\s*(\d{4}-\d{2}-\d{2})")
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                break
            found = pattern.search(line)
            if found:
                return date.fromisoformat(found.group(1)), date.fromisoformat(found.group(2))
    raise Refused(f"{path}: no covered range in its header comment")


def usda_coverage(base: Path = USDA_BASE, ext: Path = USDA_EXT) -> list[tuple[date, date]]:
    ranges = [USDA_BASE_RANGE] if base.is_file() else []
    if ext.is_file():
        ranges.append(_covered_range(ext))
    return ranges


def release_trade_date(moment_utc: datetime) -> date:
    """The trade date whose window [D-1 16:00 CT, D 16:00 CT) holds the moment."""
    local = moment_utc.astimezone(CT)
    return local.date() + timedelta(days=1) if local.time() >= time(16, 0) else local.date()


def load_usda(paths: tuple[Path, ...] = (USDA_BASE, USDA_EXT)) -> tuple[dict[date, tuple[int, ...]],
                                                                        dict[str, int]]:
    """USDA release instants (UTC ns) by trade date (lead note 2026-10-22): every row whose
    report is not NOPA (not USDA), except "-NORELEASE" dates (no release happened) and rows
    without a clock time (counted); UNCERTAIN and RULE-DERIVED rows are used as listed; time_et
    is America/New_York local time. The counts dict holds rows used per report and the skips."""
    out: dict[date, list[int]] = {}
    skipped = {"skipped_nopa": 0, "skipped_norelease": 0, "skipped_no_time": 0}
    for path in paths:
        if not path.is_file():
            continue
        with path.open(encoding="utf-8") as fh:
            lines = [ln for ln in fh if not ln.startswith("#")]
        for row in csv.DictReader(lines):
            report = (row.get("report") or "").strip()
            if "NOPA" in report:
                skipped["skipped_nopa"] += 1
                continue
            listed = row["date"].strip()
            if listed.endswith("-NORELEASE"):
                skipped["skipped_norelease"] += 1
                continue
            stamp = (row.get("time_et") or "").strip()
            if not re.fullmatch(r"\d{1,2}:\d{2}", stamp):
                skipped["skipped_no_time"] += 1
                continue
            skipped[f"used: {report}"] = skipped.get(f"used: {report}", 0) + 1
            hh, mm = (int(x) for x in stamp.split(":"))
            days = listed.split("-OR-")  # UNCERTAIN "X-OR-Y" rows: both alternatives are used
            if len(days) > 1:
                skipped["uncertain_or_rows"] = skipped.get("uncertain_or_rows", 0) + 1
            for listed_day in days:
                moment = datetime.combine(date.fromisoformat(listed_day), time(hh, mm),
                                          tzinfo=ET).astimezone(UTC)
                ns = int(moment.timestamp()) * core.NS
                out.setdefault(release_trade_date(moment), []).append(ns)
    return {d: tuple(sorted(set(v))) for d, v in out.items()}, skipped


# ------------------------------------------------------------------ calendar, symbology ----
def grains() -> GroupCalendar:
    return load_group_calendar("grains")


def month_trade_dates(cal: GroupCalendar, months: list[str]) -> list[date]:
    out = []
    for label in sorted(set(months)):
        first = date.fromisoformat(f"{label}-01")
        day = first
        while day.month == first.month:
            if cal.covers(day) and cal.is_trade_date(day) and day < core.CUTOFF_TRADE_DATE:
                out.append(day)
            day += timedelta(days=1)
    return out


def calendar_reason(cal: GroupCalendar, day: date) -> str:
    if cal.holiday(day) is not None:
        return REASON_HOLIDAY
    if day in cal.scheduled_late_opens or day in cal.late_opens:
        return REASON_LATE_OPEN
    return ""


Mappings = dict[str, list[tuple[date, date, int]]]


def merge_mappings(markers: list[dict[str, Any]]) -> Mappings:
    out: Mappings = {}
    for m in markers:
        for sym, entries in (m.get("mappings") or {}).items():
            for e in entries:
                s = str(e["symbol"]).strip()
                if s.isdigit():
                    out.setdefault(sym, []).append((date.fromisoformat(str(e["start_date"])[:10]),
                                                    date.fromisoformat(str(e["end_date"])[:10]),
                                                    int(s)))
    return {k: sorted(set(v)) for k, v in out.items()}


def instrument_on(maps: Mappings, symbol: str, day: date) -> int | None:
    """Mapping intervals are UTC dates, end exclusive; a CBOT grain trade date's sessions lie
    inside UTC calendar day D (19:00 CT on D-1 is 00:00 or 01:00 UTC on D)."""
    found = {iid for a, b, iid in maps.get(symbol, []) if a <= day < b}
    if len(found) > 1:
        raise Refused(f"{symbol} maps to {sorted(found)} on {day}")
    return next(iter(found)) if found else None


def roll_reasons(maps: Mappings, symbol: str, days: list[date],
                 cal: GroupCalendar) -> dict[date, str]:
    """Spec 2: the trade date on which the symbol's instrument changes, and the trade date after,
    are excluded. A first date whose previous trade date has no mapping is excluded as unknown."""
    out: dict[date, str] = {}
    for day in sorted(days):
        iid = instrument_on(maps, symbol, day)
        if iid is None:
            out[day] = REASON_NO_MAPPING
            continue
        prev = day - timedelta(days=1)
        while not (cal.covers(prev) and cal.is_trade_date(prev)):
            prev -= timedelta(days=1)
        before = instrument_on(maps, symbol, prev)
        if before is None:
            out.setdefault(day, REASON_ROLL_UNKNOWN)
        elif before != iid:
            out[day] = REASON_ROLL
            nxt = day + timedelta(days=1)
            while not (cal.covers(nxt) and cal.is_trade_date(nxt)):
                nxt += timedelta(days=1)
            out.setdefault(nxt, REASON_AFTER_ROLL)
    return out


# ------------------------------------------------------------------ split ----
def compact(chunk: np.ndarray, dtype: np.dtype) -> np.ndarray:
    out = np.empty(len(chunk), dtype=dtype)
    for name in dtype.names:
        src = chunk[MBP_SOURCE.get(name, name)]
        if src.dtype.kind == "S":
            src = src.astype("S1").view(np.uint8)
        out[name] = src
    return out


def day_bounds(start_ns: int, end_ns: int) -> tuple[list[date], np.ndarray]:
    first = datetime.fromtimestamp(start_ns / core.NS, CT).date() - timedelta(days=1)
    last = datetime.fromtimestamp(end_ns / core.NS, CT).date() + timedelta(days=2)
    days = [first + timedelta(days=k) for k in range((last - first).days + 1)]
    bounds = np.array([core.ct_ns(d - timedelta(days=1), time(16, 0)) for d in days],
                      dtype=np.int64)
    return days, bounds


def split_dir(root: Path, series: str) -> Path:
    return root / series


def _marker_path(root: Path, sf: SourceFile) -> Path:
    return split_dir(root, sf.series) / f"{sf.month}.split.json"


def _write_day(folder: Path, day: date, parts: list[np.ndarray]) -> int:
    arr = np.concatenate(parts) if len(parts) > 1 else parts[0]
    tmp = folder / f".{day.isoformat()}.npy.tmp"
    with tmp.open("wb") as fh:
        np.save(fh, arr)
    tmp.replace(folder / f"{day.isoformat()}.npy")
    return len(arr)


def split_file(sf: SourceFile, root: Path, cal: GroupCalendar, chunk_records: int = DEFAULT_CHUNK,
               store: Any = None) -> dict[str, Any]:
    """Stream one Z1/Z2/Z3 file once into per-trade-date compact arrays (resumable per file)."""
    marker = _marker_path(root, sf)
    if marker.is_file():
        done = json.loads(marker.read_text(encoding="utf-8"))
        folder = split_dir(root, sf.series)
        if done.get("sha256") == sf.sha256 and all(
                (folder / f"{d}.npy").is_file() for d in done.get("dates", {})):
            return done
    if store is None:
        store = open_store(sf)
    dtype = MBO_COMPACT if sf.series == "Z1" else MBP_COMPACT
    folder = split_dir(root, sf.series)
    folder.mkdir(parents=True, exist_ok=True)
    meta = store.metadata
    days, bounds = day_bounds(int(meta.start), int(meta.end))
    parts: dict[int, list[np.ndarray]] = {}
    written: dict[str, int] = {}
    counts = {"records": 0, "late_records_dropped": 0, "outside_trade_dates": 0}
    finished = -1

    def flush(below: int) -> None:
        for d in sorted(k for k in parts if k < below):
            written[days[d].isoformat()] = _write_day(folder, days[d], parts.pop(d))

    for chunk in store.to_ndarray(count=chunk_records):
        if len(chunk) == 0:
            continue
        guard_chunk(chunk["ts_recv"], chunk["ts_event"], str(sf.path))
        c = compact(chunk, dtype)
        counts["records"] += len(c)
        idx = np.searchsorted(bounds, c["ts_recv"], side="right") - 1
        for d in np.unique(idx).tolist():
            sel = c[idx == d]
            day = days[d] if 0 <= d < len(days) else None
            if day is None or not (cal.covers(day) and cal.is_trade_date(day)) or \
                    f"{day:%Y-%m}" != sf.month:
                counts["outside_trade_dates"] += len(sel)
                continue
            if d <= finished:
                counts["late_records_dropped"] += len(sel)
                continue
            parts.setdefault(d, []).append(sel)
        low = int(idx.min())
        flush(low)
        finished = max(finished, low - 1)
    flush(len(days) + 1)
    mappings = {str(k): [{"start_date": str(e["start_date"]), "end_date": str(e["end_date"]),
                          "symbol": str(e["symbol"])} for e in v]
                for k, v in (meta.mappings or {}).items()}
    result = {"series": sf.series, "month": sf.month, "path": str(sf.path), "sha256": sf.sha256,
              "dates": written, "counts": counts, "mappings": mappings,
              "written": datetime.now(UTC).isoformat()}
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    tmp.replace(marker)
    return result


# ------------------------------------------------------------------ jobs and workers ----
@dataclass(frozen=True)
class DayTask:
    job: core.DayJob
    zm_path: str | None
    zs_path: str | None
    zl_path: str | None
    out_dir: str


def build_tasks(days: list[date], markers: dict[str, list[dict[str, Any]]],
                defs: dict[int, dict[str, Any]], usda: dict[date, tuple[int, ...]],
                cal: GroupCalendar, derived: Path, out: Path,
                coverage: list[tuple[date, date]] | None = None) -> list[DayTask]:
    """One task per trade date. A date outside the USDA coverage gets no releases, so its
    usda_min is NaN (lead note item 7: not refused)."""
    zm_maps = merge_mappings(markers.get("Z1", []))
    cond_maps = {s: merge_mappings(markers.get(s, [])) for s in ("Z2", "Z3")}
    rolls = {sym: roll_reasons(zm_maps, sym, days, cal) for sym in SYMBOLS}
    zm_tick = checked_tick(defs, "ZM")
    if zm_tick != ZM_TICK_1E9:
        raise Refused(f"ZM min_price_increment {zm_tick} != {ZM_TICK_1E9} (0.10 x 1e9): the "
                      "price encoding is not USD/short ton; stopped")
    zs_tick, zl_tick = checked_tick(defs, "ZS"), checked_tick(defs, "ZL")
    tasks = []
    for day in days:
        syms = []
        for sym in SYMBOLS:
            iid = instrument_on(zm_maps, sym, day)
            raw = defs.get(iid, {}).get("raw_symbol", "") if iid is not None else ""
            syms.append(core.SymbolJob(sym, iid or 0, raw, rolls[sym].get(day, "")))
        job = core.DayJob(day=day, symbols=tuple(syms), calendar_reason=calendar_reason(cal, day),
                          zm_tick_1e9=ZM_TICK_1E9, zs_tick_1e9=zs_tick, zl_tick_1e9=zl_tick,
                          zs_iid=instrument_on(cond_maps["Z2"], COND_SYMBOLS["Z2"], day),
                          zl_iid=instrument_on(cond_maps["Z3"], COND_SYMBOLS["Z3"], day),
                          usda_ns=usda.get(day, ()) if _covered(day, coverage) else ())

        def path(series: str, d: date = day) -> str | None:
            p = split_dir(derived, series) / f"{d.isoformat()}.npy"
            return str(p) if p.is_file() else None

        tasks.append(DayTask(job, path("Z1"), path("Z2"), path("Z3"), str(out)))
    return tasks


def _covered(day: date, coverage: list[tuple[date, date]] | None) -> bool:
    return coverage is None or any(a <= day <= b for a, b in coverage)


def _load(path: str | None, dtype: np.dtype) -> dict[str, np.ndarray] | None:
    if path is None:
        return None
    arr = np.load(path, mmap_mode="r")
    if arr.dtype != dtype:
        raise Refused(f"{path}: dtype {arr.dtype} is not the split dtype")
    return {name: np.asarray(arr[name]) for name in dtype.names}


def _empty_mbo() -> dict[str, np.ndarray]:
    return {name: np.zeros(0, dtype=MBO_COMPACT[name]) for name in MBO_COMPACT.names}


def run_task(task: DayTask) -> dict[str, Any]:
    """Worker: one trade date -> four parquet files, diag.json, then DONE."""
    started = _time.perf_counter()
    zm = _load(task.zm_path, MBO_COMPACT) or _empty_mbo()
    tables = core.measure_day(task.job, zm, _load(task.zs_path, MBP_COMPACT),
                              _load(task.zl_path, MBP_COMPACT))
    folder = Path(task.out_dir) / task.job.day.isoformat()
    write_day_tables(folder, tables, {"zm_records": int(len(zm["ts_recv"])),
                                      "seconds": round(_time.perf_counter() - started, 3)})
    return {"day": task.job.day.isoformat(), "rows": len(tables["placements"]["model"]),
            "records": int(len(zm["ts_recv"])), "seconds": _time.perf_counter() - started}


def arrow_schema(table: str) -> Any:
    """The TABLES31.md column order with arrow types (measure31_core.COLUMN_TYPES)."""
    import pyarrow as pa

    kinds = {"date32": pa.date32(), "str": pa.string(), "uint32": pa.uint32(),
             "int8": pa.int8(), "int32": pa.int32(), "int64": pa.int64(),
             "float64": pa.float64(), "bool": pa.bool_()}
    cols = core.TABLE_COLUMNS[table]
    types = {**core.COLUMN_TYPES["*"], **core.COLUMN_TYPES[table]}
    return pa.schema([(c, kinds[types[c]]) for c in cols])


def write_day_tables(folder: Path, tables: dict[str, Any], extra: dict[str, Any]) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    folder.mkdir(parents=True, exist_ok=True)
    marker = folder / DONE
    if marker.exists():
        marker.unlink()
    for name in ("placements", "loop", "implied", "days"):
        schema = arrow_schema(name)
        cols = tables[name]
        arrays = [pa.array(cols[f.name], type=f.type) for f in schema]
        tmp = folder / f".{name}.parquet.tmp"
        pq.write_table(pa.Table.from_arrays(arrays, schema=schema), tmp)
        tmp.replace(folder / f"{name}.parquet")
    (folder / "diag.json").write_text(json.dumps({**tables["diag"], **extra}, indent=1,
                                                 default=str) + "\n", encoding="utf-8")
    marker.write_text(datetime.now(UTC).isoformat() + "\n", encoding="utf-8")


def _nice() -> None:
    with contextlib.suppress(OSError):
        os.nice(10)


def max_workers(requested: int | None) -> int:
    cap = max(1, min(8, (os.cpu_count() or 2) // 2))
    return cap if requested is None else max(1, min(cap, requested))


# ------------------------------------------------------------------ main ----
def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--manifest", type=Path, default=None, help="required unless --summarize-diag")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=None)
    ap.add_argument("--dates", type=Path, default=None, help="ISO dates to measure, one per line")
    ap.add_argument("--write-expected-dates", type=Path, default=None,
                    help="write every purchased trade date (one ISO date per line) to FILE")
    ap.add_argument("--derived", type=Path, default=DERIVED_ROOT)
    ap.add_argument("--chunk-records", type=int, default=DEFAULT_CHUNK)
    ap.add_argument("--summarize-diag", action="store_true",
                    help="only aggregate every <out>/<date>/diag.json into "
                         "<out>/../measure31_diag_summary.json (counts, no market values)")
    return ap


DIAG_SUMMARY = "measure31_diag_summary.json"


def _add_counts(into: dict[str, int], counts: dict[str, Any]) -> None:
    for key, value in counts.items():
        if isinstance(value, int | float) and not isinstance(value, bool):
            into[key] = into.get(key, 0) + value


def summarize_diag(out: Path) -> dict[str, Any]:
    """Review B5: sum every date's diag.json counts per symbol (book anomalies, event, timer and
    implied counters, markout drops by reason, exclusion reasons) and the ratios that would show
    a wrong T/F/C ordering assumption. Counts only; no price, markout or fill value is read."""
    folders = sorted(p for p in out.iterdir() if p.is_dir() and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}", p.name)) if out.is_dir() else []
    per: dict[str, dict[str, Any]] = {}
    missing, totals = [], {"zm_records": 0, "seconds": 0.0}
    for folder in folders:
        path = folder / "diag.json"
        if not path.is_file():
            missing.append(folder.name)
            continue
        diag = json.loads(path.read_text(encoding="utf-8"))
        _add_counts(totals, {k: diag.get(k, 0) for k in totals})
        for sym, d in (diag.get("symbols") or {}).items():
            acc = per.setdefault(sym, {"dates": 0, "reasons": {}, "run": {}, "book": {},
                                       "markout_drops": {}, "placements_dropped_bad_book": 0})
            acc["dates"] += 1
            reason = d.get("reason") or "included"
            acc["reasons"][reason] = acc["reasons"].get(reason, 0) + 1
            for key in ("run", "book", "markout_drops"):
                _add_counts(acc[key], d.get(key) or {})
            acc["placements_dropped_bad_book"] += int(d.get("placements_dropped_bad_book", 0))
    for acc in per.values():
        run, events = acc["run"], acc["run"].get("events", 0)
        acc["ratios"] = {f"{k}_per_event": (run.get(k, 0) / events if events else None)
                         for k in ("events_mid_update", "events_without_passive_fill")}
    summary = {"out": str(out), "date_folders": len(folders), "folders_without_diag": missing,
               "totals": totals, "per_symbol": per,
               "written": datetime.now(UTC).isoformat()}
    target = out.parent / DIAG_SUMMARY
    target.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def read_dates(path: Path) -> list[date]:
    return sorted({date.fromisoformat(s.strip()) for s in path.read_text().splitlines()
                   if s.strip()})


def plan_days(files: list[SourceFile], cal: GroupCalendar,
              dates_file: Path | None) -> tuple[list[date], list[date]]:
    """(every purchased trade date, the dates to measure). Trade dates outside the USDA coverage
    are measured with usda_min NaN (lead note item 7 replaces the brief's refusal)."""
    expected = month_trade_dates(cal, [f.month for f in files if f.series == "Z1"])
    wanted = expected if dates_file is None else read_dates(dates_file)
    stray = sorted(set(wanted) - set(expected))
    if stray:
        raise Refused(f"--dates holds {len(stray)} date(s) outside the purchased trade dates, "
                      f"e.g. {stray[:3]}")
    return expected, wanted


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    _nice()
    if args.summarize_diag:
        summary = summarize_diag(args.out)
        print(f"measure31: diag of {summary['date_folders']} date folders summarized into "
              f"{args.out.parent / DIAG_SUMMARY}")
        return RC_OK
    if args.manifest is None:
        print("REFUSED: --manifest is required")
        return RC_REFUSED
    try:
        files = load_manifest(args.manifest)
        cal = grains()
        expected, wanted = plan_days(files, cal, args.dates)
        coverage = usda_coverage()
        if args.write_expected_dates is not None:
            args.write_expected_dates.write_text("".join(f"{d}\n" for d in expected))
        defs = read_definitions(files)
        args.out.mkdir(parents=True, exist_ok=True)
        summary = definitions_summary(defs)
        (args.out / "definitions31.json").write_text(json.dumps(summary, indent=1) + "\n")
        if not summary["zm_outrights_all_K"]:
            print("WARNING: not every ZM outright is match algorithm K; model (a) reports this")
        markers: dict[str, list[dict[str, Any]]] = {}
        for sf in sorted((f for f in files if f.series in SPLIT_SERIES),
                         key=lambda f: (f.series, f.month)):
            markers.setdefault(sf.series, []).append(
                split_file(sf, args.derived, cal, args.chunk_records))
        usda, skipped = load_usda()
        tasks = [t for t in build_tasks(wanted, markers, defs, usda, cal, args.derived, args.out,
                                        coverage)
                 if not (args.out / t.job.day.isoformat() / DONE).exists()]
        outside = sum(not _covered(d, coverage) for d in wanted)
    except (Refused, core.MeasureRefused) as exc:
        print(f"REFUSED: {exc}")
        return RC_REFUSED
    print(f"measure31: {len(wanted)} dates wanted, {len(tasks)} to run; USDA coverage "
          f"{coverage}, {outside} dates outside (usda_min NaN); USDA rows {skipped}")
    return _run_pool(tasks, max_workers(args.workers))


def _run_pool(tasks: list[DayTask], workers: int) -> int:
    failed: list[str] = []
    done = 0
    started = _time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers, initializer=_nice) as pool:
        futures = {pool.submit(run_task, t): t.job.day for t in tasks}
        for fut in as_completed(futures):
            try:
                fut.result()
                done += 1
            except Exception as exc:  # noqa: BLE001 - reported per date, the run continues
                failed.append(f"{futures[fut]}: {type(exc).__name__}: {exc}")
            if (done + len(failed)) % 25 == 0:
                print(f"  {done + len(failed)}/{len(tasks)} dates, "
                      f"{_time.perf_counter() - started:.0f} s", flush=True)
    print(f"measure31: {done} dates written, {len(failed)} failed "
          f"({_time.perf_counter() - started:.0f} s){'; ' if failed else ''}"
          f"{'; '.join(failed[:5])}")
    return RC_OK if not failed else RC_STOPPED


def with_job(task: DayTask, **changes: Any) -> DayTask:
    return replace(task, job=replace(task.job, **changes))


if __name__ == "__main__":
    sys.exit(main())
