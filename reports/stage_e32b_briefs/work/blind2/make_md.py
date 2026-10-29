import json, subprocess
B = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/'
o = json.load(open(B + 'F4_blind_ratings_masked.json'))
sr = json.load(open(B + 'work/blind2/short_reasons.json'))
alts = json.load(open(B + 'work/blind2/r_pairs_alts.json'))
now = subprocess.check_output(['date', '+%Y-%m-%d %H:%M %Z'], env={'TZ': 'America/Vancouver'}).decode().strip()
def cell(r):
    s = ('%g' % r['value'])
    if r['unknown']: s += ' u'
    if r.get('unverified') is True: s += ' v'
    return s
L = []
L.append('# F4 blind ratings (masked), BlindScorer2-OpusXHigh')
L.append('')
L.append('Generated %s from the three files the brief allows (brief_blind.md, F4_masked_contracts.json, F4_masked_firms.json). Full reasons with masked item ids are in F4_blind_ratings_masked.json; this file has short reasons only. Marks: "u" = unknown rule applied (value is the rule\'s default); "v" = unverified (the script caps it). No rating carries unverified true.' % now)
L.append('')
L.append('Conventions used (each is also a flag below):')
L.append('- Own facts = the items listed under the contract in the sheet, read through each scale\'s wording. D2a and D2b count only this-contract or product-group items (sibling programs and shares excluded). s2 and s3 ("product or its underlying"), D6 ("this contract or a same-underlying sibling") and s1 also count sibling-tagged items about the same underlying.')
L.append('- D6 "on data after 2010": a sample that runs across 2010 with no post-2010 split (the Baltussen et al. product rows, 1980s/90s to 2020) is not counted as post-2010 evidence. Out-of-sample positives on such samples score 3, not 4. A null for one pattern on such a sample does not reach 0.')
L.append('- D6 in-sample evidence from multi-predictor rows counts only when a coefficient is significant at 1% or the paper\'s Clark-West out-of-sample test is significant. An isolated 5% coefficient with no out-of-sample support does not count.')
L.append('- unknown = true only where the sheet has no bearing item and the value is the rule\'s default (D2a crypto; D2b satellites with leader-only programs; sat_iii with no study; rel_payout with review-site pointers only).')
L.append('- Pairs: a product not listed on the modelled plan (or capped at 0) cannot be traded there, so R = 1. A is firm-wide, because the pair facts carry no automation items.')
L.append('')
L.append('## Contracts (47 labels x 7 ratings = 329)')
L.append('')
L.append('| Label | D2a | D2b | s1 | s2 | s3 | sat_iii | D6 | Short reasons |')
L.append('|---|---|---|---|---|---|---|---|---|')
for k, v in o['codes'].items():
    L.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (k, cell(v['D2a']), cell(v['D2b']), cell(v['s1']), cell(v['s2']), cell(v['s3']), cell(v['sat_iii']), cell(v['D6']), sr[k]))
L.append('')
L.append('## Pairs (235 labels x 2 ratings = 470)')
L.append('')
L.append('A per firm (same for all 47 pairs of the firm):')
L.append('')
L.append('| Firm | A | Short reason |')
L.append('|---|---|---|')
Ashort = {
 'V-FRQI': "Firm's own API explicitly allowed in evaluation and funded; HFT ban and SIM-exploitation examples (seconds-long, hundreds of trades) met; rate limit is the API's technical limit; undefined 'any short term ... trades' manipulation example; live-stage API ban outside the modelled stages",
 'V-PCDG': 'Automation permitted firm-wide; no firm API; only through named third-party platforms; microscalping (<=5 s) and qualitative HFT rules met',
 'V-PCAN': "Own non-HFT bots allowed; the named platform's API is live-stage only (none in evaluation or sim funded); automation only via named platforms; 10-s hold gate met",
 'V-CXFO': 'Automation allowed if not exploiting sim fills; no firm API, accounts on a named third-party platform (API enablement unverified); HFT ban undefined',
 'V-OJVP': "User-built bots allowed; API only via a named platform through an approved third-party API ($100/month); third-party algorithms need approval; undefined 'scalping algorithms' ban",
}
fa = {}
for pk, v in o['pairs'].items():
    fa.setdefault(pk.split('|')[0], v['A']['value'])
for f in o['firms']:
    L.append('| %s | %s | %s |' % (f, fa[f], Ashort[f]))
L.append('')
L.append('R per pair (A column repeats the firm value):')
L.append('')
L.append('| Pair | R | A | Short reason (R) |')
L.append('|---|---|---|---|')
def rshort(reason):
    s = reason.split(' [I-')[0]
    return s if len(s) <= 150 else s[:147] + '...'
