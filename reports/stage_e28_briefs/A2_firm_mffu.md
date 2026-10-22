# A2 firm facts: My Funded Futures (MFFU), as of 2026-10-21

Worker: A2_mffu (Stage E.28 Layer 2 facts; no scoring). Pages saved raw under
reports/stage_e28_briefs/pages/A2_mffu/ (log.tsv has URL, UTC/PDT fetch time, sha256). Files named `mffu_*`
below are in that folder; `.txt` siblings are tag-stripped text used for grep. All MFFU pages fetched by curl on
2026-10-21 between about 06:25 and 07:10 PDT (13:25-14:10 UTC), after a terms check (section 0).
E.13 copies (reports/stage_e13_briefs/pages/PropVenues1/mff_*, fetched 2026-10-03 21:4x UTC) were used as
pointers and for change checks; "E.13 date" below means that copy.

## 0. Terms check and fetch route

- myfundedfutures.com/terms (mffu_terms.html, fetched today): grep for robot|scrap|spider|crawl|automat|harvest
  finds no clause forbidding automated access (the only hits are "automatic charges" and 12.5 data monitoring).
- robots.txt: myfundedfutures.com "User-agent: * / Disallow:" (allow all) (mffu_robots.txt);
  help.myfundedfutures.com disallows "/*=" (query URLs) with "Crawl-delay: 1" (mffu_help_robots.txt). Help-centre
  search URLs (?q=) were therefore not fetched; articles were fetched with >= 1.5 s spacing.
- Decision (logged in log.tsv row TERMS): curl allowed on both hosts; no Scrapling needed; no deviation fetches.

## 1. Standard 50K plan (spec rule: first 50K evaluation plan on the pricing page today)

**Which plan.** The homepage plan selector (mffu_home.html.txt lines 36-152) lists, under the default "Standard
Plans" tab, BUILDER first, then RAPID, RAPID EOD, PRO; a second tab "Studio Static Plans" follows. The figures shown
are for the 50K selection ("Targets and drawdowns shown for the selected account size"). So the standard 50K plan is
**Builder 50K** (Default MLL option; a cheaper "Add-On" option with a $1,500 MLL also exists).
Quotes: "Four plans, each with clear rules." / "Standard Standard Plans Studio Static Plans" / "BUILDER / Easiest
path to your first payout / One-time payment $92 Based on current promotions / $153". (mffu_home.html.txt l.37-44)
E.13 date (2026-10-03, mff_home.txt l.50-53): same order, BUILDER first. Unchanged.

Note for the lead: the Builder page headline says "$25K & $50K Builder" while its rules table lists 25K, 50K,
100K and 150K (mffu_plans_builder.html.txt). Not material for 50K.

### 1a. Price and billing
| Fact | Value | Source | Quote |
|---|---|---|---|
| List price, Builder 50K Default | USD 153, one-time | mffu_art_14290805.html.txt (Builder 50K guide, "Updated today", dateModified 2026-10-21T08:34:41Z) | "Builder - Default / Builder - Add-On / Price / $153 / $125" |
| Promo prices | 30% off: $107 (Default) / $87 (Add-On); 40% off (2 uses only): $92 / $75 | same | "Discounted Price (30% OFF) / $107 / $87 / Discounted Price (40% OFF - 2 uses only) / $92 / $75" |
| Billing model | one-time payment, no renewals (since 2026-08-25; legacy subscribers keep monthly) | mffu_plans_builder.html.txt; mffu_art_16596406.html.txt | "No activation fee · One-time payment, no renewals"; "Effective August 25, 2026, MyFundedFutures will transition to a one-time payment model for all new purchases." |
| Activation fee | USD 0 | mffu_art_14290805; mffu_art_12398151 (2026-08-25) | "Activation Fee / $0 / $0"; "all MFFU plans, regardless of account size, come with $0 activation fee." |
| Reset fee | **unknown** (no firm page states a reset price; under the one-time model a breached funded account needs a new evaluation) | mffu_art_16596406.html.txt; mffu_plans_builder.html.txt | "Resets will continue to work the same way for all accounts, regardless of purchase date." / "If you breach max drawdown on the sim-funded Builder account, the account ends and you start a new evaluation." Third-party figures (Rapid 50K reset $157, Pro 50K $227, pre-2026-08-25 subscription era) are [unverified, search snippet only, proptradingvibes.com]. |

