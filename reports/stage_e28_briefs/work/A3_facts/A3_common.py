"""Stage E.28 A3 (FactTable): shared constants and helpers for the fact-table, masking and scoring scripts.

Facts only. Nothing here scores a qualitative criterion. Candidate codes follow spec section 0 as the A1 readers
resolved them (reports/stage_e28_briefs/A1_<family>.json).
"""
import hashlib
import json
import os
import re

REPO = '/home/kiros-li/Documents/GitHub/PropExperiment'
BR = os.path.join(REPO, 'reports', 'stage_e28_briefs')
SPEC = os.path.join(REPO, 'reports', 'stage_e28_ranking_spec.md')
SPEC_SHA256 = '89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f'

FAMILIES = {
    'crude': ['MCL', 'QM', 'CL'],
    'natgas': ['MNG', 'QG', 'NG'],
    'metals': ['MGC', 'GC', 'SIL', 'SI', 'MHG', 'HG'],
    'fx': ['M6E', '6E', 'M6A', '6A'],
    'crypto': ['MET', 'ETH', 'MBT', 'BTC'],
    'equity': ['M2K', 'RTY', 'MYM', 'YM', 'MNQ', 'NQ'],
    'rates': ['2YY', '5YY', '10Y', '30Y', 'ZT', 'ZF', 'ZN', 'ZB'],
    'grains': ['MZC', 'MZS', 'MZW', 'MZL', 'MZM', 'XC', 'XK', 'XW', 'ZC', 'ZS', 'ZW', 'ZL', 'ZM'],
}
CANDIDATES = [c for fam in FAMILIES.values() for c in fam]
FAMILY_OF = {c: f for f, cs in FAMILIES.items() for c in cs}

# Product class used for the R criterion (restrictions differ by class at some firms).
CLASS_OF_FAMILY = {'crude': 'crude_oil', 'natgas': 'natural_gas', 'metals': 'metals', 'fx': 'fx',
                   'crypto': 'crypto', 'equity': 'equity_index', 'rates': 'rates', 'grains': 'grains'}
CLASS_OF = {c: CLASS_OF_FAMILY[FAMILY_OF[c]] for c in CANDIDATES}

# OC-1 (lead decision): owned sibling on the SAME underlying price for sigma_1m and R_d in ticks.
# Micro/mini grains only where the A1 price units match (checked in the builder).
OC1_SIBLING = {
    'MNQ': 'NQ', 'M2K': 'RTY', 'MYM': 'YM', 'MNG': 'NG', 'QG': 'NG', 'QM': 'CL', 'M6E': '6E', 'M6A': '6A',
    'BTC': 'MBT', 'XC': 'ZC', 'XK': 'ZS', 'XW': 'ZW', 'MZC': 'ZC', 'MZS': 'ZS', 'MZW': 'ZW', 'MZL': 'ZL', 'MZM': 'ZM',
}
# Same-underlying siblings (for the informational C4 jump-transfer variant only; not part of OC-1).
SAME_UNDERLYING_OWNED = dict(OC1_SIBLING)

FIRMS = ['topstep', 'lucid', 'tradeify', 'mffu', 'bulenox']
FIRM_NAME = {'topstep': 'Topstep', 'lucid': 'Lucid Trading', 'tradeify': 'Tradeify', 'mffu': 'My Funded Futures (MFFU)',
             'bulenox': 'Bulenox'}
# Alphabetical key used by the tie rule ("then firm name, alphabetically").
FIRM_SORT_NAME = {'topstep': 'Topstep', 'lucid': 'Lucid Trading', 'tradeify': 'Tradeify', 'mffu': 'My Funded Futures',
                  'bulenox': 'Bulenox'}
PLATFORMS = ['ProjectX/TopstepX', 'Tradovate', 'Rithmic', 'NinjaTrader', 'CQG', 'Volumetrica/dxFeed', 'WealthCharts']


