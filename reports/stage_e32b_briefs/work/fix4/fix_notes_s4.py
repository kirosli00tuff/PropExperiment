"""Lead fixes for the FixVerifier's NOTE items N1-N5, N7 (REVIEW_fixes.md; 2026-10-29 session 4). Exact replacements,
each count checked: lead text identical in lead_sections.md and the recommendations file (1 each); others >= 1."""
from pathlib import Path

B = Path(__file__).resolve().parents[2]
R = B.parent
LEAD = [  # N4 in the lead's text (verbatim in both files)
    ("and 2026-06-17 onward (power about 0.05 on the 273 dates)",
     "and the dates after 2026-06-17, the end of the Stage E research windows (power about 0.05 on the 273 dates)"),
    ("over their unread 2024-03..2025-03 and 2026-06-17+ dates,", "over their unread 2024-03..2025-03 dates and those after 2026-06-17,"),
    ("(2026-06-17 onward is also unread)", "(the dates after 2026-06-17 are also unread)"),
]
DRAFT = [  # N4 and N5 in the drafter's and assembler's text
    ("(13 months; 2026-06-17 onward,", "(13 months; the dates after 2026-06-17,"),
    ("2026-06-17 onward not owned", "2026-06-18..2026-06-20 owned and unread (owned bars end 2026-06-20), later dates not owned"),
    ("| YM, NQ, RTY | 2026-06-17 onward |", "| YM, NQ, RTY | after 2026-06-20 |"),
    ("their one-day sigma is USD 544.45", "their combined daily P&L sigma at one lot each is USD 544.45"),
]
RECS_ONLY = [("after 2024-03; 2026-06-17 onward", "after 2024-03; the dates after 2026-06-17")]
RANK = [  # N3, N7 in the ranking header (template and output)
    ("with the same inputs and the fixed scorer at 08:51:03 PDT",
     "with the same inputs (econ32b.json rewritten in between by pass 2's collect, with the blocks the scorer reads\nunchanged) and the fixed scorer at 08:51:03 PDT"),
    ("is kept as work/score/score32b_out_run2.json and .md, and the two differ",
     "is kept as work/score/score32b_out_run2.json and .md (sha256 70809d50...; the rerun's score32b_out.json is\nee74c6a0...), and the two differ"),
]
JOBS = [
    (B / "work/R4/lead_sections.md", [(a, b, 1) for a, b in LEAD]
     + [("revised in session 4, 08:49-09:00 PDT, for LR-Q3b and RV2 S1-S3", "revised in session 4, 08:47-08:49 and 09:22 PDT, for LR-Q3b, RV2 S1-S3 and the Lead check", 1)]),
    (R / "stage_e32b_recommendations.md", [(a, b, 1) for a, b in LEAD] + [(a, b, 0) for a, b in DRAFT + RECS_ONLY]),
    (B / "work/R4/draft_sections.md", [(a, b, 0) for a, b in DRAFT]),
    (B / "work/rankmd/template.md", [(a, b, 1) for a, b in RANK]
     + [("Draft by RankingWriter-OpusHigh (worker, Opus 5.5 at high effort), {{NOW}}, for the lead.",
         "Draft by RankingWriter-OpusHigh (worker, Opus 5.5 at high effort), 2026-10-29 05:43 PDT, for the lead; rebuilt by\nScoreFixer-OpusHigh (wave F) at {{NOW}}.", 1)]),
    (R / "stage_e32b_ranking.md", [(a, b, 1) for a, b in RANK]
     + [("Draft by RankingWriter-OpusHigh (worker, Opus 5.5 at high effort), 2026-10-29 08:53 PDT, for the lead.",
         "Draft by RankingWriter-OpusHigh (worker, Opus 5.5 at high effort), 2026-10-29 05:43 PDT, for the lead; rebuilt by\nScoreFixer-OpusHigh (wave F) at 2026-10-29 08:53 PDT.", 1)]),
    (B / "work/R4/fix_lead_text_s4.py", [("(2026-10-29 ~09:24 PDT)", "(2026-10-29 09:22 PDT)", 1)]),
]
for f, reps in JOBS:
    s = f.read_text()
    for a, b, want in reps:
        n = s.count(a)
        assert (n == want) if want else (n >= 1), (f.name, n, a[:50])
        s = s.replace(a, b)
        print(f"{f.name}: {n} x {a[:44]}")
    f.write_text(s)
