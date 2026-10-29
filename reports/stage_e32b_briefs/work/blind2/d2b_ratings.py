import json
def r(v, reason, unk=False): return {"value": v, "unknown": unk, "reason": reason}
IIPg = "the International Incentive Program (volume-fee incentive with progressive volume discounts, in force 2011-12-16..2026-01-31) lists this contract's class in its fee table"
IIPt = "the International Incentive Program (volume-fee incentive with progressive volume discounts, in force 2011-12-16..2026-01-31) lists this contract by name"
satel = "Only the leader's/sibling's programs are sourced (grain extended-hours MM program, deferred-month VIP, 'none found' note) %s; nothing on this contract itself; the script handles the leader link; unknown 0.5"
D = {
 "K-SGKW": r(1, "Own Liquidity Provider Program with continuous two-sided quoting on Globex, 2021-07-12..2026-01-31 [I-1489485]"),
 "K-PXYN": r(1, "No own MM program 2021-2026 found (2013 MMP only [I-1446648]); " + IIPt + " [I-7166892]; counted as a volume-incentive program"),
 "K-LRVK": r(1, "Own volume-incentive programs on outright futures: Crude and Refined Futures VIP 2018-02..2025-01 [I-5893881], Crude Oil Incentive Program 2024-25 [I-1675819], Crude Liquidity Program 2024-25 [I-7909359]; also IIP [I-8241054]"),
 "K-LIRS": r(1, "Own Futures Market Development Program (volume incentive on Globex), 2023-11-06..2024-01-31 [I-9366791] [I-7926314]"),
 "K-DLUC": r(1, "No own MM program (sibling programs only); " + IIPt + " [I-6534996]; counted as a volume-incentive program"),
 "K-YJXE": r(1, "Financial Natural Gas Market Maker Program names this contract on Globex, 2017-01-01..2027-07-31 [I-3384838] [I-9848180]; also IIP [I-7717602]; strips/deferred-spread programs not counted [I-4789653] [I-1109366]"),
 "K-NYZZ": r(1, "Own futures MM program only 2010-2012 and an options MM program [I-0300845] (not counted); " + IIPt + " [I-8121501]; counted as a volume-incentive program"),
 "K-LGJM": r(1, "Globex Precious Metals Volume Incentive Program on outright futures, 2018-02-01..2026-01-31 [I-7913392]; also IIP [I-5128571]"),
 "K-OEVC": r(1, "Korea Retail FCM Rebate Program (volume rebate) 2022-11-01..2028-07-31 [I-8014777]; also " + IIPt + " [I-6602309]"),
 "K-AAUT": r(1, "Globex Precious Metals Volume Incentive Program on outright futures, 2018-02-01..2026-01-31 [I-4353137]; also IIP [I-2254101]"),
 "K-SLBV": r(1, "Own Market Development Program with continuous two-sided quoting obligations on outright futures, 2022-05-01..2025-01-31 [I-3606770]"),
 "K-YBWI": r(1, "Globex Base Metals Volume Incentive Program on outright futures, 2018-02-01..2026-01-31 [I-3907216] [I-8372419]; also IIP [I-7312382]"),
 "K-OTEO": r(1, "FX [size class] Market Maker Program covering this contract's futures, two-sided quoting, 2021-08-01..2025-08-31 [I-4205014]"),
 "K-ASSS": r(1, "No outright MM program found (calendar-spread [I-3699676] and BTIC [I-5039570] programs not outright; not-found note [I-2077117]); " + IIPg + " (FX futures row) [I-9607712]; counted as a volume-incentive program"),
 "K-QIUI": r(1, "FX [size class] Market Maker Program covering this contract's futures, two-sided quoting, 2021-08-01..2025-08-31 [I-2417994]"),
 "K-LTAT": r(1, "No outright MM program found (calendar-spread program not outright [I-1191379]; not-found note [I-4631033]); " + IIPg + " (FX futures row) [I-0870707]; counted as a volume-incentive program"),
 "K-UQNU": r(1, "Own [size class] MM Program 2021-12-06..2025-01-31 and [size class] Cryptocurrency Futures MM Program 2025-02..2027-01 [I-8721257]; market-wide fee discount 2023-24 [I-8883149]"),
 "K-JGJF": r(1, "Own Market Maker Program 2021-02-08..2021-08-31 (in force in 2021) [I-6536040]; BTIC/TAS program not counted [I-0573297]"),
 "K-ZXJD": r(1, "Named in Bitcoin Friday Futures MM Program 2024-09..2025-07 and [size class] Cryptocurrency Futures MM Program 2025-02..2027-01 [I-5476749]; market-wide fee discount [I-8093144]"),
 "K-OJGY": r(1, "Cryptocurrency Futures Market Maker Program names this contract, 2018-03-05..2027-01-31 [I-7596610]"),
 "K-RISF": r(1, "[size class] Futures Market Maker Program on outright futures incl. this contract, 2019-05-06..2022-04-30 [I-3828422] [I-0846950]"),
 "K-FICQ": r(1, "Own outright MM program only 2017-18 [I-0272562]; TACO/BTIC/TMAC programs not outright [I-5693014] [I-6489841] [I-6503284]; " + IIPg + " (row says outrights and spreads) [I-7016482]; counted as a volume-incentive program"),
 "K-DNXQ": r(1, "[size class] Futures Market Maker Program on outright futures incl. this contract, 2019-05-06..2022-04-30 [I-9313699] [I-4154768]"),
 "K-QAJV": r(1, "Equity Index Futures Market Maker Program incl. this contract, 2013-04-01..2021-01-31 (in force January 2021 by the overstrike reading) [I-5985905]; also IIP class row [I-0260270]"),
 "K-YEPF": r(1, "[size class] Futures Market Maker Program on outright futures incl. this contract, 2019-05-06..2022-04-30 [I-8029533] [I-4289279]"),
 "K-KVJD": r(1, "Equity Index Futures Market Maker Program incl. this contract, 2013-04-01..2021-01-31 (in force January 2021 by the overstrike reading) [I-9080790]; also IIP class row covering outrights [I-2839485]; TACO/BTIC/TMAC not counted"),
 "K-EXGX": r(1, "Yield Futures Market Maker Program names this contract among its Products, 2021-08-16..2028-02-29 [I-9677543] (outright quoting obligation is on a sibling; this contract via spreads and fee waivers); also IIP class row [I-2103388]"),
 "K-DCJJ": r(1, "Yield Futures Market Maker Program names this contract among its Products, 2021-08-16..2028-02-29 [I-8362842] (outright quoting obligation is on a sibling; this contract via spreads and fee waivers); also IIP class row [I-6328363]"),
 "K-NUPE": r(1, "Yield Futures Market Maker Program with quoting obligations on this contract's outright, 2021-08-16..2028-02-29 [I-2418311]; also IIP class row [I-9585386]"),
 "K-LWIK": r(1, "Yield Futures Market Maker Program names this contract among its Products, 2021-08-16..2028-02-29 [I-4246140] (outright quoting obligation is on a sibling; this contract via spreads and fee waivers); also IIP class row [I-1760418]"),
 "K-AIIW": r(1, "Only an invoice-spread IDB program (not outright) [I-3654541]; " + IIPg + " (U.S. Treasury Futures row) [I-5243124]; counted as a volume-incentive program"),
 "K-HIOT": r(1, "Only an invoice-spread IDB program (not outright) [I-0348372]; " + IIPg + " (U.S. Treasury Futures row) [I-9391390]; counted as a volume-incentive program"),
 "K-TATP": r(1, "Only an invoice-spread IDB program (not outright) [I-6320022]; " + IIPg + " (U.S. Treasury Futures row) [I-0134609]; counted as a volume-incentive program"),
 "K-UPOR": r(1, "Only an invoice-spread IDB program (not outright) [I-2265500]; long-term bond MMP is for another product [I-6350451]; " + IIPg + " (U.S. Treasury Futures row) [I-9996396]; counted as a volume-incentive program"),
 "K-JCID": r(0.5, satel % "[I-7638113] [I-0006078] [I-6264488]", True),
 "K-ASNW": r(0.5, satel % "[I-6020558] [I-2278948] [I-5874449]", True),
 "K-OMOR": r(0.5, satel % "[I-2031307] [I-0051256] [I-0309070]", True),
 "K-GOMC": r(0.5, satel % "[I-1665518] [I-8954818] [I-6506042]", True),
 "K-WSRZ": r(0.5, satel % "[I-0935870] [I-9829173] [I-2096749]", True),
 "K-AMNJ": r(1, "Own [size class] grains MM program expired 2009, none 2021-2026 found [I-3435157]; " + IIPg + " ([size class] Agricultural Contracts row) [I-2577405]; counted as a volume-incentive program"),
 "K-BMTO": r(1, "Own [size class] grains MM program expired 2009, none 2021-2026 found [I-4725715]; " + IIPg + " ([size class] Agricultural Contracts row) [I-9340836]; counted as a volume-incentive program"),
 "K-CSTX": r(1, "Own [size class] grains MM program expired 2009, none 2021-2026 found [I-9474166]; " + IIPg + " ([size class] Agricultural Contracts row) [I-3661273]; counted as a volume-incentive program"),
 "K-OQCY": r(1, "Grain & Oilseed Futures extended-hours Market Maker Program on this contract's outright futures, 2017-01-01..at least 2024-07-31 [I-5241870]; deferred-month VIP to 2025-07 [I-7929583]; IIP [I-6981457]"),
 "K-IXHJ": r(1, "Grain & Oilseed Futures extended-hours Market Maker Program on this contract's outright futures, 2017-01-01..at least 2024-07-31 [I-6240367]; deferred-month VIP [I-7258868]; IIP [I-9352383]"),
 "K-AJZH": r(1, "Grain & Oilseed Futures extended-hours Market Maker Program on this contract's outright futures, 2017-01-01..at least 2024-07-31 [I-9115565]; deferred-month VIP [I-5772015]; IIP [I-8785599]"),
 "K-ODAS": r(1, "Grain & Oilseed Futures extended-hours Market Maker Program on this contract's outright futures, 2017-01-01..at least 2024-07-31 [I-3084424]; deferred-month VIP [I-1738222]; IIP [I-3076996]"),
 "K-KQRO": r(1, "Grain & Oilseed Futures extended-hours Market Maker Program on this contract's outright futures, 2017-01-01..at least 2024-07-31 [I-1516259]; deferred-month VIP [I-7961036]; IIP [I-2039044]"),
}
labs = list(json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json'))['contracts'])
assert set(D) == set(labs), (set(labs) - set(D), set(D) - set(labs))
json.dump({k: {"D2b": v} for k, v in D.items()}, open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/blind2/r_d2b.json', 'w'), indent=1)
print('ok', len(D))
