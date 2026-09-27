"""Stage E frozen inputs for the generalized screening runner (Stage E.2b Task 1, design D11.6).

Every value that could change a Stage E screening result and is not code comes from here, read from
the files E.2a froze, and nowhere else: the product rules (rules/products.py), the D8 cost table
(reports/stage_e2a_costs.json), the D2 vehicles and sizes (reports/stage_e2a_vehicles.json,
reports/stage_e2a_vehicle_sizes.json) and the operative epsilon per vehicle
(reports/stage_e2a_epsilon.json). ``load_frozen_tables`` refuses unless each table's sha256 equals
the value E.2a recorded (``E2A_TABLES``), and the paths are module constants under the repository
root: no argument or environment variable can point the runner at another table.

Readings (each stated in reports/stage_e2b_task1_runner_worker.md):
- Event-window cost (D8, audit ruling T12-4): a fill in an event window pays, per side, the
  largest half-spread s_b of the product's buckets PLUS the fill's own bucket's depth term (the
  separate depth rule); never the table's ``event_window_side_ticks`` field, which is
  max(s_b + depth) for M2K, M6B, MCL, MNG and MYM.
- Slippage in cents: ceil(qty x slippage ticks x tick value in cents), the MES engine's rounding
  (sim/fill_model.py: "Rounding is up, never down"); commission per side = half the round-turn
  cents of rules/products.py (every round turn is an even number of cents; checked at load).
- A traded leg must be a vehicle of reports/stage_e2a_vehicles.json with status "chosen" or
  "undersized"; its q_c comes from that table and its eps from stage_e2a_epsilon.json's
  ``eps_operative`` (NULL_CRITERIA_E 2: min(translated, funnel)).
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, time
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType
from zoneinfo import ZoneInfo

from data.config import REPO_ROOT
from rules.products import Product, product

CT = ZoneInfo("America/Chicago")
SIDES = ("buy", "sell")

# name -> (path relative to the repository root, sha256 recorded by E.2a; reports/E.2a_RETURN.md 7)
E2A_TABLES: Mapping[str, tuple[str, str]] = MappingProxyType({
    "costs": ("reports/stage_e2a_costs.json",
              "f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14"),
    "sizes": ("reports/stage_e2a_vehicle_sizes.json",
              "280d7e9df1953069448ca1762588477146a5d3c35bc53d3e9e2df50272c47325"),
    "vehicles": ("reports/stage_e2a_vehicles.json",
                 "1f1cafee4330961799f33d5493e640897cfa79827be98597dbaba23292e29913"),
    "epsilon": ("reports/stage_e2a_epsilon.json",
                "4e2c773182a23e7d073305ca4eb0134d3b3ac554ccc8215730bc1e194eaff496"),
})
TRADED_STATUSES = ("chosen", "undersized")
# MES's research parquet (not in the E.2a size table; pinned by tests/test_e2a_bars.py and by
# data/holdout.py's manifest): MES is read only as a leg (D1.5) and by the MES regressions.
MES_RESEARCH_SHA256 = "aea959a518c32984832126f8314000796318efa219379a1ac4aea556a1736ae0"


class FrozenInputError(RuntimeError):
    """A frozen table is missing, differs from its recorded hash, or cannot answer."""


class CostLookupError(FrozenInputError):
    """The frozen cost table has no bucket for the fill time; never guessed."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _cents(usd: object) -> Fraction:
    """An exact cents value from a decimal string, Decimal or float repr."""
    return Fraction(str(usd)) * 100


def _int_if_whole(value: Fraction) -> int | Fraction:
    return int(value) if value.denominator == 1 else value


def ct_minute(ts_utc: datetime) -> int:
    if ts_utc.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    local = ts_utc.astimezone(CT)
    return local.hour * 60 + local.minute


# ------------------------------------------------------------------ costs ----
@dataclass(frozen=True)
class BucketSlippage:
    key: str
    start_min: int  # CT minute of day, inclusive
    end_min: int  # exclusive
    half_spread_ticks: float  # s_b
    depth_ticks: Mapping[str, float]  # side -> depth term at q_c
    side_ticks: Mapping[str, float]  # side -> s_b + depth (the table's own sum, checked)


