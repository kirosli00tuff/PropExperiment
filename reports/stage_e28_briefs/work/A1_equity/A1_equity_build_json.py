"""A1_equity: build reports/stage_e28_briefs/A1_equity.json from the facts in A1_equity.md.

Every field is {"value", "unit", "window", "source_file", "quote", "note"}. Source files are relative to
reports/stage_e28_briefs/pages/A1_equity/ unless they start with another folder name.
"""
import json

OUT = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A1_equity.json'


def f(value, unit=None, window=None, source_file=None, quote=None, note=None):
    return {'value': value, 'unit': unit, 'window': window, 'source_file': source_file, 'quote': quote,
            'note': note}


LAUNCH_FILE = 'cftc_ptc041519_micro_emini_launch.txt'
MM_MICRO = f('Micro E-mini Futures Market Maker Program (MES, MNQ, M2K, MYM), quoting obligations', None,
             '2019-05-06 to at least 2020-04-30 (modified 2020-05-01; end date text reads "April 30, 2020 January 31, 2021")',
             'cftc_rule041619_micro_emini_mm_program.txt; cftc_rule041620_micro_emini_mm_mod.txt',
             'participants must quote two-sided markets in the Products at predetermined average bid/ask spreads and '
             'minimum quote sizes during a specified percentage of time-in-market.',
             'Status 2022-2024 not found (WebSearch calls 6, 20). Overstrike lost in text extraction; family F5.')
MM_EMINI = f('CME/CBOT E-mini Equity Index Futures Market Maker Program (ES, NQ, EMD, YM), RTH quoting obligations',
             None, 'start 2013-04-01; end date text "January 31, 2019 January 31, 2021"',
             'cftc_rule012819_emini_eq_mm_program.txt; cftc_rul031214_emini_eq_mm_program.txt',
             'Product Scope E-mini S&P 500 Futures ("ES"), E-mini Nasdaq-100 Futures ("NQ"), E-mini S&P MidCap 400 '
             'Futures ("EMD"), and E-mini Dow ($5) Futures ("YM") on Globex',
             'Participants must also be in the "CME Group E-mini Equity Liquidity Provider Program". Status 2022-2024 '
             'not found (WebSearch call 20).')
MM_RTY = f('E-mini Russell 2000 Futures Market Maker Program, up to 15 participants', None,
           '2017-07-10 to 2017-12-31 or 2018-03-31 (overstrike)', 'cftc_rule053017_RTY_mm_program.txt',
           'Participants must quote continuous two-sided markets in the Products at maximum bid/ask spreads and minimum '
           'quote sizes.', 'Status after 2018 not found.')

HOURS = f('Sunday-Friday 18:00-17:00 ET (17:00-16:00 CT), daily 17:00-18:00 ET break; 16:15-16:30 ET halt removed '
          'from trade date 2021-06-28', None, 'from 2021-06-28',
          'cme_old_specs_*.html.txt; cftc_rule061421_equity_halt_removal.txt',
          'CME and CBOT will eliminate the 3:15 p.m. - 3:30 p.m. Central Time (CT) trading halt on CME Globex which '
          'currently exists for certain Equity futures and options contracts.',
          'Current schedule inferred from the 2020-21 spec pages plus the 2021 filing; no current CME spec page read. F3.')
LIMITS = f('Overnight: +/-7% hard limit with +/-3.5% dynamic variant; RTH: coordinated with primary listing exchange '
           'MWCB (7%/13%/20%), resume 10 minutes after a regulatory halt', None, 'from trade date 2020-10-12',
           'cftc_ptc093020_rule589_equity_7pct.txt',
           'The Exchanges will amend the Overnight Trading Hours ("OTH") price limits for certain CME and CBOT equity '
           'index futures and options on futures from the current ±5% hard limits to ±7% hard limits.',
           'Before 2020-10-12 the overnight limit was 5% (launch filing, F1). F2.')
LIMIT_HITS = f(4, 'trade dates with RTH circuit-breaker halt (lower bound)', '2019-2024',
               'fr_2021-22941_mwcb.txt',
               'U.S. equities markets experienced four MWCB Level 1 halts, on March 9, 12, 16, and 18, 2020.',
               'All in March 2020; S&P 500 trigger, applies to the whole family (F2 coordination). Overnight 5% '
               'limit hits in March 2020 not verified from a primary source (news pointers only, WebSearch 4, 19). '
               'No sourced hit in 2019, 2021-2024; absence of evidence, not a sourced zero. Mean >= 0.67 per year.')
