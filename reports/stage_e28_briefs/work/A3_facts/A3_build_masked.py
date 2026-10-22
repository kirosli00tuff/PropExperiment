"""Stage E.28 A3 (FactTable): masked evidence sheets for the blind scorer, and the mask key.

A3_masked_contracts.json: per contract label (C01..), only the evidence text for C1(a), C1(b) and C6.
A3_masked_firms.json: per firm label (F01..F05), the evidence for R (per product class), A, F and the Rel items.
Labels are assigned in random order with seed 28 (random.Random(28): candidates sorted then shuffled, then firms,
then platforms, then other product codes). The key goes to A3_mask_key.json (the lead holds it).
The study relation to each label is normalized to SAME / SIBLING / COUSIN / CLASS / UNSTATED / NONE from the readers'
own relation fields (no rating).
"""
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A3_common import (BR, CANDIDATES, CLASS_OF, FAMILIES, FAMILY_OF, FIRMS, OTHER_CODES, PLATFORM_PATTERNS,  # noqa: E402
                       Masker, load)
from A3_research_items import items_for  # noqa: E402

C1A_KEYS = ['retail', 'small_trader', 'commercial', 'hedger', 'nonrep', 'tff', 'trader_type', 'cot_', 'manual_share',
            'reportable_level', 'outside_us_hours']
C1B_KEYS = ['market_maker', 'hft', 'ats_share', 'automated', 'spread', 'depth', 'touch_queue', 'queue', 'match',
            'volume_per_minute', 'brokertec', 'relation_to_es', 'spot_interaction']
RESEARCH_KEYS = {'microstructure_research', 'microstructure_studies', 'research'}
REL_HELP = {
    'SAME': 'study on this product itself',
    'SIBLING': 'study on a micro, mini or full-size version of this product on the same underlying',
    'COUSIN': 'study on another product of the same asset class on CME Globex',
    'CLASS': 'study on futures broadly or the asset class broadly (other venues, spot, theory)',
    'UNSTATED': 'venue or product of the study not stated in the reader\'s source (may be this product or a cousin)',
    'NONE': 'negative search result (no study found)',
}
RATING_SCHEMA = {
    'file': 'reports/stage_e28_briefs/A3_blind_ratings.json',
    'contracts': {'<Cnn>': {'C1a': 'high | medium | low  (unknown -> medium)',
                            'C1b': 'low | medium | high  (unknown -> high)',
                            'C6': 'integer 0..4 by the spec anchors',
                            'reasons': {'C1a': 'one line quoting the masked evidence', 'C1b': '...', 'C6': '...'}}},
    'firms': {'<Fnn>': {'R': {'<product class>': 'integer 0..4 (unknown -> 1); give every class listed in the sheet'},
                        'A': 'integer 0..4 (0 = the pair gate fails)',
                        'F': 'integer 1, 2 or 4',
                        'Rel_deductions': {'under_2_years': '0 or 1', 'payout_delays_denials_disputes_12m': '0 or 1',
                                           'two_plus_adverse_rule_changes_12m': '0 or 1', 'regulatory_action_vs_firm': '0 or 2'},
                        'reasons': {'R': '...', 'A': '...', 'F': '...', 'Rel': '...'}}},
}


def assign_labels():
    rng = random.Random(28)
    cands = sorted(CANDIDATES)
    rng.shuffle(cands)
    firms = sorted(FIRMS)
    rng.shuffle(firms)
    plats = sorted(PLATFORM_PATTERNS)
    rng.shuffle(plats)
    others = sorted(set(OTHER_CODES))
    rng.shuffle(others)
    return ({c: f'C{i + 1:02d}' for i, c in enumerate(cands)}, {f: f'F{i + 1:02d}' for i, f in enumerate(firms)},
            {p: f'P{i + 1:02d}' for i, p in enumerate(plats)}, {o: f'X{i + 1:02d}' for i, o in enumerate(others)})


def product_names(a1):
    names = []
    for fam, rows in a1.items():
        for r in rows:
            pn = r.get('product_name')
            v = pn.get('value') if isinstance(pn, dict) else pn
            if v:
                names.append(v)
                names.append(re.sub(r'\s*\(.*?\)', '', v).strip())
                names.append(re.sub(r'\s+[Ff]utures$', '', re.sub(r'\s*\(.*?\)', '', v).strip()))
    return [n for n in names if len(n) > 4]


def cellstr(v):
    if isinstance(v, dict):
        return {k: v.get(k) for k in ('value', 'unit', 'window', 'quote', 'note') if v.get(k) not in (None, '')}
    return {'value': v}


