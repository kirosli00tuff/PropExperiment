import sys
sys.path.insert(0, '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/FIRMS')
from FIRMS_lib import E, save_firm
T = 'reports/stage_e28_briefs/A2_firm_bulenox.json:'
P = 'reports/stage_e28_briefs/A3_firm_products.json:pairs[firm=bulenox]'
BP = 'reports/stage_e28_briefs/pages/A2_bulenox/'
F = 'blx_wb20261024_cms_help_items.json.flat.txt'
listed = ['QG','NG','MCL','QM','CL','MGC','GC','SI','HG','M6E','6E','M6A','6A','MET','MBT','M2K','RTY','MYM','YM','MNQ','NQ','ZS','ZW','ZL','ZM']
f = {}
f['plan'] = E('Qualification Account $50,000, Option 1 (trailing, no scaling) or Option 2 (EOD drawdown, scaling, DLL); then simulated Master Account; Funded at discretion after 3 Master payouts',
    'Option 1 — No Scaling Account, with a real-time Trailing Drawdown; ... Option 2 — EOD Account, with an End-of-Day Drawdown, Dynamic Scaling Plan and Daily Loss Limit.', F,
    old_value='Qualification Account $50,000, Option 1 or Option 2', old_path=T+'plan_50k.plan_name', changed=False,
    note='Source: Wayback capture 2026-10-24 of the Bulenox CMS help_items JSON (the help centre content), flattened to text (English). Bulenox terms forbid robots; no direct fetch.')
f['products_50k'] = E({'listed': listed, 'not_listed': ['MNG','SIL','MHG','ETH','BTC','2YY','5YY','10Y','30Y','ZT','ZF','ZN','ZB','MZC','MZS','MZW','MZL','MZM','XC','XK','XW','ZC'], 'changes_vs_e28': []},
    'instruments: Wheat (ZW) instruments: Soybeans (ZS) instruments: Soybean Meal (ZM) instruments: Soybean Oil (ZL) instruments: Oats (ZO)', F,
    old_value='same 25 listed codes', old_path=P+'.listed_50k', changed=False, note='Instrument list identical to E.28 (no Corn ZC, no rates, no SIL/MHG/MNG).')
f['news_windows'] = E({'events': [], 'note': 'news allowed, no blackout windows (FAQ, E.28 2026-10-08 capture and 2026-10-21 check); no news rule in the 2026-10-24 help items for Qualification/Master'},
    None, BP+'blx_wb20261008_cms_faq_items.txt', old_value='allowed, no blackout windows', old_path=T+'restrictions.news', changed=False,
    note='FAQ JSON has no Wayback capture after 2026-10-08; carried from E.28. The 2026-10-24 help items contain no news restriction for Qualification or Master (news text appears only for Fast Track and Momentum, both "allowed").')
f['flat_by_close'] = E({'time': '15:59', 'zone': 'CT', 'trading_day': '17:00 CT to 16:00 CT next day', 'stages': 'Qualification and Master'},
    'All positions must be closed by 3:59 PM (CT). ... master-trading-rules: All positions must be closed by 3:59 PM CT.', F,
    old_value='15:59 CT all products all stages', old_path=T+'restrictions.flat_by', changed=False,
    also=[('The trading day starts at 5:00 PM and ends at 4:00 PM the following day, North American Central Time (CT).', F)])
f['overnight'] = E({'evaluation': False, 'funded': False, 'weekend': False}, 'Holding positions overnight is strictly prohibited.', F, old_value='no overnight', old_path=T+'plan_50k.flat_by', changed=False)
f['dll_50k'] = E({'option1': None, 'option2': 1100, 'kind': 'Option 2 only: soft (trading disabled for the rest of the day, not a violation), realized+unrealized incl. commissions; Master: removed once drawdown locks (E.28)'},
    'option-2: $1,100 ... If your Daily Loss Limit is reached, trading is disabled for the rest of the trading day. This is not considered a rule violation', F,
    old_value={'option1': None, 'option2': 1100}, old_path=T+'plan_50k.daily_loss_limit_option1/2', changed=False)
f['mll_50k'] = E({'amount': 2500, 'type': 'Option 1: real-time trailing on highest intraday value incl. unrealized; Option 2: end-of-day trailing', 'lock': 'Master: fixed at 50,100 once account value reaches 52,600'},
    '$2,500 | $47,500 | $50,100 ... The drawdown becomes permanently fixed when it reaches starting balance + $100 . ... The trailing drawdown follows your account’s highest value throughout the trading day, including both realized and unrealized (open) profits.', F,
    old_value=2500, old_path=T+'plan_50k.max_loss_limit_option1/2', changed=False)
