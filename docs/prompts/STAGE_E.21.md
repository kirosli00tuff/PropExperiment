STAGE E.21 "MULTI-DAY ROUND: PUBLISHED TREND, TURN-OF-MONTH AND A COMBINED BOOK ON 17 ROOTS, 2010-2024, OWNED DATA, FIVE HOURS"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.20 closed the intraday program on Topstep (V38): nothing in 528
trials passed, and every published intraday effect on our 17 roots is
below the retail round trip. Multi-day holds have barely been tested
here: only H2 (month-end NQ/ZN, 5-day hold, t 1.52) and H3 (auction cycle)
held past one session. For holds of weeks, the D8 round trip is a small
fraction of the move, so the cost wall that ended the intraday work mostly
disappears. This stage tests the published multi-day effects with the
longest records, as their papers define them, on the owned 2010-07..
2024-02 history of the 17 roots: 12-month time-series momentum, a
1/3/12-month trend blend, the equity turn-of-month effect, and one
combined book with H2. Four tests, registered before any bar is read,
evaluated once, Fable-verified. A short literature check confirms each
rule's specification against its primary source before the freeze. No
purchase, no Databento call. A five-hour session.

Decisions in force: docs/DECISIONS.md V20 to V38. Binding, in this order:
this prompt's FIXED DESIGN, then reports/stage_e16_briefs/lead_spec.md's
clock, cost, exclusion, roll and statistics conventions (sections 0 to 3
and 5), then the E.16 rulings and windows.

Lead: Opus 5.5, effort xhigh. Ultracode: on (the user's choice; launched
interactively).

Why this lead and effort: four registered tests built on frozen
conventions, unattended, in a fixed time budget. The silent failures to
guard against: a published rule mis-specified (lookback, volatility
estimator, rebalance day); look-ahead in the volatility scaling or the
month-end signal; returns chained wrongly across contract rolls; costs
omitted at rolls; and a wrong verdict number.

Usage and time: the user gave a five-hour window with fresh limits.
reports/stage_e21_STATE.md is updated after every step. At 4 h 30 min of
wall time, whatever is unfinished is checkpointed and the return is
written with each part's status; no evaluation is started after 4 h 00
min unless it was already registered. Parallel work follows CLAUDE.md's
maximum-parallelism rule (V37).

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue.

============================================================
FIXED DESIGN (DECIDED HERE, BEFORE ANY DATA IS READ)
============================================================

F1. Universe and windows. The 17 roots with owned 2010-2019 history:
NG, NQ, ZN, 6E, GC, ZC (ext2010) and ZT, ZF, ZB, UB, TN, CL, ZL, ZS, RTY,
HE, LE (ext2010h), spliced with their E.12 training stores
(data/processed_step2/) to 2024-02-29. Per-root windows and exclusions as
reports/stage_e16_windows.json (TN from 2016-01, RTY from 2017-06, HE from
2017-07; LE 2010-06-07..2014-12-14 excluded, R-S3). Nothing dated
2024-03-01 or later is read: not the March 2024 embargo, not holdout-2,
not the research window, not MES's sealed stores.

F2. Daily series. One mark per product per trade date: the settlement
mark MK of lead_spec section 0 (the same marks H2, H3 and H5 used). Daily
returns are same-contract returns; a return across a splice is chained as
base_rules/h2.py chained_return does, never taken across two contracts.
Roll-blackout and unsourced dates follow lead_spec section 2.

F3. Volatility scaling, causal. sigma_i,d = annualized EWMA volatility of
root i's daily returns with center of mass 60 trade dates (Moskowitz, Ooi
and Pedersen 2012), using returns strictly before d. Target 40% annual per
root as in the paper; the portfolio is the equal-weight average across
the roots available that month. The statistic uses fractional (risk-unit)
positions; integer-contract feasibility is descriptive (F8).

F4. The tests.
- E21-T1, TSMOM-12 (Moskowitz, Ooi and Pedersen, JFE 2012): at each
  month-end settlement, position_i = sign(chained return over the past 12
  months) x 0.40 / sigma_i, held one month. First signal after 12 months
  plus the volatility warm-up.
