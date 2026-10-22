"""Stage E.28 Part A scoring script (FactTable-OpusHigh). Applies reports/stage_e28_ranking_spec.md literally.

Reads   reports/stage_e28_briefs/A3_facts.json, A3_firm_products.json, A3_blind_ratings.json, A3_econ.json
        and A3_lead_rulings.json (the lead's rulings of 2026-10-21 15:13 PDT) and A3_lead_rulings_v2.json (16:47 PDT: RR-01,
        RR-03, RR-04, RR-05), applied exactly; see load_rulings. work/REV_rank/rr_econ_lucidalt.json for RR-05
        (and A3_mask_key.json to map the blind labels back to codes and firms).
Writes  reports/stage_e28_briefs/A3_ranking_table.json and A3_ranking_table.md.
Refuses to run if the spec's sha256 differs from the frozen hash.

Missing inputs (no blind ratings or no econ yet) do not stop the run: the criteria that need them are left null,
the table is marked INCOMPLETE and nothing is ranked. Usage: python3 score.py
"""
import hashlib
import json
import math
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A3_common import (BR, CANDIDATES, CLASS_OF, FIRM_SORT_NAME, FIRMS, SPEC_SHA256, spec_sha256)  # noqa: E402

W_L1 = {'C1': 0.25, 'C2': 0.20, 'C3': 0.15, 'C4': 0.15, 'C5': 0.10, 'C6': 0.15}
W_L2 = {'E': 0.40, 'D': 0.10, 'R': 0.10, 'A': 0.15, 'F': 0.10, 'P': 0.05, 'Rel': 0.10}
INF = math.inf
RULINGS_SHA_PREFIX = '82581c92030d4664'     # A3_lead_rulings.json, checked like the spec hash
RULINGS_V2_SHA256 = 'f99b6e9f63de7f22a83838f7f57b193083a68a835eb7f8f235b456751c4f3b1f'   # A3_lead_rulings_v2.json (full hash)
LUCID_ALT_FILE = os.path.join('work', 'REV_rank', 'rr_econ_lucidalt.json')   # reviewer's Lucid economics at the u-rule fee

# RR-03: the 13 blind labels of the grain contracts whose C6 = 3 rests only on an OpenAlex abstract (R_rank.md RR-03: MZC,
# MZS, MZW, MZL, MZM, XC, XK, XW, ZC, ZS, ZW, ZL, ZM, mapped through A3_mask_key.json). Kept by label; the code mapping is
# checked in test_score.py.
RR03_CAP_LABELS = ('C04', 'C08', 'C10', 'C11', 'C13', 'C14', 'C16', 'C23', 'C28', 'C29', 'C35', 'C39', 'C45')
C6_UNVERIFIED_CAP = 2
# RR-04: micro contracts among the candidates (the reviewer's list, rr_score.py MICRO); R_by_size gives micro vs non-micro.
MICRO_CODES = frozenset({'MCL', 'MNG', 'MGC', 'SIL', 'MHG', 'M6E', 'M6A', 'MET', 'MBT', 'M2K', 'MYM', 'MNQ',
                         '2YY', '5YY', '10Y', '30Y', 'MZC', 'MZS', 'MZW', 'MZL', 'MZM'})

# Variants run after the primary. Each changes one thing relative to the primary (rulings applied).
VARIANT_NAMES = ('primary', 'OC1_off', 'C4_conservative', 'QV_proxy_only', 'OC2_published',
                 'D_unknown_0', 'E_unknown_0', 'C4_no_transfer', 'C6_as_rated', 'v1_rulings_only')


# ------------------------------------------------------------------------------------------------ anchor functions
def c1_score(a, b):
    """C1 = 2 + (a: high +1, medium 0, low -1) + (b: low +1, medium 0, high -1). Unknown a -> medium, b -> high."""
    a = (a or 'unknown').strip().lower()
    b = (b or 'unknown').strip().lower()
    a = 'medium' if a == 'unknown' else a
    b = 'high' if b == 'unknown' else b
    da = {'high': 1, 'medium': 0, 'low': -1}[a]
    db = {'low': 1, 'medium': 0, 'high': -1}[b]
    return 2 + da + db


def c2_score(qv=None, r=None):
    """C2 from QV (minutes); else proxy r = tick/sigma_1m (never 4 or 0); else 1."""
    if qv is not None:
        if qv <= 0.5:
            return 4
        if qv <= 2:
            return 3
        if qv <= 5:
            return 2
        if qv <= 15:
            return 1
        return 0
    if r is not None:
        if r >= 1.0:
            return 1
        if r >= 0.5:
            return 2
        if r >= 0.1:
            return 3
        return 2
    return 1


def c3_score(adv, spread_ratio=None):
    """C3 from ADV (contracts/day); minus 1 (floor 0) if a sourced overnight/main spread ratio is >= 3. Unknown ADV -> 1."""
    if adv is None:
        s = 1
    elif adv >= 200_000:
        s = 4
    elif adv >= 50_000:
        s = 3
    elif adv >= 10_000:
        s = 2
    elif adv >= 1_000:
        s = 1
    else:
        s = 0
    if spread_ratio is not None and spread_ratio >= 3:
        s = max(0, s - 1)
    return s


