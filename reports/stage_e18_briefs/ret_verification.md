## 5. Verification (each Fable finding, the ruling and the fix; rulings in reports/stage_e18_rulings.md)

**Step 2, DiffReviewer-FableXHigh (11:58-12:14): APPROVE WITH FIXES.** All six checks PASS (reports/stage_e18_review.md
lines 3-243).

| Finding | What | Ruling | Fix |
|---|---|---|---|
| S-1 SHOULD FIX | section 3's criterion said "as in training", false read literally for g17_mbt (87/84 training rows) | R-1 accepted | reworded via the generator; text and diff regenerated before the freeze |
| N-1 | the prompt's criterion sentence does not fit CL (listed), though the prompt names CL | R-2 accepted | one clause: for CL the operative test is section 2's "not applicable by design" |
| N-2 | section 2 named H1 and H4; the composite H5 also covers NG | R-3 accepted | H5 named |
| N-3 | section 11 omitted E.17's ext2010h session constants in data/config.py | R-3 accepted | named |
| N-4 | the result's code_sha256 lists c1b.py beside C1's ten files | R-5 no action | expected; pins c1b.py |
| N-5 | C1's log and schema strings carry into C1b's files | R-5 no action | the "test": "C1b" field distinguishes them |
| N-6 | --out stays free; the result path is not fixed | R-4 text only | section 9 step 7 names the path; the fixed marker is the run-once guard |
| N-7 | test-coverage misses | R-5 no action | none weakens clause 2's coverage |
| N-8 | text fixes must go through the generator and the diff | R-5 followed | done |
| N-9 | older launch dates [unverified] | R-5 no action | the two decisive dates are verified verbatim |

**Step 6, VerdictVerifier-FableXHigh (12:19-12:29): VERIFIED WITH NOTES** (reports/stage_e18_review.md lines 245-366;
scripts reports/stage_e18_verify/). Own recompute on disk at 12:23:48, before the result, marker or log was opened;
66 compared items, 0 unequal at 1e-9; trades_sha256 equal; amended C10: nothing dead; order of events as the freeze's
section 9; one marker, one result; 105 input items, 1 unequal (NOTE 2); spend ledger unchanged.

| Finding | What | Ruling | Fix |
|---|---|---|---|
| NOTE 1 | criterion 1 in code reads the trade-level mean, the freeze text says per-date; T1 +0.585 vs -0.914 | V-1 recorded | none: both below 2.562 and p 0.797, FAIL under either reading; carried to section 7 as a lesson |
| NOTE 2 | C1's freeze-inputs list holds the v10 harness manifest; the run used v12 | V-2 no action | declared in C1b's section 11 |
