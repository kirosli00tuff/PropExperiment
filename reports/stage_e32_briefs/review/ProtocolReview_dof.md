# ProtocolReview_dof: hidden degrees of freedom and selection integrity in reports/stage_e32_discovery_protocol.md

Reviewer: DofReviewer-FableXHigh (claude-fable-5-1; the lead confirms the model from the transcript). Lens: every
choice an implementer or the E.33 lead could still make after seeing an outcome, every definition with two readings
that give different values, and the consistency of P7-P10 with each other and with docs/prompts/STAGE_E.33.md.
Object: reports/stage_e32_discovery_protocol.md, DRAFT v0.2, 647 lines (read in full). Started 07:32 PDT 2026-10-27.
Scripts and outputs: reports/stage_e32_briefs/review/work_protocol_hidden/ (checks.py, cal_check.py; no market data
opened, no web access, no data/ path touched). Line numbers below are the protocol's unless a file is named.

Severity as the brief defines it: BLOCKING = would leak, would let an outcome steer a choice, would make a number
entering a verdict wrong, or cannot be run as written; SHOULD FIX = two readings with different outcomes, a missing
rule, an unstated assumption, a wrong number not changing a verdict; NOTE = clarity.

## Findings table

| ID | Section, line | Severity | One line |
|---|---|---|---|
| DO-1 | 0.2 l.34-36 (and E.33 prompt l.51-53, B3) | BLOCKING | "Most conservative" decisions have no deadline relative to outcomes; a reading can be chosen in P8 after the funnel is seen |
| DO-2 | P7.2 l.567-568; P8 G4 l.582-583 | BLOCKING | The user's "drop the protocol-added test DSR" decision moves the selection threshold 0.2007 -> 0.1724 and has no cut-off before registration |
| DO-3 | P7.1 l.542-546 | SHOULD FIX | The 300 IDs do not match screening.trial_registry's `_ID` regex; registration as written is refused |
| DO-4 | P7.1 l.546 vs P8 G3 l.580 | SHOULD FIX | "the registered N at E.33's start" (538) contradicts G3's "N after E.33's registration" (838); G3 differs 0.1678 vs 0.1724 |
| DO-5 | P8 Tier B l.594-596 | SHOULD FIX (BLOCKING if DO-2 is resolved by dropping the added DSR) | Tier B = next two by SR_d are near-duplicates of Tier A #1, which minimises the V14(c) variance and empties the program DSR |
| DO-6 | P6.2 l.489-490; P8 G3-G4, ranking l.589 | SHOULD FIX | "sample SD" for SR_d against moments()'s population SD; the gap (1.1e-4 to 1.6e-4) straddles the 1e-4 tie band |
| DO-7 | P8 ranking l.589-591 | SHOULD FIX | A tie band of 1e-4 is not transitive; two sorts give two Tier A lists |
| DO-8 | P3.6 rule 3 l.275-277 | SHOULD FIX | 2022-11 and 2022-12 have NOPA placeholder rows (`2022-11-MISSING`, blank time): "has a NOPA row" and "time 12:00 counts" give opposite exclusion sets |
| DO-9 | P3.4 l.246-247; P3.6 rule 5 l.280; F2.8, F3.1 | SHOULD FIX | "Book update" is undefined: a record or an F_LAST event (16% of ZM records are intra-event); first-touch, lock checks and OFI differ |
| DO-10 | P3.8 l.296-298 | SHOULD FIX | The program runner's 2-minute minimum hold (D9.3, `hold_below_2min`) is neither adopted nor declined; TB exits can come in seconds |
| DO-11 | P4 G4 l.318-319 | SHOULD FIX | The clipped set is ambiguous for C.3-C.6 (C.4 = log depth reaches 5 at 147 contracts) |
| DO-12 | 0.3 l.52-54; F1.1, F1.3, F1.7, F4.7, F4.10; G5 l.320; G5(c) l.586 | SHOULD FIX | No SD convention (ddof, weighted SD form, OLS residual SD) anywhere; B3's 1e-9 agreement cannot hold and every such gap becomes a 0.2 decision |
| DO-13 | F3.12 l.386 | SHOULD FIX | OLS slope with or without an intercept is not stated; the two slopes differ |
| DO-14 | P8 G5(d) l.587-588 | SHOULD FIX | Tercile cut points: quantile definition and boundary side unstated |
| DO-15 | P3.7 l.290-293 | SHOULD FIX | "span covers m": minute marks (h+1) or minute intervals (h); weights differ by h/(h+1), G7 agreement fails |
| DO-16 | F3.9 l.383 | SHOULD FIX | A modify that moves an order off the touch price is neither a cancel nor "size-reducing"; counted or not changes CR5 |
| DO-17 | P5 LGBM l.441-450; LT3 l.409-411 | SHOULD FIX | LightGBM bin boundaries (max_bin 255) must come from the fold's training rows only; not stated and not in LT3 |
| DO-18 | P10 l.637 | SHOULD FIX | "3 times the P5 estimate": the estimate is a range to be replaced by a probe; the stop's base is undefined |
| DO-19 | P5 l.474-475, P10 l.638-640 vs E.33 C3 | SHOULD FIX | Deadline 01:00 vs 00:00 and "feature set" vs "family": the protocol must say it supersedes C3's wording |
| DO-20 | P8 vs E.33 D1 | SHOULD FIX | D1 lists per-firm trade-through nets, FDR and "sessions" inside "apply P8 exactly"; P8 gates on none of them |
| DO-21 | P4.2 l.422-427 | SHOULD FIX | "At least 20 null searches" permits reruns until a pass; "the planted configuration family enters Tier A" is undefined |
| DO-22 | P5/P6 (no text); E.33 C2 | SHOULD FIX | A configuration with one failed fold fit: failed, or evaluated on five folds? Two different objects |
| DO-23 | P3.5 l.256-258 | NOTE | mu_k when a class has zero training weight is undefined |
| DO-24 | P5 LOGIT l.435-437, LGBM l.441-445 | NOTE | Implicit settings: class_weight None, fit_intercept True, row order for saga, label mapping {-1,0,1} -> {0,1,2} for LightGBM |
| DO-25 | P1.1 l.81-83 | NOTE | The 3-date store check names no dates and compares counts only |
| DO-26 | P8 G3 l.579; P9 l.622 | NOTE | ">= 0.95" at discovery, "> 0.95" in the program verdict; an undefined DSR should be said to fail G3 |
| DO-27 | P7.2, P9 l.621-624 | NOTE | b_test is computed at N 838; the test's "list's program N" may be larger by then |
| DO-28 | F4.11 l.397, F4.13 l.399, C.15 l.347, Tier A 0.70 l.593 | NOTE | Declared constants with no cited source; say they are declared, not derived |
| DO-29 | P6.4 (ii) l.509 | NOTE | min(60 s, h/5) is 60 s for every h if h/5 is in minutes; units unstated (report-only) |
| DO-30 | P1.5 item 1 l.132-134 vs item 3 l.138-139 and M3 g.3 rule 3 | NOTE | The release window's evidence list (M3 g.3) includes E.31's -8.98 markout; item 1's "no E.31 statistic sets a threshold" should carve out the exclusion window explicitly |
| DO-31 | P3.6 rule 3 "intersects", rule 5 "in force on D"; C.7 | NOTE | Interval boundary conventions and which definition record is "in force" |
| DO-32 | P8 l.598-599 | NOTE | The tested object (6-model average) is not the selected object (per-fold OOF); no DOF, but the power statements assume they coincide |
| DO-33 | F3.7-F3.8 l.374-375 | NOTE | Seasoning: fills and size-decreasing modifies (priority-keeping) reset the clock or not; snapshot orders' time |
| DO-34 | F3.11 l.385; F4.6 l.392; 0.3 l.55-57 | NOTE | Refill unit (records or contracts); Hi/Lo over updates or minute marks; window half-openness |
| DO-35 | P8 Tier B l.594; P9 l.621 | NOTE | Say Tier B is bought and run on the test whatever Tier A's size (P9 implies it; P8's "when Tier A has one member" reads otherwise) |
| DO-36 | P4 G3 l.315-317 | NOTE | Family flags: "else 1" is implicit |

