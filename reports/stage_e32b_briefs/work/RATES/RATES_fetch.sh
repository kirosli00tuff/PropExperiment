#!/usr/bin/env bash
# RATES_fetch.sh <url> <outfile_basename> <note>
# curl with browser headers into pages/RATES, pdftotext if PDF, log to log.tsv
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/RATES
mkdir -p "$P"
LOG="$P/log.tsv"
[ -f "$LOG" ] || printf 'url\tfetched_utc\tfetched_pdt\tmethod\tsha256\tfile\tnote\n' > "$LOG"
url="$1"; out="$2"; note="${3:-}"
curl -sL --max-time 90 -o "$P/$out" \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' "$url"
rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
if [ $rc -ne 0 ] || [ ! -s "$P/$out" ]; then
  printf '%s\t%s\t%s\tcurl\tFAILED\t%s\trc=%s %s\n' "$url" "$utc" "$pdt" "$out" "$rc" "$note" >> "$LOG"; echo "FAIL rc=$rc"; exit 1; fi
sha=$(sha256sum "$P/$out" | cut -c1-64)
kind=$(file -b "$P/$out" | cut -c1-40)
if echo "$kind" | grep -qi pdf; then pdftotext -layout "$P/$out" "$P/$out.txt" 2>/dev/null; fi
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$sha" "$out" "$note" >> "$LOG"
echo "OK $out $(stat -c %s "$P/$out")B $kind sha=${sha:0:12}"
