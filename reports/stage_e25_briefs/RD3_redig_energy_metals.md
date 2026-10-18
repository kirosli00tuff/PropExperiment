# RD3 re-dig: energy and metals sources (E.20 product_CL/NG/GC, energy class notes)

Reader RD3 (RedigReader-EnergyMetals-OpusHigh), Stage E.25. Run 1 started 2026-10-18 01:39 PDT
(cut about 01:44 by a usage limit); run 2 06:21 PDT (cut about 06:33); run 3 (this one) 11:16 PDT,
continuing from the partial file and pages/RD3/. Verified quotes from runs 1-2 are kept unchanged.
FINAL as of 11:25 PDT (see section 10 for what is not done).

## 1. Answer (at most 250 words)

The deeper reading leaves the energy and metals verdicts standing. Three new primary sources were
read beyond E.20. (a) Alturki (2020) / Alturki and Kurov (J. Futures Markets 2022): the 30-minute
post-API crude return predicts the (-60,-1) pre-EIA return (slope 0.17, R2 0.04, 2011-2019, only
in low liquidity and attention). Converted, the gross is about 4.5 MCL ticks per trade, under the
4.75-tick hurdle, in-sample. It is the published form of K4-apipre-01 (Tier B fail). (b) Gu, Kurov
and Stan (WP Aug 2025; J. Futures Markets 2026, doi 10.1002/fut.70104): over 1,120 storage
releases 2002-2023 the unconditional (-90,-5) NG return is -0.092% (s.e. 0.036), about 2.8 MNG
ticks at $3.00, far under 8.03; this supports the K4-ngpre-01 NULL. (c) Awartani et al. (2024,
re-read deeper): after FOMC surprises, the 5-10 minute gold-futures bar responds about 3.4 times
the 0-5 minute bar (-0.073 vs -0.021 percent per 1-sd survey surprise, 2007-2020). That is a
continuation on the surprise, which the program does not observe; with gold's own first-bar sign
as the proxy (K5-fomc-01) the proxy is weak, consistent with the E.22 NULL. One reader-built
variant (rate-futures first-bar sign as the surprise proxy, trade MGC 13:05-13:10) is listed for
the lead as a candidate with a perfect-sign gross of about 10.5 MGC ticks at $1,800, an upper
bound, not a published trading result. No forward citation of the E.20 sources replicates or
extends a tradable intraday result. V38 and V39 are supported.

## 2. Candidate hypotheses

Two rows. Neither is a published trading rule that clears the hurdle; both are recorded so the lead
can rule. Zero clean candidates is the honest headline.

| id | hypothesis | instruments | window CT | trades/yr | published effect | gross per trade (micro ticks) | grade | owned | overlap | note |
|---|---|---|---|---|---|---|---|---|---|---|
| RD3-C1 | FOMC statement day: sign of the 13:00-13:04 rate-futures return (ZT or ZN; price up = looser) as the surprise proxy; trade MGC in the same direction 13:05 to 13:10 (or 13:15) | MGC (signal ZT/ZN) | 13:04 signal, 13:05-13:10 | 8 | Awartani et al. 2024 Table 4: 5-10 min bar -0.073% per 1-sd FOMC survey surprise (t -12.4), 0-5 min bar -0.021%, 2007-2020 | perfect-sign upper bound 10.5 at GC $1,800 (14.0 at $2,400) vs hurdle 6.13 | peer-reviewed (AAM) | yes (ZT/ZN/GC bars, FOMC calendar) | K5-fomc-01, K2-fomcpost-01, K8 lead-lag | reader construction; proxy unvalidated; Smales and Yang (2015) say most of the reaction is done in 90 s; possible bar-label convention; about 112 events 2010-2024, about 10 in the research window |
| RD3-C2 | WPSR Wednesday: sign of the CL return 15:30-16:00 CT Tuesday (30 min after the API release); trade MCL in that direction 08:30-09:29 CT Wednesday (-60,-1 before the 09:30 WPSR) | MCL | Tue 16:00 signal, Wed 08:30-09:29 | about 44 | Alturki (2020) Table 2: slope 0.17 (s.e. 0.04), R2 0.04, N 385, 2011-01..2019-08 | about 4.5 (derived) vs hurdle 4.75 | thesis (published JFM version not read) | yes (CL bars, WPSR/API calendar) | K4-apipre-01 (same mechanism, different windows) | re-parameterization of a failed member; under the hurdle even in-sample; effect only in low-liquidity periods |

