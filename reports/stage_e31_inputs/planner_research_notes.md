# Planner research notes for E.31 (planning chat, 2026-10-21/22)

These notes come from two external web research runs in the planning chat.
They are pointers to verify, not evidence the stage may cite without
checking. CME pages were not fetched (program rule); the CME figures below
came through secondary sources.

## QM (E-mini WTI)

- QM is about 1% of CL's volume in spot months, and CL carries about 80%
  of WTI price discovery. Source: CFTC, Burns and Kane 2022,
  https://www.cftc.gov/sites/default/files/2022-05/WTIpaper_RP_resubmit_ada.pdf
- QM ADV was 18,621 in 2018 (Wikipedia E-mini table). 2026 single-session
  snapshots showed 48 to 420 a day (TradingView, Yahoo; low reliability).
- QM has used FIFO with no LMM since April 2012 (CME advisory 20120326,
  seen through a search snippet only).
- QM is financially settled off CL's settlement.
- One QM tick is 2.5 CL ticks, so resting QM quotes go stale when CL
  moves.
- Passive fills in CL were adverse 518 of 625 times (83%) on 2024-04-23,
  in a TT queue simulator. Source: Lalor and Swishchuk, arXiv 2409.12721.

## ZM (soybean meal)

- Matching on CBOT grains and oilseeds uses the K algorithm: TOP priority
  (capped at 100 contracts on grain outrights), then 40% FIFO, then 60%
  pro-rata with leveling, then FIFO for the residual. Sources: CME's
  presentation to the CFTC Agricultural Advisory Committee, 2019-04
  (https://www.cftc.gov/system/files/2019/04/10/aac041119presentation_cmegroup.pdf);
  CME filing 14-270; Peng, JFM 2024. Globex uses FIFO when the aggressor's
  size is at least all displayed quantity at the price.
- Implied intercommodity spreads (the board crush SOM: 10 ZS : 11 ZM :
  9 ZL; calendars; butterflies; ZM-MZM) feed the outright book. Implied
  bids and offers are eligible but "not disseminated in market data"
  (CME Client Systems wiki, Implied Intercommodity Ratio Spreads).
- Hours: 19:00-07:45 CT overnight and 08:30-13:20 CT day session.
  Physically delivered.
- Daily limit on trade date 2026-10-21: 20 USD/ton on outrights, 30
  expanded. Limits reset in May and November. A limit move expands ZS, ZM
  and ZL together.
- Volume: 2020 CBOT soybean meal futures traded 29.9 million contracts
  (about 119k a day), with 415,506 year-end OI (FIA via CFTC, 2021-06). In
  Oct 2026 the front-month OI was about 258k (Farmbucks).
- Liquidity spills over across the soy complex within about 30 seconds.
  Source: de Boer et al., JFM 42(7) 2022, doi:10.1002/fut.22325.
- Fees per round trip in USD (firm pages read 2026-10-22):

  | Firm | ZM | MGC |
  |---|---|---|
  | Topstep | 5.28 | 1.92 |
  | MFFU | 6.12 | 2.20 |
  | Tradeify | 9.20 | 2.12 |
  | Bulenox | 5.72 | 1.52 |
  | Lucid | 5.60 | 1.60 |

- Topstep's Tier 1 window (page 13613539, updated 2026-10-22) covers CPI,
  NFP, PPI and FOMC. It blocks the minis ES, RTY, YM, NQ, NKD, GC, SI, HG
  and PL, and caps MGC at 3 on a 50K account. "Other products (energies,
  rates, FX, etc.) are unaffected"; grains are not listed. So the E.26
  rules record's "minis blocked" needs this product list.
- Topstep's "Prohibited Trading Strategies" page (2026-06-10) bans
  "hundreds of rapid trades to take advantage of preferential queue
  position in SIM" and orders outside the best bid or offer.
- MFFU makes the EIA report Tier 1 for energy on its Rapid and Pro sim
  funded accounts. Lucid prohibits microscalping, meaning more than half
  of profit from trades of 5 seconds or less (secondary source).

## MGC

- MGC's fees are 1.5 to 2.2 ticks a round trip at every firm, more than
  the one-tick spread a passive round trip can earn. The research run
  advises dropping it for passive spread capture.
