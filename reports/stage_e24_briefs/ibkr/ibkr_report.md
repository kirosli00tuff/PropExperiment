# Stage E.24 Part B (B2-B4): IBKR adapter for E22-F1. IBKRCoder-OpusXHigh report

Times are PDT from `date`. Phase 1 (01:40-02:05) built against a mock gateway. A usage-limit
pause followed (02:05-06:12; not work). Phase 2 (06:12 on) aligned the code with
reports/stage_e24_briefs/facts/ibkr_facts.md. Then the corrections of reports/stage_e24_briefs/facts/ibkr_factcheck.md were applied (written 06:25; C1 and C3 affect the adapter, C2 and C4 only the facts file). Final checks ran at 06:28. No network was used, no
credentials, no .env read, no commits. The frozen E22-F1 files are unchanged (check at the end).

## Files (all new)

| File | sha256 (06:28:43 PDT) | Role |
|---|---|---|
| forward/ibkr_gateway.py | a767c24115097cc4ddcf15988875b69f6f6d161a3b0ffd2a142cc2d623081266 | Gateway Protocol (mirrors ib_async.IB), Vendor, errors (SourceUnavailable, SubscriptionNeeded, DayNotReady, ...), error classification, RetryPolicy, Pacer, GatewaySession (connect, reqMarketDataType(3), reconnect, retry, pacing, redaction), env var names, lazy `connect_live`/`live_vendor` |
| forward/sources_ibkr.py | 1a76ad8afb2d03cdc05b36e3f9c25530380c80b2ee4786af15633e8465802255 | IB_SPECS, cutoff and time-zone rule, ContractResolver, IBKRSettlementSource, warm-up assembly, CSV export |
| forward/orders_ibkr.py | bfba91fe4ba8e5d5f4bc56c6e7daa98aa380b706adc6f40327976921dc14b187 | Shadow route |
| forward/shadow_f1.json | b14f679248d1d912103faaeb336b6d0030c6071774c8921ef80346b83b24ec22 | Shadow config, `"enabled": false`, order types documented |
| forward/daily_f1.py | d9fac73ea0f4e78cad3952761f89b668232f41f536be6fb6e0c80d2e79513712 | Driver: `run`, `warmup`, `export-csv`, `probe`, `ready`, `env-status` |
| tests/_forward_ibkr_mock.py | a8f95def0376f951752f71c3dc95a9da4dce1818b0e92135e1df780dfd684ac8 | Mock gateway and fake ib_async objects (a helper; not collected) |
| tests/test_forward_ibkr_contracts.py | 2aafe6b2052422579739dfb2492368ac7f604d05f32bbb559538ae9baf143e76 | 11 test functions (13 cases) |
| tests/test_forward_ibkr_source.py | 61a12c1d72768008488cdbd5c094c064e820af19ee4d68ac19143e6f700baff8 | 23 functions (31 cases) |
| tests/test_forward_ibkr_warmup.py | 83efe750e182b0d161ef72e93435920e174d61533ef9ccfcfbd8e0cdc923b25f | 5 |
| tests/test_forward_ibkr_shadow.py | 00deae12c29d20fec7d00409b6e86f40e84758b58ed35e0618f59ca4158fc290 | 7 functions (9 cases) |
| tests/test_forward_ibkr_driver.py | aa9b55d7cce596ea8bd727890e86278dc41ebde7cc9b15c608f7a4e79f2b7446 | 13 |
| tests/test_forward_ibkr_vendor_contract.py | cb9ff5acdcdaeff6f05f325026a6b95f55ed49c3b9a0c0141ab75c64c83cb725 | 3 (importorskip ib_async) |

Line counts: ibkr_gateway 443, sources_ibkr 741, orders_ibkr 392, daily_f1 377 (all under 800). `ruff check` is clean on every new file.

Not touched: every file in reports/stage_e22_f1_files.sha256, pyproject.toml, uv.lock,
forward/requirements_broker.txt, the alpaca/f2/etf files, live/, ops/, sim/, rules/, screening/
and data/.

## Design notes per requirement

1. **Dependencies.** `import ib_async` appears only in `forward.ibkr_gateway._import_ib_async()`,
   which only `connect_live()` and `live_vendor()` call. `test_modules_import_and_run_without_ib_async`
   blocks the import: every module still imports, and `live_vendor()` raises IBKRConfigError
   naming the overlay command. The Protocol mirrors ib_async 2.1.0. Its source was read from the
   local uv cache (no network), and facts I9 confirm the signatures. The vendor contract test
   passes through `uv run --offline --frozen --with-requirements forward/requirements_broker.txt`.
   `connect_live()` sets `RaiseRequestErrors = True`, because ib_async's default ends a failed
   request silently with whatever bars had arrived (wrapper.py `error()` -> `_endReq(reqId)`),
   which would look like a partial history.
