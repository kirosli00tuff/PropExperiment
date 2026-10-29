#!/usr/bin/env bash
# NATGAS reader private fetch helper: NATGAS_fetch.sh <url> <outfile_basename> <note>
# Saves raw page under pages/NATGAS, appends a log.tsv row (UTC, PDT, method, sha256).
set -u
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/NATGAS
url="$1"; out="$2"; note="${3:-}"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
code=$(curl -sL --max-time 60 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o "$D/$out" -w '%{http_code}' "$url")
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$D/$out" 2>/dev/null | cut -d' ' -f1)
sz=$(stat -c %s "$D/$out" 2>/dev/null)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "curl http=$code" "$sha" "$out" "$note size=$sz" >> "$D/log.tsv"
case "$out" in *.pdf) pdftotext -layout "$D/$out" "$D/$out.txt" 2>/dev/null ;; esac
echo "http=$code size=$sz sha=${sha:0:12} file=$out"
