"""Stage A.1 Task 3 cross-check: aggregate existing MES tick trades to 1-minute bars
and compare against the pulled ohlcv-1m bars.

Reads MLCryptoEngine's already-paid-for trades files IN PLACE, read-only
(never copied into this repo). Both dates (2026-07-15, 2026-07-31) fall inside
the pulled window.

Tolerance (stated up front, not tuned afterward):
- open/high/low/close: EXACT to the tick (|diff| = 0 ticks). Databento builds
  ohlcv-1m from the same trades feed, so any nonzero tick difference is a finding.
- volume: EXACT (0 contracts).
- minute coverage: every minute with >= 1 trade must have a bar and vice versa.
- boundary minutes: first/last minute of each UTC-day file are compared like
  any other and also listed separately.

Finding recorded 2026-09-16: Databento assigns trades to ohlcv-1m bars by
``ts_recv`` (its capture clock), while stamping each bar with the bucket start.
A trade CME stamped 04:59:59.9998 but received 05:00:00.0095 is in the 05:00
bar. The check therefore runs twice: ``ts_recv`` bucketing (the vendor method,
held to the exact tolerance above) and ``ts_event`` bucketing (a diagnostic
that quantifies how many minutes differ on the exchange clock).
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from data.config import REPO_ROOT
from data.validate import ts_recv_ordering

MLCE_VENDOR = REPO_ROOT.parent / "MLCryptoEngine" / "data" / "vendor" / "databento" / "GLBX.MDP3"
TICK_DATES = ("2026-07-15", "2026-07-31")
BARS_PATH = (
    REPO_ROOT / "data" / "processed" / "MES" / "ohlcv-1m_MES_v_0_2025-04-01_2026-09-16.parquet"
)
OUT_PATH = REPO_ROOT / "reports" / "tick_crosscheck_summary.json"
NS_PER_MIN = 60 * 1_000_000_000
TICK_FIXED = 250_000_000
PRICE_TOLERANCE_TICKS = 0
VOLUME_TOLERANCE = 0


@dataclass
class DayCrossCheck:
    date: str
    bucket_clock: str
    trades_file: str
    trade_records: int = 0
    ts_recv_regressions: int = 0
    tick_instruments: list[int] = field(default_factory=list)
    bar_instruments: list[int] = field(default_factory=list)
    tick_minutes: int = 0
    bar_minutes: int = 0
    minutes_only_in_ticks: list[str] = field(default_factory=list)
    minutes_only_in_bars: list[str] = field(default_factory=list)
    compared_minutes: int = 0
    mismatched_minutes: int = 0
    max_price_diff_ticks: int = 0
    max_volume_diff: int = 0
    mismatches: list[dict] = field(default_factory=list)
    edge_minutes: list[dict] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (self.ts_recv_regressions == 0 and self.mismatched_minutes == 0
                and not self.minutes_only_in_ticks and not self.minutes_only_in_bars
                and self.tick_instruments == self.bar_instruments)


def aggregate_trades(
    path: Path, bucket_clock: str
) -> tuple[pd.DataFrame, dict[str, int], list[int]]:
    import databento  # lazy

    store = databento.DBNStore.from_file(path)
    chunks = list(store.to_ndarray(count=1_000_000))
    arr = np.concatenate(chunks)
    ordering = ts_recv_ordering(arr["ts_recv"].astype(np.int64))
    df = pd.DataFrame({
        "ts_event": arr["ts_event"].astype(np.int64),
        "ts_recv": arr["ts_recv"].astype(np.int64),
        "price": arr["price"].astype(np.int64),
        "size": arr["size"].astype(np.int64),
        "instrument_id": arr["instrument_id"].astype(np.int64),
    })
    # Feed order (ts_recv) within a bucket; stable sort keeps file order on ties.
    df = df.sort_values(["ts_recv"], kind="stable")
    df["minute"] = df[bucket_clock] // NS_PER_MIN * NS_PER_MIN
    bars = df.groupby("minute").agg(
        open=("price", "first"), high=("price", "max"), low=("price", "min"),
        close=("price", "last"), volume=("size", "sum"),
    )
    return bars, ordering, sorted(df["instrument_id"].unique().tolist())


def _ct(ns: int) -> str:
    return pd.Timestamp(ns, tz="UTC").tz_convert("America/Chicago").strftime("%m-%d %H:%M")


def cross_check_day(day: str, all_bars: pd.DataFrame, bucket_clock: str) -> DayCrossCheck:
    path = MLCE_VENDOR / f"date={day}" / "MES_c_0.trades.dbn.zst"
    result = DayCrossCheck(date=day, bucket_clock=bucket_clock, trades_file=str(path))
    tick_bars, ordering, tick_ids = aggregate_trades(path, bucket_clock)
    result.trade_records = ordering["records"]
    result.ts_recv_regressions = ordering["ts_recv_regressions"]
    result.tick_instruments = tick_ids

    start = int(pd.Timestamp(day, tz="UTC").value)
    end = start + 86_400 * 1_000_000_000
    bars = all_bars[(all_bars["ts_event"] >= start) & (all_bars["ts_event"] < end)]
    bars = bars.set_index("ts_event")
    result.bar_instruments = sorted(bars["instrument_id"].unique().tolist())
    tick_bars = tick_bars[(tick_bars.index >= start) & (tick_bars.index < end)]
    result.tick_minutes, result.bar_minutes = len(tick_bars), len(bars)
    result.minutes_only_in_ticks = [_ct(m) for m in tick_bars.index.difference(bars.index)]
    result.minutes_only_in_bars = [_ct(m) for m in bars.index.difference(tick_bars.index)]

    common = tick_bars.index.intersection(bars.index)
    edges = {start, end - NS_PER_MIN}
    for minute in common:
        t = tick_bars.loc[minute]
        b = bars.loc[minute]
        diffs = {
            k: int(round(b[k] * 1e9)) - int(t[k]) for k in ("open", "high", "low", "close")
        }
        tick_diffs = {k: v // TICK_FIXED for k, v in diffs.items()}
        vol_diff = int(b["volume"]) - int(t["volume"])
        row = {"minute_ct": _ct(minute), **{f"d_{k}_ticks": v for k, v in tick_diffs.items()},
               "d_volume": vol_diff}
        if minute in edges:
            result.edge_minutes.append(row)
        result.compared_minutes += 1
        worst = max(abs(v) for v in tick_diffs.values())
        result.max_price_diff_ticks = max(result.max_price_diff_ticks, worst)
        result.max_volume_diff = max(result.max_volume_diff, abs(vol_diff))
        if worst > PRICE_TOLERANCE_TICKS or abs(vol_diff) > VOLUME_TOLERANCE:
            result.mismatched_minutes += 1
            if len(result.mismatches) < 50:
                result.mismatches.append(row)
    return result


def main() -> int:
    from datetime import date

    from data.splits import HOLDOUT_START

    if any(date.fromisoformat(d) >= HOLDOUT_START for d in TICK_DATES):
        print(f"REFUSED: tick cross-check days {TICK_DATES} are inside the sealed holdout "
              f"(>= {HOLDOUT_START}). The Stage A.1 result is preserved in {OUT_PATH.name}. "
              "Re-running needs the data.holdout unlock ceremony (Stage D.2 only).")
        return 4
    all_bars = pd.read_parquet(BARS_PATH, columns=["ts_event", "open", "high", "low", "close",
                                                   "volume", "instrument_id"])
    results = [
        cross_check_day(d, all_bars, clock) for clock in ("ts_recv", "ts_event") for d in TICK_DATES
    ]
    payload = {
        "tolerance": {"price_ticks": PRICE_TOLERANCE_TICKS, "volume_contracts": VOLUME_TOLERANCE,
                      "minute_coverage": "exact set equality"},
        "days": [asdict(r) | {"passed": r.passed} for r in results],
    }
    OUT_PATH.write_text(json.dumps(payload, indent=1))
    for r in results:
        print(r.bucket_clock, r.date, "passed" if r.passed else "FAILED", r.trade_records, "trades",
              r.compared_minutes, "minutes", "mismatched", r.mismatched_minutes,
              "only_ticks", len(r.minutes_only_in_ticks), "only_bars", len(r.minutes_only_in_bars),
              "ids", r.tick_instruments, r.bar_instruments, "recv regress", r.ts_recv_regressions,
              "max dpx", r.max_price_diff_ticks, "max dvol", r.max_volume_diff)
        print("  mismatches:", r.mismatches[:5], "edges:", r.edge_minutes)
        print("  only ticks:", r.minutes_only_in_ticks[:10],
              "only bars:", r.minutes_only_in_bars[:10])
    return 0 if all(r.passed for r in results if r.bucket_clock == "ts_recv") else 3


if __name__ == "__main__":
    sys.exit(main())
