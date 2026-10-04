# Stage E.13 Task 4: backward NG replication, draft pre-registration (NOT frozen)

Drafted 2026-10-03 by ReplicationDesigner-OpusXHigh (worker-xhigh, opus). Status: draft for the lead's rulings.
Nothing was run, bought, quoted or frozen. No market-data file of any window was opened. No Gate 0 value
beyond what reports/E.12_RETURN.md prints was read (only the key names of reports/stage_e12_gate0.json, and
the file names and counts of E.12's persisted state). Web evidence: reports/stage_e13_briefs/pages/
ReplicationDesigner/ (fetch_log.md, ids R01-R20). Code claims cite file:line in this repository at commit
5d85924.

Provisional lead rulings L4-1 to L4-7 are followed. Where the code showed a ruling needs a detail or an
amendment, the item is in section 10 (choices) for the lead.

---

## 1. Hypothesis and the two tests

**Hypothesis (fixed by the stage prompt, docs/prompts/STAGE_E.13.md:224-227):** the Gate 0 family B result
for NG at h60 (and hF, as the second of exactly two tests) reflects an edge that also holds on
2010-01-04..2019-05-03 NG data, a period no part of the program has read.

What E.12 observed (reports/E.12_RETURN.md:548-549): NG h60 mean gross 5.569 ticks, c 1.713, 3.25c, t_B 2.51,
p 6.20e-03, 518 trades, Holm rank 1 of 273, not rejected; NG hF 13.921 ticks, c 1.766, 7.88c, t_B 2.33,
p 1.03e-02, 494 trades.

**The two tests** (and only these; NG h120 is not tested although it also cleared 1.5c, E.12_RETURN.md:557):
- T1 = NG h60, the frozen family B model M1_h60, threshold q_h60.
- T2 = NG hF, the frozen family B model M1_hF, threshold q_hF.

The usable window is shorter than the hypothesis text: Databento's GLBX.MDP3 starts on 2010-06-06 (section
5), so 2010-01-04..2010-06-04 cannot be bought. The tested window is the first trade date the data and the
warm-up allow, through 2019-05-03 (L4-4).

## 2. Model and the model rule (L4-1)

**Model M1:** for each horizon h in {h60, hF}, one ridge at lambda 0.1 on every feature column of the E.12
phase-1 panel (z-scores, variable applicability flags, the 28 product and 7 cluster one-hots), pooled over all
81 admissible pairs' ok rows at h, fitted ONCE on the whole E.12 training panel (no CPCV), then applied
unchanged to NG rows of the replication window.

How the frozen code does it, with no modification:
- The training rows are exactly Gate 0's: `cpcv.horizon_data(panel, h, admissible)` (ml_route_v2/cpcv.py:324-348),
  the same call Gate 0's `_oof` makes (ml_route_v2/gate0.py:272).
- The fit is `models.fit_model(configs.ridge_spec(0.1), X, y)` (ml_route_v2/models.py:125-139;
  ml_route_v2/configs.py:87-90): X and y centred on the training rows, unpenalized intercept, alpha = lambda x
  n_train (ml_route_v2/models.py:3-4, 92-104). Prediction is `models.predict` (ml_route_v2/models.py:141-156).
- The E.12 panel is persisted: `~/.cache/propexp_e12_phase1/stages/phase1_panel.pkl` (103 MB) and
  `phase1_filter.pkl` (the admissible pairs), read by `phase1.build.load_build` (ml_route_v2/phase1/build.py:221-233;
  state dir fixed at ml_route_v2/phase1/cli.py:39).

**Which of (a) / (b) holds: neither, on the code evidence. M1 applies.**
- (a) "the frozen code cannot fit M1 on the E.12 stores without modification": does NOT hold. The three calls
  above fit M1 from the persisted build; only a new driver script is needed (a new file, hashed at the next
  freeze). One hard constraint: `load_build` and Gate 0's state refuse a changed constants fingerprint (sha256
  of ml_route_v2/constants.py's bytes and public values: ml_route_v2/fingerprint.py:11-14, 31-39;
  ml_route_v2/phase1/build.py:227-233; ml_route_v2/gate0.py:255-263). So ml_route_v2/constants.py must stay
  byte-identical; every replication constant (window, D4 amendment, q) goes in a new module.
- (b) "a feature live on NG rows cannot be computed for 2010-2019 from purchasable data and official
  calendars": does NOT hold in principle. Every live feature (section 3) reads NG's bars, one of five legs
  priced in E.12's 2010 quote (NQ, ZN, 6E, GC, ZC), or a calendar of scheduled events (CME session and holiday
  calendars, EIA's storage and petroleum release schedules, the FOMC calendar). Open risk, not verified here:
  whether the 2010-2019 CME calendars can be sourced at the program's evidence grade (E.2a read CME's files
  through Wayback captures, data/calendars/energy.py:12-25). If the energy calendar or NG's release list cannot
  be built, M2 does not rescue the test: M2 needs the same energy calendar, NGS table and release calendar. Only
  a failure confined to a leg's group calendar (equity, rates, FX, metals, grains) would make (b) hold and
  trigger M2 under L4-1.
- If M2 ever applies, it tests a weaker, different hypothesis (an NG-only ridge on NG's own-path features was
  never a Gate 0 test), and its threshold would need new out-of-fold predictions on NG's E.12 training rows,
  a new CPCV computation on the 2019-2024 stores, which V24 (docs/DECISIONS.md:446-467) likely rules out.

## 3. Features live on NG rows

