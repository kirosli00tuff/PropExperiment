"""Which frozen Stage E member a trigger id runs, and how its table is given (brief items 3, 5).

A trigger id is the member's freeze label (reports/stage_e_k*_member_freeze.json, e.g.
"K2-monthend-01 ZN"; an underscore stands for the space); the member is resolved and its code
verified through the harness's own screening.stage_e_freeze (load_cluster_freeze,
verify_cluster_code, resolve_member) and built by the frozen factory, unchanged.

Table members on W_ext (the frozen tables start on 2019-05-01). The member's own code reads its
table; only the table's 2010-2019 rows are supplied, three ways:
- "context": the W_ext context (trigger_hold.events_context: pattern_search.backward's swap)
  binds the module-level name the member reads at run time (K2-monthend-01:
  strategy.members.k2.monthend.EVENT_DATES, swap S6); checked here against
  trigger_hold.events_tables' own derivation of the same rule on the window;
- "module": the factory runs while the module-level name read at construction is bound to the
  table (K2 fomcpost: fomcpost.FOMC_STATEMENT_DATES; K2 aucpre/aucpost:
  _event_common.TREASURY_AUCTIONS), restored at once;
- "kwarg": the member's class takes the table as a field (K5 Fomc.statement_dates).
On W_cf no table is replaced: the member is the frozen factory's, as the harness builds it. A
W_ext run of a member whose module reads a 2019-on table without a declared way is refused.
"""

from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from typing import Any

from screening.stage_e_freeze import load_cluster_freeze, resolve_member, verify_cluster_code
from trigger_hold.events_tables import Table

TABLE_MARKERS = ("_releases", "auction_schedule", "_calendar", "_month_end")


class MemberRefused(RuntimeError):
    """The trigger id names no frozen member, or its table cannot be given (refused)."""


@dataclass(frozen=True)
class Injection:
    kind: str  # "context" | "module" | "kwarg"
    table: str  # a trigger_hold.events_tables.TABLE_BUILDERS kind
    target: str  # module path ("context", "module") or field name ("kwarg")
    attr: str | None = None  # the module-level name ("context", "module")


@dataclass(frozen=True)
class TriggerSpec:
    trigger_id: str
    cluster: str
    label: str
    injection: Injection | None = None


INJECTIONS: Mapping[str, Injection] = {
    "K2-monthend-01": Injection("context", "month_end_dates", "strategy.members.k2.monthend",
                                "EVENT_DATES"),
    "K2-fomcpost-01": Injection("module", "fomc_statement_dates",
                                "strategy.members.k2.fomcpost", "FOMC_STATEMENT_DATES"),
    "K2-aucpost-01": Injection("module", "treasury_auctions",
                               "strategy.members.k2._event_common", "TREASURY_AUCTIONS"),
    "K2-aucpre-01": Injection("module", "treasury_auctions",
                              "strategy.members.k2._event_common", "TREASURY_AUCTIONS"),
    "K5-fomc-01": Injection("kwarg", "fomc_statement_dates", "statement_dates"),
}


def spec_for(trigger_id: str) -> TriggerSpec:
    label = trigger_id.replace("_", " ").strip()
    member_id = label.split(" ", 1)[0]
    cluster = member_id.split("-", 1)[0]
    if not (len(cluster) == 2 and cluster[0] == "K" and cluster[1] in "12345678"):
        raise MemberRefused(f"{trigger_id!r}: not a Stage E member label (K1..K8)")
    return TriggerSpec(label, cluster, label, INJECTIONS.get(member_id))


@contextmanager
def bound(module: Any, attr: str, value: Any) -> Iterator[None]:
    if not hasattr(module, attr):
        raise MemberRefused(f"{module.__name__} has no {attr}")
    old = getattr(module, attr)
    setattr(module, attr, value)
    try:
        yield
    finally:
        setattr(module, attr, old)


