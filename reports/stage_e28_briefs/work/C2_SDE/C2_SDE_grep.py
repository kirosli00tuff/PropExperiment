import re,sys,html
# usage: C2_SDE_grep.py file pattern [width] [max]
f,pat=sys.argv[1],sys.argv[2]; w=int(sys.argv[3]) if len(sys.argv)>3 else 200; mx=int(sys.argv[4]) if len(sys.argv)>4 else 4
t=open(f,encoding='utf-8',errors='ignore').read()
if f.endswith('.html'):
    t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',t,flags=re.S); t=html.unescape(re.sub(r'<[^>]+>',' ',t))
t=re.sub(r'\s+',' ',t)
for m in list(re.finditer(pat,t,flags=re.I))[:mx]:
    print('::',t[max(0,m.start()-w):m.end()+w])
