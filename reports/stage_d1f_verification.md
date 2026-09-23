# Stage D.1f verification: holdout-2 sealing (Task 2) and Family H look-ahead (Task 5)

Verifier: SealVerifier-FableXHigh (Fable 5.1, xhigh), 2026-09-23. Independent of the Opus
workers that wrote the code. Nothing under the repo was edited except this file; scratch work is
under the session scratchpad `verify/`. Zero Databento calls. No H module was run on real bars
(R-7): every H run below is on the tests' synthetic bars.

Holdout invariant at the start of this task: `uv run python -m data.holdout status` reports
holdout 1 `all_ok true, unlocks_logged 0`; holdout 2 `state not_yet_sealed, chunks_sealed 0,
unlocks_logged 0, all_ok false` (expected before the purchase). Same at the end (section 4).
REGISTRATION.md is 0 bytes. `docs/HOLDOUT2_MANIFEST.json` and `data/sealed/MES_holdout_v2`
do not exist yet.

Test runs (all on the working tree as of this task):

| Command | Result |
|---|---|
| `pytest tests/test_d1f_holdout2.py tests/test_holdout.py` | 100 passed (110.7 s) |
| `pytest tests/test_d1f_h_daily_bar.py tests/test_d1f_confirmation_window.py` | 110 passed (40.0 s) |
| `pytest tests/test_leakage_canaries.py` | 15 passed |
| scratch `verify/test_mutants_h.py` (8 mutants, 19 parametrised runs) | 19 passed: every mutant made the real test fail |
| scratch `verify/test_mutants_holdout.py` (6 mutants) | 6 passed: every mutant made the real test fail |
| scratch `verify/hand_check.py` | every hand figure equals the engine's booked figure and the test's expected value |

Verdict in one line: both test sets prove what they claim; no BLOCKER; two SHOULD-FIX items
(section 3), both on rarely taken resume paths of the puller, neither affecting a clean run.

## 1. Part A: holdout-2 sealing

Spec: reports/stage_d1f_confirmation_list.md sections 1.2 and 5.2 (FROZEN). Code:
data/holdout.py (770 lines), data/pull_mes.py (`--d1f-pull`, `RequestCappedGate`, `pull_d1f`),
data/adapter.py (`fetch_range`, unchanged: `git diff data/adapter.py` is empty). Tests:
tests/test_d1f_holdout2.py (61 tests).

### A(i) No plaintext of any of the 13 chunks after sealing: VERIFIED

What the real code path does (not the docstrings):

- `adapter.fetch_range` (data/adapter.py:85-144): refuses sealed ranges and existing targets
  (lines 97-106), quotes, authorizes, commits, then `client.timeseries.get_range(..., path=partial)`
  with `partial = <target>.partial` (117), `os.link(partial, target)` (122), `partial.unlink()`
  (126), `chmod 0444` (127), `delivered_record_bytes(target)` (129), settle. The hard link is the
  same inode as the partial, so after `partial.unlink()` exactly one directory entry holds the
  bytes. `delivered_record_bytes` (147-151) is `DBNStore.from_file(path).to_ndarray(count=1_000_000)`:
  in-memory decode, nothing written (audited below).
- `pull_mes.pull_d1f` (data/pull_mes.py:229-254): for each chunk oldest first, `fetch_range`
  (249) then, for a holdout-2 chunk, `ho.seal_holdout2_chunk(path, h2)` (251) in the same loop
  iteration, before the next iteration's request.
- `holdout.seal_holdout2_chunk` (data/holdout.py:637-690): refuse (609-634), read plaintext (650),
  seal in memory and prove the round trip in memory (652-653), write the blob with `"xb"` +
  fsync (657-661), prove the round trip FROM DISK (662-665), manifest record (667-671), SEALED log
  entry (673-680), re-pin the log (681-683), then `raw.unlink()` and `partial_path(raw).unlink`
  (685-686), and a final existence check that raises (688-689).

