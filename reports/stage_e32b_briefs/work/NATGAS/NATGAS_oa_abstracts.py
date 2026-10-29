"""NATGAS reader: fetch OpenAlex records by id, save raw JSON, print reconstructed abstracts (first 1500 chars)."""
import json, sys, urllib.request, urllib.parse, hashlib, datetime, subprocess, os
D = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/NATGAS"
email = ""
for line in open("/home/kiros-li/Documents/GitHub/PropExperiment/.env"):
    if line.startswith("OPENALEX_EMAIL="):
        email = line.split("=", 1)[1].strip().strip('"').strip("'")
out, ids = sys.argv[1], sys.argv[2:]
pub = "https://api.openalex.org/works?" + urllib.parse.urlencode({"filter": "openalex:" + "|".join(ids), "per-page": "50"})
url = pub + ("&mailto=" + urllib.parse.quote(email) if email else "")
raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research"}), timeout=60).read()
open(os.path.join(D, out), "wb").write(raw)
utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
pdt = subprocess.run(["date", "+%Y-%m-%dT%H:%M:%S%Z"], env={"TZ": "America/Vancouver"}, capture_output=True, text=True).stdout.strip()
with open(os.path.join(D, "log.tsv"), "a") as f:
    f.write(f"{pub}\t{utc}\t{pdt}\topenalex api (mailto omitted)\t{hashlib.sha256(raw).hexdigest()}\t{out}\tabstract records\n")
for w in json.loads(raw)["results"]:
    inv = w.get("abstract_inverted_index") or {}
    pos = sorted((p, t) for t, ps in inv.items() for p in ps)
    ab = " ".join(t for _, t in pos)
    au = ", ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:5])
    print("==", w["id"].split("/")[-1], w["publication_year"], w.get("doi"), "|", au, "|", w["title"])
    print(ab[:1500])