for pk, v in o['pairs'].items():
    L.append('| %s | %s | %s | %s |' % (pk, cell(v['R']), cell(v['A']), rshort(v['R']['reason'])))
L.append('')
L.append('## Firms (5 labels x 4 ratings = 20)')
L.append('')
L.append('| Firm | rel_age | rel_payout | rel_rules | rel_regulatory | Short reasons |')
L.append('|---|---|---|---|---|---|')
Fshort = {
 'V-FRQI': 'Founded 2010; open pro se court complaint (2026-04) alleging payout blocking; payout-cap cut and platform cut (dates after Sep/Oct 2025 observations); no regulatory action found',
 'V-PCDG': 'Operating since 2025 (<2 years); payout complaints only on review sites; split cut 100% -> 90/10 and fee rises in window; none found',
 'V-PCAN': 'Site since <=2022-12; review-site pointers only; one clearly material adverse change in window (another plan\'s target), payout-balance change dated outside it; none found',
 'V-CXFO': 'Since 2023; pointers only, payout page states fast approval; fee rise, five product restrictions, micro cap, inactivity closure in window; none found',
 'V-OJVP': 'Since <=2021-06; flipping-denial reports unverified (pointers); automation narrowing, account cap cut, split tier removed, payout cap added; none found',
}
for f, v in o['firms'].items():
    L.append('| %s | %s | %s | %s | %s | %s |' % (f, cell(v['rel_age']), cell(v['rel_payout']), cell(v['rel_rules']), cell(v['rel_regulatory']), Fshort[f]))