### 1b. Evaluation stage (Builder 50K Default)
| Fact | Value | Quote (mffu_art_14290805.html.txt unless noted) |
|---|---|---|
| Starting balance | 50,000 | "Starting Balance / $50,000 / $50,000" |
| Profit target | USD 3,000 | "Profit Target / $3,000 / $3,000" |
| Max loss limit (MLL) | USD 2,000, **end-of-day trailing** (Add-On: 1,500) | "Max EOD Drawdown (MLL) / $2,000 / $1,500"; "Starting Minimum Balance / $48,000 / $48,500" |
| MLL mechanics | trails up on EOD equity highs, never down; open-equity losses count at day end; locks at start + 100 | "It does not move intraday. It only adjusts after the market closes each session, based on where your account closed." / "Open equity losses are counted when determining whether your account has breached the rule at the end of the trading day." / "The MLL locks permanently once it reaches $100 above the starting balance." |
| Daily loss limit | USD 1,000 **soft pause** (session ends, account not breached) | "Daily Loss Limit / $1,000 - soft pause"; plan page FAQ: "When your session hits $1,000 down for the day, trading pauses until the next session — but the account is not breached." (mffu_plans_builder.html.txt) |
| Consistency rule (eval) | none | "Consistency Rule / None / None" |
| Minimum trading days | 1 | "Minimum Trading Days / 1 Day / 1 Day" |
| Time limit | none stated; inactivity: account may be closed after 7 calendar days without a trade (one-time-payment accounts) | plan page "Inactivity Rule / 7 Calendar Days"; mffu_art_16596524: "If a trader does not place a trade for 7 consecutive calendar days , the account could be closed. This includes simulated funded accounts." |
| Max contracts | 4 minis / 40 micros | "Max Contracts / 4 Minis / 40 Micros" |
| News (eval) | allowed | "News Trading / Allowed" |
| Overnight | not allowed; auto-flat at session close | "Q: Can I hold positions overnight? No. All positions must be closed before the end of the trading session." |

Inconsistency (pointer for the lead): the Builder plan page box says "Evaluation Stage / One phase · min 2 days ·
no activation fee" directly above "Days to Pass 1" (mffu_plans_builder.html.txt); the rules table and the help guide
say 1 day.

### 1c. Funded stage (Builder 50K, sim-funded)
| Fact | Value | Quote (mffu_art_14290805.html.txt unless noted) |
|---|---|---|
| Sim or live | **sim-funded** first (up to 5 payouts), then live at Blue Row Capital | "Once you hit your $3,000 profit target with at least 1 trading day logged, you are promoted to the Sim Funded stage."; plan page: "The fifth rung is a real live brokerage account at Blue Row Capital"; footer: "All MFFU accounts operate in a simulated environment." |
| Starting balance | 0 (balance may go negative) | "Your account begins at $0, meaning the balance can go negative before the MLL trails up to breakeven." |
| Drawdown | USD 2,000 EOD trailing, starting floor -2,000; locks at +100 | "Max EOD Drawdown (MLL) / $2,000 / $1,500 / Starting Minimum Balance / -$2,000 / -$1,500"; plan page "MLL Lock Level / $100" |
| Daily loss limit | USD 1,000 soft pause | "Daily Loss Limit / $1,000 soft pause" |
| Max contracts | 4 minis / 40 micros (no scaling ladder stated for Builder) | "Max Contracts / 4 Minis / 40 Micros" |
| Accounts | 1 Builder account per user (sim funded); new one no earlier than next trading day after a breach | "Only one Sim Funded account may be active per user at any time on the Builder Plan. In the event of a breach, the earliest a new Sim Funded account may be activated is the following trading day." |
| Inactivity | 7 calendar days | "Inactivity Rule / 7 Calendar Days" |
| News (sim funded) | allowed on Builder | "News trading is fully unrestricted during the evaluation and sim funded stage." |
| Breach | account ends; new evaluation needed | plan page FAQ: "If you breach max drawdown on the sim-funded Builder account, the account ends and you start a new evaluation." |

