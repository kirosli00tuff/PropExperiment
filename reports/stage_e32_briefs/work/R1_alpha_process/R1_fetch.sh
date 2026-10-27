#!/usr/bin/env bash
# usage: R1_fetch.sh <url> <outfile_basename> <note>
# curl with browser headers; saves raw page to pages dir, logs to log.tsv; pdftotext if PDF.
set -u
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/R1_alpha_process
url="$1"; f="$2"; note="${3:-}"
curl -sL --max-time 60 -o "$P/$f" \
 -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' \
 -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8' \
 -H 'Accept-Language: en-US,en;q=0.9' -w '%{http_code}' "$url" > "$P/.code_$f"
code=$(cat "$P/.code_$f"); rm -f "$P/.code_$f"
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%z)
sz=$(stat -c %s "$P/$f" 2>/dev/null || echo 0)
sha=$(sha256sum "$P/$f" | cut -d' ' -f1)
typ=$(file -b "$P/$f" | cut -c1-30)
if [[ "$typ" == PDF* ]]; then pdftotext -layout "$P/$f" "$P/$f.txt" 2>/dev/null; fi
printf '%s\t%s\t%s\tcurl\t%s\t%s\tHTTP %s; %s bytes; %s; %s\n' "$url" "$utc" "$pdt" "$sha" "$f" "$code" "$sz" "$typ" "$note" >> "$P/log.tsv"
echo "HTTP $code size $sz type $typ"
