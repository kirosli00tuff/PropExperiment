# Stage E.11 STATE (ML route v2: design draft and synthetic build)

Resume rule: read this file first, skip tasks marked done, continue at "Next".
Lead: Opus 5.5 (claude-opus-5-5), xhigh. Times are America/Vancouver (PDT).
Prompt: the user's pasted E.11 prompt (revision 2026-10-03), committed at 5c28a92.

## Files and hashes in force
- Harness manifest: v7 IN FORCE since commit 5931e30, sha256
  eee8a8b92a0210b245429135cf08b42f739b9328fa4eb49bf9034e5b387853d4 (v6 9a8ebe73... before it).
  Every harness command now takes --harness-sha256 eee8a8b9...
- HEAD at start: 5c28a92 (clean tree)
- Ledger: 17400 lines, sha256 0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
- Holdouts: all_ok, 0 unlocks (start)

## Task status
| Task | Status | Start | End | Artifacts |
|---|---|---|---|---|
| 0 Startup | done (suite 5582 passed, 2 skipped, 1 xfailed, 17:03) | 01:03 | 01:22 (suite) | reports/stage_e11_briefs/start_checks.txt, checks.sh, pytest_start.out |
| 0a ApiSurvey-SonnetMed | done | 01:07:45 | 01:12:38 | reports/stage_e11_briefs/api_inventory.md |
| 0b MemberInventory-SonnetMed | done (54 rows) | 01:07:15 | 01:13:15 | reports/stage_e11_briefs/member_inventory.md/.json |
| 1 Design draft (lead) | done (v0 draft) | 01:08 | 01:21:26 | docs/STAGE_E_ML_V2_DESIGN.md |
| 6 KeyFix-OpusXHigh + harness v7 | done, committed 5931e30 | 01:22:30 | 01:36 worker, 01:36 commit | data/config.py, tests/test_stage_e_config_keys.py, manifest |
| Interfaces (lead) | done | 01:23 | 01:29 | reports/stage_e11_interfaces.md, ml_route_v2/constants.py, __init__.py |
| 2 SignalCoder-OpusXHigh | first pass done ~02:21 (415 passed; 90 signals, 206 cols); port pooling done 02:23 (321 passed; 66 signals = 42 member + 24 generic; 154 feature cols); follow-up started 02:21 | 01:29 | | ml_route_v2/signals/, normalize.py, targets.py |
| 3 ModelCoder-OpusXHigh | done (54 passed; fit probe ridge 0.19 s, LGBM d3 4.28 s at 250k x 90) | 01:29 | 01:50 | | ml_route_v2/models.py, cpcv.py, gate0.py, decide.py, configs.py |
| 4 PortfolioCoder-OpusXHigh | first pass done 01:58 (117 passed, 1 xfail); follow-up done 02:06 (139 passed, 0 xfail); follow-up started 01:59 | 01:29 | | ml_route_v2/sizing.py, portfolio.py, killswitch.py, simulate.py, payout_sim.py |
| 5 CanaryCoder-OpusXHigh | done ~03:33 (546 passed, 2 xfail; all canaries caught; probe B 20.4 min measured, A ~46 min extrap, A peak 7.2 GB) | 02:21 | | tests/test_ml_v2_leakage.py, reports/stage_e11_runtime_probe.md |
| 7 Suite + probe (lead) | done: 6299 passed, 2 skipped, 2 xfailed (pre-existing + C-1), exit 0, 21:20; probe figures in reports/stage_e11_runtime_probe.md | 05:19 | 05:40 | | |
| 5b FixCoder-OpusXHigh (G0-1, roll-blackout rule, memory/checkpoints) | done ~04:45 (629 passed, 1 xfail C-1; size-A engine peak 4.78 GB = 49%) | 03:37 | | |
| 8a DesignReviewer-FableMax | Part 1 written (36 KB, complete) before the usage-limit stop; return message lost | 03:37 | | reports/stage_e11_review.md Part 1 |
| 8a' Lead rulings on Part 1 + design text fixes | done 04:40 | 04:15 | 04:40 | reports/stage_e11_rulings.md Part 1; design updated |
| 5c DesignFixCoder-OpusXHigh (Part 1 code: D-01,03,04,05,08,21 + per-product blackout + isolate) | done ~05:15 (683 passed, 1 xfail C-1) | 04:52 | 05:15 | brief_designfix.md |
| 8b CodeReviewer-FableXHigh | done 05:45 (0 BLOCKING, 2 SHOULD FIX, 10 NOTE; mutations 9/9) | 05:19 | | reports/stage_e11_review.md |
| 9 Rulings, return, commit | pending | | | reports/stage_e11_rulings.md, reports/E.11_RETURN.md |