The E.12 panel has 64 covered signals (reports/stage_e12_gate0_list.json "covered_signals"; g17_mes,
k8_flight_ret, k8_flight_tail uncovered after P-1a). A member signal applies only on its own vehicles' rows and
is 0 with flag 0 elsewhere (ml_route_v2/signals/_core.py:10-12; vehicle restrictions e.g. k4.py:67, 86, 105
(MCL only), k8.py:98 (6C), k9.py:60, 194 (MNQ, M2K, MYM)). A feature that is 0 on every NG row adds only a
constant to NG's prediction (absorbed with the intercept, ml_route_v2/models.py:102). So 29 signals are live
on NG rows, 35 are not.

| Feature (panel stem) | What it reads | Live on NG rows | 2010-2019 |
|---|---|---|---|
| cp1_ret, cp2_range, cp2_brk, cp3_clv (pooled ports) | NG bars; Globex open and early-halt days of the energy calendar | yes, always applicable (signals/__init__.py:82; signals/ports.py:221) | needs purchase (NG) + calendar build (energy) |
| k4_ngpre_mto, k4_ngpre_msince | NGS release instants, strategy/members/k4/_releases.py (table starts 2019-05-02, line 277) via ngpre.schedule | yes, NG rows only (signals/k4.py:118-126) | needs calendar build (NGS 2010-06..2019-05). Without it the feature is SILENTLY n/a on every row (signals/_events.py:54-68) |
| k4_ovr_ret, k4_ovr_pct | NG bars; 20 reference dates from ENERGY_FULL_SESSIONS (strategy/members/k4/ovr.py:76-80; table 2019-05-01..2026-06-18, k4/_calendar.py:8-11) | yes (signals/k4.py:158-205) | needs purchase + calendar build (without it pct is missing and every row is dropped) |
| g01_ret30, g02_ret60, g03_ret120 | NG bars; in-session check | yes (flag varies) | purchase + energy calendar |
| g04_ret_day, g06_rv60, g07_range, g08_prev_ret, g09_vol_state, g10_logvol30 | NG bars; sigma_X,d and the daily table (D6 O_X, C_X; early halts) | yes, always applicable (signals/generic.py:398-400) | purchase + energy calendar |
| g05_gap | NG bars; previous trade date's C_X - 1 close (group calendar) | yes (signals/generic.py:146-164) | purchase + energy calendar |
| g11_t_index, g12_dow | decision clock | yes, always | energy calendar + flatten table (clock) |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | NG's D8 release list in reports/stage_e2b_release_calendar.json: NGS, WPSR and FOMC (coverage 2019-05-01..2026-06-21) | yes, inside the calendar's coverage | needs calendar build. Outside coverage they are SILENTLY n/a (signals/generic.py:19-20, 277-281, 308) |
| g16_month_end | energy group calendar | yes, always | energy calendar |
| g17_nq | NQ bars, booked by the equity calendar; n/a on NQ's roll-blackout dates (signals/_core.py:14-24) | yes | needs purchase (NQ) + equity calendar |
| g17_zn | ZN bars (rates calendar) | yes | needs purchase (ZN) + rates calendar |
| g17_6e | 6E bars (FX calendar) | yes | needs purchase (6E) + FX calendar |
| g17_gc | GC bars (metals calendar) | yes | needs purchase (GC) + metals calendar |
| g17_zc | ZC bars (grains calendar) | yes | needs purchase (ZC) + grains calendar |
| g17_cl | CL bars | NO: the row's own cluster lead is never applicable (signals/generic.py:22-25, 351-352; CL leads K4) | n/a by construction; CL need not be bought |
| g17_mbt | MBT bars | not in 2010-2019 (MBT not listed); in E.12, live only from MBT's S_X 2024-01-02 (E.12_RETURN.md:535-537) | n/a by design (L4-3) |
| g17_mes | MES | no feature (P-1a, E.12_RETURN.md:533-535) | none |
| id_root_NG, id_cluster_K4 | constants | yes (panel.py:99-104) | none |
| the other 35 signals (K1-K3 and K5-K9 members; k4_apipre_ret, k4_eiafade_move, k4_eiamom_r3 on MCL; k8_* on 6C, MNQ, MBT; k9_anncday on MNQ, M2K, MYM; g17_cl; g17_mbt) | other vehicles | no: 0 and flag 0 on NG rows | not needed; computed as n/a |

Calendars also act outside the feature list:
- the decision clock: O_X, F_X, closure, early-halt and early-close dates (ml_route_v2/clock.py:11-21;
  ml_route/inputs.py:249-261, which needs a session spec for the date, data/group_session.py:121-131);
- bar booking to CME trade dates, which refuses rows outside a store's range (data/stage_e_bars.py:16-28, 115-134);
- NG's own roll blackout, which drops rows, and each leg's roll blackout, which blanks its g17 (ml_route_v2/clock.py:16-21;
  data/stage_e_bars.py:30-33);
- the D8 event-window cost and the D9.5a fill-guard deferral, both on NG's release list (ml_route_v2/targets.py:5-20).

**Code-path note.** `g17_<lead>` calls `bars_of` for its lead unconditionally (signals/generic.py:342), and
`bars_of` raises when a root has no bars in the context (signals/_core.py:189-195). The replication context
therefore needs a frame for CL and for MBT even though neither is ever live on NG rows. Proposed: empty frames,
with a test that the NG-row columns equal those from a context with real CL bars (choice C7).

**Build assertions (proposed):** before the evaluation, print per feature only the count of NG rows where it
is applicable, and stop if any feature that was applicable on NG rows in E.12 has zero applicable rows in the
replication. This catches the silent n/a failure modes above. It also checks that the replication panel's
feature_cols equal the E.12 panel's feature_cols, names and order (panel.py:128-130).

