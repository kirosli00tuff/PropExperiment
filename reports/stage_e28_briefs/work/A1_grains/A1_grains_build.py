"""A1_grains: build A1_grains.json (one object per candidate, every field {value, unit, window, source_file, quote,
note}) and the per-candidate sheet tables appended to A1_grains.md. All values and quotes are typed from the saved
source files (see A1_grains.md family sections F1-F10)."""
import json

P = 'reports/stage_e28_briefs/pages/A1_grains/'
OUT_JSON = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A1_grains.json'
OUT_MD = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A1_grains.md'


def f(value, unit=None, window=None, src=None, quote=None, note=None):
    return {'value': value, 'unit': unit, 'window': window,
            'source_file': (P + src) if src and not src.startswith('reports/') else src,
            'quote': quote, 'note': note}


# ---------- shared facts ----------
HOURS = f('Sun-Fri 19:00-07:45 CT and Mon-Fri 08:30-13:20 CT (17:00-05:45 and 06:30-11:20 America/Vancouver)',
          None, 'current (2025 SER; same for all grain classes)', 'cme_ser9512_micro_grains.txt',
          'CME Globex: Sunday - Friday: 7:00 p.m. - 7:45 a.m. CT and Monday - Friday, 8:30 a.m. - 1:20 p.m. CT',
          'cme_faq_micro_ag.html.txt: "All three classes of futures share the same expiration months and trading '
          'times". The day session ends 11:20 PT, before the stage main-session window ends (13:00 PT).')
RELEASES = f('In season (Apr-Nov): 2 weekly product-specific USDA releases (Crop Progress Mon 16:00 ET; Export Sales '
             'Thu 08:30 ET), plus monthly WASDE/Crop Production (12:00 ET) and quarterly Grain Stocks; out of season: '
             '1 weekly (Export Sales) plus monthly/quarterly', 'releases per week', '2026 calendars',
             'usda_wasde_report.html.txt; nass_calendar.html.txt; fas_export_sales_wb.html.txt',
             '"2026 WASDE Release Dates (12:00pm ET)"; "4:00 pm ET|- Crop Progress"; "FAS publishes a weekly summary '
             'of export sales activity every Thursday at 8:30 a.m. ET"',
             'Crop Progress season months [unverified]. Whether Export Sales counts as high impact is for the scorer.')
USDA_TIMING = f('WASDE and Crop Production 12:00 ET (11:00 CT, inside the day session); Grain Stocks with them at '
                'noon ET [quarterly dates unverified]; Crop Progress Monday 16:00 ET (after the 13:20 CT close); '
                'Export Sales Thursday 08:30 ET (overnight session)', None, '2026; noon release since January 2013',
                'usda_wasde_report.html.txt; agecon_285883.txt',
                '"Since May 21, 2012, all sensitive USDA reports are released during trading hours (at 7:30:00 am CT '
                'until December 2012 and at 11:00:00 am CT since January 2013)."', None)
WEEKEND = f('no weekend-traded underlying found', None, None, 'cme_ser9512_micro_grains.txt',
            'CME Globex: Sunday - Friday: 7:00 p.m. - 7:45 a.m. CT and Monday - Friday, 8:30 a.m. - 1:20 p.m. CT',
            'Globex closes Fri 13:20 CT and reopens Sun 19:00 CT; cash grain markets do not trade continuously over '
            'the weekend (no source checked for weekend OTC grain trading). Weekend weather news can gap the open.')
LIMIT_HITS_UNKNOWN = f(None, 'days per year', '2019-2024', 'cftc_ptc030422_wheat_limits.txt',
                       'Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent '
                       'of all daily price movements, making limit days rare.',
                       'No count of limit-settle days 2019-2024 was found (WebSearch calls 8 and 9; CBOT filings '
                       '2022-2023). A0 owned bars can count them.')
HFT_GROUP = ('cftc_haynes_roberts_2017_update.txt',
             'Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7) 49.0 (3.9) 55.4 (3.8) 46.9 (3.8)')
MATCH_K = f('Configurable (CME algorithm K): TOP order first, then split 40% FIFO / 60% pro rata (with leveling), '
            'then FIFO residual', None, 'K for ZC/ZS/ZW outrights: Databento 2025-08; 40/60 split: Peng (2022) for '
            'the 2018 sample', 'databento_cme_matching_algos.html.txt; ideals_2022_three_essays_ag_liquidity.txt',
            'Databento: "Configurable ... Popular CME products: ZT, ZQ, ZC, ZS, ZW outrights". Peng: "Throughout our '
            'sample period, the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural '
            'futures and spread futures markets. ... allocated on a "40 percent FIFO and 60 percent Pro-Rata" basis."',
            'Primary per-product parameters (GCC Product Reference Sheet) not retrieved; current split unverified '
            'against CME.')
MATCH_UNKNOWN = f(None, None, None, 'ideals_2022_three_essays_ag_liquidity.txt',
                  'the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and '
                  'spread futures markets',
                  'Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT '
                  'agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified.')
MM_NONE_FULL = f('none current found; historical CBOT overnight Corn/Wheat/Soybean futures market-maker program '
                 '2009-11-01..2010-12-31 and ETH fee incentive 2011-10-17..2011-12-31', None, 'checked 2026-10-21',
                 'cbot_fee_schedule_2026-10-01.txt; cftc_rul100909cbot001.txt; cftc_rul093011cbot001.txt',
                 'Fee Waiver table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted '
                 'Futures - Dow Jones (QDF)", "Rapeseed Oil Futures (RSO)"',
                 'Two WebSearches (calls 5, 6). CME market-maker programs are not always public; absence in search is '
                 'not proof of none. The 2009 overnight program covered Corn, Wheat and Soybean only.')
WEEK = '2022-11-01..2023-10-31 (53 weekly reports)'
LAT = '2025-10-14..2026-10-13 (53 weekly reports)'
COT_SRC = 'reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt'
ADV26 = 'cme_web_adv_report_2026-10.txt'
ADV23 = 'cme_web_adv_report_2023-09.txt'


def cot(code, name, w_oi, w_pm, w_nr, l_oi, l_pm, l_nr, line_w, line_l):
    return {
        'open_interest': f({'2022-11..2023-10_mean': w_oi, 'latest_52wk_mean': l_oi}, 'contracts (futures-only OI)',
                           f'{WEEK}; {LAT}', COT_SRC, line_w + ' || ' + line_l,
                           f'CFTC Disaggregated COT, {name} ({code}); computed from cftc_fut_disagg_txt_*.zip'),
        'commercial_hedger_share': f({'2022-11..2023-10': w_pm, 'latest_52wk': l_pm}, 'share of OI positions',
                                     f'{WEEK}; {LAT}', COT_SRC, line_w,
                                     'Producer/Merchant/Processor/User share = mean (long+short)/(2 OI). Position '
                                     'share, not volume share.'),
        'nonreportable_share': f({'2022-11..2023-10': w_nr, 'latest_52wk': l_nr}, 'share of OI positions',
                                 f'{WEEK}; {LAT}', COT_SRC, line_w, 'small-trader proxy'),
    }


