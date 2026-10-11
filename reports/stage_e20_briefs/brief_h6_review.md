# Brief: H6Reviewer-FableXHigh (Stage E.20 Step 2, independent review before the H6 freeze)

One objective: an independent, adversarial review of the H6 pre-registration and its code before
the freeze, registration and single evaluation. Three checks:
1. The text (reports/stage_e20_prereg_H6.md) against docs/prompts/STAGE_E.20.md F2, F3, F5 and F9:
   every F5 clause present and exact; nothing added beyond F5 except what F5 leaves to
   implementation (record each such choice and say whether it is the natural reading); T3's status
   and the GEX ruling (reports/stage_e20_briefs/product_NQ.md section 4c) consistent with F5's
   condition ("only if the NQ reader clears the GEX source under its terms before any NQ bar is
   read").
2. The rule against the papers: Baltussen, Da, Lammers, Martens (JFE 2021), full text on disk at
   reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md (grep it; never load it whole),
   and the NQ reader's notes (reports/stage_e20_briefs/shared/baltussen_notes.md,
   shared/rosa_2022_notes.md). The prereg's section 7a lists the known differences; check that the
   list is complete and correct. F5 binds: a difference is a disclosure, not a change, unless the
   text misstates F5.
3. The code against the text: h6_rod/ and tests/test_h6_rod_*.py (the build notes are
   reports/stage_e20_briefs/h6_build.md). In particular:
   - causality: the signal uses only P(prior C) and P(C-30), both closed before the entry intent;
     the T2 median uses only earlier eligible dates inside the allowed ranges (prereg section 2);
     the T3 mask uses only the GEX row dated the previous equity trade date; no future value enters;
   - the clock: CP1's conventions (strategy/members/k1/cp1.py); C on shortened days; the exit rule;
     the engine's flatten on shortened days; the instrument_id rule; each no-trade reason;
   - the engine path: the frozen engine called unchanged (screening/stage_e_engine.py,
     screening/stage_e_rules.py, ml_route_v2/simulate.py), D8 MNQ costs per bucket, the roll-blackout
     refusal, the MLL restart, the XFA gate; costs taken from the engine's own records;
   - the statistic: ml_route_v2.gate0._b_test called as the prereg says; Holm step-down at 0.025 over
     m = 3; the annualized Sharpe over every equity trade date of the verdict window with zeros;
     the pass bar's four conditions; the 1.5 x slippage and bp descriptives;
   - the guard (F3): planted cases cover processed_hist, sealed, holdout, other roots' stores, and
     a 2024-03-01 bar; the loader can open only the NQ store; GEX rows on or after 2024-03-01 cut;
   - the run discipline: freeze check, registration check, run-once marker before any bar, no
     data condition raising after the marker, no second evaluation possible;
   - anything that would let the evaluation see NQ bars outside 2019-05-06..2024-02-29, or read
     reports/stage_e12_gate0.*, E.15, E.17 or E.18 results.
   Run the h6_rod tests yourself (`uv run pytest -q -p no:cacheprovider tests/test_h6_rod*.py` at
   nice 10) and add any adversarial test you need in a scratch location (not in tests/), on
   synthetic bars only.

## Output

reports/stage_e20_review_h6.md: a verdict (APPROVE, APPROVE WITH FIXES, or BLOCK), then findings,
each with an id (H6R-n), severity (BLOCKING, SHOULD FIX, NOTE), the file and line or prereg section,
what is wrong, why it matters, and the fix you recommend. A BLOCKING finding is one that would make
the single evaluation's verdict wrong or the run unrepeatable; SHOULD FIX is a material weakness
that the freeze should not carry; NOTE is for the record. Reply to the lead: the path, a summary of
at most 200 words, and anything you could not check.

## Boundaries

- No real data: do not open any data store (data/processed*, data/sealed, data/raw, data/vendor, any
  parquet), the GEX CSV's values, reports/stage_e12_gate0.md or .json, or any E.15, E.17 or E.18
  result. Do not run `python -m h6_rod check|register|evaluate` against the real files.
- Do not edit h6_rod/, tests/, the prereg or any frozen file: report; the lead applies fixes. No
  ledger writes, no commits, no Databento or TopstepX. Do not spawn agents.
