# Stage E.22 Part A: frozen facts for clusters K6 and K8

Read-only compilation. Sources: reports/E.8_RETURN.md, reports/E.9_RETURN.md, reports/stage_e_k6_member_freeze.json, reports/stage_e_k8_member_freeze.json, per-trial research records in reports/stage_e8_k6_screen/ and reports/stage_e9_k8_screen/ (JSON, field `screen`, `window_dates`, `coverage`, `labels`), reports/stage_e2a_epsilon.json and .md, reports/stage_e8_member_specs.md, reports/stage_e9_member_specs.md. No bar/parquet content was read.

## 1. Cluster freezes and code paths

| Cluster | Freeze file | sha256 of file (computed now with sha256sum) | Return statement | Commit | Created UTC |
|---|---|---|---|---|---|
| K6 | reports/stage_e_k6_member_freeze.json | a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 | reports/E.8_RETURN.md:8-10 ("cluster freeze a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604"), :111 (27 members OK) | 0a14a9a (E.8_RETURN.md:90) | 2026-10-01T08:58:09+00:00 |
| K8 | reports/stage_e_k8_member_freeze.json | 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 | reports/E.9_RETURN.md:9-10, :367-368 (4 members, 7 files) | 558a5dc (E.9_RETURN.md:9, :228) | 2026-10-02T06:39:20+00:00 |

