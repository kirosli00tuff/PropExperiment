"""CALENDAR-ONLY counts for the freeze text (lead_spec section 11): no bar row is read.

Inputs: the calendars, the settlement table, the windows, the release rules (base_rules'
event-window and guard rows) and each store's METADATA (its roll instants, hence the real roll
blackout) through base_rules.store.preflight and data.stage_e_bars' metadata reader. A required
bar (MK, PS) is ASSUMED present when its minute lies inside the trade date's open intervals
(base_rules.counts.settle_ok / in_session); missing bars inside the session: 0.

Reported: rebalance dates per root and year, rebalances moved earlier (by the reason of each
later date skipped), months with no eligible rebalance date, references, T3 units and their
exclusions by reason (sigma warm-up estimated from the calendar: 60 consecutive mark pairs), S_M
and S_u per month.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import date
from pathlib import Path

from base_rules import hist_plan as HP
from base_rules.common import RunContext
from base_rules.store import EXT2010, STEP2_ERA, RunManifest, preflight
from data.stage_e_bars import _meta, splices_and_blackout
from multiday import constants as K
from multiday.daily import era_of
from multiday.signals import (
    CalendarOracle,
    divisor_su,
    divisor_table,
    rebalances,
    tom_units,
)


def metadata_blackout(ctx: RunContext, manifest: RunManifest, root: str,
                      resolver: HP.Resolver = HP.default_resolver) -> tuple[frozenset[date],
                                                                             list[str]]:
    """The root's roll blackout from its stores' metadata (preflight first; no row read)."""
    cals = ctx.cal(root)
    by_era = {EXT2010: cals.hist, STEP2_ERA: cals.frozen}
    preflight(root, manifest.stores[root], by_era, resolver)
    out: set[date] = set()
    splices: list[str] = []
    for era, ref in manifest.stores[root].items():
        if ref is None:
            continue
        meta = _meta(Path(ref.path))
        sp, bl = splices_and_blackout(root, by_era[era], meta, f"{era} {root}")
        out |= set(bl)
        splices += [str(d) for d in sp]
    return frozenset(out), splices


def _year(d: date) -> str:
    return str(d.year)


def calendar_returns_before(ctx: RunContext, oracle: CalendarOracle, root: str
                            ) -> dict[date, int]:
    """Per window trade date d: the number of mark pairs (d_prev, d') with d' < d, both marks
    possible and in one era (the calendar estimate of the defined returns before d)."""
    out, n, prev = {}, 0, None
    for d in ctx.window_dates(root):
        out[d] = n
        ok = oracle.has_mark(d)
        if ok and prev is not None and prev[1] and era_of(prev[0]) == era_of(d) and \
                ctx.cal(root).previous(d) == prev[0]:
            n += 1
        prev = (d, ok)
    return out


def calendar_counts(ctx: RunContext, blackouts: Mapping[str, frozenset[date]],
                    roots: Sequence[str] = K.ROOTS) -> dict:
    sm = divisor_table(ctx, roots)
    per_root: dict[str, dict] = {}
    toms = {}
    for r in roots:
        oracle = CalendarOracle(ctx, r, blackouts.get(r, frozenset()))
        rbs = rebalances(ctx, oracle, r)
        per_year: dict[str, Counter] = {}
        moved: Counter = Counter()
        for rb in rbs:
            y = per_year.setdefault(str(rb.month[0]), Counter())
            y["months"] += 1
            if rb.d_star is None:
                y["no eligible rebalance date"] += 1
                moved["no eligible rebalance date"] += 1
                continue
            y["rebalance dates"] += 1
            if rb.skipped:
                y["moved earlier"] += 1
                moved["moved earlier"] += 1
                moved[f"moved by {len(rb.skipped)} trade date(s)"] += 1
                for _d, why in rb.skipped:
                    moved[f"skipped date: {why}"] += 1
            for k in K.LOOKBACKS:
                if rb.refs.get(k) is None:
                    moved[f"no {k}-month reference"] += 1
        per_root[r] = {"window_start": str(ctx.starts[r]), "rebalances": len(rbs),
                       "per_year": {k: dict(v) for k, v in sorted(per_year.items())},
                       "moved_and_exclusions": dict(sorted(moved.items())),
                       "rebalances_moved": [{"month": f"{rb.month[0]}-{rb.month[1]:02d}",
                                             "e": str(rb.e), "d_star": str(rb.d_star),
                                             "skipped": [[str(d), w] for d, w in rb.skipped]}
                                            for rb in rbs if rb.skipped]}
        if r in K.T3_ROOTS:
            nret = calendar_returns_before(ctx, oracle, r)
            units = [replace(u, why="sigma warm-up (calendar estimate)")
                     if u.why is None and nret.get(u.entry, 0) < K.SIGMA_WARMUP_RETURNS else u
                     for u in tom_units(ctx, oracle, r)]
            toms[r] = (units, nret)
    su = divisor_su({r: us for r, (us, _) in toms.items()})  # lead Q2: warm-up units excluded
    t3: dict[str, dict] = {}
    for r, (units, _nret) in toms.items():
        c: Counter = Counter()
        years: dict[str, Counter] = {}
        for u in units:
            y = years.setdefault(str(u.month[0]), Counter())
            if u.why is not None:
                c[u.why] += 1
                y["sigma warm-up" if u.why.startswith("sigma") else "excluded"] += 1
                continue
            c["traded (calendar estimate)"] += 1
            y["traded"] += 1
        t3[r] = {"units": len(units), "by_reason": dict(sorted(c.items())),
                 "per_year": {k: dict(v) for k, v in sorted(years.items())}}
    return {"S_M": {f"{m[0]}-{m[1]:02d}": v for m, v in sm.items()},
            "per_root": per_root,
            "T3": {"per_root": t3, "S_u": {f"{m[0]}-{m[1]:02d}": v
                                           for m, v in sorted(su.items())}}}


def counts_md(out: dict) -> str:
    lines = ["# Stage E.21: calendar-only counts (no bar row read)", "",
             f"Written {out['written_local']}. Inputs: calendars, the settlement table, the "
             "windows, the release rules and each store's roll metadata (preflight, no row). A "
             "required bar is assumed present inside the session; missing bars inside it: 0.",
             "", "## Rebalance dates (T1, T2) per root", "",
             "| Root | Window start | Months | Rebalance dates | Moved earlier "
             "| No eligible date |",
             "|---|---|---|---|---|---|"]
    for r, row in out["counts"]["per_root"].items():
        tot: Counter = Counter()
        for v in row["per_year"].values():
            tot.update(v)
        lines.append(f"| {r} | {row['window_start']} | {tot['months']} | "
                     f"{tot['rebalance dates']} | {tot['moved earlier']} | "
                     f"{tot['no eligible rebalance date']} |")
    lines += ["", "Skipped later dates by reason, per root:", ""]
    for r, row in out["counts"]["per_root"].items():
        skipped = {k: v for k, v in row["moved_and_exclusions"].items()}
        lines.append(f"- {r}: " + ", ".join(f"{k} {v}" for k, v in skipped.items()))
    lines += ["", "## T3 units (NQ, RTY)", ""]
    for r, row in out["counts"]["T3"]["per_root"].items():
        lines.append(f"- {r}: {row['units']} months; " + ", ".join(
            f"{k} {v}" for k, v in row["by_reason"].items()))
    sm = out["counts"]["S_M"]
    vals = sorted(set(sm.values()))
    lines += ["", "## S_M (calendar-defined divisor)", "",
              f"{len(sm)} months; values {vals}. First month with each value: " + ", ".join(
                  f"{v}: {next(m for m, x in sm.items() if x == v)}" for v in vals), "",
              "Full per-month values in the JSON (S_M, T3.S_u)."]
    return "\n".join(lines) + "\n"


__all__ = ["calendar_counts", "calendar_returns_before", "counts_md", "metadata_blackout"]
