"""Stage E.4 Task 4: write the K4 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e4_member_specs.md S0.2 (K4-L-11): 12 trials, label "<member id> <ROOT>",
ordinals in catalog order then MCL (crude) before NG (gas); one leg each, the traded vehicle.
Usage: PYTHONPYCACHEPREFIX=<fresh dir> PYTHONPATH=. uv run python reports/stage_e4_briefs/write_k4_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

MEMBERS = (  # (member id, module, roots) in catalog order (reports/stage_e0_catalog_K4.md section 1)
    ("K4-cp1-01", "strategy.members.k4.cp1", ("MCL", "NG")),
    ("K4-cp2-01", "strategy.members.k4.cp2", ("MCL", "NG")),
    ("K4-cp3-01", "strategy.members.k4.cp3", ("MCL", "NG")),
    ("K4-ngpre-01", "strategy.members.k4.ngpre", ("NG",)),
    ("K4-apipre-01", "strategy.members.k4.apipre", ("MCL",)),
    ("K4-eiafade-01", "strategy.members.k4.eiafade", ("MCL",)),
    ("K4-eiamom-01", "strategy.members.k4.eiamom", ("MCL",)),
    ("K4-ovr-01", "strategy.members.k4.ovr", ("MCL", "NG")),
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
    assert len(decls) == 12, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory)
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K4", decls))
