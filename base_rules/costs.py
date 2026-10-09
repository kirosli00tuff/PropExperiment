"""Per-fill costs in exact cents (lead_spec section 1, U3a) and the release rules of the fills.

One fill of one vehicle contract pays, per side, the frozen D8 cost the engine charges
(screening.stage_e_rules.StageERules._market_cost at qty 1): commission per side plus
ceil(slippage ticks x tick value) with the slippage of screening.stage_e_frozen.ProductCosts.
side_slippage_ticks at the fill bar's open (the fill minute's 30-minute CT bucket; in a D8 event
window the product's largest half-spread plus the bucket's depth term). Cases: base; stress =
base + one vehicle tick per side; slip150 = commission + ceil(1.5 x slippage ticks x tick value).

Release rules: the event window [r, r + 30 min) and the D9.5a fill guard [r, r + 2 min) of the
release rows concerning the product (its price-path root or its vehicle root), through the frozen
screening.stage_e_rules.ReleaseCalendar built by release_calendar_from_dict from: the frozen D8
calendar's rows 2019-05-01..2024-02-29, E.14's FOMC/NGS/WPSR rows before 2019-05-01 (a row without
an instant becomes every clock time its type uses, conservative), and Task 3b's EC-AUC rows before
2019-05-01. Release types that touch an H fill minute in 2019-05..2024-02 and have no row before
2019-05-01 get the conservative fallback: before 2019-05-01, a fill whose CT minute lies in
[t, t + 30) for a clock time t of the type pays the event cost, and none lies in [t, t + 2).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from base_rules import constants as K
from base_rules.inputs import read_json
from screening.stage_e_frozen import (
    CostLookupError,
    ProductCosts,
    ct_minute,
    leg_inputs,
    slippage_cents,
)
from screening.stage_e_rules import (
    RELEASE_CALENDAR_SCHEMA,
    ReleaseCalendar,
    release_calendar_from_dict,
)

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000
Money = int | Fraction


class CostError(RuntimeError):
    """A fill has no frozen cost (no calibrated bucket at its minute)."""


# ------------------------------------------------------------------ vehicle costs ----
@dataclass
class VehicleCost:
    """The vehicle of a price path (E.12, D2): its frozen D8 costs and tick value in cents."""

    path_root: str
    vehicle: str
    costs: ProductCosts
    tick_value_cents: Money
    _cache: dict = field(default_factory=dict, repr=False)

    def fill_costs(self, ts_ns: int, side: str, event: bool) -> tuple[dict[str, Money], bool]:
        """({case: cents}, uncalibrated) for one contract filled at the bar opening at ``ts_ns``.
        Ruling R-B2: a fill minute whose 30-minute CT bucket has no frozen calibration pays,
        per side, the product's LARGEST per-side slippage over its frozen buckets (s_b plus that
        bucket's depth term), D8's own rule for a bucket quoted on fewer than 3 of 5 dates."""
        at = datetime.fromtimestamp(ts_ns / NS, tz=UTC)
        key = (ct_minute(at), side, event)
        got = self._cache.get(key)
        if got is None:
            uncalibrated = False
            try:
                slip = self.costs.side_slippage_ticks(at, side, event)
            except CostLookupError:
                if side not in ("buy", "sell"):
                    raise
                slip = max(b.side_ticks[side] for b in self.costs.buckets)
                uncalibrated = True
            tv = self.tick_value_cents
            comm = self.costs.commission_side_cents
            base = comm + slippage_cents(1, slip, tv)
            got = ({K.BASE: base, K.STRESS: base + K.STRESS_EXTRA_TICKS * tv,
                    K.SLIP150: comm + slippage_cents(1, slip * float(K.SLIPPAGE_MULTIPLE), tv)},
                   uncalibrated)
            self._cache[key] = got
        return got


def vehicle_cost(path_root: str) -> VehicleCost:
    leg = leg_inputs(K.VEHICLE_OF[path_root], traded=True)
    assert leg.costs is not None
    return VehicleCost(path_root, leg.root, leg.costs, leg.tick_value_cents)


# ------------------------------------------------------------------ release rules ----
@dataclass(frozen=True)
class ReleaseRules:
    calendar: ReleaseCalendar
    fallback: Mapping[str, tuple[int, ...]]  # root -> CT minutes t (fills before 2019-05-01)
    hist_types: frozenset[str]
    record: Mapping[str, Any]

    def _roots(self, path_root: str) -> tuple[str, str]:
        return path_root, K.VEHICLE_OF.get(path_root, path_root)

    def _fallback_hit(self, path_root: str, ts_ns: int, width: int) -> bool:
        local = datetime.fromtimestamp(ts_ns / NS, tz=UTC).astimezone(CT)
        if local.date() >= K.FROZEN_CAL_FIRST:
            return False
        m = local.hour * 60 + local.minute
        return any(t <= m < t + width for r in self._roots(path_root)
                   for t in self.fallback.get(r, ()))

    def event(self, path_root: str, ts_ns: int) -> bool:
        return any(self.calendar.in_event_window(r, ts_ns) for r in self._roots(path_root)) \
            or self._fallback_hit(path_root, ts_ns, K.EVENT_MINUTES)

    def guard(self, path_root: str, ts_ns: int) -> bool:
        return any(self.calendar.in_fill_guard(r, ts_ns) for r in self._roots(path_root)) \
            or self._fallback_hit(path_root, ts_ns, K.GUARD_MINUTES)


def _ct_minute_of(instant: str) -> int:
    dt = datetime.fromisoformat(instant.replace("Z", "+00:00")).astimezone(CT)
    return dt.hour * 60 + dt.minute


def _instant_at(day: date, minute: int) -> str:
    local = datetime(day.year, day.month, day.day, minute // 60, minute % 60, tzinfo=CT)
    return local.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _row(row: dict, instant: str) -> dict:
    return {"id": row.get("id"), "release": row.get("release"), "instant_utc": instant,
            "products": list(row.get("products") or []), "cpi": bool(row.get("cpi", False))}


def combine_rows(frozen: Iterable[dict], hist: Iterable[dict], auctions: Iterable[dict]
                 ) -> tuple[list[dict], dict[str, Any]]:
    """The cost rule's release rows 2010-06..2024-02 (module docstring)."""
    rows, expanded = [], []
    for row in frozen:
        day = date.fromisoformat(str(row["date"]))
        if K.FROZEN_CAL_FIRST <= day <= K.WINDOW_LAST:
            rows.append(_row(row, row["instant_utc"]))
    hist = [r for r in hist if date.fromisoformat(str(r["date"])) < K.FROZEN_CAL_FIRST]
    hist += [r for r in auctions if date.fromisoformat(str(r["date"])) < K.FROZEN_CAL_FIRST]
    times: dict[str, set[int]] = {}
    for row in [*rows, *hist]:
        if row.get("instant_utc"):
            times.setdefault(str(row["release"]), set()).add(_ct_minute_of(row["instant_utc"]))
    for row in hist:
        if row.get("instant_utc"):
            rows.append(_row(row, row["instant_utc"]))
            continue
        day = date.fromisoformat(str(row["date"]))
        for m in sorted(times.get(str(row["release"]), ())):
            rows.append(_row({**row, "id": f"{row['id']}@{m}"}, _instant_at(day, m)))
        expanded.append(str(row["id"]))
    hist_types = sorted({str(r["release"]) for r in hist})
    return rows, {"hist_types": hist_types, "rows": len(rows), "expanded_no_instant": expanded,
                  "clock_times_ct": {k: sorted(v) for k, v in sorted(times.items())}}


