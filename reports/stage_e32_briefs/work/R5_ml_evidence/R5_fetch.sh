#!/usr/bin/env bash
# usage: R5_fetch.sh <url> <filename> [note]
set -u
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/R5_ml_evidence
url="$1"; fn="$2"; note="${3:-}"
out="$D/$fn"
curl -sL --max-time 90 -o "$out" -w "%{http_code} %{content_type}\n" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.9" "$url"
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$out" | cut -d' ' -f1)
printf "%s\t%s\t%s\tcurl\t%s\t%s\t%s\n" "$url" "$utc" "$pdt" "$sha" "$fn" "$note" >> "$D/log.tsv"
if file "$out" | grep -q PDF; then pdftotext -layout "$out" "$out.txt" 2>/dev/null; echo "pdf pages: $(pdfinfo "$out" 2>/dev/null | grep Pages)"; wc -l "$out.txt"; else echo "size $(wc -c < "$out")"; fi