## Lead decisions so far (for return section 6)
- New ml_route_v2 tests are named tests/test_ml_v2_*.py so they do not match the harness manifest's
  TEST_PATTERNS ("test_ml_route_*.py"); ml_route_v2/ is outside HARNESS_DIRS. The v7 manifest therefore
  differs from v6 only by data/config.py and its new test.
- The key-fix test is tests/test_stage_e_config_keys.py (matches "test_stage_e_*.py", so the manifest
  freezes it with data/config.py).
- Start suite run as `uv run pytest -q -p no:cacheprovider` (nice 10) to keep .pytest_cache out of the tree.
- Design choices logged for return section 6 (lead, Task 1):
  1. Cost gate read literally (net edge > k c, i.e. gross > (1+k)c); gross > k c listed open.
  2. Gate 0 canary "edge smaller than the cost passes Gate 0 then cost gate rejects" implemented as a
     binary edge in [1.5c, 2.5c) (passes Gate 0, rejected by the gate) plus an edge < c (fails both).
  3. Model fit on gross normalized target; "net model" = model + cost gate + sizing, selected on net P&L.
  4. Ridge only (no elastic net); 45 configs (3 ridge + 2 LGBM) x 3 k x 3 h, at MinBTL ~45.
  5. Decision clock by rule (t1 = O+30, t3 latest with t3+120 <= F, t2 midpoint); h in {60,120,F}.
  6. c/sigma tau = 0.10 derived from IC 0.10 x z 2.5 vs 2.5c hurdle.
  7. Gate 0 family A = per signal x horizon date-clustered IC t (two-sided); family B = ridge
     lambda 0.1 CPCV OOF top-20% |r_hat| per pair; Holm 0.05 over A+B; 30-trade floor.
  8. Research-window pass bar t >= 1.0 (window cannot confirm S 1.5); training-window t >= 3 median path.
  9. Selection metric = fixed-D (MLL) daily Sharpe at 50K, eligibility >= 30 trades per validation set.
 10. Simulator: PortfolioRules subclass drops catalog one-position rule, member lot cap per product;
     150K economics via payout_sim re-sizing (engine encodes 50K only); 150K tiers = 50K tiers.
 11. Phase-1 scope = training window only (holdout-2 deferred to phase 2) - departs from V1, listed open.
 12. Sizing rounding band: n_risk 0 -> 1 when one contract's h-sigma <= 2b (D2 band) - added 01:30.
 13. Payout policy: request max at first eligibility; reset cost/delay are parameters (open).
- Briefs on disk: reports/stage_e11_briefs/brief_task5.md, brief_design_review.md,
  brief_code_review.md, prompt_findings.md (verbatim F1-F13 + Task 1 list).

## Next
- On suite end: record result. On CodeReviewer return: rule Part 2; one fix round (incl. pending engine per-split risk sizing, D-04 follow-up); final suite; return doc; Task 9 commit.

## Time note
- Times in this file come from file mtimes and tool timestamps (TZ=America/Vancouver). The first
  draft of this table had guessed times; corrected at 01:23.

## Notes from KeyFix (for return)
- compute/remote.py's outgoing-file secret scan now checks only the active account's key (KEY2), not KEY1 (no caller edited per the prompt). Listed for the user.
- Lead's no-print scan: 3 .env values x 18 new files, 0 hits (01:37).
- Run tests/test_harness_freeze.py WITHOUT PYTHONPYCACHEPREFIX (its bytecode tests break under a prefix).

## Task 3 rulings (lead, 01:51)
- Family A: z = 0 where not applicable, all usable rows: accepted (V2.3).
- Family B: top 20% by normalized |r_hat|: accepted (reads predictions only).
- DSR variance: per-config Sharpe of the PATH-AVERAGED OOS daily series (same matrix as PBO): pipeline rule.
- c/sigma filter on the whole training window once (vol only): accepted per V2.2.
- Score-fn leak guard checks outputs only: limitation, for the code reviewer.
- Deviations: SplitScore in configs.py; extra kwargs admissible/calendar/rule; blocks 0-based; PBO
  date cut remainder to last block; scipy Student-t (lightgbm dependency).

