# Stage E.0 independent review (Task 6)

Reviewer: CatalogAuditor-FableXHigh (worker-xhigh, model Fable 5.1). Adversarial, independent of every
Opus worker and of the lead. Start 2026-09-24 02:27 PDT; paused with the session 02:35 to 06:10 PDT;
resumed 06:10 PDT; end: see the last line of this file. All times America/Vancouver.

**What I read (in full unless stated):** reports/stage_e0_STATE.md; docs/STAGE_E_DESIGN.md (D1-D15 with the
21:12, 21:52, 01:40, 01:52, 02:10, 02:15, 02:22 rulings); docs/NULL_CRITERIA_E.md; the eight cluster catalogs
reports/stage_e0_catalog_K1.md to K8.md (the assembled reports/stage_e0_catalog.md is their verbatim copy;
stage_e0_catalog.json used for the counts); reports/stage_e0_topstep_facts.md (F1-F12);
reports/stage_e0_partition.md; reports/stage_e0_liquidity.json and stage_e0_quotes.json (for the D1
recheck); reports/stage_e0_source_registry.jsonl; the research logs K1-K8 at every passage cited below
(extracted by id); docs/NULL_CRITERIA.md sections 1-3; reports/stage_d1f_confirmation_list.md sections
2.1-2.3; reports/stage_d1b_family_f_declaration.md F3.3; strategy/research/b_reference_breakout/
h1_friction_aware_opening_range_breakout.py; strategy/research/h_daily_bar/h6_prior_close_location.py.
No price, bar, tick or book data of any product was opened. No Databento call. No commit.

