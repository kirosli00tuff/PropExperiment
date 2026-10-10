"""Stage E.18: write reports/stage_e18_c1b_diff.md (C1b's text and code against C1's freeze, line by line).
Usage: python3 reports/stage_e18_briefs/make_diff_doc.py  (from the repo root, after make_c1b_text.py)."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

C1 = Path("reports/stage_e14_prereg_C1.md")
C1B = Path("reports/stage_e18_prereg_C1b.md")
GEN = Path("reports/stage_e18_briefs/make_c1b_text.py")
OUT = Path("reports/stage_e18_c1b_diff.md")


def sha(p: Path | str) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main() -> None:
    diff = subprocess.run(["diff", "-u", str(C1), str(C1B)], capture_output=True, text=True).stdout
    code = subprocess.run(["git", "status", "--short", "--", "c1_replication", "tests"],
                          capture_output=True, text=True).stdout
    doc = f"""# Stage E.18: C1b's text and code against C1's freeze (line-by-line diff)

Lead, Stage E.18 Step 1 (revised after the Step 2 review), 2026-10-10 (PDT). Inputs: C1's freeze {C1} (sha256
{sha(C1)}); C1b's text {C1B} (sha256 {sha(C1B)} at the time of this diff; the freeze manifest
reports/stage_e18_freeze.json records the final one). Generator: {GEN} (sha256 {sha(GEN)}), 15 exact replacements on
C1's freeze, each required to match exactly once, plus section 13 appended. This file's generator:
reports/stage_e18_briefs/make_diff_doc.py.

Revision after DiffReviewer-FableXHigh (reports/stage_e18_review.md; rulings reports/stage_e18_rulings.md R-1..R-5):
section 3's exempt criterion no longer says "as in training" (S-1) and says why CL qualifies (N-1); section 2 names
H5 beside H1 and H4 (N-2); section 11 names E.17's ext2010h session constants in data/config.py (N-3); section 9
step 7 names the result path (N-6). No code changed in the revision.

## 1. What each change is (the prompt's THE ONE FIX: item 1 ids and registration, item 2 the C10 clause, item 3 every other feature unchanged)

