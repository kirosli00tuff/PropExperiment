# Stage E.13 Task 6: adversarial review of the ranking and the pre-registration drafts

Reviewer: RankingReviewer-FableXHigh (worker-xhigh, fable), 2026-10-03. I wrote none of the files reviewed. Brief:
reports/stage_e13_briefs/brief_rankingreviewer.md. Helper folder (script and full recomputation table):
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/dbc7460b-72c3-4537-8327-d14819b62f5c/scratchpad/RankingReviewer/
(recompute.py, recompute_table.md). No market data of any window was read; no Databento call, no web fetch, no
contact with any firm, no commit, no agent spawned. Quotes were checked against the saved raw pages under
reports/stage_e13_briefs/pages/ by grep (whitespace-tolerant where the saved text wraps).

## Verdict

**BLOCK** (one BLOCKING finding, R-01, on how the ranking rule was applied to the top two; it is resolvable by a
single lead ruling and does not require new research). Counts: BLOCKING 1, SHOULD FIX 7, NOTE 8.

Everything numerical holds: of 161 recomputed quantities, every load-bearing one agrees (C1 and C2 income, C2
power and cost bar, the NG prior, Bayes factors, power table, odds and joint false-pass rate, the purchase and
top-up arithmetic, the trend/carry IDM, targets, portfolio sigma, income and expected maximum drawdown, and the
Part D ruin bounds including the D/27 rule by my own Monte Carlo). The disagreements are labels and conventions
(R-03, R-07, R-08). The NG draft cannot see its test data (check 5 passes). The venue classifications match
their quotes, stale captures are declared as such, and the Scrapling deviations are the workers' own disclosures.

## Findings

### R-01 BLOCKING. The top-two order rests on a tie criterion that section 1 does not contain

- File and line: reports/stage_e13_ranking.md section 1 (lines 16-22), section 3 rows "Lead's odds (a)" and
  "(b)" (lines 66-67), section 5 lines 99-100 and 102-115, the "Ease check" (130-133) and the process note
  (135-138); reports/stage_e13_STATE.md 23:21 entry (lines 85-88).
- What is wrong: section 1 fixes the primary key as "the lead's odds" and gives tie-breaks, but defines no tie.
  The lead's own odds favor C1 over C2 on both measures and at every point of the stated ranges: (a) 12% (7-35%)
  against "about 10% (5-20%)", and (b) "about 4%" against "about 3%". Section 5 then declares the two "tied on
  the primary key" because the ranges overlap, and the first tie-break (published evidence) moves C2 to first.
  "Ranges overlap means a tie" is a criterion introduced after scoring. Applied as written, section 1 ranks C1
  first; the first version of the file (STATE, sha256 prefix e4106799b2781972) had C1 first. The reordered
  result is also the cheaper candidate ($10 against $59 plus a $41 top-up; 2.5-3 sessions against 3.5-4), which
  is exactly the silent failure the stage prompt names ("a ranking that favors what is easy over what has
  evidence"). The ease check's claim that "C2 would stay first if it cost as much as C1" is true only under the
  undeclared tie.
- Compounding: C2's odds are asserted, not derived. C1's (b) is computed (0.12 x [0.5-0.8] x 0.5 = 3.0-4.8%); C2's
  (a) "about 10%" and (b) "about 3%" have no arithmetic behind them in sections 3-5. The primary key for the
  candidate placed first is therefore the least supported number in the table. (R-02 shows the power input to
  those odds is also mis-stated.)
- Evidence: the four odds cells as quoted; section 1 verbatim has no tie definition; recompute_table.md rows
  "combined pass odds" and the C1 (b) derivation.
- Fix proposed (a lead ruling, either branch acceptable; the user should see which was taken):
  (i) apply section 1 as written: C1 first, C2 second, recommendation adjusted (C1 with the calendar probe, C2 as
  the companion), with the process note rewritten accordingly; or
  (ii) amend section 1 with an explicit tie criterion (for example: odds whose stated ranges overlap are tied),
  mark the amendment as made after scoring and after the first version, and derive C2's (a) and (b) the way
  C1's are derived (P(effect present in 2011-2019 at the program's cost) x power, with the power from R-02's
  sourced share), so that the primary key is a computed number for both candidates. If the derived C2 odds then
  exceed C1's, the order follows without any tie-break and the finding is closed.

### R-02 SHOULD FIX. The negative-gamma share is marked UNSOURCED, but the saved Baltussen paper reports it

- File and line: reports/stage_e13_ranking.md section 3 "Power" row (line 64) and section 4 "C2 power" (77-82);
  reports/stage_e13_prereg_gexmom.md section 7 (86-91) and section 9 step 3; reports/stage_e13_info_sources.md
  2.7(a) "share UNSOURCED" (line 269) and section 3 (line 345).
- What is wrong: reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md states: "In the period from
  1996 until May 2020 there have been 2930 days with a negative NGE and 3158 with a positive one." That is a share
  of 0.481 for the paper's own NGE measure. The ranking's power row assumes 0.10-0.30 and calls the share
  UNSOURCED; the prereg's minimum-power stop (200 dates) is calibrated on that assumption. At 0.48 the expected
  T1 count is about 920 of 1,913 dates, and power at the 0.025 bar is 0.33 / 0.86 / 0.995 at a per-trade Sharpe
  of 0.05 / 0.10 / 0.15 (my arithmetic, same formula as the ranking's). This feeds C2's odds, the primary key
  (R-01).
- Caveat the fix must keep: the paper's NGE (OptionMetrics construction to 2017, SqueezeMetrics to 2020) is not
  the SqueezeMetrics GEX column the prereg will read, whose sign distribution may differ; the prereg's count
  step (section 9 step 3) still decides the realized share. But a sourced reference point exists and should
  replace "UNSOURCED" in the ranking and the prereg, with the 48% figure and its caveat.
- Fix: cite the quote (I-37b, page on disk) in INF 2.7(a), the ranking's power row and prereg section 7; add a
  power line at share 0.48; reconsider the 200-date stop in that light (at 0.48 the window would give about 920
  dates, so the stop is far from binding, which is itself worth stating).

### R-03 SHOULD FIX. C2 income: "$13-$31 net per MES per trade" is the figure for two MES

- File and line: reports/stage_e13_ranking.md section 4 "C2 income if real" (lines 89-91).
- What is wrong: gross per-trade Sharpe 0.10-0.20 on a $91 half-hour sigma is $9.1-$18.2 gross; less $2.55 of
  cost is $6.5-$15.6 net per MES per trade. $13-$31 is two MES. The monthly figures that follow ($55-$131 on a
  50K with two MES, $109-$261 on a 150K with four) are correct, so the label, not the result, is wrong.
- Evidence: recompute_table.md rows "C2 net $/trade per MES" and "C2 $/month".
- Fix: write "$6.5-$15.6 net per MES per trade ($13-$31 for the two MES of a 50K)".

### R-04 SHOULD FIX. The NG pre-registration names only half of the V24 question

- File and line: reports/stage_e13_prereg_ngrepl.md section 10 item 1 (lines 123-124); annex
  reports/stage_e13_ng_replication_draft.md section 4 "V24 question for the user" (lines 148-151).
- What is wrong: the prereg asks the user only whether E.12's persisted out-of-fold predictions may be reloaded to
  fix q, and says "it is not a refit". The annex says more: "The M1 fit is also a computation on the 2019-2024
  panel, though the stage prompt itself prescribes it. V24 rules out 're-mining the 2019-2024 stores', so the
  user should confirm both before the freeze." M1 is a new full-panel ridge fit that Gate 0 never ran (Gate 0 used
  15 CPCV split fits). The user decision in the prereg therefore understates what V24 is being asked to allow.
