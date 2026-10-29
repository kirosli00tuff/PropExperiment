"""NATGAS reader: one OpenAlex search; saves raw JSON under pages/NATGAS and prints id, year, venue, title only.
Usage: python NATGAS_openalex.py <outfile> <search string> [from_year]"""
import json, os, sys, urllib.parse, urllib.request, hashlib, datetime, subprocess
D = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/NATGAS"
email = ""
for line in open("/home/kiros-li/Documents/GitHub/PropExperiment/.env"):
    if line.startswith("OPENALEX_EMAIL="):
        email = line.split("=", 1)[1].strip().strip('"').strip("'")
out, q = sys.argv[1], sys.argv[2]
fy = sys.argv[3] if len(sys.argv) > 3 else "2015"
params = {"filter": f"title_and_abstract.search:{q},from_publication_date:{fy}-01-01", "per-page": "50",
          "select": "id,doi,title,publication_year,primary_location,cited_by_count"}
url_public = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
url = url_public + ("&mailto=" + urllib.parse.quote(email) if email else "")
raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research"}), timeout=60).read()
open(os.path.join(D, out), "wb").write(raw)
sha = hashlib.sha256(raw).hexdigest()
utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
pdt = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%Z"], env={"TZ": "America/Vancouver"}, capture_output=True, text=True).stdout.strip()
with open(os.path.join(D, "log.tsv"), "a") as f:
    f.write(f"{url_public}\t{utc}\t{pdt}\topenalex api (mailto omitted from log)\t{sha}\t{out}\tOpenAlex search\n")
d = json.loads(raw)
print("count", d["meta"]["count"])
for w in d["results"]:
    v = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
    print(w["publication_year"], w["id"].split("/")[-1], (v or "")[:30], "|", (w["title"] or "")[:110])
