"""The evaluation of E21-T1..T4 on a run context (no guard here: run.py checks the freeze, the
registration, the run manifest and the stores, and writes the run-once marker, before calling
``evaluate``). Roots are loaded one at a time; no data condition raises (R-B3): a refused store
excludes the root (counted, the reason in the notes)."""

from __future__ import annotations

import gc
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from base_rules.common import RunContext, load_or_exclude, lock_rule
from multiday import constants as K
from multiday.book import (
    BookResult,
    RootData,
    assemble,
    process_root,
    series_dates,
    simulate_book,
    t3_orders,
    t12_orders,
)
from multiday.combine import Component, combine, component_from_series
from multiday.signals import divisor_su, divisor_table
from multiday.stats import bootstrap_sharpe, case_stats, own_t, per_year


@dataclass
class TestOutput:
    test: str
    series: dict[str, list[tuple[date, float]]]
    counters: Counter
    per_root: dict[str, dict] = field(default_factory=dict)
    fills_by_kind: dict[str, dict] = field(default_factory=dict)
    gross_costs: dict[str, dict] = field(default_factory=dict)
    notes: dict[str, Any] = field(default_factory=dict)
    holdings: dict[str, list[dict]] = field(default_factory=dict)
    fills: dict[str, list[dict]] = field(default_factory=dict)

    def record(self) -> dict:
        base = [v for _, v in self.series[K.BASE]]
        return {
            "test": self.test, "test_id": K.TEST_IDS[self.test],
            "series": {c: [[str(d), v] for d, v in s] for c, s in self.series.items()},
            "stats": {c: case_stats([v for _, v in s], K.NW_LAGS[self.test])
                      for c, s in self.series.items()},
            "sharpe_ci95_base": bootstrap_sharpe(base),
            "per_year_base": per_year(self.series[K.BASE]),
            "per_root": self.per_root, "fills_by_kind": self.fills_by_kind,
            "gross_costs": self.gross_costs,
            "exclusions": dict(sorted(self.counters.items())), "notes": self.notes}


@dataclass
class EvalOutput:
    tests: dict[str, TestOutput]
    roots: dict[str, dict]  # per-root rows for the descriptive economics (spec 10)
    notes: dict[str, Any]


def _book_summary(out: TestOutput, books: Mapping[str, BookResult], dates: Sequence[date],
                  per_root: Mapping[str, dict]) -> None:
    kinds: dict[str, dict] = {}
    diag: Counter = Counter()
    for b in books.values():
        out.counters.update(b.counters)
        for f in b.fills:
            for kind in f["kind"].split("+"):
                row = kinds.setdefault(kind, {"fills": 0, "abs_contracts_per_capital": 0.0})
                row["fills"] += 1
                row["abs_contracts_per_capital"] += abs(f["trade"])
            diag["fills"] += 1
            diag["fills in an event window"] += int(f["event"])
            diag["fills in an uncalibrated bucket (R-B2)"] += int(f["uncalibrated"])
            diag["diag: fills the limit-lock test flags (not moved)"] += int(f["locked"])
            diag["diag: 2010-2019 fill bars with high == low"] += int(f["flat_bar"])
            diag["diag: forced fills inside a guard window"] += int(f["guard"])
    out.fills_by_kind = dict(sorted(kinds.items()))
    out.notes["fill_diagnostics"] = dict(diag)
    gross = sum(sum(b.gross.values()) for b in books.values())
    for c in K.COST_CASES:
        cost = sum(sum(b.cost[c].values()) for b in books.values())
        out.gross_costs[c] = {"gross": gross, "costs": cost, "net": gross - cost,
                              "costs_share_of_gross": (cost / gross) if gross else None}
    for r, b in books.items():
        net = per_root[r]["net_base"]
        vals = [net.get(d, 0.0) for d in dates]
        out.per_root[r] = {"contribution_base": float(sum(net.values())), "n": len(vals),
                           "own_t": own_t(vals), "fills": len(b.fills),
                           "gross": float(sum(b.gross.values())),
                           "costs": {c: float(sum(b.cost[c].values())) for c in K.COST_CASES}}
        out.holdings[r] = b.holdings
        out.fills[r] = b.fills


def _return_counts(rds: Mapping[str, RootData], roots: Sequence[str]) -> Counter:
    """FR-6: daily returns skipped by sigma (e.g. "return undefined: previous mark missing"),
    in total and per root ("<ROOT>: <reason>")."""
    out: Counter = Counter()
    for r in roots:
        if r not in rds:
            continue
        for k, v in rds[r].counters.items():
            if k.startswith("return undefined"):
                out[k] += v
                out[f"{r}: {k}"] += v
    return out