def decision_schedule(member: Any) -> Mapping[date, int] | None:
    """Trade date -> the CT clock minute of the entry decision bar, for a table member:
    FixedSideEvent.schedule (entry, exit), SignedMoveEvent.plans (start, entry, exit), or
    K2 MonthEndSlice (module EVENT_DATES at the leg's O); None for any other member."""
    core = getattr(member, "_core", None)
    for name in ("schedule", "plans"):
        table = getattr(core, name, None)
        if isinstance(table, Mapping):
            return {d: (p[1] if len(p) == 3 else p[0]) for d, p in table.items()}
    if type(member).__name__ == "MonthEndSlice":
        module = importlib.import_module(type(member).__module__)
        o = member._leg.o
        return {d: o.hour * 60 + o.minute for d in module.EVENT_DATES}
    return None


def _expected_dates(table: Table, root: str) -> frozenset[date]:
    if table.kind in ("fomc_statement_dates", "month_end_dates"):
        return frozenset(date.fromisoformat(d) for d in table.rows)
    from strategy.members.k2._event_common import AUCTION_TENOR

    tenor = AUCTION_TENOR[root]
    return frozenset(date.fromisoformat(d) for d, t, _ in table.rows if t == tenor)


@dataclass(frozen=True)
class BuiltMember:
    member: Any
    decl: Any  # screening.stage_e_freeze.MemberDecl
    freeze_sha256: str
    table: Table | None


def resolve(spec: TriggerSpec) -> tuple[Any, Callable[[], Any], str]:
    freeze = load_cluster_freeze(spec.cluster)
    verify_cluster_code(freeze)
    decl, factory = resolve_member(freeze, spec.label, None)
    return decl, factory, freeze.sha256


def build_member(spec: TriggerSpec, table: Table | None, first: date | None = None,
                 last: date | None = None) -> BuiltMember:
    """The frozen member; with ``table`` (W_ext) given its declared way and checked."""
    decl, factory, sha = resolve(spec)
    if table is None:
        return BuiltMember(factory(), decl, sha, None)
    inj = spec.injection
    if inj is None or inj.table != table.kind:
        raise MemberRefused(f"{spec.trigger_id}: no declared way to give it a {table.kind} table")
    member = _inject(factory, inj, table)
    root = next(leg.root for leg in decl.legs if leg.traded)
    sched = decision_schedule(member)
    got = None if sched is None else frozenset(
        d for d in sched if (first is None or d >= first) and (last is None or d <= last))
    want = frozenset(d for d in _expected_dates(table, root)
                     if (first is None or d >= first) and (last is None or d <= last))
    if got != want:
        n = 0 if got is None else len(got)
        raise MemberRefused(f"{spec.trigger_id}: the built member's schedule ({n} dates in the "
                            f"window) is not the table's ({len(want)} dates)")
    return BuiltMember(member, decl, sha, table)


def _inject(factory: Callable[[], Any], inj: Injection, table: Table) -> Any:
    if inj.kind == "context":  # the W_ext context already binds the name; build as frozen
        return factory()
    if inj.kind == "module":
        assert inj.attr is not None
        with bound(importlib.import_module(inj.target), inj.attr, tuple(table.rows)):
            return factory()
    if inj.kind == "kwarg":
        frozen = factory()
        cls = type(frozen)
        if inj.target not in inspect.signature(cls).parameters:
            raise MemberRefused(f"{cls.__name__} takes no {inj.target!r}")
        return cls(frozen.root, **{inj.target: tuple(table.rows)})
    raise MemberRefused(f"unknown injection kind {inj.kind!r}")


def check_table_need(spec: TriggerSpec) -> None:
    """Refuse a W_ext run of a member that reads a 2019-on table without a declared way."""
    decl, _, _ = resolve(spec)
    source = inspect.getsource(importlib.import_module(decl.module))
    if spec.injection is None and any(m in source for m in TABLE_MARKERS):
        raise MemberRefused(f"{spec.trigger_id}: {decl.module} reads a 2019-on table "
                            f"({'/'.join(TABLE_MARKERS)}); declare its 2010-2019 table first")


__all__ = ["INJECTIONS", "BuiltMember", "Injection", "MemberRefused", "TriggerSpec", "bound",
           "build_member", "check_table_need", "decision_schedule", "resolve", "spec_for"]
