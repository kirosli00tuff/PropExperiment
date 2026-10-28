# PipelineReview_b (Stage E.33b B7 first bullet, continued; PipelineReviewer-FableXHigh)

Reviewer: PipelineReviewer-FableXHigh, fresh context, wrote none of this code; the session identifies itself as
claude-fable-5-1 (the lead confirms the model from the transcript). Started 2026-10-28 09:13 PDT; times from `date`.
Phase 1 written 09:13-09:23 PDT; Phase 2 is appended below when the lead sends it.
Starting point: review/PipelineReview.md (the E.33 PipelineReviewer, also Fable; 0 BLOCKING, 3 SHOULD FIX, 10 NOTE,
provisional NOT YET). Its findings are not repeated; this file covers what it listed as not reached, the test reruns,
the R-L3 hash condition, and the lead's rulings of 09:12 PDT (R-B3-FD6, R-B3-FD7, R-B3-N10). Standard, object and
focus items as in briefs/brief_PipelineReviewer.md; INTERFACE rule 1 and R-L2 hold (every real-data check here is a
count, a hash or an equality; no label or outcome statistic was read).

File versions. At 09:13 every pipeline/ and implB/ file was byte-identical to the version the E.33 review read
(feat33 66b4e251dce9, lab33 025bdedff858, search33 a7d30b2a6786, select33 9b9928066a35, synth33 5a5ed5b91f09,
run_proofs33 4a0f4e9825cd, build_features33 2784e6b9ef85, cost33 505f52524aad, data33 8295a6ee26e5, split33
b8c3a96afb13, check33 93abc1361c78, g6_33 bf1f3d2e5961, build_labels33 947c2b5e0be0; implB featB 33269b3a4b4e,
dayB 150d3c6c8dee, replayB c20eab0a2df6, build_featB b9fee7234fcb, labB 0dcee18f63d7, labB_book b9867131569e,
labB_cal b77caabb4105, build_labB da2f69b4de42). During this review two files changed: feat33.py at 09:15:18 PDT
(now b216f11ee2df; `git diff` against HEAD 66b4e251dce9: 3 lines at 410-413, the R-B3-FD7 gate dropped, plus 57 new
lines in tests/test_feat33.py) and implB/replayB.py at 09:15:39 (now 5910d217000a; against HEAD c20eab0a2df6: the
R-B3-FD6 `rem == 0` condition at 153-158 and the R-B3-N10 clear-then-mark at 181-182, plus 66 new lines in
implB/tests/test_replayB.py). Those diffs are Phase 2 material; where this file cites feat33.py or replayB.py lines it
says which version. Every other file above was unchanged at 09:18.

## Interim verdict (Phase 1)

NOT YET, unchanged in kind from the E.33 review, narrower in content. Nothing read in Phase 1 is BLOCKING; the
modules the E.33 review did not reach implement the protocol's declared choices and have no silent-failure path on an
outcome; the named tests pass (140 of 140); the R-L3 hash condition holds. The conditions for GO are the E.33 review's
three, as they now stand:
1. B3 to 59 of 59 columns at 0 cells on the ruled code. The rulings R-B3-FD6/FD7/N10 are made and the fixes are on
   disk (09:15); the 20-date rerun on them is Phase 2.
2. SF1 (the readings file hashed by the freeze list) and SF2 (the freeze list covering screening/, funnel/, the p7
   files and the E.31 modules): still open; reports/stage_e33_protocol_readings.md line 139 still reads "(to be filled
   from ...)".
3. N10 fixed on B's side: the fix is on disk; the final B4 synthetic feature run on it is Phase 2.
Phase 1 counts (new items only): BLOCKING 0, SHOULD FIX 0, NOTE 4 (N11-N14 below). Carried from the E.33 review:
SHOULD FIX 3 (SF1, SF2 open; SF3 ruled as R-B3-FD6, fix landed, rerun pending), NOTE 10.

## R-L3 hash condition (checked 09:14 PDT)

Every one of the 10 files in /mnt/large-storage/market_data/PropExperiment/derived/e33/proofs/run_manifest.json
`code_sha256` is byte-identical to the current file (cal33, data33, guard33, run_proofs33, run_search33, search33,
select33, synth33 under work/pipeline/; p7_final, p7_thresholds under reports/stage_e32_briefs/protocol/): SAME on all
10 (my script, scratchpad pr_b). `engine_pipeline_sha` 323a82ff96ca recomputed from search33.pipeline_files()'s
closure (guard33, run_search33, search33) with the same AST walk: SAME. `versions.uv_lock_sha256` 7fecbfa47327 equals
the current uv.lock. The manifest records two starts (pid 2022359 at 02:36:25 and pid 2277373 at 09:09:19 PDT, both
with the 40 seeds); the 09:09 restart passed check_manifest (run_proofs33.py:102-128), which is the same comparison.
The 09:15 changes to feat33.py and replayB.py do not touch the condition: neither is in the manifest, by R-L3 (b)
(the proofs never execute the record-level builders; verified: pipeline_closure() from the proof roots returns
cal33, data33, guard33, run_proofs33, run_search33, search33, select33, synth33 and nothing else).

## Test reruns (one process, nice 10, 09:14:30-09:17:39 PDT; `free -m` available 6,021 MB at start; log
scratchpad pr_b/pytest_rerun.log)

`uv run pytest -q -p no:cacheprovider -rfExX` on tests/test_search33.py (45 tests; the E.33 review's "36" predates
the SF1-SF4 fixes), test_guard33 (44), test_data33 (10), test_synth33 (15), test_run_proofs33 (10), tests_b4
test_lt3_embargo (3), test_lt5_canary (3), test_lt6_guard_classes (10): 140 passed in 187.87 s, no failure, no xfail,
no xpass. Provenance: feat33.py changed at 09:15:18 while the run was in test_search33; the only test here that
imports feat33 is test_lt3_embargo's test_builders_load_at_most_21_history_dates (asserts N_HIST == 21), which ran
after 09:17 on the new file; the assertion does not depend on the FD7 lines. lab33 (unchanged) is what test_synth33
and test_lt5 import. With the E.33 review's 333 and the 19 of test_cost33 it ran, every test file under tests/,
tests_b4/ and implB/tests has now been run by a reviewer; test_feat33 and test_replayB must be rerun on the 09:15
files (Phase 2).

## Findings

### BLOCKING

None.

### SHOULD FIX

None new. SF1 and SF2 of the E.33 review stand as written there. SF3 is now R-B3-FD6 (see Readings).

### NOTE

