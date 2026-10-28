# Stage E.33b return: ZM discovery search (continuation), stopped by the protocol's compute limit

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh, Ultracode on; session b8cfc9d8-3e96-415a-a441-462542346e80.
Launched 2026-10-28 09:05 PDT; times are America/Vancouver, from `date`, file mtimes, log stamps and transcripts.
Prompt: docs/prompts/STAGE_E.33b.md, under docs/prompts/STAGE_E.33.md (rules, gates, sections; not its times) and
docs/DECISIONS.md V20-V52. Protocol: reports/stage_e32_discovery_protocol.md FROZEN v1.0, sha256
c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05 (verified at start, in the freeze and at the end).

## 1. Summary (E.33 and E.33b together)

The frozen ZM discovery protocol was built twice, proved on synthetic data, frozen, registered and started on real
data. The search stopped at 16:08:11 PDT under the protocol's compute limit (P10's 3x rule; protocol 0.2: stop and
report). Nothing was selected.

- N: 538 before, 838 after (r009-E33, 300 configurations, 14:23:13 PDT).
- Part B: both implementations agree on all 59 features, 6 labels and sigma on the 20 B3 dates (0 cells). LT1 (200
  draws, both priors) and LT2-LT7 pass. Synthetic proofs: the null put nothing in Tier A in 20 of 20 seeds; the plant
  entered Tier A in 20 of 20. PipelineReview (Fable): GO, 0 BLOCKING.
- Run: 72 of 300 configurations finished (all of S5, 12 of S1; 440 of 1,800 fits), 0 failed, 3 partial; S3, S2 and
  S4 never started. The limit (37.6 minutes projected, stop at 3x) came from a synthetic probe. On real data the
  probe configuration's fold 6 took 227.4 s against 6.6 s synthetic (34x), most likely from slower convergence.
- Null comparison, finalists, clean negative: none. P8 selects over all 300, so a partial run cannot be selected
  from. No outcome of a finished configuration was read, so a decision to continue stays blind to results.
- Rule 5 (V52): its limit part removes minutes on 95-98 of 796 dates (about 7% of grid minutes).
- E.34: nothing to buy or test yet.
- Next: decision D1, a user amendment of the compute limit, then a resume of the same registration from the DONE
  markers (about 2 more hours of fits).
- Lead errors: a 2-hour wait (10:18-12:16) on a worker that had stopped mid-build, and no warning before C1 that the
  3x allowance was below every earlier estimate of the fit time (section 6, items 25-26).

## 2. Guardrail evidence

Start (09:06-09:07; reports/stage_e33b_briefs/checks_start.txt, verify_discovery_hashes.out, guard_dry_check_start.txt):
protocol sha256 c4ffb9d7 matches; data.holdout status all_ok with unlocks_logged 0 on all 6 stores; soy seal 114/114;
REGISTRATION.md 0 bytes; harness v14 preflight ok (2e908c81); ledger/databento_spend.jsonl 37,290 lines, sha256
42589d7b; N 538; DATABENTO_API_KEY3 present (checked by name only, never printed); discovery hashes 156/156; data
manifests 09396842 x4; the guard dry check refused 4 of 4 forbidden reads.

Before C1 (14:22-14:23): V52 records E.32 D1 = KEEP (docs/DECISIONS.md:1078-1080); N 538; holdout all_ok,
unlocks_logged 0; REGISTRATION.md 0 bytes; PipelineReview GO (14:17:14); readings file FINAL; freeze verify
--remeasure 0 differences (227 files and 4,125 derived inputs); check-proofs 0 differences and 0 weak.
After C1: require_registered(300 ids, test E33) ok; run_search33 re-checked the registration at launch.

