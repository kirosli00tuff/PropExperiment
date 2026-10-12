# Stage E.20 Step 5: independent review of the Part C search plan

Reviewer: PlanReviewer-FableXHigh (worker-xhigh on fable). Written 2026-10-11, 16:14 PDT, before
the build, the 45 registrations and any fit. Object: reports/stage_e20_plan.md (DRAFT, 305 lines).
Read against docs/prompts/STAGE_E.20.md (F1, F2, F3, F6, F7, F8, F9, SCOPE, Steps 5-9),
docs/STAGE_E_ML_V2_DESIGN.md V2.2-V2.9, reports/stage_e20_product_summary.md sections 1.3, 1.4
and 2, the five code maps in reports/stage_e20_briefs/codemap_*.md, and the frozen code by section
(ml_route_v2/{pipeline,configs,constants,clock}.py, signals/{k1,k2,k4,k5,ports,_daily,_events,
generic}.py, screening/trial_registry.py, c1_replication/context.py, strategy/members/k2 and k4
module headers, ml_route/inputs.py, rules/sessions.py, base_rules/costs.py). Also read:
reports/stage_e16_windows.json and stage_e16_rulings.md, reports/stage_e12_phase1_bars.json
("roots" -> "s_x"), docs/DECISIONS.md V31, the registry's last line (N fields only). Not read: any
data store, any E.12 Gate 0, E.15, E.17 or E.18 result, the H6 result.

## Verdict

**BLOCK**, on one finding (PR-1). The remaining findings are SHOULD FIX and NOTE. PR-1's fix is
documentary plus one pre-fit check on synthetic frames; once it is in the plan the verdict becomes
APPROVE WITH FIXES.

Why BLOCK rather than APPROVE WITH FIXES: F6 says a feature that would be not-applicable by design in
the backward window is "dropped now, not exempted later". Eleven of the 35 kept features read
module-level literal tables that cover 2019-05 onward only (section PR-1). Whether each is
computable in 2010-2019 depends on a per-feature table swap that the plan does not list and defers
to the Step 8 dry check, after the search. A feature found uncomputable then cannot be removed
without a second search, which SCOPE forbids ("run any evaluation twice") and F9 would count again.

