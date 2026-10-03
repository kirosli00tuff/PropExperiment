"""Fixture stores for the phase-1 tests (Stage E.12 Task 1b). No test lives here; no real store row
is read: every store is synthetic, written under a pytest tmp dir in the real formats.

Formats (read from the real stores' parquet schema and file metadata only, and from the JSON
summaries reports/step2/bars_NG.json): BAR_COLUMNS in the real column order and dtypes, written by
data.build_mes_bars._write_read_only_parquet (the builders' own writer, 0444, "propexperiment"
schema metadata with ``rolls`` as {"symbol", "date", "ts_ns", ...}, and for step 2 stores
``splice_trade_dates``, ``roll_blackout_dates``, ``trade_date_range``, the degraded lists); the
step 2 summary bars_<ROOT>.json with "parquet" {"path", "sha256"} and "degraded"
{"degraded_utc_dates", "on_store_trade_dates"}; research stores with every column.

Roots: HE and LE (livestock: 08:30-13:05 CT, small) are the phase-1 vehicles; ZC (grains) is a
third requested root whose step 2 store holds one January 2023 date only, so D4's window is empty
(P-3: dropped by name); MES (signal only) is a fixture of the confirmation parquet with its S_X
injected (the real D.1f record pins the real store's sha256). Prices come from
ml_route_v2.synthetic._root_bars, so the synthetic plants ("sign" edges, noise) flow through the
stores. LE's June 2022 volume is 1 (below 0.25 V_ref), so its S_X is July 2022 (the S_X cut).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from data.build_bars import research_parquet_path
from data.build_mes_bars import _write_read_only_parquet
from data.group_session import group_of, load_group_calendar, trade_dates_between
from data.stage_e_bars import BAR_COLUMNS, splices_and_blackout
from data.step2_store import step2_parquet_path
from ml_route_v2.phase1.world import MES, MES_STORE, RootStart
from ml_route_v2.synthetic import _plants, _root_bars, default_vol_ticks
from screening.stage_e_frozen import sha256_file
from screening.stage_e_stats_start import REFERENCE_MONTHS

CT = ZoneInfo("America/Chicago")
VEHICLES = ("HE", "LE")
EMPTY_ROOT = "ZC"
REQUESTED = (*VEHICLES, EMPTY_ROOT)
FIRST = date(2022, 6, 1)
LE_FIRST = date(2022, 7, 1)  # June 2022 volume 1: M* = 2022-07
LAST = date(2024, 2, 29)
SEED = 20261003
EDGE_C = 10.0
HE_DEGRADED = ("2023-03-15", "2023-08-10")  # on-store degraded trade dates of HE
OUTSIDE_DEGRADED = "2024-09-18"  # a vendor-degraded UTC date outside the window
RESEARCH_VOLUME = 100
ROLL_MONTHS = (3, 6, 9, 12)


@dataclass(frozen=True)
class Stores:
    step2_root: Path
    research_root: Path
    summaries_root: Path
    mes_path: Path
    research_sha256: Any  # root -> sha256 (the E.2a stand-in)
    mes_start: RootStart

    def world_kw(self) -> dict[str, Any]:
        return {"step2_root": self.step2_root, "research_root": self.research_root,
                "summaries_root": self.summaries_root, "mes_path": self.mes_path,
                "research_sha256": self.research_sha256, "mes_start": self.mes_start}


# ------------------------------------------------------------------ helpers ----
def _ct_ns(day: date, at: time) -> int:
    return int(datetime.combine(day, at, tzinfo=CT).timestamp()) * 1_000_000_000


def _utc_midnight_ns(day: date) -> int:
    return int(datetime.combine(day, time(0, 0), tzinfo=UTC).timestamp()) * 1_000_000_000


def store_frame(frame: pd.DataFrame, root: str, degraded: tuple[str, ...] = ()) -> pd.DataFrame:
    """A bar frame in the real stores' BAR_COLUMNS order and dtypes."""
    n = len(frame)
    days = frame["trade_date"].astype(str).to_numpy(dtype=object)
    out = pd.DataFrame({
        "ts_event": frame["ts_event"].to_numpy(np.int64),
        "open": frame["open"].to_numpy(np.float64), "high": frame["high"].to_numpy(np.float64),
        "low": frame["low"].to_numpy(np.float64), "close": frame["close"].to_numpy(np.float64),
        "volume": frame["volume"].to_numpy().astype(np.int64),
        "instrument_id": frame["instrument_id"].to_numpy().astype(np.int64),
        "raw_symbol": np.full(n, f"{root}Z9", dtype=object),
        "in_flatten_window": np.zeros(n, dtype=bool),
        "in_no_new_positions_window": np.zeros(n, dtype=bool),
        "early_halt_ct": np.full(n, "", dtype=object),
        "in_scheduled_closure": np.zeros(n, dtype=bool), "trade_date": days,
        "is_roll_session": np.zeros(n, dtype=bool),
        "gap_before_minutes": np.zeros(n, dtype=np.int64),
        "vendor_degraded_day": np.isin(days, list(degraded)),
    })
    return out[list(BAR_COLUMNS)]


