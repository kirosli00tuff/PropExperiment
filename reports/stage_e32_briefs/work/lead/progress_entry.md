
## 2026-10-27 — Stage E.32: ZM discovery design: test window sealed, methods brief, frozen discovery protocol for E.33; N = 538

Prompt docs/prompts/STAGE_E.32.md (V51). Return: reports/E.32_RETURN.md. Deliverables: reports/stage_e32_test_seal.md,
reports/stage_e32_data_facts.md, reports/stage_e32_methods_brief.md, reports/stage_e32_discovery_protocol.md (FROZEN
v1.0, sha256 c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05, also in
reports/stage_e32_discovery_protocol.sha256); working files reports/stage_e32_briefs/; STATE reports/stage_e32_STATE.md.
Holdout unlocks_logged 0 at start, at every resume and at the end; REGISTRATION.md 0 bytes; nothing registered; no
Databento or TopstepX call; no data dated 2017-05-01..2020-11-30 or from 2024-03-01 opened; nothing pushed.

**What ran.** Three lead sessions (Opus 5.5 xhigh): a51871c6 (10-26 22:21 to 10-27 00:51), 900dd54a (02:32 to 08:02)
and 89bc0cd0 (08:39 to the end), with three usage-limit pauses, one planner pause and one planned context wipe. Part 0
sealed 114 ZM/ZS/ZL files touching 2017-05..2020-11 under a new soy-test seal (own manifest, unlock log and tests).
Fourteen readers (Opus high; X1 on Sonnet before the user's never-Sonnet rule, re-verified on Opus) wrote Parts R, M
and F. Four MathReviewers (Fable xhigh) checked Part M. The lead wrote the protocol; four ProtocolReviewer lenses
(Fable xhigh) raised 6 BLOCKING and 39 SHOULD FIX items on v0.2, all applied (v0.3); four FixVerifier re-checkers,
two FixSpotCheck checkers and one FinalDiffCheck (all Fable xhigh) found and fixed the residue (v0.4 to v0.6); frozen
as v1.0 at 13:08 PDT on 10-27. Every reviewer's model was confirmed from its transcript (claude-fable-5-1).

**Result.** The protocol searches four families (crush-residual reversion; ZS/ZL leading ZM; ZM order flow and book
state; ZM's own path), each with a context block plus all pooled: 5 sets x 6 executable labels x 10 grid points (6
logistic, 4 LightGBM) = 300 configurations, N 838 after E.33. Binding discovery threshold: daily Sharpe 0.2007 (t
5.66), about 1.22 ticks net per 15-minute trade at 4 a day. ZM MBO starts 2017-05-21, so the test is
2017-05-22..2020-11-30 (870 dates after burn-in); its bar (0.1649) has 80% power at a true 0.1936. Honest odds about
3% (1-6%) that this route ends with a passing candidate. Full pytest: 8,116 passed, 1 failed (the known
test_h6_rod_run failure; it fails identically at HEAD 3a75f3b, so E.32 did not cause it), 5 skipped, 3 xfailed.

**For the user** (return section 7): D1 keep the protocol-added test DSR (decide before E.33's C1); D2 amend V14 (c)
for this test; D3 launch E.33; D4 the test-data quote plan (about 134 USD by proportion, an estimate; only after a
funded account and a non-empty Tier A); D5 remove DATABENTO_API_KEY3 from .env; D6 the test window starts
2017-05-22; D7 re-pin or xfail the h6 test; D8 E.33's deadlines live in its prompt.

### Session cost

Tokens come from the transcripts, each message at its final usage, counted by
reports/stage_e32_briefs/work/lead/cost32.py (reports/stage_e10_briefs/cost.py's scan, recursive over subagents/**,
so workflow agents count) over the three lead sessions a51871c6-ae95-4aa9-8b23-0daf24b41dc1,
900dd54a-de4d-4012-a455-b0efd91bbcf0 and 89bc0cd0-ddc5-469d-b633-94a1a978350a and all their subagents, from
2026-10-27T05:00Z to 20:11:27Z (13:11 PDT); the last calls (filling these tables, the commit and the closing reply)
are not counted. Output: reports/stage_e32_briefs/work/lead/cost_raw.txt; per-agent lines in deleg_all.tsv. Token
counts, never estimates; plan-meter percentages are the user's reading.

Wall clock: 2026-10-26 22:21 to 2026-10-27 13:11 = 14 h 50 min. Pauses, not work: PAUSE 1 (planner) 23:16-00:14
(58 min); USAGE LIMIT 1 00:51-02:32 (1 h 41 min); USAGE LIMIT 2 about 03:12-07:31 (4 h 19 min); the planned context
wipe 08:02-08:39 (37 min); USAGE LIMIT 3 08:57-12:35 (3 h 38 min): 11 h 13 min in all. Work: 3 h 37 min.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 5,100 | 2,296,520 | 440,697,045 | 7,738,397 | 450,737,062 |
| claude-fable-5-1 | 16,240 | 1,211,290 | 72,087,677 | 4,751,351 | 78,066,558 |
| claude-sonnet-5-5 (X1 only) | 200 | 72,108 | 16,167,864 | 260,941 | 16,501,113 |
| all | 21,540 | 3,579,918 | 528,952,586 | 12,750,689 | 545,304,733 |

Delegation share: lead 122,728,688 (22.5%; sessions 48,849,791 + 43,326,750 + 30,552,147), workers 422,576,045
(77.5%): Opus workers 328,008,374 (60.2% of all), Fable workers 78,066,558 (14.3%), Sonnet 16,501,113 (3.0%, the one
X1 run before the never-Sonnet rule). Cache reads are 97.0% of all tokens. Per worker spawn (agent file, model,
effort, tokens): the worker rows of the final table below and section 4 of the return. No max effort was used; the
cost driver was the 18 Opus reader runs (re-spawns included) with long saved-page contexts, 60% of the total.

Final table (times PDT; 10-27 unless marked; tokens by transcript; lead tokens per session in the lead rows at the
end):

| # | Task / agent | Model (effort) | Start-end | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|
| 1 | Lead: read inputs, plan, estimate table, start checks | opus (xhigh) | 10-26 22:21-22:42 | 21 min | (lead) | done |
| 2 | Lead: Part 0 seal (tool, 26 tests, 114 files), store-test subsets | opus (xhigh) | 10-26 22:42-23:01 | 19 min | (lead) | done |
| 3 | ValidationMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:13 | 10 min | 10,800,750 | done |
| 4 | LeadLagMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:15 | 12 min | 14,919,332 | done |
| 5 | CrushEconomics-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:16 | 13 min | 14,081,770 | done |
| 6 | EventStructure-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:16 | 13 min | 12,607,561 | done |
| 7 | OrderFlowMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:03-23:15 | 12 min | 17,711,143 | done |
| 8 | FableProbe-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-26 23:03-23:03 | 0 min | 63,019 | done |
| 9 | ExposureInventory-SonnetMed (worker-medium, wf_2ed35392-831) | sonnet-5-5 (medium) | 10-26 23:03-23:14 | 11 min | 16,501,113 | done |
| 10 | Lead: seal doc, P1 hash check 156/156, p7_thresholds.py, design notes | opus (xhigh) | 10-26 23:05-23:15 | 10 min | (lead) | done |
| 11 | LabelsMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-26 23:14-23:15 | 1 min | 1,451,306 | done |
| 12 | PAUSE 1 (planner request) | - | 10-26 23:16-10-27 00:14 | 58 min | - | not work |
| 13 | Lead: resume, M6/P6 execution variants, X1 corrections to the seal doc, cftc terms, reviewer briefs | opus (xhigh) | 10-27 00:15-00:51 | 36 min | (lead) | done |
| 14 | ValidationMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:32 | 16 min | 12,877,539 | done |
| 15 | LeadLagMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:28 | 12 min | 9,060,031 | done |
| 16 | CrushEconomics-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:23 | 7 min | 5,292,706 | done |
| 17 | OrderFlowMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:29 | 13 min | 13,300,400 | done |
| 18 | X1Verifier-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:29 | 13 min | 24,233,595 | done |
| 19 | EventStructure-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:16-00:30 | 14 min | 17,687,636 | done |
| 20 | LabelsMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:23-00:39 | 16 min | 16,865,073 | done |
| 21 | PowerStability-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:29-00:44 | 16 min | 11,970,110 | done |
| 22 | DataFacts-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:29-00:46 | 17 min | 13,560,264 | done |
| 23 | PropStrategyMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:29-00:50 | 21 min | 14,633,090 | done |
| 24 | ModelsMath-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:30-00:51 | 21 min | 14,327,082 | done |
| 25 | SoyMicrostructure-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:32-00:49 | 17 min | 25,547,321 | done |
| 26 | AgDesks-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:39-00:51 | 12 min | 14,158,856 | done |
| 27 | AlphaProcess-OpusHigh (worker-high, wf_2ed35392-831) | opus-5-5 (high) | 10-27 00:44-00:51 | 7 min | 6,676,053 | done |
| 28 | MLEvidence-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 00:46-00:50 | 3 min | 3,081,497 | done |
| 29 | MathReviewerC-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 00:50-00:51 | 1 min | 1,444,111 | done |
| 30 | USAGE LIMIT 1 | - | 10-27 00:51-02:32 | 101 min | - | not work |
| 31 | Lead: resume (continuation script), test-bar ruling, p7_final.py, protocol v0.1, brief front | opus (xhigh) | 10-27 02:32-03:12 | 40 min | (lead) | done |
| 32 | MLEvidence-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 02:33-02:48 | 15 min | 13,425,372 | done |
| 33 | MathReviewerC-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:33-02:51 | 17 min | 2,980,789 | done |
| 34 | PropStrategyMath-OpusHigh (worker-high, wf_df544c98-716) | opus-5-5 (high) | 10-27 02:33-02:45 | 11 min | 7,888,116 | done |
| 35 | AgDesks-OpusHigh (worker-high, wf_df544c98-716) | opus-5-5 (high) | 10-27 02:34-02:42 | 9 min | 7,915,557 | done |
| 36 | AlphaProcess-OpusHigh (worker-high, wf_df544c98-716) | opus-5-5 (high) | 10-27 02:34-02:51 | 18 min | 18,736,590 | done |
| 37 | MathReviewerA-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:34-02:53 | 19 min | 2,174,991 | done |
| 38 | MathReviewerB-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:43-03:03 | 20 min | 8,255,017 | done |
| 39 | MathReviewerD-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 02:46-03:11 | 24 min | 7,412,718 | done |
| 40 | LeakageReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:11 | 6 min | 2,932,000 | done |
| 41 | ArithmeticReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:11 | 6 min | 1,605,800 | done |
| 42 | FeasibilityReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:11 | 6 min | 3,484,948 | done |
| 43 | DofReviewer-FableXHigh (worker-xhigh, wf_3d631049-c34) | fable-5-1 (xhigh) | 10-27 03:05-03:07 | 2 min | 1,707,444 | done |
| 44 | FixApplier-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 03:11-03:11 | 0 min | 220,726 | done |
| 45 | USAGE LIMIT 2 | - | 10-27 03:12-07:31 | 259 min | - | not work |
| 46 | Lead: protocol v0.2, relaunches, Part V draft, v0.3 (45 items) | opus (xhigh) | 10-27 07:31-08:02 | 31 min | (lead) | done |
| 47 | LeakageReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:53 | 21 min | 8,536,712 | done |
| 48 | FixApplier-OpusHigh (worker-high, Agent) | opus-5-5 (high) | 10-27 07:32-07:38 | 6 min | 4,978,898 | done |
| 49 | DofReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:57 | 24 min | 9,806,052 | done |
| 50 | ArithmeticReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:52 | 19 min | 3,907,769 | done |
| 51 | FeasibilityReviewer-FableXHigh (worker-xhigh, wf_30d7118e-f81) | fable-5-1 (xhigh) | 10-27 07:32-07:55 | 22 min | 3,088,124 | done |
| 52 | PLANNED CONTEXT WIPE | - | 10-27 08:02-08:39 | 37 min | - | not work |
| 53 | Lead: resume checks, re-check plan, estimate table | opus (xhigh) | 10-27 08:39-08:42 | 3 min | (lead) | done |
| 54 | Full pytest (background shell, nice 10) | - | 10-27 08:42-09:01 | 19 min | - | 8,116 passed, 1 known failure |
| 55 | Lead: model checks, deleg32.py, drafts | opus (xhigh) | 10-27 08:42-08:57 | 15 min | (lead) | done |
| 56 | FixVerifierLeakArith-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:56 | 14 min | 5,415,437 | done |
| 57 | FixVerifierFeas-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:52 | 10 min | 1,275,543 | done |
| 58 | FixVerifierDofA-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:50 | 8 min | 2,784,627 | done |
| 59 | FixVerifierDofB-FableXHigh (worker-xhigh, wf_6418603c-1ef) | fable-5-1 (xhigh) | 10-27 08:42-08:54 | 12 min | 1,528,664 | done |
| 60 | USAGE LIMIT 3 | - | 10-27 08:57-12:35 | 218 min | - | not work |
| 61 | Lead: pytest failure investigation (clean worktree at HEAD) | opus (xhigh) | 10-27 12:35-12:38 | 3 min | (lead) | predates E.32 |
| 62 | Lead: re-check rulings, protocol v0.4 | opus (xhigh) | 10-27 12:38-12:42 | 4 min | (lead) | done |
| 63 | Lead: return drafts; spot-check rulings, v0.5 | opus (xhigh) | 10-27 12:42-12:58 | 16 min | (lead) | done |
| 64 | FixSpotCheckB-FableXHigh (worker-xhigh, wf_22487789-c6a) | fable-5-1 (xhigh) | 10-27 12:42-12:56 | 14 min | 4,445,077 | done |
| 65 | FixSpotCheckA-FableXHigh (worker-xhigh, wf_22487789-c6a) | fable-5-1 (xhigh) | 10-27 12:42-12:52 | 10 min | 3,770,126 | done |
| 66 | FinalDiffCheck-FableXHigh (worker-xhigh, Agent) | fable-5-1 (xhigh) | 10-27 12:58-13:06 | 8 min | 1,447,590 | done |
| 67 | Lead: final-check rulings, v0.6, FREEZE v1.0 | opus (xhigh) | 10-27 13:06-13:08 | 2 min | (lead) | done |
| 68 | Lead: brief assembly, end checks, return, progress, STAGES, cost, commit | opus (xhigh) | 10-27 13:08-13:11 | 3 min | (lead) | done |
| - | Lead session a51871c6, whole | opus 5.5 (xhigh) | 10-26 22:21-10-27 00:51 | - | 48,849,791 | - |
| - | Lead session 900dd54a, whole | opus 5.5 (xhigh) | 02:32-08:02 | - | 43,326,750 | - |
| - | Lead session 89bc0cd0, whole | opus 5.5 (xhigh) | 08:39-13:11 | - | 30,552,147 | - |
| total | Stage E.32 | - | 10-26 22:21-10-27 13:11 | work 3 h 37 min (pauses 11 h 13 min) | 545,304,733 | initial estimate (10-26 23:01): done by about 11:20 PDT 10-27; this session's estimate (08:41): 10:40 |
