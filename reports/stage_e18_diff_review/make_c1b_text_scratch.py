"""Stage E.18: write reports/stage_e18_prereg_C1b.md from C1's freeze by exact replacements.

Each replacement's old text must occur exactly once in C1's freeze (else refused, nothing written); the list
below is every change (section 13 of the output repeats it). Usage: uv run python
reports/stage_e18_briefs/make_c1b_text.py  (from the repo root).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

C1 = Path("reports/stage_e14_prereg_C1.md")
C1_SHA = "afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b"
OUT = Path("reports/stage_e18_diff_review/c1b_regen.md")

R = []  # (fix item, old, new)

R.append(("1", "# Pre-registration FROZEN: backward NG replication of the E.12 Gate 0 near-miss (C1)\n",
          "# Pre-registration FROZEN: backward NG replication of the E.12 Gate 0 near-miss (C1b, C1 re-registered)\n"))

R.append(("1", """Status: FROZEN by the Stage E.14 lead on 2026-10-05, from the draft reports/stage_e13_prereg_ngrepl.md (sha256
a16e860003a80806d97ff32e08e1265ae8feb1acb236153064bf32fb60714f43) with the user's decisions V25 item 1 and V26
applied, the Stage E.14 Task 1-2 results recorded (section 11) and the FreezeReviewer's required changes (listed
in section 12). Nothing else changed. FROZEN, AWAITING FUNDS: this test is NOT registered in Stage E.14. Its
registration (+2 on whatever N then is: 471 -> 473 if nothing else registers first), fresh quote, purchase, store builds and single evaluation happen in a later session,
under this freeze, with harness v10 or a later harness that changes only ACCOUNT_2_CAP_USD and the session caps
(section 11). This file's sha256 is written into reports/stage_e14_STATE.md. No 2010-2019 byte of any root exists
on disk or was read to write it.
""", """Status: FROZEN by the Stage E.18 lead on 2026-10-10. This file is C1's freeze reports/stage_e14_prereg_C1.md (sha256
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b), which the Stage E.14 lead froze on 2026-10-05 from
the draft reports/stage_e13_prereg_ngrepl.md (sha256 a16e860003a80806d97ff32e08e1265ae8feb1acb236153064bf32fb60714f43),
with exactly the Stage E.18 prompt's one fix (the user's decision V31) and the bookkeeping a new registration needs.
Section 13 lists every change; reports/stage_e18_c1b_diff.md shows them line by line. C1's registered attempt
(r001-C1, N 471 -> 473, Stage E.17) stopped at its guard C10 before any statistic existed and stays closed
(reports/stage_e14_c1_result.json; reports/E.17_RETURN.md section 3). C1b is a new registration (N 478 -> 480) in
Stage E.18, evaluated once on the six stores bought and built in Stage E.17, with harness v12; nothing is bought.
This file's sha256 is written into reports/stage_e18_freeze.json and reports/stage_e18_STATE.md. The 2010-2019
bytes now on disk were read in Stage E.17 as section 2 states; C1b's one change does not depend on anything read
there (section 3).
"""))

R.append(("1", """- Never read before the test: no program file has read NG or any leg before 2019-05 (annex section 5, evidence
  list). The test window is never summarized, plotted or printed before the single evaluation (section 9).
