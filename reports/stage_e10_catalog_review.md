# Stage E.10 Task 5: adversarial review of the draft K9 catalog

Reviewer: CatalogReviewer-FableXHigh (Fable 5.1, claude-fable-5-1, effort xhigh). Brief:
reports/stage_e10_briefs/reviewer_brief.md. Start 2026-10-02 23:31 PDT, end 2026-10-02 23:55 PDT (America/Vancouver).
No Stage E result was opened: nothing under data/, no reports/stage_e*_screen*, no confirmation record, no
*_RETURN.md, no results JSON. One external fetch (R-11), saved under reports/stage_e10_briefs/review_scratch/.

## Files reviewed (sha256 at review start, 23:31 PDT)

| File | sha256 | Note |
|---|---|---|
| reports/stage_e10_catalog_K9.md | 199eea594d0308318bbb6cff9676a6e381ef296618eb29bcb1c122ec8e8a9947 | matches hand-off (199eea594d0308318bbb) |
| reports/stage_e10_catalog_K9.json | 0dd851e5c7f61a86e84e421d3de7c85a9af6fb2646fd6f871fa96bc519241bb6 | matches hand-off |
| docs/STAGE_E_DESIGN_K9_DRAFT.md | 31ad9aedfe7016dc57b9d83e3747de0f611c9120681d5586ad03953ef4662470 | matches hand-off |
| reports/stage_e10_design_target.md | ce798814661bf40ee9440f9b021670972576b986d465f23f72bf5030617ca065 | matches reports/stage_e10_briefs/design_target.sha256 (recomputed); mtime 22:29:01 PDT, hash file mtime 22:29:07, readers started 22:32 (STATE) |
| reports/stage_e10_briefs/task4_lead_rulings.md | c19d2ab1748df2384e9b0971051e2d54d4cdb285d5d8a4c170235ecf2db6e214 | rounds 1 and 2 |
| reports/stage_e10_search_plan.md | 4a75b69a9672c91e677356183d48035dc784ad67ed5e3de1f5fe9298e8a9a346 | |
| reports/stage_e10_research_regime.md | 7f81ae147623e1bafbb4b5f2ebf83ea356de70784f0ca816b45e45cb1892a5be | |
| reports/stage_e10_research_overnight.md | ccb2f80d66327e5f580606389d54251241f238dd67de51b1689d1b933563c5ac | |
| reports/stage_e10_research_calendar.md | 17e8109dfe0eb66ad48d2be5664108597fb3e9fccf9f9c52b66e893dce12e077 | |
| reports/stage_e10_research_commodity.md | 4a07a69ac47fccd7a5b3d16323c4c725b4e4a1d456585c071a36b5e76466b771 | |
| docs/NULL_CRITERIA_E.md | b27ca69cf8f3ec411c0bc174b50c277e8b769e38f38581af171022ea3bef0cdd | section 3 |
| reports/stage_e10_research/cost_wall.json | 8ef052dc958f82f606e40e53da79a5186e5cf108a35b9b08769b46a328772f5d | before and after re-running cost_wall.py (R-13) |

Also read, by section: docs/STAGE_E_DESIGN.md D9 (lines 478-640); reports/stage_e0_catalog_K1.md (CP1-CP3
headings, K1-vxnband-01 lines 403-470, K1-predrift-01 lines 595-640); K2 (fomcpost, predrift, monthend
mechanism lines); K5-fomc-01; K7-montrend-01; K8-wkndbtc-01 (lines 490-610); docs/prompts/STAGE_E.10.md
(lines 28-40, 98-110, 166-182, 248-260, 305-316); progress.md lines 1260 and 1428 (the D.1 E-H1 family's
definition and D.1c verdict; no Stage E figure); the saved sources named in the catalog's section 8.
Scratch: reports/stage_e10_briefs/review_scratch/ (verify_quotes.py, verify_by_id.py, quote_check.tsv,
quote_by_id.tsv, cost_wall_before.json, hpwz_jfe_mit.pdf/.txt, fetchlog_review.tsv).

## Verdict table

Counts: BLOCKING 0, SHOULD FIX 8, NOTE 8. Two SHOULD FIX findings (R-01, R-03) become BLOCKING under the
stricter reading stated in each; the lead decides which reading governs and writes it down before the freeze.

| Id | Grade | Member or file | Finding |
|---|---|---|---|
| R-01 | SHOULD FIX | K9-vixspike-01 (X10 ruling) | The condition is a one-day change in VIX, not a "volatility level" as the design target's borderline test requires, and the source reports a -70% daily correlation between returns and that change; the ruling does not say it is extending the test, and the X10 falsification is descriptive only. BLOCKING under the stricter reading |
| R-02 | SHOULD FIX | K9-anncday-01 (novelty) | The entry never addresses the D.1 MES family E-H1 (unconditional long from the 17:00 CT open into FOMC/CPI/NFP; D.1c non-resolution) or the E.0 reason that excluded K1-predrift-01 ("MES scheduled-macro-drift family re-run on a sibling index"); the lead must rule on it in writing |
| R-03 | SHOULD FIX | K9-vixspike-01 (label; section 7 item 19) | K9R-006 (1990-2022) is listed in the member's evidence and in the JSON `sources` beside `source_overlap: false`; under NULL_CRITERIA_E section 3's letter that is source-overlap. Fix by removing K9R-006 from the entry's evidence (nothing else changes) or by flipping the label. BLOCKING if left as written |
| R-04 | SHOULD FIX | K9-vixspike-01 (quote gloss, C-K9R-001-24) | "large price drops alone do not carry the premium" overstates Table 8: next-day returns after large drops are positive and larger than the member's own row (15-28 bps versus 10.34 bps), only less significant on fewer days |
| R-05 | SHOULD FIX | K9-vixspike-01 (cutoff) | No stated rule picks the 1.0 cutoff over the source's 0.5 cutoff, which meets (b)1 with margin (about 62 capped trips) and matches the design target's own preference for the upper end of the band; the (b)1 shortfall the user is asked to waive follows from this unexplained choice |
| R-06 | SHOULD FIX | docs/STAGE_E_DESIGN_K9_DRAFT.md (D-entry amendment) | The round-2 change of D-entry (17:00 first bar to 17:59 intent / 18:00 fill) is a design-rule change made after sources were read; it is absent from the design draft's decisions (K9-A..G), so E.11 would freeze it without a user decision; its justification is a judgment, not "a frozen constraint" |
| R-07 | SHOULD FIX | K9-anncday-01 (decision time) | "Known in advance from the official schedules" has no evidence for the releases rescheduled by the 2025 lapse in appropriations (about 8 of the 60 dates); the dates were read ex post from archive file names |
| R-08 | SHOULD FIX | Excluded table row 2 (pre-announcement overnight long) | The secondary reason "the 2012-2018 row is weak" contradicts the source ("stable and significant", 6.98 bps); and the offer to the user omits that this variant is NOT source-overlap while K9-anncday-01 IS, and that the post-release segment the member adds has near-zero mean and large variance in the source |
| R-09 | NOTE | K9-vixspike-01 (37.8 trips) | The "40 of 202" inference behind 37.8 is traceable (Table 2 Non-Ann 4,976 minus Table 9 Normal Days 4,814 = 162 of 202) but the derivation was dropped with Q1; restate it |
| R-10 | NOTE | design target header; STATE | The design target's header says "22:40-23:10 PDT" while its mtime (22:29:01), the hash file (22:29:07) and the STATE row (22:24-22:29) place it before the readers started (22:32); STATE says the design draft was "written 23:32" though its mtime is 23:24:40. The hash is intact; the stated times are not |
| R-11 | NOTE | K9-vixspike-01 (round 2 item 16) | The published version's author manuscript (JFE, accepted 1 September 2021), saved to scratch, states "The sample period is from September 1994 to May 2018" and carries identical Table 7 rows; the E.11 re-check can be closed as "not source-overlap" |
| R-12 | NOTE | both members (holiday sessions) | "Trade date t+1" and the announcement set are undefined for CME sessions without a US cash session (Thanksgiving Thursday half session; Good Friday 2026-04-03, which carries the Employment Situation); K8-wkndbtc-01 excluded early-halt and closure dates |
| R-13 | NOTE | reports/stage_e10_research/cost_wall.json | Re-running cost_wall.py rewrote the file in place; content byte-identical (sha256 8ef052dc unchanged), mtime moved to this review |
| R-14 | NOTE | K9-vixspike-01 (X14 ruling) | Accepted on the K1-vxnband-01 precedent; the signal is the S&P 500's implied volatility transferred to three sibling indices, which the entry states |
| R-15 | NOTE | Appendix A (K9-vixback-01) | Both withdrawal reasons hold against the saved source (Table 3, K = 1 day: D1 and D2 starred, D3 and D4 not); the cap arithmetic reproduces |
| R-16 | NOTE | K9-vixspike-01 (ratio route) | 0.115 divides a 1994-2018 return by the 1986-2018 standard deviation (which includes October 1987); conservative, and the entry says so |