RELEASES = f(None, 'scheduled product-specific high-impact releases per week', None, None, None,
             'None found in any fetched source; the shared US macro calendar is excluded by the spec. Constituent '
             'earnings and index reconstitutions are not weekly [unverified]. F9.')
WEEKEND = f(False, 'underlying trades while Globex closed', None, None, None,
            'Globex closed Fri 17:00 ET to Sun 18:00 ET (F3). No source found of the index underlyings trading on '
            'weekends; US cash equities not trading on weekends is general knowledge [unverified]. F4.')
JUMPS = f(None, 'days per year with |daily return| > 4 x yearly SD', '2019-2024', 'A0_contract_stats.md', None,
          'Not computed here (owned-bar magnitude, A0). A0 has NQ, RTY, YM; none for the micros.')
SPREAD_MAIN = f(None, 'ticks', 'main session', None, None,
                'No public source found (WebSearch 13, 14; CME RTY liquidity report holds only an interactive chart; '
                'CME Liquidity Tool needs a login). F10.')
SPREAD_ON = f(None, 'ticks', 'overnight', None, None, 'Not found; see spread_main.')
DEPTH = f(None, 'contracts at best bid/ask', 'by session', None, None, 'Not found (F10).')
QUEUE = f(None, 'contracts at the touch', 'main session', None, None, 'Not found (F10).')
OUT_US = f(0.20, 'share of volume outside US trading hours (all four Micro E-mini equity futures)', '2023 to 2023-03-17',
           'cme_pr_20230317_micro_2bn.html.txt', '20% of volume occurs outside of U.S. trading hours',
           'Not split by product. CME OpenMarkets 2024 says 24% (cme_om_2024_micro_five_years_v2.html.txt).')
HEDGER = f(None, 'share of OI', '2022-11-01..2023-10-31', 'cot22/FinFutYY.txt; cot23/FinFutYY.txt', None,
           'CFTC Traders in Financial Futures has no commercial-hedger category; see cot_* fields (Dealer, Asset '
           'Manager, Leveraged Funds, Other Reportables, Nonreportable).')
HFT = f(None, 'share of volume', None, 'cftc_haynes_roberts_2015.txt', None,
        'No HFT share by contract found. CFTC OCE reports classify automated (ATS) vs manual by the CME manual order '
        'indicator, not HFT.')
ES_REL = f('Same MWCB trigger (S&P 500) halts all; micros associated with minis for limits; Rule 855 offset 10 micro '
           '= 1 mini', None, None, 'cftc_ptc041519_micro_emini_launch.txt; fr_2021-22941_mwcb.txt',
           'MNQ/MNQ ... 361 10 NQ/NQ ... 359',
           'No intraday correlation or lead-lag source with ES fetched. F9.')
CASH = f('Main session 09:30-16:00 ET is the cash session; futures trade about 23 hours; RTH limits coordinated with '
         'the primary listing exchange', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt',
         'during Regular Trading Hours ("RTH"), CME and CBOT equity index futures and options on futures contracts are '
         'coordinated with the Primary Listing Exchange price limits.', 'F3, F9.')
RETAIL_PCT = f(None, 'share of volume retail', None, None, None,
               'No CME, CFTC or regulator percentage found (WebSearch 2, 9, 12). Proxies: cot_nonrept_share; for NQ the '
               'CFTC small-trader volume share.')
RETAIL_MICRO = f('CME describes the micros as built for individual/retail traders', None, '2019-2024',
                 'cme_om_2024_micro_five_years_v2.html.txt; cme_micro_emini_faq.html.txt',
                 'At one-tenth the size of its regular E-mini futures contract, the micros offer retail traders an '
                 'opportunity to execute trades with smaller sums and lower margin requirements.',
                 'Qualitative only; also "More than 324 firms and 172,000 unique accounts have traded these contracts in '
                 'the last year" (cme_pr_20230317_micro_2bn.html.txt, all four micros).')
RETAIL_MINI = f(None, None, None, None, None,
                'No CME statement describing the mini as retail found; see small_trader_volume_share and cot_nonrept_share.')
GATE_NOTE = ('Launched before 2023-11 and no delisting found; listing through the window is inferred, no market data '
             'read.')


