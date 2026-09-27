# Brief: PurchaseCoder2-OpusXHigh (Stage E.2b Task 4; worker-xhigh on opus)

Objective: fix the purchase guard to refuse by CME trade date, build the step 2 purchase path with holdout-2 sealing per
product and the step 2 bar store builder, and run the free step 2 quotes. NO PURCHASE.

## Read first (by section)
- reports/stage_e2b_briefs/00_common.md (binding).
- docs/STAGE_E_DESIGN.md (FROZEN): D4 (windows, holdout-2 sealing per product), D11.4, D13 (spend plan, step 2 per
  cluster). docs/STAGE_E_ML_DESIGN.md M1 and M2 (the step 2 range and the 31 price-path contracts), read-only.
- reports/E.2a_RETURN.md section 2, the paragraph "Holdout-1 rows inside step 1 files" (the L-9 finding: the guard was set
  by timestamp, so MBT bars booked to trade date 2026-06-22 arrived in step 1 files), and section 7.
- Code: data/pull_universe.py (the step 1 path: plan_requests, check_window, check_holdout, the gate, the ledger,
  resume_scan, run_quote_only, run_buy), data/pull_mes.py (its holdout-2 sealing in the download call), data/holdout.py
  (sealing, status, the unlock log; never call unlock), data/spend_gate.py (per-account caps), data/config.py,
  data/quote_universe.py, data/build_bars.py (the research-window bar builder whose schema the step 2 store reuses),
  data/calendars/ and data/group_session.py (trade dates per group), reports/stage_e2a_vehicles.json (read-only).

## Build
1. The guard fix (L-9): every purchase path refuses by CME trade date, not only by timestamp, so a request can never
   deliver bars booked to a holdout trade date: using the product's group calendar, a request whose [start, end) contains
   any minute booked to a holdout-1 trade date (>= 2026-06-22) is refused; an unsealed request containing any minute booked
   to a holdout-2 trade date (2024-04-01..2025-03-31) is refused (holdout-2 chunks are only fetched through the sealing
   download). A test plants MBT's case (a request ending 2026-06-21 00:00 UTC, which the calendar books partly to trade
   date 2026-06-22 because of Juneteenth and the weekend) and proves the refusal; the lead's Task 9 DECISIONS entry cites it.
2. The step 2 path (new module, e.g. data/pull_step2.py): ohlcv-1m monthly chunks 2019-05..2025-03 for a given contract
   list, oldest first; each holdout-2 chunk (range=2024-03-01_2024-04-01 through range=2025-03-01_2025-04-01) sealed in
   the download call after its byte check, exactly as data/pull_mes.py seals MES's; one sealed store per product; the same
   unlock log; a per-cluster mode for confirmation purchases (the cluster's chosen vehicles from
   reports/stage_e2a_vehicles.json); the ML route mode (its 31 price-path contracts); gate and ledger on acct-2 with that
   account's cap; resume. `--quote-only` issues no billable request. The buy path must refuse to start in this session
   (the E.2b caps are $0.00) and must call screening.harness_freeze.preflight() first.
3. The E.2b spend policy in data/config.py: STAGE_E2B_SESSION_ID = "stage-E.2b-2026-09-26", session and request caps $0.00
   (the E.0 pattern). No other cap changes.
4. The step 2 bar store builder (lead ruling OC-C: you own it because you define the chunk layout): builds per-product
   bars for trade dates 2019-05-06..2024-02-29 from the unsealed step 2 chunks, reusing data/build_bars.py's per-product
   logic (calendars, rolls, flags, the parquet schema and metadata); refuses any row whose trade date is on or after
   2024-03-01 (note: the February 2024 chunk holds bars booked to trade date 2024-03-01, the embargo; they must be dropped
   unread by trade date, never written) and never opens a sealed chunk. This store is both the ML route's training-window
   store and the cluster confirmation-window store. Nothing to read yet (the history is not bought): test on synthetic
   chunk files. Document the store layout (paths, file names, schema, metadata) at the top of your report within your
   first 45 minutes; the lead relays it to RunnerCoder and MLPipelineCoder.
Tests prove: the sealing order (seal in the download call after the byte check, before the next chunk; no plaintext
holdout byte persists after a failure mid-chunk), the refusal of holdout-1 dates, the trade-date guard (MBT case), the
per-account caps on acct-2, resume, quote-only issuing no billable request, the store builder's refusals.
Every existing test of the files you touch passes unchanged (tests/test_pull_universe*.py, test_holdout*.py, the
pull_mes tests, test_spend_gate*.py; find them with grep).

## The free quote run (network allowed: Databento metadata/cost calls only; the key via data.config)
Under the E.2b session id with $0.00 caps, quote two request sets: (a) the ML route's 31 price-path contracts over
2019-05..2025-03; (b) each cluster's chosen vehicles over the same range. Ledger lines are $0.00 quote lines only. Write
reports/stage_e2b_step2_quotes.json and .md: totals per set and per cluster, per contract, and the acct-2 top-up the user
needs for each (acct-2 holds $21.52 by the gate's count: verify that figure from the ledger with the gate's own
arithmetic and state the cap headroom under ACCOUNT_2_CAP_USD). A quote failure is logged and the set reported
incomplete; no cap changes. Run it at most once per set (plus retries of failed pieces).

## Ownership
You own data/pull_step2.py (or your name), the guard fix in data/pull_universe.py (and any other purchase path that needs
it), data/config.py's E.2b block, the step 2 store builder (a new data/ module), your tests, and the quote reports. Do not
edit data/pull_mes.py or data/holdout.py unless the guard fix requires it (report it if so). Others own screening/ (runner
workers), ml_route/ and pyproject/uv.lock (MLPipelineCoder), compute/ (lead, Windows worker).

## Report
reports/stage_e2b_task4_purchase_worker.md: the store layout first, then the guard fix, tests and what each proves, the
quote tables (per set, per cluster, top-up), the ledger diff (`git diff --stat ledger/` and the added lines' amounts).