Counts: BLOCKING 2, SHOULD FIX 20, NOTE 14. Total 36.

## How to read the fixes

Every proposed fix is replacement text for the protocol. Where I name a choice (population SD, F_LAST events,
intercept in F3.12), I give the reading I would defend as the conservative or standard one; the lead decides. What
matters for this lens is that one reading is written down before E.33's first real-outcome fit.

---

## BLOCKING

### DO-1. Interpretive decisions have no deadline relative to outcomes (0.2 l.34-36)

As written (l.34-36): "A detail this text does not settle and that can affect an outcome is decided by E.33 in the
most conservative way and logged (E.33 prompt). Details that cannot affect an outcome (file layout, names,
parallelism, logging) are E.33's."

The E.33 prompt (l.51-53): "A choice the protocol does not cover is decided in the most conservative way and logged.
The protocol is never changed." B3: "if the protocol text was ambiguous, the most conservative reading is chosen and
logged."

What is wrong. "Most conservative" is not an operational rule: for a tie band, a tercile boundary, a month with a
placeholder NOPA row (DO-8) or the two readings of "covers m" (DO-15), both readings can be argued conservative, and
the one that is chosen decides which configurations pass. The text puts no time limit on these decisions. The
ambiguities I found in P8 (DO-6, DO-7, DO-14) would be met while P8 is being coded or run, after the 300 OOF series
exist. An implementer who sees that reading A puts configuration X into Tier A and reading B does not is choosing
an outcome, whatever the log says. B3's version is safe only because B3 runs before any model (feature and label
agreement on 20 dates); the general 0.2 clause has no such guard. P1.5 item 5's promise ("no person or model chooses
among configurations after seeing outcomes") is not kept by the text as it stands.

Fix (replace l.34-36 with):
"A detail this text does not settle and that can affect an outcome is decided before E.33's registration (its C1):
every such decision is written, with the two readings and the one chosen, in reports/stage_e33_protocol_readings.md,
whose sha256 enters the pipeline freeze (B7) and the registration note. After the first real-outcome fit no new
interpretive decision is made: a question that arises then is answered by the frozen readings file, and if it is
not answered there, that part of E.33 stops and reports (0.2, second bullet). P8 in particular is coded and unit-
tested on synthetic series (P4.2) before any real OOF series exists, so that every tie, boundary and gate rule is
exercised before an outcome can inform it. Details that cannot affect an outcome (file layout, names, parallelism,
logging) are E.33's at any time."

### DO-2. The user's decision on the protocol-added test DSR can move the selection threshold after outcomes (P7.2 l.567-568; P8 G4 l.582-583)

As written (l.567-568): "If the user drops the protocol-added test DSR (return section 7), b_test = 0.1017 and the
selection threshold is G3's 0.1724." G4 (l.582-583): "b_test from P7.2 at the registered N."

What is wrong. p7_final_budget300.md (section "Power gate G4") gives the two regimes: with the added DSR, G4 = 0.2007 binds; without
it, G4 = 0.1373 and G3's 0.1724 binds. Recomputed with the program's deflated_sharpe_ratio (checks.py section 6):
0.2007 and 0.1373, G3 0.1724. A configuration with discovery SR_d in [0.1724, 0.2007) is in Tier A under one regime
and out under the other. The protocol does not say when the user decides. "Return section 7" is E.32's decisions
list; the E.33 prompt tells its lead not to ask and to decide and log open choices. If the user has not ruled by the
time E.33 reaches P8, E.33's lead picks b_test with the funnel in front of it; if the user rules after seeing E.33's
funnel (the E.33 return is reviewed before any purchase), the same selection on outcomes happens one level up. Either
way an outcome steers the threshold.

Fix (replace l.567-568 with):
"G4 uses b_test = 0.1649 (the protocol-added test DSR applies). Dropping the protocol-added test DSR is an amendment
under 0.2: it is valid only if the user records it before E.33's registration (C1), in which case the frozen protocol
version E.33 runs carries b_test = 0.1017, G4 = 0.1373 and the binding selection threshold 0.1724. No change to
b_test is admitted after registration, whatever the funnel shows."
And add to P8 G4: "b_test is the value frozen in the protocol version whose sha256 E.33 verified at start."

