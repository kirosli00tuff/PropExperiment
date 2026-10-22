"""OpenAlex title/abstract search; prints id, year, venue, cites, title. Email read from .env (never printed)."""
import json, sys, urllib.parse, urllib.request, time
from pathlib import Path
email = ""
for line in Path(".env").read_text().splitlines():
    if line.startswith("OPENALEX_EMAIL="):
        email = line.split("=", 1)[1].strip().strip('"')
out = []
for q in sys.argv[1:]:
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
        {"search": q, "per-page": 12, "mailto": email, "select": "id,doi,title,publication_year,primary_location,cited_by_count,open_access"})
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.load(r)
    print(f"## {q} ({d['meta']['count']})")
    for w in d["results"]:
        v = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
        oa = (w.get("open_access") or {}).get("oa_url") or ""
        print(f"{w['publication_year']} | {w['cited_by_count']} | {v[:40]} | {(w['title'] or '')[:120]} | {w.get('doi') or ''} | {oa[:90]}")
    time.sleep(1)