def mask_cell(mask, fam, field, v, limit=700):
    c = cellstr(v)
    out = {'field': mask(field, fam, refs=False)}
    for k, x in c.items():
        s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
        out[k] = mask(s, fam)[:limit]
    return out


# ---------------------------------------------------------------------------------------------- relation normalizing
def rel_from_text(t):
    t = (t or '').lower()
    if not t or t in ('-', 'none'):
        return 'NONE'
    if 'same underlying' in t or 'full-size version' in t or 'micro version' in t or 'mini' in t and 'version' in t:
        return 'SIBLING'
    if t.startswith('same product') or t == 'same':
        return 'SAME'
    if 'close cousin' in t or t == 'cousin':
        return 'COUSIN'
    if 'asset class' in t or 'futures broadly' in t or t == 'class':
        return 'CLASS'
    if 'not stated' in t or 'unknown' in t:
        return 'UNSTATED'
    return 'UNSTATED'


def rates_table():
    """F12 table rows of A1_rates.md: id -> (study, product, result, evidence)."""
    rows = {}
    with open(os.path.join(BR, 'A1_rates.md')) as fh:
        for line in fh:
            m = re.match(r'^\| (R\d+) \| (.*)$', line.strip())
            if m:
                cols = [c.strip() for c in m.group(2).split(' | ')]
                rows[m.group(1)] = {'study': cols[0] if cols else '', 'product': cols[1] if len(cols) > 1 else '',
                                    'relation_to_ZN': cols[2] if len(cols) > 2 else '',
                                    'result': cols[3] if len(cols) > 3 else '', 'evidence': cols[4] if len(cols) > 4 else ''}
    return rows


def expand_ids(s):
    ids = []
    for a, b in re.findall(r'R(\d+)(?:-R(\d+))?', s):
        a = int(a)
        b = int(b) if b else a
        ids += [f'R{i}' for i in range(a, b + 1)]
    return ids


def research_for(code, fam, row, a1map, rtab):
    """List of (relation_code, item dict) for C6, per the reader's relation fields."""
    out = []
    if fam == 'rates':
        txt = row['microstructure_research']['value']
        if code in ('2YY', '5YY', '10Y', '30Y'):
            m_fam = re.search(r'FAM relation[^:]*: see F12 ([^.]+)\.', txt)
            m_cls = re.search(r'CLASS: ([^.]+)\.', txt)
            for rid in expand_ids(m_fam.group(1) if m_fam else ''):
                out.append(('SIBLING', dict(rtab.get(rid, {}), id=rid, reader_relation='FAM (same tenor, different design)')))
            for rid in expand_ids(m_cls.group(1) if m_cls else ''):
                out.append(('CLASS', dict(rtab.get(rid, {}), id=rid, reader_relation='CLASS')))
            out.append(('NONE', {'study': 'no study on this product itself found', 'note': txt}))
        else:
            for rid, inner in re.findall(r'(R\d+) \(([^)]*)\)', txt):
                code_txt = inner.split(',')[0].strip()
                rc = {'SAME': 'SAME', 'COUSIN': 'COUSIN', 'CLASS': 'CLASS', 'FAM': 'SIBLING', 'SAME/COUSIN': 'UNSTATED'}.get(
                    code_txt.split(' ')[0], 'UNSTATED')
                out.append((rc, dict(rtab.get(rid, {}), id=rid, reader_relation=inner)))
        return out
    items = items_for(fam, row)
    if not items and fam == 'grains' and code.startswith('MZ'):
        src = {'MZC': 'ZC', 'MZS': 'ZS', 'MZW': 'ZW', 'MZL': 'ZL', 'MZM': 'ZM'}[code]
        note = (row.get('microstructure_research') or {}).get('note', '')
        for rc, sub in research_for(src, fam, a1map[src], a1map, rtab):
            out.append(('SIBLING' if rc == 'SAME' else rc,
                        dict(sub, reader_relation=f'(reader: "{note}") from the full-size record: ' + str(sub.get('reader_relation', '')))))
        return out
    if fam == 'fx':
        for it in items:
            note = it.get('note') or ''
            m = re.search(r'relation: ([^;]+);\s*result: (.*)', note)
            rel = m.group(1) if m else ''
            res = m.group(2) if m else note
            rc = 'NONE' if it.get('study') in (None, 'None') else rel_from_text(rel)
            if 'CME FX futures' in rel:
                rc = 'UNSTATED'
            out.append((rc, {'study': it.get('study'), 'reader_relation': rel, 'result': res, 'quote': it.get('quote')}))
        return out
    sibling_src = {'MCL': 'CL', 'QM': 'CL', 'MGC': 'GC', 'SIL': 'SI', 'MHG': 'HG'}
    for it in items:
        study = str(it.get('study') or '')
        rel = str(it.get('relation') or '')
        if study.startswith('CL studies (see CL record)') or study.startswith('see GC entry'):
            src = sibling_src[code]
            for rc, sub in research_for(src, fam, a1map[src], a1map, rtab):
                if rc == 'SAME':
                    rc = 'SIBLING'
                out.append((rc, dict(sub, reader_relation=f'(from the {src}-sibling record) ' + str(sub.get('reader_relation', '')))))
            continue
        if fam == 'equity':
            rc = {'SAME': 'SAME', 'MMF': 'SIBLING', 'COUSIN': 'COUSIN', 'CLASS': 'CLASS'}.get(rel.strip(), rel_from_text(rel))
        elif fam == 'grains':
            rc = {'same': 'SAME', 'size': 'SIBLING', 'cousin': 'COUSIN'}.get(rel.strip().lower(), rel_from_text(rel))
        elif fam == 'natgas':
            rc = rel_from_text(rel)
            if rc == 'SAME' and code != 'NG':
                rc = 'SIBLING'   # the natgas reader's "same product" studies are on the full-size NG
        elif fam == 'crude' and 'exchange not stated' in rel:
            rc = 'UNSTATED'
        else:
            rc = rel_from_text(rel)
        if 'none found' in str(it.get('result', '')).lower() or study.lower().startswith('none found'):
            rc = 'NONE'
        d = {k: it.get(k) for k in ('study', 'result', 'quote', 'note', 'peer_reviewed') if it.get(k) not in (None, '')}
        d['reader_relation'] = rel
        out.append((rc, d))
    return out


