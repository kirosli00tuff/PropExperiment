STAGE E.31 "VOLUME CHECK, THEN A ZM ORDER-BOOK PILOT ON THE TEMPORARY ACCOUNT"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.28's frozen QM pilot is dropped before any purchase (V48).
External research found QM to be a thin satellite of CL, and ZM (CBOT
soybean meal) to be the best standalone candidate. ZM's fees are 0.53 to
0.61 tick a round trip at Topstep, Lucid, Bulenox and MFFU, and no firm
restricts it around news. This stage:
- Part 1: buys daily volume for QM and ZM for a few cents, under fixed
  kill rules;
- Part 2: freezes a new ZM pilot spec;
- Part 3: builds and tests the pilot code;
- Part 4: has the spec and code reviewed, then spends the rest of acct-3
  on ZM order-by-order data plus soybean (ZS) and soybean oil (ZL) top of
  book;
- Part 5: runs the pilot measurement if time allows.
Nothing is registered and N stays 538. The pilot measures fills and
markouts, never a strategy's P&L.

Decisions in force: docs/DECISIONS.md V20 to V48. Binding: this prompt,
reports/stage_e28_pilot_spec.md (its rules, reused unless this prompt
changes them), V37.

Read first (inputs):
- docs/DECISIONS.md V46 to V48
- reports/E.28_RETURN.md sections 1 and 7, and reports/E.29_RETURN.md
  sections 1 and 7
- reports/stage_e28_pilot_spec.md and the code it froze,
  reports/stage_e28_briefs/work/B_pilot/
- reports/stage_e30_request.md and reports/stage_e30_briefs/ (E.30's
  unfinished request and pull script; nothing was bought)
- the planning chat's research summaries in reports/stage_e31_inputs/
  (written by the planner; treat them as pointers to verify, not as facts)

Lead: Opus 5.5, effort xhigh.
- On Max: Ultracode on, Fable xhigh reviews.
- On Pro: Ultracode off, reviews by Opus 5.5 xhigh in a fresh context
  (V46 item 5).
- At most 4 workers at once.

Time: launched about 08:00 PDT on 2026-10-22. Work stops at 23:00 PDT and
the return is written by 23:30. Checkpoint reports/stage_e31_STATE.md after
every step. After a usage limit, resume from it.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
KEYS AND SPEND (FIXED HERE)
============================================================

- Only acct-3 (DATABENTO_API_KEY3) exists in .env now. The user removed
  the KEY1 and KEY2 lines. Check presence by NAME only; never read, print,
  copy or log any key.
- Every Databento call goes through SpendGate with account="acct-3" and
  this session's own id, with a fresh logged quote before each purchase.
- The total spend bound is all of acct-3's funds under its USD 125 cap
  (V45, V46, V48).
- acct-3's pilot-only guard stays in place. Route the Part 1 purchase
  through the pilot path, or make a minimal change to the guard reviewed
  in Part 4. Do not remove the guard.
- Data goes under /mnt/large-storage/market_data/PropExperiment/ with a
  sha256 manifest.
- No date on or after 2024-03-01 for ZM, ZS or ZL in Parts 2 to 5. Recent
  data needs a separate user approval, which is not given.
- When the last purchase is verified, write "ACCOUNT_3 SAFE TO WIPE" with
  the time and the amount left into the STATE file.

============================================================
PART 1: VOLUME CHECK (CENTS)
============================================================

V1 Request, written before any quote:
- GLBX.MDP3, ohlcv-1d, stype_in parent.
- QM.FUT and ZM.FUT, 2023-01-01 to the latest available date.
- Nothing else. Prices are not used or reported. Drop spread instruments,
  meaning any symbol with a hyphen.
QM and ZM daily volume is not a sealed series. ZM's owned one-minute bars
are not opened for this.

V2 Buy only if the quote is at most USD 1.00.

V3 Measures:
- For each root and quarter: median and 10th percentile of total daily
  volume, and the front-month share.

Kill rules, fixed now, over the last 12 full months available:
- QM: fails below a median of 1,000 contracts a day. If it fails, the
  frozen QM pilot is closed for good.
- ZM: fails below a median of 5,000 contracts a day. If ZM fails, stop
  before Part 4, buy nothing more, and report.

============================================================
PART 2: THE ZM PILOT SPEC (FROZEN BEFORE ANY ZM PURCHASE)
============================================================

