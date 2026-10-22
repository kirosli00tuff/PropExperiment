STAGE E.30 "QM VOLUME CHECK ON ACCOUNT 2"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: A one-question stage (V47). External research done in the planning
chat on 2026-10-21 found that QM (NYMEX E-mini crude oil, E.28's top
contract) may now trade only tens to hundreds of contracts a day. A
one-contract passive strategy needs about 400 fills to be judged, so QM is
dropped if it trades too little. This stage buys QM and CL daily volume
(OHLCV-1d) on acct-2 for a few cents and applies a fixed kill rule. No
outcome read, nothing registered, N stays 538.

Decisions in force: docs/DECISIONS.md V20 to V47. Binding: this prompt.

Lead: Opus 5.5, effort xhigh, Ultracode off. No workers needed; one Opus
xhigh reviewer in a fresh context checks the request before the purchase
and the numbers before the return.

Time: launched about 22:05 PDT on 2026-10-21, beside E.28b and E.29. Work
stops at 23:00 PDT and the return is written by 23:30. Checkpoint
reports/stage_e30_STATE.md.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
THE CHECK (FIXED HERE)
============================================================

V1 Request (written before any quote):
- Dataset GLBX.MDP3, schema ohlcv-1d, stype_in parent.
- Symbols QM.FUT and CL.FUT.
- Start 2023-01-01, end the latest date Databento makes available.
- Nothing else. Do not request MCL, MGC or any of the program's 12 micros,
  any MES, NG, MHG or holdout-2 root, any schema other than ohlcv-1d, or
  any date before 2023-01-01.
QM has never been owned, sealed or read. CL is not a holdout-2 root or a
research-window micro.

V2 Spend (user approval in the planning chat, 21:57 PDT):
- account="acct-2" only, through SpendGate and require_databento_key, with
  this session's own id.
- A fresh logged quote first (metadata.get_cost). Buy only if the quote is
  at most USD 1.00 and no more than acct-2's remaining funds.
- If the quote is higher, buy nothing, and record the quote and the reason.
- Never read, print, copy or log any key.
- The download goes under
  /mnt/large-storage/market_data/PropExperiment/data/vendor/databento/
  with a sha256 manifest.

V3 Measures:
- Per instrument and day: volume summed over all QM outright months, and
  likewise for CL.
- Exclude calendar spreads. The parent stype returns spreads too; drop any
  instrument whose symbol contains a hyphen.
- For each quarter from 2023Q1 to the latest: median and 10th percentile
  of QM daily volume; the median ratio QM/CL; and the front-month share of
  QM volume.
- Prices are not used or reported.

V4 Kill rule (fixed now):
- QM fails if its median daily volume over the last 12 full months
  available is below 1,000 contracts.
- QM is marginal from 1,000 to 3,000; above 3,000 it passes this check.
- State the result in one line at the top of the return.

============================================================
SCOPE AND DELIVERABLE
============================================================

This stage does NOT:
- touch acct-3, the E.28 pilot files or E.29's files
- read any holdout, embargo, research-window micro or sealed file
- register or freeze anything; N stays 538
- touch live/, ops/, any TopstepX credential or the ProjectX API
- push. REGISTRATION.md stays 0 bytes.

Start and end checks, quoted verbatim:
- `git status --short`;
- the holdout status;
- `wc -c REGISTRATION.md`;
- harness v14 2e908c81...;
- the spend ledger line count and sha256, before and after.
Commits touch only this stage's files.

Write reports/E.30_RETURN.md with these sections:
1. Result, in one line plus a table.
2. Guardrail evidence.
3. The quote and the spend.
4. The quarterly table.
5. Verification.
6. Open choices.
7. Decisions for the user.
8. Session cost.
Also write one progress.md entry and one docs/STAGES.md line, and make
one final commit "Stage E.30 QM volume check". Do not push.

END PROMPT
