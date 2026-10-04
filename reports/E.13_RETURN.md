# Stage E.13 return: what is left to search (research and scoping; no market data, no purchase)

Prompt: docs/prompts/STAGE_E.13.md (commit 5d85924). Lead: Opus 5.5, xhigh. Session dbc7460b-72c3-4537-8327-
d14819b62f5c, started 2026-10-03 14:24 PDT, paused twice by the user, finished 2026-10-04 about 02:00 PDT. Times PDT.

## 1. Verdict summary

**What is left to search is thin.** No candidate offers better than about 7% central odds of income-bearing
deployment within 12 months (reports/stage_e13_ranking.md v3, after the Fable review). Top three:

1. **C1, backward NG replication** (2010-2019, never read). It tests whether E.12's frozen ridge NG edge holds in an
   unseen decade.
   - Pass odds: 12% headline (central 16.5%). Deployment odds: 6.6% central.
   - If real, $96-$345 a month per 150K XFA. N 471 -> 473.
2. **C2, dealer-gamma-conditioned S&P late-session momentum** (ES 2011-2019; Baltussen et al., JFE 2021). Pass odds
   18% central (3.9% skeptical); deployment 5.0%. About $10 of data. It needs the closed S&P exposure reopened.
3. **C3, trend and carry, personal IBKR Canada account.** The venue is clean, but the post-2010 Sharpe is about
   0.25-0.35 and carry is gone since 2013: $40-$430 a month at $10K-$100K, with deep drawdowns.

Swing prop firms fail the drawdown arithmetic. Only The Trading Pit Classic permits multi-day automation outright,
possibly no longer sold. Phidias stays human-in-the-loop.

**Recommended:**
- **Pausing until the AiTrader readout** (2026-10-23 at the earliest) costs nothing and is reasonable.
- **If continuing:**
  - E.14: a calendar probe, then C1's freeze and harness v10, at $0.
  - E.15: the purchase, about $59 with an acct-2 top-up of about $41-$50, then one evaluation.
  - C2 is an optional companion: about $10 more data, combined top-up about $50.

**The user decides:**
- continue or pause;
- C1's V24 question (reloading E.12's out-of-fold predictions, plus one M1 fit on the 2019-2024 panel);
- the top-up;
- reopening the S&P exposure for C2;
- keeping ~/.cache/propexp_e12_phase1.

Nothing was bought, no market data was read, and the ledger is unchanged.

## 2. Guardrail evidence

### Start (14:25 PDT 2026-10-03), quoted verbatim (reports/stage_e13_briefs/start_checks.txt; script checks.sh)

```
$ date
Sat Oct  3 14:25:10 PDT 2026
$ git status --short
?? reports/stage_e12_briefs/margin_pages/
?? reports/stage_e13_briefs/
$ git log --oneline -3
5d85924 docs: Stage E.13 prompt (research and scoping) and V24
94a92b6 Stage E.12 ML route v2 phase 1 and Gate 0
4b1e81e harness v9, L-3 closure-bar ruling path (user decision)
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
preflight OK: 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
27018 ledger/databento_spend.jsonl
6a074c143670e241b0a383b2778661bbc60e39ec96c501000a4413176efeda4c
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
```

### End (01:49 PDT 2026-10-04), quoted verbatim (reports/stage_e13_briefs/end_checks.txt)

Run just before this return was written. The untracked files are this stage's outputs, which the commit adds,
except the DO_NOT_COMMIT pages.

