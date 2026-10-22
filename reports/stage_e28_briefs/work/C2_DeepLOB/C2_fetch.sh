#!/bin/bash
# usage: C2_fetch.sh <url> <filename> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_DeepLOB
URL="$1"; F="$2"; NOTE="$3"
[ -f "$P/log.tsv" ] || printf "url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n" > "$P/log.tsv"
curl -sL --max-time 120 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
 -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.9" \
 -o "$P/$F" "$URL"
RC=$?
UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ); PDT=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
SZ=$(stat -c %s "$P/$F" 2>/dev/null || echo 0)
SHA=$(sha256sum "$P/$F" 2>/dev/null | cut -d' ' -f1)
printf "%s\t%s\t%s\tcurl\t%s\t%s\t%s (rc=%s,bytes=%s)\n" "$URL" "$UTC" "$PDT" "$SHA" "$F" "$NOTE" "$RC" "$SZ" >> "$P/log.tsv"
case "$F" in *.pdf) pdftotext -layout "$P/$F" "$P/${F%.pdf}.txt" 2>/dev/null; echo "txt lines: $(wc -l < "$P/${F%.pdf}.txt" 2>/dev/null)";; esac
echo "rc=$RC bytes=$SZ type=$(file -b "$P/$F" | cut -c1-40)"
