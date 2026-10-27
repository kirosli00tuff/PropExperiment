# SpotCheck A: FixSpotCheckA-FableXHigh, v0.3 -> v0.4 diff hunks in sections 0, P1, P2, P3

Label: FixSpotCheckA-FableXHigh (independent adversarial checker; did not write the protocol or its edits).
Object: reports/stage_e32_discovery_protocol.md DRAFT v0.4, sha256
87d8203a3a3279368e8218ccaab27a701e632d1b6d8a4ba333831fd828716cd3 (read and hashed 2026-10-27; `wc -l` gives
822 lines, 761 non-blank; the brief's and STATE's "817 lines" does not recompute, the sha256 does).
Sections checked: v0.4 lines 1-358 (section 0, P1, P2, P3; "## P4. Features" is line 359). v0.3 lines 1-339.
Diff: 37 hunks in all; 12 fall in these sections (saved as work_spot_A/diff_v03_v04.txt). No hunk touches P2
(v0.4 172-247) and no finding has lines there.
Inputs read by section: the diff; Recheck_W1..W4 per-item tables, new-findings tables and "not finished" lists;
STATE lines 483-499 (the 12:38-12:41 rulings); docs/prompts/STAGE_E.33.md lines 10-30, 40-58, 90-94, 126-150;
protocol lines 1-10, 26-45, 60-76, 95-146, 248-358, 425, 433-434, 474, 481, 628-634, 660-670, 696-697, 770-772;
code by grep (reports/stage_e31_briefs/work/pilot/{mbo_book31,measure31_core,kalgo31}.py); directory names only
under reports/stage_e31_briefs/work/pilot/runs/ and reports/stage_e32_briefs/work/X1_exposure/. No market data,
no data/, no parquet, no registry or ledger call. Scripts: work_spot_A/cal_count.py (release-calendar recount).

## 1. Per-hunk table

