# Literature brief for Stage E.20 (planning chat research run, 2026-10-10)

Provenance: an Advanced Research run launched from the planning chat on
2026-10-10, from web sources. It is reference material, not a verdict: the
per-trade bp figures for Baltussen et al. are the research run's own
derivations from annualized returns, almost every published number is gross
of costs, and the post-2020 evidence comes from weak sources (a working
draft, a master's thesis read in abstract, an unreviewed blog). Every claim
a stage relies on must be re-checked against the primary source by that
stage's readers.

## Cost wall in bp (D8)
- MNQ $2.06 round trip, about 0.4 bp of notional; 3x gate about 1.2 bp.
- NQ $15.55, about 0.3 bp; 3x gate about 0.9 bp.
- MES $2.54, about 0.8-0.9 bp (estimate); 3x gate about 2.5 bp.
- Full-size ZN: one tick ($15.625) about 1.4 bp; CL one tick ($10) about
  1.5 bp. Rates and energy effects need about 4 bp gross for a 3x gate.

## Findings
1. Market intraday momentum, rest-of-day to last half-hour (ROD -> LH).
   Baltussen, Da, Lammers and Martens, "Hedging demand and market intraday
   momentum", JFE 142 (2021) 377-403; 1-minute bars on 60+ futures,
   1974-12..2020-05.
   - Rule: 30 minutes before the market's common close (15:30 ET for
     ES/NQ, 14:30 CT), go long if r_ROD = P(close-30)/P(prior close) - 1 > 0,
     short if < 0; exit at the close (16:00 ET, 15:00 CT).
   - Equity portfolio 6.86%/yr, Sharpe 1.73, hit rate 55%; bonds 2.16%/yr
     (1.62); commodities 4.34%/yr (1.42); FX 0.85%/yr (0.87). Derived per
     trade: about 2.7, 0.9, 1.7, 0.3 bp. Gross, except a positive net Sharpe
     reported for S&P futures at one tick.
   - NQ alone, 1996-2020: coefficient 6.36 (x100), t 7.97, OOS R2 3.76%
     (about 6.4 bp expected per 1% ROD move).
   - Mechanism: significant on negative dealer-gamma days (6.63, t 4.78),
     not on positive-gamma days; leveraged-ETF rebalancing adds power; stops
     at the 16:00 ET cash close; reverses over 1-3 days.
   - Differs from the program's tested first-30-minute continuation (Gao,
     Han, Li, Zhou 2018 ONFH); Baltussen show ROD dominates ONFH OOS.
   - Post-2020: Adams, Dim, Eraker, Fontaine, Ornthanalai and Vilkov (2026
     draft) find high market-maker hedging needs predict weaker momentum or
     reversal; an unreviewed SPX retest 2022-04..2026-08 finds insignificant
     unconditional slopes, significant only on short-gamma closes; an Aalto
     thesis (2008-2024, 20 futures) finds the patterns persist but mostly not
     after costs, especially bonds and FX; Rosa (J. Futures Markets 2022)
     finds overnight-return -> LH vanishes OOS and a threshold version beats
     always-on.
2. Overnight drift 2-3 a.m. ET in ES (Boyarchenko, Larsen and Whelan, RFS
   2023): about 1.4 bp a day 1998-2019; near zero since 2021 (NY Fed Liberty
   Street, July 2026). Requires an overnight window. Drop.
3. Closing-auction distortions (Bogousslavsky and Muravyev, JFM 2023):
   small and reverse overnight. Not tradable flat by 15:08 CT.
4. Pre-announcement drift (Kurov, Sancetta, Strasser and Wolfe, JFQA 2019):
   for 9 of 20 market-moving US releases, ES and ZN drift the right way
   about 30 minutes early, about 40% of the total move; pre-2015 sample; a
   2022 draft ("Drift Begone") tests whether release policies removed it.
   Per-trade net unknown.
