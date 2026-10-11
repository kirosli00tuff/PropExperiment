# Energy class notes (crude and products): intraday evidence published since 2015

Written by ProductReader-CL-OpusHigh (Stage E.20 Part A), 2026-10-11 10:33-10:55 PDT. Shared
assignment: the energy class (crude and products), the EIA WPSR and API release windows, momentum,
reversal, the settlement window 13:28-13:30 CT, with decay. The NG reader cites this file for class
evidence. Raw pages, fetch log and search log: `reports/stage_e20_briefs/pages/CL/`
(`fetch_log.md`, `search_log.md`). Every number below carries a verbatim quote from a saved full
text, or a grade of [secondary-only] (abstract, repository summary or search result only).

## Price level and tick conversion used throughout

- EIA annual WTI spot (Cushing, RWTC), saved `pages/CL/eia_rwtc_annual.html` (sha256 dac81c9e...):
  "2010's 79.48 94.88 94.05 97.98 93.17 48.66 43.29 50.80 65.23 56.99 2020's 39.16 68.13 94.90
  77.58 76.63 65.39".
- Search-window level P_s = mean of 2019-2023 annual means = (56.99 + 39.16 + 68.13 + 94.90 + 77.58)
  / 5 = $67.35. Backward-window level P_b = mean of 2010-2018 = $74.17.
- MCL: tick $0.01/bbl, 100 bbl, $1.00 per tick (root table). 1 bp of notional = P x 1e-4 $/bbl =
  P / 100 MCL ticks: 0.674 ticks at P_s, 0.742 at P_b. CL (1,000 bbl, $10 per tick) has the same
  ticks-per-bp figure.
- MCL D8 round trip (root table): 4.346 ticks = $4.35 = 6.45 bp at P_s (5.86 bp at P_b). 1.5x
  hurdle: 6.52 ticks = 9.7 bp at P_s.

## Evidence rows

