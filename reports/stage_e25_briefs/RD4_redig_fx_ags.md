# RD4 re-dig: FX (6E) and grains/livestock (ZC ZS ZL LE HE) sources

Reader: RedigReader-FXAgs-OpusHigh (RD4), Stage E.25, research only. Started 01:38 PDT, written 02:05 PDT 2026-10-18.
Sources: every source cited in reports/stage_e20_briefs/product_{6E,ZC,ZS,ZL,LE,HE}.json (50 evidence rows,
about 35 distinct sources), plus the E.0 K3 notes (reports/stage_e0_research_K3.md) for the fix papers.
Ranked by relevance to a sized intraday effect: (1) Krohn-Mueller-Whelan 2024 JF; (2) Ito-Yamada 2018 and
Evans et al. 2018 FCA (post-reform fix); (3) Evans 2018 JBF; (4) Melvin-Prins 2015; (5) Janardanan-Qiao-
Rouwenhorst 2019 and He 2022 (limits); (6) Anderson-McKenzie-Noyes 2024 (WASDE); (7) Elaut-Froemmel-
Lampaert 2018; the rest (Fanta, Wang, the Aalto thesis, the soybean-complex and Chinese-futures papers)
carry no sized intraday effect on a CME vehicle and were not re-dug past their E.20 rows.

## 1. Answer (at most 250 words)

The deeper reading supports the FX and ag closures. Krohn-Mueller-Whelan (KMW), the source of E.20's two
largest 6E rows, also report the fix reversals on CME futures. There the post-London leg for the dollar
portfolio is 0.64 bp (t 2.20), against 1.20 bp on spot (Table III, 2006-2019). The paper also says that
"for the trader (or liquidity demander), reversal returns turn negative once transaction costs are taken
into account", and it notes a "downward trend towards the end of the sample period". E.20's 6E E2/E3
sizes (6.06 and 7.84 6E ticks, from spot data over the full sample) therefore overstate what a futures
trader would earn. The post-reform month-end evidence (Ito-Yamada EUR/USD +1.21 bp after spread; FCA:
reversals "disappear from 2015 onwards") sits below the M6E hurdle. That supports the K3-ldnrev-01 null.

Limit continuation sits in the close-to-open gap. JQR: 0.76% close-to-open against 0.15% close-to-close per
1% implied move. He 2022: after the gap, the level "remains persistently far ... after one hour". K6's entry
at 08:45 CT comes after that move, so the "null by inactivity" verdict is supported.

The KMW forward-citation dig reached co-author Whelan's later paper (Baltussen-Terstegge-Whelan 2024). It
reports a 3rd-Friday SOQ spike in ES futures: +14.30 bp from Thursday close to Friday open (about 34 MES
ticks at ES 6,000), then -12.89 bp from the open to the close, and 24.2 bp combined after spread (2003-2021).
This weakens V38's wording, but it duplicates R12-C1/C2. The one post-2015 pre-registered fix study
(Benenchia et al. 2025) could not be retrieved.

## 2. Candidate hypotheses

| id | hypothesis | instruments | window CT | trades/yr | published effect | micro ticks | grade | note |
|---|---|---|---|---|---|---|---|---|
| RD4-C1 | 3rd Friday Price Spike: long in the Thursday night session into the Friday 08:30 CT SOQ open, then short until about 11:00 CT (full reversal "by about noon" ET) | MES, MNQ, MYM | Thu 17:00 to Fri 08:30; Fri 08:30 to 11:00 or 15:00 | 12 | ES futures +14.30 bp (t 3.54, sd 60.53), then -12.89 bp (t -2.40, sd 80.45); combined 24.20 bp after bid-ask (SR 0.80) | leg 1: 34.3 MES ticks (14.30 bp x 6000/10000 = 8.58 pt / 0.25); leg 2: 30.9 | working-paper | DUPLICATE of R12-C1/C2 (same paper, independent route); the lead merges |

