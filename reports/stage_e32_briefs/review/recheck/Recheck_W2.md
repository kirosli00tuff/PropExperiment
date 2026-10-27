# Recheck W2: FixVerifierDofA-FableXHigh (items DO-1..DO-11, sections P2-P3)

Worker: FixVerifierDofA-FableXHigh (Fable 5.1, xhigh). Started 08:42 PDT 2026-10-27.
Inputs read (by section): reports/stage_e32_discovery_protocol.md DRAFT v0.3, 738 lines,
sha256 330c4af7379791e3957f13818e31b9900adac722e465030a77925e99fc587e1f (verified);
reports/stage_e32_briefs/work/lead/protocol_v0.2.md (diff only); reports/stage_e32_briefs/review/ProtocolReview_dof.md
(table rows and sections DO-1..DO-11); reports/stage_e32_STATE.md l.356-367; screening/trial_registry.py l.44-56,
124-128, 199-232; screening/stage_e_verdict.py (grep: l.26, 178-183, 209, 219, 231); screening/stage_e_runner.py
l.31-39, 138; docs/prompts/STAGE_E.33.md l.50-66, 88-95, 126-150, 198-204, 228-235; the two release-calendar CSVs
under reports/stage_e31_briefs/research/ (counts only, via work_W2/cal_check.py). No market data opened. No
register() call (work_W2/id_check.py reads the regex objects and current_n() only; output work_W2/id_check.out).

## Per-item table