## 4. Trade rule and threshold (L4-2)

**What Gate 0 did** (ml_route_v2/gate0.py:301-306, 324-339): for pair (NG,h), n = NG's ok rows at h; n_take =
floor(0.20 x n); the trades are the n_take rows with the largest |r_hat| among non-zero OOF predictions (stable
order on ties), side sign(r_hat). That is a count rule, not a quantile. From the printed counts, n is 2,590 to
2,594 at h60 (518 trades) and 2,470 to 2,474 at hF (494 trades).

**Replication rule (proposed form of L4-2):** q_h = the smallest |r_hat| among Gate 0's NG trades at h, i.e. the
|r_hat| of the n_take-th largest OOF prediction. On each NG ok row of the replication window, trade sign(r_hat)
iff |r_hat| >= q_h, where r_hat = predict(M1_h, x). This reproduces Gate 0's trade set exactly on the training
window. A linear-interpolated 80th percentile (numpy default) would sit between the n_take-th and
(n_take+1)-th values. The difference is tiny but avoidable (choice C3). q is never computed from replication data.

**Persisted or recompute: the OOF predictions are persisted; the threshold is not.**
- Per-split predictions are cached under the state dir as `gate0B_<h>_sNN.npy` (ml_route_v2/gate0.py:279-291).
  On disk: `~/.cache/propexp_e12_phase1/gate0/`, 15 files per horizon for h60, h120 and hF, plus
  gate0B_meta.json, whose fingerprint pins the panel, features, blocks, admissible set and constants
  (gate0.py:251-266).
- The trades with r_hat exist only in memory (gate0.py:334-339; pipeline.py:338-345). The report writes test
  rows only (ml_route_v2/phase1/gate0_stage.py:176-218; the keys of reports/stage_e12_gate0.json have no trade
  rows or threshold).
- **Recompute is a reload, not a refit:** `gate0._oof` loads each cached split (gate0.py:280-284), checks its
  length, and averages the 5 out-of-fold predictions per row (gate0.py:292-298). `gate0.gate0_b_trades`
  (gate0.py:309-342) then rebuilds the trade frame. Registration with the same spec writes nothing
  (ml_route_v2/configs.py:19). The next stage must check the ledger's sha256 before and after, as E.12's run did
  (gate0_stage.py:305-320).
- **Gate:** reproduce E.12's NG h60 row (518 trades, mean 5.569, t_B 2.51) and NG hF row (494, 13.921, 2.33) to
  1e-9 against reports/stage_e12_gate0.json, then read q_h60 and q_hF and compute nothing else. On a mismatch,
  stop.
- **V24 question for the user:** this reads E.12's Gate 0 state (2019-2024 derived values). It is a
  reproduction, not a new test and not a rerun of the gate's decision (no Holm, no verdict). The M1 fit is also
  a computation on the 2019-2024 panel, though the stage prompt itself prescribes it. V24 rules out "re-mining
  the 2019-2024 stores", so the user should confirm both before the freeze.
- **Fragility:** the state lives outside the repository in ~/.cache. The next stage's first step should hash
  every state file (45 .npy, gate0B_meta.json, the two stage pickles, phase1_build.json) and keep a read-only
  copy (choice C17).

**Scale caveat (descriptive, not a gate):** q comes from OOF predictions (each the mean of 5 ridge fits on
two-thirds of the dates), while replication predictions come from one full fit. Ridge shrinkage scales with
n_train (models.py:98), so the scales should be close, but the share of replication rows above q need not be
20%. Report the realized share after the evaluation.

## 5. Window, warm-up, D4 amendment, rolls, calendars (L4-4)