Conversions (RD3 derivations, not published numbers; the lead checks):
- RD3-C1: for a sign trade with the sign known exactly, E[gross] = |beta| x E|S| = 0.0732% x 0.798
  (normal approximation for a standardized surprise) = 0.0584% = 5.84 bp. At GC $1,800/oz (the 2020
  sample end level, an assumption): 5.84 x 1,800 / 10,000 = $1.05/oz = 10.5 MGC ticks ($0.10 tick).
  At $2,400/oz: $1.40/oz = 14.0 ticks. A real proxy with sign accuracy p gives (2p - 1) of this; at
  p = 0.75 the gross is half (5.3 ticks at $1,800, under 6.13). The survey surprise is mostly zero
  in 2009-2015 (zero lower bound), so E|S| over the zero-bound years is overstated.
- RD3-C2: E|R_API| = 0.51% x 0.798 = 0.41%; gross = 0.17 x 0.41% = 0.069% = 6.9 bp; at CL $65/bbl:
  $0.045/bbl = 4.5 MCL ticks (hurdle $0.0475/bbl = 4.75 ticks).

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Post-API 30-min CL futures return predicts the pre-EIA (-60,-1) return | slope 0.17 (s.e. 0.04), R2 0.04, OLS; robust 0.14 (0.05) | "Panel A of Table 2 shows that the 30-minute return of oil futures post-API release predicts the 60-minute return of oil futures prior to the EIA oil inventory announcements." Table 2 Panel A: "Slope \| 0.17*** (0.04) \| 0.14*** (0.05)" ... "R2 \| 0.04 \| 0.02" | Essay 2 s.2.4.1 and Table 2 (md lines 3294-3305, 3678-3725) | Alturki, S. (2020), Three Essays on Energy Markets, WVU PhD dissertation, essay 2, https://researchrepository.wvu.edu/etd/7647; published as Alturki and Kurov, J. Futures Markets 42 (2022), doi 10.1002/fut.22264 | thesis (published version peer-reviewed, not read) | pages/RD3/alturki_2020_wvu_diss_firecrawl.md (sha256 90c9b25c7e12ef06...) |
| Dispersion of the post-API return | sd 0.51 (%), N 385, 2011-01..2019-08 | "Post-API Return \| 385 \| 0.003 \| 0.51 \| -2.36 \| 2.01" | Essay 2 Table 1 | same | thesis | same |
| Predictability only in low liquidity and low attention | n/a | "our results indicate that the predictive power of the post-API oil futures return for the pre-EIA oil return is significant only when the liquidity in the oil futures market is low." | s.2.4.3 | same | thesis | same |
| Split-sample stability | n/a | "we split the sample in two equal sub-samples and repeated the entire analysis of Table 2. The results in both subsamples are similar to those reported in the paper." | fn 28 | same | thesis | same |
| Predictor strategy (API actual minus Bloomberg consensus; NOT owned data) | annualized Sharpe 0.67 (-60,-1), 0.62 (-90,-1), 0.54 (-120,-1) | "\| (-60 min, -1 min) \| 0.67 \| 2.1 \|" ... "\| (-120 min, -1 min) \| 0.54 \| 1.19 \|" | Table 8 | same | thesis | same |
| No drift before the API release itself | n/a | "Figure 3 shows no evidence of statistically significant drift prior to the API oil inventory announcements" | s.2.4 | same | thesis | same |
| Published abstract claims OOS predictor | n/a | "We also construct a predictor that can predict inventory surprises and preannouncement returns in-sample and out-" (abstract truncated in Crossref) | Crossref abstract | Alturki and Kurov (2022) JFM, doi 10.1002/fut.22264 | peer-reviewed [secondary-only] | pages/RD3/cr_alturki_jfm.json |
| Unconditional NG pre-release drift (-90,-5), 2002-2023 | intercept -0.092 (s.e. 0.036), N 1,120 | Table 8 row 1: "-0.092 (0.036)**  -0.107 (0.037)***  -0.129 (0.049)***"; notes: "calculated from 90 minutes before announcement to 5 minutes before announcement ... The sample period is from May 2002 through December 2023 and contains 1,120 announcements." (row label garbled by the PDF font; the model is "R_t = a0 + b1 ...", so row 1 is a0) | Table 8, txt lines 1296-1322 | Gu, Kurov, Stan (Aug 2025 draft), Trader Attention and Market Reaction to Fundamental News, business.ucdenver.edu working paper; published J. Futures Markets 2026, doi 10.1002/fut.70104 | working-paper (published version peer-reviewed, not read) | pages/RD3/gu_kurov_stan_2025wp_ucdenver.pdf (sha256 4f699da16795d11f...) and .txt |
| Pre-release drift exists, in the direction of the surprise | about 0.2% on Thursday releases | "For the regular Thursday announcements, this drift amounts to about 0.2% on average, and the overall market move before and after the announcement is about 1% on average." | s.3, txt lines 549-552 | same | working-paper | same |
| Drift tied to the (ex post) surprise | slope -0.020 (s.e. 0.005) per unit surprise | "We find evidence of a significant pre-announcement drift in the natural gas futures market, consistent with Gu and Kurov (2018)." | s.4.4, txt lines 866-868; Table 8 row S | same | working-paper | same |
| E.20 NG E1/E2 numbers re-checked | after 2011 2.91%/yr, Sharpe 0.50 | "In the more recent period, this has declined to only 3% and a Sharpe ratio of 0.5, which do not withstand transaction and funding costs." | accepted version txt line 724 (E.20 copy) | Prokopczuk, Wese Simen, Wichmann (2021) Energy Journal 42(2) | peer-reviewed | reports/stage_e20_briefs/pages/NG/prokopczuk_wesesimen_wichmann_2021_ej_accepted.pdf.txt |
| E.20 NG E4 number re-checked | Sharpe 0.84 (analyst predictor, not owned) | "This strategy produces an annualized Sharpe ratio of 0.84 in the full" | Gu dissertation md line 393 (E.20 copy) | Gu and Kurov (2018) via Gu WVU dissertation | thesis | reports/stage_e20_briefs/pages/NG/gu_2016_wvu_dissertation_firecrawl.md |
| FOMC gold response, 0-5 and 5-10 min bars | -0.021267 (t -3.61), -0.073231 (t -12.42), % per 1-sd surprise | Table 4 Panel A: "FOMC monetary surprises (-1) -0.021267* -3.606783 / FOMC monetary surprises (-2) -0.073231* -12.41975"; text: "the adjustment 10 minutes after the shock is significantly threefold higher than after 5 minutes" | Table 4 (txt line 1486ff); s.5 (line 321) | Awartani, Hussain, Virk (2024) IRFA 103486, AAM, https://ndownloader.figshare.com/files/65204829 | peer-reviewed | reports/stage_e20_briefs/pages/GC/awartani_etal_2024_irfa_aam.pdf (sha256 095015c35d6de6ad...) |
| Sample and surprise definition | 2007-01-02..2020-12-31; S = (announced rate - mean expectation)/sd | "The sample period is from January 2, 2007, through December 31, 2020."; "Assume A_k,t to be the announced FOMC monetary rate and E_k,t is its mean market expectation; then the surprise in the announcement is" | Table 4 notes; s.4 | same | peer-reviewed | same |
| Subsamples | 2007-12..2009-06: (-1) -0.002 (t -0.15), (-2) -0.120 (t -8.64); 2020: (-1) -0.155 (t -8.06), (-2) -0.076 (t -3.96) | "FOMC monetary surprises (-1) -0.002066 -0.148500 -0.155231* -8.061715 / FOMC monetary surprises (-2) -0.120288* -8.644550 -0.076188* -3.956697" | Table 5 Panel A | same | peer-reviewed | same |
| Asymmetry | 23 bp looser vs 4 bp tighter per 1 se | "One standard error of monetary policy shock could move gold returns by 23 basis points if the policy lowers rates more than expected. However, it changes gold returns by only four basis points if the policy is tighter" | s.5, lines 935-937 | same | peer-reviewed | same |
| FOMC is the main driver of gold intraday jumps (5-min data 2010-2018) | n/a | "FOMC Rate Decision is the most dominant and statistically significant US scheduled macroeconomic news."; "Using high-frequency data sampled at 5 minutes for a relatively long sample period covering eight years from 1st January 2010 to 31st March 2018." | slides, txt lines 166-167, 336-337 | Sobti Gupta, N. (2024), What causes intraday price jumps and co-jump in Gold, IGPC-IIMA conference slides, https://www.iima.ac.in/sites/default/files/2024-03/Neharika%20Sobti%20-%20Intraday%20price%20jumps.pdf; published IRFA 105 (2025) 104380 | working-paper (slides; no sized drift) | pages/RD3/sobti_2024_iima.pdf (sha256 19091fec1796d453...) |
| Osler and Turnbull: London 4 pm FX fix dealer model (forward citation of Caminschi and Heaney) | n/a | "This paper develops a model of dealer conduct - and misconduct - at the London 4 pm fix, a major currency market benchmark." | abstract | Osler and Turnbull (2017) Brandeis IBS WP 101R; published as "Dealer misconduct and price dynamics at the fix", J. Banking and Finance (2026), doi 10.1016/j.jbankfin.2026.107641 | working-paper | pages/RD3/osler_turnbull_wp101r.pdf (sha256 4bb9b850bd5eb23d...) |

