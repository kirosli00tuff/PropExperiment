import os, sys, json, time, urllib.request, urllib.parse, re
email = ""
for line in open(".env"):
    if line.startswith("OPENALEX_EMAIL="): email = line.split("=",1)[1].strip().strip('"')
out_dir = sys.argv[1]
for tag, q in [a.split("|",1) for a in sys.argv[2:]]:
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({"search": q, "per-page": 25, "mailto": email})
    req = urllib.request.Request(url, headers={"User-Agent": "PropExperiment-research"})
    data = urllib.request.urlopen(req, timeout=60).read()
    open(f"{out_dir}/openalex_{tag}.json","wb").write(data)
    d = json.loads(data)
    print(f"== {tag} [{q}] count={d['meta']['count']}")
    for w in d["results"][:25]:
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
        print(f"  {w['publication_year']} | {(w['title'] or '')[:110]} | {src} | {w.get('doi')}")
    time.sleep(1.5)