---

## SHOULD FIX

### DO-3. The configuration IDs cannot be registered as written (P7.1 l.542-546)

As written: ID "E33-<S1..S5>-<FH05|...>-<L-C0.01-r0 | ... | G-d3-m200>", registered "in ledger/trial_registrations.jsonl
(screening.trial_registry) before any real-outcome fit".

Evidence. screening/trial_registry.py l.48: `_ID = re.compile(r"[A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}")`, applied
with fullmatch in register() (l.213-216): one hyphen, alphanumerics only, at most 16 characters after it. checks.py
section 1: `'E33-S1-FH05-L-C0.01-r0' fullmatch _ID: False`, `'E33-S5-TB30-G-d3-m200' fullmatch _ID: False`,
`'E33-S1FH05LC001r0' fullmatch _ID: True`. The registry is harness code; E.33 may not loosen its regex (0.2 allows
fixing E.33's code, not the program's). Under 0.2 "names" are E.33's, so E.33 would invent a mapping; the protocol,
the registry and the finalists file would then carry different IDs, and nothing says which is canonical.

Fix (append to P7.1 after the ID line):
"Registry IDs (screening.trial_registry accepts `E33-` plus at most 16 alphanumerics): E33-<set><label><grid>, with
set S1..S5, label FH05|FH15|FH30|FH60|TB15|TB30, and grid LC001r0|LC001r5|LC01r0|LC01r5|LC1r0|LC1r5 for the six LOGIT
points (C 0.01, 0.1, 1; rho 0, 0.5) and Gd2m50|Gd2m200|Gd3m50|Gd3m200 for the four LGBM points. Example:
E33-S1FH05LC001r0 (13 characters after the hyphen). The long form above is the display name; the registry ID is
canonical in every table and in reports/stage_e33_finalists.md." (I checked the longest: S5TB30Gd3m200 and
S1FH05LC001r5 are 13 characters.)

### DO-4. Two statements of N (P7.1 l.546 vs P8 G3 l.580)

As written (l.546): "the registered N at E.33's start is used in every DSR". G3 (l.580): "N = the registered N after
E.33's registration".

What is wrong. "At E.33's start" is 538 (ledger/trial_registrations.jsonl, last entry n_after 538; current_n() 538
in checks.py). G3 at N 538 would be 0.1678, at 838 it is 0.1724 (program function). The P7.2 heading and G3 make the
intent clear, but the P7.1 sentence says the opposite, and it is the sentence closest to the registration step.

Fix (l.546): replace "the registered N at E.33's start is used in every DSR" with "the registered N immediately
after E.33's registration (838 if no other stage registers first) is the N in every discovery DSR (G3) and in b_test
(P7.2); E.33 quotes it before the first fit and p7_final.py is rerun at that N if it is not 838."

### DO-5. Tier B as the next two by SR_d minimises the program verdict's DSR variance (P8 l.594-596)

As written: "Tier B (2 configurations, run on the test window only to supply the program verdict's DSR variance and
PBO when Tier A has one member; never finalists): the two highest-ranked configurations by SR_d among all 300 that are
not in Tier A, whatever their gates."

What is wrong. The configurations ranked just below Tier A #1 are its grid neighbours (same set and label, another C
or rho, or the LGBM point next to it); Tier A's own rule rejects anything with correlation above 0.70, so the
rejected near-duplicates are exactly what Tier B collects. stage_e_verdict.edge_chain (l.548-551) takes the Sharpe
variance over Tier A when it has two or more series, else over every run series (A plus B); dsr_table (l.219)
uses statistics.pvariance of those Sharpes. With near-duplicates the variance is close to 0 and expected_max_sharpe
(funnel/multiple_comparisons.py l.78: sqrt(variance) x term) is close to 0, so the program DSR degenerates to
Phi(t). Simulation (checks.py section 7; T 870, N 838, 4,000 reps per cell, Tier A true daily Sharpe 0.12, which is
below b_test 0.1649): P(program DSR > 0.95) is 0.000 when Tier B is independent of Tier A, 0.429 at rho 0.70, 0.805 at
rho 0.90, 0.927 at rho 0.98; the median E[max SR] falls from 0.075 to 0.012. The lead's own design notes
(work/lead/design_notes.md l.52-54, 68-69) name this soft spot and add the protocol-level DSR with V = 1/(T - 1) as
the answer; DO-2 shows that answer is user-droppable. The Tier B rule is mechanical (no one chooses), but it is
pinned in the direction that favours a pass, and it is the only rule in P8 with that property.

Fix (replace l.594-596 with):
"Tier B (2 configurations, bought and run on the test window to supply the program verdict's DSR variance and PBO
when Tier A has one member, V14 c; never finalists): continue the Tier A walk down the full ranking of all 300
configurations with the gates ignored, taking a configuration if its OOF daily series has Pearson correlation
<= 0.70 with every configuration already taken (Tier A and Tier B); the first two taken are Tier B. If fewer than
two qualify, Tier B is filled by the highest-ranked remaining configurations and E.33 reports the correlations."
Severity note: if the user drops the protocol-added test DSR (DO-2), this item becomes BLOCKING, because the program
DSR is then the only DSR at the test and the present Tier B rule makes it pass at true Sharpes far below b_test.

### DO-6. SD convention for SR_d against the verdict code and the tie band (P6.2 l.489-490; G3, G4; ranking l.589)

As written (l.489-490): "daily Sharpe SR_d = mean/SD (sample SD), skewness and raw kurtosis (as
screening/stage_e_verdict.py moments() computes them)". Ranking (l.589): "Ties (|difference| < 1e-4)".

What is wrong. moments() (stage_e_verdict.py l.178-189) uses statistics.pstdev (population SD) for sd, skew and
kurtosis and sharpe = mean/sd. The protocol asks for sample SD for SR_d but population moments for skew and kurtosis,
so SR_d and the moments fed to deflated_sharpe_ratio are on two conventions, and the test verdict will use the
population Sharpe. The size: at T 796, SR_pop 0.17 -> SR_sample 0.169893 (gap 1.07e-4); 0.20 -> gap 1.26e-4; 0.25 ->
1.57e-4 (checks.py section 3). The gap is the size of the tie band, so which convention is used decides which pairs
are ties, and G3 and G4 move in the fourth decimal (no verdict change on its own, but see DO-7).