def roll_meta(root: str, first: date, last: date, *, record: bool) -> dict[str, Any]:
    """Quarterly rolls (the first trade date on or after the 10th of Mar/Jun/Sep/Dec) as the
    stores record them (ts_ns at 00:00 UTC of the splice date), plus the recorded splice and
    roll-blackout dates the loader re-derives (L-8) when ``record``."""
    cal = load_group_calendar(group_of(root))
    days = trade_dates_between(cal, first, last)
    rolls = []
    for year in range(first.year, last.year + 1):
        for month in ROLL_MONTHS:
            nxt = [d for d in days if d >= date(year, month, 10)][:1]
            if nxt and nxt[0].month == month:
                rolls.append({"symbol": f"{root}.v.0", "date": nxt[0].isoformat(),
                              "ts_ns": _utc_midnight_ns(nxt[0]), "from_instrument": "1",
                              "to_instrument": "1", "from_raw_symbol": f"{root}Z9",
                              "to_raw_symbol": f"{root}Z9"})
    meta: dict[str, Any] = {"rolls": rolls, "trade_date_range": [first.isoformat(),
                                                                  last.isoformat()]}
    if record:
        splices, blackout = splices_and_blackout(root, cal, meta, "fixture")
        meta["splice_trade_dates"] = [d.isoformat() for d in splices]
        meta["roll_blackout_dates"] = sorted(d.isoformat() for d in blackout)
    return meta


def write_parquet(frame: pd.DataFrame, meta: dict[str, Any], path: Path) -> str:
    _write_read_only_parquet(frame, Path(path), meta)
    return sha256_file(Path(path))


def synthetic_bars(root: str, first: date, last: date, *, plant: Any, seed: int = SEED
                   ) -> pd.DataFrame:
    return _root_bars(root, first, last, seed=seed, vol_ticks=default_vol_ticks(root),
                      plants=_plants(plant), vehicles=VEHICLES, compact=False)


# ------------------------------------------------------------------ stores ----
def write_step2(root: str, frame: pd.DataFrame, step2_root: Path, summaries_root: Path, *,
                degraded: tuple[str, ...] = ()) -> str:
    first = date.fromisoformat(str(frame["trade_date"].iloc[0]))
    last = date.fromisoformat(str(frame["trade_date"].iloc[-1]))
    meta = roll_meta(root, first, last, record=True)
    meta.update({"store": "step2", "degraded_vendor_days": [*degraded, OUTSIDE_DEGRADED],
                 "degraded_on_store_trade_dates": list(degraded)})
    path = step2_parquet_path(root, Path(step2_root))
    sha = write_parquet(store_frame(frame, root, degraded), meta, path)
    summary = {"product": root, "store": "step2", "parquet": {"path": str(path), "sha256": sha},
               "degraded": {"degraded_utc_dates": sorted([*degraded, OUTSIDE_DEGRADED]),
                            "on_store_trade_dates": sorted(degraded)}}
    Path(summaries_root).mkdir(parents=True, exist_ok=True)
    (Path(summaries_root) / f"bars_{root}.json").write_text(json.dumps(summary),
                                                            encoding="utf-8")
    return sha


def day_session_bars(root: str, days: list[date], at: time, n: int, volume: int) -> pd.DataFrame:
    ts = np.array([_ct_ns(d, at) + k * 60_000_000_000 for d in days for k in range(n)],
                  dtype=np.int64)
    price = np.full(len(ts), 100.0)
    return pd.DataFrame({"ts_event": ts, "open": price, "high": price, "low": price,
                         "close": price, "volume": np.full(len(ts), volume, dtype=np.uint32),
                         "instrument_id": np.ones(len(ts), dtype=np.uint32),
                         "trade_date": np.array([d.isoformat() for d in days for _ in range(n)],
                                                dtype=object)})


def write_research(root: str, research_root: Path) -> str:
    """One trade date per reference month (2025-04..2026-05), 20 day-session bars of volume 100."""
    cal = load_group_calendar(group_of(root))
    days = []
    for month in REFERENCE_MONTHS:
        y, m = map(int, month.split("-"))
        days.append(next(d for d in trade_dates_between(cal, date(y, m, 1), date(y, m, 28))))
    frame = day_session_bars(root, days, time(9, 0), 20, RESEARCH_VOLUME)
    meta = roll_meta(root, days[0], days[-1], record=False)
    return write_parquet(store_frame(frame, root), meta, research_parquet_path(root,
                                                                               Path(research_root)))


