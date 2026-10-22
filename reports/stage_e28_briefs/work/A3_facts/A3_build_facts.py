"""Stage E.28 A3 (FactTable): build A3_facts.json (one row per Layer 1 candidate) from A0 and A1.

Facts only, with provenance per cell. Lead decisions applied: OC-1 (sibling-derived sigma_1m and R_d in ticks)
and OC-2 (ADV source). Every reading choice the spec leaves open is tagged in the cell's flags and listed in
reports/stage_e28_briefs/A3_facts.md. Run: python3 A3_build_facts.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A3_common import BR, CANDIDATES, FAMILY_OF, FAMILIES, OC1_SIBLING, CLASS_OF, fact, load  # noqa: E402

FIELDS = {
    'crude': dict(gate='globex_60_dates_in_2023-11..2024-02', adv_latest='adv_published_latest', adv_win='adv_2022_11_2023_10',
                  spr_main='median_spread_ticks_main', spr_on='median_spread_ticks_overnight', rel='scheduled_releases_per_week',
                  wknd='weekend_gap_exposure', limit='limit_hit_days_2019_2024', jump='jump_frequency'),
    'natgas': dict(gate='pilot_window_globex_60_dates', adv_latest='adv_latest', adv_win='adv_2022_11_2023_10',
                   spr_main='spread_median_ticks_by_session', spr_on='spread_median_ticks_by_session',
                   rel='scheduled_releases_per_week', wknd='weekend_gap_exposure', limit='limit_hit_days_2019_2024',
                   jump='jump_frequency'),
    'metals': dict(gate='globex_60_dates_pilot', adv_latest='adv_latest', adv_win='adv_window', spr_main='median_spread_ticks',
                   spr_on=None, rel='scheduled_releases_per_week', wknd='weekend_gap', limit='limit_hit_days',
                   jump='jump_frequency'),
    'fx': dict(gate='globex_60_dates_pilot_window', adv_latest='adv_latest_published', adv_win='adv_pre_pilot_published',
               spr_main='median_spread_ticks', spr_on='overnight_vs_main_spread', rel='product_specific_releases_per_week',
               wknd='weekend_gap_exposure', limit='limit_hit_days_2019_2024', jump='jump_frequency'),
    'crypto': dict(gate='globex_60_dates_in_pilot_window', adv_latest='adv_latest', adv_win='adv_2022_11_2023_10',
                   spr_main='median_spread_ticks', spr_on='median_spread_ticks', rel='scheduled_releases_per_week',
                   wknd='weekend_gap_exposure', limit='limit_hit_days_2019_2024', jump='jump_frequency'),
    'equity': dict(gate='traded_60_dates_pilot_window', adv_latest='adv_latest_published', adv_win='adv_derived_2022-11_2023-10',
                   spr_main='median_spread_ticks_main', spr_on='median_spread_ticks_overnight',
                   rel='product_specific_releases_per_week', wknd='weekend_gap_exposure', limit='limit_hit_days_2019_2024',
                   jump='jump_frequency'),
    'rates': dict(gate='globex_60_dates_in_2023-11..2024-02', adv_latest='adv_published_latest', adv_win='adv_2022_11_2023_10',
                  spr_main='median_spread_ticks_main', spr_on='median_spread_ticks_overnight', rel='scheduled_releases_per_week',
                  wknd='weekend_gap_exposure', limit='limit_hit_days_2019_2024', jump='jump_frequency'),
    'grains': dict(gate='globex_60_dates_in_2023-11..2024-02', adv_latest='adv_published_latest', adv_win='adv_2022_11_2023_10',
                   spr_main='median_spread_ticks_main', spr_on='median_spread_ticks_overnight', rel='scheduled_releases_per_week',
                   wknd='weekend_gap_exposure', limit='limit_hit_days_2019_2024', jump='jump_frequency'),
}

# QV components where a published best-level displayed size exists AND A0 owns main-session volume per minute.
# (size_contracts, A1 field path, window, flags). ZT excluded: CME's 2018 depth predates the early-2019 tick halving
# (A1_rates.md F12 note on R8), so it is not a figure for today's tick.
QV_SIZE = {
    'CL': (7.0, 'A1_crude.json:CL.depth_best_level.value.median', '2012-08..2013-07',
           ['QV_mixed_windows', 'median, bid side, random timestamps (session not stated)']),
    'GC': (4.62, 'A1_metals.json:GC.depth_best_level.value.2010_level1_median', '2010 (06:30-13:30 window)',
           ['QV_mixed_windows', 'level-1 median, bid (ask also 4.62)']),
    'ZN': (2507.0, 'A1_rates.json:ZN.touch_queue_size.value', '2018 RTH, front month',
           ['QV_mixed_windows', 'average not median', 'side not split']),
    'ZF': (1319.0, 'A1_rates.json:ZF.touch_queue_size.value', '2018 RTH, front month',
           ['QV_mixed_windows', 'average not median', 'side not split']),
    'ZB': (377.0, 'A1_rates.json:ZB.touch_queue_size.value', '2018 RTH, front month',
           ['QV_mixed_windows', 'average not median', 'side not split']),
    'ZC': ((377.69 + 375.27) / 2, 'A1_grains.json:ZC.depth_best_level.value (bid 377.69, ask 375.27)', '2015-11-23..2016-03-31',
           ['QV_mixed_windows', 'mean not median', 'mean of the two sides']),
    'ZS': (103.0 / 2, 'A1_grains.json:ZS.depth_best_level.value.top_depth_bid_plus_ask_day_2019 (103) / 2', 'H1 2019 day session',
           ['QV_mixed_windows', 'mean not median', 'per side = bid+ask / 2; more recent than the 2015-16 per-side 62-64']),
    'ZW': ((45.26 + 43.92) / 2, 'A1_grains.json:ZW.depth_best_level.value (bid 45.26, ask 43.92)', '2015-11-23..2016-03-31',
           ['QV_mixed_windows', 'mean not median', 'mean of the two sides']),
}

# OC-2 for codes without owned window bars: A1's published all-expiry ADV, latest available; (field, key, value, window, flags)
ADV_NONOWNED = {
    'QM': None,
    'MNG': ('adv_ytd_2025', None, 13781, '2025-01..2025-10 (YTD)', ['ADV_not_trailing_12m']),
    'QG': ('adv_latest', 'note: YTD Jan-Sep 2026 3,937', 3937, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    'SIL': ('adv_latest', None, 74000, 'Q2 2026 (quarter)', ['ADV_not_trailing_12m', 'quarter only']),
    'SI': ('adv_latest', None, 64000, 'Q2 2026 (quarter)', ['ADV_not_trailing_12m', 'quarter only']),
    'M6E': ('adv_latest_published', None, 23742, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    'M6A': ('adv_latest_published', None, 7384, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    'MET': ('adv_latest', '2025_calendar', 144000, 'calendar 2025', ['secondary source citing CME']),
    'ETH': ('adv_latest', '2026_04', 19000, '2026-04 (single month)', ['ADV_not_trailing_12m', 'single month']),
    'BTC': None,  # only Oct 2023 (13,000) published: not within 12 months of the lookup date
    'MNQ': ('adv_latest_published', '2025 full year', 1600000, 'calendar 2025', ['rounded CME release figure']),
    'M2K': ('adv_derived_2022-11_2023-10', None, 79724, '2022-11..2023-10 (derived from CME monthly reports)',
            ['ADV_standard_window_not_latest', 'derived by reader with assumed trade-date counts']),
    'MYM': ('adv_derived_2022-11_2023-10', None, 114779, '2022-11..2023-10 (derived from CME monthly reports)',
            ['ADV_standard_window_not_latest', 'derived by reader with assumed trade-date counts']),
    '2YY': ('adv_published_latest', 'YTD_Jan-Sep_2026', 0, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    '5YY': ('adv_published_latest', 'YTD_Jan-Sep_2026', 0, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    '10Y': ('adv_published_latest', 'YTD_Jan-Sep_2026', 1277, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    '30Y': ('adv_published_latest', 'YTD_Jan-Sep_2026', 0, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    'XC': ('adv_published_latest', None, 1160, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    'XK': ('adv_published_latest', None, 1980, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    'XW': ('adv_published_latest', None, 922, '2026-01..2026-09 (YTD)', ['ADV_not_trailing_12m']),
    'MZC': None, 'MZS': None, 'MZW': None, 'MZL': None, 'MZM': None,
}

# C4 item 1 (>= 2 scheduled product-specific high-impact releases per week), by family:
# (holds, ambiguous, basis). 'ambiguous' marks a reader-flagged judgment; the C4-conservative variant counts it as holding.
C4_RELEASES = {
    'crude': (False, True, 'EIA WPSR 1/week sourced; API 1/week sourced timing but weak measured impact (reader: scorer\'s call)'),
    'natgas': (False, False, 'EIA Weekly Natural Gas Storage Report, 1/week'),
    'metals': (False, True, 'reader: 0 product-specific releases (CME metals event list holds only macro events); absence'),
    'fx': (False, False, 'central-bank decisions 0.15/week; other monthly releases below 2/week by count [unverified]'),
    'crypto': (False, True, 'reader: none found; absence, not a sourced statement'),
    'equity': (False, True, 'reader: none found in any fetched source (value null); absence read as false'),
    'rates': (False, True, 'Treasury auctions of the matching tenor 0.23/week (reader: whether auctions count is for the scorer)'),
    'grains': (True, False, 'USDA: in season 2 weekly product-specific releases (Crop Progress, Export Sales) plus monthly WASDE'),
}
# C4 item 2 (weekend-gap exposure from an underlying trading while Globex is closed)
C4_WEEKEND = {
    'crude': (False, False, 'no 24/7 underlying sourced (reader)'),
    'natgas': (False, False, 'no weekend-traded Henry Hub instrument found (reader)'),
    'metals': (False, False, 'no crypto-type weekend exposure in 2019-2024 (weekend 1OZ/SIC trading began 2026)'),
    'fx': (False, False, 'no 7-day underlying documented; spot FX closes at the weekend [unverified]'),
    'crypto': (True, False, 'reference rate published every day while Globex closed weekends, through 2026-05-28'),
    'equity': (False, False, 'cash index constituents do not trade at weekends [unverified general knowledge]'),
    'rates': (False, True, 'reader value null: no source states cash Treasuries trade while Globex is closed; read as false'),
    'grains': (False, False, 'no weekend-traded underlying found (reader)'),
}


# Informational OC-2 sensitivity only: a clean published multi-month all-expiry ADV for owned roots
# (code: (value, A1 field, window)). Roots without such a figure keep A0's v_0 value in that variant.
ADV_PUBLISHED_OWNED = {
    'MCL': (95000, 'adv_published_latest.2023_YTD_to_2023-06-28', '2023 YTD to 2023-06-28 ("over 95,000")'),
    'NG': (400923, 'adv_2022_11_2023_10', '2023-01..2023-08'),
    'MGC': (75000, 'adv_window', '2023 YTD to Q3 (reader-derived)'),
    'MHG': (4882, 'adv_window.note', 'calendar 2023'),
    '6E': (223555, 'adv_pre_pilot_published', '2023-01..2023-08'),
    '6A': (93860, 'adv_pre_pilot_published', '2023-01..2023-08'),
    'NQ': (666813, 'adv_derived_2022-11_2023-10', '2022-11..2023-10 (derived)'),
    'RTY': (217387, 'adv_derived_2022-11_2023-10', '2022-11..2023-10 (derived)'),
    'YM': (177933, 'adv_derived_2022-11_2023-10', '2022-11..2023-10 (derived)'),
    'ZT': (797491, 'adv_2022_11_2023_10.YTD_Jan-Aug_2023', '2023-01..2023-08'),
    'ZF': (1542263, 'adv_2022_11_2023_10.YTD_Jan-Aug_2023', '2023-01..2023-08'),
    'ZN': (1971131, 'adv_2022_11_2023_10.YTD_Jan-Aug_2023', '2023-01..2023-08'),
    'ZB': (405796, 'adv_2022_11_2023_10.YTD_Jan-Aug_2023', '2023-01..2023-08'),
    'ZC': (361462, 'adv_2022_11_2023_10', '2023-01..2023-08'),
    'ZS': (243723, 'adv_2022_11_2023_10', '2023-01..2023-08'),
    'ZW': (128465, 'adv_2022_11_2023_10', '2023-01..2023-08'),
    'ZL': (147995, 'adv_2022_11_2023_10', '2023-01..2023-08'),
    'ZM': (140498, 'adv_2022_11_2023_10', '2023-01..2023-08'),
}


def a1_rows():
    out = {}
    for fam in FAMILIES:
        for r in load(f'A1_{fam}.json'):
            out[r.get('candidate') or r.get('code')] = (fam, r)
    return out


def a0_rows():
    return {r['root']: r for r in load('A0_contract_stats.json')['roots']}


def cell(row, field):
    v = row.get(field) if field else None
    return v if isinstance(v, dict) else {}


def tick_facts(code, fam, row, a0):
    t, tv = cell(row, 'tick_size'), cell(row, 'tick_value')
    prov_t = f'A1_{fam}.json:{code}.tick_size'
    prov_v = f'A1_{fam}.json:{code}.tick_value'
    conflicts = []
    a0r = a0.get(code)
    if a0r:
        cents = 'cent' in str(t.get('unit', '')).lower()
        a0_tick = float(a0r['tick_size_exchange_units']) * (100.0 if cents else 1.0)
        if abs(a0_tick - float(t['value'])) > 1e-9:
            conflicts.append(f"tick size A1 {t['value']} vs A0 {a0r['tick_size_exchange_units']}")
        if abs(float(a0r['tick_value_usd']) - float(tv['value'])) > 1e-9:
            conflicts.append(f"tick value A1 {tv['value']} vs A0 {a0r['tick_value_usd']}")
    return (fact(float(t['value']), t.get('unit'), prov_t, quote=t.get('quote')),
            fact(float(tv['value']), 'USD per tick per contract', prov_v, quote=tv.get('quote')), conflicts)


def owned_window(a0r):
    return bool(a0r) and a0r.get('sigma_1m_ticks') is not None


def price_stat(code, a0, ticks, stat, oc1, units=None):
    """sigma_1m or R_d in ticks: owned (A0), OC-1 sibling-derived, or unknown."""
    key = 'sigma_1m_ticks' if stat == 'sigma_1m' else 'R_d_median_ticks'
    a0r = a0.get(code)
    if owned_window(a0r):
        return fact(float(a0r[key]), 'ticks', f'A0_contract_stats.json:{code}.{key}', window='2022-11-01..2023-10-31')
    sib = OC1_SIBLING.get(code)
    if oc1 and sib and owned_window(a0.get(sib)) and units and units[sib] == units[code]:
        s = a0[sib]
        factor = ticks[sib] / ticks[code]  # both A1 ticks, same price units (checked)
        val = float(s[key]) * factor
        return fact(val, 'ticks', f'A0_contract_stats.json:{sib}.{key} x tick({sib})/tick({code}) = x{factor:g} (OC-1)',
                    flags=['OC1_derived'], window='2022-11-01..2023-10-31 (sibling)')
    return fact(None, 'ticks', None, u=True, note='no owned window bars and no OC-1 sibling (or OC-1 off); unknown')


def adv_fact(code, fam, row, a0):
    a0r = a0.get(code)
    adv_f = FIELDS[fam]['adv_latest']
    win_f = FIELDS[fam]['adv_win']
    published = {'latest': cell(row, adv_f).get('value'), 'latest_window': cell(row, adv_f).get('window'),
                 'standard_window_or_nearest': cell(row, win_f).get('value'),
                 'standard_window_or_nearest_window': cell(row, win_f).get('window'),
                 'provenance': f'A1_{fam}.json:{code}.{adv_f}; {win_f}'}
    if owned_window(a0r):
        return fact(float(a0r['ADV_median_contracts_v0_front']), 'contracts/day (median, v_0 front contract)',
                    f'A0_contract_stats.json:{code}.ADV_median_contracts_v0_front', window='2022-11-01..2023-10-31',
                    flags=['OC2_owned_v0_front']), published
    spec = ADV_NONOWNED.get(code)
    if spec is None:
        return fact(None, 'contracts/day', None, u=True,
                    note='no owned window bars and no published all-expiry ADV within 12 months of the lookup date'), published
    field, key, val, window, flags = spec
    return fact(float(val), 'contracts/day (published, all expiries)', f'A1_{fam}.json:{code}.{field}' + (f'.{key}' if key else ''),
                window=window, flags=['OC2_published'] + flags), published


def qv_fact(code, a0, sigma, ticks):
    a0r = a0.get(code)
    if code in QV_SIZE and owned_window(a0r) and a0r.get('vol_per_min_main_median'):
        size, prov, window, flags = QV_SIZE[code]
        vpm = float(a0r['vol_per_min_main_median'])
        qv = size / vpm
        return fact(qv, 'minutes (QV)', f'{prov} / A0_contract_stats.json:{code}.vol_per_min_main_median ({vpm:g})',
                    flags=flags, window=f'size {window}; volume 2022-11..2023-10', note=f'size {size:g} contracts / {vpm:g} per minute')
    if sigma.get('value'):
        r = 1.0 / sigma['value']
        return fact(r, 'r = tick / sigma_1m (proxy)', f'1 / sigma_1m ({sigma["provenance"]})', flags=['proxy'] + sigma['flags'])
    return fact(None, 'QV or proxy r', None, u=True, note='neither QV nor sigma_1m available')


def spread_facts(code, fam, row):
    f = FIELDS[fam]
    main = cell(row, f['spr_main'])
    on = cell(row, f['spr_on']) if f['spr_on'] else {}
    main_v = main.get('value')
    if fam == 'natgas' or fam == 'crypto':      # one combined field, no session split sourced
        on_v = None
    elif fam == 'fx':                            # this field is the overnight/main ratio itself
        on_v = None
    else:
        on_v = on.get('value')
    num = lambda x: float(x) if isinstance(x, (int, float)) else None  # noqa: E731
    mv, ov = num(main_v), num(on_v)
    ratio = (ov / mv) if (mv and ov) else None
    if fam == 'fx' and isinstance(on.get('value'), (int, float)):
        ratio = float(on['value'])
    main_cell = fact(mv, 'ticks', f'A1_{fam}.json:{code}.{f["spr_main"]}', note=str(main.get('note'))[:300],
                     flags=([] if mv is not None else ['not numeric or unknown']), window=main.get('window'))
    if main_v is not None and mv is None:
        main_cell['raw'] = str(main_v)[:200]
    on_cell = fact(ov, 'ticks', f'A1_{fam}.json:{code}.{f["spr_on"]}' if f['spr_on'] else None, window=on.get('window'))
    ratio_cell = fact(ratio, 'overnight / main median spread', 'derived from the two cells' if ratio else None,
                      note=None if ratio else 'not sourced: C3 overnight deduction not applied (the spec applies it only to a sourced ratio)')
    return main_cell, on_cell, ratio_cell


def c4_items(code, fam, row, a0, oc1_jump_transfer=False):
    f = FIELDS[fam]
    rel_h, rel_amb, rel_basis = C4_RELEASES[fam]
    wk_h, wk_amb, wk_basis = C4_WEEKEND[fam]
    rel = fact(rel_h, None, f'A1_{fam}.json:{code}.{f["rel"]}', note=rel_basis, flags=['ambiguous'] if rel_amb else [],
               quote=cell(row, f['rel']).get('quote'))
    wk = fact(wk_h, None, f'A1_{fam}.json:{code}.{f["wknd"]}', note=wk_basis, flags=['ambiguous'] if wk_amb else [],
              quote=cell(row, f['wknd']).get('quote'))
    lim_raw = cell(row, f['limit'])
    lim_note = 'per-year count 2019-2024 not sourced; counted as holding (spec: unknown item holds)'
    if fam == 'equity':
        lim_note = ('sourced: 4 trade dates with RTH circuit-breaker halts (all March 2020) = 0.67/yr lower bound; overnight '
                    'limit hits in March 2020 not verified, so the >= 1/yr average is unknown; counted as holding')
    lim = fact('unknown', None, f'A1_{fam}.json:{code}.{f["limit"]}', u=True, note=lim_note,
               flags=['unknown_holds'], quote=str(lim_raw.get('value'))[:200])
    a0r = a0.get(code)
    if owned_window(a0r):
        rate = float(a0r['c4_rate_per_252d_2019_to_2023_10_31'])
        jump = fact(rate >= 10, None, f'A0_contract_stats.json:{code}.c4_rate_per_252d_2019_to_2023_10_31 = {rate:.2f}/yr',
                    note='2019-01..2023-10-31 (2024 not readable under the data rule)', window='2019-2023-10')
    elif fam == 'fx' and isinstance(cell(row, f['jump']).get('value'), dict):
        jump = fact(False, None, f'A1_fx.json:{code}.jump_frequency (reader: A0 counts of the full-size contract)',
                    note='reader-sourced value (sibling counts, at most 2 per year)', flags=['A1_sibling_value'])
    elif oc1_jump_transfer and OC1_SIBLING.get(code) and owned_window(a0.get(OC1_SIBLING[code])):
        sib = OC1_SIBLING[code]
        rate = float(a0[sib]['c4_rate_per_252d_2019_to_2023_10_31'])
        jump = fact(rate >= 10, None, f'A0_contract_stats.json:{sib}.c4_rate_per_252d_2019_to_2023_10_31 = {rate:.2f}/yr',
                    flags=['jump_transfer_variant'])
    else:
        jump = fact('unknown', None, None, u=True, note='no owned bars, no reader value: counted as holding', flags=['unknown_holds'])
    return {'releases_2plus_per_week': rel, 'weekend_gap_exposure': wk, 'limit_hit_1plus_per_year': lim,
            'big_moves_10plus_per_year': jump}


def gate_fact(code, fam, row, a0):
    g = cell(row, FIELDS[fam]['gate'])
    v = g.get('value')
    a0r = a0.get(code)
    files = (a0r or {}).get('pilot_window_files_by_name') or []
    val = True if v is True else (False if v is False else 'unknown')
    return fact(val, 'traded on >= 60 Globex trade dates in 2023-11-01..2024-02-29',
                f'A1_{fam}.json:{code}.{FIELDS[fam]["gate"]}' + (f'; A0 pilot-window files by name: {len(files)}' if files else ''),
                u=(val == 'unknown'), note=g.get('note'), flags=['inferred from listing, not counted'] if v is True else [])


def build(oc1=True, oc1_jump_transfer=False):
    a1, a0 = a1_rows(), a0_rows()
    ticks = {c: float(a1[c][1]['tick_size']['value']) for c in CANDIDATES}
    units = {c: str(a1[c][1]['tick_size'].get('unit')).split('(')[0].strip().lower() for c in CANDIDATES}
    rows, conflicts = {}, []
    for code in CANDIDATES:
        fam, row = a1[code]
        tick, tv, tconf = tick_facts(code, fam, row, a0)
        conflicts += [{'code': code, 'field': 'tick', 'detail': d} for d in tconf]
        sigma = price_stat(code, a0, ticks, 'sigma_1m', oc1, units)
        rd = price_stat(code, a0, ticks, 'R_d', oc1, units)
        adv, adv_pub = adv_fact(code, fam, row, a0)
        sm, so, ratio = spread_facts(code, fam, row)
        rows[code] = {
            'code': code, 'family': fam, 'product_class': CLASS_OF[code],
            'product_name': (row.get('product_name') or {}).get('value'),
            'owned_window_bars': owned_window(a0.get(code)),
            'tick_size': tick, 'tick_value': tv,
            'sigma_1m': sigma, 'R_d': rd,
            'QV_or_r': qv_fact(code, a0, sigma, ticks),
            'ADV': adv, 'ADV_published_all_expiry': adv_pub,
            'spread_main': sm, 'spread_overnight': so, 'spread_ratio_overnight_main': ratio,
            'C4': c4_items(code, fam, row, a0, oc1_jump_transfer),
            'gate_60_dates': gate_fact(code, fam, row, a0),
        }
    return rows, conflicts


def main():
    rows, conflicts = build(oc1=True)
    rows_off, _ = build(oc1=False)
    rows_jt, _ = build(oc1=True, oc1_jump_transfer=True)
    out = {
        'generated_by': 'reports/stage_e28_briefs/work/A3_facts/A3_build_facts.py',
        'spec_sha256': '89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f',
        'lead_decisions_applied': ['OC-1 sibling-derived sigma_1m and R_d in ticks', 'OC-2 ADV source'],
        'n_candidates': len(rows),
        'candidates': rows,
        'variants': {
            'OC1_off': {c: {'sigma_1m': rows_off[c]['sigma_1m'], 'R_d': rows_off[c]['R_d'], 'QV_or_r': rows_off[c]['QV_or_r']}
                        for c in rows},
            'C4_jump_transfer': {c: {'big_moves_10plus_per_year': rows_jt[c]['C4']['big_moves_10plus_per_year']} for c in rows},
            'OC2_published': {c: {'ADV': fact(float(v[0]), 'contracts/day (published, all expiries)',
                                              f'A1_{rows[c]["family"]}.json:{c}.{v[1]}', window=v[2], flags=['OC2_published_variant'])}
                              for c, v in ADV_PUBLISHED_OWNED.items()},
        },
        'conflicts': conflicts,
    }
    with open(os.path.join(BR, 'A3_facts.json'), 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print('wrote A3_facts.json candidates', len(rows), 'tick conflicts', len(conflicts))


if __name__ == '__main__':
    main()
