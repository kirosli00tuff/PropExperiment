"""Shared types of the Stage E.19 funnel model.

Lead-defined interface; specification reports/stage_e19_briefs/sim_spec.md. The returns module
(prop_econ/returns.py) produces ``ShockSet``; the funnel simulators (prop_econ/funnel.py,
prop_econ/vec.py) consume it. Nothing here reads data or draws random numbers.

Units: a shock is a daily P&L per unit of the vehicle's own daily P&L standard deviation (sigma),
already signed for the day's position direction. ``z`` is the close (exit) P&L, ``w`` the worst
intraday P&L of the same position (w <= min(0, z) is guaranteed by the producer). Dollars per
contract come from ``ProductSpec``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# MNQ/NQ, MCL/CL, MGC/GC, M6E/6E: the micro is one tenth of the full-size contract.
MICROS_PER_FULL = 10


@dataclass(frozen=True)
class ProductSpec:
    """One price path and its vehicles.

    sigma_* are the per-contract daily P&L sd in USD (demeaned, training window).
    """

    name: str  # price path root, e.g. "NQ"
    sigma_full_usd: float  # sd of the full-size contract's day-session P&L
    # round-trip cost per full-size contract (D8 day mean, or the E.10 cost wall)
    rt_full_usd: float
    micro_name: str | None  # e.g. "MNQ"; None when no micro exists (ZN)
    # sigma_full_usd / MICROS_PER_FULL when a micro exists
    sigma_micro_usd: float | None
    rt_micro_usd: float | None  # round-trip cost per micro contract

    @property
    def has_micro(self) -> bool:
        return self.micro_name is not None


@dataclass(frozen=True)
class ShockSet:
    """Daily shocks for a batch of paths: arrays of shape (n_paths, n_days)."""

    # float64, signed standardized close P&L (mean 0 by construction before any edge)
    z: np.ndarray
    w: np.ndarray  # float64, signed standardized worst intraday P&L, w <= min(0, z)
    prod: np.ndarray  # int16, index into ``products`` for each path-day
    products: tuple[ProductSpec, ...]

    def __post_init__(self) -> None:
        if self.z.shape != self.w.shape or self.z.shape != self.prod.shape or self.z.ndim != 2:
            raise ValueError(
                f"shape mismatch: z {self.z.shape} w {self.w.shape} prod {self.prod.shape}"
            )
        if np.any(self.w > np.minimum(0.0, self.z) + 1e-12):
            raise ValueError("w must be <= min(0, z) on every path-day")
        if self.prod.size and (self.prod.min() < 0 or self.prod.max() >= len(self.products)):
            raise ValueError("prod index out of range")

    @property
    def n_paths(self) -> int:
        return int(self.z.shape[0])

    @property
    def n_days(self) -> int:
        return int(self.z.shape[1])
