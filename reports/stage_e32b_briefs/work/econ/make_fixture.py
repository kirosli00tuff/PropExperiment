"""Synthetic F3/F4-shaped fixture for the timing run (NOT facts): built from E.28's A3_inputs.json (copied here).

sigma_h = sigma_1m * sqrt(h) (a diffusive placeholder; real 60-minute sigmas are usually below this, so the grid caps
here are, if anything, larger than the real ones and the timing is conservative), L_main = 390 minutes for every
code, S unsourced (1 tick) except GC (1.5 ticks "sourced", to exercise the non-shared spread1 lattice), fees, tick
values and firm limits from E.28's inputs and models. Writes fixture/F3_fixture.json, fixture/F4_fixture.json and
fixture/edir_fixture.json. Usage: PYTHONPATH=. uv run python reports/stage_e32b_briefs/work/econ/make_fixture.py
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK))

from econ32b import SPEC_SHA256  # noqa: E402

H = (1, 2, 5, 15, 30, 60, 120, 240)
L_MAIN = 390
FIXTURE_S = {"GC": 1.5}
EDIR = ["topstep|MNQ"]
NOTE = "SYNTHETIC fixture from E.28 A3_inputs.json (sigma_h = sigma_1m sqrt(h)); not an E.32b fact"


def main() -> int:
    import econ32b_model as M

    inp = json.loads((WORK / "A3_inputs.json").read_text())
    roots, codes = {}, {}
    for code, c in inp["candidates"].items():
        s1 = c["sigma_1m_ticks"]
        roots[code] = {"status": "unknown" if s1 is None else "owned", "tick_size": c["tick_size"], "L_main": L_MAIN,
                       "h": {str(h): {"sigma": None if s1 is None else s1 * math.sqrt(h)} for h in H}}
        s = FIXTURE_S.get(code)
        codes[code] = {"tick_size": c["tick_size"], "tick_value_usd": c["v_usd"], "excluded": False,
                       "spread_S": {"value": s, "sourced": s is not None, "item": "fixture" if s else None}}
    pairs = {f"{p['firm']}|{p['code']}": {"listed_50k": True, "fee_rt_usd": p["F_rt_usd"], "fee_kind": "stated"}
             for p in inp["pairs"]}
    firms = {f: {"mll_50k": v["mll_usd"], "dll_50k": v["dll_usd"]} for f, v in M.model_limits().items()}
    out = WORK / "fixture"
    out.mkdir(exist_ok=True)
    (out / "F3_fixture.json").write_text(json.dumps({"spec_sha256": SPEC_SHA256, "note": NOTE, "roots": roots}))
    (out / "F4_fixture.json").write_text(json.dumps({"spec_sha256": SPEC_SHA256, "note": NOTE, "codes": codes,
                                                     "pairs": pairs, "firms": firms}))
    (out / "edir_fixture.json").write_text(json.dumps(EDIR))
    print(f"wrote {out}: {len(roots)} roots, {len(pairs)} pairs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