Is the test's search by content, and is the /tmp search real? Yes.
`_files_holding` (tests/test_d1f_holdout2.py:162-181) walks
`[world.root, /tmp, tempfile.gettempdir(), REPO_ROOT, ~/.cache/databento, ~/.databento,
$XDG_CACHE_HOME/databento]`, hashes every regular file whose size is one of the 71 payload sizes
(each payload is `4096 + 37k` random bytes, unique per chunk), and matches sha256 only; names are
ignored. The positive control (267-269) requires the same scan to find each of the 58 unsealed
chunks exactly once, at its target path, so the scan is known to work on the very run that asserts
absence. I confirmed the /tmp reach with a mutant: a copy of a sealed chunk's plaintext written
under a random name in `tempfile.gettempdir()` (= `/tmp` on this machine) makes `test_i` fail with
"sealed plaintext survived" (scratch `test_ma_...`, passed = detected; the copy was removed in a
`finally`). A mutant that re-creates the plaintext at its original path is also caught
(`test_mb_...`).

Does the stub client behave like databento 0.82.0? Yes for the path fetch_range uses. The
installed package is 0.82.0 at `.venv/lib/python3.12/site-packages/databento`. Sync
`BentoHttpAPI._stream` (common/http.py:116-152): `writer = open(path, "x+b")`, streams response
chunks into it, closes, returns `DBNStore.from_file(path)`; `historical/api/timeseries.py:124-131`
passes `path` straight through after `validate_file_write_path`. The stub's `_get_range`
(test:100-112) opens `path` with `"x+b"` and writes once. Every other write-mode `open(` in the
package is in `DBNStore.to_file/to_csv/to_json` (dbnstore.py:849, 1108-1122, 1182) and the batch
download API (historical/api/batch.py:520, 613), none of which fetch_range or the seal call.
`DBNStore.from_file` reads through `zstandard.ZstdDecompressor().stream_reader` (dbnstore.py:357-359,
543) in memory. The package sources contain none of `tempfile`, `mkstemp`, `NamedTemporaryFile`,
`gettempdir`, `diskcache` (TestVendorAudit, test:726-741, pins this to version 0.82.0 and fails on
any other version; it ran, not skipped, since databento is installed).

The `.partial` file and the hard link leave no copy: the stub writes only to
`partial_path(target)` and the test asserts that name no longer exists (test:271-273); the seal
also removes a stale partial (686) and `_verify_holdout2` treats a surviving partial as plaintext
present (716-717, 729-730).

### A(ii) 13 manifest records with both sha256: VERIFIED