def research(rows, note=None):
    return f(rows, None, None, 'see A1_grains.md F10', None, note)


R_HU = {'study': 'Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics', 'relation': None, 'result':
        'gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted',
        'file': 'ideals_hu_2020_three_essays.txt'}
R_VOLK = {'study': 'Volkenand, Filler, Odening (2018) AFR, order imbalance', 'relation': None,
          'result': 'positive (lagged order imbalance predicts returns for some contracts) [abstract only]',
          'file': 'openalex_10_1108_afr_10_2017_0099.json'}
R_ARZ = {'study': 'Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes', 'relation': None,
         'result': 'positive for LOB information share (40-42% for grains); not a trading test',
         'file': 'agecon_259344.txt'}
R_SHANG = {'study': 'Shang, Mallory, Garcia (2016/2018), spread components', 'relation': None,
           'result': 'adverse selection 12.1% of spread on average, 15.0% on USDA days; mixed',
           'file': 'agecon_285856.txt'}
R_HE = {'study': 'He, Serra, Garcia (2018; AJAE 2020), spread resilience and flash events', 'relation': None,
        'result': 'spread reverts within 15-40 s; active market making (professional liquidity provision)',
        'file': 'agecon_285890.txt; openalex_10_1111_ajae_12146.json'}
R_COUL = {'study': 'Couleau, Serra, Garcia (2020 AJAE), jumps', 'relation': None,
          'result': 'jumps cluster on USDA report days (2.30 per announcement day since 2013)',
          'file': 'agecon_285883.txt'}
R_JOS = {'study': 'Joseph and Garcia (2017), soybean announcements', 'relation': None,
         'result': 'null (no systematic under/overreaction)', 'file': 'agecon_235772.txt'}
R_LEH = {'study': 'Lehecka, Wang, Garcia (2014 AEPP)', 'relation': None,
         'result': 'null (reactions done in ~10 min) [abstract only]', 'file': 'openalex_10_1093_aepp_ppu010.json'}
R_DEB = {'study': 'de Boer et al. (2022 JFM), soybean complex LOB liquidity', 'relation': None,
         'result': 'liquidity spillovers within 30 s across ZS/ZL/ZM; not return predictability [abstract only]',
         'file': 'wur_soy_complex_liquidity.html.txt'}


def rel(r, relation):
    return dict(r, relation=relation)


def full_size(sym, name, chapter, tick_q, tick_size, tick_value, size_q, size, adv26_line, adv23_line, adv26_val,
              adv23_val, cotd, extra):
    d = {
        'candidate': sym, 'family': 'grains',
        'product_name': f(name, None, None, extra['ch_file'], extra['ch_title_q']),
        'product_code': f(sym, None, None, extra.get('code_file', 'cme_ser9151_price_limit_amend.txt'),
                          extra['code_q']),
        'tick_size': f(tick_size[0], tick_size[1], None, extra['ch_file'], tick_q),
        'tick_value': f(tick_value, 'USD per contract', None, extra['ch_file'], tick_q),
        'contract_size': f(size[0], size[1], None, extra['ch_file'], size_q),
        'settlement': f('physical delivery', None, None, extra['ch_file'], extra['deliv_q']),
        'launch_date': f('before 2023-11 (exact date not sourced; long-listed CBOT contract)', None, None, ADV23,
                         adv23_line, 'Listed in CME ADV report (Aug 2023) and in every weekly CFTC COT report '
                         '2022-11..2023-10 and 2025-10..2026-10.'),
        'globex_60_dates_in_2023-11..2024-02': f(True, None, '2023-11-01..2024-02-29', ADV26, adv26_line,
                                                  'Inferred from continuous listing and trading before and after '
                                                  'the window (2023 and 2026 ADV rows; weekly COT). No market data '
                                                  'for the window was read.'),
        'match_algorithm': MATCH_K if sym in ('ZC', 'ZS', 'ZW') else MATCH_UNKNOWN,
        'trading_hours': HOURS,
        'price_limits': extra['limits'],
        'limit_hit_days_2019_2024': extra.get('limit_hits', LIMIT_HITS_UNKNOWN),
        'adv_published_latest': f(adv26_val, 'contracts/day, all expiries, all venues',
                                  'YTD Jan-Sep 2026 (also Sep 2026 month)', ADV26, adv26_line,
                                  'CME Exchange ADV Report; not a trailing 12 months; Globex not split out.'),
        'adv_2022_11_2023_10': f(adv23_val, 'contracts/day, all expiries, all venues', 'YTD Jan-Aug 2023 (partial '
                                 'window)', ADV23, adv23_line, 'Owned-bar ADV for the full window belongs to A0.'),
        'retail_share': f(None, None, None, 'cftc_haynes_roberts_2015.txt', extra.get('retail_q'),
                          extra.get('retail_note', 'No retail share published for this product found.')),
        'market_maker_program': MM_NONE_FULL if sym in ('ZC', 'ZS', 'ZW') else f(
            'none current found', None, 'checked 2026-10-21', 'cbot_fee_schedule_2026-10-01.txt',
            'Fee Waiver table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted '
            'Futures - Dow Jones (QDF)", "Rapeseed Oil Futures (RSO)"',
            'Historical futures market-maker programs found covered Corn, Wheat, Soybeans only (2007-2010); ETH fee '
            'incentive 2011 covered ZL and ZM too (cftc_rul093011cbot001.txt). Not proof that none exists.'),
        'hft_automated_share': extra['hft'],
        'median_spread_ticks_main': extra['spread_main'],
        'median_spread_ticks_overnight': extra['spread_on'],
        'depth_best_level': extra['depth'],
        'touch_queue_size': extra.get('queue', f(None, 'contracts', None, None, None,
                                                 'No queue-size (orders at the touch) figure found; see depth.')),
        'volume_per_minute': extra['vpm'],
        'scheduled_releases_per_week': RELEASES,
        'usda_report_timing': USDA_TIMING,
        'weekend_gap_exposure': WEEKEND,
        'jump_frequency': extra['jump'],
        'microstructure_research': extra['research'],
    }
    d.update(cotd)
    return d


