import json
B='pages/A2_mffu/'
def f(value,unit,src,quote,note=""):
    return {"value":value,"unit":unit,"source_file":B+src if src else "","quote":quote,"note":note}
G='mffu_art_14290805.html.txt'
d={"firm":"My Funded Futures (MFFU)","entity":f("MyFunded Futures, LLC","",'mffu_terms.html.txt',"Company / We / Us: MyFunded Futures, LLC, and any relevant successors and assigns."),
"lookup_date":"2026-10-21","worker":"A2_mffu",
"terms_check":f("curl allowed; no scraping clause; robots allow (help: Disallow /*=, Crawl-delay 1)","",'mffu_terms.html.txt',"","see log.tsv row TERMS"),
"plan":{
 "name":f("Builder 50K (Default MLL option)","",'mffu_home.html.txt',"Standard Standard Plans Studio Static Plans / Select your plan / $25K $50K $100K $150K / BUILDER","first plan in the default Standard tab; Add-On option has MLL 1,500 at $125"),
 "price_list":f(153,"USD one-time",G,"Price / $153 / $125"),
 "price_promo":f(92,"USD one-time",G,"Discounted Price (40% OFF - 2 uses only) / $92 / $75","30% code gives $107"),
 "billing":f("one-time payment, no renewals","",'mffu_plans_builder.html.txt',"No activation fee · One-time payment, no renewals","since 2026-08-25"),
 "activation_fee":f(0,"USD",G,"Activation Fee / $0 / $0"),
 "reset_fee":f(None,"USD","", "","unknown: no firm page states a reset price; sim-funded breach requires a new evaluation"),
 "eval":{
  "start_balance":f(50000,"USD",G,"Starting Balance / $50,000 / $50,000"),
  "profit_target":f(3000,"USD",G,"Profit Target / $3,000 / $3,000"),
  "mll":f(2000,"USD",G,"Max EOD Drawdown (MLL) / $2,000 / $1,500","Add-On 1,500"),
  "mll_type":f("EOD trailing; locks at start+100","",G,"It does not move intraday. It only adjusts after the market closes each session, based on where your account closed.","Open equity losses are counted at day end; 'The MLL locks permanently once it reaches $100 above the starting balance.'"),
  "dll":f(1000,"USD soft pause",G,"Daily Loss Limit / $1,000 - soft pause","session paused, account not breached"),
  "consistency":f(None,"",G,"Consistency Rule / None / None"),
  "min_days":f(1,"trading days",G,"Minimum Trading Days / 1 Day / 1 Day","plan page box also says 'min 2 days' (inconsistency)"),
  "time_limit":f(None,"",'mffu_art_16596524.html.txt',"If a trader does not place a trade for 7 consecutive calendar days , the account could be closed.","no time limit; 7-day inactivity rule"),
  "max_contracts":f("4 minis / 40 micros","",G,"Max Contracts / 4 Minis / 40 Micros"),
  "news":f("allowed","",G,"News Trading / Allowed"),
  "overnight":f("not allowed","",G,"No. All positions must be closed before the end of the trading session.")},
 "funded":{
  "type":f("sim-funded, then live at Blue Row Capital after 5 payouts","",G,"Once you hit your $3,000 profit target with at least 1 trading day logged, you are promoted to the Sim Funded stage."),
  "start_balance":f(0,"USD",G,"Your account begins at $0, meaning the balance can go negative before the MLL trails up to breakeven."),
  "mll":f(2000,"USD EOD trailing, floor -2000, locks at +100",G,"Max EOD Drawdown (MLL) / $2,000 / $1,500 / Starting Minimum Balance / -$2,000 / -$1,500"),
  "dll":f(1000,"USD soft pause",G,"Daily Loss Limit / $1,000 soft pause"),
  "max_contracts":f("4 minis / 40 micros","",G,"Max Contracts / 4 Minis / 40 Micros","no scaling plan stated"),
  "max_accounts":f(1,"active Builder accounts per user",G,"Only one Sim Funded account may be active per user at any time on the Builder Plan."),
  "inactivity":f(7,"calendar days",G,"Inactivity Rule / 7 Calendar Days"),
  "news":f("allowed","",G,"News trading is fully unrestricted during the evaluation and sim funded stage.")},
 "payout":{
  "split":f(0.80,"trader share",G,"Profit Split / 80% Trader / 20% Firm"),
  "buffer":f(2100,"USD",G,"Buffer (Must Be Cleared to Request) / $2,100 / $1,600"),
  "first_payout_min_profit_above_buffer":f(500,"USD",G,"For your first payout: you must have at least $500 in net profit above the buffer."),
  "later_payout_min_profit":f(500,"USD since last payout",G,"For all subsequent payouts: you must have at least $500 in net profit since your last approved payout."),
  "min_days_per_cycle":f(2,"trading days",G,"You must have traded on at least 2 trading days in the current cycle."),
  "first_request_delay":f(48,"hours after first trade",G,"You may request a payout 48 hours after your first trade has been placed"),
  "consistency":f(0.50,"max best-day share of cycle profit",G,"your single largest profit day cannot represent more than 50% of your total profits in the cycle. This calculation resets after each approved payout."),
  "min_amount":f(500,"USD gross",G,"Minimum Payout Amount / $500 / $500"),
  "max_amount":f(2000,"USD gross per cycle",G,"Maximum payout per cycle is $2,000. You keep 80% of what you withdraw."),
  "max_sim_payouts":f(5,"payouts",G,"Max Sim Payouts / 5 Payouts"),
  "processing":f("most instant; manual review up to 6-12 business hours","",'mffu_art_13745661.html.txt',"Most payouts are approved instantly. If a manual review is required, processing may take up to 6–12 business hours on weekdays."),
  "mll_after_payout":f("not stated in Builder guide","",'mffu_art_13745661.html.txt',"After your first payout, the Max Loss Limit resets to $100","older general article (2026-08-25); conservative mapping"),
  "rail":f("Riseworks: bank transfer or crypto; Plaid/ACH US only","",'mffu_art_11542406.html.txt',"Note: Plaid/ACH payouts are available for US traders.")},
 "live":{
  "trigger":f("after 5th approved sim payout","",G,"Promotion Trigger / After 5th approved sim payout"),
  "mll":f(2000,"USD EOD trailing, static once MLL reaches 0",G,"Live Account Drawdown / $2,000 EOD Trailing"),
  "dll":f(1000,"USD",G,"Daily Loss Limit (Live) / $1,000"),
  "split":f(0.80,"trader share",G,"Profit Split (Live) / 80% Trader / 20% Firm"),
  "cadence":f("daily","",G,"Live Payout Cycle / Daily"),
  "min_payout":f(250,"USD",G,"Minimum Payout Amount / $250 / $250"),
  "cooldown_after_breach":f(21,"calendar days",G,"21-Day Cooldown Period initiation: All Sim Funded account trading is prohibited.")}},
"products":{},
"position_limits":{
 "minis_micros":f("4 minis / 40 micros (10:1)","",G,"Max Contracts / 4 Minis / 40 Micros"),
 "metals_micros_cap":f(5,"micro contracts at 50K",'mffu_art_9735811.html.txt',"$50k account → maximum 5 micro contracts","since April 17 [2026]"),
 "mbt_as_mini":f(True,"",'mffu_art_9735811.html.txt',"MBT is treated as a mini contract."),
 "cross_instrument":f("combined minis+micros must stay within limit","",'mffu_art_10244682.html.txt',"Orders that combine different instruments (e.g., 2 minis and 20 micros) may technically execute even if they exceed the overall limit (e.g., more than 2 contracts in total), but this is not permitted!")},
"restrictions":{
 "hours":f("18:00 ET open to 16:10 ET auto-flat","",'mffu_art_9558251.html.txt',"Trades may be placed beginning at 6:00 PM EST when the Globex session opens and can remain open until the New York session closes at 4:10 PM EST."),
 "news_builder":f("unrestricted in eval and sim funded; live allowed","",'mffu_art_8230009.html.txt',"Unrestricted Accounts : Trading on T1 News events is permitted for the following: All evaluations / Builder Plans","conflicting general lines: news page 'Ensuring no open positions or orders are active in the order book 2 minutes before and after any data release.'; fair play 'Tier 1 Economic Data Trading: Engaging in trades during tier 1 economic data releases is restricted.'"),
 "news_restricted_accounts":f("no positions or orders 2 min before/after T1: FOMC, FOMC minutes, Employment, CPI; EIA for energy; Ag reports for ags","",'mffu_art_8230009.html.txt',"No positions or orders (including limit orders) can be open 2 minutes before and after the release.","applies to Rapid and Pro sim funded"),
 "news_burst_ban":f(True,"",'mffu_art_8230009.html.txt',"Utilizing strategies that exploit immediate news bursts, such as straddles or strangles."),
 "price_limit_rule":f("no trading within 2% of CME price limit (sim funded, live)","",'mffu_art_9698984.html.txt',"we do not allow market participation when a product is trading within 2% of a price limit"),
 "restricted_products":f(["SI","HG","PL","NG","QG"],"",'mffu_art_9735811.html.txt',"The following products are currently restricted from trading: Silver (SI) Copper (HG) Platinum (PL) Natural Gas (NG) E-Mini Natural Gas (QG)","'temporary', since February 7 [2026]"),
 "hedging_ban":f(True,"",'mffu_art_8444599.html.txt',"MyFunded Futures prohibits hedging of any kind.")},
"automation":{
 "eval_and_sim_funded":f("allowed if not exploiting sim fills","",'mffu_art_8444599.html.txt',"Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment."),
 "live":f("allowed under CME guidelines","",'mffu_art_8444599.html.txt',"Traders trading live accounts with automated trading must abide by CME guidelines."),
 "hft":f("banned, undefined","",'mffu_art_8444599.html.txt',"High-frequency Trading is not allowed on our plans.","pre-Sept-2025 wording defined >200 trades/day and banned bots (wb_fairplay_20250626071257.html.txt)"),
 "order_rate_limit":f(None,"","","","none published"),
 "min_hold":f(None,"",'mffu_art_12109396.html.txt',"Yes, microscalping is permitted on the live accounts.","no minimum hold published for sim"),
 "trade_count_live":f("no limit","",'mffu_art_12109396.html.txt',"No, there are no limits to the maximum or minimum number of trades you can have per week or per day."),
 "sim_fill_exploits_banned":f(True,"",'mffu_art_8444599.html.txt',"Slippage and Bracket Usage: Exploiting the absence of slippage and utilizing tight brackets to gain from favorable fills are not permitted.","also bans multiple limit orders at same price to manipulate fills, and isolated fills in gapped/illiquid markets"),
 "api":f("no MFFU API documented; Tradovate accounts (plus dxFeed connection for Quantower/ATAS/DeepChart/Volumetrica); no Rithmic or ProjectX","",'mffu_art_8528337.html.txt',"Access Tradovate : Head over to the Tradovate website at https://trader.tradovate.com and sign in using your credentials.","Tradovate API enablement for MFFU accounts unverified"),
 "copier":f("allowed for own accounts","",'mffu_art_10771500.html.txt',"Tradesyncer is our preferred trade copier partner and is fully compatible with all MFFU accounts.")},
"platforms":f(["NinjaTrader","Hyperprop","Tradovate","TradingView","Quantower","Volumetrica","DeepChart/DeepDom","ATAS"],"",'mffu_art_8528335.html.txt',"Platform Choices","dateModified 2026-10-08"),
"sim_fill_rule":f("undocumented","",'mffu_art_8444599.html.txt',"Certain trading strategies may exploit the simulated fill algorithm, performing well in the evaluation stage but inevitably resulting in losses when transitioned to live markets."),
"vps":f("no MFFU statement found","",'mffu_art_8444599.html.txt',"Each individual trader may not use the same device (tablet, phone or computer) as used by another trader.","device rule only"),
"reliability":{
 "operating_since":f(2023,"year",'mffu_whyus.html.txt',"© 2023- 2026 MyFundedFutures. All rights reserved.","month unverified"),
 "paid_claim":f("$250M+","USD paid to traders (firm claim)",'mffu_home.html.txt',"$250M+ / Paid to traders"),
 "program_stats":f({"eval_pass":0.1997,"funded_with_payout":0.392,"promoted_live":0.042},"share",'mffu_disclaimer.html.txt',"39.2% of participants who reached the simulated Funded Stage earned at least one payout","measurement period not stated"),
 "regulatory_actions":f("none found (search-negative; CFTC search 403; NFA BASIC not queried)","","","","pointer: Finance Magnates 2025 says not registered with NFA/CFTC"),
 "payout_disputes_12m":f("no firm or regulator evidence; third-party review pointers only","","","","[unverified]"),
 "rule_changes_12m":f(["fee schedule raised (most products) between 2025-10-07 and 2026-01-13 captures","Rapid split 90% from 2026-01-12","2026-02-07 temporary restriction SI/HG/PL/NG/QG (GC until mid-2026)","2026-04-17 metals micro cap 5 at 50K","2026-08-25 one-time payment model and 7-day inactivity closure","Builder plan launched 2026; live-breach 21-day cooldown","Hyperprop platform added Oct 2026"],"",'wb_instr_20260330022839.html.txt',"As of February 7th:","see md section 6")},
"eligibility":{
 "canada_bc":f("accepted (Canada not on restricted list)","",'mffu_art_8229993.html.txt',"Restricted Countries List:","0 hits for Canada; dateModified 2026-10-14"),
 "kyc":f("Sumsub; ID, selfie, proof of address <= 3 months; before sim funded trading","",'mffu_art_9717961.html.txt',"It is a prerequisite to begin trading your simulated-funded account."),
 "payout_methods_canada":f("Riseworks bank transfer or crypto (ACH is US-only); currency not stated","",'mffu_art_11542406.html.txt',"You can withdraw funds via bank transfer or cryptocurrency.")}}