def studies(rel):
    """rel maps study id to relation for this candidate."""
    base = {
        'R1': ('Rodas (2026) SSRN 10.2139/ssrn.7330219, OFI and queue depletion vs +/-3-tick barrier, 20 RTH sessions of NQ',
               'negative/null', 'crossref_rodas2026_ssrn7330219.json',
               'Neither feature departs measurably from the unconditional base rate: OFI resolves up-first in 49.91% of '
               'races and DEPL in 50.20%, against an unconditional 49.71% and a breakeven requirement of 63.00% at the '
               'measured passive cost line.', 'abstract only; SSRN preprint'),
        'R2': ('Lalor and Swishchuk (2024) arXiv 2409.12721v3, market making with adverse fills on ES, NQ, CL, ZN',
               'negative for naive passive posting', 'arxiv_2409.12721v3_lalor_swishchuk.txt',
               '2024/04/25 NQ Jun24 1929 1269 660',
               'full text; Table 2 = total LO fills, adverse, non-adverse; "excluding adverse fills and realistic '
               'non-adverse fill probabilities substantially inflates trading performance."'),
        'R3': ('Dixon (2017) arXiv 1707.05642 and 1710.03870, RNN price-flip classification on ES level II, Aug 2016',
               'positive (classification), no realistic net test', 'pages/C2_DeepLOB/dixon_rnn_seq2017.txt',
               'The capability to adjust quotes according to this prediction reduces the likelihood of adverse price '
               'selection.', 'file in C2_DeepLOB folder'),
        'R4': ('Baron, Brogaard and Kirilenko (2014 draft) CFTC, HFT risk and return in ES',
               'negative for slow passive traders', 'pages/C2_Control/baron_brogaard_kirilenko_2014_cftc.txt',
               'revenue is concentrated among a small number of HFT firms who achieve greater investment performance '
               'through liquidity-taking activity and higher speed.', 'file in C2_Control folder'),
        'R5': ('Takahashi (2025) arXiv 2508.06788, returns and OFI in ES at 1 s', 'contemporaneous impact only',
               'arxiv_api_abstracts_batch1.xml',
               'Impulse responses indicate that shocks dissipate almost entirely within a second.', 'abstract only'),
        'R6': ('Fassas (2021) J. Derivatives 10.3905/jod.2021.1.131, price discovery micros vs minis',
               'not a predictability test', 'icbe_fassas_micro_emini.html.txt',
               'they contribute approximately equal amounts to the information transmission process with the '
               'established E-Mini index futures.', 'abstract only'),
        'R7': ('Kurov (2008) JFM 10.1002/fut.20341, NQ tick size cut 2006', 'not a predictability test',
               'crossref_kurov2008_fut20341.json',
               'The results show a significant reduction in the effective spreads in both of the contract markets but '
               'especially in the electronically traded E-mini futures.', 'abstract only'),
        'R8': ('Mesfin (2026) arXiv 2605.04004 and 2605.17724, MNQ 5-minute OHLCV signals 2021-2025',
               'null (bar-based, not order-book)', 'arxiv_api_abstracts_batch1.xml',
               'Fourteen signal families were evaluated on 947 trading days of five-minute data from 2021-2025 ... None '
               'passed all five.', 'abstract only; arXiv preprints'),
    }
    out = []
    for k, r in rel.items():
        t, res, src, q, n = base[k]
        out.append({'id': k, 'study': t, 'relation': r, 'result': res, 'source_file': src, 'quote': q, 'note': n})
    return f(out, None, None, None, None,
             'Relation: SAME / MMF (micro, mini or full version) / COUSIN (CME Globex equity index) / CLASS. '
             'No study on RTY, M2K, YM or MYM order books found (Crossref, arXiv, WebSearch 15, 16). F11.')


def cot(code, name, n, first, last, oi, dealer, am, lev, other, nonrep, traders):
    win = f'{first}..{last} ({n} weekly reports in 2022-11-01..2023-10-31)'
    src = 'cot22/FinFutYY.txt; cot23/FinFutYY.txt (work/A1_equity/A1_equity_cot_out.txt)'
    note = (f'CFTC code {code}, market "{name}". Share = (long+short+2*spread)/(2*OI), mean over reports. '
            'Computed by work/A1_equity/A1_equity_cot.py.')
    return {
        'cot_reports_in_window': f(n, 'weekly reports', win, src, None, note),
        'cot_mean_open_interest': f(oi, 'contracts', win, src, None, note),
        'cot_dealer_share': f(dealer, 'share of OI', win, src, None, note),
        'cot_asset_mgr_share': f(am, 'share of OI', win, src, None, note),
        'cot_lev_money_share': f(lev, 'share of OI', win, src, None, note),
        'cot_other_rept_share': f(other, 'share of OI', win, src, None, note),
        'cot_nonrept_share': f(nonrep, 'share of OI (small-trader proxy)', win, src, None, note),
        'cot_mean_reportable_traders': f(traders, 'traders', win, src, None, note),
    }