What passed (checked, no finding): the universe and its UNIVERSE keys; E.12's recorded S_X (ZF
2020-10-01, ZT 2021-10-01, 15 roots 2019-05-06; the D4 rule reads the research store's ts_event,
volume and trade_date, so re-running it is forbidden by F2 and S_X is an allowed research-derived
constant under V2.4); the 45-configuration grid, its order (models, then k, then horizon;
CONFIGS[0] ridge_l0.01_k1.5_h60, CONFIGS[44] lgbm_d3_k3_hF) and the LightGBM literals (LGBM_FIXED
matches section 7 exactly); the registry label rule (`_TEST` admits no hyphen; N += len(ids)) and
the N path 483 -> 528 -> 529 (the registry's last line has n_after 483); N_total 528 for the DSR;
the screen's three items as the frozen `_stats`/`_daily_t`/`pbo_cscv` compute them (median of 5
per-path t with zeros on every calendar date; PBO on config_daily, 16 blocks; Sharpe on the
path-averaged series x sqrt(252)); the B1 statistic's form (daily net $, zeros, t, one-sided p at
n_dates - 1, Sharpe, 100 round trips); purge and embargo as frozen and unchanged by t4 (all holds
intraday); the risk table per outer split and inner fold from training rows only, the frozen table
from all six blocks; the admissibility filter one pass, volatility only; the causal normalization
(strictly before d, same-date rows never pooled, t4 joining the vehicle's pool); t4 targets (h120
unavailable by t + h <= F_X; h60's exit at t4 is the bar opening at F_X, the same bar as hF, same
cost minute); rod_ret's definition against F5/F6 and D6's C (c1_close, the G5 pattern, early-halt
rule); rod_absratio's causality (strictly before d); the empty-admissible refusal (the frozen
`adm or None` would remove the filter; refusing is right); MES never loaded and its two store
locations (data/processed/MES confirmation parquet, data/sealed/MES_holdout_v1 and v2) both inside
the guard's refused paths; the leg-rule drops; 35 kept + 32 dropped = 67 = REGISTRY; the
compute arithmetic (1,125 fits = 15 x 5 x 5 models x 3 horizons, k shared; 3,375 scoring passes);
no edit to a hashed file is needed for the composition path described (code maps and the frozen
functions' signatures agree).

## Findings

### PR-1. BLOCKING. Sections 5.1 and 10: eleven kept features need a 2010-2019 table swap the plan does not specify or verify before the fit

What is wrong. The kept features k1_vwap_dist, k2_auction_mto, k2_auction_msince, k2_fomc_mto,
k4_eiafade_move, k4_ngpre_mto, k4_ngpre_msince, k4_ovr_ret, k4_ovr_pct, k5_ovr_ret and k5_ovr_pct
do not read a calendar file at run time. They read module-level literals bound in the frozen
member modules, all covering 2019-05 onward:
- k2.py `_fomc`: `strategy.members.k2._releases.FOMC_STATEMENT_DATES`, placed at FOMC_MIN = 13:00
  CT (a constant from k5/fomc.py's SIGNAL_START_CT + 1);
- k2.py `_auction`: `strategy.members.k2._releases.TREASURY_AUCTIONS` and AUCTION_TENOR;
- k4.py `_eiafade`: `eiafade.make_mcl().wpsr`, where WPSR is a dataclass default bound at import
  (eiafade.py:81: "the frozen table; a test may pass another");
- k4.py `_ngpre`: `ngpre.make_ng().ngs`, the same pattern (NGS);
- k1.py `_full_sessions`: `strategy.members.k1._calendar.EQUITY_FULL_SESSIONS`; rows off that list
  are excluded, so an empty 2010-2019 list makes k1_vwap_dist not applicable on every backward row;
- k4/k5 `ovr_frames`: the k4 and k5 `ovr` modules' full-session lists and reference dates.

Under `fixed_clock` (_events.py:45-69) a date absent from the event list gives flag 0 on both
sides, so without a swap every one of these features is not applicable on every 2010-2019 row:
the exact state F6 bans. C1's `c1_replication.context.hist_tables` swaps module attributes by
setattr (no edit), but its PATCHES cover only what NG rows read: the group calendars,
rules.sessions' holidays and leads, `ngpre.make_ng`, and k4's ENERGY_FULL_SESSIONS. Its docstring
says the K1-K3 and K5-K9 member tables and K4's WPSR table are "not swapped". The plan's section 10
says "swapped in ... as C1 did", which therefore covers the clock and k4_ngpre only.

Section 5.1's rule ("a table that a frozen rule derives from a calendar existing over both windows
counts as existing; the B1 dry check must show it computes") defers the determination to Step 8.
F6 requires it now.

Why it matters. If the swap is missing or does not reach the frozen read path for one feature, the
search runs with a feature that is live in 2019-2024 and dead in 2010-2019. That is the by-design
inapplicability F6 forbids, it cannot be repaired after the fit, and a B1 verdict would then rest
on a model whose backward inputs differ from its training inputs by construction.

Recommended fix (before the search freeze; no bar is read):
1. Add to section 10 a table: frozen module attribute -> 2010-2019 source (file path, sha256,
   schema) -> swap mechanism, for every one of the eleven features. Where the table is a dataclass
   default bound at import (eiafade's WPSR, ngpre's NGS), swap the factory (`make_mcl`, `make_ng`),
   as C1 did for NG. Where the read is an import inside the function (`_fomc`, `_auction`,
   `_full_sessions`), a module-attribute swap reaches it.
2. Name the sources now: EC-AUC 2010-2019 (base_rules/auctions.py; E.16 R-C4), the hist NGS table
   (C1), the base_rules release rows for FOMC, the hist group calendars under
   data/calendars/hist2010/ for the full-session lists. The 2010-2019 WPSR table in eiafade's
   schema (day, time, weekday, standard) was not found by name in this review; if it does not
   exist, k4_eiafade_move is dropped now.
3. Run a sentinel-frame dry check of the 35 features under the swapped tables at Step 6, before the
   search freeze (F8's dry check, moved forward for the feature cut; the B1 dry check at Step 8
   repeats it with the frozen model). Any feature that does not compute, or computes as
   not-applicable on every sentinel row, is dropped from the KEPT list before the freeze.
4. Record the final KEPT list and the swap table in reports/stage_e20_search_freeze.json.

### PR-2. SHOULD FIX. Section 5.1: k2_fomc_mto is not-applicable by design for about a third of the backward window; drop it

What is wrong. k2's FOMC event minute is the constant 13:00 CT. FOMC statements before 2013-03-20
were released at 12:15 or 13:15 CT (the product summary's own finding). A 2010-2019
FOMC_STATEMENT_DATES list either excludes those dates (the feature is then blind to every FOMC day
from 2010-07 to 2013-03, flag 0 on days the forward window would flag) or includes them (the event
is then placed 45 or 15 minutes from its true time, so at t3 = 12:50 the feature says "10 minutes
to the statement" on days the statement is already out). Neither is a data-driven row loss; the
product summary lists it under "partial row loss" but no row is lost, the feature silently changes
meaning. The plan's 5.1 omits it from its own partial-loss list.

Why it matters. F6's ban is on exactly this: a feature applicable in 2019-2024 and not applicable
by design in part of 2010-2019. A kept feature that fires on 2013-2019 FOMC days only also makes
the backward FOMC-day behaviour unrepresentative of the fitted one.

Recommended fix. Drop k2_fomc_mto now (34 frozen signals + 2 = 36 features), with this reason
logged as F6 requires. The decision is the lead's; this review sees no reading of F6 under which
it stays. The partial-row-loss class proper (PR-15) is a different case and is consistent with F6.

### PR-3. SHOULD FIX. Section 9 item 3: the above-4.0 rule contradicts itself

What is wrong. Item 3 says Sharpe "must be >= 0.5 and <= 4.0" and "Above 4.0: the result is held
and FableLeakageAudit runs before any freeze"; the next paragraph says "the screen passes iff 1, 2
and 3 hold" and "a failed screen ends Part C: no freeze". Read literally, a Sharpe above 4.0 fails
item 3, ends Part C, and there is no freeze for the audit to precede. F7's wording ("<= 4.0 (above
4.0 is a leakage alarm: hold the result and run an independent Fable leakage audit first)") admits
both readings: (a) above 4.0 fails, and the audit's purpose is to find the leak for the record;
(b) above 4.0 holds the result, and a clean audit lets the screen pass.

Why it matters. Which reading applies must be fixed before the fit; choosing it after seeing the
Sharpe is a post-hoc selection rule. It is pre-registration content and the lead's decision.

Recommended fix. State the rule in section 9 now: what the audit covers (at least the V2.9 controls
rerun on the real panel, the composition path of PR-4, and the r_ROD and t4 paths), and whether a
clean audit converts the hold into a pass or the result stays a fail with a logged alarm.

### PR-4. SHOULD FIX. Section 6: the composed panel builder must re-apply the frozen checks it bypasses

What is wrong. pattern_search replicates `pipeline.build_world_panel` (to inject t4 rows) and
calls `data.stage_e_bars.load_confirmation_leg` per root (to avoid `phase1_world`'s D4 rule, which
reads the research store). Both steps bypass checks the frozen path applies:
- `build_world_panel(check_grid=True)` calls `assert_bars_on_session_grid(world.bars)`
  (pipeline.py:237-257), the V2.9 "product shifted by one minute" guard. The plan does not name
  it. check_grid is about bars, not the clock, so t4 is no reason to skip it.
- `build_world_panel` also applies `assert_window(out, "train")`, the calendar cut (rows outside
  world.calendar dropped and counted) and the empty-panel refusal.
- `phase1_world`'s per-root steps after the loader: `refuse_late` (ts_event or trade_date >=
  2024-03-01), the degraded-day record, `closure_counts`, `compact_bars`, the empty-calendar
  refusal.
- For the two appended features, build_panel's masking, NaN-drop and `avail_max <= decision_ts`
  check do not apply (codemap_clock Q2); the plan says the caller applies them (5.2), which is
  right, and should add `signals.assert_causal` on the rod frames (the feature-timestamp validator
  of V2.9) so the same validator checks them.

Why it matters. These are the frozen leakage and window controls. The brief's question "does
anything bypass a frozen check that run_pipeline would have applied?" has the answer yes for the
grid guard unless the plan says otherwise.

Recommended fix. List in section 6 every frozen check the composed builder re-applies, by function
name: assert_bars_on_session_grid, refuse_late (or the guard's equivalent), assert_window, the
calendar cut, the empty-panel refusal, assert_causal on the rod frames, and the three build_panel
rules applied to the rod columns. Section 13's tests then plant a shifted root and show the
composed builder raises.

### PR-5. SHOULD FIX. Section 10: say what "V2.7 and V2.8 as frozen" means for B1, and add F2's price-limit convention

What is wrong, part 1. The plan evaluates B1 with the fixed-D `score_split` construction (D held
at $2,000, no engine). That is the construction behind the screen's nested record
(codemap_sizing Q2: the nested OOS series is the fixed-D fast path, not the engine), and V2.9's own
text describes it as "built with V2.7 and V2.8: D is held at the MLL". F8's "its daily t computed
as V2.9 computes the screen's daily t" supports the same reading. The other reading of "V2.7 and
V2.8 as frozen" is the engine run V2.9 prescribes for the research-window test (path-dependent D,
kill switches, the MLL audit, D9.5a fills, the CPI window, D9.7 price-limit locks). The plan
chooses the first without saying it is a choice or what it excludes.

What is wrong, part 2. F2 requires "the E.16 rulings' conventions for sessions, closures and price
limits". E.16 F-07's convention: the engine's limit-lock test applies only where a limit table
exists (2019-05 on); before that, single-price fill bars are reported as a diagnostic. Section 10
says nothing about price limits, and the fixed-D construction has no limit rule at all (V2.5:
limits "act through the engine at evaluation and are not modelled in the targets").

Why it matters. FreezeReviewer and VerdictVerifier must recompute B1 from one definition. Grains
and livestock, 5 of the 17 roots, had locked-limit days in 2010-2019; a fill priced at a locked
bar's open is a fill that could not have happened.

Recommended fix. In section 10 (and the B1 prereg): state that B1 is evaluated with the frozen
score_split construction, name the mechanics it excludes, and give the reason (the same
construction as the screen's record; no real-data engine path exists in the frozen code). Add the
F-07 convention: count and report entries and exits whose fill bar is a single-price bar before
2019-05-01, as E.16 did, and state whether any such trade is excluded from the statistic (a
decision to make now). The decision between the two readings is the lead's.

### PR-6. SHOULD FIX (low). Section 9: the ruin probability's deferral is decided after the screen

What is wrong. F7 lists the ruin probability (V2.9 criterion 7) among the reported items on the
nested record. The plan computes it only on a passed screen, through "a real-data engine adapter
built by composition", and reports "not computed" on a fail. The reason given is sound (criterion 7
reads engine trade records with adverse excursions; Phase1World has no engine frames; codemap_sizing
Q3). But building the adapter after the screen means new evaluation code is written after the
result is known, even though the figure is non-gating.

Recommended fix. Either build the adapter in Step 6 with its tests, so the figure is reported in
both outcomes, or state in section 9 that it is not computable without new code and will be
reported as "not computed" on a fail and computed on a pass, with the adapter written before the
B1 freeze and hashed by it. Either is acceptable if fixed now.

### PR-7. SHOULD FIX (low). Section 5.3: write the acceptance rule as it was applied

What is wrong. Rule (c) says "expected gross per trade from the published evidence is at least
1.5 x the root's D8 round trip". As applied: ZF's zf_auc10y is rejected "at post-2014 strength"
(0.76) although its full-sample figure (1.53) clears 1.5; RTY's fomc_r1 is rejected because its
figure (2.51) is for another instrument and hold (SPY 15:30-16:00 ET, 1993-2013) and for a sample
ending 2013. Both rejections are defensible and consistent with V31 (the pass multiple is V2.7's
loosest hurdle, so 1.5 is right), but the written rule does not contain the refinements used: the
most recent published subsample governs when decay is documented, and the figure must be for the
instrument class and hold the feature would serve. RTY's second ground, (d) "a conditional of
cp1_ret", is weak: with k9_anncday dropped and k2_fomc_mto rates-only, no FOMC-day indicator exists
on equity rows, so the library cannot express that conditional; (c) alone carries the rejection.

Causality of the seven proposals, as far as checked (RTY, ZF, and the summary rows of the rest):
each is a function of a calendar known in advance and of bars closed by its decision time. None
is accepted, so no consequence follows for the search.

Recommended fix. Rewrite 5.3 (c) to include the subsample and same-instrument-and-hold conditions,
and drop or qualify RTY's (d).

### PR-8. NOTE. Section 2: the backward start and end dates differ from F2's shorthand; say why

The plan starts RTY at 2017-07-10 and TN at 2016-01-11 (E.16 R-S4, the sourced listings), while
reports/stage_e16_windows.json gives window_start_on_or_after 2017-06-01 and 2016-01-01 and F2's
parenthetical says "RTY 2017-06, TN 2016-01". The later date is the conservative one and R-S4 is
one of the E.16 conventions F2 invokes; state "the later of the json start and R-S4's listing
date". LE: the json starts 2010-07-01 and the plan excludes 2010-06-07..2014-12-14 by R-S3, as F2
says. End: the plan uses 2019-04-30 ("its store's last date"); F2 says 2019-05-05. E.16's chunk
naming ("chunks_2010_to_2019_04") supports 2019-04-30; this review did not verify it against a
store. State that 2019-05-01..03 are outside the stores and not in the B1 calendar.

### PR-9. NOTE. Section 4: two structural properties of t4 worth recording

- Under an hF configuration a t3 position is open until F, so t4 is skipped (one open position per
  product) whenever t3 traded; under h120, likewise for groups where t3 + 120 min > t4 (equity
  13:00 + 120 = 15:00 > 14:08; grains 11:00 + 120 = 13:00 > 12:18). t4 therefore trades only on
  dates when no earlier decision of that product traded. This shapes F7's "share of P&L from t4
  rows" and should be said when that share is read.
- For energy (C 13:30), rates and FX (C 14:00) and gold (C 12:30), t4 = 14:08 is after D6's C, so
  the t4 hold is post-settlement and rod_ret at t4 spans past the same day's close. H6's
  late-session reading of a t4 signal applies to equity, grains and livestock only. Not a defect
  (F6 fixes t4 = F_X - 60 for every group); record it.
- The four-entries-per-product consequence is correctly recorded; MAX_ENTRIES_PER_PRODUCT_DAY = 3
  is read by no v2 module (confirmed), and the daily variance budget still binds.

### PR-10. NOTE. Section 3: where the guard's primary refusal sits, and three edge cases

- `sys.addaudithook` sees Python-level opens only; pyarrow opens parquet files natively. The plan
  says "for Python-level opens", which is accurate, so the primary refusal must be on every path
  handed to any loader (wrap `load_confirmation_leg` / `read_leg` and any direct parquet read).
  Say so.
- GUARDRAILS require the backward stores' sha256 to be checked at start "by hash only". Hashing
  reads the bytes. State that this runs outside the guarded process (shell sha256sum) or through a
  hash-only exemption that decodes nothing.
- The run-once marker: write it before the first processed_hist open, and refuse when a marker
  already exists from another process (the plan's "written by that same process" implies this;
  make the ordering explicit).
- Calling `phase1_world` would read the research store (D4 rule) and the MES parquet; the
  data/processed/ refusal blocks both, which is a useful second line. The guard cannot cover
  report files (E.15, E.17, E.18 results); that stays a process rule under SCOPE.

### PR-11. NOTE. Sections 8 and 9: three small definitions

- "PBO undefined or degenerate counts as not < 0.5": define it by `pbo_cscv`'s own `degenerate`
  field and a NaN result (the frozen `_stats` records NaN when pbo_cscv raises).
- The fourth screen condition ("final_selection returns a configuration") is V2.9's rule ("if none
  is eligible for the final model, the route has no model, and that is a fail"), not an addition;
  cite it so it is not read as one.
- The DSR's N: `_stats(nested, ledger, n_program=483)` gives ledger.n_total = 483 + 45 = 528, the
  same as `dsr_at_n(daily, 528, var)`. Name the call used.

### PR-12. NOTE. Section 10: make the normalization state and the frozen tables explicit

- Say that every trailing quantity (z-score means and sds, sigma_X,d, the G6/G10 baselines, G9's
  120-date median, rod_absratio's 60-date median) is recomputed from the backward window's own
  earlier dates, that no 2019-2024 statistic is carried, and that the first roughly 180 trade dates
  per vehicle are warm-up and lost. F8's "normalization state" is then the rule, its constants and
  this statement.
- Say which 2019-2024 objects are carried by F8's design: the model payload, the risk table from
  all six blocks (sigma(p,h), L(p,h)), the admissible pairs, k, the D8 cost table. Applying a
  2019-2024 risk table to 2010-2019 trades is a look-ahead in sizing only, mandated by F8; record
  it as such.
- The D6 (O, C) table stays the frozen 2019 one in B1 (C1's choice; "date-independent"), while the
  clock's O_X and F_X come from the swapped hist calendars and rules.sessions. The declared row
  losses (rates before 2011-10-03, grains before 2012-05-21, livestock eras) follow from that mix.
  F_X comes from REGULAR_FLATTEN_CT (a constant) and the swapped early-close rows, so the grains
  2012-05-21..2013-04-05 era (session to 14:00) is kept with F = 13:18; the dry check should
  confirm it and the livestock 08:00/09:05 era.

### PR-13. NOTE. Sections 11 and 15: when the first search-window bar is read

The plan header says it was written "before any search-window bar is read for this stage"; F9 says
the 45 are registered "before any fit". State in section 15 whether the real 17-root panel is
built before or after the registration line, and that in either case no filter statistic, fit or
score is computed before it. Building the panel after registration is the cleaner order and costs
nothing.

### PR-14. NOTE. Section 13: two gaps the leakage code map shows

- No prediction-level perturbation test exists in the frozen suite (feature level only), and the
  synthetic edge plant (synthetic.py:282) stays on t1-t3, so a planted-edge canary at t4 needs a
  pattern_search-side plant on a copy of the synthetic bars. Add it or declare its absence.
- Include the cross-date target-shuffle null on the composed 17-root, t4, 37-feature panel (the
  frozen canary uses a 3-time, 3-vehicle panel), and `assert_causal` on the rod frames.

### PR-15. NOTE. Section 5.1: the partial-row-loss class is consistent with F6; declare its size now

cp1_ret on rates before 2011-10-03, cp1/cp2 and G4/G5/G7 on grains before 2012-05-21: the input
bar does not exist, the ports are ALWAYS_APPLICABLE, and a missing value drops the row. In the
code's vocabulary that is "missing", never "not applicable", so no flag-0 state reaches the model
and F6's ban does not apply. The cost is whole eras of whole groups (about 15 months of six rates
vehicles; about 22 months of three grain vehicles). State the expected share per root from the
calendars before B1 and have the dry check reproduce it. k2_fomc_mto is not in this class (PR-2).

## Items checked against the brief, by number

1. Leakage paths: normalization, risk table, purge and embargo, admissibility, r_ROD, t4: no
   leakage path found; the composition path bypasses the grid guard unless re-applied (PR-4).
2. Feature cut: KEPT computability depends on the swap list (PR-1); k2_fomc_mto fails F6 (PR-2);
   every DROPPED reason checked and right; g13-g15 and k9_anncday rightly dropped (the 2010-2019
   release calendars lack most types; a pooled release column cannot be made product-specific
   without an edit); the partial-row-loss class is consistent with F6 (PR-15).
3. Part A: none accepted; each rejection stands; the written rule lags the applied one (PR-7).
4. Guard: every path class named is covered (processed_hist, sealed, holdout from data/holdout.py,
   data/processed including MES, other roots, the date bound, the B1-only exception with its two
   conditions); PR-10 for where the primary refusal sits and the hash-only start check.
5. Screen and bar: F7 items 1-3 and the reported items match; the above-4.0 rule is ambiguous
   (PR-3); the ruin probability's deferral (PR-6); F8's statistic and bar match; the fixed-D
   reading and the price-limit convention (PR-5).
6. Other choices: S_X, MES, the entries cap, the 45 ids, N accounting, the empty-admissible
   refusal, the new directories, no v2 amendment: all consistent (PR-8, PR-9, PR-11, PR-13 notes).
7. Nothing in the plan adds a configuration, horizon, feature, model or test beyond F5 and F6, and
   nothing requires a change to a file hashed by harness v12, the v2 freeze, or the E.14, E.16 or
   E.18 freezes. The tightening rules (empty-admissible refusal, PBO-degenerate-fails) are
   conservative and not additions.

## Not checked

- The pattern_search package (not yet written); this review is of the plan and the frozen code.
- The verbatim source quotes behind the seven Part A proposals, beyond the RTY and ZF entries.
- Whether a 2010-2019 WPSR table in eiafade's schema exists on disk (PR-1 item 2).
- The hist stores' last date (2019-04-30), taken from E.16's chunk naming, not from a store.
- The H6 result and any E.12 Gate 0, E.15, E.17 or E.18 result (excluded by the brief).

## Recheck (2026-10-11 16:46 PDT), after the lead's revisions (reports/stage_e20_rulings.md section 4)

Read: the revised reports/stage_e20_plan.md (413 lines; sections 2-6, 9, 10, 10.1, 13, 15),
reports/stage_e20_briefs/backward_swap_table.md (S1-S13, feature verdicts, Task 2, open items),
the rulings table, E.16 R-B1 and F-09, and screening/stage_e_engine.py session_end_bar. No data
store, no H6 result, no E.15/E.17/E.18 result.

**Verdict after recheck: APPROVE WITH FIXES.** The BLOCK on PR-1 is lifted. Every SHOULD FIX is
FIXED. The revisions introduce no leakage path and no F7/F8 departure. One new SHOULD FIX (low,
PR-16) and two NOTEs (PR-17, PR-18) concern rulings 2-4 in section 10.1; none requires a change
to a kept feature or to the screen.

### Per-finding verdicts

| Finding | Verdict | Basis |
|---|---|---|
| PR-1 | FIXED, as far as can be judged before the Step 6 dry check | Section 10.1 and the swap table give, for every 2019-on literal, constant or factory a KEPT feature, the clock or the cost path reads, the 2010-2019 source with sha256 and schema, the swap mechanism (setattr, or a factory swap for eiafade.make_mcl and ngpre.make_ng, where the table is a dataclass default bound at import) and a verdict; each derived table (S4 equity full sessions, S5 auctions, S6 month ends, S7 WPSR in eiafade's schema, S10 metals full sessions) is built by the frozen generator's own rule and reproduces the frozen table on the 2019-05 overlap; no feature is NO-SOURCE. The table also found S6 (k2_monthend_msince reads strategy.members.k2.monthend.EVENT_DATES, a 2019-on literal), which my list of eleven missed; it is covered. Section 5.1 now says the Step 6 sentinel dry check must show every KEPT feature computes and is applicable on its event rows under the swapped tables before the search freeze, and that a failing feature is dropped with its reason; section 13 specifies the check; section 15 places it before the freeze manifest. That is F6's "dropped now". What remains is the check itself, which the plan makes binding. |
| PR-2 | FIXED | k2_fomc_mto dropped with the reason logged (5.1, DROPPED 33); KEPT 34, 36 features; counts verified (34 + 33 = 67). |
| PR-3 | FIXED (reading (a)) | Section 9 item 3: above 4.0 fails item 3, Part C ends, the audit runs for the record with its scope named, a clean audit does not convert the fail. Decided before the fit. |
| PR-4 | FIXED | Section 6 names assert_bars_on_session_grid, refuse_late (or the guard's equivalent) with the degraded-day record, closure_counts and compact_bars, assert_window, the calendar cut, the empty-panel refusal, build_panel's three rules on the rod columns and signals.assert_causal on the rod frames; section 13 plants a shifted root. |
| PR-5 | FIXED | Section 10 "Construction": the fixed-D score_split construction declared as the lead's reading of F8 with the reason, the excluded engine mechanics named, E.16 F-07's single-price-bar diagnostic counted per product and kept in the statistic (decided now). |
| PR-6 | FIXED | Section 9: not computed on a fail with the reason; on a pass the adapter is written, tested and hashed by the B1 freeze before the B1 registration. Decided now. |
| PR-7 | FIXED | 5.3 (c) carries the instrument-and-hold and governing-subsample conditions; RTY's (d) withdrawn; ZF's subsample stated. |
| PR-8 | FIXED | Section 2: the later of the json start and R-S4; end 2019-04-30 with 2019-05-01..05 outside the stores. |
| PR-9 | FIXED | Section 4 "Structure" paragraph. |
| PR-10 | FIXED | Section 3: wrapped loaders as the primary refusal; hashing in a separate shell process (checks.sh); O_EXCL marker before the first processed_hist open; an existing marker refuses. |
| PR-11 | FIXED | Section 9: PBO degenerate, NaN or raise; V2.9's no-model rule cited; dsr_at_n with 528 = 483 + 45. |
| PR-12 | FIXED | Section 10 "Carried from 2019-2024" paragraph: carried objects and recomputed trailing quantities named; the frozen D6 table and the swapped O_X/F_X stated. |
| PR-13 | FIXED | Sections 6 and 15: the real panel only after the 45 registrations; no filter statistic, fit or score before the registry line. |
| PR-14 | FIXED | Section 13: a pattern_search-side t4 planted-edge canary, the composed-panel cross-date shuffle null, assert_causal on the rod frames. |
| PR-15 | FIXED | Section 10.1's declared row-loss table, from calendars only, with the dry check and B1 to reproduce it. |

### Rulings 1-7 in section 10.1, checked for new issues

- Ruling 1 (metals sub-group map copied in memory; livestock calendar wired into the loader and
  flatten tables): composition, no edit, no leakage. ACCEPTED-AS-RULED.
- Ruling 2 (LE 08:00 era: a backward decision row whose decision time precedes the availability of
  an always-applicable feature is excluded and counted): calendar-driven, non-directional, backward
  only (in the search window t1 = O + 30 is never before the ports' availability, so the rule never
  fires there), and it prevents the flag-0 state F6 bans and the CausalityError the frozen
  assert_causal would raise. ACCEPTED-AS-RULED; see PR-18 for its verification.
- Ruling 3 (grains hF and t4-h60 exit on 1,031 backward dates whose F_X = 13:18 bar does not exist:
  the close of the last bar before the session close, priced with that bar's bucket, E.16 R-B1):
  R-B1's exit clause is "the frozen engine's own fill for a position at a closure"
  (stage_e_engine.session_end_bar: the last bar before the current minute), and F-09's "stated
  departure" concerns R-B1(b), the entry after a closure, which the ML route never makes. The
  description is accurate. The exit is known after the decision, so no leakage; it is non-directional
  and declared before the fit; the alternative (the frozen build_targets yields NaN and drops the
  row from hF) would remove 46% of grain dates from hF. ACCEPTED-AS-RULED; see PR-17 for its
  mechanism and reporting.
- Ruling 4 (release types with no 2010-2019 rows: E.16's cost fallback at the type's frozen release
  minutes on every backward trade date; no deferral and no release-window refusal for those
  types): cost-side conservative and E.16's convention under F2; the omitted deferral and refusal
  are disclosed as the non-conservative element. ACCEPTED-AS-RULED; see PR-16 for its size.
- Rulings 5-7 (WPSR 2012-11-01 excluded for MCL; hist-calendar unsourced dates excluded; cross-tenor
  labelling recorded): consistent with C1's C12, E.16 R-C3 and the frozen E.2b convention (the same
  convention applies in 2019-2024, so both windows are treated alike). ACCEPTED-AS-RULED.

### New findings

#### PR-16. SHOULD FIX (low). Section 10.1 ruling 4: quantify the daily fallback's reach before the freeze

What it does. By the swap table's S11 list and the frozen release minutes (NFP and CPI 07:30 CT,
ISM Services 09:00 CT, WASDE and Crop Production 11:00 CT, G17 08:15 CT), the fallback window
[m, m + 30) contains a decision time's entry minute for most of the universe: rates t1 (07:50;
NFP for ZT, ZF, TN, UB, and NFP or ISM for ZN, ZB), 6E and MGC t1 (07:50; NFP, CPI), NQ and RTY t1
(09:00; ISM), and grains and livestock t3 (11:00; WASDE, Crop Production). In the search window
the event-window cost applies on actual release dates (roughly 12 to 24 a year per type); in B1 it
applies to every t1 entry of 10 vehicles and every t3 entry of 5 vehicles on every trade date.

Why it matters. Not a leakage and conservative on cost, but a structural cost difference between
the two windows that the cost gate will turn into a different trade set at t1 and t3 in B1, which
lowers B1's power against the same model. The lead should know its size before the freeze, and
the FreezeReviewer and VerdictVerifier should read it from the plan rather than discover it.

Recommended fix. From calendars and the frozen release minutes alone (no bar), add to 10.1 a table
of (vehicle, decision time) pairs whose entry minute lies in a fallback window, with the share of
backward entries affected per vehicle (100% of t1 for the ten, 100% of t3 for the five, if the
reading above is right), and the statement that the search window charges this cost on release
dates only. Report the share of B1 trades that paid the fallback cost beside the result. Whether
F2's "E.16 conventions" requires the daily fallback for the ML route, or whether a published
schedule for a type is admissible as a 2010-2019 source, is the lead's decision and is not
re-opened here.

#### PR-17. NOTE. Section 10.1 ruling 3: the substituted exit lives outside the frozen targets code

The frozen build_targets gives y_gross_hF NaN where the F_X bar is absent, so the R-B1 exit on the
1,031 grain dates is a pattern_search post-step on the targets frame (y_gross_hF, cost columns,
exit_ts_ns for hF and for t4's h60). State that in 10.1, add a hand-computed test for it in section
13, and report the hF and t4-h60 P&L on those dates separately in B1's descriptive output so the
substituted-fill share is visible. The purge reads exit_ts_ns, so the substituted exit must be
written there too.

#### PR-18. NOTE. Section 10.1 ruling 2: verify the "only LE t1" claim by count

The rule is generic (any always-applicable feature available after the decision time). The dry
check should report the excluded rows per root and t_index, so the calendar claim (only LE's t1 on
296 dates) is confirmed rather than assumed, and the B1 result should carry the same count.

### Process note

The rulings record that SearchCoder started at 16:21, before the PR-1 table existed, to build the
parts the plan had already fixed, and that no fit happens before this recheck and the Step 6 dry
check. The plan's sections 13 and 15 say the same. No finding.
