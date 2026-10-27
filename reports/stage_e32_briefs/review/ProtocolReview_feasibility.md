# ProtocolReview: feasibility on the ThinkPad and implementability (FeasibilityReviewer-FableXHigh)

Object: reports/stage_e32_discovery_protocol.md, DRAFT v0.2, 647 lines (byte-identical to
reports/stage_e32_briefs/work/lead/protocol_v0.2.md at 07:32 PDT). Reviewed 2026-10-27 07:33-08:05 PDT.
Model: claude-fable-5-1 (this transcript). Lens: can E.33 implement and run P0-P10 as written, within its
prompt's limits (docs/prompts/STAGE_E.33.md: at most 6 workers, at most 2 heavy compute jobs, stop below 2 GB
free, work stops 01:00 PDT on 2026-10-28, two implementations, synthetic proofs, reviews) on this machine
(20 logical CPUs, 15,118 MB RAM, RTX 3050 4 GB; CLAUDE.md compute rules). I did not write the protocol; I assumed
it wrong until checked. No market data was opened (nothing under data/, /mnt/large-storage, ~/.cache, no .dbn,
.zst or .parquet); `df -h`, `free -m` and `nproc` only. No web access (log.tsv has no fetch rows). Scripts and
outputs: reports/stage_e32_briefs/review/work_protocol_feasibility/ (probe_fits.py and .log from the first
launch of this lens at 03:09-03:12, probe_fits2.py and .log at 07:38-07:42, binom_sched.py).

Severity as briefed: BLOCKING = cannot be run as written, or a number entering a verdict would be wrong, or an
outcome could steer a choice; SHOULD FIX = an ambiguity two careful implementers would read differently with
different outcomes, a missing rule, an unstated assumption; NOTE = clarity.

## Findings table

| ID | Section, line | Severity | Finding (short) |
|---|---|---|---|
| FE-1 | P7.1 l.541-545 | BLOCKING | The configuration ID format `E33-S5-FH15-L-C0.01-r0` is refused by `screening.trial_registry.register` (`_ID.fullmatch`: one hyphen, no dots, at most 16 characters after `E33-`); C1 cannot register and the search cannot start as written |
| FE-2 | P4.2 l.418-428 (with P5 l.461-475, P10 l.635-640) | BLOCKING | "run the full pipeline" for at least 20 null and 20 planted searches = 72,000 fits (40 x the real search) plus 40 synthetic record streams of 820 M records each; cannot finish before 01:00 on 2026-10-28 and runs before any real fit |
| FE-3 | P5 l.444-445, 470-471 | SHOULD FIX | "7 worker processes" x LightGBM `num_threads` min(8, cpu//2) = 8 is up to 56 threads against CLAUDE.md's cap (half the cores, never more than 8); the parallelism as written cannot be run under the rules. `deterministic=true` makes the fit independent of `num_threads`, so a cap changes no outcome |
| FE-4 | P10 l.637 with P5 l.466-471 | SHOULD FIX | "measured compute above 3 times the P5 estimate": P5 gives ranges and says a probe replaces them; the reference of the 3x rule is undefined, and "one configuration per model family" for the probe is not the worst case (my two probes differ 20x by class balance and scaling) |
| FE-5 | P1.2 l.85-93, P10 l.635; E.33 prompt l.22-28 | SHOULD FIX | "any read outside P1.2" stops E.33 at once, but P1.2 lists only data, E.31 code and "this protocol and the E.32 briefs": the program's code (screening/, funnel/, prop_econ/, data/), docs and the E.33 prompt's own "Read first: reports/E.31_RETURN.md (all of it)" are outside it or contradict it |
| FE-6 | P6.5 l.521-539, P6.4 l.514-517 | SHOULD FIX | No compute estimate or priority for the diagnostics: SFI is 5 x 59 x 6 = 1,770 refits (about the search); the VECM needs statsmodels, which is not installed and cannot be added after the freeze (uv.lock is in the pipeline hash); P6.4 (iii) reuses E.31 fill code that F 6.2 classes as tied to the virtual-order loop |
| FE-7 | P4.2 l.424-428 | SHOULD FIX | The planted size is "the signal that gives a true OOF daily Sharpe of 0.25 net" without saying whose Sharpe (oracle or fitted pipeline); the fitted pipeline's realised Sharpe is lower, and at a realised 0.20 the 14-of-20 rule passes with probability 0.05: a P10 stop that no code fix can cure |
| FE-8 | P3.6 rule 5 l.280-284; C.7 l.342 | SHOULD FIX | "the definitions in force on D" names no record; `measure31.read_definitions` keeps only the last definition per instrument (F 6.1), so per-date limits need a per-date as-of pass; UNDEF_PRICE (2^63 - 1) is not named as "no limit" |
| FE-9 | P4 G5 l.320-322; P5 l.451-452 | SHOULD FIX | The weighted SD of G5 (biased or unbiased) and the calibrator's `max_iter`/`tol` (sklearn default 100) are not fixed; both change LOGIT coefficients or calibrated probabilities, and only one implementation runs the model step |
| FE-10 | P4 F1.3 l.357, F3.12 l.386; G7 l.330-331 | SHOULD FIX | Two OLS fits on near-collinear level regressors must agree within 1e-9 relative in B3; normal equations versus `lstsq` differ by far more at the condition numbers of (1, M_ZS, M_ZL) levels, and B3 cannot "fix" a numerics-only disagreement without a declared solver |
| FE-11 | P10 l.638-640; P5 l.474-475; E.33 prompt C3 l.156-159 | SHOULD FIX | The deadline clause ranks nothing but the feature sets: it does not say what is cut first (P6.5 items, P6.4 (iii), SFI), whether the features-only store may be built before the freeze, and it says 01:00 where the E.33 prompt cuts the search at 00:00 |
| FE-12 | P5 l.461-475 | NOTE | The AiTrader collector window (15:30-16:00 PT, CLAUDE.md) is not mentioned; a 1-3 h search launched in the afternoon overlaps it; per-date and per-configuration resumability makes a pause cheap |
| FE-13 | P4 F3 header l.374-375 | NOTE | Seasoned depth needs per-order last add/modify ts_recv; `mbo_book31.Book` stores none (orders are [size, prio, price, side] lists), so E.33 keeps its own map; the text counts size-reducing modifies as re-seasoning (CME keeps their priority); say so explicitly |
| FE-14 | 0.3 l.39-41 | NOTE | "All ordering ... use ts_recv": F 1.5 shows ts_recv never decreases per instrument in file order, so this equals file order; say "stable; file order on ties" so the book replay is unambiguous |
| FE-15 | P5 l.432-437 | NOTE | sklearn 1.9.1 deprecates `penalty` (removed in 1.10); the grid maps to `l1_ratio = rho` with `penalty` left at its default; the multinomial loss is automatic (`coef_` shape (3, p)); write the parameter names |
| FE-16 | P8 l.598-601 | NOTE | The frozen fold model's artefacts are not listed: the G5 scaler (LOGIT); the booster at its best iteration plus the calibrator (LGBM); the mu_k; and the P3.6 calendar |
| FE-17 | P5 l.466, 469 | NOTE | "about 170,000 rows": after P1.4 exclusions (about 52 dates) and the release windows, FH15 has about 196,000 rows and about 154,000 per training fold; immaterial to the estimate |
| FE-18 | P5 l.441-453 | NOTE | A booster with no positive-gain split (LightGBM "No further splits with positive gain", best_iteration 1) gives constant raw scores, a near-constant calibrator and a constant EV: say the configuration still runs, counts and is reported as degenerate (not a stop) |
| FE-19 | P4 C.5 l.340 | NOTE | Vbar "at the same minute of day over the 20 trade dates before D": on early-close dates in the look-back some minutes do not exist; say the mean is over the dates where the minute exists |

Counts: BLOCKING 2, SHOULD FIX 9, NOTE 8 (19 findings).

## Findings in full

### FE-1 (BLOCKING) P7.1: the configuration IDs are refused by the registry

Text as written (P7.1 l.542-545): "ID: E33-<S1..S5>-<FH05|...|TB30>-<L-C0.01-r0 | L-C0.01-r0.5 | ... | G-d3-m200>
(the P7.1 grid order). E.33 registers the 300 in ledger/trial_registrations.jsonl (screening.trial_registry)
before any real-outcome fit".

What is wrong. screening/trial_registry.py l.48-49 and l.210-214: `_TEST = re.compile(r"[A-Z][A-Za-z0-9]{0,15}")`,
`_ID = re.compile(r"[A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}")`, and `register` refuses unless
`_ID.fullmatch(t)` and `t.startswith(f"{test}-")`. An ID may hold exactly one hyphen, no dot, and at most 16
alphanumerics after it. My check (uv run, this session): `_ID.fullmatch("E33-S5-FH15-L-C0.01-r0")` is False,
`_ID.fullmatch("E33-S5-FH15-G-d2-m50")` is False, `_ID.fullmatch("E33-S1FH05LC001r0")` is True. Every one of the
300 IDs as written fails, so C1 (the registration before any real-outcome fit) raises TrialRegistryError and the
search cannot start. The registry also refuses a duplicate `test` name, so all 300 must go in one `register`
call, and its FIELDS (schema, entry_id, test, test_ids, freeze_path, freeze_sha256, harness_sha256, n_before,
n_after, time_local, source, note) carry no per-trial hyperparameters: the E.33 prompt's C1 fields (family,
feature set, label, horizon, model, hyperparameters, pipeline sha256, protocol sha256) must live in the freeze
file the registration points to. Existing IDs in the ledger follow the pattern (C1-T1, E16-H1, E22-F1,
E23-MEZFh5).

