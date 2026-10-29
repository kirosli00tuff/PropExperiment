"""FX_items.py: the FX reader's facts (Stage E.32b F2). Data only; FX_build.py assembles F2_fx.json."""

R = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/"
MY = R + "stage_e32b_briefs/pages/FX/"
E28 = R + "stage_e28_briefs/pages/A1_fx/"
E20 = R + "stage_e20_briefs/pages/6E/"
A1 = R + "stage_e28_briefs/A1_fx.json"
P6E = R + "stage_e20_briefs/product_6E.json"
ALL = ["M6E", "6E", "M6A", "6A"]
EUR = ["M6E", "6E"]
AUD = ["M6A", "6A"]

META = {
    "family": "fx",
    "worker": "FXReader-OpusHigh",
    "codes": ALL,
    "started_pdt": "2026-10-28 23:03",
    "finished_pdt": "2026-10-28 23:17",
    "websearch_calls": 19,
    "fulltext_reads_t6": 4,
    "notices": [],
}

ITEMS = [
    # ---------------- T1 spread and touch ----------------
    dict(codes=["6E"], topic="T1", field="median_spread_ticks", value=1.2, scope="product",
         window="June 2021 (CME FX Market Profile data); whole trading day",
         detail=("STATISTIC IS AN AVERAGE, NOT A MEDIAN: time-weighted average top-of-book spread of outright EUR/USD "
                 "futures, about 0.6 pips over the whole trading day (not split by session; CME says TOB spreads are "
                 "'consistent throughout the trading day'). 0.6 pip = 0.00006 = 1.2 ticks of 6E (tick 0.00005); "
                 "arithmetic E.28's. No median main-session figure found."),
         quote="At the top of the book, outright FX futures have the tightest pricing (white line), at an average of around 0.6 pips.",
         source={"file": E28 + "cme_fx_market_profile_usecase.html", "field": "A1_fx.json [code=6E].median_spread_ticks"},
         verified="reused"),
    dict(codes=["6E"], topic="T1", field="touch_size", value="about USD 3.5 million at the top of book (about 23 contracts, my arithmetic)",
         scope="product", window="June 2021 (CME FX Market Profile); whole trading day",
         detail=("Average top-of-book size of outright EUR/USD futures, June 2021, statistic not stated beyond 'typical'; "
                 "not split by session. Conversion (mine, assumption): EUR 125,000 x about 1.20 USD/EUR (June 2021) = "
                 "about USD 150,000 per contract, so USD 3.5m is about 23 contracts; if the figure is EUR notional, 28. "
                 "Same article: futures TOB size rose from about USD 1.8m (January 2021) to USD 3.0m (June 2021). "
                 "E.28 recorded touch size as null; this is a new fact from a page E.28 saved."),
         quote=("Whilst this can be compared to the TOB size for futures of around $3.5 million [...] "
                "futures seeing the greatest rate of growth rising from around $1.8 million at TOB in January to $3.0 million in June"),
         source={"file": E28 + "cme_fx_market_profile_usecase.html"}, verified="full_text"),
    dict(codes=["6A"], topic="T1", field="median_spread_ticks", value=1.0, scope="product",
         window="December 2020 to the week after Christmas 2020 (CME FX report 2021 Q1); whole trading day",
         detail=("MEDIAN over the whole trading day (distribution of the top-of-book spread in CME's FX Market Profile), "
                 "not a main-session median: 'median spread is now consistently 0.5 pips'. 0.5 pip = 0.00005 = 1 tick of 6A "
                 "(tick halved to 0.00005 on 2020-11-23). Same report: average TOB spread 0.75 pips in December 2020 "
                 "(1.5 ticks), weekly averages 1.15 pips before the change, 0.86 the week after, 0.68 the week after "
                 "Christmas. Page fetched via Wayback (cmegroup.com not fetched live)."),
         quote=("the average bid-ask spread for AUD/USD futures – the white line in the chart – is averaging 0.75 pips. [...] "
                "This shows that the median spread is now consistently 0.5 pips, with the market now rarely being wider than one pip."),
         source={"file": MY + "cme_fx_report_2021q1_in_our_markets_wayback.html"}, verified="full_text"),
    dict(codes=["6A"], topic="T1", field="touch_size", value="about USD 1.5 million average at the top of book (about 15 to 20 contracts, my arithmetic)",
         scope="product", window="three days after 2020-11-23 (tick change); whole trading day",
         detail=("Average size shown at the top of book through the day, three days after the tick was halved; "
                 "before the change sizes were 'sometimes in excess of $6 million' and the typical spread 1.1 pips "
                 "with 1 pip (then the minimum) the median. Conversion (mine): 6A is AUD 100,000; at about 0.74 USD/AUD "
                 "USD 1.5m is about 20 contracts, or 15 if the figure is AUD notional (CME does not say). Short window, "
                 "includes the US Thanksgiving week per the article."),
         quote=("In the three days after the change, the average size shown at the top-of-book throughout the day was $1.5 million. [...] "
                "futures had a typical spread of 1.1 pips throughout the trading day, perhaps slightly wider in the London morning."),
         source={"file": MY + "cme_aud_tick_change_review_wayback.html"}, verified="full_text"),
    dict(codes=["M6E", "M6A"], topic="T1", field="median_spread_ticks", value=None, scope="product",
         window="n/a",
         detail=("No published spread or touch size for M6E or M6A found. Structural fact (E.28 F1/F10): the micro tick "
                 "(0.0001) is one pip, twice the full-size tick, so the micro spread is at least 1 pip = 1 micro tick. "
                 "Forum posts (pointers only, not saved, never a source): a NexusFi poster says M6E spreads are wider "
                 "than 6E; a 2010 NinjaTrader post reports 'a 5 tick spread late at night Central Time' on M6E."),
         quote="CME 292 ... Minimum price fluctuations shall be in multiples of $.0001 per Euro, equivalent to $1.25 per contract.",
         source={"file": A1, "field": "[code=M6E].median_spread_ticks; [code=M6A].median_spread_ticks; [code=M6E].tick_size"},
         verified="reused", negative=False),
    dict(codes=["M6E"], topic="T1", field="spread_pointer", value="5 ticks late at night (2010 forum post)", scope="product",
         window="2010 (forum)", detail="Pointer only (forum, search snippet; page not saved). Not a source for S.",
         quote="M6E is kind of illiquid at times (currently sitting at a 5 tick spread late at night Central Time",
         source={"url": "https://forum.ninjatrader.com/forum/ninjatrader-7/platform-technical-support/36744-bid-ask-charting"},
         verified="snippet", pointer=True),

    # ---------------- T2a automated / HFT share (non-CFTC sources) ----------------
    dict(codes=ALL, topic="T2a", field="auto_share_pct", value="about 70% of EBS orders algorithmic", scope="other_venue",
         window="as of 2018 (BIS Markets Committee report, September 2018)",
         detail=("Spot FX interdealer CLOB (EBS), share of ORDERS submitted by algorithms, not share of volume; "
                 "covers spot EUR/USD and other pairs, not CME futures. CFTC per-product futures shares are in the "
                 "shared file F2_shared_cftc_automation.json (RatesReader) and E.28 A1_fx.json ats_share."),
         quote=("an estimated 70% of orders on EBS, a primary central limit order book (CLOB) and a major inter-dealer platform "
                "for spot FX, are now submitted by algorithms, rather than manually"),
         source={"file": MY + "bis_mktc10_fast_paced_markets_2018.pdf"}, verified="full_text"),
    dict(codes=ALL, topic="T2a", field="auto_share_pct", value="HFT about 24-30% of spot turnover", scope="other_venue",
         window="2010-2011 estimate (BIS Markets Committee 2011)",
         detail="Spot FX market estimate (pre-2012); HFT also active on CME FX futures per the same report.",
         quote="about 24–30% of spot turnover",
         source={"file": E28 + "bis_mktc05_hft_fx_2011.txt", "field": "A1_fx.md F10"}, verified="reused"),

    # ---------------- T2b market-maker programs ----------------
    dict(codes=["M6E", "M6A"], topic="T2b", field="mm_program", value="FX Micros Market Maker Program", scope="product",
         window="2021-08-01 to 2025-08-31 (per the 2023 and 2024 CME filings to the CFTC)",
         detail=("Covers Micro AUD/USD (M6A) and Micro EUR/USD (M6E) futures among other micros; participants quote "
                 "continuous two-sided markets at maximum spreads and minimum sizes; no participant cap. No filing "
                 "extending it beyond 2025-08-31 was found (searched cftc.gov filings, 2 queries)."),
         quote="Start date is August 1, 2021. End date is August 31, 2024 August 31, 2025.",
         source={"file": E28 + "cftc_cme_rules0808244211_fx_mm_2024.txt", "field": "A1_fx.json [code=M6E].market_maker_program"},
         verified="reused"),
    dict(codes=["6E", "6A"], topic="T2b", field="mm_program", value="FX Futures Calendar Spreads Market Maker Program (spreads only)",
         scope="product", window="2021-01-01 to 2021-12-31 (as filed; later extensions not checked)",
         detail=("Covers CALENDAR SPREAD transactions in Australian dollar (AD = 6A), Euro FX (EC = 6E), BP, C1, J1 on "
                 "Globex, not the outright futures. Up to 14 participants per the search summary (not checked)."),
         quote=("Spread transactions in Australian Dollar Futures (“AD”), British Pound Futures (“BP”), Canadian Dollar [...] "
                "Start date is January 1, 2021. End date is December 31, 2021."),
         source={"file": MY + "cftc_rule121720_fx_calspread_mm.pdf"}, verified="full_text"),
    dict(codes=["6E"], topic="T2b", field="mm_program", value="EUR/USD FX Futures BTIC Market Maker Program (BTIC only)",
         scope="product", window="2023-02-06 to 2024-01-31 (as modified effective 2023-07-01)",
         detail="Covers Basis Trade at Index Close (BTIC and BTIC+) on EUR/USD futures, not outright 6E trading.",
         quote="Start date is February 6, 2023. End date is January 31, 2024.",
         source={"file": MY + "cftc_rules0612232810_eurusd_btic_mm.pdf"}, verified="full_text"),
    dict(codes=["6E", "6A"], topic="T2b", field="mm_program", value=None, scope="product",
         window="2021-2026 searched",
         detail=("No market-maker or incentive program for OUTRIGHT 6E or 6A futures found (E.28 searched CFTC filings; "
                 "this reader searched cftc.gov filings again with 2 queries and fetched 5 filings: FX calendar spreads, "
                 "EUR/USD BTIC, ICE's own FX program, an S&P BTIC and a crypto program). The 2019 FX Futures MM "
                 "Program's full-size scope lists crosses and EM pairs, not EUR/USD or AUD/USD. Not found, not 'none exists'."),
         quote=None, source={"file": A1, "field": "[code=6E].market_maker_program; [code=6A].market_maker_program"},
         verified="reused"),

    # ---------------- T2c retail ----------------
    dict(codes=ALL, topic="T2c", field="retail_share", value=None, scope="product",
         window="n/a",
         detail=("No numeric retail share found for any of the four (E.28 searched; not re-searched). CME describes the "
                 "E-micros as aimed at retail traders (2009 launch release). Manual (non-ATS) volume share of the "
                 "E-micro FX group 29.1% (2016-18, CFTC; shared file owns it)."),
         quote="designed to enable retail traders and investors to cost-effectively access the security, transparency and liquidity of CME Group's FX products",
         source={"file": E28 + "mv_cme_emicro_launch_2009.html.txt", "field": "A1_fx.json [code=M6E].retail_share"},
         verified="reused"),

    # ---------------- T3 structural relationships ----------------
    dict(codes=EUR, topic="T3", field="relationship", value="micro/full pair M6E-6E", scope="product",
         window="contract terms in force 2021-2025",
         detail=("Mechanical (arbitrage-tight) pair on the same underlying: M6E is EUR 12,500, 6E EUR 125,000; both "
                 "physically delivered on the third Wednesday (see T5). No intraday lead-lag study of M6E vs 6E found."),
         quote="The unit of trading shall be 12,500 Euro.",
         source={"file": E28 + "cme_rulebook_ch292.txt"}, verified="reused"),
    dict(codes=AUD, topic="T3", field="relationship", value="micro/full pair M6A-6A", scope="product",
         window="contract terms in force 2021-2025",
         detail="Mechanical pair on the same underlying: M6A AUD 10,000, 6A AUD 100,000; both physically delivered.",
         quote="The unit of trading shall be 10,000 Australian dollars.",
         source={"file": E28 + "cme_rulebook_ch291.txt"}, verified="reused"),
    dict(codes=["6E", "6A"], topic="T3", field="relationship", value="calendar spreads (implied spread book, Algorithm K)",
         scope="product", window="from 2019-08-12 (6E) and 2020-01-27 (6A)",
         detail="Calendar type; mechanical. FX calendar spreads matched by Algorithm K; outrights FIFO.",
         quote=("CME is amending the CME Globex trade matching algorithm for all calendar spread transactions of FX contracts "
                "from Matching Algorithm C to Matching Algorithm K"),
         source={"file": E28 + "cftc_cme_rule071819_fx_spread_algo.txt", "field": "A1_fx.md F2"}, verified="reused"),
    dict(codes=["6E", "M6E", "6A", "M6A"], topic="T3", field="relationship", value="futures vs OTC spot: CME FX Link and FX Spot+",
         scope="product", window="FX Link median spread June 2021; FX Spot+ deck 2026",
         detail=("Arbitrage-tight futures-spot basis: FX Link is one Globex spread between OTC spot and the future "
                 "(EUR/USD FX Link median spread 0.1 pip, TOB about USD 90m, June 2021); FX Spot+ (2026 CME deck hosted by "
                 "the Bank of Canada; exchange marketing, practitioner level) links spot to implied futures liquidity. "
                 "Applies to the underlyings; minute-level lead-lag between futures and spot is under T5."),
         quote=("With the median spread at 0.1 pips during the bulk of the trading day [...] "
                "This shows a typical TOB size for FX Link of around $90 million."),
         source={"file": E28 + "cme_fx_market_profile_usecase.html"}, verified="full_text"),
    dict(codes=["6E", "M6E", "6A", "M6A"], topic="T3", field="relationship", value="FX Spot+ implied futures liquidity (practitioner)",
         scope="product", window="2026 (CME deck)",
         detail="Exchange deck, not a study: over 70 FX Spot+ participants, nearly 40 banks that do not trade futures.",
         quote="FX Spot+ has seen over 70 participants - including",
         source={"file": MY + "boc_cme_evolution_fx_market_structure_2026.pdf"}, verified="full_text"),
    dict(codes=AUD, topic="T3", field="relationship", value="AUD/USD vs gold, copper, crude oil (economic, cross-asset)",
         scope="other_venue", window="2000-2009, daily and 5-minute data",
         detail=("Economic cross-asset pair, spot AUD/USD (not CME futures). Multi-horizon Granger causality at 5-minute "
                 "and daily frequency: causality both ways, stronger at short horizons, commodity -> exchange rate "
                 "dominant (ratios up to 5 or 10). In-sample causality measures, not a trading test. Zhang, Dufour, "
                 "Galbraith (2013), CIRANO 2013s-39 (working paper)."),
         quote=("(1) Granger causality between commodity prices and exchange rates is visible in both directions; (2) it is stronger at "
                "short horizons, and becomes weaker as the horizon increases"),
         source={"file": MY + "cirano_2013s39_commodity_fx.pdf"}, verified="full_text"),
    dict(codes=AUD, topic="T3", field="relationship", value="AUD futures vs commodity index futures: no Granger causality (daily)",
         scope="product", window="1992-07-28 to 2009-01-28, daily futures",
         detail=("Chan, Tse and Williams (NBER-EASE volume, 2011 chapter c11859): contemporaneous relation only, no "
                 "lead-lag at daily horizon for AUD, CAD, NZD, ZAR futures. Daily horizon; negative for lead-lag."),
         quote="relation- ships exist contemporaneously, but fail to exhibit Granger-causality in either direction.",
         source={"file": MY + "nber_c11859_chan_tse_williams.pdf"}, verified="full_text", negative=True, quote_unchecked=False),

    # ---------------- T4 scheduled events ----------------
    dict(codes=ALL, topic="T4", field="event", value="US macro releases (08:30 ET employment etc.): conditional-mean jumps, quick adjustment",
         scope="underlying", window="1992-01 to 1998-12, 5-minute Reuters indicative quotes (DM, euro, pound, yen, CHF vs USD)",
         detail=("Absorption: conditional mean adjusts quickly ('effectively amounting to jumps'); variance adjusts "
                 "gradually. Response coefficients plotted at 0, 5 and 10 minutes after. German releases with uncertain "
                 "times adjust more gradually, 'perhaps for a few hours' (conjecture). Andersen, Bollerslev, Diebold, "
                 "Vega (NBER w8959; AER 2003). AUD not covered."),
         quote=("We show that conditional mean adjustments of exchange rates to news occur quickly, effectively "
                "amounting to “jumps,” in contrast to conditional variance adjustments, which are much more gradual"),
         source={"file": MY + "abdv_2002_nber_w8959.pdf"}, verified="full_text"),
    dict(codes=EUR, topic="T4", field="event", value="US releases (08:30 ET) and FOMC: effect completed within a few minutes (EBS EUR/USD)",
         scope="underlying", window="January 1999 to January 2004, EBS one-minute data, euro-dollar and dollar-yen",
         detail=("Absorption within a few minutes; returns after the first few minutes orthogonal to the surprise; "
                 "the expected rate a few minutes after equals that an hour later. Volume stays elevated longer "
                 "(activity, not mean). Chaboud, Chernenko, Howorka, Iyer, Liu, Wright, FRB IFDP 823 (2004)."),
         quote=("the surprise component of the announcement produces a movement in the conditional mean "
                "that is generally completed within a few minutes, and that is effectively a jump."),
         source={"file": MY + "chaboud_chernenko_wright_ifdp823.pdf"}, verified="full_text"),
    dict(codes=AUD, topic="T4", field="event", value="RBA policy announcements: rapid impact within 10 minutes, little after",
         scope="underlying", window="Australia 1993-07-30 to 2004-06-02 (79 events); spot AUD/USD intraday",
         detail=("Kearns and Manners (RBA RDP 2005-02; IJCB 2006): sharp spike in the 10 minutes after the event, "
                 "coefficients stable over the following six hours (no drift). RBA met 11 times a year then; 8 a year in "
                 "2025-26 (E.28 F11). Fetched via Wayback (rba.gov.au answered 403 to curl)."),
         quote=("In all 4 countries there is a sharp spike in the impact in the 10 minutes following the event, demonstrating that monetary "
                "policy announcements have a rapid impact on the exchange rate. The relative stability of the coefficients over the six hours after the event indicate that the "
                "surprise has little additional influence after its immediate impact."),
         source={"file": MY + "kearns_manners_rba_rdp2005_02_wayback.pdf"}, verified="full_text"),
    dict(codes=EUR, topic="T4", field="event", value="ECB inter-meeting communication: no reliable intraday drift (null)",
         scope="underlying", window="2008-06 to 2016-05 (1,868 coded statements), EUR/USD 1-minute",
         detail=("Volatility and small short-lived responses; CARs within a few bp by +20 minutes; no drift. Fanta "
                 "(2025) IES WP 23/2025. Meeting-day ECB timing per its literature review: 13:45 press release and "
                 "14:30 press conference CET (Altavilla et al. 2019 era; current times not verified here)."),
         quote=("Cumulative abnormal returns remain within a few basis points by t=+20 [...] "
                "(13:45 press release and 14:30 press conference)"),
         source={"file": E20 + "fanta_2025_ies_wp23.pdf", "field": "product_6E.json evidence[id=E8]"},
         verified="reused", negative=True),
    dict(codes=ALL, topic="T4", field="event", value="FOMC (about 14:15 ET in sample): currency drift before and partial reversal 12-24 h after",
         scope="asset_class", window="1999-01 to 2015-12, 17 currencies, 136 scheduled meetings, 15-minute data",
         detail=("Drift at 12-hour windows (dollar factor -12:0h 23.4% p.a., 0:12h 13.8%, 12:24h -47.5%); a horizon of "
                 "hours, not minutes after the release; in sample; gross. Wang (2018) Georgia Tech dissertation ch.1."),
         quote="Dollar factor 0.085 23.115 23.407 13.751 -47.521 [...] Scheduled FOMC announcements occur at about 14:15 Eastern Standard Time.",
         source={"file": E20 + "wang_2018_gatech_dissertation.pdf", "field": "product_6E.json evidence[id=E7]"},
         verified="reused"),
    dict(codes=ALL, topic="T4", field="event", value="ECB (8/yr) and RBA (8/yr in 2025-26) meeting calendars",
         scope="underlying", window="ECB 2027 calendar; RBA 2026 calendar",
         detail="Frequency facts reused from E.28 F11 (about 0.15 per week each). Release times not re-verified.",
         quote="Governing Council of the ECB: monetary policy meeting in Frankfurt (Day 2), followed by press conference",
         source={"file": E28 + "ecb_meeting_calendar.html.txt", "field": "A1_fx.json [code=6E].product_specific_releases_per_week"},
         verified="reused"),

    # ---------------- T5 settlement basis and price discovery ----------------
    dict(codes=["6E"], topic="T5", field="settlement_basis", value="physical delivery", scope="product",
         window="CME rulebook ch. 261 (Wayback 2023)", detail="Delivered on the third Wednesday of the contract month.",
         quote="26102.A. Physical Delivery", source={"file": E28 + "cme_rulebook_ch261_6E.txt"}, verified="reused"),
    dict(codes=["M6E"], topic="T5", field="settlement_basis", value="physical delivery", scope="product",
         window="CME rulebook ch. 292 (Wayback 2025-05-15)",
         detail="Physically delivered like 6E; NOT financially settled off 6E's settlement price.",
         quote="29202.A. Physical Delivery", source={"file": E28 + "cme_rulebook_ch292.txt"}, verified="reused"),
    dict(codes=["6A"], topic="T5", field="settlement_basis", value="physical delivery", scope="product",
         window="CME rulebook ch. 255 (Wayback 2023)", detail="Delivered on the third Wednesday of the contract month.",
         quote="25502.A. Physical Delivery", source={"file": E28 + "cme_rulebook_ch255_6A.txt"}, verified="reused"),
    dict(codes=["M6A"], topic="T5", field="settlement_basis", value="physical delivery", scope="product",
         window="CME rulebook ch. 291 (Wayback 2025)",
         detail="Physically delivered like 6A; NOT financially settled off 6A's settlement price.",
         quote="29102.A. Physical Delivery", source={"file": E28 + "cme_rulebook_ch291.txt"}, verified="reused"),
    dict(codes=EUR, topic="T5", field="info_share", value="spot dominant in 2006 (futures informative in 1996)", scope="product",
         window="1996 and 2006 samples", detail="Rosenberg and Traub, FRBNY SR 262 (J. Derivatives 2009). Full text (E.28).",
         quote="in our more recent sample that the spot market has the dominant information share",
         source={"file": E28 + "rosenberg_traub_frbny_sr262.txt", "field": "A1_fx.md F10"}, verified="reused"),
    dict(codes=EUR, topic="T5", field="info_share", value="spot (EBS) leads CME regular and E-mini euro futures", scope="product",
         window="sample per paper (2000s; not stated in abstract)",
         detail="Cabrera, Wang and Yang (2009), JFM 29:137-156. Abstract only (E.28).",
         quote="the spot market is found to consistently lead the price discovery process for both currencies during the sample period",
         source={"file": E28 + "openalex_10.1002_fut.20352_abstract.txt", "field": "A1_fx.md F10"}, verified="abstract"),
    dict(codes=EUR, topic="T5", field="info_share", value="spot (EBS) more price discovery than CME futures overall; futures share rises around US releases",
         scope="product", window="sample not stated in abstract",
         detail="Chen and Gau (2010), J. Banking & Finance 34(7):1628-1636; information shares and common factor weights; EUR-USD and JPY-USD. Abstract only (IDEAS).",
         quote=("The results show that the spot rates provide more price discovery than do the CME futures rates overall; however, the contribution "
                "of the futures rates to price discovery increases in the time surrounding macroeconomic announcement releases."),
         source={"file": MY + "ideas_chen_gau_2010_jbf.html"}, verified="abstract"),
    dict(codes=EUR, topic="T5", field="info_share", value="futures dominate price discovery once order flows of both markets are included",
         scope="product", window="sample not stated in abstract",
         detail="Chen and Gau (2022), J. Futures Markets 42(8):1549-1572; EUR-USD and JPY-USD electronic futures and spot, intraday. Abstract only (IDEAS). Conflicts with the 2010 result.",
         quote="the futures market dominates price discovery when compared with the spot market, confirming that order flows have a permanent impact on prices, even more so in futures markets",
         source={"file": MY + "ideas_jfm2022_orderflow_futures_spot.html"}, verified="abstract"),
    dict(codes=EUR, topic="T5", field="info_share", value="6E about 66.5% vs E-mini euro (futures-to-futures)", scope="product",
         window="2010", detail="Malhotra and Corelli (2021), Risks 9(6):111; regular vs E-mini futures, not vs spot. Abstract only (E.28).",
         quote="accounting for approximately 66.5% of price discovery in the EURO/USD market",
         source={"file": E28 + "openalex_10.3390_risks9060111_abstract.txt", "field": "A1_fx.md F9"}, verified="abstract"),
    dict(codes=ALL, topic="T5", field="info_share", value="BIS: spot became dominant over FX futures in the 2000s (euro, yen, sterling)",
         scope="asset_class", window="2000s (literature summary in a 2018 BIS report)",
         detail="Summary statement citing Rosenberg-Traub, Wang-Yang, Chen-Gau; no AUD study found.",
         quote="venues has been associated with the spot market becoming the dominant source of price discovery over FX futures markets in the",
         source={"file": MY + "bis_mktc10_fast_paced_markets_2018.pdf"}, verified="full_text"),

    # ---------------- T6 directional evidence ----------------
    dict(codes=ALL, topic="T6", field="directional_study", value="EUR/USD: currency falls in its local trading hours; strategy profitable after costs; AUD/USD not after costs",
         scope="other_venue", window="1997-01 to 2007-06, EBS spot (firm quotes), hourly",
         detail=("Breedon and Ranaldo (QMUL WP 694, 2012; JMCB 45(5) 2013, 953-965); peer-reviewed. Horizon: session "
                 "(European session 02:00-08:00 NY time short EUR, US session long), several hours. In sample. Net of "
                 "costs (EBS bid/ask): EUR/USD 0.06 (EUR session) and 0.07 (USD session) annualised log returns, Sharpe "
                 "1.3 and 0.9; AUD/USD -0.51 and -0.50 (negative after costs). Year-by-year EUR/USD session gap stable "
                 "except 2004. Spot, pre-2010."),
         quote=("the notable exception is EUR/USD where the significant intraday pattern combined with narrow spreads in this cross means that this basic strategy has been profitable on "
                "average with Sharpe Ratios of 1.3 and 0.9 respectively for the morning short and afternoon long. [...] "
                "AUD/USD AUD session ‐0.028** ‐0.038* 0.50 ‐0.51"),
         source={"file": MY + "breedon_ranaldo_2012_qmul_wp694.pdf"}, verified="full_text"),
    dict(codes=ALL, topic="T6", field="directional_study", value="Fix-driven intraday V-shapes; CME futures dollar portfolio post-London-fix +0.64 bp/day (t 2.20); liquidity demanders lose after costs",
         scope="underlying", window="1999-01 to 2019-12 spot mid-quotes; CME futures 2006-06 to 2019-12",
         detail=("Krohn, Mueller, Whelan (2024), J. Finance 79(1); author manuscript, full text (E.20). Horizons: windows "
                 "of hours around the Tokyo (9:55 JST), ECB (14:15 CET, 14:00 after July 2016) and London 16:00 fixes. "
                 "EUR post-London (11:00-17:00 ET) +2.73 bp/day (t 6.78); AUD pre-Tokyo -2.84 (t -8.24), post-Tokyo +1.85, "
                 "post-London +1.93 (t 3.75). In sample; gross; decays in later subsamples (dollar portfolio post-L "
                 "0.86 bp in 2014-19, E.20). Authors: client-market liquidity demanders' returns are negative after costs."),
         quote=("AUD -2.84 1.85 -0.41 -0.05 1.93 0.47 [...] CME Futures -1.46 1.80 -1.64 0.11 0.64 -0.56 [...] "
                "the unconditional return patterns cannot easily be arbitraged in the client market as transaction cost adjusted returns are significantly"),
         source={"file": E20 + "krohn_mueller_whelan_2024_jf_wrap.pdf", "field": "product_6E.json evidence[id=E2,E3,E4]"},
         verified="reused"),
    dict(codes=ALL, topic="T6", field="directional_study", value="Month-end WMR fix contrarian, 5-15 min holds, net of half spread; post-2010 out-of-sample average 3.25% p.a.",
         scope="underlying", window="2004-2013, 21 pairs, Gain Capital 1-s and EBS",
         detail=("Evans (2018), J. Banking & Finance 87 (MPRA 81583 version, full text, E.20). One trade a month; h = 1, 5, "
                 "15 min. Table 6 (annual %, h=15/5/1): EUR/USD 3.965/0.486/0.068 (Sharpe 1.881 at 15); AUD/USD "
                 "9.187/12.292/8.353 (Sharpe 3.375 at 15). Net: costs zero at the fix and half the spread at exit. "
                 "Out of sample: post-2010 returns of the pre-2010 best pairs averaged 3.25%. Sample ends before the "
                 "Feb 2015 fix-window widening to 5 minutes. Column order in Table 6 is h = 15, 5, 1 (checked)."),
         quote=("A: EUR/USD 3.965 0.486 0.068 1.881 0.222 0.042 [...] D: AUD/USD 9.187 12.292 8.353 3.375 4.353 3.124 [...] "
                "Returns are inclusive of trading costs [...] average return across the currencies of 3.25 percent."),
         source={"file": E20 + "evans_2018_jbf_wmrfix_mpra81583.pdf", "field": "product_6E.json evidence[id=E5]"},
         verified="reused"),
    dict(codes=ALL, topic="T6", field="directional_study", value="Month-end equity-hedging flow predicts currency move 15:00-16:00 London",
         scope="underlying", window="2004-04-28 to 2012-12-31, 10 currencies, EBS/Reuters 5-min",
         detail=("Melvin and Prins (2015 JFM 22; 2013 ECB-workshop draft, full text E.20). 60-minute horizon, last day "
                 "of month only; in sample; gross; 10% equity rise -> 14 bp currency fall. No post-2012 check found."),
         quote="predicts a statistically significant depreciation in the currency in the hour leading up to the end of month fix",
         source={"file": E20 + "melvin_prins_2013_ecb_wp.pdf", "field": "product_6E.json evidence[id=E6]"},
         verified="reused"),
    dict(codes=ALL, topic="T6", field="directional_study", value="Market intraday momentum in currency futures: insignificant 2000-2020; Euro FX null",
         scope="product", window="Euro FX 1999-01-06 to 2020-05-01; 8 currency futures 1974-2020; 1-minute",
         detail=("Baltussen et al. (2021 JFE). Shared source owned by EquityReader (F2_shared_baltussen.json); cited "
                 "here only via E.20's sourced reading: Euro FX beta_ROD -0.04 (t -0.17), out-of-sample R2 -0.07%; "
                 "currency class 2000-2020 beta 0.33 (t 1.45). Horizon: last 30 minutes. A null on 6E; no 6A row "
                 "read here."),
         quote="| EC | 0.04 (0.12) | -0.02 | -0.08 | 0.01 (0.04) | -0.47 (-1.25) | 4.07 (1.44) | 0.22 | -0.30 | -0.04 (-0.17) | -0.02 | -0.07 |",
         source={"file": P6E, "field": "evidence[id=E1]"}, verified="reused", negative=True),
    dict(codes=ALL, topic="T6", field="directional_study", value="Intraday momentum/reversal in currency futures mostly not feasible after costs",
         scope="asset_class", window="2008-01 to 2024-10, 20 equity, bond and currency futures",
         detail="Aalto University master's thesis (2025), abstract only (E.20 shared notes); horizon last 30 minutes; net of costs; negative.",
         quote="most intraday momentum and reversal trading strategies may not be feasible after transactions costs, especially in bond and currency futures.",
         source={"file": R + "stage_e20_briefs/shared/aalto_thesis_notes.md"}, verified="abstract", negative=True),
    dict(codes=ALL, topic="T6", field="directional_study", value="Intraday momentum (first half hour -> last half hour) in RUB-USD",
         scope="asset_class", window="2005-2014, Moscow exchange transaction data",
         detail="Elaut, Frömmel, Lampaert (2018), J. Financial Markets 37:35-51. FX asset class, other venue (MICEX RUB-USD, explicit hours). In sample; gross. Abstract only (IDEAS); full text paywalled.",
         quote="intraday momentum in the ruble market is induced by risk aversion to overnight holdings among liquidity providers",
         source={"file": MY + "ideas_elaut_2018_jfm.html"}, verified="abstract"),
    dict(codes=ALL, topic="T6", field="directional_study", value="Intraday reversals after large moves in 5 of 7 CME currency futures",
         scope="product", window="1988-2003",
         detail="Rentzler, Tandon, Yu (2006), JFM 26(11). Pre-2010; abstract only (E.28); GLOBEX made markets 'fairly efficient', patterns renewed after 1999.",
         quote="Significant intraday price‐reversal patterns are observed in five of the seven currency futures contracts",
         source={"file": E28 + "ideas_rentzler_2006_jfm.html.txt", "field": "A1_fx.md F12"}, verified="reused"),
    dict(codes=EUR, topic="T6", field="directional_study", value="European currencies gain in US hours, lose in foreign hours (risk-based)",
         scope="asset_class", window="not verified",
         detail="Jiang (2018), Kellogg working paper 'Currency Returns in Different Time Zones'. Search snippet only; landing page is JS-rendered (saved, no text). [unverified: snippet].",
         quote="European currencies have positive average returns during US business hours and negative average returns during foreign business hours",
         source={"url": "https://www.kellogg.northwestern.edu/academics-research/research/detail/2018/currency-returns-in-different-time-zones"},
         verified="snippet"),
    dict(codes=EUR, topic="T6", field="directional_study", value="excluded: weekly horizon",
         scope="product", window="1999-12 to 2005-03",
         detail="Chen et al., EFMA 2009: weekly 6E returns reverse after extreme trade imbalance (net of costs). Excluded: horizon weekly, not 5 minutes to session.",
         quote="weekly returns in Euro FX futures exhibit significant reversals",
         source={"file": E28 + "efma2009_0102_euro_fx_trade_imbalance.txt", "field": "A1_fx.md F12"}, verified="reused"),

    # ---------------- T7 session structure ----------------
    dict(codes=ALL, topic="T7", field="session_hours", value="Globex Sun-Fri 17:00-16:00 CT, 60-minute daily break from 16:00 CT",
         scope="product", window="spec pages, Wayback 2020-12 to 2021-04",
         detail="Reused from E.28 trading_hours (all four codes identical). Former pit/RTH window 07:20-14:00 CT used by Baltussen et al. as the FX day (E.20 E1).",
         quote="Sunday - Friday 5:00 p.m. - 4:00 p.m. CT with a 60-minute break each day beginning at 4:00 p.m. CT",
         source={"file": E28 + "cme_old_specs_e-micro-euro.html.txt", "field": "A1_fx.json [code=*].trading_hours"}, verified="reused"),
    dict(codes=ALL, topic="T7", field="settlement_window", value="FX daily settlement 13:59:30-14:00:00 CT",
         scope="product_group", window="CME client wiki page (fetched 2026-10-29 UTC)",
         detail="Daily settlement time range for the FX group. No study of a settlement-window return effect on CME FX futures found.",
         quote="13:59:30-14:00:00 CT",
         source={"file": MY + "cme_wiki_daily_settlement_times.html"}, verified="full_text"),
    dict(codes=ALL, topic="T7", field="session_handoff", value="Regional sessions: a currency depreciates during its own local trading hours",
         scope="other_venue", window="1997-2007, EBS spot",
         detail=("Breedon and Ranaldo: session hours US 08:00-16:00 NY, Europe 07:00-15:00 local, Japan 08:00-15:00, "
                 "Australia 10:00-16:00; home-session return below foreign-session return at 1% for all pairs except "
                 "USD/JPY. Horizon: session (hours). Spot, pre-2010, in sample."),
         quote="in all cases the return in the home session is significantly lower than the return in the foreign session at the 1% level",
         source={"file": MY + "breedon_ranaldo_2012_qmul_wp694.pdf"}, verified="full_text"),
    dict(codes=ALL, topic="T7", field="session_handoff", value="Fix handoffs: Tokyo 9:55 JST, ECB 14:15 CET (14:00 CET from July 2016), London WMR 16:00",
         scope="underlying", window="1999-2019",
         detail=("USD appreciates into each fix and reverses after (Krohn et al. 2024; hours-long windows). WMR fix "
                 "window widened from 1 to 5 minutes on 2015-02-15 (BIS, Debelle 2015); ECB publication moved to 16:00 CET "
                 "in July 2016. Applies to EUR and AUD; CME futures show the same pattern (T6)."),
         quote=("the long position in the U.S. dollar is held from 17:00 ET to the Tokyo fix at 9:55 local time [...] "
                "the ECB has moved the publication of the reference rates to 16:00 CET in July 2016"),
         source={"file": E20 + "krohn_mueller_whelan_2024_jf_wrap.pdf", "field": "product_6E.json evidence[id=E2,E4]"},
         verified="reused"),
    dict(codes=ALL, topic="T7", field="session_handoff", value="WMR fix window widened to 5 minutes from 2015-02-15",
         scope="underlying", window="from 2015-02-15", detail="Changes the London 16:00 fix mechanics after Evans (2018) and Melvin-Prins samples.",
         quote="widen the fix window to five minutes commencing on 15 February",
         source={"file": E20 + "bis_debelle_2015_fx_benchmarks.html"}, verified="reused"),

    # ---------------- F1 changes ----------------
    dict(codes=["6A"], topic="F1", field="changed_fact", value="median_spread_ticks: 1.0 (median, whole day, Dec 2020); was null in E.28",
         scope="product", window="December 2020",
         detail="Old value null at A1_fx.json [code=6A].median_spread_ticks. New value from item on 6A spread (CME FX report 2021 Q1).",
         quote="This shows that the median spread is now consistently 0.5 pips",
         source={"file": MY + "cme_fx_report_2021q1_in_our_markets_wayback.html"}, verified="full_text"),
    dict(codes=["6E"], topic="F1", field="changed_fact", value="touch_queue_size: about USD 3.5m TOB (June 2021); was null in E.28",
         scope="product", window="June 2021",
         detail="Old value null at A1_fx.json [code=6E].touch_queue_size (E.28 wrote 'The article gives no contract count at the touch'). The article states USD size, not contracts.",
         quote="TOB size for futures of around $3.5 million",
         source={"file": E28 + "cme_fx_market_profile_usecase.html"}, verified="full_text"),
]

