# AmendReview_c: adversarial review of protocol version 0.3 before the hash (Stage E.33c, S2)

Reviewer: AmendReviewer-FableXHigh (model claude-fable-5-1, independent of the lead). Written 2026-10-28 18:32 PDT
(review ran 18:23-18:32 PDT by `date`). Brief: reports/stage_e33c_briefs/brief_AmendReviewer_c.md.
Outcome seal kept: no file under /mnt/large-storage/market_data/PropExperiment/derived/e33/search/ was opened or
stat-ed by this reviewer. Own code: scratchpad recompute_r03.py (parser and arithmetic written here, the lead's
project_ref_v03.py neither imported nor run) and scan_inputs.py (prints tool-call inputs only).

Verdict: GO for hashing version 0.3. Findings: 0 BLOCKING, 0 SHOULD FIX, 9 NOTE.

## Check 1. Scope of the diff: CONFIRMED

- v1.0 sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05 (matches the brief); v0.3 as reviewed
  a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246 (895 lines; v1.0 865).
- My own `diff -u`: 3 hunks, 5 lines removed, 35 added. Body identical to the lead's
  reports/stage_e33c_briefs/protocol_v0.3.diff (headers aside).
  1. v1.0 lines 3-5 -> v0.3 lines 3-8: the Status paragraph (brief item a).
  2. v1.0 after line 606 -> v0.3 lines 610-636 inserted: inside P5's "Probe and compute stop" bullet (v1.0 596-606,
     under "## P5. Models (two families) and compute", "### Compute estimate" at 578); the next bullet "- Every long
     job" is unchanged (brief item b).
  3. v1.0 lines 838-839 -> v0.3 868-869: the P10 stop clause that names the reference (under "## P10. Stop rules and
     the null report", v1.0 line 830) (brief item c).
- Every other line byte-identical: `diff` of v1.0 minus lines 3-5, 838-839 against v0.3 minus lines 3-8, 610-636,
  868-869 is empty.
- make_v03.py (reports/stage_e33c_briefs/tools/make_v03.py:53-57) asserts each of the 3 old blocks occurs exactly once
  and replaces it; it reads only the v1.0 file.

## Check 2. No outcome was read to make it: CONFIRMED

(a) Inputs carry wall times only.
- Runner log statements (reports/stage_e33_briefs/work/pipeline/run_search33.py): 81 "registration checked for %d
  ids"; 158/161 collector-window pause and resume; 218 "%d fold tasks to run"; 244 "start %s fold %d (%d thr; pid %d;
  %d MB available)"; 272 "%s fold %d done %.1f s"; 274 "FAILED FIT: %s" (error string; 0 in this log); 149
  "%s finalized (%s) in %.1f s"; 284 "finished: ..." (counts and ids); 365 "manifest %s" (argv, env, ids, versions).
  Nothing prints a statistic, loss, prediction or iteration count.
- The seconds on a done line bracket the fit call only: search33.py:563 `t0 = time.perf_counter()` ... :568
  `meta["seconds"] = time.perf_counter() - t0`, with fit_logit/fit_lgbm between (table slicing and class means lie
  before t0). Fit statistics (n_iter, converged, best_iteration, ...) go to the config DONE marker
  (search33.py:975-980), not to the log.
- Log census (965 lines, ids and numbers masked): 15 line shapes, all of the forms above; 448 start, 440 done,
  72 finalized (ok), 2 collector-window, 3 header lines; 0 unmatched lines. The Haiku parser's summary
  (fold_times_summary.md) reports the same 440/8/72/0.
- The other three inputs: p5_builder_probe_e33b.log holds 3 JSON lines with "wall_s" and info key names;
  p10_stop.json holds times and the two measured parts; trial_registrations.jsonl holds ids.
(b) The projection script (project_ref_v03.py:39-42, 86, 91, 95-96, 113-116) opens: search_real.log,
  ledger/trial_registrations.jsonl, p5_builder_probe_e33b.log, p10_stop.json, and, when the optional third argument is
  given (it was: ref_v03.json carries haiku_csv_check), the Haiku fold_times_real.csv (sha256 00ff98e0..., itself
  parsed from the log), plus its own source for the self-hash. No path under derived/e33/search; no outcome file.
  NOTE 1: that is five inputs plus itself, not "four"; the fifth is log-derived. The brief's wording, not the
  protocol's, is what differs.
(c) Lead transcript 7c6136a3...jsonl (170 assistant messages, 69 tool calls): 9 tool-call inputs name an outcome file
  or the search directory, none reads content:
  - 18:10:45 `findmnt -no OPTIONS -T .../derived/e33/search` (mount options);
  - 18:10:56 `ls | head -3; ls | wc -l; find E33-S5F15L100E -printf '%P %s %TT %AT'` (names, sizes, times);
  - 18:11:10 `find E33-S5F15L100E -maxdepth 1 -name stats.json -o ... -printf 'M %TT A %AT C %CT'` (stat times
    only), then a grep of search33.py;
  - 18:12:11 writes scratchpad/tools/scan_outcome_reads.py (the names appear in its regex);
  - 18:12:47 reads the E.33b PostStop reviewer's transcript (the names in a filter);
  - 18:13:01 writes and runs scratchpad/tools/atime_census.py: `os.stat()` on each outcome file, no open (I read the
    script text from the tool input), output reports/stage_e33c_briefs/atime_census_start.txt;
  - 18:22:23, 18:22:41 Write of my brief (seal text); 18:22:52 the Agent call that spawned me.
  Subagent agent-aadd39ce6b99390fc (FoldTimes-Haiku): 10 tool calls, 0 hits. Subagent agent-aeb4add165385635d is
  this reviewer: 1 hit, my own scan_inputs.py Write.

## Check 3. Independent recompute of R_0.3: CONFIRMED (every value identical, difference 0.0 s)

Parsed from search_real.log with my own regexes (done lines `INFO <id> fold k done <s> s`; start lines
`INFO start <id> fold k (`), ids from ledger/trial_registrations.jsonl entry r009-E33 (300, unique):

| quantity | mine | lead (ref_v03.json / 0.3 text) |
|---|---|---|
| folds done before the stop | 440 | 440 |
| folds cut (started, no done line) | 8: S1F15L100E f3; S1F30L010E f3,f5,f6; S1F30L100A f1-f4 | same 8 |
| folds not started | 1,352 | 1,352 |
| S5 cells (label, grid, fold) measured | 360 | 360 |
| rho_LOGIT (cells; S1 sum / S5 sum) | 0.492659 (56; 2,124.0 / 4,311.3) | 0.492659 (56; 2,124.0 / 4,311.3) |
| rho_LGBM (cells; sums) | 0.707670 (24; 48.9 / 69.1) | 0.70767 (24; 48.9 / 69.1) |
| B = 796 x mean(3.65, 5.41, 5.66) / 4 | 976.43 s | 976.43 s |
| LOGIT fold sum (measured 25,726.7 + projected 50,455.1) | 76,181.8 s | 76,181.8 s |
| LGBM fold sum (measured 770.7 + projected 2,260.8) | 3,031.5 s | 3,031.5 s |
| R_0.3 = B + LOGIT/8 + LGBM/2 | 12,014.9 s | 12,014.9 s |
| 3 x R_0.3 | 36,044.7 s | 36,044.7 s |
| measured at the 0.2 stop (build 2,387.0 + fits net 4,387.8) | 6,774.8 s | 6,774.8 s |
| allowance for the resumed run's fits, net of pauses | 29,269.9 s | 29,269.9 s |
| projected part (1,360 folds): 50,455.1/8 + 2,260.8/2 | 7,437.3 s | 7,437.3 s |

Per-set sums (S1 LGBM 48.9+461.9, S1 LOGIT 2,124.0+9,504.1, S2 577.4/13,144.8, S3 599.6/13,650.4,
S4 621.8/14,155.9, S5 721.8/23,602.7) also equal the JSON's per_set_model. Feature counts verified from the frozen
module: search33.SETS lengths S1 23, S2 26, S3 27, S4 28, S5 59; GRID is the 10 names the log shows.

## Check 4. The text alone: CONFIRMED reproducible, with small gaps (all NOTE)

A reader with the log (its sha256 is in the text), the 300 ids and the protocol's id scheme can reproduce R_0.3: the
formula, B with its three probe times, t_f for measured folds (the done-line seconds), t_f for the rest
(t_S5(l,g,k) x rho_m x n_s / 23), n_s per set, rho_m as a ratio of sums over the finished S1 cells with the cell
counts given, and P_b, P_L, P_G are all stated. Gaps:
- NOTE 2: the text does not say how a "cut" fold is told from a "not started" one (a start line without a done
  line). Both get the same projected t_f, so the value is unaffected; the 8/1,352 split is only a check figure.
- NOTE 3: the decomposition of an id into set, label, grid and family (E33-S5F15L100E -> S5, F15, L100E, LOGIT by the
  grid's first letter) is not restated in the bullet; it rests on the protocol's id scheme elsewhere and the example
  on v0.3 line 601. Unambiguous in practice (all 300 ids parse the same way).
- NOTE 4: rho is quoted to 6 decimals; using the rounded values moves the fold sums by under 0.1 s, so the quoted
  R_0.3 is reproducible from the text's own numbers as well as from full precision.
- NOTE 5: v1.0 asked that the reference be written to the STATE file "with the probe times and this formula"; the
  0.3 sentence says only "R_0.3 is written to the STATE file" and points to ref_v03.json for the parts. Enough,
  since the parts are in the protocol text itself.

## Check 5. Fidelity to V53 and the prompt: CONFIRMED

- V53 item 1 (DECISIONS.md:1096-1102): one amendment, for r009-E33 only, reference projected from the real per-fold
  wall times in search_real.log (timings only), 3x stop kept, hashed before the resume, nothing else changed. The
  0.3 Status paragraph and the P5 insertion both name V53 and r009-E33; the 3x factor is kept (P5 text and P10 clause);
  the two other hunks are the version line and the P10 clause that names the reference (prompt S2 bullets 1-3).
- Measured wall time keeps its v1.0 definition: v0.3 line 627 "The measured wall time compared with it is the one
  defined above" (the two parts of v0.3 lines 605-609, net of STATE-logged pauses). The 0.2 run's parts (2,387.0 +
  4,387.8) carry forward; the stop-to-resume interval is declared a logged pause (line 628-629); the resumed run's
  own pauses are netted the same way.
- P10 (v0.3 868-869) now names "the reference of P5's compute stop (in version 0.3, R_0.3, written to the STATE file
  before the resumed search's first fit)", coherent with P5. The one other projection in the protocol, the C3
  set-start rule (v0.3 875-877), uses its own running-mean formula tied to the 07:00 deadline that V52 lifted and
  does not name the P5 reference; it needs no edit.
- NOTE 6: procedural conditions the text itself sets for S3, not defects: R_0.3 (and 3 x R_0.3) must appear in the
  STATE file before the resumed search's first fit, and the STATE file must log the 16:08:11-to-first-fold interval
  as a pause. Neither is in reports/stage_e33_STATE.md yet (the E.33c section ends at the 18:16 entries). Out of this
  brief's scope but checked for coherence: tools/p10_watch_v03.py uses SO_FAR_S = 6774.8 and STOP_AT_S = 36044.7
  and nets collector-window pauses from the resumed log, which matches the 0.3 wording.
- NOTE 7: v0.3 line 10 still says "E.33 runs this protocol unchanged"; literally stale under an amendment, but
  changing it would breach "nothing else changes". Leave it.
- NOTE 8: the text's build part 2,387.0 s is p10_stop.json's value (the watcher's constant); the E.33b PostStop
  verifier measured 2,387.7 s. The text cites p10_stop.json, so it is internally consistent; 0.7 s is immaterial.

## Check 6. Judgment on wall times: a defensible projection, not tuned either way

Pace evidence (log timestamps and p10_stop.json only):
- S5: 360 folds from 14:29:04.1 to the last S5 done line 16:01:01.97 = 91.96 min wall, 65.96 min (3,957.9 s) net of
  the 1,560 s pause; ideal-parallel sum 23,602.7/8 + 721.8/2 = 3,311.2 s; efficiency 1.195.
- Whole 0.2 run: fits net 4,387.8 s against the measured folds' ideal-parallel 3,601.2 s: efficiency 1.218 (the S1
  tail 16:00:56-16:08:11 includes the 8 cut folds' lost work).
- Remaining 1,360 folds: ideal projection 7,437.3 s; at the measured efficiency about 9,060 s (2.5 h), inside the
  E.33b return's 1.8-2.5 h estimate (RETURN 3.7). Allowance 29,269.9 s (8.1 h): the stop fires only if the resumed
  run is about 3.2x slower than the pace measured so far (3.9x the ideal projection). That is a working guard
  against a pathological slowdown (memory pressure, S2-S4 saga runs far beyond S5's) and not inert; it is also not
  set to fire at the expected pace.
Assumptions I would name (none changes the verdict):
- Linear feature-count factor n_s/23 on an S1-based time. Sensitivity with my own code: S1-to-S5 interpolation of the
  per-cell factor gives R 11,657.4 s (-3.0%); per-grid-point rho (LOGIT 0.34-0.65, LGBM 0.58-0.81, 5-12 cells each)
  gives 12,615.9 s (+5.0%). The lead's choice sits between two defensible alternatives; the whole choice set moves R
  by at most about 5%, so there was no room to tune the stop.
- rho pooled over the S1 cells that finished: 45 of 56 LOGIT cells are L001/L010 (the faster grid points), only
  F15 and F30 labels, and the slow L100E has 5 cells. Time-weighted pooling is the right estimator for a sum; the
  per-grid alternative above bounds the effect.
- Ideal-parallel sums (fold sum / P) ignore scheduler imbalance (measured 1.2x). This is v1.0's own convention, and
  the 3x factor absorbs it.
- B stays the projected 976.43 s although the build measured 2,387 s: faithful to v1.0 (projection against
  measurement), and in the direction that makes the stop more likely, not less.
- NOTE 9: because 3x applies to the whole R while 6,774.8 s is already spent, the remaining part effectively gets
  3.9x its projection. A "3x on the remaining part" reading would give 22,312 s (6.2 h), still about 2.5x the
  realistic pace. V53 says "keep a 3x stop against the new reference", which the text does; this is for the
  user's awareness, not a change.

## Findings by level

- BLOCKING: none.
- SHOULD FIX: none.
- NOTE: 1 (five inputs plus itself, not four), 2 (cut vs not-started not defined; no effect), 3 (id scheme rests on
  the protocol elsewhere), 4 (rounded rho reproduces R within 0.1 s), 5 (STATE entry wording), 6 (S3 conditions:
  write R_0.3 to STATE and log the pause before the first resumed fit; watcher constants match), 7 (line 10
  "unchanged" is stale but must stay), 8 (2,387.0 vs 2,387.7 build), 9 (3x on the whole gives 3.9x on the rest).

## Verdict

GO: hash version 0.3 as it stands (sha256 a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246 at review
time). The diff touches only the Status paragraph, P5's compute-stop bullet and the P10 clause that names it; every
input is a wall time; the lead's tool calls read no outcome content; R_0.3 and every derived number recompute
identically from the log; the method is faithful to V53 and robust to its own assumptions within about 5%.