MES_NAME = "ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet"


def write_mes(path: Path, *, mislabel: tuple[str, str] | None = None) -> str:
    """The MES confirmation-parquet fixture (rolls only in its metadata, as the real file).
    ``mislabel`` = (day, label): that trade date's bars carry ``label`` instead, so the loader's
    booking check raises TradeDateMismatch (the P-1a test)."""
    mes = synthetic_bars(MES, FIRST, LAST, plant=None)
    if mislabel is not None:
        days = mes["trade_date"].astype(str).to_numpy(dtype=object)
        mes["trade_date"] = np.where(days == mislabel[0], mislabel[1], days)
    meta = roll_meta(MES, FIRST, LAST, record=False)
    meta["degraded_vendor_days"] = [{"date": "2022-08-15", "condition": "degraded"},
                                    {"date": OUTSIDE_DEGRADED, "condition": "degraded"}]
    return write_parquet(store_frame(mes, MES, ("2022-08-15",)), meta, Path(path))


def build_stores(base: Path, *, plant: Any, mes_path: Path | None = None,
                 mes_sha256: str | None = None, extra_bars: dict[str, pd.DataFrame] | None = None
                 ) -> Stores:
    """Fixture stores under ``base`` (module docstring). ``mes_path``/``mes_sha256``: reuse an
    MES fixture; ``extra_bars``: rows appended to a root's step 2 frame (the window-guard test)."""
    base = Path(base)
    step2, research, summaries = base / "step2", base / "research", base / "summaries"
    shas = {}
    for root in VEHICLES:
        frame = synthetic_bars(root, FIRST, LAST, plant=plant)
        if root == "LE":
            june = frame["trade_date"].astype(str).str.startswith("2022-06").to_numpy()
            frame.loc[june, "volume"] = np.uint32(1)
        if extra_bars and root in extra_bars:
            frame = pd.concat([frame, extra_bars[root]], ignore_index=True)
        write_step2(root, frame, step2, summaries,
                    degraded=HE_DEGRADED if root == "HE" else ())
        shas[root] = write_research(root, research)
    zc_days = trade_dates_between(load_group_calendar(group_of(EMPTY_ROOT)), date(2023, 1, 3),
                                  date(2023, 1, 3))
    write_step2(EMPTY_ROOT, day_session_bars(EMPTY_ROOT, zc_days, time(9, 0), 20, 100), step2,
                summaries)
    shas[EMPTY_ROOT] = write_research(EMPTY_ROOT, research)
    if mes_path is None:
        mes_path = base / "MES" / MES_NAME
        mes_sha256 = write_mes(mes_path)
    start = RootStart(MES, FIRST, None, MES_STORE, str(mes_path), str(mes_sha256), None, None,
                      MappingProxyType({"s_x": FIRST.isoformat(), "source": "fixture"}), ())
    return Stores(step2, research, summaries, Path(mes_path), MappingProxyType(shas), start)


NO_STORE_VEHICLE = "ZN"  # in the fixture ranking, but no step 2 store (F-3: dropped by name)
RANKED = (*REQUESTED, NO_STORE_VEHICLE)


def write_ranking(reports_dir: Path, vehicles: tuple[str, ...] = RANKED) -> Path:
    """The lead's Task 5 ranking (schema {"subset": [{"vehicle", "path", "account",
    "quote_usd"}], ...}) under ``reports_dir``."""
    from ml_route_v2.constants import UNIVERSE

    doc = {"schema": "stage_e12_ranking/1",
           "subset": [{"vehicle": v, "path": UNIVERSE[v][1], "account": "acct-1",
                       "quote_usd": 1.0} for v in vehicles]}
    path = Path(reports_dir) / "stage_e12_ranking.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    return path


def write_freeze(root: Path, files: dict[str, bytes]) -> tuple[Path, str]:
    """A v2 freeze manifest under ``root`` hashing ``files`` (written there); (path, sha256)."""
    import hashlib

    entries = []
    for rel, data in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        entries.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest(),
                        "bytes": len(data)})
    doc = {"schema": "ml_v2_freeze/1", "files": entries, "program_n": 198}
    path = Path(root) / "reports" / "stage_e12_ml_v2_freeze.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(doc, indent=2).encode()
    path.write_bytes(raw)
    return path, hashlib.sha256(raw).hexdigest()
