# PostStop_b (independent check of the E.33b return after the P10 stop; PipelineReviewer-FableXHigh)

Written 16:11-16:20 PDT 2026-10-28 (times from `date`). Brief: the lead's message after the stop. Outcome seal kept:
under derived/e33/search/ I opened only DONE status fields, fold*.DONE, fold*.attempts, names, sizes and counts; no
stats.json, daily/trades/not_made parquet, fold*.npz, fold*.model.json or fold*.timing.json, and no outcome statistic
was computed or read. Everything else comes from the logs, STATE, the ledger, the label store's exclusion records
and the feature store's markers. Light work only (nice 10, one process).

Counts: 38 items CONFIRMED, 1 DIFFERS (a wording misattribution, D1). Language: BLOCKING 0, SHOULD FIX 2, NOTE 3.

## (1) P5 projection (STATE "P5 PROJECTION", 14:18:35; protocol P5 lines 596-606)

- CONFIRMED Builder probe inputs: work/logs/p5_builder_probe_e33b.log lines 3, 5, 7: 2022-02-15 3.65 s, 2022-07-27
  5.41 s, 2021-05-07 5.66 s, code_sha12 2b30cb0e953b, start 14:17:20, end 14:17:35; mean 14.72 / 3 = 4.9067 s
  (STATE "4.907").
- CONFIRMED Fold-6 probe inputs: work/logs/p5_probe_e33b.log lines 3-4 (14:16:31 "E33-S5F15L100E fold 6: 6.6 s (1 thr,
  160896 train rows)", 14:16:33 "E33-S5F15G3050 fold 6: 1.1 s (4 thr, ...)"); the timing files
  proofs/seed9000/probes/search/<cid>/fold6.timing.json: L100E wall_seconds_incl_mu 6.598577 (seconds 6.5771, 41
  iterations, converged, 664 train dates, 160,896 rows), G3050 1.079396 (best_iteration 2, 52 rounds). STATE's
  "6.5986 s incl. mu" and "6.60 / 1.08" match. Fold 6 is P5's "largest training set, 664 dates".
- CONFIRMED P_b 4 / P_L 8 / P_G 2: the builder's MAX_PROCS is 4 (build_features33.py:51, INTERFACE 2.4); the thread
  cap 8 gives 8 single-thread LOGIT processes and 2 four-thread LGBM fits; P5 line 600 asks for "the process counts
  the thread cap of this section allows".
- CONFIRMED Arithmetic: 796 x 4.9067 / 4 = 976.4; 1,080 x 6.598577 / 8 = 890.8; 720 x 1.079396 / 2 = 388.6; sum
  2,255.82 s (STATE 2,255.8; 37.60 min); 3 x 2,255.82 = 6,767.45 s, written as 6,767.5 (the watcher's REF_3X;
  the rounding is 0.05 s against a crossing margin of 7.3 s).
- CONFIRMED Written before the first real-outcome fit: the block header says 14:18:35; the probes ran 14:16:21-14:17:35;
  the search log's first line is 14:29:03,603 ("registration checked for 300 ids") and the first fold tasks at
  14:29:04; the earliest attempt `start` across all 448 attempt records is 14:29:04 PDT.
- Not re-derived: that the three builder dates are F 5's median, p90 and maximum ZM message-count dates (the E.33
  lead's identification; the protocol names the rule at line 597, not the dates; open choice 11 says E.33 timed the
  same dates).

## (2) Measured feature build 2,387 s

- CONFIRMED The store's DONE markers (features/2b30cb0e953b, _p1/*.DONE and *.DONE, 1,632 markers) fall in two runs
  separated by one gap > 5 min: run 1 09:28:58.281-09:54:35 (1,537.3 s, 348 markers), gap 09:54:35-12:26:00
  (9,085 s), run 2 12:26:00-12:40:11.190 (850.4 s, 1,284 markers). Sum 2,387.7 s; the lead's 2,387.0 (p10_watch.py
  BUILD_S) rounds it down by 0.7 s, which does not touch the crossing (6,774.8 vs 6,767.5). First-to-last literal
  span 11,472.9 s = 191.2 min (return: "191 minutes").