def build_contracts(clab, olab, plab, a1):
    a1map = {(r.get('candidate') or r.get('code')): r for fam in a1 for r in a1[fam]}
    rtab = rates_table()
    mask = Masker(clab, olab, {}, product_names(a1), platform_label=plab)
    sheets = {}
    for code in CANDIDATES:
        fam = FAMILY_OF[code]
        row = a1map[code]
        c1a, c1b = [], []
        for k, v in row.items():
            if k in RESEARCH_KEYS or not isinstance(v, (dict, list)):
                continue
            kl = k.lower()
            if any(x in kl for x in C1A_KEYS):
                c1a.append(mask_cell(mask, fam, k, v))
            elif any(x in kl for x in C1B_KEYS):
                if isinstance(v, list):
                    for i, x in enumerate(v):
                        c1b.append(mask_cell(mask, fam, f'{k}[{i}]', x))
                else:
                    c1b.append(mask_cell(mask, fam, k, v))
        c6 = []
        for rc, it in research_for(code, fam, row, a1map, rtab):
            m = {'relation': rc}
            for k, x in it.items():
                if x in (None, ''):
                    continue
                s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
                m[k] = mask(s, fam)[:700]
            c6.append(m)
        sheets[clab[code]] = {'label': clab[code], 'C1a_evidence': c1a, 'C1b_evidence': c1b, 'C6_evidence': c6}
    ordered = {k: sheets[k] for k in sorted(sheets)}
    return {'_about': 'Stage E.28 Part A masked contract sheets (FactTable-OpusHigh). Evidence text only; product codes, '
                      'product names, underlying names, exchanges, agencies, firms and platforms replaced by labels or tokens '
                      '([U] underlying word, [PRODUCT] product name, [EXCHANGE], [AGENCY], Xnn other products, Pnn '
                      'platforms, [FILE] file names). Cnn labels inside the text are other candidates (siblings or '
                      'cousins). Rate C1 (a), C1 (b) and C6 per the spec anchors.',
            '_relation_codes': REL_HELP, '_rating_schema': RATING_SCHEMA, 'contracts': ordered}


