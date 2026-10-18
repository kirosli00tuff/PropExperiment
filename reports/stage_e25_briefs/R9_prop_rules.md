# R9: futures prop-firm rules landscape since E.21 (SourceReader-PropRules-OpusHigh)

Reader R9, Stage E.25 (research only). Written 2026-10-18, 01:38 to about 02:05 PDT. All fetches 2026-10-18 UTC
(fetch log, section 9). Updates E.13 (reports/stage_e13_venues.md, fetched 2026-10-03), E.19 (Topstep, fetched
2026-10-10) and E.21 section 3.2 (PropEd, 2026-10-14). Grades follow brief section 6. Firm pages are graded
`firm-page`. Third-party summaries are `pointer`. A claim read only through a search-engine summary is marked
`[secondary-only]`.

## 1. Answer (at most 250 words)

No futures prop firm found gives a plain, public grant of **fully automated trading together with overnight holds**.
The firms that now allow automation all require flat positions every day: Topstep (API), FundedNext Futures, DayTraders.com
(new to this program), MyFundedFutures, Lucid, Tradeify (own algorithm only) and Bulenox (personal tools only).
The firms that allow overnight holds either ban automation or allow only semi-automated or written-authorized use:
- Phidias Premium: semi-automated only. Unchanged since 2026-09-22.
- The5ers Futures **Swing**: new to this program. Up to 1 mini or 10 micros overnight, no weekend holds. "Algorithmic
  Trading ... strictly forbidden" (FAQ updated 2026-10-12).
- Elite Trader Funding Diamond Hands and Direct To Funded: automation needs ETF's written authorization (terms updated 2026-10-11).
- Alpha Prime Live: invitation only, automation banned.
- PropEd: automation not granted publicly.
- PropShopTrader Gladiator Swing: new to this program. Overnight and weekend holds per its pricing page; its algorithm
  rule was NOT read (terms forbid scraping) [secondary-only].
- The Trading Pit Classic: overnight holds and own EAs per its help pages, but no current sales listing was found.

**Biggest change since E.19 and E.21: Topstep.** Between 2026-10-10 and 2026-10-16 its CPI-only block became a "Tier 1 News
Events" window, 5 minutes either side of CPI, NFP, the FOMC decision and the FOMC press conference.
- Inside the window: no new mini positions, micro openings capped at 3 (50K) or 9 (150K) on equity index and metals, and
  pending orders do not fill.
- Energies, rates and FX are unaffected.
- The help article that said "Topstep doesn't require you to flatten" was rewritten (dateModified 2026-10-15).

**BC:** no firm read names British Columbia. Canada is open at Topstep, MFFU, DayTraders, Alpha and Phidias (E.13).
TradeDay and FundedNext limit Canadians outside Ontario to sim and a case-by-case live review.

## 2. Candidate hypotheses

**Zero.** R9's objective is venue rules, not effects; no source read publishes a trading effect. Venue facts that bear on
other readers' candidates are in sections 6 and 8 (notably the Topstep Tier 1 window for any R5/R6 news candidate).

