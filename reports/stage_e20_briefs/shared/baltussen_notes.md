# Baltussen, Da, Lammers, Martens (JFE 2021): shared notes for the 17 E.20 roots

Reader: ProductReader-NQ-OpusHigh (Stage E.20 Part A), written 2026-10-11 (PDT). Other readers cite
this file as `reports/stage_e20_briefs/shared/baltussen_notes.md`.

## Source and provenance

- Paper: G. Baltussen, Z. Da, S. Lammers, M. Martens, "Hedging demand and market intraday momentum",
  Journal of Financial Economics 142 (2021) 377-403, doi 10.1016/j.jfineco.2021.04.029.
- Copy read: `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` (4,443 lines,
  sha256 18cb436e9d18cb3eff3565cddfe85b35fa1c5d5d8bf2afb85df42b6ab49e0465, checked 2026-10-11). Its
  header (lines 1-30) reads "EUR Research Information Portal", "Document Version / Publisher's PDF, also
  known as Version of record", "Published: 01/10/2021". E.13 fetched it on 2026-10-03 from
  https://pure.eur.nl/files/58145484/1_s2.0_S0304405X21001598_main.pdf by Firecrawl after a curl 403
  (`reports/stage_e13_info_sources.md` I-37b and its "Lead note (2026-10-04)": the Scrapling step was
  skipped; the lead accepted the text as the published paper). Not re-fetched here.
- The copy is a PDF-to-markdown conversion. Table cells were read as printed in the file, located by
  grep and line number (Lnnn below). Figure "tables" in the file (for example the yearly values under
  Fig. 2, Fig. 3, and the leveraged-ETF share chart near L2405) are digitised from charts by the
  converter, not printed numbers: **do not cite them as data.**

## Definitions (verbatim, with line numbers)

- Return until the last half hour, L589-L596: "the return of buying at previous day's close and selling
  30 minutes before today's close, r_ROD,t = P_c-30,t / P_c,t-1 - 1" (equation (2); the file writes it as
  `r_{R O D,t}=\frac{P_{c-30,t}}{P_{c,t-1}}-1`).
- Predicted return: the last half-hour return r_LH (L619 onward; equations (5)-(7)); equation (7) is
  `r_{L H,t}=\alpha+\beta_{R O D}\cdot r_{R O D,t}+\varepsilon_{t}`.
- Trading hours, equity, L541-L546: "This corresponds to the trading hours of the underlying for equity
  futures; e.g., we select the observations of the S&P E-Mini between 09:30 and 16:00, as these are the
  trading hours of the S&P 500."
- Outside-hours rule, L625-L632: "We remove all observations outside of the trading hours we consider a
  trading day. This way, the overnight return, which is contained in the first half-hour return, is
  computed using the price at our closing time on the previous day".
- Day filters, L527-L534: "we filter the data by subsequently (i) removing all observations with
  non-positive prices, (ii) removing all non-business days, (iii) removing all days in which the exchange
  closed earlier (such as Memorial Day), and (iv) removing all days in which the total traded volume is
  less than 100 contracts."
- Roll, L525-L527: "We consider the most liquid contract (generally the nearest-to-delivery contract) and
  roll it over when the daily tick volume of the next back-month contract exceeds the current contract."
- Mini contracts, footnote 6 (L601-L604): "To obtain the largest sample, we first consider the standard
  contracts and replace them with the mini versions after its introduction."
- Bonds, L556-L563: hours chosen from volume spikes; "this results in using the regular opening hours of
  the futures as open, and the end of the daily settlement period as close."
- Currencies, L565-L567: "These futures show volume spikes at 8:21 and 15:00, which correspond to the open
  outcry hours of options on those futures; 15:00 also happens to be the end of the daily settlement period
  for these futures."
- Trading strategy (Table 6 caption, L1704-L1712): "Timing strategies η(rONF H) (η(r_ROD)) take a long
  position when the first half hour return rONF H(return until 30 minutes before close r_ROD) is positive,
  and a short position otherwise." ... "For each asset class, a 1/N portfolio is used to combine the
  various futures belonging to the same asset class into one portfolio."
