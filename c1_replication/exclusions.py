"""Ruling C12 for test C1: the NG dates excluded as unsourced, from the calendars alone.

No bar is read: the exclusion and its share follow from the pinned calendar files, so the
evaluation checks them BEFORE its run-once marker.

- Candidate dates: every weekday d of the test window (2010-06-07..2019-04-30) that the hist
  energy calendar does not source as a full closure (a sourced closure is not an NG date; an
  unsourced one stays a candidate, since its status is unknown).
- d is excluded (each reason recorded; the first in this order is d's "first reason"):
  1. "energy_unsourced": d is unsourced in the energy calendar (NG's own sessions);
  2. "energy_prior_unsourced": NG's prior energy trade date, or any weekday between it and d, is
     unsourced (G5, G8 and the session's evening segment read that date; an unverified closure
     books its bars into d; the same rule as test C2's prior_trade_date_unsourced);
  3. "equity_unsourced": d is unsourced in the equity calendar (Topstep's flatten rows are
     derived from it by Rule H-1, so F on d is not established);
  4. "<group>_unsourced" for rates, fx, metals, grains: a G17 leg's own session status on d is
     unknown (its store drops that date's bars);
  5. "release_unsourced": a release of NG's D8 list on d is unsourced or graded neither "official"
     nor "secondary" (the release-window rule, D8's event window and G13-G15 read it).
- share = excluded / candidates; ruling C12 stops when share > C12_MAX_SHARE (0.02).
The excluded dates enter the frozen pipeline as NG's own excluded dates (clock.decision_rows'
exclude map, the slot V2.2 uses for roll-blackout dates): no NG decision row exists on them.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from c1_replication.constants import C12_MAX_SHARE, WINDOW_FIRST, WINDOW_LAST

LEG_GROUPS = ("equity", "rates", "fx", "metals", "grains")
REASONS = ("energy_unsourced", "energy_prior_unsourced", "equity_unsourced", "rates_unsourced",
           "fx_unsourced", "metals_unsourced", "grains_unsourced", "release_unsourced")
PRIOR_SEARCH_DAYS = 10  # data.group_session.previous_trade_date's max_back


@dataclass(frozen=True)
class C12Result:
    first: date
    last: date
    candidates: tuple[date, ...]
    excluded: Mapping[date, tuple[str, ...]]
    max_share: float = C12_MAX_SHARE
    notes: Mapping[str, Any] = field(default_factory=dict)

    @property
    def n_candidates(self) -> int:
        return len(self.candidates)

    @property
    def share(self) -> float:
        return len(self.excluded) / self.n_candidates if self.n_candidates else 1.0

    @property
    def stops(self) -> bool:
        return self.share > self.max_share

    def excluded_dates(self) -> frozenset[date]:
        return frozenset(self.excluded)

    def record(self) -> dict[str, Any]:
        first = Counter(r[0] for r in self.excluded.values())
        every = Counter(x for r in self.excluded.values() for x in r)
        return {"window": [self.first.isoformat(), self.last.isoformat()],
                "candidates": self.n_candidates, "excluded": len(self.excluded),
                "share": self.share, "max_share": self.max_share, "stops": self.stops,
                "by_first_reason": {k: first.get(k, 0) for k in REASONS},
                "by_reason": {k: every.get(k, 0) for k in REASONS},
                "excluded_dates": {d.isoformat(): list(r) for d, r in sorted(
                    self.excluded.items())}}


def _weekdays(first: date, last: date) -> list[date]:
    days = (first + timedelta(days=i) for i in range((last - first).days + 1))
    return [d for d in days if d.weekday() < 5]


def _prior_unsourced(energy: Any, day: date) -> bool:  # noqa: ANN401
    """The prior energy trade date of ``day``, or a weekday between it and ``day``, is
    unsourced (no prior trade date within the search: True, it is not established)."""
    for n in range(1, PRIOR_SEARCH_DAYS + 1):
        d = day - timedelta(days=n)
        if d.weekday() >= 5:
            continue
        if energy.is_unsourced(d):
            return True
        if energy.is_trade_date(d):
            return False
    return True


def c12_exclusions(calendars: Mapping[str, Any], release_unsourced: Sequence[date] | Mapping,
                   *, first: date = WINDOW_FIRST, last: date = WINDOW_LAST,
                   max_share: float = C12_MAX_SHARE) -> C12Result:
    """Ruling C12 on the calendars (module docstring)."""
    energy = calendars["energy"]
    rel = frozenset(release_unsourced)
    candidates: list[date] = []
    excluded: dict[date, tuple[str, ...]] = {}
    for d in _weekdays(first, last):
        if energy.is_full_closure(d) and not energy.is_unsourced(d):
            continue
        candidates.append(d)
        reasons = []
        if energy.is_unsourced(d):
            reasons.append("energy_unsourced")
        if _prior_unsourced(energy, d):
            reasons.append("energy_prior_unsourced")
        reasons += [f"{g}_unsourced" for g in LEG_GROUPS if calendars[g].is_unsourced(d)]
        if d in rel:
            reasons.append("release_unsourced")
        if reasons:
            excluded[d] = tuple(reasons)
    return C12Result(first, last, tuple(candidates), excluded, max_share)


__all__ = ["LEG_GROUPS", "REASONS", "C12Result", "c12_exclusions"]