def c4_score(items):
    """C4 = 4 minus the number of items that hold (True) or are unknown (conservative), floor 0."""
    n = sum(1 for v in items if v is True or v == 'unknown' or v is None)
    return max(0, 4 - n)


def c5_score(sigma):
    """C5 from sigma_1m in ticks; boundaries go to the higher score; unknown -> 1."""
    if sigma is None:
        return 1
    x = sigma
    if 1.5 <= x <= 6:
        return 4
    if 1 <= x < 1.5 or 6 < x <= 10:
        return 3
    if 0.5 <= x < 1 or 10 < x <= 20:
        return 2
    if 0.25 <= x < 0.5 or 20 < x <= 40:
        return 1
    return 0


def l1_value(s):
    return sum(W_L1[k] * s[k] for k in W_L1)


def l1_gate(l1, scores, gate60):
    """Layer 1 gate: L1 >= 2.00, no criterion 0, traded on >= 60 Globex dates (unknown counts as not shown)."""
    reasons = []
    if round(l1, 10) < 2.0:
        reasons.append('L1 < 2.00')
    zeros = [k for k in W_L1 if scores[k] == 0]
    if zeros:
        reasons.append('criterion 0: ' + ','.join(zeros))
    if gate60 is not True:
        reasons.append('60-date gate ' + ('unknown (not shown)' if gate60 == 'unknown' else 'fails'))
    return (not reasons), reasons


def s_fn(x, x0):
    """s(x; x0) = 4 * max(0, 1 - x / x0); x = inf ('> 4') gives 0."""
    if x is None:
        return None
    if x == INF:
        return 0.0
    return 4.0 * max(0.0, 1.0 - x / x0)


def e_score(mu_lim, mu_mkt, mu10k, unknown=1):
    """E = 0.60 s(mu_lim; 2) + 0.15 s(mu_mkt; 3) + 0.25 s(mu10K; 3). Ruling OC-A3-3: each s() component whose mu is
    unknown scores `unknown` (1), so E = 1 when all three are unknown; the E_unknown_0 variant passes 0."""
    parts = [s_fn(mu_lim, 2.0), s_fn(mu_mkt, 3.0), s_fn(mu10k, 3.0)]
    parts = [unknown if p is None else p for p in parts]
    return 0.60 * parts[0] + 0.15 * parts[1] + 0.25 * parts[2]


def d_score(room, unknown=1):
    """D from room = MLL / (R_d v). Unknown room -> `unknown` (ruling OC-A3-2: 1, the spec's general unknown default;
    the D_unknown_0 variant passes 0). Flagged u by the caller."""
    if room is None:
        return unknown
    if room >= 4:
        return 4
    if room >= 3:
        return 3
    if room >= 2:
        return 2
    if room >= 1:
        return 1
    return 0


def p_score(items):
    """P = 4 minus the number of deductions that hold (True or unknown), floor 0."""
    n = sum(1 for v in items if v is True or v == 'unknown' or v is None)
    return max(0, 4 - n)


def rel_score(deductions):
    """Rel = 4 minus the deductions (1, 1, 1, 2), floor 0."""
    return max(0, 4 - sum(deductions))


def l2_value(s):
    return sum(W_L2[k] * s[k] for k in W_L2)


