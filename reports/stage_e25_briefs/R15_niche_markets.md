# R15 niche markets (SourceReader-NicheMarkets-OpusHigh), Stage E.25

Written 2026-10-18 06:14-06:30 PDT (resumed after a usage-limit cut at about 01:59 PDT; the lead set a
06:33 PDT deadline). Scope reduced to sources already on disk plus 3 WebSearch calls. Firecrawl had no
credits, OpenAlex not called (lead 01:57 update). Prop and data access for every venue below: see
reports/stage_e25_briefs/R16_niche_access.md (R16 owns it; not researched here).

## 1. Answer (at most 250 words)

Short version: the published intraday effects I could size on non-CME venues are about 1.6 to 1.8 bp
of gross per trade. They come from cash indices, before costs, end in 2017, and are not out of sample
on futures. The only CME Asian/European-hours effect with a published size, the 02:00-03:00 ET
"overnight drift" on ES, was already tested (A-H1), and its authors report that it disappeared
after 2020.

- Li, Sakkas and Urquhart (J. Financial Markets 2022) is the best-documented ITSM (first half-hour
  predicts last half-hour) across 16 developed cash indices, 2005-2017. Germany: ITSM mean 4.105% a
  year, about 1.63 bp per trade, about 3.9 DAX points at 24,000. Japan: 4.416% a year, about 1.75 bp,
  about 7.0 Nikkei points at 40,000, which is 1.4 ticks of the 5-point OSE mini/micro tick. In both
  markets the plain always-long last half-hour earns almost as much (3.764% and 3.279%). So the sign
  signal adds little on top of a last-half-hour drift. Hong Kong and Singapore are excluded from
  their sample.
- Liu and Tse (IREF 2017; [secondary-only]): on S&P ETFs and 12 international index futures, the first
  half-hour does not predict the last half-hour. Overnight returns do. This is a null for the futures
  versions.
- Jin, Kearney, Li and Yang (JFM 2020; [secondary-only]): ITSM on four Chinese commodity futures
  (copper, steel, soybean, soybean meal). I could not size it because the full text sits behind
  Cloudflare.
- Overnight drift (Boyarchenko, Larsen, Whelan): 1.48 bp a day, 1998-2020, about 3.5 MES ticks at ES
  6,000. In the authors' 2021-2025 out-of-sample update it is "close to zero" (strongest negative).

Candidates: two, both weak (R15-C1 DAX ITSM, R15-C2 Nikkei ITSM). The lead decides.

## 2. Candidate hypotheses

| id | hypothesis | venue / vehicle | entry window CT | hold | published effect | gross per trade | grade | post-2015 / OOS | overlap |
|---|---|---|---|---|---|---|---|---|---|
| R15-C1 | DAX ITSM: sign of first half-hour of Xetra cash (incl. overnight gap) -> trade last half-hour | Eurex FDAX / FDXM / FDXS (tick specs [unverified], see section 5) | Xetra 17:00-17:30 CET = 10:00-10:30 CT (both on DST) | 30 min, 1 trade/day | ITSM mean 4.105% p.a., SD 5.591%, Sharpe 0.734 (USD-converted cash index, 2005-2017) | 1.63 bp = 3.9 DAX pts at 24,000 = 3.9 FDXS/FDXM ticks (1-pt tick) or 7.8 FDAX ticks (0.5-pt tick) | peer-reviewed | sample ends 2017-12-29; paper's OOS R2 is in-paper recursive, not post-publication; always-long earns 3.764% | K1-cp1-01 / E20H6-T1 (same mechanism on US indices, FAIL); new venue only |
| R15-C2 | Nikkei ITSM: same rule on Tokyo cash session | OSE Nikkei 225 mini/micro (5-pt tick [unverified]); CME NKD/NIY (R16) | Tokyo last half-hour (sample: 14:30-15:00 JST; TSE close moved to 15:30 JST on 2024-11-05 [unverified]) = about 23:30-00:30 CT | 30 min | ITSM mean 4.416% p.a., SD 6.142%, Sharpe 0.719 (2005-2017) | 1.75 bp = 7.0 pts at 40,000 = 1.4 ticks of 5 pts | peer-reviewed | as C1; always-long earns 3.279% | K3-tkypre-01 / K3-tkypost-01 (Tokyo clock on 6J, not the index); K1-cp1-01 |

