"""Stage E.19 lead: section 5 table (each Fable finding, its ruling and fix) from the two review files."""
import re

RULING = {
    "RR-1": "ACCEPTED: churn metrics, label (L-19), forfeiture column added post hoc; recommendations only low churn in band; fee-budget stop rule",
    "RR-2": "ACCEPTED as a bot rule (below full tier size through releases); no rerun",
    "RR-3": "ACCEPTED: slots read as different products; bot rule one product per account or same direction",
    "RR-4": "ACCEPTED: P35 bot_implication fixed by the lead (purchase rate)",
    "RR-5": "ACCEPTED: copy-traded figure carries the RTP caveat",
    "ER-1": "ACCEPTED: results state SEs are pool-conditional; total 1.3x-2.5x; no sign/ranking change",
    "ER-2": "ACCEPTED: label kept, stated as partly definitional; reset-inclusive rate reported",
    "ER-4": "ACCEPTED: lead's draft corrected (f 0.50 claim)",
    "ER-5": "ADOPTED in the text",
    "ER-13": "Phase C run: all verdict cells reproduce",
    "ER-14": "ACCEPTED: text says the f 0.50 DLL cell's sign is not established",
}


def rows(path, prefix):
    out = []
    for line in open(path):
        m = re.match(rf"\| ({prefix}-\d+) \| ([A-Z ]+) \| ([^|]+) \| ([^|]+) \|", line)
        if m:
            fid, grade, area, finding = (x.strip() for x in m.groups())
            short = finding if len(finding) <= 150 else finding[:147].rsplit(" ", 1)[0] + "..."
            out.append((fid, grade, area[:60], short, RULING.get(fid, "Acknowledged (NOTE); no change needed or text note")))
    return out


print("| ID | Grade | Area | Finding (abridged) | Ruling and fix |\n|---|---|---|---|---|")
for r in rows("reports/stage_e19_review_rules.md", "RR") + rows("reports/stage_e19_review.md", "ER"):
    print("| " + " | ".join(x.replace("|", "/") for x in r) + " |")
