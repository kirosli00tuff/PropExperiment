# C3a report: Alpaca adapter half (AlpacaCoder-OpusXHigh, Stage E.24 Part C)

## Status and timeline

All times are PDT and come from `date`.

- **01:40 to 01:59:** Phase 1. forward/etf_bars.py was written by 01:42.
- **Usage-limit pause.**
- **06:12 to 06:21:** resumed. The lead's ruling at about 06:15 switched the return formula to raw bars plus corporate
  actions, and that change is applied.
- **06:26:** alpaca_factcheck.md appeared.
- **06:27 to 06:31:** its corrections were applied, together with one more fix found while checking it: capital gains
  distributions carry `long_term_rate` and `short_term_rate`, not `rate` (section 2).
- **06:32:** this report was finalised.

Constraints held throughout:
- No network: no Alpaca endpoint was called, no keys were used and no .env file was read.
- alpaca-py 0.44.0 came only from the local uv cache (`--offline`).
- No commit was made.

## 1. Files (sha256 at 06:30 PDT)

| File | sha256 |
|---|---|
| forward/etf_bars.py | 6f7aa2d8bef1bc0a1411bacaa82a6f06b203fa1bb8d80c401cea9fad573dbe7e |
| forward/sources_alpaca.py | 8158ba158f92e2c2002c72ad24e475c318e871b42f8af4a409295b30107f66a0 |
| forward/orders_alpaca.py | 7376e9f273062060732287941f208622c572ca053fe01e37e8f2b1963f49ed82 |
| forward/shadow_f2.json | c44924c6b70ec678b08bbf6a07a9cb594a2927c38c88ebbd853f9a15dd94d360 |
| tests/test_forward_etf_bars.py | 9785ed7b72a527780125068262912f9378f17d3df74f03de4afa7f57ef66bc16 |
| tests/test_forward_alpaca_sources.py | 602f862e3ae78362f9942886d6953ac07112b168b6552b0d62a52d631d4e68b6 |
| tests/test_forward_alpaca_orders.py | c2f29aa0bc5af1656ee233c2f026a229ba2abc069eb430bf6549b9c4a7381c94 |
| tests/test_forward_alpaca_contract.py | 3eda6c843ddb22fdefbdd4fbc39ec10391823b33dc0a8ae44ce61b8cc4412cd8 |

Boundaries:
- `sha256sum -c reports/stage_e22_f1_files.sha256`: all 14 files OK, 0 failures, checked at 06:29.
- Not touched: forward/sources.py, forward/ledger.py, pyproject.toml, uv.lock, the IBKR files, the *_f2.py files and
  config_f2.json.
- forward/requirements_broker.txt was read only.
- alpaca-py is imported lazily, only inside the factories (`make_data_client`, `make_corporate_actions_client`,
  `alpaca_bars_request`, `alpaca_corporate_actions_request`, `make_trading_client`, `market_order_request`,
  `orders_query`). A subprocess test imports all three modules with `sys.modules['alpaca'] = None` and checks that a
  factory raises ImportError with the overlay hint.

## 2. Design notes per requirement

### etf_bars.py (the interface)

- `EtfBar(close, ret, prev_date)` is frozen. It requires a finite close > 0 and a finite ret > -1; ret and prev_date
  are both None or both set; prev_date must be a `date`, not a `datetime`.
- `EtfDay = Mapping[str, EtfBar]`. `Missing` is re-exported from forward.sources, which was not edited.
- `SourceUnavailable(Exception)` is defined here.
- **Added beyond the spec:**
  - `NotReady(SourceUnavailable)`. A runner that catches SourceUnavailable writes no record before the cutoff with no
    change of its own.
  - `EtfDayRow` (one warm-up row).
- `EtfBarSource` is a runtime-checkable Protocol. Also provided: `normalize_etf_day` and `InMemoryEtfSource`. The
  in-memory source accepts a SourceUnavailable instance as an answer and raises it.
- `CsvEtfSource`:
  - header `trade_date,symbol,close,ret,prev_date`;
  - a duplicate (date, symbol) is an error;
  - the file is re-read on every call.
