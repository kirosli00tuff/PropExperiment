"""Lead corrections after the RecsDrafter's "Lead check" (2026-10-29 ~07:08 PDT). Whitespace-tolerant exact
replacements, each required to match exactly once per file; nothing is written unless every pair matches."""
import re
import sys
from pathlib import Path

R = [
 ("a market-maker or volume-incentive program in 2021-2026 (D2 b = 1 for 42 of 47 codes).",
  "a market-maker or volume-incentive program in 2021-2026 (D2 b = 1 for 42 of the 47 codes' own ratings and 46 of 47 "
  "as scored, where satellites take their leader's value)."),
 ("T1 gross 1.25 ticks against a 4.08-tick cost, t -0.53 net)", "T1 gross 1.25 ticks against a 4.08-tick cost, t -0.53)"),
 ("the rest-of-day momentum rule on YM (E16-H1)", "the rest-of-day momentum rule in E16-H1 (a pooled test whose roots included YM)"),
 ("the F08-type reversal E16-H4 on YM.", "the F08-type reversal E16-H4 (pooled, YM included)."),
 ("F09 asks whether crude oil, heating oil and the rest of the soy complex lead ZL at 15 to 60 minutes, through biofuel "
  "demand and crush margins that a slower participant set prices with a delay;",
  "F09 asks whether the rest of the soy complex (ZS and ZM) leads ZL at 15 to 60 minutes, through crush margins that a "
  "slower participant set prices with a delay (the dossier's F09 covers ZS and ZM, not crude or heating oil);"),
 ("Case. The Russell 2000 future against the large-cap index futures: a small-cap index whose constituents are slower to "
  "reprice may lag ES and NQ at 15 to 30 minutes.",
  "Case. The Russell 2000 future against the large-cap index futures at 15 to 30 minutes; the dossier's evidence "
  "(F09.E06) has the Russell leading ES, so the family's direction is an open question, not a small-cap lag."),
 ("but RTY has no clean test window before 2024-03 (E.20 and E.21 read it),",
  "but RTY has no clean test window before 2024-03 (E.16, E.20 and E.21 read it),"),
 ("Prior: about 1.5% (P(edge) about 0.04, discovery about 0.7; the only unread RTY data after 2024-03 is 2024-03..2025-03, "
  "13 months, about 273 dates, which raises the test's per-trade hurdle from 0.165 to 0.296 and cuts the chance of "
  "detecting a real edge to about half).",
  "Prior: under 1% (P(edge) about 0.04, discovery about 0.7; RTY's unread data after 2024-03 is 2024-03..2025-03 (13 "
  "months, about 273 dates) and 2026-06-17 onward, both needing the user's approval; on 273 dates the test's daily "
  "hurdle rises from 0.165 to 0.296 and its power at the 43-month detectable size falls to about 0.05)."),
 ("Prior: about 1.5% for YM and 1% for MNQ (P(edge) about 0.05, discovery about 0.6 at one trade a day, persistence about "
  "0.5; MNQ's only unread data after 2024-03 is the same 13-month window, and on Topstep's Standard Path its C falls to "
  "2.40).",
  "Prior: about 1.5% for YM if V31 were narrowed (P(edge) about 0.05, discovery about 0.6 at one trade a day, persistence "
  "about 0.5) and under 1% for MNQ, whose unread data after 2024-03 is the same short windows (power about 0.05 on 273 "
  "dates); on Topstep's Standard Path MNQ's C falls to 2.40."),
 ("F01's rest-of-day rule at a 30-minute hold was already read on YM (E16-H1, V31)",
  "F01's rest-of-day rule at a 30-minute hold was already read on YM in E16-H1's pooled test (V31)"),
 ("E16-H4, an F08-type reversal, failed on YM;", "E16-H4, an F08-type reversal, failed in a pooled test that included YM;"),
 ("where Baltussen et al.'s full-sample estimate implies about 15%", "where Baltussen et al.'s out-of-sample estimate implies about 15%"),
 ("1. Run at most one more registered build: the ZL program above. If it fails its discovery gate or its sealed test, the "
  "directional program stops, unless the user opens data that makes RTY F09 testable (2024-03 onward), in which case "
  "RTY F09 is the final build and its failure stops the program.",
  "1. Run at most one more registered build: the ZL program above. If it fails its discovery gate or its sealed test, the "
  "directional program stops. RTY F09, MNQ F08 and YM F08 are not fallbacks: their only test windows are closed by V31 "
  "or, after 2024-03, so short that the test's power at the detectable size is about 0.05."),
 ("recommend keeping it closed unless the ZL program passes; it only enables the weaker RTY and MNQ candidates.",
  "recommend keeping it closed unless the ZL program passes; it only enables the weaker RTY and MNQ candidates, at a "
  "power of about 0.05 on the 13 unread months."),
]

def pat(s):
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))

for f in sys.argv[1:]:
    p = Path(f); t = p.read_text()
    for old, new in R:
        n = len(pat(old).findall(t))
        if n != 1:
            sys.exit(f"refused: {f}: {old[:60]!r} matches {n} times")
    for old, new in R:
        t = pat(old).sub(lambda m: new, t, count=1)
    p.write_text(t)
    print("fixed", len(R), "passages in", f)