f['payout_qualification'] = E({'trading_days_per_cycle': 10, 'min_profit_per_day': None, 'min_payout': 1000, 'max_payout_first3_50k': 1500,
     'max_payout_from_4th': 'requested amount < 50% of total profit on the Master Account', 'consistency': '40% best day / Total P&L of the payout period; resets after each payout; reserve counted on payout 1',
     'safety_threshold_reserve_50k': 2600, 'split': '90/10 (no "100% of first $10,000" sentence in the 2026-10-24 capture)', 'schedule': 'weekly, Wednesdays; request by Fri 23:59 CT', 'master_inactivity': 'at least one trade per week'},
    'complete at least 10 individual trading days; ... request at least $1,000; ... Starting from the fourth payout, the requested amount must be less than 50% of the total profit on the Master Account. ... Best Day P&L resets; ... Total P&L resets;', F,
    old_value={'max_after_3rd': 'no cap', 'consistency_reset': 'does not reset (cumulative over the Master period)', 'split': '100% of first $10,000 per trader profile, then 90%'},
    old_path=T+'master_stage.payout_max_first3 (note) / master_stage.consistency / master_stage.split', changed=True,
    also=[('the trader receives 90% of each additional payout; ... Bulenox receives a 10% commission.', F),
          ('The Master Account requires executing at least one trade per week and should not be inactive for more than a week.', F)],
    note='Changed between the 2026-09-28 capture (E.28 source) and the 2026-10-24 capture: (a) "You receive 100% of the first $10,000 paid from your profile" removed (absence in the capture; leftover word "additional" kept; third-party sites still show the 100% tier, so the split change rests on absence); (b) a cap from the 4th payout (< 50% of total profit) replaces "no maximum payout limit"; (c) consistency now resets after each payout (was cumulative); (d) Master inactivity rule added. E.28 also had a 2026-10-21 WebFetch summary that did not quote these sentences, so the exact change date is unknown.')
f['automation'] = E({'evaluation': 'allowed: user-built personal bots, algorithms, trade copiers; third-party algorithms need management approval', 'funded': 'same (no stage distinction stated)', 'api': 'Rithmic via an approved third-party API or Trader Composite interface, $100/month', 'banned': "scalping algorithms; DTC Protocol Bridge API; 'automated discretional trading'; hundreds or thousands of rapid trades", 'order_rate_limit': None, 'min_hold': None, 'changes_since_2026-10-21': 'none found (Terms PDF latest capture 2026-10-19 = E.28 copy)'},
    'If a trader chooses to connect to Rithmic through a Third-Party API or Trader Composite Software, a $100 monthly fee applies.', F,
    old_value='user-built bots allowed; third-party approval; Rithmic API $100/month; scalping algorithms banned', old_path=T+'automation.*', changed=False,
    note="The scalping-algorithm and rapid-trades bans are from the Terms PDF (E.28 copy, blx_terms_wb20261019.txt), not refetched.")
f['fees'] = E({'changes_vs_e28_for_47': [], 'commission_basis': 'per side, all-in (Rates PDF, E.28)', 'ZM': 5.72, 'MGC': 1.52, 'QM': 3.92, 'professional_data_fee_month': 133},
    'status: Traders with professional status pay a monthly fee of $133 for the exchange data feed covering CME, CBOT, NYMEX and COMEX.', F,
    old_value={'professional_data_fee_month': 116}, old_path=T+'plan_50k.data_fee_professional', changed=True,
    note='Per-product commissions: help-item "commissions" text unchanged between captures; Rates PDF not recaptured after 2026-10-10 (E.28 had a 2026-10-21 copy). Only the professional data fee changed (116 -> 133 a month; non-professional unaffected).')
f['rel_founded'] = E('2021-06-12 or earlier (home page capture)', None, BP+'blx_wb20210612_home.html.txt', old_value='same', old_path=T+'reliability.operating_since', changed=False)
f['rel_payout_disputes_12m'] = E("[unverified] review-site reports of payout denials for 'flipping trading days' (2026); pointers only", None, None, old_value='same', old_path=T+'reliability.disputes', changed=False, verified=False)
f['rel_rule_changes_12m'] = E(['billing: monthly auto-renew -> one-time with 30-day access', 'max Master accounts 3/11 -> 5', "automation: 'not forbidden' -> user-built only, third-party approval, $100/month API fee", 'household single-profile rule (Terms Oct 2026)', 'ProjectX removed (Dec 2025)', 'Funded structure changed', '$10K/$250K sizes and Wise dropped',
     'NEW (between 2026-09-28 and 10-24 captures): 100%-of-first-$10,000 split sentence removed; cap from 4th payout (< 50% of total profit); professional data fee 116 -> 133; Master weekly-trade inactivity rule; consistency now resets per payout (favourable)'],
    'A maximum payout limit applies to every payout.', F, old_value='7 items (E.28)', old_path=T+'rule_changes_12m', changed=True)
f['rel_regulatory'] = E('none found', None, None, old_value='none found', old_path=T+'reliability.regulatory_actions', changed=False, verified=False)
f['bc_accepted'] = E(True, None, BP+'blx_wb20261008_cms_faq_items.txt', old_value=True, old_path=T+'eligibility.british_columbia', changed=False, note='Not re-verified (no FAQ capture after 2026-10-08); E.28: Canada accepted, no province rule.')
f['p_inputs'] = E({'native_api': 'third-party Rithmic API only, approval and $100/month', 'oco_api': 'unknown (NinjaTrader OCO is client-side)', 'vps_chicago': 'unknown', 'api_rate_limit_per_s': 'unknown', 'server': 'Rithmic Paper Trading, Chicago gateway'}, None, 'reports/stage_e28_briefs/A2_firm_bulenox.json', old_value='same', old_path=T+'platforms.*', changed=False)
save_firm('bulenox', f, notices=[{'what': 'Bulenox terms forbid robots: Wayback only. New capture 2026-10-24 of CMS help_items used; FAQ JSON, Rates PDF and Terms PDF have no capture after E.28.'}],
          gaps=[{'what': 'Bulenox 100%-first-$10k removal rests on absence of the sentence in one capture; third-party pages still list it.'}, {'what': 'Bulenox news rule and BC eligibility carried from E.28 (FAQ not recaptured).'}])