| # | Effect | Rule | Hold | Gross per trade | Sample | Decay | Source | Grade |
|---|---|---|---|---|---|---|---|---|
| EN1 | ROD -> LH (rest-of-day to last half-hour) in CL | r_LH on r_ROD, CL day 09:00-14:30 ET (LH = 14:00-14:30 ET = 13:00-13:30 CT) | 30 min | none: CL's slope is insignificant | CL tickdata 1987-01-06..2020-05-01, 8,336 days, 1-min | OOS R2 negative over the full sample | Baltussen, Da, Lammers, Martens, JFE 2021, Table B3 and Table A3 (on-disk copy) | primary |
| EN2 | EIA-day third half-hour -> last half-hour (USO) | on WPSR Wednesdays (10:30 ET): r3 = log(p 11:00 / p 10:30 ET); long (short) at 15:30 ET if r3 >= 0 (< 0), exit 16:00 ET | 30 min | 4.14% "per annum" (t 1.88); per trade 1.6 bp (x252 reading) or 9.3 bp (per-EIA-day reading); 1.1 or 6.3 MCL ticks at P_s | USO ETF 1-min, 2006-04-10..2019-07-31, 591 Wednesday 10:30 releases | rolling 5-year interaction coefficient "declining trend"; "not observed" in the 2014-2016 plunge | Wen, Indriawan, Lien, Xu, Energy Journal 44(5) 2023 (accepted version, Adelaide repository) | primary |
| EN3 | Non-EIA-day first half-hour -> last half-hour (USO) | r1 = prior 16:00 close to 10:00 ET; same timing as EN2 | 30 min | 1.88% "per annum" (t 2.10); per trade 0.75 bp (x252) or 0.94 bp (per non-EIA day); 0.5-0.6 MCL ticks | same, 2,649 non-EIA days | the predictive source is mostly the overnight component (V34 dropped overnight effects) | same | primary |
| EN4 | Overnight component of r1 -> last half-hour (USO) | r_overnight = prior 16:00 close to 09:30 ET open | 30 min | 2.39% "per annum" (t 2.45) | same | n/a | same | primary (overnight: V34 drop category) |
| EN5 | Pre-EIA order flow and drift | more buyer-initiated orders in the 2 hours before the release on above-forecast inventory days; average price -0.25% before the release | about 2 h | sign known only ex post (inventory surprise); not codeable from bars and calendars | WTI futures (sample years not verified) | n/a | Rousse and Sevi, Energy Journal 40(2) 2019 | secondary-only (HAL Anubis page, FEEM CAPTCHA: full text blocked) |
| EN6 | API and EIA surprise impact, 5-min | surprise relative to Reuters consensus (API) and to API (EIA) moves 5-min returns; EIA effect larger and longer | minutes | not sized in what was read; needs released values | CL futures, about 2013-2014 (search summary) | n/a | Ye and Karali, Energy Economics 59 (2016) 349-364 | secondary-only (AgEcon and UGA bot checks) |
| EN7 | Post-WPSR reversion | price "reverts quickly after the initial reaction"; activity lasts about 25 min | minutes | unsized in what was read | WTI futures around EIA reports | n/a | Geman and Li, Journal of Energy Markets 11(2) 2018 | secondary-only (Birkbeck copy restricted; risk.net paywall; not fetched) |
| EN8 | Intraday overreactions (1 min to 1 h), energy most | large moves followed by proportional reversals; more and larger in COVID | up to 1 h | unsized in the abstract | 20 commodity futures, 2019-11-20..2020-06-03 | sample is 6.5 months | Borgards, Czudaj, Van Hoang, Resources Policy (ISSN 0301-4207), LMU Open Access record 97149 | secondary-only (abstract page saved; no full text) |
| EN9 | Brent intraday seasonality (time-of-day long-short) | long and short at particular times of day; "some" strategies give positive CAPM alphas after costs and margin | intraday | unsized in the abstract | ICE Brent tick data 2010-01..2021-10, 1-min | n/a | Haugom, Ouyang, Smith-Meyer, Stordal (and coauthors), Quantitative Finance 2025, Glasgow eprint 363707 | secondary-only (PDF HTTP 401) |
| EN10 | Settlement window 13:28-13:30 CT | no post-2015 study of systematic returns in or around the window found; the only study found is the 2020-04-20 negative settlement (closing pressure about $7/bbl in the authors' model, TAS predatory trading for the rest) | n/a | n/a | one event | n/a | Ge, Kang, Tang, Yang (AEA 2023 session paper) | secondary-only (search summary); a null for the window |
| EN11 | Passive-fill adverse selection in CL (execution, not alpha) | resting 1-lot limit orders in a simulator | n/a | 518 of 625 CL fills adverse (82.9%) | CL Jun24, one day 2024-04-23, TT simulator | n/a | Lalor and Swishchuk, arXiv 2409.12721, Table 2 | primary |

Quotes (verbatim, from the saved files):
- EN1, `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` lines 3673-3680 (Table B3
  caption): "Market intraday momentum: individual commodity futures results. ... Samples range from
  April 1981 to May 2020. ... Adjusted R2, R2OOS, and slope coefficients are multiplied by 100." Line
  3769 (CL row; columns beta_ONFH, R2, R2OOS, beta_TONFH, beta_M, beta_SLH, R2, R2OOS, beta_ROD, R2,
  R2OOS): "| CL | 2.00(0.72) | 0.17 | -0.48 | 2.40(1.12) | -0.06(-0.03) | -13.95(-0.99) | 1.25 |
  -1.77 | 0.67(0.25) | 0.03 | -1.04 |". Line 3294 (Table A3): "| Light crude oil futures NYMEX | CL |
  1987-01-06 | 2020-05-01 | 8336 | 09:00-14:30 | Energies |". The same table's other energy rows
  (lines 3770-3772): HO beta_ROD "2.40***(4.95)", R2OOS "0.44***"; NG "3.02***(6.15)", "0.92***"; XB
  "1.92**(2.04)", "-0.00". Crude is the one energy contract with no ROD effect.
- EN2-EN4, `pages/CL/wen_etal_2023_ej_adelaide.txt` (pdftotext of the accepted version, sha256
  110ec616...): data, lines 346-350: "We collect USO ETF data at a one-minute frequency from Refinitv
  Tick History. The sample period is from April 10, 2006, when the ETF started trading, to July 31,
  2019." Line 391-393: "During our sample period, 685 weekly EIA crude oil reports were released, but
  we focus on 591 EIA announcements that fall on Wednesdays at 10:30." Table 1 (line 1635 on), Panel A
  [1]: "r3 0.038**" "[2.12]", "Obs. 591", "Adj. R2(%) 3.10". Text, lines 502-516: "The coefficient for
  r3 is 0.038 with an adjusted R2 of 3.10%. This can be interpreted as a 1% increase in the third
  half-hour return leads to a 0.038% increase in returns by the end of the trading day." Strategy,
  section 3.5: "we take the long (short) position at the beginning of the last half-hour of the
  regular trading session if the intraday predictor is positive (negative) and then close the
  position at the end of each trading day." Table 6: "Panel E: using r3 as a trading signal on EIA
  days ... 4.14* [1.88] 0.21 19.54 0.66 10.09 58"; "Panel B: using r1 as a trading signal on non-EIA
  days ... 1.88** [2.10] 0.20 9.28 ... 57"; "Panel C: using r_overnight ... 2.39** [2.45] 0.20 11.98
  ... 58"; "Panel D: using r3 as a trading signal on non-EIA days ... -0.36 [-0.37]". Text: "an even
  higher average return of 4.14% per annum and a Sharpe ratio of 19.54." Decay, section 4 (lines
  1101-1110): "the intraday momentum phenomenon is strong and statistically significant over our
  sample period, albeit with a declining trend. ... during the crude oil price plunge between 2014 and
  2016, the intraday return predictability is not observed." No transaction cost is applied anywhere
  in the paper (grep "transaction cost": none).
