# DF1: second reader on shortlist C1, noise-area intraday momentum (Zarattini, Aziz, Barbon, "Beat the Market")

Reader: DF1-NoiseAreaMomentum-OpusHigh (rerun after a usage-limit cut at about 06:35 PDT; built on the
pages the first run saved). Written 2026-10-18 11:20-12:00 PDT. No market data read, nothing bought.

## 1. Answer (at most 250 words)

The lead's numbers check out against the paper's local copy (R10's file, "This Version: September 22,
2025"): $0.09/share net per trade at a time-average SPY price of $247; costs $0.0035/share commission
plus $0.001/share slippage per side; Table 5/6 "Unconditional 2620 12 5.34" (2,620 is the number of
*traded* days, not calendar days); 7,668 trades from May 2007 to April 2024 (about 451 a year); FAQ Q13
futures table for 2007-01..2024-09 with S&P500 SR 1.32, Nasdaq 1.23, Russell 0.45. The futures cost
assumption is not stated. The paper never says whether a "trade" means a round trip or a fill.
Independent replications put the number of round trips at about half the paper's count.

Nine independent tests were found. Four of them cover the period after publication (2024-05). On the
S&P side (SPY, ES) every one shows the edge at or below zero. Brusco ES, the paper's exact rule:
-0.61 bp per trade net, Sharpe -0.07. VigorTas ES, post-publication: -$6.44 per MES trade net.
Paz: out-of-sample Sharpe 0.39, t 0.54. Delgado: Sharpe -0.46 from 2025-09 to 2026-08. The Nasdaq side
is still positive in two tests. VigorTas NQ, after publication: +$13.90/day per MNQ, t 1.37, gross
about 10.3 NQ points = 41 MNQ ticks per trade. Chuk (SSRN abstract only) reports MNQ 2020-2026 at
+$10.26/day net, in-sample, one of 2 survivors among 144 tests. Before publication, gross per trade is
about 14.8 MNQ ticks and about 4.2 MES ticks (VigorTas, fixed size, one contract). The research window
(2025-04..2026-06) is no longer blind: the third-party results above already cover it.

## 2. Candidate hypotheses

One candidate. It restates R10-C1 for MNQ; there is no new member.

| id | hypothesis | instruments | entry window CT | hold | trades/yr | best source | grade | gross per trade | overlap |
|---|---|---|---|---|---|---|---|---|---|
| DF1-C1 | Noise-area momentum. Upper band = max(RTH open, prior RTH close) x (1 + sigma); lower band = min(RTH open, prior RTH close) x (1 - sigma). Sigma = 14-day mean of abs(close at HH:MM / open - 1) for the same minute of day. Checks at HH:00/HH:30 only: long above the upper band, short below the lower band. Trailing stop: max(UB, VWAP) for longs, min(LB, VWAP) for shorts. Flip on the opposite signal; flat at the RTH close. VM = 1. | MNQ (primary; NQ path), MES (secondary) | 09:00-14:30 CT checks (10:00-15:30 ET); exit by 15:00 CT | intraday, at most to 15:00 CT | about 200-225 round trips (VigorTas NQ: 3,351 entries over 2010-06..2026-10; Brusco: about 0.9 trades/day). The paper's 7,668 / 17 yr = 451 may count fills | Zarattini, Aziz, Barbon WP (rule); VigorTas 2026 GitHub (MNQ cost, checkable code) | working-paper (rule); pointer, code checkable (futures numbers) | MNQ: 14.8 ticks pre-publication, 41.3 ticks post (VigorTas, DF1-derived); MES: 4.2 ticks pre-publication, -1.8 post; paper SPY 4.0 bp gross = 9.6 MES ticks at ES 6,000 | K1-vwap-01 (stop), K1-cp2-01 / B-H1 / RT1-RT4 (open breakouts), E20H6 (rest-of-day momentum), V34 |

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| Sample | May 2007 to April 2024 | "data from IQFeed, covering the period from May 2007 to April 2024" | sec. 3, txt line 180 | Zarattini, Aziz, Barbon, "Beat the Market", WP, first version 2024-05-10, this version 2025-09-22, https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf | working-paper | pages/R10/concretum_Beat-the-Market.txt (local-only, Concretum terms) |
| Noise area, gap-adjusted | max/min(open, prior close) x (1 +/- sigma) | "UpperBoundt,HH:M M = max(Opent,9:30 , Closet−1,16:00 ) × (1 + σt,9:30−HH:M M )" ; "computed using the average movements recorded over the previous 14 days" | eq. after Fig. 1; lines 200, 245-249 | same | working-paper | same |
| Half-hour checks | HH:00, HH:30 | "trading is restricted to semi-hourly intervals, specifically at HH:00 and HH:30" | sec. 3, line 310 | same | working-paper | same |
| Trailing stop | band or VWAP | "Long TrailingStopt,HH:M M = max(U Bt,HH:M M , V W APt,HH:M M )" ; "as soon as the price crosses either the curent band or the VWAP, the position is closed" | sec. 3, lines 451-458 | same | working-paper | same |
| Cost assumption | $0.0035 + $0.001 per share | "a commission fee of $0.0035 per share, which represents the entry-level commission charged by Interactive Brokers. Additionally, we account for a slippage of $0.001 per share" | sec. 3, lines 347-349 | same | working-paper | same |
| Slippage basis | avg $0.001, median $0.0005 | "After executing over 1,000 trades, involving more than $50 million in notional value, the average slippage recorded is approximately $0.001, with a median value even lower at $0.0005" | sec. 4.6, line 946 | same | working-paper | same |
| Per-trade profit | $0.09/share net | "the average profit per trade is $0.09 per share" ; "From 2007 to 2024, the average SPY price was $247" | FAQ Q23, p. 40 | same | working-paper | same |
| Later per-trade profit | $0.18/share | "Over the last seven years, the average profit per share has been a robust $0.18." (no average price given for that window) | FAQ Q23, p. 40 | same | working-paper | same |
| Trade count | 7,668 trades, 1.8/day | "Intra Mom.   Curr.Band + VWAP    Dyn.   7,668       1.8       37%       0.09" | Table 4 | same | working-paper | same |
| Daily t-stat | 12 bp/day, t 5.34, 2,620 days | "Unconditional                2620           12       5.34     43%      1.7"; Table 6 calls the column "the number of traded days" | Tables 5 and 6 | same | working-paper | same |
| Futures table | S&P SR 1.32, Nasdaq 1.23, Russell 0.45; 2007-01..2024-09 | "between January 2007 and September 2024" ; "S&P500           Equity         2,501   19.8    14.9   1.32" ; "Nasdaq           Equity         1,533   16.8    13.6   1.23" ; "Russell          Equity          181     6.1    13.6   0.45" | FAQ Q13, p. 35 | same | working-paper; cost assumption, sizing and trade counts not stated; 29 of 33 rows masked "***" | same |
| Post-publication (authors) | 2024 +32.2%, 2025 Jan-Aug +1.0% | "2025    -1.2    7.6   -0.2    4.3   -2.1    -2      -2    -2.9                                1.0" | FAQ Q24 table | same | working-paper (self-reported) | same |
| Earlier losing years | 2016 -12.8%, 2017 -6.9% | "2016 ... -12.8" ; "2017 ... -6.9" | FAQ Q24 table | same | working-paper | same |
| Paz OOS, SPY | OOS Sharpe 0.39, t 0.54 | "The OOS daily mean return of 0.023\% is not statistically different from zero ($t = 0.54$, $p = 0.59$)" ; "the Sharpe Ratio declines from 1.34 to 0.39" | sec. 4 (tex lines 203, 322) | Paz (Serpa), "Out-of-Sample Evaluation of an Intraday Momentum Strategy for the S&P 500 ETF (SPY)", SSRN 7290621, 2026; https://github.com/PazSheimy/spy-intraday-momentum-oos | working-paper (GitHub copy of the SSRN paper; code in repo, IQFeed data not shared) | pages/DF1/paz_Out-of-Sample_Intraday_Momentum_SPY_PazSerpa_2026.{tex,pdf} |
| Paz IS replication | Sharpe 1.34 (2015-2024), t 4.06; same costs | "We apply a commission of \$0.0035 per share and a slippage of \$0.001 per share" ; "The in-sample daily mean return of 0.076\% is highly statistically significant ($t = 4.06$" | sec. 3-4 (tex lines 145, 174) | same | working-paper | same |
| Paz yearly | 2025 -2.7% (SR -0.10), 2026 -3.1% (SR -0.99) | "2025 &  $-2.7$ &  16.4 & $-0.10$ & 44.4 & OOS" ; "2026 &  $-3.1$ &  $-4.6$ & $-0.99$ & 46.2 & OOS" | yearly table | same | working-paper | same |
| Delgado post-publication split | 2024-05..2025-08 SR 1.057; 2025-09-02..2026-08-14 SR -0.461 | "May 2024–29 August 2025 returns 19.3% with Sharpe 1.057" ; "the subsequent 2 September 2025–14 August 2026 stretch returns -8.1% with Sharpe -0.461" ; "pooled May 2024–August 2026 Sharpe of 0.35" | abstract | Delgado, '"Beat the Market" Revisited: An Independent Replication and Statistical Audit of an Intraday Momentum Strategy', SSRN 7323419, 2026 (Crossref record) | working-paper [secondary-only] (abstract via Crossref; SSRN full text blocked) | pages/DF1/crossref_ssrn_7323419.json |
| Delgado paper-window reproduction | SR 1.317 | "the original result is reproduced almost exactly: 1,989% total return and a Sharpe Ratio of 1.317 on the paper window" | abstract | same | working-paper [secondary-only] | same |
| Chuk MNQ adaptation | +$10.26/day net, 1 MNQ, 2020..2026-07 | "earns +$10.26 per trading day net of costs (day-block bootstrap 95% interval [+$3.27, +$17.25]), with a daily Sharpe ratio of 1.14" ; "The rule is one of two survivors among 144 preregistered tests on the same archive, all intervals are in-sample, and no live contract has been traded" | abstract | Chuk, "Noise-band Intraday Momentum in Nasdaq-100 Futures", SSRN 7609644, 2026 (Crossref record created 2026-10-15) | working-paper [secondary-only] | pages/DF1/crossref_ssrn_7609644.json |
| Chuk stop slippage | 1 pt on stops removes 22% | "one index point of slippage on stop fills removes 22% of the edge" ; "95th-percentile maximum drawdown of $3,406 as backtested and $4,081 under combined lag and slippage" | abstract | same | working-paper [secondary-only] | same |
| VigorTas NQ | all +$5.35/day, t 2.74; post-publication +$13.90/day, t 1.37 | "| NQ, all (2010–2026) | 4,053 | $21,665 | $5.35 | 2.74 | 24% | −$4,250 |" ; "| NQ, after publication | 585 | $8,130 | $13.90 | 1.37 | 24% | −$4,250 |" | README table; results/NQ_yearly.md | VigorTas, "Beat the Market: a replication on Nasdaq and S&P 500 futures", GitHub 2026, https://github.com/VigorTas/beat-the-market-replication | pointer (code checkable: backtest.py read; Databento data not shared) | pages/DF1/gh_VigorTas_*.{md,csv,py} |
| VigorTas ES | all -$0.25/day, t -0.20; post -$5.56/day, t -1.21 | "| ES, all (2013–2026) | 3,410 | −$867 | −$0.25 | −0.20 | 24% | −$4,652 |" ; "| ES, after publication | 585 | −$3,254 | −$5.56 | −1.21 | 23% | −$4,652 |" | README table | same | pointer (code checkable) | same |
| VigorTas costs and fills | $1.75 RT + 1 tick per fill; next-bar open | "Costs per micro contract: $1.75 commission per round trip and 1 tick slippage per fill" ; "the trade is filled at the **open of the next bar**" ; "Size: always 1 contract" | backtest.py docstring; README | same | pointer | same |
| VigorTas per trade (DF1-derived) | NQ net $6.47/trade all, $4.67 pre, $17.91 post; ES $-0.29 all, $0.97 pre, $-6.44 post | tabulated by DF1 from results/{NQ,ES}_daily.csv (columns "date,pnl,entries"): NQ 3,351 entries, ES 2,974 entries | results CSVs | same | pointer; DF1 arithmetic on a published results file, no market data | pages/DF1/gh_VigorTas_NQ_daily.csv, gh_VigorTas_ES_daily.csv |
| Brusco ES, paper rule | Sharpe -0.07, -0.61 bp/trade net, 477 trades, 2024-05-30..2026-07-10 | "| Sharpe | **0.52** | **-0.07** | 0.93 |" ; "| 0.25 tick | -2.1% | -0.07 | -0.61 bps |" ; "Costs are not the cause of the negative result (~0.4 bps/round trip at 0.25 tick): it is the signal that does not pay in this period." | reports/validation_es.md | Brusco, "Beat the Market replication: Intraday Momentum on SPY & ES", GitHub 2026, https://github.com/giovannibrusco/zarattini-2024-momentum-spy | pointer (code checkable, 49 tests; IB/Alpaca data not shared) | pages/DF1/brusco_validation_es.md |
| Brusco ES and SPY agree | corr 0.97 | "Correlation of daily returns, ES-final vs SPY-final: 0.97." ; "| ES final | -0.04 | -1.7% | 473 | 37.8% | -0.60 |" | validation_es.md | same | pointer | same |
| Brusco base variant, ES | +2.61 bp/trade, 2024-07-01.. | "| ES base | 0.69 | +11.1% | 322 | 53.7% | +2.61 |" (post-hoc variant; Brusco calls promoting it "a-posteriori selection") | validation_es.md; CONCLUSIONS | same | pointer | same |
| Brusco SPY yearly | 2025 SR -0.27, 2026 SR -1.91 | "| 2025 | -4.9%      |    -0.27 |" ; "| 2026 | -12.9%     |    -1.91 |" | reports/validation.md | same | pointer | pages/DF1/brusco_validation.md |
| Brusco SPY trade level | +2.58 bp/trade, 1,379 trades 2020-07..2026-07 | "| Expectancy (bps)  | +4.09   | +2.58   | — |" ; "| Trades            | 941     | 1379    | — |" | validation.md | same | pointer | same |
| Maróy grid OOS (Brusco) | OOS SR 0.16, -0.17 bp | "| Sharpe           | 0.16     | 0.16              |" ; "| Expectancy (bps) | -0.17    | -0.17             |" (OOS 2024-01-01 onward) | reports/maroy_experiment.md | same | pointer | pages/DF1/brusco_maroy_experiment.md |
| Walk-forward (Brusco) | SR 0.57 vs 0.92 fixed | "| Walk-forward           |     0.57 | +7.9%  | -27.6%   |" | walkforward_experiment.md | same | pointer | pages/DF1/brusco_walkforward_experiment.md |
| Quantitativo ES | about +2 bp/trade | "A public replication on ES exists (Quantitativo, Jan 2025) which finds: ~+2bps/trade, win rate ~36%, payoff ratio ~2.09" | docs/SPEC.md | cited by Brusco; Quantitativo not fetched | pointer [secondary-only] | pages/DF1/brusco_SPEC.md |
| Maróy optimisation | Sharpe > 3 claimed | search result only: forum post on forums.bearbulltraders.com describes exits with "Sharpe ratios above 3.0" | WebSearch result | Maróy, SSRN 5095349, 2025 (Crossref: no abstract) | pointer [unverified] | pages/DF1/crossref_ssrn_5095349.json |

## 4. Negative evidence

- S&P side after publication, every independent test: Brusco ES, paper configuration, 2024-05-30..2026-07-10:
  "-0.61 bps" per trade, Sharpe -0.07. Brusco SPY, 2025: Sharpe -0.27; 2026 YTD: -1.91. VigorTas ES,
  after publication: "−$5.56" per day per MES, t -1.21; DF1-derived: -$6.44 per trade net, gross -0.44
  ES points. Paz SPY OOS (2024-05..2026-03): "Sharpe Ratio declines from 1.34 to 0.39", daily mean t 0.54.
  Delgado: "2 September 2025–14 August 2026 stretch returns -8.1% with Sharpe -0.461". Maróy-grid OOS
  (2024-01 onward): expectancy "-0.17" bp.
- The authors' own update: March to August 2025 has five losing months out of six ("-0.2 4.3 -2.1 -2 -2
  -2.9"); January to August 2025 is +1.0%. No Concretum update after the 2025-09-22 version was found;
  R10 fetched the current PDF today.
- Before publication the ES result is weak in VigorTas's fixed-size test: 2013..2024-05, "$0.84" per
  day, t 0.69; 2016 t -2.20 and 2017 t -3.05. The paper's futures-table S&P SR of 1.32 is therefore not
  reproduced at fixed size with 1 tick per fill. The paper's SR uses its vol-target sizing (leverage
  capped at 4x) and an unstated futures cost.
