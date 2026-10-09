"""H5, the equal-risk daily combination of H1..H4 (lead_spec section 4, H5).

Components x_1..x_4: H1's and H4's daily pooled net series (0 on grid dates with no trade), H2's
and H3's daily mark-to-settlement net series in risk units (0 when flat). Grid: the union of the
dates on which any component is defined (any product's H1 or H4 eligible date, any open H2 or H3
date). sigma_i,d = sample std (ddof 1) of x_i over the 60 grid dates strictly before d;
H5_d = mean over the components with a defined, positive sigma_i,d of x_i,d / sigma_i,d. The
first 60 grid dates are warm-up. Each cost case builds its own H5 from that case's components.
H5 reads no bar: it combines the component series the H1..H4 runs wrote (run.py checks them).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

from base_rules import constants as K
from base_rules.common import RunOutput
from base_rules.scaling import trailing_sigma


@dataclass(frozen=True)
class Component:
    name: str
    daily: Mapping[str, Mapping[date, float]]  # case -> date -> x
    grid: frozenset[date]


def combine(components: Mapping[str, Component], *, window: int = K.H5_SIGMA_WINDOW,
            warmup: int = K.H5_WARMUP) -> RunOutput:
    names = [n for n in K.H5_COMPONENTS if n in components]
    if not names:
        raise ValueError("H5 needs at least one component")
    grid = sorted(set().union(*(components[n].grid for n in names)))
    counters: Counter = Counter({"grid dates": len(grid), "warmup": min(warmup, len(grid))})
    series: dict[str, list[tuple[date, float]]] = {}
    daily: dict[str, dict[date, float]] = {}
    used: dict[str, Counter] = {n: Counter() for n in names}
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
        daily[case] = dict(out)
    counters["units"] = len(series[K.BASE])
    return RunOutput("H5", series, daily, set(grid), counters, used, [],
                      {"components": names})


__all__ = ["Component", "combine"]