2. **Contract resolution** (`ContractResolver.resolve(instrument, contract_id)`).
   `forward.rolls.parse_contract` gives the year and month. The query is
   `Future(symbol, lastTradeDateOrContractMonth=YYYYMM, exchange, currency, includeExpired=True, tradingClass)`,
   sent through `reqContractDetails`. I9: an empty list means unknown and more than one means
   ambiguous. Zero matches raise ContractNotFound and two or more raise ContractResolutionError;
   there is never a guess. The single match must agree on secType FUT, symbol, currency,
   exchange, contractMonth, priceMagnifier, multiplier, conId > 0 and a parseable last trade
   date. `check_specs` checks at construction that each spec's implied runner multiplier
   (ib_multiplier / priceMagnifier x price_divisor) equals config_f1.json's. Foreign roots and
   off-cycle months are refused before any request. Micro Henry Hub resolves as symbol MHNG,
   trading class MNG (I7). Results are cached, with a conId map for the shadow route.
3. **Daily prices.** `IBKRSettlementSource.settlements(t)` returns `{inst: {cid: price}}`. For
   each instrument it delivers the rolls_f1.json reference contract, plus the previous contract
   from that contract's roll date through its anchor date (`contracts_for_day`). The frozen
   runner then has both legs on the switch date, and still has the held leg while a roll is
   deferred. The field is the close of the TRADES 1-day bar (useRTH False), converted to runner
   units: cents / 100 for MZC, MZS and MZL, exact through Decimal. Its label is
   `close_last_trade` (I6). The provenance JSONL (`--provenance`) records per contract: field,
   whatToShow, useRTH, bar size, bar date, IB close, divisor, runner price, conId, localSymbol and
   status/reason. It holds no account, host or port. Answers are memoised per date, so the
   driver's pre-check and the runner's call share one fetch.
4. **Missing vs unavailable** (`sources_ibkr.decide`). A contract with no bar for t counts as
   affirmatively missing only if (a) a later bar exists for it, (b) its last trade date is
   before t, or (c) a later bar exists on the same exchange (the t session is over). [Wave 3,
   S2: in (a) and (c) only a FINAL later bar counts, one whose own 18:00 CT cutoff has passed;
   the open session's partial bar dated t+1 confirms nothing.] Any other
   absence raises DayNotReady (a SourceUnavailable). Missing(reason) is returned only when no
   contract has a price for t and every absence is affirmative. Error handling (GatewaySession):
   - Retried up to 4 attempts, with backoff 15/30/60 s (cap 120; I5: no identical request within
     15 s) and a reconnect first when the socket is down: dropped sockets, ib_async's empty
     timeout result, 162 pacing violations and connectivity codes. [Wave 3, B1: also any
     historical answer that took the whole request timeout, whatever bars came with it; its
     bars are discarded, never used as a complete answer.] When retries run out:
     SourceUnavailable.
   - Factcheck C1: the adapter does not assume historical bars fail without a subscription.
     GatewaySession calls `reqMarketDataType(3)` (delayed) after every connect, before any
     historical request (default 3; `--market-data-type` overrides). A refusal (codes 354, 10089,
     10090, 10186, 10187, or any code, 162 included, whose text says "market data permission",
     "not subscribed" or "requires subscription") raises **SubscriptionNeeded**, a
     SourceUnavailable whose message begins "market data subscription needed (delayed type 3 was
     requested first)". It is never retried and never a Missing, and no record is written. The
     `probe` subcommand (writes nothing) shows what the login can read: bars, or the refusal code.
   - Stopped at once (SourceUnavailable): 321. [Wave 3, N1: as first written this was
     inaccurate. ib_async 2.1.0 lists 321 in warningCodes, so the request only timed out and
     was retried for about six minutes. GatewaySession now records 321 from errorEvent during
     a historical request and stops at once.]
   - Treated as "no bars": 162 "no data" and 166 "HMDS Expired Contract Violation" (I4). That is
     never a price and never a Missing by itself.
   - 200: not-found for contract details, fatal for bars.
   One failed contract fails the whole day, so no partial day is ever delivered. The driver also
   refuses to record a whole-day Missing without `--accept-missing-day` (exit 3), so a forgotten
   holiday declaration cannot become a permanent 0. Socket error texts are redacted (host, port,
   account and client id replaced) before any message is raised or printed.