LIM_CORN = f('initial = 7% of 45-day average settlement (nearest 5c, floor 20c/bu in 2019 text), expanded +50%; '
             'reset May and November; since 2023-05-16 one contract settling at limit triggers expansion, and two '
             'consecutive days at expanded raise both levels', 'cents per bushel', 'rule text 2019; amendment 2023',
             'cbot_rulebook_ch10_2019.txt; cme_ser9151_price_limit_amend.txt',
             '"Daily price limits for Corn futures are reset every six months." ... "multiplied by seven percent. The '
             'resulting number, rounded to the nearest 5 cents per bushel, or 20 cents per bushel, whichever is '
             'higher, will be the new initial price limit" ; SER 9151: "if current initial price limits in Corn '
             'Futures are $0.70 per bushel and expanded price limits are $1.05 per bushel"', None)
LIM_SOY = f('initial = 7% of 45-day average settlement (nearest 5c, floor 50c/bu), expanded = 1.5x; reset May and '
            'November; 2023 amendment as for corn', 'cents per bushel', 'PDF 2024-12-31; SER 9151 (2023)',
            'cbot_rulebook_ch11.txt; cme_ser9151_price_limit_amend.txt',
            '"Initial and expanded daily price limits for Soybean futures are reset every six months." ... "rounded to '
            'the nearest 5 cents per bushel, or 50 cents per bushel, whichever is higher, will be the new initial"',
            None)
LIM_WHEAT = f('initial = higher of 7% rule (nearest 5c, floor 30c/bu) for SRW and KC HRW; expanded = 1.5x; 2022 '
              'amendment (one month at limit triggers; consecutive expanded days raise levels), effective 2022-08-29',
              'cents per bushel', 'PDF 2023-02-13; CBOT submission 22-254', 'cbot_rulebook_ch14.txt; '
              'cftc_ptc071522_wheat_limit_rules.txt',
              '"rounded to the nearest 5 cents per bushel, or 30 cents per bushel, whichever is higher, will be the '
              'preliminary new initial price limit" ; "Should one or more Wheat futures contract months within the '
              'first five listed non-spot contracts settle at limit"', None)
LIM_OIL = f('initial = 7% of 45-day average (nearest 0.5c/lb, floor 2c/lb); expanded per rule; 2023 amendment as for '
            'corn', 'cents per pound', 'PDF 2022-12-19; SER 9151', 'cbot_rulebook_ch12.txt; '
            'cme_ser9151_price_limit_amend.txt', '"rounded to the nearest 0.5 cents per pound, or 2 cents per pound, '
            'whichever is higher, will be the new initial price limits"', None)
LIM_MEAL = f('initial = 7% of 45-day average (nearest $5/ton, floor $20/ton); expanded = 1.5x; 2023 amendment',
             'USD per short ton', 'PDF 2025-12-16; SER 9151', 'cbot_rulebook_ch13.txt; '
             'cme_ser9151_price_limit_amend.txt', '"rounded to the nearest 5 dollars per ton, or 20 dollars per ton, '
             'whichever is higher, will be the new initial price limits for Soybean Meal futures"', None)

GR_SPREAD_POOL = f(1.1, 'ticks (mean, grains pooled ZC/ZW/ZS)', 'nearby, 2015-11-23..2016-03-31',
                   'agecon_259344.txt', '0.27 cent (1.1 ticks) for grains',
                   'Mean, not median; all sessions pooled as far as stated.')

ZC = full_size(
    'ZC', 'Corn Futures', 10, 'The minimum fluctuation for Corn futures shall be ¼ cent per bushel ($12.50 per contract),',
    (0.25, 'US cents per bushel'), 12.50, 'The unit of trading shall be 5,000 bushels of corn.', (5000, 'bushels'),
    'CORN 461,528 284,493.81 62.2% 602,349.38 -23.4% 500,733 455,813 9.9%',
    'CORN 320,584 305,121.35 5.1% 345,825 -7.3% 361,462 340,068 6.3%', 500733, 361462,
    cot('002602', 'CORN - CHICAGO BOARD OF TRADE', 1300458, 0.384, 0.114, 1732054, 0.349, 0.092,
        '002602 | CORN - CHICAGO BOARD OF TRADE | 2022-11-01..2023-10-31 ... meanOI=1300458 | ProdMerc=0.384 Swap=0.108 '
        'MM=0.254 OtherRept=0.140 NonRept=0.114',
        '002602 | CORN - CHICAGO BOARD OF TRADE | latest_52wk ... meanOI=1732054 | ProdMerc=0.349 ... NonRept=0.092'),
    {'ch_file': 'cbot_rulebook_ch10_2019.txt', 'ch_title_q': 'Chapter 10 Corn Futures',
     'code_q': 'Corn Futures ZC C 10', 'deliv_q': 'The procedures for trading, clearing, inspection, delivery and '
     'settlement of Corn futures', 'limits': LIM_CORN,
     'retail_q': 'for individual products like corn and soybeans, small traders contribute the majority share of volume',
     'retail_note': 'Not a retail share: "small" = accounts under 0.5% of daily volume (Haynes-Roberts 2015, '
                    '2012-14). Table 6: small traders ATS 18.7% + MAN 36.0% of corn volume.',
     'hft': f({'ATS-ATS': [15.9, 23.1], 'ATS-MAN': [42.8, 45.1], 'MAN-MAN': [34.8, 27.1]}, '% of volume',
              '2012-11..2014-10 and 2014-11..2016-10', 'cftc_haynes_roberts_2017_update.txt',
              'Corn 128 168 15.9 23.1 42.8 45.1 34.8 27.1',
              'Group ATS share: ' + HFT_GROUP[1] + '. Passive: "over 90 percent of passive executed corn orders '
              'remained in the book longer than one second" (2015 report).'),
     'spread_main': f(1.26, 'ticks (mean 0.314 c/bu; tick 0.25 c)', '2008-01-14..2010-01-29, last 40 days before '
                      'expiry month, day session', 'agecon_wang_garcia_irwin_confp04-12.txt',
                      'During the last forty trading days prior to the expiration month, the average BAS is slightly '
                      'more than one tick, 0.314 cents/bushel',
                      'Mean, not median; old window. Pooled grains 2015-16: "0.27 cent (1.1 ticks) for grains" '
                      '(agecon_259344.txt). Shang et al.: "averaging very near to one \'tick\' (0.25 cents)".'),
     'spread_on': f(None, 'ticks', None, None, None, 'No ZC session split found (ZS: night/day spread ratio 1.09-1.11, '
                    'Peng 2022, see F9).'),
     'depth': f({'bid': 377.69, 'ask': 375.27}, 'contracts at best, mean per side', 'nearby, 2015-11-23..2016-03-31',
                'agecon_259344.txt', 'Quant.1 buy 5.91 6.33 377.69 45.26 62.45 160.35 / Quant.1 sell 5.56 6.48 375.27 '
                '43.92 64.00 159.31', 'Columns Live Cattle, Lean Hogs, Corn, Wheat, Soybeans, E-mini S&P 500. Mean, '
                'not median. During large moves 2014-17 "well below 500 contracts" (Peng 2022 citing He et al.).'),
     'vpm': f({'trades_per_min': 39.405, 'contracts_per_trade': 12.07, 'implied_contracts_per_min': 476},
              'per minute', 'trades: 2015-12..2017-05 day session; size: 2015-11..2016-03',
              'ideals_hu_2020_three_essays.txt; agecon_259344.txt',
              'Trades per minute 39.405 33.887 ... ; Volume (contract) ... 12.07',
              'Implied contracts/min is worker arithmetic across two samples (means). Implied QV ~ 376/476 = 0.8 min '
              '(orientation only).'),
     'jump': f({'days_with_jump_share': 0.253, 'jumps_per_announcement_day_since_2013': 2.30,
                'jumps_per_non_announcement_day_since_2013': 0.26}, None, '2008-2015 nearby', 'agecon_285883.txt',
               'We find 495 days with at least one jump, which represents 25.3% of the total trading days',
               'Intraday nonparametric jumps (Lee-Mykland), not the >4 sigma daily-return count of C4 (A0 owned).'),
     'research': research([rel(R_HU, 'same'), rel(R_VOLK, 'same'), rel(R_ARZ, 'same'), rel(R_SHANG, 'same'),
                           rel(R_HE, 'same'), rel(R_COUL, 'same'), rel(R_LEH, 'same'), rel(R_JOS, 'cousin')])})

