import sys, re, html
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
s = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', s)
s = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</tr>|</h\d>|</div>', '\n', s)
s = re.sub(r'<[^>]+>', ' ', s)
s = html.unescape(s)
s = re.sub(r'[ \t]+', ' ', s); s = re.sub(r'\n\s*\n+', '\n', s)
open(sys.argv[2], 'w').write(s)
print(len(s))
