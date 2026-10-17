# Stage E.23 P1.2 mechanism memo: M6_AUCTION (Treasury auction cycle)

Worker: MechanismReaderM6_AUCTION-OpusHigh. Brief: reports/stage_e23_briefs/brief_mechanism.md.
Written 2026-10-17, from 02:25 PDT (shell clock). Pages and the fetch log are in
reports/stage_e23_briefs/mech_pages/M6_AUCTION/ (fetch_log.md has the URL, PDT fetch time, sha256 and tool for each).
No market data was opened. No member was run.

Members (strategy/members/k2/aucpre.py, aucpost.py docstrings): both fire on every tenor-matched Treasury auction date
(ZT 2Y, ZF 5Y, ZN and TN 10Y, ZB and UB 30Y; T_a = competitive close, 13:00 ET = 12:00 CT on most dates).
- K2-aucpre-01: SELL from T_a-180 to T_a-1 min (the pre-auction concession). Fixed side.
- K2-aucpost-01: BUY from T_a+5 to T_a+185 min (the post-auction recovery). Fixed side.
For E.23 both triggers have the same trade date (the auction day) and the same entry (that day's settlement, after the
auction). Their multi-day legs are therefore the same position with opposite signs, not two independent hypotheses. The
question for both is the same: what happens to the auctioned tenor's price from the auction-day close to +5 and +20 days.

## (1) Evidence table

Saved paths are relative to reports/stage_e23_briefs/mech_pages/M6_AUCTION/ unless they start with reports/.
Durations used for the [derived] yield-to-price conversions (2Y 1.9, 5Y 4.5, 10Y 8.0, 30Y 15.8 years) are from HS19,
p.14: "the average duration for the 2-, 5-, 10- and 3-year on-the-run securities is equal to 1.9, 4.5, 8.0, and 15.8
years" (the "3-year" there is the paper's typo for 30-year, as the order 2, 5, 10, 30 shows).

