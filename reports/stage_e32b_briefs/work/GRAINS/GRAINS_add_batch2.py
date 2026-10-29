import json
P='reports/stage_e32b_briefs/pages/GRAINS/'
items=[
 dict(id="GRAINS-15",codes=["ZS","ZM","ZL","XK","MZS","MZM","MZL"],topic="T3",field="relationship",value="soybean crush (ZS vs ZM and ZL): intraday cointegration at 1-minute sampling in the day session",scope="underlying",
  window="calendar 2015, 243 trading days, CME LOB data",
  detail="Type: economic spread. Zhou, Bagnarosa, Gohin, Pennings, Debie (2023) J. Commodity Markets 30, 100314 (peer-reviewed; open-access copy). Day session (08:30-13:20 CT, 'session 2'), 1-minute data, missing-data filtered: cointegrated on 180 of 243 days (Table 2), 229 days at 2-minute sampling (NCCC-134 2022 version); Johansen without filtering only 64-70 days. Overnight 'session 1' (19:00-07:45 CT): 52 days (NCCC version Table 7). Speed of reversion related to volume and liquidity; stronger cointegration on USDA days. Horizon: minute-level, within-day. No half-life or trading test reported. In sample.",
  quote="A high level of cointegration is indeed observed during session 2 trading hours, which fades away during session 1. Another interesting result is the stronger intraday cointegration observed on average on USDA announcement days, although the number of observations available is limited.",
  source={"file":P+"wur_edepot_629433.pdf","field":"text lines 744-747; Table 2 'Missing data filtered cointegration test ... ZS open interest rollover 180 11 3'"},verified="full_text"),
 dict(id="GRAINS-16",codes=["ZS","ZM","ZL","XK","MZS","MZM","MZL"],topic="T3",field="relationship",value="soybean crush: overnight session cointegration on 52 days vs 180 in the day session (1-minute, 2015)",scope="underlying",
  window="2015",
  detail="NCCC-134 2022 conference version of GRAINS-15 (working paper). Table 7 'Cointegration Summary of Session 1': ZS open interest rollover 52 days, 2 months, 1 quarter. Two-minute data: 229 cointegrated days in session 2.",
  quote="cointegration is mainly playing during session 2 (market official trading hours) of a trading day and significantly less so during session 1 (electronic trading hours). In addition, prices in session 1 are so greatly affected by market noise that even the combining of both sessions yields no additional information",
  source={"file":P+"zhou_etal_nccc134_2022.pdf","field":"lines 2647-2652, 2681-2684, 2756-2757"},verified="full_text"),
 dict(id="GRAINS-17",codes=["ZC","XC","MZC"],topic="T7",field="session_handoff",value="settlement-window reversals: pre-close to settlement price moves reversed at next open less often after the 2012 settlement-rule change",scope="product",
  window="CBOT corn, March-June 2012 (before/after 2012-06-25)",
  detail="Onur and Reiffen (CFTC working paper, Jan 2018) 'The Effect of Settlement Rules on the Incentive to Bang the Close'. Horizon: settlement minute to next-day open (overnight/daily, not intraday 5-min+). Before 2012-06-25 the settlement period was 13:14-13:15 CT (floor only). Evidence of a settlement-window effect that weakened; variance-ratio random walk after the change. Old data.",
  quote="We find that reversals became less common after the rule change. The aggregate statistics also show that settlement prices become more efficient after the change.",
  source={"file":P+"onur_reiffen_cftc.pdf","field":"lines 200-207, 532-536"},verified="full_text"),
]
with open('reports/stage_e32b_briefs/work/GRAINS/GRAINS_items.jsonl','a') as fh:
    for it in items: fh.write(json.dumps(it,ensure_ascii=False)+'\n')
