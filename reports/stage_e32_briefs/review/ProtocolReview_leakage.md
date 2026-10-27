# ProtocolReview, lens: leakage and look-ahead (Stage E.32, reports/stage_e32_discovery_protocol.md DRAFT v0.2)

Reviewer: LeakageReviewer-FableXHigh (claude-fable-5-1), 2026-10-27. Independent adversarial review; I did not
write the protocol. Object: reports/stage_e32_discovery_protocol.md, 647 lines (DRAFT v0.2). Inputs read by
section: docs/prompts/STAGE_E.32.md 196-274, docs/prompts/STAGE_E.33.md 40-135, docs/DECISIONS.md V14/V43/V50/V51,
screening/stage_e_verdict.py (docstring, moments, dsr, dsr_table, pbo, edge_chain), funnel/multiple_comparisons.py
(expected_max_sharpe, deflated_sharpe_ratio), reports/stage_e32_data_facts.md 1.4, 1.5, 2, 4.3, 6.1, 6.3, M1 2.5
and 9, M2 bottom line, M3 b.5/d.2/d.5/e.7/f.5/g.3, M4 a (inner folds), M5a a.1-a.2/c.5, M5b b.2/b.5, R2/R4 grep,
X1_exposure 220-278, the four MathReview files (C-3, C-15, A-2, A-3, D-11), E.31's measure31.py (day_bounds,
instrument_on, roll_reasons, calendar_reason) and mbo_book31.py (Book), the two release calendars (schema and
anomalous rows only), reports/stage_e32_test_seal.md 4, the saved Databento GLBX.MDP3 page, and the program
calendars through code. No market data was opened. No web access was used (work folder log.tsv). Scripts and
their outputs: reports/stage_e32_briefs/review/work_protocol_leakage/ (calendar_counts.py, test_window_counts.py,
test_window_counts2.py, csv_check.py).

Severity key (from the brief): BLOCKING = would leak, would let an outcome steer a choice, would make a number
entering a verdict wrong, or cannot be run as written; SHOULD FIX = an ambiguity a careful implementer could read
two ways with different outcomes, a missing rule, an unstated assumption, a wrong number not changing a verdict;
NOTE = clarity.

## Findings table

| ID | Severity | Section (line) | Finding in one line |
|---|---|---|---|
| LE-1 | BLOCKING | P3.2 (235-236), P3.5 (260), P3.6 rule 5 (279-283), P3.8 | The trade simulator's entry decision at t conditions on the whole future span [t, t+L+h] having a two-sided book; a look-ahead inside the code that produces X_D, the verdict series |
| LE-2 | SHOULD FIX | P3.6 rule 5 (281-283) | Limit prices "in the definitions in force on D" are not point-in-time; use the latest definition record with ts_recv <= t |
| LE-3 | SHOULD FIX | P3.6 rule 3 (263-271), P9 calendar (601-602) | The calendar rule as written cannot be applied to the files as they are: report strings differ, two NOPA rows have a non-date and a blank time (two readings give two exclusion sets), the ext file opens with a comment line, and the coverage statement names the wrong file |
| LE-4 | SHOULD FIX | P6.1 (466-469), LT3 (408-410) | "20 = the longest feature look-back in trade dates" is off by one: F1.7/F4.7's sd_g/sd_gap reach the 13:15 mid of the 21st prior date, so the first post-embargo training date reads one price from the evaluation block's last date |
| LE-5 | SHOULD FIX | P4.1 LT1 (403-405), LT1-LT6 as a set | LT1 names "record streams" without the definitions stream and the calendars, and no test checks that the simulator's entry decision is causal (the gap LE-1 falls through) |
| LE-6 | SHOULD FIX | P3.6 rule 5 (279-281), 0.3 Book (37-40), P3.3/P3.4 | Rule 5 excludes a missing side but not a book marked bad (F_MAYBE_BAD_BOOK); the mid is undefined while bad, bid_1/ask_1 are not; FH exits and TB barrier checks are then read two ways |
| LE-7 | SHOULD FIX | P1.2 (97-106), P1.5 item 5 (147-148), LT6 (415) | E.31's outputs are "never" read but are not in the list the guard refuses; the allowlisted E.32 briefs include X1_exposure.md, which reproduces E.31's queue-imbalance markout table (lines 273-278) |
| LE-8 | NOTE | P4.1 LT5 (412-414) | "the label shifted by one step" names one canary; y(t-1) and y(t+1) both leak and only the second is obviously future; name both |
| LE-9 | NOTE | P3.4 (243-246), P3.6 (262) | The TB vertical exit at tau + L with tau = t + L + h is t + 2L + h, 1 s outside the declared span; harmless but inconsistent with FH's t + h + L |
| LE-10 | NOTE | P8 G5 d (564-565), P6.5 (521-522), P9 | Discovery tercile cut points are outcome-free (sound); the test's tercile diagnostic does not say it reuses them (M5b b.5 trap 2) |
| LE-11 | NOTE | P5 LGBM inner block (434-435) | Causal (nothing in training follows the inner block), but for folds 1-5 the "latest 15% of training dates" is the same ~97-date tail of block 6, so five of six calibrators share one block |
| LE-12 | NOTE | P1.5 firewall item 1 (134-136) | "The shortest look-back is 1 minute; E.31's splits are at 1 s and 10 s" understates the overlap: QI1/QI3 are instantaneous states and E.31's markouts run to 60 s; items 2 and 4 carry the defence, item 1 should not overclaim |
| LE-13 | NOTE | P9 (589-592) | The ts_recv comparability check names no consequence; say explicitly that its outcome changes no rule (the pipeline orders by ts_recv either way) and is reported |
| LE-14 | NOTE | F3.10 (387) | A sweep group (one ts_event) is known only at its last record; say a group counts at the ts_recv of its last record and only if that is <= t |
| LE-15 | NOTE | F3 seasoned depth (370-371) | "last add or modify" should say "any A or M record for that order_id (size reductions included)" so the two implementations agree |
| LE-16 | NOTE | P8 frozen model (581-583) | Name the LOGIT scaler (G5) and the LGBM calibrator as parts of each frozen fold model; otherwise "nothing is refit" is read two ways |
| LE-17 | NOTE | P9 (587), 0.1 | T_test = 870 reproduces only with the hist calendar to 2019-05-31 and the program grains calendar after; neither alone gives 890 (902 and 908) |
| LE-18 | NOTE | P1.4 (ii) (93) | "scheduled late-open dates (measure31.calendar_reason)": that function also excludes recorded unscheduled late opens; in discovery both maps hold the same 8 dates; say which the rule means |