| # | v0.4 lines | Finding IDs | Verdict | Evidence (quote, recomputation, grep) | Proposed fix |
|---|---|---|---|---|---|
| H1 | 3 | none (status line) | UNTAGGED-OK | "Status: DRAFT v0.4 (2026-10-27, lead Opus 5.5 xhigh; ProtocolReviewer findings and the FixVerifier re-check applied). Not frozen." Version label and provenance only. | none |
| H2 | 35-41 | DO-1 (PARTIAL), R-W2-2 (SHOULD FIX, 34-38 half), R-W2-7 (NOTE) | CORRECT | Text is W2's DO-1 proposal verbatim plus R-W2-7's "No reading is made after C1". Checked: "second bullet" of 0.2 is the stop-that-part-and-report bullet (lines 29-32), so the cross-reference is right; "B7 pipeline freeze list" exists in the prompt (STAGE_E.33.md 132-134: "a sha256 list of every code file, config and environment lock"); C1 (prompt 142-148) precedes every real-outcome fit, so "before C1" is at least as strict as v0.3's "before the first real-outcome fit"; the prompt's own conservative-reading rule (lines 55-56, 92-93) is looser but the protocol binds first (prompt 17-20) and 0.1 "This document". No outcome can steer a reading made before C1. | Two NOTEs, S-A-3 and S-A-4: "C1 registration note" is defined nowhere (not in the prompt's C1, not in P7.1, which names only the freeze file and reports/stage_e33_run_marker.md); and a reading made between the B7 freeze and C1 cannot be "a line of the B7 pipeline freeze list" without a re-freeze (0.2 bullet 1 allows it, the text does not say so). |
| H3 | 68-71 | R-W2-6 (NOTE); W2's unfinished DO-9 coverage, lead ruling "0.3 OFI list F2.8-F2.11, F3.1-F3.4" | CORRECT | "OFI sums (F2.8-F2.11, F3.1-F3.4) step through book updates ... A book update's time is the ts_recv of its F_LAST record (FixVerifier R-W2-6)." Grep of P4: F2.8-F2.9 (line 425) "summed over the MBP-1 updates in the window", F2.10-F2.11 (426) "the same for ZL", F3.1-F3.3 (433) "as F2.8 on the ZM top of book from MBO", F3.4 (434) "the e_n of F2.8 on level-m prices" over the window: exactly the sums over updates, no other P4 feature is a sum over updates (CR5, SW5, RF15 count records or events, not book states). mbo_book31.py 39: `F_LAST, F_TOB, F_SNAPSHOT, F_MBP = 1 << 7, ...` exists. Every other "book update" use (260, 280, 285, 328) is unchanged and consistent. | NOTE S-A-5 (wording): the quoted term is split across lines 69-70 as `"as of` / `u"`, which defeats a grep for the term. Join the lines. |
| H4 | 101-104 | R-W4-6 (NOTE); FE-5 residual | CORRECT | Text is W4's R-W4-6 proposal with "except the files named in the third bullet" added. "Where the E.33 prompt's reading list and this section differ, this section applies" agrees with the prompt's binding order (STAGE_E.33.md 17-20: "Binding, in this order: the frozen protocol ..., this prompt"). "Third bullet" is the "Not opened by E.33's workers" bullet (116-120). The glob reports/stage_e32_*.md matches STATE.md and test_seal.md, which mention Table C by name only (grep: 2 and 1 lines, no figures). | NOTE S-A-6: read literally, "readable, except the files named in the third bullet" closes E.31_RETURN.md whole (it is named there) and closes the X1 files to the lead too, while the bullet says "read by grep" and "The E.33 lead may read them". Replace with "readable, except, for E.33's workers, the section and the three files named in the third bullet". See also S-A-1 (the firewall's coverage). |
| H5 | 108-109 | FE-6 (PARTIAL, (iii), lines 100-101 half); lead ruling "FE-6 (iii): a port of measure31_core's fill logic written by E.33" | CORRECT | Text is W4's FE-6 replacement for l.100-101 verbatim. Code refs exist: measure31_core.py `class VOrder` (161), `class Placement` (236), `class InstrumentRun` (248) with `def fill(self, v: VOrder, t: int, trigger: str, mid0: float)` (307) and `def _k_allocation` (402); kalgo31.py (`allocate`, `allocate_steps`, `KParams`). Data facts: "### 6.1 Reusable as is" (456), "### 6.2 Not reusable for this purpose" (479), so "F 6.1-6.2" is the right citation. Consistent with the P6.4 (iii) hunk (v0.4 629-633: "a port of E.31's queue state machine, measure31_core's VOrder, Placement and fill logic ... written and tested by E.33; reported as not done if it is not ready by the P10 cut"). | none |
| H6 | 114-115 | R-W1-8 (i) (NOTE); lead ruling "runs/measure31/ named inside the refused runs/ folder" | CORRECT | Directory names (no file opened): reports/stage_e31_briefs/work/pilot/runs/measure31/ exists with per-date folders (2020-12-01, ...) holding parquet files, matching README_measure31's `<out>/<date>/...` layout W1 cited; `find reports -name stats31.md -o -name stats31.json` returns exactly runs/stats31.md and runs/stats31.json, both inside the refused folder. "every stats31.md and stats31.json" is therefore true and the guard has a path to test. | none |
| H7 | 117-120 | R-W1-8 (ii) (NOTE); lead ruling "X1_exposure.md, X1_verify.md and the Table C appendix closed to E.33 workers as whole files (E.31_RETURN 3.5 by grep)" | CORRECT as to the ruling; see S-A-1 | All three paths exist (44,137, 38,392 and 118,137 bytes). E.31_RETURN.md has "### 3.5 Part 5: the measurement" at line 175, running to line 213 (next heading "## 4." at 214). The lead's option (whole files) is the one R-W1-8 (ii) asked to be chosen. LT6 (B's section, v0.4 474) now says "P1.2's Refused list" (R-W1-8 iii). | SHOULD FIX S-A-1: the closure names three files "because they reproduce E.31's discovery-date statistics", but sibling files in the same readable folder reproduce the same tables (work/X1_exposure/X1_part2.md is headed "Table B. Overlap with the 538 trials", 56 table rows; X1_part3b.md 37 rows and X1_part3c_raw.md 10 rows carry the same markout figures as the appendix, grep count 2 lines each), and "the E.32 briefs are readable" admits them. NOTE S-A-7: "read by grep, never that section" does not say what a grep hit inside 3.5 means; give the line bounds. |
| H8 | 263-268 | R-W1-7 (NOTE), R-W1-2 (SHOULD FIX); LE-1 residual | CORRECT | Both sentences are W1's texts verbatim. Consistency checked: P3.4 (279) still defines m0 = M_ZM(t + L) for rows; for a kept row rule 5 (row rule, 328-329) excludes any span with a one-sided or bad book update, and P3.7 requires a valid M_ZM(t), so M_ZM(t + L) is defined for every row and the override is needed only for trades, where P3.2 now states it. "Equal to M_ZM(t + L) when no fallback fired" holds because the no-fallback fill is "as of u + L" = the last book update with ts_recv <= t + L (0.3). No barrier can fire between t + L and a fallback fill update (every update there has an empty side or a bad book, which P3.4 285-286 says never triggers a barrier), so the trade's barrier window is well defined without more text. LT7 (B's section, 481) names "the fallback fill update of P3.2", the same event. "touch" is P3.2's own term (257). | NOTE S-A-8: "before it emptied" covers the empty-side case but not the marked-bad case that also triggers the fallback (259); write "before it emptied or the book was marked bad". |
| H9 | 296-297 | R-W1-6 (NOTE); LE-1 residual | CORRECT | "the entry rules of P3.6 hold at t (P3.6, first paragraph; FixVerifier R-W1-6)". P3.6's first paragraph (303-307) states the entry rule ("a trade may be entered at t only if the possible span [t, t + L + h min] meets them and the ZM book at t has both sides and is not marked bad") and excludes the locked-book part. P3.8 (352) uses the same phrase. | none |
| H10 | 321-325 | LE-3 (PARTIAL), R-W1-5 (SHOULD FIX) | CORRECT | Recomputed with work_spot_A/cal_count.py on the two calendar files (sha256 0743c0e2... and 55df3b14..., both match lines 314-316; files are under reports/, not market data): after the parse rule exactly as written (skip "#" lines, valid YYYY-MM-DD, time_et "12:00", the seven report strings) the counts are USDA WASDE 39, NASS Crop Production 39, NASS Crop Production Annual 4, NASS Grain Stocks 13, NASS Prospective Plantings 3, NASS Acreage 3, NOPA 37; 1 comment line, 7 invalid-date rows; valid dates 2020-12-01..2022-10-31 (ext) and 2022-11-01..2024-02-29 (main); the window has 39 calendar months; the months with no valid NOPA row are exactly 2022-11 and 2022-12, none has two; 37 + 2 rule dates = 39. Every number in the hunk recomputes. The P9 half of LE-3 is in B's section (v0.4 770-772, "43 each"). W1's dropped parenthetical "(39 release dates per monthly report over the 39 months)" is redundant with the counts. | none |
| H11 | 332-334 | R-W4-8 (NOTE), R-W1-11 (NOTE); FE-8 and LE-2 residuals | CORRECT | Text is W4's R-W4-8 sentence verbatim. mbo_book31.py 41: `UNDEF_PRICE = int(np.iinfo(np.int64).max)` = 9223372036854775807 = 2^63 - 1 (recomputed). R-W1-11's first clause ("the latest earlier record in the Z4 files is used") is already the rule: "the front's last definition record with ts_recv <= 08:30:00 CT on D" is a bound on time, not on date, so any earlier record qualifies; only the no-record-at-all case remained and the skip covers it. Both findings are therefore resolved by one sentence, and the two re-checkers agreed the case has no consequence for outcomes (LE-2 row). | NOTE S-A-9: "a per-date as-of pass over the Z4 files" (331) with 39 monthly files (P1.1, 92) can be implemented per file; say the as-of state carries across files. |
| H12 | 343-344 | DO-15 (PARTIAL) | CORRECT | Text is W3's DO-15 replacement verbatim: "u_i = the mean of 1/c_m over the intervals m that span_i intersects by more than one second (the same intervals that count span_i in c_m)". One criterion now defines both c_m and u_i. The FH parenthetical "(so an FH span of h minutes plus L covers h intervals)" holds at L = 1.000 s (line 77): the (h + 1)th interval is intersected by exactly 1.000 s, which "more than one second" excludes (W3's recomputation, re-done). | none |