Ag and FX candidates: none. Every re-dug FX or ag effect is either below the hurdle on futures (KMW
futures, Ito-Yamada), concentrated in the overnight gap (limit continuation), conditioned on data the
program does not own (the WASDE analyst surprise), or classified only ex post. He's temporary-limit
reversal is defined by "whether the last limit move continues until the end of the trading session", so it
cannot be traded in real time.

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| KMW reversals on CME futures, dollar portfolio | post-L 0.64 bp (t 2.20) vs spot 1.20 (t 3.08); pre-E -1.64 vs -1.65 | "RTH Spot -1.58 1.88 -1.65 -0.04 1.20 -0.20 ... CME Futures -1.46 1.80 -1.64 0.11 0.64 -0.56 (-8.94) (9.37) (-4.76) (0.30) (2.20) (-0.90)" | Table III p.33; "The sample period is June 2006 to December 2019." | Krohn, Mueller, Whelan 2024 JF 79(1); WRAP copy | peer-reviewed | reports/stage_e20_briefs/pages/6E/krohn_mueller_whelan_2024_jf_wrap.pdf (a7975f26f9b42b83) |
| KMW: liquidity demander loses after costs | AUD LD pre-L+post-L -6.53 bp (t -5.86); GBP -0.73 (t -0.74) | "for the trader (or liquidity demander), reversal returns turn negative once transaction costs are taken into account" | text p.32; Table X p.40 | same | peer-reviewed | same |
| KMW decay | qualitative | "we do observe a downward trend towards the end of the sample period ... arbitrage capital is indeed allocated to exploiting the reversal patterns, leading to a decline in the intraday return predictability." | p.14 | same | peer-reviewed | same |
| KMW counterpoint | qualitative | "some of the largest average European reversal returns were realized in 2015 and 2016." | p.14-15 | same | peer-reviewed | same |
| Post-reform month-end contrarian, EUR/USD, after spread | +1.21 bp (15 min), +1.32 (5 min), -1.02 (1 min); intra-month all negative | "After Reform, End of month: 'EUR/USD ... 1.21 1.32 -1.02'" (E.0 verified passage P-K3-002-g) | Table 2, via E.0 notes | Ito, Yamada 2018 JIMF 80; NBER w23327 | peer-reviewed [secondary-only] (NBER terms now forbid automated access; not refetched) | reports/stage_e0_research_K3.md |
| Fix reversals gone after 2015 (all days pooled) | figure only | "short-term price reversals in prices around the fix decrease steadily throughout our sample period, and disappear from 2015 onwards" (E.0 P-K3-019-a) | FCA OP46 summary | Evans, O'Neill, Rime, Saakvitne 2018 | exchange-regulator [secondary-only] | reports/stage_e0_research_K3.md |
| Fix dynamics "unchanged since 2015" (theory) | data 1996-2013 | "Our model can explain why fix-price dynamics are qualitatively unchanged since 2015 despite notable reforms (Ito and Yamada, 2017b; van der Linden, 2017)"; "Data for all currencies end in December 2013" | section B (txt 1910); data (txt 1644) | Osler, Turnbull, Brandeis WP 101R; JBF 185 (2026) | working-paper | pages/RD4/osler_turnbull_brandeis_wp101r.pdf (4bb9b850bd5eb23d) |
| Evans month-end returns annualised by a x252 convention | EUR/USD 3.965 "annual percent" at 1 min: about 1.57 bp per event if x252, about 33 bp if x12 (unresolved) | "Because returns are generated at the daily frequency, I include the 1/sqrt(252) scale factor to "annualize" the ratio (using the convention that a year equals 252 trading days)." | p.32 | Evans 2018 JBF 87 (MPRA 81583) | peer-reviewed | reports/stage_e20_briefs/pages/6E/evans_2018_jbf_wmrfix_mpra81583.pdf (f34bf1d22e364cf4) |
| Limit continuation is in the open gap | 0.76% close-to-open vs 0.15% close-to-close per 1% | "a 1% increase in the return calculated from limit day close to options-implied prices is associated with a 0.76% increase in the close-to-open futures returns, and 0.15% increase in the close-to-close futures returns. Implied prices forecast next day opening prices better than closing prices" | WP intro; sample 01/07/1991-05/23/2016 | Janardanan, Qiao, Rouwenhorst WP 2017; JFM 39(8) 2019 | peer-reviewed (WP read) | reports/stage_e20_briefs/pages/LE/janardanan_etal_2017_wp_ou.pdf (f8a3ed6596667a3d) |
| Locked-limit next day: gap, then flat for an hour | gap 0.3-0.4 c/lb (median) | "On the next trading day following a locked-limit day, the price jumps to a new level that is 0.3 to 0.4 cents/lb. outside the previous day's limit. The price level remains persistently far from the previous limit after one hour of trading" | printed p.69; sample 6 June 2014 to 23 December 2019 | He 2022, UIUC dissertation ch.3 | thesis | reports/stage_e20_briefs/pages/HE/he_2022_dissertation_ideals.pdf (e0624529946c8ccf) |
| Temporary vs locked limit is an ex-post split | 144 HE temporary vs 172 locked events | "When the last limit move continues until the end of the trading session, we characterize the corresponding event as a locked-limit day, otherwise, we characterize the event as a temporary limit day." | txt 2760-2772 | same | thesis | same |
| WASDE soybean drift 30 min to close | -0.061 (30 min, SE 0.031) to -0.124 (day, SE 0.049) | "Soy News -0.028 -0.061** -0.124** (0.027) (0.031) (0.049)" | Table 2 p.5 | Anderson, McKenzie, Noyes 2024 NCCC-134 | working-paper | reports/stage_e20_briefs/pages/ZC/anderson_mckenzie_noyes_2024.pdf (e9df84b1f3fdad98) |
| 3FPS in ES futures | +14.30 / -12.89 bp; 24.20 bp after spread | "The average overnight cumulative return in the active futures contract is equal to 14 bps which completely reverses by 12:00."; Table II "Panel (b) Futures ... 14.30 -12.89 ... t-stat ... 3.54 -2.40 ... The sample period is 2003 to 2021." | p.12-13; Table II; Table A.4 | Baltussen, Terstegge, Whelan, "The Derivative Payoff Bias", WP Sept 2024 (AEA 2025) | working-paper | pages/RD4/baltussen_terstegge_whelan_2024_aea.pdf (b98e7372007c4329) |