| ID | Verdict | v0.3 lines | Evidence (verbatim) | Proposed fix if not CORRECT |
|---|---|---|---|---|
| DO-1 | PARTIAL | 34-38 | "Every such reading is written into one file and hashed into the pipeline freeze before the C1 registration; none may be made after the first real-outcome fit (ProtocolReview DO-1). P8 is coded and unit-tested on synthetic series before that fit." | The deadline (before C1) and the P8 synthetic tests are there. Missing from the reviewer's route: the file is unnamed; its entry format (question, readings considered, the one chosen) is unstated; the hash is not tied to the C1 registration note; no stop clause for a question that arises after C1 and is not in the file. Replace l.35-37 with: "Every such reading is written by E.33's lead, before the C1 registration, into reports/stage_e33_protocol_readings.md (per entry: the protocol line, the readings considered, the one chosen and why it is the conservative one); that file's sha256 is a line of the B7 pipeline freeze list and is quoted in the C1 registration note. No reading is made after C1: a question that arises later is answered by that file, and if it is not answered there, that part of E.33 stops and reports (0.2, second bullet)." |
| DO-2 | PARTIAL | 628-629, 639-642, 661-662 | l.639-641: "b_test is pinned at 0.1649 (N 838, T_test 870). The user may drop the protocol-added test DSR only by a decision recorded before E.33's C1 registration; then b_test = 0.1017 and the selection threshold is G3's 0.1724. After the registration b_test does not change". l.628-629: "SR_d >= 0.2007 ... Binding selection threshold: 0.2007." G4 l.662: "b_test from P7.2 at the registered N." | Both branches and the before-C1 cut-off are stated. Missing: where the user's decision is recorded (nothing hashed carries it; the protocol text itself still reads 0.1649) and the reviewer's G4 anchor. Add to l.640 after "C1 registration": "(recorded as an amendment under 0.2: a new protocol version hashed before C1, whose P7.2 states b_test = 0.1017, G4 = 0.1373 and the binding threshold 0.1724)". Replace G4 l.662 "b_test from P7.2 at the registered N" with "b_test = the value P7.2 pins in the protocol version whose sha256 E.33 verified at A1, recomputed by p7_final.py only if N differs from 838". |
| DO-3 | CORRECT | 610-616 | "E33-<set><label><grid>, set S1..S5; label F05, F15, F30, F60, T15, T30; grid, in the P7.1 order: L001A ... G3200 ... Example: E33-S5F15L010A. E.33 registers all 300 in one screening.trial_registry.register call (test "E33", ...)" | id_check.py: 300 generated, 300 unique, all fullmatch `_ID`, all start with "E33-", longest suffix 10 chars; "E33" fullmatches `_TEST`; register() l.213-216 accepts them (not called). Old v0.2 forms fail as the reviewer found. "50h" is P5 l.501's own notation (min_data_in_leaf in {50 h, 200 h}). |
| DO-4 | CORRECT | 616-618, 641-642, 657-658 | P7.1: "The N of every DSR, threshold and test in P7.2, P8 and P9 is trial_registry.current_n() immediately after that registration: 838 if no other stage registers first". G3: "N = the registered N after E.33's registration". P7.2: "If the registered N differs from 838, p7_final.py recomputes every threshold at that N before any real-outcome fit." | No "at E.33's start" text remains (grep). current_n() today is 538 (read-only), so 838 after a 300-ID registration. |
| DO-5 | PARTIAL | 674-679 | "continue the Tier A walk over all 300 configurations ordered by the same key, gates ignored, taking the next two whose OOF daily series has correlation <= 0.70 with every configuration already taken (Tier A and Tier B)." | The reviewer's route is adopted. Missing: the "fewer than two qualify" fallback, and the walk "over all 300" includes failed configurations (P5: no OOF series) and zero-trade configurations (constant series, Pearson undefined), for which "correlation <= 0.70" is two-valued (numpy: NaN compares False; a careful reader may take "not above 0.70"). Append to l.677: "A configuration with no OOF series (failed, P5) or a constant OOF series (no trade) is skipped. If fewer than two qualify, Tier B is filled by the highest-ranked remaining configurations with a defined series and E.33 reports their correlations." Also l.678-679's "93% of the time" is the rho 0.98 cell of the reviewer's table (0.429 at 0.70, 0.805 at 0.90): write "at rho 0.98". |
| DO-6 | CORRECT | 64-71, 555-557 | P6.2: "mean, population SD, daily Sharpe SR_d = mean / population SD, skewness, raw kurtosis and t, exactly as screening/stage_e_verdict.py moments() and t_stat() compute them". 0.3 l.70-71: "Statistics of daily series (mean, SD, Sharpe, skewness, raw kurtosis, t) are those of ... moments() and t_stat() (population SD; Sharpe = mean / pstdev)." | moments() l.183 uses statistics.pstdev (confirmed). G5(c)'s "mean/SD x sqrt(n)" (l.665) is covered by 0.3's daily-series convention. Residual wording: G3 l.659 says "the configuration's own sample skewness" (R-W2-3, NOTE). |
| DO-7 | CORRECT | 669-671 | "(a total order; ProtocolReview DO-7): SR_d rounded to 4 decimals, descending; then fewer trades per date; then LOGIT before LGBM; then the lower set index; then the shorter horizon (FH before TB at equal h); then the earlier grid point in the P7.1 order." | The last key (set, label, grid) is unique per configuration, so the order is total. The reviewer's "(round half to even)" was dropped; the rounding function is unstated (R-W2-4, NOTE). |
| DO-8 | CORRECT | 300-309 | "skip lines that start with "#"; columns date, time_et, report, source_url, evidence; skip rows whose date is not a valid YYYY-MM-DD ...; keep rows with time_et "12:00" and report exactly one of "USDA WASDE", ..., "NOPA Monthly Crush (not USDA)" ...; A calendar month with no valid NOPA row (2022-11 and 2022-12 among them) gets its rule date" | cal_check.py on the two files (hashes match l.302-304): headers as stated; the seven report strings and "12:00" match exactly; ext has 1 comment line and 3 invalid-date rows, main 0 and 4; valid date ranges 2020-12-01..2022-10-31 and 2022-11-01..2024-02-29 as l.304-305 says; 37 months have one valid NOPA row, 2022-11 and 2022-12 none, none has two: 39 NOPA dates. "asserts the counts per report type" replaces the reviewer's date list; equivalent as a pre-fit check. |
| DO-9 | CORRECT | 64-66, 271-273, 311-312 | 0.3: ""Book update": the book state after a record that carries F_LAST ... First-touch tests (P3.4), locked-book checks (P3.6 rule 5) and OFI sums (F2.8, F3.1, F3.4) step through book updates; "as of u" means the last book update with ts_recv <= u". P3.4: "ignores updates at which M_ZM is undefined (an empty side or a bad book never triggers a barrier". | The lead took the F_LAST route for every use, including "as of u" (more conservative than the reviewer's per-record as-of; consistent with P3.2 fills and P3.6). Rule 5 still excludes the span (l.311-312) as the reviewer asked. Not verified (context budget): whether F2.9-F2.11 and F3.2-F3.3 are defined "as F2.8"/"as F3.1" so that the 0.3 list covers them. Residual: the ts_recv of a book update (its F_LAST record's) is unstated (R-W2-6, NOTE). |
| DO-10 | CORRECT | 329-334 | "That runner's 2-minute minimum hold and 10-minute mean-holding floor are bar-runner rules and are not adopted ... When flat at t in G_h(D), the entry rules of P3.6 hold at t, and fewer than 20 entries have been made on D, apply P3.5." | stage_e_runner.py l.37-38 and LABEL_MIN_HOLD l.138 confirm the rule exists; v0.3 declines it explicitly and adopts only the entry cap. Equivalent to the reviewer's text. |
| DO-11 | CORRECT | 353-355 | "clipped to [-5, 5] after their own normalisation (38): C.5, F1.1-F1.4, F1.6-F1.8, F2.1-F2.11, F3.1-F3.4, F3.10-F3.12, F4.1-F4.5, F4.7-F4.13. Not clipped (21): C.1-C.4, C.6-C.15, F1.5, F3.5-F3.9, F4.6" | Feature tables (l.372-435) define C.1-C.15, F1.1-F1.8, F2.1-F2.11, F3.1-F3.12, F4.1-F4.13 = 59. Clipped 1+4+3+11+4+3+5+7 = 38; not clipped 4+10+1+5+1 = 21; 38+21 = 59, each ID in exactly one list. Matches the reviewer's list. |

