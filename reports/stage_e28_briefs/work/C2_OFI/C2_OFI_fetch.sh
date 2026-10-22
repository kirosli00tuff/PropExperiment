#!/usr/bin/env bash
# usage: C2_OFI_fetch.sh <url> <filename> <note>
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/C2_OFI
url="$1"; f="$2"; note="$3"
[ -f "$P/log.tsv" ] || printf 'url\tutc_fetch\tpdt_fetch\tmethod\tsha256\tfile\tnote\n' > "$P/log.tsv"
curl -sL --max-time 90 -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' -H 'Accept-Language: en-US,en;q=0.9' \
  -o "$P/$f" "$url"; rc=$?
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha=$(sha256sum "$P/$f" 2>/dev/null | cut -d' ' -f1); sz=$(stat -c %s "$P/$f" 2>/dev/null); ty=$(file -b "$P/$f" | cut -c1-40)
printf '%s\t%s\t%s\tcurl\t%s\t%s\t%s (rc=%s size=%s type=%s)\n' "$url" "$utc" "$pdt" "$sha" "$f" "$note" "$rc" "$sz" "$ty" >> "$P/log.tsv"
echo "$f rc=$rc size=$sz type=$ty"
if [[ "$ty" == PDF* ]]; then pdftotext -layout "$P/$f" "$P/${f%.pdf}.txt" 2>/dev/null; echo "  txt lines: $(wc -l < "$P/${f%.pdf}.txt")"; fi
