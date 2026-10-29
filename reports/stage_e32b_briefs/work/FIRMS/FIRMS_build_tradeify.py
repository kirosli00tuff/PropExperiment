import sys
sys.path.insert(0, '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/FIRMS')
from FIRMS_lib import E, save_firm
T = 'reports/stage_e28_briefs/A2_firm_tradeify.json:'
P = 'reports/stage_e28_briefs/A3_firm_products.json:pairs[firm=tradeify]'
TP = 'reports/stage_e28_briefs/pages/A2_tradeify/'
listed = ['QG','NG','MCL','QM','CL','MGC','GC','SI','HG','M6E','6E','M6A','6A','M2K','RTY','MYM','YM','MNQ','NQ','ZC','ZS','ZW','ZL','ZM']
f = {}
f['plan'] = E('Growth 50K (evaluation with EOD trailing drawdown and DLL; simulated funded)', 'A Growth account with a $2,000 trailing drawdown locks its floor at $50,100 once its end-of-day balance reaches $52,100.',
    'tf_12268167.html.txt', old_value='Growth 50K', old_path=T+'plan.name', changed=False,
    note='Tradeify terms forbid robots/scrapers: Wayback captures only. Newest captures: growth eval 2026-10-14, payout 2026-10-11, essential rules 2026-10-12; products/news/fees/times captures are June-July 2026, older than E.28 (2026-10-21 mirror fetches), so E.28 values are carried for those.')
f['products_50k'] = E({'listed': listed, 'not_listed': ['MNG','SIL','MHG','MET','ETH','MBT','BTC','2YY','5YY','10Y','30Y','ZT','ZF','ZN','ZB','MZC','MZS','MZW','MZL','MZM','XC','XK','XW'], 'changes_vs_e28': []},
    None, 'reports/stage_e28_briefs/A3_firm_products.json', old_value='same 24 listed codes', old_path=P+'.listed_50k', changed=False, verified=False,
    note='Not re-verified after 2026-10-21: the latest Wayback capture of the products page is 2026-07-09 (older than E.28). Carried from E.28.')
f['news_windows'] = E({'events': [], 'note': 'no news rule at all; evaluation and funded'},
    'We do not have any rules against or guidelines around trading news events.', 'tf_10495874.html.txt', old_value='none', old_path=T+'restrictions.news', changed=False,
    note='Capture 2026-06-24; E.28 mirror copy of 2026-10-21 has the same sentence.')
f['flat_by_close'] = E({'time': '16:45', 'zone': 'ET', 'holiday_early_close': '12:59 ET', 'reopen': '18:00 ET Sun-Thu', 'auto_close': 'positions left open are closed by Tradeify, no failure'},
    'Close all positions by 4:45 PM Eastern Time (Monday-Friday) Holiday Early Close Days: Close all positions by 12:59 PM Eastern Time ... Any positions left open when the market closes will be automatically closed by Tradeify.',
    'tf_12268167.html.txt', old_value='16:45 ET (12:59 ET holiday early close)', old_path=T+'plan.flat_by', changed=False)
f['overnight'] = E({'evaluation': False, 'funded': False, 'weekend': False},
    'All positions must be closed before the market closes each day. No swing trading or holding positions overnight is allowed.', 'tf_12268167.html.txt',
    old_value='no overnight or weekend holds', old_path=T+'restrictions.hours', changed=False)
f['dll_50k'] = E({'amount': 1250, 'stages': 'Growth evaluation and Growth funded', 'kind': 'soft per E.28 (trading paused for the session)'},
    'Growth Evaluation: Daily loss limit varies by account size ($1,250 for $50k, $2,500 for $100k, $3,750 for $150k) ... Growth Accounts: Daily loss limit varies by account size ($1,250 for $50k, $2,500 for $100k, $3,750 for $150k)',
    'tf_12268167.html.txt', old_value=1250, old_path=T+'plan.daily_loss_limit / funded.daily_loss_limit', changed=False)
f['mll_50k'] = E({'amount': 2000, 'type': 'end-of-day trailing, enforced in real time on net liquidation', 'lock': 'evaluation: floor 50,100 at EOD 52,100 (per essential rules example); funded: locks at 50,100 at 52,100 EOD or first payout request (E.28)'},
    'The limit trails your highest end-of-day balance (the high water mark) and only moves up, never down. ... A Growth account with a $2,000 trailing drawdown locks its floor at $50,100 once its end-of-day balance reaches $52,100.',
    'tf_12268167.html.txt', old_value='2000 EOD trailing; no lock in evaluation; funded locks at 50,100', old_path=T+'plan.max_loss_type / funded.max_loss', changed=True,
    note='Possible change: E.28 recorded "no lock in evaluation" (growth eval page); the essential-rules capture of 2026-10-12 (page dated August 26, 2026) gives the 50,100 lock example under "All Evaluation Accounts". Treat the evaluation lock as conflicting sources; funded lock unchanged.')
