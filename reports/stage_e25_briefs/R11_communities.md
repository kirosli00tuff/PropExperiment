# R11 Communities as pointers (SourceReader-Communities-OpusHigh)

Reader R11, Stage E.25 (research only). Started 2026-10-18 01:38 PDT, written 01:50-02:05 PDT.
Nothing in sections 1, 2 or 7 that comes from a forum, video, podcast or social post is evidence;
those items are pointers (brief section 6). The evidence rows in section 3 are the published sources
each pointer maps to.

## 1. Answer (at most 250 words)

Method: 34 successful search queries (25 WebSearch, 9 Firecrawl search before its credits ran out at 08:43:21Z)
over r/FuturesTrading, r/Daytrading, r/algotrading, r/TopStepX, NexusFi/futures.io, Elite Trader,
YouTube titles and podcast listings. I logged 107 distinct result URLs to pages/R11/search_log.tsv,
each tagged by the setup its title or snippet names. Most queries named a setup, so the counts show
what the community talks about, not how often a setup really pays (query-design bias).

Recurring setups claimed to pay at prop firms, by result count: opening-range breakout, mostly 5 or
15 min on NQ (22); ICT family, meaning liquidity sweep, fair value gap, Silver Bullet 10-11 ET and
Asian/London range sweep (18); time-of-day windows (15); volume or market profile, value area and the
"80% rule" (15); automation (12); risk shaping, such as one or two trades a day or stopping after a
winner (10); order flow and footprint (9); scalping (8); VWAP (8); copy trading across accounts (6);
initial balance (5); news days (5); gamma levels (4); gap fill (3).

The top idea, ORB, has already been tested and failed in the program (B-H1, B-H3, B-H4, H1-H5,
RT1-RT4, G3, K1-cp2). Two recurring ideas are untested and can be run on the 1-minute bars the
program owns: the value-area 80% rule (C1) and a liquidity-sweep reversal in a fixed window (C2).
Neither has a published gross per trade. The nearest evidence for C2 (Osler 2002) points the other
way and is small: stop-run crossings continue rather than reverse, and the extra move is about 0.7 bp.
Base rates are negative: fewer than 1% of Taiwan day traders beat the market consistently (Barber et
al.), and 97% of persistent Brazilian mini-index futures day traders lost money (Chague et al.).

## 2. Candidate hypotheses (pointers mapped to evidence; zero published gross per trade)