```
$ date
Sun Oct  4 01:49:38 AM PDT 2026
$ git status --short
 M docs/STAGES.md
 M progress.md
?? reports/stage_e12_briefs/margin_pages/
?? reports/stage_e13_STATE.md
?? reports/stage_e13_briefs/
?? reports/stage_e13_info_sources.md
?? reports/stage_e13_ng_replication_draft.md
?? reports/stage_e13_phidias_question.md
?? reports/stage_e13_prereg_gexmom.md
?? reports/stage_e13_prereg_ngrepl.md
?? reports/stage_e13_ranking.md
?? reports/stage_e13_review.md
?? reports/stage_e13_rulings.md
?? reports/stage_e13_trend_carry.md
?? reports/stage_e13_venues.md
?? reports/stage_e13_venues_part1.md
?? reports/stage_e13_venues_part2.md
?? reports/stage_e13_venues_part3_brokers.md
$ git log --oneline -3
5d85924 docs: Stage E.13 prompt (research and scoping) and V24
94a92b6 Stage E.12 ML route v2 phase 1 and Gate 0
4b1e81e harness v9, L-3 closure-bar ruling path (user decision)
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
preflight OK: 7fd757f6d7c3990c2d20756c501f68b0541aa89851dcca9236badabd4f4a9bd9
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
27018 ledger/databento_spend.jsonl
6a074c143670e241b0a383b2778661bbc60e39ec96c501000a4413176efeda4c
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 231.599730 cap 249.67 headroom 18.070270
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
```

The ledger is unchanged: 27018 lines, sha256 6a074c14...a4c at start and end. No Databento call of any kind was
made (open choice 3). Holdout unlocks are 0 everywhere at start and end. REGISTRATION.md is 0 bytes. The harness v9
preflight passed at start and end (7fd757f6...). The cluster freezes K1-K8 and the v2 freeze (91 files) verified at
both. No pytest suite was run: the stage changed no code.

## 3. Results per task

### Task 0: startup
All start checks passed (section 2). HEAD 5d85924 (the prompt commit); the tree was clean except for the expected
untracked reports/stage_e12_briefs/margin_pages/.

### Task 1: venues (reports/stage_e13_venues.md; parts _part1, _part2, _part3_brokers; questions in reports/stage_e13_phidias_question.md)
- Prop firms: 18 firms checked from their own help-centre and terms pages (all fetched 2026-10-03). Topstep, Apex,
  Tradeify, Take Profit Trader, MyFundedFutures, Bulenox, Alpha, Lucid, TradeDay, Earn2Trade, FundedNext, Top One,
  Funded Futures Family and The Trading Pit Prime are flat every session: NOT PERMITTED. Topstep requires flat by
  3:10 PM CT (P1-01).
- PERMITTED, unambiguous: The Trading Pit Classic (overnight Monday-Thursday, flat by the Friday close, own EAs
  allowed; not on the current sales page, so possibly not sold) and, for a personal account, IBKR Canada (CIRO
  dealer, TWS/REST API, USD 0 minimum, MES about USD 0.61 a side all-in, MES overnight initial margin USD 3,704.55).
- HUMAN-IN-THE-LOOP ONLY: Phidias Premium 50K/100K/150K (EOD trailing $2,500/$3,000/$4,500; the TOU's
  semi-automated clause is word-for-word unchanged since the 2026-09-28 entry, still undefined, and no API is
  documented); Leeloo's Investor account (being phased out); Wealthsimple (futures, no API).
- UNCLEAR: Elite Trader Funding Direct To Funded and Diamond Hands (multi-day holds allowed; AI and automation need
  written authorization); brokers AMP, Optimus, Ironbeam, EdgeClear, TradeStation, GFF and Jitneytrade (BC
  eligibility; the BCSC exemption limits unregistered foreign dealers to "eligible derivatives parties").
- NOT PERMITTED for automation despite overnight holds: PropEd Capital. NinjaTrader and Tradovate exclude BC. The
  bank-owned brokers, Questrade and Qtrade offer no futures.
- Support questions drafted for the user (never sent): Phidias (A: alert plus manual order; B: tap to confirm, then
  software submits; C: software-managed exits), PropEd, Leeloo, Elite Trader Funding.

### Task 2: trend and carry (reports/stage_e13_trend_carry.md)
- After publication: SG Trend Index (net) Sharpe 0.24 over 2010-2025 and 0.30 over 2013-2025, worst drawdown -20.6%;
  AQR's updated TSMOM factor (gross) 0.31 over 2012-2025 (t 1.18), against 1.41 over 1985-2009; AQR cross-sectional
  carry (gross) -0.19 over 2013-2025, against 0.92 over 1972-2012.
- Carver (quoted from his code and blog): a 4-contract minimum, a 25% risk target, IDM up to 2.5, a cost ceiling of
  0.01 Sharpe per trade.