Both file sha256 values match the returns exactly. Harness v6 sha256 in force: 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87 (E.8_RETURN.md:46; each record's harness_sha256). Release calendar sha256 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8 (record field release_calendar_sha256).

K6 member code (strategy/members/k6/, freeze `files`): __init__.py (0 B), _calendar.py (59654 B), _event_common.py (4061), _limits.py (4585), _port_common.py (5792), _wasde.py (3661), cp1.py (7944), cp2.py (6970), cp3.py (9547), crushgap.py (9431), limitcont.py (11127), wasdepost.py (4174), wasdepre.py (4401); plus strategy/members/__init__.py (0 B). Per-file sha256 are in the freeze JSON `files`.

K8 member code (strategy/members/k8/): __init__.py (0 B), _calendar.py (30150 B, 1e10dc29...), _releases.py (50543, 2acb8ab3...), flight.py (15667, 02005663...), oilcad.py (13028, b64db6b4...), wkndbtc.py (9031, 04847787...); plus strategy/members/__init__.py. Modules by member: flight.make_h30 / make_heod, oilcad.make_6c, wkndbtc.make_mnq (freeze `members`).

K6 test files named at E.8_RETURN.md:186-192: tests/test_k6_members_ports.py, _ports_cp2.py, _ports_cp3.py, _crushgap.py, _tables.py, _limitcont.py, _wasde.py. K8 tests (E.9_RETURN.md:212-215): tests/test_k8_members_tables.py, _flight.py, _flight_exits.py, _flight_engine.py, _oilcad.py, _wkndbtc.py (209 tests).

## 2. Common to all trials

- Window: research, 2025-04-01 onward (record `window`: research); `power` = not_run on every trial, reason StartRuleMissing: no frozen S_X (K6: E.8_RETURN.md:206-207; K8: E.9_RETURN.md:234-235; record field power.reason).
- Research-window n_b: NOT RECORDED anywhere I checked. `n_b` appears in no E.8/E.9 report or record; the power check that would compute it did not run (power.status not_run). UNKNOWN. (grep of reports/*.md and docs/*.md for the token n_b hits only D.1e/D.1f/E.2b/E.5/E.12 files, outside K6/K8 scope, and docs/prompts/STAGE_E.22.md A3.)
- Tier rule: D5 screen and OC-H, as cited by the returns (E.8_RETURN.md:182-189 region, now :321-328; E.9_RETURN.md:262). The exact D5 threshold was not read here; the record field `passes` is the runner's verdict (every `passes: true` has t > 1.0 in the data, every false has t < 1.0 or undefined). Tier B note in cluster file: "fails the D5 screen".
- q_c is 1 for every K6 and K8 trial (specs: stage_e8_member_specs.md:119-145 table; stage_e9_member_specs.md:82-87; load_frozen_tables().vehicles).
- eps: eps_operative ticks per contract per day from reports/stage_e2a_epsilon.json exposures[]; $/day = eps x tick_value_usd (derived by me, not recorded in the return). Recorded bar $/day (eps_translated x q_c x tick value) is in epsilon.json bar_usd_per_day / epsilon.md.

| Root | q_c | status | tick value $ | eps_translated | bar $/day (recorded) | eps_operative ticks | eps_operative $/day (derived) |
|---|---|---|---|---|---|---|---|
| ZC | 1 | undersized | 12.5 | 6 | 75.00 | 4 | 50.00 |
| ZW | 1 | chosen | 12.5 | 6 | 75.00 | 4 | 50.00 |
| ZS | 1 | chosen | 12.5 | 6 | 75.00 | 5 | 62.50 |
| ZM | 1 | chosen | 10.0 | 8 | 80.00 | 5 | 50.00 |
| ZL | 1 | chosen | 6.0 | 14 | 84.00 | 11 | 66.00 |
| HE | 1 | chosen | 10.0 | 8 | 80.00 | 7 | 70.00 |
| LE | 1 | chosen | 10.0 | 8 | 80.00 | 8 | 80.00 |
| MGC | 1 | chosen | 1.0 | 85 | 85.00 | 71 | 71.00 |
| 6C | 1 | undersized | 5.0 | 17 | 85.00 | 9 | 45.00 |
| MNQ | 1 | chosen | 0.5 | 170 | 85.00 | 170 | 85.00 |

DISCREPANCY to flag: reports/stage_e8_member_specs.md:34-35 states "LE 11" as operative eps, but reports/stage_e2a_epsilon.json (LE: eps_operative 8, eps_funnel 11) and epsilon.md row 24 ("eps operative 8 | eps funnel 11") give operative 8; 11 is the funnel figure. The specs line cites epsilon.md lines 28-34 and appears to have read the funnel column for LE. Whether the screen used eps is not applicable (eps_X affects only the later power check). E.9 specs use eps_operative via load_frozen_tables().eps_operative: MGC 71, 6C 9, MNQ 170 (stage_e9_member_specs.md:31-33; E.9_RETURN.md:176), consistent with the JSON.

## 3. K6: all 27 frozen trials (research window)

Source for trial/ordinal/factory/legs: freeze JSON `members`. Source for screen: record `screen`; output dir reports/stage_e8_k6_screen/; files K6_<member with spaces to underscores>_research.json and ..._research_trips.json; cluster file K6_research_cluster.json. Vehicle = traded root = record primary_vehicle. Labels from the record `labels` field are empty for every trial (runner wrote none; E.8_RETURN.md:243); lead-assigned labels are listed in section 5. Days = n_days; mean = net ticks per contract per day; t = daily t; closed trips = n_trips.

| Ord | Member id | Trial (member + root) | Module.factory | Legs (traded T / signal S) | q_c | eps ticks | Days | Mean | t | Trips | Tier (reason) | Record file |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K6-cp1-01 ZC | K6-cp1-01 ZC (root ZC) | cp1.make_zc | ZC T | 1 | 4 | 276 | -1.3932 | -6.013 | 265 | B: fails the D5 screen | K6_K6-cp1-01_ZC_research.json |
| 2 | K6-cp1-01 ZW | K6-cp1-01 ZW (root ZW) | cp1.make_zw | ZW T | 1 | 4 | 283 | -1.3931 | -4.334 | 269 | B: fails the D5 screen | K6_K6-cp1-01_ZW_research.json |
| 3 | K6-cp1-01 ZS | K6-cp1-01 ZS (root ZS) | cp1.make_zs | ZS T | 1 | 5 | 285 | -2.5301 | -5.756 | 280 | B: fails the D5 screen | K6_K6-cp1-01_ZS_research.json |
| 4 | K6-cp1-01 ZM | K6-cp1-01 ZM (root ZM) | cp1.make_zm | ZM T | 1 | 5 | 278 | -1.4134 | -3.820 | 270 | B: fails the D5 screen | K6_K6-cp1-01_ZM_research.json |
| 5 | K6-cp1-01 ZL | K6-cp1-01 ZL (root ZL) | cp1.make_zl | ZL T | 1 | 11 | 287 | -1.1361 | -1.235 | 271 | B: fails the D5 screen | K6_K6-cp1-01_ZL_research.json |
| 6 | K6-cp1-01 HE | K6-cp1-01 HE (root HE) | cp1.make_he | HE T | 1 | 7 | 273 | -1.7366 | -3.717 | 255 | B: fails the D5 screen | K6_K6-cp1-01_HE_research.json |
| 7 | K6-cp1-01 LE | K6-cp1-01 LE (root LE) | cp1.make_le | LE T | 1 | 8 | 266 | -1.6911 | -1.699 | 197 | B: fails the D5 screen | K6_K6-cp1-01_LE_research.json |
| 8 | K6-cp2-01 ZC | K6-cp2-01 ZC (root ZC) | cp2.make_zc | ZC T | 1 | 4 | 276 | -1.2369 | -2.414 | 247 | B: fails the D5 screen | K6_K6-cp2-01_ZC_research.json |
| 9 | K6-cp2-01 ZW | K6-cp2-01 ZW (root ZW) | cp2.make_zw | ZW T | 1 | 4 | 283 | -1.5501 | -2.014 | 265 | B: fails the D5 screen | K6_K6-cp2-01_ZW_research.json |
| 10 | K6-cp2-01 ZS | K6-cp2-01 ZS (root ZS) | cp2.make_zs | ZS T | 1 | 5 | 285 | -1.9418 | -1.803 | 272 | B: fails the D5 screen | K6_K6-cp2-01_ZS_research.json |
| 11 | K6-cp2-01 ZM | K6-cp2-01 ZM (root ZM) | cp2.make_zm | ZM T | 1 | 5 | 278 | -3.2959 | -3.458 | 262 | B: fails the D5 screen | K6_K6-cp2-01_ZM_research.json |
| 12 | K6-cp2-01 ZL | K6-cp2-01 ZL (root ZL) | cp2.make_zl | ZL T | 1 | 11 | 287 | -0.5481 | -0.262 | 276 | B: fails the D5 screen | K6_K6-cp2-01_ZL_research.json |
| 13 | K6-cp2-01 HE | K6-cp2-01 HE (root HE) | cp2.make_he | HE T | 1 | 7 | 273 | -3.6279 | -3.046 | 249 | B: fails the D5 screen | K6_K6-cp2-01_HE_research.json |
| 14 | K6-cp2-01 LE | K6-cp2-01 LE (root LE) | cp2.make_le | LE T | 1 | 8 | 266 | -4.2907 | -1.707 | 232 | B: fails the D5 screen | K6_K6-cp2-01_LE_research.json |
| 15 | K6-cp3-01 ZC | K6-cp3-01 ZC (root ZC) | cp3.make_zc | ZC T | 1 | 4 | 276 | -0.6851 | -1.123 | 135 | B: fails the D5 screen | K6_K6-cp3-01_ZC_research.json |
| 16 | K6-cp3-01 ZW | K6-cp3-01 ZW (root ZW) | cp3.make_zw | ZW T | 1 | 4 | 283 | -0.0791 | -0.084 | 131 | B: fails the D5 screen | K6_K6-cp3-01_ZW_research.json |
| 17 | K6-cp3-01 ZS | K6-cp3-01 ZS (root ZS) | cp3.make_zs | ZS T | 1 | 5 | 285 | -0.5618 | -0.475 | 136 | B: fails the D5 screen | K6_K6-cp3-01_ZS_research.json |
| 18 | K6-cp3-01 ZM | K6-cp3-01 ZM (root ZM) | cp3.make_zm | ZM T | 1 | 5 | 278 | +0.4725 | 0.495 | 119 | B: fails the D5 screen | K6_K6-cp3-01_ZM_research.json |
| 19 | K6-cp3-01 ZL | K6-cp3-01 ZL (root ZL) | cp3.make_zl | ZL T | 1 | 11 | 287 | -1.9353 | -0.723 | 143 | B: fails the D5 screen | K6_K6-cp3-01_ZL_research.json |
| 20 | K6-cp3-01 HE | K6-cp3-01 HE (root HE) | cp3.make_he | HE T | 1 | 7 | 273 | -2.4697 | -1.590 | 115 | B: fails the D5 screen | K6_K6-cp3-01_HE_research.json |
| 21 | K6-cp3-01 LE | K6-cp3-01 LE (root LE) | cp3.make_le | LE T | 1 | 8 | 266 | +1.5336 | 0.568 | 112 | B: fails the D5 screen | K6_K6-cp3-01_LE_research.json |
| 22 | K6-crushgap-01 ZS | K6-crushgap-01 ZS (root ZS) | crushgap.make_zs | ZS T, ZM S, ZL S | 1 | 5 | 264 | -3.4807 | -2.708 | 137 | B: fails the D5 screen | K6_K6-crushgap-01_ZS_research.json |
| 23 | K6-limitcont-01 HE | K6-limitcont-01 HE (root HE) | limitcont.make_he | HE T | 1 | 7 | 273 | +0.1869 | 1.002 | 1 | A: passes D5 (E.8_RETURN.md:14,17-20) | K6_K6-limitcont-01_HE_research.json |
| 24 | K6-limitcont-01 LE | K6-limitcont-01 LE (root LE) | limitcont.make_le | LE T | 1 | 8 | 266 | +0.0000 | undefined | 0 | B: 0 trips, t undefined; fails D5 | K6_K6-limitcont-01_LE_research.json |
| 25 | K6-wasdepre-01 ZC | K6-wasdepre-01 ZC (root ZC) | wasdepre.make_zc | ZC T | 1 | 4 | 276 | -0.4729 | -1.315 | 12 | B: fails the D5 screen | K6_K6-wasdepre-01_ZC_research.json |
| 26 | K6-wasdepre-01 ZS | K6-wasdepre-01 ZS (root ZS) | wasdepre.make_zs | ZS T | 1 | 5 | 285 | -0.7410 | -1.288 | 13 | B: fails the D5 screen | K6_K6-wasdepre-01_ZS_research.json |
| 27 | K6-wasdepost-01 ZC | K6-wasdepost-01 ZC (root ZC) | wasdepost.make_zc | ZC T | 1 | 4 | 276 | -0.1777 | -0.748 | 13 | B: fails the D5 screen | K6_K6-wasdepost-01_ZC_research.json |

Excluded trials: none. Refused: none. Not traded: K6-limitcont-01 LE (0 trips, E.8_RETURN.md:274). Status of all 27: run (E.8_RETURN.md:8-9,214-240). Window dates per record: first 2025-04-01, last 2026-06-15 (ZS, ZW, crushgap, wasdepre ZS) or 2026-06-17 (others); exclusions (roll_blackout_any_leg / UR-1) in each record's window_dates.excluded.

E.8_RETURN.md run table (lines 74-102) also records, per trial: min coverage, mean hold min, MLL liquidations (accounts restarted), D9.7 exits and entry refusals; read there rather than duplicated. Net-USD per trial is not in the return table; the per-record daily_net_usd list holds it.

### K6 Tier A list, quoted exactly

- E.8_RETURN.md:12-15: "| A | K6-limitcont-01 HE | 1 | +0.1869 | 1.002 |" and "| B | the other 26 (best: cp3 LE +1.53, t 0.57; cp3 ZM +0.47, t 0.50) | 0-280 | -4.29 to +1.53 | <= 0.57 |".
- E.8_RETURN.md:274: "**Tiers.** Tier A: K6-limitcont-01 HE. Tier B: the other 26. Excluded: none. Refused: none."
- E.8_RETURN.md:252-256 (the trial): "K6-limitcont-01 HE traded once: trade date 2025-04-07, sold at the 08:45 open after a limit-down close on 2025-04-04 as the D9.7 proxy shows it, closed at 10:24 CT by the engine's D9.7 forced exit, gross +53 ticks ($530), net $510.34 (51.03 ticks), hold 99 minutes. Mean 51.034 / 273 = +0.1869 ticks a day; t = 1.0018."

## 4. K8: all 4 frozen trials (research window)

Output dir reports/stage_e9_k8_screen/; files K8_<member_underscored>_research.json, ..._research_trips.json; cluster file K8_research_cluster.json. Labels: none on any trial (E.9_RETURN.md:244; records `labels` empty).

| Ord | Member id | Module.factory | Traded vehicle | Legs | q_c | eps ticks (eps $/day derived) | Days | Mean | t | Trips | Net USD (E.9_RETURN.md:239-242) | Coverage (record) | Window excluded (not-every-leg / roll / UR-1) | Tier |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K8-flight-01 H30 MGC | flight.make_h30 | MGC | MGC (traded), MES (signal only, no position) | 1 | 71 (71.00) | 280 | +4.2700 | 0.976 | 55 | +1,195.59 | MES 1.0000, MGC 0.9990 | 1 / 33 / 2 | B |
| 2 | K8-flight-01 HEOD MGC | flight.make_heod | MGC | MGC (traded), MES (signal only, no position) | 1 | 71 (71.00) | 280 | +10.6764 | 1.395 | 55 | +2,989.39 | MES 1.0000, MGC 0.9990 | 1 / 33 / 2 | A |
| 3 | K8-oilcad-01 6C | oilcad.make_6c | 6C | 6C (traded), MCL (signal only, no position) | 1 | 9 (45.00) | 255 | -4.4544 | -5.907 | 552 | -5,679.30 | 6C 0.9823, MCL 0.9985 | 1 / 60 / 0 | B |
| 4 | K8-wkndbtc-01 MNQ | wkndbtc.make_mnq | MNQ | MNQ (traded), MBT (signal only, no position) | 1 | 170 (85.00) | 250 | +28.9749 | 1.072 | 39 | +3,621.86 | MBT 0.9739, MNQ 0.9980 | 8 / 57 / 1 | A |

Window ends (record window_dates.last): H30 and HEOD 2026-06-12, oilcad 2026-06-16, wkndbtc 2026-06-12; first 2025-04-01. Mean hold min: H30 29.6, HEOD 292.3, oilcad 15.0, wkndbtc 1226.8; MLL liquidations: 0, 0, 2, 0 (E.9_RETURN.md:239-242). Signal legs: MES (flight; owned; research parquet sha256 aea959a5...), MCL (oilcad; V16(c)), MBT (wkndbtc), per stage_e9_member_specs.md:31-37. Note: the stage task says the K8-flight-01 signal is the MES leg, K8-oilcad-01 the MCL leg, K8-wkndbtc-01 the MBT leg; all confirmed by freeze `legs`.

### K8 Tier A list, quoted exactly

- E.9_RETURN.md:15-18: "| A | K8-flight-01 HEOD MGC | 55 | +10.676 | 1.395 |", "| A | K8-wkndbtc-01 MNQ | 39 | +28.975 | 1.072 |", "| B | K8-flight-01 H30 MGC | 55 | +4.270 | 0.976 |", "| B | K8-oilcad-01 6C | 552 | -4.454 | -5.907 |".
- E.9_RETURN.md:262-263: "**Task 7 (the result).** Tier A: K8-flight-01 HEOD MGC and K8-wkndbtc-01 MNQ. Tier B: K8-flight-01 H30 MGC and K8-oilcad-01 6C. Not traded, refused or unimplementable: none."

## 5. Labels

K6 (lead's labels, E.8_RETURN.md:243-250): 
- K6-cp2-01, all seven: "tick history not source-verified for the research window" (K6-L-16 item 13(a)).
- K6-limitcont-01 HE and LE: "limits are the frozen initial limits; expanded limits not encoded (K6-L-07)"; "settlements by the D9.7 proxy (one bar's close); official settlements not tested" (R-T3-2). LE also: "limit table partly contradicted by CME in the window (14 dates dropped)" (R-1b-2).
- K6-limitcont-01 HE: "Tier A on a single trip".
- Every K6 member: source-overlap (confirmation only). No member carries "calendar partly unverified".
K8: runner labels none (E.9_RETURN.md:244). wkndbtc is labelled source-overlap (E.9_RETURN.md:387; stage_e0_catalog_K8.md:836). No member carries "calendar partly unverified" (E.9_RETURN.md:208).

## 6. Open issues flagged for confirmation (quoted with file:line)

### K6 (reports/E.8_RETURN.md)
- :17-18 "**K6's Tier A rests on one trade:** a single positive day among 273 gives t = sqrt(273/272) = 1.002 whatever its size, so D5 passes it mechanically." Also :390-392 "K6-limitcont-01 HE is Tier A on one trade (t = 1.002 is arithmetic, not evidence). Run K6's confirmation with it as the Tier A member, or treat the screen's pass on a single trip as uninformative? Either way, D4's power check will probably call it inconclusive by design (C11)." Also :358-360 (open choice 14, "The one-trip Tier A stands ... D5 and OC-H have no minimum-trade rule").
- :393-394 "K6-L-06 and K6-L-07: limitcont runs on the D9.7 settlement proxy and the initial limit. Accept for confirmation, or buy the statistics schema (official settlements) and an expanded-limit table first?"
- :395-398 harness limit table differs from CME: "on LE 2026-06-01..06-18 (research window, $0.0725 vs $0.0850), and, between the confirmation window and the research window, on HE 2024-09-04..09-12 and LE 2024-10-09..10-24 (Task 1b B2). A harness fix (a new manifest version) or a recorded acceptance before any K6 confirmation?"
- :399 K6-L-01 (grain CP1's first bar). :400 "The ZS stop beyond the MLL at one contract". :401 "The tick and unit history (C7) over the confirmation window, owed before any K6 confirmation bar is read."
- :280-285 and :386-389 funding: "Step 2 history of ZC, ZW, ZS, ZM, ZL, HE and LE: quoted $26.52 on 2026-09-26 ... acct-2 holds $0.326239 ... top-up of about $26.19 at the quote, $28.85 at quote + 10% ... ACCOUNT_2_CAP_USD raised to at least $151.19 ($153.85). A fresh quote first. Also owed before a confirmation: the frozen start rule (S_X) for the seven roots (power is not_run), the tick and unit history over the confirmation window (C7), and a ruling on the limit-table periods 1b found wrong (section 7)."
- :19-20 one limit period dropped for LE 2026-06-01..06-18; :17 LE limitcont did not trade (0 trips).
- D9.7 effects: LE trials hit D9.7 often (:259-262); ZS D9.7 stop ~216 ticks ($2,700) beyond the $2,000 MLL (:267-268).
- No 'not permitted' wording found in E.8_RETURN.md or E.9_RETURN.md (grep -i 'not permitted|not allowed' returned nothing in either, nor in the two specs files). UNKNOWN beyond that.

### K8 (reports/E.9_RETURN.md)
- :20-21 "Both passes are thin: wkndbtc's t is 0.781 without 2026-06-08, its only post-24/7 trade; HEOD's is 1.085 without its best day, 0.751 without two."
- :380-383 (a) "**Tier A strength.** wkndbtc's pass rests on one Monday (2026-06-08; t 0.781 without it), its only trade after the 24/7 change; HEOD passes without its best day (1.085) but not its best two (0.751). D5 is frozen and both pass it (V18's minimum-trade concern does not apply at 39 and 55 trips), but neither is strong. Whether a K8 confirmation is worth funding is yours." Sensitivity at :312-314: HEOD best day 2026-04-02 (+849.9 ticks); wkndbtc 2026-06-08 (+2,267.6 ticks), t 0.477 without the top two.
- :384-388 (b) 24/7 regime: "The confirmation window lies wholly in the weekend-closure regime; deployment would lie wholly in the continuous one. Research window: 51 eligible Mondays before the change, 3 after (2026-06-01 and 06-15 were roll-blackout Mondays, so 1 traded). Is a confirmation on the old regime acceptable for wkndbtc? It is also labelled source-overlap: no edge could be claimed on it without a registered holdout read." Regime split: 38 trips before (+$2,488.06 net), 1 after (2026-06-08, +$1,133.80) (:255-256).
- :389-391 (c) "The runner found no frozen S_X for MES (as a Stage E leg), 6C, MNQ or MBT, so no power check ran. A confirmation session must build them first (MES's D.1f S = 2020-02-03 is the program's value; D4 says every leg starts at its own S)."
- :273-274 "wkndbtc's MBT history starts 2021-05, and the catalog expects 'inconclusive by design'." Catalog: reports/stage_e0_catalog_K8.md:185 "MBT: listed 2021-05-03, so it has no bars for 2019-05..2021-04."; :856-860 "MBT exists from 2021-05-03, and its start rule may move S later. The member will likely be 'inconclusive by design'. CME's full-size bitcoin futures (BTC, listed 2017-12) could serve as the signal leg for 2019-05..2021-04, but BTC is not in D13, so a quote would be needed."; docs/DECISIONS.md:316 "BTC reads MBT" (V16 context) and reports/stage_e9_member_specs.md:369 "MBT's short history: the start rule's, later (BTC only under D4's power clause and the user's agreement)".
- MES leg start: reports/stage_e0_catalog_K8.md:20, :173, :850-851 "MES's own start rule gave S = 2020-02-03"; E.9_RETURN.md:390; docs/DECISIONS.md:316 "(so an S&P leg starts 2020-02-03, D4)".
- :392-394 (d) earlier clusters' calendar tables: K3 FX 14 US-holiday dates 2022-2023, K4/K5 2024-07-03 (outside research window). :395-398 (e) MES's research-window roll blackouts were not on file before the run.
- :305-308 wkndbtc 2026-03-16 has no trip and no refusal (40 expected, 39 trips), accepted as not checkable.
- :376-379 funding: "6C, MNQ and MBT step 2 ($17.75 of the $29.65 K8 quote of 2026-09-26; MGC and MCL already bought) and an acct-2 top-up of about $17.42 ($19.20 with 10%); for the two Tier A trials only, MNQ and MBT ($10.70; top-up about $10.37, $11.44 with 10%), since HEOD needs no purchase." Quote detail: reports/stage_e2b_step2_quotes.md (MBT $3.11, line 28/62).

### Items asked for that I could NOT locate
- "BTC quoted free in E.1": UNKNOWN. Checked reports/E.1_RETURN.md (grep BTC|MNQ|MBT: only MNQ mbp-1 items at :230, :261, :273, :362), reports/E.2b_RETURN.md (BTC only at :419, :428: BTC has no D6 session record, a member that reads BTC is refused by name), reports/E.5_RETURN.md, reports/stage_e2b_step2_quotes.md (no BTC row; MBT $3.11 quoted), docs/DECISIONS.md (:316 only). No quote of BTC found.
- MNQ leg history notes (K8-wkndbtc traded leg): no short-history note found for MNQ; MNQ research parquet sha256 9506eace (stage_e9_member_specs.md:36-37); MNQ vehicle epsilon.md row 26 (K1, chosen, eps 170). MNQ step 2 not bought (E.9_RETURN.md:376-377).
- Research-window n_b: UNKNOWN (see section 2).
- eps_X $/day: not recorded in the returns; bar $/day recorded in epsilon.md/json; operative $/day is derived in section 2.

## 7. Other facts worth carrying
- Program N: K6 adds 27 -> 194 (E.8_RETURN.md:19-20,277-278); K8 adds 4 -> 198 (E.9_RETURN.md:19,265).
- Holdout: both returns report unlocks_logged 0 and REGISTRATION.md 0 bytes at start and end (E.8_RETURN.md:93-97; E.9_RETURN.md guardrail section).
- Verification: E.8 Part 2 item 1 screen recomputed 27 of 27 to 1e-9 (E.8_RETURN.md:321-328); E.9 Part 2 every screen recomputed, relative difference 0.0 (E.9_RETURN.md:257-259).
- Cluster result files: reports/stage_e8_k6_screen/K6_research_cluster.json (keys cluster, harness_sha256, members, not_tiered, power_check_undefined, refused_members, tiers, window); reports/stage_e9_k8_screen/K8_research_cluster.json.
- Specs/audit/rulings: reports/stage_e8_member_specs.md, _member_audit.md, _member_rulings.md; reports/stage_e9_member_specs.md, _member_audit.md, _member_rulings.md; release checks reports/stage_e8_release_check.md/.json and stage_e9_release_check.md/.json.