Counts: BLOCKING 1, SHOULD FIX 6, NOTE 11. Coverage (checked and found sound): 31 items, section 3 below.

## 1. Findings in full

### LE-1 (BLOCKING) The simulator's entry decision uses the future validity of the span

Text as written. P3.2: "A label whose span contains an update at which the ZM book lacks a bid or an ask is
excluded (P3.6 rule 5); the trade simulation checks the same rule on the whole span before entry." P3.5: "At a
decision time t at which the simulated account is flat and the span of the label starting at t meets P3.6: enter
long if ...". P3.6: "for the entry decision the whole possible span [t, t + L + h min] is used for both types. A
row is kept, and a trade may be entered at t, only if that span ... meets every rule: ... 5. ... no span with an
update at which the ZM book lacks a bid or an ask".

What is wrong. Rules 1-4 and the limit-proximity half of rule 5 are decidable at t (calendar, grid, M_ZM(t),
definitions). The first half of rule 5 is not: whether the book will be one-sided at any update in (t, t + L + h]
is known only at t + L + h. As a ROW rule (which labels exist, for training and for scoring OOF rows) that is the
ordinary "label undefined" exclusion and is fine. As an ENTRY rule in the P3.8 simulation it is a look-ahead: the
simulated strategy never enters a trade that would run into a limit-locked or halted book, which no live strategy
can know. The daily series X_D produced by P3.8 is the series behind SR_d, G1-G5, the ranking, Tier A and, in P9,
the one-shot verdict; so the look-ahead sits in verdict-producing code on both windows.

Size. In the day session a ZM book with no displayed ask or bid (full MBO depth) occurs at limit locks and halts.
The data facts count 7,630 F_MAYBE_BAD_BOOK records over 39 months (F 1.5) but no count of one-sided-book updates;
E.33 would report it under "how many rows and minutes each rule removes". Limit moves in ZM cluster on release
days (mostly inside the 30-minute exclusion) and on the largest-move days; the test window holds the 2018
trade-war limit days (soybean complex, May-July 2018) and the 2020 March liquidity collapse (R3b d), so the
discovery estimate of the effect does not bound the test's. The sign is unknown (the excluded entries are the
ones that would have been hardest to exit, and their realised P&L under a forced exit rule can go either way).