Forward-citation and replication record (OpenAlex `cites:`, saved under pages/RD4/oa_cites_*.json):
- KMW (W4389903555, 17 citing works; SSRN version W3024923689, 11): no re-test on CME futures. The citing
  works are fix-design theory (Muhle-Karbe and Oomen 2023-2025), manipulation studies (Colla-Distaso-Vitale
  2024), FX transaction costs (Filippou et al. 2024 JFE), FOMC FX (Lee-Wang 2025 RAPS, the published version
  of the Wang 2018 dissertation row 6E E7), and the co-author's 3FPS paper (BTW 2023/2024).
- Melvin-Prins (W2040846150, 60 citing works): post-2015 re-tests are Benenchia-Galati-Lepone 2024/2025
  (pre-registered; Stage 2 not retrieved), Osler-Turnbull 2024/2026 (theory, data to 2013), Ben Zeev-Nathan
  2024 RAPS and Sizova-Syrstad-Saevareid 2025 (hedging channel; abstracts only, not used as evidence), and
  Ito-Yamada 2017/2018 (read in E.0).
- Evans 2018 (W3022362291, 28 citing works): the same fix literature plus Evans 2019, "Front-running and
  collusion in forex trading" (SSRN, not read).
- Elaut-Froemmel-Lampaert (W3125300284, 49 citing works): intraday momentum in other markets (China,
  crypto, VIX futures, KOSPI, coffee 2025). None re-tests FX futures intraday momentum by title. The full
  text was not retrieved (Elsevier).
- JQR price limits (W3125825929, 8 citing works): He-Serra 2022 AJAE (closed; its dissertation form is
  read above), Bunek-Janzen 2024 JCM (USDA realized volatility), and no intraday continuation test.
- Data and code: Benenchia et al. 2025 code on Mendeley Data (zbdgtt8mmt, R scripts; not fetched). No
  KMW, JQR or He data release was found.

## 4. Negative evidence

- KMW Table X: liquidity-demanding fix-reversal trades lose money after costs (AUD -6.53 bp, t -5.86;
  GBP -0.73 bp), and their returns fall at the end of the sample. The post-L leg on CME futures is about
  half its spot size.
- FCA OP46 (via E.0): reversals "disappear from 2015 onwards" on pooled days. Ito-Yamada: intra-month
  contrarian trades are negative after spread before and after the reform. The month-end trade at 1 minute
  is -1.02 bp for EUR/USD.
- JQR / He: the limit continuation is a gap at the open with no measured drift after the first hour.
  Temporary limits are classified ex post.
- AMN: the soybean 30-minute-to-close increment (-0.061 to -0.124) is about 1.3 standard errors, in one
  sample (2010-2021, 122 events), with no out-of-sample test.
- RD4-C1 (3FPS): working paper only; no post-2021 data. The authors offer charm hedging as the explanation
  and do not rule out manipulation. The 0DTE shift to p.m. settlement since 2022 is untested. The paper's
  Figure 1 begins at 16:00 ET, so the part of leg 1 that accrues between 15:00 and 17:00 CT (when Topstep
  must be flat) is unknown.