- EN11, `pages/CL/lalor_swishchuk.txt`, Table 2: "2024/04/23 CL Jun24 625 518 107" (total LO fills,
  adverse, non-adverse), "over active trading trading hours (8:30 EST - 16:00 EST)".

## Reading for the class

1. Momentum: the one primary CL-futures result (Baltussen, CL row) is a null for ROD -> LH: slope
   0.67 (x100), t 0.25, OOS R2 -1.04%. Products differ: HO and NG show the effect, XB weakly in sample
   only. Any energy feature built on r_ROD should expect nothing from CL on this evidence.
2. EIA window: the only sized post-2015 evidence (Wen et al. 2023) is on USO, not CL futures, and its
   exit (15:30-16:00 ET = 14:30-15:00 CT) is after CL's 13:30 CT settlement, in thin post-settlement
   trading. It is the published rule behind the library's K4-eiamom-01 (r3 = 09:29-09:59 CT on
   standard WPSR days, entry 14:30, exit 14:59 CT), so it is not a new feature. The per-trade size is
   ambiguous: the paper does not say how "per annum" is formed. Under either reading (1.6 bp or 9.3 bp
   per trade, 1.1 or 6.3 MCL ticks at $67.35), it is below 1.5x the MCL D8 round trip (6.52 ticks).
   It is gross, significant only at 10% in the strategy table, declined over 2006-2019 and was absent
   in 2014-2016.
3. API window: no primary intraday study of the Tuesday API bulletin since 2015 was retrieved. Ye and
   Karali (2016) study API surprises against consensus (needs released values; not codeable here).
   API's own page (Wayback capture 2016-04-10, saved `pages/CL/api_wsb_wb20160410.html`): "The weekly
   reports are scheduled for release every Tuesday afternoon at 4:30 pm Eastern. If Monday is a
   Federal holiday, the reports are scheduled for release on Wednesday afternoon." The 2014-04-06
   capture says only "Published weekly every Tuesday afternoon (published Wednesday afternoon in the
   event of a Monday holiday)." The 4:30 pm time before 2016 rests on Ye and Karali's AAEA paper as
   summarised by a search result [secondary-only].
4. Reversal: post-release reversion within about 25 minutes (Geman and Li 2018) and intraday
   overreactions (Borgards et al. 2021) are unsized in what could be read, and both are minute-scale,
   shorter than v2's 60-minute minimum hold.
5. Settlement window 13:28-13:30 CT: no systematic study found; unknown, not rejected. The window
   itself is unchanged 2010-2024 (`reports/stage_e16_settlement.md` rows for CL).
6. Pre-announcement drift: Kurov, Sancetta, Strasser, Wolfe (ECB WP 1901, saved
   `pages/CL/kurov_etal_ecbwp1901.pdf`) covers E-mini S&P 500 and 10-year note futures only; its
   release list has no EIA petroleum report (grep finds no crude, oil, petroleum or EIA row). It is
   no evidence for CL either way.
7. The Aalto thesis (ZN reader, `shared/aalto_thesis_notes.md`) has no commodities: "It has no
   commodities: no energy, metals, grains or livestock."
8. Costs: CL passive fills were adverse 82.9% of the time on the one simulated day; market orders
   only (as v2) is consistent with this.

## Gaps (blocked or not read)

Rousse and Sevi 2019 (HAL Anubis anti-AI page; FEEM CAPTCHA), Ye and Karali 2016 (AgEcon and UGA
bot checks), Geman and Li 2018 (restricted, paywalled), Wen, Gong, Ma, Xu 2021 Economic Modelling
(paywalled; not fetched), Haugom et al. 2025 (Glasgow PDF 401), the Hull repository item 3303156
(Cloudflare; title not known). Each is a gap in the record, not evidence of absence.
