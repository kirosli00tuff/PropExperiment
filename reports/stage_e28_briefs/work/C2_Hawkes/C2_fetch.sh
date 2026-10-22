#!/usr/bin/env bash
# usage: C2_fetch.sh <url> <filename> <note>
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_Hawkes
url="$1"; f="$2"; note="${3:-}"
curl -sL --max-time 90 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.9" \
  -o "$P/$f" "$url"
rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$P/$f" | cut -d' ' -f1); sz=$(stat -c%s "$P/$f")
typ=$(file -b "$P/$f" | cut -c1-30)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s (rc=%s,%sB,%s)\n' "$url" "$utc" "$pdt" "$sha" "$f" "$note" "$rc" "$sz" "$typ" >> "$P/log.tsv"
if [[ "$f" == *.pdf ]] && [[ "$typ" == PDF* ]]; then pdftotext -layout "$P/$f" "$P/${f%.pdf}.txt" 2>/dev/null; echo "$f ok $sz $(wc -l < "$P/${f%.pdf}.txt") lines"; else echo "$f rc=$rc $sz $typ"; fi
sleep 3
