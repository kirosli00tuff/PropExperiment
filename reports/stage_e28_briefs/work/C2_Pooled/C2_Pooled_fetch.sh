#!/usr/bin/env bash
# usage: C2_Pooled_fetch.sh <url> <outfile_basename> <note>
set -u
ROOT=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_Pooled
url="$1"; out="$2"; note="${3:-}"
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
curl -sL --max-time 90 -A "$UA" -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o "$ROOT/$out" "$url"
rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sz=$(stat -c %s "$ROOT/$out" 2>/dev/null || echo 0)
sha=$(sha256sum "$ROOT/$out" 2>/dev/null | cut -d' ' -f1)
[ -f "$ROOT/log.tsv" ] || printf 'url\tutc\tpdt\tmethod\tsha256\tfile\tnote\n' > "$ROOT/log.tsv"
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s (rc=%s,bytes=%s)\n' "$url" "$utc" "$pdt" "$sha" "$out" "$note" "$rc" "$sz" >> "$ROOT/log.tsv"
case "$out" in *.pdf) pdftotext -layout "$ROOT/$out" "$ROOT/${out%.pdf}.txt" 2>/dev/null; file "$ROOT/$out" | cut -c1-80; wc -l "$ROOT/${out%.pdf}.txt";; *) file "$ROOT/$out" | cut -c1-80;; esac
