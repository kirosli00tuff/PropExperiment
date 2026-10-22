# FIXES_E28b: pilot code against the final QM spec and RS-01..RS-13

Worker: PilotFixer-OpusXHigh (Opus 5.5, xhigh), 2026-10-21 16:54-17:05 PDT (times from `date`).
Spec: reports/stage_e28_pilot_spec.md, sha256 8937740338e81103b0a5a3edcf90fab46d1aa62140bcaf7abb309a7fdc87d0ae
(checked at start; not edited). Review: reports/stage_e28_briefs/R_spec.md lines 17-37 and section 6.
No Databento call of any kind, no key or .env read, nothing outside B_pilot/ written, no commit.
Pre-edit copy of the folder: /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c4961140-6cb5-4eeb-8deb-096950337c09/scratchpad/bpilot_before/

## 1. RS items

Line numbers are for the files as they are now.

| RS | status | where |
|---|---|---|
| RS-01 end 2024-02-29T22:00:00Z; verify cutoff at 23:00Z | code already in; tests and README fixed now | pilot_common.py:76-81 (CUTOFF_BOUND, CUTOFF_UTC, CUTOFF_OPEN_NS); request refusal pilot_common.py:262-264; pilot_stream.py:377-380 (counts); verify.py:42, 147-150 (hard check plus info count for [22:00Z, 23:00Z)). Fixed now: tests/test_b_files.py:72-100 (old check name replaced by `verify.CUTOFF_CHECK`; a record at exactly 23:00Z and at 03-01 07:00Z fails, rc 1; records at 22:00:00Z and 22:59:59Z are info only, rc 0); tests/test_b_sessions.py:96-104 (trade date 03-01 is no longer a candidate day of a pilot file; the old 2024-03-01 bound still shows it); README steps 1, 5 |
| RS-02 FIFO row | not applicable (spec wording; already in spec section 0) | none |
| RS-03 outright book; side counts | already in | pilot_stream.py:278 (trades_side_A/B/N per date); verify.py:160 (manifest total) and per-day column; phase 2 sums them into data_checks. README convention 8 now says so |
| RS-04 through clause A/B only | already in; core tests added now | measure_core.py:99-101, 125-128 (defined_aggressor mask; N never fills under any rule); measure_stats.py:198 (fills by trigger/aggressor). New tests: tests/test_b_core.py:236 (N through: no fill under any rule; A through fills, trigger "through"/"A"), :254 (queue trigger/aggressor). README convention 8 rewritten (it still said N "can trade through") |
| RS-05 no-drop markout variant | already in; tests added now | measure_core.py:180-198; measure_stats.py:202-213 (markouts_nodrop, vpo_nodrop, dropped_share). New tests: tests/test_b_core.py:294 (headline dropped as invalid_book, no-drop gives the last valid mid; no valid state after t_f gives no_valid_book); tests/test_b_stats.py:57-79, 103-109. README convention 9 rewritten |
| RS-06 stale share | already in; tests added now | measure_core.py:226-236 (is_stale); measure_stats.py:200 (stale_share per cell). New tests: tests/test_b_core.py:283; tests/test_b_stats.py:106. README convention 4 |
| RS-07 minimum span | fixed now (QM value) | pilot_common.py:14-17, 83-86: MIN_SPAN_FIRST_TRADE_DATE = date(2024, 1, 12) (was 2024-01-18, the QG value), docstring of min_span_refusal pilot_common.py:274-276; pilot_pull.py:25-27, 43 docstrings. The checks themselves were already in: buy refusal pilot_pull.py:498; quote warning :474-476; plan flag :452; span search candidates and "buy nothing" :588, :614. Tests updated: tests/test_b_pull.py:421-432 (comment), :458-473 (minimum span 35 ES trade dates x 1.25 = 43.75 > TARGET 30, first quote at 2024-01-12), :494-503 (refusals at 01-15, 01-18, 02-26, start 2024-01-12 00:00Z, 2024-01-11T22:00:01Z), :505-513 (01-12, 2024-01-11T22:00:00Z and 01-11 pass the span check). README parameters and steps 1-4 |
| RS-08 margin rule | code already in; README fixed now | pilot_common.py:87-88, 285-291 (margin_target); pilot_pull.py:178-186 (approved must be the fresh quote, quote <= APPROVED < quote + 0.01; quote > TARGET refused, nothing bought); tests/test_b_pull.py:524-545 already there. README parameters table, steps 2-4 |
| RS-09 SAFE TO WIPE precondition | fixed now (README) | README step 5: written by the lead to the STATE file only after verify.py exits 0, or 3 for data-quality findings only, and `sha256_matches_purchase_record` passed (verify.py:95; so verify.py must run with `--purchase-record`); never after 1 or 2 |
| RS-10 every purchased date measured | not applicable to code (already true: measure.py measures every trade date in the file); README step 6 says so |
| RS-11 latency an assumption | not applicable (spec wording) | none |
| RS-12 ts_event as time axis | not applicable (spec wording; code already uses it) | README convention 1 cites spec section 2 |
| RS-13 life end | already in (as a clip, not an assert); test added now | measure_core.py:285-286 (c = min(j + 60.05 s, piece end)). New test tests/test_b_core.py:263 (forced grid 30 s before a piece end: life ends at the piece end, a trade 15 s later does not fill, a trade inside does; on the regular grid the clip does not bind). README convention 5 |