Write reports/stage_e31_pilot_spec.md and hash it. Fix:

Data:
- ZM MBO for the front and second month.
- ZS and ZL MBP-1, front month, for the same days.
- Instrument definitions for all three, to confirm the match algorithm
  and implied-spread fields.

Window:
- Whole months, ending 2024-02-29T22:00:00Z and extending backwards.
- The window must include at least one WASDE day and one limit-reset
  month if it can.
- Its length is the most months whose total fresh quote fits the funds
  left after Part 1, less a USD 2 margin. All three series cover the same
  days.
- At least 2 months. Below that, buy nothing.

Sessions: the day session (08:30 to 13:20 CT) is primary. The overnight
session is reported separately.

Order: 1 contract, resting at the best bid or ask, cancelled and replaced
as the existing E.28 rules state where they apply.

Three fill models:
- (a) CBOT's K algorithm, reconstructed from MBO queue state: TOP, then
  40% FIFO, then 60% pro-rata with leveling, then FIFO for the residual.
  Use the parameters from the definitions and CME's published rules. Log
  any parameter not found.
- (b) Pure FIFO, back of the visible queue.
- (c) Fill only when price trades through. This model is the gate.

Markouts:
- At 1, 10 and 60 seconds, in ZM ticks, against the ZM mid.
- Each conditioned on ZS and ZL moves in the 1 to 10 seconds before the
  fill.
- Split by session, by distance in minutes from USDA releases, and by
  queue imbalance at entry.

Fees: Topstep 5.28, Lucid 5.60, Bulenox 5.72, MFFU 6.12 and Tradeify
9.20 USD a round trip. Verify each against E.28's firm-product file and
log any difference.

Kill rule, before any data. ZM fails the pilot if any of these holds:
- under model (c), mean 10-second markout plus half the spread captured,
  less the Topstep fee in ticks, is not above zero with a 95% bound;
- there are fewer than 400 fills under model (c);
- there are fewer than 20 feasible round trips per day-session day.
Report all three models; only (c) decides.

Also record the implied-liquidity check: how often ZM trades print with no
matching displayed resting quantity.

============================================================
PART 3: CODE
============================================================

Build the pilot code beside E.28's in reports/stage_e31_briefs/work/pilot/.
Reuse E.28's pull, verify and markout code where it fits. The K-algorithm
simulator and MBO queue reconstruction are new. Use synthetic tests only,
with no Databento call, including hand-built K-algorithm allocation cases
checked against CME's published examples.

============================================================
PART 4: REVIEW, THEN PURCHASE
============================================================

SpecReviewer, using Fable xhigh or the Pro substitute:
- checks the spec, the kill rule, the window arithmetic and the code;
- returns GO or NO GO.
Fix every BLOCKING item and re-check once.

On GO only:
- take a fresh quote;
- buy within the bound;
- verify the download against the manifest (sizes, record counts,
  sha256, date range);
- write the SAFE TO WIPE line.

============================================================
PART 5: MEASUREMENT
============================================================

If time and usage remain before 23:00, run the frozen measurement and
report the three fill models and the kill-rule verdict. Otherwise write
the exact command to run it.

============================================================
SCOPE AND DELIVERABLE
============================================================

This stage does NOT:
- read any holdout, embargo, research-window or sealed file
- read ZM, ZS or ZL data dated 2024-03-01 or later
- register or freeze a trading hypothesis (N stays 538)
- touch live/, ops/, any TopstepX credential or the ProjectX API
- push. REGISTRATION.md stays 0 bytes.

Start and end checks, quoted verbatim:
- `git status --short`;
- the holdout status;
- `wc -c REGISTRATION.md`;
- harness v14 2e908c81...;
- the spend ledger line count and sha256;
- N;
- pytest at the end, with the 2 GB memory rule.
Commits touch only this stage's files. E.30's unfinished files may be
reused and committed under this stage.

Write reports/E.31_RETURN.md in the usual eight sections, one progress.md
entry, one docs/STAGES.md line, and one final commit "Stage E.31 volume
check and ZM pilot". Do not push. Section 1 leads with:
- the two volume verdicts;
- the amount spent and left on acct-3, and whether it is safe to wipe;
- the pilot verdict, or what is left to run.
The last thing before ending: list every open choice in section 6.

END PROMPT