Fix (l.489-490): "daily Sharpe SR_d, SD, skewness and raw kurtosis exactly as screening.stage_e_verdict.moments()
computes them (population SD, n in every denominator); the same function supplies G3's moments, G4's se(SR_d), the
ranking key and the tie test." Add to G5(c) (l.586): "mean/SD x sqrt(n) with the same population SD".

### DO-7. The tie band is not a total order (P8 l.589-591)

As written: "Ranking of the configurations that pass G1-G5: SR_d descending. Ties (|difference| < 1e-4) go to fewer
trades per date, then LOGIT before LGBM, then the lower set index, then the shorter horizon (FH before TB at equal h),
then the earlier grid point in the P7.1 order."

What is wrong. "Within 1e-4" is not transitive: with SR_d 0.20150 (A), 0.20142 (B), 0.20134 (C), A ties B and B
ties C but A does not tie C. If B has the fewest trades per date, one implementer sorts A, B, C by SR then applies
the tie key pairwise and gets B, A, C or A, B, C depending on the comparison order; another rounds first. The Tier A
walk then sees different first members and different correlation partners. The memory rule "define ties and derive
every candidate's key number before ordering" is half met: ties are defined, the order is not.

Fix: "Ranking key: SR_d rounded to 4 decimal places (round half to even), descending; then trades per date
ascending; then LOGIT before LGBM; then the lower set index; then the shorter horizon (FH before TB at equal h); then
the earlier grid point in the P7.1 order. The key is a total order; E.33 sorts by it once."

### DO-8. NOPA placeholder rows make rule 3 two-valued in 2022-11 and 2022-12 (P3.6 l.275-277)

As written: "Every row of those six reports with time 12:00 ET counts whatever its evidence grade; a calendar month
with no NOPA row gets its rule date (the 15th, or the next trade date if the 15th is not one) at 11:00 CT."

Evidence (cal_check.py on the two hashed files; hashes match the protocol's): usda_releases.csv holds two NOPA rows
with date `2022-11-MISSING` and `2022-12-MISSING`, time blank, evidence "MISSING: 2022 NOPA reporting-dates PDF not
found". Every other month 2020-12..2024-02 has one NOPA row at 12:00 (39 of 39 months have a row; 0 have none; none
has two). Reading A: those months "have a NOPA row", the row has no 12:00 time, so no NOPA window is excluded in
2022-11 and 2022-12. Reading B: a placeholder is not a row with a date, so the rule date applies (2022-11-15 and
2022-12-15, both weekdays). Different exclusion sets, different rows and trades in two of the 39 months, which also
feed G5 (b)-(c) month statistics. Also found: the extension file has a leading comment line and three
`-NORELEASE` rows (Export Sales only, outside the six reports), which a strict CSV read must skip.

Fix (l.276-277): "Every row of those six reports whose date parses as a calendar date and whose time is 12:00 ET
counts whatever its evidence grade; a calendar month with no such NOPA row (including the months whose NOPA row is
a placeholder with no date or time: 2022-11 and 2022-12 in usda_releases.csv) gets its rule date (the 15th, or the
next trade date if the 15th is not one) at 11:00 CT. The extension file's comment line and its `-NORELEASE` rows are
skipped. E.33 lists the resulting 39 NOPA dates and all 12:00 release dates in its return before the first fit."

### DO-9. "Book update" is undefined: record or F_LAST event (P3.4 l.246-247; P3.6 rule 5 l.280; F2.8-F2.9 l.370; F3.1-F3.3 l.378)

As written (l.246-247): "tau_up = the first ZM book update u in (t + L, t + L + h min] with M_ZM(u) >= m0 + b(t)".
Rule 5: "no span with an update at which the ZM book lacks a bid or an ask". F2.8: OFI "summed over the MBP-1 updates
in the window"; F3.1: "as F2.8 on the ZM top of book from MBO".

What is wrong. Data facts 1.5: ZM MBO has 1.195 records per F_LAST event and 16.27% of records share ts_event with
the previous record of the same instrument; MBP-1 has 1.09 records per event. Between the records of one event the
book passes through states that never existed as a quotable book (a level emptied by fills before the replenishing
add in the same event, a one-sided or crossed touch). Reading A (per record) can trigger a barrier or a rule-5
exclusion on such a transient state; reading B (after each F_LAST event) cannot. The two give different tau, different
TB labels and different rule-5 exclusions, and different OFI sums wherever intra-event states move the touch. 0.3
defines "known at u" per record (ts_recv <= u), which settles as-of lookups but not what an "update" is for first-
touch and for sums over updates.

Fix (add to 0.3): "A book update is the state after the last record of one event (the record with F_LAST set, data
facts E10); first-touch searches (P3.4), the locked-or-halted check (P3.6 rule 5) and sums over updates (F2.8-F2.11,
F3.1-F3.4) use book updates. 'As of u' lookups use the state after every record with ts_recv <= u; if that state has
no valid mid (0.3), the lookup is invalid." And in P3.4: "an update at which M_ZM is invalid is skipped by the
barrier search (it still triggers rule 5 for the span)."

### DO-10. The runner's 2-minute minimum hold is neither adopted nor declined (P3.8 l.296-298)

As written: "at most 20 entries per trade date (the program's entry cap, screening/stage_e_runner.py 31-39; that
runner's 10-minute mean-holding floor is a bar-runner rule and is not adopted: the firms' hold-time rules are 5-10 s,
M6 5.3)".

Evidence. stage_e_runner.py l.31-36 lists three D9.3 rules: the 21st entry (refused), "an exit sooner than 2 full
minutes after an opening fill (refused likewise)", and the 10-minute mean hold (labelled); l.138 LABEL_MIN_HOLD =
"hold_below_2min". The protocol adopts the first, declines the third, and says nothing about the second. TB exits
(P3.4) happen at the first barrier touch, which can be seconds after the entry fill. An implementer following "the
program's entry cap" may import the engine's refusal of early exits with it; another will not. The realised P&L and
the trade count differ.

