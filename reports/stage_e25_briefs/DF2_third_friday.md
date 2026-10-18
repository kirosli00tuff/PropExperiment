# DF2 Third Friday price spike (second reader on C2/C3 and B1)

Reader: DF2-ThirdFriday-OpusHigh (DeepReader-ThirdFriday-OpusHigh), Stage E.25, research only.
Resumed run: the first DF2 run (cut about 06:35 PDT) saved the papers, calendars and SEC order in
pages/DF2/; this run re-read them, digitized the figures and wrote this file (11:16 to about 12:10 PDT).
Price levels used for conversions: ES 6,000 (1 bp = 0.60 ES pt = 2.40 MES ticks), NQ 22,000 (1 bp = 2.2 NQ pt
= 8.8 MNQ ticks), YM 44,000 (1 bp = 4.4 YM pt = 4.4 MYM ticks). Times are ET in the paper; CT = ET - 1 h.

## 1. Answer (at most 250 words)

The full text confirms the ES numbers RD4 and R12 quoted. In the January 2024 version they sit in Table II,
labelled "Panel c: E-mini" (RD4 and R12 cite the September 2024 copy as "Panel (b) Futures"; the numbers
match): Thursday close to Friday open +14.30 bp (t 3.54, sd 60.53), Friday open to close -12.89 bp
(t -2.40, sd 80.45), 2003.2-2021.12. The August 2026 version ("The Third Friday Price Spike", R&R at RFS)
extends the sample to 2023 but drops that futures table. Its Figure 1 text gives ES as "12 bps, which
completely reverses by noon".
I digitized the vector figures. The Thursday 15:00-17:00 CT window (Topstep must be flat) adds about
-0.6 bp, so it holds none of the run-up. All of the run-up accrues after the 17:00 CT reopen, mostly
02:00-05:00 CT and in the last 30 minutes before the open. The reversal is fast: about 70% of it comes
in 08:30-09:00 CT (ES -8.6 bp, NQ -12.5 bp), it is complete by about 10:30 CT, and the trough is about
12:30 CT. NQ and YM show the same pattern (Figure 6, 2024 version; no table).
There are two risks. (a) Quarterly expiries carry most of the intraday leg: on the SOQ basis it is
-37 bp quarterly but only -6 bp off-quarter. (b) The overnight leg decays on the SPX basis: about
4.2 bp per event over 2015-2023 and 1.6 bp over 2022-2023, against an intraday short leg of 17.6 and
14.8 bp. No evidence after 2023 was found. The window 2025-04-01..2026-06-19 holds 15 monthly expiries
(5 quarterly, 2 moved to Thursday). The order book at the open was not studied anywhere I found.

## 2. Candidate hypotheses

