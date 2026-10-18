# C4a review: Alpaca adapter (forward/etf_bars.py, sources_alpaca.py, orders_alpaca.py, shadow_f2.json)

Reviewer: AlpacaReviewer-FableXHigh (worker-xhigh, fable; independent: wrote none of the files). Stage E.24.
Written 2026-10-18, 11:18 to 11:37 PDT (times from `date`). Brief: reports/stage_e24_briefs/brief_reviews.md,
Common rules + C4a, with the lead's updates (returns from RAW bars plus /v1/corporate-actions; the "all" adjustment
is not used).

Inputs read: brief_C3a_alpaca.md; reports/stage_e24_prereg_F2.md sections 5 to 7; facts alpaca_facts.md (A3, A4,
A9, A10, "What this means"), alpaca_factcheck.md (corrections, supplementary, unchecked), fees_facts.md (headings
only; the adapter computes no fees); the coder's report alpaca_report.md; the saved vendor reference
pages/alpaca/ref_us_corporateactions-1.md (field names, process_date sorting, split and capital-gains examples);
alpaca-py 0.44.0 source from the local uv cache (common/rest.py `_get_marketdata`, data/historical/
corporate_actions.py, data/requests.py `CorporateActionsRequest`, common/exceptions.py `APIError`, common/enums.py
`BaseURL`); forward/ledger.py (frozen, read only), forward/runner_f2.py and forward/daily_f2.py (read only, for the
consumer's side of the interface; they belong to C4b). No network, no endpoint, no keys, no .env.

Files reviewed (sha256, first 16 hex):

| file | sha256 |
|---|---|
| forward/etf_bars.py | 6f7aa2d8bef1bc0a |
| forward/sources_alpaca.py | 8158ba158f92e2c2 |
| forward/orders_alpaca.py | 7376e9f273062060 |
| forward/shadow_f2.json | c44924c6b70ec678 |
| tests/test_forward_etf_bars.py | 9785ed7b72a52778 |
| tests/test_forward_alpaca_sources.py | 602f862e3ae78362 |
| tests/test_forward_alpaca_orders.py | c2f29aa0bc5af165 |
| tests/test_forward_alpaca_contract.py | 3eda6c843ddb22fd |

Invariants: `sha256sum -c --quiet reports/stage_e22_f1_files.sha256` OK at start and end; `data.holdout status`
unlocks_logged 0 at start and end; no file under review modified; no commit.

Tests run (read-only):
- `uv run pytest -q -p no:cacheprovider tests/test_forward_etf_bars.py tests/test_forward_alpaca_sources.py
  tests/test_forward_alpaca_orders.py tests/test_forward_alpaca_contract.py`: 116 passed, 1 skipped (the contract
  module skips without alpaca-py), 0.29 s.
- `uv run --offline --frozen --with-requirements forward/requirements_broker.txt pytest -q -p no:cacheprovider
  tests/test_forward_alpaca_contract.py`: 8 passed (alpaca-py 0.44.0 from the uv cache; `--offline` so no network).
- A scratch demonstration of finding S2 (not part of the suite), in the scratchpad:
  /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/c2dca792-060d-4694-91ef-4a6f3f808f1d/scratchpad/demo_orders_truncation.py
  prints `orders on the account since the first record: 500` then `run() raised ShadowError: get_orders(all)
  returned a full page; possibly truncated`.

## 1. Checklist (the lead's list and the brief's hunt list)

Each line: what was checked, where, result.

1. Return formula. `total_return` (sources_alpaca.py:346-357) computes `k x (raw_t + D) / raw_prev - 1`, the
   registration's section 6 formula, with `k` the product of split ratios and `D` the sum of distribution amounts of
   the actions passed in. `fetch_day` passes `ca.between(s, prev, trade_date)` (line 494), i.e. ex_date in
   (prev, t]. The "all" adjustment is never requested: every bars request carries `adjustment="raw"` (lines 468,
   499; test `test_daily_fetch_requests_raw_bars_and_corporate_actions_never_all`, sources tests:274). PASS.
2. Split. `parse_corporate_actions` (725-767) sets `ratio = new_rate / old_rate` (new shares per old share). The
   saved reference's forward_split example has `new_rate: 2, old_rate: 1` (ref lines 575-576), so a 2-for-1 gives
   k = 2 and k x (P/2) / P - 1 = 0. `old_rate` 0, negative or non-finite rates raise SourceUnavailable (682-693,
   746-749). PASS.
3. Reverse split. Same path; the UNG-style 1-for-4 test (sources tests:298) gives k = 0.25 and +2% rather than
   +308%. PASS.
4. Cash dividend and special dividend. `_distribution_amount` (701-710) takes `rate`; the `special` flag is not
   consulted, so special dividends are included as section 6 requires. A non-USD `currency` raises
   SourceUnavailable (695-698); an absent `currency` is accepted as USD. PASS.
5. Capital gains. `long_term_rate + short_term_rate`, each leg only when present; no leg at all raises
   SourceUnavailable (704-710). Matches the reference ("At least one of the two rates is always present", ref line
   210) and the 0.44.0 typed set would drop the type (contract test `test_the_typed_sdk_set_would_drop_capital_gains`
   shows `CorporateActionsSet(raw).data == {}`), which is why the client runs with `raw_data=True`
   (make_corporate_actions_client, 227-238). PASS.
6. Same-day split and dividend. `k x (raw_t + D)`: D is treated as per post-split share and scaled by k together with
   the post-split close, which is the registration's wording ("per share after that day's split"). Test
   `test_split_and_dividend_on_the_same_day` (321): 2 x (50.5 + 0.10) / 100 - 1. PASS (see N7 for the multi-action
   gap case).
7. BIL's monthly dividend. Booked on its ex_date only (`between` is strict on both ends: `after < ex_date <=
   through`, line 334); test 396 shows MON counted, WED not. PASS.
8. Empty or malformed corporate-actions responses. `{}` and `{"corporate_actions": {}}` parse to no actions and the
   return is the raw return (test 416); a non-mapping, a type whose value is not a list, a missing or bad ex_date,
   a bad rate or old_rate raise SourceUnavailable (727-731, 735-736, 713-722, 682-693). The raw shape the parser
   expects, `{type_plural: [record, ...]}`, is what alpaca-py 0.44.0 returns in raw mode: `CorporateActionsClient.
   get_corporate_actions` returns `_get_marketdata(...)`, which merges every page's `response["corporate_actions"]`
   sub-dict by key (rest.py:368-408, corporate_actions.py:66-76). PASS.
9. Pagination. Bars: no `limit` on the request (251-272; contract test asserts `"limit" not in fields`), so the SDK
   follows `next_page_token` to the end; a failure in the middle propagates out of `get_stock_bars`, and `_call`
   either retries the whole request or raises SourceUnavailable, never using a partial page (tests 664, 672).
   Corporate actions: `limit=None` (241-248) means `_get_marketdata` runs with `limit` unset and `page_size=1000`,
   paging until `next_page_token` is null (rest.py:377-407); the class default 1000 would have capped the answer
   (contract test `test_corporate_actions_request_and_client_match_the_sdk`). PASS (N9: the CA paging itself has no
   unit test; the SDK does it).
10. process_date filter. The endpoint's start/end is a process_date interval (ref lines 66, 109: "sorted by their
    `process_date`"). The daily request spans process dates [t - 21 - 60, t + 60] (469-472, `CA_MARGIN_DAYS` 150),
    the warm-up [first - 60, last + 60] (526-528), and ex_date is filtered locally in (prev, t] (`between`,
    331-336). A dividend listed by a process_date 15 days after its ex_date is found (test 371, whose fake filters on
    process_date). PASS (N2: the default fake filters on ex_date; N4: a future `end`).
11. The window (prev, t]. `between` excludes ex_date == prev (already inside prev's return) and includes ex_date ==
    t; `prev` is the symbol's latest bar before t in the same response restricted to dates <= t (483-485). An
    ex_date inside a bar gap is applied to the return spanning the gap (test 407). PASS (S1 for gaps longer than the
    request window).
12. Session dates in America/New_York. `session_date` converts the aware bar timestamp to New York and takes the
    date (162-164); a naive timestamp or clock is refused (156-159, 571-572). Tests: a 05:00Z stamp whose Vancouver
    date is the day before (201), 22:30 PT already the next New York date (233), and a real alpaca-py `BarSet` built
    from `"2026-11-04T05:00:00Z"` (contract test). PASS.
13. Cutoff. `bar_cutoff(t)` = t 16:00 New York + 2 h (86, 91, 167-169); before it `fetch_day` raises `NotReady`
    without sending a request (461-465; test 219). The request `end` is `min(t 23:59:59 NY, now - 16 min)` (467),
    so SIP history is requested at least 15 minutes old (A2). The registration names no numeric cutoff; the 2 h
    value is the adapter's declared constant and the coder's report states it. PASS.
14. Missing vs SourceUnavailable. A symbol lacking t's bar is re-requested alone; if the single-symbol answer has
    the bar the multi-symbol response was partial and SourceUnavailable is raised, otherwise the symbol is Missing
    (498-508; tests 471, 487). Weekends and declared closed dates raise `NotASession` (ValueError), never Missing
    (574-578). HTTP 429/500/502/503/504 and OSError (requests' ConnectionError and Timeout are OSErrors) are retried
    up to 5 attempts with backoff 2, 4, 8, 16 s capped at 60 s, honouring Retry-After and X-RateLimit-Reset
    (282-312, 589-604); other errors (403 feed refusal, 422, a malformed body) raise SourceUnavailable at once.
    alpaca-py's `APIError` exposes `status_code` and `response` as properties (exceptions.py:25-39), which `_status`
    and `_reset_wait` read. Requests are paced to 200/min (100-101, 580-587). PASS (S3 for the empty-window case).
15. Paper-only enforcement. `make_trading_client` refuses `paper is not True` and a non-paper `url_override`, builds
    `TradingClient(..., paper=True)` and then `assert_paper` checks `client._base_url` (string or `BaseURL` enum)
    against https://paper-api.alpaca.markets (orders_alpaca.py:308-335; SDK rest.py:65, enums.py:9-10). `run()`
    also asserts it on an injected client (445). The contract test refuses a real `TradingClient(paper=False)`.
    PASS.
16. Fractional longs, whole-share shorts. `_desired` (192-198): shorts always whole; longs fractional (9 decimals,
    A5) in `fractional_day`, whole in `moc_whole`; a non-fractionable asset is rounded. Fractional sells are only
    ever sells of a long (FR line 84, fact check correction 1). The `moc_whole` default rounds all targets to whole
    shares; disclosed in the report and accepted by the lead (report section 6, Q3). PASS.
17. Crossing split. `_legs` (201-219) emits sell-to-close then whole-share sell-to-open, or buy-to-close then buy;
    tests 253, 266, 274 (a short that rounds to zero only closes). PASS (N5 on the paper account's likely rejection
    of the second leg).
18. Shadow route never touches the E22-F2 ledger. `check_ledger_paths` (297-305) refuses the F2 path by resolved
    path, abspath and samefile, at construction (417) and at every run (430); the route writes only through
    `Ledger(self.config.ledger_path)` (432, 484); test 421 asserts the F2 file's sha256 is unchanged. shadow_f2.json
    ships `"enabled": false` and a non-F2 ledger path (test 182). `f2_fields` (154-166) reads only date, targets
    and positions, the names runner_f2.py:216-218 uses. PASS.
19. Keys never logged. Only the names `ALPACA_PAPER_KEY_ID` and `ALPACA_PAPER_SECRET_KEY` appear; values are read in
    `paper_credentials` (205-214) and passed to the SDK constructors; error messages name the variable, never the
    value (test 763). `_describe` (both modules) puts `str(exc)` of the SDK exception in messages: alpaca-py's
    `APIError` text is the HTTP body, which carries no credentials (exceptions.py:10-23). PASS.
20. Lazy imports. All `alpaca` imports sit inside the factories (217-272; orders 320-369); test 774 blocks the
    package in a subprocess and the modules import and fail with the install hint. PASS.
21. Mock fidelity vs alpaca-py 0.44.0. `FakeBar(timestamp, close)` and `FakeBarSet(data)` match `Bar` and
    `BarSet.data`; `FakeCAClient` returns the raw `{type_plural: [...]}` shape (item 8); `FakeAPIError.status_code`
    matches the `APIError` property; `FakeTradingClient._base_url` is a plain string where the SDK holds a `BaseURL`
    enum, and `_url` handles both (308-311); the contract tests exercise the real request classes, `BarSet`,
    `StockHistoricalDataClient`, `CorporateActionsClient(raw_data=True)` and `TradingClient`. PASS, with N2 (the CA
    fake's filter field).
22. Warm-up. One raw fetch and one corporate-actions fetch from 2024-03-01 to start - 1 (511-552), the same
    formula per row, the first row of each symbol with `ret None`, gaps confirmed by a single-symbol request,
    sha256 of the canonical JSONL, `write_warmup` refuses to overwrite and re-checks the digest (391-397).
    PASS.
23. Report accuracy. The report's claims (two requests per day, raw only, process_date window, 5 attempts, the
    capital-gains legs, the fact-check corrections applied, test list) match the code and the tests. The test
    counts it quotes could not be compared line by line (its section 5 was not re-read in full); the suite's current
    result is above. PASS.

## 2. Findings

### BLOCKING

None.

### SHOULD FIX

**S1. A symbol whose previous bar lies outside the 21-day request window loses the return over the gap
(registration section 6: "r spans the gap").**
forward/sources_alpaca.py:93 (`DAILY_WINDOW_DAYS = 21`), 483-491 (`prev = max(...)`, `Missing("no earlier bar
within ...")`); enshrined by tests/test_forward_alpaca_sources.py:504
(`test_symbol_with_no_earlier_bar_in_the_window_is_missing_not_a_none_return`).
Scenario: an ETF has no bar from session h+1 through h+k with k >= about 14 sessions (a halt, or a vendor data gap
longer than three weeks). On its first session back, R, the raw window [R - 21 d, R] holds R's bar but not h's, so
`prev` is None and the symbol is Missing for R; the runner carries the position and books nothing (runner_f2.py:
652-657). On R+1, `prev` = R and `ret` = raw(R+1)/raw(R) - 1. The return from h to R, with any ex_dates in (h, R],
is never delivered: the registration's rule that "its P&L accrues when its data returns (r spans the gap)" is not
met. The runner notices only that `prev_date` differs from its last recorded session for the symbol, appends
`prev_date_mismatch:<s>` and books the one-day return anyway (runner_f2.py:659-662), so the wrong P&L is flagged,
not silent, but the record is permanent. Reach: rare for these ETFs; the cost is a wrong, unrepairable P&L entry.
Fix: when t's bar exists and no earlier bar is in the window, re-request that symbol alone with a much earlier
`start` (for example 400 days, or `WARMUP_FIRST_DATE`) before declaring Missing; keep Missing only if that wider
request has no earlier bar either. Change test 504 to expect the widened single-symbol request and the spanning
return; add a test with a gap of, say, 30 calendar days and a dividend inside it. The lead may read this as a
registration deviation and promote it; the fix is small and belongs in the adapter, where the raw closes are.

**S2. `ShadowRoute._orders` bounds the `all` query from the FIRST shadow record, so the route fails permanently
once the paper account holds 500 orders.**
forward/orders_alpaca.py:497-508 (`dates = [... for r in history] + [day]`; `after = min(dates) - 3 days`;
`if len(batch) >= ORDERS_LIMIT: raise ShadowError`).
Scenario: `min(dates)` is the first record's date for the whole life of the shadow ledger, so the `status="all"`
query covers every order ever placed; Alpaca returns at most 500 (newest first), the full-page check fires, and
`run()` raises ShadowError on every later day. With 12 symbols and daily rebalancing this happens within weeks. The
scratch demonstration above reproduces it with a filter-respecting fake (500 filled orders over 125 sessions, then
`run()` raises). Reach: shadow record only; loud (ShadowError, daily_f2 exits EXIT_SHADOW_FAILED); the E22-F2 book
is untouched.
Fix: compute `after` from the records that still hold pending orders (the records whose order ids `_pending_ids`
returns) and the current day, minus the 3-day margin, so the query covers only what reconciliation needs; or page
with `until`/`direction=asc` until fewer than 500 come back. Add a test with a fake whose `get_orders` honours
`after` and the 500 cap and a history of more than 500 orders.

**S3. A 200 response with no bar for any symbol on any date of the window is classified as a missing day, not as an
unavailable source.**
forward/sources_alpaca.py:476-509 (`have_session`, the `unconfirmed` loop) and 370-379 (`DayFetch.answer`).
Scenario: the bars endpoint answers 200 with empty data for all 12 symbols over the 21-day window (a silent
entitlement or routing fault, or an outage that returns empty rather than 5xx; no vendor page documents such a case,
so this is a guard, not a reproduced defect). Every symbol is "confirmed" missing by an equally empty single-symbol
request, `have_session` stays False, `bars()` returns Missing, and the runner records a missing day: P&L 0, flagged,
and it COUNTS as a 0 in the evaluation series (registration section 6), permanently. The brief's rule is that a
symbol is Missing only when the response "affirmatively lacks t's bar while the session is over"; a response that
lacks every bar of every symbol for three weeks affirms nothing about t.
Fix: after the raw fetch, if `raw` has no bar for any symbol on any date, raise SourceUnavailable ("empty window")
before the per-symbol logic; keep the current path (earlier bars present, none for t, each confirmed) as the
registration's undeclared-closure missing day. Add a test: an all-empty window raises SourceUnavailable, and
`test_missing_day_when_no_symbol_has_the_session_after_the_cutoff` (495) still passes because its tables hold
earlier sessions.

### NOTE

**N1. Stale interface documentation.** forward/etf_bars.py:8-10 (module docstring) still defines `ret` as
"adj(t) / adj(prev) - 1, both values taken from ONE fetch with adjustment 'all'". The lead's ruling and
registration section 6 replaced that with raw bars plus corporate actions; the code is agnostic, but the
interface's own definition should match the registration. Fix: rewrite the two sentences to "k x (rawclose(t) + D)
/ rawclose(prev) - 1 (registration section 6)".

**N2. The default corporate-actions fake filters on ex_date; the endpoint filters on process_date.**
tests/test_forward_alpaca_sources.py:82-97 (`FakeCAClient.get_corporate_actions` keeps records with
`request_params.start <= ex_date <= request_params.end`). Only `test_action_processed_after_its_ex_date_is_found_by_
the_wide_window` (371-394) uses a process_date-filtering subclass. The `div()` and `split()` helpers set
`process_date == ex_date`, so switching the default fake to filter on `process_date` changes no expected value and
makes every test exercise the endpoint's real semantics. Fix: filter on `process_date` in `FakeCAClient` and drop
the subclass.

**N3. Flags without an ex_date repeat; flags of symbols without a bar are dropped.** forward/sources_alpaca.py:
338-343: an `other` action with no ex_date (for example a name_change, which carries only process_date) is flagged
on every daily fetch whose 141-day process_date window includes it. forward/sources_alpaca.py:496: flags are
collected only for symbols that have t's bar; a flagged symbol with no bar on t (a merger or redemption that stops
trading) loses its flag. Fix: flag undated actions once (by process_date == t, or by id) and collect flags for the
`unconfirmed` symbols too.

**N4. A future `end` on /v1/corporate-actions is not verified.** forward/sources_alpaca.py:471 (daily: t + 60 days)
and 527 (warm-up: last + 60 days). The reference describes `end` as "The inclusive end of the interval ... Default:
current day" and states no maximum; whether the endpoint accepts a date 60 days ahead cannot be checked offline. If
it answered 400/422, `_call` would raise SourceUnavailable at once on every daily fetch (loud; no record written)
until the code is changed. Fix: confirm on the first connection session; if refused, clamp `end` to the New York
date of `now` (nothing is lost if Alpaca lists only processed actions; the coder's report note 2 already asks to
test whether actions appear before their process_date).

**N5. The two legs of a crossing are submitted in the same run.** forward/orders_alpaca.py:215-219, 243-262. The
whole-share sell-to-open is placed while the sell-to-close of the same symbol is still pending, so the paper
account's position check will probably reject it ("insufficient qty" or a long position still open); the rejection is
recorded (`_submit`, 520-558) and the next day re-plans from flat, one session late. The brief prescribed the split,
and the coder discloses the uncertainty (report section 6, item 5). The same applies to a fractional residual long
left by `floor(c)` in `moc_whole` mode after a mode switch (216; note "residual kept", 237-238). Shadow record only.
Fix (optional): submit the open leg only after the close leg's fill is seen (the next run), or document the one-day
lag as the shadow route's behaviour.

**N6. Window interplay with the F2 runner's cutoff.** forward/orders_alpaca.py:285: the `moc_whole` window opens at
19:00 ET on t, while the F2 record can be written from 18:00 ET (bar cutoff). A daily_f2 run between 18:00 and
19:00 ET stores the F2 record and the shadow raises ShadowWindowError (daily_f2.py:174-181 prints the failure and
exits EXIT_SHADOW_FAILED; the record is unaffected). Whether daily_f2 can re-run the shadow for an already stored
record is the runner's design (C4b). The coder's report states the practical schedule (after 19:00 ET). No code
change in the adapter; the operator's schedule must respect 19:00 ET for `moc_whole`.

**N7. Multi-action gaps.** `total_return` multiplies the whole sum `raw_t + D` by the full product `k` over
(prev, t]. When a bar gap contains a dividend with an ex_date earlier than a split's ex_date in the same gap, the
dividend (declared per pre-split share) is also scaled by that later split. This is what the registration's formula
says ("per share after that day's split" refers to the action's own day); the code follows it literally, and the case
needs a gap containing both actions. Recorded so the lead knows the simplification is the registration's, not an
adapter error.

**N8. Cross-reference for C4b (daily_f2.py:138).** `late_actions_for` calls `source.corporate_actions(first - 31
days, last)` with `last` = the last recorded session as the process_date upper bound. An action processed after the
last record (process_date = today) is therefore not seen until a later run whose `last` has passed its process_date:
a one-session lag in booking late actions, not a loss. The adapter's docstring (sources_alpaca.py:554-559) and the
coder's report say to query through today. Belongs to the C4b review; noted here because the lead's list names the
process_date filter.

**N9. No unit test of corporate-actions pagination.** The SDK pages inside `get_corporate_actions` with
`limit=None` (rest.py `_get_marketdata`, page_size 1000), so a fake at the client boundary cannot exercise it; the
contract test checks `limit is None` and `"limit" not in fields`, and a transport error on the call is tested (436
area, `test_malformed_corporate_action_raises_unavailable` and the ConnectionError/403 cases in the report's list).
Acceptable; a mid-page failure would surface as the SDK's exception and take the same retry path as bars.

## 3. Not verified (offline by design)

- Whether /v1/corporate-actions accepts a future `end` (N4) and whether it publishes actions before their
  process_date (report note 2): first connection session.
- Whether the paper account serves SIP daily bars (registration section 6's iex rule): first connection session.
- Whether Alpaca paper accepts the second leg of a crossing while the first is pending (N5).
- The alpaca-py source was read from the uv cache by grep and line ranges; the contract tests imported it offline.

## Verdict

APPROVE WITH FIXES. Counts: BLOCKING 0, SHOULD FIX 3 (S1 gap return beyond the 21-day window; S2 shadow
`get_orders` bound from the first record; S3 all-empty window read as a missing day), NOTE 9.