Fix (l.297-298): "...is not adopted, and neither is that runner's refusal of exits within 2 full minutes of the
opening fill (D9.3, LABEL_MIN_HOLD): barrier exits fire at the first touch whatever the elapsed time. Only the entry
cap is adopted."

### DO-11. The clipped set is ambiguous (P4 G4 l.318-319)

As written: "every z-type and ratio feature is clipped to [-5, 5] after its own normalisation; features bounded by
construction (C.1, C.2, C.7-C.15, F1.5, F3.5-F3.9, F4.6) are not clipped."

What is wrong. C.3 (min(s, 5)), C.4 (log(1 + qb_1 + qa_1)), C.5 (a log ratio) and C.6 (log sigma) are in neither
list. C.4 exceeds 5 whenever touch depth exceeds e^5 - 1 = 147 contracts, which a deep ZM touch reaches; clipping it
or not changes the feature and every fit. C.5 is a ratio in log form; one reader clips, one does not.

Fix: "Clipped to [-5, 5]: F1.1-F1.4, F1.6-F1.8, F2.1-F2.11, F3.1-F3.4, F3.10-F3.12, F4.1-F4.5, F4.7-F4.13, C.5. Not
clipped: C.1-C.4, C.6-C.15, F1.5, F3.5-F3.9, F4.6." (C.4 unclipped keeps its scale; the lead may prefer clipping C.4
at log(1 + 200); either way the list must be exhaustive: 59 features, each in one list.)

### DO-12. No SD or weighted-SD convention anywhere (0.3 l.52-54; F1.1 l.355; F1.3 l.357; F1.7 l.361; F4.7 l.393; F4.10 l.396; G5 l.320-321; G5(c) l.586)

As written: "sigma_X(D): the SD of 1-minute mid changes"; "sd_30"; "sd_e = the fit's residual SD"; "sd_g = the SD of
the same quantity over the 20 trade dates"; "sd_gap"; "RV15 = SD of the 15 one-minute mid changes"; G5 "scaled by the
training fold's weighted mean and SD"; G5(c) "mean/SD x sqrt(n)".

What is wrong. Each SD can be population (n) or sample (n - 1); the OLS residual SD can divide by n, n - 1 or
n - 3; a weighted SD can be sum w (x - m)^2 / sum w or carry a Bessel-type correction. The differences are 1/(2n)
relative: 1.7% at n = 30 (sd_30), 2.6% at n = 20 (sd_g, sd_gap), 3.5% at n = 15 (RV15), well above G7's 1e-9
tolerance. So B3's agreement test fails on every one of them unless the two coders happen to agree, and each failure
becomes a 0.2 "most conservative" decision (DO-1) with no conservative side. Feature scales also shift LOGIT's
effective regularisation through the standardisation. None of this changes a verdict by itself; all of it is a
reading an implementer must choose.

Fix (add to 0.3): "Every SD in this protocol is the population SD (divide by the count, numpy ddof = 0), including
sigma_X(D), sd_30, sd_g, sd_gap, RV15 and the SDs of P6.2 and G5(c). The residual SD of an OLS fit (sd_e) divides the
residual sum of squares by the number of samples. The weighted mean and SD of G5 are sum w x / sum w and
sqrt(sum w (x - m)^2 / sum w)."

### DO-13. F3.12's OLS slope: intercept or not (l.386)

As written: "lam60 = the OLS slope of dM_ZM (ticks) on signed volume (B - S, contracts) over the 60 one-minute
intervals ending at t".

What is wrong. A regression through the origin and one with an intercept give different slopes whenever the mean
signed volume over the hour is not zero, which is the normal case. Kyle's lambda is conventionally fitted with an
intercept (M1 4.2 writes the Hasbrouck-style regression with one); the text does not say.

Fix: "the OLS slope, with an intercept, of dM_ZM (ticks) on signed volume (B - S, contracts) over the 60 one-minute
intervals ending at t, using only the intervals that contain at least one trade".

### DO-14. Tercile cut points and boundaries (P8 G5(d) l.587-588)

As written: "mean daily net > 0 within each tercile of sigma_ZM(D) (cut points from the 796 OOF dates' values;
sigma_ZM(D) is known before D opens)".

What is wrong. "Tercile" leaves the quantile estimator (numpy's nine methods differ by up to one rank) and the
boundary side (does a date at the cut go up or down) open. With 796 dates the 1/3 cut falls between ranks; a
configuration whose low-tercile mean is near zero can pass or fail on one date's assignment. M5b b.2 item 5 asks for
cut points "frozen in the protocol"; here they are computed, which is fine (sigma needs no model), but the rule must
be exact.

Fix: "Sort the 796 OOF dates by sigma_ZM(D) ascending (ties by date); tercile 1 = ranks 1..265, tercile 2 = 266..530,
tercile 3 = 531..796. Mean daily net (zeros included) > 0 in each."

### DO-15. "Span covers m": minute marks or minute intervals (P3.7 l.290-293)

As written: "for minute m, c_m = the number of rows of the same label type and date whose span covers m ... u_i = the
mean over the minutes m in span_i of 1/c_m".

What is wrong. A span [t, t + L + h] with L = 1 s contains h + 1 minute marks (t, ..., t + h) and h full one-minute
intervals (plus one second of the next). AFML's concurrency counts return bars (M3 d.2: labels "are concurrent at t
if they are a function of at least one common return"), that is intervals. Marks give h + 1 terms per row, intervals
h (or h + 1 if the one-second overhang counts). The weights differ by about h/(h + 1) (17% at h = 5), G7 agreement
fails, and the sum of weights (the effective sample size) changes.

Fix: "for each one-minute interval [m, m + 1 min) of the day session, c_m = the number of rows of the same label type
and date whose span [t, t + L + h] (TB: [t, tau + L]) intersects the interval in more than one second; u_i = the mean
of 1/c_m over the intervals that span_i so intersects."

### DO-16. Price-changing modifies at the touch (F3.9 l.383)

As written: "CR5 = (Ca_5 - Cb_5)/(Ca_5 + Cb_5): contracts removed by cancels and size-reducing modifies at the price
that was the best ask (Ca) or best bid (Cb) at that moment".

What is wrong. mbo_book31 (header l.6) treats a modify to a new price as remove-and-insert; such a modify takes the
order's whole size off the touch but is not "size-reducing". Counted or not, CR5 changes materially (price
improvements and pull-backs are a large share of touch removals). Two readings.