Proposed fix (replacement text). In P3.2 replace the second sentence with: "The trade simulation (P3.8) decides
entry at t from information known at t only: the ZM book has a bid and an ask at t, and rules 1-4 and the
limit-proximity part of rule 5 hold for the span [t, t + L + h min]. If at the fill time t + L the ZM book lacks
the side the order needs, no fill occurs, the decision is void and counted, and the account stays flat." In P3.6
rule 5 replace "no span with an update at which the ZM book lacks a bid or an ask" with "(rows) no span with an
update at which the ZM book lacks a bid or an ask or is marked bad; (trades) this part of rule 5 is not an entry
condition, see P3.2 and P3.8." In P3.8 add after the exit sentence: "If at the scheduled exit instant (FH:
t + h + L; TB: tau + L) the book lacks the side the exit needs or is marked bad, the exit fills at the first later
update at which that side exists and the book is not bad, at that touch, no later than 13:19:59 on D; if no such
update exists, the exit is marked at the limit price against the position (LL for a long, HL for a short, from
the definitions as of t) and the trade is flagged. During a TB trade, updates at which M_ZM is undefined are
skipped by the barrier check. E.33 reports the counts of void decisions, delayed exits and limit-marked exits
per configuration." This keeps the entry causal, is conservative in the forced case, and changes nothing on
dates without a one-sided or bad book. The lead may prefer a stricter variant (treat a delayed exit as a loss of
the full span's adverse move); any variant is fine as long as the entry rule reads only data with ts_recv <= t
and the fill at t + L. Add the simulator causality test of LE-5.

### LE-2 (SHOULD FIX) Limit prices "in force on D" are not tied to the decision clock

Text as written (P3.6 rule 5): "HL and LL are the front's high and low limit prices in the definitions in force
on D and c = (HL + LL)/2 ... If the definitions carry no limit prices for D, the second part is skipped for D".

What is wrong. Definition records (schema Z4, F 1.1) carry ts_recv and can arrive more than once per UTC day
(security_update_action; CME republishes the instrument definition when a limit is expanded or a field changes).
"In force on D" admits the reading "the last definition record dated D", which may postdate t. G1 says a
feature at t uses only records with ts_recv <= t; the exclusion rule should obey the same clock, or the two
implementations of E.33 B3 will disagree on days with an intraday definition update, and one of them will use a
future record. The expiration date (C.7) and tick size are static and unaffected.

Proposed fix. Replace "in the definitions in force on D" with "in the latest definition record of the ZM front
with ts_recv <= t (G1; if that record carries no limit prices, the latest earlier record with them on D; if none
on D, the second part of this rule is skipped for D and the date is counted)". Add the definitions stream to
LT1's truncation (LE-5).

### LE-3 (SHOULD FIX) The release-calendar rule does not match the two files as they are

Text as written (P3.6 rule 3): "Calendar: reports/stage_e31_briefs/research/usda_releases.csv (sha256 0743c0e2...)
and usda_releases_ext.csv (sha256 55df3b14...), E.31's sourced calendar covering 2020-12-01..2024-02-29, read as
reference data. Every row of those six reports with time 12:00 ET counts whatever its evidence grade; a calendar
month with no NOPA row gets its rule date (the 15th, or the next trade date if the 15th is not one) at 11:00 CT."

What I found (work_protocol_leakage/csv_check.py; schema and anomalous rows only, no dates printed beyond the
two non-date rows):
- usda_releases.csv (182 rows) covers the six reports for 2022-11..2024-02 only; usda_releases_ext.csv (272 rows
  after its comment line) covers 2020-12..2022-10. Together they cover the 39 months. The text attributes the
  whole coverage to the first file.
- The report strings are 'USDA WASDE', 'NASS Crop Production', 'NASS Crop Production Annual', 'NASS Grain
  Stocks', 'NASS Prospective Plantings', 'NASS Acreage', 'NOPA Monthly Crush (not USDA)'. The protocol names
  "NASS Crop Production (monthly and annual)" and "NOPA Monthly Crush"; an exact-string implementation misses the
  annual rows (4) and all NOPA rows (39). Counts per report over both files: WASDE 39, Crop Production 39 (+ 4
  annual), Grain Stocks 13, Prospective Plantings 3, Acreage 3, NOPA 37 dated + 2 undated.
- Two NOPA rows have date '2022-11-MISSING' and '2022-12-MISSING' with time_et '' and evidence "MISSING: 2022 NOPA
  reporting-dates PDF not found". Under the text, these rows do not count (time is not 12:00), and the months DO
  have a NOPA row, so the fallback ("a calendar month with no NOPA row") does not fire either: reading A gives no
  NOPA exclusion in 2022-11 and 2022-12; reading B (treat an undated row as no row) gives the 15th of each. Two
  exclusion sets, two outcome series on two dates.
- usda_releases_ext.csv begins with a '#' comment line; csv.DictReader on the raw file yields one two-column
  mess (my first attempt did exactly that). Three rows there carry a date ending in '-NORELEASE' (all FAS Export
  Sales, outside the six) and one row has time '17:00' (not one of the six).
- The calendar carries no outcome information (columns date, time_et, report, source_url, evidence): sound.

Proposed fix. Replace the calendar sentences with: "Calendar: the union of reports/stage_e31_briefs/research/
usda_releases_ext.csv (2020-12..2022-10; sha256 55df3b14...) and usda_releases.csv (2022-11..2024-02; sha256
0743c0e2...), E.31's sourced calendar, read as reference data: lines beginning with '#' are skipped; a row
counts iff its 'date' parses as an ISO date, its 'time_et' equals '12:00' and its 'report' is one of exactly
{'USDA WASDE', 'NASS Crop Production', 'NASS Crop Production Annual', 'NASS Grain Stocks', 'NASS Prospective
Plantings', 'NASS Acreage', 'NOPA Monthly Crush (not USDA)'}, whatever its evidence grade. A calendar month with
no counting NOPA row (2022-11 and 2022-12 in these files) gets its rule date (the 15th, or the next trade date
if the 15th is not one) at 11:00 CT. E.33 asserts 39 WASDE, 39 Crop Production and 39 NOPA release dates over
the 39 months and stops on any other count." P9's test calendar inherits the same parse and count assertions.

### LE-4 (SHOULD FIX) The embargo covers the longest look-back minus one date

Text as written (P6.1): "the embargo, the 20 trade dates immediately after block k's last date (20 = the
longest feature look-back in trade dates: sigma_X, the trailing references, F1.3's 10 dates, F1.7's and F4.7's
20)". LT3: "the embargo (20 dates) exceeds every label's span".

Derivation. Let E be block k's last date and D = E + 21 the first training date after the embargo (dates
E + 1..E + 20 removed). sigma_X(D), Vbar, Obar, Dbar, sbar, rbar and lam60's reference use minute marks inside
08:35-13:13 of dates E + 1..E + 20: none in block k. F1.3 uses 10 dates: none. F1.7's sd_g is the SD of
gC over the 20 dates E + 1..E + 20, and gC(E + 1) = C(08:35 on E + 1) - C(13:15 on E); likewise sd_gap for
F4.7 uses M_ZM(13:15 on E). So the feature of a training row on D contains one price from block k's last date.
That price is at 13:15, after every block-k label has ended (13:13:00 + L at the latest), so no label
information crosses; but the sentence "20 = the longest feature look-back" is wrong by one date, and LT3's
unit test as written would pass while the stated invariant does not hold. My script confirms the embargo
ranges (calendar_counts.py: after block 1, 2021-07-13..2021-08-09, 20 dates, and so on; none after block 6).

