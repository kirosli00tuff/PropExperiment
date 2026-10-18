# Stage E.24 STATE (forward plumbing: loader fix, IBKR and Alpaca paper adapters, E22-F2)

Prompt: docs/prompts/STAGE_E.24.md. Lead: Opus 5.5 xhigh, ultracode on. Session c2dca792-060d-4694-91ef-4a6f3f808f1d.
Times PDT (America/Vancouver), from `date`, file mtimes or transcripts (never estimated; an 01:47/01:52 estimate was corrected at 01:41 from mtimes). Work ends 15:00, return by 15:30 (planner window changes 06:18 and 11:16; was 07:00/07:30, then 09:00/09:30). At most 6 workers at once (planner pacing, 11:16).
No outcome read, no market data read, no broker connection (V41, V42). On resume: read this file first, skip done tasks.

## Task status

| Task | Owner | Status | Start | End | Artifacts |
|---|---|---|---|---|---|
| 0 Startup checks | lead | done | 01:27 | 01:29 | reports/stage_e24_briefs/start_checks.txt, checks.sh |
| 0 Start suite (detached, nice 10, watchdog 2 GB) | lead | done: 1 failed (known h6), 7728 passed; min avail 2069 MB | 01:29:13 | 01:59:56 | reports/stage_e24_briefs/pytest_start.out |
| 0 Broker deps pinned outside pyproject/uv.lock | lead | done | 01:31 | 01:34 | forward/requirements_broker.txt (sha256 1639eb77...) |
| A1 Loader fix | LoaderCoder-OpusXHigh | done (new package mdio/; replay 79,207 values, 0 mismatches) | 01:35:08 | 06:16:45 | reports/stage_e24_briefs/loader/loader_report.md |
| A2 Loader review | LoaderReviewer-FableXHigh 06:32 APPROVE WITH FIXES; LoaderFixer 11:17-11:25; LoaderRecheck-FableXHigh 11:25-11:35 APPROVE (0 B, 0 SF, 3 N) | done | 06:16:45 | 11:35 | reports/stage_e24_briefs/loader/loader_review.md |
| B1 IBKR facts | IBKRReader-OpusHigh (workflow wf_a244ece8-d25) | done (file complete 01:59:09; agent cut by the limit after writing) | 01:35 | 01:59 | reports/stage_e24_briefs/facts/ibkr_facts.md |
| C1 Alpaca facts | AlpacaReader-OpusHigh (workflow wf_a244ece8-d25) | done | 01:35 | 01:47 | reports/stage_e24_briefs/facts/alpaca_facts.md |
| B1/C1 fact checks | IBKRFactChecker-FableXHigh: done (8 OK, I4 OVERSTATED); AlpacaFactChecker-FableXHigh: done (9 OK, A7 OVERSTATED) | | 06:13 | 06:27:05 | reports/stage_e24_briefs/facts/ibkr_factcheck.md, alpaca_factcheck.md |
| B2-B4 IBKR code | IBKRCoder-OpusXHigh | done (373 forward tests pass; C1 applied) | 01:40:23 | 06:29:49 | reports/stage_e24_briefs/ibkr/ibkr_report.md |
| C2 E22-F2 design | lead | draft 1 done (slots wait on facts) | 01:41 | 01:43 | reports/stage_e24_prereg_F2.md; draft 1 copy reports/stage_e24_briefs/f2/prereg_F2_draft1.md (ed24f811...) |
| C3a Alpaca adapter | AlpacaCoder-OpusXHigh | done 06:31:04 (raw+corporate actions, fact-check corrections; 116 own tests); first report 06:16:03 (106 tests pass); resumed for corporate-actions returns, stop 06:45 | 01:40:23 |
| C3b F2 book | F2BookCoder-OpusXHigh | done 06:33:52 (rulings Q1-Q20 applied; Q21-Q23 new); F2Fixer (wave 2) for Q21-Q23 | 01:44:33 |
| C fees/holidays lookup | FeeReader-OpusMed | done (F6 not fetched: ICE terms bar robots) | 01:40:23 | 01:45 | reports/stage_e24_briefs/facts/fees_facts.md, fees_log.md |
| B5 Adapter review | AdapterReviewer-FableXHigh: first spawn cut by the limit, no file; respawned in wave 2 11:17:48 | running | 06:29:49 | | reports/stage_e24_briefs/ibkr/adapter_review.md |
| C4a Alpaca adapter review | AlpacaReviewer-FableXHigh: first spawn cut, no file; respawned in wave 2 11:17:48 | running | 06:22:04 | | reports/stage_e24_briefs/alpaca/adapter_review.md |
| C4b Reg review, freeze, commit, register | RegReviewer-FableXHigh, lead | pending C3b | | | |
| D1 Warm-up declarations | lead | done | 01:50 | 06:14 | reports/stage_e24_warmup_declaration.md |
| D2 User checklist | lead | done | 06:13 | 06:14 | reports/stage_e24_user_checklist.md |
| End checks, end suite | lead | pending | | | |
| Return, progress, STAGES, cost, commit | lead | pending | | | reports/E.24_RETURN.md |