inst=json.load(open('work/A2_mffu/A2_mffu_instr_today.json'))
restricted={"SI","HG","NG","QG","PL"}
for k in ['MNG','QG','NG','MCL','QM','CL','MGC','GC','SIL','SI','MHG','HG','M6E','6E','M6A','6A','MET','ETH','MBT','BTC','M2K','RTY','MYM','YM','MNQ','NQ','2YY','5YY','10Y','30Y','ZT','ZF','ZN','ZB','MZC','MZS','MZW','MZL','MZM','XC','XK','XW','ZC','ZS','ZW','ZL','ZM']:
    v=inst.get(k)
    if not v:
        d["products"][k]={"allowed":f(False,"",'mffu_art_9735811.html.txt',"","not on the firm's instrument list"),"rt":f(None,"USD","","","")}
        continue
    rt=float(v['rt'].strip('$'))
    q=f"{v['name']} | {k} | ... | {v['tick_size']} | {v['tick_value']} | {v['rt']}"
    d["products"][k]={"allowed":f(k not in restricted,"",'mffu_art_9735811.html.txt',q,"currently restricted" if k in restricted else ""),
      "rt":f(rt,"USD per round trip",'mffu_art_9735811.html.txt',q,"Total Cost Round Trip (commission + fees)"),
      "per_side":f(round(rt/2,3),"USD per side",'mffu_art_9735811.html.txt',q,"derived RT/2")}
json.dump(d,open('A2_firm_mffu.json','w'),indent=1,ensure_ascii=False)
print(len(d["products"]))
