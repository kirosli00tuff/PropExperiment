"""CME Globex algorithm K (Configurable) for one match at one price level: spec section 3.1.

Pure functions, no I/O. Source: reports/stage_e31_pilot_spec.md section 3.1 (binding) and
reports/stage_e31_briefs/research/K_algorithm.md (parameters, step order, CME's per-step examples).

ZM outright values (``ZM_K``): TOP 100 % with TOP Min 1 and TOP Max 100, no LMM, Split 40 % FIFO /
60 % pro rata, pro-rata minimum 1, Leveling on, residual FIFO; the FIFO exception (sweep) applies.

Step order for an event's outright volume ``q`` over a level's resting orders (time priority order,
the virtual order included at its place):
0. FIFO exception: q >= the level's displayed quantity -> every order fills in time order.
1. TOP: the TOP order (if any) takes min(floor(q x TOP %), its displayed quantity, its TOP room).
2. LMM: none in futures.
3. Split of the rest q1: FIFO lots = ceil(FIFO % x q1) (exact rational arithmetic), pro rata
   the rest.
4. FIFO: the FIFO lots in time priority.
5. Pro rata: floor(w_i x lots / W) over the working quantities after steps 1 and 4 (W = their sum);
   an allocation below the pro-rata minimum is 0. The TOP order takes part with what is left of it.
6. Leveling: lots left by rounding, at most one each, to orders that took part in step 5 and got 0,
   larger working quantity first, then earlier time priority.
7. FIFO for anything still left.
Every function returns new lists; inputs are never changed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class KParams:
    top_pct: Fraction = Fraction(1)
    top_min: int = 1
    top_max: int = 100
    fifo_pct: Fraction = Fraction(2, 5)
    pr_min: int = 1
    leveling: bool = True
    fifo_exception: bool = True


ZM_K = KParams()  # spec 3.1: ZM (and ZS, ZL) outrights


def split(q: int, fifo_pct: Fraction) -> tuple[int, int]:
    """(FIFO lots, pro-rata lots): FIFO is at least its percentage, rounded up to a whole lot."""
    if q <= 0:
        return 0, 0
    fifo = min(q, math.ceil(Fraction(fifo_pct) * q))
    return fifo, q - fifo


def fifo_step(rem: list[int], lots: int) -> tuple[list[int], int]:
    """FIFO over ``rem`` (time priority order): (allocation per order, lots left unallocated)."""
    alloc = [0] * len(rem)
    left = max(0, lots)
    for i, have in enumerate(rem):
        if left == 0:
            break
        take = min(have, left)
        if take > 0:
            alloc[i] = take
            left -= take
    return alloc, left


def pro_rata_step(rem: list[int], lots: int, pr_min: int) -> tuple[list[int], list[bool]]:
    """Pro rata of ``lots`` over the working quantities ``rem``: (allocation, participated).
    An order participates when it has working quantity; its share is floor(w x lots / W) and an
    allocation below ``pr_min`` is 0."""
    total = sum(rem)
    participated = [w > 0 for w in rem]
    if lots <= 0 or total <= 0:
        return [0] * len(rem), participated
    alloc = []
    for w in rem:
        share = (w * lots) // total if w > 0 else 0
        alloc.append(min(share, w) if share >= pr_min else 0)
    return alloc, participated


def leveling_step(rem: list[int], pr_alloc: list[int], participated: list[bool],
                  lots: int) -> list[int]:
    """At most one lot each to orders that took part in pro rata and got 0 from it, larger
    working quantity first (``rem``: working quantity at the time of distribution), then earlier
    time priority (lower index)."""
    alloc = [0] * len(rem)
    if lots <= 0:
        return alloc
    order = sorted((i for i in range(len(rem))
                    if participated[i] and pr_alloc[i] == 0 and rem[i] > 0),
                   key=lambda i: (-rem[i], i))
    left = lots
    for i in order:
        if left == 0:
            break
        alloc[i] = 1
        left -= 1
    return alloc


def _add(a: list[int], b: list[int]) -> list[int]:
    return [x + y for x, y in zip(a, b, strict=True)]


def _sub(a: list[int], b: list[int]) -> list[int]:
    return [x - y for x, y in zip(a, b, strict=True)]


def allocate_steps(qty: list[int], q: int, top: int | None = None, top_room: int | None = None,
                   params: KParams = ZM_K) -> dict[str, list[int] | int | bool]:
    """Every step's allocation of an event's outright volume ``q`` over ``qty`` (displayed
    working quantities in time priority order). ``top``: index of the level's TOP order, or None;
    ``top_room``: TOP Max minus the lots already counted against it (default TOP Max).
    Keys: fifo_exception, top, fifo, pro_rata, leveling, residual (lists), total (list),
    unallocated (int)."""
    n = len(qty)
    zero = [0] * n
    out: dict[str, list[int] | int | bool] = {
        "fifo_exception": False, "top": zero, "fifo": zero, "pro_rata": zero,
        "leveling": zero, "residual": zero, "total": zero, "unallocated": max(0, q)}
    if q <= 0 or n == 0:
        return out
    if any(w < 0 for w in qty):
        raise ValueError(f"negative working quantity in {qty}")
    rem = list(qty)
    if params.fifo_exception and q >= sum(rem):
        alloc, left = fifo_step(rem, q)
        return {**out, "fifo_exception": True, "residual": alloc, "total": alloc,
                "unallocated": left}
    top_alloc = list(zero)
    left = q
    if top is not None and 0 <= top < n:
        room = params.top_max if top_room is None else max(0, top_room)
        take = min(math.floor(Fraction(params.top_pct) * left), rem[top], room)
        if take > 0:
            top_alloc[top] = take
            left -= take
    rem = _sub(rem, top_alloc)
    fifo_lots, pr_lots = split(left, params.fifo_pct)
    fifo_alloc, fifo_left = fifo_step(rem, fifo_lots)
    rem = _sub(rem, fifo_alloc)
    pr_alloc, participated = pro_rata_step(rem, pr_lots, params.pr_min)
    rem = _sub(rem, pr_alloc)
    rest = fifo_left + pr_lots - sum(pr_alloc)
    lev_alloc = (leveling_step(rem, pr_alloc, participated, rest) if params.leveling
                 else list(zero))
    rem = _sub(rem, lev_alloc)
    rest -= sum(lev_alloc)
    res_alloc, unallocated = fifo_step(rem, rest)
    total = _add(_add(_add(_add(top_alloc, fifo_alloc), pr_alloc), lev_alloc), res_alloc)
    return {"fifo_exception": False, "top": top_alloc, "fifo": fifo_alloc, "pro_rata": pr_alloc,
            "leveling": lev_alloc, "residual": res_alloc, "total": total,
            "unallocated": unallocated}


def allocate(qty: list[int], q: int, top: int | None = None, top_room: int | None = None,
             params: KParams = ZM_K) -> list[int]:
    """Total lots each order receives from the event (see ``allocate_steps``)."""
    total = allocate_steps(qty, q, top, top_room, params)["total"]
    assert isinstance(total, list)
    return total
