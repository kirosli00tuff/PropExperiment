"""R1 builder: writes R1_closed_lines.json and R1_closed_lines.md from hand-entered, source-quoted facts plus
reports/stage_e32b_briefs/work/R1/members.json (made by agg_inventory.py from the E.23 inventory). Extraction only."""
import json, collections, os
B = 'reports/stage_e32b_briefs/'
M = json.load(open(B + 'work/R1/members.json'))
DEC, STG = 'docs/DECISIONS.md', 'docs/STAGES.md'

def members_of(assign, exclude_prefix=()):
    out = []
    for m in M:
        if m['assignment'] != assign or m['member_id'].startswith(exclude_prefix):
            continue
        out.append(dict(member_id=m['member_id'], roots=m['roots'], side=(m['side_kind'] or '')[:24],
                        decision=(m['decision'] or '')[:70], hold=(m['hold'] if isinstance(m['hold'], str) else str(m['hold']))[:70],
                        tiers=m['tiers'], verdict=(m['verdicts'][0] if m['verdicts'] else '')[:150]))
    return out

RES = '2025-04-01..2026-06-17'  # research-window screen span quoted per cluster below
L = []
def add(**k): L.append(k)

# ---------- ledger ladder (ledger/trial_registrations.jsonl) ----------
LADDER = [('baseline', 471, None, 'N after E.12 (198 screened + 273 Gate 0)'), ('r001-C1', 473, 2, 'C1 NG backward replication'),
 ('r002-E16', 478, 5, 'E16-H1..H5'), ('r003-C1b', 480, 2, 'C1b'), ('r004-E20H6', 483, 3, 'E20H6-T1..T3'),
 ('r005-E20S', 528, 45, 'E20S-01..45'), ('r006-E21', 532, 4, 'E21-T1..T4'), ('r007-E22', 533, 1, 'E22-F1'),
 ('r008-E23', 538, 5, 'E23 trigger-holds'), ('r009-E33', 838, 300, 'E33 ZM search')]
prev = 471
for e, n, d, _ in LADDER[1:]:
    assert n - prev == d, e; prev = n
assert prev == 838

# ---------- closed lines ----------
add(id='R1-01', type='intraday_screen_confirm', family='MES intraday program (Stage D.1, D.1a, D.1b, D.1d, D.1e, D.1f): 58 Tier A tests in 7 classes C1-C7; families A calendar/clock windows, B opening-range and breakout, C reversal and fade, D vol-regime gates and gaps, E scheduled-macro and calendar, F data-native, G bucket/price-path statistics, H NR4/NR7/inside-day ORB and prior-close follow-through',
 products=[dict(code='MES', role='traded')], horizons='from 5 minutes to the session close (A-H2 30 min; A-H1 about 60 min; B-H1 hold 5 and 75; D.1d sweep at 5/15/30/60-minute bars)',
 bar_data='ohlcv-1m MES (docs/STAGES.md:8,48); D.1d sweep at 5/15/30/60-minute bars (STAGES:38-43)',
 windows=['screens D.1/D.1a/D.1b/D.1d/D.1e: research window 2025-04-01..2026-05-13 (289 train-union dates)',
          'D.1f confirmation 2020-02-03..2024-02-29 (S = 2020-02-03, 1,055 window days); Family H never read before D.1f',
          'holdout-2 2024-04-01..2025-03-31 sealed (docs/STAGES.md:44-47)'],
 registrations=[], n_trials=58, n_note='N 31 after D.1d (STAGES:41-42); N 58 after D.1f (+21 event statistics +6 Family H); pre-ledger; baseline 471 includes them. D.1f class counts of the 58: C1 6, C2 19, C3 16, C4 6, C5 4, C6 1, C7 6 (inventory CDE.json)',
 closing=dict(decision='V38/V40 (programme level); D.1f verdict in STAGES',
  quote='no member passed confirmation (Holm rejects none of 58); C1–C5 and C7 null under docs/NULL_CRITERIA.md (C5 null by inactivity via E-H3), C6 awaits D.1g; independently verified with no discrepancy; N = 58.',
  source=STG + ':55'),
 exceptions=['MES enters later only as a leg (STAGES:65: "MES is closed and enters only as a leg")'],
 notes=['all 7 D.1d re-tests at the source grid failed; the 28-statistic 5/15/30/60-minute sweep admitted zero hypotheses (STAGES:38-43)'],
 members=members_of('CDE', ('E16',)))
add(id='R1-02', type='passive_execution', family='C6 passive execution (C-H4 reversal with resting limit orders); Stage D.1g not run', products=[dict(code='MES', role='traded')],
 horizons='n/a (reversal, passive fill)', bar_data='would have bought 181 full trade-date MBO days; not bought', windows=['none read'], registrations=[], n_trials=0, n_note='C-H4 is inside R1-01 counts; D.1g not run, no C6 null statement exists',
 closing=dict(decision='user decision 2026-09-23 ("C6 closed, Stage D.1g not run")', quote='C6, passive execution (C-H4\'s resting limit orders), is closed as non-deployable on the XFA, and Stage D.1g (a queue-position fill model on 181 purchased MBO days) will not run.', source=DEC + ':30-34'),
 exceptions=[], notes=['STAGES:56-60: "A scope decision, not a null: no C6 null statement exists."'])

def kline(i, cl, fam, prods, n, trigs, assign, stage, win, close_src, note=None):
    add(id=i, type='intraday_screen', family=fam, products=prods, horizons='intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members',
        bar_data='1-minute step bars (Stage E harness; bar-based)', windows=win, registrations=[], n_trials=n,
        n_note='counted in N 198 (STAGES ladder); ' + trigs, closing=close_src, exceptions=[], notes=note or [], members=members_of(assign))

