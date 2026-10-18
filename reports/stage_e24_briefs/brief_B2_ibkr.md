# Brief B2-B4: IBKRCoder-OpusXHigh (worker-xhigh, opus). Stage E.24 Part B

Objective: forward/sources_ibkr.py (daily prices of E22-F1's 12 micros from IBKR through IB Gateway, in E22-F1's
history format, plus the warm-up assembly), forward/orders_ibkr.py (the optional shadow order route), a small daily
driver, and tests against a mock gateway. No network: never connect to IB Gateway, TWS or any IBKR host; no account,
no credentials, no .env read. The registered verdict of E22-F1 stays the paper book of its freeze; IBKR orders are a
shadow record only.

Inputs (read by section, never whole): docs/prompts/STAGE_E.24.md Part B; reports/stage_e22_prereg_F1.md (FROZEN,
sections 2, 3, 5, 6, 7); forward/README.md, forward/sources.py (SettlementSource protocol, DaySettlements, Missing,
CsvSettlementSource and its CSV format), forward/history.py (HistoryRow, load_warmup JSONL, back_adjusted_series:
switch rows must hold both contracts' prices), forward/runner.py (ForwardRunner(ledger_path, source, config, *,
target_fn, warmup); run_date; its CLI --csv/--warmup), forward/rolls.py and forward/rolls_f1.json (contract months,
active_contract, roll dates). Facts: reports/stage_e24_briefs/facts/ibkr_facts.md and ibkr_factcheck.md are being
written now (ETA about 02:35 PDT). Phase 1 (now): build against a gateway Protocol of your own that mirrors the ib_async
API (Future/Contract, qualifyContracts or reqContractDetails with includeExpired, reqHistoricalData with barSizeSetting
'1 day', BarData.date/close, connect/disconnect, disconnectedEvent, placeOrder, Trade/Fill objects). Phase 2: when
both facts files exist (check with a one-off `ls` every 10 minutes or so; never a wait loop that greps your own command
line), read them and align contract fields, exchanges, bar date conventions, time zones, expired-contract depth,
pacing and error codes; apply the fact checker's corrections; cite fact numbers in code comments where a constant
comes from a fact.

Requirements:
1. Dependencies: the vendor library is ib_async 2.1.0, pinned in forward/requirements_broker.txt (a uv overlay; do
   NOT edit pyproject.toml or uv.lock: harness v13 pins them). Import ib_async lazily, only inside the live client
   factory; every module must import and every test must run without ib_async installed. Optional contract tests that
   check your Protocol against the real ib_async classes (no network) may use pytest.importorskip("ib_async") and can be
   run with `uv run --frozen --with-requirements forward/requirements_broker.txt pytest -q -p no:cacheprovider <file>`.
2. Contract resolution: instrument + contract_id (e.g. MNQZ26, 10YF27) -> an IB futures contract (symbol, exchange,
   lastTradeDateOrContractMonth, currency, multiplier check against config_f1.json), using forward.rolls for the month
   codes; expired contracts via includeExpired. A contract that does not resolve uniquely is an error, never a guess.
3. Daily prices: SettlementSource.settlements(trade_date) returns {instrument: {contract_id: price}} for the reference
   contract and, on and around roll dates, the next contract (the frozen runner needs both on a switch date). Record
   which bar field is used (whatToShow, close) and the bar's own date. Time zones: CME trade dates (the session that
   ends at the settlement), never the local calendar date of the ThinkPad; a bar for date t is accepted only after a
   declared cutoff (settlement time plus the data delay); before it, the day is not ready (no record).
4. Missing vs unavailable: Missing(reason) only when the source affirmatively has no bar for that date while bars for
   later dates exist or the session is over and confirmed; a connection failure, timeout, pacing violation or partial
   response raises a SourceUnavailable error so that NO ledger record is written (a missing day counts as a 0 in
   E22-F1's evaluation, so a false Missing is harmful). Reconnect with bounded retries and backoff.
5. Warm-up assembly: daily prices of the 12 micros from 2024-03-01 (V42) to the day before the start date, per
   contract, with each day's reference contract after that day's rolls per rolls_f1.json, written as the JSONL of
   HistoryRow objects that forward.history.load_warmup reads; switch rows carry both contracts' prices so
   back_adjusted_series (additive, Panama) works; contracts missing early history give fewer prior settlements (the
   runner keeps such an instrument flat until 256 differences). Write the file and its sha256; report per instrument
   the count of rows and the first date. Also an export of daily prices to forward.sources' CSV format (the frozen
   runner's --csv), so the frozen runner CLI can run unchanged on IBKR-sourced data.
6. If ibkr_facts.md says the daily bar close is NOT the official settlement, still build the adapter (it labels the
   field it delivers), but register nothing and change nothing in E22-F1: the lead writes the user decision.
7. forward/orders_ibkr.py: after each day's runner step, compute the changes between the record's target positions
   and the shadow account's current positions, place them as paper orders (order type configurable, documented),
   and append orders and fills (price, time, commission, contract) to a separate shadow ledger (forward.ledger.Ledger,
   append-only sha256 chain) whose path can never equal the E22-F1 ledger path (refuse it). Off by default; a config
   switch (a new JSON file, e.g. forward/shadow_f1.json with "enabled": false) turns it on. The shadow route reads the
   E22-F1 ledger only; it never writes to it or changes the runner's inputs.
8. A daily driver (e.g. forward/daily_f1.py): source -> frozen ForwardRunner.run_date -> optional shadow route; plus
   a "warmup" subcommand. Credentials: none in code; connection parameters from environment variable NAMES you define
   (e.g. IBKR_GATEWAY_HOST, IBKR_GATEWAY_PORT, IBKR_CLIENT_ID, IBKR_ACCOUNT_ID); list every name in your report. Never
   print or log any value of them.
9. Tests (new files tests/test_forward_ibkr_*.py, TDD, mock gateway, no network): contract resolution (incl. expired
   and ambiguous), rolls across the anchor date (both contracts delivered on the switch date; reference switches as
   rolls_f1.json says), a missing day, a reconnect (drop mid-request, then recovery; and exhaustion -> SourceUnavailable,
   no ledger record), a partial history, the warm-up assembly (round trip through load_warmup and back_adjusted_series),
   time zones (a bar fetched before the cutoff, a bar whose date differs from the local date), and the E22-F1 ledger
   byte-identical with the shadow route on and off over several fixture days (compare file bytes and sha256).
   Fixtures are written by hand (synthetic prices), never fetched.

Boundaries: do not modify any file in reports/stage_e22_f1_files.sha256 (forward/README.md, core.py, runner.py,
sources.py, history.py, rolls.py, rolls_f1.json, config_f1.json, tables_f1.json, the listed tests, ...); verify with
`sha256sum -c --quiet reports/stage_e22_f1_files.sha256` at the end. Do not touch forward/*alpaca*, forward/*_f2*,
forward/etf_bars.py (another worker), base_rules/, multiday/, trigger_hold/ (another worker), live/, ops/, sim/,
rules/, screening/, data/, pyproject.toml, uv.lock. No market data, no network except none. Run only your own tests plus
tests/test_forward_*.py (`uv run pytest -q -p no:cacheprovider tests/test_forward_*.py`); the full suite is the lead's.
No commits.

Output: the code and tests; reports/stage_e24_briefs/ibkr/ibkr_report.md (file list with sha256, design notes per
requirement, env var names, the cutoff and time-zone rule, which facts each constant uses, test output verbatim,
open questions for the lead). Return: the report path, a summary of at most 200 words, anything unfinished.