Proposed replacement (P7.1, the ID sentence and the registration sentence):
"ID: `E33-<set><label><model><grid>` with no further hyphen or dot, so that screening.trial_registry accepts it
(`[A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}`): set S1..S5; label FH05, FH15, FH30, FH60, TB15, TB30; model L or
G; grid for L: C001R0, C001R05, C01R0, C01R05, C1R0, C1R05 (C 0.01, 0.1, 1.0; rho 0, 0.5); grid for G: D2M50,
D2M200, D3M50, D3M200. Examples: E33-S5FH15LC001R0, E33-S1TB30GD3M200 (13 characters after the hyphen; the
limit is 16). The P7.1 grid order is unchanged. Before any real-outcome fit, E.33 writes the 300 rows (ID, set,
label, h, model, hyperparameters, pipeline sha256, protocol sha256) to reports/stage_e33_configurations.md,
hashes it, and makes one call `screening.trial_registry.register(test="E33", test_ids=<the 300 IDs in grid
order>, freeze=<that file>, freeze_sha256=<its sha256>, harness_sha256=<from the harness preflight>)`. A second
registration under the test name E33 is refused by the registry, so a stop and restart re-uses the one
registration (the IDs are already counted)."

### FE-2 (BLOCKING) P4.2: the synthetic proofs as written cannot finish in E.33's day

Text as written (P4.2 l.418-428): "Null: on synthetic books with the tick size, volatility and event rates of
the data facts and no signal, run the full pipeline (features, labels, folds, models, EV rule, daily series,
gates, Tier A). ... E.33 runs at least 20 null searches ... Planted signal: ... The proof passes if the planted
configuration family enters Tier A in at least 14 of 20 seeds". E.33's prompt B5 says the same ("run the full
search pipeline on synthetic order flow ... built with the same tick size, volatility and event rates as the
data facts") and "proves the pipeline on synthetic data ... before it touches real outcomes".

Arithmetic (binom_sched.py). One search = 300 configurations x 6 folds = 1,800 fits. 20 null + 20 planted =
40 searches = 72,000 fits = 40 x the real search. At my second probe's rates (the realistic regime: balanced
classes, standardised correlated features; 3.0 s a LOGIT fit, 9 s an LGBM fit at 5 threads) the real search is
0.9 CPU-h of LOGIT plus 9 thread-h of LGBM, about 1.2 h of wall time under an 8-thread cap; 40 searches are
about 50 h of wall time. At the first probe's rates (99% class 0, unscaled: 20 s and 12 s at 8 threads) the real
search is about 3.1 h and 40 searches about 125 h. The record streams add to it: at "the event rates of the data
facts" one replicate is 414.4 M ZM.v.0 + 248.2 M ZS + 158.0 M ZL = 820.6 M records (F 4.4, 4.1); 40 replicates
are 32.8 G records to generate, split, replay and featurise; the book replay alone is 0.2 CPU-h per replicate
at F 5's 0.5 M records/s (9 CPU-h for 40), and the feature pass is several times the book pass (P5's own guess
is 1-3 CPU-h per pass; 40-120 CPU-h). E.33 has at most 13 h from a midday launch to 01:00, under two heavy jobs
at once, and B5 must finish before the first real fit. The proof as written is therefore a P10 stop by itself
(compute above any P5 figure), and P5's compute estimate does not mention it.