End (16:11-16:13; reports/stage_e33b_briefs/checks_end.txt, guard_dry_check_end.txt, freeze_verify_end.txt,
pytest_end.txt): data.holdout status all_ok with unlocks_logged 0 on all 6 stores; soy seal 114/114 (state sealed,
no plaintext in the window); REGISTRATION.md 0 bytes; harness preflight OK (2e908c81); N 838 (r009-E33 the last
line); protocol sha256 c4ffb9d7; freeze file sha256 eb565a37; the guard dry check refused 4 of 4; freeze verify
--remeasure 0 differences on 227 files and 4,125 derived inputs; DATABENTO_API_KEY3 present by name. Full suite
(`uv run pytest -q -p no:cacheprovider`, nice 10, started with 12.3 GB available, 2 GB guard): 16:13:01-16:32:22, 1 failed, 8,116 passed, 5 skipped, 3 xfailed (1,157 s), available memory
at least 11.7 GB. The one failure is tests/test_h6_rod_run.py::test_the_lead_set_constants_and_the_cli_refuses_a_wrong_freeze_sha,
the known failure that predates E.32 (E.32 D7; harness v13), with the same counts as E.33's end run. No worker,
job or shell of this stage runs at the end (checked before the commit).

Scope: no Databento call (the spend ledger is unchanged at the end: 37,290 lines, sha256 42589d7b; per-account spend as at the start); no read of the test window (2017-05-01
to 2020-11-30) or of anything dated 2024-03-01 or later (guard33; data 2020-12 to 2024-02); the protocol is
unchanged; no pipeline file changed after the freeze (verify --remeasure at 16:12, 0 differences); nothing under live/ or ops/, no TopstepX or
ProjectX; no key printed or logged; REGISTRATION.md 0 bytes; no push. Large outputs are under
/mnt/large-storage/market_data/PropExperiment/derived/e33/ (features/2b30cb0e953b, labels/b15c4ca10d68, search/, b3/,
b4/, probes/), with their manifests, not in git.

## 3. Results

### 3.1 B3 agreement (20 seeded dates; work/b3_runs/full_r3.md)
After the continuation rulings (R-B3-FD6: Coder-A's literal reading, fixed in B; R-B3-FD7: fixed in A; R-B3-N10:
fixed in B), run full_r3 (12:21:52-12:21:59) found 0 disagreeing cells in all 59 feature columns (5,460 rows), in
all 6 labels (19 columns plus the row join; F05 5,460, F15 5,260, F30 4,960, F60 4,360, T15 5,260, T30 4,960 rows)
and in sigma_ZM, sigma_ZS and sigma_ZL on 20 of 20 dates. Codes: features A 2b30cb0e953b and B 0485beafebbb; labels
A b15c4ca10d68 and B efdde5c74ee1. The mismatch file has 0 rows. No feature is NaN: P4 G3 sets an invalid value to 0
with its family flag 0.

### 3.2 B4 leakage tests (work/B4_leakage.md, work/b4_runs/)
- LT1, 200 draws (seed 20261027), on the final code: prior=production 200/200 with 0 columns outside tolerance and
  0 rows after t (12:44:57-12:48:16); prior=recompute (D and its 21 history dates re-streamed under the cutoff)
  200/200 the same (12:51:36-14:15:29, about 75 s a draw; 22 pass-1 markers per draw folder, 21 on the first OOF date).