`test_ii` (test:275-294): exactly 13 records, in chunk order, each with exactly the keys
`{original_path, original_relpath, sealed_relpath, bytes, sha256_plaintext, sha256_sealed}`,
`sha256_plaintext` equal to the sha256 of the bytes the stub wrote, `bytes` equal to the payload
length, the on-disk blob hashing to `sha256_sealed` and differing from `sha256_plaintext`;
`expected_raw_chunks` lists the 13 names; `unlock_log_at_seal` equals the log's current size and
hash; and the manifest text contains none of `rows`, `trade_dates`, `close`. Per chunk the manifest
holds bytes, hashes and paths only (data/holdout.py:667-669), matching 1.2 ("only bytes and
sha256, no row counts and no dates"). The top-level `holdout_start_trade_date` /
`holdout_end_trade_date` (598-600) are the declared bounds, not data-derived. A mutant that strips
`sha256_sealed` from the records is caught by `test_ii` (scratch `test_md_...`).

### A(iii) verify_seal all_ok with plaintext absent: VERIFIED

`_verify_holdout2` (data/holdout.py:706-740) reports, per record, `sealed_ok` (blob exists and
hashes to `sha256_sealed`) and `plaintext_absent` (neither the original path nor its `.partial`
exists, both spellings of the path), plus `state`, `sealed_in_order`, `unsealed_plaintext_present`
(unsealed chunks or partials on disk), `unlock_log_ok` (pinned prefix), and
`confirmation_has_no_holdout2_rows` (None when the confirmation parquet is not built; the parquet
is read for `trade_date` only). `all_ok` (735-739) requires state `sealed`, in order, log intact, no
unsealed plaintext, the parquet not dirty, and every record `sealed_ok and plaintext_absent`.
`test_iii` (test:296-304) asserts all of it for the 13; `test_plaintext_of_a_sealed_chunk_on_disk_stops_the_pull`
(487-495) shows `all_ok` and `plaintext_absent` go False when a plaintext reappears; the parametrised
parquet test (560-568) shows a 2024-03-01 row flips `all_ok` to False.

### A(iv) The confirmation loader (screening/runner.py, data/research_bars.py, tests/test_d1f_confirmation_window.py): VERIFIED

`load_confirmation_bars` (data/research_bars.py:183-195) pushes down a `[2019-05-01, 2024-02-29]`
filter and then re-checks every returned row through `assert_confirmation_rows` (144-147) ->
`refuse_non_confirmation_dates` (134-141): every date must classify as `confirmation`
(`DATE_CLASSES`, 83-90, a gap-free partition pinned by a test), refusing holdout-1, holdout-2,
embargo-2, research-embargo, mined and pre-MES dates in that order, and then an explicit
`max(trade_date) <= 2024-02-29` assertion (139-141) that stands even if the class table were
mis-declared (test:254-262). `ConfirmationWindow.__post_init__` and `_screen_confirmation`
(runner diff) run the same refusal on the window's dates, and `screen_candidate` dispatches a
`ConfirmationWindow` to a path that reads only the confirmation parquet (booby-trapped research
entry points in the test's `confirmation_run` fixture). Tests cover the filter (236-242), the
re-check with the pushdown filter broken (245-251: 2024-03-01, 2024-03-29, 2024-04-01, 2024-12-31,
2025-03-31, 2025-04-01, 2026-05-13, 2026-06-12, 2026-06-16, 2026-06-22, 2026-09-16), the forced
window (321-329) and the null generator. My own direct call of `refuse_non_confirmation_dates` on
the boundary dates:

```
2024-02-29 ALLOWED
2024-03-01 REFUSED: embargo-2 (March 2024, in a sealed chunk) ...
2024-03-31 REFUSED: embargo-2 ...
2024-04-01 REFUSED: holdout-2 (sealed, 2024-04-01..2025-03-31) ...
2025-03-31 REFUSED: holdout-2 ...
2025-04-01 REFUSED: mined research-slice (train union, test folds, EDA; 2025-04-01..2026-06-12) ...
2026-06-22 REFUSED: holdout-1 (sealed, 2026-06-22 on) ...
2019-04-30 REFUSED: pre-MES (before 2019-05-01) ...
```

### A(v) `python -m data.holdout status` reports both holdouts: VERIFIED

`status_report` (data/holdout.py:743-746) returns holdout 1's report with its keys unchanged at
the top level plus a `holdout_2` section; `main` prints it (751-753). Run at the start of this task:
holdout 1 `all_ok true`, four raw files `sealed_ok/plaintext_absent true`, `unlocks_logged 0`;
`holdout_2.state not_yet_sealed`, `chunks_sealed 0`, `unsealed_plaintext_present []`,
`unlocks_logged 0`, `all_ok false`. `test_v` (test:306-320) checks both before and after a full
synthetic pull. Process note for later sessions: until the last chunk is sealed,
`holdout_2.all_ok` is False by design (735); the session-start check must read `state`.

### A, further questions from the brief

- Sealing in the same call, before the next request, oldest first: VERIFIED.
  `d1f_chunks` (pull_mes.py:186-192) is `monthly_chunks(2019-05-01, 2025-04-01)` and must equal
  `CONFIRMATION_RAW_CHUNKS + HOLDOUT2_RAW_CHUNKS` (58 + 13, ascending; test:215-222). The loop seals
  at line 251 inside the iteration that bought the chunk. `test_each_chunk_is_sealed_before_the_next_is_requested`
  (test:249-253) reads the manifest count inside the stub at every download and requires
  `[0]*58 + [0, 1, ..., 12]`. Mutants: deferring each seal to the next request (`test_mc_...`) and
  reversing the order (`test_me_...`) are both caught. `next_holdout2_chunk` (holdout.py:560-566)
  and `_refuse_holdout2_seal` (622-624) refuse any out-of-order seal, and `pull_d1f` refuses to
  BUY out of order before quoting (246-248; test:355-360).
- Can a failure leave plaintext behind or continue the pull? A failure stops the pull (no
  `except` around the seal; `main_d1f` catches only `BudgetRefusedError`) and keeps the plaintext
  on disk, by design ("paid raw data is never lost"): `test_a_sealing_failure_stops_the_pull_keeps_the_plaintext_and_resumes`
  (test:438-465, corruption at chunk 3: manifest has 2 records, plaintext of chunk 3 intact, no
  blob, nothing after it requested; the resume seals it without re-buying), `test_a_crash_before_the_manifest...`
  (467-485: orphan blob blocks the rerun, plaintext kept), `test_removal_waits_for_the_proof_from_disk`
  (526-540). Plaintext kept after a failure is the intended fail-closed state, not a leak past the
  seal; `verify_seal` reports it. Two resume-path gaps are listed in section 3 (D1, D2).
- Can the puller re-buy a sealed chunk? No, on three layers: `pull_d1f` skips a chunk listed in
  either manifest (232-238) and any plaintext on disk (239-244); `fetch_range` refuses through
  `is_sealed_raw` with no `paths` (both manifests, holdout.py:275-285) and through
  `request_touches_sealed_window` (196-201), which now also returns True for any request
  overlapping a sealed holdout-2 chunk (any schema); the A.1 `--pull` path uses the same defaults
  (test:414-434). Tests: rerun buys nothing (337-345), holdout-1-listed chunk skipped (347-353),
  every download path refuses (362-378). Mutant: ignoring the holdout-2 manifest in `is_sealed_raw`
  is caught (`test_mf_...`).
- Holdout-1 behaviour unchanged: VERIFIED. `git diff --stat HEAD -- docs/HOLDOUT_MANIFEST.json
  tests/test_holdout.py docs/HOLDOUT_UNLOCK_LOG.md REGISTRATION.md data/adapter.py` is empty;
  `sha256(tests/test_holdout.py)` at HEAD equals the working copy
  (7a16b0ac...d62752). tests/test_holdout.py passes unchanged (in the 100). In data/holdout.py the
  holdout-1 code paths keep their logic: `STAGE_PATTERNS[1]` is the Stage C regex verbatim (97),
  `unseal_raw_file`'s holdout-1 heading is unchanged (363-364), `verify_seal` for holdout 1 is the
  old body behind an `if paths.holdout_id == 2` dispatch (395-396), `prior_unlocks` counts the same
  headings for holdout 1 (only headings containing " UNLOCK holdout 2 " are excluded, which no
  holdout-1 ceremony can produce because its stage regex cannot contain "holdout 2"). `HoldoutPaths`
  gained two defaulted fields (117-118), so `DEFAULT_PATHS` is unchanged (test:662-669).
  Holdout 1 verifies after holdout-2 entries are appended to the shared log (test:685-689) and
  unlock counts are per holdout (633-650).

## 2. Part B: Family H look-ahead

Spec: list section 2.1 A3 (every bullet). Code: strategy/research/h_daily_bar/_mechanics.py and
the six modules. Tests: tests/test_d1f_h_daily_bar.py (68 tests).

### B.1 Look-ahead case re-derived by hand: VERIFIED (H1; H6 also shown)

Inputs: the test's Day specs (tests/test_d1f_h_daily_bar.py:87-138, 179-196), the frozen table,
sim/slippage_calibration.json (read directly, not through sim.costs) and sim/fill_model.py's
booking rule (commission 61 c per micro per side = half of $1.22; slippage cents =
ceil(qty x slip_ticks x 125) at the FILL bar's 15-minute CT bucket, size bucket = smallest
calibrated size >= qty, so 2 micros pay the "5" bucket).

Condition value for day d = DAYS[4] = 2025-09-12 (H1, NR4). Each `up(i, r)` session has its
08:30 bar spanning 5999.00..6001.00 and a 12:00 wick to 5999.00 + r/4, so Range = r ticks:
ranges by day = 40, 36, 32, 20, 44, 36, 24, 40 (all eight days complete: 08:30 and 14:59 bars,
one instrument A, no halt). Prior complete bars for day 4 are days 0..3; values in table order
(Range[d-1], Range[d-2], Range[d-3], Range[d-4]) = (20, 32, 36, 40); 20 < 32, 20 < 36, 20 < 40 ->
holds. Engine: `Condition(holds=True, values=(20.0, 32.0, 36.0, 40.0))`, equal to the test's
`case.before`. Replacing day 3 by `up(3, 32)`: (32, 32, 36, 40); 32 < 32 is false -> holds False;
engine `Condition(False, (32.0, 32.0, 36.0, 40.0))` = `case.after`. Day d scaled x1.01: day 4's
own range stays 44 ticks and its condition is unchanged (it reads only days 0..3).

Fills and P&L for that trade (2 micros): OR over the 30 bars 08:30..08:59 = [5999.00, 6001.00]
(only the 08:30 bar is not flat). The explicit 10:00 bar is (6000.00, 6001.25, 6000.00, 6001.25):
close 6001.25 > OR_high 6001.00 -> BUY 2 decided on the 10:00 bar (decision stamp 10:01), fills at
the 10:01 bar's OPEN; the `steps` set the level to 6001.50 from 10:01, so entry = 6001.50. Exit:
the 14:58 bar is the first with CT time >= 14:58 and before 15:08 -> SELL 2 decided (stamp 14:59),
fills at the 14:59 bar's open = 6003.00 (step at 14:59). Gross = (6003.00 - 6001.50)/0.25 = 6 ticks
x 2 micros x 125 c = +1500 c. Entry side cost: bucket 10:00, size 5 mean 0.5639 ticks
(slippage_calibration.json `buckets_ct["10:00"]["5"]["mean"]`): commission 2 x 61 = 122 c;
slippage ceil(2 x 0.5639 x 125 = 140.975) = 141 c; side = 263 c. Exit side: bucket 14:45, size 5
mean 0.5306: 122 + ceil(2 x 0.5306 x 125 = 132.650) = 122 + 133 = 255 c. Net = 1500 - 263 - 255 =
982 c = $9.82. Engine (scratch `hand_check.py`, FillEvent fields): entry `comm=122 slip=141`,
exit `gross=1500 comm=122 slip=133`, booked 982 c; the test's `net_cents` = `1500 - 263 - 255` =
982 and `report.net_pnl_usd == 9.82`. Agreement to the cent.

H6 by hand: day 0 has H 6005.00, L 5995.00, C 6004.00 -> CLV = (6004 - 5995)/(6005 - 5995) =
0.9 >= 0.8 -> BUY decided on day 1's 08:30 bar, fills at the 08:31 open 6000.50 (bucket 08:30,
size 5 mean 0.5605: 122 + ceil(140.125) = 263 c), exit at the 14:59 open 6002.00 (255 c): +1500 -
518 = 982 c. Day 2 C 5996.00 -> CLV 0.1 <= 0.2 -> SELL on day 3: 5999.50 in, 5998.00 out, +1500 -
518 = 982 c. Total 1964 c = $19.64 = test value `2 * (1500 - 263 - 255)`. Replacement day 0 with C
6002.75: CLV = 7.75/10 = 0.775 (31/40 in ticks) -> neither cut -> holds False, equal to
`case.after`. The engine booked 1964 c. The other four cases (H2, H3, H4, H5) were run the same way
and agree (H5: gross -1500, net -2018 c; the fade sells the up breakout).

### B.2 The look-ahead pair fails when the module reads day d's bars: VERIFIED (by mutants)

Two leaks were inserted by monkeypatching `_mechanics.DailyBarStrategy` in process (never the
files): M1, the condition computed at day d's close with day d's own complete bar as "d-1"
(the classic off-by-one); M1b, day d's 08:30 bar appended to the history at evaluation time. For
all six modules `test_condition_ignores_day_d_and_follows_day_d_minus_1` fails under both. Where it
fails matters: on the by-hand assertion `records[day].condition == case.before` (test:323) and
the d-1 replacement (337), NOT on the scaled-copy assertion (332). Measured: x1.01 on the 0.25
grid leaves every probe day's tick range unchanged (H1 44 -> 44, H2 40 -> 40, H3 48 -> 48, H4 40
-> 40, H5 40 -> 40, H6 40 -> 40) and CLV exactly unchanged, so a module using day d's own
range or CLV would pass "condition unchanged under scaling". The frozen text prescribes x1.01, the
test implements it, and the pair as a whole still catches the leak through the hand-computed
values; see NOTE N1.