- Costs, L1687-L1695: "Note that we do not consider transaction costs. Given that trading on market intraday
  momentum requires frequent rebalancing, the strategy as presented might not be exploitable to many
  investors after accounting for transaction costs." ... "exploiting the effect in the S&P 500 futures
  yields a positive net Sharpe ratio when we assume transaction cost equal to a tick (a cost level faced
  commonly by advanced investors in the S&P 500 futures market)." (No net figure is printed.)
- Gamma (Table 7 caption L2036-L2041 and text L1970-L1976): Table 7 regresses r_LH,t on r_ROD,t "conditioned
  on the sign of the net gamma exposure (NGE) for the S&P 500 futures" with rows NGE_t-1 >= 0 and
  NGE_t-1 < 0; "Using data from OptionMetrics, we compute the NGE measure from 1996 until the end of 2017.
  We use data from SqueezeMetrics to extend the sample until May 2020." Footnote 7 (L1998): "We have
  verified the computations of SqueezeMetrics using Option- Metrics data over the 2002 to 2017 period,
  yielding virtually identical results." L1975-L1976: "In the period from 1996 until May 2020 there have
  been 2930 days with a negative NGE and 3158 with a positive one."

## Caveats every reader needs

1. **Sample ends 2020-05-01** (Appendix A "End" column) for every root here. Nothing in the paper speaks
   to 2020-06..2024-02.
2. **Gross only.** No table reports costs. Per-trade figures below are derived, not printed.
3. **Time zone of Table 1 for Chicago products is ambiguous.** The caption says "U.S.-listed futures are
   expressed in Eastern Standard Time (EST)", but the currency text (L565-L567) puts the volume spikes at
   8:21 and 15:00, while Tables 1 and A4 print currency hours "7:20 - 14:00"; 7:20-14:00 matches the CME
   FX pit hours in Central time and 8:21/15:00 the same instants in Eastern time. Treat the printed hours
   of rates, FX, grains and livestock as **unresolved between CT and ET**; equity hours (09:30-16:00) are
   unambiguous cash-market hours (ET), that is 08:30-15:00 CT.
4. Table 7 (gamma) is estimated **for S&P 500 futures only**; no other root has a gamma row.
5. Table 2, Table 5 and Table 6 are pooled or 1/N portfolios per asset class; per-market rows exist only in
   Appendix B (regressions; no per-market trading-strategy rows).
6. Appendix B Panel B t-statistics are Newey-West; Panels A and Table 2 cluster on time and market. Stars
   on R2_OOS are the Clark-West test (L740-L760).
7. Coefficients and R2 are multiplied by 100 (captions).

## Root to symbol map and per-root rows (Appendix A and Appendix B Panel B, r_ROD columns)