L.append('')
L.append('## Flags for the lead')
L.append('')
L.append('Gates: none. No pair has A = 0; no fact forbids the strategy (<=20 round trips, holds >= 5 min) at any firm.')
L.append('')
L.append('Binary scales (D2a, s3, sat_iii, rel_*) sit on a boundary by construction. The flags below cover ratings whose evidence is near the threshold, conflicting, or open to a different reading. Each gives the alternative value.')
L.append('')
L.append('### Global reading choices')
L.append('- Rater name: the brief\'s template says "BlindScorer-OpusXHigh"; the JSON uses "BlindScorer2-OpusXHigh", the name this run was given.')
L.append('- Sibling-tagged items for s1/s2/s3. Under a this-contract-only reading these drop: s1 2 -> 1 for K-NYZZ, K-OEVC, K-RISF, K-YEPF, K-ASNW, K-GOMC, K-WSRZ, K-BMTO; s2 2 -> 1 for K-NYZZ, K-OEVC, K-SLBV, K-JCID, K-ASNW, K-AMNJ, K-BMTO; s3 1 -> 0 for K-SGKW, K-PXYN, K-LIRS, K-DLUC, K-NYZZ, K-OEVC, K-JCID, K-ASNW, K-AMNJ, K-BMTO.')
L.append('- D6 spanning samples. If a sample running to 2020 counts as "data after 2010", every D6 = 3 resting on a Baltussen out-of-sample row becomes 4: K-YJXE, K-LIRS, K-DLUC, K-LGJM, K-NYZZ, K-AAUT, K-OEVC, K-LTAT, K-QIUI, K-KVJD, K-YEPF, K-FICQ, K-RISF, K-QAJV, K-DNXQ, K-AIIW, K-HIOT, K-TATP, K-UPOR, K-EXGX, K-DCJJ, K-NUPE, K-LWIK, K-OQCY, K-JCID, K-AMNJ, K-IXHJ, K-ASNW, K-BMTO, K-KQRO, K-WSRZ. The own-contract nulls would then give D6 0 (from 2) for K-LRVK, K-ASSS, K-AJZH, K-ODAS (one tested pattern each).')
L.append('- D6 in-sample threshold: K-YBWI and K-SLBV are 2 (alt 3: a 5%-level first-half-hour coefficient, t 1.97, with negative OOS R2). K-IXHJ, K-ASNW, K-BMTO, K-KQRO and K-WSRZ are 3 (alt 2: the reader labelled these rows negative; the 3 rests on secondary predictors plus Clark-West significance with negative R2_OOS).')
L.append('- Unlisted pairs: R = 1 for all 109 pairs with listed_on_modelled_plan false. If the script applies listing as its own gate, the stated restrictions alone give R = 4, except R = 1 for these six: V-FRQI|K-AAUT and V-FRQI|K-YBWI (50K cap 0), and V-CXFO|K-AAUT, V-CXFO|K-YBWI, V-CXFO|K-YJXE, V-CXFO|K-DLUC (restricted products). Each alternative is in work/blind2/r_pairs_alts.json.')
L.append('')
L.append('### Contracts')
L.append('- D2a near the 50% line: K-OQCY 52.5% and K-IXHJ 53.3% (2016-18 ATS share; earlier periods and HFT shares are below 50%); the grain group siblings rest on a 55.2% subgroup share. Alt 0 for each if the narrower HFT share or the prior period governed.')
L.append('- D2a conflicting facts: an ATS share of 50% or more sits beside an HFT share below 50% for K-YJXE (31.7%), K-LGJM (48.1%), K-ASSS (46.2%), K-TATP (45.2%), K-AJZH (26.6%), K-OQCY (23.9%) and K-IXHJ (36.0%). I gave 1 because "a published automated-trading or HFT share of at least 50% exists". Alt 0 if the most recent figure governs.')
L.append('- D2a crypto (K-UQNU, K-JGJF, K-ZXJD, K-OJGY): no figure at all; the unknown rule gives 1.')
L.append('- D2b counted the International Incentive Program (fee discounts with a volume floor, 2011-2026) as a volume-incentive program. For K-PXYN, K-DLUC, K-NYZZ, K-ASSS, K-LTAT, K-FICQ, K-AIIW, K-HIOT, K-TATP, K-UPOR, K-AMNJ, K-BMTO and K-CSTX it is the only basis. Alt 0.5 if it does not count.')
L.append('- D2b K-QAJV and K-KVJD: the outright MM program was in force only to 2021-01-31 (overstrike reading); the IIP class row also applies. Alt 0.5 if neither counts.')
L.append('- D2b unknown 0.5 for K-JCID, K-ASNW, K-OMOR, K-GOMC, K-WSRZ (only the leader\'s programs are sourced). Alt 1 if the leader program applies, which the script\'s link handles.')
L.append('- s1 K-LRVK, K-SGKW, K-PXYN = 1. Alt 2 if the WTI-Brent lead-lag ("fully reflecting new information within minutes", 1-second data) counts as a horizon of a minute or more.')
L.append('- s1 K-YJXE, K-LIRS, K-DLUC = 1. Alt 2 if the gas-crude volatility causality at 10-min intervals, or the cross-product inventory response, counts as an economic lead-lag.')
L.append('- s1 K-QIUI, K-LTAT = 2, resting on a spot AUD-commodity 5-min Granger study (2000-2009, in sample, working paper) that conflicts with a daily no-causality result on futures. Alt 1.')
L.append('- s1 K-KVJD, K-FICQ (and siblings K-YEPF, K-RISF) = 2, resting on a preprint\'s 60-min chart-extrema lead of about 5-12 min, not a return regression. Alt 1.')
L.append('- s1 crypto (K-UQNU, K-JGJF, K-ZXJD, K-OJGY): the minute-level cross-asset lead-lag that would give 2 is abstract-only. The full-text items alone give 1, the cap, so 1 is reported with unverified false.')
L.append('- s1 K-EXGX, K-DCJJ, K-NUPE, K-LWIK = 1. The only item is a reused full-text fact with no quote. Alt 0 if treated as unsourced.')
L.append('- s2 crude (K-LRVK, K-SGKW, K-PXYN) = 2, resting on a full-text other-venue (USO) finding of slow adjustment to the day\'s end. Conflicting full-text futures evidence says absorption within [-5,+10] min and no predictability after 10:35, and the effect was absent in 2014-16. Alt 1.')
L.append('- s2 K-YBWI, K-SLBV = 2 (copper "somewhat delayed response", delay not sized); K-AAUT, K-OEVC = 2 (delayed peaks; authors call the metals efficient). Alt 1.')
L.append('- s2 equity (K-KVJD, K-FICQ, K-QAJV, K-RISF, K-YEPF, K-DNXQ) = 1. Continuing 10-30 min adjustment is documented only on a cousin index future. Alt 2 if cousin evidence counts.')
L.append('- s2 K-EXGX, K-DCJJ, K-NUPE, K-LWIK = 1. Their lists lack the FOMC 3-hour yield-drift item that gives the Treasury contracts 2. Alt 2.')
L.append('- s2 K-OQCY, K-IXHJ and grain siblings = 2, resting on a working paper (WASDE reaction growing after 30 min). Conflicting: two other studies find no systematic under- or overreaction. Alt 1.')
L.append('- s2 crypto = 1: volatility responses are in abstracts only; full text finds no price response for bitcoin within 25-55 min. Alt 0. K-ODAS, K-KQRO, K-GOMC, K-WSRZ = 1 on a USDA schedule plus snippet pointers. Alt 0.')
L.append('- s3 = 1 on volatility, jump or volume handoff effects only: K-LRVK, K-SGKW, K-PXYN, K-IXHJ, K-ASNW, K-BMTO, K-AIIW, K-HIOT, K-UPOR, K-EXGX, K-DCJJ, K-NUPE, K-LWIK. Alt 0 if s3 needs a directional effect.')
L.append('- s3 crypto = 1 on a spot study whose session is defined by the futures break; the futures moved to 24/7 from 2026-05-29. Alt 0.')
L.append('- s3 = 0 for K-YBWI, K-SLBV (alt 1: group-level regional volume pattern) and for K-AJZH, K-OMOR, K-CSTX, K-ODAS, K-KQRO, K-GOMC, K-WSRZ (alt 1: same session pause as corn and soybeans, where effects are documented).')
L.append('- sat_iii K-ZXJD = 0. Spot held 84-87% on one of five study days; 0.52-0.56 for the futures on the other four. Alt 1 if one day suffices. K-ASSS and K-OTEO = 0: spot "dominant" with no share number. Alt 1 if "dominant" means 75% or more.')
L.append('- D6 K-OJGY, K-ZXJD = 4, resting on one peer-reviewed full-text study (CME 2020 minute data, 8 months, about 54% hold-out accuracy, gross). Alt 3.')
L.append('- D6 K-YEPF = 3 (sibling OOS row); K-YEPF\'s own full-text preprint finds 14 signal families fail net of friction in 2021-25. Alt 0.')
L.append('- D6 K-YJXE, K-LIRS, K-DLUC = 3; one full-text peer-reviewed pattern (storage-day short) is insignificant and net-negative after 2011. Alt 0 if that counts as "arbitraged away".')
L.append('- D6 K-EXGX, K-DCJJ, K-NUPE, K-LWIK = 3 via rows tagged same-underlying sibling. The reader notes these are not price-transfer siblings ("scorer decides"). Alt 2.')
L.append('- D6 K-LGJM, K-AAUT, K-YBWI: an overreaction study on these contracts (Covid sample) defines its turning points ex post, so I did not count it. Alt 3 for K-YBWI if counted.')
L.append('')
L.append('### Pairs')
L.append('- V-FRQI|K-FICQ, V-FRQI|K-QAJV, V-FRQI|K-KVJD, V-FRQI|K-LGJM: R = 3 (5-min no-new-opens windows around CPI, FOMC decision, FOMC press conference, NFP, PPI). Alt 2 or 1: some weeks hold more than 2 windows.')
L.append('- V-FRQI|K-RISF, |K-DNXQ, |K-YEPF, |K-NYZZ, |K-OEVC, |K-SLBV: R = 4 (Tier 1 window caps size; one lot still allowed). Alt 3.')
L.append('- V-CXFO listed pairs: R = 4. The firm\'s pages conflict: plan P1 is an "unrestricted account", but a general bullet says no positions or orders 2 min around any data release. Alt 3, or 1 for K-SGKW, K-PXYN, K-LRVK and the five listed grains (weekly EIA/agricultural reports plus Tier 1 macro).')
L.append('- Listed crypto pairs (V-FRQI, V-CXFO, V-OJVP with K-UQNU and K-ZXJD): R = 4. Alt 1 if firm-wide weekday-only hours count against the 24/7 exchange hours (about a third excluded since 2026-05-29).')
L.append('- A V-FRQI = 3. Alt 2: the terms cite "any short term or high frequency trades" as manipulation, undefined. Its live-stage API ban binds only the live stage, outside the modelled evaluation and funded stages.')
L.append('- A V-PCDG and V-CXFO = 2. Alt 3 if automation on third-party platforms counts as "API explicitly allowed".')
L.append('- A V-PCAN = 2. Alt 1: the named API is explicitly unavailable in evaluation and sim funded.')
L.append('- A V-OJVP = 2. Alt 3 if the approved third-party API counts as an explicit API route.')
L.append('')
L.append('### Firms')
L.append('- V-FRQI rel_payout = 1, resting on one open pro se complaint (an allegation). Alt 0.')
L.append('- V-FRQI rel_rules = 1. The change dates are not stated, only that the old rules were seen in Sep/Oct 2025, so they could predate the 12-month window. Alt 0.')
L.append('- V-PCDG rel_rules = 1: split cut plus fee rises. Alt 0 if fee increases are not rule changes.')
L.append('- V-PCDG, V-PCAN, V-CXFO, V-OJVP rel_payout = 0 unknown: review-site pointers only. Alt 1 for V-OJVP and V-PCDG if pointer-level denial reports count.')
L.append('- V-PCAN rel_age = 0. Alt 1 if the futures program launched in 2024 (pointer) after 2024-10-21.')
L.append('- V-PCAN rel_rules = 0. Alt 1 if the ~3% price rise, reset-fee rises on other sizes or the VPS clause (content unknown) count as a second material adverse change.')
L.append('- rel_regulatory = 0 for all five rests on search-negative results (NFA BASIC not read).')
open(B + 'F4_blind_ratings_masked.md', 'w').write('\n'.join(L) + '\n')
print('lines', len(L))
