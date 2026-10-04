# Stage E.13 STATE (research and scoping; no market data, no purchase)

Prompt: docs/prompts/STAGE_E.13.md (commit 5d85924). Lead: Opus 5.5 xhigh. Session dbc7460b-72c3-4537-8327-d14819b62f5c.
Times PDT. On resume: read this file first, skip finished tasks, check each running worker's output file on disk
before re-spawning (memory: agent-cut-by-usage-limit).

## Task status

| Task | Owner | Model/effort | Status | Start-end PDT | Artifact |
|---|---|---|---|---|---|
| 0 Startup | lead | opus xhigh | done | 14:24-14:34 | reports/stage_e13_briefs/start_checks.txt, checks.sh |
| 1a Prop firms part 1 | PropVenues1-OpusHigh | opus high (worker-high) | done | 14:34-14:54 | reports/stage_e13_venues_part1.md |
| 1b Prop firms part 2 + Phidias | PropVenues2-OpusHigh | opus high (worker-high) | done | 14:34-14:52 | reports/stage_e13_venues_part2.md, reports/stage_e13_phidias_question.md |
| 1c Personal-account brokers | BrokerVenues-OpusHigh | opus high (worker-high) | done | 14:55-15:16 | reports/stage_e13_venues_part3_brokers.md |
| 1 merge | lead | opus xhigh | done | 15:16-15:17 | reports/stage_e13_venues.md |
| 2 Trend and carry | TrendCarry-OpusHigh | opus high (worker-high) | done | 14:34-15:07 | reports/stage_e13_trend_carry.md |
| 3 Information sources | InfoSource-OpusHigh | opus high (worker-high) | done | 14:53-15:20 | reports/stage_e13_info_sources.md |
| 4 NG replication draft | ReplicationDesigner-OpusXHigh | opus xhigh (worker-xhigh) | done; lead rulings applied | 14:34-15:00 (rulings 15:01) | reports/stage_e13_ng_replication_draft.md |
| 5 Ranking, prereg drafts | lead | opus xhigh | done | 15:21-15:26 and 23:13-23:20 | reports/stage_e13_ranking.md, reports/stage_e13_prereg_ngrepl.md, reports/stage_e13_prereg_gexmom.md |
| 6 Review | RankingReviewer-FableXHigh | fable xhigh (worker-xhigh) | done: BLOCK (1 B, 7 SF, 8 N); follow-up R-01 CLOSED, APPROVE WITH FIXES (R-17 SF, R-18/R-19 N) | 23:21-23:39; follow-up 01:44-01:48 | reports/stage_e13_review.md, reports/stage_e13_rulings.md |
| 7 Return, commit | lead | opus xhigh | done | 01:48-01:51 | reports/E.13_RETURN.md, progress.md, docs/STAGES.md |

## Log

- 14:24 session start. 14:25 start checks: all pass (reports/stage_e13_briefs/start_checks.txt). HEAD 5d85924
  (the prompt commit); tree clean but for the expected untracked reports/stage_e12_briefs/margin_pages/ and
  this stage's reports/stage_e13_briefs/. Holdout unlocks 0 everywhere; REGISTRATION.md 0 bytes; v9 preflight
  OK 7fd757f6...; ledger 27018 lines sha256 6a074c14...; acct-1 headroom $1.609980, acct-2 $18.070270;
  v2 freeze OK 91 files.
- Lead choices so far (go to the return's section 6): OC-1 Task 1 split into three workers (two prop-firm
  halves, one broker); OC-2 the prompt's "reports/stage_e12_purchase.md" does not exist, the 2010-extension
  record is reports/stage_e12_quotes_ext2010.md/.json (NG $8.52, 106/112 chunks, 2010-01..06 unpriced); OC-3
  no Databento quote run: E.12's record covers NG and every leg, so the ledger stays unchanged; OC-4 Task 2
  tabulates ruin over a grid of drawdown sizes so it does not wait for Task 1.
- 14:34 batch 1 spawned: PropVenues1, PropVenues2, TrendCarry (worker-high, opus) and ReplicationDesigner
  (worker-xhigh, opus). Briefs: reports/stage_e13_briefs/research_rules.md, brief_propvenues.md,
  brief_trendcarry.md, brief_ngreplication.md. Next: write brief_infosource.md and brief_brokers.md; spawn
  InfoSource and BrokerVenues when slots free.
