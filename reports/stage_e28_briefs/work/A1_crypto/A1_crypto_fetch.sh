#!/bin/bash
# usage: A1_crypto_fetch.sh <url> <filename> <note>
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A1_crypto
W=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/work/A1_crypto
LOG=$D/log.tsv
[ -f $LOG ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > $LOG
url="$1"; f="$2"; note="$3"
code=$(curl -sL --max-time 120 -o "$D/$f" -w '%{http_code}' -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' "$url")
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sz=$(stat -c %s "$D/$f" 2>/dev/null || echo 0)
sha=$(sha256sum "$D/$f" 2>/dev/null | cut -d' ' -f1)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$url" "$utc" "$pdt" curl "$sha" "$f" "http=$code size=$sz $note" >> $LOG
case "$f" in
 *.pdf) pdftotext -layout "$D/$f" "$D/${f%.pdf}.txt" 2>/dev/null ;;
 *.html|*.htm) python3 -I $W/A1_crypto_h2t.py "$D/$f" > "$D/$f.txt" 2>/dev/null ;;
esac
echo "$code $sz $f"
