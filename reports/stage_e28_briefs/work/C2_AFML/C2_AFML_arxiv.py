import re,sys,urllib.request,time
for q in sys.argv[1:]:
    u="https://export.arxiv.org/api/query?search_query="+q+"&max_results=25"
    t=urllib.request.urlopen(u,timeout=60).read().decode()
    print('### ',q)
    for e in re.findall(r'<entry>(.*?)</entry>',t,re.S):
        i=re.search(r'<id>(.*?)</id>',e).group(1).split('/abs/')[-1]
        ti=' '.join(re.search(r'<title>(.*?)</title>',e,re.S).group(1).split())
        print(i,'|',ti[:110])
    time.sleep(3)
