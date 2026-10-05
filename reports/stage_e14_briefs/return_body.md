# Stage E.14 return: C1 frozen and ready, awaiting funds; C2 stopped at its power rule; nothing bought

Lead Opus 5.5 xhigh, 2026-10-05 00:26 to {{END_TIME}} PDT, session 19c73927. Prompt docs/prompts/STAGE_E.14.md
(revision V26). STATE: reports/stage_e14_STATE.md. Times are PDT unless marked UTC.

## 1. Verdict summary

**C2 (dealer-gamma-conditioned late-session momentum): STOPPED** at its minimum-power rule (draft section 7),
before its freeze, registration and purchase. Only 135 eligible 2011-05-03..2019-04-30 dates had GEX < 0
(lag 1, share 6.8%), against the floor of 200. No calendar can lift it above 146. Two implementations agree, and
Fable recomputed it independently. The draft expected about 48% negative days, the paper's share for its own
NGE measure; SqueezeMetrics' GEX is negative far less often. No T1 or T2 statistic exists, no ES bar was read,
and nothing is learned about the effect. Per section 7, the user decides C2's next step.

**C1 (backward NG replication): FROZEN, AWAITING FUNDS.**
- The calendar probe passed: 0 of 258 energy dates and 0 of 52 NGS dates unsourced in 2012.
- Six 2010-2019 CME group calendars have 0 unsourced dates. The release calendar has 1 unsourced time.
- Freeze reports/stage_e14_prereg_C1.md: sha256 afc5c10f..., commit 1680982.
- The q reproduction is exact: E.12's NG h60 row (518 trades, t_B 2.5143) and hF row (494 trades, t_B 2.3299)
  rebuild with differences of 0.0.
- q_h60 = 0.033735277284776724 and q_hF = 0.0831931045522869.
- M1 payload sha256s: 9c2d9986... (h60) and 153c2bdc... (hF). Fable reran both bit-identically.

**Money:** bought nothing; spent $0.00 (738 quote lines at $0.00). Funds: acct-1 $1.61, acct-2 $18.07. C1's
fresh quote is $57.742330 (x 1.03 = $59.474600). The top-up it needs is $41.404330: ACCOUNT_2_CAP_USD to $291.08
or more.

**Hashes:** harness v10 fde3a49c... (commit dc93e9b); C1 freeze afc5c10f... (commit 1680982); C1's input list
3356d676.... **N stays 471**: nothing was registered.

## 3. Results per task

### Task 0: startup
HEAD 77be2a9, clean apart from the E.12/E.13 DO_NOT_COMMIT page folders. Holdouts all_ok with 0 unlocks.
Start suite: 6505 passed, 2 skipped, 3 xfailed (E.12's end state). ~/.cache/propexp_e12_phase1 present (51
files).

### Task 1: the calendar probe (reports/stage_e14_probe.md)
- 2012 energy: 258 trade dates, 0 unsourced, all graded "cme". The session was 17:00-16:15 CT; holiday halts
  12:15 CT; Sandy left energy on regular hours.
- 2012 NGS: 52 releases, 0 unsourced. One release (2012-12-28) rests on EIA's schedule alone.
- Rule ruled at 01:36: it does not fire under any reading the rule defines (open choice 15).

### Task 2: calendars (reports/stage_e14_calendars.md)

| Group | Trade dates | Closures / halts / late opens | Unsourced (2010-06-07..2019-04-30) |
|---|---|---|---|
| Equity | 2,325 | 24 / 78 / 6 | 0 of 2,298 (C2's window 0 of 2,064) |
| Rates | 2,324 | 25 / 97 / 6 | 0 of 2,297 |
| FX | 2,325 | 24 / 96 / 6 | 0 of 2,298 |
| Energy | 2,323 | 26 / 73 / 0 | 0 of 2,296 |
| Metals | 2,323 | 26 / 73 / 0 | 0 of 2,296 |
| Grains | 2,269 | 80 / 23 / 25 | 0 of 2,243 |

- Release calendar: NGS 470 (C13 drops 0), WPSR 470, FOMC 72. One WPSR time is unsourced (2012-11-01); its NG
  date is excluded.
- Energy full sessions: 2,250.
- Every 2% stop is clear.
- Accepted limit: CME's weekly Globex notices were not read one by one.

### Task 3: the GEX file (reports/stage_e14_gex.md)
- Terms read first; ruled that they do not forbid one download of the offered file.
- The CSV was fetched once at 07:43:01 UTC: sha256 51bef9ea..., kept uncommitted and git-ignored.
- Timing rule: lag 1. Evidence: the server's Last-Modified and same-evening captures (a Monday 08:19 CT capture
  holds Friday's row).
- The 2011-2019 rows are unchanged since 2020.
- Count 135 < 200: C2 stopped at 01:34.

### Task 4: harness v10 and the freezes
- **v10** (dc93e9b, manifest fde3a49c...; v9 was 7fd757f6...). 3 files changed, 19 added.
  - Contents: the E.14 caps (all 0.00, acct-2 cap unchanged at 249.67); the es2011 and ext2010 plans, stores and
    loader; the hist calendar loader with the six calendars; C2's inert code; the trial registry (baseline
    N = 471).
  - Full suite on the candidate: 6737 passed. Diff against v9: `git show --stat dc93e9b`.
