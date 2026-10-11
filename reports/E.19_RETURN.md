# Stage E.19 return: prop economics, the Topstep Combine-to-XFA funnel in the user's wallet

Prompt docs/prompts/STAGE_E.19.md (V22, V31, V32). Lead Opus 5.5 xhigh, session 087ee4a8. All times PDT (America/Vancouver), 2026-10-10. Results: reports/stage_e19_results.md and .json.

## 1. Verdict summary

**No: at zero edge the Topstep funnel loses money for the user.** Inside the policy band (daily risk at most 0.25
of the drawdown distance), all 1,500 zero-edge configurations are negative: every size, path, pricing, DLL and Back2Funded choice and
sensitivity (a cycle: one subscription through its funded XFA).
Best case, 50K with Standard payout and pricing: **-$250 per cycle**, -$31 per Combine purchase. 100K loses $1,063
per cycle and 150K $2,696. It depends on costs (a gross edge just covering trading costs
and the $14.50/month API fee leaves 50K near break-even) and on sizing (sizing beyond the terms reaches break-even
at best).

**Break-even net Sharpe** (after costs, best sizing): 50K about 0, 100K 0.34 to 0.52, 150K 0.54 to 0.86. Zero gross edge is about
-0.5 net.

**Best setup:** 50K, Consistency path, DLL at purchase, Standard pricing, Back2Funded (keep-D payouts, tested
separately, add more). At a net Sharpe of 0.5 it makes +$906 per cycle (+$477 without Back2Funded).

**Cash targets** (five 50K accounts, Standard path; 50% / 80% probability):

| Target | Edge | Combine purchases | Fees |
|---|---|---|---|
| $5,000 withdrawn | zero | 112 / 164 | $7.9K / $11.5K |
| $5,000 withdrawn | net Sharpe 0.5 | 51 / 76 | $4.1K / $5.9K |
| $10,000 withdrawn | net Sharpe 0.5 | 86 / 121 | $6.9K / $9.5K |

**Risk of losing all fees:** at zero edge, 48% (Standard) to 74% (Consistency) of cycles pay nothing; at 0.5, 36% /
54%.

**Terms:** bots may trade the Combine and XFA via the API from the user's own machine, never a Live Funded account. Prohibited: account stacking, excessive Combine or Reset purchases, cross-account hedging, and full
size into news. No thresholds are published.

Fable reproduced the headline (0 BLOCKING). No purchase; N stays 480.

## 2. Guardrail evidence

No purchase and no Databento call (spend ledger 36,402 lines, sha256 034a454b..., the same at start and end); N = 480
at start and end (registry 4 lines, sha256 55b1d24c..., unchanged; nothing registered); holdouts all_ok with 0
unlocks at start and end; REGISTRATION.md 0 bytes; harness v12 preflight OK at start and end; no file under live/,
ops/, ml_route_v2/, rules/, sim/, screening/ or data/ code changed (git diff check in both blocks); no TopstepX or
ProjectX call, no credential, no key printed. End suite: 7,138 passed, 3 skipped, 3 xfailed, rc 0 (19:57:06 to 20:14:17, 17 min 11 s; `uv run pytest -q -p no:cacheprovider` at nice 10, PYTHONPYCACHEPREFIX unset; reports/stage_e19_briefs/pytest_end.out); the 148 prop_econ tests are new.

### Start checks (17:03), verbatim (untracked page lists collapsed)

```
$ date
Sat Oct 10 05:03:05 PM PDT 2026
$ git status --short
?? .claude/worktrees/
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e19_briefs/start_checks.txt)
?? reports/stage_e19_briefs/
$ git log --oneline -3
9d745e0 docs: Stage E.19 prompt (prop economics) and V32
4ba7171 Stage E.18 C1b evaluated
b714751 C1b freeze
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
preflight OK: ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 480 (4 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
r003-C1b: C1b ['C1b-T1', 'C1b-T2'] N 478 -> 480 at 2026-10-10T12:17:48-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
4
55b1d24c65d484186c4494294fdae03e374141eba5c3f210800d77e56e95289d
$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
tracked
no diff vs HEAD
1680982 
$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)
list sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e entries 43 mismatches ['reports/stage_e2b_harness_freeze.json']
$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
exit 0
$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md
exit 0
$ E.18 C1b freeze: uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
E.18 C1b freeze OK: 48 files, 10 external; manifest sha256 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
exit 0
$ git diff --quiet b714751 -- c1_replication/c1b.py tests/test_c1b.py reports/stage_e18_prereg_C1b.md reports/stage_e18_freeze.json
exit 0
$ git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops
exit 0
```

### End checks, verbatim (untracked page lists collapsed)

