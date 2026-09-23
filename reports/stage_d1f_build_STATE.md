# Stage D.1f (build and freeze, no purchase): STATE

All times are Vancouver local (PDT), per the user's instruction of 2026-09-23 00:20 PDT.

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh. Ultracode off. Session start 2026-09-23T23:39 PDT
(2026-09-22 23:39 PDT). Resume rule: read this file first, skip finished tasks.

## Task 0 startup evidence (23:39 PDT)

- git: clean at 9cbd815.
- `uv run python -m data.holdout status`: all_ok true, unlocks_logged 0, research_has_no_holdout_rows true.
- Declaration hashes (reports/stage_d1e_declaration_hashes.json) match on disk:
  reports/stage_d1f_confirmation_list.md c19cbac1...147c OK; docs/NULL_CRITERIA.md 6f69e318...97e2 OK.
- Worker files present: worker-medium, worker-high, worker-xhigh, worker-max.
- Baseline suite: 543 passed, 1 xfailed, 129 s wall (probe for ETAs).
- N = 31. Databento calls this stage: 0. Spend $0.00.

## Plan and routing (stated before any spawn)

| # | Task | Agent name | subagent_type / model | Effort | P/S | Files it may touch |
|---|---|---|---|---|---|---|
| 0 | Startup, plan, constants, config | lead | Opus 5.5 | xhigh | serial | data/config.py, data/research_bars.py (date constants only), this file |
| 1 | T2 holdout-2 sealing + D.1f seal-on-arrival puller | HoldoutSealer-OpusXHigh | worker-xhigh / opus | xhigh | wave 1 | data/holdout.py, data/pull_mes.py, tests/test_d1f_holdout2.py |
| 2 | T1 ConfirmationWindow, loader, null-generator refusal | WindowLoader-OpusXHigh | worker-xhigh / opus | xhigh | wave 1 | screening/runner.py, screening/drift.py, funnel/null_generator.py (refusal only), data/research_bars.py, tests/test_d1f_confirmation_window.py |
| 3 | T3a CME 2019-2024 holiday entries, verbatim citations | CalendarExtractor-SonnetMed | worker-medium / sonnet | medium | wave 1 | reports/stage_d1f_calendar_sources.{md,json} |
| 4 | T6a FOMC/CPI/NFP 2019-05..2024-02 dates, verbatim citations | ReleaseExtractor-SonnetMed | worker-medium / sonnet | medium | wave 1 | reports/stage_d1f_release_sources.{md,json} |
| 5 | T5 six Family H modules + look-ahead tests (synthetic only) | HModuleCoder-OpusXHigh | worker-xhigh / opus | xhigh | wave 2 | strategy/research/h_daily_bar/*, tests/test_d1f_h_daily_bar.py |
| 6 | T3b calendar code, coverage assertion, confirmation bar build, step-4b validator | BarBuilder-OpusXHigh | worker-xhigh / opus | xhigh | wave 2 | data/cme_calendar.py, data/build_mes_bars.py, data/bars.py, data/validate.py, tests/test_d1f_calendar_build.py |
| 7 | T4 statistics wrapper + T6b release-table module + E-H amendment | StatsWrapper-OpusHigh | worker-high / opus | high | wave 2 | strategy/research/_d1f_statistics.py, e_calendar_event/_release_table_2019_2024.py, E-H1/E-H2 (amendment only), tests/test_d1f_statistics.py, tests/test_d1f_release_table.py |
| 8 | T7 list runner + freeze-manifest script | ListRunner-OpusXHigh | worker-xhigh / opus | xhigh | wave 3 | strategy/research/_d1f_confirmation.py, strategy/research/_d1f_freeze.py, tests/test_d1f_confirmation.py |
| 9 | T8a verification of sealing + look-ahead tests | SealVerifier-FableXHigh | worker-xhigh / fable | xhigh | after 1, 5 | reports/stage_d1f_verification.md |
| 10 | T8b adversarial review | AdvAuditor-FableMax | worker-max / fable | max | after 8, 9 | reports/stage_d1f_adversarial_review.md |
| 11 | Fixes from rulings | FixApplier-OpusXHigh | worker-xhigh / opus | xhigh | after 10 | as ruled |
| 12 | T9 freeze manifest, suite, guardrails, entry, STAGES.md, cost | lead | Opus 5.5 | xhigh | serial | reports/stage_d1f_harness_freeze.json, progress.md, docs/STAGES.md |

Deviations from the prompt's suggestions (logged):
- T5: ONE worker for all six H modules, not one per pair. The six share the daily-bar,
  complete-day, guard, opening-range, entry and exit mechanics; three separate implementations
  would be three chances for a look-ahead divergence. Effort xhigh, not high, because
  look-ahead is the review focus.
- T6b (E-H amendment and the release-table module) goes to the T4 worker, which already runs
  the train-union reproduction machinery; the sonnet extractor never writes code.
- The confirmation bar build, the per-date raw-symbol rule and the step-4b validator are not
  separate tasks in the prompt but must exist and be frozen before the purchase (list 1.5
  steps 2 to 4b run next session with frozen code); they go to row 6.
- The freeze script goes to the runner worker (row 8), which verifies the same manifest.

## Estimate ETA table (printed in chat 23:45 PDT; * = guess)

Base rates from the D.1e final table: opus xhigh code 9-16 min, opus high 5-15 min, sonnet
extraction 4 min on local files, fable xhigh verification 20 min, fable max review 27 min.
This stage's code tasks are larger and its extraction is web-bound, so each row is scaled up.

| # | Task | Owner | Model | Effort | P/S | ETA | Cumulative (from 23:39 PDT) |
|---|---|---|---|---|---|---|---|
| 0 | Startup, plan, constants | lead | opus | xhigh | serial | 15 min | 0:15 |
| 1 | T2 holdout-2 + puller | HoldoutSealer-OpusXHigh | opus | xhigh | wave 1 | 40 min* | 0:55 |
| 2 | T1 ConfirmationWindow | WindowLoader-OpusXHigh | opus | xhigh | wave 1 | 40 min* | 0:55 |
| 3 | T3a calendar citations | CalendarExtractor-SonnetMed | sonnet | medium | wave 1 | 30 min* | 0:45 |
| 4 | T6a release citations | ReleaseExtractor-SonnetMed | sonnet | medium | wave 1 | 35 min* | 0:50 |
| 5 | T5 H modules | HModuleCoder-OpusXHigh | opus | xhigh | wave 2 | 45 min* | 1:35 |
| 6 | T3b calendar code + bar build | BarBuilder-OpusXHigh | opus | xhigh | wave 2 | 35 min* | 1:30 |
| 7 | T4 wrapper + T6b + E-H amendment | StatsWrapper-OpusHigh | opus | high | wave 2 | 40 min* | 1:35 |
| 8 | T7 list runner + freeze script | ListRunner-OpusXHigh | opus | xhigh | wave 3 | 50 min* | 2:30 |
| 9 | T8a verification | SealVerifier-FableXHigh | fable | xhigh | beside 8 | 20 min* | (1:55) |
| 10 | T8b adversarial review | AdvAuditor-FableMax | fable | max | serial | 30 min* | 3:00 |
| 11 | Fixes | FixApplier-OpusXHigh | opus | xhigh | serial | 20 min* | 3:20 |
| 12 | T9 freeze, suite, entry, cost | lead | opus | xhigh | serial | 25 min | 3:45 |

Projected end about 03:25 PDT.

## Open choices the lead made (reason in each line)

- (0.1) data/config.py: STAGE_D1F_SESSION_ID "stage-D.1f-2026-09", D1F_SESSION_CAP_USD 10.00,
  D1F_REQUEST_CAP_USD 10.00, as the prompt instructs. SpendGate has no per-request cap, and
  data/spend_gate.py is outside the list's 5.8 allowed files, so the per-request cap is
  enforced in the D.1f pull function in data/pull_mes.py (allowed), before each fetch.
- (0.2) Holdout-2 and confirmation date constants live in data/research_bars.py (allowed by
  5.8), not data/splits.py (not in 5.8's list), and are written by the lead before wave 1 so
  the two wave-1 workers share one definition.
- (0.3) The research path now also refuses holdout-2 and embargo-2 dates, and confirmation
  dates are refused on the research path, the reading that makes a leak least likely.

- (0.4) The external spend ledger configured in data/config.py (../MLCryptoEngine/data/vendor/
  spend_ledger.jsonl) is absent; the copy lives at /mnt/large-storage/Archive/GitHub/MLCryptoEngine/
  data/vendor/spend_ledger.jsonl. SpendGate fails closed on a missing external ledger, so the
  run session's purchase would be refused. NOT changed here (it alters spend accounting, which
  the prompt did not ask for); flagged to the user, who can repoint EXTERNAL_LEDGER_PATHS before
  the freeze commit and re-run the freeze script.
- (0.5) The estimate table was printed in chat just after the wave-1 spawn rather than before
  it (minor order deviation from CLAUDE.md). CLAUDE.md changed on disk at 23:48 PDT (Opus default
  lead; fable for independent/adversarial work); the plan already conforms.
- (6.1) Release-table collisions: the extraction found two dates carrying two releases,
  2019-12-11 and 2020-06-10 (FOMC 14:00 ET and CPI 08:30 ET). The hashed table's type is one
  release per trade date (its builder raises on a duplicate). Ruling: keep the EARLIEST release
  (CPI 08:30 ET) on both dates, because E-H1's pre-announcement window ends at the first
  scheduled release of the day and E-H2 reacts to the first release; the FOMC entries on those
  two dates are listed as dropped in the module's docstring. Conservative for a null claim in
  the sense that no event is invented; it removes two FOMC events from C5.
- (1.1) screening/__init__.py does not export ConfirmationWindow; left as is (screening/__init__.py
  is not on 5.8's allowed list). The runner imports from screening.runner directly.
- (2.1) Holdout-2 exact trade-date counts (list 1.2 "recorded at sealing"): the manifest carries
  no dates or counts (list 1.2 L-1). Ruling: at sealing the run session records the CALENDAR
  count (weekdays minus listed full closures, 2024-04-01..2025-03-31) in its STATE file; the
  count from bars is recorded only at a D.2 unlock. Reading the sealed bytes for a count is a read.
- (2.2) data/adapter.py refusal messages name holdout-1's window even when holdout-2 triggers the
  refusal; the refusal is correct and adapter.py is outside 5.8, so left as is.
- (2.3) reports/stage_d1e_quotes.json (hashed) cites data/pull_mes.py line numbers that have
  moved (58/83/95/104 -> 102/126/138/147); descriptive only, not a definition.
- (2.4) D.2 unseals holdout-2 chunk by chunk (13 log entries); a D.2 registration can add a
  batch unseal later (after the D.1f run, a holdout.py change no longer voids anything).
- (5.1) H readings (worker's, accepted by the lead as the look-ahead-conservative ones):
  early_halt_ct read from the bars dated d; CT clock windows count only bars dated d; d-1 = the
  latest complete daily bar before d; exit window [14:58, no-new-positions time). Forced exits
  are recorded on the instance (forced_exit_dates); the list runner must keep the instance.
- (7.1) DECLARED AMENDMENT (list 5.7, NEW-1), recorded here before any purchase:
  E-H1 strategy/research/e_calendar_event/h1_scheduled_macro_drift.py
    old 94e92ff15efe2160c5e967da6d1a415385681a43cf500505004b87b363ab25b2
    new f28529f058e9a6cc63d1030f6e08ce1b78e7c11c7f89ad64aa583468e1eb7a35
  E-H2 strategy/research/e_calendar_event/h2_post_release_momentum.py
    old b2f09ab6e71dafe554c8db35c04a02f3476cb25e0f3783ca740ebffc19b5f005
    new 7183d9bda56b36b9089b05b9ee02cbd9609392f29d88f14ca005fb6bb341aeca
  Diff (both): + `release_table: dict[date, datetime] = field(default_factory=lambda:
  RELEASE_TABLE_ET, repr=False, compare=False)`; the lookup `RELEASE_TABLE_ET.get(...)` becomes
  `self.release_table.get(...)`. Nothing else. Reason: the modules read a module-level table with
  no hook and cannot fire on 2019-2024 dates (N-1). Test: both reproduce stage_d1d_accounting.json
  on the train union to the cent under the no-argument factory and the combined-table factory;
  reverting the edit as text restores the old hash.
- (7.2) Release table count: 37 scheduled statements in 2019-05..2024-02 (the md's 38 counted the
  excluded January 2020 meeting); minus the two collision dates = 35 FOMC.
- (7.3) Rulings on the wrapper's questions: F4.4 forward intervals crossing the daily halt or a
  weekend are charged drift as the sum of the drift path's per-minute mean changes over every
  clock-minute bar the interval covers, halt minutes 0 (the literal "own forward clock interval");
  F4.4's interval starts at the crossing bar's open (drift.py's inside-bar convention).
- (6.2) Calendar judgment calls (BarBuilder): 12:00 CT settlement lines read as 12:15 CT halts,
  graded inferred (the 2025 convention, confirmed by 2025 bars); Good Friday 2021 08:15 CT time
  [unverified]; New Year's Day 2021 status [unverified]; no entry for 2022-01-03, 2020-07-02,
  2021-07-02 (CME shows normal processing). Step 4b tests all of them against the bars.
- (6.3) Raw-symbol rule reads "the bar's date" as the UTC date (symbology intervals are UTC);
  the stop test uses trade dates >= 2019-05-06. The build fetches per-date symbology once (free)
  into VENDOR_ROOT/symbology/...2019-04-01_2024-03-01.json, frozen once written.
- (6.4) Run-session caveat, not a defect: before 2021-06-28 CME equity futures had a
  15:15-15:30 CT pause and closed 16:15 CT [unverified, web search only]; the frozen data/session.py
  halts at 16:00, so 16:00-16:15 bars are flagged in_scheduled_closure (the engine refuses only
  intents on them, not the bars; they belong to the same trade date) and the pause shows as gaps.
  Trials flatten by 15:10 CT, before both. Thin 2019 trading may make step 4b report
  discrepancies that are not calendar errors; the list's own procedure handles that before step 5.
- (6.5) Section 0's data/cme_calendar.py line is checked by the runner through the 2025-2026
  block (git show 9cbd815 version, sha 5f24edda, block byte-equality); the runner refuses on a
  build stop flag, a failed step 4b, or a missing degraded-date comparison (message sent to the
  ListRunner 00:28 PDT).
- (8a) Rulings on the verification (reports/stage_d1f_verification.md), fixes queued for row 11:
  D1 ACCEPT (resume path runs delivered_record_bytes before sealing, count in the SEALED note);
  D2 ACCEPT (complete_interrupted_seal with the same round-trip proof, called instead of raising);
  N1 ACCEPT (an added, separately named test replacing day d by a copy with a different tick range);
  N2 ACCEPT, stricter reading: a holdout-2 unlock requires "holdout 2" in the stage argument
  (the regex still fullmatches (stage\s+)?d\.2(\s+holdout\s+2)?; holdout-1 unchanged);
  N7 ACCEPT (clear message on SealIntegrityError, still stops); N3, N4, N5, N6 NOTED, no change
  (N4: synthetic H bars dated inside the mined range are synthetic, not a look).
- (8.1) ListRunner interpretations, all accepted (each the literal or stricter reading): a
  statistic's composite verdict uses its own post-exclusion dates for T and the drift path; a
  member can be both "edge" and meet the null conditions, and the class verdict follows 3.3
  alone; Tier B anomaly "net edge >= +2.11 per event" read as mean v >= 2.11 (stricter);
  class per-trade epsilon uses the median trades/day of the class's trial members on the
  window; continuity also checks trip counts and daily Sharpe to 1e-6 (as D.1d did); step 5
  refuses if M* = 2019-05 but its first trade date is not 2019-05-06; the manifest also covers
  the two recorded-facts files the runner reads. The runner was split into five _d1f_* modules
  to respect the 800-line cap; every _d1f_* file is inside the manifest (5.8's list names only
  _d1f_statistics.py and _d1f_confirmation.py; the split is logged as a deviation of form).
- (8.2) Ruling (c) revised (c'): a Tier B "sign reversal versus the mined window" is tested on the
  GROSS per-date series s x e (direction of the effect), one-sided for mean < 0, BH 10% within
  Tier B; testing net v would label cost-driven negatives as reversals. Anomaly test unchanged.
- (8b) Rulings on the adversarial review (reports/stage_d1f_adversarial_review.md), all written
  before the freeze:
  F1 ACCEPT: required --manifest-sha256 argument; E-H post-amendment hashes as literals in the preflight.
  F2 ACCEPT: the D.1f pull and the confirmation build run the file-hash preflight first; the
     build stamps the manifest sha256 into its summary and the parquet; check_build compares.
  F3 ACCEPT, BROADENED: empty strategy/research/__init__.py; the freeze pins every *.py under
     strategy/, data/, screening/, sim/, funnel/, rules/; the preflight refuses unlisted *.py there.
  F4 ACCEPT: the git anchor covers every manifest path; the freeze commit must include the harness.
  F5 ACCEPT: run-session inputs (parquet, build summary, rolls/condition/symbology JSONs,
     HOLDOUT2_MANIFEST) hashed at step 5 and re-checked at every later step.
  F6 ACCEPT, runner side: H forced exits counted from the ledger, the instance's set recorded
     beside it, differences flagged (P&L unaffected either way).
  N5 ACCEPT (interpreter and library versions in every output header; the run prompt should set
     OPENBLAS_NUM_THREADS=1). N6 ACCEPT (docs/HOLDOUT_MANIFEST.json in the manifest).
  N7 ACCEPT, lead applied it (reverses choice 0.4): data/config.EXTERNAL_LEDGER_PATHS now points
     at /mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl. Reason:
     config is frozen, so leaving a missing path means the purchase is refused or the run is voided
     by the fix; the gate now reads shared spend $84.006048 (matches D.1e), session $0; a local file
     read, no Databento call; tests/test_spend_gate.py 12 passed.
  N1, N2, N3, N8, N9 NOTED. N4 (two fail-closed residues needing manual steps) goes into the
     run-session checklist of the progress entry.

## Task status

| # | Status | Start | End | Artifacts |
|---|---|---|---|---|
| 0 | done | 23:39 PDT | 23:47 PDT | this file; data/config.py (+3 constants); data/research_bars.py (+D.1f date constants) |
| 1 | done | 23:47 PDT | 00:09 PDT | data/holdout.py (770 lines: HOLDOUT2 paths, per-chunk seal, verify, per-holdout unlock), data/pull_mes.py (--d1f-pull oldest first with seal-on-arrival, per-request cap gate subclass, --d1f-quote-only, D.1f rolls), tests/test_d1f_holdout2.py (61 tests; 14 mutants all caught); fetch_range writes <target>.partial then hard-links, databento 0.82.0 has no cache |
| 2 | done | 23:47 PDT | 00:00 PDT | data/research_bars.py (trade_date_class, load_confirmation_bars, stricter research re-check), screening/runner.py (ConfirmationWindow, confirmation_window(S)), funnel/null_generator.py (_refuse_outside_one_slice), tests/test_d1f_confirmation_window.py (66 tests); full suite 609 passed 1 xfailed; E-H3 train-union continuity to the cent; screening/drift.py unchanged |
| 3 | done | 23:47 PDT | 00:01 PDT | reports/stage_d1f_calendar_sources.{json,md}: 71 entries (cme 67, secondary 3, unverified 1); gaps listed in the md |
| 6 | done | 00:01 PDT | 00:27 PDT | data/cme_calendar.py (68 entries 2019-2024 + SOURCES_2019_2024, 2025-26 block byte-identical, ENTRIES_2025_2026_SHA256; whole-file sha 5f24edda -> d2aca685), data/bars.py (assert_calendar_coverage in add_flags), data/validate.py (validate_calendar_step4b), data/build_mes_bars.py (build_confirmation, --confirmation, stop_for_lead_decision, exit 7), tests/test_d1f_calendar_build.py (29 tests) |
| 4 | done | 23:47 PDT | 23:54 PDT | reports/stage_d1f_release_sources.{json,md}: 154 entries (38 FOMC, 58 CPI, 58 NFP), all primary grade; 2 collisions; 10 unscheduled/cancelled notes |
| 5 | done | 23:53 PDT | 00:21 PDT | strategy/research/h_daily_bar/ (_mechanics.DailyBarStrategy + six thin modules, H_TRIALS in __init__), tests/test_d1f_h_daily_bar.py (44 tests; 38 mutants, all behaviour-changing ones caught); full suite 730 passed 1 xfailed; no real bars touched an H module (no look, N unchanged) |
| 9 | done | 00:21 PDT | 00:38 PDT | reports/stage_d1f_verification.md: all 5 sealing assertions VERIFIED on real code paths; H1 and H6 re-derived by hand to the cent; 14 extra mutants caught; 0 BLOCKER, 2 SHOULD-FIX, 7 NOTE |
| 7 | done | 00:00 PDT | 00:27 PDT | strategy/research/_d1f_statistics.py (compute_statistics, forward_mean_moves_ticks), e_calendar_event/_release_table_2019_2024.py (151 entries: 35 FOMC, 58 CPI, 58 NFP), E-H amendment, tests/test_d1f_statistics.py (16), tests/test_d1f_release_table.py (30); EDA reproduction to 1e-9; E-H train-union to the cent under both factories; full suite 789 passed 1 xfailed |
| 8 | done | 00:25 PDT | 00:48 PDT | strategy/research/_d1f_confirmation.py (CLI, steps 5-8), _d1f_preflight.py, _d1f_start_rule.py, _d1f_members.py, _d1f_decisions.py, _d1f_freeze.py; tests/test_d1f_confirmation.py (50); full suite 839 passed 1 xfailed; refuses to run this session as designed; freeze dry-run to scratch: 114 files |
| 11a | done | 00:49 PDT | 01:06 PDT | data/holdout.py (800 lines; complete_interrupted_seal, holdout-2 stage must name 'holdout 2'), data/pull_mes.py (D1 resume decode, N7 message), _d1f_decisions.py (gross reversal test); tests 81/50/51 in the three d1f files; full suite 866 passed 1 xfailed |
| 10 | done | 01:08 PDT | 04:39 PDT | 01:08-01:19 work; Fable session rate limit 01:19-04:31 PDT (3 h 12 min, not work: 'You've hit your session limit, resets 4:30am'); resumed with context 04:31 PDT; reports/stage_d1f_adversarial_review.md: 0 BLOCKER, 6 SHOULD-FIX, 9 NOTE; READY TO FREEZE on conditions |
| 11b | done (FreezeHardener-OpusXHigh: F1-F6, N5, N6; 898 passed) | 04:40 PDT | | |
| P | pause: Fable session rate limit | 01:19 PDT | 04:31 PDT | not work; the lead idled, nothing ran |
| 12 | done | 04:59 PDT | 05:07 PDT | full suite 898 passed 1 xfailed (lead run); canaries 15 passed; reports/stage_d1f_harness_freeze.json written 05:03:25 PDT, 129 files, sha256 ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a; preflight refuses only on uncommitted files, missing build summary, unsealed holdout-2 (no hash mismatch); end guardrails clean; progress.md entry and docs/STAGES.md line written |

## FREEZE (printed for the user)

reports/stage_d1f_harness_freeze.json  sha256 ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a  (129 files)
The run session cannot start until the user commits this manifest together with every file it
lists. Any change to a listed file after the commit voids the run. Changing data/config.py (session
id, caps, ledger path) means re-running `uv run python -m strategy.research._d1f_freeze` first.