@dataclass(frozen=True)
class ProductCosts:
    """D8 for one contract, from the frozen table (units: ticks of the contract, per side)."""

    root: str
    commission_rt_cents: int
    buckets: tuple[BucketSlippage, ...]
    max_half_spread_ticks: float  # the largest s_b of the product's buckets (T12-4)

    @property
    def commission_side_cents(self) -> int:
        return self.commission_rt_cents // 2

    def bucket_at(self, ts_utc: datetime) -> BucketSlippage:
        minute = ct_minute(ts_utc)
        found = [b for b in self.buckets if b.start_min <= minute < b.end_min]
        if len(found) != 1:
            raise CostLookupError(f"{self.root}: no calibrated bucket at CT "
                                  f"{minute // 60:02d}:{minute % 60:02d} ({ts_utc.isoformat()})")
        return found[0]

    def side_slippage_ticks(self, ts_utc: datetime, side: str, in_event_window: bool) -> float:
        if side not in SIDES:
            raise ValueError(f"side must be one of {SIDES}, not {side!r}")
        bucket = self.bucket_at(ts_utc)  # a time with no bucket raises, event window or not
        if in_event_window:
            return self.max_half_spread_ticks + bucket.depth_ticks[side]
        return bucket.side_ticks[side]


def _bucket(entry: dict, root: str) -> BucketSlippage:
    if entry.get("fallback"):
        raise FrozenInputError(f"{root} bucket {entry['key']}: a fallback bucket; the event-cost "
                               "reading for fallback buckets is not encoded (none existed in E.2a)")
    half = float(entry["half_spread_ticks"])
    depth = {s: float(entry["depth_ticks"][s]) for s in SIDES}
    side = {s: float(entry["side_ticks"][s]) for s in SIDES}
    for s in SIDES:
        if abs(side[s] - (half + depth[s])) > 1e-12:
            raise FrozenInputError(f"{root} bucket {entry['key']}: side_ticks[{s}] {side[s]} != "
                                   f"half-spread {half} + depth {depth[s]}")
    return BucketSlippage(str(entry["key"]), int(entry["start_min"]), int(entry["end_min"]), half,
                          MappingProxyType(depth), MappingProxyType(side))


def _product_costs(entry: dict) -> ProductCosts:
    root = entry["product"]
    if not entry.get("calibrated", False):
        raise FrozenInputError(f"{root} was not calibrated")
    p = product(root)
    rt = _cents(entry["commission_rt_usd"])
    if rt != p.commission_rt_cents:
        raise FrozenInputError(f"{root}: cost-table commission {rt} cents != rules/products.py "
                               f"{p.commission_rt_cents}")
    if p.commission_rt_cents % 2:
        raise FrozenInputError(f"{root}: round-turn commission {p.commission_rt_cents} cents does "
                               "not split into two equal sides")
    if Fraction(str(entry["tick_value_usd"])) != Fraction(str(p.tick_value_usd)):
        raise FrozenInputError(f"{root}: cost-table tick value differs from rules/products.py")
    buckets = tuple(_bucket(b, root) for b in entry["buckets"])
    return ProductCosts(root, p.commission_rt_cents, buckets,
                        max(b.half_spread_ticks for b in buckets))


# ------------------------------------------------------------- the tables ----
@dataclass(frozen=True)
class VehicleEntry:
    exposure: str
    cluster: str
    vehicle: str
    status: str
    q_c: int


@dataclass(frozen=True)
class FrozenTables:
    hashes: Mapping[str, str]  # table name -> sha256 (verified)
    costs: Mapping[str, ProductCosts]
    vehicles: Mapping[str, VehicleEntry]  # vehicle root -> entry (traded exposures only)
    eps_operative: Mapping[str, int]  # vehicle root -> operative eps, net ticks per contract
    research_parquet_sha256: Mapping[str, str]  # contract root -> recorded research parquet sha
    day_session_ct: Mapping[str, tuple[time, time]]  # contract root -> (O_X, C_X) of D6


def _read_verified(root: Path, name: str) -> tuple[dict, str]:
    rel, expected = E2A_TABLES[name]
    path = root / rel
    if not path.is_file():
        raise FrozenInputError(f"{rel} is missing")
    digest = sha256_file(path)
    if digest != expected:
        raise FrozenInputError(f"{rel}: sha256 {digest[:12]}... is not the recorded "
                               f"{expected[:12]}...; refusing to screen on an altered table")
    return json.loads(path.read_text(encoding="utf-8")), digest


