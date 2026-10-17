# Brief: ListReviewer-FableXHigh, Stage E.22 Part A, review of the four confirmation lists BEFORE any read

Lead: E.22 (Opus 5.5, xhigh). Independent, adversarial (a different model from the lead who wrote the lists).
No confirmation-window bar has been read by any run. Your review gates the list commit and every run.

## Inputs
- The lists: reports/stage_e22_k5_confirmation_list.json, _k3_, _k6_, _k8_ (machine-read; they govern) and
  reports/stage_e22_confirmation_list.md (restatement embedding each JSON's sha256).
- How they were built: reports/stage_e22_briefs/build_list.py and render_list_md.py.
- The lead's rulings: reports/stage_e22_briefs/partA_rulings.md (R-E22-A1..A15), the price-path declaration
  reports/stage_e22_price_paths.json, the not-run declaration reports/stage_e22_untestable_K8.json.
- Facts gathered from the records: reports/stage_e22_briefs/partA_facts_K5_K3.md, partA_facts_K6_K8.md,
  partA_decisions_scan.md, partA_harness_audit.md.
- Start rules: reports/stage_e_start_rule_K3.json, _K5.json, _K6.json, _K8.json. Power: research re-runs in
  reports/stage_e22_power_k3/, _k5/, _k6/, _k8/ and their replay comparisons reports/stage_e22_briefs/c2_compare_k*.md.
- The harness v13 change and its review: reports/stage_e22_harness_change.md, reports/stage_e22_harness_review.md.
- The rules: docs/STAGE_E_DESIGN.md D2 (146-204), D4 (244-296), D5 (298-346), D9 member coverage; docs/NULL_CRITERIA_E.md;
  docs/DECISIONS.md V14, V16, V18, V39; the E.5 precedent reports/E.5_RETURN.md and reports/stage_e5_k4_confirmation_list.json;
  the prompt docs/prompts/STAGE_E.22.md Part A (A1-A5).

## Check, at least
1. Every frozen trial of each cluster freeze is listed once with the right tier (from the screening cluster records),
   vehicle, legs, q_c, operative eps_X (reports/stage_e2a_epsilon.json), seed = 20260923 + ordinal, and the right
   run flag (Tier A/B run unless by design with no window or declared untestable; excluded never run).
2. Labels: source-overlap per the amendment's governing column (reports/stage_e2a_source_window_amendment.md:36) and R-04;
   D9 labels; inconclusive by design exactly where power says so; untestable only where declared.
3. Windows: S_X per root equals the start-rule files; price-path roots (GC for MGC, NQ for MNQ) as declared; MES 2020-02-03;
   cross-product windows as D4 states. Is the MNQ -> NQ reading (R-E22-A5) defensible under D2/D4/U8/V39 and the prompt
   A2, or should K8-wkndbtc-01 have been "untestable (missing MNQ)"? (It is not run either way; say whether the label or
   anything else in K8 changes.)
4. Power: each trial's power object equals its research re-run record; supply and n_b consistent with D4; the replays match
   the screening records except power (c2_compare files).
5. K = 5 and N = 533 (R-E22-A10, A11): sources correct, consistent with the prompt A4 and E.5's precedent? A Tier A trial
   with no record at p = 1 (R-E22-A13): consistent with the v13 verdict code?
6. Anything in a list that is a choice made with knowledge of confirmation-window outcomes (there should be none), or
   that differs from "each member exactly as its cluster freeze defines it".
7. Will `python -m screening.stage_e_runner ... --dry-run` under the committed harness resolve every member? (You may run
   the dry run for each cluster: `uv run python -m screening.stage_e_runner --harness-sha256 <harness in
   reports/stage_e2b_harness_freeze.json> --cluster KX --all --window confirmation --research-root data/processed
   --step2-root data/processed_step2 --out-dir /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/1414530f-7e36-4869-ba6c-9cc19af7d435/scratchpad/lr_dry_KX --dry-run`
   plus `--untestable reports/stage_e22_untestable_K8.json` for K8. The dry run reads only timestamps/trade dates,
   writes nothing and runs no engine. Never run without --dry-run; never pass --run-once-marker.)

## Boundaries
Read-only except your output. No confirmation run (dry run only), no bar values, no commit, no edits.

## Output
reports/stage_e22_list_review.md: findings numbered and classed BLOCKING (no read until fixed), SHOULD FIX, NOTE; each with
the list, trial and field, the problem and a suggested fix; plus what you verified and how. Return the path, counts by class,
and a summary of at most 200 words.