5. **Warm-up.**
   - `warmup_windows` lists each contract that is the reference, or its roll partner, in
     [2024-03-01, the weekday before start], with the window [previous contract's roll date, own
     anchor date].
   - `fetch_warmup_prices` makes one paced request per window, with an explicit end time
     (23:59:59 Chicago in the API's UTC form `YYYYMMDD-hh:mm:ss`, I6; a bare date would be read
     in the local or TWS time zone). Contracts beyond the 2-year depth (I5) that are not found,
     have no data or return empty are noted and skipped. A not-found contract inside the depth
     is accepted only BEFORE the instrument's first resolved contract (a product listed later,
     e.g. the micro grains). A gap after it raises, an instrument with no resolved contract
     raises (wrong symbol mapping), and so does any connection failure. [Wave 3, S1: "a gap
     after it raises" held only for not-found contracts; a "no data" answer inside the depth
     was skipped. It now raises too, and so does a timed-out window (B1).]
   - `assemble_rows` applies rolls_f1.json as the runner does. The first reference is the
     declared contract on the instrument's first priced day. A due roll switches on the first
     day at or after the roll date where both legs are priced, and that row carries both prices
     (additive Panama back-adjustment works).
   - `write_warmup` refuses to overwrite, writes JSONL that `load_warmup` reads back identical
     (checked) and writes `<file>.sha256`.
   - `warmup_summary` gives per instrument: rows, first and last date, contracts, last
     reference, `open_roll`, back-adjusted points (it runs `back_adjusted_series`) and
     `live_at_start` (at least 256 differences, config `warmup_diffs`).
   - The `warmup` subcommand prints rows, first date, live_at_start and open_roll per instrument,
     and writes `<out>.summary.json` with the file sha256 and the runner's `history_fingerprint`.
   - **No real counts exist yet: this stage made no read.** In the mock run (MZC listed from
     2025-02-24; MNQH24/M24 beyond the depth), MZC starts 2025-02-24, MCL starts 2024-03-01, and
     all 12 instruments are live at start.
   - `export_csv` writes forward.sources' CSV with repr() prices (exact float round trip). It is
     idempotent, refuses a different duplicate and re-validates through CsvSettlementSource. The
     IBKR-driven ledger and the frozen `forward.runner` CLI run on the exported CSV give
     byte-identical ledgers (driver test).
6. **Settlement vs last trade (I6).** The TRADES daily close is the last traded price. Legacy
   docs say it "can be" the settlement, sometimes hours later or on Saturday. No API field
   carrying the settlement was found in the pages read (factcheck C3: the docs site was not
   crawled exhaustively). The adapter labels the field `close_last_trade` in the provenance, the
   CSV header comment and the docstrings. Nothing was registered and nothing in E22-F1 changed.
   The decision is the lead's and the user's (open question 1).
7. **Shadow route** (`orders_ibkr.ShadowRoute`; off by default, `forward/shadow_f1.json`
   `"enabled": false`).
   - It reads the E22-F1 ledger as text through `parse_chain`, so it is chain-verified and
     read-only. Targets come from the record's `orders`, else its `positions`, in the reference
     contract. Current holdings come from the paper account's positions by conId (falling back
     to details by conId). An unmappable position in a universe symbol raises; other symbols are
     noted as foreign.
   - `plan_orders` takes target minus current per contract, closing legs first, so a roll closes
     the old contract and opens the new one. Order type is MKT (default) or LMT at the record's
     settlement +- `limit_offset_ticks` ticks, rounded to the tick in IB units; TIF DAY or GTC;
     orderRef `E22F1-shadow:<date>`. Orders are placed once and never retried.
   - After up to `fill_wait_s`, one record is appended to a separate forward.ledger Ledger
     (schema `E22-F1-shadow/1`): targets, positions before, orders and status, fills (IB and
     runner price, time, commission, currency, contract, conId, execId), and late fills from
     reqExecutions by orderRef. The account id is never stored; only its variable name.
   - Guards: a disabled route refuses. A path equal to, symlinked to or hard-linked to the
     E22-F1 ledger is refused. A non-shadow record in the shadow file is refused. The account
     must start with DU and be in managedAccounts. Ports 4001 and 7496 (I1 live defaults) are
     refused. Open shadow orders block a new run. A date already in the shadow ledger returns the
     stored record without placing orders.
8. **Driver** (`python -m forward.daily_f1`).
   - `run`: source pre-check -> frozen `PaperRunner.run_date` (default target forward.strategy)
     -> optional CSV mirror -> optional shadow route. It needs exactly one of `--warmup FILE` or
     `--no-warmup`, because the warm-up is fingerprinted into every record. It connects read-only
     unless the shadow route is on.
   - Exit codes: 0 ok; 2 no record (not ready, unavailable, contract or convention error, no
     warm-up choice); 3 whole-day Missing without the flag; 4 record kept but the shadow route
     failed (any exception).
   - `warmup` refuses an existing output and a last day before its cutoff, both before
     connecting. `export-csv` exports a warm-up file. `ready` prints the latest CME trade date
     past its cutoff. `env-status` prints names with set/unset only.
