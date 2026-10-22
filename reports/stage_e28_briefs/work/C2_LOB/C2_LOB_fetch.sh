#!/bin/bash
# usage: C2_LOB_fetch.sh <url> <filename> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_LOB
url="$1"; f="$2"; note="$3"
curl -sL --max-time 90 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" \
 -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8" -H "Accept-Language: en-US,en;q=0.9" \
 -o "$P/$f" -w "%{http_code} %{content_type}\n" "$url"
u=$(date -u +%FT%TZ); p=$(TZ=America/Vancouver date +%FT%T%Z)
s=$(sha256sum "$P/$f" | cut -d' ' -f1)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\n' "$url" "$u" "$p" "$s" "$f" "$note" >> $P/log.tsv
case "$f" in *.pdf) pdftotext -layout "$P/$f" "$P/${f%.pdf}.txt" 2>/dev/null; echo "pages: $(pdfinfo "$P/$f" 2>/dev/null | grep Pages)"; wc -c "$P/${f%.pdf}.txt";; *) wc -c "$P/$f";; esac
