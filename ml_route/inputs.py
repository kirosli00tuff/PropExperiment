"""Frozen inputs of the ML route: products, vehicles, D8 costs, sessions, S_X, release calendars.

Everything here is read from frozen files or modules, never from arguments:
- the 31 price-path contracts, clusters and F16 leads: ml_route.constants (ML-A07);
- each exposure's D2 vehicle and q_c: reports/stage_e2a_vehicles.json (sha256 checked);
- the vehicle's D8 cost surface: reports/stage_e2a_costs.json (sha256 checked), read with D8's
  literal event-window rule (lead ruling T12-4: an event-window fill pays, per side, the largest
  bucket half-spread s_b of the product plus the fill bucket's own depth term, not the table's
  ``event_window_side_ticks`` field);
- sessions: D6's day session (O_X, C_X) from the group calendar (data.group_session), F_X from
  rules.sessions (D9.1, D9.13, Topstep's schedules), early-halt dates from the group calendar;
- S_X per product (lead ruling OC-K): ``load_start_rule`` reads the ONE shared loader,
  ``screening.stage_e_start_dates.start_dates_for`` (the runner uses the same files), for every
  price-path contract with a D2 vehicle, from set ML's file; with each S_X it returns the
  sha256 of the step 2 parquet the start rule read (review F-3 (b)), to which the training
  store reader is pinned. A missing module, a root without a frozen S_X, an S_X from another
  set or a missing sha256 is refused by name (``RouteInputMissing``), never skipped;
- the scheduled-release calendar (D8's list, D9.5a, D9.12's CPI instants; lead ruling OC-J):
  ``load_event_calendar`` reads the runner's frozen file through
  ``screening.stage_e_rules.load_release_calendar`` (reports/stage_e2b_release_calendar.json).
  A price-path contract takes the release list of its D2 VEHICLE, the list the engine applies to
  the vehicle's fills at the test (train/test parity); the vehicle must be listed, and when the
  price-path root is listed too its list must be the same, else the case is refused by name
  (``ReleaseListMismatch``, a question for the lead). F13-F15, the entry guard, the target's fill
  guard and event-window cost, and the CPI exclusion all read this one list.
Tests and probes pass synthetic ones explicitly through ``RouteInputs``.

Units: a price move in the price-path contract's vendor units is converted to ticks of the
exposure's D2 vehicle by ``vehicle_ticks_per_vendor_unit`` = 1 / (path vendor factor x vehicle
tick size in exchange units) (ML-A08: both quote the same underlying in the same price units).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from zoneinfo import ZoneInfo

import numpy as np

from data.config import REPO_ROOT
from ml_route.constants import (
    CLUSTER_OF,
    COSTS_SHA256,
    EARLIEST_S_X,
    PRICE_PATH_CONTRACTS,
    TRAIN_LAST,
    VEHICLES_SHA256,
)

CT = ZoneInfo("America/Chicago")
COSTS_PATH = REPO_ROOT / "reports" / "stage_e2a_costs.json"
VEHICLES_PATH = REPO_ROOT / "reports" / "stage_e2a_vehicles.json"
NS_PER_MIN = 60_000_000_000


class RouteInputMissing(RuntimeError):
    """A frozen input the route needs does not exist yet; the job refuses by name."""


class ReleaseListMismatch(RouteInputMissing):
    """A price-path contract and its vehicle have different release lists in the calendar."""


class FrozenInputMismatch(RuntimeError):
    """A frozen table's sha256 differs from its recorded value."""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _checked_json(path: Path, expected: str) -> dict:
    got = sha256_file(path)
    if got != expected:
        raise FrozenInputMismatch(f"{path.name}: sha256 {got} != frozen {expected}")
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- D8 costs (literal) ----
@dataclass(frozen=True)
class CostBucket:
    start_min: int
    end_min: int
    half_spread: float
    depth: Mapping[str, float]  # "buy" / "sell"


@dataclass(frozen=True)
class VehicleCost:
    """D8's round-turn cost of one vehicle in its own ticks (commission / tick value + sides)."""

    root: str
    commission_rt_ticks: float
    buckets: tuple[CostBucket, ...]
    max_half_spread: float

    def bucket(self, ct_min: int) -> CostBucket | None:
        for b in self.buckets:
            if b.start_min <= ct_min < b.end_min:
                return b
        return None

    def side_ticks(self, ct_min: int, side: str, in_event_window: bool) -> float | None:
        """One side in ticks; None when no calibrated bucket covers the minute."""
        b = self.bucket(ct_min)
        if b is None:
            return None
        spread = self.max_half_spread if in_event_window else b.half_spread
        return spread + b.depth[side]

    def long_round_turn_ticks(self, entry_min: int, exit_min: int, entry_event: bool,
                              exit_event: bool) -> float | None:
        buy = self.side_ticks(entry_min, "buy", entry_event)
        sell = self.side_ticks(exit_min, "sell", exit_event)
        if buy is None or sell is None:
            return None
        return self.commission_rt_ticks + buy + sell