## 2. Extra changes (item 4 of the brief: spec sections 0-6 against the code)

1. Second fee (spec section 0: "net markouts are also reported at 0.296 tick per side"). The code
   had one `--fee-side` only, and an `--aggregate-only` rerun with another fee would overwrite
   results.json. Added: measure.py `--fee-side-alt FEE ...` (measure.py:399-401; checked >= 0 and
   de-duplicated at :420-423; passed to phase 2; recorded as `fee_side_alt_ticks` at :328;
   results.md header note `_alt_note` :360); measure_stats.py `fee_side_alt` in all_cells /
   cell_stats / _markout_stats (`fee_key` :171; `mean_net_alt` per horizon for the headline and
   no-drop markouts :255; `vpo_alt` and `vpo_nodrop_alt` :210; markdown rows "... at fee 0.296
   tick/side"). Fees stay out of the fingerprint (phase 2 only). Tests: tests/test_b_stats.py:114
   (by hand: net 60 s 1.5 - 0.296, VPO 0.5 x 1.204, no-drop -0.296 labelled negative),
   tests/test_b_files.py:146 (end to end through measure.main with `--aggregate-only`).
2. Spec hash references: measure.py:48 SPEC_REF and measure_core.py:3-5 said `8f5711fb...`; now
   `8937740338e81103...`, contract QM. CODE_VERSION bumped to e28-b-measure-3 (measure.py:47; no day
   file exists anywhere, so nothing is invalidated).
3. Synthetic stats tables: tests/test_b_stats.py `_one_day_table` lacked the trigger, stale and
   no-drop columns the RS-04/05/06 code reads (2 tests failed with KeyError 'spec:trigger');
   completed, with by-hand assertions for each new output.
4. README.md rewritten for the final spec: QM parameter table (ROOT QM, TICK 0.025, FEE_SIDE 0.1368,
   FEE_SIDE_ALT 0.296, SIMRULE trade_through_only, label Topstep, B, TARGET, D, APPROVED), the
   request end, the QM minimum span, RS-08, RS-09, the target path
   `/mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/range=<start>_2024-02-29T220000Z.dbn.zst`
   (minimum span: `range=2024-01-11T220000Z_2024-02-29T220000Z.dbn.zst`, computed with
   data.pull_universe.target_path, no call), the exact verify and measure commands, conventions 3-5,
   8, 9, 10, 12 updated, and the `--aggregate-only` overwrite stated (the old text said "Nothing
   is overwritten").
5. Lint: three ruff findings in tests fixed (one pre-existing E501 at tests/test_b_pull.py:99, two
   in my new asserts). `ruff check` on the folder: all checks passed.

Checked and found consistent with the spec, no change: the code is contract-generic (`--root`,
`--tick`); QM is in data.calendars' GROUP_OF_PRODUCT (energy group); `pilot_stream.tick_units(0.025)`
is exact (25,000,000 price units); the QM calendar gives 76 MAIN grid times on every regular trade
date (58 on the two early closes, which are excluded) in 2024-01-12..02-29, matching spec section 6;
the QM minimum-span request passes every request refusal (pilot_common.request_refusals returned an
empty list); roll handling is by instrument change per trade date (pilot_common.py roll_exclusions),
so QM's monthly rolls need nothing special; SIMRULE trade_through_only is a choice of measure.py.
In 2024-01-12..02-29 the QM (energy) calendar has 35 trade dates with 2 holiday or early-close dates
(01-15, 02-19); about 2 monthly rolls (about 4 exclusions) leave about 29 usable, above the 26 the
spec needs (a count, not a check of the spec's arithmetic).

## 3. Test results

| suite | log | result |
|---|---|---|
| B_pilot (`uv run --project <repo> python -m pytest -q tests -p no:cacheprovider`, from B_pilot/, nice 10) | runs/pytest_bpilot_e28b.txt | 168 passed, 0 failed, rc 0 (17:04:22 PDT). Before this work: 153 passed, 4 failed (test_b_files cutoff name, test_b_sessions candidate days, two test_b_stats KeyErrors) |
| SpecReviewer adversarial (`uv run pytest -q reports/stage_e28_briefs/work/REV_spec/test_rev_spec_adversarial.py -p no:cacheprovider -rf`, repo root, nice 10; file not edited) | runs/pytest_adversarial_e28b.txt | 18 passed, 2 failed, rc 1 (17:04:23 PDT); both failures are expected by design, below. Same 2 failures before this work (they come from the earlier worker's RS-04 and RS-13 code, not from these edits) |

Expected-by-design failures (each test's docstring says it DOCUMENTS the pre-fix behaviour):
- `test_side_none_trade_through_fills_under_spec_but_never_adds_to_v` (line 106): asserts that a
  side-N trade strictly through the price fills under the spec rule. RS-04 removed that: the
  through clause now needs aggressor A or B (spec section 3: "the first trade with a defined
  aggressor (side A or B, never N)"). Its first half (N at the price never adds to V) still passes.
- `test_life_window_may_extend_past_a_session_piece_end_if_the_grid_allows_it` (line 180): asserts
  a fill 15 s after the piece end under a forced grid. RS-13 now clips the life at the piece end,
  so there is no fill. The companion test (the spec grid never puts a life across a piece end)
  passes.
No RS-01 test exists in the adversarial file, so no RS-01 failure there.

## 4. Open questions for the lead (not decided here)

1. MIN_SPAN_FIRST_TRADE_DATE is one constant, now the QM value. pilot_pull.py accepts any root in
   GROUP_OF_PRODUCT, so a run with `--root QG` would use QM's bound (and QG's own spec bound,
   2024-01-18, is later). Should pilot_pull.py refuse any root other than QM? Not done: it would
   be a new guard, and the tests run on ES.
2. VPO at the second fee: spec section 0 says net markouts are also reported at 0.296; the code
   also reports VPO_10 and VPO_60 at 0.296 (the same quantity at the other fee). Remove if the lead
   wants only the literal wording.
3. verify.py does not require `--purchase-record`; without it the sha256 check is skipped and exit 0
   is possible. The README makes the SAFE TO WIPE line depend on that check passing. Make it
   mandatory in code?
4. Wording only, no change: spec section 4 says "fills within 60 s"; the code counts fills up to the
   effective cancel (j + 60.05 s), as section 3 says ("fills inside that window count"), reports the
   late ones separately (`fills_in_cancel_latency`) and censors the KM curve at 60 s. The touch rate
   uses the same 60.05 s window. The no-drop variant also drops at a session end, which the spec
   grid never reaches.
5. RS-13 is a clip (a change of behaviour off the grid), not the comment or assert the reviewer
   suggested. Under the spec grid the two are the same.

Nothing in the brief is unfinished.

## E.28b round 2: DeltaReviewer RD-01 to RD-03 (lead rulings)

Worker: PilotFixer-OpusXHigh, 2026-10-21 17:14-17:22 PDT. Inputs: reports/stage_e28_briefs/R_delta.md
(findings table, section (c), verdict NO GO) and work/REV_delta/test_rev_delta_adversarial.py (not
edited). Same boundaries: no Databento call, no .env or key, nothing outside B_pilot/ written,
the real ledger never touched (tests use their tmp ledgers), no commit, nice 10.

| RD | ruling applied | where |
|---|---|---|
| RD-01 (BLOCKING) root | every pilot_pull.py mode (--plan, --quote, --span-search, --buy) refuses a root other than QM before any key read or call | pilot_common.py:76 `PILOT_ROOT = "QM"` (spec section 0), :298-311 pilot_root_refusal / require_pilot_root; pilot_pull.py:431 (main, all modes); also inside check_request via pilot_refusals (pilot_common.py:323-333), so every span-search candidate is pinned too |
| RD-01 (BLOCKING) one purchase | --buy refuses when the ledger already holds a commit line on acct-3 for any other request (any session: acct-3 is pilot-only; a commit line with no request counts). The same request's resume (done, settle_only, retry) is unchanged. The refusal is a PilotRefused before any client is built and writes nothing to the ledger | pilot_pull.py:196-210 other_purchases (reads the entries the buy already reads), :531-536 |
| RD-02 (BLOCKING) end | --plan, --quote and --buy refuse any end other than exactly 2024-02-29T22:00:00Z (string equal to CUTOFF_BOUND; later or earlier); --span-search already pinned it (pilot_pull.py:600) and its candidates now also pass check_request's pin. The buy's RS-07 check stays on the start (min_span_refusal), so every bought span holds [2024-01-12, 2024-02-29T22:00Z) | pilot_common.py:314-321 end_pin_refusal, :323-333; pilot_pull.py _request -> check_request |
| RD-03 (SHOULD FIX) verify | --purchase-record required: missing, unreadable, non-dict JSON, or no 64-hex sha256 -> rc 2, nothing opened. Every --dbn file gets the hard check sha256_matches_purchase_record (no more `expected if len(paths) == 1 else None`); with two or more files at most one can match, so the run exits 1 | verify.py:230-240 purchase_sha256, :253, :259; check at :100-101 |

request_refusals stays root-generic (verify.py and measure.py still read files of any calendar root,
which the ES-based file tests use); the pins sit in pilot_refusals / check_request. The reviewer's
CHECK test `request_refusals(pilot_params("QM", ...), "QM") == []` still holds.

Tests (B_pilot):
- tests/test_b_pull.py switched from ES to `ROOT = pc.PILOT_ROOT` (QM) throughout: BASE, Env.target,
  fake_client (now `root=` for the written DBN header and the symbology key), the plan, get_range and
  purchase-record assertions, and the span-search tests on the QM (energy) calendar. The hand-computed
  span numbers are unchanged on QM: 40 trade dates -> 2024-01-05 at TARGET 50; 49 from 2023-12-21;
  minimum span 35 trade dates = 43.75. `--symbol ES.c.0` stays as a wrong-symbol refusal.
- test_buy_refused_by_acct3_cap (:289): rewritten. With one purchase only, the account cap can bind
  only on the same request: an orphan commit of this request (100.00, another session) plus a
  --retry-download quoted at 30.00 exceeds 125.00 while the session cap alone would allow it.
- New: :313 (another request's commit on acct-3 blocks the buy: no full request, another QM span,
  another root; nothing ledgered, no client), :328 (a second QM span after a settled purchase is
  refused; the first still resumes as "already bought"), :345 (12 cases: QG/CL/ES x every mode
  refused before any key, client or ledger line), :359 (12 cases: four ends before the cutoff x
  plan/quote/buy), :370 (pilot_refusals pins root and end, request_refusals stays generic).
- tests/test_b_files.py: helpers purchase_record (:40) and run_verify (:47) pass a record with the
  file's sha256 to every verify call; test_verify_clean_file asserts the sha check passed. New: :240
  (no record -> rc 2, no manifest), :248 (4 bad records -> rc 2), :258 (wrong sha -> rc 1), :266
  (two files: both checked, [pass, fail], rc 1; with the second file's sha, rc 1 again).
- README: request paragraph, steps 1, 4 and 5, and the SAFE TO WIPE paragraph (exit 0 or 3 now
  implies the sha256 matched for every file).

Results (round 2 logs; round 1 logs kept):

| suite | log | result |
|---|---|---|
| B_pilot | runs/pytest_bpilot_e28b_r2.txt | 204 passed, 0 failed, rc 0 (17:19:19 PDT) |
| REV_spec adversarial | runs/pytest_adversarial_e28b_r2.txt | 18 passed, 2 failed, rc 1 (17:19:20 PDT): the same two by-design failures as round 1 (RS-04, RS-13) |
| REV_delta adversarial | runs/pytest_rev_delta_e28b_r2.txt | 8 passed, 7 failed, rc 1 (17:19:21 PDT): the 7 DOCUMENTS tests fail by design; all 8 CHECK tests pass |

REV_delta tests that now fail by design (each asserted a hole that is now closed):
- test_DOCUMENTS_buy_of_a_root_other_than_QM_is_not_refused[QG], [CL], [ES]: the --quote for that
  root already returns rc 2 (RD-01), so the test stops at its quote step (line 39).
- test_DOCUMENTS_a_second_contract_can_be_bought_after_the_first: the QM buy succeeds; the QG quote
  is refused rc 2 (RD-01, line 39 via 64). A second QM span would be refused by the one-purchase rule
  (B_pilot test :328).
- test_DOCUMENTS_buy_with_an_end_before_the_cutoff_passes_the_minimum_span_check: the quote with
  --end 2023-12-01 is refused rc 2 (RD-02, line 39 via 78).
- test_DOCUMENTS_verify_exits_0_without_a_purchase_record: rc 2, not 0 (RD-03, line 128).
- test_DOCUMENTS_verify_with_two_files_skips_the_sha_check_silently: rc 1, both files' sha checks
  written and failed (RD-03).
Ruff on the folder: all checks passed.

Round 1 open questions: Q1 is closed by RD-01, Q3 by RD-03; Q2, Q4 and Q5 were rated NOTE (RD-04 to
RD-06), no change.

Open questions after round 2 (not decided here):
1. verify.py and measure.py are not pinned to QM (the ruling named pilot_pull.py; their tests use
   ES files). The file-name and header checks still tie a file to the --root given. Pin them too?
2. --quote is still allowed after a purchase (it is free but writes a quote line to the ledger);
   only --buy enforces one purchase.
3. The one-purchase rule counts any commit on acct-3, in any session, as "a pilot purchase" (acct-3
   is pilot-only by data.config.PILOT_ONLY_ACCOUNTS). If a non-pilot commit ever landed on acct-3,
   the buy would refuse; that is the conservative reading of "one purchase only".
