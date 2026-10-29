import sys
sys.path.insert(0, '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/FIRMS')
from FIRMS_lib import E, save_firm
T = 'reports/stage_e28_briefs/A2_firm_mffu.json:'
P = 'reports/stage_e28_briefs/A3_firm_products.json:pairs[firm=mffu]'
listed = ['MCL','QM','CL','MGC','GC','SIL','6E','6A','M6E','M6A','MET','MBT','M2K','RTY','MYM','YM','MNQ','NQ','ZC','ZS','ZW','ZL','ZM']
f = {}
f['plan'] = E('Builder 50K, Default MLL option ($2,000); evaluation then sim funded (1 per user), live after 5th sim payout', 'The Builder Plan is available with two Max Loss Limit (MLL) options at checkout.',
    'mffu_art_14290805.html.txt', old_value='Builder 50K (Default MLL option)', old_path=T+'plan.name', changed=False,
    note='Other 50K plans exist (Rapid, Pro; Flex linked as a related guide). E.28 chose Builder as the standard 50K plan; kept.')
f['products_50k'] = E({'listed': listed, 'not_listed': ['MNG','QG','NG','SI','MHG','HG','ETH','BTC','2YY','5YY','10Y','30Y','ZT','ZF','ZN','ZB','MZC','MZS','MZW','MZL','MZM','XC','XK','XW'], 'changes_vs_e28': [], 'restricted_on_page': ['SI','HG','PL','NG','QG'], 'metals_micro_cap_50k': 5, 'MBT_counted_as_mini': True},
    'The following products are currently restricted from trading: Silver (SI) Copper (HG) Platinum (PL) Natural Gas (NG) E-Mini Natural Gas (QG) ... $50k account → maximum 5 micro contracts ... MBT is treated as a mini contract',
    'mffu_art_9735811.html.txt', old_value='same 23 listed codes', old_path=P+'.listed_50k', changed=False,
    note='Fee table lists 39 codes; for the 47, listed set and restrictions identical to E.28 (QG/NG/SI/HG on the fee table but restricted; MNG, MHG absent).')
f['news_windows'] = E({'builder_50k': 'none: news trading fully unrestricted in evaluation and sim funded (Builder is an "Unrestricted Account" for T1 news)',
     'restricted_accounts_T1': {'accounts': ['Rapid Sim Funded', 'Pro Sim Funded'], 'minutes_before': 2, 'minutes_after': 2, 'rule': 'no positions or orders (including limit orders); flat by 2 minutes before'},
     'T1_events': {'all_traders': ['FOMC meetings', 'FOMC minutes', 'Employment Report', 'CPI'], 'energy_traders': ['EIA'], 'agricultural_traders': ['Agricultural Reports']},
     'eia_time_on_page': 'Wednesdays 10:30 ET (no natural-gas Thursday report named)',
     'ambiguity': 'The same page has a "Standard Trading Protocols" bullet ("no open positions or orders ... 2 minutes before and after any data release", "These protocols apply to all news releases") and the Fair Play page says trading during Tier 1 releases "is restricted"; the Builder guide and the T1 section state Builder news trading is unrestricted.'},
    'Restricted Accounts : Trading on T1 News events is prohibited for the following: Rapid Sim Funded Pro Sim Funded Unrestricted Accounts : Trading on T1 News events is permitted for the following: All evaluations Builder Plans Tier 1 News Includes: For All Traders : FOMC Meetings, FOMC Minutes, Employment Report, CPI For Energy Traders : EIA For Agricultural Traders : Agricultural Reports',
    'mffu_art_8230009.html.txt', old_value='Builder unrestricted; restricted accounts 2 min before/after T1 (FOMC, minutes, Employment, CPI; EIA for energy; Ag reports for ags)',
    old_path=T+'restrictions.news_builder / news_restricted_accounts', changed=False,
    also=[('News trading is fully unrestricted during the evaluation and sim funded stage. You may open and hold positions through any scheduled news event without limitation.', 'mffu_art_14290805.html.txt'),
          ('Ensuring no open positions or orders are active in the order book 2 minutes before and after any data release. These protocols apply to all news releases.', 'mffu_art_8230009.html.txt'),
          ('Tier 1 Economic Data Trading: Engaging in trades during tier 1 economic data releases is restricted.', 'mffu_art_8444599.html.txt'),
          ('EIA reports are released every Wednesday at 10:30 am EST', 'mffu_art_8230009.html.txt')],
    note='Pointer check (planner notes, "MFFU EIA rule covers energy" on Rapid and Pro sim funded): VERIFIED for Rapid/Pro Sim Funded; it does NOT apply to the Builder 50K plan or to any evaluation. The page names "Energy Traders", not product codes. Page dated August 31, 2026, unchanged from E.28.')