Venue shortlist for the lead (facts only; ranking is the lead's):

| Venue / plan | Overnight | Weekend | Automation (as published) | BC / Canada | Status |
|---|---|---|---|---|---|
| Phidias Premium 50K/100K/150K | allowed | allowed ("over-week") | semi-automated only, trader "actively monitors and manually adjusts all trades" | not restricted (E.13) | unchanged since 2026-09-22 |
| The5ers Futures Swing | 1 mini / 10 micros | not allowed | "Algorithmic Trading ... strictly forbidden" | not read | NEW to program |
| ETF Diamond Hands / DTF | allowed | allowed | only with ETF written authorization (terms 2026-10-11) | E.13: not restricted | terms re-dated after E.13 |
| PropShopTrader Gladiator Swing | allowed [secondary-only] | allowed [secondary-only] | Tickblaze automation promoted; rule unread [unverified] | unread | NEW; terms forbid scraping |
| Alpha Prime LIVE (by selection) | "indeed permitted" | not stated | AI, bots, automated banned on all account types | not restricted | unchanged (page 2026-06-20) |
| PropEd (E.21) | allowed | add-on | not granted publicly | not restricted | not refetched |
| The Trading Pit Classic | Mon-Thu [secondary-only] | no | own EAs [secondary-only] | E.13: not restricted | no current sales listing found |
| Leeloo Investor PA | up to 3 micros through the close (E.13) | unread | banned; manual execution of alerts allowed | E.13: not stated | phasing out (E.13) |

## 3. Evidence table

Saved paths are relative to reports/stage_e25_briefs/pages/R9/. sha256 values (first 12) are in section 9.

| # | Claim | Number | Verbatim quote | Location | Source | Grade | Saved |
|---|---|---|---|---|---|---|---|
| E01 | Topstep Tier 1 window replaces CPI-only block | 10-min window; 50K: 3 micros, minis blocked | "Ahead of Tier 1 News Events (for example, CPI, FOMC, NFP), Topstep temporarily restricts new opening positions on equity index products and metals in SIM ... Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after). Micros (MES, M2K, MYM, MNQ, MGC): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes" | Risk Adjustments article, "Tier 1 News Events Restrictions"; dateModified 2026-10-16T17:11:31Z (E.19 copy: 2026-10-08, CPI only) | Topstep help 13613539 | firm-page | ts_13613539 |
| E02 | Tier 1 windows (CT) | 7:25-7:35; 12:55-13:05; 13:25-13:35 | "CPI 7:30 AM 7:25 to 7:35 AM FOMC rate decision 1:00 PM 12:55 to 1:05 PM FOMC press conference 1:30 PM 1:25 to 1:35 PM Non Farm Payroll (NFP/Unemployment Rate) 7:30 AM 7:25 to 7:35 AM" | same | same | firm-page | ts_13613539 |
| E03 | Pending orders do not fill in window; other products unaffected | n/a | "Other products (energies, rates, FX, etc.) are unaffected." ... "Pending orders are not open positions. They will not fill during the 10-minute window, and new pending orders intended to execute during this timeframe cannot be placed. TP/SL brackets that are reducing/closing positions will be accepted during the window." | same | same | firm-page | ts_13613539 |
| E04 | Topstep economic-release article rewritten | n/a | new: "Trading During the News Topstep restricts trading for a short period during Tier 1 News Events." (removed E.19 sentence: "Topstep doesn't require you to flatten positions during economic releases — in SIM or Funded Accounts.") | Economic Releases; dateModified 2026-10-15T17:51:06Z; removed sentence verified in E.19 copy reports/stage_e19_briefs/pages/art_8284211.html | Topstep help 8284211 | firm-page | ts_8284211 |
| E05 | Topstep flat by 3:10 CT, no swing | 15:10 CT | "Topstep is a day trading program. All positions must be closed by 3:10 PM CT every weekday. You can resume trading at 5:00 PM CT. No swing trading." | dateModified 2026-07-13 | help 8284206 | firm-page | ts_8284206 |
| E06 | Topstep API automation; no VPS | n/a | "TopstepX™ API Access lets advanced Traders and developers build automated strategies" ... "The use of VPS, VPNs, and remote servers is prohibited by Topstep's Terms of Use. Running automation on a VPS can result in account suspension" | dateModified 2026-09-17 (unchanged vs E.19) | help 11187768 | firm-page | ts_11187768 |
| E07 | Topstep P06 unchanged | n/a | "Trading Maximum Position Size into Major News Events Purposefully trading your full Maximum Position Size directly into a scheduled major news event." | dateModified 2026-06-10 (unchanged) | help 10305426 | firm-page | ts_10305426 |
| E08 | Topstep Canada eligible | n/a | "I'm Canadian — can I earn a Funded Account? Yes. You trade on a sub-account of Topstep's master account, considered a US-based account." | Eligibility FAQ, dateModified 2026-09-04 | help 8284116 | firm-page | ts_8284116 |
| E09 | Topstep XFA payout paths (consistency text expanded) | caps 50K $2,000/$3,000; 150K $5,000/$6,000 | "Standard Path Consistency Path 5 winning days of $150+ 3 days wit..." ; "Stay at or below the 40% consistency target. Your largest single day cannot exceed 40% of your total net profit." ; "For example, if your best trading day’s profit is $2,000, your total net profit must be at least $5,000 ($2,000 ÷ 0.4)." | Payout Policy, dateModified 2026-10-13 (E.19: 2026-09-30); added sentences only | help 8284233 | firm-page | ts_8284233 |
| E10 | FundedNext terms permit bots | n/a | "2.2.6. Using automated trading bots, artificial intelligence, or ultra-high-speed execution strategies is allowed. Fair trading conditions must be maintained for all participants. Automated systems that violate trading policies will be identified and disabled. In any event FundedNext can ask the customer to share the system used to execute trades for review" | Futures Challenge Terms s.2.2.6; "Last updated: 25 September 2026" | fundednext.com/futures-challenge-terms | firm-page | terms_fundednext |
| E11 | FundedNext no overnight | 15:10 CT | "2.2.16. Holding trades overnight beyond market close is not allowed." ; HC: "Traders must close all positions by 3:10 PM Central Time (CT) each trading day." | terms s.2.2.16; HC 14268506 (June 10, 2026) | FundedNext | firm-page | terms_fundednext, fn_14268506 |
| E12 | FundedNext HC on EAs | n/a | "FundedNext Futures allows the use of automated trading systems, including Expert Advisors (EAs) and trading bots , during both the Challenge Phase and on FundedNext Accounts" ; "Any strategies that exploit system vulnerabilities —such as latency abuse or order flooding —are strictly prohibited." | HC 14298560 (April 9, 2026) | FundedNext | firm-page | fn_14298560 |
| E13 | FundedNext hold-time rule | 5 ticks / 15-20 s | "2.2.7. Entering and exiting trades within 5 ticks or without reasonable holding (15-20 seconds) repeatedly is against trading guidelines." | terms s.2.2.7 | FundedNext | firm-page | terms_fundednext |
| E14 | FundedNext Canada (except Ontario) on live-review list | n/a | "Traders who achieve live eligibility but reside in one of the listed countries will be contacted directly by our Risk Desk" ... "Canada (except Ontario)" | HC 17228971 (dateModified 2026-09-30) | FundedNext | firm-page | fn_17228971 |
| E15 | FundedNext Legacy funded: no DLL, no consistency | MLL $1,000/$2,000/$3,000 (25/50/100K) trailing EOD | "On the Legacy FundedNext Account there is no Consistency Rule and no daily loss limit , but the Maximum Loss Limit still applies — 1,000(25K) , 2,000(50K) , 3,000(100K)" | HC 17229581 (2026-09-30) | FundedNext | firm-page | fn_17229581 |
| E16 | DayTraders allows custom algorithms and bots, HFT banned | n/a | "Yes. DayTraders allows traders to use AI tools, automations, workflows, scripts, and custom algorithms, as long as they follow all account rules and do not qualify as High-Frequency Trading." ; "Can I Use a Trading Bot? Yes, as long as the bot does not operate as High-Frequency Trading" | HC 17281269, dateModified 2026-10-01 | daytraders.com/help | firm-page | dt_ai |
| E17 | DayTraders HFT definition | milliseconds | "HFT is not allowed when the system is designed to trade at extremely high speeds, especially in milliseconds." ; allowed: "A custom strategy that places trades at normal execution speeds" | same | same | firm-page | dt_ai |
| E18 | DayTraders flat by 4:59 PM ET | 15:59 CT | "All trades should be closed by 4:59 PM ET." | HC 9854981 (December 17, 2025) | same | firm-page | dt_close |
| E19 | DayTraders news allowed; eval consistency 50% | 50% | "News Trading: is allowed." ; "During the evaluation phase, there is a 50% consistency rule." | Evaluation Account Rules (August 24, 2026) | same | firm-page | dt_evalrules |
| E20 | DayTraders EOD plan parameters | 50K EOD: target $3,000, EOD trailing $2,000, DLL $1,250, 10 minis/100 micros | "Full EOD Account Parameters: 25k EOD 50k EOD 150k EOD 300k EOD ... Drawdown Type EOD Trailing ... Profit Target $1,500 $3,000 $8,500 $15,000 Total Drawdown $1,000 $2,000 $4,000 $6,500 Daily Loss Limit $800 $1,250 $2,000 $3,250 ... Consistency Rule 50% 50% 50% 50%" | HC 10131750 | same | firm-page | dt_sizes |
| E21 | DayTraders Canada not restricted | n/a | restricted list ("Afghanistan Jordan Russia ... Zimbabwe Jersey Reunion") has no Canada | HC 9854908 | same | firm-page | dt_country |
| E22 | The5ers Futures Swing overnight limits | 1 mini / 10 micros; no weekend | "Swing : You can hold 1 mini contract or 10 micro contracts overnight. Bigger positions must close at least 10 minutes before market close." ; "Both programs : No weekend holding allowed." | FAQ "last update: July 15, 2026" | the5ers.com/futures-faqs | firm-page | 5ers_overnight |
| E23 | The5ers Futures bans algorithmic trading | n/a | Q "Is High-Frequency Trading, Algorithmic Trading, or Hedging Permitted?" A "No. These practices are strictly forbidden. Any trader found using them will be banned from our programs." | FAQ "last update: October 12, 2026" | same | firm-page | 5ers_algo |
| E24 | The5ers Futures general rules | max loss 4% EOD; consistency 40% per trade | "Maximum loss (EOD): 4% in both evaluation and funded stages. Consistency: One trade cannot represent more than 40% of total profits ... News trading: Allowed. Overnight positions: Allowed on Swing accounts ." | FAQ "last update: October 12, 2026" | same | firm-page | 5ers_general |
| E25 | Alpha Futures: automation banned; semi-auto defined | 100 trades/day | "The use of AI, bots, and other automated trading mechanisms is strictly prohibited across all account types. Semi-Automated Trading, such as a custom indicator that gives buy or sell signals, is permissible under the condition that the user manually places, monitors, and manages the trade" ; "Any form of hands-off, continuous day and night trading, or any other type of full automation is strictly forbidden." | HC 9508585 (2025-10-30) | help.alpha-futures.com | firm-page | alpha_9508585 |
| E26 | Alpha sim flat 4:20 PM ET; Prime Live overnight | 15:20 CT | "all trades must be closed before 4:20PM EST every day" ; Live: "Swing trading/holding overnight is indeed permitted" | HC 9492096 (2026-07-17); HC 11023753 (2026-06-20) | same | firm-page | alpha_9492096, alpha_11023753 |
| E27 | Alpha Standard parameters | 50K target $3,000, MLL $2,000; 50% eval / 40% qualified consistency | "Standard Account Parameters ... Profit Target $3,000 $6,000 $9,000 Maximum Loss Limit $2,000 $3,000 $4,500 Daily Loss Guard (NONE on Evaluation!)" ; "Consistency 50% on Evaluation 40% on Qualified" | HC 11632512 (2026-07-27) | same | firm-page | alpha_11632512 |
| E28 | Alpha news | n/a | "There are no news trading restrictions for any Evaluation Accounts. Advanced Qualified Accounts do not have News Trading Restrictions" | HC 9492063 (July 27, 2026) | same | firm-page | alpha_9492063 |
| E29 | MFFU automation allowed; HFT banned | n/a | "High-frequency Trading is not allowed on our plans. Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment." | HC 8444599 (2026-08-24) | help.myfundedfutures.com | firm-page | mffu_8444599 |
| E30 | MFFU flat 4:10 PM ET | 15:10 CT | "can remain open until the New York session closes at 4:10 PM EST" | HC 9558251 | same | firm-page | mffu_9558251 |
| E31 | MFFU Rapid EOD 50K plan rules | target $3,000; MLL EOD $2,000; no DLL; 30% eval consistency; T1 news yes eval / no sim funded | "Profit Target $3,000 Maximum Loss Limit (EOD) $2,000 Daily Loss Limit None Max Contract 3 mini / 30 micro Consistency 30% (Eval Only) ... T1 News Trading Yes" ; sim funded: "T1 News Trading No" | HC 16158363 (August 24, 2026) | same | firm-page | mffu_16158363 |
| E32 | MFFU news-burst ban | n/a | "Utilizing strategies that exploit immediate news bursts, such as straddles or strangles." | HC 8230009 (August 31, 2026) | same | firm-page | mffu_8230009 |
| E33 | MFFU restricted list (modified 2026-10-14) does not name Canada | 0 hits for "Canada" | page "Updated this week"; restricted-country list has no Canada entry | HC 8229993 (dateModified 2026-10-14T16:54:30Z) | same | firm-page | mffu_8229993 |
| E34 | TradeDay: no API; third-party bots forbidden | n/a | "We do not make platform APIs available to traders." ; "Algos and Bots purchased from a third party and employed by the trader are forbidden." | HC 103000085101 (Modified Fri, 28 Nov, 2025; unchanged vs E.13) | tradeday.freshdesk.com | firm-page | td_103000085101 |
| E35 | TradeDay Canada outside Ontario: sim only | n/a | "German citizens and Canadian citizens or residents outside the province of Ontario are not eligible for Funded Live accounts. Traders in this category who pass an evaluation may trade in a Funded Sim account only and may remain in Funded Sim indefinitely." | HC 103000123294 | same | firm-page | td_103000123294 |
| E36 | TradeDay Tier 1 auto-flat | 2 min each side | "TradeDay will auto-liquidate all open positions 2 minutes before TradeDay's tier 1 economic data releases , and open markets back up to trade 2 minutes after" | HC 103000081072 (22 Feb 2025) | same | firm-page | td_103000081072 |
| E37 | Phidias Premium overnight and over-week; semi-auto only | 50K EOD $2,500; 100K $3,000 | "Premium Overnight & over-week positions ALLOWED" ; "The use of robots, fully automated trading algorithms, or any other form of automated trading is not permitted. Only semi-automated software is permitted, provided the trader actively monitors and manually adjusts all trades." ; "50K Eval Drawdown $2,500 max loss 100K Eval Drawdown $3,000 max loss" ; "News Trading Authorized on ALL accounts" | rules page, article:modified_time 2026-09-22T08:15:33 (unchanged vs E.13) | phidiaspropfirm.com/rules | firm-page | phidias_rules |
| E38 | ETF terms (updated after E.13) keep written-authorization rule | n/a | "(ac) makes use of artificial intelligence (AI), bots, automated trading systems, trade copiers, or other automated trading strategies that are not expressly authorized in writing by ETF." ; "'AI' means systems ... (including ... automated decision-making systems)" | Terms, "Last updated: October 11, 2026" (terms page, read for the terms check) | elitetraderfunding.com/terms-of-service | firm-page | terms_etf |
| E39 | ETF Diamond Hands 100K numbers | EOD DD $3,500; DLL $1,500; target $5,000; 2 minis / 20 micros | (search summary of elitetraderfunding.app/diamond-hands-evaluation; not fetched: terms forbid) | WebSearch 2026-10-18 | ETF | firm-page [secondary-only] | none |
| E40 | TPT terms: copiers and "third-party automation tools" are the trader's responsibility | n/a | "Traders are fully responsible for the use of any trade copiers or third-party automation tools connected to their TakeProfit Trader accounts." | takeprofittrader.com/terms (terms page) | TPT | firm-page | terms_tpt2 |
| E41 | TPT bans bots on Test, PRO, PRO+; PRO flat 1 min around FOMC/NFP/CPI | 1 min | (search summary of the UTP and PRO Account Rules articles; not fetched) | WebSearch | TPT | firm-page [secondary-only] | none |
| E42 | Tradeify personal bot allowed; Risk & Compliance FAQ dated 2026-09-15 | n/a | (search summary of help.tradeify.co 10468318 and 17069653; not fetched) | WebSearch | Tradeify | firm-page [secondary-only] | none |
| E43 | Lucid: automation permitted; new LucidMaxx (invite-only) and New Live Structure articles; FAQ vs support conflict on LucidLive overnight | n/a | (search summary of support.lucidtrading.com 11404728, 17327076, 16558826 and lucidtrading.com/general-faq; not fetched) | WebSearch | Lucid | firm-page [secondary-only] | none |
| E44 | Apex user agreement: each order initiated manually | n/a | (search summary of dashboard.apextraderfunding.com/legal/user-agreement: trading must be "initiated manually by the User through a discrete and intentional action for each individual order") | WebSearch | Apex | firm-page [secondary-only] | none |
| E45 | Bulenox: personal user-built tools only; third-party algorithms need management approval; $100/mo API fee | $100/mo | Terms PDF (read for the terms check) carries the approval rule per E.13 [P1-57]; current FAQ via search summary | WebSearch + E.13 | Bulenox | firm-page [secondary-only] | terms_bulenox_pdf |
| E46 | AquaFutures: full automation banned; semi-auto with trader present; overnight-gap exploitation prohibited | 100 trades/day | (search summary of intercom.help/aquafutures-help-center 15863742; not fetched) | WebSearch | AquaFutures | firm-page [secondary-only] | none |
| E47 | Funded Futures Network: flat by 4:50 PM ET; automation "at FFN's discretion"; flat 1 min around Tier 1 news | n/a | (search summary of third-party reviews only; FFN rules page needs login) | WebSearch | reviews | pointer [secondary-only] | none |
| E48 | PropShopTrader Gladiator Swing: "Overnight & Weekend holding allowed"; Tickblaze "twelve ready-to-run systems"; FAQ titled "Do you allow Algos or Fully Automated Strategies?" (answer not seen) | 12.5K swing trailing DD $1,250 | (search summaries of propshoptrader.com/pricing and FAQ; not fetched) | WebSearch | PropShopTrader | firm-page [secondary-only] | none |
| E49 | Top One Futures terms ban bots/EAs | n/a | "Using bots, Expert Advisors (EAs), or automated trading systems." (listed as prohibited) | terms, "Last updated: June 10, 2026" | toponefutures.com | firm-page | terms_topone |
| E50 | Earn2Trade terms (unchanged wording vs E.13) | n/a | "You shall not create or use any program, tags, markers, bots, mousetraps, highjackers or other similar computer routines or sub-routines to automatically access or manipulate the Service" | terms page | earn2trade.com | firm-page | terms_e2t |
| E51 | Leeloo: automation banned (support pages) | n/a | (search summary of support.leelootrading.com a205; not fetched) | WebSearch | Leeloo | firm-page [secondary-only] | none |

## 4. Negative evidence

- The5ers Futures, newly read, bans algorithmic trading outright (E23). Its Swing plan allows overnight holds but caps
  them at 1 mini or 10 micros and forbids weekend holds (E22). It is not an automated multi-day venue.
- AquaFutures (new) bans full automation, and even its overnight-gap and news-execution strategies are listed as
  prohibited (E46) [secondary-only].
- Funded Futures Network (new): flat daily per third-party reviews; its rules are behind a login (E47) [unverified on firm page].
- Topstep moved against news trading (E01 to E04). Inside Tier 1 windows, minis are blocked and micros are capped,
  e.g. 3 on a 50K Combine. A news strategy that opens equity-index or metals positions at the release cannot run at size there.
- Elite Trader Funding re-dated its terms on 2026-10-11 and kept the written-authorization rule (E38). Nothing public grants
  automation on Diamond Hands. A search of ETF's own site found no automation statement for that plan (search 2026-10-18).
- The Trading Pit Classic: third-party search results show only Futures Prime for 2026, and nothing confirms Classic
  can still be bought [secondary-only]. The E.13 caveat stands.
- Third-party "rules" sites were stale about Topstep news (a search summary says "No news window" as of 2026-10-02). Any
  such page postdates nothing: use firm pages only.

## 5. Data and cost

Not applicable to venue rules (no market data is needed). Plan prices were not re-collected, except as quoted in the
tables above. E.13 and E.19 hold the fee tables, and E.19 the Topstep fees. Topstep API: $14.50/month with code (E.13 [P1-02]),
billed as "Sim2Funded Solutions" (help 11187768).

## 6. Prop compatibility (per firm, 2026-10-18)

| Firm | Flat time | Overnight | DLL / drawdown (example plan) | Consistency / payout | Automation clause | HFT clause | News clause | Canada / BC | Changed since E.13/E.19/E.21 |
|---|---|---|---|---|---|---|---|---|---|
| Topstep | 15:10 CT | no | optional DLL; EOD trailing MLL (E.19) | XFA Standard 5 x $150 days; Consistency 3 days, 40% (E09) | API allowed, no VPS (E06) | "no HFT" (E.19) | **NEW Tier 1 window** (E01-E04); P06 unchanged (E07) | Canadians yes (E08) | YES: Tier 1 window (2026-10-15/16); payout text (2026-10-13) |
| FundedNext Futures | 15:10 CT | no (E11) | Legacy MLL trailing EOD $1K/$2K/$3K; funded no DLL (E15) | Legacy funded no consistency (E15) | "allowed" (terms 2.2.6, E10) | latency abuse/order flooding banned; 15-20 s hold guideline (E12, E13) | not found (E.13 UNSOURCED) | Canada exc. Ontario on live-review list (E14) | terms clause read now (E.13 found none in the Challenge terms) |
| DayTraders.com (NEW) | 15:59 CT (E18) | no | 50K EOD trailing $2,000, DLL $1,250 (E20) | eval 50% (E19) | custom algorithms and bots allowed (E16) | ms-speed HFT banned (E17) | allowed (E19) | Canada not listed (E21) | new to program |
| MyFundedFutures | 15:10 CT (E30) | no | Rapid EOD 50K MLL $2,000, no DLL (E31) | 30% eval (E31) | allowed, not to exploit sim fills (E29) | banned (E29) | sim funded T1 no; straddles banned (E31, E32) | Canada not listed (E33) | restricted list edited 2026-10-14 (Canada still absent) |
| Lucid | 15:45 CT (E.13) | no (sim) | Flex EOD (E.13) | per plan | permitted (E43) [secondary-only] | banned | Flex/Pro/Direct allowed (E.13) | not restricted (E.13) | new LucidMaxx and Live articles (E43) [secondary-only] |
| Tradeify | 15:45 CT (E.13) | no | EOD (E.13) | per plan | own algorithm only (E42) [secondary-only] | HFT bots banned | "own risk" (E.13) | E.13 | Risk & Compliance FAQ 2026-09-15 (E42) |
| Bulenox | 15:59 CT (E.13) | no | Option 1/2 (E.13) | per plan | personal tools; third-party approval (E45) | rapid algos banned | E.13 | not restricted (E.13) | none found |
| Alpha Futures | 15:20 CT (E26) | sim no; Prime Live yes | Standard 50K MLL $2,000 (E27) | 50% eval / 40% qualified (E27) | banned; semi-auto with manual placement (E25) | >100 trades/day (E25) | eval none (E28) | not listed (alpha_9523389) | none (pages 2025-10 to 2026-08) |
| TradeDay | 10 min before close (E.13) | no | E.13 | E.13 | own ATS on supported platforms; no API (E34) | >200 trades/day (E.13) | auto-flat ±2 min (E36) | BC: sim only (E35) | none |
| Take Profit Trader | 15:55 CT (E.13) | no | E.13 | E.13 | banned (E41) [secondary-only] | n/a | PRO flat ±1 min FOMC/NFP/CPI (E41) | E.13 | none found |
| Apex | 15:59 CT (E.13) | no | EOD (E.13) | 50% PA (search) | banned; user agreement: each order manual (E44) [secondary-only] | banned | E.13 | E.13 | none confirmed since E.13 |
| Phidias Premium | none (overnight ok) | yes, and over-week (E37) | EOD $2,500 (50K) / $3,000 (100K) (E37) | 30% on CASH (E.13) | semi-automated only (E37) | banned | allowed (E37) | not restricted (E.13) | none (2026-09-22) |
| The5ers Futures (NEW) | Day Trade: 10 min before close | Swing: 1 mini / 10 micros (E22) | 4% EOD max loss (E24) | 40% per trade (E24) | algorithmic forbidden (E23) | banned | allowed (E24) | not read | new; FAQ re-dated 2026-10-12 |
| ETF DTF / Diamond Hands | none | yes, and weekends (E.13) | DH 100K EOD $3,500, DLL $1,500 (E39) [secondary-only] | E.13 | written authorization only (E38) | abusive HFT banned (E38) | no restrictions (E.13) | E.13 | terms re-dated 2026-10-11, clause same |
| PropEd | E.21 | yes | E.21 | E.21 | not granted publicly (E.21) | E.21 | allowed (E.13) | not restricted (E.21) | not refetched (terms forbid) |
| PropShopTrader (NEW) | intraday 16:45 ET (search) | Swing: yes (E48) | Swing 12.5K trailing $1,250 (E48) | 30% (search) | unread (E48) | unread | FAQ exists, unread | unread | new; terms forbid scraping |
| AquaFutures (NEW) | unread | gap exploitation banned (E46) | Beginner 25K EOD $1,000 (pointer) | 40% Beginner (pointer) | full automation banned; semi-auto (E46) | >=100 trades/day banned | review around events (E46) | unread | new |
| Funded Futures Network (NEW) | 15:50 CT (E47) | no | 50K EOD $2,000 (pointer) | n/a | discretionary (E47) | n/a | flat ±1 min T1 (E47) | unread | new |
| Earn2Trade, Leeloo, Top One, The Trading Pit, FFF | E.13 | E.13 | E.13 | E.13 | unchanged wording where read (E49, E50, E51) | | | | none found |

## 7. Overlap with tested mechanisms

Not applicable: no trading hypothesis is proposed. The Topstep Tier 1 window bears directly on any news candidate:
K2 rates releases (rates are unaffected), K5-fomc-01 (gold is affected: GC blocked, MGC capped), and K1/K-equity
release-window members (affected). That is a constraint for the lead to apply, not an overlap claim.

## 8. Earlier verdicts the update supports, weakens or overturns

| Verdict | Effect | Quote | Source |
|---|---|---|---|
| E.19 rule R040 `news_flatten_required = false` | **overturns** (in part) | "Topstep restricts trading for a short period during Tier 1 News Events." (E04) and the micro cap, mini block and pending-order rule (E01, E03) | help 8284211 (2026-10-15), 13613539 (2026-10-16) |
| E.19 / brief s.3 summary "news trading allowed but NOT at full maximum position size into a scheduled major release (P06)" | **weakens** (P06 still stands, but a hard platform window now sits on top of it for equity index and metals) | "Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes" | E01 |
| V38 "PropEd Capital, the only firm found whose terms allow automated strategies with overnight holds" | **supports V39's correction** (no firm found grants both publicly) | The5ers: "Algorithmic Trading ... strictly forbidden" (E23); Phidias "Only semi-automated software is permitted" (E37); ETF "not expressly authorized in writing" (E38) | E23, E37, E38 |
| V39 "manual or semi-automated execution is acceptable" | **supports** (widens the overnight set) | The5ers Swing "You can hold 1 mini contract or 10 micro contracts overnight" (E22); Phidias Premium overnight and over-week (E37) | E22, E37 |
| E.13 "FundedNext: Challenge terms: no automation clause found [P2-156]" | **overturns** (clause exists now) | "2.2.6. Using automated trading bots, artificial intelligence, or ultra-high-speed execution strategies is allowed." (terms last updated 25 September 2026) | E10 |
| E.13 Topstep row (flat 15:10, API allowed, Canadians yes) | **supports** | E05, E06, E08 | Topstep help |
| E.13 Phidias row | **supports** (unchanged, modified 2026-09-22) | E37 | phidias rules |
| E.13 Trading Pit Classic "may no longer be sold" | **supports** (still no current listing found) [secondary-only] | search found only Futures Prime for 2026 | WebSearch |
| E.13 BC note "TradeDay: evaluation and Funded Sim only" | **supports** | E35 | TradeDay HC |

## 9. Fetch log, terms, budget notices

Terms rulings: appended to reports/stage_e25_briefs/terms/terms_log.md (R9 lines). Allowed for named pages one at a time:
topstep.com, tradeday.com, alpha-futures.com, fundednext.com, myfundedfutures.com, phidiaspropfirm.com (main site only),
fundedfuturesfamily.com, toponefutures.com, daytraders.com, the5ers.com, fxify.com.
Forbidden, so search results only:
- tradeify.co
- bulenox.com
- elitetraderfunding.com
- leelootrading.com
- thetradingpit.com: its general terms ban "automated retrieval or extraction of data (scraping, crawling ...)". This is a
  stricter ruling than E.13, which fetched TTP pages.
- earn2trade.com: a stricter ruling than E.13.
- takeprofittrader.com
- propshoptrader.com (dashboardanalytix terms)
- propedcapital.com: the E.21 ruling, re-used.

Terms unread, so treated as forbidden: apextraderfunding.com (Cloudflare 403), lucidtrading.com (403), aquafutures.io
(JS shell), fundedfuturesnetwork.com (TLS chain error, rules behind login), propfirmmatch.com (403).

Deviations:
- propshoptrader.com and aquafutures.io homepages (and fundedfuturesnetwork.com, through scrapling fetch) were fetched once,
  only to find the terms link, before their terms were read. None of that content is used as evidence, and the files are
  listed in DO_NOT_COMMIT.txt.
- Only the terms pages of forbidden hosts were saved, as the terms check requires. They are listed in DO_NOT_COMMIT.txt.

Budget notices:
- 2026-10-18T08:44:36Z (01:44 PDT): Firecrawl firecrawl_search returned "Insufficient credits to perform this request"
  (4 calls, none run). Fallback: WebSearch and curl. Firecrawl was not used again.
- Playwright: "Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome" (about 08:51Z). Not used.
  Scrapling fetch was used once instead, after a free-memory check (2,865 MB available).
- WebSearch: 29 calls (cap 45). No over-budget notice.

Fetch log (url | UTC | sha256 first 12 | saved | HTTP status or rc | tool):

| url | UTC | sha256 (12) | saved | status | tool |
|---|---|---|---|---|---|
| https://www.topstep.com/terms-of-use | 2026-10-18T08:40:28Z | c9566df52a03 | pages/R9/terms_topstep.html | 200 | curl |
| https://www.thetradingpit.com/general-terms-and-conditions | 2026-10-18T08:40:28Z | c450592cc326 | pages/R9/terms_ttp.html | 200 | curl |
| https://tradeify.co/terms-of-use | 2026-10-18T08:40:34Z | 1d321f74b905 | pages/R9/terms_tradeify.html | 200 | curl |
| https://elitetraderfunding.com/terms-of-service | 2026-10-18T08:40:34Z | 83cafcbaf3e3 | pages/R9/terms_etf.html | 200 | curl |
| https://lucidtrading.com/terms-of-use/ | 2026-10-18T08:40:39Z | c4a432d5508a | pages/R9/terms_lucid.html | 403 | curl |
| https://leelootrading.com/terms-of-service | 2026-10-18T08:40:41Z | adb146447487 | pages/R9/terms_leeloo.html | 200 | curl |
| https://alpha-futures.com/terms-and-conditions | 2026-10-18T08:40:45Z | 55ecb0435754 | pages/R9/terms_alpha.html | 200 | curl |
| https://bulenox.com/legal/Terms_of_Use.pdf | 2026-10-18T08:40:47Z | cb4810bb9a27 | pages/R9/terms_bulenox_pdf.html | 200 | curl |
| https://fundednext.com/futures-challenge-terms | 2026-10-18T08:40:51Z | 2b27bd106443 | pages/R9/terms_fundednext.html | 200 | curl |
| https://www.toponefutures.com/terms-and-conditions | 2026-10-18T08:40:53Z | 5ea488871c1c | pages/R9/terms_topone.html | 200 | curl |
| https://www.earn2trade.com/terms-and-conditions | 2026-10-18T08:40:56Z | 16004beb55cf | pages/R9/terms_e2t.html | 200 | curl |
| https://www.fundedfuturesfamily.com/terms-and-conditions/ | 2026-10-18T08:41:00Z | bca66231e4f7 | pages/R9/terms_fff.html | 200 | curl |
| https://www.tradeday.com/terms-and-conditions | 2026-10-18T08:41:02Z | 6e9598b847b3 | pages/R9/terms_tradeday.html | 200 | curl |
| https://myfundedfutures.com/terms-of-service | 2026-10-18T08:41:07Z | 5a4121c05903 | pages/R9/terms_mffu.html | 404 | curl |
| https://phidiaspropfirm.com/tou | 2026-10-18T08:41:07Z | 3f82270c07cd | pages/R9/terms_phidias.html | 200 | curl |
| https://takeprofittrader.com/terms-and-conditions | 2026-10-18T08:41:12Z | 9917f3aa4338 | pages/R9/terms_tpt.html | 404 | curl |
| https://apextraderfunding.com/terms-and-conditions | 2026-10-18T08:41:18Z | 32b313f32a34 | pages/R9/terms_apex.html | 403 | curl |
| https://takeprofittrader.com/terms | 2026-10-18T08:42:57Z | 256e776022ee | pages/R9/terms_tpt2.html | 200 | curl |
| https://myfundedfutures.com/terms | 2026-10-18T08:42:57Z | d146749727c5 | pages/R9/terms_mffu2.html | 200 | curl |
| https://apextraderfunding.com/terms-and-conditions | 2026-10-18T08:42:57Z | bc4a1f422ef5 | pages/R9/terms_apex_sg.md | 0 | scrapling-get |
| https://lucidtrading.com/terms-of-use/ | 2026-10-18T08:42:58Z | 87299e073dba | pages/R9/terms_lucid_sg.md | 0 | scrapling-get |
| https://www.daytraders.com/ | 2026-10-18T08:44:59Z | 679dbc65900e | pages/R9/home_daytraders.html | 200 | curl |
| https://fundedfuturesnetwork.com/ | 2026-10-18T08:44:59Z |  | pages/R9/home_ffn.html | 000 | curl |
| https://aquafutures.io/ | 2026-10-18T08:44:59Z | 1a018ba4202f | pages/R9/home_aqua.html | 200 | curl |
| https://propshoptrader.com/ | 2026-10-18T08:44:59Z | be31e01da5f7 | pages/R9/home_propshop.html | 200 | curl |
| https://the5ers.com/ | 2026-10-18T08:44:59Z | c48cea53951c | pages/R9/home_5ers.html | 200 | curl |
| https://fxify.com/futures | 2026-10-18T08:44:59Z | 81abbfefbb18 | pages/R9/home_fxifyfut.html | 404 | curl |
| https://www.daytraders.com/privacy | 2026-10-18T08:45:15Z | c867d5162d91 | pages/R9/terms_daytraders.html | 200 | curl |
| https://www.fundedfuturesnetwork.com/ | 2026-10-18T08:45:15Z |  | pages/R9/home_ffn.html | 000 | curl |
| https://aquafutures.io/legal/terms-and-conditions | 2026-10-18T08:45:15Z | 1a018ba4202f | pages/R9/terms_aqua.html | 200 | curl |
| https://fxify.com/terms-and-conditions/ | 2026-10-18T08:45:15Z | b2a6ac6799a4 | pages/R9/terms_fxify.html | 200 | curl |
| https://the5ers.com/terms-and-conditions/ | 2026-10-18T08:45:15Z | 4bc6c71e7b55 | pages/R9/terms_5ers.html | 200 | curl |
| https://dashboardanalytix.com/client-terms-and-policies/ | 2026-10-18T08:45:15Z | 4fda4b8e8ad1 | pages/R9/terms_propshop.html | 200 | curl |
| https://www.daytraders.com/help/ | 2026-10-18T08:45:41Z | 94a498b2833d | pages/R9/dt_help.html | 200 | curl |
| https://the5ers.com/futures-faqs/ | 2026-10-18T08:45:41Z | 53b43966b44e | pages/R9/5ers_futfaq.html | 200 | curl |
| https://fxify.com/faqs/ | 2026-10-18T08:45:41Z | 8bffaeff495b | pages/R9/fxify_faqs.html | 200 | curl |
| https://www.daytraders.com/overnight-trading-rules-prop-firms | 2026-10-18T08:45:47Z | 7df1a14b967d | pages/R9/dt_overnight_blog.html | 200 | curl |
| https://the5ers.com/faqs/prohibited-trading-practices/ | 2026-10-18T08:45:47Z | f5d7b6bdcf0b | pages/R9/5ers_prohib.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/9492096 | 2026-10-18T08:46:18Z | 984d4a521851 | pages/R9/alpha_9492096.html | 200 | curl |
| https://helpfutures.fundednext.com/en/articles/14268506 | 2026-10-18T08:46:18Z | 7d7bb60b487a | pages/R9/fn_14268506.html | 200 | curl |
| https://tradeday.freshdesk.com/support/solutions/articles/103000085101 | 2026-10-18T08:46:18Z | c30c953898f9 | pages/R9/td_103000085101.html | 200 | curl |
| https://help.topstep.com/en/articles/8284206 | 2026-10-18T08:46:18Z | 7c8b7b32120b | pages/R9/ts_8284206.html | 200 | curl |
| https://help.myfundedfutures.com/en/articles/8444599 | 2026-10-18T08:46:18Z | edf4f8345936 | pages/R9/mffu_8444599.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/9508585 | 2026-10-18T08:46:24Z | 57df6c41d564 | pages/R9/alpha_9508585.html | 200 | curl |
| https://helpfutures.fundednext.com/en/articles/14298560 | 2026-10-18T08:46:24Z | 894edfc7ff65 | pages/R9/fn_14298560.html | 200 | curl |
| https://tradeday.freshdesk.com/support/solutions/articles/103000018874 | 2026-10-18T08:46:24Z | 2e0b1e659a0a | pages/R9/td_103000018874.html | 200 | curl |
| https://help.myfundedfutures.com/en/articles/9558251 | 2026-10-18T08:46:24Z | 83e51ea23c6c | pages/R9/mffu_9558251.html | 200 | curl |
| https://help.topstep.com/en/articles/11187768 | 2026-10-18T08:46:24Z | b93c21e559f1 | pages/R9/ts_11187768.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/9523389 | 2026-10-18T08:46:30Z | f31ce975efa4 | pages/R9/alpha_9523389.html | 200 | curl |
| https://help.myfundedfutures.com/en/articles/8230009 | 2026-10-18T08:46:30Z | 8fc5a46700f1 | pages/R9/mffu_8230009.html | 200 | curl |
| https://help.topstep.com/en/articles/8284197 | 2026-10-18T08:46:30Z | 0c16884cb41e | pages/R9/ts_8284197.html | 200 | curl |
| https://tradeday.freshdesk.com/support/solutions/articles/103000123294 | 2026-10-18T08:46:30Z | 7310129e9a93 | pages/R9/td_103000123294.html | 200 | curl |
| https://helpfutures.fundednext.com/en/articles/14298337 | 2026-10-18T08:46:30Z | d12c3349aa6e | pages/R9/fn_14298337.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/9492063 | 2026-10-18T08:46:35Z | 2be5a2e6b5f9 | pages/R9/alpha_9492063.html | 200 | curl |
| https://help.myfundedfutures.com/en/articles/8229993 | 2026-10-18T08:46:36Z | 4189db4bf6fc | pages/R9/mffu_8229993.html | 200 | curl |
| https://help.topstep.com/en/articles/8284215 | 2026-10-18T08:46:36Z | a6d45d39869b | pages/R9/ts_8284215.html | 200 | curl |
| https://tradeday.freshdesk.com/support/solutions/articles/103000081072 | 2026-10-18T08:46:36Z | 4615b2feef2d | pages/R9/td_103000081072.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/11023753 | 2026-10-18T08:46:41Z | 6dc7649364be | pages/R9/alpha_11023753.html | 200 | curl |
| https://helpfutures.fundednext.com/en/articles/17228971 | 2026-10-18T08:46:41Z | 11b3ee28ca80 | pages/R9/fn_17228971.html | 200 | curl |
| https://help.topstep.com/en/articles/8284116 | 2026-10-18T08:46:42Z | c97fcd9c78b4 | pages/R9/ts_8284116.html | 200 | curl |
| https://help.myfundedfutures.com/en/articles/16158363 | 2026-10-18T08:46:42Z | 01dd3919d2ba | pages/R9/mffu_16158363.html | 200 | curl |
| https://tradeday.freshdesk.com/support/solutions/articles/103000304248 | 2026-10-18T08:46:42Z | befc7fea1194 | pages/R9/td_103000304248.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/9491999 | 2026-10-18T08:46:46Z | fcf0b231f5a4 | pages/R9/alpha_9491999.html | 200 | curl |
| https://helpfutures.fundednext.com/en/articles/17229536 | 2026-10-18T08:46:46Z | ea2b61eed053 | pages/R9/fn_17229536.html | 200 | curl |
| https://help.topstep.com/en/articles/8284211 | 2026-10-18T08:46:48Z | 98c43f88bf1f | pages/R9/ts_8284211.html | 200 | curl |
| https://help.myfundedfutures.com/en/articles/14290805 | 2026-10-18T08:46:48Z | 271ec93ba9c8 | pages/R9/mffu_14290805.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/9492051 | 2026-10-18T08:46:52Z | 08f1874131a3 | pages/R9/alpha_9492051.html | 200 | curl |
| https://helpfutures.fundednext.com/en/articles/17229581 | 2026-10-18T08:46:52Z | d272eb3c8fcf | pages/R9/fn_17229581.html | 200 | curl |
| https://help.topstep.com/en/articles/10305426 | 2026-10-18T08:46:54Z | b9ae09d5ed26 | pages/R9/ts_10305426.html | 200 | curl |
| https://help.myfundedfutures.com/en/articles/13745661 | 2026-10-18T08:46:54Z | 7e52faab92fd | pages/R9/mffu_13745661.html | 200 | curl |
| https://help.alpha-futures.com/en/articles/11632512 | 2026-10-18T08:46:57Z | 6817200335a1 | pages/R9/alpha_11632512.html | 200 | curl |
| https://phidiaspropfirm.com/rules | 2026-10-18T08:47:00Z | bb9ccc4e6cea | pages/R9/phidias_rules.html | 200 | curl |
| https://help.topstep.com/en/articles/8284204 | 2026-10-18T08:47:00Z | 13944fd9191e | pages/R9/ts_8284204.html | 200 | curl |
| https://help.topstep.com/en/articles/10490293 | 2026-10-18T08:47:06Z | de4d2292ec3a | pages/R9/ts_10490293.html | 200 | curl |
| https://help.topstep.com/en/articles/8284208 | 2026-10-18T08:47:12Z | 97744572c9a0 | pages/R9/ts_8284208.html | 200 | curl |
| https://help.topstep.com/en/articles/8284233 | 2026-10-18T08:47:18Z | 56f65f1f4f4c | pages/R9/ts_8284233.html | 200 | curl |
| https://help.topstep.com/en/articles/13613539 | 2026-10-18T08:47:24Z | c3968edb2ef9 | pages/R9/ts_13613539.html | 200 | curl |
| https://daytraders.com/help/collections/10316680-general-faqs | 2026-10-18T08:49:54Z | 68e90b82ab7a | pages/R9/dt_coll_general.html | 200 | curl |
| https://daytraders.com/help/articles/9859996-what-products-do-we-offer | 2026-10-18T08:49:59Z | 0abebcf1e4e6 | pages/R9/dt_products.html | 200 | curl |
| https://daytraders.com/help/articles/17281269-can-i-trade-with-ai-automations-scripts-or-algorithms | 2026-10-18T08:50:14Z | fde05185be44 | pages/R9/dt_ai.html | 200 | curl |
| https://daytraders.com/help/articles/9854981-closing-trades-key-cutoff-times-and-holiday-considerations | 2026-10-18T08:50:19Z | 85deba53ddff | pages/R9/dt_close.html | 200 | curl |
| https://daytraders.com/help/collections/10393779-getting-started | 2026-10-18T08:50:37Z | 0bfdf14ca78a | pages/R9/dt_coll_start.html | 200 | curl |
| https://daytraders.com/help/collections/10394879-evaluation-accounts | 2026-10-18T08:50:43Z | c6f15afa7d92 | pages/R9/dt_coll_eval.html | 200 | curl |
| https://daytraders.com/help/articles/14368378-evaluation-account-rules | 2026-10-18T08:50:54Z | 37a46bfdf175 | pages/R9/dt_evalrules.html | 200 | curl |
| https://daytraders.com/help/articles/9854908-country-eligibility-for-trading-current-restrictions-explained | 2026-10-18T08:51:00Z | ca6589406ecf | pages/R9/dt_country.html | 200 | curl |
| https://daytraders.com/help/articles/10131750-evaluation-account-sizes-fees-and-details | 2026-10-18T08:51:05Z | 869be534e2e0 | pages/R9/dt_sizes.html | 200 | curl |
| https://fundedfuturesnetwork.com/ | 2026-10-18T08:51:39Z |  | pages/R9/home_ffn.md | rc1 | scrapling-get |
| https://fundedfuturesnetwork.com/ | 2026-10-18T08:52:00Z | 81ccdc098974 | pages/R9/home_ffn.md | rc0 | scrapling-fetch |
| https://aquafutures.io/legal/terms-and-conditions | 2026-10-18T08:52:11Z | 5ee67cd2914e | pages/R9/terms_aqua_sf.md | rc0 | scrapling-fetch |
| https://propfirmmatch.com/terms-of-service | 2026-10-18T08:52:50Z | d06b51c12b2c | pages/R9/terms_pfm.html | 403 | curl |
| https://the5ers.com/futures-faqs/overnight-holding-2/ | 2026-10-18T08:54:01Z | 916cd9303c15 | pages/R9/5ers_overnight.html | 200 | curl |
| https://the5ers.com/futures-faqs/is-high-frequency-algorithmic-trading-and-hedging-allowed/ | 2026-10-18T08:54:07Z | 63c3aa825072 | pages/R9/5ers_algo.html | 200 | curl |
| https://the5ers.com/futures-faqs/what-are-the-general-rules-for-the-futures-program/ | 2026-10-18T08:54:13Z | a84b71de207e | pages/R9/5ers_general.html | 200 | curl |

## 10. Unfinished and unverified

- Forbidden-terms firms (Apex, Tradeify, Lucid, TPT, Bulenox, ETF plan pages, TTP, E2T, Leeloo, PropShop, Aqua, FFN) were
  read only through search summaries. Their current plan-level numbers rest on E.13 or on [secondary-only] summaries.
  Changes since E.13 for these firms cannot be ruled out.
- PropShopTrader: the algorithm rule (FAQ "Do you allow Algos or Fully Automated Strategies?"), Canada eligibility and
  swing drawdown were not read. This is the one new overnight-and-weekend venue whose automation answer is unknown.
  A written question to the firm is the route. None was sent.
- The5ers Futures: Canada eligibility, plan prices and contract sizes were not read.
- FXIFY Futures: rules not read (homepage /futures returned 404). Search summaries conflict.
- Alpha restricted list: "Canada" had 0 hits in the fetched text. The page may render its list in an image or a
  script. Treat it as not verified.
- No firm page names British Columbia. A propfirmmatch BC page exists (forex list per search) but could not be read
  (403, terms unread).
- Topstep XFA Tier 1 caps under the Scaling Plan (table partly read) are not tabulated here; see ts_13613539.
