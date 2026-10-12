# Brief: VerdictVerifier-FableXHigh (Stage E.20 Step 4, independent recomputation of H6)

One objective: recompute H6's verdict independently, without reading the lead's statistics first,
and check the order of events. The rule is reports/stage_e20_prereg_H6.md (FROZEN, commit 498fd05,
manifest reports/stage_e20_h6_freeze.json sha256 22e606f0b74532e267a4155d93e295702ff86f6e8f4143236882f3c2f230e795).

## Order of work

1. Before opening reports/stage_e20_H6_result.json or .md (or the evaluate log's verdict line),
   build your own computation from the prereg text and the frozen inputs:
   - the NQ store (path and sha256 in prereg section 2; verify the sha256 first; read only
     ts_event, open, close, instrument_id, trade_date and what the D8 costs need), the GEX CSV (E.14
     copy, sha256 in section 7; rows on or after 2024-03-01 never used), the frozen equity calendar
     (data/calendars/equity.py, data/group_session.py), the D8 MNQ cost table
     (screening/stage_e_frozen.py), MNQ's roll-blackout dates (as the prereg defines), and the
     frozen engine's flatten rule (rules/sessions.py);
   - an independent bar-level reconstruction, written by you (do not import h6_rod): per verdict
     date, r_ROD, eligibility and its reason, the T2 threshold under the warm-up rule, the T3 mask;
     per trade, the entry fill (the C-30 bar's open), the exit fill (the open after the first present
     bar at or after C-2, or the engine's forced flatten where the prereg says so), gross ticks, the
     D8 round trip c, net; then per test the trade count, mean gross, mean c, t_B and one-sided p
     (you may call ml_route_v2.gate0._b_test, the frozen statistic the prereg names, and also
     recompute it by hand), Holm at 0.025 over m = 3, the annualized net Sharpe over every equity
     trade date of the window with zeros, and the pass bar.
   - Where your bar-level reconstruction cannot reproduce an engine-only effect (an MLL-breach
     flatten, a D9.7 exit, a locked-market fill, an engine refusal), say so and quantify it from the
     result file in step 2; do not guess.
   Write your numbers to reports/stage_e20_briefs/h6_verify_independent.json before step 2.
2. Then open the lead's result and compare: every verdict number (trades, mean gross, mean c, mean
   net, t_B, p, Holm decision, Sharpe, PASS/FAIL), per test; the eligibility and refusal counts; a
   per-trade match (dates, sides, entry and exit prices, costs) to the cent where both exist.
   Every difference is explained or reported as a finding.
3. The order of events, from git and the registry: the H6 freeze commit (498fd05) precedes the
   registry line r004-E20H6 (ledger/trial_registrations.jsonl), which precedes the run-once marker
   reports/stage_e20_H6_RUN_ONCE.json, which precedes the result; the marker and the result record
   the freeze and registration they ran under; the evaluation ran once (one marker, one result); the
   freeze manifest still verifies (`PYTHONPATH=. uv run python reports/stage_e20_briefs/h6_freeze_manifest.py verify <sha>`).
4. The guard: from the result and the code, no bar outside 2019-05-06..2024-02-29 and no store other
   than NQ's was read.

## Output

reports/stage_e20_review.md (section "H6 verification"): a verdict (VERIFIED, VERIFIED WITH NOTES,
or NOT VERIFIED), your independent numbers beside the lead's for every verdict figure, then findings
(H6V-n, BLOCKING / SHOULD FIX / NOTE). BLOCKING: a verdict number or decision that is wrong; it is
resolved by finding the code error, never by a second evaluation. Reply to the lead: the path, a
summary of at most 200 words, and anything you could not check.

## Boundaries

Read no other store and nothing dated 2024-03-01 or later; do not read reports/stage_e12_gate0.*,
E.15, E.17 or E.18 results. Do not run `python -m h6_rod evaluate` or `register`, and do not delete or
edit the marker, the result, the registry or any frozen file. Compute at nice 10, one heavy job at a
time. No commits, no ledger writes. Do not spawn agents.
