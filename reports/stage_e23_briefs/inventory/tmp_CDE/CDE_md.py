import json
from pathlib import Path
O = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e23_briefs/inventory")
d = json.loads((O / "CDE.json").read_text())
def c(x):
    if isinstance(x, dict): x = "; ".join(f"{k}: {v}" for k, v in x.items())
    if isinstance(x, list): x = ", ".join(map(str, x))
    return str(x).replace("|", "/").replace("\n", " ")
L = ["# Stage E.23 P1.1 inventory: CDE (Stage C, Stage D D.1..D.1f, E.13 to E.18)", "",
     "Written by InventoryReaderCDE-OpusHigh, 2026-10-17. Extraction only: no judgment of mechanisms, no ranking. "
     "Full fields (verbatim definitions, side and exit rules, inputs, stages_read) are in CDE.json; this table is the compact view.", "",
     f"Rows: {len(d['rows'])} (58 D.1f Tier A members on MES: 31 trials, 21 event statistics, 6 Family H; plus E16-H1 and E16-H4 pooled over 27 price paths). Excluded: {len(d['excluded'])}.", "",
     "Data facts common to all 58 MES rows: MES has no W_ext data (not one of the 17 roots, no full-size equivalent owned). "
     "W_cf for MES (2020-02-03..2024-02-29) was read once by every one of the 58 in the D.1f confirmation run. Rows from D.1/D.1b/D.1d were screened on the research window 2025-04-01..2026-05-13 (barred for this stage). "
     "Family H (H1-H6) was never read before D.1f. E16-H1 and E16-H4 were read once, in E.17, on 2010-07..2024-02 for the 17 W_ext roots (both W_ext and W_cf) and on 2019-05-06..2024-02-29 for 10 fallback roots.", "",
     "| # | trigger_id | stage | root(s) | trigger event | decision time (CT) | side kind | hold | stages read (stage: purpose, window) | verdict |",
     "|---|---|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(d["rows"], 1):
    st = "; ".join(f"{s['stage']}: {s['purpose']}, {(s['window_dates'] or 'no bars')[:110]}" for s in r["stages_read"])
    roots = "27 price paths (17 W_ext)" if isinstance(r["traded_root"], list) else r["traded_root"]
    v = r["verdicts"].get("D.1f") or r["verdicts"].get("E.17", "")
    L.append(f"| {i} | {c(r['trigger_id'])} | {c(r['cluster_or_stage'])} | {roots} | {c(r['trigger_event'])} | {c(r['decision_time_ct'])} | {c(r['side_kind'])} | {c(r['intraday_hold'])} | {c(st)} | {c(v)} |")
L += ["", "## Non-bar inputs (rows that need one)", ""]
for r in d["rows"]:
    for inp in r["inputs_needed"][1:]:
        L.append(f"- {r['trigger_id']}: {inp['input']}; W_ext {inp['covers_w_ext']}, W_cf {inp['covers_w_cf']}; {inp['path']}; {inp['stated_range']}")
L += ["", "## Excluded", ""] + [f"- {e['item']}: {e['reason']}" for e in d["excluded"]]
L += ["", "## Not finished", ""] + [f"- {x}" for x in d["not_finished"]]
L += ["", "## Sources read (path and section)", ""] + [f"- {s['path']}: {s['section']}" for s in d["sources_read"]]
L += ["- reports/stage_e23_briefs/brief_inventory.md (whole); docs/prompts/STAGE_E.23.md lines 35-80 and 170-180",
      "- reports/E.14_RETURN.md lines 1-13, 161-165; reports/stage_e13_prereg_gexmom.md lines 1-30; reports/stage_e14_prereg_C1.md section 3; reports/stage_e18_prereg_C1b.md lines 67, 109-116",
      "- reports/stage_e16_prereg_H5.md sections 1-3; reports/E.10_RETURN.md lines 28, 117, 233, 308-312 (E-H1 mentions, no read)",
      "- reports/stage_e14_cal_releases.json coverage/counts; data/calendars/hist2010/*.json coverage/products; data/calendars/equity.py and data/cme_calendar.py docstrings; strategy/members/k5 and k8 _releases.py TABLE_RANGE",
      "- reports/stage_e16_settlement.md lines 32-34, 57, 90-94 (no MES row)"]
(O / "CDE.md").write_text("\n".join(L) + "\n")
print(len(L))
