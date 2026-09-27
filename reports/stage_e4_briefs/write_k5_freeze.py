"""Stage E.4 Part 2 Task 4: write the K5 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e4b_member_specs.md S0.2 (K5-L-11): 11 trials, label "<member id> <ROOT>",
ordinals in catalog order then MGC (gold) before MHG (copper); one leg each, the traded vehicle.
Usage: PYTHONPYCACHEPREFIX=<fresh dir> PYTHONPATH=. uv run python reports/stage_e4_briefs/write_k5_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

MEMBERS = (  # (member id, module, roots) in catalog order (reports/stage_e0_catalog_K5.md section 1)
    ("K5-cp1-01", "strategy.members.k5.cp1", ("MGC", "MHG")),
    ("K5-cp2-01", "strategy.members.k5.cp2", ("MGC", "MHG")),
    ("K5-cp3-01", "strategy.members.k5.cp3", ("MGC", "MHG")),
    ("K5-preauc-01", "strategy.members.k5.preauc", ("MGC",)),
    ("K5-pmfix-01", "strategy.members.k5.pmfix", ("MGC",)),
    ("K5-fomc-01", "strategy.members.k5.fomc", ("MGC",)),
    ("K5-ovr-01", "strategy.members.k5.ovr", ("MGC", "MHG")),
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
    assert len(decls) == 11, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory)
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K5", decls))
