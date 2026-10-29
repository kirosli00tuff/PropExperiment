"""Masking vocabulary for the FactTable's blind sheets (Stage E.32b C1). Data only.

Product names are mapped to the code they identify (longest phrases first at use). Underlying and asset-class words
(crude oil, natural gas, gold, Treasury, corn, bitcoin ...) stay, as spec section 6 allows."""

PRODUCT_NAMES = {
    # crude
    "Micro WTI Crude Oil": "MCL", "Micro Crude Oil": "MCL", "Micro WTI": "MCL", "Micro Crude": "MCL",
    "E-mini Crude Oil": "QM", "E-mini Crude": "QM", "Light Sweet Crude Oil": "CL", "Crude Oil (CL)": "CL",
    # natgas
    "Micro Henry Hub Natural Gas": "MNG", "Micro Natural Gas": "MNG", "Micro Henry Hub": "MNG",
    "E-mini Natural Gas": "QG", "E-mini Henry Hub": "QG", "Henry Hub Natural Gas Futures": "NG",
    "Henry Hub Natural Gas (NG)": "NG",
    # metals
    "E-micro Gold": "MGC", "Micro Gold": "MGC", "1,000 oz. Silver": "SIL", "1,000-ounce silver": "SIL",
    "1,000 oz silver": "SIL", "Micro Silver": "SIL", "Micro Copper": "MHG", "COMEX Gold Futures": "GC",
    "COMEX gold futures": "GC", "Gold Futures": "GC", "Silver Futures": "SI", "Copper Futures": "HG",
    # fx
    "Micro EUR/USD": "M6E", "E-micro EUR/USD": "M6E", "Micro AUD/USD": "M6A", "E-micro AUD/USD": "M6A",
    "Euro FX Futures": "6E", "Euro FX": "6E", "EUR/USD futures": "6E", "Australian dollar futures": "6A",
    "Australian Dollar Futures": "6A", "AUD/USD futures": "6A",
    # crypto
    "Micro Bitcoin": "MBT", "Micro Ether": "MET", "Bitcoin Futures": "BTC", "bitcoin futures": "BTC",
    "Ether Futures": "ETH", "ether futures": "ETH",
    # equity
    "Micro E-mini Nasdaq-100": "MNQ", "Micro E-mini Nasdaq 100": "MNQ", "Micro Nasdaq": "MNQ",
    "E-mini Nasdaq-100": "NQ", "E-mini NASDAQ 100": "NQ", "E-mini Nasdaq 100": "NQ", "E-mini Nasdaq": "NQ",
    "E-mini NQ": "NQ", "Micro E-mini Russell 2000": "M2K", "Micro Russell": "M2K", "E-mini Russell 2000": "RTY",
    "E-mini Russell": "RTY", "Micro E-mini Dow": "MYM", "Micro Dow": "MYM", "E-mini Dow ($5)": "YM",
    "E-mini Dow": "YM",
    # rates
    "Micro 2-Year Yield": "2YY", "Micro 5-Year Yield": "5YY", "Micro 10-Year Yield": "10Y",
    "Micro 30-Year Yield": "30Y", "Short-Term U.S. Treasury Note": "ZT", "2-Year T-Note": "ZT",
    "2-Year Note": "ZT", "2 Yr Note": "ZT", "5-Year T-Note": "ZF", "5-Year Note": "ZF", "5 Yr Note": "ZF",
    "10-Year T-Note": "ZN", "10-Year Note": "ZN", "10 Yr Note": "ZN", "10-year T-note": "ZN",
    "10-year note futures": "ZN", "U.S. Treasury Bond Futures": "ZB", "Treasury Bond Futures": "ZB",
    "30-Year Bond": "ZB", "T-Bond futures": "ZB",
    # grains
    "Micro Corn": "MZC", "Micro Soybean Oil": "MZL", "Micro Soybean Meal": "MZM", "Micro Soybeans": "MZS",
    "Micro Soybean": "MZS", "Micro Wheat": "MZW", "Mini-sized Corn": "XC", "Mini-Corn": "XC",
    "Mini-sized Soybean": "XK", "Mini-sized Soybeans": "XK", "Mini-sized Wheat": "XW", "Mini-Wheat": "XW",
    "Soybean Oil Futures": "ZL", "Soybean Meal Futures": "ZM", "Corn Futures": "ZC", "Soybean Futures": "ZS",
    "Wheat Futures": "ZW",
}

# Exchange-internal or vendor tickers that identify a universe code.
ALT_TICKERS = {"TY": "ZN", "TU": "ZT", "FV": "ZF", "ER2": "RTY", "ER": "RTY", "EC": "6E", "AD": "6A",
               "XBT": "BTC"}

