# Stage E.14 Task 6: quotes, registration and purchase

Lead: Opus 5.5 xhigh, 2026-10-05. Prompt: docs/prompts/STAGE_E.14.md, Task 6 and the Spend guardrail (V26).

## Result: two fresh quotes, no registration, nothing bought

Test C2 stopped at its power rule (reports/stage_e14_gex.md: 135 eligible GEX < 0 dates, under 200) before its
freeze and registration. So C2's T1 and T2 were not registered (N stays 471) and ES was not bought, although the
ES quote fitted the spend guardrail. Test C1 is quoted only, by the stage's design (V26). No billable request was
sent to Databento in Stage E.14.

## Quotes (fresh, quote-only, ledgered at $0.00 under stage-E.14-2026-10-05, acct-2)

| Plan | Test | Run (PDT) | Chunks | Quoted $ | x 1.03 | Fits acct-2's headroom $18.070270 with 3%? | File |
|---|---|---|---|---|---|---|---|
| es2011: ES 2011-05..2019-04 | C2 | 01:29-01:32 | 96 of 96, 0 failed | 10.109048 | 10.412319 | yes | reports/stage_e14_quotes_es2011.json |
| ext2010: NG, NQ, ZN, 6E, GC, ZC, 2010-06-06..2019-05-01 | C1 | 01:33-01:56 | 642 of 642, 0 failed | 57.742330 | 59.474600 | no: short $41.404330 | reports/stage_e14_quotes_ext2010.json |

C1 per root: NG 8.570392, NQ 10.625886, ZN 10.106134, 6E 11.072096, GC 11.182294, ZC 6.185528 (107 chunks each;
the June-2010 partial chunk from 2010-06-06 priced for all six). Largest single chunk $0.116497 (GC), under the
$3.00 request cap. E.13's estimate was $57.314736 for 106 chunks per root plus the unquoted June-2010 chunks.

Logs: reports/stage_e14_briefs/quote_es2011.log, quote_ext2010.log.

## Caps (harness v10, data/config.py)

| Constant | Value | Note |
|---|---|---|
| ACCOUNT_2_CAP_USD | 249.67 | unchanged (V26) |
| E14_SESSION_CAP_USD | 0.00 | set to 10.41 (= $10.412319 in whole cents) at 01:33 from the ES quote, reset to 0.00 at 01:34 when C2 stopped; never committed or used at 10.41 |
| E14_EXT2010_SESSION_CAP_USD | 0.00 | C1 cannot buy under v10 |
| E14_REQUEST_CAP_USD | 3.00 | D13 |

## Ledger (ledger/databento_spend.jsonl)

| | Lines | sha256 | acct-1 spent / cap / headroom | acct-2 spent / cap / headroom |
|---|---|---|---|---|
| Start (00:26) | 27,018 | 6a074c143670e241b0a383b2778661bbc60e39ec96c501000a4413176efeda4c | 118.390020 / 120.00 / 1.609980 | 231.599730 / 249.67 / 18.070270 |
| After the quotes (03:07) | 27,756 | 0312fbc0b1ca2da652ca7caaab2313ccbbc6920ae3a19d9651ff2e94cd1c48fb | 118.390020 / 120.00 / 1.609980 | 231.599730 / 249.67 / 18.070270 |

The 738 new lines are all event "quote", session stage-E.14-2026-10-05, account acct-2, usd 0.0, timestamped
08:29:29Z to 08:55:48Z (01:29 to 01:55 PDT); their quoted_usd sum to $67.851378 (= 10.109048 + 57.742330).
Billed against quoted per chunk: none (nothing billed). Balance left: acct-1 $1.609980, acct-2 $18.070270.

## The top-up C1 needs

C1's quote x 1.03 minus acct-2's headroom left after C2 (C2 spent nothing): $59.474600 - $18.070270 =
**$41.404330**, at this quote. The later session quotes fresh; the cap raise must cover that quote x 1.03 less the
headroom then. acct-1's $1.609980 fits no root.

## Holdout status (the post-purchase check; no purchase happened), 03:07 PDT

```
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
```