PER_CODE = {
    "M6E": {"median_spread_ticks": None, "spread_item": "FX-5", "touch_size": None, "touch_item": "FX-5",
            "settlement_basis": "physical delivery (not financially settled off 6E)", "settlement_item": "FX-28",
            "leader": "6E",
            "notes": ("Own spread unknown (tick = 1 pip; leader 6E averaged 0.6 pip = 1.2 6E ticks in June 2021). FX Micros "
                      "MM program 2021-08 to 2025-08 (FX-9). Leader-level ATS share: shared CFTC file. Best directional "
                      "evidence: other venue (spot EUR/USD, Breedon-Ranaldo net of costs, pre-2010) and fix studies; "
                      "same-product nulls (Baltussen Euro FX; Aalto thesis abstract).")},
    "6E": {"median_spread_ticks": None, "whole_day_average_spread_ticks_jun2021": 1.2, "spread_item": "FX-1", "touch_size": "about USD 3.5m (about 23 contracts, arithmetic)",
           "touch_item": "FX-2", "settlement_basis": "physical delivery", "settlement_item": "FX-27", "leader": "6E",
           "notes": ("Spread found only as a whole-day time-weighted AVERAGE 0.6 pip = 1.2 ticks (June 2021), not a "
                     "main-session median, so median_spread_ticks is left null; the lead decides. No outright MM program "
                     "found (calendar spreads 2021 and BTIC 2023 programs only). Price discovery: spot led in 2000s "
                     "studies; Chen-Gau 2022 abstract says futures dominate with order flow.")},
    "M6A": {"median_spread_ticks": None, "spread_item": "FX-5", "touch_size": None, "touch_item": "FX-5",
            "settlement_basis": "physical delivery (not financially settled off 6A)", "settlement_item": "FX-30",
            "leader": "6A",
            "notes": "Own spread unknown. FX Micros MM program (FX-9). No AUD price-discovery study found."},
    "6A": {"median_spread_ticks": None, "whole_day_median_spread_ticks_dec2020": 1.0, "spread_item": "FX-3", "touch_size": "about USD 1.5m (15 to 20 contracts, arithmetic)",
           "touch_item": "FX-4", "settlement_basis": "physical delivery", "settlement_item": "FX-29", "leader": "6A",
           "notes": ("median_spread_ticks left null: the 1-tick figure is a whole-trading-day median for December 2020, not a main-session median; average "
                     "that month 1.5 ticks. Touch size is a 3-day average just after the tick change. No outright MM "
                     "program found. AUD/USD time-of-day strategy negative after costs on EBS (Breedon-Ranaldo).")},
}