- NQ was flat to negative for 2010-2017 (VigorTas: 2010 t -2.94, 2013 -1.10, 2016 -0.65). The whole NQ
  edge comes from 2018 onward. Fixed one-contract dollar P&L also rises with the NQ price level
  (about 2,000 in 2010 versus 20,000-25,000 in 2025), which by itself weights the late years.
- Chuk's MNQ figure is "one of two survivors among 144 preregistered tests", "all intervals are
  in-sample". That is a selection-conditioned number.
- Paz's Sharpe-difference test ("$z = 17.05$") is implausible for about 470 OOS days. For two years the
  Lo (2002) standard error of an annual Sharpe is about 0.7, so a 0.95 drop gives z of about 1.4. This
  is DF1's arithmetic; treat Paz's "statistically significant decline" claim as unsupported. The t 0.54
  on the OOS mean is the usable statistic.
- Trade-count ambiguity: the paper reports 7,668 trades at 1.8 per day. Brusco's replication of the same
  rule makes about 0.9 per day on SPY (1,379 trades over 1,493 days) and on ES (477 over 530).
  VigorTas makes 0.83 per day on NQ. If the paper counts fills, its "per trade" figure is half a round
  trip, so per-round-trip gross would be about 8 bp, not 4 bp. The paper does not say which; the lead
  decides how to use it.