Forward citations (OpenCitations index v2, run 2 at 2026-10-18 13:2x UTC; titles from Crossref):
Prokopczuk et al. 2021 (10.5547/01956574.42.2.mpro) 5; Gu and Kurov 2018 (10.1002/fut.21926) 18;
Alturki and Kurov (10.1002/fut.22264) 3; Wen et al. 2023 (10.5547/01956574.44.4.zwen) 3;
Caminschi and Heaney 2014 (10.1002/fut.21636) 25; Aspris, Foley, O'Neill 2020 (10.1002/fut.22120)
12; Smales and Yang 2015 (10.1016/j.irfa.2015.01.017) 25. 88 distinct citing DOIs, titles in
pages/RD3/cr_fwd_1..5.json. Read or screened: none is a replication or extension of a tradable
intraday rule. Relevant titles: Gu-Kurov-Stan 2026 (read, above); "Drift Begone! Release policies
and preannouncement informed trading" (Kurov, Sancetta, Wolfe, JIMF 2022; full text not found);
"Natural Gas Storage Forecasts: Is the Crowd Wiser?" (Fernandez-Perez, Garel, Indriawan, EJ 2020;
abstract: crowd forecasts add nothing beyond professional consensus; not a trading result);
"Did the New Fix, Fix the Fix?" (Nilsson 2015, SSRN 2657767; no open copy found); "To fix or not to
fix, the Fix" (PBFJ 2024, FX 4 pm fix, pre-registered; not in scope); "Monetary policy and
uncertainty resolution in commodity markets" (Gu, Kurov, Stan, FRL 55, 2023; implied volatility,
not direction; abstract via search result only, paywalled); "Latent Petroleum News and Asset
Prices" (SSRN 2026, 10.2139/ssrn.7617680; abstract: headline surprises capture only part of the
WPSR response; window response, not pre-positionable).

