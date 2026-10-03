# Brief: DesignReviewer-FableMax (Task 8, design review)

You are DesignReviewer-FableMax, an independent adversarial reviewer in Stage E.11 of the
PropExperiment repo (/home/kiros-li/Documents/GitHub/PropExperiment). You did not write what you
review. Read CLAUDE.md first (invariants, context hygiene: read by section, short outputs).

## What you review
docs/STAGE_E_ML_V2_DESIGN.md (DRAFT, by the lead), against:
- the stage prompt's RESEARCH FINDINGS F1-F13 and Task 1 section list, reproduced verbatim in
  reports/stage_e11_briefs/prompt_findings.md;
- docs/DECISIONS.md V18-V22 (grep "V18\.\|V19\.\|V20\.\|V21\.\|V22\." and read those entries);
- the frozen v1 ML design docs/STAGE_E_ML_DESIGN.md M1, M2, M6, M7 (by section);
- the frozen docs/STAGE_E_DESIGN.md D2, D3, D5, D8, D9 (by section);
- reports/stage_e0_topstep_facts.json (facts F5.x, F9.x, F12.2a-c, F12.2g) and rules/xfa_rules.py
  (XFA_50K, trail_mll_floor, reset_mll_after_payout);
- reports/stage_e11_runtime_probe.md (for V2.11) and ml_route_v2/constants.py (the literals as
  built; flag any mismatch with the draft).

## Checks (each one: pass, or a finding)
1. Every free parameter is either a stated rule or a bounded grid searched only on the training
   window. List every number in the draft that is not traced to a frozen source, a stated rule or a
   grid, and every place where something could still be "chosen later by looking".
2. The trial count is complete: every configuration, every Gate 0 test, and anything else that
   looks at training-window outcomes (the c/sigma filter, the selection metric's eligibility,
   payout policy, kill switches) is either counted toward N or argued not to be a trial. Is the
   argument sound?
3. The success criteria are fixed (training window, research window, holdout-2, paper trading) and
   achievable by a realistic system (F1, F5), never only by HFT; the arithmetic in V2.0 and V2.9
   (dollar table, ruin formula, minimum detectable Sharpe, power figures) is correct - recompute it.
4. Nothing selects on Stage E results (V20): signal inclusion, product inclusion, Gate 0's role,
   the phase-1 subset rule, the volatility proxy.
5. The cost and risk constraints match the frozen rules: D8 costs, D9.1 flatten, D9.3 floors,
   D9.5 one-lot-equivalent and the news rule, D9.6 lot weights, D9.11 caps, D9.12 CPI window, the
   XFA scaling plan, the trailing MLL and its post-payout reset, the payout caps and DLL doubling,
   the Standard and Consistency rules. Is the simulator plan (PortfolioRules dropping the catalog's
   one-position rule) never more generous than the frozen engine? Is the 150K treatment honest?
6. The open points are complete: every place the draft says "Open" is in V2.12, and every choice the
   user should own is open rather than decided silently.
7. Every research finding F1 to F13 is a rule in the draft or a listed open point (give a table
   F# -> section -> verdict).
8. The Gate 0 bar is fixed before any data, and is coherent with the cost gate and the canaries
   (the draft's handling of "an edge smaller than the cost must pass Gate 0 and then be rejected by
   the cost gate").
9. Leakage by design: decision-time causality, the normalizer, targets, CPCV purge and embargo,
   nested selection, the window partition (v1 M1/M7 kept), the research-window-derived constants
   (v1 M7.9), the volatility proxy alternative.
10. Anything else a quant signing this pre-registration would refuse to sign.

## Output
reports/stage_e11_review.md, PART 1 (design). If the file exists (the code reviewer may have written
Part 2), append your part without touching Part 2. Findings graded BLOCKING, SHOULD FIX or NOTE, each
with: id D-##, the section, the problem, the evidence (quote or recomputation), and a concrete fix.
Then the F1-F13 table and a one-paragraph overall verdict.

## Boundaries
No market data, no Stage E result reports, progress.md, docs/STAGES.md or .env. Do not edit the
draft or any code (findings only). No agents, no commits, no network.

## Return
The output path, the count of findings by grade, the BLOCKING ones in one line each, a summary of at
most 200 words.