| E.20 root | Paper symbol (Tickdata) | Sample (Appendix A) | Obs | Hours (as printed) | beta_ROD x100 (t, NW) | R2 % | R2_OOS % | Lines |
|---|---|---|---|---|---|---|---|---|
| NQ | NQ ("NASDAQ 100 futures*") | 1996-04-12..2020-05-01 | 6017 | 09:30-16:00 | 6.36*** (7.97) | 4.10 | 3.76*** | L3234, L3430 |
| RTY | ER ("Russell 2000 ICE/CME*") | 1993-02-08..2020-05-01 | 6746 | 09:30-16:00 | 6.00*** (5.86) | 3.35 | 3.15*** | L3235, L3431 |
| ZT | TU | 1991-01-04..2020-05-01 | 7153 | 08:20-15:00 | 2.07*** (4.45) | 0.71 | 0.70*** | L3262, L3612 |
| ZF | FV | 1988-07-06..2020-05-01 | 7907 | 08:20-15:00 | 2.33*** (6.25) | 1.05 | 0.93*** | L3263, L3613 |
| ZN | TY | 1983-01-05..2020-05-01 | 9296 | 08:20-15:00 | 2.53*** (6.96) | 1.06 | 0.86*** | L3264, L3614 |
| TN | not in the sample | - | - | - | - | - | - | (no TN row in Table 1 or A2) |
| ZB | US | 1982-10-05..2020-05-01 | 9366 | 08:20-15:00 | 2.11*** (3.85) | 0.64 | 0.22*** | L3265, L3615 |
| UB | UB | 2010-02-03..2020-05-01 | 2564 | 08:20-15:00 | 3.39*** (4.36) | 2.35 | -3.40* | L3266, L3616 |
| 6E | EC | 1999-01-06..2020-05-01 | 5284 | 07:20-14:00 | -0.04 (-0.17) | -0.02 | -0.07 | L3322, L3920 |
| CL | CL | 1987-01-06..2020-05-01 | 8336 | 09:00-14:30 | 0.67 (0.25) | 0.03 | -1.04 | L3294, L3769 |
| NG | NG | 1993-01-06..2020-05-01 | 6824 | 09:00-14:30 | 3.02*** (6.15) | 1.04 | 0.92*** | L3296, L3771 |
| GC | GC | 1984-01-05..2020-05-01 | 9044 | 08:20-13:30 | 1.09*** (2.95) | 0.25 | 0.08** | L3289, L3764 |
| ZC | CN | 1982-07-06..2020-05-01 | 9462 | 08:30-13:20 | 0.82** (2.09) | 0.05 | -0.01 | L3299, L3774 |
| ZS | SY | 1982-07-06..2020-05-01 | 9462 | 08:30-13:20 | -0.05 (-0.13) | -0.01 | -0.07 | L3301, L3776 |
| ZL | BO | 1982-07-06..2020-05-01 | 9458 | 08:30-13:20 | 0.03 (0.08) | -0.01 | -0.06 | L3298, L3773 |
| LE | LC | 1984-08-14..2020-05-01 | 8797 | 08:30-13:05 | 0.42 (1.03) | 0.00 | -0.05 | L3308, L3783 |
| HE | LH | 1981-04-03..2020-05-01 | 9499 | 08:30-13:05 | 0.03 (0.06) | -0.01 | -0.06 | L3309, L3784 |

Reading (facts only): r_ROD is positive and significant with a positive, significant R2_OOS for NQ, RTY,
ZT, ZF, ZN, ZB, NG and GC; UB is significant in sample but its R2_OOS is negative; 6E, CL, ZS, ZL, LE and
HE show no predictability; ZC is significant in sample (t 2.09) with R2_OOS -0.01. 16 of the 17 roots are
covered; TN is not.

## Asset-class figures and the derived per-trade gross

Table 6, η(r_ROD) 1/N portfolio per class (gross, L1736 and L1742), with a per-trade figure derived as
annual return / 252. **The 252 factor is an assumption: the paper says "annualized" but does not print
the factor.** Each class portfolio holds one last-half-hour position per market per day, so the daily
portfolio mean is the average per-market trade.

| Class | Avg ret % / yr | Std % | SR | Success | Derived bp per trade (/252) |
|---|---|---|---|---|---|
| Equity index | 6.86 | 3.96 | 1.73 | 0.55 | 2.72 |
| Government bond | 2.16 | 1.33 | 1.62 | 0.55 | 0.86 |
| Commodity | 4.34 | 3.05 | 1.42 | 0.56 | 1.72 |
| Currency | 0.85 | 0.98 | 0.87 | 0.53 | 0.34 |

Table 5 (subsamples, L1661-L1669), beta_ROD x100 (t): equity 5.96 (4.80) in 1974-1999 vs 3.98 (6.65) in
2000-2020; bonds 3.19 (8.38) vs 1.53 (3.61); commodity 1.59 (3.92) vs 1.04 (2.86); currency 1.31 (6.48) vs
0.33 (1.45, not significant). Every class's coefficient is smaller in 2000-2020, and currency loses
significance.

Table 7 (S&P 500 futures, Jan 1996 - May 2020, L2060-L2061): NGE_t-1 >= 0: beta_ROD 0.82 (1.03), R2 0.05;
NGE_t-1 < 0: beta_ROD 6.63*** (4.78), R2 3.58.

## Verbatim rows (copied by script from the file; Lnnn = line in the saved copy)

### Table 1 rows (verbatim; the table has two futures per row)