""", """- Never read before the test (C1, Stage E.14): no program file had read NG or any leg before 2019-05 (annex
  section 5, evidence list). Read since, in Stage E.17, before C1b's evaluation: the store builds (counts only:
  bars, trade dates, exclusions); C1's stopped run, which built the test window's features and printed every
  feature's applicable-row count and the panel's row counts, with no value, no return and no statistic
  (reports/stage_e17_review.md, C1 check 4); and the base-rule batch E16-H1..H5, whose own frozen rules read these
  six stores (H1 and H4 report per-product results whose window includes NG's 2010-07..2019-04 bars). None of it
  changes C1b: every parameter of sections 3 to 5 was frozen on 2026-10-05, before any 2010-2019 byte was bought,
  and C1b's one change (section 3, C10) follows from listing dates and section 2 alone. Beyond those reads, the
  test window is never summarized, plotted or printed before the single evaluation (section 9).
"""))

R.append(("2, 3", """- Guard against silently n/a features: applicable-row counts per feature, printed without values. The run stops
  if any feature live in E.12 has 0 applicable rows (ruling C10). These counts are computed from the test window's
  features, so they read the test bars (no values printed). A C10 stop therefore CLOSES this registered attempt.
  Any calendar correction and rerun is a new registration, with its tests counted in N again (Fable R-12, lead
  ruling).
""", """- Guard against silently n/a features: applicable-row counts per feature, printed without values. The run stops
  if any feature live in E.12 has 0 applicable rows (ruling C10), unless the feature is on the exempt list below.
  These counts are computed from the test window's features, so they read the test bars (no values printed). A C10
  stop therefore CLOSES this registered attempt. Any calendar correction and rerun is a new registration, with its
  tests counted in N again (Fable R-12, lead ruling).
  Exempt (C1b, V31): a feature whose leg section 2 already makes "not applicable" on every NG row of the test
  window, as in training. The list is decided from listing dates and section 2 alone, never from a count of the
  test window, and holds exactly two features:
  - g17_mbt, leg MBT: no MBT contract was listed on any date of 2010-06-07..2019-04-30. CME launched Micro Bitcoin
    futures on 2021-05-03 ("today launched Micro Bitcoin futures", CME press release of May 3, 2021) and its
    Bitcoin futures (BTC) for the trade date 2017-12-18 ("effective on Sunday, December 17, 2017 for a trade date of
    December 18", CME press release of December 1, 2017). BTC is not a leg of the model: no feature reads it, and
    E.12 never read it for g17_mbt, so BTC's listing does not make MBT listed. Section 2: "MBT is not listed (n/a by
    design)".
  - g17_cl, leg CL: listed throughout the window, but CL is the lead of NG's own cluster K4, and G17 never applies
    a cluster's own lead on that cluster's rows (ml_route_v2/signals/generic.py, ``_lead``). Section 2: "CL is never
    live on NG rows". Its E.12 reference count is 0 on both horizons, so C1's rule never reached it and this
    exemption changes nothing for it.
  Every other feature keeps C10 exactly as C1 had it: 0 applicable rows stops the attempt and closes it. Every
  other leg read by a feature live on NG rows in E.12 (NQ, ZN, 6E, GC, ZC) was a listed CME Group contract on every
  date of the window (launch dates before 2010 [unverified]; annex ruling C5: "all six were mature contracts in
  2010").
"""))

R.append(("1", "Two tests, T1 = NG h60 and T2 = NG hF, each with Gate 0's own statistic",
          "Two tests, T1 = NG h60 and T2 = NG hF (registered as C1b-T1 and C1b-T2), each with Gate 0's own statistic"))

R.append(("1", """ledger/trial_registrations.jsonl, in the later session. Test C2 stopped in Stage E.14 before its registration
(its power rule), so N is still 471 and C1's registration takes it to 473 unless another test registers first
(then +2 on that N). The q reproduction and the M1 fit are
not tests.""", """ledger/trial_registrations.jsonl, in Stage E.18: N 478 -> 480. C1's own registration (r001-C1, N 471 -> 473,
Stage E.17) stays counted; its attempt is closed. The q reproduction and the M1 fit are
not tests."""))

R.append(("1", "(t >= 3, DSR at N = 473, PBO)", "(t >= 3, DSR at N = 480, PBO)"))

R.append(("1", "nothing more is built on v2's model, and N is\n  473.",
          "nothing more is built on v2's model, and N is\n  480."))

R.append(("1", "## 9. Order of events (rulings C9, C20; amends L4-7; as the Stage E.14 prompt orders them)\n",
          "## 9. Order of events (rulings C9, C20; amends L4-7; as the Stage E.14 prompt orders them; C1b's steps as the\n"
          "Stage E.18 prompt orders them)\n"))

R.append(("1", """In a later session, under this freeze (section 11 lists what it verifies first):
5. Register T1 and T2 (N 471 -> 473, or +2 on N then) with this file's sha256.
6. Quote fresh (logged first), then buy NG and the five legs after the user's acct-2 top-up and a harness that
   differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else. The store builds print counts only.
7. Compute the replication features and run the evaluation once, behind a run-once marker
   (c1_replication.evaluate; the gate0_stage.py:260-264 pattern).
8. Report the verdict, then the descriptive outputs.
""", """In Stage E.17, under C1's freeze, C1's steps 5-8: registration r001-C1 (N 471 -> 473); the fresh quote and the
purchase of NG and the five legs under harness v11, as C1's step 6 allowed; the store builds (counts only); the one
evaluation, STOPPED at C10, the attempt closed.
In Stage E.18, under this freeze (section 11 lists what it verifies first), in this order:
5. Before the freeze: a Fable review of this file's diff against C1's freeze; the dry check (the amended C10 on
   E.12's reference counts against synthetic sentinel frames with MBT and CL absent and every other leg present,
   then with one non-exempt leg removed; no test-window bar read; reports/stage_e18_dry_check.md); the freeze
   commit.
6. Register C1b-T1 and C1b-T2 (N 478 -> 480) with this file's sha256. No quote and no purchase: the six ext2010
   stores of Stage E.17 are used.
7. Compute the replication features and run the evaluation once, behind a new run-once marker
   (reports/stage_e18_c1b_RUN_ONCE.json; c1_replication.c1b, which runs c1_replication.evaluate with C1b's ids and
   the amended C10; the gate0_stage.py:260-264 pattern).
8. Report the verdict, then the descriptive outputs.
"""))

R.append(("1", "## 10. Decisions made by the user before the freeze (V25, V26)\n",
          "## 10. Decisions made by the user before the freeze (V25, V26; C1b: V31)\n"))

R.append(("1", "4. **The calendar probe first** (V25 item 4): run inside Stage E.14 with the rule of section 9 step 1.\n",
          "4. **The calendar probe first** (V25 item 4): run inside Stage E.14 with the rule of section 9 step 1.\n"
          "5. **V31** (2026-10-10, after Stage E.17): C1 stopped at C10 on g17_mbt. The user chose this re-registration,\n"
          "   C1b, identical to C1 except that C10 exempts legs with no listed contract in the test window (MBT; CL),\n"
          "   which section 2 already treats as not applicable; N 478 -> 480; no purchase.\n"))

R.append(("1", "## 11. Frozen inputs, Stage E.14 results, and what the later session verifies first\n",
          "## 11. Frozen inputs, Stage E.14 results, and what Stage E.18 verifies first\n"))

R.append(("1", """  a Friday-to-Monday session handover and a day holding both an early halt and a late open (grains).
""", """  a Friday-to-Monday session handover and a day holding both an early halt and a late open (grains).
- **C1b's code (Stage E.18):** c1_replication/c1b.py and tests/test_c1b.py, hashed in reports/stage_e18_freeze.json.
  Every C1 file is unchanged: c1b runs the frozen c1_replication.evaluate with C1b's ids and the amended C10.
"""))

R.append(("1", """The later session, before anything else: (1) verify, by script, every entry of reports/stage_e14_c1_freeze_inputs.json (recording the result in its STATE
before registering), that this file is committed and unchanged in git (`git ls-files --error-unmatch` and
`git diff --quiet HEAD --` on it), the
E.12 state copy against its manifest, the model JSON and both M1 payloads against the hashes recorded in Stage
E.14's return; (2) verify that its harness differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and the comments beside them) and in the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else; (3) quote fresh, and stop if the
quote x 1.03 exceeds acct-2's headroom; then register, buy, build and evaluate once, in that order
(c1_replication/README.md gives the commands).
""", """Stage E.18, before registering: (1) verify, by script, every entry of reports/stage_e14_c1_freeze_inputs.json
(recording the result in its STATE) except reports/stage_e2b_harness_freeze.json, the harness manifest that
harnesses v11 and v12 replaced in Stage E.17 (item 2); that C1's freeze and this file are committed and unchanged in
git (`git ls-files --error-unmatch` and `git diff --quiet HEAD --` on each); the E.12 state copy against its
manifest; the model JSON and both M1 payloads against the hashes recorded in Stage E.14's return; (2) verify harness
v12 (ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32, Stage E.17) by its preflight. v12 differs
from v10 in data/config.py (the caps), data/pull_hist.py (plan ext2010h), data/hist_store.py (its docstring and the
ext2010h choice of its CLI), data/hist_calendar.py (a seventh group, livestock, and its docstring), the livestock
calendar file and tests; none of these changes the code C1b's evaluation calls for plan ext2010 (c1_replication
names its six groups itself); (3) verify the six ext2010 stores against reports/stage_e17_c1_store_hashes.json and
the calendars against reports/stage_e17_c1_calendar_hashes.json (Stage E.17's files). Then register and evaluate
once, in that order (c1_replication/c1b.py gives the command). No quote and no purchase.
"""))

SECTION_13 = """
## 13. Changes from C1's freeze (C1b; every one)

The Stage E.18 prompt's one fix has three items: (1) the ids C1b-T1 and C1b-T2 and a new registration (N 478 ->
480), C1's closed attempt cited; (2) C10's exemption clause; (3) every other feature keeps C10 as C1 had it.
1. Title: C1b (item 1).
2. Status block: C1b's provenance, C1's closed attempt, the new registration, no purchase (item 1).
3. Section 2, "Never read before the test": what Stage E.17 read since C1's freeze, so the statement stays true
   (item 1: C1's attempt and E.17 are cited).
4. Section 3, C10: the exempt list, g17_mbt and g17_cl (item 2), and "every other feature keeps C10 exactly as C1
   had it" with the listing state of the other legs (item 3).
5. Section 5: T1 and T2 are registered as C1b-T1 and C1b-T2 (item 1).
6. Section 6: N 478 -> 480 in Stage E.18; C1's registration stays counted (item 1).
7. Section 8: N = 480 in the pass and fail readings (item 1).
8. Section 9: C1's steps 5-8 as done in Stage E.17; C1b's steps 5-8 in Stage E.18, with no quote or purchase and a
   new marker (item 1).
9. Section 10: the user's decision V31 (item 1).
10. Section 11: C1b's code; what Stage E.18 verifies first, with harness v12 as the Stage E.18 prompt fixes it and
    no quote (item 1).
11. Section 13 added: this list.
Nothing else changed: sections 1, 4, 7 and 12, the model M1, q, the windows, the calendars, the trade rule, the
exclusions, the costs and the pass bar are C1's, byte for byte.
"""


def main() -> int:
    raw = C1.read_bytes()
    if hashlib.sha256(raw).hexdigest() != C1_SHA:
        print("REFUSED: C1's freeze is not afc5c10f...", file=sys.stderr)
        return 2
    text = raw.decode()
    for i, (item, old, new) in enumerate(R, 1):
        n = text.count(old)
        if n != 1:
            print(f"REFUSED: replacement {i} (item {item}) matches {n} times", file=sys.stderr)
            return 2
        text = text.replace(old, new)
    text = text.rstrip("\n") + "\n" + SECTION_13
    if OUT.exists():
        print(f"note: overwriting {OUT} (before the freeze only)")
    OUT.write_text(text)
    print(f"{OUT}: {len(R)} replacements + section 13; sha256 {hashlib.sha256(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