ZS = full_size(
    'ZS', 'Soybean Futures', 11, 'The minimum fluctuation for soybean futures shall be ¼ cent per bushel ($12.50 per '
    'contract),', (0.25, 'US cents per bushel'), 12.50, 'The unit of trading shall be 5,000 bushels of soybeans.',
    (5000, 'bushels'), 'SOYBEAN 289,853 215,397.62 34.6% 266,856.24 8.6% 301,529 285,015 5.8%',
    'SOYBEAN 189,515 155,104.91 22.2% 226,716.9 -16.4% 243,723 202,811 20.2%', 301529, 243723,
    cot('005602', 'SOYBEANS - CHICAGO BOARD OF TRADE', 676863, 0.438, 0.089, 969705, 0.427, 0.066,
        '005602 | SOYBEANS - CHICAGO BOARD OF TRADE | 2022-11-01..2023-10-31 ... meanOI=676863 | ProdMerc=0.438 '
        'Swap=0.118 MM=0.222 OtherRept=0.133 NonRept=0.089',
        '005602 | SOYBEANS ... latest_52wk ... meanOI=969705 | ProdMerc=0.427 ... NonRept=0.066'),
    {'ch_file': 'cbot_rulebook_ch11.txt', 'ch_title_q': 'Chapter 11 Soybean Futures',
     'code_q': 'Soybean Futures ZS S 11', 'deliv_q': 'The procedures for trading, clearing, inspection, delivery and '
     'settlement of soybean futures', 'limits': LIM_SOY,
     'retail_q': 'for individual products like corn and soybeans, small traders contribute the majority share of volume',
     'retail_note': 'Not a retail share (small = under 0.5% of daily volume). Table 6: small traders ATS 19.2% + MAN '
                    '42.2% of soybean volume (2012-14).',
     'hft': f({'ATS-ATS': [15.2, 25.1], 'ATS-MAN': [42.5, 45.6], 'MAN-MAN': [36.3, 24.1]}, '% of volume',
              '2012-11..2014-10 and 2014-11..2016-10', 'cftc_haynes_roberts_2017_update.txt',
              'Soybean 93 115 15.2 25.1 42.5 45.6 36.3 24.1', 'Group ATS share: ' + HFT_GROUP[1]),
     'spread_main': f(1.118, 'ticks (mean 0.2795 c/bu)', 'H1 2019, day session 08:30-13:20 CT, top-5 contracts '
                      'volume-weighted', 'ideals_2022_three_essays_ag_liquidity.txt',
                      'Bid-ask spread (cents per bushel) 0.2795 0.0063 0.2672 0.2945 0.3055 0.0115 0.2761 0.3402',
                      'Mean of daily volume-weighted spreads; H1 2020: 0.2775 day. Pooled grains 2015-16: 1.1 ticks.'),
     'spread_on': f(1.222, 'ticks (mean 0.3055 c/bu)', 'H1 2019, night session 19:00-07:45 CT',
                    'ideals_2022_three_essays_ag_liquidity.txt',
                    'Bid-ask spread (cents per bushel) 0.2795 0.0063 0.2672 0.2945 0.3055 0.0115 0.2761 0.3402',
                    'Night/day ratio 1.09 (2019), 1.11 (2020: 0.3068/0.2775). Worker arithmetic.'),
     'depth': f({'bid_mean_2015_16': 62.45, 'ask_mean_2015_16': 64.00, 'top_depth_bid_plus_ask_day_2019': 103,
                 'top_depth_bid_plus_ask_night_2019': 43}, 'contracts', '2015-11..2016-03 (per side); H1 2019 '
                'and H1 2020 (both sides summed)', 'agecon_259344.txt; ideals_2022_three_essays_ag_liquidity.txt',
                'Quant.1 buy ... 62.45 / Quant.1 sell ... 64.00 ; Top depth (number of contract) 103 32 45 212 43 10 24 83',
                'H1 2020: day 109, night 48. COVID: "Soybean depth drops by half for outright futures" (Feb-Apr '
                '2020).'),
     'vpm': f({'trades_per_min': 53.881, 'contracts_per_trade': 5.32, 'implied_contracts_per_min': 287},
              'per minute', 'trades: 2015-12..2017-05 day session; size: 2015-11..2016-03',
              'ideals_hu_2020_three_essays.txt; agecon_259344.txt',
              'Trades per minute 39.405 33.887 53.881 46.992 ... ; Volume (contract) ... 5.32',
              'Implied contracts/min is worker arithmetic across two samples. Implied QV ~ 63/287 = 0.2 min.'),
     'jump': f(None, None, None, 'agecon_235772.txt', 'releases during trading hours result in a smaller volatility '
               'spike which extends for five to six minutes at a higher magnitude',
               'No ZS jump-frequency count found; ZC (cousin): 25.3% of days with an intraday jump 2008-15.'),
     'research': research([rel(R_HU, 'same'), rel(R_VOLK, 'same'), rel(R_ARZ, 'same'), rel(R_JOS, 'same'),
                           rel(R_DEB, 'same'), rel(R_SHANG, 'cousin'), rel(R_COUL, 'cousin')])})