**Data start (sourced).** Databento's dataset page gives `"temporalCoverage":"2010-06-06/.."` and
`"history_from":[0,"2010-06-06"]`, with ohlcv-1m `"start":[0,"2010-06-06T00:00:00.000000000Z"]` (R01, fetched
2026-10-03). E.12's quote record agrees. Every 2010-01..2010-06 chunk failed (reports/stage_e12_quotes_ext2010.md;
NG 106/112 chunks priced), and the ledger records Databento's own error text: "`start` in query
('2010-06-01 00:00:00+00:00') was before the available start of dataset GLBX.MDP3 ('2010-06-06
00:00:00+00:00')" (ledger/databento_spend.jsonl, NG.v.0 2010-06 quote line, 2026-10-03T19:52:13Z).
2010-06-06 is a Sunday, so the first full CME trade date is Monday 2010-06-07.

**Window.**
- Start S^R = 2010-06-07 (choice C5 on how D4 enters).
- Warm-up: sigma_X,d needs 20 complete dates (constants.py:68). G9 needs a 120-date median of sigma_X,d with
  min_periods 120 (signals/_daily.py:122; constants.py:162). z-scores need 60 prior row dates and at least two
  values (normalize.py:39-47, 66). The first rows therefore come about 142 trade dates after S^R, around
  2010-12-22 to early January 2011 (calendar arithmetic; the build prints the exact first row date).
- End 2019-05-03 (Friday). E.12's quote ends at 2019-05-01 00:00 UTC (data/pull_step2.py:224-231), so trade
  dates 2019-05-01..03 come from the owned May-2019 raw chunks,
  `data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/range=2019-05-01_2019-06-01.dbn.zst`, present for NG,
  NQ, ZN, 6E, GC and ZC. The step 2 builder dropped those dates' rows before any price was read
  (data/step2_store.py:26-28). Alternative: end at 2019-04-30, the quote's end (choice C6).
- Span: 2010-06-07..2019-05-03 = 8.90 years (the same convention as E.12's 4.82 years for
  2019-05-06..2024-02-29), about 2,325 weekdays before holidays.

**D4 start-rule amendment needed.** D4 fixes S_X >= 2019-05-06 and reads months 2019-05..2024-02 against
V_ref from 2025-04..2026-05 (screening/stage_e_start_dates.py:3-7). The step 2 store and loader admit only trade
dates 2019-05-06..2024-02-29 (data/stage_e_bars.py:10-14, 26-27, 61-62, 115-120; data/step2_store.py:5-6,
86-88). The extension is quote-only in the code (data/pull_step2.py:80-81). Proposed amendment D4-R, for the
replication store only:

> D4-R. For the NG replication, the store "ext2010" holds trade dates 2010-06-07..2019-05-03. S^R_NG is the
> first trade date with bars of the earliest month M* >= 2010-06 from which every month through 2019-04 has a
> median day-session one-minute volume >= 0.25 V_ref,NG (V_ref,NG unchanged from D4's record). It reads
> ts_event, volume and trade_date only. Only S^R_NG is printed (no monthly medians). Each leg (NQ, ZN, 6E, GC,
> ZC) starts at 2010-06-07. D4's earliest-S_X clause (2019-05-06) does not apply to this store. The
> replication store never enters any v2 training window, Gate 0 or the 2019-2024 stores.

Rationale for legs from the data start: in E.12, NG's five live legs all had S_X = 2019-05-06, the store's
first date (E.12_RETURN.md:535-536), so "available from the first date of data" is the faithful carry-over.
Applying D4 to the legs could set a listed leg to n/a, which L4-3 forbids. The lead may instead apply D4-R to
every root (choice C5).

**Rolls.** The price path is the volume-ranked continuous `NG.v.0` (stype continuous, the ledger's quote
request). Splices come from Databento's free symbology for `<ROOT>.v.0` over the window, as the step 2 builder
does (data/step2_store.py:17). The roll blackout is the splice date plus the two group trade dates before it
(data/stage_e_bars.py:30-33, 64). NG's own blackout dates drop its rows; a leg's blackout dates blank its g17.

**Calendar builds needed (no prices read).**
- C-1 Energy group calendar 2010-06..2019-05: holidays, early halts, and session specs with any change in
  Globex hours or settlement time as a dated SessionSpec (data/group_session.py:121-131; current coverage
  2019-05-01..2026-06-19, data/calendars/energy.py:187).
- C-2 Equity (NQ), rates (ZN), FX (6E), metals (GC) and grains (ZC) group calendars, same span (for leg
  booking, g17's same-trade-date rule, signals/generic.py:344-348, and the legs' roll blackouts).
- C-3 Topstep flatten-table rows for 2010-2019 holidays derived by Rule H-1, as Stage E.5 derived 2019-2023
  (rules/sessions.py:26-38). Topstep's own schedules do not exist for those years.
- C-4 Release calendar for NG's D8 list: EIA NGS and WPSR release instants and FOMC statements, 2010-06..2019-05,
  built and verified like reports/stage_e2b_release_calendar.json (screening/stage_e_rules.py:153-184).
- C-5 Regenerated K4 literal tables: NGS (strategy/members/k4/_releases.py, with C9's drop rules) and
  ENERGY_FULL_SESSIONS (strategy/members/k4/_calendar.py). Both are generated files whose tests recompute them
  from their sources (_releases.py:3-8; _calendar.py:3-6).
- Also free Databento metadata: the dataset condition file for vendor-degraded days (data/step2_store.py:94
  covers 2019-04..2025-04 only) and the symbology for the rolls.

**No program file has read NG or any leg before 2019-05 (evidence).**
- Every bar store starts at 2019-05-06 (step 2) or 2025-04-01 (research) (data/stage_e_bars.py:59-62).
- The step 2 builder refuses inputs outside 2019-05-01..2024-03-01 before opening a file, and drops rows outside
  2019-05-06..2024-02-29 before reading a price (data/step2_store.py:21-28).
- Of 2,853 parquet, dbn, zst and csv files under data/, none is named with a range before 2019-05 (file names
  counted, 2026-10-03).
- The 2010 extension was quote-only, $0.00 ledger lines (E.12_RETURN.md:570; data/pull_step2.py:80-81).
- Disclosures:
  - the May-2019 raw chunks hold trade dates 2019-05-01..03, decoded and dropped unread (above);
  - the K4 calendar tables start 2019-05-01 (calendar only);
  - MES's confirmation parquet is labelled from 2019-05-01 (MES is not an input here);
  - the K4 member families entered the library from published sources. Whether any source sample overlaps
    2010-2019 was not checked here (K4-ovr-01's is 2019-11-20..2020-06-03, reports/stage_e0_catalog_K4.md R-04).

## 6. Cost (L4-5), vehicle and sizing

**Cost.** D8 at the vehicle, unchanged. NG is its own vehicle and price path (docs/STAGE_E_ML_V2_DESIGN.md:162).
c(NG,h) is the mean D8 round trip of the sides taken over the test's trades, as Gate 0 computes it: commission
plus the entry and exit buckets' one-side slippage at size 1, with the event-window rule (ml_route_v2/gate0.py:16-17,
332-333, 357; ml_route_v2/targets.py:16-20). Buckets depend on the CT minute only (targets.py:64). Event windows
need C-4. The pass bar is gross, so cost enters only as c(NG,h) in the 1.5c bar. **D8 was calibrated on
2025-2026 samples; 2010s spreads and depth may differ, and nothing in this design checks them.**

**Vehicle facts.**
- NG: 10,000 MMBtu, tick 0.001 = $10 (rules/products.py:178). At EIA's 2025 Henry Hub average of $3.52/MMBtu
  (R05) a contract is worth about $35,200.
- Published volatility (EIA, 30-day historical volatility of the Henry Hub front-month future, annualized):
  - "averaged 69% in 2023 compared with 91% across all of 2022" (R10, 2024-06-04);
  - "quarterly volatility falling from a recent high of 81% in the fourth quarter of 2024 to 69% by mid-2025"
    (R17, 2025-07-24).
- Typical h60 move per contract, an estimate from the published figures (not the program's bars): daily sigma =
  69% / sqrt(252) x $35,200 = about $1,530. One hour is $320 (uniform intraday variance over about 23 trading
  hours) to $460 (60% of the daily variance in the 6.6-hour day session, an assumption). Cross-check: E.12's
  frozen proxy E|m_1| for NG, the mean absolute day-session move, is $639.3 per contract
  (E.12_RETURN.md:487). That implies an hourly sigma near $340, inside the range.
- Micro: CME launched Micro Henry Hub futures on 2023-11-06, "one-tenth the size of the company's benchmark
  Henry Hub futures" (R18, CME press release of 2023-09-27). Program records:
  - MNG is 1,000 MMBtu, tick $1 (rules/products.py:179);
  - Topstep lists it: "Micro Henry Hub Natural Gas (MNG)" under CME NYMEX Futures
    (reports/stage_e0_topstep_facts.json, F1.4, help.topstep.com/en/articles/8284206);
  - D2 chose NG over MNG on cost per dollar of risk, "NG 0.02615376 < MNG 0.08191186"
    (reports/stage_e2a_vehicles.json:682).

**Sizing under V2.8** (sigma_target = 0.10 x D; budget b = sigma_target / sqrt(3), rounded up to 1 contract
when one contract's h-sigma <= 2b; daily variance budget sigma_target^2; n_loss = floor(0.25 x D / ((L + c) x
tick $)) with L the 99th-percentile loss, taken as about 2.33 sigma here; ml_route_v2/sizing.py:3-19;
constants.py:99-104). Lot rules: one NG = 1 lot. The per-product cap is 1 lot-equivalent (constants.py:107),
and "1 mini = 10 micros" (rules/xfa_rules.py:55).

| Account | MLL = D at start | sigma_target | 2b band | 0.25 x D | one NG at h60 ($320-460 sigma, L+c $760-1,090) | one NG at hF (hold up to 6.6 h, sigma about $820-1,190) | MNG at h60 ($32-46) |
|---|---|---|---|---|---|---|---|
| 50K XFA (2 lots base) | $2,000 (account.py:74-89) | $200 | $231 | $500 | does NOT fit: sigma > 2b, sigma > daily budget, L+c > $500 | does not fit | fits: 2-3 MNG |
| 150K XFA (3 lots base) | $4,500 (account.py:95-99) | $450 | $520 | $1,125 | fits marginally at a fresh account; stops fitting once D falls to about $2,800-4,350 | does not fit | fits |

**Implication:** an NG edge of E.12's size, $55.7 gross per NG contract at h60 against a $17.1 round trip,
is economic only on full NG. On MNG, ten micros cost about $53.5 per NG-equivalent (commission $1.92 + 2 x
1.714797 ticks x $1, per micro, reports/stage_e2a_vehicles.json:677). That roughly equals the gross edge. So
even a pass is a 150K-only, one-contract, h60-only rule.

## 7. Pass bar, trial count (L4-6), what a pass and a fail mean

**Pass bar.** For each test Tk (NG h60, NG hF) on the replication window, computed with Gate 0's own statistic
`gate0._b_test` (ml_route_v2/gate0.py:345-358): per-date means of g = side x y_gross (vehicle ticks), t_B =
mean / (sd / sqrt(n_dates)) (gate0.py:114-122), one-sided p from Student's t with n_dates - 1 df
(gate0.py:125-134). Tk passes iff all of:
1. mean g >= 1.5 x c(NG,h), with c the mean D8 round trip of the sides taken over Tk's trades;
2. p <= 0.025 (Bonferroni 0.05 / 2), one-sided in the direction mean g > 0;
3. n_trades >= 30;
4. sign as in Gate 0: trades are sign(r_hat), and mean g > 0, which 1 and 2 already imply.

**The replication passes iff at least one of T1, T2 passes.** Under no edge, the chance of at least one pass is
about 0.041-0.045 for an assumed correlation of 0.5-0.7 between the two t's (computed; T1 and T2 share decision
rows, and h60 is the first hour of hF). Bonferroni bounds it by 0.05.

**Trial count.** N goes from 471 to 473 at registration, before the evaluation, whatever the outcome. The D4-R
volume check, the q reproduction and the M1 fit are not tests and add nothing.

**What a pass means.** The frozen pooled ridge's NG predictions carried a gross edge of at least 1.5x D8 cost,
with p <= 0.025, in a disjoint decade with a different supply regime. Under the global null, the chance that
the best of 81 tests reaches t >= 2.51 and also replicates at this bar is about 0.40 x 0.045 = 0.018, so a pass
is real evidence that Gate 0's NG near-miss was not only selection.

It is not a tradeable verdict:
- the bar is gross;
- costs are 2025-2026 calibrations;
- it clears none of the program's verdict bars (t >= 3, DSR at N = 473, PBO);
- the only vehicle that fits is one NG contract at h60 on a 150K XFA (section 6).

A pass would justify one more pre-registered, net, NG-only design with its own N and a forward or holdout
test before any money (holdout-2's NG chunks are owned and sealed, opened only under a registered Stage D.2).

**What a fail means.** The NG near-miss is closed. Gate 0's reading (selection among 273 tests) stands, nothing
more is built on v2's model, and N = 473. The six bought 2010-2019 stores stay on disk, reusable only under a
new pre-registration. A fail cannot separate "never real" from "real only in the 2019-2024 LNG-era regime"
(section 9), so it says less about today's market than a pass would. The test is lopsided: a pass is
informative, a fail mostly confirms the prior.

## 8. Feasibility and cost

**What must be bought:** NG plus the five live legs NQ, ZN, 6E, GC and ZC (L4-3). Not CL (g17_cl is never live
on K4 rows), not MBT (not listed), not MES (no feature), and no other root (the replication panel holds NG rows
only; NG's z-scores use NG's rows only, normalize.py:88-93).

Quoted in E.12's record (reports/stage_e12_quotes_ext2010.json, set "ml-v2+extension-2010", per_contract
"usd"; 106 of 112 monthly chunks each, 2010-07..2019-04; the 2010-06 chunk failed for all six):

| Root | Role | Quoted $ (106 chunks) | x 1.03 | Placement with today's funds |
|---|---|---|---|---|
| NG | price path | 8.515948 | 8.771426 | acct-2 (fits; leaves $9.298844) |
| ZC | g17_zc | 6.150736 | 6.335258 | acct-2 (fits; leaves $2.963586) |
| NQ | g17_nq | 10.544864 | 10.861210 | does not fit either account |
| ZN | g17_zn | 10.026241 | 10.327028 | does not fit |
| 6E | g17_6e | 10.982691 | 11.312172 | does not fit |
| GC | g17_gc | 11.094256 | 11.427084 | does not fit |
| **Total** | | **57.314736** | **59.034178** | |

- **Funds left:** acct-1 $1.609980 (holds no item), acct-2 $18.070270 (E.12_RETURN.md:572). Under the 1.03
  margin and one-account-per-item placement (docs/STAGE_E_ML_V2_DESIGN.md:229-231), today's funds cover NG and
  ZC only.
- **Top-up:** an acct-2 cap raise of **$40.963908** (= 59.034178 - 18.070270) with the margin. On E.12's
  convention (quoted total minus combined headroom, before the margin, E.12_RETURN.md:572) it is $37.634486.
  The June-2010 chunks come on top, plus the 10% session-cap convention if the lead keeps it ($63.05 cap at
  the quote).
- **Not in E.12's record (not quoted here):** the six partial chunks 2010-06-06..2010-07-01. Every 2010-06
  quote failed with data_start_before_available_start, so the purchase plan's first chunk must start at
  2010-06-06 and needs a fresh free quote. CLAUDE.md requires a fresh quote logged before any spend anyway.
- **Owned, $0:** the May-2019 raw chunks for the six roots (section 5).
- **Fallback M2** would need NG alone, $8.515948, which fits acct-2 today (only if (b) holds).

**Build effort, in sessions (estimates, not measured):**
- Calendars C-1 to C-5: 1.5 to 2 sessions. E.2a's eight calendar builders for 2019-2026 used 326M tokens (CLAUDE.md,
  context hygiene). This build is six groups over nine years plus three release series, and 2010-2013 Wayback
  coverage of CME's files is unverified.
