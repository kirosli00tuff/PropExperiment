"""RV1 independent recomputation of Stage E.32b Step 4 (spec sections 0-6).

Written by RankingReviewer-FableXHigh from the frozen spec text only (not from the
ScoreCoder's modules). Exact arithmetic: JSON floats parsed as Fractions.
Usage: python3 -I recompute.py [--variant NAME] [--params JSON] [--patches JSON-file ruling-name]
Prints a comparison against score32b_out.json.
"""
import json, sys, copy, math
from fractions import Fraction as F

B = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs'
SPEC_SHA = '09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635'

FAMILIES = {
    'crude': ['MCL', 'QM', 'CL'], 'natgas': ['MNG', 'QG', 'NG'],
    'metals': ['MGC', 'GC', 'SIL', 'SI', 'MHG', 'HG'], 'fx': ['M6E', '6E', 'M6A', '6A'],
    'crypto': ['MET', 'ETH', 'MBT', 'BTC'], 'equity': ['M2K', 'RTY', 'MYM', 'YM', 'MNQ', 'NQ'],
    'rates': ['2YY', '5YY', '10Y', '30Y', 'ZT', 'ZF', 'ZN', 'ZB'],
    'grains': ['MZC', 'MZS', 'MZW', 'MZL', 'MZM', 'XC', 'XK', 'XW', 'ZC', 'ZS', 'ZW', 'ZL', 'ZM'],
}
FAM_OF = {c: f for f, cs in FAMILIES.items() for c in cs}
FIRMS = ['topstep', 'lucid', 'tradeify', 'mffu', 'bulenox']
# spec 2.4: same-price groups (price transfer allowed) -> used only to borrow a median close
SAME_PRICE = [['MNQ', 'NQ'], ['M2K', 'RTY'], ['MYM', 'YM'], ['QM', 'MCL', 'CL'], ['QG', 'MNG', 'NG'],
              ['M6E', '6E'], ['M6A', '6A'], ['BTC', 'MBT'], ['MZC', 'XC', 'ZC'], ['MZS', 'XK', 'ZS'],
              ['MZW', 'XW', 'ZW'], ['MZL', 'ZL'], ['MZM', 'ZM']]
# contract size (multiplier) ordering for "larger-size sibling" when ratio unknown
W_L1 = {'D1': F('0.30'), 'D2': F('0.15'), 'D3': F('0.15'), 'D4': F('0.15'), 'D5': F('0.10'), 'D6': F('0.15')}
W_L2 = {'E': F('0.40'), 'R': F('0.15'), 'A': F('0.15'), 'D': F('0.15'), 'Rel': F('0.10'), 'P': F('0.05')}


def load(p):
    with open(p) as fh:
        return json.load(fh, parse_float=F)


def num(x):
    if x is None:
        return None
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, F)):
        return F(x)
    if isinstance(x, str):
        try:
            return F(x)
        except Exception:
            return None
    return None


def round2_half_up(x):
    # half-up at 2 decimals on an exact Fraction
    return math.floor(x * 100 + F(1, 2)) / F(100)


def d1_band(r):
    if r <= F('0.025'):
        return 4
    if r <= F('0.05'):
        return 3
    if r <= F('0.10'):
        return 2
    if r <= F('0.20'):
        return 1
    return 0


def room_band(x):
    if x is None:
        return 1  # unknown sigma_240 or R_d: band 1
    if x >= 4:
        return 4
    if x >= 3:
        return 3
    if x >= 2:
        return 2
    if x >= 1:
        return 1
    return 0


def s_of(x, x0):
    return 4 * max(F(0), 1 - x / x0)


def blind_val(block, key, unk_default):
    r = block.get(key) if block else None
    if not r or r.get('unknown') or r.get('value') is None:
        return F(unk_default), True
    return F(r['value']), False


def apply_patches(inputs, patches):
    inputs = copy.deepcopy(inputs)
    for p in patches:
        tgt = inputs[p['file']]
        for k in p['path'][:-1]:
            tgt = tgt.setdefault(k, {})
        v = p['value']
        # make numbers exact
        v = json.loads(json.dumps(v, default=lambda o: float(o)), parse_float=F) if not isinstance(v, F) else v
        tgt[p['path'][-1]] = v
    return inputs