def vehicle_cost_from_entry(entry: dict) -> VehicleCost:
    buckets = []
    for b in entry["buckets"]:
        depth = {s: float(b["depth_ticks"][s]) for s in ("buy", "sell")}
        half = float(b["half_spread_ticks"])
        for s in ("buy", "sell"):
            if abs(half + depth[s] - float(b["side_ticks"][s])) > 1e-9:
                raise FrozenInputMismatch(f"{entry['product']} bucket {b['key']}: side_ticks is "
                                          "not half-spread plus depth")
        buckets.append(CostBucket(int(b["start_min"]), int(b["end_min"]), half,
                                  MappingProxyType(depth)))
    return VehicleCost(
        root=entry["product"],
        commission_rt_ticks=float(entry["commission_rt_usd"]) / float(entry["tick_value_usd"]),
        buckets=tuple(buckets),
        max_half_spread=max(b.half_spread for b in buckets))


# ---------------------------------------------------------------- products ----
@dataclass(frozen=True)
class ProductSpec:
    root: str  # the price-path contract (ML-A07)
    cluster: str
    group: str
    exposure: str
    vehicle: str | None  # None: D2 "no candidate", so no target and no rows (ML-A08)
    q_c: int | None
    vehicle_ticks_per_vendor_unit: float | None
    cpi_no_open: bool  # D9.12 binds on the vehicle (NQ, RTY, YM, GC, SI, HG)


def load_products(vehicles_path: Path = VEHICLES_PATH,
                  expected_sha256: str = VEHICLES_SHA256) -> dict[str, ProductSpec]:
    from rules.constraints import CPI_NO_OPEN
    from rules.products import product as product_of

    raw = _checked_json(vehicles_path, expected_sha256)
    out: dict[str, ProductSpec] = {}
    for exp in raw["exposures"]:
        paths = [p for p in PRICE_PATH_CONTRACTS if p in exp["admissible"]]
        if len(paths) != 1:
            raise FrozenInputMismatch(f"exposure {exp['exposure']}: price-path contracts {paths}")
        root = paths[0]
        if CLUSTER_OF[root] != exp["cluster"]:
            raise FrozenInputMismatch(f"{root}: cluster {exp['cluster']} != {CLUSTER_OF[root]}")
        vehicle = exp.get("vehicle")
        path_p = product_of(root)
        per_unit = None
        if vehicle is not None:
            veh_p = product_of(vehicle)
            if veh_p.exposure != path_p.exposure:
                raise FrozenInputMismatch(f"{root} and its vehicle {vehicle} differ in exposure")
            per_unit = 1.0 / (path_p.vendor_price_factor * float(veh_p.tick_size))
        out[root] = ProductSpec(root, exp["cluster"], path_p.group, exp["exposure"], vehicle,
                                exp.get("q_c"), per_unit,
                                vehicle is not None and vehicle in CPI_NO_OPEN)
    missing = set(PRICE_PATH_CONTRACTS) - set(out)
    if missing:
        raise FrozenInputMismatch(f"no exposure entry for {sorted(missing)}")
    return out


def load_vehicle_costs(products: Mapping[str, ProductSpec], costs_path: Path = COSTS_PATH,
                       expected_sha256: str = COSTS_SHA256) -> dict[str, VehicleCost]:
    raw = _checked_json(costs_path, expected_sha256)
    if raw.get("depth_term") != "applied":
        raise FrozenInputMismatch("the cost table's depth term is not applied")
    out = {}
    for spec in products.values():
        if spec.vehicle is None:
            continue
        entry = raw["products"].get(spec.vehicle)
        if entry is None or not entry.get("calibrated", False):
            raise FrozenInputMismatch(f"vehicle {spec.vehicle} is not calibrated")
        out[spec.vehicle] = vehicle_cost_from_entry(entry)
    return out


# ---------------------------------------------------------------- sessions ----
@dataclass(frozen=True)
class DayTimes:
    open_ns: int  # O_X, UTC ns
    close_ns: int  # C_X
    flatten_ns: int  # F_X
    early_halt: bool  # an early-halt or early-close date of the group calendar