9. **Tests.** All use hand-written fixtures and a mock gateway, with no network. Brief items:
   - contract resolution incl. expired and ambiguous: contracts file;
   - rolls across the anchor (both contracts 2026-12-10..12-18; the runner rolls MNQZ26 -> MNQH27
     on 12-10, as rolls_f1.json says): source file;
   - missing day: source and driver files;
   - reconnect (a drop then recovery, and exhaustion -> SourceUnavailable with no ledger file):
     source file;
   - partial history: source file;
   - warm-up round trip through load_warmup and back_adjusted_series, plus the CLI and the frozen
     strategy trading off the warm-up: warmup and driver files;
   - time zones (before the cutoff; a bar dated differently from the local date; DST end times):
     source file;
   - E22-F1 ledger byte-identical with the shadow route on and off, by bytes and sha256: shadow
     file (stub plan, 6 days with a roll) and driver file (frozen strategy, warm-up, 5 days).

## Environment variable NAMES (values never printed, logged or stored)

`IBKR_GATEWAY_HOST`, `IBKR_GATEWAY_PORT`, `IBKR_CLIENT_ID` (positive integer: I9 says clientId
0 merges manual TWS trading) are required for run and warmup. `IBKR_ACCOUNT_ID` is required only
when the shadow route is enabled. Example:
`uv run --env-file .env --with-requirements forward/requirements_broker.txt python -m forward.daily_f1 run ...`.
No code reads .env. `ConnectionParams.__repr__` hides the values, and error texts are redacted.

## Cutoff and time-zone rule

- The trade date is the CME trade date: the day the session closes. Daily bars come as
  yyyyMMdd, dated by the closing day (I6). The ThinkPad's local date is never used, and naive
  datetimes are refused.
- A bar for t is used only at or after **18:00 America/Chicago on t** (16:00 Vancouver). That is
  the 16:00 CT session end plus 2 h for the data delay and late updates. This is a declared
  choice, not a fact. Before the cutoff: DayNotReady, no record. `ready` and the default
  `--date` use `latest_ready_trade_date(now)`.
- Tested example: 2026-11-03 06:30 UTC is 22:30 on 11-02 in Vancouver and 00:30 on 11-03 in
  Chicago. The latest ready date is 11-02. The open session's partial bar dated 11-03 is ignored
  for 11-02, and 11-03 is not ready. At 17:30 CT on 11-02 the latest ready date is Friday 10-30.
- End times go to the API as `YYYYMMDD-hh:mm:ss` in UTC (I6). A date or a zone-less string is
  never passed (I9: zone-less strings use the TWS login time zone; ib_async reads bare dates in
  local time).
- Bar sanity: a datetime bar date, a weekend date or a duplicate date raises ConventionError,
  which would expose a different date convention.

## Facts each constant uses

| Constant | Value | Source |
|---|---|---|
| IB_SPECS exchange / symbol / trading class | I7 table; **MNG = symbol MHNG, trading class MNG** | facts I7 |
| IB_SPECS multipliers, priceMagnifier (x100 for MZC/MZS/MZL) | derived from config_f1.json, checked against reqContractDetails at runtime | I7: multipliers [unverified] on IBKR pages, so read at runtime as I7 advises |
| includeExpired=True; EXPIRED_DEPTH_DAYS 730 | 2 years after expiry | facts I5 |
| WHAT_TO_SHOW TRADES; FIELD_LABEL close_last_trade | last traded price, not guaranteed settlement | facts I6 |
| USE_RTH False; bar date = session closing day | | facts I6, "What this means" 4 |
| End-time format YYYYMMDD-hh:mm:ss (UTC) | | facts I6 (historical date format page), I9 |
| DEFAULT_MARKET_DATA_TYPE 3 before historical requests; SubscriptionNeeded on refusal | | factcheck C1 |
| 162 / 166 / 200 / 354 handled as data-unavailable; 10089, 10186, 10187 as no subscription | | facts I4, "What this means" 6 |
| PACING_S 1.0; backoff base 15 s | about 1 request/s; no identical request within 15 s | facts I5, "What this means" 6 |
| LIVE_PORTS {4001, 7496} | live defaults (paper 4002, 7497) | facts I1 |
| clientId > 0 | | facts I9 |
| PAPER_ACCOUNT_PREFIX "DU" | | **[unverified]**: not in the facts file |
| CUTOFF_CT 18:00 CT | | declared choice |
| CONNECTIVITY_CODES 502, 504, 1100, 1300, 2110; 321 | | TWS API list from memory, **[unverified]** (I9 confirms 1100 triggers the Watchdog) |

## Test output (verbatim)

`uv run pytest -q -p no:cacheprovider tests/test_forward_*.py` (06:28 PDT; log
reports/stage_e24_briefs/ibkr/pytest_forward.out):

```
........................................................................ [ 96%]
.............                                                            [100%]
373 passed, 2 skipped in 22.97s
```

The 2 skips are `tests/test_forward_ibkr_vendor_contract.py:14: could not import 'ib_async'`
and `tests/test_forward_alpaca_contract.py:16: could not import 'alpaca'`. The vendor libraries
are not in the project environment, by design.

