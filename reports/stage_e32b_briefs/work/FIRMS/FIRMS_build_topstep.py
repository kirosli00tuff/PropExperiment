import sys
sys.path.insert(0, '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/FIRMS')
from FIRMS_lib import E, save_firm
T = 'reports/stage_e28_briefs/A2_firm_topstep.json:'
P = 'reports/stage_e28_briefs/A3_firm_products.json:pairs[firm=topstep]'
listed = ['MCL','QM','CL','MNG','QG','NG','MGC','GC','SIL','MHG','M6E','6E','M6A','6A','MET','MBT','M2K','RTY','MYM','YM','MNQ','NQ','ZT','ZF','ZN','ZB','ZC','ZS','ZW','ZL','ZM']
f = {}
f['products_50k'] = E(
    {'listed': listed, 'not_listed': ['SI','HG','ETH','BTC','2YY','5YY','10Y','30Y','MZC','MZS','MZW','MZL','MZM','XC','XK','XW'], 'changes_vs_e28': []},
    'Micro Bitcoin (MBT)* ... Micro Ether (MET)* ... 2-Year Note (ZT) ... Soybean Meal (ZM) ... Micro Silver (SIL)* ... Micro Copper (MHG)',
    'ts_8284206.html.txt', old_value='same 31 listed codes', old_path=P+'.listed_50k', changed=False,
    also=[('Silver (SI) = 0 ... Copper (HG) = 0', 'ts_13613539.html.txt')],
    note='Product codes on the page are identical to the E.28 copy (diff of all "(CODE)" tokens). SI and HG are on the page but capped at 0 at 50K.')
f['product_caps_50k'] = E(
    {'Combine/XFA/Pro 50K': {'CL':3,'QM':3,'MCL':30,'GC':3,'MGC':30,'SI':0,'SIL':2,'HG':0,'MHG':2}, 'LFA 50K': {'CL':3,'QM':3,'MCL':3,'GC':3,'MGC':5,'SI':0,'SIL':2,'HG':0,'MHG':2}, 'temporary': True},
    'Crude Oil (CL) = 3/6/9 ... Micro Crude Oil (MCL) = 30/60/90 ... E-Mini Crude Oil (QM) = 3/6/9 ... Gold (GC) = 3/6/9 ... Micro Gold (MGC) = 30/60/90 ... Silver (SI) = 0 ... Micro Silver (SIL) = 2/5/7',
    'ts_13613539.html.txt', old_value={'CL':3,'QM':3,'MCL':30,'GC':3,'MGC':30,'SI':0,'SIL':2,'HG':0,'MHG':2}, old_path=T+'rules.volatility_caps_50k', changed=False)
