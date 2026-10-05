# Stage E.14 Task 7: test C2 (dealer-gamma-conditioned late-session momentum), result

**Verdict: STOPPED** by the draft's minimum-power rule (reports/stage_e13_prereg_gexmom.md section 7, applied at
section 9 step 3; stage prompt Task 3: "Under 200: C2 stops"). JSON: reports/stage_e14_c2_result.json.

| Item | Value |
|---|---|
| Eligible dates with GEX < 0, 2011-05-03..2019-04-30, lag 1 | **135** (of 1,987 calendar-eligible; share 0.068) |
| Threshold | 200 |
| Upper bound under any calendar (from the CSV's dates alone) | 146 |
| GEX < 0 rows among the CSV's 2,011 rows dated 2011-05-02..2019-04-29 | 138 |
| Implementations agreeing | the lead's count script; harness v10's `screening.stage_e14_c2 count` |
| Stopped at | 01:34 PDT 2026-10-05, Task 3, before C2's freeze, registration and purchase |
| T1, T2 run | no (no ES bar was bought or read) |
| Trials registered | 0; program N stays 471 |
| Spent | $0.00 (the ES quote, $10.109048, would have fitted acct-2's headroom) |

Inputs: the GEX CSV (sha256 51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62, uncommitted), the
equity calendar reports/stage_e14_cal_equity.json (sha256 b12aee433635bc8334adb15d8f06c21255b0cb24889ea123a4d4375fb22657be),
the timing rule and terms ruling in reports/stage_e14_gex.md. The Fable verifier recomputes the count (Task 8,
reports/stage_e14_review.md).

## What this outcome means (draft sections 7 and 8)

Section 8 names three outcomes (pass, fail, T2 alone passes); none applies, because no test ran. Section 7 states
what a stop means: "The stage then stops before the purchase and reports, and the user decides." The draft
expected about 920 negative-gamma trades at the paper's 48% share for its own NGE measure and warned that
SqueezeMetrics' GEX "is a different construction, so its share may differ". In 2011-2019 its share is about 7%,
so T1 would have had at most about 135 trades, where the draft's power is below 0.5 even at a per-trade Sharpe of
0.14 and the 1.5c bar binds first. No price was read: nothing is learned about late-session momentum itself, and
the S&P exposure reopened by V25 stays unread for 2011-2019. The decision for the user is in reports/E.14_RETURN.md
section 7.