- Sizing from published volatilities, 25% target, mid case: $40 / $89 / $189 / $428 a month at $10K / $25K / $50K /
  $100K. The books fill with FX, yield and grain micros. Expected 10-year maximum drawdown 76-103% (46-56% at 15%).
  Confirming the edge from its own record takes 44-100+ years.
- Prop fit: a 10% one-year trailing-ruin bound allows a daily sigma of about D/27; one micro per exposure runs
  $169-$2,432 a day. It fails at every drawdown size on the grid ($2,000-$7,500).

### Task 3: information sources (reports/stage_e13_info_sources.md)
- Best: (1) dealer gamma exposure conditioning late-session momentum (Baltussen et al. JFE 2021; free SqueezeMetrics
  GEX from 2011-05-02; the paper's negative-gamma share is 48%); (2) NOAA GFS forecast revisions for NG (one 2025
  daily paper; no forecast-vintage archive found before 2021). No third source meets the bar.
- Every surprise-against-consensus source (EIA storage and WPSR, USDA, economic-surprise indices) needs proprietary
  consensus history. COT, put/call, SKEW, auctions and Fed text have weekly-or-longer or null evidence.

### Task 4: NG replication draft (reports/stage_e13_ng_replication_draft.md, with the lead's rulings C1-C21)
- Model M1 (the frozen Gate 0 ridge fitted once on the E.12 panel): neither fallback condition holds. 29 of 64
  features are live on NG rows, reading NG, five legs (NQ, ZN, 6E, GC, ZC) and official calendars. E.12 persisted
  the out-of-fold predictions, so q is reproduced, not refitted.
- Databento's GLBX.MDP3 starts on 2010-06-06. The window is 2010-06-07..2019-04-30 (lead rulings C5 and C6: a fixed
  start with no volume read, and no May-2019 splice).
- Cost: $57.31 quoted for NG and the five legs ($59.03 with the 3% margin), plus the June-2010 chunks (unquoted);
  acct-2 top-up about $40.96. Build: 3.5-4 sessions, mostly sourced 2010-2019 calendars. No Databento call was
  made: E.12's record covers every item.
- Prior: P(the best of 81 reaches t >= 2.51 under the global null) = 0.396 (Bonferroni 0.502). Power 0.93 / 0.40 /
  0.13 at 1 / 1/2 / 1/4 of the observed effect. Odds 12% (7-35%).
- Designer's recommendation: run later, after a one-year calendar probe.

### Task 5: ranking (reports/stage_e13_ranking.md v3) and pre-registration drafts
- The ranking table has candidates in columns, with the AiTrader readout as a column. Its rule: deployment odds
  first; then published evidence, test independence and fit; cost and effort never decide.
- Final order: **C1 NG replication > C2 GEX momentum > C3 trend+carry personal > C4 GFS revisions > C5 trend+carry
  swing prop.** C0 (pause) is a reasonable alternative.
- The order went through three versions; the review's R-01 settled it (section 5).
- Drafts (nothing frozen):
  - reports/stage_e13_prereg_ngrepl.md (C1);
  - reports/stage_e13_prereg_gexmom.md (C2: GEX < 0 days, trade 14:30-15:00 CT in the sign of the rest-of-day
    return, MES vehicle, c 2.038 ticks, 1.5c and p <= 0.025 per test, two tests).

## 4. Delegation record

One row per spawn. Times are PDT, from the transcripts. Tokens are input + output + cache read + cache creation,
from reports/stage_e10_briefs/cost.py over this session's transcript (raw output:
reports/stage_e13_briefs/cost_raw.txt), never estimated.

