import re,html,sys
t=open(sys.argv[1],errors='ignore').read()
m=re.search(r'<article.*?</article>',t,flags=re.S)
s=m.group(0) if m else t
s=re.sub(r'<script.*?</script>|<style.*?</style>','',s,flags=re.S)
s=re.sub(r'</t[dh]>',' | ',s); s=re.sub(r'</tr>','\n',s); s=re.sub(r'<br\s*/?>|</p>|</h\d>|</li>|</div>',' \n',s)
s=html.unescape(re.sub(r'<[^>]+>','',s)); s=re.sub(r'[ \t]+',' ',s); s=re.sub(r'\n\s*(\|\s*)?\n+','\n',s)
open(sys.argv[1]+'.body.txt','w').write(s)
print(sys.argv[1], len(s.splitlines()))
