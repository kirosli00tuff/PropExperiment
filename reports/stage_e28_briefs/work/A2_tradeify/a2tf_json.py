import json
P="reports/stage_e28_briefs/pages/A2_tradeify/"
E13="reports/stage_e13_briefs/pages/PropVenues1/"
def f(v,u,s,q,n=""): return {"value":v,"unit":u,"source_file":s,"quote":q,"note":n}
comm_q='"All costs are per contract round trip (both sides of the trade)"; "Total Round Trip Cost includes Exchange fees, NFA fees, Clearing fees, and Commissions."'
fees={"QG":4.00,"NG":6.20,"MCL":2.12,"QM":5.40,"CL":5.98,"MGC":2.12,"GC":6.20,"SI":6.20,"HG":6.20,"M6E":1.60,"6E":6.20,"M6A":1.60,"6A":6.20,"M2K":1.82,"RTY":5.76,"MYM":1.82,"YM":5.76,"MNQ":1.82,"NQ":5.76,"ZC":7.20,"ZS":15.20,"ZW":17.20,"ZL":7.20,"ZM":9.20}
notlisted={"MNG":"no micro natural gas listed","SIL":"explicitly unsupported: \"The CME 1,000 oz Micro Silver (SIL) is not a Tradeify-supported product.\"","MHG":"\"The only micro metal Tradeify supports is MGC.\"","MET":"crypto: \"Tradeify does not support any cryptocurrency derivatives, including Bitcoin futures.\"","ETH":"crypto (same quote)","MBT":"crypto (same quote)","BTC":"crypto (same quote)","2YY":"no US rates listed","5YY":"no US rates listed","10Y":"no US rates listed","30Y":"no US rates listed","ZT":"no US rates listed","ZF":"no US rates listed","ZN":"no US rates listed","ZB":"no US rates listed","MZC":"micro grains not listed","MZS":"micro grains not listed","MZW":"micro grains not listed","MZL":"micro grains not listed","MZM":"micro grains not listed","XC":"not listed","XK":"not listed","XW":"not listed"}
products={}
for k,v in fees.items():
    products[k]={"allowed":f(True,"bool",P+"tf_wf_products.txt; "+P+"tf_products_wb.tables.txt","product listed in the supported-products tables","firm-wide list, applies to the 50K plans"),
                 "fee_rt":f(v,"USD per contract round trip",P+"tf_wf_comm.txt; "+P+"tf_comm_wb.html.body.txt",comm_q,"today (deviation fetch); CL was 6.00 on 2026-07-09 Wayback" if k=="CL" else "today (deviation fetch); same on 2026-07-09 Wayback raw"),
                 "fee_side":f(round(v/2,3),"USD per contract per side","derived","", "RT/2, derived; firm quotes round trips only")}
for k,n in notlisted.items():
    products[k]={"allowed":f(False,"bool",P+"tf_wf_products.txt; "+P+"tf_products_wb.tables.txt","\"Never assume a micro version of a standard contract exists — only products listed in the tables above are supported.\"",n),
                 "fee_rt":f(None,"USD","","","not listed"),"fee_side":f(None,"USD","","","not listed")}