- **C1's freeze** (1680982): the draft plus V25 item 1, V26, the E.14 facts and the FreezeReviewer's fixes (seven
  listed changes).
  - Code c1_replication/ (75 synthetic tests).
  - E.12's state hashed (51 files) with a read-only copy.
- **C2: not frozen** (stopped in Task 3).

### Task 5: M1 and q (reports/stage_e14_c1_model.md)
- Run 03:29:54-03:29:57, after the freeze commit; no 2010-2019 byte exists.
- Reproduction exact. q and M1 are as in section 1.
- 150 features, feature_cols sha256 af7d43d6...; the ML ledger unchanged.
- C1 is FROZEN, AWAITING FUNDS. The later session's exact steps and hashes are in that file's section 4.

### Task 6: quotes, registration and purchase (reports/stage_e14_purchase.md)
- Fresh quotes ($0.00 lines on acct-2): ES $10.109048 (96 of 96 chunks, would have fitted) and C1 $57.742330
  (642 of 642).
- No registration, no purchase. The holdout status at the post-purchase point (03:07) is all_ok, 0 unlocks.
- C1's top-up: $41.404330.

### Task 7: evaluations (reports/stage_e14_c2_result.md, .json)
- C2: STOPPED at the power rule.
- C1: not evaluated in this stage.

## 4. Delegation record

| Agent (description) | Agent file | Model | Effort | Start | End | Tokens | Status |
|---|---|---|---|---|---|---|---|
{{DELEGATION_ROWS}}

## 5. Verification

Both Fable passes: reports/stage_e14_review.md. Rulings: reports/stage_e14_rulings.md.

- **Freeze review** (FreezeReviewer-FableXHigh, 03:06-03:26): APPROVE WITH FIXES (1 BLOCKING, 2 SHOULD FIX,
  12 NOTE).
  - F-01 BLOCKING: the later-harness clause ignored four tests that pin the caps. Fixed in the C1 freeze text and
    the README.
  - F-02: the C7 sentinel bar is now stated in the freeze text.
  - F-03: the CSV is git-ignored.
  - F-04/F-05: the later session's scripted input check and git-state check were added as text.
  - F-08: the Wayback CSV copies are recorded as a deviation.
  - F-10: times corrected to 01:34.
  - No code change was required. The fixes changed the manifest (a comment), the input list and the freeze sha;
    each was rebuilt in that order.
- **Verification** (VerdictVerifier-FableXHigh, 03:30-03:39): every verdict number MATCHES.
  - C2: 135, the bound 146, the stop. The strictest timing reading gives 131, which also stops.
  - C1: q, both M1 payloads and feature_cols bit-identical on an independent rerun.
  - The order of events in git, the ledgers and the files.
  - F-V1 SHOULD FIX: the terms ruling now states the curl and Wayback fetches. NOTEs F-V2 to F-V5 were recorded or
    applied.
  - F-V6 incident: the verifier's first `head` printed two GEX rows' values. That came after the stop; nothing was
    derived from them. It is disclosed for any future C2-like test.

## 6. Open choices (every decision the lead made on its own)

{{OPEN_CHOICES}}

## 7. Decisions for the user (the lead's recommendation first)

1. **C2's next step.** Recommendation: **close C2 as specified.**
   - Its rule cannot reach 200 trades on SqueezeMetrics' GEX.
   - Any rescue (a threshold other than zero, a GEX quantile, or the paper's own NGE construction) is a new
     hypothesis. It would need a new pre-registration counted in N.
   - The sign count, and now two rows' values, have been seen. A threshold chosen to reach 200 would be informed
     by the data.
   - The unconditional T2 alone was never a C2 pass, and the program's related price-only tests were null.
   - Alternative: a new pre-registration on a GEX quantile, decided before any price is read. The lead rates it
     low value.
2. **C1's top-up and completion session.**
   - Recommendation: if the user keeps searching, top up acct-2 by at least $41.41, plus a cushion for quote
     drift, say $45-50 (ACCOUNT_2_CAP_USD to $291.08 or more). Then run one completion session of about 1-1.5
     hours.
   - That session: verify the 43 inputs, the freeze and M1; raise the two caps (and the asserts that pin them);
     quote; register (N 471 -> 473); buy; build; evaluate once; Fable recomputes.
   - Everything else is built and frozen. The odds of a pass are about 12% (7-35%), and a pass is evidence, not a
     deployment verdict (freeze section 8).
   - If the user would rather not spend, C1 can wait frozen indefinitely; nothing in it expires. The E.12 state
     copy must be kept.
3. **Before the AiTrader readout (2026-10-23 at the earliest).** Recommendation: nothing else is required. The
   only open item is C1's completion session, which is independent of AiTrader. Absent the top-up, pausing until
   the readout costs nothing.

## 8. Session cost

{{COST}}
