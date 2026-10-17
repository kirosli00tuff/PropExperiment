# Stage E.23 BookCoder-OpusXHigh report (2026-10-17, finished 02:45 PDT)

Brief: the generic trigger-hold engine of `trigger_hold/` per reports/stage_e23_briefs/lead_spec.md,
plus the lead's mid-task additions (a) series from the first unit, (b) descriptive alpha3,
(c) in-market fraction. No commit, no registry write, no web. Nothing existing edited.
Holdout status was not run by this worker (lead's invariant).

## Files written

| File | What it does |
|---|---|
| trigger_hold/types.py | STABLE event type `TriggerEvent(d0, tau_ns, side, trigger_id)` and the events-file schema `stage_e23_events/1` (`events_record`, `parse_events`, `load_events`). Rows must hold exactly `d0, tau_ns, side`: a price/P&L key is refused. TriggerCoder's events.py already imports it. |
| trigger_hold/constants.py | Every E.23 parameter (windows, holds, 0.40 target, cases, Holm 0.05, bars 2.0/0.3/4, DSR 0.95, PBO 0.5 / 8 blocks, power 0.5 / 0.2 / 30, verdict labels, paths, schemas, exit codes). E.21 values are imported from multiday.constants. |
| trigger_hold/units.py | Events -> units (spec 1, 2): d_e rule (tau strictly before the open of bar S_i(d0), from the settlement table; else the next mark date), d_e and d_x eligibility via multiday.signals.action_why, d_x = h-th mark date, window/boundary exclusions counted by reason, u = side x m. `BarMarks` (run) and `CalendarMarks` (power, calendar-only). `book_days` (addition a), `in_market_fraction` (addition c). |
| trigger_hold/book.py | `E23VehicleCost` (base = D8 unchanged; stress = commission + 2 x (base - commission) per side), `prepare_root` (multiday.book.process_root + a fill cost for every mark date), `net_path` / `unit_orders` (clip(sum u, -1, 1), orders only when net changes, n = net x 0.40 / sigma / (divisor x V), divisor 1 except the T3 test parameter `divisor_at`), `unit_book` -> multiday.book.simulate_book (reused unchanged), `daily_series`, `book_summary`, `buy_hold_returns` (addition b). |
| trigger_hold/stats.py | Raw t, NW t (newey_west_se, lags h), Sharpe, OLS alpha on v_T1, v_T2 with the Bartlett HAC sandwich (same kernel and normalization as newey_west_se), plain t, p_alpha = max(Student n-3, normal NW), R^2, betas, correlations, per year; `alpha3_descriptive`; Holm (base_rules.stats.holm at 0.05); `discovery_survivors` (spec 7); DSR (base_rules.stats.dsr_at_n; `dsr_with_variance` for confirmation); CSCV PBO (screening.stage_e_verdict.pbo on union-aligned series); `confirmation_hurdle`, `confirmation_verdicts`. |
| trigger_hold/power.py | Spec 5: greedy non-overlapping count, n_dates (book_days), E[t], power_gate, power_holm1, in-market fraction, inconclusive rule; `power_row`. No price. |
| trigger_hold/trend.py | The per-root E.21 T1/T2 base daily nets (frozen E.21 code, E.21 freeze verified first) + the sum check + the T3 reproduction; `load_trend` refuses an unchecked file. |
| trigger_hold/config.py | The registration config schema and loader (below). |
| trigger_hold/evaluate.py | `read_root` (one root at a time, bars dropped before the books), `discovery`, `confirmation`, `confirmation_gate`, `survivors_from` (re-derived by code, must equal the stored list). |
| trigger_hold/run.py | `power` (O_EXCL power table) and `evaluate --phase discovery|confirmation` (preconditions, O_EXCL marker before any bar, exit 2/0/1, STOPPED.json). |
| trigger_hold/freeze_manifest.py | `build` (O_EXCL) / `verify --sha256` of reports/stage_e23_freeze.json: trigger_hold/*.py (TriggerCoder's included), tests, multiday/*.py + README, base_rules/*.py, screening/trial_registry.py, screening/stage_e_verdict.py, every input role, every events file of the config, every trend file. |
| tests/test_trigger_hold_{book,stats,run}.py | 58 tests (23 + 22 + 13). |
| reports/stage_e23_trend_per_root/<ROOT>.json | 17 files, 3.4 MB, schema stage_e23_trend_per_root/1, `v_T1`, `v_T2` (date -> capital units), counters, `check`. |
| reports/stage_e23_briefs/tmp_bookcoder/ | logs, t3_reproduction.json, t3_reproduction_final.json, dry_power.py + dry/ (synthetic-event power dry run), pycache. |

## Tests
`uv run pytest -q -p no:cacheprovider tests/test_trigger_hold_*.py`: 58 passed (4.5 s); ruff clean.
Covered: tau before / at / after bar S (and a 1 ns boundary), a missing mark on d_e, roll blackout
on entry and exit, the h-th mark exit with a missing mark carried (gross = n x (MK(d_x) - MK(d_e))),
m x side, window edges and the store boundary by reason, overlapping units (one trade, extended
hold, sized at the first d_e only), clip and opposite units netting to 0, a flip as one fill of
the difference sized at the flip date, sigma warm-up skip, a hold across a roll paying both legs
(each case), stress = comm + 2 x slippage on every fill and base equal to the frozen D8 cost,
series zero when flat; HAC alpha: intercept-only by hand (0.078125) and == newey_west_se, against
an independent pure-Python sandwich at lags 1/5/20 (statsmodels is NOT installed in the uv env,
so no statsmodels check), p_alpha, rank deficiency; Holm; survivor rule, cap 4, ties; the
confirmation hurdle (S=4: 2.2414) and verdicts; DSR/PBO wiring; power: 1953 -> E[t] 1.392,
gate 0.272; 1215 -> 1.098, 0.183; greedy count; inconclusive; events schema refusals; marker
written before compute, second run exit 2, stop exit 1, refused precondition writes nothing;
config schema; freeze build/verify/tamper; calendar-only power row with additions (a)/(c);
buy-hold returns; a synthetic discovery end to end; the confirmation gate.

## Trend regressors (02:31-02:33 PDT; nice 10; one root at a time; >= 9.6 GB free)
Recomputed (E.21's per_root files hold holdings and fills, not per-root daily series): E.21
freeze 0bb899e5... verified, E.21 context + e21_starts, lock_rule, process_root, t12_orders,
simulate_book. Check: sum over the 17 roots == T1_result.json and T2_result.json series.base on
all 3,205 dates, max |diff| 0.0 (bitwise), 0 per-root values off the series. Written into each
root's file (`check.T1/T2.passed = true`, published sha256 e382770e... / ab73750a...).

## T3 reproduction (the only real-bar run of the unit engine)
T3's own units (tom_units / tom_sigma eligible, u = +1, d_e = day -2, d_x = day +3) through
`unit_book` with `divisor_at` = S_u of the unit's month: NQ 154 units / 308 fills, RTY 73 / 146,
max |diff| vs the frozen t3_orders + simulate_book 0.0 on every date; NQ + RTY == T3_result.json
series.base on 3,319 dates, max |diff| 0.0. Run twice (02:33 and 02:41 with the final code), both
passed (tmp_bookcoder/t3_reproduction*.json).

## Power dry run (real calendars + store metadata, SYNTHETIC events; no price)
tmp_bookcoder/dry_power.py: weekday month-ends at 12:00 CT as fake events for K2-monthend-01 on
ZF/ZN/ZB (m +1, h 5) and E20H6-T1 on NQ (m -1, h 5, 20). The `power` code path handles the four
trigger-roots and five rows. Two findings for the lead (not outcomes; calendar facts):
1. The T3 entry rule's roll blackout excluded 31 of 94 synthetic W_ext month-end entries on each
   Treasury root (18-19 of 58 in W_cf): Treasury roll blackouts sit at quarter month-ends, so a
   month-end trigger loses about a third of its units there.
2. W_cf n_dates is 1,169 (Treasuries, from 2019-06-28) to 1,187 (NQ): power_gate 0.178-0.180
   < 0.2, so EVERY W_cf row is inconclusive by design even before the S-hurdle (b >= 2.0).
   W_ext: 1,932-1,938 dates, gate 0.269-0.270.

## Registration config schema (reports/stage_e23_registration.json, `stage_e23_registration/1`)
```
{"schema": "stage_e23_registration/1", "registry_test": "E23", "n_before": 533,
 "trigger_holds": [
   {"id": "E23-...", "trigger_id": "<events files' trigger_id>", "root": "ZF",
    "m": 1, "h": 5, "s_x": "YYYY-MM-DD" | null,
    "events": {"W_ext": "reports/stage_e23_events/<trigger>_<root>__ext.json",
               "W_cf": "reports/stage_e23_events/<trigger>_<root>__cf.json" | null}}, ...]}
```
Exact row keys; 1-24 rows; unique ids with the "E23-" prefix; root in the E.21 roots; m +-1;
h in {5, 20}; a W_ext file required; each events file must carry the row's trigger_id, root and
window. Power table (`stage_e23_power/1`): `{"k_family", "config", "events_sha256", "rows":
{id: {"W_ext": row, "W_cf": row | null}}}`, row = power.power_row's fields.

Order for the lead: config -> `uv run python -m trigger_hold.run power` -> freeze `build` ->
review -> commit -> register -> `evaluate --phase discovery` -> `--phase confirmation`.

## Questions for the lead (conservative choices made, each a one-line change)
1. Exit eligibility: d_x must also be an eligible action date (T3's exit rule; E.21 coder choice
   2), else the unit is excluded ("excluded: exit: <why>"); the spec only states it for d_e.
2. Entry eligibility is multiday.signals.action_why in full: action exclusion (incl. roll
   blackout, early halt, unsourced), listed, MK and PS present, MK outside guard windows. See
   power finding 1 (month-end Treasury units).
3. Stress per side = commission + 2 x (base - commission), i.e. 2 x the ceil'd D8 slippage cents
   (microbook S6, c1_replication precedent); ceil(2 x ticks x tv) would be up to 1 cent lower.
4. Confirmation DSR: the survivor's W_cf base series, Sharpe variance over the read discovery
   series (the spec names the variance only for discovery).
5. PBO: the K series aligned on the union of their dates, zero off a series' own dates
   (stage_e_verdict.aligned_series precedent); with addition (a) the series start differently.
6. Discovery runs on a context with last = 2019-04-30, so no W_cf mark, sigma or path is computed
   in discovery (the stores still load both eras as E.21 did). Equivalent for W_ext books (no
   unit spans the boundary); confirmation uses the full context so W_cf sigma uses earlier returns.
7. d0 without a settlement minute: entry at the next mark date (never earlier than the event).
8. Holm's m counts every registered trigger-hold (discovery: inconclusive ones with p None;
   confirmation: all S survivors, gated ones with p None).
9. alpha3 used the lead's fallback (per-contract dollar move / notional at the interval's opening
   mark, costs excluded): one long simulate_book hold would be zeroed by any failed interval.
10. In-market fraction: share of book dates d with clip(sum u over d_e < d <= d_x) != 0 (spec 3's
    (d_e, d_x]); calendar-mode units in the power table, bar-mode units in the results.
11. Survivor ties after t_NW and Sharpe: id ascending. Rank-deficient alpha design: undefined.
12. A store-refused root in confirmation is labelled UNCONFIRMABLE ON OWNED DATA.
13. Default paths are mine (config, prereg reports/stage_e23_prereg.md, power table); edit
    constants.py before the freeze if the lead's names differ.

## Not finished / not verified
- No real config, power table or freeze exist yet (they need the lead's config and TriggerCoder's
  events). `evaluate` preconditions are tested with stubs only, not against a real freeze and
  registry; the confirmation computation is covered by unit tests of the gate and verdicts, not by
  a synthetic end-to-end run (discovery has one).
- statsmodels comparison not possible (not installed; no dependency added).
- No independent (Fable) check of any of this.
