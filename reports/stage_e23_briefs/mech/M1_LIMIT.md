# M1_LIMIT: limit-move continuation and delayed price discovery (Stage E.23 P1.2 mechanism memo)

Worker: MechanismReaderM1_LIMIT-OpusHigh. Written 2026-10-17, 02:16-02:30 PDT (times from `TZ=America/Vancouver date`).
Brief: reports/stage_e23_briefs/brief_mechanism.md. Pages and logs: reports/stage_e23_briefs/mech_pages/M1_LIMIT/
(fetch_log.md, query_log.md). No market data was opened and no member was run.

Member: K6-limitcont-01 on HE and LE (strategy/members/k6/limitcont.py docstring, lines 1-24). Event: the settlement proxy
of d-1 is exactly +L or -L ticks from d-2's (an initial-limit close; d-2 itself was not a limit close). The member trades
day d intraday (08:45 to 12:59 CT) in the limit direction. **Event timing for E.23:** the trigger day is d, the day AFTER
the limit day. In the literature's notation (limit day = t=0), E.23 enters at the close of t=1 and holds over t=2..t=6
(h=5) or t=2..t=21 (h=20). So the published next-day continuation (t=0 close to t=1 close), which is the bulk of the
documented effect, falls BEFORE the E.23 entry and is not available to the multi-day book.

## 1. Evidence table