f['news_windows'] = E(
    {'events': ['CPI 07:30 CT', 'FOMC rate decision 13:00 CT', 'FOMC press conference 13:30 CT', 'NFP 07:30 CT', 'PPI 07:30 CT'],
     'minutes_before': 5, 'minutes_after': 5, 'effect': 'no new opening transactions; existing positions may be kept; pending orders will not fill in the window; reducing brackets accepted',
     'blocked_minis_page_list': ['ES','RTY','YM','NQ','NKD','GC','SI','HG','PL'],
     'capped_micros_50k': {'MES':3,'M2K':3,'MYM':3,'MNQ':3,'MGC':3,'MHG':2,'SIL':2},
     'xfa_50k_caps_by_balance': 'below $1500: 0 minis / 1 micro (SIL&MHG 1); $1500-2000: 0/1 (1); above $2000: 0/3 (2)',
     'unaffected': 'energies, rates, FX, etc.; grains not named on the list',
     'blocked_among_47': ['RTY','YM','NQ','GC','SI','HG'], 'capped_among_47_one_lot_still_allowed': ['M2K','MYM','MNQ','MGC','MHG','SIL'],
     'stages': 'Trading Combine and Express Funded Account (SIM); LFA: below $3,000 balance limited to 1 contract during Tier 1 events'},
    'Ahead of Tier 1 News Events (for example, CPI, FOMC, NFP, PPI), Topstep temporarily restricts new opening positions on equity index products and metals in SIM to protect Traders from extreme volatility. Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after). Micros (MES, M2K, MYM, MNQ, MGC): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes, respectively, during the window (see table below) MHG and SIL: Opening transactions limited to 1, 2, 5, 7, 12 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes, respectively, during the window (see table below) Other products (energies, rates, FX, etc.) are unaffected.',
    'ts_13613539.html.txt', old_value='no new opens on ES,RTY,YM,NQ,NKD,GC,SI,HG,PL 5 min before to 5 min after CPI, FOMC decision, FOMC presser, NFP, PPI; micros capped (3 at 50K Combine); energies, rates, FX unaffected',
    old_path=T+'rules.tier1_news', changed=False,
    also=[('Live traders with a balance below $3,000 will be limited to 1 contract during Tier 1 News Events', 'ts_13613539.html.txt'),
          ('Pending orders are not open positions. They will not fill during the 10-minute window', 'ts_13613539.html.txt'),
          ('Consumer Price Index (CPI) 7:30 AM 7:25 to 7:35 AM FOMC rate decision 1:00 PM 12:55 to 1:05 PM FOMC press conference 1:30 PM 1:25 to 1:35 PM', 'ts_13613539.html.txt')],
    note='Pointer check (planner notes, "Tier 1 list blocks named minis only"): VERIFIED. Minis named are blocked; MGC capped at 3 (also MES/M2K/MYM/MNQ at 3, MHG/SIL at 2) at 50K; EIA and crop reports are listed on the Economic Releases page but are not Tier 1 events. E.28 RR-04 superseded by this list (spec section 4).')
f['news_other_rules'] = E('Prohibited: purposefully trading full Maximum Position Size directly into a scheduled major news event (not a window; a one-lot is not max size).',
    'Trading Maximum Position Size into Major News Events Purposefully trading your full Maximum Position Size directly into a scheduled major news event.',
    'ts_10305426.html.txt', old_value=None, old_path=None, changed=False, note='Present in the E.28 copy as well (not recorded as a field there).')
f['flat_by_close'] = E({'time': '15:10', 'zone': 'CT', 'no_new_opens_after': '15:08 CT', 'reopen': '17:00 CT', 'friday': '15:10 CT, closed until Sunday 17:00 CT', 'early_close_product': 'exit before the product close if earlier than 15:10 CT'},
    'All positions must be closed by 3:10 PM CT every weekday. You can resume trading at 5:00 PM CT. No swing trading. ... Avoid opening new positions after 3:08 PM CT — Risk Managers begin flattening at that time. ... If you\'re trading a product with an earlier daily close than 3:10 PM CT, you must exit before that product\'s close.',
    'ts_8284206.html.txt', old_value='15:10 CT', old_path=T+'rules.flat_by', changed=False)
f['session_cutoffs'] = E({'cbot_grains': 'Sun-Mon 19:00-07:45 CT; Mon-Fri 08:30-13:20 CT; pause 07:45-08:30 CT no orders accepted', 'holiday': 'flat 15 min before any early close'},
    'Sunday–Monday: 7:00 PM – 7:45 AM CT Monday–Friday: 8:30 AM – 1:20 PM CT ... (Mon–Fri): 7:45 AM – 8:30 AM CT. No orders accepted during this window.',
    'ts_8284206.html.txt', old_value='19:00-07:45 and 08:30-13:20 CT', old_path=T+'rules.grain_hours', changed=False,
    also=[('All account types must close positions 15 minutes before any early close.', 'ts_13350348.html.txt')])
f['overnight'] = E({'evaluation': False, 'funded': False, 'weekend': False, 'margin_or_fee': 'n/a'},
    'Can I swing trade or hold positions overnight? No. All positions must be closed by 3:10 PM CT each weekday. Topstep does not permit holding positions from one session to the next.',
    'ts_8284206.html.txt', old_value='flat by 15:10 CT (no overnight)', old_path=T+'rules.flat_by', changed=False)