V40 = dict(decision='V40 (and V38)', quote='Stage E\'s intraday clusters are closed (E.22 return item 3 accepted); no holdout read.', source=DEC + ':728-729')
kline('R1-03', 'K1', 'K1 equity-index screen: CP1 open-to-first-half-hour momentum port, CP2 opening-range breakout, CP3 prior-day close-location, VXN band fade, VWAP stop-and-reverse',
 [dict(code='MNQ', role='traded'), dict(code='M2K', role='traded'), dict(code='MYM', role='traded'), dict(code='NQ', role='price path/W_ext'), dict(code='RTY', role='price path/W_ext'), dict(code='YM', role='price path')], 11,
 '5 members, 11 trials on MNQ, M2K, MYM (STAGES:105-107)', 'K1', 'E.7',
 ['E.7 screen: research window 2025-04-01..2026-06-12, 299 trade dates', 'all eleven Tier B, Tier A empty; no confirmation run'], V40,
 ['K1-cp3-01 MNQ Tier B rests on four MLL-liquidated days (STAGES:106)'])
kline('R1-04', 'K2', 'K2 rates screen: CP1/CP2/CP3 ports, pre/post Treasury-auction windows, post-FOMC, ISM pre-drift, month-end', 
 [dict(code=c, role='traded') for c in ('ZT', 'ZF', 'ZN', 'TN', 'ZB', 'UB')], 44, '8 members, 44 trials (STAGES:86-88)', 'K2', 'E.3',
 ['E.3 screen: research window 2025-04-01..2026-06-17, 299 trade dates (15 roll-blackout, 2 UR-1 removed)', 'all 44 Tier B; K2 confirmation never run (STAGES:260 still lists it "planned")'], V40,
 ['K2-monthend-01 is reused at 5-day holds in R1-18', 'E.16 overlap audit (E.16_RETURN:222-229) names K2-aucpre-01/aucpost-01 as the closest tested member of E16-H3 and K2-monthend-01 of E16-H2: "related, not identical"'])
kline('R1-05', 'K3', 'K3 FX screen: CP1/CP2/CP3, London-fix reversal and momentum (ldnrev, ldnmom), ECB fix, Tokyo fix pre/post, month-end hedge', 
 [dict(code=c, role='traded') for c in ('6E', '6A', '6B', '6C', '6J', '6N', '6S')], 27, '9 members, 30 trials, 27 counted (3 excluded on coverage; STAGES:96-98; N 123 -> 150)', 'K3', 'E.4c',
 ['E.4c screen: research 2025-04-01..2026-06-17 (299 trade dates)', 'E.22 confirmation of K3-ldnrev-01 6E on 2019-05-06..2024-02-29 (1191 trade dates): null'], V40,
 ['K3-mehedge-01 on EUR not traded (no free index history); K3-ldnrev-01 6E Tier A -> E.22 null (STAGES:183)'])
kline('R1-06', 'K4', 'K4 energy screen: CP1/CP2/CP3, NG storage pre-release, API/EIA pre/post, overreaction fade', 
 [dict(code='MCL', role='traded (CL bars)'), dict(code='NG', role='traded'), dict(code='CL', role='price path')], 12, '8 members, 12 trials (STAGES:89-92)', 'K4', 'E.4a',
 ['E.4 screen: 2025-04-01..2026-06-19 (270 MCL / 269 NG dates)', 'E.5 confirmation: NG 2019-05-06..2024-02-29, MCL 2021-07-12..2024-02-29: NULL (K4-ngpre-01 fails Holm)'], V40, None)
kline('R1-07', 'K5', 'K5 metals screen: CP1/CP2/CP3, LBMA AM/PM auction windows, FOMC, overreaction fade', 
 [dict(code='MGC', role='traded (GC bars)'), dict(code='MHG', role='traded (HG bars)'), dict(code='GC', role='price path')], 9, '7 members, 11 trials in STAGES:93, 9 counted (N 114 -> 123; 3 excluded: two MHG ports, pmfix)', 'K5', 'E.4b',
 ['E.4b screen: research 2025-04-01..2026-06-17, 295 trade dates', 'E.22 confirmation K5-fomc-01 MGC W_cf 2019-05-06..2024-02-29 (1174 days): null'], V40,
 ['inventory shows 11 K5 rows, counted 9: row/counted mismatch (see ambiguities)'])
kline('R1-08', 'K6', 'K6 grains/oilseeds/livestock screen: CP1/CP2/CP3, soybean crush gap, WASDE pre/post, livestock limit continuation', 
 [dict(code=c, role='traded') for c in ('ZC', 'ZS', 'ZL', 'ZM', 'ZW', 'HE', 'LE')], 27, '7 members, 27 trials (STAGES:108-110)', 'K6', 'E.8',
 ['E.8 screen: research window 2025-04-01..2026-06-19 (264-287 dates per trial)', 'E.22 confirmation K6-limitcont-01 HE: null by inactivity (2019-05-06..2024-02-29)'], V40,
 ['K6-crushgap-01 ZS used ZM 1-minute bars as the signal leg (ZM is also R1-14/R1-21 product)'])
kline('R1-09', 'K7', 'K7 bitcoin screen: CP1/CP2/CP3, expiry, 2-hour reversal, monthly trend', [dict(code='MBT', role='traded')], 6, '6 members, 6 trials (STAGES:102-104)', 'K7', 'E.6',
 ['E.6 screen: research 2025-04-01..2026-06-17, 265 trade dates', 'all six Tier B, Tier A empty'], V40, ['K7-expiry-01 not traded (every research expiry day in a roll blackout)'])
