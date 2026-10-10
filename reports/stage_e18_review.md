# Stage E.18 reviews

## C1b diff review (DiffReviewer-FableXHigh)

Worker: worker-xhigh, model fable (Fable 5.1). Brief: reports/stage_e18_briefs/brief_diff_review.md. Started 11:58
PDT, written 12:14 PDT, 2026-10-10 (times from `date`). Scratch: reports/stage_e18_diff_review/ (c1_vs_c1b.diff, the
tag-stripped CME pages, the v10 -> v12 data diffs and the v10 copies of pull_hist/hist_store/hist_calendar, the
patched generator copy and its output c1b_regen.md, pytest_run.log). Nothing was written outside this file and that
directory; no C1b file, ledger, registry, marker or git state was touched (`git status --short c1_replication tests`:
only `?? c1_replication/c1b.py` and `?? tests/test_c1b.py`). No 2010-2019 bar, store value, stage_e14_c1_result.json
or stage_e17_runs file was read; c1_replication.c1b, evaluate and q_m1 ran on synthetic tests only. No page fetched.

**Verdict: APPROVE WITH FIXES** (0 BLOCKING, 1 SHOULD FIX, 9 NOTE). C1b's text is C1's freeze plus THE ONE FIX and the
bookkeeping item 1 forces, nothing else; the exempt list follows from listing dates and section 2 alone; no other leg
or input of the 30 live features can hit C1's contradiction; the code does exactly clause 2 with C1's files
untouched; harness v12 changes nothing the ext2010 evaluation path calls; 101 tests pass. The one SHOULD FIX is a
wording precision in the new exempt clause ("as in training" is false for g17_mbt read literally), fixed before the
freeze by one phrase; it stops nothing.

### Check 1: scope of the text diff. PASS

