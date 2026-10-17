# Stage E.22 Part A: harness v12 audit for one confirmation run per cluster (K5, K3, K6, K8)

Worker: read-only audit (no tracked file edited, no bar/parquet/dbn content read, no runner or
confirmation run, no web). Harness manifest checked: `sha256sum reports/stage_e2b_harness_freeze.json`
= ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32 (v12, commit d30f50c).
Every fact below cites file:line, a report section, or a JSON report field. Statements marked
INFERENCE are reasoned from cited code/reports, not observed in a run.

## 0. Bottom line

| Cluster | Tier A (as E.22 lists it) | Under v12 unchanged | What blocks it |
|---|---|---|---|
| K3 (30 members, roots 6A 6B 6C 6E 6J 6N 6S) | K3-ldnrev-01 6E | **Runnable** once `--set K3` start-rule file is built (no code change) | nothing in code; the K3 FX-table open item R-A2-1 is a lead ruling (section 9) |
| K6 (27 members, roots ZC ZW ZS ZM ZL HE LE) | K6-limitcont-01 HE | **Runnable** once `--set K6` start-rule file is built (no code change) | nothing in code |
| K5 (11 members, MGC and MHG) | K5-fomc-01 MGC | **Not runnable**: `--all` aborts at ordinal 1 (MGC empty window); the verdict module refuses a Tier A/B trial with no record | needs GC price path (N1, N2) or the no-record path (N4) |
| K8 (4 members, legs MGC MES 6C MCL MNQ MBT) | K8-flight-01 HEOD MGC; K8-wkndbtc-01 MNQ | **Not runnable**: no start-rule entry for MES, 6C, MNQ, MBT; K8 set cannot be built (no MNQ step 2 store); MES has no loader path in the confirmation window and its Stage D store fails the Stage E loader's checks (E.12) | N1, N2, N3 (and N4 if any trial stays untestable) |

NEEDED changes for v13 (section 8): N1 a declared price-path mapping in the confirmation loader and
supply count; N2 start-rule entries for the path roots (GC, NQ) and a K8 set that does not read
MNQ's absent store; N3 an MES confirmation-leg path and a ruling on its 3 mismatched rows;
N4 (conditional) the verdict module and runner accepting a Tier A/B trial that has no record;
N5 (conditional) HOLM_K if the lead's K is not 9. NICE: an in-harness run-once marker, a
no-bar-read dry run, a program-N cross-check, a price-path cross-check in the verdict.

---

## 1. How the confirmation window loads each leg's bars; MES as a leg

**Path, in order (screening/stage_e_runner.py):**
1. `screen_member` calls `harness_freeze.preflight` first (stage_e_runner.py:410), loads and
   verifies the cluster freeze (:414-415), takes the frozen legs (:419), builds per-leg frozen
   inputs `_legs_inputs` (:420; :287-295) and calls `_load_frames` (:422).
2. `_load_frames` (:297-312), confirmation branch:
   `starts, provenance = _start_dates([leg.root for leg in legs])` (:307), i.e.
   `screening.stage_e_start_dates.start_dates_for` (:278-284; stage_e_start_dates.py:600-622),
   which merges every `reports/stage_e_start_rule_*.json` file. A root no file lists raises
   `StartRuleMissing` (stage_e_start_dates.py:607-610); a root whose `s_x` is null raises
   `StartWindowEmpty` (:611-615).
3. Per leg: `load_confirmation_leg(leg.root, step2_root, starts[leg.root],
   expected_sha256=provenance[leg.root]["step2_sha256"])` (stage_e_runner.py:308-310).
   `data/stage_e_bars.py:297-312` resolves the file with `_step2_parquet_path` (:240-246) =
   `data.step2_store.step2_parquet_path(root, step2_root)` (data/step2_store.py:113-114) =
   `<step2_root>/<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet`. `read_leg`
   (stage_e_bars.py:271-289) checks the sha256 against the start-rule file's recorded store
   (review F-3), reads the 16 `BAR_COLUMNS` (:66-70), books every row on
   `product(root).group`'s calendar (`check_bookings`, :154-177: unbookable, holdout/embargo/
   out-of-store, label mismatch all refuse), reads the roll splices from the file's
   `propexperiment` metadata (:180-219) and only then cuts at S_X (:306-312).
4. `member_window(frames, STEP2)` (stage_e_runner.py:425; stage_e_align.py:57-73): intersection
   of the legs' trade dates less the union of every leg's roll blackout; every leg must come
   from the same store label (stage_e_align.py:62-63). Then D9 coverage (:432;
   stage_e_align.py:116-143), the engine, the series. The record carries `s_x` keyed by leg root
   (stage_e_runner.py:311-312) and `bars` with each file's name and sha256 (:440-441).

**MES as a leg in the confirmation window: it fails.** Three independent failures, in the order
the code reaches them:
1. **No S_X entry.** Only `reports/stage_e_start_rule_K4.json` (products MCL, NG) and
   `_K5.json` (MGC, MHG) exist (`ls reports/stage_e_start_rule_*.json`; their `products` keys).
   MES enters a set file only through `mes_from_d1f` (stage_e_start_dates.py:268-292) when a
   set's roots include MES (`build_set`, :353-354); only K8's members read MES
   (reports/stage_e_k8_member_freeze.json members 1-2). So today `_start_dates` raises
   `StartRuleMissing` for MES. E.9's own research records show it:
   reports/stage_e9_k8_screen/K8_K8-flight-01_HEOD_MGC_research.json `power.reason` =
   "StartRuleMissing: no frozen S_X for ['MES']".