NOT_FOUND = [
    {"codes": ALL, "topic": "T1", "queries": [
        "CME Group FX futures \"Australian dollar\" bid-ask spread \"top of book\" depth liquidity report AUD/USD futures",
        "CME \"FX Market Profile\" EUR/USD futures median spread pips top of book size 2022 OR 2023 OR 2024 article",
        "\"Micro EUR/USD\" OR \"E-micro EUR/USD\" futures M6E bid-ask spread typical ticks liquidity"],
     "note": "No main-session median spread for any code; no micro (M6E, M6A) spread or touch size; no post-2021 CME figures."},
    {"codes": ALL, "topic": "T2b", "queries": [
        "cftc.gov CME \"FX Micros Market Maker Program\" 2025 extension submission",
        "cftc.gov/filings/orgrules CME \"FX\" \"Market Maker Program\" \"Micro EUR/USD\" OR \"Euro FX Futures\" 2025 OR 2026"],
     "note": "No FX Micros MM extension after 2025-08-31 found; no outright 6E or 6A program found."},
    {"codes": ALL, "topic": "T4", "queries": [
        "exchange rate intraday response macroeconomic announcements post-announcement drift EUR/USD high-frequency 2010s study \"drift\" minutes after release"],
     "note": "No post-2010 study showing a mean drift of 5 minutes or more after a scheduled release for EUR/USD or AUD/USD; Almeida-Goodhart-Payne (1998) and Evans-Speight (2010) seen as snippets only, not fetched."},
    {"codes": ALL, "topic": "T6", "queries": [
        "Elaut Frömmel Lampaert \"Intraday momentum in FX markets\" pdf",
        "\"Intraday momentum in FX markets\" Elaut biblio.ugent.be OR working paper Ghent University RUB",
        "intraday momentum currency futures first half-hour last half-hour euro yen CME study",
        "\"intraday\" return predictability \"currency futures\" OR \"FX futures\" momentum reversal 2019..2025 journal \"out-of-sample\"",
        "\"currency futures\" intraday \"time-of-day\" OR \"intraday seasonality\" returns predictability CME euro australian dollar journal 2015 2020",
        "Jiang \"Currency Returns in Different Time Zones\" pdf"],
     "note": ("No post-2010 peer-reviewed study of intraday directional predictability (5 min to session) on 6E, 6A, "
              "M6E or M6A themselves, out of sample or net of costs, beyond Krohn et al.'s CME-futures dollar portfolio "
              "(in sample, gross) and the Baltussen Euro FX null. Irrelevant hits checked: CFR WP 26-02 (option returns), "
              "PBFJ 2023 (APAC equity ETFs).")},
    {"codes": AUD, "topic": "T5", "queries": [
        "price discovery CME currency futures versus spot EBS information share 2015..2024 EUR/USD AUD/USD study"],
     "note": "No AUD/USD futures-vs-spot information-share study found; no post-2015 EUR/USD information-share figure with a number."},
    {"codes": ALL, "topic": "T7", "queries": [
        "CME FX futures daily settlement procedure 14:00 CT \"settlement period\" Euro FX VWAP 13:59"],
     "note": "Settlement window found; no study of a return effect around the CME FX settlement window."},
]

GAPS = [
    "No main-session median spread for any code (6E: whole-day average only; 6A: whole-day median, Dec 2020); none for the micros.",
    "Touch sizes are in USD as CME gives them; contract counts are my arithmetic with assumed exchange rates.",
    "Chen-Gau 2010 and 2022, Cabrera et al., Malhotra-Corelli, Elaut et al. are abstract-level; sample periods of the Chen-Gau papers not read.",
    "ECB current decision and press-conference times not re-verified (13:45/14:30 CET in the cited literature; changed later).",
    "Kearns-Manners PDF fetched via Wayback because rba.gov.au answered 403 to curl; RBA site not tried with Scrapling.",
    "Jiang (2018) Kellogg WP: snippet only (JS-rendered landing page).",
]
