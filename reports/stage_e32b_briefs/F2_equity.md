# F2_equity: equity family facts (M2K RTY MYM YM MNQ; NQ leader facts only, V49)

Worker: EquityReader-OpusHigh (Stage E.32b, step F2). Started 2026-10-28 22:48 PDT, finished 23:02 PDT (clock times
from `date`). Machine-readable twin: `F2_equity.json` (54 items, ids EQUITY-n). Shared source owned here:
`F2_shared_baltussen.json` (30 items, ids SB-n). Pages: `pages/EQUITY/` with `log.tsv`. Helpers:
`work/EQUITY/` (EQUITY_fetch.sh, EQUITY_make_baltussen.py, EQUITY_make_f2.py; the builders check every quote
verbatim against its saved file before writing). Facts only; nothing is scored.

WebSearch calls: 14 of 60. No budget notice seen. T6 full-text reads: 3 (Baltussen, Taylor 2026, Boyarchenko
et al.). Reuse: E.28 A1_equity (F1, F3, F5, F9, F10, F11, F13), E.20 shared/equity_class_notes.md, rosa_2022_notes.md,
macro_calendars.md, product_NQ.md, E.16 rulings R-S6, E.25 RD8. RETURN files E.29/E.31/E.33c: no equity spread or
touch measurement (E.29 assumes 1 tick per member; E.31 is ZM).

## Shared: Baltussen, Da, Lammers, Martens (2021, JFE 142(1)), `F2_shared_baltussen.json`

- Authors note: the brief says "Baltussen, van Bekkum and Da"; the saved text names Baltussen, Da, Lammers,
  Martens (same title, DOI 10.1016/j.jfineco.2021.04.029).
- Design: last 30 min before the class close predicted by prev close -> close-30 (r_ROD); 62 futures, Dec 1974 to
  May 2020, Tick Data 1-min; in-sample OLS plus recursive expanding-window OOS R2 (min 500 obs, Clark-West).
  NOT net of costs (one sentence claims a positive net Sharpe for ES at one tick). Effect reverts over the next days.
- Asset classes (pooled beta_ROD x100, t): equity 4.18 (7.29), R2_OOS 2.88% (SB-1); bonds 1.90 (5.97) (SB-2);
  commodities 1.21 (3.63), R2_OOS 0.07% (SB-3); currencies 0.72 (4.57) full sample (SB-4) but 0.33 (t 1.45),
  not significant, in 2000-2020 (SB-5, negative).
- Product rows (Appendix B): positive and OOS-significant for YM, NQ, ER (Russell), ES, TU, FV, TY, US, GC, SI, NG,
  AD; negative or null for UB (OOS R2 -3.40%), HG, CL, BO (ZL), CN (ZC: in-sample only), SM (ZM), SY (ZS), WC (ZW),
  EC (6E). No crypto, no micro, no yield futures in the sample.

## Per code

### MNQ (baseline) and NQ (leader; excluded from scoring, V49)
- T1 spread/touch: not found (EQUITY-1: Kurov-Zabotina 2005 abstract says the NQ tick binds the spread; EQUITY-2 a
  broker claim of 1 tick in the US session, pointer only). Spec rule S = 1 (u).
- T2b: Micro E-mini Futures MM Program covered MNQ 2019-05-06 to 2022-01-31, extended to 2022-04-30 (CME 22-047,
  full text; EQUITY-4, -5, F1 change EQUITY-54). NQ outright: E-mini Equity Index Futures MM Program 2013-04-01 to
  2021-01-31 by the overstrike reading (EQUITY-6, reused); nothing later found. Programs on NQ's TACO (to 2026-01-31),
  BTIC (to 2026-01-31) and TMAC (2023-07..2025-01) contracts exist but are not outright (EQUITY-8, -9, -10).
- T3: MNQ-NQ 10:1 mechanical pair (EQUITY-12); NQ leads ES by about 9-12 min and Russell by about 8-11 min at
  60-min chart extrema, 2004-2014, preprint, no trading test (EQUITY-13).
- T5: MNQ final = Nasdaq-100 SOQ, same as NQ; MNQ daily settlement = NQ's 30-s VWAP (FAQ, pre-2020 window)
  (EQUITY-22, -23, -24). NQ financially settled (EQUITY-26). NQ held over 80% of Nasdaq-100 price discovery vs QQQ
  and the floor contract, Mar-May 2000 (EQUITY-27, full text). Micros about equal to minis in their first three months
  (Fassas 2021, abstract; EQUITY-28).
- T6 best level: peer-reviewed, product itself (NQ), in sample plus recursive OOS, gross, data to 2020-05:
  Baltussen NQ beta_ROD 6.36 (t 7.97), R2_OOS 3.76% (EQUITY-29); Nasdaq-100 cash 4.39% (EQUITY-32).
  Negatives: Rosa 2022 (abstract) predictability disappears OOS (EQUITY-41); Mesfin 2026 MNQ 5-min, none of 14
  families passes net of 2 points (EQUITY-43, full text in E.20); Taylor 2026 NQ 15-min AMD signal has no direction
  beyond the daily trend regime (EQUITY-44, full text); Rodas 2026 excluded (<5 min, EQUITY-45).