| id | hypothesis | instruments | entry CT | hold | trades/yr | published effect | gross pts / micro ticks (price used) | dispersion | decay | overlap |
|---|---|---|---|---|---|---|---|---|---|---|
| DF2-C1 | Short at the 08:30 CT RTH open on the monthly a.m.-settlement day; cover at a fixed time (the lead picks the time; the path below is given for 09:00, 11:00 and 15:00 CT) | MES (MNQ, MYM) | 08:30 | 30 min to 6.5 h | 12 (8 if quarterly is excluded) | ES Fro->Frc -12.89 bp (Table II 2024); path: open->09:00 CT -8.6 bp, ->11:00 CT -15.0 bp, ->15:00 CT -12.5 bp (Fig 1, 2026, digitized) | 7.73 ES pts = 30.9 MES ticks (Table II); 09:00 CT 5.1 pts = 20.6 ticks; 11:00 CT 9.0 pts = 35.9 ticks (ES 6,000). NQ open->11:00 CT 19.6 bp = 43 pts = 172 MNQ ticks (NQ 22,000) | t -2.40, sd 80.45 bp per event (48.3 ES pts), n about 225 | intraday leg on SPX basis 17.6 bp/event 2015-2023, 14.8 bp 2022-2023 (Fig 3, 2026, digitized); off-quarter intraday only -6 bp (Table III 2024) | E-H3, D-H4, A-H4 (rth leg) |
| DF2-C2 | Long from the 17:00 CT Thursday reopen to the 08:30 CT Friday open (exit at or just before the open) on the monthly a.m.-settlement day | MES (MNQ, MYM) | 17:00 Thu | about 15.5 h | 12 | ES Thc->Fro +14.30 bp (Table II 2024; the Thc point is 15:00 CT, before the break); path from 17:00 CT to the 09:30 ET point +12.75 bp (2026 Fig 1) | 7.65 ES pts = 30.6 MES ticks to the open point; to 08:25 CT 6.8 pts = 27.2 ticks. NQ +13.7 bp = 30.1 pts = 120 MNQ ticks; YM +11.2 bp = 49 MYM ticks | t 3.54, sd 60.53 bp per event (36.3 ES pts) | overnight leg on SPX basis 4.2 bp/event 2015-2023, 1.6 bp 2022-2023; quarterly 15.5 bp vs non-quarterly 7.0 bp (2026 text) | A-H1, A-H4 (eth leg), E-H1 |
| DF2-C3 (B1) | C2's exit or C1's entry made as a resting sell limit placed before 08:30 CT, filled only on a trade-through at or after the open | MES | limit live 08:25-08:35 | as C1/C2 | 12 | no published evidence on the book or fills at the open; the average path peaks in the 09:30 ET interval and falls 1.2 bp in the next 5 min, 2.9 bp in 10 min, 5.6 bp in 15 min (ES 2026 Fig 1) | not estimable | none | none | C-H4 (passive-fill reversal, unconditional) |

