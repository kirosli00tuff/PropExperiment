"""RankingReviewer-FableXHigh: independent recomputation of the Stage E.28 Part A ranking (spec section 2-4).

Written from the frozen spec text (reports/stage_e28_ranking_spec.md, sha256 89347e97...a5f) and the lead rulings
(A3_lead_rulings.json). Does NOT import score.py. Reads the same four fact files and the mask key.

Usage: python3 rr_score.py            -> writes rr_primary.json, rr_variants.json, prints the diff vs A3_ranking_table.json
"""
import hashlib
import json
import math
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
BR = os.path.abspath(os.path.join(HERE, '..', '..'))
REPO = os.path.abspath(os.path.join(BR, '..', '..'))
SPEC = os.path.join(REPO, 'reports', 'stage_e28_ranking_spec.md')
SPEC_SHA = '89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f'
INF = math.inf

W1 = {'C1': 0.25, 'C2': 0.20, 'C3': 0.15, 'C4': 0.15, 'C5': 0.10, 'C6': 0.15}
W2 = {'E': 0.40, 'D': 0.10, 'R': 0.10, 'A': 0.15, 'F': 0.10, 'P': 0.05, 'Rel': 0.10}
FIRM_NAME = {'topstep': 'Topstep', 'lucid': 'Lucid Trading', 'tradeify': 'Tradeify', 'mffu': 'My Funded Futures',
             'bulenox': 'Bulenox'}


def load(name):
    with open(os.path.join(BR, name)) as fh:
        return json.load(fh)


def v(cell):
    return None if cell is None else cell.get('value')


# ---------------------------------------------------------------- spec section 2 anchors (my own reading)
def c1(a, b):
    a = 'medium' if a in (None, 'unknown') else a
    b = 'high' if b in (None, 'unknown') else b
    return 2 + {'high': 1, 'medium': 0, 'low': -1}[a] + {'low': 1, 'medium': 0, 'high': -1}[b]


def c2(qv, r):
    if qv is not None:
        return 4 if qv <= 0.5 else 3 if qv <= 2 else 2 if qv <= 5 else 1 if qv <= 15 else 0
    if r is not None:
        return 1 if r >= 1.0 else 2 if r >= 0.5 else 3 if r >= 0.1 else 2
    return 1


def c3(adv, ratio):
    if adv is None:
        s = 1
    else:
        s = 4 if adv >= 200000 else 3 if adv >= 50000 else 2 if adv >= 10000 else 1 if adv >= 1000 else 0
    if ratio is not None and ratio >= 3:
        s = max(0, s - 1)
    return s


def c4(items):
    # an item holds if True; unknown (string or None) counts as holding
    return max(0, 4 - sum(1 for x in items if x is True or x in ('unknown', None)))


def c5(sig):
    if sig is None:
        return 1
    if 1.5 <= sig <= 6:
        return 4
    if 1 <= sig < 1.5 or 6 < sig <= 10:
        return 3
    if 0.5 <= sig < 1 or 10 < sig <= 20:
        return 2
    if 0.25 <= sig < 0.5 or 20 < sig <= 40:
        return 1
    return 0


def s_fn(x, x0):
    if x is None:
        return None
    if x == INF:
        return 0.0
    return 4.0 * max(0.0, 1.0 - x / x0)


def e_score(ml, mm, m10, unknown=1):
    parts = [s_fn(ml, 2.0), s_fn(mm, 3.0), s_fn(m10, 3.0)]
    parts = [unknown if p is None else p for p in parts]
    return 0.60 * parts[0] + 0.15 * parts[1] + 0.25 * parts[2]


def d_score(room, unknown=1):
    if room is None:
        return unknown
    return 4 if room >= 4 else 3 if room >= 3 else 2 if room >= 2 else 1 if room >= 1 else 0


def parse_mu(x):
    if x is None:
        return None
    if isinstance(x, str):
        return INF if '>' in x else float(x)
    return INF if x > 4 else float(x)


