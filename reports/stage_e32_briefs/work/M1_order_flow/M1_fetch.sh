#!/usr/bin/env bash
# M1_fetch.sh <url> <outname> <note>  -- curl with browser headers, save raw to pages dir, log to log.tsv, pdftotext if PDF
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/M1_order_flow
url="$1"; out="$2"; note="${3:-}"
mkdir -p "$P"
curl -sL --max-time 90 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" \
  -H "Accept-Language: en-US,en;q=0.9" -o "$P/$out" "$url"
rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sz=$(stat -c %s "$P/$out" 2>/dev/null || echo 0)
sha=$(sha256sum "$P/$out" 2>/dev/null | cut -d' ' -f1)
typ=$(file -b "$P/$out" | cut -c1-40)
if echo "$typ" | grep -q PDF; then pdftotext -layout "$P/$out" "$P/${out%.pdf}.txt" 2>/dev/null; fi
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$url" "$utc" "$pdt" "curl" "$sha" "$out" "rc=$rc size=$sz type=$typ; $note" >> "$P/log.tsv"
echo "rc=$rc size=$sz type=$typ"