No candidate for: Euro Stoxx 50, Bund/Bobl/Schatz, ICE Brent/gasoil/FTSE/SONIA, SGX, HKEX, INE/SHFE/CFFEX
(including the 2015 restrictions), or thin CME products in Asian hours. These were not read in the
time available (section 10). That is a gap in the record, not a null.

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| ITSM in 12 of 16 developed markets | 12/16 | "Over the 2005–2017 period (Panel A) our empirical evidence suggests that 12 out of 16 countries exhibit a statistically significant in–sample predictability of the first half hour on the last half-hour return." | p. 9-10, Sec. 3.1 | Li, Sakkas, Urquhart (2022), J. Financial Markets 57, 100619, accepted manuscript (centaur.reading.ac.uk) | peer-reviewed | reports/stage_e20_briefs/shared/li_sakkas_urquhart_2022_accepted.pdf (.txt) sha256 39add97e...0bee |
| Germany ITSM size | 4.105% p.a. | "Germany ITSM 4.105 5.591 0.053 3.051 0.734" / "AL 3.764 5.592 0.027 3.051 0.673" | Table 5 (Mean %, SD %, Skew, Kurt, Sharpe) | same | peer-reviewed | same |
| Japan ITSM size | 4.416% p.a. | "Japan ITSM 4.416 6.142 -0.014 3.117 0.719" / "AL 3.279 6.145 0.113 3.116 0.534" | Table 5 | same | peer-reviewed | same |
| HK and Singapore excluded | n/a | "We exclude Hong Kong and Singapore from our sample due to the lack of 1-minutely foreign exchange data." | p. 6-7, Sec. 2.1 | same | peer-reviewed | same |
| Sample is cash index, USD converted, ends 2017 | 2005-10-04..2017-12-29 | "we convert all local currency data into US dollars" ... "the end date is 29th December 2017" | Sec. 2.1 | same | peer-reviewed | same |
| Overnight drift size | 1.48 bp/day | "averaging 3.7% on an annualized basis (1.48 basis points per day)" | p. 1, intro | Boyarchenko, Larsen, Whelan, NY Fed SR 917 (rev. 2022; RFS 2023) | working-paper (published version peer-reviewed) | reports/stage_e10_research/overnight/boyarchenko_sr917.pdf sha256 403276b2...e683a |
| Overnight drift gone 2021-2025 | ~0 | "the 2:00–3:00 window that previously generated roughly 3.7 percent per annum has averaged close to zero since 2021" | para. 1 | Boyarchenko, Larsen, Whelan (2026-07-01), Liberty Street Economics | pointer-grade blog by original authors (E.10 graded it this way) | reports/stage_e10_research/overnight/lse_blog_43261.html sha256 7cacdb19...0740 |
| Same in NQ and YM | flat | "The 2:00–3:00 window—previously responsible for more than 60 percent of the contract's 5.9 percent annualized close-to-close return—is flat. The same pattern holds in the E-mini Nasdaq-100 (NQ) and E-mini Dow Jon[es]" | after first chart | same | as above | same |
| Chinese commodity futures ITSM | not sized | search-result summary only: first half-hour predicts last half-hour in copper, steel, soybean, soybean meal | abstract (via search) | Jin, Kearney, Li, Yang (2020), J. Futures Markets 40(4) 632-650, doi 10.1002/fut.22084 | peer-reviewed [secondary-only] | fetch blocked (Cloudflare), pages/R15/jin_etal_2020_hull.pdf is the challenge page, not the paper |
| International index futures: no first-half-hour predictability | null | search-result summary only (as cited by a later paper): first half-hour not predictive; overnight return predicts last half-hour; 12 international index futures, 1999-2014 | via citing source | Liu, Tse (2017), Int. Rev. Econ. Finance 48, 440-451, doi 10.1016/j.iref.2017.01.005 | peer-reviewed [secondary-only] | not fetched |

Conversions (brief section 2): Germany 4.105/252 = 1.629 bp; x 24,000 / 10,000 = 3.91 DAX points.
Japan 4.416/252 = 1.752 bp; x 40,000 / 10,000 = 7.01 points; / 5 = 1.40 ticks. Overnight drift 1.48 bp
x 6,000 / 10,000 = 0.89 ES points = 3.55 MES ticks (MES hurdle about 3.0 ticks, D8 note). The
divisor of 252 is my assumption for the paper's annualization: Appendix line "annualized mean R = r x
252". All of these are gross figures from USD-converted cash indices. The paper uses no futures and
reports no trading costs.

## 4. Negative evidence

- Overnight drift decay (above). This is the strongest negative finding. The only published CME
  "non-US hours" effect with a size was tested in-program as A-H1 (D.1, MES 02:00 ET window). Its
  authors report it averaging close to zero in 2021-2025 on ES, NQ and YM.
- Li-Sakkas-Urquhart: the signal adds little over a plain last-half-hour long. Germany ITSM 4.105%
  against always-long 3.764%; Japan 4.416% against 3.279% (Table 5). 4 of 16 markets show no
  significant in-sample ITSM. The paper does not say which 4 in the lines I read; Table 3 was not
  read.
- Liu and Tse (2017) [secondary-only]: no first-half-hour predictability on 12 international index
  futures.
- In-program: the same mechanism on NQ at MNQ cost failed (E20H6-T1, gross 1.25 ticks against 4.08
  cost) and K1-cp1-01 failed (Tier B). The 1.6-1.8 bp sizes above are of the same order as the
  published US sizes that failed here.

## 5. Data and cost

