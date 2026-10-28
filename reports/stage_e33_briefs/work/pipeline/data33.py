"""E.33 raw-record loaders (brief_DataCoder deliverable 2). Every read goes through guard33.

Loaders (all take ``cutoff_ns=None``; with a cutoff they return only records with
ts_recv <= cutoff_ns, for LT1):

- ``load_zm(D)``: E.31's per-day ZM MBO split store (derived/e31/Z1/<D>.npy), every ZM instrument
  (ZM.v.0 and ZM.v.1 ids), dtype ``MBO_COMPACT`` (measure31): ts_recv, ts_event (int64 ns UTC),
  instrument_id, order_id, price (int64, 1e-9 USD/short ton), size, flags, action, side (uint8
  ASCII codes, mbo_book31.ACT_* / SIDE_*), sequence.
- ``load_mbp1(root, D)``, root "ZS" or "ZL": the E.33 split (DERIVED/split/<root>/<D>.npy), dtype
  ``MBP1_SPLIT``: every MBP-1 field (length dropped) with ts_recv/ts_event as int64 and action/side
  as uint8 ASCII codes; prices int64 in 1e-9 units of the instrument's quote (US cents for ZS and
  ZL, see cal33.tick).
- ``definitions()``: every Z4 definition record (outrights and spreads; ``outright_only=True``
  keeps the 148 ZM/ZS/ZL outright futures, instrument_class F) with the fields ``DEF_FIELDS``, in
  ts_recv order, from a cache built once from the 39 raw Z4 files (``build_definitions``).

Trade date D owns the ts_recv window [D-1 16:00 CT, D 16:00 CT) (``window(D)``;
measure31.day_bounds).

Ordering (P0.3, LT4): every loader returns records in ts_recv order. The raw files are ts_recv
non-decreasing in file order (manifest check ``ts_recv_non_decreasing``, detail 0 in all 156 files;
E.32 data facts 1.5: 0 decreases per instrument), and the per-day stores keep file order. Each
loader counts ts_recv decreases in the array as stored; if there is any, it returns a stable
ts_recv sort instead and records the count in ``ORDER_LOG`` (expected to stay empty). Records with
ts_recv < ts_event keep their ts_recv position.
"""

# ruff: noqa: I001 - guard33 sets sys.path before the E.31 and repo imports
from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import guard33 as g  # noqa: E402  (adds REPO and the E.31 pilot folder to sys.path)
import measure31 as m31  # noqa: E402
from data.session import ct_ns as _ct_ns  # noqa: E402

NS = g.NS
SPLIT_ROOT = g.DERIVED / "split"
DEF_DIR = SPLIT_ROOT / "Z4"
DEF_ALL = DEF_DIR / "definitions_all.npy"
DEF_OUTRIGHT = DEF_DIR / "definitions_outright.npy"
DEF_MANIFEST = DEF_DIR / "definitions_manifest.json"
DONE_SUFFIX = ".DONE"
ROOT_SERIES = {"ZS": "Z2", "ZL": "Z3"}
MBO_COMPACT = m31.MBO_COMPACT

MBP1_SPLIT = np.dtype([
    ("ts_recv", "<i8"), ("ts_event", "<i8"), ("rtype", "u1"), ("publisher_id", "<u2"),
    ("instrument_id", "<u4"), ("action", "u1"), ("side", "u1"), ("depth", "u1"),
    ("price", "<i8"), ("size", "<u4"), ("flags", "u1"), ("ts_in_delta", "<i4"),
    ("sequence", "<u4"), ("bid_px_00", "<i8"), ("ask_px_00", "<i8"), ("bid_sz_00", "<u4"),
    ("ask_sz_00", "<u4"), ("bid_ct_00", "<u4"), ("ask_ct_00", "<u4")])

# Z4 fields kept (source dtypes, except ts_recv/ts_event as int64). Prices int64 1e-9 units;
# expiration/activation uint64 ns UTC (UNDEF_TIMESTAMP 2^64-1 kept as is); S fields bytes.
DEF_FIELDS = (
    "ts_recv", "ts_event", "instrument_id", "raw_symbol", "instrument_class",
    "security_update_action", "expiration", "activation", "high_limit_price", "low_limit_price",
    "min_price_increment", "display_factor", "unit_of_measure_qty",
    "min_price_increment_amount", "max_price_variation", "match_algorithm",
    "inst_attrib_value", "market_depth_implied", "maturity_year", "maturity_month",
    "maturity_day", "asset", "group", "channel_id", "rtype", "publisher_id")

ORDER_LOG: dict[str, int] = {}  # "<feed> <D>" -> ts_recv decreases found (then sorted)


# ------------------------------------------------------------------ helpers ----
def as_date(d: date | datetime | str) -> date:
    return g._as_date(d)


