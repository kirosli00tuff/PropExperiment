"""Assemble A3 blind ratings (JSON + Markdown) from the rater's work files.

Inputs (all in this folder): A3_blind_rules.json, A3_blind_firms.json, A3_blind_contracts.jsonl.
Outputs: reports/stage_e28_briefs/A3_blind_ratings.json and A3_blind_ratings.md.
No market data, no masked-key file, no web source is read here.
"""
import json
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
OUT_DIR = WORK.parent.parent
OUT_JSON = OUT_DIR / "A3_blind_ratings.json"
OUT_MD = OUT_DIR / "A3_blind_ratings.md"
RATED_AT = sys.argv[1] if len(sys.argv) > 1 else "unknown"

A_POINTS = {"high": 1, "medium": 0, "low": -1}
B_POINTS = {"low": 1, "medium": 0, "high": -1}
EXPECTED_CONTRACTS = [f"C{i:02d}" for i in range(1, 48)]
EXPECTED_FIRMS = [f"F{i:02d}" for i in range(1, 6)]


def load():
    rules = json.loads((WORK / "A3_blind_rules.json").read_text())
    firms = json.loads((WORK / "A3_blind_firms.json").read_text())
    rows = [json.loads(line) for line in (WORK / "A3_blind_contracts.jsonl").read_text().splitlines() if line.strip()]
    return rules, firms, rows


def validate(firms, rows):
    labels = [r["label"] for r in rows]
    if sorted(labels) != EXPECTED_CONTRACTS:
        raise SystemExit(f"contract labels wrong: {sorted(set(EXPECTED_CONTRACTS) ^ set(labels))}")
    if sorted(firms) != EXPECTED_FIRMS:
        raise SystemExit(f"firm labels wrong: {sorted(firms)}")
    for r in rows:
        if r["C1a"] not in A_POINTS or r["C1b"] not in B_POINTS or r["C6"] not in range(5):
            raise SystemExit(f"bad contract rating {r['label']}")
    for lab, f in firms.items():
        d = f["Rel_deductions"]
        rel = max(0, 4 - sum(d.values()))
        if rel != f["Rel"]:
            raise SystemExit(f"Rel mismatch {lab}: {rel} vs {f['Rel']}")
        if f["A"] not in range(5) or f["F"] not in (1, 2, 4):
            raise SystemExit(f"bad firm rating {lab}")
        if any(v not in range(5) for v in f["R"].values()):
            raise SystemExit(f"bad R {lab}")


def c1(r):
    return 2 + A_POINTS[r["C1a"]] + B_POINTS[r["C1b"]]


