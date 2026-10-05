# Stage E.14 rulings on the Fable reviews (reports/stage_e14_review.md)

Lead: Opus 5.5 xhigh, 2026-10-05.

## Freeze review (Task 4), ruled about 03:20-03:28 PDT

Verdict APPROVE WITH FIXES: 1 BLOCKING, 2 SHOULD FIX, 12 NOTE. Every BLOCKING and SHOULD FIX finding is fixed below.
After the fixes: harness v10 manifest sha256 fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b (the
candidate 22fcdbbb... changed only by the comment fix of F-10), C1's input list
reports/stage_e14_c1_freeze_inputs.json sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e (43
files), C1's freeze reports/stage_e14_prereg_C1.md sha256 afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| F-01 Section 11's later-harness check is unsatisfiable: four manifest test files pin the two caps | BLOCKING | ACCEPTED | prereg_C1.md section 9 step 6 and section 11 step (2), and c1_replication/README.md, now allow exactly: data/config.py's ACCOUNT_2_CAP_USD, E14_EXT2010_SESSION_CAP_USD and their comments, plus the test assertions that pin those two values (tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64), nothing else. The asserts stay as they are (v10 unchanged). |
| F-02 The freeze contradicts itself on C7 (empty frames vs a sentinel bar) | SHOULD FIX | ACCEPTED | Section 3 states C7 as implemented (one sentinel bar dated 2019-05-31, after the window; the equality test named); section 12 lists the change. |
| F-03 The GEX CSV is not git-ignored | SHOULD FIX | ACCEPTED | .gitignore lists reports/stage_e14_briefs/gex/DIX.csv, DIX.csv.headers and reports/stage_e14_briefs/pages/gex/wayback/DIX_*.csv (git check-ignore confirms). .gitignore is not in the manifest. |
| F-04 "Freeze commit, then registration" is not enforced in code | NOTE | ACCEPTED as text; code left for a later harness | Section 11 step (1): the later session checks the freeze file is committed and unchanged in git before registering. |
| F-05 C1's code hashes are not self-verified | NOTE | ACCEPTED as text | Section 11 step (1): the input list is verified by script and the result written to that session's STATE before registering. |
| F-06 Registration and evaluation harness shas are not compared | NOTE | No change (intended; both are recorded) | none |
| F-07 C2 code interpretations, for any future C2 freeze | NOTE | Recorded for a future C2 freeze; inert now | none (C2 stopped) |
| F-08 Wayback captures of the SqueezeMetrics CSV are outside the prompt's source list | NOTE | ACCEPTED: recorded as a deviation (open choices) | read-only, hashes and last-row dates only; no verdict rests on it |
| F-09 The C2 stop and its two rulings | NOTE | No change (the reviewer finds both defensible; Task 8 recomputes the count) | none |
| F-10 The config comment says 01:42; the file's mtime says 01:34 | NOTE | ACCEPTED | The reset time is 01:34 PDT everywhere (data/config.py comment, gex.md, c2_result.md and .json, purchase.md, STATE, open choices). The manifest was rebuilt. |
| F-11 The 3% stop measures a byte-ratio proxy of the bill | NOTE | Recorded (no purchase happened) | none |
| F-12 Calendar citations; CME filings hosted on cftc.gov graded "cme" | NOTE | No change: a CME document hosted elsewhere is still CME's document; no count changes either way | none |
| F-13 The 2% windows recomputed | NOTE | No change | none |
| F-14 What a change invalidates | NOTE | Followed: manifest rebuilt, input list rerun, freeze sha re-recorded, in that order | none |
| F-15 The C2 side of F-01 (E14_SESSION_CAP_USD pinned at 0.0 in a test) | NOTE | Recorded for any future C2 decision | none |

## Verification (Task 8), ruled about 03:40 PDT

All verdict numbers MATCH (C2's count 135, bound 146, the stop; C1's reproduction, q_h60, q_hF, both M1 payloads
and feature_cols bit-identical on an independent rerun; the order of events in git, the ledgers and the files).
BLOCKING 0, SHOULD FIX 1, NOTE 5.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| F-V1 The terms ruling describes a button download; the file was fetched by curl with browser headers, plus Wayback copies | SHOULD FIX | ACCEPTED | reports/stage_e14_gex.md section 1 states what was done; the conclusion stands. |
| F-V2 44 eligible dates use a lag-1 row older than the prior CME trade date; the strictest reading gives 131 | NOTE | ACCEPTED | gex.md section 4 and c2_result.json record both readings; both stop C2. |
| F-V3 c2_result.json does not say when it was written | NOTE | ACCEPTED | a written_local field added. |
| F-V4 The Monday 2022-12-05 08:19 CT capture already holds Friday's row | NOTE | ACCEPTED | cited in gex.md section 3. |
| F-V5 One eligible date has GEX exactly 0 (not counted as negative) | NOTE | Recorded | gex.md section 4. |
| F-V6 The verifier's first `head` printed two rows' values (2011-05-02, 2011-05-03) | NOTE (incident) | Recorded: after the stop, no evaluation to bias; disclosed for any future C2-like test | gex.md section 4, c2_result.json, the return's guardrail evidence. |