# Product codes outside the universe (E.28 other_products plus codes the F2 readers name).
OTHER_CODES = [
    "6C", "GF", "E7", "HO", "PA", "ZO", "SIC", "XAU", "ZQ", "LE", "ZR", "GE", "6N", "XAG", "SR3", "KE", "FESX",
    "6M", "NIY", "BIT", "YMR", "TN", "1OZ", "6B", "TNX", "BFF", "BRR", "TU", "RB", "MFF", "FDAX", "MBZ", "BZ",
    "MCLE", "MES", "QO", "ES", "PL", "UB", "NKD", "6S", "M6B", "VX", "J7", "HE", "6J", "EMD", "NNQ", "NES",
    "N2K", "NDOW", "ESQ", "NQQ", "RTQ", "NQT", "RLT", "YMT", "NQX", "RTX", "YMX", "BNB", "TBT", "MYB", "ENB",
    "EYB", "HH", "HTT", "WTT", "SGC", "SGU", "4GC", "LO", "ON", "LN", "QQQ", "SPX", "SPY", "BFF", "KC", "ZB1",
]

FIRM_NAMES = {
    "topstep": ["Topstepfunded LLC", "Topstepfunded", "Topstep Trader", "TopstepTrader", "TopstepX", "Topstep",
                "Patak Trading Partners"],
    "lucid": ["Lucid Trading", "LucidPro", "LucidFlex", "LucidDirect", "LucidLive", "Lucid"],
    "tradeify": ["Tradeify"],
    "mffu": ["My Funded Futures", "MyFundedFutures", "MFFU", "Blue Row Capital"],
    "bulenox": ["Bulenox"],
}

PLATFORMS = ["ProjectX/TopstepX", "ProjectX Gateway API", "ProjectX", "Tradovate", "Sierra Chart", "ATAS",
             "NinjaTrader", "Bookmap", "MotiveWave", "Jigsaw", "DeepChart", "Volumetrica/dxFeed", "Volumetrica",
             "dxFeed", "DTC Protocol Bridge", "CQG", "WealthCharts", "Tradesyncer", "Trader Composite",
             "TradingView", "MultiCharts", "R|Trader Pro", "R|Trader", "R|API", "Rithmic", "Hyperprop",
             "Quantower", "Tradesea"]

# Plan and stage names per firm -> neutral labels (applied before firm names).
PLAN_NAMES = {
    "topstep": [("Trading Combine", "plan P1 evaluation stage"), ("Express Funded Account", "plan P1 funded stage"),
                ("Live Funded Account", "plan P1 live stage"), ("Combine", "plan P1 evaluation stage"),
                ("XFA", "plan P1 funded stage"), ("LFA", "plan P1 live stage"),
                ("Standard Path", "payout path A"), ("Consistency Path", "payout path B"),
                ("Back2Funded", "reactivation option")],
    "lucid": [("LucidPro", "plan P1"), ("LucidFlex", "plan P2"), ("LucidDirect", "plan P3"),
              ("LucidLive", "live stage"), ("Daily plan", "plan P4"), ("pro_flex_direct", "plans P1-P3")],
    "tradeify": [("Growth", "plan P1"), ("Select", "plan P2"), ("Lightning", "plan P3")],
    "mffu": [("Builder", "plan P1"), ("Rapid Sim Funded", "plan P2 sim funded"), ("Pro Sim Funded",
             "plan P3 sim funded"), ("Rapid", "plan P2"), ("Core", "plan P4"), ("Blue Row Capital",
             "[live-account partner]")],
    "bulenox": [("Qualification Account", "plan P1 evaluation stage"), ("Master Account", "plan P1 funded stage"),
                ("Qualification", "plan P1 evaluation stage"), ("Master", "plan P1 funded stage"),
                ("Option 1", "risk option a"), ("Option 2", "risk option b"), ("Fast Track", "plan P2"),
                ("Momentum", "plan P3")],
}
MODELLED_PLAN = {
    "topstep": "plan P1 (50K, payout path A), evaluation and funded stages",
    "lucid": "plan P1 (50K, DLL on)",
    "tradeify": "plan P1 (50K)",
    "mffu": "plan P1 (50K, default MLL option)",
    "bulenox": "plan P1 (50K, risk option a: trailing drawdown, no daily loss limit)",
}

# Litigation identifiers (lead follow-up to for_lead item 10): party names, case numbers, court district, docket
# receipt numbers and the news site that names a suit. Facts (a suit exists, date, subject, status) stay.
LITIGATION = [
    (r"Vincent McCrudden", "[a plaintiff]"), (r"McCrudden", "[a plaintiff]"), (r"Wieland", "[a defendant]"),
    (r"\b\d{1,2}:\d{2}-[a-z]{2}-\d{3,6}(?:-[A-Z]{2,4})?\b", "[case number]"),
    (r"M\.D\. Fla\.?", "a US federal district court"),
    (r"receipt number \d+", "receipt number [redacted]"), (r"tradeinformer", "[news site]"),
]
LITIGATION_LEAK = ["McCrudden", "Vincent", "Wieland", r"\d{1,2}:\d{2}-[a-z]{2}-\d{3,6}", "00816", "38733",
                   r"M\.D\. Fla", "tradeinformer"]
