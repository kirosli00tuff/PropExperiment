import sys
sys.path.insert(0, '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/FIRMS')
from FIRMS_lib import E, save_firm
T = 'reports/stage_e28_briefs/A2_firm_lucid.json:'
P = 'reports/stage_e28_briefs/A3_firm_products.json:pairs[firm=lucid]'
listed = ['QG','NG','MCL','QM','CL','MGC','GC','SIL','SI','HG','6E','6A','M2K','RTY','MYM','YM','MNQ','NQ','ZC','ZS','ZW','ZL','ZM']
f = {}
f['plan'] = E('LucidPro 50K (evaluation then simulated funded); one-time fee, no rebilling', 'LucidPro evaluation accounts: $25K-$150K accounts, profit targets from $1,250, one-time fee with no rebilling',
    'lucid_12890029.html.txt', old_value='LucidPro 50K', old_path=T+'plan.name', changed=False,
    note='All Lucid pages read from Wayback captures (TOU bars robots). Captures: products 2026-09-22, other activities and trading times 2026-10-07, microscalping/HFT/DLL/drawdown 2026-10-26, eval/funded 2026-10-07, payouts 2026-10-12.')
f['products_50k'] = E({'listed': listed, 'not_listed': ['MNG','MHG','M6E','M6A','MET','ETH','MBT','BTC','2YY','5YY','10Y','30Y','ZT','ZF','ZN','ZB','MZC','MZS','MZW','MZL','MZM','XC','XK','XW'], 'changes_vs_e28': []},
    'MNQ Micro E-mini Nasdaq-100 Index Futures 0.50 CME ... QM E-mini Crude Oil Futures 2.00 NYMEX ... ZM Soybean Meal Futures 2.80 CBOT',
    'lucid_11508978.html.txt', old_value='same 23 listed codes', old_path=P+'.listed_50k', changed=False,
    note='No rates, no crypto, no M6E/M6A, no MNG/MHG on the approved list (34 symbols). The 23 listed codes of the 47 match E.28 exactly. Capture 2026-09-22 is the latest on Wayback; E.28 also had a 2026-10-21 WebFetch of the same page.')
f['news_windows'] = E({'pro_flex_direct': 'none; entering or exiting around scheduled or unscheduled news is allowed', 'daily_plan': 'red-folder news trading is a hard breach (not the 50K Pro plan)', 'stages': 'evaluation and funded (plan-level rule)'},
    'News Trading Not allowed on Daily Trading red folder news on the LucidDaily is a hard breach Allowed on Flex, Pro and Direct Traders may enter or exit positions around scheduled or unscheduled news events on these plans without it being a breach',
    'lucid_11404728.html.txt', old_value='allowed, no window', old_path=T+'restrictions.news_pro', changed=False)
f['flat_by_close'] = E({'time': '16:45', 'zone': 'ET (page writes EST)', 'reopen': '18:00 ET Sun-Thu', 'auto_close': 'positions auto-closed at 16:45 ET; holding past it is not a failed account', 'holiday': 'flat before the altered market close', 'live': 'LucidLive: 16:45 ET Tradovate, 16:15 ET Rithmic; no swing'},
    'All positions must be closed by 4:45 PM EST, Monday through Friday Any open positions will be automatically closed by Lucid Trading at 4:45 PM EST Important: Holding a position past this time does not result in a failed account Market Reopen Times: Trading resumes at 6:00 PM EST, Sunday through Thursday',
    'lucid_11404729.html.txt', old_value='16:45 ET Mon-Fri; reopen 18:00 ET Sun-Thu', old_path=T+'restrictions.flat_by', changed=False,
    also=[('Traders may hold positions until 4:45 PM EST on Tradovate Live accounts, or 4:15 PM EST on Rithmic Live accounts', 'lucid_11404729.html.txt')])
f['overnight'] = E({'evaluation': False, 'funded': False, 'weekend': False, 'note': 'daily flat by 16:45 ET means no hold across the 17:00-18:00 ET break; product sessions with an earlier close (for example CBOT grains 14:20 ET day close) are not addressed on the page'},
    'All positions must be closed by 4:45 PM EST, Monday through Friday', 'lucid_11404729.html.txt', old_value='flat by 16:45 ET', old_path=T+'restrictions.flat_by', changed=False)
f['dll_50k'] = E({'amount': 1200, 'kind': 'soft (trading stops until next session, account kept); evaluation fixed; funded fixed below 52,100 then 60% of highest EOD profit (never decreases); DLL optional at purchase (customization)'},
    'All DLLs at Lucid Trading are considered soft breaches, meaning you do not lose your account for hitting DLL as long as the Max Loss Limit (MLL) has not been reached. ... $50,000 $1,200 $52,100 ... Highest end-of-day account profit × 60% = LucidScale DLL',
    'lucid_12890122.html.txt', old_value=1200, old_path=T+'plan.daily_loss_limit', changed=False,
    also=[('The Daily Loss Limit is optional, and each Pro account can be customized at the time of evaluation purchase.', 'lucid_12890069.html.txt')])
f['mll_50k'] = E({'amount': 2000, 'type': 'end-of-day trailing (evaluation and funded)', 'lock': '50,100 once the account exceeds 52,100'},
    'LucidPro evaluation and funded accounts use an End-of-Day Drawdown (EOD Drawdown) system to calculate the Max Loss Limit (MLL). ... $50,000 $2,000 $52,100 $50,100',
    'lucid_12890136.html.txt', old_value='2000; end-of-day trailing, locks at 50,100 once balance exceeds 52,100', old_path=T+'plan.max_loss_limit / max_loss_limit_type', changed=False)