`uv run pytest -q -p no:cacheprovider tests/test_forward_ibkr_*.py`: `69 passed, 1 skipped in 8.09s`.

`uv run --offline --frozen --with-requirements forward/requirements_broker.txt pytest -q -p no:cacheprovider tests/test_forward_ibkr_vendor_contract.py`
(log pytest_vendor.out): `3 passed in 0.19s`.

`sha256sum -c --quiet reports/stage_e22_f1_files.sha256`: no output, exit 0.

The case AlpacaCoder saw failing (a "2027" contract-month parametrize case in
test_forward_ibkr_contracts.py) belonged to an intermediate version. It was removed at about
06:12, and the full run above is green.

## Operational notes for the user checklist (Part D, lead's call)

- Whether historical bars come without a Level 1 subscription is open (factcheck C1: I4
  overstated). The first connection session should run `python -m forward.daily_f1 probe`
  (delayed type 3 by default) and record the outcome. Bars mean the warm-up can run. A
  SubscriptionNeeded (354/10089/10186/10187 or a 162 permission text) means a subscription is
  needed, per I8 on a funded IBKR Pro account, with paper seeing data only through sharing.
  Until then every run and warm-up stops with no record, which is safe.
- IB Gateway "Read-Only API" is on by default and blocks API orders (I1). That is fine for the
  source. The shadow route needs it off on the paper login. Paper port is 4002 (I1).
- ib_async has no automatic reconnect (I9). The adapter reconnects within one run. Gateway
  restarts (IBC daily restart, weekly re-authentication after Sunday 01:00 ET) are outside it:
  a run during a restart ends in exit 2 and is retried later.
- Schedule `run` after 16:00 PT (the cutoff) and outside the AiTrader 15:30-16:00 PT window,
  e.g. 16:15 PT on weekdays.

## Open questions for the lead

1. **Settlement (requirement 6, B2).** E22-F1 section 6 asks for daily settlement prices. IB's
   close is the last trade (I6). The two options, for the user: (a) a pre-clock amendment
   E22-F1b (N + 1) that defines the price as IB's last-trade close; (b) a second source for
   settlements only, with IBKR used for orders.
2. **Cutoff vs settlement timing.** Per I6 the close may be replaced by the settlement hours
   later. A later cutoff (e.g. 08:00 CT on the next weekday) would raise the chance that the
   close is the settlement, but never guarantee it, and it delays each record by a night. The
   declared 18:00 CT is a one-constant change if the lead prefers otherwise. Because values can
   change between requests, re-running a recorded date in a later process can raise the frozen
   runner's LedgerConflictError. That is safe (nothing is written), but the operator should not
   re-run recorded dates.
3. **Thin contracts.** TRADES bars exist only on days with trades. For thin contracts (micro
   grains, deferred months), a day without trades is "affirmatively missing" once a later bar
   exists, so the runner flags `missing:I`, and a roll can be deferred when the new contract has
   not traded. A settlement source would not have this gap.
4. **Warm-up not-found rule.** Inside the 2-year depth, not-found contracts are accepted only
   before an instrument's first resolved contract. (The micro grains launched in early 2025 is
   from memory, [unverified].) Please confirm the rule.
5. **Unverified constants:** paper prefix "DU", connectivity codes, the multipliers/magnifiers
   (checked at runtime, so a wrong value stops the run rather than mis-pricing it).
6. **Holiday declarations** stay manual (`--closed`), as in the frozen runner. Exit 3 protects
   against a forgotten one but does not check the exchange calendar.

## Not finished

- No independent review (B5, AdapterReviewer-FableXHigh) has run. It belongs to the lead.
- Not testable here: real-gateway behaviour (actual multipliers, priceMagnifier and localSymbol
  of the 12 micros, I7 [unverified]; whether delayed type 3 serves historical daily bars; IBKR's
  exact error texts). The runtime checks stop the run on any mismatch, and the `probe`
  subcommand is the first step of the connection session.
- Nothing else from brief B2-B4 is unfinished.

---

## Wave 3 fixes (IBKRFixer-OpusXHigh, 2026-10-18 11:54 to 12:13 PDT)

Brief: reports/stage_e24_briefs/brief_wave3_fixers.md (Common, IBKRFixer). Inputs: review_rulings.md
(B5 section) and ibkr/adapter_review.md (1 B, 5 SF, 8 N). Test first throughout: the new tests
were written and run against the old code (27 failed, 70 passed, 1 skipped; the 2 new tests
that passed then are guards on behaviour that must not change), then the code was fixed. No
network, no gateway, no .env, no market data. Times are from `date`.

### Items

