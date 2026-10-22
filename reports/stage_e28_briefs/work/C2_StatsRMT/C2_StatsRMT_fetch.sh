#!/bin/bash
# usage: C2_StatsRMT_fetch.sh <url> <filename> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_StatsRMT
LOG=$P/log.tsv
[ -f $LOG ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > $LOG
url="$1"; f="$2"; note="$3"
curl -sL --max-time 90 -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -H 'Accept: text/html,application/pdf,application/xhtml+xml,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' -o "$P/$f" "$url"; rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sz=$(stat -c %s "$P/$f" 2>/dev/null || echo 0); ty=$(file -b "$P/$f" | cut -c1-40)
sha=$(sha256sum "$P/$f" | cut -d' ' -f1)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s (rc=%s size=%s type=%s)\n' "$url" "$utc" "$pdt" "$sha" "$f" "$note" "$rc" "$sz" "$ty" >> $LOG
echo "$f rc=$rc size=$sz $ty"
if [[ "$ty" == PDF* ]]; then pdftotext -layout "$P/$f" "$P/${f%.pdf}.txt" 2>/dev/null; pdftotext "$P/$f" "$P/${f%.pdf}.raw.txt" 2>/dev/null; fi