Fix: "contracts removed from the touch by cancels, by size-reducing modifies (the reduction) and by modifies to
another price (the whole size), at the price that was the best ask (Ca) or best bid (Cb) when the record arrived;
fills are not removals".

### DO-17. LightGBM bin boundaries from training rows only (P5 l.441-450; LT3 l.409-411)

As written: "max_bin 255 ... Inner validation block: the latest 15% of the fold's training dates"; LT3 tests "that the
scaler, the calibrator and the mu_k use training rows only".

What is wrong. LightGBM builds its histogram bins from the Dataset it is constructed on. M4 b.5 names the trap
("Binning (histogram) bounds computed on the full sample ... Build the Dataset from the training fold only and
construct validation and test with reference= to the training Dataset") and the protocol's leakage tests do not cover
it; a Dataset built on all rows of a horizon is the convenient implementation. Bins built with evaluation rows are a
(mild) look at the evaluation distribution; and two implementations (B3) that differ here produce different trees.

Fix (P5 LGBM): "The lightgbm.Dataset (bin boundaries) is built from the fold's inner-training rows only; the inner
validation block and the evaluation fold are constructed with reference= to it." (LT3): add "and that LightGBM's bin
boundaries come from inner-training rows only (unit test on a fold with a distinct evaluation distribution)".

### DO-18. The compute stop has no defined base (P10 l.637)

As written: "measured compute above 3 times the P5 estimate, or two out-of-memory failures".

What is wrong. P5 gives ranges ("10-60 s a fit", "1-4 hours of wall time") and says a timed probe "replaces the guess
before the full run". Three times 1 hour and three times 4 hours are different stops, and a stop after outcomes
exist decides which configurations P8 sees (P10's own third bullet). A stop whose trigger E.33 can place is a
choice; it must be fixed before the run.

Fix: "measured wall time of the search above 3 times the projection E.33 writes to reports/stage_e33_STATE.md from the
P5 probes before the first real-outcome fit (the projection names the probe times and the formula), or two
out-of-memory failures".

### DO-19. Deadline and cut unit against E.33 C3 (P5 l.474-475; P10 l.638-640)

As written (P10): "E.33's deadline (its prompt: work stops at 01:00 PDT on 2026-10-28): runs follow the P5 order, so a
cut leaves whole feature sets". E.33 C3: "Order the runs by family, so that a cut still leaves complete families. If
the full budget cannot finish by 00:00 on 2026-10-28, finish whole families."

What is wrong. Two deadlines (00:00 for the search in C3, 01:00 for all work in the prompt's header) and two units
(feature set in the protocol, "family" in the prompt; S5 contains all four families). The protocol binds first, but
the E.33 lead reads both, and the subset P8 runs on depends on which it follows.

Fix (P10): "The search order of P5 and this deadline supersede the wording of E.33's C3 ('by family', '00:00'):
configurations are cut by whole feature set in the P5 order; no new configuration starts after 00:00 PDT 2026-10-28
and running ones finish or are recorded as failed by 01:00." (The lead may prefer the other times; one pair must be
written.)

### DO-20. E.33 D1 lists gates P8 does not have (P8 against E.33 prompt D1)

As written (E.33 D1): "Apply the selection rule P8 exactly: net expected ticks per trade after costs for each firm
under the trade-through rule; trade counts; the deflated Sharpe at the full N; FDR (and Holm, for reference); PBO via
CSCV; stability across months and sessions; no single month dominating."

What is wrong. P8 gates on the Topstep market variant only (G2), has no FDR gate (P7.2 lists FDR thresholds as
references that gate nothing), runs PBO as a report (P6.3), and has one session. A lead reading D1 as a checklist
could add a per-firm trade-through net or an FDR cut as a gate "to apply P8 exactly", and any such addition made
after the funnel is seen is a selection on outcomes.

Fix (add to P8 after the gate list): "These five gates and the ranking are the whole selection rule. E.33's D1 items
map as follows: per-firm trade-through nets are P6.4 reports; FDR and Holm are the P7.2 reference thresholds,
reported; PBO is P6.3, reported; 'sessions' is void (one session). Nothing in D1 adds a gate."

### DO-21. The synthetic proofs leave a retry and an undefined pass criterion (P4.2 l.422-427)

As written: "E.33 runs at least 20 null searches; more than 1 non-empty Tier A in 20 fails the proof" and "The proof
passes if the planted configuration family enters Tier A in at least 14 of 20 seeds".

What is wrong. "At least 20" lets E.33 run 40 and read "more than 1 in 20" as "more than 2 in 40", or rerun a failed
batch of 20 with new seeds. The proof gates whether the real search runs at all (P10 stops on a failure that cannot be
fixed), so a retry is a hidden choice even though it precedes outcomes. "The planted configuration family enters Tier
A" does not say whether Tier A must contain a configuration whose feature set includes the planted family (S_k or
S5), one whose feature set is exactly S_k, or one at the planted horizon.

Fix: "E.33 runs exactly 20 null searches with seeds 20261027 + 1..20 and exactly 20 planted searches with seeds
20261027 + 101..120; no search is rerun or added. The null proof fails if more than 1 of the 20 has a non-empty Tier
A. The planted proof passes if, in at least 14 of the 20, Tier A contains a configuration whose feature set includes
the planted family (S_k or S5) at the planted label type." (Binomials checked: P(>= 2 of 20 | 0.05) = 0.264,
P(>= 14 of 20 | 0.80) = 0.913.)

### DO-22. A configuration with a failed fold fit (no text; E.33 C2)

As written: nothing in the protocol; E.33 C2: "a configuration that errors is counted, and recorded as failed with
the error". P10: "every configuration run stays in N".

