"""CRUDE_items_D.py: pointers, snippets and asset-class evidence (session 2026-10-28)."""
from CRUDE_lib import it, src, write
NOSRC = {"file": None, "field": None, "url": None, "fetched_utc": None, "sha256": None}
items = [
 it(42, ["MCL","QM","CL"], "T2a", "auto_share_pct", "HFT more than 60% of all US futures volume in 2012 (Tabb Group, via news)", "futures_broad", "2012",
    "Pointer only: consultancy estimate reported in a 2013 Reuters-syndicated news article (country-guide.ca, farmtario.com); both copies answered 403, so not saved. Not product-specific. Never to be used alone.",
    "High-frequency trading accounted for more than 60 per cent of all futures volume in 2012 on U.S. exchanges, according to New York industry researcher The Tabb Group.",
    {**NOSRC, "url": "https://www.country-guide.ca/?p=79780"}, "snippet", pointer=True),
 it(43, ["MCL","QM","CL"], "T6", "directional_study", "positive in and out of sample: first half-hour return predicts last half-hour return (USO)", "other_venue", "USO ETF 2006-2018",
    "Wen, Gong, Ma and Xu (2021), Economic Modelling, 'Intraday momentum and return predictability: Evidence from the crude oil market'. Known only from a search snippet (Quantpedia summary); full text blocked in E.20 (product_CL.json unfinished[0]). Horizon 30 min; costs unknown.",
    "The first half-hour return from the previous day's market close positively predicts the last half-hour return both in-sample and out-of-sample.",
    {**NOSRC, "url": "https://vvv.quantpedia.com/?p=4247"}, "snippet"),
 it(44, ["MCL","QM","CL"], "T6", "directional_study", "null after costs: intraday momentum and reversal strategies on 31 Chinese commodity futures do not cover costs", "asset_class", "minute data, Chinese commodity futures (period not in abstract; published 2018)",
    "Yang, Goncu and Pantelous (2018), International Review of Financial Analysis 60. Other venue (Chinese exchanges), commodity class broadly; out-of-sample backtests with per-commodity cost estimates. Crude oil membership not stated in abstract. Abstract only.",
    "the intra-day strategies used cannot generate sufficiently enough high excess returns to cover the excessive costs due to the higher frequency of trading.",
    src("itu_chinese_commodity_momentum_reversal.html.txt"), "abstract", negative=True),
 it(45, ["MCL","QM","CL"], "T1", "median_spread_ticks", "WTI average best bid/ask 1.07 ticks in US hours vs 1.18 in Asian hours (CME 2016 deck)", "product", "about 2016 (deck date)",
    "Search snippet of CME 'product-updates-hk-2016.pdf'. Not fetched: cmegroup.com is never fetched by rule and the file has no Wayback capture (archive.org availability API empty). Average, not median; session-split. [unverified: snippet]",
    "average best bid/ask difference of 1.18 ticks during Asian hours versus 1.07 during US hours",
    {**NOSRC, "url": "https://www.cmegroup.com/globex/resources/files/product-updates-hk-2016.pdf"}, "snippet"),
]
write("D", items)