- 14:53 PropVenues2 done (19 min): venues_part2.md, phidias_question.md, pages/PropVenues2 (156 pages, 16
  WebSearch). Deviation: 3 lucidtrading.com pages fetched by Scrapling before its terms (robots ban) were read;
  listed in DO_NOT_COMMIT.txt. 14:52 InfoSource spawned (brief_infosource.md).
- 14:55 PropVenues1 done (21 min): venues_part1.md, pages/PropVenues1 (77 pages, 11 WebSearch). ETF Direct To Funded
  and Diamond Hands UNCLEAR (AI/automation ban unless authorized in writing); the other six NOT PERMITTED.
  Deviation: Scrapling on help.tradeify.co (6) and elitetraderfunding.com (2) before their terms were read;
  listed in DO_NOT_COMMIT.txt. Apex site down: Wayback captures. 14:54 BrokerVenues spawned (brief_brokers.md).
- 15:00 ReplicationDesigner done (26 min): ng_replication_draft.md (38.7 KB), pages/ReplicationDesigner (21 files,
  8 WebSearch). M1 applies ((a) and (b) fail); 29 of 64 features live on NG rows; legs NQ ZN 6E GC ZC (CL never
  live on NG rows); data from 2010-06-06; purchase $57.31 quoted ($59.03 x1.03), top-up $40.96; odds ~12%
  (7-35%); recommends run later after a one-session calendar probe; 3.5-4 sessions mostly calendar work.
- 15:01 Lead rulings on C1-C21 written into the draft's section 10: all accepted except C5 (fixed S^R 2010-06-07,
  no volume read) and C6 (end 2019-04-30, no May-2019 splice); C19 user decision. OC-6 ETF question appended to
  reports/stage_e13_phidias_question.md section 4 by the lead. E.12 persisted Gate 0 state:
  ~/.cache/propexp_e12_phase1 (107 MB, outside the repo; names/sizes only recorded, contents not read): the only
  source of q, so the user must not clean ~/.cache.
- Running: TrendCarry, InfoSource, BrokerVenues. Next: merge venues (lead) when BrokerVenues returns; Task 5.
- 15:08 TrendCarry done (34 min): trend_carry.md, pages/TrendCarry (43 raw + 30 text, 19 WebSearch). SG Trend
  (net) Sharpe 0.24 (2010-2025), 0.30 (2013-2025), worst DD -20.6%; AQR TSMOM (gross) 0.31 (2012-2025); AQR
  carry -0.19 (2013-2025); mid-case income at a 25% target $40/$89/$189/$428 a month at $10K/$25K/$50K/$100K;
  prop fit fails (allowed daily sigma ~D/27 vs $2,432 for one micro per exposure). Assumptions: $3 RT for
  untraded micros, average correlation 0.125.
- 15:18 BrokerVenues done (21 min): venues_part3_brokers.md, pages/BrokerVenues (81 files, 28 WebSearch). IBKR
  Canada PERMITTED (CIRO, API, USD 0 minimum, MES USD 0.61/side all-in, MES overnight initial USD 3,704.55);
  Wealthsimple HUMAN-IN-THE-LOOP (no API); NinjaTrader and Tradovate exclude BC; 7 brokers UNCLEAR (BCSC
  eligible-derivatives-party exemption); bank-owned brokers, Questrade and Qtrade offer no futures.