| Key | Citation | URL | Saved path (sha256) | Verbatim quote (page/section) | Claim supported (horizon, direction, magnitude, sample, instrument) |
|---|---|---|---|---|---|
| JQR-WP | Janardanan, R., Qiao, X., Rouwenhorst, K.G. (2017), "On Commodity Price Limits", working paper (OU energy-finance conference version) | https://www.ou.edu/content/dam/price/Finance/energyfinanceconference/papers/Janardanan-et-al-Limits%20Paper.pdf | reports/stage_e20_briefs/pages/LE/janardanan_etal_2017_wp_ou.pdf (f8a3ed65...ec28fc); .txt (73f48aaa...c80) (fetched in E.20, reused) | p.3: "We calculate average returns from three days before to five days after the limit day and do not find return reversal." p.11: "On the day after a limit up day, on average across the nine commodities the next day return is 63 basis points if we include all limit days and 39 basis points if we only include non-consecutive limit days." p.12: "it is clear the large positive returns after the limit up day do not reverse over the next week." p.12: "Cumulative returns show slight reversal in the week after the limit down day, mostly driven by the positive average return five days after the limit day." p.23: "returns on the first day after limit days continue in the same direction, and do not reverse after the first day." p.23: "Hedgers and speculators agree where the true price should be for the next day when trading resumes, such that there is no additional drift afterwards." p.7: "Our sample is from 01/07/1991 to 05/23/2016." | Horizon: t=1 to t=5 (pooled, 9 commodities incl. LC, LH). Direction after t=1: none (no further drift, no reversal for limit up; slight reversal after limit down). The paper's own mechanism (delayed price discovery) predicts the adjustment completes at t=1. Close-to-close daily. 1991-2016. |
| JQR-WP-T2 | same, Table 2 "The Effect of Limit Hits on Next Day Returns" | same | same | p.13, Table 2, LH column: All Limit Days "bup 0.44% (2.53)", "bdown -0.88% (-4.24)"; No Consecutive Limit Days "bup 0.20% (1.23)", "bdown -0.53% (-3.23)"; LC column: All "0.57% (4.07)", "-0.41% (-1.99)"; No Consecutive "0.36% (2.41)", "-0.08% (-0.50)". Note: "T-statistics in parentheses are clustered by time." | Horizon: t=1 only (excluded from E.23). Direction: continuation. Per-instrument (LH = HE, LC = LE). 1991-2016. Shows the gap between all-limit and non-consecutive estimates: part of the next-day effect comes from runs of limit days. |
| JQR-JFM | Janardanan, R., Qiao, X., Rouwenhorst, K.G. (2019), "On commodity price limits", Journal of Futures Markets 39(8), doi 10.1002/fut.21999 | https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/fut.21999 | mech_pages/M1_LIMIT/jqr2019_jfm_fig4_firecrawl.md (61b0cd47...ccda0); earlier passages reports/stage_e20_briefs/pages/LE/janardanan_qiao_rouwenhorst_2019_jfm_quotes.md. Raw PDF not saved (Firecrawl text only; curl and Scrapling 403 per E.20) | "The 95% confidence interval excludes zero for all 10 days. Cumulative returns are 52 and 36 basis points after 10 days." "After a limit up event (t = 0), the next-day return (t = 1) is on average 56 basis points across 12 commodities ... If we remove consecutive limit days, the average return is 29 basis points" (E.20 quotes file). Figure 4 data as extracted, limit up all events, cumulative %: "| 1 | 0.56 |" ... "| 5 | 0.46 |" "| 6 | 0.55 |" ... "| 10 | 0.54 |". Limit-down passage: "Cumulative returns show no reversal over the next 2 weeks." Page numbers not returned. | Horizon: t=1 to t=10 (2 weeks), pooled 12 commodities, 1991-2016. The confidence interval statement is for the CUMULATIVE return from t=0, which includes t=1; it does not test the t=2..t=10 increment. Increment after t=1, limit up: all events 0.56 to 0.54 (about -2 bp by t=10; about -1 bp at t=6); non-consecutive 29 to 36 bp (about +7 bp by t=10). Limit down: the column labels of the extracted tables are garbled (see section 4); the text says no reversal over 2 weeks. Nothing beyond t=10. |
| RB2010 | Reiffen, D., Buyuksahin, B. (2010), "The Puzzle of Privately-imposed Price Limits: Are the Limits Imposed by Financial Exchanges Effective?", Aestimatio 1: 110-143; MPRA Paper 35927 | https://mpra.ub.uni-muenchen.de/35927/1/MPRA_paper_35927.pdf | mech_pages/M1_LIMIT/reiffen_buyuksahin_mpra35927.pdf (716dbac8...63549); text rb_plain.txt (90a14eee...ea94) | p.122 (s.4.2): "we would expect that the price change between the closing price and the opening price on the following day would move in the same direction as the limit hit." "between 75 and 79% of limit hits were followed by continuations." Table 1: "Lean Hogs $2 $57.31 295 $0.44 74.92% 77.21%"; "Live Cattle $1.50 $73.19 266 $0.76 77.06% 81.97%". Sample: "January 2, 1998 through February 23, 2005". Abstract: "options prices accurately predict the (unconstrained) futures price the next day." | Horizon: limit close to NEXT OPEN only. Direction: continuation, completed at the next open. HE/LE (and pork bellies), 1998-2005. No multi-day evidence. Supports the timing point: the continuation is in the price before the E.23 entry. |
| HE2022 | He, X. (2022), "Essays on Extreme Events in Agricultural Futures Markets", PhD dissertation, University of Illinois (IDEALS); chapter later published as He and Serra, AJAE 104(5) | (IDEALS item; E.20 fetch) | reports/stage_e20_briefs/pages/HE/he_2022_dissertation_ideals.pdf (e0624529...c4b); .txt (31a089ab...a2152ae) (reused) | p.69: "On the next trading day following a locked-limit day, the price jumps to a new level that is 0.3 to 0.4 cents/lb. outside the previous day's limit. The price level remains persistently far from the previous limit after one hour of trading, suggesting that price limits impede price discovery and induce market under-reaction on locked-limit days." p.69: "In contrast, temporary-limit moves are followed by a price reversal". App. B.4, p.179-180: "The results provide strong support to the notion that price limits induce under-reactions in the lean hog and live cattle futures market on locked-limit days." Table B.5: "SignedLimit d−1,c 1.006*** 0.181 0.974*** 0.181". | Horizon: next open to +1 hour, and next-day settle-to-settle direction (logit). HE and LE, first five nearbys, 2014-2019 intraday. Continuation at t=1 only; nothing on t=2+. Also: a limit touched intraday but not closed reverses (not this member's event, which requires a limit close). |
| VM2003 | Veld-Merkoulova, Y. (2003), "Price limits in futures markets: effects on the price discovery process and volatility", International Review of Financial Analysis 12(3): 311-328 | https://dspace.stir.ac.uk/handle/1893/11985 | mech_pages/M1_LIMIT/stir_11985.html (83d81b68...df37ea). ABSTRACT ONLY (full text embargoed at Stirling; EUR and Glasgow pages carry no file) | Abstract: "we find evidence confirming the hypothesis that price limits delay price discovery instead of facilitating it. Our results also suggest that the impact of price limits on volatility and price reversals, found in previous studies, are mainly due to the properties inherent to the futures returns, such as volatility clustering." | Delayed price discovery (direction: continuation), agricultural futures. Horizon not stated in the abstract (RB2010 p.5 summarizes it as next-day: "price on the day following a limit hit tends to move in the same direction"). |
| PARK2000 | Park, C.W. (2000), "Examining futures price changes and volatility on the trading day after a limit-lock day", Journal of Futures Markets 20(5): 445-466 | https://ideas.repec.org/a/wly/jfutmk/v20y2000i5p445-466.html | mech_pages/M1_LIMIT/ideas_park_2000.html (7f811908...afd68). ABSTRACT ONLY | "The results show evidence that prices continue to rise on average the day after an up‐limit day." | Next day only; continuation; CBOT ags. |
| KR1997 | Kim, K.A., Rhee, S.G. (1997), "Price Limit Performance: Evidence from the Tokyo Stock Exchange", Journal of Finance 52(2): 885-901 | https://ideas.repec.org/a/bla/jfinan/v52y1997i2p885-99.html | mech_pages/M1_LIMIT/ideas_kim_rhee_1997.html (63fdd166...9b8). ABSTRACT ONLY | "Their evidence supports all three hypotheses suggesting that price limits may be ineffective." (the hypotheses include "delayed price discovery hypothesis") | Equity analog; delayed price discovery; abstract gives no horizon or size. |
| CME20-112 (context) | CME Submission No. 20-112 (cftc.gov ptc030220cmedcm002), Lean Hog limit amendment | https://www.cftc.gov/filings/ptc/ptc030220cmedcm002.pdf | reports/stage_e20_briefs/pages/HE/ptc030220cmedcm002.pdf (eaf18961...6150); .txt (ea103afb...c36) (reused) | "the Contract settled at the daily price limit ($3.00 or $4.50/cwt) 31 times (14 percent of trading days) in 2019." "Limit settlements can inhibit price discovery" | Event frequency for HE in the member's window (2019); not return evidence. |

Not used as evidence (fetched, not relevant): Fernandes and Rocha (2006) QMUL WP 579 (Brazilian index futures, intraday
cool-off; qmul_wp579.pdf/.txt), Fontinelle and Janzen (2020) NCCC-134 (wheat, trading volume on limit days;
fontinelle_janzen_nccc134_2020_firecrawl.md).

## 2. Member paragraph

### K6-limitcont-01 (HE, LE)

- **Strength: weak** for the E.23 window (t=2 onward). The published multi-day evidence on this event class (JQR-WP,
  JQR-JFM) is real and overlaps 2010-2016, but it shows that the continuation ends at t=1, before E.23's entry; the
  increment over t=2..t=10 is near zero and untested, and there is no published evidence at all for t=11..t=21. The
  next-day effect itself is "strong" (t >= 2, livestock-specific) but is excluded by the E.23 design.
- **Direction: neither continuation nor reversal after t=1 (literature: flat).** If the lead must assign a sign, the
  only source-backed sign is continuation of the limit move (it is the sign of the cumulative effect, and the paper reports
  "no reversal"), with a slight reversal reported after limit DOWN in the first week (JQR-WP p.12, driven by t=5).
  The sources do not disagree with each other; they agree the post-t=1 drift is about zero.
- **Reason.** Delayed price discovery: a daily limit stops the price short of its new equilibrium, so the remainder
  arrives when trading resumes (JQR-WP p.3, p.23; RB2010 s.4.2; HE2022 p.69; VM2003 abstract; PARK2000 abstract). The
  limit events are tied to fundamentals, not speculation (JQR-JFM abstract quoted in the E.20 quotes file: "shocks to
  fundamentals that lead to persistent price changes"), which is why the move does not reverse. But the same mechanism is
  self-limiting: once trading resumes, "there is no additional drift afterwards" (JQR-WP p.23), and RB2010 and HE2022 place
  the catch-up at the next OPEN (options-implied prices forecast the open; HE2022: the new level is reached at the open and
  "remains persistently far from the previous limit after one hour"). The member's own intraday window (08:45 to 12:59 on
  t=1) already starts after that open; E.23 enters even later, at t=1's settlement. A mechanism that would carry into t=2+
  exists only for a subset: when t=1 (the member's day d) is itself a limit close, the move is still unresolved at E.23's
  entry and the next-day continuation applies again. JQR-WP-T2's gap between all-limit and non-consecutive estimates for LH
  (bup 0.44% vs 0.20%; bdown -0.88% vs -0.53%) is consistent with runs of limit days carrying the move forward, and
  Fontinelle-Janzen (wheat) report a lagged limit move raises the next day's limit probability; no source measures the
  return from the close of a second consecutive limit day onward, so this sub-mechanism is [unverified] as a return
  claim. Under E.23's alpha-over-trend measure, whatever post-t=1 drift exists would also load on the same root's
  trend return, since a limit day is by construction a large move in the trend's direction (worker's reasoning, no source).
- **Horizon.** 5 days: JQR-WP (to t=5) and JQR-JFM (to t=10) cover it; they show about zero increment after t=1. 20
  days: no published evidence (JQR-JFM stops at 10 days; nothing found beyond).
- **Magnitude (for the V31 cost test).** Published increments after t=1 (pooled 12 commodities, 1991-2016, close to
  close, JQR-JFM Figure 4 as extracted): limit up, all events, cumulative 56 bp at t=1, 55 bp at t=6, 54 bp at t=10, so
  about -1 bp over E.23's h=5 and about -2 bp over t=2..t=10; non-consecutive limit up 29 bp at t=1, 36 bp at t=10, about
  +7 bp. Limit down: about zero to slightly reversing within the first week (JQR-WP p.12), no reversal by 2 weeks
  (JQR-JFM). No standard error or t statistic is published for the t=2+ increment; the "95% confidence interval excludes
  zero for all 10 days" statement is about the cumulative return from t=0. No per-commodity (HE, LE) multi-day figures
  exist in either version. For reference only, the excluded next-day effect for LH: +44 bp (t 2.53) up, -88 bp (t -4.24)
  down, all limit days; LC +57 bp (t 4.07), -41 bp (t -1.99); RB2010 1998-2005 mean next-day change $0.44/cwt (HE) and
  $0.76/cwt (LE), 75-77% continuation rates, close to next open. Unit conversion (worker's arithmetic, not sourced):
  ticks = bp x price($/lb) / (0.00025 x 10,000); at an illustrative HE price of $0.80/lb, 10 bp is 3.2 ticks ($32 per
  contract); at an illustrative LE price of $1.50/lb, 10 bp is 6 ticks ($60). The published post-t=1 increment
  (-2 to +7 bp) is a fraction of a typical round trip. Post-publication decay: not studied by any source; sample ends
  2016, before most of the member's 2019-2026 window. Event frequency: HE settled at limit 31 times in 2019 (CME 20-112);
  He (2022) counted few front-month locked-limit days in 2014-2019 (E.20 product_HE.md: 39, most in 2014).

## 3. Query log

Full log with time brackets: reports/stage_e23_briefs/mech_pages/M1_LIMIT/query_log.md. 13 WebSearch calls (of 60
allowed), 2 Firecrawl scrapes, no over-budget notice. Queries: (1) price limit hits futures returns days after limit
move continuation reversal agricultural futures; (2) lean hog live cattle futures limit move subsequent returns price
discovery delayed; (3) Veld-Merkoulova price limits futures markets; (4) Ma Rao Sears 1989 price limits reversal;
(5) Chen 1998 price limits overreaction price resolution; (6) Reiffen price limits price discovery CFTC; (7) Kim Rhee
1997 Tokyo; (8) commodity futures returns weeks after limit-up limit-down event study livestock; (9) China commodity
futures limit hit subsequent days; (10) Murphy Purcell live cattle limit move trader activity; (11) Park 2000 day after a
limit-lock day; (12) lean hog consecutive limit days 2020 subsequent week returns; (13) price limits event study 20 days
or one month after limit hit. Queries 12 and 13 added no new relevant source (stopping rule met). Every source found
measures the next day only, except JQR (to 5 and 10 days).

## 4. Not verified or not reached

- JQR-JFM: the raw PDF could not be saved (Wiley 403 to curl and Scrapling in E.20); only Firecrawl's extracted text is on
  disk. Its Figure 4 data are the extractor's reading of a figure: the first table (limit up, all events, and 90% up
  moves) is internally consistent with the text (0.56 at t=1, "52 ... after 10 days" vs 0.54 extracted), but the second
  and third tables have garbled column labels (the third table's "Limit Up (%)" column, starting -0.54, matches the text's
  limit-down all-events next-day value of -53 bp, so it is probably limit down; the "Limit Down (%)" column starting
  -0.86 is unidentified). The limit-down increments are therefore [unverified]. Page numbers were not returned.
- No standard errors for the t=2..t=10 increment in any source; no source covers t=11..t=21; no HE- or LE-specific
  multi-day figures in any source.
- Full text not reached (abstract only or bibliographic only): Veld-Merkoulova 2003 (embargoed), Park 2000, Chen 1998
  (no abstract on IDEAS), Kim and Rhee 1997, Ma, Rao and Sears 1989, Hall and Kofman 2001 (UTS full text embargoed),
  Kuserk and Locke 1996, Murphy and Purcell 1995 (not fetched). RB2010 summarizes Chen 1998 and Veld-Merkoulova 2003 as
  next-day continuation results (rb_plain.txt lines 296-310); none is cited by any source as a multi-day study.
- AgEcon Search served a JavaScript bot check to Scrapling and an empty 202 to curl; Firecrawl was used once there.
- The sub-mechanism for events whose day d is itself a limit close (continuation into d+1) has no direct published return
  measurement from the second limit close onward; it is inference from JQR-WP Table 2 and is marked [unverified].
