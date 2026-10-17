### Final ETA table (actuals; PDT; the initial estimate in brackets)

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Start checks; start suite | lead | opus | xhigh | 00:47 | 01:09 | 22 min | in lead | done; 7402 passed [1 min + 20 min] |
| A0 Part A facts (workflow, 4 agents) | HarnessGapAudit-OpusXHigh; TierAFactsK5K3-, TierAFactsK6K8-, DecisionsScan-SonnetMed | opus / sonnet | xhigh / medium | 00:53 | 01:11 | 18 min | 23,719,572 + 3,488,024 + 2,400,102 + 4,805,088 | done [40 min] |
| B1 Carver sources | CarverReader-OpusHigh | opus | high | 00:59 | 01:08 | 9 min | 10,371,337 | done [35 min] |
| B2 Data-source memo, IBKR margins | DataSourceReader-OpusHigh | opus | high | 00:59 | 01:19 | 20 min | 21,314,667 | done; 14 searches [60 min] |
| B3 Rule core, study, tables, wiring | MicroBookCoder-OpusXHigh | opus | xhigh | 00:59 | 01:36 | 37 min | 31,993,960 | done; two follow-ups [3 h] |
| B4 Paper runner | ForwardRunnerCoder-OpusXHigh | opus | xhigh | 00:59 | 01:19 | 20 min | 8,799,199 | done; 88 tests [2 h] |
| A1 Rulings, K3/K6 start rules, declaration | lead | opus | xhigh | 01:03 | 01:14 | 11 min | in lead | done [20 min] |
| A2 Harness v13 and review fixes | HarnessBuilder-OpusXHigh | opus | xhigh | 01:15 | 02:07 | 33 min of work | 36,721,085 | done [65 min] |
| A2b v13 review and recheck | HarnessReviewer-FableXHigh | fable | xhigh | 01:40 | 02:10 | 19 min of work | 7,287,736 | done; 0 blocking [20 min] |
| B6 E22-F1 review and recheck | RegReviewer-FableXHigh | fable | xhigh | 01:36 | 01:55 | 16 min of work | 3,943,562 | done; 2 blocking fixed [25 min] |
| B7 Pin test, status strings | F1FixApplier-SonnetMed | sonnet | medium | 01:49 | 01:50 | 1 min | 377,319 | done |
| A3 W1 manifest, K8 start rule, power (W1) | lead | opus | xhigh | 01:40 | 01:55 | 15 min | in lead | done (power redone under v13) |
| A4/A5 v13 commit; power under v13 | lead | opus | xhigh | 02:08 | 02:20 | 12 min | in lead | done [40 + 25 min] |
| B10/B11 F1 freeze commit; registration | lead | opus | xhigh | 02:11 | 02:12 | 1 min | in lead | done; N 532 -> 533 |
| A6/A7 Lists; list review and recheck | lead; ListReviewer-FableXHigh | opus / fable | xhigh | 02:20 | 02:43 | 23 min | 4,371,839 | done; 0 blocking [60 min] |
| E1 End suite (quoted) | lead | - | - | 02:20 | 02:40 | 20 min | in lead | 1 failed (h6, expected), 7634 passed |
| PAUSE: usage limit, user pause 07:57, laptop restart | - | - | - | 02:43 | 18:26 | 15 h 43 min | - | excluded from work |
| R0/R1 Resume checks; list commit | lead | opus | xhigh | 18:26 | 18:28 | 2 min | in lead | done; ccd7fa7 |
| A8 Confirmations K5, K8, K3, K6 (once each) | lead | - | - | 18:28 | 18:59 | 31 min | in lead | done [30 min] |
| A10 Verifiers K5, K8, K3, K6 | VerdictVerifier-K5/K8/K3/K6-FableXHigh | fable | xhigh | 18:32 | 19:12 | 40 min (overlapping) | 2,471,132 + 3,098,209 + 2,424,785 + 2,435,262 | done; no discrepancy [35 min] |
| E1b End checks; suite rerun | lead | - | - | 18:59 | 19:15 | 16 min | in lead | checks done; rerun stopped at 81% (memory) |
| E2 Return, progress, STAGES, cost, commit | lead | opus | xhigh | 19:01 | ~19:20 | ~19 min | in lead | done [35 min] |
| **Stage** | | | | 00:46 | ~19:20 | **about 2 h 55 min of work (00:46-02:43 and 18:26-~19:20), excluding the 15 h 43 min pause** | **308,963,957** (lead and workers; split below) | initial estimate: about 7 h 5 min of work to ~07:55; the build and review steps ran much faster than estimated |

### Tokens per model (transcripts; reports/stage_e22_briefs/make_cost.py over the lead's .jsonl and every subagent transcript, each message's final usage; to 2026-10-17T02:15:19Z; the lead's last few messages after the count are not included)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 4,034 | 474,495 | 23,583,225 | 1,970,771 | 26,032,525 |
| claude-opus-5-5 | 1,898 | 1,044,899 | 266,933,115 | 3,880,987 | 271,860,899 |
| claude-sonnet-5-5 | 182 | 80,926 | 10,447,508 | 541,917 | 11,070,533 |
| all | 6,114 | 1,600,320 | 300,963,848 | 6,393,675 | 308,963,957 |

Delegation share: lead 138,941,079 (45.0%), workers 170,022,878 (55.0%). By model: claude-fable-5-1 8.4%, claude-opus-5-5 88.0%, claude-sonnet-5-5 3.6%.

Per worker spawn (agent, model, effort as set, tokens): HarnessGapAudit-OpusXHigh (opus, xhigh) 23,719,572; TierAFactsK5K3-SonnetMed (sonnet, medium) 3,488,024; TierAFactsK6K8-SonnetMed (sonnet, medium) 2,400,102; DecisionsScan-SonnetMed (sonnet, medium) 4,805,088; CarverReader-OpusHigh (opus, high) 10,371,337; DataSourceReader-OpusHigh (opus, high) 21,314,667; MicroBookCoder-OpusXHigh (opus, xhigh) 31,993,960; ForwardRunnerCoder-OpusXHigh (opus, xhigh) 8,799,199; HarnessBuilder-OpusXHigh (opus, xhigh) 36,721,085; HarnessReviewer-FableXHigh (fable, xhigh) 7,287,736; RegReviewer-FableXHigh (fable, xhigh) 3,943,562; F1FixApplier-SonnetMed (sonnet, medium) 377,319; ListReviewer-FableXHigh (fable, xhigh) 4,371,839; VerdictVerifier-K5-FableXHigh (fable, xhigh) 2,471,132; VerdictVerifier-K8-FableXHigh (fable, xhigh) 3,098,209; VerdictVerifier-K3-FableXHigh (fable, xhigh) 2,424,785; VerdictVerifier-K6-FableXHigh (fable, xhigh) 2,435,262.
(The script's effort column reads workflow agents as 'high'; the efforts above are those set in the workflow script.)

These are token counts, not plan-credit percentages; the /usage meter is the user's to read.
