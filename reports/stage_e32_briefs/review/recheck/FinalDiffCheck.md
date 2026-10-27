# FinalDiffCheck: v0.4 -> v0.5 of the E.32 discovery protocol

- Checker: FinalDiffCheck-FableXHigh (Fable 5.1, xhigh), Stage E.32, 2026-10-27.
- Object: reports/stage_e32_discovery_protocol.md, DRAFT v0.5, 845 lines, sha256 read at start
  9b699dc15f82731eaab7e5dc31eebe4e4e67208e3256e71f4475c7c01e7af26d (matches the brief).
- Base: reports/stage_e32_briefs/work/lead/protocol_v0.4.md (822 lines). Diff saved to
  reports/stage_e32_briefs/review/recheck/work_final/diff_v04_v05.txt (15 hunks, 109 lines).
- Inputs read by grep and line range: SpotCheck_A.md, SpotCheck_B.md (findings S-A-1..9, S-B-1..7), stage_e32_STATE.md
  lines 509-520 (the 12:50-12:58 LEAD entry), docs/prompts/STAGE_E.33.md lines 40-50, 126-166, 226-238,
  screening/trial_registry.py lines 42-50 and 199-231, reports/E.31_RETURN.md heading lines only, the listing of
  reports/stage_e32_briefs/work/X1_exposure/, reports/stage_e32_briefs/protocol/p7_final_budget300.md line 44. No market
  data, no registry call (the regexes were tested on strings only), no edits outside this file and the work folder.

## 1. Per-hunk table

Verdicts: CORRECT = resolves the finding as stated or by the lead's stated choice and introduces no error; the rest
as the brief defines. "Evidence" quotes v0.5.

