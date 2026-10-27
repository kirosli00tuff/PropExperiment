STAGE E.32b "RERANK THE FIRM-CONTRACT PAIRS FOR DIRECTIONAL STRATEGIES"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.28 ranked firm-contract pairs for PASSIVE limit-order trading.
E.31 then closed that line (V50): passive fills at prop-firm simulators
lose about a tick per fill. E.28's limit-case economics (mu*_lim) and
several of its contract criteria therefore score the wrong thing:
- C1 adverse selection for resting orders;
- C2 queue mechanics;
- the F fill-rule score.
Its mu*_mkt is simply mu*_lim plus a 1-tick default spread, so the
market-order order is the same list.

The program now looks for DIRECTIONAL signals (V50 item 2, V51), executed
with market orders or with limit orders priced under the trade-through
rule. This stage builds a new two-layer ranking for that purpose. It
reuses E.28's verified facts wherever they still apply, adds the facts a
directional ranking needs, and scores blind as E.28 did. It runs beside
Stage E.32 and does not change it. If the rerank puts another contract
above ZM, E.32/E.33 still finish on ZM (the user's thesis, V51), and the
rerank sets the order of the products that follow.

No outcome is read, no strategy is tested, N stays 538, and no Databento
call is made.

Decisions in force: docs/DECISIONS.md V20 to V51. Binding: this prompt,
V49 (NQ is dropped and is not scored; list it as excluded), V50, V37.
E.28's spec reports/stage_e28_ranking_spec.md is the model for method,
blinding and arithmetic, except where this prompt changes it.

Read first:
- reports/stage_e28_ranking_spec.md
- reports/stage_e28_ranking.md
- reports/stage_e28_briefs/A0_contract_stats.*, A1_*.md/.json,
  A2_firm_*.md/.json, A2_platforms.*, A3_facts.json,
  A3_firm_products.json, A3_econ.json, A3_lead_rulings_v2.json
- reports/E.29_RETURN.md section 1
- reports/E.31_RETURN.md sections 1 and 7
- reports/stage_e31_inputs/planner_research_notes.md
- reports/stage_e32_inputs/planner_research_soy_complex.md

Lead: Opus 5.5, effort xhigh, Ultracode on (launched interactively on
Max).
- Readers are Opus high.
- The blind scorer is Opus xhigh.
- Reviews are Fable xhigh, each model confirmed from its transcript (V50
  item 5). If Fable is unavailable or the transcript shows another model,
  use Opus 5.5 xhigh in a fresh context and say so. Never Sonnet.
- At most 4 workers at once, because E.32 runs beside this stage.

Time: launched about 23:00 PDT on 2026-10-26. The return is due by 23:00
PDT on 2026-10-27. Checkpoint reports/stage_e32b_STATE.md after every
step, and resume from it after any usage limit or reboot.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
STEP 1: THE NEW SPEC, HASHED BEFORE ANY NEW LOOKUP OR SCORE
============================================================

Write reports/stage_e32b_ranking_spec.md and hash it. It fixes the
criteria, weights, scales, gates, unknown rules and blinding. The lead
may adjust the weights below only before hashing, with the reason
logged.

Layer 1, contract (directional suitability):
- D1 Cost in volatility units (0.30). The market-order round-trip cost
  in ticks (the firm-independent part: 1 spread tick, from a sourced
  median where one exists, plus a slippage allowance stated in the spec)
  divided by sigma_h, the typical absolute move over horizon h in ticks.
  Use h = 15, 60 and 240 minutes and the day session. Score each h by
  fixed bands, then average. Lower cost per sigma scores higher. This
  criterion replaces E.28's volatility-per-tick criterion as the main
  driver.
- D2 Crowding and attention (0.15). How many fast and institutional
  players work the contract's directional flow, and how much published
  research covers its intraday predictability. Less attention scores
  higher (the user's thesis, V51). Use observable proxies: HFT share where
  published, market-maker programs, volume share of the largest contract
  in the family, and a count of academic papers on its intraday behaviour.
- D3 Structural signal sources (0.15):
  - cointegrated siblings or spread relationships, such as the crush,
    calendars and mini/full pairs;
  - scheduled information events whose prices are absorbed slowly enough
    to trade;
  - a session structure with known handoffs.
  Each must be sourced.
- D4 Tradability at one contract (0.15):
  - liquidity enough for market orders without walking the book;
  - jump and limit-move risk against a 50K plan's daily loss limit;
  - satellite status (a contract whose price is derived from another, as
    QM is from CL, scores low: its direction is set elsewhere).
- D5 Data access (0.10): order-by-order history on Databento from 2017
  and its approximate cost per month; the program's owned data; and what
  is sealed or spent for it.
- D6 Published directional evidence (0.15): intraday directional
  predictability at minutes-to-hours horizons, rated by evidence quality.
  Correctly signed contemporaneous order flow does not count.
Gates: a contract fails Layer 1 if
- D4 = 0, or
- its sigma at 60 minutes is below 2 x its round-trip cost in ticks
  (with the arithmetic shown).

Layer 2, firm x contract, for directional one-lot strategies:
- E Economics under market orders, from E.28's model, rerun with the
  corrected spread where a sourced spread replaces the 1-tick default.
  Also report each mu* in sigma_60 units. Lower is better. Weight 0.40.
- R Product restrictions and news windows (0.15). Use the product lists
  from the planner research notes: Topstep's Tier 1 list blocks named
  minis only, and MFFU's EIA rule covers energy. Verify both against the
  firm pages.
- A Automation rules (0.15).
- D Room under the dollar limits, relative to sigma_240 and to the daily
  range (0.15).
- Rel Reliability and eligibility (0.10).
- P Platform and API (0.05).
E.28's F (sim fill rule) is dropped. The trade-through rule is assumed
everywhere (V50).

The pair score is S = 0.5 L1 + 0.5 L2, with the same gates and unknown
rules as E.28 unless the spec says otherwise.

============================================================
STEP 2: FACTS
============================================================

F1 Reuse E.28's sourced facts, with their citations, where the meaning
is unchanged: fees, listing, position limits, automation, reliability,
platforms, ADV, sessions and limits.

F2 New facts by readers (Opus high), one contract family each:
- crude
- natgas
- metals
- fx
- crypto
- equity
- rates
- grains (with ZM, ZS, ZL and the micros)
Each reader covers:
- the spread median;
- crowding proxies;
- structural relationships;
- scheduled events and absorption speed;
- satellite status;
- the intraday directional evidence;
- Databento MBO availability and price per month.
Follow E.28's reader rules: terms read first, never CME's site by
automation, and pointers labelled.

F3 Volatility at horizons (script):
- compute sigma_15, sigma_60 and sigma_240 in ticks, and the median
  daily range, from the program's owned one-minute bars;
- use only E.28's standard window (2022-11-01 to 2023-10-31), day
  session, with the same OC-1 sibling transfer for contracts with no
  owned data;
- never read the sealed or spent windows: holdout-2, the March 2024
  embargo, the research window, ZM/ZS/ZL 2017-05 to 2020-11, or anything
  from 2024-03-01 on;
- show the holdout status and the E.32 test-seal guard check before and
  after;
- these are volatility statistics only, never strategy outcomes.

F4 FactTable (Opus high): build the masked fact table (contracts and
firms coded, as in E.28) and the mask key.

============================================================
STEP 3: BLIND SCORING, ECONOMICS, TABLE
============================================================

- BlindScorer (Opus xhigh, fresh context) rates the qualitative criteria
  from the masked table only.
- EconCoder reruns E.28's economic model for market orders with the new
  spreads, and reports mu* in ticks and in sigma_60 units.
- ScoreApplier (a script) computes L1, L2, S, the gates and the ranks.
- Report the full table for every listed pair, the top 15, and a
  comparison with E.28's order (moves up and down, and why).
- Run sensitivity variants for every lead ruling that changes the top 5.

============================================================
STEP 4: REVIEW
============================================================

RankingReviewer (fable xhigh, model confirmed):
- recomputes every score from the facts;
- checks the blinding;
- checks the unknown rules;
- checks the volatility arithmetic and the F3 window discipline.
Fix every BLOCKING and SHOULD FIX item before the return.

============================================================
SCOPE
============================================================

This stage does NOT:
- test any strategy, compute any return-based outcome, or read any data
  beyond F3's volatility statistics in the standard window
- call Databento; prices per month come from published pricing or E.31's
  ledger
- touch E.32's or E.33's files; this stage writes only stage_e32b_*
  files, plus its return
- register anything; N stays 538
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
GUARDRAILS AND DELIVERABLE
============================================================

Start and end checks, quoted verbatim:
- `git status --short`;
- the holdout status;
- the E.32 test-seal guard check, if E.32 has written it;
- `wc -c REGISTRATION.md`;
- the harness;
- the spend ledger line count and sha256, and N.
Commits touch only this stage's files. Before committing, `git status`
shows no file of E.32 staged. Before ending, confirm no worker or shell
is still running.

Write:
- reports/stage_e32b_ranking.md (the table and its reading);
- reports/E.32b_RETURN.md;
- one progress.md entry;
- one docs/STAGES.md line;
- one final commit "Stage E.32b directional rerank". Do not push.

The return's fixed sections:
1. Summary, at most 250 words. Cover:
   - the new top 10 pairs;
   - where ZM, ZL, QM, MGC and the micros landed, and why;
   - the next products after ZM.
2. Guardrail evidence.
3. Results.
4. Delegation record, with each reviewer's confirmed model.
5. Verification.
6. Open choices.
7. Decisions for the user, each with a recommendation.
8. Session cost, per CLAUDE.md, never estimated.

The last thing before ending: list every open choice in section 6.

END PROMPT