kline('R1-10', 'K8', 'K8 cross-market screen: equity-flight into gold (H30, HEOD), oil/CAD, weekend bitcoin to NQ', 
 [dict(code='MGC', role='traded'), dict(code='MES', role='signal leg'), dict(code='6C', role='traded'), dict(code='MCL', role='signal leg'), dict(code='MNQ', role='traded'), dict(code='MBT', role='signal leg')], 4, '3 members, 4 trials (STAGES:111-114)', 'K8', 'E.9',
 ['E.9 screen: research 2025-04-01..2026-06-16 (250-280 dates)', 'E.22 confirmation: K8-flight-01 HEOD null (2020-02-04..2024-02-29, 944 dates); K8-wkndbtc-01 inconclusive by design (not run)'], V40, None)
add(id='R1-11', type='ml_search', family='ML route v2 Gate 0: Family A (64 generic signals x 3 horizons = 192 tests) and Family B (27 products x 3 horizons = 81 product-horizon tests), ridge/LightGBM design, cost-gated', 
 products=[dict(code=c, role='tested') for c in ('6A','6B','6C','6E','6J','6N','6S','HE','LE','M2K','MCL','MGC','MHG','MNQ','MYM','NG','TN','UB','ZB','ZC','ZF','ZL','ZM','ZN','ZS','ZT','ZW')],
 horizons='h60, h120, hF (minutes; hF = to flat)', bar_data='1-minute bars, 64-feature library, decision clock', windows=['training window 2019-05..2024-02 (S_X 2019-05-06; ZF 2020-10-01, ZT 2021-10-01); 1,067-1,068 dates', 'MBT no Gate 0 row; holdout-2 not read'],
 registrations=['ledger baseline (N 471); ledger/ml_v2_config_ledger.jsonl 273 entries'], n_trials=273, n_note='N 198 + 273 = 471 (reports/E.12_RETURN.md:28)',
 closing=dict(decision='V24', quote='Under the frozen V2.2b, ML route v2 stops: no phase-2 purchase, no V2.6 model, no holdout-2 registration.', source=DEC + ':449-451'),
 exceptions=['V24: "any reuse needs a new pre-registration that counts N = 471" (DECISIONS:453-454)', 'V43 reopens ML for order-book/limit-order strategies only'],
 notes=['best pair NG h60: mean gross 5.57 ticks vs c 1.71, t_B 2.51, Holm rank 1 of 273 not rejected (reports/E.12_RETURN.md:10-12)', 'pooled family B mean gross -0.72 ticks vs cost 2.26, t 0.28 (E.12_RETURN:13)'])
add(id='R1-12', type='replication', family='C1 / C1b backward NG replication (frozen ridge M1 with world-market features)', products=[dict(code='NG', role='traded'), dict(code='NQ', role='feature leg'), dict(code='ZN', role='feature leg'), dict(code='6E', role='feature leg'), dict(code='GC', role='feature leg'), dict(code='ZC', role='feature leg')],
 horizons='h60, hF', bar_data='1-minute bars (ext2010 store)', windows=['W_ext NG 2010-07..2019-04 (store 2010-06-07..2019-04-30), read once each'], registrations=['r001-C1 (2; stopped at guard C10, no statistic)', 'r003-C1b (2; evaluated once)'], n_trials=4,
 n_note='ledger: r001-C1 N 471->473; r003-C1b N 478->480', closing=dict(decision='V31 (C1 attempt closed), V32 (NG near-miss closed)', quote='C1b failed (NG h60 t_B -0.83, hF -0.41; Fable verified); the NG near-miss is closed; N is 480.', source=DEC + ':578-580'),
 exceptions=[], notes=['V31 :564 "no statistic exists; the attempt is closed" for C1', 'STAGES:160-162: T1 NG h60 mean 0.585 ticks vs bar 2.562; T2 NG hF -0.113 vs 2.649'])
add(id='R1-13', type='base_rule_batch', family='E.16 forced-flow base rules: H1 settlement-window intraday momentum (pooled), H2 month-end NQ vs ZN pair, H3 Treasury auction cycle, H4 next-day reversal of the settlement-window move, H5 equal-risk combination',
 products=[dict(code=c, role='pooled (H1/H4)') for c in ('NQ','YM','RTY','ZT','ZF','ZN','TN','ZB','UB','6E','6A','6B','6C','6J','6S','6N','CL','NG','GC','HG','ZC','ZW','ZS','ZM','ZL','LE','HE')] ,
 horizons='H1/H4 settlement-window intraday; H2 and H3 hold overnight (multi-day, personal-account venue); H5 combination', bar_data='1-minute bars', windows=['2010-07..2024-02 on the 17 W_ext roots; 2019-05-06..2024-02-29 on the 10 fallback roots (YM 6A 6B 6C 6J 6S 6N HG ZW ZM)'],
 registrations=['r002-E16 (E16-H1..H5; 5)'], n_trials=5, n_note='N 473 -> 478',
 closing=dict(decision='V31', quote='The base-rule batch H1 to H5 is closed: all five failed (H1\'s gross is about a quarter of its D8 cost; H2 positive at p 0.068, not a pass); no rerun or variant on these windows, no purchase of the 10 fallback roots, no holdout-2 read.', source=DEC + ':568-571'),
 exceptions=['H2 (month-end NQ/ZN) noted as a personal-account candidate only, not pursued (V33 item 4, DECISIONS:608)'], notes=['H3 roots not extracted (Treasury tenors per E.16 freeze)', 'E.16 overlap audit closest tested members: H1 CP1 port, H2 K2-monthend-01, H3 K2-aucpre/aucpost-01, H4 CP3 port, H5 none (E.16_RETURN:222-229)', 'ambiguous: for lead: V28 (DECISIONS:524) says H2 and H3 hold overnight; E.16 overlap audit lists their closest members as intraday-only', 'DSR at N=478: all about 0 (E.17_RETURN:575)'])
