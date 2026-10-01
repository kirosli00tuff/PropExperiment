"""Stage E.8 Task 4: write the K6 cluster freeze (lead script; run once, after the audit rulings).

Declarations from reports/stage_e8_member_specs.md S0.2 (K6-L-14): 27 trials, label "<member id> <root>",
ordinals in catalog order then ZC, ZW, ZS, ZM, ZL, HE, LE. Every declaration trades one leg; K6-crushgap-01
also reads ZM and ZL as signal legs, after the traded ZS (S0.1; the first traded leg is the primary leg).
Usage: PYTHONPYCACHEPREFIX=<fresh dir> PYTHONPATH=. uv run python reports/stage_e8_briefs/write_k6_freeze.py [--dry-run]
"""

from __future__ import annotations

import sys

from screening.stage_e_freeze import MemberDecl, write_cluster_freeze
from strategy.stage_e.interface import LegSpec

ALL = ("ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE")
MEMBERS = (  # (member id, module, roots) in catalog order (reports/stage_e0_catalog_K6.md section 1)
    ("K6-cp1-01", "strategy.members.k6.cp1", ALL),
    ("K6-cp2-01", "strategy.members.k6.cp2", ALL),
    ("K6-cp3-01", "strategy.members.k6.cp3", ALL),
    ("K6-crushgap-01", "strategy.members.k6.crushgap", ("ZS",)),
    ("K6-limitcont-01", "strategy.members.k6.limitcont", ("HE", "LE")),
    ("K6-wasdepre-01", "strategy.members.k6.wasdepre", ("ZC", "ZS")),
    ("K6-wasdepost-01", "strategy.members.k6.wasdepost", ("ZC",)),
)
SIGNAL_LEGS = {"K6-crushgap-01": ("ZM", "ZL")}


def legs(member_id: str, root: str) -> tuple[LegSpec, ...]:
    return (LegSpec(root, True),) + tuple(LegSpec(r, False) for r in SIGNAL_LEGS.get(member_id, ()))


def declarations() -> list[MemberDecl]:
    rows = [(member_id, module, root) for member_id, module, roots in MEMBERS for root in roots]
    return [MemberDecl(f"{member_id} {root}", i + 1, module, f"make_{root.lower()}", legs(member_id, root))
            for i, (member_id, module, root) in enumerate(rows)]


if __name__ == "__main__":
    decls = declarations()
    assert len(decls) == 27, len(decls)
    for d in decls:
        print(d.ordinal, d.label, d.module, d.factory, [(leg.root, leg.traded) for leg in d.legs])
    if "--dry-run" in sys.argv:
        sys.exit(0)
    print("cluster freeze sha256:", write_cluster_freeze("K6", decls))
