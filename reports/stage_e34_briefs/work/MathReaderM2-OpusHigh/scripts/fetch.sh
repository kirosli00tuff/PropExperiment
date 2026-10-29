#!/usr/bin/env bash
# usage: fetch.sh <url> <outname>   (saves raw under pages/, pdftotext if PDF, logs to pages/log.tsv)
set -u
W=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e34_briefs/work/MathReaderM2-OpusHigh
P=$W/pages; url="$1"; out="$2"
[ -f $P/log.tsv ] || printf 'url\tutc\tpdt\tmethod\thttp\tsha256\tfile\tnote\n' > $P/log.tsv
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
code=$(curl -sL -m 60 -o "$P/$out" -w '%{http_code}' -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -H 'Accept: text/html,application/pdf,*/*' -H 'Accept-Language: en-US,en;q=0.9' "$url")
sha=$(sha256sum "$P/$out" | cut -c1-64); typ=$(file -b "$P/$out" | cut -c1-30)
note="$typ"
if file -b "$P/$out" | grep -q PDF; then pdftotext -layout "$P/$out" "$P/$out.txt" 2>/dev/null; note="$note; words=$(wc -w < $P/$out.txt)"; fi
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" "$code" "$sha" "$out" "$note" >> $P/log.tsv
echo "$code $out $note"