## Task 4 rulings (lead, 01:59)
- Engine checks MLL per leg; with concurrent legs it understates account-level breach. Ruling: a
  conservative post-run combined-MLL audit in simulate.py (sum of per-leg adverse extremes vs floor);
  any hit = MLL breach in every verdict. Engine untouched. (follow-up sent)
- Ruin with KS on is 0 by construction: the verdict reads ruin with KS OFF; KS-on reported beside.
- Max payout at first eligibility halted accounts (D < 0.25 MLL): payout policy now keeps
  D >= 0.5 x MLL (PAYOUT_KEEP_D_FRAC = 0.5). (follow-up sent)
- Hand-computed day 2019-06-05: MNQ +55.23, MGC +86.04, day $141.27, floor -1,858.73 (to the cent).
- Payout sim 10k x 252 on 1,200 days: 1.87 s, 145 MB.
- Accepted deviations: AccountSpec extra fields; TradeRecord cluster/entry/exit; run_portfolio 50K only;
  KS only in payout_sim; CPI cap by engine member only; constants TRADE_DATES_PER_MONTH=21,
  PAYOUT_RESET_DELAY_DATES=0.
- Design draft updated (V2.8 audit + KS note; V2.9 payout policy, ruin with KS off; V2.12 item 15).
- Task 4 follow-up (02:06): combined_mll_audit (pinned 2019-06-05 MNQ long 10 + MGC long 9: combined
  -$2,236.08 vs floor -$2,000 at 09:40, engine no breach -> audit 1 record); payout keep-D policy pinned
  (Standard d8 $285, d14 $899.90; Consistency d6 $350, d11 $750); simulate_payouts_pair (ks on/off, one draw).

## Task 2 rulings (lead, 02:21)
- 206 columns > design's "under 100": accepted (estimate, n/p ~435); design V2.3 size text corrected.
- Ports pooled across products (D6: one rule ported to every product) - follow-up sent to SignalCoder.
- G9 120-date median (140-date warm-up on the training window): accepted, logged.
- Early-close dates excluded whole: accepted (v1 ML-A09).
- EXCLUDED K5-fomc (13:05 > 12:50), K6-wasdepost (11:15 > 11:00), K9-anncday (EC-K9 uncovered 2019-24):
  accepted; K9 calendar build listed open (V2.12 item 8).
- New design rule (open): research-window warm-up skips the sealed gap (training dates then research
  dates); alternative research-only warm-up loses 80-140 of 299 dates.
- Roll-blackout union: the pipeline passes clock.exclude_union (in Task 5 brief).
- Mid-stage suite 02:23-02:40 (excl. test_ml_v2_leakage/e2e): 6130 passed, 2 skipped, 1 xfailed, exit 0 (pytest_mid.out).

## Task 5 rulings (lead, 03:37)
- G0-1 (gate0.py read-only view bug): fix (FixCoder).
- C-1 (ridge extrapolates a bounded edge past the 2.5c hurdle; trades realize ~+1.1c net): model
  property, not leakage; xfail kept as documentation; noted in design V2.7.
- S-1 (within-date shuffle not a valid null due to lagged cross-product features): accepted; canary uses
  across-date shuffle; noted in design V2.9.
- Roll-blackout union over 8 leads would drop many dates for all products: design V2.2 changed -
  own roll date excludes rows; a signal leg's roll date makes features reading it not applicable
  (FixCoder implements).
- Size-A engine peak 7.2 GB = 73% of free (>70% rule): free bars / per-path process + per-path
  checkpoints (FixCoder).
- Engine/payout figures from the nested OOS schedule (5 paths), not the in-sample final refit: accepted.
- Design V2.11 updated with probe figures; ThinkPad sufficient (<1 h at 28 products).

## Pause
- Usage limit hit about 03:58 PDT; reset 04:10. Work resumed 04:11. FixCoder resumed via SendMessage
  (partial work on disk). DesignReviewer's Part 1 was already complete on disk; not re-run.