| # | v0.5 lines | Finding IDs | Verdict | Evidence (verbatim) | Proposed fix |
|---|---|---|---|---|---|
| 1 | 3 | none (status line) | UNTAGGED-OK | "DRAFT v0.5 (2026-10-27, lead Opus 5.5 xhigh; ProtocolReviewer, FixVerifier and FixSpotCheck findings applied)" | none |
| 2 | 37-40 | S-A-3, S-A-4 | CORRECT (one NOTE) | "and before the B7 freeze (a reading added between the freeze and C1 re-takes the freeze list, first bullet); that file's sha256 is a line of the B7 pipeline freeze list, is quoted in reports/stage_e33_run_marker.md (the prompt's C1) and is carried in the freeze file of P7.1". Matches both proposals; the prompt's C1 (line 148) does write reports/stage_e33_run_marker.md. NOTE: P7.1 684-685 lists the freeze file's fields ("the set, label, h, model, hyperparameters, pipeline sha256 and protocol sha256") and the readings sha256 is not among them. | F-5 |
| 3 | 71-72 | S-A-5 (no tag on the hunk) | UNTAGGED-OK | v0.4 `"as of` / `u" means the last book update ... of its` / `F_LAST record`; v0.5 `"as of u" means the last book update with ts_recv <= u (ProtocolReview DO-9). A book update's time is the ts_recv` / `of its F_LAST record (FixVerifier R-W2-6).` Word for word the same; the term is now on one line (grep "as of u" hits 71). | none (a "(FixSpotCheck S-A-5)" tag is a convention, not a protocol matter) |
| 4 | 103-105 | S-A-6 | CORRECT | "readable, except, for E.33's workers, the section and the files named in the third bullet (FixSpotCheck S-A-6)". The third bullet of P1.2 is "Not opened by E.33's workers" (117). "the files" instead of the proposal's "the three files" is right, since hunk 5 widened the list. | none |
| 5 | 119-124 | S-A-1, S-A-7 | CORRECT | "(lines 175-213 are never read, by grep or otherwise; a grep hit inside them is discarded; the rest of the file is read by grep) ... and every file under reports/stage_e32_briefs/work/X1_exposure/ ... The aggregate E.31 figures quoted in this protocol (P1.3, P1.5) and in the reader files M2, M3, M6, R3b and R4 are not closed". Checked: E.31_RETURN.md has "### 3.5 Part 5: the measurement" at 175 and "## 4. Delegation record" at 214, so 175-213 is the section; the folder holds 12 files (X1_part1..3e, X1_frag_gate0.md, X1_ledger_summary.py/.txt, X1_tableC_appendix.md, X1_tableC_copy.py), all closed by "every file under"; this is the lead's S-A-1 option as the STATE entry states it. | none |
| 6 | 269-270 | S-A-8 | CORRECT | "the exit is marked at the last valid touch on that side before it emptied or the book was marked bad, and flagged (FixSpotCheck S-A-8)". Matches the trigger at 264: "if the needed side is empty, or the book is marked bad, at u + L". | none |
| 7 | 337-339 | S-A-9 | CORRECT | "(a single as-of pass over the Z4 files in ts_recv order, state carried across files and dates; ProtocolReview LE-2, FE-8; FixSpotCheck S-A-9)". Verbatim the proposal. | none |
| 8 | 489-495 | S-B-1 (lead's choice: E33A, N rises) | PARTIAL | "the thresholds are recomputed at that N, P8 is re-run and the test list re-hashed". Executable in the registry (E33A is a valid label; a second label is accepted), but P7.1 687-689, P7.2 715-716, P8 739 and P9 795 still pin N to the E33 registration; the affected set and P8's input after the re-run are not defined; the E33A registration's freeze file is not mentioned. See section 2.1. | F-1, F-2 |
| 9 | 524-525 | S-B-4 | CORRECT | "and selection alone 0.914 (the P7.2 table)". p7_final_budget300.md line 44: "| 0.25 | 0.914 | 0.993 | 0.908 |". | none |
| 10 | 584-586 | S-B-5 | CORRECT (wording NOTE) | "(1.5-9 hours of wall time at 7 single-thread processes, a rough figure under the thread rule above; FixSpotCheck" / "S-B-5), 6-10" / "CPU-hours at the FeasibilityReviewer's balanced probes". Words as proposed; the wrap leaves "S-B-5), 6-10" alone on line 586. | F-8 |
| 11 | 596-598 | S-B-3 | CORRECT (one NOTE) | "The measured wall time compared with it is the sum of the feature build's wall time (from its first to its last DONE marker, whenever it was built) and the 1,800 fits' wall time (from the first real-outcome fit to the last DONE marker), the same two parts as the projection". Verbatim the proposal. NOTE: read literally, a usage-limit wait or reboot between the first fit and the last DONE marker counts as wall time and can fire the 3x stop on a healthy search; the prompt (lines 41-42) expects such pauses. | F-7 |
| 12 | 721-723 | S-B-6 | CORRECT | "needs 0.217 and passes with about 0.83, and" / "beside 0.10 it needs 0.297 and passes with about 0.09 (FixSpotCheck S-B-6)". As proposed (SpotCheck_B recomputed 0.2167/0.833 and 0.2974/0.085). | none |
| 13 | 790-792 | S-B-7 (lead's choice: counts derived from the saved sources, none written) | CORRECT (one NOTE) | "and, for the four other P3.6 rule-3 report types, the counts it derives from the saved sources, recorded and hashed with the calendar before the read; it stops on any other count". Executable and outcome-neutral. NOTE: if the same build derives the counts and the calendar from the same sources, the assertion is an integrity check of the hashed calendar, not an independent count. | F-6 |
| 14 | 824-827 | S-B-2 (deadline paraphrase) | CORRECT | "if the full budget cannot finish by 07:00 PDT on 2026-10-28, whole families are finished (C3); work stops at 08:00; the return is written by 08:45; nothing runs after 09:00". Prompt 44-46: "work stops at 08:00 PDT on 2026-10-28; the return is written by 08:45; nothing runs after 09:00"; C3 161-163: "If the full budget cannot finish by 07:00 PDT on 2026-10-28, finish whole families". The old paraphrase ("no new configuration starts after 07:00", "recorded as failed") is gone (grep: 0 hits). | none |
| 15 | 828-833 | S-B-2 (lead's choice: start gate 07:00, whole-set drop at 08:00) | PARTIAL | "a set is started only if the P5 projection, updated with the measured times, says it finishes by 07:00; a started set runs to completion; a set still running at 08:00 is stopped and all its configurations are recorded as unrun, so P8 sees whole sets only". Matches the STATE entry's choice. "the P5 projection, updated with the measured times" names no statistic (P5's formula is for the whole search); "recorded as unrun" misreports configurations that did finish inside a stopped set. See section 2.2. | F-3, F-4 |

Counts: CORRECT 11 (hunks 2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14), PARTIAL 2 (hunks 8, 15), UNTAGGED-OK 2 (hunks 1, 3),
WRONG 0, UNTAGGED-ERROR 0.

## 2. The two new lead texts

### 2.1 S-B-1 (v0.5 489-495): LT7's second run after the test list is hashed

What the text says: at each time t the fold model is the one whose OOF block holds t's date; a first-run mismatch is
fixed under 0.2 with the pipeline hash re-taken before the first real-outcome fit; a second-run mismatch is "a bug found
after the pipeline freeze: E.33 stops the test list, reports the mismatch, and follows its prompt's B7 rule (a logged
amendment; every configuration whose OOF series the fix changes is re-run under a new ID registered under test "E33A",
so N rises by their number; the thresholds are recomputed at that N, P8 is re-run and the test list re-hashed)".

Checks.
- Prompt B7 (134-136): "A bug found later is fixed only by a logged amendment, with every affected configuration re-run
  and counted." Prompt 232-234: "change ... the pipeline after its freeze, except by a logged amendment with every
  affected configuration re-run and counted." The text follows the rule and takes "counted" as "added to N", the stricter
  reading (a larger N tightens G3, G4 and b_test). Consistent.
- Registry (screening/trial_registry.py). `_TEST = [A-Z][A-Za-z0-9]{0,15}`: "E33A" fullmatches (tested). `_ID =
  [A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}` and `t.startswith(f"{test}-")`: ids must read E33A-<suffix>; "E33A-S5F15L010A"
  fullmatches (tested). register() refuses only `set(ids) & taken or any(e["test"] == test ...)` (219-221), so a second
  registration under a different label with fresh ids is accepted, and the entry_id becomes r00X-E33A. register() also
  requires `freeze` and `freeze_sha256` (`_freeze_record` checks the file hashes to the given value) and the harness
  preflight. So the path is executable, provided E.33 writes a freeze file for the E33A ids; the text does not say so, and
  P7.1's freeze file lists E33-... ids with the pre-fix pipeline sha256 (684-685). Reusing it would record the wrong
  pipeline hash (the registry does not check the file's contents). F-2 adds the sentence.
- Fold-model rule: the OOF blocks partition the 796 dates (SpotCheck_B: blocks 133x4, 132x2; fold 6 trains on 664 =
  796 - 132, so the embargo is cut from training, not from the block). Every LT1 time has exactly one fold model. Well
  defined.
- First-run clause against 0.2 bullet 1 ("the frozen pipeline hash is re-taken before the first real outcome"):
  consistent.
- P7.1 and P10: P7.1 686-687 "The registry refuses a second registration under E33" stays true (E33A is another
  label). P10 "No result stops, shortens or extends the search" (816-817) is not breached: the re-run is forced by a
  mismatch, not by a result.
- Contradictions found (F-1). The text says "the thresholds are recomputed at that N" (the raised N), but four lines
  still pin N to the E33 registration: P7.1 687-689 "The N of every DSR, threshold and test in P7.2, P8 and P9 is
  trial_registry.current_n() immediately after that registration: 838 if no other stage registers first"; P7.2 715-716
  "After the registration b_test does not change (ProtocolReview DO-2). If the registered N differs from 838, p7_final.py
  recomputes every threshold at that N before any real-outcome fit" (the E33A recompute happens after real-outcome fits);
  P8 G3 739 "at N = the registered N after E.33's registration"; P9 795 "(= the N of P7.1, 838, unless trials were
  registered after E.33". An implementer on the E33A path can take N = 838 (P7.1, P7.2, P8, P9 literal) or N = 838 + k
  (LT7); the two give different G3, G4 and b_test. The verdict number N is therefore defined two ways. SHOULD FIX by the
  brief's definition (the ambiguity exists only on the E33A path, but on that path it enters every gate).
- Undefined pieces (F-2). (i) "every configuration whose OOF series the fix changes": by code analysis or by re-running
  all 300 and comparing? The two can give different affected sets, hence different N. A simulator fix (LT7 tests the
  entry decision and the fill) leaves the fits untouched, so re-running the P3.8 simulation for all 300 and comparing
  series is cheap and mechanical. (ii) "P8 is re-run": on which 300 series? P8's input (730) is "the 300 OOF series"; the
  text does not say that an affected configuration's registered (buggy) series is withdrawn and its E33A series used.
  Left both in the pool, a buggy series stays selectable. (iii) "a logged amendment": the prompt's B7 pipeline amendment,
  not a protocol amendment under 0.2 bullet 2 ("decided by the user"); say so and say where it is logged (0.2 bullet 1's
  form: the protocol line the fix restores).
- Can an outcome steer a choice? The re-run is triggered by a mismatch, its scope by the fix, and the fix is bound to
  "the code does what this text says" (0.2 bullet 1) and logged with the restored line. With F-2's mechanical
  determination of the affected set and the withdrawal of superseded series, no outcome-dependent choice remains. Without
  it, the affected set is a judgment made after the test list is known.

### 2.2 S-B-2 (v0.5 824-833): deadlines and the cut rule

What the text says: the prompt's times (07:00 cut, 08:00 stop, 08:45 return, 09:00 nothing runs) as feasibility
limits; "a set is started only if the P5 projection, updated with the measured times, says it finishes by 07:00; a
started set runs to completion; a set still running at 08:00 is stopped and all its configurations are recorded as
unrun, so P8 sees whole sets only".

Checks.
- Against the prompt. Lines 40-50: "work stops at 08:00 PDT on 2026-10-28; the return is written by 08:45; nothing
  runs after 09:00. Quality comes first. If time runs short, finish whole parts and report what did not run." C3 161-163:
  "If the full budget cannot finish by 07:00 PDT on 2026-10-28, finish whole families. Record which ran; unrun
  configurations stay registered and count in N". The paraphrase at 824-827 is faithful. The cut rule is one admissible
  reading of "finish whole families" (SpotCheck_B left the 07:00-versus-08:00 choice to the lead; the STATE entry records
  07:00). The three clauses are mutually consistent: "runs to completion" is qualified by the 08:00 stop, and the 08:00
  stop precedes "nothing runs after 09:00".
- Against P5. Run order 606-607 "S5, S1, S3, S2, S4; inside a set, FH15, FH30, FH05, FH60, TB15, TB30; inside a label,
  the P7.1 grid order. Unrun configurations stay registered and count in N" agrees. The projection (587-595) is for the
  whole search: "796 x the mean per-date builder seconds / P_b + 1,080 x the L100E fold seconds / P_L + 720 x the G3050
  fold seconds / P_G". A per-set projection (one set = 60 configurations x 6 folds = 216 LOGIT + 144 LGBM fits) is not
  written, and "updated with the measured times" names no statistic (mean, median or maximum of the finished fits; of
  the same family or of all). Two careful implementers can project the same set to end before or after 07:00, so the
  set of configurations P8 sees differs (F-3). The decision is made at a moment when the finished sets' results are
  known; a fixed statistic removes the only lever an outcome could pull.
- "recorded as unrun" (831): a set stopped at 08:00 may hold configurations that finished with DONE markers and OOF
  series on disk. Recording them as unrun contradicts the prompt's "Record which ran" and P5's DONE-marker bookkeeping;
  the P8 effect (excluded with their set) is the lead's choice and is fine, the record is not (F-4). P5's "failed" (an
  error, fails G1) is a different class and is not confused here.
- Executable as written: yes, apart from the unspecified statistic. Steering: only through the statistic (F-3). Other
  contradictions: none found; 3x stop (821-823) uses the whole-search projection and is unaffected by a cut.

## 3. Protocol-wide consistency (grep of v0.5)

| Term | Hits | Result |
|---|---|---|
| 0.217 / 0.83 | 721 (0.83 also at 631, the unrelated null band "0.13-0.83") | consistent; 0.216 and 0.84: 0 hits |
| 0.297 / 0.09 | 722 | consistent; 0.296: 0 hits |
| 0.914 | 524; table file line 44 "0.25 | 0.914" | consistent; "about 0.92": 0 hits |
| E33A | 494 only | the only mention; P7.1 687-689, P7.2 715-716, P8 739 and P9 795 still describe a single E33 registration (F-1) |
| run_marker | 39 only; prompt C1 148 defines reports/stage_e33_run_marker.md | consistent; "C1 registration note": 0 hits |
| X1_exposure | 120-121 only | consistent with the folder listing |
| "as of u" | 71 (defined), 262 ("as of u + L") | consistent; no split term remains |
| readings file (reports/stage_e33_protocol_readings.md) | 36 (named), 37-40 ("that file") | consistent; its sha256 is said to be "carried in the freeze file of P7.1" but P7.1 684-685 does not list it (F-5) |
| old wording | "per-date as-of", "at 7 processes", "recorded as failed", "no new configuration": 0 hits each | removed everywhere |
| unrun | 831 (also 606, 832 unchanged) | see F-4 |

## 4. Problems

| ID | Severity | v0.5 lines | Problem | Proposed fix (replacement text) |
|---|---|---|---|---|
| F-1 | SHOULD FIX | 489-495 with 687-689, 715-716, 739, 795 | On the E33A path the N of every threshold is defined two ways: LT7 says "recomputed at that N" (the raised N); P7.1 pins N to "immediately after that registration" (E33, 838); P7.2 says "After the registration b_test does not change" and allows a recompute only "before any real-outcome fit"; P8 G3 says "after E.33's registration"; P9 says "the N of P7.1, 838". G3, G4 and b_test differ between the readings. | 687-689: "The N of every DSR, threshold and test in P7.2, P8 and P9 is trial_registry.current_n() immediately after E.33's last registration: the E33 registration (838 if no other stage registers first; ProtocolReview DO-4, AR-3), or the E33A registration of P4.1 LT7 when one is made (838 plus the E33A count)." 715-716: "After the E33 registration b_test changes only with an E33A registration (P4.1 LT7), when p7_final.py recomputes every threshold at the new N before P8 is re-run (ProtocolReview DO-2). If the registered N differs from 838 at the E33 registration, p7_final.py recomputes every threshold at that N before any real-outcome fit." 739: "at N = the registered N of P7.1 (after E.33's last registration)". 795: "(= the N of P7.1: 838, or 838 plus the E33A count, unless trials were registered after E.33, ...". |
| F-2 | SHOULD FIX | 491-495 | "every configuration whose OOF series the fix changes" has no determination rule (analysis versus re-run and compare: different affected sets, different N); "P8 is re-run" does not withdraw the superseded series from P8's 300 inputs (a buggy series stays selectable); the E33A registration needs its own freeze file (register() requires one; P7.1's carries the pre-fix pipeline sha256); "a logged amendment" is not placed (prompt B7 sense, logged where). | Replace from "A mismatch at the second run" (491) to "(FixSpotCheck S-B-1, lead's choice)." (495) with: "A mismatch at the second run is a bug found after the pipeline freeze: E.33 stops the test list, reports the mismatch, and follows its prompt's B7 rule, a logged pipeline amendment (the fix is logged in the STATE file with the protocol line it restores, as in 0.2's first bullet; it is not a protocol amendment under 0.2). The fixed pipeline is hashed; the P3.8 simulation, and any fit the fix touches, is re-run for all 300 configurations; the affected set is every configuration whose OOF daily series differs from its registered series at G7's tolerance. The affected configurations are registered in one register call under test "E33A" as E33A-<set><label><grid>, with a new freeze file of the P7.1 form listing those IDs and the amended pipeline sha256, so N rises by their number (P7.1); p7_final.py recomputes the thresholds at that N; P8 is re-run on the 300 series with each affected configuration's registered series replaced by its E33A series (the superseded series is reported, never selectable); the test list is re-hashed and P6.4 and P6.5 are re-run on it (FixSpotCheck S-B-1, lead's choice)." |
| F-3 | SHOULD FIX | 829-831 | "the P5 projection, updated with the measured times, says it finishes by 07:00": P5's formula projects the whole search and no statistic is named for the update; two careful implementers can start or skip the same set, and the decision is taken when the finished sets' results are known. | Replace "a set is started only if the P5 projection, updated with the measured times, says it finishes by 07:00;" with "a set is started only if its projected wall time, 216 x the mean measured wall seconds of the LOGIT fits finished so far in this run / P_L + 144 x the same for the LGBM fits / P_G (the P5 probe seconds in place of a mean that does not exist yet; P_L and P_G the process counts in use), written to the STATE file with the clock time before the decision, ends by 07:00;" |
| F-4 | NOTE | 831 | "all its configurations are recorded as unrun": configurations that finished (DONE marker, OOF series on disk) inside a set stopped at 08:00 would be recorded as unrun, against the prompt's "Record which ran" (C3) and P5's DONE-marker bookkeeping. The P8 effect (whole-set exclusion) is unchanged. | "all its configurations are excluded from P8 as a set and recorded as not evaluated (the finished ones' series stay on disk and the return lists them as run but not evaluated, the rest as unrun), so P8 sees whole sets only" |
| F-5 | NOTE | 39 with 684-685 | 0.2 says the readings file's sha256 "is carried in the freeze file of P7.1", but P7.1 lists the freeze file's fields without it. | 684-685, after "pipeline sha256 and protocol sha256": "and, once for the file, the sha256 of reports/stage_e33_protocol_readings.md (0.2)". |
| F-6 | NOTE | 790-791 | "the counts it derives from the saved sources": if the same build derives the counts and the calendar from the same sources, the assertion checks the hashed calendar against itself (an integrity check, not an independent count). Outcome-neutral. | "the counts a worker other than the calendar builder derives by hand from the saved source pages" |
| F-7 | NOTE | 596-598 | The measured wall time "from the first real-outcome fit to the last DONE marker" includes usage-limit waits and reboots, which the prompt (41-42) expects; a long pause could fire the 3x stop (821-823) on a healthy search. Feasibility only. | After "(from the first real-outcome fit to the last DONE marker)": ", each net of the pauses the STATE file logs (usage-limit waits, reboots)". |
| F-8 | NOTE | 584-586 | Wrapping: "S-B-5), 6-10" stands alone on line 586. Words are right. | Rewrap lines 584-587 so the parenthesis closes on the line it opens or the next. |

Nothing BLOCKING. No leak and no sealed-data path is opened by any hunk; hunk 5 only widens the worker firewall.

## 5. Not done or not verified

- The fold-block partition (every OOF date in exactly one block) is taken from SpotCheck_B's fold arithmetic, not
  recomputed here.
- SpotCheck_B's recomputations behind 0.217/0.83, 0.297/0.09 and 0.914 were not repeated; the table file's 0.914 was
  read directly.
- P1.3 and P1.5 were not reread to confirm which E.31 aggregates they quote (hunk 5's "not closed" clause can only widen
  what is readable, so no verdict depends on it).
