# Stage E.23 P1.2 mechanism memo: M7_MONTHEND (month-end and turn-of-month flows)

Worker: MechanismReaderM7_MONTHEND-OpusHigh. Written 2026-10-17, 02:16 to about 02:30 PDT.
Brief: reports/stage_e23_briefs/brief_mechanism.md. Pages and logs: reports/stage_e23_briefs/mech_pages/M7_MONTHEND/
(fetch_log.md, query_log.md). Pages Stage E.20 already saved were reused from reports/stage_e20_briefs/pages/ and not refetched.
No market data was opened. No member was run.

Members (from the module docstrings):
- **K2-monthend-01** (strategy/members/k2/monthend.py, k2/_month_end.py), on ZT ZF ZN TN ZB UB. It buys unconditionally on
  two event dates each month, N-1 and N, where N is the last EC-CAL rates trade date of the month. The intraday trade runs
  07:20 to 15:04 CT. Under E.23 the entry is the trigger day's settlement. A 5-day hold from **N-1** therefore contains
  day N plus about 4 days of the next month. A 5-day hold from **N** contains only the next month's first 5 days.
- **K3-mehedge-01** (strategy/members/k3/mehedge.py), on 6J only. On ME(m), the month's last FX trade date, it SELLs 6J if
  the Nikkei's month-to-date log return R_eq > 0 and BUYs if R_eq < 0. The trade runs from T_L-60 to T_L-3, where T_L is the
  London 4pm fix. Under E.23 the entry is the settlement of ME(m), after the fix.

## 1. Evidence table