- My diff (`diff -u reports/stage_e14_prereg_C1.md reports/stage_e18_prereg_C1b.md`, scratch c1_vs_c1b.diff): 10
  hunks, 36 lines removed, 101 added. C1's freeze on disk hashes to afc5c10f... (equal to the brief). Hunks and items:
  title (item 1); status block, lines 1-13 -> 1-16 (item 1: provenance, C1's closed attempt r001-C1 cited, N 478 ->
  480, v12, no purchase); section 2 "Never read before the test", lines 33-34 -> 35-43 (bookkeeping item 1 forces,
  below); section 3 C10 bullet, lines 62-65 -> 72-93 (items 2 and 3); section 5 line 83 -> 84 (item 1: "registered
  as C1b-T1 and C1b-T2", the pass conditions are context lines); section 6 lines 92-94 -> 95-96 (item 1); section 8
  lines 104, 110 -> 105, 111 (N 473 -> 480 only); section 9 heading and steps 5-8, lines 113, 123-128 -> 114-115,
  129-141 (item 1); section 10 heading and new item 5 (V31); section 11 heading, new "C1b's code" bullet and the
  "verifies first" paragraph, lines 158, 170-176 -> 159, 167-168, 177-188 (item 1 bookkeeping: harness v12, no
  quote); section 13 (new). Every other line is byte-identical: sections 1, 4 (costs), 7 and 12 have no hunk; in
  sections 2, 3, 5, 6, 8, 9, 10, 11 only the lines above changed. M1, q, the windows (2010-06-07..2019-04-30), the
  calendars and C12, the trade rule, the exclusions, the costs, the pass bar (1.5x cost, p <= 0.025, 30 trades) and
  every parameter are C1's. Section 13's list of 11 changes maps one to one onto the 10 hunks (the status block and
  the title share hunk 1) and is complete.
- The generator: a copy of reports/stage_e18_briefs/make_c1b_text.py with only OUT redirected to scratch (sed on line
  16) reproduces reports/stage_e18_prereg_C1b.md byte for byte (sha256 b6b5b96e3c364f8aa232116d240bf5a83636e3efdeac
  90c6aa9dac7d3ef6ca95 both; "15 replacements + section 13"; it checks C1's sha first, line 194).
- The three consequential edits: (a) section 2 lines 35-43: C1's sentence "no program file has read NG or any leg
  before 2019-05" is false since E.17 (store builds, C1's stopped run, the base-rule batch); the new text keeps the
  original claim dated to C1 and lists what was read since, each with its artefact, and states that no parameter
  depends on it (sections 3-5 frozen 2026-10-05, before the purchase of 2026-10-09). That is bookkeeping item 1
  forces (C1's attempt cited; a freeze may not carry a false sentence), not a design change. Its facts check: the
  stopped run printed counts only (reports/stage_e17_review.md check 4, lines 258-265); "under harness v11, as C1's
  step 6 allowed" (section 9 line 130) matches E.17_RETURN.md:112-113, 433 (v11 = the two caps and their pinning
  tests, the one freeze-inputs mismatch C1's section 11 allowed); NG is a product of H1 and H4
  (base_rules/constants.py:29-30 PRODUCTS; INTRADAY_TESTS = ("H1", "H4"), line 23); N 478 is the registry's N now
  (`python -m screening.trial_registry status`: N = 478, r001-C1 471 -> 473, r002-E16 473 -> 478). (b) Section 9
  lines 129-142: C1's steps 5-8 as done, C1b's 5-8 (review, dry check, freeze commit; register C1b-T1/T2; evaluate
  once behind reports/stage_e18_c1b_RUN_ONCE.json, which is c1b.MARKER_PATH, c1b.py:47; verdict); no quote, no
  purchase: item 1 bookkeeping, consistent with the prompt's STEP list. (c) Section 11 lines 177-188: the v12
  description matches the diffs (check 5); step (1)'s exclusion of reports/stage_e2b_harness_freeze.json is exactly
  the one entry that no longer verifies: I re-hashed all 43 entries of reports/stage_e14_c1_freeze_inputs.json now
  and exactly one mismatches (the harness manifest, fde3a49c... recorded, ece91ae8... on disk); the other 42
  (calendars, releases, c1_replication/*.py, tests, E.12 files, ml_route_v2/constants.py, the quotes file) verify, so
  step (1) is satisfiable as written. Step (3)'s files exist (reports/stage_e17_c1_store_hashes.json 537 B,
  reports/stage_e17_c1_calendar_hashes.json 1,269 B). reports/stage_e18_freeze.json, stage_e18_dry_check.md and the
  C1b marker do not exist yet, as the order of events requires.
- Nothing changes M1, q, calendars, windows, trade rule, costs, pass bar or any parameter.

### Check 2: the exempt list follows from listing dates and section 2 alone. PASS

- Section 3 lines 79-81: "The list is decided from listing dates and section 2 alone, never from a count of the
  test window, and holds exactly two features". No count of the test window appears in the C10 clause; the only
  counts named are E.12's training references (g17_cl 0, g17_mbt's liveness), which are frozen in the model JSON
  (reports/stage_e14_c1_model.json c10_reference: g17_mbt 87 / 84, g17_cl 0 / 0; my own read of the file).
- The two quotes: both verbatim in the saved pages after tag stripping (scratch mbt_page_stripped.txt,
  btc_page_stripped.txt): "CME Group, the world's leading and most diverse derivatives marketplace, today launched
  Micro Bitcoin futures" (mbt_launch_20210503.html; the raw HTML holds it with entity escaping, grep -o found it
  three times) and "effective on Sunday, December 17, 2017 for a trade date of December 18" (btc_selfcert_20171201.
  html; found only after stripping, the raw page breaks it across tags). Both saved pages hash to LOG.md's sha256s
  (d9686454..., 64d1652f...). The section-2 quotes exist unchanged: "CL is / never live on NG rows" (C1b lines
  31-32, across the line break) and "MBT is not listed (n/a by design)" (line 32); the annex phrase "all six were
  mature contracts in 2010" is at reports/stage_e13_ng_replication_draft.md:439 (1 hit).
- CL never applicable on NG rows, in code: ml_route_v2/signals/generic.py:343 `own_cluster = next((k for k, p in
  CLUSTER_LEADS.items() if p == lead), None)` gives "K4" for CL (ml_route_v2/constants.py:36-37 CLUSTER_LEADS K4 ->
  CL); lines 352-353 `if own_cluster is not None: ok &= view.cluster != own_cluster`; NG's cluster is K4
  (constants.py:28 `"NG": ("K4", "NG")`). So app_g17_cl is 0 on every NG row by construction, in training and in the
  replication; the replication also gives CL the C7 sentinel frame (c1_replication/world.py:123, constants.py:22
  EMPTY_ROOTS), so `j = -1` on every row as well.
- g17_mbt reads MBT bars only: generic.py:390-392 builds `g17_{lead.lower()}` with `partial(_lead, lead)` for each
  CLUSTER_LEADS value (K7 -> "MBT") and SIGNAL_ONLY_ROOTS ("MES"); `_lead` reads `bars_of(ctx, lead)` (line 342), the
  world's bars["MBT"], which is the sentinel frame (world.py:123). No root "BTC" exists in ml_route_v2 or
  c1_replication (grep: only k8's WKNDBTC date-list name and c1b.py:51's reason string). g17_mes is a spec but not a
  covered signal (the 64 covered signals hold g17_6e, _cl, _gc, _mbt, _nq, _zc, _zn only), so "MES gets no feature"
  holds and the world rightly loads no MES.
- g17_cl's inclusion matches V31 ("MBT; CL", docs/DECISIONS.md:566) and the prompt's clause 2, which names "CL,
  already 0 in E.12 on NG rows" (STAGE_E.18.md:50-51). It is a no-op: evaluate.py:382 stops only on `n > 0` in the
  reference, and g17_cl's reference is 0 on both horizons, so C1's rule never reached it; the text says exactly
  this (lines 86-88) and describes CL accurately: listed throughout the window (CL is a 1983 NYMEX contract
  [unverified], but nothing hangs on the date), excluded by the own-cluster rule, reference 0. See NOTE N-1 on the
  criterion wording.

### Check 3: no other leg or input can hit the same contradiction. PASS

- The 30 signals with a non-zero E.12 reference on NG rows (both horizons; from the model JSON, training panel):
  cp1_ret, cp2_brk, cp2_range, cp3_clv; g01_ret30 .. g16_month_end (16); g17_6e, g17_gc, g17_mbt, g17_nq, g17_zc,
  g17_zn; k4_ngpre_msince, k4_ngpre_mto, k4_ovr_pct, k4_ovr_ret. The 34 others (g17_cl and the K1-K3/K5-K9 members)
  are 0 in E.12 and are never reached by C10 under either rule (evaluate.py:382). Inputs, from code:
  - cp1_ret, cp2_range, cp2_brk, cp3_clv (ml_route_v2/signals/ports.py:83-200, `own_path_only=True`, lines 208-215):
    NG's own bars and fixed session literals (`_member_literals`, lines 47-55). NG store: ext2010 plan, by design.
  - g01-g04, g06-g10 (generic.py `_ret`, `_ret_day`, `_rv`, `_range`, `_prev_ret`, `_vol_state`, `_logvol`): NG's own
    bars; g05_gap (`_gap`, `_previous_trade_day` line 137) and g16_month_end (`_month_end_days`, 316) the group
    calendar; g11_t_index, g12_dow the row's clock and day; halts (`_daily._halt_days`, 75-81) the group calendar
    via ml_route.inputs._group_calendar; `session_minutes` (66-71) the frozen D6 table, which clock_check asserts
    equals every hist energy session (evaluate.py:283-291). The group calendar is swapped to the hist calendars
    (c1_replication/context.py:12-16, 52-53), 2010-2019 by design (E.14 probe, section 11).
  - g13_min_to_rel, g14_min_since_rel, g15_rel_day (`_release`, generic.py:289-313): `ctx.releases` = the world's
    releases = the hist D8 calendar (world.py:102-105, evaluate.py:505 `prep.releases.calendar`); `_covered`
    (277-281) masks rows outside the release file's coverage, which is the window by design (reports/stage_e14_cal_
    releases.json; NGS, WPSR, FOMC; 0 unsourced in the 2012 probe, C12 <= 2%).
  - k4_ngpre_mto, k4_ngpre_msince (k4.py:118-127): `ngpre.make_ng().ngs`, the NGS schedule; context.py:24-26, 58
    swaps `strategy.members.k4.ngpre.make_ng` to the hist NGS table less C13's drops, so the schedule is 2010-2019 by
    design. This was the one input that could have reproduced C1's contradiction silently (a 2019+ table on 2010
    rows); the swap closes it.
  - k4_ovr_ret, k4_ovr_pct (k4.py:158-204, vehicles (MCL, NG), NG rows only here): NG's own bars and the energy full
    sessions, swapped to the hist energy full sessions (context.py:27-28, 59).
  - g17_nq, g17_zn, g17_6e, g17_gc, g17_zc: the leg's bars (`_lead`, generic.py:342), each from an ext2010 store
    (data.pull_hist get_plan("ext2010").roots = NG, NQ, ZN, 6E, GC, ZC; 107 chunks; 2010-06-07..2019-04-30).
  - g17_mbt: the sentinel frame (exempt). No live feature reads MES, CL, release tables other than D8's, or any
    calendar outside the six hist groups.
- Listing state 2010-06-07..2019-04-30: NQ (CME E-mini Nasdaq-100, 1999), ZN (CBOT 10-Year Note, 1982), 6E (CME
  Euro FX, 1999), GC (COMEX Gold, 1974), ZC (CBOT Corn, 1877; on Globex since the 2007-08 merger), CL (NYMEX WTI,
  1983), NG (NYMEX Henry Hub, 1990): all listed on every date of the window, launch dates [unverified] (no fetch
  made; no real doubt: each is a decades-old CME Group contract, and the six stores were bought and built for the
  whole window in E.17). MBT: not listed before 2021-05-03 (verified quote). MES: launched 2019-05-06, after the
  window, and reads no covered signal. Beyond listing, a lead needs bars closed on the row's trade date by the
  decision time (`b.on_day`, generic.py:345); for 23-hour Globex contracts that holds by design on nearly every
  date, as E.12's 93-95% reference shares show, and C10 stops only on 0 rows.
- Other design-time contradictions in C1b's text: none found. C11 (evaluate.py:329-330, 512-513), C12 (334-338),
  the clock check (276-302, 339-340), the v2 freeze (324), the Gate 0 list (325-326), the model JSON and both M1
  payload hashes (173-205; keyed by horizon, lines 191-204, so C1b's ids change nothing; its "test": "C1" field is
  not checked), the store hashes (331-332, E.17's file) and the calendar hashes (333) all ran unchanged in E.17 on
  the same hashed inputs and passed (C1's run reached C10: reports/stage_e17_review.md check 2 and 5), so they pass
  again deterministically. The registry check under C1b's ids: evaluate.py:320-321 `require_registered(TEST_IDS,
  test=TEST, freeze_sha256=inp.freeze_sha256)` needs one entry holding C1b-T1 and C1b-T2 together under test "C1b"
  and C1b's freeze sha (screening/trial_registry.py:136-162); `register` accepts the label and ids (`_TEST`, `_ID`
  regexes lines 48-49: both match, checked) and refuses a repeated label or id (217-220), so C1's entry neither
  admits nor blocks C1b (tests/test_c1b.py:137-141). The run-once check (313-316) looks at C1b's marker and out
  paths, neither of which exists. The freeze hash check (317) needs the committed file; the lead's step.

### Check 4: the code does exactly clause 2. PASS

- c1b.c10_check (c1_replication/c1b.py:64-70): builds a new reference per horizon with the C10_EXEMPT keys removed
  from "applicable" (no mutation; tests/test_c1b.py:83-87) and calls `_C1_C10_CHECK` (line 59, `ev.c10_check` bound
  at import, i.e. evaluate.py:376-384 unchanged). Result: C1's rule on every signal except g17_mbt and g17_cl.
  C10_EXEMPT (49-56) holds exactly those two, with reasons from listing dates and section 2 only.
- The profile (85-101) swaps SWAPS = TEST, TEST_IDS, HORIZON_OF, c10_check, preconditions (57) and restores them in
  reverse order in `finally`, also on an exception and on a partial swap; nesting refused (88-89). Every use of
  these names on the run path is a module-global lookup at call time: evaluate.py:191-192 (load_model), 320
  (registry), 379-380 (c10_check), 428 (verdict_of), 466 (trades_sha256), 516-517, 520, 525-526 (evaluate), 551
  (preconditions), 553, 566 (run). No other c1_replication module references TEST, TEST_IDS or HORIZON_OF (grep:
  only constants.py:16-18 defines them); q_m1.c10_reference keys its counts by horizon, so the counts and the
  reference match under either id set. The C1b record (73-77, 80-82) enters `prep.records`, hence the marker
  (evaluate.py:553-555) and the result (569) before any bar is read.
- Marker: c1b.py:47, 125 (reports/stage_e18_c1b_RUN_ONCE.json, equal to section 9 step 7). Freeze: 46, 119
  (reports/stage_e18_prereg_C1b.md as the `--freeze` default). Exit codes and the refusal set equal
  evaluate.main's (126-132 vs evaluate.py:612-618).
- No C1 file changed: `git diff --quiet HEAD -- c1_replication tests/test_c1_evaluate.py tests/_c1_fixtures.py
  tests/_c1_state.py` rc 0; `git status --short c1_replication tests` lists only the two new files; the 42 non-
  harness freeze-input hashes verify (check 1).

### Check 5: harness v12 against the evaluation path. PASS

- get_plan("ext2010") built from dc93e9b's data/pull_hist.py (scratch pull_hist_v10.py, imported side by side with
  HEAD's): all nine v10 fields equal (name, test, test_ids, roots, chunks, first_trade_date, last_trade_date,
  data_start, data_end); v12 adds one field, `root_chunks = ()` for ext2010, and `chunks_of(root) == chunks` for all
  six roots. data/hist_bars.py (load_hist_leg, check_hist_bookings) is unchanged v10 -> v12 and reads only
  `p.roots` and the v10 fields (hist_bars.py:64, 96-100). hist_parquet_path(ext2010, each of the six roots) is
  identical in both versions; the hist_store.py diff is the docstring and the CLI's `choices` gaining "ext2010h"
  (scratch v10_v12_hist_store.diff). parse_hist_calendar's source is identical; hist_calendar.py's only code
  change is HIST_GROUPS gaining "livestock" (line 62), used as a membership check (line 460) that the six groups
  still pass, and c1_replication.evaluate names its own six groups (evaluate.py:91). data/config.py's changes are
  the two caps, E17_EXT2010H_SESSION_CAP_USD and STAGE_E17_EXT2010H_SESSION_ID (scratch v10_v12_config.diff),
  none read by the evaluation (c1_replication reads REPO_ROOT and HIST_ROOT only; grep of its data imports).
  Section 11's description of v12 is accurate (NOTE N-3 on one omitted constant).

### Check 6: tests. PASS

- `PYTHONPYCACHEPREFIX=<scratchpad>/pycache_c1b nice -n 10 uv run pytest -q -p no:cacheprovider tests/test_c1b.py
  tests/test_c1_evaluate.py tests/test_c1_world.py`: 101 passed in 30.37 s (12:03:45-12:04:16 PDT; MemAvailable
  4.1 GB before launch; log reports/stage_e18_diff_review/pytest_run.log).
- Clause 2 coverage: exempt never stops (test_c1b.py:77-80, both exempt signals, against C1's rule stopping);
  every other covered signal still stops under both rules and a dead-in-E.12 signal never does (69-74, parametrized
  over the 62 non-exempt of the 64 real covered signals, SIGNALS from the Gate 0 list); C1's rule unchanged
  (62-66, 120-124: the same reference stops C1's frozen run end to end); the exempt list is exactly the two (55-59);
  the reference is not mutated (83-87); swap, restore on exit and on exception, nesting refused (91-101); end to
  end a g17_mbt-live reference passes under C1b with C1b's ids, record and marker and the attributes restored
  (105-117); a dead non-exempt signal stops and closes (127-134); C1's registration does not admit C1b (137-141);
  the CLI's freeze and marker defaults and its refusal path (144-173).
- Misses: the frozen model JSON's real reference against the sentinel frames (the prompt's dry check, Step 3, by
  design outside the suite; E.17 N-2 stands until then); the STOPPED end-to-end case does not assert the attributes
  are restored (the exception test does, and `run` catches guard stops inside the profile, so it holds); no test
  that C1's real marker on disk leaves C1b unblocked (only path inequality, line 158, and the real-registry refusal,
  172); no test of the code record (NOTE N-4).

### Findings

- BLOCKING: none.
- SHOULD FIX S-1 (text, section 3 line 79-80): "a feature whose leg section 2 already makes 'not applicable' on
  every NG row of the test window, as in training." Read as a statement about training, "as in training" is false
  for g17_mbt: E.12 had it applicable on 87 / 84 NG rows (29 trade dates 2024-01-04..2024-02-29, the frozen
  reference). The phrase is meant as section 2 line 48 uses it (unlisted dates get "not applicable", the
  treatment training gave them), but this is the sentence the E.17 stop came from, and a reader comparing it with
  the frozen reference sees the same section-2-versus-section-3 looseness F-1 named. Fix (one phrase, in
  make_c1b_text.py replacement 4 and the regenerated file and diff): "... on every NG row of the test window, the
  treatment section 2 gives an unlisted or own-cluster leg, as training gave MBT before its listing." Nothing in
  code reads this sentence; it stops nothing.
- NOTE N-1 (text, section 3 lines 79-81 versus the prompt's clause 2): the prompt's criterion sentence is "a feature
  whose leg had no listed contract on any date of the test window", which CL (listed) fails, yet the prompt names
  CL; the text states the criterion as the prompt's "because" (section 2 makes it not applicable by design), the
  only reading under which both named legs qualify, and closes the list at two. Consistent with V31 and the prompt's
  named list. Optional: add "(the Stage E.18 prompt names both; CL is listed, so the operative test is section 2's
  'not applicable by design', the prompt's stated reason)" after "holds exactly two features".
- NOTE N-2 (text, section 2 lines 39-40): "H1 and H4 report per-product results whose window includes NG": true;
  H5, the composite of H1-H4 (base_rules/constants.py:93), also covers NG; H2 (NQ, ZN) and H3 (ZT, ZF, ZN, ZB) do
  not. Optional: "H1, H4 and the composite H5".
- NOTE N-3 (text, section 11 line 182-183): "data/config.py (the caps)" omits STAGE_E17_EXT2010H_SESSION_ID, a new
  session-id constant (scratch v10_v12_config.diff). Immaterial to the run path. Optional: "(the caps and E.17's
  ext2010h session constants)".
- NOTE N-4 (code record): evaluate.py:357 records q_m1.code_hashes(), which globs c1_replication/*.py (q_m1.py:
  95-96), so C1b's marker and result will list 11 files including c1b.py while the model JSON's code_sha256
  (q_m1.py:338) lists 10; nothing compares the two. No fix; the lead's post-run verification should expect the
  extra key, and it usefully pins c1b.py's hash in the result.
- NOTE N-5 (log and schema strings): "C1 marker written" and "C1 verdict" (evaluate.py:556, 572) and the schemas
  stage_e14_c1_run_once/1 and stage_e14_c1_result/1 (constants.py:71-72; evaluate.py:553, 566) carry into C1b's
  files; the "test": "C1b" field distinguishes them (c1b.py docstring line 24 says so). No fix: changing them would
  touch C1's code.
- NOTE N-6 (result path): c1b.main inherits `--out` as required (evaluate.py:598); the docstring names
  reports/stage_e18_c1b_result.json (c1b.py:7), the freeze text names only the marker (section 9 step 7). Optional,
  the lead's choice: `parser.set_defaults(out=...)` beside the freeze default (c1b.py:119), or name the path in step
  7, so the run-once check (evaluate.py:313) guards a fixed file.
- NOTE N-7 (tests): the misses listed under check 6; none weakens clause 2's coverage.
- NOTE N-8 (process): section 13 cites reports/stage_e18_c1b_diff.md "line by line" and the generator; any fix to
  the text (S-1) must go through make_c1b_text.py (its C1_SHA check, line 194, and OUT, line 16), regenerate the
  file, re-run the diff into stage_e18_c1b_diff.md section 4 and refresh its table, and re-hash before the freeze.
  Today the on-disk text equals the generator's output (sha256 b6b5b96e...).
- NOTE N-9 (listing dates): NQ, ZN, 6E, GC, ZC, CL and NG stay [unverified] for launch date, as the text marks
  them; I made no fetch (no real doubt; the six stores exist for the whole window by the plan's design). The two
  dates that matter, MBT 2021-05-03 and BTC trade date 2017-12-18, are verified verbatim.

Not done: nothing the brief asked for was left undone. No listing page was fetched for the long-established
contracts (allowed, not needed). The dry check on the real reference (Step 3) is outside this review.
