"""E.20 lead: assemble reports/stage_e20_product_summary.md from the 17 product_<ROOT>.json files plus
the lead's rulings (feature cut, Part A acceptance, GEX). Mechanical assembly; rulings are the lead's text below."""
import json, subprocess
ROOTS = ["NQ","RTY","ZT","ZF","ZN","TN","ZB","UB","6E","CL","NG","GC","ZC","ZS","ZL","HE","LE"]
def esc(s, n=None):
    s = ("" if s is None else str(s)).replace("|", "/").replace("\n", " ")
    return s if n is None or len(s) <= n else s[:n - 3] + "..."
out = ["# Stage E.20 Part A: product summary (lead consolidation, 2026-10-11)", "",
 "Sources: reports/stage_e20_briefs/product_<ROOT>.md and .json (17 ProductReader-<ROOT>-OpusHigh, opus high,",
 "spawned together 10:33 PDT, all returned by about 10:58), shared notes under reports/stage_e20_briefs/shared/.",
 "Evidence rows are the readers'; every number entering a decision below was read in the reader's file by the lead.",
 "Feature availability matrix: reports/stage_e20_briefs/feature_matrix.py (y yes, n no, p partial, u undetermined,",
 "first letter 2010-2019, second 2019-2024, '.' not applicable on that root's rows).", ""]
out += ["## 1. Lead rulings", "", open("reports/stage_e20_briefs/rulings_partA.md").read(), ""]
out += ["## 2. Feature availability matrix", "", "```",
        subprocess.run(["python3", "reports/stage_e20_briefs/feature_matrix.py"], capture_output=True, text=True).stdout.rstrip(),
        "```", ""]
out += ["## 3. Per-root evidence, proposals and notes", ""]
for r in ROOTS:
    d = json.load(open(f"reports/stage_e20_briefs/product_{r}.json"))
    out += [f"### {r}", "", "| id | effect | hold | gross bp | gross ticks | gross/net | sample | decay | source | grade |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for e in d.get("evidence", []):
        out.append("| " + " | ".join(esc(e.get(k), w) for k, w in [("id", 6), ("effect", 90), ("hold", 40),
                   ("gross_per_trade_bp", 20), ("gross_per_trade_ticks", 20), ("gross_or_net", 10), ("sample", 70),
                   ("decay_evidence", 90), ("source", 80), ("grade", 16)]) + " |")
    pf = d.get("proposed_features", [])
    out += ["", "Proposed features: " + ("none" if not pf else "")]
    for p in pf:
        out.append(f"- `{esc(p.get('name'),120)}`: ratio to D8 {p.get('ratio_to_d8')}, clears 1.5x per reader: {p.get('clears_1p5x')}; {esc(p.get('derivation'),300)}")
    un = d.get("unfinished", [])
    out += ["", f"Unfinished or unverified (reader): {len(un)} items; see product_{r}.md section 6.", ""]
open("reports/stage_e20_product_summary.md", "w").write("\n".join(out) + "\n")
print("written", len(out), "lines")
