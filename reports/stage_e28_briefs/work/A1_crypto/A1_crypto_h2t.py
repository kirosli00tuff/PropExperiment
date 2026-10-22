import sys, re, html
t = open(sys.argv[1], encoding='utf-8', errors='replace').read()
t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', t)
t = re.sub(r'(?i)<br\s*/?>|</(p|div|li|tr|h\d|td|th)>', '\n', t)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
t = re.sub(r'[ \t\xa0]+', ' ', t)
t = re.sub(r'\n\s*\n+', '\n', t)
print(t)
