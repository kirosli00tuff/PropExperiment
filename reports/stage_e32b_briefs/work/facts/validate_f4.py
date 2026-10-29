"""Validate briefs/F4_facts_unmasked.json with the consumers' own readers (imported, never run as computations):
score32b.validate (with stub econ blocks so only the F4 checks bite), econ32b_inputs.jobs_from_facts + firm_check,
and F5's reader functions. Run from the repo root with PYTHONPATH=. (E.28's model package is imported for the
firm limits). Prints a summary; exit 1 on any failure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
B = REPO / "reports" / "stage_e32b_briefs"
W = B / "work"


def load(p: Path) -> dict:
    return json.loads(p.read_text())


def main() -> int:
    f4p = Path(sys.argv[1]) if len(sys.argv) > 1 else B / "F4_facts_unmasked.json"
    f3, f4 = load(B / "F3_vol.json"), load(f4p)
    fails = []

    # 1. score: validate (fatal contract checks) and soft cross-checks
    sys.path.insert(0, str(W / "score"))
    import score32b as S  # noqa: E402
    stub = {"pairs": {}}
    for key, pf in f4["pairs"].items():
        code = key.split("|")[1]
        if code != "NQ" and pf.get("listed_50k") is True and (f3["roots"].get(code) or {}).get("status") in (
                "owned", "OC1"):
            stub["pairs"][key] = {b: {} for b in S.ECON_BLOCKS}
    docs = {"F3": f3, "F4": f4, "econ": stub, "attention": load(B / "F2_attention.json"),
            "data_access": load(B / "F2_data_access.json")}
    try:
        soft = S.validate(docs)
        print(f"score validate: OK; {len(soft)} soft findings")
        for s in soft:
            print("   soft:", s)
    except Exception as e:  # noqa: BLE001
        fails.append(f"score validate: {type(e).__name__}: {e}")
    from s32b_layer2 import p_score  # noqa: E402
    for f, ff in f4["firms"].items():
        try:
            p, d, u = p_score(ff.get("p_inputs"))
            print(f"   P {f}: {p} {d}")
        except Exception as e:  # noqa: BLE001
            fails.append(f"p_score {f}: {e}")

    # 2. econ: job builder and firm-limit check
    sys.path.insert(0, str(W / "econ"))
    import econ32b_inputs as I  # noqa: E402
    import econ32b_model as M  # noqa: E402
    try:
        limits = M.model_limits()
        jobs, meta, skipped = I.jobs_from_facts(f3, f4, set(limits))
        fc = I.firm_check(f4, limits)
        print(f"econ jobs_from_facts: {len(meta)} pairs, {len(jobs)} jobs, {len(skipped)} not computed")
        reasons = {}
        for k, why in skipped.items():
            reasons[why] = reasons.get(why, 0) + 1
        print("   not computed:", reasons)
        print("   firm_check mismatches:", fc["mismatches"] or "none")
        for f, row in fc["rows"].items():
            print(f"   {f}: " + "; ".join(f"{k} {v['status']}" for k, v in row.items() if isinstance(v, dict)))
        if fc["mismatches"]:
            fails.append(f"econ firm_check mismatches {fc['mismatches']}")
    except Exception as e:  # noqa: BLE001
        fails.append(f"econ: {type(e).__name__}: {e}")

    # 3. F5 readers on every code and every listed pair's firm
    sys.path.insert(0, str(W / "F5"))
    import f5_core as C  # noqa: E402
    import f5_holding as H  # noqa: E402
    n = 0
    for code, fc4 in f4["codes"].items():
        root = f3["roots"].get(code) or {}
        try:
            if root.get("status") in ("owned", "OC1"):
                H.check_tick(code, root, fc4)
                H.spread(fc4)
                ms, me = H.main_session(root)
                H.pause_relations(fc4.get("pauses"), ms, me)
                n += 1
        except Exception as e:  # noqa: BLE001
            fails.append(f"F5 code {code}: {e}")
    for f, ff in f4["firms"].items():
        try:
            fl = C.parse_flat_by_close(ff.get("flat_by_close"))
            print(f"   F5 {f}: flat {fl.status} {C.min_to_hhmm(fl.pt_min)} PT; limits {H.firm_limits(f, ff)[:3]}; "
                  f"overnight {H.overnight_allowed(ff)}")
        except Exception as e:  # noqa: BLE001
            fails.append(f"F5 firm {f}: {e}")
    for key, pf in f4["pairs"].items():
        if pf.get("listed_50k") is True:
            try:
                H.number(pf.get("fee_rt_usd"), f"{key} fee")
            except Exception as e:  # noqa: BLE001
                fails.append(f"F5 pair {key}: {e}")
    print(f"F5 readers: {n} codes checked")
    if fails:
        print("FAILURES:")
        for x in fails:
            print("  ", x)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
