# Stage E.19 STATE (prop economics: the Topstep Combine-to-XFA funnel's cash value to the user)

Prompt docs/prompts/STAGE_E.19.md. Lead Opus 5.5 xhigh, session 087ee4a8-1bec-45a0-a9cd-046722cb28a9. All times PDT
(America/Vancouver), from `date`. On resume: read this file first and skip finished steps.

## In force

- Harness: v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32 (preflight OK at start, 17:03).
- Trial registry at start: N = 480, 4 lines, sha256 55b1d24c65d484186c4494294fdae03e374141eba5c3f210800d77e56e95289d
  (must be unchanged at end: no registration in this stage).
- Spend ledger at start: 36,402 lines, sha256 034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
  (must be unchanged at end: no purchase, no Databento call).
- Holdout at start: all_ok True, unlocks_logged 0 (top, holdout_2, MCL, MGC, MHG, NG). REGISTRATION.md 0 bytes.
- Frozen code not to be edited: ml_route_v2/ (v2 freeze, 91 files), rules/, sim/, screening/, data/ code, live/, ops/.
  New code goes in prop_econ/ and tests/test_prop_econ_*.py only.

## Steps

| Step | Status | Start | End | Artifacts / notes |
|---|---|---|---|---|
| 0 read prompt and context | done | 16:54 | 17:02 | |
| 0 start checks | done | 17:03:05 | 17:03:13 | reports/stage_e19_briefs/start_checks.txt (checks.sh = E.18's plus the C1b freeze verify and a no-diff check on ml_route_v2 rules sim screening data/holdout.py live ops); all pass |
| 0 specs, interface, briefs | done | 17:04 | 17:09 | reports/stage_e19_briefs/sim_spec.md (lead's binding model), rules_schema.md, rules_provisional.json (E.0/E.12 values, dev only), brief_rules.md, brief_funnel.md, brief_returns.md; prop_econ/__init__.py, prop_econ/types.py (lead interface) |
| 1 TopstepRules-OpusHigh (worker-high, opus) | done | 17:09 | 17:24 | reports/stage_e19_rules.json, .md; pages under reports/stage_e19_briefs/pages/ (41 curl fetches, all 200). 214 rules (198 SOURCED, 6 INFERRED, 7 UNSOURCED, 3 CONFLICT), 42 practices, 48 added fields; validator: all quotes verbatim. Rulings L-11..L-16; FunnelCoder told (17:25) |
| 2 FunnelCoder-OpusXHigh (worker-xhigh, opus) | done | 17:09 | 17:41 | prop_econ/rules.py, funnel.py, vec.py, assemble.py; tests/test_prop_econ_{fixtures,funnel,vec,rules,assemble}.py; 117 tests (132 with returns) pass, ruff clean (lead wrapped its own types.py lines 17:42); vec == scalar on 24 configs + 12 rule variants + FINAL file; speed 20k XFAs x 756 d 0.3-0.6 s, 20k attempts 0.1 s, 20k 5-slot campaigns 1.2 s. 14 questions (reports/stage_e19_briefs/funnel_questions.md) ruled in L-17 |
| 3a ReturnsCoder-OpusHigh (worker-high, opus) | done | 17:09 | 17:15 | prop_econ/returns.py; tests/test_prop_econ_returns.py; reports/stage_e19_returns_summary.json, .md. 15 tests pass, ruff clean; D6 windows from screening/vehicles.py:50-63; sigma_full NQ 2999, CL 1396, GC 1225, ZN 368, 6E 470 $; kept 1203-1222 of ~1248 dates (skips: early-halt days); 4 spec questions answered in L-10 |
| 3b GridCoder-OpusHigh (worker-high, opus): grid runner, aggregator, full run | done | 17:43 | 19:26 | brief reports/stage_e19_briefs/brief_grid.md; prop_econ/grid.py, report.py; reports/stage_e19_runs/; reports/stage_e19_results.json; reports/stage_e19_briefs/results_tables.md. Run restarted 18:02 after the churn addition (first partial run discarded); 780/780 jobs, 0 failures, 82.7 min on 4 workers (~1.15 GB each), 4,464 records; 148 prop_econ tests pass; every kept job carries fingerprint d4644acce4988b94 (rules file after the RR-4 edit). Q1-Q20 in grid_questions.md, ruled in L-20 |
| 5a RulesReviewer-FableXHigh (worker-xhigh, fable) | done | 17:43 | 18:00 | brief reports/stage_e19_briefs/brief_rules_review.md; reports/stage_e19_review_rules.md; reports/stage_e19_verify/ (started early: the rules file is final). 1 BLOCKING (RR-1 account stacking / excessive purchases: churn metrics and label needed), 4 SHOULD FIX, 14 NOTE; 207/207 rule and 42/42 practice quotes verbatim; 5/5 re-fetched pages unchanged; L-11 upheld. Rulings in reports/stage_e19_rulings.md (18:02); RR-4 text fix to P35 applied 18:01 (rules sha256 now ebc29f8b41edfdb0...); GridCoder told to add churn metrics (18:00) and that the fingerprint change is benign (18:01) |
| 5b EconReviewer-FableXHigh (worker-xhigh, fable), Phase A (blind recompute) | done | 17:43 | 17:59 | brief reports/stage_e19_briefs/brief_econ_review.md; reports/stage_e19_verify/recompute.json (written 17:57:25, before any results file existed; results.json absent at 17:59:04); returns table rebuilt independently, matches the summary to 1e-9, demeaned mean 0; own simulator 60 configs x 20k (176 s); hand paths 11/11 to the cent; 8 convention readings C1-C8 for Phase B. Phase B by SendMessage after the grid |
| 5b EconReviewer-FableXHigh Phase B (compare + code review) | done | 19:27 | 19:46 | reports/stage_e19_review.md: 0 BLOCKING, 2 SHOULD FIX (ER-1 SEs omit pool sampling error, total 1.3x-2.5x; ER-2 churn metric floor, omits credit resets), 11 NOTE. Headline reproduces: per path 1e-11 on identical shocks; 60 configs agree in sign and best f within 2.6 total SD. ER-4: zero edge negative in all 1,500 in-band records; positive only at f 0.50 with the DLL (+27 at 50K Std). |
| 5b Phase C (verdict cells: campaigns, DLL-on, B2F, keep-D, f 0.50 DLL cell) | done | 19:46 | 19:56 | appended to reports/stage_e19_review.md section 7: 48 campaign quantiles within 1 purchase / 1.3%; cycle cells |z| <= 1.1; ER-14 SHOULD FIX (the f 0.50 DLL-on zero-edge +27 is +2.5 (10) on independent shocks). Final counts 0 / 3 / 11; all three SHOULD FIX are text fixes, applied |
| 4 results md (lead) | draft done | 19:28 | 19:30 | reports/stage_e19_results.md assembled by reports/stage_e19_briefs/make_results_md.py from results_narrative.md + key_numbers.py output + results_tables.md; numbers in the narrative checked against the tables by script; final after the EconReviewer's Phase B |
| 5c rulings and fixes | done | 19:46 | 19:56 | reports/stage_e19_rulings.md (RR-1..RR-19, ER-1..ER-14); narrative fixed and results md reassembled |
| 6 return, progress, STAGES, end checks, end suite, commit | done | 19:57 | 20:15:45 | end suite 19:57:06-20:14:17: 7138 passed, 3 skipped, 3 xfailed, rc 0 (reports/stage_e19_briefs/pytest_end.out); end checks 20:14:40 all pass, identical to start (reports/stage_e19_briefs/end_checks.txt): 0 unlocks, REGISTRATION.md 0 bytes, ledger 36,402 / 034a454b..., N 480 / 55b1d24c..., preflight OK, no diff in frozen code; docs/STAGES.md line; .gitignore npz line (L-21); memory no-input-edits-mid-run.md; tokens to 20:15 (03:15Z): 99,859,166 (lead 42.2%); reports/E.19_RETURN.md assembled; commit "Stage E.19 prop economics" 20:15:45 (STATE row amended into it); no push |

## Lead decisions so far (copied into the return's Open choices)

- L-1 (17:09): headline return model is semi-continuous sizing (fractional contracts above one, at least one contract of
  the day's vehicle) on the pooled 5-path bootstrap (product drawn per 5-day block); integer contracts per single product
  is the granularity sensitivity. Reason: the question is the funnel's economics as a function of risk; granularity is a
  vehicle detail a multi-product bot can approximate, and the per-product table shows where it binds.
- L-2 (17:09): the zero-edge bot takes a random direction each day (fair coin) on demeaned day-session returns; long-only
  is a sensitivity. Reason: a bot is long and short; long-only keeps index skew, shown separately.
- L-3 (17:09): daily P&L = a day-session hold [O_X, C_X) per contract; 1 or 3 round trips a day cost D8 RT each with the
  same exposure. Reason: the full-session sigma is the most cost-favourable reading, so the zero-edge cost drag is a
  lower bound; stated in the results.
- L-4 (17:09): edges are net of costs (prompt: "after costs"), so for S > 0 the cost model changes nothing but the gross
  edge needed (reported as S_gross = S_net + k x rt/sigma x sqrt(252)); costs bite only at zero edge.
- L-5 (17:09): MLL breach is checked against the day's worst intraday P&L from the 1-minute bars (all costs counted, no
  drift credit); liquidation at the floor, gap-through overshoot ignored.
- L-6 (17:09): billing period 30 calendar days = 21 trading days; reset next day; attempt cap 60 per cycle; XFA and
  attempt horizon 756 trading days, remaining balance worth 0; Live Funded call-up ends the XFA with balance worth 0.
- L-7 (17:09): payout policy headline = the largest allowed amount as soon as eligible; keep-D 0.5 x MLL sensitivity.
- L-8 (17:09): Task 5 split into two Fable xhigh workers (EconReviewer: simulator and recomputation; RulesReviewer:
  rule table against its quotes and the terms) instead of one, for context hygiene; both fable xhigh as the prompt routes.
- L-9 (17:09): sizing grid adds 0.20 to the prompt's example, and 0.35 / 0.50 as diagnostics outside the policy band
  (to show whether expected cash keeps rising with aggression, the account-stacking incentive).
- L-10 (17:16, ReturnsCoder's questions): (1) a date is kept only when the bars exactly at O_X and C_X - 1 min exist,
  so CME early-halt days are skipped (Topstep flattens early on those days anyway); accepted. (2) cost_wall.json has no
  NQ, CL, GC, M6E rows: the coder applied E.10's formula (commission + 2 x worst bucket side) to D8, reproducing the
  five published rows to 3 decimals; accepted. (3) ShockSet carries all five ProductSpecs under a one-product draw;
  accepted. (4) MCL and M6E D8 costs are measured at q_c 4 and 10; used as they stand (per-contract cost at the depth
  the D8 model calibrated).
- L-11 (17:25): terms reading. Topstep ToU section 28 bans software that "crawl[s]" or "spider[s]" web pages; the worker
  fetched 41 named pages one at a time (>= 3.5 s apart, no link-following, robots.txt allows the article paths). The lead
  reads that as outside the crawl/spider ban and accepts the fetches; flagged for the user, and RulesReviewer checks it.
- L-12 (17:25): rules the simulator models from the added fields: the DLL (chosen at Combine checkout) applies in both
  phases; Combine consistency best day < 0.55 x total profit (strict); XFA consistency <= 40% (inclusive). Post hoc in
  the wallet: the API subscription $14.50/month (third party, needed by a bot) per 21 trading days of operation (one per
  user: per cycle in the one-slot view, per elapsed month in campaigns); payout transfer fee $0 (Wise/Aeropay; ACH or
  wire $30 per payout shown as a sensitivity).
- L-13 (17:25): call-up is discretionary (www stats: 0.71% of XFA participants called up). Headline: no automatic
  call-up; sensitivities: call-up right after the 1st and the 3rd payout, ending the XFA with the balance worth 0 to the
  bot (LFA bans the API).
- L-14 (17:25): not modelled, carried as terms constraints in the recommendations: the Slowdown / FTP path for
  "Excessive Resets and Trading Combine purchases" and "Activating and losing many XFAs in a short period" (no threshold
  published, R061); the Responsible Trading Program when several accounts hit the MLL the same day (R059/R060, relevant
  to copy-trading); no VPS (the bot runs on the user's own machine, R042); no cross-account hedging (R039); a minimum
  payout balance after the first payout (R058, no amount published, cannot be simulated).
- L-15 (17:25): the voluntary-close payout (50% of balance up to $5,000, R056/R057) is only on a stale www page (June
  2025); headline values an XFA alive at the horizon at 0; sensitivity: close at the horizon for 0.9 x min(0.5 x B, 5000).
- L-16 (17:25): scaling-plan boundary (UNSOURCED, R092/R143/R196): both readings run in the UNSOURCED sensitivity.
- L-17 (17:42, FunnelCoder's 14 questions): all accepted as implemented: k = 1 at a Sharpe edge (k only matters for
  costs at zero edge); the scaling tier after a morning payout is read from the prior close, before the payout; a DLL /
  MLL tie is an MLL breach (exact arithmetic, conservative); D_open <= 0 raises (unreachable); the Consistency path
  needs window net > 0; a call-up or payout limit right after a payout ends the XFA that day; intraday MLL trailing,
  payout_total_usd call-ups and Combine time limits raise UnsupportedRule (none in the FINAL file); rebill before a
  same-day reset; the DLL discount applies to the monthly price only, not resets (conservative; not published);
  activation and XFA start the day after the pass, Back2Funded the day after the breach; max_payouts raised to 192
  (worst case seen 189; overflow is credited at XFA end and counted); campaign cap 400 purchases; payout fees and the
  API fee are applied post hoc by the grid runner (L-12).
- L-18 (17:43): Task 5's EconReviewer starts its blind Phase A (own returns table, own simulator, hand paths) while
  the grid runs, and is resumed by message for Phase B (comparison and code review) once the results are final; the
  rules review started at 17:43 as soon as the rules file was final. Reason: the review is the longest serial step.
- L-19 (18:00, ruling RR-1): churn label per configuration: "low" <= 2.0 Combine purchases per 21 Combine-phase trading
  days per account, "medium" <= 4.0, "high" above; recommendations only from low churn inside f <= 0.25. Topstep
  publishes no threshold; this is the lead's reading of "not excessive".
- L-20 (19:28, GridCoder's questions): L-19's churn label stays per account (Combine purchases per 21 Combine-phase days);
  the 5-slot campaign rate (2.86 to 8.73 purchases per 21 elapsed days in year one) is reported beside it (Q20). The
  cost-wall comparison is unpaired (different shock seeds, Q1) and T5 differences use unpaired SEs (Q3): accepted, both
  conservative. API list price $29 (Q8): given by arithmetic from the "API excluded" column, not rerun. R025 (DLL cap
  needs the DLL at a new purchase) coincides with the modelled DLL-on scenario (DLL chosen at purchase); R058 cannot be
  simulated (no amount). The effective zero-edge Sharpe uses a 200-row replay per phase (Q-list): accepted as a
  description, not a verdict number.
- L-21 (19:48): commit the 780 run JSONs (8.8 MB), results.json (13 MB), the saved Topstep pages and the reviewers'
  verify directory (2 MB); leave the 97 MB of headline .npz pool arrays out (git-ignored; regenerable from the seeded
  grid). Earlier stages committed their raw pages (E.12 topstep_pages, E.18 pages) and run files up to ~30 MB.
- L-22 (19:57): end suite = E.18's command (`uv run pytest -q -p no:cacheprovider` at nice 10), PYTHONPYCACHEPREFIX unset,
  detached (setsid nohup) -> reports/stage_e19_briefs/pytest_end.out. No start suite: the prompt's Task 0 lists checks
  only, and the end suite covers the new prop_econ tests and the untouched rest.
- L-23 (19:58): verdict wording. "No" at zero edge, with the two dependencies the reviews found: trading costs plus the
  API fee (at a net Sharpe of exactly 0, 50K is about break-even) and sizing beyond the terms (f 0.50 with the DLL is
  about break-even, sign not established, ER-14). The "best setup" figure (+$906) is DLL + Back2Funded with payout
  policy max; keep-D was tested only with both off, so the combination is not claimed.