| Key | Citation | URL | Saved path | sha256 (pdf / txt) | Verbatim quote (location) | Claim supported |
|---|---|---|---|---|---|---|
| LYZ13 | Lou, D., H. Yan, J. Zhang (2013), "Anticipated and Repeated Shocks in Liquid Markets," Review of Financial Studies 26, 1891-1912. Author draft, May 2013 | https://ifr.hkust.edu.hk/uploads/upload/files/20250212/f5cba4b7e2aa3ada8477ad2fc38fab02.pdf (also FMG DP684, https://www.fmg.ac.uk/sites/default/files/publications/DP684.pdf) | lou_yan_zhang_2013_hkust.pdf(.txt); lou_yan_zhang_fmg_dp684.pdf(.txt) | 98ad8352...e011d / 730d9d66...7e021 | Abstract: "Treasury security prices in the secondary market decrease significantly in the few days leading up to Treasury auctions and recover shortly thereafter, even though the time and amount of each auction are announced in advance." p.9: "The yield of 2-year notes increases, on average, by 2.53 basis points during the 5-day period before the auctions, and decreases by 2.32 basis points during the 5-day period afterward." p.10: "the yield of the on-the-run 5-/10-year notes increases by 2.67/1.57 basis points during the 5 days before auctions, and decreases by 2.74/2.00 basis points in the 5 days after." Table II (txt lines 1424-1458), Y(t)-Y(0) with Y(0) the auction-day yield, Newey-West t: 2Y "5 -2.32** (-2.18)", "10 -3.91** (-2.13)"; 5Y "5 ... -2.74*** (-2.63)", "10 ... -2.95* (-1.88)"; 10Y "5 ... -2.00 (-1.51)", "10 ... -4.68** (-2.00)"; obs 332 / 210 / 132. Sample: "January 1980 to June 2008" | Post-auction-close continuation of the price recovery (yields fall, prices rise) over +5 and +10 days. 2Y and 5Y t > 2 at +5; 10Y t 1.51 at +5, 2.00 at +10. Cash on-the-run (becomes off-the-run) notes, CRSP daily bid-ask mid. [derived] price: 2Y +4.4 bp (+5d), +7.4 bp (+10d); 5Y +12.3 / +13.3 bp; 10Y +16.0 / +37.4 bp. No +20 day figure (window ends at +10) |
| LYZ13-strategy | same | same | same | same | p.2: "By going short the on-the-run 2-year note and long a duration-matched portfolio ... during the 10 days before each 2-year note auction, and holding the reverse positions during the 10 days after, one can achieve an annualized Sharpe ratio of 0.84, after accounting for bid-ask spreads and repo funding costs." p.14 (txt line 772-776): "the average return of this trading strategy is 8.62 basis points (t = 3.65) per month. For the more recent sample period (1998-2008) ... 8.52 basis points per month, with a t-statistic of 4.95." | Pre-2008 profitability of the two-sided (pre and post) 10-day cycle trade, hedged. Not the one-sided long futures leg E.23 tests |
| FNR24 | Fleming, M., G. Nguyen, J. Rosenberg (2024), "How Do Treasury Dealers Manage Their Positions?" Journal of Financial Economics; NY Fed Staff Report 299, revised March 2024 | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr299.pdf | fleming_nguyen_rosenberg_sr299.pdf(.txt) | 49511bc1...ee6 / 5cf0ea75...de72 | Abstract: "Dealers are compensated for inventory risk by means of subsequent price appreciation of their holdings. Amid increased balance sheet costs attributable to post-crisis regulatory changes, dealers significantly reduce their position taking and layoff inventory faster." Table 8 (p.66; 1990-07-04 to 2020-12-30; yields "pre-adjusted for day-of-month effects"; NW 12 lags), Y(t)-Y(0): 2Y "5 −2.00∗∗∗", "10 −4.82∗∗∗"; 5Y "5 ... −2.57∗∗∗", "10 ... −2.75∗∗∗"; 10Y "1 ... 1.14∗∗∗", "2 ... 3.25∗∗∗", "3 ... 3.43∗∗∗", "5 ... −0.01", "7 ... −3.92∗∗∗", "10 ... −2.26∗∗"; auctions 366 / 322 / 245. p.37 fn 38: "Once we control for day-of-month effects, the 10-year note does not exhibit any significant effects in advance of auctions. The expected post-auction effects (a decrease in yield, or a price appreciation) only start to become significant after five days." | Same post-auction continuation for 2Y and 5Y on 1990-2020 (overlaps 2010-2020), robust to the month-end effect. [derived] price: 2Y +3.8 bp (+5d), +9.2 bp (+10d); 5Y +11.6 / +12.4 bp. 10Y: yields RISE on days +1 to +3 (price about -27 bp at +3, [derived]), net zero at +5, fall by +7 to +10 (+18 bp price at +10, [derived]). Standard errors not printed in Table 8, stars only |
| FNR24-decay | same | same | same | same | p.42: "The more important source of intermediary compensation—the post-auction appreciation of acquired inventory reported in the lower panel of the table—is significant in the earlier periods (mainly for the coupon securities) but dissipates after the crisis." Table 10 Panel B (p.68), next-week return per $1bn of dealer auction purchases, coefficient (NW se): 2Y pre-crisis "0.973∗∗ (0.402)", rule implementation (2015-2020) "0.461 (0.295)"; 5Y "2.788∗∗ (1.140)" vs "0.939 (0.772)"; 10Y "4.640∗∗ (2.004)" vs "0.922 (1.460)"; rule development (2010-2014): 0.178 (0.110), 0.440 (0.586), 0.461 (1.193). p.43: "an increase in investment funds' participation dampens the post-auction price appreciation" (five-day measure, ∆p ∝ −∆y(5)) | Post-publication / post-2010 decay of the week-after appreciation: insignificant in 2010-2014 and 2015-2020 for all three notes |
| FLN26 | Fleming, M., W. Liu, G. Nguyen (2026), "Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions," NY Fed Staff Report 1188, March 2026, revised July 2026 | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf | reports/stage_e20_briefs/pages/ZN/nyfed_sr1188.pdf(.txt) (reused, E.20) | 93f9b196...095b / 0103fe18...a6 | p.10-11: Lou et al. "find that yields increase by 2–3 bps in the days leading up to and including the auction day, and then decline by roughly 2 bps over the subsequent days. Although their study considers a 20-day window around each auction, most of the rise and subsequent reversal occurs within 3–4 days of the auction." p.19: "Over the full sample, the 10-day effect averages roughly 2–5 bps. Thus, the six-hour window we study accounts for approximately 25% of the total 10-day effect". p.20-21: "the strong auction-cycle effects documented by Lou et al. (2013), whose sample ends in 2008, do not persist at the same magnitude when the sample is extended through 2024." p.21 fn 14: "While yield pressure is significant over the full sample, the effect is most pronounced during 2007–2014 and weakens markedly in 2015–2024." Table 2 (p.46), 6-hour ∆Y(post): "−0.315∗∗ −0.394∗∗∗ −0.473∗∗∗ −0.438∗∗∗ −0.750∗∗∗ −0.235" (2,3,5,7,10,30Y); S3 2015-2024 yield pressure "0.419∗∗∗ 0.340∗ 0.919∗∗∗ 0.417∗ 0.593∗ 0.592" | 10-day (pre plus post) effect 2-5 bp yield, 1991-2024, weakening markedly in 2015-2024; most of the post-auction move within 3-4 days, so it mostly lies inside a 5-day hold. 30Y: intraday post leg not significant. The 10-day subsample numbers sit in Online Appendix Table A2, which I could not reach (see section 4) |
| HS19 | Hartley, J., K. Schwarz (2019), "Predictable End-of-Month Treasury Returns," working paper, November 22, 2019 | (E.20 source) | reports/stage_e20_briefs/pages/ZN/hartley_schwarz_2019.pdf(.txt) (reused) | 56403762...a32809 / 3f47ed6c...840197 | p.9-10: "Excess returns do indeed tend to be depressed on the days before auctions, and boosted on the days after auctions, in line with Lou, Yan and Zhang (2013)." "Our results show that that the auction is a significant, but distinct effect from the off-the-run month-end patterns that we document." Sample "January 1990 to the end of 2018" | Confirms the post-auction boost separately from the month-end effect (relevant because the 2Y, 5Y and 7Y auctions fall in the last week of the month, so a 5-day hold spans month-end). Daily |
| BGJW16 | Beetsma, R., M. Giuliodori, F. de Jong, D. Widijanto (2016), "Price Effects of Sovereign Debt Auctions in the Euro-zone: The Role of the Crisis," Journal of Financial Intermediation 25, 30-53; Tinbergen DP 13-150/VI, Sept 2013 | https://papers.tinbergen.nl/13150.pdf | beetsma_etal_ti13150.pdf(.txt) | 59d0f87c...d25 / 1ed99163...80d5 | Abstract: "secondary-market yields on Italian public debt increase in anticipation of auctions of new issues and decrease after the auction, while no or a smaller such effect is present for German public debt. However, these yield movements on the Italian debt are largely confined to the period of the crisis since mid-2007." p.1: "Yields revert to their original level again three to five days after the auction." | Analog (euro sovereigns, 1999-2013): the post-auction decline lasts 3-5 days; it is absent or small in the safe-haven market (Germany) and concentrated in stress periods. Daily |
| SWX25 | Somogyi, F., J. Wallen, L. Xu (2025), "Treasury Auctions and Long-Term Bond Yields," draft 22 May 2025 (FRBSF/BoC/FRB-C fixed income conference) | https://www.frbsf.org/wp-content/uploads/Somogyi-paper.pdf | somogyi_wallen_xu_frbsf2025.pdf(.txt) | 75963f96...d5 / bfc8fa64...112d | Abstract: "we find that long-term bond yields have declined over a narrow 3-day window around US Treasury auctions." p.1: "On average, over a narrow 3-day window around each Treasury auction, US yields fall by 1.04 bps". p.18: "much of the decline in USD and G10 yields occurs on the second trading day after the auction, not immediately after the auction. This is consistent with ... primary dealers gradually offload their inventory after auctions to investors (Fleming et al., 2024)." | 10Y yield, 1994-2021, around 5+ year auctions: part of the move comes after the auction-day close (day +2), the same direction as the recovery (price up). The 3-day window starts at t-1, so it includes the auction day; the post-close part alone is not given as a number in the lines I read |
| SWX25-later | Somogyi, Wallen, Xu (2025), "What Treasury Auctions Reveal About Investor Demand," 6 Dec 2025 | https://finance.darden.virginia.edu/wp-content/uploads/2025/12/Somogyi_Wallen_Xu_2025_What_Treasury_Auctions_Reveal_About_Investor_Demand.pdf | not saved (HTTP 404, no Wayback copy) | - | [unverified: search-result abstract only] "Prior to 2010, long-term yields declined on average by 1.5 basis points after auctions ... After 2010, this trend has reversed" | Would be direct post-2010 decay evidence; unverified |
| DUF25 | Duffee, G. (2025), discussion of Somogyi, Wallen and Xu, FRBSF/BoC/FRB-C Fixed Income Conference, May 2025 (slides) | https://www.frbsf.org/wp-content/uploads/Duffee-Slides.pdf | duffee_slides_frbsf2025.pdf(.txt) | 7267016f...dd37 / 49929a4e...e4c2 | Slide 6: "Mean change of −1 b.p. from day t − 1 to t + 2"; "Mean change of −0.5 b.p. from day t − 5 to day t + 5"; "In line with mean daily change of −0.06 b.p. from 1994 through 2021". Slide 11: "In US data, the bid-to-cover innovation has explanatory power only for change from the close before the auction to the close on auction day" | Over 10 days the 10Y yield change around long-term auctions is no larger than the 1994-2021 bond-market trend. The auction demand surprise is priced on the auction day itself, with no drift after it. Against a multi-day post-auction effect in the 10Y |
| FJ15 | Fleming, M., C. Jones (2015), "Dealers' Positions and the Auction Cycle," Liberty Street Economics, Oct 14, 2015 | https://libertystreeteconomics.newyorkfed.org/2015/10/dealers-positions-and-the-auction-cycle.html | libst_2015_dealers_auction_cycle.html(.txt) | (html) see fetch_log / d5fd7bd0...33a4 | "As of the first Wednesday after a security's issuance, dealers' net positions in the benchmark securities increase a statistically significant $3.1 billion (for seven-year notes) to $5.9 billion (for three-year notes) ... In subsequent weeks, dealers' net positions decline, and by a cumulative amount over the subsequent three weeks that is roughly similar to the increase seen in the first week." (post-crisis sample from April 2013) | Mechanism, post-2013: dealer inventory from the auction is unwound over about 3 weeks. Quantities only, no returns |
| CD11 | Collin-Dufresne, P. (2011), discussion of Lou, Yan and Zhang, US Treasury conference, Nov 2011 (slides) | https://home.treasury.gov/system/files/276/2011-session-2-yan-shocks-in-liquid-market-DISCUSSION-collin-dufresne.pdf | collin_dufresne_2011_discussion.pdf(.txt) | eda1514d...db58 / c31a6c46...739d | "It seems hard to reconcile consistent sharpe ratio of 1.5 in a liquid market since 1980 with 'slow-moving' capital"; "Hedge funds (not insurance company) should have moved into this trade if the profits are indeed significant and sizable."; "Repo specialness? (strategy requires shorting the on-the run note and buying back when it becomes off-the-run)" | Grounds to expect decay after publication, and a measurement concern (on-the-run to off-the-run switch, repo specialness) that futures avoid but that also means the cash-note numbers may not carry over to futures one for one |
| TM24 | Trademachine (2024), "Anomalies in US Treasury Bond Prices During Auction Weeks," Substack, Mar 14, 2024 | https://trademachine.substack.com/p/anomalies-in-us-treasury-bond-prices | trademachine_auction_weeks.html(.txt) | (html) see fetch_log / 20c7936d...449c | "Go long on TLT X days ahead of the auction, sell Y days after." Optimize (X, Y) for a positive return." "The average daily gain in the assessed hold periods is 0.06%, which is much better than on any random days (0.02%)." | Practitioner, in-sample optimized, no statistics or sample dates. Anecdote only; not used for strength |

