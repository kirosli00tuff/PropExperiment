# Brief: ScreenVerifier-FableXHigh (Stage E.20, independent check of the Part C screen numbers)

CLAUDE.md: every number entering a verdict gets an independent fable xhigh check. One objective:
verify the F7 screen verdict of the search (reports/stage_e20_search.json and .md: SCREEN FAIL;
median-path t -1.334, PBO 0.596, annualized net Sharpe -0.826, DSR at N = 528 about 0) and the
order of events, without trusting pattern_search's own summary.

1. Recompute from the saved nested record (the run's state directory ~/.cache/propexp_e20_search:
   the stage checkpoints and cpcv/cpcv_units.jsonl; and reports/stage_e20_search/), with your own
   code calling only frozen functions where a frozen definition exists (pipeline._daily_t, cpcv.pbo_cscv /
   funnel.multiple_comparisons.probability_of_backtest_overfitting, cpcv.dsr_at_n, cpcv.sharpe_variance)
   and also by hand: the 5 path t statistics and their median, the path-average annualized Sharpe,
   PBO on config_daily (16 blocks), the DSR at 528 with the Sharpe variance over the 45 configurations.
   Check that path_daily covers every training-calendar date (1,248) with zeros where no trade.
2. Check the record's integrity on a sample: re-derive at least one outer split's selected-config
   daily P&L from its saved predictions or by one refit of that split's selected model with the frozen
   fit_model and score_split (nice 10, one fit at a time; keep compute light, a full test suite is
   running), and compare with the record.
3. Check the screen against plan section 9 and F7 (reports/stage_e20_plan.md, docs/prompts/STAGE_E.20.md):
   the bars, the fail, the final_selection, no leakage alarm (Sharpe below 4.0).
4. Order of events: the search freeze manifest (sha256 94ee86b02d1cb644c9307be958b7791587d42c062996a6220dc901d4fe5a0f2f)
   verifies (`uv run python -m pattern_search.freeze_manifest verify --sha256 <sha>`); the registry line
   r005-E20S (ledger/trial_registrations.jsonl, 17:43:59 PDT, N 483 -> 528) precedes the run (log
   reports/stage_e20_briefs/search_run.log, started 17:44:15) and the first CPCV unit's time; the panel's
   feature list equals the plan's 34 KEPT names plus rod_ret and rod_absratio; 45 configurations in the
   frozen order; nothing under data/processed_hist, data/sealed, data/processed (MES, research) or after
   2024-02-29 was read (code paths, logs, world_check.json).

## Output

Append a section "Search screen verification" to reports/stage_e20_review.md: verdict (VERIFIED,
VERIFIED WITH NOTES, NOT VERIFIED), your numbers beside the reported ones, findings (SV-n, BLOCKING /
SHOULD FIX / NOTE). Reply: the path, a summary of at most 200 words, anything you could not check.

## Boundaries

Do not rerun `python -m pattern_search run`, register anything, or edit the state directory, results,
registry, plan or code. No 2010-2019 store, no data/processed (MES, research), nothing dated 2024-03-01
or later. No commits, no ledger writes. Do not spawn agents.