- Harness v10: 1 session of code with a Fable review. It needs an "ext2010" store type in
  data/stage_e_bars.py and data/step2_store.py, a buy plan in data/pull_step2.py starting 2010-06-06, the May-2019
  splice, D4-R, a replication world, the M1 and q drivers, and a run-once evaluation guard like
  gate0_stage.py:260-264.
- Quote, buy, build and evaluate: 1 session.
- **Total about 3.5 to 4 sessions**, most of it sourced calendar work.

## 9. Prior, stated honestly

**Selection under the global null.** The NG h60 one-sided p was 0.0062 (z = 2.50).
- Independent tests: P(best of 81 reaches t >= 2.51) = 1 - (1 - 0.0062)^81 = **0.396**. A simulation of the
  max of 81 iid normals gives 0.388, and the expected maximum is 2.43.
- Bonferroni bound: 81 x 0.0062 = **0.502**.
- Positive correlation lowers it. For Gaussian tests with non-negative correlations, P(max >= c) <= the
  independence value (Slepian), so 0.40 is close to an upper value. With effective counts of 30 to 50 it is
  0.17 to 0.27.
- The 81 tests are correlated: one pooled model per horizon, three horizons per product on the same decision
  rows. NG h60 and hF share entries, and h60 is the first hour of hF, so the "two NG hits" are close to one
  observation, not two. The observed 2.51 is about what the best of 81 nulls looks like.