## Hunk map (v0.2 -> v0.3) for P2 (v0.3 162-237) and P3 (238-339)

P2 has no hunk (no diff header lands in 162-237; the nearest are 95-110 and 249-254). P3 hunks:

| v0.2 lines -> v0.3 lines | Item ID(s) | Check |
|---|---|---|
| 233,234c249,254 | LE-1 (P3.2 fallback fills and limit marks) | Other lens; read for consistency with rule 5 l.311-316: the limit side convention is defined there. Not re-checked. |
| 251c271,273 | DO-9, LE-6 | Checked under DO-9: CORRECT. |
| 266,268c288,293 | LE-1 (row rule vs entry rule split) | Other lens; consistent with l.331-334 "the entry rules of P3.6 hold at t". Not re-checked. |
| 275,278c300,309 | LE-3, DO-8 | Checked under DO-8: CORRECT (cal_check.py). |
| 280,284c311,316 | LE-6, LE-2, FE-8 | Other lens; the rule-5 row part is DO-9's "still triggers rule 5" and is present. Not re-checked beyond that. |
| 290,293c322,327 | DO-15 | Other lens. Not re-checked. |
| 297,301c331,336 | DO-10, LE-1 | Checked under DO-10: CORRECT. |

Hunks mapped: 7. Unmapped (HUNK-): 0.

## Cross-checks

(a) Registry IDs. `_ID = [A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16}` (trial_registry.py l.49), applied with fullmatch
and `startswith("E33-")` in register() l.213-216; `_TEST` accepts "E33". id_check.py: the stated mapping
E33-<S1..S5><F05|F15|F30|F60|T15|T30><L001A|L001E|L010A|L010E|L100A|L100E|G2050|G2200|G3050|G3200> generates
exactly 5 x 6 x 10 = 300 distinct IDs, every one fullmatches, the longest suffix is 10 characters (limit 16), and the
examples in the protocol (E33-S5F15L010A l.614; E33-S5F15L100E and E33-S5F15G3050 l.534) are members. PASS.

