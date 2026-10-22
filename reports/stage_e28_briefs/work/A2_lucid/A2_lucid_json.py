import json
P="reports/stage_e28_briefs/pages/A2_lucid/"
def f(value,unit,src,quote,note=""):
    return {"value":value,"unit":unit,"source_file":P+src if src else None,"quote":quote,"note":note}
HOME="lucid_home_wb.html"
comm_src="sup_products_commissions.html.txt"
comm={"QG":1.30,"NG":2.00,"MCL":0.50,"QM":2.00,"CL":2.00,"MGC":0.80,"GC":2.30,"SIL":1.60,"SI":2.30,"HG":2.30,"6E":2.40,"6A":2.40,
      "M2K":0.50,"RTY":1.75,"MYM":0.50,"YM":1.75,"MNQ":0.50,"NQ":1.75,"ZC":2.80,"ZS":2.80,"ZW":2.80,"ZL":2.80,"ZM":2.80}
names={"QG":"E-mini Natural Gas Futures","NG":"Henry Hub Natural Gas Futures","MCL":"Micro Crude Oil","QM":"E-mini Crude Oil Futures","CL":"Crude Oil Futures",
 "MGC":"Micro Gold Futures","GC":"Gold Futures","SIL":"Micro Silver","SI":"Silver","HG":"Copper Futures","6E":"Euro FX Futures","6A":"Australian Dollar Futures",
 "M2K":"Micro E-mini Russell 2000 Index Futures","RTY":"E-mini Russell 2000 Index Futures","MYM":"Micro E-mini Dow Jones Industrial Average Index Futures",
 "YM":"E-mini Dow ($5) Futures","MNQ":"Micro E-mini Nasdaq-100 Index Futures","NQ":"E-mini Nasdaq-100 Futures","ZC":"Corn Futures","ZS":"Soybean Futures",
 "ZW":"Chicago SRW Wheat Futures","ZL":"Soybean Oil Futures","ZM":"Soybean Meal Futures"}
exch={"QG":"NYMEX","NG":"NYMEX","MCL":"NYMEX","QM":"NYMEX","CL":"NYMEX","MGC":"COMEX","GC":"COMEX","SIL":"COMEX","SI":"COMEX","HG":"COMEX","6E":"CME","6A":"CME",
 "M2K":"CME","RTY":"CME","MYM":"CBOT","YM":"CBOT","MNQ":"CME","NQ":"CME","ZC":"CBOT","ZS":"CBOT","ZW":"CBOT","ZL":"CBOT","ZM":"CBOT"}
order=["MNG","QG","NG","MCL","QM","CL","MGC","GC","SIL","SI","MHG","HG","M6E","6E","M6A","6A","MET","ETH","MBT","BTC","M2K","RTY","MYM","YM","MNQ","NQ",
 "2YY","5YY","10Y","30Y","ZT","ZF","ZN","ZB","MZC","MZS","MZW","MZL","MZM","XC","XK","XW","ZC","ZS","ZW","ZL","ZM"]
products={}
for c in order:
    if c in comm:
        q=f"{c} / {names[c]} / {comm[c]:.2f} / {exch[c]}"
        products[c]={"allowed":f(True,"bool",comm_src,q,"approved-products table; same row in deviation fetch 2026-10-21"),
                     "commission_per_side":f(comm[c],"USD per contract per side",comm_src,q,"column 'Commission (Per Side)'; inclusion of exchange/NFA fees not stated"),
                     "commission_round_trip":f(round(2*comm[c],2),"USD per round trip",comm_src,q,"2 x per side (worker arithmetic)")}
    else:
        products[c]={"allowed":f(False,"bool",comm_src,"Futures products approved for trading at Lucid Trading and the commission rates per contract","not in the 34-row approved table (Wayback 2026-09-22; deviation fetch 2026-10-21 identical)"),
                     "commission_per_side":f(None,"USD",None,None,"not approved"),"commission_round_trip":f(None,"USD",None,None,"not approved")}