- L890: `| Future | Symbol | Trading hours | Future | Symbol | Trading hours |`
- L893: `| Dow Jones futures* | YM | 9:30 - 16:00 | Gold futures COMEX | GC | 8:20 - 13:30 |`
- L894: `| S&amp;P 500 futures* | ES | 9:30 - 16:00 | Copper high grade futures COMEX | HG | 8:10 - 13:00 |`
- L895: `| NASDAQ 100 futures* | NQ | 9:30 - 16:00 | Silver futures COMEX | SV | 8:25 - 13:25 |`
- L896: `| Russell 2000 ICE/CME* | ER | 9:30 - 16:00 | Palladium futures NYMEX | PA | 8:30 - 13:00 |`
- L898: `| Amsterdam AEX Index futures | EO | 9:00 - 17:30 | Light crude oil futures NYMEX | CL | 9:00 - 14:30 |`
- L900: `| Swiss Market Index futures | SW | 9:00 - 17:30 | Natural gas futures NYMEX | NG | 9:00 - 14:30 |`
- L902: `| CAC 40 Index futures | CF | 9:00 - 17:30 | Soybean oil futures | BO | 8:30 - 13:20 |`
- L903: `| IBEX 35 Index futures | IB | 9:00 - 17:30 | Corn futures | CN | 8:30 - 13:20 |`
- L905: `| FTSE 100 Index futures | FT | 8:00 - 16:30 | Soybean futures | SY | 8:30 - 13:20 |`
- L912: `| Government bond futures |  |  | Live cattle futures | LC | 8:30 - 13:05 |`
- L913: `| US 2-year T-note futures | TU | 8:20 - 15:00 | Lean hogs futures | LH | 8:30 - 13:05 |`
- L914: `| US 5-year T-note futures | FV | 8:20 - 15:00 |  |  |  |`
- L915: `| US 10-year T-note futures | TY | 8:20 - 15:00 |  |  |  |`
- L916: `| US 30-Year T-bond futures | US | 8:20 - 15:00 | Currency futures |  |  |`
- L917: `| Ultra T-bond futures | UB | 8:20 - 15:00 | Australian dollar futures | AD | 7:20 - 14:00 |`
- L920: `| Euro-Bund 10-yearfutures | BN | 8:00 - 17:15 | Euro FX futures | EC | 7:20 - 14:00 |`

### Table 2 (all rows, pooled per asset class)

- L971: `|  | Panel A Equity futures |  |  | Panel B Bond futures |  |  |`
- L972: `| --- | --- | --- | --- | --- | --- | --- |`
- L973: `| βONFH | 4.86*** (6.52) | 4.72*** (6.46) |  | 1.59*** (4.65) | 1.66*** (4.99) |  |`
- L974: `| βM |  | 2.92*** (4.43) |  |  | 1.97*** (5.93) |  |`
- L975: `| βSLH |  | 9.08*** (4.82) |  |  | 3.11* (1.68) |  |`
- L976: `| βROD |  |  | 4.18*** (7.29) |  |  | 1.90*** (5.97) |`
- L977: `| R2 (%) | 1.49 | 2.74 | 2.45 | 0.2 | 0.66 | 0.64 |`
- L978: `| ROOS2 (%) | -1.71 | 2.22 | 2.88 | -0.05 | 0.56 | 0.60 |`
- L979: `|  | Panel C Commodity futures |  |  | Panel D Currency futures |  |  |`
- L980: `| βONFH | 1.33*** (3.04) | 1.29*** (3.02) |  | 0.91*** (4.58) | 0.91*** (4.61) |  |`
- L981: `| βM |  | 0.85*** (2.73) |  |  | 0.37 (1.60) |  |`
- L982: `| βSLH |  | 2.24 (1.16) |  |  | 0.62 (0.33) |  |`
- L983: `| βROD |  |  | 1.21*** (3.63) |  |  | 0.72*** (4.57) |`
- L984: `| R2 (%) | 0.09 | 0.15 | 0.15 | 0.19 | 0.21 | 0.19 |`
- L985: `| ROOS2 (%) | -0.01 | -0.14 | 0.07 | 0.28 | 0.03 | 0.26 |`

### Table 5 (all rows)