### 4a. Gross per trade, converted (inputs for the lead; D8 RT: MNQ 4.119 ticks, MES about 2.03 ticks)

| source | instrument, period | published (units) | conversion | gross MNQ ticks | gross MES ticks |
|---|---|---|---|---|---|
| Paper Table 4 / Q23 | SPY 2007-05..2024-04 | $0.09/share net at $247 (time-average price) = 3.64 bp net | gross = 0.09 + 2 x (0.0035 + 0.001) = $0.099 = 4.01 bp. ES 6,000: 4.01e-4 x 6,000 = 2.40 pts / 0.25 = 9.6 ticks (ES 6,700: 2.69 pts, 10.7). NQ 21,000-25,000: 8.4-10.0 pts / 0.25 | 33.7-40.1 (assumes the bp effect carries over from SPY to NQ) | 9.6-10.7 |
| VigorTas NQ (DF1-derived) | NQ path at MNQ cost, 2010-06..2024-05 | $4.67 net per trade per MNQ | + $2.75 RT cost ($1.75 + 2 x 0.25 pt x $2) = $7.42 = 3.71 NQ pts / 0.25 | 14.8 | - |
| VigorTas NQ (DF1-derived) | 2024-06..2026-10-09 (454 trades) | $17.91 net per trade | + $2.75 = $20.66 = 10.33 pts | 41.3 | - |
| VigorTas NQ (DF1-derived) | 2025-01..2026-10-09 (340 trades) | $16.46 net per trade | + $2.75 = $19.21 = 9.60 pts | 38.4 | - |
| VigorTas NQ (DF1-derived) | all, 3,351 trades | $6.47 net per trade | + $2.75 = 4.61 pts | 18.4 | - |
| VigorTas ES (DF1-derived) | ES path at MES cost, 2013-01..2024-05 | $0.97 net per trade per MES | + $4.25 ($1.75 + 2 x 0.25 x $5) = $5.22 = 1.04 ES pts | - | 4.2 |
| VigorTas ES (DF1-derived) | 2024-06..2026-10-09 (505 trades) | -$6.44 net per trade | + $4.25 = -$2.19 = -0.44 pts | - | -1.8 |
| VigorTas ES (DF1-derived) | 2025-01..2026-10-09 (382 trades) | -$8.14 net per trade | + $4.25 = -0.78 pts | - | -3.1 |
| Brusco ES, paper rule | ES 2024-05-30..2026-07-10, 477 trades | -0.61 bp net per trade; cost "~0.4 bps/round trip" | gross about -0.21 bp x 6,000 = -0.13 pts | - | -0.5 |
| Brusco ES, base (post-hoc) | ES 2024-07..2026-07, 322 trades | +2.61 bp net | gross about 3.0 bp x 6,000 = 1.8 pts | - | 7.2 (post-hoc variant) |
| Chuk | MNQ 2020..2026-07, in-sample | +$10.26 per day net (per trade not in abstract) | $10.26 / $0.50 = 20.5 MNQ ticks net per day | n/a per trade | - |

