import sys,urllib.request,urllib.parse,re,time
qs=sys.argv[1:]
out=open('work/A1_rates/A1_rates_arxiv_hits.txt','a')
for q in qs:
    url='http://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'max_results':40})
    x=urllib.request.urlopen(url,timeout=60).read().decode()
    ents=re.findall(r'<entry>(.*?)</entry>',x,re.S)
    out.write(f'## {q} n={len(ents)}\n')
    for e in ents:
        t=re.sub(r'\s+',' ',re.search(r'<title>(.*?)</title>',e,re.S).group(1))
        i=re.search(r'<id>(.*?)</id>',e).group(1); p=re.search(r'<published>(.*?)</published>',e).group(1)[:10]
        out.write(f'{i}\t{p}\t{t}\n')
    print(q,len(ents)); time.sleep(4)