## 5. Data and cost

- RD4-C1: 1-minute MES/MNQ/MYM bars (owned: MES 2019-05..2025-03, NQ 2010-2024, the research window) plus
  a monthly 3rd-Friday a.m.-settlement calendar (computable; R12 notes the holiday-Thursday rule). No
  purchase is needed.
- FX fix and limit items: no candidate, so no data needed.
- WASDE surprise drift: it needs analyst survey expectations (Reuters/Bloomberg surveys), which the
  program does not own. No published price was checked.

## 6. Prop compatibility (RD4-C1)

Leg 1 starts at the Thursday 17:00 CT reopen and exits at the 08:30 CT open. That is one Topstep trading
day, flat by 15:10 CT. No overnight hold crosses a session boundary, there is no HFT, and automation is
allowed. P06 applies only when a major release falls on the same morning. With 12 events a year, the
Combine consistency rule (best day below 55% of total profit) binds, so this works only as a book
component. Quarterly 3rd Fridays fall inside the roll blackout.

## 7. Overlap with tested mechanisms

- RD4-C1 duplicates R12-C1/C2 (same paper). It differs from E-H3, the quarterly witching short at
  14:30-15:00 CT, which trades the close rather than the SOQ open, and only quarterly. The overnight leg
  overlaps nothing tested.
- The re-dug FX sources map to K3-ldnrev-01, K3-ldnmom-01, K3-ecbfix-01 and K3-mehedge-01, and to E.20
  rows 6E E1-E9. The ag sources map to K6-limitcont-01, K6-wasdepre-01 and K6-wasdepost-01.

## 8. Verdict checks

| verdict | effect | quote | source |
|---|---|---|---|
| E.4/E.22 K3-ldnrev-01 NULL | SUPPORTS | KMW: "we do observe a downward trend towards the end of the sample period"; "for the trader (or liquidity demander), reversal returns turn negative once transaction costs are taken into account"; FCA (E.0): reversals "disappear from 2015 onwards"; Ito-Yamada post-reform month-end EUR/USD +1.21 bp at 15 min after spread, below the M6E hurdle of 2.88 ticks (about 2.6 bp at EURUSD 1.10) | KMW 2024; FCA OP46; Ito-Yamada 2018 |
| E.4/E.22 K3-ldnrev-01 NULL | WEAKENS (slightly) | Osler-Turnbull: "fix-price dynamics are qualitatively unchanged since 2015 despite notable reforms" (theory; data end 2013). The decisive post-2015 pre-registered test (Benenchia et al. 2025, 2015-2023) was not retrieved | Osler-Turnbull WP101R / JBF 2026 |
| E.20 Part A 6E E2/E3 sizes (6.06 / 7.84 6E ticks) and K3-ecbfix-01 NULL | WEAKENS the E.20 sizes; SUPPORTS the null | "CME Futures -1.46 1.80 -1.64 0.11 0.64 -0.56" (Table III): on futures the post-London leg is 0.64 bp against 1.20 bp on spot; demand-side trades are negative after costs | KMW Tables III, X |
| E.8/E.22 K6-limitcont-01 null by inactivity | SUPPORTS | JQR: "Implied prices forecast next day opening prices better than closing prices"; He: "the price jumps to a new level ... The price level remains persistently far from the previous limit after one hour of trading". The move happens before K6's 08:45 CT entry | JQR 2017/2019; He 2022 |
| E.8/E.22 K6-wasdepost-01 null | SUPPORTS | "Soy News -0.028 -0.061** -0.124** (0.027) (0.031) (0.049)": the drift after 30 minutes is about 1.3 SE and needs the survey surprise the program does not own | AMN 2024 |
| V38 (no post-2015 intraday effect on the 17 roots above 1.5 x RT) | WEAKENS | "Panel (b) Futures ... 14.30 -12.89 ... t-stat ... 3.54 -2.40 ... The sample period is 2003 to 2021"; NQ shows the same spike ("Nasdaq 100 (NQ) E-mini futures", Figure 5). 14.30 bp is about 34 MES ticks against a hurdle of about 3. Caveats: working paper, 12 events a year, a leg held overnight within the Topstep day, no data after 2021 | Baltussen-Terstegge-Whelan 2024 |
| V38 (FX and ag rows) | SUPPORTS | No re-dug FX or ag source gives a post-2015, futures-traded intraday effect above the hurdle (KMW futures post-L 0.64 bp; Ito-Yamada 1.21-1.32 bp after spread; limit continuation in the gap) | KMW; Ito-Yamada; JQR; He |

