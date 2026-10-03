# Brief: FreezeReviewer-FableXHigh (worker-xhigh, fable). Stage E.12 Task 8 (freeze review)

You are the independent reviewer of the ML route v2 freeze in Stage E.12 (prompt
docs/prompts/STAGE_E.12.md: read SCOPE, GUARDRAILS, Tasks 1, 3 and 8). A different model (Opus)
wrote the design edits, the code and the manifest; your job is to find what it got wrong. You run
BEFORE the freeze commit, so a BLOCKING finding can still be fixed without changing a Gate 0 rule
after the commit (the lead's ordering choice). No market data exists for v2 yet; read none.

## Inputs
- The decisions: docs/DECISIONS.md V18-V23 (lines 332-445), V23 in particular (its 19 items).
- The design: docs/STAGE_E_ML_V2_DESIGN.md (git diff 8b93e98 -- docs/STAGE_E_ML_V2_DESIGN.md shows
  every E.12 edit; read the diff, then the sections it touches: V2.1, V2.2, V2.2b, V2.3, V2.7, V2.8,
  V2.9, V2.12).
- The manifest: reports/stage_e12_ml_v2_freeze.json (schema ml_v2_freeze/1) and its builder
  reports/stage_e12_briefs/build_v2_freeze.py; the verifier ml_route_v2/phase1/freeze.py.
- The code: `git diff 8b93e98 -- ml_route_v2 tests` plus the new ml_route_v2/phase1/ package and
  ml_route_v2/signals/k9.py; the worker reports reports/stage_e12_briefs/v23coder_report.md and
  phase1coder_report.md; the STATE file reports/stage_e12_STATE.md (lead rules P-1..P-6).
- The Task 2 files: reports/stage_e12_cme_margins.json (the blocked margin route),
  reports/stage_e12_topstep_150k.md, reports/stage_e12_ec_k9_2019_2024.json and .md.
- The ranking script reports/stage_e12_briefs/rank_phase1.py (the subset rule as applied).

## Checks (each one: PASS, or a finding graded BLOCKING / SHOULD FIX / NOTE with file:line)
1. V23 item by item (1-19 and the research-window Holm slot): the frozen design states each
   decision, and the built code implements it as the DEFAULT (constants, decide, cost_filter,
   gate0, portfolio's release-window rule, K9, account 150K, payout reset delay). Item 18 is the
   only open item. Quote the design line and the code line for each.
2. No free parameter left open: grep the design for "Open", "open", "TBD", "the freeze session",
   "later", "until"; every number Gate 0 and the c/sigma filter use is fixed in code before data
   (no argument, environment variable or data-dependent choice can change the Gate 0 bar, tau,
   the horizons, CPCV blocks, embargo, top fraction, the ridge lambda, Holm, the 30-trade floor).
   The P-2 list rule leaves no choice to the lead at Task 6 (the list is a function of the bought
   products, the bars' coverage and the admissible pairs only).
3. The manifest covers everything Gate 0, the filter and the panel read: every ml_route_v2 module
   imported on the phase-1 path, every data file opened (calendars, release calendar, cost tables,
   EC-K9 files, start-rule records, catalog), and the harness modules it imports are covered by the
   harness manifest (v7 now, v8 later; v8 must not touch any of them). Name anything Gate 0 reads
   that neither manifest hashes. Run the verifier: `uv run python -c "from ml_route_v2.phase1.freeze
   import verify_v2_freeze; import hashlib,pathlib; p=pathlib.Path('reports/stage_e12_ml_v2_freeze.json');
   verify_v2_freeze(p, hashlib.sha256(p.read_bytes()).hexdigest()); print('ok')"`.
4. Leakage and window: the phase-1 path cannot read a bar dated on or after 2024-03-01, any
   research-window bar row (S_X reads volume only: check), any holdout or sealed store. The run-once
   guard and the list-hash check cannot be bypassed by a CLI flag.
5. The lead's own rules P-1..P-6, the MES contingency P-1a, the E|m_1| proxy switch (V2.1 step 6)
   and the subset-rule application P-4: each consistent with the design text and V23, and the
   ranking script implements P-4 exactly (pass 1 = the seven cluster-best, acct-1 first, 3% margin).
6. The EC-K9 2019-2024 calendar: the rule matches C9's text (reports/stage_e10_catalog_K9.md);
   spot-check 5 dates against the saved official pages (grep, never whole files); uncovered spans
   are excluded, not guessed.

## Output
reports/stage_e12_review.md, Part 1 "Freeze review": a table of findings (id F-1.., grade, what,
where, why it matters, the fix you suggest), then the per-check PASS list with evidence. Grade
honestly: BLOCKING only for something that would make Gate 0's verdict wrong or unauditable, a
decision implemented against V23, or a leak.

## Boundaries
Read-only. Do not edit any file except reports/stage_e12_review.md. No network, no key, no
Databento, no commits. Run tests only if a check needs it (nice -n 10, -p no:cacheprovider).
Follow CLAUDE.md's context hygiene (read by section, grep, short outputs).

## Return (at most 200 words)
The path, the count by grade, each BLOCKING and SHOULD FIX finding in one line, and anything you
could not check.
