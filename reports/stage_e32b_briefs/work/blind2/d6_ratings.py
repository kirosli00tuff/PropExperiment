import json
def r(v, reason, unk=False, unv=None):
    d = {"value": v, "unknown": unk, "reason": reason}
    if unv is not None: d["unverified"] = unv
    return d
P = "data span runs across 2010 with no post-2010 split, so not 'on data after 2010': 3 not 4"
crude = "Own-contract full-text test is a null (rest-of-day -> last half hour beta 0.67, t 0.25, R2_OOS -1.04%%, 1987-2020) %s; own-contract positives are abstract-only (EIA-day 10:20-10:25 strategy) %s; best full-text positives are another venue (USO, in sample, gross) %s and the asset class pooled (energies R2_OOS 0.20%%) %s: 2"
ng = "Peer-reviewed rest-of-day -> last half hour on %s: beta 3.02 (t 6.15), R2_OOS 0.92%%, recursive out of sample, 1993-2020, gross %s; pre-release drift strategy Sharpe 0.84, 2008-2016, in sample %s; %s; conflicting: storage-day (-90,+30) short insignificant and net negative after 2011 %s"
D = {
 "K-LRVK": r(2, crude % ("[I-3243046]", "[I-9449433]", "[I-0611503]", "[I-2304534]")),
 "K-SGKW": r(2, crude % ("[I-2207953] (sibling)", "[I-4130273]", "[I-1059550]", "[I-5806304]")),
 "K-PXYN": r(2, crude % ("[I-1122719] (sibling)", "[I-1991501]", "[I-8228239]", "[I-8792934]")),
 "K-YJXE": r(3, ng % ("this contract", "[I-4274394]", "[I-3021761]", P, "[I-3602224]")),
 "K-LIRS": r(3, ng % ("the same-underlying sibling", "[I-0469863]", "[I-3892370]", P, "[I-9061655]")),
 "K-DLUC": r(3, ng % ("the same-underlying sibling", "[I-8657607]", "[I-6546948]", P, "[I-9805308]")),
 "K-LGJM": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 1.09 (t 2.95), R2_OOS 0.08%** (out of sample), 1984-2020, gross [I-9618474] [I-0551449]; " + P + "; fix-window pattern significant only 2007-11 and below spread costs (thesis) [I-2693041]; overreaction study uses ex-post turning points, not counted [I-3455534]"),
 "K-NYZZ": r(3, "Same-underlying sibling: rest-of-day -> last half hour beta 1.09 (t 2.95), R2_OOS 0.08%**, 1984-2020, gross [I-8014730]; " + P + "; fix pattern decayed after 2011 (thesis) [I-3545836]"),
 "K-AAUT": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 2.93 (t 5.44), R2_OOS 1.01%***, 1983-2020, gross [I-7677851]; fixing-window price drop 2000-2013, in sample, gross [I-2351131]; " + P),
 "K-OEVC": r(3, "Same-underlying sibling: rest-of-day -> last half hour beta 2.93 (t 5.44), R2_OOS 1.01%***, 1983-2020 [I-6502377]; fixing-window drop 2000-2013 in sample [I-6910693]; " + P),
 "K-YBWI": r(2, "Own-contract full-text test: rest-of-day predictor null (t 1.34, R2_OOS -0.25%), only a 5%-level first-half-hour coefficient (t 1.97) with negative OOS R2 and no OOS significance [I-6175557]; overreaction study uses ex-post turning points, not counted [I-9302061]; another venue: first half-hour predicts last half-hour, 2002-2013, in sample, gross [I-8913070]: 2"),
 "K-SLBV": r(2, "Sibling full-text test essentially null (rest-of-day t 1.34, R2_OOS -0.25%) [I-4449352]; another venue: first half-hour predicts last half-hour, 2002-2013, in sample [I-1048169]; asset class pooled positive [I-5875287]: 2"),
 "K-ASSS": r(2, "Own-contract full-text test null (beta -0.04, t -0.17, R2_OOS -0.07%, 1999-2020) [I-7763472]; currency class insignificant 2000-2020 [I-7440670]; positives on another venue: EUR local-hours pattern net of costs, spot 1997-2007 [I-5661474], month-end fix contrarian net of half spread [I-4464887]; own-contract reversal study pre-2010, abstract only [I-1991189]: 2"),
 "K-OTEO": r(2, "Sibling full-text test null (t -0.17, R2_OOS -0.07%) [I-7055999]; class insignificant 2000-2020 [I-1399001]; another-venue positives net of costs, spot, pre-2010/2013 [I-5627872] [I-8453935]: 2"),
 "K-LTAT": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 0.89 (t 3.25), R2_OOS 0.17%***, 1987-2020, gross [I-3307613]; " + P + "; conflicting: currency class insignificant 2000-2020 [I-8241357]; AUD local-hours strategy negative after costs (spot) [I-1561443]"),
 "K-QIUI": r(3, "Same-underlying sibling: beta 0.89 (t 3.25), R2_OOS 0.17%***, 1987-2020, gross [I-5171336]; " + P + "; conflicting: class insignificant 2000-2020 [I-6820293]"),
 "K-OJGY": r(4, "Peer-reviewed full-text study on this contract: ML mid-price direction at 5-60 min, about 54% accuracy vs 50% random walk on hold-out samples, CME minute data 2020 (8 months), gross [I-1113821]; only CME directional study found [I-1251520]; spot studies out of sample [I-1954124] [I-8024268]"),
 "K-ZXJD": r(4, "Same-underlying sibling: peer-reviewed full-text ML direction study at 5-60 min, about 54% out-of-sample accuracy, CME 2020 minute data, gross [I-0961957]; no study of this contract itself [I-4826394]; spot out-of-sample studies [I-8162637] [I-0738628]"),
 "K-JGJF": r(2, "No study on this contract found (full-text search note) [I-2585560]; evidence only for another venue of the underlying and the asset class (spot Ethereum predictability, abstracts) [I-9435658] [I-6828620] [I-7081207]: 2"),
 "K-UQNU": r(2, "No study on this contract or its sibling found [I-1185799]; evidence only for another venue and the asset class (abstracts) [I-6383927] [I-5981656] [I-8086031]: 2"),
 "K-KVJD": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 6.36 (t 7.97), R2_OOS 3.76%***, 1996-2020, gross [I-6391399] [I-7774055]; " + P + "; conflicting: overnight -> last half hour disappears out of sample (abstract) [I-2107724]; single-signal null (preprint) [I-6260185]; sibling 5-min OHLCV families fail net of friction 2021-25 (preprint) [I-4145404]"),
 "K-YEPF": r(3, "Same-underlying sibling: beta 6.36 (t 7.97), R2_OOS 3.76%***, 1996-2020, gross [I-3956981]; " + P + "; conflicting own-contract full-text preprint: 14 OHLCV signal families on 5-min bars fail walk-forward net of friction, 2021-2025 [I-7644253]"),
 "K-FICQ": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 6.00 (t 5.86), R2_OOS 3.15%***, 1993-2020, gross [I-5184718] [I-8665382]; same-underlying ETF OOS R2 2.43%, 2000-2013 [I-1489418]; " + P),
 "K-RISF": r(3, "Same-underlying sibling: beta 6.00 (t 5.86), R2_OOS 3.15%***, 1993-2020, gross [I-1079992]; ETF OOS R2 2.43% [I-8974813]; " + P),
 "K-QAJV": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 5.02 (t 4.12), R2_OOS 2.18%***, 1997-2020, gross [I-7977888] [I-7966152]; " + P + "; conflicting abstract: overnight predictor fails out of sample [I-6973872]"),
 "K-DNXQ": r(3, "Same-underlying sibling: beta 5.02 (t 4.12), R2_OOS 2.18%***, 1997-2020, gross [I-5302548]; " + P + "; conflicting abstract [I-9940890]"),
 "K-AIIW": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 2.07 (t 4.45), R2_OOS 0.70%***, 1991-2020, gross [I-7175392] [I-6486099]; bond class 2000-2020 still significant (beta 1.53, t 3.61) [I-3854496]; " + P),
 "K-HIOT": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 2.33 (t 6.25), R2_OOS 0.93%***, 1988-2020, gross [I-7296512] [I-2972649]; " + P),
 "K-TATP": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 2.53 (t 6.96), R2_OOS 0.86%***, 1983-2020, gross [I-9392522] [I-0640571]; auction-day decline and recovery 1983-2024, gross, practitioner study [I-0423935]; pooled 2010-2023 trend/reversion is multi-asset (level 2) [I-9696534]; " + P),
 "K-UPOR": r(3, "Peer-reviewed rest-of-day -> last half hour on this contract: beta 2.11 (t 3.85), R2_OOS 0.22%***, 1982-2020, gross [I-9147399] [I-0032974]; " + P),
 "K-EXGX": r(3, "Item tagged same-underlying sibling: Treasury futures rest-of-day -> last half hour beta 2.07 (t 4.45), R2_OOS 0.70%***, 1991-2020, gross [I-0564233] (reader: not a price-transfer sibling, scorer decides; contract listed only from 2021); " + P),
 "K-DCJJ": r(3, "Item tagged same-underlying sibling: Treasury futures beta 2.33 (t 6.25), R2_OOS 0.93%***, 1988-2020, gross [I-2922406] (reader: not a price-transfer sibling, scorer decides); " + P),
 "K-NUPE": r(3, "Item tagged same-underlying sibling: Treasury futures beta 2.53 (t 6.96), R2_OOS 0.86%***, 1983-2020, gross [I-8830711] (reader: not a price-transfer sibling, scorer decides); " + P),
 "K-LWIK": r(3, "Item tagged same-underlying sibling: Treasury futures beta 2.11 (t 3.85), R2_OOS 0.22%***, 1982-2020, gross [I-4903125] (reader: not a price-transfer sibling, scorer decides); " + P),
 "K-OQCY": r(3, "Own-contract full-text row: rest-of-day beta 0.82 (t 2.09) in sample with R2_OOS -0.01%, mid-day predictor 2.89 (t 3.54) with multivariate R2_OOS 0.03%*** (Clark-West), 1982-2020, gross [I-5236390]; in-sample evidence with a tiny OOS gain; " + P),
 "K-JCID": r(3, "Same-underlying sibling row: rest-of-day beta 0.82 (t 2.09) in sample, mid-day predictor t 3.54, multivariate R2_OOS 0.03%***, 1982-2020, gross [I-0104202]; " + P),
 "K-AMNJ": r(3, "Same-underlying sibling row: rest-of-day beta 0.82 (t 2.09) in sample, mid-day predictor t 3.54, multivariate R2_OOS 0.03%***, 1982-2020, gross [I-3950490]; " + P),
 "K-IXHJ": r(3, "Own-contract full-text row: rest-of-day null, but first half-hour predicts the last half hour negatively (beta -1.17, t -2.17, Clark-West OOS significant at 5% despite R2_OOS -0.04%), 1982-2020, gross [I-0247313]: in-sample reversal evidence; another venue positive [I-6289271]; " + P),
 "K-ASNW": r(3, "Same-underlying sibling row: first half-hour reversal beta -1.17 (t -2.17), Clark-West OOS at 5%, 1982-2020, gross [I-3899241]; another venue positive [I-2608600]; " + P),
 "K-BMTO": r(3, "Same-underlying sibling row: first half-hour reversal beta -1.17 (t -2.17), Clark-West OOS at 5%, 1982-2020, gross [I-2845578]; another venue positive [I-9321343]; " + P),
 "K-KQRO": r(3, "Own-contract full-text row: rest-of-day null, mid-day predictor 2.49 (t 3.22) in sample, multivariate Clark-West significant though R2_OOS -0.27%, 1982-2020, gross [I-9429987]; another venue positive in sample [I-3504825]; program's own OOS search found nothing net of costs (not a publication) [I-7488467]; " + P),
 "K-WSRZ": r(3, "Same-underlying sibling row: mid-day predictor t 3.22 in sample, multivariate Clark-West significant, 1982-2020, gross [I-5437146]; another venue positive [I-5080319]; program's own sibling search negative (not a publication) [I-2332572]; " + P),
 "K-AJZH": r(2, "Own-contract full-text row null on every predictor (rest-of-day t 0.67, R2_OOS -0.07%) [I-0989017]; order-imbalance predictability only in an abstract, horizon unknown [I-4441177]; asset class pooled positive [I-6385434]: 2"),
 "K-OMOR": r(2, "Sibling full-text row null (t 0.67, R2_OOS -0.07%) [I-1303567]; abstract-only order-imbalance item [I-1056015]; asset class pooled positive [I-9758737]: 2"),
 "K-CSTX": r(2, "Sibling full-text row null (t 0.67, R2_OOS -0.07%) [I-1442403]; abstract-only order-imbalance item [I-6659719]; asset class pooled positive [I-5504554]: 2"),
 "K-ODAS": r(2, "Own-contract full-text row null on every predictor (rest-of-day t 0.08, R2_OOS -0.06%) [I-6691865]; asset class pooled positive [I-8734729]: 2"),
 "K-GOMC": r(2, "Sibling full-text row null (t 0.08, R2_OOS -0.06%) [I-6851643]; asset class pooled positive [I-4148211]: 2"),
}
labs = list(json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json'))['contracts'])
assert set(D) == set(labs), (set(labs) - set(D), set(D) - set(labs))
json.dump({k: {"D6": v} for k, v in D.items()}, open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/blind2/r_d6.json', 'w'), indent=1)
print('ok', len(D))
