# PipelineReview (Stage E.33 B7, PipelineReviewer-FableXHigh)

Reviewer: PipelineReviewer-FableXHigh (fresh context; wrote none of this code; the session identifies itself as
claude-fable-5-1; the lead confirms the model from the transcript). Started 2026-10-28 03:08 PDT, written as I went;
times from `date`. Line numbers are against the files as of 03:08-03:20 PDT (feat33.py mtime 02:51, lab33.py 02:46,
search33.py 02:21, run_search33.py 02:22, select33.py 02:35, synth33.py 02:02, run_proofs33.py 02:33, cost33.py
15:25 (10-27), cal33.py 15:01, data33.py 14:57, guard33.py 14:53, split33.py 14:57; implB featB/dayB/replayB 02:45).

Standard: reports/stage_e32_discovery_protocol.md FROZEN v1.0 (sha256 c4ffb9d7...; every P-line cited below is from
it), docs/prompts/STAGE_E.33.md Part B, reports/stage_e33_briefs/INTERFACE.md, and the lead's draft
reports/stage_e33_protocol_readings.md (R-L1..R-L8, the B3 rulings of 02:47). Prior reviews read and not repeated:
review/SearchReview.md (0 BLOCKING / 4 SF / 10 NOTE), review/ProofReview.md (0 / 2 / 11), review/MathReview.md
(0 / 1 / 6). Whether their SHOULD FIX items are fixed is recorded in "Checked and found correct".

INTERFACE rule 1 and R-L2: no statistic of any label or outcome on real data appears here; every real-data check
below is a count, a hash or an equality.

