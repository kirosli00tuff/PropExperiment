#!/usr/bin/env bash
# usage: fetch.sh <url> <outfile-basename>; appends a line to fetch_log.tsv
set -u
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e22_briefs/carver_pages
url="$1"; out="$D/$2"
t=$(date -u +%Y-%m-%dT%H:%M:%SZ)
code=$(curl -sS -L -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" -o "$out" -w "%{http_code}" "$url")
sz=$(stat -c %s "$out" 2>/dev/null || echo 0)
sha=$(sha256sum "$out" | cut -d' ' -f1)
printf "%s\t%s\t%s\tcurl\t%s\t%s\t%s\n" "$2" "$url" "$t" "$code" "$sz" "$sha" >> "$D/fetch_log.tsv"
echo "$2 $code $sz $sha $t"
