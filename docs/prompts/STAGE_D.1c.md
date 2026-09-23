STAGE D.1c "CONSTRAINT AUDIT: XFA FLATTEN AND THE EXCLUDED HYPOTHESIS SPACE"

Model: Opus 5, high effort.

Reasoning: this session is mostly synthesis and careful framing of research
that already exists (D.1's and D.1b's logged findings), not a genuinely
parallelizable investigation. It does not meet the standing bar for
ultracode. Task 1 (reconfirming the flatten rule against Topstep's current
help center) is a reasonable Sonnet-delegation candidate — it's a
mechanical fact-check against a public source, not a judgment call. Task
2 (cataloging which hypotheses D.1/D.1b's own logs show were structurally
excluded) is largely mechanical extraction from existing logs and is also
delegable. Task 3 (the decision brief itself) stays entirely with the
lead — how this gets framed is itself a judgment with real weight, and a
subtly slanted brief here would functionally make the program's next
strategic decision by the back door, which is explicitly not this
session's role.

============================================================
SCOPE — READ THIS FIRST, IT IS UNUSUALLY IMPORTANT THIS SESSION
============================================================

This session's job is to produce a neutral, evidence-based decision
brief on one question: does the XFA's mandatory intraday flatten rule out
strategy families that the research so far suggests might otherwise be
viable, and if the program wanted to pursue those, what would actually be
required? This session does NOT decide whether to pursue them. It does
NOT recommend a course of action beyond laying out the options and their
honest tradeoffs. It does NOT touch REGISTRATION.md, does NOT build any
code toward a second prop firm, an LFA workflow, or an IBKR adapter —
those remain explicitly shelved per the existing scope lock in
docs/DECISIONS.md, and researching what they would require is different
from starting to build them. If you find yourself writing a
recommendation ("the program should move to X"), stop and rewrite that
section as a neutral tradeoff statement instead — the user decides, not
this session.

Working directory: /home/kiros-li/Documents/GitHub/PropExperiment. Read
README.md, docs/DECISIONS.md, docs/STAGES.md, and the full progress.md
entries for Stage D.1, D.1a, and D.1b before starting. In particular:

- rules/xfa_rules.py's flatten logic and the constants it uses
  (in_flatten_window at 15:10 CT, in_no_new_positions_window at 15:08 CT,
  and the early-close adjustment) are the CURRENT encoded understanding
  of the rule. This session checks that understanding, it does not assume
  it's already correct.
- Stage D.1b's closing section ("Should the program keep searching?")
  is the direct trigger for this session — read it in full before
  starting anything, since Task 3 below is answering the question it
  raised, not a new question invented independently.
- Stage A.1's progress.md entry already flagged several Topstep rule
  figures (the consistency percentage contradiction, the exact Scaling
  Plan boundary, several others) as needing checkout reconfirmation,
  still unresolved as of this session. The flatten timing itself was
  sourced with more confidence at the time (15:08/15:10 CT, "Risk
  Managers begin flattening at that time," with early-close days shifted
  15 minutes earlier), but it has not been re-checked since 2026-09-16,
  and Topstep's help center has changed multiple times since then on
  other figures. Do not assume it is still accurate without checking.

CREDENTIAL AND HOLDOUT GUARDRAILS — unchanged. No TopstepX API reference
of any kind (this session reads Topstep's public help center, which is
different from touching the API — web research about the rule is fine,
touching live/ or ops/ or any credential is not). Do not unlock the
sealed holdout. Check `python -m data.holdout status` at the start and
end and confirm unlocks_logged: 0 in the final report, as every session
since Stage C has.

SPEND GUARDRAIL: this session needs no Databento spend at all — it is
rules research and literature synthesis, not backtesting. If you find
yourself about to make a data request, stop; that would mean this
session has drifted into Stage D.1-style hypothesis testing, which is
out of scope here.

============================================================
TASK 1 — RECONFIRM THE FLATTEN RULE ITSELF
============================================================

Check Topstep's current help center (as of this session's date) for the
exact current wording on the mandatory daily flatten: the timing, whether
it differs between the Combine, XFA, and LFA stages, whether it differs
by product (some CBOT products have earlier closes, as Stage A.1's
research already noted), and whether anything has changed since the
2026-09-16 reading currently encoded in rules/xfa_rules.py.

Report explicitly:
- Whether the current code's understanding (15:08 CT no-new-positions,
  15:10 CT forced flatten, 15 minutes earlier on early-close days) still
  matches the help center exactly, or has drifted.
- Whether the flatten rule is described anywhere as applying differently
  at different stages (Combine vs. XFA vs. LFA) — this matters because if
  the LFA's flatten rule is genuinely different or absent, that changes
  what "moving to LFA to access multi-day strategies" would actually mean,
  which is directly relevant to Task 3.
- Whether Topstep documentation anywhere describes any account type,
  product, or exception that permits an overnight or multi-day position —
  do not assume the answer is no; check.
