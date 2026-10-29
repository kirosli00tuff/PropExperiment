"""Session-4 lead corrections after the RecsAssembler's Lead check (2026-10-29 09:22 PDT): exact replacements in the
lead's own text, applied identically to work/R4/lead_sections.md and reports/stage_e32b_recommendations.md (where the
text appears verbatim); each count is checked (lead file exactly 1; recommendations file >= 1, reported)."""
from pathlib import Path

B = Path(__file__).resolve().parents[2]
FILES = [B / "work/R4/lead_sections.md", B.parent / "stage_e32b_recommendations.md"]
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
for f in FILES:
    s = f.read_text()
    for a, b in REPS:
        n = s.count(a)
        if f.name == "lead_sections.md":
            assert n == 1, (f.name, n, a[:50])
        print(f.name, n, "x", a[:48])
        s = s.replace(a, b)
    f.write_text(s)