## Findings

### R-01 (SHOULD FIX; BLOCKING under the stricter reading): K9-vixspike-01 against X10

**What is wrong.** The design target fixed the borderline test before any source was read: "'Long the session
after a volatility spike' differs from X10 only if the mechanism is a state-dependent risk premium, with no
fade of a specific move (the condition reads a volatility level, not the sign of the last move). A rule signed
against the prior move is X10." (reports/stage_e10_design_target.md lines 174-177). The member's condition is
VIX_close(t) - VIX_close(t-1) >= 1.0, a one-day change, not a level, and the trade is long after that specific
move. The source itself ties the change to the sign of the price move: "although the correlation between daily
returns and daily changes in VIX is close to -70%, the information contents of these two variables are not the
same" (reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt lines 1660-1662), and its Prediction 5
frames the trade as a reversal: "Unanticipated spikes in VIX will be followed by VIX reversals and high re-
turns." (line 859). So on most signal days the rule is "long the day after a down day", which X10's row calls
"the same mechanism at a different frequency" (design target line 161).

The lead's ruling (rulings lines 28-31) says the condition "reads an implied-volatility change, not the sign or
size of the price move". That is literally true, but it does not meet the borderline test as fixed ("level"),
and the ruling does not say it is extending the test from a level to a change, or why. The only evidence that
separates the two readings is the source's Table 8, and R-04 shows the entry overstates what it says. The
entry's falsification lists a "reversal check (X10 risk), reported" (catalog lines 343-346) with no pre-stated
reading, so the screen never resolves the X10 question.

**Why not BLOCKING outright.** The signal variable differs from every X10 member: K1-vxnband-01 fades an
intraday breach of a band sized by VXN with a 30-minute hold (reports/stage_e0_catalog_K1.md lines 403-470), the
K4/K5/K6 overreaction members and K7-rev2h fade the vehicle's own move. The design target pre-declared this
borderline for a lead ruling (lines 172-177), so the member does not differ "only in parameters, frequency or
product" from a tested family; it differs in the signal read. Whether that difference is a different mechanism
is the judgment at issue.

**Fix.** (1) The lead's ruling states in writing that the borderline test's "level" is read to cover a one-day
change in the implied-volatility index, and gives the ground (the model-led mechanism, P-K9R-001-h; Table 8's
significance contrast read correctly per R-04), or withdraws the member. (2) The reversal check gets a
pre-stated reading in the entry: the mean trip P&L on signal days whose day-session return of the vehicle
(D-ret) is non-negative is reported beside the overall mean; if the overall mean is positive only through the
negative-return subset, the entry records "reversal of the spike-day fall (X10 in mechanism), not an
uncertainty premium", and the lead states now whether that reading affects Tier A or is descriptive. (3) The
entry's X10 risk paragraph carries the -70% correlation sentence (line 1660-1662) as the source's own statement.

### R-02 (SHOULD FIX): K9-anncday-01 against the D.1 family E-H1 and the E.0 exclusion of K1-predrift-01

**What is wrong.** The entry's exclusion-list check covers X4, X6 and X12 (catalog lines 433-445) and never
mentions the program's own D.1 family E-H1, "scheduled macro drift": on MES, long "from the trade date's
17:00 CT open to the release, about 14.5-20 hours" (progress.md line 1260), which "goes long before FOMC, CPI
and NFP releases whatever the direction" (reports/stage_e0_catalog_K1.md lines 618-619), with the D.1c verdict
"NON-RESOLUTION" (progress.md line 1428; underpowered, 31 trades in 289 days per line 1281). At E.0 the lead
excluded K1-predrift-01 with 0 trials because it was "MES's scheduled-macro-drift family (E-H1/E-H2, class C5,
null on MES under docs/NULL_CRITERIA.md) re-run on the Dow, a sibling index highly correlated with the S&P; the
K1 brief allows MES families only through the core ports" (K1 catalog line 597). K9-anncday-01 is an
unconditional long on three sibling indices from 18:00 CT the evening before through the release to 14:59 CT:
its first 13.5 to 19 hours are E-H1's trade, with a wider date set and a longer hold. The Excluded table's
pre-announcement variant (row 2) is E-H1 almost exactly (reopen to release - 5 min on NFP/ISM/GDP).

The design target (c) says: "A K9 member may revisit [an E.0 excluded entry] only if it states why E.0's
failure reason no longer applies" (lines 168-170). K9-anncday-01 is not literally K1-predrift-01, and the E.10
prompt scopes the exclusion list to "every family Stage E already tested" (docs/prompts/STAGE_E.10.md line
170), so this is not a formal X1-X15 breach; that is why it is not graded BLOCKING. But the lead's E.0
reasoning applies to K9-anncday-01 at least as strongly as it applied to the signed drift it excluded, and
the catalog is silent on it. The prompt's stated silent failure is exactly "a catalog that looks new but
repeats a family ... already tested" (line 35).

