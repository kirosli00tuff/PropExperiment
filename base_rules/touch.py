"""Which release types touch an H fill minute, from the frozen 2019-05..2024-02 release calendar
alone (lead_spec section 1). A fill at instant f is touched by a release r concerning the product
(its price-path or vehicle root) when r <= f < r + 30 min (event cost) and, inside that, when
r <= f < r + 2 min (D9.5a guard). The H fill minutes: H1 S-30 and S; H4 O+1 and S-31 (every
trade date of the product); H2 the decision minute on d5 and S_X on dL (NQ, ZN); H3 S_T on t-3, t
and t+5 of the kept auction windows; roll fills, every calendar date's 23:59 and 00:00 UTC bar for
the multi-day legs (a superset of every possible splice).
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, date, datetime, time, timedelta

import numpy as np

from base_rules import constants as K
from base_rules.common import RunContext
from base_rules.costs import _ct_minute_of
from base_rules.h2 import months
from base_rules.h3 import windows
from base_rules.inputs import read_json
from data.session import ct_ns

NS_MIN = 60_000_000_000


def _ns(day: date, minute: int) -> int:
    return ct_ns(day, time(minute // 60, minute % 60))


def settle_ns(ctx: RunContext, p: str, d: date) -> int:
    """The cost-lookup instant of an exit or mark at the settlement minute (R-B1 a): bar S's
    open, or bar S-1's open when a scheduled closure begins at S (a close fill's cost is looked
    up at its bar's open, as the engine's close_cost does)."""
    s = int(ctx.settlement.settle_minute(p, d))
    return _ns(d, s - 1) if ctx.closure_at(p, d, s) else _ns(d, s)


def entry_ns(ctx: RunContext, p: str, d: date, minute: int) -> int | None:
    """An entry at the settlement or decision minute (R-B1 b); None: no entry bar."""
    return ctx.reopen_ns(p, d, minute) if ctx.closure_at(p, d, minute) else _ns(d, minute)


def fill_instants(ctx: RunContext, first: date = K.FROZEN_CAL_FIRST) -> Iterator[tuple]:
    """(test, product, trade date, fill instant ns) for every scheduled H fill in the era."""
    st = ctx.settlement
    for p in K.PRODUCTS:
        for d in ctx.cal(p).trade_dates():
            if d < first or d > ctx.last:
                continue
            if not ctx.listed(p, d):
                continue
            s, o = st.settle_minute(p, d), ctx.open_minute(p, d)
            yield "H1", p, d, _ns(d, s - K.H1_WINDOW_MIN)
            yield "H1", p, d, settle_ns(ctx, p, d)
            yield "H4", p, d, _ns(d, o + 1)
            yield "H4", p, d, _ns(d, s - K.H1_WINDOW_MIN - 1)
    for _ref, d5, d_last in months(ctx):
        if d5 < first or d_last > ctx.last:
            continue
        if any(st.settle_minute(x, d) is None for x in K.H2_LEGS for d in (d5, d_last)):
            continue
        decision = max(st.settle_minute(x, d5) for x in K.H2_LEGS)
        for x in K.H2_LEGS:
            got = entry_ns(ctx, x, d5, decision)
            if got is not None:
                yield "H2", x, d5, got
            yield "H2", x, d_last, settle_ns(ctx, x, d_last)
    from collections import Counter

    for a, before, t, after in windows(ctx, ctx.auctions, Counter()):
        for d in (before, t, after):
            if first <= d <= ctx.last and st.settle_minute(a.root, d) is not None:
                if d != before:
                    yield "H3", a.root, d, settle_ns(ctx, a.root, d)
                if d != after:
                    got = entry_ns(ctx, a.root, d, int(st.settle_minute(a.root, d)))
                    if got is not None:
                        yield "H3", a.root, d, got
    roots = sorted({*K.H2_LEGS, *K.H3_TENOR_ROOT.values()})
    d = first
    while d <= ctx.last:
        midnight = int(datetime(d.year, d.month, d.day, tzinfo=UTC).timestamp()) * 10**9
        for p in roots:
            yield "roll", p, d, midnight - NS_MIN
            yield "roll", p, d, midnight
        d += timedelta(days=1)


def hist_release_types(hist_path=K.RELEASE_HIST_PATH, auctions_path=K.ECAUC_HIST_PATH
                       ) -> set[str]:
    """Release types with rows before 2019-05-01 on disk (E.14's file; Task 3b's EC-AUC)."""
    raw, _ = read_json(K.repo_path(hist_path))
    out = {str(r["release"]) for r in raw["releases"] if str(r["date"]) < str(K.FROZEN_CAL_FIRST)}
    if auctions_path is not None and K.repo_path(auctions_path).is_file():
        out.add(K.AUCTION_RELEASE)
    return out


def release_touch(ctx: RunContext, frozen_path=K.RELEASE_FROZEN_PATH,
                  hist_types: set[str] | None = None) -> dict:
    raw, digest = read_json(K.repo_path(frozen_path))
    rows = [r for r in raw["releases"] if r.get("instant_utc") and K.FROZEN_CAL_FIRST
            <= date.fromisoformat(str(r["date"])) <= K.WINDOW_LAST]
    by_root: dict[str, list[tuple[int, str]]] = {}
    for r in rows:
        ns = int(datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00"))
                 .timestamp()) * 10**9
        for root in r.get("products") or ():
            by_root.setdefault(root, []).append((ns, str(r["release"])))
    arrays = {k: (np.array([x[0] for x in sorted(v)], dtype=np.int64), [x[1] for x in sorted(v)])
              for k, v in by_root.items()}
    out: dict[str, dict] = {}
    for test, p, d, f in fill_instants(ctx):
        for root in {p, K.VEHICLE_OF.get(p, p)}:
            if root not in arrays:
                continue
            ts, kinds = arrays[root]
            hi = int(np.searchsorted(ts, f, side="right"))
            lo = int(np.searchsorted(ts, f - K.EVENT_MINUTES * NS_MIN, side="right"))
            for j in range(lo, hi):
                kind = kinds[j]
                row = out.setdefault(kind, {"event_fills": 0, "guard_fills": 0, "products": set(),
                                            "tests": set(), "examples": []})
                row["event_fills"] += 1
                row["guard_fills"] += int(f < int(ts[j]) + K.GUARD_MINUTES * NS_MIN)
                row["products"].add(p)
                row["tests"].add(test)
                if len(row["examples"]) < 3:
                    row["examples"].append(f"{test} {p} {d} fill "
                                           f"{datetime.fromtimestamp(f / 1e9, UTC):%H:%M}Z")
    hist_types = hist_release_types() if hist_types is None else hist_types
    clock = {}
    for r in rows:
        clock.setdefault(str(r["release"]), set()).add(_ct_minute_of(r["instant_utc"]))
    return {"frozen_calendar": {"path": str(frozen_path), "sha256": digest, "rows": len(rows)},
            "types": {k: {**v, "products": sorted(v["products"]), "tests": sorted(v["tests"]),
                          "clock_times_ct": [f"{m // 60:02d}:{m % 60:02d}"
                                             for m in sorted(clock.get(k, ()))],
                          "rows_2010_2019": k in hist_types}
                      for k, v in sorted(out.items())},
            "not_touching": sorted(set(clock) - set(out))}


def touching_types(ctx: RunContext, frozen_path=K.RELEASE_FROZEN_PATH,
                   hist_path=K.RELEASE_HIST_PATH, auctions_path=K.ECAUC_HIST_PATH
                   ) -> dict[str, list[str]]:
    rep = release_touch(ctx, frozen_path, hist_release_types(hist_path, auctions_path))
    return {k: v["products"] for k, v in rep["types"].items()}


__all__ = ["fill_instants", "hist_release_types", "release_touch", "touching_types"]