What is wrong. If one of the six fold fits fails (saga exception, LightGBM error, out of memory on one process), the
configuration can be recorded as failed (no OOF series, fails every gate) or evaluated on the five folds that ran
(zeros on the failed block). The second object has a different series and can pass the gates. Which one is produced
is a choice made when the failure is seen, possibly after other configurations' outcomes.

Fix (add to P5): "A configuration with any failed fold fit is recorded as failed with the error, has no OOF series,
fails G1 and stays in N; no fold is refit with changed settings. A LOGIT non-convergence warning is not a failure
(the fit is used as is)."

---

## NOTE

### DO-23. mu_k for an empty class (P3.5 l.256-258)
If a class has zero training weight (conceivable for y = 0 at TB15 on a volatile fold), mu_long_k is undefined and
sklearn needs all three classes present to fit a 3-class model. Add: "a fold whose training rows lack a class
records the configuration as failed (DO-22)" or "mu_k = 0 and p_k = 0 for a class absent from training".

### DO-24. Implicit model settings (P5 l.435-437, l.441-445)
State: class_weight None; fit_intercept True; rows passed in (date, t) order (saga's sampling path depends on row
order, so an unconverged fit does too); the label mapping {-1, 0, +1} -> {0, 1, 2} for LightGBM's multiclass
objective and the inverse on its scores (a wrong order silently swaps mu_k); warm_start False. sklearn's saga does not
penalise the intercept (only liblinear does) and sklearn 1.9.1 uses the multinomial loss for saga on three classes
without a multi_class argument [from the library's documented behaviour, not re-fetched here]. LightGBM's
`deterministic = true` with `force_row_wise = true` is documented to give the same result for different num_threads
[official parameter docs as I recall them; E.33 should verify in its environment with a two-thread-count equality
test], so "at most min(8, cpu//2)" is reproducible; a unit test makes it so.

### DO-25. The E.31 store check (P1.1 l.81-83)
"checks it against the raw files on 3 dates (equal record counts per date)" names no dates and compares counts only.
Suggest: the first OOF date, a roll date and the last OOF date; compare sha256 of the (ts_recv, action, price, size,
order_id) columns, not counts.

### DO-26. Inequality direction and undefined DSR (P8 G3 l.579; P9 l.622)
Discovery G3 is "DSR >= 0.95", the program verdict is "> 0.95" (stage_e_verdict._chain_verdict: d_value > DSR_MIN).
Harmless at these decimals but write both the same way. Add to G3: "a DSR the function cannot compute (degenerate
moments, sd = 0) fails G3", mirroring the verdict code.

### DO-27. N at the test (P7.2; P9 l.621-624)
b_test and G4 are computed at the N registered after E.33 (838). The program verdict uses "the list's program N",
which is whatever is registered when the test list is hashed; if another stage registers first, the test's DSR bar
is higher than the one G4 powered for. Say so in P9 ("E.33's selection assumed N 838; the test uses the N at its list
hash; a larger N is reported as reduced power, never as a reason to re-select").

### DO-28. Declared constants without a source (F4.11 |B*| >= 3; F4.13 12:15; C.15 Jun-Aug; Tier A rho <= 0.70;
G5 9 of 13, 25%, 2.5)
None of these comes from a cited measurement and none was set on an outcome; the text should say "declared" for
each so a later reader does not look for a derivation. The CORe burst threshold (|T| > 4.0 on their statistic) is a
different statistic from F4.11's 2-minute z-score.

### DO-29. P6.4 (ii) timeout units (l.509)
"within min(60 s, h/5)": with h in minutes, h/5 is 1 to 12 minutes and the minimum is always 60 s; if h/5 were read
in seconds the timeout is 1 to 12 s. Report-only, so no selection effect; write "within 60 s" or "within min(60 s,
h/5 minutes)".

### DO-30. The release window's evidence includes an E.31 statistic (P1.5 item 1 vs item 3; M3 g.3 rule 3)
P1.5 item 1: "No E.31 statistic sets a sign, threshold, look-back or weight." M3 g.3 rule 3, which the protocol
adopts, lists "E.31's passive fills '0-5 minutes after a USDA release' averaged -8.98 ticks" as evidence beside Huang
and Joseph and Garcia. Item 3 already says the window is set from R4 and M3 and is wider than E.31's split; item 1
should add "the exclusion window of P3.6 rule 3 is the one place an E.31 figure appears in the rationale, as
corroboration of a literature-set width, not as its source".

### DO-31. Boundary conventions (P3.6 rule 3 "intersects"; rule 5 "in force on D"; C.7)
Say whether [R - 2 min, R + 30 min] is closed and whether a span ending exactly at R - 2 min intersects it; which
definition record is "in force on D" (the latest with ts_recv before D's 08:30 open); whether C.7 counts D itself
and the expiration date.

### DO-32. Selected object versus tested object (P8 l.598-599)
The OOF Sharpe that selects a configuration comes from six single-fold models each scored on its own block; the test
runs the average of the six. This is pinned (no DOF) and averaging should not hurt, but the P7.2 power statements
treat the two as one model; E.33's P6.5 reversed walk-forward is the nearest rehearsal and should be read with that
in mind.

### DO-33. Seasoning details (F3.7-F3.8 l.374-375)
"Last add or modify (by ts_recv) at least 1.000 s before t": say that a fill (on_fill) and a size-decreasing modify
(which keep priority in mbo_book31) do, or do not, reset the clock, and that snapshot orders take the snapshot's
ts_recv. E.31's Book keeps no per-order time (orders are [side, price, size, prio], mbo_book31.py l.43), so this is
new code either way.

### DO-34. Units and sampling (F3.11 l.385; F4.6 l.392; 0.3 l.55-57)
F3.11: refills counted as add records or as contracts. F4.6: Hi and Lo over every valid mid in [08:30, t] or over
the minute marks. 0.3: a window of k minutes ending at t is (t - k, t] or [t - k, t] (ties at a nanosecond mark are
rare but definitional).

### DO-35. Tier B always runs on the test (P8 l.594; P9 l.621)
P8 says Tier B supplies the variance "when Tier A has one member"; P9 computes "the Tier A and Tier B daily series"
unconditionally. Say in P8 that Tier B is bought and run whatever Tier A's size (it is unused in the verdict when Tier
A has two or more).

