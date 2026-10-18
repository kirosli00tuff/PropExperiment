# Brief C3a: AlpacaCoder-OpusXHigh (worker-xhigh, opus). Stage E.24 Part C (adapter half)

Objective: forward/etf_bars.py (the ETF bar interface E22-F2's runner consumes; write it FIRST, within your first
15 minutes, because F2BookCoder imports it), forward/sources_alpaca.py (daily ETF bars from Alpaca's market data API),
forward/orders_alpaca.py (the optional shadow order route on Alpaca paper), and tests on mocks and hand-written
fixtures. No network: never call any Alpaca endpoint (paper or live, trading or data); no account, no keys, no .env
read. E22-F2's registered verdict will be its paper book; Alpaca paper orders are a shadow record only.

Inputs: docs/prompts/STAGE_E.24.md Part C; forward/sources.py (Missing, the SettlementSource style and the CSV source
pattern to mirror), forward/ledger.py (Ledger, append-only sha256 chain); facts: reports/stage_e24_briefs/facts/
alpaca_facts.md and alpaca_factcheck.md are being written now (ETA about 02:35 PDT). Phase 1 (now): etf_bars.py and the
adapter against a client Protocol mirroring alpaca-py 0.44.0 (StockHistoricalDataClient.get_stock_bars with
StockBarsRequest(symbol_or_symbols, timeframe=TimeFrame.Day, start, end, adjustment, feed); TradingClient(paper=True)
.submit_order / get_orders / get_all_positions / get_account). Phase 2: when both facts files exist (a one-off `ls`
every 10 minutes or so; never a wait loop that greps your own command line), align feed, adjustment semantics, bar
timestamps and time zone, fractional and short rules, order types near the close, rate limits; apply the checker's
corrections; cite fact numbers in comments where a constant comes from a fact.

forward/etf_bars.py (the interface; keep it small and exact):
- `@dataclass(frozen=True) class EtfBar: close: float` (the session's raw, unadjusted closing price, USD per share),
  `ret: float | None` (total return from the previous session's close: adj(t) / adj(prev) - 1, both values taken from
  ONE fetch with adjustment "all", so splits and distributions are inside the return; None only for the first row of
  a history), `prev_date: date | None` (the session ret is measured from). Validation: finite, close > 0, ret > -1.
- `EtfDay = Mapping[str, EtfBar]` (symbol -> bar); `Missing` re-exported from forward.sources (do not edit that file);
  `class SourceUnavailable(Exception)` (a connection failure, timeout, rate limit or partial response: the caller must
  write NO ledger record); `class EtfBarSource(Protocol): def bars(self, trade_date: date) -> EtfDay | Missing`.
- Warm-up JSONL: one line per session `{"date": "YYYY-MM-DD", "bars": {"QQQ": {"close": ..., "ret": ..., "prev_date":
  ...}, ...}}`, strictly ascending; `load_etf_warmup(path)`, `dump_etf_warmup(rows, path)`, `etf_history_sha256`.
- `InMemoryEtfSource` and `CsvEtfSource` (header trade_date,symbol,close,ret,prev_date; duplicates are errors) for
  manual entry and tests.

forward/sources_alpaca.py:
1. Library: alpaca-py 0.44.0 pinned in forward/requirements_broker.txt (uv overlay; do NOT edit pyproject.toml or
   uv.lock: harness v13 pins them). Import alpaca lazily inside the client factory; modules and tests must work without
   it. Optional contract tests against the real alpaca-py request classes (no network) may use
   pytest.importorskip("alpaca") and run under `uv run --frozen --with-requirements forward/requirements_broker.txt`.
2. For a trade date t and a symbol list (E22-F2's 11 ETFs plus BIL, the cash benchmark; take the list from the caller,
   do not hard-code the universe): request daily bars over a short window ending at t with adjustment "raw" and with
   adjustment "all" (same feed); close = raw close of t; ret = all-adjusted close(t) / all-adjusted close(previous
   bar in the same response) - 1; prev_date = that previous bar's session date. Session dates in America/New_York, never
   the ThinkPad's local date. A bar for t is accepted only after a declared cutoff (the close plus the data delay
   and Alpaca's bar finalisation; from facts); before it the day is not ready (raise or return a NotReady signal the
   driver treats as "no record yet").
3. Missing vs unavailable: Missing(reason) for a symbol only when the response affirmatively lacks t's bar while the
   session is over (e.g. a halted ETF); a whole-day Missing only when no symbol has t's bar after the cutoff and t is a
   weekday not declared closed; transport errors, HTTP 429/5xx, timeouts or truncated pagination raise
   SourceUnavailable. Bounded retries with backoff, honouring the documented rate limits.
4. Warm-up: sessions from 2024-03-01 to the day before the start date for every symbol, one fetch per adjustment, in
   the warm-up JSONL above, with its sha256; report the first date and row count per symbol.
5. Credentials: environment variable NAMES ALPACA_PAPER_KEY_ID and ALPACA_PAPER_SECRET_KEY (read only inside the
   client factory, never printed, logged or stored); the trading client is constructed with paper=True only, and any
   attempt to use a live trading endpoint raises.

forward/orders_alpaca.py (shadow route):
6. Input: the E22-F2 ledger record just written by the F2 runner (another worker builds forward/runner_f2.py; read
   only these record fields: "date", "targets" {symbol: shares (float)}, "positions" {symbol: shares}; if the runner
   names them differently later, adapt in one mapping function). Compute the changes against the shadow account's
   positions and place them as paper orders for the next session's close (market-on-close / time_in_force per facts,
   submitted before the cutoff), fractional quantities for longs, whole shares for shorts, a long-to-short crossing split
   into a close-the-long order and a whole-share short order; append orders and fills to a separate shadow ledger
   (forward.ledger.Ledger) whose path can never equal the E22-F2 ledger path (refuse it). Off by default; a config
   switch (forward/shadow_f2.json, "enabled": false) turns it on. It never writes to the E22-F2 ledger.
7. Tests (new files tests/test_forward_alpaca_*.py and tests/test_forward_etf_bars.py, TDD, mocks, no network): the
   interface validation and warm-up round trip; raw vs all-adjusted return on a split day and on a distribution ex-date
   (hand-written fixtures); a missing symbol, a missing day, a rate limit then recovery, exhaustion -> SourceUnavailable;
   the cutoff and time zone (a request before the close; a session date that differs from the local date); pagination;
   order construction (fractional long, whole-share short, crossing zero, no-change day, refusing the F2 ledger path,
   refusing a live endpoint).

Boundaries: do not modify any file listed in reports/stage_e22_f1_files.sha256; do not touch forward/*ibkr*,
forward/daily_f1.py, forward/shadow_f1.json (IBKRCoder), forward/*_f2.py and forward/config_f2.json (F2BookCoder; you
own only etf_bars.py, sources_alpaca.py, orders_alpaca.py, shadow_f2.json and your tests), base_rules/, multiday/,
trigger_hold/, live/, ops/, sim/, rules/, screening/, data/, pyproject.toml, uv.lock. Run only your tests plus
tests/test_forward_*.py. No commits.

Output: the code and tests; reports/stage_e24_briefs/alpaca/alpaca_report.md (file list with sha256, design notes per
requirement, env var names, cutoff and time-zone rule, the facts each constant uses, test output verbatim, open
questions). Return: the report path, a summary of at most 200 words, anything unfinished.