### B.3 The other checks

| Check | Code | Test | Mutant (must fail the test) | Status |
|---|---|---|---|---|
| OR uses only [08:30, 09:00), needs the 08:30 bar and >= 25 of 30 bars | `_accumulate` adds to the OR only when `at < OR_END_CT` (=09:00) inside RTH (_mechanics.py:306-309); `or_ok = has_open_bar and or_bars >= 25` (327) | 387-402 (09:00 wick excluded, 08:59 wick included, 09:00 bar is the first trigger bar), 505-513 (25 vs 24 bars) | M2 `OR_END_CT` = 09:01: caught | VERIFIED |
| Breakout trigger reads the CLOSE, strict, in [09:00, 14:30) | `bar.close > or_high` / `< or_low` (331-334); `at >= ENTRY_END_CT` (=14:30) blocks (328) | 405-416 (high pierces, close equals OR_high: no trade) | M3 trigger on high/low: caught; M4 non-strict: caught | VERIFIED |
| One entry per trade date, first side breached | `day.entry_side` set on the first `_enter`; later bars go only to `_exit` (262-263) even when the engine refused the entry | 438-449 (blackout refusal, no re-entry at 11:00) | M8 re-entry after refusal: caught | VERIFIED |
| Fill at the next bar's open | engine: pending market orders fill at the next bar's open (sim/engine.py:521-533; `fill_ts_ns` = fill bar's open, 438); decision stamp = bar open + 60 s | intents at 10:01 / 14:59 stamps, fills at the 10:01 / 14:59 opens (405-416); leakage canaries 15 passed | (engine, not H) | VERIFIED |
| Exit on the first bar >= 14:58 before the no-new-positions time; forced flatten counted and logged | `_exit` (349-360): `at < EXIT_CT` -> nothing; `before_cutoff` uses `no_new_positions_time_ct(bar.early_halt_ct)` and the bar flag; otherwise `_mark_forced`; `_close_day` marks a position still open at session end (285-287); WARNING log | 405-416, 419-435 (gap to 15:08 -> engine flatten at 15:10, reason `forced_flatten`; session ends 14:57 -> `forced_flatten_session_end`; `forced_exit_dates`, caplog) | M5 `EXIT_CT` = 14:57: caught | VERIFIED |
| Instrument guard and exemptions (H-1, NEW-9) | `_evaluate` (311-320): the last `guarded_bars` complete bars must carry the 08:30 bar's instrument_id; GUARDED_BARS = 1 (H1, H2, H4, H5, H6), 2 (H3) | 516-537 (roll between d-1 and d blocks all six; roll between d-2 and d-1 blocks only H3) | M7 guard dropped: caught for all six | VERIFIED |
| Complete-day rule; incomplete days do not exist for lookbacks | `_Day.daily_bar` (193-201): 08:30 bar, 14:59 bar, no halt, one instrument over RTH bars; `_close_day` appends only complete bars (288-290) | 482-502 (missing 14:59, missing 08:30, two instruments, early halt -> day 3 is d-1 for day 5), 453-462 | M6 lenient completeness: caught | VERIFIED |
| Early-halt days: no trade | `_evaluate` returns on `day.early_halt` (313); `_enter` and `_breakout` re-check (343, 328) | 453-462 | (covered by M6's early_halt branch) | VERIFIED |
| Inequalities (H-6) | strict `<` in `narrowest_range` (126) and H3 (h3:30-31); `<=` H4 (h4:43), `>=` H5 (h5:44), `>= 0.8` / `<= 0.2` H6 (h6:37-39) | ties: H1 32 vs 32 false (222), H3 equal lows false (233), H4 32 <= 32 true (240), H5 44 >= 44 true (246), H6 exactly 0.8 / 0.2 trade (352-353) | M4 (triggers) | VERIFIED |
| Percentile call (H-7) | `np.percentile(baseline, q, method="linear")` over `window[:-1]`, the 60 (test: 6) complete ranges before d-1 (129-139); q literals 33.33, 66.67 (h4:31, h5:32) | 234-246 hand cuts (index 1.6665 -> 32.0; 3.3335 -> 44.0) and 356-366 at the production lookback 61 (16.647, 23.353); my recomputation agrees | - | VERIFIED |
| Factories argument-free; warm-up override private (H-4) | `factory()` takes nothing (each module); `_lookback` is keyword-only, private, default `LOOKBACK` = 61 (h4:47, h5:48); `condition.__kwdefaults__ == {"_lookback": 61}` | 551-571 (`inspect.signature(factory).parameters == {}`, `"_lookback" not in getsource(factory)`, production lookbacks 4/7/2/61/61/1, labels equal the table IDs) | - | VERIFIED |
| Modules read no file, frame, configuration or hindsight field | imports restricted to an allow-list; `vendor_degraded_day` absent; 8 files, <= 800 lines | 574-593 | - | VERIFIED |
| Synthetic bars only (R-7) | tests use `run_backtest` / `screen_frame` on frames built in the test | test docstring; no loader import | - | VERIFIED (nothing under `data/processed` is read by this test file) |
| Leakage canaries pass after the modules were added | - | 15 passed | - | VERIFIED |

### B.4 The worker's four readings against the frozen text

1. "early_halt_ct read per calendar date d": CONSISTENT. The frozen text says "the date has
   early_halt_ct null" and "Days with early_halt_ct set: no trade". data/bars.py:171-182 attaches
   `early_halt_ct` per CT calendar date (`halt_by_date[d] for d in local_date`), so every bar of CT
   date d carries the same value and the evening bars of trade date d (CT date d-1) carry d-1's.
   Reading it from the bars dated d makes "the date" mean day d's own RTH date and keeps the
   Tuesday after a Monday early-halt tradable, which the frozen text does not forbid. Note the
   engine turns the builder's "" into `None` (sim/engine.py:121, 131) and refuses any non-time
   value (strategy/interface.py:174-175), so the `is not None` test in `_accumulate` (294) is
   sound on real bars.
2. "clock windows count only bars dated d": CONSISTENT. Every window in A3 ([08:30, 15:00),
   [08:30, 09:00), [09:00, 14:30), >= 14:58, the 14:59 close) lies inside the RTH calendar date of
   trade date d; the bars of trade date d on CT date d-1 are 17:00-23:59 and belong to no window.
   `on_bar` returns `()` for them (256-258), which cannot change any window's content.
3. "d-1 = the latest complete daily bar before d": CONSISTENT, it is the frozen text verbatim
   ("Incomplete days do not exist for the lookbacks: 'the last k daily bars' means the last k
   complete ones"; "Conditioning for day d uses only complete daily bars of trade dates strictly
   before d").
4. "exit window [14:58, no-new-positions time)": CONSISTENT, verbatim ("on the first bar the
   strategy sees with CT time >= 14:58 and before the engine's no-new-positions time").

### B.5 One reading of the frozen text the test takes that the lead should know

Bullet 3 says "a synthetic 8-day series with one NR4 day, one NR7 day, one inside day, a
bottom-tercile and a top-tercile day (...) and CLV 0.9 / 0.1 days". The test builds one 8-day
series per module (six series, `CASES` 215-257), each containing that module's event day(s) and
producing exactly the specified trade to the cent. All the listed events and trades are present;
they are not in a single shared series. I read this as within the text (each series is an 8-day
synthetic series) and as the cleaner known-answer design; flagged only so the lead is not
surprised (N3).

## 3. Defects

No BLOCKER.

D1. SHOULD-FIX. Resume path seals a chunk without the record-byte check. data/pull_mes.py:239-242:
when a holdout-2 chunk is found on disk (an earlier pull was interrupted after `os.link` in
`fetch_range`), it is sealed as is. If the interruption fell between the link (adapter.py:122)
and the settle (134), `delivered_record_bytes` never ran on that chunk, so the chunk is sealed
without the "one decode" of 1.2 and the ledger keeps the pessimistic commit with no settle. The
seal is still byte-exact, so this is not a leak. Fix: in that branch call
`delivered_record_bytes(target)` (the same single decode; import from data.adapter) before
`seal_holdout2_chunk`, and put the delivered byte count into the `note` so the SEALED log entry
records that the check ran on resume. The stub-based tests keep working because
`delivered_record_bytes` is already monkeypatched by the autouse fixture.

D2. SHOULD-FIX (low). A crash after the manifest record is written but before `raw.unlink()`
(holdout.py:671-685) leaves a chunk that is listed as sealed with its plaintext still on disk.
`pull_d1f` then stops with "an earlier seal was interrupted" (232-235) and `verify_seal` reports
`plaintext_absent False`, which is fail-closed, but the only way out is a manual removal of paid
raw data by hand. Fix: add `complete_interrupted_seal(target, paths)` that re-reads the blob,
requires `sha256(blob) == record["sha256_sealed"]` and `open_sealed(blob, ...)` to decrypt to
`record["sha256_plaintext"]` (the same proof that licenses removal on the normal path), appends a
"plaintext removed on resume" log entry, re-pins the log, then unlinks; have `pull_d1f` call it in
the 232-235 branch instead of raising. Until then, write the manual procedure into the run
prompt's STATE checklist.

N1. NOTE. The scaled-copy half of the look-ahead pair is a weak detector by itself: x1.01 on the
0.25 grid leaves tick ranges and CLV unchanged for every probe day (section B.2). The pair is
sound because of the hand-computed `case.before` and the d-1 replacement, both present. The
frozen text fixes x1.01, so no change to the existing test; if the lead wants the scaled
assertion itself to bite, add a second, separately named test (outside the frozen wording) that
replaces day d by a copy with a different tick range (for example x1.5, or a different 12:00
wick) and asserts the condition is unchanged.

N2. NOTE. Holdout-2 ceremony stage argument. 1.2 says "with 'holdout 2' named in the stage
argument" and, in the same paragraph, that the argument "must match
`(stage\s+)?d\.2(\s+holdout\s+2)?` exactly (L-3)", where the "holdout 2" group is optional. The
code implements the L-3 regex (holdout.py:97) and the test pins both "d.2" and "stage d.2 holdout
2" as accepted for holdout 2 (test:572-588, 633-650). The log heading always names the holdout
("UNLOCK holdout 2 raw file (...)"). The frozen text is internally inconsistent here; the code
cannot satisfy both readings. A lead decision for the D.2 declaration, not a code change now.

N3. NOTE. Bullet 3 of the look-ahead list is implemented as six 8-day series, one per module,
not one shared series (section B.5). All specified events and trades are present.

N4. NOTE. The synthetic H bars are dated 2025-09-08..2025-09-17, inside the mined research-slice
date range. Harmless today because the tests call `run_backtest` / `screen_frame` directly and
no loader or date refusal is involved, and no real bar is read; but a future tightening of
`screen_frame` to refuse mined dates would break the test for a reason unrelated to Family H.
Recommend moving `DAYS` to a neutral range (for example March 2021, as
tests/test_d1f_confirmation_window.py does) when the test is next touched.

N5. NOTE. `test_i`'s scan skips unreadable directories silently (`os.walk(onerror=None)`) and
only hashes files whose size equals a payload size. Both are the right choices for a by-content
search of exact copies (a plaintext copy is byte-identical), and the positive control proves the
scan works on each run; a truncated or recompressed copy would not be found, and no code path
produces one.

N6. NOTE. `holdout_2.all_ok` is False by design until the 13th chunk is sealed (holdout.py:735).
The session-start invariant for every later session should be phrased as "holdout 1 all_ok true;
holdout 2 state sealed and all_ok true once the purchase has run, else not_yet_sealed with
unsealed_plaintext_present empty".

N7. NOTE. `main_d1f` (pull_mes.py:293-301) catches only `BudgetRefusedError`; a
`SealIntegrityError` surfaces as a traceback with a non-zero exit. The pull stops either way, which
is what 1.2 requires; a friendlier message is optional.

## 4. Holdout invariant at the end of this task

`uv run python -m data.holdout status` at the end: holdout 1 `all_ok true, unlocks_logged 0`;
holdout 2 `state not_yet_sealed, chunks_sealed 0, unsealed_plaintext_present [], unlocks_logged 0`.
No scratch leftovers under `/tmp` (`ls -d /tmp/verify_leak_*` empty). REGISTRATION.md 0 bytes.

## 5. What I could not check

- The real vendor round trip (a live `timeseries.get_range` writing a real `.partial`) is not
  exercisable here (zero Databento calls); the audit rests on reading the installed 0.82.0 sources.
- The confirmation parquet does not exist yet, so `confirmation_has_no_holdout2_rows` and the
  runner's `ConfirmationWindow` were verified on synthetic parquets only.
- The `(v)` requirement "at the start and end of every later session" is procedural; only the
  command's output was verified.
- data/cme_calendar.py, data/build_mes_bars.py, data/bars.py (beyond the early_halt_ct
  attachment at lines 171-182, read only), data/validate.py, strategy/research/_d1f_statistics.py
  and the E-H modules were still being edited by other workers and were not reviewed.