def compute(inputs, params):
    f3 = inputs['F3']['roots']
    f4 = inputs['F4']
    blind = inputs['blind']
    econ = inputs['econ']['pairs']
    att = inputs['attention']['underlyings']
    slip = F(str(params.get('slip', '0.5')))
    disp = params.get('dispersion', 'sigma')  # 'sigma' or 'mad' (m)
    d1_all = params.get('d1_all', False)
    e_dir60 = params.get('e_dir60', False)
    oc1_off = params.get('oc1_off', False)
    sat_ded = F(params.get('sat_deduction', 2))
    d2_own = params.get('d2_own', False)
    l1min2 = params.get('l1min2', False)
    spread1 = params.get('spread1', False)

    codes = f4['codes']
    # --- F3 statistic access (OC1_off: OC1 codes have no statistics)
    def stat(code):
        r = f3.get(code)
        if not r or r.get('status') not in ('owned', 'OC1'):
            return None
        if oc1_off and r.get('status') == 'OC1':
            return None
        return r

    def disp_h(code, h):
        r = stat(code)
        if not r:
            return None
        if h == 'OC':
            blk = r.get('OC')
        else:
            blk = r.get('h', {}).get(str(h))
        if not blk:
            return None
        return num(blk.get('sigma' if disp == 'sigma' else 'm'))

    def median_close(code):
        r = stat(code)
        if r and r.get('median_close') is not None:
            return num(r['median_close'])
        # borrow a same-price sibling's close (ScoreCoder reading 4, LR-SC)
        for grp in SAME_PRICE:
            if code in grp:
                for s in grp:
                    rs = stat(s)
                    if rs and rs.get('median_close') is not None:
                        return num(rs['median_close'])
        return None

    def adv(code):
        return num(codes[code]['adv']['value'])

    def notional(code):
        a = adv(code); m = num(codes[code]['multiplier']); c = median_close(code)
        if a is None or m is None or c is None:
            return None
        return a * m * c

    # --- D2 d: attention terciles by underlying
    counts = {}
    code_under = {}
    for u, x in att.items():
        st = str(x.get('status'))
        cnt = x.get('count')
        for c in x.get('codes', []):
            assert c not in code_under, c
            code_under[c] = u
        if st in ('200', 'ok') and isinstance(cnt, int) and cnt >= 0:
            counts[u] = cnt
    n = len(counts)
    def d_of(code):
        u = code_under.get(code)
        if u is None or u not in counts:
            return F(1, 2), True
        k = sum(1 for v in counts.values() if v > counts[u])
        if k < F(n, 3):
            return F(1), False
        if k < F(2 * n, 3):
            return F(1, 2), False
        return F(0), False

    # --- leader and satellite
    def leader_of(code):
        sibs = codes[code].get('siblings') or []
        cand = [code] + list(sibs)
        nots = {c: notional(c) for c in cand}
        if all(v is not None for v in nots.values()):
            return max(cand, key=lambda c: nots[c]), 'computed'
        return codes[code].get('leader') or code, 'F4'

    def sat_i(code):
        """(i) a sibling has >= 5x the candidate's notional ADV; unknown ratio with a larger-size sibling: holds."""
        me = notional(code)
        best = None
        unknown_larger = False
        for s in codes[code].get('siblings') or []:
            ns = notional(s)
            # siblings share the underlying price: the notional ratio needs only ADV x multiplier
            a_me, a_s = adv(code), adv(s)
            m_me, m_s = num(codes[code]['multiplier']), num(codes[s]['multiplier'])
            if me is not None and ns is not None and me > 0:
                ratio = ns / me
                best = ratio if best is None or ratio > best else best
            elif a_me is not None and a_s is not None and m_me and m_s and a_me > 0:
                ratio = (a_s * m_s) / (a_me * m_me)
                best = ratio if best is None or ratio > best else best
            else:
                # ratio unknown: larger-size sibling? compare multiplier x close, or multiplier when same price
                ms = num(codes[s]['multiplier']); mm = num(codes[code]['multiplier'])
                cs = median_close(s); cm = median_close(code)
                if ms is not None and mm is not None and cs is not None and cm is not None:
                    larger = ms * cs > mm * cm
                elif ms is not None and mm is not None and any(code in g and s in g for g in SAME_PRICE):
                    larger = ms > mm
                else:
                    larger = True  # both unknown: counts as holding (ScoreCoder reading 5, accepted)
                if larger:
                    unknown_larger = True
        if best is not None and best >= 5:
            return True, best, False
        if unknown_larger:
            return True, best, True
        return False, best, False

    def sat_ii(code):
        so = codes[code].get('settles_off_sibling') or {}
        return bool(so.get('value')) and bool(so.get('item'))

    L1rows = {}
    for code in FAM_OF:
        x = codes[code]
        row = {'code': code, 'family': FAM_OF[code], 'u': [], 'notes': []}
        if x.get('excluded') or code == 'NQ':
            row['status'] = 'excluded (V49)'
        # S
        sp = x['spread_S']
        if spread1:
            S = F(1); S_sourced = False
        elif sp.get('sourced') and sp.get('value') is not None:
            S = num(sp['value']); S_sourced = True
        else:
            S = F(1); S_sourced = False; row['u'].append('S')
        row['S'] = S; row['S_sourced'] = S_sourced
        c_RT = S + slip
        row['c_RT'] = c_RT
        hs = ['5', '15', '30', '60', '120', '240', 'OC']
        row['disp'] = {h: disp_h(code, h) for h in hs}
        row['r'] = {h: (c_RT / row['disp'][h] if row['disp'][h] else None) for h in hs}
        d1_hs = hs if d1_all else ['30', '60', '120', '240']
        bands = {h: d1_band(row['r'][h]) for h in d1_hs if row['r'][h] is not None}
        row['D1_bands'] = bands
        d1_unknown = any(row['r'][h] is None for h in d1_hs)
        row['D1'] = (F(sum(bands.values()), len(bands)) if bands and not d1_unknown else None)
        # D4 pieces first (Sat decides D2/D6 facts_of)
        a_v = adv(code)
        L = 0
        if a_v is None:
            L = 1; row['u'].append('L adv')
        elif a_v < 1000:
            L = 2
        elif a_v < 10000:
            L = 1
        if sp.get('sourced') and sp.get('value') is not None and not spread1:
            sv = num(sp['value'])
            if sv > 2:
                L = max(L, 2)
            elif sv > 1:
                L = max(L, 1)
        tc = x.get('touch') or {}
        if tc.get('sourced') and tc.get('value') is not None:
            tv = num(tc['value'])
            if tv < 2:
                L = max(L, 2)
            elif tv < 5:
                L = max(L, 1)
        r3 = stat(code)
        tick_v = num(x.get('tick_value_usd'))
        rd_p99 = num(r3['R_d']['p99']) if r3 and r3.get('R_d') else None
        rd_med = num(r3['R_d']['median']) if r3 and r3.get('R_d') else None
        if rd_p99 is None or tick_v is None:
            J = 1; row['u'].append('J')
        else:
            J = 1 if rd_p99 * tick_v > 1000 else 0
        si, ratio, si_unknown = sat_i(code)
        sii = sat_ii(code)
        siii_v, siii_u = blind_val(blind['codes'].get(code), 'sat_iii', 0)
        if siii_u:
            row['u'].append('sat_iii')
        siii = siii_v == 1
        Sat = 1 if (si or sii or siii) else 0
        D4 = max(F(0), 4 - L - J - sat_ded * Sat)
        row.update(L=L, J=J, Sat=Sat, sat_i=si, sat_ii=sii, sat_iii=siii, sib_ratio=ratio, D4=D4)
        # leader
        lead, lead_basis = leader_of(code)
        row['leader'] = lead; row['leader_basis'] = lead_basis
        facts_of = lead if (Sat and (si or sii) and not d2_own) else code
        row['facts_of'] = facts_of
        # D2
        a, au = blind_val(blind['codes'].get(facts_of), 'D2a', 1)
        b, bu = blind_val(blind['codes'].get(facts_of), 'D2b', F(1, 2))
        if au: row['u'].append('D2a')
        if bu: row['u'].append('D2b')
        # c: largest notional in family (NQ included), among codes with a known notional
        fam = FAMILIES[FAM_OF[code]]
        nots = {c: notional(c) for c in fam}
        known = {c: v for c, v in nots.items() if v is not None}
        if nots.get(facts_of) is None:
            c = F(0); row['notes'].append('D2c: own/leader notional unknown -> 0 (provisional)')
        else:
            c = F(1) if nots[facts_of] == max(known.values()) else F(0)
            if len(known) < len(fam):
                row['notes'].append('D2c provisional: unknown notional for ' + ','.join(sorted(set(fam) - set(known))))
        d, du = d_of(code)
        if du: row['u'].append('D2d')
        D2 = max(F(0), 4 - a - b - c - d)
        row.update(D2=D2, D2_parts={'a': a, 'b': b, 'c': c, 'd': d})
        # D3
        bl = blind['codes'].get(code, {})
        s1, _ = blind_val(bl, 's1', 0); s2, _ = blind_val(bl, 's2', 0); s3, _ = blind_val(bl, 's3', 0)
        for k, v in (('s1', s1), ('s2', s2)):
            if v == 2 and bl.get(k, {}).get('unverified'):
                row['notes'].append(f'{k} capped 2->1 (unverified)')
        if bl.get('s1', {}).get('unverified') and s1 == 2: s1 = F(1)
        if bl.get('s2', {}).get('unverified') and s2 == 2: s2 = F(1)
        D3 = min(F(4), s1 + s2 + s3)
        row.update(D3=D3, D3_parts={'s1': s1, 's2': s2, 's3': s3})
        # D5
        da = x.get('data_access') or {}
        ms = da.get('mbo_start')
        if not ms:
            h5 = 1; row['u'].append('D5h')
        else:
            ms = str(ms)
            if len(ms) == 7: ms = ms + '-01'
            if ms <= '2017-06-30': h5 = 0
            elif ms <= '2020-12-31': h5 = 1
            else: h5 = 2
        kv = num(da.get('k_usd_month'))
        if kv is None or da.get('k_kind') == 'unknown':
            k5 = 1; row['u'].append('D5k')
        elif kv <= 10: k5 = 0
        elif kv <= 50: k5 = 1
        else: k5 = 2
        o = da.get('o_owned_36m')
        o5 = 0 if o is True else 1
        if o is None: row['u'].append('D5o')
        p = da.get('p_all_read')
        p5 = 1 if p is True else 0
        if p is None: row['u'].append('D5p')
        D5 = max(F(0), 4 - h5 - k5 - o5 - p5)
        row.update(D5=D5, D5_parts={'h': h5, 'k': k5, 'o': o5, 'p': p5})
        # D6: satellite (i)/(ii) takes leader's evidence (reading 3); D2_own does not change D6
        ev_of = lead if (Sat and (si or sii)) else code
        d6, d6u = blind_val(blind['codes'].get(ev_of), 'D6', 1)
        if d6u: row['u'].append('D6')
        if blind['codes'].get(ev_of, {}).get('D6', {}).get('unverified'):
            if d6 >= 3: d6 = F(2)
            if d6 == 0: d6 = F(1)
        row['D6'] = d6; row['evidence_of'] = ev_of
        # gate
        reasons = []
        sig60 = disp_h(code, '60')
        if D4 == 0: reasons.append('D4 = 0')
        if sig60 is None:
            reasons.append('sigma_60 unknown')
        elif sig60 < 2 * c_RT:
            reasons.append(f'sigma_60 = {float(sig60):.4g} ticks vs 2 x (S + {float(slip)}) = {float(2*c_RT):.4g} ticks')
        if sig60 is not None and d1_unknown:
            reasons.append('another D1 horizon sigma unknown (reading 6)')
        if row['D1'] is not None:
            L1 = sum(W_L1[k] * row[k] for k in W_L1)
        else:
            L1 = None
        row['L1'] = L1
        row['L1_below_2'] = (L1 is not None and L1 < 2)
        if l1min2 and L1 is not None and L1 < 2:
            reasons.append('L1 < 2.00 (L1min2)')
        row['gate_reasons'] = reasons
        row['gate_pass'] = (not reasons) and code != 'NQ'
        row['sigma_240'] = disp_h(code, '240') if disp == 'sigma' else (num(stat(code)['h']['240']['sigma']) if stat(code) else None)
        row['rd_med'] = rd_med
        L1rows[code] = row

    # --- Layer 2
    pairs = []
    firms = f4['firms']
    econ_block = 'E_dir60' if e_dir60 else ('spread1' if spread1 else 'primary')
    for key, pr in f4['pairs'].items():
        firm, code = key.split('|')
        l1 = L1rows[code]
        row = {'key': key, 'firm': firm, 'code': code, 'u': [], 'gate_reasons': []}
        fr = firms[firm]
        bp = blind['pairs'].get(key, {})
        if code == 'NQ':
            row['status'] = 'excluded (V49)'
        elif not l1['gate_pass']:
            row['status'] = 'Layer 1 gate'; row['gate_reasons'] = list(l1['gate_reasons'])
        # Layer 2 gates
        listed = pr.get('listed_50k')
        A, Au = blind_val(bp, 'A', 1)
        if Au: row['u'].append('A')
        R, Ru = blind_val(bp, 'R', 1)
        if Ru: row['u'].append('R')
        g2 = []
        if listed is not True: g2.append('not listed for 50K' if listed is False else 'listing unknown (excluded)')
        if A == 0: g2.append('A = 0')
        if fr.get('bc_accepts') is not True: g2.append('BC not accepted/unknown')
        if 'status' not in row and g2:
            row['status'] = 'Layer 2 gate'; row['gate_reasons'] = g2
        # E
        eb = econ.get(key, {}).get(econ_block)
        E = None; m_star = None; m10k = None; cpa = None
        if eb:
            above = eb.get('above_cap') or {}
            ms_ = num(eb.get('m_star')); m10_ = num(eb.get('m10K'))
            e1 = F(0) if above.get('mu_star') else (s_of(ms_, F('0.20')) if ms_ is not None else None)
            e2 = F(0) if above.get('mu10K') else (s_of(m10_, F('0.30')) if m10_ is not None else None)
            if e1 is not None and e2 is not None:
                E = F(3, 4) * e1 + F(1, 4) * e2
            m_star = math.inf if above.get('mu_star') else ms_
            m10k = m10_
            cpa = num(eb.get('cost_per_attempt'))
        row.update(E=E, m_star=m_star, m10K=m10k, cost_per_attempt=cpa)
        # D
        v = num(codes[code]['tick_value_usd'])
        dll = fr.get('dll_50k'); mll = num(fr.get('mll_50k'))
        dll_f = mll if dll == 'none' else num(dll)
        s240 = l1['sigma_240']; rdm = l1['rd_med']
        room_a = dll_f / (s240 * v) if (dll_f is not None and s240 and v) else None
        room_b = mll / (rdm * v) if (mll is not None and rdm and v) else None
        D = F(room_band(room_a) + room_band(room_b), 2)
        row.update(D=D, room_a=room_a, room_b=room_b)
        # Rel
        bf = blind['firms'].get(firm, {})
        ded = 0
        for k, dflt in (('rel_age', 0), ('rel_payout', 0), ('rel_rules', 0), ('rel_regulatory', 0)):
            val, unk = blind_val(bf, k, dflt)
            ded += val
        Rel = 4 - ded
        # P
        pi = fr.get('p_inputs') or {}
        pd = 0
        if pi.get('native_api') is not True: pd += 1
        if pi.get('oco_api') is not True: pd += 1
        vps = pi.get('vps_chicago')
        if not (vps == 'allowed' or vps is True): pd += 1
        rl = pi.get('api_rate_limit_per_s')
        if rl == 'no_limit':
            pass
        else:
            rln = num(rl)
            if rln is None or rln < 10: pd += 1
        P = 4 - pd
        row.update(R=R, A=A, Rel=Rel, P=P)
        if E is not None:
            L2 = W_L2['E'] * E + W_L2['R'] * R + W_L2['A'] * A + W_L2['D'] * D + W_L2['Rel'] * Rel + W_L2['P'] * P
        else:
            L2 = None
        row['L1'] = l1['L1']; row['L2'] = L2
        if 'status' not in row:
            if E is None:
                row['status'] = 'NO ECON BLOCK'
            else:
                row['status'] = 'ranked'
        row['S'] = (l1['L1'] + L2) / 2 if (L2 is not None and l1['L1'] is not None) else None
        row['S_rounded'] = round2_half_up(row['S']) if row['S'] is not None else None
        pairs.append(row)

    ranked = [p for p in pairs if p['status'] == 'ranked']
    def key_fn(p):
        ms = p['m_star']
        ms_key = F(10**9) if ms == math.inf else ms
        return (-p['S_rounded'], ms_key, -p['L1'], p['cost_per_attempt'], p['code'], p['firm'])
    ranked.sort(key=key_fn)
    for i, p in enumerate(ranked, 1):
        p['rank'] = i
    # also the unrounded order for comparison
    unr = sorted(ranked, key=lambda p: -p['S'])
    return L1rows, pairs, ranked, unr