## 4. Negative evidence

- NG storage pre-release (K4-ngpre-01 family): Prokopczuk et al. after 2011, "declined to only 3%
  and a Sharpe ratio of 0.5, which do not withstand transaction and funding costs." Gu-Kurov-Stan's
  unconditional (-90,-5) mean over 2002-2023 is -0.092%: 2.76 MNG ticks at $3.00/MMBtu (0.092% x
  3.00 = $0.00276; tick $0.001), 3.7 ticks at $4.00, against the 8.03-tick hurdle. Their drift is
  in the direction of the surprise, which is known only after the release.
- API to WPSR (K4-apipre-01): in-sample gross about 4.5 MCL ticks, below 4.75; "significant only
  when the liquidity in the oil futures market is low"; sample ends 2019-08.
- FOMC gold (K5-fomc-01): Smales and Yang (2015), as quoted by E.20: "with the majority of the
  reaction complete within 90-seconds" (E.20 quote; RD3 could not refetch the text: Curtin's old
  handle now redirects to the new repository home). This conflicts with Awartani's 5-10 minute
  peak. Awartani's 2020 subsample has the first bar larger than the second (-0.155 vs -0.076),
  i.e. faster adjustment in the latest year sampled. Awartani's survey surprise is not owned.
- Gold PM fix (K5-pmfix-01): no post-2015 study of a tradable fix-window drift was found. Aspris
  et al. (E.20 E2) "no significant leakage prior to the start of the fix"; the 2014 Caminschi and
  Heaney leakage applies to the telephone fix replaced 2015-03-20.