f['dll_50k'] = E({'amount': 1000, 'kind': 'optional, chosen at purchase (fixed) or as a personal DLL; not a rule violation, ends the session', 'default': None},
    'The Daily Loss Limit (DLL) is optional in the Trading Combine® and Express Funded Account® (XFA). It’s automatic in the Live Funded Account® (LFA). Triggering it is not a rule violation ... $50K Account: $1,000',
    'ts_10490293.html.txt', old_value='optional; 1000 if added at purchase (fixed, carries into XFA); not a violation', old_path=T+'plan_50k.dll', changed=False,
    note='Where no DLL is chosen the spec uses the MLL (section 4, D).')
f['mll_50k'] = E({'amount': 2000, 'type': 'trailing on end-of-day balance, monitored intraday on realized+unrealized P&L', 'lock': 'Combine: locks at the starting balance (50,000); XFA: starts -2,000, locks at 0 once balance reaches 2,000'},
    'The MLL is a trailing limit. It rises as your end-of-day balance grows, but never moves down. Once it reaches your starting balance, it locks permanently. ... For a 50K XFA, your MLL starts at -$2,000 and trails upward. Once your balance reaches $2,000, the MLL locks at $0 permanently.',
    'ts_8284204.html.txt', old_value='2000; trailing on end-of-day balance, monitored intraday, locks at starting balance', old_path=T+'plan_50k.mll_amount / plan_50k.mll_type', changed=False)
f['payout_qualification'] = E({'standard_path': '5 winning days of $150+ net P&L; positive net profit since last payout; 50% of balance up to $2,000 (50K; $4,000 with DLL)', 'consistency_path': '3 traded days, best day <= 40%; up to $3,000 (50K; $6,000 with DLL)', 'min_payout': 125, 'split': 0.9, 'combine_consistency': 'best day <= 55% of profit target, no buffer', 'combine_min_days': 2},
    'Minimum Payout: $125 90/10 profit split — you keep 90% ... 5 winning days of $150+ 3 days with 40% consistency target',
    'ts_8284233.html.txt', old_value='Standard: 5 winning days >= 150; Consistency: 3 traded days, best day <= 40%; caps 2000/3000 (4000/6000 with DLL)', old_path=T+'funded_stage.payout_paths', changed=False,
    also=[('55% is a hard line. It is not rounded, and there is no buffer.', 'ts_8284208.html.txt')])
f['automation'] = E({'evaluation': 'allowed with conditions', 'funded_xfa': 'allowed with conditions', 'live_lfa_api': False, 'api': 'TopstepX/ProjectX API, $29/month list ($14.50/month offer)', 'hft': 'prohibited (undefined)', 'order_rate_limit': '200 requests / 60 s (all endpoints other than bars; bars 50 / 30 s)', 'min_hold_or_scalping_rule': 'none numeric; SIM-exploitation examples: "hundreds or thousands of trades per day, with average durations measured in seconds"', 'vps': 'prohibited for order flow', 'changes_since_2026-10-21': 'none found'},
    'Yes. Custom automated strategies and bots are allowed via the TopstepX / ProjectX API, subject to standard platform rules and our prohibition on highfrequency trading (HFT). ... No, Live funded accounts are not allowed to trade through the ProjectX API.',
    'ts_11187768.html.txt', old_value='allowed via TopstepX/ProjectX API; HFT prohibited; not on LFA', old_path=T+'rules.api_bots', changed=False,
    also=[('Can I use automated trading strategies? Yes, with conditions.', 'ts_8284197.html.txt'),
          ('usually hundreds or thousands of trades per day, with average durations measured in seconds, not minutes.', 'ts_10305426.html.txt'),
          ('200 requests / 60 seconds', 'px_rate_limits.html.txt')])
