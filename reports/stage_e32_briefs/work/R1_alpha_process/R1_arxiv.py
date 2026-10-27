import re,sys,urllib.request,time
for q in sys.argv[1:]:
    u="https://export.arxiv.org/api/query?search_query="+q+"&max_results=6"
    t=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})).read().decode()
    for e in t.split('<entry>')[1:]:
        i=re.search(r'<id>(.*?)</id>',e).group(1);ti=re.sub(r'\s+',' ',re.search(r'<title>(.*?)</title>',e,re.S).group(1))
        print(i,'|',ti[:110])
    print('---'); time.sleep(3)