def build_json(rules, firms, rows):
    contracts = {}
    for r in sorted(rows, key=lambda x: x["label"]):
        entry = {
            "C1a": r["C1a"],
            "C1b": r["C1b"],
            "C6": r["C6"],
            "C1_computed": c1(r),
            "reasons": r["reasons"],
            "flags": r.get("flags", []),
        }
        if r["C6"] == 1:
            entry["C6_alt_cross_sheet_class"] = 2
        if r["C1b"] == "medium":
            entry["C1b_alt_if_partial_unknown_counts_high"] = "high"
        contracts[r["label"]] = entry
    return {
        "_about": (
            "Stage E.28 Part A blind ratings (BlindScorer-OpusXHigh, Opus 5.5, xhigh), rated " + RATED_AT + ". "
            "Read only reports/stage_e28_ranking_spec.md (sha256 89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f, "
            "checked), reports/stage_e28_briefs/READER_RULES.md, A3_masked_contracts.json and A3_masked_firms.json. "
            "Not read: A3_mask_key.json, any A0/A1/A2 file, any page under pages/, any web source; no searches. "
            "C1_computed = 2 + (a: high +1, medium 0, low -1) + (b: low +1, medium 0, high -1), shown for convenience; "
            "the lead's script remains the scorer of record. Rel = 4 minus the deductions, not below 0."
        ),
        "_rules_applied": rules,
        "_global_notes": [
            "C6 cross-sheet CLASS evidence: the X39 order-book studies (Dixon 2017 price-flip classification on X39 level II; "
            "the energy readers' 'X39 OFI studies ... significant at the one-second horizon') are 'futures broadly' evidence for every "
            "non-equity product, but appear as CLASS items only in C17, C19 and C40. C6 here is rated per sheet, as the anchor "
            "'nothing found within the reader's search budget' reads. If the lead applies that CLASS evidence across sheets, every "
            "C6 = 1 becomes 2 (field C6_alt_cross_sheet_class).",
            "C1b partial evidence: every C1b = medium rests on a negative or expired market-maker programme search with HFT share and "
            "spread unknown. Under a stricter reading that such partial evidence is still 'unknown' (spec default high), each becomes "
            "high (field C1b_alt_if_partial_unknown_counts_high). No product met 'low'.",
            "Gate-relevant alternatives: C25 C6 = 0 (fails the Layer 1 gate) rests on an abstract-only SSRN preprint; C07 alt 0 and "
            "C15 alt 0 under stricter readings; F04 A alt 0 (pair gate) under a strict reading of its 'scalping algorithms' ban; "
            "metals products with a 50K cap of 0 at F03 and two restricted metals products at F05 need the listing gate (key needed).",
            "Sheet defects: F04 Rel_evidence rule_changes_12m string is cut at 700 characters ('... it is not forbidde'). "
            "Masking leaks: some sheets keep identifying text (CFTC market names such as 'UST 5Y NOTE' and 'MICRO 10 YEAR', a "
            "'relation_to_ZN' key, CFTC codes, product names inside firm quotes, an account-type acronym and a lawsuit caption in F03, "
            "forum and staff names in platform records). Ratings were made from the evidence text only; no outside knowledge of which "
            "product, firm or platform a label is was used.",
        ],
        "contracts": contracts,
        "firms": firms,
    }


def md_firms(firms):
    lines = ["## Firm ratings", "", "| Firm | R by class | A | F | Rel deductions (age, payout, rules, regulator) | Rel |", "|---|---|---|---|---|---|"]
    for lab in EXPECTED_FIRMS:
        f = firms[lab]
        r = ", ".join(f"{k} {v}" for k, v in sorted(f["R"].items()))
        if "R_by_size" in f:
            r += "; micro: " + ", ".join(f"{k} {v['micro']}" for k, v in f["R_by_size"].items())
        if "R_not_rated" in f:
            r += "; not rated: " + ", ".join(f["R_not_rated"])
        d = f["Rel_deductions"]
        ded = f"{d['under_2_years']}, {d['payout_delays_denials_disputes_12m']}, {d['two_plus_adverse_rule_changes_12m']}, {d['regulatory_action_vs_firm']}"
        lines.append(f"| {lab} | {r} | {f['A']} | {f['F']} | {ded} | {f['Rel']} |")
    lines.append("")
    for lab in EXPECTED_FIRMS:
        f = firms[lab]
        lines += [f"### {lab}", ""]
        for k in ("R", "A", "F", "Rel"):
            lines.append(f"- {k}: {f['reasons'][k]}")
        lines.append(f"- F platform rated: {f['F_platform_rated']}")
        if "R_not_rated" in f:
            for k, v in f["R_not_rated"].items():
                lines.append(f"- R not rated ({k}): {v}")
        for fl in f.get("flags", []):
            lines.append(f"- Flag: {fl}")
        lines.append("")
    return lines