### DO-36. Family flags (P4 G3 l.315-317)
"its family flag (C.11-C.14) is 0 for that row if any feature of the family is invalid": add "and 1 otherwise".

---

## Coverage: what I checked and found sound (counts)

Numbers recomputed with the program's functions or my own scripts (checks.py; 9 sections, all reproduce):
- P4.2 binomials: P(>= 2 of 20 | 0.05) = 0.264 (text 0.26); P(>= 14 of 20 | 0.80) = 0.913 (text 0.91); 300 x
  P(Z > 4.86) = 1.8e-4 (text about 2e-4). 3 of 3.
- P7.2 at N 838 via funnel.multiple_comparisons: SR0 0.1137; G3 0.1724 (t 4.86), 0.1756 at skew -0.5 kurtosis 6;
  t > 3 at T 870 = 0.1017; DSR_test 0.1649; b_test 0.1649; G4 0.2007; G4 without the added DSR 0.1373; the joint
  select-and-pass table (0.026, 0.109, 0.417, 0.908 against the text's 0.03, 0.11, 0.42, 0.91). 10 of 10. Hashes
  of usda_releases.csv, usda_releases_ext.csv and verify_discovery_hashes.py equal the protocol's. 3 of 3.
- Grid sizes 273, 263, 248, 218; folds 133 x 4 + 132 x 2 = 796; 39 months = 13 Dec-Feb quarters; feature counts
  C 15, F1 8, F2 11, F3 12, F4 13, sets 23, 26, 27, 28, 59; budget 5 x 6 x 10 = 300; current N 538. 7 of 7.
- Entry cap: binds only at h = 5 (46 back-to-back trades possible against 20); LGBM min_data_in_leaf 50h-200h is
  0.6%-6.9% of a fold's rows. 2 of 2.

Rules I traced for hidden choices and found pinned (no finding):
- 0.3 "known at u iff ts_recv <= u": unambiguous because data facts 1.5 report 0 ts_recv decreases per instrument in
  file order (and 0 ts_event inversions); the E.31 time_axis ordering by ts_event therefore coincides on these files.
- P1.4 roll exclusions on ZM.v.0's 24 runs with 5 returns and 1-3-day runs: mechanical by the stated rule.
- P3.3 labels: N is never exactly 0 (integer ticks minus 0.528), so y has no tie. P3.5: an exact EV tie is no trade.
- P3.8: next decision "the first grid minute at or after the exit fill time" is unambiguous for FH (t + h + 1 min)
  and TB (first mark >= tau + L); X_D booked to the entry date; zeros on excluded dates stated.
- P6.1: embargo of 20 dates equals the longest feature look-back, so no training feature reads the evaluation block;
  labels end intraday; the "train on later blocks" direction is declared (M5a c).
- P5: each (C, rho) and (d, m) point is its own configuration; no inner lambda or round selection (M4 a.7's warning);
  early stopping on a date-block inner split; calibration on the inner block; mu_k from all training rows; LOGIT
  objective matches sklearn's C and l1_ratio convention; non-convergence used as is (no retry).
- P6.4 and P6.5 run after the test list is hashed and select nothing; L = 0.3 s is a report; the synthetic proofs
  read no real outcome; failed and unrun configurations stay in N; the 6-fold ensemble is pinned (no refit choice).
  The budget count is right: 300 configurations and nothing else enters N. 7 items.
- P8 G1-G2 and G5(a)-(b) are exact as written (total <= 0 fails (b) through "total net > 0"; the first quarter is
  the OOF part of Dec 2020-Feb 2021); Tier A's correlation is on the 796-date OOF series and is undefined only for a
  constant series, which cannot pass G1; the Tier A walk is mechanical.
- P9 matches stage_e_verdict.edge_chain: Holm on Tier A p_upper at K = 9 (V14 b; the list carries k_holm), the
  V14 c variance rule (Tier A if >= 2 else all run series), PBO over the same set, t > 3.0; the protocol-added DSR is
  stated as an addition; "no re-run" is stated.
- P10: no result stops the search; the deadline cut keeps N; the null report is specified.
- P1.5 firewall and P2: every feature traces to a reader citation (F1 Zhou et al. via R3a; F2 M2 b and M1 section 10;
  F3 M1 (a)-(f), 9.1-9.3 and R2's spoofing case for seasoning; F4 R4 4.2, 5.3 and M1 9 with the extremum-timing trap
  removed by fixed windows); the overlaps with K6-crushgap-01, K6-cp1/cp2/cp3, E16-H1/H4, E.20 and E.31's splits are
  disclosed; no sign, threshold, look-back or weight comes from an E.31 number (DO-30 is the one rationale citation);
  the dropped candidates' figures match their sources (R4 2.4's about 10 ticks for 24 events; p7's 3.46 ticks for one
  30-minute trade a date; M2 b; M4 c; M1 8). The four families and the context block are justified by the evidence
  cited, with F4's weak prior stated honestly.
- Consistency P7-P8-P9-P10: thresholds, N, T_disc, T_test, the selection variant and the test bar agree except as
  DO-2, DO-4, DO-19, DO-20 and DO-27 state. Against the E.33 prompt: binding order (protocol first), A1-A2, B1-B7,
  C1-C2, D2-D5 and Part E are consistent with the protocol; C3 and D1 are not (DO-19, DO-20).

## Not checked

- The arithmetic of F2.7, the crush constants and MathReview A's confirmations (ArithmeticReviewer and MathReviewer).
- Leakage paths other than the ones that are also two-readings items (DO-9, DO-17): the LeakageReviewer's lens.
- Feasibility of the compute and disk figures in P5 (FeasibilityReviewer).
- Whether E.31's measure31 functions (day_bounds, instrument_on, roll_reasons, calendar_reason) implement the 0.3
  and P1.4 definitions exactly: I read their names and signatures, not their bodies.
- The LightGBM `deterministic` and sklearn saga intercept statements in DO-24 are from the libraries' documented
  behaviour as I know it; I did not fetch the documentation (no web access used).
- The two release calendars were read for structure (columns, report names, times, placeholder rows) only; no
  release date was verified against a source.

Finished 07:56 PDT 2026-10-27 (started 07:32 PDT; both from `date`).