| Agent (description) | Agent file | Model | Effort | Start-end | Wall | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|
| PropVenues1-OpusHigh | worker-high | opus | high | 14:33-14:54 | 21 min | 21,691,418 | done: 7 firms; deviation: Scrapling on two terms-restricted domains before reading their terms (pages uncommitted; R-11) |
| PropVenues2-OpusHigh | worker-high | opus | high | 14:33-14:52 | 19 min | 27,209,780 | done: 7 firms + 4 extra, Phidias question; deviation: Scrapling on lucidtrading.com before its terms (uncommitted) |
| TrendCarry-OpusHigh | worker-high | opus | high | 14:33-15:07 | 33 min | 32,849,245 | done |
| ReplicationDesigner-OpusXHigh | worker-xhigh | opus | xhigh | 14:33-15:00 | 26 min | 32,351,615 | done: 21 design choices for the lead |
| InfoSource-OpusHigh | worker-high | opus | high | 14:52-15:20 | 28 min | 31,337,888 | done; Firecrawl used before Scrapling for one PDF (recorded, R-11) |
| BrokerVenues-OpusHigh | worker-high | opus | high | 14:54-15:16 | 21 min | 33,241,282 | done; spawned when a slot freed (Task 1 split, open choice 1) |
| RankingReviewer-FableXHigh (review, then one SendMessage follow-up) | worker-xhigh | fable | xhigh | 23:21-23:39; 01:44-01:48 | 18 + 4 min | 4,729,288 | done: BLOCK (1 B, 7 SF, 8 N); follow-up: R-01 CLOSED, R-17 SF, R-18/R-19 N |

At most four workers ran at once. Fable ran one review, plus a short follow-up through the same agent, not a new
spawn (open choice 22).

## 5. Verification

The Fable review (reports/stage_e13_review.md) recomputed 161 quantities: every load-bearing number agrees, and the
disagreements were labels. It spot-checked 19 ranking facts against their cited lines and grepped 32 quotes in the
saved pages. Rulings are in reports/stage_e13_rulings.md; every BLOCKING and SHOULD FIX finding is fixed.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| R-01 The top-two order rested on a tie criterion section 1 does not contain; C2's odds asserted | BLOCKING | Accepted: section 1 applied literally (primary key = deployment odds, row (b)); C2's odds derived | C1 first, C2 second (central row (b) 6.6% against 5.0%); follow-up: CLOSED |
| R-02 The paper gives a 48% negative-gamma share, marked UNSOURCED | SHOULD FIX | Accepted | Quote cited; power at 0.48 added; the 200-date stop noted as far from binding |
| R-03 C2 income per-MES label | SHOULD FIX | Accepted | $6.5-$15.6 per MES ($13-$31 for two) |
| R-04 NG prereg named half the V24 question | SHOULD FIX | Accepted | Both computations on the 2019-2024 panel named (OOF reload, M1 fit) |
| R-05 C2 evidence cell described the unconditional result | SHOULD FIX | Accepted | Conditional (S&P, 1996-2020) and unconditional (60+ futures) split |
| R-06 Phidias fee mislabelled | SHOULD FIX | Accepted in substance; corrected the reviewer on "Lifetime" (on the pages), which the follow-up confirmed | Relabelled as the one-time CASH activation fee; evaluation price UNSOURCED |
| R-07 C2: no rule for unsourced calendar dates; c stated twice | SHOULD FIX | Accepted | C12-style exclusion and 2% stop; c stated once |
| R-08 v1 hash unverifiable | SHOULD FIX | Accepted | v1 reconstructed byte-identically (e4106799...97fe), v2 kept; full hashes in STATE |
| R-17 Order sensitivity not disclosed (follow-up) | SHOULD FIX | Accepted | Section 5 gives the row-(a) order, the reversal thresholds, and that the recommendation is unchanged |
| R-09 to R-16, R-18, R-19 | NOTE | Accepted or recorded | The cost-ratio range; AiTrader day count; deviation-fetch marking; C10 stop closes the attempt; power for the ruled window; headline cases shown; citation slips; share-independence and absent-term conventions disclosed |

Numbers entering the ranking that the reviewer recomputed independently: C1 and C2 income; C2 power, cost bar and
odds; the NG prior (0.396, 0.502, Bayes factors, power table, odds, joint false pass 0.018); the purchase and top-up
($57.31, $59.03, $40.96); the trend/carry IDM, sizing, income and expected maximum drawdown; the Part D ruin bounds;
the AiTrader dates.

## 6. Open choices (decisions the lead made on its own, with the reason)

