Computed at 09:44:52 PDT 2026-10-29 (the cutoff) from the transcripts of the four lead sessions and their subagents
(main .jsonl and subagents/**/*.jsonl of 3d79635b, 7e35d21b, 3860d0d1 and 0d036ce2) with
reports/stage_e32b_briefs/work/cost/make_cost.py (adapted from E.25/E.26; it keeps each message's final usage, as
reports/stage_e10_briefs/cost.py does; output work/cost/ret_cost_tokens.md and cost_raw.txt). No session is a resume
of another and none holds usage from before the stage. These are token counts, not plan-credit percentages; the
commit and the checks after 09:44:52 are not counted.

Wall clock: 22:06:09 (2026-10-28) to 09:44:52, 11 h 39 min. Not counted as work: the usage-limit pause (01:55:44-03:11:01,
1 h 15 min; the local econ run kept going) and three planned context wipes with nothing running (22:35:17-22:40:26,
5 min; 00:56:14-00:56:45; 07:28:50-08:39:23, 1 h 11 min). Counted: the lead's wait while econ pass 1 ran (04:09-05:24,
stage compute). Work time: 9 h 07 min. Per session (first to last record): 1 0 h 29 min; 2 2 h 16 min; 3 6 h 32 min
(5 h 17 min without the pause); 4 1 h 05 min to the cutoff.

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,382 | 385,969 | 21,663,145 | 1,851,038 | 23,903,534 |
| claude-haiku-5-5 | 58 | 79,231 | 3,743,478 | 319,077 | 4,141,844 |
| claude-opus-5-5 | 5,844 | 3,645,088 | 627,519,667 | 11,011,541 | 642,182,140 |
| claude-sonnet-5-5 | 526 | 238,462 | 37,525,195 | 1,241,992 | 39,006,175 |
| all | 9,810 | 4,348,750 | 690,451,485 | 14,423,648 | 709,233,693 |

(Three records marked <synthetic>, with zero usage, are the usage-limit cuts.)

Worker spawns (agent file, model from the transcript, effort, tokens):
- Session 1: FableProbe-FableMed: worker-medium, claude-fable-5-1, medium, 65,309
- Session 2: CrudeReader-OpusHigh: worker-high, claude-opus-5-5, high, 32,162,972; NatgasReader-OpusHigh: same, 28,090,644;
  MetalsReader-OpusHigh: same, 22,423,835; GrainsReader-OpusHigh: same, 31,237,627; RatesReader-OpusHigh: same,
  23,549,545; EquityReader-OpusHigh: same, 22,171,338; FXReader-OpusHigh: same, 21,236,586; CryptoReader-OpusHigh:
  same, 21,612,823; FirmRules-OpusHigh: same, 27,291,824; IdeaFamilies-OpusHigh: same, 10,643,052; VolCoder-OpusXHigh:
  worker-xhigh, claude-opus-5-5, xhigh, 5,038,247; ScoreCoder-OpusXHigh: same, 14,892,068; EconSetup-OpusXHigh: same,
  28,798,889; HoldingCoder-OpusXHigh: same, 7,374,669; DataAccess-SonnetHigh: worker-high, claude-sonnet-5-5, high,
  14,815,324; ClosedLines-SonnetHigh: same, 8,793,559; NonProp-SonnetHigh: same, 10,188,926; AttentionCounter-HaikuMed:
  worker-medium, claude-haiku-5-5, medium, 672,961
- Session 3: FactTable-OpusHigh: worker-high, claude-opus-5-5, high, 39,400,501; RankingWriter-OpusHigh: same,
  13,086,414; ScopeWriter-OpusHigh: same, 6,819,605; BlindScorer-OpusXHigh: worker-xhigh, claude-opus-5-5, xhigh,
  15,031,894; BlindScorer2-OpusXHigh: same, 12,026,958; F5Runner-OpusXHigh: same, 7,640,619; DossierWriter-OpusXHigh:
  same, 29,440,132; CombinationScorer-OpusXHigh: same, 4,504,982; RecsDrafter-OpusXHigh: same, 38,031,774;
  VariantBuilder-SonnetHigh: worker-high, claude-sonnet-5-5, high, 4,185,724; FactAuditor-FableXHigh: worker-xhigh,
  claude-fable-5-1, xhigh, 5,783,847; RankingReviewer-FableXHigh: same, 8,010,050; RecsReviewer-FableXHigh: same,
  5,465,653
- Session 4: ScoreFixer-OpusHigh: worker-high, claude-opus-5-5, high, 8,892,840; R1Fixer-OpusHigh: same, 8,951,432;
  RecsAssembler-OpusXHigh: worker-xhigh, claude-opus-5-5, xhigh, 27,063,610; CostTabler-SonnetHigh: worker-high,
  claude-sonnet-5-5, high, 1,022,642; DelegationTabler-HaikuMed: worker-medium, claude-haiku-5-5, medium, 3,468,883;
  FixVerifier-FableXHigh: worker-xhigh, claude-fable-5-1, xhigh, 4,578,675

Lead sessions (claude-opus-5-5, max effort): 3d79635b 13,097,805; 7e35d21b 19,115,950; 3860d0d1 74,510,690; 0d036ce2
28,042,815 (to the cutoff).

Delegation share: lead 134,767,260 (19.0%), workers 574,466,433 (81.0%). By model: Opus 642,182,140 (90.5%; lead
134,767,260, workers 507,414,880), Sonnet 39,006,175 (5.5%), Fable 23,903,534 (3.4%), Haiku 4,141,844 (0.6%). Cache
reads are 97.4% of all tokens. By session: 1 13,163,114; 2 350,110,839 (the eight research readers alone 202,485,370);
3 263,938,843; 4 82,020,897.