add(id='R1-14', type='intraday_test', family='H6 rest-of-day to last-half-hour momentum on NQ (Baltussen, Da, Lammers, Martens 2021): T1 always, T2 above trailing |r_ROD| median, T3 negative prior-day GEX', products=[dict(code='NQ', role='traded (MNQ cost)')],
 horizons='last half hour (about 30 min), entry at 14:30 CT', bar_data='1-minute NQ step2 store', windows=['2020-06-01..2024-02-29 (GEX rows 2020-05-29..2024-02-28), run once'], registrations=['r004-E20H6 (3)'], n_trials=3, n_note='N 480 -> 483',
 closing=dict(decision='V38', quote='The intraday program on Topstep is closed: nothing in 528 trials passed', source=DEC + ':678-679'), exceptions=[], notes=['T1 gross 1.25 ticks vs 4.08 cost, t -0.53 (STAGES:172-173)', 'reversal direction reused at 5/20-day holds in R1-18'], members=members_of('H6'))
add(id='R1-15', type='ml_search', family='E.20 Part C ML pattern search: ridge and shallow LightGBM, 45 configurations, extra decision time t4 = F_X - 60 min, r_ROD features', products=[dict(code=c, role='searched') for c in ('NQ','RTY','ZT','ZF','ZN','TN','ZB','UB','6E','CL','NG','GC','ZC','ZS','ZL','LE','HE')],
 horizons='h60, h120, hF', bar_data='1-minute step2 stores, 36 features', windows=['2019-05-06..2024-02-29 (nested CPCV, 57,775 decision rows); backward 2010-2019 read not run'], registrations=['r005-E20S (E20S-01..45; 45)'], n_trials=45, n_note='N 483 -> 528',
 closing=dict(decision='V38', quote='nothing in 528 trials passed, and no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip (E.20 Part A, 157 evidence rows)', source=DEC + ':679-681'),
 exceptions=['V45 item 4 amends the sentence: three working-paper effects (see R1-19)'], notes=['all 45 configurations negative out of sample; median-path t -1.33, PBO 0.60, net Sharpe -0.83 (STAGES:172-174)', 'E.20 Part A: 17 root readers, 0 features accepted'])
add(id='R1-16', type='multiday', family='E.21 multi-day: T1 12-month TSMOM (MOP 2012), T2 1/3/12-month trend blend (HOP 2017), T3 equity turn of the month, T4 equal-risk book with H2', products=[dict(code=c, role='traded') for c in ('NQ','RTY','ZT','ZF','ZN','TN','ZB','UB','6E','CL','NG','GC','ZC','ZS','ZL','LE','HE')],
 horizons='monthly/multi-day (T3 turn of month on NQ and RTY)', bar_data='daily/settlement paths from owned 1-minute stores', windows=['2010-2024 owned data (E.21 return: AQR comparison 2010-07..2024-02)'], registrations=['r006-E21 (4)'], n_trials=4, n_note='N 528 -> 532',
 closing=dict(decision='V39', quote='Trend is recorded as consistent with the published evidence, not established by this program\'s bar; no further trend variant on 2010-2024.', source=DEC + ':697-699'),
 exceptions=[], notes=['T1 net Sharpe 0.50 [-0.06, 1.05], t 1.78, p 0.042; T2 0.44; T3 0.15; T4 0.12; all FAIL on Holm 0.025 (STAGES:177-180)', 'V39: no ML overlay on trend built (DECISIONS:709)'])
add(id='R1-17', type='forward_registered_parked', family='E22-F1 micro trend book forward test at USD 25,000 (E.21 trend rule on 12 micros)', products=[dict(code='MICROS12', role='12 micros on E.21 owned paths (list in the E.22 freeze; not extracted)')],
 horizons='daily', bar_data='daily settlement', windows=['forward test, 36 months from the first ledger record after a settlement source is approved; warm-up read approved in V42 (2024-03-01 to start)'], registrations=['r007-E22 (1)'], n_trials=1, n_note='N 532 -> 533',
 closing=dict(decision='V43 (parked), not a closing', quote='no paper trading for now and no 24/7 gateway on the laptop (E22-F1, E22-F1b, E22-F2 and any C1 forward record parked, unregistered, N 538)', source=DEC + ':804-806'),
 exceptions=[], notes=['ambiguous: for lead: V43 says "unregistered" while the ledger holds r007-E22 (N 533)'])
add(id='R1-18', type='multiday', family='E.23 program triggers at 5- and 20-day holds (entered at the trigger day\'s settlement; alpha over E.21 trend returns): K2-monthend-01 long ZF/ZN/ZB at 5 days; E20H6-T1 reversal on NQ at 5 and 20 days', products=[dict(code='ZF', role='traded'), dict(code='ZN', role='traded'), dict(code='ZB', role='traded'), dict(code='NQ', role='traded')],
 horizons='5 and 20 trading days', bar_data='daily from owned stores', windows=['discovery W_ext 2011-07-27..2019-04-30, read once', 'confirmation W_cf 2019-05..2024-02 not computed (power 0.18)'], registrations=['r008-E23 (E23-MEZFh5, MEZNh5, MEZBh5, H6NQh5, H6NQh20; 5)'], n_trials=5, n_note='N 533 -> 538',
 closing=dict(decision='V41', quote='"The program\'s intraday triggers at multi-day holds" is closed as a direction; no variant (other roots, other holds, the opposite H6 direction) is tested on these windows.', source=DEC + ':749-751'),
 exceptions=['W_cf (2019-05..2024-02, trigger-conditional multi-day outcomes unread) and holdout-2 kept for a hypothesis with a stronger prior (DECISIONS:751-754)'], notes=['alpha t 0.55/0.38/0.10/-1.61/-0.71; Holm smallest p 0.31 (STAGES:194-195)', 'the month-end gain is the bonds\' drift'])