**Fix.** The lead rules in writing whether the E.0 reason ("MES family re-run on a sibling index") binds K9.
If yes, the member is cut (K9 then holds 3 trials, or 0 with R-01's stricter reading). If no (defensible: the
K1 brief's rule was K1-specific; E-H1's verdict was a non-resolution, not a null; the date set, the hold and the
source literature differ), the entry states that in its exclusion-list check, and the Excluded table's row 2
cites E-H1 as a further reason for the variant's exclusion (its window coincides with E-H1's).

### R-03 (SHOULD FIX; BLOCKING if left as written): K9R-006 and the "not source-overlap" label

**What is wrong.** docs/NULL_CRITERIA_E.md section 3 (lines 78-83): "every member records its sources' data
windows. A member whose supporting source's sample overlaps its confirmation window was chosen partly on
evidence from that window, so its confirmation is not fully out of sample. Such a member is labelled
'source-overlap' in the hashed list". The trigger is the overlap of a supporting source's sample; the "was
chosen partly" clause is the rationale, and the program has applied the rule by its letter (E.1 audit FA-06,
same section: every member without a recorded window is source-overlap; the R-04 rulings on K1-vxnband-01,
K2-fomcpost-01, K5-fomc-01 and K7-montrend-01 in the E.0 catalogs). The catalog lists K9R-006 in the member's
evidence under "Context (supporting sign at longer horizons)" (catalog lines 201-209) and in the JSON as a
`sources` element with `sample_window` "1990..2022" beside `source_overlap: false`. As written, a listed
supporting source overlaps the confirmation window and the label says it does not. The lead's item 19 ruling
(post-selection context, no literal taken) is reasonable in spirit, but it creates a third category the rule
does not have, and E.11 would hash the inconsistency.

**Fix (either).** (a) Remove K9R-006 from the member's evidence and from the JSON `sources`; keep it in section
5 as "read in round 2 after selection; monthly horizon; not used". Nothing else changes and the label stands.
(b) Keep it and label the member source-overlap. (a) is the cleaner fix. If K9R-006 stays in the entry with
the label unchanged, the finding is BLOCKING (a label that contradicts a recorded window).

### R-04 (SHOULD FIX): the Table 8 gloss overstates the source

**What is wrong.** Catalog lines 328-331: "Within the source, Table 8 (1986-2018) shows that large price drops
alone do not carry the premium: after daily falls beyond -1.5% to -2.4% the next-day t-stats run from 0.74 to
1.77 ... This supports the VIX reading over a pure reversal". Source, lines 1657-1660: "As shown in the left
panel, after large price drops, the stock market does on average yield positive returns on the next day, but
the predicted returns are statistically insignificance." Table 8 left panel (lines 1670-1683): cutoff -2.4,
5.3 days a year, 27.96 bps, t 1.26; -2.3, 6.0, 16.93, 0.85; -2.2, 7.0, 14.70, 0.84; -2.1, 7.7, 12.15, 0.74;
... -1.5, 16.3, 15.48, 1.77. The point estimates after price drops (12-28 bps) are larger than the member's own
row (10.34 bps at the 1.0 cutoff, 39.7 days a year, t 2.01); only the significance is lower, on 5-16 days a
year. "Do not carry the premium" is a misreading; the t-stat range quoted is correct. The sentence is
load-bearing for the X10 ruling (R-01).

**Fix.** Reword to the source's claim ("positive, of comparable or larger size, statistically insignificant on
5-16 days a year") and move it from the "supports the VIX reading" sentence into the X10 risk paragraph.

### R-05 (SHOULD FIX): the cutoff selection rule

**What is wrong.** The rulings choose the 1.0 cutoff "by design rule (b)1: the source's 1.0 cutoff gives 39.7
days a year (about 47 in 299 dates), and its 1.5 cutoff gives 24.6 (about 29, below the 40-trip expectation).
The choice follows the frequency rule, not a result." (rulings lines 19-21). (b)1 admits any cutoff whose
expected count is at least 40, and the design target's reading 3 says to "prefer conditions that fire near the
upper end of the band (one to two trades a week) over very rare conditions" (lines 83-85). The source's 0.5
row, under the same η = 0 panel, is "0.5 68.0 7.87 2.28" for 1994-2018 (line 1612) and "0.5 65.4 4.84 1.62" for
1986-2018 (line 1623): 68.0 / 252 x 299 = 80.7 trips before the non-announcement filter, about 68 after it
(x 0.842), about 62 after the cap (binomial as in C10). It clears (b)1 with the one-third margin, needs no user
waiver, and its t-stat (2.28) is above the 1.0 row's (2.01) on the main sample. The rulings give no rule for
1.0 over 0.5. Both figures are the source's, so this is not a Stage E result leak; but the lever that produced
the (b)1 shortfall now put to the user (K9-G.1) is this unexplained choice, and the lead's own reading 3
points the other way.

