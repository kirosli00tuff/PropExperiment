"""The 2010-2019 context a frozen member and the Stage E engine run in on W_ext (brief items 1,
3; lead message 4: reproduce what changes whether and when the member enters).

The harness's calendars, session rules and member tables start in 2019. On W_ext the program's
own 2010-2019 swap is used, unchanged: pattern_search.backward (Stage E.20 B1, tables S1-S12 of
reports/stage_e20_briefs/backward_swap_table.md), ``backward_context(backward_tables())``:
- S1 data.group_session.load_group_calendar -> the seven hist calendars (data/calendars/hist2010);
- S2 rules.sessions holidays and late opens from the hist calendars;
- S3 Rule H-1 Topstep rows from the hist equity calendar and the 30-minute early-close lead for
  2010-2018 (C1's L-E5-2), so F on an early-halt date is what the harness gives in 2019-2023;
- S6 strategy.members.k2.monthend.EVENT_DATES = gen_k2_month_end.py's rule (N, N-1 of each month)
  on the hist rates calendar before 2019-05-01, the frozen table after (and S4, S5, S7-S10 for
  other members);
- S11 the release calendar: base_rules.costs.build_release_rules' combined rows (frozen D8 rows
  from 2019-05-01; E.14 FOMC/NGS/WPSR and E.16 auctions before).
Added here, both restored on exit:
- screening.stage_e_rules._calendar (a functools cache outside backward's CACHE_MODULES) is
  cleared on entry and exit, so the engine's prior-settlement calendar is the hist one inside;
- rules.price_limits.HARD_LIMIT_PRODUCTS is bound to the empty set: the price-limit table starts
  on 2019-05-01 (rules.price_limits.TABLE_WINDOW) and raises LimitPending before it, so D9.7 has
  no limit to show on any W_ext date; this is base_rules.limits' reading (a date before the table:
  no lock can be shown) carried to the entry check. Recorded as a rule not reproduced.
Nothing here reads a store.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

NOT_REPRODUCED_W_EXT = (
    "D9.7 price-limit proximity (entry refusal, forced exit, locked fills): no limit table "
    "before 2019-05-01; not applied (base_rules.limits reading RR-4)",
    "D9.12 CPI window: no CPI rows before 2019-05-01 in the combined release rows; binds only "
    "on NQ/RTY/YM/GC/SI/HG full-size or micros above 3 contracts",
    "D8 event-window cost and D9.5a fill guard: only FOMC, NGS, WPSR and Treasury-auction rows "
    "before 2019-05-01 (costs do not change an entry; the guard only delays a fill)",
)


@contextmanager
def hist_context() -> Iterator[dict[str, Any]]:
    """W_ext: backward_context plus the two bindings above; yields the tables and a record."""
    from pattern_search import backward as BW
    from rules import price_limits as pl
    from screening import stage_e_rules as SR

    tables = BW.backward_tables()
    rules = BW.backward_release_rules()
    saved_hard = pl.HARD_LIMIT_PRODUCTS
    with BW.backward_context(tables):
        SR._calendar.cache_clear()
        pl.HARD_LIMIT_PRODUCTS = frozenset()
        try:
            yield {"tables": tables, "release_rules": rules,
                   "hard_limit_products_outside": sorted(saved_hard),
                   "not_reproduced": list(NOT_REPRODUCED_W_EXT)}
        finally:
            pl.HARD_LIMIT_PRODUCTS = saved_hard
            SR._calendar.cache_clear()
    SR._calendar.cache_clear()


def backward_inputs() -> dict[str, dict[str, str]]:
    """The pinned sources of the swap (path, sha256) and the module itself."""
    from base_rules import constants as BK
    from pattern_search import backward as BW
    from screening.stage_e_frozen import sha256_file

    out = {f"backward:{k}": {"path": p, "sha256": s} for k, (p, s) in BW.SOURCES.items()}
    out["code:pattern_search/backward.py"] = {
        "path": "pattern_search/backward.py",
        "sha256": sha256_file(BK.repo_path("pattern_search/backward.py"))}
    return out


__all__ = ["NOT_REPRODUCED_W_EXT", "backward_inputs", "hist_context"]
