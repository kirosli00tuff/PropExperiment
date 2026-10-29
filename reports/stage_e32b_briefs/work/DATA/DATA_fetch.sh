#!/bin/bash
# usage: DATA_fetch.sh <url> <file> <note>
cd /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/DATA
url="$1"; f="$2"; note="$3"
curl -sL --max-time 60 -A "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0" -H "Accept: text/html,application/xhtml+xml,*/*" -H "Accept-Language: en-US,en;q=0.9" -o "$f" -w "%{http_code} %{size_download}\n" "$url"
u=$(date -u +%FT%TZ); p=$(TZ=America/Vancouver date +%FT%T%z); h=$(sha256sum "$f"|cut -d' ' -f1)
[ -f log.tsv ] || printf "url\tutc\tpdt\tmethod\tsha256\tfile\tnote\n" > log.tsv
printf "%s\t%s\t%s\tcurl\t%s\t%s\t%s\n" "$url" "$u" "$p" "$h" "$f" "$note" >> log.tsv