- Warm-up JSONL:
  - written as canonical lines, so `etf_history_sha256(rows)` equals the sha256 of the file `dump_etf_warmup` writes;
  - dumping refuses to overwrite;
  - the loader checks that dates strictly ascend and that each symbol's `prev_date` is its own previous row.
- A missing symbol is absent from the EtfDay, as in forward/sources.py. Per-symbol `Missing(reason)` objects are in
  `AlpacaEtfSource.fetch_day(t).missing`.

### sources_alpaca.py (changed per the lead's ruling and E22-F2 registration section 6, bullets 1 to 3)

**Requests per day.** Two requests: daily bars with adjustment "raw" over [t - 21 days, t], and GET
/v1/corporate-actions for the symbols over the same dates. The "all" adjustment is never requested anywhere.

**Return formula.** `close = rawclose(t)`. `prev` is the symbol's previous bar in the same response.

    ret = k x (rawclose(t) + D) / rawclose(prev) - 1     (function total_return)

- `k` is the product of `new_rate / old_rate` over forward_split and reverse_split actions with ex_date in (prev, t].
- `D` is the sum of per-share amounts with ex_date in (prev, t]:
  - cash_dividend (special included): `rate`;
  - capital_gains_distribution: `long_term_rate` + `short_term_rate`. Per the corporate-actions reference, "At least
    one of the two rates is always present", and the type has no `rate` field.
- Amounts in a currency other than USD raise SourceUnavailable.
- An ex_date inside a bar gap is applied to the return that spans the gap.
- `DayFetch.applied[sym]` keeps the actions used, for the record.

**Corporate-actions client.**
- It is alpaca-py's `CorporateActionsClient` with `raw_data=True`.
- Raw mode is required. The 0.44.0 typed `CorporateActionsSet` has no capital-gains model and silently drops that key,
  and `CorporateActionsType` has no capital-gains member. A contract test demonstrates both.
- The request asks for all types, so capital gains and the flagged types come back, with `limit=None`. The class
  default of 1000 would cap the result silently; with no limit the SDK follows `next_page_token`.
- The parser (`parse_corporate_actions`):
  - accepts `{type_plural: [record]}` or `{"corporate_actions": {...}}`;
  - matches type names singular or plural;
  - accepts both "capital_gains_distribution" and "capital_gain_distribution";
  - rejects a missing or bad ex_date, rate, new_rate or old_rate (old_rate 0, negative or non-finite) with
    SourceUnavailable.

**Flags.** Any other type that names a requested symbol in any `*symbol` field (for example spin_off's
`source_symbol`) is a flag in `DayFetch.flags[sym]`, such as `"spin_off ex_date 2026-11-04"`. It is never booked. The
runner decides whether the symbol is held.

**The endpoint's start/end is a process_date interval.** The reference says "The corporate actions are sorted by their
`process_date`" for both start and end, and defines process_date as "The date when the corporate action is processed by
Alpaca". Its examples show process_date up to about 15 days after ex_date: cash dividend FCF, ex 2023-05-04, processed
2023-05-19; capital gains GCAD, ex 2025-12-26, processed 2026-01-08. Therefore:
- the daily request covers process dates [t - 21 - 60, t + 60] and the warm-up [first - 60, last + 60]
  (`CA_MARGIN_DAYS = 60`);
- ex_date in (prev, t] is filtered locally;
- a test shows a dividend listed by a process_date 15 days after its ex_date is still found.

**Late actions.** `AlpacaEtfSource.corporate_actions(start, end, symbols=None)` returns what the endpoint publishes for a
process_date range as `CorporateActions(booked, other)`, with `.between(sym, after, through)` and `.flags(...)`. The
runner uses it to find actions whose ex_date falls in an already-recorded session and book them as late_ca. It should
query by process_date, for example from a few weeks before the last record to today.