f['fees'] = E({'changes_vs_e28_for_47': [], 'note': 'every one of the 31 listed codes has the same round-turn total as A3_firm_products.json; MCL/MNG exchange-fee rise of 2026-10-01 already in E.28', 'ZM': 5.28, 'MGC': 1.92, 'QM': 3.42, 'MCL': 1.72},
    'Exchange fee increase starting the October 1, 2026 trading day ... Micro Crude Oil (MCL) $1.72 E-mini Crude Oil (QM) $3.42 ... Micro Gold (MGC) $1.92 ... Soybean Meal (ZM) $5.28',
    'ts_8284213.html.txt', old_value='per-code fee_rt_usd unchanged', old_path=P+'.fee_rt_usd', changed=False)
f['rel_founded'] = E('2010 (Patak Trading Partners); Topstep Trader launched 2012', None, 'reports/stage_e28_briefs/pages/A2_topstep/ts_www_about-us.html.txt', old_value='same', old_path=T+'reliability.founded', changed=False, verified=True, note='Reused from E.28 (not refetched).')
f['rel_payout_disputes_12m'] = E('McCrudden v. Topstepfunded LLC, M.D. Fla. 3:26-cv-00816, filed 2026-04-09 (pro se; alleges rule changes used to block payouts), open as of E.28; no new item found 2026-10-28 (pointer search: NexusFi threads only)',
    None, 'reports/stage_e28_briefs/pages/A2_topstep/cl_docket_mccrudden.html.txt', old_value='same', old_path=T+'reliability.litigation', changed=False, verified=True,
    note='Docket status not refetched. Topstep v. Wieland (Topstep as plaintiff, statements about the firm) is a pointer (tradeinformer) and not a payout dispute.')
f['rel_rule_changes_12m'] = E(['Oct 2025 -> now: 50K Standard payout cap $5,000 or 50% -> $2,000', 'Sep 2025 -> now: Combine consistency best day <50% (with buffer) -> 55% no buffer', 'Sep 2025 -> now: platforms NinjaTrader/Quantower/Tradovate/TradingView -> TopstepX only (+Quantower via TopstepX)', '2026-05-29: Back2Funded window 7 -> 30 days (favourable)'],
    None, 'reports/stage_e28_briefs/A2_firm_topstep.json', old_value='same', old_path=T+'reliability.change_*', changed=False, note='No further change found between 2026-10-21 and 2026-10-28 on the 17 refetched pages.')
f['rel_regulatory'] = E('none found against the firm; Topstep is an NFA member (Swap Firm, CTA, Apr-May 2026, secondary press)', None, 'reports/stage_e28_briefs/A2_firm_topstep.json', old_value='none found', old_path=T+'reliability.regulatory_actions', changed=False, note='One WebSearch 2026-10-28 found no CFTC, NFA or state action (pointer-level negative).')
f['bc_accepted'] = E(True, 'residents of OFAC-sanctioned or partner-restricted countries are not eligible to trade, earn funding, or receive payouts', 'ts_8284116.html.txt', old_value=True, old_path=T+'eligibility.canada_bc_accepted', changed=False, note='Canada appears on neither the XFA-not-LFA list nor the ineligible list (grep "canada": 0 hits).')
f['p_inputs'] = E({'native_api': True, 'oco_api': True, 'vps_chicago': 'prohibited', 'api_rate_limit_per_s': 3.33},
    'All trading activity must originate from your personal device. The use of VPS, VPNs, and remote servers is prohibited by Topstep\'s Terms of Use.',
    'ts_11187768.html.txt', old_value={'native_api': True, 'oco_api': True, 'vps': 'prohibited', 'rate': '200/60 s'}, old_path=T+'rules.api_rate_limit / api_brackets / vps', changed=False,
    also=[('stopLossBracket', 'px_order_place.html.txt'), ('200 requests / 60 seconds', 'px_rate_limits.html.txt')],
    note='3.33 = 200/60 requests a second (all requests, not orders only).')
save_firm('topstep', f, notices=[{'what': 'Topstep Terms bar crawling/spidering; targeted single-page curl of 18 named articles, >=4 s apart (as E.28).'}],
          gaps=[{'what': 'McCrudden docket status not refetched; reliability founded/claims reused from E.28.'}])