| # | Where | Item | Change |
|---|---|---|---|
| 1 | title | 1 | "(C1)" -> "(C1b, C1 re-registered)" |
| 2 | status block | 1 | C1b's provenance (C1's freeze sha256, the draft's), C1's closed attempt cited, new registration N 478 -> 480, harness v12, no purchase; the 2010-2019 bytes now on disk were read in E.17 (section 2) |
| 3 | section 2, "Never read before the test" | 1 | C1's sentence "no program file has read NG or any leg before 2019-05" became false in E.17 (store builds, C1's stopped run, the base-rule batch on these stores: H1, H4 and the composite H5 cover NG); the bullet now says what was read and why none of it changes C1b. Without this, C1b's text would assert something false. |
| 4 | section 3, C10 bullet | 2, 3 | "unless the feature is on the exempt list below"; the criterion (section 2's not-applicable-by-design treatment of an unlisted or own-cluster leg); the exempt list g17_mbt (MBT not listed; BTC is not a leg) and g17_cl (own cluster lead; reference 0, so a no-op); "every other feature keeps C10 exactly as C1 had it"; the other legs' listing state |
| 5 | section 5 | 1 | T1, T2 "registered as C1b-T1 and C1b-T2" |
| 6 | section 6 | 1 | N 478 -> 480 in Stage E.18; C1's registration stays counted |
| 7 | section 8, pass | 1 | DSR at N = 480 |
| 8 | section 8, fail | 1 | N is 480 |
| 9 | section 9 heading | 1 | "C1b's steps as the Stage E.18 prompt orders them" |
| 10 | section 9 later-session steps | 1 | C1's steps 5-8 as done in E.17; C1b's steps 5-8 (review, dry check, freeze commit; register; evaluate once behind a new marker, result path named; verdict then descriptive); no quote, no purchase |
| 11 | section 10 heading | 1 | "(V25, V26; C1b: V31)" |
| 12 | section 10 item 5 | 1 | V31 |
| 13 | section 11 heading | 1 | "what Stage E.18 verifies first" |
| 14 | section 11, new bullet | 1 | C1b's code (c1_replication/c1b.py, tests/test_c1b.py); every C1 file unchanged |
| 15 | section 11, last paragraph | 1 | what Stage E.18 verifies before registering: C1's freeze inputs except the harness manifest (replaced by v11 and v12 in E.17), C1's freeze and this file in git, the E.12 state copy, the model and payloads; harness v12 by its preflight and the list of its differences from v10; the stores and calendars against E.17's hash files; no quote, no purchase |
| 16 | section 13 (new) | 1 | the list of changes |

Unchanged byte for byte: sections 1, 4, 7 and 12, and in sections 2, 3, 5 and 8 every line not listed above (the
model M1, q, the windows, the vehicle and legs, the C7 sentinel frames, the trade rule and exclusions, the calendars
and C12, the costs, the pass bar, the power and prior, the outcome readings apart from N).

## 2. The exempt list: listing dates and section 2 only

The applicable-row counts that E.17's stopped run printed (reports/stage_e14_c1_result.json, guards.C10; counts only,
no values) are known to the lead. C1b's design change does not use them: the exempt list follows from the listing
state of each leg in 2010-06-07..2019-04-30 and from section 2's text, and would be the same whatever those counts
were. Every leg and non-leg input of the 30 features live on NG rows in E.12 (reference counts from
reports/stage_e14_c1_model.json, E.12's training panel, not the test window):

| Input | Features live on NG rows in E.12 that read it (E.12 reference h60 / hF) | State on every date of 2010-06-07..2019-04-30 | C10 in C1b |
|---|---|---|---|
| NG (own path) | cp1_ret, cp2_brk, cp2_range, cp3_clv, g01-g11, k4_ovr_pct, k4_ovr_ret, k4_ngpre_* (with the NGS table) | listed (the vehicle; annex ruling C5) [launch date unverified] | applies |
| NQ | g17_nq (2453 / 2345) | listed [launch date unverified; annex C5] | applies |
| ZN | g17_zn (2457 / 2341) | listed [unverified; annex C5] | applies |
| 6E | g17_6e (2450 / 2354) | listed [unverified; annex C5] | applies |
| GC | g17_gc (2423 / 2311) | listed [unverified; annex C5] | applies |
| ZC | g17_zc (2468 / 2351) | listed [unverified; annex C5] | applies |
| MBT | g17_mbt (87 / 84; 29 trade dates 2024-01-04..2024-02-29, Fable E.17 C1 check 1) | NOT listed: CME Micro Bitcoin futures launched 2021-05-03 (verbatim quote, reports/stage_e18_briefs/pages/LOG.md). BTC (from the trade date 2017-12-18) is not a leg: no feature reads BTC | exempt (section 2: "MBT is not listed (n/a by design)") |
| CL | g17_cl (0 / 0) | listed, but NG's own cluster lead (K4): generic.py `_lead` sets app 0 on own-cluster rows | exempt; a no-op (reference 0; section 2: "CL is never live on NG rows") |
| MES | none (no covered signal reads it; P-1a) | n/a | n/a |
| Release calendar (NGS, WPSR, FOMC) | g13_min_to_rel, g14_min_since_rel, g15_rel_day, k4_ngpre_msince, k4_ngpre_mto | published on every week of the window; sourced in E.14 (NGS 470, WPSR 470, FOMC 72; reports/stage_e14_calendars.md) | applies |
| Group calendars, D6 sessions, energy full sessions | g12_dow, g16_month_end, the clock, g09, k4_ovr_* reference dates | sourced in E.14, 0 unsourced trade dates in the window; energy full sessions 2,250 | applies |

No other input of a live feature is absent by design in the window, so no third feature can meet C1's
contradiction (live in E.12, absent by design in 2010-2019). Features with a zero E.12 reference (34 of 64, g17_cl
among them) are never reached by C10 under C1's rule or C1b's. DiffReviewer-FableXHigh traced all 30 independently
(reports/stage_e18_review.md, check 3).

## 3. The code change

- New: c1_replication/c1b.py (runs the frozen c1_replication.evaluate.run inside `c1b_profile()`, which swaps
  evaluate's TEST, TEST_IDS, HORIZON_OF, c10_check and preconditions for C1b's and restores them; c10_check is C1's
  function called on the reference less C10_EXEMPT; preconditions is C1's plus the C1b record in the marker and
  result; the CLI defaults to C1b's freeze and marker paths). New: tests/test_c1b.py (74 tests).
- Every C1 file is unchanged (c1_replication/*.py other than c1b.py, tests/test_c1_*.py, tests/_c1_*.py): the E.14
  freeze-inputs list still verifies them (start checks, reports/stage_e18_briefs/start_checks.txt).
- Why not an edit in place (c10_check lives in c1_replication/evaluate.py): editing evaluate.py or constants.py
  would change C1's frozen code (hashed in the E.14 freeze-inputs list and in C1's result), break C1's own tests
  (which pin C1's ids and marker) and make C1's closed attempt irreproducible from its files. The new module leaves
  all of that intact and confines C1b's difference to one file. Lead decision D-1.
- git status of code paths at the time of this diff:
```
{code.rstrip()}
```

## 4. The text diff (`diff -u {C1} {C1B}`)

```diff
{diff.rstrip()}
```
"""
    OUT.write_text(doc)
    print(f"written {OUT}: {len(doc.splitlines())} lines, sha256 {sha(OUT)}")


if __name__ == "__main__":
    main()