def round2(x):
    return float(Decimal(repr(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def rank_key(p):
    """Spec tie rule: S rounded to 2 decimals (half-up), then lower mu*_lim, higher L1, lower cost per attempt,
    contract code, firm name (alphabetical)."""
    mu = p['mu_star_lim'] if p['mu_star_lim'] is not None else INF
    cost = p['cost_per_attempt_usd'] if p['cost_per_attempt_usd'] is not None else INF
    return (-round2(p['S']), mu, -p['L1'], cost, p['code'], FIRM_SORT_NAME[p['firm']])


TIE_LEVELS = ('S rounded', 'mu*_lim', 'L1', 'cost per attempt', 'contract code', 'firm name')


def find_ties(ranked):
    """Groups of consecutive ranked pairs with equal S rounded to 2 decimals; for each adjacent pair, the first
    tie-rule level that separated them (the spec's order)."""
    groups, cur = [], []
    for p in ranked:
        if cur and round2(p['S']) != round2(cur[-1]['S']):
            groups.append(cur)
            cur = []
        cur.append(p)
    groups.append(cur)
    out = []
    for g in groups:
        if len(g) < 2:
            continue
        steps = []
        for a, b in zip(g, g[1:]):
            ka, kb = rank_key(a), rank_key(b)
            lvl = next(i for i in range(len(ka)) if ka[i] != kb[i])
            steps.append({'higher': f"{a['firm']} {a['code']}", 'lower': f"{b['firm']} {b['code']}", 'decided_by': TIE_LEVELS[lvl]})
        out.append({'S_rounded': round2(g[0]['S']), 'ranks': [p['rank'] for p in g],
                    'pairs': [f"{p['firm']} {p['code']}" for p in g], 'steps': steps})
    return out


# ------------------------------------------------------------------------------------------------ input readers
def load_json(name):
    path = os.path.join(BR, name)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def norm_key(k):
    return ''.join(ch for ch in str(k).lower() if ch.isalnum())


def getk(d, *names):
    if not isinstance(d, dict):
        return None
    nd = {norm_key(k): v for k, v in d.items()}
    for n in names:
        if norm_key(n) in nd:
            return nd[norm_key(n)]
    return None


def parse_mu(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return INF if x > 4 else float(x)
    s = str(x).strip()
    if '>' in s:
        return INF
    try:
        v = float(s)
        return INF if v > 4 else v
    except ValueError:
        return None


def norm_firm(f):
    f = str(f).lower()
    for key, pat in (('topstep', 'topstep'), ('lucid', 'lucid'), ('tradeify', 'tradeify'), ('mffu', 'mffu'),
                     ('mffu', 'funded futures'), ('bulenox', 'bulenox')):
        if pat in f:
            return key
    return f


def read_econ(d):
    if d is None:
        return {}
    if isinstance(d, dict) and isinstance(d.get('pairs'), list):
        rows = d['pairs']
    elif isinstance(d, list):
        rows = d
    elif isinstance(d, dict) and isinstance(d.get('pairs'), dict):
        rows = list(d['pairs'].values())
    else:
        rows = [v for v in d.values() if isinstance(v, dict) and getk(v, 'code') is not None]
    out = {}
    for r in rows:
        firm, code = getk(r, 'firm'), getk(r, 'code', 'candidate')
        if firm is None or code is None:
            continue
        out[(norm_firm(firm), str(code))] = {
            'mu_star_lim': parse_mu(getk(r, 'mu_star_lim', 'mustar_lim', 'mu*_lim')),
            'mu_star_mkt': parse_mu(getk(r, 'mu_star_mkt', 'mustar_mkt', 'mu*_mkt')),
            'mu10K': parse_mu(getk(r, 'mu10K', 'mu_10K', 'mu10k')),
            'cost_per_attempt_usd': getk(r, 'cost_per_attempt_usd', 'cost_per_attempt'),
            'MLL_usd': getk(r, 'MLL_usd', 'mll'), 'room': getk(r, 'room'), 'flags': getk(r, 'flags'),
            'raw_mu': {k: getk(r, k) for k in ('mu_star_lim', 'mu_star_mkt', 'mu10K')},
        }
    return out


def read_blind(d, key):
    """Map label-keyed blind ratings back to codes and firms through the mask key."""
    if d is None or key is None:
        return {}, {}
    cons = getk(d, 'contracts') or {k: v for k, v in d.items() if str(k).startswith('C')}
    firms = getk(d, 'firms') or {k: v for k, v in d.items() if str(k).startswith('F')}
    c_out, f_out = {}, {}
    for lab, r in (cons or {}).items():
        code = key['contracts'].get(lab)
        if code is None:
            continue
        c6 = getk(r, 'C6')
        c_out[code] = {'C1a': getk(r, 'C1a', 'C1_a', 'C1 (a)'), 'C1b': getk(r, 'C1b', 'C1_b', 'C1 (b)'),
                       'C6': None if c6 is None else int(c6), 'label': lab}
    for lab, r in (firms or {}).items():
        firm = key['firms'].get(lab)
        if firm is None:
            continue
        R = getk(r, 'R')
        reld = getk(r, 'Rel_deductions', 'Rel deductions', 'reldeductions')
        if isinstance(reld, dict):
            ded = []
            for k, v in reld.items():
                if isinstance(v, dict):
                    v = getk(v, 'value', 'deduction', 'points')
                ded.append(int(v or 0))
            rel = rel_score(ded)
        else:
            relv = getk(r, 'Rel')
            rel = int(relv) if isinstance(relv, (int, float)) else None
            ded = None
        f_out[firm] = {'R': R, 'R_by_size': getk(r, 'R_by_size'), 'A': getk(r, 'A'), 'F': getk(r, 'F'), 'Rel': rel,
                       'Rel_deductions': ded, 'label': lab}
    return c_out, f_out


def r_for(firm_r, cls):
    """R rating for a product class: int for all classes, or a dict per class ('all' as fallback). Unknown -> 1."""
    if firm_r is None:
        return None
    if isinstance(firm_r, (int, float)):
        return int(firm_r)
    if isinstance(firm_r, dict):
        v = getk(firm_r, cls)
        if v is None:
            v = getk(firm_r, 'all', 'all classes', 'default')
        if isinstance(v, dict):
            v = getk(v, 'level', 'value', 'R')
        return 1 if v is None else int(v)
    return 1


def r_by_size_for(bf, code, cls):
    """RR-04: the blind scorer's R_by_size reading (micro / non-micro) for a firm and product class, or None when the
    firm's sheet gives no R_by_size entry for the class."""
    tbl = getk(bf.get('R_by_size'), cls) if isinstance(bf.get('R_by_size'), dict) else None
    if not isinstance(tbl, dict):
        return None
    v = tbl.get('micro' if code in MICRO_CODES else 'non_micro')
    return None if v is None else int(v)


# ------------------------------------------------------------------------------------------------ scoring
def val(cell):
    return None if cell is None else cell.get('value')


def load_rulings():
    """Read A3_lead_rulings.json (v1) and A3_lead_rulings_v2.json and return the parameters they fix. Refuses on a hash
    mismatch (v1: sha256 prefix; v2: full sha256) or a missing file. v2 inherits every v1 ruling and adds RR-01, RR-03,
    RR-04 and RR-05."""
    def read(name, ok):
        path = os.path.join(BR, name)
        if not os.path.exists(path):
            sys.exit(f'REFUSED: {name} missing')
        with open(path, 'rb') as fh:
            raw = fh.read()
        got = hashlib.sha256(raw).hexdigest()
        if not ok(got):
            sys.exit(f'REFUSED: {name} sha256 {got} does not match the frozen hash')
        return got, json.loads(raw)
    got, d = read('A3_lead_rulings.json', lambda g: g.startswith(RULINGS_SHA_PREFIX))
    got2, d2 = read('A3_lead_rulings_v2.json', lambda g: g == RULINGS_V2_SHA256)
    if d2.get('inherits') != 'A3_lead_rulings.json':
        sys.exit('REFUSED: A3_lead_rulings_v2.json does not inherit A3_lead_rulings.json')
    return {'sha256': got, 'sha256_v2': got2,
            'mng_gate': d['OC-A3-1_gate_unknown']['mng_gate'] is True,            # OC-A3-1
            'D_unknown': d['OC-A3-2_D_unknown']['D_unknown_score'],                 # OC-A3-2
            'E_unknown': d['OC-A3-3_E_unknown']['E_component_unknown_score'],       # OC-A3-3
            'jump_transfer': d['OC-A3-6_jump_transfer']['c4_jump_transfer_primary'] is True,   # OC-A3-6
            'C6_floor': d['OC-7_class_evidence']['c6_floor'],                       # OC-6 / OC-7
            'C1b_override': dict(d2['RR-01_C1b_all_unknown']['labels']),            # RR-01: {label: rating}
            'C6_cap_labels': tuple(RR03_CAP_LABELS) if d2['RR-03_C6_cap_unverified']['cap_labels'] else (),   # RR-03
            'topstep_R_by_size': d2['RR-04_topstep_R_micro']['R_by_size'] is True,  # RR-04
            'lucid_fee_u_rule': d2['RR-05_lucid_fee']['lucid_fee_u_rule'] is True}  # RR-05


def variant_params(name, rulings):
    """Parameters for a variant: the primary is the rulings; each variant flips exactly one of them (or one reading)."""
    prm = {'mng_gate': rulings['mng_gate'], 'D_unknown': rulings['D_unknown'], 'E_unknown': rulings['E_unknown'],
           'jump_transfer': rulings['jump_transfer'], 'C6_floor': rulings['C6_floor'], 'c4_conservative': False,
           'oc1_off': False, 'data_variant': None, 'C1b_override': rulings['C1b_override'],
           'C6_cap_labels': rulings['C6_cap_labels'], 'topstep_R_by_size': rulings['topstep_R_by_size'],
           'lucid_fee_u_rule': rulings['lucid_fee_u_rule']}
    if name == 'v1_rulings_only':       # the four v2 rulings (RR-01, RR-03, RR-04, RR-05) off: reproduces the v1 table
        prm.update(C1b_override={}, C6_cap_labels=(), topstep_R_by_size=False, lucid_fee_u_rule=False)
    elif name == 'D_unknown_0':
        prm['D_unknown'] = 0
    elif name == 'E_unknown_0':
        prm['E_unknown'] = 0
    elif name == 'C4_no_transfer':
        prm['jump_transfer'] = False
    elif name == 'C6_as_rated':
        prm['C6_floor'] = None
    elif name == 'C4_conservative':
        prm['c4_conservative'] = True
    elif name == 'OC1_off':
        prm['oc1_off'] = True
        prm['data_variant'] = 'OC1_off'
    elif name in ('QV_proxy_only', 'OC2_published'):
        prm['data_variant'] = name
    return prm


def apply_variant(facts, name, prm=None):
    """Return a per-candidate fact view. `name` is a data variant (OC1_off, QV_proxy_only, OC2_published) or None;
    `prm` carries the ruling parameters (jump transfer, MNG gate)."""
    prm = prm or {'jump_transfer': False, 'mng_gate': False}
    cands = {c: dict(r) for c, r in facts['candidates'].items()}
    var = facts.get('variants', {})
    if prm.get('jump_transfer'):     # ruling OC-A3-6: sibling big-move counts apply to the OC-1 codes in every variant
        for c, v in var.get('C4_jump_transfer', {}).items():
            cands[c]['C4'] = dict(cands[c]['C4'], **v)
    if prm.get('mng_gate') and 'MNG' in cands:   # ruling OC-A3-1
        g = cands['MNG']['gate_60_dates']
        cands['MNG']['gate_60_dates'] = dict(g, value=True, flags=sorted(set((g.get('flags') or []) + ['lead_ruling_OC-A3-1'])),
                                             provenance=str(g.get('provenance')) + ' | lead ruling OC-A3-1: passes by inference')
    if name == 'OC1_off':
        for c, v in var.get('OC1_off', {}).items():
            cands[c].update(v)
    elif name == 'OC2_published':
        for c, v in var.get('OC2_published', {}).items():
            cands[c]['ADV'] = v['ADV']
    elif name == 'QV_proxy_only':
        for c, r in cands.items():
            q = r['QV_or_r']
            if q.get('value') is not None and 'proxy' not in q.get('flags', []):
                sig = val(r['sigma_1m'])
                cands[c]['QV_or_r'] = {'value': 1.0 / sig, 'flags': ['proxy'], 'u': False,
                                       'provenance': '1 / sigma_1m (QV_proxy_only variant)'}
    return cands


def score_layer1(cands, blind_c, c4_conservative=False, c6_floor=None, c1b_override=None, c6_cap_labels=()):
    out = {}
    for code in CANDIDATES:
        r = cands[code]
        b = blind_c.get(code, {})
        u = []
        q = r['QV_or_r']
        is_proxy = 'proxy' in (q.get('flags') or [])
        qv = None if is_proxy else val(q)
        rr = val(q) if is_proxy else None
        if val(q) is None:
            u.append('C2')
        c2 = c2_score(qv=qv, r=rr)
        adv = val(r['ADV'])
        if adv is None:
            u.append('C3')
        c3 = c3_score(adv, val(r['spread_ratio_overnight_main']))
        items = []
        for k, cell in r['C4'].items():
            v = cell.get('value')
            if c4_conservative and 'ambiguous' in (cell.get('flags') or []):
                v = True
            if v == 'unknown':
                u.append(f'C4:{k}')
            items.append(v)
        c4 = c4_score(items)
        sig = val(r['sigma_1m'])
        if sig is None:
            u.append('C5')
        c5 = c5_score(sig)
        c1 = c6 = c6_rated = None
        if b:
            if b.get('C1a') in (None, 'unknown') or b.get('C1b') in (None, 'unknown'):
                u.append('C1')
            c1b = b.get('C1b')
            if (c1b_override or {}).get(b.get('label')) is not None:
                c1b = c1b_override[b['label']]     # ruling RR-01: every C1(b) field unknown -> high (spec: 'Unknown counts as high')
                u.append('C1b:RR-01')
            c1 = c1_score(b.get('C1a'), c1b)
            c6 = b.get('C6')
            c6_rated = c6
            if c6 is not None and c6_floor is not None and c6 < c6_floor:
                c6 = c6_floor            # rulings OC-6 / OC-7: every C6 below the floor takes the floor (C25's 0 included)
            if c6 is not None and b.get('label') in c6_cap_labels and c6 > C6_UNVERIFIED_CAP:
                c6 = C6_UNVERIFIED_CAP   # ruling RR-03: C6 >= 3 resting only on an abstract is capped at 2
        scores = {'C1': c1, 'C2': c2, 'C3': c3, 'C4': c4, 'C5': c5, 'C6': c6}
        complete = all(v is not None for v in scores.values())
        l1 = l1_value(scores) if complete else None
        gate60 = val(r['gate_60_dates'])
        if complete:
            ok, reasons = l1_gate(l1, scores, gate60)
        else:
            ok, reasons = None, ['pending: blind ratings for C1/C6']
        flags = sorted(set(f for k in ('sigma_1m', 'R_d', 'QV_or_r', 'ADV') for f in (r[k].get('flags') or [])))
        out[code] = {'code': code, 'family': r['family'], **scores, 'L1': l1, 'u': u, 'gate60': gate60,
                     'L1_gate_pass': ok, 'L1_gate_reasons': reasons, 'fact_flags': flags, 'C6_rated': c6_rated,
                     'sigma_1m': sig, 'R_d': val(r['R_d']), 'ADV': adv, 'QV_or_r': val(q), 'QV_is_proxy': is_proxy}
    return out


def score_layer2(cands, l1, fp, econ, blind_f, oc1_off=False, d_unknown=1, e_unknown=1, r_by_size=False,
                 lucid_u_fee=None):
    pairs = []
    for p in fp['pairs']:
        firm, code = p['firm'], p['code']
        if p['listed_50k']['value'] != 'yes':
            continue
        fo = fp['firms'][firm]
        r = cands[code]
        u = []
        e = econ.get((firm, code), {})
        mu_lim, mu_mkt, mu10 = e.get('mu_star_lim'), e.get('mu_star_mkt'), e.get('mu10K')
        if oc1_off and val(cands[code]['sigma_1m']) is None:
            mu_lim = mu_mkt = mu10 = None    # sigma_T unknown under the spec's literal defaults: mu unknown
        if not econ:
            E = None                         # no econ file yet: pending
        else:
            E = e_score(mu_lim, mu_mkt, mu10, unknown=e_unknown)   # ruling OC-A3-3: unknown component scores 1
            if mu_lim is None or mu_mkt is None or mu10 is None:
                u.append('E')                # some mu unknown (no econ row, or no sigma_1m): flagged u
        mll = val(fo['MLL_usd'])
        rd, tv = val(r['R_d']), val(r['tick_value'])
        room = mll / (rd * tv) if (mll and rd and tv) else None
        if room is None:
            u.append('D')
        D = d_score(room, unknown=d_unknown)     # ruling OC-A3-2: unknown R_d scores 1
        bf = blind_f.get(firm)
        R = A = F = Rel = None
        if bf:
            R = r_for(bf.get('R'), CLASS_OF[code])
            if r_by_size:                # ruling RR-04: the scorer's R_by_size reading (micro 4, non-micro 3 at Topstep)
                rs = r_by_size_for(bf, code, CLASS_OF[code])
                R = R if rs is None else rs
            A = None if bf.get('A') is None else int(bf['A'])
            F = None if bf.get('F') is None else int(bf['F'])
            Rel = bf.get('Rel')
        P = p_score([c.get('value') for c in fo['P_items'].values()])
        fee_reading = 'sourced'
        if lucid_u_fee is not None and firm == 'lucid':     # ruling RR-05: Lucid's all-in fee is unknown (u-rule)
            u.append('fee')
            fee_reading = lucid_u_fee['reading'].get(code, 'u: E from A3_econ unchanged (not rerun at the u fee)')
        scores = {'E': E, 'D': D, 'R': R, 'A': A, 'F': F, 'P': P, 'Rel': Rel}
        complete = all(v is not None for v in scores.values())
        L2 = l2_value(scores) if complete else None
        gate_reasons = []
        if fo['bc_eligible']['value'] is not True:
            gate_reasons.append('BC residents not accepted or unknown')
        if A == 0:
            gate_reasons.append('A = 0')
        l1r = l1[code]
        S = 0.5 * l1r['L1'] + 0.5 * L2 if (complete and l1r['L1'] is not None) else None
        econ_room = e.get('room')
        pairs.append({'firm': firm, 'code': code, **scores, 'L2': L2, 'L1': l1r['L1'], 'S': S, 'u': u,
                      'mu_star_lim': mu_lim, 'mu_star_mkt': mu_mkt, 'mu10K': mu10,
                      'cost_per_attempt_usd': e.get('cost_per_attempt_usd'), 'room': room, 'fee_reading': fee_reading,
                      'fee_rt_usd_u_rule': (lucid_u_fee or {}).get('fee', {}).get(code) if firm == 'lucid' else None,
                      'room_econ': econ_room, 'MLL_usd': mll,
                      'L1_gate_pass': l1r['L1_gate_pass'], 'L2_gate_reasons': gate_reasons,
                      'eligible_for_rank': bool(l1r['L1_gate_pass']) and not gate_reasons and S is not None})
    ranked = sorted([p for p in pairs if p['eligible_for_rank']], key=rank_key)
    for i, p in enumerate(ranked):
        p['rank'] = i + 1
        p['S_rounded'] = round2(p['S'])
    return pairs, ranked


def lucid_u_rule(econ_raw):
    """Ruling RR-05. For each Lucid pair: the u-rule fee (the highest fee found for that code at the other four firms,
    from A3_econ.json), and, where the reviewer's rerun (rr_econ_lucidalt.json) has the pair, its recomputed economics.
    Returns {'fee': {code: usd}, 'reading': {code: text}, 'econ': {(lucid, code): econ row}, 'sha256': ...}."""
    rows = (econ_raw or {}).get('pairs') or []
    fee = {}
    for r in rows:
        if r['firm'] != 'lucid' and r.get('F_rt_usd') is not None:
            fee[r['code']] = max(fee.get(r['code'], 0.0), float(r['F_rt_usd']))
    lucid_codes = sorted({r['code'] for r in rows if r['firm'] == 'lucid'})
    fee = {c: fee.get(c) for c in lucid_codes}
    path = os.path.join(BR, LUCID_ALT_FILE)
    if not os.path.exists(path):
        sys.exit(f'REFUSED: {LUCID_ALT_FILE} missing')
    with open(path, 'rb') as fh:
        raw = fh.read()
    alt = read_econ({'pairs': json.loads(raw)['rows']})
    reading = {}
    for c in lucid_codes:
        if ('lucid', c) in alt:
            reading[c] = f'u: fee {fee[c]:.2f} RT (highest at the other firms); economics rerun by the reviewer'
        else:
            reading[c] = (f"u: fee {fee[c]:.2f} RT (highest at the other firms)" if fee[c] is not None else 'u: no other-firm fee') + \
                '; E from A3_econ unchanged (not rerun)'
    return {'fee': fee, 'reading': reading, 'econ': alt, 'sha256': hashlib.sha256(raw).hexdigest()}


def run_variant(name, facts, fp, econ, blind_c, blind_f, rulings=None, econ_raw=None):
    prm = variant_params(name, rulings or load_rulings())
    cands = apply_variant(facts, prm['data_variant'], prm)
    l1 = score_layer1(cands, blind_c, c4_conservative=prm['c4_conservative'], c6_floor=prm['C6_floor'],
                      c1b_override=prm['C1b_override'], c6_cap_labels=prm['C6_cap_labels'])
    lucid_u_fee, econ_v = None, econ
    if prm['lucid_fee_u_rule']:
        lucid_u_fee = lucid_u_rule(econ_raw)
        econ_v = {**econ, **{k: {**econ[k], **{f: v[f] for f in ('mu_star_lim', 'mu_star_mkt', 'mu10K', 'cost_per_attempt_usd')}}
                             for k, v in lucid_u_fee['econ'].items() if k in econ}}
    pairs, ranked = score_layer2(cands, l1, fp, econ_v, blind_f, oc1_off=prm['oc1_off'], d_unknown=prm['D_unknown'],
                                 e_unknown=prm['E_unknown'], r_by_size=prm['topstep_R_by_size'], lucid_u_fee=lucid_u_fee)
    return l1, pairs, ranked


def sanitize(o):
    if isinstance(o, float) and math.isinf(o):
        return '> 4'
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    return o


def fmt(x, nd=2):
    if x is None:
        return '-'
    if x == INF:
        return '> 4'
    if isinstance(x, float):
        return f'{x:.{nd}f}'
    return str(x)


def write_md(res, status, path):
    prim = res['variants']['primary']
    L = [f'# Stage E.28 Part A ranking table (score.py)', '',
         f'Status: **{status}**. Spec sha256 {SPEC_SHA256} (checked). Generated by '
         'reports/stage_e28_briefs/work/A3_facts/score.py from A3_facts.json, A3_firm_products.json, '
         'A3_blind_ratings.json, A3_econ.json. Every score is computed from unrounded criterion scores; "u" lists criteria '
         'or C4 items that took the spec\'s unknown default. Inputs present: ' + ', '.join(f'{k}: {v}' for k, v in res['inputs'].items()), '',
         '## Layer 1 (all candidates)', '',
         '| Code | Family | C1 | C2 | C3 | C4 | C5 | C6 | L1 | Gate | u | Fact flags |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for c in CANDIDATES:
        r = prim['layer1'][c]
        gate = 'pending' if r['L1_gate_pass'] is None else ('pass' if r['L1_gate_pass'] else 'FAIL: ' + '; '.join(r['L1_gate_reasons']))
        L.append(f"| {c} | {r['family']} | {fmt(r['C1'])} | {r['C2']} | {r['C3']} | {r['C4']} | {r['C5']} | {fmt(r['C6'])}{' (rated ' + str(r['C6_rated']) + ')' if r['C6_rated'] != r['C6'] else ''} | "
                 f"{fmt(r['L1'], 3)} | {gate} | {', '.join(r['u'])} | {', '.join(r['fact_flags'])} |")
    L += ['', '## Layer 2 and pair score (listed pairs)', '',
          '| Rank | Firm | Code | E | D | R | A | F | P | Rel | L2 | L1 | S | mu*_lim | mu*_mkt | mu10K | cost/attempt | room | gates | u |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    order = sorted(prim['pairs'], key=lambda p: (p.get('rank') or 10**6, p['code'], p['firm']))
    for p in order:
        g = []
        if p['L1_gate_pass'] is False:
            g.append('L1 gate fails')
        g += p['L2_gate_reasons']
        L.append(f"| {p.get('rank', '-')} | {p['firm']} | {p['code']} | {fmt(p['E'])} | {p['D']} | {fmt(p['R'])} | {fmt(p['A'])} | "
                 f"{fmt(p['F'])} | {p['P']} | {fmt(p['Rel'])} | {fmt(p['L2'], 3)} | {fmt(p['L1'], 3)} | {fmt(p['S'], 3)} | "
                 f"{fmt(p['mu_star_lim'])} | {fmt(p['mu_star_mkt'])} | {fmt(p['mu10K'])} | {fmt(p['cost_per_attempt_usd'])} | "
                 f"{fmt(p['room'])} | {'; '.join(g) or 'ok'} | {', '.join(p['u'])} |")
    ties = find_ties(prim['ranked'])
    L += ['', f'## Ties in the primary ranking (equal S at 2 decimals, half-up): {len(ties)} group(s)', '']
    for t in ties:
        L.append(f"- S {t['S_rounded']:.2f}, ranks {t['ranks'][0]}-{t['ranks'][-1]}: " +
                 '; '.join(f"{x['higher']} over {x['lower']} by {x['decided_by']}" for x in t['steps']))
    if not ties:
        L.append('- none')
    L += ['', '## Top 5 and the MNQ baseline, by variant', '']
    for name, v in res['variants'].items():
        top = ', '.join(f"{p['rank']}. {p['firm']} {p['code']} (S {p['S']:.3f})" for p in v['ranked'][:5]) or 'none ranked'
        mnq = [f"{p['firm']} rank {p.get('rank', '-')}" for p in v['pairs'] if p['code'] == 'MNQ']
        L.append(f"- **{name}**: {top}. MNQ: {', '.join(mnq) or 'no pair'}. Layer 1 survivors: "
                 f"{sum(1 for r in v['layer1'].values() if r['L1_gate_pass'])}.")
    lp = [p for p in prim['pairs'] if p['firm'] == 'lucid']
    L += ['', '## Lucid fee reading (ruling RR-05: the all-in fee is unknown, so the spec u-rule applies)', '',
          '| Code | Fee used (RT, USD, u-rule) | Reading | Rank |', '|---|---|---|---|']
    for p in sorted(lp, key=lambda q: q['code']):
        L.append(f"| {p['code']} | {fmt(p['fee_rt_usd_u_rule'])} | {p['fee_reading']} | {p.get('rank', '-')} |")
    L += ['', 'Primary = OC-1 on, OC-2 as decided, and the lead rulings of A3_lead_rulings.json (sha256 ' + res['rulings']['sha256'] +
          ') plus A3_lead_rulings_v2.json (sha256 ' + res['rulings']['sha256_v2'] + '): RR-01 C40 C1(b) = high (every C1(b) field '
          'unknown, spec: unknown counts as high); RR-03 the 13 grain C6 = 3 ratings resting on an abstract are capped at 2; '
          'RR-04 Topstep R from the blind R_by_size (micro 4, non-micro 3); RR-05 Lucid fees by the u-rule (rerun economics '
          'where rr_econ_lucidalt.json has the pair, A3_econ unchanged elsewhere, flagged u). The v1 rulings: MNG passes the 60-date gate (OC-A3-1); D with unknown R_d scores 1 (OC-A3-2); each E component with unknown mu '
          'scores 1 (OC-A3-3); C4 jump-transfer reading primary (OC-A3-6); C6 floor of 2 for every contract rated below 2, '
          'which replaces C25\'s 0 (OC-6, OC-7). Variants, each flipping one thing against the primary: OC1_off (the spec\'s '
          'literal unknown defaults for sigma_1m, R_d and the r proxy of codes without owned bars; their mu values are unknown, '
          'E = 1 by the ruling, flagged); C4_conservative (reader-flagged ambiguous C4 items counted as holding); QV_proxy_only '
          '(proxy r for every code); OC2_published (published all-expiry ADV for owned roots); D_unknown_0 (unknown D scores 0); '
          'E_unknown_0 (unknown E components score 0); C4_no_transfer (the old reading: no sibling big-move counts); '
          'C6_as_rated (no C6 floor, C25 = 0); v1_rulings_only (the four v2 rulings off, reproduces the v1 table; the other '
          'variants sit on the new primary). The old C4_jump_transfer variant is now the primary. The v1 table is kept in '
          'A3_ranking_table_v1.json and .md.', '']
    with open(path, 'w') as fh:
        fh.write('\n'.join(L))


def main():
    got = spec_sha256()
    if got != SPEC_SHA256:
        sys.exit(f'REFUSED: spec sha256 {got} differs from the frozen {SPEC_SHA256}')
    facts, fp = load_json('A3_facts.json'), load_json('A3_firm_products.json')
    if facts is None or fp is None:
        sys.exit('REFUSED: A3_facts.json or A3_firm_products.json missing')
    rulings = load_rulings()
    blind, econ_raw, key = load_json('A3_blind_ratings.json'), load_json('A3_econ.json'), load_json('A3_mask_key.json')
    econ = read_econ(econ_raw)
    blind_c, blind_f = read_blind(blind, key)
    inputs = {'A3_blind_ratings.json': 'yes' if blind else 'MISSING', 'A3_econ.json': f'yes ({len(econ)} pairs)' if econ_raw else 'MISSING',
              'A3_mask_key.json': 'yes' if key else 'MISSING'}
    status = 'COMPLETE' if (blind and econ_raw and key) else 'INCOMPLETE (missing inputs: nothing ranked)'
    res = {'spec_sha256': got, 'rulings': {**rulings, 'lucid_alt_econ_sha256': lucid_u_rule(econ_raw)['sha256']}, 'status': status, 'inputs': inputs, 'variants': {}}
    for name in VARIANT_NAMES:
        l1, pairs, ranked = run_variant(name, facts, fp, econ, blind_c, blind_f, rulings, econ_raw)
        res['variants'][name] = {'layer1': l1, 'pairs': pairs, 'ranked': ranked}
    res['variants']['primary']['ties'] = find_ties(res['variants']['primary']['ranked'])
    with open(os.path.join(BR, 'A3_ranking_table.json'), 'w') as fh:
        json.dump(sanitize(res), fh, indent=1, allow_nan=False)
    write_md(res, status, os.path.join(BR, 'A3_ranking_table.md'))
    prim = res['variants']['primary']
    print(status, '| L1 survivors', sum(1 for r in prim['layer1'].values() if r['L1_gate_pass']),
          '| listed pairs', len(prim['pairs']), '| ranked', len(prim['ranked']))


if __name__ == '__main__':
    main()
