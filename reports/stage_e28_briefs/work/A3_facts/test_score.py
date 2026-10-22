"""Unit tests for score.py: every anchor function at its boundaries, the tie rule and the input readers.
Run: pytest -q reports/stage_e28_briefs/work/A3_facts/test_score.py
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score as S  # noqa: E402
from A3_common import SPEC_SHA256, spec_sha256  # noqa: E402

INF = math.inf


def test_spec_hash_matches_frozen():
    assert spec_sha256() == SPEC_SHA256


@pytest.mark.parametrize('a,b,exp', [('high', 'low', 4), ('high', 'medium', 3), ('high', 'high', 2),
                                     ('medium', 'low', 3), ('medium', 'medium', 2), ('medium', 'high', 1),
                                     ('low', 'low', 2), ('low', 'medium', 1), ('low', 'high', 0),
                                     ('unknown', 'unknown', 1), (None, None, 1), ('High', ' LOW ', 4)])
def test_c1(a, b, exp):
    assert S.c1_score(a, b) == exp


@pytest.mark.parametrize('qv,exp', [(0.0, 4), (0.5, 4), (0.5000001, 3), (2.0, 3), (2.0000001, 2), (5.0, 2),
                                    (5.0000001, 1), (15.0, 1), (15.0000001, 0), (1e9, 0)])
def test_c2_qv(qv, exp):
    assert S.c2_score(qv=qv) == exp


@pytest.mark.parametrize('r,exp', [(1.0, 1), (5.0, 1), (0.9999999, 2), (0.5, 2), (0.4999999, 3), (0.1, 3),
                                   (0.0999999, 2), (0.0, 2)])
def test_c2_proxy_never_4_or_0(r, exp):
    assert S.c2_score(r=r) == exp


def test_c2_qv_takes_precedence_and_none_gives_1():
    assert S.c2_score(qv=20.0, r=0.3) == 0
    assert S.c2_score() == 1


@pytest.mark.parametrize('adv,exp', [(200_000, 4), (199_999.9, 3), (50_000, 3), (49_999.9, 2), (10_000, 2),
                                     (9_999.9, 1), (1_000, 1), (999.9, 0), (0, 0), (None, 1)])
def test_c3_adv(adv, exp):
    assert S.c3_score(adv) == exp


@pytest.mark.parametrize('adv,ratio,exp', [(200_000, 3.0, 3), (200_000, 2.9999, 4), (500, 3.5, 0), (None, 4.0, 0),
                                           (60_000, None, 3)])
def test_c3_overnight_deduction(adv, ratio, exp):
    assert S.c3_score(adv, ratio) == exp


@pytest.mark.parametrize('items,exp', [([False] * 4, 4), ([True, False, False, False], 3), (['unknown', False, False, False], 3),
                                       ([True, True, 'unknown', None], 0), ([True, True, False, False], 2)])
def test_c4(items, exp):
    assert S.c4_score(items) == exp


@pytest.mark.parametrize('sig,exp', [(1.5, 4), (6.0, 4), (3.0, 4), (1.4999, 3), (1.0, 3), (6.0001, 3), (10.0, 3),
                                     (0.9999, 2), (0.5, 2), (10.0001, 2), (20.0, 2), (0.4999, 1), (0.25, 1),
                                     (20.0001, 1), (40.0, 1), (0.2499, 0), (40.0001, 0), (0.0, 0), (None, 1)])
def test_c5_boundaries_go_higher(sig, exp):
    assert S.c5_score(sig) == exp


def test_l1_weights_and_gate():
    s = {'C1': 2, 'C2': 2, 'C3': 2, 'C4': 2, 'C5': 2, 'C6': 2}
    assert S.l1_value(s) == pytest.approx(2.0)
    ok, reasons = S.l1_gate(S.l1_value(s), s, True)
    assert ok and not reasons
    ok, reasons = S.l1_gate(1.9999, s, True)
    assert not ok and 'L1 < 2.00' in reasons
    s0 = dict(s, C3=0, C1=4)
    ok, reasons = S.l1_gate(S.l1_value(s0), s0, True)
    assert not ok and any('criterion 0' in r for r in reasons)
    ok, reasons = S.l1_gate(3.0, dict(s, C1=4), 'unknown')
    assert not ok and any('60-date' in r for r in reasons)
    assert S.l1_value({'C1': 4, 'C2': 0, 'C3': 0, 'C4': 0, 'C5': 0, 'C6': 0}) == pytest.approx(1.0)


def test_l1_float_boundary_exact_two_passes():
    s = {'C1': 3, 'C2': 1, 'C3': 2, 'C4': 2, 'C5': 1, 'C6': 2}   # 0.75+0.2+0.3+0.3+0.1+0.3 = 1.95
    assert S.l1_value(s) == pytest.approx(1.95)
    s = {'C1': 2, 'C2': 3, 'C3': 1, 'C4': 2, 'C5': 2, 'C6': 2}   # 0.5+0.6+0.15+0.3+0.2+0.3 = 2.05
    assert S.l1_gate(S.l1_value(s), s, True)[0]
    s = {'C1': 2, 'C2': 2, 'C3': 3, 'C4': 1, 'C5': 2, 'C6': 2}   # exactly 2.00 with float sums
    assert S.l1_gate(S.l1_value(s), s, True)[0]


@pytest.mark.parametrize('x,x0,exp', [(0.0, 2.0, 4.0), (1.0, 2.0, 2.0), (2.0, 2.0, 0.0), (3.0, 2.0, 0.0), (INF, 3.0, 0.0),
                                      (1.5, 3.0, 2.0), (None, 2.0, None)])
def test_s_fn(x, x0, exp):
    assert S.s_fn(x, x0) == (pytest.approx(exp) if exp is not None else None)


def test_e_score():
    assert S.e_score(0.0, 0.0, 0.0) == pytest.approx(4.0)
    assert S.e_score(1.0, 1.5, 1.5) == pytest.approx(0.6 * 2 + 0.15 * 2 + 0.25 * 2)
    assert S.e_score(INF, INF, INF) == 0.0
    # ruling OC-A3-3: an unknown component scores 1, not None
    assert S.e_score(None, 1.0, 1.0) == pytest.approx(0.6 * 1 + 0.15 * 8 / 3 + 0.25 * 8 / 3)
    assert S.e_score(0.0, None, None) == pytest.approx(0.6 * 4 + 0.15 * 1 + 0.25 * 1)


@pytest.mark.parametrize('room,exp', [(4.0, 4), (3.9999, 3), (3.0, 3), (2.9999, 2), (2.0, 2), (1.9999, 1), (1.0, 1),
                                      (0.9999, 0), (0.0, 0), (None, 1)])
def test_d(room, exp):
    assert S.d_score(room) == exp   # unknown room -> 1 (ruling OC-A3-2)


def test_p_and_rel():
    assert S.p_score([False, False, False, False]) == 4
    assert S.p_score([True, False, 'unknown', False]) == 2
    assert S.p_score([True] * 4) == 0
    assert S.rel_score([0, 0, 0, 0]) == 4
    assert S.rel_score([1, 1, 1, 2]) == 0
    assert S.rel_score([1, 0, 0, 2]) == 1


def test_l2_weights():
    s = {'E': 4, 'D': 4, 'R': 4, 'A': 4, 'F': 4, 'P': 4, 'Rel': 4}
    assert S.l2_value(s) == pytest.approx(4.0)
    assert sum(S.W_L2.values()) == pytest.approx(1.0)
    assert sum(S.W_L1.values()) == pytest.approx(1.0)


def test_round2_half_up():
    assert S.round2(1.235) == 1.24
    assert S.round2(1.2349999) == 1.23
    assert S.round2(2.005) == 2.01


def _pair(code, firm, s, mu, l1, cost):
    return {'code': code, 'firm': firm, 'S': s, 'mu_star_lim': mu, 'L1': l1, 'cost_per_attempt_usd': cost}


def test_tie_rule_order():
    a = _pair('ZN', 'topstep', 2.504, 1.0, 2.5, 100)
    b = _pair('CL', 'topstep', 2.496, 0.9, 2.4, 100)   # ties a at 2.50: lower mu wins
    c = _pair('GC', 'lucid', 2.51, 2.0, 2.0, 50)       # 2.51 ahead
    d = _pair('MCL', 'bulenox', 2.50, 0.9, 2.6, 100)   # ties b on mu, higher L1 wins
    e = _pair('MCL', 'lucid', 2.50, 0.9, 2.6, 90)      # ties d on mu and L1: lower cost wins
    f = _pair('MCL', 'mffu', 2.50, 0.9, 2.6, 90)       # ties e: firm name alphabetical (Lucid Trading < My Funded Futures)
    g = _pair('ES', 'tradeify', 2.50, None, 2.6, None)  # unknown mu sorts last in the tie
    order = sorted([a, b, c, d, e, f, g], key=S.rank_key)
    assert [(p['code'], p['firm']) for p in order] == [('GC', 'lucid'), ('MCL', 'lucid'), ('MCL', 'mffu'), ('MCL', 'bulenox'),
                                                       ('CL', 'topstep'), ('ZN', 'topstep'), ('ES', 'tradeify')]


def test_tie_rule_code_before_firm():
    a = _pair('ZC', 'bulenox', 2.0, 1.0, 2.0, 10)
    b = _pair('CL', 'tradeify', 2.0, 1.0, 2.0, 10)
    assert [p['code'] for p in sorted([a, b], key=S.rank_key)] == ['CL', 'ZC']


def test_parse_mu():
    assert S.parse_mu(1.23) == 1.23
    assert S.parse_mu('> 4') == INF
    assert S.parse_mu(4.5) == INF
    assert S.parse_mu('2.5') == 2.5
    assert S.parse_mu(None) is None


def test_read_econ_shapes():
    rows = [{'firm': 'Topstep', 'code': 'MNQ', 'mu_star_lim': 0.5, 'mu_star_mkt': '> 4', 'mu10K': 1.0,
             'cost_per_attempt_usd': 120}]
    for d in (rows, {'pairs': rows}):
        e = S.read_econ(d)
        assert e[('topstep', 'MNQ')]['mu_star_mkt'] == INF
        assert e[('topstep', 'MNQ')]['cost_per_attempt_usd'] == 120
    assert ('mffu', 'CL') in S.read_econ([{'firm': 'My Funded Futures', 'code': 'CL'}])


def test_read_blind_and_r_for():
    key = {'contracts': {'C01': 'MNQ'}, 'firms': {'F01': 'topstep'}}
    d = {'contracts': {'C01': {'C1a': 'high', 'C1b': 'high', 'C6': 3}},
         'firms': {'F01': {'R': {'equity_index': 3, 'all': 4}, 'A': 3, 'F': 1,
                           'Rel_deductions': {'under_2_years': 0, 'payout': 1, 'changes': 1, 'regulatory': 0}}}}
    c, f = S.read_blind(d, key)
    assert c['MNQ']['C6'] == 3 and c['MNQ']['C1a'] == 'high'
    assert f['topstep']['Rel'] == 2 and f['topstep']['A'] == 3
    assert S.r_for(f['topstep']['R'], 'equity_index') == 3
    assert S.r_for(f['topstep']['R'], 'rates') == 4
    assert S.r_for({'metals': 2}, 'rates') == 1          # unknown class -> 1
    assert S.r_for(3, 'grains') == 3


def test_pipeline_smoke_with_synthetic_ratings():
    """End-to-end on the real fact files with synthetic blind ratings and econ (no files written)."""
    facts, fp = S.load_json('A3_facts.json'), S.load_json('A3_firm_products.json')
    assert facts and fp
    blind_c = {c: {'C1a': 'medium', 'C1b': 'medium', 'C6': 2} for c in facts['candidates']}
    blind_f = {f: {'R': 4, 'A': 3, 'F': 1, 'Rel': 3} for f in S.FIRMS}
    econ = {(p['firm'], p['code']): {'mu_star_lim': 1.0, 'mu_star_mkt': 2.0, 'mu10K': 1.5, 'cost_per_attempt_usd': 100.0}
            for p in fp['pairs']}
    l1, pairs, ranked = S.run_variant('primary', facts, fp, econ, blind_c, blind_f)
    assert len(l1) == 47
    assert all(r['L1'] is not None for r in l1.values())
    assert l1['MZC']['L1_gate_pass'] is False                       # not listed in the pilot window
    assert l1['2YY']['C3'] == 0 and l1['2YY']['L1_gate_pass'] is False
    assert all(p['eligible_for_rank'] for p in ranked)
    assert [p['rank'] for p in ranked] == list(range(1, len(ranked) + 1))
    assert all(S.round2(ranked[i]['S']) >= S.round2(ranked[i + 1]['S']) for i in range(len(ranked) - 1))
    # MNQ: room = 2000 / (967 ticks * 0.5) = 4.14 -> D 4
    mnq = [p for p in pairs if p['code'] == 'MNQ' and p['firm'] == 'topstep'][0]
    assert mnq['D'] == 4 and mnq['P'] == 2
    l1o, pairs_o, _ = S.run_variant('OC1_off', facts, fp, econ, blind_c, blind_f)
    assert l1o['MNQ']['C5'] == 1 and 'C5' in l1o['MNQ']['u']
    mnq_o = [p for p in pairs_o if p['code'] == 'MNQ' and p['firm'] == 'topstep'][0]
    assert mnq_o['E'] == pytest.approx(1.0) and 'E' in mnq_o['u'] and mnq_o['D'] == 1   # rulings OC-A3-2/3: unknown -> 1


def test_refuses_on_spec_hash_mismatch(monkeypatch):
    monkeypatch.setattr(S, 'spec_sha256', lambda: '0' * 64)
    with pytest.raises(SystemExit) as ei:
        S.main()
    assert 'REFUSED' in str(ei.value)


# ------------------------------------------------------------------------------------------------ lead rulings
def test_rulings_file_loads_and_hash_guard(monkeypatch):
    r = S.load_rulings()
    assert r['sha256'].startswith(S.RULINGS_SHA_PREFIX)
    v1 = ('mng_gate', 'D_unknown', 'E_unknown', 'jump_transfer', 'C6_floor')      # the v1 rulings (v2 keys are tested below)
    assert {k: r[k] for k in v1} == {'mng_gate': True, 'D_unknown': 1, 'E_unknown': 1, 'jump_transfer': True, 'C6_floor': 2}
    monkeypatch.setattr(S, 'RULINGS_SHA_PREFIX', 'deadbeef')
    with pytest.raises(SystemExit) as ei:
        S.load_rulings()
    assert 'REFUSED' in str(ei.value)


def test_variant_params_flip_exactly_one_ruling():
    r = S.load_rulings()
    base = S.variant_params('primary', r)
    assert (base['mng_gate'], base['D_unknown'], base['E_unknown'], base['jump_transfer'], base['C6_floor']) == (True, 1, 1, True, 2)
    for name, key, val in (('D_unknown_0', 'D_unknown', 0), ('E_unknown_0', 'E_unknown', 0),
                           ('C4_no_transfer', 'jump_transfer', False), ('C6_as_rated', 'C6_floor', None)):
        p = S.variant_params(name, r)
        assert p[key] == val
        assert {k: v for k, v in p.items() if k != key} == {k: v for k, v in base.items() if k != key}, name
    assert set(S.VARIANT_NAMES) >= {'primary', 'D_unknown_0', 'E_unknown_0', 'C4_no_transfer', 'C6_as_rated'}
    assert 'C4_jump_transfer' not in S.VARIANT_NAMES


def _facts():
    facts = S.load_json('A3_facts.json')
    assert facts
    return facts


def test_ruling_mng_passes_60_date_gate_others_stay_unknown():
    facts, r = _facts(), S.load_rulings()
    assert facts['candidates']['MNG']['gate_60_dates']['value'] == 'unknown'   # the raw fact is untouched
    cands = S.apply_variant(facts, None, S.variant_params('primary', r))
    assert cands['MNG']['gate_60_dates']['value'] is True
    assert 'lead_ruling_OC-A3-1' in cands['MNG']['gate_60_dates']['flags']
    for c in ('5YY', '30Y'):
        assert cands[c]['gate_60_dates']['value'] == 'unknown'
    assert facts['candidates']['MNG']['gate_60_dates']['value'] == 'unknown'   # no mutation of the input
    ok, reasons = S.l1_gate(3.0, {k: 2 for k in S.W_L1}, cands['MNG']['gate_60_dates']['value'])
    assert ok and not reasons
    ok, reasons = S.l1_gate(3.0, {k: 2 for k in S.W_L1}, cands['5YY']['gate_60_dates']['value'])
    assert not ok and any('60-date' in x for x in reasons)


def test_ruling_d_unknown_scores_1_variant_0():
    assert S.d_score(None) == 1 and S.d_score(None, unknown=0) == 0
    assert S.d_score(0.5) == 0          # a known room below 1 still scores 0


def test_ruling_e_unknown_components_score_1_variant_0():
    assert S.e_score(None, None, None) == pytest.approx(1.0)
    assert S.e_score(None, None, None, unknown=0) == pytest.approx(0.0)
    assert S.e_score(INF, None, None) == pytest.approx(0.15 + 0.25)   # a known '> 4' stays 0, unknown parts take 1


def test_ruling_c4_jump_transfer_primary_and_no_transfer_variant():
    facts, r = _facts(), S.load_rulings()
    sib = facts['variants']['C4_jump_transfer']
    code = 'QM'
    key = 'big_moves_10plus_per_year'
    assert code in sib
    prim = S.apply_variant(facts, None, S.variant_params('primary', r))
    old = S.apply_variant(facts, None, S.variant_params('C4_no_transfer', r))
    assert prim[code]['C4'][key]['value'] == sib[code][key]['value']
    assert 'jump_transfer_variant' in prim[code]['C4'][key]['flags']
    assert old[code]['C4'] == facts['candidates'][code]['C4']
    assert facts['candidates'][code]['C4'][key] is not prim[code]['C4'][key]


def test_ruling_c6_floor_of_2_replaces_c25_zero_and_as_rated_variant():
    blind = S.load_json('A3_blind_ratings.json')
    key = S.load_json('A3_mask_key.json')
    blind_c, _ = S.read_blind(blind, key)
    assert blind_c['NQ']['C6'] == 0                      # C25 as rated (OC-6: abstract-only evidence)
    assert any(v['C6'] == 1 for v in blind_c.values())
    facts, r = _facts(), S.load_rulings()
    cands = S.apply_variant(facts, None, S.variant_params('primary', r))
    fl = S.score_layer1(cands, blind_c, c6_floor=2)
    asr = S.score_layer1(cands, blind_c, c6_floor=None)
    assert fl['NQ']['C6'] == 2 and fl['NQ']['C6_rated'] == 0
    assert asr['NQ']['C6'] == 0 and asr['NQ']['L1_gate_pass'] is False and any('criterion 0' in x for x in asr['NQ']['L1_gate_reasons'])
    for code, b in blind_c.items():
        assert fl[code]['C6'] == max(2, b['C6'])          # below 2 -> 2; 2 and 3 as rated
        assert asr[code]['C6'] == b['C6']


def test_every_other_primary_rating_as_given():
    """The floor touches C6 only: C1 comes from the blind C1a/C1b and ratings of 2 and 3 are unchanged."""
    blind = S.load_json('A3_blind_ratings.json')
    key = S.load_json('A3_mask_key.json')
    blind_c, blind_f = S.read_blind(blind, key)
    facts, r = _facts(), S.load_rulings()
    cands = S.apply_variant(facts, None, S.variant_params('primary', r))
    fl = S.score_layer1(cands, blind_c, c6_floor=2)
    asr = S.score_layer1(cands, blind_c, c6_floor=None)
    for code in blind_c:
        assert fl[code]['C1'] == asr[code]['C1'] == S.c1_score(blind_c[code]['C1a'], blind_c[code]['C1b'])


def test_find_ties_reports_deciding_level():
    a = dict(_pair('GC', 'lucid', 2.504, 1.0, 2.5, 100), rank=1)
    b = dict(_pair('CL', 'topstep', 2.496, 1.0, 2.4, 100), rank=2)
    c = dict(_pair('ZN', 'topstep', 2.30, 1.0, 2.4, 100), rank=3)
    ties = S.find_ties(sorted([a, b, c], key=S.rank_key))
    assert len(ties) == 1 and ties[0]['ranks'] == [1, 2]
    assert ties[0]['steps'][0]['decided_by'] == 'L1'


# ------------------------------------------------------------------------------------------------ v2 rulings (RR-01, RR-03, RR-04, RR-05)
def _inputs():
    key = S.load_json('A3_mask_key.json')
    blind_c, blind_f = S.read_blind(S.load_json('A3_blind_ratings.json'), key)
    econ_raw = S.load_json('A3_econ.json')
    return key, blind_c, blind_f, econ_raw, S.read_econ(econ_raw)


def _run(name, rulings=None):
    facts, fp = _facts(), S.load_json('A3_firm_products.json')
    key, blind_c, blind_f, econ_raw, econ = _inputs()
    return S.run_variant(name, facts, fp, econ, blind_c, blind_f, rulings or S.load_rulings(), econ_raw)


def test_rulings_v2_load_and_hash_guard(monkeypatch):
    r = S.load_rulings()
    assert r['sha256_v2'] == S.RULINGS_V2_SHA256 and r['sha256_v2'].startswith('f99b6e9f')
    assert r['C1b_override'] == {'C40': 'high'} and len(r['C6_cap_labels']) == 13
    assert r['topstep_R_by_size'] is True and r['lucid_fee_u_rule'] is True
    assert r['mng_gate'] is True and r['C6_floor'] == 2          # v1 rulings still applied (inherited)
    monkeypatch.setattr(S, 'RULINGS_V2_SHA256', 'deadbeef')
    with pytest.raises(SystemExit) as ei:
        S.load_rulings()
    assert 'REFUSED' in str(ei.value)


def test_v1_rulings_only_turns_off_exactly_the_four_v2_rulings():
    r = S.load_rulings()
    base, v1 = S.variant_params('primary', r), S.variant_params('v1_rulings_only', r)
    changed = {k for k in base if base[k] != v1[k]}
    assert changed == {'C1b_override', 'C6_cap_labels', 'topstep_R_by_size', 'lucid_fee_u_rule'}
    assert v1['C1b_override'] == {} and v1['C6_cap_labels'] == () and not v1['topstep_R_by_size'] and not v1['lucid_fee_u_rule']
    for name in ('D_unknown_0', 'E_unknown_0', 'C4_no_transfer', 'C6_as_rated', 'OC1_off'):   # other variants keep the v2 rulings
        p = S.variant_params(name, r)
        for k in ('C1b_override', 'C6_cap_labels', 'topstep_R_by_size', 'lucid_fee_u_rule'):
            assert p[k] == base[k], (name, k)


def test_v1_rulings_only_reproduces_the_v1_table():
    import json
    with open(os.path.join(S.BR, 'A3_ranking_table_v1.json')) as fh:
        v1 = json.load(fh)['variants']['primary']
    l1, _pairs, ranked = _run('v1_rulings_only')
    sig = [(p['rank'], p['firm'], p['code'], p['S'], p['E'], p['R']) for p in ranked]
    assert sig == [(p['rank'], p['firm'], p['code'], p['S'], p['E'], p['R']) for p in v1['ranked']]
    assert {c: r['L1_gate_pass'] for c, r in l1.items()} == {c: r['L1_gate_pass'] for c, r in v1['layer1'].items()}


def test_rr01_c40_c1b_all_unknown_is_high_and_qg_fails_layer1():
    key, blind_c, _bf, _er, _e = _inputs()
    assert key['contracts']['C40'] == 'QG' and blind_c['QG']['C1b'] == 'medium'   # as the blind scorer rated it
    cands = S.apply_variant(_facts(), None, S.variant_params('primary', S.load_rulings()))
    off = S.score_layer1(cands, blind_c, c6_floor=2)
    on = S.score_layer1(cands, blind_c, c6_floor=2, c1b_override={'C40': 'high'})
    assert off['QG']['C1'] == 2 and off['QG']['L1_gate_pass'] is True
    assert on['QG']['C1'] == 1 and on['QG']['L1'] == pytest.approx(off['QG']['L1'] - 0.25)
    assert on['QG']['L1'] < 2.0 and on['QG']['L1_gate_pass'] is False and 'C1b:RR-01' in on['QG']['u']
    for code in blind_c:                                   # only C40 (QG) changes
        if code != 'QG':
            assert on[code]['C1'] == off[code]['C1'] and on[code]['L1'] == off[code]['L1']
    assert _run('primary')[2] and all(p['code'] != 'QG' for p in _run('primary')[2])
    assert any(p['code'] == 'QG' for p in _run('v1_rulings_only')[2])


def test_rr03_cap_the_13_grain_labels_at_2_and_leave_equity_c6_3():
    grains = {'MZC', 'MZS', 'MZW', 'MZL', 'MZM', 'XC', 'XK', 'XW', 'ZC', 'ZS', 'ZW', 'ZL', 'ZM'}
    key, blind_c, _bf, _er, _e = _inputs()
    assert {key['contracts'][lab] for lab in S.RR03_CAP_LABELS} == grains and len(set(S.RR03_CAP_LABELS)) == 13
    cands = S.apply_variant(_facts(), None, S.variant_params('primary', S.load_rulings()))
    capped = S.score_layer1(cands, blind_c, c6_floor=2, c6_cap_labels=S.RR03_CAP_LABELS)
    plain = S.score_layer1(cands, blind_c, c6_floor=2)
    for code in grains:
        assert plain[code]['C6'] == 3 and capped[code]['C6'] == 2 and capped[code]['C6_rated'] == 3
        assert capped[code]['L1'] == pytest.approx(plain[code]['L1'] - 0.15)
    for code in ('MNQ', 'M2K', 'MYM', 'RTY', 'YM'):         # the 5 equity ratings rest on full text and stand
        assert capped[code]['C6'] == plain[code]['C6'] == 3
    others = set(blind_c) - grains
    assert all(capped[c]['L1'] == plain[c]['L1'] for c in others)


def test_rr04_topstep_r_from_r_by_size_micro_4_non_micro_3():
    _k, _bc, blind_f, _er, _e = _inputs()
    assert blind_f['topstep']['R_by_size']['equity_index'] == {'non_micro': 3, 'micro': 4}
    assert S.r_by_size_for(blind_f['topstep'], 'MNQ', 'equity_index') == 4
    assert S.r_by_size_for(blind_f['topstep'], 'NQ', 'equity_index') == 3
    assert S.r_by_size_for(blind_f['topstep'], 'MGC', 'metals') == 4 and S.r_by_size_for(blind_f['topstep'], 'GC', 'metals') == 3
    assert S.r_by_size_for(blind_f['topstep'], 'MCL', 'crude_oil') is None      # no R_by_size entry: class dict stays
    assert S.r_by_size_for(blind_f['lucid'], 'MNQ', 'equity_index') is None     # only Topstep's sheet carries R_by_size
    assert S.MICRO_CODES <= set(S.CANDIDATES)
    on = {(p['firm'], p['code']): p for p in _run('primary')[1]}
    off = {(p['firm'], p['code']): p for p in _run('v1_rulings_only')[1]}
    for code in ('MNQ', 'M2K', 'MYM', 'MGC', 'MHG', 'SIL'):
        assert on[('topstep', code)]['R'] == 4 and off[('topstep', code)]['R'] == 3, code
    for code in ('NQ', 'RTY', 'YM', 'GC'):
        assert on[('topstep', code)]['R'] == off[('topstep', code)]['R'] == 3, code
    assert all(on[k]['R'] == off[k]['R'] for k in on if k[0] != 'topstep')


def test_rr05_lucid_fee_u_rule_qg_qm_rerun_others_flagged_unchanged():
    import json
    _k, _bc, _bf, econ_raw, econ = _inputs()
    lu = S.lucid_u_rule(econ_raw)
    assert lu['fee']['QG'] == pytest.approx(4.0) and lu['fee']['QM'] == pytest.approx(5.4)   # highest at the other four firms
    assert set(lu['econ']) == {('lucid', 'QG'), ('lucid', 'QM')}
    assert lu['econ'][('lucid', 'QG')]['mu_star_lim'] == pytest.approx(0.33) and lu['econ'][('lucid', 'QM')]['mu10K'] == pytest.approx(0.88)
    on = {(p['firm'], p['code']): p for p in _run('primary')[1]}
    off = {(p['firm'], p['code']): p for p in _run('v1_rulings_only')[1]}
    assert on[('lucid', 'QG')]['mu_star_lim'] == pytest.approx(0.33) and off[('lucid', 'QG')]['mu_star_lim'] == pytest.approx(0.22)
    assert on[('lucid', 'QG')]['E'] < off[('lucid', 'QG')]['E'] and on[('lucid', 'QM')]['E'] < off[('lucid', 'QM')]['E']
    assert 'rerun' in on[('lucid', 'QG')]['fee_reading'] and 'fee' in on[('lucid', 'QG')]['u']
    nr = on[('lucid', 'MNQ')]                                  # not in the rerun file: E unchanged, flagged
    assert 'not rerun' in nr['fee_reading'] and 'fee' in nr['u'] and nr['fee_rt_usd_u_rule'] == pytest.approx(1.9)
    assert nr['E'] == off[('lucid', 'MNQ')]['E'] and nr['mu_star_lim'] == off[('lucid', 'MNQ')]['mu_star_lim']
    assert all(on[k]['fee_reading'] == 'sourced' and 'fee' not in on[k]['u'] for k in on if k[0] != 'lucid')
    assert all(off[k]['fee_reading'] == 'sourced' for k in off)
    assert S.read_econ(econ_raw)[('lucid', 'QG')]['mu_star_lim'] == pytest.approx(0.22)    # the input is not mutated
    assert econ[('lucid', 'QG')]['mu_star_lim'] == pytest.approx(0.22)