### RTY and M2K
- T1: not found. T2b: M2K in the Micro program to 2022-04-30 (EQUITY-4, -5). RTY outright: E-mini Russell 2000 MM
  program 2017-07-10 to 2018-03-31 only (EQUITY-7); TACO/BTIC/TMAC programs on RTY contracts (EQUITY-8, -9, -10).
- T3: M2K-RTY pair (EQUITY-12); Russell leads ES by about 5 min, lags NQ (EQUITY-13).
- T5: RTY final = Russell 2000 SOQ (EQUITY-25); M2K as the micros above.
- T6 best level: peer-reviewed, Russell futures (ER, ICE then CME), 1993-2020, gross: beta_ROD 6.00 (t 5.86),
  R2_OOS 3.15% (EQUITY-30). IWM (other venue) 2000-2013: OOS R2 2.43% (EQUITY-37). No post-2020 Russell study found.
- F1: 2025 ADV to Oct 2025: RTY 217,000, M2K 85,000 contracts/day (FTSE Russell page, EQUITY-53), shown beside E.28.

### YM and MYM
- T1: not found. T2b: MYM in the Micro program to 2022-04-30; YM in the E-mini Equity Index MM program to
  2021-01-31 (overstrike reading); YM's BTIC/TMAC contracts have programs (EQUITY-9, -10). Not in TACO.
- T3: MYM-YM pair only; no lead-lag study for YM found (EQUITY-14).
- T5: MYM final SOQ, daily from YM (EQUITY-22, -23); YM financially settled (EQUITY-26).
- T6 best level: peer-reviewed, YM itself, 1997-2020, gross: beta_ROD 5.02 (t 4.12), R2_OOS 2.18% (EQUITY-31);
  DJIA cash 1.69% (EQUITY-33). Rosa (abstract; DJIA per snippet only) negative OOS.

## Family-wide facts
- T2a: no post-2012 non-CFTC automated/HFT share found. Older: ES HFT 34.22% of volume, May 3-5 2010 (Kirilenko et
  al. slides, EQUITY-3). CFTC OCE shares are RatesReader's shared source.
- T2c: no retail share of volume found (E.28 F13 and one new search).
- T4: macro releases 08:30 ET (NFP, CPI, PPI, GDP), 10:00 ET (ISM), FOMC 14:00 ET (EQUITY-16). Absorption: ES
  2008-2014 shows pre-release drift from about 30 min before (7 of 18 announcements) and "some evidence of continuing
  adjustment" in t+10 to t+30 min (EQUITY-17, -18; cousin, full text). ES order-flow shocks dissipate within a second
  (abstract, EQUITY-19). FOMC days: SPY intraday momentum 20.04%/yr vs 6.24% (1993-2013, EQUITY-20). Pre-FOMC drift
  gone after 2015 (abstract, EQUITY-21, negative). No equity-index product-specific scheduled release.
- T6 class and decay: SPY first-half-hour 6.67%/yr gross, 6.52% net of spread 2005-2013 (EQUITY-36); SPX cash 2005-2017
  (EQUITY-38); ES 2018-2024 reversal when dealer gamma is high (EQUITY-39, draft, negative); SPX 2022-2026 flat slope
  (EQUITY-40, pointer, negative); SPY noise-area momentum 6.2%/yr net 2007-2024 (EQUITY-42, practitioner WP); Aalto
  thesis: persists 2008-2024 but mostly not cost-feasible (EQUITY-46, abstract).
- T7: Globex Sun-Fri 18:00-17:00 ET, halt removed 2021-06-28 (EQUITY-47); daily settlement 15:00 CT from 2020-10-26
  (EQUITY-48); cash-close last-half-hour effect (EQUITY-49); European-open 02:00-03:00 ET drift on ES 1998-2020,
  +3.7%/yr gross, Sharpe -0.5 after bid-ask spreads (EQUITY-50, -51, negative net); 20-24% of micro volume outside
  US hours (EQUITY-52).

## Searched, not found
- T1 median spread and touch size for all six (3 WebSearches; E.28 F10 also none).
- T2a post-2012 non-CFTC HFT share (1 search). T2c retail share (1 search).
- T2b outright programs for NQ/YM after 2021-01, RTY after 2018, micros after 2022-04 (3 searches; 6 filings read).
  Absence is "not found", not "none exists".
- T3 minute-level lead-lag or cointegration of NQ/RTY/YM vs ES (1 search, arXiv API).
- T6 post-2020 peer-reviewed tests on NQ, RTY or YM (1 search, 3 arXiv API queries).

## Gaps and failures
- ACFR conference paper (Zhou, intraday momentum) blocked: HTTP 403 by curl and WebFetch; not read.
- Skidmore copy of Kurov et al. 2017 returned 404; the 2015 Stern draft was used.
- Fassas (2021) full text not found; Rosa (2022) full text closed (E.20).
- Current micro daily-settlement window (post-2020-10-26) not verified; NQ/YM SOQ wording read only by analogy.
- Overstrike readings of program end dates (E-mini 2021-01-31, RTY 2018-03-31) rest on the filings' stated
  convention, checked against the logic of CME 22-047; strikethrough is not visible in the text extraction.