d={
 "firm":"Lucid Trading","lookup_date":"2026-10-21","root":"A2_lucid",
 "access":{
  "terms_decision":f("no automated access to lucidtrading.com or support.lucidtrading.com; Wayback, snippets, one deviation WebFetch per page","text","lucid_tou_wb.html.txt","Use any robot, spider, or other automatic device, process, or means to access the Website for any purpose, including monitoring or copying any of the material on the Website.","TOU Last Modified: March 20, 2025"),
  "pricing_page_today":f("HTTP 403 to WebFetch on 2026-10-21; latest Wayback 200 copy 2026-10-05","text",None,None,"today's price unverified; 16-day-old capture used"),
 },
 "plan":{
  "name":f("LucidPro 50K","text",HOME,'"id":"pro","slug":"lucidpro","label":"LucidPro","headerSuffix":"PRO EVAL","order":10,"enabled":true',"first plan type (order 10) in LucidPricingConfig; Wayback 20261005200451; lead to confirm vs visible label list"),
  "price":f(172,"USD one-time",HOME,'"1661":"172"',"one_time_fee cell s50k = product 1661; DLL ON version; Wayback 2026-10-05"),
  "billing":f("one-time","text","sup_sim_fees.html.txt","LucidPro Evaluation and LucidDirect accounts are purchased by paying a one-time fee. There is no subscription and no automatic rebilling.","updated 2026-08-26"),
  "price_dll_off":f(192,"USD one-time",HOME,'"addonFees":{"56539":15,"1661":20',"inference: +20 add-on for DLL OFF"),
  "discount":f(30,"percent with code VAULT",HOME,'"couponCode":"VAULT","resetDiscountPct":0',"config discountPct 30 per size; 172*0.7=120.40 is an inference"),
  "reset_fee":f(120,"USD",HOME,'"9789":"120"',"reset_fee cell s50k = product 9789; +20 if DLL OFF (inference)"),
  "activation_fee":f(0,"USD","sup_sim_fees.html.txt","There is no activation fee to upgrade a LucidPro Evaluation to a LucidPro Funded.",""),
  "profit_target":f(3000,"USD","sup_pro_eval.html.txt","$50,000 / $3,000 / $2,000 / $1,200 / 4 mini or 40 micros","table row; updated 2026-08-26"),
  "max_loss_limit":f(2000,"USD","sup_pro_drawdown.html.txt","$50,000 / $2,000 / $52,100 / $50,100","MLL / Initial Trail Balance / Locked MLL Balance"),
  "max_loss_limit_type":f("end-of-day trailing, locks at 50,100 once balance exceeds 52,100","text","sup_pro_drawdown.html.txt","LucidPro evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system to calculate the Max Loss Limit (MLL).","breach test: 'If your account balance reached the MLL, your account will be breached.' (intraday vs EOD not stated)"),
  "daily_loss_limit":f(1200,"USD, soft","sup_pro_dll.html.txt","All DLLs at Lucid Trading are considered soft breaches, meaning you do not lose your account for hitting DLL as long as the Max Loss Limit (MLL) has not been reached.","optional; DLL OFF version has none"),
  "consistency_eval":f(None,"percent","sup_pro_eval.html.txt",None,"none published for LucidPro eval (Flex/Daily evals: 50%)"),
  "min_days_eval":f(1,"trading days","sup_pro_eval.html.txt","Pass the evaluation in one trading day",""),
  "time_limit":f(None,"days","sup_pro_eval.html.txt","One-time fee, no monthly rebilling, take as long as you need to pass","inactivity: deleted after 30 calendar days without $1 net P&L (sup_inactivity)"),
  "max_size":f("4 minis or 40 micros","contracts","sup_pro_eval.html.txt","4 mini or 40 micros","ratio 1:10"),
 },
 "funded":{
  "type":f("simulated","text","sup_pro_funded.html.txt","The LucidPro funded account is a simulated account where traders build simulated capital to earn payouts and potentially be moved to live markets.",""),
  "drawdown":f(2000,"USD EOD trailing, lock 50,100","sup_pro_drawdown.html.txt","Once your account exceeds the Initial Trail Balance, the MLL locks and no longer moves",""),
  "daily_loss_limit":f("1,200 fixed below 52,100; then 60% of highest EOD profit (never decreases)","USD","sup_pro_dll.html.txt","Highest end-of-day account profit × 60% = LucidScale DLL","soft; optional"),
  "profit_split":f(0.90,"trader share","sup_pro_payouts.html.txt","All funded account payouts are split 90% to the trader and 10% to Lucid Trading.","accounts bought/reset before 2025-11-28 15:00 EST keep 100% of first $10k"),
  "min_profit_per_cycle":f(500,"USD","sup_pro_payouts.html.txt","$50,000 / $500","resets after each payout"),
  "consistency":f(40,"percent max single day of cycle profit","sup_pro_payouts.html.txt","Your largest single-day profit must be no more than 40% of your total profit during the payout cycle.",""),
  "buffer":f(52100,"USD balance","sup_pro_payouts.html.txt","The buffer is equal to: Initial Max Loss Limit + $100","cannot withdraw from buffer"),
  "min_payout":f(500,"USD","sup_pro_payouts.html.txt","Minimum payout request: $500",""),
  "max_payout_first":f(2000,"USD","sup_pro_payouts.html.txt","$50,000 / $52,100 / $500 / $52,600 / $2,000 / $54,100","Payout 1 table"),
  "max_payout_2plus":f(2500,"USD","sup_pro_payouts.html.txt","$50,000 / $52,100 / $500 / $52,600 / $2,500 / $54,600","Payouts 2+ table"),
  "days_to_payout":f(3,"days",HOME,'"label":"Days to Payout","kind":"text","cells":{"s25k":"3","s50k":"3","s100k":"3","s150k":"3"}',"pricing config, Pro funded"),
  "payout_frequency":f("any day once criteria met; disbursed within 2 business days","text","sup_pro_payouts.html.txt","There is no fixed payout window, you may request a payout any day after meeting all eligibility criteria.",""),
  "max_number_of_payouts":f(5,"payouts","sup_new_live.html.txt","Payout 5 represents the maximum payout level, not a guaranteed minimum for live eligibility. This maximum payout level applies to Flex, Pro, and Direct plans.","then live review pool; Pro payouts page states no count"),
  "scaling_plan":f(None,"none","sup_pro_funded.html.txt","No scaling plan, access to max contract size immediately",""),
  "max_size":f("4 minis or 40 micros","contracts","sup_pro_funded.html.txt","4 mini or 40 micros",""),
  "max_funded_accounts":f(5,"per household","sup_max_accounts.html.txt","Up to 5 active funded accounts per household or family.","10 evals, 10 total"),
  "live_stage":f("discretionary; $0 start, $2,000 EOD drawdown, daily payouts, no DLL, 90/10","text","sup_new_live.html.txt","All live transitions occur at the discretion of the Lucid risk team.","cashout option = 50% of live starting balance"),
 },
 "products":products,
 "position_limit_50k":f("4 minis or 40 micros (1:10); no sim product-specific cut","contracts","sup_pro_funded.html.txt","4 mini or 40 micros","live: COMEX reduced (sup_live_scaling)"),
 "restrictions":{
  "news_pro":f("allowed, no window","text","sup_other_activities.html.txt","Allowed on Flex, Pro and Direct","LucidDaily: red folder news is a hard breach"),
  "flat_by":f("16:45 ET Mon-Fri; reopen 18:00 ET Sun-Thu","time","sup_trading_times.html.txt","All positions must be closed by 4:45 PM EST, Monday through Friday","auto-closed, not a failure; holidays: before market close"),
  "product_specific":f(None,"none found","sup_products_commissions.html.txt",None,"none in sim stages"),
 },
 "automation":{
  "allowed":f(True,"bool","sup_other_activities.html.txt","Automated trading systems and trade copiers are permitted","firm-wide; no eval/funded distinction stated"),
  "api":f(None,"unknown",None,None,"no Lucid page names Tradovate API, Rithmic R|API, ProjectX or NinjaTrader API; [snippet] secondary claims only"),
  "hft":f("banned, qualitative definition","text","sup_hft.html.txt","HFT strategies can result in hundreds of orders being placed within minutes","no numeric threshold"),
  "microscalping":f("flag if >50% of profits from trades held <=5 s","rule","sup_microscalping.html.txt","More than 50% of your profits are generated from trades held for 5 seconds or less","unchanged since 2026-03-30 copy"),
  "scalping":f(True,"bool","sup_other_activities.html.txt","Genuine scalping is allowed",""),
  "order_rate_limit":f(None,"unknown",None,None,"none published"),
  "sim_fill_exploitation_ban":f("banned","text","lucid_tou_wb.html.txt","While utilizing the Website, Software, and Services, taking advantage of the simulated environment to gain an edge is not permitted.","also sup_integrity: 'Exploiting discrepancies in simulated prices'"),
 },
 "platforms":{
  "list":f("CQG: NinjaTrader, Tradovate, TradingView; Rithmic: MotiveWave, Quantower, Tradesea, Sierra Chart, Jigsaw, Bookmap, ATAS, R|Trader Pro, MultiCharts","text","sup_platforms2.html.txt","All listed platforms work with all Lucid account types.","updated 2026-07-28"),
  "sim_fill_rule":f(None,"undocumented",None,None,"no Lucid page documents it; Rithmic paper-trading queue claim is a forum pointer only"),
  "vps":f(None,"unknown",None,None,"no Lucid page mentions VPS"),
 },
 "reliability":{
  "operating_since":f("2025 (waitlist page on 2025-02-20; domain for sale 2024-09-01)","date","lucid_home_wb_20250220204435.html","Sign up now to join our waitlist and receive our exclusive launch discount.","under 2 years at lookup"),
  "firm_claims":f("$700M+ earned by traders; 15ish min from request to bank","claim",HOME,"$700M+","unaudited firm claims"),
  "regulatory_actions":f(None,"none found",None,None,"WebSearch + Firecrawl gov search; NFA BASIC not queried"),
  "disputes":f("review-site complaints (closures after payout approval, KYC locks)","pointer",None,None,"[snippet] Trustpilot/PropFirmMatch; not evidence"),
  "rule_changes_12m":f(["2025-11-28 split 100% first $10k -> 90/10","2025-11-28 Pro funded consistency 35% -> 40%","50K eval $135 list (2025-11-01) -> $172 (2026-10-05); reset $90 -> $120","LucidBLACK legacy, LucidDaily/LucidMaxx added, new Live structure 2026-10-14","news: LucidDaily ban added 2026-07..08","Payout 5 maximum (start date unknown)"],"list","sup_pro_payouts.html.txt","Accounts purchased or reset before 11/28/2025 at 3:00 PM EST are still eligible for 100% on the first $10k.","see md section 6 for each source"),
 },
 "eligibility":{
  "canada_bc":f(True,"accepted (not restricted)","sup_restricted_countries.html.txt","If you are a citizen or resident of any of the countries listed below, you are not eligible to use Lucid Trading services:","Canada absent; TOU says site is for persons in the US (line 190)"),
  "payout_methods":f("WorkMarket by ADP (bank transfer or PayPal) or crypto for international","text","sup_payout_methods.html.txt","Available for both U.S. and international traders","currency not stated"),
  "kyc":f("at payout when required by provider","text","lucid_general_faq_wb.html.txt","Yes — at the time of payout when required by the payout provider.",""),
 },
}
json.dump(d,open("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A2_firm_lucid.json","w"),indent=1,ensure_ascii=False)
print("ok",len(products))