## FixCoder rulings (lead, 04:50)
- Engine shared blackout (union of traded products' roll dates) vs V2.2 own-date rule: PortfolioRules
  goes per product (added to brief_designfix.md item 8).
- isolate_paths default on (item 9). own_path_only flag on 23 SignalSpecs: accepted.
- Deleted ~/.cache/propexp_e11_probe/A_fix3 (1.9 GB synthetic engine frames, session-created).
  A (139 MB) and B (60 MB) probe states kept for now.

## DesignFixCoder rulings (lead, 05:18)
- Readings accepted: budget not KS2-scaled; budget spent on intent; KS2b moot under new ruin; no passive surcharge;
  surcharge counts as slippage at 1.5x; ranking on net edge/c in both readings.
- PENDING: engine run on nested OOS paths sizes with the all-blocks risk table (D-04 not yet in the engine schedule):
  goes into the post-code-review fix round.
- Pinned values changed by D-08a (checked: two-product day 141.27 -> 137.27 = $4 extra ticks).
- Old probe states (~/.cache/propexp_e11_probe/A, B) no longer resume (fingerprints changed): delete at end.
- constants.py long comments wrapped by the lead (values unchanged).

## Session cost inputs (for return section 8)
- Lead transcript: ~/.claude/projects/-home-kiros-li-Documents-GitHub-PropExperiment/92aec2d7-3280-45ef-b6c1-bb26a4cd2ae9.jsonl
  (+ 92aec2d7.../subagents/*.jsonl). Slice from 2026-10-03T08:00:00Z. Script: reports/stage_e10_briefs/cost.py
  (copy to reports/stage_e11_briefs/cost.py). Pause 03:58-04:10 PDT (usage limit) shown separately.
- Agent id -> role: a0a7e11c207adb749 ApiSurvey-SonnetMed; a63014d776f605b6e MemberInventory-SonnetMed;
  a9e40aaa8fb0803c7 KeyFix-OpusXHigh; a944f8fe65056fa25 SignalCoder-OpusXHigh; ac955cbe589b59d0d ModelCoder-OpusXHigh;
  a14f3ccdff08cb97d PortfolioCoder-OpusXHigh; ae487871ed8c60a2f CanaryCoder-OpusXHigh; ac18b79294d8b2456 FixCoder-OpusXHigh;
  a92b482ef984b6ea0 DesignReviewer-FableMax; a7479e4e9ddc3f6bd DesignFixCoder-OpusXHigh;
  afe96b537abfff42b CodeReviewer-FableXHigh; a86333acfe2e6eba6 ReviewFixCoder-OpusXHigh.
- Spawn/return times (PDT): ApiSurvey 01:07:45-01:12:38; MemberInventory 01:07:15-01:13:15; KeyFix 01:22:30-01:36;
  SignalCoder 01:29-02:21 (+pooling 02:22-02:25); ModelCoder 01:29-01:50; PortfolioCoder 01:29-01:58 (+follow-up 01:59-02:06);
  CanaryCoder 02:23-03:33; FixCoder 03:38-03:58 + 04:12-04:45; DesignReviewer 03:38-~03:58 (Part 1 written; cut by limit);
  DesignFixCoder 04:52-05:15; CodeReviewer 05:19-05:45; ReviewFixCoder 05:56-.
- Part 2 rulings written 05:55 (reports/stage_e11_rulings.md); C-08 design text added; C-10 deferred to the next
  purchase session (docs/ACCESS.md:9 stale; data/config.py key.strip()).

## Final phase (06:11)
- Part 2 ruled; ReviewFixCoder done 06:11 (704 passed, 1 xfail C-1). Deviations accepted (C-01 live values hashed;
  C-02 per-split table lists every root + sd 0 = risk_unknown; C-03 16 flagged rows; C-04 strict row-level; C-05
  kept rows; C-07 fit only).
- Probe states deleted (probe_A.json/probe_B.json saved to briefs). End suite running (pytest_end.out).
- Return draft reports/E.11_RETURN.md with @@ placeholders; ret_open_choices.md, ret_decisions.md, ret_fmap.md in briefs.
- Next: end checks (checks.sh v7 sha), cost.py, fill placeholders, progress.md + docs/STAGES.md, commit
  "Stage E.11 ML route v2 design draft and build" (ml_route_v2/, tests/test_ml_v2_*.py, tests/ml_v2_fixtures.py,
  design, interfaces, runtime probe, review, rulings, return, progress.md, docs/STAGES.md).

## DONE (06:35 PDT)
- Stage commit 39738c3 "Stage E.11 ML route v2 design draft and build" (69 files). Harness v7 commit 5931e30.
- Post-commit: v7 preflight OK; holdouts all_ok, 0 unlocks; REGISTRATION.md 0 bytes.
- Left untracked: this STATE file, reports/stage_e11_briefs/, reports/stage_e11_keyfix.md,
  reports/stage_e11_signal_coverage.md (listed in the return, section 2).
- Nothing left to do in E.11. Next stage: the v2 freeze session after the user's 19 decisions.