Status: the session was cut by a usage limit at about 03:25 PDT and resumed at 07:02 PDT (lead's message); this
file was finalised 07:02-07:15 PDT from the review as it stood. The lead says the pipeline will not be frozen in
this stage; the review feeds the continuation stage. At 07:02 every code file I read was byte-identical to the
version read (feat33.py 66b4e251dce9..., search33.py a7d30b2a6786..., select33.py 9b9928066a35..., featB.py
33269b3a4b4e..., dayB.py 150d3c6c8dee..., replayB.py c20eab0a2df6...; lab33.py read at mtime 02:46, sha256 at
07:02 025bdedff858..., the lead confirms it is the same version).

## Verdict

NOT YET (provisional). Nothing I reviewed is BLOCKING, and every module I read implements the protocol's declared
choices; but the pipeline cannot be frozen until the items below are closed, and the last of them is a measured
disagreement, not a reading of mine:

1. B3 is not yet passed on the ruled feature code. The partial rerun feat_r2_partial (TestCoder, 03:18; Coder-A
   store 6873427a6150 = feat33 66b4e251dce9 on 10 of the 20 dates, against Coder-B 7d28f22509b4) has 58 of 59
   columns agreeing on every one of 2,730 rows (the whole OFI family, C_5, F1, F2, F3.9, F3.10, F3.12, F4, the flags,
   sigma_ZM/ZS/ZL); F3_11 disagrees on 2,690 rows. The cause is the one residual divergence I had found by reading
   before the rerun landed (SF3 below, the TestCoder's FD6): it needs a lead ruling, a fix in one side, and the full
   20-date rerun at 0 cells. Labels already agree exactly (lab_r3: 0 cells, 46,886 rows; LT2 0 violations).
2. SF1 (the readings file) and SF2 (the freeze list) are done before the freeze hash is taken.
3. N10 (replayB's D1 order) is fixed on B's side before the final synthetic feature run, or the lead accepts the
   zero-effect divergence in writing.
When 1-3 are closed with no other change to the files I read, my verdict on the reviewed modules is GO; any change
to a file I read re-opens this review for that diff only. What I did not reach is listed at the end.

Counts: BLOCKING 0, SHOULD FIX 3, NOTE 10.

## Findings

### BLOCKING

None. I found no departure from a declared choice (P0.2) in the code I read, no path by which a record with
ts_recv > t reaches a feature, a decision or a label, no training row from an evaluation block or its embargo, and
no error swallowed on a path that produces an outcome.

### SHOULD FIX

SF1. The readings file is not yet the file P0.2 freezes. reports/stage_e33_protocol_readings.md line 113 still
reads "(to be filled from reports/stage_e33_briefs/work/*_readings.md and implB/*_readings.md)"; the file holds
R-L1..R-L8 and the B3 rulings only.
- Protocol: P0.2 lines 35-40: "Every such reading is written by E.33's lead, before the C1 registration, into
  reports/stage_e33_protocol_readings.md ... and before the B7 freeze ...; that file's sha256 is a line of the B7
  pipeline freeze list ... No reading is made after C1: a question that arises later is answered by that file, and
  if it is not answered there, that part of E.33 stops and reports."
- Failure scenario: the freeze list hashes a file that answers almost none of the outcome-relevant readings the
  code embodies; after C1 the first such question (say, "which 10 dates does F1.3 fit on?") finds no entry, and
  by P0.2 that part stops, or someone answers it from memory and the reading changes silently.
- Readings that can affect an outcome and are not yet in the file (my view on each is in "Readings" below):
  FA-1 = B-OPEN-1 (open-time junction at 07:45, the 08:30 state never sampled), FA-3 (composites from the
  unclipped quantities), FA-5 = B-MISS-1 (every sample point required), FA-7, FA-9 = B-SEAS-1, FA-10 = B-SW-1,
  FA-12/13 = B-LAM-1/2, FA-14 = B-RP-1, FA-15 = B-SIG-1, FA-16 = B-REF-1, FA-17/18 = B-F13-DATES/REL, FA-19,
  FA-20 = B-GAP-1, FA-21, FA-22 = B-VOL-1, FA-24 = B-C34, FA-25 = B-F49, FA-31, FA-32, B-WIN-1, B-MBP-BAD = FA-4,
  B-OFI-2; TB-SPAN = LB-2, LOCKED-LITERAL = LB-17, TB-M0 = LB-7, ENTRY-WINDOW = LB-4, TB-TIE = LB-9, W-SUM = LB-18,
  REPLAY-END; S1, S2, S3, S5, S6, S18, S20; Q1, Q2, Q4, Q5, Q6, Q8, Q10, Q11 (R-L8 carries Q3 and Q9 only);
  C1-C7; CAL-1 = B-C7, CAL-4, CAL-5, CAL-6 = B-C10; T-4, T-5, T-6, T-8, T-9, T-10, T-11.
- Fix: one entry per reading (where A and B chose the same, one entry naming both IDs), with the lead's agree /
  disagree; then hash the file and put the hash in the freeze list (P0.2, P7.1).

SF2. The freeze list must cover code the pipeline executes outside pipeline/ and implB/, which no in-pipeline hash
covers. search33.pipeline_files() (search33.py:83-99) and run_proofs33.pipeline_closure() (run_proofs33.py:67-86)
walk imports inside pipeline/ only; the feature code_sha12 (build_features33.py:46-66, FA-28) adds mbo_book31.py.
Not covered by any marker: screening/stage_e_verdict.py (moments, t_stat, pbo: search33.py:31, select33.py:36-37),
funnel/multiple_comparisons.py (deflated_sharpe_ratio: select33.py:35), reports/stage_e32_briefs/protocol/
p7_final.py and p7_thresholds.py (select33.b_test_at; in the proof manifest only), the E.31 library modules
cal33/data33 import (measure31.py, measure31_core.py, mbo_book31.py), the program calendars under data/, and the
two release CSVs (sha-pinned in guard33.REFERENCE_FILES, guard33.py:64-69, so these are covered).
- Protocol: prompt B7 "a sha256 list of every code file, config and environment lock (uv.lock)"; P7.1 "pipeline
  sha256"; P5 "uv.lock is hashed".
- Failure scenario: harness v14 pins screening/ and funnel/, but the E.31 pilot modules and p7_*.py are ordinary
  files; an edit to measure31.day_bounds or p7_final.required_sharpe after the freeze changes every label window
  or b_test without any marker noticing.
- Fix: list those files with their sha256 in the freeze file beside the pipeline files, uv.lock (sha256
  7fecbfa47327..., equal to the proof manifest's) and the protocol sha.

SF3. F3.11 refill window at a record that removes fill lots and non-fill lots at once (the TestCoder's FD6; I found
the same divergence by reading before feat_r2_partial measured it). feat33.py:493-513 (_removal returns the
(side, price) that opens a window only when `rest == 0`, i.e. the record's whole reduction is attributed to fill
lots of the same batch, and the caller at 444-445 checks the level is then empty); replayB.py:140-154 (`reduce`
opens the window when `fill > 0`, i.e. any fill lots, and the level reaches 0 after the record; the non-fill
remainder is also counted as a removal at 149-152, as A does at 511-512).
- Protocol: F3.11 "a refill is an add at the same price and side within 100 ms (ts_recv) after that price level,
  while it was the touch, reached 0 displayed quantity through trades"; the lead's ruling R-B3-FD4 (b): "a level
  whose last lots are cancelled does not". Neither text settles a single record that removes both kinds of lot
  (an order partially filled, then a C or M for its whole remaining size in the same batch).
- Measured effect (feat_r2_partial): rbar_15 differs on every date, so F3_11 differs on 2,690 of 2,730 rows; no
  other column is touched.
- Failure scenario: without a ruling, whichever side "wins" the rerun sets a feature definition by accident, and
  the readings file cannot answer the question after C1 (P0.2).
- Fix: the lead rules (my view, for the lead: A's reading is the literal one, "through trades" meaning the lots
  that emptied the level were all filled lots; B's counts a level emptied partly by a cancel; neither direction is
  the conservative one for the outcome, so the literal reading governs), the other side changes, the 20-date rerun
  is repeated to 0 cells, and the entry goes into the readings file.

### NOTE

N1. Pending P4.1 items are correctly sequenced after the freeze, and the STATE file should say so. LT1 (200 draws on
the full store of the frozen feature code), LT2 on the final label store, and LT7 (now runnable: seed 1's fold
models exist under DERIVED/proofs/seed1/) are "before any model is fitted on real outcomes" (P4.1), not before the
freeze; a mismatch "stops E.33 until the code is fixed under 0.2 (the pipeline hash re-taken before the first
real-outcome fit)". P10 allows the features-only store before the freeze, "rebuilt if the frozen feature code
differs". So: freeze -> full feature store under the frozen sha -> LT1 (T-5: prior=recompute, or
prior=production plus a recompute subset; the lead's choice, to be logged) -> labels -> LT2 -> LT7 -> C1.

N2. S3 (search33.py:641-646): an entry that is not made (flag 16/32) does not count toward the 20-entry cap and the
next minute is decided. Literal ("entries"), and the flags were 0 on the 20 B3 dates (B3_agreement.md), so the
effect is negligible; log it (SF1). A stricter reading (count attempts) would be equally defensible.

N3. The LabelCoder's data finding (LabelCoder_readings.md 72-81): on 2021-07-01 the definition record's limit band
(HL 384.9 from the record with ts_recv <= 08:30 CT) lies below the traded price, so rule 5's limit part removes
every minute of every label on that date. The rule is implemented as P3.6 rule 5 writes it (FixSpotCheck S-A-9);
P0.2 forbids changing it. P3.6's last line requires the per-rule removal counts to be reported, which
build_labels33's _excl files hold. Suggest the lead records this in the readings file as a data note (not a
reading) so the test stage knows the band can be stale.

N4. The per-date limit-band test in lab33 is exact integer arithmetic (lab33.py:387-393): 100 (bid + ask) tick-fixed
>= 198 HL - 2 LL and <= 202 LL + 2 HL. I re-derived both inequalities from M >= HL - 0.02 c, c = (HL + LL)/2 and
M <= LL + 0.02 c: correct.

N5. lab33's FH entry fallback window ends strictly before t + h (planned_exit_ns, lab33.py:433-437, ENTRY-WINDOW),
TB's before t + L + h. P3.2 says "before its planned exit time" without naming it for FH; t + h is the exit
decision (P3.8 "FH at t + h"). Conservative (fewer fallback entries); B agrees (LB-4); log it (SF1).

N6. On the TB row rule, lab33 checks the locked-book condition over [t, max(t + L + h, tau + L)] (TB-SPAN (c),
lab33.py:612-615) and the release/close rules over [t, t + L + h] only. I checked that the union cannot cross a
release edge or 13:13 where the possible span does not: t and h are whole minutes, R - 2 min, R + 30 min, 08:35 and
13:13 are minute marks, and tau + L <= t + h + 2 s, so a span that clears a minute-mark edge by >= 58 s cannot be
caught by the extra <= 1 s. span_violations (lab33.py:773-794, LT2) re-checks the union anyway.

N7. search33 fails a fit only on FitError (search33.py:872-883) and converts sklearn ValueError/ArithmeticError/
LinAlgError inside est.fit (439-445) and LightGBMError other than bad_alloc (451-460) into FitError; bad_alloc
becomes MemoryError. A ValueError raised by sklearn for a reason that is not numerical (a malformed argument) would
also be a "failed fit" rather than a stop; with the fixed grid and the tested spellings (test_search33: 36 tests)
that path cannot arise in production, so this is a note, not a fix.

N8. Two readings the proof design rests on are sound but worth stating in the return: the planted proof's pass
event is per seed (R-L4 (a)); the first planted seed (101) shows two S5F15 LOGIT configurations in Tier A at best
SR_d 0.3531 against an oracle 0.3286 (B5_proofs.md), consistent with ProofReview N3 (the oracle is an anchor, not
a ceiling). The null seed 1 has an empty Tier A, 0 failed fits (ProofReview SF1's failed column is in the summary).
Design judged only; the 38 remaining seeds run after this review.

N9. The two implementations agree on every label column exactly (B3 lab_r3, 0 cells) with A's TB barrier read
from A's own sigma_ZM(D) (features/c22b0a50f4cd/_day), and sigma_ZM/ZS/ZL agree A = B on all 20 dates. The
production label build after the freeze must point --features-sha at the frozen feature store's _day
(build_labels33.py:254-262 refuses TB without it, and the DONE markers carry sigma_source, 126-137): the lead
should confirm sigma_ZM(D) of the frozen store equals c22b0a50f4cd's on the 20 dates (FD1-FD5 change window
counters, not the wall-minute mids sigma pools, so equality is expected; FA-31). feat_r2_partial already shows
sigma_ZM/ZS/ZL equal A = B on the 10 rebuilt dates.

N10. Coder-B's feature replay applies the bad-book mark before the R's clear: replayB.py:162-166 marks the book bad
on any record carrying F_MAYBE_BAD_BOOK (or F_TOB/F_MBP), then 175-176 runs `book.clear()` for an R, and
mbo_book31.Book.clear (mbo_book31.py:123-130) sets `bad = False`. So an R record that carries the flag leaves B's
feature book GOOD, which is the pre-ruling Coder-A behaviour, against R-B3-D1 ("the book stays bad until the next
R"); feat33.py:416-420 and lab33.py:305-313 (and B's own label replay, labB_book) clear first and then mark.
- Protocol: 0.3 "not marked bad (F_MAYBE_BAD_BOOK)"; the lead's ruling R-B3-D1.
- Effect on real data: none (tests_b3/count_d1.py: 0 R records carry the flag on all 816 dates; all 5,417 flagged
  records precede the date's first R). Effect on the B4 synthetic feature run: its date 11 plants exactly this
  case, so the final synthetic run on the ruled code would show A != B there for every ZM-book feature after 11:57
  for the wrong reason.
- Fix (B's side, one line): mark bad after the clear for an R record, as feat33 does.

## Readings (my view on each; the lead decides)

Lead readings R-L1..R-L8: agree with all. R-L1 (b) keeps the probe outcome-free; R-L2 (b) is what the checks need;
R-L3 (b) is sound because the proofs never execute the record-level builders, and the hash condition it adds is
met at 03:19 (all ten files of the run manifest are byte-identical to the current files; uv.lock
7fecbfa47327... equals the manifest's); R-L4 (a) is the protocol's own binomial; R-L5 reproduced by the TestCoder;
R-L6 is P9; R-L7 is the declared metric made deterministic (SearchReview probe 1: 1.6e-10, same stopping
iteration); R-L8 "continue" is the literal reading and ProofReview's analysis of its conservativeness holds.

B3 rulings R-B3-FD1/FD2 (actual session), FD3a (d), FD3b (a), FD3c (literal), FD4 (b), FD5 (b), D1 (B), D2 (B),
D3-D5: agree with every one, and each is the reading the text supports or the stricter one. I read the fix sites:
feat33.py:60-69, 161-189 (FD1/FD2 axis), 352, 457-470 (FD3a, no term for the first update of an interval, bad
count only inside), 251-263 and 597-601 (FD3b/c), 439-445 and 493-534 (FD4 refill window opens only when the
emptying record's whole reduction is fill lots and the level is then empty), 455 (FD5 clear at F_LAST), 405-420
(D1 clear-then-mark); lab33.py:308-313 (D1), 413-417 (D2); dayB.py:53-101 (FD3a/b/c on B's side, ofi_included
and OfiWindows). The two sides implement the same rule in each case as far as reading shows; equality is condition
1 of the verdict.

Coder readings (agree unless stated; "log" = carry into the readings file, SF1):
- FA-1 = B-OPEN-1 (axis junction 07:45; the 08:30:00 pre-open state is never a sample point): agree; the
  alternative samples a book the protocol says to skip, and MathReview's hand marks match. Log.
- FA-2 (D-1 = calendar day): agree, no value depends on it.
- FA-3 (composites from unclipped zC30, gC, GAP, DB, rOpen; clipped last): agree; the text names the quantities.
  Log.
- FA-4 = B-MBP-BAD (MBP-1 bad per batch; ZM bad until the next R): agree; 0 open-time flags measured.
- FA-5 = B-MISS-1 (a window with an undefined sample point is invalid): agree, conservative. Log.
- FA-6 (OFI terms): superseded by FD3; the implementation follows the ruling.
- FA-7 (F3.4 invalid when a side has < 5 levels at any update in the window) and FA-8 (Dbar on valid-mid minutes,
  missing level 0): agree. B-OFI-2 reads "lacks a side" at level m the same way.
- FA-9 = B-SEAS-1 (seasoned quantity on the displayed book's levels; every M resets the time): agree, literal.
- FA-10 = B-SW-1 (trade set = T records sharing one ts_event; checked at each book update; counted once per side;
  no aggressor condition): agree; causal.
- FA-11 (removals): follows FD5; agree.
- FA-12/13 = B-LAM-1/2 (any T record makes an interval "contain trades"; an interval with an undefined dM is
  excluded and not counted toward 30): agree.
- FA-14 = B-RP-1 (F4.6 over the as-of function M(u), seeded at the 08:30:00 state): agree, literal.
- FA-15 = B-SIG-1, FA-16 = B-REF-1 (pooled over the 20 dates, undefined with fewer; references over defined
  marks): agree. Log.
- FA-17/18 = B-F13-DATES/REL (the 10 trade dates before D that lie in the segment and contribute a sample, at
  least 3; a closed release window for an instant): agree; (ii) "the 10 most recent in-segment dates" would reach
  further back and is less conservative. Log.
- FA-19 (rank < 3 invalid): agree.
- FA-20 = B-GAP-1 (qualifying dates among the 20, not the 20 most recent qualifying; D's own gap invalid across a
  front change): agree. Log.
- FA-21 (F4.11 invalid if any B(e) undefined; latest e on exact ties): agree.
- FA-22 = B-VOL-1 (side-N trades count in volume; MBP-1 F records do not): agree, literal. Log.
- FA-23: follows FD4; agree.
- FA-24 = B-C34 (C.3, C.4 invalid without a defined ZM mid): agree.
- FA-25 = B-F49: agree.
- FA-26 = B-LT1-1 (cutoff mechanics; history re-streamed by default): agree; T-5's variant is identical by
  construction, and the lead's choice should be logged.
- FA-27 (E.31 book driver): agree, with D1.
- FA-28 (code_sha12 files): agree, see SF2 for the rest of the freeze list.
- FA-29 (exact crush integer): agree; B3 shows A = B within G7 on F1 columns apart from FD1/FD2 rows.
- FA-30: the FD1/FD2 ruling; agree.
- FA-31 (instant states as of the wall minute; windows on the mapped axis): agree; this is the reading that keeps
  sigma and Dbar free of 68 copies of a halt state. Log.
- FA-32 (C.1, C.9, F1.8/F4.8, F4.9, F4.13 on wall minutes): agree; differs only on excluded dates. Log.
- B-WIN-1, B-EARLYIDX, B-BOOKBAD, B-C7 = CAL-1 ((a) D < T <= E), B-C10 = CAL-6, B-SEG-1 = CAL-7, B-F15: agree.
- LabelCoder TB-SPAN (c), LOCKED-LITERAL (a), TB-M0 (a), ENTRY-WINDOW, ENTRY-FLAGS, EXIT-MARK-TIME (13:20:00),
  FILL-TIME, TB-TIE (a), TB-EXACT, TB-SIGMA (stop), W-SUM (fsum), BOOK-BAD-FLAGS, BOOK-UPDATE, REPLAY-END,
  GRID-R1R2, LIMIT-ORDER, MIDMOVE-EXCL: agree with all; LOCKED-LITERAL is the literal text and lab33 asserts
  P3.3's "both cannot be positive" (lab33.py:598-599), which a crossed book could break only if it were entered,
  and D2 forbids that. B's LB-1..LB-19 match where they overlap (B3: 0 cells).
- SearchCoder S1 (a class without a training row fails the fit), S2 (exact constant = SD 0), S3 (see N2), S4, S5
  (missing sigma stops), S6 (P6.2 quarters = G5 (a)'s), S7, S8, S9 (never guess between code versions), S10, S11
  (= R-L7), S12, S13 (revised for SF2-SF4), S14, S15, S16, S17, S18 (inner split counts training dates, excluded
  dates included: literal "training dates"), S19, S20, S21: agree with all.
- ProofCoder Q1-Q11 and the generator readings P-*: agree with ProofReview's view on each (Q3 "continue" = R-L8).
- StatsCostCoder C1 (a print stamped at the placement time is not a fill), C2 (side-N prints never fill), C3 (W
  at the exchange, cancel/convert with latency L), C4 (an exit decision before the timeout ends the window;
  (ii-b) converts to a zero-length round trip, net -spread - fee), C5 (no touch on the order's side -> not placed),
  C6 (variants share the selection variant's exit decision, P6.4 "one common signal set"), C7: agree; C4 is the
  conservative choice and C6 is P6.4's text. These run after the test list is hashed and select nothing.
- DataCoder DG-1..DG-5, DATA-1..DATA-6, CAL-1..CAL-8, G6-1/2: agree; the guard dry check refuses 4 of 4 classes
  (guard_dry_check_start.txt) and LT6 adds a test per Refused class.
- TestCoder T-1..T-12: agree; T-8 (embargo "covers" = 21 >= 21) is P6.1's own arithmetic; T-9's shift direction
  is the subtle one.

## Checked and found correct (by reading, with the small runs named)

Labels (lab33.py, all 837 lines read):
- P3.2 entry fill as of t + L at ask_1/bid_1 (440-460); fallback to the first later update with that side present
  and the book good, strictly before the planned exit, else not made with flag 16; TB entry needs M_ZM defined at
  the fill update, else flag 32 (458-459) (P3.2, FixVerifier R-W1-2).
- P3.2 exit fallback before 13:20:00, then the limit mark (LL for a long, HL for a short), then the last valid
  touch with no limits (478-503).
- P3.3 nets and class (590-601); the both-positive assertion (598-599).
- P3.4 barrier: first update in (t + L, t + L + h] with M defined (undefined mids ignored, 523), exact test
  (S - S0) >= 2b on integer tick sums (522-526), both-barrier assertion (527-528), tau = vertical when none,
  exit at tau + L (560-562, 609-620).
- P3.6 entry rules on the possible span, closed release window, limit band exact (382-420); D2 applied.
- P3.7 weights: intervals met by > 1 s (632-640; an FH span covers exactly h intervals), c_m over kept rows of the
  same label and date, u_i = mean of 1/c_m, raw (643-657).
- Grid G_h(D) = i <= 277 - h (366-368); rules 1-2 can never fire on it (checked).
- D1 clear-then-mark, D2 M_ZM(t) defined: as ruled.
- Invariants (809-837) and LT2 re-check (773-794) raise on any inconsistency; no silent drop.
- 37 tests of tests/test_lab33.py pass (my run, 03:13, in the 147 below).

Search engine (search33.py: 83-200, 261-363, 364-660, 690-997 read; run_search33.py 97-377 read):
- P6.1 folds: 133,133,133,133,132,132; embargo = the 21 dates after block k; training 642,642,642,642,643,664,
  asserted (156-179); no date before the block removed, as P6.1 says.
- P3.5 mu_k over all training rows (376-386, 557-573), EV in class order, decision with the exact-tie rule
  (608-624).
- P3.8 simulation: flat, entry_ok at t, cap 20 entries made, exit per the label table's fill times, next decision
  = first grid minute at or after the exit fill (627-656); X_D = sum of nets of trades entered on D (781).
- G5 standardisation by the training fold's weighted mean and population SD; SD 0 -> 0 (389-404); LGBM unscaled.
- P5 LOGIT spelling (424-431): saga, C, l1_ratio = rho, max_iter 2000, tol 1e-4, random_state 20261027.
- P5 LGBM (463-468, 509-554): the declared parameters; bins from the inner-train Dataset with reference= for the
  inner-validation set (519-521, DO-17); early stopping on the weighted multi_logloss of the inner block
  (R-L7); best iteration kept; calibrator (C 1e4, lbfgs, 1000, 1e-6) on the inner block with weights w, needing
  all three classes (538-546).
- P6.2 statistics from screening.stage_e_verdict moments/t_stat (31, 793-827); quarters Dec-Feb.. (696-702);
  terciles ranks 1-265/266-530/531-796 (719-726); the reported-only items never enter P8.
- SearchReview SF1 fixed: PIPELINE_SHA in every marker, check_markers refuses stale markers (901-919),
  load_fold_payload re-hashes the npz/model (921-931), tables_fingerprint compared at finalize (966-970),
  plan() refuses the whole run on any stale marker (run_search33.py:119-128).
- SF2 fixed: only FitError writes FAILED (872-883); other errors propagate and stop the run (rc 5; MemoryError rc
  4) (run_search33.py:263-269). SF3 fixed: one worker per fold with its own pipe; a dead worker charges only its
  own fold (166-209, 256-262). SF4 fixed: the attempt record is written before load_tables (843-850, 868).
- load_tables validates the grid, t_ns equality of features and labels, finite features, the label schema,
  classes and weights (261-360), and stops on a missing sigma (S5).
- The real root needs --registered (S10, run_search33.py:69-83) so no real-outcome fit happens before C1.

Selection (select33.py 75-291 read; the rest per ProofReview):
- b_test = p7_final's unrounded value, asserted 0.164882 at N 838 (75-88); se(SR) as P8 G4 (91-96); G1 integer
  comparisons (154), G2 (155), G3 DSR with (sharpe, T, N, 1/(T-1), skew, kurt) in the function's own argument
  order (funnel/multiple_comparisons.py:81-88 checked) (157-165), G4 (166-170), G5 (a)-(d) (178-206), the total
  order (220-228), Tier A and Tier B walks at rho <= 0.70 (245-288).
- 147 tests of test_lab33, test_cal33, test_cost33, test_select33, test_stats_repro33 pass (my run 03:13:37-03:13:57
  PDT, nice 10, one process; log in my scratchpad pipereview/pytest_light.log).

Calendar and data (cal33.py 181-410 read; data33, guard33, split33, check33 by their function maps and docstrings):
- P1.4 exclusions by the rule (roll = ZM front differs from the previous grains trade date, the date after, the
  calendar reasons), cross-checked against measure31.roll_reasons (207-235).
- P3.6 rule 3 parse rule exactly as written (259-278), the count assertion (290-292), the two NOPA rule dates
  (293-305); the CSVs sha-pinned (guard33.py:64-69, 341-348).
- Rule 5 limits from the front's last outright definition with ts_recv <= 08:30:00 CT on D, UNDEF/0 -> None
  (333-359); per-instrument stable sort of a ts_recv-ordered array = the single as-of pass.
- C.7, C.10, C.15 (367-404). G6 report: 39 months, 0 flagged (G6_clock_report.md:51).
- Guard dry check: 4 of 4 refused (guard_dry_check_start.txt); LT6 44 + 10 tests (B4_leakage.md).

Features (feat33.py 119-1148 read; dayB.py 42-123; implB readings):
- The 59 features in INTERFACE order; the G4 clip list is exactly the protocol's 38 (105-110, re-counted); G3
  invalid -> 0 with the family flag (922-935, 1144-1146).
- Window (mark p - k, mark p] on the open-time axis (664-667); sample points p-1..p-k (943-950); references and
  sigma pooled from the 20 dates (759-791); F1.3 fit on centred regressors with the intercept recovered from the
  means, sd_e = sqrt(SSR/n)/0.10 (815-850); gC and GAP with their 20-date SDs (853-918); F2.7, F3.5-F3.12,
  F4.1-F4.13 as defined (1032-1126); C.5's Vbar at the same minute of day (900-902, 993-995).
- Point in time: every counter and state is "as of" the mark (192-196, 304-305); the builder's --cutoff-ns
  truncates all four streams (build_features33.py:146-172, 276-303) and refuses a cutoff before 08:30 on D
  (FA-26).
- The MathReview hand values (10 features, 12 labels) matched A and B exactly or to 2e-13.

Proofs and cost (per ProofReview; my checks): the run manifest pins code, p7 files, versions and uv.lock
(run_proofs33.py:40-130), refuses a resume under other code (113-118); seeds interleaved 1,101,2,102,...; a seed
with selection.DONE is skipped, never rerun (141-143); ProofReview SF1 (failed column) and SF2 (versions) fixed
(B5_proofs.md shows both). cost33 (138-370 read): market fills as lab33, the trade-through limit entry resting at
the touch at t + L, filled by the first A/B print strictly through it in (t + L, c + L], c = min(t + W,
exit_decision), W = min(60 s, h/5); conversion at c; per-firm fees from the protocol table; 19 tests pass.

## Not checked / limits

- The B3 rerun itself (condition 1); the full feat33/featB equality on real data is the TestCoder's harness.
- replayB.py and featB.py were read by their function maps and readings only (B's side was the ruled one for FD4
  and FD5; FD3b/c on B's side read in dayB.py). build_featB.py not read.
- synth33.py was not re-read beyond its imports (no real-data loader; cal33 for dates only); ProofReview covers it.
- test_search33.py (36 tests, 150 s) not rerun: SearchReview ran it at 02:07 and the engine changed after that
  for SF1-SF4; the lead should rerun it once before the freeze (it is the LT3 evidence).
- tests_b4/test_lt4_labels_handbuilt.py, tests/test_feat33.py and implB/tests (test_featB, test_replayB,
  test_labB): 186 passed in 31.9 s (my run 03:19:14-03:19:48 PDT, nice 10, one process, -rfExX: no failure, no
  xfail, no xpass; so the superseded D1/D2 "documented" tests the LabelCoder reported had already been updated).
  Together with the 147 above: 333 tests run by me, 0 failures. Not run by me: test_search33 (36), test_guard33
  (44), test_data33, test_synth33, test_run_proofs33, tests_b4/test_lt3/lt5/lt6 (run by their authors and the
  earlier reviewers).
- No real-data run beyond counts, hashes and the existing stores was made; no outcome was read.

## Not reached (for the continuation stage)

Modules not read, or read by function map and docstring only: data33.py (loaders; its ordering rule and
truncate were covered by LT4's tests and the docstring), split33.py, check33.py, g6_33.py (its report read: 0
flagged months), build_labels33.py (read 150-168 and the sigma/DONE lines only), build_features33.py (read by
grep: cutoff, history, manifest, pool), featB.py (44-95 read; families by map), replayB.py 94-258 read,
build_featB.py and labB*.py not read (B's labels agree exactly with A's, 0 cells), synth33.py and run_proofs33.py
beyond ProofReview's coverage and the manifest/resume logic (40-143), cost33.py 1-137 and 370-420 (fee loading
from E.28's file; the E.31 per-fill accounting and its agreement claim in StatsCostCoder_readings.md 138+ were not
verified by me), tests/test_stats_repro33.py's worked examples (run, 147 passed, but the cited digits were not
re-derived by me; MathReview re-derived the threshold arithmetic).
Evidence not reached: the full 20-date B3 rerun (only the 10-date partial), the final B4 synthetic feature run on
the ruled code, LT1 (200 draws), LT7, the 38 remaining proof seeds, DataCoder_progress.md and probe files beyond
B4_leakage.md's summary of them.
Focus items of the brief covered: 1 (departures: none found in what I read), 2 (leakage: none found; LT3/LT4/LT5
evidence read), 3 (agreement: every FD diagnosis read, SF3 is the one open one), 4 (silent failures: none on an
outcome path; N7), 5 (tests: 333 run; the gaps are listed above), 6 (readings: every coder reading I reached has a
view above; not reached: LB-5/6/8/10-16 and B-* readings not named in SF1, DataCoder DG/DATA/CAL beyond those
named, and the generator readings P-* beyond ProofReview's view).
