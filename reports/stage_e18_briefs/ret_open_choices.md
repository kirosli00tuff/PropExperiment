## 6. Open choices (every decision the lead made on its own, with the reason)

1. **C1b's code is a new module, not an edit of C1's files** (D-1). The prompt allowed the change "in
   c1_replication/guards.py (or wherever c10_check lives)"; c10_check lives in c1_replication/evaluate.py. The lead
   wrote c1_replication/c1b.py, which runs the frozen evaluate.run with five attributes swapped and restored, the
   pattern c1_replication.context.hist_tables already uses. Reason: an edit of evaluate.py or constants.py would have
   changed C1's frozen code (hashed in E.14's freeze-inputs list and in C1's result), broken C1's own tests (they pin
   C1's ids and marker) and left C1's closed attempt irreproducible from its files. Every C1 file is byte-identical;
   C1b's difference is one file. Fable checked the swap (Step 2, check 4).
2. **g17_cl is on the exempt list, with its true reason** (D-2). V31 and the prompt name CL; the prompt's criterion
   sentence ("no listed contract on any date of the test window") does not fit CL, which was listed throughout. The
   text exempts CL under section 2's "CL is never live on NG rows" (NG's own cluster lead, never applicable on its
   cluster's rows) and says that the exemption is a no-op (E.12 reference 0). Reason: follow the user's list without
   writing a false listing claim into a freeze (Fable N-1 agreed; the clarifying sentence was added, R-2).
3. **C1's section 2 "never read" sentence was corrected** (D-3). After E.17 it was false: the store builds, C1's
   stopped run (C10 counts) and the base-rule batch H1-H5 (whose H1, H4 and composite H5 results include NG's
   2010-07..2019-04 bars) read these six stores. C1b's text says so and why it changes nothing (every parameter was
   frozen on 2026-10-05, before any purchase; the one change uses listing dates and section 2 only). The lead did not
   open the H1/H4 per-product values. Reason: a freeze must not assert something false; this is bookkeeping of item 1.
4. **C1's section 11 harness clause was replaced by v12** (D-4). C1 required the evaluating harness to differ from v10
   only in data/config.py; the prompt fixes v12, which also changes data/pull_hist.py, hist_store.py, hist_calendar.py
   and adds the livestock calendar. C1b's section 11 names v12 and lists the differences; Fable confirmed none touches
   the ext2010 evaluation path (get_plan("ext2010") equal on every v10 field). Reason: otherwise C1b's own text would
   contradict the prompt's harness, a second contradiction of the kind this stage guards against.
5. **The C1b record in the marker and result** (part of D-1). c1b wraps C1's preconditions to add the ids and the
   exempt list to the records written before any bar is read. Reason: the result shows g17_mbt at 0 applicable rows;
   the record makes the exemption in force visible in the same file. Not required by the fix; one dataclass replace.
6. **The dry check's design** (D-5): synthetic bars (tests._c1_fixtures, seed 11) over the sub-window
   2010-06-07..2011-09-30 on the pinned official 2010-2019 calendars, so every calendar-driven feature (NGS release
   times, overnight sessions) is exercised as in the run; each of the five non-exempt legs removed in turn rather than
   one (the prompt asked for one). A smoke run on SYNTHETIC calendars (scratch output) tested the script's mechanics
   before the review; the real dry check ran after the review, as the prompt orders. The expected outcome was written
   into STATE before the real run.
7. **Listing evidence** (D-6): only the two dates the exemption turns on (MBT 2021-05-03, BTC trade date 2017-12-18)
   were fetched and quoted verbatim; the long-established contracts' launch dates are marked [unverified]. Reason: the
   prompt's rule (a quote or [unverified]); no doubt exists for NQ, ZN, 6E, GC, ZC, CL, NG (Fable N-9 agreed).
8. **Review fixes in the text only** (R-1..R-5): S-1 and four notes taken as text precision; N-6 (a fixed result
   path) answered in the text, with no code change, because the fixed marker path is already the run-once guard.
9. **The start suite's three failures were treated as an invocation artifact** (D-7): the lead had set
   PYTHONPYCACHEPREFIX for the suite (the prompt's fresh-prefix rule is for harness commands; its suite command has
   none); the three bytecode tests in tests/test_harness_freeze.py then fail by construction. The file rerun without
   the prefix passed 17/17, and the end suite ran the prompt's exact command. The full start suite was not rerun.
10. **The statistic's two means** (D-8): gate0._b_test's `mean` (criterion 1) is the trade-level mean, its t_B the
    per-date mean; the freeze's wording ("per-date mean") fits t_B. The lead applied the frozen code as C1 and E.12
    did, and had Fable compute both readings; the verdict is FAIL under either.
11. **Times corrected from `date`** (process): three times in this stage the lead typed estimated times that ran ahead
    of the clock (12:24 for 11:57; 12:03-12:04 for 12:00; an end of "about 12:55" for 12:48:04); each was replaced
    from `date`, file mtimes or git.
12. **Commit scope**: both commits staged explicit paths (E.18's files, the two Fable scratch folders); the
    untracked pages of earlier stages, .claude/worktrees/ and other untracked files were left alone.
