"""Size constraints of the Stage E members, $50K XFA (design D9.5, D9.6, D9.11, D9.12).

- Lot-equivalents (D9.6): minis 1, micros 0.1, SIL 0.2, MBT 1; held in tenths (rules.products).
- The member cap (D9.5): every member holds at most 1 lot-equivalent across all its legs, and at
  most ``member_cap_contracts(root)`` contracts of one product: floor(1 / weight), then the 50K
  volatility cap (D9.11: SIL and MHG 2, MCL and MGC 10, CL, QM, RB, HO and GC 1).
- CPI window (D9.12, facts F12.1e): no opening fill in [CPI - 5 min, CPI + 5 min] on NQ, RTY,
  YM, GC, SI or HG (and ES, a leg): such an entry is skipped for the day, not deferred. On MNQ,
  M2K, MYM, MGC, SIL and MHG (and MES) an opening fill in the window is at most 3 contracts (the
  $50K figure). The CPI release instants are an input; the release calendar is E.2b's.

Every check returns None (proceed) or a ``Refusal`` with its arithmetic, as rules.xfa_rules does.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta

from rules.products import MEMBER_CAP_TENTHS, TENTHS_PER_LOT, member_cap_contracts, product
from rules.xfa_rules import Refusal

# D9.12, facts F12.1e. ES and MES are listed by Topstep; in Stage E they are legs only.
CPI_NO_OPEN: frozenset[str] = frozenset({"NQ", "RTY", "YM", "GC", "SI", "HG", "ES"})
CPI_MICRO_LIMITED: frozenset[str] = frozenset({"MNQ", "M2K", "MYM", "MGC", "SIL", "MHG", "MES"})
CPI_MICRO_MAX_50K = 3
CPI_HALF_WINDOW = timedelta(minutes=5)


def lot_equivalents_tenths(positions: Mapping[str, int]) -> int:
    """Sum of |contracts| x weight over every product, in tenths of a lot."""
    return sum(abs(q) * product(root).lot_weight_tenths for root, q in positions.items())


def _lots(tenths: int) -> str:
    return f"{tenths / TENTHS_PER_LOT:.1f}"


def check_member_size(positions_after: Mapping[str, int]) -> Refusal | None:
    """D9.5 and D9.11 on a member's positions after a fill (signed contracts per product)."""
    for root, q in positions_after.items():
        cap = member_cap_contracts(root)
        if abs(q) > cap:
            return Refusal(
                "member_product_cap_exceeded",
                f"|{q}| {root} > cap {cap} (floor(1 lot / {_lots(product(root).lot_weight_tenths)}"
                f" lot) and the 50K volatility cap)",
            )
    total = lot_equivalents_tenths(positions_after)
    if total > MEMBER_CAP_TENTHS:
        return Refusal(
            "member_lot_equivalent_cap_exceeded",
            f"{_lots(total)} lot-equivalents > {_lots(MEMBER_CAP_TENTHS)} "
            f"({', '.join(f'{r} {q}' for r, q in sorted(positions_after.items()) if q)})",
        )
    return None


def _in_cpi_window(fill_ts: datetime, cpi_releases: Iterable[datetime]) -> datetime | None:
    if fill_ts.tzinfo is None:
        raise ValueError("fill timestamp must be timezone-aware")
    for release in cpi_releases:
        if release.tzinfo is None:
            raise ValueError("CPI release timestamps must be timezone-aware")
        if release - CPI_HALF_WINDOW <= fill_ts <= release + CPI_HALF_WINDOW:
            return release
    return None


def check_cpi_opening(
    root: str, fill_ts: datetime, opening_contracts: int, cpi_releases: Iterable[datetime]
) -> Refusal | None:
    """D9.12 for an opening (position-increasing) fill of ``opening_contracts`` at ``fill_ts``.

    A refusal on a CPI_NO_OPEN product means the entry is skipped for the day (not deferred).
    """
    if opening_contracts <= 0:
        return None
    release = _in_cpi_window(fill_ts, cpi_releases)
    if release is None:
        return None
    if root in CPI_NO_OPEN:
        return Refusal(
            "cpi_window_no_opening",
            f"{root} opening fill at {fill_ts.isoformat()} lies in [CPI - 5 min, CPI + 5 min] "
            f"around {release.isoformat()}; skipped for the day",
        )
    if root in CPI_MICRO_LIMITED and opening_contracts > CPI_MICRO_MAX_50K:
        return Refusal(
            "cpi_window_micro_limit",
            f"{root} opening fill of {opening_contracts} > {CPI_MICRO_MAX_50K} contracts in the "
            f"CPI window around {release.isoformat()} ($50K figure)",
        )
    return None
