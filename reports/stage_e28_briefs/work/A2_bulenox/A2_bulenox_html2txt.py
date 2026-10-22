import re, html, sys
for f in sys.argv[1:]:
    s = open(f, encoding='utf-8', errors='replace').read()
    s = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', '', s, flags=re.S)
    t = html.unescape(re.sub(r'<[^>]+>', '\n', s))
    t = '\n'.join(l.strip() for l in t.splitlines() if l.strip())
    open(f + '.txt', 'w').write(t)
    print(f, len(t.splitlines()))