**Fix.** The lead states the selection rule it applied (the arithmetic implies "the largest cutoff whose
unfiltered count clears 40", which is a rarity preference, the opposite of reading 3) and offers the 0.5
cutoff in K9-G.1 beside the waiver as the alternative that satisfies (b)1 as written. The no-grids rule still
holds: the user picks one literal set.

### R-06 (SHOULD FIX): the D-entry amendment is not in the design draft

**What is wrong.** Round 2 item 5 replaces the design target's D-entry default ("on the 17:00 CT reopen this is
the first bar at or after 17:00 CT", design target lines 136-138) with intent on the 17:59 CT bar and a fill at
18:00 CT for every K9 reopen entry, "on weekdays and Sundays alike" (rulings lines 129-133). This is a change to
a design rule fixed before sources were read, made after they were read, on a non-result ground. It has a
transfer cost both members state (catalog lines 212-216 and Q20(a), lines 674-676: the 15:00-18:00 CT part of
the sources' close-to-close return is missed). The design draft lists the K9 design decisions for the user
(K9-A to K9-G) and does not contain it: K9-F prints "18:00 fill" as a fact and K9-G asks no decision on it. E.11
would then freeze a changed D-entry without a recorded user decision, against the draft's own rule that
accepted proposals go into an amendment and docs/DECISIONS.md (draft lines 3-7).

On the justification: D9.4 is a conduct rule against "Initiating reckless trades in gapped markets to profit
from stray fills" (docs/STAGE_E_DESIGN.md lines 505-508); K8-wkndbtc-01 applied it to the Sunday reopen after
a weekend closure and also wanted the 00:00 UTC crypto-day boundary (reports/stage_e0_catalog_K8.md lines
553-559). A weekday reopen follows a one-hour halt, the harness charges slippage on every fill, and one
market order at q_c once a day is not a stray-fill pattern. Extending the one-hour wait to weekdays is a
judgment; the rulings call it "a frozen constraint and precedent" (line 132), which overstates it. Inside the
catalog the amendment is applied consistently (C3, both members, Appendix A), so there is no internal
inconsistency.

**Fix.** Add the amendment to the design draft as its own item (K9-H, or inside K9-B) with the D9.4 reasoning,
the K8 precedent, the transfer cost, and the alternative (the 17:00 CT first bar, as D-entry was fixed), for the
user's decision; record the decision in docs/DECISIONS.md at E.11.

### R-07 (SHOULD FIX): "known in advance" is unsupported for the rescheduled BLS releases

**What is wrong.** Catalog lines 420-421: "Decision time: known in advance from the official schedules; the date
set for d is fixed from the calendar published before d's first bar." The EC-K9 dates were read ex post from
the BLS archive file names (C9, lines 116-117), which give actual release dates, not announcement dates. For
the releases moved by the October-November 2025 lapse in appropriations the catalog has no passage showing
when the date became public: Employment Situation 2025-11-20 and 2025-12-16 and 2026-02-11 (not a first
Friday); CPI 2025-10-24 and 2025-12-18; PPI 2025-11-25, 2026-01-14, 2026-01-30 and 2026-02-27 (the inflation
pairing uses the CPI dates 2025-10-24, 12-18 and 2026-02-13). About 8 of the 60 member dates rest on an
unsupported claim. The ISM dates carry an [unverified] flag (line 125); these do not. (The saved archive
pages do confirm the dates themselves: bls_empsit_archive_sget.html file names empsit_11202025,
empsit_12162025, empsit_02112026; the CPI and PPI archives likewise; and the reference-month titles the
pairing needs: "September 2025 Consumer Price Index" at cpi_10242025, "November 2025 Producer Price Index"
at ppi_01142026, "December 2025 Producer Price Index" at ppi_01302026.)

**Fix.** Fetch and save BLS's revised-schedule notice (the news-release schedule page as captured in November
2025, or BLS's "revised release schedule" notice), record each affected release's announcement date, and keep a
date only if its announcement precedes the entry intent (17:59 CT the evening before); otherwise drop it or flag
it [unverified] as ISM is. State in the entry that E.12's harness uses the date set as known at the entry
intent.

### R-08 (SHOULD FIX): the pre-announcement overnight long's row

**What is wrong.** Excluded table row 2 (catalog line 535): "The 2012-2018 row is weak (P-K9C-006-f)". The
source says the opposite of "weak": "the performance of the non-FOMC macro announcements remains stable and
significant across all three subperiods. In particular, during the last subperiod of 2012-2018, the
pre-announcement return is on average 6.98 basis point and statistically significant for the non-FOMC macro
announcements" (P-K9C-006-e, reports/stage_e10_research_calendar.md lines 311-315, verified by the reader in
the saved text). The row's primary reason (variant of K9-anncday-01; the hold window as a parameter under
no-grids) is a lead judgment and stands, and R-02 adds a stronger one (the window is E-H1's). But the row is
"offered to the user as K9-anncday-01's alternative window", and the user's comparison needs two facts the row
and K9-G omit: (i) the variant's source (HPWZ, sample to May 2018; R-11) is NOT source-overlap, while
K9-anncday-01 IS (K9C-003 to 2023-08), so an edge on the variant could be claimed without a registered holdout
read and an edge on the member could not; (ii) the source reports that the post-announcement segment the member
adds has "small and insignificant" returns "while exhibiting large variances" (P-K9C-006-c, calendar log lines
303-305), which lowers the daily t-statistic that D5 screens on.

**Fix.** Replace "weak" with the source's statement; add (i) and (ii) to the row and to K9-G.

### R-09 (NOTE): the "40 of 202" derivation

Catalog line 299 cites "40 of 202 in Table 9, inferred in Q1", but Q1's text was replaced by its answer summary
(section 7). The figure reconstructs from the source: Table 2 gives Non-Ann 4,976 and All Days 5,965
observations (lines 1004-1005) and Table 9 gives Normal Days 4,814 (line 1780, "all trading days that are not
FOMC, NFP, ISM, and GDP announcement days and not heightened VIX days", lines 1787-1789): 4,976 - 4,814 = 162
non-announcement HVIX days of 202, so 40 HVIX days (19.8%) fall on announcement days against 16.6% of all
days. Fix: restate this in the entry so 37.8 is traceable without the round-1 question.

### R-10 (NOTE): provenance times

reports/stage_e10_design_target.md line 3 says "22:40-23:10 PDT, before any literature source is read". Its
mtime is 22:29:01 PDT, the hash file's mtime 22:29:07, the STATE row says 22:24-22:29, and the readers
started at 22:32. The recomputed sha256 equals the stored one, so the file has not changed since 22:29:07
and the "before any source" claim holds; the header's times are wrong. STATE row 4 says the design draft was
"written 23:32" while the draft's mtime is 23:24:40 and STATE's own mtime 23:24:50; the rulings file says
"23:25 PDT" (mtime 23:23:54); the catalog header says "23:27-23:31" (mtime 23:30:35). Fix: do not edit the
hashed design target; record the mtimes and the discrepancy in the E.10 return and correct the STATE row.

### R-11 (NOTE): the published version's sample, resolving round 2 item 16

Fetched by curl and saved: reports/stage_e10_briefs/review_scratch/hpwz_jfe_mit.pdf (URL
https://www.mit.edu/~zhuh/HuPanWangZhu_preannouncement.pdf, 2026-10-03T06:41:55Z, sha256
f926f3efaae9b530023f90b0996cdf09e0452d75485a17ba2673dc762b889681, 33 pages; text in hpwz_jfe_mit.txt; row in
fetchlog_review.tsv). It is the author manuscript of the JFE article ("ARTICLE IN PRESS", "Received 28 July
2021", "Accepted 1 September 2021", DOI 10.1016/j.jfineco.2021.09.015, txt lines 34-37, 85). It states "The
sample period is from September 1994 to May 2018." (line 958) and "extend the sample period to May 2018. We
focus most of our analysis on the sample from September 1994 to May 2018" (lines 851-853), and its Table 7
rows are identical to the NBER text's ("1.0 39.7 10.34 2.01", line 1755; "1.0 36.5 6.59 1.41", line 1766). The
"not source-overlap" label therefore holds on the published version too; E.11 can close the re-check with this
file. Caveat: an author-hosted accepted manuscript, not the typeset article.

### R-12 (NOTE): holiday sessions without a US cash session

Both entries define the trade as "the 17:59 CT bar of calendar day t" into "trade date t+1" (lines 244-250,
423-429), and C4 excludes only dates where the external series has no value for the decision day. Two cases
are undefined: (a) Thanksgiving Thursday is a CME equity session (Wednesday 17:00 to Thursday 12:00 CT) with
no cash session and no VIX close, so a VIX spike on the Wednesday would be traded into the Thursday half
session, not the source's next day (Friday); (b) Good Friday 2026-04-03 carries the Employment Situation
(bls_empsit_archive_sget.html, empsit_04032026) while the cash market is closed and CME runs an abbreviated
session, so K9-anncday-01 would hold from Thursday 18:00 to the early F with no cash-index day behind the
source's return. K8-wkndbtc-01 excluded "Monday trade dates that EC-CAL marks as early halt or closure"
(K8 catalog lines 571-574). Fix: define t+1 (and d) as a date on which both the CME equity session and the US
cash session are open (regular or early close), and exclude early-halt sessions from the D10 calendar; two or
three dates a year at most.

### R-13 (NOTE): cost_wall.py rewrote its output

The brief allowed running reports/stage_e10_briefs/cost_wall.py; its OUT path is
reports/stage_e10_research/cost_wall.json, which it rewrote. The content is byte-identical (sha256
8ef052dc958f82f606e40e53da79a5186e5cf108a35b9b08769b46a328772f5d before, in review_scratch/cost_wall_before.json,
and after; the same value the catalog JSON records under `inputs`). Only the mtime moved. The script's table
matches the design target's table row for row, including MYM's RT_X 7.52 against the event-window 7.19.

### R-14 (NOTE): the X14 ruling

Accepted. The design target's X14 is "a signal read from another market's move (the K8 class; V16)"; VIX is
the S&P 500's option-implied volatility, the precedent K1-vxnband-01 conditioned a Nasdaq-100 member on VXN
inside K1, and the design target itself transfers S&P 500 evidence to the three equity exposures for every
member. The entry states the transfer (VXN, RVX and VXD not used). No change.

### R-15 (NOTE): Appendix A's withdrawal reasons hold

Reason (a): the D-pct persistence arithmetic (55.9 independent, 23.9 in full weeks) reproduces. Reason (b):
fassas_hourvouliades_2019_jrfm.txt lines 566-569, K = 1 day column: "D1 0.0237 **", "D2 0.0050 **", "D3
0.0005", "D4 0.0000"; 0.10 x 299 = 29.9. Table 2's K = 1 day row (lines 523-525) reads "-0.0004 0.0245
-0.1687 *** 0.009 10.59 2.07" as quoted. No change.

### R-16 (NOTE): the ratio route's mixed samples

The 0.115 ratio divides the 1994-2018 return (10.34 bps) by 0.798 x 1.13%, the daily standard deviation of the
1986-2018 sample (Table 8 note, lines 1687-1688), which includes October 1987; the 1994-2018 standard
deviation is not reported. The denominator is overstated, so the ratio is conservative for the member; the
entry says the sample mismatch (line 309). No change.

## Per-member checklist

| Check | K9-vixspike-01 | K9-anncday-01 | Appendix A (K9-vixback-01, withdrawn) |
|---|---|---|---|
| 1 Quotes | pass; one gloss overstated (R-04); all passages found (table below) | pass | pass (R-15) |
| 2 Novelty | X10: R-01; X14: accepted (R-14); X1-X9, X11-X13, X15: pass | X4, X6, X12: rulings accepted (the member reads no pre- or post-release move and is keyed to release calendars; 29 of 60 dates sit at the turn of the month and the day-of-month split is in the falsification); D.1 E-H1 and the E.0 K1-predrift-01 reason: R-02 | not assessed beyond the withdrawal |
| 3 Data hygiene | pass: every literal traces to a passage or a rule (parameters table, lines 280-291); design target hash intact (R-10 on its header); the cutoff selection rule is unstated (R-05); no exposure narrowing | pass: literals trace (lines 451-459); the GDP first-and-last and inflation pairing follow the source | pass (literals trace to C-K9R-004-*) |
| 4 Arithmetic | pass: 39.7 / 252 x 299 = 47.1; 50 announcement dates of 316 (10 + 14 + 15 + 13 - 2); 47.1 x 0.842 = 39.7; 37.8 traceable (R-09); cap by binomial 38.5 / 36.7 / 45.1 (catalog 38.4 / 36.7 / 45.1); ratios 0.115 and 0.073, M_X ratios 5.1x / 1.28x / 1.33x and 3.3x / 0.81x / 0.85x; G(f) at f = 0.128: 1.83 / 1.86 / 1.69; "one sixteenth" | pass: union 60 (62 - 2), weeks 30 / 12 / 2, 58 after the cap, 56.8 / 54.9 scaled; 11.4 / (0.798 x 98.6) = 0.145; M_X ratios 6.5x / 1.62x / 1.68x; G(f) at f = 0.1835: 1.28 / 1.31 / 1.19; C12 figures (300 / 100 / 100 ticks; $363 / $318 / $393) | pass: 59.8; 55.9 / 23.9; 29.9 at 10% |
| 5 K9 shape and D9 | pass: two a week by D-wk; one position; inside trade date t+1 (18:00 to 14:59 CT, 20 h 59 min); flat by F; market; q_c; D9.3, 5, 5a, 6, 7, 12, 13 addressed; look-ahead: VIX close publication before 17:59 CT [unverified] and routed to E.12, fallback sourced (Table A1 line 2029-2033). Open: D-entry amendment recorded only in the rulings (R-06); holiday sessions (R-12) | pass: as left; the hold contains the release at q_c <= 0.3 lot-equivalent (D9.5 permits it, D9.5a clear of 07:30, 09:00 and 13:00 CT fills); early-close exit at F; Mondays listed are the seven Monday dates in the set. Open: decision time for rescheduled releases (R-07); Good Friday 2026-04-03 (R-12) | as left (not frozen) |
| 6 Source-overlap label and trials | label "not source-overlap" on K9R-001 (to 2018-05) is right and now confirmed on the published version (R-11); but K9R-006 (1990-2022) is listed as a source (R-03). No holdout-2 or research-window overlap. 3 trials | label "source-overlap" is right (K9C-003 to 2023-08; also K9C-007 to 2019-12 among the conflicts); no holdout-2 or research-window overlap; 3 trials | not source-overlap (2010-01-04..2017-12-29); 0 trials |

Trial count and N: 2 members x 3 exposures = 6; 198 + 6 = 204; budget 40, 34 unused. Consistent across the
catalog .md (header, section 6), the .json (`totals`), the rulings (round 2 totals) and the design draft (K9-F).

Excluded table (check 7): every row's primary reason is in the rulings and is consistent with the logs'
"Candidate mechanisms" sections (regime lines 721-768, overnight 789-827, calendar 809-853, commodity
734-771), which list exactly the admitted and excluded set; no sourced, shape-fitting, novel mechanism in those
sections was passed over. The sources the rulings do not name (K9R-009 to -011, -015, -016, -018, -020 to -025;
K9C-012, -013, -019; K9O-006 to -008, -012, -015 to -019; K9M-006, -009, -012, -015, -016, -018, -020) are
context, conflicts or non-survivors in their own logs. One row's secondary reason is wrong (R-08).

## Passage re-verification table

Method: reports/stage_e10_briefs/review_scratch/verify_by_id.py locates, for each section 8 row, every quoted
string in the catalog followed by that passage id and searches it in the row's saved file (normalization:
whitespace collapsed, line-break hyphens joined, curly and straight quotes and dash glyphs equated, HTML
tags stripped and entities decoded). Rows the script could not pair with a quote (evidence-only rows, rows
quoted under a sibling id such as P-K9R-002-c#1-3, and the repo-file rows RUL-*, DT-*, D9-*, F9-*, K8-1, LOG-1)
were checked by direct grep or by reading the passage in context, as the "how" column says. "Found" means the
quote is in the saved file and says what the entry claims in context; "misread" means found but glossed
beyond what it says.

| Passage id | Saved file | Catalog line claim | Status | How verified |
|---|---|---|---|---|
| P-K9R-001-b | hu_pan_wang_zhu_nber_w25817.txt | 291 | found | script, L291 |
| P-K9R-001-c | hu_pan_wang_zhu_nber_w25817.txt | 297 | found | script, L297 |
| P-K9R-001-d | hu_pan_wang_zhu_nber_w25817.txt | 1588 | found | three pieces at L1588-1592; the catalog splices them with "..." |
| P-K9R-001-e#1 | hu_pan_wang_zhu_nber_w25817.txt | 1609 | found | script, L1610 |
| P-K9R-001-e#2 | hu_pan_wang_zhu_nber_w25817.txt | 1610 | found | script, L1610 |
| P-K9R-001-f#1 | hu_pan_wang_zhu_nber_w25817.txt | 1619 | found | script, L1620 |
| P-K9R-001-f#2 | hu_pan_wang_zhu_nber_w25817.txt | 1620 | found | script, L1620 |
| P-K9R-001-h | hu_pan_wang_zhu_nber_w25817.txt | 859 | found | verbatim L859-860 ("re- turns" is the source's line break) |
| P-K9R-002-a | giot_uclouvain.txt | 19 | found | script, L19 |
| P-K9R-002-c#1 | giot_uclouvain.txt | 613 | found | L613 "VIX larger than its 90% percentile (=28.98, N=413)" |
| P-K9R-002-c#2 | giot_uclouvain.txt | 614 | found | L614 "Mean 0.19 0.96 2.52 5.28" (first column read as the 1-day horizon; see "could not check") |
| P-K9R-002-c#3 | giot_uclouvain.txt | 615 | found | L615 "Std. 2.31 3.48 5.43 8.24" |
| P-K9R-003-b | simon_wiggins_2001_ideas.html | 33 | found | script, L97 |
| P-K9R-004-a | fassas_hourvouliades_2019_jrfm.txt | 494 | found | script, L496 |
| P-K9R-004-b | fassas_hourvouliades_2019_jrfm.txt | 500 | found | script, L502 |
| P-K9R-004-c | fassas_hourvouliades_2019_jrfm.txt | 523 | found | script, L523 |
| P-K9R-004-d | fassas_hourvouliades_2019_jrfm.txt | 547 | found | script, L547/548 |
| P-K9R-005-a | lubnau_todorova_2015_ideas.html | 33 | found | script, L97 |
| P-K9R-008-a | moreira_muir_nber_w22208.txt | 56 | found | script, L56 |
| P-K9R-012-a | sentana_wadhwani_1992_ideas.html | 33 | found | script, L97 |
| P-K9R-014-b (as logged, one piece) | bianco_corsi_reno_2009_pnas.txt | - | not found as one piece (as the catalog says) | removed by the writer; the two pieces are found (.1, .2) |
| P-K9C-001-a | savor_wilson_2013_draft.txt | 47 | found | script, L47 |
| P-K9C-002-a | ai_bansal_2018_econometrica.txt | 45 | found | L46-47 |
| P-K9C-003-a | ai_bansal_guo_2023_w31923.txt | 100 | found | script, L100 |
| P-K9C-003-b#1 | ai_bansal_guo_2023_w31923.txt | 122 | found | script, L124 |
| P-K9C-003-b#2 | ai_bansal_guo_2023_w31923.txt | 123 | found | script, L124 |
| P-K9C-003-b#3 | ai_bansal_guo_2023_w31923.txt | 124 | found | script, L124 |
| P-K9C-003-c | ai_bansal_guo_2023_w31923.txt | 131 | found | script, L131 |
| P-K9C-003-d | ai_bansal_guo_2023_w31923.txt | 110 | found | script, L110 |
| P-K9C-003-e | ai_bansal_guo_2023_w31923.txt | 141 | found | script, L141/143 |
| P-K9C-004-b | ernst_gilbert_hrdlicka_2021.txt | 163 | found | script, L163 |
| P-K9C-004-c#1 | ernst_gilbert_hrdlicka_2021.txt | 176 | found | script, L178 |
| P-K9C-004-c#2 | ernst_gilbert_hrdlicka_2021.txt | 178 | found | script, L178 |
| P-K9C-007-a | kurov_wolfe_gilbert_2020.txt | 19 | found | script, L21 |
| C-K9R-001-1 | hu_pan_wang_zhu_nber_w25817.txt | 1585 | found | script, L879/1585/1610 |
| C-K9R-001-2 | hu_pan_wang_zhu_nber_w25817.txt | 1569 | found | script, L1569/1600/1610 |
| C-K9R-001-3 | hu_pan_wang_zhu_nber_w25817.txt | 1626 | found | script, L1626 |
| C-K9R-001-4 | hu_pan_wang_zhu_nber_w25817.txt | 1601 | found | L1601 Table 7 column heads |
| C-K9R-001-5 | hu_pan_wang_zhu_nber_w25817.txt | 1602 | found | L1602 "(%)" |
| C-K9R-001-6 | hu_pan_wang_zhu_nber_w25817.txt | 1623 | found | script, L1623 |
| C-K9R-001-7 | hu_pan_wang_zhu_nber_w25817.txt | 1627 | found | script, L1627 |
| C-K9R-001-8 | hu_pan_wang_zhu_nber_w25817.txt | 1628 | found | script, L1628 |
| C-K9R-001-9 | hu_pan_wang_zhu_nber_w25817.txt | 1014 | found | script, L1014 |
| C-K9R-001-10 | hu_pan_wang_zhu_nber_w25817.txt | 878 | found | script, L879 |
| C-K9R-001-11 | hu_pan_wang_zhu_nber_w25817.txt | 1688 | found | script, L1688 |
| C-K9R-001-12 | hu_pan_wang_zhu_nber_w25817.txt | 2014 | found | script, L2014 |
| C-K9R-001-13 | hu_pan_wang_zhu_nber_w25817.txt | 2004 | found | script, L2004 |
| C-K9R-001-14 | hu_pan_wang_zhu_nber_w25817.txt | 1753 | found | L1753 (HVIX days defined with η = 0.3; evidence) |
| C-K9R-001-15 | hu_pan_wang_zhu_nber_w25817.txt | 1771 | found | script, L1771 |
| C-K9R-001-16 | hu_pan_wang_zhu_nber_w25817.txt | 1780 | found | L1780 "Obs 202 202 4814 4814" |
| C-K9R-001-17 | hu_pan_wang_zhu_nber_w25817.txt | 1004 | found | L1004 Table 2 "Non-Ann ... 4976" |
| C-K9R-001-18 | hu_pan_wang_zhu_nber_w25817.txt | 1572 | found | script, L1627 |
| C-K9R-001-19 | hu_pan_wang_zhu_nber_w25817.txt | 1606 | found | L1606 Table 7 row "3.0 7.7 42.70 2.46" |
| C-K9R-001-20 | hu_pan_wang_zhu_nber_w25817.txt | 291 | found | L291 (same text as P-K9R-001-b) |
| C-K9R-004-1 | fassas_hourvouliades_2019_jrfm.txt | 133 | found | script, L133/196/466 |
| C-K9R-004-2 | fassas_hourvouliades_2019_jrfm.txt | 134 | found | script, L135 |
| C-K9R-004-3 | fassas_hourvouliades_2019_jrfm.txt | 141 | found | script, L141 |
| C-K9R-004-4 | fassas_hourvouliades_2019_jrfm.txt | 147 | found | script, L147 |
| C-K9R-004-5 | fassas_hourvouliades_2019_jrfm.txt | 148 | found | script, L148 |
| C-K9R-004-6 | fassas_hourvouliades_2019_jrfm.txt | 152 | found | script, L152 |
| C-K9R-004-7 | fassas_hourvouliades_2019_jrfm.txt | 473 | found | script, L473 |
| C-K9R-004-8 | fassas_hourvouliades_2019_jrfm.txt | 596 | found | script, L596 |
| C-K9R-004-9 | fassas_hourvouliades_2019_jrfm.txt | 566 | found | L566 "D1 0.0237 **" |
| C-K9R-004-10 | fassas_hourvouliades_2019_jrfm.txt | 567 | found | L567 "D2 0.0050 **" |
| C-K9R-004-11 | fassas_hourvouliades_2019_jrfm.txt | 568 | found | L568 "D3 0.0005" |
| C-K9R-004-12 | fassas_hourvouliades_2019_jrfm.txt | 569 | found | L569 "D4 0.0000" |
| C-K9R-004-13 | fassas_hourvouliades_2019_jrfm.txt | 202 | found | L202 Table 1 std row "0.0166 0.0093" |
| C-K9R-004-14 | fassas_hourvouliades_2019_jrfm.txt | 135 | found | L135 "We set the beginning date of our sample in" (4 January 2010) |
| C-K9R-004-15 | fassas_hourvouliades_2019_jrfm.txt | 466 | found | script, L466 |
| C-K9R-004-16 | fassas_hourvouliades_2019_jrfm.txt | 523 | found | script, L523 |
| C-K9R-004-17 | fassas_hourvouliades_2019_jrfm.txt | 187 | found | L187 Table 1 mean row |
| C-K9R-004-18 | fassas_hourvouliades_2019_jrfm.txt | 471 | found | script, L471 |
| P-K9R-014-b.1 | bianco_corsi_reno_2009_pnas.txt | 96 | found | L96 "serial correlation has almost disappeared, the AR(1)" |
| P-K9R-014-b.2 | bianco_corsi_reno_2009_pnas.txt | 98 | found | L98-99 "coefficient of Rt being just −0.0276, whereas the mean value found by LeBaron in the period 1928–1990 was 0.0618" |
| C-K9C-001-1 | savor_wilson_2013_draft.txt | 664 | found | script, L664 |
| C-K9C-001-2 | savor_wilson_2013_draft.txt | 1713 | found | script, L1713 |
| C-K9C-003-1 | ai_bansal_guo_2023_w31923.txt | 127 | found | script, L127 |
| C-K9C-003-2 | ai_bansal_guo_2023_w31923.txt | 101 | found | script, L101 |
| C-K9R-001-21 | hu_pan_wang_zhu_nber_w25817.txt | 1600 | found | script, L1600/1610 |
| C-K9R-001-22 | hu_pan_wang_zhu_nber_w25817.txt | 1005 | found | L1005 Table 2 "All Days ... 5965" |
| C-K9R-001-23 | hu_pan_wang_zhu_nber_w25817.txt | 1610 | found | L1610 Table 7 row "1.0 39.7 10.34 2.01" |
| P-K9C-001-d | savor_wilson_2013_draft.txt | 794 | found | script, L794 |
| P-K9C-002-d | ai_bansal_2018_econometrica.txt | 251 | found | script, L252 |
| C-K9R-001-24 | hu_pan_wang_zhu_nber_w25817.txt | 1683 | found; the entry's gloss overstates it (R-04) | script L1683 |
| C-K9R-004-19 | fassas_hourvouliades_2019_jrfm.txt | 196 | found | script, L196 |
| RUL-1 | task4_lead_rulings.md | 28 | found | rulings L28-30 (X10 ruling), read in full |
| RUL-2 | task4_lead_rulings.md | 31 | found | rulings L31-33 (X14 ruling) |
| RUL-3 | task4_lead_rulings.md | 68 | found | rulings L68 |
| RUL-4 | task4_lead_rulings.md | 69 | found | rulings L69 |
| RUL-5 | task4_lead_rulings.md | 70 | found | rulings L70 |
| RUL-6 | task4_lead_rulings.md | 71 | found | rulings L71 |
| RUL-7 | task4_lead_rulings.md | 74 | found | rulings L74 |
| RUL-8 | task4_lead_rulings.md | 49 | found | rulings L49 |
| RUL-9 | task4_lead_rulings.md | 87 | found | rulings L87 |
| DT-1 | stage_e10_design_target.md | 121 | found | design target L121 |
| LOG-1 | stage_e10_research_regime.md | 190 | found | regime log L190-191 (reader's note on the X10 borderline) |
| D9-1 | STAGE_E_DESIGN.md | 510 | found | STAGE_E_DESIGN.md L510 (D9.5 news quotes) |
| D9-2 | STAGE_E_DESIGN.md | 506 | found | STAGE_E_DESIGN.md L506 (D9.4 prohibited patterns) |
| F9-1 | stage_e0_topstep_facts.json | 70 | found | topstep facts L70 "Payout eligibility 5 winning days of $150+" |
| F9-2 | stage_e0_topstep_facts.json | 71 | found | topstep facts L71 "Consistency = Largest Winning Day ÷ Total Net Profit" |
| K8-1 | stage_e0_catalog_K8.md | 97 | found | K8 catalog L97 Topstep hours |
| P-K9R-006-a | bansal_stivers_quantpedia_pointer.md | 44 | found | script, L44 |
| P-K9R-007-a | copeland_1999_ideas.html | 33 | found | script, L97 |
| P-K9R-007-a#2 | copeland_1999_ideas.html | 33 | found | script, L97 |
| C-K9R-001-25 | hu_pan_wang_zhu_nber_w25817.txt | 2032 | found | script, L2032 |
| C-K9R-001-26 | hu_pan_wang_zhu_nber_w25817.txt | 2029 | found | script, L2032 |
| CAL-BLS-1 | bls_empsit_archive_sget.html | 420 | found | script, L420 |
| CAL-BLS-2 | bls_cpi_archive_sget.html | 417 | found | CPI archive: "October 2025 Consumer Price Index – Not published because of 2025 lapse in federal government appropriations" |
| CAL-BLS-3 | bls_ppi_archive_sget.html | 421 | found | PPI archive: "October 2025 Producer Price Index– Not published because of 2025 lapse ..." |
| CAL-BLS-4 | bls_empsit_11202025.html | 422 | file present | embargo line not re-read; page in fetchlog.tsv with sha256; the archive file name empsit_11202025 carries the date |
| CAL-BLS-5 | bls_cpi_10242025.html | 400 | file present | as CAL-BLS-4 (cpi_10242025) |
| CAL-BLS-6 | bls_ppi_11252025.html | 397 | file present | as CAL-BLS-4 (ppi_11252025) |
| CAL-FED-1 | fed_fomccalendars.html | 1492 | found | 2025 panel parsed: May 6-7, Jun 17-18, Jul 29-30, Sep 16-17, Oct 28-29, Dec 9-10 (statement day = second day) |
| CAL-FED-2 | fed_fomccalendars.html | 1213 | found | 2026 panel parsed: Jan 27-28, Mar 17-18, Apr 28-29, Jun 16-17 |
| CAL-FED-3 | fed_fomccalendars.html | 1677 | found | 2025 panel: August "22 (notation vote)" |
| CAL-BEA-1 | bea_gdp_news_archive.html | 530 | found | script, L528 |
| CAL-BEA-2 | bea_gdp_news_archive.html | 528 | found | archive: "December 23, 2025 | Gross Domestic Product, 3rd Quarter 2025 (Initial Estimate)" |
| CAL-BEA-3 | bea_schedule_full.html | 377 | found | schedule: "February 20" precedes "GDP (Advance Estimate), 4th Quarter and Year 2025" |
| CAL-BEA-4 | bea_schedule_full.html | 417 | found | schedule: "April 9" precedes the Q4 2025 Third Estimate; "March 13" the Second |
| CAL-BEA-5 | bea_schedule_full.html | 492 | found | schedule: "June 25" precedes the Q1 2026 Third Estimate; "April 30" Advance, "May 28" Second |
| CAL-ISM-1 | ism_rob_calendar_fetch.html | 673 | found | script, L673 |
| CAL-ISM-2 | ism_rob_calendar_fetch.html | 733 | found | script, L673 |
| CAL-ISM-3 | ism_rob_calendar_wayback_20251009.html | 935 | found | 2025 table: Apr 1, May 1, Jun 2, Jul 1, Aug 1, Sep 2, Oct 1, Nov 3, Dec 1 |
Rows: 123. Found: 119 (of which 1 found but glossed beyond the source, C-K9R-001-24, R-04). Not found as one piece, as the catalog itself records: 1 (P-K9R-014-b). File present, embargo line not re-read: 3. Not re-checked: 0. No passage was fabricated; no table row was read under the wrong panel, column or sample (Table 7 η = 0 rows and panels, Table A1's 3:45 pm column, Table 8's left panel and Fassas Table 3's K = 1 day column were read in context).


## Design-draft check (docs/STAGE_E_DESIGN_K9_DRAFT.md)

- **K9-A (Holm).** 8 x 0.05 / 9 + 2 x 0.05 / 10 = 0.04444 + 0.01 = 0.0544; with seven non-empty, 0.0389 + 0.01
  = 0.0489; both reproduce. P(Z > 3.0) = 0.001350 and 0.05 / 37 = 0.001351, so "any K up to 37 is non-binding"
  holds by a margin of one part in a thousand (0.05 / 38 = 0.001316 would bind); 0.05 / 18 = 0.00278. The
  draft rightly says the count of non-empty Tier A clusters is not re-read. Consistent with the design target.
- **K9-B (minimum trade count).** 30 / 299 = 10.0%; 0.40 x 299 = 119.6; 1 / sqrt(30) = 0.183, 1 / sqrt(120) =
  0.091; t = sqrt(n / (n - 1)) for one positive day. "K9-anncday-01 meets the margin (about 55-57 trips)" and
  "K9-vixspike-01 ... expects about 37-40" match the catalog (56.8 / 54.9 and 39.7 / 38.4, 37.8 / 36.7). The
  0.5-cutoff alternative (R-05) is absent.
- **K9-C (budget and N).** sqrt(2 ln 198) = 3.252 and sqrt(2 ln 238) = 3.308 reproduce; 198 + 40 = 238.
- **K9-D (eps reading).** Restates design target (a) reading 2 (0.32-1.03 x E|m_1| at two a week, 0.60-1.96 x
  at one a week: the table's G(0.4) and G(0.2) over E|m_1| columns run 0.32-1.03 and 0.60-1.96). Consistent.
- **K9-E (purchases).** The holdout-2 inventory is from the start checks, not a result; the K1 quote figure
  ($22.11-22.53) is from D13. Not re-verified here (outside the brief's files).
- **K9-F (the catalog in one table).** Mechanisms, conditions, holds, exposures, trip ranges, labels and the
  6-of-40 count match the catalog after round 2. "18:00 fill" is printed as a fact (R-06).
- **K9-G (decisions for the user).** Lists the (b)1 waiver, the floor, Holm K, the budget, the eps reading, the
  exposures and the reinstatement of K9-vixback-01. Missing: the D-entry amendment (R-06), the cutoff
  alternative (R-05), the E-H1 ruling (R-02), the K9R-006 handling (R-03); and the JFE re-check item can be
  closed (R-11).
- The (b)1 shortfall is stated honestly in the catalog (Status, section 6), the rulings (round 2 item 1) and
  the draft (K9-B, K9-G.1), and the lead did not relax (b)1 after reading sources. R-05 records that the lead's
  own cutoff choice, not the source, produced the shortfall.

## What this review could not check

- The announcement dates of the rescheduled BLS releases (R-07) and ISM's actual release dates (the catalog's
  own [unverified] flag): no saved page carries them.
- CBOE's VIX close publication time relative to the 17:59 CT intent, and a free intraday VIX history for the
  3:45 pm ET fallback (the catalog's Q18): routed to E.12 by the catalog; not checked here.
- Giot's Table (P-K9R-002-c): the cells "Mean 0.19" and "Std. 2.31" are the first column of the "VIX larger than
  its 90% percentile (=28.98, N=413)" block (giot_uclouvain.txt lines 613-616); that the first column is the
  one-day horizon is read from the increasing pattern across columns (0.19, 0.96, 2.52, 5.28), not from a
  header line in the saved text.
- Appendix A's evidence-only rows C-K9R-004-13, -14, -17 and LOG-1 were not re-checked individually (withdrawn
  draft; the brief limits Appendix A to its withdrawal reasons).
- The typeset JFE article itself (paywalled); the author manuscript stands in (R-11).
