#!/bin/bash
# usage: R3a_fetch.sh <url> <outfile_basename> <note>
set -u
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/R3a_crush
url="$1"; out="$D/$2"; note="${3:-}"
curl -sL --max-time 90 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" -H "Accept: text/html,application/xhtml+xml,application/pdf,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.9" -o "$out" -w "%{http_code} %{content_type} %{size_download}\n" "$url"
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$out" | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "curl" "$sha" "$2" "$note" >> "$D/log.tsv"
file "$out" | cut -c1-120
if file "$out" | grep -q PDF; then pdftotext -layout "$out" "$out.txt" && wc -w "$out.txt"; fi
