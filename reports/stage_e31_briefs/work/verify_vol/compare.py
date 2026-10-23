import json, math
mine = json.load(open('verify_numbers.json'))
prod = json.load(open('../pilot/runs/vol_measures.json'))
rows = []   # (item, mine, producer, match)
def add(item, a, b, tol=0.0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        ok = abs(a - b) <= tol * max(1.0, abs(a), abs(b)) if tol else a == b
    else:
        ok = a == b
    rows.append((item, a, b, ok))
add('records', mine['n_records'], prod['records_total'])
w = mine['window']; pw = prod['window']
add('window start', w['start'], pw['start']); add('window end', w['end'], pw['end'])
add('window days primary', w['universe_days'], pw['days_primary'])
for rt in ('QM', 'ZM'):
    p = prod['roots'][rt]
    add(f'window days own {rt}', w['own_days'][rt], pw[f'days_{rt}'])
    add(f'median primary {rt}', w['median_primary'][rt], p['window_primary']['median'])
    add(f'median own {rt}', w['median_own'][rt], p['window_own']['median'])
    add(f'p10 primary {rt}', w['stats_primary'][rt]['p10'], p['window_primary']['p10'], 1e-12)
    add(f'p10 own {rt}', w['stats_own'][rt]['p10'], p['window_own']['p10'], 1e-12)
    add(f'window volume {rt}', w['sum_volume'][rt], p['window_primary']['total_volume'])
    add(f'zero-fill days {rt}', w['zero_fill_days_primary'][rt], p['window_zero_days_primary'])
    add(f'verdict primary {rt}', w['verdict_primary'][rt], p['verdict_primary'])
    add(f'verdict own {rt}', w['verdict_own'][rt], p['verdict_own'])
    h = mine['hyphen_and_weekend_overall'][rt]
    add(f'hyphen symbols {rt}', h['hyphen_instruments'], prod['hyphen_dropped'][rt]['symbols'])
    add(f'hyphen bars {rt}', h['hyphen_bars'], prod['hyphen_dropped'][rt]['bars'])
    add(f'hyphen volume {rt}', h['hyphen_volume'], prod['hyphen_dropped'][rt]['volume'])
    add(f'weekend bars {rt}', h['outright_bars_weekend'], prod['weekend_bars'][rt]['bars'])
    add(f'weekend volume {rt}', h['outright_volume_weekend'], prod['weekend_bars'][rt]['volume'])
    add(f'outright instruments {rt}', h['outright_instruments'], prod['instruments'][rt]['outright_with_weekday_bars'])
    add(f'instruments with bars {rt}', h['outright_instruments'] + h['hyphen_instruments'], prod['instruments'][rt]['with_bars'])
    cl = mine['nonstandard_outrights'][rt]; pc = prod['check_line'][rt]
    add(f'check bars {rt}', cl['nonmatching_bars'], pc['bars'])
    add(f'check volume {rt}', cl['nonmatching_volume'], pc['volume'])
    add(f'check symbols {rt}', sorted(cl['nonmatching_symbols']), sorted(pc['symbols']))
    add(f'check root volume weekday-only {rt}', cl['root_outright_volume'] - h['outright_volume_weekend'], pc['root_volume'])
    add(f'check share(weekday) {rt}', (cl['nonmatching_volume']) / (cl['root_outright_volume'] - h['outright_volume_weekend']), pc['share'], 1e-12)
    # quarters
    mq = {r['quarter']: r for r in mine['quarters'][rt]}
    for key, suffix in (('quarters_primary', 'primary'), ('quarters_own', 'own')):
        pq = {r['quarter']: r for r in p[key]}
        add(f'quarter set {rt} {suffix}', sorted(mq), sorted(pq))
        for qn, r in pq.items():
            m = mq[qn]
            add(f'{rt} {qn} {suffix} days', m[f'days_{suffix}'], r['days'])
            add(f'{rt} {qn} {suffix} median', m[f'median_{suffix}'], r['median'])
            add(f'{rt} {qn} {suffix} p10', m[f'p10_{suffix}'], r['p10'], 1e-12)
            add(f'{rt} {qn} {suffix} total_volume', m['volume'], r['total_volume'])
            add(f'{rt} {qn} {suffix} front_share', m['front_share'], r['front_share'], 1e-12)
            add(f'{rt} {qn} {suffix} top_share', m['top_share_info'], r['top_share'], 1e-12)
        add(f'last quarter partial {rt} {suffix}', [q['quarter'] for q in p[key] if q['partial']], ['2026Q4'])
add('universe 989', mine['universe_dates_total'], prod['universe_days']['primary'])
add('universe QM', mine['own_dates_total']['QM'], prod['universe_days']['QM'])
add('universe ZM', mine['own_dates_total']['ZM'], prod['universe_days']['ZM'])
add('other root bars', mine['root_not_QM_ZM_records'], prod['other_root']['bars'])
n = len(rows); bad = [r for r in rows if not r[3]]
print('compared', n, 'match', n - len(bad), 'differ', len(bad))
for r in bad:
    print('DIFF', r[0], '| mine:', str(r[1])[:90], '| producer:', str(r[2])[:90])
json.dump([[a, str(b), str(c), d] for a, b, c, d in rows], open('compare_rows.json', 'w'))
