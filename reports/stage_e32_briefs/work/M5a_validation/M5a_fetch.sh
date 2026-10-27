#!/usr/bin/env bash
# usage: M5a_fetch.sh <url> <outfile-name> <note>   (curl with browser headers; logs to log.tsv; pdftotext if PDF)
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/M5a_validation
url="$1"; out="$P/$2"; note="${3:-}"
[ -f "$P/log.tsv" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$P/log.tsv"
curl -sL --max-time 90 -o "$out" -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' "$url"
rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
if [ -f "$out" ]; then sha=$(sha256sum "$out" | cut -d' ' -f1); ty=$(file -b "$out" | cut -c1-60); sz=$(stat -c%s "$out"); else sha=NA; ty=missing; sz=0; fi
case "$ty" in PDF*) pdftotext -layout "$out" "$out.txt" 2>/dev/null; pg=$(pdfinfo "$out" 2>/dev/null | awk '/^Pages/{print $2}');; *) pg=NA;; esac
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" curl "$sha" "$2" "$note (rc=$rc size=$sz type=$ty pages=$pg)" >> "$P/log.tsv"
echo "rc=$rc size=$sz type=$ty pages=$pg"