| Item | Fix (file:line after the fix) | Tests |
|---|---|---|
| B1 timeout or partial answer accepted | `daily_bars` treats any historical answer that took the whole request timeout (minus `TIMEOUT_SLACK_S` 0.5 s) as `RequestTimedOut`, whatever bars came with it; the bars are discarded, retried, then SourceUnavailable (forward/ibkr_gateway.py:39, 106, 451-500). `GatewaySession` takes a `clock` (the driver passes `Deps.clock`, forward/daily_f1.py:125) and refuses a gateway with `RaiseRequestErrors` not True (ibkr_gateway.py:350); `RetryPolicy` refuses `request_timeout_s` <= 0.5 (ibkr_gateway.py:264). Warm-up: a timed-out window inside the depth raises; beyond the depth it is noted and skipped as empty answers were (forward/sources_ibkr.py:702). Mock fault mode `stall` (tests/_forward_ibkr_mock.py:324, 439): the mock clock advances by the timeout and a cut list (first N bars, or the bars before a date) comes back with no error. | tests/test_forward_ibkr_source.py:155 (daily path, 3 cases: cleared list, 1 bar, all bars before t on MCL/NYMEX; SourceUnavailable "timed out", no ledger file), :171 (one stall retried, full answer used), :191 (RaiseRequestErrors); tests/test_forward_ibkr_warmup.py:171 (warm-up raises); tests/test_forward_ibkr_driver.py:384 (warmup subcommand exits 2, nothing written) |
| S1 no-data inside the depth skipped | `_fetch_contract` re-raises NoHistoricalData unless the contract is beyond the depth (sources_ibkr.py:697). `stale_open_rolls` (sources_ibkr.py:741; tolerance `OPEN_ROLL_STALE_WEEKDAYS` = 3, line 84) and `cmd_warmup` now builds the summary first and refuses (exit 2, no file, no summary, no CSV) when an instrument has an open roll and its last priced date is more than 3 weekdays before the last warm-up day (daily_f1.py:330). Report sentence corrected in section 5 above. | test_forward_ibkr_warmup.py:182 (MNQU25 no data raises), :192 (MNQH24 beyond the depth still noted and skipped), :204 (stuck MNQU26 -> Z26 roll flagged, a roll deferred at the end not flagged); test_forward_ibkr_driver.py:398 (warmup exits 2, nothing written) |
| S2 confirmation by the open session's partial bar | `_observe` counts a later bar only once its own cutoff has passed: `is_ready(d, now)` (sources_ibkr.py:472), for rules (a) and (c). The not-ready test no longer edits the mock: it runs in the production state at 19:00 CT on t with the partial t+1 bar served (asserted in the test) and expects DayNotReady, then expects the absence affirmed one evening later. | test_forward_ibkr_source.py:122 (MGC/COMEX and MZC/CBOT; replaces the old test that stripped bars after t), :145 (a Friday absence waits for Monday's final bar) |
| S3 holiday dates (ruling) | `run` refuses (exit 2, before connecting) without `--date` unless `--holidays FILE` is given; then it runs the latest ready date (daily_f1.py:154). A date the file lists exits 2 ("declare it closed"); the listed dates strictly inside the gap since the ledger's last record are passed to the runner as declared closed (daily_f1.py:182). File format: one YYYY-MM-DD per line, '#' comments, text after the date ignored; a weekend date, a non-date or an empty file is refused (daily_f1.py:134). Exchange-gap guard: when every contract of one gap group is affirmed missing while another group is priced, exit 5 unless `--accept-exchange-gap` (daily_f1.py:239; `exchange_gaps` sources_ibkr.py:529, the source keeps decide()'s log per date, line 444). | test_forward_ibkr_driver.py:324, :331 (holiday on its own evening and as --date: exit 2; the next day records with declared_closed ["2026-11-26"]), :348, :355 (COMEX and CBOT grains: exit 5, then 0 with the flag and missing:I flags), :369 (one NYMEX contract missing is not a gap) |
| S4 warm-up vs live price definition | Decision stays with the user (return section 7, decision 1). Code: `probe --log FILE` appends every bar of both probe requests with fetch time (UTC), `age_h` (hours after the bar date's 18:00 CT cutoff; negative for the open session's bar), request end, field label, contract and conId, and prints a "changed" line for any bar whose close differs from its first logged fetch (daily_f1.py:395, 440, 458). Run it at 18:00 CT, 08:00 CT next day and a week later to see whether IB replaces the close. | test_forward_ibkr_driver.py:414 (same bar at ages 1.0 h and 62.0 h, close changed by 1.0, "changed" printed, no host, port or account in the log) |
| S5 shadow late fills lost | Every earlier shadow order that its record left short of its quantity is reconciled once: shares found in reqExecutions go to `late_fills` (now with `order_ref`); shares still unaccounted that `reqCompletedOrders(apiOnly=True)` shows filled go to `late_fills_unretained` (quantity, status, `source: completed_order`; ib_async 2.1.0's completed orders carry no price or commission, so `avg_fill_price_ib` is set only when non-zero); a completed order with nothing more filled goes to `closed_orders`; an order with no trace goes to `unresolved_orders` (forward/orders_ibkr.py:29, 418, 472). Orders and fills now carry `order_ref` and `con_id` (orders_ibkr.py:371, 393). `reqCompletedOrders` added to the Gateway Protocol (ibkr_gateway.py:158). Mock: `reqExecutions` returns the current Chicago date's executions only; `reqCompletedOrders` returns finished orders shaped as ib_async 2.1.0 builds them (status only, `order.filledQuantity`, no fills) (_forward_ibkr_mock.py:504). shadow_f1.json: fill_wait_s doc states the retention limit and the fallback. | test_forward_ibkr_shadow.py:224 (fill at 19:00 CT, next run a day later: recovered from completed orders, listed once), :240 (no trace: unresolved, listed once), :254 (late fills within retention carry order_ref) |
| N1 321 | `GatewaySession` subscribes to `errorEvent` and keeps 321 seen during a historical request; `daily_bars` raises `RequestRejected` (FATAL), so no retries (ibkr_gateway.py:110, 370, 487). Mock: `warn_321`. Report line corrected in section 4 above. | test_forward_ibkr_source.py:180 |
| N2 endDateTime form | `probe` makes a second request with the explicit end (`ib_end_of_day`) and checks it ends at the open-end answer's last bar on or before the date with equal closes (`explicit_end=consistent`, else exit 2) (daily_f1.py:480). The end string form itself is unchanged. | test_forward_ibkr_driver.py:414 |
| N3 RunnerError traceback | `cmd_run` maps RunnerError (e.g. an undeclared gap) to exit 2 with "no record written" (daily_f1.py:245). The catch-up loop is NOT done (see below). | test_forward_ibkr_driver.py:376 |
| N4 connect before guards | Prefix and port checked before `ensure_connected`; managed accounts after (orders_ibkr.py:196, 205). | test_forward_ibkr_shadow.py:269 |
| N5 grains queued to 19:00 CT | shadow_f1.json `order_type` doc. | (doc) |
| N6 depth from the anchor | `fetch_warmup_prices` docstring states it (sources_ibkr.py:642). | (doc) |
| N7 grain unit check | `bar_prices` refuses an MZC/MZS/MZL close below 100/300/10 cents (`MIN_IB_CLOSE_CENTS`, sources_ibkr.py:81, 387). The review's "> 50" would refuse MZL (soybean oil is quoted near 45 cents/lb; the mock uses 45.12). | test_forward_ibkr_source.py:201 |
| N8 holidays and rule (c) | No code; covered by the S3 grains group below. | (S3 tests) |

### Points for the lead (choices made inside the rulings; each is one place to change)

1. B1, vendor fact: the review quotes ib_async 2.1.0's timeout path as returning the bars
   received so far. The cached source (ib.py `reqHistoricalDataAsync`) calls `bars.clear()`
   after `cancelHistoricalData`, so 2.1.0 returns an EMPTY list on a timeout, which the old code
   already retried as EmptyResponse. The fix was made as ruled anyway. It does not depend on
   the vendor version, and `test_vendor_facts_the_wave3_fixes_lean_on` (vendor contract test,
   line 55) pins the 2.1.0 facts used. Mechanism: elapsed time, not the review's
   `wait_for(reqHistoricalDataAsync(timeout=0))`. That form cancels the coroutine without
   `cancelHistoricalData`, which would leave the HMDS request open at IB, and it would need an
   async method in the Protocol.
2. S3 groups: the exchange-gap guard groups by IB exchange as ruled, but the CBOT grains form a
   group of their own (`GAP_GROUP_OVERRIDES`, sources_ibkr.py:88). The S3 failure scenario is a
   holiday on which the grains are missing while the CBOT yields trade. A pure by-exchange guard
   cannot see that case. The grouping only adds refusals: every by-exchange gap is still caught.
   Setting the constant to `{}` restores the literal ruling.
3. S3 holiday file: listed holidays inside the gap are declared closed automatically. Without
   that, the run after each holiday would fail the frozen gap check. The new exit code is 5.
4. S5 record layout: shadow records gain keys (`order_ref` and `con_id` on orders and fills;
   `late_fills_unretained`, `closed_orders`, `unresolved_orders`). The schema label stays
   `E22-F1-shadow/1` because no shadow ledger exists yet. Bump it if preferred.

### Not fixed, with the reason

- N3 catch-up loop: `run` does not iterate from the ledger's last date to the latest ready
  date. It decides how many records one unattended call writes, so it is a design change, not
  a cheap one. It now matters more because of S2: a genuinely missing contract on t is
  confirmed only on t+1 after 18:00 CT. A `--holidays` run on t+1 defaults to t+1, hits the gap
  check and exits 2 (no traceback any more) until `--date t` is run. Listed for the lead.
- N1, the review's alternative of catching 321 per reqId: done more simply (any 321 during the
  one outstanding historical request). The adapter never runs two historical requests at once.