add(id='R1-19', type='intraday_closure_umbrella', family='Intraday program closure with its exceptions (E.20 Part A literature, 17 roots, 157 evidence rows; re-dug in E.25)', products=[dict(code=c, role='scope') for c in ('NQ','RTY','ZT','ZF','ZN','TN','ZB','UB','6E','CL','NG','GC','ZC','ZS','ZL','LE','HE')],
 horizons='intraday', bar_data='published-effect census, no data read', windows=['n/a'], registrations=[], n_trials=0, n_note='covers 528 trials at V38 (N 538 later)',
 closing=dict(decision='V38 as amended by V45 item 4', quote='no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip, except three working-paper effects whose samples run past 2015, none with a significant post-2015 estimate', source=DEC + ':910-916'),
 exceptions=['V45: pre-refunding-announcement ZN gain (Wang and Zhao 2025, cash, +12.62 bp, t 3.32)', 'V45: pre-FOMC ZN drift (Pan and Peng 2026, futures, +7.26 bp, t 2.82, 2004-01..2025-06)', 'V45: ES 3rd-Friday reversal (Baltussen, Terstegge and Whelan, -12.89 bp, t -2.40, 2003-2021; 2015-23 not significant alone)', 'V45: "Each gives 3 to 15 events in the research window (power 0.11 to 0.22 at the published sizes), so none can be tested with adequate power on owned data." (DECISIONS:919-921)'],
 notes=['quote of the closure end: "The closure of the intraday program (V38) stays in place." (DECISIONS:922)', 'E.25 shortlist also named noise-area intraday momentum on MNQ (V34 item 4 had dropped it as "unsized"); never tested (reports/E.25_RETURN.md:13,29)'])
add(id='R1-20', type='passive_execution_measured', family='Passive spread capture at the touch, one lot, trade-through fills (E.31 ZM order-book pilot); covers ZM, QM (frozen QM pilot never bought) and ZL follow-up (skipped)', products=[dict(code='ZM', role='measured'), dict(code='QM', role='closed by decision, not measured'), dict(code='ZL', role='closed by decision, skipped'), dict(code='ZS', role='conditioning data (MBP-1)')],
 horizons='10 s markout per fill', bar_data='ZM MBO (front two months), ZS and ZL MBP-1; 156 files, 24.2 GB', windows=['2020-12..2024-02 (39 whole months; 816 trade dates measured, 764 DAY dates usable)', 'nothing on or after 2024-03-01'], registrations=['none (nothing registered; N 538)'], n_trials=0, n_note='E.31 registered nothing',
 closing=dict(decision='V50', quote='Passive spread capture at the touch with a one-lot at prop-firm simulators is closed. This covers ZM, QM (E.28\'s frozen QM pilot is closed, never bought) and the ZL follow-up of V49 (skipped). E.29 D2 (baskets around ZM) is not run.', source=DEC + ':1034-1037'),
 exceptions=['V50 item 2: "Limit orders stay allowed as an execution method for a directional signal. They are not a source of edge in themselves."', 'V56 item 2: limit orders as execution of a directional signal stay open; "Order-book direction is not closed for other products." (DECISIONS:1149-1152)'],
 notes=['ZM front-month DAY 10 s edge net of Topstep fee -1.234 ticks [-1.252, -1.214]; gross -0.970; K-algorithm -0.29, FIFO -0.25 gross (E.31_RETURN:20-27)', 'V50 item 4: E.31 read these dates for passive-fill markouts incl. queue-imbalance splits; "Any test of an order-flow signal on these dates is therefore not a clean holdout." (DECISIONS:1046-1050)', 'V49 item 2: MGC out of passive spread capture (fee 1.5-2.2 ticks vs 1-tick maximum capture): decision, not measurement; MGC kept "only as a possible directional test"'])
add(id='R1-21', type='directional_search', family='ZM directional 5-60 minute search, five feature sets: S1 crush residual, S2 cross-asset propagation from ZS and ZL, S3 ZM order flow and book state, S4 ZM own price path, S5 all four pooled; x 6 labels x 10 model settings (6 regularised multinomial logits, 4 shallow LightGBM)', products=[dict(code='ZM', role='traded'), dict(code='ZS', role='input'), dict(code='ZL', role='input')],
 horizons='fixed horizons 5, 15, 30, 60 minutes; triple barrier at 15 and 30', bar_data='ZM MBO plus ZS/ZL MBP-1 (order-book schemas), 59 features, Topstep market orders 1 s latency, fee 0.528 tick', windows=['796 out-of-fold dates 2020-12-30..2024-02-29, 6 blocked folds, 21-date embargo', 'test window 2017-05-01..2020-11-30 sealed, unread'], registrations=['r009-E33 (300 configurations)'], n_trials=300, n_note='N 538 -> 838',
 closing=dict(decision='V56', quote='ZM\'s directional route at 5-60 minute holds is closed. There is no E.34 and no purchase. The 2017-05..2020-11 window stays sealed for a future hypothesis family.', source=DEC + ':1146-1148'),
 exceptions=['V56 item 2: order-book direction not closed for other products; limit orders as execution of a directional signal stay open'], notes=['Tier A empty; best loses 1.098 ticks/trade; best daily Sharpe 0.0478 vs binding 0.2007; DSR at most 0.025; BH and Holm reject 0; PBO 0.14 (E.33c_RETURN:15-31)', '61 of 300 met G1 (all lose over 1.0 tick/trade); 8 averaged at least 0.5 tick on at most 55 trades', 'minimum detectable edge 1.5-4.4 ticks/trade at the trade rates seen (E.33c_RETURN:355-357)', 'E.33c: "not a null statement in the program\'s sense"; no statement for all five sets'])
