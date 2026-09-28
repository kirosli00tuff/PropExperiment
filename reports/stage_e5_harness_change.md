# Stage E.5 Task A2: harness v5 change set (HarnessBuilder-OpusXHigh)

Written 2026-09-27, about 12:38 to 13:10 PDT, against reports/stage_e5_harness_plan.md section 3 (with
the lead's rulings in section 4) and the brief reports/stage_e5_briefs/A2_harness_builder.md. No
commit, no manifest rebuild, no vendor call, no Databento key, no bar read, no web access. Files
touched: rules/sessions.py, screening/stage_e_verdict.py (new), data/config.py, data/pull_step2.py,
tests/test_stage_e_sessions_holidays.py (new), tests/test_stage_e_verdict.py (new),
tests/test_e2b_pull_step2.py, tests/test_e2a_rules.py. Nothing else.

**Read first (needs the lead): the change to rules/sessions.py breaks three frozen-K3 table tests.**
strategy/members/k3/_calendar.py (K3 member freeze c4fb5da4) carries `SOURCE_SHA256` pinning
rules/sessions.py at its v4 sha256 (d9a7fcfe...) and a literal `FX_FULL_SESSIONS` table that
reports/stage_e4_briefs/gen_k3_tables.py computed from v4's `day_rule`. Under v5, 14 of those
1,797 "full FX sessions" are no longer full sessions for the engine: 2022-01-17, 02-21, 05-30, 06-20,
07-04, 09-05, 11-24, 2023-01-16, 02-20, 05-29, 06-19, 07-04, 09-04, 11-23 (every K3 root now
flattens at 11:30 CT there). K3's members (tkypre, ecbfix, ldnmom, ldnrev, ...) still read the
frozen table, so they would plan events on those dates and the v5 engine would force them flat at
11:30. The failing tests (tests/test_e4_k3_members_b.py, not a harness TEST_PATTERN and not in any
freeze): `test_every_source_file_has_the_pinned_sha256`, `test_both_modules_are_exactly_the_
generators_output`, `test_fx_full_sessions_are_ec_cal_dates_without_halt_and_with_the_regular_f`.
Making them pass needs either a K3 member-code change (regenerating _calendar.py: a K3 freeze
change) or rewriting the K3 tests to pin the v4 sessions source. Both are outside what the brief
lets me decide (STOP rule), so I made neither; the rest of the change set is complete. K4 and K5
member code does not reference rules/sessions.py.

## 1. Changes, file by file

### 1.1 rules/sessions.py (3a)
- :18-35 module docstring: the 2019-2023 paragraph now says what is derived (Rule H-1, the lead,
  the source id, `TOPSTEP_DERIVED_YEARS`) and what is unsettled (`TOPSTEP_UNSETTLED_DATES`); the
  lead sentence says 30 minutes in 2019-2025, 15 in 2026.
- :93 `_TS_DERIVED = "topstep_derived_e5_equity_calendar"`; :94 adds `_0745`.
- :100-161 the comment block (Rule H-1, the 30-minute lead L-E5-2, the four published exceptions,
  the unsettled rule and the ordinary-holiday reading) and 48 literal rows
  `TopstepHoliday(date(...), _1130 | _1145 | _0745 | _CLOSED, _TS_DERIVED)`, trade dates
  2019-05-27..2023-12-25, in the same dict before the published 2024 rows (unchanged).
- :205-213 `TOPSTEP_EARLY_CLOSE_LEAD` gains 2019..2023 at 30 minutes (2024-2026 unchanged).
- :214 `TOPSTEP_SCHEDULE_YEARS = frozenset({2024, 2025, 2026})` (written out; no longer derived from
  the lead table); :215 `TOPSTEP_DERIVED_YEARS = frozenset(range(2019, 2024))`; :216-217
  `TOPSTEP_DERIVED_FIRST/LAST` (2019-05-01, 2023-12-31).
- :218-226 `TOPSTEP_UNSETTLED_DATES`: a literal tuple of (date, reason) pairs.
- `day_rule` (:294) and every other function: unchanged. File sha256 before d9a7fcfe6724f066...
  (v4), now different (426 lines).

### 1.2 screening/stage_e_verdict.py (3b, new, about 690 lines)
See section 4.

### 1.3 data/config.py (3c)
:114-127, after the E.2b block and its STEP2_ROOT lines, before `DATABENTO_KEY_ENV`. Every earlier
line is byte-identical (git diff shows 15 added lines, 0 removed). As written:

```python
# Stage E.5 spend policy (stage prompt, 2026-09-27): the step 2 purchase of K4 and K5 on
# ACTIVE_ACCOUNT (acct-2). The E.5 lead sets both caps in Task B1 from the fresh quote before any
# purchase; 0.00 means the gate refuses every billable request until then, and
# `python -m data.pull_step2 --buy` refuses to start.
STAGE_E5_SESSION_ID = "stage-E.5-2026-09-27"
E5_SESSION_CAP_USD = 0.00
E5_REQUEST_CAP_USD = 0.00

# The active step 2 purchase policy: the three names data.pull_step2.step2_gate reads. A later
# purchase session adds its own block above and repoints these three (a config-only edit, as the
# E.2b design intended); the blocks of earlier sessions stay as they were.
STEP2_PURCHASE_SESSION_ID = STAGE_E5_SESSION_ID
STEP2_SESSION_CAP_USD = E5_SESSION_CAP_USD
STEP2_REQUEST_CAP_USD = E5_REQUEST_CAP_USD
```

### 1.4 data/pull_step2.py (3c, lead ruling L-E5-1)
- :36-40 module docstring: the gate sentence names the active step 2 purchase policy.
- :83-90 import list: `STEP2_PURCHASE_SESSION_ID`, `STEP2_REQUEST_CAP_USD`,
  `STEP2_SESSION_CAP_USD` replace the three E.2b names.
- :371-378 `step2_gate`: `LockedQuoteGate(STEP2_PURCHASE_SESSION_ID,
  session_cap_usd=STEP2_SESSION_CAP_USD, request_cap_usd=STEP2_REQUEST_CAP_USD,
  account=ACTIVE_ACCOUNT, **overrides)`; docstring follows.
- :388-395 `require_buy_caps` message: "step 2 buy refused: session cap $0.00, request cap $0.00
  (<session id>). A purchase session sets its own caps in data/config.py first" (the "Stage E.2b is
  quotes only" clause is gone).
- Nothing else: chunk plan, seals, byte check, quote writer and paths unchanged (the :139 comment
  naming E.2b's quote session is history and stays).

### 1.5 tests
- tests/test_stage_e_sessions_holidays.py (new, 21 tests): 3a (i)-(v), section 3 below.
- tests/test_stage_e_verdict.py (new, 86 tests): 3b, sections 4 and 5 below.
- tests/test_e2b_pull_step2.py: :257-259 and :393 assert the active policy's session id
  (`config.STEP2_PURCHASE_SESSION_ID`) instead of "stage-E.2b-2026-09-26"; :335 the zero-caps test
  is renamed `test_the_buy_refuses_to_start_with_the_active_zero_caps` and :342 matches the new
  message; :641 new `test_the_step2_gate_reads_the_e5_block_and_refuses_to_buy_at_its_zero_caps`
  (config pins: E.5 id and 0.00 caps, the three active names point at them, the E.2b block
  unchanged; the CLI's gate is "stage-E.5-2026-09-27" on acct-2 with the account cap; `--buy`
  returns RC_REFUSED after the preflight, with no key loaded and no client built; the ledger stays
  empty); :676 new `test_quote_only_ledgers_its_lines_under_the_e5_session` (tmp ledger: every line
  a $0.00 quote on acct-2 under "stage-E.5-2026-09-27", the quotes JSON carries the id, the real
  ledger, holdout manifest and unlock log untouched). File: 41 passed in 81.9 s.
- tests/test_e2a_rules.py: :251 `NO_LEAD_WED = date(2027, 3, 10)`; :275-281
  `test_early_close_flatten_is_the_close_minus_15` moves its synthetic halt from 2021-03-10 to that
  date and asserts the year has no Topstep lead. Reason: 2021 now carries the derived 30-minute
  lead, so D9.1's "halt minus 15" alone can only be pinned in a year with no lead; the derived-year
  case is pinned in the new file. Its other tests keep 2021-03-10.

## 2. Rule H-1 validation against the published rows (test (i))

Rule H-1 applied to the equity calendar's 2024, 2025 and 2026 entries with each year's published
lead (30, 30, 15 minutes). The table holds 37 published rows (the plan says 38: its count is off
by one). 36 lie in the rule's domain (the equity calendar ends 2026-12-25); 35 match; the one
mismatch and the three unpublished rule dates are the four named exceptions; 2027-01-01 is outside
the domain. The test fails on a fifth mismatch, a new unpublished rule date or a lost row.

| Date | Equity entry | Lead | Rule H-1 | Published | Match |
|---|---|---|---|---|---|
| 2024-01-01 | New Year's Day (observed), closure | 30 | closed | not published | exception: rule date not published (before the 2024 article's first row) |
| 2024-01-15 | Martin Luther King Jr. Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2024-02-19 | Presidents Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2024-03-29 | Good Friday, closure | 30 | closed | closed | yes |
| 2024-05-27 | Memorial Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2024-06-19 | Juneteenth, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2024-07-03 | Day before Independence Day, halt 12:15 | 30 | 11:45 | 11:30 | exception: published 11:30, rule 11:45 (equity halt 12:15) |
| 2024-07-04 | Independence Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2024-09-02 | Labor Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2024-11-28 | Thanksgiving Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2024-11-29 | Day after Thanksgiving, halt 12:15 | 30 | 11:45 | 11:45 | yes |
| 2024-12-24 | Christmas Eve, halt 12:15 | 30 | 11:45 | 11:45 | yes |
| 2024-12-25 | Christmas Day, closure | 30 | closed | closed | yes |
| 2025-01-01 | New Year's Day, closure | 30 | closed | closed | yes |
| 2025-01-09 | National Day of Mourning (Carter), halt 08:30 | 30 | 08:00 | not published | exception: rule date not published (unscheduled day of mourning) |
| 2025-01-20 | Martin Luther King Jr. Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2025-02-17 | Presidents Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2025-04-18 | Good Friday, closure | 30 | closed | closed | yes |
| 2025-05-26 | Memorial Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2025-06-19 | Juneteenth, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2025-07-03 | Day before Independence Day, halt 12:15 | 30 | 11:45 | not published | exception: rule date not published (omitted from the 2025 schedule) |
| 2025-07-04 | Independence Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2025-09-01 | Labor Day, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2025-11-27 | Thanksgiving, halt 12:00 | 30 | 11:30 | 11:30 | yes |
| 2025-11-28 | Day after Thanksgiving, halt 12:15 | 30 | 11:45 | 11:45 | yes |
| 2025-12-24 | Christmas Eve, halt 12:15 | 30 | 11:45 | 11:45 | yes |
| 2025-12-25 | Christmas Day, closure | 30 | closed | closed | yes |
| 2026-01-01 | New Year's Day, closure | 15 | closed | closed | yes |
| 2026-01-19 | Martin Luther King Jr. Day, halt 12:00 | 15 | 11:45 | 11:45 | yes |
| 2026-02-16 | Presidents Day, halt 12:00 | 15 | 11:45 | 11:45 | yes |
| 2026-04-03 | Good Friday (abbreviated, jobs report), halt 08:15 | 15 | 08:00 | 08:00 | yes |
| 2026-05-25 | Memorial Day, halt 12:00 | 15 | 11:45 | 11:45 | yes |
| 2026-06-19 | Juneteenth, halt 12:00 | 15 | 11:45 | 11:45 | yes |
| 2026-07-03 | Independence Day (observed), halt 12:00 | 15 | 11:45 | 11:45 | yes |
| 2026-09-07 | Labor Day, halt 12:00 | 15 | 11:45 | 11:45 | yes |
| 2026-11-26 | Thanksgiving, halt 12:00 | 15 | 11:45 | 11:45 | yes |
| 2026-11-27 | Day after Thanksgiving, halt 12:15 | 15 | 12:00 | 12:00 | yes |
| 2026-12-24 | Christmas Eve, halt 12:15 | 15 | 12:00 | 12:00 | yes |
| 2026-12-25 | Christmas Day, closure | 15 | closed | closed | yes |
| 2027-01-01 | (none) | n/a | n/a | closed | outside the rule's domain: the frozen equity calendar ends 2026-12-25 |

## 3. The derived rows, the unsettled list and the day_rule effect

### 3.1 The 48 derived rows (2019-05-01..2023-12-31, lead 30 minutes)

Rule H-1 gives 51 dates in the span; the three July 3s are unsettled; 48 rows are written.

| Date | Equity entry | Close-by |
|---|---|---|
| 2019-05-27 (Mon) | Memorial Day, halt 12:00 | 11:30 |
| 2019-07-04 (Thu) | Independence Day, halt 12:00 | 11:30 |
| 2019-09-02 (Mon) | Labor Day, halt 12:00 | 11:30 |
| 2019-11-28 (Thu) | Thanksgiving Day, halt 12:00 | 11:30 |
| 2019-11-29 (Fri) | Day after Thanksgiving, halt 12:15 | 11:45 |
| 2019-12-24 (Tue) | Christmas Eve, halt 12:15 | 11:45 |
| 2019-12-25 (Wed) | Christmas Day, closure | closed |
| 2020-01-01 (Wed) | New Year's Day, closure | closed |
| 2020-01-20 (Mon) | Martin Luther King Jr. Day, halt 12:00 | 11:30 |
| 2020-02-17 (Mon) | Presidents Day, halt 12:00 | 11:30 |
| 2020-04-10 (Fri) | Good Friday, closure | closed |
| 2020-05-25 (Mon) | Memorial Day, halt 12:00 | 11:30 |
| 2020-09-07 (Mon) | Labor Day, halt 12:00 | 11:30 |
| 2020-11-26 (Thu) | Thanksgiving Day, halt 12:00 | 11:30 |
| 2020-11-27 (Fri) | Day after Thanksgiving, halt 12:15 | 11:45 |
| 2020-12-24 (Thu) | Christmas Eve, halt 12:15 | 11:45 |
| 2020-12-25 (Fri) | Christmas Day, closure | closed |
| 2021-01-01 (Fri) | New Year's Day, closure | closed |
| 2021-01-18 (Mon) | Martin Luther King Jr. Day, halt 12:00 | 11:30 |
| 2021-02-15 (Mon) | Presidents Day, halt 12:00 | 11:30 |
| 2021-04-02 (Fri) | Good Friday (abbreviated, jobs report), halt 08:15 | 07:45 |
| 2021-05-31 (Mon) | Memorial Day, halt 12:00 | 11:30 |
| 2021-07-05 (Mon) | Independence Day (observed), halt 12:00 | 11:30 |
| 2021-09-06 (Mon) | Labor Day, halt 12:00 | 11:30 |
| 2021-11-25 (Thu) | Thanksgiving Day, halt 12:00 | 11:30 |
| 2021-11-26 (Fri) | Day after Thanksgiving, halt 12:15 | 11:45 |
| 2021-12-24 (Fri) | Christmas Day (observed), closure | closed |
| 2022-01-17 (Mon) | Martin Luther King Jr. Day, halt 12:00 | 11:30 |
| 2022-02-21 (Mon) | Presidents Day, halt 12:00 | 11:30 |
| 2022-04-15 (Fri) | Good Friday, closure | closed |
| 2022-05-30 (Mon) | Memorial Day, halt 12:00 | 11:30 |
| 2022-06-20 (Mon) | Juneteenth (observed), halt 12:00 | 11:30 |
| 2022-07-04 (Mon) | Independence Day, halt 12:00 | 11:30 |
| 2022-09-05 (Mon) | Labor Day, halt 12:00 | 11:30 |
| 2022-11-24 (Thu) | Thanksgiving Day, halt 12:00 | 11:30 |
| 2022-11-25 (Fri) | Day after Thanksgiving, halt 12:15 | 11:45 |
| 2022-12-26 (Mon) | Christmas Day (observed), closure | closed |
| 2023-01-02 (Mon) | New Year's Day (observed), closure | closed |
| 2023-01-16 (Mon) | Martin Luther King Jr. Day, halt 12:00 | 11:30 |
| 2023-02-20 (Mon) | Presidents Day, halt 12:00 | 11:30 |
| 2023-04-07 (Fri) | Good Friday (abbreviated, jobs report), halt 08:15 | 07:45 |
| 2023-05-29 (Mon) | Memorial Day, halt 12:00 | 11:30 |
| 2023-06-19 (Mon) | Juneteenth, halt 12:00 | 11:30 |
| 2023-07-04 (Tue) | Independence Day, halt 12:00 | 11:30 |
| 2023-09-04 (Mon) | Labor Day, halt 12:00 | 11:30 |
| 2023-11-23 (Thu) | Thanksgiving Day, halt 12:00 | 11:30 |
| 2023-11-24 (Fri) | Day after Thanksgiving, halt 12:15 | 11:45 |
| 2023-12-25 (Mon) | Christmas Day, closure | closed |

### 3.2 The unsettled list (`TOPSTEP_UNSETTLED_DATES`)

| Date | Equity entry | Reason |
|---|---|---|
| 2019-07-03 | Day before Independence Day, halt 12:15 | July 3: the one date Rule H-1 does not reproduce in the published years (2024-07-03 published 11:30 against the rule's 11:45; 2025-07-03 not published) |
| 2020-07-03 | Independence Day (observed), halt 12:00 | same |
| 2023-07-03 | Day before Independence Day, halt 12:15 | same |

No other date is unsettled. The plan also lists "any other date whose equity entry is not an
ordinary holiday (an unscheduled closure such as a national day of mourning, a holiday name the
published years never carry)". I read "holiday name" as the holiday without its qualifier
("(observed)", "(abbreviated, jobs report)"): Topstep's schedules name holidays ("Juneteenth",
"Christmas") and publish observed days under them (2026-07-03, Independence Day observed, is
published and reproduced). Under that reading every 2019-05..2023-12 entry is ordinary (the test
computes the set from the equity names on Topstep's published dates). Under the stricter
full-name reading three more dates would be unsettled: 2021-12-24 and 2022-12-26 ("Christmas Day
(observed)", closures: no difference, every group's calendar closes them) and 2022-06-20
("Juneteenth (observed)", equity halt 12:00), where it matters. With the row (as written) every
trading group flattens at 11:30. Unsettled, fx and crypto would flatten at 15:08 (their calendars
list nothing that day), energy and metals at 13:00 (their 13:30 halt minus the 30-minute lead),
equity and rates at 11:30. This can change K4 and K5 confirmation figures, so it needs the lead's
confirmation (open point O-2).

On the unsettled dates themselves: on 2020-07-03 the unsettled status changes nothing (every
trading group's calendar lists a 12:00 halt, so the year's lead gives 11:30, the same as a row
would). On 2019-07-03 and 2023-07-03 rates, fx, energy and metals (and crypto on 2023-07-03) list nothing and trade to 15:08
(a row would give 11:45); equity flattens at 11:45 (12:15 minus 30).

### 3.3 The audit's 15 FX dates (6E; every FX root is the same)

13 of the 15 now flatten at the derived close-by 11:30. The two July 3s stay at 15:08 because the
plan's July 3 rule leaves them unsettled and the FX calendar lists nothing on them. The plan's
(iv) wording ("on the 15 FX dates ... the derived close-by (11:30 or 11:45) or closed, instead of
15:08") therefore holds for 13; the test pins 13 at 11:30 and 2 at 15:08 (open point O-3). A 14th
FX date the audit list does not name also changes: 2022-06-20 (Juneteenth observed), 15:08 to 11:30.

| Date | Equity entry | FX calendar | v4 F (6E) | v5 F (6E) | Why |
|---|---|---|---|---|---|
| 2019-07-03 | Day before Independence Day, halt 12:15 | none | 15:08 | 15:08 | unsettled July 3: no row; FX calendar lists nothing |
| 2022-01-17 | Martin Luther King Jr. Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2022-02-21 | Presidents Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2022-05-30 | Memorial Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2022-07-04 | Independence Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2022-09-05 | Labor Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2022-11-24 | Thanksgiving Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2023-01-16 | Martin Luther King Jr. Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2023-02-20 | Presidents Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2023-05-29 | Memorial Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2023-06-19 | Juneteenth, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2023-07-03 | Day before Independence Day, halt 12:15 | none | 15:08 | 15:08 | unsettled July 3: no row; FX calendar lists nothing |
| 2023-07-04 | Independence Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2023-09-04 | Labor Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |
| 2023-11-23 | Thanksgiving Day, halt 12:00 | none | 15:08 | 11:30 | derived close-by |

### 3.4 Energy early-halt dates 2019-05..2023-12 (CL; before v4, after v5)

| Date | energy calendar halt | Topstep row (v5) | v4 F | v5 F |
|---|---|---|---|---|
| 2019-05-27 | Memorial Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-07-04 | Independence Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-09-02 | Labor Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-11-28 | Thanksgiving Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-11-29 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2019-12-24 | Christmas Eve, 12:45 | 11:45 | 12:30 | 11:45 |
| 2020-01-20 | Martin Luther King Jr. Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-02-17 | Presidents Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-05-25 | Memorial Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-07-03 | Independence Day (observed), 12:00 | none (unsettled) | 11:45 | 11:30 |
| 2020-09-07 | Labor Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-11-26 | Thanksgiving Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-11-27 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2020-12-24 | Christmas Eve, 12:45 | 11:45 | 12:30 | 11:45 |
| 2021-01-18 | Martin Luther King Jr. Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-02-15 | Presidents Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-05-31 | Memorial Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-07-05 | Independence Day (observed), 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-09-06 | Labor Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-11-25 | Thanksgiving Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-11-26 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2022-01-17 | Martin Luther King Jr. Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-02-21 | Presidents Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-05-30 | Memorial Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-06-20 | Juneteenth (observed), 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-07-04 | Independence Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-09-05 | Labor Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-11-24 | Thanksgiving Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-11-25 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2023-01-16 | Martin Luther King Jr. Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-02-20 | Presidents Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-05-29 | Memorial Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-06-19 | Juneteenth, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-07-04 | Independence Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-09-04 | Labor Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-11-23 | Thanksgiving Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-11-24 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |

### 3.5 Metals early-halt dates 2019-05..2023-12 (GC; before v4, after v5)

| Date | metals calendar halt | Topstep row (v5) | v4 F | v5 F |
|---|---|---|---|---|
| 2019-05-27 | Memorial Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-07-04 | Independence Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-09-02 | Labor Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-11-28 | Thanksgiving Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2019-11-29 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2019-12-24 | Christmas Eve, 12:45 | 11:45 | 12:30 | 11:45 |
| 2020-01-20 | Martin Luther King Jr. Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-02-17 | Presidents Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-05-25 | Memorial Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-07-03 | Independence Day (observed), 12:00 | none (unsettled) | 11:45 | 11:30 |
| 2020-09-07 | Labor Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-11-26 | Thanksgiving Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2020-11-27 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2020-12-24 | Christmas Eve, 12:45 | 11:45 | 12:30 | 11:45 |
| 2021-01-18 | Martin Luther King Jr. Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-02-15 | Presidents Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-05-31 | Memorial Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-07-05 | Independence Day (observed), 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-09-06 | Labor Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-11-25 | Thanksgiving Day, 12:00 | 11:30 | 11:45 | 11:30 |
| 2021-11-26 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2022-01-17 | Martin Luther King Jr. Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-02-21 | Presidents Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-05-30 | Memorial Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-06-20 | Juneteenth (observed), 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-07-04 | Independence Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-09-05 | Labor Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-11-24 | Thanksgiving Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2022-11-25 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |
| 2023-01-16 | Martin Luther King Jr. Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-02-20 | Presidents Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-05-29 | Memorial Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-06-19 | Juneteenth, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-07-04 | Independence Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-09-04 | Labor Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-11-23 | Thanksgiving Day, 13:30 | 11:30 | 13:15 | 11:30 |
| 2023-11-24 | Day after Thanksgiving, 12:45 | 11:45 | 12:30 | 11:45 |

### 3.6 Other day_rule effects and the tests (ii)-(v)
- Totals, 2019-05-01..2023-12-31, all 8 groups, every weekday: 251 (group, date) results change on
  42 dates (equity 41, crypto 40, rates 39, fx 39, energy 37, metals 37, grains 9, livestock 9). Every
  change moves F earlier or closes the date; none moves it later (tested). 41 of the 42 dates are
  equity-calendar dates; the 42nd is 2020-07-02, where grains (12:05) and livestock (12:15) list an
  early halt the equity calendar does not ("Day before Independence Day (observed)"): the derived
  2020 lead gives ZC 11:35 (v4 11:50) and LE 11:45 (v4 12:00), exactly as the plan intends for such
  halts (the lead table), and pinned in the test.
- (iv) One derived early-close date per group: 2022-01-17 (MLK; equity halt 12:00, row 11:30) for
  equity, rates, fx, energy, metals and crypto, all 11:30; grains and livestock are CME-closed on
  MLK, so 2022-11-25 (day after Thanksgiving; row 11:45; their halt 12:05): 11:45. The test asserts
  F = min(regular F, group halt - 15, derived close-by), and also the plan's formula with
  "group halt - 30" wherever halt - 30 >= the close-by. Deviation (open point O-4): on a date with a
  row, the unchanged `day_rule` adds no "halt minus the year's lead" candidate (the lead applies only
  when the year's schedule has no row), exactly as on the published dates. For grains and livestock
  on the derived Fridays after Thanksgiving and Christmas Eves (12 group-dates) the plan's formula
  would give 12:05 - 30 = 11:35, the code gives the row's 11:45. The published year does the same
  (2025-11-28: ZC and LE 11:45, pinned in tests/test_e2a_rules.py and in the new file); adding the
  candidate would change 2024-2026 and break (v), so the code is unchanged. Not a K4/K5 question.
- Derived "markets closed" rows close every group (2019-12-25, 2021-12-24, 2023-01-02 tested).
- A group halt on a derived-year date without a row gets the 30-minute lead (synthetic energy halt
  13:30 on 2021-03-10: F = 13:00).
- (v) Every `day_rule` result (closed flag, F and reasons) for every group and every weekday
  2024-01-01..2027-12-31 equals the v4 result, computed in the test from a frozen literal copy of the
  v4 table (37 rows with source ids) and lead table monkeypatched into the module: 0 differences.
  The research window 2025-04-01..2026-06-19 is inside that range.

## 4. screening/stage_e_verdict.py (3b)

Imports only funnel.multiple_comparisons, funnel.null_generator, screening.harness_freeze,
screening.stage_e_stats (`holm_tier_a`), screening.stage_e_stats_power (`LABEL_INCONCLUSIVE`) and
screening.stage_e_stats_units (`frozen_epsilon`); nothing from strategy/ (tested by AST). Constants
as the plan lists them (BOOTSTRAP_SEED_BASE 20260923, BOOTSTRAP_RESAMPLES 10,000, MEAN_BLOCK_DAYS
5.0, UCB_QUANTILE 0.95, NULL_Z 1.645, NULL_POWER_MIN 0.80, INACTIVITY_MIN 30, HOLM_K 9, DSR_MIN
0.95, T_MIN = HLZ_HURDLE 3.0, PBO_MAX 0.5, N_PBO_BLOCKS 8) and the five labels.

### 4.1 Restated D.1f functions and their counterparts (equality tested)

| stage_e_verdict | D.1f / D.1b counterpart | Equality test |
|---|---|---|
| `resampled_means(daily, n_resamples, seed, mean_block=5.0)` | `_d1f_decisions.resampled_means` | array-equal, 3 seeds at B = 500 and one at B = 10,000 |
| `summarize_means(daily, means)` -> `Bootstrap` | `_d1f_decisions.summarize_means` | every field equal (n_days, theta_hat, ucb95, se_boot, p_upper, p_lower) |
| `null_power(se_boot, epsilon)` (epsilon required) | `_d1f_decisions.null_power` | 6 cases incl. SE = 0 |
| `moments(xs)` | `_d1b_accounting._moments` | 4 series incl. sd = 0 |
| `blocks(series)` | `_d1b_accounting._blocks` | same 4 series |
| `dsr(mom, n_trials, variance)` | `_d1f_decisions._dsr` | 5 series incl. flat |
| `t_stat(mom)` | `_d1f_decisions._t_stat` | same |
| `dsr_table(moms, variance_over, n_trials, members)` | `_d1f_decisions.dsr_table` | dict-equal |
| `pbo(series)` | `_d1f_decisions.pbo` | dict-equal on three aligned series |
| `aligned_series(dates, values, window_dates)` | `_d1f_decisions.aligned_series(member, window)` | array-equal, 3 date sets |
| Holm: `screening.stage_e_stats.holm_tier_a(p, 9)` (harness) | `_d1f_decisions.holm(p, alpha=0.05/9)` | reject pattern equal, 4 p-sets |

### 4.2 New public functions (no D.1f counterpart)
- `parse_list(payload) -> ConfirmationList`: the hashed list schema of the plan; every field read
  is checked.
- `record_name(cluster, member)`: the runner's file name `<cluster>_<member>_confirmation.json`
  through the runner's `_safe` (equality tested).
- `check_record(record, trial, clist) -> Series | None`: refusals by name; the series of a "run"
  record, None for any other status.
- `trial_figures(series, eps_ticks, seed, n_resamples=10000)`: theta_hat, UCB95, SE_boot, p_upper,
  n_days, n_trips, trips per day r, theta_hat / r and UCB95 / r, null power, `ucb_below_eps`,
  `power_ok`, status and reasons.
- `edge_chain(clist, rows, series)`: Holm, composite "pending", DSR (V14 c switch), t, PBO (L-E5-3
  switch); per Tier A trial the verdict, first failing step and every step's result.
- `null_statement(clist, rows, chain)`: "null" or "no statement", covered, not covered with reason,
  blocking trials with status, reasons and their chain verdict, "null by inactivity" trials.
- `resolution_table(clist, rows)`: per vehicle eps_X ticks and $ at q_c, q_c, fewest-trip covered
  trial and count, largest UCB95 / r over covered trials, inactivity labels, trials not covered.
- `evaluate(list_payload, records, n_resamples=10000)`: the whole verdict dict (schema
  `stage_e_confirmation_verdict/1`); `n_resamples` is for tests, the CLI always uses 10,000.
- `load_records(dir, list_payload)`, `write_verdict(verdict, out)` (open "x": written once),
  `main(argv)`: `python -m screening.stage_e_verdict --harness-sha256 SHA --list LIST.json --records
  DIR --out OUT.json`; `harness_freeze.preflight` first, then the output-exists check, the list
  (its harness_sha256 must equal the preflighted one), the records (trip files are not read), one
  JSON with the list's sha256 and file name added. A refusal prints "REFUSED (...)" to stderr and
  returns 2.
- `VerdictRefusal(ValueError)`.

### 4.3 Refusals
The plan's: record harness sha256, cluster freeze sha256, member, ordinal, window, S_X (and cluster,
schema) differing from the list; a trial marked run without a record; a record not in the list
(both in `evaluate` and, for files of the cluster in DIR, in `load_records`); series dates not
strictly increasing; a non-finite value; K not 9; seed base not 20260923. Added, each refusal-only
(none can change a figure): the list's resamples, mean block or quantile differing from the
constants; `bootstrap_seed` not seed base + ordinal; a trial's vehicle, eps_ticks, q_c or $ figure
differing from the frozen E.2a epsilon table; an unknown label (allowed: "source-overlap",
"calendar partly unverified", "inconclusive by design" and the runner's four D9 labels); tier and
run disagreeing (Tier A and B are run, "excluded" is not); duplicate member or ordinal; series dates and values misaligned; series vehicle not the list's; negative
n_trips; a list for another harness sha256; an existing output file. An excluded trial's record
(the runner's `--all` runs every frozen member, so one may exist) is checked like any other and
never used: its row says so, it enters no Holm, DSR or PBO set and blocks nothing.

## 5. Known-answer tests (tests/test_stage_e_verdict.py, 86 tests, 2.1 s)

| Test | What it pins |
|---|---|
| `test_summary_known_answer_on_a_given_means_array` | theta_hat 50; means 1..100: UCB95 = 95.05 (linear quantile), SE_boot = sqrt((100^2 - 1)/12), p_upper = 2/101 |
| `test_null_power_known_answers` | Phi(0) = 0.5 at eps/SE = 1.645; 0.80 at eps/SE = 1.645 + z_0.80; 0 at SE = 0 |
| `test_constant_series_has_se_zero_and_is_inconclusive` | constant 2.5: UCB = theta = 2.5, SE = 0, p = 1/(B+1), status inconclusive ("SE_boot = 0", power < 0.80) |
| `test_zero_trips_is_inconclusive_not_null` | zero trips: inconclusive, p = 1, per-trade figures None |
| `test_null_and_null_by_inactivity` (3 cases) | alternating +-1 at eps 8: null at 40 and 30 trips, "null by inactivity" at 29; r and UCB95 / r |
| `test_ucb_at_or_above_eps_is_inconclusive` | mean 10 > eps 8: inconclusive with the single reason UCB95 >= eps_X; theta / r = 12.5 |
| `test_low_power_alone_is_inconclusive` | theta -20, SE about 10: UCB < eps but power < 0.80: inconclusive for power alone |
| `test_the_trial_seed_is_base_plus_ordinal_and_b_is_10000_by_default` | seed 20260923 + 4, B = 10,000 through `evaluate`; figures equal a direct bootstrap |
| `test_holm_with_one_tier_a_trial_at_k9` | m = 1, alpha_k = 0.05/9, p = 1/1001 rejects |
| `test_holm_with_three_tier_a_trials_at_k9` | thresholds alpha_k/3, /2; two strong trials reject, a mean-0 one does not; given p (0.001, 0.002, 0.004) all reject, (0.001, 0.003, 0.004) only the first |
| `test_dsr_variance_with_one_tier_a_trial_is_over_every_run_trial` | V14 (c): variance over A + B + B = pvariance of the three Sharpes; DSR = deflated_sharpe_ratio(sharpe, n, 150, var, skew, kurt) |
| `test_dsr_variance_with_two_tier_a_trials_is_over_tier_a` | variance over the two Tier A trials only |
| `test_t_is_the_hlz_t_on_the_population_sd` | t = mean / (pstdev / sqrt(n)) |
| `test_pbo_with_one_tier_a_trial_is_over_every_run_series_on_the_union_of_dates` | L-E5-3: PBO over A, B, B; three unequal windows aligned on their 260-day union, 0 off own dates, blocks of 32; equals a hand-built CSCV |
| `test_pbo_with_two_tier_a_trials_is_over_tier_a_aligned_on_every_run_trial` | PBO over the two Tier A series, aligned on the union of every run trial's dates (reading O-5) |
| `test_pbo_is_undefined_with_a_single_run_series` | one run series: PBO undefined, the chain fails at "pbo" though Holm and t pass |
| `test_the_passing_wording_the_source_overlap_wording_and_never_edge_alone` | "edge candidate, composite pending"; the source-overlap sentence; composite "pending"; no verdict reads "edge"; an above-eps edge candidate blocks the statement and carries its chain verdict |
| `test_a_failing_chain_names_its_first_failing_step` | first failing step in the order Holm, DSR, t, PBO |
| `test_an_all_null_cluster_gets_the_statement_and_the_resolution_table` | "null"; inactivity label; per vehicle eps ticks/$/q_c (NG 8/80.0/1, MCL 21/4), fewest trips (K4-b, 12), largest UCB95 / r |
| `test_inconclusive_by_design_and_excluded_trials_are_not_covered_and_block_nothing` | by-design trial keeps its figures, not covered; excluded trial "not run"; statement "null"; both named with reasons |
| `test_an_inconclusive_trial_keeps_the_cluster_out_of_the_statement` | "no statement", naming the trial and its reason |
| `test_a_run_record_without_a_series_is_inconclusive_and_blocks` | a "refused_case" record: inconclusive, blocks, enters Holm at p = 1 with m = 2 (open point O-6) |
| `test_the_verdict_carries_the_constants_and_the_hashes` | schema, harness and freeze sha256, program N, K |
| `test_an_excluded_trials_record_is_checked_and_never_used` | an excluded trial's record: "not run", no figures, in no run set, the statement unaffected; a mismatching one is refused |
| refusal tests (10 + 1 with 2 checks + 6 + 8 + 7 + 1 cases) | every refusal in 4.3 |
| CLI tests (4) | preflight first (called before the list is read; a failing preflight leaves nothing written); written once (second run returns 2); list sha256 and file name carried; trip files never read (they hold invalid JSON); another cluster's record ignored; a cluster record not in the list refused |


## 6. Full suite

Command (PYTHONPYCACHEPREFIX unset, once, 12:56:16 to 13:07:24 PDT):
`env -u PYTHONPYCACHEPREFIX nice -n 10 uv run pytest -q > <scratch>/pytest_full.out 2>&1`. Tail, verbatim:

```
FAILED tests/test_e4_k3_members_b.py::test_every_source_file_has_the_pinned_sha256
FAILED tests/test_e4_k3_members_b.py::test_both_modules_are_exactly_the_generators_output
FAILED tests/test_e4_k3_members_b.py::test_fx_full_sessions_are_ec_cal_dates_without_halt_and_with_the_regular_f
FAILED tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists
4 failed, 4147 passed, 2 skipped, 1 xfailed, 54 warnings in 666.13s (0:11:06)
```

Start of stage: 4043 passed, 2 skipped, 1 xfailed. 4043 + 108 new tests (21 holidays, 85 verdict as
collected, 2 step 2) = 4151 = 4147 + 4. The four failures are the expected ones and nothing else:
the three K3 table pins (O-1) and the manifest test (O-8), whose mismatch list is exactly
data/config.py, data/pull_step2.py, rules/sessions.py and tests/test_e2b_pull_step2.py (sha256
differs) and screening/stage_e_verdict.py (not listed). The suite is therefore not green, and it
cannot be made green inside my file list without the K3 decision (O-1) and the lead's A4 rebuild.

After the run started (collection had finished) two small edits were made: the excluded-trial
record handling in screening/stage_e_verdict.py with its test (the file now has 86 tests, re-run
alone: `86 passed in 2.12s`) and a docstring reflow in data/pull_step2.py (no code). The earlier
targeted runs: tests/test_stage_e_sessions_holidays.py 21 passed; tests/test_e2b_pull_step2.py
41 passed in 81.9 s; the session-dependent subset (tests/test_stage_e_*, test_e3_*, test_e4_*,
test_e2a_*, test_cross_platform_static, test_ml_route_*) 12:45-12:50: 2799 passed, 3 failed (the
same three K3 tests). ruff: all changed and new files pass (data/config.py:98's E501 predates E.5).


## 7. Deviations and open points (for the lead)

- **O-1 (STOP item, K3).** The Read-first paragraph at the top: three tests in tests/test_e4_k3_members_b.py pin the v4
  rules/sessions.py (sha256 and the FX_FULL_SESSIONS table K3's frozen _calendar.py was generated
  from). v5 removes 14 dates from what the engine treats as full FX sessions; the frozen K3 table
  still lists them. Not changed by me: K3 member code is frozen and the test rewrite is a decision
  about K3's inputs. Options the lead has: keep K3's table (the members plan events on 14 dates the
  engine now closes at 11:30) and re-pin the test to the v4 source; or treat it as a K3 member issue
  for a K3 session. Under the strict holiday-name reading (O-2) the list would be 13 dates.
- **O-2 (can change K4/K5 figures).** "Ordinary holiday" read as the holiday without its
  qualifier; the strict full-name reading would make 2022-06-20 (Juneteenth observed) unsettled:
  energy and metals F 13:00 instead of 11:30, fx and crypto 15:08 instead of 11:30 (3.2).
- **O-3.** The plan's July 3 rule leaves 2019-07-03 and 2023-07-03 unsettled, so 2 of the audit's
  15 FX dates stay at 15:08 (3.3); rates, energy and metals likewise. On 2020-07-03 the unsettled
  status is immaterial.
- **O-4.** (iv)'s formula with "group halt - 30" differs from the unchanged `day_rule` on the 12
  grains/livestock derived Fridays after Thanksgiving and Christmas Eves (11:35 against 11:45); the
  code matches the published years and (v) forbids changing it (3.6).
- **O-5 (PBO alignment; can change a PBO figure when Tier A has two or more trials with different
  windows).** The union of window dates is taken over every run trial with a series, also when PBO
  is over Tier A only (read from "aligned on the union of the run trials' window dates"); the
  alternative is the union over the PBO set only. Pinned by
  `test_pbo_with_two_tier_a_trials_is_over_tier_a_aligned_on_every_run_trial`.
- **O-6.** A Tier A or B trial whose confirmation record is not "run" (the runner's
  "refused_case" or "excluded_before_screening" on the confirmation window) has no series: it is
  inconclusive and blocks the statement (NULL_CRITERIA_E 6: no evidence), and a Tier A one enters
  Holm at p = 1, keeping the family size m. The switches (DSR variance, PBO set) count Tier A trials
  with a series.
- **O-7.** Plan counts: the published table has 37 rows, not 38; the rule reproduces 35 of the 36
  rows in its domain, and 2027-01-01 is outside the domain (the equity calendar ends 2026-12-25).
  The four exceptions are exactly the plan's.
- **O-8.** tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_
  exists fails until the lead rebuilds the manifest in A4 (four listed files differ from v4
  82ae8536..., screening/stage_e_verdict.py is unlisted; the two new test files match
  TEST_PATTERNS and join at the rebuild). Expected.
- **O-9.** Setting the E.5 caps in B1 edits data/config.py, a harness file: done after the v5
  freeze it changes the manifest and `--buy`'s preflight refuses. Three tests pin the 0.00 caps
  and follow that edit: `test_the_step2_gate_reads_the_e5_block_and_refuses_to_buy_at_its_zero_caps`,
  `test_the_buy_refuses_to_start_with_the_active_zero_caps` and
  `test_quote_only_issues_no_billable_request_and_ledgers_zero_lines_on_acct2` (its payload cap
  assertion).
- **O-10.** data/pull_step2_report.py:39 still prints "(quotes only)" beside the request cap in the
  quote markdown. Outside my file list; cosmetic; left.
- **O-11.** screening/harness_freeze.py's ENTRY_MODULES does not name screening.stage_e_verdict. It
  lies in screening/, so the manifest build lists it, and it imports only harness files; the plan
  keeps harness_freeze.py unchanged.
- Decided by me, none able to change a verdict figure: the extra refusals of 4.3; the excluded
  trial's record checked and unused; `evaluate`'s `n_resamples` test parameter; the verdict JSON
  schema name and fields; the CLI's return code 2 on refusal; `TOPSTEP_UNSETTLED_DATES` as
  (date, reason) pairs; `TOPSTEP_DERIVED_FIRST/LAST` constants; the source id's comment.

## 8. Lead follow-up (rulings R-A2-1, R-A2-2), 13:12-13:25 PDT

Accepted without change by the lead: O-2 (2022-06-20 keeps its derived row), O-3, O-4 (day_rule
governs), O-5, O-6, O-7, O-10, O-11.

- **R-A2-1 (O-1, K3), tests/test_e4_k3_members_b.py.** K3 member code is untouched. The three
  failing tests (`test_every_source_file_has_the_pinned_sha256`,
  `test_both_modules_are_exactly_the_generators_output`,
  `test_fx_full_sessions_are_ec_cal_dates_without_halt_and_with_the_regular_f`) carry
  `@pytest.mark.xfail(strict=True, reason=V5_XFAIL_REASON)` with their bodies unchanged; the reason
  is the ruling's text verbatim. New test
  `test_v5_flattens_exactly_14_frozen_full_fx_sessions_all_before_2024`: the frozen
  FX_FULL_SESSIONS dates whose v5 F for 6E is not 15:08 equal exactly the 14 dates of the ruling;
  each has a derived row (source `topstep_derived_e5_equity_calendar`, close-by 11:30 = F) and lies
  before 2024-01-01. Run alone: `44 passed, 3 xfailed in 2.01s`.
- **R-A2-2 (O-9), tests/test_e2b_pull_step2.py.** No test pins the config's cap values now. A
  `set_caps` helper monkeypatches `data.pull_step2.STEP2_SESSION_CAP_USD` and
  `STEP2_REQUEST_CAP_USD`. `test_quote_only_issues_no_billable_request_and_ledgers_zero_lines_on_acct2`
  asserts the payload caps equal the active caps, whatever they are.
  `test_the_buy_refuses_to_start_with_the_active_zero_caps` sets them to 0.00 first. The E.5
  section is rewritten: `test_the_step2_gate_is_the_e5_session_on_acct2_and_reads_the_active_caps`
  runs at (0.00, 0.00) and (21.52, 3.00): the session is "stage-E.5-2026-09-27" on acct-2, the gate's
  caps are the patched values, the buy start check refuses at 0.00 and passes at the positive caps.
  `test_the_buy_refuses_before_any_vendor_call_at_zero_caps`: RC_REFUSED after the preflight, no key,
  no client, empty ledger. `test_quote_only_ledgers_only_zero_lines_under_the_e5_session` runs at
  both cap pairs: only $0.00 quote lines on acct-2 under the E.5 id, payload caps = the patched
  pair. The E.2b pin keeps its session id only. Run alone: `44 passed in 77.86s`. Also checked
  with an in-process pytest plugin that set the config's E.5 and active caps to 21.52 / 3.00 before
  import, as a Task B1 edit would (no file edited): the 7 cap-related tests `7 passed, 37 deselected
  in 63.36s`.
- Files touched in the follow-up: tests/test_e4_k3_members_b.py, tests/test_e2b_pull_step2.py, this
  report. No full-suite run (the lead runs it after the A4 rebuild). ruff: both files pass.

## 9. Lead follow-up 2 (Fable review fixes, reports/stage_e5_harness_review.md), 13:30-13:45 PDT

1. **SF-1**, screening/stage_e_verdict.py:105 (`DSR_VARIANCE_UNDEFINED`), :503-507 (`edge_chain`),
   :518: when the V14 (c) variance set has fewer than 2 series no DSR is computed (no
   pvariance of one value). The chain's `dsr` block reads `{"variance_over": [...], "undefined":
   "variance over fewer than 2 series (V14 c)"}`, the trial's `dsr` is None, its `dsr_undefined`
   carries the reason, and it fails the DSR step. Known answer:
   tests/test_stage_e_verdict.py:401 `test_a_single_series_cluster_has_no_dsr_the_variance_is_undefined`.
   The case is one strong Tier A trial plus a Tier B trial with no series. Holm and t pass, DSR is
   undefined, and the verdict is "no edge (dsr undefined)". The test also shows the trap: the old
   path's variance of 0.0 gives an undeflated DSR above 0.95.
2. **N-4**, screening/stage_e_verdict.py:103-104 and `_chain_verdict` :522-549: a first failing
   step "dsr" or "pbo" whose value is undefined reads "no edge (dsr undefined)" or "no edge (pbo
   undefined)". Each trial row carries `dsr_undefined` and a new `pbo_undefined`. Tests: :401 (DSR),
   :433 `test_an_undefined_pbo_reads_no_edge_pbo_undefined` (two strong Tier A trials on 6 days:
   Holm, DSR and t pass; "6 days cannot form 8 blocks"), and :452 (a defined failing DSR stays
   plain "no edge"). The review's N-4 case, one run series, now fails first at DSR (SF-1), so the old
   `test_pbo_is_undefined_with_a_single_run_series` is replaced by :401, which also checks the PBO
   reason.
3. **N-5**, screening/stage_e_verdict.py:313-319 (`_trial`): `frozen_epsilon`'s KeyError becomes
   `VerdictRefusal("<member>: vehicle 'ES' has no operative eps in the frozen E.2a epsilon
   table")`, and a missing vehicle is refused too. Test :747
   `test_cli_refuses_an_unknown_vehicle_by_name`: rc 2, "REFUSED (VerdictRefusal)" and 'ES' on
   stderr, nothing written.
4. **N-6**, screening/stage_e_verdict.py:87-88 (`SERIES_UNIT` = the runner's literal "net ticks per
   contract per day", `CONFIRMATION_LAST` = 2024-02-29), :411-412 (unit) and :429-434 (first date
   before the list's S_X of the trial's primary vehicle, or no S_X for it; last date after
   2024-02-29), `_series` now takes the list. Tests: the bad-series parametrization (:623, :647)
   gains "unit", "before_s_x" and "after_2024_02_29"; :212-215 pin the unit to the runner's source
   literal and `CONFIRMATION_LAST` to data.stage_e_bars.CONFIRMATION_LAST_TRADE_DATE. The fixture
   `record()` (:88-89) now starts a series at its vehicle's S_X (MCL 2021-06-01).
5. **SF-2**, tests/test_e4_k3_members_b.py:337-434: the three xfail markers and the reason constant
   are removed. `V4_SESSIONS_SHA256` and `V5_SESSIONS_SHA256` (:343-344, comment naming R-A2-1 and
   SF-2) are pinned literally; the v5 value is beb9501d6235299cd716868a8c14cf1df1b3cc71fa0b58c4e9780e9035b07d28,
   the sessions file after item 6. The review's a7401d70... predates that docstring edit.
   (a) :351: every pinned source matches; K3's own pin of rules/sessions.py is still v4's, and the
   file equals v5's. (b) :375, with deviation D-F2 below: `_clocks.py` regenerates exactly.
   `_calendar.py` differs in exactly three names, all from the 14 dates: FX_FULL_SESSIONS loses
   them, FX_EARLY_F_DATES gains them, and SOURCE_SHA256's rules/sessions.py entry becomes v5's.
   Every other value is equal, and every other changed text line is a date-table line, the sha
   line or one of the two "(N dates)" count comments. (c) :410: the K3-L-11 rule holds for every
   frozen date except the 14; there are 1797 - 14 full sessions, and "removed" is the frozen
   FX_EARLY_F_DATES plus the 14. The research-window checks are unchanged. The pinned-difference test (:437) is kept.
6. **N-1**, rules/sessions.py:35-38 (docstring only): the rows cover trade dates
   2019-05-01..2023-12-31, but the 2019-2023 lead is keyed by calendar year, so it also moves the
   equity F on 2019-01-21 and 2019-02-18 (halt 12:00: 11:45 to 11:30), before any store's first bar
   (2019-05-06). Checked: `flatten_time_ct("NQ", ...)` gives 11:30 on both dates.

**Deviation D-F2 (SF-2 (b)).** The ruling asks that the regenerated `_calendar.py` differ "exactly
on the FX_FULL_SESSIONS table ... everything else ... equal". Under v5 the generator necessarily
also changes FX_EARLY_F_DATES (its complement: the same 14 dates move there) and the
rules/sessions.py sha256 in SOURCE_SHA256, with the two count comments. I verified this by
regenerating in memory; no file was written. The test pins all three differences exactly. The
substance is the ruling's (the 14 dates and nothing else), and no verdict figure is affected.

Results, each file run alone (13:41 PDT):
- tests/test_stage_e_verdict.py: `92 passed in 1.54s`
- tests/test_stage_e_sessions_holidays.py: `21 passed in 0.12s`
- tests/test_e4_k3_members_b.py: `47 passed in 1.05s`

ruff passes on every file touched. Files touched in this follow-up: screening/stage_e_verdict.py,
tests/test_stage_e_verdict.py, tests/test_e4_k3_members_b.py, rules/sessions.py (docstring), this
report. No full-suite run.
