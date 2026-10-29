## 2026-10-29 — Stage E.32b: directional rerank of the firm-contract pairs: YM, MNQ and RTY lead, 15-60 minute holds (not hours), one ZL build candidate (prior about 4%); N = 838

Prompt docs/prompts/STAGE_E.32b.md (V50 item 2, V51; binding V49, V50, V37; routing V55). Return:
reports/E.32b_RETURN.md. STATE reports/stage_e32b_STATE.md (four lead sessions); rulings and open choices
reports/stage_e32b_briefs/RULINGS.md. Spec reports/stage_e32b_ranking_spec.md (09ebe697, hashed 22:32:14 before any
new lookup or score). Outputs: reports/stage_e32b_ranking.md, reports/stage_e32b_holding_scope.md,
reports/stage_e32b_recommendations.md (the main output). [GUARDRAILS]

**What ran.** Four lead sessions (Opus 5.5, max effort), split by three planned context wipes (22:35, 00:56, 07:28)
and one usage-limit pause (01:56-03:10), and 39 worker spawns with models confirmed from their transcripts: eight
family readers, FirmRules, IdeaFamilies, FactTable, F5Runner, DossierWriter, RankingWriter, ScopeWriter, RecsDrafter,
ScoreFixer, R1Fixer and RecsAssembler (opus); VolCoder, ScoreCoder, EconSetup, HoldingCoder, two BlindScorers and the
CombinationScorer (opus xhigh); DataAccess, ClosedLines, NonProp, VariantBuilder and CostTabler (sonnet);
AttentionCounter and DelegationTabler (haiku); FableProbe, FactAuditor, RankingReviewer, RecsReviewer and FixVerifier
(fable, claude-fable-5-1). Detached econ runs on 8 workers: pass 1 (224 jobs, 01:17-05:24), S_mean (03:53-04:05),
pass 2 (E_dir 30/120/240 for the top 15, 05:26-07:28).

**Result.** Layer 1: 35 of 47 codes survive (8 fail on unknown sigma, QG, QM and XW on D4 = 0; NQ excluded, V49);
103 pairs ranked. Top 10: Bulenox YM 3.113, Topstep MNQ 3.096, Tradeify MNQ 3.087, Tradeify YM 3.081, Topstep YM
3.055, MFFU YM 3.026, Bulenox RTY 3.017, MFFU MNQ 3.014, Topstep RTY 3.009, Tradeify RTY 2.994; YM is in the top 5 of
all 28 variants; E.28's QM leaders fail Layer 1; ZM falls to 24, ZL is 15. Holding scope: every top-15 pair's band is
15-30 minutes (15-60 for Topstep ZL, 30-60 for MFFU MYM), minimum at 30 minutes, and the E_dir economics agree; no band
reaches 120 minutes and no prop firm allows overnight holds, so the user's minutes-to-hours prior holds only for
minutes. Recommendations: 23 closed lines (838 trials) filtered, 185 combinations scored by the hashed R3 rule; R4 =
one ZL program at Topstep (F10 order-book state + F09 soy-complex lead-lag, one registration on the single sealed read
2017-05..2020-11, prior about 4%), then MNQ F08, YM F08 and the EQ3 F08 pool (each under 1%; YM about 1.5% only if
V31 were narrowed); own broker C141 ZL F10 at IBKR 2.60, not favoured now. Stop rule: at most one more registered
build.

**Verification.** FactAuditor (Fable): two blinding leaks (B1, B2) found and patched before the final blind ratings;
every value PASS. RankingReviewer (Fable): PASS, 0 BLOCKING, 3 SHOULD FIX, 13 NOTE, every score recomputed exactly.
RecsReviewer (Fable): PASS WITH ONE RULING NEEDED, 1 BLOCKING (RTY and ZL F09 Q3: ruled LR-Q3b, which drops RTY F09
from the R4 and adds the EQ3 F08 pool), 6 SHOULD FIX, 7 NOTE. All fixed in session 4. [FIXVERIFIER]

**Decisions for the user.** D1 keep V31's scope for YM (recommended); D2 assign the ZL sealed window's single read to
the ZL program if a prior of about 4% is acceptable, else stop the directional program; D3 admit V51-style discovery
without a published expected gross, judged by the power rule (recommended), or keep the gate and stop; D4 keep
2024-03+ data closed unless the ZL program passes (recommended); D5 if D2 and D3 are accepted, one pre-registration
stage for the ZL program with a Databento quote logged first.

**Session cost.**

[COST]
