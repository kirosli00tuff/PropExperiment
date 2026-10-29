"""FixVerifier (F4) items 4-5 and the addendum: the lead text appears verbatim in the recommendations file; the six
replacements of fix_lead_text_s4.py are applied (new text present, old text absent, pre-edit copies hold the old);
the RV2 grep patterns; the lead's numbers quoted in section 0."""
import re
from pathlib import Path

B = Path(__file__).resolve().parents[3]
lead = (B / "work/R4/lead_sections.md").read_text()
recs = (B.parent / "stage_e32b_recommendations.md").read_text()
s4a = (B / "work/R4/lead_sections_s4a.md").read_text()
pre = (B / "work/fix4/recs/recommendations_pre_s4fix.md").read_text()
body = lead.split("## Base rates", 1)[1]
lines = [l for l in body.splitlines() if l.strip() and not l.startswith("#")]
missing = [l for l in lines if l not in recs]
print("lead non-heading lines from '## Base rates':", len(lines), "; missing verbatim in recommendations:", len(missing))
for l in missing[:10]:
    print("  MISSING:", l[:160])
# contiguous blocks: each section body as one block
secs = re.split(r"\n(?=#{2,3} )", body)
blocks = 0
for s in secs:
    bl = "\n".join(l for l in s.splitlines()[1:] if l.strip())
    if bl and bl not in recs:
        print("  block not contiguous:", s.splitlines()[0][:80])
    elif bl:
        blocks += 1
print("contiguous section bodies found:", blocks, "of", sum(1 for s in secs if "\n".join(s.splitlines()[1:]).strip()))

REPS = [
    ("(NQ, ZN, 6E, CL, GC) on ZL without a pass",
     "(NQ, ZN, 6E, CL, GC; in E.12 also MBT, for its last two months) on ZL without a pass"),
    ("6E, CL, GC and ZC on M2K and RTY at 60 minutes and longer",
     "6E, CL, GC and ZC (in E.12 also MBT, for its last two months) on M2K and RTY at 60 minutes and longer"),
    ("(MNQ: read by E.20 and E.21;", "(MNQ: read by E.16, E.20, E.21, C1b and E.23;"),
    ("under 1% for MNQ, whose unread data after 2024-03 is the same short windows (power about 0.05 on 273 dates)",
     "under 1% for MNQ, whose only unread data are 2024-03..2025-03 (about 273 dates) and 2026-06-17 onward (power about 0.05 on the 273 dates)"),
    ("dates after 2024-03 the test's daily hurdle rises",
     "dates of 2024-03..2025-03 (2026-06-17 onward is also unread) the test's daily hurdle rises"),
    ("the test runs on MNQ and RTY over their 273 unread dates,",
     "the test runs on MNQ and RTY over their unread 2024-03..2025-03 and 2026-06-17+ dates,"),
]
print("\nsix replacements (old count lead/recs/s4a/pre ; new count lead/recs/s4a/pre):")
for a, b in REPS:
    print(f"  old {lead.count(a)}/{recs.count(a)}/{s4a.count(a)}/{pre.count(a)} ; new {lead.count(b)}/{recs.count(b)}/{s4a.count(b)}/{pre.count(b)} : {a[:50]}")

PATS = ["12.3 ticks", "not a small-cap lag", "priors of 1.5-4%", "about 1.5% each", "final build only if",
        "no cross-market configuration", "measured no correlation", "late-session", "E.12 also MES", "05678907"]
print("\npattern counts in recommendations / ranking / scope / draft_v3:")
rank = (B.parent / "stage_e32b_ranking.md").read_text()
scope = (B.parent / "stage_e32b_holding_scope.md").read_text()
draft = (B / "work/R4/draft_sections.md").read_text()
for p in PATS:
    print(f"  {p!r}: {recs.count(p)} / {rank.count(p)} / {scope.count(p)} / {draft.count(p)}")
# leftovers anywhere in the deliverables
for p in ("PENDING", "PLACEHOLDER", "still running", "TODO"):
    print(f"  {p!r} in recs/ranking/scope: {len(re.findall(p, recs))} / {len(re.findall(p, rank))} / {len(re.findall(p, scope))}")
# numbers in the lead text to eyeball
for pat in (r"1,305", r"0\.158", r"10\.0 ticks", r"23\.3", r"8\.2 ticks", r"12\.2 ticks", r"28\.5", r"1/19", r"4%", r"2\.50", r"2\.60",
            r"2\.38", r"0\.044", r"2\.8 ticks", r"51\.8", r"0\.165", r"0\.296", r"273", r"147 ticks", r"1\.25 ticks", r"15%"):
    print(f"  lead has {pat!r}: {len(re.findall(pat, lead))}")
