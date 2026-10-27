#!/bin/bash
# usage: R4_fetch.sh <url> <outfile-basename> <note>
set -u
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/R4_events
url="$1"; f="$2"; note="${3:-}"
curl -sL --max-time 90 -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o "$D/$f" -w '%{http_code} %{content_type} %{size_download}\n' "$url"
utc=$(date -u +%FT%TZ); pdt=$(TZ=America/Vancouver date +%FT%T%Z)
sha=$(sha256sum "$D/$f" | cut -d' ' -f1)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$sha" "$f" "$note" >> "$D/log.tsv"
case "$f" in *.pdf) pdftotext -layout "$D/$f" "$D/${f%.pdf}.txt" 2>/dev/null && wc -l "$D/${f%.pdf}.txt";; esac
file "$D/$f" | cut -c1-150