- LT2 on the R-L10 span: 46,886 rows, 0 violations over 12 rules. LT3-LT6: pass (E.33; LT3 21-date embargo).
- LT7 simulator causality: 3,620 of 3,620 decisions equal; 259 of 259 trade fills; 724 of 724 fills on both sides;
  0 of 622 fill times differ from the label table; entry_ok 362 of 362. Usable draws 190 per F15 configuration and
  172 per T30 configuration (the rest fall outside the configuration's grid).
- B4 synthetic feature run, seed 10, on the final code: 8,190 rows, 0 cells in 59 of 59 columns, sigma equal on 30
  of 30 dates; the independent oracle finds 0 mismatches for A and for B. Correction: E.33's synthetic runs "7", "8"
  and "9" all used seed 7's streams (the harness ignored --seed; fixed and logged), so E.33 had one stream, not three.
  Limit: the oracle covers C.1-C.4, C.15, F4.1 and F4.6; for F3.9 and F3.11 the planted-case evidence is A/B agreement.

### 3.3 B5 synthetic proofs (work/B5_proofs.md, 40 seeds, each run once on pinned code)
Seeds 19, 119, 20 and 120 ran in E.33b (09:09:18-09:50:18, rc 0) on the code pinned in E.33. Null proof: Tier A
empty in 20 of 20 seeds (pass needs at most 1 non-empty). Planted proof: the plant entered Tier A in 20 of 20 (pass
needs 14). 0 failed fits. The best null SR_d over the 20 null seeds runs from -0.0757 to 0.0602 (median 0.0058). The
null daily-Sharpe SD is 0.0425 (0.0436 with the df correction), above the iid reference 0.0354; the gates do not use
it. Only F15 configurations caught the 15-minute plant (T30 in 0 of 20 planted seeds).

### 3.4 The freeze and C1
Pipeline freeze reports/stage_e33_pipeline_freeze.sha256, sha256 eb565a37f814953d0f86dd99e15a34c3bd19c7f0f670a8e7e1a44853a085173e:
166 pipeline files, 11 documents, 47 verification-evidence files and 3 freeze tools, with a derived-inputs manifest
(4,125 files, 60.8 GiB, identical to the 09:54 dry run). Readings file FINAL, sha256 da58c77f. Evidence behind the
GO: reports/stage_e33_freeze_evidence.sha256 (124 files). Configuration freeze reports/stage_e33_c1_freeze.json,
sha256 ea002c60 (300 configurations: 60 per set, 50 per label, 180 LOGIT and 120 LGBM). Run marker
reports/stage_e33_run_marker.md.

### 3.5 Stores built after the freeze
- Features (P10 features-only store, built after B3 passed and before the freeze, keyed by code 2b30cb0e953b, which
  is the frozen code): 816 pass-1 and 816 pass-2 dates, 217,308 rows (796 x 273), in two runs (09:28:58-09:54:35 and
  12:26:00-12:40:11). F1.7 and F1.8 are invalid on 277 of the 796 dates, F1.3 on 120 and F4.7-F4.8 on 22: the
  definitions need history inside the segment (data note in the readings file).
- Labels (frozen code b15c4ca10d68): 796 OOF dates x 6 labels; 776 built 14:24:21-14:28:46, rc 0; the other 20 are
  the B3 tables built earlier by the same code (R-L12).

### 3.6 P5 projection and the P10 stop
Written to the STATE file at 14:17-14:18, before the first real-outcome fit:
- builder probe on the 3 P5 dates (pass 1, fresh process each): 3.65, 5.41 and 5.66 s, mean 4.907 s;
- fold-6 probe on the synthetic seed9000 table (R-L1): E33-S5F15L100E 6.60 s, E33-S5F15G3050 1.08 s;
- projected 796 x 4.907 / 4 + 1,080 x 6.60 / 8 + 720 x 1.08 / 2 = 2,255.8 s (37.6 minutes); stop above 6,767.5 s.
Measured: the feature build 2,387 s (the two runs, first to last DONE each), plus the fits from 14:29:04, net of the
logged collector-window pause (15:34:05-16:00:05, 1,560 s). On real data the S5 LOGIT folds took a mean of 109.3 s (up to 654.2
s) and the S1 LOGIT folds 37.9 s; the LGBM folds took 5.0 s (S5) and 2.0 s (S1). The probe configuration
E33-S5F15L100E took 227.4 s on its real fold 6 against 6.6 s on the synthetic table, and E33-S5F15G3050 2.6 s
against 1.08 s. P5's formula with these real fold-6 times would give 32,611 s (9.1 hours). The measured total passed 6,767.5 s at
16:08:11, and the watcher stopped the search at its next 10-second check (work/logs/p10_stop.json: fits net
4,387.8 s, measured 6,774.8 s; the process group ended on SIGTERM, so the search log ends at 16:08:07 with a fold start and no rc line; the
watcher's own log records its exit, rc=0, at 16:08:12).

### 3.7 What ran
- Finished, status ok (72): all 60 S5 configurations (6 labels x 10 grid points), and 12 of S1: S1F15 G2050,
  G2200, G3050, G3200, L001A, L001E, L010A, L010E, L100A and S1F30 L001A, L001E, L010A. Failed: 0.
- Partial (3): S1F15L100E, S1F30L010E and S1F30L100A; 8 folds were cut mid-fit.
- Not started: the rest of S1 (45 configurations) and all of S3, S2 and S4 (180). 440 of 1,800 fold fits are done.
- S5, the largest set (59 features), took 91.95 minutes of wall time (65.9 net of the pause); S1 ran about 11 folds
  a minute. The remaining 1,360 folds would need about 2 hours (1.8-2.5) at that pace on 8 processes.
Every finished configuration has its fold models, OOF predictions, daily series, trades and statistics on disk under
derived/e33/search/<id>/ with DONE markers. None of them was read or summarised (decision in section 6). Folds cut
by the stop carry one interrupted attempt each; a resume refits them, and a second interruption would fail the
configuration (P5).

### 3.8 Selection table, robustness, finalists
Not run. P8's inputs are the 300 OOF series; after a stop, protocol 0.2 and P10 call for a report of what ran, and
nothing is selected from a partial budget. Parts D and E wait for decision D1.

### 3.9 Price-limit rule 5 on the 796 dates (V52 item 2; work/rule5_count_796.txt)
Counted from the label store's per-date exclusion records (counts only). The limit part (r5_limit) removes minutes
on 98 dates for F05, F15 and T15, 96 for F30 and T30, and 95 for F60. Minutes removed, by any rule / by rule 5 as the
first failing rule: F05 15,315 / 15,109 of 217,308 grid minutes; F15 and T15 14,645 / 14,400 of 209,348; F30 and
T30 13,659 / 13,355 of 197,408; F60 11,766 / 11,350 of 173,528. The locked-span and book-at-t parts remove 0; no date
lacks limits; 49 dates are excluded whole by the calendar rules. The limit band is refreshed only on Sundays (E.33
section 3.1), so these removals follow the band's staleness as well as the market. Recount: the PipelineReviewer (Fable) recounted every cell from the same records, and every cell is equal
(review/PostStop_b.md, section 7).

## 4. Delegation record

| Agent | Model (confirmed from transcript) | Effort | Start-end (PDT) | Status |
|---|---|---|---|---|
| FeatureCoder-OpusXHigh (Coder-A fixes FD7, N11, R-L10) | claude-opus-5-5 (204 messages) | xhigh | 09:13-12:18 | done; idle 09:54-12:16 (not woken) |
| FeatureCoder2-OpusXHigh (Coder-B fixes FD6, N10, R-L11) | claude-opus-5-5 (146) | xhigh | 09:13-10:01 | done |
| PipelineReviewer-FableXHigh (phase 1, 2a, 2b, final GO; post-stop check) | claude-fable-5-1 (157) | xhigh | 09:13-14:17, 16:11-16:17 | done, GO |
| ReadingsCompiler-OpusXHigh | claude-opus-5-5 (187) | xhigh | 09:13-09:39 | done |
| FreezeCoder-OpusXHigh | claude-opus-5-5 (220) | xhigh | 09:13-10:00 | done |
| TestCoder-OpusXHigh (B3 r3, B4 synthetic, LT1/LT7) | claude-opus-5-5 (262) | xhigh | 10:01-14:16 | done |

No Sonnet or Haiku worker ran. Six workers in all, at most 6 at once; heavy jobs at most 2 at once. Coders and
reviewers ran as Agent-tool workers, resumable with SendMessage, not as workflow agents (section 6, item 1). Tokens
per worker are in section 8.

## 5. Verification

- B3 full_r3: run by the TestCoder; the lead read the table and the mismatch file (0 rows); the PipelineReviewer
  recounted it on disk.
- B4 (LT1 both priors, LT2, LT7, synthetic seed 10): run by the TestCoder; the lead tallied the JSON files; the
  PipelineReviewer recounted them, reproduced the LT1 draw from its seed, and checked the 22-marker recompute folders.
- B5: the PipelineReviewer recounted the 40 selection files and confirmed one run per seed on pinned code.
- Fix diffs: the PipelineReviewer checked every diff against its ruling; 438 + 45 unit tests passed.
- Freeze: verify --remeasure and check-proofs by the lead (0 differences); the reviewer checked the freeze tool and
  its coverage (SF2).
- Numbers in this return after the stop (P5 projection inputs and arithmetic, the measured times and the stop, what
  ran, N, the rule-5 count, the frozen-code tie of the search): the PipelineReviewer (Fable, resumed with a narrow
  brief, outcome seal kept) found 38 CONFIRMED and 1 DIFFERS (the rc line's log, corrected), 0 BLOCKING, 2 SHOULD FIX
  (both applied) and 3 notes (applied) (review/PostStop_b.md). It also tied the search's pipeline_sha 323a82ff96ca
  to the frozen list.

## 6. Open choices

Every choice the lead made without the user, in the order made. Each is also in the STATE file, with its time.

1. Workers as Agent-tool spawns, resumable with SendMessage, rather than workflow agents, although Ultracode was on.
   A workflow agent cannot be resumed, and the coders and the reviewer needed follow-up rounds.
2. Thread budget: at most 10 threads in all and 2 heavy jobs (the prompt's cap). A one-process 20-date rebuild ran
   as a light job beside the last proof seeds.
3. B3 rulings R-B3-FD6 (F3_11: Coder-A's literal `rest == 0`; fix in B), R-B3-FD7 (F3_9: attribute fill lots by order
   id within the batch; fix in A) and R-B3-N10 (clear, then mark bad; fix in B).
4. R-L9: LT1 at 200 draws under both priors (recompute and production), not one of them.
5. The ReadingsCompiler's 10 NEEDS LEAD items: R-L10 (the TB row span is [t, t+2L+h]; entry rules stay on
   [t, t+L+h]; fix in A and in LT2), R-L11 (F4.6 Hi and Lo over the as-of function; fix in B). Confirmed without a
   code change: F06, L11-L13 (B's labels are verification code), K01 (Lucid at 0.560 and 0.920), K04 (W = 60 s
   from the resting time), K14 (AFML from secondary sources, labelled), P12, P14, T07. Every other compiled entry was
   adopted as compiled.
6. N11 ordered: both builders record data33.ORDER_LOG in their DONE records (all empty on real data). The
   per-process accumulation the reviewer noted (N16) was left as is.
7. LT1/LT7 started at 12:21, beside B3 full_r3, on the stated condition that any A-side code change would force a
   rerun. B3 found none.
8. Freeze coverage: ledger/trial_registrations.jsonl listed as state, not hashed (C1 appends to it);
   ledger/databento_spend.jsonl hashed; the 5 guard-refused MES and condition files left unread (P1.2). N17: the
   derived inputs re-hashed fresh rather than reused. N18: the evidence results hashed separately. N19: any edit of a
   hashed harness or document file between the freeze and C1 would have re-taken the freeze; none was made.
9. R-L12 (PipelineReview N21): the pre-freeze label tables (20 B3 dates; the LT dates) are B3/B4 test inputs. Their
   values entered only equality and rule checks (R-L2 (b)). The 20 B3 tables were kept in the production label store
   because the frozen label code is the same code. Data note N22 added beside N3.
10. Readings appendix: the compiled readings were copied in unchanged, with each heading one level deeper. A lead
    note says that the rulings above it govern.
11. P5 builder probe: pass 1 only, a fresh process per date, as E.33 timed it; P_b = 4 (the builder's process limit
    and the count used), P_L = 8, P_G = 2.
12. Measured feature build for the 3x rule: the sum of the two build runs, each from its first to its last DONE
    marker (2,387 s). The idle gap between them, while B3 was re-run as P10 requires, is excluded. Read literally,
    "first to last DONE marker" would span 09:28-12:40 (191 minutes) and would have exceeded the 3x reference before
    the first fit, so no real-outcome fit would have run (0 fits rather than 440). Neither reading changes any outcome:
    both end in a stop with nothing selected.
13. The collector-window pause (15:30-16:00) is netted out of the measured fit time, from the runner's "pausing
    submissions" line to its "resuming" line (15:34:05-16:00:05, 1,560 s).
14. The 3x stop was applied by a watcher (reports/stage_e33_briefs/work/lead/p10_watch.py, written at 14:46, after the
    freeze and outside the selection pipeline), decided in STATE at 14:30 before any result: TERM, then KILL, of the
    search's process group at the crossing.
15. After the stop, no outcome statistic of any finished configuration was read, summarised or reported, and Parts D
    and E were not run. Reason: P8 needs all 300, and a continuation decided by the user stays blind to results.
16. The rule-5 count was taken from the label store's exclusion records: both the any-rule and the first-rule counts,
    with the locked-span and book-at-t parts reported beside the limit part.
17. Post-stop verification by the same PipelineReviewer (Fable), resumed with a narrow brief, rather than a seventh
    worker. This respects the prompt's cap of 6 workers under either reading (at once, or in total).
18. Two empty logs under the real search root (search/_logs/run_20261028_091637_* and run_20261028_122056_*) came
    from the reviewer's refusal tests of run_search33, whose logger starts before the refusal. They hold no fit, and
    no fit record predates 14:29:04 (the earliest attempt start).
19. Lead tools written after the freeze, all outside the selection pipeline: work/lead/p10_watch.py (the stop),
    reports/stage_e33b_briefs/tools/check_2r.py (LT1 recompute check) and evidence_manifest.py (N18).
20. Harness fix found by the TestCoder: run_synth_features ignored --seed. E.33's synthetic runs 7-9 were one stream;
    this is recorded in B4_leakage.md and section 3.2.
21. Oracle scope: F3.9 and F3.11 on the planted cases rest on A/B agreement, not on the independent oracle.
22. The P5 fold probe ran on the synthetic seed9000 table (R-L1, chosen in E.33). R-L1 held that the table "measures
    the same code path at the same table size". At equal table size the real fits took far longer, most likely
    because saga converges more slowly on real features (inferred from the times; the iteration counts sit in sealed
    files), so the synthetic probe under-measured the LOGIT cost by about 34x (227.4 s against 6.6 s for E33-S5F15L100E fold 6).
23. A pause of the fits at 15:30 is the runner's own collector-window rule (S14). Folds already running finished
    inside the window.
24. Time stamps corrected after the fact: rulings stamped 09:20, actually 09:12; two messages that say 09:52 were sent
    at 09:40:55; one message that says 12:33 was sent at 12:28; "GO at 14:20" in a draft of the readings status line
    was corrected to the review file's 14:17:14 before the freeze.
25. Process failure, not a choice: FeatureCoder ended its turn at 09:53 to wait for its own build, which finished at
    09:54. It was never woken, and the lead waited on it from 10:18 to 12:16, about 2 hours. From then on every brief
    told workers not to end a turn while their own job ran, and the lead used watchers and heartbeats.
26. Lead miss: before C1, the P5 projection left 73 minutes for the fits, while P5's own guesses (lines 586-589: 1-4
    hours of fit wall time) and E.33's return ("about 2-3 hours") were both larger. The 3x stop was a foreseeable
    risk, and it was not flagged before registering. Registering followed the prompt (C1 "may proceed once every gate
    before it passes"; the 3x rule is a run-time stop, not a gate), but the risk should have been written down, with
    a recommendation.
27. Deviation from CLAUDE.md: no estimate table was printed at launch. The first came at 12:17, when the user asked
    for an ETA; its finish of 21:30-00:30 assumed the full search.
28. The lead's memory guard for the full suite (stop pytest below 2 GB available) used a pgrep pattern that also
    matched its own command, so it never logged an end line. It was stopped at 16:33. The suite's available memory
    stayed at or above 11.7 GB (pytest_end.txt), so the 2 GB rule was met.

## 7. Decisions for the user (each with a recommendation)

D1. The compute limit that stopped the search. Under protocol 0.2, only a new protocol version, decided by the user
    and hashed before it runs, can let the search continue. Options:
    (a) Amend P5/P10 for this run only: replace the 3x reference with one projected from the real fold times already
    measured (the per-fold wall times in work/logs/search_real.log, which hold no outcomes), and keep a 3x
    stop against it. Then resume the same registration r009-E33 (N stays 838) from the DONE markers in a
    continuation stage, run P8 on all 300, then Parts D and E. At the measured pace that is about 2 more
    hours of fits on 8 processes (1.8-2.5).
    (b) Lift the 3x stop for E.33 alone, as V52 lifted the deadlines, and resume as in (a).
    (c) Close E.33 as stopped: N 838 stays charged, nothing is selected, and ZM discovery ends without a verdict.
    Recommendation: (a). The 3x rule bounds compute; it has no bearing on inference. No result of any finished
    configuration has been read, so the continuation stays blind to outcomes. The 300 registrations are already
    counted in N. A new 3x reference still protects the machine and the budget, which (b) would not.
D2. Limit bands for the test stage (V52 item 2, the part left open): rule 5's limit part removes minutes on 95-98 of
    the 796 discovery dates, and the band is refreshed only on Sundays. Recommendation: decide, when E.34 is drafted,
    whether the test uses daily limits from another source, with this count in hand. Nothing changes for discovery.
D3. Future protocols (process, not E.33): a probe that sets a stop limit should run on data that converges like the
    real data. Recommendation: register a 1-2 configuration real-data timing probe as its own trial before the main
    registration, or set the compute stop against the protocol's own guess range (here 1-4 hours of fits).
E.32 D2 (amend V14 (c) for the test's DSR variance) stays open until the test stage is drafted (V52 item 4).

## 8. Session cost

Computed at 16:33 PDT from this session's transcripts (main .jsonl and subagents/*.jsonl of session b8cfc9d8,
2026-10-28 09:05-16:33 PDT) with reports/stage_e10_briefs/cost.py (output: reports/stage_e33b_briefs/cost_e33b.txt).
These are token counts, not plan-credit percentages; the commit step after 16:33 is not counted.

Wall clock: 09:05-16:33 PDT, 7 h 28 min. Of that, 1 h 58 min (10:18-12:16) was lead idle time, waiting on a worker
that had stopped (not a usage limit, not a pause). The search's own collector-window pause (15:34:05-16:00:05,
26 min) was not lead downtime: the lead drafted the return meanwhile. Usage-limit pauses: none. Work time excluding
the idle stretch: 5 h 30 min.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,633 | 157,155 | 15,586,332 | 2,011,344 | 17,756,464 |
| claude-opus-5-5 | 1,782 | 796,316 | 181,758,270 | 3,005,528 | 185,561,896 |
| all | 3,415 | 953,471 | 197,344,602 | 5,016,872 | 203,318,360 |

Worker spawns (agent file worker-xhigh for all):
- FeatureCoder-OpusXHigh: opus (claude-opus-5-5), xhigh, 18,776,437 tokens
- FeatureCoder2-OpusXHigh: opus, xhigh, 10,125,116
- ReadingsCompiler-OpusXHigh: opus, xhigh, 24,615,678
- FreezeCoder-OpusXHigh: opus, xhigh, 20,578,518
- TestCoder-OpusXHigh: opus, xhigh, 34,667,178
- PipelineReviewer-FableXHigh: fable (claude-fable-5-1), xhigh, 17,756,464

Delegation share: lead 76,798,969 (37.8%), workers 126,519,391 (62.2%). By model: Opus 185,561,896 (91.3%), Fable
17,756,464 (8.7%). Cache reads are 97.1% of all tokens.

Final table (times PDT, from STATE, logs and transcripts; tokens from the transcripts):

| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|
| 1 | Lead: start checks, gates, reading, plan | opus (xhigh) | 09:05-09:09 | 4 min | (lead) | done; no estimate table printed at launch (deviation) |
| 2 | Proof seeds 19, 119, 20, 120 (lead-run job, 8 procs) | - | 09:09:18-09:50:18 | 41 min | - | done, rc 0 |
| 3 | Lead: rulings FD6/FD7/N10, briefs, 4 spawns | opus (xhigh) | 09:10-09:14 | 4 min | (lead) | done |
| 4 | FeatureCoder-OpusXHigh | opus-5-5 (xhigh) | 09:13-12:18 | about 44 min active | 18,776,437 | done; idle 09:54-12:16, never woken |
| 5 | FeatureCoder2-OpusXHigh | opus-5-5 (xhigh) | 09:13-10:01 | 48 min | 10,125,116 | done |
| 6 | ReadingsCompiler-OpusXHigh | opus-5-5 (xhigh) | 09:13-09:39 | 26 min | 24,615,678 | done |
| 7 | FreezeCoder-OpusXHigh | opus-5-5 (xhigh) | 09:13-10:00 | 47 min | 20,578,518 | done |
| 8 | PipelineReviewer-FableXHigh | fable-5-1 (xhigh) | 09:13-09:24, 12:20-13:00, 14:16-14:17, 16:11-16:17 | about 1 h active | 17,756,464 | done; GO; post-stop check |
| 9 | Lead: 10 NEEDS LEAD rulings | opus (xhigh) | 09:39-09:41 | 2 min | (lead) | done |
| 10 | TestCoder-OpusXHigh | opus-5-5 (xhigh) | 10:01-14:16 | 4 h 15 min (mostly its jobs) | 34,667,178 | done |
| 11 | Idle: lead waiting on FeatureCoder | - | 10:18-12:16 | 1 h 58 min | - | lost time (section 6, item 25) |
| 12 | LT1/LT7 job (TestCoder, 3 procs) | - | 12:21:39-14:15:30 | 1 h 54 min | - | rc 0, all pass |
| 13 | Feature store, 816 dates (lead-run, 4 procs) | - | 12:25:50-12:40:11 | 14 min | - | rc 0 |
| 14 | Lead: readings appendix, review rounds, Part D briefs, tools | opus (xhigh) | 12:16-14:16 (interleaved) | - | (lead) | done |
| 15 | P5 probe and projection | lead | 14:16:21-14:18:35 | 2 min | (lead) | written before the first fit |
| 16 | Readings FINAL; freeze build, verify, check-proofs | lead | 14:18-14:23 | 5 min | (lead) | 0 differences |
| 17 | C1 registration, run marker | lead | 14:23-14:24 | 1 min | (lead) | N 538 -> 838 |
| 18 | Labels, 796 dates (lead-run, 3 procs) | - | 14:24:21-14:28:46 | 4 min | - | rc 0 |
| 19 | Search (lead-run, 8 procs) | - | 14:29:04-16:08:11 | 1 h 39 min (73 min net) | - | stopped by P10 3x rule; 72/300 |
| 20 | Pause: collector window (search only) | - | 15:34:05-16:00:05 | 26 min | - | pause, netted out |
| 21 | Lead: rule-5 count, stop watcher, return draft | opus (xhigh) | 14:30-16:08 (interleaved) | - | (lead) | done |
| 22 | Lead: post-stop count, end checks, return, progress, STAGES, cost | opus (xhigh) | 16:08-16:33 | 25 min | (lead) | done |
| 23 | Full pytest suite | - | 16:13:01-16:32:22 | 19 min | - | 1 known failure (h6), as E.33 |
| all | Stage E.33b | lead + 6 workers | 09:05-16:33 | 7 h 28 min (5 h 30 min excluding the idle stretch) | 203,318,360 (lead 76,798,969; workers 126,519,391) | initial estimate (first table 12:17): finish 21:30-00:30 with the full search; actual: stopped at 16:08 by the compute rule, return by 16:40 |