```
$ date
Sat Oct 10 08:14:40 PM PDT 2026
$ git status --short
 M .gitignore
 M docs/STAGES.md
?? .claude/worktrees/
?? prop_econ/
?? reports/stage_e12/e13/e14/e16_briefs page files: 639 lines (collapsed; full text in reports/stage_e19_briefs/end_checks.txt)
?? reports/stage_e19_STATE.md
?? reports/stage_e19_briefs/
?? reports/stage_e19_results.json
?? reports/stage_e19_results.md
?? reports/stage_e19_returns_summary.json
?? reports/stage_e19_returns_summary.md
?? reports/stage_e19_review.md
?? reports/stage_e19_review_rules.md
?? reports/stage_e19_rules.json
?? reports/stage_e19_rules.md
?? reports/stage_e19_rulings.md
?? reports/stage_e19_runs/
?? reports/stage_e19_verify/
?? tests/test_prop_econ_assemble.py
?? tests/test_prop_econ_fixtures.py
?? tests/test_prop_econ_funnel.py
?? tests/test_prop_econ_grid.py
?? tests/test_prop_econ_returns.py
?? tests/test_prop_econ_rules.py
?? tests/test_prop_econ_vec.py
$ git log --oneline -3
9d745e0 docs: Stage E.19 prompt (prop economics) and V32
4ba7171 Stage E.18 C1b evaluated
b714751 C1b freeze
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ python3 reports/stage_e2b_briefs/check_frozen.py
reports/stage_e1_freeze.json: manifest sha256 96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c files 32/32 match
reports/stage_e2a_ml_freeze.json: manifest sha256 077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2 files 4/4 match
ALL_OK
$ PYTHONPYCACHEPREFIX=<fresh> uv run python -m screening.harness_freeze verify --expected ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
preflight OK: ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
$ cluster freezes (load_cluster_freeze + verify_cluster_code)
K1 cluster freeze OK cf48f514dcf26490fa79a4322f764af991ee2555f2147354f12a31621fbe7ce2 11 members
K2 cluster freeze OK 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 44 members
K3 cluster freeze OK c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95 30 members
K4 cluster freeze OK 7abcde1705440e97efcf1ce255d979213eed9840f03a8383f2784a74f5f1534a 12 members
K5 cluster freeze OK 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655 11 members
K6 cluster freeze OK a6f8b497eee727688f3d0e9a3fc7af3abfe41c02f0354a55f5d918c01e61c604 27 members
K7 cluster freeze OK 46cae3082ae17cfd2a0e731cba27f6cc5dd2bdb94bb757d7ae48c684a5449462 6 members
K8 cluster freeze OK 99f5a6ce4f91fd63ae4a7dc91b5eb39ecbf8a7eac6f210b3472bf49eaf8463b7 4 members
$ ledger
36402 ledger/databento_spend.jsonl
034a454b49f2d9c93f3ff8872a5fb322cd351de57a7d73842d08f5d07d94c700
$ ledger total per account (SpendGate.account_spent_usd: external ledgers plus this repo's lines)
acct-1: spent 118.390020 cap 120.00 headroom 1.609980
acct-2: spent 353.455228 cap 355.38 headroom 1.924772
$ v2 freeze manifest (ml_route_v2.phase1.freeze.verify_v2_freeze)
v2 freeze OK: 91 files
$ uv run python -m screening.trial_registry status
N = 480 (4 lines)
r001-C1: C1 ['C1-T1', 'C1-T2'] N 471 -> 473 at 2026-10-09T19:29:06-07:00
r002-E16: E16 ['E16-H1', 'E16-H2', 'E16-H3', 'E16-H4', 'E16-H5'] N 473 -> 478 at 2026-10-10T00:30:15-07:00
r003-C1b: C1b ['C1b-T1', 'C1b-T2'] N 478 -> 480 at 2026-10-10T12:17:48-07:00
$ wc -l ledger/trial_registrations.jsonl; sha256sum
4
55b1d24c65d484186c4494294fdae03e374141eba5c3f210800d77e56e95289d
$ E.14 C1 freeze (reports/stage_e14_prereg_C1.md; pinned afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b): sha256, tracked, no diff vs HEAD, commits touching
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b
tracked
no diff vs HEAD
1680982 
$ E.14 C1 freeze inputs list (reports/stage_e14_c1_freeze_inputs.json; pinned 3356d676...)
list sha256 3356d67604245db99383215f1fb7f694d25a1beb71b0693a86faeb7243a5140e entries 43 mismatches ['reports/stage_e2b_harness_freeze.json']
$ E.16 freeze: uv run python reports/stage_e16_briefs/freeze_manifest.py verify --expected 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
E.16 freeze OK: 97 files; manifest sha256 5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4
exit 0
$ git diff --quiet 8f388c8 -- base_rules tests/test_base_rules_*.py reports/stage_e16_prereg_*.md
exit 0
$ E.18 C1b freeze: uv run python reports/stage_e18_briefs/freeze_manifest.py verify --expected 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
E.18 C1b freeze OK: 48 files, 10 external; manifest sha256 5ed208a21c2556e84830aca6fb7b2dba08a3012713f62de6e7bd1c57fb702d03
exit 0
$ git diff --quiet b714751 -- c1_replication/c1b.py tests/test_c1b.py reports/stage_e18_prereg_C1b.md reports/stage_e18_freeze.json
exit 0
$ git diff --quiet HEAD -- ml_route_v2 rules sim screening data/holdout.py live ops
exit 0
```

## 3. Results per task

Full results: reports/stage_e19_results.md (narrative, key numbers, and the machine tables T1-T8 with every grid
point) and reports/stage_e19_results.json (4,464 records). Model: reports/stage_e19_briefs/sim_spec.md and lead
decisions L-1..L-21 (section 6).

### Task 0: startup
Start checks at 17:03 passed (section 2). The lead wrote the binding model spec, the rules-JSON schema and the shared
interface (prop_econ/types.py) before any spawn.

### Task 1: rules and terms (TopstepRules-OpusHigh)
reports/stage_e19_rules.json and .md hold 214 rules from 41 Topstep help-centre and terms pages, fetched one at a
time by curl on 2026-10-10. Counts: 198 SOURCED, 6 INFERRED, 7 UNSOURCED, 3 CONFLICT; 42 prohibited or restricted
practices. Every quote is verbatim (validated by script, re-validated by Fable: 207/207 rules, 42/42 practices).
- The terms reading: ToU section 28 bans crawling and spidering; fetching named pages one by one is outside it (L-11,
  upheld by RulesReviewer).
- Changes from the earlier facts: Combine consistency is now "best day below 55% of total profit"; the Live Funded
  call-up is discretionary, closes all XFAs and transfers capped balances; the API costs $14.50/month; a VPS is not
  allowed; XFAs close after 30 days without trading.
- Key rules (value [source]; the UNSOURCED scaling boundary runs both readings):

| Rule | 50K | 100K | 150K |
|---|---|---|---|
| Combine monthly price, Standard / No Activation Fee pricing | 49.0 [S06] / 95.0 [S06] | 99.0 [S06] / 149.0 [S06] | 199.0 [S06] / 229.0 [S06] |
| Reset price, Standard / NAF | 49.0 [S06] / 95.0 [S06] | 99.0 [S06] / 149.0 [S06] | 199.0 [S06] / 229.0 [S06] |
| Profit target | 3000.0 [S13] | 6000.0 [S13] | 9000.0 [S13] |
| Combine MLL (EOD trailing; locks at start balance) | 2000.0 [S11] / 0.0 [S11] | 3000.0 [S11] / 0.0 [S11] | 4500.0 [S11] / 0.0 [S11] |
| Combine consistency: best day max share of total profit | 0.55 [S13] | 0.55 [S13] | 0.55 [S13] |
| Minimum trading days | 2 [S07] | 2 [S07] | 2 [S07] |
| Max position (minis) | 5 [S07] | 10 [S07] | 15 [S07] |
| Optional DLL (both phases, chosen at purchase) | 1000.0 [S12] | 2000.0 [S12] | 3000.0 [S12] |
| Activation fee, Standard / NAF | 149.0 [S06] / 0.0 [S06] | 149.0 [S06] / 0.0 [S06] | 149.0 [S06] / 0.0 [S06] |
| XFA MLL (EOD trailing, locks at $0) / after the 1st payout | 2000.0 [S11] / 0.0 [S11] | 3000.0 [S11] / 0.0 [S11] | 4500.0 [S11] / 0.0 [S11] |
| Standard path: winning days x minimum | 5 [S17] / 150.0 [S17] | 5 [S17] / 150.0 [S17] | 5 [S17] / 150.0 [S17] |
| Standard path cap / with DLL | 2000.0 [S17] / 4000.0 [S17] | 3000.0 [S17] / 6000.0 [S17] | 5000.0 [S17] / 10000.0 [S17] |
| Consistency path: days / best-day max share | 3 [S17] / 0.4 [S17] | 3 [S17] / 0.4 [S17] | 3 [S17] / 0.4 [S17] |
| Consistency path cap / with DLL | 3000.0 [S17] / 6000.0 [S17] | 4000.0 [S17] / 8000.0 [S17] | 6000.0 [S17] / 12000.0 [S17] |
| Payout max share of balance | 0.5 [S17] | 0.5 [S17] | 0.5 [S17] |
| Back2Funded price / max per XFA | 599.0 [S18] / 2 [S18] | 699.0 [S18] / 2 [S18] | 829.0 [S18] / 2 [S18] |
| Scaling plan first tier (minis) / boundary reading | 2 [S40] / lower (UNSOURCED) [None] | 3 [S40] / lower (UNSOURCED) [None] | 3 [S40] / lower (UNSOURCED) [None] |

