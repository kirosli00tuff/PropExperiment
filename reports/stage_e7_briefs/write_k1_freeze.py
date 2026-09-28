"""Stage E.7 Task 4: write the K1 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e7_member_specs.md S0.2 (K1-L-12): 11 trials, label "<member id> <root>",
ordinals in catalog order then MNQ, M2K, MYM; one leg each, the traded vehicle.
Usage: PYTHONPYCACHEPREFIX=<fresh dir> PYTHONPATH=. uv run python reports/stage_e7_briefs/write_k1_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

ROOTS = ("MNQ", "M2K", "MYM")
MEMBERS = (  # (member id, module, roots) in catalog order (reports/stage_e0_catalog_K1.md section 1)
    ("K1-cp1-01", "strategy.members.k1.cp1", ROOTS),
    ("K1-cp2-01", "strategy.members.k1.cp2", ROOTS),
    ("K1-cp3-01", "strategy.members.k1.cp3", ROOTS),
    ("K1-vxnband-01", "strategy.members.k1.vxnband", ("MNQ",)),
    ("K1-vwap-01", "strategy.members.k1.vwap", ("MNQ",)),
)


def declarations() -> list[MemberDecl]:
    rows = [(member_id, module, root) for member_id, module, roots in MEMBERS for root in roots]
    return [MemberDecl(f"{member_id} {root}", i + 1, module, f"make_{root.lower()}", (LegSpec(root, True),))
            for i, (member_id, module, root) in enumerate(rows)]


if __name__ == "__main__":
    decls = declarations()
    assert len(decls) == 11, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory)
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K1", decls))
