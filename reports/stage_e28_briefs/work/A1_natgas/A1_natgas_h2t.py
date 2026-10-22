import sys, re, html
t = open(sys.argv[1], encoding='utf-8', errors='replace').read()
t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', t)
t = re.sub(r'(?i)<br\s*/?>|</(p|div|tr|li|h[1-6]|td|th)>', '\n', t)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
lines = [re.sub(r'[ \t\xa0]+', ' ', l).strip() for l in t.split('\n')]
print('\n'.join(l for l in lines if l))