out={
 "firm":"Tradeify","lookup_date":"2026-10-21","root":"A2_tradeify",
 "access":f("Wayback copies + E.13 copies + deviation WebFetch via intercom.help/tradeify mirror","text",P+"log.tsv","use any robot, spider, scraper or other automatic device ... to access, harvest, monitor, copy or use the Site without the express written permission of Tradeify","terms forbid automation; help.tradeify.co 403s WebFetch; deviation fetches are model-extracted quotes, listed in DO_NOT_COMMIT.txt"),
 "plan":{
  "name":f("Growth 50K","text",P+"tf_home_wb.html.txt; "+P+"tf_wf_pricing.txt","Growth | Pass in 1 day ... Select | Pass in 3 days ... Lightning | Instant","first-listed 50K evaluation plan; selection under the spec rule is the lead's"),
  "price":f(145,"USD one-time",P+"tf_wf_pricing.txt","Growth 50K | $145 | $95","list price; promo codes frequent"),
  "billing":f("one-time","text",P+"tf_wf_pricing.txt","All plans are one-time purchases with no recurring billing."),
  "reset_fee":f(95,"USD",P+"tf_wf_pricing.txt","Growth 50K | $145 | $95"),
  "activation_fee":f(0,"USD",P+"tf_wf_pricing.txt","There are no activation fees for any current Tradeify account type."),
  "profit_target":f(3000,"USD",P+"tf_growth_eval_wb.html.body.txt","$50k | $3,000 | $1,250 | $2,000 | 4 Contracts (40 Micros)","raw Wayback 2026-10-14; confirmed today tf_wf_growth_eval.txt"),
  "max_loss_type":f("EOD trailing (updates at end of day, enforced intraday on net liquidation; no lock in evaluation)","text",P+"tf_growth_eval_wb.html.body.txt","The GROWTH™ evaluation uses an End of Day Trailing Max Drawdown, which is based on the account balance at the end of the trading day."),
  "max_loss":f(2000,"USD",P+"tf_growth_eval_wb.html.body.txt","$50k | $3,000 | $1,250 | $2,000 | 4 Contracts (40 Micros)"),
  "daily_loss_limit":f(1250,"USD, soft breach",P+"tf_growth_eval_wb.html.body.txt","If you hit it, trading stops for the day but your account is not failed."),
  "consistency_eval":f(None,"none",P+"tf_growth_eval_wb.html.body.txt","A: No. GROWTH™ evaluation does NOT have a consistency requirement.","E.13 2026-10-03 copy said 35%: changed"),
  "min_days":f(1,"trading days",P+"tf_growth_eval_wb.html.body.txt","Minimum Trading Days | 1 day (can pass immediately)"),
  "time_limit":f(None,"none",P+"tf_growth_eval_wb.html.body.txt","There is no deadline to hit the profit target","weekly activity rule applies"),
  "position_limit":f("4 minis or 40 micros, combined at 10:1","contracts",P+"tf_wf_essential.txt","10 Micro contracts = 1 Mini contract","5/50 for accounts bought before 2025-09-12"),
  "flat_by":f("16:45 ET (12:59 ET holiday early close)","time",P+"tf_wf_essential.txt","Close all positions by 4:45 PM Eastern Time (Monday-Friday)"),
  "monthly_eval_cap":f(15,"evaluations per month",E13+"tf_pricing.txt","it does not count toward the 15-evaluation monthly limit","2026-10-03 copy"),
 },
 "funded":{
  "type":f("simulated (Sim Funded); may be moved to Live after any payout","text",P+"tf_growth_payout_wb.html.body.txt","Tradeify reserves the right to move you to a Live Funded Account at any time after a successful payout."),
  "start_balance":f(50000,"USD","reports/stage_e28_briefs/pages/A2_tradeify/tf_getfunded_wb.html.body.txt","Your funded account starts at your base account size ($50K, $100K, or $150K) regardless of your evaluation ending balance."),
  "max_loss":f("EOD trailing 2,000; locks at floor 50,100 when EOD balance >= 52,100 or at first payout request","USD",E13+"tf_drawdown.txt","A 50K Growth account with $2,000 drawdown locks when EOD balance reaches $52,100. The drawdown floor becomes $50,100 and never moves up again.","2026-10-03 copy (dateModified 2026-08-26)"),
  "daily_loss_limit":f(1250,"USD, soft breach",P+"tf_wf_essential.txt","Growth Accounts: Daily loss limit varies by account size ($1,250 for $50k, $2,500 for $100k, $3,750 for $150k)"),
  "split":f(0.90,"trader share",P+"tf_growth_payout_wb.html.body.txt","Traders receive 90% of the payout amount requested.","Elite Live 80%"),
  "min_balance_to_request":f(53000,"USD",P+"tf_growth_payout_wb.html.body.txt","$50,000 | $53,000"),
  "payout_caps":f([1500,2000,2500,3000],"USD per request, payout 1,2,3,4+",P+"tf_growth_payout_wb.html.body.txt","These are hard caps — even if your account balance is higher, you can only withdraw up to the amount shown for that payout number"),
  "min_payout":f(500,"USD",P+"tf_growth_payout_wb.html.body.txt","$500 for $50k accounts"),
  "winning_days":f(5,"days with profit > 150 USD per payout cycle",P+"tf_growth_payout_wb.html.body.txt","Minimum Trading Days: 5 or more of the Trading Days must show a profit greater than: ... $150 in profit for 50k accounts","count resets after each payout"),
  "consistency":f(0.35,"max share of one day in total profit",P+"tf_growth_payout_wb.html.body.txt","Consistency Rule: Abide by the 35% Consistency Rule","exact formula in Consistency Rule article, not fetched"),
  "microscalping":f(">50% of trades and >50% of profit from holds >10 s, payout gate","rule",P+"tf_guidelines_wb.html.body.txt","Over 50% of your trades are longer than 10 seconds / Over 50% of your profit must come from trades held longer than 10 seconds."),
  "frequency":f("when conditions met; one open request per account","text",P+"tf_growth_payout_wb.html.body.txt","Payout requests can be submitted directly from your dashboard once payout conditions have been met."),
  "processing":f("24-48 h after approval; up to 72 h outside business hours","hours",P+"tf_growth_payout_wb.html.body.txt","Payments will be issued within 24-48 hours after the withdrawal has been processed."),
  "scaling":f("none for Growth","text",P+"tf_wf_essential.txt","Growth and Lightning use their maximum position size from day one; Select funded accounts scale up as the account grows"),
  "max_accounts":f(5,"sim funded accounts per household",P+"tf_wf_pricing.txt","The 5-account cap applies to active Sim Funded accounts per household."),
  "reset":f(False,"bool",P+"tf_growth_eval_wb.html.body.txt","the Simulated Funded counterpart cannot be reset."),
 },
 "products":products,
 "restrictions":{
  "news":f("none","text",P+"tf_news_wb.html.body.txt; "+P+"tf_wf_essential.txt","We do not have any rules against or guidelines around trading news events."),
  "product_specific":f("none found","text","","","EUREX Tradovate only; hedging rule firm-wide"),
  "hours":f("Globex 18:00-17:00 ET; flat by 16:45 ET; no overnight or weekend holds","text",P+"tf_wf_essential.txt","A trading day runs from 6:00 PM ET to 5:00 PM ET the next calendar day."),
 },
 "automation":{
  "bots_allowed":f("yes, own non-HFT bots, eval and funded","text",P+"tf_guidelines_wb.html.body.txt","At Tradeify, we allow the use of bots and algorithms under certain conditions:"),
  "api":f("Tradovate API only on LIVE funded; none in eval/sim funded; Rithmic API unstated; no ProjectX","text",P+"tf_products_wb.tables.txt","The Tradovate API is only available for LIVE funded accounts. It is not available for evaluation or sim funded accounts."),
  "order_rate_limit":f(None,"none published","","","HFT banned without threshold"),
  "min_hold":f("10 s rule (>50% trades and profit), funded payout gate","rule",P+"tf_guidelines_wb.html.body.txt","This rule applies to funded accounts only. It does not apply during an evaluation.","news article says it also gates evaluation activation: conflict"),
  "sim_exploit":f("prohibited","text",P+"tf_wf_riskfaq.txt","exploitation of simulated conditions"),
 },
 "platform":{
  "brokers":f(["Tradovate","Rithmic","WealthCharts"],"list",P+"tf_platforms_wb.html.body.txt","Tradeify supports three broker connections: Tradovate, Rithmic, and WealthCharts."),
  "sim_fill_rule":f(None,"undocumented","","","no Tradeify or Tradovate statement found"),
  "vps":f("conditionally prohibited (where it obscures verification)","text",E13+"tf_terms.txt","use a Virtual Private Server (“VPS”), virtual machine, virtualized environment, remote computing environment, or similar technology ... where such technology obscures, alters, masks, or prevents Tradeify from reliably verifying"),
 },
 "reliability":{
  "operating_since":f("<= 2022-12-05","date",P+"tf_home_2022_wb.html.txt","Tradeify – Accessible trading education and funding","interview says futures prop launched 2024 (pointer)"),
  "payout_claims":f("Over $350 million in verified payouts; 1 hour payouts","claim",P+"tf_home_wb.html.txt","Over $350 million in verified payouts"),
  "funded_payout_rate":f(0.285,"share of funded participants paid, Aug 2025-Jul 2026",P+"tf_home_wb.html.txt","(c) 28.5% of individual participants at the Funded Level received a payout"),
  "eval_pass_rate":f(0.172,"share of evaluation accounts passed",P+"tf_home_wb.html.txt","(a) 17.2% of evaluation accounts initiated were successfully completed"),
  "regulatory_actions":f("none found","text","","","Firecrawl gov search + WebSearch; NFA BASIC unread; absence is a gap"),
  "disputes_12m":f("review-site reports only (pointer)","text","","","thetrustedprop.com, PropFirmMatch [snippet]"),
  "rule_changes_12m":f(["Tradeify 3.0 (~2026-04): subscriptions ended, ~3% price rise, Select 50K target 2,500->3,000","Growth eval consistency removed (2026-10)","Growth 100K/150K reset fees up (2026-10)","CL fee 6.00->5.98","VPS clause / Risk & Compliance FAQ (~2026-09)"],"list","A2_firm_tradeify.md section 6.4","","see md for sources"),
 },
 "eligibility":{
  "bc_canada":f("accepted by omission (not restricted)","text",P+"tf_wf_restricted.txt","The page does not mention Canada, British Columbia, Quebec, Ontario, or any US state."),
  "canada_payout_terms":f("none specific; Rise (bank ACH, crypto, local currencies) or Plane; Sumsub + Rise KYC; CAD unstated","text",P+"tf_kyc_wb.html.body.txt; "+P+"tf_rise_wb.html.body.txt","Local Currencies - Varies by region"),
 },
}
json.dump(out,open("reports/stage_e28_briefs/A2_firm_tradeify.json","w"),indent=1,ensure_ascii=False)
print(len(products))
