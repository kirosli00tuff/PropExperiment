"""The ML training job's only data access: the step 2 (training-window) bar store (M7.4, ML-A23).

Layout (PurchaseCoder2's step 2 store, reports/stage_e2b_task4_purchase_worker.md section 1.1, as
relayed by the lead): one parquet per product at
    <STEP2_ROOT>/<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet
(STEP2_ROOT = data/processed_step2 in data/step2_store.py), the research store's schema and
metadata (data/build_bars.py), trade dates 2019-05-06..2024-02-29, S_X NOT applied in the store.
The research-window store stays in data/processed/, a different root.

Refusals (every one raises ``StoreRefused``, naming the case; nothing is skipped silently):
- the store root is data/processed/ itself, lies inside it, or contains it (the research store);
- any file under the store root that is not ``<ROOT>/<step 2 file name of ROOT>`` (a planted
  research-window parquet, a partial file, anything else): the path allowlist of ML-A23;
- a symlink whose target is not a step 2 file name, or lies under data/processed/;
- a parquet whose metadata does not say ``"store": "step2"``;
- any row whose trade date is on or after 2024-03-01 (M7.4's planted research-window bar), or
  before 2019-05-06;
- any row whose TIMESTAMP, booked on the group calendar (data.stage_e_bars.check_bookings, review
  NOTE-4), books to no trade date, to a date on or after 2024-03-01 or outside the step 2 store,
  or to a date other than its trade_date label (a mislabelled row).
Rows before the product's S_X are cut here (D4's start rule; the store does not apply it) and the
cut is asserted on the returned rows. Warm-up for trailing statistics therefore comes only from
bars on or after S_X (M4, missing inputs).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from data.config import PROCESSED_ROOT
from ml_route.constants import EARLIEST_S_X, FORBIDDEN_FROM

STEP2_FILE_TEMPLATE = "ohlcv-1m_{root}_v_0_2019-05-06_2024-02-29_step2.parquet"
STEP2_NAME_RE = re.compile(r"^ohlcv-1m_([0-9A-Z]+)_v_0_2019-05-06_2024-02-29_step2\.parquet$")
META_KEY = b"propexperiment"
COLUMNS = ("ts_event", "open", "high", "low", "close", "volume", "instrument_id", "trade_date")


class StoreRefused(RuntimeError):
    """The training job refuses its data (M7.4, ML-A23)."""


def step2_file_name(root: str) -> str:
    return STEP2_FILE_TEMPLATE.format(root=root)


def _inside(path: Path, other: Path) -> bool:
    return path == other or path.is_relative_to(other)


def assert_store_root(store_root: Path, forbidden_root: Path = PROCESSED_ROOT) -> dict[str, Path]:
    """The allowlisted step 2 files under ``store_root`` by product root; raises otherwise."""
    root = Path(store_root).resolve()
    forbidden = Path(forbidden_root).resolve()
    if _inside(root, forbidden) or _inside(forbidden, root):
        raise StoreRefused(f"REFUSED: store root {root} is, contains or lies inside the research "
                           f"store root {forbidden}")
    if not root.is_dir():
        raise StoreRefused(f"REFUSED: store root {root} is not a directory")
    found: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if path.is_dir() and not path.is_symlink():
            continue
        rel = path.relative_to(root)
        match = STEP2_NAME_RE.match(rel.name)
        if len(rel.parts) != 2 or match is None or match.group(1) != rel.parts[0]:
            raise StoreRefused(f"REFUSED: {rel.as_posix()} is not on the step 2 path allowlist")
        if path.is_symlink():
            target = path.resolve()
            if STEP2_NAME_RE.match(target.name) is None or _inside(target, forbidden):
                raise StoreRefused(f"REFUSED: {rel.as_posix()} links to {target}, not a step 2 "
                                   "file")
        found[rel.parts[0]] = path
    return found


@dataclass(frozen=True)
class ProductBars:
    """One product's bars from the store, cut at S_X. Prices in vendor units."""

    root: str
    s_x: date
    ts: np.ndarray  # int64 UTC ns, bar open
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray  # float64
    instrument_id: np.ndarray  # int64
    trade_date: np.ndarray  # datetime64[D]
    roll_blackout_dates: frozenset[date]
    rows_cut_before_s_x: int
    file_name: str
    file_sha256: str  # the parquet's sha256, checked against the start rule's when given

    def __len__(self) -> int:
        return len(self.ts)


def read_metadata(path: Path) -> dict:
    meta = pq.read_schema(path).metadata or {}
    if META_KEY not in meta:
        raise StoreRefused(f"REFUSED: {path.name} has no propexperiment metadata")
    return json.loads(meta[META_KEY])