| id | hypothesis | mechanism | instruments | entry window CT | hold | published gross/trade | best source (grade) | overlap |
|---|---|---|---|---|---|---|---|---|
| R11-C1 | Value-area "80% rule": RTH opens outside the prior RTH value area (70% of volume, approximated from 1-min bar volume spread over each bar's range), then two consecutive 30-min periods close inside it; trade toward the opposite value-area edge, flat by 15:00 | auction / mean reversion to prior-day accepted value (Dalton market-profile theory) | MES, MNQ (ES, NQ price paths) | 09:30 to 13:00 (after two 30-min brackets from the 08:30 open) | to opposite VA edge or 15:00 | none published; forum claim of about 62% "completion" (TradeStation, no sample stated) | Dalton, Mind Over Markets (practitioner-book) [unverified: not fetched]; NexusFi Academy 80% rule (pointer) | F6_1, D-H4, cp3 CLV family, H6: none uses prior-day volume-at-price value area |
| R11-C2 | Liquidity-sweep reversal (ICT "Silver Bullet" / Asian-range or overnight-high sweep): in 09:00-10:00 CT, the first 1-min close back inside after a print beyond the overnight (ETH) high or low, or the 02:00-08:30 CT range extreme, enters the reversal; target the range midpoint or 30-60 min | stop-run exhaustion: stops beyond obvious highs/lows fill, then price reverts | MNQ, MES | 09:00 to 10:00 | 30-60 min or range midpoint | none published for the reversal; Osler 2002: crossing stop clusters gives continuation of about 0.7 bp extra in 15 min (FX, 1996-98) | Osler (2002) NY Fed SR 150 (working-paper; later J. Int. Money Finance 2005 [unverified]) | B-H2 (stop cascade, follow), G5 (first RTH slot beyond ETH high/low), B-H3 fade leg, H5 (OR fade), F4_4 (round numbers): the sweep-and-reclaim reversal in a fixed window is untested |
| R11-C3 (low priority, high overlap) | Initial-balance (08:30-09:30 CT, 60-min) breakout, conditioned on a narrow IB (bottom 20th percentile of the last 20) | volatility expansion after compression | MNQ, MES | 09:30 to 14:30 | to 15:00 | none published for IB60 on index futures; forum "narrow IB extends 70-80%" is a range-extension frequency, not P&L | Holmberg, Lönnbark, Lundström (2013), crude ORB (peer-reviewed, already D.1 B4); Zarattini et al. ORB (R10 owns) | B-H1, B-H3, B-H4 (narrow OR15), H1-H5 (OR30), RT1-RT4, G3, K1-cp2: only the 60-min window differs |

Recurring ideas that are not proposed, with the reason:
- ORB, 5 or 15 min on NQ (the most frequent idea): already tested, see the C3 overlap list.
- First-hour direction to the close (edgeful "84% on NQ over six months", a vendor figure): tested as
  K1-cp1, F3_3 and E20H6-T1..T3 (Baltussen first-half-hour signal); all FAIL.
- Gap fill, half-gap target (edgeful, NexusFi Academy): tested as D-H4 (overnight gap fade).
- VWAP mean reversion "when VWAP is flat": R4 owns the VWAP families; the program tested K1-vwap-01
  and the Gate 0 k1_vwap_dist feature.
- Order flow, footprint, absorption and 2-4 tick DOM scalps: these need trades or MBO data the program
  does not own, and the 2-4 tick targets sit below the MES and MNQ round trip (R3 and R4 own this).
- Gamma or GEX levels: R1 and R2 own this; E20H6-T3 and C2 were tested or stopped. Community threads
  disagree on it ("Gamma exposure = snake-oil?", "GEX is a scam").
- News-day trading and the "full port on CPI/NFP" way of passing an evaluation: this is variance
  seeking, not an edge. It conflicts with Topstep P06 (no maximum position size into a scheduled major
  release), and E.19 found the funnel loses money at zero edge. E-H2 and the K-family release
  trials were tested.
- Copy trading across 5 to 20 funded accounts, small daily targets to satisfy consistency rules, and
  one or two trades a day or stopping after a winner: these shape account mechanics or risk. They
  scale or reshape an edge but do not create one (R9 owns the rules).

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Base rate: few day traders profit persistently | < 1% (1,000 of 360,000) outperform consistently; about 13% profitable in a typical year | "While about 13% earn profits net of fees in the typical year, the results of our analysis suggest that less than 1% of day traders (1,000 out of 360,000) are able to outperform consistently." | printed p. 13, Section on Table 1 results (2011-05-23 draft) | Barber, Lee, Liu, Odean, "The Cross-Section of Speculator Skill: Evidence from Day Trading", draft 2011; published J. Financial Markets 18 (2014) 1-24; https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf | working-paper (draft of a peer-reviewed paper; published numbers differ, see note) | pages/R11/barber_etal_2011_day_trading_skill.pdf |
| Top day traders' gross edge does not survive costs (Taiwan equities) | gross +13.1 bp/day (t=17.28) vs net -6.8 bp/day (t=-9.02) | "In aggregate, they earn positive gross returns on their day trading of 13.1 basis points per day (t=17.28), but these profits do not survive costs, and active day traders lose about 6.8 basis points per day net of fees (t=-9.02)." | printed p. 12, discussion of Table 1 | same | working-paper | same |
| Persistent futures day traders lose (Brazil mini-index futures, 2013-2015 entrants) | 97% of those persisting at least 300 days lost money; 0.4% earned more than a bank teller | "We observe all individuals who began to day trade between 2013 and 2015 in the Brazilian equity futures market, the third in terms of volume in the world, and persisted for at least 300 days: 97% of them lost money, only 0.4% earned more than a bank teller (US$54 per day), and the top individual earned only US$310 per day with great risk (a standard deviation of US$2,560). Additionally, we find no evidence of learning by day trading." | abstract | Chague, De-Losso, Giovannetti (2019), "Day Trading for a Living?", FEA-USP WP 2019-47 / FGV EESP TD 525 / SSRN 3423101; https://ideas.repec.org/p/spa/wpaper/2019wpecon47.html | working-paper [secondary-only: abstract only; full PDF fetch from repec.eae.fea.usp.br failed and the FGV repository shows a bot challenge, which I did not bypass] | pages/R11/ideas_chague_2019wpecon47.html |
| Stop-run crossings continue rather than reverse (nearest evidence to the "liquidity sweep") | absolute 15-min move 0.061% after crossing a round number vs 0.054% after an arbitrary number (dollar-mark); round number higher in 51 of 58 10-day intervals | "For example, dollar-mark moves an average 0.061 percent during the 15 minutes after crossing a round number, but only 0.054 percent after crossing an arbitrary number. Since the average move is higher for round numbers than for arbitrary numbers in 51 of the 58 relevant 10-day intervals, marginal significance for this test is below 0.001 percent." | printed p. 12, Section II | Osler, C. L. (June 2002), "Stop-Loss Orders and Price Cascades in Currency Markets", Federal Reserve Bank of New York Staff Report 150; https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr150.pdf | working-paper | pages/R11/osler_2002_sr150_stop_loss_cascades.pdf |
| Take-profit clusters reverse, stop-loss clusters trend | qualitative | "(2) The response to stop-loss orders is larger than the response to take-profit orders, which generate negative-feedback trading and are therefore unlikely to contribute to price cascades. (3) The response to stop-loss orders lasts longer than the response to take-profit orders. Most results are statistically significant for hours, although not for days." | abstract | same | working-paper | same |
| Pointer: open-based ORB on futures weakened after electronic 24-h trading | none | "What I can tell you is that in the old Pit days "Open" worked well across many markets. Now in 24hr e-trading, Close at a bigger spread and (High+Low+Close)/3 work well in different markets." (post quoting Murray Ruggiero, 2011-01-10) | post 5 | Elite Trader thread 210738, "Opening range breakout in new electronic markets"; https://www.elitetrader.com/et/threads/opening-range-breakout-in-new-electronic-markets.210738/ | pointer | pages/R11/et_210738_orb_electronic.html |

Conversion for the Osler row, in index terms; the lead computes ratios. The round-number excess is
0.061% - 0.054% = 0.007% = 0.7 bp, and it is an unsigned 15-minute move magnitude in 1990s FX, not a
signed trade P&L. At ES 6,000: 0.7e-4 x 6,000 = 0.42 ES points = 1.68 MES ticks (0.25 pt tick). At
NQ 24,000: 0.7e-4 x 24,000 = 1.68 NQ points = 6.72 MNQ ticks. Note the draft figures for Barber et al.
differ from the 2014 published version (a search summary gives 61.3/37.9 bp for the top 500 in the
published version; I did not fetch it, so that figure is [unverified]).

## 4. Negative evidence

- Base rates (section 3): Barber et al. find that fewer than 1% of Taiwan day traders outperform
  consistently, and the top group's gross 13.1 bp/day does not survive costs. Chague et al. find that
  97% of Brazilian mini-index futures day traders who persisted for 300 days lost money, with "no
  evidence of learning". Both are equities or equity-index futures. Their samples are not prop
  evaluations, but the setups below are traded by that population.
- Selection bias in every community pointer: payout posts ("$300,000 in payouts this year AMA",
  "$83000 prop firm payouts in 2025", "$32,504 across 17 funded accounts") are self-selected
  survivors, often tied to course or indicator sales. Losses go unposted, or are posted as
  "4 years of blowing challenges" or "3 funded accounts ... blew them all". No pointer I found
  carried a broker or firm statement.
- Community nulls (pointers): "6 months full time on algo, 17 strategies dead on MNQ/NQ" (r/algotrading;
  the snippet says studies "claiming Sharpe 2 to over 6 in intraday ES and NQ ... were just curve
  fitted"); "Breakout strategies are not profitable" (r/Daytrading); "ran the 15-min NQ opening
  range breakout through 18 years of 1-min data before buying another eval. glad I did."
  (r/TopstepCommunity; the snippet implies a negative result, but I did not read the thread);
  "I'm done trying ICT" (too discretionary); "Orderflow is impossible"; a YouTube commenter on a
  Silver Bullet video reporting an October win rate "like only 10%" (WebSearch summary, not seen
  verbatim).
- 80% rule: the only figure (about 62% completion in a TradeStation test, NexusFi) comes with no
  sample, period or P&L. LuxAlgo calls 80% "a rule-of-thumb label rather than a rigorously audited
  statistic" (WebSearch summary, not fetched).
- Osler (2002) predicts continuation, not reversal, after stop clusters are hit. That runs against
  the "sweep then reverse" reading of C2 and supports the follow-direction tests already run (B-H2,
  G5), which failed on MES.

## 5. Data and cost

- R11-C1, value-area 80% rule: needs ES/NQ 1-min OHLCV (owned; MES 2019-05 to 2025-03, NQ
  2010-07 to 2024-02, research window 2025-04 to 2026-06). Volume at price has to be approximated by
  spreading each bar's volume over its high-low range. A true TPO or tick profile would need trades
  data (not owned; R4 has the Databento prices). Research window testable: yes.
- R11-C2, sweep reversal: needs 1-min OHLCV only (owned). ETH and Asian-range extremes come from the
  same bars. Testable: yes.
- R11-C3, IB60 breakout: 1-min OHLCV (owned). Testable: yes.
- No prices quoted: none of these needs bought data.

## 6. Prop compatibility

- C1: RTH only, entry 09:30-13:00 CT, flat by 15:00 CT (before Topstep's 15:10 CT cutoff). One
  trade a day at most, which fits DLL sizing. Release days: CPI/NFP at 07:30 CT come before the entry
  window. FOMC at 13:00 CT falls inside the window's last minutes, so exclude FOMC days or stop entries
  at 12:30 (that is a design choice for the lead). No HFT, so automation via the TopstepX API is fine.
- C2: entry 09:00-10:00 CT, which is 07:00-08:00 PT in Vancouver, workable by hand (V39). The
  London/Asia-range variant (01:00-04:00 CT) is inside Topstep's trading day but means trading by hand
  at 23:00-02:00 PT, so it would need automation. The 09:00 CT window holds the 09:00 CT ISM/JOLTS-type
  releases (P06: not at maximum size into scheduled major releases).
- C3: flat by 15:00 CT; no conflicts.
- Community mechanics, for R9: copy trading across 5 XFAs (TopstepX) or up to 20 Apex PAs is claimed
  in vendor guides, and one pointer reports "Topstep start denying some payouts" for copy traders.
  The rules are R9's to verify.

## 7. Overlap with tested mechanisms

- ORB family (the most frequent pointer): B-H1, B-H3, B-H4, RT1-RT4, G3.RTH.15, H1-H5, K1-cp2-01
  (and the cp2 ports K2-K7). All FAIL. C3 differs only in the 60-min window.
- First-hour continuation: K1-cp1-01, F3_3, E20H6-T1..T3, E16-H1. FAIL.
- Gap fill: D-H4. FAIL.
- VWAP: K1-vwap-01, Gate 0 k1_vwap_dist. FAIL.
- Stop-run and level crossings: B-H2 (prior-day stop cascade), G5.RTH.15/30 (beyond ETH high/low),
  F4_4 (round numbers), B-H3 fade leg, H5 (OR fade). C2 differs: it trades the reclaim back inside
  after the sweep, in a fixed 09:00-10:00 CT window, not the breakout or an OR fade.
- Value area: no tested member uses a prior-day volume-at-price value area. The nearest are F6_1
  (open's position in the ETH range), the cp3 CLV family, and H6.
- Gamma: E20H6-T3, C2 (stopped). News: E-H2, K5-fomc-01, K2 release trials.

## 8. Re-dig verdict checks

Not a re-dig reader. No verdict is changed. The pointers above are consistent with the D.1 ORB
failures (Ruggiero's "pit days" remark) but they are not evidence.

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://nexusfi.com/robots.txt | 2026-10-18T08:39Z | (terms folder) | terms/nexusfi.com_robots.txt | ok | curl |
| https://www.elitetrader.com/robots.txt | 2026-10-18T08:39Z | (terms folder) | terms/elitetrader.com_robots.txt | ok | curl |
| https://nexusfi.com/terms.php | 2026-10-18T08:39Z | - | overwritten | 404 | curl |
| https://nexusfi.com/disclaimer/ (site rules and terms) | 2026-10-18T08:40Z | see terms_log.md | terms/nexusfi.com_terms.html | ok; terms FORBID automation, so no NexusFi content page was fetched | curl |
| https://www.elitetrader.com/et/help/terms/ | 2026-10-18T08:40Z | see terms_log.md | terms/elitetrader.com_terms.html | ok; allowed for named pages one at a time | curl |
| https://www.elitetrader.com/et/threads/opening-range-breakout-in-new-electronic-markets.210738/ | 2026-10-18T08:44:21Z | 93206d0d4a5e8744d4277b6eda631953bacc34c2f02f36d0f303051871f6e72f | pages/R11/et_210738_orb_electronic.html | ok | curl |
| https://www.elitetrader.com/et/threads/trading-with-futures-prop-firms-2025.382648/ | 2026-10-18T08:44:28Z | 21d764c1c66a005b2d4a596411cb4340b09e26859fc8f43dceb4fe40f89b91eb | pages/R11/et_382648_prop_firms_2025.html | ok (no setup content) | curl |
| https://www.elitetrader.com/et/threads/the-main-reason-why-doing-business-with-these-get-funded-programs-is-a-bad-idea.360334/ | 2026-10-18T08:44:35Z | fcef184b147066ef628671378cae06904371941afbe82f706322dba6217bd6c4 | pages/R11/et_360334_get_funded_bad_idea.html | ok (anecdotes on rules and liquidation) | curl |
| https://api.openalex.org/works (5 searches) | 2026-10-18T08:45Z | - | scratch | blocked: "Insufficient budget ... free daily budget shared by everyone on your network's IP address ... used up" | curl |
| https://api.semanticscholar.org/graph/v1/paper/search (2) | 2026-10-18T08:45:47Z | - | scratch | throttled (429), not retried; OpenAlex was also exhausted | curl |
| https://repositorio.fgv.br/items/e87d04fc-4b4c-4a56-ab5a-1c84c1afde1b/full | 2026-10-18T08:46Z | - | pages/R11/fgv_chague_item.html | blocked (bot-check page; not bypassed) | curl |
| https://faculty.haas.berkeley.edu/odean/papers/day%20traders/Day%20Trading%20Skill%20110523.pdf | 2026-10-18T08:46:38Z | 485aadd54702716224bdea95868d40027a0e8bf8732d3d68a6f7d5a29026adf1 | pages/R11/barber_etal_2011_day_trading_skill.pdf | ok | curl |
| https://econpapers.repec.org/RePEc:fgv:eesptd:525 | 2026-10-18T08:47Z | - | pages/R11/repec_chague.html | moved stub | curl |
| https://ideas.repec.org/p/spa/wpaper/2019wpecon47.html | 2026-10-18T08:47Z | dbd48d37a0e4d3ab1620e409557ee0bde3f15d3bc60a533c45477fc386d8dd00 | pages/R11/ideas_chague_2019wpecon47.html | ok (abstract) | curl |
| http://www.repec.eae.fea.usp.br/documentos/Chague_Losso_Giovannetti_47WP.pdf | 2026-10-18T08:47:45Z | - | none | failed (no file returned) | curl |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr150.pdf | 2026-10-18T08:48:23Z | 0132a12fe1116a4608e437bb36212e21589fec22e925a04edb903d0f0e601904 | pages/R11/osler_2002_sr150_stop_loss_cascades.pdf | ok (robots.txt checked: no disallow on staff reports) | curl |
| search-result log (107 URLs, 34 queries) | 08:41-08:49Z | cdcd6745... (pre-final) | pages/R11/search_log.tsv | ok | WebSearch, Firecrawl |

Terms read: nexusfi.com (forbidden, cited via search results only, and added to DO_NOT_COMMIT.txt for
the saved terms page); elitetrader.com (allowed one page at a time). Reddit and YouTube were used
through search results only. No reddit.com page, proxy mirror (r.til.io, redlib) or YouTube page or
transcript was fetched. Sites listed in search results but not fetched: sozai.app, videohighlight.com
(transcript sites; terms not read).

Budget notices:
- Firecrawl: HTTP 429 at about 08:43Z, then HTTP 402 at 2026-10-18T08:43:21Z: "The connected
  Firecrawl account is out of credits". Firecrawl was not used after that. The tool also asked to
  pass this on: "Your Firecrawl credits ran out. Add credits or upgrade to keep going:
  https://www.firecrawl.dev/billing/bw5epbcjrpzvwg0ds2wf0wh7xf408gb7".
- OpenAlex keyless daily IP budget exhausted at 08:45Z.
- WebSearch: 27 calls (25 returned results), with no over-budget notice. Two calls with
  allowed_domains=reddit.com returned "domains are not accessible to our user agent". Query
  numbers in search_log.tsv skip 27-28 (the two rejected calls).

## 10. Unfinished and unverified

- Chague et al. full text is not read (abstract only). Barber et al.'s published 2014 numbers are
  not fetched, so I quote the 2011 draft.
- Dalton's 80% rule source (Mind Over Markets, The Profile Reports) is not fetched [unverified].
- Reddit thread bodies are not read (terms). Recurrence counts come from titles and snippets, and
  the queries were setup-specific, so they are biased.
- No podcast episode or YouTube video content was read. Titles and descriptions come from search
  results only.
- The Zarattini ORB and VWAP papers are cited as R10's (owner); no number from them is used here.
