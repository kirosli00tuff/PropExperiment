"""Stage E.6 Task 4: write the K7 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e6_member_specs.md S0.2 (K7-L-10): 6 trials, label "<member id> MBT",
ordinals in catalog order; one leg each, the traded vehicle MBT.
Usage: PYTHONPYCACHEPREFIX=<fresh dir> PYTHONPATH=. uv run python reports/stage_e6_briefs/write_k7_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

MEMBERS = (  # (member id, module) in catalog order (reports/stage_e0_catalog_K7.md section 1)
    ("K7-cp1-01", "strategy.members.k7.cp1"),
    ("K7-cp2-01", "strategy.members.k7.cp2"),
    ("K7-cp3-01", "strategy.members.k7.cp3"),
    ("K7-expiry-01", "strategy.members.k7.expiry"),
    ("K7-rev2h-01", "strategy.members.k7.rev2h"),
    ("K7-montrend-01", "strategy.members.k7.montrend"),
)


def declarations() -> list[MemberDecl]:
    return [MemberDecl(f"{member_id} MBT", i + 1, module, "make_mbt", (LegSpec("MBT", True),))
            for i, (member_id, module) in enumerate(MEMBERS)]


if __name__ == "__main__":
    decls = declarations()
    assert len(decls) == 6, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory)
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K7", decls))