def window(d: date | str) -> tuple[int, int]:
    """[D-1 16:00 CT, D 16:00 CT) in UTC ns (measure31.day_bounds convention, DST-aware)."""
    day = as_date(d)
    return _ct_ns(day - timedelta(days=1), time(16, 0)), _ct_ns(day, time(16, 0))


def ts_recv_decreases(ts: np.ndarray) -> int:
    return int(np.count_nonzero(np.diff(ts.astype(np.int64)) < 0)) if len(ts) > 1 else 0


def _in_ts_recv_order(arr: np.ndarray, feed: str, day: date) -> np.ndarray:
    dec = ts_recv_decreases(arr["ts_recv"])
    if dec == 0:
        return arr
    ORDER_LOG[f"{feed} {day}"] = dec
    return arr[np.argsort(arr["ts_recv"], kind="stable")]


def truncate(arr: np.ndarray, cutoff_ns: int | None) -> np.ndarray:
    """Records with ts_recv <= cutoff_ns (arr must be in ts_recv order)."""
    if cutoff_ns is None:
        return arr
    return arr[: int(np.searchsorted(arr["ts_recv"], np.int64(cutoff_ns), side="right"))]


def _check_window(arr: np.ndarray, day: date, where: str) -> None:
    lo, hi = window(day)
    if len(arr) and (int(arr["ts_recv"][0]) < lo or int(arr["ts_recv"][-1]) >= hi):
        raise g.GuardRefused(f"{where}: records outside the trade-date window of {day}")


@lru_cache(maxsize=1)
def source_files() -> dict[str, list[m31.SourceFile]]:
    """The 156 discovery files by series (Z1..Z4), month order, from the sha-checked manifest."""
    g.discovery_manifest()
    files = m31.load_manifest(g.DISCOVERY_DIRS["Z1"] / "manifest.json")
    out: dict[str, list[m31.SourceFile]] = {}
    for sf in sorted(files, key=lambda f: (f.series, f.month)):
        g.check_path(sf.path)
        out.setdefault(sf.series, []).append(sf)
    if sorted(out) != ["Z1", "Z2", "Z3", "Z4"] or any(len(v) != 39 for v in out.values()):
        raise g.GuardRefused("discovery manifest: expected 39 files in each of Z1..Z4")
    return out


@lru_cache(maxsize=1)
def _e31_markers_ok() -> dict[str, dict[str, int]]:
    """E.31 Z1 month markers: sha256 equal to the discovery manifest's; dates -> counts."""
    want = {sf.month: sf.sha256 for sf in source_files()["Z1"]}
    out: dict[str, dict[str, int]] = {}
    for month, sha in want.items():
        marker = g.check_path(g.E31_Z1 / f"{month}.split.json")
        data = json.loads(marker.read_text(encoding="utf-8"))
        if data.get("sha256") != sha:
            raise g.GuardRefused(f"E.31 Z1 marker {month}: sha256 differs from the manifest")
        out[month] = {k: int(v) for k, v in data.get("dates", {}).items()}
    return out


# ------------------------------------------------------------------ loaders ----
def zm_path(d: date | str) -> Path:
    return g.E31_Z1 / f"{as_date(d).isoformat()}.npy"


def load_zm(d: date | str, cutoff_ns: int | None = None) -> np.ndarray:
    """E.31's Z1 per-day split records of trade date D (MBO_COMPACT, all ZM instruments), in
    ts_recv order, truncated at ts_recv <= cutoff_ns when given."""
    day = as_date(d)
    path = g.check_request(zm_path(day), day, day)
    counts = _e31_markers_ok().get(f"{day:%Y-%m}", {})
    if day.isoformat() not in counts:
        raise g.GuardRefused(f"{path}: trade date {day} is not in E.31's Z1 marker")
    arr = np.load(path)
    if arr.dtype != MBO_COMPACT or len(arr) != counts[day.isoformat()]:
        raise g.GuardRefused(f"{path}: dtype or record count differs from the E.31 marker")
    g.check_records(arr["ts_recv"], arr["ts_event"], str(path))
    arr = _in_ts_recv_order(arr, "ZM", day)
    _check_window(arr, day, str(path))
    return truncate(arr, cutoff_ns)


def mbp1_path(root: str, d: date | str) -> Path:
    if root not in ROOT_SERIES:
        raise ValueError(f"root must be ZS or ZL, not {root!r}")
    return SPLIT_ROOT / root / f"{as_date(d).isoformat()}.npy"


