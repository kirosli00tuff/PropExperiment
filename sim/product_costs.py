"""Stage E per-product execution cost model: the frozen D8 table as lookups (Stage E.2a Task 8).

``load_cost_table`` reads reports/stage_e2a_costs.json (written once by
``python -m sim.calibrate_costs build`` and then frozen) and returns one ``ProductCostModel`` per
contract. Every function below is pure given a loaded model. MES's own model (sim/costs.py,
sim/fill_model.py, sim/slippage_calibration.json) is separate and unchanged.

Units and conventions:
- Slippage is per side, per contract, in ticks of the contract, against the quoted mid; a buy
  market order hits the ask (its depth term uses the ask's median top size), a sell hits the bid.
- The bucket is the 30-minute CT clock bucket containing the fill's CT wall-clock time (partial
  buckets at segment edges are their own buckets); a time in no bucket (a closure, a pause, a
  time the sample never traded) raises ``CostLookupError``, never a guess.
- Event window (D8): a fill in [release, release + 30 min) after a scheduled major release that
  concerns the product pays, per side, the product's largest one-side slippage. The caller says
  whether a fill is in such a window (the release calendar is Stage E.2b's).
- Commission is Topstep's round-turn total per contract (D8), half per side.
- Round turn in ticks = commission / tick value + entry side + exit side.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from data.config import REPO_ROOT

CT = ZoneInfo("America/Chicago")
COST_TABLE_PATH = REPO_ROOT / "reports" / "stage_e2a_costs.json"
SIDES = ("buy", "sell")


class CostLookupError(ValueError):
    """The frozen table cannot answer the question asked; never guessed."""


class ProvisionalTableError(RuntimeError):
    """The table's depth term is still pending the Task 9 sizes."""


@dataclass(frozen=True)
class BucketCost:
    key: str
    start_min: int  # CT minute of day, inclusive
    end_min: int  # CT minute of day, exclusive (1440 = midnight)
    side_ticks: dict[str, float]  # "buy" / "sell" -> one-side slippage in ticks
    fallback: bool
    day_session: bool

    def contains(self, minute: int) -> bool:
        return self.start_min <= minute < self.end_min


@dataclass(frozen=True)
class ProductCostModel:
    product: str
    tick_size: str
    tick_value_usd: float
    commission_rt_usd: float
    q_c: int | None
    buckets: tuple[BucketCost, ...]
    event_side_ticks: dict[str, float]
    provisional: bool

    @property
    def commission_rt_ticks(self) -> float:
        return self.commission_rt_usd / self.tick_value_usd

    def bucket_at(self, when: datetime | time) -> BucketCost:
        minute = ct_minute(when)
        found = [b for b in self.buckets if b.contains(minute)]
        if len(found) != 1:
            raise CostLookupError(
                f"{self.product}: no calibrated bucket at CT {minute // 60:02d}:{minute % 60:02d}")
        return found[0]

    def side_slippage_ticks(self, when: datetime | time, side: str,
                            in_event_window: bool = False) -> float:
        """One side's slippage per contract, in ticks, at a fill time."""
        if side not in SIDES:
            raise ValueError(f"side must be one of {SIDES}, not {side!r}")
        bucket = self.bucket_at(when)  # a closed time raises even inside an event window
        return self.event_side_ticks[side] if in_event_window else bucket.side_ticks[side]

    def side_cost_usd(self, when: datetime | time, side: str, qty: int,
                      in_event_window: bool = False) -> float:
        """Commission (half the round turn) plus slippage for one side of ``qty`` contracts."""
        _check_qty(qty)
        slip = self.side_slippage_ticks(when, side, in_event_window)
        return qty * (self.commission_rt_usd / 2 + slip * self.tick_value_usd)

    def round_turn_ticks(self, entry: datetime | time, exit_: datetime | time, direction: int,
                         entry_event: bool = False, exit_event: bool = False) -> float:
        """Commission/tick value + entry-side + exit-side slippage per contract (direction +1
        long: buy then sell; -1 short: sell then buy)."""
        if direction not in (1, -1):
            raise ValueError(f"direction must be +1 or -1, not {direction!r}")
        entry_side, exit_side = ("buy", "sell") if direction == 1 else ("sell", "buy")
        return (self.commission_rt_ticks
                + self.side_slippage_ticks(entry, entry_side, entry_event)
                + self.side_slippage_ticks(exit_, exit_side, exit_event))

    def round_turn_usd(self, entry: datetime | time, exit_: datetime | time, direction: int,
                       qty: int, entry_event: bool = False, exit_event: bool = False) -> float:
        _check_qty(qty)
        ticks = self.round_turn_ticks(entry, exit_, direction, entry_event, exit_event)
        return qty * ticks * self.tick_value_usd


def _check_qty(qty: int) -> None:
    if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
        raise ValueError(f"quantity {qty!r} is not a positive integer")


def ct_minute(when: datetime | time) -> int:
    """CT minute of day of a tz-aware datetime, or of a CT wall-clock ``time``."""
    if isinstance(when, datetime):
        if when.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        local = when.astimezone(CT)
        return local.hour * 60 + local.minute
    if isinstance(when, time):
        if when.tzinfo is not None:
            raise ValueError("a time of day is read as CT wall clock and must be naive")
        return when.hour * 60 + when.minute
    raise TypeError(f"{when!r} is neither a datetime nor a time")


def model_from_entry(entry: dict, provisional: bool) -> ProductCostModel:
    if not entry.get("calibrated", False):
        raise CostLookupError(f"{entry['product']} was not calibrated: "
                              f"{entry.get('uncalibrated_reason')}")
    buckets = tuple(
        BucketCost(key=b["key"], start_min=int(b["start_min"]), end_min=int(b["end_min"]),
                   side_ticks={s: float(b["side_ticks"][s]) for s in SIDES},
                   fallback=bool(b["fallback"]), day_session=bool(b["day_session"]))
        for b in entry["buckets"])
    return ProductCostModel(
        product=entry["product"], tick_size=entry["tick_size"],
        tick_value_usd=float(entry["tick_value_usd"]),
        commission_rt_usd=float(entry["commission_rt_usd"]), q_c=entry["q_c"],
        buckets=buckets,
        event_side_ticks={s: float(entry["event_window_side_ticks"][s]) for s in SIDES},
        provisional=provisional)


def load_cost_table(path: Path = COST_TABLE_PATH, allow_provisional: bool = False
                    ) -> dict[str, ProductCostModel]:
    """All calibrated contracts of the frozen table. A table whose depth term is still pending is
    refused unless ``allow_provisional`` (its figures are the half-spread part only)."""
    raw = json.loads(Path(path).read_text())
    provisional = raw.get("depth_term") != "applied"
    if provisional and not allow_provisional:
        raise ProvisionalTableError(f"{path}: depth term {raw.get('depth_term')!r}; the table is "
                                    "provisional until the Task 9 sizes are applied")
    return {root: model_from_entry(entry, provisional)
            for root, entry in raw["products"].items() if entry.get("calibrated", False)}