ZW = full_size(
    'ZW', 'Wheat Futures (Chicago SRW)', 14, 'The minimum fluctuation for wheat futures shall be ¼ cent per bushel '
    '($12.50 per contract),', (0.25, 'US cents per bushel'), 12.50, 'The unit of trading shall be 5,000 bushels of '
    'Wheat.', (5000, 'bushels'), 'CHI WHEAT 142,002 93,115.24 52.5% 217,204.05 -34.6% 176,115 138,609 27.1%',
    'CHI WHEAT 128,550 103,224.61 24.5% 139,457.85 -7.8% 128,465 110,180 16.6%', 176115, 128465,
    cot('001602', 'WHEAT-SRW - CHICAGO BOARD OF TRADE', 363360, 0.168, 0.099, 471403, 0.174, 0.071,
        '001602 | WHEAT-SRW - CHICAGO BOARD OF TRADE | 2022-11-01..2023-10-31 ... meanOI=363360 | ProdMerc=0.168 '
        'Swap=0.140 MM=0.448 OtherRept=0.145 NonRept=0.099',
        '001602 | WHEAT-SRW ... latest_52wk ... meanOI=471403 | ProdMerc=0.174 Swap=0.148 MM=0.479 ... NonRept=0.071'),
    {'ch_file': 'cbot_rulebook_ch14.txt', 'ch_title_q': 'Chapter 14 Wheat Futures', 'code_file':
     'cftc_ptc071522_wheat_limit_rules.txt', 'code_q': 'Wheat Futures ZW W 14',
     'deliv_q': '14107. REGISTRATION AND DELIVERY OF WHEAT CERTIFICATES AND DELIVERY', 'limits': LIM_WHEAT,
     'limit_hits': f('>= 1 multi-day episode (2022) known; count unknown', 'days per year', '2019-2024',
                     'cftc_ptc071522_wheat_limit_rules.txt', 'On March 4, 2022, the Exchange again requested '
                     'expedited approval to increase price limits in the Contracts following multiple limit-move days '
                     'due to significant volatility caused by the war in Ukraine.',
                     'Number of limit days in 2022 and other years not sourced; A0 owned bars can count.'),
     'retail_q': None, 'retail_note': 'No retail share found. Managed money is the largest COT category (0.448).',
     'hft': f({'ATS-ATS': [18.5, 29.3], 'ATS-MAN': [44.9, 47.5], 'MAN-MAN': [33.9, 21.6]}, '% of volume',
              '2012-11..2014-10 and 2014-11..2016-10', 'cftc_haynes_roberts_2017_update.txt',
              'Wheat 49 62 18.5 29.3 44.9 47.5 33.9 21.6', 'Group ATS share: ' + HFT_GROUP[1]),
     'spread_main': GR_SPREAD_POOL,
     'spread_on': f(None, 'ticks', None, None, None, 'No ZW session split found.'),
     'depth': f({'bid': 45.26, 'ask': 43.92}, 'contracts at best, mean per side', 'nearby, 2015-11-23..2016-03-31',
                'agecon_259344.txt', 'Quant.1 buy 5.91 6.33 377.69 45.26 62.45 160.35 / Quant.1 sell 5.56 6.48 375.27 '
                '43.92 64.00 159.31', 'Mean, not median.'),
     'vpm': f({'contracts_per_trade': 4.72}, 'contracts per trade', 'nearby, 2015-11..2016-03', 'agecon_259344.txt',
              'Volume (2.06) 2.19 12.07 4.72 5.32 10.13', 'No trades-per-minute figure for wheat found.'),
     'jump': f(None, None, None, None, None, 'No ZW jump study found; A0 owned bars.'),
     'research': research([rel(R_VOLK, 'same'), rel(R_ARZ, 'same'), rel(R_HU, 'cousin'), rel(R_COUL, 'cousin'),
                           rel(R_HE, 'cousin')])})

ZL = full_size(
    'ZL', 'Soybean Oil Futures', 12, 'The minimum fluctuation for soybean oil futures shall be 1/100th of one cent per '
    'pound ($6.00 per contract), including spreads.', (0.01, 'US cents per pound'), 6.00,
    'The unit of trading shall be 60,000 lbs. of crude soybean oil.', (60000, 'pounds'),
    'SOYBEAN OIL 185,351 172,338.33 7.6% 218,667.19 -15.2% 227,516 183,650 23.9%',
    'SOYBEAN OIL 124,353 114,709.74 8.4% 153,846.15 -19.2% 147,995 112,117 32.0%', 227516, 147995,
    cot('007601', 'SOYBEAN OIL - CHICAGO BOARD OF TRADE', 459495, 0.434, 0.064, 668533, 0.415, 0.047,
        '007601 | SOYBEAN OIL - CHICAGO BOARD OF TRADE | 2022-11-01..2023-10-31 ... meanOI=459495 | ProdMerc=0.434 '
        'Swap=0.138 MM=0.244 OtherRept=0.121 NonRept=0.064',
        '007601 | SOYBEAN OIL ... latest_52wk ... meanOI=668533 | ProdMerc=0.415 ... NonRept=0.047'),
    {'ch_file': 'cbot_rulebook_ch12.txt', 'ch_title_q': 'Chapter 12 Soybean Oil Futures',
     'code_q': 'Soybean Oil Futures ZL 07 12', 'deliv_q': '12107. REGISTRATION AND DELIVERY OF SOYBEAN OIL RECEIPTS '
     'AND DELIVERY', 'limits': LIM_OIL,
     'hft': f(None, '% of volume', '2012-2016', HFT_GROUP[0], HFT_GROUP[1],
              'No per-contract table for soybean oil; group "Grain and Oilseed" ATS 39.0% (2012-14) -> 49.0% '
              '(2014-16). Update appendix has a soybean oil chart only.'),
     'spread_main': f(None, 'ticks', None, None, None, 'No ZL spread figure found (OpenAlex queries in '
                      'work/A1_grains/A1_grains_oa_*.txt).'),
     'spread_on': f(None, 'ticks', None, None, None, 'Not found.'),
     'depth': f(None, 'contracts', None, None, None, 'Not found.'),
     'vpm': f(None, 'contracts per minute', None, None, None, 'Not found.'),
     'jump': f(None, None, None, None, None, 'No ZL jump study found; A0 owned bars.'),
     'research': research([rel(R_DEB, 'same'), rel(R_HU, 'cousin'), rel(R_VOLK, 'cousin'), rel(R_ARZ, 'cousin')],
                          'Also "Microstructure and high-frequency price discovery in the soybean complex" (JCM 2023, '
                          'abstract only).')})

