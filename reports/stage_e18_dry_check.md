# Stage E.18 Step 3: dry check of C1b's amended C10 (Fable E.17 F-1)

Lead, 2026-10-10. Run 2026-10-10T12:16:02-07:00 .. 2026-10-10T12:16:05-07:00 (4.6 s wall, 373 MB peak, nice 10), exit 0.
Script reports/stage_e18_briefs/dry_check.py; output reports/stage_e18_dry_check.json (sha256 8b98a6281bfcf292413e093ec758fe2c8baa79e419e8aedcb36896abd97b9dbc); log
reports/stage_e18_briefs/dry_check.log. Run after the Step 2 review (11:58-12:14) and its fixes (12:14-12:15), before
the freeze. The expected outcome was written into reports/stage_e18_STATE.md at 12:00:19, before the run.

**Result: PASS.** Every case came out as expected.

## What was checked

- The check: c1_replication.c1b.c10_check (C1b's amended C10) on E.12's frozen reference counts
  (reports/stage_e14_c1_model.json c10_reference, sha256 c6075306ddfd70cb22a2b32f8017ae41ba6050778e6cb66568d00b94585421e6; E.12's 2019-2024 training
  panel), beside C1's frozen evaluate.c10_check as a control.
- The world: SYNTHETIC bars (tests._c1_fixtures.synthetic_leg, ml_route_v2.synthetic, seed 11) for NG and the
  five legs (NQ, ZN, 6E, GC, ZC) over 2010-06-07..2011-09-30, a sub-window of the test window (warm-up plus
  about nine months of rows); CL and MBT as C1's C7 sentinel frames (one bar dated 2019-05-31, after the window), the
  2010-2019 listing state; the pinned official 2010-2019 calendars, release tables and energy full sessions
  (reports/stage_e17_c1_calendar_hashes.json, sha256 d5e48579d2bd70b2e73d7583010e7c7ef61f94cc58fe68b07e7734a12911f6f8), no prices; C12 on the
  sub-window: 0 of 343 candidate dates excluded. The panel is
  E.12's call (c1_replication.world.replication_panel) inside c1_replication.context.hist_tables.
- Then each non-exempt leg in turn replaced by the same sentinel frame (its roll blackout emptied, as for CL and MBT).
- No 2010-2019 bar was read: no store was opened; the counts below are of the synthetic world.
- Code hashed at the run: c1b.py 4f8ce49bf0964ca333115211e016194cf3d76a8e317bf974dc7d1ca0dcf84b1f, evaluate.py 5f22c251095e90f2bb3f72185e79727dfb677e6b602893fe87cb13c8cbe1d381.

## Results

| Case | C1b's check returned | Expected | C1's frozen check (control) | NG ok rows h60 / hF | As expected |
|---|---|---|---|---|---|
| all_legs_present | (none) | (none) | g17_mbt (h60), g17_mbt (hF) | 564 / 564 | yes |
| NQ_removed | g17_nq (h60), g17_nq (hF) | g17_nq (h60), g17_nq (hF) | g17_mbt (h60), g17_nq (h60), g17_mbt (hF), g17_nq (hF) | 564 / 564 | yes |
| ZN_removed | g17_zn (h60), g17_zn (hF) | g17_zn (h60), g17_zn (hF) | g17_mbt (h60), g17_zn (h60), g17_mbt (hF), g17_zn (hF) | 564 / 564 | yes |
| 6E_removed | g17_6e (h60), g17_6e (hF) | g17_6e (h60), g17_6e (hF) | g17_6e (h60), g17_mbt (h60), g17_6e (hF), g17_mbt (hF) | 564 / 564 | yes |
| GC_removed | g17_gc (h60), g17_gc (hF) | g17_gc (h60), g17_gc (hF) | g17_gc (h60), g17_mbt (h60), g17_gc (hF), g17_mbt (hF) | 564 / 564 | yes |
| ZC_removed | g17_zc (h60), g17_zc (hF) | g17_zc (h60), g17_zc (hF) | g17_mbt (h60), g17_zc (h60), g17_mbt (hF), g17_zc (hF) | 564 / 564 | yes |

With every leg present, the 30 features live on NG rows in E.12 apply on these synthetic counts of rows (h60/hF):
cp1_ret 564/564, cp2_brk 564/564, cp2_range 564/564, cp3_clv 564/564, g01_ret30 564/564, g02_ret60 564/564, g03_ret120 564/564, g04_ret_day 564/564, g05_gap 546/546, g06_rv60 564/564, g07_range 564/564, g08_prev_ret 564/564, g09_vol_state 564/564, g10_logvol30 564/564, g11_t_index 564/564, g12_dow 564/564, g13_min_to_rel 564/564, g14_min_since_rel 564/564, g15_rel_day 564/564, g16_month_end 564/564, g17_6e 564/564, g17_gc 564/564, g17_mbt 0/0, g17_nq 564/564, g17_zc 564/564, g17_zn 564/564, k4_ngpre_msince 78/78, k4_ngpre_mto 39/39, k4_ovr_pct 376/376, k4_ovr_ret 376/376. Only g17_mbt is 0 among them; g17_cl is 0 in E.12 and here. The smallest non-exempt count is k4_ngpre_mto
(39/39, the NGS release-time feature).

## Reading

- With the 2010-2019 listing state (MBT and CL absent, every other leg present), C1b's amended check passes, while
  C1's frozen check stops on g17_mbt: the E.17 contradiction is reproduced on synthetic data and removed by the one fix.
- With any one non-exempt leg removed, C1b's check stops on exactly that leg's g17 feature, both horizons: the fix
  does not weaken C10 for any other leg.
- Limits: synthetic bars, so the counts say nothing about the test window; a sub-window, so a feature that applies only
  outside it would not be seen (none of the 28 non-exempt live features is 0 here); the dry check reads the same
  frozen calendars and NGS table as the evaluation.