All three have the same mechanism: dealers' option delta drifts into the a.m. settlement, they buy
equities overnight, the SOQ prints high, and the price reverses once the payoff is fixed (2026 version).
Topstep: C2 enters after the 17:00 CT reopen and C1 exits before 15:10 CT, so both are inside one
trading day. The Thursday 15:00 CT close to 17:00 CT reopen window is not holdable and contributes
about -0.6 bp (ES) or +0.2 to +0.5 bp (NQ, YM).

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| ES futures Thc->Fro and Fro->Frc | +14.30 / -12.89 bp; t 3.54 / -2.40; sd 60.53 / 80.45 | "Panel c : E-mini / mean 2.69 0.91 3.60 -2.09 -1.71 14.30 -12.89 ... t-stat 2.75 0.68 2.12 -0.60 -0.28 3.54 -2.40 / Std 67.47 92.25 117.16 51.96 90.33 60.53 80.45" ; "Panel (c) reports statistics for a strategy that trades S&P 500 E-mini futures at open and close. The sample period is 2003.2 to 2021.12." | Table II, p.42 (txt l.1891-1910) | Baltussen, Terstegge, Whelan, "The Derivative Payoff Bias", version January 2024 (AFA program copy) | working-paper | pages/DF2/afa_viewp_98196.pdf |
| SOQ basis (untradeable open) is larger than futures | +18.54 / -16.91 bp | "Panel a : SOQ / SPX mean 2.30 1.06 3.59 -3.17 -0.55 18.54 -16.91 ... t-stat ... 4.65 -2.99" | Table II Panel a | same | working-paper | same |
| ES path, 2003-2023 | about 12 bp overnight, reverts by noon | "The average overnight cumulative return in the active futures contract is equal to 12 bps, which completely reverses by noon." ; "prices drift up overnight, accelerating in early morning trade until the 9:30 interval, at which point returns sharply revert" | Section II.A, p.9 (txt l.346-353) | Baltussen, Terstegge, Whelan, "The Third Friday Price Spike", version August 2026, julianterstegge.com | working-paper (R&R RFS per author page) | pages/DF2/btw_third_friday_price_spike_2026.pdf |
| ES futures method | 5-min VWAP, front month, 2003-2023 | "Futures intraday returns are computed from 5-minute volume-weighted average (VWAP) prices on E-mini futures. Our futures sample spans January 2003 to December 2023" | p.8 (l.329-331) | same 2026 | working-paper | same |
| Digitized ES path (2026 Fig 1, 3rd-Friday line), cumulative bp from Thu 16:00 ET | 18:00 ET -0.57; 03:00 ET 3.36; 06:00 8.79; 09:00 9.25; 09:25 10.75; 09:30 12.18 (peak); 09:45 6.55; 10:00 3.61; 11:00 1.93; 12:00 -2.77; 13:30 -4.79 (trough); 16:00 -0.27. Other days: 09:30 1.96, 16:00 3.35 | figure, no quote; caption "Figure 1. The Third Friday Price Spike in S&P 500 E-mini Futures" | p.40 of PDF (page index 40), vector paths 74/75, y-calibration from axis ticks (0 bp at y=343.21, 11.12 px/bp) | same 2026 | working-paper (digitized by DF2) | pages/DF2/btw_third_friday_price_spike_2026.pdf; scripts in scratchpad series.py |
| Digitized ES path (2024 Fig 1, 2003.2-2021.12) | 18:00 ET -0.33; 06:00 9.71; 09:30 13.84 (peak); 10:00 5.57; 12:00 0.06; 14:00 -1.85; 16:00 0.20 | text: "From around 2:00, which is the opening of the London market, equity prices drift steadily up ... until exactly the 9:30 interval ... The average overnight cumulative return in the active futures contract is equal to 14 bps which completely reverses by 12:00." | p.12-13 (l.488-492); figure page index 2 | 2024 version | working-paper | pages/DF2/afa_viewp_98196.pdf |
| NQ and YM | NQ 14 bp, YM 12 bp overnight, reversal of the same size by noon | "The NDX (DJIA) displays a overnight return before the option expiry of 14 bps (12 bps), followed by a significant reversal of about the same size between expiry and noon on the 3rd Fridays" ; caption "Figure 6. 3rd Friday Price Spike in Nasdaq and Dow-Jones futures ... The sample period is 2003.2 - 2021.12." | Section E "Other Markets", p.16 (l.668-672); Figure 6 p.36 (the brief's "Figure 5" is Figure 6 in this version; Figure 5 is positive vs negative spikes) | 2024 version | working-paper | same |
| Digitized NQ path (Fig 6a) | 18:00 ET 0.22; 06:00 11.83; 09:30 13.90 (peak); 10:00 1.37; 12:00 -5.67; 15:00 -10.09; 16:00 -8.41. Other days 09:30 4.82, 16:00 6.11 | figure | page index 36, paths 36/37, 0 bp at y=230.72, 6.178 px/bp | 2024 | working-paper (digitized) | same |
| Digitized YM path (Fig 6b) | 18:00 ET 0.47; 09:30 11.64 (peak); 10:00 5.06; 12:00 0.17; 14:15 -4.26 (trough); 16:00 -1.72 | figure | page index 36, paths 81/82, 0 bp at y=492.48, 9.485 px/bp | 2024 | working-paper (digitized) | same |
| NQ settlement differs (NOOP cross) | - | "Since November 2004 derivatives on this index settle on the NASDAQ Official Opening Price (NOOP) which is based on the first opening cross of every constituent ... based on the order imbalance among orders at the open book disseminated to investor between 9:25 and 9:30 a.m." | p.16 (l.675-682) | 2024 | working-paper | same |
| Quarterly vs off-quarter (SOQ basis) | quarterly +27 / -37 bp; off-quarter +14 / -6 bp | "Effects are stronger on the quarterly triple-witch days, with a 3rd Thursday overnight return of on average 27 bps, reverting -37 bps intraday on the third Friday. Off-quarterly expiries still display a strong reversal pattern around the publication of the SOQ, equal to 14 bps overnight and -6 bps intraday." | Section IV.B, p.14-15 (l.584-587), Table III | 2024 | working-paper | same |
| Quarterly vs non-quarterly overnight (2026) | 15.5 vs 7.0 bp | "the spike is present in both groups, averaging 15.5 basis points on quarterly and 7.0 basis points on non-quarterly expirations." | Section II.C, p.10 (l.401-403) | 2026 | working-paper | 2026 pdf |
| Full SPX sample, 1992-2023 | +9.80 (t 3.04) / -15.10 (t -3.57) bp, 371 expiries | "mean 9.80 -15.10 1.30 2.47 8.50 -17.58 / t-stat (3.04) (-3.57) (1.66) (2.25) (2.41) (-3.50)" ; "the sample contains 371 3rd Friday expirations" | Table I, p.33 | 2026 | working-paper | 2026 pdf |
| Post-2011 subsample (SPX/SOQ) | +10.07 (t 2.20) / -15.51 (t -2.34) | "mean 10.07 -15.51 -13.14 -5.13 / t-stat (2.20) (-2.34) (-1.66) (-0.59)"; "The sample period runs from September 2011 ... to December 2023." | Table II, p.34 | 2026 | working-paper | 2026 pdf |
| No spike at p.m. settlement | - | "Overall, we find no evidence of a pre-settlement spike around p.m. settlement and weak evidence of a post-settlement decline." | p.11 (l.427-428) | 2026 | working-paper | 2026 pdf |
| Persistence | combined about 25 bp per expiry, $1 -> $2.52 | "the combined strategy, which averages approximately 25 basis points per expiration and turns one dollar in November 1992 into $2.52 by December 2023" | p.10 (l.397-399) | 2026 | working-paper | 2026 pdf |
| Subperiod means, digitized from 2026 Fig 3 (SPX/SOQ basis, log cumulative; check: full sample 9.6 / 15.1 bp vs Table I 9.80 / 15.10) | overnight long: 2003-14 26.2, 2015-23 4.2, 2016-23 6.9, 2019-23 14.6, 2021-23 2.0, 2022-23 1.6 bp/event; intraday short: 15.2, 17.6, 17.4, 26.4, 19.9, 14.8 | figure; caption "The gray solid line shows cumulative log returns from a long position from 3rd Thursday close to 3rd Friday open. The gray dotted line shows cumulative log returns from a short position from 3rd Friday open to 3rd Friday close." | p.41 (page index 41) paths 210/211/212; 0 at y=553.02, 128.95 px per unit log return; event index = months since Nov 1992 less 3 excluded expiries | 2026 | working-paper (digitized) | 2026 pdf; scratchpad fig3.py |
| Reversal regression | slope about -0.4, R2 10-25% | "Coefficients are sizable (about -0.4), with (unreported) R2 values of roughly 10% to 25% ... Toward the close, the reversal effect weakens and becomes insignificant" | p.9 (l.367-370) | 2026 | working-paper | 2026 pdf |
| Order flow at the open (B1 context) | overnight +2.63, intraday -11.26 thousand contracts signed volume | "Overnight they are significant and positive (2.63, t-statistic = 3.59), whereas intraday they turn roughly six times more negative than on non-expiry days (-11.26, t-statistic = -5.38)." | Section IV.A, p.16 (l.655-657) | 2026 | working-paper | 2026 pdf |
| Conditional on dealer delta drift | non-quarterly: +17 bp if DDD < 0, -2 bp if DDD > 0 | "Overnight returns average 17 bps when DDD is negative, but turn negative at -2 bps when DDD is positive (Panel (b)). In the non-quarterly sample, 113 expirations have a negative projected drift and 105 a positive drift. The difference between the two groups is 19 bps (t-statistic = 2.16)." | p.26 (l.1070-1074) | 2026 | working-paper | 2026 pdf |
| Holiday rule | expiry moves to the preceding business day | "In cases where the 3rd Friday is not a trading day, expiration occurs on the immediately preceding business day, most commonly a Thursday." | footnote 7, p.8 | 2026 | working-paper | 2026 pdf |
| Futures roll in the paper | roll a few days before quarterly expiry | "We use the front-month futures contract and roll into the next-to-maturity contract when it becomes more liquid, typically a few days before quarterly expiry ... results are very similar when using the expiring futures contract until its expiry." | footnote 8, p.8 | 2026 | working-paper | 2026 pdf |
| SPX a.m. options now trade in GTH up to settlement | rule approved 2025-06-10 | "expiring A.M.-settled non-Volatility index options would trade through the end of the GTH trading session on the expiration date" | SEC Release 34-103219, p.1 | SEC order on SR-CBOE-2025-011, June 10, 2025 | exchange-regulator | pages/DF2/sec_34-103219.pdf |
| A.M.-settled SPX dailies approved | approved 2026-06-12 | "Order Approving a Proposed Rule Change to Permit the Listing of A.M.-Settled Options on the S&P 500 Index that Expire on Any Monday, Tuesday, Wednesday, Thursday, or Friday (other than the Third Friday-of-the-Month or Days that Coincide with an End-of-Month Expiration)" ; "June 12, 2026." | SEC Release 34-105678, title, p.1 | SEC order on SR-CBOE-2026-044 (Federal Register public inspection 2026-12157) | exchange-regulator | pages/DF2/fr_2026-12157.pdf |
| Monthly expiry dates 2025-2026 | see section 5 | calendar marks (navy box, legend "Equity, Equity Index, ETF & ETN Options Standard Expiration"; yellow "Exchange Holiday") | Cboe 2025 and 2026 Options Expiration Calendars, page 1, read from vector fills | Cboe (res-certification.cboe.com PDFs) | exchange-regulator | pages/DF2/cboe2025_options_calendar.pdf, cboe2026_options_calendar.pdf |

## 4. Negative evidence

- The tradeable futures intraday leg is smaller than the SOQ leg: -12.89 bp futures against -16.91 bp
  SOQ/SPX (Table II 2024). The paper's headline numbers on the SOQ basis cannot be traded.
- Off-quarter intraday reversal is small: "equal to 14 bps overnight and -6 bps intraday" (2024, p.15).
  If the roll blackout or a design choice drops quarterly expiries, the published intraday leg falls to
  about -6 bp (SOQ basis) on 8 to 10 events a year.
- The overnight leg decays (SPX basis, digitized 2026 Fig 3): 26.2 bp per event over 2003-2014, 4.2 bp
  over 2015-2023, 1.6 bp over 2022-2023 (24 events). The intraday short leg holds up (14.8 bp in
  2022-2023), but each digitized subperiod mean has n = 24 to 108 and per-event sd of 60-85 bp (Table II),
  so the standard error is about 12-17 bp at n = 24. None of the subperiod means is significant on its own.
- Dispersion: per-event sd 60.53 bp (ES overnight) and 80.45 bp (ES intraday). At n = 12 a year the
  sd of the yearly mean is about 23 bp, larger than the effect.
- Toward the close the reversal "weakens and becomes insignificant" (2026, p.9). The digitized ES path
  recovers from -4.79 bp at 13:30 ET to -0.27 bp at 16:00 ET.
- Related overnight evidence decays: the Boyarchenko-Larsen-Whelan 2:00-3:00 a.m. ET drift was reported
  faded since 2021 (NY Fed Liberty Street, July 2026, seen only in a search summary: [unverified], not
  fetched). That is a different, unconditional effect.
- No study after 2023 was found. The 2026 paper's samples all end December 2023. Elms (2026), "From
  Pinning to Amplification ... 2016-2025" (SSRN 6564078) is unread: SSRN is blocked, and the only hit was a
  Substack summary that I did not fetch. The search summary says it studies SPY pinning and daily
  ranges, not the SOQ spike [unverified].

## 5. Data and cost

- Needs: MES/ES (also MNQ, MYM) 1-minute bars around 15:00 CT Thursday through 15:00 CT Friday on
  monthly expiries, and a monthly a.m.-settlement calendar. The program owns 1-minute futures bars
  (section 4 of the shared brief); no data purchase is needed. Optional conditioning on the dealer delta drift
  needs Cboe Open-Close dealer positions (not owned; price not looked up in this run).
- Monthly a.m.-settlement dates inside 2025-04-01..2026-06-19, from the Cboe calendars (navy
  "Standard Expiration" boxes; holiday boxes in yellow):
  2025-04-17 (Thu; 04-18 Good Friday marked Exchange Holiday), 2025-05-16, 2025-06-20 (Q), 2025-07-18,
  2025-08-15, 2025-09-19 (Q), 2025-10-17, 2025-11-21, 2025-12-19 (Q), 2026-01-16, 2026-02-20,
  2026-03-20 (Q), 2026-04-17, 2026-05-15, 2026-06-18 (Thu, Q; 06-19 Juneteenth marked Exchange Holiday).
  15 events: 5 quarterly, 10 non-quarterly. On the two Thursday expiries the run-up window is Wednesday
  close to Thursday open (footnote 7 rule). The calendar also marks the Thursday before each expiry
  (2026: green "Last day to trade Expiring" box), which matches the a.m. contracts' last trading day.
- Roll blackout (docs/SCREENING.md l.25): "The splice trade date plus the 2 sessions before it, from the
  vendor roll schedule." Whether a quarterly 3rd Friday falls in it depends on the vendor splice date,
  which I did not read (data boundary). The paper rolls "typically a few days before quarterly expiry".
  If the vendor splice is about a week before expiry, the quarterly Friday lies after the blackout. The
  lead checks this against the roll schedule. On quarterly Fridays the contract held should be the next
  one. The expiring ES stops trading at the 08:30 CT open [unverified: CME page not fetched by rule].

## 6. Prop compatibility

- Topstep: C2 enters at or after the 17:00 CT Thursday reopen and exits by 08:30 CT. C1 enters at
  08:30 and exits by 15:00 CT. Both are inside one trading day and flat before 15:10 CT. The Thursday
  close-to-reopen gap is not held, and the digitized paths show it carries no run-up (ES -0.6 bp).
- Combined C2 then C1 (long overnight, flip short at the open) is one trading day. The flip at 08:30 CT
  is a market event, so slippage at the open applies (D8 opening bucket; lead).
- DLL: per-event sd about 36-48 ES pts is $180-$240 per MES lot, and much larger on MNQ (NQ sd unknown).
  Size must keep a 2-3 sd day inside the DLL.
- P06: 3rd Fridays are not scheduled major releases as such. Some may fall on release days; check the
  release table for each date (not checked).
- No HFT; one or two orders per event; semi-automated or manual execution is feasible (V39).

## 7. Overlap with tested mechanisms

- E-H3 (quarterly witching short, 14:30-15:00 CT): same expiry days for the quarterly subset, but a
  different window (end of day, not the open) and a quarterly-only calendar. The digitized path shows
  14:00-15:00 ET (13:00-14:00 CT) rising on 3rd Fridays. E-H3's window misses the effect.
- A-H1 (European-open overnight drift, every day), A-H4 (session-open hold, eth and rth legs),
  D-H4 (overnight gap fade): unconditional. DF2-C1/C2 restrict to the 12 a.m.-settlement days.
- C-H4 (reversal with passive fills): generic. DF2-C3 is passive fills conditioned on the expiry calendar.
- E-H1 (macro drift, overnight-through-day hold from 17:00 CT): the same holding shape as C2, with a
  different calendar.

## 8. Earlier verdicts (re-dig check)

- RD4 and R12 numbers are SUPPORTED: Table II E-mini 14.30 / -12.89, t 3.54 / -2.40, sd 60.53 / 80.45
  (quote above). The only correction is the label: "Panel c : E-mini" in the January 2024 version.
- R12-C1 note "fully reverts afterward by about noon": SUPPORTED for ES (2026 text "completely reverses
  by noon"). The digitized path adds that most of the move comes in the first 30 minutes and that the
  trough is at about 12:30 CT.
- R12's statement that NQ/YM numbers were not read: now read (14 and 12 bp overnight; digitized paths above).

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| julianterstegge.com (author page, home) | 2026-10-18T13:30Z (first DF2 run) | 78548d9d7dcca733 | pages/DF2/julianterstegge_home.html | ok | first run |
| https://julianterstegge.com/assets/papers/third_friday_price_spike.pdf (link on the author page; first run, exact UTC not logged) | about 2026-10-18T13:30Z | 0e4dd3c65b8060c5 | pages/DF2/btw_third_friday_price_spike_2026.pdf | ok | first run |
| AFA program copy, January 2024 version (afajof.org; first run, URL not logged beyond file name afa_viewp_98196) | about 2026-10-18T13:25Z | 841d9c2e183e6f04 | pages/DF2/afa_viewp_98196.pdf | ok | first run (WebFetch) |
| Cboe 2025 / 2026 options expiration calendars (res-certification.cboe.com) | about 2026-10-18T13:27Z | 6bdc3ed80c411b20 / 421a0699055b99eb | pages/DF2/cboe2025_options_calendar.pdf, cboe2026_options_calendar.pdf | ok | first run |
| Terstegge CV (umich) | about 2026-10-18T13:29Z | 3d05e8b470db1b0a | pages/DF2/terstegge_cv_umich.pdf | ok | first run |
| https://www.sec.gov/... 34-103219.pdf | about 2026-10-18T13:33Z | 953ba6629dbb081f | pages/DF2/sec_34-103219.pdf | ok | first run |
| Cboe notice 55365 "Cboe Options Exchange Updates AM-Settled Index Options Closing Time" | about 2026-10-18T13:32Z | 6ca1802bef128f8b | pages/DF2/cboe_notice_55365.html | partial: body is JavaScript-rendered, only the title was readable | first run |
| https://public-inspection.federalregister.gov/2026-12157.pdf | 2026-10-18T18:19:57Z | 366f424fdadeb5d3c245f406985e1e953914b2c92b17eaef1b2eaa5221c64280 | pages/DF2/fr_2026-12157.pdf (+ .txt) | ok | WebFetch |
| https://www.risk.net/investing/7957783/witching-day-price-spikes-point-to-options-market-manipulation-study | 2026-10-18T18:21Z | not saved (paywalled) | - | paywalled: only "Looking at futures data from February 2003 to December 2021" visible | WebFetch |
| https://www.cboe.com/notices/content/?id=55365 | 2026-10-18T18:25Z | not saved | - | partial: title only (JS-rendered) | WebFetch |
| https://ww2.cboe.com/us/options | 2026-10-18T18:25Z | not saved (scratch) | scratchpad | ok, no relevant text | scrapling extract get |

Terms: lines for res-certification.cboe.com, afajof.org, julianterstegge.com and www.sec.gov were logged by the first
DF2 run. This run appended public-inspection.federalregister.gov. WebSearch calls this run: 6 of 15. No
budget notices. OpenAlex not called. Firecrawl not used.

## 10. Unfinished and unverified

- Elms (2026) SSRN 6564078: unread (SSRN blocked; no open copy found).
- No 0DTE-era futures evidence (2024-2026) on the 3FPS was found. The paper's sample ends 2023.
- Cboe notice 55365 body unread: WebFetch at 2026-10-18T18:25Z returned only the title and navigation.
  A Scrapling get of ww2.cboe.com/us/options (scratch only, not evidence) had no matching text. A
  WebSearch summary says SPX expiring a.m. options would stop at 09:25 ET in GTH, with the effective trade
  date later "to be determined" (2025-09-25 update) [unverified, search summary only]. So it is unknown
  whether the change was live during 2025-04..2026-06. The SEC approval is dated 2025-06-10.
- A.M.-settled SPX dailies (approved 2026-06-12) and the SPXO weeklies (news pointer: effective
  2026-11-09, [unverified]) post-date the research window. They could dilute the 3rd-Friday
  concentration going forward.
- The digitized values depend on the paper's plotted 5-min VWAP points. Whether the "09:30" point is the
  09:25-09:30 or the 09:30-09:35 bar cannot be told from the figure. Digitizing error is about 0.1 bp.
  The OA tables (A.3, A.4) with futures detail for 2003-2023 were not in the saved copies.
- No evidence on ES book depth or fill rates at the 08:30 CT open on expiry days (B1).
- The first run's exact fetch URLs and UTC times were not logged. The times above come from file mtimes
  (PDT 06:23-06:32 = 13:23-13:32Z).
- Press coverage with numbers (Bloomberg, Barron's): not fetched (paywalls).