- L1658: `|  | βONFH | R2(%) | βONFH | βM | βSLH | R2(%) | βROD | R2(%) |`
- L1659: `| --- | --- | --- | --- | --- | --- | --- | --- | --- |`
- L1660: `|  | Panel A: 1974–1999 |  |  |  |  |  |  |  |`
- L1661: `| Equity | 3.73*** (2.74) | 0.53 | 3.81*** (2.70) | 6.94*** (4.25) | 9.46*** (4.35) | 3.74 | 5.96*** (4.80) | 3.41 |`
- L1662: `| Bonds | 1.65*** (3.49) | 0.17 | 1.89*** (4.14) | 3.71*** (7.46) | 9.40*** (4.75) | 1.68 | 3.19*** (8.38) | 1.28 |`
- L1663: `| Commodity | 0.83 (1.45) | 0.03 | 0.72 (1.29) | 2.08*** (4.06) | 4.13*** (3.14) | 0.31 | 1.59*** (3.92) | 0.23 |`
- L1664: `| Currency | 1.79*** (7.54) | 0.68 | 1.84*** (7.66) | 0.97*** (2.99) | -4.05 (-1.55) | 0.95 | 1.31*** (6.48) | 0.61 |`
- L1665: `|  | Panel B: 2000–2020 |  |  |  |  |  |  |  |`
- L1666: `| Equity | 4.97*** (6.06) | 1.67 | 4.83*** (6.02) | 2.42*** (3.82) | 8.89*** (4.11) | 2.73 | 3.98*** (6.65) | 2.34 |`
- L1667: `| Bonds | 1.56*** (3.63) | 0.21 | 1.60*** (3.79) | 1.52*** (4.16) | 1.00 (0.35) | 0.47 | 1.53*** (3.61) | 0.47 |`
- L1668: `| Commodity | 1.58*** (3.22) | 0.13 | 1.57*** (3.25) | 0.34 (1.08) | 0.86 (0.28) | 0.14 | 1.04*** (2.86) | 0.12 |`
- L1669: `| Currency | 0.38 (1.29) | 0.03 | 0.37 (1.27) | -0.04 (-0.12) | 3.44 (1.41) | 0.17 | 0.33 (1.45) | 0.04 |`

### Table 6 (all rows)

- L1731: `|  | Avg ret(%) | Std dev(%) | SR | Success | Avg ret(%) | Std dev(%) | SR | Success |`
- L1733: `|  | Panel A: Equity index futures |  |  |  | Panel B: Government bond futures |  |  |  |`
- L1734: `| η(rONFH) | 4.21 | 3.95 | 1.07 | 0.55 | 1.08 | 1.33 | 0.81 | 0.53 |`
- L1735: `| η(rONFH, rROD) | 5.47 | 3.42 | 1.60 | 0.61 | 1.57 | 1.10 | 1.42 | 0.58 |`
- L1736: `| η(rROD) | 6.86 | 3.96 | 1.73 | 0.55 | 2.16 | 1.33 | 1.62 | 0.55 |`
- L1737: `| Always Long | 0.44 | 4.20 | 0.11 | 0.53 | 0.48 | 1.42 | 0.34 | 0.53 |`
- L1738: `| Buy &amp; Hold | 8.76 | 17.29 | 0.51 | 0.54 | 4.07 | 5.96 | 0.68 | 0.53 |`
- L1739: `|  | Panel C: Commodity futures |  |  |  | Panel D: Currency futures |  |  |  |`
- L1740: `| η(rONFH) | 2.48 | 3.03 | 0.82 | 0.54 | 0.93 | 0.97 | 0.96 | 0.54 |`
- L1741: `| η(rONFH, rROD) | 3.29 | 2.56 | 1.29 | 0.56 | 0.89 | 0.86 | 1.03 | 0.54 |`
- L1742: `| η(rROD) | 4.34 | 3.05 | 1.42 | 0.56 | 0.85 | 0.98 | 0.87 | 0.53 |`
- L1743: `| Always Long | -0.68 | 3.50 | -0.19 | 0.51 | 0.49 | 1.13 | 0.43 | 0.52 |`
- L1744: `| Buy &amp; Hold | 1.92 | 13.34 | 0.14 | 0.51 | 0.53 | 7.27 | 0.07 | 0.50 |`

### Table 7 (all rows)

- L2058: `|  | Intercept | βROD,t | R2 (%) |`
- L2059: `| --- | --- | --- | --- |`
- L2060: `| NGEt-1 ≥ 0 | 0.00 (0.17) | 0.82 (1.03) | 0.05 |`
- L2061: `| NGEt-1 < 0 | -0.01 (-0.63) | 6.63*** (4.78) | 3.58 |`