### 1d. Payout rules (Builder 50K Default, sim funded)
| Fact | Value | Quote (mffu_art_14290805.html.txt unless noted) |
|---|---|---|
| Split | 80/20 (trader/firm) | "Profit Split / 80% Trader / 20% Firm" |
| Buffer | USD 2,100 (= MLL + 100) must be cleared before any request | "Buffer (Must Be Cleared to Request) / $2,100 / $1,600"; "The buffer equals your MLL + $100" |
| First payout | >= USD 500 net profit above buffer (balance >= 2,600) | "For your first payout: you must have at least $500 in net profit above the buffer." / "your account balance must reach at least $2,600" |
| Later payouts | >= USD 500 net profit since last approved payout | "For all subsequent payouts: you must have at least $500 in net profit since your last approved payout." |
| Min days | 2 trading days per cycle; first request >= 48 h after first trade | "You must have traded on at least 2 trading days in the current cycle." / "You may request a payout 48 hours after your first trade has been placed" |
| Consistency (payout) | 50%: best day <= 50% of cycle profit; resets after each payout | "your single largest profit day cannot represent more than 50% of your total profits in the cycle. This calculation resets after each approved payout." |
| Min / max per request | USD 500 / USD 2,000 (gross, before the 80/20 split) | "Minimum Payout Amount / $500"; "Maximum payout per cycle is $2,000. You keep 80% of what you withdraw." Example: "Requested payout: $1,500 ... After 80/20 split, trader receives: $1,200" |
| Number of sim payouts | max 5, then promotion to live | "Max Sim Payouts / 5 Payouts"; "After your 5th approved sim payout, you are eligible for promotion to a live funded account." |
| Frequency | every 48 hours (plan page "Get Paid Every 48 hrs") | mffu_plans_builder.html.txt "Payout cadence Every 48 hours" |
| Processing | "Most payouts are approved instantly"; manual review up to 6-12 business hours | mffu_art_13745661.html.txt (2026-08-25) |
| Payment rail | Riseworks (bank transfer or crypto); Plaid/ACH for US traders | mffu_art_11542406.html.txt (2026-08-26): "Set Up a Riseworks Account: Create an account on Riseworks to receive your payouts. Note: Plaid/ACH payouts are available for US traders." / "You can withdraw funds via bank transfer or cryptocurrency." |

Conflicts to flag (older general payout article, mffu_art_13745661, dateModified 2026-08-25, vs the Builder 50K guide
updated today): the older article says "After your first payout, the Max Loss Limit resets to $100" and "No daily
loss limits on Builder, Rapid or Pro plans"; the Builder guide (today) says the MLL locks at $100 above start once
reached, and that "The Evaluation, Sim Funded and Live stage have a $1,000 soft pause DLL." It also lists a further
live trigger "Reaching the total sim cap of $100k" for Builder. I report the plan-specific guide as current; the
lead may choose the conservative mapping (MLL reset to +100 after first payout, i.e. a static floor at +100).

Interpretation of buffer for a coder (my reading, not a firm quote): the sim-funded account starts at 0 with floor
-2,000; the first request needs balance >= 2,600; a request of X (500 <= X <= 2,000, and X <= balance - 2,100 is
implied by "net profit above buffer") is paid at 0.8 X. The page does not state where the floor sits after a
withdrawal; the MLL lock at +100 means the floor is +100 once the EOD high reaches 2,100.

### 1e. Live stage (Builder)
| Fact | Value | Quote (mffu_art_14290805.html.txt) |
|---|---|---|
| Trigger | after 5th approved sim payout | "Promotion Trigger / After 5th approved sim payout" |
| Drawdown | USD 2,000 EOD trailing, static once MLL reaches 0 | "Live Account Drawdown / $2,000 EOD Trailing / ... / Max Loss Limit / Static once MLL reaches $0" |
| DLL | USD 1,000 | "Daily Loss Limit (Live) / $1,000" |
| Split / cadence / min | 80/20, daily, min USD 250 | "Minimum Payout Amount / $250 / $250 / Profit Split (Live) / 80% Trader / 20% Firm / Live Payout Cycle / Daily" |
| Consistency | none | "Consistency Rule (Live) / None" |
| Accounts | 1 | "Max Live Accounts / 1" |
| Post-breach | 21-day cooldown (no sim trading, no new evals or resets) | "21-Day Cooldown Period initiation: All Sim Funded account trading is prohibited." |
| Live payout timing | requests before 11 AM ET processed same day by partner FCM; one per day | mffu_art_12109396.html.txt (live FAQ, 2025-11-10): "payout requests must be sent before 11 AM EST for the request to be processed the same day." / "payouts are processed once a day by our partner FCM." |
| Live data fees | charged to the live balance | live FAQ: "Your exchange fee will be automatically deducted on the first trading day of the month." |