Proposed replacement (P4.2, a new paragraph "Scale" after the first sentence, and the two pass rules kept):
"Scale (so that the proofs run inside E.33's day; the code path, folds, gates and thresholds are the
production ones, nothing is loosened):
(a) Record level, for the feature code: one synthetic ZM MBO stream and one ZS/ZL MBP-1 stream over 30 synthetic
trade dates (20 burn-in plus 10), at the median per-date event rates of F 3.1, with the tick sizes and the
sigma of 0.4, pushed through the production split, book and feature code. It serves LT1 and LT5, and a planted
record-level signal (a known order-flow imbalance placed a known number of minutes before a known mid move)
that the feature code must recover at the stated minute.
(b) Selection level, the null and planted searches: each search runs the production pipeline from the feature
and label tables onward (P3.5-P3.8, P6.1-P6.2, P8) on synthetic tables with the real decision grid, the 796 OOF
dates and the real exclusion calendar, over the declared subset S5 x {FH15, TB30} x the 10 grid points (20
configurations, 120 fits a search, about 1/15 of the real search), with the gates and thresholds of P7.2 and P8
unchanged (N = 838, T_disc = 796). Synthetic mids are random walks at sigma_ZM(D) from 0.4 with a 1-tick spread;
synthetic features are independent of future mids (null) or carry the planted signal (planted). 20 null and 20
planted searches; the pass rules above apply. This subset proves the gates and the pipeline; the null maximum of
the full grid is given analytically in P7.2 (E[max SR] = 0.1137 at N 838; 300 x P(Z > 4.86) about 2e-4), not by
simulation. Cost: 4,800 fits, about 1.6-3.3 h of wall time under FE-3's thread cap; they may run beside B7's
reviews and beside the features-only store of FE-11."
If the lead prefers 10 seeds each (2,400 fits, 0.8-1.7 h): the null rule becomes "0 of 10 non-empty" (a leak
check: P(>= 1 of 10 | 0.05) = 0.40, so the 0.05 bound is stated, not tested; with 20 seeds it was not tested
either: P(>= 2 of 20 | 0.05) = 0.26) and the planted rule "at least 7 of 10" (P(>= 7 | 0.8) = 0.88,
P(>= 7 | 0.914) = 0.99). The replication is the lead's decision; the arithmetic is above.

### FE-3 (SHOULD FIX) P5: the thread arithmetic breaks the compute rules

Text as written: "num_threads at most min(8, os.cpu_count() // 2)" (l.444-445) and "With 7 worker processes at
nice 10, about 1-4 hours of wall time" (l.470-471).

