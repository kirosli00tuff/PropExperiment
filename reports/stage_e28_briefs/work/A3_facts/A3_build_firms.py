"""Stage E.28 A3 (FactTable): build A3_firm_products.json from the A2 firm and platform records.

Per (firm, candidate): listed (yes/no/unknown), round-trip fee in USD and ticks, the 50K position limit, product
restriction text. Per firm: the facts behind D (MLL), R, A, F, P, Rel and the Layer 2 gates (BC eligibility).
P is the only firm criterion scored by script; its four items are encoded here as true/false/unknown with sources.
Run: python3 A3_build_firms.py (after A3_build_facts.py).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A3_common import BR, CANDIDATES, CLASS_OF, FIRMS, FIRM_NAME, fact, load  # noqa: E402

FEE_FIELD = {'topstep': 'fee_rt', 'lucid': 'commission_round_trip', 'tradeify': 'fee_rt', 'mffu': 'rt',
             'bulenox': 'commission_round_trip'}


def get(d, path):
    cur = d
    for p in path.split('.'):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def fc(firm, d, path, unit=None, **kw):
    """Fact cell from an A2 path, keeping value, quote and note."""
    c = get(d, path)
    if isinstance(c, dict) and 'value' in c:
        return fact(c.get('value'), unit or c.get('unit'), f'A2_firm_{firm}.json:{path}', quote=c.get('quote'),
                    note=c.get('note'), **kw)
    if c is None:
        return fact(None, unit, f'A2_firm_{firm}.json:{path} (absent)', u=True)
    return fact(c, unit, f'A2_firm_{firm}.json:{path}', **kw)


def pc(platform, path):
    c = get(load('A2_platforms.json'), f'{platform}.{path}')
    if isinstance(c, dict) and 'value' in c:
        return fact(c.get('value'), c.get('unit'), f'A2_platforms.json:{platform}.{path}', quote=c.get('quote'), note=c.get('note'))
    return fact(None, None, f'A2_platforms.json:{platform}.{path} (absent)', u=True)


# Firm-level paths (value, quote, note copied with provenance). Grouped by the criterion they inform.
PATHS = {
    'topstep': {
        'plan': ['plan_50k.plan_name', 'plan_50k.mll_amount', 'plan_50k.mll_type', 'plan_50k.dll', 'plan_50k.max_position',
                 'funded_stage.xfa_sim_or_live', 'funded_stage.xfa_mll', 'funded_stage.xfa_dll'],
        'R': ['rules.tier1_news', 'rules.volatility_caps_50k', 'rules.flat_by', 'rules.grain_hours', 'rules.holiday_rule'],
        'A': ['rules.automation_combine', 'rules.automation_xfa', 'rules.api_bots', 'rules.api_cost', 'rules.api_rate_limit',
              'rules.terms_short_term_hft', 'rules.sim_fill_exploitation', 'rules.outside_bbo', 'rules.min_hold_or_rate_rule',
              'funded_stage.lfa_api', 'rules.platforms'],
        'F': ['rules.sim_limit_fill_rule', 'rules.platforms'],
        'Rel': ['reliability.founded', 'reliability.regulatory_actions', 'reliability.nfa_registration_news',
                'reliability.litigation', 'reliability.outages_late_2025', 'reliability.change_payout_cap',
                'reliability.change_consistency', 'reliability.change_platforms', 'reliability.change_b2f_window',
                'reliability.change_wise'],
        'info': ['reliability.paid_out_claim', 'reliability.approval_rate_claim', 'reliability.stats_2025',
                 'funded_stage.payout_approval_time', 'eligibility.payout_methods_canada', 'eligibility.currency', 'eligibility.kyc'],
        'bc': 'eligibility.canada_bc_accepted', 'mll': 'plan_50k.mll_amount', 'dll': 'plan_50k.dll',
        'poslimit': 'rules.position_limit_50k',
    },
    'lucid': {
        'plan': ['plan.name', 'plan.max_loss_limit', 'plan.max_loss_limit_type', 'plan.daily_loss_limit', 'plan.max_size',
                 'funded.type', 'funded.drawdown', 'funded.daily_loss_limit'],
        'R': ['restrictions.news_pro', 'restrictions.flat_by', 'restrictions.product_specific'],
        'A': ['automation.allowed', 'automation.api', 'automation.hft', 'automation.microscalping', 'automation.scalping',
              'automation.order_rate_limit', 'automation.sim_fill_exploitation_ban', 'platforms.list'],
        'F': ['platforms.sim_fill_rule', 'platforms.list'],
        'Rel': ['reliability.operating_since', 'reliability.regulatory_actions', 'reliability.disputes',
                'reliability.rule_changes_12m'],
        'info': ['reliability.firm_claims', 'eligibility.payout_methods', 'eligibility.kyc', 'access.pricing_page_today'],
        'bc': 'eligibility.canada_bc', 'mll': 'plan.max_loss_limit', 'dll': 'plan.daily_loss_limit',
        'poslimit': 'position_limit_50k',
    },
    'tradeify': {
        'plan': ['plan.name', 'plan.max_loss', 'plan.max_loss_type', 'plan.daily_loss_limit', 'plan.position_limit',
                 'funded.type', 'funded.max_loss', 'funded.daily_loss_limit'],
        'R': ['restrictions.news', 'restrictions.product_specific', 'restrictions.hours', 'plan.flat_by'],
        'A': ['automation.bots_allowed', 'automation.api', 'automation.order_rate_limit', 'automation.min_hold',
              'automation.sim_exploit', 'funded.microscalping', 'platform.brokers'],
        'F': ['platform.sim_fill_rule', 'platform.brokers'],
        'Rel': ['reliability.operating_since', 'reliability.regulatory_actions', 'reliability.disputes_12m',
                'reliability.rule_changes_12m'],
        'info': ['reliability.payout_claims', 'reliability.funded_payout_rate', 'reliability.eval_pass_rate',
                 'funded.processing', 'eligibility.canada_payout_terms'],
        'bc': 'eligibility.bc_canada', 'mll': 'plan.max_loss', 'dll': 'plan.daily_loss_limit', 'poslimit': 'plan.position_limit',
    },
    'mffu': {
        'plan': ['plan.name', 'plan.eval.mll', 'plan.eval.mll_type', 'plan.eval.dll', 'plan.eval.max_contracts',
                 'plan.funded.type', 'plan.funded.mll', 'plan.funded.dll'],
        'R': ['restrictions.hours', 'restrictions.news_builder', 'restrictions.news_restricted_accounts',
              'restrictions.news_burst_ban', 'restrictions.price_limit_rule', 'restrictions.restricted_products',
              'restrictions.hedging_ban', 'position_limits.metals_micros_cap', 'position_limits.mbt_as_mini'],
        'A': ['automation.eval_and_sim_funded', 'automation.live', 'automation.hft', 'automation.order_rate_limit',
              'automation.min_hold', 'automation.trade_count_live', 'automation.sim_fill_exploits_banned', 'automation.api',
              'automation.copier', 'platforms'],
        'F': ['sim_fill_rule', 'platforms'],
        'Rel': ['reliability.operating_since', 'reliability.regulatory_actions', 'reliability.payout_disputes_12m',
                'reliability.rule_changes_12m'],
        'info': ['reliability.paid_claim', 'reliability.program_stats', 'plan.payout.processing', 'eligibility.kyc',
                 'eligibility.payout_methods_canada'],
        'bc': 'eligibility.canada_bc', 'mll': 'plan.eval.mll', 'dll': 'plan.eval.dll', 'poslimit': 'position_limits.minis_micros',
    },
    'bulenox': {
        'plan': ['plan_50k.plan_name', 'plan_50k.max_loss_limit_option1', 'plan_50k.max_loss_limit_option2',
                 'plan_50k.daily_loss_limit_option1', 'plan_50k.daily_loss_limit_option2', 'plan_50k.contracts_option1',
                 'plan_50k.contracts_option2', 'master_stage.stage_type', 'master_stage.drawdown'],
        'R': ['restrictions.news', 'restrictions.product_specific', 'restrictions.trading_day', 'restrictions.flat_by'],
        'A': ['automation.bots_allowed', 'automation.third_party_approval', 'automation.api', 'automation.api_fee',
              'automation.banned', 'automation.order_rate_limit', 'automation.minimum_hold', 'automation.flipping_review',
              'platforms.platforms'],
        'F': ['platforms.sim_fill_rule', 'platforms.server', 'platforms.platforms'],
        'Rel': ['reliability.operating_since', 'reliability.regulatory_actions', 'reliability.disputes', 'rule_changes_12m'],
        'info': ['reliability.payout_speed_claim', 'reliability.entity', 'eligibility.payout_methods', 'eligibility.kyc',
                 'eligibility.payout_currency'],
        'bc': 'eligibility.british_columbia', 'mll': 'plan_50k.max_loss_limit_option1', 'dll': 'plan_50k.daily_loss_limit_option2',
        'poslimit': 'position_limits_50k.option1',
    },
}

# Platform the strategy would use for the API (OC-4 reading: F rated on the API platform the strategy would use),
# and the platform records consulted for P and F.
API_PLATFORMS = {'topstep': ['projectx_topstepx'], 'lucid': ['rithmic', 'tradovate'], 'tradeify': ['rithmic', 'tradovate'],
                 'mffu': ['tradovate'], 'bulenox': ['rithmic']}


def p_items(firm, d):
    """P criterion items (each True = the deduction holds). Encoded from the records with the reading noted."""
    T, F, U = True, False, 'unknown'
    if firm == 'topstep':
        return {
            'no_documented_api': fact(F, None, 'A2_firm_topstep.json:rules.api_bots; A2_platforms.json:projectx_topstepx.native_api',
                                      note='ProjectX Gateway API permitted for bots (Combine and XFA; not on live funded)'),
            'no_api_oco_bracket': fact(F, None, 'A2_firm_topstep.json:rules.api_brackets; A2_platforms.json:projectx_topstepx.api_oco_bracket',
                                       note='Auto OCO Brackets attach stop-loss and take-profit to an order on the API'),
            'vps_prohibited_or_unknown': fact(T, None, 'A2_firm_topstep.json:rules.vps', note='VPS, VPNs and remote servers prohibited'),
            'rate_limit_below_10ps_or_unknown': fact(T, None, 'A2_platforms.json:projectx_topstepx.api_rate_limit',
                                                     note='200 requests / 60 s = 3.3 per second'),
        }
    if firm == 'lucid':
        return {
            'no_documented_api': fact(T, None, 'A2_firm_lucid.json:automation.api',
                                      note='no Lucid page names an API (Tradovate API, R|API, ProjectX, NinjaTrader API); '
                                           'automation documented only through listed desktop platforms', flags=['ambiguous']),
            'no_api_oco_bracket': fact(F, None, 'A2_platforms.json:rithmic.api_oco_bracket; tradovate.api_oco_bracket',
                                       note='both back ends offer native OCO/brackets', flags=['ambiguous']),
            'vps_prohibited_or_unknown': fact(T, None, 'A2_firm_lucid.json:platforms.vps', u=True, note='no Lucid page mentions VPS'),
            'rate_limit_below_10ps_or_unknown': fact(T, None, 'A2_platforms.json:rithmic.api_rate_limit; tradovate.api_rate_limit',
                                                     note='Rithmic unpublished; Tradovate 5,000/hour = 1.4/s'),
        }
    if firm == 'tradeify':
        return {
            'no_documented_api': fact(T, None, 'A2_firm_tradeify.json:automation.api',
                                      note='Tradovate API only on LIVE funded, not in evaluation or sim funded; Rithmic API unstated'),
            'no_api_oco_bracket': fact(F, None, 'A2_platforms.json:rithmic.api_oco_bracket; tradovate.api_oco_bracket',
                                       note='both back ends offer native OCO/brackets', flags=['ambiguous']),
            'vps_prohibited_or_unknown': fact(T, None, 'A2_firm_tradeify.json:platform.vps',
                                              note='VPS prohibited where it obscures verification (conditional): counted as holding',
                                              flags=['ambiguous']),
            'rate_limit_below_10ps_or_unknown': fact(T, None, 'A2_platforms.json:rithmic.api_rate_limit; tradovate.api_rate_limit',
                                                     note='Rithmic unpublished; Tradovate 5,000/hour = 1.4/s'),
        }
    if firm == 'mffu':
        return {
            'no_documented_api': fact(T, None, 'A2_firm_mffu.json:automation.api',
                                      note='no MFFU API documented; Tradovate API enablement for MFFU accounts unverified'),
            'no_api_oco_bracket': fact(F, None, 'A2_platforms.json:tradovate.api_oco_bracket', note='Tradovate placeOCO/placeOSO',
                                       flags=['ambiguous']),
            'vps_prohibited_or_unknown': fact(T, None, 'A2_firm_mffu.json:vps', u=True, note='no MFFU statement found'),
            'rate_limit_below_10ps_or_unknown': fact(T, None, 'A2_platforms.json:tradovate.api_rate_limit',
                                                     note='5,000/hour = 1.4/s'),
        }
    if firm == 'bulenox':
        return {
            'no_documented_api': fact(F, None, 'A2_firm_bulenox.json:automation.api; automation.api_fee',
                                      note='direct Rithmic connectivity through an approved third-party API (USD 100/month)'),
            'no_api_oco_bracket': fact(F, None, 'A2_platforms.json:rithmic.api_oco_bracket',
                                       note='Rithmic server-side OCO/brackets; the firm documents only NinjaTrader client-side OCO',
                                       flags=['ambiguous']),
            'vps_prohibited_or_unknown': fact(T, None, 'A2_firm_bulenox.json:platforms.vps', u=True, note='no VPS rule on any firm page'),
            'rate_limit_below_10ps_or_unknown': fact(T, None, 'A2_platforms.json:rithmic.api_rate_limit', u=True,
                                                     note='not published'),
        }
    raise KeyError(firm)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def firm_level(firm, d):
    P = PATHS[firm]
    out = {'firm': firm, 'name': FIRM_NAME[firm]}
    for grp in ('plan', 'R', 'A', 'F', 'Rel', 'info'):
        out[grp] = {p: fc(firm, d, p) for p in P[grp]}
    mll = fc(firm, d, P['mll'], unit='USD')
    mll['value'] = num(mll['value'])
    out['MLL_usd'] = mll
    out['DLL'] = fc(firm, d, P['dll'])
    out['position_limit_50k'] = fc(firm, d, P['poslimit'])
    bc = fc(firm, d, P['bc'])
    v = bc['value']
    bc['value'] = True if (v is True or (isinstance(v, str) and v.lower().startswith('accepted'))) else (False if v is False else 'unknown')
    out['bc_eligible'] = bc
    out['P_items'] = p_items(firm, d)
    out['platform_facts'] = {pl: {k: pc(pl, k) for k in ('sim_fill_rule', 'native_api', 'api_oco_bracket', 'api_rate_limit',
                                                         'platform_vps_rule', 'sim_market_data')}
                             for pl in API_PLATFORMS[firm]}
    if firm == 'bulenox':
        out['platform_facts']['rithmic']['sim_fill_rule_vendor_page'] = pc('rithmic', 'sim_fill_rule_vendor_page')
    return out


def listed_fact(firm, d, code):
    p = (d.get('products') or {}).get(code)
    if not p:
        return fact('unknown', None, f'A2_firm_{firm}.json:products.{code} (absent)', u=True)
    a = p.get('allowed', {})
    v = a.get('value')
    val = 'yes' if v is True else ('no' if v is False else 'unknown')
    flags, note = [], a.get('note')
    if firm == 'topstep' and code in ('SI', 'HG'):
        caps = get(d, 'rules.volatility_caps_50k') or {}
        cap = (caps.get('value') or {}).get(code)
        if cap == 0:
            val, flags = 'no', ['conflict_resolved']
            note = (f'products list says allowed; the 50K volatility cap (Combine/XFA/Pro) is {cap} contracts '
                    '("temporary, no end date"): not tradeable on the 50K plan (more specific source)')
    return fact(val, None, f'A2_firm_{firm}.json:products.{code}.allowed', quote=a.get('quote'), note=note, flags=flags)


def product_caps(firm, d, code):
    if firm == 'topstep':
        caps = (get(d, 'rules.volatility_caps_50k') or {}).get('value') or {}
        if code in caps:
            return f'50K volatility cap {caps[code]} contracts (Combine/XFA/Pro; temporary)'
    if firm == 'mffu':
        if code in ('MGC', 'SIL', 'MHG'):
            return '50K metals micros cap 5 contracts (since 2026-04-17)'
        if code == 'MBT':
            return 'MBT counted as a mini contract'
    return None


RESTRICTION_TEXT = {
    'topstep': {
        'equity_index': 'Tier 1 news: no new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press '
                        'conference, NFP and PPI on the full-size equity index products; micros capped (3 at 50K Combine) in the window',
        'metals': 'Tier 1 news window as for equity index (full-size metals); 50K volatility caps per product',
        'crude_oil': '50K volatility caps per product (temporary); not affected by the Tier 1 news rule',
        'natural_gas': 'none product-specific found (energies unaffected by the Tier 1 news rule)',
        'fx': 'none product-specific (FX unaffected by the Tier 1 news rule)',
        'crypto': 'none product-specific found',
        'rates': 'none product-specific (rates unaffected by the Tier 1 news rule)',
        'grains': 'grain trading hours 19:00-07:45 and 08:30-13:20 CT (the Globex grain sessions)',
        'all': 'flat by 15:10 CT every weekday; flat 15 min before any early close; orders outside the current best bid or '
               'offer prohibited (scope undefined)',
    },
    'lucid': {'all': 'news trading allowed on the evaluated plan family; flat by 16:45 ET Mon-Fri; no product-specific restriction found'},
    'tradeify': {'all': 'no news rules; no product-specific restriction found; flat by 16:45 ET; no overnight or weekend holds'},
    'mffu': {
        'all': 'hours 18:00 ET to 16:10 ET auto-flat; T1 news unrestricted on the 50K Builder plan in evaluation and sim funded '
               '(the 2-minute T1 window applies to other account types); news-burst strategies (straddles) banned; no trading '
               'within 2% of a CME price limit (sim funded and live); hedging banned',
        'metals': 'SI and HG restricted (temporary, since 2026-02-07); metals micros capped at 5 on 50K',
        'natural_gas': 'NG and QG restricted (temporary, since 2026-02-07)',
        'crypto': 'MBT counted as a mini',
    },
    'bulenox': {'all': 'news trading allowed (no blackout windows); flat by 15:59 CT, no overnight; no product-specific restriction found'},
}


def main():
    facts = load('A3_facts.json')['candidates']
    firms_out, pairs = {}, []
    for firm in FIRMS:
        d = load(f'A2_firm_{firm}.json')
        firms_out[firm] = firm_level(firm, d)
        firms_out[firm]['restrictions_by_class'] = RESTRICTION_TEXT[firm]
        for code in CANDIDATES:
            p = (d.get('products') or {}).get(code) or {}
            fee = p.get(FEE_FIELD[firm]) or {}
            fee_v = num(fee.get('value'))
            tv = facts[code]['tick_value']['value']
            listed = listed_fact(firm, d, code)
            rt = RESTRICTION_TEXT[firm]
            pairs.append({
                'firm': firm, 'code': code, 'product_class': CLASS_OF[code],
                'listed_50k': listed,
                'fee_rt_usd': fact(fee_v, 'USD per round trip', f'A2_firm_{firm}.json:products.{code}.{FEE_FIELD[firm]}',
                                   quote=fee.get('quote'), note=fee.get('note'), u=fee_v is None),
                'fee_rt_ticks': fact(None if fee_v is None else fee_v / tv, 'ticks', f'fee_rt_usd / tick_value ({tv:g})',
                                     u=fee_v is None),
                'position_limit_50k': firms_out[firm]['position_limit_50k']['value'],
                'product_cap': product_caps(firm, d, code),
                'restrictions_text': '; '.join(x for x in (rt.get(CLASS_OF[code]), rt.get('all')) if x),
            })
    out = {'generated_by': 'reports/stage_e28_briefs/work/A3_facts/A3_build_firms.py',
           'spec_sha256': '89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f',
           'firms': firms_out, 'pairs': pairs}
    with open(os.path.join(BR, 'A3_firm_products.json'), 'w') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    n_listed = sum(1 for p in pairs if p['listed_50k']['value'] == 'yes')
    print('wrote A3_firm_products.json pairs', len(pairs), 'listed', n_listed)
    for f in FIRMS:
        fo = firms_out[f]
        print(f, 'MLL', fo['MLL_usd']['value'], 'BC', fo['bc_eligible']['value'], 'P deductions',
              sum(1 for v in fo['P_items'].values() if v['value'] is True))


if __name__ == '__main__':
    main()
