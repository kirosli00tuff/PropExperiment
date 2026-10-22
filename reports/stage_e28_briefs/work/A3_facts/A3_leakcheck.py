"""A3 helper: search the masked sheets for identifying strings that survived masking."""
import json, re, sys
sys.path.insert(0, '.')
from A3_common import CANDIDATES, PLATFORM_PATTERNS, BR
words = (['Topstep', 'Lucid', 'Tradeify', 'MFFU', 'Funded Futures', 'Bulenox', 'Nasdaq', 'Russell', 'Dow', 'Treasury',
          'crude', 'gold', 'silver', 'copper', 'bitcoin', 'ether', 'corn', 'soy', 'wheat', 'NYMEX', 'COMEX', 'CBOT',
          'EIA', 'USDA', 'Henry Hub', 'WTI', 'euro', 'Australian', 'yen', 'S&P', 'bushel', 'barrel', 'ounce', 'MMBtu',
          'grain', 'energy', 'metal', 'crypto', 'equity', 'currency', 'bond', 'note futures', 'yield'] +
         [p for v in PLATFORM_PATTERNS.values() for p in v if p.isalpha()])
for name in sys.argv[1:]:
    s = open(f'{BR}/{name}').read()
    print('==', name)
    for c in CANDIDATES:
        n = len(re.findall(r'(?<![A-Za-z0-9_])' + re.escape(c) + r'(?![A-Za-z0-9_])', s))
        if n: print('  code', c, n)
    for w in words:
        hits = [m.start() for m in re.finditer(re.escape(w), s, re.IGNORECASE)]
        if hits:
            ctx = s[max(0, hits[0]-60):hits[0]+60].replace('\n', ' ')
            print('  word', w, len(hits), '|', ctx)