**Client construction.** By default the CA client is built on first use by `make_corporate_actions_client()` with the
same paper keys, so daily_f2.py's existing `AlpacaEtfSource(universe, client, feed=..., closed_dates=...)` call works
unchanged. Tests inject `ca_client` and `ca_request_factory`.

**Missing vs unavailable** (unchanged except that the raw-versus-all comparison is gone):
- A symbol lacking t's bar is re-requested alone. If it is still absent, it is Missing; if the single-symbol answer has
  it, the multi-symbol response was partial and the source raises SourceUnavailable.
- The whole day is Missing only when no symbol has t's bar, each one confirmed.
- A weekend or declared closed date raises `NotASession`.
- A symbol with no earlier bar in the window is Missing, never given a None ret.
- A corporate-actions transport error raises SourceUnavailable, through the same retry path.

**Retries** apply to both calls:
- HTTP 429/500/502/503/504 and OSError are retried, up to 5 attempts, with backoff 2, 4, 8 and 16 s capped at 60 s;
  `Retry-After` and `X-RateLimit-Reset` are honoured (A9).
- Other errors (403, 422, an empty-body AttributeError) raise at once.
- Requests are paced at no more than 200 per minute (A9).
- No `limit` is passed on bars. A failure part-way through pagination raises SourceUnavailable.

**Warm-up.** `fetch_warmup(start_date)` makes one raw-bar fetch and one corporate-actions fetch, both from 2024-03-01
to start_date - 1, and applies the same formula per row.
- A symbol with no bars raises SourceUnavailable.
- A symbol whose sessions differ from the union is re-requested alone. If the two answers differ it raises; if they
  agree the gaps are accepted and reported.
- It returns `rows`, `sha256`, `first_date`, `row_count`, `gaps` and `corporate_actions`. `write_warmup` re-checks the
  sha256.

**Credentials** (items 1 and 5): only the names `ALPACA_PAPER_KEY_ID` and `ALPACA_PAPER_SECRET_KEY` appear, read in
`paper_credentials`. alpaca-py reads no environment variables (A1, A10). A missing variable is named in the error; no
value is ever printed.

### orders_alpaca.py (item 6; unchanged since 01:59)

- **Reading the F2 record:** `f2_fields()` alone knows `date`, `targets` and `positions` (`F2_FIELDS`).
- **Paths:** the shadow ledger is refused if it is the F2 ledger by resolved path, abspath, symlink or hardlink. This is
  checked at construction and again at run.
- **Disabled (the default):** `run()` returns None and builds no client.
- **Checks before any client call:** a date on or before the last shadow record raises `LedgerOrderError`, and a time
  outside the window raises `ShadowWindowError`.
- **Client and account checks:** paper endpoint only (`assert_paper`; `make_trading_client` refuses `paper=False` and
  a live `url_override`). The account must be ACTIVE and not blocked. Open foreign orders, and open shadow orders from
  earlier dates, are refused.
- **Order rules:**
  - Opening shorts need shortable, easy_to_borrow and shorting_enabled (A6).
  - Crossings are split: sell-to-close then a whole-share sell-to-open; a cover then a buy.
  - A no-change day places no orders.
  - Held symbols that are not in the targets are logged as unmanaged and left alone.
- **Crash safety:** client order ids are deterministic (`e22f2-YYYYMMDD-SYM-n`), so a rerun after a crash records the
  orders as "existing" and does not resubmit them.
- **Errors and fills:** submit errors are recorded as "rejected" (HTTP 4xx) or "error". Fills of earlier orders are
  reconciled into the next record, and orders not yet found stay `pending`.
- **Mode (disclosed, accepted by the lead as Q3):** the default `moc_whole` rounds every target half away from zero to
  whole shares and sends market-on-close orders. The reason is that fractional orders allow TIF `day` only and CLS
  takes whole shares only (A5, A8).
  - The brief's "fractional quantities for longs" is available only as `fractional_day`: fractional longs and whole
    shorts as `day` orders.
  - In that mode, orders submitted after t's close queue for the next session and fill near its OPEN, not its close.

### Item 7: tests on mocks and hand-written fixtures

