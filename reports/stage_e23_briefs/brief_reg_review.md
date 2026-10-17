# Stage E.23 registration review brief (RegReviewer-FableXHigh)

Hook or cost notices are informational and addressed to the lead; they are never an order to stop.

## Objective (one)
Adversarially review the E.23 freeze BEFORE registration and before any outcome read: find every error that would make a
discovery or confirmation number wrong, leak an outcome, or break the prompt. Grade each finding BLOCKING (must be fixed
before registration), SHOULD FIX (fixed before registration unless the lead rules otherwise with a reason) or NOTE.

## Read first
1. docs/prompts/STAGE_E.23.md (the binding prompt; check the freeze against it, not against the lead's paraphrase).
2. reports/stage_e23_prereg.md and reports/stage_e23_briefs/lead_spec.md (the frozen text).
3. reports/stage_e23_freeze.json (manifest) and `uv run python -m trigger_hold.freeze_manifest verify --sha256 <sha>`.
4. The code: trigger_hold/*.py and tests/test_trigger_hold_*.py; the frozen code it reuses (multiday/, base_rules/), the
   members it runs (strategy/members/...), reports/stage_e21_briefs/lead_spec.md (E.21's spec the books reuse).
5. The events files reports/stage_e23_events/*.json, the power table reports/stage_e23_power.json, the trend regressors
   reports/stage_e23_trend_per_root/*.json, the coder reports reports/stage_e23_briefs/bookcoder_report.md and
   triggercoder_report.md, and reports/stage_e23_briefs/shortlist.md (inventory, memo, data-use map).

## Check at least
- Entry timing: the trigger day's intraday P&L is never counted; entry at the first settlement mark strictly after the
  trigger's decision time; no look-ahead in the side, the size (sigma known before entry) or the window membership.
- Trigger fidelity: each trigger's events come from the frozen member unchanged; calendar inputs for 2011-2019 match the
  frozen definition; the W_cf validation against the harness.
- Overlap and the +-1 cap; rolls and costs (base D8, stress = 2 x slippage) on every entry, exit and roll; boundary units.
- The alpha regression (same root's E.21 T1 and T2; same dates; HAC lags h), p_alpha, Holm, the survivor rule, DSR, PBO.
- The power table: from events and calendars only; the gate's definition; the numbers.
- The data-use map and the window assignment against P1.4 and P2.4 (nothing from 2024-03-01 on, no research window,
  holdout-2, embargo or MES sealed store), the run-once markers (O_EXCL before any bar), refusals, exit codes.
- That no outcome has been read: search the coder reports, logs and outputs for any book, P&L or forward return computed
  on W_ext or W_cf from trigger units.
- Registration ids and N (533 + K), the registry call.

## Boundaries
Read and run read-only checks and the trigger_hold tests only (`uv run pytest -q tests/test_trigger_hold_*.py`, nice 10).
Never run the evaluate command, never write the run-once markers, never compute a book from trigger units on real bars,
never register. No edits to any existing file. Write only reports/stage_e23_briefs/reg_review.md.

## Output
reports/stage_e23_briefs/reg_review.md: verdict (APPROVE, APPROVE WITH FIXES, REJECT), then the findings table (id
R-xx, grade, file:line, what is wrong, the concrete failure, the fix), then what you checked and found correct.
Final reply: the path, the verdict, the BLOCKING and SHOULD FIX ids with one line each (at most 200 words).