### 4b. Adversarial: reasons C1 may fail on MNQ in 2025-2026

1. The S&P version is gone after publication in all six S&P-side tests (section 4). The Nasdaq version
   rests on one fixed-size GitHub backtest (VigorTas post-publication t 1.37 over 585 days) and one
   in-sample abstract that survived a 144-test search (Chuk). Before 2018, NQ lost money on this rule.
2. Crowding: at least 15 public GitHub implementations exist (gh search "zarattini", 2026-10-18), plus
   several open-source TradingView scripts ("Concretum Bands", "Noise Area"). Concretum promotes the
   rule. Paz names crowding: "Increased adoption of similar strategies could reduce available profits
   through crowding effects" (tex line 303). Crowding is a hypothesis; no one has measured it.
3. 2025 losing months: the authors' table shows 2025-03..08 at five of six months negative. Delgado
   reports Sharpe -0.461 for 2025-09..2026-08. On the S&P side, then, both 2025 and 2026 are weak.
   VigorTas NQ for the same years is positive but not significant (2025 t 0.78, 2026 t 0.68).
4. Session hours: the rule is anchored on the 09:30 ET equity open and the 16:00 ET prior close. For
   futures the RTH 08:30 CT open and 15:00 CT close align with those (VigorTas and Brusco use RTH).
   Two things change if the 17:00 CT Globex open is used as "the open" instead. The gap term
   max/min(open, prior close) disappears or changes meaning. Sigma would then measure moves from an
   overnight anchor. No test of that variant was found, so it would be a new rule, not a replication.
   VWAP must also be RTH-only. A Globex-session VWAP is dominated by overnight volume.