def spec_sha256():
    with open(SPEC, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(name):
    with open(os.path.join(BR, name)) as fh:
        return json.load(fh)


def fact(value, unit=None, provenance=None, u=False, flags=None, note=None, quote=None, window=None):
    """One fact cell: {value, unit, provenance, u, flags, note, quote, window}."""
    d = {'value': value, 'unit': unit, 'provenance': provenance, 'u': bool(u), 'flags': list(flags or [])}
    if window is not None:
        d['window'] = window
    if quote:
        d['quote'] = str(quote)[:400]
    if note:
        d['note'] = str(note)[:600]
    return d


# ----------------------------------------------------------------------------------------------------------------
# Masking. Product codes of candidates map to contract labels (C01..); other product codes map to X labels; firm,
# platform, plan, exchange, agency and underlying names map to neutral tokens.
# ----------------------------------------------------------------------------------------------------------------
OTHER_CODES = ['ES', 'MES', 'NKD', 'EMD', 'E7', 'J7', '6B', '6C', '6J', '6N', '6S', '6M', 'M6B', 'TN', 'UB', 'TY', 'TU',
               'FV', 'US', 'KE', 'HE', 'LE', 'GF', 'PL', 'PA', 'RB', 'HO', 'BZ', 'MBZ', '1OZ', 'SIC', 'MCLE', 'QO',
               'ZQ', 'SR3', 'GE', 'ZR', 'ZO', 'BIT', 'BFF', 'MFF', 'NIY', 'VX', 'FDAX', 'FESX', 'BRR', 'ETHUSD_RR',
               'TNX', 'YMR', 'XAU', 'XAG']
# Codes whose word also has another meaning in some families (handled by family context).
AMBIGUOUS_CODES = {'ETH': {'rates', 'equity', 'grains', 'metals', 'fx', 'natgas', 'crude'},  # ETH = electronic hours
                   'US': set(FAMILIES)}  # 'US' = United States everywhere; never masked as a code

FIRM_PATTERNS = [r'Topstep(?:X|Trader|funded(?: LLC)?)?', r'Patak(?: Trading Partners)?', r'Lucid(?: ?Trading)?',
                 r'Lucid(?:Pro|Flex|Direct|Daily|BLACK|Black)', r'Tradeify', r'My ?Funded ?Futures', r'MyFunded ?Futures',
                 r'MFFU', r'Bulenox(?: LLC)?', r'Blue Row Capital', r'Sim2Funded(?: Solutions)?(?: LLC)?']
PLATFORM_PATTERNS = {   # canonical platform name -> patterns; labels P01.. are assigned in random order (seed 28)
    'ProjectX/TopstepX': [r'Project ?X(?: Gateway)?(?: API)?', r'TopstepX', r'projectx_topstepx'],
    'Tradovate': [r'Tradovate(?: API)?', r'tradovateapi'],
    'Rithmic': [r'Rithmic(?: Paper Trading)?', r'R ?\| ?(?:Trader Pro|API\+?|Protocol API|Diamond API|Trader)', r'R\|API'],
    'NinjaTrader': [r'NinjaTrader(?: 8)?', r'Sim101', r'ninjatrader_sim_engine'],
    'CQG': [r'CQG'],
    'Volumetrica/dxFeed': [r'Volumetrica', r'VolSys', r'VolBook', r'dxFeed', r'volumetrica_dxfeed'],
    'WealthCharts': [r'WealthCharts'],
    'Quantower': [r'Quantower'], 'TradingView': [r'TradingView'], 'Sierra Chart': [r'Sierra ?Chart'],
    'MotiveWave': [r'MotiveWave'], 'ATAS': [r'ATAS'], 'Bookmap': [r'Bookmap'], 'Jigsaw': [r'Jigsaw'],
    'MultiCharts': [r'MultiCharts'], 'Tradesea': [r'Tradesea'], 'Hyperprop': [r'Hyperprop'],
    'DeepChart': [r'DeepChart(?:/DeepDom)?', r'DeepDom'], 'Tradesyncer': [r'Tradesyncer'],
    'Trader Composite': [r'Trader Composite'], 'DTC Protocol Bridge': [r'DTC Protocol Bridge'],
}
PAYMENT_PATTERNS = [r'Riseworks', r'\bRise\b', r'\bWise\b', r'WorkMarket(?: by ADP)?', r'Sumsub', r'\bPlane\b',
                    r'Plaid', r'PayPal']
PLAN_PATTERNS = [r'Trading Combine(?:®)?', r'Express Funded Account(?:®)?', r'\bXFA\b', r'\bLFA\b', r'Live Funded Account',
                 r'Back2Funded', r'\bBuilder(?: Plan)?\b', r'\bGrowth(?:™)?\b', r'\bLightning\b', r'\bSelect\b',
                 r'Qualification Account', r'Master Account', r'Fast Track', r'Momentum', r'\bRapid\b', r'\bPro\b',
                 r'\bFlex\b', r'\bDirect\b', r'Standard Path', r'No Activation Fee Path', r'\bCombine\b', r'\bMaster\b']
EXCHANGE_PATTERNS = [r'CME Group and Nasdaq', r'NYMEX', r'COMEX', r'CBOT', r'CBoT', r'Chicago Board of Trade', r'New York Mercantile Exchange',
                     r'Eurex', r'ICE Futures(?: Europe| U\.S\.)?', r'\bICE\b', r'Binance', r'Bybit', r'Mt\. ?Gox',
                     r'BrokerTec', r'\bEBS\b', r'Coinbase', r'Kraken', r'EEX']
AGENCY_PATTERNS = [r'\bEIA\b', r'Energy Information Administration', r'\bUSDA\b', r'\bNASS\b', r'\bFAS\b', r'WASDE',
                   r'\bOPEC\+?', r'\bECB\b', r'\bRBA\b', r'Reserve Bank of Australia', r'European Central Bank',
                   r'Baker Hughes', r'American Petroleum Institute', r'U\.S\. Treasury', r'Treasury Department',
                   r'CF Benchmarks', r'Weekly Petroleum Status Report', r'WPSR', r'Weekly Natural Gas Storage Report',
                   r'WNGSR', r'Crop Progress', r'Export Sales', r'Grain Stocks', r'Crop Production']
UNDERLYING_PATTERNS = [
    r'Light Sweet Crude(?: Oil)?', r'West Texas Intermediate', r'\bWTI\b', r'\bBrent\b', r'crude(?: oil)?', r'\boil\b',
    r'petroleum', r'Henry Hub', r'natural gas', r'nat(?:ural)? ?gas', r'\bLNG\b', r'\bgas\b', r'gasoline', r'heating oil',
    r'\bgold\b', r'\bsilver\b', r'\bcopper\b', r'platinum', r'palladium', r'precious metals?', r'base metals?',
    r'\bmetals?\b', r'Euro FX', r'EUR/USD', r'AUD/USD', r'\bEUR\b', r'\bAUD\b', r'\beuros?\b', r'Australian dollars?',
    r'\bAussie\b', r'\byen\b', r'\bJPY\b', r'\bpeso\b', r'sterling', r'\bpound sterling\b', r'Swiss franc',
    r'Canadian dollar', r'currenc(?:y|ies)', r'\bFX\b', r'foreign exchange', r'\bpips?\b', r'bitcoins?', r'\bether(?:eum)?\b',
    r'crypto(?:currenc(?:y|ies))?', r'\bBTC/USD\b', r'\bETH/USD\b', r'\bUSDT\b', r'stablecoin', r'perpetuals?',
    r'Nasdaq(?:-100| 100)?', r'NASDAQ(?:-100| 100)?', r'Russell(?: 2000)?', r'Dow Jones(?: Industrial Average)?',
    r'\bDow\b', r'\bDJIA\b', r'S&P(?: 500)?', r'E-?mini', r'E-?micro', r'equity index', r'equit(?:y|ies)', r'\bstocks?\b',
    r'small-?caps?', r'Treasur(?:y|ies)', r'T-?Notes?', r'T-?Bonds?', r'\bUltra\b', r'\byields?\b', r'\bbonds?\b',
    r'\b(?:2|5|7|10|20|30)-?Y(?:ea)?r\b', r'basis points?', r'\bbps?\b', r'\bcorn\b', r'soybeans?', r'\bsoy\b',
    r'soybean (?:oil|meal)', r'\bmeal\b', r'\bwheat\b', r'\bSRW\b', r'\bHRW\b', r'\bgrains?\b', r'agricultur(?:e|al)',
    r'\bags?\b', r'livestock', r'\bcattle\b', r'\bhogs?\b', r'bushels?', r'barrels?', r'MMBtu', r'troy ounces?',
    r'\bounces?\b', r'\boz\b', r'\bpounds?\b', r'\blbs?\b', r'short tons?', r'\bcents? per\b', r'\benerg(?:y|ies)\b',
    r'interest rates?', r'\brates\b', r'\btenors?\b', r'auctions?', r'\bcoupons?\b', r'commodit(?:y|ies)',
    r'Asian hours', r'European hours',
]

TOKEN = {'firm': '[FIRM]', 'payment': '[PAYMENT-SERVICE]', 'plan': '[PLAN]', 'exchange': '[EXCHANGE]',
         'agency': '[AGENCY]', 'underlying': '[U]'}


def _compile(patterns, flags=re.IGNORECASE):
    return [re.compile(p, flags) for p in sorted(patterns, key=len, reverse=True)]


_FIRM_RE = _compile(FIRM_PATTERNS)
_PAY_RE = _compile(PAYMENT_PATTERNS, 0)
_PLAN_RE = _compile(PLAN_PATTERNS, 0)
_EXCH_RE = _compile(EXCHANGE_PATTERNS, 0)
_AGENCY_RE = _compile(AGENCY_PATTERNS, 0)
_UND_RE = _compile(UNDERLYING_PATTERNS)


class Masker:
    """Replace product codes, product names, firm, platform and other identifying names by labels."""

    def __init__(self, contract_label, other_label, firm_label, product_names, code_to_class=None,
                 class_tokens=False, platform_label=None):
        self.contract_label = contract_label        # candidate code -> 'Cnn'
        self.other_label = other_label              # other code -> 'Xnn'
        self.firm_label = firm_label                # firm key -> 'Fnn'
        self.code_to_class = code_to_class or {}    # code -> class name (firm sheets use class tokens, not labels)
        self.class_tokens = class_tokens
        self.platform_label = platform_label or {}
        names = sorted(set(n for n in product_names if n), key=len, reverse=True)
        self.name_re = [re.compile(re.escape(n), re.IGNORECASE) for n in names]
        codes = sorted(set(list(contract_label) + list(other_label)), key=len, reverse=True)
        self.code_re = re.compile(r'(?<![A-Za-z0-9_])(' + '|'.join(re.escape(c) for c in codes) + r')(?![A-Za-z0-9_])')

    def _code_sub(self, family):
        def sub(m):
            c = m.group(1)
            if c in AMBIGUOUS_CODES and (family in AMBIGUOUS_CODES[c] or family is None):
                return c if c != 'ETH' else '[electronic-hours]'
            if self.class_tokens:
                cls = self.code_to_class.get(c, 'other')
                return f'[{cls} product]'
            if c in self.contract_label:
                return self.contract_label[c]
            return self.other_label.get(c, '[X]')
        return sub

    def __call__(self, text, family=None, refs=True):
        if text is None:
            return None
        s = text if isinstance(text, str) else json.dumps(text, ensure_ascii=False)
        if refs:
            # URLs, paths and file or snake_case reference names can carry product or firm names: drop them first
            s = re.sub(r'https?://\S+', '[URL]', s)
            s = re.sub(r'(?<![\w\[])(?:reports|pages|work|data|docs|rules|prop_econ|A[0-3]_\w+)/[\w.*/-]+', '[FILE]', s)
            s = re.sub(r'\b[\w.-]+\.(?:txt|html?|pdf|json|xml|md|tsv|js)\b', '[FILE]', s)
            s = re.sub(r'\b[A-Za-z0-9]+(?:_[A-Za-z0-9.*-]+)+\b', '[REF]', s)
            s = re.sub(r'\b(?:Stage )?E\.\d+[a-z]?\b', '[STAGE]', s)   # program stage ids can identify a product
        for r in self.name_re:
            s = r.sub('[PRODUCT]', s)
        s = self.code_re.sub(self._code_sub(family), s)
        for name, pats in PLATFORM_PATTERNS.items():
            lab = self.platform_label.get(name, '[PLATFORM]')
            for p in sorted(pats, key=len, reverse=True):
                s = re.sub(p, lab, s, flags=re.IGNORECASE)
        for r in _FIRM_RE:
            s = r.sub(TOKEN['firm'], s)
        for r in _PAY_RE:
            s = r.sub(TOKEN['payment'], s)
        for r in _PLAN_RE:
            s = r.sub(TOKEN['plan'], s)
        for r in _EXCH_RE:
            s = r.sub(TOKEN['exchange'], s)
        for r in _AGENCY_RE:
            s = r.sub(TOKEN['agency'], s)
        if not self.class_tokens:
            for r in _UND_RE:
                s = r.sub(TOKEN['underlying'], s)
        return s
