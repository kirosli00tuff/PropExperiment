#!/usr/bin/env bash
# C2_SDE private fetch helper: curl a URL to pages/C2_SDE/<file>, log to log.tsv.
# usage: C2_SDE_fetch.sh <url> <file_name> [method_note] [note]
set -u
ROOT=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_SDE
LOG="$ROOT/log.tsv"
url="$1"; fn="$2"; method="${3:-curl}"; note="${4:-}"
[ -f "$LOG" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$LOG"
out="$ROOT/$fn"
if [ "$method" = "curl" ]; then
  curl -sL --max-time 90 -o "$out" \
    -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
    -H 'Accept-Language: en-US,en;q=0.9' "$url"
  rc=$?
else
  rc=0
fi
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
if [ -s "$out" ]; then
  sha=$(sha256sum "$out" | cut -d' ' -f1)
  typ=$(file -b "$out" | cut -c1-40)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$method" "$sha" "$fn" "rc=$rc; $typ; $note" >> "$LOG"
  echo "OK $fn $(stat -c %s "$out")B $typ"
  case "$typ" in PDF*) pdftotext -layout "$out" "${out%.pdf}.txt" 2>/dev/null && echo "txt $(wc -l < "${out%.pdf}.txt") lines";; esac
else
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$method" "-" "$fn" "FAILED rc=$rc; $note" >> "$LOG"
  echo "FAIL $fn rc=$rc"; rm -f "$out"
fi
