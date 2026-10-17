# Stage E.22 return: the five Tier A members confirmed once each (no edge; K8 null, K3/K5/K6 no cluster statement), the micro trend book designed, E22-F1 registered; N = 533

Lead: Opus 5.5, effort xhigh, ultracode on, session 1414530f, unattended. Prompt docs/prompts/STAGE_E.22.md (commit 5a5674b,
V39). Run 2026-10-16 00:46-02:43 PDT, paused (usage limit 02:43, then the user's pause at 07:57 and a laptop restart), resumed
18:26 PDT under a user-approved window (no confirmation read after 02:00 PDT 2026-10-17, return by 03:00 PDT). Times PDT,
from `date`, file mtimes and git.

## 1. Summary

**Part A** (one confirmation run per cluster on S_X..2024-02-29 under harness v13, Holm K = 5 at alpha 0.01, N = 533; every
figure recomputed by Fable):
- **K5-fomc-01 MGC** (on GC bars, U8): **NULL**, no edge. UCB95 +0.09 against eps 71 ticks; Holm p 0.894. Cluster K5:
  no statement (two MHG Tier B trials excluded at confirmation, coverage 0.77).
- **K3-ldnrev-01 6E: NULL**, no edge. UCB95 +0.10 against 12; Holm p 0.797. K3: no statement (6S, 6N Tier B, coverage 0.93-0.94).
- **K6-limitcont-01 HE: NULL BY INACTIVITY** (10 trips < 30), no edge. UCB95 +0.39 against 7; Holm p 0.409. K6: no
  statement (limitcont LE, 0 trips; ruled R-E22-A16 before the read).
- **K8-flight-01 HEOD MGC** (on GC bars): **NULL**, no edge. UCB95 +2.25 against 71; Holm p 0.574. **K8: NULL.**
- **K8-wkndbtc-01 MNQ: INCONCLUSIVE BY DESIGN** (D4: MBT-limited window 34 days < n_b 43; BTC not owned); not run.
No Tier A member passes Holm; no edge candidate; N unchanged.

**Part B** (design study on data E.21 already read; not evidence of edge). Net Sharpe, unrounded / simple / greedy: $10K
0.47 / 0.47 / 0.07; $25K 0.47 / 0.41 / 0.29; $50K 0.47 / 0.46 / 0.31. At $25K, simple rounding: costs $572 a year,
expected 1-year max drawdown 22% of capital (95th percentile 39%), realized max drawdown 63.5% (2015-2017), IBKR margin
52% of capital on average and 104% at the 95th percentile (12 of 21 micros modelled).

**E22-F1** registered (r007-E22, **N 532 -> 533**): the $25K simple-rounded book, 36 months from its first ledger record,
PASS iff one-sided p <= 0.05 and net Sharpe >= 0.3; power about 0.22 at a true Sharpe of 0.5.

**For the user:** approve a daily settlement source (recommendation: a fresh Databento statistics-schema quote); E22-F1's
clock starts only then.

## 2. Guardrail evidence

### Start checks (verbatim; reports/stage_e22_briefs/start_checks.txt; 1,027 untracked paths omitted)

```
{{START_CHECKS}}
$ uv run pytest -q -p no:cacheprovider (detached, 00:48:05-01:09:26)
7402 passed, 3 skipped, 3 xfailed, 54 warnings in 1276.46s (0:21:16)
rc 0
```

### Resume checks after the pause (reports/stage_e22_briefs/resume_checks.txt, 18:26:48)

No run-once marker, no confirmation output, no runner or pytest process existed. Harness v13 dd2bcc60 preflight OK; holdout
all_ok True, unlocks_logged 0; REGISTRATION.md 0 bytes; spend ledger 36,402 lines 034a454b...; trial registry 8 lines
df7b662d..., N = 533; git: only ` M ledger/trial_registrations.jsonl` (r007) plus untracked files.

### End checks (verbatim; reports/stage_e22_briefs/end_checks.txt; untracked paths omitted)

```
{{END_CHECKS}}
{{END_PYTEST}}
```

The quoted end suite ran 02:20-02:40 on the final code (v13 and E22-F1 committed). A second run after the confirmations
(18:59:54) was stopped at 81% at 19:14:51 when free memory fell to 1.5 GB (pytest at 6.85 GB beside the user's other
applications); no tested code changed after 2a2bdd8 (git: no .py change outside reports/), so the 02:20 result stands.

Changed between start and end: the trial registry gained line 8 (r007-E22; 7 -> 8 lines, 085ed33c... -> df7b662d...);
the spend ledger is unchanged (36,402 lines, 034a454b...); the harness moved from v12 ece91ae8... to **v13 dd2bcc60...**
(commit e40ca85, Fable-reviewed, before any confirmation read), as the prompt's guardrail allows. **Four earlier freezes
no longer verify under v13** (E.16: screening/stage_e_verdict.py and data/stage_e_bars.py; E.18 C1b and the E.20 search
freeze: the harness manifest; E.20 H6: data/stage_e_bars.py): every file named is one the sanctioned v13 change rewrote;
those freezes pinned v12 for their own completed runs and were not edited (the same class as the E.14 inputs-list note after
v12). The end suite's single failure (tests/test_h6_rod_run.py) is the same cause: h6_rod pins the v12 harness inside the E.20
H6 freeze. Nothing dated 2024-03-01 or later was read; the March 2024 embargo and holdout-2 were never read; no Databento or
TopstepX call; no purchase; no push; no edit under live/ or ops/; no key printed.

### Order of events

| Event | Time (PDT) | Evidence |
|---|---|---|
| Prompt commit | 2026-10-16 00:45:57 | 5a5674b (git) |
| Start checks; start suite | 00:47:41; 00:48-01:09 | start_checks.txt; pytest_start.out |
| Part A facts (4 agents); rulings | 00:53-01:11; 01:03-01:05 | reports/stage_e22_briefs/partA_*.md |
| K3, K6 start rules (v12) | 01:12:47-01:13:47 | reports/stage_e_start_rule_K3.json, _K6.json |
| Price-path declaration (before any read) | 01:14:03 | reports/stage_e22_price_paths.json 860f4b11... |
| Harness v13 built; Fable review; fixes; recheck | 01:15-01:40; 01:40-01:58; 01:59-02:07; ~02:10 | reports/stage_e22_harness_change.md, _review.md |
| K8 start rule; power re-runs (working tree W1) | 01:41; 01:41-01:54 | reports/stage_e22_briefs/power_w1/ |
| v13 commit | 02:10:40 | e40ca85 |
| E22-F1 freeze commit; registration | 02:11:33; 02:12:01 | 2a2bdd8; r007-E22 (N 532 -> 533) |
| Power re-runs under v13 (identical to W1) | 02:08:38-02:19:52 | reports/stage_e22_power_k*/ |
| Lists; ListReviewer; fixes; recheck | 02:20:10; 02:20-02:37; 02:40:12; ~02:43 | reports/stage_e22_list_review.md |
| PAUSE (usage limit; user pause at 07:57; laptop restart) | 02:43-18:26 | STATE file |
| Resume checks; list commit | 18:26:48; 18:27:48 | resume_checks.txt; ccd7fa7 |
| K5 marker; run; verdict | 18:28:16; -18:31:46; 18:31:49 | reports/stage_e22_K5_RUN_ONCE.json; k5_verdict.json |
| K8 marker; run; verdict | 18:32:35; -18:34:42; 18:34:43 | K8 marker; k8_verdict.json |
| K3 marker; run; verdict | 18:36:23; -18:48:46; 18:48:54 | K3 marker; k3_verdict.json |
| K6 marker; run; verdict | 18:50:00; -18:59:17; 18:59:25 | K6 marker; k6_verdict.json |
| Verifiers K5, K8, K3, K6 | 18:32-{{VERIFY_END}} | reports/stage_e22_verify_k*.md |
| End checks; end suite (quoted) | 19:00:01; 02:20:36-02:40:13 | end_checks.txt; pytest_end.out |
| Second end suite after the confirmations | 18:59:54-19:14:51, stopped at 81% (free memory 1.5 GB, pytest 6.85 GB) | pytest_end_1859_stopped.out |

## 3. Results

### 3.1 Part A: the list (A1)

The prompt's five Tier A members match the screening returns exactly (E.4b:13, E.4c:14, E.8:12-15 and 274, E.9:15-18 and
262-263); K5 has no other Tier A trial. As in E.5, each cluster's single run covers every runnable frozen trial (Tier A and
Tier B), so V14 (c) and L-E5-3 can use the one run (R-E22-A1). Lists (commit ccd7fa7): K5 d2a230f3..., K3 43456def...,
K6 ebb3d034..., K8 28ad6f63...; combined reports/stage_e22_confirmation_list.md 6f2fbf38....