- **Interface:** validation; the warm-up round trip; the sha256 equal to the file hash; a broken prev_date chain.
- **Corporate actions:**
  - a split day: a UNG-style 1:4 reverse split, k = 0.25, +2% rather than +308%;
  - a dividend ex-date: TLT 0.30, where the raw return is negative and the total return positive;
  - a 2:1 split and a 0.10 dividend on one day;
  - a special dividend plus a capital gains distribution with both legs;
  - a capital gains distribution with one leg; a capital gains record without legs, giving SourceUnavailable; a
    non-USD amount, giving SourceUnavailable;
  - an action listed by a process_date 15 days after its ex_date, still found;
  - BIL's monthly dividend: counted on its ex_date MON, not on WED;
  - an ex_date inside a bar gap;
  - an empty corporate-actions response, giving raw returns;
  - a transport error on the corporate-actions call (ConnectionError exhausted, and a 403 that is not retried), giving
    SourceUnavailable;
  - a spin-off as a flag;
  - a malformed split (old_rate 0);
  - the range API for late actions;
  - the warm-up with a dividend and a split.
- **Data path failures:** a missing symbol, a missing day, a rate limit then recovery, and exhaustion giving
  SourceUnavailable.
- **Cutoff and time zone:** a request before the close; a bar at 05:00Z whose Vancouver date is the day before; 22:30
  PT already being the next New York date.
- **Pagination:** a multi-page response, a failure mid-page, and a truncated multi-symbol response.
- **Orders:** fractional long, whole-share short, both crossings, a no-change day, refusing the F2 ledger path,
  refusing a live endpoint, the window, a rerun after a crash, fills, pending orders, and the F2 ledger staying
  byte-identical.

## 3. Env var names, cutoff and time-zone rule

- **Credentials:** `ALPACA_PAPER_KEY_ID` and `ALPACA_PAPER_SECRET_KEY`. They are read only inside `paper_credentials`,
  which the three client factories call. They are never printed, logged or stored.
- **Session date:** `bar.timestamp.astimezone(America/New_York).date()`. A naive timestamp or clock is refused.
- **Cutoff:** `bar_cutoff(t) = t 16:00 America/New_York + 2 h` (18:00 ET, 15:00 PT). Before it, `NotReady` is raised
  and no request is sent.
- **Request end:** a bars request's `end` is `min(t 23:59:59 ET, now - 16 min)`. The corporate-actions request covers
  [t - 21 days, t] as dates.
- **Early-close days** keep the 18:00 cutoff, which is conservative.
- **Practical schedule:** after 19:00 ET (16:00 PT), after the AiTrader window.

## 4. Facts behind each constant (alpaca_facts.md; the registration where it decides)

| Constant | Value | Source |
|---|---|---|
| `DATA_FEED` | "sip"; the caller passes `feed` (daily_f2.py passes config_f2.json `data_feed`) | registration s6 (sip, with the iex rule on a first-session refusal); A2; A4 |
| `QUERY_END_LAG` | 16 min | A2 FAQ ("`end` … at least 15 minutes old … SIP") |
| `BAR_CUTOFF_DELAY` | 2 h | A4 (closing trade sets the close; extended hours do not; revision timing not established), A2, A8 |
| session date rule | New York date of `t` | A4 |
| raw bars only; returns from corporate actions | `total_return` | registration s6 bullets 1-2; A3 ("all" method undocumented) |
| corporate-action types booked | cash_dividend (special included), capital_gains_distribution, forward_split, reverse_split | registration s6; A3 (type list; the fact check lists all 16 types) |
| capital gains amount | `long_term_rate` + `short_term_rate` | /v1/corporate-actions reference (pages/alpaca/ref_us_corporateactions-1.md, `capital_gains_distribution` schema: "At least one of the two rates is always present") |
| `CA_MARGIN_DAYS` | 60 (the request is a process_date interval) | same reference: start/end "sorted by their `process_date`"; examples with process_date 15 days after ex_date |
| shorts whole shares, fractional sells long only | | A5 as corrected by the fact check (FR line 84: "We do not support short sales in fractional orders. All fractional sell orders are marked long.") |
| account fields logged include `pattern_day_trader`, `daytrade_count` | | A7 as corrected (PDT status at Alpaca not settled; keep a guard) |
| other types flagged | everything else naming a symbol | registration s6 bullet 3 |
| `RATE_LIMIT_PER_MINUTE`, 429, reset headers | 200/min; `X-RateLimit-Reset` | A9 |
| keys passed explicitly | env names read by our code | A1, A10 |
| `PAPER_TRADING_URL` | https://paper-api.alpaca.markets | A1, A10 |
| CLS window | after 19:00 ET on t, before 15:45 ET on the next session | A8 |
| moc_whole whole shares | | A5, A8 |
| `FRACTION_DECIMALS` | 9 | A5 |
| opening short needs shortable and easy_to_borrow | | A6 |

