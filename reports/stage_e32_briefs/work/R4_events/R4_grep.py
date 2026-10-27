import re,sys,html
pat=sys.argv[2]; n=int(sys.argv[3]) if len(sys.argv)>3 else 12
t=open(sys.argv[1],errors='ignore').read()
if '<' in t[:2000]:
  t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S|re.I); t=html.unescape(re.sub(r'<[^>]+>',' ',t))
t=re.sub(r'\s+',' ',t)
for i,m in enumerate(re.finditer(r'.{0,200}(?:'+pat+r').{0,200}',t,flags=re.I)):
  if i>=n: break
  print('-',m.group(0))
