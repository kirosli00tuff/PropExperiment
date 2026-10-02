"""Stage E.9 Task 4: write the K8 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e9_member_specs.md S0.2 (K8-L-01): 4 trials, label "<member id> [grid]
<traded root>", ordinals in catalog order (reports/stage_e0_catalog_K8.md section 5). Every declaration
trades one leg, declared first (the primary leg), then reads one signal leg (S0.1; V16(b), (c)).
Usage: PYTHONPYCACHEPREFIX=<fresh dir> PYTHONPATH=. uv run python reports/stage_e9_briefs/write_k8_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

DECLS = (  # (label, module, factory, traded root, signal root) in catalog order
    ("K8-flight-01 H30 MGC", "strategy.members.k8.flight", "make_h30", "MGC", "MES"),
    ("K8-flight-01 HEOD MGC", "strategy.members.k8.flight", "make_heod", "MGC", "MES"),
    ("K8-oilcad-01 6C", "strategy.members.k8.oilcad", "make_6c", "6C", "MCL"),
    ("K8-wkndbtc-01 MNQ", "strategy.members.k8.wkndbtc", "make_mnq", "MNQ", "MBT"),
)


def declarations() -> list[MemberDecl]:
    return [MemberDecl(label, i + 1, module, factory, (LegSpec(traded, True), LegSpec(signal, False)))
            for i, (label, module, factory, traded, signal) in enumerate(DECLS)]


if __name__ == "__main__":
    decls = declarations()
    assert len(decls) == 4, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory, [(leg.root, leg.traded) for leg in d.legs])
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K8", decls))
