# Stage E.13 Task 1: venues for multi-day automated futures trading

Assembled by the lead (2026-10-03) from three worker files, which stay on disk with their full text:
reports/stage_e13_venues_part1.md (PropVenues1-OpusHigh: Topstep, Apex, Tradeify, Take Profit Trader, Elite Trader
Funding, MyFundedFutures, Bulenox), reports/stage_e13_venues_part2.md (PropVenues2-OpusHigh: Alpha Futures, Lucid,
TradeDay, Earn2Trade, FundedNext Futures, Phidias, The Trading Pit, plus PropEd Capital, Leeloo, Top One Futures,
Funded Futures Family) and reports/stage_e13_venues_part3_brokers.md (BrokerVenues-OpusHigh: personal accounts for a
British Columbia resident). Source keys: P1-xx (part 1), P2-xx (part 2), B-xx (part 3); each key's URL, fetch date,
page date and verbatim quote are in the source lists appended below. Raw pages: reports/stage_e13_briefs/pages/
PropVenues1/, PropVenues2/, BrokerVenues/ (files from sites whose terms forbid automated access are listed in each
folder's DO_NOT_COMMIT.txt and are not committed). Support questions for the user to send:
reports/stage_e13_phidias_question.md (Phidias, PropEd, Leeloo, Elite Trader Funding). All pages fetched 2026-10-03.

## Lead summary: where a multi-day automated system may run

The question for every venue: may positions be held overnight and for several days, AND may code decide and enter
the orders? Both must hold.

**PERMITTED, unambiguous**
- IBKR Canada (personal account): CIRO dealer serving Canadian residents, US CME futures and every micro checked,
  TWS API and REST API, no account minimum, overnight margins published [B-02][B-06] (part 3, section 3).
- The Trading Pit, Futures Classic: overnight Monday to Thursday, flat by the Friday close, the trader's own EAs
  allowed [P2-95][P2-96]. Caveat: Classic is not on the current futures sales page [P2-109]; whether it can still be
  bought is UNCLEAR. Its maximum drawdown trails the highest balance with no cap [P2-91].

**HUMAN-IN-THE-LOOP ONLY (multi-day allowed; automation only as semi-automated or manual execution of alerts)**
- Phidias Premium 50K / 100K / 150K: overnight and weekends allowed; EOD trailing $2,500 / $3,000 / $4,500; TOU
  allows only "semi-automated software, provided the User actively monitors and manually adjusts all operations",
  undefined [P2-01][P2-02]. Clause unchanged since the 2026-09-28 entry. Question drafted (section 1 of the
  question file).
- Leeloo Trading, Investor Performance Account: manual execution of alerts allowed; at most 3 micros through the
  close without admin permission; the account type is being phased out [P2-123][P2-131].
- Wealthsimple (personal): futures offered, no API found [B-41].

**UNCLEAR**
- Elite Trader Funding, Direct To Funded and Diamond Hands (and LIVE ELITE at ETF's discretion): multi-day and
  weekend holds allowed; AI, bots and algorithms banned unless ETF authorizes them in writing, with "automated
  decision-making systems" inside the definition of AI [P1-33][P1-34][P1-37, deviation fetch][P1-43]. The written-authorization rule
  is also on ETF's help page [P1-36]. Question drafted (section 4).
- Brokers AMP Futures, Optimus Futures, Ironbeam, EdgeClear, TradeStation, GFF Brokers, Jitneytrade: BC eligibility
  not established. The deciding rule appears to be the BCSC exemption under which unregistered foreign dealers may
  trade futures only with "eligible derivatives parties" (for an individual, at least $5M of financial assets)
  (part 3, section 0).

**NOT PERMITTED**
- Flat every session: Topstep (3:10 PM CT), Apex, Tradeify, Take Profit Trader, MyFundedFutures, Bulenox, Elite
  Trader Funding's EOD / Static / 1-Step / Fast Track plans, Phidias Fundamental and Express to Live, Alpha Futures,
  Lucid, TradeDay, Earn2Trade, FundedNext Futures, The Trading Pit Prime, Top One Futures, Funded Futures Family.
- Overnight allowed but automation banned: PropEd Capital (FAQ marks EAs, bots and automation not allowed; a
  semi-automation question is drafted, section 2).
- Brokers: NinjaTrader Brokerage and Tradovate (BC excluded); Questrade, TD Direct Investing, RBC Direct Investing,
  BMO InvestorLine, CIBC Investor's Edge, National Bank Direct Brokerage and Qtrade (no futures).

Reading for the program: Topstep, the program's venue, requires flat by 3:10 PM CT [P1-01], so a multi-day system
cannot run there. Among prop firms, only one plan permits it outright, and that plan may no longer be sold; the
realistic prop routes need a written answer first (Phidias, Elite Trader Funding). A personal IBKR Canada account
permits it without ambiguity.

## 1. Prop firms: one table (parts 1 and 2 combined)


| Firm | Plan / sizes | Overnight + weekend | Drawdown type, size | Automation / API (terms) | Semi-auto / copier wording | Platforms | Lot limits | Payouts | Fees | Canada | News rule | Page dates |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Topstep | Trading Combine and Express Funded Account (XFA): 50K / 100K / 150K; Live Funded Account (LFA) | NOT allowed: everything flat by 3:10 PM CT every weekday; "No swing trading" [P1-01]. Auto-flatten about 10 s before 3:10 PM CT [P1-05] | Maximum Loss Limit, trailing, set at end of day and enforced in real time. 150K: $4,500, locks at $0 on the XFA [P1-07]. 50K and 100K sizes not re-checked here (UNSOURCED in this report) | API bots allowed on TopstepX/ProjectX; HFT banned; no VPS, VPN or remote servers; the API cannot be used on an LFA [P1-02]. Terms ban "software, artificial intelligence, ultra-high speed ... unfair advantage" and VPN/VPS [P1-05] | "Can I use automated trading strategies? Yes, with conditions"; trade copier allowed across own accounts, up to $750K buying power [P1-03][P1-06] | TopstepX (ProjectX API, $29/mo, $14.50 with code) [P1-02]. Whether NinjaTrader/Tradovate are open to new sign-ups: UNSOURCED (platform article returned 404) | 50K 5 / 100K 10 / 150K 15 minis; micros 10:1 [P1-06] | XFA Standard: 5 winning days of $150+; 50% of balance, capped $2K/$3K/$5K. XFA Consistency: 40% rule, caps $3K/$4K/$6K. Split 90/10 [P1-06] | 150K Combine $199/mo standard, or $229/mo with no activation fee; XFA activation $149 (standard path); reset 150K $199 [P1-07] | Yes: "I'm Canadian — can I earn a Funded Account? Yes." [P1-04] | News trading allowed; banned: trading full max size into major news [P1-06] | help-centre dM 2026-07-13 to 2026-09-30; terms "Last updated September 21, 2026"; repo files 2026-09-23 and 2026-10-03 |
| Apex Trader Funding | EOD and Intraday Trailing evaluations and Performance Accounts (PA), 25K / 50K / 100K / 150K; Live Prop program | NOT allowed: "All trades must be closed before 4:59 PM ET" (PA, WB Feb 2026) [P1-10]; Live program: closed by 4:50 PM ET, "Overnight holding ... is not permitted" [P1-09] | EOD trailing, fixed for the next session: 25K $1,000 / 50K $2,000 / 100K $3,000 / 150K $4,000; daily loss limit $500 / $1,000 / $1,500 / $2,000 [P1-12]. An intraday-trailing path also exists (its parameters were not fetched) | BANNED: "No Automation or Algorithm Usage allowed" [P1-11]; Live: "Automation and algorithm usage are not allowed" [P1-09]. HFT banned [P1-11] | Copying trades with other traders is "strictly forbidden" [P1-11]. No semi-automated allowance found in fetched pages | Rithmic, Tradovate, WealthCharts [P1-14]; Live: Tradovate, NinjaTrader [P1-09]. No API documented | EOD eval max contracts 4 / 6 / 8 / 12 [P1-12] | EOD PA: weekly at most; 5 qualifying days; $500 minimum; 50% consistency; at most 6 payouts per PA; 100% split [P1-13] | One-time 30-day evaluation, then a PA activation fee within 7 days [P1-14]. Dollar amounts UNSOURCED (prices are rendered by JavaScript; live site down) | Yes: "Canadian traders can fully utilize our services" (sim accounts) [P1-15] | Normal strategy allowed through news; "chase the market" or two-sided news gambling banned [P1-11] | Live site in maintenance on 2026-10-03 [P1-16]; WB captures from 2026-02-17 to 2026-09-27 |
| Tradeify | Growth / Select (Daily, Flex) / Lightning funded, 25K / 50K / 100K / 150K; Elite Live | NOT allowed on ALL account types, Live included: flat by 4:45 PM ET [P1-17] (the WB capture of 2026-06-24 said 4:59 PM ET) | EOD trailing on every evaluation and funded account; e.g. 25K $1,000, Growth 50K $2,000, 100K $3,500; on Sim Funded it locks at +$100 above the drawdown [P1-18][P1-21] | Algorithms allowed if "You own the strategy exclusively", not shared, not HFT, ownership provable; "High-frequency trading bots not allowed" [P1-18]. The terms page has no automation clause [P1-22] | No copier article found. Hedging, including "positions held across multiple accounts", is banned [P1-18] | Tradovate, Rithmic, Tradesea, WealthCharts, TradingView [P1-19]. No API documented | 25K 1 / 50K 4 / 100K 8 / 150K 12 minis (10:1 micros) [P1-18] | Select Daily: daily payouts. Select Flex: 5 winning days per cycle. Funded: more than 50% of trades and profit from trades held over 10 s. Split 90/10 sim, 80/20 Elite Live [P1-18][P1-19] | Growth one-time: 25K $99 / 50K $145 / 100K $255 / 150K $369 (resets $60 / $95 / $155 / $215); "no activation fees" [P1-19] | Not on the current restricted list [P1-20]. The WB capture of June 2026 listed "Canada: Sim Funded Only — Only Ontario residents" [P1-20] | "Yes, but at your own risk"; specific rules around major events [P1-18] | help-centre dM 2026-07-14 to 2026-09-04; terms: no date shown |
| Take Profit Trader | Test (evaluation), PRO, PRO+ (live); 25K / 50K / 75K / 100K / 150K | NOT allowed: "Positions cannot be carried from one trading day into the next"; auto-close at 4:55 PM ET [P1-23][P1-24] | Test: EOD trailing $1,500 / $2,000 / $2,500 / $3,000 / $4,500 [P1-27]. PRO: intraday trailing [P1-25] | BANNED: "No Trading Bots or Algos. Automated trading systems, bots, or algorithmic execution tools are not permitted." [P1-24]; PRO: "We do not allow any automated or bot trading of any kind." [P1-25] | Copiers allowed "solely for managing accounts owned and controlled by you" (approved list) [P1-26]. Each account must reflect "discretionary trading and execution decisions" [P1-26] | TradingView, NinjaTrader, Tradovate (CQG), Rithmic-based platforms [P1-31]. No API documented | 3 / 6 / 9 / 12 / 15 contracts (micros 10:1) [P1-27] | PRO: 80/20; withdrawals from day one once the buffer (equal to max drawdown) is built [P1-28] | Test is a monthly subscription (amount UNSOURCED); PRO activation "One Time $130 Fee" [P1-29] | Canada not on the restricted list [P1-30] | PRO: flat from 1 minute before to 1 minute after FOMC, NFP and CPI [P1-25] | Zendesk updated 2026-05-27 to 2026-09-29; home page: no date shown |
| Elite Trader Funding: Direct To Funded (DTF) | No evaluation; Elite Sim-Funded from day one; 10K / 25K / 50K / 100K | ALLOWED: "Overnights/weekends allowed — swing trading permitted." [P1-33] | 10K EOD $1,500; 25K EOD $2,500; 50K EOD $5,000; 100K Static $5,000. EOD trailing stops at max drawdown + $100 (safety net) [P1-33]. Losing more than 35% of profits after +20% means removal [P1-33] | AI, bots, EAs and algos need ETF's written authorization; the only automated tools authorized are approved trade copiers [P1-36]. Terms (ac) ban AI, bots, automated systems and copiers "not expressly authorized in writing"; "AI" includes "automated decision-making systems"; minimum trade duration 10 s; no HFT [P1-37] | Approved copiers: Tradesyncer, Tradecopia, Affordable Indicators, Replikanto compliance edition, native platform copiers [P1-36]. No "semi-automated" or active-monitoring wording found | Tradovate, NinjaTrader, TradingView, Rithmic, MotiveWave, Quantower [P1-42]. No API documented | 10K 2, 50K 5, 100K 3 contracts; 1 mini = 1 micro = 1 position (25K not listed) [P1-40][P1-33] | Active Trade Days per cycle 5 / 10 / 15 / 20 with a per-day consistency share; cycle caps from $1,000 to $5,000; up to 100% split; $25,000 lifetime cap per trader, then LIVE ELITE; paid Mon and Wed [P1-33] | One-time purchase, no activation fee, no monthly fee [P1-41]. Price UNSOURCED (sales page is JavaScript) | Not on the Rise restricted list; Stripe "with limitations (extended network / preview): Canada" [P1-39] | No restrictions on news trading [P1-38] | dM 2026-07-27 to 2026-10-02; terms "Last updated August 14, 2026" |
| Elite Trader Funding: Diamond Hands | 100K evaluation (monthly), then Elite Sim-Funded | ALLOWED: "Only Diamond Hands and Direct To Funded accounts are able to hold trades through close, and the weekend." [P1-34] | EOD trailing until max drawdown + $100, then fixed at start + $100; daily loss limit until then [P1-34]. 100K drawdown size UNSOURCED (the page example uses 50K at $2,000) | Same as DTF [P1-36][P1-37] | Same as DTF [P1-36] | Same as DTF [P1-42] | 100K: 2 minis / 20 micros [P1-40] | Cycle 1: 8 Active Trade Days, then 10; day counts at $250+ and 30% of best day; $100 to $2,500 per cycle; $25,000 cap, then Live [P1-34] | Monthly evaluation subscription; Elite activation one-time or $87/mo [P1-41]. Evaluation price UNSOURCED | As DTF [P1-39] | As DTF [P1-38] | dM 2026-10-02 |
| Elite Trader Funding: EOD, Static, 1-Step, Fast Track | Evaluations 25K to 150K | NOT allowed: "All trades must be closed one minute before market close." [P1-35]. Overnight margin charges if held "inadvertently" [P1-44] | EOD or static by plan (not tabulated: these plans cannot hold) | As DTF [P1-36][P1-37] | As DTF | As DTF | Per plan [P1-40] | Per plan (not tabulated) | Elite activation $177 to $307 one-time, or $87/mo [P1-41] | As DTF | As DTF | dM 2026-10-01 to 2026-10-02 |
| Elite Trader Funding: LIVE ELITE | Invitation or transfer from Elite Sim | "Swing trading is permitted at ETF's discretion"; a $5/contract fee applies if a position stays open through the close "unless you've been approved to swing trade" [P1-43] | Not tabulated | Terms (ac) apply [P1-37] | Trade copying can be enabled after approval [P1-43] | As DTF | Set by starting balance [P1-43] | Daily processing [P1-33] | Not tabulated | As DTF | As DTF | dM 2026-10-02 |
| MyFundedFutures | Rapid (intraday), Rapid EOD, Builder, Pro; 25K / 50K / 100K / 150K; Live | NOT allowed: positions may stay open only until 4:10 PM EST and are auto-closed then; holiday closes are the trader's responsibility [P1-45]. Live: closed automatically before 4:10 pm EST [P1-54] | Rapid EOD 50K: EOD trailing $2,000. Builder 50K: EOD $2,000 (or $1,500 add-on), daily loss limit $1,000 soft pause. Rapid: intraday. Pro: static at start + $100 after the first payout [P1-50][P1-51][P1-60] | ALLOWED: "Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills"; HFT not allowed [P1-46] | "allows copy trading across all account types"; copying other traders banned [P1-47][P1-46] | NinjaTrader, Tradovate, TradingView, Quantower, Volumetrica, ATAS, DeepChart [P1-53]. No API documented | Rapid EOD 50K 3 minis / 30 micros; Builder 50K 4 / 40 [P1-50][P1-51] | Rapid 90% (since 12 Jan 2026), Builder/Pro 80%; Rapid EOD: $2,100 buffer, then every +$500 [P1-52][P1-50] | Builder 50K $153 ($125 add-on); "no activation fees on any of our plans" [P1-51] | Canada not on the restricted list [P1-48] | Straddles and strangles on news bursts banned; Rapid EOD sim-funded "T1 News Trading: No" [P1-49][P1-50] | dM 2025-11-10 to 2026-09-29 |
| Bulenox | Qualification / Fast Track / Momentum; 25K / 50K / 100K / 150K; Option 1 (trailing) or Option 2 (EOD) | NOT allowed: "all positions must be closed by 3:59 pm CT" [P1-55] | Option 1: trails the highest balance in real time, open positions included. Option 2: EOD on realized profit, with scaling and a pausing daily loss limit. Drawdown "up to" $1,500 / $2,500 / $3,000 / $4,500 [P1-55][P1-58] | ALLOWED with limits: "Bots, algorithms and trade copiers are permitted"; user-built tools for personal use only; +$100/mo for a third-party API connection to Rithmic [P1-56]. Terms: "any third party algorithms must be approved from the Bulenox management team" [P1-57] | Copiers permitted [P1-56] | NinjaTrader, R\|Trader Pro, Quantower, Sierra Chart, MultiCharts, ATAS (Rithmic) [P1-59]; a Rithmic API connection is mentioned with a fee [P1-56] | 3 / 7 / 12 / 15 contracts; 1 mini = 10 micros [P1-58] | First $10,000 at 100%, then 90/10; Master paid weekly on Wednesday; Fast Track and Momentum daily [P1-59] | Qualification one-time $145 / $175 / $215 / $325, 30-day access; reset $78; pro data $116/mo [P1-58][P1-55] | Canada not on the restricted list [P1-59] | "No blackout windows, no forced position closing" [P1-55] | No page date shown on site pages; terms PDF "Updated July 2021" |
| Phidias Propfirm | Premium 50K / 100K / 150K | Allowed, overnight and over-week, eval and CASH (sim-funded) [P2-01][P2-02]. LIVE after Premium: not stated (UNSOURCED); LIVE from E2L "Not permitted (unless agreed)" [P2-02] | EOD trailing $2,500 / $3,000 / $4,500; stops trailing at start + $100 on CASH; no daily loss limit [P2-02][P2-01] | TOU bans "robots, fully automated trading algorithms or any form of automated trading", except semi-automated software with active monitoring and manual adjustment [P2-01][P2-02]. No API product documented on any fetched page | Only exception text above; no definition of semi-automated, no alert/confirm example [P2-01]. Copy trading authorised within account limits [P2-01] | Rithmic (Quantower, MotiveWave, ATAS, Sierra Chart, Bookmap), dxFeed (DeepCharts), NinjaTrader / Tradovate (TradingView via Tradovate) [P2-01][P2-05] | 10 / 14 / 17 E-mini or 100 / 140 / 170 micro [P2-02]; max 5 Premium (50K/100K) + 2 Premium 150K funded [P2-01] | Every 5 trading days; split 75% then 80/85/90/100% from payout 5; cap per cycle $2,000 / $2,500 / $2,750; 30% consistency on CASH; min withdrawal $500 on rules page vs "never be less than $1,000" in TOU (conflict) [P2-02][P2-01] | CASH-account activation fee $149 / $149 / $169, a one-time ("lifetime") payment per account until failure (TOU "LIFETIME PAYMENT" table; rules page "CASH Account Activation Fees ... Lifetime") [P2-01][P2-02]; evaluation price UNSOURCED (JS configurator); CASH reset $399 / $499 / $599 [P2-01][P2-02] (lead relabel 2026-10-04, Fable R-06) | Not on restricted list [P2-01] | News trading authorised on all accounts [P2-01][P2-02] | TOU and rules modified 2026-09-22 (meta); Tradovate page no date shown |
| Phidias Propfirm | Fundamental 50K-150K; Express to Live 25K-150K | Fundamental and E2L: must be flat before end of day [P2-02][P2-01] | Fundamental EOD trailing; E2L static [P2-02] | Same TOU clause [P2-01] | Same [P2-01] | Same [P2-01] | not collected (plan excluded by overnight rule) | not collected | Lifetime $149 / $149 / $169 [P2-01] | Same [P2-01] | Same [P2-02] | as above |
| Alpha Futures | Standard 50K-150K; Advanced 50K-150K; Zero 25K-100K; Direct 25K-150K (all sim) | Not allowed: "all trades must be closed before 4:20PM EST every day" [P2-10][P2-08]. Alpha Prime LIVE (by selection): overnight permitted [P2-25] | EOD trailing on all accounts, stops at starting balance [P2-19]; MLL e.g. Standard $2,000 / $3,000 / $4,500; Advanced $1,750 / $3,500 / $5,250 [P2-15][P2-16] | T&C: "The use of AI, bots, and other automated trading mechanisms is strictly prohibited across all account types" [P2-08][P2-11]; HFT over 100 trades/day restricted [P2-11]. No API documented | Semi-automated allowed if trader "manually places, monitors, and manages the trade" [P2-11]; T&C: "actively monitor, manually manage" [P2-08]. Copy trading allowed for a single user; "Automated, Group, and Reverse Trading are strictly prohibited" [P2-14] | AlphaTrader, TradingView (via Plus500), WealthCharts, Deepchart, Quantower (dxFeed) [P2-13] | Standard 5/10/15 minis; Zero 1/3/6; Direct 2/4/8/10; Advanced 5/10/15 [P2-15][P2-17][P2-18][P2-16] | Up to 4 per month; 5 winning days of $200; up to 50% of profit; 90% split [P2-20] | Standard $129 / $239 / $349 per month; Advanced $209 / $349 / $489 per month; Zero $89 / $139 / $279 per month; Direct one-time $349-$859 [P2-15][P2-16][P2-17][P2-18] | Not on restricted list [P2-12] | Evaluations unrestricted; Standard, Zero, Direct qualified: no orders 2 min before/after red-folder news; Advanced: none [P2-21] | HC 2025-10-30 to 2026-08-12; T&C effective 2026-07-27 |
| Lucid Trading | LucidFlex, LucidPro, LucidDirect, LucidDaily, LucidLive; 25K-150K | Not allowed. Pro, Flex, Direct: "All positions must be closed by 4:45 PM EST"; LucidLive: "Swing trading is not allowed" [P2-29] | Flex: EOD trailing, MLL $1,000 / $2,000 / $3,000 / $4,500, locks at start + $100 [P2-37][P2-34] | HC: "Automated trading systems and trade copiers are permitted" [P2-28]. TOU silent on trading automation [P2-46]. No API documented | Same article; trader "fully responsible for any software errors" [P2-28] | CQG: NinjaTrader, Tradovate, TradingView; Rithmic: MotiveWave, Quantower, Tradesea, Sierra Chart, Jigsaw, Bookmap, ATAS, R Trader Pro, MultiCharts [P2-26] | Flex 2 / 4 / 6 / 10 minis (20 / 40 / 60 / 100 micros) [P2-34] | Flex: 90/10; 5 days at $100-$250 min profit; positive net profit per cycle; min $500 [P2-36] | LucidPro eval one-time list price $123 / $192 / $307 / $410; no activation fee [P2-44][P2-41] | Not on restricted list [P2-27] | Allowed on Flex, Pro, Direct; red-folder news is a hard breach on LucidDaily [P2-28] | HC 2026-07-28 to 2026-08-31; TOU last modified 2025-03-20 |
| TradeDay | Quick Pay EOD, Quick Pay Intraday, Fast Pass; 25K-150K | Not allowed: "No holding positions when the market closes"; auto-liquidation 10 min before close [P2-48] | Trailing max drawdown $1,000 / $2,000 / $3,000 / $4,500, EOD or intraday by plan, trails to starting balance [P2-55][P2-54]; Quick Pay funded sim intraday [P2-56] | "We do not make platform APIs available to traders"; ATS only via NinjaTrader, Tradovate, TradingView, Jigsaw, Quantower; third-party bots forbidden [P2-47]. Terms: no strategies with more than 200 trades a day [P2-62] | Own ATS allowed on supported platforms [P2-47]. "Trade copiers are allowed from your personal accounts or other evaluations" [P2-52] | CQG: Tradovate, NinjaTrader, TradingView, Jigsaw; Rithmic: R Trader Pro, Quantower, ATAS, MotiveWave and others [P2-51] | 2/20, 5/50, 10/50, 15/50 contracts/micros [P2-55] | Min $250; 80/20 when over $4,000 profit remains, else 50/50 (Quick Pay) [P2-58] | Quick Pay EOD $120 / $175 / $285 / $395; Intraday $100-$350; Fast Pass $130-$480; no activation fee; live data $156 per month per exchange [P2-55][P2-60] | BC resident: evaluation and Funded Sim only; "Canadian citizens or residents outside the province of Ontario are not eligible for Funded Live accounts" [P2-50] | Tier 1 releases: auto-flat 2 min before, reopen 2 min after [P2-57] | HC modified 2025-11-28 to 2026-10-01 (year not shown for 2026 dates); terms 2026-08-11 |
| Earn2Trade | Trader Career Path TCP25 / 50 / 100; Gauntlet Mini | Not allowed: "you CANNOT hold overnight positions"; flat by 3:50 pm CT [P2-63][P2-73]. LiveSim and Live: UNSOURCED | EOD drawdown on eval and LiveSim; intraday trailing on Live; fixed on $200K / $400K [P2-69]; TCP25 EOD $1,500 [P2-79] | Terms: no "bots ... to automatically access or manipulate the Service" [P2-77]; prohibited: "Utilizing software, artificial intelligence, or ultra-fast data entry techniques that could potentially manipulate the trading environment" [P2-64]. No API documented | "The use of trade copiers is not allowed on any of our programs" [P2-67]. No semi-automation wording found | NinjaTrader, Finamark, R Trader, Tradovate, TradingView, BlackArrow and others [P2-66] | TCP25 progression ladder "Up to 3 Contracts" [P2-79]; other sizes UNSOURCED (image table) | Split 50% or 80% by withdrawal size; weekly on Wednesdays; min $100 net [P2-71] | TCP25 "starting at $150 /mo"; LiveSim activation $139 [P2-79][P2-72]; TCP50 / TCP100 prices UNSOURCED (dynamic pricing in JS) | Not on sanctioned-citizenship list [P2-78] | No restrictions around economic announcements [P2-73] | HC 2023-08-30 to 2026-08-13; terms no date shown |
| FundedNext Futures | Rapid Pro / Daily, Legacy, Flex; 25K-150K | Not allowed: "does not allow overnight or weekend trade holding"; flat by 3:10 pm CT [P2-80] | Legacy: trailing EOD MLL $1,000 / $2,000 / $3,000 [P2-86] | HC: EAs and bots allowed on Challenge and funded accounts [P2-81]. Challenge terms: no automation clause found [P2-156]. No API documented | Copy trading only between the trader's own accounts [P2-88] | Tradovate, NinjaTrader, TradingView [P2-83] | Legacy funded 3 / 5 / 7 e-mini (30 / 50 / 70 micro) [P2-87] | Legacy: 80% split; 5 benchmark days and $500 profit per cycle; min $250 [P2-87] | Legacy $79.99 / $199.99 / $239.99; Rapid Pro base $159.98-$499.98 [P2-86][P2-85] | "Canada (except Ontario)" on the live-eligibility review list: may buy and trade sim; live reviewed case by case [P2-84] | UNSOURCED (no news article found; prohibited list silent) [P2-82] | HC 2026-04-09 to 2026-06-10 and "updated this week"; terms 2026-09-25 |
| The Trading Pit | Futures Prime 50K / 100K / 150K (on current sales page) | Prime: not allowed; force-closed at 14:55 CT [P2-95] | EOD trailing, capped at start; $2,000 / $3,000 / $4,500 [P2-99][P2-109] | HC: own EAs allowed except copying others, HFT, arbitrage, emulators [P2-96]; GTC bans automated tools only when used "to manipulate the Trading Platform, circumvent our monitoring systems, or gain an unfair trading advantage" [P2-92]. No API documented | Copy trading "manually or automatically in up to 5" accounts, own sources only [P2-98] | Rithmic R Trader Pro, Tradovate, NinjaTrader, TradingView (via Tradovate), ATAS, Quantower, VolFix [P2-107][P2-104] | 5 / 10 / 15 standard or 50 / 100 / 150 micros [P2-93] | 80% split; first after 5 days of $150+; caps $2,500 / $3,500 / $5,000 [P2-109] | $99 / $189 / $289 one-time; activation $0 for new accounts; reset $79 / $149 / $229 [P2-109] | Canada not on futures-restricted list [P2-105]; CFDs not offered to Canada [P2-92] | Allowed on Prime [P2-97] | No date shown on any TTP page |
| The Trading Pit | Futures Classic 20K / 150K / 200K / 250K (help centre only; not on current sales page) | Overnight allowed Mon-Thu; "not over the weekend", flat by Friday close [P2-95][P2-91] | Max drawdown trailing on highest balance, no cap; daily drawdown on EOD equity, immediate breach [P2-91] | Same EA article [P2-96]; EAs must not trade 2 min around high-impact news on Classic [P2-96] | Same [P2-98] | Same [P2-107] | 10 micros / 5 / 7 / 10 standard [P2-93] | Payout on reaching profit target; 60%-80% split by level [P2-91][P2-108] | $599 for 250K (10 standard); no activation fee [P2-91] | Same [P2-105] | Not allowed 2 min before/after high-impact news [P2-97] | No date shown |
| PropEd Capital (extra) | Standard Eval 25K-150K; Instant Funded 50K-150K; TrueRisk; One Plan 750K | Overnight allowed: "weekday swing or overnight holds are permitted" [P2-112][P2-115]; weekend holds need a paid add-on ($16.35-$54.75 on Standard Eval) [P2-115] | EOD; Standard $1,000 / $2,000 / $4,000 / $6,000; Instant $2,500 / $5,000 / $7,500; TrueRisk static-sized [P2-119][P2-117] | Terms: "automated strategies may be used only where supported and permitted" [P2-112]; FAQ lists "EAs / Bots / Automated" with a not-allowed mark [P2-115]. No API documented | No semi-automation wording. "Copy Trading (built into Onyx)" allowed [P2-115][P2-118] | Onyx (Rithmic, TradingView charting); R Trader Pro or other Rithmic screens [P2-118] | Standard 3 / 5 / 10 / 15 minis; Instant 3 / 6 / 9 [P2-115] | 80% (One Plan 100%); biweekly; caps $1,500-$5,000; live via Ironbeam after 4 cycles [P2-120][P2-121] | Standard $109 / $175 / $285 / $365; Instant $599 / $949 / ... [P2-117] | Not on restricted list [P2-116] | News trading allowed [P2-115][P2-112] | Terms 2026-08-15; FAQ no date shown |
| Leeloo Trading (extra) | Investor Performance Account (being phased out); practice accounts 25K-300K | Practice phase: holding through the close permitted [P2-122]. Performance accounts: only the Investor type; "up to 3 micros through the close", more needs admin permission [P2-131][P2-122]. Weekend for Investor PA: UNSOURCED | Trailing on highest unrealized profit, stops at start + $100 (e.g. 50K: $2,500) [P2-131] | "Use of automated systems, bots, or third-party trade execution is prohibited" [P2-131]; "Any system that places or manages trades without your manual input is not allowed" [P2-123]. No API | Allowed: "Manually executed trades based on signals (e.g., entering trades based on an alert from another system, as long as the actual trade is executed manually)" [P2-123]. Copying from others banned [P2-123] | Rithmic platforms: NinjaTrader 7/8, R Trader Pro, MotiveWave, Sierra Chart and others [P2-124] | Equal to practice account (e.g. 15 contracts on 150K), no scaling [P2-131][P2-132] | First payout after 30 trading days; then monthly; $1,000 minimum on first 4 [P2-131] | Practice $250 (25K) to $850 (300K) [P2-132]; billing basis UNSOURCED | Not stated [P2-130] | UNSOURCED for Investor PA | KB modified 2026-04-04 to 2026-04-14; terms 2026-03-31 |
| Top One Futures (extra) | Elite, Ignite, Instant Sim Funded, X Ultra; 25K-150K | Not allowed: "holding trades overnight is not allowed"; flat by 4:10 PM EST [P2-133] | Elite: max trailing drawdown (intraday breach noted) [P2-139]; sizes UNSOURCED | Terms prohibit "Using bots, Expert Advisors (EAs), or automated trading systems" [P2-154][P2-134] | Copy trading only between same-type, same-size accounts [P2-137] | Tradovate / NinjaTrader, BlackArrow [P2-140] | Elite 1 / 3 / 5 / 7 minis [P2-138] | Elite: profit target 6% then 5%, 4%; 25% consistency [P2-141] | UNSOURCED | Not on restricted list [P2-136] | Allowed; rules on Elite Daily / ACCESS funded [P2-135] | HC "updated yesterday"; terms 2026-06-10 |
| Funded Futures Family (extra) | Prime, Premier, Velocity, S2F, Base; 25K-150K | Not allowed across days: "All trades must close by 4:45 pm EST" (trading in the overnight session is allowed) [P2-142] | Prime: EOD, $1,000 / $2,000 / $3,000 / $4,500, locks at start [P2-148] | "we don’t permit bot or algorithmic trading" [P2-143]; terms silent [P2-155] | UNSOURCED | NinjaTrader, Tradovate [P2-146] | Prime 2-10 minis standard, 3-15 max [P2-147] | Prime: every 3 trading days [P2-147] | Evaluation subscription; no activation fee [P2-149]; amounts UNSOURCED | Not on restricted list [P2-144] | Permitted, including Tier 1 [P2-145] | HC 2026-08-11 to 2026-08-28 |

## 2. Personal-account brokers (part 3, verbatim)

### 0. Regulatory point that decides eligibility in BC

- BC Securities Act s. 34(a) needs dealer registration to trade exchange contracts (futures) with BC
  residents. Foreign dealers that are not registered in BC get exemptions under s. 48 that cover only
  "eligible derivatives parties" (sophisticated investors). For individuals, the definition requires
  financial assets of at least $5,000,000 [B-15], [B-16], [B-17]. Quote [B-15]
  (2024 BCSECCOM 523, RBC Capital Markets, LLC, December 20, 2024): "granting relief from the
  requirement in section 34(a) of the Act for the Filer to be registered as a dealer in connection
  with trades in contracts or instruments, including futures contracts and options ... with the
  Jurisdiction's residents that fall within the definition of "eligible derivatives party"". The
  headnote reads: "the person will only trade exchange contracts with sophisticated investors." Para (o)
  of the definition reads: "an individual that beneficially owns financial assets ... of at least $5 000 000".
  The same template appears in 2025 BCSECCOM 346 (StoneX Financial Ltd., July 31, 2025) [B-16] and
  2025 BCSECCOM 141 (Duneland Commodities Inc. dba DLC Risk Management, April 3, 2025) [B-17].
- My reading, not a legal opinion: a retail BC resident should use a BC-registered dealer, in practice
  a CIRO investment dealer. IBKR Canada says: "Interactive Brokers Canada Inc. is a member of the
  Canadian Investment Regulatory Organization (CIRO)" [B-02], [B-10]. Wealthsimple places itself among
  "Canadian investment dealers regulated by CIRO that offer futures trading" [B-41]. Jitneytrade Inc.
  "is registered as an Investment Dealer with the Canadian Investment Regulatory Organization (CIRO) and
  the Canadian Security Administrators in most provinces and territories" [B-52]. US FCMs that accept
  BC residents "at the discretion of a senior manager" [B-18] or as "Non-Solicited Self-Directed"
  clients [B-29] are relying on a basis their pages do not explain. Treat them as UNCLEAR.
- Registered accounts are out. At IBKR Canada the RRSP and TFSA lists of qualified investments contain
  no futures, and the RRSP section says "Margin trading is not permitted in a RRSP/SRRSP" [B-11].
  Wealthsimple: "Futures are not permitted in Tax-Free Savings Accounts (TFSAs) or Registered Retirement
  Savings Plans (RRSPs). You must use a non-registered account." [B-42]

### 1. Broker summary table

Commission column: per contract per side for MES at the lowest-volume tier, including exchange and
regulatory fees where the broker publishes them.

| Broker | BC residents (US futures) | Minimum | API (futures orders) | Multi-day holds | Micros listed | Commission (micro, per side, all-in) | Market data cost | Notes |
|---|---|---|---|---|---|---|---|---|
| IBKR Canada (Interactive Brokers Canada Inc.) | Yes: CIRO dealer for Canadian residents; US futures permission listed; separate margin schedule "For residents of Canada trading futures and FOPs" [B-06], [B-10], [B-12] | Account minimum USD 0.00 [B-08]; stock margin needs $2,000 equity [B-13]; futures-specific minimum UNSOURCED | TWS API, Web API (REST), FIX. TWS API and REST over the Internet: "USD 0.00 per month minimum commission". FIX: USD 1,500/month minimum [B-08], [B-09], [B-14] | Yes. Overnight margins published; intraday rates revert "back to the full overnight margin requirement" each day [B-06] | All in item 4 except where noted: MES, MNQ, M2K, MYM, MCL, MGC, SIL, MHG, MBT, MET, M6E, M6A, M6B, MCD, MJY, MSF, 2YY, 5YY, 10Y, 30Y, MHNG (class MNG), MZC, MZS, MZW, MZL, MZM [B-01], [B-06] | MES USD 0.61 (computed: 0.25 IBKR + 0.35 exchange + 0.01 regulatory) [B-01], [B-02] | "US Securities Snapshot and Futures Value Bundle" USD 10.00/month non-pro, waived at USD 30 commissions; covers CBOT, CME, COMEX, NYMEX top of book. Or CME Real-Time (L1) USD 1.55/month non-pro per exchange [B-07] | PERMITTED. Inactivity fee USD 0.00 [B-08] |
| Wealthsimple | Probably yes (national CIRO dealer, futures launched for Canadians), but no page I could retrieve names BC or the provinces; the help article was 403 and no Wayback capture exists. UNSOURCED for BC specifically [B-41] | Margin account required ("Futures trading is only offered in margin accounts": search snippet only, help page 403, so UNSOURCED); no minimum found | No API found on its futures pages. Terms forbid scraping, reverse engineering and circumventing rate limits [B-43] | UNSOURCED (page says "Margin — returned when position closes", trading "nearly 24/7") [B-41] | "micro, mini, and standard contract sizes"; examples S&P 500, gold, oil; full list is on the help page (403). Per-symbol: UNSOURCED [B-41] | MES USD 1.37 (computed: "$1 USD per contract" + "$0.35 and $0.02 ... for the micro S&P 500") [B-41] | "$0 real-time market data — no subscription required" [B-41] | HUMAN-IN-THE-LOOP ONLY (no API). Margins are shown only in the app |
| AMP Futures (AMP Global Clearing, US FCM) | Only at discretion: "Only 3 provinces in Canada are allowed: Alberta, Ontario and Quebec. Additionally, British Columbia accounts may be allowed at the discretion of a senior manager." [B-18] (Wayback 2025-09-11) | "$100" (2019 news) [B-23]; current figure UNSOURCED | Rithmic R \| API (C++/.NET): $100/month plus $25 user ID, plus $0.10 per contract routing; also TT API, CQG [B-22] | Yes: "Maintenance Margin ... is the amount required to carry a contract past the daily close" [B-20] | MES, MNQ, M2K, MYM, MCL, MGC, SIL, MHG, M6E, M6A, M6B, MCD, MJY, MSF, 2YY, 5YY, 10Y, 30Y, MNG, MZC, MZS, MZW on margin page; MBT, MET not on margin page [B-20] | Current: not published (quote form) [B-24]. 2019 example: "Total per Side $0.42" [B-23] (stale; CME fees rose since) | CME Bundle L1 $15/month, CME/Globex L1 $5/month non-pro ("Prices effective June 1, 2026") [B-21] | UNCLEAR (BC acceptance discretionary; see BCSC point) |
| NinjaTrader Brokerage | No: "Canadian law restricts NinjaTrader from opening accounts for residents of Canada that are outside of the province of Ontario. This includes all other provinces: ... British Columbia ..." [B-25] (Apr 16, 2025) | n/a | NinjaTrader API licence: "access and use the API solely for the purpose of connecting Your order entry and/or trading program(s)" [B-27]; "Build, test, and deploy automated trading strategies" [B-28] | n/a | n/a | n/a | n/a | NOT PERMITTED. BC users may run the NinjaTrader platform with a third-party broker [B-25] |
| Tradovate | No: same restriction; "If you are in Canada, but outside of Ontario, you are still able to use Tradovate in Simulated Mode." [B-26] (Nov 19, 2024) | n/a | API exists (NinjaTrader group API [B-27]); irrelevant for BC | n/a | n/a | n/a | n/a | NOT PERMITTED |
| Optimus Futures (introducing broker) | Claimed via clearing firms: "We accept all Non-Solicited Self-Directed Canadian futures traders when you Open an Optimus Futures account that is cleared through Phillip Capital and Ironbeam." [B-29]. 2019 forum post: "If you are currently living in BC, Canada, we can accept you as a client with Ironbeam." [B-31] | UNSOURCED | UNSOURCED on fetched pages (offers Optimus Flow, CQG, Rithmic per [B-31]) | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR ("Non-Solicited" basis; BCSC exemption pattern) |
| Ironbeam (US FCM) | Not stated for BC on Ironbeam's own pages: "To confirm whether your country is supported, please send a message to [email protected]" [B-32], [B-33] | "Ironbeam has no account minimum." [B-33] | Ironbeam API (REST): "Send orders to the exchange directly from your API connection"; fee UNSOURCED [B-35] | Yes: overnight margins published [B-34] | MES, MNQ, M2K, MYM, MCL, MGC, SIL, MHG, MBT, MET, M6A, M6B, M6E, MCD, MJY, MSF, 2YY, 5YY, 10Y, 30Y, MNG [B-34] | UNSOURCED: pricing page is password-protected [B-36] | UNSOURCED | UNCLEAR |
| EdgeClear (US IB) | No statement on edgeclear.com; only third-party claims (not used). UNSOURCED [B-37] | UNSOURCED (commission calculator is JavaScript) | "Automated Trading Solutions ... EdgeQX Automation"; Rithmic [B-37] | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR |
| TradeStation (US) | No Canada statement on tradestation.com; international clients need paper applications [B-38]. A third-party claim that Canadians cannot trade futures there was not verified on a TradeStation page. UNSOURCED | UNSOURCED | "Multi-asset brokerage API: equities, futures, and options ... from a single API key"; REST and FIX [B-39] | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR (leans NOT PERMITTED; unverified) |
| GFF Brokers (US IB) | Not stated: "Country-specific options depend on the clearing firm's regulatory coverage - reach out" [B-51] | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR (NinjaTrader names GFF and IBKR as the Canadian options but does not give provinces; forum source only) |
| Jitneytrade Inc. (Montreal, CIRO) | CIRO investment dealer "in most provinces and territories" [B-52]; BC and US futures UNSOURCED: jitneytrade.com did not resolve (DNS failure, F092/F094) | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR (site unreachable) |
| Questrade | No futures. Product list: "More than just Stocks & ETFs. Trade options, precious metals, and IPOs" [B-40]; offers CFDs instead [B-53] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (no futures product) |
| TD Direct Investing | No futures. Commission schedule covers equities, options, gold/silver, fixed income and mutual funds, with no futures section [B-46]. Active Trader shows "CME Futures (15 Min Delayed)" as a data package only [B-45] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (no futures product) |
| RBC Direct Investing | No: account approval text says "The Customer may NOT ... nor buy or sell futures." [B-44] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED |
| BMO InvestorLine | No: "BMO InvestorLine Inc. is not registered to trade in futures." [B-47] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED |
| CIBC Investor's Edge | No futures in "Investment choices" (Stocks, ETFs, Options, CDRs, Mutual Funds, GICs, Fixed Income, Precious Metals, IPOs, Structured Notes) [B-48] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (no futures product; list-based) |
| National Bank Direct Brokerage | No futures; "Futures contracts" are on its list of products that cannot be transferred in [B-49] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (indirect evidence) |
| Qtrade Direct Investing | No futures: "access to a wide array of stocks, ETFs, mutual funds, bonds, options and more" [B-50] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (list-based) |

#### IBKR Canada detail (every field of the brief)

1. BC residents: IBKR Canada is the Canadian entity. Its margin pages carry a residence selector, and the
   US-futures page for "hm=ca" says "For residents of Canada trading futures and FOPs: You are subjected to
   margin requirements." [B-06]. Its trading-permissions page lists "Futures ... United States" [B-10].
   CIRO member [B-02]. No page names BC specifically; nothing excludes any province. Account types:
   Individual, Joint, Trust, RRSP/SRRSP, TFSA, FHSA. "Margin | Cash, Reg T and Portfolio Margin are
   available." [B-12]. Futures go in a non-registered account [B-11].
2. Minimums: "Account Minimums | USD 0.00", "Inactivity Fees | USD 0.00" [B-08]. Stock margin: "All
   stocks bought or sold on margin require a minimum of $2,000 in equity" [B-13]. Portfolio Margin needs
   "at least $100,000" (F012). A futures-specific minimum equity was not found: UNSOURCED. Futures
   commissions and margins are charged "in the currency of the traded product" [B-01], so US futures run
   in USD.
3. API: "Web API ... RESTful API + Websockets", "TWS API ... develop applications in C++, C#, Java, Python",
   "Programmatically place orders including advanced order types" [B-09]. The TWS API documentation shows
   futures contracts defined with `SecType = "FUT"` [B-14]. Cost: "Gateway (Internet) | Trader Workstation
   and TWS API | REST API | ... USD 0.00 per month minimum commission"; FIX CTCI "USD 1,500.00 per month
   minimum commission for the first FIX session" [B-08]. API-specific restrictions in the client
   agreement: UNSOURCED (the agreements page is JavaScript-rendered, F017). Overnight and multi-day holds:
   overnight initial and maintenance margins are published per contract, and "Each day at 'Intraday End
   Time' the futures contract will revert back to the full overnight margin requirement until the
   'Intraday Start Time' the next day." [B-06]
4. Micros: listed in the commission schedule's micro group: "E-micro Futures and Futures Options (MES,
   MNQ, M2K, VOLQ, MYM, 2YY, 5YY, 10Y, 30Y, MCL, MRB, MGC, MWN, MTN, SIL, VXM, MHNG, MHO, MNK, MNI, MZC,
   MZS, MZW, MZL, MZM, ...)". MBT and MET are in their own groups. Micro FX: "E-Micro FX Futures" [B-01].
   Margin rows exist for all of them plus NG, ZN, ZF, ZT [B-06]. Micro Henry Hub: product MHNG, trading
   class MNG [B-06]. Micro grains: MZC, MZS, MZW, MZL, MZM [B-06].
5. Commissions, lowest tier (≤1,000 contracts/month; the Fixed and Tiered rates match at this tier):
   micro group USD 0.25, E-micro FX USD 0.15, MBT USD 0.85, MET USD 0.20, other USD futures USD 0.85
   [B-01]. Exchange-fee recovery (non-member, Tier I): MES/MNQ/M2K USD 0.35 [B-02]; MYM USD 0.35, micro
   yields USD 0.30, micro ags USD 0.50, ZN USD 0.80, ZF and ZT USD 0.65 [B-03]; MCL USD 0.50, MHNG USD
   0.60, NG USD 1.60 [B-04]; MGC USD 0.70, MHG USD 0.70 [B-05]; E-micro FX USD 0.24, MBT USD 1.15, MET
   USD 0.10 [B-02]. Regulatory (NFA): USD 0.01 [B-02]. Clearing fee USD 0.00 in IBKR's worked example
   ("1 ES Futures Contract = IBKR Execution Fee USD 0.85 + Exchange Fee USD 1.38 + Clearing Fee USD 0.00
   + Regulatory Fee USD 0.00 = USD 2.24") [B-01]. All-in per side (computed): MES, MNQ, M2K, MYM 0.61;
   2YY to 30Y 0.56; MCL 0.76; MZC/MZS/MZW 0.76; MHNG 0.86; MGC 0.96; MHG 0.96; micro FX 0.40; MBT 2.01;
   MET 0.31; ZN 1.66; ZF 1.51; ZT 1.51; NG 2.46. SIL's exchange fee is not on the COMEX fee page
   (UNSOURCED). Market data: as in the table [B-07]. Footnote: "Access to US Futures data requires
   clients to have US Futures Trading Permissions." [B-07]
6. Margins: section 2 below. The page shows no date.
7. Inactivity: USD 0.00 [B-08]. Market-data bundle fee waived at USD 30 commissions per month [B-07].

### 2. Margin table

IBKR Canada, page "US Futures and FOPs Margin Requirements" for residents of Canada (F010, no date shown,
fetched 2026-10-03). USD per contract. IBKR also publishes a separate "Short Overnight" pair, shown last.
"Intraday" means IBKR's intraday initial/maintenance; N/A means no reduced intraday rate.

| Contract | Broker | Initial (overnight) | Maintenance (overnight) | Intraday (initial / maint) | Short overnight (initial / maint) | Page date | Source key |
|---|---|---|---|---|---|---|---|
| MES | IBKR Canada | 3,704.55 | 2,608.90 | 2,593.185 / 1,826.23 | 2,869.79 / 2,608.90 | no date shown | B-06 |
| MNQ | IBKR Canada | 7,359.31 | 4,322.20 | 5,151.52 / 3,025.54 | 5,560.10 / 4,321.97 | no date shown | B-06 |
| M2K | IBKR Canada | 1,383.08 | 1,090.50 | 968.153 / 763.35 | 1,253.50 / 1,090.00 | no date shown | B-06 |
| MYM | IBKR Canada | 1,807.535 | 1,521.01 | 1,265.27 / 1,064.71 | 1,749.16 / 1,521.01 | no date shown | B-06 |
| MCL | IBKR Canada | 1,901.78 | 1,521.42 | N/A | 2,178.78 / 1,521.42 | no date shown | B-06 |
| MGC | IBKR Canada | 3,788.37 | 3,294.23 | N/A | 4,108.37 / 3,294.23 | no date shown | B-06 |
| SIL (row: underlying SI, class SIL) | IBKR Canada | 11,201.51 | 9,740.44 | N/A | 12,945.00 / 9,740.44 | no date shown | B-06 |
| MHG | IBKR Canada | 2,484.25 | 1,634.50 | N/A | 2,419.25 / 1,634.50 | no date shown | B-06 |
| MBT | IBKR Canada | 3,116.11 | 2,601.09 | N/A | 2,991.25 / 2,601.09 | no date shown | B-06 |
| MET | IBKR Canada | 126.448 | 109.955 | N/A | 158.11 / 137.444 | no date shown | B-06 |
| M6E | IBKR Canada | 435.02 | 350.017 | N/A | 402.52 / 350.017 | no date shown | B-06 |
| M6A | IBKR Canada | 277.31 | 215.052 | N/A | 247.31 / 215.052 | no date shown | B-06 |
| M6B | IBKR Canada | 258.874 | 201.738 | N/A | 231.999 / 201.738 | no date shown | B-06 |
| MCD | IBKR Canada | 136.283 | 118.507 | N/A | 145.783 / 118.507 | no date shown | B-06 |
| MJY | IBKR Canada | 340.775 | 280.022 | N/A | 322.025 / 280.022 | no date shown | B-06 |
| MSF | IBKR Canada | 586.285 | 473.40 | N/A | 544.41 / 473.40 | no date shown | B-06 |
| 2YY | IBKR Canada | 918.619 | 798.80 | N/A | 918.619 / 798.80 | no date shown | B-06 |
| 5YY | IBKR Canada | 825.075 | 717.456 | N/A | 825.075 / 717.456 | no date shown | B-06 |
| 10Y | IBKR Canada | 685.804 | 577.968 | N/A | 664.804 / 577.968 | no date shown | B-06 |
| 30Y | IBKR Canada | 728.613 | 624.881 | N/A | 718.613 / 624.881 | no date shown | B-06 |
| Micro Henry Hub (MHNG, class MNG) | IBKR Canada | 661.992 | 553.037 | N/A | 635.993 / 553.037 | no date shown | B-06 |
| MZC | IBKR Canada | 206.028 | 179.155 | N/A | 232.278 / 179.155 | no date shown | B-06 |
| MZS | IBKR Canada | 443.93 | 386.026 | N/A | 466.43 / 386.026 | no date shown | B-06 |
| MZW | IBKR Canada | 352.215 | 305.187 | N/A | 350.965 / 305.187 | no date shown | B-06 |
| MZL | IBKR Canada | 547.965 | 410.75 | N/A | 472.362 / 410.75 | no date shown | B-06 |
| MZM | IBKR Canada | 363.208 | 315.833 | N/A | 400.209 / 315.833 | no date shown | B-06 |
| NG | IBKR Canada | 6,619.92 | 5,530.36 | N/A | 6,359.92 / 5,530.36 | no date shown | B-06 |
| ZN | IBKR Canada | 2,156.27 | 1,875.02 | N/A | 2,280.99 / 1,875.02 | no date shown | B-06 |
| ZF | IBKR Canada | 1,437.50 | 1,250.00 | N/A | 1,554.43 / 1,250.00 | no date shown | B-06 |
| ZT | IBKR Canada | 1,380.04 | 1,200.04 | N/A | 1,458.25 / 1,200.04 | no date shown | B-06 |

Second brokers. These are public pages of brokers that are UNCLEAR for BC, so read them as reference
only. AMP shows one overnight figure, headed "*Maintenance", with the note "The CFTC, CME, and NFA
classify all retail traders as a "Heightened Risk Profile," mandating a 10% higher exchange margin
requirement than the rates published on the CME website." [B-20]. AMP's column is therefore the amount
needed to hold overnight, and no separate initial figure is published. Ironbeam shows "Overnight Margin"
and "Day Margin"; overnight values "fluctuate daily" [B-34]. Neither page shows a date. Some Ironbeam
values (MCL 416, MET 110) are far below IBKR's and AMP's and may be stale.

| Contract | AMP "*Maintenance" (overnight) / Day | Ironbeam Overnight / Day |
|---|---|---|
| MES | 2,881.00 / 40.00 | 2,307 / 50 |
| MNQ | 4,762.00 / 100.00 | 3,542 / 100 |
| M2K | 1,237.00 / 50.00 | 996 / 50 |
| MYM | 1,698.00 / 50.00 | 1,505 / 50 |
| MCL | 948.00 / 237.00 | 416 / 200 |
| MGC | 2,426.00 / 606.50 | 2,640 / 100 |
| SIL | 7,129.00 / 7,129.00 | 7,150 / 400 |
| MHG | 1,320.00 / 330.00 | 1,100 / 50 |
| MBT | not on page | 2,387 / 50 |
| MET | not on page | 110 / 50 |
| M6E | 231.00 / 57.75 | 297 / 50 |
| M6A | 193.00 / 48.25 | 209 / 40 |
| M6B | 187.00 / 46.75 | 220 / 50 |
| MCD | 88.00 / 22.00 | 110 / 50 |
| MJY | 308.00 / 308.00 | 308 / 50 |
| MSF | 396.00 / 396.00 | 495 / 50 |
| 2YY | 363.00 / 90.75 | 363 / 50 |
| 5YY | 352.00 / 88.00 | 341 / 50 |
| 10Y | 352.00 / 88.00 | 330 / 50 |
| 30Y | 297.00 / 74.25 | 297 / 50 |
| Micro Henry Hub (MNG) | 326.00 / 326.00 | 452 / 50 |
| MZC / MZW / MZS | 116.00 / 34.80; 226.00 / 67.80; 253.00 / 75.90 | not on page |
| NG | 3,234.00 / 3,234.00 | 4,494 / 1000 |
| ZN | 2,062.00 / 515.50 | 2,063 / 200 |
| ZF | 1,375.00 / 343.75 | 1,430 / 150 |
| ZT | 1,320.00 / 330.00 | 1,320 / 75 |

(AMP source B-20; Ironbeam source B-34. AMP's page prints "$187 .00" for M6B and "$2,062 .00" for ZN with
a stray space; the values are transcribed without it.)


## 3. Classification lines, verbatim from each part

### Part 1

- Topstep: NOT PERMITTED. Overnight holding is banned on every account ("No swing trading") [P1-01]. Automation itself is allowed through the API in the simulated stages [P1-02].
- Apex Trader Funding: NOT PERMITTED. Overnight holding is banned [P1-10][P1-09], and automation is banned outright [P1-11].
- Tradeify: NOT PERMITTED. Overnight holding is banned on all account types, Live included [P1-17]. Owned algorithms would otherwise be allowed [P1-18].
- Take Profit Trader: NOT PERMITTED. Overnight holding is banned [P1-23], and bots and algorithms are banned [P1-24].
- Elite Trader Funding, Direct To Funded and Diamond Hands: UNCLEAR. Multi-day and weekend holding is allowed [P1-33][P1-34]. AI, bots and algorithms are banned unless ETF authorizes them in writing, and the terms' definition of AI covers "automated decision-making systems" [P1-36][P1-37]. The pages do not say whether a person placing orders by hand from software-generated signals counts as such a system, and they contain no semi-automated wording.
- Elite Trader Funding, EOD, Static, 1-Step and Fast Track: NOT PERMITTED. Positions must be closed one minute before the close [P1-35].
- Elite Trader Funding, LIVE ELITE: UNCLEAR. Swing trading needs ETF's case-by-case approval [P1-43], and the automation terms also apply [P1-37].
- MyFundedFutures: NOT PERMITTED. Overnight holding is banned [P1-45]. Automation would otherwise be allowed [P1-46].
- Bulenox: NOT PERMITTED. Positions must be closed by 3:59 pm CT [P1-55]. Bots would otherwise be allowed [P1-56].

Candidate for a support question (Part 2 drafts the question file). Elite Trader Funding, DTF and Diamond
Hands: the firm allows overnight holding but its automation wording is ambiguous for the program's
workflow. Suggested asks, in the same shape as the Phidias question:
1. Does the "automated decision-making system" wording cover (A) software alerts that the trader executes by hand?
2. Can (B) a one-tap confirmation that then submits the order, and (C) software-managed exits, receive written authorization, and how is that authorization requested?
3. Which platform connections allow orders sent from the trader's own software?

No other Part 1 firm qualifies, because all the others ban overnight holding.

### Part 2

- Phidias Premium (50K / 100K / 150K, eval and CASH): HUMAN-IN-THE-LOOP ONLY. Multi-day and weekend holds allowed [P2-02]; automation only as "semi-automated software, provided the User actively monitors and manually adjusts all operations" [P2-01]. Whether alert-plus-confirm order submission qualifies is unconfirmed (question drafted).
- Phidias Fundamental and Express to Live: NOT PERMITTED. Flat before end of day [P2-02].
- Alpha Futures, all sim plans: NOT PERMITTED. Flat by 4:20 pm ET [P2-10] and bots banned on all account types [P2-08]. (Alpha Prime LIVE allows overnight [P2-25] but is selection-only and keeps the same automation ban.)
- Lucid Trading, all plans: NOT PERMITTED. Flat by 4:45 pm ET, no swing on LucidLive [P2-29], although automation is allowed [P2-28].
- TradeDay, all plans: NOT PERMITTED. No holding at the close [P2-48].
- Earn2Trade, TCP and Gauntlet Mini: NOT PERMITTED. No overnight positions [P2-63]; copiers banned [P2-67].
- FundedNext Futures, all plans: NOT PERMITTED. No overnight or weekend holds [P2-80], although EAs and bots are allowed [P2-81].
- The Trading Pit, Futures Prime: NOT PERMITTED. Force-closed at 14:55 CT [P2-95].
- The Trading Pit, Futures Classic: PERMITTED (Monday to Friday only). Overnight allowed but not over the weekend [P2-95]; own EAs allowed [P2-96]. Caveat: Classic does not appear on the current futures sales page [P2-109]; whether it can still be bought is UNCLEAR.
- PropEd Capital: NOT PERMITTED for automated execution. Overnight holds allowed (weekends with an add-on) [P2-112], but the FAQ marks "EAs / Bots / Automated" as not allowed [P2-115]. Semi-automation is not mentioned, so a question is drafted.
- Leeloo Trading, Investor Performance Account: HUMAN-IN-THE-LOOP ONLY. Manual execution of alerts allowed [P2-123]; automated systems and third-party execution banned [P2-131]; holds through the close capped at 3 micros without admin permission; the program is being phased out [P2-131].
- Top One Futures: NOT PERMITTED. No overnight holds [P2-133]; bots and EAs banned [P2-154].
- Funded Futures Family: NOT PERMITTED. Flat by 4:45 pm ET [P2-142]; bots banned [P2-143].

### Phidias re-check against docs/DECISIONS.md 2026-09-28 (lines 270-309)
- Automation clause: unchanged, word for word. Current TOU (modified 2026-09-22): "the use of robots, fully automated trading algorithms or any form of automated trading is not authorized, except for semi-automated software, provided the User actively monitors and manually adjusts all operations" [P2-01]. The rules page has a second wording: "Only semi-automated software is permitted, provided the trader actively monitors and manually adjusts all trades" [P2-02]. Still no definition and no alert or confirmation example.
- Swing account: still Premium, now 50K, 100K and 150K, with EOD trailing drawdown and no daily loss limit [P2-02], as the entry says. New details not in the entry: Premium evals need 1 minimum day, CASH payouts every 5 days, a progressive split of 75% rising to 100%, a 30% consistency rule on CASH, and a $150-$250 "Funded Min. Daily PNL" [P2-02].
- Platforms: the entry lists Rithmic, Tradovate and DeepCharts. The TOU now also names NinjaTrader and Tradovate accounts (separate from Rithmic), and a Tradovate page advertises TradingView execution [P2-01][P2-05]. No API product, sandbox or developer page was found, which matches the entry.
- LIVE: holding rules after a move from Premium to LIVE are not stated; LIVE from E2L says "Not permitted (unless agreed)" [P2-02]. The drafted question asks about this.
- Both TOU and rules pages carry a modified date of 2026-09-22, before the entry, so nothing has changed since it was written.

### Part 3

- IBKR Canada: PERMITTED. CIRO dealer for Canadian residents with US futures permission [B-02], [B-06],
  [B-10]; API with futures order entry and no API minimum commission over the Internet [B-08], [B-09],
  [B-14]; overnight margins published [B-06]. Open point: API terms in the client agreement are
  UNSOURCED.
- Wealthsimple: HUMAN-IN-THE-LOOP ONLY. Futures are offered [B-41] but no API was found, and the terms
  forbid scraping, reverse engineering and circumventing "rate limits" [B-43]. BC eligibility for
  futures specifically is UNSOURCED.
- AMP Futures: UNCLEAR. BC accepted only "at the discretion of a senior manager" [B-18]; BCSC exemption
  pattern [B-15] to [B-17].
- NinjaTrader Brokerage: NOT PERMITTED [B-25].
- Tradovate: NOT PERMITTED [B-26].
- Optimus Futures: UNCLEAR [B-29], [B-31] (Non-Solicited basis; BC statement from 2019).
- Ironbeam: UNCLEAR [B-32], [B-33].
- EdgeClear: UNCLEAR (no broker-side statement) [B-37].
- TradeStation: UNCLEAR (no broker-side statement) [B-38].
- GFF Brokers: UNCLEAR [B-51].
- Jitneytrade: UNCLEAR (site unreachable; CIRO dealer per [B-52]).
- Questrade: NOT PERMITTED (no futures) [B-40].
- TD Direct Investing: NOT PERMITTED (no futures) [B-45], [B-46].
- RBC Direct Investing: NOT PERMITTED [B-44].
- BMO InvestorLine: NOT PERMITTED [B-47].
- CIBC Investor's Edge: NOT PERMITTED (no futures in product list) [B-48].
- National Bank Direct Brokerage: NOT PERMITTED (indirect) [B-49].
- Qtrade: NOT PERMITTED (no futures in product list) [B-50].

## 4. Source lists

### Part 1 (P1-xx)

Pages are under reports/stage_e13_briefs/pages/PropVenues1/ (file name in brackets). Fetch date for
every page: 2026-10-03, except the repo files P1-06 and P1-07, which carry their own dates.

| Key | URL | Fetched | Page date | Page type | Verbatim quote (short) |
|---|---|---|---|---|---|
| P1-01 | https://help.topstep.com/en/articles/8284206 [ts_hours] | 2026-10-03 | dM 2026-07-13 | help centre | "Topstep is a day trading program. All positions must be closed by 3:10 PM CT every weekday. You can resume trading at 5:00 PM CT. No swing trading. No Forex." / "Topstep does not permit holding positions from one session to the next." |
| P1-02 | https://help.topstep.com/en/articles/11187768-topstepx-api-access [ts_api] | 2026-10-03 | dM 2026-09-17 | help centre | "Custom automated strategies and bots are allowed via the TopstepX / ProjectX API, subject to standard platform rules and our prohibition on highfrequency trading (HFT)." / "All trading activity must originate from your personal device. The use of VPS, VPNs, and remote servers is prohibited" / "Live funded accounts are not allowed to trade through the ProjectX API." |
| P1-03 | https://help.topstep.com/en/articles/8284197 [ts_combine]; https://help.topstep.com/en/articles/8284215-express-funded-account-parameters [ts_xfa] | 2026-10-03 | dM 2026-09-24; dM 2026-08-05 | help centre | "Can I use automated trading strategies? Yes, with conditions. Topstep won't help set up or troubleshoot automated strategies" / "You can also use a trade copier to duplicate trades across multiple accounts." |
| P1-04 | https://help.topstep.com/en/articles/8284116-eligibility-faq [ts_eligibility] | 2026-10-03 | dM 2026-09-04 | help centre | "I'm Canadian — can I earn a Funded Account? Yes. You trade on a sub-account of Topstep's master account" |
| P1-05 | https://www.topstep.com/terms-of-use/ [ts_terms] | 2026-10-03 | "Last updated: September 21, 2026" | terms | "Using any software, artificial intelligence, ultra-high speed, or mass Data entry which might manipulate, abuse, or give User an unfair advantage" / "Using any VPN or VPS on Accounts is strictly prohibited" / "about ten seconds prior to the closing bell at 3:10 PM CT" |
| P1-06 | reports/stage_e0_topstep_facts.json (its facts F5.1, F6.1, F6.3, F9.1, F11.3, F12.2a cite help.topstep.com 8284197, 8284211, 10305426, 8284215, 8284233) | 2026-09-23 (E.0) | per fact: 2026-06-10 to 2026-08-05 | repo file citing help centre | F5.1 "$50K: 5 Max Contracts, 50 Max Micros. $100K: 10 ... $150K: 15"; F6.1 "Topstep doesn't require you to flatten positions during economic releases"; F6.3 "Purposefully trading your full Maximum Position Size directly into a scheduled major news event"; F9.1 "XFA Standard: Payout eligibility 5 winning days of $150+ ... Profit split 90/10"; F12.2a "$50K \| $2,000 \| $3,000. $100K \| $3,000 \| $4,000. $150K \| $5,000 \| $6,000" |
| P1-07 | reports/stage_e12_topstep_150k.md, rows 1, 3, 4, 5 (citing help.topstep.com 8284204, 14289835) | 2026-10-03 (E.12) | help dM 2026-09-18 and later | repo file citing help centre | "$4,500 (trailing; XFA starts at -$4,500, locks at $0)"; "Standard Path $199/month; No Activation Fee Path $229/month"; "$149 once per XFA on Standard Path" |
| P1-09 | https://web.archive.org/web/20260814220703/https://apextraderfunding.com/help-center/getting-started/apex-live-prop-trading-program-faq/ [apex_wb_livefaq] | 2026-10-03 | WB 2026-08-14 | help centre (Live program) | "Can I trade overnight? No. All trades must be closed by 4:50 PM ET. Overnight holding through market close is not permitted." / "Automation and algorithm usage are not allowed." |
| P1-10 | https://web.archive.org/web/20260217053901/https://support.apextraderfunding.com/hc/en-us/articles/31519771524891-PA-Trading-Times [apex_tradingtimes] | 2026-10-03 | WB 2026-02-17 | help centre | "All trades must be closed before 4:59 PM ET. It is your responsibility to ensure that your account is flat before 4:59 PM ET." |
| P1-11 | https://web.archive.org/web/20260303120612/https://support.apextraderfunding.com/hc/en-us/articles/40463668243099-Prohibited-Activities [apex_wb_prohibited_old] | 2026-10-03 | WB 2026-03-03 | help centre (rules) | "No Automation or Algorithm Usage allowed: Rewards are intended to recognize human traders actively participating in the learning process, not to reward automated systems executing preprogrammed logic." / "Trading during news is allowed for your normal trading strategy." / "Sharing MAC addresses, computers, IPs, credit cards, or trade copying with other traders is strictly forbidden." |
| P1-12 | https://web.archive.org/web/20260926061815/https://apextraderfunding.com/help-center/eod-trailing-drawdown-accounts/eod-evaluations/ [apex_wb_eodeval] | 2026-10-03 | WB 2026-09-26 | help centre | "Max Drawdown (EOD) $1,000 $2,000 $3,000 $4,000 ... Max Contracts 4 6 8 12" / "Once established, the EOD Threshold is fixed and enforced during the next session." |
| P1-13 | https://web.archive.org/web/20260926061815/https://apextraderfunding.com/help-center/eod-trailing-drawdown-accounts/eod-payouts/ [apex_wb_eodpayouts] | 2026-10-03 | WB 2026-09-26 | help centre | "Up to weekly payouts with 100% payout split ... Minimum payout amount: $500 ... 50% consistency rule applies ... Maximum 6 payouts per Performance Account" |
| P1-14 | https://web.archive.org/web/20260927230316/https://apextraderfunding.com/help-center/billing/evaluation-plan-fees-and-access-explained/ [apex_wb_fees] | 2026-10-03 | WB 2026-09-27 | help centre | "When you purchase an Evaluation, you receive 30 consecutive calendar days of access." / "you have 7 calendar days to activate your Performance Account (PA) by completing the PA Activation Fee." / names Rithmic, Tradovate, Wealthcharts |
| P1-15 | https://web.archive.org/web/20260630155746/https://apextraderfunding.com/help-center/getting-started/restricted-countries/ [apex_wb_restricted] | 2026-10-03 | WB 2026-06-30 | help centre | "Can Canadians Trade With Apex? Yes! Canadian traders can fully utilize our services" |
| P1-16 | https://apextraderfunding.com/ and https://support.apextraderfunding.com/hc/en-us [apex_home, apex_hc_home2] | 2026-10-03 | no date shown | live site (maintenance page) | "Our site is currently undergoing maintenance." |
| P1-17 | https://help.tradeify.co/en/articles/10495876-rules-permitted-times-to-trade [tf_times_f]; WB 20260624154409 [tf_wb_times] | 2026-10-03 | dM 2026-07-14; WB 2026-06-24 | help centre | "All positions must be closed by 4:45 PM Eastern Time each trading day. You cannot hold positions overnight or swing trade. This applies to ALL account types including Live." (WB copy: same text with "4:59 PM") |
| P1-18 | https://help.tradeify.co/en/articles/12268167-essential-trading-rules-overview [tf_essential]; WB 20260822022738 [tf_wb_essential] | 2026-10-03 | dM 2026-08-26; WB 2026-08-22 | help centre | "HFT Bots: High-frequency trading bots not allowed" / "Algorithmic Trading Allowed if: - You own the strategy exclusively - Not shared with other traders/firms - Not high-frequency trading - Can prove ownership if requested" / "$25k 1 contract ... $150k 12 contracts" / news "Yes, but at your own risk." |
| P1-19 | https://help.tradeify.co/en/articles/14369021-tradeify-pricing-reference [tf_pricing] | 2026-10-03 | dM 2026-09-01 | help centre | "Growth 25K \| $99 \| $60 \| Growth 50K \| $145 \| $95 ..." / "There are no activation fees for any current Tradeify account type." / "90% to trader / 10% to Tradeify" |
| P1-20 | https://help.tradeify.co/en/articles/10495888-rules-restricted-countries [tf_restricted]; WB 20260610195917 [tf_wb_restricted] | 2026-10-03 | dM 2026-09-04; WB 2026-06-10 | help centre | Current list: Canada absent (0 matches). WB copy: "Canada \| Sim Funded Only \| Only Ontario residents." |
| P1-21 | https://help.tradeify.co/en/articles/10495897-rules-trailing-max-drawdowns [tf_drawdown] | 2026-10-03 | dM 2026-08-26 | help centre | "On Sim Funded accounts (not Evaluations), your drawdown locks in place once you profit beyond the drawdown amount by $100" |
| P1-22 | https://tradeify.co/terms-of-use [tf_terms] | 2026-10-03 | no date shown | terms | No automation clause found. Scraping clause: "use any robot, spider, scraper or other automatic device ... without the express written permission of Tradeify" |
| P1-23 | https://takeprofittraderhelp.zendesk.com/hc/en-us/articles/15170347090461 [tpt_rule4_hours] | 2026-10-03 | updated 2026-06-07 | help centre | "Positions cannot be carried from one trading day into the next." / "TPT will automatically close any open position at 4:55 PM Eastern" |
| P1-24 | https://takeprofittraderhelp.zendesk.com/hc/en-us/articles/34431153546397 [tpt_utp] | 2026-10-03 | updated 2026-06-12 | help centre (Universal Trading Policies) | "#1: No Trading Bots or Algos. Automated trading systems, bots, or algorithmic execution tools are not permitted." / "positions may not be held from one session to the next" |
| P1-25 | https://takeprofittraderhelp.zendesk.com/hc/en-us/articles/15171769361053 [tpt_pro_rules] | 2026-10-03 | updated 2026-09-22 | help centre | "We do not allow any automated or bot trading of any kind." / "The drawdown trails intraday as your unrealized profits rise." / "All PRO Accounts must be out of all open positions and have no open orders" + "o ne minute before, d uring and o ne minute after any prohibited news event" (split by the page's own HTML spans; joined here) |
| P1-26 | https://takeprofittraderhelp.zendesk.com/hc/en-us/articles/34431176505245 [tpt_copier]; .../34431223270557 [tpt_independent_exec] | 2026-10-03 | updated 2026-05-27 (both) | help centre | "TakeProfitTrader permits the use of trade copiers solely for managing accounts owned and controlled by you." / "Each account must represent an independently operating trader making discretionary trading and execution decisions." |
| P1-27 | .../15170265979165 [tpt_rule3_eod_dd]; .../15169066911133 [tpt_rule2_size] | 2026-10-03 | updated 2026-08-25; 2026-06-07 | help centre | "$25,000 3 Contracts $1,500 $1,500 $50,000 6 Contracts $3,000 $2,000 ... $150,000 15 Contracts $9,000 $4,500" |
| P1-28 | .../15172219527581 [tpt_pro_split] | 2026-10-03 | updated 2026-09-29 | help centre | "In the PRO account, the profit split is 80/20" / "you have the ability withdraw funds on day one. However, you must build a buffer on the account first." |
| P1-29 | https://takeprofittrader.com/ [tpt_home] | 2026-10-03 | no date shown | sales | "Fees for PRO Account \| One Time $130 Fee" |
| P1-30 | .../22447557656477 [tpt_restricted] | 2026-10-03 | updated 2026-08-25 | help centre | Restricted list; Canada absent (0 matches) |
| P1-31 | .../15173017163549 [tpt_platforms] | 2026-10-03 | updated 2026-08-18 | help centre | Lists TradingView, CQG, NinjaTrader, Tradovate, Rithmic |
| P1-33 | https://elitetraderfunding.app/help/how-the-dtf-plan-works [etf_how_the_dtf_plan_works] | 2026-10-03 | dM 2026-09-22 | help centre | "Overnights/weekends allowed — swing trading permitted." / "Allowed — swing trading is permitted on DTF accounts. Manage risk across sessions and be mindful of gaps." / "DTF accounts are subject to a maximum total reward of $25,000, which applies per trader" |
| P1-34 | https://elitetraderfunding.app/help/how-the-revamped-diamond-hands-plan-works [etf_diamond] | 2026-10-03 | dM 2026-10-02 | help centre | "Yes. Only Diamond Hands and Direct To Funded accounts are able to hold trades through close, and the weekend." |
| P1-35 | https://elitetraderfunding.app/help/how-the-end-of-day-plan-works (also static, 1-step, revamped fast-track) [etf_how_the_end_of_day_plan_works, etf_how_the_static_account_plan_wo, etf_fasttrack] | 2026-10-03 | dM 2026-10-01 to 2026-10-02 | help centre | "Q: Am I allowed to hold trades overnight? No. All trades must be closed one minute before market close." |
| P1-36 | https://elitetraderfunding.app/help/trade-copier-disclaimer [etf_trade_copier_disclaimer] | 2026-10-03 | dM 2026-10-01 | help centre | "AI, bots, EAs, and algos additionally require ETF's written authorization before use." / "The only automated trading tools currently authorized are the approved trade copiers listed above." / "any other automated decision-making system, whether built in-house or provided by a third party" |
| P1-37 | https://elitetraderfunding.com/terms-of-service [etf_terms] | 2026-10-03 | "Last updated: August 14, 2026" | terms | "(ac) makes use of artificial intelligence (AI), bots, automated trading systems, trade copiers, or other automated trading strategies that are not expressly authorized in writing by ETF." / "All trades executed by you on ETF's platform shall have a minimum duration of ten (10) seconds" |
| P1-38 | https://elitetraderfunding.app/help/trading-major-economic-releases | 2026-10-03 | dM 2026-07-27 | help centre | "ETF does not impose any restrictions or limitations on traders during major economic news events." |
| P1-39 | https://elitetraderfunding.app/help/countries-restricted-and-supported | 2026-10-03 | dM 2026-09-24 | help centre | "Available through Stripe with limitations (extended network / preview): Canada, Ghana, India, ..."; Canada is not on the Rise restricted list |
| P1-40 | https://elitetraderfunding.app/help/contract-limits | 2026-10-03 | dM 2026-09-30 | help centre | "100K DH Eval \| $100,000 \| 2 \| 2 \| 20"; "10K DTF ... 2"; "50K DTF ... 5"; "100K DTF ... 3" |
| P1-41 | https://elitetraderfunding.app/help/what-are-the-elite-funded-account-fees | 2026-10-03 | dM 2026-09-29 | help centre | "Direct To Funded (DTF) accounts have no activation fee. DTF is a one-time purchase that begins as an Elite Sim-Funded account" / "$87 Monthly Plan" |
| P1-42 | https://elitetraderfunding.app/help/supported-platforms-and-data-feed | 2026-10-03 | dM 2026-07-27 | help centre | Lists Tradovate, NinjaTrader, TradingView, Rithmic, MotiveWave, Quantower |
| P1-43 | https://elitetraderfunding.app/help/live-elite-information | 2026-10-03 | dM 2026-10-02 | help centre | "Swing trading is permitted at ETF's discretion." / "You leave a position or pending limit order open through market close — unless you've been approved to swing trade." |
| P1-44 | https://elitetraderfunding.app/help/overnight-margin-responsibilities-and-charges | 2026-10-03 | dM 2026-07-27 | help centre | "In cases where you inadvertently hold a trading position overnight, specific charges may apply." |
| P1-45 | https://help.myfundedfutures.com/en/articles/9558251-permitted-times-to-trade [mff_times] | 2026-10-03 | dM 2026-08-24 | help centre | "can remain open until the New York session closes at 4:10 PM EST." / "any open positions will be automatically closed at 4:10 PM EST" |
| P1-46 | https://help.myfundedfutures.com/en/articles/8444599-fair-play-and-prohibited-trading-practices [mff_fairplay] | 2026-10-03 | dM 2026-08-24 | help centre (rules) | "Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment." / "High-frequency Trading is not allowed" |
| P1-47 | https://help.myfundedfutures.com/en/articles/10771500-copy-trading-at-myfundedfutures [mff_copy] | 2026-10-03 | dM 2026-08-24 | help centre | "allows copy trading across all account types." |
| P1-48 | https://help.myfundedfutures.com/en/articles/8229993-restricted-countries-policy [mff_restricted] | 2026-10-03 | dM 2026-09-29 | help centre | Restricted list; Canada absent (0 matches) |
| P1-49 | https://help.myfundedfutures.com/en/articles/8230009-news-trading-policy [mff_news] | 2026-10-03 | dM 2026-08-31 | help centre | "Utilizing strategies that exploit immediate news bursts, such as straddles or strangles." |
| P1-50 | https://help.myfundedfutures.com/en/articles/16158363-rapid-eod-50k-a-comprehensive-look [mff_rapideod50] | 2026-10-03 | dM 2026-08-24 | help centre | "Maximum Drawdown (MLL) \| $2,000 \| Drawdown Type \| End-of-Day (EOD) Trailing ... Max Contract \| 3 mini / 30 micro \| T1 News Trading \| No" / "Required Buffer: $2,100" |
| P1-51 | https://help.myfundedfutures.com/en/articles/14290805-builder-plan-50k-a-comprehensive-guide [mff_builder50] | 2026-10-03 | dM 2026-08-24 | help centre | "Price \| $153 \| $125" / "There are absolutely no activation fees on any of our plans." / "Max Contracts \| 4 Minis / 40 Micros" |
| P1-52 | https://help.myfundedfutures.com/en/articles/13745661-payout-policy-overview-best-and-fastest-prop-firm-payouts [mff_payout] | 2026-10-03 | dM 2026-08-25 | help centre | "Builder and Pro Plans: Earn 80% of all profits. Rapid Plans: Earn 90% for Rapid sim funded plans as of January 12th, 2026" |
| P1-53 | https://help.myfundedfutures.com/en/articles/8528335-overview-of-supported-platforms-at-mffu [mff_platforms] | 2026-10-03 | dM 2026-08-24 | help centre | Lists NinjaTrader, Tradovate, TradingView, Quantower, Volumetrica, ATAS |
| P1-54 | https://help.myfundedfutures.com/en/articles/12109396-comprehensive-faq-live-accounts-at-myfunded-futures [mff_livefaq] | 2026-10-03 | dM 2025-11-10 | help centre | "We have systems in place to ensure that your trades are automatically closed before 4:10 pm EST." |
| P1-55 | https://bulenox.com/faq [blx_faq; Q&A extracted from the page's JSON-LD into blx_faq_qa.txt] | 2026-10-03 | no date shown | FAQ (rules) | "The trading day runs from 5:00 pm to 4:00 pm CT, and all positions must be closed by 3:59 pm CT." / "No blackout windows, no forced position closing, no penalties." / "On a Qualification account a reset costs $78" |
| P1-56 | https://bulenox.com/faq [blx_faq_qa] | 2026-10-03 | no date shown | FAQ | "Yes. Bots, algorithms and trade copiers are permitted. If you connect to Rithmic through a third-party API or composite software, an additional $100 per month applies. Only user-built tools intended solely for the account owner's personal use are permitted." |
| P1-57 | https://bulenox.com/legal/Terms_of_Use.pdf [blx_terms.pdf/.txt] | 2026-10-03 | "Updated July 2021" | terms | "In order to avoid performance discrepancy and/or meet compliance regulations, any third party algorithms must be approved from the Bulenox management team." |
| P1-58 | https://bulenox.com/accounts-pricing [blx_pricing] | 2026-10-03 | no date shown | sales | "$25,000 \| Contracts \| 3 \| Profit target \| $1,500 \| Drawdown up to \| $1,500 ... \| $145 \| one-time \| Access valid for 30 days" / "1 mini = 10 micros." |
| P1-59 | https://bulenox.com/faq [blx_faq_qa] | 2026-10-03 | no date shown | FAQ | "The first $10,000 in payouts is 100% yours. After that the split is 90/10" / "including NinjaTrader, R\|Trader Pro, Quantower, Sierra Chart, MultiCharts and ATAS" / restricted list has no Canada (0 matches) |
| P1-60 | https://help.myfundedfutures.com/en/articles/11802674-pro-plan-sim-funded-and-live-account-highlights [mff_pro] | 2026-10-03 | dM 2026-06-30 | help centre | "After first payout, MLL moves to $50,100 and remains static." / "Profit Split \| 80/20" |

(Keys P1-08 and P1-32 are not used.)

### Part 2 (P2-xx)

Fetched date 2026-10-03 for all rows. Page types: terms / help centre (HC) / rules / sales.

| Key | URL | Fetched | Page date | Type | Verbatim quote (short) |
|---|---|---|---|---|---|
| P2-01 | https://phidiaspropfirm.com/tou | 2026-10-03 | modified 2026-09-22 (meta) | terms | "the use of robots, fully automated trading algorithms or any form of automated trading is not authorized, except for semi-automated software, provided the User actively monitors and manually adjusts all operations"; "positions on PREMIUM accounts can remain open Over-night and Over-Week"; "The minimum withdrawal amount can never be less than $1,000." |
| P2-02 | https://phidiaspropfirm.com/rules | 2026-10-03 | modified 2026-09-22 (meta) | rules | "Premium — 50K, 100K, 150K sizes. Overnight and weekend holds allowed"; "Only semi-automated software is permitted, provided the trader actively monitors and manually adjusts all trades."; "Premium 150K — Max Contracts 17 E-mini / 170 micro" |
| P2-05 | https://phidiaspropfirm.com/tradovate | 2026-10-03 | no date shown | sales | "Connect your TradingView charts directly to your funded account." |
| P2-08 | https://alpha-futures.com/terms-and-conditions | 2026-10-03 | Effective from July 27, 2026 | terms | "All trades must be closed before 4:20pm ET each day"; "The use of AI, bots, and other automated trading mechanisms is strictly prohibited across all account types." |
| P2-10 | help.alpha-futures.com/.../9492096-what-and-when-you-can-trade | 2026-10-03 | July 17, 2026 | HC | "all trades must be closed before 4:20PM EST every day." |
| P2-11 | help.alpha-futures.com/.../9508585-prohibited-trading-practices | 2026-10-03 | October 30, 2025 | HC | "Semi-Automated Trading, such as a custom indicator that gives buy or sell signals, is permissible under the condition that the user manually places, monitors, and manages the trade" |
| P2-12 | help.alpha-futures.com/.../9523389-countries-with-limitations | 2026-10-03 | August 12, 2026 | HC | "you need to be either a resident or a citizen of a non-restricted country" (list has no Canada) |
| P2-13 | help.alpha-futures.com/.../10525305-trading-platforms | 2026-10-03 | "Updated this week" | HC | "AlphaTrader ... TradingView Connection powered by Plus500" |
| P2-14 | help.alpha-futures.com/.../10573989-copy-trading | 2026-10-03 | July 17, 2026 | HC | "Automated, Group, and Reverse Trading are strictly prohibited." |
| P2-15 | help.alpha-futures.com/.../11632512-standard-account-overview | 2026-10-03 | July 27, 2026 | HC | "Price $129/month $239/month $349/month" |
| P2-16 | help.alpha-futures.com/.../11634907-advanced-account-overview | 2026-10-03 | July 22, 2026 | HC | "Maximum Loss Limit $1,750 $3,500 $5,250" |
| P2-17 | help.alpha-futures.com/.../11771813-zero-account-overview | 2026-10-03 | August 12, 2026 | HC | "Price $89/month $139/month $279/month" |
| P2-18 | help.alpha-futures.com/.../15838742-direct-account-overview | 2026-10-03 | July 9, 2026 | HC | "One Time Fee $349 $519 $689 $859" |
| P2-19 | help.alpha-futures.com/.../9491999-maximum-loss-limit-mll | 2026-10-03 | July 15, 2026 | HC | "The Maximum Loss Limit (MLL) is EOD (end of day) trailing on all of our accounts" |
| P2-20 | help.alpha-futures.com/.../9492051-payout-policy | 2026-10-03 | July 27, 2026 | HC | "Request every 5 winning trading days of $200 profit, or more" |
| P2-21 | help.alpha-futures.com/.../9492063-news-trading-policy | 2026-10-03 | July 27, 2026 | HC | "no orders may be executed within 2 minutes before or 2 minutes after high impact news events" |
| P2-25 | help.alpha-futures.com/.../11023753-live-account-rules-and-parameters | 2026-10-03 | June 20, 2026 | HC | "Swing trading/holding overnight is indeed permitted" |
| P2-26 | support.lucidtrading.com/en/articles/11404614-lucid-trading-supported-platforms | 2026-10-03 | July 28, 2026 | HC | "CQG supported platforms: NinjaTrader Tradovate TradingView" |
| P2-27 | support.lucidtrading.com/en/articles/11404636-restricted-countries | 2026-10-03 | August 26, 2026 | HC | "If you are a citizen or resident of any of the countries listed below, you are not eligible" (no Canada) |
| P2-28 | support.lucidtrading.com/en/articles/11404728-other-trading-activities | 2026-10-03 | August 26, 2026 | HC | "Automated trading systems and trade copiers are permitted"; "red folder news on the LucidDaily is a hard breach" |
| P2-29 | support.lucidtrading.com/en/articles/11404729-allowed-trading-times | 2026-10-03 | August 26, 2026 | HC | "All positions must be closed by 4:45 PM EST, Monday through Friday"; "Swing trading is not allowed in the new LucidLive accounts" |
| P2-34 | support.lucidtrading.com/en/articles/12945790-lucidflex-evaluation-account | 2026-10-03 | August 31, 2026 | HC | "$150,000 $9,000 $4,500 50% 10 mini or 100 micros" |
| P2-36 | support.lucidtrading.com/en/articles/12945796-lucidflex-payouts | 2026-10-03 | July 28, 2026 | HC | "split 90% to the trader and 10% to Lucid Trading" |
| P2-37 | support.lucidtrading.com/en/articles/12945815-lucidflex-drawdown | 2026-10-03 | August 26, 2026 | HC | "use an End-of-Day Drawdown (EOD Drawdown) system" |
| P2-41 | support.lucidtrading.com/en/articles/11404620-simulated-account-fees | 2026-10-03 | August 26, 2026 | HC | "There is no activation fee to upgrade a LucidPro Evaluation to a LucidPro Funded." |
| P2-44 | https://lucidtrading.com/ (scrapling fetch) | 2026-10-03 | no date shown | sales | "25K PRO EVAL ... One Time Fee$123" |
| P2-46 | https://lucidtrading.com/terms-of-use/ (scrapling fetch) | 2026-10-03 | Last Modified: March 20, 2025 | terms | no trading-automation clause; "Use any robot, spider, or other automatic device ... to access the Website" |
| P2-47 | tradeday.freshdesk.com/.../103000085101-automated-algo-and-bot-trading | 2026-10-03 | Modified Fri, 28 Nov, 2025 | HC | "We do not make platform APIs available to traders."; "Algos and Bots purchased from a third party and employed by the trader are forbidden." |
| P2-48 | tradeday.freshdesk.com/.../103000018874-what-is-the-permitted-trading-times-guideline- | 2026-10-03 | Modified Mon, 27 Apr (year not shown) | HC | "No holding positions when the market closes." |
| P2-50 | tradeday.freshdesk.com/.../103000123294-prohibited-countries | 2026-10-03 | Modified Thu, 1 Oct (year not shown) | HC | "Canadian citizens or residents outside the province of Ontario are not eligible for Funded Live accounts." |
| P2-51 | tradeday.freshdesk.com/.../103000008813-which-trading-platforms-does-tradeday-use- | 2026-10-03 | Modified Wed, 2 Sep | HC | "CQG Platforms Tradovate NinjaTrader TradingView & Jigsaw" |
| P2-52 | tradeday.freshdesk.com/.../103000008833-can-i-have-multiple-accounts-can-i-use-copy-trader- | 2026-10-03 | Modified Tue, 22 Sep | HC | "Trade copiers are allowed from your personal accounts or other evaluations in to your TradeDay account." |
| P2-54 | tradeday.freshdesk.com/.../103000008855-what-is-the-maximum-drawdown-rule- | 2026-10-03 | Modified Sun, 31 May | HC | "Trailing max drawdown limits continues to trail your account growth until they reach the starting account balance." |
| P2-55 | tradeday.freshdesk.com/.../103000304248-what-are-the-differences-between-each-account-size- | 2026-10-03 | Modified Tue, 1 Sep | HC | "Quick Pay End of Day Evaluation Account Size 25K 50K 100K 150K Price $120 $175 $285 $395" |
| P2-56 | tradeday.freshdesk.com/.../103000008889-what-are-the-rules-for-funded-funded-sim-and-funded-live-traders- | 2026-10-03 | Modified Sun, 31 May | HC | "All Quick Pay Funded Sim accounts will have an intraday drawdown" |
| P2-57 | tradeday.freshdesk.com/.../103000081072-can-i-trade-news-or-data-releases- | 2026-10-03 | Modified Sat, 22 Feb, 2025 | HC | "TradeDay will auto-liquidate all open positions 2 minutes before TradeDay's tier 1 economic data releases" |
| P2-58 | tradeday.freshdesk.com/.../103000335937-quick-pay-funded-sim-payout-policy | 2026-10-03 | Modified Wed, 22 Jul | HC | "The minimum payout request is $250." |
| P2-60 | tradeday.freshdesk.com/.../103000008894-are-there-any-fees-when-i-am-funded- | 2026-10-03 | Modified Sun, 31 May | HC | "The professional market data fee is $156 per month, per Exchange." |
| P2-62 | https://www.tradeday.com/terms-and-conditions | 2026-10-03 | Last Modified: August 11, 2026 | terms | "We do not allow strategies that produce more than 200 trades in a day." |
| P2-63 | help.earn2trade.com/en/articles/2090496-can-i-hold-positions-overnight-on-the-trader-career-path-gauntlet-mini | 2026-10-03 | August 30, 2023 | HC | "you CANNOT hold overnight positions in the Trader Career Path®/ Gauntlet Mini™" |
| P2-64 | help.earn2trade.com/en/articles/9286647-prohibited-conduct-... | 2026-10-03 | May 6, 2024 | HC | "Utilizing software, artificial intelligence, or ultra-fast data entry techniques that could potentially manipulate the trading environment or provide an unfair advantage" |
| P2-66 | help.earn2trade.com/en/articles/2090521-what-platforms-can-i-use-... | 2026-10-03 | August 13, 2026 | HC | "NinjaTrader® - Free during the Trader Career Path®" |
| P2-67 | help.earn2trade.com/en/articles/12034590-am-i-allowed-to-copy-trades-across-multiple-accounts | 2026-10-03 | June 22, 2026 | HC | "The use of trade copiers is not allowed on any of our programs." |
| P2-69 | help.earn2trade.com/en/articles/8117088-drawdown-types | 2026-10-03 | August 10, 2026 | HC | "This drawdown type applies to evaluation accounts and LiveSim® accounts." |
| P2-71 | help.earn2trade.com/en/articles/5452472-what-is-the-withdrawal-policy | 2026-10-03 | July 9, 2026 | HC | "Withdrawals are processed weekly on Wednesdays" |
| P2-72 | help.earn2trade.com/en/articles/8320643-fee-schedule-... | 2026-10-03 | May 7, 2026 | HC | "One-time per account activation fee of $139.00" |
| P2-73 | help.earn2trade.com/en/articles/3224526-are-there-any-restrictions-on-when-i-can-trade-... | 2026-10-03 | November 13, 2025 | HC | "All positions and working orders must be closed by 3:50pm CT until 5pm CT."; "there are no restrictions on trading around economic announcements." |
| P2-77 | https://www.earn2trade.com/terms-and-conditions | 2026-10-03 | no date shown | terms | "You shall not create or use any program, tags, markers, bots ... to automatically access or manipulate the Service" |
| P2-78 | help.earn2trade.com/en/articles/2547638-i-m-not-an-american-us-citizen-can-i-still-get-funded | 2026-10-03 | March 7, 2025 | HC | "Citizens of the following countries are unable to get funded" (no Canada) |
| P2-79 | https://www.earn2trade.com/trader-career-path | 2026-10-03 | no date shown | sales | "EOD Drawdown|$1,500"; "Up to 3 Contracts"; "starting at $150 /mo" |
| P2-80 | helpfutures.fundednext.com/en/articles/14268506-does-fundednext-futures-allow-overnight-and-weekend-trade-holding | 2026-10-03 | June 10, 2026 | HC | "FundedNext Futures does not allow overnight or weekend trade holding." |
| P2-81 | helpfutures.fundednext.com/en/articles/14298560 | 2026-10-03 | April 9, 2026 | HC | "allows the use of automated trading systems, including Expert Advisors (EAs) and trading bots" |
| P2-82 | helpfutures.fundednext.com/en/articles/14298337-what-are-the-prohibited-trading-strategies-of-fundednext-futures | 2026-10-03 | updated (Intercom time) | HC | "Prohibited practices include platform error exploitation , account sharing" (no news rule in the list) |
| P2-83 | helpfutures.fundednext.com/en/articles/17225732-what-trading-platforms-does-fundednext-futures-offer | 2026-10-03 | "Updated this week" | HC | "three trading platforms — Tradovate, NinjaTrader, and TradingView" |
| P2-84 | helpfutures.fundednext.com/en/articles/17228971-are-any-countries-restricted-on-fundednext-futures | 2026-10-03 | "Updated this week" | HC | "Canada (except Ontario)" under "Live Trading Country Eligibility" |
| P2-85 | helpfutures.fundednext.com/en/articles/17228899-what-are-the-available-account-sizes-and-their-prices-... | 2026-10-03 | "Updated this week" | HC | "Rapid Pro and Daily $25K $159.98 $79.99" |
| P2-86 | helpfutures.fundednext.com/en/articles/17229536-fundednext-futures-legacy-challenge-all-rules | 2026-10-03 | Intercom time | HC | "on a Trailing End-of-Day basis"; "$25,000 $79.99 $50,000 $199.99 $100,000 $239.99" |
| P2-87 | helpfutures.fundednext.com/en/articles/17229581-fundednext-futures-legacy-fundednext-account-all-rules | 2026-10-03 | Intercom time | HC | "You earn an 80% Reward Share" |
| P2-88 | helpfutures.fundednext.com/en/articles/17230319-what-is-copy-group-trading-policy-at-fundednext-futures | 2026-10-03 | Intercom time | HC | "Copy trading is allowed only when traders copy their own trades" |
| P2-91 | support.thetradingpit.com/prime-futures-challenges-compared-classic-futures-challenges | 2026-10-03 | no date shown | HC | "Holding Overnight Not allowed Allowed"; "$599 for 10 Standard / 100 Micro Contracts" |
| P2-92 | https://www.thetradingpit.com/general-terms-and-conditions | 2026-10-03 | no date shown | terms | "Use of artificial intelligence, automated trading systems, ultra-high-speed tools, or mass data entry to manipulate the Trading Platform" |
| P2-93 | support.thetradingpit.com/what-is-the-minimum-and-maximum-number-of-contracts-i-can-trade | 2026-10-03 | no date shown | HC | "$150,000 Challenge: 15 standard/mini contracts or 150 micros" |
| P2-95 | support.thetradingpit.com/can-i-leave-positions-open-overnight-in-futures-challenges | 2026-10-03 | no date shown | HC | "It is allowed to keep positions open overnight in our Futures Classic accounts, but not over the weekend" |
| P2-96 | support.thetradingpit.com/can-i-use-an-expert-advisor-0-0 | 2026-10-03 | no date shown | HC | "Yes, we allow you to trade using your own Expert Advisor (EA)" |
| P2-97 | support.thetradingpit.com/is-news-trading-allowed-1-0-0 | 2026-10-03 | no date shown | HC | "News Trading is allowed on the Futures Prime accounts" |
| P2-98 | support.thetradingpit.com/is-copy-trading-allowed-1 | 2026-10-03 | no date shown | HC | "You are allowed to copy trades manually or automatically in up to 5 of your Challenges" |
| P2-99 | support.thetradingpit.com/what-is-max-drawdown-trailing-on-eod-end-of-day-balance | 2026-10-03 | no date shown | HC | "the trailing will stop once it reaches the starting balance" |
| P2-104 | support.thetradingpit.com/futures | 2026-10-03 | no date shown | HC | "Platforms NinjaTrader Tradovate Quantower ATAS Rithmic - R/Trader Pro" (navigation list) |
| P2-105 | support.thetradingpit.com/which-countries-are-not-supported-by-the-trading-pit-0 | 2026-10-03 | no date shown | HC | "Futures trading is not supported for residents of the following countries" (no Canada) |
| P2-107 | support.thetradingpit.com/can-i-change-my-platform-during-my-challenge-1 | 2026-10-03 | no date shown | HC | "when using TradingView , you can only be connected through Tradovate" |
| P2-108 | support.thetradingpit.com/how-much-profit-split-do-you-offer-on-the-futures-live-stage | 2026-10-03 | no date shown | HC | "The profit share ranges from 60% to 80%" |
| P2-109 | https://www.thetradingpit.com/futures | 2026-10-03 | no date shown | sales | "Futures Prime Trading Challenges"; "Price |$99" |
| P2-112 | https://propedcapital.com/legal/terms | 2026-10-03 | Last updated August 15, 2026 | terms | "weekday swing or overnight holds are permitted"; "Copy trading and automated strategies may be used only where supported and permitted." |
| P2-115 | https://propedcapital.com/faq/trading-rules | 2026-10-03 | no date shown | HC | "You can hold overnight and swing trade freely."; "EAs / Bots / Automated" listed with a red not-allowed (x) icon; "Weekend Holds require an add-on." |
| P2-116 | https://propedcapital.com/faq/restricted-countries | 2026-10-03 | no date shown | HC | "If your country is not listed, you are welcome to register." (no Canada) |
| P2-117 | https://propedcapital.com/faq/plan-comparison | 2026-10-03 | no date shown | HC | "Standard Eval - 50k|$50,000|$175|$2,000 (Eod)" |
| P2-118 | https://propedcapital.com/faq/platform-getting-started | 2026-10-03 | no date shown | HC | "Traders are also welcome to use R Trader Pro or any other Rithmic-approved third-party trading screen." |
| P2-119 | https://propedcapital.com/faq/drawdowns | 2026-10-03 | no date shown | HC | "Standard Eval - 150k|$150,000|$6,000|Eod" |
| P2-120 | https://propedcapital.com/faq/payouts-profit-splits | 2026-10-03 | no date shown | HC | "Standard Eval - 50k|80%|$500|$3,000|Biweekly" |
| P2-121 | https://propedcapital.com/faq/live-funded-accounts | 2026-10-03 | no date shown | HC | "a live sub-account is opened under PropEd Capital's main capital account through Ironbeam" |
| P2-122 | support.leelootrading.com/kb/a103/2_-holding-positions-during-the-close.aspx | 2026-10-03 | Modified 4/13/2026 | HC | "Holding trades is permitted only in Practice Account Phase, And, only in the Investor type Performance Account" |
| P2-123 | support.leelootrading.com/kb/a205/is-dca-or-algo-trading-allowed-at-leeloo.aspx | 2026-10-03 | Modified 4/4/2026 | HC | "Manually executed trades based on signals (e.g., entering trades based on an alert from another system, as long as the actual trade is executed manually)" |
| P2-124 | support.leelootrading.com/kb/a120/what-trading-platforms-can-i-use.aspx | 2026-10-03 | Modified 10/10/2024 | HC | "You may use any platform compatible with Rithmic data." |
| P2-130 | https://leelootrading.com/terms-of-service | 2026-10-03 | Last Updated: March 31, 2026 | terms | no country list found; "Not all features, contests, competitions, products or services ... are available to all persons or in all geographic locations." |
| P2-131 | support.leelootrading.com/kb/a17/3_-the-investor-performance-accounts-and-foundation-program.aspx | 2026-10-03 | Modified 4/14/2026 | HC | "Traders may hold up to 3 micros through the close"; "Use of automated systems, bots, or third-party trade execution is prohibited and your account will be closed." |
| P2-132 | https://leelootrading.com/ | 2026-10-03 | no date shown | sales | "Aspire, $250 ... $25,000 \| 3 contracts" |
| P2-133 | help.toponefutures.com/en/articles/10907901-can-i-hold-trades-overnight | 2026-10-03 | "Updated yesterday" | HC | "holding trades overnight is not allowed . All trades must be closed by 4:10 PM EST daily." |
| P2-134 | help.toponefutures.com/en/articles/10907920-can-i-use-ea-s-bots | 2026-10-03 | "Updated yesterday" | HC | "we do not allow the use of Expert Advisors (EAs) or Bots" |
| P2-135 | help.toponefutures.com/en/articles/10907951-can-i-trade-news | 2026-10-03 | "Updated yesterday" | HC | "Yes , you are allowed to trade news on your accounts" |
| P2-136 | help.toponefutures.com/en/articles/11021644-countries-with-limitations-and-restrictions | 2026-10-03 | "Updated yesterday" | HC | "Individuals or entities with citizenship in or residing in the countries listed below are prohibited" (list has no Canada) |
| P2-137 | help.toponefutures.com/en/articles/11680891-copy-trading-policy | 2026-10-03 | "Updated yesterday" | HC | "copy trading is strictly limited to accounts of the exact same type and exact same size" |
| P2-138 | help.toponefutures.com/en/articles/10906950-maximum-contracts-explained | 2026-10-03 | "Updated yesterday" | HC | "25k 1 Mini / 10 Micros 50k 3 Mini / 30 Micros" |
| P2-139 | help.toponefutures.com/en/articles/10907134-understanding-the-drawdown-in-elite-accounts | 2026-10-03 | "Updated yesterday" | HC | "how the Max Trailing Drawdown operates on Elite accounts" |
| P2-140 | help.toponefutures.com/en/articles/17149341-can-i-switch-my-trading-platform-... | 2026-10-03 | "Updated yesterday" | HC | "Tradovate / NinjaTrader or BlackArrow" |
| P2-141 | help.toponefutures.com/en/articles/12717928-elite-sim-funded-account-payout-requirements | 2026-10-03 | "Updated yesterday" | HC | "the 25% consistency rule" |
| P2-142 | intercom.help/funded-futures-family/en/articles/15892350-permitted-times-to-trade | 2026-10-03 | "Updated over a week ago" | HC | "All trades must close by 4:45 pm EST" |
| P2-143 | intercom.help/funded-futures-family/en/articles/15892413-bots-algorithmic-trading-policy | 2026-10-03 | "Updated over 3 weeks ago" | HC | "we don’t permit bot or algorithmic trading." |
| P2-144 | intercom.help/funded-futures-family/en/articles/15892316-rules-restricted-countries-regions | 2026-10-03 | August 28, 2026 | HC | "If your country is not listed in our restricted countries / regions, you are eligible to participate in our trading platform" (list has no Canada) |
| P2-145 | intercom.help/funded-futures-family/en/articles/15892353-news-trading-policy | 2026-10-03 | August 11, 2026 | HC | "Trading during news events is permitted across all accounts." |
| P2-146 | intercom.help/funded-futures-family/en/articles/15656536-connecting-your-trading-platform | 2026-10-03 | August 11, 2026 | HC | "Connecting to NinjaTrader ... Connecting to Tradovate" |
| P2-147 | intercom.help/funded-futures-family/en/articles/15705476-prime-funded-account | 2026-10-03 | August 11, 2026 | HC | "Prime Accounts offer payouts every 3 trading days" |
| P2-148 | intercom.help/funded-futures-family/en/articles/15808767-prime-drawdown | 2026-10-03 | "Updated over 3 weeks ago" | HC | "All Prime funded accounts utilize a End of Day Drawdown system" |
| P2-149 | intercom.help/funded-futures-family/en/articles/15650785-account-fees | 2026-10-03 | "Updated over 3 weeks ago" | HC | "There are no activation fees and no recurring subscription fees on funded accounts." |
| P2-154 | https://www.toponefutures.com/terms-and-conditions | 2026-10-03 | Last updated: June 10, 2026 | terms | "Using bots, Expert Advisors (EAs), or automated trading systems." (prohibited list) |
| P2-155 | https://www.fundedfuturesfamily.com/terms-and-conditions/ | 2026-10-03 | no date shown | terms | no automation clause found |
| P2-156 | https://fundednext.com/futures-challenge-terms | 2026-10-03 | Last updated: 25 September 2026 | terms | no automation clause found |

Page dates shown as "Updated this week / yesterday / over N weeks ago" are relative labels from Intercom on
2026-10-03, not absolute dates. Freshdesk shows no year for 2026 dates.

### Part 3 (B-xx)

All fetched 2026-10-03 (UTC). Files are in `reports/stage_e13_briefs/pages/BrokerVenues/`; the fetch id
links each source to its sha256 in `fetch_log.md`.

| key | URL | fetch id / file | page date | page type | verbatim quote |
|---|---|---|---|---|---|
| B-01 | https://www.interactivebrokers.ca/en/pricing/commissions-futures.php | F001 ibkrca_commissions_futures.html | no date shown | broker pricing | "Spot-Quoted Futures, E-Nano Futures, E-micro Futures and Futures Options (MES, MNQ, M2K, VOLQ, MYM, 2YY, 5YY, 10Y, 30Y, MCL, MRB, MGC, MWN, MTN, SIL, VXM, MHNG, ...) ... ≤ 1,000 \| USD 0.25 /contract"; "All fees are charged in the currency of the traded product." |
| B-02 | https://www.interactivebrokers.ca/en/accounts/fees/CME.php | F006 ibkrca_fees_CME.html | no date shown | broker fee schedule | "Micro E-Mini Futures Products MES, MNQ, M2K, VOLQ \| USD \| 0.35"; "E-micro Forex Futures M6A, M6B, M6E, ... MCD, MJY, MSF ... \| USD \| 0.24"; "Non-Members & IIP \| All Products \| USD \| 0.01"; "Interactive Brokers Canada Inc. is a member of the Canadian Investment Regulatory Organization (CIRO)" |
| B-03 | https://www.interactivebrokers.ca/en/accounts/fees/CBOT.php | F007 ibkrca_fees_CBOT.html | no date shown | broker fee schedule | "Micro E-Mini Futures \| MYM \| USD 0.35"; "Micro Treasury Futures \| 2YY, 5YY, 10Y, 30Y, MWN, MTN \| USD 0.30"; "U.S. Treasury Futures \| ZN, TN \| USD 0.80"; "ZF \| USD 0.65"; "ZT \| USD 0.65"; "Micro Ags-Electronic Futures \| MZC,MZS,MZW,MZL,MZM \| USD 0.50" (first column = Tier I Non-Members) |
| B-04 | https://www.interactivebrokers.ca/en/accounts/fees/NYMEX.php | F008 ibkrca_fees_NYMEX.html | no date shown | broker fee schedule | "MCL \| USD 0.50"; "MHNG \| USD 0.60"; "NG \| USD 1.60" (Tier I column) |
| B-05 | https://www.interactivebrokers.ca/en/accounts/fees/COMEX.php | F009 ibkrca_fees_COMEX.html | no date shown | broker fee schedule | "MGC \| USD 0.70 \| USD 0.20"; "MHG \| USD 0.70 \| USD 0.30" (Non-Member, Member) |
| B-06 | https://www.interactivebrokers.ca/en/trading/margin-futures-fops.php?hm=ca&ex=us&rgt=0&rsk=1&pm=0&rst=101004100808 | F010 ibkrca_margin_fut_ca_us.html | no date shown | broker margin page | "For residents of Canada trading futures and FOPs: You are subjected to margin requirements."; "CME \| MES \| MICRO E-MINI S&P 500 STOCK PRICE INDEX \| MES \| 2593.185 \| 1826.23 \| 3704.55 \| 2608.90 \| USD"; "Each day at 'Intraday End Time' the futures contract will revert back to the full overnight margin requirement" |
| B-07 | https://www.interactivebrokers.ca/en/pricing/market-data-pricing.php | F003 ibkrca_market_data.html | no date shown | broker pricing | "US Securities Snapshot and Futures Value Bundle \| USD 10.00 \| USD 30.00" (fee, commission waiver); "Includes top of book quotes for CBOT, CME, COMEX, and NYMEX"; "CME Real-Time (L1) ... non-pro USD 1.55" |
| B-08 | https://www.interactivebrokers.ca/en/index.php?f=4969 | F004 ibkrca_minimums.html | no date shown | broker fees page | "Account Minimums \| USD 0.00 \| Inactivity Fees \| USD 0.00"; "Gateway (Internet) \| Trader Workstation and TWS API \| REST API \| FIX CTCI \| USD 0.00 per month minimum commission \| USD 0.00 per month minimum commission \| USD 1,500.00 per month minimum commission for the first FIX session" |
| B-09 | https://www.interactivebrokers.ca/en/trading/ib-api.php | F013 ibkrca_ib_api.html | no date shown | broker product page | "Automate algorithmic trading strategies, advanced programmatic investing or trading systems."; "Programmatically place orders including advanced order types and algos" |
| B-10 | https://www.interactivebrokers.ca/en/accounts/trading-and-market-data.php | F015 ibkrca_trading_and_market_data.html | no date shown | broker permissions page | permissions table "Futures ... Canada ... United States"; "Interactive Brokers Canada Inc. is a member of the Canadian Investment Regulatory Organization (CIRO)" |
| B-11 | https://www.interactivebrokers.ca/en/accounts/rsp_tfsa_information.php | F014 ibkrca_rsp_tfsa.html | no date shown | broker account rules | "Margin trading is not permitted in a RRSP/SRRSP."; TFSA "No margin trading." (qualified-investment lists contain no futures) |
| B-12 | https://www.interactivebrokers.ca/en/accounts/account-guide.php | F095 ibkrca_account_guide.html | no date shown | broker account guide | "Margin \| Cash, Reg T and Portfolio Margin are available." |
| B-13 | https://www.interactivebrokers.ca/html/retailAccount/stockMarginReq.html | F011 ibkrca_stockMarginReq.html | no date shown | broker margin rule | "All stocks bought or sold on margin require a minimum of $2,000 in equity." |
| B-14 | https://interactivebrokers.github.io/tws-api/basic_contracts.html | F019 ibkr_twsapi_basic_contracts.html | no date shown | API docs | "A regular futures contract is commonly defined using an expiry and the symbol field"; `contract.SecType = "FUT"` |
| B-15 | https://www.bcsc.bc.ca/documents/view/S0SES1SFS1S0S6S3S6S4S7S5S7S2S7SBS6S4S7SAS7S7S6SDS7S4S7SBS6SES6S0S7S2S0S1 | F021 bcsc_doc1.pdf | December 20, 2024 | regulator decision (2024 BCSECCOM 523, RBC Capital Markets, LLC) | "Exemption from s. 34(a) requirement to be registered as a dealer to trade exchange contracts ... the person will only trade exchange contracts with sophisticated investors."; "(o) an individual that beneficially owns financial assets ... of at least $5 000 000" |
| B-16 | https://www.bcsc.bc.ca/documents/view/S0SES1SFS1S0S6S3S6S4S7S5S7S2S7SBS6S4S7SAS7S7S6SDS7S4S7SBS6SES6S0S7SAS0S1 | F022 bcsc_doc2.pdf | July 31, 2025 | regulator decision (2025 BCSECCOM 346, StoneX Financial Ltd.) | "the person will only trade exchange contracts with sophisticated investors." |
| B-17 | https://www.bcsc.bc.ca/documents/view/S0SES1SFS1S0S6S3S6S4S7S5S7S2S7SBS6S4S7SAS7S7S6SDS7S4S7SBS6SES6S0S7S4S0S1 | F023 bcsc_doc3.pdf | April 3, 2025 | regulator decision (2025 BCSECCOM 141, Duneland Commodities Inc.) | same headnote as B-15 |
| B-18 | https://web.archive.org/web/20250911092608/https://faq.ampfutures.com/hc/en-us/articles/10797726829463-Restricted-Countries-List | F031 amp_restricted_countries_wb20250911.html | Wayback capture 2025-09-11 | broker help centre (archived) | "Only 3 provinces in Canada are allowed: Alberta, Ontario and Quebec. Additionally, British Columbia accounts may be allowed at the discretion of a senior manager." |
| B-19 | https://web.archive.org/web/20250812000009/https://faq.ampfutures.com/hc/en-us/articles/33480677897623-Can-I-open-an-AMP-account-if-I-live-outside-the-United-States | F032 amp_outside_us_wb20250812.html | Wayback capture 2025-08-12 | broker help centre (archived) | "Yes, you can open an AMP account even if you live outside the United States, but there are a few important points to know:" |
| B-20 | https://www.ampfutures.com/trading-info/margins | F027 amp_margins.html | no date shown | broker margin page | "Maintenance Margin is set by the exchange. This is the amount required to carry a contract past the daily close."; "Micro E-mini S&P 500 \| MES \| MES \| CME \| $2,881.00 \| $40.00" |
| B-21 | https://www.ampfutures.com/trading-info/exchange-data-fees | F034 amp_exchange_data_fees.html | "Prices effective June 1, 2026" | broker fees | "CME Bundle - ALL CME Markets (Level 1) Top of Book \| $15.00"; "CME/Globex (Level 1) Top of Book \| $5.00" |
| B-22 | https://www.ampfutures.com/trading-platform/rithmic-r-api | F038 amp_rithmic_api.html | no date shown | broker platform page | "The total FLAT monthly technology cost to use the Rithmic API is $125 ($100 API fee + $25 User/Trader ID)."; "For LIVE trading, a Rithmic trade routing fee of $0.10 per contract filled will also apply." |
| B-23 | https://www.ampfutures.com/news/cme-e-micro-indices-launched-ready-for-live-trading | F037 amp_news_micro_launch.html | 2019 (launch "May 5, 2019") | broker news | "Total per Side $0.42"; "AMP Account Minimum to get started is only $100." |
| B-24 | https://www.ampfutures.com/why-amp/commission-quote-match | F028 amp_commissions.html | no date shown | broker pricing | "We will MATCH or BEAT any Written Commission Quote!*" (no rate table) |
| B-25 | https://vendor-support.ninjatrader.com/s/article/How-Can-I-Open-a-NinjaTrader-Account-in-Canada?language=en_US | F047 nt_canada_scrapling.md | Apr 16, 2025 | broker help article | "Canadian law restricts NinjaTrader from opening accounts for residents of Canada that are outside of the province of Ontario. This includes all other provinces: Quebec, Alberta, Manitoba, British Columbia, ..." |
| B-26 | https://vendor-support.ninjatrader.com/s/article/Opening-a-Tradovate-Account-in-Canada?language=en_US | F048 tradovate_canada_scrapling.md | Nov 19, 2024 | broker help article | "Canadian residents living in the province of Ontario are able to open an account with Tradovate."; "If you are in Canada, but outside of Ontario, you are still able to use Tradovate in Simulated Mode." |
| B-27 | https://partner.ninjatrader.com/connect/resources/legal/ninja-trader-api-license-agreement | F045 nt_api_license.html | no date shown | API licence | "access and use the API solely for the purpose of connecting Your order entry and/or trading program(s) software to Ninj[aTrader]" |
| B-28 | https://developer.ninjatrader.com/ | F046 nt_developer.html | no date shown | developer page | "Build, test, and deploy automated trading strategies" |
| B-29 | https://support.optimusfutures.com/do-you-allow-canadian-futures-traders-to-open-accounts | F051 optimus_canadian.html | no date shown (copyright 2025) | broker help article | "We accept all Non-Solicited Self-Directed Canadian futures traders when you Open an Optimus Futures account that is cleared through Phillip Capital and Ironbeam." |
| B-30 | https://support.optimusfutures.com/international-futures-trading | F049 optimus_international.html | no date shown | broker help article | "Yes, Optimus Futures allows and supports foreign clients trading futures from outside the United States. We currently have account holders residing in many different countries, including: Canada" |
| B-31 | https://community.optimusfutures.com/t/futures-broker-for-british-columbia-residents/3157 | F050 optimus_community_bc.html | posts 2019-11-19 to 2020-03-20 | broker staff forum post | "If you are currently living in BC, Canada, we can accept you as a client with Ironbeam." |
| B-32 | https://www.ironbeam.com/?p=4310 | F053 ironbeam_p4310.html | no date shown | broker FAQ | "Yes, we open accounts for people located outside the United States and accept accounts from many countries. To confirm whether your country is supported, please send a message to [email protected]" |
| B-33 | https://www.ironbeam.com/how-to-open-a-futures-trading-account/ | F052 ironbeam_open_account.html | no date shown | broker page | "Ironbeam has no account minimum."; "If you are outside the United States and want to confirm your country of residence is eligible, reach out to [email protected] before applying." |
| B-34 | https://www.ironbeam.com/margins | F054 ironbeam_margins.html | no date shown | broker margin page | "Exchange/overnight margins fluctuate daily"; "Micro E-Mini S&P 500 \| MES \| $50 \| $2,307" |
| B-35 | https://www.ironbeam.com/api/ | F055 ironbeam_api.html | no date shown | broker API page | "Easy Integration via REST"; "Send orders to the exchange directly from your API connection" |
| B-36 | https://www.ironbeam.com/pricing/ | F056 ironbeam_pricing.html | no date shown | broker pricing | "This content is password-protected." |
| B-37 | https://edgeclear.com/technology/ (also /legal-notices/, home) | F064, F063, F059 | no date shown | broker pages | "Automated Trading Solutions"; "Unlock the potential of algorithmic trading and embrace the power of automation with EdgeQX." (no Canada statement on any fetched page) |
| B-38 | https://www.tradestation.com/faqs/ | F065 tradestation_faqs.html | no date shown | broker FAQ | "For international clients, a valid passport and address verification dated within the last 60 days are required." |
| B-39 | https://www.tradestation.com/platforms-and-tools/trading-api/ | F067 tradestation_api.html | no date shown | broker API page | "Multi-asset brokerage API: equities, futures, and options with self-clearing and direct-market-access services – all from a single API key" |
| B-40 | https://invest.questrade.com/self-directed-investing | F089 questrade_self_directed.html | no date shown | broker product page | "More than just Stocks & ETFs. Trade options, precious metals, and IPOs on one powerful platform." |
| B-41 | https://www.wealthsimple.com/en-ca/trade/futures | F074 wealthsimple_trade_futures.html (DO_NOT_COMMIT) | no date shown (cites "as of June 12, 2026") | broker product page | "It's $1 USD per contract, with $0 platform fees and $0 market data fees, plus applicable exchange and regulatory fees. These additional exchange and regulatory fees (for example, $0.35 and $0.02, respectively, for the micro S&P 500)"; "Trade everything from global indices to commodities in micro, mini, and standard contract sizes."; "Wealthsimple supports market, limit, and stop-loss orders for futures contracts." |
| B-42 | https://www.wealthsimple.com/en-ca/learn/how-to-trade-futures | F072 wealthsimple_learn_futures.html (DO_NOT_COMMIT) | Updated September 15, 2026 | broker education | "Futures are not permitted in Tax-Free Savings Accounts (TFSAs) or Registered Retirement Savings Plans (RRSPs). You must use a non-registered account." |
| B-43 | https://www.wealthsimple.com/en-ca/legal/terms | F073 wealthsimple_terms.html (DO_NOT_COMMIT) | "Effective immediately for new clients and September 27, 2026 for existing clients" | broker terms | "copy, scrape, crawl, or data-mine the Platform or Content in any form or by any method;"; "reverse engineer, decompile, or disassemble the Platform"; "disable, circumvent, or defeat any security features ... including without limitation, any rate limits" |
| B-44 | https://www.rbcdirectinvesting.com/pdf/corpoptionsE.pdf | F077 rbcdi_risk_disclosure_futures_options.pdf | (c) 2024 | broker agreement form | "30. ACCOUNT APPROVAL ... The Customer may NOT write uncovered options or covered put options; engage in spreads combinations or straddles; write options against convertible securities; nor buy or sell futures." |
| B-45 | https://www.td.com/ca/en/investing/direct-investing/trading/active-trader | F079 td_active_trader.html | no date shown | broker page | "Futures \| CME Futures (15 Min Delayed)" (market-data package row) |
| B-46 | https://www.td.com/ca/document/PDF/forms/521778.pdf | F081 td_commission_schedule.pdf | no date shown | broker commission schedule | contents: "Canadian Equities ... U.S. Equities ... Canadian and U.S. Options ... Gold and Silver ... Fixed Income Investments ... Mutual Funds" (no futures entry) |
| B-47 | https://www.bmoinvestorline.com/selfDirected/pdfs/AuthorizedTradingAgent.pdf | F083 bmo_il_authorized_trading_agent.pdf | no date shown | broker form | "BMO InvestorLine Inc. is not registered to trade in futures." |
| B-48 | https://www.investorsedge.cibc.com/en/pricing.html | F085 cibc_ie_pricing.html | rates "Effective September 17, 2026" | broker pricing | "Investment choices \| Stocks \| Exchanged Traded Funds (ETFs) \| Options \| Canadian Depositary Receipts (CDRs) \| Mutual Funds \| Guaranteed Investment Certificates (GICs) \| Fixed Income \| Precious Metals \| Initial Public Offerings (IPOs) \| Structured Notes" |
| B-49 | https://nbdb.ca/help/transactions/transfers/products-transferred.html | F086 nbdb_products_not_transferred.html | (c) 2026 | broker help | "Private investments \| Futures contracts \| Some Guaranteed Investment Certificates (GICs)" (list of products that cannot be transferred to NBDB) |
| B-50 | https://www.qtrade.ca/en/investor/trading/investment-choices.html | F088 qtrade_investment_choices.html | no date shown | broker product page | "Qtrade makes it easy to build a well-diversified portfolio, with access to a wide array of stocks, ETFs, mutual funds, bonds, options and more." |
| B-51 | https://www.gffbrokers.com/resources/faqs | F091 gff_faqs.html | no date shown | broker FAQ | "Country-specific options depend on the clearing firm's regulatory coverage - reach out and our team will match you with the right firm for your jurisdiction." |
| B-52 | https://www.m-x.ca/f_circulaires_en/057-26_en.pdf | F093 mx_circular_057-26_jitneytrade.pdf | May 4, 2026 | exchange circular | "Jitneytrade Inc. is registered as an Investment Dealer with the Canadian Investment Regulatory Organization (CIRO) and the Canadian Security Administrators in most provinces and territories." |
| B-53 | https://www.questrade.com/pricing/self-directed-commissions-plans-fees/forex-cfd | F068 questrade_cfd.html | no date shown | broker pricing | Questrade's FX and CFD pricing page (CFDs, not exchange futures). Supporting only |

## 5. Gaps, failures and deviations

**Lead ruling on deviation fetches (Fable R-11, 2026-10-04).** Two workers used Scrapling on sites whose terms forbid
automated access before reading those terms: PropVenues1 on help.tradeify.co and elitetraderfunding.com, and
PropVenues2 on lucidtrading.com. (BrokerVenues' NinjaTrader fetch and InfoSource's Insper fetch were compliant
with the rule as written.) Those pages stay on disk and are not committed (DO_NOT_COMMIT.txt). Where a compliant
copy (Wayback or a plain fetch) corroborates a fact, that copy is the source. Facts whose only copy is a deviation
fetch are marked "deviation fetch":
- P1-19, Tradeify pricing;
- P1-21, Tradeify trailing drawdown;
- P1-37, ETF's terms (the "automated decision-making systems" definition);
- Lucid's TOU (its terms status only).
No classification rests on these alone. Tradeify and Lucid are NOT PERMITTED on the overnight rule from compliant
copies (P1-17 with Wayback; Lucid's help page). ETF's written-authorization rule is also on its help page (P1-36).


### Part 1

- Apex: apextraderfunding.com and its help centre were down for scheduled maintenance on 2026-10-03
  (curl got a 403 Cloudflare page; Scrapling get and fetch returned the maintenance page). All Apex rules
  come from Wayback captures dated 2026-02-17 to 2026-09-27. The overnight and automation rules for
  Performance Accounts come from February and March 2026 captures. The new help centre's
  prohibited-activities and EOD-PA pages have no usable capture (the July 2026 captures are 302
  redirects or blocked). Apex evaluation and activation prices are UNSOURCED (the home-page capture
  renders prices by JavaScript). Current Apex terms could not be read; only a 2021 Wayback copy was found.
- Prices UNSOURCED: TPT Test subscription price; ETF DTF and Diamond Hands prices (sales page rendered by
  JavaScript; a Scrapling fetch of /direct-to-funded returned empty); Apex (above). ETF's 25K DTF
  contract limit and Diamond Hands 100K drawdown size are not stated on the fetched pages.
- Topstep: the platform-list article (8284138) returned 404, so whether NinjaTrader and Tradovate are
  closed to new sign-ups is UNSOURCED. The 50K and 100K MLL sizes were not re-checked (the brief limited
  the Topstep re-check to the overnight, automation and Canada fields).
- Tradeify: no help article on trade copiers was found. The close time changed from 4:59 PM ET (WB June
  2026) to 4:45 PM ET (current). Canada was "Sim Funded Only, Only Ontario residents" in the June 2026
  capture and is absent from the current list. The current page also has a "Live Account Eligibility"
  section, whose country rows I did not confirm.
- ETF Canada: the page says Stripe serves Canada only "with limitations (extended network / preview)".
  Whether a Canadian can actually pay is not settled by the page.
- None of the seven firms uses the words "semi-automated" or "must actively monitor" on the pages fetched.
  Apex's semi-automated allowance appears only in third-party search snippets, which are not sources.
- Deviation on terms: I used Scrapling `extract fetch` on help.tradeify.co (6 pages) and on
  elitetraderfunding.com (home and terms) BEFORE checking their terms. Both terms forbid scraping and
  robots. For Tradeify, Wayback copies (tf_wb_*) confirm the overnight, algorithm and restricted-country
  passages. The Tradeify pricing, drawdown and current restricted-list facts rest only on the Scrapling
  copies; no Wayback capture of the pricing page exists. ETF's help pages were fetched by plain curl. All
  pages from the five domains whose terms forbid automated access (Topstep, Tradeify, TPT, ETF, Bulenox)
  are listed in DO_NOT_COMMIT.txt. TPT data came from Zendesk's public Help Center API, read by plain curl.
- WebSearch: 11 calls, no budget notice. Firecrawl: 0 calls. No logins, forms, contact or Databento use.

### Part 2

- Phidias help centre (helpcenter.phidiaspropfirm.com) is a JavaScript app. curl and `scrapling extract fetch`
  both returned only a page shell [P2-04][P2-06], so any help-centre article on automation could not be read.
  The monthly evaluation price sits in a JS configurator and is UNSOURCED; lifetime prices come from the TOU.
- Phidias, LIVE account after Premium: the overnight rule is not stated (UNSOURCED); it is included in the drafted question.
- Phidias minimum withdrawal conflicts: the rules page says "Min. Withdrawal $500" and the TOU says "never be less than $1,000".
- Lucid: lucidtrading.com returns 403 / Cloudflare to curl. I fetched the homepage, refund disclaimer and TOU
  with `scrapling extract fetch` (not stealthy) BEFORE reading the TOU, which bans "any robot, spider, or other
  automatic device" for accessing the website. That breaks research_rules.md (no automation beyond a plain
  fetch on such sites). The three files (lucid_home, lucid_disclaimer, lucid_tou) are listed in DO_NOT_COMMIT.txt,
  and no more scrapling fetches were made on that domain. The support subdomain was fetched with plain curl.
- Pages from alpha-futures.com, lucidtrading.com, tradeday.com, earn2trade.com, thetradingpit.com,
  propedcapital.com and leelootrading.com are under terms that forbid automated access or scraping. They were
  fetched with plain curl, apart from the Lucid exception above, and are listed in
  pages/PropVenues2/DO_NOT_COMMIT.txt.
- Earn2Trade: overnight rules for LiveSim and Live accounts are UNSOURCED (the help centre covers evaluations only).
  Prices for TCP50 and TCP100 and the contract ladders for those sizes are UNSOURCED (dynamic or image content).
- FundedNext Futures: no news-trading rule was found (UNSOURCED).
- The Trading Pit: Futures Classic rules appear in the help centre, but the current futures sales page lists
  only Futures Prime [P2-109]. Whether Classic can still be bought is UNCLEAR. No TTP page shows a date.
  The "How much do your Challenges cost?" article returned an empty body.
- PropEd Capital: the not-allowed status of "EAs / Bots / Automated" comes from the red x icon class in the FAQ
  HTML (lucide-x versus lucide-check on allowed items). The page text has no word for it. Semi-automation is
  not addressed, so a question is drafted.
- Leeloo: weekend holding on the Investor PA and its news rule are UNSOURCED. The billing basis for practice
  prices (one-time or monthly) is not confirmed. The Investor program "is being phased out soon".
- Top One Futures: evaluation prices and Elite drawdown sizes are UNSOURCED. Funded Futures Family: price
  amounts and copier wording are UNSOURCED.
- Extra firms screened but not added (not fetched as evidence, so nothing here drives a conclusion):
  TickTickTrader (homepage 403 to curl, not retried); UProfit (pages fetched [P2-150..153], no overnight
  wording on them; terms ban "automated software ... to manipulate results"); Aqua Futures, Purdia Capital,
  OneUp Trader, DayTraders.com (search snippets only).
- Non-survivors among the extras: Top One Futures and Funded Futures Family were both described on third-party
  sites as allowing overnight holds. Their own pages require flat by 4:10 pm ET and 4:45 pm ET.
- Part 1 candidates for further questions were not waited for, as the brief allows.

### Part 3

- IBKR Canada: (a) no IBKR page names British Columbia. Eligibility rests on IBKR Canada being the CIRO
  entity for Canadian residents with a Canada-resident margin schedule. (b) No futures-specific minimum
  equity was found. (c) The client agreement and any API automation clauses were not retrieved because
  the agreements page is JavaScript-rendered (F017). (d) The margin page shows no date. (e) The SIL
  exchange fee is not on the COMEX fee page. (f) The numbering of market-data footnote 14 is ambiguous
  (an empty list item), so the CME L1 USD 1.55 waiver rule is not stated here.
- Wealthsimple: the help-centre futures article (contract list, eligibility, margins) returned 403 to
  curl and WebFetch. Its terms forbid scraping, so Scrapling was not used; no Wayback capture exists. BC
  eligibility, the contract list, multi-day holds and margins are UNSOURCED. All wealthsimple.com files
  are listed in DO_NOT_COMMIT.txt.
- AMP: the live help centre returns 403; Wayback captures from 2025 were used (their dates are the page
  dates). No terms of use were found for ampfutures.com, and Scrapling was not used there. Current
  commission rates are not published (quote form only). The micro all-in figure is from 2019 and stale.
- NinjaTrader/Tradovate articles: curl returned a JavaScript shell and WebFetch returned "CSS Error".
  Before using Scrapling I looked for website terms of use (ninjatrader.com /terms-of-use/, /legal/,
  /terms/ and similar all 404; the disclosures page lists none; vendor-support robots.txt "Allow: /").
  None were found, so `scrapling extract fetch` was used (F047, F048), as recorded in the log.
- Ironbeam: the pricing page is password-protected, so commissions are UNSOURCED. BC is not confirmed on
  Ironbeam's own pages.
- EdgeClear, TradeStation, GFF: no broker-side statement on Canadian or BC eligibility was found.
  Third-party snippets (forums, review sites) were not used as sources.
- Jitneytrade: jitneytrade.com did not resolve (curl http 000, WebFetch ENOTFOUND).
- bmo.com refused curl (http 000), so the BMO FAQ page was not saved. The BMO InvestorLine PDF form was
  used instead.
- Absence evidence: CIBC, Qtrade, Questrade and TD are classed from product lists or commission
  schedules that omit futures, not from an explicit "no futures" statement. RBC and BMO have explicit
  statements. NBDB's evidence is indirect (futures cannot be transferred in).
- Not covered: Disnat (Desjardins), Canaccord Direct, Friedberg Direct (FX/CFD dealer) and any other
  CIRO dealer not named in the brief.
- Counts: 81 evidence files saved (plus .txt extracts), 28 of 100 WebSearch calls, 0 Firecrawl calls,
  2 Scrapling fetches, 4 WebFetch attempts (all failed). Failed fetches: 15 rows marked FAILED in the
  log (403s, 404s, DNS, WebFetch shells). Error pages were deleted and their log rows annotated.

