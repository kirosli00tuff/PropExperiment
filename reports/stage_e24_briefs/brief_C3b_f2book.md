# Brief C3b: F2BookCoder-OpusXHigh (worker-xhigh, opus). Stage E.24 Part C (the E22-F2 paper book)

Objective: implement the E22-F2 paper book exactly as reports/stage_e24_prereg_F2.md (DRAFT 1; sections 2-8 are your
spec; the code must match the text, and where the text is ambiguous, stop and list the question in your report rather
than choosing silently). New files only: forward/strategy_f2.py, forward/runner_f2.py, forward/evaluate_f2.py,
forward/config_f2.json, forward/tables_f2.json, forward/daily_f2.py (driver: source -> runner_f2 -> optional shadow
route), tests/test_forward_f2_*.py. No network, no market data: fixtures are written by hand (synthetic prices).

Inputs: reports/stage_e24_prereg_F2.md; forward/etf_bars.py (EtfBar, EtfDay, EtfBarSource, Missing,
SourceUnavailable, warm-up JSONL; written by AlpacaCoder, who owns it: if you need a change there, list it in your
report and message nothing; work around it); forward/core.py and forward/strategy.py (FROZEN; reuse
strategy.instrument_state with a mapping of DataFrames with columns adj_price and price, spec multiplier 1 and
yield_quoted false; core.unrounded_position, core.average_position, core.idm_for_live, core.round_half_away);
forward/ledger.py (FROZEN; reuse Ledger, canonical_json, the sha256 chain); forward/evaluate.py (FROZEN; reuse
newey_west, one_sided_p, annualised_sharpe, passes, add_months, max_drawdown); forward/runner.py (FROZEN; read it as the
model for the step order, missing-data rules, declared-closed checks, LedgerConflictError re-run semantics, config
fingerprint; mirror them; do not import its futures-specific parts); forward/config_f1.json (FROZEN; copy into
config_f2.json, with a "source" pointing back to config_f1.json, every value the rule needs: ewmac speeds and scalars,
forecast cap, average_abs_forecast, vol block, vol_target, fdm value, warmup_diffs, simple_rounding buffer_size, and the
idm correlation restricted to the 11 modelled exposures in the order QQQ IWM GLD USO UNG FXE SHY IEF TLT CORN SOYB =
MNQ M2K MGC MCL MNG M6E 2YY 10Y 30Y MZC MZS; a test must recompute the IDM 2.3293791420997985 from that block and also
check the block equals the corresponding sub-matrix of config_f1.json).

Requirements (section numbers are the prereg's):
1. strategy_f2.target_shares(history, prev_shares, config) -> {symbol: float}: section 4 steps 1-6 in order (cap on the
   unrounded targets, buffer around the capped targets, granularity: longs to the fractional increment in config,
   shorts toward zero to whole shares, second cap check scaling longs only). The signal frame per ETF: adj_price = the
   back-adjusted total-return close of section 6 (latest equals the raw close), price = raw close.
2. runner_f2: one call per NYSE session in order; per session: read bars (SourceUnavailable -> no record, re-raise);
   apply section 5's share update for splits/distributions, then fills of the pending orders at t's raw close (orders
   expire if the ETF has no bar), costs (half spread per share from tables_f2.json, SEC fee rate x sale proceeds, FINRA
   TAF per share sold capped per order; constants in config_f2.json with sources), the four P&L terms of section 5 with
   calendar-day accruals d/360, flags, the declared-closed and missing-day rules of section 6, then the new targets and
   orders. A missing day: P&L 0, flagged, counts as 0. Every record carries: date, prev_record_sha256/record_sha256
   (via forward.ledger), schema "E22-F2-ledger/1", config fingerprint and warm-up sha256, bars used (close, ret,
   prev_date per symbol and BIL), positions before and after fills, fills with price and costs, targets for the next
   session, the P&L terms separately and net_pnl, gross exposure and the cap scale factor, flags, declared_closed.
   Re-running a recorded date returns the stored record when identical and raises on a mismatch; never writes twice.
3. evaluate_f2: the section 8 verdict on the ledger (36 calendar months from the first record, series = net_pnl of every
   record in the window, no --clock-start option at all), reusing forward/evaluate.py's functions; plus a descriptive
   look (section 9; no p-value in the look).
4. config_f2.json: schema "stage_e24_f2_config/1", test_id "E22-F2", capital 25000, leverage cap 50000 (with the formula
   2 x capital and a source), the fractional increment, b, s, the SEC fee rate and FINRA TAF values with their sources,
   the 11 symbols and BIL, each instrument's spec (multiplier 1, exposure, the E22-F1 micro it maps to). Values still
   marked [SLOT] in the prereg go in as the prereg's declared defaults with "source": "PENDING facts <id>" so the lead
   can replace them; a test must fail if any "PENDING" string remains, marked xfail(strict=False) until the lead fills
   them. tables_f2.json: per-ETF half spread per share, pinned equal to config_f2.json by a test.
5. daily_f2.py: run one session (source from forward.sources_alpaca when credentials exist, else a CSV source), then
   the shadow route (forward/orders_alpaca.py, forward/shadow_f2.json "enabled": false by default) only when enabled;
   a "warmup" subcommand writing the warm-up file and its sha256. The shadow route reads the record only.
6. Tests (TDD, hand-written fixtures): the rule equals E22-F1's on the same synthetic series (same forecast and same
   unrounded target per unit of dollar vol, before the cap); the cap (binding and not binding; proportional scale; the
   second check); the buffer; fractional longs and whole-share shorts toward zero; a sign change; a split day and a
   distribution day (shares change, P&L equals the total-return formula); each P&L term on a hand-computed example
   including a weekend accrual; a missing ETF, a missing BIL, a missing day, a declared-closed day matching the
   calendar, SourceUnavailable writes nothing; ledger chain and re-run semantics; the verdict on a synthetic ledger
   (PASS and FAIL cases, the 36-month window); and the E22-F2 ledger byte-identical with the shadow route on and off
   over several fixture days (use a fake trading client for forward/orders_alpaca.py).

Boundaries: do not modify any file in reports/stage_e22_f1_files.sha256 (check with `sha256sum -c --quiet
reports/stage_e22_f1_files.sha256` at the end) and do not edit forward/etf_bars.py, forward/sources_alpaca.py,
forward/orders_alpaca.py, forward/shadow_f2.json (AlpacaCoder) or forward/*ibkr*, forward/daily_f1.py,
forward/shadow_f1.json (IBKRCoder), base_rules/, multiday/, trigger_hold/, live/, ops/, sim/, rules/, screening/, data/,
pyproject.toml, uv.lock, reports/stage_e24_prereg_F2.md (the lead's). Run only your tests plus tests/test_forward_*.py.
No commits.

Output: the code and tests; reports/stage_e24_briefs/f2/f2book_report.md (file list with sha256, a table mapping every
prereg sentence of sections 4-8 to the function that implements it, questions where the text was ambiguous, test output
verbatim). Return: the report path, a summary of at most 200 words, anything unfinished.