f['payout_qualification'] = E({'winning_days': 5, 'min_profit_per_winning_day': 150, 'consistency': 0.35, 'min_balance_to_request': 53000, 'caps': [1500, 2000, 2500, 3000], 'min_payout': 500, 'microscalping_gate': '>50% of trades AND profits from holds > 10 s (funded only)', 'min_activity': 'at least 1 trade per week (eval and funded)', 'eval_consistency': None, 'eval_min_days': 1},
    'Abide by the 35% Consistency Rule ... 5 or more of the Trading Days must show a profit greater than: ... $150 in profit for 50k accounts ... $50,000 $53,000',
    'tf_11083796.html.txt', old_value='5 winning days, 35% consistency, min balance 53,000, caps 1500/2000/2500/3000', old_path=T+'funded.winning_days / consistency / min_balance_to_request / payout_caps', changed=False,
    also=[('Over 50% of your trades AND profits must come from trades held longer than 10 seconds', 'tf_12268167.html.txt'),
          ('At least 1 trade per week (Monday-Friday) — applies to both evaluation and funded accounts', 'tf_12268167.html.txt')])
f['automation'] = E({'evaluation': 'allowed (own, non-HFT, not shared)', 'funded': 'allowed', 'api': 'Tradovate API only on LIVE funded accounts; none in evaluation or sim funded (E.28, products page)', 'hft': 'not allowed (undefined)', 'min_hold': '10 s rule (>50% of trades and profit), funded payout gate', 'order_rate_limit': None, 'changes_since_2026-10-21': 'none detectable (no capture after 2026-10-14)'},
    'HFT Bots: High-frequency trading bots not allowed Algorithmic Trading Allowed if: - You own the strategy exclusively - Not shared with other traders/firms - Not high-frequency trading - Can prove ownership if requested',
    'tf_12268167.html.txt', old_value='own non-HFT bots in eval and funded; Tradovate API live only', old_path=T+'automation.bots_allowed / automation.api', changed=False)
f['fees'] = E({'changes_vs_e28_for_47': [], 'ZM': 9.20, 'MGC': 2.12, 'QM': 5.40}, None, 'reports/stage_e28_briefs/A3_firm_products.json', old_value='unchanged', old_path=P+'.fee_rt_usd', changed=False, verified=False,
    note='Not re-verified: latest Wayback capture of the commissions page is 2026-07-09 (older than E.28).')
f['rel_founded'] = E('<= 2022-12-05 (home page capture)', None, TP+'tf_home_2022_wb.html.txt', old_value='same', old_path=T+'reliability.operating_since', changed=False)
f['rel_payout_disputes_12m'] = E('review-site reports only (pointers); no firm or regulator evidence', None, 'reports/stage_e28_briefs/A2_firm_tradeify.json', old_value='same', old_path=T+'reliability.disputes_12m', changed=False)
f['rel_rule_changes_12m'] = E(['Tradeify 3.0 (~2026-04): subscriptions ended, ~3% price rise, Select 50K target 2,500 -> 3,000', 'Growth evaluation consistency removed (2026-10)', 'Growth payout min balance 52,100 -> 53,000 and new caps for accounts bought from 2025-09-12'],
    'Account Balance Needed for Growth purchased before September 12, 2025 at 8:00 AM EST:', 'tf_11083796.html.txt', old_value='E.28 list', old_path=T+'reliability.rule_changes_12m', changed=False,
    note='Third item is dated 2025-09-12, just outside or at the edge of the 12-month window before 2026-10-28.')
f['rel_regulatory'] = E('none found', None, None, old_value='none found', old_path=T+'reliability.regulatory_actions', changed=False, verified=False, note='Search-negative (pointer-level).')
f['bc_accepted'] = E(True, None, TP+'tf_wf_restricted.txt', old_value='accepted by omission', old_path=T+'eligibility.bc_canada', changed=False,
    note='Latest Wayback capture of restricted countries (2026-06-10) is older than E.28; E.28 mirror copy shows Canada not restricted.')
f['p_inputs'] = E({'native_api': False, 'oco_api': 'unknown', 'vps_chicago': 'conditionally prohibited (where it obscures verification)', 'api_rate_limit_per_s': 'unknown'}, None, 'reports/stage_e28_briefs/A2_firm_tradeify.json', old_value='api live only; vps conditional', old_path=T+'automation.api / platform.vps', changed=False)
save_firm('tradeify', f, notices=[{'what': 'Tradeify terms forbid robots: Wayback captures only; no capture newer than 2026-10-14, so changes after E.28 (2026-10-21) cannot be detected by permitted routes. One WebSearch (2026-10-28): third-party reviews only, no official October change.'}],
          gaps=[{'what': 'Tradeify products, fees, BC eligibility not re-verified after 2026-10-21 (captures older than E.28).'}, {'what': 'Tradeify evaluation MLL lock: E.28 "no lock in evaluation" vs essential-rules example of 50,100 lock under All Evaluation Accounts.'}])