- N2: the aware-datetime alternative for `endDateTime` was not adopted. `probe` confirms the
  string form at the first connection instead.
- S4 decision itself: the user's (not code).
- Unverified, as before: IB's executions retention boundary (modelled as the Chicago date), the
  retention of completed orders, and IB's dating of holiday sessions.

### Test output

- `uv run --frozen pytest -q -p no:cacheprovider tests/test_forward_ibkr_*.py`: before 69
  passed, 1 skipped; RED 27 failed, 70 passed, 1 skipped; after 97 passed, 1 skipped (6.1 s).
- `uv run --offline --frozen --with-requirements forward/requirements_broker.txt pytest -q -p
  no:cacheprovider tests/test_forward_ibkr_vendor_contract.py`: 4 passed (was 3).
- Brief command `uv run --frozen pytest -q -p no:cacheprovider tests/test_forward_*.py
  tests/test_mdio_*.py` at 12:11 PDT: 457 passed, 2 skipped, 10 failed. All 10 failures are in
  tests/test_forward_f2_*.py, F2Fixer2's scope, which was being fixed in parallel. No failure
  is in an IBKR or mdio file. Baseline at 11:59 PDT: 410 passed, 2 skipped.
- `ruff check` and `ruff format --check` on the 11 files: clean. `sha256sum -c --quiet
  reports/stage_e22_f1_files.sha256`: OK (12:11 and at the end). Holdout `unlocks_logged`: 0.