def _ct_ns(day: date, at: time) -> int:
    local = datetime(day.year, day.month, day.day, at.hour, at.minute, tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * 1_000_000_000


def ct_minute_of_ns(ts_ns: int) -> int:
    local = datetime.fromtimestamp(ts_ns / 1e9, tz=UTC).astimezone(CT)
    return local.hour * 60 + local.minute


@lru_cache(maxsize=16)
def _group_calendar(group: str):  # noqa: ANN202 - data.group_session.GroupCalendar
    from data.group_session import load_group_calendar

    return load_group_calendar(group)


def _session_lookup(cal, root: str, day: date) -> tuple[time, time]:  # noqa: ANN001
    table = cal.spec_for(day).day_session_ct
    sub = getattr(cal, "subgroup_of_product", {}).get(root)
    if root in table:
        return table[root]
    if sub in table:
        return table[sub]
    if "*" in table:
        return table["*"]
    if len(set(table.values())) == 1:
        return next(iter(table.values()))
    raise RouteInputMissing(f"{root} {day}: no D6 day session in {sorted(table)}")


def day_times(root: str, group: str, day: date) -> DayTimes | None:
    """D6's O_X and C_X and D9.1's F_X on trade date ``day``; None when not a trade date."""
    from rules.sessions import flatten_time_ct

    cal = _group_calendar(group)
    if not cal.is_trade_date(day):
        return None
    f_ct = flatten_time_ct(root, day)
    if f_ct is None:
        return None
    o_ct, c_ct = _session_lookup(cal, root, day)
    return DayTimes(_ct_ns(day, o_ct), _ct_ns(day, c_ct), _ct_ns(day, f_ct),
                    cal.early_halt_ct(day) is not None)


# ---------------------------------------------------------------- events, S_X ----
@dataclass(frozen=True)
class EventCalendar:
    """Scheduled major releases per price-path product (D8's list) and the CPI instants (D9.12),
    as sorted int64 UTC ns. Known in advance (calendar availability)."""

    releases: Mapping[str, np.ndarray]
    cpi: np.ndarray
    source: str
    sha256: str
    first: date | None = None  # the calendar's coverage (None: synthetic, not checked)
    last: date | None = None

    def of(self, root: str) -> np.ndarray:
        if root not in self.releases:
            raise RouteInputMissing(f"the release calendar has no entry for {root}")
        return self.releases[root]

    def require_coverage(self, first: date, last: date, what: str) -> None:
        if self.first is None or self.last is None or self.first > first or self.last < last:
            raise RouteInputMissing(f"the release calendar ({self.first}..{self.last}, "
                                    f"{self.source}) does not cover {what} {first}..{last}")


def _ns_of(when: datetime) -> int:
    if when.tzinfo is None:
        raise RouteInputMissing(f"CPI instant {when!r} is not timezone-aware")
    return (when - datetime(1970, 1, 1, tzinfo=UTC)) // timedelta(microseconds=1) * 1000


def event_calendar_from_release(calendar, products: Mapping[str, ProductSpec]  # noqa: ANN001
                                ) -> EventCalendar:
    """The route's per-price-path view of the runner's ReleaseCalendar (see the module doc)."""
    releases: dict[str, np.ndarray] = {}
    for root, spec in products.items():
        if spec.vehicle is None:
            continue  # no vehicle: no target, no rows, no release list needed (ML-A08)
        if spec.vehicle not in calendar.by_root:
            raise RouteInputMissing(
                f"{calendar.source} lists no release for {spec.vehicle}, the vehicle of {root}: "
                "every product of the universe is listed (FOMC concerns all), so the calendar "
                "does not cover it")
        listed = tuple(int(x) for x in calendar.by_root[spec.vehicle])
        own = calendar.by_root.get(root)
        if root != spec.vehicle and own is not None and tuple(int(x) for x in own) != listed:
            raise ReleaseListMismatch(
                f"{calendar.source}: {root} ({len(own)} releases) and its vehicle {spec.vehicle} "
                f"({len(listed)}) have different release lists; which one a price-path "
                "contract's features and targets read is a question for the lead")
        releases[root] = np.array(listed, dtype=np.int64)
    cpi = np.array(sorted(_ns_of(c) for c in calendar.cpi), dtype=np.int64)
    return EventCalendar(MappingProxyType(releases), cpi, calendar.source, calendar.sha256,
                         calendar.first, calendar.last)


def load_event_calendar(products: Mapping[str, ProductSpec] | None = None,
                        repo_root: Path = REPO_ROOT) -> EventCalendar:
    """The frozen release calendar as the route reads it (the runner's file and loader, under
    ``repo_root``, the repository by default)."""
    from screening.stage_e_rules import ReleaseCalendarMissing, load_release_calendar

    try:
        calendar = load_release_calendar(Path(repo_root))
    except ReleaseCalendarMissing as exc:
        raise RouteInputMissing(f"the scheduled-release calendar is not available: {exc}") from exc
    return event_calendar_from_release(calendar, products if products is not None
                                       else load_products())


START_RULE_SET_FILE = "stage_e_start_rule_ML.json"  # the route's S_X set ("ML", OC-K)


def load_start_rule(roots: Iterable[str] | None = None, repo_root: Path = REPO_ROOT
                    ) -> tuple[dict[str, date], dict[str, str]]:
    """S_X and the pinned step 2 parquet sha256 of every price-path contract with a vehicle (or
    of ``roots``), from the shared loader ``screening.stage_e_start_dates.start_dates_for``
    (files under ``repo_root``). Refused by name: a missing module, a root without a frozen S_X
    (or with an empty window), an S_X that does not come from set ML's file
    (reports/stage_e_start_rule_ML.json), and a recorded store sha256 that is not a sha256
    (review F-3 (b): the training store is pinned to the store the start rule read)."""
    try:
        from screening import stage_e_start_dates as shared
    except ImportError as exc:
        raise RouteInputMissing(
            "screening.stage_e_start_dates (the shared S_X loader, lead ruling OC-K) is not "
            "built yet; S_X per price-path contract cannot be read") from exc
    from screening.stage_e_runner import RunnerRefusal

    if roots is None:
        roots = [p for p, s in load_products().items() if s.vehicle is not None]
    roots = list(roots)
    try:
        dates, provenance = shared.start_dates_for(roots, root=Path(repo_root))
    except RunnerRefusal as exc:
        raise RouteInputMissing(f"no frozen S_X for the route: {type(exc).__name__}: {exc}"
                                ) from exc
    shas: dict[str, str] = {}
    for root in roots:
        value = dates.get(root)
        if not isinstance(value, date) or isinstance(value, datetime):
            raise RouteInputMissing(f"S_X of {root} is {value!r}, not a date")
        prov = provenance.get(root, {})
        files = [Path(str(f.get("path", ""))).name for f in prov.get("files", ())]
        if START_RULE_SET_FILE not in files:
            raise RouteInputMissing(f"S_X of {root} comes from {files}, not from set ML's "
                                    f"{START_RULE_SET_FILE}")
        sha = prov.get("step2_sha256")
        if not (isinstance(sha, str) and len(sha) == 64
                and all(c in "0123456789abcdef" for c in sha)):
            raise RouteInputMissing(f"the start rule records no step 2 sha256 for {root}: "
                                    f"{sha!r} (review F-3)")
        shas[root] = sha
    return {r: dates[r] for r in roots}, shas


def load_start_dates(roots: Iterable[str] | None = None,
                     repo_root: Path = REPO_ROOT) -> dict[str, date]:
    """S_X only (``load_start_rule``'s first half)."""
    return load_start_rule(roots, repo_root)[0]


@dataclass(frozen=True)
class RouteInputs:
    products: Mapping[str, ProductSpec]
    costs: Mapping[str, VehicleCost]
    events: EventCalendar
    s_x: Mapping[str, date]
    provenance: Mapping[str, str] = field(default_factory=dict)
    # review F-3 (b): root -> the step 2 parquet sha256 its start rule read; the store reader
    # refuses any other file. None only for synthetic inputs (tests, probes), never from
    # load_route_inputs, which always sets one per traded root.
    step2_sha256: Mapping[str, str] | None = None

    def traded(self) -> tuple[str, ...]:
        """Price-path contracts with a D2 vehicle and an S_X (the ones that get rows)."""
        return tuple(p for p in PRICE_PATH_CONTRACTS
                     if p in self.products and self.products[p].vehicle is not None
                     and p in self.s_x)


def load_route_inputs(repo_root: Path = REPO_ROOT) -> RouteInputs:
    """E.ML-train's frozen inputs; the calendar must cover the whole training window."""
    products = load_products()
    events = load_event_calendar(products, repo_root)
    events.require_coverage(EARLIEST_S_X, TRAIN_LAST, "the training window")
    s_x, store = load_start_rule([p for p, s in products.items() if s.vehicle is not None],
                                 repo_root)
    return RouteInputs(products, load_vehicle_costs(products), events, s_x,
                       {"costs_sha256": COSTS_SHA256, "vehicles_sha256": VEHICLES_SHA256,
                        "s_x_set": "ML"}, store)


def minutes(n: int) -> timedelta:
    return timedelta(minutes=n)