What is wrong. min(8, 20 // 2) = 8 threads per LGBM fit; 7 processes give up to 56 threads on 20 logical CPUs.
CLAUDE.md: "Parallel compute jobs: at most half the cores (use os.cpu_count() // 2, never more than 8), and at
most one heavy computation at a time across the lead and all workers"; the E.33 prompt allows two heavy jobs.
The run as written either breaks the rule or oversubscribes and runs slower than the estimate. No outcome
depends on the fix: LightGBM's parameters page (reports/stage_e32_briefs/pages/M4_models/lightgbm_parameters.html,
the M4 reader's saved copy) says of `deterministic`: "setting this to true should ensure the stable results when
using the same data and the same parameters (and different num_threads)"; saga is single-threaded; numpy's BLAS
is the only other thread source. My probes: LOGIT 2.4-3.5 s a fit (balanced, standardised; 21-22 saga epochs at
0.11-0.16 s an epoch) and 1.9-65.6 s (99% class 0, unscaled; 16-381 epochs); LGBM 8.1-10.0 s at 5 threads,
10.5-13.2 s at 8 threads (no early stop in the pure-noise case: best_iteration 499-500). Under an 8-thread cap
the real search is about 1.2 h (second regime) to 3.1 h (first), inside P5's 1-4 h.

Proposed replacement: "Parallelism: the sum over all running processes of their thread counts stays at or
below 8 (CLAUDE.md: half the cores, never more than 8; the E.33 prompt: at most two heavy jobs). LOGIT fits run
one per process with OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = 1 (up to 7 processes beside one
coordinator); LGBM fits run in at most two processes with num_threads 4 each, or one with 8. `deterministic =
true` with `force_row_wise = true` makes the LGBM fit independent of num_threads (LightGBM parameters page),
so the thread count is an E.33 detail that cannot affect an outcome. Expected wall time under this cap: 1.2-3.1
h for the 1,800 fits (probes of 2026-10-27, work_protocol_feasibility/probe_fits*.log)."

### FE-4 (SHOULD FIX) P10 with P5: the 3x compute stop has no defined reference, and the probe is not the worst case

Text as written: P10 "measured compute above 3 times the P5 estimate" (l.637); P5 "a guess of 1-3 CPU-hours
over the 39 months, to be replaced by a timed probe on 3 dates" (l.466-468); "Guesses: LOGIT (saga) 10-60 s a
fit ... A timed probe on one fold of one configuration per model family replaces the guess before the full
run" (l.469-471).

What is wrong. Three readings give three stop points (3 x the lower guess, 3 x the upper guess, 3 x the
probe), and the stop is a hard "stop at once". The probe as written ("one configuration per model family") can
land on the cheapest point: my two probes of the same grid differ 20x (3.5 s against 65.6 s at C = 1, rho = 0.5)
on class balance and scaling alone, and inside one regime the C = 1 points take 3-30 x the C = 0.01 points
(probe_fits.log: 1.9 s to 65.6 s).

Proposed replacement (P5, the probe sentence): "Before the full run E.33 times, on one fold, the two slowest
grid points of the slowest set, E33-S5FH15LC1R05 and E33-S5FH15GD3M50 (FE-1's IDs), and the feature builder on
3 dates (the median, p90 and maximum message-count dates of F 5), and writes the projection (fits x seconds,
dates x seconds, under FE-3's cap) to reports/stage_e33_STATE.md before the first real-outcome fit." And (P10):
"measured compute above 3 times that written projection (not the guesses of P5), measured at the end of each
feature set".

### FE-5 (SHOULD FIX) P1.2 and P10: the read rule as written stops E.33 at its first step

Text as written: P1.2 "Data allowlist (anything not listed is refused) E.33 may read: (a) the 156 files; (b) the
program calendars ...; (c) the release calendar of P3.6; (d) E.31's code ... never E.31's outputs (runs/,
stats31.md/json, the measure31 tables, the result tables of reports/E.31_RETURN.md, ...); (e) this protocol and
the E.32 briefs." P10: "Stop at once on: ... a guard refusal or any read outside P1.2".

What is wrong. E.33 must also read, and its prompt tells it to read: docs/prompts/STAGE_E.33.md, CLAUDE.md,
docs/DECISIONS.md, reports/E.32_RETURN.md, reports/stage_e32_test_seal.md, docs/soy_test/SOY_TEST_MANIFEST.json
(for the guard), screening/stage_e_verdict.py, funnel/multiple_comparisons.py, screening/trial_registry.py,
prop_econ/, data/holdout, the E.19 simulator, and "reports/E.31_RETURN.md" (E.33 prompt l.22-28: "Read
first: ... reports/E.31_RETURN.md"). The last one contradicts P1.2 (d) directly, and the others are "outside P1.2". The prompt binds the
protocol first ("Binding, in this order: the frozen protocol ... this prompt"), so a careful E.33 lead reading
P10 literally stops before A1. The intent (P1.5 item 5) is a firewall on E.31's measured outcomes, not on code or
documents.

Proposed replacement (P1.2, first sentence): "Market-data allowlist (any market data, derived market-data table
or earlier stage's measured outcome not listed is refused; the program's code, docs, prompts, calendars, the
seal manifest and this stage's own files are not restricted by this list): E.33 may read ...". And in (d), after
"never E.31's outputs": "The lead and the workers do not open the result tables of reports/E.31_RETURN.md
(sections 5-7 and the appendix tables); the E.33 prompt's 'Read first: reports/E.31_RETURN.md' is satisfied by
its sections 0-4 (scope, data, code, guards). Where the prompt and this rule differ, this rule applies." And in
P10: "a guard refusal or any market-data read outside P1.2".

### FE-6 (SHOULD FIX) P6.5 and P6.4: diagnostics with no cost, a missing package, and non-library code

Text as written: P6.5 "Clustered MDA on the folds ... and SFI, with noise canaries"; "The VECM loadings of the
crush (Johansen) ...; statsmodels is not installed, so E.33 writes it with tests or reports it as not done";
P6.4 (iii) "fills simulated with E.31's model (a) K-algorithm and (b) FIFO back of queue (kalgo31 and E.31's
fill code, reused for this report only)".

What is wrong. (i) SFI refits one model per feature: 5 configurations (Tier A and B) x 59 features x 6 folds =
1,770 fits, about as many as the search (1-3 h of wall time), and MDA's permutation count R is not stated (its
cost is R x 59 x 5 simulations; cheap at R = 10, not at R = 1,000). (ii) statsmodels is absent (uv run python:
ModuleNotFoundError, checked 07:33) and pyproject pins no such package; uv.lock is part of the frozen pipeline
hash (E.33 prompt B7: "a sha256 list of every code file, config and environment lock (uv.lock)"), so adding it
after the freeze voids the freeze; a Johansen implementation "with tests" is hours of work on the critical day.
(iii) F 6.2 classes `measure31_core.VOrder`, `Loop`, `Placement`, `InstrumentRun.fill`, `_k_allocation` as "Not
reusable for this purpose" (virtual passive orders on E.31's 5-minute grid); using them at the signal times
means lifting the loop out, which is new code, not reuse. None of (i)-(iii) selects anything, so none threatens
a verdict, but 0.2 says a declared choice that cannot be implemented as written stops that part, and P10's
deadline clause does not say these are the first to go.

Proposed replacement (P6.5, a closing sentence; P6.4 (iii), one clause): "Cost and order: the P6.5 items run
in this order after the test list is hashed: reversed walk-forward (25 fits); results by year, release day,
roll phase and volatility tercile; the day-block bootstrap; the non-return test; the decay profile; robustness;
calibration; clustered MDA with R = 20 date permutations per fold; SFI (1,770 refits; may be run on Tier A only);
the VECM last. No package is added after the freeze: the Johansen fit is written against numpy and scipy with
a test against a textbook example, or reported as not done. Any item not finished by the E.33 deadline is
reported as not done; none affects the test list." P6.4 (iii): "... (kalgo31 as is, and a port of E.31's queue
state machine to the signal times, written and tested by E.33; reported as not done if it is not ready by the
deadline)".

### FE-7 (SHOULD FIX) P4.2: the planted proof can fail for reasons no fix may cure

Text as written: "Planted signal: the minimum planted size is the signal that gives a true OOF daily Sharpe of
0.25 net under the selection variant (about 1.5 ticks net per trade at 15-minute holds and 4 trades a date).
Stated power of selection for it: 0.91 (P7.2 table, normal days). The proof passes if the planted configuration
family enters Tier A in at least 14 of 20 seeds (P(at least 14 | 0.8) = 0.91)."

What is wrong. "True OOF daily Sharpe of 0.25" is the Sharpe of a trader who knows the signal (the oracle under
the P3.5 rule). The fitted pipeline realises less: estimation loss over 6 folds, the class-mean EV rule (P3.5
states the assumption itself), the dead zone. P7.2's own table gives P(select) = 0.914 at a realised 0.25 but
0.492 at 0.20 and 0.195 at 0.17; the 14-of-20 rule then passes with probability 0.999, 0.050 and 0.000
(binom_sched.py). A 20% realised loss turns a sound pipeline into "a synthetic-proof failure that cannot be
fixed without changing a declared choice" (P10), i.e. a stop of the whole stage. The proof should test the
pipeline, not the inevitable estimation loss.

Proposed replacement: "Planted signal: the planted size is the one at which the P3.5 rule applied with the true
class probabilities (the oracle) gives a daily Sharpe of 0.35 net under the selection variant on the synthetic
series (about 2.1 ticks net per trade at 15-minute holds and 4 trades a date); the margin over P7.2's 0.25
power row allows the fitted models up to 30% of estimation loss. The proof passes if a configuration of the
planted family enters Tier A in at least 14 of 20 seeds (P(at least 14 | 0.8) = 0.91) and E.33 reports, per
seed, the planted configuration's realised OOF Sharpe beside the oracle's." (If the lead keeps 0.25, the pass
rule must be stated against the realised oracle-minus-loss Sharpe, or the proof is not a test of the code.)

### FE-8 (SHOULD FIX) P3.6 rule 5 and C.7: which definition record

Text as written: "HL and LL are the front's high and low limit prices in the definitions in force on D ... If
the definitions carry no limit prices for D, the second part is skipped for D and the date is counted." C.7:
"the ZM front's expiration in the definitions".

What is wrong. The Z4 schema carries `high_limit_price`, `low_limit_price`, `expiration`, `min_price_increment`
(F 1.1 field list; databento_dbn.InstrumentDefMsg has all of them, checked; the saved page says "high_limit_price
... The allowable high limit price for the trading day in units of 1e-9"). But a definition record arrives at
least daily plus on changes, and `measure31.read_definitions` returns "The last definition of every outright
future" over all files (F 6.1), so the one reusable reader gives one record per instrument, not the record in
force on D. Two implementers would pick different records (the last before 00:00 UTC, before 19:00 CT on D-1,
before 08:30 CT on D), and the "no limit prices" case has no stated encoding (Databento writes UNDEF_PRICE =
9,223,372,036,854,775,807 for an absent price; `mbo_book31.UNDEF_PRICE` exists).

Proposed replacement: "HL and LL are the `high_limit_price` and `low_limit_price` of the last Z4 definition
record of the ZM front with ts_recv <= 08:30:00 CT on D (E.33 writes a per-date as-of pass over the 70,131
outright definition records, F 1.1; `read_definitions` keeps only the last record and is used for ticks only). A
value of UNDEF_PRICE (2^63 - 1) or 0 in either field means no limit price for D. C.7 uses the `expiration` of
the same record."

### FE-9 (SHOULD FIX) G5 and the LGBM calibrator: two unfixed numerical details that change outcomes

Text as written: G5 "features are centred and scaled by the training fold's weighted mean and SD"; P5 LGBM
"Calibration: a multinomial logistic regression (C = 1e4, lbfgs) of y on the booster's three raw scores, fitted
on the inner validation block with weights w".

What is wrong. (i) "Weighted SD" has two common definitions (divisor sum w, or the unbiased sum w - sum w^2 /
sum w); the penalty of LOGIT acts on scaled coefficients, so the choice moves every LOGIT fit. B3 compares
features and labels only, so the model step has one implementation and no agreement check; the choice must be
in the text. (ii) The calibrator inherits sklearn's `max_iter = 100`, `tol = 1e-4`; in my probe it converged in
34-49 iterations on a healthy booster, but on a near-constant booster (FE-18) lbfgs at C = 1e4 may not, and the
probabilities then depend on the iteration cap. Both are details "that can affect an outcome" (0.2), so they
belong in the declaration, not in E.33's conservative-choice log.

Proposed replacement: G5: "... weighted mean m = sum w x / sum w and SD = sqrt(sum w (x - m)^2 / sum w) over
the training rows ...". P5: "Calibration: sklearn LogisticRegression(C = 1e4, solver 'lbfgs', max_iter 1000,
tol 1e-6, l1_ratio 0) of y on the booster's three raw scores (predict with raw_score = True at the best
iteration), fitted on the inner validation block with weights w; a ConvergenceWarning is logged and the fit
used as is."

### FE-10 (SHOULD FIX) F1.3 and F3.12 with G7: the OLS solver must be declared for B3 to pass

Text as written: F1.3 "OLS on the 1-minute samples ... M_ZM = a + b_S M_ZS + b_L M_ZL + eps in natural units";
F3.12 "the OLS slope of dM_ZM (ticks) on signed volume"; G7 "features equal within 1e-9 relative (1e-12 absolute
near 0)".