## Start checks (01:28:39, verbatim in start_checks.txt)

Holdout all_ok, 0 unlocks; REGISTRATION.md 0 bytes; harness v13 dd2bcc60... preflight OK; spend ledger 36402 lines
034a454b...; N = 538 (9 lines, 25c04088...); E.21 freeze verified (18 inputs); E.23 freeze verified (20 inputs, 5 ids);
E22-F1 file set 30/30 OK (list bb3bf3b3...); E22-F1 prereg 04ef33a6... tracked, no diff. Known v13-era mismatches as in
E.23 (E.14 inputs list, E.16 manifest, E.18, E.20 H6, E.20 search). Tracked tree clean; 1272 untracked lines.
.env: no IBKR_/IB_/ALPACA_/APCA_ names.

## Lead decisions (open choices, carried to the return section 6)

- OC-1 (01:34) Broker libraries pinned in forward/requirements_broker.txt (hashes; uv overlay
  `uv run --frozen --with-requirements`), not added to pyproject.toml/uv.lock: harness v13 pins both files; a v14 would
  make trigger_hold/events.py's v13 preflight refuse (an earlier stage's code path). Adapters import the vendor
  libraries lazily; tests use mocks. Versions: ib_async 2.1.0, alpaca-py 0.44.0 (released before 2026-10-01; shared
  packages equal the lock: numpy 2.5.3, pandas 3.0.5).
- OC-2 (01:29) Start suite run despite 7.5 GB available (< 8 GB note) with a watchdog at 2 GB; if killed, quote the E.23
  end suite (code identical: git diff ef2902d..HEAD touches docs only).

## Event log

- 01:27 session start; 01:28:39 start checks; 01:29:13 start suite launched.
- 01:35:08 LoaderCoder spawned; facts workflow wf_a244ece8-d25 launched (2 readers, 2 Fable fact checkers).
- 01:40:23 IBKRCoder, AlpacaCoder (phase 1 on mocks, phase 2 after facts), FeeReader spawned. F2 IDM from the frozen F1 matrix without MZL: 2.3293791420997985.
- 01:44:33 F2BookCoder spawned on prereg draft 1 (facts slots pending). Draft 1 decisions: excess-of-BIL P&L, cap before buffer, shorts toward zero (OC-3..OC-7 in the return).

## Lead decisions added (C2 draft 1, 01:43)

- OC-3 E22-F2 P&L is in excess of cash (BIL total return): long notional earns r_i - r_BIL, shorts earn -r_i (no
  credit on proceeds) and pay borrow b, the debit above $25,000 pays spread s over cash. Reason: an ETF book's total
  return includes the risk-free rate and carry, so a zero-skill long-biased book could pass the bar; the futures book
  of E22-F1 is an excess return; a flat book must earn 0.
- OC-4 IDM 2.3294: E22-F1's frozen subsystem correlation restricted to the 11 modelled exposures (no ETF data read).
  FDM: E22-F1's frozen 1.1314.
- OC-5 Soybean oil not modelled (no single-exposure US ETF); BIL as cash benchmark, never traded.
- OC-6 Cap on unrounded targets before the buffer, second check scaling longs only; shorts rounded toward zero.
- OC-7 Warm-up window 2024-03-01 to the session before the start (parity with E22-F1, V42).
- OC-8 Total-return accounting via one-response ratios of all-adjusted closes; shares updated through
  q x rawclose(t-1) x (1+r) / rawclose(t) (splits exact, distributions reinvested at the close).