**alpaca_factcheck.md (06:26): applied.** Its result is 9 OK and 1 OVERSTATED (A7, the PDT sentence).

| Correction | What I did |
|---|---|
| 1 (A5: fractional shorts not supported) | Matches the existing design (shorts whole in both modes); the citation was added in orders_alpaca.py |
| 2 and 3 (A7: PDT status not settled) | The shadow record now logs `pattern_day_trader` and `daytrade_count`. A daily close route makes no day trades, so this is a log, not a block |
| 4 (A2: support for SIP when `end` >= 15 min) | Consistent with `QUERY_END_LAG = 16 min`; no change |
| 5 (A4: the iex close differs from the sip close in the vendor example, 171.29 vs 171.21) | Supports the explicit feed; no change |
| 6 to 9 (citation details) | No code impact |

While checking the reference for correction 4, I found two more things the facts file did not cover: the capital-gains
field names and the process_date interval. Both are fixed above.

## 5. Test output (verbatim tails)

My tests, run in the project environment:

```
$ uv run --frozen pytest -q -p no:cacheprovider tests/test_forward_etf_bars.py tests/test_forward_alpaca_sources.py tests/test_forward_alpaca_orders.py tests/test_forward_alpaca_contract.py
114 passed, 1 skipped in 0.46s
```

The contract tests against the real alpaca-py 0.44.0 classes, with no network:

```
$ uv run --frozen --offline --with-requirements forward/requirements_broker.txt pytest -q -p no:cacheprovider tests/test_forward_alpaca_contract.py
8 passed, 1 warning in 0.72s
```

(The warning is the websockets.legacy DeprecationWarning inside the overlay.)

All of `tests/test_forward_*.py` at 06:29 PDT:

```
FAILED tests/test_forward_f2_late_ca.py::test_late_split_multiplies_shares_held_into_ex_session
FAILED tests/test_forward_f2_late_ca.py::test_duplicate_not_booked_twice_and_rerun_reuses_stored_input
FAILED tests/test_forward_f2_late_ca.py::test_unknown_type_of_held_etf_flagged_not_booked
FAILED tests/test_forward_f2_late_ca.py::test_missing_day_defers_late_action
5 failed, 370 passed, 2 skipped in 25.33s
```

- All 5 failures are in F2BookCoder's new tests/test_forward_f2_late_ca.py. One more, test_late_dividend_booked_as_cash…,
  is in the full log. Each fails with `KeyError: 'cash_usd'` inside their runner (forward/runner_f2.py, modified 06:29,
  still being written).
- Their fake source mirrors my `DayFetch` (`answer()`, `applied`, `flags`), so the interface lines up.
- At 06:20, before that file existed: `350 passed, 2 skipped`. The IBKR failure from 06:13 had been fixed by then.

Ruff is clean on all my files.

## 6. Questions and notes for the lead

1. **Resolved:** the lead's ruling replaced Q1 to Q3.
   - Returns come from raw bars plus corporate actions, with "all" removed.
   - The feed is "sip" with the registration's iex rule.
   - Whole-share MOC is the default in the shadow route (disclosed in section 2).