add(id='R1-22', type='product_decision', family='NQ dropped for the passive limit-order direction', products=[dict(code='NQ', role='dropped')], horizons='n/a', bar_data='n/a', windows=['none read'], registrations=[], n_trials=0, n_note='decision from E.28 ranks 33, 45, 52, 54, 62',
 closing=dict(decision='V49 item 1', quote='NQ is dropped as a candidate at every firm (E.28 ranks 33, 45, 52, 54 and 62), despite Topstep\'s 0.44-tick break-even. Reasons: very long queues and HFT competition ... Topstep\'s Tier 1 news windows block NQ. NQ is not used as a pilot or comparison contract.', source=DEC + ':1010-1016'),
 exceptions=[], notes=['ambiguous: for lead: V49 is headed "For the passive limit-order direction (V43, E.28)"; its scope for directional market-order use of NQ is not stated. Ranking spec section 0 treats NQ as "excluded (V49)"', 'NQ appears in other closed lines: R1-03 (price path of MNQ), R1-12 (feature leg), R1-13, R1-14, R1-15, R1-16, R1-18'])
add(id='R1-23', type='closed_directions_no_trials', family='Directions closed by the user without a program trial: prediction markets; crypto; commodity event drift as a standalone stage; ML overlay on trend; C2 GEX late-session momentum stopped before freeze', products=[dict(code='MBT', role='crypto direction (K7 screened, R1-09)'), dict(code='CRUDE_METALS_NATGAS', role='commodity event drift direction, no product list given')],
 horizons='n/a', bar_data='n/a', windows=['none read'], registrations=[], n_trials=0, n_note='C2 stopped at its power rule, N unchanged',
 closing=dict(decision='V39 (and V27 for C2)', quote='Closed as directions: prediction markets (user), crypto (every prior crypto line closed negative across the user\'s projects), commodity event drift as a standalone stage (planning research: geopolitical news is priced fast, OPEC drift has decayed; at most an overlay on trend).', source=DEC + ':702-706'),
 exceptions=['V39: small caps "marginal ... not run now" (DECISIONS:706-709): not closed', 'V27: C2 "stays stopped with no rerun planned" (DECISIONS:499-501)'], notes=['ambiguous: for lead: V27 says C2 stopped at its power rule before its freeze (135 eligible negative-GEX dates, floor 200); a stop, not a test'])

# ---------- other standing constraints (not closed lines) ----------
CONSTRAINTS = [
 dict(id='V28', text='No deep network, reinforcement learning or other ML layer goes onto a rule set that has not passed a pre-registered test', source=DEC + ':509-512', note='amended by V33 item 5 (E.20) and V43 (order-book/limit-order ML may itself be the strategy)'),
 dict(id='V31', text='cost-feasibility gate: every future hypothesis states expected gross per trade from published evidence against the D8 round-trip cost and is dropped if it does not clear the pass multiple', source=DEC + ':571-576'),
 dict(id='V33', text='No Combine is bought until a strategy passes a registered test and its follow-up reads with a net Sharpe of about 0.5 or more', source=DEC + ':596-598'),
 dict(id='V51', text='ZM test window 2017-05-01..2020-11-30 sealed by E.32 Part 0, covers every schema; 2024-03 onward closed unless the user approves', source=DEC + ':1062-1067'),
]

# ---------- invariants ----------
cnt = collections.Counter(l['type'] for l in L)
pre = sum(l['n_trials'] for l in L if l['id'] in ('R1-01',))
k = sum(l['n_trials'] for l in L if l['id'] in ('R1-03','R1-04','R1-05','R1-06','R1-07','R1-08','R1-09','R1-10'))
assert k == 140, k
sumall = pre + k + sum(l['n_trials'] for l in L if l['id'] in ('R1-11','R1-12','R1-13','R1-14','R1-15','R1-16','R1-17','R1-18','R1-21'))
assert sumall == 838, sumall

# ---------- lookup tables ----------
by_prod = collections.defaultdict(list)
for l in L:
    for p in l['products']:
        by_prod[p['code']].append((l['id'], p['role']))
CODES47 = 'MCL QM CL MNG QG NG MGC GC SIL SI MHG HG M6E 6E M6A 6A MET ETH MBT BTC M2K RTY MYM YM MNQ NQ 2YY 5YY 10Y 30Y ZT ZF ZN ZB MZC MZS MZW MZL MZM XC XK XW ZC ZS ZW ZL ZM'.split()
assert len(CODES47) == 47
OTHER = ['ES', 'MES', 'TN', 'UB', '6B', '6C', '6J', '6S', '6N', 'HE', 'LE']
GROUPS = [('MCL','QM','CL'),('MNG','QG','NG'),('MGC','GC'),('SIL','SI'),('MHG','HG'),('M6E','6E'),('M6A','6A'),('MET','ETH'),('MBT','BTC'),
          ('M2K','RTY'),('MYM','YM'),('MNQ','NQ'),('MZC','XC','ZC'),('MZS','XK','ZS'),('MZW','XW','ZW'),('MZL','ZL'),('MZM','ZM'),('MES','ES')]  # spec section 0 "same underlying"