- 01:45 FeeReader done. 01:46:43: prereg section 5 cost constants fixed (SEC 0.0000206 x value on sells, TAF 0 as printed by Alpaca, CAT 0.000003/share, daily ceil to cent; b 1.0%; s 2.50% = 6.50% Alpaca margin - 4.00% FOMC upper bound since 2026-09-17, lead fetch of federalreserve.gov at 08:45:53Z); F2BookCoder told.

- OC-9 FeeReader fetched two finra.org content pages in the same command as FINRA's terms, whose terms bar scraping tools: those pages are not cited; the TAF follows Alpaca's printed schedule ($0 per share).
- OC-10 The NYSE holiday calendar was not fetched (ICE terms bar robots); E22-F2 references it as E22-F1 references the exchange's calendar, checked by the operator in a browser.
- OC-11 s = 2.50% (Alpaca 6.50% margin minus FOMC upper bound 4.00%), b = 1.0% (Alpaca ETB fee 0; declared HTB allowance), h_i 1 or 3 cents declared without quotes.
- ~02:00-06:10 PAUSE: session usage limit (resets 06:10). IBKRCoder, AlpacaCoder, F2BookCoder, LoaderCoder, IBKRReader (facts file complete at 01:59:09), AlpacaFactChecker cut off; IBKRFactChecker never ran. Work on disk kept.
- 06:11 resumed. 06:13 the four coders resumed by message (hard stop 06:35); IBKRFactChecker and AlpacaFactChecker spawned (stop 06:40, no new fetches). Prereg slots filled from alpaca_facts (feed sip with iex fallback rule, increment 0.001, cap 50000).
- KEY FINDING (ibkr_facts I6): IBKR TRADES daily close = last traded price; legacy docs: 'can be the settlement price if provided by the exchange'. Not reliably the settlement -> no new registration for E22-F1; decision to the user. I4/I8: API historical bars need L1 subscriptions (USD 1.55/month x 4 exchanges, funded IBKR Pro >= USD 500).
- 06:14 D1 slots filled (IBKR TRADES close, not declared settlement; Alpaca feed sip/iex rule); D2 checklist written.
- 06:16:03 AlpacaCoder first report (reports/stage_e24_briefs/alpaca/alpaca_report.md). Lead ruling: E22-F2 returns from raw closes + /v1/corporate-actions (r = k x (raw(t)+D)/raw(prev) - 1), late corporate actions booked in the next record (fifth P&L term), 'all' adjustment not used (A3: method undocumented, reported errors). Both coders told (stop 06:45).

- OC-12 E22-F2 total return from raw closes plus corporate actions instead of Alpaca's 'all' adjustment (undocumented method, reported errors); late-published actions booked in the next record; other types flagged, not booked.
- OC-13 Shadow route on Alpaca uses whole-share market-on-close orders by default (Alpaca: fractional orders are day-only, CLS orders whole-share only); shadow record only.
- 06:16:45 LoaderCoder done; LoaderReviewer spawned.