What is wrong. F1.3 regresses levels on levels: M_ZS about 1,300 cents and M_ZL about 60 cents with intraday
variation of a few cents, so the design matrix (1, M_ZS, M_ZL) has a condition number of order 1e5-1e6. A solver
on the normal equations loses about cond^2 x 1e-16 = 1e-6 to 1e-4 relative accuracy in the coefficients; an SVD
or QR solver (numpy.linalg.lstsq) loses about cond x 1e-16. Two implementations ("event loop versus
vectorised", E.33 prompt B2) that differ only in the solver would disagree on zR by more than 1e-9 relative, and
B3 says every disagreement is "traced to a cause and fixed in the wrong implementation": here neither is wrong,
and the fix is a declaration. F3.12 (60 points, slope ratio) is better conditioned but the same applies.

Proposed replacement (G7, one sentence): "Every OLS in P4 (F1.3, F3.12) is solved by numpy.linalg.lstsq on
regressors centred by their sample means (the intercept recovered from the means), in float64; two
implementations then agree within G7's tolerance." (Centring removes most of the conditioning problem; lstsq
removes the rest.)

### FE-11 (SHOULD FIX) P10 and P5: the deadline clause must rank the cuts and allow the features-only store

Text as written: P10 "E.33's deadline (its prompt: work stops at 01:00 PDT on 2026-10-28): runs follow the P5
order, so a cut leaves whole feature sets; unrun configurations stay registered and count in N, and P8 runs on
the configurations that ran"; P5 "Run order ... S5, S1, S3, S2, S4". E.33 prompt C3: "If the full budget cannot
finish by 00:00 on 2026-10-28, finish whole families."

What is wrong. (i) The schedule below shows the serial path at 11-13.7 h from launch with no usage-limit pause
(E.31 had three in one day, progress.md E.31 Session cost), so the clause will probably be exercised; it ranks
only the feature sets and says nothing about the order in which P6.4 (iii), P6.5's heavy items, D2's
reference fill models and the synthetic replication give way. (ii) The real feature store (features only, no
label, no return) is 0.5-1.5 h of wall time on the critical path after the freeze; nothing in P4.2 or the prompt
forbids building it after B3 passes, before the freeze (it contains no outcome; LT1 and B3 have run on it), and
rebuilding it if a later fix touches feature code (fingerprinted). Saying so saves about an hour. (iii) The
prompt cuts the search at 00:00 and stops work at 01:00; the protocol quotes 01:00 for the cut.

Proposed replacement: "E.33's deadline (its prompt: the search cut at 00:00 and work stopping at 01:00 PDT on
2026-10-28): the feature store (P4 features at every minute mark, no label) may be built as soon as B3 passes
and before the freeze, fingerprinted by the feature code's sha256 and rebuilt if that code changes; labels,
fits and simulations wait for the freeze and the registration. Fits follow the P5 order, so a cut leaves whole
feature sets; unrun configurations stay registered and count in N; P8 runs on the configurations that ran, with
N unchanged. Under time pressure E.33 drops, in this order and reporting each as not done: P6.5's VECM, SFI, MDA,
P6.4 (iii) and the prop simulator, P6.4 (i)-(ii) for Tier B, then the remaining P6.5 items; the selection
variant's fits, P8 and D4's recomputation are never dropped."