Proposed fix (either). (a) "the 21 trade dates immediately after block k's last date (21 = the longest feature
look-back in trade dates: F1.7's and F4.7's SDs over 20 overnight changes reach the 13:15 mid of the 21st prior
date; sigma_X, the trailing references and F1.3 reach 20, 20 and 10)", which removes 5 more training dates in
all; or (b) keep 20 and add: "F1.7's and F4.7's oldest overnight change uses the 13:15 mid of block k's last
date, which lies after every evaluation label of that date; this one price is admitted." LT3 then asserts the
stated rule.

### LE-5 (SHOULD FIX) LT1's scope, and no test of the simulator's causality

Text as written (LT1): "recompute every feature from record streams truncated at ts_recv <= t; every feature
equals the production value within G7's tolerance." LT2 checks spans and feature windows; LT3 folds, scaler,
calibrator, mu_k, early stopping; LT4 the clock; LT5 the canary; LT6 the guard.

What each can detect, as written. LT1 catches any feature that reads a later MBO/MBP-1 record, a normaliser
computed over the whole sample (the truncated recomputation changes it), and a wrong as-of join; it does not
catch a later definition record (LE-2) unless "record streams" includes definitions, and it cannot see a wrong
clock shared by production and recomputation (LT4 covers that by unit test: fine). LT2 catches window ends past
t and spans outside the session. LT3 covers the fold hygiene it names; the per-date uniqueness weights need no
test (whole-date folds). LT5 is caught by LT1 (a shifted label cannot be computed from the truncated stream).
LT6 is a guard test. Nothing tests that the P3.8 entry decision at t is a function of records with ts_recv <= t
(plus the fill at t + L): the look-ahead of LE-1 passes LT1-LT6 untouched, because it is not a feature.

Proposed fix. LT1: "from all input streams (ZM MBO, ZS and ZL MBP-1, definitions) truncated at ts_recv <= t,
with the calendars unchanged". Add "LT7 Simulator causality: for 200 decision times drawn with seed 20261028
across the OOF dates and 20 configurations, the entry decision (side or no trade) recomputed from the streams
truncated at t + L equals the production decision; any mismatch stops E.33 until fixed." Add to LT3: "and the
P3.7 weights of a training row use rows of its own date only".

### LE-6 (SHOULD FIX) "Marked bad" books are excluded from mids but not from rule 5 or from executable prices

Text as written. 0.3: "Mid M_X(u) ... defined only when both sides exist, bid_1 < ask_1 and the book is not
marked bad (F_MAYBE_BAD_BOOK)". P3.6 rule 5: "no span with an update at which the ZM book lacks a bid or an
ask". P3.3 uses bid_1 and ask_1 directly; P3.4 uses M_ZM(u) for the barriers and bid_1/ask_1 for the fills.

What is wrong. After an unrecoverable gap the Book stays bad until the next R (F 6.1, mbo_book31 mark_bad);
its bid_1 and ask_1 still exist. Under the text, an FH label whose exit instant falls in a bad stretch is kept
and priced from an untrustworthy touch, a TB label skips or stalls its barrier check (undefined mid: the text
does not say which), and the row rule 5 keeps the span. The two B3 implementations can diverge here. 7,630 ZM
records over 39 months (F 1.5) is small; the point is the missing rule, and that LE-1's fallback exit needs it.

