
## Part 2: Gate 0 verification (Gate0Verifier-FableXHigh, 2026-10-03 12:20-12:45 PDT)

Verdict line: **VERIFIED WITH NOTES.** Every Gate 0 number recomputed independently agrees with
reports/stage_e12_gate0.json to at most 6.5e-13 relative (tolerance 1e-6 family A, 1e-4 family B);
every count and every Holm decision is exact; the verdict FAIL with no passing pair is reproduced.
No finding is above NOTE.

Method (brief steps 1-7, written to disk before the lead's JSON was opened): own code in
reports/stage_e12_briefs/gate0verifier/ (recompute.py, compare.py, spot_check.py, checks.py,
mes_mbt_check.py; raw outputs my_*.csv/json/npy, compare*.csv/json, checks.json,
mes_mbt_check.json, recompute.log). Inputs: the saved build pickles
~/.cache/propexp_e12_phase1/stages/phase1_panel.pkl (68,138 rows, 27 roots, 150 feature columns,
64 signals, 1,068 trade dates 2019-11-19..2024-02-29; MBT has no row) and the build calendar in
it (1,248 CME dates 2019-05-06..2024-02-29); the registered list; the training-window step 2
parquet files for the spot check. ml_route_v2.gate0 / cpcv / cost_filter / models were read for
definitions and not imported; the panel module was imported only to unpickle the Panel dataclass.
The ridge is my own closed-form solve (centred X and y, alpha = 0.1 x n_train, Cholesky on the
Gram matrix; the lead's uses LU). Blocks, splits, embargo and purge were built from V2.9's text
(6 blocks of floor(1248/6) = 208 dates: 2019-05-06..2020-02-21, 2020-02-24..2020-12-10,
2020-12-11..2021-09-30, 2021-10-01..2022-07-21, 2022-07-22..2023-05-11, 2023-05-12..2024-02-29;
15 splits; one-date embargo each side; the purge removed 0 extra rows, as all holds are intraday).
Every row was out of fold exactly 5 times. nice 10, 6 BLAS threads, 9.5 GB free before loading.

### Comparison table (mine vs the lead's JSON)

| Quantity | Mine | Lead | Agreement |
|---|---|---|---|
| Admissible pairs (tau 0.167) | 81 of 81; max c/sigma 0.1403 | 81 (JSON admissible_pairs; filter.pkl table) | exact; c, sigma, ratio max rel 6.8e-15; n_rows exact |
| Family B pairs recomputed | 81 (3 horizons, CPCV OOF) | 81 | mean g, c, t_B, p: max rel 2.9e-14; n_trades, n_dates, n_obs exact on all 81 |
| Best pair (largest t_B, n >= 30) | gate0B_NG_h60 | gate0B_NG_h60 | same pair |
| NG h60 mean gross per trade (ticks) | 5.5694980694980805 | 5.5694980694980805 | 0 |
| NG h60 c (mean round trip of sides taken) | 1.7128756307018145 | 1.7128756307018143 | 1.3e-16 |
| NG h60 cost multiple vs 1.5c | 3.2515c (bar 1 met) | gross_cost_multiple 3.2515 | 0 |
| NG h60 t_B (date-clustered, 330 dates) | 2.5143449337178385 | 2.5143449337178385 | 0; bar 2 (t >= 3) not met |
| NG h60 one-sided p | 0.0062010357819135 | 0.00620103578191354 | 6.4e-15 |
| NG h60 trades / pair rows | 518 / 2,590 | 518 / 2,590 | exact |
| NG h60 Holm (my p, lead's other 272 p) | rank 1 of 273, threshold 1.8315e-4, not rejected | rank 1, 1.8315e-4, not rejected | exact; bar 3 not met |
| Pairs with t_B >= 3 | 0 | 0 | exact |
| Second pair NG hF | mean 13.921, c 1.766 (7.88c), t 2.330, p 0.0103, 494 trades | same | within 1e-14 |
| Pooled B | mean g -0.71718, cost 2.26000, t 0.28075, 39,997 trades, 1,067 dates | same | rel 0; counts exact |
| Family A, seeded three (seed 0x53e7ef57 = 1407709015 over the 192 A ids in list order) | k5_ovr_pct_h60: m 3.1269e-4, t 0.5985, p 0.5496, 1068 dates, IC -0.00303; k2_auction_mto_h120: m -9.9009e-4, t -1.8619, p 0.06289, IC -0.00984; g01_ret30_h120: m 1.9992e-3, t 0.2661, p 0.7902, IC 0.00623 | same | max rel 3.2e-13 |
| Family A, all 192 (bonus) | computed | 192 | mean, t, p, IC, gross_ticks_sign max rel 6.5e-13; n_dates, n_obs exact |
| Smallest A p | 0.0154, gate0A_g07_range_hF | same | exact |
| Holm family | 273 tests, 0 rejections; the lead's table is internally consistent (ranks follow p, thresholds 0.05/(m - rank + 1)) | 273, 0 | exact |
| Verdict / passing | FAIL / none | FAIL / none | exact |
| N | \|A\| 192 + \|B\| 81 = 273; 198 + 273 = 471 | n_a 192, n_b 81, n_contributed 273, n_holm_family 273 | exact |
| Targets spot check (20 rows, same seed, h60 and h120 both ok, entry and both exits outside [r - 5, r + 30) min of every release) | (open(b_{t+h}) - open(b_t)) x ticks per vendor unit from the step 2 parquet | y_gross_h60, y_gross_h120, entry_price | 20/20 exact for h60, h120 and the entry open (19 roots; per-unit factors e.g. NG 1000, ZN 64, 6J 2e6, M2K 10) |

### Reconciliation (freeze review F-10) and the lead's three added checks

- Store hashes: for all 28 phase-1 roots, reports/stage_e12_phase1_bars.json roots.<R>.store_sha256
  = reports/step2/bars_<R>.json parquet.sha256 = sha256 of the parquet on disk; each bars_<R>.json
  purchase_manifest.sha256 = sha256 of reports/step2/purchase_<R>.json, and its input_files equal
  the purchase record's 58 chunk files and hashes (28/28). Vehicles: the ranking subset (28) =
  phase1_bars vehicles = the list's vehicles = the JSON's vehicles; dropped none; the list's
  ranking_sha256 matches reports/stage_e12_ranking.json. List sha256
  53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea matches STATE line 21 and the
  JSON's list_sha256. Ledger: 273 entries, ids and specs equal the list in order, all stamped
  2026-10-03T12:15:25-07:00, before created_pdt 12:15:54; sha256 aacca512... now = before = after.
  Fingerprints: the JSON's constants (013fa5a4...) and inputs (969d3b7e...) equal the panel
  pickle's; freeze a647cd06... equals STATE; gate0.json sha256 c0af61c2..., .md 363c5676... as in
  STATE line 22.
- Harness v9 (commit 4b1e81e): the diff adds the closure-ruling path to data/step2_store.py
  (load_closure_rulings, _closure_ruling, parameters of build_step2_product / _build_window /
  run_product, the closure_ruling metadata) and one FROZEN_INPUTS line in
  screening/harness_freeze.py. reports/stage_e12_closure_rulings.json (sha256 af7967b5...) holds 24
  entries, all keep_and_flag, for exactly the 12 roots held under v8 (store_builds.log: NQ 6A 6B 6E
  6N YM RTY LE 6C HE 6S 6J; store_builds_v9.log: the same 12 built), and the union of those 12
  summaries' deep closure bars (close_minute false) equals the 24 entries exactly (NQ 6, RTY 5,
  YM 4, one each for the other nine). Each of the 12 summaries records closure_ruling with the
  file's sha256 (equal to the file on disk) and bars_ruled = its deep-bar count. The 15 stores
  built under v8 (harness 452c4a51...) and the pre-existing NG store (harness 9a8ebe73...) carry
  no deep closure bar. Read path: ml_route_v2/phase1/world.py imports only STEP2_REPORTS and
  step2_parquet_path from data.step2_store, neither touched by v9; the v2 freeze manifest (91
  files) does not include data/step2_store.py or screening/harness_freeze.py, and its sha256 is
  unchanged; the build (12:13:59) and Gate 0 (12:15:54) both ran after v9 (12:05:01). See N-4.
- MES (P-1a): booking the confirmation store's 1,695,822 rows by ts_event with the equity group
  calendar (close-minute prints to the session they close) gives exactly 3 rows whose label
  differs from the booking: 2020-03-30 21:59 UTC (label 2020-03-30, booked 2020-03-31), 2020-03-31
  21:59 UTC and 2020-06-30 21:59 UTC (each booked to the next date). The refusal is genuine and the
  recorded "3 rows, first label 2020-03-30 booked 2020-03-31" is exact. The MES-reading signals in
  ml_route_v2/signals are g17_mes (generic.py G17) and k8_flight_ret, k8_flight_tail (k8.py); the
  list's uncovered_signals are exactly those three; 64 covered signals x 3 = 192 A tests.
- MBT: V_ref 48.0 as recorded; thresholds 7.2 / 12.0 / 19.2. On the recorded monthly medians, the
  first month from which every month through 2024-02 stays at or above the threshold is 2023-11
  (0.15), 2024-01 (0.25; 2023-12 = 9 < 12, 2024-01 = 14, 2024-02 = 16) and none (0.40; 2024-02 = 16
  < 19.2), equal to the record's m_star; S_X = the first calendar date of 2024-01 = 2024-01-02.
  The MBT step 2 store holds 41 trade dates from 2024-01-02 (the recorded 41; the union calendar
  has 43, the two early-close holidays). 41 < Z_MIN_DATES 60, so no panel row: consistent.

### Order of events (lead addition, all PDT)

1. 09:25:53 freeze commit 9466f2e "ML route v2 freeze"
2. 10:02:53 v8 commit deccd17
3. 10:03:54 first E.12 "commit" event in ledger/databento_spend.jsonl (17:03:54.03 UTC, acct-1,
   NQ.v.0 2019-05); the session's first row is a quote at 09:26:34
4. 12:05:01 v9 commit 4b1e81e
5. 12:15:25 last (and first) Gate 0 registration in ledger/ml_v2_config_ledger.jsonl (273 entries)
6. 12:15:54 created_pdt in reports/stage_e12_gate0.json (panel built 12:13:59)

Strictly increasing.

### Findings

BLOCKING: none. SHOULD FIX: none.

- N-1 (NOTE, documentation): c(p,h) in cost_filter.py is the mean of max(cost_long, cost_short),
  while V2.2 says "the mean D8 round trip". Under the symmetric reading (mean of the two sides)
  no admissibility changes (0 of 81; max ratio 0.1403 against 0.167), so the Gate 0 list and
  verdict are unaffected. Record the max reading in V2.2 at the next design edit; no rerun.
- N-2 (NOTE, informational): the blocks are cut on the 1,248-date build calendar from
  2019-05-06, while the first panel row is 2019-11-19 (warm-up), so block 1 holds rows on only
  about 68 of its 208 dates. This is V2.9 as written ("from calendars alone").
- N-3 (NOTE, disclosure): STATE lines 21-22, which carry the lead's headline Gate 0 numbers,
  entered my context when I grepped STATE for the list sha256 (the brief's step 6 asks for it).
  My code was written from the design text and the module definitions before it ran, and all
  273 tests were recomputed, not only the headline figures.
- N-4 (NOTE, wording): "no module on the Gate 0 read path changed between v8 and v9" holds for
  the v2 freeze manifest's files and for the two names world.py imports from data.step2_store,
  but data/step2_store.py itself is imported on the read path and did change (build-side
  functions only). State it that way. The harness sha256 therefore differs between the v8
  stores (452c4a51...) and the v9 stores and Gate 0 (7fd757f6...), by design.
- N-5 (NOTE, unverified by rule): V_ref = 48.0 for MBT derives from research-window medians,
  which this review may not read; taken as recorded (research store sha256 78ef1710...).

### Not checked

- The MES refusal path inside the frozen loader itself (I replicated the booking with
  data.group_session; I did not step through world.py's refusal code).
- V_ref inputs (research window, sealed to this review) and the day-session medians' source
  computation; only the arithmetic on the recorded medians.
- The lead's ridge numerics beyond agreement: my solve is a different algorithm (Cholesky vs LU)
  and agrees to 3e-14, which is the check.