f['payout_qualification'] = E({'min_profit_per_cycle': 500, 'winning_day_minimum': None, 'consistency': 'largest day <= 40% of cycle profit', 'buffer': 'profits above 52,100 (MLL + 100)', 'min_payout': 500, 'max_first': 2000, 'max_2plus': 2500, 'split': 0.9, 'min_days': 'not stated on the payouts page (E.28: 3 days from home page)', 'eval_consistency': None, 'eval_min_days': 1},
    'You must earn at least the minimum goal between payout cycles to earn a payout. ... $50,000 $500 ... Your largest single-day profit must be no more than 40% of your total profit during the payout cycle. ... The buffer is equal to: Initial Max Loss Limit + $100',
    'lucid_12890092.html.txt', old_value='min profit 500/cycle, consistency 40%, buffer 52,100, max 2000 then 2500', old_path=T+'funded.min_profit_per_cycle / consistency / buffer / max_payout_*', changed=False,
    note='Secondary review sites (pointer) mention 5 profitable days per cycle; the firm page does not state any winning-day count.')
f['automation'] = E({'evaluation': 'allowed', 'funded': 'allowed', 'api': 'no Lucid API documented; platforms via CQG (NinjaTrader, Tradovate, TradingView) or Rithmic', 'hft': 'prohibited (qualitative: high volume of trades within seconds or milliseconds)', 'microscalping': 'flag if >50% of profits from trades held <= 5 s', 'order_rate_limit': None, 'changes_since_2026-10-21': 'none found'},
    'Automated trading systems and trade copiers are permitted All automated activity must comply with Lucid Trading rules',
    'lucid_11404728.html.txt', old_value='allowed; HFT banned (qualitative); microscalping >50% profit from <=5 s', old_path=T+'automation.*', changed=False,
    also=[('More than 50% of your profits are generated from trades held for 5 seconds or less', 'lucid_11404742.html.txt'),
          ('submitting and executing a high volume of trades within extremely short time frames, often measured in seconds or even milliseconds', 'lucid_11404736.html.txt')])
f['fees'] = E({'stated_basis': 'Commission (Per Side) table; no statement that exchange, clearing or NFA fees are included or excluded', 'all_in_stated': False, 'changes_vs_e28_for_47': [], 'per_side': {'ZM': 2.80, 'MGC': 0.80, 'QM': 2.00, 'MCL': 0.50, 'MNQ': 0.50}},
    'Symbol Name Commission (Per Side) Exchange', 'lucid_11508978.html.txt', old_value='2 x per side (E.28 arithmetic; e.g. ZM 5.60 RT)', old_path=P+'.fee_rt_usd', changed=False,
    note='Lucid does not state an all-in fee. One WebSearch (2026-10-28) found no firm statement either. E.28 treatment (RT = 2 x per side, all-in status unknown) stands.')
f['rel_founded'] = E('2025 (waitlist page 2025-02-20; domain for sale 2024-09-01): under 2 years', None, 'reports/stage_e28_briefs/pages/A2_lucid/lucid_home_wb_20250220204435.html', old_value='same', old_path=T+'reliability.operating_since', changed=False)
f['rel_payout_disputes_12m'] = E('review-site complaints only (pointers); no firm or regulator evidence; no new item 2026-10-28', None, 'reports/stage_e28_briefs/A2_firm_lucid.json', old_value='review-site complaints', old_path=T+'reliability.disputes', changed=False)
f['rel_rule_changes_12m'] = E(['2025-11-28 split 100% of first $10k -> 90/10', '2025-11-28 Pro funded consistency 35% -> 40%', '50K eval $135 (2025-11-01) -> $172 (2026-10-05); reset $90 -> $120', 'news ban on LucidDaily added 2026-07/08 (not Pro)', 'new Live structure 2026-10-14'],
    'Accounts purchased or reset before 11/28/2025 at 3:00 PM EST are still eligible for 100% on the first $10k.', 'lucid_12890092.html.txt', old_value='same list', old_path=T+'reliability.rule_changes_12m', changed=False,
    note='No change found 2026-10-21..28 on the refetched pages (latest Wayback captures, see plan note).')
f['rel_regulatory'] = E('none found', None, None, old_value=None, old_path=T+'reliability.regulatory_actions', changed=False, verified=False, note='Search-negative (pointer-level), as E.28.')
f['bc_accepted'] = E(True, None, 'reports/stage_e28_briefs/pages/A2_lucid/sup_restricted_countries.html.txt', old_value=True, old_path=T+'eligibility.canada_bc', changed=False,
    note='Restricted-countries page has no Wayback capture; E.28 (2026-10-21) found Canada not on the list. Not re-verified.')
f['p_inputs'] = E({'native_api': False, 'oco_api': 'unknown', 'vps_chicago': 'unknown', 'api_rate_limit_per_s': 'unknown'}, None, 'reports/stage_e28_briefs/A2_firm_lucid.json', old_value='api None; vps None', old_path=T+'automation.api / platforms.vps', changed=False,
    note='No Lucid page documents an API, VPS rule or rate limit (E.28 and this pass).')
save_firm('lucid', f, notices=[{'what': 'Lucid TOU bars robots: Wayback captures only; supported-platforms and restricted-countries pages have no Wayback capture (reused E.28). First Wayback batch stored gzip bytes and some HTTP 000 rows; refetched with --compressed (last log row per file is the valid one).'}],
          gaps=[{'what': 'Lucid pages are Wayback captures 2026-09-22..10-26, not live pages of 2026-10-28.'}, {'what': 'Lucid all-in fee not stated by the firm.'}])