| Rule (all sizes) | Value |
|---|---|
| Profit split to trader | 0.9 [S17] |
| Minimum payout | 125.0 [S17] |
| Max active XFAs | 5 [S14] |
| Billing period (calendar days) | 30 [S08] |
| Rebill adds a reset credit | True [S09] |
| Live Funded call-up | discretionary [S19] |
| Automated trading allowed (Combine, XFA) | True [S26] |
| VPS allowed | False [S26] |
| Cross-account hedging allowed | False [S21] |
| API access per month | 14.5 [S26] |

### Task 2: simulator (FunnelCoder-OpusXHigh)
prop_econ/rules.py (loader with reading overrides), funnel.py (the scalar reference), vec.py (vectorized; equal to the
scalar path for path) and assemble.py (fees, rebills, credits, resets, activation, Back2Funded, cycles, campaigns).
- 117 tests pin the hand-computed paths the prompt names: a pass then a payout, a fail and reset, a drawdown lock, a
  payout under each path, and the five-account cap. 148 prop_econ tests in all.
- Speed: 20,000 XFAs x 756 days in 0.3 to 0.6 s.
- GridCoder-OpusHigh added grid.py (the 780-job grid, resumable, seeded with common random numbers) and report.py
  (the aggregator).

### Task 3: return models (lead, with ReturnsCoder-OpusHigh)
Day-session holds from the owned E.12 training stores, read for return magnitudes only. Each path is demeaned, so
zero edge has exactly zero gross drift; the direction is a fair coin each day; draws are 5-day block bootstrap blocks
pooled over the five paths, against a normal comparison. The EconReviewer rebuilt this table independently: it
matches to 1e-9, with a mean of 0.

| Path | Window CT | Dates | Kept | Skips (none/roll/open/close) | Mean r removed $ | sigma_full $ | sigma_micro $ | skew | ex. kurt | share abs z>4 | w_L mean / p01 | w_S mean / p01 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NQ | 08:30-15:00 | 1248 | 1205 | 2/0/0/41 | 102.15 | 2999.10 | 299.91 | -0.239 | 1.869 | 0.0008 | -0.716 / -3.281 | -0.679 / -2.532 |
| CL | 08:00-13:30 | 1246 | 1220 | 1/0/0/25 | -44.04 | 1395.80 | 139.58 | -0.966 | 5.630 | 0.0066 | -0.731 / -3.601 | -0.645 / -2.783 |
| GC | 07:20-12:30 | 1246 | 1214 | 0/0/9/23 | -9.94 | 1224.60 | 122.46 | -0.312 | 2.611 | 0.0016 | -0.764 / -3.607 | -0.715 / -3.158 |
| ZN | 07:20-14:00 | 1248 | 1203 | 0/0/6/39 | -21.79 | 368.06 | - | -0.124 | 2.868 | 0.0025 | -0.725 / -3.354 | -0.678 / -3.181 |
| 6E | 07:20-14:00 | 1248 | 1222 | 0/0/0/26 | 0.73 | 470.19 | 47.02 | 0.495 | 3.347 | 0.0049 | -0.730 / -2.989 | -0.735 / -3.108 |

Costs: the D8 round trip per contract, 1 or 3 per day. Measured on the vehicles actually traded, zero gross edge is
a net Sharpe of about -0.5 at one round trip a day and -1.5 at three. Edges S are net of costs.