def _first_fill(books: Mapping[str, BookResult]) -> date | None:
    days = [date.fromisoformat(f["date"]) for b in books.values() for f in b.fills]
    return min(days) if days else None


def evaluate(ctx: RunContext, h2: Component | None, *, roots: Sequence[str] = K.ROOTS,
             use_locks: bool = True) -> EvalOutput:
    notes: dict[str, Any] = {}
    load_counts: Counter = Counter()
    sm = divisor_table(ctx, roots)
    rds: dict[str, RootData] = {}
    for root in roots:
        bars = load_or_exclude(ctx, root, load_counts, notes)
        if bars is None:
            continue
        locks = lock_rule(ctx, bars) if use_locks else None
        rds[root] = process_root(ctx, bars, root, locks=locks, with_tom=root in K.T3_ROOTS)
        del bars, locks
        gc.collect()
    notes["S_M"] = {f"{m[0]}-{m[1]:02d}": v for m, v in sm.items()}
    notes["window_starts"] = {r: str(ctx.starts[r]) for r in roots}
    notes["root_counters"] = {r: dict(sorted(rd.counters.items())) for r, rd in rds.items()}
    tests: dict[str, TestOutput] = {}
    for test in ("T1", "T2"):
        c: Counter = Counter(load_counts)
        c.update(_return_counts(rds, roots))
        books = {r: simulate_book(rd, t12_orders(rd, test, sm, c)) for r, rd in rds.items()}
        dates = series_dates([rd.mark_days for rd in rds.values()], _first_fill(books))
        series, per_root = assemble(books, dates, c)
        out = TestOutput(test, series, c)
        _book_summary(out, books, dates, per_root)
        tests[test] = out
    c3: Counter = Counter({k: v for k, v in load_counts.items()})
    t3 = [r for r in K.T3_ROOTS if r in rds]
    c3.update(_return_counts(rds, t3))
    su = divisor_su({r: rds[r].tom for r in t3})
    books3 = {r: simulate_book(rds[r], t3_orders(rds[r], su, c3)) for r in t3}
    entries = [date.fromisoformat(f["date"]) for b in books3.values() for f in b.fills
               if "entry" in f["kind"]]
    dates3 = series_dates([rds[r].mark_days for r in t3], min(entries) if entries else None)
    series3, per_root3 = assemble(books3, dates3, c3)
    out3 = TestOutput("T3", series3, c3)
    _book_summary(out3, books3, dates3, per_root3)
    out3.notes["S_u"] = {f"{m[0]}-{m[1]:02d}": v for m, v in sorted(su.items())}
    tests["T3"] = out3
    comps = {"T2": component_from_series("T2", tests["T2"].series),
             "T3": component_from_series("T3", tests["T3"].series)}
    if h2 is not None:
        comps["H2"] = h2
    series4, c4, used = combine(comps)
    out4 = TestOutput("T4", series4, c4)
    out4.notes["components"] = list(comps)
    out4.notes["component_usage_base"] = {k: dict(v) for k, v in used.items()}
    tests["T4"] = out4
    roots_out = {r: _root_rows(rd, tests) for r, rd in rds.items()}
    return EvalOutput(tests, roots_out, notes)


def _root_rows(rd: RootData, tests: Mapping[str, TestOutput]) -> dict:
    """Spec 10: rebalances and entries/exits (date, n per unit capital, price ticks, V), the
    per-contract daily dollar P&L of one vehicle contract held (roll-adjusted; None on a failed
    interval), and every fill with its per-contract costs per case."""
    pc = rd.path.per_contract_daily()
    return {"schema": K.PER_ROOT_SCHEMA, "root": rd.root, "vehicle": rd.vehicle,
            "tick_value_cents": str(rd.tick_value_cents),
            "per_contract_daily_dollars": {str(d): (None if v is None else float(v) / 100.0)
                                           for d, v in sorted(pc.items())},
            "holdings": {t: tests[t].holdings.get(rd.root, []) for t in ("T1", "T2", "T3")},
            "fills": {t: tests[t].fills.get(rd.root, []) for t in ("T1", "T2", "T3")},
            "counters": dict(sorted(rd.counters.items()))}


__all__ = ["EvalOutput", "TestOutput", "evaluate"]