(b) Tier B. Mentions: P6.4 l.567 and P6.5 l.587 ("Tier A and Tier B only; they select nothing"); P8 l.674-679 (the
walk, gates ignored, next two at corr <= 0.70 against everything taken); P9 l.703-706 ("computes the Tier A and Tier B
daily series ... population variance of the Tier A Sharpes if two or more, else of Tier A and Tier B, V14 c");
P7.2 l.644 ("the population variance of the 2-3 tested Sharpes"); P10 l.731 ("Tier B's variants" in the cut order).
All agree with each other and with stage_e_verdict.py (l.26: PBO over Tier A if two or more else every run series;
l.219: pvariance of the Sharpes) and with the lead's summary. Residual: P8's "when Tier A has one member" (l.674-675)
can be read as a condition on running Tier B at all; P9 settles it (always run). That is DO-35 (other lens). PASS.

(c) DO-1. Written and hashed before C1 for every reading: yes (l.35-36, "before the C1 registration", no outcome
condition). Who writes: "decided by E.33" (l.34), no role named. Where the hash goes: "the pipeline freeze", which
the E.33 prompt (B7, l.132-134) defines as the sha256 list of every code file, config and environment lock, and
which C1 (l.142-146) writes into the registry as the pipeline sha256. So the hash reaches the registration only
indirectly, and the readings file itself is unnamed. PARTIAL: see DO-1 and R-W2-2.

(d) DO-2. Both branches stated: keep -> G4 binds at SR_d >= 0.2007 (l.628-629, b_test 0.1649 l.626, 639); drop ->
b_test 0.1017 and G3's 0.1724 binds (l.640). Decision before C1: l.639-640. PASS on content; the record of the
decision has no named location and the drop branch's G4 value (0.1373) is not stated (DO-2, R-W2-2).

## New findings

| ID | Severity | Lines | Finding | Proposed fix |
|---|---|---|---|---|
| R-W2-1 | SHOULD FIX | 675-677 | The Tier B walk runs "over all 300 configurations" and takes "the next two whose OOF daily series has correlation <= 0.70": failed configurations (P5 l.511-513, no OOF series) and zero-trade configurations (constant series, Pearson undefined) make the test two-valued, and nothing says what happens if fewer than two qualify. Tier B's composition sets the program verdict's DSR variance and PBO when Tier A has one member. | Append to l.677: "A configuration with no OOF series (failed, P5) or a constant OOF series is skipped. If fewer than two qualify, Tier B is filled by the highest-ranked remaining configurations with a defined series and E.33 reports their correlations." |
| R-W2-2 | SHOULD FIX | 34-38, 639-641 | Neither the conservative-readings file nor the record of the user's keep-or-drop decision on the added test DSR is named; both are "recorded" somewhere before C1, and nothing hashed before C1 is required to carry them. An E.33 lead can satisfy the text with a STATE line written after the funnel exists. | DO-1's and DO-2's proposed text above: name reports/stage_e33_protocol_readings.md, put its sha256 in the B7 list and the C1 note; make the drop decision an amendment under 0.2 (a new protocol version hashed before C1). |
| R-W2-3 | NOTE | 659 | G3 says "the configuration's own sample skewness and raw kurtosis" while P6.2 and 0.3 fix the population convention; "sample" can be read as the ddof-1 convention. | "the configuration's own skewness and raw kurtosis (P6.2)". |
| R-W2-4 | NOTE | 669 | "SR_d rounded to 4 decimals" names no rounding function; Python round() and numpy.round can differ on the 5th-decimal edge. The reviewer's "(round half to even)" was dropped. | "SR_d rounded to 4 decimals with Python's round() (half to even)". |
| R-W2-5 | NOTE | 678-679 | "a true daily Sharpe of 0.12 would pass the program's DSR 93% of the time" is the rho 0.98 cell of DO-5's simulation (0.429 at rho 0.70, 0.805 at 0.90); unqualified it overstates the general case. | "...93% of the time at rho 0.98 between the series (43% at rho 0.70)". |
| R-W2-6 | NOTE | 64-66 | A book update's time is unstated: records of one event batch can carry different ts_recv values, and "the last book update with ts_recv <= u" needs one. | Add: "A book update's time is the ts_recv of its F_LAST record." |
| R-W2-7 | NOTE | 36 | "none may be made after the first real-outcome fit" is looser than the same sentence's "before the C1 registration" (C1 precedes every fit); a reader may take the fit as the deadline. | "none may be made after C1". |

## Not finished or not verified
- DO-9: whether F2.9-F2.11 and F3.2-F3.3 are defined by reference to F2.8/F3.1 (so that 0.3's list "F2.8, F3.1,
  F3.4" covers every sum over updates) was not read (context budget). If any is a sum over updates defined on its
  own, add it to the 0.3 list.
- The other-lens hunks in P3 (LE-1, LE-2, LE-6, FE-8, DO-15) were mapped, not re-checked.
- Finished 09:0x PDT (see file mtime).
