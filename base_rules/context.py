"""Building a run context from the frozen inputs (E.17) or from objects (tests, the probe)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any

from base_rules import constants as K
from base_rules import hist_plan as HP
from base_rules.auctions import Auction, load_auctions
from base_rules.calendars import GroupCalendars, load_calendars
from base_rules.common import RunContext
from base_rules.costs import ReleaseRules, build_release_rules
from base_rules.inputs import SettlementTable, load_settlement, load_windows
from base_rules.store import EXT2010, STEP2_ERA, ProductBars, RunManifest, load_product
from base_rules.touch import touching_types
from screening.stage_e_rules import ReleaseCalendar


def empty_release_rules() -> ReleaseRules:
    cal = ReleaseCalendar(MappingProxyType({}), (), date(2010, 6, 1), K.WINDOW_LAST, "0" * 64,
                          "none")
    return ReleaseRules(cal, {}, frozenset(), {"note": "no releases"})


def starts_for(manifest: RunManifest | None, windows: Mapping[str, date] | None = None,
               products=K.PRODUCTS) -> dict[str, date]:
    """Window start per product: U2's (``windows``, else the constants) or the fallback."""
    full = windows or K.WINDOW_START
    return {p: (K.FALLBACK_FIRST if manifest is not None and manifest.fallback(p)
                else full[p]) for p in products}


def store_loader(manifest: RunManifest, calendars: Mapping[str, GroupCalendars],
                 resolver: HP.Resolver = HP.default_resolver) -> Callable[[str], ProductBars]:
    def load(p: str) -> ProductBars:
        cals = calendars[K.GROUP_OF[p]]
        return load_product(p, manifest.stores[p], {EXT2010: cals.hist, STEP2_ERA: cals.frozen},
                            resolver)

    return load


def make_context(calendars: Mapping[str, GroupCalendars], settlement: SettlementTable,
                 starts: Mapping[str, date], load_bars: Callable[[str], ProductBars],
                 auctions: tuple[Auction, ...] = (), releases: ReleaseRules | None = None,
                 release_paths: Mapping[str, Any] | None = None) -> RunContext:
    """``releases`` None: built from ``release_paths`` (frozen, hist, auctions) with the touch
    report's fallback (costs.build_release_rules)."""
    ctx = RunContext(calendars, settlement, dict(starts), releases or empty_release_rules(),
                     load_bars, tuple(auctions))
    if releases is None:
        touching = touching_types(ctx, **(release_paths or {}))
        ctx.releases = build_release_rules(touching=touching, **(release_paths or {}))
    return ctx


def context_from_freeze(freeze: Mapping[str, Any], manifest: RunManifest,
                        resolver: HP.Resolver = HP.default_resolver) -> RunContext:
    """E.17's context: every input from the freeze's paths (already hash-checked)."""
    inputs = freeze["inputs"]
    pins = {g: inputs[f"hist_calendar_{g}"]["sha256"] for g in K.HIST_GROUPS_FROZEN}
    pins[K.LIVESTOCK] = inputs["livestock_hist"]["sha256"]
    calendars = load_calendars(hist_dir=Path(inputs["hist_calendar_equity"]["path"]).parent,
                               livestock_path=Path(inputs["livestock_hist"]["path"]), pins=pins)
    settlement = load_settlement(Path(inputs["settlement"]["path"]))
    windows = load_windows(Path(inputs["windows"]["path"]))
    auctions, _ = load_auctions(Path(inputs["ecauc_hist"]["path"]),
                                Path(inputs["release_frozen"]["path"]),
                                Path(inputs["ecauc_announcements"]["path"]))
    paths = {"frozen_path": Path(inputs["release_frozen"]["path"]),
             "hist_path": Path(inputs["release_hist"]["path"]),
             "auctions_path": Path(inputs["ecauc_hist"]["path"])}
    return make_context(calendars, settlement, starts_for(manifest, windows),
                        store_loader(manifest, calendars, resolver), tuple(auctions), None,
                        paths)


__all__ = ["context_from_freeze", "empty_release_rules", "make_context", "starts_for",
           "store_loader"]