- The rest of Gate 0 points the same way: pooled B mean gross -0.72 ticks, t 0.28; no family A test near Holm
  (E.12_RETURN.md:12-14).

**Winner's curse and power.** Expected replication t = (observed t / sqrt(4.82)) x sqrt(8.90). That is
1.143 x 2.984 = 3.41 at h60 at full effect, and 1.061 x 2.984 = 3.17 at hF. The critical one-sided t at 0.025
(about 900 dates) is 1.963. Expected trades if the share above q stays near 20%: about 957 (h60) and 913 (hF).

| True effect / observed | h60 power (t bar) | h60 power incl. 1.5c bar at tick-vol ratio 0.7 | hF power |
|---|---|---|---|
| 1 (equal to observed) | 0.93 | 0.88 | 0.89 |
| 1/2 | 0.40 | 0.29 | 0.35 |
| 1/4 | 0.13 | 0.08 | 0.12 |
| 0 | 0.025 | 0.012 | 0.025 |

The cost bar binds only at h60 and only if NG's tick volatility is lower in 2010-2019. A normalized edge then
gives fewer ticks against the same D8 cost in ticks; the published figures below suggest a ratio of about 0.6
to 0.8. A selected t of 2.51 out of 81 is a strongly upward-biased estimate. Shrinking it under an effect prior
(half-normal, sd 1 in t units) gives a posterior mean of 1.3 rather than 2.5, about half the observed effect.