| key | citation | URL | saved path | sha256 (raw file) | verbatim quote (location) | claim supported |
|---|---|---|---|---|---|---|
| HS19-a | Hartley, J. and K. Schwarz (2019), "Predictable End-of-Month Treasury Returns", Wharton Rodney L. White Center WP 17-19, Nov 22 2019 | https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2019/12/17-19.Schwarz.pdf | reports/stage_e20_briefs/pages/ZN/hartley_schwarz_2019.pdf (.txt) | 56403762378f606f595dcce11afcf1f1eaccf8810237c58999f653a230a32809 | "Average returns are positive and highly significant in the last few days of the month, and are not significantly different from zero at other times." (Abstract, p.1) | Direction: long Treasuries is paid only in the month's last days. Elsewhere in the month, about zero |
| HS19-b | same, Table 8 (futures) | same | same (.txt lines 1513-1537) | same | "10-Year 0.09*** 0.14*** 0.17*** 0.18*** 0.22*** 0.20*** -0.06 -0.08* -0.10** -0.04 / (0.01) (0.02) (0.02) (0.03) (0.03) (0.03) (0.04) (0.04) (0.05) (0.05)"; 5-Year "0.07*** 0.10*** ... (0.01) (0.01)"; 30-Year "0.15*** 0.21*** ... (0.02) (0.03)"; notes: "100 times the average returns on long positions on Treasury futures contracts held only over the last t days of the month ... The sample period is from 1990 to 2018. Standard errors are shown in brackets." (Table 8, p.32) | Magnitude, futures, last day (t=1, close of N-1 to close of N): 5y +7 bp (se 1), 10y +9 bp (se 1), 30y +15 bp (se 2) of price. 1990-2018. t ≈ 7 to 9 |
| HS19-c | same, Table 1 (cash, zero-coupon) | same | same (.txt lines 1243-1270) | same | Last t days: "2-Year 0.03*** 0.05*** 0.06*** ..."; "10-Year 0.14*** 0.20*** 0.25*** 0.24*** 0.28*** ..."; All except last t days: "10-Year 0.19 0.13 0.07 0.10 0.06 ... (0.14) (0.13) (0.13)" (Table 1, p.25) | Rest of the month (about 20 days) for 10y: +0.06 to +0.19%/month, not significant. Cash 2y last day: +3 bp (se 1) |
| HS19-d | same, Table 4 subperiods and text | same | same (.txt lines 436-442, 1356-1366) | same | "The estimates in the final period, from 2015-2018 are smaller than most of the other periods, but they remain significant." (p.8). 2015-2019, last 2 days panel: "10-Year 0.13*** 0.08 0.27*** ... (0.04) (0.07) (0.10)"; 2010-2014: "10-Year 0.11* 0.28*** ... (0.07) (0.10)" (Table 4, p.27) | Decay: weaker but still significant in 2015-2019. 10y last day 2015-2019: +13 bp cash (se 4) |
| HS19-e | same, futures text | same | same (.txt lines 798-822) | same | "Annualized returns on the longest maturity futures contracts, held only over the last few days of the month, can exceed 3 percentage points." (Section 4.2, p.15) | The effect carries over to CBOT Treasury futures |
| ERSV20-a | Etula, E., K. Rinne, M. Suominen and L. Vaittinen (2020), "Dash for Cash: Monthly Market Impact of Institutional Liquidity Needs", Review of Financial Studies 33(1), 75-111 | https://acris.aalto.fi/ws/portalfiles/portal/40965155/hhz054.pdf | mech_pages/M7_MONTHEND/etula_etal_2020_rfs_dashforcash.pdf (.txt) | 7f66ea4a5aa2b9285fc210f6cd0c73924ede5bd4ff5d788d369f390b1b9939f4 | "In the U.S. Treasury market, the shorter 1-day settlement convention permits liquidity-driven selling until the close of T−2." (p.77); "Treasury yields tend to rise and remain elevated until T−2 ... Once the liquidity related selling pressure eases, yields decline on the back of recovering prices." (p.78) | Mechanism: month-end cash-need selling depresses Treasury prices until T-2, and prices then recover. The text gives a direction only (Figure 3, 1995-2013). No post-T magnitude in the text |
| ERSV20-b | same, Table 4 and Section 2.2 | same | same (.txt lines 1199-1245) | same | "T −8 to T −4 yield change −0.189 (−2.48)" (52-week bill), "−0.186 (−2.58)" (3-year note); "the reversal in yields in the bond market seems to be highest on T−1 after the selling pressure in the Treasury bond market has come to an end." (Table 4 and Section 2.2, p.91) | Reversal inside the month-end window: T-8..T-4 against T-3..T-1, Newey-West t ≈ -2.5, 1995-2013. Speaks to days before T, not after |
| HMM26 | Harvey, C., M. Mazzoleni and A. Melone, "The Unintended Consequences of Rebalancing", EDHEC seminar slides, 2026-03 (authors' slides; paper not fetched) | https://www.edhec.edu/sites/default/files/2026-03/slides_EDHEC_Michele%20Mazzoleni%20%281%29.pdf | mech_pages/M7_MONTHEND/hmm_rebalancing_edhec_slides.pdf (.txt) | c21b1a0fd14b8e8c3a1a8e00b29c68c97bd99b79c4b154e09bddd9ce49843a8a | "When stocks are overweight, funds sell stocks/buy bonds, leading to 17 bps decrease in equity returns of and 3 bps increase in bond returns"; "Rebalancing pressures are largely temporary, resolving almost completely within two weeks" (slide 2); "We use daily returns on S&P 500 and 10-year Treasury note futures from 1997-09-10 to 2023-03-17" (slide 20) | Conditional month-end rebalancing pressure in 10y futures: +3 bp next day when stocks are overweight. The pressure reverses within about 10 trading days. No t-stat in the quoted lines. Slides only |
| BP26 | "Two Calendar Effects at the Month Boundary", Beyond Passive (Substack), 2026-04-05 (practitioner blog; secondary) | https://beyondpassive.substack.com/p/two-calendar-effects-at-the-month | mech_pages/M7_MONTHEND/beyondpassive_month_boundary.html (.txt) | 34f7bfc9081ff0d5f10d9cf747d4c50d7636e3ae5e41bd2070f919e1fca78130 | "TLT drifts steadily downward through the first seven trading days, reaching a cumulative trough near −0.30%. It then flattens mid-month and rallies sharply in the final three to five days."; "trading day 3 stands out as the weakest single day for TLT (t = −2.9)"; "All analysis in this article uses actual ETF data from August 2002 onward"; "he stopped trading the bond seasonality during a 2023–2024 flat stretch — and missed a strong recovery in 2025" | Practitioner evidence for early-month weakness, i.e. reversal after N, in a long-duration Treasury ETF, 2002-2025. Not peer reviewed. The 2023-2024 flat stretch suggests decay or variance |
| JVA10 | Jalonen, E., S. Vähämaa and J. Äijö (2010), "Turn-of-the-month and intramonth effects in government bond markets", Research in International Business and Finance 24(1), 75-81 | https://ideas.repec.org/a/eee/riibaf/v24y2010i1p75-81.html | mech_pages/M7_MONTHEND/ideas_jalonen_etal_2010_riibaf.html (.txt) | 6dd806eb4fd3780cc47c64cdaa34b8770a975d6160edd9d16ab6bdc26d814b7a | "Using data on the 2-year and 10-year US Treasury Notes and German government bonds, we document a modest TOM effect in government bond returns." (abstract only) | A turn-of-month effect exists in Treasury notes. Window and size unknown (abstract only) |
| LSE26 | Dyer, H., M. Fleming and O. Shachar, "Treasury Trading at the Close", Liberty Street Economics, 2026-09-22 | https://libertystreeteconomics.newyorkfed.org/2026/09/treasury-trading-at-the-close/ | reports/stage_e20_briefs/pages/ZN/lse_index_strike.html (.txt) | 2036a2f067b9c0639d01ede8cb3dd0991f57dd0dea5874cdd06819c6c2336553 | "The share of activity around 4 p.m. has since increased from an average of 11.6 percent in 2021 to 20.4 percent in 2025." (month-end days); "We conjecture that the increased concentration of activity may reflect the growth of assets managed relative to fixed-income indexes, many of which are rebalanced at month-end." | The index-rebalancing flow behind HS19 has grown through 2025. Volume only, no returns |
| MP13 | Melvin, M. and J. Prins (2013), "Equity hedging and exchange rates at the London 4pm Fix", BlackRock WP, ECB Third FX Workshop, Nov 2013 (published J. Financial Markets 2015 [unverified]) | https://www.ecb.europa.eu/events/pdf/conferences/131216/Third_FX_Workshop_MELVIN_PRINS_Equity%20hedging%20and%20exchange%20rates%20Nov%202013.pdf | reports/stage_e20_briefs/pages/6E/melvin_prins_2013_ecb_wp.pdf (.txt) | 606a6c402741982f4f81423f6df3ca055348156fe728d54976807579168d587c | "Equity market appreciation over the month predicts currency depreciation before the end-of-month fix" (Abstract, p.1); "a 10% equity appreciation leads to 14 basis points of currency depreciation" (p.13); "on end of month days, the sum of the two coefficients tell us that 72% of the price movement in the hour leading up to the fix has been reversed before noon of the next day." (p.16-17); sample "20040428-20121231", ten currencies including JPY (p.16) | The K3 mechanism. The pre-fix move is about 14 bp per 10% equity move. **Reversal**: 72% of the pre-fix hour move is undone by noon of the next day. Horizon under 1 day. Pooled across 10 currencies, 2004-2012 |
| KMW24 | Krohn, I., P. Mueller and P. Whelan (2024), "Foreign Exchange Fixings and Returns Around the Clock", Journal of Finance 79(1) (WRAP accepted version) | https://wrap.warwick.ac.uk/177333/1/WRAP-foreign-exchange-fixings-returns-around-clock-Mueller-2023.pdf | reports/stage_e20_briefs/pages/6E/krohn_mueller_whelan_2024_jf_wrap.pdf (.txt) | a7975f26f9b42b837a0b2a6c1474a63e448fff5a0fa7957bc2233b1c0302e6a3 | "The U.S. dollar appreciates in the run-up to foreign exchange fixes and depreciates thereafter, tracing a W-shaped return pattern around the clock." (Abstract, p.1) | Intraday reversal after fixes (dollar demand, unconditional). Intraday only. Gives no 5-20 day evidence |
| CHR22 | Camanho, N., H. Hau and H. Rey, "Global Portfolio Rebalancing and Exchange Rates", NBER WP 24320 rev. Dec 2020 (published RFS 35(11), 2022) | https://www.nber.org/system/files/working_papers/w24320/revisions/w24320.rev1.pdf | mech_pages/M7_MONTHEND/camanho_hau_rey_nber_w24320rev1.pdf (.txt) | 7a7f011f2ccc6efc1f09c1c70ce19be3540a73a45162074db56eb6aee4890f0a | "excess returns on the foreign equity market portion of the investor portfolio should be partially repatriated" (p.4, .txt line 241); "even the second quarterly lag of foreign excess returns ... has some explanatory power for fund rebalancing" (p.25-26) | Analog: equity outperformance leads to a lagged rebalancing outflow over quarters. That flow is in the same currency direction as the K3 signal. Quarterly fund-level flows, with no 5-20 day return figure |

## 2. Per-member paragraphs

### K2-monthend-01 (ZT ZF ZN TN ZB UB; BUY on N-1 and on N)

- **Strength:** strong for the N-1 trigger at the 5-day horizon, because the hold contains day N (HS19-b, t ≈ 7 to 9 in
  futures, 1990-2018, still significant in 2015-2019 per HS19-d). Weak and disputed for the N trigger at 5 days. Moderate
  at best for either trigger at 20 days.
- **Direction:** N-1 trigger: same side as the member (long). N trigger at 5 days: the literature disagrees. One side finds
  zero or a recovery (same side): HS19-a/c, ERSV20-a. The other finds early-month weakness (opposite side): BP26, HMM26.
  N trigger at 20 days: no directional evidence beyond the unconditional term premium (HS19-c).
- **Reason:** Hartley and Schwarz attribute the excess Treasury return in the month's last days to "temporary spikes in
  investor demand for specific securities due to window dressing and portfolio rebalancing", led by life insurers buying
  on benchmark index rebalancing dates (HS19-a). The demand is a recurring calendar flow, not information. Its price effect
  therefore sits in the last 1 to 5 days and is, by their account, absent the rest of the month: "not significantly
  different from zero at other times" (HS19-a, HS19-c). Etula et al. add a second, liquidity-driven flow. Month-end cash
  needs force Treasury selling up to T-2 (1-day settlement), and prices then recover into T (ERSV20-a, ERSV20-b). Both
  channels pay a long position held from N-1's settlement into N. Neither shows a post-N continuation in its quoted text.
  Two newer sources point to a partial giveback after N: Harvey, Mazzoleni and Melone (slides) and the practitioner
  TLT study. HMM26 says rebalancing pressure in 10y futures "resolv[es] almost completely within two weeks". BP26 says TLT
  drifts down about 0.30% over the first seven trading days (day 3 t = -2.9, 2002-2025). LSE26 shows the month-end index
  flow has grown through 2025, so the mechanism is still active. The return evidence after 2019 is limited to BP26's
  remark that 2023-2024 was flat.
- **Horizon:** 5 days. For N-1 it is supported through day N. For N the evidence is mixed. 20 days: a 20-trading-day hold
  from N ends about when the next month's last-days window opens, usually at or before the next N-1 settlement on a
  19-23-day month. It therefore captures little of the next month-end premium. This is my reading of the calendar against
  HS19, not a published test. No source tests a 20-day post-month-end hold.
- **Magnitude (per event, gross, price return):** the last day (N-1 settlement to N settlement) in futures, 1990-2018
  (HS19-b): ZF-like 5y +7 bp (se 1). ZN-like 10y +9 bp (se 1); E.20 converted this to about 6.3 ZN ticks
  (reports/stage_e20_briefs/shared/rates_class_notes.md R8). ZB-like 30y +15 bp (se 2). For ZT, cash 2y gives +3 bp
  (se 1) (HS19-c); there is no 2y futures row. For TN and UB there is no row; the nearest are 10y and 30y. In cash 10y the
  last day is +14 bp in 1990-2018 and +13 bp (se 4) in 2015-2019 (HS19-d). After N, the next 4 to 19 days are about zero
  in HS19-c (10y "all except last t days" +0.06 to +0.19%/month, se 0.12 to 0.14, the whole rest of the month).
  BP26 gives about -30 bp in TLT over days 1-7, in a longer-duration ETF than any CBOT contract except UB.
  HMM26: +3 bp next day in 10y futures, conditional on stocks being overweight. Post-publication decay: HS19-d finds
  2015-2019 weaker but significant. BP26 reports 2023-2024 flat.
  Caveat on HS19-b: the futures columns for t = 7 to 10 turn negative (-0.06 to -0.10) right after +0.20 at t = 6. That
  implies about -26 bp on the 7th-to-last day, which the cash tables do not show. A roll or delivery-month artifact is
  possible [unverified]. The columns for t = 1 to 6 do not depend on it.

### K3-mehedge-01 (6J; SELL if Nikkei month-to-date return > 0, BUY if < 0, on ME(m))

- **Strength:** none: intraday-only for the documented effect. The equity-hedge flow concentrates in the hour before the
  London 4pm fix and reverses within a day (MP13, KMW24). There is a weak analog for a same-side move over quarters
  (CHR22).
- **Direction:** the literature disagrees by horizon. Under one day: reversal of the fix-hour move, i.e. opposite side to
  the member (MP13; KMW24 for fixes generally). Over quarters: same side as the member through lagged rebalancing outflows
  (CHR22). That is fund flows, not a tested 5-20 day return. Nothing found speaks to 5 or 20 days.
- **Reason:** Melvin and Prins identify month-end re-hedging by international equity managers. After a month of foreign
  equity gains, a hedged manager must sell more of the foreign currency at the 4pm fix. This produces "currency
  depreciation before the end-of-month fix" (MP13). They argue the flow carries no information about the currency and
  that liquidity providers "absorb the trades for a premium and then lay them off over time". Their regression shows "72%
  of the price movement in the hour leading up to the fix has been reversed before noon of the next day" on month-end
  days (MP13, p.16-17). The E.23 entry is at 6J settlement after the fix. A 5-day hold would therefore sit in the reversal
  window. Part of the reversal may already be in the settlement price, and the source does not split it by hour. KMW24
  documents the same post-fix reversal for the dollar at every fix, intraday. The only multi-period channel found is
  Camanho, Hau and Rey (CHR22). Funds partially repatriate foreign equity excess returns, with lags up to two quarters.
  For foreign holders of Japanese equities after a Nikkei rise, this implies yen selling, the same side as the member.
  But the evidence is quarterly fund-level flows, not a daily or weekly 6J return.
- **Horizon:** neither 5 nor 20 days is tested. MP13 covers about 1 day. CHR22 covers quarters.
- **Magnitude:** pre-fix hour, pooled across 10 currencies, 2004-2012: about 14 bp of depreciation per 10% monthly equity
  rise, with 72% reversed by noon the next day (MP13; no JPY-only figure in the quoted lines). No published per-event
  return exists for 5 or 20 days. Decay: KMW24 reports fix reversals present across its 21-year sample (abstract). There is
  no month-end-specific decay figure.

## 3. Query log

Full table in reports/stage_e23_briefs/mech_pages/M7_MONTHEND/query_log.md. There were 14 WebSearch calls, from 02:17 to
02:22 PDT. Queries 12, 13 and 14 added no new relevant source.

| # | query (short) | kept |
|---|---|---|
| 1 | Etula et al. Dash for Cash pdf | ERSV20 |
| 2 | Hartley Schwarz end-of-month published | none new (HS19 already on disk) |
| 3 | Camanho Hau Rey global portfolio rebalancing pdf | CHR22 |
| 4 | turn-of-month Treasury bond futures first days reversal | JVA10 (abstract) |
| 5 | month-end FX rebalancing yen days after | none new (practitioner) |
| 6 | end-of-month Treasury returns 2019-2024 persists | BP26; LSE posts (volume) |
| 7 | Harvey Mazzoleni Melone Unintended Consequences pdf | none |
| 8 | KMW fixings month-end next-day reversal | none new |
| 9 | Harvey 2025 rebalancing month-end NBER | HMM26 slides |
| 10 | Liao Zhang hedging channel pdf | fetched, no month-end content, not used |
| 11 | HMM NBER full text | none |
| 12 | month-end yen hedge ratio Nikkei study | none new |
| 13 | turn-of-month FX currency futures academic | none new relevant |
| 14 | Treasury negative first week after month-end, academic | none new |

## 4. Not verified or not reached

- Harvey-Mazzoleni-Melone full paper: not found (searches 7, 9, 11). HMM26 numbers are from the authors' slides. No
  t-stats were quoted. The reversal statement "within two weeks" covers the equity/bond pair, conditional on the
  rebalancing signal.
- Jalonen et al. 2010: abstract only (Elsevier). The TOM window and magnitude are unknown.
- Etula et al. Figure 3: the post-T path of Treasury yields is shown only in a figure. The text gives a direction (recovery
  after T-2) with no number for days T+1 onward.
- Melvin-Prins 2015 journal version: the publication is [unverified]. The 2013 ECB-workshop version was used. No JPY-only
  coefficient or reversal figure was extracted.
- No source tests a 5- or 20-trading-day hold entered at the settlement of N-1, N or ME(m). Horizon statements for
  20 days are my reading of HS19's within-month profile, not published tests.
- Treasury month-end returns after 2019 (peer reviewed): none found. The only post-2019 return remark is BP26
  (practitioner).
- HS19-b futures columns t = 7 to 10: an unexplained sign change, possibly a roll artifact [unverified].
- Liano and Kelly (1995, Global Finance Journal), "Currency futures and the turn-of-month effect": seen in search
  results only, no abstract. Not read. It is unconditional and not the K3 hedge signal.
