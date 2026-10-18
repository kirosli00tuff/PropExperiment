# Adapter review: E.24 Part B IBKR adapter (AdapterReviewer-FableXHigh)

Independent review, 2026-10-18 11:17 to 11:40 PDT (times from `date`). Reviewer did not write any
file under review. No file was modified except this one. No network, no gateway, no .env read.

Scope read in full: forward/ibkr_gateway.py, forward/sources_ibkr.py, forward/orders_ibkr.py,
forward/daily_f1.py, forward/shadow_f1.json, tests/_forward_ibkr_mock.py, tests/test_forward_ibkr_*.py
(6 files). Reference: brief_B2_ibkr.md, brief_reviews.md (Common rules, B5), stage_e22_prereg_F1.md
sections 5-7, facts/ibkr_facts.md (I3, I5, I6, I7, I9, "What this means"), facts/ibkr_factcheck.md,
ibkr/ibkr_report.md, the frozen forward/{rolls,runner,history,sources,ledger}.py and rolls_f1.json
(by section), forward/strategy.py (grep), and the ib_async 2.1.0 source in the local uv cache
(~/.cache/uv/archive-v0/gvotQ0GydvB6H-_6/ib_async: ib.py, util.py, wrapper.py; no install, no network).

Checks run:
- sha256 of the 12 reviewed files equals the report's table (first 16 hex compared, all 12 match).
- `uv run pytest -q -p no:cacheprovider tests/test_forward_ibkr_*.py`: 69 passed, 1 skipped in 5.22 s.
- `uv run --offline --frozen --with-requirements forward/requirements_broker.txt pytest -q -p no:cacheprovider
  tests/test_forward_ibkr_vendor_contract.py`: 3 passed in 0.26 s (ib_async 2.1.0 from the cache).
- `sha256sum -c --quiet reports/stage_e22_f1_files.sha256`: OK at 11:18 PDT (re-run at the end, see the
  return to the lead).

Labels follow brief_reviews.md: BLOCKING (wrong result, frozen behaviour changed, a silent failure that
can corrupt a ledger or a verdict, a spec violation), SHOULD FIX (real defect with limited reach, or a
missing test of a required case), NOTE.

---

## BLOCKING

### B1. A timed-out historical request returns a partial bar list and the adapter accepts it as complete

- Where: forward/ibkr_gateway.py:415-440 (`GatewaySession.daily_bars`); the only timeout signature
  recognised is an empty list (line 440, `EmptyResponse`). Consumers: forward/sources_ibkr.py:423-442
  (`_observe`), 464-492 (`decide`, rules at 468 and 480), 611-651 (`_fetch_contract`).
- Vendor fact (verified in the cached ib_async 2.1.0 source, ib.py `reqHistoricalDataAsync`):
  `bars = BarDataList()`; `self.wrapper.startReq(reqId, contract, container=bars)`;
  `task = asyncio.wait_for(future, timeout)`; `except asyncio.TimeoutError: self.client.cancelHistoricalData(reqId)`;
  `return bars`. Bars are appended to the container as `historicalData` messages arrive, so when the
  60 s timeout fires mid-stream (an HMDS farm break, codes 2105/2106, between the first bar and
  `historicalDataEnd`) the call returns the bars received so far, with no error and no flag.
  `RaiseRequestErrors = True` (which the coder sets) covers error-ended requests only; a timeout is not
  an error in ib_async.
- Spec: brief B2 item 4: "a connection failure, timeout, pacing violation or partial response raises a
  SourceUnavailable error so that NO ledger record is written". The report (ibkr_report.md:69) says
  "ib_async's empty timeout result" is retried; the non-empty timeout result is not handled.
- Failure scenario, daily path: at 18:00 CT on t, contract A's stream stalls after its first bars (bars
  arrive oldest first, so A's bar for t is the one cut off) while contract B on the same exchange
  returns a full list ending with the open session's bar dated t+1. In `decide`, `exchanges_moved_on`
  contains A's exchange (line 468), so A is `affirmed_missing` by rule (c) (line 480). The frozen
  runner writes `missing:A` for t: A's position is carried at the old mark and A's pending order is
  recorded `order_expired:A` (runner.py:244-249). A wrong record that can never be changed (prereg
  sec. 6), produced by a transient fault that the spec says must yield no record.
