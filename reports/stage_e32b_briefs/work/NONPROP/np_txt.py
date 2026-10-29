import sys,re,html
for f in sys.argv[1:]:
    s=open(f,errors='ignore').read()
    s=re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>','',s)
    s=re.sub(r'(?i)</(tr|p|div|li|h\d|table|thead|tbody|section)>','\n',s)
    s=re.sub(r'(?i)</t[dh]>',' | ',s)
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s)
    s=re.sub(r'[ \t]+',' ',s)
    s=re.sub(r'\n\s*\n+','\n',s)
    open(f+'.txt','w').write(s)
    print(f,len(s))