### Task 4: results (lead)
Key numbers (headline configuration at each rule set's best band f; API fee included; B2F = Back2Funded):

| size | path | DLL | edge | best band f | cycle net (SE) | net ex API | P(no payout) | P(pass) | net per purchase | per funded XFA | purchases | cycle days | days to 1st payout | B2F on: net | break-even S (best f) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 50K | standard | off | zero_k1 | 0.25 | -250 (7) | -94 | 0.482 | 0.175 | -31 | 298 | 8.1 | 216 | 204 | -373 (9) | 0.02 |
| 50K | standard | off | S0.5 | 0.25 | 278 (13) | 387 | 0.360 | 0.307 | 52 | 637 | 5.3 | 148 | 131 | 358 (15) | 0.02 |
| 50K | standard | on | zero_k1 | 0.25 | -273 (8) | -108 | 0.474 | 0.175 | -32 | 305 | 8.5 | 230 | 217 | -358 (10) | 0.04 |
| 50K | standard | on | S0.5 | 0.25 | 249 (12) | 363 | 0.345 | 0.312 | 45 | 632 | 5.5 | 155 | 138 | 344 (14) | 0.04 |
| 50K | consistency | off | zero_k1 | 0.25 | -283 (8) | -120 | 0.741 | 0.175 | -35 | 267 | 8.1 | 226 | 209 | -554 (12) | < 0 |
| 50K | consistency | off | S0.5 | 0.20 | 391 (15) | 538 | 0.537 | 0.325 | 61 | 863 | 6.4 | 204 | 170 | 692 (19) | < 0 |
| 50K | consistency | on | zero_k1 | 0.25 | -307 (9) | -133 | 0.745 | 0.175 | -36 | 279 | 8.5 | 242 | 224 | -494 (13) | < 0 |
| 50K | consistency | on | S0.5 | 0.25 | 477 (17) | 608 | 0.594 | 0.312 | 86 | 875 | 5.5 | 181 | 150 | 906 (23) | < 0 |
| 100K | standard | off | zero_k1 | 0.25 | -1,063 (13) | -811 | 0.434 | 0.130 | -81 | 486 | 13.2 | 356 | 340 | -1,111 (15) | 0.52 |
| 100K | standard | off | S0.5 | 0.25 | -25 (17) | 134 | 0.310 | 0.254 | -3 | 923 | 8.1 | 221 | 199 | 117 (18) | 0.52 |
| 100K | standard | on | zero_k1 | 0.25 | -1,128 (14) | -864 | 0.432 | 0.128 | -82 | 489 | 13.8 | 372 | 356 | -1,143 (15) | 0.57 |
| 100K | standard | on | S0.5 | 0.25 | -83 (15) | 84 | 0.307 | 0.254 | -10 | 911 | 8.5 | 231 | 209 | 78 (17) | 0.57 |
| 100K | consistency | off | zero_k1 | 0.25 | -1,098 (14) | -836 | 0.734 | 0.130 | -83 | 455 | 13.2 | 370 | 349 | -1,263 (18) | 0.34 |
| 100K | consistency | off | S0.5 | 0.25 | 263 (21) | 440 | 0.584 | 0.254 | 32 | 1,208 | 8.1 | 247 | 213 | 825 (26) | 0.34 |
| 100K | consistency | on | zero_k1 | 0.25 | -1,142 (15) | -868 | 0.737 | 0.128 | -83 | 488 | 13.8 | 387 | 365 | -1,201 (20) | 0.31 |
| 100K | consistency | on | S0.5 | 0.25 | 344 (24) | 532 | 0.587 | 0.254 | 40 | 1,355 | 8.5 | 262 | 224 | 1,096 (31) | 0.31 |
| 150K | standard | off | zero_k1 | 0.25 | -2,696 (26) | -2,397 | 0.412 | 0.128 | -169 | 777 | 15.9 | 423 | 403 | -2,664 (27) | 0.86 |
| 150K | standard | off | S0.5 | 0.25 | -697 (26) | -513 | 0.286 | 0.257 | -73 | 1,386 | 9.5 | 257 | 231 | -461 (27) | 0.86 |
| 150K | standard | on | zero_k1 | 0.25 | -2,878 (27) | -2,563 | 0.410 | 0.126 | -171 | 779 | 16.8 | 446 | 425 | -2,814 (29) | 0.90 |
| 150K | standard | on | S0.5 | 0.25 | -795 (23) | -604 | 0.282 | 0.260 | -80 | 1,371 | 9.9 | 267 | 240 | -548 (25) | 0.90 |
| 150K | consistency | off | zero_k1 | 0.25 | -2,701 (28) | -2,390 | 0.736 | 0.128 | -170 | 778 | 15.9 | 441 | 407 | -2,659 (33) | 0.54 |
| 150K | consistency | off | S0.5 | 0.25 | -131 (33) | 75 | 0.577 | 0.257 | -14 | 1,967 | 9.5 | 289 | 244 | 939 (41) | 0.54 |
| 150K | consistency | on | zero_k1 | 0.25 | -2,840 (30) | -2,512 | 0.738 | 0.126 | -169 | 833 | 16.8 | 465 | 430 | -2,666 (36) | 0.49 |
| 150K | consistency | on | S0.5 | 0.25 | 18 (39) | 235 | 0.578 | 0.260 | 2 | 2,213 | 9.9 | 305 | 255 | 1,390 (49) | 0.49 |

Zero edge, every band f (DLL off, standard pricing, Back2Funded off): cycle mean net

| size | path | f 0.05 | f 0.10 | f 0.15 | f 0.20 | f 0.25 | f 0.35 (diag) | f 0.50 (diag) | best band f gap to runner-up (paired SE) |
|---|---|---|---|---|---|---|---|---|---|
| 50K | standard | -1,089 | -953 | -710 | -452 | -250 | -72 | -30 | 0.25 vs 0.20: 202 (4) |
| 50K | consistency | -1,092 | -941 | -702 | -449 | -283 | -172 | -161 | 0.25 vs 0.20: 166 (5) |
| 100K | standard | -9,998 | -6,492 | -3,575 | -1,900 | -1,063 | -420 | -260 | 0.25 vs 0.20: 837 (12) |
| 100K | consistency | -9,934 | -6,399 | -3,497 | -1,869 | -1,098 | -578 | -496 | 0.25 vs 0.20: 771 (13) |
| 150K | standard | -52,841 | -20,238 | -8,989 | -4,762 | -2,696 | -1,050 | -718 | 0.25 vs 0.20: 2,066 (27) |
| 150K | consistency | -52,686 | -20,048 | -8,825 | -4,664 | -2,701 | -1,262 | -1,067 | 0.25 vs 0.20: 1,962 (28) |

Break-even net Sharpe (T3; linear interpolation over S; '< 0' means positive already at S = 0):

| size | path | DLL | pricing | f 0.05 | f 0.10 | f 0.15 | f 0.20 | f 0.25 | f 0.35 | f 0.50 | best band f |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 50K | standard | off | standard | 0.72 | 0.64 | 0.49 | 0.26 | 0.02 | < 0 | < 0 | 0.02 |
| 50K | standard | off | no_activation_fee | > 1 | 0.90 | 0.73 | 0.49 | 0.23 | < 0 | < 0 | 0.23 |
| 50K | standard | on | standard | 0.75 | 0.67 | 0.52 | 0.31 | 0.04 | < 0 | < 0 | 0.04 |
| 50K | standard | on | no_activation_fee | 0.95 | 0.85 | 0.68 | 0.45 | 0.19 | < 0 | < 0 | 0.19 |
| 50K | consistency | off | standard | 0.42 | 0.33 | 0.22 | 0.11 | < 0 | < 0 | 0.02 | < 0 |
| 50K | consistency | off | no_activation_fee | 0.65 | 0.53 | 0.42 | 0.29 | 0.18 | 0.09 | 0.18 | 0.18 |
| 50K | consistency | on | standard | 0.45 | 0.33 | 0.23 | 0.09 | < 0 | < 0 | 0.04 | < 0 |
| 50K | consistency | on | no_activation_fee | 0.61 | 0.49 | 0.36 | 0.22 | 0.10 | 0.00 | 0.15 | 0.10 |
| 100K | standard | off | standard | > 1 | > 1 | > 1 | 0.84 | 0.52 | 0.08 | < 0 | 0.52 |
| 100K | standard | off | no_activation_fee | > 1 | > 1 | > 1 | > 1 | 0.71 | 0.27 | 0.18 | 0.71 |
| 100K | standard | on | standard | > 1 | > 1 | > 1 | 0.87 | 0.57 | 0.05 | < 0 | 0.57 |
| 100K | standard | on | no_activation_fee | > 1 | > 1 | > 1 | 0.96 | 0.66 | 0.13 | < 0 | 0.66 |
| 100K | consistency | off | standard | > 1 | 0.83 | 0.61 | 0.47 | 0.34 | 0.25 | 0.37 | 0.34 |
| 100K | consistency | off | no_activation_fee | > 1 | > 1 | 0.76 | 0.62 | 0.50 | 0.40 | 0.52 | 0.50 |
| 100K | consistency | on | standard | > 1 | 0.83 | 0.59 | 0.43 | 0.31 | 0.16 | 0.28 | 0.31 |
| 100K | consistency | on | no_activation_fee | > 1 | 0.92 | 0.67 | 0.51 | 0.38 | 0.22 | 0.37 | 0.38 |
| 150K | standard | off | standard | > 1 | > 1 | > 1 | > 1 | 0.86 | 0.33 | 0.22 | 0.86 |
| 150K | standard | off | no_activation_fee | > 1 | > 1 | > 1 | > 1 | 0.90 | 0.36 | 0.25 | 0.90 |
| 150K | standard | on | standard | > 1 | > 1 | > 1 | > 1 | 0.90 | 0.32 | 0.06 | 0.90 |
| 150K | standard | on | no_activation_fee | > 1 | > 1 | > 1 | > 1 | 0.83 | 0.24 | 0.02 | 0.83 |
| 150K | consistency | off | standard | > 1 | > 1 | 0.77 | 0.63 | 0.54 | 0.41 | 0.58 | 0.54 |
| 150K | consistency | off | no_activation_fee | > 1 | > 1 | 0.81 | 0.68 | 0.58 | 0.43 | 0.58 | 0.58 |
| 150K | consistency | on | standard | > 1 | > 1 | 0.76 | 0.60 | 0.49 | 0.36 | 0.47 | 0.49 |
| 150K | consistency | on | no_activation_fee | > 1 | > 1 | 0.73 | 0.57 | 0.45 | 0.29 | 0.40 | 0.45 |

Campaigns to $5,000 and $10,000 of withdrawn cash (T4, five slots, best band f, DLL and Back2Funded off, API in):

| edge | size | path | pricing | best f | churn (purch/21 Combine d) | slots | $5k not reached | $5k purchases P50/P80 | $5k fees P50/P80 | $5k days P50/P80 | $10k not reached | $10k purchases P50/P80 | $10k fees P50/P80 | $10k days P50/P80 | $5k purchases per 21 elapsed d (reached) | low-churn best f: $5k purch P50/P80 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zero_k1 | 50K | standard | standard | 0.25 | low (0.90) | 5 | 0.000 | 112 / 164 | 7,918 / 11,499 | 570 / 845 | 0.018 | 202 / 276 | 14,366 / 19,390 | 1,055 / 1,439 | 4.15 | 0.25: 112 / 164 |
| zero_k1 | 50K | consistency | standard | 0.25 | low (0.90) | 5 | 0.004 | 123 / 192 | 8,720 / 13,480 | 656 / 1,029 | 0.065 | 220 / 313 | 15,652 / 22,096 | 1,193 / 1,706 | 3.97 | 0.25: 123 / 192 |
| zero_k1 | 100K | standard | standard | 0.25 | low (0.86) | 5 | 0.006 | 133 / 206 | 15,114 / 23,168 | 687 / 1,071 | 0.096 | 239 / 339 | 27,248 / 38,472 | 1,260 / 1,794 | 4.10 | 0.25: 133 / 206 |
| zero_k1 | 100K | consistency | standard | 0.25 | low (0.86) | 5 | 0.026 | 144 / 237 | 16,362 / 26,845 | 770 / 1,281 | 0.167 | 255 / 380 | 29,110 / 43,172 | 1,394 / 2,075 | 3.95 | 0.25: 144 / 237 |
| zero_k1 | 150K | standard | standard | 0.25 | low (0.87) | 5 | 0.004 | 112 / 183 | 23,816 / 38,658 | 572 / 941 | 0.054 | 199 / 297 | 42,200 / 62,838 | 1,032 / 1,545 | 4.18 | 0.25: 112 / 183 |
| zero_k1 | 150K | consistency | standard | 0.25 | low (0.87) | 5 | 0.023 | 123 / 218 | 26,103 / 45,981 | 651 / 1,159 | 0.119 | 209 / 338 | 44,278 / 71,489 | 1,126 / 1,824 | 4.03 | 0.25: 123 / 218 |
| S0.3 | 50K | standard | standard | 0.25 | low (0.97) | 5 | 0.000 | 59 / 88 | 4,600 / 6,764 | 297 / 447 | 0.000 | 101 / 141 | 7,881 / 10,866 | 524 / 732 | 4.22 | 0.25: 59 / 88 |
| S0.3 | 50K | consistency | standard | 0.25 | low (0.97) | 5 | 0.000 | 57 / 88 | 4,424 / 6,800 | 305 / 476 | 0.000 | 94 / 137 | 7,390 / 10,580 | 530 / 762 | 3.95 | 0.25: 57 / 88 |
| S0.3 | 100K | standard | standard | 0.25 | low (0.92) | 5 | 0.000 | 68 / 106 | 8,084 / 12,411 | 341 / 535 | 0.000 | 116 / 170 | 13,907 / 19,944 | 602 / 875 | 4.24 | 0.25: 68 / 106 |
| S0.3 | 100K | consistency | standard | 0.25 | low (0.92) | 5 | 0.000 | 64 / 106 | 7,626 / 12,456 | 341 / 567 | 0.000 | 105 / 160 | 12,562 / 18,946 | 583 / 879 | 4.01 | 0.25: 64 / 106 |
| S0.3 | 150K | standard | standard | 0.25 | low (0.92) | 5 | 0.000 | 58 / 96 | 12,639 / 20,680 | 288 / 482 | 0.000 | 98 / 148 | 21,141 / 31,911 | 500 / 758 | 4.33 | 0.25: 58 / 96 |
| S0.3 | 150K | consistency | standard | 0.25 | low (0.92) | 5 | 0.000 | 55 / 95 | 11,878 / 20,410 | 288 / 503 | 0.000 | 87 / 140 | 18,808 / 30,204 | 474 / 763 | 4.11 | 0.25: 55 / 95 |
| S0.5 | 50K | standard | standard | 0.25 | low (0.98) | 5 | 0.000 | 51 / 76 | 4,052 / 5,934 | 255 / 383 | 0.000 | 86 / 121 | 6,900 / 9,530 | 449 / 628 | 4.24 | 0.25: 51 / 76 |
| S0.5 | 50K | consistency | standard | 0.20 | low (0.96) | 5 | 0.000 | 55 / 83 | 4,119 / 6,162 | 304 / 460 | 0.000 | 87 / 127 | 6,646 / 9,494 | 508 / 727 | 3.81 | 0.20: 55 / 83 |
| S0.5 | 100K | standard | standard | 0.25 | low (0.93) | 5 | 0.000 | 58 / 90 | 6,987 / 10,720 | 289 / 455 | 0.000 | 97 / 142 | 11,774 / 16,964 | 502 / 734 | 4.28 | 0.25: 58 / 90 |
| S0.5 | 100K | consistency | standard | 0.25 | low (0.93) | 5 | 0.000 | 53 / 87 | 6,395 / 10,288 | 283 / 462 | 0.000 | 85 / 131 | 10,268 / 15,668 | 474 / 723 | 4.03 | 0.25: 53 / 87 |
| S0.5 | 150K | standard | standard | 0.25 | low (0.93) | 5 | 0.000 | 50 / 83 | 10,982 / 17,934 | 247 / 412 | 0.000 | 83 / 127 | 18,077 / 27,610 | 423 / 651 | 4.37 | 0.25: 50 / 83 |
| S0.5 | 150K | consistency | standard | 0.25 | low (0.93) | 5 | 0.000 | 46 / 79 | 10,108 / 17,153 | 242 / 420 | 0.000 | 71 / 115 | 15,548 / 24,937 | 392 / 629 | 4.13 | 0.25: 46 / 79 |
| S1 | 50K | standard | standard | 0.25 | low (1.03) | 5 | 0.000 | 36 / 53 | 3,036 / 4,409 | 179 / 266 | 0.000 | 58 / 82 | 4,920 / 6,894 | 303 / 427 | 4.27 | 0.25: 36 / 53 |
| S1 | 50K | consistency | standard | 0.15 | low (1.00) | 5 | 0.000 | 43 / 63 | 3,268 / 4,674 | 243 / 348 | 0.000 | 63 / 90 | 4,850 / 6,797 | 382 / 528 | 3.75 | 0.15: 43 / 63 |
| S1 | 100K | standard | standard | 0.25 | low (0.97) | 5 | 0.000 | 40 / 62 | 4,972 / 7,548 | 196 / 306 | 0.000 | 64 / 94 | 8,008 / 11,539 | 329 / 480 | 4.35 | 0.25: 40 / 62 |
| S1 | 100K | consistency | standard | 0.20 | low (0.98) | 5 | 0.000 | 41 / 64 | 4,950 / 7,512 | 221 / 340 | 0.000 | 59 / 89 | 7,195 / 10,634 | 342 / 501 | 3.97 | 0.20: 41 / 64 |
| S1 | 150K | standard | standard | 0.25 | low (0.97) | 5 | 0.000 | 34 / 56 | 7,628 / 12,226 | 165 / 272 | 0.000 | 53 / 82 | 11,878 / 17,999 | 272 / 416 | 4.47 | 0.25: 34 / 56 |
| S1 | 150K | consistency | standard | 0.20 | low (0.98) | 5 | 0.000 | 37 / 59 | 8,118 / 12,768 | 196 / 312 | 0.000 | 52 / 80 | 11,246 / 17,296 | 290 / 442 | 4.11 | 0.20: 37 / 59 |

Sensitivities (T5; details in the results md, section 4):
- Normal tails make zero edge $34 to $230 less negative.
- A long-only direction is $31 to $325 worse.
- The cost wall is $36 to $975 worse.
- Integer single-product contracts are much worse for 6E, CL and GC.
- Keep-D payouts are better with any edge (+$209 at 50K Standard, net Sharpe 0.5).
- A call-up after the first payout costs $132 to $1,048 per cycle.
- The UNSOURCED scaling boundary and the CONFLICT consistency boundary have no effect.
- ACH payouts cost $10 to $42 per cycle.
- Copy-trading five accounts multiplies results by about five, but trips the Responsible Trading Program.

No sensitivity turns zero edge positive inside the band.

### Task 5: review (RulesReviewer-FableXHigh, EconReviewer-FableXHigh)
Section 5.

## 4. Delegation record

One row per spawn (six spawns; at most three ran at once). Tokens: input + output + cache read + cache creation from each transcript (reports/stage_e10_briefs/cost.py, per-field final usage per message).

| Agent (description) | Agent file | Model | Effort | Start | End | Tokens (transcript) | Status, deviations |
|---|---|---|---|---|---|---|---|
| TopstepRules-OpusHigh | worker-high | opus (claude-opus-5-5) | high | 17:09 | 17:24 | 10,488,168 | done; 214 rules, 42 practices; terms reading L-11 |
| FunnelCoder-OpusXHigh | worker-xhigh | opus (claude-opus-5-5) | xhigh | 17:09 | 17:41 | 11,526,887 | done; 117 tests; one lead message 17:24 (final-rules facts) |
| ReturnsCoder-OpusHigh | worker-high | opus (claude-opus-5-5) | high | 17:09 | 17:15 | 2,653,369 | done; 15 tests; 4 spec questions (L-10) |
| GridCoder-OpusHigh | worker-high | opus (claude-opus-5-5) | high | 17:43 | 19:26 | 11,385,402 | done; run restarted 18:02 to add churn metrics (RR-1); 780 jobs, 0 failures |
| RulesReviewer-FableXHigh | worker-xhigh | fable (claude-fable-5-1) | xhigh | 17:43 | 18:00 | 3,657,605 | done; 1 BLOCKING (RR-1), 4 SHOULD FIX, 14 NOTE; started early (rules final) |
| EconReviewer-FableXHigh | worker-xhigh | fable (claude-fable-5-1) | xhigh | 17:43 | 19:56 | 18,049,709 | done; Phase A 17:43-17:59 blind, B 19:27-19:46, C 19:46-19:56 (two resumes by message); 0 / 3 / 11 |

## 5. Verification

Two Fable xhigh reviewers, independent of the authors (L-8): RulesReviewer-FableXHigh checked the rule table
against its quotes and the terms (reports/stage_e19_review_rules.md); EconReviewer-FableXHigh rebuilt the returns,
wrote its own simulator, recomputed the headline blind (recompute.json written 17:57, before any result existed),
compared, reviewed the code, and in Phase C recomputed every remaining verdict cell (reports/stage_e19_review.md,
reports/stage_e19_verify/). Result: the headline reproduces (per path to 1e-11 on identical shocks; 60
configurations within 2.6 total SD; 48 campaign quantiles within one purchase or 1.3%; 11/11 hand paths to the cent).
Counts: rules review 1 BLOCKING, 4 SHOULD FIX, 14 NOTE; model review 0 BLOCKING, 3 SHOULD FIX, 11 NOTE. Rulings in
full: reports/stage_e19_rulings.md.

| ID | Grade | Area | Finding (abridged) | Ruling and fix |
|---|---|---|---|---|
| RR-1 | BLOCKING | P01 Account stacking (S23), P29 Excessive purchases (S24), P | The modelled funnel is, at high churn, the practice Topstep names: sequential Combine purchases and resets after MLL breaches, up to 60 attempts... | ACCEPTED: churn metrics, label (L-19), forfeiture column added post hoc; recommendations only low churn in band; fee-budget stop rule |
| RR-2 | SHOULD FIX | P06 full Maximum Position Size into scheduled news (S23), P3 | The simulator cuts n to the lot cap (Combine max_minis or the XFA scaling tier) whenever f x D / sigma exceeds it, so on those days the bot holds... | ACCEPTED as a bot rule (below full tier size through releases); no rerun |
| RR-3 | SHOULD FIX | P18 Cross-account hedging (S24), P19 overlap even if brief o | The 5-slot campaign draws each slot's product (pooled, per 5-day block) and direction (fair coin per day) independently, so two slots hold the... | ACCEPTED: slots read as different products; bot rule one product per account or same direction |
| RR-4 | SHOULD FIX | P35 "Unusually large number of orders (Terms)" bot_implicati | The clause is about orders for the Services, i.e. purchases of Combines and Resets (ToU "Services" = the Trading Combine and related services; the... | ACCEPTED: P35 bot_implication fixed by the lead (purchase rate) |
| RR-5 | SHOULD FIX | P32 Multiple MLL hits in one day (S31), R059/R060; sim_spec  | Copy-traded accounts breach the MLL on the same day; S31 lists that as an RTP trigger, after which new Combines and XFAs get a forced DLL and only... | ACCEPTED: copy-traded figure carries the RTP caveat |
| RR-6 | NOTE | R066 / R115 / R166 dll_discount_monthly_usd.standard = null  | S06's sentence names "Express Funded Account Activations" among the DLL-discount-eligible purchases, but S06's discount table lists only the No... | Acknowledged (NOTE); no change needed or text note |
| RR-7 | NOTE | R002 profit_split_trader = 0.9 | Verified. The "100% of your first $10,000" clause on S17 is a note "for traders who joined the new Topstep dashboard before January 12, 2026"; a... | Acknowledged (NOTE); no change needed or text note |
| RR-8 | NOTE | R046 / R047 payout fee $0 (Wise, Aeropay), L-12 headline | Wise is available for Canada (the user's region) since August 2026 and carries no Topstep fee, so the $0 headline holds for Topstep's side; Wise's... | Acknowledged (NOTE); no change needed or text note |
| RR-9 | NOTE | R074 / R075 Combine consistency type and frac; R029 boundary | The two wordings are one rule. "Best day at or below 55% of the Profit Target, else the target rises to best day / 0.55" (S13) and "no single day... | Acknowledged (NOTE); no change needed or text note |
| RR-10 | NOTE | R058 xfa_min_payout_balance_after_first_required = true (CON | The structured JSON value is true but the rule cannot be simulated (no amount published) and prop_econ/rules.py does not read the field (checked... | Acknowledged (NOTE); no change needed or text note |
| RR-11 | NOTE | sim_spec section 5 "A pass ends the subscription (unused cre | S09 says Reset Credits stay on the profile after the subscription ends and can be applied to an existing active subscription of the same size and... | Acknowledged (NOTE); no change needed or text note |
| RR-12 | NOTE | Terms check (ToU section 28, robots.txt), L-11 | The clause and both robots files are quoted verbatim and correctly. The ban is on processes that "crawl" or "spider" pages; Task 1 fetched 41... | Acknowledged (NOTE); no change needed or text note |
| RR-13 | NOTE | R056 / R057 voluntary-close payout (S35), L-15 | The only source is the www XFA rules page dated June 26, 2025, which is stale elsewhere (7-day Back2Funded window, superseded 2026-05-29 per S18).... | Acknowledged (NOTE); no change needed or text note |
| RR-14 | NOTE | R009, R033; sim_spec section 4 payout timing | The simulator requests at the start of the next trading day, so the request day never counts and the next window starts the day after. A real... | Acknowledged (NOTE); no change needed or text note |
| RR-15 | NOTE | R092 / R143 / R196 scaling_boundary (UNSOURCED), R034 | Both readings are listed and run (L-16). The S32 hint toward "upper" is recorded. The tier-from-prior-close rule (R034) is supported. | Acknowledged (NOTE); no change needed or text note |
| RR-16 | NOTE | Prohibited-practices completeness (check 5) | The keyword census over all 39 saved text pages found no bot-relevant practice missing from the 42. Items in the sources and not listed are not... | Acknowledged (NOTE); no change needed or text note |
| RR-17 | NOTE | P36 flat by 3:10 PM CT, R032; D6 windows | All five modelled day sessions close before 15:10 CT (equity 15:00, rates and fx 14:00, energy 13:30, gold 12:30 CT) and ReturnsCoder skips... | Acknowledged (NOTE); no change needed or text note |
| RR-18 | NOTE | Spot re-fetch (check 6) | 5 of 5 pages returned 200. S19 and S23 are byte-identical to Task 1's copies; S06, S17 and S14 differ only in dynamic Intercom markup: every one... | Acknowledged (NOTE); no change needed or text note |
| RR-19 | NOTE | R043 API fee 14.5 | The $14.50 depends on the "topstep" code (list $29, billed by a third party); both readings are in the rule. The wallet applies it post hoc per 21... | Acknowledged (NOTE); no change needed or text note |
| ER-1 | SHOULD FIX | statistics (grid.py `_mean_se`, report T1-T7, derived SEs) | The reported Monte Carlo SE of every cycle metric (net mean, its SE, "sens - twin (SE)", the optimum's SE) conditions on the 20,000-path attempt... | ACCEPTED: results state SEs are pool-conditional; total 1.3x-2.5x; no sign/ranking change |
| ER-2 | SHOULD FIX | churn label (report.add_churn, L-19, Q20) | The metric is computed exactly as defined (max error 0.0 over 4,464 records: 21 x mean purchases / mean Combine-phase days, ratios of means). But... | ACCEPTED: label kept, stated as partly definitional; reset-inclusive rate reported |
| ER-3 | NOTE | T5 SEs (Q3) | "sens - twin (SE)" uses sqrt(se1^2 + se2^2) even where both sides are the same draws: ccons_inclusive rows read "0 (62)" for a difference that is... | Acknowledged (NOTE); no change needed or text note |
| ER-4 | NOTE | zero-edge sign (verdict input) | Within the policy band the zero-edge cycle net is negative in every one of the 1,500 zero-edge records (all families, pricings, DLL, B2F); the... | ACCEPTED: lead's draft corrected (f 0.50 claim) |
| ER-5 | NOTE | optimum f (verdict input) | Standard path: the cycle net rises with f through the band in every headline group and keeps rising at 0.35 and 0.50 (f0.50 > f0.25 in all... | ADOPTED in the text |
| ER-6 | NOTE | conventions the spec left open | My eight independent readings (verify/recompute.json `conventions` C1-C8) all match the code: a reset day is traded by the next attempt; a rebill... | Acknowledged (NOTE); no change needed or text note |
| ER-7 | NOTE | returns (D8 round trips) | For GC, ZN and 6E the D8 table's `day_session` flag covers 11/14 buckets while 10/13 lie inside the D6 window: one edge bucket straddles the... | Acknowledged (NOTE); no change needed or text note |
| ER-8 | NOTE | grid.py `_attempt_pools` | The pool cache key is (f, dll, ccons_inclusive) without the edge; correct only because `group_tasks` groups jobs by (shock config, size, edge). | Acknowledged (NOTE); no change needed or text note |
| ER-9 | NOTE | day indexing | `payout_days` / `first_payout_day` are 0-based start-of-day indices; `end_day` and cycle `end` are elapsed-day counts. Assembly is consistent... | Acknowledged (NOTE); no change needed or text note |
| ER-10 | NOTE | seeds (Q1) | The cost model is in the shock seed, so cost_wall is unpaired with its d8 twin; the T5 unpaired SE is then the right one for that row. Everything... | Acknowledged (NOTE); no change needed or text note |
| ER-11 | NOTE | zero-edge label | zero_k1 is a bot with a net Sharpe of about -0.5 (k = 3: about -1.5) once D8 costs per unit sigma are counted (T3 effective Sharpe, risk-weighted... | Acknowledged (NOTE); no change needed or text note |
| ER-12 | NOTE | integer sensitivities | integer_NQ and integer_ZN are f-insensitive in the band (one contract at every f <= 0.30 for a 50K Combine), so their band optimum (0.05 / 0.15)... | Acknowledged (NOTE); no change needed or text note |
| ER-13 | NOTE | verification coverage | Not recomputed independently in Phase B: campaigns (P50/P80), DLL-on, Back2Funded-on, keep-D, call-up, normal-tail, integer and cost-wall records,... | Phase C run: all verdict cells reproduce |
| ER-14 | SHOULD FIX | wording of the positive zero-edge cell (verdict item 4) | The grid's +27 (SE 11) for 50K standard, DLL on, f 0.50, zero_k1 (and +34 (16) with Back2Funded) reproduces on the same shocks (+16 (10), +37... | ACCEPTED: text says the f 0.50 DLL cell's sign is not established |

## 6. Open choices (every decision the lead made on its own, with the reason)

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

## 7. Decisions for the user (each with a recommendation)

1. **Buy a Combine at all?** Recommendation: **not yet.** With no validated edge (N = 480, nothing has passed), the
   funnel loses money in expectation at every size, path, pricing and sizing: the best case is -$250 per 50K cycle
   (-$94 without the API fee), and half of all cycles lose every fee paid. Buy only when a strategy has passed a
   registered test with a net Sharpe of about 0.5 or more after costs (a gross Sharpe near 1.0 at one round trip a
   day). Even then the gain is modest: +$278 to +$906 per 50K cycle. Payout luck is weak evidence of edge: at zero
   edge a cycle pays something 52% of the time on the Standard path, at a net Sharpe of 0.5 64% of the time. So no
   number of Combines bought will tell an edge from luck in a useful time.
2. **Which size?** Recommendation: **50K.** It has the lowest break-even (net Sharpe about 0), the smallest zero-edge
   loss and the cheapest failures. 100K is positive at a net Sharpe of 0.5 only on the Consistency path (or with
   Back2Funded). 150K needs a net Sharpe of 0.5 to 0.9 to break even, because its Combine is slow and billed at
   $199 a month.
3. **Which payout path and options?** Recommendation, for a bot with a validated edge: **Consistency path, DLL added
   at purchase, Standard pricing ($49/month + $149 activation), Back2Funded used when an XFA is lost before its first
   payout, and a keep-D payout policy** (leave half the MLL in the account after each payout). At a net Sharpe of 0.5
   on 50K the best tested combination is +$477 per cycle with the DLL and +$906 with Back2Funded as well (payout
   policy max). Keep-D was tested separately, with the DLL and Back2Funded off. Keep-D
   adds $42 (Consistency) to $209 (Standard) on 50K at a net Sharpe of 0.5, and more on the larger sizes. Choose the Standard path instead if fewer empty
   cycles matter more than the mean: 36% of cycles pay nothing, against 54% on the Consistency path. The No Activation
   Fee pricing path is worse, except at 150K with the DLL.
4. **How many attempts to budget?** With five accounts and a net Sharpe of 0.5 on 50K, withdrawing $5,000 takes about
   51 Combine purchases and $4,100 of fees with 50% probability, or 76 purchases and $5,900 with 80%. That is 255 to
   383 trading days. $10,000 takes 86 / 121 purchases and $6,900 / $9,500. At zero edge, $5,000 takes $7,900 / $11,500
   of fees. Recommendation: **no Combine budget at zero edge.** With a validated edge, see the fee table in section 3
   (T4), and note that $4,000 to $6,000 of fees is about what a small personal micro-futures account needs, which is
   the user's real goal (V32).
5. **Stop rule.** Recommendation: **a hard fee budget fixed before the first purchase, and never raised after
   losses.** Suggested: at most $1,000 on 50K, about two cycles. Stop at once when the budget is spent, when the bot's
   own tracked net Sharpe over 60 or more trading days falls below 0, or at a Live Funded call-up (the LFA bans the
   API). Never buy faster after losses: that is the account-stacking pattern.
6. **What a bot must and must not do under Topstep's terms.**
   - **Must:** run on the user's own machine (no VPS, VPN or remote server); use the TopstepX / ProjectX API only on
     Combines and XFAs; be flat by 15:10 CT, with no new positions after 15:08 CT; keep the position below the
     tier's full size through scheduled releases (the V23 item 11 release-window fraction).
   - **Must:** trade one product per account, or the same direction on every copied account; size at or below
     f = 0.25 of the drawdown distance; keep Combine and Reset purchases modest (L-19: about two per account per
     month at most); stop all automation at a call-up.
   - **Must not:** hedge across accounts, even briefly; trade full size into news; scalp SIM fills or make hundreds of
     rapid trades; trade outside the best bid or offer; use the diagnostic sizes (0.35, 0.50), which raise expected
     cash only by breaching faster; or rotate through accounts after MLL hits (account stacking).
   - **Note:** several accounts hitting the MLL on the same day can put the trader in the Responsible Trading
     Program. That makes copy-trading five accounts riskier than its arithmetic.

## 8. Session cost

Wall clock 16:54 to the final commit (see the ETA table's last rows), 2026-10-10, one session: no pause, no usage-limit
wait, no outage. Tokens are summed from this session's transcript and its six subagent transcripts up to
2026-10-11T03:15:07Z (reports/stage_e10_briefs/cost.py; raw output reports/stage_e19_briefs/cost_raw.txt); the lead's
last steps after that (the final assembly and the commit) are not in the count. Never estimated.

### Final ETA table (actuals; PDT; the initial estimate in brackets)

| # | Task or spawn | Owner | Model | Effort | Parallel / serial | Start | End | Time | Status, deviations [initial estimate] |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Read prompt and context | lead | opus | xhigh | first | 16:54 | 17:02 | 8 min | done |
| 0 | Start checks | lead | opus | xhigh | serial | 17:03:05 | 17:03:13 | 8 s | all pass |
| 0 | Spec, schema, interface, briefs | lead | opus | xhigh | serial | 17:04 | 17:09 | 5 min | done [task 0 total 16 min; actual 15] |
| 1 | TopstepRules-OpusHigh | worker-high | opus | high | parallel with 2, 3a | 17:09 | 17:24 | 15 min | done [60 min, guess] |
| 2 | FunnelCoder-OpusXHigh | worker-xhigh | opus | xhigh | parallel with 1, 3a | 17:09 | 17:41 | 32 min | done [90 min, guess] |
| 3a | ReturnsCoder-OpusHigh | worker-high | opus | high | parallel with 1, 2 | 17:09 | 17:15 | 6 min | done [45 min, guess] |
| 3b | Lead checks and rulings L-10..L-17, ruff fix | lead | opus | xhigh | serial, between returns | 17:15 | 17:43 | interleaved | done [15 min] |
| 3c | GridCoder-OpusHigh (runner, aggregator, full grid) | worker-high | opus | high | parallel with 5a, 5b-A | 17:43 | 19:26 | 103 min | done; first run stopped 18:01 and restarted 18:02 to add the churn metrics (RR-1); grid 82.7 min on 4 workers [80 min: 40 code + 40 run] |
| 5a | RulesReviewer-FableXHigh | worker-xhigh | fable | xhigh | parallel with 3c | 17:43 | 18:00 | 17 min | done; started before the results (rules final) [75 min with 5b, after task 4] |
| 5b-A | EconReviewer-FableXHigh, Phase A (blind) | worker-xhigh | fable | xhigh | parallel with 3c | 17:43 | 17:59 | 16 min | done [in the 75 min above] |
| 5c | Rulings RR-1..RR-19, RR-4 fix | lead | opus | xhigh | serial | 18:00 | 18:02 | 2 min | done |
| 4 | Results md (narrative, key numbers, assembler) | lead | opus | xhigh | parallel with 5b-B | 19:26 | 19:31 | 5 min draft | done; final after the review fixes (19:56) [45 min] |
| 5b-B | EconReviewer, Phase B (compare, code review) | worker-xhigh | fable | xhigh | parallel with 4 | 19:27 | 19:46 | 19 min | done; 0 BLOCKING |
| 5b-C | EconReviewer, Phase C (verdict cells) | worker-xhigh | fable | xhigh | serial | 19:46 | 19:56 | 10 min | done; ER-14 |
| 5d | Rulings ER-1..ER-14, text fixes | lead | opus | xhigh | parallel with 5b-C | 19:46 | 19:56 | 10 min | done [30 min] |
| 6 | End suite (detached) | lead | - | - | parallel with 6 | 19:57:06 | 20:14:17 | 17 min 11 s | 7,138 passed, 3 skipped, 3 xfailed, rc 0 |
| 6 | Return, progress, STAGES, end checks, commit | lead | opus | xhigh | serial | 19:57 | 20:15 (commit within minutes) | 18 min | [40 min] |
| | **Total** | | | | | 16:54 | 20:15 (commit within minutes) | 3 h 21 min | no pause, no outage; initial estimate ended 23:25 (6 h 31 min); revised at 17:43 to 20:20 and at 18:36 to 21:30 |

### Tokens per model

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 3,084 | 243,150 | 20,626,103 | 834,977 | 21,707,314 |
| claude-opus-5-5 | 742 | 652,168 | 74,197,620 | 3,301,322 | 78,151,852 |
| all | 3,826 | 895,318 | 94,823,723 | 4,136,299 | 99,859,166 |

Delegation share: lead 42,098,026 (42.2%), workers 57,761,140 (57.8%). Per worker: section 4.