def book_rows(root: str, frame: pd.DataFrame, where: str) -> None:
    """Review NOTE-4: book every row's timestamp on the product's group calendar
    (data.stage_e_bars.check_bookings, as the runner and compute/datarules do) and refuse, by
    name, a row that books to no trade date, a row booked to a date outside the step 2 store or
    to a forbidden class (March 2024 embargo, holdout-2, holdout-1: every date on or after
    2024-03-01), and a row whose trade_date label differs from its booking."""
    from data.group_session import load_group_calendar
    from data.stage_e_bars import STEP2, StageEBarRefusal, check_bookings
    from rules.products import product

    try:
        check_bookings(root, load_group_calendar(product(root).group), frame, STEP2,
                       f"step 2 bars {where}")
    except StageEBarRefusal as exc:
        raise StoreRefused(f"REFUSED: {root}: {type(exc).__name__}: {exc}") from exc


def _sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_product_bars(store_root: Path, root: str, s_x: date,
                      forbidden_root: Path = PROCESSED_ROOT,
                      expected_sha256: str | None = None) -> ProductBars:
    """Read one product from the allowlisted store, refuse any out-of-window row, cut at S_X.
    ``expected_sha256``: the step 2 parquet sha256 the product's start rule recorded (review
    F-3 (b)); a file that hashes otherwise is refused. The training job always passes it
    (ml_route.dataset, ml_route.adapters); None is for tests and probes on synthetic stores."""
    if s_x < EARLIEST_S_X or s_x >= FORBIDDEN_FROM:
        raise StoreRefused(f"REFUSED: S_X {s_x} of {root} is outside 2019-05-06..2024-02-29")
    files = assert_store_root(store_root, forbidden_root)
    if root not in files:
        raise StoreRefused(f"REFUSED: no step 2 file for {root} under {store_root}")
    path = files[root]
    file_sha = _sha256(path)
    if expected_sha256 is not None and file_sha != expected_sha256:
        raise StoreRefused(f"REFUSED: {root}: {path.name} hashes to {file_sha[:12]}, the start "
                           f"rule's recorded step 2 parquet is {expected_sha256[:12]} (review "
                           "F-3: the training store must be the store the start rule read)")
    meta = read_metadata(path)
    if meta.get("store") != "step2":
        raise StoreRefused(f"REFUSED: {path.name} metadata store={meta.get('store')!r}, not step2")
    frame = pd.read_parquet(path, columns=list(COLUMNS))
    days = pd.to_datetime(frame["trade_date"], format="%Y-%m-%d").to_numpy().astype("datetime64[D]")
    late = days >= np.datetime64(FORBIDDEN_FROM)
    if late.any():
        raise StoreRefused(f"REFUSED: {root}: {int(late.sum())} rows with trade date on or after "
                           f"{FORBIDDEN_FROM} (first {days[late][0]}) in the training store")
    early = days < np.datetime64(EARLIEST_S_X)
    if early.any():
        raise StoreRefused(f"REFUSED: {root}: {int(early.sum())} rows before {EARLIEST_S_X}")
    book_rows(root, frame, path.name)
    keep = days >= np.datetime64(s_x)
    kept_days = days[keep]
    if kept_days.size and (kept_days.min() < np.datetime64(s_x)
                           or kept_days.max() >= np.datetime64(FORBIDDEN_FROM)):
        raise StoreRefused(f"REFUSED: {root}: the S_X cut failed its own assertion")
    blackout = frozenset(date.fromisoformat(str(d)) for d in meta.get("roll_blackout_dates", []))
    return ProductBars(
        root=root, s_x=s_x,
        ts=frame["ts_event"].to_numpy(np.int64)[keep],
        open=frame["open"].to_numpy(np.float64)[keep],
        high=frame["high"].to_numpy(np.float64)[keep],
        low=frame["low"].to_numpy(np.float64)[keep],
        close=frame["close"].to_numpy(np.float64)[keep],
        volume=frame["volume"].to_numpy(np.float64)[keep],
        instrument_id=frame["instrument_id"].to_numpy(np.int64)[keep],
        trade_date=kept_days,
        roll_blackout_dates=blackout,
        rows_cut_before_s_x=int((~keep).sum()),
        file_name=path.name,
        file_sha256=file_sha,
    )


def assert_window(root: str, s_x: date, days: np.ndarray, step: str) -> None:
    """M7.4's window test on a saved row index (datetime64[D] or date objects)."""
    arr = np.asarray(days).astype("datetime64[D]")
    if arr.size == 0:
        return
    if arr.max() >= np.datetime64(FORBIDDEN_FROM):
        raise StoreRefused(f"REFUSED: {step}: {root} has a row dated {arr.max()} (>= "
                           f"{FORBIDDEN_FROM})")
    if arr.min() < np.datetime64(s_x):
        raise StoreRefused(f"REFUSED: {step}: {root} has a row dated {arr.min()} before S_X {s_x}")
