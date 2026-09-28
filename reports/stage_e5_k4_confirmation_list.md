# Stage E.5 K4 confirmation list (hashed before any confirmation read)

STATUS: FROZEN at commit ("K4 confirmation list"). Written by the E.5 lead 2026-09-27T19:15:28-07:00 against the E.5 prompt,
before any bar of the confirmation window was read by any run. After the commit nothing in this file or its JSON changes.
The machine-read list is reports/stage_e5_k4_confirmation_list.json, sha256 **22388c6b3cbfb2b32809cba1ffbcd6a72ad6ff2b0bff0890474d80a65037d46c**; this file restates it for a reader (the JSON
governs where they differ). Shape after reports/stage_d1f_confirmation_list.md.

## 0. Provenance

- Harness: v6 9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87 (reports/stage_e2b_harness_freeze.json; the verdict code is screening/stage_e_verdict.py).
- Cluster freeze: reports/stage_e_k4_member_freeze.json, sha256 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a.
- Holm K = 9 (V14 b). Program N for DSR = 150 (E.4's final section; screened trials).
- Bootstrap: stationary, mean block 5.0, B = 10,000, a fresh generator per trial seeded 20260923 + list ordinal, np.quantile 0.95 (NULL_CRITERIA_E 3).
- Inputs and their sha256:
  - docs/DECISIONS.md: 1676d18b622802bf609dcb7994216642f93668044434ddc62bd271b823d0308c
  - docs/NULL_CRITERIA_E.md: b27ca69cf8f3ec411c0bc174b50c277e8b769e38f38581af171022ea3bef0cdd
  - docs/STAGE_E_DESIGN.md: 615bb1e14f9072b12f6a5c6206b463fc7828989ad0a9c8e463ebb301ea55103a
  - reports/stage_e2a_epsilon.json: 4e2c773182a23e7d073305ca4eb0134d3b3ac554ccc8215730bc1e194eaff496
  - reports/stage_e2a_source_window_amendment.md: 9fe401c1c156ebba38162256bf151d9888dec00e42cd24026d348d039e64f13d
  - reports/stage_e5_harness_plan.md: 11d234bb2a8ace9a83c0fb06ab108051fcf95594b79b77b0acf7dedee0029630
  - reports/stage_e5_ngs_check.json: ddfecb3e1575dc817aaeebc0f8795ebcbbbd10e78b4a936ec8b454d277706b44
  - reports/stage_e5_power_k4/K4_K4-apipre-01_MCL_research.json: 255b1a4b1bc9e3652d97d7e06251a761e6f67e3241bf8894b5b86da2f7a1bc35
  - reports/stage_e5_power_k4/K4_K4-cp1-01_MCL_research.json: 230d2df677455a83d5a4888a94d4c1b6992f1007b428603c1a67c348ca4f1b61
  - reports/stage_e5_power_k4/K4_K4-cp1-01_NG_research.json: 35fec585b9e805fb46b44e7394e61ae7addd3ad14c7b53bc4ff6afc680d44a79
  - reports/stage_e5_power_k4/K4_K4-cp2-01_MCL_research.json: 965e1f5d42a5235225e0f2c6192c257cd2819a0d71c284b96a84814dfcb4f60f
  - reports/stage_e5_power_k4/K4_K4-cp2-01_NG_research.json: 967ce75f7b0cd327ccecc4abc551f76ad9c70b07bc806de4d7a7b103798c077f
  - reports/stage_e5_power_k4/K4_K4-cp3-01_MCL_research.json: 18d831bd16cfc97aa725b916183d06d120817c79fe0124ba1e38e342e0ca6fa9
  - reports/stage_e5_power_k4/K4_K4-cp3-01_NG_research.json: 0df3063d987740e62bb8e029d0f6316f906d00d2b21f7f2a7427a683ccf52e8c
  - reports/stage_e5_power_k4/K4_K4-eiafade-01_MCL_research.json: 9a7ead6980acb455adcc91c5f6f9e0cba53aae3318c6f5a7af026419c792092c
  - reports/stage_e5_power_k4/K4_K4-eiamom-01_MCL_research.json: 94a1d2d7719a2a756b328d6aaf24cf90f5cc3b671ae1d1eff3b14e3b7d9206ca
  - reports/stage_e5_power_k4/K4_K4-ngpre-01_NG_research.json: 937cd2b14ee3248b52f0de56646ae07d3f3e245295dab6af02ea0db51163b787
  - reports/stage_e5_power_k4/K4_K4-ovr-01_MCL_research.json: 8022ad861b5671444aca7dc1ab245351ded7197824f2ec66d686938978349dc2
  - reports/stage_e5_power_k4/K4_K4-ovr-01_NG_research.json: bc361e001ddeb7f3d08ac245e8d22a9f06b03e0fbf2933de870bdc9b0e72daae
  - reports/stage_e_start_rule_K4.json: 523f2e25a7f5855901856c3b17a0eaf9fb8ddd1135526b03f80814f26bd34a6b

## 1. Windows (D4)

| Root | S_X | Confirmation window |
|---|---|---|
| MCL | 2021-07-12 | 2021-07-12..2024-02-29 |
| NG | 2019-05-06 | 2019-05-06..2024-02-29 |

Embargo (March 2024) and holdout-2 (2024-04-01..2025-03-31) sealed on arrival (reports/stage_e5_purchase.md); never read.

## 2. The frozen list

| Ord | Trial | Vehicle | q_c | eps_X ticks/ct/day ($/day at q_c) | Tier | Run | Labels | S_X | Seed | Power (supply, n_b, label) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K4-cp1-01 MCL | MCL | 4 | 21 ($84.00) | B | yes | source-overlap | MCL 2021-07-12 | 20260924 | 586, 27, power sufficient |
| 2 | K4-cp1-01 NG | NG | 1 | 8 ($80.00) | B | yes | source-overlap | NG 2019-05-06 | 20260925 | 1070, 58, power sufficient |
| 3 | K4-cp2-01 MCL | MCL | 4 | 21 ($84.00) | B | yes | source-overlap | MCL 2021-07-12 | 20260926 | 586, 49, power sufficient |
| 4 | K4-cp2-01 NG | NG | 1 | 8 ($80.00) | B | yes | source-overlap | NG 2019-05-06 | 20260927 | 1070, 130, power sufficient |
| 5 | K4-cp3-01 MCL | MCL | 4 | 21 ($84.00) | B | yes | source-overlap | MCL 2021-07-12 | 20260928 | 586, 97, power sufficient |
| 6 | K4-cp3-01 NG | NG | 1 | 8 ($80.00) | B | yes | source-overlap | NG 2019-05-06 | 20260929 | 1070, 209, power sufficient |
| 7 | K4-ngpre-01 NG | NG | 1 | 8 ($80.00) | A | yes | calendar partly unverified | NG 2019-05-06 | 20260930 | 1070, 94, power sufficient |
| 8 | K4-apipre-01 MCL | MCL | 4 | 21 ($84.00) | B | yes | source-overlap | MCL 2021-07-12 | 20260931 | 586, 15, power sufficient |
| 9 | K4-eiafade-01 MCL | MCL | 4 | 21 ($84.00) | B | yes | source-overlap | MCL 2021-07-12 | 20260932 | 586, 5, power sufficient |
| 10 | K4-eiamom-01 MCL | MCL | 4 | 21 ($84.00) | B | yes | source-overlap | MCL 2021-07-12 | 20260933 | 586, 1, power sufficient |
| 11 | K4-ovr-01 MCL | MCL | 4 | 21 ($84.00) | B | yes | source-overlap | MCL 2021-07-12 | 20260934 | 586, 53, power sufficient |
| 12 | K4-ovr-01 NG | NG | 1 | 8 ($80.00) | B | yes | source-overlap | NG 2019-05-06 | 20260935 | 1070, 91, power sufficient |

K4-ngpre-01's storage dates: the confirmation-window NGS rows were checked against EIA's record (reports/stage_e5_ngs_check.md);
five rows were dropped by C9's rule (lead ruling R-C3-1, the K4 C9 table amendment commit); unverifiable in the confirmation window: 0. The label "calendar partly unverified" comes from E.4's three unverifiable
research-window releases (2025-05-01, 2025-05-29, 2025-06-18).

## 3. Tests and decision rules (fixed now)

- **null.** NULL_CRITERIA_E 3: UCB95 < eps_X and Phi(eps_X / SE_boot - 1.645) >= 0.80; zero trips or SE_boot = 0 inconclusive; < 30 closed trips 'null by inactivity'; a trial labelled 'inconclusive by design' is not covered; OC-H-excluded trials are listed, not run, not covered (L-E5-5).
- **edge_chain.** D5 with V14: Holm over the Tier A one-sided p at 0.05 / K, K = 9 (V14 b); composite verdict pending, not built unless the rest passes (V14 a); DSR > 0.95 at program N with the Sharpe variance over Tier A, or over every run trial of the cluster when Tier A has one member (V14 c); daily t > 3.0 one-sided; CSCV PBO < 0.5 on 8 contiguous blocks over Tier A, or over every run trial when Tier A has one member (L-E5-3), aligned on the union of the run trials' window dates, zeros off each trial's dates.
- **wording.** A trial passing Holm, DSR, t and PBO reads 'edge candidate, composite pending', never 'edge'; a source-overlap trial adds 'no edge claim without a registered holdout read'.
- **code.** screening/stage_e_verdict.py under the harness sha256 above; one confirmation run per cluster.
- **Per trial reported:** theta_hat, UCB95, SE_boot, p_upper, n_days, closed trips, trips per day r, theta_hat / r, UCB95 / r,
  achieved null power Phi(eps_X / SE_boot - 1.645), the null status; for Tier A every edge-chain step.
- **Cluster statement:** NULL_CRITERIA_E 1 and 7 with the per-exposure resolution table.

## 4. Hashing record

The JSON was written first (sha256 above); this file embeds that hash and is hashed second; both hashes go into the commit
message "K4 confirmation list". The confirmation run (python -m screening.stage_e_runner --window confirmation) happens only
after that commit, once.