### sha256 before (11:54 PDT) and after

| File | Before | After |
|---|---|---|
| forward/ibkr_gateway.py | a767c24115097cc4ddcf15988875b69f6f6d161a3b0ffd2a142cc2d623081266 | 32b944600adb87f155882b00df3829fa933d1d009428fd56eaa6918ca11a5a16 |
| forward/sources_ibkr.py | 1a76ad8afb2d03cdc05b36e3f9c25530380c80b2ee4786af15633e8465802255 | 8780259bcfdeb0efd60b2f681351bdebf4497b1515ea705102364c9c1b03c5c7 |
| forward/orders_ibkr.py | bfba91fe4ba8e5d5f4bc56c6e7daa98aa380b706adc6f40327976921dc14b187 | ec0ede0c4e83b4eedee17c60d312711a5e65aea6bab619d14c65e2fb873cfb98 |
| forward/daily_f1.py | d9fac73ea0f4e78cad3952761f89b668232f41f536be6fb6e0c80d2e79513712 | e1344ebbbef145f254ff9f7d2544b76f2b4b981f2e400a01fb79bbbe3daede12 |
| forward/shadow_f1.json | b14f679248d1d912103faaeb336b6d0030c6071774c8921ef80346b83b24ec22 | eb37144c408c56600f19718120635b53706da116392fe61109ff7b1dc4bb93c0 |
| tests/_forward_ibkr_mock.py | a8f95def0376f951752f71c3dc95a9da4dce1818b0e92135e1df780dfd684ac8 | 27be5c9ec2c39c96a80caa5cfe0cb1b6e632c43626b241d2f2a337eb763e1fe3 |
| tests/test_forward_ibkr_contracts.py | 2aafe6b2052422579739dfb2492368ac7f604d05f32bbb559538ae9baf143e76 | unchanged |
| tests/test_forward_ibkr_driver.py | aa9b55d7cce596ea8bd727890e86278dc41ebde7cc9b15c608f7a4e79f2b7446 | 7a073535dfbd67672f6f3ebfc87ac41705c8d79c6deab36d4cbba2ae348159ce |
| tests/test_forward_ibkr_shadow.py | 00deae12c29d20fec7d00409b6e86f40e84758b58ed35e0618f59ca4158fc290 | 9226a72300913a0173283cc422e220972bbb943ca3aa6eeac89ceab9ca472925 |
| tests/test_forward_ibkr_source.py | 61a12c1d72768008488cdbd5c094c064e820af19ee4d68ac19143e6f700baff8 | 12dd35861952a21133f7c9f9f88936e1d3a8f3d42632ed768435f93461b3cbb5 |
| tests/test_forward_ibkr_vendor_contract.py | cb9ff5acdcdaeff6f05f325026a6b95f55ed49c3b9a0c0141ab75c64c83cb725 | bb8b91fcf6c2fec8c05d00d01ee2bdc541c0e86e9be4224947e6f36cb35528b0 |
| tests/test_forward_ibkr_warmup.py | 83efe750e182b0d161ef72e93435920e174d61533ef9ccfcfbd8e0cdc923b25f | 8456e2293d5f2aa7065e81a52f1d42ccad4072589ce5e660ea81f2742eb377b0 |
| reports/stage_e24_briefs/ibkr/ibkr_report.md | 32af27295f251c7fa576d7dc3a1e936244486d2b2c61ac014a6df0ef422cd536 | this file (sections 4 and 5 corrected in place, this section appended) |