def round2(x):
    return float(Decimal(repr(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------- scoring
def layer1(facts, blind_c, key, opts):
    """opts: jump_transfer (bool), mng_gate (bool), c6_floor (int|None), c6_cap_unverified (set of codes -> cap 2),
    c1b_unknown_high (bool), c4_conservative (bool)."""
    out = {}
    lab_of = {code: lab for lab, code in key['contracts'].items()}
    for code, r in facts['candidates'].items():
        q = r['QV_or_r']
        proxy = 'proxy' in (q.get('flags') or [])
        qv = None if proxy else v(q)
        rr = v(q) if proxy else None
        C2 = c2(qv, rr)
        C3 = c3(v(r['ADV']), v(r['spread_ratio_overnight_main']))
        c4cells = dict(r['C4'])
        if opts.get('jump_transfer'):
            for k, cell in facts['variants']['C4_jump_transfer'].get(code, {}).items():
                c4cells[k] = cell
        items = []
        for k, cell in c4cells.items():
            x = cell.get('value')
            if opts.get('c4_conservative') and 'ambiguous' in (cell.get('flags') or []):
                x = True
            items.append(x)
        C4 = c4(items)
        C5 = c5(v(r['sigma_1m']))
        b = blind_c[lab_of[code]]
        c1b = b.get('C1b')
        if opts.get('c1b_unknown_high') and b.get('C1b_alt_if_partial_unknown_counts_high'):
            c1b = b['C1b_alt_if_partial_unknown_counts_high']
        C1 = c1(b.get('C1a'), c1b)
        C6r = int(b['C6'])
        C6 = C6r
        if opts.get('c6_floor') is not None and C6 < opts['c6_floor']:
            C6 = opts['c6_floor']
        if code in opts.get('c6_cap_unverified', set()) and C6 > 2:
            C6 = 2
        sc = {'C1': C1, 'C2': C2, 'C3': C3, 'C4': C4, 'C5': C5, 'C6': C6}
        L1 = sum(W1[k] * sc[k] for k in W1)
        gate60 = v(r['gate_60_dates'])
        if code == 'MNG' and opts.get('mng_gate'):
            gate60 = True
        reasons = []
        if round(L1, 9) < 2.0:
            reasons.append('L1<2')
        if any(sc[k] == 0 for k in W1):
            reasons.append('zero:' + ','.join(k for k in W1 if sc[k] == 0))
        if gate60 is not True:
            reasons.append('gate60:' + str(gate60))
        out[code] = {**sc, 'C6_rated': C6r, 'L1': L1, 'pass': not reasons, 'reasons': reasons,
                     'sigma': v(r['sigma_1m']), 'R_d': v(r['R_d']), 'v': v(r['tick_value'])}
    return out


def layer2(facts, l1, fp, econ, blind_f, key, opts):
    lab_of = {firm: lab for lab, firm in key['firms'].items()}
    cls = {c: r['product_class'] for c, r in facts['candidates'].items()}
    pairs = []
    for p in fp['pairs']:
        if p['listed_50k']['value'] != 'yes':
            continue
        firm, code = p['firm'], p['code']
        fo = fp['firms'][firm]
        e = econ.get((firm, code))
        ml = mm = m10 = cost = None
        if e is not None:
            ml, mm, m10 = parse_mu(e.get('mu_star_lim')), parse_mu(e.get('mu_star_mkt')), parse_mu(e.get('mu10K'))
            cost = e.get('cost_per_attempt_usd')
        ov = opts.get('econ_override', {}).get((firm, code))
        if ov:
            ml, mm, m10 = ov['mu_star_lim'], ov['mu_star_mkt'], ov['mu10K']
            cost = ov.get('cost_per_attempt_usd', cost)
        E = e_score(ml, mm, m10, unknown=opts.get('e_unknown', 1))
        mll = v(fo['MLL_usd'])
        rd, tv = l1[code]['R_d'], l1[code]['v']
        room = mll / (rd * tv) if (mll and rd and tv) else None
        D = d_score(room, unknown=opts.get('d_unknown', 1))
        bf = blind_f[lab_of[firm]]
        Rraw = bf['R']
        R = Rraw.get(cls[code]) if isinstance(Rraw, dict) else int(Rraw)
        if R is None:
            R = 1    # spec: unknown gives 1
        if opts.get('r_by_size') and isinstance(bf.get('R_by_size'), dict):
            bs = bf['R_by_size'].get(cls[code])
            if bs:
                micro = facts['candidates'][code].get('code', code) in opts['micro_codes']
                R = bs['micro'] if micro else bs['non_micro']
        A, F = int(bf['A']), int(bf['F'])
        ded = bf['Rel_deductions']
        Rel = max(0, 4 - sum(int(x) for x in ded.values()))
        if opts.get('rel_override', {}).get(firm) is not None:
            Rel = opts['rel_override'][firm]
        P = max(0, 4 - sum(1 for c in fo['P_items'].values() if c.get('value') is True or c.get('value') in ('unknown', None)))
        sc = {'E': E, 'D': D, 'R': R, 'A': A, 'F': F, 'P': P, 'Rel': Rel}
        L2 = sum(W2[k] * sc[k] for k in W2)
        S = 0.5 * l1[code]['L1'] + 0.5 * L2
        gates = []
        if fo['bc_eligible']['value'] is not True:
            gates.append('BC')
        if A == 0:
            gates.append('A=0')
        elig = l1[code]['pass'] and not gates
        pairs.append({'firm': firm, 'code': code, **sc, 'L2': L2, 'L1': l1[code]['L1'], 'S': S,
                      'mu_star_lim': ml, 'mu_star_mkt': mm, 'mu10K': m10, 'cost': cost, 'room': room,
                      'eligible': elig, 'gates': gates})
    def keyf(p):
        mu = p['mu_star_lim'] if p['mu_star_lim'] is not None else INF
        cost = p['cost'] if p['cost'] is not None else INF
        return (-round2(p['S']), mu, -p['L1'], cost, p['code'], FIRM_NAME[p['firm']])
    ranked = sorted([p for p in pairs if p['eligible']], key=keyf)
    for i, p in enumerate(ranked):
        p['rank'] = i + 1
    return pairs, ranked


def read_econ(d):
    return {(p['firm'], p['code']): p for p in d['pairs']}


MICRO = {'MCL', 'MNG', 'MGC', 'SIL', 'MHG', 'M6E', 'M6A', 'MET', 'MBT', 'M2K', 'MYM', 'MNQ', '2YY', '5YY', '10Y', '30Y',
         'MZC', 'MZS', 'MZW', 'MZL', 'MZM'}


def run(opts, facts, fp, econ, blind, key):
    l1 = layer1(facts, blind['contracts'], key, opts)
    pairs, ranked = layer2(facts, l1, fp, econ, blind['firms'], key, opts)
    return l1, pairs, ranked


def fmt(x):
    if x is None:
        return '-'
    if x == INF:
        return '> 4'
    return f'{x:.2f}' if isinstance(x, float) else str(x)


def top(ranked, n=10):
    return [f"{p['rank']}. {p['firm']} {p['code']} S={p['S']:.3f} (L1 {p['L1']:.3f}, L2 {p['L2']:.3f}, E {p['E']:.2f}, mu*lim {fmt(p['mu_star_lim'])})"
            for p in ranked[:n]]


def main():
    with open(SPEC, 'rb') as fh:
        got = hashlib.sha256(fh.read()).hexdigest()
    assert got == SPEC_SHA, got
    facts, fp, blind, econ_raw, key = (load('A3_facts.json'), load('A3_firm_products.json'),
                                       load('A3_blind_ratings.json'), load('A3_econ.json'), load('A3_mask_key.json'))
    econ = read_econ(econ_raw)
    primary = {'jump_transfer': True, 'mng_gate': True, 'c6_floor': 2, 'd_unknown': 1, 'e_unknown': 1}
    l1, pairs, ranked = run(primary, facts, fp, econ, blind, key)
    # ------------------------------------------------------------ diff vs the published table
    pub = load('A3_ranking_table.json')['variants']['primary']
    mism = []
    for code, r in l1.items():
        q = pub['layer1'][code]
        for k in ('C1', 'C2', 'C3', 'C4', 'C5', 'C6'):
            if r[k] != q[k]:
                mism.append(f'L1 {code} {k}: mine {r[k]} pub {q[k]}')
        if abs(r['L1'] - q['L1']) > 1e-9:
            mism.append(f'L1 {code} L1: mine {r["L1"]} pub {q["L1"]}')
        if r['pass'] != bool(q['L1_gate_pass']):
            mism.append(f'L1 {code} gate: mine {r["pass"]} {r["reasons"]} pub {q["L1_gate_pass"]} {q["L1_gate_reasons"]}')
    pubp = {(p['firm'], p['code']): p for p in pub['pairs']}
    for p in pairs:
        q = pubp.get((p['firm'], p['code']))
        if q is None:
            mism.append(f'pair {p["firm"]} {p["code"]}: mine listed, pub missing')
            continue
        for k in ('E', 'D', 'R', 'A', 'F', 'P', 'Rel', 'L2', 'S'):
            a, b = p[k], q[k]
            if a is None or b is None or abs(float(a) - float(b)) > 1e-9:
                mism.append(f'pair {p["firm"]} {p["code"]} {k}: mine {a} pub {b}')
        if p.get('rank') != q.get('rank'):
            mism.append(f'pair {p["firm"]} {p["code"]} rank: mine {p.get("rank")} pub {q.get("rank")}')
    extra = set(pubp) - {(p['firm'], p['code']) for p in pairs}
    for k in sorted(extra):
        mism.append(f'pair {k}: pub listed, mine not')
    print(f'listed {len(pairs)} ranked {len(ranked)} L1 survivors {sum(1 for r in l1.values() if r["pass"])}')
    print(f'MISMATCHES vs published primary: {len(mism)}')
    for m in mism[:60]:
        print('  ', m)
    print('TOP 10 (mine):')
    for s in top(ranked):
        print('  ', s)
    out = {'spec_sha256': got, 'opts': {k: (sorted(v) if isinstance(v, set) else v) for k, v in primary.items()},
           'layer1': l1, 'pairs': pairs, 'ranked': ranked, 'mismatches': mism}
    with open(os.path.join(HERE, 'rr_primary.json'), 'w') as fh:
        json.dump(json.loads(json.dumps(out, default=lambda o: '> 4' if o == INF else str(o))), fh, indent=1)
    # ------------------------------------------------------------ reviewer variants
    grains_abstract_only = {c for c, b in ((key['contracts'][lab], b) for lab, b in blind['contracts'].items())
                            if int(b['C6']) >= 3 and 'abstract only' in (b['reasons'].get('C6') or '')}
    variants = {
        'primary': primary,
        'OC6_cap_abstract_only_C6': {**primary, 'c6_cap_unverified': grains_abstract_only},
        'C1b_unknown_counts_high': {**primary, 'c1b_unknown_high': True},
        'C4_conservative': {**primary, 'c4_conservative': True},
        'topstep_R_by_size_micro4': {**primary, 'r_by_size': True, 'micro_codes': MICRO},
        'lucid_Rel3': {**primary, 'rel_override': {'lucid': 3}},
        'tradeify_Rel2': {**primary, 'rel_override': {'tradeify': 2}},
    }
    variants['topstep_Rel2_lawsuit_as_dispute'] = {**primary, 'rel_override': {'topstep': 2}}
    # econ overrides from my re-runs (rr_econ_rerun.py), if present
    def rows_to_override(rows):
        return {(r['firm'], r['code']): {'mu_star_lim': parse_mu(r['mu_star_lim']), 'mu_star_mkt': parse_mu(r['mu_star_mkt']),
                                         'mu10K': parse_mu(r['mu10K']), 'cost_per_attempt_usd': r.get('cost_per_attempt_usd')}
                for r in rows}
    alt = os.path.join(HERE, 'rr_econ_altfee.json')
    if os.path.exists(alt):
        with open(alt) as fh:
            rows = json.load(fh)['rows']
        for fee, name in ((3.70, 'topstep_fee_3.70_RT'), (7.40, 'topstep_fee_3.70_per_side')):
            sel = [r for r in rows if r.get('reviewer_fee_override') == fee]
            if sel:
                variants[name] = {**primary, 'econ_override': rows_to_override(sel)}
    luc = os.path.join(HERE, 'rr_econ_lucidalt.json')
    if os.path.exists(luc):
        with open(luc) as fh:
            rows = json.load(fh)['rows']
        if rows:
            variants['lucid_fee_u_rule'] = {**primary, 'econ_override': rows_to_override(rows)}
    seeds = [os.path.join(HERE, f'rr_econ_{j}.json') for j in ('seedA', 'seedB')]
    if all(os.path.exists(s) for s in seeds):
        rows = []
        for s in seeds:
            with open(s) as fh:
                rows += json.load(fh)['rows']
        variants['econ_seed_20261022'] = {**primary, 'econ_override': rows_to_override(rows)}
    res = {}
    for name, o in variants.items():
        l1v, pv, rv = run(o, facts, fp, econ, blind, key)
        res[name] = {'top10': top(rv), 'survivors': sum(1 for r in l1v.values() if r['pass']),
                     'ranked': [{k: (fmt(p[k]) if k in ('mu_star_lim', 'mu_star_mkt', 'mu10K') else p[k])
                                 for k in ('rank', 'firm', 'code', 'S', 'L1', 'L2', 'E', 'D', 'R', 'A', 'F', 'P', 'Rel',
                                           'mu_star_lim', 'mu_star_mkt', 'mu10K', 'cost')} for p in rv],
                     'mnq': [f"{p['firm']} {p.get('rank', '-')}" for p in pv if p['code'] == 'MNQ'],
                     'C6_capped': sorted(o.get('c6_cap_unverified', [])) if 'c6_cap_unverified' in o else None}
        print(f'\n== variant {name}: survivors {res[name]["survivors"]}')
        for s in res[name]['top10'][:6]:
            print('  ', s)
    with open(os.path.join(HERE, 'rr_variants.json'), 'w') as fh:
        json.dump(res, fh, indent=1, default=str)


if __name__ == '__main__':
    main()