2. **For the registration, needs the lead's judgment: late distributions may be the normal case, not the exception.**
   The reference's examples show dividends and capital gains processed about 15 days after their ex_date (process_date
   equal to the payable date in the FCF example). If Alpaca publishes an action only once it is processed, D is often
   unknown when the ex_date session is recorded. Most distributions would then arrive through section 6 bullet 3
   (booked later as cash P&L, flagged late_ca).
   - That would leave the ex-date drop in r_i and in the back-adjusted signal series of bullet 4. Only the P&L gets the
     cash.
   - Splits look processed on their ex_date (SRE example), so they should normally be on time.
   - The wide process_date window catches anything already published. Whether actions are published before processing
     cannot be known without a connection; check it on the first connection session, for example by listing BIL's
     actions with process dates after today.
3. **Resolved:** the capital-gains field names (`long_term_rate`, `short_term_rate`) come from the saved reference.
4. **For F2BookCoder / daily_f2.py:**
   - `AlpacaEtfSource` now takes `ca_client=`, `ca_request_factory=` and `ca_client_factory=`. Tests of the Alpaca path
     should inject a CA fake.
   - For late_ca booking, call `source.corporate_actions(start, end, symbols)`.
   - `DayFetch.applied` and `DayFetch.flags` carry per-day actions and flags, if the runner wants them in the record.
     `bars()` returns only the EtfDay.
5. **Unverified paper behaviour, still open:** the CLS "contact sales" asterisk and paper's quote-based CLS fills (A8);
   whether a short leg is accepted while the close-the-long leg of the same symbol is pending (a rejection is recorded
   and the next day re-plans from flat); and paper's lack of dividend and borrow-fee simulation (A6), which makes the
   shadow record's P&L not comparable with the book.

## 7. Not finished

- **Fable review** of these files: the lead's C4 step, not yet done.
- **Two points to confirm on the first connection session:** whether corporate actions are published before their
  process_date (note 2), and whether the account gets SIP bars (registration s6).

## Wave 3 fixes (AlpacaFixer-OpusXHigh, 2026-10-18 11:54 to 12:10 PDT)

Brief: reports/stage_e24_briefs/brief_wave3_fixers.md (Common + AlpacaFixer); rulings: review_rulings.md C4a; review:
alpaca/adapter_review.md. Test first: the new unit tests below were written and run RED before each fix (sources: 6
failed / 46 passed; orders: 3 failed / 35 passed; outputs kept in the session scratchpad, alpacafix/red_*.txt). The
two SDK contract tests were written after the fix, as guards of the real alpaca-py request path. No network, no keys,
no .env, no market data; pyproject.toml, uv.lock and the registration untouched; no commit.