GRP = {c: g for g in GROUPS for c in g}
def row(c):
    lines = by_prod.get(c, [])
    d = [(i, r) for i, r in lines]
    sibs = [x for x in GRP.get(c, ()) if x != c]
    sl = sorted({i for x in sibs for i, _ in by_prod.get(x, [])} - {i for i, _ in d})
    return dict(code=c, lines=[dict(line=i, role=r) for i, r in d], siblings=sibs, sibling_lines=sl)
PROD_TABLE = {'codes47': [row(c) for c in CODES47], 'other_roots': [row(c) for c in OTHER]}
extra = sorted(set(by_prod) - set(CODES47) - set(OTHER))
PROD_TABLE['unlisted_in_either'] = [row(c) for c in extra]

FAM = [
 ('Opening-range / breakout momentum (CP2 port; MES B-H1,B-H3,B-H4, Family H NR4/NR7/inside-day ORB)', ['R1-01','R1-03','R1-04','R1-05','R1-06','R1-07','R1-08','R1-09'], 'members *-cp2-01 on every K cluster; MES B-*, H1-H5'),
 ('Open-to-first-half-hour / overnight-to-decision momentum into the close (CP1 port; E20 H6 rest-of-day; E16-H1 settlement-window)', ['R1-01','R1-03','R1-04','R1-05','R1-06','R1-07','R1-08','R1-09','R1-13','R1-14'], '*-cp1-01; H6 T1-T3; E16-H1,H4'),
 ('Prior-day close-location continuation or reversal (CP3 port; MES C-H3)', ['R1-01','R1-03','R1-04','R1-05','R1-06','R1-07','R1-08','R1-09'], '*-cp3-01; MES C-H3'),
 ('Overreaction / spike fade after an intraday move (ovr, C-H1,C-H2, VXN band)', ['R1-01','R1-03','R1-06','R1-07'], 'K4-ovr-01, K5-ovr-01, K1-vxnband-01, MES C-H*'),
 ('Scheduled macro / event windows: FOMC, Treasury auctions, ISM, API/EIA, NG storage, WASDE, LBMA fix, ECB/Tokyo fix', ['R1-01','R1-04','R1-05','R1-06','R1-07','R1-08'], 'K2 aucpre/aucpost/fomcpost/predrift; K3 ldnrev/ldnmom/ecbfix/tky*; K4 ngpre/apipre/eia*; K5 preauc/pmfix/fomc; K6 wasde*'),
 ('Calendar: month-end, turn of the month, weekend, overnight / European-open drift', ['R1-01','R1-04','R1-13','R1-16','R1-18'], 'K2-monthend-01; E16-H2; E21 T3; MES A-H1,A-H3,E-H4'),
 ('Volatility-regime gates, range compression, gaps, sizing', ['R1-01','R1-03'], 'MES D-H1..D-H4; K1-vxnband-01'),
 ('Cross-market relationships: equity flight to gold, oil/CAD, weekend bitcoin, soybean crush gap', ['R1-08','R1-10'], 'K8-*; K6-crushgap-01'),
 ('Crypto (MBT) rules', ['R1-09','R1-10'], 'K7-*; K8-wkndbtc-01'),
 ('ML pooled-feature or model search at 60 minutes, 120 minutes, to flat', ['R1-11','R1-12','R1-15','R1-21'], 'Gate 0 (192+81), C1/C1b M1, E20S-01..45, E33 logit/LightGBM'),
 ('Trend / TSMOM / trend blend and equity turn of month (multi-day)', ['R1-16','R1-17','R1-18'], 'E21 T1-T4, E22-F1, E23'),
 ('Intraday triggers held 5 and 20 days', ['R1-18'], 'E23-MEZFh5/MEZNh5/MEZBh5/H6NQh5/H6NQh20'),
 ('Passive spread capture / resting limit orders (one lot, trade-through)', ['R1-02','R1-20'], 'C-H4/C6; E.31 ZM pilot; QM and ZL by decision'),
 ('Order flow and book state on ZM at 5-60 minutes; crush residual; ZS/ZL propagation; own price path', ['R1-21'], 'E33 sets S1-S5'),
 ('Published-effect census on 17 roots (intraday)', ['R1-15','R1-19'], 'E.20 Part A, E.25 re-dig'),
]

OUT = dict(schema='R1_closed_lines/1', generated_pdt=os.popen('TZ=America/Vancouver date +"%Y-%m-%d %H:%M:%S %Z"').read().strip(),
 sources=[DEC, STG, 'reports/stage_e23_briefs/inventory_compact.txt', 'reports/stage_e23_briefs/inventory/*.json', 'ledger/trial_registrations.jsonl', 'reports/E.33c_RETURN.md', 'reports/E.31_RETURN.md', 'reports/E.12_RETURN.md', 'reports/E.17_RETURN.md', 'reports/E.25_RETURN.md', 'reports/stage_e12_gate0.json', 'reports/stage_e20_search_freeze.json'],
 ledger_ladder=[dict(entry=e, n_after=n, trials_added=d, note=t) for e, n, d, t in LADDER],
 n_total=838, trials_by_line={l['id']: l['n_trials'] for l in L}, lines=L, standing_constraints=CONSTRAINTS, lookup_by_product=PROD_TABLE,
 lookup_by_family=[dict(family=f, lines=ls, members=m) for f, ls, m in FAM], type_counts=dict(cnt))
json.dump(OUT, open(B + 'R1_closed_lines.json', 'w'), indent=1)
print('lines', len(L), dict(cnt), 'N', sumall, 'unlisted codes', extra)