### 1f. Other 50K plans on the same page (context only; not the standard plan)
From mffu_home.html.txt l.53-95 (50K selection): RAPID $125 promo / $209 list, target 3,000, max drawdown 2,000
**intraday** trailing in funded, 90/10, daily payouts, eval min 2 days; RAPID EOD $135 / $225, EOD trailing, eval
4 days; PRO $159 / $265, EOD trailing, bi-weekly payouts, 80/20. The "Studio Static Plans" tab (mffu_studio.html)
offers static MLL plans ("Max Loss Limit Static $250, $500 or $1,000", homepage l.20). Rapid 50K position limit
"5 minis / 50 micros max" (mffu_plans_rapid.html.txt l.54).

### 1g. Mapping notes for the Combine-to-funded simulator (worker's reading, for EconCoder; lead decides)
- Eval: start 50,000; pass when balance >= 53,000 with >= 1 trading day; fail when EOD balance (incl. open P&L at
  close) <= trailing floor (EOD high - 2,000, capped at 50,100 once the EOD high reaches 52,100 [lock rule "$100
  above the starting balance"]). DLL 1,000 = stop trading for the day (not a fail). No eval consistency. Flat at
  16:10 ET. Inactivity 7 days (not binding at T = 20 trades/day).
- Cost per attempt: 153 (list; 92 with the 40% code, limited to 2 uses), no activation fee; no reset price found.
- Funded (sim): start 0, floor -2,000 trailing on EOD highs, locks at +100. DLL 1,000 soft. Payout cycle: >= 2
  trading days, balance >= 2,100 + 500 for the first request, then >= 500 new net profit; request 500..2,000;
  trader receives 80%; best day <= 50% of cycle profit; >= 48 h after first funded trade; at most 5 payouts, then
  live (Blue Row Capital) with the same 2,000 EOD trailing MLL (static at 0), DLL 1,000, daily payouts, 80/20, min
  250. Breach of sim funded: new evaluation; breach of live: 21-day cooldown.
- Not stated: where the floor sits after a withdrawal (the older payout article says "After your first payout, the
  Max Loss Limit resets to $100"; conservative mapping = floor jumps to +100 after the first payout).

## 2. Products, fees and position limits

Source: "Futures Instrument List / Includes Contract Specifications, Commissions, and Trading Fees", help article
9735811, page date "August 24, 2026" (mffu_art_9735811.html.txt). Each row gives "Total Cost Round Trip"; per side is
my derivation (RT / 2), not a firm figure. The page gives one figure per product (no split by platform, no separate
exchange/NFA line); it says nothing about whether live accounts pay the same. The page also states: "MyFundedFutures
trading hours are between 6:00pm EST through 4:10pm EST." Line numbers are in the tag-stripped text.

| Code | Listed? | Tick size / tick value (as printed) | RT cost USD | Per side (derived) | Status / note |
|---|---|---|---|---|---|
| MNG | not listed | | | | absent from the list |
| QG | listed | 0.005 / $12.50 | 2.92 | 1.46 | **currently restricted** (since "February 7th" [2026]) |
| NG | listed | 0.00025 / $2.50 | 5.12 | 2.56 | **currently restricted** (same notice); tick value printed $2.50 (CME NG tick is $10; firm typo, flag) |
| MCL | listed | 0.01 / $1.00 | 1.16 | 0.58 | allowed |
| QM | listed | 0.025 / $12.50 | 4.32 | 2.16 | allowed |
| CL | listed | 0.01 / $10.00 | 4.92 | 2.46 | allowed |
| MGC | listed | 0.10 / $1.00 | 2.20 | 1.10 | allowed; metals micro cap 5 at 50K (since "April 17th" [2026]) |
| GC | listed | 0.10 / $10.00 | 5.12 | 2.56 | allowed today (on the restricted list in the 2026-03-30 and 2026-06-10 Wayback copies; gone by the 2026-08-04 copy; see 6) |
| SIL | listed | 0.005 / $5.00 | 2.84 | 1.42 | allowed; metals micro cap 5 at 50K |
| SI | listed | 0.005 / $25.00 | 5.12 | 2.56 | **currently restricted** |
| MHG | not listed | | | | absent |
| HG | listed | 0.0005 / $12.50 | 5.12 | 2.56 | **currently restricted** |
| M6E | listed | 0.0001 / $1.25 | 1.44 | 0.72 | allowed |
| 6E | listed | 0.00005 / $6.25 | 5.12 | 2.56 | allowed |
| M6A | listed | 0.0001 / $1.00 | 1.44 | 0.72 | allowed |
| 6A | listed | 0.00005 / $5.00 | 5.04 | 2.52 | allowed |
| MET | listed | 0.50 / $0.05 | 1.16 | 0.58 | allowed (note: site footer says "cryptocurrencies ... are prohibited"; MET/MBT are on the futures list, so I read the footer as spot crypto; flag) |
| ETH | not listed | | | | absent |
| MBT | listed | 5.00 / $0.50 | 3.50 | 1.75 | allowed; "MBT is treated as a mini contract" |
| BTC | not listed | | | | absent |
| M2K | listed | 0.10 / $0.50 | 1.90 | 0.95 | allowed |
| RTY | listed | 0.10 / $5.00 | 4.68 | 2.34 | allowed |
| MYM | listed | 1.00 / $0.50 | 1.90 | 0.95 | allowed |
| YM | listed | 1.00 / $5.00 | 5.76 | 2.88 | allowed |
| MNQ | listed | 0.25 / $0.50 | 1.90 | 0.95 | allowed |
| NQ | listed | 0.25 / $5 | 4.68 | 2.34 | allowed |
| 2YY, 5YY, 10Y, 30Y | not listed | | | | absent |
| ZT, ZF, ZN, ZB | not listed | | | | absent (no Treasury product on the list) |
| micro grains (MZC, MZS, MZW, MZL, MZM) | not listed | | | | absent |
| XC, XK, XW | not listed | | | | absent |
| ZC | listed | 0.0025 / $12.50 | 6.12 | 3.06 | allowed; hours printed "Sunday - Friday 19:00 - 07:45 CT / Monday - Friday 08:30 - 13:20 CT" |
| ZS | listed | 0.0025 / $12.50 | 6.12 | 3.06 | allowed |
| ZW | listed | 0.0025 / $12.50 | 6.12 | 3.06 | allowed |
| ZL | listed | 0.0001 / $6.00 | 6.12 | 3.06 | allowed |
| ZM | listed | 0.10 / $10.00 | 6.12 | 3.06 | allowed |

Quotes (mffu_art_9735811.html.txt): "As of February 7th: Due to increased market volatility, MFFU is implementing
temporary commodities trading restrictions ... The following products are currently restricted from trading: Silver
(SI) Copper (HG) Platinum (PL) Natural Gas (NG) E-Mini Natural Gas (QG)" / "As of April 17th , new limits have been
implemented for micro contracts on metals trading: ... $50k account → maximum 5 micro contracts" / "Also note that
due to volatility, MBT is treated as a mini contract. If you have 3 minis max, you have access to 3 MBT contracts
max." Row example: "Micro E-mini Nasdaq-100 | MNQ | ... | 0.25 | $0.50 | $1.90".
Also listed but outside the candidate set: ES, MES (1.90), 6B, 6C, 6J, 6N, 6S, HE, LE, NKD, PL, HO, RB.
Absence = not on the firm's own list; third-party pages disagree on Treasuries (pickmytrade.io blog, pointer only).

Printed tick values that differ from CME specs (firm typos to flag, not corrected): NG $2.50, YM $5.00, NQ $5, 6A
tick 0.00005/$5.00, ZL $6.00, HO/RB $4.20, MET 0.50/$0.05. The RT costs are what matter for c_lim = F_rt / v; the
coder should take v from CME specs (Layer 1), not from this page.

**Position limits at 50K Builder:** "Max Contracts / 4 Minis / 40 Micros" (ratio 10 micros per mini), MBT counted as
a mini, metals micros capped at 5. Cross-instrument rule (mffu_art_10244682.html.txt, 2026-08-24): "Orders that
combine different instruments (e.g., 2 minis and 20 micros) may technically execute even if they exceed the overall
limit (e.g., more than 2 contracts in total), but this is not permitted!" Hedging banned (fair-play section 5:
"MyFunded Futures prohibits hedging of any kind. Hedging is defined as a trader entering both buy and sell positions
on the same underlying asset, at the same time.").

## 3. Product restrictions, news windows, hours

**Trading hours / flat-by** (mffu_art_9558251.html.txt, 2026-08-24): "Trades may be placed beginning at 6:00 PM EST
when the Globex session opens and can remain open until the New York session closes at 4:10 PM EST." / "any open
positions will be automatically closed at 4:10 PM EST on regular (non-holiday) trading days." Holidays: "auto-
liquidation will not occur at the half-time market close, and the trader is responsible for closing the
positions." So 16:10-17:00 ET (50 min) of the 23-hour CME day is excluded for products whose Globex day is
18:00-17:00 ET (about 3.6%; my arithmetic). Overnight holding not allowed (Builder guide FAQ).

**News, Builder plan (standard plan):** unrestricted in evaluation and sim funded. Builder guide: "News trading is
fully unrestricted during the evaluation and sim funded stage. You may open and hold positions through any scheduled
news event without limitation." News policy (mffu_art_8230009.html.txt, "August 31, 2026"): "Restricted Accounts :
Trading on T1 News events is prohibited for the following: Rapid Sim Funded / Pro Sim Funded / Unrestricted Accounts :
Trading on T1 News events is permitted for the following: All evaluations / Builder Plans". Live: "Q. Can I trade
news on my live account? A. Yes, you can trade news." (live FAQ).
- Window on restricted accounts: "No positions or orders (including limit orders) can be open 2 minutes before and
  after the release." Events: "For All Traders : FOMC Meetings, FOMC Minutes, Employment Report, CPI / For Energy
  Traders : EIA / For Agricultural Traders : Agricultural Reports". "EIA reports are released every Wednesday at
  10:30 am EST".
- Conflicts on the same page / site (flag for the lead's R score): the news policy also lists, under "Standard
  Trading Protocols ... These protocols apply to all news releases": "Ensuring no open positions or orders are active
  in the order book 2 minutes before and after any data release." The fair-play page lists "Tier 1 Economic Data
  Trading: Engaging in trades during tier 1 economic data releases is restricted." Both are general pages; the
  Builder guide (updated today) and the news page's own account list say Builder is unrestricted. Also banned on all
  accounts: "Utilizing strategies that exploit immediate news bursts, such as straddles or strangles."
- The page says "Below you will find the T1 news for all of 2026." but the calendar is an image (not machine-read).

**Product-specific restrictions:** SI, HG, PL, NG, QG restricted (section 2); metals micro cap; MBT as mini.
**2% price-limit rule** (mffu_art_9698984.html.txt, 2026-08-24), enforced in "Sim Funded Account and Live Funded
Account": "we do not allow market participation when a product is trading within 2% of a price limit"; for equity
index overnight limits "Consequently, trading is suspended at MyFunded Futures" when within 2% of the 7% limit.

## 4. Automation, order-rate and strategy rules

| Item | Finding | Source / quote |
|---|---|---|
| Automation in evaluation and sim funded | **allowed**, conditional on not exploiting sim fills | mffu_art_8444599.html.txt (fair play, 2026-08-24), "Section 1: Automated Trading Protocols / High-frequency Trading is not allowed on our plans. / Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment." |
| Automation on live | allowed under CME rules | same: "Traders trading live accounts with automated trading must abide by CME guidelines." |
| HFT | banned, **undefined** today | same quote. Earlier wording (Wayback 2025-06-26, wb_fairplay_20250626071257.html.txt): "The platform restricts the use of automated systems designed for ultra-high-frequency scalping, particularly those resulting in over 200 trades per day." and "The use of AI, bots, and other automated trading mechanisms is strictly prohibited across all account types." Replaced by the current text by the 2025-09-07 capture (wb_fairplay_20250907144859.html.txt); unchanged in captures 2025-11-27, 2026-01-04, 2026-03-30, 2026-06-10, 2026-07-18 and today. |
| Order-rate limit | none published by MFFU | no help article (77 English articles in the help sitemap, mffu_help_sitemap.xml) on rate limits, APIs or VPS |
| Trades per day | live: no limit | live FAQ: "No, there are no limits to the maximum or minimum number of trades you can have per week or per day." |
| Minimum hold / microscalping | no minimum hold published for sim; live explicitly allows microscalping | live FAQ (2025-11-10): "Yes, microscalping is permitted on the live accounts." (example trade "Duration: 5 Seconds") |
| Sim-fill exploitation | prohibited | fair play section 2: "Order Placement: Simultaneously placing multiple limit orders at the same price to manipulate order fills is prohibited." / "Gapped or Illiquid Market Trading: Initiating trades to profit from isolated fills in these markets is not allowed." / "Slippage and Bracket Usage: Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted." Consequence: "Profits generated from prohibited trading practices will be confiscated." |
| Other prohibited | hedging same underlying; collaborative/opposite trading across accounts; device sharing; copy-trading other traders; news straddles | fair play sections 2, 4, 5; terms 23.1.3.3 "use multiple accounts to hedge, mirror, copy, or coordinate trades" |
| Copiers (own accounts) | allowed (Tradesyncer, Tradovate group copier) | mffu_art_10771500.html.txt: "Tradesyncer is our preferred trade copier partner and is fully compatible with all MFFU accounts." / "Tradovate users can utilize the built-in group copier feature" |
| Firm discretion | broad | terms 23.3: "The Company reserves the right to determine, at its own discretion, whether certain trades, practices, strategies, or situations are Prohibited Conduct." |
| Which API | **no MFFU API documented.** Accounts are Tradovate accounts (login at trader.tradovate.com; NinjaTrader via "My NinjaTrader"); third-party platforms (Quantower, DeepChart, ATAS, Volumetrica) connect through a dxFeed "MyFundedFutures" connection. No Rithmic R|API, no ProjectX/TopstepX. Whether the Tradovate REST/WebSocket API is enabled for MFFU accounts is not stated by MFFU [unverified]. Pointer only: a TradersPost blog (ptr_traderspost_mffu.html, updated 2026-03-03) says MFFU accounts connect to TradersPost with Tradovate credentials; its "200+ trades/day" and "semi-automated only" claims cite the fair-play page but match only the pre-September-2025 wording, so they are stale. | mffu_art_8528337, mffu_art_8445591, mffu_art_10082979, mffu_art_10083873, mffu_art_10088299, mffu_art_10083143 |

## 5. Platforms, fill rule, VPS

- Platforms (mffu_art_8528335.html.txt, "Updated over a week ago", dateModified 2026-10-08): NinjaTrader, Hyperprop,
  Tradovate, TradingView, Quantower, Volumetrica, DeepChart/DeepDom, ATAS. Hyperprop is new ("Hyperprop is live on
  MyFundedFutures", mffu_hyperprop.html.txt; brackets "link your stop and target"). Native OCO/brackets exist on
  Tradovate (platform feature; MFFU does not document API brackets).
- Sim engine fill rule for resting limit orders: **not documented by MFFU.** The only statements: "The simulated
  market, while a robust and close approximation of live trading conditions, isn't without its disparities." and
  "Certain trading strategies may exploit the simulated fill algorithm, performing well in the evaluation stage but
  inevitably resulting in losses when transitioned to live markets." and "favorable fills offered in the Simulated
  Environment" / "absence of slippage" (fair play). One WebSearch for Tradovate's sim fill rule found no Tradovate
  documentation (only forum posts, pointers). Treat as undocumented.
- VPS: **no MFFU statement found** (help sitemap of 77 articles has no VPS/VPN article; site-restricted search found
  none). Related: "Each individual trader may not use the same device (tablet, phone or computer) as used by another
  trader." Terms 12.7.3 disclaim "any losses arising from technical issues, connectivity, latency, or outages."
  (Pointer only: sister brand MyFundedFX's help page restricts VPS use to evade copy/group rules; not MFFU.)

## 6. Reliability

| Item | Finding | Source |
|---|---|---|
| Entity | MyFunded Futures, LLC; disputes: JAMS arbitration, Collin County, Texas; courts in Collin County / E.D. Texas | mffu_terms.html.txt: "Company / We / Us: MyFunded Futures, LLC"; s.19-20 |
| Operating since | 2023 (firm footer "© 2023- 2026 MyFundedFutures"); so > 2 years on 2026-10-21. Month: third-party sources disagree (Sept 2023 per Benzinga, others June or Nov 2023) [unverified, search snippets] | mffu_whyus.html.txt l.77 |
| Payout claims (firm's claims) | "$250M+ Paid to traders"; "75%+ of payouts auto-approved in milliseconds"; "Most payouts are approved instantly. If a manual review is required, processing may take up to 6–12 business hours on weekdays."; "Trusted by over 100,000 traders" | mffu_home.html.txt l.8-11; mffu_art_13745661.html.txt |
| Program statistics (firm disclosure, measurement period not stated) | "19.97% of all evaluation participants completed the required objectives"; "39.2% of participants who reached the simulated Funded Stage earned at least one payout"; "4.2% of participants trading in a Simulated Funded Account were promoted to a Live Funded Account." | mffu_plans_builder.html.txt footer; mffu_disclaimer.html.txt l.38 ("During the applicable measurement period:") |
| Live payouts | via "our partner FCM", daily, before 11 AM ET | live FAQ |
| Regulatory actions (CFTC, NFA, FTC, state AGs) | **none found** by: WebSearch (firm name + lawsuit/CFTC/attorney general/FTC; site:cftc.gov/nfa.futures.org/ftc.gov "MyFunded") with no regulator hit; CFTC site search returned HTTP 403 (reg_cftc_search_myfunded.html), so this is a search-negative, not a registry check. NFA BASIC not queried directly (JavaScript app). Pointer: Finance Magnates via CoinSpectator (2025-07-28, mffu_news_coinspectator_20250728.html.txt): "The company, however, does not yet appear to be registered with the NFA or CFTC." and MFFU plans to become an Introducing Broker. Peers: CFTC v. My Forex Funds (different firm; court dismissal reported) [pointer]. | log.tsv |
| Payout delays / denials / disputes in the past 12 months | no firm-source or regulator evidence; third-party review aggregators only (Pipback: account closures, unfilled orders, KYC-blocked withdrawals; TheTrustedProp: no payout-denial reports) [unverified, search snippets, pointers only]. Firm side: Dispute & Chargeback Abuse Policy (mffu_art_15936848, 2026-09-02) and the profit-confiscation clause. | |

**Rule changes 2025-10-21 to 2026-10-21 (firm pages and Wayback copies; adverse/favourable is my label, the lead
decides "material"):**
1. Fee schedule raised between the 2025-10-07 and 2026-01-13 captures of the instrument list (wb_instr_*):
   MNQ/MES/M2K/MYM 1.74 -> 1.90; M6E/M6A 1.36 -> 1.44; MGC 2.04 -> 2.20; YM 5.58 -> 5.76; GC/SI/HG 5.02 -> 5.12;
   NG 4.92 -> 5.12; MET 1.00 -> 1.16; lowered: MCL 1.80 -> 1.16, MBT 6.04 -> 3.50. (adverse for most products)
2. Rapid funded split to 90%: "Earn 90% for Rapid sim funded plans as of January 12th, 2026" (favourable; not the
   standard plan).
3. "As of February 7th" (first seen in the 2026-03-30 capture, absent on 2026-01-13): temporary restriction of SI,
   HG, PL, NG, QG (and GC, restricted in the 2026-03-30 and 2026-06-10 copies, lifted by the 2026-08-04 copy). (adverse)
4. "As of April 17th" (first seen in the 2026-06-10 capture): metals micros capped at 5 on 50K. (adverse)
5. 2026-08-25: one-time payment model replaces monthly billing; new 7-calendar-day inactivity closure "This includes
   simulated funded accounts" (mffu_art_16596524). (mixed: no renewals; new inactivity closure)
6. Builder plan launched in 2026 (plan page comparison "as of May 18, 2026"); live-breach 21-day cooldown (date not
   stated); Builder guide edited today (2026-10-21, cooldown scope note only versus the E.13 copy of 2026-10-03).
7. Hyperprop platform added (platform article dateModified 2026-10-08).
8. Outside the window but relevant: automation changed from banned to allowed between 2025-06-26 and 2025-09-07.

## 7. Eligibility: British Columbia and Canada

- Canada is **not** on the restricted-countries list (mffu_art_8229993.html.txt, "Updated this week", dateModified
  2026-10-14T16:54:30Z; same list in the KYC article mffu_art_9717961, dateModified 2026-10-13). 0 hits for
  "Canada" or "British Columbia" on either page and in the terms. E.13 copy (2026-09-29 version): also no Canada.
  No province-level carve-out found. Terms s.24: "Restricted participants may only access simulated accounts, with
  limited payouts." applies to "Restricted Jurisdiction[s]" (OFAC etc.), which do not include Canada on the list.
- KYC: required "to begin trading your simulated-funded account"; Sumsub; passport/ID/driving licence, live selfie,
  proof of address "cannot be older than 3 months" (mffu_art_9717961).
- Payouts: Riseworks; "You can withdraw funds via bank transfer or cryptocurrency."; "Plaid/ACH payouts are
  available for US traders." (so not for Canadians). Payout currency: not stated (amounts are USD on every page);
  no Canada-specific payout terms found. Tax forms: 1099s are sent by Rise (US); nothing on Canadian forms.
- Purchase: Visa/Mastercard, crypto (ETH, LTC, USDT, USDC, SOL, POL, TRON); "Google Pay ... Available at certain
  states" (mffu_art_17339138).
- Live stage runs at Blue Row Capital / "partner FCM"; whether Canadians can open the live account is not stated
  [unknown].

## 8. What I could not verify

- Reset fee (no firm page); Tradovate API enablement for MFFU accounts; any order-rate limit; sim fill rule; VPS
  policy; regulator registry checks (CFTC search 403, NFA BASIC not queried); founding month; payout disputes (only
  third-party pointers); payout currency and Canadian live-account eligibility.
- Searches used: 11 of 40 WebSearch calls. No deviation fetches; no Scrapling; no Firecrawl.
