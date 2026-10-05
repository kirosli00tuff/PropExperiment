# Brief: VerdictVerifier-FableXHigh (Stage E.14 Task 8: independent verification)

You are the independent verifier of Stage E.14 (PropExperiment, main checkout). A different model (Opus) produced
every number you check. Recompute first, compare second: do NOT read the lead's figures for a number before you
have computed it yourself (the files to avoid until then are named per item). The user is asleep; do not ask
questions. Read by section; keep command output short.

## 1. Test C2's verdict (STOPPED at its power rule)
Recompute, from the rule and the inputs only, the number of eligible trade dates d in 2011-05-03..2019-04-30
with GEX < 0, under: the draft reports/stage_e13_prereg_gexmom.md (sections 2, 3, 7, 9 step 3), the timing rule
"the row of the latest CSV date strictly before d" (lag 1), and the equity calendar
data/calendars/hist2010/equity.json (= reports/stage_e14_cal_equity.json; load it with
data.hist_calendar.load_hist_group_calendar or parse the JSON yourself): a CME equity trade date, not an early
halt or late open, not unsourced, with a prior trade date, with a GEX row. The GEX CSV is
reports/stage_e14_briefs/gex/DIX.csv (check its sha256 is 51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62).
You may read the CSV's date and gex columns, and only the SIGN of gex: print counts only, never a value. Write
your own short script (in the scratchpad /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/19c73927-ec62-4304-916b-b9a703235eab/scratchpad/verify/),
not the lead's. Also compute the calendar-free upper bound (weekdays in the window whose lag-1 row is negative).
Only then compare with reports/stage_e14_c2_result.json and reports/stage_e14_gex.md section 4. Also check the
timing rule's evidence (section 3 of that file; the capture files under reports/stage_e14_briefs/pages/gex/) and
the terms ruling (section 1) on their merits.

## 2. Test C1's q reproduction and M1 hash
Re-run the frozen code yourself into scratch paths (never overwrite the lead's files):
```
uv run python -m c1_replication.q_m1 --state ~/.cache/propexp_e14_c1/e12_state_copy \
  --state-manifest reports/stage_e14_c1_e12_state_manifest.json \
  --state-manifest-sha256 8a38eeb150ba7c063e1f7b4292b00efb0bd10549c61e8202fcb926bc8dab1ad9 \
  --out <scratch>/c1_model_verify.json --model-dir <scratch>/m1_verify
```
(nice 10; it loads a 103 MB panel; check free memory first). Then compare with reports/stage_e14_c1_model.json:
the reproduced NG h60 and hF rows (trades, mean, t_B) against reports/stage_e12_gate0.json, q_h60 and q_hF, both
M1 payload sha256s, the feature_cols sha256, the ML ledger sha256 unchanged. Independently of the code, read
ml_route_v2/gate0.py (_oof, _top_trades, gate0_b_trades, _b_test) and c1_replication/q_m1.py and confirm that q is
the smallest |r_hat| of the NG trades and that no refit happened.

## 3. Order of events (git, ledgers, files)
- git log: "harness v10, E.14 caps and stores" before the freeze commit; the freeze commit holds
  reports/stage_e14_prereg_C1.md with the sha256 STATE records; v10's manifest sha256 matches the commit.
- reports/stage_e14_c1_model.json written after the freeze commit (file mtime and STATE times) and before any
  2010-2019 byte exists (no ext2010 or es2011 file under data/vendor or data/processed_hist: list names only).
- ledger/databento_spend.jsonl: every line this session (session stage-E.14-2026-10-05) is a $0.00 quote; no
  billable line; account totals unchanged (acct-1 118.390020, acct-2 231.599730).
- ledger/trial_registrations.jsonl: the baseline only (N = 471); no C1 or C2 registration.
- C2: the GEX fetch, the count and the stop came before any freeze; no C2 freeze file exists.
- `uv run python -m data.holdout status`: all_ok, 0 unlocks.

## Output
Append a section "Verification (Task 8)" to reports/stage_e14_review.md: for each item your recomputed value,
the lead's value, MATCH or MISMATCH, and findings graded BLOCKING, SHOULD FIX or NOTE with evidence. A BLOCKING
finding on a verdict number must name the code or data error you found. No market data beyond the GEX signs; no
.env, key or Databento call; edit nothing but the review file. Return: path, a summary of at most 200 words with
the match results and counts per grade, and anything you could not check.
