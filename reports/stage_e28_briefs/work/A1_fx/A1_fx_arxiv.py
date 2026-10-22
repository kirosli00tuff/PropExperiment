import sys,re,urllib.request,urllib.parse,time
for q in sys.argv[1:]:
    u='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'max_results':15})
    s=urllib.request.urlopen(u,timeout=60).read().decode()
    print('## ',q)
    for e in s.split('<entry>')[1:]:
        t=re.sub(r'\s+',' ',re.search(r'<title>(.*?)</title>',e,re.S).group(1)); i=re.search(r'<id>(.*?)</id>',e).group(1); d=re.search(r'<published>(.{4})',e).group(1)
        print(d,i.split('/abs/')[1],t[:130])
    time.sleep(3)
