"""MES execution cost model: time-of-day slippage + round-turn commission.

Slippage is read from ``sim/slippage_calibration.json``, produced by
``sim/calibrate_slippage.py`` from the two MES mbp-10 days already owned in
MLCryptoEngine (2026-07-15, 2026-07-31; read in place, not re-purchased).
It is a table, not a flat number, because the open, the midday lull and the
close genuinely differ (e.g. 50-micro mean: 1.16 / 0.87 / 0.98 ticks).

Units: slippage is in MES ticks (0.25 pt = $1.25 per micro) for ONE side
(entry or exit) of a market order, measured against the mid. It excludes
latency/adverse selection, queue position and hidden liquidity; Stage C
should add a strategy-specific adverse-selection term on top.

Every function is pure given a loaded table; ``load_slippage_table`` is the
only I/O.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")
CALIBRATION_PATH = Path(__file__).with_name("slippage_calibration.json")

MES_TICK_VALUE_USD = 1.25

# Official MES round-turn commission on Topstep (TopstepX), per contract:
# $0.02 NFA + $0.70 exchange + $0.50 commission = $1.22.
# Source: Topstep "TopstepX Commissions and Fees" help article
# (help.topstep.com/en/articles/8284213-topstepx-commissions-and-fees), recorded in
# prior project research and re-read 2026-09-16 (article updated 2026-07-28).
# TODO(Stage A.2, BLOCKING): reconfirm this figure at Topstep checkout before any
# backtest result is trusted. Topstep changed commission/fee figures several
# times in 2026 (e.g. metals exchange fees from 2026-07-20); a stale number here
# silently corrupts every downstream cost calculation.
MES_ROUND_TURN_COMMISSION_USD = 1.22
COMMISSION_NEEDS_RECONFIRMATION = True

STATISTICS = ("mean", "p50", "p90", "p99")


class SlippageTableError(ValueError):
    """The calibration cannot answer the question asked; never guessed."""


@dataclass(frozen=True)
class SlippageTable:
    sizes_micros: tuple[int, ...]
    bucket_minutes: int
    buckets: dict[str, dict[str, Any]]  # "HH:MM" CT -> stats
    windows: dict[str, dict[str, Any]]


def load_slippage_table(path: Path = CALIBRATION_PATH) -> SlippageTable:
    raw = json.loads(path.read_text())
    return SlippageTable(
        sizes_micros=tuple(raw["sizes_micros"]),
        bucket_minutes=int(raw["bucket_minutes"]),
        buckets=raw["buckets_ct"],
        windows=raw["windows"],
    )


def bucket_key(ts_utc: datetime, bucket_minutes: int) -> str:
    if ts_utc.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    local = ts_utc.astimezone(CT)
    minute = (local.hour * 60 + local.minute) // bucket_minutes * bucket_minutes
    return f"{minute // 60:02d}:{minute % 60:02d}"


def calibrated_size(qty_micros: int, sizes: tuple[int, ...]) -> int:
    """Smallest calibrated size >= qty: never round an order DOWN to a cheaper size."""
    if qty_micros <= 0:
        raise ValueError(f"quantity {qty_micros} must be positive")
    for size in sorted(sizes):
        if size >= qty_micros:
            return size
    raise SlippageTableError(f"{qty_micros} micros exceeds largest calibrated size {max(sizes)}")


def expected_slippage_ticks(
    table: SlippageTable, ts_utc: datetime, qty_micros: int, statistic: str = "mean"
) -> float:
    """One-side slippage in ticks for a market order of ``qty_micros`` at ``ts_utc``."""
    if statistic not in STATISTICS:
        raise ValueError(f"statistic must be one of {STATISTICS}")
    key = bucket_key(ts_utc, table.bucket_minutes)
    bucket = table.buckets.get(key)
    if bucket is None:
        raise SlippageTableError(
            f"no calibration for CT bucket {key} (market closed in the sample?)"
        )
    size = calibrated_size(qty_micros, table.sizes_micros)
    value = bucket[str(size)][statistic]
    if value is None or value != value:  # NaN: depth too thin in every sample
        raise SlippageTableError(f"bucket {key} size {size}: no usable samples")
    return float(value)


def round_turn_cost_usd(
    table: SlippageTable,
    entry_ts_utc: datetime,
    exit_ts_utc: datetime,
    qty_micros: int,
    statistic: str = "mean",
) -> float:
    """Commission + entry slippage + exit slippage, in USD, for ``qty_micros``."""
    slip_ticks = expected_slippage_ticks(table, entry_ts_utc, qty_micros, statistic) + (
        expected_slippage_ticks(table, exit_ts_utc, qty_micros, statistic)
    )
    return qty_micros * (MES_ROUND_TURN_COMMISSION_USD + slip_ticks * MES_TICK_VALUE_USD)
