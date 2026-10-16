# E22-F1 registration review (RegReviewer-FableXHigh, Stage E.22 Part B)

Reviewer: Fable 5.1 (claude-fable-5-1), worker-xhigh, independent of the authors (lead Opus 5.5 wrote
reports/stage_e22_prereg_F1.md; MicroBookCoder and ForwardRunnerCoder, both Opus, wrote forward/).
Reviewed 2026-10-16, 01:36-01:48 PDT (spawn time from reports/stage_e22_STATE.md row B6; end time from
`date` at the write). Read-only; this file is the only write. No data/ read, no network, no commit.

Brief: reports/stage_e22_briefs/brief_reg_review.md. Inputs read: the draft (125 lines, whole),
docs/prompts/STAGE_E.22.md lines 85-160, reports/stage_e22_briefs/lead_spec_B.md (whole),
reports/stage_e22_briefs/carver_sources.md sections A, B.1, B.3, C, all nine forward/*.py files
(whole), forward/config_f1.json, forward/tables_f1.json, forward/rolls_f1.json (compact dumps),
forward/README.md, reports/stage_e22_microbook.md sections 3, 4, 7, 8, 10b, 11, microbook/book.py
and study.py (grep), the nine tests/test_forward_*.py (names and the strategy tests' setup).

Counts: BLOCKING 2, SHOULD FIX 8, NOTE 10.

Verdict on the lead's two questions. (1) R-B7 is legitimate for a forward registration (section 1
below). (2) Text and code agree on the rounding method and on the bar; they disagree on which file
holds the costs and multipliers the runner uses (B1) and on what "start" means (B2). Both are text
fixes of a few lines.

## 1. Ruling R-B7 (rounding method changed from the greedy to simple rounding): legitimate

The forward test's validity rests on the hypothesis, the rule and the bar being fixed before the first
forward observation exists, and on no forward observation entering the choice. Both hold:

- The change was made 2026-10-16 ~01:29-01:33 PDT (STATE row B5; draft mtime 01:33:18; config_f1.json
  mtime 01:34) and no data source is approved, so no forward datum exists. The clock has not started.
- The data behind the choice (2010-07..2024-02, E.21 roots already read; reports/stage_e22_microbook.md
  section 4) are disjoint from the forward series by construction (forward data begin after approval,
  2026 or later). A selection made on one sample does not bias a test on an independent sample.
- The historical figures do not enter the verdict (draft section 1 line 14; section 8).
- Both candidate methods were pre-declared by the prompt (B2 lines 108-110); the choice is between two
  listed options, not a new method invented from the result.
- N accounting is unaffected: the forward test is one hypothesis (the book earns positive net P&L) and
  adds one trial; the two rounding variants were never tested against a bar.

What the selection does cost: the simple book's historical Sharpe (0.41 net at $25K) is a selected
figure and is optimistically biased as a description of the past; the draft already says it is not
evidence (section 4 line 52-53). One evidentiary gap, non-blocking: the 01:05 draft that chose the
greedy is not preserved (the file is untracked, `git log` shows nothing, mtime 01:33:18, no copy under
reports/), so the sequence "greedy chosen, study run, changed" is attested by the STATE file and the
lead's transcript only. See S6.

The study's own basis for the change checks out against reports/stage_e22_microbook.md: at $25,000 the
greedy holds 0.71 of live instruments at zero (section 7) and loses 0.19 of net Sharpe (section 4;
0.16 without yields, 0.29 with the book scalars, section 10); simple rounding loses 0.07 with daily
correlation 0.95 to the unrounded book (section 4). The draft's "about two thirds" and "about 0.07,
0.95" match; "about 0.2-0.3" overstates the main row (0.19); see S6.

Text and code now agree on the method: forward/config_f1.json `rounding_method.value` = "simple";
forward/strategy.py:140-143 takes the simple branch (core.buffered_round); the study's simple rows used
the same function (microbook/book.py:250); the draft's section 4 describes exactly that function
(core.py:157-167: optimal +- 10% of the forecast-10 position, each edge rounded half away from zero,
trade to the edge, else hold). One implementation is frozen, as S7 requires.

## 2. Findings

### BLOCKING (fix before the freeze)

**B1. The runner's costs and multipliers come from forward/tables_f1.json, which the registration never
names.** Draft section 5 line 64-65: "Costs per contract per side: the D8-based table frozen in
config_f1.json"; section 2 lines 20-25 lists config_f1.json and rolls_f1.json; section 11 hashes "every
file in section 2". But forward/runner.py:444-451 (`load_tables`) and :458-470 (`--tables`, required)
read multipliers and per-side costs from a separate JSON; forward/README.md:53-56 says that file is
"frozen by the lead; not written here". config_f1.json's `instruments.*.cost_per_side_usd` is read only
by the greedy branch (strategy.py:134), which E22-F1 does not use, and its `multiplier` only for sizing
(strategy.py:76). So the file that sets every fill cost, roll cost and the P&L multiplier of the series
is outside the freeze. Failure scenario: the two files drift (today they agree: I checked all 12 rows of
both tables, no mismatch, same order); the ledger fingerprint (runner.py:118-127) would notice a change
after the clock starts, but the registration would have no hash to hold it to, and "the code governs"
would make the unfrozen file authoritative. Fix: name forward/tables_f1.json in sections 2, 5 and 11
(hash it), state that config_f1.json `instruments.*` and tables_f1.json must be identical in multiplier
and cost per side, and add the test of S7.

**B2. "Start" is ambiguous between the text and the code, and the code accepts a post-hoc choice.**
Draft section 7 line 88: start = "the first trade date after the user approves a daily data source";
line 91-92: "P&L counts only from the first fill after the start date"; line 93-94: the window is
[start, start + 36 months). forward/evaluate.py:123-130 `resolve_clock_start`: start = the first
ledger record's date unless `--clock-start` is passed (evaluate.py:202, report.py:131), and any
declared date on or before the first record is accepted. Three forks: (a) if the ledger's first record
is later than approval + 1 trade date (the draft itself says "the clock does not run until data
flows"), text and code give different starts; (b) a declared earlier clock start moves `end` earlier
and drops the last records from the window, a choice available after the series exists; (c) "counts
only from the first fill" can be read as starting the series at the first fill, while evaluate.py:157
and :176 include every record in the window, including the zero-P&L days before the first fill and
the missing-day zeros. Fix (text, three lines): "The start date is the date of the first ledger
record, which is the first trade date on which the approved source delivers settlements.
forward.evaluate and forward.report are run without --clock-start. The evaluation series is the
net_pnl of every ledger record dated in [start, start + 36 months), including zero days before the
first fill and missing days." Section 6 line 71-72 and section 7 line 90-91 also refer to a "start
record" and to recording the source "in the ledger's first record"; the ledger schema (runner.py:
298-315) has no such field and PaperRunner._load (runner.py:385-393) refuses any record without the
runner's fingerprint, so a hand-written start record is impossible. Put the source name, terms,
approval date, start date and the warm-up file's sha256 in docs/DECISIONS.md and the E.22 STATE file
instead; the warm-up is already bound into every record's `config_sha256` (runner.py:125).

### SHOULD FIX

**S1. The warm-up history is left open and one of its two declared options is impossible in kind.**
Section 7 line 89-91 allows "the source's own back history, or the owned stores up to 2024-02-29
spliced to the source", declared later. An instrument is live only after 256 daily differences
(config `warmup_diffs`; strategy.py:78), so with no warm-up the whole book is flat for about a year of
the 36 months and that year enters the series as zeros (evaluate counts them), lowering t. The owned
stores are full-size contracts (NQ, RTY, GC, CL, NG, 6E, ZC, ZS, ZL) in the micros' quote units, so a
splice is feasible for nine instruments; for 2YY, 10Y and 30Y the owned paths are ZT/ZN/ZB prices,
while section 3 line 38-40 runs their forecasts on yields in percent. A price history cannot be
spliced to a yield series; the study's proxy transform (core.yield_proxy_diffs, "study" only) would
make the forward forecast run on a different series than registered. The choice is pre-data and so not
a forking path, but it decides how much of the horizon trades. Fix: fix the warm-up rule now (for
example: the source's own back history for every instrument, as HistoryRow JSONL with both contracts
on each switch date, no owned-store splice; or the splice for the nine price-quoted micros and the
source's history for the three yield micros), state that the warm-up file's sha256 is fingerprinted
into every ledger record, and say how many instruments are expected to be live on the start date.

**S2. rolls_f1.json must be checked before the clock starts, but section 2 makes any post-freeze
change a new registration.** forward/rolls_f1.json `status` and every instrument's `flags` say "to be
checked against the exchange's published roll schedule before the clock starts"; all 12 anchors are
UNSOURCED for the micro (parent rules assumed; 2YY/10Y/30Y have no source at all); forward/README.md:
28-37 and :164-165 require the check. Section 2 line 25-26: "Any change to any listed file after the
freeze is a new registration with a new ID (and N + 1)". If the check changes one roll date, the lead
either burns an N or starts with a known-wrong schedule. A wrong schedule has a hard consequence in
the code: when a held contract stops settling before its roll executed, runner.py:245-251 flags the
instrument `missing` on every later day, never fills or rolls it, and freezes its mark; `roll_overdue`
(runner.py:213-214) is a flag, not a refusal, so the instrument silently leaves the P&L series for the
rest of the test. Fix: (a) add a pre-clock clause: "Before the first ledger record, rolls_f1.json may be
corrected against the exchange's published schedule; the correction and the new sha256 are logged in
docs/DECISIONS.md and the STATE file; this is not a new registration. After the first record the file
is frozen (it is in every record's fingerprint)"; (b) state the consequence of a held position whose
contract has no settlement on or after its anchor date (`roll_overdue` with qty != 0): the test ends
"abandoned, no verdict" (or make it a RunnerError in runner.py:213-214 so it cannot pass unnoticed).
[unverified, my recollection, no network allowed here] CME's Micro Treasury Yield futures list
consecutive monthly contracts and cash-settle on the last business day of the contract month, not a
HMUZ cycle; the pre-clock check should look at the yield micros first.

**S3. The back-fill clause (section 6 line 83-84) is a forking path and is not implementable.** "Prices
are never back-filled from a second source after the fact, except under a written lead ruling logged in
the ledger before the affected date's evaluation" lets a day's price be replaced at any time up to the
36-month evaluation, with the running P&L known. The ledger has no field for a ruling and refuses
rewrites (ledger.py:157-166), and a re-run with a different price raises LedgerConflictError
(runner.py:430-437), so a back-fill of a recorded day is impossible without a new ledger (which is
"abandoned"). Fix: "A day's settlements may be taken from a second approved source only before that
day's record is written; the switch is logged in docs/DECISIONS.md. A recorded day is never changed."

**S4. Power statement arithmetic (section 8 lines 104-107).** t = S x sqrt(3) and the one-sided
critical value 1.645 give power 1 - Phi(1.645 - t): S = 0.5 -> t 0.866, power 0.218 ("roughly 0.2",
fine); S = 1.0 -> t 1.732, power 0.535, not "about 0.6". Also worth stating: under iid daily P&L,
t >= 1.645 at 36 months implies realised annual Sharpe >= 1.645 / sqrt(3) = 0.95, so the Sharpe >= 0.3
leg (evaluate.py:36, :101) is non-binding except when the Newey-West long-run variance is far below the
naive variance; the bar is in practice the p-value alone. Fix the 0.6; optionally add S = 0.3 (power
0.13) so the reader sees that the registered Sharpe floor is below the detectable range.

**S5. Section 2 line 31 "x the frozen IDM" is imprecise.** The code freezes the 12 x 12 correlation
matrix and recomputes the IDM on the live sub-matrix each day (strategy.py:117-118,
core.idm_for_live:128-134; S3.5). The frozen value 2.3518 holds only when all 12 are live (recomputed:
1/sqrt(w'Hw) on the floored matrix = 2.3518129452424255, equal to the stored value; FDM likewise
1.1313802916085167). Fix: "x the IDM computed from the frozen correlation matrix (config_f1.json idm)
over the live instruments; 2.3518 when all 12 are live".

**S6. Section 4's history is not independently reconstructible and understates one ruling.** (a) The
01:05 draft is not preserved (see section 1); put its text, or its sha256 recovered from the lead's
transcript, in the freeze record. (b) "at the November 2021 post's own parameters" (line 53): the main
greedy rows use a 0.5 correlation shrink, which is pysystemtrade's value, not the post's (ruling R-B6;
config_f1.json greedy.correlation.shrinkage; carver_sources.md B.3 D3). lead_spec_B.md S8 B-R4 still
says the shrink is "not applied"; neither R-B6 nor R-B7 appears in the spec. Record both rulings in S8
(or state in the draft that S8 is superseded by config_f1.json's `source` strings). (c) "about 0.2-0.3"
(line 54) -> "0.19 (0.16 without the yield micros; 0.29 with the book scalars)". (d) Line 58 "it is
listed as an open choice in reports/E.22_RETURN.md": the file does not exist yet; write "will be
listed".

**S7. No test pins forward/tables_f1.json to config_f1.json.** tests/test_forward_core_strategy.py:169
builds the tables in memory with microbook.config_build.build_tables(cfg); nothing loads the file the
operator will pass as `--tables`. Add a test: `runner.load_tables("forward/tables_f1.json")` equals
`{c: instruments[c].multiplier}` and `{c: instruments[c].cost_per_side_usd}` from config_f1.json, same
key order. Also replace the `status` strings "DRAFT written by MicroBookCoder ... the lead ... freezes
it" in config_f1.json, tables_f1.json and rolls_f1.json ("DECLARED ... the lead freezes it") before
hashing, since the hashes and the ledger fingerprint cover them.

**S8. Abandonment is a selective-stopping path unless its reporting is fixed.** Section 9 line 113-115:
the user may stop the test ("abandoned, no verdict"). State that an abandoned E22-F1 stays in N (it
does, from registration) and is reported in the program record with its descriptive figures at the
stop date and the reason, so the file drawer is visible; and that a restart of the same rule is a new
ID and N + 1 (section 9 says "never restarted under the same ID", which leaves this implicit).

### NOTE

**N1.** Section 1 line 13: the quoted command lacks the required flags; screening/trial_registry.py:
240-246 requires `--freeze`, `--freeze-sha256` and `--harness-sha256` as well. Current N = 532
confirmed (`trial_registry status`: r006-E21 N 528 -> 532).

**N2.** A non-finite forecast would hold the previous position silently under simple rounding:
core.buffered_round:166 compares `last` with NaN edges (both False) and returns `last`; nothing flags
it. It cannot happen once an instrument is live (vol is defined after 10 differences and ffilled,
liveness needs 256), so no fix is required; a `np.isfinite(nstar).all()` check in strategy.py:129 would
make it fail loud.

**N3.** Declared exchange-closed days (section 6 line 76-77, runner.check_date:168-191) are the
operator's statement; add "and must match the exchange's published holiday calendar" so the
declarations are checkable after the fact. Declaring an open day closed merges two days' moves into one
record (P&L preserved, one fewer observation); not a P&L leak.

**N4.** The interim look (report.py) prints mean, sd and n_days, from which a reader can form a t by
hand; this is inherent in any descriptive look. The text's "No p-value is computed at a look" is
accurate for the code (report.py has no t or p; evaluate interim returns neither, README choice 12).

**N5.** Constants verified: every config_f1.json key has a `source`; FDM and IDM recomputed from the
stored matrices equal the stored values (above); the IDM matrix is symmetric with unit diagonal and
positive definite (smallest eigenvalue 0.063); `idm.instruments` equals `instruments_order`;
tables_f1.json equals config_f1.json on all 24 figures. `warmup_diffs` 256 is declared "not a Carver
figure"; fine.

**N6.** Rounding halves away from zero (core.round_half_away) where pysystemtrade rounds half to even
(carver_sources.md A13b, C note); declared immaterial by B-R3; agreed.

**N7.** The four frozen D8 per-side costs (MNQ 1.05, M2K 1.09, MGC 2.04, MCL 1.58) are derived in
microbook/study.py:62-75 from the instrument frame's `cost_buy`/`cost_sell` at the 2024-02-29 mark,
which needs a store read; the brief forbids data/ reads, so they are [unverified by recomputation].
The eight extension costs (commission / 2 + one tick) recompute by hand from the config's tick values:
MNG 0.96 + 1.00 = 1.96, M6E 0.50 + 1.25 = 1.75, yields 0.96 + 1.00 = 1.96, MZC/MZS 0.96 + 2.50 = 3.46,
MZL 0.96 + 1.20 = 2.16: all match.

**N8.** Section 8 line 106-107 "a PASS is strong evidence": one pre-registered one-sided test at 0.05
is evidence; "strong" is the lead's word to defend. Not a correctness issue.

**N9.** The greedy, though not used by E22-F1, was checked against carver_sources.md B.1: start at zero,
direction sign(optimum) with sign(0) = +1, one contract per step, stop when no step improves, objective
sqrt(gap' Sigma gap)/C + 250 x sum|cost x trade|/C (annualised TE as a fraction of capital; the
incremental update var + 2 d sg_i + Sigma_ii at core.py:288 is algebraically right), the three-step
buffer with adjustment max((x - b)/x, 0) and rounded trades (core.py:317-338). Shrink 0.5 is the code's
value (R-B6), the buffer 0.0125 is not rescaled from 25% to 20% (B-R4). No defect found.

**N10.** pytest: `nice -n 10 uv run python -m pytest -q -p no:cacheprovider tests/test_forward_*.py`:
139 passed in 17.05s (free memory 10.8 GB before the run).

## 3. What I verified and how

Text against B4 (docs/prompts/STAGE_E.22.md:121-127): rule (section 2), universe (3), rounding method
(4), start date (7; see B2), 36-month horizon (7; evaluate.HORIZON_MONTHS = 36, window [start, start +
36 months) via add_months, which clamps to month end), the bar (8: one-sided Newey-West lag 10,
Bartlett, p from the normal, p <= 0.05 AND net Sharpe x sqrt(252) >= 0.3; evaluate.py:33-46, :67-101,
:176-190, inclusive comparisons on both sides), the 6-monthly look that changes nothing (9; report.py
has no t or p and prints NOTHING_LINE), N 532 -> 533 (1, 10; registry at 532). Nothing in the
registration fetches data, buys, computes a p-value on history, or lets a look stop or change the test;
the study report and microbook code contain no p-value (grep).

Bar implementation: I recomputed the Newey-West long-run variance, se, t and the annualised Sharpe for
an 800-day autocorrelated synthetic series with my own numpy formula (divisor T, Bartlett weights
1 - k/11, sd ddof 1): identical to evaluate.newey_west and evaluate.annualised_sharpe to 1e-15.
statsmodels is not installed, so no third-party cross-check. Refusal before 36 months (evaluate.py:
171-175) and the interim path (164-170, no t or p) read as the text says. A zero-variance series gives
t None -> p None -> FAIL (passes():101).

Look-ahead: runner.step order is fill pending orders at settle(t) (runner.py:256-263), roll at
settle(t), mark to market q(t-1) x (p(t) - mark(t-1)) x multiplier (:254-255), then call the strategy
with history through t (:352-356), whose targets fill at settle(t+1). A signal from settle(t) therefore
first earns P&L on t+2; fills and rolls add no gross P&L on their own day; a roll closes at the old
contract's settle and re-marks at the new one's (:216-229, :264-265), so no gap P&L is booked. The
strategy sees only rows through t (history.py; the row for t holds settle(t) prices of every contract
the source delivered).

Missing data: an instrument without its reference contract's settlement is flagged, its pending order
expires, its position and mark are carried, and the strategy keeps its previous target (runner.py:
245-251; strategy.py:123-124 `out = prev.copy()`, `today` mask); a whole missing day writes a P&L-0
record with `missing_day` (runner.py:332-336) that evaluate counts (section 6 agrees). Weekday gaps are
refused unless declared closed (check_date). Ledger: canonical JSON, sha256 chain, refuses rewrites,
backwards dates, blank or truncated lines (ledger.py:68-100, :157-166).

Sizing: Carver's subsystem position (daily cash vol target / instrument value vol) x F/10 x w x IDM,
with daily cash vol target = C x tau / 16 and instrument value vol = M x sigma(dP), reduces to
(F/10) x C x tau x IDM x w / (M x 16 x sigma(dP)) = core.unrounded_position (core.py:138-142) with
annual_dollar_vol = M x 16 x sigma (core.py:62-64). Average position = position at forecast 10
(core.py:145-147; A13). Vol: ewm std span 35 min 10 adjust True, slow ewm span 2560, blend 0.3/0.7,
floor 1e-10 (core.py:37-49; A12). EWMAC: ewm(span, min_periods 1) fast minus slow over vol.ffill()
(core.py:68-72; A1), scaled by the A6b scalars, capped 20, equal-weight x FDM 1.1314, capped 20
(core.py:89-106; A8). Yield micros: multiplier 1000 per 1.00 yield point = $10 per bp, tick 0.001 =
$1.00; sizing $ vol = 1000 x 16 x sigma(dy in %) = 10 x 16 x sigma(dy in bp) (S3.6). All 12 tick x
multiplier products equal the config's tick_value.

Integer arithmetic: buffered_round returns integer-valued floats; target_positions returns
int(round(p)) of those (strategy.py:146); runner refuses non-integers (runner.py:280-281).

Not done: D8 cost recomputation (needs a store read), roll-calendar check (no network), third-party
Newey-West check (statsmodels absent).

## 4. Recheck of draft 2

Recheck 2026-10-16 01:53-01:55 PDT (`date`), on reports/stage_e22_prereg_F1.md "DRAFT 2" (mtime
01:51:58), forward/config_f1.json and tables_f1.json (01:50:05), rolls_f1.json (01:50:13; status text
unchanged, as the coordinator said), lead_spec_B.md (01:52:13), tests/test_forward_tables_pin.py
(01:50:05), reports/stage_e22_briefs/prereg_F1_draft_0105.md. pytest `tests/test_forward_*.py`:
142 passed in 22.74s (139 + the 3 pin tests).

Counts after recheck: original findings 20, RESOLVED 19, NOT RESOLVED 0, left as-is by agreement 1
(N2). NEW: 0 BLOCKING, 1 SHOULD FIX, 1 NOTE.

| Finding | Status | Evidence |
|---|---|---|
| B1 tables_f1.json outside the freeze | RESOLVED | Section 2 lines 27-31 names it and the identity with config_f1.json; section 5 line 74 points at it; section 11 hashes "every file in section 2". Pin test present (3 tests, pass): key order, multipliers, costs. |
| B2 start / --clock-start / zeros | RESOLVED | Section 7 lines 101-103 (start = first ledger record's date), 116-119 (series = every record in the window incl. zero and missing days; evaluate and report WITHOUT --clock-start; a run with it "is not the registered evaluation"). Section 6 lines 82-84 moves the source/approval/start/warm-up sha to docs/DECISIONS.md and the STATE file; the "start record" wording is gone. |
| S1 warm-up undefined / yield splice | RESOLVED | Section 7 lines 104-109: the source's own back history, no owned-store splice, >= 260 dates, HistoryRow format, fingerprinted; "< 257 prior settlements -> flat until 256 differences" matches strategy.py:78 and config warmup_diffs. |
| S2 rolls pre-clock correction; roll_overdue consequence | RESOLVED (clause) | Section 7 lines 110-115 and section 2 lines 32-34 (exception named). The abandonment trigger's flag name is wrong; see NEW-1. |
| S3 back-fill clause | RESOLVED | Section 6 lines 93-94: second source only before the day's record; recorded day never changed. |
| S4 power arithmetic; Sharpe leg | RESOLVED | Section 8 lines 128-132: 0.13 / 0.22 / 0.53 (my values 0.13 / 0.218 / 0.535); the non-binding Sharpe leg stated. |
| S5 IDM wording | RESOLVED | Section 2 lines 39-41. |
| S6 history reconstructible; R-B6 recorded; numbers; "will be listed" | RESOLVED | Draft 1 preserved; sha256sum of reports/stage_e22_briefs/prereg_F1_draft_0105.md = 904c194d46d8d201e05a984bea43500a686078f63496a6fcf4927482c50bfc6d (equals the status line), and its section 4 line 45 chooses the greedy. lead_spec_B.md S8 lines 185-189 record the rulings (as B-R6/B-R7; see NEW-2). Numbers at line 61-63: 0.47 / 0.41 / 0.95 / 0.29 / 0.20 without shrink / 0.75 all match reports/stage_e22_microbook.md section 4 line 131-133 and section 10 line 293. Line 67-68 "will be listed". |
| S7 pin test; status strings | RESOLVED | tests/test_forward_tables_pin.py (3 tests). config_f1.json and tables_f1.json status: "DECLARED for E22-F1 ... frozen by the E22-F1 registration (section 11)". rolls_f1.json keeps the CHECK_FLAG text that forward/rolls.py:206 requires; consistent with the pre-clock clause. |
| S8 abandonment reporting | RESOLVED | Section 9 lines 138-141: stays in N, reported with descriptive figures and reason, restart = new ID and N + 1. |
| N1 registry command | RESOLVED | Section 1 lines 15-17: all three required flags present. |
| N2 NaN forecast holds silently | left as-is | By agreement (no fix required; cannot occur once live). |
| N3 holiday calendar | RESOLVED | Section 6 line 89. |
| N4-N7, N9, N10 | no action needed | Informational. N5: FDM 1.1314 and IDM 2.3518 recomputed again from the unchanged matrices; tables == config re-verified by the pin test. |
| N8 "strong evidence" | RESOLVED | Section 8 line 132: "evidence for one at the registered level". |

**NEW-1 (SHOULD FIX, not blocking). The abandonment trigger in section 7 lines 113-115 names a flag
the runner does not set in the hazardous case.** The text: "If a held position's contract has no
settlement on or after its roll anchor before the roll executed (`roll_overdue` with a non-zero
position), E22-F1 ends abandoned." In forward/runner.py, `roll_overdue:I` is set only inside `_roll`
(:213-214), which runs only when the held contract DID settle that day (`_instrument_day` returns at
:245-251 when it did not, setting `missing:I` and `order_expired:I`). So when the held contract stops
settling (the stuck-position case of S2), the ledger shows `missing:I` on every later day and never
`roll_overdue:I`; the registered trigger would not fire and the lead would face a choice after data
exist. Fix (one sentence): "E22-F1 ends abandoned when a non-zero position's reference contract is
past its roll anchor date (forward.rolls.expiry_guard) and the roll has not executed, whichever flag
the runner sets (`missing:I` on or after the anchor, or `roll_overdue:I`)". The condition is checkable
from the record's `positions[I].contract`, `positions[I].qty` and the date against rolls_f1.json.
Pre-data and conservative, so not a bar issue; fix before the freeze because it is a text-only line.

**NEW-2 (NOTE). Ruling labels differ across files.** The draft (section 4 lines 62-67), config_f1.json
and the study report write "R-B6"/"R-B7"; lead_spec_B.md S8 lines 185-189 write "B-R6"/"B-R7" (the
spec's own convention B-R1..B-R5). A grep for one label misses the other. Pick one, or add "(= B-R6,
B-R7 in lead_spec_B.md)" to the draft's section 4.

Other checks on draft 2 with no finding: section 2's code list now includes forward/__init__.py and
forward/history.py (both missing from draft 1; the fingerprint and hash lists now cover every module
in the package); section 11's supporting-file list is resolvable (reports/stage_e22_microbook.json
exists, 149,695 bytes, mtime 01:35; tests/test_forward_*.py matches the pin test's name); the
pre-clock exception in section 2 and the frozen-after-first-record rule in section 7 are consistent
with the runner's fingerprint (rolls are in `config_sha256`, runner.py:123).