def fmt(x):
    if x is None: return 'None'
    if x == math.inf: return 'inf'
    if isinstance(x, F): return f'{float(x):.6g}'
    return str(x)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', default='primary')
    ap.add_argument('--params', default='{}')
    ap.add_argument('--ruling', default=None)
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()
    inputs = {
        'F3': load(f'{B}/F3_vol.json'), 'F4': load(f'{B}/F4_facts_unmasked.json'),
        'blind': load(f'{B}/F4_blind_unmasked.json'), 'econ': load(f'{B}/econ32b.json'),
        'attention': load(f'{B}/work/F5run/F2_attention_listcodes.json'),
        'data_access': load(f'{B}/F2_data_access.json'),
    }
    for k in ('F3', 'F4', 'blind', 'econ'):
        assert inputs[k]['spec_sha256'] == SPEC_SHA, k
    params = json.loads(args.params)
    declared = {
        'slip0': {'slip': '0'}, 'slip1': {'slip': '1.0'}, 'mad': {'dispersion': 'mad'},
        'D1_all': {'d1_all': True}, 'E_dir60': {'e_dir60': True}, 'OC1_off': {'oc1_off': True},
        'sat1': {'sat_deduction': 1}, 'D2_own': {'d2_own': True}, 'L1min2': {'l1min2': True},
        'spread1': {'spread1': True}, 'primary': {},
    }
    if args.variant in declared:
        params = {**declared[args.variant], **params}
    elif args.ruling or args.variant:
        lv = load(f'{B}/work/score/lead_variants.json')
        rl = [r for r in lv['rulings'] if r['name'] == (args.ruling or args.variant)]
        assert rl, 'no such ruling'
        params = {**rl[0].get('params', {}), **params}
        inputs = apply_patches(inputs, rl[0]['patches'])
    L1rows, pairs, ranked, unr = compute(inputs, params)
    out = load(f'{B}/score32b_out.json')
    if args.variant == 'primary':
        ref_pairs = {p['key']: p for p in out['primary']['pairs']}
        ref_l1 = out['primary']['layer1']
    else:
        ref = out['variants'][args.variant]
        ref_pairs = None; ref_l1 = None
    # ---- compare
    mism = []
    if ref_l1:
        for code, r in L1rows.items():
            o = ref_l1[code]
            if o.get('status','').startswith('excluded') or 'D4_parts' not in o:
                continue
            for k in ('D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'L1', 'S', 'c_RT'):
                mine = r[k]; theirs = o.get(k)
                if (mine is None) != (theirs is None) or (mine is not None and abs(float(mine) - float(theirs)) > 1e-9):
                    mism.append((code, k, fmt(mine), theirs))
            if bool(r['gate_pass']) != bool(o['gate_pass']) and code != 'NQ':
                mism.append((code, 'gate_pass', r['gate_pass'], o['gate_pass'], r['gate_reasons'], o['gate_reasons']))
            for k, ok in (('L', 'L'), ('J', 'J'), ('Sat', 'Sat')):
                if int(r[k]) != int(o['D4_parts'][ok]):
                    mism.append((code, 'D4.' + k, r[k], o['D4_parts'][ok]))
            for k in ('a', 'b', 'c', 'd'):
                if float(r['D2_parts'][k]) != float(o['D2_parts'][k]):
                    mism.append((code, 'D2.' + k, fmt(r['D2_parts'][k]), o['D2_parts'][k]))
            for k in ('h', 'k', 'o', 'p'):
                if int(r['D5_parts'][k]) != int(o['D5_parts'][k]):
                    mism.append((code, 'D5.' + k, r['D5_parts'][k], o['D5_parts'][k]))
            if r['facts_of'] != o['D2_parts']['facts_of']:
                mism.append((code, 'facts_of', r['facts_of'], o['D2_parts']['facts_of']))
            if r['evidence_of'] != o['D6_parts']['evidence_of']:
                mism.append((code, 'evidence_of', r['evidence_of'], o['D6_parts']['evidence_of']))
        for p in pairs:
            o = ref_pairs[p['key']]
            if p['status'] != o['status']:
                mism.append((p['key'], 'status', p['status'], o['status']))
            for k in ('E', 'R', 'A', 'D', 'Rel', 'P', 'L2', 'S', 'room_a', 'room_b', 'cost_per_attempt'):
                mine = p.get(k); theirs = o.get(k)
                if (mine is None) != (theirs is None) or (mine is not None and theirs is not None and abs(float(mine) - float(theirs)) > 1e-9):
                    mism.append((p['key'], k, fmt(mine), theirs))
            if p['status'] == 'ranked' and p['rank'] != o['rank']:
                mism.append((p['key'], 'rank', p['rank'], o['rank']))
        print(f'PRIMARY: {len(mism)} mismatches; ranked {len(ranked)} vs {out["primary"]["n_ranked"]}')
        for m in mism[:80]:
            print('  MISMATCH', m)
        # unrounded vs rounded-tie order
        diffs = [(a['key'], a['rank'], i + 1) for i, a in enumerate(unr) if a['rank'] != i + 1]
        print('ranks where the unrounded-S order differs from the spec order:', diffs)
        surv = sorted(c for c, r in L1rows.items() if r['gate_pass'])
        print('survivors equal:', surv == out['primary']['layer1_survivors'], len(surv))
        below = sorted(c for c, r in L1rows.items() if r['L1_below_2'])
        print('L1_below_2 equal:', below == out['primary']['L1_below_2'], below)
        mnq = {p['firm']: p['rank'] for p in ranked if p['code'] == 'MNQ'}
        print('MNQ ranks', mnq, 'ref', out['primary']['MNQ_ranks'])
    else:
        top5 = [(p['firm'], p['code'], fmt(p['S']), fmt(p['S_rounded'])) for p in ranked[:5]]
        print(f'VARIANT {args.variant}: params {params}')
        print(' mine top5:', top5)
        print(' ref  top5:', [(t['firm'], t['code'], round(float(t['S']), 6)) for t in ref['top5']])
        mnq = {p['firm']: p['rank'] for p in ranked if p['code'] == 'MNQ'}
        print(' MNQ ranks', mnq, 'ref', ref['MNQ_ranks'])
        surv = sorted(c for c, r in L1rows.items() if r['gate_pass'])
        print(' n_ranked', len(ranked), 'ref', ref['n_ranked'], '| survivors equal', surv == ref['layer1_survivors'])
        if 'ranks' in ref or 'pairs' in ref:
            pass
    # dump my full tables for the record
    tag = args.variant
    with open(f'{B}/work/rv1/recomp_{tag}.json', 'w') as fh:
        json.dump({'params': {k: str(v) for k, v in params.items()},
                   'layer1': {c: {k: (fmt(v) if not isinstance(v, (dict, list, str, bool)) else v) for k, v in r.items() if k not in ('disp', 'r')} for c, r in L1rows.items()},
                   'ranked': [{k: (fmt(v) if not isinstance(v, (dict, list, str, bool, int)) else v) for k, v in p.items()} for p in ranked]}, fh, indent=1, default=str)


if __name__ == '__main__':
    main()
