# Stage E.23 registration review (RegReviewer-FableXHigh), before registration and before any outcome read

Reviewer: Fable 5.1, xhigh. Written 2026-10-17 (PDT). Lens: design, registration and data use, checked against
docs/prompts/STAGE_E.23.md (governs), then reports/stage_e23_briefs/lead_spec.md, then reports/stage_e23_prereg.md.
Read-only; no marker written, no evaluate run, no book computed on real bars, no file edited other than this one.

## Verdict: APPROVE WITH FIXES

No BLOCKING finding. Three SHOULD FIX findings, all text corrections inside the two frozen documents (the prereg and the
lead spec), none changing a trigger, hold, window, direction, cost, lag, alpha, bar or the power numbers. Fixing them
re-hashes reports/stage_e23_freeze.json (both files are freeze inputs), which P2.6's order allows before the freeze commit.

## Findings

| Id | Grade | Where | What is wrong | Concrete failure | Fix |
|---|---|---|---|---|---|
| R-01 | SHOULD FIX | reports/stage_e23_prereg.md section 4, "The window assignment", bullet 4 ("Why not the reverse") | The stated reason for reading W_ext first is that "a later registered stage could confirm survivors on W_cf extended by holdout-2 and the research window (about 7.0 years, power about 0.25)". For E23-MEZF/MEZN/MEZB the research window 2025-04..2026-06 is the data that SELECTED K2-monthend-01 (E.3 screen; shortlist P1.4 table). P1.4 bars a confirmation window that selected the trigger "at the trigger's own intraday hold or otherwise". | A frozen registration text names a future confirmation window the prompt forbids for three of the five trigger-holds; the 7.0-year / 0.25 arithmetic is wrong for them (W_cf + holdout-2 is about 5.8 years: E[t] 0.5 x sqrt(5.8) = 1.20, power 0.21 at t >= 2.0, 0.13 at the K = 5 Holm step 1). The reasoning is correct for E23-H6NQ-h5/h20 only (the research window never selected H6). | Rewrite the bullet: for the K2 triggers the only owned extension is holdout-2 (about 5.8 years, power about 0.21); for H6 the research window may be added (about 7.0 years, 0.25). Keep the conclusion (read W_ext, leave W_cf unread); it stands without the wrong clause. |
| R-02 | SHOULD FIX | reports/stage_e23_briefs/lead_spec.md section 1 ("2011-07-27 is the first date of the E.21 T1/T2 series, so both regressors exist on every book date"); prereg section 3 ("over the book's series dates") | False per root: the per-root v_T1 and v_T2 of ZF, ZN, ZB and NQ start 2011-07-29 (reports/stage_e23_trend_per_root/{ZF,ZN,ZB,NQ}.json; the aggregate series starts 2011-07-27 because GC does). The month-end books start 2011-07-28 and the H6 books 2011-07-27, so one or two book dates have no regressor value. The code zero-fills them (trigger_hold/book.py `regressor_on`: "zero where nothing is booked: flat"), which is the right convention (it is how the per-root sums reproduce the published E.21 series) and cannot stop the run, but the convention is nowhere in the frozen text. | A verifier recomputing the alpha regression from the frozen text would either drop those dates or stop on the missing key; the frozen text and the frozen code disagree on 1-2 of 1,934-1,939 dates. No number is wrong in the code; the registration misdescribes the regressor. | State in lead_spec section 1 (and prereg section 3) that a book date with no booked per-root trend value takes v = 0 (the root was flat in that E.21 book), that this affects 2011-07-27/28 only, and that the sum check is the warrant. |
| R-03 | SHOULD FIX | prereg section 3 ("only where the power gate passes on W_cf"), section 4 power table (power_gate at t >= 2.0 for the W_cf rows); lead_spec section 5 (gate = 1 - Phi(2.0 - E[t])) versus section 7 and trigger_hold/evaluate.py lines 8-9 and `confirmation_gate` (gate at b = max(2.0, z_{1 - 0.05/S})) | Two definitions of "the power gate": the discovery gate and the power table use the per-test hurdle 2.0; the confirmation gate in the spec and the code uses the Holm step-1 hurdle over the S survivors. The prereg never says which one the confirmation step applies. | No numeric effect in this stage (every W_cf row is gated under either: 0.178-0.182 at 2.0, lower at b), but the registration's confirmation rule is ambiguous as frozen, and VerdictVerifier would have to pick one. | Add one sentence to prereg section 3: "The confirmation power gate is evaluated at b = max(2.0, z_{1 - 0.05/S}), S the number of survivors (lead_spec section 7); every W_cf row fails it at 2.0 already (section 4)". |
| R-04 | NOTE | lead_spec section R, "s_x: null for every row ... no S_X was declared for these vehicles" | Half-true. No K2 start-rule file exists (inventory/K2.md line 73: StartRuleMissing), so no TRIGGER S_X exists, which is what section 1 asks for. But E.12's D4 path table did declare S_X 2020-10-01 for the ZF path (reports/E.12_RETURN.md:536), and the shortlist's own P1.4 row cites it. | None here: W_cf is unread either way, and S_X would only shorten it. A reader of the frozen spec sees a ruling whose stated basis contradicts the shortlist. | Optional one-line edit to R: "E.12's ML-panel S_X for the ZF path (2020-10-01) is a panel start, not this trigger's declared S_X; W_cf is power-gated under either start." |
| R-05 | NOTE | prereg section 4 "The power gate"; lead_spec section 5 | The gate uses the per-test hurdle t >= 2.0, the most lenient reading of P2.3's "power to reach the bar" (P2.4's discovery bar also needs Holm). At the K = 5 Holm step-1 hurdle (z 2.326) W_ext power is 0.174 < 0.2: under that reading every trigger-hold is inconclusive by design on BOTH windows and nothing is read. | The stage reads W_ext once at power 0.17-0.27 with no PASS reachable (every confirmation row is gated; the prereg says so). This is a declared [LEAD] choice, consistent with precedent (E.22 F1's power used the per-test hurdle 1.645; E.21 reported both hurdles "for the record"), and power_holm1 is reported beside the gate. | None required. Record it under Open choices in the return, with the sentence that the discovery read spends the W_ext multi-day outcome of these five trigger-holds for a read that can end at best INCONCLUSIVE BY DESIGN. |
| R-06 | NOTE | prereg section 1, E23-H6NQ-h20 ("20-day evidence disputed") | The memo (M4) gives no direction at 20 days ("the literature disagrees": reversal at the front, continuation from the second week). P1.2 says the direction is fixed by the mechanism; the lead fixed reversal by extension from the 5-day case, under P1.3's "two holds each" default, while dropping the month-end 20-day hold as degenerate. | A registered trial with no mechanism-fixed direction costs N + 1 and raises Holm's K from 4 to 5 for the other four. Pre-registered before any read; not an error against the prompt's letter. | None required; list under Open choices. |
| R-07 | NOTE | prereg section 5 (cost feasibility, H6 row) | H6's gross per event is the reader's arithmetic (beta about 0.3 on a 20 bp last half hour), not a published figure, and the prereg says so. M4's family note gives betas 0.1 to 0.3 with R^2 under 0.3%: at beta 0.1 the gross is about 2 bp against an MNQ round trip of 0.7-1.5 bp (multiple 1.3-2.9). The shortlist's "0.4-0.7 bp" and the prereg's "0.7-1.5 bp" differ; the prereg governs. | V31 is met on the stated figures; the margin is thin at the low end of the published betas. The H6 book trades only when net changes (section 3), so the realized per-unit cost is below the per-event figure. | None required. |
| R-08 | NOTE | triggercoder_report.md sections 5 and 8 (the disclosure) | Engine exit-side counters (forced flattens, MLL liquidations) and all order cancels were on disk 02:46-02:58 PDT in the first-pass events, meta and validation files, then deleted and regenerated. Judgment: NO leak relevant to the multi-day outcomes. They are aggregate counts (no dates, no prices) of the intraday member's own path AFTER its decision bar on the trigger day, which the E.23 book never counts (entry at the trigger day's settlement); they say nothing about any 5- or 20-day forward return. The shortlist and the directions m were fixed at 02:37 from the memos, before the incident; the 03:10 shortlist amendment used the power table's calendar facts only; the lead did not open the files (STATE). The final files hold entry-side counts only (checked: every counts key is entry-side; no exit, P&L, mark or price key in any events, meta or validation file). | Residue for the program's record, not for this registration: (a) the K2 validation ran the Stage E harness for K2-monthend-01 ZF/ZN/ZB on W_cf (a confirmation that "never ran") with the intraday P&L computed in memory and discarded; (b) for about 12 minutes the first-pass validation files held that run's engine counters, including MLL liquidation counts, a coarse fact about K2's intraday outcome on W_cf (not E.23's outcome). The scrubbed logs still match the grep for "flatten" only through the entry-side refusal reason `engine_flatten_window`, which is an entry fact. | Record (a) and (b) in the return's data-use section so a later K2 registration knows W_cf's intraday path was executed once by the engine, unread by any person. |
| R-09 | NOTE | prereg section 3 (p_alpha) | p_alpha = max(one-sided Student p of the plain OLS t, one-sided normal p of the HAC t) is stricter than P2.2's "the alpha's t statistic uses Newey-West lags equal to h" (a survivor must clear both). Conservative, pre-registered, and the t >= 2.0 bar is on t_NW as the prompt says. | None. | None. |

## What was checked and found correct

Prompt compliance (STAGE_E.23.md read in full)
- P1.1-P1.3: 208 inventory rows, 34 reader exclusions and the lead's data exclusions are traceable to inventory/*.json and
  the memos. Shortlist of 4 triggers / 5 trigger-holds is within "at most 12 / 24". The lead's added shortlist rule
  (moderate or strong mechanism; data on both windows; multi-day outcome unread; no duplicate mechanism per root; a
  trigger test, not a fixed-side near-continuous book) is written before any read and applied consistently: month-end
  h20 and K4-ngpre-01 dropped by the same "buy-and-hold" rule, H6 kept because its side follows the trigger.
- Drops checked against the memos: K2-aucpre/aucpost (M6 moderate on ZT, ZF): their E.23 book, long from the auction
  day's settlement to t+5, is exactly E16-H3's long leg (base_rules/h3.py docstring: "at the open of bar(T, t, S_T)
  cover and go long ... exit at the open of bar(T, t+5, S_T)"), read in E.17 on 2010-07..2024-02; the drop is correct
  and the prompt itself excludes H3. K8-flight-01 (M3 moderate reversal at 20 days): MES signal leg has no W_ext store;
  correct. K1-vxnband-01 (M11 moderate): VXN table starts 2019-04-30; correct. E16-H4, CP1, E16-H1 (M4 moderate on
  equity): on NQ the same mechanism as H6; elsewhere M4 says "bonds, FX: no effect at one week" and RTY is too short on
  W_ext; not shortlisting them is within the lead's remit. ZT and UB month-end: no published futures-tenor figure (HS19
  Table 8 has 5y/10y/30y); a narrowing, not an error. No moderate or strong trigger with owned data on both windows was
  found wrongly dropped; the weakest kept item is R-06.
- Directions m: month-end +1 = the member's side (BUY), M7 "same side (long)" for the N-1 trigger whose hold contains
  day N (HS19 Table 8 +7/+9/+15 bp, se 1-2); the N trigger's disputed 5-day direction only extends the capped long by
  one day. H6 m = -1 = reversal of sign(r_ROD), M4 (BDLM2021 1-3 days, t -3.16; BvD2019). Both fixed from the memos at
  02:37, before any trigger event was extracted.
- P1.4 and P2.4 data use: W_ext (2011-07-27..2019-04-30) never read any of the four triggers at any hold; W_cf never
  read K2-monthend-01 by a rule (K2's confirmation never ran; E.12/E.20 used the month-end feature inside ML models) and
  read E20H6-T1 once at its intraday hold (E.20, FAIL): tested, not selected. Discovery on W_ext is "owned data" under
  P1.4 (the ideal window, the research window, is barred by P2.4); confirmation declared on W_cf is owned data that
  never selected the triggers. The E.21 drift statement is present in both the shortlist and the prereg. Nothing dated
  2024-03-01 or later, no holdout-2, embargo, research window or MES store is touched: trend files end 2024-02-29
  (ZN/ZT 2024-02-26), events end 2024-02-29, constants pin W_CF_LAST = 2024-02-29, stores are the E.17 manifest's.
- P2.1: entry at the trigger day's settlement mark when tau is strictly before the settlement bar's open (units.py
  `entry_mark_date`), else the next mark date (R7); both triggers decide before settlement (rates 14:00 CT; NQ 15:15 CT
  per reports/stage_e16_settlement.json 2010-06-07 on, 15:00 CT after 2020-10-25), so the trigger day's intraday P&L
  (07:21-14:00 CT month-end; 14:30-15:15 CT H6) is never in the book. Exit at the h-th mark date; cap clip(sum, -1, 1);
  sizing 0.40 / (sigma x notional) with sigma strictly before the change date (E.21 EWMA com 60); D8 base, stress =
  commission + 2 x slippage (R3 = the prompt's "2 x slippage"); rolls, marks and attribution through the frozen E.21
  code. Units spanning the store boundary or a window edge are excluded by calendar, never by price.
- P2.2: regressors = the same root's E.21 T1 and T2 per-root base net values, recomputed by the frozen E.21 code and
  checked against the published sums (check.passed in all 17 files, |diff| <= 1e-12 on 3,205 dates), stated as the
  prompt requires; HAC lags = h; one-sided H1 a > 0.
- P2.3: power from events, calendars and mark existence only (power.py; basis field in power.json). Recomputed every
  row's E[t], power_gate and power_holm1 from n_dates: all agree to 3 decimals (W_ext 1.387/0.270/0.174 at 1,939 dates;
  1.385/0.269/0.173 at 1,934; W_cf 1.077/0.178/0.106 at 1,170; 1.093/0.182/0.109 at 1,204). Non-overlapping events
  71/77/76/374/95 on W_ext (all >= 30); 39/39/39/233/59 on W_cf. Event counts match the events files (137/143/142/1860;
  79/77/79/1147). Every W_cf row inconclusive by design; every W_ext row read.
- P2.4 bars: discovery Holm one-sided 0.05 over K = 5 on p_alpha, t_NW >= 2.0, base Sharpe >= 0.3, at most 4 survivors
  (largest t_NW, ties by Sharpe, then id); confirmation Holm over survivors, t_NW >= 2.0, Sharpe >= 0.3 base and > 0
  stress, DSR > 0.95 at N 538 (run.py passes current_n of the registry after registration), CSCV PBO < 0.5 (8 blocks) on
  the discovery window. All as the prompt fixes them.
- P2.5-P2.6: registry N = 533 (`trial_registry status`, 8 chained lines); E23 ids unused; N -> 538; the register
  command in lead_spec section 8 matches the CLI (`--test --ids --freeze --freeze-sha256 --harness-sha256`); the runner
  refuses without a matching registration (require_registered) and writes the O_EXCL marker before any bar is read,
  after freeze, config, registry, output-free, manifest and store-preflight checks; exit codes 2/0/1 as base_rules.
  Order in prereg section 6 matches P2.6.
- Freeze: `freeze_manifest verify --sha256 3fdd98d7...` returns "freeze verified: 20 inputs, 5 ids", rc 0; the manifest
  pins 108 files with sha256: trigger_hold code, its 4 test files, multiday/, base_rules/, screening/trial_registry.py,
  the 8 events files, the 17 trend files, the calendars, settlement and windows tables, the run manifest, the E.21
  freeze, the spec, the prereg, the config and the power table. Harness v13 dd2bcc60... named in the prereg and config
  path. `pytest -q tests/test_trigger_hold_*.py`: 93 passed (5.1 s, nice 10, 8 GB free).
- No outcome read: no run-once marker and no reports/stage_e23_runs exist; the events and validation files hold only
  d0, tau_ns, side and entry-side counts; BookCoder's only real-bar runs were the trend recomputation (E.21's own
  series) and the T3 reproduction (T3's units, read in E.21; t3_reproduction_final.json records fill counts and the
  sum-vs-published check only); the power dry run used synthetic events at 02:4x, before any real events file existed;
  no Sharpe, alpha or P&L of any trigger unit appears in either coder report, the STATE file or the scratch logs.
- W_cf validation: adapter events identical to the harness for all four triggers (0 differences; frames equal column
  for column for K2; tau equals E.20's entry fill instant on all 1,147 H6 entries). Calendar inputs for 2011-2019 come
  from the program's own tables (hist rates calendar month-end rule equal to pattern_search.backward S6, 190 dates).
  Engine rules not reproduced on W_ext (D9.7 limits, CPI window, event-window costs) are listed with their effect; none
  changes whether a month-end entry happens; a few H6 limit-zone dates are the only uncertainty, disclosed.
- Git: no tracked file modified; HEAD cb07387; REGISTRATION.md 0 bytes; holdout status all_ok.

## Not done
- Line-by-line code review (CodeReviewer-FableXHigh's lens); I read units.py, power.py, book.py `regressor_on`,
  evaluate.py `read_root`/gates and run.py's precondition order only as far as the design claims required.
- The non-overlapping counts were not recomputed independently from the events files (they need the per-root mark
  dates and the roll-blackout action rule, i.e. a store read); the gate arithmetic was recomputed from n_dates.