N11. data33 re-sorts a per-day store silently when its ts_recv order has a decrease, and Coder-A's builders do not
record that it happened. data33.py:94-99 (`_in_ts_recv_order`: a stable argsort, the count into the module dict
ORDER_LOG); the docstring (21-26) says the stores keep file order and the count is expected to stay 0. Readers of
ORDER_LOG: implB/build_featB.py:112, 129-130 and implB/build_labB.py:90-91 write it into their logs; pipeline/
build_features33.py and build_labels33.py never read it.
- Protocol: P0.3 (records known at ts_recv; LT4's ordering rule).
- Failure scenario: a store rebuilt in another order would be silently re-sorted on A's side and the DONE markers
  would carry no trace; on real data the count is 0 (discovery manifest `ts_recv_non_decreasing` detail 0 in all 156
  files; the E.31 markers' counts and check_records are asserted on every load, data33.py:153-161), so this is a
  marker gap, not a data risk.
- Fix (optional, after the freeze is not possible without a re-hash, so either now or never): write
  `dict(data33.ORDER_LOG)` into pass1's DONE info (build_features33.py:166-173) and build_date's result
  (build_labels33.py:169-176), as B does.

N12. implB/build_labB.py's resume marker is not keyed by the code: a date with `_day/<D>.json` under --out is skipped
whatever code built it (build_labB.py:151-153), and manifest.json at the end records the current code_sha12 for every
date (247-250). build_featB keys dayraw/ and features/ by code_sha12 (build_featB.py:172-173); build_labels33 keys
the folder by code_sha12 and refuses a marker whose code or sigma source differs (build_labels33.py:129-139).
- Protocol: none directly (B's labels are the agreement check, not the frozen code); INTERFACE 4.2.
- Failure scenario: a labB fix followed by a rerun into the same --out keeps the old tables and claims the new sha.
  It has not happened: labB.py, labB_book.py, labB_cal.py, build_labB.py are unchanged since 2026-10-27 15:12 and
  efdde5c74ee1 is the only B label code built (B3_agreement.md line 23).
- Also: `--sigma auto` falls back to B's own sigma when no FeatureCoder2 `_day` file exists (build_labB.py:161-168),
  recorded in `_day/<D>.json` `sigma_source`; the B3 TB comparison depends on that field saying "implB/features/_day
  sigma_zm (FeatureCoder2)" on all 20 dates (the E.33 review's N9 covers A's side).
- Fix: if any labB change is ever ordered, run it into a fresh --out; otherwise none.

N13. The production feature run must target every OOF date so the label build finds its sigma. build_features33.pass2
writes `_day/<D>.json` for its target D only (build_features33.py:207-211), although the module docstring (5-7) says
"for every date it covers"; build_labels33 reads `_day/<D>.json` for each OOF date (85-90, 254-259) and
sigma_from_features raises through g.check_path on a missing file. A run with `--dates oof` or `--dates all` covers
it (pass 1 adds the 21 history dates itself, 255-259); a run on a subset would stop the label build on the first
date not targeted (a loud failure, so a NOTE for the run plan, not a fix).

N14. B's label-side book does not mark bad on F_TOB / F_MBP (implB/labB_book.py:12-13, 74-75: counted only), whereas
R-B3-D3 chose Coder-A's convention (such records mark the book bad) and B's feature-side replay follows D3
(replayB.py:167-170, 181-182 in the 09:15 version: BAD | TOBMBP). 0 such records in Z1 (R-B3-D3), so no label cell
can differ; B's labels are not frozen code. Record it in the readings file beside D3 (SF1) so the test stage does
not read B's label replay as the ruled rule.

## Readings: the lead's rulings of 09:12 PDT (my view; the lead decides)

R-B3-FD6 (F3.11, a record whose reduction is partly fill lots and partly a voluntary remainder): chosen (a), Coder-A's
`rest == 0`. Agree. The protocol text "reached 0 displayed quantity through trades" names the cause of the level
reaching 0; under (b) the level reaches 0 only because the cancelled lots also left, so the cause is mixed, not
trades. (a) is also the reading under which R-B3-FD4 (b) ("a level whose last lots are cancelled does not") needs no
exception. Both readings are causal (everything is inside the record's own batch at its ts_recv), neither is the
conservative one for an outcome (the refill-rate feature F3.11 is a count whose direction has no sign for the label),
and the measured difference is about one refill event a day (B3_agreement.md: 4,013 vs 4,014 on 2021-01-19), which
moves rbar_15 and so every F3_11 row at 1e-9. The non-fill remainder counting as a removal on both sides (feat33.py
511-512 of 66b4e251dce9; replayB.py 149-152) is right: those lots left the touch voluntarily. The fix on B's side is
one condition (the 09:15 diff adds `rem == 0`); A's `_removal` (feat33.py:493-513, unchanged by the 09:15 diff)
already returns the level only when `rest == 0` and the caller checks `level_total == 0` after the record (444-445);
B's `level_total(side, price) - red <= 0` before the record is the same test. Phase 2 reads the diff and its tests.

R-B3-FD7 (F3.9, an F record naming an order not yet in the book, the batch then adding and reducing it): chosen (b),
Coder-B's attribution by order id within the batch. Agree. "Fills are not removals" classifies lots by what happened
to them, and the F record says those lots traded; whether the feed emitted the F before or after the A inside one
batch is record order, which the text does not make a condition. R-B3-FD5 already scopes fill lots to their batch
(`pending.clear()` at F_LAST, feat33.py:455 and at R 422; replayB.py:245 at F_LAST and 184 at R, 09:15 version), so
an id that never gets booked leaves nothing behind;
the reduction that consumes the lots is a C or M of an order that is in the book by then (`book.orders.get(oid)`,
feat33.py:502-504), so no fill lot is ever attributed to a level the book does not hold. Causal. Neither reading is the
conservative one (F3.9 is a removal count). Measured effect 10 cells (2 events x one 5-minute window, 2022-09-01;
B3_agreement.md full_r2). The fix in A is the 3-line diff of 09:15 (the gate `if oid in orders` dropped); I note for
Phase 2 that `pending.pop(oid)` at feat33.py:451 runs only for booked orders, which is correct under (b) because an
unbooked id is cleared at F_LAST anyway.

R-B3-N10 (B's feature replay marks bad before the R's clear): chosen R-B3-D1 as written, fix in B. Agree; this was
the E.33 review's N10 and the reasoning there holds (0 R records carry the flag on the 816 dates, tests_b3/count_d1.py;
B4's synthetic date 11 plants the case, so the final synthetic feature run must be on the fixed replayB). B's own
label replay already does clear-then-mark (labB_book.py:76-82), so after the fix B's two replays agree with each
other and with feat33.py:416-420 and lab33.py:308-313. The 09:15 diff adds the two lines after `book.clear`.

## Checked and found correct (Phase 1 modules; by reading, with the small runs named)

data33.py (all 285 lines): `truncate` keeps ts_recv <= cutoff by `searchsorted(side="right")` on a ts_recv-ordered
array (102-106), which `_in_ts_recv_order` guarantees; `_check_window` on a sorted array needs only the first and last
record (109-112); load_zm asserts dtype and record count against E.31's month marker, whose sha256 must equal the
discovery manifest's (129-140, 148-162); load_mbp1 asserts against its DONE marker (171-186); definitions are the
stable ts_recv sort of all 39 Z4 files, read-only, truncated by the same rule (189-203, 218-255); every path goes
through guard33 (check_request, check_path, check_records). No exception is caught anywhere in the module.

split33.py (all 202 lines): window [D-1 16:00 CT, D 16:00 CT) by ts_recv; a chunk's records are assigned by
`searchsorted(ts, lo[j], "left")` / `searchsorted(ts, hi[j], "left")`, i.e. lo <= ts < hi (122-131); a decrease in
file order raises (117-118); a date is flushed only when every later record is past its window end (133-136); a date
met by a file's request range with no record gets an empty table, not a missing one (137-139); a date left pending at
the end raises (143-145); outside-window records are counted (132, 140). Resumable per date, atomic writes, quiet
window 15:28-16:00 PT respected (110-113).

check33.py (all 175 lines): the independent count recomputes the window with zoneinfo America/Chicago (37-41), not
measure31.day_bounds or data33.window; `full_counts` assigns each raw record to the last window start <= ts and keeps
it only if ts < that window's end (132-135). Counts only.

g6_33.py (all 169 lines): per month, numpy.percentile p1/median/p99 of ts_recv - ts_event with F_SNAPSHOT and
F_BAD_TS_RECV records dropped and counted (READING G6-1), front-only column, the 100 ms flag rule (138-143). No
outcome. The report shows 39 months, 0 flagged (the E.33 review read it).

build_labels33.py (all 350 lines): replay cutoff `session_end_ns - 1` = records with ts_recv < 13:20:00 CT (153-157;
P3.2 exit fallback bound); an excluded date without Z1 records is reported as book_missing, a non-excluded one raises
(155-162); DONE markers carry code_sha12 and sigma_source and a differing marker raises rather than skips (129-139);
manifest.json refuses a run whose code files or sigma source differ (280-291); TB without --features-sha refused
(252-259); worker exceptions propagate through pool.map (328-330); prints counts only (335-346). The per-rule
removal counts P3.6 asks for are in `_excl/<D>.json` (123-125, lb.compute_label's excl).

build_features33.py (all 340 lines; version 2784e6b9ef85 of 03:04, which the E.33 review grepped but did not read):
code_sha12 over feat33, build_features33, mbo_book31 (46-64; FA-28); pass 1 streams D (and the previous date first
under FD2 when D has no overnight session, 124-138, 155-159) through data33 with the LT1 cutoff on all three feeds
(157-159); pass 2 builds the references from the 21 history dates' pass-1 tables (194-205) and keeps rows t_ns <=
cutoff under LT1 (215-219); build_cutoff refuses a cutoff before 08:30:00 CT on D (288-289, FA-26) and offers
prior = recompute (history re-streamed under the cutoff) or production (203-210, 294-303; T-5); b3_dates is the STATE
rule (88-93); set_nice 10; MAX_PROCS 4; exceptions propagate (248-252). Docstring/code gap on `_day` noted as N13.

run_proofs33.py (143-388, beyond the E.33 review's 40-143): a seed with selection.DONE is never rerun (141-143);
synth33.write_seed is skipped when synth/DONE exists (synth33.py:615-621), so the 09:09 restart reused the finished
seeds' tables and the search markers' tables_fingerprint check (search33, SearchReview SF1) guards a partial seed; a
non-zero run_search33 exit stops the whole run (157-158); selection.json and selection.DONE carry select33's sha
(162-169); the summary prints the writer's sha beside the manifest's (270-285, ProofReview N6 fixed) and the
ProofReview SF1 counting rule (291-293, 303-305, 327-330); the null-Sharpe SD is centred per configuration with the df
correction printed (226-255, ProofReview N2); production seeds refuse mixed, partial (without --allow-partial),
resized or re-kinded runs (355-361); OMP/BLAS threads pinned to 1 (375-376).

synth33.py: the E.33 review relied on ProofReview, whose coverage (ProofReview.md 211-247) I re-read against the
function map: generator, labels, oracle, calibration, determinism and layout are covered there; write_seed (615-676)
read by me: DONE written last, _day json for all dates with sigma null where undefined, `_excl` with the rule-4 and
rule-3 counts, oracle.json without the series, manifest with generator_sha256 and the constants. Nothing beyond
ProofReview's view.

cost33.py 1-137 and 370-420 (the E.33 review read 138-370): per-firm fees from E.28's A2 files with the A3 and P6.4
cross-checks and FEE_TOL 1e-9 (85-126); a non-positive or non-finite fee raises (103-104); per-fill nets as E.31's
s (mid(t_f + h) - price) - fee/2, NaN when the mid is undefined (372-379); limit_summary raises on no signals
(400-401). The E.31 per-fill agreement claim (StatsCostCoder_readings.md "E.31 agreement (B6)") is verified by
reading tests/test_cost33.py 224-323: E.31's measure31_core.InstrumentRun is run end to end on 5 hand-built MBO
cases with one placement grid time (a buy and a sell each = 10 orders), the fill time and limit price are compared
order by order against cost33.through_fill, and the per-fill net against stats31.edge_arrays minus
stats31_core.FEE_PER_FILL_TICKS for 3 horizons x 5 firms at abs 1e-9, with the expected fill counts 2, 2, 0, 2, 0
(= 6 fills) asserted; test_e31_window_differs_only_by_its_cancel_latency documents the one window-length difference.
E.31 code is imported, never edited. The 19 tests passed in the E.33 review's run (03:13); not rerun by me.

tests/test_stats_repro33.py cited digits (spot check, re-derived independently in a 15-line script with
statistics.NormalDist and the Bailey-Lopez de Prado formulas): SR0 at N 100, V 1/(2 x 250): 0.113172 (cited 0.1132);
DSR at N 100, T 1250, skew -3, kurtosis 10: 0.900397 (0.9004); N 46: 0.950502 (0.9505); N 88 with normal moments:
0.950491 (0.9505); population kurtosis of [1,2,3,4]: 1.64; BH 4/15 x 0.05 = 0.013333 and 0.05/15 = 0.003333. All
match at the cited precision. b_test 0.164882 at N 838 is asserted in select33.b_test_at (75-88) from p7_final's
unrounded value; MathReview re-derived it, I did not.

implB/build_featB.py (all 214 lines): outputs keyed by code_sha12 over calB, replayB, dayB, featB, build_featB
(44-59); day raws resumable by file (117); LT1 refuses history dates whose window ends after the cutoff (183-186) and
builds the target's raw under lt1/<cutoff>/ (188-190); memory guard 2.5 GB; worker exceptions propagate
(126-127); ORDER_LOG logged (112, 129-130).

implB/build_labB.py (all 257 lines): see N12; replay cutoff ts_recv < 13:20:00 for labels and <= 13:13:00 for the
sigma mids (48-49, 79-92); own sigma = population SD of 1-minute mid changes pooled over 20 dates with both ends valid
(labB_book.py:142-152; P0.3); `_day` json written last as the marker (187).

implB/labB_book.py (all 152 lines): D1 clear-then-mark on R (76-82); records before the first R not applied and
counted (83-84); side-N A/M counted, not applied (91-94); one update per F_LAST record with has_bid/has_ask and
bad = not started or bad (104-112); tick-multiple assertion (118-119). N14 on F_TOB/F_MBP.

implB/labB.py 206-330 and 400-584 (rules, simulation, table): tb_half_width None when sigma undefined or <= 0
(206-211); release rule closed intervals [R - 2 min, R + 30 min] on the entry span and the TB-extended row span
(215-221, 256-260, 289, 303-304); the limit test 50 s2 >= 99 HL - LL or <= 101 LL + HL, which I re-derived from
M >= HL - 0.02c and M <= LL + 0.02c with c = (HL + LL)/2 (224-230; equal to lab33's 198 HL - 2 LL form); r5_row by a
cumulative count of updates lacking a side in the closed [t, span end] (283-288); entry fill as of t + L else the
first later update with the side present strictly before the planned exit else not made with the flag (416-425);
TB entry needs M defined at the fill update (427-429) and sigma (430-431); exit fallback before 13:20:00, then the
limit mark, then the last valid touch, which raises if there is none (441-460); check_invariant raises when a clean
row's simulated net differs from its label or a not-made entry carries no flag (533-542); exclusion counts first-rule
and any-rule (545-584). No exception is caught in labB.py; the only `except` in the four B label modules is the
os.nice OSError in build_labB.py:72-76.

implB/labB_cal.py 60-140 and 140-241: 816 dates asserted (68-73); exclusions from measure31.roll_reasons and
calendar_reason (120-138); release parse rule with the counts asserted against P3.6 rule 3's table and the two NOPA
gap months (151-196: a malformed row is skipped by `continue` but the asserted counts catch any loss); limit prices
from the front's last outright definition with ts_recv <= 08:30 CT, UNDEF/0 -> None with the reason recorded
(216-241), the same rule as cal33.limits.

## Not checked / limits (Phase 1)

- The 09:15 diffs of feat33.py and replayB.py and their new tests: Phase 2 (the lead sends them).
- featB.py and dayB.py beyond the E.33 review's lines (44-95, 42-123): not read; B3 full_r2 shows A = B on 57 of 59
  columns and FD6/FD7 explain the other two.
- labB.py 1-205 and 330-400 (Updates, derive, asof, grid, first_passage, fh_labels, tb_label_row, weights): read by
  function map only; B's labels equal A's on 0 cells over 20 dates (lab_r3, full_r2) and LT2_r3 has 0 violations.
- cost33.py 138-370 and test_cost33's 19 tests: the E.33 review's; not rerun by me.
- No real-data run beyond counts and hashes; no outcome read.

# Part 2a (lead's message of 12:20 PDT; written 12:20-12:30 PDT)

Scope: (1) every diff since E.33's commit under work/pipeline and work/implB against its ruling; (2) the readings
file as it stands (last edit 12:19); (3) the freeze tool and its dry run. Verdict on the freeze is Part 2b.

Counts (Part 2a, new items): BLOCKING 0, SHOULD FIX 0, NOTE 6 (N15-N20). Every fix diff implements its ruling;
nothing changed under pipeline/ or implB/ beyond the lead's list except two LT7 harness files (N15); all 10 NEEDS LEAD
items are ruled and none of the rulings contradicts the frozen protocol; the freeze tool covers SF2 and the R-L3
check passes under it.

## (1) Fix diffs (`git diff HEAD`, 14 tracked files + 4 untracked; hashes at 12:20)

Hashes verified by me against the lead's: feat33 b216f11ee2df, build_features33 5bb65afb1689, build_labels33
e0da4cf1996a, lab33 e1c3c0163fb8; feature code_sha12 2b30cb0e953b (feat33 + build_features33 + mbo_book31), label
code_sha12 b15c4ca10d68 (lab33, build_labels33, cal33, data33, guard33, mbo_book31); Coder-B 0485beafebbb (calB,
replayB, dayB, featB, build_featB; replayB 5910d217000a, dayB 87a57970fb21). Protocol sha c4ffb9d79af4.

Coder-A:
- R-B3-FD7, feat33.py:410-413 (3 lines): the `if oid in orders` gate on F records dropped; `pending[oid]` now
  accumulates for any id; the per-batch clear at F_LAST (455) and the R clear (422) are untouched, `_removal`
  (493-513) and `_consume_fill` (525-534) untouched. Implements R-B3-FD7 (b) exactly as the ruling says ("drop the
  book-membership gate on F records, keep the per-batch clear"). Nothing else in feat33 changed (diff: 6 lines).
- PipelineReview_b N11, build_features33.py:161, 173 and build_labels33.py:163, 177, 189: `dict(data33.ORDER_LOG)`
  taken after the date's loads and written into pass 1's DONE info, build_date's result and every label DONE marker.
  As asked. See N16 for the one subtlety.
- R-L10, lab33.py:582-598 (new `tb_row_end` = t + 2L + h min and `tb_row_rule_fail`: rules 2 and 3 of P3.6 as TB row
  rules on that span), 622-634 (`label_row`: the TB-M0 branch and the locked-book row rule both check
  `any_not_both_ok(t, row_end)`, the old `max(poss_end, span_end)` union gone), 751-752 (`compute_label`: the row
  rules applied to every entry-ok TB minute before `label_row`; entry_ok unchanged), 797-805 (`span_violations`, LT2:
  hi = max(t + 2L + h, span_end) for TB). The entry rules stay on [t, t + L + h] (`entry_rule_fails` untouched);
  FH untouched; `first_barrier` still monitors (t + L, t + L + h]. Implements R-L10 (d) and matches B's
  `possible_span_end` (labB.py:256-260) and `r5_row`/`span_row` (283-306), which were already (d). I re-checked the
  docstring's claim that rules 2-3 cannot fire on the grid where their entry part holds: t + h <= 13:12:00 so
  t + 2L + h <= 13:12:02 < 13:13:00, and t + h + 2 s >= R - 2 min iff t + h >= R - 2 min (whole minutes), the same
  condition as the entry span's t + h + 1 s. First-fail attribution in `_excl` changes order (r2/r3 before
  r5_locked_span/tb_m0), the row set does not.
- Tests: test_feat33.py +99 lines (FD7 with its two contrasts across batches, FD6 (a) with the all-fill contrast, the
  N11 DONE record on well-ordered and planted-decrease stores), test_lab33.py +101 lines (R-L10: early tau kept under
  the old union and dropped now, vertical, the closed end, 1 ns past it, FH unchanged, compute_label with LT2 0; rules
  2-3 on the whole span; the N11 marker). Each would fail on the pre-ruling code by construction (the old `max(poss_end,
  span_end)` keeps the "early" row; the old gate gives Ca = 3).

Coder-B:
- R-B3-FD6, replayB.py:153-158: `fill > 0 and rem == 0 and price == best and level_total - red <= 0` (the `rem == 0`
  added); the non-fill remainder still counted as a removal at 149-152. Implements (a). B's own count: 80,521 ->
  80,305 refill events on the 20 dates, a subset per date (FeatureCoder2_readings.md, E.33b section).
- R-B3-N10, replayB.py:181-182: `book.mark_bad()` after `book.clear` on an R carrying BAD | TOBMBP. Implements
  R-B3-D1 as written; B's feature replay and its label replay (labB_book.py:76-82) now agree.
- R-L11, dayB.py:352-354 (docstring) and 364-369: `last_of_ts[:-1] = ts[1:] != ts[:-1]`, `v = valid & last_of_ts`
  before the running max/min. Implements (a): only the state after the last update of each ts_recv can set Hi or Lo,
  the 08:30:00 seed unchanged. A's loop (feat33.py:474-477, `nxt[j] > t`) is the same rule, so the two sides now read
  F4.6 alike; B measured 0 changed F4.6 values on the 20 dates (58,115 same-ts_recv updates, none a new Hi or Lo).
- Tests: test_replayB.py +88 lines (FD6 C and M-to-another-price cases plus the all-fill contrast, N10 for the three
  flags with the next R restoring the book, R-L11 with a crossed later same-ts state). B reports 6 of 7 fail on HEAD.
- calB, featB, build_featB unchanged (hashes above); FeatureCoder2_readings.md and timing_featB.md: notes only.

TestCoder harness (evidence code, not pipeline code):
- run_synth_features.py: `SEED = args.seed` in main() before any fork (the module constant 7 was used by every run,
  so E.33's synthetic feature runs 7, 8 and 9 all generated seed 7's streams); `--expect-a-sha/--expect-b-sha`
  refusals; code_used.json keeps a run list; the oracle follows R-B3-D1 (clear then mark, 227-229) and R-L11
  (`last_at_ts`, 268-271); every generated date carries PLANT_FD6 (6 a day) and PLANT_FD7 (4 a day), target k = 11 the
  flagged R. synth_streams.py: `Episodes.mixed_trades` / `unbooked_fills` and `_mixed_trade` (one part-fill, part-
  cancel C empties the touch, an add 40 ms later) / `_unbooked_fill` (T, F for a new id, A, C in one batch; even j all
  fill lots, odd j 3 fill + 2 voluntary). I checked the record structures against the rulings: under FD6 (a) the
  mixed C opens no window on either side and the fully filled orders' Cs leave the level non-empty; under FD7 (b)
  the odd case yields a removal of 2 on both sides. test_synth_plants.py replays the plants through mbo_book31 and
  asserts exactly that structure. lt2_span.py: `span_hi` (R-L10) and test_lt2_span.py (6 tests, stub calendar).
- Changed after the lead's list (N15): lt7_causality.py (12:20:58) and run_lt1_lt7.py (12:21:23).

Nothing else changed: `git status` at 12:24 lists, under work/, exactly the files above plus B3_agreement.md,
B5_proofs.md (rewritten by the proof run), FeatureCoder_readings.md (+53 lines, 12:17) and TestCoder_readings.md
(2 lines); untracked: lead/freeze33.py, lead/test_freeze33.py, tests_b4/test_lt2_span.py, tests_b4/test_synth_plants.py
and logs/. No file under screening/, funnel/, sim/, rules/, data/ or docs/ is modified; REGISTRATION.md is 0 bytes.

Tests: pipeline/tests and implB/tests, one process, nice 10, 12:20:17-12:21:13 PDT: 438 passed in 55.8 s (log
scratchpad pr_b/pytest_2a.log). With Phase 1's 140 (test_search33 ran under the pre-FD7 feat33 but does not import
it) and tests_b4's new files not in this run (test_lt2_span, test_synth_plants: run by their author), every unit test
on the final code has passed in a reviewer's run except those two, which Part 2b should include.

## (2) The readings file (reports/stage_e33_protocol_readings.md, 2,013 lines, last edit 12:19 PDT)

- Status (lines 3-8): DRAFT until B3 full_r3, LT1/LT7 at scale and this review's Phase 2 report; finalised and
  hashed before the freeze; no reading after C1; a reading between the freeze and C1 re-takes the list. Consistent
  with P0.2 (protocol lines 35-40) and SF1.
- B3 continuation (112-145): R-B3-FD6, FD7, N10 as reviewed in Phase 1; R-L9 (LT1 prior = recompute on all 200
  draws with production beside it) is the literal P4.1 text (protocol line 467).
- Rulings on the compiled readings (146-186): R-L10 and R-L11 as reviewed above; the eight "confirmed or decided
  without a code change" items. Every one of the compiled file's 10 NEEDS LEAD items (its lines 245-269: L01, F06,
  L11-L13, K01, K04, K14, P12, P14, T07, F14; 12 flag lines, L11-L13 being one item) has a ruling or a confirmation
  there. Checked against the protocol: R-L10 is the "whole possible span" of P3.6 line 315 read with line 310's TB
  span over every tau; R-L11 is 0.3's "as of u" (line 72) applied to F4.6 (line 455); FD6/FD7 against lines 448/446;
  N10 against line 58; K01 against line 645 (both Lucid figures named); T07 against lines 477 and 620; P12 keeps a
  stricter proof count than P4.2's literal (line 521), which only lowers the chance of a null-proof pass and has
  not triggered (0 failed fits). No ruling contradicts the frozen text.
- N14 beside D3 (108-110): as I asked in Phase 1.
- Appendix (207-2013): byte-identical to reports/stage_e33b_briefs/readings_compiled.md after one '#' is stripped
  from every heading (my diff: empty). The compiled file is itself in the freeze list's documents section.

## (3) The freeze tool (work/lead/freeze33.py, 1,119 lines; test_freeze33.py 26 tests, not run by me) and its dry run
(reports/stage_e33b_briefs/freeze_dryrun.sha256 of 09:58, 239 lines; provenance 419 rows; freeze_inputs_dryrun.sha256
of 09:54, 4,125 files, 65.3 GB)

Read: the docstring and constants (1-115), `assemble` (662-752), `proof_lines`, `unpinned_evidence`,
`cmd_check_proofs` (997-1075); the rest by function map.
- Coverage of the import closure: the pipeline section (166 files) is measured by a child interpreter that imports
  every pipeline/*.py and follows static, function-level and dynamic imports, then runs four read-only probes under an
  audit hook (cal33.release_table, cal33.trade_dates, cost33.load_firm_fees, select33.b_test_at(838)). It holds every
  item of SF2: screening/stage_e_verdict.py, funnel/multiple_comparisons.py, p7_final.py, p7_thresholds.py, the E.31
  modules (measure31, measure31_core, mbo_book31, kalgo31), the grains and hist2010 calendars, the two release CSVs,
  the four discovery manifests (one file, 09396842c4fd, copied to the four request folders, equal to
  guard33.DISCOVERY_MANIFEST_SHA256), the E.28 fee files, the protocol, the readings file, uv.lock and pyproject.toml,
  and the derived-inputs manifest (Z1 855 files = 816 stores + 39 markers, ZS 1,633, ZL 1,633, Z4 4). The 49
  literal-unmatched rows are all outputs or glob patterns (fold*.npz, stats.json, *.parquet, the Z4 cache names,
  which are in the inputs manifest); the 39 outside-repo opens are the Z1 markers (in the inputs manifest).
- P0.2 documents: the readings file is a pipeline-section line (P0.2 line 39); documents section: INTERFACE.md, the
  nine coder readings files and the compiled readings. Evidence section: implB/ (9 modules, 3 test files, 2 timing
  notes) and tests/, tests_b3/, tests_b4/ (12 + 3 + 16 = 31 files at 09:58; 45 in the section). Freeze tools section: freeze33, test_freeze33,
  c1_freeze. Sections are disjoint by construction (736-742).
- State versus hashed: ledger/trial_registrations.jsonl is classified state (CONSTANT_CLASS, 105-106: C1 appends to
  it) and listed in the provenance, not hashed; ledger/databento_spend.jsonl is hashed as a harness path constant
  (provenance row 125). G6_clock_report.md and B5_proofs.md are classified output (107-108). data/sealed/ and .env are
  never read or hashed (74-75, 145-147; a probe opening one stops the build, 681-682). guard-refused constants (the
  MES research/confirmation series, the condition files) are listed, not hashed. An unclassified pipeline-owned
  constant stops the build (715). Sound.
- R-L3 under the tool: I ran `freeze33.py check-proofs --freeze freeze_dryrun.sha256` (read-only; nice 10;
  12:24:26-12:24:40 PDT; log scratchpad pr_b/check_proofs_dryrun.log): all 10 manifest files OK, uv.lock OK, the 7
  environment versions OK, engine_pipeline_sha recomputed from the list = 323a82ff96ca OK; of the files the proof run
  can execute or read that the manifest does not pin, 77 "ok" (modified before 02:36:25 and equal to HEAD, or sha
  pinned in a pinned file) and 0 WEAK; rc 0. Matches my Phase 1 check by another route.

### NOTE (Part 2a)

N15. Two LT7 harness files changed after the lead's list and are not in it: tests_b4/lt7_causality.py (12:20:58:
per-configuration accounting of every (draw, configuration) pair under six reasons, forked per-date workers with
`--procs` <= 3 at nice 10, sorted mismatch lists, `draws_total`) and tests_b4/run_lt1_lt7.py (12:21:23: step tokens
1, 2p, 2r, 3, 4 in the given order, `--expect-label-sha`, the label folder taken by code sha rather than the newest
mtime, `no_production_table` and `draws_picked` recorded). Evidence code only; the LT1/LT7 job started 12:21 on them
(`--expect-sha 2b30cb0e953b --expect-label-sha b15c4ca10d68`). Read: no silent path (a missing table or LT1 rebuild
is listed under missing_inputs and counted per configuration; decisions on excluded dates are counted apart as
"usable_on_excluded_date"). Fix: none; the lead's Part 2b list and the freeze's evidence section take the versions
the job ran, and the dry-run hashes of both (bc99a3db... is lt2_span; lt7_causality 7f425585..., run_lt1_lt7
8a4644f4...) are stale.

N16. N11's snapshot `dict(data33.ORDER_LOG)` (build_features33.py:161, build_labels33.py:163) is the module dict of
the worker process, which serves many dates in one ProcessPoolExecutor run; a date's DONE can therefore carry
entries of earlier dates handled by the same worker. Each key names the feed and the date, so nothing is
misattributed, and the count is 0 on real data. Fix: none needed; a per-date clear would be cosmetic.

N17. The freeze dry run (09:58) is stale on at least nine files it lists and two it does not: the readings file
(12:19), FeatureCoder_readings.md (12:17), TestCoder_readings.md (10:07), FeatureCoder2_readings.md and timing_featB.md
(about 10:01), lt7_causality.py and run_lt1_lt7.py (N15), and the new test_lt2_span.py (10:06) and
test_synth_plants.py (10:10), which the evidence glob will pick up. Expected for a dry run; the final `build` must
follow Part 2b's last edit and be checked with `verify --remeasure`. The derived inputs did not change, so the
09:54 inputs manifest can be reused (`--inputs`) with one `verify` of it (2 processes, nice 10).

N18. The evidence results the freeze decision cites are not in any section: B3_agreement.md, B4_leakage.md,
G6_clock_report.md and B5_proofs.md (the last two classified output), b4_runs/LT1_*.json and LT7_*.json, DERIVED/b3
and b4 outputs. P0.2 and B7 do not require them (they are results, not inputs), and B5_proofs.md changes until the
40th seed. Suggest the lead record their sha256 (as they stand at the freeze) in the freeze file header or the
progress entry, so the evidence behind the GO is pinned with the code.

N19. The measured closure hashes harness files the search never varies but a human may edit between the freeze and
C1: docs/ACCESS.md, docs/NULL_CRITERIA.md, docs/HOLDOUT_MANIFEST.json, docs/HOLDOUT2_MANIFEST.json, the stage_e0..e2b
JSON/MD reports named by data/config.py and screening/ constants, ledger/databento_spend.jsonl (an approved purchase
would change it). Any such edit fails `verify` and re-takes the freeze by P0.2, which is the safe direction but
noisy. Fix (optional): classify documentation-only harness constants in CONSTANT_CLASS as "doc" (listed, not
hashed), or accept and say so in the freeze header.

N20. B4_leakage.md lines 48-61 record the E.33 synthetic feature runs as "seed 7", "seed 8" and "final run seed 9";
by the TestCoder's finding all three generated seed 7's streams (run 8 and 9 differed from 7 only by harness and
code changes), so the E.33 evidence was one stream, not three. Run 10 (logs/synthfeat_10_genb.log: A 2b30cb0e953b,
B 0485beafebbb, plants on) is the first run on a chosen seed and on the final code; its result is Part 2b. Fix: a
sentence in B4_leakage.md (or the progress entry) saying so, so the stage record does not overstate the E.33 runs.

Not checked in Part 2a: test_freeze33.py not run (outside the lead's test permission); the B4 synthetic run 10's
comparison stage and the LT1/LT7 job (running); FeatureCoder_readings.md's new 53 lines and B3_agreement.md's
full_r3 section (Part 2b).

# Part 2b(i) (lead's message; written 12:48-12:56 PDT; the finished evidence, LT1/LT7 follows as 2b(ii))

Counts (Part 2b(i), new items): BLOCKING 0, SHOULD FIX 0, NOTE 3 (N21-N23). Every one of the six evidence items is
as the lead states; every number I could recount independently agrees. Real data: counts, hashes and equalities only;
the proofs are synthetic. Interim position after 2b(i): the three GO conditions of Phase 1 are now (1) B3 closed
(full_r3, 59 of 59 and 19 x 6 at 0 cells), (2) SF1/SF2 closed in substance (readings file complete, freeze tool
sound) pending the final hash and build, (3) N10 closed (run 10 at 0 cells with date 11 planted). What remains for
GO is 2b(ii): LT1 (200 draws, both priors) and LT7 at scale with 0 mismatches, then the final freeze list built
after the last edit and verified with `--remeasure`.

## (1) B3 full_r3: PASSED

b3_runs/full_r3.md (written 12:21 PDT, 180 lines) and B3_agreement.md lines 21-39 (12:23): A features
DERIVED/features/2b30cb0e953b against B implB/features/0485beafebbb; A labels DERIVED/labels/b15c4ca10d68 (TB sigma
from features/2b30cb0e953b/_day) against B implB/labels (efdde5c74ee1); run 12:21:52-12:21:59. Features: 59 columns,
5,460 rows joined (20 x 273), every column 5,460 agree / 0 disagree, NaN cells A 0, B 0 (I scanned the 59-row table
for any non-zero disagree count: none). Labels: 19 columns + `__row__` on F05/F15/F30/F60/T15/T30 with 5,460 / 5,260 /
4,960 / 4,360 / 5,260 / 4,960 rows joined, 0 disagreeing cells in every column on every one of the 20 dates (the T15/T30
rows are the R-L10 span on A's side now; 0 rows changed side). sigma_ZM/ZS/ZL: A feature = B feature = B label-builder
on all 20 dates (12-digit equality in the table). DERIVED/b3/mismatches_full_r3.parquet: 0 rows (pyarrow metadata,
mtime 12:21:59). Harness: compare_b3.py eb92aa8cb1e4, mtime 02:03:14, unmodified against HEAD (the E.33 review's
test_compare_b3 covers its tolerances: labels exact with NaN == NaN, w at 1e-12 relative, features at G7). The FD6 and
FD7 cells of full_r2 (F3_11 5,385, F3_9 10) are gone and no other column moved. The lead's G3 point holds: the protocol's
G3 (line 377) encodes an uncomputable feature as 0 with the family flag, so a pass-2 table has no NaN by construction
(feat33.py 922-935, 1144-1146 per the E.33 review); the invalid counts live in the builder's summary, see (6).

## (2) B4 synthetic feature run, seed 10: PASSED

DERIVED/b4/synthfeat/10/features_summary.json (12:25): 30 target dates 2023-11-28..2024-01-10, rows 8,190 (30 x 273),
rows_with_mismatch 0, cells_by_column {}, dates_with_mismatch {}, NaN cells A 0 / B 0, sigma_zm_disagree_dates [],
oracle columns C_1, C_2, C_3, C_4, C_15, F4_1, F4_6 with oracle_mismatch_dates {} (both sides); feature_mismatches.parquet
0 rows. code_used.json records two runs, both seed 10: stages gen,b at 10:11:17 PDT and a,cmp at 12:22:20 PDT, both
with A 2b30cb0e953b and B 0485beafebbb and the harness synth_streams.py f858cc7cc23d / run_synth_features.py
20f94ece41fd, which are the files on disk now (sha256 recomputed by me). So the streams carry the FD6 and FD7 plants
and target k = 11 the flagged R (N10), the seed is the one asked for, and the two builders agree on every cell with the
oracle agreeing on both. The log logs/synthfeat_10_genb.log shows the refusal-capable header line and the stage times
(gen 222 s, b 52 s).

## (3) LT2_r5: PASSED

b4_runs/LT2_r5.json (12:23:56; B4_leakage.md line 31: run 12:22:54-12:23:56, labels A b15c4ca10d68 and B efdde5c74ee1,
features A 2b30cb0e953b and B 0485beafebbb, the 20 B3 dates). Rows: A and B each 4,303 / 4,113 / 3,828 / 3,258 /
4,113 / 3,828 for F05..T30 = 23,443 a side, 46,886 in all; violations summed by me over the 12 rules x 2 sides x 6
labels: 0 (rules: grid_time, open_0835, close_1313, span_nonempty, fh_end_exact, tb_end_range, release_window,
excluded_date, book_side_or_bad_in_span, mid_invalid_at_t, limit_band_at_t, front_undefined); the feature part 5,460
rows a side, bad_t_ns 0. The run used lt2_span.py 28f93c969894 (mtime 10:06:09, the R-L10 `span_hi` version; the
09:58 dry-run hash bc99a3db is the pre-edit file, N17). The two P1.4-excluded dates among the 20 have no front entry
and 0 kept rows, as the excluded_date rule requires.

## (4) The 40-seed proof summary: both proofs PASS under P4.2

B5_proofs.md (mtime 09:50:17, 72 lines, no "not run" row), written by run_proofs33.py whose sha256 4a0f4e9825cd...
equals the manifest's and the file on disk; it prints the manifest's code sha256 list, engine PIPELINE_SHA
323a82ff96ca, versions and both starts (02:36:25 and 09:09:19, 40 seeds each). My recount from the 40 seeds'
selection.json / selection.DONE / proof_timing.json (script in the transcript; counts only):
- Null seeds 1-20: Tier A non-empty 0, seeds with any failed configuration 0, counted against the proof 0; P4.2 fails
  at 2 or more of 20 (protocol line 521): PASS.
- Planted seeds 101-120: Tier A non-empty 20, failed 0, pass count 20; P4.2 passes at 14 or more of 20 (lines
  530-531): PASS. The summary's Tier A membership shows the F15 configurations carrying it (S5F15L001E in 19 seeds)
  and no T30 configuration in any seed; the rule is "FH15 or TB30", so this is informational (N23).
- Every seed: kind correct, 20 configurations, selection.DONE carrying the pinned select33 sha256, exactly one
  search run with rc 0 (the 09:09 restart skipped the DONE seeds and ran the rest once; first DONE 02:48:18, last
  09:50:17). check-proofs on the dry-run list (Part 2a, 12:24): 0 manifest differences, 0 weak. So every seed ran
  once on the pinned code.
- Also in the summary: oracle SR_d mean 0.3443 (target 0.35); the null daily-Sharpe SD centred per configuration
  0.0425 (df-corrected 0.0436) against the 1/sqrt(796) = 0.0354 reference (ProofReview N2 asked for it to be
  printed; N23).

## (5) The notes

FeatureCoder_readings.md (+53 lines, 09:19-12:17 by its own times): records FD7 as applied, FD6 pinned by test, the
red checks on HEAD (FD7 test fails there, FD6 test passes), the identities feat33 b216f11ee2df / build_features33
5bb65afb1689 / lab33 e1c3c0163fb8, code_sha12s 2b30cb0e953b and b15c4ca10d68 (4fd0bb31d210 never built), the superseded
store features/efc132631cc1 (43 pass-1 dates, left in place), N11's cumulative ORDER_LOG (= my N16), R-L10 as applied
with LT2 0 and r5_locked_span 0 rows removed, and the test counts. Consistent with the diffs I read in Part 2a.
B4_leakage.md: the new "E.33b runs" section states the --seed defect ("SEED stayed 7, so runs 7, 8 and 9 all generated
with seed 7; fixed: set before any fork"), as N20 asked, plus the harness edits (1)-(5) and the stale-pin search.

## (6) The full feature store DERIVED/features/2b30cb0e953b: as stated; P10 met

Counted by me: _p1/*.DONE 816, *.DONE 816, *.parquet 796, _day/*.json 816; rows 217,308 = 796 x 273; 62 columns
(date, i, t_ns + 59); manifest.json code_sha12 2b30cb0e953b with feat33 b216f11ee2df, build_features33 5bb65afb1689,
mbo_book31 619622865fff and protocol c4ffb9d79af4; sigma_zm null on exactly 20 _day files (the burn-in dates: FA-15
pools 20 prior dates); `order_log` present and {} on all 816 pass-1 DONEs (0 re-sorts on real data: N11 closed on
the evidence); summary pass1_dates 816, pass2_dates 816, walls 740 s and 118 s. DONE mtimes run 09:28:58-12:40:11:
the 20 B3 dates and their 21-date histories were built at 09:28-09:54 under this same code (they are the tables full_r3
compared) and the resumable build filled the remaining dates 12:25:50-12:40:11. P10 (protocol lines 854-856): "A
features-only store ... may be built as soon as B3 passes and before the pipeline freeze, keyed by the sha256 of
the feature code that built it, and is rebuilt if the frozen feature code differs": B3 passed at 12:21:59, the full
build started 12:25:50, the folder is the feature code_sha12, and the freeze list carries the three files whose
concatenation it hashes. Met. Data note (counts only, N22): G3-invalid cells F1_7 and F1_8 75,621 each = 277 whole
dates, F1_3 32,760 = 120 whole dates, F4_7/F4_8 6,006 = 22 dates, F3_7 3,119 cells; 24 of 59 features have some
invalid cell. These follow the definitions (F1.7's sd_g needs at least 10 of the 20 prior in-segment dates, F1.3 at
least 3 of 10, F4.7 at least 10 same-front dates), so the dates after each ZM roll carry 0-with-flag for them.

Tests run for 2b(i): tests_b4/test_lt2_span.py, test_synth_plants.py, test_compare_b3.py, test_lt4_labels_handbuilt.py,
one process, nice 10, 12:51:59-12:52:19 PDT: 45 passed (log scratchpad pr_b/pytest_2b.log). With Phase 1, Part 2a
and this, every unit test file under pipeline/tests, tests_b4 and implB/tests has passed in a reviewer's run on the
final code except tests_b4/test_lt3_embargo, test_lt5_canary, test_lt6_guard_classes (run in Phase 1 before the
09:15 edits; none imports the edited modules except lt3's N_HIST constant check).

### NOTE (Part 2b(i))

N21. Label tables on real dates exist before the freeze: DERIVED/labels/b15c4ca10d68 holds the 20 B3 dates (12:17)
and run_lt1_lt7's step 3 builds the LT1-draw dates for LT7 (B4_leakage.md; the job running since 12:21). P10 (line
856) says "labels, fits and simulations wait for the freeze and the C1 registration" and names only a features-only
store as the pre-freeze real-data store. These tables are test inputs that prompt B3 (the 20-date agreement) and B4
(LT2, LT7) require, no outcome of theirs is read (counts only, LT2's rules, LT7's entry fills), and no fit uses
them. Fix: a sentence in the readings file or the STATE file saying that the pre-freeze label tables are B3/B4 test
inputs, that the production label store is built only after the freeze under the frozen label code sha, and that
b15c4ca10d68 is rebuilt if the frozen label code differs (the same rule P10 states for features), so the record does
not read as a departure from P10.

N22. The feature store's G3 invalidity by whole dates (F1.7/F1.8 on 277 of 796 OOF dates, F1.3 on 120, F4.7/F4.8 on
22): a property of the definitions at segment starts, not a defect. Record it as a data note beside N3 so the test
stage expects three features to be 0-with-flag on about a third of the dates after each roll.

N23. Informational, no action: the proofs show the plant detected only by F15 configurations (T30 in 0 of 20 planted
seeds), which is what a 15-minute drift plant should show; and the null daily-Sharpe SD (0.0425, 0.0434 over
non-constant series) exceeds the iid reference 0.0354 by about 20 percent, which the P8 gates do not use (they use
the fitted series' own se). Both are already printed in B5_proofs.md; nothing in P4.2 turns on them.

Not checked in 2b(i): LT1 (200 draws, both priors) and LT7 at scale (running; 2b(ii)); B5_proofs.md's per-seed
funnel columns and SR_d values beyond the pass counts (not gates); the LT7 harness's smoke check against the 03:12
partial run (B4_leakage.md's claim, not re-run by me).

# Part 2b(ii-a) (lead's message; written 12:55-13:02 PDT; LT1 prior = production, LT7, the draw, step 3; 2r running)

Counts (Part 2b(ii-a), new items): BLOCKING 0, SHOULD FIX 0, NOTE 1 (N24).

## Verdict: GO, conditional on LT1 prior = recompute (step 2r) finishing 200 of 200 with 0 rows after t and 0
columns outside G7

Everything else the freeze rests on is now on disk and checked: B3 at 0 cells on 59 + 19 x 6 columns, the synthetic
run at 0 cells with the FD6/FD7/N10 cases planted, LT2 at 0 violations on the R-L10 span, the two proofs passed on
the pinned code, the full feature store under P10, LT1 prior = production 200 of 200 clean, LT7 3,620 of 3,620
decisions and 259 of 259 fills equal, every unit test green in a reviewer's run on the final code, the readings file
complete, the freeze tool sound. The condition depends on:
1. 2r reaching 200 of 200 draws with rows_after_t 0 and bad_cols empty on every draw (8 of 200 at 12:55, all
   clean; the driver deletes each `_lt1/<t>` folder before its recompute draw, run_lt1_lt7.py:95-97, so no draw
   can reuse the production-prior rebuild through build_cutoff's DONE skip, which was my one mechanical worry). A
   single bad column or a row after t is a P4.1 stop ("stops E.33 until the code is fixed under 0.2"), so the
   verdict turns on the full count, not a sample.
2. No file in the freeze list's pipeline section changing after the evidence runs (the checked shas: feat33
   b216f11ee2df, build_features33 5bb65afb1689, lab33 e1c3c0163fb8, build_labels33 e0da4cf1996a, the rest as at
   12:20); any change re-opens this review for that diff.
3. The readings file finalised (Status line to final) and the final freeze list built after that last edit, checked
   with `verify --remeasure` and `check-proofs` (0 differences expected: the proof-pinned files are unchanged), the
   readings file's sha256 being a line of it (P0.2). The lead sends me the finished 2r file for the last check; the
   final list's `verify` output is the lead's.
GO here means the pipeline may be frozen (B7); C1 and the real-outcome fits stay behind the freeze and P4.1's
remaining items (LT2 on the full label store, LT7 again after the test list is hashed).

## (0) The readings file's new section (lines 194-208, 12:54 PDT)

R-L12 says what N21 asked and no more: the pre-freeze label tables are test inputs of prompt B3/B4, their values
enter equality comparisons and rule checks only under R-L2 (b), no statistic is reported and no fit or simulation
uses them, the production label store is built after the freeze and C1 under the frozen label code sha, and
b15c4ca10d68 is rebuilt if the frozen label code differs. Accurate to P10 line 856 and to what is on disk
(DERIVED/labels/b15c4ca10d68 holds the 20 B3 dates; the 178 LT dates are under DERIVED/b4/lt_labels/b15c4ca10d68,
178 F15 and 178 T30 tables, not under the production root). The data note states N22's counts as mine and marks it
"not a reading". Both fine.

## (1) LT1 prior = production: 200 of 200 clean

b4_runs/LT1_full_2b30cb0e953b.json: prior "production", draws_picked 200, no_production_table [], results 200 on
178 distinct dates, each with bad_cols [] and rows_after_t 0 (sums by me: 0 and 0); the (date, i, t_ns) set of the
results equals the draw's. Log: "200 checked of 200 picked (0 without a production table), 0 with a column outside
G7, 0 rows after t, 199 s", step 2p 12:44:57-12:48:16. The rebuilt row is build_cutoff's (all four streams truncated
at ts_recv <= t, D re-streamed, the 21 history dates' pass-1 tables from the LT folder), compared at G7 with the
production row and the rebuilt table required to hold no row after t (lt1_truncation.py 8-12, 58-64). The LT folder's
178 feature tables (DERIVED/b4/lt_features/2b30cb0e953b, step 1: 816 pass-1 dates, 178 pass-2, 1,399 s) are
byte-for-byte the production store's tables for those dates (my check: schema and every column of all 178 equal,
48,594 rows; _day sigma_zm equal on 178 of 178), so the production-prior comparison is against the production store
in substance as well as in code.

## (2) LT7: every count agrees with the definition

b4_runs/LT7_2b30cb0e953b.json (12:51:36, 132.8 s, 3 processes): draws 200 = draws_total; checks 3,620, decision_equal
3,620; decided_trades 259, fill_checks 259, fill_equal 259; fill_vs_table_checks 622, 0 mismatches; both_side_fill
724 / 724; entry_ok 362 / 362; skipped_not_in_grid 380; missing_inputs []; per_config 20 configurations, each summing
to 200 over the six reasons; reasons over all configurations: usable 3,400, usable_on_excluded_date 220, not_in_grid
380, the three missing-input reasons 0. The arithmetic closes against the draw: 20 x 200 = 4,000 = 3,620 + 380; from
the draw's i values 190 draws lie in G_15 (i <= 262) and 172 in G_30 (i <= 247), so entry_ok checks 190 + 172 = 362,
not_in_grid 10 x 10 + 10 x 28 = 380, both-side fills 2 x 362 = 724, and the 11 draws on P1.4-excluded dates give
11 x 20 = 220 "usable_on_excluded_date" pairs (both sides no trade). Against P4.1 lines 484-491: the seed-1 null
proof's 20 configurations (S5 x {FH15, TB30} x 10 grid points) at the 200 LT1 times restricted to each
configuration's grid G_h(D); the decision recomputed from all streams truncated at t (the LT1 rebuilt row, lab33
entry rules on ZM records truncated at t) equals the production decision (the label table's entry_ok and decide() on
the production row); the entry fill recomputed from streams truncated at the production fill time (t + L or the
fallback update) equals the production fill, on the decided side (259) and on both sides (724); the fold model is the
one whose OOF block holds t's date (`fold[d]`, lt7_causality.py); models read only. The harness adds the production
fill time against the table's entry_ns (622, 0) and entry_ok against the table (362, 0). B4_leakage.md line 35 states
the same numbers. No mismatch, so P4.1's stop does not fire.

## (3) Steps 1 and 3 under R-L2 (b)

The job log (logs/lt1_lt7_2b30cb0e953b.log, 11 lines: start 12:21:39, "code: features 2b30cb0e953b, labels
b15c4ca10d68", the four step lines, the LT7 count line) carries counts and seconds only; step 3's subprocess output is
reduced to ['done 178 dates'] (rc 0, 67 s). I grepped the log for any Sharpe, mean, net, P&L or return figure: none.
LT7_2b30cb0e953b.json holds counts and empty mismatch lists; LT1's JSON holds bad_cols, rows_after_t and seconds per
draw. The label tables are read by lt7_causality for entry_ok, long/short_entry_ns and i only (lt7_causality.py:
`columns=["i", "entry_ok", "long_entry_ns", "short_entry_ns"]`). No label value, class or net was read or written
anywhere I can see.

## (4) The draw

reports/stage_e33_briefs/work/LT1_draw.json (mtime 02:17 PDT, sha256 0a2193958ec4...): seed 20261027, n 200, the rule
stated in the file; I recomputed `default_rng(20261027).choice(796 x 273, 200, replace=False)` with date = OOF[idx //
273] (the 796 OOF dates taken from the production store's table names) and i = idx % 273: the 200 (date, i) pairs
equal the file's; LT1's results and LT7's draws (200 = draws_total) are that set, with t_ns equal on every draw.

## (5) 2r at 12:55

b4_runs/LT1_recompute_2b30cb0e953b.json: prior "recompute", draws_picked 200, results 8, rows_after_t 0, bad_cols
empty on all 8. The 12 `_lt1` folders present under the LT root are the recompute draws in progress; the 200
production-prior folders were removed at 2r's start (run_lt1_lt7.py:95-97) after LT7 had read them (step order
1, 2p, 3, 4, 2r), which is the right order.

### NOTE (Part 2b(ii-a))

N24. The recompute prior's evidence is one file that grows draw by draw and is rewritten at the end
(run_lt1_lt7.py step2); the production-prior rebuild folders it relies on for nothing are gone. When 2r finishes,
the lead's last check should confirm `draws_picked` 200, `len(results)` 200, the (date, i) set equal to the draw's,
rows_after_t 0 and bad_cols [] on every draw, and that each recompute folder held 22 pass-1 DONE markers (D and its
21 history dates re-streamed under the cutoff; a folder with only D's would mean the prior fell back to production).
Checked at 12:58 on the folders finished so far: 14 hold 22 pass-1 DONE markers and 1 (the first OOF date, which has
only 20 trade dates before it) holds 21, every marker carrying the folder's cutoff_ns; 3 folders were mid-build.
So the recompute prior is doing what R-L9 (b) says. I will repeat the count on the file the lead sends. Fix: none; a
record note.

# Part 2b(ii-b) (lead's message; written 14:16-14:20 PDT): LT1 prior = recompute finished; final verdict

Counts (2b(ii-b), new items): BLOCKING 0, SHOULD FIX 0, NOTE 0. Totals for this review (Phase 1, 2a, 2b(i), 2b(ii-a),
2b(ii-b)): BLOCKING 0, SHOULD FIX 0 new (the E.33 review's SF1-SF3 closed: SF1 by the readings file, SF2 by the freeze
tool, SF3 by R-B3-FD6 and full_r3), NOTE 14 (N11-N24), none of which conditions the freeze.

## Verdict: GO on the pipeline freeze (B7)

The condition of 2b(ii-a) is met. Recount by me at 14:16 on b4_runs/LT1_recompute_2b30cb0e953b.json: prior
"recompute", draws_picked 200, results 200, 200 unique (date, i), the set equal to LT1_draw.json's, no_production_table
0, rows_after_t 0 on every draw (sum 0), bad_cols empty on every draw; per-draw seconds 55-129 (median 73). Log:
"step2 LT1 recompute: 200 checked of 200 picked (0 without a production table), 0 with a column outside G7, 0 rows
after t, 5033 s", "step 2r done 14:15:29", "rc=0 end 2026-10-28 14:15:30 PDT". Folders: 200 under
DERIVED/b4/lt_features/2b30cb0e953b/_lt1, their names equal to the draw's 200 t_ns; pass-1 DONE markers 22 on 199
folders and 21 on 2020-12-30 (the first OOF date, 20 trade dates before it), every marker carrying its folder's
cutoff_ns, and every folder holding D's pass-2 DONE and table. R-L9 (b), the literal P4.1 text, is satisfied on all
200 draws, with (a) beside it (2b(ii-a) (1)).

No pipeline-section file changed after the evidence runs. At 14:16 every executed file carries the sha it had when
the jobs ran and the dry run hashed it: feat33 b216f11ee2df (mtime 09:15:18), build_features33 5bb65afb1689 (09:26:20),
lab33 e1c3c0163fb8 (09:42:45), build_labels33 e0da4cf1996a (09:26:25), cal33 f054788ee5ca, data33 8295a6ee26e5, guard33
782929fed014, search33 a7d30b2a6786, run_search33 d44fb7c16e55, select33 9b9928066a35, synth33 5a5ed5b91f09,
run_proofs33 4a0f4e9825cd, cost33 505f52524aad, split33 b8c3a96afb13, check33 93abc1361c78, g6_33 bf1f3d2e5961 (all
mtimes 10-27 or before 09:43 on 10-28); mbo_book31 619622865fff, measure31 61ff83fd6683, measure31_core 2277a92c0f30,
kalgo31 ca2016e7eed6 (10-23); p7_final 3db06f1276bf, p7_thresholds 5d3590197bbc (10-27); screening/stage_e_verdict
54e10a296f49, funnel/multiple_comparisons 6666cf229b98, uv.lock 7fecbfa47327, the protocol c4ffb9d79af4. `sha256sum -c`
of the whole dry-run list against the files now fails only on the ten documents and harness files already named in
N15/N17 (the readings file, four readings notes, timing_featB.md, lt2_span, lt7_causality, run_lt1_lt7,
run_synth_features, synth_streams), none of them executed by the search; the only files in the list modified after the
LT job started at 12:21:39 are reports/stage_e33_protocol_readings.md (12:54:08, the R-L12 and data-note section) and
work/TestCoder_readings.md (14:15:57, the TestCoder's closing note).

What GO covers and what it does not. It covers the code the search executes and its inputs as hashed, the two
implementations' agreement, the leakage tests LT1-LT7 as run, the proofs, and the readings file's content. The freeze
itself is the lead's act under P0.2 and P7.1: finalise the readings file (its Status line), build the list after that
last edit, run `verify --remeasure` and `check-proofs` on it (0 differences expected: no proof-pinned file changed), and
quote the readings file's sha256 from the list. Any edit to an executed file after this verdict re-opens the review for
that diff. Still ahead of C1 and outside this verdict: LT2 on the full label store built under the frozen label code,
LT7 again after the test list is hashed (P4.1), and the P10 sequence for labels, fits and simulations.