- Failure scenario, warm-up path: a stalled window request for contract C drops the tail of C's
  series. If the tail held C's roll date, `_day_quotes` (sources_ibkr.py:542-562) never sees both legs
  on a roll-due day and the reference sticks on C for the rest of the warm-up; `write_warmup` round-trips
  cleanly; only `warmup_summary` (`open_roll` true, a stale `last_date`) shows it, and `cmd_warmup`
  (daily_f1.py:198-249) prints it but exits 0. The frozen strategy then raises ValueError on the first
  live day (`instrument_frame` -> `back_adjusted_series`: the switch row lacks the old leg), which is
  loud and writes no record, but by then the warm-up file and its sha256 are recorded (prereg sec. 6).
- Mock fidelity: tests/_forward_ibkr_mock.py:370-413 cannot return a truncated list without an error, so
  no test exercises this path; `test_partial_history_empty_answers_raise_unavailable_never_missing`
  (tests/test_forward_ibkr_source.py:132) covers only the empty case despite its name.
- Fix: make a timeout raise instead of returning. One way: in `daily_bars` call
  `gw.run(asyncio.wait_for(gw.reqHistoricalDataAsync(contract, ..., timeout=0), self.policy.request_timeout_s))`
  so `TimeoutError` (TRANSIENT) is raised and no partial list can ever be returned (add
  `reqHistoricalDataAsync` and `run` to the Gateway Protocol and the vendor contract test; both exist in
  ib_async 2.1.0). Keep the empty-list check. Add a mock fault mode "truncate the list, raise nothing" and
  tests for the daily path (expects SourceUnavailable, no record) and the warm-up path (expects a raise,
  no file). Until this is fixed, rule (c) in `decide` can turn a stall into a false `missing:I`.

---

## SHOULD FIX

### S1. Warm-up: a "no data" answer inside the 2-year depth is accepted silently; the report says a gap raises

- Where: forward/sources_ibkr.py:643-645 (`_fetch_contract`): `except NoHistoricalData:` notes "server: no
  data for the window" and returns `{}` for every contract, `old` or not. Only `ContractNotFound`
  (lines 632-639) and `EmptyResponse` (646-650) honour `old`. The docstring (572-585) and
  ibkr_report.md:97 ("A gap after it raises") describe the ContractNotFound rule as if it covered gaps.
- Failure: MNQU25 (anchor 2025-09-19, inside the depth at a 2026-11 read) answers 162 "HMDS query
  returned no data" (a transient HMDS state, or a wrong query). Its window is skipped. In
  `assemble_rows`, M25 stops being priced after its last trade in June 2025, U25 is never available, so
  the switch M25 -> U25 never happens and the switch to Z25 cannot either (`_day_quotes` 557-561 needs
  the current leg priced on the switch row). MNQ's warm-up reference sticks on M25; the file is written
  and hashed; the summary shows `open_roll: true` and a stale `last_date` but nothing refuses.
- Fix: re-raise `NoHistoricalData` unless `old` (mirror lines 646-650). Make `cmd_warmup` refuse (exit 2,
  nothing written) when any instrument's `open_roll` is true and its last priced date is more than a
  few weekdays before `last` (a legitimately deferred roll at the end has a recent `last_date`; the
  coder sets the tolerance). Add a test with a mid-window no-data contract. Correct the report sentence.

### S2. Missing-day confirmation leans on the open session's partial bar; the "not ready" test edits the mock to pass

- Where: forward/sources_ibkr.py:441 (`later = max(d for d in prices if d > trade_date)`), 468 and 480
  (rule (c), by exchange). Mock: tests/_forward_ibkr_mock.py:362-368 dates the open session's bar t+1
  after 17:00 CT, as IB does (I6). Test: tests/test_forward_ibkr_source.py:119-130; line 122 strips
  every bar after t from the mock, which is the only reason DayNotReady is reached.
