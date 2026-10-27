#!/bin/bash
# usage: M5b_fetch.sh <url> <filename> [note]  -- curl with browser headers, save under pages/M5b_power, log
set -u
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/M5b_power
url="$1"; fn="$2"; note="${3:-}"
curl -sL --max-time 90 -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36' \
 -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' \
 -o "$D/$fn" -w '%{http_code} %{content_type}\n' "$url"
sz=$(stat -c %s "$D/$fn" 2>/dev/null || echo 0)
sha=$(sha256sum "$D/$fn" | cut -d' ' -f1)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\n' "$url" "$(date -u +%FT%TZ)" "$(TZ=America/Vancouver date +%FT%T%Z)" "$sha" "$fn" "size=$sz $note" >> "$D/log.tsv"
echo "size=$sz"; file -b "$D/$fn" | cut -c1-60
case "$fn" in *.pdf) pdftotext -layout "$D/$fn" "$D/${fn%.pdf}.txt" 2>/dev/null && wc -l "$D/${fn%.pdf}.txt";; esac