**Sources re-fetched by me** (curl, pdftotext, /usr/bin/python3; saved under the scratchpad
fetch/audit/ directory, never in the repository): NY Fed SR1188 (K2-002, sr1188.pdf); Hartley-Schwarz
EOM.pdf (K2-021); Kurov-Sancetta-Strasser-Wolfe 2017 (K2-007: Wayback copy of the skidmore PDF,
kurov_wb.pdf; the direct URL refused) and ECB WP 1901 (an older version, numbers differ); NBER w23327
(K3-002) and w22820 (K3-022); arXiv 2301.13204 (K3-005); Osler-Turnbull Brandeis WP101R (K3-017,
Wayback); Krohn-Mueller-Whelan INSEAD file (K3-016, krohn.pdf, full text); EFMA 2017_0580 (K5-012);
Prokopczuk-Wese Simen-Wichmann accepted manuscript (K4-001, Reading CentAUR); Awartani-Hussain-Virk
(K5-024, figshare file 65204829); Borgards-Czudaj-Hoang (K5-029, PMC9759686); Nilsson SSRN abstract
(K5-002, Wayback); Seeck (K1-005) abstract from the Crossref API (the reader's saved SSRN page is a
"Content Blocked" stub); Semantic Scholar API abstracts for K4-006, K4-021, K4-022, K8-003; AgEcon OAI
record for K6-027 (abstract; the PDF returned HTTP 202 with no body); Crossref bibliographic records for
Melvin-Prins (K3-001).
**Readers' saved copies used, each stated per row:** z_vwap.txt (K1-027), blasco.txt (K7-005),
denic.txt (K7-012), conc.txt (K7-042), shen.txt (K7-011), alquist.txt (K8-001), zdg.txt (K8-006),
wb3243111.html (K8-003), wb5382090.html (K8-004), k6/rp93.txt (K6-001), k6/jqr19.txt (K6-002),
k6/crushpdf.txt (K6-050), k6/cmefaq.txt (K6-048), alturki.txt (K4-009).
**Could not fetch:** Wen et al. Table 1 (K4-021; the Adelaide bitstream redirects to a login, Wayback
holds only the 302), the Rousse-Sevi working paper body (K4-022; only the journal abstract), the
Melvin-Prins body (K3-001; JFM paywalled), the Aitkulova-Balsamo-Seamon body (K6-027), the FiscalData
auctions API (no response from this sandbox; K2's auction counts not spot-checked).

---

## A. Passage re-read table (46 rows; every numeric claim a member rests on that I could reach)

Verdicts: MATCH = the source says what the log says, to the digit; MISREAD = it does not; UNVERIFIABLE =
the passage could not be reached. "Copy" names the text I checked: my fetch (audit/...) or the reader's
saved copy (fetch/...).

| # | Passage | Member(s) | What the log says | What the source says | Copy | Verdict |
|---|---|---|---|---|---|---|
| 1 | P-K1-005-a | K1-vxnband-01, K1-ml-01 KF2 | band = prior close +/- VXN/16; 860 events 2018-2026; 85.2% reversion | identical (Crossref abstract, DOI 10.2139/ssrn.7364204) | audit/cr_seeck.json | MATCH |
| 2 | P-K1-005-b | K1-vxnband-01 (cuts 20, 30; hold 30) | Sharpe 0.38 (VXN<20), 0.64 (VXN>=30); IS 2018-22 n=298 Sh 0.47; OOS 2023-26 n=191 Sh 1.29; pre-sample -0.94 | identical; the abstract adds "A momentum alternative that enters in the breach direction is rejected on the same data" and "the strongest edge appearing when VXN >= 30" (not logged; supports the fade side) | audit/cr_seeck.json | MATCH (log incomplete, not wrong) |
| 3 | P-K1-027-a/b/c/d | K1-vwap-01 | long above / short below VWAP, none overnight; "assumed no slippage"; ~22,000 trades (21,967); Sharpe 2.1, max DD 9.4%; hit ratio ~17% | all present: lines 296, 344-348, 612, 632, 623/730, 31/854 | fetch/z_vwap.txt (reader's) | MATCH |
| 4 | P-K2-002-b | K2-aucpre-01, aucpost-01 | V-shaped pattern, 0.7 to 1.2 bps across maturities | line 149-150 identical | audit/sr1188.txt | MATCH |
| 5 | P-K2-002-c | K2-aucpre-01 (180-min window), aucpost-01 | pre window = minute before close vs 180 minutes earlier; post = minute after results to 180 minutes later | lines 636-640 identical | audit/sr1188.txt | MATCH |
| 6 | P-K2-002-d | K2-aucpost-01 (direction) | reversal -0.32 to -0.75 bps | line 673 identical | audit/sr1188.txt | MATCH |
| 7 | P-K2-002-e | K2-fomcpost-01 | FOMC followed by a persistent decline in yields, 0.5-1.5 bps | lines 875-877 identical; context: Online Appendix Figs A4-A5, post-announcement window | audit/sr1188.txt | MATCH |
| 8 | P-K2-007-a | K2-predrift-01 (T-30 signal) | "Nine of the 20 ... about 30 minutes before ... about 40%" | lines 13-16 identical (2017 version) | audit/kurov_wb.txt | MATCH |
| 9 | P-K2-007-c/d | K2-predrift-01 (ZN, sign) | S&P +0.104% per 1 sd ISM Non-Mfg surprise; ZN row "0.104 (0.017)*** / -0.044 (0.009)***"; 5-min sd 0.12 / 0.04 | lines 503-506, 531 identical. Note: ECB WP 1901 (2016 version) has 0.064/-0.041 and 0.139/-0.058; the log cites the 2017/JFQA version, which is the one it fetched | audit/kurov_wb.txt, audit/ecbwp1901.txt | MATCH |
| 10 | P-K2-007-f | K2-predrift-01 (ZB) | "E-mini Dow ... 30-year Treasury bond futures ... All tests confirm robustness" | line 207 identical | audit/kurov_wb.txt | MATCH |
| 11 | P-K2-021-a/b/c/d | K2-monthend-01 | positive last few days of month; ~20 bp/month at 10y; two-day position 4.5% annualized; Sharpe ~1 | lines 15-17, 156-158, 787-789 identical ("two-day position", not "two trading days") | audit/eom.txt | MATCH |
| 12 | P-K3-001-a | K3-mehedge-01 | equity appreciation over the month predicts depreciation before the end-of-month fix | JFM abstract not reachable; the SSRN precursor abstract (10.2139/ssrn.2019274) says "hedging demand has a strong, but temporary, impact on exchange rates" and hedging flows "predict the direction of temporary exchange rate movements"; the registry DOI 10.1016/j.finmar.2015.09.002 is a different paper (JFM 26, "The Value of the Wildcard Option..."); the correct one is 10.1016/j.finmar.2014.11.001 (JFM 22, 50-72) | Crossref | UNVERIFIABLE (consistent at abstract level; registry DOI wrong) |
| 13 | P-K3-001-b | K3-mehedge-01 (magnitude) | 10% equity appreciation -> 14 bp depreciation in the hour before the fix | body not reachable | - | UNVERIFIABLE |
| 14 | P-K3-002-d | K3-ldnrev-01, ldnmom-01 | fixing window widened from 1 to 5 minutes; reform 2015-02-15 | lines 143, 581, 774 identical | audit/w23327.txt | MATCH |
| 15 | P-K3-002-f | K3-ldnrev-01 (month-end only; 15-min hold) | after the reform end-of-month profit still there; 1-minute gone; 15-minute stronger; intra-month none | lines 349-352 identical | audit/w23327.txt | MATCH |
| 16 | P-K3-002-g | K3-ldnrev-01 (EUR, JPY, CHF cells) | after-reform end-of-month profit (bp) 15/5/1 min: EUR/USD 1.21 1.32 -1.02; USD/JPY 2.39 2.27 -0.511; USD/CHF 6.19 -0.0809 -1.45 | Table 2 lines 960-964 identical; profits net of the bid-ask spread (footnote 9). BUT footnote 9 (lines 340-343) defines the pre-fix return over ~10 minutes (15:49:30 to 16:00:00) and the entry at the last quote before 16:00:30, holding X = 1, 5, 10 minutes, while the table and text say 15/5/1: a source-internal inconsistency the log did not record | audit/w23327.txt | MATCH on the numbers; see R-05 |
| 17 | P-K3-005-c | K3-tkypre-01 | gotobi PF 1.46 (no GC filter) vs non-gotobi 0.51 | lines 135-136, 159 identical | audit/arxiv2301.txt | MATCH |
| 18 | P-K3-016-b/c/d | K3-tkypost-01, ecbfix-01, clocks | post-Tokyo -5.5% p.a. (2.2 bp/day) t 9.2; fix times; windows 2:00-8:15 ET etc. | lines 90, 252, 961-962 identical | audit/krohn.txt | MATCH |
| 19 | P-K3-016-e | K3-ecbfix-01 | CME euro Sharpe 0.61 for the ECB fix trade | line 987-988 identical | audit/krohn.txt | MATCH |
| 20 | P-K3-016-f | K3-ecbfix-01, tkypost-01, section 3 | Table 8 CME row returns "5.53 0.58 6.11 0.06 -4.89 -4.83 -11.23 2.41 -8.82", Sharpe "0.99 0.08 0.65 0.01 -0.99 -0.51 -2.25 0.52 -1.27" | lines 1469, 1479 identical; the row sits under BA100% (full spread), CME 2009-2018 | audit/krohn.txt | MATCH |
| 21 | P-K3-017-b | K3-ldnmom-01 | front-run "immediately after 3:45 ... liquidate partly before and partly after the fix" | lines 228-234 identical | audit/osler.txt | MATCH |
| 22 | P-K3-022-b/c/d | K3-tkypre-01, X-01 | gotobi definition; 1.8 bp switch strategy; no reversal at the Tokyo fix; "particularly high at 5th and 10th days" | lines 827, 836, 841 identical | audit/w22820.txt | MATCH |
| 23 | P-K4-001-c | K4-ngpre-01 (window, side) | (-90,30) average return -0.37, (-90,-5) -0.18, (-5,30) -0.19 | Table 5 Panel B line 1142 identical | audit/prokopczuk.txt | MATCH |
| 24 | P-K4-001-d/e | K4-ngpre-01 | 12% (t 2.93), Sharpe 1.76 net; after 2011 Raw+TC+FC -0.97 (0.843) | lines 112, 1250-1255 identical; sample 2003-03..2018-12 | audit/prokopczuk.txt | MATCH |
| 25 | P-K4-006-a | K4-ngrev-01 | "Storage flows higher or lower than analysts had expected one week tend to be partially reversed the following week" | identical; the same abstract also says "Analyst's natural gas forecasts efficiently impound the available time-series information" (logged in the passage, not used by the catalog) | S2 abstract | MATCH; see R-06 |
| 26 | P-K4-009-a | K4-apipre-01 | "predict inventory surprises and pre-announcement returns in-sample and out-of-sample" | lines 94-97 identical | fetch/alturki.txt (reader's) | MATCH |
| 27 | P-K4-021-a | K4-eiamom-01 | third half-hour on EIA days predicts the last half-hour | abstract identical | S2 abstract | MATCH |
| 28 | P-K4-021-c | K4-eiamom-01 | slope 0.038 [2.12], 591 obs, adj R2 3.10% | Table 1 not reachable | - | UNVERIFIABLE |
| 29 | P-K4-022-a | K4-eiafade-01, apipre-01 | -0.25% ahead of the release; over-reaction partly compensated | journal abstract identical in substance | S2 abstract | MATCH |
| 30 | P-K4-022-d | K4-eiafade-01 (0.5% threshold, 4-hour exit) | positive-surprise days: drop ~0.5%, half corrected four hours later | working-paper body not reachable | - | UNVERIFIABLE |
| 31 | P-K5-002-a | K5-preauc-01 (the whole member) | negative price pressure into the auctions outside active US hours; none in US hours | Wayback SSRN abstract identical | audit/nilsson_wb.html | MATCH |
| 32 | P-K5-012-h/i | K5-pmfix-01 (10-min hold), preauc-01 | fix complete within ten minutes; no significant leakage before the start | lines 266, 592 identical | audit/efma0580.txt | MATCH |
| 33 | P-K5-024-a/b | K5-fomc-01 | adjustment continues past 5 min; 10-minute adjustment threefold the 5-minute | lines 319-321, 343 identical; sample 2007-01-02..2020-12-31 (line 559) | audit/awartani.txt | MATCH |
| 34 | P-K5-029-a/c/d | K4-ovr-01, K5-ovr-01 | decile overreactions 1 min to 1 h; crude 11.91%; industrial metals 0.98% lower but positive; metals 4.0% (5.0%); costs negligible | identical (PMC full text). The 11.91% sentence sits in the paragraph on the day "the contract price temporarily became negative" (2020-04-20) | audit/borgards_pmc.txt | MATCH; see R-07 |
| 35 | P-K6-001-a/d/f | K6-crushgap-01 (direction, 2-cent filter) | reverse crush after a gap down; corr -0.49 (-23.7); net mean per trade -0.36/0.35/1.02/1.74 over 3352/1861/922/457 trades; 1.5 c/bu cost | lines 69, 137, 235, 426, 434 identical | fetch/k6/rp93.txt (reader's) | MATCH |
| 36 | P-K6-002-a/b/d | K6-limitcont-01 | continuation after limit days; +40 to 62 bp / -38 to -63 bp next day; 0.76% close-to-open vs 0.15% close-to-close; 2063 ups, 2393 downs | lines 20, 56, 81, 276-277 identical | fetch/k6/jqr19.txt (reader's) | MATCH |
| 37 | P-K6-027-a | K6-wasdepre-01 | "directionally correct drift prior to release" | AgEcon OAI abstract identical; venue: Journal of the ASFMRA 2026 (practitioner); body unreachable, window and sample unknown | audit/agecon_oai.xml | MATCH (abstract only) |
| 38 | P-K6-050-a/b, P-K6-048-a/b | K6-crushgap-01 weights; EC-LIM | 11 lb oil, 44 lb meal, 0.022; corn limit 7% of a 45-day average, reset first trade date of May and November | identical | fetch/k6/crushpdf.txt, k6/cmefaq.txt (reader's) | MATCH |
| 39 | P-K7-005-b/d | K7-expiry-01 (5-hour window, long) | effect 5 h before expiry, strongest D2/D1; robustness "about 5 h before, not the last hour" | lines 3026-3027, 3115 identical; "15 h prior" (lines 380, 2983) refers to volume and volatility, not returns | fetch/blasco.txt (reader's) | MATCH |
| 40 | P-K7-011-b | K7-cp1-01 (covered) | first half hour predicts the last, slope 0.968, t 4.38 | line 257 identical | fetch/shen.txt (reader's) | MATCH |
| 41 | P-K7-012-b/c/f | K7-rev2h-01 (2-hour block, zero threshold) | autocorr -0.0557 (1h), -0.0858 (2h), -0.0564 (4h); rule text; x8 over three years | lines 467-470, 687, 799 identical | fetch/denic.txt (reader's) | MATCH |
| 42 | P-K7-042-a/b | K7-montrend-01 | Sharpe ~1.6 gross 2018-2025; "starting on Sunday at around 7:00 PM New York time ... roughly the next 24 hours" | lines 55, 64-68 identical | fetch/conc.txt (reader's) | MATCH |
| 43 | P-K8-001-e/f/h | K8-oilcad-01 (direction), K8-ml-01 KF5 (0.090) | dollar depreciates on higher oil, strongest vs CAD/MXN; Table 5 post-2008M9 CAD 0.090***; 5- and 30-minute windows "very close to the benchmark" | lines 559, 662, 1059 identical; column order 2y 5y 10y AUS CAD EUR GBP MXN NZD ZAR confirmed at 1046 | fetch/alquist.txt (reader's) | MATCH |
| 44 | P-K8-003-a/b/c | K8-flight-01 | 2007-2018; extreme negative 5-min S&P returns -> positive gold reaction; post-hours continuation; fast reaction | abstract identical (S2 and Wayback SSRN) | S2 abstract, fetch/wb3243111.html | MATCH |
| 45 | P-K8-004-a/b | K8-wkndbtc-01 | Bayesian regression and Kalman filter; negative weekend crypto returns predict poorer Monday stocks, evident after LUNA mid-2022 | identical (17 pages, posted 2025-08-06) | fetch/wb5382090.html (reader's) | MATCH |
| 46 | P-K8-006-a/b | K8-oilcad-01, K8-ml-01 KF1/KF2 | 5-minute data Canada only, 2005-01-03..2009-12-31; weak two-way Granger causality, stronger commodity->FX at horizon one, drops after | lines 824-828 identical | fetch/zdg.txt (reader's) | MATCH |

Summary: 42 MATCH (row 37 at abstract level only), 0 MISREAD, 4 UNVERIFIABLE (rows 12, 13, 28, 30). No member rests
on a misread number. Two logs are incomplete in a way that matters (rows 16 and 25); those are findings
R-05 and R-06 below, not misreads.

---

## B. Findings

Grades: BLOCKING = must change before E.1 can freeze it (look-ahead, Topstep conflict, misread number a
member rests on, leak). SHOULD FIX = wrong or ambiguous as written; fixable by a text or rule change the
lead can make in Task 8 without new data. NOTE = record it; no change required.

**Counts: BLOCKING 0; SHOULD FIX 10 (R-01 to R-10); NOTE 18 (R-11 to R-28).**

### R-01 SHOULD FIX. The ML member's Tier A membership is defined two ways.
- Where: docs/STAGE_E_DESIGN.md D5 lines 271-274 ("Tier A ...: every member that passes the ... screen ...,
  plus the cluster's ML member"); D15.10 line 837 ("failing the screen puts it in Tier B"); every K#-ml-01
  entry repeats D15.10 (K1 line 737, K2 630, K3 906, K4 829, K5 859, K6 871, K7 750, K8 667).
- What is wrong: under D5 the ML member is always in the Holm family; under D15.10 only if it passes the
  screen. A rule with two readings is not freezable; after screening a lead could take whichever reading
  suits.
- Smallest fix: one sentence in D5 (and D15.10) choosing one reading. My recommendation is D15.10's (the
  same screen for every member); D5's "plus the cluster's ML member" then goes.

### R-02 SHOULD FIX. CP1 is described as "the family null on MES", but MES's confirmation tested the opposite sign.
- Where: D6 row CP1 (design line 323); the "MES record" sentence in every cp1 entry (K1 lines 233-236,
  K2 136-142, K3 236-245, K4 231-241, K5 280-292, K6 231-240, K7 246-261).
- Evidence: reports/stage_d1f_confirmation_list.md lines 260-262 ("Confirmation direction s = the sign of
  the recorded implied edge (a negative recorded edge means the tested trade is the reversal of the
  predictor's sign)") and lines 284-286: F3_3_overnight_to_close_momentum recorded edge -4.9925, s = -1;
  F3_3_opening_30min_to_close_momentum -6.3358, s = -1. So D.1f's null for F3.3 covers the reversal-signed
  trade; the momentum form D6 ports lost about 5 to 6 ticks per event on MES's mined window and was never
  confirmed on MES. The catalogs' "these trials are close to the MES record" (K1 line 235) is wrong in
  sign; D6's selection criterion (4) ("the three cover three different MES classes") is met by class label
  only.
- Smallest fix: D6 and the cp1 entries say: "MES's confirmation tested the reversal-signed F3.3 statistics
  (s = -1) and found them null; the ported momentum form was negative on MES's research window and is
  untested on its confirmation." Keep the port (it is the literature's form) or drop the "MES record"
  sentences. No rule change.

### R-03 SHOULD FIX. CP1 on livestock is the (b) form D6 says it does not port.
- Where: K6 lines 248-253 (livestock signal = close 08:59 minus open 08:30, because the first bar is
  08:30) and K6 question 6 (line 1090-1091); D6 line 323 ("(b) is not ported").
- What is wrong: with no overnight session the "(a)" signal degenerates to the 30-minute open return,
  which is F3.3(b). Two trials (HE, LE) are then the un-ported form under the ported label.
- Smallest fix: either exclude K6-cp1-01 on HE and LE (-2 trials) or amend D6 to say the (b) form is what
  CP1 becomes on products with no overnight session. Either is fine; pick before hashing.

### R-04 SHOULD FIX. The "source-overlap" label is applied to one member; at least twelve trials qualify.
- Where: docs/NULL_CRITERIA_E.md section 3 lines 75-80 ("every member records its sources' data windows";
  overlap with the confirmation window -> label). Only K8 records windows (K8 C15 and the trial table);
  K1 to K7 were written before or without the rule and record none.
- Evidence (source windows I verified): K1-vxnband-01, Seeck 2018-2026 with OOS 2023-2026 (row 2; overlaps
  BOTH windows, so the research-window screen also re-tests the author's OOS); K1-vwap-01, 2018-01..2023-09
  (row 3); K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, SR1188 sample 1991-2024 (sr1188.txt line 134);
  K4-ovr-01 and K5-ovr-01, 2019-11-20..2020-06-03 (row 34); K5-fomc-01, 2007-2020 (row 33);
  K7-expiry-01, 2017-12..2020-11 (blasco.txt lines 190-191); K7-montrend-01, 2018-2025 (row 42);
  K6-wasdepre-01, K6-027 (2026 paper, sample unknown, flagged by K6 question 11); K1-cp2-01 on the
  Nasdaq-100 (hold 75 was chosen in D.1 from Mesfin's MNQ result, D.1 B5; sample unknown).
- Why it matters: without the label an edge on any of these could be "discussed for a final read" on a
  window its source already mined.
- Smallest fix: in Task 8 the lead adds the source-window line and, where it overlaps, the label to each
  entry above (and any I could not reach: K4-021 Wen, K4-022 Rousse-Sevi). No rule change.

### R-05 SHOULD FIX. K3-ldnrev-01's signal window is not the source's, and the entry says the log lacks it.
- Where: K3 lines 416-418 (M over 15 minutes, T_L-16 to T_L-1) and 433-437 ("The log does not give
  K3-002's window length"), 438-441 (entry at T_L+5).
- Evidence: NBER w23327 footnote 9 (audit/w23327.txt lines 340-343): "The pre-fix return is measured as
  the log-difference of the price at 16:00:00 and the first-recorded price during 15:49:30 to 15:59:30.
  The post-fix return is measured as the log-difference of the last quotes before 16:00:30 and the last
  quotes before 16:00+X:30, where X is chosen from 1, 5, and 10 minutes." So the source's signal is a
  ~10-minute pre-fix move and its entry is 30 seconds after the fix; the table and text say 15/5/1
  minutes (an inconsistency inside the source that the log did not record).
- Smallest fix: signal = close of the bar at T_L-1 minus close of the bar at T_L-11 (10 minutes), or keep
  15 and state it as a deviation from footnote 9 with a reason. The 16:05 entry can stay as a stated
  judgment (the post-reform window is 15:57:30-16:02:30; the source entered inside it).

### R-06 SHOULD FIX. K4-ngrev-01's chain contradicts the same abstract it rests on.
- Where: K4 lines 432-453, steps 1-3 ("this week's surprise tends to have the opposite sign of last
  week's").
- Evidence: the K4-006 abstract (row 25) says the flows "tend to be partially reversed" AND "Analyst's
  natural gas forecasts efficiently impound the available time-series information". If analysts impound
  the flow reversal, the SURPRISE does not reverse, and the member's step 2 has no support. The entry
  notes "Whether the market already prices the reversal is [unverified]" but does not quote the sentence
  that says it does.
- Smallest fix: quote the "efficiently impound" sentence as evidence against, and make the reported
  correlation of consecutive responses (K4 line 486-487) the stated falsification of the mechanism; the
  lead decides keep (1 trial, likely null) or drop.

### R-07 SHOULD FIX (text). K4-cp2-01's buffer table is the pre-ruling reading.
- Where: K4 lines 292-303 (QM 0.100, QG 0.020 = 4 vehicle ticks); K4 question 2 lines 1015-1022.
- Evidence: D6 lines 327-331 (21:52 ruling): 4 ticks of the exposure's MOST ACTIVE contract in price
  units, fixed whatever the vehicle. D6 says its text governs, but the hashed catalog must not carry a
  contradicting table.
- Smallest fix: crude buffer 0.04 on CL, QM and MCL alike; gas 0.004 on NG, QG and MNG alike.

### R-08 SHOULD FIX. Locked-limit exits are simulated as fills.
- Where: D9.7 (design lines 486-500: "an immediate exit ... fills at the next bar's open"); K6 C4 lines
  91-92 ("A lock at the daily limit shows up as bars at one price, and D9.7 governs it"); K6 C13.
- What is wrong: a market exit against a locked market has no counterparty (a long cannot sell at
  limit-down). The next-open fill is exactly a fill "improbable in live markets" (Topstep F7.2). It also
  truncates the loss, which flatters every grain and livestock member on lock days (conservative for a
  null, not for an edge).
- Smallest fix: an E.2 harness rule, written before any bar is read: when the bars show a lock on the
  exit's side, the D9.7 exit is not filled until a bar trades through, the trip is flagged, and the
  count of flagged trips is reported per member.

### R-09 SHOULD FIX. Six ML members leave the vehicle to "the lead decides" after D2's figures are seen.
- Where: K1 line 691-692, K3 856-857, K4 778-780, K6 826-827, K7 687 (no member if not admitted: fine),
  K8 612; D15.10 requires the vehicle "and reason" in the entry.
- What is wrong: D2's admission uses research-window risk and cost figures; a vehicle chosen after they
  are seen is a post-data choice inside a pre-registered member (item 7 of the brief).
- Smallest fix: each entry declares now a fallback order (as K2 and K5 do) or "no ML member if the
  exposure is not admitted". For K5-ml-01 the ruling at K5 line 792 contradicts the entry's "No fallback
  is declared" (801-802); align the text, and say that KF1-KF3 and KF5 are gold-event features whichever
  metal becomes the vehicle.

### R-10 SHOULD FIX (text). K6's D9.7 "release residual" predates the 01:52 exemption.
- Where: K6 C13 lines 213-221, K6-wasdepre-01 item 8 lines 662-665, K6 question 3 lines 1075-1081 ("the
  D9.7 exit fills at the first bar D9.5a allows, 11:02 at the earliest").
- Evidence: D9.7 lines 494-497: the D9.7 exit "is EXEMPT from the event-minute fill guard".
- Smallest fix: strike the residual paragraphs or mark them superseded.

### R-11 NOTE. K6-ml-01's first decision cannot trade.
- K6 lines 847-848 set W0 = 08:44; D15.4 B1 is the 30-minute return ending at t_j, which needs the 08:14
  bar; that minute is inside the 07:45-08:30 pause. Under D15.4's missing-input rule every 08:44 row is
  "no trade". Effective window is 09:14-12:44 (8 decisions). Fix the text (W0 = 09:14) before hashing so
  the row count is right.

### R-12 NOTE. D3 has no rule when no funnel cell passes.
- D3 lines 189-197 define eps_funnel as a minimum over passing cells; a thin or dear exposure may have
  none. Add: "if no cell passes, eps_X = the translated bar and the exposure is flagged".

### R-13 NOTE. The D1 input change (21:02 PDT) was legitimate and changed no verdict.
- STATE lines 148-153; design lines 64-70. From reports/stage_e0_liquidity.json: the 11 products with a
  2025 full-year figure (MNQ 1,600,000; ZF 1,800,000; ZT 1,000,000; HO 197,000; MGC 325,000; SIL 48,000;
  ZC 437,000; ZL 182,000; ZS 293,000; MBT 75,000; MET 144,000) all clear 10,000 under either period, so
  the only effect of the change is to rescue the 39 products the literal rule would have failed for want
  of a figure. The coverage figures in the D1 table recompute to the digit from stage_e0_quotes.json
  (NKD 0.6210, 6M 0.9035, MET 0.9472, 6N 0.9575, 6S 0.9700, TN 0.9725, ZT 0.9815). MET's exclusion
  (0.947) rests on five Wednesdays with per-date values 0.910 to 1.000, i.e. inside sampling noise of
  the 0.95 line; the rule was fixed first and applied as written, which is correct; the user may re-admit.
  Recommend the entry state the no-flip invariance explicitly.

### R-14 NOTE. Registry and provenance hygiene.
- K3-001's registry DOI (10.1016/j.finmar.2015.09.002) belongs to a different paper; the correct record
  is 10.1016/j.finmar.2014.11.001 (JFM 22, 50-72). K1-005's saved SSRN page (fetch/ssrn7364204.html) is
  a "Content Blocked" stub, so the log's "(abstract)" passages have no retrievable provenance in the
  scratchpad; they are nonetheless correct (row 1-2, Crossref). The readers' own hygiene lists (K2-006/
  K2-014 duplicate, K1-001 DOI, K3 author fields, K4-042/044 authors, K5-004/005 DOIs, K6-005=K5-023)
  stand.

### R-15 NOTE. K2-aucpost-01's 5-minute lag is supported by a passage the log did not quote.
- K2 lines 365-367 say no source gives a results release time. SR1188 lines 497-500: "For auction results
  release time, we collect the time stamp of the first Bloomberg news article ... The time between auction
  close and release of auction results ... has been just a few minutes for nearly all auctions since late
  2001." The 5-minute lag is therefore after the release on nearly every day; no change.

### R-16 NOTE. K4-ovr-01's crude figure is the 2020-04-20 episode.
- K4 lines 714-716 quote the 11.91% crude return; in the source (row 34) that sentence is in the
  paragraph on the day "the contract price temporarily became negative". K4's own C10 guard (P0 > 0)
  would have kept the member out that day. The number is not evidence for hourly crude reversal in
  2019-2026 generally; keep the trial, state this, and apply R-04's label.

### R-17 NOTE. The lead's narrowings and exclusions are not result-driven.
- K3-ldnmom-01 to EUR and JPY (K3 lines 471-474): by published ADV, a mechanical criterion. K5-preauc-01
  platinum (K5 line 438): one abstract, coverage and suspension risk; the same reasons the writer gave.
  K6-crushgap-01 ZS only, K6-limitcont-01 HE/LE only, K6-ovr-01 excluded (K6 lines 372, 488, 735): the
  spread cannot meet the 1-lot cap; grain limit trials are a same-direction subset of CP3; no grain-specific
  result. K1-predrift-01 (K1 line 583): the brief's rule on MES families. None reads a price result. One
  asymmetry to record: K2-predrift-01 (same paper, same rule, ZN and ZB) is kept while the Dow version is
  cut as "MES's E-family re-run"; defensible by product correlation, but the K2 member has the same
  relation to MES E-H1 (class C5, null) and should say so.

### R-18 NOTE. D5 argued adversarially.
- The screen (t >= 1.0 on the research window) cannot inflate a confirmation p-value: different data, and
  Tier B is never promoted (NULL_CRITERIA_E section 3). Two levers remain: R-01's ambiguity, and
  K = "clusters with a non-empty Tier A", which is known only after all eight screening sessions; a
  cluster confirming early must either wait for K or use K = 8. Fix: state "K = 8 unless every screening
  session has run", the conservative choice. DSR's Sharpe variance over a small, correlated Tier A is a
  noisy input; acceptable as a heuristic.

### R-19 NOTE. D2, D3, D4 argued adversarially.
- D2: r_c and the D8 costs come from 2025-26 and are applied to 2019-2024 bars (accepted program-wide, as
  for MES); q enters the per-contract series only through the depth term and the ML cost threshold, so it
  cannot manufacture an edge. The "not traded" decisions at rho outside [0.5, 2.0] are made after
  research-window risk is seen but by a mechanical rule; fine. D3: min(translated, funnel) only makes a
  null harder; for ZB/UB the translated bar is floor(85/31.25) = 2 ticks a day, so those nulls will be
  inconclusive rather than easy. D4: the "inconclusive by design" label is the one lever that makes a
  cluster null easier; it is decided from research-window series by a mechanical rule, before the
  confirmation purchase; require the power script and its inputs to be hashed with the list. Signal legs
  at their own S (MES 2020-02-03) is right. Not buying holdout-1 is strictly stronger.

### R-20 NOTE. The ML protocol (D15) and the eight entries.
- Leakage: purge and a one-date embargo are sufficient for forward-chaining folds (training precedes
  validation, so 20-date feature lookbacks cannot reach validation data); the timestamp validator, the
  planted-future canaries, the perturbation test and the window test are the right checks. Every feature's
  availability is <= t_j under D15.4; the boundary cases (K2 eqopen_ret at 09:00, K5 pm_open_move at
  T_P+2, K4 wpsr_move at T_W+15, K6 usda_resp at 11:14, K8 cl_wpsr at T_W+10) use bars that close
  exactly at t_j, which D15.4 permits. No normalization constant is taken from a confirmation or holdout
  date. Counting the ML member as ONE trial at confirmation is defensible: grid, folds and the refit touch
  research data only, and the grid is charged (+48) where it was searched. Two gaps: D15.5 does not say
  how the three outer scores become the D5 screen's daily t (concatenate the three scored blocks' daily
  series, or average three block means?); fix the definition. K7-ml-01 has about 1,100-1,200 rows against
  min_data_in_leaf 200 in the early folds (K7 question 7); acceptable, flagged.

### R-21 NOTE. Topstep items checked and clean.
- Flatten: every member's last fill precedes its group's F (grains 13:14 < 13:18; livestock 12:59 <
  13:03; the K6 CP2 livestock FOMC case is handled by the 01:52 skip rule). Grain pause: no member holds
  across it. CPI window: no K1, K5 or K8 fill in [07:25, 07:35] except K5-cp2-01 on HG, which the catalog
  skips (K5 line 376-377). Volatility caps: SIL and MHG <= 2; SI, HG, PL suspension flagged. Size: 1
  lot-equivalent everywhere. Orders: market only; no fill better than trade-through. Trade rate: K1-vwap-01
  <= 20 entries with >= 2-minute holds; K7-montrend-01 sits exactly at the 20-entry cap (allowed). Members
  that enter shortly before a release at half the maximum (K2-predrift-01, K4-ngpre-01, K4-ngrev-01,
  K6-wasdepre-01, K2-aucpre-01 at 07:30 on 11:30 ET closes) are permitted by F6.3's wording ("full Maximum
  Position Size"); the user should know these are the ones a risk manager would look at first.

### R-22 NOTE. Look-ahead items checked and clean.
- Clocks: T_L, T_E, T_T (K3 C9), the LBMA table (K5 C10) and T_exp (K7 C9) recomputed against the IANA
  rules, including the second-Sunday-of-March to last-Sunday-of-March and last-Sunday-of-October to
  first-Sunday-of-November mismatch weeks; all correct. No settlement, auction result, fix value or report
  value is read before publication (K6-limitcont-01 and K6-ml-01 read S(c, d-1) after d-1's settlement;
  K6 cp_ge_chg reads the Crop Progress table published at 15:00 CT for the session that opens at 19:00;
  K2 EC-AUC reads announcement fields with the announcemt_date < auction_date guard; K7 usrel_day reads
  publication at 07:30 for decisions from 09:30). Cross-leg timing in K8 (C4) is sound. One ex-post
  selection: K4 C9 drops releases whose actual time differed from the schedule; it cannot create an edge
  and is fixed pre-data; log the dropped dates.

### R-23 NOTE. Ports against D6 and the MES modules.
- CP2: matches h1_friction_aware_opening_range_breakout.py (OR 15 bars, 4 ticks, first close-through, one
  entry, hold counted in bars seen: lines 146-181) plus the two amendments; the bar-count hold lengthens on
  missing minutes and the catalogs say so. CP3: matches h6_prior_close_location.py and the Family H
  mechanics (complete-day, instrument guard, non-strict cuts, 08:30 intent, 14:58 exit). CP1: see R-02.
  Every instantiation's O, C, F, buffer and tick arithmetic checked (K1-K8 C7 tables; ZT 1/256 = $7.8125,
  ZB 1/32 = $31.25, MBT $0.50, eps_bitcoin 170, 6C 0.844 ticks per round turn, SI buffer $100).

### R-24 NOTE. Duplicates across clusters.
- K4-ovr-01 and K5-ovr-01 share one rule text (60-minute signal, 20-date trailing deciles, >= 80% of
  reference values, np.percentile linear, entry at t, exit t+59); the only differences are K4's positive-
  denominator guard and K5's sign-split report; harmonized. No cluster re-wrote a port as a new member; the
  "covered by CP#" dispositions (K3-010, K4-037, K4-013, K7-011, K7-022, K5-028, K1-026) are consistent.
  Correlated Tier-A members are flagged by the writers (K3's three London-fix members on month-end days,
  K3 lines 1058-1061; K6-limitcont-01 nested in K6-cp3-01; K4-eiafade-01 against K4-ovr-01's 10:00
  decision); Holm stays valid under dependence.

### R-25 NOTE. Nothing in the catalog required price data.
- Every threshold is a source value (VXN 16/20/30; 0.5% WPSR; 2 cents crush; deciles), a calendar count,
  or a stated judgment with no data behind it (K8-flight-01 0.5% tail, K8-oilcad-01 |z| >= 2, K3-ldnmom-01
  three bars, K3-tkypre-01 17:30 entry, K5-preauc-01 30 minutes). Expected-count arithmetic is from
  calendars and the sources' own counts. The only MES-derived constants (R* = $360.68, E|m_1| = 144.27)
  are the public NULL_CRITERIA.md figures. The one parameter set with the traded product's own price
  results is CP2's 75-minute hold on MNQ (from Mesfin, D.1 B5), inherited from D.1: see R-04.

### R-26 NOTE. NULL_CRITERIA_E's two new rules.
- "Inconclusive by design": sound if computed by hashed code from research-window series before the
  confirmation purchase (R-19). "Source-overlap": the label is conservative in the right direction (a
  member picked for an edge its source found on the confirmation window is biased toward showing that
  edge, so it makes a null harder, not easier) and correctly blocks an edge claim; it needs R-04's
  consistent application, and one wording fix: "overlaps its confirmation window" should read "overlaps
  its confirmation OR research window", since a research-window overlap makes the D5 screen a re-test of
  the source (K1-vxnband-01, K7-montrend-01).

### R-27 NOTE. K7 regime and window.
- Every MBT-dependent trial (K7 x7, K8-wkndbtc-01) confirms on at most 739 weekdays of a regime that ended
  2026-05-29 (24/7 trading, verified by the K7 writer from CME's releases). NULL_CRITERIA_E should carry
  the K7 statement caveat the writer asked for (K7 question 3). K7-expiry-01's surviving expiry days
  depend on the MBT.v.0 splice timing (K7 line 483-485); the count should be reported before screening
  and the member withdrawn (logged) if it is near zero.

### R-28 NOTE. Small text items for Task 8.
- K1-vxnband-01 and K1-ml-01 KF1: Cboe's VXN publication time is [unverified] in the entry; VXN's close
  is 15:15 CT and the file is updated overnight, so 08:30 CT use is safe; E.2 confirms as written.
- K5 header and K5-preauc-01 still say 3 trials beside the ruling's 2; the assembler flagged it.
- K2 and K3 CP2 entries carry the pre-amendment writer notes (K2 lines 214-217); harmless.
- K6 C7's ZL tick "0.0001 USD/lb (0.01 cent)" is right; K6-crushgap-01 uses USD/lb consistently with the
  CME cents formula (crushpdf.txt lines 250-257).

---

## C. Coverage of the brief's seven items and the extra checks

1. Look-ahead: R-22 (clean), R-20 (ML boundaries clean), R-11 (a no-trade decision, not a leak). No
   field is read before publication; no time-zone conversion moves a read earlier (all recomputed).
2. Topstep: R-21 (clean), R-08 (locked-limit fills, harness), R-10 (stale residual text). No member
   depends on a prohibited pattern; no fill better than trade-through; the news rule is met at half the
   maximum size by construction.
3. Misread sources: table A, 46 rows, 42 MATCH, 0 MISREAD, 4 UNVERIFIABLE; two logs incomplete in a way
   that matters (R-05, R-06).
4. Duplicates and ports: R-24 (harmonized), R-23 (CP2, CP3 match the MES modules), R-02 and R-03 (CP1).
5. D2 to D5 adversarially: R-18, R-19, R-01, R-12.
6. Price-data dependence: R-25 (none found), R-04/R-25 (the inherited MNQ hold).
7. ML protocol and entries: R-20, R-09, R-11, R-01.
Extra checks: D1 floor and the 21:02 input change, R-13 (legitimate, no verdict changed, coverage
figures recomputed); the lead's narrowings, R-17 (not result-driven); the NULL_CRITERIA_E rules, R-26.

Not checked (tools): K2's FiscalData auction counts (API unreachable from this sandbox); the bodies of
K4-021, K4-022, K3-001 and K6-027 (table A rows 12, 13, 28, 30, 37).

---

## Verdict

**READY WITH FIXES.** No BLOCKING finding: no look-ahead, no Topstep conflict, no misread number a member
rests on, no leak. Ten SHOULD FIX items are text or rule clarifications the lead can make in Task 8
without data: the ML Tier A definition (R-01), the CP1 sign statement (R-02) and its livestock case
(R-03), the source-overlap labels (R-04), K3-ldnrev-01's window (R-05), K4-ngrev-01's counter-evidence
(R-06), K4's buffer table (R-07), a locked-limit harness rule for E.2 (R-08), ML vehicle fallbacks
(R-09), and K6's stale D9.7 text (R-10). After those, the catalog and design are fit for the user's review
and E.1's freeze.

End: 2026-09-24 06:18 PDT