def _rows(path: Path) -> tuple[list[dict], str]:
    raw, digest = read_json(K.repo_path(path))
    rows = raw.get("releases", raw.get("rows")) if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        raise CostError(f"{path}: no release rows")
    return rows, digest


def build_release_rules(*, frozen_path: Path = K.RELEASE_FROZEN_PATH,
                        hist_path: Path = K.RELEASE_HIST_PATH,
                        auctions_path: Path | None = K.ECAUC_HIST_PATH,
                        touching: Mapping[str, Iterable[str]] | None = None) -> ReleaseRules:
    """``touching``: release type -> roots it touched at an H fill minute in 2019-05..2024-02
    (base_rules.touch). The fallback covers those types without rows before 2019-05-01, for
    every product the type's 2019-2024 rows concern, at every CT clock time they use."""
    frozen, f_sha = _rows(frozen_path)
    hist, h_sha = _rows(hist_path)
    auctions, a_sha = ([], None) if auctions_path is None else _rows(auctions_path)
    rows, rec = combine_rows(frozen, hist, [r for r in auctions
                                            if r.get("release") == K.AUCTION_RELEASE])
    digest = hashlib.sha256(json.dumps([f_sha, h_sha, a_sha]).encode()).hexdigest()
    raw = {"schema": RELEASE_CALENDAR_SCHEMA,
           "coverage": {"first": "2010-06-01", "last": str(K.WINDOW_LAST)}, "releases": rows}
    calendar = release_calendar_from_dict(raw, digest, "base_rules combined release rows")
    hist_types = frozenset(rec["hist_types"])
    fallback: dict[str, set[int]] = {}
    in_window = [r for r in frozen if r.get("instant_utc") and K.FROZEN_CAL_FIRST
                 <= date.fromisoformat(str(r["date"])) <= K.WINDOW_LAST]
    for kind in (touching or {}):
        if kind in hist_types:
            continue
        of_kind = [r for r in in_window if r.get("release") == kind]
        minutes = {_ct_minute_of(r["instant_utc"]) for r in of_kind}
        for root in {p for r in of_kind for p in r.get("products") or ()}:
            fallback.setdefault(root, set()).update(minutes)
    record = {**rec, "inputs": {"frozen": [str(frozen_path), f_sha],
                                "hist": [str(hist_path), h_sha],
                                "auctions": [str(auctions_path), a_sha]},
              "fallback_ct_minutes": {r: sorted(v) for r, v in sorted(fallback.items())}}
    return ReleaseRules(calendar, {r: tuple(sorted(v)) for r, v in fallback.items()},
                        hist_types, record)


__all__ = ["CostError", "ReleaseRules", "VehicleCost", "build_release_rules", "combine_rows",
           "vehicle_cost"]
