"""Stage E.4 Part 3 Task 4: write the K3 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e4c_member_specs.md S0.2: 30 trials (K3-mehedge-01 on 6J only: no free EURO STOXX 50 history), label "<member id> <ROOT>",
ordinals in catalog order then EUR, AUD, GBP, CAD, JPY, CHF, NZD; one leg each, the traded vehicle.
Usage: PYTHONPYCACHEPREFIX=<fresh dir> PYTHONPATH=. uv run python reports/stage_e4_briefs/write_k3_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

ROOTS = ("6E", "6A", "6B", "6C", "6J", "6S", "6N")
MEMBERS = (  # (member id, module, roots) in catalog order (reports/stage_e0_catalog_K3.md section 1)
    ("K3-cp1-01", "strategy.members.k3.cp1", ROOTS),
    ("K3-cp2-01", "strategy.members.k3.cp2", ROOTS),
    ("K3-cp3-01", "strategy.members.k3.cp3", ROOTS),
    ("K3-ldnrev-01", "strategy.members.k3.ldnrev", ("6E", "6J", "6S")),
    ("K3-ldnmom-01", "strategy.members.k3.ldnmom", ("6E", "6J")),
    ("K3-mehedge-01", "strategy.members.k3.mehedge", ("6J",)),
    ("K3-ecbfix-01", "strategy.members.k3.ecbfix", ("6E",)),
    ("K3-tkypre-01", "strategy.members.k3.tkypre", ("6J",)),
    ("K3-tkypost-01", "strategy.members.k3.tkypost", ("6J",)),
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
    assert len(decls) == 30, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory)
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K3", decls))