ZM = full_size(
    'ZM', 'Soybean Meal Futures', 13, 'The minimum fluctuation for Soybean Meal futures shall be ten cents ($.10) per '
    'ton ($10.00 per contract), including spreads.', (0.10, 'USD per short ton'), 10.00,
    'The unit of trading for Soybean Meal shall be 100 tons (2,000 pounds per ton).', (100, 'short tons'),
    'SOYBEAN MEAL 213,478 170,665.29 25.1% 166,698.48 28.1% 185,193 172,222 7.5%',
    'SOYBEAN MEAL 137,490 106,543.78 29.0% 138,946.2 -1.0% 140,498 107,575 30.6%', 185193, 140498,
    cot('026603', 'SOYBEAN MEAL - CHICAGO BOARD OF TRADE', 449564, 0.419, 0.084, 592664, 0.412, 0.065,
        '026603 | SOYBEAN MEAL - CHICAGO BOARD OF TRADE | 2022-11-01..2023-10-31 ... meanOI=449564 | ProdMerc=0.419 '
        'Swap=0.111 MM=0.263 OtherRept=0.123 NonRept=0.084',
        '026603 | SOYBEAN MEAL ... latest_52wk ... meanOI=592664 | ProdMerc=0.412 ... NonRept=0.065'),
    {'ch_file': 'cbot_rulebook_ch13.txt', 'ch_title_q': 'Chapter 13 Soybean Meal Futures',
     'code_q': 'Soybean Meal Futures ZM 06 13', 'deliv_q': 'The procedures for trading, clearing, inspection, '
     'delivery and settlement not specifically covered herein', 'limits': LIM_MEAL,
     'hft': f(None, '% of volume', '2012-2016', HFT_GROUP[0], HFT_GROUP[1],
              'No per-contract table for soybean meal; group-level only (update appendix chart only).'),
     'spread_main': f(None, 'ticks', None, None, None, 'No ZM spread figure found.'),
     'spread_on': f(None, 'ticks', None, None, None, 'Not found.'),
     'depth': f(None, 'contracts', None, None, None, 'Not found.'),
     'vpm': f(None, 'contracts per minute', None, None, None, 'Not found.'),
     'jump': f(None, None, None, None, None, 'No ZM jump study found; A0 owned bars.'),
     'research': research([rel(R_DEB, 'same'), rel(R_HU, 'cousin'), rel(R_VOLK, 'cousin'), rel(R_ARZ, 'cousin')],
                          'Also JCM 2023 soybean-complex paper (abstract only).')})


def mini(sym, clr, name, ch_file, unit_q, tick_q, adv26_line, adv23_line, adv26, adv23, parent, limit_q, cotd=None,
         research_rows=None):
    d = {
        'candidate': sym, 'family': 'grains',
        'product_name': f(name, None, None, ch_file, name),
        'product_code': f(sym, None, None, 'cme_ser9151_price_limit_amend.txt' if sym != 'XW' else
                          'cftc_ptc071522_wheat_limit_rules.txt', f'{name} {sym} {clr}',
                          'Globex code; clearing code ' + clr),
        'tick_size': f(0.125, 'US cents per bushel', None, ch_file, tick_q),
        'tick_value': f(1.25, 'USD per contract', None, ch_file, tick_q),
        'contract_size': f(1000, 'bushels', None, ch_file, unit_q),
        'settlement': f('physical delivery (delivery by mini-sized certificates)', None, None, ch_file,
                        f'{ch_file.split("_ch")[1].split("_")[0].split(".")[0]}07. DELIVERIES BY MINI-SIZED ... '
                        'CERTIFICATES AND DELIVERY'),
        'launch_date': f('2003-04-07 (open auction); electronic from 2007 (e-cbot); on Globex by 2007-11', None, None,
                         'mondo_cbot_mini_ag_2003.html.txt; mondo_cbot_mini_ag_ecbot_2007.html.txt; '
                         'cftc_rul091009cbot001.txt',
                         '"will launch mini-sized Corn, Wheat, and Soybean futures on Monday, April 7, 2003" ; "This is '
                         'the first time these contracts will be available on an electronic platform" ; "Mini-sized '
                         'Corn, Wheat and Soybean futures contracts traded on the Globex platform" (program start '
                         'November 1, 2007)', 'Mondo Visione reprints of CBOT releases. Exact e-cbot date (May 14, '
                         '2007) appears only in a CME URL slug from search [unverified].'),
        'globex_60_dates_in_2023-11..2024-02': f(True, None, '2023-11-01..2024-02-29', ADV26, adv26_line,
                                                  'Inferred: listed throughout (rule amendments 2022-2023 name it; ADV '
                                                  'rows 2023 and 2026). With ADV ~1,000-2,000/day trading on most days '
                                                  'is likely but days-with-trades in the window were not verified (no '
                                                  'market data read).'),
        'match_algorithm': MATCH_UNKNOWN,
        'trading_hours': HOURS,
        'price_limits': f(f'same as {parent}', None, None, ch_file, limit_q,
                          'SER 9151 / CBOT 22-254: limit levels set to the full-size values each business day.'),
        'limit_hit_days_2019_2024': dict(LIMIT_HITS_UNKNOWN, note=f'Same limits as {parent}; see {parent}.'),
        'adv_published_latest': f(adv26, 'contracts/day', 'YTD Jan-Sep 2026', ADV26, adv26_line),
        'adv_2022_11_2023_10': f(adv23, 'contracts/day', 'YTD Jan-Aug 2023 (partial window)', ADV23, adv23_line),
        'open_interest': f(None, 'contracts', None, None, None, 'No CFTC COT market for this contract in the 2022-2026 '
                           'files; CME OI not retrieved.'),
        'retail_share': f(None, None, None, 'mondo_cbot_mini_ag_ecbot_2007.html.txt',
                          'offer global customers, particularly in Asia, a smaller contract that is sized to their needs',
                          'No retail share found; small-size design (1/5 of full size).'),
        'commercial_hedger_share': f(None, None, None, None, None, 'No COT market; parent ' + parent + ' figures do '
                                     'not transfer.'),
        'nonreportable_share': f(None, None, None, None, None, 'No COT market.'),
        'market_maker_program': f('none current found; CBOT mini-sized grains MM program 2007-11-01..2009-12-31 (up to '
                                  '3 market makers, max spread 32 ticks, min size 1, fee waivers)', None,
                                  'checked 2026-10-21', 'cftc_rul091009cbot001.txt; cbot_fee_schedule_2026-10-01.txt',
                                  'Start Date is November 1, 2007 End Date is December 31, 2009',
                                  'Fee schedule 2026-10-01 waiver table names no mini grain.'),
        'hft_automated_share': f(None, None, None, None, None, 'Not tabulated by CFTC OCE for minis.'),
        'median_spread_ticks_main': f(None, 'ticks', None, None, None, 'Not found.'),
        'median_spread_ticks_overnight': f(None, 'ticks', None, None, None, 'Not found.'),
        'depth_best_level': f(None, 'contracts', None, None, None, 'Not found.'),
        'touch_queue_size': f(None, 'contracts', None, None, None, 'Not found.'),
        'volume_per_minute': f(None, 'contracts per minute', None, None, None,
                               'Not found; ADV ~1,000-2,000/day over ~17 h of trading.'),
        'scheduled_releases_per_week': RELEASES, 'usda_report_timing': USDA_TIMING, 'weekend_gap_exposure': WEEKEND,
        'jump_frequency': f(None, None, None, None, None, f'Same underlying as {parent}; see {parent}.'),
        'microstructure_research': research(research_rows or [], 'No study on the mini contract itself found.'),
    }
    if cotd:
        d.update(cotd)
    return d


