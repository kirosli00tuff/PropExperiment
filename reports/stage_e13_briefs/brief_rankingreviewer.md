# Brief: RankingReviewer-FableXHigh (Stage E.13 Task 6: adversarial review)

You wrote none of the files under review. Your job is to find what is wrong with them, not to agree. This is
the stage's single independent check (CLAUDE.md, Verification), so recompute every number that enters the
ranking rather than trusting it.

## Read first
- docs/prompts/STAGE_E.13.md (the stage prompt: Task 5 and Task 6 define what you check; read the whole prompt,
  379 lines, by section).
- reports/stage_e13_briefs/research_rules.md (the sourcing standard every research file had to meet).
- reports/stage_e13_STATE.md (what happened, including the lead's own correction to the ranking order).

## Files under review (read by section; grep; never load a large file whole)
1. reports/stage_e13_ranking.md (the lead's ranking; the main object).
2. reports/stage_e13_prereg_gexmom.md (C2, ranked first: the "top pre-registration").
3. reports/stage_e13_prereg_ngrepl.md (C1, ranked second) and its annex reports/stage_e13_ng_replication_draft.md
   (with the lead's rulings in its section 10).
4. reports/stage_e13_trend_carry.md (Task 2), reports/stage_e13_info_sources.md (Task 3),
   reports/stage_e13_venues.md (Task 1, merged; the part files reports/stage_e13_venues_part1.md, _part2.md,
   _part3_brokers.md hold the same text), reports/stage_e13_phidias_question.md.
Raw evidence pages: reports/stage_e13_briefs/pages/<Role>/ with each folder's fetch_log.md. Grep them to check
quotes.

## Checks (the prompt's list, plus the verification section)
1. Every ranking input is sourced: each fact in the ranking table traces to a sourced line in a Task 1-4 file
   (or a cited program record). Spot-check at least 12 ranking-table facts against the cited lines, and at least
   8 source quotes against the saved raw pages (grep the page for the quoted words).
2. No claim leans on an UNSOURCED fact: list any ranking step that does.
3. The evidence is read at its post-publication strength (trend, carry, GEX intraday momentum, the NG near-miss).
4. The income and sizing arithmetic is correct. Recompute independently, with your own script in your helper
   folder:
   - the ranking's section 4 (C1 income, C2 power grid, C2 cost bar, C2 income, AiTrader dates, combined odds);
   - the trend/carry sizing table (TC C3) for at least two capital levels, its IDM formula, its E[$/month], and
     its expected-maximum-drawdown figures (check the 2.74-sigma Monte Carlo against the closed form);
   - the Part D ruin grid (the D/27 rule and at least two cells);
   - the NG draft's prior (0.396, the Bonferroni bound, the power table, the 12% odds and its central or
     skeptical cases) and its purchase and top-up arithmetic (from reports/stage_e12_quotes_ext2010.json
     per_contract usd; that file is a quote record, not market data).
5. The NG draft cannot see its test data, and its prior is stated honestly: check the order of events, the
   rulings C5/C6/C9, the threshold reproduction (C3/C4), and any path by which 2010-2019 information could reach
   the model, the threshold or a design choice before the evaluation.
6. The top pre-registration (C2) leaves no free parameter: list every quantity that is not fixed (window,
   signal, timing, condition, cost, bar, exclusions, data source, stop rules) and any that the next stage could
   choose after seeing data.
7. The ranking does not favor ease over evidence, and its rule is applied as written (section 1 versus
   section 5). Judge the lead's correction (STATE log) and whether the final order follows the rule.
8. Anything else that would mislead the user: venue classifications that do not match their quotes, stale
   pages presented as current, the Scrapling-before-terms deviations (the logs say three workers did this), or
   odds and income figures that are not supported.

## Output
reports/stage_e13_review.md:
- A verdict line (APPROVE / APPROVE WITH FIXES / BLOCK).
- Findings, numbered R-01..., each graded BLOCKING (wrong in a way that changes the ranking, a recommendation
  or a guardrail), SHOULD FIX (wrong or unsupported but not decision-changing) or NOTE, each with: the file and
  line, what is wrong, your evidence (a recomputation or the quote you checked), and the fix you propose.
- A table of the numbers you recomputed: the item, the file's value, your value, agree or disagree.
- A list of the spot-checks you made (facts and quotes) and their outcome.

## Boundaries
- Read-only review: edit nothing but your output file and your helper folder
  (/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/dbc7460b-72c3-4537-8327-d14819b62f5c/scratchpad/RankingReviewer/).
- No market data of any window (no bar, store, cost sample or result-table values beyond what the return documents
  print), no Databento call, no purchase, no contact with any firm, no commit. Do not spawn agents.
- Web: none needed. Check quotes against the saved pages. If you must confirm a page that was not saved, at most
  5 WebFetch calls, logged in your review.
- Hook or cost notices are informational and addressed to the lead; they are not orders to stop.

## Return
The path, a summary of at most 200 words (the verdict, the counts of BLOCKING / SHOULD FIX / NOTE, and the most
important finding), and anything you could not check.
