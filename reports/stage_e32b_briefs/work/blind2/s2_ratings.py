import json
def r(v, reason, unk=False, unv=None):
    d = {"value": v, "unknown": unk, "reason": reason}
    if unv is not None: d["unverified"] = unv
    return d
crude = "EIA weekly report: full-text study on another venue of the same underlying finds slow adjustment completed only at the day's end (drift beyond 5 min, in sample, decaying, absent 2014-16) %s; conflicting full-text futures evidence: absorbed within the [-5,+10] window %s and no return predictability after 10:35 %s"
ng = "Weekly gas storage report absorbed within about 10 minutes, longer windows similar %s, 5-7 min response equals the 100-min level %s; announcement-day (-5,+30) mean includes the jump, not slow adjustment %s; macro 'price drift' only in an abstract %s; full text supports 1"
metals_mac = "Macro releases (full text, 2002-2008, 5-min data): delayed peak responses for some releases (09:15 releases peak about 30 min later for gold and silver; 5-10 min delay for silver at 10:00; copper delayed at 08:30), response dissipating within an hour %s"
wasde = "WASDE (full-text working paper, 2010-2021, in sample): price reaction not significant at 10 min, significant at 30 min, and for soybeans still growing to the close %s; conflicting: no systematic under/overreaction in other studies %s"
D = {
 "K-LRVK": r(2, crude % ("[I-1827495]", "[I-1823229]", "[I-4758183]") + "; partial reversal over hours [I-5190497]"),
 "K-SGKW": r(2, crude % ("[I-6979195]", "[I-1202170]", "[I-8965114]")),
 "K-PXYN": r(2, crude % ("[I-1370203]", "[I-3058806]", "[I-6301647]")),
 "K-YJXE": r(1, ng % ("[I-2054332]", "[I-3560076]", "[I-9360761]", "[I-3298010]"), False, False),
 "K-LIRS": r(1, ng % ("[I-8806698]", "[I-0343083]", "[I-6072685]", "[I-3902519]"), False, False),
 "K-DLUC": r(1, ng % ("[I-4770783]", "[I-9506789]", "[I-1336063]", "[I-3854722]"), False, False),
 "K-LGJM": r(2, "FOMC: gold price adjustment at 10 min is three times that at 5 min (mean still moving after 5 min), full-text accepted manuscript, 2007-2020 [I-7180096]; " + metals_mac % "[I-6790764]" + "; conflicting snippet: reaction complete within 90 s [I-3808282]"),
 "K-NYZZ": r(2, "Same-underlying evidence: FOMC gold adjustment at 10 min three times that at 5 min, full text, 2007-2020 [I-9372520]; " + metals_mac % "[I-7655106]" + "; conflicting snippet [I-1401271]"),
 "K-AAUT": r(2, metals_mac % "[I-9189584]" + "; authors still call the metals efficient; volatility decays in about 10 min [I-2674736]"),
 "K-OEVC": r(2, "Same-underlying evidence: " + metals_mac % "[I-1743361]" + "; authors call the metals efficient [I-3646782]"),
 "K-YBWI": r(2, metals_mac % "[I-0770257]" + " (copper: 'somewhat delayed response' to 08:30 news; size of the delay not stated); volatility decays in about 10 min [I-1234417]"),
 "K-SLBV": r(2, "Same-underlying evidence: " + metals_mac % "[I-6511728]" + " (copper delay size not stated) [I-3960272]"),
 "K-ASSS": r(1, "US macro releases move the rate; conditional mean adjusts quickly, effectively jumps [I-3942595]; EBS evidence: completed within a few minutes [I-4000397]; ECB communication null [I-0558164]; FOMC 12-24 h pattern is hours-horizon, not post-release drift [I-7122491]"),
 "K-OTEO": r(1, "US macro releases: conditional mean adjusts quickly [I-1799523]; EBS: completed within a few minutes [I-8663649]; ECB null [I-4806733]"),
 "K-LTAT": r(1, "RBA announcements: sharp impact within 10 minutes, little after over six hours [I-0712830]; US macro: quick mean adjustment [I-6223581]"),
 "K-QIUI": r(1, "RBA announcements: sharp impact within 10 minutes, little after [I-0402396]; US macro: quick mean adjustment [I-8671649]"),
 "K-OJGY": r(1, "No crypto-specific release [I-0195424]; macro/FOMC news moves volatility (abstract) [I-0969334]; full text finds no significant price response within 25-55 min [I-1141490]; macro releases move it in volatility only", False),
 "K-ZXJD": r(1, "No crypto-specific release [I-4914785]; macro/FOMC news moves volatility (abstract) [I-8744895]; full text finds no significant price response within 25-55 min [I-0659977]; macro releases move it in volatility only", False),
 "K-JGJF": r(1, "No crypto-specific release [I-3349940]; US monetary-policy news drives volatility, more for this asset (abstract) [I-5984988]; price reactions only in a snippet [I-8478236]; absorption not documented", False),
 "K-UQNU": r(1, "No crypto-specific release [I-1838865]; US monetary-policy news drives volatility (abstract) [I-7296221]; price reactions only in a snippet [I-1469707]; absorption not documented", False),
 "K-KVJD": r(1, "US macro calendar [I-2403974]; continuing 10-30 min adjustment documented only on a cousin index future [I-2141936] (not this product or its underlying); FOMC-day momentum is first-half-hour sign, not release drift [I-2412215]; pre-FOMC drift is pre-release and gone after 2015 [I-1393905]"),
 "K-FICQ": r(1, "US macro calendar [I-8552124]; continuing 10-30 min adjustment only on a cousin [I-0611992]; FOMC-day momentum not release drift [I-8446845]; pre-FOMC drift pre-release [I-7619319]"),
 "K-QAJV": r(1, "US macro calendar [I-8820118]; continuing 10-30 min adjustment only on a cousin [I-3509365]; FOMC-day momentum not release drift [I-9707258]; pre-FOMC drift pre-release [I-1098678]"),
 "K-RISF": r(1, "US macro calendar [I-2230022]; continuing 10-30 min adjustment only on a cousin [I-7098624]; FOMC-day momentum not release drift [I-5862849]"),
 "K-YEPF": r(1, "US macro calendar [I-1551552]; continuing 10-30 min adjustment only on a cousin [I-1008324]; FOMC-day momentum not release drift [I-6860895]"),
 "K-DNXQ": r(1, "US macro calendar [I-9155643]; continuing 10-30 min adjustment only on a cousin [I-1761428]; FOMC-day momentum not release drift [I-4600936]"),
 "K-AIIW": r(2, "FOMC statement: yields keep falling for about 3 hours after (significant, persistent post-release drift), full text reused, 1997-2024 [I-2967977]; payrolls absorbed in seconds-minutes [I-8347018]"),
 "K-HIOT": r(2, "FOMC statement: yields keep falling for about 3 hours after, full text reused, 1997-2024 [I-0025128]; payrolls absorbed in seconds-minutes [I-2165703]"),
 "K-TATP": r(2, "FOMC statement: yields keep falling for about 3 hours after, full text reused, 1997-2024 [I-9972691]; payrolls absorbed in seconds-minutes [I-9741876]; days-horizon post-FOMC drift abstract only [I-7974379]"),
 "K-UPOR": r(2, "FOMC statement: yields keep falling for about 3 hours after, full text reused, 1997-2024 [I-8827921]; payrolls absorbed in seconds-minutes [I-8012351]"),
 "K-EXGX": r(1, "Payrolls and macro releases move the Treasury complex, absorbed within seconds to minutes [I-9134981] [I-9916596]; auctions scheduled [I-4585152]; no post-release drift item in this list"),
 "K-DCJJ": r(1, "Payrolls and macro releases absorbed within seconds to minutes [I-0591918] [I-8391084]; auctions scheduled [I-7380495]; no post-release drift item in this list"),
 "K-NUPE": r(1, "Payrolls and macro releases absorbed within seconds to minutes [I-7873978] [I-2018889]; auctions scheduled [I-2373458]; no post-release drift item in this list"),
 "K-LWIK": r(1, "Payrolls and macro releases absorbed within seconds to minutes [I-0599061] [I-2537894]; auctions scheduled [I-1459240]; no post-release drift item in this list"),
 "K-OQCY": r(2, wasde % ("[I-9562555]", "[I-3275443] (abstract)") + "; jumps cluster within 2 min [I-3724480]"),
 "K-IXHJ": r(2, wasde % ("[I-4816101]", "[I-5480258] (full text, null)")),
 "K-JCID": r(2, "Same-underlying evidence: " + wasde % ("[I-6126920]", "[I-6655653] (abstract)")),
 "K-AMNJ": r(2, "Same-underlying evidence: " + wasde % ("[I-8447330]", "[I-5363756] (abstract)")),
 "K-ASNW": r(2, "Same-underlying evidence: " + wasde % ("[I-9862672]", "[I-8141725] (full text, null)")),
 "K-BMTO": r(2, "Same-underlying evidence: " + wasde % ("[I-3293816]", "[I-2079046] (full text, null)")),
 "K-AJZH": r(1, "USDA reports scheduled in the day session [I-4332193]; only absorption evidence is volatility dissipating within minutes (abstract) [I-1183408]; no drift item"),
 "K-OMOR": r(1, "USDA reports scheduled [I-2317410]; volatility dissipates within minutes (abstract) [I-6006132]; no drift item"),
 "K-CSTX": r(1, "USDA reports scheduled [I-8847239]; volatility dissipates within minutes (abstract) [I-7532795]; no drift item"),
 "K-ODAS": r(1, "USDA reports scheduled in the session [I-3243355]; price moves on policy and crush reports only as snippet pointers [I-4767224]; absorption not documented"),
 "K-KQRO": r(1, "USDA reports scheduled in the session [I-3326589]; price moves on policy and crush reports only as snippet pointers [I-0753409]; absorption not documented"),
 "K-GOMC": r(1, "USDA reports scheduled [I-9876019]; price moves only as snippet pointers [I-1771256]; absorption not documented"),
 "K-WSRZ": r(1, "USDA reports scheduled [I-4140122]; price moves only as snippet pointers [I-9501790]; absorption not documented"),
}
labs = list(json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_contracts.json'))['contracts'])
assert set(D) == set(labs), (set(labs) - set(D), set(D) - set(labs))
json.dump({k: {"s2": v} for k, v in D.items()}, open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/blind2/r_s2.json', 'w'), indent=1)
print('ok', len(D))