XC = mini('XC', 'YC', 'Mini-Sized Corn Futures', 'cbot_rulebook_ch10B_2017.txt',
          'The unit of trading shall be 1,000 bushels of corn.',
          'The minimum fluctuation for mini-sized Corn futures shall be 1/8 cent per bushel ($1.25 per',
          'MINI CORN 1,318 1,048.71 25.6% 1,462.24 -9.9% 1,160 1,533 -24.3%',
          'MINI CORN 1,645 2,111.57 -22.1% 2,666.4 -38.3% 1,711 2,831 -39.6%', 1160, 1711, 'ZC',
          'Daily price limits for mini-sized Corn futures are the same as those for standard-sized Corn',
          research_rows=[rel(R_HU, 'size'), rel(R_VOLK, 'size'), rel(R_ARZ, 'size'), rel(R_COUL, 'size')])
XK = mini('XK', 'YK', 'Mini-Sized Soybean Futures', 'cbot_rulebook_ch11B.txt',
          'The unit of trading shall be 1,000 bushels of soybeans.',
          'The minimum fluctuation for mini-sized soybean futures shall be 1/8 cent per bushel ($1.25 per',
          'MINI SOYBEAN 1,587 1,362.9 16.4% 1,659.43 -4.4% 1,980 1,952 1.4%',
          'MINI SOYBEAN 1,955 2,725.13 -28.3% 3,263.15 -40.1% 2,077 2,951 -29.6%', 1980, 2077, 'ZS',
          'Daily price limits for mini-sized Soybean futures are the same as those for standard-sized',
          cotd={
              'open_interest': f({'2022-11..2023-10_mean': 21858, 'latest_mean': 27728}, 'contracts',
                                 '2023-07-25..2023-09-26 (10 reports only); 2026-05-05..2026-10-13 (24 reports)',
                                 COT_SRC, '005603 | MINI SOYBEANS - CHICAGO BOARD OF TRADE | ... n=10 | meanOI=21858',
                                 'CFTC publishes this market only in some weeks.'),
              'commercial_hedger_share': f({'2023 weeks': 0.210, '2026 weeks': 0.184}, 'share of OI positions',
                                           'as above', COT_SRC, 'ProdMerc=0.210 Swap=0.000 MM=0.000 OtherRept=0.376 '
                                           'NonRept=0.414', 'Thin sample.'),
              'nonreportable_share': f({'2023 weeks': 0.414, '2026 weeks': 0.362}, 'share of OI positions',
                                       'as above', COT_SRC, 'NonRept=0.414 ; NonRept=0.362', 'Thin sample.')},
          research_rows=[rel(R_HU, 'size'), rel(R_VOLK, 'size'), rel(R_ARZ, 'size'), rel(R_JOS, 'size')])
XW = mini('XW', 'YW', 'Mini-Sized Wheat Futures', 'cbot_rulebook_ch14B.txt',
          'The unit of trading shall be 1,000 bushels of wheat.',
          'The minimum fluctuation for mini-sized wheat futures shall be 1/8 cent per bushel ($1.25 per',
          'MINI WHEAT 970 524.14 85.0% 1,122.86 -13.6% 922 958 -3.7%',
          'MINI WHEAT 1,917 1,117.26 71.6% 2,708.55 -29.2% 1,523 1,302 17.0%', 922, 1523, 'ZW',
          'Daily price limits for mini-sized Wheat futures are the same as those for standard-sized Wheat',
          research_rows=[rel(R_VOLK, 'size'), rel(R_ARZ, 'size')])

SER = 'cme_ser9512_micro_grains.txt'


def micro(sym, name, ch, size, unit, tick, tick_unit, tval, parent, tick_q, size_q):
    return {
        'candidate': sym, 'family': 'grains',
        'product_name': f(name, None, None, 'cme_faq_micro_ag.html.txt', name),
        'product_code': f(sym, None, None, SER, f'Commodity Code MZC MZW MZS MZL MZM; Rulebook Chapter 10O 14O 11O 12O 13O',
                          f'Rulebook chapter {ch}'),
        'tick_size': f(tick, tick_unit, None, SER, tick_q,
                       'Twice the standard tick: "All Micro Agricultural contracts have a tick size that is twice the '
                       'size of the standard contract." (cme_faq_micro_ag.html.txt; its table prints "$0.050/bu", '
                       'apparently cents mislabelled as dollars; the SER value is used.)'),
        'tick_value': f(tval, 'USD per contract', None, SER, tick_q),
        'contract_size': f(size, unit, None, SER, size_q),
        'settlement': f('financially settled to the standard contract settlement', None, None, SER,
                        'Settlement Method Financially Settled',
                        'FAQ: "They settle on a daily and final basis to the standard sized contract, which can be at '
                        'a nontradable tick."'),
        'launch_date': f('2025-02-24', 'trade date', None, SER, 'Effective Sunday, February 23, 2025, for trade date '
                         'Monday, February 24, 2025 ... will list the Micro Corn, Micro Wheat, Micro Soybean, Micro '
                         'Soybean Oil, and Micro Soybean Meal Futures contracts',
                         'SER subject: "Initial Listing". cme_pr_20250130_micro_grains.html.txt: "will launch a suite '
                         'of micro grain and oilseed futures contracts on February 24, 2025".'),
        'globex_60_dates_in_2023-11..2024-02': f(False, None, '2023-11-01..2024-02-29', SER,
                                                  'for trade date Monday, February 24, 2025',
                                                  'Not listed until 2025-02-24, so zero trade dates in the pilot window.'),
        'match_algorithm': MATCH_UNKNOWN,
        'trading_hours': f(HOURS['value'], None, 'from launch', SER, HOURS['quote']),
        'price_limits': f(f'mirror {parent}', None, None, 'cme_faq_micro_ag.html.txt',
                          'The daily price limits for Micro Agricultural contracts will mirror the daily price limits '
                          'for the standard-sized contracts.'),
        'limit_hit_days_2019_2024': f(None, 'days per year', '2019-2024', SER, 'for trade date Monday, February 24, '
                                      '2025', f'Not listed in 2019-2024; underlying limits as {parent}.'),
        'adv_published_latest': f(None, 'contracts/day', 'searched Sep 2026 report', ADV26, None,
                                  'No micro grain row in the CME Exchange ADV Report (September 2026). One WebSearch '
                                  '(call 7). News (irei_micro_launch.html.txt, citing Bloomberg): "More than 54,000 '
                                  'contracts had been traded by the morning of Feb. 24, according to CME." [news, all '
                                  'five micros, not evidence-grade].'),
        'adv_2022_11_2023_10': f(None, 'contracts/day', '2022-11..2023-10', SER, None, 'Not listed.'),
        'open_interest': f(None, 'contracts', None, None, None, 'No CFTC COT market for micro grains in the 2025-2026 '
                           'files.'),
        'retail_share': f(None, None, None, 'cme_pr_20250130_micro_grains.html.txt',
                          '"These products are key to expanding market opportunities for retail investors, and their '
                          'smaller contract sizes enable our clients to more effectively diversify" (Saxo, quoted in the '
                          'CME release)', 'No CME retail share. A Bloomberg headline "CME is targeting retail traders '
                          'with micro corn soy contracts" seen only as a search-result title [unverified].'),
        'commercial_hedger_share': f(None, None, None, None, None, 'No COT market.'),
        'nonreportable_share': f(None, None, None, None, None, 'No COT market.'),
        'market_maker_program': f('none found', None, 'checked 2026-10-21', 'cbot_fee_schedule_2026-10-01.txt',
                                  'Micro Agricultural Cash Settlement/Delivery $0.15 $0.20 $0.50',
                                  'Fee schedule lists micro ag fees but no waiver; SER 9512 lists fees and general '
                                  'IIP/IVIP/FMIP rows only. Two WebSearches.'),
        'hft_automated_share': f(None, None, None, None, None, 'Not tabulated (product post-dates CFTC OCE studies).'),
        'median_spread_ticks_main': f(None, 'ticks', None, None, None, 'Not found.'),
        'median_spread_ticks_overnight': f(None, 'ticks', None, None, None, 'Not found.'),
        'depth_best_level': f(None, 'contracts', None, None, None, 'Not found.'),
        'touch_queue_size': f(None, 'contracts', None, None, None, 'Not found.'),
        'volume_per_minute': f(None, 'contracts per minute', None, None, None, 'Not found.'),
        'scheduled_releases_per_week': RELEASES, 'usda_report_timing': USDA_TIMING, 'weekend_gap_exposure': WEEKEND,
        'jump_frequency': f(None, None, None, None, None, f'Same underlying as {parent}.'),
        'microstructure_research': research([], f'No study on micro grains found; see {parent} for full-size studies '
                                            '(relation: size).'),
    }


