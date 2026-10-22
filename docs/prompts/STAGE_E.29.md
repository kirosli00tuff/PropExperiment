STAGE E.29 "COMBINING THE RANKED CONTRACTS IN ONE PROP ACCOUNT: A SIMULATION STUDY"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: A simulation-only stage (V46). E.28 ranked firm-contract pairs one
contract at a time; QM leads at all five firms but leaves little room under
the dollar loss limits (room about 1.6 median daily ranges at Topstep). This
stage asks whether trading two or three of the ranked contracts at once in
one 50K account lowers the break-even edge per trade and raises the chance
of payouts, and at what correlation that benefit disappears. It uses E.28's
economic model (prop_econ/ on E.19's simulator) with assumed edges on a
grid, never a measured edge. No outcome read, no purchase, nothing
registered, N stays 538.

Decisions in force: docs/DECISIONS.md V20 to V46. Binding: this prompt,
reports/stage_e28_ranking_spec.md (its economic model, reused unchanged
except where this prompt extends it), V37.

Lead: Opus 5.5. On Max at launch: effort xhigh, Ultracode on, Fable xhigh
reviews. On Pro: effort high, Ultracode off, the review by an Opus 5.5
xhigh agent in a fresh context that sees only the files it checks (V46
item 5). At most 4 workers at once.

Usage and time: launched after E.28b's purchase is verified (or after
E.28b ends without one). Checkpoint reports/stage_e29_STATE.md after every
step and resume from it after any usage limit. If launched on 2026-10-21,
work stops at 23:00 PDT and the return is written by 23:30.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
THE STUDY (FIXED HERE)
============================================================

Z1 Inputs (lead, from files only):
- The ranked table, reports/stage_e28_briefs/A3_ranking_table.md (v2).
- Per-contract facts: A3_facts.json (sigma_1m in ticks, R_d, tick value)
  and A3_firm_products.json (fees, listing, position limits, product
  restrictions, Topstep's Tier 1 news window).
- The firms' rules records used by E.28's EconCoder.

Z2 Baskets (fixed here, not chosen from results):
- B0 QM alone (the reference).
- B1 QM + ZM.
- B2 QM + MGC.
- B3 QM + ZM + MGC.
- B4 QM + MNQ (the program's baseline contract).
A basket is run at a firm only if every member is listed at that firm's
50K plan (E.28's listing gate). Firms: Topstep, MFFU, Tradeify, Bulenox,
Lucid.

Z3 Model (an extension of E.28's model, written down before any run):
- Each member trades T_i round trips a day, 1 contract each. The total T
  is 20, split equally across members (rounded, logged).
- Gross P&L per trade in ticks for member i is normal with mean mu_i and
  standard deviation sigma_1m,i.
- Members' daily P&L have pairwise correlation rho. rho runs on the grid
  0, 0.25, 0.5, 0.75 and is the same for every pair in a basket.
- Costs are E.28's limit case per member (F_rt over tick value). E.28's
  market case is reported for B0 and the best basket only.
- Every firm rule E.28 mapped (daily loss limit, trailing drawdown,
  consistency, payout rules, scaling and position limits, the Topstep news
  window) is applied to the account's combined P&L. A position limit that
  binds is applied, not ignored, and logged.
- The edge is set in one of two ways:
  (i) every member at the same mu, measured in units of that member's
      break-even mu*_lim from E.28, so a member at 1.0 just breaks even
      alone;
  (ii) QM at a grid mu and the others at zero edge, which shows whether
       adding zero-edge contracts only adds cost and risk.
- The paths, seed, grid and reporting quantities (mu*, mu10K, cost per
  attempt, pass rate, expected net cash per cycle) follow E.28's spec.
Measured correlations (reference only, not an input): from owned
one-minute bars dated before 2024-03-01 only, compute the daily-return and
daily-range correlations of the CL, ZM (or its owned sibling), GC and NQ
front contracts, and state where they sit on the rho grid. No holdout,
embargo, research-window or MES-sealed file is read. The holdout status
is checked before and after this read.

Z4 Outputs:
- A table per firm: basket by rho by edge setting, against B0.
- A plain answer to three questions:
  (a) does any basket beat QM alone at realistic rho;
  (b) at what rho does the benefit vanish;
  (c) does adding a zero-edge contract ever help (it should not; if it
      does, find out why).
- The ranking these results would imply, marked as conditional on an edge
  no one has measured yet.

Z5 Review: a reviewer (see Lead) recomputes B0 against E.28's numbers
(it must match), re-runs two random cells with a different seed, and
checks the rule mapping on the combined account. BLOCKING and SHOULD FIX
items are fixed before the return.

============================================================
SCOPE
============================================================

This stage does NOT:
- read any outcome, holdout, embargo, research-window or E.28 pilot data,
  or any bar dated 2024-03-01 or later
- buy anything, call Databento, or touch acct-3
- register or freeze anything; N stays 538
- change prop_econ/ behaviour for existing callers. New code goes in a new
  module, with tests showing B0 reproduces E.28's QM results exactly.
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
GUARDRAILS AND DELIVERABLE
============================================================

Start and end checks, quoted verbatim in the return:
- `git status --short` and `git log --oneline -3`;
- the holdout status;
- `wc -c REGISTRATION.md`;
- harness v14 2e908c81...;
- the spend ledger line count and sha256, and N;
- `uv run pytest -q -p no:cacheprovider` at the end. Stop it if free
  memory falls below 2 GB, and quote the last full run on identical code.
Commits touch only this stage's files. Before ending, confirm no worker
or shell is still running.

Write reports/E.29_RETURN.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.29 basket simulation". Fixed
sections:
1. Summary, at most 200 words.
2. Guardrail evidence.
3. Results (Z3 model text, Z4 tables and answers).
4. Delegation record.
5. Verification.
6. Open choices.
7. Decisions for the user, each with a recommendation.
8. Session cost, per CLAUDE.md, never estimated.
The last thing before ending: list every open choice in section 6.

END PROMPT