### Appendix A (Tables A1-A4) rows

- L3230: `| Future | Symbol | Start | End | Obs | Times | Group |`
- L3260: `| Future | Symbol | Start | End | Obs | Times | Group |`
- L3287: `| Future | Symbol | Start | End | Obs | Times | Group |`
- L3317: `| Future | Symbol | Start | End | Obs | Times |`
- L3234: `| NASDAQ 100 futures* | NQ | 1996-04-12 | 2020-05-01 | 6017 | 09:30-16:00 | USA |`
- L3235: `| Russell 2000 ICE/CME* | ER | 1993-02-08 | 2020-05-01 | 6746 | 09:30-16:00 | USA |`
- L3233: `| S&amp;P 500 futures* | ES | 1982-04-23 | 2020-05-01 | 9535 | 09:30-16:00 | USA |`
- L3262: `| US 2-year T-note futures | TU | 1991-01-04 | 2020-05-01 | 7153 | 08:20-15:00 | USA |`
- L3263: `| US 5-year T-note futures | FV | 1988-07-06 | 2020-05-01 | 7907 | 08:20-15:00 | USA |`
- L3264: `| US 10-year T-note futures | TY | 1983-01-05 | 2020-05-01 | 9296 | 08:20-15:00 | USA |`
- L3265: `| US 30-year T-bond futures | US | 1982-10-05 | 2020-05-01 | 9366 | 08:20-15:00 | USA |`
- L3266: `| Ultra T-bond futures | UB | 2010-02-03 | 2020-05-01 | 2564 | 08:20-15:00 | USA |`
- L3289: `| Gold futures COMEX | GC | 1984-01-05 | 2020-05-01 | 9044 | 08:20-13:30 | Metals |`
- L3294: `| Light crude oil futures NYMEX | CL | 1987-01-06 | 2020-05-01 | 8336 | 09:00-14:30 | Energies |`
- L3296: `| Natural gas futures NYMEX | NG | 1993-01-06 | 2020-05-01 | 6824 | 09:00-14:30 | Energies |`
- L3298: `| Soybean oil futures | BO | 1982-07-06 | 2020-05-01 | 9458 | 08:30-13:20 | Softs |`
- L3299: `| Corn futures | CN | 1982-07-06 | 2020-05-01 | 9462 | 08:30-13:20 | Softs |`
- L3301: `| Soybean futures | SY | 1982-07-06 | 2020-05-01 | 9462 | 08:30-13:20 | Softs |`
- L3308: `| Live cattle futures | LC | 1984-08-14 | 2020-05-01 | 8797 | 08:30-13:05 | Softs |`
- L3309: `| Lean hogs futures | LH | 1981-04-03 | 2020-05-01 | 9499 | 08:30-13:05 | Softs |`
- L3322: `| Euro FX futures | EC | 1999-01-06 | 2020-05-01 | 5284 | 07:20-14:00 |`

### Appendix B (Tables B1-B4) rows (header rows repeat per panel)