def md_contracts(rows):
    lines = ["## Contract ratings", "", "| Label | C1 (a) | C1 (b) | C1 | C6 |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda x: x["label"]):
        lines.append(f"| {r['label']} | {r['C1a']} | {r['C1b']} | {c1(r)} | {r['C6']} |")
    lines.append("")
    for r in sorted(rows, key=lambda x: x["label"]):
        lines += [f"### {r['label']}", ""]
        for k in ("C1a", "C1b", "C6"):
            lines.append(f"- {k}: {r['reasons'][k]}")
        for fl in r.get("flags", []):
            lines.append(f"- Flag: {fl}")
        lines.append("")
    return lines


def md_counts(rows):
    from collections import Counter
    ca = Counter(r["C1a"] for r in rows)
    cb = Counter(r["C1b"] for r in rows)
    c6 = Counter(r["C6"] for r in rows)
    cc = Counter(c1(r) for r in rows)
    return [
        "## Counts",
        "",
        f"- C1 (a): high {ca['high']}, medium {ca['medium']}, low {ca['low']} (47 labels).",
        f"- C1 (b): high {cb['high']}, medium {cb['medium']}, low {cb['low']}.",
        f"- C1: " + ", ".join(f"{k}: {cc[k]}" for k in sorted(cc)) + ".",
        f"- C6: " + ", ".join(f"{k}: {c6[k]}" for k in sorted(c6)) + ". No product reached 4 under the rules above.",
        "",
    ]


def build_md(rules, firms, rows, data):
    lines = [
        "# Stage E.28 Part A: blind ratings (A3)",
        "",
        f"BlindScorer-OpusXHigh (Opus 5.5, xhigh), rated {RATED_AT}. Machine-readable copy: "
        "reports/stage_e28_briefs/A3_blind_ratings.json (same ratings, plus alternatives and the rules as applied).",
        "",
        "## What was read",
        "",
        "- reports/stage_e28_ranking_spec.md, sections 2 and 3 for the anchors (sha256 89347e97...a5f, checked against the STATE file); "
        "reports/stage_e28_briefs/READER_RULES.md.",
        "- reports/stage_e28_briefs/A3_masked_contracts.json (47 labels C01..C47) and A3_masked_firms.json (5 labels F01..F05).",
        "- Not read: A3_mask_key.json, any A0, A1 or A2 file, any page under reports/stage_e28_briefs/pages/, any web source. No searches.",
        "",
        "## Rules as applied",
        "",
        "The spec's anchors leave some readings open; these are the readings used for every label, so ratings are comparable.",
        "",
    ]
    for crit, items in rules.items():
        lines.append(f"**{crit}**")
        lines.append("")
        lines += [f"- {it}" for it in items]
        lines.append("")
    lines += [
        "**Firms**",
        "",
        "- R: a firm-wide rule that applies to every product does not lower R. A position-size cap of one contract or more does not "
        "bind a 1-contract strategy and no lower anchor describes it, so it is not counted; where this changes a class result the "
        "split is given (R_by_size). A product the firm lists but bars from trading is a listing-gate matter, flagged, not an R score.",
        "- A: anchors 4 and 3 need automated trading through an API explicitly permitted in both stages. Automation permitted only "
        "through listed platforms, with no firm page naming an API route, is anchor 2 ('permitted only through a named third-party "
        "platform'). A published rule whose wording could catch a 20-round-trip, 1-minute-hold strategy makes it borderline (2).",
        "- F: forums are pointers only under READER_RULES, so a fill rule known only from a forum post is 'undocumented' (1). "
        "Where a firm offers several API platforms, the one the strategy would use is rated and named; ties go to the higher.",
        "- Rel: per the lead's reading, a 'documented' item with no documentation in the sheet takes no deduction, and an unknown "
        "founding date takes the under-2-years deduction (none was unknown here). Review-site and snippet reports are not documentation.",
        "",
    ]
    lines += md_firms(firms)
    lines += md_contracts(rows)
    lines += ["## Notes for the lead", ""]
    lines += [f"- {n}" for n in data["_global_notes"]]
    lines.append("")
    lines += md_counts(rows)
    return "\n".join(lines)


def main():
    rules, firms, rows = load()
    validate(firms, rows)
    data = build_json(rules, firms, rows)
    OUT_JSON.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    OUT_MD.write_text(build_md(rules, firms, rows, data) + "\n")
    print(f"wrote {OUT_JSON.name} ({OUT_JSON.stat().st_size} B) and {OUT_MD.name} ({OUT_MD.stat().st_size} B)")


if __name__ == "__main__":
    main()
