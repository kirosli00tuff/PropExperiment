"""Stage E.3 Task 4: write the K2 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e3_member_specs.md S0.2 (L-18): 44 trials, label "<member id> <ROOT>",
ordinals in catalog order then ZT, ZF, ZN, TN, ZB, UB; one leg each, the traded vehicle.
Usage: PYTHONPYCACHEPREFIX=<fresh dir> uv run python reports/stage_e3_briefs/write_k2_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

ROOTS = ("ZT", "ZF", "ZN", "TN", "ZB", "UB")
MEMBERS = (  # (member id, module, roots) in catalog order (reports/stage_e0_catalog_K2.md section 1)
    ("K2-cp1-01", "strategy.members.k2.cp1", ROOTS),
    ("K2-cp2-01", "strategy.members.k2.cp2", ROOTS),
    ("K2-cp3-01", "strategy.members.k2.cp3", ROOTS),
    ("K2-aucpre-01", "strategy.members.k2.aucpre", ROOTS),
    ("K2-aucpost-01", "strategy.members.k2.aucpost", ROOTS),
    ("K2-fomcpost-01", "strategy.members.k2.fomcpost", ROOTS),
    ("K2-predrift-01", "strategy.members.k2.predrift", ("ZN", "ZB")),
    ("K2-monthend-01", "strategy.members.k2.monthend", ROOTS),
)


def declarations() -> list[MemberDecl]:
    out: list[MemberDecl] = []
    for member_id, module, roots in MEMBERS:
        for root in roots:
            out.append(MemberDecl(f"{member_id} {root}", len(out) + 1, module,
                                  f"make_{root.lower()}", (LegSpec(root, True),)))
    return out


if __name__ == "__main__":
    decls = declarations()
    assert len(decls) == 44, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory)
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K2", decls))