## 5. Data and cost

- RD3-C1: ZT or ZN 1-minute bars, GC price path (MGC hurdle), FOMC statement calendar: all owned
  (section 4). No purchase. The survey surprise (Bloomberg/Reuters consensus) used by Awartani is
  not owned and not needed for the proxy version; no price quoted.
- RD3-C2: CL 1-minute bars, WPSR calendar, API release times (owned calendars per K4-apipre-01).
  The paper's stronger predictor (API minus consensus) needs API values and consensus, not owned.
- No Databento pages were read; no spend.

## 6. Prop compatibility

- RD3-C1: 13:05-13:15 CT entry and exit, flat well before 15:10 CT. P06 news rule: the trade sits
  inside the FOMC release window; Topstep's news restrictions must be checked by the lead per firm
  (not re-read here; see R9). Two orders per event; no HFT.
- RD3-C2: entry 08:30 CT Wednesday, exit 09:29 CT, before the WPSR at 09:30 CT; signal from the
  prior day's 15:30-16:00 CT bars; no overnight hold. Flat by 15:10 CT. Manual or automated.

## 7. Overlap with tested mechanisms

- RD3-C1: K5-fomc-01 (gold's own 13:00-13:04 sign, 13:05-13:15 hold; Tier A, E.22 NULL): same
  window and target, different signal (rate futures instead of gold). K2-fomcpost-01 (rates, 13:29
  to 15:04): different window and target. K8 lead-lag family (MES->MGC flight, MCL->6C): same
  cross-market structure, different event. Release-minute momentum group (index line 269).
- RD3-C2: K4-apipre-01 (signal 15:24/15:39 closes, trade 07:30-09:29): same mechanism; the paper's
  signal is 30 min post-API and its main window (-60,-1). A re-parameterization of a failed member.

## 8. Verdict checks (re-dig)

- K4-ngpre-01 (E.4a Tier A; E.5 confirmation NULL): SUPPORTS. Prokopczuk et al.'s quotes re-check
  exactly in the saved accepted version; after 2011 the published gross is 2.91%/yr = 5.6 bp per
  event = 1.68 MNG ticks at $3.00. Gu-Kurov-Stan (2025/2026), a later paper by the Gu-Kurov
  authors, find the unconditional (-90,-5) mean -0.092% over 2002-2023 (2.76 MNG ticks at $3.00).
  Quote: "-0.092 (0.036)**" (Table 8). No forward citation replicates the trading result.
- K4-apipre-01 (E.4a Tier B, fail): WEAKENS slightly (does not overturn). Alturki (2020) is a
  primary source the E.20 class notes lacked ("no primary intraday study of the Tuesday API
  bulletin since 2015 was retrieved"). Its windows differ from the member's; even in-sample the
  derived gross is about 4.5 MCL ticks, at or under the hurdle. Quote: "the 30-minute return of oil
  futures post-API release predicts the 60-minute return of oil futures prior to the EIA oil
  inventory announcements."
- K4-eia* members (K4-eiafade-01, K4-eiamom-01; Tier B): SUPPORTS. No source read sizes a
  post-WPSR fade or a 14:30 continuation; the 2026 latent-news paper describes the release-window
  response, not a later drift. Wen et al. (2023, E.20) checks unchanged.
- K5-fomc-01 (Tier A; E.22 confirmation on GC bars NULL): SUPPORTS, with a caveat. Awartani's
  5-10 min continuation is conditional on the survey surprise; gold's own first-bar response is
  small (-0.021 vs -0.073) and in 2020 reverses the ordering, so the first-bar sign is a weak proxy,
  consistent with the NULL. Quote: "the adjustment 10 minutes after the shock is significantly
  threefold higher than after 5 minutes." The caveat (an untested rate-futures proxy) is RD3-C1.
- K5-pmfix-01 (screened, excluded on the mean-hold floor): SUPPORTS. No post-2015 source shows a
  fix-window drift; Osler and Turnbull is the FX 4 pm fix. Quote (Aspris et al. 2017, E.20): "there
  is no significant leakage prior to the start of the fix".
- C1/C1b (NG replication FAIL): SUPPORTS. No source read reports an NG intraday pattern at 60-min or
  end-of-day horizons that would clear 8.03 MNG ticks; the only documented NG intraday effect is the
  storage-day drift, which decayed after 2011 and is small unconditionally. Quote: "which do not
  withstand transaction and funding costs" (Prokopczuk et al.).
- V38 (no published post-2015 intraday effect on the 17 roots above 1.5 x RT): SUPPORTS for CL, NG
  and GC. The two near-misses found (Alturki, about 4.5 vs 4.75 MCL ticks, sample to 2019; the
  Awartani perfect-sign upper bound, which is not a tradable published rule) do not breach it.
- V39 (commodity event drift closed as a standalone stage): SUPPORTS. The event-drift effects read
  are either ex post (surprise-signed), under the hurdle, or decayed.

## 9. Fetch log

| url | UTC | sha256 (16) | saved path | status | tool |
|---|---|---|---|---|---|
| https://researchrepository.wvu.edu/etd/7647 (Alturki 2020) | 2026-10-18T08:43Z (file mtime 01:43 PDT) | 90c9b25c7e12ef06 | pages/RD3/alturki_2020_wvu_diss_firecrawl.md | ok | firecrawl (run 1) |
| https://researchrepository.wvu.edu/robots.txt, about page | 2026-10-18T08:42Z | a0a51283a93c222a / 087bf385cf92bb2b | pages/RD3/wvu_robots.txt, wvu_about.html | ok | curl (run 1) |
| munin.uit.no item 26973 (title not known) | 2026-10-18T08:54Z | c9840c68d1609c33 | pages/RD3/munin_26973.html | blocked (JS challenge page) | curl (run 1) |
| hull-repository.worktribe.com item 3303156 | 2026-10-18T08:55Z and 13:29Z | 87299e073dba157e / 056ee0c6df583e16 | pages/RD3/hull_3303156*.md | blocked (Cloudflare) | scrapling get, fetch (runs 1-2) |
| api.opencitations.net index v2 citations (7 DOIs) | 2026-10-18T13:24Z-13:25Z | see files | pages/RD3/oc_*.json | ok | curl (run 2) |
| api.crossref.org works (88 citing DOIs, source DOIs, author queries) | 2026-10-18T13:23Z-13:31Z | see files | pages/RD3/cr_*.json | ok | curl (run 2) |
| business.ucdenver.edu working paper PDF (Gu, Kurov, Stan, Aug 2025; exact URL not recorded by run 2) | 2026-10-18T13:32Z | 4f699da16795d11f | pages/RD3/gu_kurov_stan_2025wp_ucdenver.pdf | ok | curl (run 2) |
| Brandeis IBS WP 101R (Osler, Turnbull; exact URL not recorded by run 2) | 2026-10-18T13:31Z | 4bb9b850bd5eb23d | pages/RD3/osler_turnbull_wp101r.pdf | ok | curl (run 2) |
| https://api.crossref.org/works/10.2139/ssrn.2657767 | 2026-10-18T18:18Z | aed36f32f8ca43e8 | pages/RD3/cr_newfix.json | ok | curl |
| https://www.efmaefm.org/.../2024-Lisbon/papers/EFMA_COMPLETEMANU_NSOBTI.pdf | 2026-10-18T18:18:32Z | n/a | (deleted 503 page) | blocked (HTTP 503) | curl |
| https://www.iima.ac.in/robots.txt | 2026-10-18T18:18:4xZ | 64f3d63e6379bb68 | pages/RD3/iima_robots.txt | ok | curl |
| https://www.iima.ac.in/sites/default/files/2024-03/Neharika%20Sobti%20-%20Intraday%20price%20jumps.pdf | 2026-10-18T18:18:53Z | 19091fec1796d453 | pages/RD3/sobti_2024_iima.pdf | ok | curl |
| https://espace.curtin.edu.au/robots.txt and .../bitstream/20.500.11937/40677/4/227313.pdf | 2026-10-18T18:20:02Z | b4d171f8c4bfcba9 | pages/RD3/curtin_robots.txt | blocked (301 to new repository home; PDF empty, deleted) | curl |
| api.crossref.org works for 4 DOIs (JIMF 2022, EJ 2020, JFM 2022 finmar, JFM 2026) | 2026-10-18T18:20Z | see files | pages/RD3/cr_10_*.json | ok | curl |
| https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.jimonfin.2022.102718 | 2026-10-18T18:20:46Z | 65ab993d12c5c2cc | pages/RD3/s2_driftbegone.json | throttled (429) | curl |
| https://api.crossref.org/works/10.2139/ssrn.3502748 | 2026-10-18T18:21Z | 7bf13c65d2c84892 | pages/RD3/cr_driftbegone_ssrn.json | ok (no abstract) | curl |

Terms: OpenCitations and Crossref (terms_log lines 127-128), WVU (line 48), ucdenver (line 157),
Brandeis (line 20), IIMA and Curtin (appended this run). WebSearch calls this run: 5 of 15
(results used only as pointers to URLs; no search summary is cited as text). OpenAlex not called. Firecrawl not
called this run. Semantic Scholar: one call, 429. No budget notices.

## 10. Unfinished and unverified

- Smales and Yang (2015) full text not refetched (Curtin repository moved); its "90-seconds" quote
  rests on E.20's reading.
- "Drift Begone!" (Kurov, Sancetta, Wolfe, JIMF 2022): no open copy found (S2 429, no Crossref
  abstract, SSRN blocked). Whether it covers the EIA storage release is unverified.
- Published versions of Alturki and Kurov (JFM 2022) and Gu-Kurov-Stan (JFM 2026) not read; the
  numbers come from the dissertation and the August 2025 draft.
- Exact source URLs of the ucdenver and Brandeis PDFs were not recorded by run 2 (hashes are).
- Awartani's bar-label convention (whether "(-2)" is the 5-10 min bar or a label offset) is not
  stated in the text found; the 5-10 min reading is the authors' own wording.
- Forward citations of Awartani et al. (2024) and Sobti (2025) were not pulled.
- Hull item 3303156 and munin item 26973 stay blocked; titles unknown.
