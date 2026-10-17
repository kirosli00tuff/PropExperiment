#!/bin/bash
# usage: fetch.sh <id> <url> <outfile_basename>
# saves raw page under datasrc_pages/, appends to fetch_log.tsv: id, url, utc, method, file, sha256, http, bytes
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e22_briefs/datasrc_pages
id="$1"; url="$2"; f="$D/$3"
case "$url" in *cmegroup.com*) echo "REFUSED cmegroup"; exit 1;; esac
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
code=$(curl -sS -L --max-time 60 -o "$f" -w '%{http_code}' -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' "$url")
sha=$(sha256sum "$f" | cut -d' ' -f1); n=$(wc -c < "$f")
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\t%s\n' "$id" "$url" "$ts" "$3" "$sha" "$code" "$n" >> "$D/fetch_log.tsv"
echo "$id $code $n $sha $ts"
