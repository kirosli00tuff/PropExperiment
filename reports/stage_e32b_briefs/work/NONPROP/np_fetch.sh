#!/bin/bash
# usage: np_fetch.sh url file note
cd /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/pages/NONPROP
url="$1"; f="$2"; note="$3"
code=$(curl -sL --max-time 60 -o "$f" -w '%{http_code}' -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,*/*' -H 'Accept-Language: en-CA,en;q=0.9' "$url")
utc=$(date -u +%FT%TZ); pdt=$(TZ=America/Vancouver date +%FT%T%z)
sha=$(sha256sum "$f" | cut -d' ' -f1)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s http %s size %s\n' "$url" "$utc" "$pdt" "$sha" "$f" "$note" "$code" "$(stat -c%s "$f")" >> log.tsv
echo "$f http $code $(stat -c%s "$f")"
sleep 2