- If anything here contradicts what's currently encoded, do NOT change
  rules/xfa_rules.py in this session — flag the discrepancy clearly in
  the report as something Stage A.2 (the eventual live TopstepX
  onboarding session) needs to resolve with a real account, and note
  whether the discrepancy is large enough to matter for Task 3's framing.

============================================================
TASK 2 — CATALOG THE EXCLUDED HYPOTHESIS SPACE FROM EXISTING LOGS
============================================================

This is extraction and organization, not new research. Go through Stage
D.1's and D.1b's full hypothesis and stylized-fact logs (the 23+1 trials,
plus Family F's 57 declared statistics) and produce a clear catalog,
answering:

- Which specific hypotheses, findings, or literature sources across all
  three sessions were EXPLICITLY noted as being about multi-day, overnight,
  or swing-horizon effects, and were therefore either not testable at all
  under the intraday-flatten constraint, or were tested in some
  intraday-truncated form that the original source's claim doesn't
  actually support? Be specific and cite the exact trial or statistic ID
  (e.g., "A-H4," "F3.3(b)") for each.
- Of the literature sources gathered in Stage D.1's Task 1 (the full
  183-item log, not just the 41 carried forward), how many were rejected
  at the pre-filter stage specifically BECAUSE they were multi-day/swing
  in nature and therefore judged out of scope at the time, rather than
  rejected for lack of relevance to equity-index futures? This requires
  re-reading Stage D.1's Task 1 rejection log, not just its formalized
  hypothesis list — the interesting number here is how much was excluded
  before it ever got a chance to be tested, not just what failed after
  being tested.
- For the handful of findings that come closest to being tradeable (the
  short-lag mean reversion in Family F, C-H4's passive-fill result,
  anything else close to the bar across all three sessions), would
  removing the intraday-flatten constraint plausibly change the verdict,
  or is the constraint irrelevant to why they failed? State this
  explicitly per case — some of D.1b's failures (C-H4's adverse-selection
  problem, for instance) have nothing to do with the flatten rule, and
  conflating "would work with more time" and "would work with better
  fills" would misrepresent the actual bottleneck.

============================================================
TASK 3 — THE DECISION BRIEF (LEAD ONLY, NO DELEGATION)
============================================================

Using Tasks 1 and 2, and the venue research already done earlier in this
project (the TopstepX/LFA wall research, the second-prop-firm comparison,
the IBKR capital-sizing analysis — all already in this project's prior
sessions, re-read rather than re-derived), produce a neutral brief
covering:

1. **What the constraint actually excludes, quantified from Task 2**,
   not asserted from general impression. If Task 2 finds that only a
   small fraction of the rejected/excluded research was genuinely
   multi-day in nature, say so plainly — that would be evidence the
   constraint matters less than D.1b's closing section implied, and this
   session's job is to report that honestly even if it deflates the
   premise that motivated the session.
2. **What relaxing it would actually require**, stated as options with
   their real costs and tradeoffs, not a ranked recommendation:
   - Staying on Topstep but reaching the LFA (which the earlier venue
     research already showed prohibits API automation entirely — so this
     option, if it's still accurate per Task 1, would mean trading
     multi-day strategies manually, which is a fundamentally different
     kind of program than what's been built).
   - A second prop firm with different flatten rules, if one exists
     among the ones already researched (Lucid, MyFundedFutures, Tradeify
     — check what's already known about each one's overnight/swing
     rules, don't re-research from scratch if it's already documented).
   - Trading on personal capital via IBKR, which removes the constraint
     entirely but reopens the capital-sizing problem already analyzed
     (the ~$5,000-$6,000 minimum against the stated $6,000 max/under
     $2,500 preferred pool).
   - Staying intraday-only and treating this as a real, informative
     negative result about what's achievable within the current
     constraint set, which is itself a legitimate conclusion, not a
     failure to find one.
3. **An explicit statement that this session is not choosing between
   these**, and a short list of the specific questions the user would
   need to answer to choose (e.g., "is manual LFA trading something you'd
   actually want to do, given the program has been built entirely around
   automation," "is the capital-sizing problem from the IBKR analysis
   still binding given current savings," etc.) — questions, not nudges
   toward a particular answer.

============================================================
WHAT NOT TO DO
============================================================

Do not write to REGISTRATION.md. Do not unlock the sealed holdout. Do not
write any code under live/, ops/, or toward a second-firm or IBKR
execution adapter — researching what they would require is in scope,
building any part of them is not. Do not run any new backtest or
hypothesis test — this session works from Task 1's rule check and Task
2's log extraction only, nothing from sim/engine.py or the screening
runner. Do not let Task 3 drift into a recommendation; if a sentence
reads like advice rather than a laid-out tradeoff, rewrite it.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry: Task 1's reconfirmation result and any
discrepancy from the currently encoded rule; Task 2's full catalog with
specific trial/statistic citations and the fraction-excluded figure from
the Stage D.1 rejection log; Task 3's neutral brief in full, ending with
the explicit list of questions for the user rather than a conclusion;
and a one-line note on what this session did NOT do (no code changes, no
new backtests, no registration).

END PROMPT