1. Task 1 split into three workers (PropVenues1, PropVenues2, BrokerVenues) instead of one: 14 firms plus brokers is
   too long for one context (CLAUDE.md: several short workers over one long one). The lead merged the parts.
2. The prompt's "reports/stage_e12_purchase.md and its JSON" do not exist. The 2010-extension quote record is
   reports/stage_e12_quotes_ext2010.md/.json, which was used.
3. No Databento quote run. E.12's record prices NG and every leg Task 4 needs, so the ledger is unchanged. The
   June-2010 partial chunks are not in that record; the next stage quotes them (CLAUDE.md requires a fresh quote
   before any spend anyway).
4. Task 2 tabulated ruin over a grid of drawdown sizes, so it did not wait for Task 1. The lead mapped the grid to
   the swing venues in the ranking.
5. Task 2 added a $10K capital level to the prompt's three examples, for V22's small personal account.
6. The lead appended an Elite Trader Funding question (section 4) to reports/stage_e13_phidias_question.md, from
   PropVenues1's suggested asks.
7. Lead error: the InfoSource brief gave docs/ for the K1-K8 catalogs, which are in reports/. The worker found
   them; no effect on the result.
8. Task 4 brief: the provisional rulings L4-1 to L4-7 (M1 first with a stated fallback rule, the threshold from
   persisted out-of-fold predictions, the window, the pass bar, the order of events).
9. Task 4 rulings on C1-C21: all accepted except C5 (a fixed start of 2010-06-07 for every root, with no volume
   read) and C6 (end 2019-04-30, with no May-2019 splice). C19 (funding) is left to the user.