2. **No step 2 file at the expected path.** Even with a K8 file, `load_confirmation_leg("MES",
   step2_root, ...)` looks for `data/processed_step2/MES/...step2.parquet`, which does not exist
   (`ls data/processed_step2/MES` fails); `read_leg` raises `ConfirmationStoreMissing`
   (stage_e_bars.py:276-278). The MES entry's `step2_sha256` would be the D.1f confirmation
   parquet's sha256 82e256b4a741... (stage_e_start_dates.py:279, 289-290;
   reports/stage_d1f_step5_start_rule.json `run_inputs_sha256.confirmation_parquet`), i.e. the
   Stage D store `data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet`,
   which no runner code path opens. `screen_member` catches only `EngineRefusedCase` and
   `FrozenInputError` (stage_e_runner.py:456), so this aborts the whole `--all` run.
3. **The Stage D store fails the Stage E loader's checks.** ML route v2 read exactly that file
   through `data.stage_e_bars.read_leg(MES, path, STEP2, expected_sha256=...)`
   (ml_route_v2/phase1/world.py:352-366) and it was refused:
   reports/stage_e12_briefs/phase1_build.log:2 "TradeDateMismatch: ... 3 MES rows labelled with a
   trade date other than their equity-calendar booking (first: label 2020-03-30, booked
   2020-03-31)"; reports/E.12_RETURN.md:533-534; reports/stage_e12_phase1_bars.json
   `mes_refusal`. The loader code has not changed since (data/stage_e_bars.py last commit 273c27b;
   data/group_session.py and data/calendars/*.py last commit 10454b1), so the same refusal
   would recur under v12 (INFERENCE: same file pinned by sha, same code).
   INFERENCE on the cause: the D.1f build summary reports exactly 3 `in_scheduled_closure` bars
   (reports/stage_d1f_confirmation_build.json `flag_counts.in_scheduled_closure` = 3) and its
   trade-date range is 2019-05-06..2024-02-29 (`trade_date_range`), so the store-range check
   passes and the 3 mismatched rows are very likely the 3 scheduled-closure prints that D.1's
   rule labelled to 2020-03-30 and the Stage E group calendar (L-3) books to 2020-03-31 (the same
   class of bar that v9's closure-ruling path handles for step 2 stores, e.g. NQ
   "2020-03-31 Tue 16:59" booked to 2020-04-01, reports/stage_e12_closure_rulings.json). The
   exact rows were not read (brief).
   The file has the 16 BAR_COLUMNS (INFERENCE: read_leg reads the columns at :279 before the
   booking check that raised). Its `rolls` metadata was never reached; data/build_mes_bars.py:571
   writes `"rolls": [asdict(r) ...]` with `ts_ns` (data/adapter.py:53-58), so it is likely
   readable, unverified.

---

## 2. Price-path substitution (micro on full-size bars): none exists

**No mechanism exists.** Every confirmation-path function keys the store file, the S_X lookup and
the pinned sha256 by `leg.root` (stage_e_runner.py:307-310, :319-326; stage_e_bars.py:297-334;
stage_e_start_dates.py:301-316, 350-362). The only "fallback" text is the runner's note that the
full-size fallback "is the user's decision" (stage_e_runner.py:104-106, `EMPTY_WINDOW_NOTE`).
ML route v2's "price path" is its own module (ml_route_v2/phase1/world.py) and never loads a
micro on a full-size store; it is not the cluster runner.

**Why keying must stay on the vehicle's root (member code untouched):** member code hard-codes
the vehicle and signal roots: strategy/members/k8/flight.py:69-70 (`TRADED = "MGC"`,
`SIGNAL = "MES"`), wkndbtc.py:51-52 (`"MNQ"`, `"MBT"`), k8/_calendar.py:54-56,
k8/_releases.py:26, k5/fomc.py:38, 74 (`Fomc("MGC")`). The engine feeds bars by `leg.root`
(stage_e_engine.py:676-683). So the GC frame must be presented under the key "MGC".

**Where each root-dependent value comes from (all keyed by `leg.root` today):**

| Value | Source | Under substitution |
|---|---|---|
| tick value (cents) | `rules.products.product(root).tick_value_usd` -> `LegInputs.tick_value_cents` (stage_e_frozen.py:261-275); used by `StageERules.tick_value` (stage_e_rules.py:298-299) | keep vehicle (MGC $1.00, MNQ $0.50) |
| price grid | `product(root).vendor_tick_fixed` (stage_e_rules.py:188-212, 301-309) | identical: GC/MGC 100000000 (0.10), NQ/MNQ 250000000 (0.25) (`uv run python -c` over rules.products) |
| D8 cost model | `FrozenTables.costs[root]` from reports/stage_e2a_costs.json (stage_e_frozen.py:212-239, 271-275); commission from products | keep vehicle (both calibrated: costs JSON `calibrated` true for MGC, MNQ, GC, NQ) |
| q_c, eps_X | reports/stage_e2a_vehicles.json / _epsilon.json via `leg_inputs` (stage_e_frozen.py:271-275) | keep vehicle (MGC q_c 1, MNQ q_c 1) |
| event windows / D9.5a guard | `ReleaseCalendar.by_root[root]` (stage_e_rules.py:122-170); calendar rows exist for MGC (212 pre-2024), MNQ (212), GC (212), NQ (212) (count over reports/stage_e2b_release_calendar.json `releases`) | keep vehicle |
| price limits D9.7 | `pl.HARD_LIMIT_PRODUCTS` / `limit_band(root, ...)` (stage_e_rules.py:318-329, 362-368); prior settlement = VWAP proxy of the leg's own bars (rules/price_limits.py:41-45) | MGC: DCB only, never consulted (stage_e_rules.py:363); MNQ: equity bands, the proxy would weight NQ's volume (prices identical; the reference is already a proxy). No MNQ/NQ/HE/LE period in 2019-05-06..2024-02-29 is `pending` (scan of `pl.LIMITS`); MGC has a pending 2019-05-01..2019-07-17 period but DCB products are never looked up |
| trade-date booking, calendar, flatten flags | `product(root).group` (stage_e_bars.py:285, 331; stage_e_align.py:121); flags precomputed in the store by group policy (data/group_session.py:516-519) | identical groups: GC/MGC metals (`stage_e_d9_1_metals` in reports/step2/bars_GC.json and bars_MGC.json), NQ/MNQ equity |
| roll blackout (D4 union) | splices from the FILE's `rolls` metadata booked on the group calendar (stage_e_bars.py:189-219) | becomes the price path's own rolls (GC, NQ): the splices the price path actually has. Lead should declare this reading |
| D9 coverage | `member_coverage(frames, dates, member.trading_windows)` keyed by frame key (stage_e_align.py:116-143) | keyed by vehicle (member windows are keyed "MGC"/"MNQ"); presence measured on GC/NQ bars |
| D6 day session (start rule) | `FrozenTables.day_session_ct[root]` (stage_e_start_dates.py:144-159) | GC 07:20-12:30 = MGC; NQ 08:30-15:00 = MNQ (reports/stage_e2a_vehicle_sizes.json `contracts`) |
| research parquet sha (V_ref) | `FrozenTables.research_parquet_sha256` (stage_e_frozen.py:233-235) | GC fa8c47a0eb2b..., NQ 5284f91e7ada... are recorded |
| S_X and the pinned step 2 sha | start-rule file entry for `root` (stage_e_runner.py:307-310, 319-326) | must be the PATH root's entry (D4: "the start rule then runs on the full-size contract", docs/STAGE_E_DESIGN.md:266-268) |
| record `s_x`, `bars` | stage_e_runner.py:311-312, 440-441 | keep `s_x` keyed by vehicle (the verdict checks `start_dates[trial.vehicle]`, stage_e_verdict.py:429); `bars` shows the GC/NQ file name and sha (auditable) |
| members' use of volume / raw_symbol | none in k5/ or k8/ (grep "volume", "raw_symbol" over strategy/members/k5, k8: no hits); engine uses volume only for a sign check (stage_e_rules.py:212) | substitution does not change any K5/K8 member input other than prices/ids |

**Minimal change (detail in section 8, N1/N2):** a frozen declared mapping {vehicle: path root}
(e.g. {"MGC": "GC", "MNQ": "NQ"}) read by (a) `data/stage_e_bars.load_confirmation_leg` and
`read_leg_dates` (open the path root's step 2 file; book on the vehicle's group calendar after
asserting `product(path).group == product(vehicle).group` and equal `vendor_tick_fixed`;
LegFrame.root stays the vehicle), (b) `stage_e_runner._load_frames` and
`confirmation_supply_days` (S_X and pinned sha from the path root's start-rule entry; record a
`price_path` map), and (c) `stage_e_start_dates.set_roots` (compute the path root's entry, never
read the vehicle's own step 2 store when it is mapped). The research window is not touched (the
micro's own research bars stay the screened series).

D2/D4 conditions the lead must state in the declaration: D2 allows it "where the vehicle is a
micro whose own history is too short for D4's power check" (docs/STAGE_E_DESIGN.md:173-177);
D4: "only if the power check fails and the user agrees" (:276-279, 293-294). MGC qualifies: its
own window is empty (reports/stage_e_start_rule_K5.json MGC `s_x` null; E.5_RETURN.md 1, the six
MGC trials "supply 0, inconclusive by design"). **MNQ does not literally qualify**: its own
history exists but is not owned (no data/processed_step2/MNQ; E.9_RETURN.md:271 "wkndbtc needs
MNQ and MBT ($10.70 ...)"); E.22 A2 lists NQ among the owned stores to use. That reading is the
lead's to log. MBT -> BTC is not available (BTC not owned).

---

## 3. The start rule (screening/stage_e_start_dates.py)

**Computation:** V_ref,X = median of the 14 reference monthly medians (2025-04..2026-05) of the
day-session one-minute volume in the research store; S_X = first trade date of the earliest month
M* from which every month through 2024-02 has median >= 0.25 V_ref; 0.15 and 0.40 descriptive
(module docstring :1-38; rule in `screening.stage_e_stats_start.start_rule`).
`product_start_rule` (:250-265) reads only `ts_event`, `volume`, `trade_date` (:95, :179-207) of
the research store (sha pinned to E.2a's record) and of the step 2 store (sha recorded, not
pinned), with every row booked (`check_bookings`). Day session = D6 (O_X, C_X) from
reports/stage_e2a_vehicle_sizes.json (:144-159); MES from D.1f's pinned record (:268-292,
`D1F_RECORD_SHA256` 4f2870f5..., matches the file's sha256).

**Invocation:** `uv run python -m screening.stage_e_start_dates --harness-sha256 <v> --set
K1..K8|ML [--research-root DIR] [--step2-root DIR]` (:625-640). One file per set,
`reports/stage_e_start_rule_<SET>.json`, written once, chmod 0444 (:375-389); `build_set` runs the
preflight first (:338-372). Set roots = the set's traded vehicles in E.2a's table plus every leg
its frozen members read (:301-316). A set with any refused root is refused whole (:323-335;
any `ConfirmationStoreMissing` in `product_start_rule` propagates out of `build_set`). The loader
does not check a file's `harness_sha256`, only its own consistency (:499-539); two files must
agree on every shared root (:551-571, StartRuleConflict).

| Set | Roots | Research store + E.2a sha + D6 | Step 2 store | Buildable under v12? |
|---|---|---|---|---|
| K3 | 6A 6B 6C 6E 6J 6N 6S | all present (`ls`; sizes JSON) | all present, status built, v9 7fd757f6 (reports/step2/bars_*.json) | **Yes** |
| K6 | HE LE ZC ZL ZM ZS ZW | all present | all present, built (HE/LE v9; grains v8 452c4a51) | **Yes** |
| K8 | 6C MBT MCL MES MGC MNQ | MNQ, MBT, MGC, MCL, 6C present; MES via D.1f | **MNQ: none** (`ls data/processed_step2/MNQ` absent) | **No**: MNQ refuses the set whole |
| K7 | MBT (reports/stage_e_k7_member_freeze.json legs) | present | present (first trade date 2021-05-03) | Yes (gives MBT's entry, but writes a K7 file) |
| ML | 31 price-path contracts incl. GC, NQ (ml_route.constants.PRICE_PATH_CONTRACTS) | present | **HO, RB, SI absent** from data/processed_step2 | **No** |

So no existing set gives GC or NQ an entry (they are neither a vehicle nor a member leg; ML fails
on HO/RB/SI), and no set can give MES or MNQ one. K3 and K6 need no code change.

**Expected values (descriptive, from E.12's call of the same frozen per-root function,
reports/stage_e12_phase1_bars.json `roots.<R>.start_rule`, stores whose sha256 equals the
bars_*.json record):** S_X 2019-05-06 for 6A 6B 6C 6E 6J 6N 6S ZC ZW ZS ZM ZL HE LE GC NQ
(V_ref: 6E 121.5, HE 30.75, GC 165.0, NQ 770.5); **MBT 2024-01-02** (V_ref 48; 0.15: 2023-11-01;
0.40: none; 41 trade dates, 7 of them roll-blackout in window). E.12 computed these without
writing set files (ml_route_v2/phase1/world.py:26-33). They are not a substitute for the set file
the runner needs; they predict what `--set K3/K6` should write.

GC/NQ as a substituted path: the per-root function itself works for them (E.12 did it); what is
missing is a set that includes them (N2). V_ref for a substituted path comes from the full-size
contract's own research volumes (GC 165, NQ 770.5), per D4's "the start rule then runs on the
full-size contract" (docs/STAGE_E_DESIGN.md:266-268).

---

## 4. The power check (E.5 C2) and the supply of cross-product members

**E.5's path:** a research re-run of the whole cluster under the confirmation harness,
`python -m screening.stage_e_runner --harness-sha256 <v6> --cluster K4 --all --window research
--research-root ... --step2-root ... --out-dir reports/stage_e5_power_k4` (E.5_RETURN.md 3 Task
C2, lines 245-248; reports/stage_e5_k4_start_power.md:16 and _k5_start_power.md:16: "a research
re-run under v6 via python -m screening.stage_e_runner --all --window research ... which first
matched E.4 field by field apart from power, harness_sha256, created_utc and the trip files
record_sha256"). The power field is filled by `_research_statistics`
(stage_e_runner.py:507-526): `confirmation_supply_days(legs, step2_root)` then
`st.power_check(series, cluster, ordinal, supply)` (screening/stage_e_stats_power.py:507-561;
seed 20260922 + ordinal; alpha_a = 0.05 / (9 x m_c) with m_c from `CLUSTER_MEMBER_COUNTS`
:77-79, K8 = 3). A refusal while counting supply is recorded as `{"status": "not_run",
"reason": ...}` (:517-519), a zero-variance series as "power check undefined" (:522-524).
The list then copies each trial's power object (reports/stage_e5_k4_confirmation_list.json
trial 7 `power`, with `supply_days`, `label`, `n_b_chosen`, ...).

**Supply for a cross-product member** (`confirmation_supply_days`, stage_e_runner.py:315-331):
S_X of every leg (signal legs included) with `allow_empty=True`; a leg with an empty window
makes the supply 0 (:320-322); otherwise each leg's step 2 trade dates from its own S_X
(`read_leg_dates`, stage_e_bars.py:315-334, timestamp and trade_date only), **intersection of the
legs' dates minus the union of every leg's full roll blackout** (:329). This equals the
`member_window` rule the confirmation run applies (stage_e_align.py:57-73; D4,
docs/STAGE_E_DESIGN.md:274-278).

**Current state of the five Tier A records (power `not_run` in every one):**
K5-fomc-01 MGC "no frozen S_X for ['MGC']" (E.4b record; E.5 later computed supply 0, n_b 1,
inconclusive by design, reports/stage_e5_power_k5/K5_K5-fomc-01_MGC_research.json);
K3-ldnrev-01 6E "['6E']"; K6-limitcont-01 HE "['HE']"; K8-flight-01 HEOD MGC "['MES']";
K8-wkndbtc-01 MNQ "['MNQ', 'MBT']" (each record's `power.reason` under
reports/stage_e4c_k3_screen/, stage_e8_k6_screen/, stage_e9_k8_screen/).

**For E.22:** K3 and K6 power checks follow E.5 exactly after the K3/K6 files exist (research
re-runs under the confirmation harness; K3's research records were written under v4 82ae8536, K6
and K8 under v6 9a8ebe73 (`harness_sha256` of each `*_research_cluster.json`); no research-path
code changed since v6 (section 7), so a field-by-field match is expected, to be verified as E.5
did). K5 and K8 power at the substituted supply needs N1 in `confirmation_supply_days` too.
Upper bound for wkndbtc (not computed): its supply <= MBT's 41 dates less MBT's 7 blackout dates
= 34 (E.12 MBT figures above), whatever NQ contributes.

---

## 5. The verdict module (screening/stage_e_verdict.py)

**Invocation:** `uv run python -m screening.stage_e_verdict --harness-sha256 SHA --list LIST.json
--records DIR --out OUT.json` (docstring :33-34; `main` :690-704). Preflight first (:707); the
list's `harness_sha256` must equal the preflighted harness (:712-714); the output is written
once (:671-679, :708-709). Every record must carry the list's harness and cluster-freeze sha256
(`check_record` :383-405), so the run, the list and the verdict must share one harness version.

**List schema `stage_e_confirmation_list/1`** (`parse_list` :334-367, `_trial` :294-331),
matching reports/stage_e5_k4_confirmation_list.json: `schema`, `cluster`, `harness_sha256`,
`cluster_freeze_sha256`, `k_holm` (must be 9), `program_n` (int >= 1), `bootstrap`
{seed_base 20260923, resamples 10000, mean_block 5.0, ucb_quantile 0.95} (exact), `start_dates`
{root: ISO date} (must cover every root in every record's `s_x`, :396-401, and each trial's
vehicle, :429-432), `trials` [{ordinal, member, vehicle, q_c, eps_ticks, eps_usd_per_day_at_q
(all checked against the frozen epsilon table, :313-326), tier A|B|excluded, run (A/B must be
true, excluded false, :300-302), labels (subset of `LIST_LABELS`: "source-overlap", "calendar
partly unverified", "inconclusive by design", and the four runner D9 labels, :97-104),
bootstrap_seed = 20260923 + ordinal (:308-311), power object or null}]. Extra keys (E.5's
`confirmation_window`, `rules`, `inputs`, `stage`, `created_pdt`) are not read. `load_records`
refuses any `<cluster>_*_confirmation.json` record in the directory that the list does not
name (:655-668): since `--all` writes a record for every frozen member, the list must list all
of them (K3 30, K5 11, K6 27, K8 4).

**Holm:** `holm_tier_a(pvalues, HOLM_K)` over the Tier A p_upper (:497-498), K a module constant
`HOLM_K = 9` (:76, "V14 (b)"); a list with any other `k_holm` is refused (:338-339; pinned by
tests/test_stage_e_verdict.py:653-655 "K 8 is not 9"). A Tier A trial without a series enters at
p = 1 (:496-497). Frozen `holm_tier_a` accepts K in 1..9 (screening/stage_e_stats.py:317-334),
and `k_from_tiers` (:253-) computes "clusters with a non-empty Tier A, plus one when the ML route
has a tested rule", but the verdict module does not call it.
- K sources: D5 "K = the number of clusters with a non-empty Tier A in the program (at most 8)"
  (docs/STAGE_E_DESIGN.md:307-308); V14 (b) "Holm K = 9 (the maximum) for every Holm run until
  every cluster and the ML route have been screened" (docs/DECISIONS.md:251-253); V21 "K = 10 as
  the proposed maximum Holm K (K9 dropped, the ML route kept)" (docs/DECISIONS.md:379-381).
- Clusters with a non-empty Tier A per the returns: K3 (E.4c_RETURN.md:151), K4 (E.5_RETURN.md
  table, K4-ngpre-01), K5 (E.4b_RETURN.md:118), K6 (E.8_RETURN.md:274), K8 (E.9_RETURN.md:262):
  **5**. Empty: K1 (E.7_RETURN.md:233), K2 (E.3_RETURN.md:276-282), K7 (E.6_RETURN.md:10, 225).
  Whether the ML route adds one (k_from_tiers' `route_tested`): UNKNOWN (not checked here).

**DSR:** at the list's `program_n` (:350, :504), any int >= 1, not cross-checked against
`screening.trial_registry.current_n()` (ledger/trial_registrations.jsonl last line E21:
n_before 528, n_after 532). Sharpe variance over the Tier A series when there are >= 2, else over
every run trial's series of the cluster (:502-506, V14 c); with one series it is undefined and the
verdict reads "no edge (dsr undefined)" (:505-506, :530-541). K3, K5, K6 each have one Tier A
trial, so their variance is over every run trial of the cluster. E.5 used `program_n` 150 (list
JSON; E.5_RETURN.md Task C4).
**t:** daily t of the trial's own series, pass > 3.0 (`T_MIN = HLZ_HURDLE`, :78; :193-198).
**PBO:** CSCV over the Tier A series (>= 2) else every run series, aligned on the union of every
run trial's dates with 0 off a trial's own dates, 8 blocks (:507-509, :558-568, :215-245).
**Null statement:** "null" when every covered trial (run and not "inconclusive by design") is
"null" or "null by inactivity" (:571-590); by-design and excluded trials are listed as not
covered and block nothing (L-E5-5, docstring :28-30).

**Trials with no record: refused.** A Tier A or B trial must have `run: true` (:300-302) and a
run trial with no record raises "marked run in the list, no record" (:630-631; pinned by
tests/test_stage_e_verdict.py:597-601). "untestable on owned data" is not a known label (:305-307
refuses unknown labels). This matches E.5_RETURN.md:420-422 ("needs a harness change first: the
verdict module must accept a Tier A or B trial with no record").
**Note for the lead (not a defect claim):** a trial labelled "inconclusive by design" that does
have a run record still gets its bootstrap figures (:473-474, no `by_design` test), so a Tier A
by-design trial enters Holm with its real p_upper (:497), and its series joins the DSR variance
and PBO sets (:500-509). Only the null side ignores it (`covered`, :264-269).

---

## 6. Run-once marker

**None in the Stage E runner or verdict module.** `grep -rln "RUN_ONCE|run_once|run-once"` over
screening/, data/, strategy/ finds only screening/stage_e14_c2.py (C2's own marker,
`MARKER_PATH` :91, checked :450-451, written O_EXCL-style via `_write_new` :508 before any bar
or GEX value is read, docstring :29-33). The runner guards only per output file: `write_record`
opens with mode "x" and refuses an existing file (stage_e_runner.py:353-362; trips list
:365-382), which happens AFTER the bars are read and the engine has run, and only within the
same `--out-dir`. E.5 had no marker (no hit in reports/E.5_RETURN.md).

**E.21's pattern** (multiday/run.py, outside the harness manifest: no `multiday/` file in
reports/stage_e2b_harness_freeze.json `files`): all input checks first (freeze, registry,
output free, stores preflight with no row read; :95-143), refuse if
`reports/stage_e21_RUN_ONCE.json` exists (:117-118), then `write_marker` with
`os.open(..., O_WRONLY | O_CREAT | O_EXCL, 0o444)` (:81-92) BEFORE any bar is read
(:151-153); after the marker any exception writes `STOPPED.json` and the attempt is closed
(:154-166). Marker content: reports/stage_e21_RUN_ONCE.json (schema stage_e21_run_once/1, test
ids, freeze sha256, registration id, registry sha256, manifest sha256, per-store preflight).
Earlier markers: reports/stage_e14_c1_RUN_ONCE.json, stage_e18_c1b_RUN_ONCE.json,
stage_e20_H6_RUN_ONCE.json.

**Abort semantics that matter for run-once:** `screen_cluster` (stage_e_runner.py:529-560)
builds every member's record in ordinal order inside one list comprehension (:534-537); any
exception other than `EngineRefusedCase`/`FrozenInputError` (StartRuleMissing,
StartWindowEmpty, ConfirmationStoreMissing, ParquetHashMismatch, TradeDateMismatch,
RollMetadataMismatch, "window is empty", release-calendar coverage, ValueError,
EngineInvariantError) aborts the cluster after the earlier members' records are written and
writes no cluster record. Under a run-once marker such an abort consumes the attempt.

---

## 7. Harness commits v7..v12 that bear on confirmation runs

`git log ce3cb66..HEAD -- screening/ data/stage_e_bars.py data/step2_store.py data/group_session.py
data/calendars rules/ sim/ strategy/stage_e/ funnel/` returns only d30f50c, dc93e9b, 4b1e81e.
Last commit per key file: stage_e_runner.py b20163a (v4), stage_e_verdict.py 2c0bfe0 (v5),
rules/sessions.py 2c0bfe0 (v5), stage_e_bars.py, stage_e_start_dates.py, stage_e_stats*.py,
stage_e_align.py, stage_e_engine.py, stage_e_rules.py, stage_e_frozen.py 273c27b (E.2b),
rules/products.py, rules/price_limits.py, data/group_session.py, data/calendars/*.py 10454b1 (E.2a).

| Version (sha prefix) | Commit | Code changed (`git show --stat`) | Bearing on a confirmation run |
|---|---|---|---|
| v7 eee8a8b9 | 5931e30 2026-10-03 | data/config.py (per-account Databento keys) | none |
| v8 452c4a51 | deccd17 2026-10-03 | data/config.py, data/pull_step2.py (training-window purchase) | stores bought/built then: GC, MBT, ZC ZW ZS ZM ZL step 2 stores carry `harness_sha256` 452c4a51 (bars_*.json); no reader change |
| v9 7fd757f6 | 4b1e81e 2026-10-03 | data/step2_store.py closure-bar ruling path; harness_freeze lists reports/stage_e12_closure_rulings.json | stores with held closure bars built keep_and_flag (6A..6S 1 each, HE 2, LE 3, NQ 7, ZS 3, ...; bars_*.json `closure_bars`); the engine already skips closure prints (OC-T, stage_e_engine.py:431-471). No reader change |
| v10 dc93e9b | dc93e9b 2026-10-05 | hist2010 calendars, data/hist_*.py, pull_hist, screening/stage_e14_c2.py, screening/trial_registry.py, harness_freeze (data/processed_hist, entry modules, test patterns) | trial_registry is the program-N source (`current_n`); C2 is the in-harness run-once precedent. Runner, loader, verdict unchanged |
| v11 | a21d82d 2026-10-09 | data/config.py (acct-2 cap for C1) | none |
| v12 ece91ae8 | d30f50c 2026-10-10 | livestock hist2010 calendar, data/config.py, hist_calendar/hist_store/pull_hist | none (hist stores only) |

So the confirmation path in v12 is byte-for-byte the v6 path E.5 used for K4 (runner v4, verdict
v5, loader and start rule E.2b), plus v9's closure-flagged stores.

---

## 8. Minimal harness changes for v13 (member code untouched)

### NEEDED

**N1. Declared price path in the confirmation loader and supply count.** Blocks K5 (every MGC
trial, Tier A K5-fomc-01) and K8 (HEOD and H30 on MGC; wkndbtc on MNQ).
- New frozen input, e.g. `reports/stage_e22_price_paths.json` (schema
  `stage_e_price_paths/1`): {vehicle: {"path": root, "reason": ..., "declared_pdt": ...}},
  {"MGC": "GC", "MNQ": "NQ"} as the lead rules; listed in `harness_freeze.FROZEN_INPUTS`
  (screening/harness_freeze.py, the tuple at :247-267) so v13 pins it, or pinned by sha256 in
  a module constant. Written before any confirmation read (D2, D4).
- data/stage_e_bars.py: `load_confirmation_leg(root, step2_root, start, *, expected_sha256,
  path_root=None)` and `read_leg_dates(..., path_root=None)` open
  `_step2_parquet_path(path_root or root)`, refuse unless `product(path_root).group ==
  product(root).group` and `vendor_tick_fixed` and `tick_size` are equal, book on the vehicle's
  group calendar, keep `LegFrame.root = root`, and keep the path file's name/sha in
  `LegFrame.path/sha256`.
- screening/stage_e_runner.py: `_load_frames` (:297-312) and `confirmation_supply_days`
  (:315-331) look up S_X and the pinned sha by `path_of(leg.root)`, pass `path_root`, key frames
  by `leg.root`, and add `"price_path": {leg.root: path}` to the record; the record's `s_x`
  stays keyed by `leg.root` (value = the path's S_X) so `stage_e_verdict.check_record`
  (:396-401) and `_series` (:429-432) work unchanged with list `start_dates` {"MGC": GC's S_X}.
  The research branch (:299-305) ignores the mapping.
- Tests (pin it): tests/test_stage_e_loader.py: a mapped leg reads the path store, is booked on
  the vehicle's calendar, keyed by the vehicle, pins the path store's sha, and refuses on a group
  or tick mismatch. tests/test_stage_e_runner.py (world fixtures): a mapped confirmation run
  records `price_path`, takes S_X from the path root, its trip cents use the micro's tick value
  and D8 table (e.g. a GC-priced 1-tick move books $1.00 on MGC), the supply count uses the path
  root, the research window ignores the mapping, an undeclared mapping or a mapping file with a
  wrong sha refuses.

**N2. Start-rule entries for the path roots, and a K8 set that can be built.** Blocks K5 and K8
(no set can give GC, NQ, MES or MNQ an entry: section 3).
- screening/stage_e_start_dates.py `set_roots` (:301-316): for a vehicle or leg with a declared
  path, add the path root and do not compute the mapped root's own entry (MNQ has no step 2
  store, so `build_set` (:338-372) refuses K8 whole today). Optionally a separate set id for
  path roots (then extend `FILE_PATTERN` :94 and `SETS` :95 and the loader's name check
  :517-523). MES keeps `mes_from_d1f`; the K8 file's MGC, MCL and 6C entries will equal K5's,
  K4's and K3's (same stores), so no StartRuleConflict (:551-571).
- Tests: tests/test_stage_e_start_dates.py next to
  `test_a_cluster_set_is_its_frozen_vehicles_and_every_leg_its_members_read` (:332): a set with a
  declared path computes the path root's entry from the path's research store (E.2a sha) and
  step 2 store and never opens the vehicle's step 2 store; a path root without an E.2a research
  sha or D6 window refuses; MES still comes from D.1f.

**N3. MES as a confirmation leg.** Blocks K8-flight-01 HEOD (Tier A) and H30 (Tier B).
- A store resolver for MES in the confirmation branch: path =
  `data.research_bars.CONFIRMATION_SERIES_PATH` (data/research_bars.py:55-56), expected sha256 =
  the MES entry's `step2_sha256` (D.1f's pinned 82e256b4...), read with the step 2 checks and cut
  at S_X (the ML v2 pattern, ml_route_v2/phase1/world.py:340-366), in both `_load_frames` and
  `confirmation_supply_days`.
- A ruling on the 3 rows E.12 found (section 1, item 3), applied by enumeration only (the v9
  pattern: data/step2_store.py:325-395, reports/stage_e12_closure_rulings.json): the listed MES
  rows are re-booked to the calendar's date and flagged `in_scheduled_closure` (or dropped),
  every other mismatch still refuses. Alternative: build a Stage E step 2 store for MES from its
  owned unsealed chunks (needs a reports/step2/purchase_MES.json manifest for data.step2_store,
  and MES's start-rule entry would then pin a different store than D.1f's record, against F-3).
  The lead chooses; both are harness changes.
- Tests: tests/test_stage_e_loader.py (a synthetic file in the D.1f layout loads as MES with the
  pinned sha; a non-enumerated label mismatch still refuses; the enumerated rows are handled as
  ruled); tests/test_stage_e_runner.py (an MES signal leg in the confirmation window starts at
  2020-02-03 and its blackout joins the union).

**N4 (conditional: needed if any Tier A or B trial has no record).** Today a trial whose leg
cannot be loaded aborts the `--all` run (section 6) and the verdict refuses a run trial with no
record (section 5). This is NEEDED if the lead leaves any trial untestable: wkndbtc if the MNQ->NQ
reading is not adopted or BTC would be required for MBT; HEOD/H30 if N3 is not built; the K5 MGC
trials if N1/N2 are not built.
- screening/stage_e_runner.py `screen_cluster` (:529-560): for a member declared untestable in a
  frozen file (named missing leg), write a record with `status` "not_run", the reason, and no
  series, instead of loading; the cluster continues. (Do not catch arbitrary refusals: an
  unexpected refusal should still stop the run.)
- screening/stage_e_verdict.py: add "untestable on owned data" to `LIST_LABELS` (:102-103);
  let a Tier A/B trial with that label or "inconclusive by design" be listed `run: false`
  (:300-302) with no record (:630-631): it enters Holm at p = 1 (already the rule, :496-497), is
  not covered, is named in `not_covered` with its label (:577-580).
- Tests: tests/test_stage_e_verdict.py beside :597 (a by-design or untestable Tier A trial with
  no record is accepted, enters Holm at p = 1, is not covered; a plain Tier A trial with no
  record is still refused; an unknown label still refuses); tests/test_stage_e_runner.py (a
  declared-untestable member writes a not-run record and the cluster continues; an undeclared
  refusal still aborts).

**N5 (conditional: needed only if the lead's K is not 9).** `HOLM_K = 9` is a constant
(stage_e_verdict.py:76) and `parse_list` refuses any other `k_holm` (:338-339). E.22 A4 defines K
as the number of clusters with a non-empty Tier A (5 by the returns, section 5; 6 if the ML route
counts), V14 (b) fixes 9 until every cluster and the ML route have been screened, V21 proposes
10. A K other than 9 needs: `HOLM_K` replaced by a validated list field (1..9, the range
`holm_tier_a` accepts, stage_e_stats.py:317-320; 10 would also need `holm_alpha_k` changed), the
verdict echoing it, and tests/test_stage_e_verdict.py:653-655 re-pinned. Keeping K = 9 is the
stricter choice (alpha 0.05/9) and needs no change.

### NICE

- **R1 run-once marker in the harness:** a `--run-once-marker PATH` on the runner's
  confirmation `--all` path, refused if present, written with O_EXCL (0o444) after the preflight,
  the start-rule resolution of every member and the store existence/sha checks, and before
  `_load_frames`; on any later exception a STOPPED record (E.21 pattern, multiday/run.py:81-92,
  145-166). Without it, a shell `set -o noclobber` marker written before the command satisfies
  E.22 A5 with no harness change, but it cannot check that the inputs were ready first. Tests:
  a present marker refuses before any bar read; the marker is written after the preflight.
- **R2 no-bar-read dry run** (`--dry-run`): for every member of the cluster, resolve legs, S_X
  entries, price paths, store paths and their pinned sha256, release-calendar coverage, and print
  the expected supply, so an abort (section 6) is found before the marker (memory note "dry-run
  guards before registering").
- **R3 program N cross-check:** the verdict CLI checks `program_n` against
  `screening.trial_registry.current_n()` (screening/trial_registry.py:124-127) or records both.
- **R4 price-path cross-check:** the verdict compares each record's `price_path` with the list
  trial's declared path (new optional list field).
- **R5** if the lead wants by-design trials kept out of Holm/DSR/PBO when they have a record
  (section 5 note), that is a verdict-module change; the current code includes them.

### Not needed
- Engine, rules, costs, frozen tables, calendars, release calendar: the micro's cost model, tick
  value, q_c, eps and release rows all key on the vehicle root already (section 2 table); the
  release calendar covers 2019-05-01..2026-06-21 (`coverage`) with rows for every relevant root.
- Member freezes and member code: no change (keys stay MGC, MNQ, MES, MBT).
- K3 and K6: no code change; build their start-rule files, re-run research for power, then the
  confirmation, under whatever harness is current when they run (one version for run, list and
  verdict, section 5).

Sequencing implication: once v13 is committed, v12's preflight refuses (the manifest file
changes), so every Part A run, list and verdict after that uses v13; K3/K6 start-rule files built
earlier stay valid (the loader does not check a file's harness field, stage_e_start_dates.py:499-539).

---

## 9. Other items the lead will meet (not harness changes)

- **K3 FX table, R-A2-1:** K3's frozen FX_FULL_SESSIONS lists 14 dates (2022-01-17..2023-11-23)
  that v5 flattens at 11:30; "amend ... or keep it, before K3's confirmation" (E.5_RETURN.md:376-378,
  423-424). E.22 forbids member changes, so the lead logs "kept"; the harness flatten governs.
- **K6-limitcont-01 HE traded once in the research window** (E.8_RETURN.md:252); its screen t
  is 1.0018 (record `screen.t_daily`), the value one positive trade gives in 273 days
  (sqrt(273/272) = 1.0018). Expect a large n_b at the power check.
- **wkndbtc's MBT leg:** S_X 2024-01-02 from E.12's computation; supply <= 34 days (section 4).
  If its power check fails, D4 allows BTC only with the user's agreement and BTC is not owned:
  "inconclusive by design" or "untestable on owned data (BTC)", the lead's label (N4 if no record).
- **E.9's flagged facts:** "Frozen start rules (S_X) for MES as a Stage E leg, 6C, MNQ and MBT:
  the runner found none, so the power check could not run" (E.9_RETURN.md:273-275).
- **Detection alpha for K8:** `CLUSTER_MEMBER_COUNTS["K8"] = 3` (frozen E.1 recount,
  stage_e_stats_power.py:77-79) though the K8 freeze has 4 members; frozen, recorded as is.

## 10. Not determined (UNKNOWN), with what was checked

- The exact 3 MES rows (timestamps) behind E.12's TradeDateMismatch: not read (brief forbids
  reading parquet content); only the first label/booking pair is in the E.12 log and the
  count matches `in_scheduled_closure` = 3 in the D.1f build summary.
- Whether the MES Stage D parquet's `propexperiment.rolls` passes `splices_and_blackout`: not
  reached in E.12; the builder writes `rolls` with `ts_ns` (data/build_mes_bars.py:571;
  data/adapter.py:53-58).
- Current sha256 of the step 2 parquets: not hashed (reading file bytes was avoided); the
  bars_*.json records and E.12's `store_sha256` agree for every root checked, and the K4/K5
  start-rule `step2_sha256` values equal bars_MGC/MHG/MCL/NG records (MGC c5ed0b15..., MHG
  2eb65778..., MCL fb0cfb3f...). The confirmation loader re-checks the hash anyway.
- Whether the ML route counts toward D5's K (k_from_tiers `route_tested`): not checked.
- The actual supply and n_b of any E.22 member: requires the start-rule files and research re-runs.