- L3374: `|  | βONFH | R2 (%) | ROOS2 (%) | βTONFH | βM | βSLH | R2 (%) | ROOS2 (%) | βROD | R2 (%) | ROOS2 (%) | ROOS2 (%) |`
- L3375: `| Total | 4.86*** (6.52) | 1.49 | -1.71 | 4.72*** (6.46) | 2.92*** (4.43) | 9.08*** (4.82) | 2.74 | 2.22 | 4.18*** (7.29) | 2.45 | 2.88 |  |`
- L3376: `| USA | 6.92*** (4.67) | 1.80 | -0.87 | 6.50*** (4.49) | 4.47*** (4.22) | 12.58*** (3.66) | 3.84 | 2.60 | 5.99*** (6.66) | 3.46 | 3.09 |  |`
- L3377: `| EU | 4.62*** (5.62) | 1.76 | 1.60 | 4.59*** (5.57) | 2.33*** (3.99) | 5.05*** (2.83) | 2.60 | 2.22 | 3.48*** (7.41) | 2.36 | 2.50 |  |`
- L3378: `| Australasia | 2.97*** (4.30) | 1.17 | 1.03 | 2.90*** (4.29) | 0.39 (0.42) | 8.66*** (3.37) | 1.73 | 1.03 | 2.40*** (5.33) | 1.17 | 0.85 |  |`
- L3426: `|  | βONFH | R2 (%) | ROOS2 (%) | βrONFH | βM | βSLH | R2 (%) | ROOS2 (%) | βROD | R2 (%) | ROOS2 (%) |`
- L3429: `| ES | 5.24*** (3.38) | 0.98 | -1.68 | 4.81*** (3.25) | 6.06** (2.48) | 12.39*** (3.49) | 3.74 | 1.21*** | 6.18*** (4.97) | 3.41 | 2.29*** |`
- L3430: `| NQ | 7.45*** (5.33) | 2.01 | 1.83*** | 6.95*** (5.03) | 5.14*** (4.74) | 11.54*** (3.26) | 4.31 | 3.58*** | 6.36*** (7.97) | 4.10 | 3.76*** |`
- L3431: `| ER | 8.17*** (4.62) | 2.38 | 2.21*** | 7.79*** (4.54) | 3.61*** (3.15) | 12.27** (2.17) | 3.91 | 3.33*** | 6.00*** (5.86) | 3.35 | 3.15*** |`
- L3565: `|  | βONFH | R2 (%) | ROOS2 (%) | βTONFH | βM | βSLH | R2 (%) | ROOS2 (%) | βROD | R2 (%) | ROOS2 (%) |`
- L3567: `| Total | 1.59*** (4.65) | 0.20 | -0.05 | 1.66*** (4.99) | 1.97*** (5.93) | 3.11* (1.68) | 0.66 | 0.56 | 1.90*** (5.97) | 0.64 | 0.60 |`
- L3568: `| USA | 1.91*** (3.57) | 0.30 | -0.11 | 1.96*** (3.71) | 2.77*** (5.23) | 5.25 (1.42) | 1.13 | 0.16 | 2.51*** (6.00) | 1.03 | 0.29 |`
- L3569: `| EU | 1.85*** (2.95) | 0.22 | 0.04 | 1.99*** (3.20) | 1.47*** (3.44) | 2.58 (1.57) | 0.57 | -0.08 | 1.69*** (4.78) | 0.56 | 0.29 |`
- L3570: `| Australasia | 0.00 (0.01) | -0.01 | -0.92 | 0.01 (0.03) | -0.22 (-0.38) | -14.07*** (-6.51) | 1.33 | 0.52 | -0.45 (-1.16) | 0.04 | -0.63 |`
- L3611: `|  | βONFH | R2 (%) | R2OOS (%) | βrONFH | βM | βSLH | R2 (%) | R2OOS (%) | βROD | R2 (%) | R2OOS (%) |`
- L3612: `| TU | 1.37** (2.11) | 0.17 | 0.09* | 1.56** (2.44) | 2.34*** (3.41) | 4.83 (1.52) | 0.80 | 0.26** | 2.07*** (4.45) | 0.71 | 0.70*** |`
- L3613: `| FV | 1.67*** (3.35) | 0.27 | 0.19*** | 1.82*** (3.72) | 2.01*** (3.89) | 8.77*** (2.93) | 1.56 | 1.12*** | 2.33*** (6.25) | 1.05 | 0.93*** |`
- L3614: `| TY | 1.68*** (3.41) | 0.24 | 0.16*** | 1.81*** (3.68) | 2.60*** (5.21) | 7.51*** (4.07) | 1.33 | 0.91*** | 2.53*** (6.96) | 1.06 | 0.86*** |`
- L3615: `| US | 1.77*** (3.62) | 0.21 | 0.09*** | 1.81*** (3.71) | 2.59*** (5.03) | 0.88 (0.15) | 0.65 | -0.43*** | 2.11*** (3.85) | 0.64 | 0.22*** |`
- L3616: `| UB | 2.46*** (2.79) | 0.61 | -2.24 | 2.44*** (2.77) | 3.73*** (3.30) | 15.06** (2.52) | 3.49 | -1.92** | 3.39*** (4.36) | 2.35 | -3.40* |`
- L3710: `|  | βONFH | R2 (%) | ROOS2 (%) | βTONFH | βM | βSLH | R2 (%) | ROOS2 (%) | βROD | R2 (%) | ROOS2 (%) |`
- L3712: `| Total | 1.33*** (3.04) | 0.09 | -0.01 | 1.29*** (3.02) | 0.85*** (2.73) | 2.24 (1.16) | 0.15 | -0.14 | 1.21*** (3.63) | 0.15 | 0.07 |`
- L3713: `| Metals | 1.60*** (4.76) | 0.28 | 0.21 | 1.61*** (4.80) | 0.69* (1.77) | 0.06 (0.05) | 0.31 | 0.10 | 1.19*** (4.50) | 0.26 | 0.31 |`
- L3714: `| Energies | 2.80** (2.43) | 0.35 | 0.03 | 2.75** (2.49) | 1.25 (1.52) | 0.73 (0.13) | 0.42 | -0.07 | 2.10** (2.34) | 0.45 | 0.20 |`
- L3715: `| Softs | 0.25 (0.70) | 0.00 | -0.06 | 0.19 (0.57) | 0.61* (1.70) | 3.50*** (2.62) | 0.09 | -0.14 | 0.65** (2.16) | 0.04 | -0.01 |`
- L3762: `|  | βONFH | R2(%) | R2OOS(%) | βTONFH | βM | βSLH | R2(%) | R2OOS(%) | βROD | R2(%) | R2OOS(%) |`
- L3764: `| GC | 1.43***(2.98) | 0.23 | 0.18***(2.98) | 1.43***(2.97) | 0.68(1.20) | 0.84(0.44) | 0.26 | -0.19 | 1.09***(2.95) | 0.25 | 0.08** |`
- L3769: `| CL | 2.00(0.72) | 0.17 | -0.48 | 2.40(1.12) | -0.06(-0.03) | -13.95(-0.99) | 1.25 | -1.77 | 0.67(0.25) | 0.03 | -1.04 |`
- L3771: `| NG | 3.89***(5.49) | 0.68 | 0.61***(5.21) | 3.74***(5.21) | 1.80***(2.58) | 9.20***(3.44) | 1.34 | 0.94*** | 3.02***(6.15) | 1.04 | 0.92*** |`
- L3773: `| BO | -0.80(-1.40) | 0.02 | -0.06 | -0.86(-1.48) | 1.02(1.20) | 2.80(1.22) | 0.06 | -0.36 | 0.03(0.08) | -0.01 | -0.06 |`
- L3774: `| CN | -0.13(-0.26) | -0.01 | -0.05 | -0.21(-0.41) | 2.89***(3.54) | 0.79(0.42) | 0.21 | 0.03*** | 0.82**(2.09) | 0.05 | -0.01 |`
- L3776: `| SY | -1.17**(-2.17) | 0.06 | -0.04** | -1.23**(-2.26) | 1.68**(2.01) | 3.11(1.19) | 0.15 | -0.45 | -0.05(-0.13) | -0.01 | -0.07 |`
- L3783: `| LC | -0.01(-0.01) | -0.01 | -0.05 | -0.03(-0.04) | 0.01(0.01) | 6.14***(2.77) | 0.19 | 0.01** | 0.42(1.03) | 0.00 | -0.05 |`
- L3784: `| LH | 0.56(0.87) | 0.00 | -0.04 | 0.58(0.89) | -0.98(-1.18) | 3.30*(1.76) | 0.08 | -0.06 | 0.03(0.06) | -0.01 | -0.06 |`
- L3861: `|  | βONFH | R2 (%) | ROOS2 (%) | βTONFH | βM | βSLH | R2 (%) | ROOS2 (%) | βROD | R2 (%) | ROOS2 (%) |`
- L3863: `| Total | 0.91*** (4.58) | 0.19 | 0.28 | 0.91*** (4.61) | 0.37 (1.60) | 0.62 (0.33) | 0.21 | 0.03 | 0.72*** (4.57) | 0.19 | 0.26 |`
- L3915: `|  | βONFH | R2 (%) | ROOS2 (%) | βrONFH | βM | βSLH | R2 (%) | ROOS2 (%) | βROD | R2 (%) | ROOS2 (%) |`
- L3920: `| EC | 0.04 (0.12) | -0.02 | -0.08 | 0.01 (0.04) | -0.47 (-1.25) | 4.07 (1.44) | 0.22 | -0.30 | -0.04 (-0.17) | -0.02 | -0.07 |`
