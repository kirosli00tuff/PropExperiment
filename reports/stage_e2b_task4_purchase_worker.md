# Stage E.2b Task 4: purchase guard, step 2 path, step 2 bar store, free quotes (PurchaseCoder2-OpusXHigh)

Status: DONE 14:40 PDT 2026-09-26; follow-up rulings (OC-R, Q2, Q-6/b2) applied by 17:45 PDT. Section 1 (the store layout) was posted at 12:50 PDT and amended at 13:0x
for the lead's STEP2_ROOT ruling; nothing else in it changed. No purchase, no cap change; quotes only.

## 1. The step 2 store layout (for RunnerCoder and MLPipelineCoder)

Nothing below exists on disk yet (the step 2 history is not bought). Paths are relative to the repo root.
Module constants live in `data/step2_store.py` (the builder), `data/pull_step2.py` (the purchase) and
`data/step2_seal.py` (the sealed stores); read them from there, never re-spell them.

### 1.1 The built bar store (what screening and the ML route read)

- One parquet per product (root = the contract's root symbol, e.g. `NQ`, `ZN`, `MBT`), under its own
  base, separate from the research store (lead ruling 13:0x PDT: M7.4 and the V10 separate data roots, so
  the ML training job's data root can be this directory alone):
  `data/processed_step2/<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet`
  Constant `data.step2_store.STEP2_ROOT` (= data/processed_step2); function
  `data.step2_store.step2_parquet_path(root, base=STEP2_ROOT)` (never defaults to data/processed).
  `data/processed_step2/` is git-ignored (one line added to .gitignore, next to data/processed/).
- Trade dates: 2019-05-06 .. 2024-02-29 inclusive (the earliest possible S_X through the last
  confirmation / training date). The file holds EVERY trade date of that range the product has bars on;
  S_X (D4's start rule) is NOT applied in the store. The runner (confirmation window S_X..2024-02-29) and the
  ML route (training window S_X..2024-02-29, M1) cut at S_X themselves.
- Never in the file: any row whose CME trade date (the product's group calendar, data.group_session) is on
  or after 2024-03-01. The February 2024 chunk's rows booked to 2024-03-01 (the embargo) are dropped by
  trade date right after decoding, before any check or flag reads their prices, and are counted, never
  written. Rows before 2019-05-06 are dropped the same way. The builder refuses (raises) if any written
  trade date is outside 2019-05-06..2024-02-29 (a second check on the frame) and never opens a sealed chunk.
- Schema: identical to the research-window store of data/build_bars.py (`flag_frame` + MES's
  `_write_read_only_parquet`), column order:
  `ts_event` (int64, UTC ns, bar open), `open`, `high`, `low`, `close` (float64, vendor price units),
  `volume` (uint64 as decoded), `instrument_id` (uint32 as decoded), `raw_symbol` (string: the outright the
  instrument maps to on the bar's UTC date), `in_flatten_window` (bool), `in_no_new_positions_window`
  (bool), `early_halt_ct` (string, "" when none), `in_scheduled_closure` (bool), `trade_date` (string
  YYYY-MM-DD, as in the research store), `is_roll_session` (bool), `gap_before_minutes` (int),
  `vendor_degraded_day` (bool).
  Same rules as the research store: group calendar (data.group_session.load_group_calendar), group flatten
  policy (STAGE_E_POLICIES), rolls from the free symbology of `<ROOT>.v.0`, the D.1f raw-symbol rule (a bar
  is kept iff a `<ROOT>` outright is what symbology maps its instrument to on its UTC date), close-minute rule
  L-3, bars in a scheduled closure beyond the close minute held for the lead.
- File mode 0444, written with os.link (never over an existing file).
- Parquet schema metadata key `propexperiment` (JSON), the research store's fields plus step 2 fields:
  `source`, `stage` ("E.2b Task 4 (data/step2_store.py)"), `store` ("step2"), `flags_doc`,
  `flatten_rule`, `group`, `calendar_modules`, `builder_files`, `input_files` (name + sha256 of each
  unsealed chunk read), `tick`, `rolls`, `rolls_source`, `splice_trade_dates`, `roll_blackout_dates`,
  `degraded_vendor_days`, `degraded_on_store_trade_dates`, `raw_symbol_rule`, `drops` (counts by cause,
  including `embargo_rows_dropped_unread` and `before_first_trade_date`), `validation`, `trade_date_range`,
  `calendar_check_passed`, `day_session_rule`, `booked_forward_sessions`, `purchase_manifest` (path +
  sha256), `sealed_chunks_not_opened` (the 13 names), `harness_sha256` (preflight's return value).
- Build summary (counts, dates and flags only): `reports/step2/bars_<ROOT>.json`.

### 1.2 Raw purchase layout (what the builder reads; nobody else opens these)

- Unsealed chunks (58 per product, UTC dates, end exclusive), MES's layout (data.adapter.raw_path):
  `data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/range=2019-05-01_2019-06-01.dbn.zst` ..
  `range=2024-02-01_2024-03-01.dbn.zst`, 0444. The step 1 files (range=2025-04-01_.. through
  range=2026-06-01_2026-06-21) share the directory; the ranges never overlap.
- Holdout-2 chunks (13 per product: range=2024-03-01_2024-04-01 .. range=2025-03-01_2025-04-01, i.e. March
  2024 embargo plus holdout-2): sealed in the download call after the record-byte check, oldest first, one
  sealed store per product:
  `data/sealed/<ROOT>_holdout_v2/raw/range=<s>_<e>.dbn.zst.sealed`, manifest
  `docs/holdout2/<ROOT>_HOLDOUT2_MANIFEST.json` (bytes and sha256s only), the same append-only unlock log
  `docs/HOLDOUT_UNLOCK_LOG.md`, the same REGISTRATION.md requirement and cipher as MES's holdout 2.
  No plaintext of these ranges ever persists.
- Step 2 purchase manifest per product (the builder's expected sha256s and record counts):
  `reports/step2/purchase_<ROOT>.json`: per unsealed file `path`, `request_start`, `request_end`,
  `sha256`, `record_count`, `instrument_ids`, `first/last_ts_event_utc`, `session_id`; per sealed chunk only
  its name, plaintext bytes and sealed sha256.
- Rolls and symbology (free symbology.resolve, fetched once, never past 2024-03-01):
  `data/vendor/databento/rolls/<ROOT>_v_0_2019-05-01_2024-03-01.jsonl` and
  `data/vendor/databento/rolls/<ROOT>_v_0_2019-05-01_2024-03-01_symbology.json`.
- Vendor-degraded days: the frozen dataset-wide D.1f condition file
  `data/vendor/databento/condition/GLBX.MDP3_2019-04-01_2025-04-01.json` (already on disk).

### 1.3 Which products get a store

- ML route (M1): the 31 price-path contracts K1 NQ, RTY, YM; K2 ZT, ZF, ZN, TN, ZB, UB; K3 6E, 6A, 6B, 6C,
  6J, 6S, 6N; K4 CL, NG, RB, HO; K5 GC, SI, HG; K6 ZC, ZW, ZS, ZM, ZL, HE, LE; K7 MBT.
- Per cluster (lead ruling on InputsCoder Q-6, follow-up 2026-09-26): the cluster's TRADED vehicles
  (status chosen or undersized, D2 R10) plus every leg root its active members read, from the frozen
  catalog, MES excluded; K8 is legs only (`data.pull_step2.cluster_roots`, section 3.1).
- A product in both sets has one store (one purchase, one sealed store).
- Lead ruling OC-R: a contract listed after 2019-05 is bought from its first vendor-priceable month
  (MBT 2021-04, MCL 2021-06, MHG 2022-04; `data.pull_step2.FIRST_PRICED_MONTH`), so its store is built
  from fewer unsealed chunks (MBT 35, MCL 33, MHG 23; `data.step2_store.expected_names(root)`); the
  builder refuses any other input list. Every product still has all 13 sealed holdout-2 chunks.

Store builder entry (added after the layout was posted): `python -m data.step2_store --products <ROOT ...>
--harness-sha256 <sha256>`; `data.step2_store.run_product(root, expected_harness_sha256=...)` runs
`screening.harness_freeze.preflight(expected)` itself before any purchased file is read (so no caller can
skip it) and writes the returned sha256 into the summary and the parquet metadata (`harness_sha256`).

## 2. The guard fix (L-9): every purchase path refuses by CME trade date

New module `data/trade_date_guard.py`. For a product root and a request [start, end) it books every minute
to a CME trade date with the product's GROUP calendar (`data.group_session.open_intervals`, so early halts,
late opens, crypto's booked-forward days and the 24/7 weekend assignment are all included):
- a minute inside one of trade date D's open intervals is booked to D;
- the close minute (the first minute after a session ends) is booked to the session it closes (ruling L-3);
- any other closure minute carries no bar and is booked to nothing;
- booking is monotone in time, so minutes AFTER the last open interval the calendar can show could belong to
  any later date (holdout-1 included): such a request is refused by name (`CalendarCoverageRefused`); minutes
  BEFORE the first shown interval are refused the same way only if that interval's trade date is on or after
  2024-04-01 (no earlier date is a holdout date otherwise). This admits the step 2 first chunk
  2019-05-01 00:00 UTC for day-only calendars (livestock opens 08:30 CT on the coverage's first date).
`refuse_holdout_bookings(root, start, end, sealing=False)` refuses any minute booked to a holdout-1 date
(>= data.splits.HOLDOUT_START = 2026-06-22) on every path, and any minute booked to a holdout-2 date
(2024-04-01..2025-03-31, data.research_bars) unless `sealing=True` (the 13 chunks fetched through the sealing
download). Embargo dates (March 2024) are not a purchase refusal: the step 2 store drops them.

Where it is wired:
- `data/pull_universe.py` (step 1): new `TradeDateGuardError(DateGuardError)`, `check_trade_dates`,
  `validate_trade_dates`; the BUY run checks the whole plan before any vendor call and every piece again in
  `acquire` before it is quoted. `plan_requests()` still builds the historical E.1 plan and `--quote-only`
  still prices it (both pinned by existing tests; a quote delivers no bar). Consequence, stated plainly: the
  E.1 plan's 45 last chunks (range=2026-06-01_2026-06-21) are now refused by `--buy`: MBT's because the crypto
  calendar books 2026-06-18T21:02Z onward to 2026-06-22; the other 44 because the calendars end at 2026-06-19
  and cannot book the rest of those files (all 45 are bought and settled already; nothing is re-bought).
  Also `resume_scan` now looks only at files inside the step 1 window (`_in_step1_window`), because the step
  2 chunks share the directory and are settled under other sessions.
- `data/pull_step2.py` (step 2): `check_chunk` calls the guard with the chunk's sealing flag, for the whole
  plan before any call and again per chunk.
- `data/pull_mes.py` is NOT edited: a test proves its A.1 chunks either touch the sealed holdout-1 window
  (skipped by its timestamp guard) or pass the trade-date guard, its 58 D.1f unsealed chunks pass, and its 13
  holdout-2 chunks book holdout-2 dates and are exactly the ones it seals. `data/holdout.py` is NOT edited.

The MBT case for the lead's Task 9 DECISIONS entry:
`tests/test_e2b_trade_date_guard.py::test_mbt_request_ending_2026_06_21_is_booked_partly_to_holdout1_and_refused`
plants MBT's step 1 last chunk 2026-06-01..2026-06-21 (ends 00:00 UTC, the old timestamp guard's end) and
shows the crypto calendar books it partly to 2026-06-22, first booked minute 2026-06-18T21:02:00Z (Thursday
16:02 CT: Juneteenth and the weekend); the refusal names that minute and the holdout-1 date, with and without
`sealing`. `test_the_step1_buy_refuses_mbts_last_chunk_before_any_vendor_call` shows `pull_universe.run_buy`
refuses it with no metadata call, no download and no ledger line.

## 3. The step 2 purchase path

`data/pull_step2.py` (726 lines) with `data/step2_seal.py` (per-product sealing) and
`data/pull_step2_report.py` (the quotes markdown).
- Range: 71 monthly ohlcv-1m chunks of `<ROOT>.v.0` 2019-05..2025-03, oldest first, root by root; 58 kept
  (2019-05..2024-02, = data.research_bars.CONFIRMATION_RAW_CHUNKS) then 13 sealed (= HOLDOUT2_RAW_CHUNKS);
  asserted at import.
- Roots: only the 45 admissible step 1 contracts; MES (its own D.1f store) and the named refusals (PL, MET,
  NKD, 6M, ES) are refused.
- Modes: `--ml-route` (the 31 price-path contracts of M1, frozen as `ML_ROUTE_CONTRACTS`, checked against
  E.0's cluster map at import) or `--cluster K#` (the cluster's `status == "chosen"` vehicles read from
  reports/stage_e2a_vehicles.json, read-only; K7 has none and is refused by name).
- Gate: `step2_gate()` = `LockedQuoteGate(STAGE_E2B_SESSION_ID, account=ACTIVE_ACCOUNT)` = acct-2 with its
  registry cap ACCOUNT_2_CAP_USD ($125.00), session and request caps E2B_*_CAP_USD = $0.00.
- Buy (`run_buy`, `main --buy --harness-sha256 <sha>`): `harness_freeze.preflight(expected)` FIRST (main
  also runs it before loading the key or building a client), then `require_buy_caps` refuses any zero
  session or request cap (so the buy cannot start in E.2b), then the plan check, then per chunk: quote ->
  authorize (session cap, per-request cap via RequestCappedGate, acct-2's cap) -> commit -> download to
  .partial -> os.link -> 0444 -> record-byte check -> settle -> for a holdout-2 chunk `seal.seal_chunk`, before
  the next chunk is requested. No splitting (a chunk over the request cap is refused; D13's largest monthly
  chunk is about $0.12). The harness sha256 goes into every purchase manifest and every seal's log note.
- Sealing (`data/step2_seal.py`): data.holdout's seal_holdout2_chunk step for step (round trip in memory,
  "xb" blob + fsync, round trip from disk, manifest record, SEALED log entry, log pin, then plaintext removal),
  built from data.holdout's own primitives, with the product's own chunk paths: store
  data/sealed/<ROOT>_holdout_v2/raw/, manifest docs/holdout2/<ROOT>_HOLDOUT2_MANIFEST.json (adds `product`,
  `continuous`, `declaration`), the same unlock log and REGISTRATION.md. `verify(root, paths)` is
  _verify_holdout2 for the product; `python -m data.pull_step2 --status` prints every product's.
- No plaintext holdout byte persists: a failed download removes its .partial (commit stays, pessimistic); for
  a holdout-2 chunk ANY failure after the link (byte check, settle, seal) purges the plaintext (chmod then
  unlink, also on Windows) before the error propagates. Delivery above the quote: settled pro rata, sealed
  (holdout-2) or kept, then the run stops.
- Resume: kept chunk with file + settle line of the same request key (ANY session on acct-2: step 2 spans
  several sessions) is skipped; file without settle or settle without file -> ResumeStateError, nothing
  deleted. Holdout-2 chunk sealed -> skipped; sealed with plaintext left -> data.holdout.complete_interrupted_seal;
  on disk unsealed -> byte-checked and sealed (never re-bought); out of order -> refused before any buy.
- Purchase manifest reports/step2/purchase_<ROOT>.json updated after every chunk (inventory: sha256, record
  count, ids, first/last ts_event; sealed chunks only name, bytes, sealed sha256).
- `--quote-only --set ml-route|clusters [--retry-failed]`: forbidden guards on timeseries and batch, only
  `gate.quote`, 4 threads (quote_universe.MAX_WORKERS), no preflight (lead ruling: the quote run precedes the
  manifest). The summary is rebuilt from the ledger (latest successful quote line of each chunk under this
  session), so a retry and the first run form one report.

### 3.1 Follow-up rulings applied (lead, 2026-09-26, after the first report)

- OC-R (was Q1): `FIRST_PRICED_MONTH = {"MBT": "2021-04-01", "MCL": "2021-06-01", "MHG": "2022-04-01"}`,
  every other admissible root 2019-05-01. Source (stated in the code): the ledger's free quote lines, no
  new metadata call. The three roots failed every earlier month in BOTH E.0 (stage-E.0-2026-09-23) and
  this session with `422 symbology_invalid_request`, and priced every month from the listed one through
  2025-03; the 37 roots quoted in this session priced every month from 2019-05; the 8 others (M6E, E7,
  M6A, M6B, QM, QG, SIL, and MNG) have E.0's lines only. Consistent with E.0's notes (MBT before 2021-04,
  MCL before 2021-06, MHG before 2022-04). `plan_step2` starts each root there; earlier months are never
  requested and never counted as refusals; `check_chunk` refuses an earlier month by name
  (`Step2BeforeListing`, a Step2ChunkError) on the plan check, the quote run and the buy, before any
  call. The gate's "unpriceable request ... never assumed cheap" rule is unchanged inside a plan.
  MNG is refused for step 2 by name (`STEP2_UNPLANNABLE`): E.0 prices it 2019-05..2019-12 and from
  2023-10 but not 2020-01..2023-09 (a gap inside the range); it is in no step 2 set.
- Q-6 (cluster legs): `cluster_roots()` = traded vehicles (chosen or undersized, R10) + leg exposures
  (`CLUSTER_EXTRA_EXPOSURES`) resolved to their vehicles through the E.2a table. From the frozen catalog's
  "Products read" lines: K1..K7's active members read only their own cluster's vehicles (K6's crush
  member reads ZS, ZM, ZL, all K6 vehicles) plus non-GLBX data (VXN, ISM, event calendars; K3-mehedge-01's
  EURO STOXX 50 and Nikkei 225 daily indices, which step 2 cannot buy); K1's MES leg belonged to the
  excluded K1-ml-01. K8 (legs only): traded legs gold -> MGC, CAD -> 6C, Nasdaq-100 -> MNQ; signal legs
  S&P 500 on MES (excluded, owned), WTI crude on "the crude exposure's price-path bars ... CL's bars if CL
  ... is declared MCL's price path, otherwise the vehicle's own bars" (no declaration found, so MCL) and
  bitcoin on MBT. Result: K1 MNQ M2K MYM; K2 ZT ZF ZN TN ZB UB; K3 6E 6A 6B 6C 6J 6S 6N; K4 MCL NG; K5 MGC
  MHG; K6 ZC ZW ZS ZM ZL HE LE; K7 MBT; K8 MGC 6C MNQ MCL MBT (28 distinct roots). `--cluster` now takes
  K1..K8 and buys these. If E.2 ever declares CL as MCL's price path, K8 needs CL (priced in set (a)).
- Q2: `python -m data.holdout status` extended additively (the only edit to data/holdout.py):
  `status_report()` adds `holdout_2["products"]` = `data.step2_seal.verify_all(HOLDOUT2_PATHS)`, the
  verify of every per-product store that exists beside MES's (docs/holdout2/, data/sealed/), and a product
  store that does not verify turns the TOP-LEVEL all_ok False. With no store the key is {} and all_ok is
  holdout 1's as before (checked live: all_ok true, unlocks_logged 0, products {}). Deviation from the
  suggested top-level key name: the new key sits inside `holdout_2`, because the existing
  tests/test_d1f_holdout2.py::test_holdout1_status_is_unaffected_by_an_unsealed_holdout2 asserts that
  every top-level key except `holdout_2` equals holdout 1's verify_seal(); a new top-level key would fail
  it. A manifest file whose name is not a product root is reported not ok, never skipped.
- Q3 stays (shared unlock count, on the user's list); Q4 (Linux-only sealing) and Q6 accepted.

## 4. The E.2b spend policy (data/config.py)

Added after the E.1 block: `STAGE_E2B_SESSION_ID = "stage-E.2b-2026-09-26"`, `E2B_SESSION_CAP_USD = 0.00`,
`E2B_REQUEST_CAP_USD = 0.00` (the E.0 pattern), and `STEP2_ROOT = DATA_ROOT / "processed_step2"` (the lead's
store-root ruling). No other cap changed (ACCOUNT_2_CAP_USD stays $125.00, E.1's caps untouched).

## 5. The step 2 bar store builder

`data/step2_store.py` (see section 1). Reuses data/build_bars.py's per-product functions (ProductSpec,
verify_inputs, ensure_rolls, embedded_intervals, _roll_summary, _calendar_check, _raw_symbols, flag_frame,
write_parquet, degraded_days, the check summaries) and replaces only the orchestration, because
build_bars._flag_kept hard-codes the research date classes and its metadata says "E.2a research window".
Order: `refuse_inputs` (exactly the 58 unsealed names in order; any holdout-2/embargo chunk name, any file
under data/sealed/, any file listed in a holdout manifest (MES's two or the product's), any file outside
`<ROOT>_v_0/` is refused before a byte is read) -> sha256 + record counts -> decode -> `drop_outside_window`
(trade dates from ts_event alone; rows outside 2019-05-06..2024-02-29 dropped BEFORE any check reads a price;
a row booked to 2024-04-01 or later, or an unbookable row, raises HoldoutLeakError) -> MES's hard checks on
the window's rows over [first open of 2019-05-06, last close of 2024-02-29 + close minute) -> closure rule L-3
-> raw-symbol rule -> flags -> `refuse_non_confirmation_dates` -> parquet (0444, never overwritten) + summary.
Symbology for the D.1f raw-symbol rule is fetched free once over 2019-05-01..2024-03-01 by the CLI's client.

## 6. Tests (all synthetic or calendar-only; no network, no vendor price file, no Stage E parquet)

`tests/test_e2b_trade_date_guard.py`: 20 tests (13 functions, one parametrized over 9 roots).
- MBT ending 2026-06-21 00:00 UTC is booked partly to 2026-06-22 (first minute 2026-06-18T21:02Z) and
  refused, sealing or not; MBT up to 2026-06-18T21:00Z is admitted (the refusal is exactly the booking).
- `pull_universe.run_buy` refuses MBT's last step 1 chunk (TradeDateGuardError, a DateGuardError) with no
  metadata call, no download, no ledger line; the real ledger untouched.
- MNQ's last step 1 chunk is refused because the calendar cannot book 2026-06-19 close..06-21 00:00Z; the
  2025-04 chunk is admitted.
- ZN March 2024 chunk: refused unsealed (its last evening is trade date 2024-04-01), admitted when sealing.
- L-3: the close minute of 2025-03-31 (21:00Z) books to 2025-03-31 (holdout-2, refused); the closure minutes
  after it book to nothing.
- CL February 2024 books to 2024-03-01 (embargo) and is admitted (the store drops those rows).
- For NQ, ZN, 6E, CL, GC, ZC, HE, LE, MBT: all 58 unsealed step 2 chunks pass; the 12 sealed chunks after
  March 2024 are refused unsealed and admitted sealing.
- HE's 2019-05 chunk (before the day-only session of the calendar's first date) is admitted; a calendar whose
  first shown session is a holdout-2 date refuses the unknown minutes before it; empty requests refused.
- MES (pull_mes.py unchanged): every A.1 chunk not touching the sealed window passes, the 58 D.1f unsealed
  chunks pass, and each of the 13 holdout-2 chunks books a holdout-2 date (so only sealing may fetch it).

`tests/test_e2b_pull_step2.py`: 39 tests (29 functions; refused roots x8, post-download failure x2,
before-listing x3). Added for the follow-up rulings: MBT, MCL, MHG plans start at 2021-04, 2021-06,
2022-04 (48, 46, 36 chunks, all 13 sealed chunks kept); an earlier month (MBT 2021-03, MCL 2019-05, MHG
2022-03) is refused by name (Step2BeforeListing) by check_chunk, the buy and the quote run with no call
and no ledger line; MNG refused by name; the cluster mode's roots (K2 with the undersized ZT, ZF; K7 MBT;
K8 MGC 6C MNQ MCL MBT; 28 distinct, no MES; a thin table refuses "nothing to buy" and a missing leg
exposure); set b2 through `main` prices each of the 28 roots once and totals K8 over its legs; holdout
status: products {} and all_ok unchanged with no store, a partially sealed ZN store turns the top-level
all_ok False (holdout_2's own all_ok untouched) and all 13 sealed turns it True, a manifest named for no
root is reported not ok, and the product stores sit beside MES's in the repo. The plan and quote tests
were updated for OC-R (MBT 48 chunks; ml-route 2,178 chunks; the retry test now plants a transient ZN
failure, since MBT's pre-listing months are no longer requested).
- Plan: 71 chunks per root, oldest first, root by root, 58 kept then 13 sealed, exact request kwargs.
- ML route = M1's 31 contracts in order; clusters from the vehicle table (22 chosen vehicles; K7 none ->
  refused by name); exactly one of ML route / cluster.
- Refused roots MES, PL, ES, NKD, 6M, MET, ZZ, zn.
- check_chunk refuses a non-step-2 window (MBT June 2026, also refused by the guard as holdout-1), a partial
  month, a wrong sealing flag, a non-ohlcv schema; the guard is called with the chunk's sealing flag.
- Quote-only through `main`: no billable namespace touched (timeseries/batch raise "forbidden"), 2,201 new
  ledger lines all ("quote", $0.00, acct-2, stage-E.2b-2026-09-26); JSON + MD written; totals add up by
  contract and cluster; acct-2 spent/headroom from a planted E.1 line ($103.48 -> $21.52); top-up
  arithmetic; the key never printed; the real ledger and holdout manifests untouched.
- Quote failures (MBT before 2021-05) mark the set and K7 incomplete; `--retry-failed` re-quotes only the
  24 failed chunks and completes the set.
- Buy refuses when the harness preflight raises (run_buy and main: no key loaded, no client, no call, no
  ledger line); refuses with the E.2b $0.00 caps after running the preflight; `--buy` without
  `--harness-sha256` refused.
- Sealing order (ZN 2024-01..2024-05): the event sequence is download, check (x2 kept) then download, check,
  seal (x3); at each holdout download every earlier holdout chunk is already sealed and no holdout plaintext is
  on disk; ledger quote/commit/settle x5 on acct-2; verify: 3 sealed in order, blobs ok, no plaintext, log
  pinned; purchase manifest lists the 2 kept files (sha256, counts) and 3 sealed chunks with the harness sha;
  the unlock log gets 3 "SEALED holdout 2 ZN" entries and no UNLOCK.
- A download failing mid-chunk leaves neither the target nor the .partial (commit stays); a byte-check
  failure or a seal failure after the download purges the holdout plaintext and leaves no manifest.
- Delivery above the quote: settled pro rata, sealed, run stops.
- acct-2 cap: $110 of acct-1 spend does not block acct-2; $124.99 of acct-2 spend refuses the next chunk
  ("account cap acct-2", a refused line); a $0.01 request cap refuses ("per-request cap").
- Resume: a second run skips all 5 chunks without a quote or a download; a settle from another session on
  acct-2 is accepted; a downloaded-but-unsealed holdout chunk is sealed without a purchase; a seal cut off
  after its manifest record leaves no plaintext and the next run skips it; a sealed chunk whose plaintext
  reappears is finished by complete_interrupted_seal; a kept file without a settle line stops the run and is
  not deleted; a holdout chunk out of order is refused before any call.
- step2_seal refuses MES, a raw file outside the product's path, and a manifest of another product;
  `status` reports "not_bought".

`tests/test_e2b_step2_store.py`: 12 tests (11 functions; sealed-name swap x2). Added: MBT's store
expects its 35 unsealed chunks from 2021-04 and refuses the full 58-name list.
- The store path is under data/processed_step2, never data/processed; names as in section 1.
- End to end on 58 synthetic ZN chunks: 10 rows decoded, 2 before 2019-05-06 and 3 booked to 2024-03-01
  dropped (the embargo rows are off-tick with high < low, so any check reading them would fail the build;
  the raw checks report 0 off-tick prices); 5 rows written, trade dates {2019-05-06, 2024-02-29}; the exact
  column order; degraded-day flag; metadata (harness sha, store, range, 13 sealed names, purchase manifest
  sha); 0444; summary sha = file sha.
- An existing store is never overwritten; a holdout-2 row inside an unsealed file raises HoldoutLeakError and
  nothing is written.
- A holdout-2 or embargo chunk name in the inputs is refused before any file is opened (the loader fails the
  test if called); inputs under a sealed store or listed in a holdout manifest are refused; a missing chunk, a
  foreign manifest and a file outside `<ROOT>_v_0/` are refused.
- The CLI and run_product refuse when the preflight raises (no file read, no summary written); the CLI passes
  the expected sha to every product; run_product records the preflight's returned sha.

Existing tests of the touched files, unchanged and passing: tests/test_pull_universe.py (57),
test_holdout.py, test_d1f_holdout2.py, test_d1f_preflight.py, test_d1e_quotes.py, test_spend_gate.py,
test_spend_gate_accounts.py, test_quote_universe.py: 357 passed together with the new files (13:05 PDT,
through heavy.sh, 120 s). Coverage of the new modules (pytest-cov, the three new files): pull_step2 93%,
step2_seal 91%, step2_store 90%, trade_date_guard 100%, pull_step2_report 100%; total 93%.

## 7. The free quote run (reports/stage_e2b_step2_quotes.json and .md)

Session stage-E.2b-2026-09-26 on acct-2, caps $0.00 / $0.00, ohlcv-1m 2019-05-01..2025-04-01, each
contract from its first vendor-priceable month (OC-R). All runs through heavy.sh (nice 10), 4 threads:
- set (a) ML route: 13:08:16-13:58:37 PDT, 2,201 chunks quoted, 23 failed (MBT 2019-05..2021-03);
- set (b) chosen vehicles: 13:59:01-14:31:55 PDT, 1,562 quoted, 60 failed (MCL 2019-05..2021-05, MHG
  2019-05..2022-03);
- after OC-R, (a) and (b) re-summarized from this session's ledger lines with `--retry-failed` (16:51
  PDT; 0 new quote calls, 0 new lines): their plans no longer contain the 83 pre-listing months, so both
  are COMPLETE (2,178 and 1,502 chunks) with totals unchanged;
- set (b2) vehicles + legs: 16:51:46-17:37:55 PDT, 1,905 chunks, 0 failed, a full fresh run. Every one of
  its 28 contracts re-priced to exactly the (a)/(b) figure.
All 83 first-pass failures were `422 symbology_invalid_request` (months before listing); none transient.

acct-2 by the gate's own arithmetic (SpendGate.account_spent_usd = sum of `usd` over this repo's acct-2
lines): spent **$103.477194** (all E.1: commits $103.477194, settle deltas $0.000000, 904 requests), so cap
headroom under ACCOUNT_2_CAP_USD $125.00 = **$21.522806** = credit left of the $125.00. The $21.52 figure
is verified. (It includes 3 requests committed twice, $0.316080; see Q6.)

How to read the top-ups: a set's top-up buys that whole set against today's $21.52; a cluster's top-up is
that cluster ALONE against today's $21.52 (cluster rows do not add; K8 shares all its roots with K1, K3,
K4, K5, K7).

### Set (a): the ML route's 31 price-path contracts: $189.31 (D13's frozen upper figure is $189.31)

| Cluster | Contracts | Quoted | Top-up at quote | Top-up at quote + 10% |
|---|---|---:|---:|---:|
| K1 | NQ, RTY, YM | $22.53 | $1.01 | $3.26 |
| K2 | ZT, ZF, ZN, TN, ZB, UB | $40.50 | $18.98 | $23.03 |
| K3 | 6E, 6A, 6B, 6C, 6J, 6S, 6N | $49.34 | $27.81 | $32.75 |
| K4 | CL, NG, RB, HO | $25.21 | $3.68 | $6.20 |
| K5 | GC, SI, HG | $22.10 | $0.58 | $2.79 |
| K6 | ZC, ZW, ZS, ZM, ZL, HE, LE | $26.52 | $5.00 | $7.65 |
| K7 | MBT (from 2021-04, 48 chunks) | $3.11 | $0.00 | $0.00 |
| **Set** | 31 contracts, 2,178 chunks, complete | **$189.31** | **$167.79** | **$186.72** |

acct-2 cap needed for the whole set: $292.79 ($311.72 with 10%). Per contract (total; kept 2019-05..2024-02
+ sealed 2024-03..2025-03 in the .md): NQ $7.62, RTY $7.34, YM $7.57, ZT $6.01, ZF $6.98, ZN $7.23, TN $6.59,
ZB $6.80, UB $6.88, 6E $7.50, 6A $7.39, 6B $7.09, 6C $7.05, 6J $7.47, 6S $6.21, 6N $6.62, CL $7.57,
NG $6.86, RB $5.29, HO $5.49, GC $7.55, SI $7.21, HG $7.34, ZC $4.67, ZW $4.53, ZS $5.11, ZM $4.39,
ZL $4.88, HE $1.47, LE $1.48, MBT $3.11. Largest single chunk $0.1161 (NQ), far under D13's $3.00 cap.

### Set (b): each cluster's chosen vehicles only (as first briefed): $128.34

| Cluster | Chosen vehicles | Quoted | Top-up at quote | Top-up at quote + 10% |
|---|---|---:|---:|---:|
| K1 | MNQ, M2K, MYM | $22.11 | $0.59 | $2.80 |
| K2 | ZN, TN, ZB, UB | $27.51 | $5.99 | $8.74 |
| K3 | 6E, 6A, 6B, 6J, 6S | $35.67 | $14.15 | $17.71 |
| K4 | MCL (from 2021-06), NG | $11.46 | $0.00 | $0.00 |
| K5 | MGC, MHG (from 2022-04) | $9.74 | $0.00 | $0.00 |
| K6 | ZW, ZS, ZM, ZL, HE, LE | $21.86 | $0.33 | $2.52 |
| K7 | (none chosen) | $0.00 | - | - |
| **Set** | 22 contracts, 1,502 chunks, complete | **$128.34** | **$106.82** | **$119.65** |

acct-2 cap needed: $231.82 ($244.65 with 10%). Superseded for purchases by (b2); kept for the record.

### Set (b2): each cluster's purchase = traded vehicles (chosen or undersized) + member legs: $162.78

| Cluster | Roots bought | Quoted | Top-up at quote | Top-up at quote + 10% |
|---|---|---:|---:|---:|
| K1 | MNQ, M2K, MYM | $22.11 | $0.59 | $2.80 |
| K2 | ZT, ZF, ZN, TN, ZB, UB | $40.50 | $18.98 | $23.03 |
| K3 | 6E, 6A, 6B, 6C, 6J, 6S, 6N | $49.34 | $27.81 | $32.75 |
| K4 | MCL, NG | $11.46 | $0.00 | $0.00 |
| K5 | MGC, MHG | $9.74 | $0.00 | $0.00 |
| K6 | ZC, ZW, ZS, ZM, ZL, HE, LE | $26.52 | $5.00 | $7.65 |
| K7 | MBT | $3.11 | $0.00 | $0.00 |
| K8 | MGC, 6C, MNQ, MCL, MBT (legs only) | $29.65 | $8.13 | $11.09 |
| **Set** | 28 distinct contracts, 1,905 chunks, complete | **$162.78** | **$141.26** | **$157.53** |

acct-2 cap needed for the whole set: $266.26 ($282.53 with 10%). Versus (b): + ZT $6.01, ZF $6.98, 6C $7.05,
6N $6.62, ZC $4.67 (undersized vehicles, R10) and MBT $3.11 (K7's undersized vehicle, also K8's bitcoin
leg); K8's other legs (MGC, 6C, MNQ, MCL) are already other clusters' vehicles. MES is excluded (owned).
Arithmetic only, no recommendation: (a) and (b2) together (set (a) plus MNQ, M2K, MYM, MCL, MGC, MHG, the
6 (b2) roots not in (a), $36.45) are $225.76: top-up $204.24 ($226.81 at +10%), cap $329.24 ($351.81).

## 8. Ledger diff

`git diff --stat ledger/`: `ledger/databento_spend.jsonl | 5668 +++` (1 file changed, 5668 insertions, 0
deletions). All 5,668 added lines are `event "quote"`, session `stage-E.2b-2026-09-26`, account `acct-2`,
`usd 0.0` (sum $0.00): 2,201 (a) + 1,562 (b) + 1,905 (b2); 83 are the first-pass failed quotes
(`quoted_usd null`, the 422 note). First 20:08:19Z (13:08 PDT), last 00:37:55Z (17:37 PDT). No commit,
settle or refused line; no cap changed; nothing bought; docs/ACCESS.md untouched.

## 9. Deviations (each with its reason)

1. Plaintext on a seal failure: MES's D.1f pull keeps the plaintext when a seal fails ("fail-closed"); the step
   2 path purges it, because the brief requires that no plaintext holdout byte persists after a failure
   mid-chunk. Cost of the choice: if a seal fails after its blob is written but before its manifest record,
   the only copy of that paid chunk is an orphan blob; the next run refuses (FileExistsError, "remove the
   orphan by hand") and the lead decides.
2. The trade-date guard is applied to the step 1 BUY run only, not to `plan_requests()` or `--quote-only`:
   tests/test_pull_universe.py (unchanged, must pass) builds and quotes the full E.1 plan including MBT's
   last chunk. A quote delivers no bar; the buy refuses before any call.
3. data/holdout.py is not edited (the brief allows it only for the guard fix): per-product sealing is
   data/step2_seal.py built from data.holdout's primitives, including its private helpers (_write_manifest,
   _append_log, _pin_log_and_remove, _unlock_log_intact, _record_paths, _sealed_chunks, _fsync_dir). A
   refactor of data.holdout would change those names; the step 2 tests would catch it.
4. data/build_bars.py is not edited: step2_store reuses its functions (several private) and replaces only
   the orchestration, because `_flag_kept` hard-codes the research date classes.
5. `.gitignore`: one line `data/processed_step2/` (lead ruling).

## 10. Open questions for the lead (after the follow-up)

- Q1: resolved by OC-R (section 3.1). Left open: MNG is refused for step 2 by name (pricing gap
  2020-01..2023-09); it is in no set.
- Q2: resolved (section 3.1); the new key sits inside `holdout_2` for the reason given there.
- Q3: stays (the frozen "same unlock log"; on the user's list).
- Q4 (sealing is Linux-only) and Q6 (3 E.1 requests committed twice, $0.316080 counted pessimistically):
  accepted by the lead.
- Q5. The harness manifest must list the new data/ modules or the preflight refuses them:
  data/trade_date_guard.py, data/step2_seal.py, data/pull_step2.py, data/pull_step2_report.py,
  data/step2_store.py, and re-hash the modified data/pull_universe.py, data/config.py, data/holdout.py.
- Q7 (new). K8's crude leg is MCL's own bars because no CL price-path declaration exists (the catalog's
  own rule). If E.2 declares CL as MCL's price path, the K8 purchase needs CL (priced in set (a), $7.57).
- Q8 (new). K3-mehedge-01 reads the EURO STOXX 50 and Nikkei 225 free daily indices; they are not GLBX
  products, so step 2 does not buy them; K3's session must obtain them (the catalog makes the member
  conditional on E.2 obtaining them).

## 11. Files and commands

Created: data/trade_date_guard.py (171 lines), data/step2_seal.py (211), data/pull_step2.py (726),
data/pull_step2_report.py (~100), data/step2_store.py (~445), tests/test_e2b_trade_date_guard.py,
tests/test_e2b_pull_step2.py, tests/test_e2b_step2_store.py, reports/stage_e2b_step2_quotes.json,
reports/stage_e2b_step2_quotes.md, this report.
Modified: data/holdout.py (additive, lead ruling on Q2: `_product_holdout2_reports`, and
`status_report` adds `holdout_2["products"]` and folds it into the top-level all_ok; +22 lines),
data/pull_universe.py (+45 lines: TradeDateGuardError, check_trade_dates, validate_trade_dates,
the buy-run and acquire calls, `_in_step1_window` in resume_scan, docstring), data/config.py (the E.2b block
and STEP2_ROOT, +14 lines), .gitignore (+1 line data/processed_step2/), ledger/databento_spend.jsonl (+5,668
$0.00 quote lines, section 8).
Not touched: data/pull_mes.py, data/build_bars.py, screening/runner.py, any frozen or hashed
file, live/, ops/, REGISTRATION.md (0 bytes), data/sealed/, docs/HOLDOUT*.json, the unlock log. Nothing was
created under docs/holdout2/, data/processed_step2/ or reports/step2/ (no purchase, no build).

Commands (all `uv run --no-sync`; times PDT):
- `python -m data.holdout status` at start (12:43) and end (14:35): unlocks_logged 0 for both holdouts,
  all_ok true.
- `pytest -q tests/test_pull_universe.py` after the guard fix: 57 passed.
- heavy.sh `pytest` of the 8 existing files + the 3 new ones: 357 passed (13:05), 358 passed (14:34, final).
- `pytest --cov` of the 3 new files: 59 passed, new modules 93% (13:06).
- `ruff check` of every new and modified file: clean (data/config.py keeps one pre-existing E501 on the E.1
  lead's comment line 98, not mine).
- heavy.sh `python -m data.pull_step2 --quote-only --set ml-route` (13:08-13:58) and `--set clusters`
  (13:59-14:31); after OC-R `--set ml-route --retry-failed` and `--set clusters --retry-failed` (16:51, 0
  quote calls) and heavy.sh `--set clusters-legs` (16:51-17:37, 1,905 quotes, 0 failed).
- After the follow-up edits: heavy.sh pytest of test_holdout.py, test_d1f_holdout2.py,
  test_d1f_preflight.py and the store and guard files: 187 passed (16:53). Final heavy.sh run of the 8
  existing files and the 3 new ones (71 new tests): 369 passed (17:41). ruff clean on every file touched.
- `python -m data.holdout status` at 17:41: holdout 1 all_ok true, unlocks_logged 0; holdout 2 all_ok
  true, unlocks_logged 0; products {}. REGISTRATION.md 0 bytes.
Read-only lookups: reports/stage_e2a_vehicles.json (exposures), the calendars, the ledger (acct-2 sums).
Probe of the guard on all 45 step 1 last chunks (scratchpad): MBT refused holdout-1, the other 44 refused
for coverage; step 2 chunks of 9 roots: no unsealed chunk books a holdout-2 date.