### FE-12 to FE-19 (NOTE)

- FE-12 (P5): add "Heavy jobs are not started between 15:25 and 16:05 PT on 2026-10-27 and are paused if
  running (the AiTrader collector window, CLAUDE.md); the per-date and per-configuration DONE markers make the
  pause free."
- FE-13 (F3 header): `Book.orders` holds `[size, prio, price, side]` (mbo_book31.py l.80-81, l.103-109); there is
  no timestamp, so seasoned depth needs E.33's own `oid -> last add/modify ts_recv` map updated on A and M
  records (and dropped on C to zero, F and R). The text counts any modify, including a size decrease that keeps
  CME priority, as re-seasoning the order; if that is intended say "any A or M record (including size
  decreases)", else "an A record or a size-increasing or price-changing M record".
- FE-14 (0.3): F 1.5 (table rows "ts_event inversions per instrument in file order 0 | 0 | 0" and "ts_recv
  decreases per instrument in file order 0 | 0 | 0") means ordering by ts_recv per instrument is file order;
  add "stable sort; records with equal ts_recv keep file order (sequence)", so a replay never reorders a cancel
  before its add.
- FE-15 (P5 LOGIT): sklearn 1.9.1 (installed and pinned): `penalty` "deprecated in version 1.8 and will be
  removed in 1.10. Use l1_ratio and C instead"; `l1_ratio` default 0.0; with solver saga and three classes the
  fit is multinomial without any flag (`coef_` shape (3, p) in my check, no warning). Write: "LogisticRegression
  (C = C, l1_ratio = rho, solver 'saga', max_iter 2000, tol 1e-4, random_state 20261027, fit_intercept True;
  `penalty` left at its default)".
- FE-16 (P8, the frozen model): list the artefacts per fold model: LOGIT: the G5 means and SDs, coef_,
  intercept_, mu_long_k, mu_short_k; LGBM: the booster text at its best iteration, the calibrator's coef_ and
  intercept_, mu_k; plus the release calendar and the limit-price table (P3.6), each with a sha256 in
  reports/stage_e33_finalists.md.
- FE-17 (P5 rows): 263 x 744 trading dates = 195,672 FH15 rows before the release windows; about 154,000 per
  training fold after the embargo (binom_sched.py). Immaterial; "about 150,000-200,000 rows" would be exact.
- FE-18 (P5 LGBM): in my check a booster with no positive-gain split stopped at best_iteration 1 with constant
  raw scores; with min_data_in_leaf = 200 h = 12,000 at h = 60 on about 110,000 inner-training rows x 0.8
  bagging, shallow trees still split in the probe (7, 6, 7 leaves at depth 3) but a quiet set may not. Say:
  "A booster whose best iteration has no split is kept; the configuration runs, counts and is reported as
  degenerate."
- FE-19 (C.5): "Vbar = the mean over those of the 20 trade dates before D on which the minute exists (early
  closes)".

## Coverage: what I checked and found sound (counts)

Library facts (brief item a), checked against the installed environment with `uv run python` (versions:
scikit-learn 1.9.1, lightgbm 4.7.0, numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, pyarrow 25.0.1, databento 0.82.0,
all equal to uv.lock; statsmodels, polars, numba absent; Python 3.12 per pyproject):
1. LogisticRegression: saga with sample_weight and l1_ratio in {0, 0.5} fits a 3-class multinomial model
   (coef_ (3, p)), no `multi_class` parameter exists, no warning; `penalty` is deprecated (FE-15).
2. The P5 objective "C x sum w l + (1 - rho)/2 ||beta||^2 + rho ||beta||_1, intercepts unpenalised" is sklearn's
   documented elastic-net form (docstring: "l1_ratio * L1 + (1 - l1_ratio) * L2").
3. lgb.train accepts every P5 parameter (objective multiclass, num_class 3, boosting gbdt, learning_rate,
   max_depth, num_leaves, min_data_in_leaf, feature_fraction, bagging_fraction, bagging_freq, lambda_l2,
   min_gain_to_split, max_bin, seed, deterministic, force_row_wise, num_threads) with no "Unknown parameter"
   warning; `lgb.early_stopping(stopping_rounds, first_metric_only, verbose, min_delta)` exists; a weighted
   validation Dataset gives a weighted multi_logloss; `best_iteration` is set and `predict` uses it by default;
   `predict(raw_score=True)` gives the three raw scores the calibrator needs.
4. `deterministic` is documented as stable across num_threads (quoted under FE-3); the page also says
   "setting this to true may slow down the training", consistent with the probes.
5. Timing probes (two, synthetic data, nice 10): see FE-3; the P5 range 10-60 s (LOGIT) and 5-30 s (LGBM)
   brackets the first regime and overstates the second; the 1,800-fit search fits in 1.2-3.1 h of wall time
   under the thread cap; the P5 "1-4 hours" holds once FE-3 is applied.

Schemas (brief items b, c), from F 1.1 and the databento package (no data file opened):
6. Definition (Z4): `min_price_increment`, `expiration`, `high_limit_price`, `low_limit_price`, `activation`,
   `unit_of_measure_qty`, `raw_symbol`, `instrument_class` present (F 1.1, 75 fields; databento_dbn
   .InstrumentDefMsg has each attribute; saved page F_db_definitions.html.txt quotes the limit-price and
   expiration definitions). P3.6 rule 5 and C.7 are implementable (FE-8 fixes which record).
7. MBO (Z1): `order_id`, `price`, `size`, `action`, `side`, `flags`, `ts_event`, `ts_recv`, `sequence` present;
   the MBO page (F_db_mbo.html.txt) gives side as "A sk for a sell order (or sell aggressor in a trade), B id for a
   buy order (or buy aggressor in a trade), or N one", which is what F3.5-F3.6 assume. Sweeps by shared
   ts_event (F3.10), cancels and size-reducing modifies at the touch (F3.9), refills within 100 ms of ts_recv
   (F3.11), seasoned depth (F3.7-F3.8; FE-13) and level-m OFI (F3.4, from `Book.prices` and `level_total`) are
   all computable from these fields plus E.31's Book.