### S1: corporate actions over any span; t's raw close whatever the window
- `AlpacaEtfSource.corporate_actions(start, end, symbols)` (forward/sources_alpaca.py:567) now returns every published
  action with **ex_date in [start, end], both ends included**, however long the span: one request over process dates
  [start - CA_MARGIN_DAYS, end + CA_MARGIN_DAYS] (the endpoint's interval is process_date), alpaca-py follows
  next_page_token to the last page (limit=None, unchanged), and `CorporateActions.within` (:357) keeps the ex_dates in
  the span (other types without an ex_date are kept, flags only). For a return over (prev, t] the runner calls
  `corporate_actions(prev, t, symbols)` and filters (prev, t], e.g. `.between(symbol, prev, t)` (leaves out
  ex_date == prev). The daily and warm-up calls now use the same method with ex_date spans (:495, :540): their
  requests are byte-for-byte the ones before (process dates [t - 81, t + 60] and [first - 60, last + 60]).
  Side effect for C4b (no edit by me): daily_f2's late-action call `corporate_actions(first - 31, last)` now asks
  process dates up to last + 60, so an action processed after the last record is seen at once (review N8 resolved).
- `fetch_day`: a symbol whose window holds t's bar and nothing earlier is no longer Missing. `_symbol_bar` (:592) and
  `_earlier_bar` (:617) re-request that symbol alone from GAP_FIRST_DATE (:104, = WARMUP_FIRST_DATE 2024-03-01); the
  wider answer must give the same close for t and no earlier bar inside the window (else SourceUnavailable, partial
  response); r then spans the gap, with `corporate_actions(prev, t, (s,))` over the whole span (applied and flags as
  before). With no earlier bar at all since 2024-03-01, the bar is `EtfBar(close)` (ret and prev_date None: the first
  row of the symbol's history, as the interface defines). DayFetch keeps its fields (applied, flags).
- Tests: tests/test_forward_alpaca_sources.py:472 `test_corporate_actions_cover_every_ex_date_in_a_long_span_whatever
  _the_process_date` (14-month span, process_date 15 days after ex, ex == start included, ex outside excluded),
  :549 `test_return_spans_a_gap_longer_than_the_request_window` (30-day gap, dividend inside the gap before the daily
  span), :576 `test_symbol_with_no_earlier_bar_since_the_first_date_gets_its_close_without_a_return` (replaces the old
  test that enshrined Missing), :590 and :598 (wider answer disagreeing: partial window, different close). Fake
  `ProcessDateCAClient` (:100) filters on process_date like the endpoint. Contract (overlay):
  tests/test_forward_alpaca_contract.py:170 `test_corporate_actions_follow_every_page_and_filter_the_ex_dates` (real
  CorporateActionsClient, two faked HTTP pages: padded start/end sent, page_token followed, out-of-span ex_date dropped).

### S2: shadow get_orders no longer bounded from the first shadow record
- forward/orders_alpaca.py:507 `_orders`: the `all` query covers orders submitted from day - ORDERS_LOOKBACK_DAYS
  (:70, 3 days, the old margin) only; every pending id of the history that the open and `all` queries did not return
  is looked up by client order id (`_order_by_client_id`, :576; alpaca-py `TradingClient.get_order_by_client_id`,
  GET /v2/orders:by_client_order_id). HTTP 404 = not on the account (stays pending, as before); any other error
  raises ShadowError (nothing written). Protocol gains `get_order_by_client_id` (:106). The query size no longer
  grows with the ledger, and a pending id that never reached Alpaca (an "error" submit) cannot pin the bound.
- Tests: tests/test_forward_alpaca_orders.py:586 `test_orders_query_stays_bounded_after_more_than_a_page_of_orders`
  (130 sessions x 4 orders = 520 on a fake that honours `after` and the 500 cap, `WindowedClient` :156; the old code
  raised "full page"), :602 `test_failed_lookup_of_a_pending_order_raises_and_writes_nothing`, :531 now asserts the
  404 lookup. Contract: tests/test_forward_alpaca_contract.py:210 (real TradingClient, faked 404 -> None, 403 ->
  ShadowError, path and params checked).

### S3: an all-empty window is SourceUnavailable, not a missing day
- forward/sources_alpaca.py:489: after the raw fetch, no bar for any symbol on any date of the window raises
  SourceUnavailable("empty window ...") before the corporate-actions request and any per-symbol logic. A window with
  earlier sessions and none on t is still the confirmed missing day.
- Test: tests/test_forward_alpaca_sources.py:539 `test_all_empty_window_raises_unavailable_not_a_missing_day`;
  `test_missing_day_when_no_symbol_has_the_session_after_the_cutoff` still passes.

### NOTEs
- N1 fixed: forward/etf_bars.py:7-11 now defines ret as k x (rawclose(t) + D) / rawclose(prev) - 1 (registration
  section 6), no "all" fetch. Module docstrings of sources_alpaca.py (prev beyond the window, the span contract, the
  empty window) and orders_alpaca.py (bounded queries, lookups by id) updated. No other "all"-adjustment docstring in
  scope (test fixtures still carry unused "all" tables; the contract test checks that the SDK enum accepts "all").
- N8 resolved as a side effect (above). N2, N3, N4, N5, N6, N7, N9 listed, not changed (N9: the contract pagination
  test now covers the SDK paging of corporate actions).

### Test counts (12:06 PDT)
- Scoped: `uv run --frozen pytest -q -p no:cacheprovider tests/test_forward_etf_bars.py tests/test_forward_alpaca_*.py`
  123 passed, 1 skipped (contract module without alpaca-py).
- Overlay: `uv run --offline --frozen --with-requirements forward/requirements_broker.txt pytest -q -p no:cacheprovider
  tests/test_forward_alpaca_contract.py` 10 passed.
- Common: `uv run --frozen pytest -q -p no:cacheprovider tests/test_forward_*.py tests/test_mdio_*.py` 39 failed, 428
  passed, 2 skipped. 20 failures are in tests/test_forward_ibkr_* and 18 in tests/test_forward_f2_wave3.py (the other
  fixers' work in progress, their scopes). **One is caused by this fix:**
  tests/test_forward_f2_daily.py::test_ledger_byte_identical_with_shadow_on_and_off (F2Fixer2's scope, not edited):
  its own FakeTradingClient returns no orders and has no `get_order_by_client_id`, so the shadow's lookup of the
  first day's still-pending orders raises ShadowError (AttributeError inside). Fix in that fake (one method):
  `def get_order_by_client_id(self, client_id): raise type("NotFound", (Exception,), {"status_code": 404})(client_id)`.
- `sha256sum -c --quiet reports/stage_e22_f1_files.sha256`: OK. `data.holdout status`: unlocks_logged 0 at start and end (12:08).

### sha256 before (11:54) and after (12:06)
| file | before | after |
|---|---|---|
| forward/etf_bars.py | 6f7aa2d8bef1bc0a1411bacaa82a6f06b203fa1bb8d80c401cea9fad573dbe7e | 0a8ac1fad5e14586d517b4de44a981efdc394fa8b058dacaaeaf5864398e45f9 |
| forward/sources_alpaca.py | 8158ba158f92e2c2002c72ad24e475c318e871b42f8af4a409295b30107f66a0 | c51c7df2f5861c656ca67b833cc59d56b3af334614c5a80e293dd75be899c700 |
| forward/orders_alpaca.py | 7376e9f273062060732287941f208622c572ca053fe01e37e8f2b1963f49ed82 | 681a119b2770f9013510cd0546975f84662307c1645bd717e4eebe3e7df58c18 |
| forward/shadow_f2.json | c44924c6b70ec678b08bbf6a07a9cb594a2927c38c88ebbd853f9a15dd94d360 | unchanged |
| tests/test_forward_alpaca_contract.py | 3eda6c843ddb22fdefbdd4fbc39ec10391823b33dc0a8ae44ce61b8cc4412cd8 | b9a906c612dfd6e1406d972b2632e12063ddc9af99d77dc7df9aff5c109f576d |
| tests/test_forward_alpaca_orders.py | c2f29aa0bc5af1656ee233c2f026a229ba2abc069eb430bf6549b9c4a7381c94 | 2cb48d63dc4075d331d14d69475856e60d06044ad2416b8a1a420b5dde5becb6 |
| tests/test_forward_alpaca_sources.py | 602f862e3ae78362f9942886d6953ac07112b168b6552b0d62a52d631d4e68b6 | 676072599490fa0525833f17f04c11eb7e535d3e12284d25022c742d03e23e2b |
| tests/test_forward_etf_bars.py | 9785ed7b72a527780125068262912f9378f17d3df74f03de4afa7f57ef66bc16 | unchanged |

### Not verified (offline)
- That /v2/orders:by_client_order_id answers 404 for an unknown client order id (alpaca-py raises APIError with the
  HTTP status; the 404 is the expected REST answer, not checked against a live account).
- Whether /v1/corporate-actions caps the length of a process_date interval (no maximum is documented; a refusal would
  surface as SourceUnavailable, loud). The future `end` (N4) is unchanged and still to confirm on the first session.
- An action processed more than CA_MARGIN_DAYS (60) after its ex_date is not found by a span ending at that ex_date;
  the late-action path finds it once the last record is within 60 days of its process_date.
