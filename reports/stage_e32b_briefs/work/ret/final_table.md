Final table (times PDT from the STATE file and the transcripts' first and last records; a resumed worker's span covers
all its runs; tokens from the transcripts):

| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|
| 1 | Lead session 1: start checks, Fable probe, spec (hashed 22:32:14), reader rules | opus (max) | 22:06-22:35 | 29 min | 13,097,805 (lead) | done; wipe at ~345k tokens |
| 2 | FableProbe-FableMed | fable (medium) | 22:22 | <1 min | 65,309 | done: Fable available |
| 3 | Planned wipe 1 (nothing running) | - | 22:35-22:40 | 5 min | - | pause, not counted |
| 4 | Lead session 2: reader and wave-B briefs, rulings LR-F3 to LR-D3, readings | opus (max) | 22:40-00:56 | 2 h 16 min | 19,115,950 (lead) | done; wipe at ~312k |
| 5 | CrudeReader, NatgasReader, MetalsReader, GrainsReader, RatesReader, EquityReader (-OpusHigh) | opus (high) | 22:48-23:09 | 15-21 min each | 32,162,972; 28,090,644; 22,423,835; 31,237,627; 23,549,545; 22,171,338 | done (F2) |
| 6 | FXReader-OpusHigh, CryptoReader-OpusHigh | opus (high) | 23:03-23:21 | 15, 18 min | 21,236,586; 21,612,823 | done (F2) |
| 7 | VolCoder-OpusXHigh | opus (xhigh) | 23:05-23:17 | 12 min | 5,038,247 | done (F3) |
| 8 | FirmRules-OpusHigh | opus (high) | 23:07-23:34 | 27 min | 27,291,824 | done |
| 9 | ScoreCoder-OpusXHigh | opus (xhigh) | 23:09-23:39 | 29 min | 14,892,068 | done |
| 10 | EconSetup-OpusXHigh | opus (xhigh) | 23:10-00:55 | 1 h 45 min (span) | 28,798,889 | done (econ code, E.28 regression) |
| 11 | DataAccess-SonnetHigh | sonnet (high) | 23:17-23:33 | 16 min | 14,815,324 | done |
| 12 | AttentionCounter-HaikuMed | haiku (medium) | 23:18-23:19 | 1 min | 672,961 | done |
| 13 | HoldingCoder-OpusXHigh | opus (xhigh) | 23:19-23:33 | 13 min | 7,374,669 | done |
| 14 | ClosedLines-SonnetHigh | sonnet (high) | 23:21-23:28 | 7 min | 8,793,559 | done |
| 15 | IdeaFamilies-OpusHigh | opus (high) | 23:29-23:41 | 12 min | 10,643,052 | done |
| 16 | NonProp-SonnetHigh | sonnet (high) | 23:33-23:42 | 9 min | 10,188,926 | done |
| 17 | Planned wipe 2 (nothing running) | - | 00:56 | <1 min | - | pause, not counted |
| 18 | Lead session 3: rulings LR-SC to LR-Q3b, econ supervision, score runs, F5, R3 runs, R4 text, review briefs | opus (max) | 00:57-07:29 | 6 h 32 min (5 h 17 min without the pause) | 74,510,690 (lead) | done; wipe 07:25 |
| 19 | Econ pass 1 (script, 8 workers, 224 jobs) | - | 01:17-05:24 | 4 h 07 min | - | done; kept running through the pause |
| 20 | FactTable-OpusHigh (resumed twice) | opus (high) | 01:06-03:22 | 2 h 16 min (span, incl. pause) | 39,400,501 | done; masks rebuilt twice for leaks |
| 21 | BlindScorer-OpusXHigh (rater 1) | opus (xhigh) | 01:36-01:53 | 17 min | 15,031,894 | cut by the usage limit; superseded (inter-rater only) |
| 22 | FactAuditor-FableXHigh (resumed once) | fable (xhigh) | 01:36-03:26 | 1 h 50 min (span, incl. pause) | 5,783,847 | done; cut at the end of run 1; B1, B2 |
| 23 | Usage-limit pause (5-hour window) | - | 01:56-03:11 | 1 h 15 min | - | pause, not counted |
| 24 | BlindScorer2-OpusXHigh (rater 2) | opus (xhigh) | 03:29-03:55 | 26 min | 12,026,958 | done |
| 25 | VariantBuilder-SonnetHigh (resumed twice) | sonnet (high) | 03:32-05:40 | 2 h 09 min (span) | 4,185,724 | done |
| 26 | Econ S_mean (script) | - | 03:53-04:05 | 12 min | - | done |
| 27 | F5Runner-OpusXHigh | opus (xhigh) | 03:57-04:07 | 10 min | 7,640,619 | done; found the attention-file format defect (LR-ATT) |
| 28 | Lead wait while econ pass 1 ran | - | 04:09-05:24 | 1 h 15 min | - | stage compute, counted |
| 29 | Econ pass 2 (script, E_dir 30/120/240) | - | 05:26-07:28 | 2 h 02 min | - | done |
| 30 | DossierWriter-OpusXHigh | opus (xhigh) | 05:27-05:59 | 32 min | 29,440,132 | done |
| 31 | RankingWriter-OpusHigh (resumed) | opus (high) | 05:27-05:43 | 16 min | 13,086,414 | done |
| 32 | ScopeWriter-OpusHigh (resumed) | opus (high) | 05:27-05:38 | 11 min | 6,819,605 | done |
| 33 | CombinationScorer-OpusXHigh | opus (xhigh) | 06:01-06:19 | 18 min | 4,504,982 | done |
| 34 | RecsDrafter-OpusXHigh (resumed twice) | opus (xhigh) | 06:21-07:06 | 45 min | 38,031,774 | done; its fact check reversed the 06:21 F01 ruling (LR-Q3a) |
| 35 | RankingReviewer-FableXHigh (RV1) | fable (xhigh) | 06:58-07:25 | 27 min | 8,010,050 | done: PASS, 0 / 3 / 13 |
| 36 | RecsReviewer-FableXHigh (RV2) | fable (xhigh) | 06:58-07:18 | 20 min | 5,465,653 | done: PASS with one ruling, 1 / 6 / 7 |
| 37 | Planned wipe 3 (nothing running) | - | 07:29-08:39 | 1 h 11 min | - | pause, not counted |
| 38 | Lead session 4: plan, LR-Q3b text, q3bleg, scope, NOTE fixes, return, progress, STAGES, end checks, cost | opus (max) | 08:39-09:45 | 1 h 05 min | 28,042,815 (lead, to the cutoff) | done |
| 39 | ScoreFixer-OpusHigh (resumed once) | opus (high) | 08:47-08:57 | 9 min | 8,892,840 | done; no rank change |
| 40 | R1Fixer-OpusHigh | opus (high) | 08:47-08:56 | 9 min | 8,951,432 | done; corrected three of RV2's statements |
| 41 | CostTabler-SonnetHigh | sonnet (high) | 08:54-08:56 | 2 min | 1,022,642 | done |
| 42 | DelegationTabler-HaikuMed | haiku (medium) | 08:55-09:01 | 7 min | 3,468,883 | done |
| 43 | RecsAssembler-OpusXHigh | opus (xhigh) | 08:57-09:22 | 25 min | 27,063,610 | done |
| 44 | FixVerifier-FableXHigh | fable (xhigh) | 09:23-09:41 | 18 min | 4,578,675 | done: PASS, 0 / 0 / 7 |
| all | Stage E.32b | lead (4 sessions) + 38 spawns | 22:06-09:45 | 11 h 39 min wall-clock; 9 h 07 min work | 709,233,693 (lead 134,767,260; workers 574,466,433) | initial estimate (session 1, 22:35): T0 + 12:00 from 22:40, about 10:40; session 2's table (22:48): 09:20; session 4's (08:44): 11:07, revised 10:43; actual 09:45 |