- CONFIRMED Open choice 12 is stated fairly: it gives the lead's reading (sum of the two runs, the idle gap excluded),
  the literal reading (first to last marker, 191 minutes, which "would have exceeded the 3x reference before the
  first fit"), and that neither changes the outcome. One point for the record (N1 below): P5 line 604-606 nets out
  only "the pauses the STATE file logs (usage-limit waits, reboots)"; the 09:54-12:26 gap was neither, so the
  literal text would have stopped the search at 14:29:04 with 0 fits. The return says this in substance.

## (3) The stop

- CONFIRMED work/logs/p10_stop.json: first_fit 14:29:04, pause 15:34:05-16:00:05, pause_s 1,560.0, fits_net_s
  4,387.8, build_s 2,387.0, measured_s 6,774.8, reference_3x_s 6,767.5, stop_time 16:08:11, killed_with SIGTERM.
- CONFIRMED Against work/logs/search_real.log (965 lines): line 732 "15:34:05,310 ... pausing submissions", line 733
  "16:00:05,331 ... collector window over: resuming" (1,560.02 s); first fit 14:29:04. 16:08:11 - 14:29:04 = 5,947 s;
  minus 1,560 = 4,387 s at second resolution (the watcher's 4,387.8 uses its fractional clock); plus 2,387 = 6,774
  to 6,774.8 > 6,767.5. The crossing (fits net > 4,380.5 s) fell at 16:08:04.5; the watcher checks every 10 s, so
  16:08:11 is its next check, as the return says.
- CONFIRMED The watcher reports/stage_e33_briefs/work/lead/p10_watch.py (2,993 bytes, 14:46): BUILD_S 2387.0,
  REF_3X 6767.5, START 14:29:04; the pause taken from the two log lines; measured = BUILD_S + (now - START - pause);
  SIGTERM to the process group, SIGKILL after 30 s if still alive; writes p10_stop.json; exits early if the log shows
  "rc=" or the group is gone. Outside the selection pipeline; reads nothing but the log.
- CONFIRMED Nothing left running: `ps` at 16:11 shows no run_search33, search33, p10_watch, build or proof process.
- DIFFERS D1 "the search log closes with rc=0 at 16:08:12" (return 3.6; STATE 16:10 line "search log rc=0 at ...").
  search_real.log has no "rc=" line; its last line is 16:08:07,494 "start E33-S1F30L100A fold 4 (1 thr; pid 2625976;
  7991 MB available)". The "rc=0 16:08:12" line is p10_watch.log line 2, the watcher's own exit after the kill. The
  runner was ended by SIGTERM and wrote no closing line. Fix: "the watcher's log closes with rc=0 at 16:08:12; the
  search log's last line is a fold start at 16:08:07".

## (4) What ran

- CONFIRMED 76 directories under search/: 60 S5, 15 S1, _logs. DONE status "ok" 72; no DONE 3 (+ _logs); failed 0.
- CONFIRMED The 72: all 60 S5 and S1F15 G2050, G2200, G3050, G3200, L001A, L001E, L010A, L010E, L100A and S1F30 L001A,
  L001E, L010A (the return's list exactly).
- CONFIRMED Partial (3): E33-S1F15L100E (fold 3 cut), E33-S1F30L010E (folds 3, 5, 6), E33-S1F30L100A (folds 1-4):
  8 attempt records without a DONE = the 8 interrupted attempts; 448 attempt records = 440 DONE + 8; 0 stray
  attempts in any ok configuration. fold*.DONE count 440; "440 of 1,800 fits". No S2, S3 or S4 directory.
- CONFIRMED Fold times from the search log's 440 "fold n done X s" lines (no outcome in them): S5 LOGIT n 216 mean
  109.3 max 654.2; S5 LGBM n 144 mean 5.0 (max 14.2); S1 LOGIT n 56 mean 37.9 (max 230.0); S1 LGBM n 24 mean 2.0;
  E33-S5F15L100E fold 6 227.4 s (also fold6.DONE seconds 227.447, 14:37:33); E33-S5F15G3050 fold 6 2.6 s. 227.4 /
  6.6 = 34.5 ("34 times").
- CONFIRMED P5's formula with the real fold-6 times: 976.4 + 1,080 x 227.4 / 8 + 720 x 2.6 / 2 = 32,611.4 s = 9.06 h.
- CONFIRMED S5 wall: last S5 fold done 16:01:01,968 = 91.95 min after 14:29:04; net of the 1,560 s pause 66.0 min
  (return "65.9", truncation). S1: 80 folds between 16:01:04 and 16:08:07 = 11.35 a minute (10.0 a minute counted
  from the pause end), "about 11".
- CONFIRMED Remaining estimate: 1,360 folds at 11 a minute = 2.06 h; at 9 and 12.5 a minute 2.52 and 1.81 h ("about
  2 hours (1.8-2.5)"). It assumes S3/S2/S4 run at S1's pace, which the return states ("at that pace").
- CONFIRMED Every ok configuration holds DONE, fold1-6 .DONE/.attempts/.model.json/.npz, daily.parquet,
  trades.parquet, not_made.parquet, stats.json (names only, E33-S5F15L001A listed).
- CONFIRMED (open choice 18) search/_logs holds 13 logs: 12 of size 0 (six of 10-27 15:06-15:25, four of 10-28
  02:03-02:24, run_20261028_091637 and run_20261028_122056) and the real run's run_20261028_142903_2625953.log
  (82,509 bytes = search_real.log). The two named ones fall inside my pytest runs of 09:14:30-09:17:39 and
  12:20:17-12:21:13. "No configuration folder existed before 14:29": consistent with the files (earliest attempt
  start 14:29:04; earliest directory ctime 14:30:34), not provable from ctime alone.

## (5) The frozen code

- CONFIRMED All 448 attempt records carry pipeline_sha 323a82ff96ca...; E33-S5F15L100E/fold6.DONE carries the same.
  Recomputed from the final freeze list reports/stage_e33_pipeline_freeze.sha256 (227 lines; guard33 782929fed014,
  run_search33 d44fb7c16e55, search33 a7d30b2a6786) with search33._pipeline_sha's rule: 323a82ff96ca. The freeze
  list's own sha256 eb565a37f814 is the one cited in the ledger note and in reports/stage_e33_c1_freeze.json
  (pipeline_sha256 eb565a37...; protocol c4ffb9d7...; readings da58c77f..., the list's entry for the readings file).
  reports/stage_e33b_briefs/freeze_verify_end.txt (16:12): "227 files + 4125 derived inputs, 0 difference(s)
  (remeasured)".

## (6) N

- CONFIRMED ledger/trial_registrations.jsonl line 10: entry_id r009-E33, n_before 538, n_after 838, test E33, 300
  test_ids, freeze_path reports/stage_e33_c1_freeze.json. `python -m screening.trial_registry status`: "N = 838
  (10 lines)"; r009-E33 is the last line. (No field named current_n exists in the files; current_n() is the
  registry function the status command prints.)

## (7) Rule 5 on the 796 dates (work/rule5_count_796.txt)

- CONFIRMED Recounted from labels/b15c4ca10d68/<label>/_excl/<date>.json (796 files per label; counts only):
  F05 98 dates, 15,315 / 15,109 of 217,308; F15 and T15 98, 14,645 / 14,400 of 209,348; F30 and T30 96, 13,659 /
  13,355 of 197,408; F60 95, 11,766 / 11,350 of 173,528; r5_locked_span (rows_removed_by_rule) 0, r5_book_at_t 0,
  limits_none 0, excluded dates 49, on every label. Equal to the file and to return 3.9 in every cell.
  15,315 / 217,308 = 7.05 percent, 11,766 / 173,528 = 6.78 percent ("about 7%").

## (8) Language (return sections 1, 3.6-3.9, 6, 7)

Every number in those sections matches the files above. Claims checked and found supported: the stop under P10 at
16:08:11; N 538 -> 838 and r009-E33 at 14:23:13 (ledger); B3 0 cells, LT1 both priors, LT2-LT7, the 40 proofs 0/20
and 20/20, "PipelineReview (Fable) gave GO with 0 BLOCKING" (PipelineReview_b.md, mtime 14:17:14, the time the
readings status line cites); 72/0/3, 440 of 1,800, S3/S2/S4 not started; 37.6 min projected and 3x; 227.4 against
6.6, 34 times; "no outcome statistic ... read" true as far as the files show (the search log has 0 outcome words,
no selection or summary file exists under search/, STATE and the return carry no outcome figure, and this check
opened none); rule 5 95-98 dates, 11,766-15,315 minutes, about 7 percent; "about 2 more hours"; D1 (a)'s "per-fold
wall times in work/logs/search_real.log, which hold no outcomes" (true: fold done lines carry seconds only); D1's
"N stays 838" (the registration is on the ledger). Open choice 24's "14:17:14" equals the review file's mtime.

### BLOCKING

None.

### SHOULD FIX

SF1. Return 3.9 ends with the placeholder "Recount: «R5CHECK»". Replace with the result above (every cell equal,
PostStop_b.md section 7) before the return is read as final.

SF2. D1 above: return 3.6 and the STATE 16:10 line attribute "rc=0 at 16:08:12" to the search log; it is the
watcher's log line. The search log ends at 16:08:07,494 with a fold start and no rc line (the runner died on
SIGTERM). One sentence.

### NOTE

N1. Open choice 12 could say in one more clause what the literal P5 text would have done: netting only logged
usage-limit waits and reboots, the measured build would be 11,472.9 s and the 3x reference would have been exceeded
at the first fit, so under the literal reading no real-outcome fit would have run. The return says the reference
"would have exceeded ... before the first fit"; the consequence (zero fits rather than 440) is implied, not stated.
Neither reading selects anything, as the return says.

N2. "Saga converges far more slowly on the real features" (section 1) and "saga convergence, not table size, sets the
LOGIT cost" (open choice 22) are inferences from the time ratio (34x at equal rows). The iteration counts that would
make them facts are in search/<cid>/fold6.timing.json (n_iter, converged; no outcome in that file), which the seal's
allowed list did not name, so I did not open it. If the lead cites n_iter from it, the sentence stands as fact;
otherwise "took 34 times longer" is the supported form.

N3. "no configuration folder existed before 14:29" (open choice 18) is supported by the earliest attempt start
(14:29:04) and the empty earlier logs, not by a creation time; ctime cannot show it. Wording as it stands is fair;
"no fit record predates 14:29:04" would be the provable form.