- E21-T2, trend blend (Hurst, Ooi and Pedersen, "A Century of Evidence on
  Trend-Following Investing", 2017): position_i = the average of the
  signs of the past 1-, 3- and 12-month chained returns, x 0.40 / sigma_i,
  monthly rebalance as T1.
- E21-T3, equity turn-of-month (Lakonishok and Smidt 1988; McConnell and
  Xu 2008), NQ and RTY: long from the settlement of trading day -2
  (two trade dates before the month's last) to the settlement of trading
  day +3 of the next month, one unit of risk per root (0.40 / sigma_i
  scaled to the hold), flat otherwise.
- E21-T4, combined book: the equal-risk combination of T2's daily series,
  T3's daily series and H2's daily mark-to-settlement series (H2 exactly
  as frozen in E.16), each scaled by its own trailing 60-grid-date sample
  standard deviation strictly before d, as H5 combines (lead_spec section
  4, H5). The first 60 grid dates are warm-up.
Carry is not tested: it needs the second contract's price, and the owned
stores hold only the front contract path (logged as a gap, not a result).

F5. Costs. Each change in contracts held, including every roll fill, pays
the root's D8 round trip at its E.12 vehicle, half per side, in the entry
and exit buckets (lead_spec section 1). The stress case (1.5 x slippage)
is descriptive.

F6. Statistic and bar. Each test's daily net series in risk units, zero on
flat days. t, and the one-sided p as the larger of the plain-t p and the
Newey-West p with lags fixed now: 21 for T1, T2 and T4, 5 for T3.
Annualized net Sharpe = daily mean / sd x sqrt(252), with a block-
bootstrap 95% interval (block 21 days, 10,000 draws, seed 20261014).
PASS per test iff both hold: one-sided p within Holm's step-down at
family alpha 0.025 over the four tests; annualized net Sharpe >= 0.3.
Power, for the record: on about 12.5 years, a true Sharpe of 0.3 gives an
expected t near 1.1, so a PASS needs a realized Sharpe near 0.7; the
interval and the published post-2010 figures (E.13: SG Trend 0.24 over
2010-2025) are reported beside every verdict so that a FAIL with a
positive point estimate is read as underpowered, not refuted.

F7. Trial accounting. E21-T1..T4 are registered before any bar is read:
N 528 -> 532.

F8. Descriptive economics (not part of the verdict), for each test:
- Personal account: capital needed to hold the book at integer micro
  contracts (MNQ, M2K, MGC, MCL, M6E, micro yields where the root maps;
  full-size otherwise, flagged) at 15% and 25% annual volatility, from
  the E.13 trend-carry table (reports/stage_e13_trend_carry.md).
- Prop, main venue PropEd Capital (V38; the only firm found whose terms
  allow automated strategies with overnight holds): for each PropEd plan
  that allows overnight holds and automation, as Step 1's PropEd reader
  sources them, the book's daily and 5-day dollar sigma at its smallest
  integer size against that plan's drawdown (type and amount) and daily
  loss limit, and the share of 21-day windows whose worst drawdown would
  breach it, with and without weekend holds (the weekend add-on). Phidias
  Premium 50K ($2,500 EOD trailing, semi-automated only) is shown beside
  it for comparison. No fee or payout model; that is a later stage if
  anything passes.

============================================================
SCOPE
============================================================

This stage does:
- Step 1: four readers in parallel. Three literature readers (T1 and T2
  specification; T3 specification and post-2008 evidence; post-2010 trend
  and turn-of-month evidence on futures) verify F4's rules against the
  primary source; a mismatch is fixed in the freeze before any data is
  read and logged; no parameter is chosen from data. One PropEd reader
  (PropEdReader-OpusHigh) sources PropEd Capital's current plans from its
  own terms, help centre and pricing pages (read the site's terms before
  any automated fetch; quote each rule with URL and date): plan names and
  sizes, prices, profit targets, drawdown type and amount, daily loss
  limit, overnight and weekend rules and the add-on's price, the exact
  automation and API wording per plan, payout rules and caps, and
  Canadian (BC) eligibility. Output reports/stage_e21_proped_rules.md and
  .json; a rule with no primary source is marked UNSOURCED. This reader
  reads no market data.
- Step 2: code in a new package multiday/ reusing base_rules' marks,
  splices, calendars and costs (never editing a frozen file), with tests
  on synthetic series: chaining across a splice, no look-ahead in
  sigma and in every signal (a planted future bar must not move a
  position), roll costs charged, month-end and turn-of-month dates.
- Step 3: freeze (reports/stage_e21_prereg.md and
  reports/stage_e21_freeze.json), FreezeReviewer-FableXHigh review
  (BLOCKING and SHOULD FIX fixed first), commit "E.21 freeze".
- Step 4: register T1..T4, evaluate each once behind
  reports/stage_e21_RUN_ONCE.json, verdict per F6, then F8.
- Step 5: VerdictVerifier-FableXHigh recomputes every verdict number
  independently without reading the lead's statistics first.
- Step 6: reports/E.21_RETURN.md, one progress.md entry, one
  docs/STAGES.md line, one commit "Stage E.21 multi-day round". No push.

This stage does NOT:
- buy anything or call Databento
- read anything dated 2024-03-01 or later
- change any rule after any bar is read, or run any test twice
- fit any model (no ML), add tests, lookbacks or variants beyond F4
- change any file the harness v12 or the E.14, E.16, E.18 or E.20 freezes
  hash
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V31 to V38.
3. reports/stage_e16_briefs/lead_spec.md sections 0 to 5 (conventions);
   base_rules/README.md; base_rules/h2.py and h5.py; reports/stage_e16_rulings.md;
   reports/stage_e16_windows.json.
4. reports/E.17_RETURN.md section 1 (H2's frozen result, for T4's input only).
5. reports/stage_e13_trend_carry.md (published trend and carry evidence,
   the capital table).
6. reports/E.20_RETURN.md section 1 (why the intraday program closed).

============================================================
GUARDRAILS
============================================================

- Harness v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
  verified at start and end, unchanged; fresh PYTHONPYCACHEPREFIX outside
  the repository for harness commands.
- Store hashes verified at start against their recorded sha256.
- Order of events with timestamps: literature check, freeze review,
  freeze commit, registration, evaluation, verification.
- Holdout status all_ok, 0 unlocks, at start and end; the spend ledger
  unchanged.
- Start and end checks quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the freeze verifications, the ledger line count and
  sha256, N, and `uv run pytest -q -p no:cacheprovider`.
- Compute at nice 10 after a free-memory check; at most 2 heavy workers.
- Before ending, confirm no worker or background shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Literature and venue | 3 x SpecReader-OpusHigh, 1 x PropEdReader-OpusHigh | opus | high | all 4 at once | primary-source specification and venue-rule checks |
| 2 Build | MultidayCoder-OpusXHigh | opus | xhigh | after 1 | conventions reuse and no-look-ahead tests |
| 3 Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | after the freeze text | independent check before registration |
| 4 Evaluate | lead | opus | xhigh | after 3 | registration and verdicts reserved to the lead |
| 5 Verify | VerdictVerifier-FableXHigh | fable | xhigh | after 4 | verdict numbers recomputed |
| 6 Return | lead | opus | xhigh | last | reserved to the lead |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. Run independent workers at once (V37); heavy compute at most 2.
    4. Collect results as files plus short summaries.
    5. Verify every number entering a verdict with an independent fable
       xhigh worker.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/<stage>_STATE.md after each task.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.21_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: each test's verdict (PASS, FAIL or
   STOPPED with the rule) with net Sharpe and its 95% interval, t, p,
   trades and costs as a share of gross; the published comparison; the new
   N; and what the outcome means for a personal account and for PropEd,
   the main prop venue (Phidias for comparison).
2. Guardrail evidence: start and end checks verbatim; the order of events.
3. Results: the literature check, PropEd's sourced rule table, the
   per-test tables (per year, per root, stress case), and F8's economics.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: on a PASS, the
   forward research-window read and a PropEd economics stage (fees,
   payouts, the plan to buy) it leads to; on a
   FAIL with a positive interval, what more data or a longer hold would
   need; on a clear FAIL, what is closed.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