| Cluster | Trials listed / run | Roots and S_X (D4 start rule; price path) | Power (D4) |
|---|---|---|---|
| K5 | 11 / 8 (3 OC-H-excluded) | MGC on **GC** 2019-05-06 (MGC's own window empty: U8 via V39); MHG 2022-06-01 | all sufficient (MGC supply 1,174; fomc n_b 1) |
| K3 | 30 / 27 (3 coverage-excluded) | 6A 6B 6C 6E 6J 6N 6S 2019-05-06 | all sufficient (supply 1,191; ldnrev n_b 1) |
| K6 | 27 / 27 | HE LE ZC ZL ZM ZS ZW 2019-05-06 | sufficient; limitcont LE undefined (0 research trips; R-E22-A16) |
| K8 | 4 / 3 | MGC on GC 2019-05-06, MES 2020-02-03 (D.1f), 6C 2019-05-06, MCL 2021-07-12, MBT 2024-01-02, MNQ on NQ 2019-05-06 | flight H30/HEOD supply 944, oilcad 569; **wkndbtc supply 34 < n_b 43: inconclusive by design, not run** |

Power re-runs (research window, E.5's method) under v13 matched the screening records in every field but `power`
(K5 23/23 files, K3 61/61, K6 54/55 where the one difference is the cluster record's power-undefined list, K8 9/9).

### 3.2 Part A: verdicts (D5; Holm K = 5, alpha_k 0.01; DSR at N = 533; t > 3.0; PBO < 0.5)

{{PARTA_TABLES}}

Reading. Every Tier A member's own null status is null (or null by inactivity) at power 1.0, and none comes near Holm, so
the edge chain stops at its first step for all five. K8's statement is **null**. K3, K5 and K6 get **no cluster statement**
under NULL_CRITERIA_E 1 and 6: in K3 and K5, Tier B trials on the thinnest products (6S, 6N; MHG) failed D9's member-level
coverage check on their confirmation windows (0.93-0.94; 0.77), so the frozen runner excluded them before screening and the
frozen verdict classes them inconclusive (VerdictVerifier-K5 confirmed this is the required reading); in K6, limitcont LE had
no trip (the outcome R-E22-A16 accepted before the read). The descriptive Holm at K = 9 (V14 b) gives the same decisions.
Program-level family-wise error: K4 was tested at 0.05/9 = 0.0056 in E.5 and the four E.22 clusters at 0.01, total at most
0.0456 < 0.05.

### 3.3 Part B: the micro trend book (design study; reports/stage_e22_microbook.md, .json)

These figures re-use data E.21 already read (2010-07..2024-02); they are a design study and not evidence of edge. No p-value,
no verdict, nothing added to N. Rule: Carver's EWMAC 8/32, 16/64, 32/128, 64/256 (his production scalars 5.95/4.10/2.79/1.91,
cap 20), FDM 1.1314 and IDM 2.3518 from his formulas (cited in reports/stage_e22_briefs/carver_sources.md), 20% vol target,
equal weights, next-settlement fills, D8 costs (D8 extension for 8 micros, flagged). Rounding: (a) Carver's rounded and
buffered baseline; (b) his November 2021 greedy minimum-tracking-error optimiser (shadow cost 250, buffer 0.0125, correlation
shrink 0.5).

{{PARTB_TABLES}}

Reading. Simple rounding tracks the unrounded book closely from $25K up (correlation 0.95 at $25K, 0.99 at $50K); at $10K
the correlation is 0.84 and 70% of live instruments sit at zero on an average day. Carver's greedy, at the November 2021
post's parameters, holds most instruments at zero and loses 0.16-0.40 of net Sharpe at every capital level in this 12-micro
universe; its own tracking error is worse than plain rounding on most dates from $50K up (section 10b of the report). The
two figures that matter most for a real account: at the 20% target the realized maximum drawdown was 55-64% of capital
(2015-2017), and IBKR's 2026 overnight margins exceed 100% of a $25K account on about one day in twenty (2026 rates on
historical positions, biased upward in the early years).

### 3.4 Part B: E22-F1 and the paper runner

reports/stage_e22_prereg_F1.md (FROZEN 02:11:20, sha256 04ef33a6...; frozen file set reports/stage_e22_f1_files.sha256,
30 files; commit 2a2bdd8; registered r007-E22 at 02:12:01, test group E22, id E22-F1). forward/ (core, strategy, runner,
ledger, sources, rolls, history, evaluate, report; config_f1.json, tables_f1.json, rolls_f1.json): 142 tests on synthetic data.
The rounding method was changed from the greedy (draft 1, preserved) to simple rounding before the freeze, on the design
study (R-B7); RegReviewer judged this legitimate because the forward test never reads historical data.

### 3.5 Part B: the data-source memo (reports/stage_e22_data_source_memo.md; DataSourceReader-OpusHigh, 14 searches)

| Source | Cost per year for this use | Settlement price | Micros covered | Main caveat |
|---|---|---|---|---|
| Databento GLBX.MDP3 usage-based, `statistics` schema | unknown until a fresh quote (none obtained tonight) | yes (final/preliminary flag) | all CME futures since 2010 | quote needed; same-day availability of the final settlement not stated |
| Databento Standard plan | USD 2,388 | yes | same | live-licence conditions |
| IBKR paper (shares live subscriptions) | USD 74.40 (waived with USD 20/month commission per exchange) or USD 120 bundle | not established | all 21 have margin rows | API settlement field unverified; funded account needed |
| Norgate Data Futures | USD 270 | yes (close = official settlement) | 3 of 21 (all 12 full-size parents) | most micros absent; Windows updater |
| CSI Data (Unfair Advantage) | USD 458 in year 1 | partly (settlement semantics unverified) | 21 of 21 | one device, personal use |
| Massive (Polygon) futures | USD 0-348 | yes (`settlement_price`) | per-symbol unverified | short history on low tiers |
| Barchart, Nasdaq Data Link, AMP, NinjaTrader, CME DataMine | unpublished or unverified | various | - | see the memo; CME's site never fetched |

`ohlcv-1d` is not a settlement series (daily bars built from trades on UTC dates); the settlement lives in the
`statistics` schema.

## 4. Delegation record

| Agent (description) | Worker file | Model | Effort | Objective | Status | Deviations |
|---|---|---|---|---|---|---|
| HarnessGapAudit-OpusXHigh | workflow agent | opus | xhigh | v12 audit for one run per cluster | done | added (the prompt's plan had no audit; needed to scope v13) |
| TierAFactsK5K3-SonnetMed | workflow agent | sonnet | medium | extraction: K5, K3 trials and open issues | done | added |
| TierAFactsK6K8-SonnetMed | workflow agent | sonnet | medium | extraction: K6, K8 | done | added |
| DecisionsScan-SonnetMed | workflow agent | sonnet | medium | rulings bearing on Part A | done | added |
| CarverReader-OpusHigh | worker-high | opus | high | Carver's constants and the Nov 2021 greedy, quoted | done | added (research on opus) |
| DataSourceReader-OpusHigh | worker-high | opus | high | data-source memo, IBKR margins | done | added |
| MicroBookCoder-OpusXHigh | worker-xhigh | opus | xhigh | rule core, study, tables, strategy wiring | done (two follow-ups) | as planned |
| ForwardRunnerCoder-OpusXHigh | worker-xhigh | opus | xhigh | paper runner, ledger, rolls, evaluate | done | added (split from the coder) |
| HarnessBuilder-OpusXHigh | worker-xhigh | opus | xhigh | harness v13 (N1-N5, R1-R3) and review fixes | done | added (the guardrail's v13 path) |
| HarnessReviewer-FableXHigh | worker-xhigh | fable | xhigh | independent review of v13; recheck | done | added (guardrail: Fable-reviewed) |
| RegReviewer-FableXHigh | worker-xhigh | fable | xhigh | E22-F1 review; recheck | done | as planned |
| F1FixApplier-SonnetMed | worker-medium | sonnet | medium | pin test, status strings | done | added |
| ListReviewer-FableXHigh | worker-xhigh | fable | xhigh | the four lists before any read; recheck | done | as planned |
| VerdictVerifier-K5/K8/K3/K6-FableXHigh | worker-xhigh | fable | xhigh | recompute every verdict figure, one cluster each | {{VERIFY_STATUS}} | one per cluster (planned as one), started as each verdict landed |

## 5. Verification (each Fable finding, the ruling and the fix)

**HarnessReviewer-FableXHigh** (reports/stage_e22_harness_review.md): 0 BLOCKING, 2 SHOULD FIX, 14 NOTE. SF-1 (the marker
path did not check the out-dir for stale records) and SF-2 (`--list` sealed into the marker after checking only cluster and
harness): fixed in code with tests. N-2 (declaration mode 0444), N-3 (descriptive Holm at K = 9), N-4, N-11, N-12: fixed.
N-8 (MES closure prints visible to the member) kept as the declared keep-and-flag reading; N-9 (h6 test) recorded as an
expected failure; others no change. Recheck: 7/7 RESOLVED, 0 new blocking; residual R-1 (the list guard does not compare the
freeze sha or vehicles) covered by reports/stage_e22_briefs/prerun_check.py before each run (ALL PASS for all four) and by
ListReviewer.

**RegReviewer-FableXHigh** (reports/stage_e22_reg_review.md): 2 BLOCKING, 8 SHOULD FIX, 10 NOTE, all accepted. B1 (the
runner's tables_f1.json was not named or hashed): named and hashed, with a pin test. B2 (an ambiguous start date and a
post-hoc `--clock-start`): start = the first ledger record; evaluate/report run without `--clock-start`. S1 (warm-up rule),
S2 (pre-clock roll correction; stuck roll -> abandoned), S3 (back-fill), S4 (power 0.13/0.22/0.53), S5-S8: fixed in the
text. Recheck: 19/20 resolved, N2 by agreement; NEW-1 (the abandonment trigger named the wrong flag) and NEW-2 fixed. R-B7
judged legitimate.

**ListReviewer-FableXHigh** (reports/stage_e22_list_review.md): 0 BLOCKING, 5 SHOULD FIX, 7 NOTE. F1 (start-rule files not
hashed: build_list.py read the wrong provenance key): fixed, lists rebuilt. F2 (limitcont LE's undefined power): ruling
R-E22-A16 before the read. F3 (wkndbtc labelled from two readings): consistent labelling, inconclusive by design only, a
reason-only not-run declaration; the strict reading recorded as an open choice. F4/F5 (the ledger line and the inputs
untracked): carried in the list commit ccd7fa7. N-1 (by-design trials always not run): applied. Recheck: 0 blocking, 1,743
field checks pass, K8 dry run rc 0.

**VerdictVerifiers** (reports/stage_e22_verify_k5.md, _k8.md, _k3.md, _k6.md):
{{VERIFY_SECTION}}

## 6. Open choices (every decision the lead made on its own, with the reason)

{{OPEN_CHOICES}}

## 7. Decisions for the user (the lead's recommendation first)

1. **E22-F1's daily data source.** Recommend: authorize a fresh Databento quote for the GLBX.MDP3 `statistics` schema
   (official settlement, every micro, 2010 on) covering the 12 micros' warm-up history and daily updates, then approve the
   spend if it is small; the usage-based price is unpublished, so the quote decides. Fallback: CSI Data (USD 458 in year 1,
   all 21 micros; settlement semantics to confirm). Not recommended: Norgate (3 of the 12 micros), IBKR paper alone
   (settlement field unverified). The clock starts on the first ledger record after approval; before it, check
   forward/rolls_f1.json against the exchange's published roll schedule (logged; not a new registration).
2. **Size and risk of any live version.** Recommend: run E22-F1 as registered (paper, $25K notional) and do not trade the
   book live at $25K at a 20% vol target: the design study shows a 55-64% historical maximum drawdown and IBKR margin above
   the account on about 5% of days. A live book would need $50K or more, or a lower target (a new registration).
3. **Stage E's intraday clusters.** Recommend: close them. Every Tier A member of K3, K4, K5, K6 and K8 is null or untestable
   with no Holm rejection; no holdout read is warranted. Accept "no statement" for K3, K5 and K6 as final (thin-product
   coverage at confirmation, one zero-trip LE member). The frozen rule classes a run-listed trial that the confirmation-window
   coverage check excludes as blocking (VerdictVerifier-K3's note); whether such exclusions deserve a "not covered" class
   instead is a criteria question for any future program, not a reason to re-read.
4. **The four pre-E.22 freezes that no longer verify under v13** (E.16, E.18, E.20 H6, E.20 search). Recommend: accept and
   carry a note in future check scripts (they pinned v12 for completed runs); re-pinning them would rewrite frozen records.
5. **Push** the E.22 commits (e40ca85, 2a2bdd8, ccd7fa7 and the final commit); not pushed, as the prompt says.
6. **The MNQ -> NQ entry in v13's price-path declaration** applies by vehicle: if K1 (MNQ) were ever confirmed it would read
   NQ. No K1 confirmation is planned; remove or keep at the next harness change.

## 8. Session cost

{{COST}}