def _vehicles(raw: dict) -> dict[str, VehicleEntry]:
    out: dict[str, VehicleEntry] = {}
    for e in raw["exposures"]:
        if e["status"] not in TRADED_STATUSES:
            continue
        v = VehicleEntry(e["exposure"], e["cluster"], e["vehicle"], e["status"], int(e["q_c"]))
        if v.vehicle in out:
            raise FrozenInputError(f"{v.vehicle} is the vehicle of two exposures")
        out[v.vehicle] = v
    return out


def _hm(text: str) -> time:
    return time.fromisoformat(text)


def build_tables(root: Path) -> FrozenTables:
    costs_raw, h_costs = _read_verified(root, "costs")
    sizes_raw, h_sizes = _read_verified(root, "sizes")
    veh_raw, h_veh = _read_verified(root, "vehicles")
    eps_raw, h_eps = _read_verified(root, "epsilon")
    vehicles = _vehicles(veh_raw)
    eps = {e["vehicle"]: int(e["eps_operative"]) for e in eps_raw["exposures"]}
    for v, entry in vehicles.items():
        if v not in eps:
            raise FrozenInputError(f"{v}: traded vehicle without an operative eps")
        eps_q = {e["vehicle"]: int(e["q_c"]) for e in eps_raw["exposures"]}[v]
        if eps_q != entry.q_c:
            raise FrozenInputError(f"{v}: q_c {entry.q_c} (vehicles) != {eps_q} (epsilon)")
    contracts = sizes_raw["contracts"]
    return FrozenTables(
        hashes=MappingProxyType({"costs": h_costs, "sizes": h_sizes, "vehicles": h_veh,
                                 "epsilon": h_eps}),
        costs=MappingProxyType({r: _product_costs(e) for r, e in costs_raw["products"].items()
                                if e.get("calibrated", False)}),
        vehicles=MappingProxyType(vehicles),
        eps_operative=MappingProxyType(eps),
        research_parquet_sha256=MappingProxyType(
            {r: c["parquet_sha256"] for r, c in contracts.items() if c.get("parquet_sha256")}
            | {"MES": MES_RESEARCH_SHA256}),
        day_session_ct=MappingProxyType(
            {r: (_hm(c["O_X"]), _hm(c["C_X"])) for r, c in contracts.items()}),
    )


@functools.cache
def load_frozen_tables() -> FrozenTables:
    """The verified E.2a tables of this repository (cached once per process)."""
    return build_tables(REPO_ROOT)


# --------------------------------------------------------------- per leg ----
@dataclass(frozen=True)
class LegInputs:
    """Everything the engine needs about one leg. ``vehicle`` is None for a signal leg."""

    root: str
    product: Product
    tick_value_cents: int | Fraction
    costs: ProductCosts | None  # None for a signal leg
    vehicle: VehicleEntry | None
    eps_ticks: int | None
    research_parquet_sha256: str | None


def leg_inputs(root: str, *, traded: bool, tables: FrozenTables | None = None) -> LegInputs:
    """The frozen inputs of a leg. A traded leg must be a Stage E vehicle."""
    t = tables if tables is not None else load_frozen_tables()
    p = product(root)
    tv = _int_if_whole(_cents(p.tick_value_usd))
    if not traded:
        return LegInputs(root, p, tv, None, None, None, t.research_parquet_sha256.get(root))
    if root not in t.vehicles:
        raise FrozenInputError(f"{root} is not a traded Stage E vehicle (reports/stage_e2a_"
                               f"vehicles.json statuses {TRADED_STATUSES}); it can only be a "
                               "signal leg")
    if root not in t.costs:
        raise FrozenInputError(f"{root}: no calibrated cost model")
    return LegInputs(root, p, tv, t.costs[root], t.vehicles[root], t.eps_operative[root],
                     t.research_parquet_sha256.get(root))


def slippage_cents(qty: int, slip_ticks: float, tick_value_cents: int | Fraction) -> int:
    """ceil to the cent, as sim.fill_model.slippage_cents (the round() strips float noise)."""
    return math.ceil(round(qty * slip_ticks * float(tick_value_cents), 6))


__all__ = [
    "E2A_TABLES", "MES_RESEARCH_SHA256", "TRADED_STATUSES", "BucketSlippage", "CostLookupError",
    "FrozenInputError", "FrozenTables", "LegInputs", "ProductCosts", "VehicleEntry",
    "build_tables", "ct_minute", "leg_inputs", "load_frozen_tables", "sha256_file",
    "slippage_cents",
]