## 9. Fetch log, terms, budget notices

| url | UTC | sha256 (16) | saved path | status | tool |
|---|---|---|---|---|---|
| api.openalex.org works/doi 10.1111/jofi.13306 | 2026-10-18T08:41:07Z | 2d99187276f26611 | pages/RD4/oa_kmw_work.json | ok | curl |
| api.openalex.org cites:W4389903555 / W3024923689 | 08:41:21Z / 08:41:23Z | 15d78491b6c15387 / 4f04382ab9a234d5 | pages/RD4/oa_cites_*.json | ok | curl |
| api.openalex.org cites:W2040846150 / W3125300284 / W3125825929 / W3022362291 | 08:41:37Z-08:41:59Z | de5038b3f82d79b3 / 5563fa23cc42b2d8 / d3b248b91886e9e8 / 39344b6bfb6a0440 | pages/RD4/oa_cites_*.json | ok | curl |
| www.nber.org/terms-and-conditions | 08:43:15Z | 841a8a284c573328 | terms/www.nber.org_terms.html | ok; terms forbid automation, so no NBER content was fetched | curl |
| brandeis.edu .../Brandeis_WP101R.pdf | 08:43:27Z | 4bb9b850bd5eb23d | pages/RD4/osler_turnbull_brandeis_wp101r.pdf | ok | curl |
| researchers.mq.edu.au Benenchia 2025 landing page | 08:43:52Z | 3d6225944eb56971 | pages/RD4/mq_benenchia2025.html | ok | curl |
| researchers.mq.edu.au/files/454662772/...main.pdf | 08:44:03Z | ac9d07cc3f8855e8 | pages/RD4/benenchia_2025_mq_blocked.html | blocked (Cloudflare); scrapling fetch also blocked; Firecrawl out of credits | curl, scrapling, firecrawl |
| api.openalex.org W4405747297 | 08:44:43Z | c7f4779acf03d3b4 | pages/RD4/oa_W4405747297.json | ok (cc-by; OA url is ScienceDirect only) | curl |
| api.openalex.org (search, author, cites:W4386902695) | 08:47:53Z, 08:53:31Z | - | - | throttled (429 after 4 tries) | curl |
| ma.imperial.ac.uk/~jmuhleka/ | 08:49:12Z | - | - | blocked (403) | curl |
| api.semanticscholar.org (4 DOI lookups) | 08:49:18Z-08:49:51Z | - | pages/RD4/s2_*.json | 2 not found (wrong DOI guesses), 1 server error, 1 429 | curl |
| aeaweb.org/conference/2025/program/paper/N7rsBN2N (PDF) | 08:49:49Z | b98e7372007c4329 | pages/RD4/baltussen_terstegge_whelan_2024_aea.pdf | ok | WebFetch |

Terms: appended to terms/terms_log.md for www.nber.org (forbidden), archytas2.birs.ca (robots Disallow /,
forbidden), www.brandeis.edu and researchers.mq.edu.au (no terms page found; robots allow; named pages one
at a time), and api.openalex.org. aeaweb.org follows R1's line (allowed for named pages one at a time).
On-disk E.20 copies were reused without refetching.

Budget notices: at 08:42Z Firecrawl reported "credits are running low" (informational). At 08:43:08Z
Firecrawl search hit its per-minute rate limit. At about 08:45Z Firecrawl scrape returned "Insufficient
credits", and Firecrawl was unusable after that. From 08:47:53Z OpenAlex returned persistent 429s (the
polite pool is shared). RD4 used 4 of its 45 WebSearch calls.

## 10. Unfinished and unverified

- Benenchia-Galati-Lepone 2025 Stage 2 full text (post-2015 reversal correlations, 2015-2023). It is the
  decisive test for K3-ldnrev-01 and was not retrieved.
- Muhle-Karbe, Oomen, Rodriguez Polo 2025 (SSRN only); Ben Zeev-Nathan 2024 and Sizova et al. 2025
  (abstracts only).
- Elaut-Froemmel-Lampaert full text (Elsevier).
- Forward citations of BTW, AMN and He-Serra were not obtained (OpenAlex throttled).
- Evans 2018 per-event size: the x252 vs x12 reading is unresolved.
- The NQ size of the 3FPS is shown in a figure only.
- RD4-C1 duplicates R12-C1/C2. Its overlap with R1 was not checked.