f['news_other_rules'] = E('All accounts: strategies exploiting immediate news bursts (straddles, strangles) and masking news trades are prohibited.',
    'Utilizing strategies that exploit immediate news bursts, such as straddles or strangles. Masking news trades as standard strategies. These prohibitions are in effect for all news releases.', 'mffu_art_8230009.html.txt',
    old_value=True, old_path=T+'restrictions.news_burst_ban', changed=False)
f['flat_by_close'] = E({'time': '16:10', 'zone': 'ET (page writes EST)', 'auto_close': 'open positions auto-closed at 16:10 ET on regular days', 'reopen': '18:00 ET', 'holiday': 'no auto-liquidation at the holiday half-day close; trader must flatten, else breach'},
    'Trades may be placed beginning at 6:00 PM EST when the Globex session opens and can remain open until the New York session closes at 4:10 PM EST. ... any open positions will be automatically closed at 4:10 PM EST on regular (non-holiday) trading days.',
    'mffu_art_9558251.html.txt', old_value='18:00 ET open to 16:10 ET auto-flat', old_path=T+'restrictions.hours', changed=False,
    also=[('During holiday trading hours, auto-liquidation will not occur at the half-time market close, and the trader is responsible for closing the positions.', 'mffu_art_9558251.html.txt')])
f['overnight'] = E({'evaluation': False, 'funded': False, 'weekend': False},
    'Q: Can I hold positions overnight? No. All positions must be closed before the end of the trading session.', 'mffu_art_14290805.html.txt', old_value='not allowed', old_path=T+'plan.eval.overnight', changed=False)
f['dll_50k'] = E({'amount': 1000, 'kind': 'soft pause; evaluation, sim funded and live'},
    'Q: Is there a Daily Loss Limit (DLL)? Yes. The Evaluation, Sim Funded and Live stage have a $1,000 soft pause DLL.', 'mffu_art_14290805.html.txt', old_value=1000, old_path=T+'plan.eval.dll', changed=False)
f['mll_50k'] = E({'amount': 2000, 'type': 'end-of-day trailing (open equity counted at the end of the day)', 'lock': 'locks once it reaches $100 above the starting balance'},
    'The Maximum Loss Limit (MLL) is an End of Day (EOD) trailing drawdown. It does not move intraday. ... The MLL locks permanently once it reaches $100 above the starting balance.',
    'mffu_art_14290805.html.txt', old_value='2000 EOD trailing; locks at start+100', old_path=T+'plan.eval.mll / mll_type', changed=False)
f['payout_qualification'] = E({'min_qualifying_days_per_cycle': 2, 'min_profit_per_day': None, 'consistency': 0.5, 'buffer': 2100, 'first_payout': '$500 net profit above buffer', 'later_payouts': '$500 since last payout', 'min_payout': 500, 'max_payout': 2000, 'split': 0.8, 'max_sim_payouts': 5, 'first_request_after': '48 h after first trade', 'eval_consistency': None, 'eval_min_days': 1},
    'You must have traded on at least 2 trading days in the current cycle. The 50% consistency rule applies: your single largest profit day cannot represent more than 50% of your total profits in the cycle.',
    'mffu_art_14290805.html.txt', old_value='2 days/cycle, 50% consistency, buffer 2,100, min 500, max 2,000, 80/20', old_path=T+'plan.payout.*', changed=False)