Proposed fix. In rule 5: "no span with an update at which the ZM book lacks a bid or an ask or is marked bad
(F_MAYBE_BAD_BOOK, until the next R)". In P3.4: "updates at which M_ZM(u) is undefined do not trigger a barrier".

### LE-7 (SHOULD FIX) The guard does not refuse E.31's outputs, and the allowlist admits X1_exposure.md

Text as written. P1.2: E.33 may read "(d) E.31's code ... as a library ..., never E.31's outputs (runs/,
stats31.md/json, the measure31 tables, the result tables of reports/E.31_RETURN.md, reports/stage_e32_briefs/
work/X1_exposure/X1_tableC_appendix.md); (e) this protocol and the E.32 briefs. E.33 may not open: [the seal,
2024-03 onward, derived_unsealed_files.tsv, other roots' market data]. E.33's data guard refuses these paths and
dates in code". P1.5 item 5: "E.33's workers do not open E.31's outputs (P1.2)". LT6: "tests that the guard
refuses every path and date class of P1.2".

What is wrong. The "never" list is prose; the "may not open" list is what the guard and LT6 cover, and E.31's
outputs are not in it. And reports/stage_e32_briefs/X1_exposure.md, an allowlisted E.32 brief, reproduces
E.31's queue-imbalance markout table (lines 273-278: five QI bins with fill counts, 10 s and 60 s edges and
intervals) and names the split families (lines 220-221). The firewall's own rule is therefore contradicted by
its allowlist. Stakes are low (the protocol is frozen, the selection is mechanical, and P1.5 itself quotes
E.31's headline numbers), but a declared firewall should be enforceable.

Proposed fix. Move the "never" list into the "may not open" list (add runs/, stats31.md, stats31.json, the
measure31 tables, and the E.31_RETURN.md result tables by path or section), add reports/stage_e32_briefs/
X1_exposure.md and X1_verify.md to it, and in (e) write "this protocol, reports/stage_e32_methods_brief.md and the
E.32 reader files M1-M6, R1-R5, F". LT6 then covers them.

### LE-8 (NOTE) LT5's canary direction

"a deliberately leaked feature (the label shifted by one step)". The E.33 prompt (B4 iv) says "the label itself,
lagged by minus one step", that is y(t + 1). The subtler canary is y(t - 1): it looks like a past value but is
not known at t for any h >= 1 (it resolves at t - 1 min + h + L). Write: "two canaries, y(t + 1) and y(t - 1);
both must fail LT1".

### LE-9 (NOTE) The TB vertical exit instant

P3.4 exits at bid_1(tau + L) with tau = t + L + h min when no barrier is hit, that is t + 2L + h, 1 s after the
FH exit at t + h + L and 1 s past the declared span [t, t + L + h min]. Harmless at the grid (the last start is
13:12:00 - h, so the latest exit is 13:12:02), but one implementation may exit at t + L + h. Write the vertical
exit as "bid_1(t + h + L) (the FH instant)" or declare the TB span as [t, tau + L] with tau <= t + L + h.

### LE-10 (NOTE) Tercile cut points in the test

P8 G5 (d) is outcome-free: sigma_ZM(D) is a price statistic of the 20 prior dates, and cut points from the 796
OOF dates use no label or P&L. P6.5 and P9 report results by volatility tercile on the test without saying which
cut points; M5b b.2 item 5 and b.5 trap 2 require the frozen discovery cut points. Add the two cut points to the
test-list contents in P8 and the sentence "the test's tercile split uses them" in P9.

### LE-11 (NOTE) The LGBM inner block is causal but nearly the same for folds 1-5

"the latest 15% of the fold's training dates by date": for k < 6 this is the tail of block 6 (about 0.15 x 650 =
97 dates, all inside block 6's 132), for k = 6 the tail of block 5. No training date follows the inner block in
time, so inner-train rows cannot carry inner-validation outcomes; sound. Five of the six early-stopping choices
and calibrators then rest on one 97-date block. Not leakage; the lead may want it said, since the ensemble's
calibration is less diverse than "6 folds" suggests.

### LE-12 (NOTE) Firewall item 1 overclaims

"The shortest look-back is 1 minute; E.31's splits are at 1 s and 10 s." QI1 and QI3 (F3.7, F3.8) are states at
t, not look-backs, and E.31 measured markouts at 1, 10 and 60 s by five QI bins (X1 273-277), a forward
measurement of exactly F3.7's quantity on the discovery dates. Items 2 and 4 are the real defence (standard
definition from the literature, no sign or threshold imported, inference from the test only). Reword item 1 to
"No E.31 statistic sets a sign, threshold, look-back or weight; E.31's conditioning quantities that recur here
(queue imbalance, ZS/ZL moves) are named in items 2 and 3."

### LE-13 (NOTE) P9's ts_recv check should name its consequence

The saved Databento page says MDP 2 data (before 2017-05-21) has ts_recv set equal to ts_event with F_BAD_TS_RECV;
it does not say what ts_recv is from 2017-05-21 to Databento's own capture start. P9 makes it "a data check the
test stage makes from the metadata before the read (the pipeline orders by ts_recv either way)". Add: "Whatever
the check finds, no rule changes; the finding is reported with the verdict. If ts_recv equals ts_event on the
test files, the decision clock there is the exchange clock, 0.1-10 ms earlier than discovery's (F 1.4),
immaterial at a 1-minute grid with L = 1 s."

### LE-14 (NOTE) Sweep groups at the window boundary

F3.10 defines a sweep over "trade records sharing one ts_event" that leave the touch at 0. The outcome is known
only after the group's last record (F_LAST). Write "a group counts in the window ending at t iff the ts_recv of
its last record is <= t".

### LE-15 (NOTE) Seasoning reset

"orders whose last add or modify (by ts_recv) is at least 1.000 s before t". Write "whose last A or M record
(any modify, size reductions included) has ts_recv <= t - 1.000 s", so both implementations reset the clock the
same way. The E.31 Book stores [side, price, size, prio] without a timestamp (mbo_book31.py 168), so E.33 adds a
per-order ts_recv; feasible, causal.

### LE-16 (NOTE) What a frozen fold model contains

P8: "the 6-model ensemble of its folds: calibrated class probabilities averaged over the 6 fold models, and the
mu_k averaged over the 6 training folds; nothing is refit." Add "each fold model carries its own G5
standardisation (LOGIT) or its own booster-plus-calibrator (LGBM) as fitted; the test applies each fold's own
transforms before averaging".

### LE-17 (NOTE) T_test's calendar composition

T_test = 870 (P9) reproduces with the hist grains calendar for 2017-05-22..2019-05-31 (511 dates) plus the program
grains calendar for 2019-06-01..2020-11-30 (379), total 890, plus 15 dates 2017-05-01..2017-05-19 = 905
(work_protocol_leakage/test_window_counts2.py). The program grains calendar alone gives 908 from 2017-05-22 (no
holidays before its 2019-05-01 coverage start) and the hist calendar alone 902 (none after 2019-05-31). P9 and
the finalists document should name the composition so the test stage's T_test is the number the thresholds used.

### LE-18 (NOTE) Late opens

P1.4 (ii) says "scheduled late-open dates (measure31.calendar_reason)". calendar_reason returns LATE_OPEN for
`cal.scheduled_late_opens` or `cal.late_opens` (recorded, including unscheduled). In discovery the two maps hold
the same 8 dates (2021-07-06, 2021-11-26, 2022-07-05, 2022-11-25, 2023-07-05, 2023-11-24, 2023-12-26, 2024-01-02;
four of them also early halts). An unscheduled late open is known at 08:30 on D itself (no open), so excluding it
is not a look-ahead; say "scheduled or recorded late opens (both maps)" so the test stage applies the same rule.

## 2. Section-by-section notes (what I looked for and what I found)

0.3 Clock and conventions. "A record is known at time u iff its ts_recv <= u"; all ordering, look-backs, as-of
lookups, label starts and ends on ts_recv; ts_event never used for timing. Consistent with F 1.4 (ts_recv
monotone per symbol, trails ts_event by 0.1-10 ms for 96% of records, precedes it for 0.14-0.16%) and with
MathReview C-3's fix. The trade-date window [D-1 16:00, D 16:00) (measure31.day_bounds, read in code) and the
UTC-date front mapping (instrument_on docstring: a grain trade date's sessions lie inside UTC day D) agree; the
16:00-19:00 CT segment belongs to UTC D-1 under the mapping and to trade date D under day_bounds, but the market
is closed then, so no price record is affected. F section 2 states the v.0 front is assigned from the previous
day's volume (cited to E12, not re-verified here): point in time, since UTC day D-1's volume is complete at 13:20
CT D-1, before D's overnight session. ZM.v.0 flips back and forth around rolls (F 2: ZMU1 for one day inside a
ZMZ1 run, ZMN2 for three days after ZMZ2 took over); each flip is a roll date plus one under P1.4, which costs
dates but leaks nothing. sigma_X(D): the 20 trade dates before D, D excluded, burn-in as history, constant within
D, 1-minute changes never cross a date (so "chained across rolls" means across dates only): sound. Trailing
20-date references: same, sound. Windows on the open-time axis reaching into D's own overnight session: that
session belongs to trade date D and to D's front; sound.

P1. Files, hashes, allowlist: see LE-7. Burn-in 20 dates, OOF 796, 816 universe dates: reproduced
(calendar_counts.py; first OOF 2020-12-30). Exclusions: roll date and the next (roll_reasons, read), early
closes and late opens (calendar_reason, read; LE-18); the front on D is known before D, so the roll exclusion
is point in time. Firewall: no number from E.31 enters P4 (checked every feature's look-back, normaliser and
threshold against the E.31 splits named in X1 220-221); the release window is from literature and wider than
E.31's 0-5 minutes; the only overlap of substance is queue imbalance, disclosed (LE-12). The release calendar
carries no outcome field (LE-3 for its parse).

P2. Idea families: nothing here computes on data; the drift-burst look-ahead that M1 9 names is removed in
F4.11 (fixed-length windows defined by their end, all ends <= t, latest end on ties). Sound.

P3. Labels: both FH prices are at t + L and t + h + L; TB m0 at t + L, barriers on the mid from (t + L, t + L + h],
exit at tau + L; the dead zone is the spread plus fee, no tuned threshold; kappa fixed; L fixed; fee fixed. The
exclusion rules 1-4 are calendar- or grid-based; rule 5 half future (LE-1), half at t; rule 6 keeps rows. Rows
and weights: per label type and date, so per fold; TB realised spans in weights use outcomes, admissible for
training weights (AFML; M3 d.5 traps 1-2 are met: no cross-fold weights, no attribution weights in any metric);
the simulation (P3.8) is unweighted. The EV rule's mu_k from training rows only, weighted: sound. Simulation:
one position, 20 entries a date, exits at the label's instant, the next decision at the first grid minute at or
after the exit fill: causal apart from LE-1. X_D = 0 on dates without a trade, burn-in dates outside the series:
sound.

P4. All 59 feature definitions read for point-in-time (C 15, F1 8, F2 11, F3 12, F4 13): every window ends at t
or before; every normaliser is a prior-date statistic or a same-row bounded quantity; F1.3's OLS is fitted before
D's open on 10 prior in-segment dates with release minutes removed by calendar, D's segment membership known
from the mapping; F1.7/F4.7 use the previous date's 13:15 mid (LE-4 for the embargo count); F3 seasoned depth,
cancels "at the price that was the touch at that moment" (the book state before the record is applied), refills
within 100 ms by ts_recv, sweeps by ts_event group (LE-14) are all past-only; F4.6's Hi/Lo over [08:30, t]
includes t (fine); F4.9 at 08:35 is 0 by definition. G1-G7: G3's family flag and G4 clipping are per row; G5's
scaler is from the training fold; G6 reports clock offsets and changes no rule. Leakage tests: LE-5, LE-8.
Synthetic proofs: no real outcome enters; the null's false-positive statement is about P8 end to end: sound.

P5. LOGIT: training-fold scaler, no calibration beyond the model. LGBM: inner block LE-11; the calibrator on the
inner block only (M4's warning met); mu_k from all training rows (inner-train and inner-validation), which is
training data: sound. Seeds fixed.

P6. Folds: whole-date blocks; labels end by 13:13:00 + L on their own date, so no training label before block k
overlaps an evaluation label (the 340-minute close gap, M5a a.2 item 4) and no purge is needed; training rows
after block k are embargoed for the look-back (LE-4); evaluation rows' features reading training-period prices
is the ordinary flow of time, not leakage. The brief's question ("none before: is that right when the evaluation
block precedes training blocks?"): yes, the direction of the embargo follows the direction of the look-back,
which is always into the past, so only training rows AFTER the evaluation block can hold evaluation-period
prices in their features; rows before it cannot. Reversed walk-forward (P6.5) uses the same embargo after block
k with training on k+1..6: the right direction. P6.2's reported-but-unused statistics and P6.3's PBO use OOF
outcomes by design and select nothing (P1.5 item 5). P6.4/P6.5 run after the list hash.

P7. Thresholds are a function of N and T only; T_disc = 796 reproduced; T_test = 870 reproduced (LE-17).
Arithmetic belongs to the ArithmeticReviewer; I checked only that no threshold reads an outcome.

P8. Gates G1-G5 and the ranking read OOF outcomes by design; the rule is mechanical and complete (ties defined).
G5 (d) cut points outcome-free (LE-10). Tier B: two configurations by SR_d outside Tier A, test-only; they add no
exposure. The frozen ensemble: no fold model saw test data; LE-16 for what a fold model contains.

P9. The test's burn-in: ZM MBO exists from 2017-05-21 (saved Databento page, quoted in P9); the first 20 trade
dates 2017-05-22..2017-06-19 are burn-in and the first scored date is 2017-06-20 (test_window_counts2.py); every
look-back is <= 20 dates except F1.7/F4.7's oldest overnight change (LE-4), which on the first scored date needs
the 13:15 mid of the date before 2017-05-22, outside the purchase and inside the 15 sealed dates: that one gC is
invalid, sd_g has 19 values, and the "at least 10" rule still accepts it. The same happens on discovery (the
13:15 mid of 2020-11-30 is before the file start 2020-11-30T22:00Z and inside the seal), so the guard is never
asked for a sealed record and both windows follow one rule. F1.3 and F1.7/F4.7 will be invalid for the first in-segment dates after the
July 2017 ZM roll, as they are after the ZMF1 to ZMH1 roll of 2020-12-18 inside the discovery burn-in: the same
rule on both windows, G3 handles it. The release calendar for the test is built from public sources by the P3.6
rule before the read and hashed (LE-3's parse rules must carry over). The verdict code (edge_chain, dsr_table,
pbo, read) matches the P9 description: Holm at the list's K, DSR over the Tier A series when two or more else
over every run trial, population variance, t > 3.0, PBO over the Tier A series or all run series. The
protocol-added DSR at V = 1/(T_test - 1) is additional and stated. No test information reaches any choice.

P10. Stop rules are integrity- and feasibility-only; the null report reads outcomes after the fact: sound.

## 3. Coverage: checked and found sound (31 items)

1. ts_recv as the single decision clock (0.3, G1, G6, LT4) and its agreement with F 1.4/1.5 and C-3.
2. Trade-date window and UTC-date front mapping consistency (day_bounds, instrument_on read in code).
3. Front assignment from the previous day's volume is point in time (F 2, cited to E12).
4. sigma_X(D): D excluded, burn-in as history, within-date 1-minute changes only.
5. Trailing 20-date references and C.5's same-minute Vbar: prior dates only.
6. Decision grid vs rule 2: latest FH exit 13:12:01, latest TB exit 13:12:02 (LE-9 is clarity only).
7. FH label prices at t + L and t + h + L; N_long + N_short < 0 identity; no tuned threshold.
8. TB label: m0 at t + L, barriers from (t + L, ...], exit at tau + L; kappa and L fixed.
9. Row exclusion rules 1-4 decidable at t; the limit-proximity half of rule 5 at t.
10. Uniqueness weights per label type and date: no cross-fold dependence; training-only use.
11. mu_k from training rows only; ensemble averages the 6 training folds' mu_k.
12. F1.3 pre-open OLS: 10 prior in-segment dates, release minutes by calendar, segment known from the mapping.
13. F1.1/F1.2/F1.4/F1.6: windows end at t - 1 min; the current value is compared with the window excluding it.
14. F1.7/F4.7 overnight changes: previous date's 13:15 mid, a past value; SDs over prior dates (LE-4 only counts).
15. F2.1-F2.7 cross-asset returns as of t on ts_recv; sigma_X(D) prior-date scale.
16. F2.8-F2.11, F3.1-F3.4 OFI sums over windows ending at t; references from prior dates; equal IOFI weights (no fitted weights, M1 2.5 trap 3 met).
17. F3.5-F3.9 trade imbalance, seasoned QI, touch cancels: state at t or windows ending at t.
18. F3.10-F3.12 sweeps, refills, lambda: windows ending at t; references from prior dates (LE-14 clarity).
19. F4.1-F4.5, F4.9, F4.10, F4.13: returns and RV ending at t.
20. F4.6 RP over [08:30, t].
21. F4.11-F4.12 burst timing: all 14 window ends <= t, extremum over the past only, ties fixed (M1 9's trap removed).
22. C.1-C.15 context: time, calendar and prior-date quantities; validity flags per row.
23. G3/G4 per row; G5 scaler training-only; G7 tolerance.
24. LGBM inner block has no later training date (no inner embargo needed); calibrator on the inner block only.
25. Fold construction: whole dates; no purge needed (labels end in session); embargo direction correct; no embargo before the block is the right call.
26. Reversed walk-forward embargo direction.
27. P6.2/P6.3 outcome statistics are reported and never select; P6.4/P6.5 after the list hash.
28. G5 (d) tercile cut points from sigma: outcome-free.
29. Tier A/Tier B and the 6-fold ensemble: no test data in any fitted object.
30. Test burn-in: 20 dates after 2017-05-21 exist; first scored date 2017-06-20; T_test 870 reproduced.
31. Release calendars carry no outcome field; the test calendar is built before the read and hashed.

## 4. Not checked (outside this lens or not possible here)

- The arithmetic of P7 (SR0 0.1137, G3 0.1724, b_test 0.1649, G4 0.2007, the power table): ArithmeticReviewer.
- Hidden degrees of freedom in grids, gates and tie rules beyond those that touch leakage: DofReviewer.
- Compute and memory estimates in P5: FeasibilityReviewer.
- Whether one-sided-book updates occur in the ZM day session on discovery dates, and how often (would need the
  data; E.33's counts will say). LE-1's size is therefore stated as unknown, bounded by the rarity of limit locks.
- The Databento symbology rule behind ".v.N ranks expirations by the previous day's volume" (F 2 cites E12); not
  re-fetched (no web access used).
- Whether ts_recv on 2017-2020 GLBX.MDP3 files is a capture timestamp (P9 defers it to the test stage; the saved
  page only covers MDP 2 before 2017-05-21).