- What the production path does: at the normal run time (18:00 CT on t; the t+1 session opened at
  17:00 CT) every contract on CME, COMEX, NYMEX and the CBOT financials ends its list with the
  in-progress bar dated t+1. Any contract with no bar for t is therefore "affirmed missing" at once
  (rule (a) by its own partial bar, or rule (c) by its exchange). Without line 122, the scenario of the
  test yields `missing:MGC`, not DayNotReady. So the test's name and the report's wording ("no later
  bar confirms the session is over") describe a state that occurs only on Friday evenings and
  weekends.
- Risk: the confirmation comes from a bar whose session has not closed. If IB commits or revises the
  bar for t after the next session has opened (I6: historical data "gets adjusted, compressed and
  filtered"; the settlement can arrive hours later) [unverified from the saved pages: none describes
  HMDS commit timing], a late bar for t is confirmed missing by the partial t+1 bar, and the runner
  writes `missing:I`. Low probability, same consequence as B1's daily case.
- Fix: count as "later" only bars whose own session is final: `is_ready(d, now)`, for rules (a) and (c).
  The ordinary priced path is unchanged; a genuinely missing contract is confirmed on t+1 after
  18:00 CT instead of on t (safe: DayNotReady, exit 2, no record), which with N3's catch-up costs
  nothing. Rewrite the test to use the production state (partial bars present) and assert the intended
  outcome explicitly. If the lead prefers the present rule, keep it but document that the next
  session's open bar is the confirmation, and add a test that says so.

### S3. The unattended default date can land on an exchange holiday that IB serves as a bar

- Where: forward/daily_f1.py:139 (`latest_ready_trade_date(deps.now())` when `--date` is absent),
  forward/sources_ibkr.py:161-166. Neither has any holiday notion (the frozen runner has none either;
  prereg sec. 6 puts declarations on the operator; the report's operational note says "Schedule run
  after 16:00 PT, e.g. 16:15 PT on weekdays").
- Why it matters for this source: IB dates a daily bar by the calendar day on which the session closes
  (I6, legacy). On US holidays several of the 12 trade a shortened session that closes on the holiday
  (CME equity index, COMEX, NYMEX, CBOT financials: roughly 12:00-13:00 CT; CBOT grains are closed), and
  the CME trade date of that session is the next business day with no settlement on the holiday
  [unverified from the saved pages: none describes IB's dating of holiday sessions]. If IB returns a bar
  dated on the holiday, a cron run at 16:15 PT writes a ledger record for a day the published calendar
  says is closed: a sec. 6 deviation ("a declaration must match the exchange's published holiday
  calendar") that can never be corrected. The grains would be `missing:MZC/MZS/MZL` on that record (via
  rule (c) through the CBOT yields), a visible signature that nothing checks.
- Fix (lead's choice of mechanism): require an explicit `--date` for `run` unless a holiday file is
  given (`--holidays FILE`, the operator's copy of the published CME calendar; a listed date exits 2
  with "declare it closed"); and/or refuse a day on which every contract of one exchange is affirmed
  missing while other exchanges are priced, unless an explicit flag accepts it. Some guard is needed
  before an unattended schedule is used.

### S4. Price definition differs between the warm-up and the live series (decision for the lead; not fixable in code alone)

- Where: forward/sources_ibkr.py:66 (`CUTOFF_CT = time(18, 0)`), 423-442 (daily fetch at the cutoff),
  611-651 (warm-up fetch, days to years after each session). Both are labelled `close_last_trade`.
- The cutoff itself is safe for its stated purpose: all 12 sessions end by 16:00 CT (grains 13:20 CT),
  the settlement times are earlier still (from memory, [unverified]: grains 13:15, metals and energy
  13:30, FX and yields 14:00, equity indices 15:00 CT), the CME-group delay is 10 minutes (I3), early
  closes end earlier, and on Fridays no next-session bar exists so a missing contract waits for
  Sunday/Monday (safe, see N3). The DST test (ib_end_of_day) is right.
- What it does not do: I6 says the TRADES close "can be" replaced by the settlement hours later
  (Friday's sometimes on Saturday) and that IB's history is "adjusted, compressed and filtered". The
  live record for t is the value at 18:00 CT on t (pre-replacement last trade); the warm-up rows and
  any later refetch are the values IB holds afterwards (post-replacement where IB applied one). The
  strategy's 256-difference window straddles that boundary on the start date, so one series carries two
  definitions under one label. The report's open question 2 names the timing but not the asymmetry
  with the warm-up. (A re-run of a recorded date raising LedgerConflictError is the symptom of the same
  fact; the coder notes that correctly.)
- Fix: this is the lead's and the user's decision (brief item 6; report open question 1). Whatever is
  decided, record it before the warm-up is built: (i) if IB's close becomes the registered price of an
  amended F1b, decide the cutoff on evidence (the probe could refetch the same bar at 18:00 CT, 08:00 CT
  next day and a week later and log the differences), and state in DECISIONS that warm-up and live
  values are fetched at different ages; (ii) or route settlements through a second source. The adapter
  needs no code change for this item beyond the probe.

### S5. Shadow route: late fills can be lost, and the mock hides it

- Where: forward/orders_ibkr.py:380-390 (`_late_fills` via `reqExecutions()` with no filter), 297-309
  (`_place`), 311-314 (`_wait`, default `fill_wait_s` 60 s). Mock: tests/_forward_ibkr_mock.py:463
  (`reqExecutions` returns every execution ever made).
- IB's `reqExecutions` returns the current day's executions only [unverified from the saved pages; the
  I9 quotes do not cover retention]. CBOT grains open at 19:00 CT, so a MKT order placed at ~18:00 CT
  for MZC/MZS/MZL is queued and fills after the 60 s wait; the next run is about 24 hours later, so the
  fill (price, time, commission: brief item 7 requires them) is never written, though `positions_before`
  reflects it. The docstring (lines 25-27) and shadow_f1.json's `fill_wait_s` doc promise late fills are
  found "through reqExecutions by orderRef", which holds only within the same IB day. Limited reach:
  the shadow ledger is a record only; E22-F1 is untouched.
- Fix: keep the session open until the last exchange in the plan has opened and collect fills from the
  Trade objects (or `ib.fills()`), or set and document a `fill_wait_s` that covers 19:00 CT when grains
  are in the plan; state the same-day limit of `reqExecutions` in shadow_f1.json; give the mock a
  same-day `reqExecutions` so a test can show a lost fill.

---

## NOTE

### N1. Error 321 is a warning in ib_async, so the FATAL path is unreachable and the report line is inaccurate
forward/ibkr_gateway.py:43 (`VALIDATION_CODES = {321}`) and 402. ib_async 2.1.0 wrapper.py:1609 lists 321
in `warningCodes`: it is logged, the future stays pending, the request times out, the empty list raises
`EmptyResponse`, and four attempts with 15/30/60 s backoff end in SourceUnavailable after about six
minutes. Safe but slow; ibkr_report.md:80 ("Stopped at once ... 321") is wrong. Optionally subscribe to
`errorEvent` to catch 321 for the pending reqId and stop at once.

### N2. `endDateTime` format: the current page documents a different form than the one hand-built
forward/sources_ibkr.py:169-178 builds "YYYYMMDD-hh:mm:ss". The saved current page
(pages/ibkr/tws_md_historical_bars.html.txt line 54) documents `endDateTime` as "YYYYMMDD HH:mm:ss TMZ";
the hyphen form appears in the legacy page's code samples built from `ToUniversalTime()`
(legacy_historical_bars.html.txt:23-40) and as `reqHeadTimeStamp` formatDate=1 output
(tws_md_earliest-data-point.html.txt:41), so it is an accepted UTC form, but not the documented one for
this call. ib_async's `formatIBDatetime` (util.py:574-590) passes strings through and would format an
AWARE datetime as "YYYYMMDD HH:MM:SS UTC" (the documented form); the "local time zone trap" the coder
avoids applies to `date` objects and naive values only. Either pass an aware
`datetime.combine(day, time(23,59,59), tzinfo=CME_TZ)` and let ib_async format it, or make `probe`
(forward/daily_f1.py:291-317, now `end=""`) also exercise an explicit end time so the first connection
session confirms the format before the warm-up relies on it.

### N3. No catch-up loop; RunnerError is not mapped to an exit code
After any exit-2 day (DayNotReady, a Friday with one missing contract, a gateway restart), the next
day's default `--date` fails the frozen gap check (runner.py:168-193) with an uncaught `RunnerError`
traceback (exit 1) from forward/daily_f1.py:153, and the schedule stalls until a manual `--date` run.
Suggest `run` iterate from the ledger's last date + 1 to the latest ready date, each day through the
full source -> run_date path, stopping at the first non-zero exit; and catch `RunnerError` -> exit 2.

### N4. The shadow route connects (readonly False) before its port and paper-account guards
forward/orders_ibkr.py:223-224. Check `params.port` against LIVE_PORTS and the DU prefix before
`ensure_connected()`; the managedAccounts check needs the connection and stays after.

### N5. Grains orders at 18:00 CT are queued until 19:00 CT
Ties to S5. Say so in shadow_f1.json's `order_type` doc ("the next session" is not yet open for the grains).

### N6. The 2-year depth is measured from the anchor date, not IB's expiration date
forward/sources_ibkr.py:599 uses `expiry_guard` (the anchor). Off by about 3 business days for MCL (the
lenient direction) and up to about 4 weeks for MGC and the grains (the conservative direction). Harmless;
say so in the comment.

### N7. No unit sanity check on grain closes
`_validated` compares IB's multiplier and priceMagnifier with the spec, so a textual mismatch stops the
run (good, and the report says so). Nothing checks the price level (an MZC close of 4.25 instead of
425.25 would pass and be divided by 100 again). A one-line level check in `bar_prices` or in `probe`
(grain IB close > 50) is cheap insurance for an [unverified] convention (I7).

### N8. Holidays and rule (c)
On a US holiday where CBOT grains are closed but the CBOT yields trade, the grains are affirmed missing
through rule (c). Consistent with the rule, and part of why S3 needs a guard.

---

## Checked and found sound

- Contract resolution: `Future(symbol, YYYYMM, exchange, currency, includeExpired=True, tradingClass)`
  through `reqContractDetails`; zero matches -> ContractNotFound, two or more -> error with the
  candidates listed, never a guess; secType, symbol, currency, exchange, contractMonth, priceMagnifier,
  multiplier, conId and a parseable last trade date are checked (sources_ibkr.py:318-360); MHNG/MNG per
  I7; `check_specs` ties the implied runner multiplier to config_f1.json; foreign roots and off-cycle
  months refused before any request. Tests cover expired, ambiguous, unknown, field mismatch.
- Rolls: `contracts_for_day` (202-209) delivers the previous contract from its roll date through its
  anchor, which is exactly when the frozen `_roll` (runner.py:194-229) needs both legs or still holds
  the old one; an expired old leg inside the anchor window is `affirmed_missing` (no deadlock); tested
  on MNQZ26 -> MNQH27 with the runner rolling on 2026-12-10.
- Trade dates: Chicago everywhere, naive datetimes refused, DST end times verified (CST and CDT), the
  Vancouver/Chicago date split tested; the partial next-session bar is never used for t (price by exact
  date) nor for t+1 (cutoff).
- Missing vs unavailable: `Missing` only when every absence is affirmative and no contract is priced;
  the driver refuses a whole-day Missing without `--accept-missing-day` (exit 3); connection drops,
  empty answers, pacing (162 text), connectivity codes retried with 15/30/60 s and reconnect; no-data
  answers (162 text, 166) never a price, never retried, never a Missing alone; subscription refusals
  (354, 10089, 10090, 10186, 10187, or permission text) stop at once after `reqMarketDataType(3)`
  (factcheck C1 applied). Mock behaviour matches ib_async 2.1.0 on: string endDateTime pass-through,
  daily bars as `datetime.date` (`parseIBDatetime`, 8 chars), `ConnectionError("Socket disconnect")` on a
  drop (wrapper.connectionClosed), `RequestError(reqId, code, message)` when `RaiseRequestErrors` is set
  (wrapper.error -> `_endReq(success=False)`), 10167 and 2100-2199 as warnings. Gaps: B1 (timeout
  partial), S5 (reqExecutions retention), N1 (321).
- Warm-up: `assemble_rows` applies rolls_f1.json as the runner does (first reference = declared
  contract on the first priced day; a switch only on a day with both legs, which carries both prices);
  `write_warmup` refuses overwrite, verifies the `load_warmup` round trip and writes `<file>.sha256`;
  `warmup_summary` gives rows, first date, live_at_start (256 differences); contracts beyond the depth
  that IB does not know are noted and skipped, and the first date moves later: detected and reported
  for the early-history case (the mid-window case is S1/B1). The round-trip test runs
  `back_adjusted_series` for all 12 and the runner accepts the file.
- CSV export: `repr()` floats, header comment skipped by the frozen parser, idempotent, different
  duplicate refused, full re-validation; the frozen `forward.runner` CLI on the exported CSV produces a
  byte-identical ledger (tests/test_forward_ibkr_driver.py:44-93).
- Shadow route and the E22-F1 ledger: read through `parse_chain` only; same path, symlink and hard link
  refused; non-shadow records refused; disabled by default; a recorded date is returned without orders;
  account id never written (variable name only). The byte-identical tests really compare bytes and
  sha256 over several days: tests/test_forward_ibkr_shadow.py:98-125 (6 days with a roll; also asserts
  the E22 ledger bytes unchanged after each shadow run) and tests/test_forward_ibkr_driver.py:198-226
  (5 days, frozen strategy, warm-up, driver on and off).
- Credentials: `ConnectionParams.__repr__` withholds values; socket error texts redacted (host, port,
  account, clientId); env-status prints names only; no .env read; `--env-file` is the operator's.
- ib_async imported lazily (`_import_ib_async` in two factories), verified by a subprocess test.
- Frozen files: `sha256sum -c --quiet reports/stage_e22_f1_files.sha256` OK at the start of the review.

---

## Counts

BLOCKING 1 (B1). SHOULD FIX 5 (S1-S5). NOTE 8 (N1-N8).

## Verdict

BLOCK. One blocking item (B1: ib_async returns a partial bar list on timeout and the adapter treats it
as complete; with rule (c) in `decide` that can write a false `missing:I`, and in the warm-up a silently
shortened series). The fix is small and local (a timeout that raises, a mock fault mode, two tests), after
which the remaining items are SHOULD FIX and the re-review can be narrow. S3 and S4 need the lead's
decisions before any unattended run or warm-up build.