8. MBP-1 (Z2, Z3): `bid_px_00`, `ask_px_00`, `bid_sz_00`, `ask_sz_00`, `action`, `side`, `price`, `size` present
   (F 1.1): F2.8-F2.11 (best-level OFI) and F1.5 (ZS/ZL traded contracts) are computable once the re-split keeps
   them (P1.1 says so; E.31's MBP_COMPACT, measure31.py l.73-76, keeps 7 fields and must be replaced by a new
   dtype in E.33's code, not by editing E.31's).
9. The E.31 split store for ZM (MBO_COMPACT, 10 fields: ts_recv, ts_event, instrument_id, order_id, price, size,
   flags, action, side, sequence; F 4.3) carries every field P4 needs for ZM.

E.31 code (brief item d), by signature and source (reports/stage_e31_briefs/work/pilot/):
10. `mbo_book31.Book` (add, cancel, modify, on_fill, clear, mark_bad, end_snapshot, best, level_total, queue,
    is_valid, top_at), `time_axis`, `UNDEF_PRICE`; `measure31.instrument_on`, `roll_reasons`, `calendar_reason`,
    `read_definitions`, `checked_tick`, `day_bounds`, `split_file`, `load_usda`; `kalgo31.allocate`;
    `stats31_core.bootstrap_weights`, `ratio_stat`, `interval`, `per_day`: all present with those names.
11. The "known ZS/ZL USD-check fix" (0.3) exists: measure31.py l.201-205 `PRICE_UNIT_TO_USD = {"ZM": (1.0,), "ZS":
    (1.0, 0.01), "ZL": (1.0, 0.01)}` with the lead ruling of 2026-10-23 in the comment; `checked_tick` accepts
    cents for ZS and ZL. (README_measure31.md l.72-77 describes the earlier stopping state.)
12. Import chain: measure31 -> measure31_core -> kalgo31, mbo_book31, data.session; measure31 -> data.holdout,
    data.group_session; canary_check31 -> pilot31_common (module-level constants only: account ids, caps,
    session names; no network or key access at import) and verify31. Importing the allowed modules runs no
    purchase code. `roll_reasons` implements P1.4 (i) exactly (roll date and the trade date after; a first date
    with no mapping is "unknown" and excluded); `calendar_reason` returns holiday or late-open reasons (early
    closes come through `cal.holiday`, whose coverage E.33 counts by the rule, as P1.4 says).
13. `measure31.day_bounds` builds the [D-1 16:00 CT, D 16:00 CT) windows the protocol cites (l.400-407).

Program code the protocol binds to:
14. `funnel.multiple_comparisons.deflated_sharpe_ratio(observed_sharpe, n_observations, n_trials,
    sharpe_variance, skewness, kurtosis)` takes V as an argument; at (0.1724, 796, 838, 1/795) it returns DSR
    0.9499 and E[max SR] 0.1137, reproducing P7.2's G3 numbers with the program's function. `expected_max_sharpe
    (838, 1/795)` = 0.1137.
15. `screening.stage_e_verdict.pbo(series: Mapping[str, ndarray])`, `moments`, `dsr_table`, `edge_chain` exist;
    the docstring states Holm at K = 9 (V14 b), DSR > 0.95 at the list's program N with the Tier A variance
    rule (V14 c), daily t > 3.0 and CSCV PBO < 0.5 with 8 blocks of n_days // 8, as P9 describes.
16. `screening.trial_registry.current_n()` = 538 now; `register` exists (FE-1 for the ID grammar);
    screening/stage_e_runner.py l.31-39 states the 20-entries-a-day cap P3.8 cites.
17. Files and hashes: verify_discovery_hashes.py sha256 c329f443...13ab (matches P1.1); usda_releases.csv
    0743c0e2...5119 and usda_releases_ext.csv 55df3b14...eb88 (match P3.6; columns date, time_et, report,
    source_url, evidence support rule 3's "time 12:00 ET" and report-name reading; 182 + 273 data rows);
    reports/stage_e32_briefs/seal/derived_unsealed_files.tsv, pages/F_data_facts/F_db_glbx-mdp3.html.txt,
    reports/stage_e32_test_seal.md, docs/soy_test/SOY_TEST_MANIFEST.json, docs/NULL_CRITERIA_E.md exist;
    data.calendars.grains, data.cme_calendar, data.hist_calendar import; prop_econ/ (assemble, funnel, grid,
    report, returns, rules, types, vec) exists for the P6.4 prop simulator.

Compute arithmetic (brief item e), recomputed:
18. P5 book rebuild: 414,363,576 / 0.76e6 = 545 s = 9.1 min; / 0.39e6 = 1,062 s = 17.7 min (F 4.4, F 5): correct.
19. ZS/ZL re-split: 56.0 + 34.5 = 90.5 s of decoding (F 4.2); 248,167,909 x 80 + 158,044,028 x 80 = 32.5 GB
    (F 4.4): correct. Disk: /mnt/large-storage 689 GB free at 07:33 (F 4.3 saw 739.5 GB earlier the same day;
    50 GB has been used since, still 21 x the need); / has 346 GB free. Predictions for 300 configurations
    (about 200,000 rows x 3 probabilities + 2 EVs, float32) are about 1.2 GB; the per-date BBO histories a few
    GB: no disk constraint.
20. Fit count: 5 x 6 x 10 = 300; x 6 folds = 1,800; LOGIT 180 x 6 = 1,080; LGBM 120 x 6 = 720; P5's CPU-hour
    ranges (3-18, 1-6) follow from its per-fit guesses. Rows: FE-17.
21. Memory: a 170,000 x 59 float64 matrix is 80 MB; saga and LightGBM copies stay under 0.5 GB a process; the
    feature builder peaks at 125-394 MB a process (F 5); `free -m` at 07:33: 10,071 MB available, 5,047 used
    (other sessions), swap 1.5 GB used. Seven LOGIT processes plus two LGBM processes stay under 4 GB; the
    E.33 prompt's 2 GB floor is not approached by the search. The full pytest suite peaks at about 6.9 GB
    (memory note): run it alone at the end, as the prompt says.
22. Trade simulation: 796 dates x at most 273 decisions in a pure-Python state machine is under a second per
    configuration; P6.4 (i)-(ii) and the P3.4 barrier scans on per-date mid histories are vectorisable and
    cheap; (iii) and the prop simulator are the only heavy diagnostics (FE-6).
23. Fold and calendar arithmetic: 133 x 4 + 132 x 2 = 796; 13 quarters Dec-2020..Dec-2023; 39 calendar months
    Dec 2020..Feb 2024; G_h sizes 273, 263, 248, 218 = 278 - h.
24. Binomials in P4.2: P(>= 2 of 20 | 0.05) = 0.264 (text: 0.26); P(>= 14 of 20 | 0.8) = 0.913 (text: 0.91).

Ordering and clocks (0.3): F 1.5's zero ts_recv decreases per instrument in file order make the ts_recv replay
feasible with E.31's Book (FE-14 for ties); the 0.137-0.156% records with ts_recv < ts_event are kept in ts_recv
order as LT4 requires, which the Book does not care about.

Checked in total: 24 sound items above, 19 findings, every section P0-P10 read in full.

## The E.33 day (brief item f): schedule arithmetic

Assumptions: launch at 12:00 PDT on 2026-10-27 (the prompt: "launched after E.32's return is reviewed"; E.32
was still running at 07:50, so midday is the early case); work stops 01:00 (13 h); at most 6 workers and 2
heavy jobs; no usage-limit pause (E.31 had three pauses, 19 h 42 min in a 30 h span, progress.md E.31 Session
cost). Agent durations from E.31's final table (progress.md): SimCoder-OpusXHigh built the MBO book, the K
allocator, the fill models, the loop and the markouts with tests in about 56 min of agent time; FixCoder 36 min;
EngineReviewer 18 min for one engine. B1 and B2 each cover about three times SimCoder's scope (59 features
with book-state extractors, two label types, weights, exclusions with limits and releases, the ZS/ZL re-split,
folds, two model families with calibration, the EV rule, the simulation, the gates, the data guard, LT1-LT6).

