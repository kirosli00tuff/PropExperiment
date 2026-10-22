"""A2_topstep: strip an HTML page to text lines (script/style dropped, table cells joined by ' | ').

Also prints JSON-LD dateModified if present as the first line 'DATEMODIFIED: ...'.
Usage: python3 -I A2_topstep_extract.py <in.html> <out.txt>
"""
import re
import sys
from html.parser import HTMLParser

BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "ul", "ol", "table", "header", "footer", "blockquote"}


class Strip(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        elif tag in BLOCK:
            self.parts.append("\n")
        elif tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def main(src, dst):
    raw = open(src, encoding="utf-8", errors="replace").read()
    dm = re.findall(r'"dateModified"\s*:\s*"([^"]+)"', raw)
    p = Strip()
    p.feed(raw)
    text = "".join(p.parts)
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in text.split("\n")]
    lines = [ln for ln in lines if ln]
    with open(dst, "w", encoding="utf-8") as f:
        if dm:
            f.write("DATEMODIFIED: " + dm[0] + "\n")
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