- OC-14 Loader fix as a new package mdio/ (base_rules/context.py, multiday/*.py, trigger_hold/*.py are frozen and their freezes refuse even new files there); the frozen runners stay unbounded if rerun; future multi-day runners must call mdio.bounded.
- 06:18 PLANNER MESSAGE (user channel): work may continue until 09:00 PDT, return by 09:30 PDT, replacing the prompt's 07:00/07:30; do not cut readers or coders short. 06:17:15 all six running workers told their stops are lifted (coders and reviewer 07:45, fact checkers 07:30, fact checkers may fetch again).

- OC-15 Planner-approved window change (06:18 PDT): work until 09:00, return by 09:30, replacing 07:00/07:30 after the 02:00-06:10 usage-limit pause; worker hard stops reset.
- 06:22:04 AlpacaCoder corporate-actions change done (114 own tests, 350 forward tests pass; waits for alpaca_factcheck to apply corrections); AlpacaReviewer spawned.
- 06:26:56 F2BookCoder first report (20 ambiguities). Lead rulings: change Q5, Q7, Q9, Q15, Q16, Q17, Q18; accept the rest; prereg text updated; coder applying (stop 07:30). IBKR fact check done: I4 overstated (delayed historical path may exist) -> checklist corrected, IBKRCoder told to probe reqMarketDataType(3).

- OC-16 Rulings on F2BookCoder's ambiguities (recorded in reports/stage_e24_briefs/f2/f2book_report.md): late split value booked as P&L and the signal series corrected; late BIL distribution corrects the cash term; missing-day accruals charged in the next record; a day without any ETF bar is missing whatever BIL does; step 5 rounds longs toward zero so gross <= B; both feeds in the config, the feed used stored per record; two float-noise guards accepted into the rule.
- 06:27:05 AlpacaFactChecker done: 9 OK, A7 overstated (PDT status at Alpaca unknown, interim period); A5 confirmed 'We do not support short sales in fractional orders' (supports whole-share shorts). No prereg change.
- 06:29:49 IBKRCoder done; AdapterReviewer spawned.

- OC-17 IBKR acceptance cutoff 18:00 America/Chicago on the trade date (coder's choice, not a fact; under review); IBKR price labelled close_last_trade.
- 06:31:04 AlpacaCoder done: capital gains carry long_term_rate + short_term_rate; corporate actions filter on process_date (about 15 days after ex_date) -> query +-60 days, filter on ex_date locally; most distributions will arrive by the late rule (prereg sentence added). 5 transient failures in F2BookCoder's in-progress test_forward_f2_late_ca.py.
- 06:32 LoaderReviewer: APPROVE WITH FIXES (independent replay 39,624 leaves, 0 mismatches; no v14 needed). 06:32:37 LoaderCoder resumed for SF-1 (null trade_date refusal) and SF-2 (bound mandatory in read_root_books).
- ~06:35-11:10 PAUSE 2: usage limit (reset 11:10); LoaderCoder (fixes not started), F2BookCoder (finished Q1-Q20 at 06:33:52), AdapterReviewer and AlpacaReviewer (no output) cut. Laptop rebooted at 10:49:30 (uptime -s).
- 11:15 resumed (planner message 11:16: work until 15:00, return by 15:30; at most 6 workers; finish started items first). Disk check: forward+mdio tests 397 passed, 2 skipped; F1 files OK; F2 rulings Q1-Q20 RULED in f2book_report.md.
- 11:20 prereg section 6 late-CA bullet revised (Q21 any late BIL action corrects the cash term by corrected-minus-recorded r_c; Q23 records store applied actions with amounts; Q22 accepted).
- 11:17:48 wave 2 workflow wf_a5926b6e-692: LoaderFixer -> LoaderRecheck; F2Fixer -> RegReviewer; AdapterReviewer; AlpacaReviewer (max 4 agents at once).

- OC-18 Planner-approved window change 2 (11:16 PDT): work until 15:00, return by 15:30, after a second usage limit (06:35-11:10) and a reboot (10:49); pacing: at most 6 workers at once, finish started items before new ones (the lead runs at most 4).
- OC-19 After the reboot, fresh workers with narrow briefs (pointing at the files on disk) instead of resuming the large earlier transcripts, to save the shared usage window.
- 11:49 wave 2 done: LoaderRecheck APPROVE (Part A done, no v14); RegReviewer BLOCK (2 B, 8 SF, 14 N); AdapterReviewer BLOCK (1 B, 5 SF, 8 N); AlpacaReviewer APPROVE WITH FIXES (0 B, 3 SF, 9 N); F2Fixer Q21-Q23 done (60 F2 tests).
- 11:50-11:56 lead rulings (reports/stage_e24_briefs/review_rulings.md); prereg sections 4-6, 8 revised for C4b B1, B2, S1-S7. 11:54:22 wave 3 workflow wf_82df3661-9de: F2Fixer2, AlpacaFixer, IBKRFixer, then RegRecheck (after F2Fixer2 and AlpacaFixer), AlpacaRecheck, AdapterRecheck (max 6 agents).

- OC-20 IBKR S3: `run` requires --date unless --holidays FILE; refuses a day with one exchange entirely missing unless --accept-exchange-gap. S4 (warm-up vs live close ages): user decision with the settlement choice; probe logs bar ages.
- OC-21 E22-F2 suspect-split guard (|ln move| > ln 1.5 without a split: no bar up to 10 sessions), delisting rule (10 sessions without a bar: closed at last close, dropped), SGOV replaces BIL after 10 sessions without a BIL bar.
- 15:59 user: finish within a credit limit. Wave 3: IBKRFixer, AlpacaFixer done; F2Fixer2 and the 3 rechecks cut (~12:15). 16:00 end checks (unchanged but date, E.25 commit, F2 draft untracked); forward+mdio 468 passed. E22-F2 NOT frozen/registered (OC-24); full end suite not run (OC-25). Return, progress, STAGES written; final commit.
