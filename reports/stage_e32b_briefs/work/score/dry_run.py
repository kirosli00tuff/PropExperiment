"""dry_run.py: build the SYNTHETIC fixture (make_fixture.py) and run score32b and r3_score on it.

Writes fixture/*.json (inputs), fixture_out.json ({"score32b": ..., "r3_score": ...}) and fixture_out.md.
Run: uv run python reports/stage_e32b_briefs/work/score/dry_run.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import make_fixture  # noqa: E402
import r3_score as R  # noqa: E402
import score32b as S  # noqa: E402
from s32b_common import E28_TABLE, file_sha256, load_json, write_json  # noqa: E402


def main() -> int:
    paths = make_fixture.write_all(os.path.join(HERE, "fixture"))
    docs = {name: load_json(paths[name]) for name in make_fixture.FILES}
    meta = {name: {"path": os.path.relpath(p, HERE), "sha256": file_sha256(p)} for name, p in paths.items()}
    s_out = S.run_all(docs, load_json(paths["rulings"]), load_json(E28_TABLE), allow_partial=True, input_meta=meta)
    r_out = R.run_r3(load_json(paths["combos"]), input_meta={"combos": meta["combos"]})
    write_json(os.path.join(HERE, "fixture_out.json"),
               {"note": "SYNTHETIC fixture dry run (make_fixture.py); no real fact was read or scored",
                "score32b": s_out, "r3_score": r_out})
    S.write_md(s_out, os.path.join(HERE, "fixture_out.md"))
    p = s_out["primary"]
    print(f"score32b: survivors {p['layer1_survivors']}; ranked {p['n_ranked']}; ties {len(p['ties'])}; "
          f"variants {len(s_out['variants'])}; lead notes {len(s_out['for_lead'])}")
    print(f"r3_score: R4 {[(c['product_or_pool'], c['family'], c['best_venue']) for c in r_out['R4']['candidates']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