Verdicts: 11 CORRECT, 1 UNTAGGED-OK, 0 PARTIAL, 0 WRONG, 0 UNTAGGED-ERROR.

## 2. Coverage: every re-check finding with lines in v0.3 1-339

| Finding | Kind | v0.3 lines (mine) | Where addressed in v0.4 | Status |
|---|---|---|---|---|
| LE-1 | PARTIAL | 249-254, 271-273, 282, 288-293, 311, 333-335 | H8 (R-W1-2, R-W1-7), H9 (R-W1-6) | addressed |
| LE-2 | CORRECT | 311-316 | no change needed; residual R-W1-11 in H11 | addressed |
| LE-3 | PARTIAL | 300-309 (+ 701-702, B's) | H10; P9 half at v0.4 770-772 (B's) | addressed |
| LE-6 | CORRECT | 249-254, 271-273, 311-312 | no change needed | n/a |
| LE-7 | CORRECT | 95-110, 159 (+ 456, B's) | residual R-W1-8 in H6, H7; LT6 at v0.4 474 (B's) | addressed |
| AR-2 | PARTIAL | 64-71 (convention part CORRECT) | missing part is at 639 (P7, B's); 0.3 unchanged, correctly | B's |
| R-W1-2 | SHOULD FIX | 249-254 | H8 | addressed |
| R-W1-5 | SHOULD FIX | 307-308 (+ 702, B's) | H10; 770-772 (B's) | addressed |
| R-W1-6 | NOTE | 282 | H9 | addressed |
| R-W1-7 | NOTE | 252-254 | H8 | addressed |
| R-W1-8 | NOTE | 105-106, 108-109 (+ 456, B's) | (i) H6, (ii) H7, (iii) v0.4 474 (B's) | addressed; see S-A-1 |
| R-W1-11 | NOTE | 314-316 | H11 (subsumed by R-W4-8's sentence) | addressed |
| DO-1 | PARTIAL | 34-38 | H2 | addressed |
| DO-6 | CORRECT | 64-71 | no change needed | n/a |
| DO-8 | CORRECT | 300-309 | no change needed (H10 adds the counts) | n/a |
| DO-9 | CORRECT (coverage unfinished) | 64-66, 271-273, 311-312 | H3 (OFI list F2.8-F2.11, F3.1-F3.4; lead ruling) | addressed |
| DO-10 | CORRECT | 329-334 | no change needed | n/a |
| DO-12 | CORRECT | 67-71 | no change needed | n/a |
| R-W2-2 | SHOULD FIX | 34-38 (+ 639-641, B's) | H2; amendment-under-0.2 text at v0.4 696-697 (B's) | addressed |
| R-W2-6 | NOTE | 64-66 | H3 | addressed |
| R-W2-7 | NOTE | 36 | H2 ("No reading is made after C1") | addressed |
| DO-15 | PARTIAL | 322-325 | H12 | addressed |
| FE-5 | CORRECT | 95-111 | residual R-W4-6 in H4 | addressed |
| FE-6 | PARTIAL | 100-101 (+ 581-582, B's) | H5; P6.4 (iii) at v0.4 629-633 (B's) | addressed |
| FE-8 | CORRECT | 312-316 | residual R-W4-8 in H11 | addressed |
| FE-9, FE-10 | CORRECT | 67-69 | no change needed | n/a |
| R-W4-6 | NOTE | 96 | H4 | addressed |
| R-W4-8 | NOTE | 315-316 | H11 | addressed |

No finding with lines in these sections is unaddressed. R-W3-13 (v0.3 393, F1.3) is P4 and belongs to checker B.

## 3. Protocol-wide consistency of the terms and numbers the hunks changed (grep of v0.4)

- F_LAST / "book update": lines 67-71 define; 260, 280, 285, 328 use; P4 OFI rows 425-426, 433-434 are the listed
  sums. Consistent.
- reports/stage_e33_protocol_readings.md: line 36 only; the prompt has no such file and no "registration note"
  (prompt C1 writes the registry lines and reports/stage_e33_run_marker.md). See S-A-3.
- "this section applies" (103) against the prompt's binding order (17-20): consistent. The prompt's "Read first"
  list (22-30) includes E.31_RETURN.md and E.31's pilot code; the protocol's narrower worker rule prevails.
- measure31_core / kalgo31: 107-108 and 629-633 say the same thing (port by E.33; fill logic as reference).
- runs/measure31/, stats31.md/json: 114-115 only; paths exist (names).
- X1_exposure.md, X1_verify.md, X1_tableC_appendix.md: 118-119 (closed to workers); 142 cites X1_verify.md as the
  source of P1.5's verification counts (a citation, not a read instruction). Sibling files: S-A-1.
- "entries not made": 266-267; "fallback fill update": 265 and LT7 481. Consistent.
- "entry rules of P3.6": 296 and 352, both pointing at the first paragraph of P3.6 (303-307). Consistent.
- UNDEF_PRICE: 333 only, value recomputed. Z4 files: 92 (39 monthly files) and 331. See S-A-9.
- "intersects ... by more than one second": c_m (341-342) and u_i (343-344) now share it; L = 1.000 s (77).
- Calendar counts 39/39/4/13/3/3/37 + 2, months 2022-11 and 2022-12: 321-325 only; recomputed; the P9 figure "43
  each" (772) is the test window's month count, a different window (B's section).
- "817 lines" (STATE 483, the brief): the file has 822 lines (761 non-blank); the sha256 matches. S-A-2.

## 4. Problems

| ID | Severity | v0.4 lines | Problem | Proposed fix |
|---|---|---|---|---|
| S-A-1 | SHOULD FIX | 101-104, 116-120 | The worker firewall (third bullet) closes three X1 files "because they reproduce E.31's discovery-date statistics", but the readable set ("the E.32 briefs") admits the other files of reports/stage_e32_briefs/work/X1_exposure/ (X1_part1.md, X1_part2.md headed "Table B. Overlap with the 538 trials", X1_part3.md, X1_part3b.md, X1_part3c_raw.md, X1_part3d.md, X1_part3e.md, X1_frag_gate0.md, X1_ledger_summary.txt), which hold the same tables and markout figures (grep: X1_part3b.md and X1_part3c_raw.md each carry 2 lines with the figures the appendix carries 8 of). The rule's stated purpose is not met by its list. No verdict number changes (every choice is frozen, P8 is mechanical), so not BLOCKING. The reader files M2, M3, M6, R3b, R4 and this protocol's own P1.3 and P1.5 also quote a few E.31 aggregates; the lead decides whether those aggregates are the concern (then the bullet should say they are not) or not. | Replace lines 117-119's file list with: "reports/E.31_RETURN.md section 3.5 (lines 175-213; the rest of the file by grep), and the whole files reports/stage_e32_briefs/X1_exposure.md and reports/stage_e32_briefs/X1_verify.md and every file under reports/stage_e32_briefs/work/X1_exposure/ (the Table C appendix and the X1_part* extraction files). The aggregate E.31 figures quoted in this protocol (P1.3, P1.5) and in the reader files M2, M3, M6, R3b and R4 are not closed: they are the figures the declared choices cite." |
| S-A-2 | NOTE | STATE 483; the brief | "817 lines" does not recompute: v0.4 has 822 lines (wc -l; 761 non-blank). The sha256 is right, so it is the same file. | Write "822 lines" in the STATE entry and wherever the count is repeated (the freeze note, the return). |
| S-A-3 | NOTE | 37-38 | "quoted in the C1 registration note": no such artifact is defined in the protocol or the prompt. The prompt's C1 writes ledger lines and reports/stage_e33_run_marker.md; P7.1 (665-668) names the freeze file. An implementer can put the hash in either, in STATE, or nowhere. Where a hash is quoted affects no outcome. | Replace "is quoted in the C1 registration note" with "is quoted in reports/stage_e33_run_marker.md (the prompt's C1) and carried in the freeze file of P7.1". |
| S-A-4 | NOTE | 35-38 | The readings file is hashed into the B7 freeze list, yet readings may be made up to C1 (after B7). A reading made between the freeze and C1 changes the file's sha256, so the freeze list must be re-taken (0.2, first bullet allows it before the first real outcome) but the text does not say so. | After "before the C1 registration" add "(and before the B7 freeze; a reading added between the freeze and C1 re-takes the freeze list, 0.2 first bullet)". |
| S-A-5 | NOTE | 69-70 | The defined term is split across lines: `"as of` / `u"`. A grep for the term in the frozen file fails. | Join the two lines so the sentence reads `... step through book updates; "as of u" means ...`. |
| S-A-6 | NOTE | 101-103 | "readable, except the files named in the third bullet" read literally closes E.31_RETURN.md whole (it is named there, but the bullet closes only section 3.5) and closes the files to the lead, while the bullet says "The E.33 lead may read them". | "readable, except, for E.33's workers, the section and the files named in the third bullet". |
| S-A-7 | NOTE | 117 | "(read by grep, never that section)" does not say what a worker does when a grep hit lands inside section 3.5, and gives no bounds. | "(lines 175-213 are never read, by grep or otherwise; a grep hit inside them is discarded; the rest of the file is read by grep)". |
| S-A-8 | NOTE | 263-264 | "the last valid touch on that side before it emptied": the fallback (259) also fires when the book is marked bad with the side present, where "emptied" does not describe the event. | "the last valid touch on that side before it emptied or the book was marked bad". |
| S-A-9 | NOTE | 331 | "a per-date as-of pass over the Z4 files" with 39 monthly files can be read as a pass that restarts per file or per date; the definition "last definition record with ts_recv <= 08:30:00 CT on D" needs the as-of state carried across files. Outcome-neutral unless a date's front has no definition record in its own file before 08:30 CT, which the skip clause then handles differently from the carried state. | "(a single as-of pass over the Z4 files in ts_recv order, state carried across files and dates; ...)". |

Severity counts: BLOCKING 0, SHOULD FIX 1, NOTE 8.

## 5. Not finished or not verified

- Hunks outside lines 1-358 (P4 to P10) were not checked; they belong to checker B. I read lines 474, 481,
  629-633, 660-670, 696-697 and 770-772 only to confirm cross-section consistency and coverage.
- The X1_part* files were identified by their first heading and table-row counts and by grep counts of three
  figures; their contents were not read.
- README_measure31.md's output layout was taken from W1's citation; the per-date parquet folder names under
  runs/measure31/ were listed, no file opened.
- The release-calendar recount is my own (cal_count.py); it agrees with W1's and W2's independent counts.