def adv(code, nov, dec, y22, octv, ytd, oi_nov, oi_dec, oi_oct, derived, oi_note=None):
    s = 'cme_eqreview_2022-11.html.txt; cme_eqreview_2022-12.html.txt; cme_eqreview_2023-10.html.txt'
    return {
        'adv_nov2022': f(nov, 'contracts/day', '2022-11', 'cme_eqreview_2022-11.html.txt', None, 'CME monthly review'),
        'adv_dec2022': f(dec, 'contracts/day', '2022-12', 'cme_eqreview_2022-12.html.txt', None, 'CME monthly review'),
        'adv_2022_full_year': f(y22, 'contracts/day', '2022-01..2022-12', 'cme_eqreview_2022-12.html.txt', None,
                                'YTD through December 31, 2022'),
        'adv_oct2023': f(octv, 'contracts/day', '2023-10', 'cme_eqreview_2023-10.html.txt', None, None),
        'adv_ytd_jan_oct_2023': f(ytd, 'contracts/day', '2023-01..2023-10', 'cme_eqreview_2023-10.html.txt',
                                  '*Through October 31, 2023', None),
        'adv_derived_2022-11_2023-10': f(derived, 'contracts/day', '2022-11-01..2023-10-31', s, None,
                                         'Derived: (Nov22*21 + Dec22*21 + JanOct23*209)/251 with ASSUMED trade-date '
                                         'counts; approximation.'),
        'open_interest_end_month': f({'2022-11': oi_nov, '2022-12': oi_dec, '2023-10': oi_oct}, 'contracts', None, s,
                                     None, oi_note),
    }


def common(gate_launch_src, gate_launch_quote):
    return {
        'traded_60_dates_pilot_window': f(True, 'boolean (inferred)', '2023-11-01..2024-02-29', gate_launch_src,
                                          gate_launch_quote, GATE_NOTE),
        'trading_hours': HOURS, 'price_limits': LIMITS, 'limit_hit_days_2019_2024': LIMIT_HITS,
        'product_specific_releases_per_week': RELEASES, 'weekend_gap_exposure': WEEKEND, 'jump_frequency': JUMPS,
        'median_spread_ticks_main': SPREAD_MAIN, 'median_spread_ticks_overnight': SPREAD_ON,
        'depth_best_level': DEPTH, 'touch_queue_size': QUEUE,
        'volume_per_minute_main': f(None, 'contracts/minute', '2022-11-01..2023-10-31', 'A0_contract_stats.md', None,
                                    'Owned-bar magnitude, A0 (NQ, RTY, YM only).'),
        'commercial_hedger_share': HEDGER, 'hft_share': HFT, 'relation_to_es_mes': ES_REL,
        'relation_to_cash_hours': CASH, 'retail_share_pct': RETAIL_PCT,
    }


MICRO_LAUNCH_Q = 'Start date is May 6, 2019.'
MICRO_LAUNCH_S = 'cftc_rule041619_micro_emini_mm_program.txt; cftc_ptc041519_micro_emini_launch.txt'