TQ_BU = '1/2 of one (1) cent ($0.005) per bushel ($2.50 per contract)'
MZC = micro('MZC', 'Micro Corn Futures', '10O', 500, 'bushels', 0.5, 'US cents per bushel', 2.50, 'ZC', TQ_BU,
            'Trading Unit 500 bushels')
MZS = micro('MZS', 'Micro Soybean Futures', '11O', 500, 'bushels', 0.5, 'US cents per bushel', 2.50, 'ZS', TQ_BU,
            'Trading Unit 500 bushels')
MZW = micro('MZW', 'Micro Wheat Futures', '14O', 500, 'bushels', 0.5, 'US cents per bushel', 2.50, 'ZW', TQ_BU,
            'Trading Unit 500 bushels')
MZL = micro('MZL', 'Micro Soybean Oil Futures', '12O', 6000, 'pounds', 0.02, 'US cents per pound', 1.20, 'ZL',
            '1/50th of one (1) cent ($0.0002) per pound ($1.20 per contract)', 'Trading Unit ... 6,000 pounds')
MZM = micro('MZM', 'Micro Soybean Meal Futures', '13O', 10, 'short tons', 0.20, 'USD per short ton', 2.00, 'ZM',
            '$0.20 per short ton ($2.00 per contract)', 'Trading Unit ... 10 short tons')

ALL = [ZC, ZS, ZW, ZL, ZM, XC, XK, XW, MZC, MZS, MZW, MZL, MZM]
json.dump(ALL, open(OUT_JSON, 'w'), indent=1, ensure_ascii=False)

# ---------- MD sheets ----------
ORDER = ['product_name', 'product_code', 'tick_size', 'tick_value', 'contract_size', 'settlement', 'launch_date',
         'globex_60_dates_in_2023-11..2024-02', 'match_algorithm', 'trading_hours', 'price_limits',
         'limit_hit_days_2019_2024', 'adv_published_latest', 'adv_2022_11_2023_10', 'open_interest', 'retail_share',
         'commercial_hedger_share', 'nonreportable_share', 'market_maker_program', 'hft_automated_share',
         'median_spread_ticks_main', 'median_spread_ticks_overnight', 'depth_best_level', 'touch_queue_size',
         'volume_per_minute', 'scheduled_releases_per_week', 'usda_report_timing', 'weekend_gap_exposure',
         'jump_frequency', 'microstructure_research']
SHARED = {'trading_hours': 'F1', 'scheduled_releases_per_week': 'F3', 'usda_report_timing': 'F3',
          'weekend_gap_exposure': 'F1'}


def cell(x):
    if x is None:
        return ''
    if isinstance(x, (dict, list)):
        if isinstance(x, list) and x and isinstance(x[0], dict) and 'study' in x[0]:
            return '; '.join(f"{r['study']} [{r['relation']}]: {r['result']}" for r in x)
        return json.dumps(x, ensure_ascii=False)
    return str(x).replace('|', '/')


lines = ['', '## S. Per-candidate fact sheets', '',
         'Generated by work/A1_grains/A1_grains_build.py from the same records as A1_grains.json. Paths are under '
         'reports/stage_e28_briefs/pages/A1_grains/ unless stated. Empty value = unknown (the note says what was '
         'searched). Fields marked "see Fx" are family-wide.', '']
for c in ALL:
    lines += [f"### {c['candidate']}: {c['product_name']['value']}", '', '| Field | Value | Window | Source | Quote / note |',
              '|---|---|---|---|---|']
    for k in ORDER:
        v = c[k]
        if k in SHARED:
            lines.append(f"| {k} | see {SHARED[k]} | | | |")
            continue
        src = (v['source_file'] or '').replace(P, '')
        qn = ' '.join(x for x in [('"' + v['quote'] + '"') if v['quote'] else '', v['note'] or ''] if x)
        val = cell(v['value'])
        if v['unit'] and val:
            val += f" ({v['unit']})"
        lines.append(f"| {k} | {cell(val)} | {cell(v['window'])} | {cell(src)} | {cell(qn)} |")
    lines.append('')
open(OUT_MD, 'a').write('\n'.join(lines) + '\n')
print('candidates', len(ALL), 'fields', len(ALL[0]))