- 15:17 Task 1 merged by the lead: reports/stage_e13_venues.md (lead summary by bucket, one combined prop-firm
  table of 25 rows, the broker tables, every part's classification, sources and gaps verbatim). Part files kept.
  Waiting: InfoSource. Next: Task 5.
- 15:17 correction: end times above re-read from the output files' modification times (PDT). BrokerVenues ran
  14:55-15:16, the merge 15:16-15:17; InfoSource has run since 14:53. The final table uses transcript times.
- 15:20 InfoSource done (28 min): info_sources.md (45 KB), pages/InfoSource (~54 pages, 39 WebSearch, 3 Firecrawl).
  Best: (1) dealer gamma (GEX) conditioning late-session momentum (Baltussen et al. JFE 2021; post-2013 decline
  reported; MES unconditional null in D.1; free SqueezeMetrics GEX from 2011-05-02); (2) NOAA GFS forecast
  revisions for NG (one 2025 daily paper; archive found only from 2021); no third. Lead error OC-7: the brief
  gave docs/ for the K1-K8 catalogs; they are in reports/.
- 15:21 Task 5 started (lead). ~15:26 USER PAUSE ("Pause operations real quick"); no worker running; nothing for
  Task 5 on disk yet. 23:13 resumed on the user's "please continue".
- 23:20 Task 5 done: ranking (criteria x candidates, AiTrader as a column): C1 NG replication > C2 GEX late-session
  momentum > C3 trend+carry personal IBKR > C4 GFS revisions > C5 trend+carry swing prop; C0 pause stated as a
  reasonable alternative. Prereg drafts for C1 and C2 (nothing frozen). Annex sha256 at drafting:
  reports/stage_e13_ng_replication_draft.md 9685fe802ee36b534b32171fdfb8d7def78c2ddba8d48c263c4dab0ff50d20bf.
  Draft hashes (prefixes): e4106799b2781972... reports/stage_e13_ranking.md; 6f0ddc3e35ace532... reports/stage_e13_prereg_ngrepl.md; 248743b4fbd2eb82... reports/stage_e13_prereg_gexmom.md
  OC-8 ranking rule fixed before scoring (odds first; tie-break evidence, then test independence, then fit; ease
  never decides). OC-9 C2's bar uses 1.5c at the test era's costs (conservative). OC-10 C2 GEX timing rule and the
  200-date minimum-power stop. Next: Task 6, RankingReviewer-FableXHigh.
- 23:21 Correction before the review: ranking section 5 had applied test independence ahead of published evidence,
  contradicting section 1's fixed tie-break order. Corrected to follow section 1: C2 first, C1 second (odds tied
  within ranges). First version sha256 prefix e4106799b2781972 (above). Recommendation now: C2 as the next stage
  (about $10 of data within funds; S&P reopening a user decision), C1 optional companion. OC-11.
- 23:21 Task 6 spawned: RankingReviewer-FableXHigh (worker-xhigh, fable), brief_rankingreviewer.md. The resumed
  session writes task files under a new session folder (11d74ea4-...); the cost step must check both session ids.
- ~23:30 USER PAUSE 2 ("actually, pause for a sec"), with the reviewer running; it finished at about 23:40
  while paused. 01:38 (2026-10-04) resumed on the user's "continue please".
- 01:40-01:44 Task 6b rulings (reports/stage_e13_rulings.md): R-01 ACCEPTED, branch (i), section 1 applied
  literally, primary key = row (b), with C2's odds derived (reports/stage_e13_briefs/c2_odds.py/.out): C1 first
  (b central 6.6% vs 5.0%, skeptical 1.8% vs 0.8%), C2 second. R-02..R-15 fixed as listed. Ranking v1 reconstructed
  byte-identically and kept; v2 kept. Full sha256 (R-08):
  7e89801b4671875513085d3b070ebe2d274c71b89ca7ffb0eaa51d4ca0e0a0b7  reports/stage_e13_ranking.md
  a16e860003a80806d97ff32e08e1265ae8feb1acb236153064bf32fb60714f43  reports/stage_e13_prereg_ngrepl.md
  2969a6637b9ce4ebf36472abfde84940d54b8ab540f022518a216ec2c8f617fd  reports/stage_e13_prereg_gexmom.md
  e4106799b27819720155833b6a3e128b3215ee440f5a0e963eda011f036297fe  reports/stage_e13_briefs/ranking_v1.md
  dcba2f0a7c84b27bdaeb4201fcacc5e84dbb718f5ee0b98dacfed7cc996cc594  reports/stage_e13_briefs/ranking_v2.md
  01:44 follow-up check sent to the same reviewer (SendMessage; no new spawn). Next: Task 7.
- 01:49 Follow-up check done: R-01 CLOSED, every odds cell reproduced; R-17 (SHOULD FIX, disclose order
  sensitivity), R-18 and R-19 (NOTES) applied in the ranking; rulings updated. Every BLOCKING and SHOULD FIX fixed.
  Task 7 started.
- 01:51 Task 7: end checks 01:49 all pass (end_checks.txt; ledger unchanged); cost from cost.py (cost_raw.txt:
  227,216,445 tokens to 01:49); reports/E.13_RETURN.md, the progress entry and the docs/STAGES.md line written.
  Commit "Stage E.13 research and scoping" (no push), excluding the 363 DO_NOT_COMMIT page files (left on disk,
  untracked) and E.12's margin_pages/. STAGE COMPLETE.
