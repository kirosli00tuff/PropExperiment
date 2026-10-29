"""Lead rulings after the RecsDrafter's L1-L3 (session 3, 2026-10-29), applied to the merged combinations file.
LR-Q3a: F01 on YM, MYM and RTY re-tests closed configurations (E16-H1, R1-13: the rest-of-day rule at h 30 on YM,
        2019-05..2024-02, failed, V31; K1-cp1-01, R1-03: 14:30-14:59 CT on MYM and M2K) -> Q3 = 0 (gate).
LR-V31: YM is a V31 fallback root ("no rerun or variant on these windows, no purchase of the 10 fallback roots"): no
        buyable clean test window for the Dow (YM, MYM) -> clean_test_window_months = 0 for every combination with a
        YM or MYM member.
LR-ZLW: ZL keeps its sealed window (V56 item 1: "stays sealed for a future hypothesis family"): no change.
Modes: primary (LR-Q3a, LR-Q3b, LR-V31), q3only (LR-Q3a and LR-Q3b without LR-V31: the narrow V31 reading), nozlw
(primary + ZL window unavailable), ts150 (primary on the Topstep-$150 file).
q3bleg (session 4, 2026-10-29): the primary without LR-Q3b, i.e. the leg-level F09 reading (Q3 2 as rated)."""
import json
import sys
from pathlib import Path

B = Path(__file__).resolve().parents[2]
mode = sys.argv[1] if len(sys.argv) > 1 else "primary"
src = B / ("work/R2/R2_combinations_topstep150.json" if mode == "ts150" else "work/R2/R2_combinations_v1.json")
out = {"primary": B / "R2_combinations.json", "q3only": B / "work/R2/R2_combinations_q3only.json",
       "nozlw": B / "work/R2/R2_combinations_nozlw.json", "ts150": B / "work/R2/R2_combinations_ts150_v2.json",
       "q3bleg": B / "work/R2/R2_combinations_q3bleg.json"}[mode]
d = json.loads(src.read_text())
n_q3 = n_v31 = n_zl = n_q3b = 0
for c in d["combinations"]:
    codes = {m["code"] for m in c["members"]}
    fam = c["family"]
    if fam.startswith("F01") and codes & {"YM", "MYM", "RTY"} and c["Q3"]["value"] != 0:
        c["Q3_rater"] = c["Q3"]
        c["Q3"] = {"value": 0, "unknown": False,
                   "reason": "LR-Q3a: re-tests E16-H1 (R1-13, rest-of-day rule at h 30 on YM, 2019-05..2024-02) and "
                             "K1-cp1-01 (R1-03, 14:30-14:59 CT on MYM and M2K); the rater's flag 1 conditional"}
        n_q3 += 1
    if mode != "q3bleg" and fam.startswith("F09") and codes & {"RTY", "ZL"} and c["Q3"]["value"] == 2:
        c.setdefault("Q3_rater", c["Q3"])
        c["Q3"] = {"value": 1, "unknown": False,
                   "reason": "LR-Q3b: R1-11 and R1-15 searched G17 cross-market lead features (60-minute lead-path returns of "
                             "NQ, ZN, 6E, CL, GC, ZC; never the own cluster) on M2K/RTY and ZL at h60-hF: same family "
                             "and product at a neighbouring horizon (RV2 B1)"}
        n_q3b += 1
    if mode in ("primary", "nozlw", "ts150", "q3bleg") and codes & {"YM", "MYM"}:
        c["data"]["clean_test_window_months_before_V31"] = c["data"].get("clean_test_window_months")
        c["data"]["clean_test_window_months"] = 0
        n_v31 += 1
    if mode == "nozlw" and "ZL" in codes:
        c["data"]["clean_test_window_months_before_nozlw"] = c["data"].get("clean_test_window_months")
        c["data"]["clean_test_window_months"] = 0
        n_zl += 1
d["lead_patch_v2"] = {"rulings": ["LR-Q3a"] + (["LR-Q3b"] if mode != "q3bleg" else []) + (["LR-V31"] if mode != "q3only" else []) + (["no ZL window"] if mode == "nozlw" else []),
                      "script": "work/R2/patch_v31_q3_lead.py", "mode": mode, "q3_gated": n_q3, "q3b_to_1": n_q3b, "v31_q7": n_v31, "zl_q7": n_zl}
out.write_text(json.dumps(d, indent=1, ensure_ascii=False))
print(mode, "-> ", out.name, "| Q3 gated", n_q3, "| Q3b", n_q3b, "| V31 Q7", n_v31, "| ZL Q7", n_zl)