def build():
    c = []
    # MNQ
    d = {'candidate': 'MNQ', 'baseline': True,
         'product_name': f('Micro E-mini Nasdaq-100 Index Futures', None, None, LAUNCH_FILE,
                           'Micro E-mini Nasdaq-100 Index Futures', None),
         'code': f('MNQ', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt',
                   'Micro E-mini NASDAQ-100 Index Futures 361 MNQ Associated NQ', 'CME, rulebook chapter 361'),
         'contract_size': f('$2 x Nasdaq-100 Index', 'USD per index point', None,
                            'cme_old_specs_micro-e-mini-nasdaq-100.html.txt', '$2 x Nasdaq-100 Index', 'Wayback 2020-12-01'),
         'tick_size': f(0.25, 'index points', None, LAUNCH_FILE,
                        'Micro E-mini Nasdaq-100 Index Futures: 0.25 Index points, equal to $0.50 per contract', None),
         'tick_value': f(0.50, 'USD', None, LAUNCH_FILE,
                         'Micro E-mini Nasdaq-100 Index Futures: 0.25 Index points, equal to $0.50 per contract', None),
         'launch_date': f('2019-05-06', 'date', None, MICRO_LAUNCH_S, MICRO_LAUNCH_Q,
                          'SER-8360 (trade date Monday, May 6, 2019) seen only as a search snippet.'),
         'matching_algorithm': f('FIFO', None, 'at launch 2019', LAUNCH_FILE, 'F: First In, First Out (FIFO)', None),
         'market_maker_program': MM_MICRO,
         'ats_share': f(None, 'share of volume', None, 'cftc_ats_update2_2019.txt', None,
                        'CFTC OCE tables cover NQ, not MNQ (launched after their samples).'),
         'small_trader_volume_share': f(None, 'share of volume', None, None, None, 'Not published for MNQ.'),
         'retail_description': RETAIL_MICRO,
         'outside_us_hours_volume_share': OUT_US,
         'adv_latest_published': f({'2025 full year': 1600000, 'Q3 2026': 2600000, '2026-09': 2400000},
                                   'contracts/day', '2025; 2026-07..09; 2026-09',
                                   'cme_pr_20260105_annual2025.html.txt; cme_pr_20261002_sep_q3_2026.html.txt',
                                   'Record annual Micro E-mini Nasdaq-100 futures ADV of 1.6 million contracts',
                                   'Rounded figures in CME releases.'),
         'microstructure_studies': studies({'R1': 'MMF', 'R2': 'MMF', 'R6': 'SAME', 'R8': 'SAME', 'R7': 'MMF',
                                            'R3': 'COUSIN', 'R4': 'COUSIN', 'R5': 'COUSIN'})}
    d.update(common(MICRO_LAUNCH_S, MICRO_LAUNCH_Q))
    d.update(adv('MNQ', 1241292, 1096418, 1453985, 1420645, 1114224, 121214, 66138, 110189, 1123365))
    d.update(cot('209747', 'MICRO E-MINI NASDAQ-100 INDEX - CHICAGO MERCANTILE EXCHANGE', 53, '2022-11-01',
                 '2023-10-31', 113447, 0.051, 0.019, 0.452, 0.041, 0.438, 42))
    c.append(d)
    # NQ
    nq_launch_q = 'Since the product launch in June 1999, more than 636 million E-mini'
    d = {'candidate': 'NQ', 'baseline': False,
         'product_name': f('E-mini Nasdaq-100 Futures', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt',
                           'E-mini NASDAQ 100 Futures 359 NQ Primary', None),
         'code': f('NQ', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt', 'E-mini NASDAQ 100 Futures 359 NQ Primary',
                   'CME, chapter 359'),
         'contract_size': f('$20 x Nasdaq-100 Index', 'USD per index point', None,
                            'cme_old_specs_e-mini-nasdaq-100.html.txt', '$20 x Nasdaq-100 Index', 'Wayback 2021-01-15'),
         'tick_size': f(0.25, 'index points', None, 'cme_old_specs_e-mini-nasdaq-100.html.txt',
                        'Outright: 0.25 index points = $5.00', None),
         'tick_value': f(5.00, 'USD', None, 'cme_old_specs_e-mini-nasdaq-100.html.txt',
                         'Outright: 0.25 index points = $5.00', None),
         'launch_date': f('1999-06', 'month', None, 'mondovisione_2009_NQ_10th.html.txt', nq_launch_q,
                          'Reprint of the 2009 CME Group / NASDAQ OMX release; day (June 21) from search snippet only.'),
         'matching_algorithm': f('FIFO', None, '2025 (vendor)', 'databento_cme_matching_algos.html.txt',
                                 'Popular products: ES, NQ, ZN, ZF, ZB, CL outrights',
                                 'Databento blog 2025-08-01 under "First in, first out (FIFO)"; not a CME source.'),
         'market_maker_program': MM_EMINI,
         'ats_share': f(0.740, 'share of volume', '2016-11-01..2018-10-31', 'cftc_ats_update2_2019.txt',
                        'E-mini NASDAQ 100 134 176 77.1 74.0 22.2 25.4 60.1 54.4 33.9 39.1 5.2 5.8',
                        'Columns: volume mm (two periods), ATS, MAN, ATS-ATS, ATS-MAN, MAN-MAN; second period values '
                        'ATS 74.0, ATS-ATS 54.4, MAN-MAN 5.8. Automated by CME manual order flag, not HFT.'),
         'small_trader_volume_share': f(0.370, 'share of volume', '2016-11-01..2018-10-31', 'cftc_ats_update2_2019.txt',
                                        'E-mini NASDAQ 100 59,030 58,910 16.8 17.5 17.2 19.5 446 410 60.3 56.5 5.0 5.8',
                                        'Small = accounts below 0.5% of daily volume; 17.5 ATS + 19.5 MAN. 2012-2014: '
                                        '37.4% (cftc_haynes_roberts_2015.txt, Table 6).'),
         'retail_description': RETAIL_MINI,
         'outside_us_hours_volume_share': f(None, 'share of volume', None, None, None, 'Not found for NQ.'),
         'adv_latest_published': f(None, 'contracts/day', None, None, None,
                                   'No product ADV for NQ after 2023-10 found in CME releases fetched.'),
         'microstructure_studies': studies({'R1': 'SAME', 'R2': 'SAME', 'R7': 'SAME', 'R8': 'MMF', 'R6': 'MMF',
                                            'R3': 'COUSIN', 'R4': 'COUSIN', 'R5': 'COUSIN'})}
    d.update(common('mondovisione_2009_NQ_10th.html.txt; cot23/FinFutYY.txt', nq_launch_q))
    d.update(adv('NQ', 624366, 657682, 699898, 762475, 671995, 256803, 241785, 259306, 666813,
                 'A0 owned ADV median for the standard window: 618,345 (A0_contract_stats.md).'))
    d.update(cot('209742', 'NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE', 53, '2022-11-01', '2023-10-31', 263220,
                 0.215, 0.269, 0.289, 0.071, 0.157, 291))
    c.append(d)
    # RTY
    rty_s = 'cftc_ptc041317_cme003_RTY_listing.txt'
    rty_q = 'effective on Sunday, July 9, 2017, for trade date of Monday, July 10, 2017.'
    d = {'candidate': 'RTY', 'baseline': False,
         'product_name': f('E-mini Russell 2000 Index Futures', None, None, rty_s, 'E-mini® Russell 2000® Index Futures',
                           None),
         'code': f('RTY', None, None, rty_s, 'E-mini Russell 2000 Index RTY RLT', 'CME, chapter 393; BTIC RLT'),
         'contract_size': f('$50 x Russell 2000 Index', 'USD per index point', None,
                            'cme_old_specs_e-mini-russell-2000.html.txt', '$50 x Russell 2000 Index', 'Wayback 2021-01-25'),
         'tick_size': f(0.10, 'index points', None, 'cme_old_specs_e-mini-russell-2000.html.txt',
                        'Outright: 0.10 index points = $5.00', None),
         'tick_value': f(5.00, 'USD', None, 'cme_old_specs_e-mini-russell-2000.html.txt',
                         'Outright: 0.10 index points = $5.00', None),
         'launch_date': f('2017-07-10', 'date (at CME)', None, rty_s, rty_q, 'Traded on ICE before (pointer only).'),
         'matching_algorithm': f('FIFO', None, 'at listing 2017', rty_s, 'F: First In First Out (FIFO)', None),
         'market_maker_program': MM_RTY,
         'ats_share': f(None, 'share of volume', None, 'cftc_ats_update2_2019.txt', None,
                        'CFTC OCE samples end 2018-10 and list NQ, YM, ES only among US index futures top products.'),
         'small_trader_volume_share': f(None, 'share of volume', None, None, None, 'Not published for RTY.'),
         'retail_description': RETAIL_MINI,
         'outside_us_hours_volume_share': f(None, 'share of volume', None, None, None, 'Not found for RTY.'),
         'adv_latest_published': f({'Q4 2025': 218000}, 'contracts/day', '2025-10..2025-12',
                                   'cme_pr_20260105_annual2025.html.txt',
                                   'E-Mini Russell 2000 futures ADV increased 20% to 218,000 contracts', None),
         'microstructure_studies': studies({'R1': 'COUSIN', 'R2': 'COUSIN', 'R3': 'COUSIN', 'R4': 'COUSIN',
                                            'R5': 'COUSIN', 'R6': 'MMF'})}
    d.update(common(rty_s, rty_q))
    d.update(adv('RTY', 190254, 236193, 237489, 231303, 218224, 483060, 445567, 559075, 217387,
                 '2023-10 Russell "Futures" OI subtotal 605,940 != RTY + M2K 582,096 (one cell inconsistent). A0 owned '
                 'ADV median 181,060.'))
    d.update(cot('239742', 'RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE', 53, '2022-11-01', '2023-10-31', 494756,
                 0.207, 0.450, 0.232, 0.063, 0.049, 337))
    c.append(d)
    # M2K
    d = {'candidate': 'M2K', 'baseline': False,
         'product_name': f('Micro E-mini Russell 2000 Index Futures', None, None, LAUNCH_FILE,
                           'Micro E-mini Russell 2000 Index Futures', None),
         'code': f('M2K', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt',
                   'Micro E-mini Russell 2000 Index Futures 363 M2K Associated RTY', 'CME, chapter 363'),
         'contract_size': f('$5 x Russell 2000 Index', 'USD per index point', None,
                            'cme_old_specs_micro-e-mini-russell-2000.html.txt', '$5 x Russell 2000 Index',
                            'Wayback 2021-01-15'),
         'tick_size': f(0.10, 'index points', None, LAUNCH_FILE,
                        'Micro E-mini Russell 2000 Index Futures: 0.10 Index points, equal to $0.50 per contract', None),
         'tick_value': f(0.50, 'USD', None, LAUNCH_FILE,
                         'Micro E-mini Russell 2000 Index Futures: 0.10 Index points, equal to $0.50 per contract', None),
         'launch_date': f('2019-05-06', 'date', None, MICRO_LAUNCH_S, MICRO_LAUNCH_Q, None),
         'matching_algorithm': f('FIFO', None, 'at launch 2019', LAUNCH_FILE, 'F: First In, First Out (FIFO)', None),
         'market_maker_program': MM_MICRO,
         'ats_share': f(None, 'share of volume', None, None, None, 'Not published.'),
         'small_trader_volume_share': f(None, 'share of volume', None, None, None, 'Not published.'),
         'retail_description': RETAIL_MICRO, 'outside_us_hours_volume_share': OUT_US,
         'adv_latest_published': f(None, 'contracts/day', None, None, None, 'No product ADV after 2023-10 found.'),
         'microstructure_studies': studies({'R6': 'SAME', 'R1': 'COUSIN', 'R2': 'COUSIN', 'R3': 'COUSIN',
                                            'R4': 'COUSIN', 'R5': 'COUSIN'})}
    d.update(common(MICRO_LAUNCH_S + '; cme_eqreview_2023-10.html.txt', MICRO_LAUNCH_Q))
    d.update(adv('M2K', 106682, 82745, 130807, 78372, 76712, 24794, 14471, 23021, 79724,
                 'No owned bars before 2025-04-01 (A0).'))
    d.update(cot('239747', 'MICRO E-MINI RUSSELL 2000 INDX - CHICAGO MERCANTILE EXCHANGE', 6, '2022-11-29',
                 '2023-10-24', 24229, 0.054, 0.022, 0.441, 0.043, 0.439, 21))
    c.append(d)
    # YM
    d = {'candidate': 'YM', 'baseline': False,
         'product_name': f('E-mini Dow ($5) Futures', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt',
                           'CBOT E-mini Dow Jones Industrial Average Index Futures ($5 Multiplier) 27 YM Primary', None),
         'code': f('YM', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt',
                   'CBOT E-mini Dow Jones Industrial Average Index Futures ($5 Multiplier) 27 YM Primary',
                   'CBOT, chapter 27'),
         'contract_size': f('$5 x DJIA', 'USD per index point', None, 'cme_old_specs_e-mini-dow.html.txt',
                            '$5 x Dow Jones Industrial Average ("DJIA")', 'Wayback 2020-12-03'),
         'tick_size': f(1.00, 'index points', None, 'cme_old_specs_e-mini-dow.html.txt', '1.00 index point = $5.00', None),
         'tick_value': f(5.00, 'USD', None, 'cme_old_specs_e-mini-dow.html.txt', '1.00 index point = $5.00', None),
         'launch_date': f(None, 'date', None, 'cftc_haynes_roberts_2015.txt',
                          'Equities - US Index E-mini Dow ($5) 73 60.9 33.6 5.4',
                          'Exact date not fetched (commonly April 2002 at CBOT, unverified); traded by 2012-11 (CFTC '
                          'sample November 12, 2012 - October 31, 2014).'),
         'matching_algorithm': f(None, None, None, None, None,
                                 'Not found in fetched filings; Databento FIFO list names ES, NQ, ZN, ZF, ZB, CL only; the '
                                 'associated micro MYM is FIFO.'),
         'market_maker_program': MM_EMINI,
         'ats_share': f(0.812, 'share of volume', '2016-11-01..2018-10-31', 'cftc_ats_update2_2019.txt',
                        'E-mini Dow ($5) 82 88 80.2 81.2 19.7 18.7 64.6 66.1 31.1 30.1 4.1 3.6',
                        'Second period: ATS 81.2, ATS-ATS 66.1, MAN-MAN 3.6.'),
         'small_trader_volume_share': f(None, 'share of volume', None, None, None,
                                        'CFTC small/large table covers 13 products; YM not among them.'),
         'retail_description': RETAIL_MINI,
         'outside_us_hours_volume_share': f(None, 'share of volume', None, None, None, 'Not found for YM.'),
         'adv_latest_published': f(None, 'contracts/day', None, None, None, 'No product ADV after 2023-10 found.'),
         'microstructure_studies': studies({'R1': 'COUSIN', 'R2': 'COUSIN', 'R3': 'COUSIN', 'R4': 'COUSIN',
                                            'R5': 'COUSIN', 'R6': 'MMF'})}
    d.update(common('cftc_haynes_roberts_2015.txt; cot23/FinFutYY.txt', None))
    d.update(adv('YM', 200321, 182876, 202211, 208407, 175187, 79187, 76110, 103936, 177933,
                 'A0 owned ADV median 163,416.'))
    d.update(cot('124603', 'DJIA x $5 - CHICAGO BOARD OF TRADE', 53, '2022-11-01', '2023-10-31', 91745,
                 0.311, 0.155, 0.244, 0.130, 0.160, 93))
    c.append(d)
    # MYM
    d = {'candidate': 'MYM', 'baseline': False,
         'product_name': f('Micro E-mini Dow Jones Industrial Average Index Futures', None, None, LAUNCH_FILE,
                           'Micro E-mini Dow Jones Industrial Average Index Futures', 'CBOT'),
         'code': f('MYM', None, None, 'cftc_ptc093020_rule589_equity_7pct.txt',
                   'Micro E-mini Dow Index Futures 28 MYM Associated YM', 'CBOT, chapter 28'),
         'contract_size': f('$0.50 x DJIA', 'USD per index point', None, 'cme_old_specs_micro-e-mini-dow.html.txt',
                            '$0.50 x DJIA Index', 'Wayback 2020-12-02'),
         'tick_size': f(1.00, 'index points', None, LAUNCH_FILE,
                        'Micro E-mini Dow Jones Industrial Average Index Futures: 1.00 Index points, equal to $0.50 per '
                        'contract', None),
         'tick_value': f(0.50, 'USD', None, LAUNCH_FILE,
                         'Micro E-mini Dow Jones Industrial Average Index Futures: 1.00 Index points, equal to $0.50 per '
                         'contract', None),
         'launch_date': f('2019-05-06', 'date', None, MICRO_LAUNCH_S, MICRO_LAUNCH_Q, None),
         'matching_algorithm': f('FIFO', None, 'at launch 2019', LAUNCH_FILE, 'F: First In, First Out (FIFO)', None),
         'market_maker_program': MM_MICRO,
         'ats_share': f(None, 'share of volume', None, None, None, 'Not published.'),
         'small_trader_volume_share': f(None, 'share of volume', None, None, None, 'Not published.'),
         'retail_description': RETAIL_MICRO, 'outside_us_hours_volume_share': OUT_US,
         'adv_latest_published': f(None, 'contracts/day', None, None, None, 'No product ADV after 2023-10 found.'),
         'microstructure_studies': studies({'R6': 'SAME', 'R1': 'COUSIN', 'R2': 'COUSIN', 'R3': 'COUSIN',
                                            'R4': 'COUSIN', 'R5': 'COUSIN'})}
    d.update(common(MICRO_LAUNCH_S + '; cme_eqreview_2023-10.html.txt', MICRO_LAUNCH_Q))
    d.update(adv('MYM', 153494, 138518, 179017, 115096, 108504, 37630, 20722, 25224, 114779,
                 'IMPLIED values (Dow futures OI subtotal minus YM); the listed MYM OI cells copy MNQ OI (copy error in '
                 'CME table). No owned bars before 2025-04-01 (A0).'))
    d.update(cot('124608', 'MICRO E-MINI DJIA (x$0.5) - CHICAGO BOARD OF TRADE', 20, '2022-11-22', '2023-08-01', 29312,
                 0.027, 0.015, 0.418, 0.065, 0.475, 21))
    c.append(d)
    return c


if __name__ == '__main__':
    data = build()
    for d in data:  # every field except candidate/baseline must have the six keys
        for k, v in d.items():
            if k in ('candidate', 'baseline'):
                continue
            assert set(v) == {'value', 'unit', 'window', 'source_file', 'quote', 'note'}, k
    with open(OUT, 'w') as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
    print(len(data), 'candidates;', sorted({len(d) for d in data}), 'keys each')