## (2) Per-member paragraphs

Both members share one event set and one E.23 entry point, so the evidence is the same; only the direction label
differs. Strength is given per root because the evidence differs by tenor.

### K2-aucpre-01 (SELL into the auction; E.23 holds from the auction-day settlement)

- Direction: **opposite side** to the member (the literature predicts that prices RISE after the auction-day close, so the
  multi-day leg is long, a reversal of the member's pre-auction sell).
- Strength: **moderate** for ZT (2Y) and ZF (5Y): by the letter of the brief's rule this is "strong" on FNR24's 1990-2020
  full sample (multi-day, this event, t >= 2 by stars, sample overlaps 2010-2020). But the same authors (FNR24 Table 10)
  and FLN26 document that the effect fades after 2010/2014, and the one direct post-2010 statement (SWX25-later) is
  unverified. The lead decides. **Weak** for ZN and TN (10Y): LYZ13 t 1.51 at +5. FNR24 shows yields rising on days +1 to
  +3 and net zero at +5, with a decline only by +7 to +10. DUF25 finds no 10-day effect beyond trend. **Weak** for ZB and
  UB (30Y): no multi-day study of the 30Y auction was found. FLN26's intraday 30Y post leg is not significant. Only the
  mechanism (dealer inventory) carries over.
- Horizon: 5 days for 2Y and 5Y (both studies). 10 days is also covered (2Y, 5Y; 10Y only at +10). 20 days: **neither**.
  No paper reports +20. Because the same tenor is auctioned monthly, day +20 is about the next auction day of that tenor,
  where the cycle puts yields back near their peak (LYZ13 Table II has Y(t) < Y(0) on both sides). So the cycle itself
  predicts a net 20-day move near zero [derived from the cycle's structure; not a published estimate].
- Magnitude (gross, per event, from the auction-day close; the yield figures are published, the price conversions are
  [derived] with the HS19 durations):
  - 2Y, +5d: LYZ13 −2.32 bp yield (t −2.18, 1980-2008), about +4.4 bp price. FNR24 −2.00 bp*** (1990-2020), about +3.8 bp.
  - 2Y, +10d: −3.91 bp (t −2.13), about +7.4 bp price. FNR24 −4.82***, about +9.2 bp.
  - 5Y, +5d: LYZ13 −2.74 bp (t −2.63), about +12.3 bp price. FNR24 −2.57***, about +11.6 bp.
  - 5Y, +10d: −2.95 (t −1.88), about +13.3 bp price. FNR24 −2.75***, about +12.4 bp.
  - 10Y, +5d: LYZ13 −2.00 (t −1.51), about +16 bp price. FNR24 −0.01, about 0.
  - 10Y, +10d: LYZ13 −4.68 (t −2.00). FNR24 −2.26**, about +18 to +37 bp price.
  - 30Y: no multi-day figure.

  Decay: FNR24 Table 10's week-after appreciation is insignificant in 2010-2014 and 2015-2020 for 2Y, 5Y and 10Y. Point
  estimates fall to about one-half (2Y) and one-fifth to one-third (5Y, 10Y) of pre-crisis. FLN26: the 10-day effect
  "weakens markedly in 2015–2024". Its 6-hour pressure in 2015-2024 is "less than half" of earlier. Treat the 2010-2024
  per-event gross as well below the full-sample figures above; no paper gives a 2015-2024 five-day number I could
  verify.

  Conversion caveats for the lead (cost check against D8): the figures are for cash on-the-run notes, which become
  off-the-run after the auction (LYZ13 p.8). Futures track the CTD. Use E.20's conversions:
  - ZT: 2.69 ticks per bp of price at P = 105 (reports/stage_e20_briefs/product_ZT.md lines 7-13).
  - ZF: tick = 0.66 bp of price (reports/stage_e20_briefs/pages/ZF/zf_conversions_output.txt).
  - ZN: cash 10Y x0.69 (reports/stage_e20_briefs/product_ZN.md line 21).
- Reason: Dealers have limited risk-bearing capacity and end investors' capital moves slowly (LYZ13 abstract; FNR24
  abstract; FLN26 p.1; Duffie 2010 as cited by FLN26 p.6). So the auction's supply goes first onto dealer balance sheets
  and is distributed to end investors over the following days and weeks. FNR24 finds that part of dealers' auction
  purchases remains unsold at the end of the auction week (txt line 1013: "The 34% (31%) unsold inventory at the end of
  the auction week"). FJ15 finds the 2013-2015 dealer positions unwind over about three weeks. Dealers are paid by the
  later price appreciation (FNR24 abstract). The trigger day is the auction day. E.23's entry at its settlement comes
  after the concession has formed and after the first hours of the recovery that K2-aucpost-01 trades. FLN26 p.19 says
  the 6-hour window is about 25% of the 10-day effect, and that most of the move is within 3-4 days. So the remaining
  recovery over the next few days favours a long. This is not post-announcement drift on news: DUF25 slide 11 shows the
  auction's demand surprise is priced by the auction-day close. The predicted move is a supply-absorption recovery,
  which the post-2010 entry of investment funds and other non-dealers into the primary market has weakened (FNR24 p.43;
  FLN26 p.21). Disagreement: for the 10Y, FNR24 finds the opposite sign on days +1 to +3. I assume, though the authors
  do not say so, that this comes from the 30Y auction the next day and the 10Y reopening cycle. DUF25 finds no 10-day
  move beyond trend around long-term auctions. BGJW16 finds the effect absent or small in the safe-haven market
  (Germany) and confined to crisis periods in Italy.

### K2-aucpost-01 (BUY after the results; E.23 holds from the auction-day settlement)

- Direction: **same side** as the member (long). The continuation of the post-auction recovery past the 180-minute
  intraday window is the post-auction leg of the multi-day auction cycle.
- Strength: same as K2-aucpre-01, by root. **Moderate** for ZT and ZF (strong by the rule's letter on 1990-2020, with
  documented post-2010 decay). **Weak** for ZN and TN. **Weak** for ZB and UB (no multi-day 30Y study; FLN26's intraday
  30Y post leg n.s.: Table 2 ∆Y(post) 30Y "−0.235", no star).
- Horizon: 5 days (2Y, 5Y). 10 days (2Y, 5Y, 10Y at +10 only). 20 days neither (no evidence; the cycle's structure
  predicts about zero, [derived]).
- Magnitude: identical to K2-aucpre-01 above. These are the same post-close yield changes; only the sign label differs.
  One point specific to this member: its own intraday P&L (T_a+5 to T_a+185) is excluded in E.23. FLN26's figures say
  that intraday piece is about a quarter of the 10-day (pre plus post) effect. The remaining post-close recovery is the
  part LYZ13 and FNR24 measure from Y(0).
- Reason: same mechanism as K2-aucpre-01: dealer inventory from the auction is distributed over days (FNR24, FJ15).
  Part of the decline comes on the second day after the auction (SWX25 p.18, long-term auctions, 10Y yield, 1994-2021).
  This supports continuing the post-auction buy across the next few closes. The same decay and disagreement sources
  apply (FNR24 Table 10, FLN26 fn 14, DUF25, BGJW16 Germany, CD11 on why such a trade should have been arbitraged).
- Note for the lead: in E.23 the two members' multi-day legs are one bet (long from the auction-day settlement), with
  aucpre's sign flipped. Counting them as two hypotheses would double-count one effect.

## (3) Query log

The clock times are brackets taken from shell timestamps around each call (PDT, -07:00). The WebSearch tool returns no
time of its own. 15 WebSearch calls in all, under the cap of 60. No over-budget notice was seen.

| # | Query | Tool | Time (PDT) | Results kept |
|---|---|---|---|---|
| 1 | Lou Yan Zhang "Anticipated and Repeated Shocks in Liquid Markets" pdf | WebSearch | 02:16:33-02:17:49 | HKUST draft PDF, FMG DP684, Collin-Dufresne discussion (LYZ13, CD11) |
| 2 | Fleming Nguyen Rosenberg "How do Treasury dealers manage their positions" auction weeks | WebSearch | 02:16:33-02:17:49 | SR299 PDF (FNR24); Trademachine (TM24) |
| 3 | Sigaux "Trading ahead of Treasury auctions" working paper pdf | WebSearch | 02:16:33-02:17:49 | ECB WP 2208 located, not fetched (Italian pre-auction mechanism; no post-auction multi-day claim needed beyond FLN26's summary) |
| 4 | Fleming Liu Nguyen "Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions" online appendix | WebSearch | 02:18:43-02:19:21 | none (appendix not listed) |
| 5 | Treasury futures returns days after auction "auction cycle" post-2008 recovery 10-day | WebSearch | 02:18:43-02:19:21 | none new (Robeco intraday, already in E.20) |
| 6 | Beetsma Giuliodori de Jong Widijanto "Price effects of sovereign debt auctions in the euro-zone" pdf | WebSearch | 02:18:43-02:19:21 | Tinbergen DP 13-150 (BGJW16) |
| 7 | 30-year Treasury bond auction cycle yields days before after auction price pressure 2010-2020 | WebSearch | 02:19:26-02:20:21 | none (news only) |
| 8 | quantpedia Treasury auction cycle anomaly bond futures strategy Lou Yan Zhang replication | WebSearch | 02:19:26-02:20:21 | Quantpedia #304 listing (search snippet only; 1998-2008 backtest; not used), TM24 |
| 9 | "auction" "price pressure" Treasury "off-the-run" daily yields 2015-2024 weakened "10-day" window intermediaries | WebSearch | 02:19:26-02:20:21 | none new |
| 10 | "post-auction" Treasury note returns subsequent days after auction study dealers inventory 2015 2023 "auction cycle" | WebSearch | 02:20:21-02:21:44 | Liberty Street 2015 (FJ15) |
| 11 | Treasury bond futures auction calendar effect daily returns week after auction ultra bond T-bond | WebSearch | 02:20:21-02:21:44 | none (Phillot 2025 AEJ is announcement supply shocks, off-topic) |
| 12 | Treasury auction supply price pressure multi-day reversal "days after the auction" yields recent evidence 2024 2025 working paper | WebSearch | 02:21:48-02:22:09 | Duffee slides (DUF25), Somogyi et al. pointer |
| 13 | Somogyi Wallen Xu "Treasury Auctions and Long-Term Bond Yields" pdf | WebSearch | 02:22:10-02:22:31 | FRBSF draft (SWX25); Darden 2025 PDF (404) |
| 14 | "What Treasury Auctions Reveal About Investor Demand" Somogyi Wallen Xu | WebSearch | 02:23:04-02:23:34 | nothing new (same Darden PDF, 404; abstract via search only) |
| 15 | 2-year 5-year note futures returns week after Treasury auction 2015-2024 dealer balance sheet auction concession persistence | WebSearch | 02:23:34-02:25:03 | nothing new (news recaps, IMF figure on corporate bonds) |

Stopping rule: each member has its paragraph. More than 6 queries are logged, and the last 2 (14, 15) added no new
relevant source. The key papers LYZ13, FNR24, FLN26 and SWX25 (May 2025 draft) were read in full text by grep and line
ranges, and BGJW16 by abstract and introduction.

## (4) Not verified or not reached

- FLN26 Online Appendix Table A2/A3 (the 10-day, daily-data yield pressure by subsample 1991-2024, the one source that
  would give a 2015-2024 multi-day magnitude): not linked from https://www.newyorkfed.org/research/staff_reports/sr1188.html.
  Guessed URLs (sr1188_appendix.pdf, ?la=en, sr1188_onlineappendix.pdf) redirect to /errors/404. Only the text's
  qualitative statement ("weakens markedly in 2015–2024") is verified.
- SWX25-later (Dec 2025 version, "after 2010 yields no longer fall after auctions"): Darden PDF returns HTTP 404 (curl and
  `scrapling extract get`). No Wayback snapshot. The claim is [unverified], search-result abstract only. Firecrawl was
  not tried, because the host returns a real 404 and a different fetcher would not change that.
- No published multi-day study of 30-year bond auctions (ZB, UB) was found. No study of Treasury futures (as opposed to
  cash notes) over 5-20 days after auctions was found either. Robeco's ZN futures study (E.20,
  reports/stage_e20_briefs/pages/ZN/robeco_quant_chart_auctions.html) is intraday.
- No paper reports a +20-trading-day post-auction return. The 20-day statement above is derived from the monthly cycle's
  structure, not published.
- LYZ13's Y(0) is a CRSP daily bid-ask mid. The time of day of that quote relative to the CME settlement is
  [unverified]. If it is later than the futures settlement, part of the recovery may sit between the two.
- Sigaux (2024, JBF; ECB WP 2208) and Amin and Tedongap (2023, TIPS) were not read. They are cited only through FLN26's
  summaries (pre-auction mechanisms), not for any number here.
- FNR24 Table 8 prints significance stars without standard errors or t statistics. "t >= 2" for it is inferred from
  ** / *** (p < .05 / .01).
