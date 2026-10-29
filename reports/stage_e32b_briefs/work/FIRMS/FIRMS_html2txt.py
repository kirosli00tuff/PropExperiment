"""Convert a saved HTML file to plain text lines (scripts/styles dropped). Usage: in out"""
import sys
from bs4 import BeautifulSoup
raw = open(sys.argv[1], 'rb').read().decode('utf-8', 'replace')
soup = BeautifulSoup(raw, 'html.parser')
for t in soup(['script', 'style', 'noscript', 'svg']):
    t.decompose()
text = soup.get_text('\n')
lines = [ln.strip() for ln in text.splitlines()]
out = [ln for ln in lines if ln]
open(sys.argv[2], 'w').write('\n'.join(out) + '\n')
