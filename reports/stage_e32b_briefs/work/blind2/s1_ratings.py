import json
def r(v, reason, unk=False, unv=None):
    d = {"value": v, "unknown": unk, "reason": reason}
    if unv is not None: d["unverified"] = unv
    return d
D = {
 "K-SGKW": r(1, "Mini/full pair with the leader, cash-settled to its final settlement (mechanical) [I-3407497]; sibling items: WTI-Brent lead-lag on 1-second data, horizon seconds to minutes, not shown at a minute or more [I-2517045]; crack/location mean reversion daily/monthly only [I-3334235]"),
 "K-PXYN": r(1, "Mini/full pair with the leader (mechanical) [I-5132838]; sibling items: WTI-Brent lead-lag at seconds, not minute-level [I-1707075]; crack mean reversion daily/monthly [I-6141369]"),
 "K-LRVK": r(1, "WTI-Brent lead-lag measured at one-second frequency, information reflected 'within minutes', not documented as a minute-plus lead [I-3769398]; crack/location spreads mean-revert at daily/monthly horizon [I-2865802]; calendars [I-2656196]"),
 "K-LIRS": r(1, "Fungible (clearing) with a sibling and the financial contracts: mechanical [I-3595570]; no economic spread relationship listed"),
 "K-DLUC": r(1, "Fungibility [I-1737834] and listed ratio intercommodity spread with the full-size contract [I-2925516]: mechanical"),
 "K-YJXE": r(1, "Ratio spread with a sibling [I-8517224] and calendars/strips [I-1908643] [I-2420356]: mechanical; gas-to-international-gas Granger causality daily only [I-9867121]; gas-crude link is volatility-only [I-5829419]; HFT stat-arb is abstract-only [I-9351278]"),
 "K-NYZZ": r(2, "Gold-silver cointegration with silver leading gold at 1-minute frequency, full text (thesis, in sample) [I-3983047], tagged same-underlying sibling; own mini/full pair mechanical [I-3108110]"),
 "K-LGJM": r(2, "Gold-silver cointegration with silver leading gold at 1-minute frequency (impulse responses), full text, CME futures 2007-2012, in sample (master's thesis) [I-6570135]"),
 "K-OEVC": r(2, "Gold-silver cointegration with silver leading gold at 1-minute frequency, full text (thesis) [I-3169885], tagged same-underlying sibling; own mini/full pair mechanical [I-3196920]"),
 "K-AAUT": r(2, "Gold-silver cointegration with silver leading gold at 1-minute frequency, full text, CME futures 2007-2012, in sample (master's thesis) [I-8511449]"),
 "K-SLBV": r(1, "Mini/full pair, cash-settles to the full-size contract (mechanical) [I-0621297]; cross-venue copper cointegration at daily horizon only [I-1987303]"),
 "K-YBWI": r(1, "Calendar spreads [I-1550646] and mini/full pair [I-5199406]: mechanical; cross-venue copper relationship documented at daily horizon only [I-3405054]"),
 "K-OTEO": r(1, "Mini/full pair with the full-size contract (arbitrage-tight) [I-5237349]; futures-spot links mechanical [I-4496272]"),
 "K-ASSS": r(1, "Mini/full pair [I-5713810], futures-vs-spot FX Link basis [I-5368875] and calendar spreads [I-5176690]: all mechanical or arbitrage-tight"),
 "K-QIUI": r(2, "Underlying AUD/USD vs gold/copper/crude: Granger causality both ways at 5-minute frequency, stronger at short horizons (spot data 2000-2009, in sample, full-text working paper) [I-5696550]; conflicting: no daily Granger causality on futures [I-4528009]; mini/full pair [I-1261355]"),
 "K-LTAT": r(2, "Underlying AUD/USD vs gold/copper/crude: Granger causality both ways at 5-minute frequency, stronger at short horizons (spot data 2000-2009, in sample, full-text working paper) [I-6548349]; conflicting: no daily Granger causality on futures [I-5096560]; mini/full pair [I-4321985]"),
 "K-UQNU": r(1, "Mini/full pair [I-6540625] and calendars [I-2319076]: mechanical; cross-asset minute-level lead-lag only in abstracts [I-4323659], so full-text items alone support 1 (= the cap); reported 1, not unverified", False, False),
 "K-JGJF": r(1, "Calendars [I-7687190] and mini/full pair [I-9615848]: mechanical; cross-asset minute-level lead-lag only in abstracts [I-8661087], so full-text items alone support 1 (= the cap); reported 1, not unverified", False, False),
 "K-ZXJD": r(1, "Mini/full pair, settlement copied from the full-size [I-8017325], calendars [I-1897671]: mechanical; cross-asset lead-lag only in abstracts [I-9476537]; full-text items alone support 1 (= the cap); reported 1, not unverified", False, False),
 "K-OJGY": r(1, "Calendars [I-0597731] and mini/full pair [I-4891303]: mechanical; cross-asset lead-lag only in abstracts, mixed [I-8281739]; full-text items alone support 1 (= the cap); reported 1, not unverified", False, False),
 "K-RISF": r(2, "Cross-index lead-lag of about 4.7-12.3 minutes at 60-minute chart extrema, full-text preprint, 2004-2014, in sample [I-6002483] (tagged same-underlying sibling); own mini/full pair mechanical [I-8872361]"),
 "K-FICQ": r(2, "This index leads the S&P futures by about 4.7-5.0 minutes at 60-minute chart extrema (cross-index pair), full-text preprint, 2004-2014, in sample, no trading test [I-4508887]; calendars [I-7477790]"),
 "K-DNXQ": r(1, "Mini/full pair [I-0331558] and calendars [I-5653599]: mechanical; no intraday cross-index study for this index [I-1910711]"),
 "K-QAJV": r(1, "Calendars [I-8431291] and mini/full pair [I-2920285]: mechanical; no intraday cross-index study for this index found [I-0637809]"),
 "K-YEPF": r(2, "This underlying leads the S&P futures by about 8.7-12.3 minutes at 60-minute chart extrema, full-text preprint, 2004-2014, in sample [I-5023024] (tagged same-underlying sibling); own mini/full pair mechanical [I-8371910]"),
 "K-KVJD": r(2, "This index leads the S&P futures by about 8.7-12.3 minutes at 60-minute chart extrema (cross-index pair), full-text preprint, 2004-2014, in sample, no trading test [I-0010971]; calendars [I-3141782]"),
 "K-EXGX": r(1, "Only item: yield-futures vs Treasury futures/cash design relationship (mechanical), reused full-text fact without a quote [I-5818937]"),
 "K-DCJJ": r(1, "Only item: yield-futures vs Treasury futures/cash design relationship (mechanical), reused full-text fact without a quote [I-8042677]"),
 "K-NUPE": r(1, "Only item: yield-futures vs Treasury futures/cash design relationship (mechanical), reused full-text fact without a quote [I-3053967]"),
 "K-LWIK": r(1, "Only item: yield-futures vs Treasury futures/cash design relationship (mechanical), reused full-text fact without a quote [I-2823067]"),
 "K-AIIW": r(1, "Curve inter-commodity spreads [I-7419500] and calendars [I-3330103]: mechanical; futures-cash links sub-second [I-3462916]; order flow vs yields weekly only [I-3278562]"),
 "K-HIOT": r(1, "Curve inter-commodity spreads [I-5891598] and calendars [I-6615053]: mechanical; futures-cash links sub-second [I-1682281]; order flow vs yields weekly only [I-4602788]"),
 "K-TATP": r(1, "Curve inter-commodity spreads [I-7804246] and calendars [I-9773913]: mechanical; futures-cash links sub-second [I-9582182]; order flow vs yields weekly only [I-8138132]"),
 "K-UPOR": r(1, "Curve inter-commodity spreads [I-3242978] and calendars [I-4252276]: mechanical; futures-cash links sub-second [I-3808698]; order flow vs yields weekly only [I-8327124]"),
 "K-JCID": r(1, "Mini/full pair [I-3903416], implied calendar books [I-6448720], nearby-deferred intraday cointegration is a calendar relationship [I-7604668]; corn-soy-wheat cointegration weekly only [I-7516110]"),
 "K-ASNW": r(2, "Soybean crush intraday cointegration at 1-minute sampling on 180 of 243 day sessions, peer-reviewed full text (2015 data, in sample) [I-1143525] [I-1095935], tagged same-underlying sibling; own mini/full pair [I-5812881]"),
 "K-OMOR": r(1, "Mini/full pair [I-1123489] and implied calendar books [I-1975915]: mechanical; corn-soy-wheat cointegration weekly only [I-3299277]"),
 "K-GOMC": r(2, "Soybean crush intraday cointegration at 1-minute sampling, peer-reviewed full text (2015) [I-6153141] [I-4192780], tagged same-underlying sibling; own mini/full pair [I-7574532]"),
 "K-WSRZ": r(2, "Soybean crush intraday cointegration at 1-minute sampling, peer-reviewed full text (2015) [I-0390906] [I-9108874], tagged same-underlying sibling; own mini/full pair [I-7389652]"),
 "K-AMNJ": r(1, "Mini/full pair [I-5742175], implied calendar books [I-5985501], nearby-deferred intraday cointegration is a calendar relationship [I-4340975]; cross-grain cointegration weekly only [I-8655329]"),
 "K-BMTO": r(2, "Soybean crush intraday cointegration at 1-minute sampling, peer-reviewed full text (2015) [I-5892172] [I-6395020], tagged same-underlying sibling; own mini/full pair [I-1031055]"),
 "K-CSTX": r(1, "Mini/full pair [I-5150948] and implied calendar books [I-4339652]: mechanical; corn-soy-wheat cointegration weekly only [I-0922873]"),
 "K-OQCY": r(1, "Nearby-deferred intraday cointegration on about 70% of days is a calendar relationship [I-0993405]; implied books [I-4593848]; economic corn-soy-wheat cointegration documented weekly only [I-6852671]"),
 "K-IXHJ": r(2, "Soybean crush (this contract vs meal and oil) intraday cointegration at 1-minute sampling on 180 of 243 day sessions, peer-reviewed full text, 2015 CME data, in sample [I-2899526] [I-5640577]"),
 "K-AJZH": r(1, "Mini/full pair [I-5008075], implied calendar books [I-6917796]: mechanical; corn-soy-wheat cointegration weekly only [I-2040614]"),
 "K-ODAS": r(2, "Soybean crush (soybeans vs this contract and oil) intraday cointegration at 1-minute sampling, peer-reviewed full text, 2015 CME data [I-4657581] [I-4547156]"),
 "K-KQRO": r(2, "Soybean crush (soybeans vs meal and this contract) intraday cointegration at 1-minute sampling, peer-reviewed full text, 2015 CME data [I-9454843] [I-2485046]"),
}
labs = list(json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json'))['contracts'])
assert set(D) == set(labs), (set(labs) - set(D), set(D) - set(labs))
json.dump({k: {"s1": v} for k, v in D.items()}, open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/blind2/r_s1.json', 'w'), indent=1)
print('ok', len(D))