f['automation'] = E({'evaluation': 'allowed if not exploiting sim fills', 'funded': 'allowed if not exploiting sim fills', 'live': 'allowed under CME guidelines', 'api': 'no MFFU API documented; Tradovate accounts (TradingView, Tradovate, NinjaTrader; dxFeed for others)', 'hft': 'not allowed (undefined)', 'order_rate_limit': None, 'min_hold': None, 'changes_since_2026-10-21': 'none found'},
    'High-frequency Trading is not allowed on our plans. Traders may make use of automated trading strategies tailored to their own specific settings so long as these automated tools do not aim to exploit the favorable fills offered in the Simulated Environment.',
    'mffu_art_8444599.html.txt', old_value='allowed if not exploiting sim fills; HFT banned undefined', old_path=T+'automation.*', changed=False)
f['fees'] = E({'changes_vs_e28_for_47': [], 'ZM': 6.12, 'MGC': 2.20, 'QM': 4.32, 'basis': 'Total Cost Round Trip'},
    'Includes Contract Specifications, Commissions, and Trading Fees', 'mffu_art_9735811.html.txt', old_value='unchanged', old_path=P+'.fee_rt_usd', changed=False)
f['rel_founded'] = E('2023 (site footer "© 2023- 2026"; month unverified)', None, 'reports/stage_e28_briefs/pages/A2_mffu/mffu_whyus.html.txt', old_value=2023, old_path=T+'reliability.operating_since', changed=False,
    note='Month unverified (E.28). A review site (pointer) says 2022.')
f['rel_payout_disputes_12m'] = E('no firm or regulator evidence; third-party review pointers only; payout page: most approved instantly, manual review up to 6-12 business hours', 'Most payouts are approved instantly. If a manual review is required, processing may take up to 6 to 12 business hours on weekdays.',
    'mffu_art_13745661.html.txt', old_value='same', old_path=T+'reliability.payout_disputes_12m', changed=False)
f['rel_rule_changes_12m'] = E(['fee schedule raised (most products) between 2025-10-07 and 2026-01-13', 'Rapid split 90% from 2026-01-12; some plans 90% -> 80% 2026-02-26 (pointer)', '2026-02-07 temporary restriction SI/HG/PL/NG/QG', '2026-04-17 metals micro cap 5 at 50K', '2026-08-25 one-time payment model and 7-day inactivity closure', 'Builder plan launched 2026; live-breach 21-day cooldown', 'Hyperprop platform added Oct 2026'],
    'As of February 7th: Due to increased market volatility, MFFU is implementing temporary commodities trading restrictions', 'mffu_art_9735811.html.txt', old_value='E.28 list', old_path=T+'reliability.rule_changes_12m', changed=False,
    note='The 90->80 split change of 2026-02-26 is from a review site (pointer only).')
f['rel_regulatory'] = E('none found (search-negative; pointer review says not CFTC-registered or NFA member)', None, None, old_value='none found', old_path=T+'reliability.regulatory_actions', changed=False, verified=False)
f['bc_accepted'] = E(True, 'we are unable to accept traders from the below countries due to regulatory restrictions and compliance requirements', 'mffu_art_8229993.html.txt', old_value='accepted', old_path=T+'eligibility.canada_bc', changed=False,
    note='Canada is not on the list (grep "canada": 0 hits).')
f['p_inputs'] = E({'native_api': False, 'oco_api': 'unknown', 'vps_chicago': 'unknown (no MFFU statement; device-sharing rule only)', 'api_rate_limit_per_s': 'unknown'}, None, 'reports/stage_e28_briefs/A2_firm_mffu.json', old_value='api none documented; vps no statement', old_path=T+'automation.api / vps', changed=False)
save_firm('mffu', f, notices=[{'what': 'MFFU terms have no scraping clause; targeted curl of 11 help articles, >=4 s apart. One WebSearch 2026-10-28: no October change found (review sites only).'}],
          gaps=[{'what': 'MFFU news scope for Builder: firm pages conflict in wording (Builder "fully unrestricted" vs Standard Trading Protocols "all news releases" and Fair Play "restricted"); recorded, not resolved.'}])