# ---------------- markdown ----------------
AMB = [
 'V49 scope (R1-22): headed "For the passive limit-order direction"; whether NQ is closed for directional market-order use is not stated.',
 'V38 scope (R1-15, R1-19): V38 says "intraday program on Topstep is closed"; V45 item 4 says "closure of the intraday program (V38) stays in place" without "on Topstep".',
 'V39 / V41 scope (R1-16, R1-18): "no further trend variant on 2010-2024" and "no variant ... tested on these windows" bind windows; V41 keeps W_cf and holdout-2 for a stronger prior.',
 'V43 vs ledger (R1-17): V43 calls E22-F1 "parked, unregistered, N 538"; ledger r007-E22 registered it (N 533). It has no outcome; counted in N, not a closed line.',
 'E.25 shortlist (R1-19): noise-area MNQ (V34 item 4 dropped it as "unsized"), the 3rd-Friday spike and the two ZN drifts were never tested; V45 lists the last three as exceptions to V38. Closed or open is for the lead.',
 'V27 (R1-23): C2 GEX late-session momentum stopped at its power rule before any test; "stays stopped with no rerun planned".',
 'docs/STAGES.md:260 still lists "Stage E.3b onward" (K2 confirmation and later cluster confirmations) as planned; V40 (DECISIONS:728-729) closes Stage E intraday clusters. K1, K2, K3 (except ldnrev), K6 (except limitcont), K7 had no confirmation.',
 'Counts: K5 inventory has 11 rows, STAGES counts 9 trials (N 114 -> 123); K3 30 rows vs 27 counted; K6 inventory excludes 4 of 27 though 27 counted. N ladder (STAGES) used for counts.',
 'E16-H2/H3: V28 (DECISIONS:524) says they hold overnight; E.16 overlap audit names intraday K2 members as closest.',
 'MES/ES/other roots are outside the 47-code universe (spec section 0) but are closed lines R1-01, R1-10 (leg).',
]
OUT['ambiguities_for_lead'] = AMB
json.dump(OUT, open(B + 'R1_closed_lines.json', 'w'), indent=1)

def wrap(t, w=150):
    import textwrap
    return textwrap.wrap(t, w)
md = []
md.append('# R1 closed lines (Stage E.32b, spec section 8.1) - extraction by ClosedLines-SonnetHigh, ' + OUT['generated_pdt'])
md.append('Full fields (members, all quotes) in R1_closed_lines.json. Facts only; no judgment on overlap. Times PDT. N = 838 (ledger).')
md.append('')
md.append('## Ledger ladder (ledger/trial_registrations.jsonl; the file has no family/product/window fields, only ids, freeze files, N)')
md.append('baseline 471 (198 screened + 273 Gate 0); ' + '; '.join('%s +%d -> %d' % (e, d, n) for e, n, d, _ in LADDER[1:]) + '. Pre-ledger parts: D.1-D.1f 58, K clusters 140, Gate 0 273.')
md.append('Trials per line: ' + ', '.join('%s %d' % (k, v) for k, v in OUT['trials_by_line'].items() if v) + ' (sum 838; R1-02, 19, 20, 22, 23 add no trials).')
md.append('')
md.append('## Closed lines (23; types: ' + ', '.join('%s %d' % kv for kv in cnt.items()) + ')')
for l in L:
    md.append('### %s [%s] %s' % (l['id'], l['type'], l['family']))
    md.append('- products: ' + ', '.join('%s (%s)' % (p['code'], p['role']) for p in l['products']))
    md.append('- horizons: %s | data: %s | windows: %s' % (l['horizons'], l['bar_data'], ' ; '.join(l['windows'])))
    md.append('- registrations: %s | trials %d | %s' % ('; '.join(l['registrations']) or 'none', l['n_trials'], l['n_note']))
    c = l['closing']
    md.append('- closing: %s, %s: "%s"' % (c['decision'], c['source'], c['quote']))
    if l['exceptions']:
        md.append('- exceptions: ' + ' | '.join(l['exceptions']))
    if l['notes']:
        md.append('- notes: ' + ' | '.join(l['notes']))
    if l.get('members'):
        md.append('- members: %d rows in JSON (member_id, roots, side, decision time, hold, tier, verdict)' % len(l['members']))
md.append('')
md.append('## Standing decisions that are constraints, not lines')
for c in CONSTRAINTS:
    md.append('- %s (%s): %s%s' % (c['id'], c['source'], c['text'], ('; ' + c['note']) if c.get('note') else ''))
md.append('')
md.append('## Lookup by product (role in line; siblings = other codes on the same underlying per spec section 0, with the extra lines they add)')
empty = []
for grp, rows in (('47 codes', PROD_TABLE['codes47']), ('other roots', PROD_TABLE['other_roots'])):
    for r in rows:
        if not r['lines'] and not r['sibling_lines']:
            empty.append(r['code']); continue
        md.append('- %s: %s%s' % (r['code'], ', '.join('%s %s' % (x['line'], x['role'].split(' (')[0]) for x in r['lines']) or 'none',
                  ('; siblings %s add %s' % ('/'.join(r['siblings']), ','.join(r['sibling_lines']))) if r['sibling_lines'] else ''))
md.append('- No closed line touches (directly or via a same-underlying code): ' + ', '.join(empty))
md.append('')
md.append('## Lookup by family or mechanism')
for f in OUT['lookup_by_family']:
    md.append('- %s -> %s [%s]' % (f['family'], ','.join(f['lines']), f['members']))
md.append('')
md.append('## Ambiguous: for lead')
for a in AMB:
    md.append('- ' + a)
open(B + 'R1_closed_lines.md', 'w').write('\n'.join(md) + '\n')
print('md lines', len(md))