**NG regime change, 2010-2019 against 2019-2024 (EIA, public domain, R04).**
- Supply (shale): U.S. dry gas production was 21,315,507 MMcf in 2010, 33,899,021 in 2019 and 37,652,438 in
  2023 (R06), +59% over the replication decade. EIA: "In 2023, about 78% (37.87 trillion cubic feet) of total
  U.S. dry natural gas production was from shale formations" (R20).
- LNG exports: "on February 24, 2016, the first liquefied natural gas (LNG) cargo from the Sabine Pass Terminal
  was exported" (R19). Annual LNG exports were 28,381 MMcf in 2015, 186,841 in 2016, 1,819,547 in 2019 and
  4,343,027 in 2023 (R07). The replication decade is mostly pre-export; the E.12 window is export-driven.
- Price level (Henry Hub spot, annual, $/MMBtu, R05):

  | Year | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | $/MMBtu | 4.37 | 4.00 | 2.75 | (blank in EIA's table) | 4.37 | 2.62 | 2.52 | 2.99 | 3.15 | 2.56 | 2.03 | 3.89 | 6.45 | 2.53 | 2.19 |

  The average level is similar (about 3.3 against 3.5), but the E.12 window spans 2.03 to 6.45.
- Volatility:
  - "averaged 179% in February compared with the five-year (2017–21) average of 48%" (R16, EIA 2022-08-11);
  - "averaged 69% in 2023 compared with 91% across all of 2022" (R10);
  - "Natural gas implied volatility averaged 21.3% in March [2019], lower than the five-year average of 37.7%"
    (R15, STEO April 2019);
  - "the volatility of the Nymex near-month natural gas futures prices at the Henry Hub was low for most of
    2018" (R11).
  - So the E.12 window includes the most volatile NG market since at least 1994 ("the most volatile since at
    least 1994", R10), while the replication decade was mostly calmer. A 2022-23 shock regime could have driven
    E.12's result, which also argues for a lower replication prior.

**Overall odds that the replication passes: about 12% (range 7% to 35%).** The odds are P(real) x
P(pass | real) + (1 - P(real)) x 0.04.
- P(real) is 0.12 to 0.22 for a per-pair prior of 0.02. That prior reflects 471 trials, nine screened clusters
  and a null pooled Gate 0. The Bayes factor of t = 2.51 is 6.6 (half-normal effect prior) to 13.9 (uniform
  0..3.5).
- P(pass | real) is 0.30 to 0.61. It is the power above integrated over the effect posterior, with the effect
  kept at 75% of its 2019-2024 size to allow for the regime change.
- Central case: 0.22 x 0.61 + 0.78 x 0.04 = 0.165. Skeptical: 0.07. Optimistic (per-pair prior 0.05, no
  regime decay): 0.35.
- If it passes, the chance the edge is real is about 0.5 (skeptical) to 0.8 (central).

## 10. Design choices for the lead (lead rulings 2026-10-03, Stage E.13)

| # | Choice | Options | Proposed | Rationale | Lead ruling |
|---|---|---|---|---|---|
| C1 | Model | M1 (full-panel single fit) / CPCV 15-split ensemble average / M2 | M1 | per L4-1; (a) and (b) do not hold (section 2) | ACCEPT: M1 (per L4-1) |
| C2 | Constants file | edit ml_route_v2/constants.py / new module | new module; constants.py byte-identical | a changed fingerprint makes the E.12 build and Gate 0 state unreadable (fingerprint.py:31-39; build.py:227-233) | ACCEPT: new constants module; constants.py stays byte-identical |
| C3 | q definition | Gate 0 cutoff (smallest \|r_hat\| of the 518/494 trades) / np.quantile 0.8 | Gate 0 cutoff, trade iff \|r_hat\| >= q | reproduces Gate 0's trade set exactly (gate0.py:301-306) | ACCEPT: q = Gate 0 exact cutoff; trade iff \|r_hat\| >= q (refines L4-2) |
| C4 | q source | reload persisted OOF splits (no refit), reproduce NG h60 and hF rows to 1e-9 / refit CPCV | reload; stop on mismatch; ledger sha unchanged | predictions persisted (gate0.py:279-291); a refit is a heavier V24 question | ACCEPT: reload the persisted OOF splits, reproduce NG h60 and hF rows to 1e-9 or stop; no refit. Goes to the user as a V24 question |
| C5 | Start rule | D4-R on NG volume, legs from 2010-06-07 / D4-R on every root / fixed 2010-06-07 for all, no volume read | D4-R on NG, legs from 2010-06-07 | legs had S_X at the store start in E.12; avoids a listed leg going n/a (L4-3); reads volume only | CHANGED: fixed S^R = 2010-06-07 for NG and every leg; no volume read (nothing in 2010-2019 data is read before the evaluation; all six were mature contracts in 2010) |
| C6 | Window end | 2019-05-03 via owned May-2019 chunks / 2019-04-30 (quote end) | 2019-05-03 | per L4-4; data owned, $0; needs a splice in the store builder | CHANGED: end 2019-04-30 (the quote end); no May-2019 splice (3 of ~2,250 dates; removes a builder change and any question about the owned chunks) |
| C7 | CL and MBT bars in context | empty frames / buy CL ($11.02) / set columns directly | empty frames + equality test | g17_cl never live on K4 rows; bars_of raises if absent (generic.py:342; _core.py:189-195) | ACCEPT: empty CL and MBT frames plus the equality test; CL not bought |
| C8 | Panel scope | NG rows only / all 28 products | NG rows only | z-scores per product (normalize.py:88-93); all 28 would cost $213.94 | ACCEPT: NG rows only for the replication features (M1 itself is fitted on the E.12 panel) |
| C9 | Order of events | L4-7 as written / fit M1 and reproduce q BEFORE the purchase | M1 coefficients and q hashed into STATE before any 2010-2019 byte is bought | model and threshold fixed with no replication data on disk | ACCEPT: M1 coefficients and q hashed into STATE before any 2010-2019 byte is bought (amends L4-7) |
| C10 | Silent n/a guard | none / per-feature applicable-row counts with a stop | counts printed (no values); stop if a feature live in E.12 has 0 applicable rows | k4_ngpre and g13-g15 fail silently without calendars (_events.py:54-68; generic.py:277-281) | ACCEPT |
| C11 | feature_cols check | none / assert equal to E.12's | assert names and order equal | M1's coefficient vector is positional | ACCEPT |
| C12 | Unsourceable calendar dates | stop / exclude the date (counted) / accept secondary grade | exclude dates whose holiday or session status is not sourced at "cme" or "secondary" grade, stop if more than 2% of dates | mirrors V2.2's exclusion of early-close dates | ACCEPT: exclude unsourced dates (counted); stop above 2% |
| C13 | NGS drop rules for 2010-2019 | apply C9's drop_actual_differs rule / none | apply it (as E.5, _releases.py:18-23) | same table semantics as training | ACCEPT |
| C14 | Cost sensitivity | none / descriptive 1.5x slippage | descriptive only, after the verdict | D8 calibrated on 2025-2026 (L4-5) | ACCEPT: descriptive, after the verdict |
| C15 | Descriptive outputs | none / realized share above q, long-short split, trades per year | these three, printed after the verdict only | flags a pass driven by the NG intercept or one year; not tests, no N | ACCEPT: descriptive, after the verdict, no N |
| C16 | Pass statistic | gate0._b_test as is | as is, p <= 0.025 one-sided | per L4-6 | ACCEPT (per L4-6) |
| C17 | Persisted state | leave in ~/.cache / hash and copy read-only | hash 45 .npy, meta, 2 pickles, build json at the freeze; read-only copy | state is outside the repo and is the only source of q | ACCEPT: hash and read-only copy at the next stage's freeze; this stage records file names and sizes only |
| C18 | Harness | v10 with an ext2010 store type and buy plan from 2010-06-06 | v10, Fable review | loader refuses non-step-2 dates (stage_e_bars.py:115-134) | ACCEPT: harness v10 with a Fable review, at the next stage |
| C19 | Funding | one acct-2 top-up (>= $40.97 + June 2010 + margin), single purchase / NG+ZC now, legs later | one top-up, one purchase session | E.12 placement rule; a split purchase adds a session | USER DECISION: recommend one acct-2 top-up and one purchase session, only if the replication is chosen to run |
| C20 | Run-once guard | marker file + report existence check, as gate0_stage.py:260-264 | yes | one evaluation (L4-7) | ACCEPT |
| C21 | N | +2 at registration | 471 -> 473 | per L4-6 | ACCEPT: 471 -> 473 at registration |

## 11. Recommendation

**Run later, not now; drop it if a calendar probe fails.** The money is small: about $57.31 quoted plus the
June-2010 chunks, needing an acct-2 top-up near $41. The code supports M1 without modification, and E.12
persisted the OOF predictions, so the threshold can be reproduced without a refit. But the odds are low (about
12%), and most of the cost is 3.5 to 4 sessions of sourced 2010-2019 calendar work across six CME groups and
three release series. The payoff is asymmetric. A pass would still be gross-only and would need a further net,
forward test, and the only vehicle that fits is one NG contract at h60 on a 150K XFA. A fail would close a
door that Gate 0's Holm result has already mostly closed.

Rank it below any E.13 candidate with better odds per session. If the lead keeps it, first run a one-session
probe that sources one year (for example 2012) of the energy calendar and the NGS table at the program's
evidence grade. If that year cannot be sourced at "cme" grade for more than a few dates, drop the replication.
Otherwise freeze this draft with the lead's rulings, after the user answers the V24 question and approves the
top-up.


## Lead rulings note (2026-10-03)

The lead ruled on C1-C21 in section 10. Two proposals were changed: C5 (fixed start 2010-06-07 for every root,
no volume read) and C6 (window end 2019-04-30, no May-2019 splice). The window is therefore
2010-06-07..2019-04-30 (first rows after the warm-up, about January 2011), a subset of the hypothesis's stated
period (Databento's GLBX.MDP3 starts 2010-06-06). Section 9's odds: its own central case computes 0.165 and its
skeptical case 0.07; the headline "about 12%" is read as the midpoint of those two, range 7% to 35%.
The ranking (reports/stage_e13_ranking.md) uses the range.