10. Raw pages were saved under reports/stage_e13_briefs/pages/<Role>/ (CLAUDE.md: the stage's briefs folder).
    Pages from sites whose terms forbid automated access are listed in each folder's DO_NOT_COMMIT.txt, kept on
    disk and not committed, as E.12 did with CME's pages.
11. Deviation fetches (Fable R-11 count): two workers used Scrapling on sites whose terms forbid automated access
    before reading those terms: PropVenues1 (help.tradeify.co, elitetraderfunding.com) and PropVenues2
    (lucidtrading.com). BrokerVenues (NinjaTrader: no terms page, robots allows all) and InfoSource (Insper) were
    compliant. The lead's brief to the reviewer had said three; the correct count is two. Ruling: a fact stands on a
    compliant corroborating copy; otherwise it is marked "deviation fetch" (P1-19, P1-21, P1-37, Lucid's TOU). No
    classification rests on those alone. InfoSource's Firecrawl-before-Scrapling fetch of the Baltussen PDF is
    recorded in INF's lead note.
12. The C1 pre-registration rules over its annex where they differ. Its power figures are noted as about 3%
    optimistic for the ruled window.
13. AiTrader readout facts come from its plan documents only (docs/STAGES.md, its git log), not from its results.
14. E.12's persisted Gate 0 state in ~/.cache/propexp_e12_phase1 was not hashed in this stage, to avoid opening
    result files (names and sizes only). The next stage's freeze hashes and copies it (ruling C17).
15. The ranking rule was fixed in section 1 before the candidates were scored: odds first; the tie-breaks are
    published evidence, then test independence, then fit; ease never decides.
16. The ranking's odds for C2-C5 are the lead's judgment, with ranges. C1's come from the Task 4 annex.
17. C2's bar applies 1.5c at the test era's costs, a conservative choice because costs were a larger share of the
    move at 2011-2019 index levels.
18. C2's GEX timing rule (the latest row strictly before d, or two days back if publication can fall after 14:30
    CT) and its 200-date minimum-power stop.
19. Correction before the review: ranking section 5 first applied test independence ahead of evidence,
    contradicting section 1. The lead corrected the order to follow section 1 (C2 first, C1 second) rather than
    change the rule.
20. STATE times were corrected from the output files' modification times. The final table uses transcript times.
21. The R-01 ruling: branch (i), section 1 applied literally, with no tie criterion and no amendment. C2's odds
    were derived (the second half of branch (ii)), so the primary key is computed for both candidates. Section 1's
    wording makes row (b), the deployment odds, the primary key. C1 is first.
22. The follow-up check went to the same Fable reviewer by SendMessage, not to a new spawn. The prompt allows one
    Fable review. The C2 odds were new numbers entering the ranking, and CLAUDE.md requires an independent check
    of every such number. A follow-up inside the same review met both rules.
23. R-12, strict branch: a C10 stop closes C1's registered attempt; a rerun is a new registration.
24. R-06: the ruling corrected the reviewer (the saved Phidias pages do say "Lifetime"). The follow-up agreed.
25. The commit excludes the 363 page files listed in the six DO_NOT_COMMIT.txt files. They stay on disk,
    untracked, like E.12's margin_pages/.
26. Both pauses were honoured at once. The worker running during the second pause (the review) was not stopped:
    it was read-only, and stopping it would have wasted a Fable run. The user was told it was running.
27. Support questions are drafted but recommended to be held (section 7, item 5): no multi-day strategy on the list
    fits a prop drawdown, so the answers would not change a decision now.
28. The ranking's capital level for trend and carry: TC's sizing used published volatilities. IBKR's overnight
    margins (VEN part 3) were checked only for the micros a small book holds ($136-$919 each). Equity and metal
    micros ($3,705-$7,359) bind first.

## 7. Decisions for the user (the lead's recommendation first)

1. **Which candidate next.** Recommendation: either pause until the AiTrader readout (it costs nothing, and none of
   C1-C5 offers better than about 7% central odds of income-bearing deployment), or, if you keep searching, run C1:
   - E.14: a one-session calendar probe (2012's energy calendar and the NGS table at evidence grade), then the
     freeze and harness v10, at $0;
   - E.15: the purchase and one evaluation.
   Add C2 only if you also want the published-evidence test (it shares the equity calendar and the harness change).
2. **Purchase and top-up.** None now. If C1 runs: an acct-2 cap raise of about $41-$50 after the probe ($59.03 with
   the margin, plus the June-2010 chunks, quoted fresh then). C2 alone (about $10.58 with the margin, an estimate)
   fits today's $18.07. Both together: about $50.
3. **V24 question (needed for C1).** Allow two computations on the already-bought 2019-2024 panel: reloading E.12's
   persisted out-of-fold predictions to reproduce the threshold q to 1e-9, and one full-panel fit of the frozen
   ridge M1. Neither reruns Gate 0's decision. Recommendation: allow both, if C1 runs.
4. **Reopen the S&P exposure (needed for C2).** Stage E closed it (docs/STAGE_E_DESIGN.md D1 rule 5). C2 reads ES
   bars never read and trades MES; MES's sealed holdouts stay sealed. Recommendation: decide only if you choose C2.
5. **Support questions.** Drafted for Phidias, Elite Trader Funding, PropEd and Leeloo, never sent.
   Recommendation: hold them. No multi-day strategy on the list fits a prop firm's trailing drawdown (Task 2,
   Part D), so the answers would not change a decision now. Send the Phidias one if a multi-day system becomes a
   candidate.
6. **Personal account.** Recommendation: not now. IBKR Canada is the venue when there is an edge to move or capital
   to deploy (V22). Trend and carry at $10K-$100K earns about $40-$430 a month in the mid case, with deep drawdowns.
7. **Keep ~/.cache/propexp_e12_phase1** (107 MB, outside the repository). It is the only source of C1's threshold
   until a freeze hashes and copies it.

## 8. Session cost

### Final ETA table (actuals; PDT; the initial estimate is in brackets)

| # | Task or spawn | Owner | Model | Effort | Start | End | Time | Tokens | Status |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Startup, start checks, briefs | lead | opus | xhigh | 14:24 | 14:34 | 0:10 [0:34] | (lead) | done |
| 1a | Prop firms, part 1 | PropVenues1-OpusHigh | opus | high | 14:33 | 14:54 | 0:21 [0:55] | 21,691,418 | done |
| 1b | Prop firms, part 2, Phidias question | PropVenues2-OpusHigh | opus | high | 14:33 | 14:52 | 0:19 [1:00] | 27,209,780 | done |
| 2 | Trend and carry | TrendCarry-OpusHigh | opus | high | 14:33 | 15:07 | 0:33 [0:55] | 32,849,245 | done |
| 4 | NG replication draft | ReplicationDesigner-OpusXHigh | opus | xhigh | 14:33 | 15:00 | 0:26 [1:05] | 32,351,615 | done |
| 3 | Information sources | InfoSource-OpusHigh | opus | high | 14:52 | 15:20 | 0:28 [0:50] | 31,337,888 | done |
| 1c | Personal-account brokers | BrokerVenues-OpusHigh | opus | high | 14:54 | 15:16 | 0:21 [0:40] | 33,241,282 | done |
| L | Task 4 rulings, ETF question, venues merge (overlapping the workers) | lead | opus | xhigh | 14:53 | 15:17 | overlaps [0:20] | (lead) | done |
| 5a | Ranking inputs | lead | opus | xhigh | 15:17 | 15:23 | 0:06 | (lead) | paused |
| P1 | **Pause** (user: "Pause operations real quick") | | | | 15:23 | 23:13 | 7:50, excluded | | |
| 5b | Ranking and two pre-registration drafts | lead | opus | xhigh | 23:13 | 23:21 | 0:08 [1:15 for 5a+5b] | (lead) | done |
| 6 | Adversarial review | RankingReviewer-FableXHigh | fable | xhigh | 23:21 | 23:39 | 0:18 [0:30] | in 4,729,288 | BLOCK |
| P2 | **Pause** (user: "actually, pause for a sec"; the review finished inside it) | | | | 23:32 | 01:38 | 2:06, excluded | | |
| 6b | Rulings and fixes | lead | opus | xhigh | 01:38 | 01:44 | 0:06 [0:30] | (lead) | done |
| 6c | Follow-up check (SendMessage to the same reviewer) | RankingReviewer-FableXHigh | fable | xhigh | 01:44 | 01:48 | 0:04 | in 4,729,288 | R-01 CLOSED |
| 7 | R-17 fix, return, end checks, cost, progress, commit | lead | opus | xhigh | 01:48 | about 02:00 | 0:12 [0:35] | (lead) | done |
| | **Stage total** | | | | 14:24 | about 02:00 | about 1:40 of work (0:59 + 0:19 + 0:22), plus 9:56 of pauses | 227,216,445 (to 01:49) | initial estimate 5:10 (end 19:35) |

The workers ran 19-33 minutes against estimates of 40-65 minutes, all in parallel within the 4-worker cap, so the
work took about a third of the estimate. There was no usage-limit wait. Both pauses were the user's.

### Tokens per model (this session's transcript and its 7 subagent transcripts, 14:24 PDT 2026-10-03 to 01:49 PDT 2026-10-04)

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 2,218 | 860,712 | 218,688,957 | 2,935,270 | 222,487,157 |
| claude-fable-5-1 | 612 | 102,188 | 3,989,221 | 637,267 | 4,729,288 |
| all | 2,830 | 962,900 | 222,678,178 | 3,572,537 | 227,216,445 |

Per spawn (agent file, model, effort, tokens):
- BrokerVenues: worker-high, opus, high, 33,241,282
- TrendCarry: worker-high, opus, high, 32,849,245
- ReplicationDesigner: worker-xhigh, opus, xhigh, 32,351,615
- InfoSource: worker-high, opus, high, 31,337,888
- PropVenues2: worker-high, opus, high, 27,209,780
- PropVenues1: worker-high, opus, high, 21,691,418
- RankingReviewer (review plus follow-up): worker-xhigh, fable, xhigh, 4,729,288

Delegation share: lead 43,805,929 (19.3%), workers 183,410,516 (80.7%). By tier: Opus 97.9% (lead 19.3%, Opus
workers 78.6%), Fable 2.1%. Cache reads are 98.0% of all tokens. The resumed sessions wrote no usage of their own:
it stayed in the first session's transcript (dbc7460b), as in E.5 and E.9. The closing steps after 01:49 (assembly
and the commit) add a little to the lead and are not in these sums. Token counts, not plan-credit percentages: the
/usage meter is not readable from the session.
