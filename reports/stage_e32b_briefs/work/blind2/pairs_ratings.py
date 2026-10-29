import json
d = json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_firms.json'))
P = d['pairs']
def ids(p, *whats):
    out = [it['id'] for it in p['R_facts'] if any(w in it['what'] for w in whats)]
    return ' '.join('[%s]' % i for i in out)
A = {
 'V-FRQI': (3, "Automation allowed with conditions in evaluation [I-9769025] and funded stage [I-3314598] via the firm's own API [I-3907697]; 200 requests/60 s is the API's technical limit [I-7099737]; HFT ban and SIM-exploitation examples ('hundreds or thousands of trades per day', durations in seconds) [I-5638304] are met by <=20 round trips and >=5-min holds; terms cite 'any short term or high frequency trades' as manipulation, undefined [I-0756007]; live-stage API ban [I-9602515] binds the live stage, outside the modelled evaluation/funded stages"),
 'V-PCDG': (2, "Automated systems permitted firm-wide, both stages [I-4833405] [I-6857903], but no firm API documented [I-9452038]: automation only through named third-party platforms [I-5051875]; HFT ban qualitative [I-8635517] and microscalping flag (>50% of profit from <=5 s holds) [I-5700661] are met by the strategy"),
 'V-PCAN': (2, "Own non-HFT bots allowed in evaluation and funded [I-6910816], but the named platform's API is live-stage only, not available in evaluation or sim funded [I-9347528]: automation only through named third-party platforms [I-2445725]; 10-s hold payout gate (funded) is met [I-6411270]"),
 'V-CXFO': (2, "Automated strategies allowed in evaluation and sim funded if not exploiting sim fills [I-2061108]; no firm API documented, accounts on a named third-party platform (API enablement unverified) [I-1831125]; HFT ban undefined [I-1723467]; no order-rate or min-hold rule [I-1701644] [I-0205563]"),
 'V-OJVP': (2, "User-built bots allowed in both stages [I-0851366]; API only through a named platform via an approved third-party API or interface, $100/month [I-1718685] [I-9983562]; third-party algorithms need management approval [I-7874036]; 'scalping algorithms' and 'hundreds or thousands of rapid trades' banned, undefined [I-9884997] (<=20 round trips, >=5-min holds should meet it)"),
}
FRQI_NEWS_BLOCK = {'K-FICQ', 'K-QAJV', 'K-KVJD', 'K-LGJM'}
FRQI_NEWS_CAP = {'K-RISF', 'K-DNXQ', 'K-YEPF', 'K-NYZZ', 'K-OEVC', 'K-SLBV'}
CRYPTO_LISTED_FLAG = {'K-UQNU', 'K-ZXJD', 'K-JGJF', 'K-OJGY'}
CXFO_RESTRICTED = {'K-AAUT', 'K-YBWI', 'K-YJXE', 'K-DLUC'}
out = {}; alts = {}
for pk, p in P.items():
    f, c = pk.split('|')
    listed = p['listed_on_modelled_plan']
    rid = ids(p, 'restrictions recorded', 'news window', 'product cap', 'trading hours')
    if not listed:
        alt = 4
        extra = ''
        if f == 'V-FRQI' and c in ('K-AAUT', 'K-YBWI'):
            alt = 1; extra = '; 50K volatility cap 0 contracts'
        if f == 'V-CXFO' and c in CXFO_RESTRICTED:
            alt = 1; extra = '; product restricted from trading (temporary, since 2026-02-07)'
        R = (1, "Not listed on the modelled 50K plan (listed_on_modelled_plan false): not tradable there, so all exchange hours are excluded%s %s" % (extra, rid))
        alts[pk] = ('R', alt, 'if listing is treated as a separate gate, the stated restrictions alone give %d' % alt)
    elif f == 'V-FRQI' and c in FRQI_NEWS_BLOCK:
        R = (3, "No new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press conference, NFP and PPI (evaluation and funded); usually <=2 such events a week; 50K cap allows a one-lot; other rules firm-wide %s" % rid)
        alts[pk] = ('R', 2, 'a week holding CPI, PPI and an FOMC decision and press conference has more than 2 windows')
    elif f == 'V-FRQI' and c in FRQI_NEWS_CAP:
        R = (4, "Tier 1 window only caps opening size for this product (one lot still allowed at 50K, funded balance tiers allow >=1); 50K cap allows a one-lot; otherwise firm-wide rules only %s" % rid)
        alts[pk] = ('R', 3, 'if the Tier 1 size cap counts as a restriction around <=2 scheduled events a week')
    elif f == 'V-CXFO':
        R = (4, "Plan P1 50K is an unrestricted account for Tier 1 news in evaluation and sim funded; no product-specific restriction; price-limit, hedging and news-burst bans and the 16:10 ET flat are firm-wide %s" % rid)
        if c in ('K-SGKW', 'K-PXYN', 'K-LRVK'):
            alts[pk] = ('R', 1, 'conflicting page lines ("no open positions or orders 2 minutes before and after any data release"; Tier 1 trading "restricted"): with EIA weekly plus Tier 1 macro this combines the 2 and 3 cases')
        elif c in ('K-OQCY', 'K-IXHJ', 'K-AJZH', 'K-ODAS', 'K-KQRO'):
            alts[pk] = ('R', 1, 'conflicting page lines: agricultural reports (weekly in season) plus Tier 1 macro would combine the 2 and 3 cases')
        else:
            alts[pk] = ('R', 3, 'conflicting page lines ("no open positions or orders 2 minutes before and after any data release"): Tier 1 macro windows only')
    else:
        R = (4, "Listed; no news window and no product-specific restriction on the modelled plan; caps allow a one-lot; flat-by time is firm-wide %s" % rid)
        if f == 'V-FRQI':
            R = (4, "Listed; not affected by the Tier 1 news rule; caps allow a one-lot; flat-by 15:10 CT, early-close and outside-BBO rules are firm-wide %s" % rid)
    if listed and c in CRYPTO_LISTED_FLAG and pk not in alts:
        alts[pk] = ('R', 1, "the firm's weekday-only hours exclude about a third of the 24/7 exchange hours this product has had since 2026-05-29 (contract sheet), if firm-wide hours count")
    a = A[f]
    out[pk] = {'R': {'value': R[0], 'unknown': False, 'reason': R[1]}, 'A': {'value': a[0], 'unknown': False, 'reason': a[1]}}
assert len(out) == 235
json.dump(out, open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/blind2/r_pairs.json', 'w'), indent=1)
json.dump(alts, open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/blind2/r_pairs_alts.json', 'w'), indent=1)
import collections
print('pairs', len(out), 'R values', collections.Counter(v['R']['value'] for v in out.values()), 'A values', collections.Counter(v['A']['value'] for v in out.values()), 'alts', len(alts))