def build_firms(clab, flab, plab, olab, a1):
    fp = load('A3_firm_products.json')
    code_class = {c: CLASS_OF[c] for c in CANDIDATES}
    extra = {'ES': 'equity_index', 'MES': 'equity_index', 'NKD': 'equity_index', 'EMD': 'equity_index', 'PL': 'metals',
             'PA': 'metals', 'RB': 'other energy', 'HO': 'other energy', 'HE': 'livestock', 'LE': 'livestock',
             'GF': 'livestock', 'KE': 'grains', 'TN': 'rates', 'UB': 'rates', 'E7': 'fx', '6B': 'fx', '6J': 'fx',
             '6C': 'fx', '6S': 'fx', '6N': 'fx', 'M6B': 'fx'}
    code_class.update(extra)
    mask = Masker(clab, olab, flab, product_names(a1), code_to_class=code_class, class_tokens=True, platform_label=plab)
    # Globex hours per class from A1 (needed to judge the 25%-of-hours anchor of R)
    hours = {}
    for fam, rows in a1.items():
        th = rows[-1].get('trading_hours') or {}
        hours[CLASS_OF[rows[-1].get('candidate') or rows[-1].get('code')]] = mask(str(th.get('value')), None)
    events = {'crude_oil': 'weekly inventory report (1 per week, inside the main session) central to the class',
              'natural_gas': 'weekly storage report (1 per week, inside the main session) central to the class',
              'grains': 'government crop and export reports (weekly in season, plus monthly) central to the class',
              'equity_index': 'no class-specific weekly report; shares the macro calendar',
              'metals': 'no class-specific weekly report; shares the macro calendar',
              'fx': 'central-bank decisions about 8 per year; shares the macro calendar',
              'crypto': 'no scheduled class-specific report found', 'rates': 'auctions about monthly per tenor; macro calendar'}
    sheets = {}
    for firm in FIRMS:
        fo = fp['firms'][firm]

        def mc(cells):
            out = []
            for path, c in cells.items():
                d = {'item': mask(path.split('.')[-1], None, refs=False)}
                for k in ('value', 'quote', 'note'):
                    if c.get(k) not in (None, ''):
                        s = c[k] if isinstance(c[k], str) else json.dumps(c[k], ensure_ascii=False)
                        d[k] = mask(s, None)[:700]
                out.append(d)
            return out
        r_by_class = {k: mask(v, None) for k, v in fo['restrictions_by_class'].items()}
        classes_listed = sorted({p['product_class'] for p in fp['pairs'] if p['firm'] == firm and p['listed_50k']['value'] == 'yes'})
        plat = {}
        for pl, cells in fo['platform_facts'].items():
            name = {'projectx_topstepx': 'ProjectX/TopstepX', 'tradovate': 'Tradovate', 'rithmic': 'Rithmic'}[pl]
            plat[plab[name]] = mc(cells)
        sheets[flab[firm]] = {
            'label': flab[firm],
            'product_classes_listed_on_50K': classes_listed,
            'R_evidence': {'restrictions_by_class (firm-wide rules under "all")': r_by_class, 'rule_records': mc(fo['R'])},
            'A_evidence': mc(fo['A']),
            'F_evidence': {'firm_records': mc(fo['F']), 'platform_records (API platforms the strategy would use)': plat},
            'Rel_evidence': mc(fo['Rel']),
            'not_scored_context (payout record, Canada terms)': mc(fo['info']),
        }
    ordered = {k: sheets[k] for k in sorted(sheets)}
    return {'_about': 'Stage E.28 Part A masked firm sheets (FactTable-OpusHigh). Firm, platform, plan, payment-service and '
                      'product names replaced by labels or tokens. Product codes are shown only as their product class. '
                      'Rate R per product class listed, A, F and the Rel deductions per the spec anchors.',
            '_class_context': {'globex_hours_by_class': hours, 'class_specific_scheduled_events': events},
            '_rating_schema': RATING_SCHEMA, 'firms': ordered}


def main():
    clab, flab, plab, olab = assign_labels()
    a1 = {fam: load(f'A1_{fam}.json') for fam in FAMILIES}
    contracts = build_contracts(clab, olab, plab, a1)
    firms = build_firms(clab, flab, plab, olab, a1)
    for name, obj in (('A3_masked_contracts.json', contracts), ('A3_masked_firms.json', firms)):
        with open(os.path.join(BR, name), 'w') as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)
    key = {'seed': 28, 'method': 'random.Random(28): sorted candidates shuffled, then sorted firms, then sorted platforms, '
                                 'then sorted other product codes; labels in shuffled order',
           'contracts': {v: k for k, v in sorted(clab.items(), key=lambda x: x[1])},
           'firms': {v: k for k, v in sorted(flab.items(), key=lambda x: x[1])},
           'platforms': {v: k for k, v in sorted(plab.items(), key=lambda x: x[1])},
           'other_products': {v: k for k, v in sorted(olab.items(), key=lambda x: x[1])}}
    with open(os.path.join(BR, 'A3_mask_key.json'), 'w') as fh:
        json.dump(key, fh, indent=1)
    print('contracts', len(contracts['contracts']), 'firms', len(firms['firms']))


if __name__ == '__main__':
    main()