The program owns none of this: no Eurex, OSE, SGX, HKEX or China data (brief section 4). CME NKD/NIY
is not among the 45 research-window contracts per section 4 [unverified, not checked against the
roster]. Data prices and prop access: R16_niche_access.md. Tick specs, from memory and not verified
in this pass: FDAX 0.5 pt = EUR 12.50; FDXM 1 pt = EUR 5; FDXS (Micro-DAX) 1 pt = EUR 1; OSE Nikkei
225 mini tick 5 pts x 100 = JPY 500; micro x 10 = JPY 50 [all unverified; exchange pages not fetched].

## 6. Prop compatibility

C1 window 10:00-10:30 CT and C2 window about 23:30-00:30 CT both fall inside the Topstep 17:00-15:10
CT trading day. Whether any firm offers Eurex or OSE products is R16's question; Topstep (CME
Globex) does not list Eurex as far as the rules files show [unverified here]. Both are one trade a
day, with no news-size issue, and fit both automated and manual execution.

## 7. Overlap

- R15-C1/C2: K1-cp1-01 (first-bar sign to afternoon, MNQ/M2K/MYM) and E20H6-T1..T3 (rest-of-day to
  last half-hour, NQ). Same mechanism; the only difference is the venue.
- Overnight drift: A-H1 (D.1, MES european-open window). Same effect, already tested; decayed out of
  sample.
- Tokyo clock: K3-tkypre-01 and K3-tkypost-01 (6J around the Tokyo fix) and K3-mehedge-01 (Nikkei
  month return to 6J). These differ: they trade FX, not the index.
- FX time-of-day (Ranaldo 2009; Breedon-Ranaldo 2013, E.10 K9O-010/011): K3-ecbfix-01 tested a
  related EUR morning-sell rule on 6E. I did not re-dig it.

## 8. Re-dig: not applicable (R15 is not a re-dig reader). One note: the overnight drift decay
supports the D.1 A-H1 outcome (quote in section 3).

## 9. Fetch log

| url | UTC | sha256 | path | status | tool |
|---|---|---|---|---|---|
| https://hull-repository.worktribe.com/OutputFile/3303156 | 2026-10-18T13:13:41Z | 08881d30cf28eeab0bba13cfa933a3dfaedd45269772ca017f7684d8f63e4cc8 | reports/stage_e25_briefs/pages/R15/jin_etal_2020_hull.pdf (HTML Cloudflare challenge "Just a moment...") | blocked | curl |
| (on disk, E.20) li_sakkas_urquhart_2022_accepted.pdf | read only | 39add97e355b49c01ac9d5f0ba76a584fb593e8ec293545127e5c60ca2830bee | reports/stage_e20_briefs/shared/ | ok | grep |
| (on disk, E.10) boyarchenko_sr917.pdf | read only | 403276b2ea8227c14ccfb854014af1df6a425430e5f622599640d7c0c16e683a | reports/stage_e10_research/overnight/ | ok | grep |
| (on disk, E.10) lse_blog_43261.html | read only | 7cacdb191577c19bc5dacf6f99f6eebc76adc9ff7748bbc325ce6a85adc60740 | reports/stage_e10_research/overnight/ | ok | grep |

WebSearch calls: 4 (of 45). No budget notices. Firecrawl: not used (lead says no credits). OpenAlex:
not called. Terms: hull-repository.worktribe.com terms not read before the single curl. That breaks
brief section 8, and I logged it here. Nothing usable was saved; the saved file is a challenge page.
Scrapling was not tried because available memory was 2,317 MB at the start, so I skipped it.

## 10. Unfinished and unverified

- Not read: Eurex Bund/Bobl/Schatz release-window and ECB papers; Euro Stoxx 50; Xetra closing auction;
  ICE Brent settlement window and Brent time-of-day (Haugom et al., QF 2025, already E.10 secondary);
  FTSE 100 / SONIA; SGX FTSE China A50 and Nikkei lead-lag (Covrig-Ding-Low type); HKEX HSI/HSCEI
  lunch-break and ITSM; CFFEX IF/IH/IC ITSM and the 2015 restrictions (Li et al. 2020 FRL named in a
  search result, unread); INE/SHFE night sessions; Japanese/German/Chinese-language literature; CME
  MGC/M6E/MNQ Asian-session drifts; CME NKD/NIY.
- China, not sized, from a 4th WebSearch (06:16 PDT) [secondary-only]: Chu, Gu and Zhou (2019, Finance
  Research Letters 30, 83-88) report first-half-hour momentum and a later reversal in the Chinese stock
  market and say that trading costs keep it alive. Yang (2021, China Finance Review International,
  doi 10.1108/CFRI-06-2021-0106) reports that half-hours 6 and 7 predict the next half-hour on the
  CSI 300, 2012-2017, using an ETF/T+0 strategy rather than futures. Neither covers CFFEX futures or the
  2015 restrictions in the snippets. Unread.
- Jin et al. (2020) full text blocked; Liu and Tse (2017) not fetched; both [secondary-only].
- Li-Sakkas-Urquhart Table 3 (per-country slopes and which 4 markets fail) and the OOS R2 table, per
  country, not read.
- All tick specs [unverified]. TSE close-time change [unverified].