- Fix: item 1 of section 10 names both computations on the 2019-2024 panel: (a) the reload of the persisted OOF
  predictions to reproduce q, and (b) the single full-panel fit of M1 on the E.12 training panel; both are
  reads of already-bought training data, neither is a rerun of Gate 0's decision, and the user confirms both.

### R-05 SHOULD FIX. The C2 evidence cell describes the unconditional result; C2 tests the conditional one

- File and line: reports/stage_e13_ranking.md section 3 "Evidence and strength" for C2 (line 59) and section 5
  item 1 (lines 102-103): "peer-reviewed, intraday, on-instrument, 60+ futures, 1974-2020".
- What is wrong: the 60+ futures, 1974-2020 result is the unconditional rest-of-day to last-half-hour effect. The
  gamma-conditioned result that C2 tests is for one index (S&P 500) over 1996 to May 2020, Tables 7-8 of the paper
  (saved page: "we compute the NGE measure from 1996 until the end of 2017. We use data from SqueezeMetrics to
  extend the sample until May 2020"; "intraday momentum is much more pronounced on negative NGE days"). The
  cell that decides the first tie-break overstates the breadth of the evidence for the hypothesis actually
  proposed. Peer-reviewed evidence on one index over 24 years still outranks the program's own best-of-81 result
  under the lead's tie-break, so this does not by itself reverse the tie-break; it changes how strong "the
  best published evidence on the list" is read, which the prompt asks to be read at post-publication strength.
- Fix: split the cell: unconditional (60+ futures, 1974-2020, both subsamples 1974-1999 and 2000-2020 similar per
  the paper's section 3.4); conditional on NGE (S&P only, 1996-2020, in-sample); post-publication record for
  the conditional form: none retrieved (I-39 is second-hand and concerns the unconditional form).

### R-06 SHOULD FIX. The C5 cost cell mislabels an activation fee as an evaluation fee and omits an UNSOURCED mark

- File and line: reports/stage_e13_ranking.md section 3 "Data cost and top-up" for C5 (line 62): "evaluation fees
  ($149-$169 Phidias Premium, P2-01/P2-02)"; reports/stage_e13_venues.md prop-firm table, Phidias rows, "Lifetime
  $149 / $149 / $169 [P2-01]".
- What is wrong: the saved TOU (pages/PropVenues2/phidias_tou.txt) reads "Activation Fee $83 $149 $149 $169" and
  the rules page reads "Premium 150K — Activation Fee $169". Neither page uses "evaluation fee" or "lifetime".
  VEN part 2 gaps (line 620-621) say the monthly evaluation price "sits in a JS configurator and is UNSOURCED".
  So the ranking cites a sourced number under the wrong name and leaves the actual evaluation price unmarked.
  C5 ranks last on the drawdown arithmetic, so the rank is unaffected.
- Fix: "activation fee $149-$169 (TOU, P2-01); evaluation price UNSOURCED (VEN part 2 gaps)"; the same relabel in
  the VEN table.

### R-07 SHOULD FIX. C2 pre-registration: no rule for calendar dates that cannot be sourced, and one sentence that reopens the cost

- File and line: reports/stage_e13_prereg_gexmom.md section 3 "Eligible date" (lines 42-46) and section 4;
  reports/stage_e13_ranking.md section 4 "C2 cost bar" last sentence (line 88).
- What is wrong (free-parameter audit, check 6): the rule fixes the window, signal, timing, entry and exit bars,
  cost, bar, exclusions and stop rule. Two openings remain. (a) Eligibility depends on "the 2011-2019 equity
  calendar built from official pages"; the C1 annex (section 2 and ruling C12) shows that 2010-2013 official
  pages may be unavailable at evidence grade, and C1 has a fixed rule (exclude the date, count it, stop above 2%).
  C2 has none, so the next stage could decide how to treat unsourced early-close or holiday dates after the
  purchase. (b) The ranking says "the next stage computes c from D8 on the test rows", while the prereg fixes c
  = 2.038 ticks for every trade. D8's bucket depends on the CT minute only and both minutes are fixed, so the two
  statements coincide in practice, but the prereg should be the only statement.
  Everything else I looked for is closed: the GEX timing branch (d-1 row, or d-2 if SqueezeMetrics documents late
  publication) is decided from documentation before any price and defaults to d-1; a date without a GEX row is
  excluded and counted (section 3); the T1-over-T2 comparison is a point comparison; the count in step 3 reads
  signs only, and the 200-date stop is fixed.
- Fix: copy ruling C12's exclusion-and-2%-stop rule into prereg section 3; delete or reword the ranking's
  sentence so c is "fixed at 2.038 MES ticks (prereg section 4)".

### R-08 SHOULD FIX. The STATE and process note cite a first-version hash that cannot be checked

- File and line: reports/stage_e13_STATE.md lines 80-81 and 85-88; reports/stage_e13_ranking.md lines 135-138.
- What is wrong: the superseded first version of the ranking (C1 first) is recorded only as a 16-hex-character
  prefix, and no copy exists on disk. The process note therefore documents the reordering but gives the reviewer
  nothing to verify it against, which matters because the reordering is the subject of R-01.
- Fix: record full sha256 values in STATE, and keep superseded versions of a ranking or pre-registration draft on
  disk (for example reports/stage_e13_briefs/ranking_v1.md) so the change can be diffed.

### R-09 NOTE. "Index levels near a third of today's" does not give 0.11 sigma

- File and line: reports/stage_e13_ranking.md section 4 "C2 cost bar" (lines 83-88); prereg section 7 (89-91).
- Recomputation: cost / half-hour sigma today = 2.55 / 91.1 = 0.028 (agrees). At one third of today's level it is
  0.084, not 0.11; 0.11 corresponds to about 27% of today's level (an S&P mean near 2,100 over 2011-05..2019-04,
  my figure, unsourced like the lead's). The 1.5c bar is then 0.13-0.17 sigma. The approximation also keeps
  today's 10.7% volatility; 2011-2019 realized volatility was higher, which lowers the ratio. None of this
  changes a rank; it is a labelled lead approximation.
- Fix: state the index level used and give the ratio as a range (about 0.08-0.11 sigma; bar about 0.13-0.17).

### R-10 NOTE. AiTrader date arithmetic depends on an unstated day-count convention

- File and line: reports/stage_e13_ranking.md section 4 "AIT dates" (lines 92-94).
- Recomputation: 15 NYSE trading days after 2026-10-02 is 2026-10-23 (agrees; assumes the 45-cluster count
  includes the 2026-10-02 session and one cluster per trading day, Columbus Day not being an NYSE holiday). The
  120th trading day is 2027-01-15 only if 2026-07-28 counts as day 1; counting it as day 0 gives 2027-01-19.
  The 45-cluster figure is confirmed by the AiTrader commit message (0eda3cd: "recorded at 45 clusters").
- Fix: write "counting 2026-07-28 as day 1".

### R-11 NOTE. Scrapling-before-terms deviations: what the logs show, and one undeclared fetch-order deviation

- Files: reports/stage_e13_briefs/pages/*/fetch_log.md and DO_NOT_COMMIT.txt; reports/stage_e13_venues.md
  section 5; reports/stage_e13_STATE.md ("three workers").
- What the logs show: PropVenues1 used Scrapling on help.tradeify.co (one get, six fetch: rows 31-38) and on
  elitetraderfunding.com (two fetch: rows 67-68) before reading terms that forbid robots; PropVenues2 used it on
  lucidtrading.com (three files) before reading a TOU that bans automatic devices. Both workers disclosed this in
  their reports and listed the files in DO_NOT_COMMIT.txt. InfoSource's Scrapling get on the Insper repository
  followed a robots refusal with no terms found (within the rule as written). BrokerVenues' Scrapling fetch of
  two NinjaTrader support articles followed a documented, unsuccessful search for terms (compliant). So I count
  two workers with terms-breaking Scrapling fetches, not three. Separately, InfoSource fetched the Baltussen PDF
  (I-37b) by Firecrawl directly after a curl 403, skipping the Scrapling step that research_rules.md step 4
  requires before Firecrawl; this is not declared in INF section 3.
- Which ranking facts rest on those pages: the Tradeify pricing, drawdown and restricted-country facts (Tradeify
  is NOT PERMITTED on the overnight rule, corroborated by Wayback copies); the Lucid TOU (Lucid is NOT PERMITTED
  on the overnight rule from a curl-fetched help page); and ETF's terms, which supply the "automated
  decision-making systems" definition quoted in the ranking's C5 cell and in reports/stage_e13_phidias_question.md
  section 4. C5's rank does not depend on them.
- Fix: the lead rules whether a fact from a deviating fetch may stand as a source (my view: yes when a compliant
  copy corroborates it, otherwise mark it "[deviation fetch]"), corrects "three workers" to the count above, and
  INF section 3 records the Firecrawl order deviation.

### R-12 NOTE. The NG prereg's C10 stop reads 2010-2019 bars before the evaluation; say what a stop ends

- File and line: reports/stage_e13_prereg_ngrepl.md section 3 last bullet (56-57) and section 9 step 5; annex
  ruling C10.
- What: the applicable-row counts are computed from the replication features, so they read the test bars (values
  not printed). The stop rule is fixed in advance, which is right, but the draft does not say whether a stop ends
  the registered attempt or allows a calendar fix and a restart. A restart after a fix is a second pass over the
  data with a changed input.
- Fix: one sentence: a C10 stop closes the attempt; any calendar correction and rerun is a new registration with
  N counted again, or, if the lead prefers, is allowed once with the fix confined to calendars, logged, and with
  M1, q and the window byte-identical.

### R-13 NOTE. Power figures use the 8.90-year span of the superseded window

- File and line: reports/stage_e13_prereg_ngrepl.md section 7 (86-90); annex section 9.
- Recomputation: expected t 3.41 (h60) and 3.17 (hF), power 0.93/0.40/0.13/0.025 and 0.88/0.29/0.08/0.012 with the
  cost bar all reproduce for 8.90 years. The ruled window (2010-06-07..2019-04-30 with rows from about January
  2011) is about 8.3 years; the prereg says so and gives the 0.97 scale factor, which puts expected t at 3.29 and
  full-effect power at about 0.91. Declared; fine. Stated here so the ranking's "0.93" is read as the upper figure.

### R-14 NOTE. The 12% headline for C1 is the midpoint of two computed cases

- File and line: reports/stage_e13_ng_replication_draft.md section 9 (420-429) and the lead rulings note (479-481).
- Recomputation: central 0.22 x 0.61 + 0.78 x 0.04 = 0.165; skeptical 0.12 x 0.30 + 0.88 x 0.04 = 0.071; midpoint
  0.118. The optimistic 0.35 reproduces only with the uniform-prior Bayes factor (P(real) 0.42 at a per-pair prior
  of 0.05, giving 0.34-0.42); with the half-normal factor it is 0.22-0.27. The prior is stated honestly: 0.396
  and 0.502 reproduce, the simulated 0.388 and expected maximum 2.43 reproduce, the Bayes factors 6.6 and 13.9
  and the posterior mean 1.3 reproduce, and the regime-change quotes (R06, R10, R19) are on disk. The designer's
  own central case is 0.165; the lead's note explains the lower headline. Fine as stated.

### R-15 NOTE. Minor citation slips

- reports/stage_e13_ranking.md line 73 cites "E.12_RETURN.md lines 10-11" for "518 trades in 4.82 years"; the 4.82
  years is the annex's arithmetic (2019-05-06..2024-02-29 = 4.82, reproduced), not in E.12_RETURN.md.
- Ranking line 62: the ES data cost for C2 is an ESTIMATE from E.0's quote (9.197823 x 96/86 = 10.27, reproduced);
  the stage prompt allowed a quote-only run only for Task 4 figures, so the lead rightly did not quote ES. Cost
  never moves a rank; the label is correct.
- Ranking line 91: "50 trades a year" at share 0.20 is 47.9 (1,913 / 7.99 x 0.20); rounding.

### R-16 NOTE. Things I looked for and did not find wrong

- Venue classifications against their quotes: Topstep NOT PERMITTED ("All positions must be closed by 3:10 PM CT",
  ts_hours), Phidias HUMAN-IN-THE-LOOP (TOU clause verbatim on disk; rules page "Overnight and weekend holds
  allowed"; "17 E-mini / 170 micro"), ETF UNCLEAR ("automated decision-making systems" in etf_terms; "swing trading
  permitted" and "able to hold trades through close, and the weekend" in the plan pages), The Trading Pit Classic
  PERMITTED Mon-Thu ("not over the weekend"; "we allow you to trade using your own Expert Advisor (EA)"; the
  current sales page has no "Classic" string, so the UNCLEAR caveat is right), IBKR Canada PERMITTED ("Account
  Minimums | USD 0.00"; MES overnight initial 3704.55; CIRO membership; API minimum "USD 0.00 per month"), AMP
  UNCLEAR ("discretion of a senior manager", Wayback 2025-09-11, declared).
- Stale pages: Apex (Wayback Feb-Sep 2026), Tradeify (Wayback June 2026 against current), AMP commissions (2019)
  are all declared as such in VEN section 5 and in the table cells. None is presented as current.
- Post-publication reading (check 3): trend (SG Trend 0.24 net 2010-2025, 0.30 2013-2025; AQR TSMOM 0.31 gross
  2012-2025, t 1.18 reproduced), carry (-0.19 gross 2013-2025, T-11 quote found inside the saved xlsx), GFS
  (one 2025 paper, no record), and the NG near-miss (own, selected, best of 81) are all read at post-publication
  strength. GEX: see R-05.
- Order of events and leakage (check 5): rulings C5 (fixed start, no volume read) and C6 (no May-2019 splice)
  remove the two data reads the designer had proposed; C9 hashes M1 and q before any purchase; calendars come
  from official pages; the threshold rule matches ml_route_v2/gate0.py `_top_trades` (floor(0.2 x n) over all
  pair rows, among non-zero predictions, stable sort) and `_b_test`; the only pre-evaluation reads of 2010-2019
  data are the feature build and the C10 counts (R-12). No path by which 2010-2019 information reaches M1, q, the
  window or an exclusion rule was found.
- Ease check: C3 (strongest long-run evidence) ranks third on income odds under 2%, consistent with the rule;
  C4 and C5 rank on evidence and fit. Only the C1/C2 order is affected by R-01.

## Numbers recomputed

The full table (161 rows) follows at the end of this file, generated by recompute.py. Summary by block:

| Block | Rows | Disagree | What disagrees |
|---|---|---|---|
| Ranking section 4: C1 income, C2 power, C2 cost bar, C2 income, AIT dates, combined odds | 36 | 5 | the two "per MES" labels (R-03); "a third" ratio (R-09, 2 rows); 120th-day convention (R-10); 50 vs 47.9 trades (R-15) |
| NG draft: prior, Bayes factors, posterior mean, power table (t bar and 1.5c bar), expected trades, odds, joint false pass, spans | 40 | 0 | (optimistic 0.35 reproduces with the uniform-prior BF only; noted R-14) |
| Purchase and top-up from reports/stage_e12_quotes_ext2010.json (per_contract usd, quoted/failed chunks, headroom) and the ES estimate | 29 | 0 | |
| Trend/carry: IDM(N) for 7 N, targets at 5 capital levels, portfolio sigma and cost at $10K and $50K, net S, E[$/month], E[MDD] 5y/10y by Monte Carlo (20,000 paths), closed-form check 2.74 vs 2.80 | 24 | 0 | |
| Part D ruin: closed forms (infinite fixed, one-year fixed), 10%-ruin bounds, EOD and intraday trailing by Monte Carlo at D/27.2, D/29.0, D/25.5 and three grid cells, set B and set D sigmas, D/27 at $2,500 and $4,500 | 24 | 0 | |
| Other (years to t = 3, GFS and GEX t-arithmetic, AQR TSMOM t) | 8 | 1 | 0.109 printed as 0.11 (rounding) |

Key agreements, file value then mine: C1 $345 / $96 / -$3.21 (345.3 / 96.0 / -3.21); C2 power at share 0.20:
0.16 / 0.50 / 0.83 (0.16 / 0.50 / 0.83); MES RT 2.04 ticks = $2.55 (2.038, $2.55); 1.5c = 3.057 ticks (3.057);
P(best of 81) 0.396 (0.396), Bonferroni 0.502 (0.502); expected t 3.41 / 3.17 (3.41 / 3.17); power 0.93 / 0.40 /
0.13 / 0.025 (0.926 / 0.399 / 0.134 / 0.025); with the 1.5c bar 0.88 / 0.29 / 0.08 / 0.012 (0.877 / 0.294 / 0.081 /
0.012); BF 6.6 / 13.9 (6.57 / 13.9); posterior mean 1.3 (1.32); P(real) 0.12-0.22 (0.119-0.221); central 0.165
(0.1654), skeptical 0.07 (0.0712); P(at least one false pass) 0.045 / 0.041 at rho 0.5 / 0.7 (0.0445 / 0.0405);
joint 0.018 (0.0178); quoted total 57.314736 (57.314736), x1.03 59.034178, top-up 40.963908 and 37.634486 (all
exact), 106 quoted and 6 failed chunks per root (exact); ES 10.27 / 10.58 (10.27 / 10.58); IDM 2.21 / 2.38 / 2.42
/ 2.48 (2.211 / 2.380 / 2.418 / 2.477); $10K sigma 3,104 (3,103), $50K 11,824 (11,805); E[$/month] 40 / 189 (40 /
188); E[MDD] 10y $10K 10,303 (10,204), $50K 37,990 (37,961); driftless 5y 2.74 sigma (2.74) against 2.80 closed
form (2.802); one-year fixed 0.430 (0.430) and 0.235 (0.234); EOD trailing ruin at D/27.2, S 0.30: 0.097 (bound
holds); grid S 0.30, D $2,000, set D: 0.64 / 0.36 / 0.63 / 0.64 (0.639 / 0.358 / 0.628 / 0.642); set B sigma
2,432 (2,431), set D 169 (169).

## Spot-checks made

### Ranking-table facts traced to cited lines (19)

| # | Fact in the ranking | Cited source | Outcome |
|---|---|---|---|
| 1 | NG h60 5.569 / 1.713 / t 2.51 / 518; hF 13.921 / 1.766 / 2.33 / 494 | E.12_RETURN.md lines 548-549 | matches |
| 2 | $57.31 for 106 chunks, x1.03 = $59.03, top-up $40.96; 2010-01..06 unpriced | stage_e12_quotes_ext2010.json per_contract | matches exactly (sum of NG, ZC, NQ, ZN, 6E, GC; quoted 106, failed 6 each) |
| 3 | Funds $1.61 / $18.07 | same JSON (accounts) and E.12_RETURN.md 572 | matches |
| 4 | MES tick $1.25 | rules/products.py:154 | matches ("0.25", "1.25") |
| 5 | MES D8 rows 14:30 (0.5191) and 15:00 (0.5428); early-era bias | reports/stage_e2a_costs.md 200-201, 100 | matches |
| 6 | E.0 ES quote $9.197823 for 86 months | reports/stage_e0_quotes.json | matches (9.197822958, months_quoted 86) |
| 7 | S&P exposure closed, D1 rule 5 | docs/STAGE_E_DESIGN.md:46 | matches |
| 8 | GEX CSV from 2011-05-02; GEX definition; platform terms | INF I-47, I-40, I-48 | I-40 and I-48 on disk; I-47 header only, not saved (declared) |
| 9 | SG Trend 0.24 / 0.30 net, DD -20.6%; TSMOM 0.31 gross (t 1.18); carry -0.19 | TC summary and evidence table | matches |
| 10 | IBKR margins: micros $136-$919, MES $3,705, MNQ $7,359, MGC $3,788 | VEN margin table (B-06) | matches (MCD 136.283 to 2YY 918.619; 3,704.55; 7,359.31; 3,788.37) |
| 11 | IBKR USD 0 minimum, API, CIRO | VEN lead summary; B-08, B-09, B-02 | matches |
| 12 | C3 income $40 / $89 / $189 / $428; E[MDD] 76-103% | TC C3 sizing table | matches |
| 13 | D/27 rule; set sigmas $169-$2,432 | TC Part D | matches (bounds D/29.0, D/27.2, D/25.5) |
| 14 | Phidias Premium "evaluation fees $149-$169" | P2-01 / P2-02 | source says "Activation Fee"; evaluation price UNSOURCED (R-06) |
| 15 | AiTrader 45 clusters on 2026-10-02, commit 0eda3cd; exit gate; 120-day hard stop | ../AiTrader git log; docs/STAGES.md 19-24 | matches |
| 16 | Roll blackout = splice date plus two prior group trade dates | data/stage_e_bars.py:30-33 | matches |
| 17 | Gate 0 threshold: floor(0.20 x n) largest abs r_hat among non-zero, stable | ml_route_v2/gate0.py:301-306 | matches |
| 18 | V24: re-mining the 2019-2024 stores ruled out | docs/DECISIONS.md 446-467 | matches |
| 19 | Databento GLBX.MDP3 start 2010-06-06; ledger error text | pages/ReplicationDesigner/databento_glbx_mdp3.html; ledger/databento_spend.jsonl | matches (162 such ledger lines; NG 2010-01 line read) |

### Quotes grepped in the saved raw pages (32)

| Key | Quoted words | Saved file | Outcome |
|---|---|---|---|
| I-37b | "market intraday momentum is present for the index when NGE is negative and becomes stronger when NGE becomes more negative" | InfoSource/baltussen_etal_2021_jfe.md | found (line-wrapped) |
| I-37b | "do not consider transaction costs"; "December 1974 to May 2020"; "from 1996 until the end of 2017"; "Sharpe ratios between" | same | found |
| I-37b | "2930 days with a negative NGE and 3158 with a positive one" | same | found; not used by INF, ranking or prereg (R-02) |
| I-37b | ROD definition "from previous market close to the last 30 minutes" | same | found; matches the C2 signal definition |
| I-40 | "dollar-denominated measure of option market-makers' hedging obligations" | InfoSource/squeezemetrics_dix.html | found |
| I-48 | "creating user accounts by automated means" | InfoSource/squeezemetrics_terms.html | found |
| I-39 | "analyzes additional data post2013, noting a decline" | InfoSource/unisg_intraday_mom.pdf.txt | found |
| I-30 | "26Feb2021-Present" | InfoSource/ncei_gfs.html | found |
| T-17 | "risk target of 25%" | TrendCarry/carver_2020_03_how-much-risk-should-we-take.html | found |
| T-04 | "Sharpe ratio of 0.05" | TrendCarry/aqr_cant_always_trend_jpm.txt | found |
| T-11 | "gross of trading costs and fees" | TrendCarry/aqr_century_factor_premia_monthly.xlsx (sharedStrings) | found |
| T-22 | "Minimum capital report produced on 02/10/2026" | TrendCarry/carver_reports_Minimum_capital_report.txt | found |
| T-24 | "RISK_TARGET_ASSUMED = 25" | TrendCarry/pysystemtrade_reporting_constants.py.txt | found |
| T-05 | "SG Trend Index" | TrendCarry/sg_indices.html, ttu_apr2023.* (the MFMF.xls itself not parsed) | found in the SG pages |
| R01 | "2010-06-06" | ReplicationDesigner/databento_glbx_mdp3.html | found |
| R19 | "February 24, 2016" | ReplicationDesigner/eia_tie_67224_sabine_pass_10yrs.html | found |
| R10 | "averaged 69% in 2023 compared with 91%"; "most volatile since at least 1994" | ReplicationDesigner/eia_tie_62203_calmed_after_2022.html | found |
| R06 | "37,652,438" | ReplicationDesigner/eia_dry_production_annual.html | found |
| P1-01 | "All positions must be closed by 3:10 PM CT" | PropVenues1/ts_hours.txt | found |
| P1-37 | "automated decision-making systems" | PropVenues1/etf_terms.txt (Scrapling fetch; R-11) | found |
| P1-33, P1-34 | "swing trading permitted"; "able to hold trades through close, and the weekend" | PropVenues1/etf_how_the_dtf_plan_works.txt, etf_diamond.txt (curl) | found |
| P2-01 | "semi-automated software, provided the User actively monitors and manually adjusts all operations" | PropVenues2/phidias_tou.txt | found |
| P2-01 | fee line | same | reads "Activation Fee $83 $149 $149 $169" (R-06) |
| P2-02 | "Overnight and weekend holds allowed"; "17 E-mini / 170 micro" | PropVenues2/phidias_rules.txt | found |
| P2-95 | "not over the weekend" | PropVenues2/ttp_can-i-leave-positions-open-overnight-in-futures-challenges.txt | found |
| P2-96 | "we allow you to trade using your own Expert Advisor (EA)" | PropVenues2/ttp_can-i-use-an-expert-advisor-0-0.txt | found |
| P2-109 | Classic absent from the sales page | PropVenues2/ttp_futures_sales.txt | 0 occurrences of "Classic", 4 of "Prime" |
| B-06 | "3704.55" | BrokerVenues/ibkrca_margin_fut_ca_us.html | found |
| B-08 | "Account Minimums \| USD 0.00"; "USD 0.00 per month minimum commission" | BrokerVenues/ibkrca_minimums.html.txt | found |
| B-02 | "Canadian Investment Regulatory Organization" | BrokerVenues/ibkrca_commissions_futures.html.txt | found |
| B-18 | "discretion of a senior manager" | BrokerVenues/amp_restricted_countries_wb20250911.html | found (Wayback 2025-09-11, declared) |

### Could not check

- The SqueezeMetrics CSV itself (I-47: header read, file not saved by design) and its terms for the public file.
- The MFMF.xls track-record workbook (T-05) was not parsed; the SG Trend Sharpe figures were taken from TC's
  table as computed by the worker.
- Rosa (JFM) on the post-2013 decline: not retrieved by any worker; I-39 is a second-hand citation, as INF says.
- The E.12 persisted state under ~/.cache (q reproduction): outside the repository and not read, as the brief requires.
- The AiTrader repository's results: not read (only docs/STAGES.md lines 8-57 and the git log line).
- Whether 2010-2013 CME calendars can be sourced at evidence grade (both drafts depend on it; C1 has a probe, C2
  has no rule: R-07).

## Appendix: full recomputation table
| Item | File value | Reviewer value | Result | Note |
|---|---|---|---|---|
| E.12 span 2019-05-06..2024-02-29 (years) | 4.82 | 4.82 | agree |  |
| C1 trades per year | 107.5 | 107.5 | agree |  |
| C1 net $/trade at f=1 | 38.56 | 38.56 | agree |  |
| C1 net $/trade at f=0.5 | 10.71 | 10.71 | agree |  |
| C1 net $/trade at f=0.25 | -3.21 | -3.21 | agree |  |
| C1 $/month f=1 | 345 | 345.0 | agree |  |
| C1 $/month f=1/2 | 96 | 96.0 | agree |  |
| C2 test dates | 1913 | 1913.0 | agree |  |
| C2 power share 0.2 s 0.05 | 0.16 | 0.16 | agree |  |
| C2 power share 0.2 s 0.1 | 0.5 | 0.5 | agree |  |
| C2 power share 0.2 s 0.15 | 0.83 | 0.83 | agree |  |
| C2 power share 0.1 s 0.05 | 0.1 | 0.1 | agree |  |
| C2 power share 0.1 s 0.1 | 0.28 | 0.28 | agree |  |
| C2 power share 0.1 s 0.15 | 0.55 | 0.55 | agree |  |
| C2 power share 0.3 s 0.05 | 0.22 | 0.22 | agree |  |
| C2 power share 0.3 s 0.1 | 0.67 | 0.67 | agree |  |
| C2 power share 0.3 s 0.15 | 0.95 | 0.95 | agree |  |
| C2 power at 200 dates, s=0.14 (prereg: below ~0.5) | <0.5 | 0.508 | DISAGREE |  |
| C2 MES RT ticks | 2.04 | 2.038 | agree |  |
| C2 MES RT $ | 2.55 | 2.547 | agree |  |
| MES daily sigma $ (7775.5, 10.7%) | 263 | 262.0 | agree |  |
| MES last-half-hour sigma $ (12% of daily variance) | 91 | 90.8 | agree |  |
| cost / sigma today | 0.028 | 0.028 | agree |  |
| cost / sigma at index level a third | 0.11 | 0.084 | DISAGREE |  |
| 1.5c bar / sigma at index level a third | 0.17 | 0.126 | DISAGREE |  |
| cost / sigma at index level mean S&P 2011-05..2019-04 about 2,100 (ratio 0.27) | 0.11 | 0.104 | agree |  |
| 1.5c bar / sigma at index level mean S&P 2011-05..2019-04 about 2,100 (ratio 0.27) | 0.17 | 0.156 | agree |  |
| 1.5c in MES ticks | 3.057 | 3.057 | agree |  |
| 1.5c in index points | 0.764 | 0.764 | agree |  |
| C2 net $/trade per MES at s=0.1 (file says $13 'per MES') | 13 | 6.53 | DISAGREE | file's $13-$31 equals TWO MES, not one |
| C2 $/month 2 MES, 50 trades/yr, s=0.1 | 55 | 54.0 | agree |  |
| C2 $/month 4 MES, s=0.1 | 109 | 109.0 | agree |  |
| C2 net $/trade per MES at s=0.2 (file says $31 'per MES') | 31 | 15.61 | DISAGREE | file's $13-$31 equals TWO MES, not one |
| C2 $/month 2 MES, 50 trades/yr, s=0.2 | 131 | 130.0 | agree |  |
| C2 $/month 4 MES, s=0.2 | 261 | 260.0 | agree |  |
| C2 trades/yr at share 0.20 (1913/7.99*0.2) | 50 | 47.9 | DISAGREE |  |
| AIT: 15th trading day after 2026-10-02 | 2026-10-23 | 2026-10-23 | agree |  |
| AIT: 120th trading day counting 2026-07-28 as day 1 | 2027-01-15 | 2027-01-15 | agree |  |
| AIT: 120 trading days after 2026-07-28 (day 0) | 2027-01-15 | 2027-01-19 | DISAGREE |  |
| combined pass odds 1-(0.88)(0.90) | 0.21 | 0.208 | agree |  |
| P(best of 81 >= 2.51) independent | 0.396 | 0.396 | agree |  |
| Bonferroni 81 x 0.0062 | 0.502 | 0.502 | agree |  |
| z for p=0.0062 | 2.5 | 2.5 | agree |  |
| simulated P(max of 81 iid N >= 2.50) | 0.388 | 0.394 | agree |  |
| expected max of 81 iid N | 2.43 | 2.43 | agree |  |
| expected replication t h60 | 3.41 | 3.41 | agree |  |
| expected replication t hF | 3.17 | 3.17 | agree |  |
| critical one-sided t at 0.025 (~900 dates) | 1.963 | 1.963 | agree |  |
| h60 power (t bar) at 1 of effect | 0.93 | 0.926 | agree |  |
| h60 power (t bar) at 0.5 of effect | 0.4 | 0.398 | agree |  |
| h60 power (t bar) at 0.25 of effect | 0.13 | 0.134 | agree |  |
| h60 power (t bar) at 0 of effect | 0.025 | 0.025 | agree |  |
| hF power at 1 of effect | 0.89 | 0.886 | agree |  |
| hF power at 0.5 of effect | 0.35 | 0.352 | agree |  |
| hF power at 0.25 of effect | 0.12 | 0.121 | agree |  |
| hF power at 0 of effect | 0.025 | 0.025 | agree |  |
| h60 power incl 1.5c bar (ratio 0.7) at 1 | 0.88 | 0.878 | agree | joint bar approximated by the binding one |
| h60 power incl 1.5c bar (ratio 0.7) at 0.5 | 0.29 | 0.294 | agree | joint bar approximated by the binding one |
| h60 power incl 1.5c bar (ratio 0.7) at 0.25 | 0.08 | 0.081 | agree | joint bar approximated by the binding one |
| h60 power incl 1.5c bar (ratio 0.7) at 0 | 0.012 | 0.012 | agree | joint bar approximated by the binding one |
| expected trades h60 if share 20%: 518*8.90/4.82 | 957 | 956.0 | agree |  |
| expected trades hF | 913 | 912.0 | agree |  |
| Bayes factor, half-normal sd 1 prior | 6.6 | 6.57 | agree |  |
| Bayes factor, uniform 0..3.5 prior | 13.9 | 13.92 | agree |  |
| posterior mean of effect (t units), half-normal prior | 1.3 | 1.32 | agree |  |
| P(real) prior 0.02, BF 6.6 | 0.12 | 0.118 | agree |  |
| P(real) prior 0.02, BF 13.9 | 0.22 | 0.221 | agree |  |
| central 0.22*0.61+0.78*0.04 | 0.165 | 0.1654 | agree |  |
| skeptical 0.12*0.30+0.88*0.04 | 0.07 | 0.0712 | agree |  |
| midpoint of 0.165 and 0.07 (the '12%') | 0.12 | 0.1175 | agree |  |
| optimistic: P(real) prior 0.05 BF 6.6 -> 0.26; odds at P(pass|real) 0.75-0.93 | 0.35 | 0.222..0.269 | see note | 0.35 lies in the range for the uniform-prior BF only |
| optimistic: P(real) prior 0.05 BF 13.9 -> 0.42; odds at P(pass|real) 0.75-0.93 | 0.35 | 0.340..0.416 | see note | 0.35 lies in the range for the uniform-prior BF only |
| P(at least one false pass), rho 0.5 | 0.045 | 0.0454 | agree |  |
| P(at least one false pass), rho 0.7 | 0.041 | 0.0417 | agree |  |
| joint null probability 0.40 x 0.045 | 0.018 | 0.0178 | agree |  |
| P(real given pass) central: 0.22*0.61/0.165 | 0.8 | 0.81 | agree |  |
| P(real given pass) skeptical: 0.12*0.30/0.0712 | 0.5 | 0.51 | agree |  |
| sqrt(8.3/8.9) | 0.97 | 0.966 | agree |  |
| span 2010-06-07..2019-05-03 years | 8.9 | 8.9 | agree |  |
| usable span 2011-01-03..2019-04-30 years (first rows after warm-up) | 8.3 | 8.32 | agree |  |
| quoted total NG+5 legs | 57.314736 | 57.314735 | agree |  |
| x1.03 | 59.034178 | 59.034177 | agree |  |
| NG quoted chunks | 106 | 106 | agree |  |
| NG failed chunks all 2010-01..06 | 6 | 6 | agree |  |
| ZC quoted chunks | 106 | 106 | agree |  |
| ZC failed chunks all 2010-01..06 | 6 | 6 | agree |  |
| NQ quoted chunks | 106 | 106 | agree |  |
| NQ failed chunks all 2010-01..06 | 6 | 6 | agree |  |
| ZN quoted chunks | 106 | 106 | agree |  |
| ZN failed chunks all 2010-01..06 | 6 | 6 | agree |  |
| 6E quoted chunks | 106 | 106 | agree |  |
| 6E failed chunks all 2010-01..06 | 6 | 6 | agree |  |
| GC quoted chunks | 106 | 106 | agree |  |
| GC failed chunks all 2010-01..06 | 6 | 6 | agree |  |
| acct-2 headroom | 18.07027 | 18.07027 | agree |  |
| acct-1 headroom | 1.60998 | 1.60998 | agree |  |
| top-up acct-2 with margin | 40.963908 | 40.963907 | agree |  |
| top-up E.12 convention (quoted - combined headroom) | 37.634486 | 37.634485 | agree |  |
| NG x1.03 fits acct-2, leaves | 9.298844 | 9.298844 | agree |  |
| then ZC x1.03 leaves | 2.963586 | 2.963586 | agree |  |
| NG alone (M2 fallback) | 8.515948 | 8.515948 | agree |  |
| CL quoted (not bought) | 11.02 | 11.02 | agree |  |
| all 27 roots total | 213.94 | 213.94 | agree |  |
| ES 86 months -> 96 months | 10.27 | 10.267 | agree |  |
| x1.03 | 10.58 | 10.575 | agree |  |
| C1+C2 combined top-up (59.03+10.58-18.07) | 50 | 51.54 | agree |  |
| months 2011-05..2019-04 | 96 | 96 | agree |  |
| IDM(N=11) | 2.21 | 2.21 | agree |  |
| IDM(N=17) | 2.38 | 2.38 | agree |  |
| IDM(N=19) | 2.42 | 2.42 | agree |  |
| IDM(N=23) | 2.48 | 2.48 | agree |  |
| IDM(N=6) | 1.92 | 1.92 | agree |  |
| IDM(N=14) | 2.31 | 2.31 | agree |  |
| IDM(N=18) | 2.4 | 2.4 | agree |  |
| target $/instr/yr K=10000 tau=0.25 N=11 | 503 | 503.0 | agree |  |
| target $/instr/yr K=25000 tau=0.25 N=17 | 875 | 875.0 | agree |  |
| target $/instr/yr K=50000 tau=0.25 N=19 | 1591 | 1591.0 | agree |  |
| target $/instr/yr K=100000 tau=0.25 N=23 | 2692 | 2692.0 | agree |  |
| target $/instr/yr K=10000 tau=0.15 N=6 | 480 | 480.0 | agree |  |
| $10K/25% portfolio sigma $/yr | 3104 | 3103.0 | agree |  |
| $50K/25% portfolio sigma $/yr | 11824 | 11821.0 | agree |  |
| $10K cost $/yr (12 contracts x 10 RT x $3) | 360 | 360.0 | agree |  |
| $50K cost $/yr (42 contracts; M2K at program RT) | 1262 | 1260.0 | agree | file 1,262; $3 flat gives 1,260; M2K RT differs |
| $10000 mid net S | 0.16 | 0.154 | agree |  |
| $10000 mid E[$/month] | 40 | 40.0 | agree |  |
| $50000 mid net S | 0.19 | 0.19 | agree |  |
| $50000 mid E[$/month] | 189 | 188.0 | agree |  |
| E[MDD] 5y driftless, daily MC (sigma units) | 2.74 | 2.74 | agree |  |
| closed form 2 sqrt(pi/8) sqrt(5) | 2.8 | 2.802 | agree |  |
| discretisation shortfall 2 x 0.5826/sqrt(252) x sqrt... (BGK) approx | 0.06 | 0.073 | agree | Broadie-Glasserman-Kou continuity correction, order of magnitude |
| $10000/25% mid E[MDD] 5y | 7529 | 7509.0 | agree |  |
| $10000/25% mid E[MDD] 10y | 10303 | 10204.0 | agree |  |
| $10000/25% mid E[MDD] 10y as % of K | 103 | 102 | agree |  |
| $50000/25% mid E[MDD] 5y | 27946 | 28145.0 | agree |  |
| $50000/25% mid E[MDD] 10y | 37990 | 37961.0 | agree |  |
| $50000/25% mid E[MDD] 10y as % of K | 76 | 76 | agree |  |
| 1y fixed closed form S=0.3 D=10s | 0.43 | 0.43 | agree |  |
| 1y fixed closed form S=1.0 D=10s | 0.235 | 0.234 | agree |  |
| infinite fixed D/s for 10% ruin S=0.15 | 121.8 | 121.8 | agree |  |
| infinite fixed D/s for 10% ruin S=0.3 | 60.9 | 60.9 | agree |  |
| infinite fixed D/s for 10% ruin S=0.5 | 36.6 | 36.6 | agree |  |
| grid S=0.3 D=2000 set D $169: P inf fixed | 0.64 | 0.639 | agree |  |
| grid S=0.3 D=2000 set D $169: P 1y fixed | 0.36 | 0.358 | agree |  |
| grid S=0.15 D=5000 set D $169: P 1y fixed | 0.05 | 0.047 | agree |  |
| grid S=0.5 D=4500 set D $169: P inf fixed | 0.19 | 0.187 | agree |  |
| 1y EOD trailing ruin at D/s=27.2, S=0.3 (should be ~0.10) | 0.1 | 0.097 | agree |  |
| 1y EOD trailing ruin at D/s=29.0, S=0.15 (should be ~0.10) | 0.1 | 0.095 | agree |  |
| 1y EOD trailing ruin at D/s=25.5, S=0.5 (should be ~0.10) | 0.1 | 0.098 | agree |  |
| grid S=0.3 D=2000 set D $169: P 1y EOD trailing | 0.63 | 0.628 | agree |  |
| grid S=0.3 D=2000 set D $169: P 1y intraday trailing | 0.64 | 0.642 | agree |  |
| grid S=0.15 D=4500 set D $169: P 1y EOD trailing | 0.14 | 0.141 | agree |  |
| ranking: D/27 at D=2500 | 93 | 93.0 | agree |  |
| ranking: D/27 at D=4500 | 167 | 167.0 | agree |  |
| set B daily sigma (27 micros, rho 0.125) | 2432 | 2432.0 | agree |  |
| set D daily sigma (10 micros) | 169 | 169.0 | agree |  |
| years to t=3 at S=0.24 | 156 | 156.0 | agree |  |
| years to t=3 at S=0.3 | 100 | 100.0 | agree |  |
| years to t=3 at S=0.5 | 36 | 36.0 | agree |  |
| GFS: years to t=3 at 150 events, s=0.1 | 6 | 6.0 | agree |  |
| GEX: per-day Sharpe from 0.87..1.73 annual | 0.055-0.11 | 0.055-0.109 | DISAGREE |  |
| AQR TSMOM t at S=0.31 over 2012-01..2026-05 (14.4y) | 1.18 | 1.18 | agree |  |

## Follow-up check (2026-10-04)

Reviewer: RankingReviewer-FableXHigh, on the lead's request (reports/stage_e13_rulings.md, "Follow-up check").
Read: reports/stage_e13_rulings.md; reports/stage_e13_briefs/c2_odds.py and c2_odds.out; reports/stage_e13_ranking.md
v3 (sections 1, 3 odds rows, 4, 5, process note); reports/stage_e13_briefs/ranking_v1.md and ranking_v2.md; the fixed
lines of prereg_ngrepl.md, prereg_gexmom.md, venues.md, venues_part2.md, info_sources.md; the saved Phidias pages.
Helper: scratchpad/RankingReviewer/c2_check.py (scipy quadrature, independent of the lead's 400-point sum).

**Verdict.** R-01 CLOSED (the defect found is fixed: section 1 unchanged and applied with no tie criterion; both
candidates' odds are computed from stated inputs; v1 is on disk and its full sha256
e4106799b27819720155833b6a3e128b3215ee440f5a0e963eda011f036297fe matches the STATE prefix; v2
dcba2f0a7c84b27bdaeb4201fcacc5e84dbb718f5ee0b98dacfed7cc996cc594 matches the ruling). R-02, R-03, R-04, R-06, R-07,
R-08, R-10, R-12, R-13 CLOSED (checked in the files). R-05, R-09, R-11, R-14, R-15 not re-checked line by line
(the rulings describe fixes consistent with the review; R-09's new wording was seen in section 4 and is right).
Two new findings on the derived odds: R-17 SHOULD FIX, R-18 NOTE, R-19 NOTE. Overall: APPROVE WITH FIXES once R-17's
disclosure is in section 5; no number is wrong.

### Check 1: c2_odds.py against section 4 and the cells

The script computes exactly what section 4 states: P(pass) = P(present) x P(pass | present) + (1 - P(present)) x
P(pass | absent); mu uniform on [lo, hi] in sigma units when present; T1 passes iff the sample mean clears
max(1.5c, 1.96 SE) with SE = 1/sqrt(n), n = share x 1,913; times 0.9 for T1 beating T2. (b) = (a) x persistence x
deployability. My recomputation (scipy quadrature in place of the 400-point sum):

| Item | File (c2_odds.out / ranking cells) | Reviewer | Result |
|---|---|---|---|
| C2 skeptical: n, P(pass given present), (a), (b) | 383, 0.154, 0.039, 0.008 | 383, 0.154, 0.039, 0.0078 | agree |
| C2 central | 918, 0.450, 0.180, 0.050 | 918, 0.450, 0.180, 0.0504 | agree |
| C2 optimistic | 918, 0.692, 0.380, 0.154 | 918, 0.692, 0.380, 0.1541 | agree |
| C2 P(pass given absent), central / skeptical | not printed | 2.7e-6 / 4.4e-4 | the cost bar makes a false pass negligible (R-19) |
| C1 (b) central 0.165 x 0.8 x 0.5 | 6.6% | 0.0660 | agree |
| C1 (b) skeptical 0.071 x 0.5 x 0.5 | 1.8% | 0.0177 | agree |
| C1 (b) optimistic 0.35 x 0.8 x 0.5 | 14% | 0.1400 | agree |
| C1 (a) central / skeptical | 0.165 / 0.071 | 0.1654 / 0.0712 | agree |
| Combined central 1 - (1 - 0.165)(1 - 0.180) | 0.32 | 0.3153 | agree |
| Combined on headline 12% and 18% | 0.28 | 0.2784 | agree |
| Sensitivity grid P(present) x b (c2_odds.out lines 4-6) | 0.135 .. 0.297 | reproduced to 3 decimals | agree |
| Share lines (c2_odds.out 7-10): central (a) at share 0.10 / 0.20 / 0.30 / 0.48 | 0.180 at all four | 0.180 at all four | agree, but vacuous (R-18) |

### Check 2: is the R-01 ruling a literal application of section 1?

- Section 1 is byte-for-byte the v1/v2 text (lines 17-23 of v3): no tie criterion was added, none is used. The
  process note lists three versions with full hashes. That part of R-01 is closed.
- Reading the primary key as row (b). Section 1's sentence, "the lead's odds that the candidate's next stage moves
  the program toward an income-bearing deployment ... combine the evidence read at its post-publication strength,
  whether a clean test with adequate power exists, and the venue fit", names two components (post-publication
  strength, venue fit) that only row (b) contains: row (a) is a test passing in 2011-2019 or 2010-2019 and involves
  neither. So (b) is the better-supported reading, not a smuggled one. It is still a reading, and it decides the
  order: on row (a) C2 leads in the central (18.0% vs 16.5%) and optimistic (38% vs 35%) cases and trails only in the
  skeptical one (3.9% vs 7.1%). Section 5 says "Row (a) supports it" without saying that under (a) the order would
  flip. That must be disclosed (R-17).
- "The lead's odds" with three cases. The ruling ranks on "central and skeptical", two of three; section 1 names one
  odds figure. Taking the central case as the lead's odds gives the same order (C1 6.6% vs C2 5.0%), so no choice is
  hidden here, but the optimistic case reverses it (14% vs 15.4%) and section 5 does say so.
- Are C2's inputs a fair parallel to C1's annex inputs? The structure is parallel and every input is stated. Two
  asymmetries remain, one in each direction, and the central (b) margin (6.6% against 5.0%) lies inside them:
  (i) C1's chain carries a 0.5 factor for "a net forward test on a 150K-only vehicle"; C2's chain carries no
  forward-test factor although prereg C2 section 8 names a forward paper test as the next step. Adding 0.5 to C2
  gives (b) central 2.5% (C1's lead widens).
  (ii) C2's chain carries a persistence factor (0.35 central) for post-publication decay and the 0DTE change; C1's
  chain carries none, although a 2010-2019 pass plus the 2019-2024 near-miss still has to persist into 2026+.
  C2 overtakes C1 on central (b) at a persistence factor of 0.458 or higher (lead: 0.35); C1 falls below C2 if it
  is given any persistence factor of 0.76 or lower (0.066 x 0.76 = 0.050).
  (iii) P(pass | absent): C1 uses the annex's 0.04 (t bar only, two tests); C2's script applies the 1.5c bar as well,
  giving about 0. With the t bar only (0.025 x 0.5 for the T1 > T2 comparison), C2 central (a) is 0.188 and (b)
  0.0525: immaterial to the order (R-19).
  I cannot show the inputs were tuned to an order: P(present) 0.25 / 0.40 / 0.55 and the mean ranges are defensible
  readings of INF 2.7(a) (the conditional effect is "larger" than the unconditional 0.055-0.11 per day, size not
  quoted), and the persistence factor is lower for C2 for stated reasons (the window is pre-publication; the
  relative CP1 was null on MES 2020-2024). But the order is not robust to those judgments, and section 5 presents
  "C1's deployment odds hold up better" as if it were.

### R-17 SHOULD FIX. Section 5 must disclose that the C1/C2 order depends on the (b) reading and on the chain asymmetries

- File and line: reports/stage_e13_ranking.md section 5 opening paragraph (115-118) and item 1 (119-129); the
  "What the whole list says" paragraph (165-176).
- What is wrong: the text states the (b) reading and the central-case order as settled. It does not say that under
  the row-(a) reading C2 is first in two of three cases, nor that the central (b) margin reverses at a C2
  persistence factor of 0.46 (against 0.35 used) or with a C1 persistence factor below 0.76, nor that C2's chain
  omits the forward-test factor C1's includes. The user is choosing between the two on this order.
- Fix: three sentences in section 5: (1) why (b) is the reading (post-publication strength and venue fit are (b)
  components); (2) the row-(a) order and the two persistence thresholds above; (3) that the practical
  recommendation (pause, or C1 with C2 as companion) is the same under either reading, so the order decides only
  which draft is called the top pre-registration. No change to the inputs is required.

### R-18 NOTE. The central P(pass given present) is independent of the share by construction

- File and line: c2_odds.py lines 33-36 and c2_odds.out lines 7-10; ranking section 4 "C2 odds" and section 5 item 2
  ("Its power is no longer the weak point ... The 1.5c bar is").
- What: in every case the bar sits inside the mean range, and in the central case exactly at its midpoint (b = 0.15,
  range 0.05-0.25). Because Phi(x) + Phi(-x) = 1, the integral of P(mean clears b) over a range symmetric about b is
  0.5 for any SE, so P(pass | present) = 0.9 x 0.5 = 0.45 at any share. The four share lines in c2_odds.out are
  therefore identical by construction, not by sensitivity, and the R-02 share (48%) does not move C2's central odds
  in this model at all. The ranking's claim that the 1.5c bar, not power, is the weak point is consistent with this,
  but the statement "the share does not change (a)" would be misleading if read as a finding.
- Fix: say in section 4 that (a) depends on where the bar sits in the assumed mean range (P(pass | present) is 0.154
  / 0.45 / 0.69 because the bar is above, at, and below the range's midpoint), and that the share matters only when
  the mean range is not centred on the bar.

### R-19 NOTE. P(pass given absent) is treated with the cost bar for C2 and without it for C1

- As in check 2 (iii). The difference is 0.180 vs 0.188 in C2's central (a) and does not change any order. For
  consistency, either apply the 1.5c bar to C1's absent term too (the annex's 0.012 at h60) or use the t-bar-only
  figure for both, and say which.

### Check 3: fixes spot-checked in the files

| Finding | Where checked | Outcome |
|---|---|---|
| R-02 | ranking.md 80, 85 (share 0.48 power 0.33 / 0.86 / 0.995); prereg_gexmom.md 92, 96 (quote, 48%, caveat); info_sources.md 435 (lead note) | fixed |
| R-03 | ranking.md 106 "$6.5-$15.6 net per MES per trade ($13-$31 for the two MES of a 50K)" | fixed |
| R-04 | prereg_ngrepl.md 127-130: item 1 names (a) the OOF reload for q and (b) the single full-panel M1 fit | fixed |
| R-06 | ranking.md C5 cell and venues.md 74 / venues_part2.md 15: "CASH-account activation fee $149 / $149 / $169, a one-time ('lifetime') payment ...; evaluation price UNSOURCED" | fixed. The ruling's correction is right: phidias_tou.txt reads "ACCOUNT LIFETIME PAYMENT (in EUR or $)" and "By a single payment (Lifetime)"; phidias_rules.txt reads "Activation fees are Lifetime on each account (one-time payment per account until failure, no monthly fees)". My review's sentence "neither page uses ... 'lifetime'" was wrong (my search stopped at the alpha_* files); the substance of R-06 (activation fee, not evaluation fee; evaluation price UNSOURCED) stands |
| R-07 | prereg_gexmom.md 49 (exclude and count unsourced dates; stop before the purchase above 2%); one statement of c = 2.038 ticks; ranking.md 104 "c itself is fixed at 2.038 MES ticks (prereg section 4)" | fixed |
| R-08 | ranking_v1.md sha256 e4106799b278...97fe = STATE prefix; ranking_v2.md dcba2f0a... as recorded; full hashes in the process note | fixed |
| R-10 | ranking.md 109-110 "counting 2026-07-28 as day 1 ... day 0 gives 2027-01-19" | fixed |
| R-12 | prereg_ngrepl.md 58-59 "A C10 stop therefore CLOSES this registered attempt" | fixed |
| R-13 | ranking.md 65 "3.29 and 0.91 for the ruled window" | fixed |

Nothing else in the review was edited. No market data read; no web fetch; no commit.
