#!/usr/bin/env bash
# usage: M2_fetch.sh <url> <filename> <note>
# Downloads with curl (browser headers) into the M2 pages dir; pdftotext for PDFs; appends log.tsv.
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/M2_lead_lag
url="$1"; fn="$2"; note="${3:-}"
out="$P/$fn"
code=$(curl -sL --max-time 90 -o "$out" -w '%{http_code}' \
  -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/pdf,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' "$url")
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sz=$(stat -c %s "$out" 2>/dev/null || echo 0)
typ=$(file -b "$out" | cut -c1-40)
sha=$(sha256sum "$out" | cut -d' ' -f1)
[ -f "$P/log.tsv" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$P/log.tsv"
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$sha" "$fn" "http=$code size=$sz type=$typ; $note" >> "$P/log.tsv"
if [[ "$typ" == PDF* ]]; then pdftotext -layout "$out" "$out.txt" 2>/dev/null; echo "PDF ok http=$code size=$sz lines=$(wc -l < "$out.txt")"; else echo "http=$code size=$sz type=$typ"; fi