5. Roll: the prior close and the 14-day sigma window must sit on one contract. Otherwise a roll week
   puts a calendar-spread jump (Brusco: "+50/+75 points" ES offsets) into the band anchor. Brusco
   back-adjusts; VigorTas does not say how it rolls.
6. Sizing: the paper's Sharpe uses vol-target leverage up to 4x. A prop account trades 1-N micros. The
   fixed-size ES result before publication is only t 0.69 (VigorTas).
7. Trade count: the paper's "450 a year" is probably fills. Independent replications run about 200-225
   round trips a year (section 4), which halves the per-year trade count used for power.
8. Stop slippage and fills: VigorTas charges 1 tick per fill and fills at the next bar open. Chuk
   finds "one index point of slippage on stop fills removes 22% of the edge". MNQ fast markets at
   10:00 ET releases are the risk.

## 5. Data and cost

- Needs 1-minute OHLCV for NQ/MNQ (or ES/MES) RTH bars: open at 08:30 CT, prior RTH close at 15:00 CT,
  RTH VWAP from volume-weighted bar prices, and a 14-day per-minute sigma. Owned (section 4): NQ
  2010-07..2024-02, MES 2019-05..2025-03 (holdout-2 sealed), research window 2025-04-01..2026-06-19.
  Owned: yes. No side data is needed. VIX is optional for the paper's VIX conditioning.