5. No usable post-2015 evidence found for lunchtime reversal, settlement
   windows, ES->ZN or CL->CAD minute lead-lag at retail latency. Unknown,
   not rejected.
6. Noise-area intraday momentum (Zarattini, Aziz and Barbon, SSRN 4824172,
   2024): SPY 2007-2024, net Sharpe 1.33 under the authors' cost model;
   bands = gap-adjusted open +/- 14-day average absolute move from the open
   at each minute; entries on half-hour marks 10:00-15:30 ET; flat by the
   close. Practitioner source, leverage in results, close to the program's
   failed opening-range family; per-trade gross unknown.
7. Base rates: Chague, De-Losso and Giovannetti (SSRN 3423101): 97% of
   Brazilian mini-index day traders who persisted 300+ days lost money.
   Topstep 2025 (first party): 16.8% of Combines completed; 33.3% of
   funded-level participants received a payout; 0.71% of XFA traders called
   up to Live.
8. ML intraday: Aleti, Bollerslev and Siggaard (Management Science 2025)
   and Huddleston, Liu and Stentoft (J. Financial Econometrics 2023) report
   after-cost results near Sharpe 1 only with cross-sectional inputs
   (hundreds of stocks or factors). A 2026 Frontiers study: better accuracy
   did not translate into profit after costs. Expect OOS R2 under 0.5% from
   bar-only futures features; a surviving signal near the close is likely
   ROD -> LH rediscovered.
9. Passive execution: ES/NQ spreads are one tick (binding tick, Kurov and
   Zabotina JFM 2005). Simulated resting 1-lot orders (Lalor and Swishchuk,
   arXiv 2409.12721, one day per contract) were adverse on 81.5% (ES),
   65.8% (NQ), 82.9% (CL), 88.8% (ZN) of fills; DeLise (arXiv 2407.16527)
   proves the expected mid move after a limit fill is negative with a
   one-tick spread. Passive entry on momentum signals keeps the losers.
   No published saving figure for micros.

## Shortlist from the research run (none on the tested list)
1. ROD -> LH on NQ via MNQ/NQ, unconditional plus a magnitude-threshold
   variant (trade only when |r_ROD| is above its trailing median). Only
   effect whose published numbers clear the 3x gate (about 7x MNQ cost on
   history). Risk: decay in the 0DTE era; power.
2. The same, filtered on negative dealer gamma. Risk: gamma data access and
   vendor conventions; snooping.
3. Noise-area momentum on MNQ/MES with the published parameters. Risk:
   overlap with the failed opening-range family; practitioner provenance.
4. Gamma-regime hourly reversal in ES (Adams et al. 2026). Magnitude
   unknown; needs gamma data.
5. Pre-announcement drift in ES/ZN for the identified releases (not ISM).
   Magnitude unknown; few events; possible policy-driven decay.

## Sources (as given by the research run)
- https://academicweb.nd.edu/~zda/intramom.pdf
- https://www.sciencedirect.com/science/article/abs/pii/S0304405X21001598
- https://www.jean-sebastienfontaine.com/papers/0dte-options-volatility.pdf
- https://dev.to/firmtape/intraday-momentum-is-dead-in-the-0dte-era-we-measured-it-on-1085-spx-sessions-43g0
- https://aaltodoc.aalto.fi/items/1011f043-edd1-4cb2-9694-b1216d77561f
- https://onlinelibrary.wiley.com/doi/abs/10.1002/fut.22375
- https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf
- https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/
- https://www.sciencedirect.com/science/article/abs/pii/S1386418123000502
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4824172
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101
- https://www.topstep.com/our-program
- https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1888767/full
- https://ideas.repec.org/a/wly/jfutmk/v25y2005i1p79-104.html
- https://arxiv.org/pdf/2409.12721
- https://arxiv.org/pdf/2407.16527
- https://pages.stern.nyu.edu/~jh4/SternMicroMtg/Old/SternMicroMtg2015/Papers/Preannouncement_042015Strasser.pdf