| Step | Serial or parallel | ETA | Basis |
|---|---|---|---|
| A gates (hashes of 24.2 GB, seal dry check, harness) | serial | 0.3-0.5 h | NVMe read + sha256 at about 1 GB/s; E.32's run matched 156/156 |
| B1 and B2 coders | parallel | 2-3 h | 3 x E.31 SimCoder's 56 min each |
| B3 agreement on 20 dates and fixes | serial | 1-2 h | the runs take minutes (F 5: 1.1-4.2 s a date for the book); tracing 59 features' disagreements dominates |
| B4 leakage tests, B6 cost model | parallel with B3's tail | 0.5-1 h | TestCoders |
| B5 as written | serial, before any real fit | 50-125 h of fits + 40 record streams | FE-2 |
| B5 as FE-2 proposes | parallel with B7 | 1.6-3.3 h (20 + 20 seeds) or 0.8-1.7 h (10 + 10) | 4,800 or 2,400 fits at probe rates under the 8-thread cap |
| B7 two Fable reviews, fixes, re-check, freeze | serial | 1-1.5 h | E.31 EngineReviewer 18 min for one module |
| C1 registration | serial | 0.25 h | FE-1 |
| C2 feature store (816 dates) | serial after the freeze, or pre-built after B3 (FE-11) | 0.5-1.5 h | 816 x 10-30 s / 5 processes; F 5's book time is the floor |
| C2 1,800 fits + simulations | serial | 1.2-3.1 h | probes, FE-3 cap |
| D1-D3 StatsCoder, D4 VerifyWorker, D5 StatsReviewer | serial | 2-2.5 h | fresh contexts, recomputation from saved predictions |
| E finalists, test registration draft, return | serial | 0.5-1 h | |
| Serial path (B5 per FE-2 in parallel, store pre-built) | | 10.0-13.0 h | 22:00-01:00 from a 12:00 launch |
| Serial path (B5 per FE-2, store after the freeze) | | 10.5-14.5 h | 22:30-02:30 |
| Serial path (B5 as written) | | does not fit | |

Reading: the stage as written does not fit because of B5 (FE-2); with FE-2 and FE-11 applied it fits with
little or no slack, and any usage-limit pause pushes the search into P10's deadline cut, which then works as
designed (whole feature sets, N unchanged) provided P10 ranks the other cuts (FE-11). The protocol cannot move
the prompt's deadline; it can make the proofs and the diagnostics fit it without loosening a gate.

## Brief item (g): the statsmodels gap

statsmodels is not installed (ModuleNotFoundError under uv run) and not in pyproject; uv.lock is part of the
frozen pipeline hash, so no package can be added after the freeze without voiding it. P6.5's "E.33 writes it
with tests or reports it as not done" is implementable only through the second branch on E.33's day; FE-6
makes the no-dependency rule and the fallback explicit. The VECM selects nothing, so no verdict depends on it.

## Brief item (h): what would make E.33 stop under P10 as written

1. C1 refused by the registry (FE-1): a stop before the first fit.
2. P10's "any read outside P1.2" on the prompt's own reading list and the program's code (FE-5): a stop at A1.
3. B5's compute (FE-2): a stop by the 3x rule or by the clock before the first real fit.
4. The planted proof failing on estimation loss alone (FE-7): a stop by "synthetic-proof failure that cannot be
   fixed without changing a declared choice".
5. The 3x compute rule with an undefined reference (FE-4): a stop that two leads would place differently.
6. Not stops: the hash check (E.32 matched 156/156 at 23:11 on 2026-10-26; the script's sha256 matches P1.1); the
   tick check (the cents fix exists); the soy seal (E.33 adds it to the guard, P1.2); statsmodels (the text
   allows "not done"); memory (the search stays far under the 2 GB floor); disk (689 GB free).

## What I could not check

- The feature builder's real throughput (no market data may be opened by this reviewer; I used F 5's book-only
  timings and a multiplier). The probe FE-4 asks for replaces the guess before the run.
- Whether saga on the real standardised features sits in my second regime (3 s a fit) or the first (20 s); the
  class balance at h = 5..60 under the P3.3 dead zone (about 1.5 ticks against sigma_h 7-24 ticks) points to
  the second, which is why I report both.
- The methods brief (reports/stage_e32_methods_brief.md) does not exist yet; I cited the reader files and the
  MathReview files instead (MathReview_D.md exists, 03:10).
- E.33's actual launch time, and whether a usage-limit pause falls in its day.
- The other three lenses (leakage, hidden degrees of freedom, threshold arithmetic) belong to the other
  reviewers; FE-7, FE-9 and FE-10 touch them where an implementability failure would follow.