def load_mbp1(root: str, d: date | str, cutoff_ns: int | None = None) -> np.ndarray:
    """The E.33 ZS or ZL MBP-1 split records of trade date D (MBP1_SPLIT, every field), in
    ts_recv order, truncated at ts_recv <= cutoff_ns when given."""
    day = as_date(d)
    path = g.check_request(mbp1_path(root, day), day, day)
    done = path.with_suffix(DONE_SUFFIX)
    if not done.is_file():
        raise FileNotFoundError(f"{path}: no DONE marker; the E.33 {root} split is not finished")
    arr = np.load(path)
    expected = json.loads(done.read_text(encoding="utf-8"))["records"]
    if arr.dtype != MBP1_SPLIT or len(arr) != int(expected):
        raise g.GuardRefused(f"{path}: dtype or record count differs from its DONE marker")
    g.check_records(arr["ts_recv"], arr["ts_event"], str(path))
    arr = _in_ts_recv_order(arr, root, day)
    _check_window(arr, day, str(path))
    return truncate(arr, cutoff_ns)


@lru_cache(maxsize=2)
def _definitions_cached(outright_only: bool) -> np.ndarray:
    path = g.check_path(DEF_OUTRIGHT if outright_only else DEF_ALL)
    if not (DEF_DIR / f"definitions{DONE_SUFFIX}").is_file():
        raise FileNotFoundError(f"{DEF_DIR}: definitions cache not built (data33.py definitions)")
    arr = np.load(path)
    arr.setflags(write=False)
    return arr


def definitions(cutoff_ns: int | None = None, outright_only: bool = False) -> np.ndarray:
    """All Z4 definition records in ts_recv order (fields DEF_FIELDS), truncated at
    ts_recv <= cutoff_ns when given. outright_only=True keeps the ZM/ZS/ZL outright futures
    (instrument_class b"F"); spreads are dropped. The returned array is read-only."""
    return truncate(_definitions_cached(bool(outright_only)), cutoff_ns)


# ------------------------------------------------------------------ builders ----
def _decode(sf: m31.SourceFile, chunk: int = m31.DEFAULT_CHUNK):  # noqa: ANN202
    """Yield raw record chunks of one discovery file (sha256 and metadata end checked by
    measure31.open_store; every chunk checked by guard33.check_records)."""
    g.check_path(sf.path)
    store = m31.open_store(sf)
    for part in store.to_ndarray(count=chunk):
        if len(part):
            g.check_records(part["ts_recv"], part["ts_event"], str(sf.path))
            yield part


def build_definitions() -> dict[str, Any]:
    """Cache every Z4 record (DEF_FIELDS) of the 39 raw files in ts_recv order (stable)."""
    DEF_DIR.mkdir(parents=True, exist_ok=True)
    g.check_path(DEF_DIR)
    parts, per_file, dec_file = [], {}, {}
    for sf in source_files()["Z4"]:
        n = 0
        last = None
        dec = 0
        for raw in _decode(sf):
            out = np.empty(len(raw), dtype=_def_dtype(raw.dtype))
            for name in DEF_FIELDS:
                out[name] = raw[name]
            ts = out["ts_recv"]
            dec += ts_recv_decreases(ts) + int(last is not None and len(ts) and ts[0] < last)
            last = int(ts[-1])
            parts.append(out)
            n += len(out)
        per_file[sf.month] = n
        dec_file[sf.month] = dec
    arr = np.concatenate(parts)
    cross = ts_recv_decreases(arr["ts_recv"])
    arr = arr[np.argsort(arr["ts_recv"], kind="stable")]
    outright = arr[arr["instrument_class"] == b"F"]
    _save(DEF_ALL, arr)
    _save(DEF_OUTRIGHT, outright)
    info = {"records": int(len(arr)), "outright_records": int(len(outright)),
            "outright_instruments": int(len(np.unique(outright["instrument_id"]))),
            "records_per_file": per_file, "ts_recv_decreases_within_files": dec_file,
            "ts_recv_decreases_concatenated_before_sort": cross,
            "max_raw_symbol_len": int(max(len(s) for s in np.unique(arr["raw_symbol"]))),
            "source_sha256": {sf.month: sf.sha256 for sf in source_files()["Z4"]},
            "fields": list(DEF_FIELDS), "written": datetime.now(UTC).isoformat()}
    DEF_MANIFEST.write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
    (DEF_DIR / f"definitions{DONE_SUFFIX}").write_text(datetime.now(UTC).isoformat() + "\n",
                                                       encoding="utf-8")
    _definitions_cached.cache_clear()
    return info


def _def_dtype(src: np.dtype) -> np.dtype:
    out = []
    for name in DEF_FIELDS:
        kind = "<i8" if name in ("ts_recv", "ts_event") else src[name].str
        out.append((name, kind))
    return np.dtype(out)


def _save(path: Path, arr: np.ndarray) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("wb") as fh:
        np.save(fh, arr)
    tmp.replace(path)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["definitions"]:
        info = build_definitions()
        print({k: v for k, v in info.items()
               if k not in ("records_per_file", "source_sha256", "fields")})
        return 0
    print("usage: data33.py definitions")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