- Data cost: none (owned). Replicators used Databento (VigorTas), IB (Brusco), IQFeed (Paz, paper) and
  TradeStation (Delgado). None of them redistributes data.
- Research-window note for the lead: the window (2025-04..2026-06) is already covered by published
  third-party results: VigorTas NQ 2025 +$13.75/day (t 0.78) and 2026 +$11.33/day (t 0.68); ES 2025
  -$1.12 and 2026 -$14.61/day; Brusco ES and Delgado, see section 4. A new test of C1 on that window
  would not be blind to its outcome.

## 6. Prop compatibility

- Timing: checks 09:00-14:30 CT and forced exit at the RTH close (15:00 CT) are before Topstep's 15:10
  CT flatten. No overnight holds.
- Drawdown versus the trailing max loss: VigorTas NQ max drawdown per single MNQ is "−$4,250" over the
  whole sample, and was reached after publication; 2025 alone was "-$2,972". Chuk's 95th-percentile
  MDD is "$3,406" to "$4,081" per MNQ. All of these exceed the 50K account's $2,000 trailing max loss
  at one micro. The $4,250 is close to the 150K account's $4,500.
- Consistency rules: only about 24% of days are winners (VigorTas: "Most days are small losses; a few
  big trend days pay for everything"). Best-day concentration works against Topstep's 55% Combine rule
  and the 40% Consistency payout path. This is not quantified here.
- P06: the 09:00 CT (10:00 ET) check lands on 10:00 ET releases (ISM and others), and positions are held
  through 13:00 CT FOMC. One or two micros is far below maximum size.
- HFT and automation: 12 decisions a day at half-hour marks with market orders. That is not HFT. It can
  run on the API or by hand (V39 allows manual execution).
- Stop fills: Chuk reports that 1 point of stop slippage removes 22% of the edge, so a fast-market exit
  costs real money on MNQ.

## 7. Overlap with tested mechanisms

| id | how C1 differs |
|---|---|
| K1-cp2-01, B-H1, RT1-RT4 | Those are fixed opening-range breaks (08:30-08:45 or 08:30-09:00 range, plus or minus 4 ticks). C1's band is time-of-day volatility-scaled and gap-adjusted, and it is re-checked every half hour all day. |
| K1-vwap-01 | Close versus VWAP with stop-and-reverse on every bar (at most 20 entries a day). C1 uses VWAP only as one leg of the trailing stop, and enters only on a band break. |
| E20H6-T1..T3 | Last-half-hour momentum from the rest-of-day sign (14:30-14:58). C1 enters from 09:00 CT and does not use the last-half-hour window. The family is related (intraday time-series momentum), but there is no common trigger. |
| V34 | Dropped noise-area momentum as "unsized"; R10 already sized it. DF1 adds futures sizing at MNQ and MES cost from replications (section 3). Whether the rule is "close to the failed opening-range family" is the lead's call. |

## 8. Verdict checks

| verdict | effect | basis |
|---|---|---|
| V34 "noise-area momentum (unsized; ...)" | WEAKENS the "unsized" basis | VigorTas gives a per-trade figure at MNQ cost, gross about 14.8 MNQ ticks before publication and 41 after (DF1-derived from "date,pnl,entries"). On the S&P side, the post-publication evidence supports dropping it. |

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| (R10) concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf | R10, 2026-10-18 08:4xZ | 865010df...6ebb (pdf) | pages/R10/concretum_Beat-the-Market.{pdf,txt} | ok (R10's copy reused, read locally) | R10 curl |
| https://github.com/giovannibrusco/zarattini-2024-momentum-spy (README) | 2026-10-18T13:29Z (first DF1 run, file mtime) | ab372fd2...ae17 | pages/DF1/gh_giovannibrusco_zarattini-2024-momentum-spy_README.md | ok | first-run fetch |
| same repo reports/validation_es.md, reports/validation.md, docs/CONCLUSIONS.md, docs/SPEC.md, reports/maroy_experiment.md, reports/walkforward_experiment.md | 2026-10-18T13:30Z (mtime) | 2bd39f71..., f8bd0634..., 2aab2481..., bc8f098e..., f3fa4d41..., c17449b9... | pages/DF1/brusco_*.md | ok | first-run fetch |
| https://github.com/PazSheimy/spy-intraday-momentum-oos (README, paper .tex/.pdf) | 2026-10-18T13:29-13:30Z (mtime) | 43f9dcdd... / 6e7e1a77... / 15a64930... | pages/DF1/gh_PazSheimy_*, paz_* | ok | first-run fetch |
| github.com/{blackswan-quants/intraday-momentum, esperu4/noise-area-intraday-momentum-ea, roman-terentiev/noise_area_mom, thatisarrty/spy-intraday-momentum-research, wlinoxox/ES-Noise-Area-Breakout-Strategy} READMEs | 2026-10-18T13:29-13:32Z (mtime) | 4a9e0012..., a3aa8503..., 2015a392..., 7f34f276..., abfc2b6c... | pages/DF1/gh_*_README.md | ok (pointers; no numbers used except as noted) | first-run fetch |
| api.crossref.org works/10.2139/ssrn.{5095349, 7290621, 7323419, 7609644} | 2026-10-18T13:27Z (mtime) | 2fe1fceb..., fd025869..., b65718e5..., 77c82023... | pages/DF1/crossref_ssrn_*.json | ok | first-run fetch (terms: terms/api.crossref.org_terms.html) |
| GitHub search API: repos "noise area momentum", "zarattini", "noise band nasdaq", "noise-band", "intraday momentum MNQ", "beat the market revisited", "noise area futures" | 2026-10-18T18:16-18:17Z | n/a | n/a | ok (Chuk and Delgado repos not found) | gh search |
| api.github.com repos/{VigorTas/beat-the-market-replication, sophietsay/wutis-algotrading-case-study, arnavahuja/spy-mometum-strategy, svettelnova/intraday-momentum-spy, hsaeed22058/strategy-backtest, noiiiise/SPY-Intraday-Momentum}/readme | 2026-10-18T18:18:22-18:18:39Z | 7c4c8876..., ab707abf..., d03e1ef9..., 6081f6fb..., 7d217f02..., 230f848a... | pages/DF1/gh_*_README.md | ok | gh api |
| VigorTas results/NQ_yearly.md, results/ES_yearly.md | 2026-10-18T18:19:00Z, 18:19:04Z | 4694a448..., 290c03e7... | pages/DF1/gh_VigorTas_{NQ,ES}_yearly.md | ok | gh api |
| VigorTas results/NQ_daily.csv, results/ES_daily.csv, backtest.py | 2026-10-18T18:19:18Z, 18:19:22Z, about 18:19:25Z | cf4f1fa4..., d516880e..., 2a9a96be... | pages/DF1/gh_VigorTas_{NQ,ES}_daily.csv, gh_VigorTas_backtest.py | ok (third-party result files, not market data) | gh api |

Terms: github.com is allowed per terms_log line 118 (R4). Crossref was logged by the first DF1 run.
QuantConnect is forbidden (terms_log line 137, DF1 first run), so nothing was fetched from it.
concretumgroup.com is allowed for named pages, with copies kept local (R10).
WebSearch: 4 calls this run (Chuk title; Delgado title; Maróy title; Quantitativo ES). No budget notice.
An informational cost notice (hook, "Informational only") appeared at about 18:16Z; it did not stop
work. OpenAlex, Firecrawl and Semantic Scholar were not used.

## 10. Unfinished and unverified

- Chuk (SSRN 7609644) and Delgado (SSRN 7323419): abstract only, from Crossref [secondary-only]. Full
  text not found on GitHub or the web (SSRN blocks automation). Chuk's per-trade figure, trade count,
  session definition (RTH or Globex open) and cost model are unknown.
- Quantitativo ES (+2 bp/trade) and Maróy (Sharpe above 3): pointers only, not fetched.
- The sophietsay, arnavahuja, svettelnova, blackswan and thatisarrty repos give no post-2024-05
  futures numbers in their READMEs. Their notebooks were not read. thatisarrty's OOS ends in 2024-04
  (before publication).
- Nobody found tests the 17:00 CT Globex open as the anchor. Every replication uses the RTH open and
  the prior RTH close. VigorTas's continuous-contract roll method is not stated. Brusco uses a
  volume-crossover roll with additive back-adjustment.
- The bp conversions of VigorTas pre-publication figures to an average index level (ES about 3,000,
  NQ about 8,000 over 2010-2024) are DF1 assumptions, used only as a rough cross-check.
