"""T4, the combined book (lead_spec section 6): base_rules.h5.combine's arithmetic on the
components T2, T3 and H2 (H2's frozen E.17 component series, not recomputed).

Grid: the union of T2's series dates, T3's series dates and H2's grid_dates; a component is 0 on
grid dates where it has no value. sigma_c(d) = sample std (ddof 1) of component c over the 60
grid dates strictly before d (base_rules.scaling.trailing_sigma); T4_d = the mean over the
components with a defined, positive sigma_c(d) of x_c(d) / sigma_c(d). The first 60 grid dates are
warm-up; a grid date with no component scaled is not in the series (counted).
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from base_rules.scaling import trailing_sigma
from multiday import constants as K


@dataclass(frozen=True)
class Component:
    name: str
    daily: Mapping[str, Mapping[date, float]]  # case -> date -> x
    grid: frozenset[date]


def component_from_series(name: str, series: Mapping[str, Sequence[tuple[date, float]]]
                          ) -> Component:
    daily = {c: dict(series[c]) for c in K.COST_CASES}
    return Component(name, daily, frozenset(d for d, _ in series[K.BASE]))


def h2_component(path: Path, expected_sha256: str | None = K.H2_RESULT_SHA256) -> Component:
    """H2's component series and grid from its E.17 result (status complete, sha256 pinned)."""
    import hashlib

    raw = Path(path).read_bytes()
    if expected_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError(f"{path}: sha256 is not the pinned {expected_sha256[:12]}...")
    rec = json.loads(raw)
    if rec.get("status") != "complete" or rec.get("test") != "H2":
        raise ValueError(f"{path}: not a complete H2 result")
    daily = {c: {date.fromisoformat(d): float(v) for d, v in rec["component"][c].items()}
             for c in K.COST_CASES}
    return Component("H2", daily, frozenset(date.fromisoformat(d) for d in rec["grid_dates"]))


def combine(components: Mapping[str, Component], *, window: int = K.T4_SIGMA_WINDOW,
            warmup: int = K.T4_WARMUP) -> tuple[dict[str, list[tuple[date, float]]], Counter,
                                                 dict[str, Counter]]:
    """(series per case, counters, per-component usage) of the equal-risk combination."""
    names = [n for n in K.T4_COMPONENTS if n in components]
    if not names:
        raise ValueError("T4 needs at least one component")
    grid = sorted(set().union(*(components[n].grid for n in names)))
    counters: Counter = Counter({"grid dates": len(grid), "warmup": min(warmup, len(grid))})
    used: dict[str, Counter] = {n: Counter() for n in names}
    series: dict[str, list[tuple[date, float]]] = {}
    for case in K.COST_CASES:
        xs = {n: [float(components[n].daily[case].get(d, 0.0)) for d in grid] for n in names}
        sig = {n: trailing_sigma(xs[n], window=window) for n in names}
        out = []
        for k, d in enumerate(grid):
            if k < warmup:
                continue
            terms = [xs[n][k] / sig[n][k] for n in names
                     if sig[n][k] is not None and sig[n][k] > 0]
            if case == K.BASE:
                for n in names:
                    used[n]["scaled" if sig[n][k] is not None and sig[n][k] > 0
                            else "no positive sigma"] += 1
            if not terms:
                if case == K.BASE:
                    counters["no component with a positive sigma"] += 1
                continue
            out.append((d, sum(terms) / len(terms)))
        series[case] = out
    counters["series dates"] = len(series[K.BASE])
    return series, counters, used


__all__ = ["Component", "combine", "component_from_series", "h2_component"]
